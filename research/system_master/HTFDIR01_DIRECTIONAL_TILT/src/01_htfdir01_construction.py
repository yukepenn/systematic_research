#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTFDIR01 -- 01_htfdir01_construction.py

Construction test per SPEC.md (committed fb44d67, BEFORE this ran). One candidate arm
(LONGONLY direction-conditioned HTF tilt), one mechanism-falsification control (SHORTONLY),
against the incumbent (SYM). Executors are `solve_A`/`solve_B` copied verbatim from
PLACEBO01/HTFMECH01 with the SINGLE spec'd change: `m_arr` is computed by tilt_mode.
Gate #2 requires SYM to reproduce grid_core's own certified full-array execution.

Nothing >= 2026-08-01 is touched (grid_core loads through 2026-07-31 only).
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
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))

OUT_DIR = os.path.join(ROOT, "research", "system_master", "HTFDIR01_DIRECTIONAL_TILT", "out")
os.makedirs(OUT_DIR, exist_ok=True)

SEED = 20260818
N_BOOT = 10_000

print("[HTFDIR01] importing grid_core (self-check = gate #1) ...", flush=True)
import grid_core as GC  # noqa: E402
from grid_core import (rha, _fill_n, TILTMULT, SHORTHALF, TILTRESCALE, KSOLAR, KBMOM,
                       WSOLAR, WBMOM, ENTRY_LEVEL, EXIT_LEVEL, PV_MNQ_A, COMM_MNQ_A,
                       PV_NQ, COMM_NQ, dd_battery)  # noqa: E402
print("[HTFDIR01] gate #1 PASS (grid_core certified-net self-check ran on import)", flush=True)

# Full arrays (through 2026-07-31), masks
T_f = GC._T0.astype(int)
B_f = np.asarray(GC.B_LEG)
tilt_f = GC.TILT_STATE
open_f, high_f, low_f, close_f = GC.OPEN_, GC.HIGH, GC.LOW, GC.CLOSE
last_f = GC.LAST
eb_f, ff_f = GC.ENTRY_BLOCKED_C4, GC.FORCED_FLAT_C4
sd_f = GC.SD
DEV = GC.DEV_MASK
sess_dt = pd.to_datetime(pd.Series(GC.SD))

EXT_MASK = ((sess_dt > GC.DEV_END) & (sess_dt <= GC.HEALTH_END)).to_numpy()


def make_m_arr(T_bar, tilt_bar, mode):
    """The ONLY spec'd degree of freedom. SYM is the incumbent, byte-equivalent to
    the verbatim expression in PLACEBO01/HTFMECH01."""
    if mode == "SYM":
        return np.where((T_bar != 0) & (tilt_bar != 0)
                        & (np.sign(T_bar) == tilt_bar), TILTMULT, 1.0)
    if mode == "LONGONLY":
        return np.where((T_bar > 0) & (tilt_bar > 0), TILTMULT, 1.0)
    if mode == "SHORTONLY":
        return np.where((T_bar < 0) & (tilt_bar < 0), TILTMULT, 1.0)
    raise ValueError(mode)


# solve_A / solve_B: copied VERBATIM from HTFMECH01 (itself verbatim from PLACEBO01),
# except m_arr is taken from make_m_arr(mode). No other line differs.
def solve_A(tilt_bar, T_bar, B_bar, open_, high, low, close, last, entry_blocked, forced_flat,
            pv=PV_MNQ_A, comm=COMM_MNQ_A, ticks=1, mode="SYM"):
    n = len(T_bar)
    m_arr = make_m_arr(T_bar, tilt_bar, mode)
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
            pv=PV_NQ, comm=COMM_NQ, ticks=1, mode="SYM"):
    n = len(T_bar)
    m_arr = make_m_arr(T_bar, tilt_bar, mode)
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


def daily(bar_pnl, mask):
    s = pd.Series(np.asarray(bar_pnl)[mask], index=pd.Index(np.asarray(sd_f)[mask]))
    return s.groupby(level=0).sum().sort_index()


def sharpe(d):
    sd = d.std(ddof=1)
    return float(d.mean() / sd * np.sqrt(252)) if sd > 0 else float("nan")


# ================= GATE #2: SYM reproduces grid_core's own execution ====================
print("[HTFDIR01] gate #2: SYM vs grid_core full-array execution ...", flush=True)
_, pnl_A_gc, _ = GC.product_a_exec(GC._T0, ticks=1)
_, pnl_A_sym, _ = solve_A(tilt_f, T_f, B_f, open_f, high_f, low_f, close_f, last_f, eb_f, ff_f,
                          mode="SYM")
