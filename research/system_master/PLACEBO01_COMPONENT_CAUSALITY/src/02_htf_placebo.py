#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLACEBO01 -- 02_htf_placebo.py: HTF (tiltState) CAUSAL PLACEBO TEST.

FALSIFICATION SCIENCE (campaign directive sec44-50): the goal is to try to show the HTF
tilt overlay is a mere turnover/exposure changer, not to defend it. Both outcomes -- real
HTF beating the null, or real HTF failing to beat the null -- are reported with equal rigor.
This script does not choose among placebo realizations after seeing them: the number of
randomizations, the seed family, and the exact null construction are all fixed and written
to disk (PREREGISTRATION section below, and out/htf_placebo_preregistration.json) BEFORE the
randomization loop runs. Only the REAL (unshuffled) reconstruction and the CORRECTNESS GATE
are computed before the preregistration is written -- that is confirming plumbing, not
peeking at a placebo result.

============================================================================================
CORRECTNESS GATE (run FIRST, before anything placebo-related is trusted)
============================================================================================
This script reuses the campaign's own already-certified substrate: it imports
`research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py`, which on
import (a) builds the 13-member Solar ensemble (T), the B-MOM leg (B_LEG), and the real HTF
tiltState (TILT_STATE, sign of session-close vs its own trailing 50-session SMA, shift(1)),
all UNMODIFIED, and (b) self-checks that Product A / Product B reproduce the campaign's
certified dev-window (2022-01-03..2026-05-31) nets EXACTLY ($177,924.40 / $301,915.92) before
returning -- if that assertion fails, grid_core's own import raises and this script never
proceeds. This is gate #1.

Gate #2 (this script's own): the restricted-canonical-window executors defined below
(`solve_A`/`solve_B`) are verbatim-formula copies of grid_core's own `product_a_exec` /
`product_b_exec` (+ `_build_pos_seq`/`_onelot_exec`), generalized only to accept an arbitrary
`tilt_bar` array instead of reading the module-level `TILT_STATE` global, and restricted to
run ONLY over the canonical-window bars (not the full 2022-2026 history) for speed. Because
every session is guaranteed flat by its own session-close/forceFlat convention (CLAUDE.md:
"strategy is flat at every session close"), starting the restricted executor fresh (p=0,
pend=0, cash=0) at the canonical window's first bar is provably equivalent to running the
full-history executor and slicing its output to the canonical window -- confirmed EXPLICITLY
below (not just asserted) by comparing `solve_A`/`solve_B` fed the REAL, unperturbed
tiltState against `grid_core.product_a_exec`/`product_b_exec`'s own full-array net, sliced by
`CANON_MASK`. Both must match to within $0.01 or this script aborts.

============================================================================================
PREREGISTRATION (see also out/htf_placebo_preregistration.json, written by this script before
the randomization loop runs)
============================================================================================
N_RANDOMIZATIONS = 1000  (>= the 200 recommended minimum; chosen after a pure engineering
    timing check on the RESTRICTED-window executors' wall-clock cost only -- ~0.35s/rep for
    both products combined, i.e. ~6 minutes total for 1000 reps -- not after looking at any
    placebo result. 1000 reps gives a percentile quantum of 0.1%, finer than the 200-rep
    0.5% floor, at negligible extra cost.)

SEED_FAMILY = 20260810 + i, for i in range(1000)  (fixed integer seed family, per governance
    instruction; each replication i uses `np.random.default_rng(20260810 + i)` and ONLY that
    generator -- no time-seeded or unseeded randomness anywhere in this script).

