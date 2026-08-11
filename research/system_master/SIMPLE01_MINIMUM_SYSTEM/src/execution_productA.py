#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMPLE01 -- execution_productA.py: EXECUTION AGENT run of the FROZEN Product A ladder
(A0, A1, A2, A_FULL) against the frozen manifest (00_SPEC_candidate_manifest.md) and frozen
margins/methodology (01_SPEC_frozen_margins.md), campaign directive sec73.

ROLE DISCIPLINE: this script does not adjudicate anything. It runs exactly the four frozen
Product A rungs, computes the metrics the execution task asked for, over the two windows the
execution task named (canonical 2023-01-01..2025-02-02, and the fuller available history
through the LOCKED_FORWARD boundary, i.e. up to and including 2026-07-31 -- grid_core's own
HEALTH_END), plus the dev window (2022-01-01..2026-05-31) that 01_SPEC_frozen_margins.md
freezes as the PRIMARY gating window for whatever adjudication phase consumes this output.
Mirrors execution_productB.py's structure exactly (same three windows, same cost-stress
levels, same metric battery, same output shape) per the task instruction "same metric battery
as specified for Product B." No pass/fail judgement, no rung selection, is made here.

REUSE, NOT REINVENTION: imports grid_core.py verbatim (the campaign's own already-certified,
self-checking substrate -- Solar13 ensemble T, real tiltState, real bmomPos/B_LEG, the C4
entry-block/forced-flat clocks). grid_core's own import-time self-check (Product A dev-window
net == $177,924.40, Product B dev-window net == $301,915.92) is CORRECTNESS GATE #1 and runs
automatically before a single line below executes. This script's own GATE #2 (below)
additionally confirms the A_FULL rung, built from this script's rung-forcing wrapper
(mm real, ss real), is bar-for-bar IDENTICAL to grid_core.product_a_exec's own output at
ticks=1 -- i.e. that the wrapper mechanism itself introduces no drift from the certified
incumbent before any A0/A1/A2 ablation result is trusted. The wrapper is a verbatim-formula
copy of grid_core.product_a_exec, generalized only to force `mm`/`ss` per rung
(00_SPEC_candidate_manifest.md sec2.3) -- no formula re-derived, only two ternaries replaced
by their forced-constant equivalents per rung, exactly as the manifest specifies.

Metric battery reuses smv2_common.dd_battery (net/Sharpe/Sortino/Calmar/maxDD_eod/CDaR5/...,
this program's own frozen definitions) and primary_objective.cdar_dollar/top10_day_retention
(house alpha=0.95 CDaR and top-10-day-retention conventions, CONVENTIONS.md/primary_objective.py).

Cost stress: reuses grid_core's own `ticks` adverse-slip generalization (the same mechanism
grid_core.product_a_exec/_fill_n already implement). ticks=1 IS the canonical base-cost
convention already embedded in every other certified figure in this repo. "+1 tick/side"
stress = ticks=2, "+2 ticks/side" stress = ticks=3 -- literal increments of the same
mechanism, not a new cost model (matches PERT01_STRUCTURAL_INVARIANCE's own et=0/1/2 ==
ticks=1/2/3 convention).

Output: research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/execution_productA_raw.json
         research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/daily_pnl_<rung>_full_history.csv
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
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))

OUT_DIR = os.path.join(ROOT, "research", "system_master", "SIMPLE01_MINIMUM_SYSTEM", "out")
os.makedirs(OUT_DIR, exist_ok=True)

T0 = time.time()

# ================================================================================================
# GATE #1 -- import grid_core. Its own module-level self-check (dev-window net == $177,924.40 /
# $301,915.92 for Product A / Product B on the incumbent G13 grid) runs INSIDE this import and
# raises AssertionError if it fails. Nothing below executes on a failed gate.
# ================================================================================================
print("[SIMPLE01-EXEC-A] importing grid_core (certified substrate; self-check runs at import) ...",
      flush=True)
import grid_core as GC  # noqa: E402
from primary_objective import cdar_dollar as po_cdar_dollar, top10_day_retention as po_top10_ret  # noqa: E402
from smv2_common import dd_battery  # noqa: E402

