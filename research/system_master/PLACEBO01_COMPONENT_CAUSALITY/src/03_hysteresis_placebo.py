#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLACEBO01 / component 03 -- Product B HYSTERESIS causal placebo test (turnover-matched null).

FALSIFICATION SCIENCE, not an alpha trial (campaign directive sec.44-50): the goal is to actively
try to show the real hysteresis(EntryLevel=3.0, ExitLevel=1.0) state machine is worthless -- a mere
turnover/exposure changer indistinguishable from a GENERIC, signal-blind churn-reduction mechanism
-- not to defend it. A reassuring null (real beats the generic-turnover-reduction placebo) and a
concerning result (it does not) are reported with equal rigor. Nothing below optimizes toward a
desired answer: the null-generator's two free parameters are calibrated ONLY against TURNOVER
statistics (discretionary event count, occupancy) of the REAL system, NEVER against its PnL/Sharpe/
DD, and that calibration is completed and locked in full before this script ever computes a single
placebo P&L number.

QUESTION: does Product B's actual 3.0/1.0 Schmitt-trigger hysteresis outperform a GENERIC
turnover-reduction mechanism that reduces churn by the same approximate amount but is completely
blind to signal strength (uses only the naive zero-hysteresis position sequence's own transition
TIMES, plus pure randomness, never M's magnitude) -- or is most of hysteresis's apparent value just
"reduces churn somehow", with no causal contribution from the SPECIFIC entry/exit level choice?

PREREGISTRATION (written to out/ FIRST, before any placebo P&L is computed -- see section 1 below):
  N_REPLICATIONS = 300 (>= the >=200 recommended in task instructions)
  SEED FAMILY    = 20260810 + i,  i in range(300)   (deterministic, disclosed, no time-seeding)
  NULL CONSTRUCTION (method, decided before any result is inspected):
    1. Build the REAL Product B NQ position sequence (M, hysteresis(EntryLevel=3.0,ExitLevel=1.0),
       forceFlat/entryBlocked exactly as coded) via EQV02's own certified functions (reused by
       file-path import, not re-derived).
    2. Build a NAIVE ZERO-HYSTERESIS baseline: position tracks sign(M) every bar with NO dead zone
       (immediate reversal the instant M's sign flips), under the IDENTICAL forceFlat/entryBlocked
       session-timing gates as the real system (so the C4 day-only overlay -- a separate,
       already-audited component -- is held FIXED across every arm of this test; only the
       hysteresis mechanism itself is varied).
    3. Identify the naive sequence's own "discretionary transition" bars (position changes that are
       NOT the mandatory forceFlat-driven end-of-window flatten).
    4. Build a GENERIC random-suppression/holding-extension null: walking bar-by-bar along the SAME
       discretionary-transition timeline the naive sequence already defines (never re-consulting
       M's magnitude at decision time -- only its SIGN, already baked into the naive sequence, and
       the bar-INDEX of each candidate transition), at each candidate transition bar draw one
       uniform random number and:
         - w.p. p_exit   : go FLAT and stay there for a randomly drawn "dwell" length, bootstrap-
                           sampled (with replacement) from the REAL system's own empirically
                           observed non-forced flat-dwell-run-length distribution (a TIMING-ONLY
                           statistic -- this uses real's aggregate dwell-length behaviour as a
                           calibration target, never a contemporaneous M reading);
         - w.p. p_accept : accept the naive candidate's new side (an ordinary flip/entry);
         - else          : suppress -- hold the current position unchanged ("entry suppression").
       (p_exit, p_accept) are the null's only two free parameters. They are calibrated ONCE, via a
       grid search over TURNOVER-ONLY objectives (mean discretionary-event count and mean occupancy
       across pilot seeds, matched to the REAL system's own canonical-window values) -- calibration
       NEVER touches PnL/Sharpe/DD. Pilot seeds for calibration: 9_000_000 + i, i in range(15) --
       DISJOINT from the N_REPLICATIONS scored seed family above, so no placebo realization used for
       scoring was ever inspected during parameter selection.
  MATCHING TARGETS: real system's own (within canonical window) discretionary-transition count and
    fraction-of-time-in-nonzero-position (occupancy); hold-duration distribution matched only
    approximately (as a consequence of the calibrated mechanism, not a separate optimization target)
    and reported via descriptive stats + a two-sample KS test, disclosed whichever way it comes out.
  SCORING: for each of the 300 replications, compute net P&L / Sharpe / Sortino / Calmar / maxDD via
    the SAME execution engine (Standard fill, canonical NQ commission $4.36/RT, one-bar decode-to-
    fill lag, session-close flatten) used for the REAL system, over the CLAUDE.md canonical window
    (2023-01-01T06:00:00Z .. 2025-02-02T22:59:59Z) -- reusing src/analytics/smv2_common.py's
    dd_battery() for every Sharpe/Sortino/Calmar/DD figure, per task instruction, not reimplemented.
    Empirical percentile of the REAL system's Sharpe/Net within the resulting 300-point null
    distribution is the headline statistic -- not a bare "beats placebo yes/no".

CORRECTNESS GATE (required before trusting ANY placebo result, per task instruction): the REAL
  (non-placebo) Product B NQ reconstruction is run through this script's execution engine over the
  canonical window and its net profit is checked, live, against EQV03_PNL_EQUALITY's own already-
  certified figure for the identical (object, window, execution-convention) cell
  (research/system_master/EQV03_PNL_EQUALITY/out/productB_pnl_equality.json,
  pnl_comparisons.operational.primary_claude_canonical.net_total.current = $83,363.3999999957) --
  this script's own P&L engine is a fresh, structurally-verbatim copy of the SAME exec_lagged() used
  there (Standard fill via sm01_solarsim._fill, $20/pt, $2.18/side commission, one-bar lag), so an
  exact (to-the-cent) match is the expected, required outcome, asserted below -- NOT a loose
  reasonableness check. If it fails, the script stops before generating any placebo.

REUSE, NOT REINVENTION (per task instruction): Solar13/B-MOM/decoder/hysteresis substrate comes
  verbatim from research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/src/
  02_productB_full_history.py (imported by file path, its own functions called directly -- not
  retyped). Execution/commission/fill convention comes verbatim from EQV03_PNL_EQUALITY's
  exec_lagged() (sm01_solarsim._fill/NQ_POINT_VALUE/NQ_COMM_SIDE). Sharpe/Sortino/Calmar/DD/CDaR
  battery comes verbatim from src/analytics/smv2_common.py's dd_battery()/boot_ci_mean(). This
  script's OWN, genuinely new contribution is only the naive-zero-hysteresis construction and the
  turnover-matched random-suppression/holding-extension null generator itself -- the actual object
  under test in this task.

CONSTANTS NOT TOUCHED: EntryLevel=3.0, ExitLevel=1.0, WSolar=0.7086, WBmom=2.83, TiltRescale=0.9026,
  TiltMult=1.25 are read from EQV02's module unchanged -- this script permutes/randomizes STATE
  INPUTS (the position-transition timeline), never the formula constants (that is EQV01/PERT01's
  job, per task instruction, out of scope here).

Data boundary: runs/AUDIT03_BARS/nq_3m_2022_2026.csv ends 2026-07-31T16:57, strictly before the
  2026-08-01 LOCKED_FORWARD boundary. Nothing >=2026-08-01 is read anywhere in this script. Research/
  backtest only -- no orders, no deployments, no live/Sim101 accounts touched.

Outputs:
  research/system_master/PLACEBO01_COMPONENT_CAUSALITY/out/PREREGISTRATION.json  (written FIRST)
  research/system_master/PLACEBO01_COMPONENT_CAUSALITY/out/hysteresis_placebo_results.csv
  research/system_master/PLACEBO01_COMPONENT_CAUSALITY/out/hysteresis_placebo_results.json
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))

