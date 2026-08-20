#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONRANGE02 -- 01_onrange02.py
Runs the FROZEN SPEC.md (commit 312b0f7). Short below mid toward ONL / long above mid toward
ONH; target-limit exits with gap-through price improvement; else 15:58 close. Run from root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "system_master", "ONRANGE02_MID_TO_EDGE")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED, NB = 20260820, 10_000
TICK, PV, COMM = 0.25, 20.0, 4.36

print("[ONRANGE02] loading ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
df["hm"] = df["time"].dt.hour * 100 + df["time"].dt.minute

facts = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                                 "ONRANGE01_OVERNIGHT_BREAK", "out",
                                 "onrange_daily_facts.csv"), parse_dates=["day"])
facts = facts[facts.open_in_range].reset_index(drop=True)
by_date = dict(tuple(df.groupby("d")))

rows = []
for _, f in facts.iterrows():
    D = f.day.date()
    onh, onl = f.on_high, f.on_low
    mid = (onh + onl) / 2.0
    r = by_date.get(D)
    r = r[(r["hm"] >= 930) & (r["hm"] <= 1558)].sort_values("time")
    if not len(r):
        continue
    o = r["open"].iloc[0]
    if o == mid or not (onl < o < onh):
        continue
    hi = r["high"].to_numpy(); lo = r["low"].to_numpy()
    op = r["open"].to_numpy(); cl = r["close"].to_numpy()
    side = -1 if o < mid else 1
    entry = o - side * TICK  # market at open, 1t adverse
    if side == -1:
        tgt_hit = lo < onl
        opp_hit = hi > onh
    else:
        tgt_hit = hi > onh
        opp_hit = lo < onl
    it = int(np.argmax(tgt_hit)) if tgt_hit.any() else -1
    io = int(np.argmax(opp_hit)) if opp_hit.any() else -1
    hit = it >= 0
    hit_before_opp = bool(it >= 0 and (io < 0 or it <= io))
    if hit:
        if side == -1:
            x = min(op[it], onl) + TICK  # buy-to-cover limit, gap-through improves
        else:
            x = max(op[it], onh) - TICK
        exit_hm = int(r["hm"].iloc[it])
    else:
        x = cl[-1] + side * (-TICK) if False else cl[-1] - side * TICK
        exit_hm = 1558
    pnl_a = side * (x - entry) * PV - COMM
    # ARM_B: stop at opposite level (first crossing bar; stop-through fills at worse open)
    pnl_b = pnl_a; stopped = False
    if io >= 0 and (it < 0 or io < it):
        stopped = True
        if side == -1:
            xs = max(op[io], onh) + TICK  # buy stop above onh; gap-through fills worse
        else:
            xs = min(op[io], onl) - TICK
        pnl_b = side * (xs - entry) * PV - COMM
    rows.append({"day": f.day, "side": side, "open_depth": (o - onl) / (onh - onl),
                 "range_pts": onh - onl, "dist_to_tgt_pts": (o - onl) if side == -1 else (onh - o),
                 "hit": hit, "hit_before_opp": hit_before_opp, "exit_hm": exit_hm,
                 "pnl": pnl_a, "pnl_b": pnl_b, "stopped_b": stopped})

A = pd.DataFrame(rows)
yr = pd.to_datetime(A["day"]).dt.year


def boot_iid(x, seed):
    rng = np.random.default_rng(seed)
    xn = np.asarray(x); m = np.empty(NB)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_yearblock(pnl, years, seed):
    groups = [pnl[years == y].to_numpy() for y in sorted(years.unique())]
    rng = np.random.default_rng(seed)
    m = np.empty(NB); ng = len(groups)
    for k in range(NB):
        pick = rng.integers(0, ng, ng)
        m[k] = np.concatenate([groups[p] for p in pick]).mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