NULL CONSTRUCTION -- "within-year natural-block permutation" of tiltState chronology:
  1. tiltState is inherently a SESSION-level quantity (sign of a session's close vs its own
     trailing 50-session SMA, shift(1) -- CANONICAL_MATHEMATICAL_SPEC.md), constant across all
     bars of a session. Extract the REAL, one-value-per-session sequence over the canonical
     window (2023-01-01 to 2025-02-02, 539 sessions), in chronological order.
  2. Within each CALENDAR YEAR separately (2023: 258 sessions: 2024: 259 sessions; 2025 stub:
     22 sessions), partition that year's own chronological tiltState sequence into its NATURAL
     BLOCKS -- maximal contiguous runs of an identical tiltState value (2023: 20 blocks, length
     1-106 sessions; 2024: 15 blocks, length 1-76; 2025 stub: 6 blocks, length 1-8). These are
     not an arbitrary fixed block length -- they are the tiltState series' own genuine runs,
     so this preserves the run-length distribution as exactly as a chronology permutation can:
     block SIZES are never split, merged, or resampled, only their ORDER is shuffled.
  3. Randomly permute the order of that year's own blocks (via the seeded Generator) and
     re-lay them, in the new order, onto that SAME year's own session-date slots.
  4. Concatenate across years. Broadcast the resulting per-session shuffled value back onto
     every bar of that session.
  MARGINAL DISTRIBUTION: preserved EXACTLY within each year (same multiset of session values,
    only reordered) and therefore exactly overall (canonical window = union of the 3 years).
  RUN-LENGTH DISTRIBUTION: preserved at the BLOCK level exactly (no block is ever resized).
    DISCLOSED CAVEAT (matched "as closely as a block-permutation allows", per task instruction
    -- not perfectly): after shuffling, two blocks that happen to share the same tiltState
    value can land adjacent, in which case the REALIZED (empirically re-measured) run-length
    in the shuffled series reads as one longer run than either contributing block -- this
    script measures and discloses how often that happens (see
    `run_length_disclosure` in the output JSON) rather than asserting it away.
  YEAR COMPOSITION: preserved EXACTLY (no session ever moves across a year boundary; blocks
    are shuffled only within their own year).
  TEMPORAL ALIGNMENT WITH REAL MARKET STATE: broken by construction -- the shuffled tiltState
    value attached to a given trading day did not actually occur on that trading day (except
    where a permutation trivially happens to fix a block's position, at the block level).
  Solar T (`grid_core._T0`, the incumbent 13-member consensus) and B-MOM (`grid_core.B_LEG`)
    are NEVER perturbed anywhere in this script -- only tiltState is randomized.
  ONE shared shuffled-tiltState realization is used for BOTH Product A and Product B within
    a given replication `i` (both consume "the same" HTF input in the real system, so a
    single per-rep shuffle, not two independently-drawn shuffles, is the faithful null).

MARGINAL CONTRIBUTION DEFINITION (per task instruction): for each metric X in {net, sharpe},
  marginal_X = X(full system, given tiltState array) - X(Solar+BMOM-only baseline, tiltState
  held at 0 everywhere in the canonical window -- which mechanically forces BOTH Product A's
  `mm` AND its `ss` short-halving term to 1.0, since `ss`'s own condition is itself gated on
  tiltState>0; Product B has no `ss` term, so tiltState=0 there only neutralizes `mm`).
  real_marginal_X   = marginal_X computed with the REAL, unperturbed tiltState.
  placebo_marginal_X[i] = marginal_X computed with replication i's shuffled tiltState.
  baseline itself (tiltState=0) is computed ONCE and is IDENTICAL across real and every
  placebo replication (it does not depend on tiltState by construction) -- so all 1001
  differences (1 real + 1000 placebo) share the same subtrahend.

REPORTED STATISTIC: empirical percentile of real_marginal_X within the {placebo_marginal_X[i]}
  null distribution: pct = 100 * mean(placebo_marginal_X <= real_marginal_X). Reported for
  net and Sharpe, separately for Product A and Product B -- NOT a bare beats-placebo boolean.

============================================================================================
Data boundary: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (via grid_core -> sm01_solarsim), ends
2026-07-31, strictly before the 2026-08-01 LOCKED_FORWARD boundary. This script only reads
the canonical window (2023-01-01..2025-02-02), far inside that boundary.
Outputs: out/htf_placebo_preregistration.json, out/htf_placebo_results.csv,
out/htf_placebo_results.json.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "system_master",
                                 "GRID01_SOLAR_RESOLUTION_CONVERGENCE", "src"))
# grid_core.py inserts src/analytics and runs/W18R1_M1_VOLSEASON/src itself on import.

OUT_DIR = os.path.join(ROOT, "research", "system_master",
                        "PLACEBO01_COMPONENT_CAUSALITY", "out")
os.makedirs(OUT_DIR, exist_ok=True)

T0 = time.time()

# =========================================================================================
# GATE #1 -- import the campaign's own certified substrate. grid_core's own module-level
# self-check (dev-window net == $177,924.40 / $301,915.92) runs INSIDE this import and raises
# AssertionError if it fails -- nothing below this line executes on a failed gate.
# =========================================================================================
print("[PLACEBO01-HTF] importing grid_core (certified substrate: Solar T, B-MOM leg, real "
      "tiltState, self-checked against BOTH certified dev-window nets on import) ...", flush=True)
import grid_core as GC  # noqa: E402
from grid_core import (rha, _fill_n, TILTMULT, SHORTHALF, TILTRESCALE, KSOLAR, KBMOM,
                        WSOLAR, WBMOM, ENTRY_LEVEL, EXIT_LEVEL, PV_MNQ_A, COMM_MNQ_A,
                        PV_NQ, COMM_NQ, dd_battery)  # noqa: E402

print(f"[PLACEBO01-HTF] grid_core imported + self-checked in {time.time() - T0:.1f}s "
      f"(gate #1 PASS -- see grid_core's own printed self-check line above)", flush=True)

SEED_BASE = 20260810
N_REPS = 1000

# =========================================================================================
# Canonical window slice (2023-01-01 to 2025-02-02, CLAUDE.md frozen convention, same window
# grid_core.CANON_MASK / CANON_START / CANON_END already encode).
# =========================================================================================
canon_idx = np.where(GC.CANON_MASK)[0]
n_canon = len(canon_idx)
T_c = GC._T0[canon_idx].astype(int)
B_c = np.asarray(GC.B_LEG)[canon_idx]
tilt_real_c = GC.TILT_STATE[canon_idx]
open_c = GC.OPEN_[canon_idx]; high_c = GC.HIGH[canon_idx]
low_c = GC.LOW[canon_idx]; close_c = GC.CLOSE[canon_idx]
last_c = GC.LAST[canon_idx]
eb_c = GC.ENTRY_BLOCKED_C4[canon_idx]; ff_c = GC.FORCED_FLAT_C4[canon_idx]
sd_c = GC.SD[canon_idx]