print(f"[SIMPLE01-EXEC-A] grid_core imported + self-checked in {time.time() - T0:.1f}s "
      f"(GATE #1 PASS: Product A dev-window net $177,924.40, Product B dev-window net "
      f"$301,915.92, both reproduced exactly on import -- see grid_core's own printed "
      f"self-check line above)", flush=True)

N = GC.N
T_full = GC._T0.astype(int)
TILT_full = GC.TILT_STATE
B_full = np.asarray(GC.B_LEG)
SD_full = GC.SD
SESS_DT_full = GC.SESS_DT

print(f"[SIMPLE01-EXEC-A] full substrate: N={N} bars, "
      f"{pd.Series(SD_full).nunique()} sessions, {SESS_DT_full.min().date()}..{SESS_DT_full.max().date()}",
      flush=True)

# ================================================================================================
# FROZEN PRODUCT A LADDER -- exact constructions per 00_SPEC_candidate_manifest.md sec2.3.
# `bmomPos` (B_full) is REAL in every rung (never ablated by this ladder -- it is not gated by
# either mm or ss in the incumbent's own decoder, per manifest sec2.1). Only mm/ss are forced.
# ================================================================================================
RUNGS = {
    "A0": {"mm": "forced", "ss": "forced",
           "desc": "Solar+B-MOM, no HTF, no short-halving: mm forced 1.0, ss forced 1.0"},
    "A1": {"mm": "forced", "ss": "real",
           "desc": "+ short-halving only: mm forced 1.0, ss real"},
    "A2": {"mm": "real", "ss": "forced",
           "desc": "+ HTF up-weight only: mm real, ss forced 1.0"},
    "A_FULL": {"mm": "real", "ss": "real",
               "desc": "incumbent, unmodified: mm real, ss real"},
}


def build_rung_Ma(mm_mode, ss_mode):
    if mm_mode == "forced":
        m_arr = np.ones(N)
    elif mm_mode == "real":
        m_arr = np.where((T_full != 0) & (TILT_full != 0) & (np.sign(T_full) == TILT_full),
                          GC.TILTMULT, 1.0)
    else:
        raise ValueError(mm_mode)

    if ss_mode == "forced":
        s_arr = np.ones(N)
    elif ss_mode == "real":
        s_arr = np.where((T_full < 0) & (TILT_full > 0), GC.SHORTHALF, 1.0)
    else:
        raise ValueError(ss_mode)

    Tpp = np.clip(GC.rha(T_full * m_arr * s_arr * GC.TILTRESCALE), -13, 13)
    M_a = np.clip(GC.rha(GC.KSOLAR * Tpp + GC.KBMOM * B_full), -13, 13)
    return M_a


