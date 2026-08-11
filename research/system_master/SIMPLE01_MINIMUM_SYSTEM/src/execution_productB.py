#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMPLE01 -- execution_productB.py: EXECUTION AGENT run of the FROZEN Product B ladder
(B0, B1, B_FULL) against the frozen manifest (00_SPEC_candidate_manifest.md) and frozen
margins/methodology (01_SPEC_frozen_margins.md), campaign directive sec73.

ROLE DISCIPLINE: this script does not adjudicate anything. It runs exactly the three frozen
Product B rungs, computes the metrics the execution task asked for, over the two windows the
execution task named (canonical 2023-01-01..2025-02-02, and the fuller available history
through the LOCKED_FORWARD boundary, i.e. up to and including 2026-07-31 -- grid_core's own
HEALTH_END), plus the dev window (2022-01-01..2026-05-31) that 01_SPEC_frozen_margins.md
freezes as the PRIMARY gating window for whatever adjudication phase consumes this output.
No pass/fail judgement, no rung selection, is made here.

REUSE, NOT REINVENTION: imports grid_core.py verbatim (the campaign's own already-certified,
self-checking substrate -- Solar13 ensemble T, real tiltState, real bmomPos/B_LEG, the C4
entry-block/forced-flat clocks, and grid_core._build_pos_seq / grid_core._onelot_exec, the
exact Product B position-sequencer and one-lot executor already used throughout this program).
grid_core's own import-time self-check (Product A dev-window net == $177,924.40, Product B
dev-window net == $301,915.92) is CORRECTNESS GATE #1 and runs automatically before a single
line below executes. This script's own GATE #2 (below) additionally confirms the B_FULL rung,
built from this script's rung-forcing wrapper, is bar-for-bar IDENTICAL to grid_core's own
product_b_exec output at ticks=1 -- i.e. that the wrapper mechanism itself introduces no drift
from the certified incumbent before any B0/B1 ablation is trusted.

