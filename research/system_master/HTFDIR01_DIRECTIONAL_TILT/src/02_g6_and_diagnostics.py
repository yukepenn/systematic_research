#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTFDIR01 -- 02_g6_and_diagnostics.py

(a) G6 per SPEC: Product A scored under BOTH O1 aggregation conventions (mixture J and
    Gamma-minimax J_worst) for incumbent and LONGONLY candidate. A has already failed
    G1/G2/G3 in script 01; this is run to honor the frozen gate list, not to rescue A.
(b) Red-team feed diagnostics for Product B's pass: concentration of the delta
    (top-day share, quarterly table, per-year), mechanism footprint (how many bars have
    a different tilt multiplier / different position), bootstrap CI of dSharpe.
Run from repo root.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
OUT_DIR = os.path.join(ROOT, "research", "system_master", "HTFDIR01_DIRECTIONAL_TILT", "out")

led = pd.read_csv(os.path.join(OUT_DIR, "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
out = {}

# ---------------- (a) G6: both O1 conventions on Product A ------------------------------
import primary_objective_v2 as po2  # noqa: E402

g6 = {}
for label, col in (("incumbent", "A_SYM"), ("candidate", "A_LONGONLY")):
    s = led[col].copy()
    res = po2.primary_objective(s, label=f"HTFDIR01_A_{label}")
    agg = res["aggregation"] if isinstance(res, dict) else res
    g6[label] = {
        "J_mixture": float(agg["J"]),
        "J_worst_gamma_minimax": float(agg["J_worst"]),
    }
g6["dJ_mixture"] = g6["candidate"]["J_mixture"] - g6["incumbent"]["J_mixture"]
g6["dJ_worst"] = (g6["candidate"]["J_worst_gamma_minimax"]
                  - g6["incumbent"]["J_worst_gamma_minimax"])
g6["verdict_flips_between_conventions"] = bool(np.sign(g6["dJ_mixture"])
                                               != np.sign(g6["dJ_worst"]))
out["G6_productA_both_conventions"] = g6
print("[HTFDIR01-02] G6:", json.dumps(g6, indent=1), flush=True)

# ---------------- (b) Product B delta diagnostics ---------------------------------------
inc = led["B_SYM"]; cand = led["B_LONGONLY"]
delta = cand - inc
yr = delta.index.year

diag = {}
diag["delta_net_total"] = float(delta.sum())
diag["n_days_delta_nonzero"] = int((delta.abs() > 1e-9).sum())
diag["n_days_total"] = int(len(delta))
top = delta.abs().nlargest(10)
diag["top10_absdelta_days"] = {str(k.date()): float(delta.loc[k]) for k in top.index}
diag["top10_absdelta_share_of_gross"] = float(top.sum() / delta.abs().sum())
best_day = float(delta.max()); worst_day = float(delta.min())
diag["best_single_delta_day"] = best_day
diag["worst_single_delta_day"] = worst_day
diag["delta_net_ex_best_day"] = float(delta.sum() - best_day)
diag["per_year_delta_net"] = {str(y): float(delta[yr == y].sum()) for y in sorted(set(yr))}
q = delta.groupby(pd.PeriodIndex(delta.index, freq="Q")).sum()
diag["per_quarter_delta_net"] = {str(k): float(v) for k, v in q.items()}
diag["quarters_positive"] = int((q > 0).sum()); diag["quarters_total"] = int(len(q))

def sharpe(d):
    sd = d.std(ddof=1)
    return float(d.mean() / sd * np.sqrt(252)) if sd > 0 else float("nan")

rng = np.random.default_rng(20260818)
x = cand.to_numpy(); y = inc.to_numpy(); n = len(x)
ds = np.empty(10_000)
done = 0
while done < 10_000:
    k = min(1000, 10_000 - done)
    idx = rng.integers(0, n, size=(k, n))
    xs = x[idx]; ys = y[idx]
    ds[done:done + k] = (xs.mean(1) / xs.std(1, ddof=1) - ys.mean(1) / ys.std(1, ddof=1)) * np.sqrt(252)
    done += k
diag["dSharpe_boot_CI90"] = [float(np.percentile(ds, 5)), float(np.percentile(ds, 95))]
diag["dSharpe_boot_CI50"] = [float(np.percentile(ds, 25)), float(np.percentile(ds, 75))]
diag["dSharpe_point"] = sharpe(cand) - sharpe(inc)

# LOYO drop-best-delta-year (stronger than LOYO>=0: drop 2024, the biggest contributor)
biggest = max(diag["per_year_delta_net"], key=lambda k: diag["per_year_delta_net"][k])
m = yr != int(biggest)
diag["drop_biggest_delta_year"] = {"year": biggest,
                                   "dSharpe_without_it": sharpe(cand[m]) - sharpe(inc[m]),
                                   "dnet_without_it": float(delta[m].sum())}
out["B_delta_diagnostics"] = diag
print("[HTFDIR01-02] B diagnostics:", json.dumps(diag, indent=1, default=float), flush=True)

with open(os.path.join(OUT_DIR, "htfdir01_g6_diagnostics.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)
print("[HTFDIR01-02] saved.", flush=True)