OUT_DIR = os.path.join(ROOT, "research", "system_master", "PLACEBO01_COMPONENT_CAUSALITY", "out")
os.makedirs(OUT_DIR, exist_ok=True)

T0 = time.time()

# =============================================================================================
# 1. PREREGISTRATION -- written to disk FIRST, before any placebo (or even the naive/real) P&L is
#    computed. Locks N, seed family, and the null-construction method in writing before any result
#    (placebo or otherwise) is inspected.
# =============================================================================================
N_REPLICATIONS = 300
SCORED_SEED_FAMILY_DESC = "20260810 + i, i in range(300)"
SCORED_SEEDS = [20260810 + i for i in range(N_REPLICATIONS)]
CALIBRATION_PILOT_SEED_FAMILY_DESC = "9_000_000 + i, i in range(15) -- DISJOINT from scored family"
CALIBRATION_PILOT_SEEDS = [9_000_000 + i for i in range(15)]

preregistration = {
    "task": "PLACEBO01 component 03 -- Product B hysteresis causal placebo (turnover-matched null)",
    "written": "before any placebo, naive, or real P&L/Sharpe/DD is computed in this run",
    "directive": "campaign directive sec.44-50 -- falsification, not an alpha trial; report a "
                 "reassuring null and a concerning result with equal rigor.",
    "n_randomizations": N_REPLICATIONS,
    "scored_seed_family": SCORED_SEED_FAMILY_DESC,
    "calibration_pilot_seed_family_disjoint_from_scored": CALIBRATION_PILOT_SEED_FAMILY_DESC,
    "object_under_test": "SolarWaveOneContractNQ_v5.cs Product B hysteresis(EntryLevel=3.0,"
                          "ExitLevel=1.0) state machine",
    "window": "CLAUDE.md canonical window, 2023-01-01T06:00:00Z .. 2025-02-02T22:59:59Z (ET bars)",
    "null_construction_method": {
        "step_1": "naive zero-hysteresis baseline: position = sign(M) every bar, no dead zone, "
                  "immediate reversal on sign flip, under the IDENTICAL forceFlat/entryBlocked "
                  "session-timing gates as the real system (C4 day-only overlay held fixed across "
                  "every arm -- only the hysteresis mechanism itself is varied).",
        "step_2": "identify the naive sequence's own discretionary-transition bars (position "
                  "changes not caused by the mandatory forceFlat flatten).",
        "step_3": "walk that SAME discretionary-transition timeline (never re-reading M's "
                  "magnitude, only its sign, already baked into the naive sequence, and the bar "
                  "index of each candidate transition) and at each candidate bar draw one uniform "
                  "random number u: "
                  "w.p. p_exit -> go flat, dwell for a length bootstrap-sampled (with replacement) "
                  "from the REAL system's own empirically observed non-forced flat-dwell-run-length "
                  "distribution (timing-only statistic, not a contemporaneous M reading); "
                  "w.p. p_accept -> accept the naive candidate's side (ordinary flip/entry); "
                  "else -> suppress, hold current position unchanged (entry suppression / holding "
                  "extension).",
        "free_parameters": "(p_exit, p_accept) -- the null's only two free parameters.",
        "calibration": "grid search over (p_exit, p_accept) MINIMIZING squared relative error "
                       "against two TURNOVER-ONLY targets measured from the real system within the "
                       "canonical window -- mean discretionary-event count and mean occupancy "
                       "(fraction of bars in a nonzero position) across the 15 disjoint pilot "
                       "seeds above. Calibration NEVER inspects PnL, Sharpe, or drawdown at any "
                       "point -- it is blind to trading performance by construction, so it cannot "
                       "be used to p-hack toward a desired placebo outcome.",
        "hold_duration_matching": "NOT a separate optimization target -- reported descriptively "
                                  "(mean/median/std + two-sample KS test vs the real system's own "
                                  "hold-duration distribution) as a consequence of the calibrated "
                                  "mechanism, disclosed honestly whichever way it comes out.",
    },
    "scoring": "net P&L / Sharpe / Sortino / Calmar / maxDD via the SAME execution engine as the "
              "real system (Standard fill, canonical NQ commission $4.36/RT, one-bar decode-to-fill "
              "lag, session-close flatten backstop), reusing src/analytics/smv2_common.py's "
              "dd_battery() for every Sharpe/Sortino/Calmar/DD figure -- not reimplemented.",
    "headline_statistic": "empirical percentile of the REAL system's Sharpe (and, secondarily, Net) "
                          "within the 300-point null distribution -- reported as a percentile, not "
                          "a bare beats/does-not-beat verdict.",
    "correctness_gate": "before any placebo is generated, the REAL Product B NQ reconstruction's "
                        "canonical-window net profit (via this script's own exec_lagged()) is "
                        "checked, live, against EQV03_PNL_EQUALITY's already-certified figure for "
                        "the identical cell ($83,363.3999999957) -- an exact match is REQUIRED "
                        "(both scripts share the identical exec_lagged() construction), not a loose "
                        "reasonableness band. The script stops before generating any placebo if "
                        "this fails.",
    "constants_not_touched": "EntryLevel=3.0, ExitLevel=1.0, WSolar=0.7086, WBmom=2.83, "
                             "TiltRescale=0.9026, TiltMult=1.25 -- read from EQV02's module "
                             "unchanged; this workflow permutes STATE INPUTS only.",
}

