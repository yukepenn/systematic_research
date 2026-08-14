#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTFMECH01 -- 01_htf_mechanism_decomposition.py

Diagnostic only, per SPEC.md (committed before this ran). Decomposes PLACEBO01's already-
established whole-window finding (HTF's real marginal net/Sharpe contribution sits at the
27.8th-32.1st percentile of its own randomized-chronology null, i.e. below the null median for
both products) by YEAR and by SIGNAL SIDE (long/short), using the exact same certified substrate
and executor functions PLACEBO01 itself used (`solve_A`/`solve_B`, copied verbatim from
`research/system_master/PLACEBO01_COMPONENT_CAUSALITY/src/02_htf_placebo.py`, not modified).

This computes ONLY the real-vs-baseline marginal (the cheap half of PLACEBO01's script) -- it does
NOT regenerate the 1000-draw null, so no new per-slice significance test is produced (see SPEC.md
sec6, disclosed as a scoping boundary, not an oversight).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "system_master",
                                 "GRID01_SOLAR_RESOLUTION_CONVERGENCE", "src"))

OUT_DIR = os.path.join(ROOT, "research", "system_master", "HTFMECH01_TILT_MECHANISM", "out")
os.makedirs(OUT_DIR, exist_ok=True)

print("[HTFMECH01] importing grid_core (certified substrate, self-checked on import) ...", flush=True)
import grid_core as GC  # noqa: E402
from grid_core import (rha, _fill_n, TILTMULT, SHORTHALF, TILTRESCALE, KSOLAR, KBMOM,
                        WSOLAR, WBMOM, ENTRY_LEVEL, EXIT_LEVEL, PV_MNQ_A, COMM_MNQ_A,
                        PV_NQ, COMM_NQ, dd_battery)  # noqa: E402
print("[HTFMECH01] grid_core imported + self-checked (gate #1 PASS)", flush=True)

# =========================================================================================
# Canonical window slice -- identical to PLACEBO01's own (2023-01-01..2025-02-02).
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

print(f"[HTFMECH01] canonical window: {n_canon} bars, {GC.CANON_START.date()}..{GC.CANON_END.date()}, "
      f"{pd.Series(sd_c).nunique()} sessions", flush=True)

# =========================================================================================
# solve_A / solve_B -- copied VERBATIM from PLACEBO01's 02_htf_placebo.py (not modified).
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
# GATE #2 -- cross-check against grid_core's own full-array execution, sliced to canonical
# window, to within $0.01 -- same gate PLACEBO01 runs before trusting anything downstream.
# =========================================================================================
print("[HTFMECH01] GATE #2: cross-checking against grid_core's own full-array execution ...", flush=True)
_bp_A_gc, _pnl_A_gc, _ = GC.product_a_exec(GC._T0, ticks=1)
_gc_net_A_canon = float(_pnl_A_gc[GC.CANON_MASK].sum())
_, _pnl_A_mine, _ = solve_A(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c, last_c, eb_c, ff_c)
_mine_net_A_canon = float(_pnl_A_mine.sum())
assert abs(_gc_net_A_canon - _mine_net_A_canon) < 0.01, \
    f"GATE #2 FAILED (A): grid_core={_gc_net_A_canon:.2f} vs solve_A={_mine_net_A_canon:.2f}"

_, _bp_B_gc, _pnl_B_gc, _ = GC.product_b_exec(GC._T0, ticks=1)
_gc_net_B_canon = float(_pnl_B_gc[GC.CANON_MASK].sum())
_, _, _pnl_B_mine, _ = solve_B(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c, last_c, eb_c, ff_c)
_mine_net_B_canon = float(_pnl_B_mine.sum())
assert abs(_gc_net_B_canon - _mine_net_B_canon) < 0.01, \
    f"GATE #2 FAILED (B): grid_core={_gc_net_B_canon:.2f} vs solve_B={_mine_net_B_canon:.2f}"
print(f"[HTFMECH01] GATE #2 PASS: A canon net ${_mine_net_A_canon:,.2f}, B canon net ${_mine_net_B_canon:,.2f} "
      f"(both match grid_core's own full-array execution to $0.01)", flush=True)