res = {"seed": SEED, "spec_commit": "312b0f7"}
res["G1_N"] = int(len(A)); res["G1_pass"] = len(A) >= 2000
sh = A[A.side == -1]; lg = A[A.side == 1]
res["prob_answers"] = {
    "P_hit_target_short_side": float(sh.hit.mean()), "n_short": int(len(sh)),
    "P_hit_target_long_side": float(lg.hit.mean()), "n_long": int(len(lg)),
    "P_hit_before_opposite_short": float(sh.hit_before_opp.mean()),
    "P_hit_before_opposite_long": float(lg.hit_before_opp.mean()),
    "win_rate_short": float((sh.pnl > 0).mean()), "win_rate_long": float((lg.pnl > 0).mean()),
    "median_exit_hm_when_hit": float(A.loc[A.hit, "exit_hm"].median()),
    "median_dist_to_target_pts": float(A.dist_to_tgt_pts.median()),
    "median_range_pts": float(A.range_pts.median())}

res["net_total"] = float(A.pnl.sum()); res["net_per_trade"] = float(A.pnl.mean())
ilo, ihi = boot_iid(A.pnl, SEED); ylo, yhi = boot_yearblock(A.pnl, yr, SEED)
res["G2_ci_iid"] = [ilo, ihi]; res["G2_ci_yearblock"] = [ylo, yhi]
res["G2_pass"] = bool(res["net_total"] > 0 and ilo > 0 and ylo > 0)

pre, post = A[yr < 2020], A[yr >= 2020]
plo, phi = boot_iid(pre.pnl, SEED + 1); qlo, qhi = boot_iid(post.pnl, SEED + 2)
res["G3_pre2020"] = {"n": int(len(pre)), "mean": float(pre.pnl.mean()), "ci": [plo, phi]}
res["G3_post2020"] = {"n": int(len(post)), "mean": float(post.pnl.mean()), "ci": [qlo, qhi]}
res["G3_pass"] = bool(pre.pnl.mean() > 0 and post.pnl.mean() > 0
                      and (plo > 0 or qlo > 0) and not (phi < 0) and not (qhi < 0))

absnet = abs(res["net_total"]) if res["net_total"] != 0 else 1.0
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
res["G8_corr_losing"] = float(losing.onr.corr(losing.solar)) if len(losing) > 10 else None
res["G8_net_on_solar_losing"] = float(losing.onr.sum())
res["G8_pass"] = bool(((res["G8_corr_losing"] is None) or (res["G8_corr_losing"] <= 0.25))
                      and res["G8_net_on_solar_losing"] > -100_000)

stress = A.pnl + COMM - 3 * COMM - 2 * (2 - 1) * TICK * PV
slo, shi = boot_iid(stress, SEED + 3)
sylo, syhi = boot_yearblock(pd.Series(stress.to_numpy()), yr.reset_index(drop=True), SEED + 3)
res["G9_stress"] = {"mean": float(stress.mean()), "ci_iid": [slo, shi],
                    "ci_yearblock": [sylo, syhi]}
res["G9_pass"] = bool(stress.sum() > 0 and slo > 0 and sylo > 0)

res["by_side_mean"] = {"short": float(sh.pnl.mean()), "long": float(lg.pnl.mean())}
res["by_depth_quartile"] = {}
A["depthq"] = pd.qcut(A.open_depth, 4, labels=["q1_low", "q2", "q3", "q4_high"])
for q, g in A.groupby("depthq", observed=True):
    res["by_depth_quartile"][str(q)] = {"n": int(len(g)), "mean": float(g.pnl.mean()),
                                        "hit_rate": float(g.hit.mean())}
res["ARM_B"] = {"net": float(A.pnl_b.sum()), "mean": float(A.pnl_b.mean()),
                "stopped_frac": float(A.stopped_b.mean()),
                "ci_iid": list(boot_iid(A.pnl_b, SEED + 4))}
res["per_year"] = {str(y): float(A.loc[yr == y, "pnl"].sum()) for y in sorted(yr.unique())}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates))

A.drop(columns=["depthq"]).to_csv(os.path.join(OUT, "onrange02_trades.csv"), index=False)
with open(os.path.join(OUT, "onrange02_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