prereg_path = os.path.join(OUT_DIR, "PREREGISTRATION.json")
with open(prereg_path, "w", encoding="utf-8") as f:
    json.dump(preregistration, f, indent=2)
print(f"[PLACEBO01-hyst] PREREGISTRATION written FIRST, before any P&L computed: {prereg_path}",
      flush=True)

# =============================================================================================
# 2. Execution constants + reused engine (verbatim from EQV03_PNL_EQUALITY/src/02_productB_pnl.py)
# =============================================================================================
from sm01_solarsim import _fill, NQ_POINT_VALUE, NQ_COMM_SIDE  # noqa: E402 -- verbatim reuse
import smv2_common as smc  # noqa: E402 -- dd_battery / boot_ci_mean, verbatim reuse, not reimplemented

PV_NQ = NQ_POINT_VALUE
COMM_NQ = NQ_COMM_SIDE
assert abs(2 * COMM_NQ - 4.36) < 1e-9, "canonical NQ commission constant drifted from $4.36/RT"


def exec_lagged(target_decided, o, h, l, c, last_of_sess_, pv, comm_side):
    """Verbatim structural copy of EQV03_PNL_EQUALITY/src/02_productB_pnl.py's exec_lagged() --
    one-bar decode-to-fill lag, Standard 1-tick-adverse-slip fill, session-close backstop."""
    n_ = len(target_decided)
    p = 0
    pend = 0
    cash = 0.0
    prev_eq = 0.0
    bar_pnl = np.zeros(n_, dtype=np.float64)
    n_fills = 0
    backstop_events = 0
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm_side
            n_fills += 1
            p = pend
        if last_of_sess_[t] and p != 0:
            backstop_events += 1
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv
            cash -= abs(p) * comm_side
            n_fills += 1
            p = 0
            pend = 0
        else:
            pend = int(target_decided[t])
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq
        prev_eq = eq
    return bar_pnl, n_fills, backstop_events


# =============================================================================================
# 3. Reuse EQV02's own Product B module (file-path import) -- substrate/decoder/hysteresis, not
#    re-derived.
# =============================================================================================
EQV02_SRC = os.path.join(ROOT, "research", "system_master", "EQV02_FULL_HISTORY_ARRAY_EQUALITY",
                          "src", "02_productB_full_history.py")
print(f"[PLACEBO01-hyst] importing EQV02's own Product B module (reuse, not re-derivation): "
      f"{EQV02_SRC}", flush=True)
spec = importlib.util.spec_from_file_location("eqv02_productB_full_history", EQV02_SRC)
eqv02b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eqv02b)

print("[PLACEBO01-hyst] loading bars + building sumNext/tiltState/bmomPos/decoder/gates via "
      "EQV02's own functions ...", flush=True)
bars = eqv02b.load_bars()
n_full = len(bars)
sumNext = eqv02b.build_sumNext(bars)
tiltState = eqv02b.build_tiltState_productB(bars)
Bmom = eqv02b.build_bmom_pos(bars)
T_arr, mm_arr, Tp_arr, M_arr, Q_B_arr = eqv02b.build_decoder(sumNext, tiltState, Bmom)
entry_blocked_full, force_flat_full = eqv02b.build_gates(bars)
times_full = bars["time"].to_numpy()
sess_date_full = bars["sess_date"].to_numpy()
open_full = bars["open"].to_numpy()
high_full = bars["high"].to_numpy()
low_full = bars["low"].to_numpy()
close_full = bars["close"].to_numpy()
last_of_sess_full = bars["is_last_of_sess"].to_numpy()
print(f"[PLACEBO01-hyst] substrate built: n={n_full} bars, {bars['time'].min()} .. "
      f"{bars['time'].max()}", flush=True)

print("[PLACEBO01-hyst] walking REAL Product B (M, hysteresis(EntryLevel=3.0,ExitLevel=1.0)) ...",
      flush=True)
pos_real_full, _ev_real_full = eqv02b.hysteresis_walk(
    M_arr, eqv02b.ENTRY_LEVEL, eqv02b.EXIT_LEVEL, force_flat_full, entry_blocked_full, times_full)

# =============================================================================================
# 4. Canonical window slice (CLAUDE.md, ET bars) -- same convention as EQV02/EQV03.
# =============================================================================================
canon_start_et = eqv02b.CANON_START_UTC.tz_convert("America/New_York").tz_localize(None)
canon_end_et = eqv02b.CANON_END_UTC.tz_convert("America/New_York").tz_localize(None)
tser = bars["time"]
mask_canonical = ((tser >= canon_start_et) & (tser <= canon_end_et)).to_numpy()
idx_canon = np.where(mask_canonical)[0]
lo, hi = int(idx_canon.min()), int(idx_canon.max())
n_w = hi - lo + 1
print(f"[PLACEBO01-hyst] canonical window: {canon_start_et} .. {canon_end_et} -> "
      f"{n_w} bars, {bars.loc[mask_canonical, 'sess_date'].nunique()} sessions", flush=True)

