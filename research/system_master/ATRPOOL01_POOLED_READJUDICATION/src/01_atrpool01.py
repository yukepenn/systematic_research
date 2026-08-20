#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRPOOL01 -- 01_atrpool01.py
Runs the FROZEN SPEC.md gates G0-G5. Pure arithmetic on SMV2AJ's committed curves;
no simulator, no new data. Battery verbatim from runs/SMV2AJ_ATR_BLEND_R2/src/gate_A.py.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "system_master", "ATRPOOL01_POOLED_READJUDICATION")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED, BLOCK, NBOOT = 20260820, 5, 10_000

dev = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2", "out", "curves.csv"))
hist = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2", "out",
                                "gate_C_hist_curves.csv"), index_col=0)
dev["sess"] = pd.to_datetime(dev["sess"])
hist.index = pd.to_datetime(hist.index)

res = {"seed": SEED, "block": BLOCK, "n_boot": NBOOT}

# ---------- G0 integrity ----------
g0 = {
    "dev_net_ctrl": (float(dev.DUAL_CONTROL.sum()), 138280.0),
    "dev_net_blend": (float(dev.DUAL_BLEND75.sum()), 144815.2),
    "hist_net_ctrl": (float(hist.DUAL_CONTROL_hist.sum()), 447134.7),
    "hist_net_blend": (float(hist.DUAL_BLEND75_hist.sum()), 533138.9),
}


def sharpe(x):
    return float(x.mean() / x.std(ddof=1) * np.sqrt(252))


def maxdd(x):
    eq = np.cumsum(np.asarray(x))
    return float((np.maximum.accumulate(eq) - eq).max())


g0.update({
    "dev_sharpe_ctrl": (sharpe(dev.DUAL_CONTROL), 0.8992),
    "dev_sharpe_blend": (sharpe(dev.DUAL_BLEND75), 0.9431),
    "hist_sharpe_ctrl": (sharpe(hist.DUAL_CONTROL_hist), 0.2945),
    "hist_sharpe_blend": (sharpe(hist.DUAL_BLEND75_hist), 0.3504),
    "hist_maxdd_ctrl": (maxdd(hist.DUAL_CONTROL_hist), 246834.0),
    "hist_maxdd_blend": (maxdd(hist.DUAL_BLEND75_hist), 213326.8),
})
res["G0_detail"] = {k: [round(a, 4), b] for k, (a, b) in g0.items()}
res["G0_pass"] = all(abs(a - b) <= (0.1 if abs(b) > 10 else 1e-4) for a, b in g0.values())

# ---------- pooled series ----------
xc = np.concatenate([hist.DUAL_CONTROL_hist.to_numpy(), dev.DUAL_CONTROL.to_numpy()])
xb = np.concatenate([hist.DUAL_BLEND75_hist.to_numpy(), dev.DUAL_BLEND75.to_numpy()])
dates = np.concatenate([hist.index.to_numpy(), dev.sess.to_numpy()])
n = len(xc)
res["n_pooled"] = int(n)


def make_idx(rng, n_, nboot):
    nb = int(np.ceil(n_ / BLOCK))
    starts = rng.integers(0, n_, size=(nboot, nb))
    return ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n_).reshape(nboot, -1)[:, :n_]


def path_stats(x, idx, k, chunk=500):
    shp = np.empty(len(idx)); cdr = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr[i:i + chunk] = (-np.partition(-dd, k - 1, axis=1)[:, :k]).mean(axis=1)
    return shp, cdr


def paired_mbb(xc_, xb_, seed, label):
    n_ = len(xc_); k = max(1, int(0.05 * n_))
    rng = np.random.default_rng(seed)
    idx = make_idx(rng, n_, NBOOT)
    sc, cc = path_stats(xc_, idx, k)
    sb, cb = path_stats(xb_, idx, k)
    p_shp = float(((sb - sc) > 0).mean())
    p_cdr = float(((cc - cb) > 0).mean())
    print(f"  [{label}] n={n_} P(dSharpe>0)={p_shp:.4f} P(dCDaR>0)={p_cdr:.4f}", flush=True)
    kk = max(1, int(0.05 * n_))
    eqc = np.cumsum(xc_); eqb = np.cumsum(xb_)
    ddc = np.maximum.accumulate(eqc) - eqc; ddb = np.maximum.accumulate(eqb) - eqb
    return {"n": n_, "k_worst": kk,
            "point_sharpe_ctrl": sharpe(pd.Series(xc_)), "point_sharpe_blend": sharpe(pd.Series(xb_)),
            "point_cdar_ctrl": float(np.sort(ddc)[::-1][:kk].mean()),
            "point_cdar_blend": float(np.sort(ddb)[::-1][:kk].mean()),
            "P_dSharpe_gt0": p_shp, "P_dCDaR_gt0": p_cdr}