def exec_rung_A(rung_name, ticks=1):
    """Verbatim-formula copy of grid_core.product_a_exec's own bar loop, generalized only in
    how M_a (== grid_core's M_a) is built (via build_rung_Ma's forced/real mm,ss per rung).
    Nothing else about the loop -- fill convention, C4 entry-block/forced-flat handling,
    cash/equity accounting -- differs from grid_core.product_a_exec."""
    spec = RUNGS[rung_name]
    M_a = build_rung_Ma(spec["mm"], spec["ss"])
    cash = 0.0
    p = 0
    pend = 0
    prev_eq = 0.0
    bar_pos = np.zeros(N, dtype=int)
    bar_pnl = np.zeros(N)
    for t in range(N):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = GC._fill_n(GC.OPEN_[t], GC.HIGH[t], GC.LOW[t], side, ticks=ticks)
            cash -= d * px * GC.PV_MNQ_A
            cash -= abs(d) * GC.COMM_MNQ_A
            p = pend
        if GC.LAST[t] and p != 0:
            side = -1 if p > 0 else 1
            px = GC._fill_n(GC.OPEN_[t], GC.HIGH[t], GC.LOW[t], side, ticks=ticks, at_close=GC.CLOSE[t])
            cash += p * px * GC.PV_MNQ_A
            cash -= abs(p) * GC.COMM_MNQ_A
            p = 0
            pend = 0
        else:
            tgt_raw = int(M_a[t])
            if GC.FORCED_FLAT_C4[t]:
                tgt = 0
            elif GC.ENTRY_BLOCKED_C4[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * GC.CLOSE[t] * GC.PV_MNQ_A
        bar_pnl[t] = eq - prev_eq
        prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl


print("[SIMPLE01-EXEC-A] rungs to execute:", flush=True)
for r in RUNGS:
    print(f"[SIMPLE01-EXEC-A]   {r}: {RUNGS[r]['desc']}", flush=True)

# ================================================================================================
# GATE #2 -- A_FULL rung (this script's own wrapper, mm real / ss real) must be bar-for-bar
# IDENTICAL to grid_core.product_a_exec's own output at ticks=1 -- confirms the rung-forcing
# wrapper mechanism itself introduces zero drift from the certified incumbent before any
# A0/A1/A2 ablation result is trusted.
# ================================================================================================
print("[SIMPLE01-EXEC-A] GATE #2: A_FULL wrapper vs grid_core.product_a_exec (ticks=1) ...",
      flush=True)
_bar_pos_gc, _bar_pnl_gc, _M_gc = GC.product_a_exec(T_full, ticks=1)
_bar_pos_afull, _bar_pnl_afull = exec_rung_A("A_FULL", ticks=1)
gate2_exact = bool(np.array_equal(_bar_pnl_afull, _bar_pnl_gc)) and \
              bool(np.array_equal(_bar_pos_afull, _bar_pos_gc))
gate2_maxdiff = float(np.max(np.abs(_bar_pnl_afull - _bar_pnl_gc)))
_dev_net_afull = float(_bar_pnl_afull[GC.DEV_MASK].sum())
gate2_devnet_ok = abs(_dev_net_afull - 177924.40) < 1.0
print(f"[SIMPLE01-EXEC-A] GATE #2: bar-for-bar exact={gate2_exact} (max abs diff {gate2_maxdiff:.2e}); "
      f"A_FULL wrapper dev-window net=${_dev_net_afull:,.2f} vs certified $177,924.40 "
      f"(match={gate2_devnet_ok})", flush=True)
assert gate2_exact, "GATE #2 FAILED: A_FULL wrapper does not reproduce grid_core.product_a_exec bar-for-bar."
assert gate2_devnet_ok, "GATE #2 FAILED: A_FULL wrapper dev-window net does not match certified $177,924.40."
print("[SIMPLE01-EXEC-A] GATE #2 PASS.", flush=True)

CORRECTNESS_GATE = {
    "gate_1_grid_core_import_self_check": "PASS (dev-window net Product A=$177,924.40, "
                                           "Product B=$301,915.92, asserted inside grid_core.py "
                                           "import; this script never proceeds past that import "
                                           "if it fails)",
    "gate_2_A_FULL_wrapper_vs_grid_core_product_a_exec": {
        "bar_for_bar_exact_match": gate2_exact,
        "max_abs_bar_pnl_diff": gate2_maxdiff,
        "A_FULL_wrapper_dev_window_net": round(_dev_net_afull, 2),
        "certified_dev_window_net": 177924.40,
        "match": gate2_devnet_ok,
    },
    "overall_pass": bool(gate2_exact and gate2_devnet_ok),
}

# ================================================================================================
# COST-STRESS LEVELS -- reuse of grid_core's own `ticks` adverse-slip generalization.
# ticks=1 is the already-certified BASE cost convention (every certified $ figure in this repo
# is at ticks=1). "+1 tick/side" stress = ticks=2, "+2 ticks/side" stress = ticks=3.
# ================================================================================================
COST_LEVELS = {"base_ticks1": 1, "stress_plus1_tick_per_side_ticks2": 2,
               "stress_plus2_ticks_per_side_ticks3": 3}

print("[SIMPLE01-EXEC-A] executing all rungs x cost-stress levels ...", flush=True)
BAR_POS = {}
BAR_PNL = {}
for r in RUNGS:
    BAR_POS[r] = {}
    BAR_PNL[r] = {}
    for cl_name, ticks in COST_LEVELS.items():
        t0 = time.time()
        if cl_name == "base_ticks1" and r == "A_FULL":
            bar_pos, bar_pnl = _bar_pos_afull, _bar_pnl_afull  # already computed in GATE #2
        else:
            bar_pos, bar_pnl = exec_rung_A(r, ticks=ticks)
        BAR_POS[r][cl_name] = bar_pos
        BAR_PNL[r][cl_name] = bar_pnl
        print(f"[SIMPLE01-EXEC-A]   {r} / {cl_name} (ticks={ticks}) done in "
              f"{time.time() - t0:.1f}s, full-history net=${bar_pnl.sum():,.2f}", flush=True)

# ================================================================================================
# WINDOWS
# ================================================================================================
WINDOWS = {
    "canonical_2023_2025": GC.CANON_MASK,     # CLAUDE.md legacy canonical, secondary/non-gating
    "dev_2022_2026_05_31": GC.DEV_MASK,       # CONVENTIONS.md CURRENT (dev), primary gating window
    "full_through_locked_forward_2026_07_31": GC.FULL_MASK,  # fuller available history, task's 2nd window
}
WINDOW_DATES = {
    "canonical_2023_2025": (str(GC.CANON_START.date()), str(GC.CANON_END.date())),
    "dev_2022_2026_05_31": (str(SESS_DT_full.min().date()), str(GC.DEV_END.date())),
    "full_through_locked_forward_2026_07_31": (str(SESS_DT_full.min().date()), str(GC.HEALTH_END.date())),
}


def daily_series(bar_pnl, mask):
    s = pd.Series(np.asarray(bar_pnl)[mask], index=pd.Index(SD_full[mask], name="sess"))
    return s.groupby(level=0).sum().sort_index()


def turnover_stats(bar_pos, mask):
    bp = np.asarray(bar_pos)[mask]
    prev = np.concatenate(([0], bp[:-1]))
    diffs = bp - prev
    return {
        "total_contracts_traded": float(np.sum(np.abs(diffs))),
        "n_position_changes_legs": int(np.sum(diffs != 0)),
    }


def _clean(v):
    if v is None:
        return None
    if isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
        return None
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    return v


def metrics_for(rung, cost_level, window_name):
    mask = WINDOWS[window_name]
    bar_pnl = BAR_PNL[rung][cost_level]
    bar_pos = BAR_POS[rung][cost_level]
    d = daily_series(bar_pnl, mask)
    battery = dd_battery(pd.to_datetime(d.index), d.to_numpy(),
                          bar_eq=np.cumsum(np.asarray(bar_pnl)[mask]),
                          label=f"{rung}/{cost_level}/{window_name}")
    cdar_house = po_cdar_dollar(d.to_numpy(), alpha=0.95)
    to = turnover_stats(bar_pos, mask)
    out = {
        "n_sessions": int(len(d)),
        "net": float(battery["net"]),
        "sharpe": _clean(battery["sharpe"]),
        "sortino": _clean(battery["sortino"]),
        "calmar": _clean(battery["calmar"]),
        "CDaR5_smv2common": _clean(battery["CDaR5"]),
        "CDaR_0.95_dollar_primary_objective_house": _clean(cdar_house),
        "maxDD_eod": _clean(battery["maxDD_eod"]),
        "maxDD_bar_intraday_MTM_proxy": _clean(battery.get("maxDD_bar")),
        "ann_vol": _clean(battery["ann_vol"]),
        "pos_day_pct": _clean(battery["pos_day_pct"]),
        "turnover": to,
    }
    return out, d


# ================================================================================================
# MAIN METRIC SWEEP: rung x cost_level x window
# ================================================================================================
print("[SIMPLE01-EXEC-A] computing metric battery for every rung x cost-level x window ...",
      flush=True)
RESULTS = {}
DAILY_BASE = {}  # rung -> window -> daily Series (base cost only), for retention/concentration calcs
for r in RUNGS:
    RESULTS[r] = {}
    DAILY_BASE[r] = {}
    for cl_name in COST_LEVELS:
        RESULTS[r][cl_name] = {}
        for w_name in WINDOWS:
            m, d = metrics_for(r, cl_name, w_name)
            RESULTS[r][cl_name][w_name] = m
            if cl_name == "base_ticks1":
                DAILY_BASE[r][w_name] = d
print(f"[SIMPLE01-EXEC-A] metric sweep done in {time.time() - T0:.1f}s total elapsed.", flush=True)

# ================================================================================================
# TOP-10-DAY RETENTION vs A_FULL (base cost, per window) -- reuses
# primary_objective.top10_day_retention verbatim, baseline = A_FULL's own daily series.
# ================================================================================================
print("[SIMPLE01-EXEC-A] top-10-day retention vs A_FULL (base cost, per window) ...", flush=True)
TOP10_RETENTION = {}
for w_name in WINDOWS:
    base_series = DAILY_BASE["A_FULL"][w_name]
    TOP10_RETENTION[w_name] = {}
    for r in RUNGS:
        s = DAILY_BASE[r][w_name]
        assert len(s) == len(base_series) and (s.index == base_series.index).all(), \
            f"daily index misalignment for {r}/{w_name} vs A_FULL"
        TOP10_RETENTION[w_name][r] = _clean(po_top10_ret(s.to_numpy(), base_series.to_numpy()))

# ================================================================================================
# LARGEST-SINGLE-DAY SHARE OF INCREMENTAL ADVANTAGE OVER A_FULL (base cost, per window, A0/A1/A2)
# advantage_day = daily_rung - daily_A_FULL; total_advantage = sum(advantage_day) (== net_rung -
# net_A_FULL for that window). Share = max(advantage_day) / total_advantage, defined only when
# total_advantage > 0 (rung outperforms A_FULL) -- the concentration gate is asymmetric by design
# (01_SPEC_frozen_margins.md sec3.8: fires only on claimed improvements).
# ================================================================================================
print("[SIMPLE01-EXEC-A] largest-single-day share of incremental advantage vs A_FULL "
      "(base cost, per window) ...", flush=True)
CONCENTRATION = {}
for w_name in WINDOWS:
    base_series = DAILY_BASE["A_FULL"][w_name]
    CONCENTRATION[w_name] = {}
    for r in ("A0", "A1", "A2"):
        s = DAILY_BASE[r][w_name]
        diff = (s - base_series).to_numpy()
        total_adv = float(diff.sum())
        max_day = float(diff.max())
        _max_day_idx = s.index[int(np.argmax(diff))]
        max_day_date = str(_max_day_idx.date() if hasattr(_max_day_idx, "date") else _max_day_idx)
        share = (max_day / total_adv) if total_adv > 0 else None
        CONCENTRATION[w_name][r] = {
            "total_incremental_advantage_over_A_FULL": total_adv,
            "applicable_rung_outperforms_A_FULL": bool(total_adv > 0),
            "largest_single_day_diff": max_day,
            "largest_single_day_date": max_day_date,
            "largest_single_day_share_of_advantage": _clean(share),
        }

# ================================================================================================
# ANNUAL NET BY YEAR (full-history daily series, base cost) -- 2022/2023/2024/2025/2026-partial.
# Reported BOTH over the full available history (2026-partial = Jan..Jul 2026, through
# grid_core.HEALTH_END) AND restricted to the dev window (2026-partial = Jan..May 2026, through
# grid_core.DEV_END, i.e. 01_SPEC_frozen_margins.md's own annual-partition definition for margin
# #7) -- both computed here, disambiguated by key, so the next phase can use whichever it needs.
# ================================================================================================
print("[SIMPLE01-EXEC-A] annual net by calendar year (base cost) ...", flush=True)
ANNUAL_NET = {}
for r in RUNGS:
    d_full = DAILY_BASE[r]["full_through_locked_forward_2026_07_31"]
    d_dev = DAILY_BASE[r]["dev_2022_2026_05_31"]
    years_full = pd.to_datetime(d_full.index).year
    years_dev = pd.to_datetime(d_dev.index).year
    annual_full = {int(y): float(d_full[years_full == y].sum()) for y in sorted(set(years_full))}
    annual_dev = {int(y): float(d_dev[years_dev == y].sum()) for y in sorted(set(years_dev))}
    ANNUAL_NET[r] = {
        "by_year_full_history_2026_partial_is_Jan_Jul": annual_full,
        "by_year_dev_window_2026_partial_is_Jan_May": annual_dev,
    }

# ================================================================================================
# WRITE DAILY PNL SERIES TO DISK (base cost, FULL available history through LOCKED_FORWARD
# boundary) -- one CSV per rung, referenced by path in the output JSON and in the structured
# summary, so the next (adjudication) phase can consume the raw daily series directly.
# ================================================================================================
DAILY_PNL_FILES = {}
for r in RUNGS:
    d = DAILY_BASE[r]["full_through_locked_forward_2026_07_31"]
    fname = f"daily_pnl_{r}_base_cost_full_history_through_20260731.csv"
    fpath = os.path.join(OUT_DIR, fname)
    d.rename("pnl").rename_axis("session_date").to_frame().to_csv(fpath)
    DAILY_PNL_FILES[r] = fpath
    print(f"[SIMPLE01-EXEC-A] wrote {fpath} ({len(d)} sessions)", flush=True)

# ================================================================================================
# FINAL SUMMARY JSON
# ================================================================================================
summary = {
    "task": "SIMPLE01 execution -- Product A frozen ladder (A0, A1, A2, A_FULL)",
    "role": "EXECUTION AGENT (campaign directive sec73) -- runs the frozen spec exactly, "
            "adjudicates nothing, selects no rung",
    "generated_utc": pd.Timestamp.utcnow().isoformat(),
    "spec_sources": [
        "research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/00_SPEC_candidate_manifest.md",
        "research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/01_SPEC_frozen_margins.md",
        "research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/02_SPEC_complexity_metric.md",
    ],
    "rungs": {r: RUNGS[r]["desc"] for r in RUNGS},
    "cost_levels": {k: {"ticks_adverse_slip_per_fill": v,
                         "note": "ticks=1 is the already-certified base convention used by every "
                                 "certified $ figure in this repo; ticks=2/3 are +1/+2 tick/side "
                                 "stress via grid_core's own generalization"}
                     for k, v in COST_LEVELS.items()},
    "windows": {w: {"start": WINDOW_DATES[w][0], "end": WINDOW_DATES[w][1],
                     "n_sessions_A_FULL_base_cost": int(RESULTS["A_FULL"]["base_ticks1"][w]["n_sessions"])}
                for w in WINDOWS},
    "correctness_gates": CORRECTNESS_GATE,
    "metrics_by_rung_costlevel_window": RESULTS,
    "top10_day_pnl_retention_vs_A_FULL_base_cost": TOP10_RETENTION,
    "largest_single_day_share_of_incremental_advantage_vs_A_FULL_base_cost": CONCENTRATION,
    "annual_net_by_year_base_cost": ANNUAL_NET,
    "daily_pnl_files_full_history_base_cost": DAILY_PNL_FILES,
    "runtime_seconds_total": round(time.time() - T0, 1),
}

json_path = os.path.join(OUT_DIR, "execution_productA_raw.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"[SIMPLE01-EXEC-A] wrote {json_path}", flush=True)
print(f"[SIMPLE01-EXEC-A] TOTAL RUNTIME {time.time() - T0:.1f}s", flush=True)
print("\n" + "=" * 78)
print("SIMPLE01 EXECUTION (Product A) -- HEADLINE (no adjudication, figures only)")
print("=" * 78)
for w in WINDOWS:
    print(f"-- window {w} ({WINDOW_DATES[w][0]}..{WINDOW_DATES[w][1]}) --")
    for r in RUNGS:
        m = RESULTS[r]["base_ticks1"][w]
        print(f"   {r:8s} net=${m['net']:>13,.2f}  sharpe={m['sharpe']!s:>8}  "
              f"sortino={m['sortino']!s:>8}  calmar={m['calmar']!s:>8}  "
              f"maxDD_eod=${m['maxDD_eod']!s:>12}  CDaR(house)=${m['CDaR_0.95_dollar_primary_objective_house']!s:>12}")