print(f"[PLACEBO01-HTF] canonical window: {n_canon} bars, "
      f"{GC.CANON_START.date()}..{GC.CANON_END.date()}, "
      f"{pd.Series(sd_c).nunique()} sessions", flush=True)

# =========================================================================================
# Restricted-window executors -- verbatim-formula copies of grid_core.product_a_exec /
# product_b_exec (+ _build_pos_seq/_onelot_exec), generalized to accept an arbitrary
# `tilt_bar` array and restricted to the slice passed in (see module docstring for the
# flat-at-session-close equivalence argument).
# =========================================================================================
def solve_A(tilt_bar, T_bar, B_bar, open_, high, low, close, last, entry_blocked, forced_flat,
            pv=PV_MNQ_A, comm=COMM_MNQ_A, ticks=1):
    n = len(T_bar)
    m_arr = np.where((T_bar != 0) & (tilt_bar != 0) & (np.sign(T_bar) == tilt_bar), TILTMULT, 1.0)
    s_arr = np.where((T_bar < 0) & (tilt_bar > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_bar * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_bar), -13, 13)
    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    total_contracts = 0
    for t in range(n):
        if pend != p:
            d = pend - p; side = 1 if d > 0 else -1
            px = _fill_n(open_[t], high[t], low[t], side, ticks=ticks)
            cash -= d * px * pv; cash -= abs(d) * comm
            total_contracts += abs(d)
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill_n(open_[t], high[t], low[t], side, ticks=ticks, at_close=close[t])
            cash += p * px * pv; cash -= abs(p) * comm
            total_contracts += abs(p)
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
            if forced_flat[t]:
                tgt = 0
            elif entry_blocked[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * close[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl, total_contracts


def solve_B(tilt_bar, T_bar, B_bar, open_, high, low, close, last, entry_blocked, forced_flat,
            pv=PV_NQ, comm=COMM_NQ, ticks=1):
    n = len(T_bar)
    m_arr = np.where((T_bar != 0) & (tilt_bar != 0) & (np.sign(T_bar) == tilt_bar), TILTMULT, 1.0)
    Tp = np.clip(rha(T_bar * m_arr * TILTRESCALE), -13, 13)
    M = WSOLAR * Tp + WBMOM * B_bar
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    for t in range(n):
        if pend != p:
            p = pend
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if forced_flat[t]:
            tgt = 0
        elif p == 0:
            tgt = 0 if entry_blocked[t] else (1 if M[t] >= ENTRY_LEVEL else (-1 if M[t] <= -ENTRY_LEVEL else 0))
        elif p > 0:
            if M[t] <= -ENTRY_LEVEL and not entry_blocked[t]:
                tgt = -1
            elif M[t] <= EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        else:
            if M[t] >= ENTRY_LEVEL and not entry_blocked[t]:
                tgt = 1
            elif M[t] >= -EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        pend = tgt

    cash = 0.0; p = 0; prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    n_legs = 0
    for t in range(n):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p; side = 1 if d > 0 else -1
            if last[t]:
                px = _fill_n(open_[t], high[t], low[t], side, ticks=ticks, at_close=close[t])
            else:
                px = _fill_n(open_[t], high[t], low[t], side, ticks=ticks)
            cash -= d * px * pv; cash -= abs(d) * comm
            n_legs += 1
            p = tgt
        eq = cash + p * close[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return pos_seq, bar_pos, bar_pnl, n_legs


def daily_from_barpnl(bar_pnl, sd_bar):
    s = pd.Series(np.asarray(bar_pnl), index=pd.Index(sd_bar))
    return s.groupby(level=0).sum().sort_index()


def metrics_from_barpnl(bar_pnl, sd_bar, label=""):
    d = daily_from_barpnl(bar_pnl, sd_bar)
    b = dd_battery(pd.to_datetime(d.index), d.to_numpy(), label=label)
    return b


# =========================================================================================
# GATE #2 -- restricted-window executor, fed the REAL unperturbed tiltState, must reproduce
# grid_core's own FULL-ARRAY (2022-01-02..2026-07-31) product_a_exec/product_b_exec net,
# sliced by CANON_MASK, to within $0.01. This is the "reconstruct the TRUE incumbent over the
# canonical window and confirm it reproduces the certified figures" gate from task instructions,
# run BEFORE any shuffled tiltState is touched.
# =========================================================================================
print("[PLACEBO01-HTF] GATE #2: cross-checking restricted-window executors (real tiltState) "
      "against grid_core's own full-array execution, sliced to the canonical window ...", flush=True)
_bp_A_gc, _pnl_A_gc, _ = GC.product_a_exec(GC._T0, ticks=1)
_gc_net_A_canon = float(_pnl_A_gc[GC.CANON_MASK].sum())
_, _pnl_A_mine, _tc_A_mine = solve_A(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c,
                                      last_c, eb_c, ff_c)
_mine_net_A_canon = float(_pnl_A_mine.sum())

_pos_B_gc, _bp_B_gc, _pnl_B_gc, _ = GC.product_b_exec(GC._T0, ticks=1)
_gc_net_B_canon = float(_pnl_B_gc[GC.CANON_MASK].sum())
_, _, _pnl_B_mine, _legs_B_mine = solve_B(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c,
                                           last_c, eb_c, ff_c)
_mine_net_B_canon = float(_pnl_B_mine.sum())

gate2_A_ok = abs(_gc_net_A_canon - _mine_net_A_canon) < 0.01
gate2_B_ok = abs(_gc_net_B_canon - _mine_net_B_canon) < 0.01
print(f"[PLACEBO01-HTF] GATE #2 Product A: grid_core-full-sliced={_gc_net_A_canon:.2f} "
      f"restricted-window={_mine_net_A_canon:.2f} match={gate2_A_ok}", flush=True)
print(f"[PLACEBO01-HTF] GATE #2 Product B: grid_core-full-sliced={_gc_net_B_canon:.2f} "
      f"restricted-window={_mine_net_B_canon:.2f} match={gate2_B_ok}", flush=True)
assert gate2_A_ok and gate2_B_ok, (
    "GATE #2 FAILED: restricted-window executor does not reproduce grid_core's own full-array "
    "canonical-window net for the REAL, unperturbed tiltState -- STOP, do not proceed to any "
    "placebo generation until this reconciles.")
print("[PLACEBO01-HTF] GATE #2 PASS -- restricted-window executors are provably faithful to "
      "the certified substrate over the canonical window. Proceeding.", flush=True)

CERTIFIED_GATE = {
    "gate_1_grid_core_import_self_check": "PASS (dev-window net Product A=$177,924.40, "
                                           "Product B=$301,915.92, asserted inside grid_core.py import)",
    "gate_2_restricted_window_vs_full_array_canonical_slice": {
        "product_A": {"grid_core_full_array_sliced_net": round(_gc_net_A_canon, 2),
                       "restricted_window_net": round(_mine_net_A_canon, 2), "match": gate2_A_ok},
        "product_B": {"grid_core_full_array_sliced_net": round(_gc_net_B_canon, 2),
                       "restricted_window_net": round(_mine_net_B_canon, 2), "match": gate2_B_ok},
    },
}

# =========================================================================================
# WRITE PREREGISTRATION -- BEFORE any shuffled/placebo tiltState is generated or run.
# =========================================================================================
preregistration = {
    "task": "PLACEBO01 -- HTF (tiltState) causal placebo test",
    "written_before_any_placebo_realization_is_generated": True,
    "n_randomizations": N_REPS,
    "n_randomizations_minimum_recommended": 200,
    "seed_family": f"{SEED_BASE} + i, for i in range(0, {N_REPS})  -- "
                   f"np.random.default_rng({SEED_BASE} + i), deterministic, no time/unseeded "
                   f"randomness anywhere in this script",
    "canonical_window": {"start": str(GC.CANON_START.date()), "end": str(GC.CANON_END.date()),
                          "convention": "CLAUDE.md frozen canonical window "
                                        "(2023-01-01T06:00:00Z..2025-02-02T22:59:59Z UTC)",
                          "n_bars": int(n_canon), "n_sessions": int(pd.Series(sd_c).nunique())},
    "null_construction_method": {
        "name": "within-year natural-block permutation of tiltState chronology",
        "unit_of_randomization": "whole trading SESSION (tiltState is a session-level quantity, "
                                  "constant across all bars of a session by construction -- never "
                                  "shuffled at the bar level)",
        "steps": [
            "1. Extract the REAL tiltState value for every session in the canonical window, "
            "chronologically ordered (539 sessions: 2023=258, 2024=259, 2025-stub=22).",
            "2. Within each CALENDAR YEAR separately, partition that year's own chronological "
            "tiltState sequence into its NATURAL BLOCKS -- maximal contiguous runs of an "
            "identical tiltState value. Block boundaries come from the real data, not from a "
            "fixed/arbitrary block length.",
            "3. Randomly permute the ORDER of that year's own blocks (seeded RNG) and re-lay "
            "them, in the new order, onto that SAME year's own session-date slots. Block sizes "
            "are never split, merged, or resampled -- only their order changes.",
            "4. Concatenate the (independently, per-year) shuffled sequences back into "
            "chronological session order across the full canonical window.",
            "5. Broadcast each session's shuffled tiltState value onto every bar of that "
            "session to get a bar-level shuffled tiltState array.",
            "6. Apply the SAME shuffled realization to BOTH Product A's mm/ss gating and "
            "Product B's mm gating within one replication (one shared HTF-input shuffle per "
            "replication, not two independent draws) -- Solar T and B-MOM stay real/unperturbed "
            "throughout.",
        ],
        "preserves_marginal_distribution": "EXACTLY, per year and therefore overall (same "
                                            "multiset of session tiltState values, only reordered)",
        "preserves_run_length_distribution": "at the BLOCK level exactly (no block resized); "
                                              "DISCLOSED CAVEAT: two blocks sharing the same "
                                              "value can land adjacent post-shuffle and read as "
                                              "one longer realized run -- quantified empirically "
                                              "in the output, not assumed away",
        "preserves_year_composition": "EXACTLY (blocks never cross a year boundary)",
        "breaks_temporal_alignment_with_real_market_state": "yes, by construction -- shuffled "
                                                              "sessions' HTF state does not match "
                                                              "what genuinely occurred on that date",
    },
    "components_perturbed": "tiltState ONLY (Product A: mm AND ss, since ss's own gating "
                             "condition is itself tiltState>0-dependent; Product B: mm only, "
                             "no ss term exists there)",
    "components_held_real_unperturbed": ["Solar T (13-member ensemble consensus)",
                                          "B-MOM position (bmomPos)",
                                          "EntryBlocked/ForcedFlat C4 day-only overlay clocks",
                                          "all decoder constants (KSolar, KBmom, TiltRescale, "
                                          "TiltMult, ShortHalf, WSolar, WBmom, EntryLevel, "
                                          "ExitLevel) -- unperturbed, per task scope (EQV01/"
                                          "PERT01's job, not this workflow's)"],
    "baseline_definition": "Solar+BMOM-only control: tiltState held at 0 (neutral) for every "
                            "bar of the canonical window, mechanically forcing Product A's mm=1.0 "
                            "AND ss=1.0 (ss's condition requires tiltState>0, never true when "
                            "tiltState==0) and Product B's mm=1.0. Computed ONCE -- identical "
                            "subtrahend for the real marginal contribution and every one of the "
                            "1000 placebo marginal contributions.",
    "marginal_contribution_definition": "marginal_X = X(full system, given some tiltState array) "
                                         "- X(Solar+BMOM-only baseline), for X in {net, sharpe}, "
                                         "computed separately for Product A and Product B",
    "reported_statistic": "empirical percentile of the REAL marginal contribution within the "
                           "null distribution of PLACEBO marginal contributions: "
                           "pct = 100 * mean(placebo_marginal <= real_marginal). NOT a bare "
                           "beats-placebo boolean.",
    "decision_rule_disclosed_in_advance": "Per campaign directive: if the real HTF-overlay's "
                                           "marginal contribution performs no better than the "
                                           "randomized-chronology null (percentile <= ~50%, i.e. "
                                           "real is unremarkable within the null distribution), "
                                           "HTF's economic interpretation weakens substantially. "
                                           "This will be reported plainly regardless of which way "
                                           "it comes out -- no result is preferred over another.",
    "seed_note": "Fixed integer seed family per governance instruction (no time-seeded or "
                 "unseeded randomness). Every np.random usage in this script is via "
                 "np.random.default_rng(SEED_BASE + i) inside the replication loop; nothing "
                 "upstream (grid_core, sm01_solarsim, sm_bmom) uses randomness at all -- the "
                 "entire non-placebo substrate is deterministic.",
    "correctness_gates_passed_before_this_file_was_written": CERTIFIED_GATE,
    "generated_utc": pd.Timestamp.utcnow().isoformat(),
}
prereg_path = os.path.join(OUT_DIR, "htf_placebo_preregistration.json")
with open(prereg_path, "w", encoding="utf-8") as f:
    json.dump(preregistration, f, indent=2, default=str)
print(f"[PLACEBO01-HTF] PREREGISTRATION WRITTEN: {prereg_path} "
      f"(N_REPS={N_REPS}, seed_family={SEED_BASE}+i) -- no placebo realization generated yet.",
      flush=True)

# =========================================================================================
# REAL (unshuffled) full reconstruction + BASELINE (tiltState=0) -- NOT a placebo realization,
# this is the actual incumbent system (already gate-confirmed above) and its own no-tilt
# control. Computed once, used as fixed reference points for every replication below.
# =========================================================================================
print("[PLACEBO01-HTF] computing REAL (unperturbed tiltState) and BASELINE (tiltState=0) "
      "reconstructions for both products ...", flush=True)

tilt_zero_c = np.zeros(n_canon)

bp_A_real, pnl_A_real, tc_A_real = solve_A(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c,
                                            last_c, eb_c, ff_c)
bp_A_base, pnl_A_base, tc_A_base = solve_A(tilt_zero_c, T_c, B_c, open_c, high_c, low_c, close_c,
                                            last_c, eb_c, ff_c)
_, bp_B_real, pnl_B_real, legs_B_real = solve_B(tilt_real_c, T_c, B_c, open_c, high_c, low_c,
                                                 close_c, last_c, eb_c, ff_c)
_, bp_B_base, pnl_B_base, legs_B_base = solve_B(tilt_zero_c, T_c, B_c, open_c, high_c, low_c,
                                                 close_c, last_c, eb_c, ff_c)

met_A_real = metrics_from_barpnl(pnl_A_real, sd_c, "A_real")
met_A_base = metrics_from_barpnl(pnl_A_base, sd_c, "A_baseline")
met_B_real = metrics_from_barpnl(pnl_B_real, sd_c, "B_real")
met_B_base = metrics_from_barpnl(pnl_B_base, sd_c, "B_baseline")

real_marginal_net_A = met_A_real["net"] - met_A_base["net"]
real_marginal_sharpe_A = met_A_real["sharpe"] - met_A_base["sharpe"]
real_marginal_net_B = met_B_real["net"] - met_B_base["net"]
real_marginal_sharpe_B = met_B_real["sharpe"] - met_B_base["sharpe"]

print(f"[PLACEBO01-HTF] Product A: net_real=${met_A_real['net']:,.2f} "
      f"net_baseline=${met_A_base['net']:,.2f} real_marginal_net=${real_marginal_net_A:,.2f} "
      f"sharpe_real={met_A_real['sharpe']:.4f} sharpe_baseline={met_A_base['sharpe']:.4f} "
      f"real_marginal_sharpe={real_marginal_sharpe_A:.4f}", flush=True)
print(f"[PLACEBO01-HTF] Product B: net_real=${met_B_real['net']:,.2f} "
      f"net_baseline=${met_B_base['net']:,.2f} real_marginal_net=${real_marginal_net_B:,.2f} "
      f"sharpe_real={met_B_real['sharpe']:.4f} sharpe_baseline={met_B_base['sharpe']:.4f} "
      f"real_marginal_sharpe={real_marginal_sharpe_B:.4f}", flush=True)

# =========================================================================================
# Block structure (real tiltState, per year) -- built once, used by every replication.
# =========================================================================================
df_sess = pd.DataFrame({"sess": sd_c, "tilt": tilt_real_c})
sess_tilt = df_sess.groupby("sess", sort=True)["tilt"].first()
sess_order = sess_tilt.index.to_numpy()          # chronological unique session dates
n_sess = len(sess_order)
sess_years = pd.to_datetime(sess_order).year.to_numpy()
sess_tilt_vals = sess_tilt.to_numpy()

sess_to_pos = {s: i for i, s in enumerate(sess_order)}
session_idx_per_bar = np.array([sess_to_pos[s] for s in sd_c])  # length n_canon, values 0..n_sess-1
assert len(session_idx_per_bar) == n_canon

years_present = sorted(set(sess_years.tolist()))


def blocks_from_values(vals):
    blocks = []
    cur_val = vals[0]; cur_len = 1
    for v in vals[1:]:
        if v == cur_val:
            cur_len += 1
        else:
            blocks.append((cur_val, cur_len))
            cur_val = v; cur_len = 1
    blocks.append((cur_val, cur_len))
    return blocks


year_block_info = {}
year_masks = {}
year_blocks = {}
for y in years_present:
    mask = (sess_years == y)
    year_masks[y] = mask
    vals = sess_tilt_vals[mask]
    blocks = blocks_from_values(vals)
    year_blocks[y] = blocks
    lens = [b[1] for b in blocks]
    year_block_info[int(y)] = {
        "n_sessions": int(mask.sum()), "n_blocks": len(blocks),
        "block_len_min": int(min(lens)), "block_len_median": float(np.median(lens)),
        "block_len_max": int(max(lens)),
        "value_counts": {str(k): int(v) for k, v in pd.Series(vals).value_counts().items()},
    }
print(f"[PLACEBO01-HTF] block structure by year: {json.dumps(year_block_info, indent=2)}", flush=True)


def shuffled_session_values(rng):
    """One within-year block-permuted session-level tiltState array, length n_sess, aligned
    to sess_order."""
    out = np.empty(n_sess)
    for y in years_present:
        mask = year_masks[y]
        blocks = year_blocks[y]
        order = rng.permutation(len(blocks))
        shuffled = np.concatenate([np.full(blocks[i][1], blocks[i][0]) for i in order])
        out[mask] = shuffled
    return out


# =========================================================================================
# RUN-LENGTH DISCLOSURE -- quantify the "adjacent-same-value block merge" caveat empirically,
# using the FIRST replication's draw as a representative example (descriptive only, not used
# to pick or discard any replication).
# =========================================================================================
def realized_run_lengths(vals):
    return [b[1] for b in blocks_from_values(vals)]


_example_rng = np.random.default_rng(SEED_BASE)
_example_shuffled = shuffled_session_values(_example_rng)
_real_run_lens = realized_run_lengths(sess_tilt_vals)
_shuffled_run_lens = realized_run_lengths(_example_shuffled)
_n_real_blocks_total = sum(len(year_blocks[y]) for y in years_present)
run_length_disclosure = {
    "note": "Descriptive only (first replication, seed=SEED_BASE, shown as a representative "
            "example) -- quantifies how often adjacent post-shuffle blocks of the same value "
            "merge into a longer REALIZED run than any single original block.",
    "n_original_blocks_total_all_years": _n_real_blocks_total,
    "n_realized_runs_in_real_series": len(_real_run_lens),
    "n_realized_runs_in_example_shuffled_series": len(_shuffled_run_lens),
    "real_run_len_mean": float(np.mean(_real_run_lens)), "real_run_len_max": int(max(_real_run_lens)),
    "shuffled_run_len_mean": float(np.mean(_shuffled_run_lens)),
    "shuffled_run_len_max": int(max(_shuffled_run_lens)),
    "interpretation": ("If n_realized_runs_in_example_shuffled_series < n_original_blocks_total, "
                        "some adjacent blocks merged post-shuffle (expected occasionally, given "
                        "tiltState's real skew toward +1 in 2023/2024 -- 197/258 and 209/259 "
                        "up-sessions respectively -- makes same-value adjacency non-trivially "
                        "likely by chance); this does not violate the preregistered method, it "
                        "is the disclosed limitation named in the preregistration."),
}
print(f"[PLACEBO01-HTF] run-length disclosure: {json.dumps(run_length_disclosure, indent=2)}",
      flush=True)

# =========================================================================================
# RANDOMIZATION LOOP -- N_REPS replications, seed family SEED_BASE + i.
# =========================================================================================
print(f"[PLACEBO01-HTF] running {N_REPS} placebo replications (seed family {SEED_BASE}+i) ...",
      flush=True)
loop_t0 = time.time()
rows = []
for i in range(N_REPS):
    rng = np.random.default_rng(SEED_BASE + i)
    sess_vals_shuf = shuffled_session_values(rng)
    tilt_bar_shuf = sess_vals_shuf[session_idx_per_bar]

    bp_A, pnl_A, tc_A = solve_A(tilt_bar_shuf, T_c, B_c, open_c, high_c, low_c, close_c,
                                 last_c, eb_c, ff_c)
    _, bp_B, pnl_B, legs_B = solve_B(tilt_bar_shuf, T_c, B_c, open_c, high_c, low_c, close_c,
                                      last_c, eb_c, ff_c)

    m_A = metrics_from_barpnl(pnl_A, sd_c, f"A_rep{i}")
    m_B = metrics_from_barpnl(pnl_B, sd_c, f"B_rep{i}")

    rows.append({
        "rep": i, "seed": SEED_BASE + i,
        "net_A": m_A["net"], "sharpe_A": m_A["sharpe"], "maxDD_A": m_A["maxDD_eod"],
        "CDaR_A": m_A["CDaR5"], "turnover_contracts_A": tc_A,
        "marginal_net_A": m_A["net"] - met_A_base["net"],
        "marginal_sharpe_A": m_A["sharpe"] - met_A_base["sharpe"],
        "net_B": m_B["net"], "sharpe_B": m_B["sharpe"], "maxDD_B": m_B["maxDD_eod"],
        "CDaR_B": m_B["CDaR5"], "turnover_legs_B": legs_B,
        "marginal_net_B": m_B["net"] - met_B_base["net"],
        "marginal_sharpe_B": m_B["sharpe"] - met_B_base["sharpe"],
    })
    if (i + 1) % 200 == 0:
        print(f"[PLACEBO01-HTF]   ... {i + 1}/{N_REPS} replications done "
              f"({time.time() - loop_t0:.1f}s elapsed)", flush=True)

loop_elapsed = time.time() - loop_t0
print(f"[PLACEBO01-HTF] randomization loop complete: {N_REPS} reps in {loop_elapsed:.1f}s "
      f"({loop_elapsed / N_REPS * 1000:.1f}ms/rep)", flush=True)

results_df = pd.DataFrame(rows)
csv_path = os.path.join(OUT_DIR, "htf_placebo_results.csv")
results_df.to_csv(csv_path, index=False)
print(f"[PLACEBO01-HTF] wrote {csv_path}", flush=True)

# =========================================================================================
# EMPIRICAL PERCENTILES -- real marginal contribution within the placebo null distribution.
# =========================================================================================
def empirical_percentile(real_val, placebo_vals):
    placebo_vals = np.asarray(placebo_vals, dtype=float)
    return float(100.0 * np.mean(placebo_vals <= real_val))


pct_net_A = empirical_percentile(real_marginal_net_A, results_df["marginal_net_A"])
pct_sharpe_A = empirical_percentile(real_marginal_sharpe_A, results_df["marginal_sharpe_A"])
pct_net_B = empirical_percentile(real_marginal_net_B, results_df["marginal_net_B"])
pct_sharpe_B = empirical_percentile(real_marginal_sharpe_B, results_df["marginal_sharpe_B"])

print(f"[PLACEBO01-HTF] Product A: real marginal net percentile within null = {pct_net_A:.1f}%  "
      f"real marginal Sharpe percentile within null = {pct_sharpe_A:.1f}%", flush=True)
print(f"[PLACEBO01-HTF] Product B: real marginal net percentile within null = {pct_net_B:.1f}%  "
      f"real marginal Sharpe percentile within null = {pct_sharpe_B:.1f}%", flush=True)

verdict_A = ("HTF's marginal contribution to Product A performs BETTER than the randomized-"
             "chronology null" if pct_net_A > 50 else
             "HTF's marginal contribution to Product A performs NO BETTER than the randomized-"
             "chronology null -- its economic interpretation weakens substantially, per campaign "
             "directive")
verdict_B = ("HTF's marginal contribution to Product B performs BETTER than the randomized-"
             "chronology null" if pct_net_B > 50 else
             "HTF's marginal contribution to Product B performs NO BETTER than the randomized-"
             "chronology null -- its economic interpretation weakens substantially, per campaign "
             "directive")

real_beats_placebo_distribution = bool(pct_net_A > 50 and pct_net_B > 50)

# =========================================================================================
# WRITE FINAL RESULTS JSON.
# =========================================================================================
summary = {
    "task": "PLACEBO01 -- HTF (tiltState) causal placebo test",
    "generated_utc": pd.Timestamp.utcnow().isoformat(),
    "preregistration_file": prereg_path,
    "correctness_gates": CERTIFIED_GATE,
    "n_randomizations": N_REPS,
    "seed_family": f"{SEED_BASE}+i for i in range(0,{N_REPS})",
    "runtime_seconds_randomization_loop": round(loop_elapsed, 1),
    "canonical_window": preregistration["canonical_window"],
    "block_structure_by_year": year_block_info,
    "run_length_disclosure": run_length_disclosure,
    "product_A": {
        "name": "Product A (SolarWaveSMMaster, MNQ execution)",
        "real_full_system": {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer))
                                  else v) for k, v in met_A_real.items()},
        "baseline_solar_bmom_only_tiltState_zero": {
            k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v)
            for k, v in met_A_base.items()},
        "real_marginal_net": float(real_marginal_net_A),
        "real_marginal_sharpe": float(real_marginal_sharpe_A),
        "placebo_marginal_net_distribution": {
            "mean": float(results_df["marginal_net_A"].mean()),
            "std": float(results_df["marginal_net_A"].std(ddof=1)),
            "min": float(results_df["marginal_net_A"].min()),
            "q05": float(results_df["marginal_net_A"].quantile(0.05)),
            "q50": float(results_df["marginal_net_A"].quantile(0.50)),
            "q95": float(results_df["marginal_net_A"].quantile(0.95)),
            "max": float(results_df["marginal_net_A"].max()),
        },
        "placebo_marginal_sharpe_distribution": {
            "mean": float(results_df["marginal_sharpe_A"].mean()),
            "std": float(results_df["marginal_sharpe_A"].std(ddof=1)),
            "q05": float(results_df["marginal_sharpe_A"].quantile(0.05)),
            "q50": float(results_df["marginal_sharpe_A"].quantile(0.50)),
            "q95": float(results_df["marginal_sharpe_A"].quantile(0.95)),
        },
        "real_marginal_net_percentile_within_null": pct_net_A,
        "real_marginal_sharpe_percentile_within_null": pct_sharpe_A,
        "verdict": verdict_A,
    },
    "product_B": {
        "name": "Product B / BEST_ONE_NQ (SolarWaveOneContractNQ, NQ direct execution)",
        "real_full_system": {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer))
                                  else v) for k, v in met_B_real.items()},
        "baseline_solar_bmom_only_tiltState_zero": {
            k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v)
            for k, v in met_B_base.items()},
        "real_marginal_net": float(real_marginal_net_B),
        "real_marginal_sharpe": float(real_marginal_sharpe_B),
        "placebo_marginal_net_distribution": {
            "mean": float(results_df["marginal_net_B"].mean()),
            "std": float(results_df["marginal_net_B"].std(ddof=1)),
            "min": float(results_df["marginal_net_B"].min()),
            "q05": float(results_df["marginal_net_B"].quantile(0.05)),
            "q50": float(results_df["marginal_net_B"].quantile(0.50)),
            "q95": float(results_df["marginal_net_B"].quantile(0.95)),
            "max": float(results_df["marginal_net_B"].max()),
        },
        "placebo_marginal_sharpe_distribution": {
            "mean": float(results_df["marginal_sharpe_B"].mean()),
            "std": float(results_df["marginal_sharpe_B"].std(ddof=1)),
            "q05": float(results_df["marginal_sharpe_B"].quantile(0.05)),
            "q50": float(results_df["marginal_sharpe_B"].quantile(0.50)),
            "q95": float(results_df["marginal_sharpe_B"].quantile(0.95)),
        },
        "real_marginal_net_percentile_within_null": pct_net_B,
        "real_marginal_sharpe_percentile_within_null": pct_sharpe_B,
        "verdict": verdict_B,
    },
    "real_beats_placebo_distribution_both_products_net_pct_gt_50": real_beats_placebo_distribution,
    "headline": (
        f"Product A: real HTF marginal net contribution (${real_marginal_net_A:,.0f}) sits at "
        f"the {pct_net_A:.1f}th percentile of {N_REPS} randomized-chronology placebo "
        f"realizations (Sharpe percentile {pct_sharpe_A:.1f}th). "
        f"Product B: real HTF marginal net contribution (${real_marginal_net_B:,.0f}) sits at "
        f"the {pct_net_B:.1f}th percentile ({N_REPS} reps; Sharpe percentile {pct_sharpe_B:.1f}th). "
        + verdict_A + ". " + verdict_B + "."
    ),
}
json_path = os.path.join(OUT_DIR, "htf_placebo_results.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"[PLACEBO01-HTF] wrote {json_path}", flush=True)
print(f"[PLACEBO01-HTF] TOTAL RUNTIME {time.time() - T0:.1f}s", flush=True)
print("\n" + "=" * 78)
print("PLACEBO01 HTF -- HEADLINE")
print("=" * 78)
print(summary["headline"])
