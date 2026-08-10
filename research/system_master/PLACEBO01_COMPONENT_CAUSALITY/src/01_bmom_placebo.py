"""PLACEBO01 -- B-MOM causal placebo test.

FALSIFICATION SCIENCE (campaign directive sec44-50), not an alpha trial. The question: does
B-MOM's real, temporally-aligned position path actually add something a same-shaped RANDOM
position path (same activation frequency, same state-duration distribution, same time-of-day
distribution, same year composition, same volatility composition) would not? A reassuring null
(real beats placebo) and a concerning result (real looks like a typical placebo draw) are BOTH
valuable and reported with equal rigor.

PREREGISTRATION: research/system_master/PLACEBO01_COMPONENT_CAUSALITY/out/PREREGISTRATION.md,
written and committed to disk BEFORE this script was run for the first time. N_REPS/BASE_SEED
below are the SAME numbers as that file -- this script does not choose them after seeing results.

REUSE, NOT REINVENTION (per this workflow's own instructions): imports
research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py verbatim -- the
campaign's own already-certified, self-checking substrate (Solar13 ensemble via
common.build_pend, B-MOM via sm_bmom's rth_3m/BAND_DAYS, HTF tilt, Product A/B decoders and their
frozen constants, dd_battery-based metrics). grid_core's own import-time self-check (incumbent
grid reproduces the certified dev-window nets, Product A $177,924.40 / Product B $301,915.92,
2022-01-03..2026-05-31) IS this script's correctness gate #1 -- it runs automatically on import
and raises AssertionError if it fails, before a single placebo replicate is built. Gate #2 (below)
additionally checks that this script's own canonical-window-sliced-then-executed real-B-MOM PnL
is identical to grid_core's full-history-then-sliced PnL, validating the (flat-at-every-session-
close) argument that lets this script run its per-bar exec loops on the much smaller canonical-
window slice alone, for speed, without changing any result.

Only bmomPos is ever shuffled here. Solar13 (T), HTF tilt state, the C4 entry-block/forced-flat
overlay, and both products' decoder formulas/constants are read verbatim from grid_core and never
touched -- this workflow permutes STATE INPUTS only, never formula constants (that is EQV01/
PERT01's job).
"""
import os
import sys
import json
import time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "system_master",
                                 "GRID01_SOLAR_RESOLUTION_CONVERGENCE", "src"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
# grid_core.py itself inserts src/analytics and runs/W18R1_M1_VOLSEASON/src on import.

OUT_DIR = os.path.join(ROOT, "research", "system_master", "PLACEBO01_COMPONENT_CAUSALITY", "out")
os.makedirs(OUT_DIR, exist_ok=True)
# NOTE: out/ is shared this session with concurrently-running sibling placebo workflows (an HTF
# placebo and a sizing placebo), which write their own generically-named PREREGISTRATION.md /
# preregistration.json into this SAME directory -- one of them overwrote this task's original
# out/PREREGISTRATION.md mid-run. The content is unaffected (recovered byte-for-byte, this
# script's N_REPS/BASE_SEED/null-construction were never read FROM that file at runtime -- it was
# only existence-checked), but the durable record now lives under a collision-resistant filename.
PREREG_PATH = os.path.join(OUT_DIR, "bmom_placebo_preregistration.md")

# ============================================================================================
# PREREGISTERED CONSTANTS -- must match out/PREREGISTRATION.md (written before this script ran)
# ============================================================================================
N_REPS = 500
BASE_SEED = 20260810
assert os.path.exists(PREREG_PATH), (
    "PREREGISTRATION.md must exist BEFORE this script runs -- write it first, per sec50.")

T0 = time.time()
print(f"[PLACEBO01] preregistration confirmed on disk: {PREREG_PATH}", flush=True)
print("[PLACEBO01] importing grid_core (correctness gate #1: certified dev-window self-check "
      "runs automatically at import) ...", flush=True)
import grid_core as GC  # noqa: E402
from smv2_common import dd_battery  # noqa: E402

print(f"[PLACEBO01] grid_core imported + self-checked in {time.time() - T0:.1f}s "
      f"(gate #1 PASS: Product A dev-window net $177,924.40, Product B dev-window net "
      f"$301,915.92, both reproduced exactly -- see grid_core's own printed self-check above)",
      flush=True)