assert abs(float(pnl_A_gc[DEV].sum()) - float(pnl_A_sym[DEV].sum())) < 0.01, "gate2 A dev"
assert np.allclose(pnl_A_gc, pnl_A_sym, atol=1e-6), "gate2 A full-array"

_, _, pnl_B_gc, _ = GC.product_b_exec(GC._T0, ticks=1)
_, _, pnl_B_sym, _ = solve_B(tilt_f, T_f, B_f, open_f, high_f, low_f, close_f, last_f, eb_f, ff_f,
                             mode="SYM")
assert abs(float(pnl_B_gc[DEV].sum()) - float(pnl_B_sym[DEV].sum())) < 0.01, "gate2 B dev"
assert np.allclose(pnl_B_gc, pnl_B_sym, atol=1e-6), "gate2 B full-array"
print(f"[HTFDIR01] gate #2 PASS: A dev ${pnl_A_sym[DEV].sum():,.2f}, "
      f"B dev ${pnl_B_sym[DEV].sum():,.2f}", flush=True)

# B-MNQ economics check (reported, not gated; disclosure if mismatch)
_, _, pnl_Bm_sym, _ = solve_B(tilt_f, T_f, B_f, open_f, high_f, low_f, close_f, last_f, eb_f, ff_f,
                              pv=PV_MNQ_A, comm=COMM_MNQ_A, mode="SYM")
mnq_dev_net = float(pnl_Bm_sym[DEV].sum())
mnq_matches = abs(mnq_dev_net - 28587.10) < 1.0
print(f"[HTFDIR01] B-MNQ SYM dev net ${mnq_dev_net:,.2f} "
      f"({'matches certified' if mnq_matches else 'DOES NOT match certified 28,587.10 — reported with disclosure'})",
      flush=True)

# ================= Runs: 3 arms x products ==============================================
arms = {}
for mode in ("SYM", "LONGONLY", "SHORTONLY"):
    if mode == "SYM":
        pnl_A, pnl_B = pnl_A_sym, pnl_B_sym
        pnl_Bm = pnl_Bm_sym
    else:
        _, pnl_A, _ = solve_A(tilt_f, T_f, B_f, open_f, high_f, low_f, close_f, last_f,
                              eb_f, ff_f, mode=mode)
        _, _, pnl_B, _ = solve_B(tilt_f, T_f, B_f, open_f, high_f, low_f, close_f, last_f,
                                 eb_f, ff_f, mode=mode)
        _, _, pnl_Bm, _ = solve_B(tilt_f, T_f, B_f, open_f, high_f, low_f, close_f, last_f,
                                  eb_f, ff_f, pv=PV_MNQ_A, comm=COMM_MNQ_A, mode=mode)
    arms[mode] = {
        "A_dev": daily(pnl_A, DEV), "B_dev": daily(pnl_B, DEV), "Bm_dev": daily(pnl_Bm, DEV),
        "A_ext": daily(pnl_A, EXT_MASK), "B_ext": daily(pnl_B, EXT_MASK),
    }
    print(f"[HTFDIR01] arm {mode}: A dev ${arms[mode]['A_dev'].sum():,.2f} "
          f"shp {sharpe(arms[mode]['A_dev']):.4f} | B dev ${arms[mode]['B_dev'].sum():,.2f} "
          f"shp {sharpe(arms[mode]['B_dev']):.4f}", flush=True)

# Persist daily ledgers
led = pd.DataFrame({f"{p}_{m}": arms[m][f"{p}_dev"]
                    for m in arms for p in ("A", "B", "Bm")})
led.index.name = "sess_date"
led.to_csv(os.path.join(OUT_DIR, "daily_ledgers_dev.csv"))

# ================= Gates ================================================================
rng = np.random.default_rng(SEED)
results = {"seed": SEED, "n_boot": N_BOOT, "mnq_econ_matches_certified": bool(mnq_matches),
           "gates": {}, "batteries": {}, "extension_2026_06_07": {}}