# confirm position is flat entering AND at the end of the canonical window (session-aligned
# boundary) -- lets every arm below be constructed by slicing rather than re-walking from t=0,
# with an explicit assertion rather than a silent assumption.
assert pos_real_full[lo - 1] == 0 and pos_real_full[lo] == 0, (
    "REAL position is not flat entering the canonical window -- window is not session-aligned as "
    "assumed; STOP, do not proceed with a windowed reconstruction.")
assert pos_real_full[hi] == 0, (
    "REAL position is not flat at the canonical window's last bar -- STOP.")
print("[PLACEBO01-hyst] canonical-window boundary precondition (flat entering & exiting) "
      "confirmed.", flush=True)

M_w = M_arr[lo:hi + 1]
ff_w = force_flat_full[lo:hi + 1]
eb_w = entry_blocked_full[lo:hi + 1]
times_w = times_full[lo:hi + 1]
sess_date_w = sess_date_full[lo:hi + 1]
open_w = open_full[lo:hi + 1]
high_w = high_full[lo:hi + 1]
low_w = low_full[lo:hi + 1]
close_w = close_full[lo:hi + 1]
last_of_sess_w = last_of_sess_full[lo:hi + 1]
pos_real_w = pos_real_full[lo:hi + 1]

# =============================================================================================
# 5. CORRECTNESS GATE -- reproduce EQV03's own certified canonical-window Product B net figure
#    BEFORE trusting anything downstream. Required exact match (same exec_lagged construction).
# =============================================================================================
print("[PLACEBO01-hyst] CORRECTNESS GATE: running REAL position array through this script's own "
      "exec_lagged() over the canonical window ...", flush=True)
bar_pnl_real_w, nfills_real, backstop_real = exec_lagged(
    pos_real_w, open_w, high_w, low_w, close_w, last_of_sess_w, PV_NQ, COMM_NQ)
net_real_this_script = float(bar_pnl_real_w.sum())

EQV03_JSON = os.path.join(ROOT, "research", "system_master", "EQV03_PNL_EQUALITY", "out",
                           "productB_pnl_equality.json")
with open(EQV03_JSON, "r", encoding="utf-8") as f:
    eqv03 = json.load(f)
certified_canonical_net = eqv03["pnl_comparisons"]["operational"]["primary_claude_canonical"][
    "net_total"]["current"]
certified_window = eqv03["windows"]["primary_claude_canonical"]

gap = net_real_this_script - certified_canonical_net
correctness_gate_pass = abs(gap) < 1.0  # exact-match expectation; $1 tolerance for float noise only
print(f"[PLACEBO01-hyst] correctness gate: this_script_net={net_real_this_script:.4f} "
      f"certified(EQV03)={certified_canonical_net:.4f} gap={gap:+.6f} "
      f"PASS={correctness_gate_pass} (window {certified_window})", flush=True)
assert correctness_gate_pass, (
    f"CORRECTNESS GATE FAILED -- this script's REAL Product B reconstruction over the canonical "
    f"window does not reproduce EQV03's certified figure (gap={gap:+.4f}). STOP -- do not proceed "
    f"to any placebo/shuffled construction until this is root-caused.")
print("[PLACEBO01-hyst] CORRECTNESS GATE PASSED -- proceeding to naive baseline + placebo null.",
      flush=True)

# =============================================================================================
# 6. NAIVE ZERO-HYSTERESIS baseline -- position tracks sign(M) every bar, no dead zone, under the
#    IDENTICAL forceFlat/entryBlocked gates as the real system.
# =============================================================================================
def naive_zero_hysteresis_walk(M, force_flat, entry_blocked):
    """Raw-sign, no-dead-zone position walk. M==0 (exact) is genuinely flat (no signal), not
    defaulted to either side. entry_blocked mirrors the real state machine's own convention:
    blocks NEW entries/reversals but a blocked reversal downgrades to a plain exit (matching
    hysteresis_walk's own 'elif s <= exit_' fallthrough shape for the p>0/p<0 branches) rather
    than silently holding the stale side."""
    n = len(M)
    pos = np.zeros(n, dtype=np.int8)
    p = 0
    for t in range(n):
        ff = bool(force_flat[t])
        eb = bool(entry_blocked[t])
        s = M[t]
        if ff:
            tgt = 0
        elif p == 0:
            if not eb:
                if s > 0:
                    tgt = 1
                elif s < 0:
                    tgt = -1
                else:
                    tgt = 0
            else:
                tgt = 0
        else:
            if s > 0:
                cand = 1
            elif s < 0:
                cand = -1
            else:
                cand = 0
            if cand == p:
                tgt = p
            else:
                tgt = 0 if eb else cand
        pos[t] = tgt
        p = tgt
    return pos


print("[PLACEBO01-hyst] building NAIVE zero-hysteresis baseline (raw sign of M, no dead zone) ...",
      flush=True)
pos_naive_w = naive_zero_hysteresis_walk(M_w, ff_w, eb_w)
assert pos_naive_w[0] == 0 or not ff_w[0], "naive walk sanity: unexpected non-flat/gated start"


def discretionary_events(pos, force_flat):
    """Bar indices where position changes vs the prior bar, EXCLUDING bars where the change is the
    mandatory forceFlat flatten (force_flat[t]=True) -- i.e., the genuinely discretionary,
    signal-driven transitions that hysteresis vs. no-hysteresis vs. the placebo null actually
    differ on."""
    n = len(pos)
    ev = []
    for t in range(1, n):
        if pos[t] != pos[t - 1] and not force_flat[t]:
            ev.append(t)
    return np.array(ev, dtype=np.int64)


def hold_runs(pos):
    """Run-lengths (in bars) of maximal constant-nonzero-position spells."""
    n = len(pos)
    runs = []
    cur_val = pos[0]
    cur_len = 1
    for t in range(1, n):
        if pos[t] == cur_val:
            cur_len += 1
        else:
            if cur_val != 0:
                runs.append(cur_len)
            cur_val = pos[t]
            cur_len = 1
    if cur_val != 0:
        runs.append(cur_len)
    return np.array(runs)