# ============================================================================================
# 1. SLICE TO THE CANONICAL WINDOW (2023-01-01 .. 2025-02-02, grid_core.CANON_MASK)
# ============================================================================================
mask = GC.CANON_MASK
n_c = int(mask.sum())
T_c = GC._T0[mask].astype(int)
TILT_c = GC.TILT_STATE[mask]
ENTRY_BLOCKED_c = GC.ENTRY_BLOCKED_C4[mask]
FORCED_FLAT_c = GC.FORCED_FLAT_C4[mask]
LAST_c = GC.LAST[mask]
OPEN_c = GC.OPEN_[mask]
HIGH_c = GC.HIGH[mask]
LOW_c = GC.LOW[mask]
CLOSE_c = GC.CLOSE[mask]
SD_c = GC.SD[mask]
TIME_c = GC.TIME.to_numpy()[mask]
B_real_c = np.asarray(GC.B_LEG)[mask]

times_c = pd.to_datetime(pd.Series(TIME_c))
hm_c = (times_c.dt.hour * 100 + times_c.dt.minute).to_numpy()
is_rth_c = (hm_c >= 933) & (hm_c <= 1600)

print(f"[PLACEBO01] canonical-window slice: n_bars={n_c}, "
      f"{pd.Timestamp(SD_c.min()).date()}..{pd.Timestamp(SD_c.max()).date()}, "
      f"n_rth_bars={int(is_rth_c.sum())}", flush=True)