def paired_boot_p_dsharpe_gt0(d_cand, d_inc):
    x = d_cand.to_numpy(); y = d_inc.to_numpy(); n = len(x)
    assert len(y) == n
    wins = 0
    chunk = 1000
    done = 0
    while done < N_BOOT:
        k = min(chunk, N_BOOT - done)
        idx = rng.integers(0, n, size=(k, n))
        xs = x[idx]; ys = y[idx]
        sx = xs.mean(1) / xs.std(1, ddof=1) * np.sqrt(252)
        sy = ys.mean(1) / ys.std(1, ddof=1) * np.sqrt(252)
        wins += int((sx > sy).sum())
        done += k
    return wins / N_BOOT


def loyo(d_cand, d_inc):
    yrs = sorted(set(pd.to_datetime(d_cand.index).year))
    out = {}
    for y in yrs:
        m = pd.to_datetime(d_cand.index).year != y
        out[str(y)] = sharpe(d_cand[m]) - sharpe(d_inc[m])
    return out


def gates_for(prod):
    inc = arms["SYM"][f"{prod}_dev"]; cand = arms["LONGONLY"][f"{prod}_dev"]
    sh_ctl = arms["SHORTONLY"][f"{prod}_dev"]
    g = {}
    g["net_inc"] = float(inc.sum()); g["net_cand"] = float(cand.sum())
    g["sharpe_inc"] = sharpe(inc); g["sharpe_cand"] = sharpe(cand)
    g["dSharpe"] = g["sharpe_cand"] - g["sharpe_inc"]
    g["G1_p_dsharpe_gt0"] = paired_boot_p_dsharpe_gt0(cand, inc)
    g["G1_pass"] = g["G1_p_dsharpe_gt0"] >= 0.85
    ly = loyo(cand, inc)
    g["G2_loyo"] = ly
    yr = pd.to_datetime(cand.index).year
    pre26 = yr <= 2025
    g["G2_dnet_2022_2025"] = float(cand[pre26].sum() - inc[pre26].sum())
    g["G2_pass"] = all(v >= 0 for v in ly.values()) and g["G2_dnet_2022_2025"] >= 0
    top10 = inc.nlargest(10)
    g["G3_top10_retention"] = float(cand.loc[top10.index].sum() / top10.sum())
    g["G3_pass"] = g["G3_top10_retention"] >= 0.95
    g["top20_table"] = {str(k): [float(v), float(cand.loc[k])]
                        for k, v in inc.nlargest(20).items()}
    bi = dd_battery(pd.to_datetime(inc.index), inc.to_numpy(), label=f"{prod}_inc")
    bc = dd_battery(pd.to_datetime(cand.index), cand.to_numpy(), label=f"{prod}_cand")
    g["G4_cdar95_inc"] = float(bi["CDaR5"]); g["G4_cdar95_cand"] = float(bc["CDaR5"])
    g["G4_pass"] = bc["CDaR5"] <= bi["CDaR5"] * 1.02
    g["maxDD_inc"] = float(bi["maxDD_eod"]); g["maxDD_cand"] = float(bc["maxDD_eod"])
    g["G5_ctl_p_dsharpe_gt0"] = paired_boot_p_dsharpe_gt0(sh_ctl, inc)
    g["G5_ctl_sharpe"] = sharpe(sh_ctl)
    g["G5_pass"] = g["G5_ctl_p_dsharpe_gt0"] < 0.85
    m26 = yr == 2026
    g["G7_dnet_2026janmay"] = float(cand[m26].sum() - inc[m26].sum())
    results["batteries"][prod] = {"incumbent": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                                                for k, v in bi.items()},
                                  "candidate": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                                                for k, v in bc.items()}}
    return g


for prod in ("A", "B", "Bm"):
    print(f"[HTFDIR01] gates for {prod} ...", flush=True)
    results["gates"][prod] = gates_for(prod)

for prod in ("A", "B"):
    e_i = arms["SYM"][f"{prod}_ext"]; e_c = arms["LONGONLY"][f"{prod}_ext"]
    results["extension_2026_06_07"][prod] = {
        "net_inc": float(e_i.sum()), "net_cand": float(e_c.sum()),
        "label": "research-consumed extension, NON-PROMOTIONAL (CURRENT_EDGE_HEALTH precedent)"}

with open(os.path.join(OUT_DIR, "htfdir01_results.json"), "w") as f:
    json.dump(results, f, indent=1, default=float)

print(json.dumps({p: {k: v for k, v in g.items() if not isinstance(v, dict)}
                  for p, g in results["gates"].items()}, indent=1, default=float), flush=True)
print("[HTFDIR01] done; G6 (primary_objective_v2 both conventions) runs in script 02.", flush=True)
