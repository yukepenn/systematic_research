"""GENESIS_H1_VOLSTATE_20260828 — discovery stage: state build + gates F1, F2, F3.

Executes the frozen spec exactly (see spec.yaml + out/spec_resolutions.txt R1-R16).
The modern (2022+) NQ parquet is NEVER opened by this program. Gate rows are printed
by program into out/gate_table.txt. All loads pass seal_guard.assert_presealed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h1_lib as L  # noqa: E402

from research_sdk.null_guard import run_circular_null, verify_null_sensitivity  # noqa: E402
from research_sdk.seal_guard import assert_presealed  # noqa: E402

OUT = L.RUN / "out"
OUT.mkdir(exist_ok=True)
DIAG: list[str] = []


def log(s: str = ""):
    DIAG.append(s)
    print(s)


def main():
    import platform
    log(f"run_discovery.py  python={platform.python_version()} numpy={np.__version__} pandas={pd.__version__}")
    log(f"frozen: tercile_window={L.TERCILE_WINDOW} rv_window={L.RV_WINDOW} "
        f"exclusion<{L.EXCLUDE_BEFORE.date()} discovery={L.DISC_START.date()}..{L.DISC_END.date()}")
    log()

    # ---------------------------------------------------------------- load certified
    vx_all = L.sealed_load_parquet(L.CERT / "vx_settlements_daily.parquet", "trade_date",
                                   "vx_settlements load")
    vix = L.sealed_load_parquet(L.CERT / "idx_VIX_daily.parquet", "date", "VIX load",
                                columns=["date", "close"])
    n_pre = int((vx_all["trade_date"] < L.EXCLUDE_BEFORE).sum())
    n_flag = int((vx_all["legacy_scale_flag"] == "LEGACY_10X_SUSPECT").sum())
    n_flag_kept = int(((vx_all["legacy_scale_flag"] == "LEGACY_10X_SUSPECT")
                       & (vx_all["trade_date"] >= L.EXCLUDE_BEFORE)).sum())
    vx = vx_all[vx_all["trade_date"] >= L.EXCLUDE_BEFORE].copy()
    log(f"vx rows total={len(vx_all)}  excluded pre-{L.EXCLUDE_BEFORE.date()}={n_pre}  "
        f"LEGACY_10X_SUSPECT total={n_flag} (kept after date-rule exclusion: {n_flag_kept})")
    dup = vx.duplicated(subset=["trade_date", "contract_year", "contract_month"]).sum()
    if dup:
        raise RuntimeError(f"DEFECT: {dup} duplicate (trade_date, contract) rows post-exclusion")

    # ---------------------------------------------------------------- expiry (R4)
    expiry_tab, val = L.build_expiry_table(vx)
    log(f"expiry validation (R4b scope: modern contracts w/ file expiry <= universe max; "
        f"{val['n_excluded_post_span']} post-span contracts excluded — they never use the derived value): "
        f"n={val['n_modern_with_file']} exact={val['n_exact']} ({val['pct_exact']:.2f}%) "
        f"off_by_1={val['n_off_by_1']} off_gt_1={val['n_off_gt_1']} max_abs_diff={val['max_abs_diff_days']}d")
    log(f"  diff distribution (derived-file, days): {val['diff_value_counts']}")
    gate_rows = [{
        "GATE": "R4b_EXPIRY_RULE",
        "SPEC": "derived expiry: >=95% exact vs in-span modern expiry_date_file, max miss <=1d",
        "OBSERVED": f"{val['pct_exact']:.2f}% exact, max miss {val['max_abs_diff_days']}d (n={val['n_modern_with_file']})",
        "VERDICT": "PASS" if val["pass"] else "FAIL",
    }]
    if not val["pass"]:
        gate_rows += [{"GATE": g, "SPEC": "-", "OBSERVED": "not computed (R4 DEFECT)", "VERDICT": "DEFECT"}
                      for g in ("F1", "F2", "F3", "PARITY", "F4")]
        finish(gate_rows, defect=True, state={})
        return

    # ---------------------------------------------------------------- basis (R5, R6)
    basis, bc = L.build_front_basis(vx, vix, expiry_tab)
    log(f"basis dates: {bc['n_basis']} of {bc['n_vx_dates_post_exclusion']} VX trade dates "
        f"(no-front-settle-row={bc['n_no_front_settle_row']}, nonpositive-settle={bc['n_nonpositive_settle']}, "
        f"no-VIX={bc['n_no_vix']})  span {basis['date'].min().date()}..{basis['date'].max().date()}")

    # terciles on the FULL basis series (backward windows => labels for d<=X identical
    # to running on any suffix-truncated series)
    labels, q33, q66 = L.rolling_tercile_labels(basis["basis"].to_numpy())
    basis["tercile"] = labels
    basis["q33"], basis["q66"] = q33, q66
    first_class = basis.loc[basis["tercile"].notna(), "date"].min()
    log(f"first classifiable basis date (252 strictly-prior obs): {first_class.date()}")

    # state_series.csv (unconditional spec output; pre-seal asserted)
    assert_presealed(basis, "date", "state_series.csv pre-write")
    ss = basis.copy()
    ss["date"] = ss["date"].dt.strftime("%Y-%m-%d")
    ss.to_csv(OUT / "state_series.csv", index=False)
    log(f"state_series.csv written: {len(ss)} rows (pre-seal asserted)")
    log()

    # ---------------------------------------------------------------- deep NQ (R1-R3)
    sess = L.stream_session_closes(L.DEEP_NQ, "deep nq1m", max_label=L.DISC_END)
    ret = L.next_session_returns(sess)
    log(f"deep NQ sessions (label<= {L.DISC_END.date()}): {len(sess)}  returns: {len(ret)}")
    log(f"  session bar counts: min={sess['n_bars'].min()} med={sess['n_bars'].median():.0f} "
        f"max={sess['n_bars'].max()}  halt-hour bars total={sess['n_halt_bars'].sum()}")
    gd = ret["gap_days"].value_counts().sort_index()
    log(f"  return calendar-gap distribution (days:count): {gd.to_dict()}")

    # RV series (R10) on deep sessions
    rets_by_next = ret.set_index("next_label")["pct_next"]
    rv_series = rets_by_next.rolling(L.RV_WINDOW, min_periods=L.RV_WINDOW).std(ddof=1)
    rv_df = pd.DataFrame({"session": rv_series.index, "rv": rv_series.to_numpy()}).dropna()
    rv_labels, _, _ = L.rolling_tercile_labels(rv_df["rv"].to_numpy())
    rv_df["rv_tercile"] = rv_labels

    # ---------------------------------------------------------------- discovery join (R8)
    disc = basis.merge(ret, left_on="date", right_on="session", how="inner")
    disc = disc.merge(rv_df, left_on="date", right_on="session", how="left", suffixes=("", "_rv"))
    disc = disc[(disc["date"] >= L.DISC_START) & (disc["date"] <= L.DISC_END)].copy()
    n_state_no_nq = int(((basis["date"] >= L.DISC_START) & (basis["date"] <= L.DISC_END)).sum() - len(disc))
    d = disc[disc["tercile"].notna() & np.isfinite(disc["pct_next"])].copy()
    log(f"discovery: state dates in window={((basis['date'] >= L.DISC_START) & (basis['date'] <= L.DISC_END)).sum()} "
        f"(no NQ next-return match: {n_state_no_nq})  classified+return N={len(d)}")
    log()

    # ---------------------------------------------------------------- F1
    f1 = L.diff_t_clustered(d, "tercile")
    per_terc = d.groupby("tercile")["pct_next"].agg(["size", "mean", "std"])
    pts_terc = d.groupby("tercile")["pts_next"].agg(["mean"])
    uncond = d["pct_next"].agg(["size", "mean", "std"])
    h1 = d[d["date"] <= L.HALF1_END]
    h2 = d[d["date"] > L.HALF1_END]

    def _diff(x):
        return float(x.loc[x["tercile"] == "T3", "pct_next"].mean()
                     - x.loc[x["tercile"] == "T1", "pct_next"].mean())
    d1, d2 = _diff(h1), _diff(h2)
    log("per-tercile next-session %% return (discovery) + unconditional control:")
    log(per_terc.to_string())
    log(f"  points means by tercile: {pts_terc['mean'].round(2).to_dict()}")
    log(f"  UNCONDITIONAL control: N={int(uncond['size'])} mean={uncond['mean']:.4f}% sd={uncond['std']:.4f}%")
    log(f"F1: T3-T1={f1['effect']:.4f}%/session  se={f1['se']:.4f}  t={f1['t']:.3f}  "
        f"(N={f1['n']}, month clusters={f1['n_clusters']})")
    log(f"F1 halves: 2007-2013 diff={d1:.4f}% (N={len(h1)})  2014-2021 diff={d2:.4f}% (N={len(h2)})")
    f1_pass = (f1["t"] >= 2.0) and (f1["effect"] > 0) and (d1 > 0) and (d2 > 0)
    gate_rows.append({"GATE": "F1_discovery_separation",
                      "SPEC": "t_clustered(T3-T1)>=2.0, T3-T1>0, same sign both halves 07-13/14-21",
                      "OBSERVED": f"diff={f1['effect']:.4f}%, t={f1['t']:.2f}, halves {d1:+.4f}/{d2:+.4f}",
                      "VERDICT": "PASS" if f1_pass else "FAIL"})

    # ---------------------------------------------------------------- F2
    d2f = d[d["rv_tercile"].notna()].copy()
    y = d2f["pct_next"].to_numpy(dtype=float)
    X = np.column_stack([
        np.ones(len(d2f)),
        (d2f["tercile"] == "T3").to_numpy(dtype=float),
        (d2f["tercile"] == "T1").to_numpy(dtype=float),
        (d2f["rv_tercile"] == "T2").to_numpy(dtype=float),
        (d2f["rv_tercile"] == "T3").to_numpy(dtype=float),
    ])
    g = d2f["next_label"].dt.strftime("%Y-%m").to_numpy()
    f2 = L.clustered_ols(y, X, g, np.array([0.0, 1.0, -1.0, 0.0, 0.0]))
    log()
    log("RV-matched table (rows=RV tercile, cells: N / mean pct_next by BASIS tercile):")
    piv_n = d2f.pivot_table(index="rv_tercile", columns="tercile", values="pct_next", aggfunc="size")
    piv_m = d2f.pivot_table(index="rv_tercile", columns="tercile", values="pct_next", aggfunc="mean")
    log("  N:\n" + piv_n.to_string())
    log("  mean %:\n" + piv_m.round(4).to_string())
    strat = (piv_m["T3"] - piv_m["T1"]).round(4)
    log(f"  per-stratum T3-T1: {strat.to_dict()}")
    log(f"F2: RV-FE contrast T3-T1={f2['effect']:.4f}%  t={f2['t']:.3f}  (N={f2['n']}, clusters={f2['n_clusters']})")
    f2_pass = (f2["effect"] > 0) and (f2["t"] >= 1.5)
    gate_rows.append({"GATE": "F2_rv_control",
                      "SPEC": "RV-tercile-matched T3-T1 keeps sign (>0) and clustered t>=1.5",
                      "OBSERVED": f"contrast={f2['effect']:.4f}%, t={f2['t']:.2f}",
                      "VERDICT": "PASS" if f2_pass else "FAIL"})

    # ---------------------------------------------------------------- F3 (null_guard)
    fb = basis[basis["date"] <= L.DISC_END].reset_index(drop=True)
    fr = fb.merge(ret[["session", "pct_next"]], left_on="date", right_on="session", how="left")
    f3_frame = pd.DataFrame({
        "session": fr["date"].dt.strftime("%Y-%m-%d"),
        "basis": fr["basis"].to_numpy(dtype=float),
        "next_ret": fr["pct_next"].to_numpy(dtype=float),
        "in_disc": ((fr["date"] >= L.DISC_START) & (fr["date"] <= L.DISC_END)).to_numpy(),
    })
    base_mask = f3_frame["in_disc"].to_numpy() & np.isfinite(f3_frame["next_ret"].to_numpy())
    base_rets = f3_frame["next_ret"].to_numpy()

    def decision_fn(frame: pd.DataFrame) -> np.ndarray:
        lab, _, _ = L.rolling_tercile_labels(frame["basis"].to_numpy())
        return lab

    def statistic_fn(decisions: np.ndarray, base: pd.DataFrame) -> float:
        m = base["in_disc"].to_numpy() & np.isfinite(base["next_ret"].to_numpy())
        r = base["next_ret"].to_numpy()
        m3 = m & (decisions == "T3")
        m1 = m & (decisions == "T1")
        if m3.sum() == 0 or m1.sum() == 0:
            raise RuntimeError("empty tercile group in null draw")
        return float(r[m3].mean() - r[m1].mean())

    loader = lambda: f3_frame.copy()  # noqa: E731
    m_units = len(f3_frame)
    probe = [1, m_units // 3, (2 * m_units) // 3]
    probe = [p for p in probe if p % m_units != 0]
    sens = verify_null_sensitivity(loader, decision_fn, statistic_fn, probe, unit="session")
    log()
    log(f"F3 sensitivity: real={sens['real_stat']:.4f} probe stats={[round(x,4) for x in sens['shift_stats']]} "
        f"spread={sens['spread']:.4f} — null CAN move")
    null = run_circular_null(loader, decision_fn, statistic_fn, n_shifts=300, unit="session", seed=0)
    arr = np.asarray(null["null_stats"], dtype=float)
    p95 = float(np.percentile(arr, 95))
    log(f"F3 null (300 whole-session circular shifts, seed=0, units={null['n_units']}): "
        f"mean={arr.mean():.4f} sd={arr.std(ddof=1):.4f} p5={np.percentile(arr,5):.4f} "
        f"p50={np.percentile(arr,50):.4f} p95={p95:.4f} max={arr.max():.4f}")
    log(f"F3: real={null['real_stat']:.4f}  percentile_rank={null['percentile']*100:.1f}%  p_ge={null['p_ge']:.4f}")
    if abs(null["real_stat"] - f1["effect"]) > 1e-9:
        log(f"  NOTE: real_stat vs F1 effect delta = {null['real_stat'] - f1['effect']:.2e} (should be ~0)")
    f3_pass = null["real_stat"] > p95
    gate_rows.append({"GATE": "F3_null",
                      "SPEC": "real T3-T1 strictly above 95th pct of >=300 circular-shift nulls",
                      "OBSERVED": f"real={null['real_stat']:.4f} vs null p95={p95:.4f} (rank {null['percentile']*100:.1f}%)",
                      "VERDICT": "PASS" if f3_pass else "FAIL"})

    # ------------------------------------------------- secondary states (R14, non-gate)
    log()
    for name, fn in (("VXN/VIX", "idx_VXN_daily.parquet"), ("VIX3M/VIX", "idx_VIX3M_daily.parquet")):
        idx = L.sealed_load_parquet(L.CERT / fn, "date", f"{name} load", columns=["date", "close"])
        j = idx.merge(vix, on="date", suffixes=("_num", "_vix"))
        j = j[np.isfinite(j["close_num"]) & np.isfinite(j["close_vix"]) & (j["close_vix"] > 0)].sort_values("date")
        j["ratio"] = j["close_num"] / j["close_vix"]
        lab, _, _ = L.rolling_tercile_labels(j["ratio"].to_numpy())
        j["tercile"] = lab
        jj = j.merge(ret, left_on="date", right_on="session", how="inner")
        jj = jj[(jj["date"] >= L.DISC_START) & (jj["date"] <= L.DISC_END)
                & jj["tercile"].notna() & np.isfinite(jj["pct_next"])]
        tt = jj.groupby("tercile")["pct_next"].agg(["size", "mean", "std"])
        try:
            st = L.diff_t_clustered(jj, "tercile")
            log(f"SECONDARY {name} (non-gate, discovery): N={len(jj)} span "
                f"{jj['date'].min().date()}..{jj['date'].max().date()}")
            log(tt.to_string())
            log(f"  T3-T1 spread={st['effect']:.4f}%  clustered t={st['t']:.3f}")
        except Exception as e:  # pragma: no cover
            log(f"SECONDARY {name}: not computable ({e})")

    # ---------------------------------------------------------------- verdicts
    all3 = f1_pass and f2_pass and f3_pass
    if all3:
        gate_rows.append({"GATE": "PARITY", "SPEC": "independent impl tercile agreement >=99.5%",
                          "OBSERVED": "pending (stage C)", "VERDICT": "PENDING"})
        gate_rows.append({"GATE": "F4_confirmation", "SPEC": "2022-01..2026-07 T3-T1 same sign, t>=1.0, ONE SHOT",
                          "OBSERVED": "pending (stage D, after parity)", "VERDICT": "PENDING"})
    else:
        gate_rows.append({"GATE": "PARITY", "SPEC": "independent impl tercile agreement >=99.5%",
                          "OBSERVED": "not run — F1-F3 precondition failed", "VERDICT": "NOT-RUN"})
        gate_rows.append({"GATE": "F4_confirmation", "SPEC": "2022-01..2026-07 T3-T1 same sign, t>=1.0, ONE SHOT",
                          "OBSERVED": "NOT READ — F1-F3 failed; 2022+ window stays unread by this family",
                          "VERDICT": "NOT-READ"})

    state = {
        "f1": f1, "f1_pass": bool(f1_pass), "half1_diff": d1, "half2_diff": d2,
        "n_half1": int(len(h1)), "n_half2": int(len(h2)),
        "f2": f2, "f2_pass": bool(f2_pass),
        "f3_real": null["real_stat"], "f3_null_p95": p95, "f3_rank_pct": null["percentile"] * 100,
        "f3_p_ge": null["p_ge"], "f3_pass": bool(f3_pass),
        "n_disc": int(len(d)),
        "n_t1": int(per_terc.loc["T1", "size"]), "n_t3": int(per_terc.loc["T3", "size"]),
        "uncond_mean": float(uncond["mean"]), "uncond_sd": float(uncond["std"]),
        "all3_pass": bool(all3),
        "seal_asserts": L.seal_assert_count(),
    }
    finish(gate_rows, defect=False, state=state)


def finish(gate_rows, defect: bool, state: dict):
    L.gate_table_write(
        gate_rows, OUT / "gate_table.txt",
        "GENESIS_H1_VOLSTATE_20260828 — gate table (printed by program, stage: discovery)\n"
        f"seal_guard.assert_presealed calls so far: {L.seal_assert_count()}\n")
    (OUT / "_gate_state.json").write_text(json.dumps(
        {"rows": gate_rows, "state": state, "defect": defect}, indent=1, default=str), encoding="utf-8")
    (OUT / "diagnostics.txt").write_text("\n".join(DIAG) + "\n", encoding="utf-8")
    if defect:
        (OUT / "ledger_result_pending.json").write_text(json.dumps({
            "trial_id": "G00010", "metrics": {}, "result": "DEFECT",
            "note": "R4 expiry derivation failed validation — front month not computable pre-2013",
        }, indent=1), encoding="utf-8")
    print("discovery stage complete")


if __name__ == "__main__":
    main()
