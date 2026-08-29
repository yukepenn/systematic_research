"""G2_F6_BREADTHPM01_20260829 — MC-41 economics stage (trial G00033).

Frozen policy (spec.yaml): SHORT 1 NQ at the 11:01-stamped bar open on bottom-tercile
11:00 cumulative adjusted-TICK sessions (state construction identical to the G00030
diagnostic, RECOMPUTED from the certified internals parquet); exit 15:59-stamped bar
close; no stop. $25.01/ctrRT primary, $33 stress non-gate. Gates B0/B1/B2/B3 per
spec.yaml; all resolutions frozen in out/spec_resolutions.txt BEFORE this program ran.
Gate tables PRINTED BY THIS PROGRAM. POINTS-based P&L (substrate law). No search.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import time as dtime

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)
from research_sdk.seal_guard import assert_presealed  # noqa: E402

RUN = os.path.join(REPO, "runs", "G2_F6_BREADTHPM01_20260829")
OUT = os.path.join(RUN, "out")
TICK_PATH = os.path.join(REPO, "research", "data_internals", "TICK_1m.parquet")
TICK_MANIFEST_SHA = "72612a1e0f308b57862d6e0adfb5883ceee05dfc697c4cb980ea7b2c82b6d80f"
NQ_PATH = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
NQ_PROV_SHA = "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d"

END_DATE = pd.Timestamp("2026-05-31")            # R1 (G00030 R1): inclusive endpoint
MORN_LO, MORN_HI = dtime(9, 31), dtime(11, 0)    # END-stamped (G00030 R2)
AFT_LO, AFT_HI = dtime(11, 1), dtime(16, 0)      # G00030 R2 (quality-filter windows)
ENTRY_T, EXIT_T = dtime(11, 1), dtime(15, 59)    # policy: 11:01-bar open -> 15:59-bar close
WARMUP = 252                                     # R2 (G00030 R4)
N_NULL = 10_000                                  # R9
N_DRAWS = 10_000                                 # R7 (spec floor >= 300)
SEED = 20260829                                  # R10 family draw
POINT_USD = 20.0                                 # NQ multiplier
COST_PRIMARY = 25.01                             # $/ctrRT, gate basis
COST_STRESS = 33.00                              # $/ctrRT, reported NON-gate
Z_POWER = 1.959963984540054 + 0.8416212335729143  # 2.8016 (R11)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    lines: list[str] = []

    def emit(s: str = "") -> None:
        print(s)
        lines.append(s)

    emit("=" * 90)
    emit("G2_F6_BREADTHPM01_20260829 / MC-41 economics stage / trial G00033")
    emit("printed by program: runs/G2_F6_BREADTHPM01_20260829/src/run_breadthpm01.py")
    emit("=" * 90)

    # ---- G1: provenance + manifest gate (abort before any read on mismatch) --------
    tick_sha, nq_sha = sha256(TICK_PATH), sha256(NQ_PATH)
    tick_ok, nq_ok = tick_sha == TICK_MANIFEST_SHA, nq_sha == NQ_PROV_SHA
    emit(f"TICK_1m.parquet sha256 {tick_sha}  manifest-match={tick_ok}")
    emit(f"nq_1m_2022_2026.parquet sha256 {nq_sha}  provenance-match={nq_ok}")
    if not (tick_ok and nq_ok):
        raise SystemExit("MANIFEST/PROVENANCE HASH MISMATCH — aborting before any read")

    # ---- G2: load through seal guard (full frames, before any windowing) -----------
    tick = pd.read_parquet(TICK_PATH, columns=["time", "close"])
    nq = pd.read_parquet(NQ_PATH, columns=["time", "open", "close"])
    assert_presealed(tick, "time", "BREADTHPM01 TICK full frame")
    assert_presealed(nq, "time", "BREADTHPM01 NQ full frame")
    emit(f"seal_guard.assert_presealed PASS on both frames "
         f"(TICK {len(tick):,} rows, NQ {len(nq):,} rows)")

    tick = tick[tick["time"].dt.normalize() <= END_DATE].copy()
    nq = nq[nq["time"].dt.normalize() <= END_DATE].copy()
    for df in (tick, nq):
        df["d"] = df["time"].dt.date
        df["t"] = df["time"].dt.time

    # ---- per-session state inputs + quality filters (R2/R3, == G00030 R2/R3/R6) ----
    tick_m = tick[(tick["t"] >= MORN_LO) & (tick["t"] <= MORN_HI)]
    g = tick_m.groupby("d")
    tick_sess = pd.DataFrame({
        "n_tick_morn": g["close"].count(),
        "cum11": g["close"].sum(),
        "has_1100": g["t"].agg(lambda s: MORN_HI in set(s)),
    })

    nq_rth = nq[(nq["t"] >= MORN_LO) & (nq["t"] <= AFT_HI)]
    gm = nq_rth[nq_rth["t"] <= MORN_HI].groupby("d")
    ga = nq_rth[nq_rth["t"] >= AFT_LO].groupby("d")
    nq_sess = pd.DataFrame({
        "n_nq_morn": gm["open"].count(),
        "n_nq_aft": ga["open"].count(),
        "last_rth": nq_rth.groupby("d")["t"].max(),
    })
    entry_bars = nq_rth[nq_rth["t"] == ENTRY_T].set_index("d")["open"]
    exit_bars = nq_rth[nq_rth["t"] == EXIT_T].set_index("d")["close"]
    nq_sess["entry_open"] = entry_bars
    nq_sess["exit_close"] = exit_bars

    s = tick_sess.join(nq_sess, how="inner")
    n_joined = len(s)
    q = (
        (s["n_tick_morn"] >= 80) & s["has_1100"]
        & (s["n_nq_morn"] >= 80) & (s["n_nq_aft"] >= 200)
        & (s["last_rth"] >= dtime(15, 59))
    )
    n_dropped_quality = int((~q).sum())
    s = s[q].sort_index()

    # ---- causal terciles, trailing 252 full window (R2; top mirror R12) ------------
    cum = s["cum11"].to_numpy()
    n_all = len(s)
    bottom = np.full(n_all, np.nan)
    top = np.full(n_all, np.nan)
    thr_bot_arr = np.full(n_all, np.nan)
    for i in range(WARMUP, n_all):
        win = cum[i - WARMUP:i]
        thr_b = np.percentile(win, 100.0 / 3.0)
        thr_t = np.percentile(win, 200.0 / 3.0)
        thr_bot_arr[i] = thr_b
        bottom[i] = 1.0 if cum[i] <= thr_b else 0.0
        top[i] = 1.0 if cum[i] >= thr_t else 0.0
    s["bottom"], s["top"], s["thr_bot"] = bottom, top, thr_bot_arr
    pop = s[~s["bottom"].isna()].copy()

    # ---- R4 availability requirement (entry/exit bars) -----------------------------
    n_missing_bars = int(pop["entry_open"].isna().sum() + pop["exit_close"].isna().sum())
    avail = pop["entry_open"].notna() & pop["exit_close"].notna()
    n_removed_avail = int((~avail).sum())
    pop = pop[avail]
    emit(f"R4 availability: {n_removed_avail} classified session(s) removed for missing "
         f"11:01/15:59 bar ({n_missing_bars} missing bar value(s))")

    ind = pop["bottom"].to_numpy().astype(bool)
    ind_top = pop["top"].to_numpy().astype(bool)
    N = len(pop)
    n1 = int(ind.sum())

    # ---- per-session P&L vectors, POINTS-based (R5) --------------------------------
    gross_pts_short = (pop["entry_open"] - pop["exit_close"]).to_numpy()
    net_short = gross_pts_short * POINT_USD - COST_PRIMARY          # $ / event, primary
    net_short_stress = gross_pts_short * POINT_USD - COST_STRESS    # $ / event, non-gate
    net_long = -gross_pts_short * POINT_USD - COST_PRIMARY          # mirror leg (R12)

    cond = net_short[ind]
    mean_cond = cond.mean()
    sd_cond = cond.std(ddof=1)
    t_cond = mean_cond / (sd_cond / np.sqrt(n1))
    mean_uncond = net_short.mean()

    # ---- family draws (R10): B3 offsets FIRST (bit-identical to G00030), then B2(i)
    rng = np.random.default_rng(SEED)
    offsets = rng.integers(1, N, size=N_NULL)
    null_means = np.empty(N_NULL)
    for j, k in enumerate(offsets):
        null_means[j] = net_short[np.roll(ind, k)].mean()
    draw_means = np.empty(N_DRAWS)
    for j in range(N_DRAWS):
        draw_means[j] = net_short[rng.choice(N, size=n1, replace=False)].mean()

    sigma_null = null_means.std(ddof=1)
    p95_null = np.percentile(null_means, 95.0)
    p_one_null = (1 + int((null_means >= mean_cond).sum())) / (N_NULL + 1)
    p95_draw = np.percentile(draw_means, 95.0)
    p_one_draw = (1 + int((draw_means >= mean_cond).sum())) / (N_DRAWS + 1)

    # ---- B0: POWER BLOCK — printed BEFORE any return table (R11) -------------------
    span_days = (pd.Timestamp(pop.index[-1]) - pd.Timestamp(pop.index[0])).days
    years = span_days / 365.25
    events_yr = n1 / years
    mde_null_usd = Z_POWER * sigma_null
    mde_analytic_usd = Z_POWER * sd_cond / np.sqrt(n1)

    emit()
    emit("---- B0 POWER BLOCK (printed BEFORE any return table, per spec) ----")
    emit(f"population: {n_joined} joined sessions; {n_dropped_quality} dropped by quality (R3); "
         f"{n_all} valid; {WARMUP} warm-up; {N} classified "
         f"({pop.index[0]} .. {pop.index[-1]}, {years:.2f} yr)")
    emit(f"events (bottom-tercile sessions): n1 = {n1}   (spec expectation ~263)   "
         f"EVENTS/YR = {events_yr:.1f}")
    emit(f"POWERED MDE on mean net/event (null-sd basis, alpha=.05 two-sided, power=.80): "
         f"${mde_null_usd:.2f}/event  [sigma_null = ${sigma_null:.2f}]")
    emit(f"analytic MDE (sd/sqrt(n) basis, reference only): ${mde_analytic_usd:.2f}/event")
    emit("(no CLOSED-BY-POWER ceiling in this spec — B0 is a print-order gate; MDE recorded)")

    # ---- RETURN TABLE (after power block) ------------------------------------------
    def row(name: str, v: np.ndarray) -> str:
        m = v.mean()
        t = m / (v.std(ddof=1) / np.sqrt(len(v)))
        return (f"{name:<44}| {len(v):>5} | {m:>+10.2f} | {t:>+7.2f} | "
                f"{v.sum():>+12.0f} | {np.median(v):>+9.2f}")

    emit()
    emit("---- RETURN TABLE (net $/event; POINTS-based gross x $20/pt, costs per R5) ----")
    emit(f"{'LEG':<44}| {'n':>5} | {'mean/ev':>10} | {'t':>7} | {'total $':>12} | {'median':>9}")
    emit("-" * 100)
    emit(row(f"CONDITIONAL SHORT bottom-tercile @ ${COST_PRIMARY}", cond))
    emit(row(f"  stress cost ${COST_STRESS} (NON-gate)", net_short_stress[ind]))
    emit(row(f"UNCONDITIONAL SHORT all sessions @ ${COST_PRIMARY}", net_short))
    emit(row(f"MIRROR LONG top-tercile @ ${COST_PRIMARY} (NON-gate)", net_long[ind_top]))
    emit("-" * 100)
    emit(f"conditional gross: {gross_pts_short[ind].mean():+.2f} pts/event "
         f"(${gross_pts_short[ind].mean() * POINT_USD:+.2f}); "
         f"win rate {(cond > 0).mean() * 100:.1f}%")

    # ---- B2 DUAL-CONTROL TABLE (explicit, both controls charged identical costs) ---
    b2i_pass = mean_cond > p95_draw
    b2ii_pass = mean_cond > mean_uncond
    emit()
    emit("---- B2 DUAL-CONTROL TABLE (both short controls charge identical $25.01/ctrRT) ----")
    emit(f"{'CONTROL':<58}| {'value $/ev':>11} | verdict")
    emit("-" * 90)
    emit(f"{'observed conditional short mean':<58}| {mean_cond:>+11.2f} |")
    emit(f"{'(i) count-matched random-session short, p95 of ' + str(N_DRAWS) + ' draws':<58}"
         f"| {p95_draw:>+11.2f} | {'BEATEN' if b2i_pass else 'NOT BEATEN'}")
    emit(f"{'      draw distribution p50 / mean':<58}"
         f"| {np.percentile(draw_means, 50):>+11.2f} | (p_one={p_one_draw:.4f})")
    emit(f"{'(ii) all-sessions unconditional short mean':<58}"
         f"| {mean_uncond:>+11.2f} | {'BEATEN' if b2ii_pass else 'NOT BEATEN'}")
    emit("-" * 90)

    # ---- B3 null readout ------------------------------------------------------------
    b3_pass = mean_cond > p95_null
    emit()
    emit(f"B3 circular-shift null (N_NULL={N_NULL}, seed={SEED}, offsets shared with G00030 "
         f"family draw): p95 = ${p95_null:+.2f}, observed = ${mean_cond:+.2f}, "
         f"p_one = {p_one_null:.4f}")

    # ---- GATE TABLE (printed by program) --------------------------------------------
    b1_pass = (mean_cond > 0) and (t_cond >= 2.0)
    all_pass = b1_pass and b2i_pass and b2ii_pass and b3_pass
    verdict = "SURVIVED-DISCOVERY" if all_pass else "NULL AT FORMULATION"

    emit()
    emit("GATE TABLE (printed by program)")
    emit(f"{'GATE':<26}| {'SPEC':<46}| {'OBSERVED':<42}| PASS-FAIL")
    emit("-" * 128)
    rows = [
        ("G1 manifest/provenance", "sha256 match both substrates",
         f"TICK={tick_ok} NQ={nq_ok}", "PASS" if tick_ok and nq_ok else "FAIL"),
        ("G2 seal compliance", "no bar > 2026-07-31 17:00 ET read",
         "assert_presealed passed, window<=2026-05-31", "PASS"),
        ("B0 power-first", "MDE + events/yr printed before returns (~263 ev)",
         f"printed first; n1={n1}, {events_yr:.1f}/yr, MDE ${mde_null_usd:.2f}", "PASS"),
        ("B1 net + clustered t", f"mean net/event > 0 AND t >= 2.0 @ ${COST_PRIMARY}",
         f"mean=${mean_cond:+.2f}, t={t_cond:+.2f}",
         "PASS" if b1_pass else "FAIL"),
        ("B2(i) matched-count ctrl", f">{N_DRAWS} random-session short p95 (floor 300)",
         f"obs ${mean_cond:+.2f} vs p95 ${p95_draw:+.2f}",
         "PASS" if b2i_pass else "FAIL"),
        ("B2(ii) uncond ctrl", "beats all-sessions short mean (printed row)",
         f"obs ${mean_cond:+.2f} vs ${mean_uncond:+.2f}",
         "PASS" if b2ii_pass else "FAIL"),
        ("B3 circular-shift null", "obs > p95 of whole-session-shift null",
         f"obs ${mean_cond:+.2f} vs p95 ${p95_null:+.2f}, p_one={p_one_null:.4f}",
         "PASS" if b3_pass else "FAIL"),
    ]
    for gname, spec_c, obs_c, pf in rows:
        emit(f"{gname:<26}| {spec_c:<46}| {obs_c:<42}| {pf}")
    emit("-" * 128)
    emit(f"VERDICT (trial G00033 / MC-41 economics): {verdict}")
    emit("REGIME-LOCAL: 2023-01 -> 2026-05-31 internals population only; no claim outside it.")
    emit("The G00030 INFORMATION finding stands either way — information and monetization "
         "are separate ledgers.")
    emit("evidence-status: DISCOVERY_CONSUMED")

    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    # ---- events.csv (R15) ------------------------------------------------------------
    ev = pop[ind].copy()
    ev_out = pd.DataFrame({
        "date": ev.index,
        "cum11": ev["cum11"].to_numpy(),
        "tercile_boundary": ev["thr_bot"].to_numpy(),
        "entry_open_1101": ev["entry_open"].to_numpy(),
        "exit_close_1559": ev["exit_close"].to_numpy(),
        "gross_pts": gross_pts_short[ind],
        "gross_usd": gross_pts_short[ind] * POINT_USD,
        "net_usd_2501": cond,
        "net_usd_3300": net_short_stress[ind],
    })
    ev_out.to_csv(os.path.join(OUT, "events.csv"), index=False, float_format="%.4f")

    frag = {
        "trial_id": "G00033",
        "mc_id": "MC-41 (economics stage)",
        "run_id": "G2_F6_BREADTHPM01_20260829",
        "date": "2026-08-29",
        "question": "does the breadth-conditioned afternoon-downside information survive "
                    "costs as a short policy (dead-short-leg burden carried explicitly)?",
        "population": {"sessions_classified": N, "bottom_tercile_events": n1,
                       "span": [str(pop.index[0]), str(pop.index[-1])],
                       "events_per_year": round(events_yr, 1)},
        "power": {"mde_usd_per_event_null_basis": round(mde_null_usd, 2),
                  "mde_usd_per_event_analytic": round(mde_analytic_usd, 2),
                  "sigma_null_usd": round(sigma_null, 2)},
        "observed": {
            "mean_net_usd_per_event_at_25_01": round(mean_cond, 2),
            "t_event_clustered": round(t_cond, 2),
            "total_net_usd_at_25_01": round(float(cond.sum()), 0),
            "mean_gross_pts": round(float(gross_pts_short[ind].mean()), 2),
            "mean_net_usd_per_event_at_33_stress_nongate": round(float(net_short_stress[ind].mean()), 2),
            "uncond_short_mean_usd": round(mean_uncond, 2),
            "b2i_p95_matched_draws_usd": round(p95_draw, 2),
            "b2i_p_one": round(p_one_draw, 4),
            "b3_p95_null_usd": round(p95_null, 2),
            "b3_p_one": round(p_one_null, 4),
            "mirror_top_tercile_long_mean_usd_nongate": round(float(net_long[ind_top].mean()), 2),
            "n_null": N_NULL, "n_draws": N_DRAWS, "seed": SEED,
        },
        "gates": {"B1": "PASS" if b1_pass else "FAIL",
                  "B2i": "PASS" if b2i_pass else "FAIL",
                  "B2ii": "PASS" if b2ii_pass else "FAIL",
                  "B3": "PASS" if b3_pass else "FAIL"},
        "verdict": verdict,
        "regime_scope": "REGIME-LOCAL 2023-01 -> 2026-05-31 internals population",
        "evidence_status": "DISCOVERY_CONSUMED",
        "promotion": "NONE",
        "spend_usd": 0,
        "live_enabled": False,
        "artifacts": ["runs/G2_F6_BREADTHPM01_20260829/out/gate_table.txt",
                      "runs/G2_F6_BREADTHPM01_20260829/out/events.csv",
                      "runs/G2_F6_BREADTHPM01_20260829/out/spec_resolutions.txt",
                      "runs/G2_F6_BREADTHPM01_20260829/src/run_breadthpm01.py"],
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(frag, f, indent=2)
    print("\nwrote out/gate_table.txt, out/events.csv, out/ledger_result_pending.json")


if __name__ == "__main__":
    main()
