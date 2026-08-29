"""G2_F6_AUCTREV01_20260829 — MC-46 EOD dislocation reversion economics (trial G00032).

Frozen spec runs/G2_F6_AUCTREV01_20260829/spec.yaml executed exactly, per
out/spec_resolutions.txt R1-R12 (written before this program ran). Gate table PRINTED
BY THIS PROGRAM; MDE and event counts printed BEFORE any return table (hard rule 7).
Substrate law: POINTS. Seal: every load passes research_sdk.seal_guard.assert_presealed.
Trailing causal 252-session deciles recomputed here (NOT the diagnostic's era deciles).
No parameter search. Seeds fixed: 20260829 everywhere.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time as _time
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)
from research_sdk.seal_guard import assert_presealed  # noqa: E402
from research_sdk import null_guard  # noqa: E402

SUBSTRATE = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
SUBSTRATE_SHA_EXPECTED = "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf"
OUT = os.path.join(REPO, r"runs\G2_F6_AUCTREV01_20260829\out")
SEED = 20260829
K_CONTROL = 1000       # E2 draws (spec floor 300)
K_NULL = 1000          # E3 shifts
SENS_SHIFTS = [1000, 2500, 4000]
TRAIL = 252
COST35 = 35.0 / 20.0   # $35/ctrRT at $20/pt = 1.75 pts
COST40 = 40.0 / 20.0   # stress, non-gate
START = date(2006, 1, 1)
END = date(2026, 5, 31)
ERA1_END = date(2015, 12, 31)

N_RET = 390  # grid stamps 09:31..16:00


def grid_idx(hh: int, mm: int) -> int:
    return (hh - 9) * 60 + (mm - 31)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_sessions():
    """Return (qual session ids [N], D [N] pts, exit_close [N] (=own 09:30 seed close),
    exit_ts [N], entry_open [N] or nan, entry_ts [N], entry_case [N], first_bar_open/ts
    per session for the overnight fallback)."""
    df = pd.read_parquet(SUBSTRATE)
    df["ts"] = pd.to_datetime(df["time"])
    assert_presealed(df, "ts", "AUCTREV01 load nq1m_2005_202605")  # hard rule 4
    df = df[(df["ts"] >= pd.Timestamp("2005-12-31")) & (df["ts"] <= pd.Timestamp("2026-06-01"))]

    t = df["ts"]
    sess = np.where(t.dt.time > pd.Timestamp("17:00").time(), (t + pd.Timedelta(days=1)).dt.date, t.dt.date)
    df = df.assign(sess=sess, minute=t.dt.hour * 60 + t.dt.minute)
    df = df[(df["sess"] >= START) & (df["sess"] <= END)]
    df = df.sort_values("ts", kind="mergesort")

    m0930, m0931, m1556, m1600, m1700 = 570, 571, 956, 960, 1020
    rth = df[(df["minute"] >= m0931) & (df["minute"] <= m1600)]
    counts = rth.groupby("sess").size()
    late = rth[rth["minute"] >= m1556].groupby("sess").size()
    has_seed = df[df["minute"] <= m0930].groupby("sess").size()
    qual = counts[counts >= 300].index.intersection(late.index).intersection(has_seed.index)
    qual = np.array(sorted(qual))
    n = len(qual)
    sess_pos = {s: i for i, s in enumerate(qual)}

    dfq = df[df["sess"].isin(sess_pos)]

    # closes grid (09:30 seed .. 16:00), forward-filled — identical to F5 R2
    C = np.full((n, N_RET + 1), np.nan)
    seeds = dfq[dfq["minute"] <= m0930].groupby("sess")["close"].last()
    for s, v in seeds.items():
        C[sess_pos[s], 0] = v
    inwin = dfq[(dfq["minute"] >= m0931) & (dfq["minute"] <= m1600)]
    rows = inwin["sess"].map(sess_pos).to_numpy()
    cols = inwin["minute"].to_numpy() - m0931 + 1
    C[rows, cols] = inwin["close"].to_numpy()
    for j in range(1, N_RET + 1):
        m = np.isnan(C[:, j])
        C[m, j] = C[m, j - 1]
    assert not np.isnan(C).any(), "unseeded session slipped through qualification"

    D = C[:, grid_idx(16, 0) + 1] - C[:, grid_idx(15, 50) + 1]  # dislocation, POINTS
    c1600 = C[:, grid_idx(16, 0) + 1]

    # exit bar per session: LAST raw bar stamped <= 09:30 (its close == C[:,0] seed)
    seed_bars = dfq[dfq["minute"] <= m0930].groupby("sess").agg(exit_close=("close", "last"), exit_ts=("ts", "last"))
    exit_close = np.full(n, np.nan)
    exit_ts = np.empty(n, dtype=object)
    for s, r in seed_bars.iterrows():
        exit_close[sess_pos[s]] = r["exit_close"]
        exit_ts[sess_pos[s]] = r["exit_ts"]
    assert np.allclose(exit_close, C[:, 0]), "exit bar close != grid 09:30 seed close"

    # primary entry: FIRST raw bar stamped in (16:00,17:00] on the signal session (R2)
    late_tape = dfq[(dfq["minute"] > m1600) & (dfq["minute"] <= m1700)].groupby("sess").agg(
        eo=("open", "first"), ets=("ts", "first"))
    entry_open = np.full(n, np.nan)
    entry_ts = np.empty(n, dtype=object)
    entry_case = np.array(["none"] * n, dtype=object)
    for s, r in late_tape.iterrows():
        i = sess_pos[s]
        entry_open[i] = r["eo"]
        entry_ts[i] = r["ets"]
        entry_case[i] = "late_tape_1601"
    # fallback source: FIRST raw bar of each session (overnight tape opens the session)
    first_bar = dfq.groupby("sess").agg(fo=("open", "first"), fts=("ts", "first"))
    fb_open = np.full(n, np.nan)
    fb_ts = np.empty(n, dtype=object)
    for s, r in first_bar.iterrows():
        fb_open[sess_pos[s]] = r["fo"]
        fb_ts[sess_pos[s]] = r["fts"]

    return qual, D, c1600, exit_close, exit_ts, entry_open, entry_ts, entry_case, fb_open, fb_ts


def trailing_edges(Dvec: np.ndarray, q: float) -> np.ndarray:
    """Causal trailing-TRAIL quantile: edge[i] = quantile(D[i-TRAIL:i], q); nan for i<TRAIL."""
    n = len(Dvec)
    out = np.full(n, np.nan)
    if n > TRAIL:
        W = np.lib.stride_tricks.sliding_window_view(Dvec, TRAIL)  # W[j] = D[j..j+TRAIL-1]
        out[TRAIL:] = np.quantile(W[: n - TRAIL], q, axis=1)       # edge for i uses D[i-TRAIL..i-1]
    return out


def main():
    t0 = _time.time()
    lines = []

    def P(s=""):
        print(s)
        lines.append(s)

    sha = sha256_file(SUBSTRATE)
    assert sha == SUBSTRATE_SHA_EXPECTED, f"substrate hash drift: {sha}"

    P("=" * 100)
    P("G2_F6_AUCTREV01_20260829 — MC-46 EOD DISLOCATION REVERSION ECONOMICS (trial G00032)")
    P("printed by src/auctrev01_mc46_econ.py — GATE/SPEC/OBSERVED/PASS-FAIL assembled by program only")
    P(f"substrate: {SUBSTRATE}")
    P(f"substrate sha256: {sha} (== GENESIS_REPRO_INCUMBENT_20260828 provenance)")
    P(f"python {sys.version.split()[0]}  numpy {np.__version__}  pandas {pd.__version__}")
    P(f"seed={SEED}  E2 draws={K_CONTROL}  E3 shifts={K_NULL}  trailing={TRAIL} sessions")
    P(f"costs: gate $35/ctrRT = {COST35} pts; stress $40/ctrRT = {COST40} pts (NQ $20/pt)")
    P("policy frozen: D = close16:00 - close15:50; BOTTOM trailing decile -> LONG 1; window per")
    P("  R1/R2 = entry first-tradable-bar open at 16:00 (NOT in halt; case documented), exit next")
    P("  qualifying session 09:30-seed bar close. evidence status: DISCOVERY_CONSUMED")
    P("=" * 100)

    (sess, D, c1600, exit_close, exit_ts, entry_open, entry_ts, entry_case, fb_open, fb_ts) = load_sessions()
    n = len(sess)
    era1 = sess <= ERA1_END
    era2 = sess >= date(2016, 1, 1)

    # ---- next qualifying session (gap <= 7 cal days), tradable outcome per session ----
    nxt = np.full(n, -1)
    for i in range(n - 1):
        if (sess[i + 1] - sess[i]).days <= 7:
            nxt[i] = i + 1
    has_next = nxt >= 0

    # apply entry fallback where signal session lacks (16:00,17:00] tape (R2)
    use_fb = (entry_case == "none") & has_next
    for i in np.flatnonzero(use_fb):
        j = nxt[i]
        if np.isfinite(fb_open[j]) and fb_ts[j] <= exit_ts[j]:
            entry_open[i] = fb_open[j]
            entry_ts[i] = fb_ts[j]
            entry_case[i] = "overnight_fallback"
    n_fallback = int((entry_case == "overnight_fallback").sum())

    ok = has_next & np.isfinite(entry_open)                       # tradable outcome exists
    gross = np.full(n, np.nan)                                    # LONG gross, POINTS
    gross[ok] = exit_close[nxt[ok]] - entry_open[ok]
    exit_ts_evt = np.empty(n, dtype=object)
    exit_close_evt = np.full(n, np.nan)
    exit_ts_evt[ok] = exit_ts[nxt[ok]]
    exit_close_evt[ok] = exit_close[nxt[ok]]

    # ---- trailing causal deciles (R4) — recomputed, NOT the diagnostic's era deciles --
    q10 = trailing_edges(D, 0.10)
    q90 = trailing_edges(D, 0.90)
    signal_valid = ~np.isnan(q10)
    bottom = signal_valid & (D < q10)
    top = signal_valid & (D > q90)

    events = bottom & ok
    events_top = top & ok
    pool = signal_valid & ok & ~bottom & ~top                     # E2 non-extreme pool
    dropped_no_next = int((bottom & ~has_next).sum())
    dropped_no_entry = int((bottom & has_next & ~np.isfinite(entry_open)).sum())

    net35 = gross - COST35
    net40 = gross - COST40
    e1_, e2_ = events & era1, events & era2
    N_ev, N1, N2 = int(events.sum()), int(e1_.sum()), int(e2_.sum())

    # ---- E2 control draws (era-stratified count-matched; R7) — computed before print --
    rng = np.random.default_rng(SEED)
    p1_idx, p2_idx = np.flatnonzero(pool & era1), np.flatnonzero(pool & era2)
    draws = np.empty(K_CONTROL)
    for k in range(K_CONTROL):
        pick = np.concatenate([rng.choice(p1_idx, size=N1, replace=False),
                               rng.choice(p2_idx, size=N2, replace=False)])
        draws[k] = net35[pick].mean()
    e2_p95 = float(np.percentile(draws, 95))

    # ---- E3 circular-shift null via null_guard (R8) — sensitivity FIRST ---------------
    frame = pd.DataFrame({"session": [s.isoformat() for s in sess], "D": D, "ok": ok, "gross": gross})

    def decision_fn(f: pd.DataFrame) -> np.ndarray:
        d = f["D"].to_numpy()
        e = trailing_edges(d, 0.10)
        return ~np.isnan(e) & (d < e)

    def statistic_fn(dec: np.ndarray, base: pd.DataFrame) -> float:
        sel = dec & base["ok"].to_numpy()
        if sel.sum() == 0:
            return np.nan
        return float((base["gross"].to_numpy()[sel] - COST35).mean())

    sens = null_guard.verify_null_sensitivity(lambda: frame, decision_fn, statistic_fn,
                                              shifts=SENS_SHIFTS, unit="session")
    nul = null_guard.run_circular_null(lambda: frame, decision_fn, statistic_fn,
                                       n_shifts=K_NULL, unit="session", seed=SEED)
    null_arr = np.asarray(nul["null_stats"], dtype=float)
    n_null_nan = int(np.isnan(null_arr).sum())
    e3_p95 = float(np.nanpercentile(null_arr, 95))
    real_stat = nul["real_stat"]

    obs_mean35 = float(net35[events].mean())
    assert abs(real_stat - obs_mean35) < 1e-9, "null_guard real stat != direct event mean"

    # ================= E0: MDE + EVENT COUNTS — BEFORE ANY RETURN TABLE ================
    P()
    P("E0 — EVENT COUNTS AND MDE (printed BEFORE any return table; hard rule 7)")
    P(f"  qualifying sessions 2006..2026-05        : {n}")
    P(f"  burn-in (first {TRAIL}, no trailing state)   : {TRAIL}")
    P(f"  signal-valid sessions                    : {int(signal_valid.sum())}")
    P(f"  BOTTOM-decile signals                    : {int(bottom.sum())}")
    P(f"  dropped: no next session <=7d            : {dropped_no_next}")
    P(f"  dropped: no tradable entry bar           : {dropped_no_entry}")
    P(f"  entry via overnight fallback             : {n_fallback} (rest = 16:01-stamped late tape)")
    P(f"  LONG events total                        : {N_ev}")
    P(f"  LONG events era 2006-2015                : {N1}")
    P(f"  LONG events era 2016-2026/05             : {N2}")
    P(f"  E2 control pool (non-extreme, valid)     : {int(pool.sum())}  (era1 {len(p1_idx)}, era2 {len(p2_idx)})")
    sd_pool = float(np.std(net35[pool], ddof=1))
    mde_t2 = 2.0 * sd_pool / np.sqrt(N_ev)
    P(f"  MDE (t=2.0, pool sd {sd_pool:.3f} pts, N={N_ev}) : {mde_t2:.3f} pts/event = ${20*mde_t2:.2f}/event")
    P(f"  E2 control p95 (count/era-matched, {K_CONTROL} draws): {e2_p95:+.4f} pts net/event")
    P(f"  E3 circular-shift null p95 ({K_NULL} shifts)     : {e3_p95:+.4f} pts net/event"
      + (f"  [{n_null_nan} nan draws excluded]" if n_null_nan else ""))
    P(f"  E3 null sensitivity (null_guard): spread {sens['spread']:.4f} pts across shifts {SENS_SHIFTS} — HAS TEETH")

    # ================= observed return tables ==========================================
    def block(sel, label):
        g, n35, n40 = gross[sel], net35[sel], net40[sel]
        N = int(sel.sum())
        t35 = float(n35.mean() / (n35.std(ddof=1) / np.sqrt(N))) if N > 1 else float("nan")
        P(f"  {label:22s} N={N:4d}  gross {g.mean():+8.3f}  net$35 {n35.mean():+8.3f}  "
          f"sd {n35.std(ddof=1):7.3f}  t(evt) {t35:+6.2f}  net$40 {n40.mean():+8.3f} pts/event")
        return N, float(n35.mean()), t35

    P()
    P("OBSERVED — LONG BOTTOM-DECILE (POINTS/event; $ = pts x 20)")
    _, mean_all, t_all = block(events, "full 2006-2026/05")
    _, mean_e1, _ = block(e1_, "era 2006-2015")
    _, mean_e2, _ = block(e2_, "era 2016-2026/05")
    drift = entry_open[events] - c1600[events]
    P(f"  R11 drift note: entry_open - close16:00 over events: mean {drift.mean():+.4f} sd {drift.std(ddof=1):.4f} pts (non-gate)")

    # ================= GATE TABLE ======================================================
    g_e1 = (mean_all > 0.0) and (t_all >= 2.0)
    g_e2 = mean_all > e2_p95
    g_e3 = mean_all > e3_p95
    g_e4 = (np.sign(mean_e1) == np.sign(mean_e2)) and mean_e1 != 0 and mean_e2 != 0
    all_pass = g_e1 and g_e2 and g_e3 and g_e4

    P()
    P("GATE TABLE — all clauses coded; verdicts printed by program ($35/ctrRT, POINTS)")
    hdr = f"  {'GATE':6s} {'SPEC':52s} {'OBSERVED':>28s} {'VERDICT':>8s}"
    P(hdr)
    P("  " + "-" * (len(hdr) - 2))
    P(f"  {'E1':6s} {'net/event > 0 AND event-clustered t >= 2.0':52s} "
      f"{f'{mean_all:+.4f} pts, t={t_all:+.2f}':>28s} {'PASS' if g_e1 else 'FAIL':>8s}")
    P(f"      clause net>0            : {'PASS' if mean_all > 0 else 'FAIL'}")
    P(f"      clause t>=2.0           : {'PASS' if t_all >= 2.0 else 'FAIL'}")
    P(f"  {'E2':6s} {f'> control p95 = {e2_p95:+.4f} (count/era-matched, {K_CONTROL} draws)':52s} "
      f"{f'{mean_all:+.4f}':>28s} {'PASS' if g_e2 else 'FAIL':>8s}")
    P(f"  {'E3':6s} {f'> circular-shift null p95 = {e3_p95:+.4f} ({K_NULL} shifts)':52s} "
      f"{f'{mean_all:+.4f}':>28s} {'PASS' if g_e3 else 'FAIL':>8s}")
    P(f"  {'E4':6s} {'net same sign in 2006-15 and 2016-26/05':52s} "
      f"{f'{mean_e1:+.4f} / {mean_e2:+.4f}':>28s} {'PASS' if g_e4 else 'FAIL':>8s}")
    P("  " + "-" * (len(hdr) - 2))
    P(f"  VERDICT: {'ALL PASS -> SURVIVED-DISCOVERY (routes to robustness + independent implementation, NOT promotion)' if all_pass else 'FAIL -> NULL at formulation'}")

    # ================= non-gate readouts ==============================================
    P()
    P("NON-GATE READOUTS")
    n40e = net40[events]
    t40 = float(n40e.mean() / (n40e.std(ddof=1) / np.sqrt(len(n40e))))
    P(f"  $40 stress (LONG, full): net {n40e.mean():+.3f} pts/event, t(evt) {t40:+.2f} "
      f"({'net>0 & t>=2 would hold' if (n40e.mean() > 0 and t40 >= 2) else 'would NOT hold'}) — reported only")
    P("  TOP-decile SHORT, same window/costs (spec: reported, never gated; dead-short-leg burden):")
    for sel, lab in ((events_top, "full"), (events_top & era1, "era 2006-2015"), (events_top & era2, "era 2016-2026/05")):
        N = int(sel.sum())
        if N > 1:
            sg35 = (entry_open[sel] - exit_close_evt[sel]) - COST35
            sg40 = (entry_open[sel] - exit_close_evt[sel]) - COST40
            ts_ = float(sg35.mean() / (sg35.std(ddof=1) / np.sqrt(N)))
            P(f"    {lab:18s} N={N:4d}  net$35 {sg35.mean():+8.3f}  t(evt) {ts_:+6.2f}  net$40 {sg40.mean():+8.3f} pts/event")
        else:
            P(f"    {lab:18s} N={N:4d}  (insufficient)")

    P()
    P(f"wall_s {int(_time.time() - t0)}")

    # ================= artifacts ======================================================
    ev_idx = np.flatnonzero(events)
    ev = pd.DataFrame({
        "session_id": [sess[i].isoformat() for i in ev_idx],
        "era": ["2006-2015" if era1[i] else "2016-2026/05" for i in ev_idx],
        "D_pts": D[ev_idx],
        "trailing_q10_pts": q10[ev_idx],
        "entry_ts": [str(entry_ts[i]) for i in ev_idx],
        "entry_open": entry_open[ev_idx],
        "entry_case": entry_case[ev_idx],
        "exit_ts": [str(exit_ts_evt[i]) for i in ev_idx],
        "exit_close": exit_close_evt[ev_idx],
        "gross_pts": gross[ev_idx],
        "net35_pts": net35[ev_idx],
        "net40_pts": net40[ev_idx],
    })
    assert_presealed(ev, "session_id", "AUCTREV01 events.csv seal check")
    ev.to_csv(os.path.join(OUT, "events.csv"), index=False)

    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    frag = {
        "kind": "RESULT",
        "trial_id": "G00032",
        "result": "PASS" if all_pass else "FAIL",
        "selected": False,
        "metrics": {
            "n_sessions": n, "n_events": N_ev, "n_events_2006_15": N1, "n_events_2016_26": N2,
            "dropped_no_next": dropped_no_next, "dropped_no_entry": dropped_no_entry,
            "entry_fallback_events": n_fallback,
            "mean_net35_pts": mean_all, "t_event_35": t_all,
            "mean_net35_era1_pts": mean_e1, "mean_net35_era2_pts": mean_e2,
            "mean_net40_pts": float(n40e.mean()), "t_event_40": t40,
            "e2_control_p95_pts": e2_p95, "e3_null_p95_pts": e3_p95,
            "e3_null_nan_draws": n_null_nan, "e3_sensitivity_spread_pts": sens["spread"],
            "mde_t2_pts": float(mde_t2), "pool_sd_pts": sd_pool,
            "gate_E1": bool(g_e1), "gate_E2": bool(g_e2), "gate_E3": bool(g_e3), "gate_E4": bool(g_e4),
            "K_control": K_CONTROL, "K_null": K_NULL, "seed": SEED,
            "cost_gate_pts": COST35, "cost_stress_pts": COST40,
            "wall_s": int(_time.time() - t0),
        },
        "note": ("MC-46 economics at frozen diagnostic geometry: trailing-252 causal BOTTOM-decile D "
                 "-> LONG overnight (16:01-bar open -> next 09:30-seed close), $35/RT. "
                 + ("ALL gates pass -> SURVIVED-DISCOVERY (robustness + independent implementation next; "
                    "NOT a promotion)." if all_pass else "Gate(s) failed -> NULL at formulation.")
                 + " Era-stratified count-matched control; null_guard-verified circular-shift null."),
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hash": None, "prev_hash": None, "seq": None,
        "pending": "orchestrator must chain hash/prev_hash/seq on append",
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(frag, f, indent=1, sort_keys=True)
    print("wrote out/gate_table.txt, out/events.csv, out/ledger_result_pending.json")


if __name__ == "__main__":
    main()