def flat_dwell_runs_genuine(pos, force_flat):
    """Run-lengths (bars) of pos==0 spells that were NOT initiated by the mandatory forceFlat
    flatten (i.e., genuine hysteresis-driven 'wait it out' dwelling, not the routine pre-close
    flatten). Used ONLY as a bootstrap source for the null generator's dwell-length draws -- a
    timing-only aggregate statistic, never a per-bar signal reading."""
    n = len(pos)
    runs = []
    t = 0
    while t < n:
        if pos[t] == 0:
            start = t
            forced = bool(force_flat[t]) and (t > 0 and pos[t - 1] != 0)
            while t < n and pos[t] == 0:
                t += 1
            length = t - start
            if not forced:
                runs.append(length)
        else:
            t += 1
    return np.array(runs)


ev_real_disc = discretionary_events(pos_real_w, ff_w)
ev_naive_disc = discretionary_events(pos_naive_w, ff_w)
runs_real = hold_runs(pos_real_w)
runs_naive = hold_runs(pos_naive_w)
occ_real = float((pos_real_w != 0).mean())
occ_naive = float((pos_naive_w != 0).mean())
DWELL_POOL = flat_dwell_runs_genuine(pos_real_w, ff_w).astype(np.int64)

TARGET_EVENTS = len(ev_real_disc)
TARGET_OCC = occ_real

print(f"[PLACEBO01-hyst] REAL:  n_discretionary_events={len(ev_real_disc)} "
      f"occupancy={occ_real:.4f} hold_mean={runs_real.mean():.2f} "
      f"hold_median={float(np.median(runs_real)):.2f} n_holds={len(runs_real)}", flush=True)
print(f"[PLACEBO01-hyst] NAIVE: n_discretionary_events={len(ev_naive_disc)} "
      f"occupancy={occ_naive:.4f} hold_mean={runs_naive.mean():.2f} "
      f"hold_median={float(np.median(runs_naive)):.2f} n_holds={len(runs_naive)}", flush=True)
print(f"[PLACEBO01-hyst] dwell-length bootstrap pool (real, genuine non-forced flat spells): "
      f"n={len(DWELL_POOL)} mean={DWELL_POOL.mean():.2f} median={float(np.median(DWELL_POOL)):.2f}",
      flush=True)

# =============================================================================================
# 7. NULL GENERATOR -- random entry-suppression + holding-extension applied to the naive sequence's
#    own discretionary-transition timeline. See module docstring / PREREGISTRATION.json section
#    "null_construction_method" for the full, pre-committed specification.
# =============================================================================================
def build_null_path(pos_naive, force_flat, events_bars, p_exit, p_accept, dwell_pool, rng, n):
    pos = np.zeros(n, dtype=np.int8)
    p = 0
    dwell_remaining = 0
    ei = 0
    ne = len(events_bars)
    for t in range(n):
        is_event = (ei < ne and events_bars[ei] == t)
        if force_flat[t]:
            p = 0
            dwell_remaining = 0
        elif dwell_remaining > 0:
            p = 0
            dwell_remaining -= 1
        elif is_event:
            cand = pos_naive[t]
            if p == 0:
                if rng.random() < p_accept:
                    p = cand
                # else: stay flat (no distinct "exit" concept from an already-flat state)
            else:
                u = rng.random()
                if u < p_exit:
                    p = 0
                    d = int(dwell_pool[rng.integers(0, len(dwell_pool))])
                    dwell_remaining = max(d - 1, 0)
                elif u < p_exit + p_accept:
                    p = cand
                # else: suppress -- hold current position (entry suppression)
        if is_event:
            ei += 1
        pos[t] = p
    return pos


def null_turnover_stats(p_exit, p_accept, seed):
    rng = np.random.default_rng(seed)
    pos_null = build_null_path(pos_naive_w, ff_w, ev_naive_disc, p_exit, p_accept, DWELL_POOL,
                                rng, n_w)
    ev = discretionary_events(pos_null, ff_w)
    occ = float((pos_null != 0).mean())
    return len(ev), occ


print("[PLACEBO01-hyst] CALIBRATING (p_exit, p_accept) via a turnover/occupancy-ONLY grid search "
      "(pilot seeds, disjoint from the scored family, NO PnL/Sharpe touched) ...", flush=True)
t_cal = time.time()
P_EXIT_GRID = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
P_ACCEPT_GRID = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
calib_results = []
best = None
for p_exit in P_EXIT_GRID:
    for p_accept in P_ACCEPT_GRID:
        evs, occs = [], []
        for seed in CALIBRATION_PILOT_SEEDS:
            n_ev, occ = null_turnover_stats(p_exit, p_accept, seed)
            evs.append(n_ev)
            occs.append(occ)
        mev, mocc = float(np.mean(evs)), float(np.mean(occs))
        err = ((mev - TARGET_EVENTS) / TARGET_EVENTS) ** 2 + ((mocc - TARGET_OCC) / TARGET_OCC) ** 2
        calib_results.append({"p_exit": p_exit, "p_accept": p_accept, "mean_events": mev,
                               "mean_occupancy": mocc, "sq_rel_err": err})
        if best is None or err < best["sq_rel_err"]:
            best = calib_results[-1]

P_EXIT, P_ACCEPT = best["p_exit"], best["p_accept"]
print(f"[PLACEBO01-hyst] calibration done in {time.time() - t_cal:.1f}s. BEST (p_exit={P_EXIT}, "
      f"p_accept={P_ACCEPT}) -> pilot mean_events={best['mean_events']:.1f} "
      f"(target {TARGET_EVENTS}), pilot mean_occupancy={best['mean_occupancy']:.4f} "
      f"(target {TARGET_OCC:.4f}), sq_rel_err={best['sq_rel_err']:.6f}", flush=True)

