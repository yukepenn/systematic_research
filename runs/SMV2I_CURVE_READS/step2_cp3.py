"""Seq 362 — C-P3 DD-constrained leverage (RESEARCH ONLY, no leverage recommendation, V4 §39).

Base = published DUAL6040 champion daily curve (reproduced exactly). L grid 1.0..3.0 step 0.1.
Constraint: P(maxDD$ over a resampled 2y (504-day) path > $25,000) <= 0.10.
Methods (all B=5000, seed 20260808, per spec path-type read):
  A stationary bootstrap, Politis-Romano, geometric mean block 20
  B moving block, block 5 (cross-check)
  C stationary mean block 20 with joint-loss block oversampling x2
    (block start prob doubled when the block contains a day where BOTH legs are negative;
     legs = DUAL and vm(BM); sign of vm(BM) equals sign of BM).
maxDD scales linearly in L, so each method's maxDD distribution is computed once and
P(L*maxDD > 25k) is read per L. L*_method = max grid L with P <= 0.10.
HEADLINE L* = worst (smallest) across methods.
Stability kill: headline L* swings > 25% when input window trimmed by +-6 months
(drop first 6mo -> start 2022-07-01; drop last 6mo -> end 2025-11-30).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from smv2i_lib import (OUT, SEED, repro_gate, maxdd_dist_moving, maxdd_dist_stationary)

res, DUAL, BM, SIG, vm, cal, champ = repro_gate()
assert res["gate_60_40_atol1e-6"]

vmBM = vm(BM)
J_full = (DUAL.values < 0) & (vmBM.values < 0)
L_GRID = np.round(np.arange(1.0, 3.0 + 1e-9, 0.1), 1)
CAP = 25_000.0
B = 5000

windows = {
    "full": np.ones(len(cal), dtype=bool),
    "trim_first6mo": np.asarray(cal >= pd.Timestamp("2022-07-01")),
    "trim_last6mo": np.asarray(cal <= pd.Timestamp("2025-11-30")),
}

rows_p = []
rows_l = []
for wname, mask in windows.items():
    x = champ.values[mask]
    J = J_full[mask]
    dists = {
        "A_stationary20": maxdd_dist_stationary(x, 504, 20, B, SEED),
        "B_moving5": maxdd_dist_moving(x, 504, 5, B, SEED),
        "C_jointloss2x": maxdd_dist_stationary(x, 504, 20, B, SEED, joint_loss=J),
    }
    lstars = {}
    for mname, d in dists.items():
        pvals = [(d * L > CAP).mean() for L in L_GRID]
        ok = [L for L, p in zip(L_GRID, pvals) if p <= 0.10]
        lstar = float(max(ok)) if ok else np.nan
        lstars[mname] = lstar
        for L, p in zip(L_GRID, pvals):
            rows_p.append({"window": wname, "method": mname, "L": L, "P_maxDD_gt_25k": p})
        rows_l.append({"window": wname, "method": mname, "n_days": int(mask.sum()),
                       "L_star": lstar, "P_at_L1": pvals[0],
                       "maxdd_dist_p50": float(np.median(d)),
                       "maxdd_dist_p90": float(np.quantile(d, 0.90))})
    lv = [v for v in lstars.values()]
    head = np.nan if any(np.isnan(v) for v in lv) else float(min(lv))
    # HEADLINE = worst (smallest) across methods; NaN if ANY method fails at grid floor L=1.0
    rows_l.append({"window": wname, "method": "HEADLINE_worst", "n_days": int(mask.sum()),
                   "L_star": head, "P_at_L1": np.nan,
                   "maxdd_dist_p50": np.nan, "maxdd_dist_p90": np.nan})

lst = pd.DataFrame(rows_l)
pcv = pd.DataFrame(rows_p)

def _head(wname):
    return float(lst[(lst.window == wname) & (lst.method == "HEADLINE_worst")]["L_star"].iloc[0])

head_full = _head("full")
if np.isnan(head_full):
    kill = "N/A_Lstar_below_grid_floor_L1.0"
    swings = {"trim_first6mo": np.nan, "trim_last6mo": np.nan}
else:
    swings = {w: abs(_head(w) - head_full) / head_full
              for w in ["trim_first6mo", "trim_last6mo"]}
    kill = bool(max(swings.values()) > 0.25)
stab = pd.DataFrame([{
    "headline_Lstar_full": head_full,
    "headline_Lstar_trim_first6mo": _head("trim_first6mo"),
    "headline_Lstar_trim_last6mo": _head("trim_last6mo"),
    "swing_first6mo": swings["trim_first6mo"],
    "swing_last6mo": swings["trim_last6mo"],
    "stability_kill_gt25pct": kill,
    "n_joint_loss_days_full": int(J_full.sum()),
}])

lst.to_csv(os.path.join(OUT, "c_p3_lstar.csv"), index=False)
pcv.to_csv(os.path.join(OUT, "c_p3_pcurves.csv"), index=False)
stab.to_csv(os.path.join(OUT, "c_p3_stability.csv"), index=False)
print(lst.to_string())
print()
print(stab.T.to_string())