Metric battery reuses smv2_common.dd_battery (net/Sharpe/Sortino/Calmar/maxDD_eod/CDaR5/...,
this program's own frozen definitions) and primary_objective.cdar_dollar/top10_day_retention
(house alpha=0.95 CDaR and top-10-day-retention conventions, CONVENTIONS.md/primary_objective.py).

Cost stress: reuses grid_core's own `ticks` adverse-slip generalization already built into
_onelot_exec (ticks=1 IS the canonical base-cost convention already embedded in every other
certified figure in this repo). "+1 tick/side" stress = ticks=2, "+2 ticks/side" stress =
ticks=3 -- literal increments of the same mechanism, not a new cost model.

Output: research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/execution_productB_raw.json
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
print("[SIMPLE01-EXEC-B] importing grid_core (certified substrate; self-check runs at import) ...",
      flush=True)
import grid_core as GC  # noqa: E402
from primary_objective import cdar_dollar as po_cdar_dollar, top10_day_retention as po_top10_ret  # noqa: E402
from smv2_common import dd_battery  # noqa: E402

print(f"[SIMPLE01-EXEC-B] grid_core imported + self-checked in {time.time() - T0:.1f}s "
      f"(GATE #1 PASS: Product A dev-window net $177,924.40, Product B dev-window net "
      f"$301,915.92, both reproduced exactly on import -- see grid_core's own printed "
      f"self-check line above)", flush=True)

N = GC.N
T_full = GC._T0.astype(int)
TILT_full = GC.TILT_STATE
B_full = np.asarray(GC.B_LEG)
SD_full = GC.SD
SESS_DT_full = GC.SESS_DT

print(f"[SIMPLE01-EXEC-B] full substrate: N={N} bars, "
      f"{pd.Series(SD_full).nunique()} sessions, {SESS_DT_full.min().date()}..{SESS_DT_full.max().date()}",
      flush=True)

# ================================================================================================
# FROZEN PRODUCT B LADDER -- exact constructions per 00_SPEC_candidate_manifest.md sec1.2.
# All three rungs reuse grid_core._build_pos_seq / grid_core._onelot_exec VERBATIM (the same
# functions grid_core.product_b_exec itself calls) -- only the mm/bmomPos FORCING differs.
# ================================================================================================
RUNGS = {
    "B0": {"mm": "forced", "bmom": "forced",
           "desc": "Solar only: mm forced 1.0, bmomPos forced 0"},
    "B1": {"mm": "forced", "bmom": "real",
           "desc": "Solar + B-MOM: mm forced 1.0, bmomPos real"},
    "B_FULL": {"mm": "real", "bmom": "real",
               "desc": "incumbent, unmodified: mm real, bmomPos real"},
}


def build_rung_M(mm_mode, bmom_mode):
    if mm_mode == "forced":
        m_arr = np.ones(N)
    elif mm_mode == "real":
        m_arr = np.where((T_full != 0) & (TILT_full != 0) & (np.sign(T_full) == TILT_full),
                          GC.TILTMULT, 1.0)
    else:
        raise ValueError(mm_mode)

    if bmom_mode == "forced":
        b_arr = np.zeros(N)
    elif bmom_mode == "real":
        b_arr = B_full
    else:
        raise ValueError(bmom_mode)

    Tp = np.clip(GC.rha(T_full * m_arr * GC.TILTRESCALE), -13, 13)
    M = GC.WSOLAR * Tp + GC.WBMOM * b_arr
    return M


def exec_rung(rung_name, ticks=1):
    """pos_seq is ticks-independent (position logic never looks at fill price); bar_pos/bar_pnl
    depend on ticks via grid_core._onelot_exec's adverse-slip fill. Reuses grid_core's own
    _build_pos_seq / _onelot_exec verbatim -- no formula re-typed here."""
    spec = RUNGS[rung_name]
    M = build_rung_M(spec["mm"], spec["bmom"])
    pos_seq = GC._build_pos_seq(M)  # verbatim reuse
    bar_pos, bar_pnl = GC._onelot_exec(pos_seq, GC.COMM_NQ, GC.PV_NQ, ticks=ticks)  # verbatim reuse
    return pos_seq, bar_pos, bar_pnl


print("[SIMPLE01-EXEC-B] building position sequences (ticks-independent) for B0/B1/B_FULL ...",
      flush=True)
POS_SEQ = {}
for r in RUNGS:
    M_r = build_rung_M(RUNGS[r]["mm"], RUNGS[r]["bmom"])
    POS_SEQ[r] = GC._build_pos_seq(M_r)
    print(f"[SIMPLE01-EXEC-B]   {r}: {RUNGS[r]['desc']}", flush=True)

# ================================================================================================
# GATE #2 -- B_FULL rung (this script's own wrapper, mm real / bmomPos real) must be bar-for-bar
# IDENTICAL to grid_core.product_b_exec's own output at ticks=1 -- confirms the rung-forcing
# wrapper mechanism itself introduces zero drift from the certified incumbent before any B0/B1
# ablation result is trusted.
# ================================================================================================
print("[SIMPLE01-EXEC-B] GATE #2: B_FULL wrapper vs grid_core.product_b_exec (ticks=1) ...",
      flush=True)
_pos_seq_gc, _bar_pos_gc, _bar_pnl_gc, _M_gc = GC.product_b_exec(T_full, ticks=1)
_pos_seq_bfull, _bar_pos_bfull, _bar_pnl_bfull = exec_rung("B_FULL", ticks=1)
gate2_exact = bool(np.array_equal(_bar_pnl_bfull, _bar_pnl_gc)) and \
              bool(np.array_equal(_bar_pos_bfull, _bar_pos_gc))
gate2_maxdiff = float(np.max(np.abs(_bar_pnl_bfull - _bar_pnl_gc)))
_dev_net_bfull = float(_bar_pnl_bfull[GC.DEV_MASK].sum())
gate2_devnet_ok = abs(_dev_net_bfull - 301915.92) < 1.0
print(f"[SIMPLE01-EXEC-B] GATE #2: bar-for-bar exact={gate2_exact} (max abs diff {gate2_maxdiff:.2e}); "
      f"B_FULL wrapper dev-window net=${_dev_net_bfull:,.2f} vs certified $301,915.92 "
      f"(match={gate2_devnet_ok})", flush=True)
assert gate2_exact, "GATE #2 FAILED: B_FULL wrapper does not reproduce grid_core.product_b_exec bar-for-bar."
assert gate2_devnet_ok, "GATE #2 FAILED: B_FULL wrapper dev-window net does not match certified $301,915.92."
print("[SIMPLE01-EXEC-B] GATE #2 PASS.", flush=True)

CORRECTNESS_GATE = {
    "gate_1_grid_core_import_self_check": "PASS (dev-window net Product A=$177,924.40, "
                                           "Product B=$301,915.92, asserted inside grid_core.py "
                                           "import; this script never proceeds past that import "
                                           "if it fails)",
    "gate_2_B_FULL_wrapper_vs_grid_core_product_b_exec": {
        "bar_for_bar_exact_match": gate2_exact,
        "max_abs_bar_pnl_diff": gate2_maxdiff,
        "B_FULL_wrapper_dev_window_net": round(_dev_net_bfull, 2),
        "certified_dev_window_net": 301915.92,
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

print("[SIMPLE01-EXEC-B] executing all rungs x cost-stress levels ...", flush=True)
BAR_POS = {}
BAR_PNL = {}
for r in RUNGS:
    BAR_POS[r] = {}
    BAR_PNL[r] = {}
    for cl_name, ticks in COST_LEVELS.items():
        t0 = time.time()
        bar_pos, bar_pnl = GC._onelot_exec(POS_SEQ[r], GC.COMM_NQ, GC.PV_NQ, ticks=ticks)
        BAR_POS[r][cl_name] = bar_pos
        BAR_PNL[r][cl_name] = bar_pnl
        print(f"[SIMPLE01-EXEC-B]   {r} / {cl_name} (ticks={ticks}) done in "
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


# ================================================================================================
# MAIN METRIC SWEEP: rung x cost_level x window
# ================================================================================================
print("[SIMPLE01-EXEC-B] computing metric battery for every rung x cost-level x window ...",
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
print(f"[SIMPLE01-EXEC-B] metric sweep done in {time.time() - T0:.1f}s total elapsed.", flush=True)

# ================================================================================================
# TOP-10-DAY RETENTION vs B_FULL (base cost, per window) -- reuses
# primary_objective.top10_day_retention verbatim, baseline = B_FULL's own daily series.
# ================================================================================================
print("[SIMPLE01-EXEC-B] top-10-day retention vs B_FULL (base cost, per window) ...", flush=True)
TOP10_RETENTION = {}
for w_name in WINDOWS:
    base_series = DAILY_BASE["B_FULL"][w_name]
    TOP10_RETENTION[w_name] = {}
    for r in RUNGS:
        s = DAILY_BASE[r][w_name]
        assert len(s) == len(base_series) and (s.index == base_series.index).all(), \
            f"daily index misalignment for {r}/{w_name} vs B_FULL"
        TOP10_RETENTION[w_name][r] = _clean(po_top10_ret(s.to_numpy(), base_series.to_numpy()))

# ================================================================================================
# LARGEST-SINGLE-DAY SHARE OF INCREMENTAL ADVANTAGE OVER B_FULL (base cost, per window, B0/B1 only)
# advantage_day = daily_rung - daily_B_FULL; total_advantage = sum(advantage_day) (== net_rung -
# net_B_FULL for that window). Share = max(advantage_day) / total_advantage, defined only when
# total_advantage > 0 (rung outperforms B_FULL) -- the concentration gate is asymmetric by design
# (01_SPEC_frozen_margins.md sec3.8: fires only on claimed improvements).
# ================================================================================================
print("[SIMPLE01-EXEC-B] largest-single-day share of incremental advantage vs B_FULL "
      "(base cost, per window) ...", flush=True)
CONCENTRATION = {}
for w_name in WINDOWS:
    base_series = DAILY_BASE["B_FULL"][w_name]
    CONCENTRATION[w_name] = {}
    for r in ("B0", "B1"):
        s = DAILY_BASE[r][w_name]
        diff = (s - base_series).to_numpy()
        total_adv = float(diff.sum())
        max_day = float(diff.max())
        max_day_date = str(s.index[int(np.argmax(diff))])
        share = (max_day / total_adv) if total_adv > 0 else None
        CONCENTRATION[w_name][r] = {
            "total_incremental_advantage_over_B_FULL": total_adv,
            "applicable_rung_outperforms_B_FULL": bool(total_adv > 0),
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
print("[SIMPLE01-EXEC-B] annual net by calendar year (base cost) ...", flush=True)
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
    print(f"[SIMPLE01-EXEC-B] wrote {fpath} ({len(d)} sessions)", flush=True)

# ================================================================================================
# FINAL SUMMARY JSON
# ================================================================================================
summary = {
    "task": "SIMPLE01 execution -- Product B frozen ladder (B0, B1, B_FULL)",
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
                     "n_sessions_B_FULL_base_cost": int(RESULTS["B_FULL"]["base_ticks1"][w]["n_sessions"])}
                for w in WINDOWS},
    "correctness_gates": CORRECTNESS_GATE,
    "metrics_by_rung_costlevel_window": RESULTS,
    "top10_day_pnl_retention_vs_B_FULL_base_cost": TOP10_RETENTION,
    "largest_single_day_share_of_incremental_advantage_vs_B_FULL_base_cost": CONCENTRATION,
    "annual_net_by_year_base_cost": ANNUAL_NET,
    "daily_pnl_files_full_history_base_cost": DAILY_PNL_FILES,
    "runtime_seconds_total": round(time.time() - T0, 1),
}

json_path = os.path.join(OUT_DIR, "execution_productB_raw.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"[SIMPLE01-EXEC-B] wrote {json_path}", flush=True)
print(f"[SIMPLE01-EXEC-B] TOTAL RUNTIME {time.time() - T0:.1f}s", flush=True)
print("\n" + "=" * 78)
print("SIMPLE01 EXECUTION (Product B) -- HEADLINE (no adjudication, figures only)")
print("=" * 78)
for w in WINDOWS:
    print(f"-- window {w} ({WINDOW_DATES[w][0]}..{WINDOW_DATES[w][1]}) --")
    for r in RUNGS:
        m = RESULTS[r]["base_ticks1"][w]
        print(f"   {r:8s} net=${m['net']:>13,.2f}  sharpe={m['sharpe']!s:>8}  "
              f"sortino={m['sortino']!s:>8}  calmar={m['calmar']!s:>8}  "
              f"maxDD_eod=${m['maxDD_eod']!s:>12}  CDaR(house)=${m['CDaR_0.95_dollar_primary_objective_house']!s:>12}")