# hold-duration match diagnostic at the calibrated parameters (descriptive only, not optimized)
diag_rng = np.random.default_rng(CALIBRATION_PILOT_SEEDS[0])
pos_null_diag = build_null_path(pos_naive_w, ff_w, ev_naive_disc, P_EXIT, P_ACCEPT, DWELL_POOL,
                                 diag_rng, n_w)
runs_null_diag = hold_runs(pos_null_diag)
try:
    from scipy import stats as _st
    ks_stat, ks_p = _st.ks_2samp(runs_real, runs_null_diag)
except Exception:
    ks_stat, ks_p = float("nan"), float("nan")
hold_match_diag = {
    "real_hold_mean": float(runs_real.mean()), "real_hold_median": float(np.median(runs_real)),
    "real_hold_std": float(runs_real.std()), "real_n_holds": int(len(runs_real)),
    "null_diag_hold_mean": float(runs_null_diag.mean()),
    "null_diag_hold_median": float(np.median(runs_null_diag)),
    "null_diag_hold_std": float(runs_null_diag.std()), "null_diag_n_holds": int(len(runs_null_diag)),
    "ks_statistic": float(ks_stat), "ks_pvalue": float(ks_p),
    "note": "descriptive diagnostic at ONE pilot seed, not an optimization target; disclosed as-is.",
}
print(f"[PLACEBO01-hyst] hold-duration match diagnostic (1 pilot seed): real mean/median="
      f"{hold_match_diag['real_hold_mean']:.1f}/{hold_match_diag['real_hold_median']:.1f}  "
      f"null mean/median={hold_match_diag['null_diag_hold_mean']:.1f}/"
      f"{hold_match_diag['null_diag_hold_median']:.1f}  KS stat={ks_stat:.4f} p={ks_p:.4f}",
      flush=True)

# =============================================================================================
# 8. SCORING -- REAL, NAIVE (context only, not the tested null), and the N_REPLICATIONS
#    preregistered scored placebo nulls, all through the SAME exec_lagged() engine, all
#    Sharpe/Sortino/Calmar/DD via smv2_common.dd_battery() (reused, not reimplemented).
# =============================================================================================
def daily_net(bar_pnl, sess_dates):
    return pd.Series(bar_pnl).groupby(pd.Series(sess_dates)).sum()


d_real = daily_net(bar_pnl_real_w, sess_date_w)
real_batt = smc.dd_battery(d_real.index, d_real.to_numpy(), label="REAL_hysteresis_3_1")
real_batt["net"] = float(d_real.to_numpy().sum())
ci_lo, ci_hi, p_pos = smc.boot_ci_mean(d_real.to_numpy(), block=5, n_boot=10000, seed=20260808)
real_batt["boot_ci90_daily_mean"] = [float(ci_lo), float(ci_hi)]
real_batt["boot_p_daily_mean_positive"] = float(p_pos)

bar_pnl_naive_w, nfills_naive, backstop_naive = exec_lagged(
    pos_naive_w, open_w, high_w, low_w, close_w, last_of_sess_w, PV_NQ, COMM_NQ)
d_naive = daily_net(bar_pnl_naive_w, sess_date_w)
naive_batt = smc.dd_battery(d_naive.index, d_naive.to_numpy(), label="NAIVE_zero_hysteresis")
naive_batt["net"] = float(d_naive.to_numpy().sum())

print(f"[PLACEBO01-hyst] REAL  net=${real_batt['net']:,.2f} sharpe={real_batt['sharpe']:.4f} "
      f"maxDD_eod=${real_batt['maxDD_eod']:,.2f}", flush=True)
print(f"[PLACEBO01-hyst] NAIVE net=${naive_batt['net']:,.2f} sharpe={naive_batt['sharpe']:.4f} "
      f"maxDD_eod=${naive_batt['maxDD_eod']:,.2f}  (context only -- not the tested null)",
      flush=True)

print(f"[PLACEBO01-hyst] running {N_REPLICATIONS} PREREGISTERED scored placebo replications "
      f"(seed family {SCORED_SEED_FAMILY_DESC}) ...", flush=True)
t_score = time.time()
null_rows = []
for i, seed in enumerate(SCORED_SEEDS):
    rng = np.random.default_rng(seed)
    pos_null = build_null_path(pos_naive_w, ff_w, ev_naive_disc, P_EXIT, P_ACCEPT, DWELL_POOL,
                                rng, n_w)
    bar_pnl_null, nfills_null, backstop_null = exec_lagged(
        pos_null, open_w, high_w, low_w, close_w, last_of_sess_w, PV_NQ, COMM_NQ)
    d_null = daily_net(bar_pnl_null, sess_date_w)
    batt = smc.dd_battery(d_null.index, d_null.to_numpy(), label=f"null_seed_{seed}")
    ev_null = discretionary_events(pos_null, ff_w)
    runs_null = hold_runs(pos_null)
    null_rows.append({
        "rep": i, "seed": seed,
        "net": float(d_null.to_numpy().sum()),
        "sharpe": batt["sharpe"], "sortino": batt["sortino"], "calmar": batt["calmar"],
        "maxDD_eod": batt["maxDD_eod"], "CDaR5": batt["CDaR5"], "ulcer": batt["ulcer"],
        "n_discretionary_events": int(len(ev_null)),
        "occupancy": float((pos_null != 0).mean()),
        "hold_mean": float(runs_null.mean()) if len(runs_null) else 0.0,
        "hold_median": float(np.median(runs_null)) if len(runs_null) else 0.0,
        "n_holds": int(len(runs_null)),
        "n_fills": int(nfills_null), "backstop_events": int(backstop_null),
    })
    if (i + 1) % 50 == 0:
        print(f"[PLACEBO01-hyst]   ... {i + 1}/{N_REPLICATIONS} replications scored "
              f"({time.time() - t_score:.1f}s elapsed)", flush=True)

null_df = pd.DataFrame(null_rows)
print(f"[PLACEBO01-hyst] all {N_REPLICATIONS} scored replications complete in "
      f"{time.time() - t_score:.1f}s.", flush=True)

