"""G2_F3_DELEV01_20260829 — MC-40 forced-deleveraging short continuation (trial G00027).

Implements the FROZEN spec.yaml + out/spec_resolutions.txt (R1-R13) exactly once.
No parameter is searched. All gate rows are printed BY THIS PROGRAM.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time as _time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from research_sdk.seal_guard import assert_presealed  # noqa: E402

RUN = REPO / "runs" / "G2_F3_DELEV01_20260829"
OUT = RUN / "out"
DEEP_NQ = REPO / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
EXPECTED_SHA = "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf"  # GENESIS_REPRO_INCUMBENT provenance

WIN_START = pd.Timestamp("2006-01-01")
WIN_END = pd.Timestamp("2026-05-31")          # pre-burn frozen window end (R2)
BAND_LO, BAND_HI = -0.05, -0.025              # [-5.0%, -2.5%) frozen
MA_N = 200                                    # frozen
HOLD = 3                                      # exit at close of t+3 (R4), frozen
VETO = -0.015                                 # gap-down veto threshold (R5), frozen
PV = 20.0                                     # $/pt NQ
COST_RT = 33.0                                # $/RT stressed tape, frozen
RV_N = 21
N_SHIFTS = 500                                # >= 300 specced
SESSION_CLOSE = pd.Timedelta(hours=17)
TOD_0931 = pd.Timedelta(hours=9, minutes=31)
TOD_1600 = pd.Timedelta(hours=16)

_LINES: list[str] = []


def emit(s: str = ""):
    print(s)
    _LINES.append(s)


def era_of(ts: pd.Timestamp) -> str:
    y = ts.year
    if y <= 2007: return "2006-07"
    if y <= 2009: return "2008-09"
    if y <= 2013: return "2010-13"
    if y <= 2017: return "2014-17"
    if y <= 2019: return "2018-19"
    if y <= 2021: return "2020-21"
    if y == 2022: return "2022"
    return "2023-26/05"


ERA_ORDER = ["2006-07", "2008-09", "2010-13", "2014-17", "2018-19", "2020-21", "2022", "2023-26/05"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    t0 = _time.time()
    emit("G2_F3_DELEV01_20260829 — gate output (printed by program)  trial G00027")
    emit("=" * 100)

    # ---------------- provenance + enforcement statements ----------------
    sha = sha256_file(DEEP_NQ)
    emit(f"substrate: {DEEP_NQ.relative_to(REPO)}")
    emit(f"  sha256={sha}  size={DEEP_NQ.stat().st_size:,}B  match_recorded_provenance={sha == EXPECTED_SHA}")
    if sha != EXPECTED_SHA:
        raise RuntimeError("substrate hash mismatch vs GENESIS_REPRO_INCUMBENT run_provenance — DEFECT")
    emit("data_esnq: NOT ACCESSED by this run -> ALLOWLIST_DEV_44 enforcement N/A (no tick reads). Blind pools untouched.")

    # ---------------- stream substrate (bounded memory), seal every row-group ----------------
    f = pq.ParquetFile(DEEP_NQ)
    open_map: dict[pd.Timestamp, float] = {}
    close_map: dict[pd.Timestamp, float] = {}
    n_seal, prev_last = 0, None
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g, columns=["time", "open", "close"]).to_pandas()
        if t["time"].dtype == object:
            t["time"] = pd.to_datetime(t["time"], format="%Y-%m-%d %H:%M:%S")
        assert_presealed(t, "time", f"DELEV01 rg{g}")
        n_seal += 1
        if not t["time"].is_monotonic_increasing:
            raise RuntimeError(f"rg{g}: time not monotonic")
        if prev_last is not None and t["time"].iloc[0] < prev_last:
            raise RuntimeError(f"rg{g}: row-group ordering broken")
        prev_last = t["time"].iloc[-1]
        day = t["time"].dt.normalize()
        tod = t["time"] - day
        label = day.where(tod <= SESSION_CLOSE, day + pd.Timedelta(days=1))
        for mask, store, px in ((tod == TOD_0931, open_map, "open"), (tod == TOD_1600, close_map, "close")):
            sub_lab = label[mask]
            sub_px = t.loc[mask, px]
            for lab, v in zip(sub_lab, sub_px):
                lab = pd.Timestamp(lab)
                if lab in store and store[lab] != float(v):
                    raise RuntimeError(f"duplicate {px} bar with differing value at session {lab.date()}")
                store[lab] = float(v)
        del t
    emit(f"seal_guard.assert_presealed calls: {n_seal} (every row-group time column) — all pre-seal (substrate ends before 2026-08-01)")

    # ---------------- session universe U (R1) ----------------
    u_labels = pd.DatetimeIndex(sorted(close_map.keys()))
    closes = np.array([close_map[l] for l in u_labels])
    opens = np.array([open_map.get(l, np.nan) for l in u_labels])
    emit(f"U (sessions with a 16:00 RTH close): {len(u_labels):,}  span {u_labels[0].date()} -> {u_labels[-1].date()}"
         f"  (max label <= {WIN_END.date()}: {u_labels[-1] <= WIN_END})")
    emit(f"U-sessions missing a 09:31 bar: {int(np.isnan(opens).sum())}")

    s = pd.Series(closes, index=u_labels)
    r = (s / s.shift(1) - 1.0).to_numpy()
    ma200 = s.rolling(MA_N, min_periods=MA_N).mean().to_numpy()
    rv = pd.Series(r, index=u_labels).rolling(RV_N, min_periods=RV_N).std(ddof=1).to_numpy()

    inwin = (u_labels >= WIN_START) & (u_labels <= WIN_END)
    off = int(np.argmax(inwin))                      # first in-window full index (contiguous range)
    N = int(inwin.sum())
    assert inwin[off:off + N].all(), "window not contiguous"
    emit(f"in-window U-sessions [{WIN_START.date()}..{WIN_END.date()}]: N={N:,} (2005 = warm-up only)")

    # ---------------- per-position policy arrays over in-window positions p=0..N-1 (R4/R5) ----------------
    j = np.arange(N) + off
    opens_next = np.full(N, np.nan); opens_next[:-1] = opens[j[:-1] + 1]
    completable = np.zeros(N, dtype=bool)
    completable[: N - HOLD] = np.isfinite(opens_next[: N - HOLD])
    with np.errstate(invalid="ignore"):
        gap = opens_next / closes[j] - 1.0
        vetoed_arr = gap < VETO
    traded_ok = completable & ~vetoed_arr
    net = np.full(N, np.nan)
    c1 = np.full(N, np.nan); c2 = np.full(N, np.nan); c3 = np.full(N, np.nan)
    v = np.where(completable)[0]
    c1[v] = opens_next[v] - closes[j[v] + 1]
    c2[v] = opens_next[v] - closes[j[v] + 2]
    c3[v] = opens_next[v] - closes[j[v] + 3]
    net[v] = c3[v] * PV - COST_RT

    # ---------------- events (R3) ----------------
    r_w, ma_w, cl_w, rv_w = r[j], ma200[j], closes[j], rv[j]
    with np.errstate(invalid="ignore"):
        band = (r_w >= BAND_LO) & (r_w < BAND_HI)
        bear = cl_w < ma_w
    detected = np.where(band & bear)[0]
    st = np.where(~completable[detected], "UNTRADEABLE", np.where(vetoed_arr[detected], "VETOED", "TRADED"))
    traded = detected[st == "TRADED"]
    lab_w = u_labels[j]
    eras_det = np.array([era_of(lab_w[p]) for p in detected])

    emit(""); emit("PER-ERA EVENT COUNTS (printed BEFORE any return table)")
    emit(f"{'era':<10} {'detected':>8} {'untradeable':>11} {'vetoed':>7} {'traded':>7}")
    for e in ERA_ORDER:
        m = eras_det == e
        emit(f"{e:<10} {int(m.sum()):>8} {int((st[m]=='UNTRADEABLE').sum()):>11} "
             f"{int((st[m]=='VETOED').sum()):>7} {int((st[m]=='TRADED').sum()):>7}")
    emit(f"{'TOTAL':<10} {len(detected):>8} {int((st=='UNTRADEABLE').sum()):>11} "
         f"{int((st=='VETOED').sum()):>7} {len(traded):>7}")
    emit("STATED: effective N concentrates in the 2008/2020/2022 stress clusters — see table above.")

    if len(traded) == 0:
        raise RuntimeError("zero traded events — cannot evaluate gates (would be DEFECT)")

    # ---------------- D1 clusters (R6) + MDE printed BEFORE return table ----------------
    tp = np.sort(traded)
    months = np.array([lab_w[p].strftime("%Y-%m") for p in tp])
    cluster_id = np.zeros(len(tp), dtype=int)
    for i in range(1, len(tp)):
        linked = (tp[i] - tp[i - 1] <= 2) or (months[i] == months[i - 1])
        cluster_id[i] = cluster_id[i - 1] if linked else cluster_id[i - 1] + 1
    y = net[tp]
    import statsmodels.api as sm
    res = sm.OLS(y, np.ones((len(y), 1))).fit(cov_type="cluster", cov_kwds={"groups": cluster_id})
    mean_net = float(res.params[0]); se = float(res.bse[0]); tstat = float(res.tvalues[0])
    n_clusters = int(pd.Series(cluster_id).nunique())
    mde = 2.0 * se
    emit(""); emit(f"MDE (printed BEFORE the return table): 2.0 x clustered SE = ${mde:,.2f} per event "
                   f"(SE=${se:,.2f}, n={len(tp)}, clusters={n_clusters})")

    # ---------------- return tables ----------------
    emit(""); emit("D1 RETURN TABLE — traded events, SHORT 1 ct, net of $33/RT")
    emit(f"  mean net/event = ${mean_net:,.2f}   median = ${np.median(y):,.2f}   sd = ${np.std(y, ddof=1):,.2f}")
    emit(f"  sum net = ${y.sum():,.2f}   win rate (net>0) = {float((y > 0).mean()):.1%}   clustered t = {tstat:.3f}")
    emit("  per-era (traded): era, n, mean net, sum net")
    eras_tr = np.array([era_of(lab_w[p]) for p in tp])
    for e in ERA_ORDER:
        m = eras_tr == e
        if m.sum():
            emit(f"    {e:<10} n={int(m.sum()):>3}  mean=${y[m].mean():>10,.2f}  sum=${y[m].sum():>12,.2f}")

    # ---------------- D2 vol-matched control (R8) — shared rng draw FIRST ----------------
    rng = np.random.default_rng(0)
    rv_valid = rv_w[np.isfinite(rv_w)]
    edges = np.quantile(rv_valid, np.arange(1, 10) / 10.0)
    decile = np.where(np.isfinite(rv_w), np.searchsorted(edges, rv_w, side="right"), -1)
    assert (decile[tp] >= 0).all(), "traded event lacking RV — DEFECT"
    det_mask = np.zeros(N, dtype=bool); det_mask[detected] = True
    with np.errstate(invalid="ignore"):
        pool_mask = (r_w < 0) & (decile >= 0) & ~det_mask & traded_ok
    ctrl_idx, shortfall = [], 0
    for d in range(10):
        need = int((decile[tp] == d).sum())
        if need == 0:
            continue
        avail = np.where(pool_mask & (decile == d))[0]
        if len(avail) < need:
            shortfall += need - len(avail)
            take = avail
        else:
            take = rng.choice(avail, size=need, replace=False)
        ctrl_idx.append(np.sort(take))
    ctrl = np.concatenate(ctrl_idx) if ctrl_idx else np.array([], dtype=int)
    yc = net[ctrl]
    mean_ctrl = float(yc.mean())
    emit(""); emit("D2 VOL-MATCHED CONTROL — down-days (r<0), no bear filter/band, matched on trailing-21 RV decile,")
    emit("  same policy incl. gap-down veto, count-matched per decile, ONE shared draw (seed 0, consumed before D3)")
    emit(f"  control n = {len(ctrl)} (events {len(tp)}, decile shortfall = {shortfall})")
    emit(f"  control mean net/event = ${mean_ctrl:,.2f}   median = ${np.median(yc):,.2f}   sd = ${np.std(yc, ddof=1):,.2f}")
    emit(f"  event-minus-control mean = ${mean_net - mean_ctrl:,.2f}")

    # ---------------- D3 circular-shift null (R9) — shared rng, drawn AFTER D2 ----------------
    shifts = rng.choice(np.arange(1, N), size=N_SHIFTS, replace=False)
    means, n_empty, n_traded_acc = [], 0, []
    for k in shifts:
        q = (detected + int(k)) % N
        m = traded_ok[q]
        if not m.any():
            n_empty += 1
            continue
        means.append(float(net[q[m]].mean()))
        n_traded_acc.append(int(m.sum()))
    means = np.array(means)
    p95 = float(np.percentile(means, 95))
    emit(""); emit(f"D3 CIRCULAR-SHIFT NULL — {N_SHIFTS} distinct whole-session shifts of the detected-event indicator")
    emit(f"  valid shifts = {len(means)} (empty: {n_empty})   pseudo-events/shift mean = {np.mean(n_traded_acc):.1f}"
         f" min = {min(n_traded_acc)}")
    emit(f"  null mean of means = ${means.mean():,.2f}   p50 = ${np.percentile(means, 50):,.2f}   p95 = ${p95:,.2f}")
    emit(f"  observed mean net = ${mean_net:,.2f}   exceeds p95: {mean_net > p95}")

    # ---------------- diagnostic (non-gate): MFE-path shape (R10) ----------------
    emit(""); emit("DIAGNOSTIC (non-gate) — MFE-path shape, traded events, gross short pts at U-closes t+1/t+2/t+3")
    for nm, arr in (("cum@c1", c1[tp]), ("cum@c2", c2[tp]), ("cum@c3", c3[tp])):
        emit(f"  {nm}: mean={arr.mean():+8.2f} pts  median={np.median(arr):+8.2f} pts")
    inc1, inc2, inc3 = c1[tp], c2[tp] - c1[tp], c3[tp] - c2[tp]
    emit(f"  increments: entry->c1 mean={inc1.mean():+.2f}  c1->c2 mean={inc2.mean():+.2f}  c2->c3 mean={inc3.mean():+.2f} pts")
    argmx = np.argmax(np.vstack([c1[tp], c2[tp], c3[tp]]), axis=0)
    emit(f"  max close-mark at: c1 {int((argmx==0).sum())}, c2 {int((argmx==1).sum())}, c3 {int((argmx==2).sum())} "
         f"(positive-early/negative-late = spiral-then-reversal signature)")

    # ---------------- gate table (printed by program) ----------------
    d1 = (mean_net > 0.0) and (tstat >= 2.0)
    d2 = mean_net > mean_ctrl
    d3 = mean_net > p95
    survived = d1 and d2 and d3
    rows = [
        ("D1", "net mean/event > 0 AND event-clustered t >= 2.0",
         f"mean=${mean_net:,.2f}, t={tstat:.3f} (n={len(tp)}, clusters={n_clusters})", "PASS" if d1 else "FAIL"),
        ("D2", "event mean net > vol-matched control mean net",
         f"${mean_net:,.2f} vs ${mean_ctrl:,.2f}", "PASS" if d2 else "FAIL"),
        ("D3", f"mean net > p95 of {N_SHIFTS} circular-shift means",
         f"${mean_net:,.2f} vs p95=${p95:,.2f}", "PASS" if d3 else "FAIL"),
        ("VERDICT", "all three PASS -> SURVIVED-DISCOVERY; any fail -> NULL",
         "SURVIVED-DISCOVERY" if survived else "NULL at formulation", "PASS" if survived else "FAIL"),
    ]
    emit(""); emit("GATE TABLE (printed by program)")
    w0 = max(len(x[0]) for x in rows); w1 = max(len(x[1]) for x in rows); w2 = max(len(x[2]) for x in rows)
    emit(f"{'GATE':<{w0}}  {'SPEC':<{w1}}  {'OBSERVED':<{w2}}  PASS-FAIL")
    emit("-" * (w0 + w1 + w2 + 15))
    for g_, sp, ob, vd in rows:
        emit(f"{g_:<{w0}}  {sp:<{w1}}  {ob:<{w2}}  {vd}")

    # ---------------- outputs ----------------
    ev = pd.DataFrame({
        "event_label": [lab_w[p].date() for p in detected],
        "era": eras_det,
        "ret_pct": r_w[detected] * 100.0,
        "close": cl_w[detected],
        "ma200": ma_w[detected],
        "rv21": rv_w[detected],
        "rv_decile": decile[detected],
        "status": st,
        "entry_label": [lab_w[p + 1].date() if p + 1 < N else None for p in detected],
        "entry_px": opens_next[detected],
        "gap_pct": gap[detected] * 100.0,
        "exit_label": [lab_w[p + 3].date() if p + 3 < N else None for p in detected],
        "exit_px": [closes[j[p] + 3] if completable[p] else np.nan for p in detected],
        "gross_pts": c3[detected],
        "net_usd": net[detected],
        "cum_pts_c1": c1[detected], "cum_pts_c2": c2[detected], "cum_pts_c3": c3[detected],
    })
    cmap = dict(zip(tp, cluster_id))
    ev["cluster_id"] = [cmap.get(p, -1) for p in detected]
    ev.to_csv(OUT / "events.csv", index=False)
    pd.DataFrame({
        "control_label": [lab_w[p].date() for p in ctrl],
        "era": [era_of(lab_w[p]) for p in ctrl],
        "ret_pct": r_w[ctrl] * 100.0, "rv21": rv_w[ctrl], "rv_decile": decile[ctrl],
        "entry_px": opens_next[ctrl], "gap_pct": gap[ctrl] * 100.0,
        "gross_pts": c3[ctrl], "net_usd": net[ctrl],
    }).to_csv(OUT / "controls.csv", index=False)

    wall = int(_time.time() - t0)
    emit(""); emit(f"wall_s {wall}")
    (OUT / "gate_table.txt").write_text("\n".join(_LINES) + "\n", encoding="utf-8")

    pending = {
        "trial_id": "G00027",
        "metrics": {
            "n_detected": int(len(detected)), "n_untradeable": int((st == "UNTRADEABLE").sum()),
            "n_vetoed": int((st == "VETOED").sum()), "n_traded": int(len(tp)),
            "n_clusters": n_clusters, "mean_net_usd": round(mean_net, 2), "median_net_usd": round(float(np.median(y)), 2),
            "clustered_t": round(tstat, 3), "clustered_se_usd": round(se, 2), "mde_usd": round(mde, 2),
            "sum_net_usd": round(float(y.sum()), 2), "win_rate": round(float((y > 0).mean()), 4),
            "ctrl_n": int(len(ctrl)), "ctrl_shortfall": int(shortfall), "ctrl_mean_net_usd": round(mean_ctrl, 2),
            "shift_n": int(len(means)), "shift_p95_usd": round(p95, 2), "shift_mean_usd": round(float(means.mean()), 2),
            "cum_pts_c1_mean": round(float(c1[tp].mean()), 2), "cum_pts_c2_mean": round(float(c2[tp].mean()), 2),
            "cum_pts_c3_mean": round(float(c3[tp].mean()), 2),
            "D1": bool(d1), "D2": bool(d2), "D3": bool(d3),
            "seal_asserts": n_seal, "substrate_sha256_match": True, "wall_s": wall,
        },
        "result": "PASS" if survived else "NULL",
        "note": ("MC-40 deleveraging short: frozen band/horizon/MA/veto, $33/RT; D1 event-clustered t (overlap+month "
                 "merged clusters); D2 trailing-21-RV-decile count-matched down-day control (shared draw seed 0); "
                 "D3 500 circular whole-session shifts (same rng). "
                 + ("All gates passed -> SURVIVED-DISCOVERY (routes to robustness + independent implementation)."
                    if survived else "Failed gate(s) -> NULL at formulation; a FAIL is a FAIL.")),
    }
    (OUT / "ledger_result_pending.json").write_text(json.dumps(pending, indent=2), encoding="utf-8")
    print("WROTE:", OUT / "gate_table.txt", OUT / "events.csv", OUT / "controls.csv", OUT / "ledger_result_pending.json")


if __name__ == "__main__":
    main()