# ============================================================================================
# 2. EXECUTION LOOPS -- verbatim formulas from grid_core.product_a_exec / product_b_exec
#    (grid_core.py lines ~163-274), generalized ONLY to accept an arbitrary bmomPos array `B`
#    instead of the hardcoded GC.B_LEG, and to operate on the canonical-window-sliced arrays
#    built above instead of the full-history ones. No constant, no control-flow branch, no
#    formula differs from grid_core's own -- every constant below is read FROM grid_core
#    (GC.KSOLAR, GC.rha, GC._fill_n, ...), never re-typed.
# ============================================================================================
def product_a_exec_custom(T, B):
    m_arr = np.where((T != 0) & (TILT_c != 0) & (np.sign(T) == TILT_c), GC.TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (TILT_c > 0), GC.SHORTHALF, 1.0)
    Tpp = np.clip(GC.rha(T * m_arr * s_arr * GC.TILTRESCALE), -13, 13)
    M_a = np.clip(GC.rha(GC.KSOLAR * Tpp + GC.KBMOM * np.asarray(B)), -13, 13)
    n = len(T)
    cash = 0.0
    p = 0
    pend = 0
    prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = GC._fill_n(OPEN_c[t], HIGH_c[t], LOW_c[t], side, ticks=1)
            cash -= d * px * GC.PV_MNQ_A
            cash -= abs(d) * GC.COMM_MNQ_A
            p = pend
        if LAST_c[t] and p != 0:
            side = -1 if p > 0 else 1
            px = GC._fill_n(OPEN_c[t], HIGH_c[t], LOW_c[t], side, ticks=1, at_close=CLOSE_c[t])
            cash += p * px * GC.PV_MNQ_A
            cash -= abs(p) * GC.COMM_MNQ_A
            p = 0
            pend = 0
        else:
            tgt_raw = int(M_a[t])
            if FORCED_FLAT_c[t]:
                tgt = 0
            elif ENTRY_BLOCKED_c[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * CLOSE_c[t] * GC.PV_MNQ_A
        bar_pnl[t] = eq - prev_eq
        prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl


def _build_pos_seq_custom(M_arr):
    n = len(M_arr)
    p = 0
    pend = 0
    pos_seq = np.zeros(n, dtype=int)
    for t in range(n):
        if pend != p:
            p = pend
        if LAST_c[t] and p != 0:
            p = 0
            pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if FORCED_FLAT_c[t]:
            tgt = 0
        elif p == 0:
            tgt = 0 if ENTRY_BLOCKED_c[t] else (
                1 if M_arr[t] >= GC.ENTRY_LEVEL else (-1 if M_arr[t] <= -GC.ENTRY_LEVEL else 0))
        elif p > 0:
            if M_arr[t] <= -GC.ENTRY_LEVEL and not ENTRY_BLOCKED_c[t]:
                tgt = -1
            elif M_arr[t] <= GC.EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        else:
            if M_arr[t] >= GC.ENTRY_LEVEL and not ENTRY_BLOCKED_c[t]:
                tgt = 1
            elif M_arr[t] >= -GC.EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq


def _onelot_exec_custom(pos_seq, comm, pv):
    n = len(pos_seq)
    cash = 0.0
    p = 0
    prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    for t in range(n):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p
            side = 1 if d > 0 else -1
            if LAST_c[t]:
                px = GC._fill_n(OPEN_c[t], HIGH_c[t], LOW_c[t], side, ticks=1, at_close=CLOSE_c[t])
            else:
                px = GC._fill_n(OPEN_c[t], HIGH_c[t], LOW_c[t], side, ticks=1)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = tgt
        eq = cash + p * CLOSE_c[t] * pv
        bar_pnl[t] = eq - prev_eq
        prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl


def product_b_exec_custom(T, B):
    m_arr = np.where((T != 0) & (TILT_c != 0) & (np.sign(T) == TILT_c), GC.TILTMULT, 1.0)
    Tp = np.clip(GC.rha(T * m_arr * GC.TILTRESCALE), -13, 13)
    M = GC.WSOLAR * Tp + GC.WBMOM * np.asarray(B)
    pos_seq = _build_pos_seq_custom(M)
    bar_pos, bar_pnl = _onelot_exec_custom(pos_seq, GC.COMM_NQ, GC.PV_NQ)
    return bar_pos, bar_pnl


# ============================================================================================
# 3. CORRECTNESS GATE #2 -- canonical-window-sliced-then-executed (this script's approach, used
#    for speed) must reproduce grid_core's own full-history-then-sliced PnL EXACTLY, under the
#    REAL (unshuffled) bmomPos. Both products are flat at every session close (CLAUDE.md's own
#    frozen convention, and structurally enforced in both exec loops above), and the canonical
#    window starts exactly on a session boundary, so this is expected to hold exactly -- checked
#    here, not assumed, BEFORE any placebo replicate is built.
# ============================================================================================
print("[PLACEBO01] correctness gate #2: canonical-window-sliced exec vs grid_core full-history "
      "exec, real (unshuffled) bmomPos ...", flush=True)
bar_pos_A_real, bar_pnl_A_real = product_a_exec_custom(T_c, B_real_c)
bar_pos_B_real, bar_pnl_B_real = product_b_exec_custom(T_c, B_real_c)

ref_pnl_A = GC._bpnl_A0[mask]
ref_pnl_B = GC._bpnl_B0[mask]
gate2_maxdiff_A = float(np.max(np.abs(bar_pnl_A_real - ref_pnl_A)))
gate2_maxdiff_B = float(np.max(np.abs(bar_pnl_B_real - ref_pnl_B)))
gate2_exact_A = bool(np.array_equal(bar_pnl_A_real, ref_pnl_A))
gate2_exact_B = bool(np.array_equal(bar_pnl_B_real, ref_pnl_B))
assert gate2_maxdiff_A < 1e-6, (
    f"gate #2 FAILED for Product A: max abs bar-pnl diff {gate2_maxdiff_A} between "
    f"canonical-window-sliced exec and grid_core full-history-sliced exec -- STOP, "
    f"the slice-before-exec speed shortcut is not actually equivalent, investigate before "
    f"trusting any placebo result.")
assert gate2_maxdiff_B < 1e-6, (
    f"gate #2 FAILED for Product B: max abs bar-pnl diff {gate2_maxdiff_B} -- STOP.")
print(f"[PLACEBO01] gate #2 PASS: Product A exact={gate2_exact_A} (max diff {gate2_maxdiff_A:.2e}), "
      f"Product B exact={gate2_exact_B} (max diff {gate2_maxdiff_B:.2e})", flush=True)

net_A_real_check = float(bar_pnl_A_real.sum())
net_B_real_check = float(bar_pnl_B_real.sum())
print(f"[PLACEBO01] real B-MOM, canonical window: Product A net=${net_A_real_check:,.2f}, "
      f"Product B net=${net_B_real_check:,.2f} (no certified $ figure exists for this exact "
      f"narrower window per EQV03's own disclosure -- gate #1/#2 above are the correctness "
      f"proof, not a third certified-figure match)", flush=True)


# ============================================================================================
# 4. METRICS HELPER (net, Sharpe, maxDD, turnover -- dd_battery reused, not reimplemented)
# ============================================================================================
def daily_net_from_bar_pnl(bar_pnl):
    s = pd.Series(np.asarray(bar_pnl), index=pd.Index(SD_c, name="sess"))
    return s.groupby(level=0).sum().sort_index()


def turnover_from_bar_pos(bar_pos):
    prev = np.concatenate(([0], np.asarray(bar_pos)[:-1]))
    return float(np.sum(np.abs(np.asarray(bar_pos) - prev)))


def metrics_from_run(bar_pnl, bar_pos, label=""):
    d = daily_net_from_bar_pnl(bar_pnl)
    b = dd_battery(pd.to_datetime(d.index), d.to_numpy(), label=label)
    sharpe = b["sharpe"]
    return {
        "net": float(b["net"]),
        "sharpe": float(sharpe) if pd.notna(sharpe) else None,
        "maxDD_eod": float(b["maxDD_eod"]),
        "turnover": turnover_from_bar_pos(bar_pos),
        "n_days": int(b["n_days"]),
    }


# ============================================================================================
# 5. REAL FULL INCUMBENT and SOLAR+HTF-ONLY BASELINE (B-MOM entirely zeroed out)
# ============================================================================================
metrics_A_real = metrics_from_run(bar_pnl_A_real, bar_pos_A_real, "A_real_full")
metrics_B_real = metrics_from_run(bar_pnl_B_real, bar_pos_B_real, "B_real_full")

B_zero_c = np.zeros(n_c)
bar_pos_A_solar, bar_pnl_A_solar = product_a_exec_custom(T_c, B_zero_c)
bar_pos_B_solar, bar_pnl_B_solar = product_b_exec_custom(T_c, B_zero_c)
metrics_A_solar = metrics_from_run(bar_pnl_A_solar, bar_pos_A_solar, "A_solar_only")
metrics_B_solar = metrics_from_run(bar_pnl_B_solar, bar_pos_B_solar, "B_solar_only")

print(f"[PLACEBO01] REAL_FULL   A: net=${metrics_A_real['net']:,.2f} sharpe={metrics_A_real['sharpe']:.4f} "
      f"maxDD=${metrics_A_real['maxDD_eod']:,.2f} turnover={metrics_A_real['turnover']:.0f}", flush=True)
print(f"[PLACEBO01] SOLAR_ONLY  A: net=${metrics_A_solar['net']:,.2f} sharpe={metrics_A_solar['sharpe']:.4f} "
      f"maxDD=${metrics_A_solar['maxDD_eod']:,.2f} turnover={metrics_A_solar['turnover']:.0f}", flush=True)
print(f"[PLACEBO01] REAL_FULL   B: net=${metrics_B_real['net']:,.2f} sharpe={metrics_B_real['sharpe']:.4f} "
      f"maxDD=${metrics_B_real['maxDD_eod']:,.2f} turnover={metrics_B_real['turnover']:.0f}", flush=True)
print(f"[PLACEBO01] SOLAR_ONLY  B: net=${metrics_B_solar['net']:,.2f} sharpe={metrics_B_solar['sharpe']:.4f} "
      f"maxDD=${metrics_B_solar['maxDD_eod']:,.2f} turnover={metrics_B_solar['turnover']:.0f}", flush=True)

delta_real = {
    "A": {k: (metrics_A_real[k] - metrics_A_solar[k]) for k in ("net", "sharpe", "maxDD_eod", "turnover")},
    "B": {k: (metrics_B_real[k] - metrics_B_solar[k]) for k in ("net", "sharpe", "maxDD_eod", "turnover")},
}
print(f"[PLACEBO01] REAL marginal contribution of B-MOM (real_full - solar_only): {delta_real}", flush=True)

# ============================================================================================
# 6. NULL CONSTRUCTION -- circular per-session block shift of the REAL bmomPos path, restricted
#    to the M canonical-window sessions, hm-(time-of-day)-aligned reattachment. Vectorized via a
#    (session x hm-slot) matrix so each of the N_REPS replicates only needs O(n_rth_bars) numpy
#    fancy-indexing, not a fresh per-bar Python loop -- exec loops (path-dependent, must stay
#    per-bar) are the only per-replicate Python-loop cost.
# ============================================================================================
sess_codes, sessions_c = pd.factorize(pd.Series(SD_c), sort=True)
M = len(sessions_c)
bar_session_rank_c = sess_codes  # length n_c, values in [0, M)
print(f"[PLACEBO01] null construction: M={M} unique canonical-window sessions "
      f"({pd.Timestamp(sessions_c[0]).date()}..{pd.Timestamp(sessions_c[-1]).date()})", flush=True)

rth_hm_vals = np.unique(hm_c[is_rth_c])
n_cols = len(rth_hm_vals)
bar_hm_col_c = np.full(n_c, -1, dtype=int)
bar_hm_col_c[is_rth_c] = np.searchsorted(rth_hm_vals, hm_c[is_rth_c])

B_matrix = np.zeros((M, n_cols))
rows_fill = bar_session_rank_c[is_rth_c]
cols_fill = bar_hm_col_c[is_rth_c]
vals_fill = B_real_c[is_rth_c]
B_matrix[rows_fill, cols_fill] = vals_fill
print(f"[PLACEBO01] B_matrix built: {M} sessions x {n_cols} time-of-day slots, "
      f"{int((B_matrix != 0).sum())} nonzero (active B-MOM) cells", flush=True)


def build_B_shuf(K):
    """Circular shift by offset K: target session rank r receives donor session rank
    (r+K) mod M's OWN complete bmomPos path, reattached by matching time-of-day slot
    (defaults to flat/0 where the donor session had already ended, i.e. early closes)."""
    donor_of = (np.arange(M) + K) % M
    donor_rows_per_bar = donor_of[bar_session_rank_c[is_rth_c]]
    B_shuf = np.zeros(n_c)
    B_shuf[is_rth_c] = B_matrix[donor_rows_per_bar, bar_hm_col_c[is_rth_c]]
    return B_shuf


# sanity: K=0 (identity, never used in the real loop below) must reproduce the real path exactly
_sanity_B0 = build_B_shuf(0)
assert np.array_equal(_sanity_B0, B_real_c), (
    "sanity check failed: build_B_shuf(0) (identity shift) does not reproduce the real bmomPos "
    "array exactly -- the session/time-of-day reattachment machinery has a bug, STOP.")
print("[PLACEBO01] sanity check PASS: build_B_shuf(K=0) reproduces the real bmomPos array "
      "exactly (identity-shift control) -- reattachment machinery verified before any real "
      "(nonzero-offset) placebo replicate is built.", flush=True)

# ============================================================================================
# 7. RUN N_REPS PLACEBO REPLICATES (preregistered seed family: seed = BASE_SEED + i)
# ============================================================================================
print(f"[PLACEBO01] running {N_REPS} placebo replicates (seed family BASE_SEED={BASE_SEED} + i) "
      f"...", flush=True)
rep_rows = []
t_loop0 = time.time()
for i in range(N_REPS):
    rng = np.random.default_rng(BASE_SEED + i)
    K = int(rng.integers(1, M))  # Uniform{1,...,M-1}: never the identity shift
    B_shuf = build_B_shuf(K)

    bp_A, bpnl_A = product_a_exec_custom(T_c, B_shuf)
    bp_B, bpnl_B = product_b_exec_custom(T_c, B_shuf)
    mA = metrics_from_run(bpnl_A, bp_A, f"A_rep{i}")
    mB = metrics_from_run(bpnl_B, bp_B, f"B_rep{i}")

    rep_rows.append({
        "rep": i, "seed": BASE_SEED + i, "K": K,
        "A_net": mA["net"], "A_sharpe": mA["sharpe"], "A_maxDD_eod": mA["maxDD_eod"], "A_turnover": mA["turnover"],
        "B_net": mB["net"], "B_sharpe": mB["sharpe"], "B_maxDD_eod": mB["maxDD_eod"], "B_turnover": mB["turnover"],
    })
    if (i + 1) % 100 == 0:
        print(f"[PLACEBO01]   ... {i + 1}/{N_REPS} replicates done "
              f"({time.time() - t_loop0:.1f}s elapsed)", flush=True)

print(f"[PLACEBO01] all {N_REPS} replicates done in {time.time() - t_loop0:.1f}s", flush=True)

rep_df = pd.DataFrame(rep_rows)

# ============================================================================================
# 8. NULL DISTRIBUTION OF DeltaPnL_placebo (placebo - solar_only) AND EMPIRICAL PERCENTILE OF
#    THE REAL B-MOM CONTRIBUTION WITHIN IT, per product, per metric
# ============================================================================================
def empirical_percentile(real_val, placebo_vals):
    placebo_vals = np.asarray(placebo_vals, dtype=float)
    placebo_vals = placebo_vals[~np.isnan(placebo_vals)]
    if len(placebo_vals) == 0 or real_val is None or (isinstance(real_val, float) and np.isnan(real_val)):
        return None
    less = np.sum(placebo_vals < real_val)
    equal = np.sum(placebo_vals == real_val)
    return float(100.0 * (less + 0.5 * equal) / len(placebo_vals))


metrics_map = {"net": "net", "sharpe": "sharpe", "maxDD_eod": "maxDD_eod", "turnover": "turnover"}
percentile_report = {}
for prod, solar_m, real_m in (("A", metrics_A_solar, metrics_A_real), ("B", metrics_B_solar, metrics_B_real)):
    percentile_report[prod] = {}
    for metric in metrics_map:
        placebo_col = rep_df[f"{prod}_{metric}"].to_numpy(dtype=float)
        placebo_delta = placebo_col - solar_m[metric]
        rv = real_m[metric]
        real_delta_val = (rv - solar_m[metric]) if rv is not None else None
        pct = empirical_percentile(real_delta_val, placebo_delta)
        percentile_report[prod][metric] = {
            "real_delta": real_delta_val,
            "placebo_delta_mean": float(np.nanmean(placebo_delta)),
            "placebo_delta_std": float(np.nanstd(placebo_delta, ddof=1)),
            "placebo_delta_min": float(np.nanmin(placebo_delta)),
            "placebo_delta_max": float(np.nanmax(placebo_delta)),
            "percentile_of_real_within_null": pct,
        }
        rep_df[f"{prod}_delta_{metric}"] = placebo_delta

print("\n[PLACEBO01] ============ PERCENTILE REPORT (real B-MOM contribution within the "
      "circular-shift null) ============", flush=True)
for prod in ("A", "B"):
    print(f"  Product {prod}:", flush=True)
    for metric in metrics_map:
        r = percentile_report[prod][metric]
        print(f"    {metric:10s}: real_delta={r['real_delta']:,.4f}  "
              f"null mean={r['placebo_delta_mean']:,.4f} std={r['placebo_delta_std']:,.4f}  "
              f"percentile={r['percentile_of_real_within_null']:.1f}", flush=True)

# ============================================================================================
# 9. INTERPRETATION (mechanical rule, decided in preregistration spirit: >=95th or <=5th
#    percentile on the PRIMARY metric (net) = tail/informative; otherwise comparable to a
#    typical placebo draw = exposure/turnover only). Reported per product; net is primary,
#    others (sharpe, DD, turnover) reported alongside for the full falsification picture.
# ============================================================================================
def interpret(pct):
    if pct is None:
        return "UNDEFINED"
    if pct >= 95.0 or pct <= 5.0:
        return "TAIL (structural/informative)"
    return "COMPARABLE_TO_PLACEBO (not distinguishable from a random same-shaped path)"


interpretation = {
    prod: {metric: interpret(percentile_report[prod][metric]["percentile_of_real_within_null"])
           for metric in metrics_map}
    for prod in ("A", "B")
}
print("\n[PLACEBO01] interpretation (>=95th or <=5th percentile on a metric => TAIL/informative; "
      "else COMPARABLE_TO_PLACEBO):", flush=True)
for prod in ("A", "B"):
    print(f"  Product {prod}: {interpretation[prod]}", flush=True)

headline_pct_B_net = percentile_report["B"]["net"]["percentile_of_real_within_null"]
headline_pct_A_net = percentile_report["A"]["net"]["percentile_of_real_within_null"]
headline = (
    f"Product B (BEST_ONE_NQ) real B-MOM net-PnL marginal contribution over Solar+HTF-only lands "
    f"at the {headline_pct_B_net:.1f}th percentile of {N_REPS} circular-shift placebo draws "
    f"({interpretation['B']['net']}); Product A (continuous-sizing) lands at the "
    f"{headline_pct_A_net:.1f}th percentile ({interpretation['A']['net']})."
)
print(f"\n[PLACEBO01] HEADLINE: {headline}", flush=True)

# ============================================================================================
# 10. WRITE OUTPUTS
# ============================================================================================
csv_path = os.path.join(OUT_DIR, "bmom_placebo_results.csv")
# prepend REAL_FULL / SOLAR_ONLY as labeled special rows (rep = -1 / -2) for convenient joint
# analysis/plotting alongside the N_REPS placebo rows
special_rows = pd.DataFrame([
    {"rep": -1, "seed": None, "K": None,
     "A_net": metrics_A_real["net"], "A_sharpe": metrics_A_real["sharpe"],
     "A_maxDD_eod": metrics_A_real["maxDD_eod"], "A_turnover": metrics_A_real["turnover"],
     "B_net": metrics_B_real["net"], "B_sharpe": metrics_B_real["sharpe"],
     "B_maxDD_eod": metrics_B_real["maxDD_eod"], "B_turnover": metrics_B_real["turnover"],
     "row_type": "REAL_FULL"},
    {"rep": -2, "seed": None, "K": None,
     "A_net": metrics_A_solar["net"], "A_sharpe": metrics_A_solar["sharpe"],
     "A_maxDD_eod": metrics_A_solar["maxDD_eod"], "A_turnover": metrics_A_solar["turnover"],
     "B_net": metrics_B_solar["net"], "B_sharpe": metrics_B_solar["sharpe"],
     "B_maxDD_eod": metrics_B_solar["maxDD_eod"], "B_turnover": metrics_B_solar["turnover"],
     "row_type": "SOLAR_ONLY"},
])
rep_df_out = rep_df.copy()
rep_df_out["row_type"] = "PLACEBO"
full_csv = pd.concat([special_rows, rep_df_out], ignore_index=True, sort=False)
full_csv.to_csv(csv_path, index=False)
print(f"[PLACEBO01] wrote {csv_path} ({len(full_csv)} rows: 2 special + {N_REPS} placebo)", flush=True)

json_path = os.path.join(OUT_DIR, "bmom_placebo_results.json")
result = {
    "task": "PLACEBO01 -- B-MOM causal placebo test (circular per-session block shift)",
    "generated": "2026-08-10",
    "preregistration_file": "research/system_master/PLACEBO01_COMPONENT_CAUSALITY/out/bmom_placebo_preregistration.md",
    "n_randomizations": N_REPS,
    "seed_family": {"base_seed": BASE_SEED, "rule": "rep i (i=0..N_REPS-1) uses seed = base_seed + i"},
    "null_construction": (
        "Circular shift of the REAL, complete per-session bmomPos path across the M canonical-"
        "window sessions by a single random offset K ~ Uniform{1,...,M-1} per replicate; donor "
        "session (r+K) mod M's own intact within-day path is reattached to target session r by "
        "matching time-of-day slot (hm), defaulting to flat/0 where the donor session had already "
        "ended (early closes). Solar13/HTF/decoder formulas/constants stay real and unperturbed; "
        "only bmomPos is shuffled."
    ),
    "canonical_window": {
        "start": "2023-01-01", "end": "2025-02-02",
        "n_bars": n_c, "n_sessions_M": int(M),
        "note": "CLAUDE.md's frozen canonical window (research/system_master/GRID01.../grid_core.py "
                "CANON_START/CANON_END). No campaign-certified $ figure exists specifically for "
                "this narrower window for either product (only the 2022-01-03..2026-05-31 dev "
                "window is certified) -- correctness here rests on gate #1 (grid_core's own "
                "dev-window certified-net self-check, run at import) and gate #2 (this script's "
                "canonical-window-sliced exec reproduces grid_core's full-history-sliced exec "
                "exactly), both PASS, plus the K=0 identity-shift sanity check.",
    },
    "correctness_gates": {
        "gate1_grid_core_devwindow_selfcheck": "PASS (raised at import if it failed; see printed "
                                                "log -- Product A $177,924.40, Product B $301,915.92)",
        "gate2_canonical_slice_vs_full_history_slice": {
            "product_A_exact_match": gate2_exact_A, "product_A_max_abs_diff": gate2_maxdiff_A,
            "product_B_exact_match": gate2_exact_B, "product_B_max_abs_diff": gate2_maxdiff_B,
        },
        "sanity_K0_identity_shift_reproduces_real_path": True,
    },
    "real_full": {"A": metrics_A_real, "B": metrics_B_real},
    "solar_only": {"A": metrics_A_solar, "B": metrics_B_solar},
    "real_marginal_contribution_delta": delta_real,
    "null_summary_and_percentile": percentile_report,
    "interpretation": interpretation,
    "headline": headline,
    "runtime_seconds": round(time.time() - T0, 1),
}
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)
print(f"[PLACEBO01] wrote {json_path}", flush=True)
print(f"[PLACEBO01] total runtime {time.time() - T0:.1f}s", flush=True)