print("[ATRPOOL01] G1 pooled paired MBB ...", flush=True)
g1 = paired_mbb(xc, xb, SEED, "G1 pooled")
res["G1"] = g1
res["G1_pass"] = bool(g1["P_dSharpe_gt0"] >= 0.90 and g1["P_dCDaR_gt0"] >= 0.90)

print("[ATRPOOL01] G2 era-level ...", flush=True)
g2_dev = paired_mbb(dev.DUAL_CONTROL.to_numpy(), dev.DUAL_BLEND75.to_numpy(), SEED + 1, "G2 dev")
g2_hist = paired_mbb(hist.DUAL_CONTROL_hist.to_numpy(), hist.DUAL_BLEND75_hist.to_numpy(),
                     SEED + 2, "G2 hist")
res["G2_dev"] = g2_dev; res["G2_hist"] = g2_hist
res["G2_pass"] = bool(
    (g2_dev["point_sharpe_blend"] > g2_dev["point_sharpe_ctrl"])
    and (g2_hist["point_sharpe_blend"] > g2_hist["point_sharpe_ctrl"])
    and g2_dev["P_dCDaR_gt0"] >= 0.55 and g2_hist["P_dCDaR_gt0"] >= 0.55)

# ---------- G3-SPLIT ----------
diff = xb - xc
pre = diff[dates < np.datetime64("2020-01-01")]
post = diff[dates >= np.datetime64("2020-01-01")]


def iid_ci(x, seed):
    rng = np.random.default_rng(seed)
    m = np.empty(NBOOT)
    xn = np.asarray(x)
    for i in range(NBOOT):
        m[i] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


plo, phi = iid_ci(pre, SEED + 3)
qlo, qhi = iid_ci(post, SEED + 4)
res["G3_pre2020"] = {"n": int(len(pre)), "mean": float(pre.mean()), "ci": [plo, phi]}
res["G3_post2020"] = {"n": int(len(post)), "mean": float(post.mean()), "ci": [qlo, qhi]}
res["G3_pass"] = bool(pre.mean() > 0 and post.mean() > 0
                      and (plo > 0 or qlo > 0) and not (phi < 0) and not (qhi < 0))

# ---------- G4 pooled right-tail retention ----------
top10 = np.argsort(xc)[::-1][:10]
ctrl_top = float(xc[top10].sum()); blend_on_top = float(xb[top10].sum())
res["G4"] = {"ctrl_top10_sum": ctrl_top, "blend_on_ctrl_top10": blend_on_top,
             "retention": blend_on_top / ctrl_top,
             "top10_dates": [str(pd.Timestamp(dates[i]).date()) for i in top10]}
res["G4_pass"] = bool(blend_on_top >= 0.95 * ctrl_top)

# ---------- G5 stratified convention ----------
print("[ATRPOOL01] G5 stratified pooled ...", flush=True)
nh, nd = len(hist), len(dev)
kpool = max(1, int(0.05 * n))
rng = np.random.default_rng(SEED + 5)
idx_h = make_idx(rng, nh, NBOOT)
idx_d = make_idx(rng, nd, NBOOT)
xch, xbh = hist.DUAL_CONTROL_hist.to_numpy(), hist.DUAL_BLEND75_hist.to_numpy()
xcd, xbd = dev.DUAL_CONTROL.to_numpy(), dev.DUAL_BLEND75.to_numpy()
shp_c = np.empty(NBOOT); shp_b = np.empty(NBOOT)
cdr_c = np.empty(NBOOT); cdr_b = np.empty(NBOOT)
chunk = 250
for i in range(0, NBOOT, chunk):
    Xc = np.concatenate([xch[idx_h[i:i + chunk]], xcd[idx_d[i:i + chunk]]], axis=1)
    Xb = np.concatenate([xbh[idx_h[i:i + chunk]], xbd[idx_d[i:i + chunk]]], axis=1)
    for X, shp_a, cdr_a in ((Xc, shp_c, cdr_c), (Xb, shp_b, cdr_b)):
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp_a[i:i + chunk] = mu / sd_ * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr_a[i:i + chunk] = (-np.partition(-dd, kpool - 1, axis=1)[:, :kpool]).mean(axis=1)
res["G5"] = {"P_dSharpe_gt0": float(((shp_b - shp_c) > 0).mean()),
             "P_dCDaR_gt0": float(((cdr_c - cdr_b) > 0).mean())}
res["G5_pass"] = bool(res["G5"]["P_dSharpe_gt0"] >= 0.85 and res["G5"]["P_dCDaR_gt0"] >= 0.85)
res["G1_G5_convention_agree"] = bool(res["G1_pass"] == res["G5_pass"])

gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates) and res["G1_G5_convention_agree"])

with open(os.path.join(OUT, "atrpool01_results.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1), flush=True)