# =============================================================================================
# 9. HEADLINE COMPARISON -- empirical percentile of REAL within the null distribution.
# =============================================================================================
def empirical_percentile(real_value, null_values):
    """Percentile RANK of real_value within null_values (0-100): fraction of null draws that are
    <= real_value, mid-rank-adjusted for ties (standard empirical-CDF percentile)."""
    arr = np.asarray(null_values, dtype=float)
    n = len(arr)
    less = np.sum(arr < real_value)
    equal = np.sum(arr == real_value)
    return 100.0 * (less + 0.5 * equal) / n


pctl_sharpe = empirical_percentile(real_batt["sharpe"], null_df["sharpe"].to_numpy())
pctl_net = empirical_percentile(real_batt["net"], null_df["net"].to_numpy())
pctl_maxdd = empirical_percentile(real_batt["maxDD_eod"], null_df["maxDD_eod"].to_numpy())
# for maxDD, LOWER is better -- report the "beats" direction explicitly, not just raw percentile
pctl_maxdd_favorable = 100.0 - pctl_maxdd

real_beats_median = bool(pctl_sharpe > 50.0)
real_significantly_beats = bool(pctl_sharpe >= 95.0)
real_significantly_worse = bool(pctl_sharpe <= 5.0)

null_summary = {
    "sharpe": {"mean": float(null_df["sharpe"].mean()), "std": float(null_df["sharpe"].std()),
               "p5": float(null_df["sharpe"].quantile(0.05)),
               "p50": float(null_df["sharpe"].quantile(0.50)),
               "p95": float(null_df["sharpe"].quantile(0.95))},
    "net": {"mean": float(null_df["net"].mean()), "std": float(null_df["net"].std()),
            "p5": float(null_df["net"].quantile(0.05)), "p50": float(null_df["net"].quantile(0.50)),
            "p95": float(null_df["net"].quantile(0.95))},
    "maxDD_eod": {"mean": float(null_df["maxDD_eod"].mean()), "std": float(null_df["maxDD_eod"].std()),
                  "p5": float(null_df["maxDD_eod"].quantile(0.05)),
                  "p50": float(null_df["maxDD_eod"].quantile(0.50)),
                  "p95": float(null_df["maxDD_eod"].quantile(0.95))},
    "n_discretionary_events": {"mean": float(null_df["n_discretionary_events"].mean()),
                                "std": float(null_df["n_discretionary_events"].std())},
    "occupancy": {"mean": float(null_df["occupancy"].mean()), "std": float(null_df["occupancy"].std())},
}

print("\n" + "=" * 90, flush=True)
print("PLACEBO01 / HYSTERESIS -- HEADLINE RESULT", flush=True)
print("=" * 90, flush=True)
print(f"REAL  Sharpe={real_batt['sharpe']:.4f}  Net=${real_batt['net']:,.2f}  "
      f"maxDD=${real_batt['maxDD_eod']:,.2f}", flush=True)
print(f"NULL  Sharpe mean={null_summary['sharpe']['mean']:.4f} std={null_summary['sharpe']['std']:.4f} "
      f"[p5={null_summary['sharpe']['p5']:.4f}, p50={null_summary['sharpe']['p50']:.4f}, "
      f"p95={null_summary['sharpe']['p95']:.4f}]", flush=True)
print(f"REAL Sharpe empirical percentile within null distribution: {pctl_sharpe:.2f}", flush=True)
print(f"REAL Net    empirical percentile within null distribution: {pctl_net:.2f}", flush=True)
print(f"REAL maxDD  empirical percentile (favorable direction, lower DD = higher): "
      f"{pctl_maxdd_favorable:.2f}", flush=True)
print(f"real_beats_median_null={real_beats_median}  "
      f"significant_outperformance(p>=95)={real_significantly_beats}  "
      f"significant_underperformance(p<=5)={real_significantly_worse}", flush=True)
print("=" * 90 + "\n", flush=True)

# =============================================================================================
# 10. WRITE OUTPUTS
# =============================================================================================
csv_path = os.path.join(OUT_DIR, "hysteresis_placebo_results.csv")
out_df = null_df.copy()
out_df.insert(0, "arm", "NULL_placebo")
real_row = pd.DataFrame([{
    "arm": "REAL_hysteresis_3_1", "rep": -1, "seed": None, "net": real_batt["net"],
    "sharpe": real_batt["sharpe"], "sortino": real_batt["sortino"], "calmar": real_batt["calmar"],
    "maxDD_eod": real_batt["maxDD_eod"], "CDaR5": real_batt["CDaR5"], "ulcer": real_batt["ulcer"],
    "n_discretionary_events": len(ev_real_disc), "occupancy": occ_real,
    "hold_mean": float(runs_real.mean()), "hold_median": float(np.median(runs_real)),
    "n_holds": int(len(runs_real)), "n_fills": int(nfills_real),
    "backstop_events": int(backstop_real),
}])
naive_row = pd.DataFrame([{
    "arm": "NAIVE_zero_hysteresis_context_only", "rep": -2, "seed": None, "net": naive_batt["net"],
    "sharpe": naive_batt["sharpe"], "sortino": naive_batt["sortino"], "calmar": naive_batt["calmar"],
    "maxDD_eod": naive_batt["maxDD_eod"], "CDaR5": naive_batt["CDaR5"], "ulcer": naive_batt["ulcer"],
    "n_discretionary_events": len(ev_naive_disc), "occupancy": occ_naive,
    "hold_mean": float(runs_naive.mean()), "hold_median": float(np.median(runs_naive)),
    "n_holds": int(len(runs_naive)), "n_fills": int(nfills_naive),
    "backstop_events": int(backstop_naive),
}])
full_csv = pd.concat([real_row, naive_row, out_df], ignore_index=True)
full_csv.to_csv(csv_path, index=False)
print(f"[PLACEBO01-hyst] wrote {csv_path}", flush=True)

