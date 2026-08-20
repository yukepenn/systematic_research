#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRPOOL01 -- 00_power_audit.py  (INSTRUMENTATION, zero alpha budget)

Question: what was the statistical power of SMV2AJ gate A's dev-only CDaR prong
(P(dCDaR>0) >= 0.85, paired MBB block=5 B=10k) to detect an effect of the size the
dev point estimates themselves showed? And what power would the same prong have at
the pooled sample size (5,269 sessions)?

CRITICAL SCOPE LIMIT: this script reads ONLY the dev pair (curves.csv, already
published in SMV2AJ's REPORT). It never touches gate_C_hist_curves.csv values --
only its ROW COUNT (4,130, also published) enters, as the pooled n. No pooled
outcome statistic is computed here. The one-shot pooled readout runs only after
SPEC.md is frozen and committed.

Method: outer Monte Carlo. DGP = circular block bootstrap (block=5) of the dev
PAIR (control, blend jointly, preserving the pairing). For each synthetic dataset
of length n, run the inner gate-A bootstrap (block=5, B=2000, fresh seed) and
record whether the CDaR prong clears 0.85. Power = fraction of outer reps passing.
"""
import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "system_master", "ATRPOOL01_POOLED_READJUDICATION")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED = 20260820
BLOCK = 5
INNER_B = 2000
OUTER_R = 300
N_DEV = 1139
N_POOLED = 1139 + 4130  # dev sessions + published hist row count; no hist values read

curves = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2", "out", "curves.csv"))
xc = curves["DUAL_CONTROL"].to_numpy()
xb = curves["DUAL_BLEND75"].to_numpy()
n0 = len(xc)
assert n0 == N_DEV


def make_idx(rng, n, nboot):
    nb = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, n, size=(nboot, nb))
    return ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(nboot, -1)[:, :n]


def path_cdar_sharpe(x, idx, k, chunk=500):
    shp = np.empty(len(idx)); cdr = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr[i:i + chunk] = (-np.partition(-dd, k - 1, axis=1)[:, :k]).mean(axis=1)
    return shp, cdr


def one_power_run(n, outer_seed_base, label):
    passes_cdar = 0; passes_sharpe = 0; passes_both = 0
    p_cdar_list = []
    for r in range(OUTER_R):
        rng = np.random.default_rng(outer_seed_base + r)
        # synthetic paired dataset of length n from the dev pair (circular block=5)
        syn_idx = make_idx(rng, n0, 1)[0] if n == n0 else None
        if n == n0:
            sc, sb = xc[syn_idx], xb[syn_idx]
        else:
            # length-n synthetic: sample ceil(n/BLOCK) blocks from the dev pair
            nb = int(np.ceil(n / BLOCK))
            starts = rng.integers(0, n0, size=nb)
            ii = ((starts[:, None] + np.arange(BLOCK)[None, :]) % n0).reshape(-1)[:n]
            sc, sb = xc[ii], xb[ii]
        k = max(1, int(0.05 * n))
        inner_idx = make_idx(rng, n, INNER_B)
        shp_c, cdr_c = path_cdar_sharpe(sc, inner_idx, k)
        shp_b, cdr_b = path_cdar_sharpe(sb, inner_idx, k)
        p_shp = float(((shp_b - shp_c) > 0).mean())
        p_cdr = float(((cdr_c - cdr_b) > 0).mean())
        p_cdar_list.append(p_cdr)
        passes_cdar += p_cdr >= 0.85
        passes_sharpe += p_shp >= 0.85
        passes_both += (p_cdr >= 0.85) and (p_shp >= 0.85)
        if (r + 1) % 50 == 0:
            print(f"  [{label}] outer {r+1}/{OUTER_R}: power_cdar so far "
                  f"{passes_cdar/(r+1):.3f}", flush=True)
    return {"n": n, "outer_reps": OUTER_R, "inner_B": INNER_B,
            "power_cdar_prong_at_085": passes_cdar / OUTER_R,
            "power_sharpe_prong_at_085": passes_sharpe / OUTER_R,
            "power_both_prongs_at_085": passes_both / OUTER_R,
            "median_inner_P_dCDaR": float(np.median(p_cdar_list)),
            "q10_inner_P_dCDaR": float(np.quantile(p_cdar_list, 0.10)),
            "q90_inner_P_dCDaR": float(np.quantile(p_cdar_list, 0.90))}


print("[ATRPOOL01 power audit] dev-length instrument (n=1139) ...", flush=True)
res_dev = one_power_run(N_DEV, SEED, "n=1139")
print("[ATRPOOL01 power audit] pooled-length instrument (n=5269) ...", flush=True)
res_pool = one_power_run(N_POOLED, SEED + 100000, "n=5269")

out = {"seed": SEED, "block": BLOCK,
       "dgp": "circular block-5 bootstrap of the SMV2AJ dev pair (effect = dev point estimate)",
       "scope_note": "no hist curve VALUES read; only published hist row count (4130) used",
       "dev_instrument": res_dev, "pooled_instrument": res_pool}
with open(os.path.join(OUT, "power_audit.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1), flush=True)