# =========================================================================================
# REAL vs BASELINE (tilt=0) -- identical construction to PLACEBO01.
# =========================================================================================
tilt_zero_c = np.zeros(n_canon, dtype=int)

_, bp_A_real, _ = solve_A(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c, last_c, eb_c, ff_c)
_, bp_A_base, _ = solve_A(tilt_zero_c, T_c, B_c, open_c, high_c, low_c, close_c, last_c, eb_c, ff_c)
marginal_A = bp_A_real - bp_A_base

_, _, bp_B_real, _ = solve_B(tilt_real_c, T_c, B_c, open_c, high_c, low_c, close_c, last_c, eb_c, ff_c)
_, _, bp_B_base, _ = solve_B(tilt_zero_c, T_c, B_c, open_c, high_c, low_c, close_c, last_c, eb_c, ff_c)
marginal_B = bp_B_real - bp_B_base

print(f"[HTFMECH01] whole-window real_marginal_net_A=${marginal_A.sum():,.2f}  "
      f"real_marginal_net_B=${marginal_B.sum():,.2f}  "
      f"(cross-check vs PLACEBO01's own reported real_marginal_net -- should match)", flush=True)

# =========================================================================================
# YEAR decomposition.
# =========================================================================================
years = pd.to_datetime(pd.Series(sd_c)).dt.year.to_numpy()
year_rows = []
for y in sorted(np.unique(years)):
    mask = years == y
    n_sessions_y = pd.Series(sd_c[mask]).nunique()
    row = {
        "year": int(y),
        "n_bars": int(mask.sum()),
        "n_sessions": int(n_sessions_y),
        "marginal_net_A": float(marginal_A[mask].sum()),
        "marginal_net_B": float(marginal_B[mask].sum()),
    }
    year_rows.append(row)
year_df = pd.DataFrame(year_rows)
year_df.to_csv(os.path.join(OUT_DIR, "htfmech01_year_decomposition.csv"), index=False)
print("[HTFMECH01] year decomposition:\n" + year_df.to_string(index=False), flush=True)

# =========================================================================================
# SIDE decomposition -- by sign(T_bar) for A, sign(Tp-driving T_bar) for B (same underlying
# Solar consensus signal feeds both products' HTF-gated multiplier).
# =========================================================================================
side = np.where(T_c > 0, "long", np.where(T_c < 0, "short", "flat"))
side_rows = []
for s in ["long", "short", "flat"]:
    mask = side == s
    row = {
        "side_T_bar": s,
        "n_bars": int(mask.sum()),
        "marginal_net_A": float(marginal_A[mask].sum()),
        "marginal_net_B": float(marginal_B[mask].sum()),
    }
    side_rows.append(row)
side_df = pd.DataFrame(side_rows)
side_df.to_csv(os.path.join(OUT_DIR, "htfmech01_side_decomposition.csv"), index=False)
print("[HTFMECH01] side decomposition (by sign of T_bar at each bar -- descriptive, position "
      "carries forward across regime changes, see SPEC.md):\n" + side_df.to_string(index=False), flush=True)

# =========================================================================================
# Results JSON.
# =========================================================================================
results = {
    "gate2_pass": True,
    "canon_window": [str(GC.CANON_START.date()), str(GC.CANON_END.date())],
    "n_bars": int(n_canon),
    "whole_window_real_marginal_net_A": float(marginal_A.sum()),
    "whole_window_real_marginal_net_B": float(marginal_B.sum()),
    "year_decomposition": year_rows,
    "side_decomposition": side_rows,
    "note": "Descriptive decomposition only -- no per-slice null/significance test computed, "
            "per SPEC.md sec6. Whole-window totals should match PLACEBO01's own reported "
            "real_marginal_net_A / real_marginal_net_B exactly (same computation, same inputs).",
}
with open(os.path.join(OUT_DIR, "htfmech01_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"[HTFMECH01] wrote {OUT_DIR}\\htfmech01_results.json", flush=True)