result = {
    "task": "PLACEBO01 component 03 -- Product B hysteresis(3.0,1.0) causal placebo, "
            "turnover-matched null (generic random suppression/extension)",
    "generated": "2026-08-10",
    "preregistration_file": prereg_path,
    "n_randomizations": N_REPLICATIONS,
    "scored_seed_family": SCORED_SEED_FAMILY_DESC,
    "calibration_pilot_seed_family": CALIBRATION_PILOT_SEED_FAMILY_DESC,
    "window": {"start": str(canon_start_et), "end": str(canon_end_et), "n_bars": int(n_w),
               "n_sessions": int(bars.loc[mask_canonical, "sess_date"].nunique())},
    "correctness_gate": {
        "this_script_real_net_canonical_window": net_real_this_script,
        "certified_reference": {"source": "research/system_master/EQV03_PNL_EQUALITY/out/"
                                          "productB_pnl_equality.json "
                                          "pnl_comparisons.operational.primary_claude_canonical."
                                          "net_total.current",
                                 "value": certified_canonical_net},
        "gap": gap, "pass": correctness_gate_pass,
    },
    "null_construction": {
        "mechanism": "naive zero-hysteresis (sign(M), no dead zone, same forceFlat/entryBlocked "
                    "gates as real) with random entry-suppression + holding-extension applied to "
                    "its own discretionary-transition timeline; two free parameters (p_exit, "
                    "p_accept) calibrated via a turnover/occupancy-ONLY grid search (never "
                    "touching PnL/Sharpe/DD), dwell-length draws bootstrap-sampled from the real "
                    "system's own empirically observed non-forced flat-dwell-run-length "
                    "distribution.",
        "calibrated_p_exit": P_EXIT, "calibrated_p_accept": P_ACCEPT,
        "calibration_grid": {"p_exit_grid": P_EXIT_GRID, "p_accept_grid": P_ACCEPT_GRID,
                              "pilot_seeds": CALIBRATION_PILOT_SEEDS,
                              "objective": "sum of squared relative error vs (target discretionary "
                                          "event count, target occupancy), both measured on the "
                                          "REAL system within the canonical window"},
        "calibration_target": {"n_discretionary_events": TARGET_EVENTS, "occupancy": TARGET_OCC},
        "calibration_achieved_pilot": {"mean_events": best["mean_events"],
                                       "mean_occupancy": best["mean_occupancy"],
                                       "sq_rel_err": best["sq_rel_err"]},
        "dwell_bootstrap_pool": {"n": int(len(DWELL_POOL)), "mean": float(DWELL_POOL.mean()),
                                 "median": float(np.median(DWELL_POOL))},
        "hold_duration_match_diagnostic": hold_match_diag,
        "all_calibration_grid_results": calib_results,
    },
    "real_system": {
        "net": real_batt["net"], "sharpe": real_batt["sharpe"], "sortino": real_batt["sortino"],
        "calmar": real_batt["calmar"], "maxDD_eod": real_batt["maxDD_eod"],
        "CDaR5": real_batt["CDaR5"], "ulcer": real_batt["ulcer"],
        "n_discretionary_events": int(len(ev_real_disc)), "occupancy": occ_real,
        "hold_mean": float(runs_real.mean()), "hold_median": float(np.median(runs_real)),
        "n_holds": int(len(runs_real)),
        "boot_ci90_daily_mean": real_batt["boot_ci90_daily_mean"],
        "boot_p_daily_mean_positive": real_batt["boot_p_daily_mean_positive"],
    },
    "naive_zero_hysteresis_context_only": {
        "net": naive_batt["net"], "sharpe": naive_batt["sharpe"], "sortino": naive_batt["sortino"],
        "calmar": naive_batt["calmar"], "maxDD_eod": naive_batt["maxDD_eod"],
        "n_discretionary_events": int(len(ev_naive_disc)), "occupancy": occ_naive,
        "note": "NOT the tested null (far more turnover than real, no calibration) -- reported "
                "only as descriptive context for how much hysteresis changes turnover in the "
                "first place.",
    },
    "null_distribution_summary": null_summary,
    "headline": {
        "real_sharpe_empirical_percentile_in_null": pctl_sharpe,
        "real_net_empirical_percentile_in_null": pctl_net,
        "real_maxDD_empirical_percentile_favorable_direction": pctl_maxdd_favorable,
        "real_beats_median_null": real_beats_median,
        "real_significantly_outperforms_null_p_ge_95": real_significantly_beats,
        "real_significantly_underperforms_null_p_le_5": real_significantly_worse,
    },
    "interpretation": (
        "Real hysteresis(3.0,1.0)'s Sharpe over the canonical window sits at the "
        f"{pctl_sharpe:.1f}th percentile of {N_REPLICATIONS} turnover-matched generic-suppression "
        "nulls (nulls calibrated to real's own discretionary-trade-count and occupancy, but blind "
        "to M's magnitude throughout). "
        + ("This is a REASSURING result for the SPECIFIC 3.0/1.0 entry/exit construction: it beats "
           "the median of a generic churn-reducer with matched turnover, suggesting the particular "
           "threshold choice (not just 'reduces churn somehow') contributes real value."
           if real_beats_median
           else "This is a CONCERNING result for the SPECIFIC 3.0/1.0 entry/exit construction: it "
           "does NOT beat the median of a generic churn-reducer with matched turnover, suggesting "
           "most of hysteresis's apparent value may be attributable to turnover/exposure reduction "
           "in general, not the specific signal-informed threshold placement.")
        + (" The result clears the p>=95 bar for statistically distinguishable outperformance."
           if real_significantly_beats else
           " The result does NOT clear the p>=95 bar for statistically distinguishable "
           "outperformance -- report the percentile, not a binary claim." if not real_significantly_worse
           else " The result falls at or below the p<=5 bar -- real UNDERPERFORMS the generic "
           "turnover-reduction null at a level that would itself warrant scrutiny.")
    ),
    "runtime_seconds": round(time.time() - T0, 1),
}

json_path = os.path.join(OUT_DIR, "hysteresis_placebo_results.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)
print(f"[PLACEBO01-hyst] wrote {json_path}", flush=True)
print(f"[PLACEBO01-hyst] TOTAL runtime {time.time() - T0:.1f}s", flush=True)
