#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONRANGE01 -- 01_onrange01.py
Runs the FROZEN SPEC.md (commit 8178106). ARM_A OCO first-break continuation, ARM_B stop
variant, stale-level PLACEBO. Costs C1. Run from repo root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "system_master", "ONRANGE01_OVERNIGHT_BREAK")
OUT = os.path.join(RUN, "out")

SEED, NB = 20260820, 10_000
TICK, PV, COMM = 0.25, 20.0, 4.36

print("[ONRANGE01] loading ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
df["hm"] = df["time"].dt.hour * 100 + df["time"].dt.minute

facts = pd.read_csv(os.path.join(OUT, "onrange_daily_facts.csv"), parse_dates=["day"])
facts = facts[facts.open_in_range].reset_index(drop=True)
by_date = dict(tuple(df.groupby("d")))


def run_day(D, onh, onl, use_stop):
    """OCO first-break entry; returns dict or None (no trigger / same-bar双破 skip)."""
    r = by_date.get(D)
    r = r[(r["hm"] >= 930) & (r["hm"] <= 1558)].sort_values("time")
    if not len(r):
        return None
    hi = r["high"].to_numpy(); lo = r["low"].to_numpy(); cl = r["close"].to_numpy()
    up = hi > onh + TICK  # buy stop at onh+1t triggers when high crosses it
    dn = lo < onl - TICK
    iu = int(np.argmax(up)) if up.any() else -1
    idn = int(np.argmax(dn)) if dn.any() else -1
    if iu < 0 and idn < 0:
        return None
    if iu >= 0 and idn >= 0 and iu == idn:
        return {"skip_samebar": True}
    if iu >= 0 and (idn < 0 or iu < idn):
        side, ei = 1, iu
        entry = onh + 2 * TICK
        stop_lvl = onl - 2 * TICK
    else:
        side, ei = -1, idn
        entry = onl - 2 * TICK
        stop_lvl = onh + 2 * TICK
    exit_px = cl[-1] - side * TICK
    stopped = False
    if use_stop:
        if side == 1:
            hit = lo[ei + 1:] < onl - TICK
        else:
            hit = hi[ei + 1:] > onh + TICK
        if len(hit) and hit.any():
            stopped = True
            exit_px = stop_lvl
    pnl = side * (exit_px - entry) * PV - COMM
    return {"side": side, "entry_i": ei, "pnl": pnl, "stopped": stopped,
            "entry_hm": int(r["hm"].iloc[ei])}


rows_a, rows_b, rows_p = [], [], []
skips = 0
prev_levels = None
for _, f in facts.iterrows():
    D = f.day.date()
    a = run_day(D, f.on_high, f.on_low, use_stop=False)
    if a is not None and a.get("skip_samebar"):
        skips += 1
        a = None
    if a is not None:
        rows_a.append({"day": f.day, "year": f.day.year, **a})
        b = run_day(D, f.on_high, f.on_low, use_stop=True)
        if b is not None and not b.get("skip_samebar"):
            rows_b.append({"day": f.day, **b})
    if prev_levels is not None:
        p = run_day(D, prev_levels[0], prev_levels[1], use_stop=False)
        if p is not None and not p.get("skip_samebar"):
            rows_p.append({"day": f.day, "pnl": p["pnl"]})
    prev_levels = (f.on_high, f.on_low)

A = pd.DataFrame(rows_a)
B = pd.DataFrame(rows_b)
P = pd.DataFrame(rows_p)


def boot_iid(x, seed):
    rng = np.random.default_rng(seed)
    xn = np.asarray(x); m = np.empty(NB)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_yearblock(tt, seed):
    yr = pd.to_datetime(tt["day"]).dt.year
    groups = [tt.loc[yr == y, "pnl"].to_numpy() for y in sorted(yr.unique())]
    rng = np.random.default_rng(seed)
    m = np.empty(NB); ng = len(groups)
    for k in range(NB):
        pick = rng.integers(0, ng, ng)
        m[k] = np.concatenate([groups[p_] for p_ in pick]).mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def t_nw(x, lag=5):
    x = np.asarray(x, float); n_ = len(x); xb = x.mean(); z = x - xb
    S = float((z ** 2).sum())
    for l in range(1, min(lag, n_ - 1) + 1):
        S += 2.0 * (1.0 - l / (lag + 1.0)) * float((z[l:] * z[:-l]).sum())
    return xb / (np.sqrt(S) / n_)


res = {"seed": SEED, "spec_commit": "8178106", "skip_samebar": skips}
res["G1_N"] = int(len(A)); res["G1_pass"] = len(A) >= 2000
res["net_total"] = float(A.pnl.sum()); res["net_per_trade"] = float(A.pnl.mean())
ilo, ihi = boot_iid(A.pnl, SEED); ylo, yhi = boot_yearblock(A, SEED)
res["G2_ci_iid"] = [ilo, ihi]; res["G2_ci_yearblock"] = [ylo, yhi]
res["G2_pass"] = bool(res["net_total"] > 0 and ilo > 0 and ylo > 0)

yr = pd.to_datetime(A["day"]).dt.year
pre, post = A[yr < 2020], A[yr >= 2020]
plo, phi = boot_iid(pre.pnl, SEED + 1); qlo, qhi = boot_iid(post.pnl, SEED + 2)
res["G3_pre2020"] = {"n": int(len(pre)), "mean": float(pre.pnl.mean()), "ci": [plo, phi]}
res["G3_post2020"] = {"n": int(len(post)), "mean": float(post.pnl.mean()), "ci": [qlo, qhi]}
res["G3_pass"] = bool(pre.pnl.mean() > 0 and post.pnl.mean() > 0
                      and (plo > 0 or qlo > 0) and not (phi < 0) and not (qhi < 0))

res["placebo_n"] = int(len(P)); res["placebo_mean"] = float(P.pnl.mean())
merged = A.merge(P, on="day", suffixes=("_a", "_p"))
res["G4_paired_n"] = int(len(merged))
res["G4_diff_tnw"] = float(t_nw((merged.pnl_a - merged.pnl_p).to_numpy()))
res["G4_pass"] = bool(A.pnl.mean() > P.pnl.mean() and res["G4_diff_tnw"] >= 2)

absnet = abs(res["net_total"])
srt = A.pnl.sort_values(ascending=False)
k1 = max(1, int(0.01 * len(A)))
res["G7_top1pct_share"] = float(srt.head(k1).sum() / absnet)
res["G7_max_win_share"] = float(srt.iloc[0] / absnet)
res["G7_max_loss_share"] = float(abs(srt.iloc[-1]) / absnet)
res["G7_pass"] = bool(res["G7_top1pct_share"] <= 0.5 and res["G7_max_win_share"] <= 0.25
                      and res["G7_max_loss_share"] <= 0.25)

led = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                               "HTFDIR01_DIRECTIONAL_TILT", "out", "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
j = pd.DataFrame({"onr": A.set_index("day").pnl, "solar": led["B_SYM"]}).dropna()
losing = j[j.solar < 0]
res["G8_overlap"] = int(len(j)); res["G8_losing_n"] = int(len(losing))
res["G8_corr_losing"] = float(losing.onr.corr(losing.solar)) if len(losing) > 10 else None
res["G8_net_on_solar_losing"] = float(losing.onr.sum())
res["G8_pass"] = (res["G8_corr_losing"] is None) or (res["G8_corr_losing"] <= 0.25)

stress = A.pnl + COMM - 3 * COMM - 2 * (2 - 1) * TICK * PV
slo, shi = boot_iid(stress, SEED + 3)
sylo, syhi = boot_yearblock(pd.DataFrame({"day": A.day, "pnl": stress}), SEED + 3)
res["G9_stress"] = {"mean": float(stress.mean()), "ci_iid": [slo, shi],
                    "ci_yearblock": [sylo, syhi]}
res["G9_pass"] = bool(stress.sum() > 0 and slo > 0 and sylo > 0)

res["by_side"] = {s: {"n": int(g.pnl.count()), "mean": float(g.pnl.mean())}
                  for s, g in A.groupby("side")}
res["by_early_late"] = {
    "le_1030": {"n": int((A.entry_hm <= 1030).sum()),
                "mean": float(A.loc[A.entry_hm <= 1030, "pnl"].mean())},
    "after_1030": {"n": int((A.entry_hm > 1030).sum()),
                   "mean": float(A.loc[A.entry_hm > 1030, "pnl"].mean())}}
res["ARM_B"] = {"n": int(len(B)), "net": float(B.pnl.sum()), "mean": float(B.pnl.mean()),
                "stopped_frac": float(B.stopped.mean()),
                "ci_iid": list(boot_iid(B.pnl, SEED + 4))}
res["per_year"] = {str(y): float(A.loc[yr == y, "pnl"].sum()) for y in sorted(yr.unique())}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates))

A.to_csv(os.path.join(OUT, "onrange01_trades_a.csv"), index=False)
B.to_csv(os.path.join(OUT, "onrange01_trades_b.csv"), index=False)
P.to_csv(os.path.join(OUT, "onrange01_placebo.csv"), index=False)
with open(os.path.join(OUT, "onrange01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
