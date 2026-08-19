#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOMFLOW01 -- 01_tomflow01.py
Runs the FROZEN SPEC.md (committed 1d5ee2d BEFORE this executed). Classic McConnell-Xu
turn-of-month long window on the 20-year NQ minute substrate. Run from repo root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "research", "system_master", "TOMFLOW01_TURN_OF_MONTH", "out")

SEED = 20260821
NB = 10_000
TICK = 0.25
PV = 20.0
COMM_RT = 4.36

print("[TOMFLOW01] loading minute substrate ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
hm = df["time"].dt.hour * 100 + df["time"].dt.minute
rth = df[(hm >= 930) & (hm <= 1558)]
g = rth.groupby("d")
nb = g.size()
valid = nb[nb >= 200].index
close = g["close"].last().loc[valid]
close.index = pd.to_datetime(pd.Index(close.index))
close = close.sort_index()
days = close.index
print(f"[TOMFLOW01] trading days: {len(days)} ({days[0].date()}..{days[-1].date()})", flush=True)

per = pd.Series(days, index=days).groupby([days.year, days.month])


def month_days(y, m):
    try:
        return list(per.get_group((y, m)))
    except KeyError:
        return []


def build_events(entry_off_from_end, exit_day_of_next):
    """entry at close of month's (entry_off_from_end)-th-to-last trading day;
    exit at close of next month's (exit_day_of_next)-th trading day."""
    rows = []
    keys = sorted(per.groups.keys())
    for i in range(len(keys) - 1):
        y, m = keys[i]
        y2, m2 = keys[i + 1]
        cur = month_days(y, m); nxt = month_days(y2, m2)
        if len(cur) < entry_off_from_end + 3 or len(nxt) < exit_day_of_next:
            continue
        ein = cur[-entry_off_from_end]
        eout = nxt[exit_day_of_next - 1]
        e = close.loc[ein] + TICK          # long entry, adverse
        x = close.loc[eout] - TICK         # exit, adverse
        pnl = (x - e) * PV - COMM_RT
        rows.append({"entry": ein, "exit": eout, "pnl": pnl})
    return pd.DataFrame(rows)


def build_placebo():
    rows = []
    for (y, m), _ in per:
        cur = month_days(y, m)
        if len(cur) < 14:
            continue
        ein = cur[-10]
        # exit 4 trading days later (may spill to next month list -> use global days)
        gi = days.get_loc(ein)
        if gi + 4 >= len(days):
            continue
        eout = days[gi + 4]
        e = close.loc[ein] + TICK
        x = close.loc[eout] - TICK
        rows.append({"entry": ein, "exit": eout, "pnl": (x - e) * PV - COMM_RT})
    return pd.DataFrame(rows)


def boot_iid(x, seed):
    rng = np.random.default_rng(seed)
    xn = np.asarray(x); m = np.empty(NB)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_yearblock(T, seed):
    yr = pd.to_datetime(T["entry"]).dt.year
    groups = [T.loc[yr == y, "pnl"].to_numpy() for y in sorted(yr.unique())]
    rng = np.random.default_rng(seed)
    m = np.empty(NB); ng = len(groups)
    for k in range(NB):
        pick = rng.integers(0, ng, ng)
        m[k] = np.concatenate([groups[p] for p in pick]).mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


res = {"seed": SEED, "n_boot": NB}
T = build_events(2, 3)   # primary: T-2 entry, exit next month's 3rd trading day
res["G1_N"] = int(len(T)); res["G1_pass"] = len(T) >= 200
res["net_total"] = float(T["pnl"].sum()); res["net_per_event"] = float(T["pnl"].mean())

ilo, ihi = boot_iid(T["pnl"], SEED)
ylo, yhi = boot_yearblock(T, SEED)
res["G2_ci_iid"] = [ilo, ihi]; res["G2_ci_yearblock"] = [ylo, yhi]
res["G2_pass"] = ilo > 0 and ylo > 0

yr = pd.to_datetime(T["entry"]).dt.year
pre = T[yr < 2020]; post = T[yr >= 2020]
plo, phi = boot_iid(pre["pnl"], SEED + 1)
qlo, qhi = boot_iid(post["pnl"], SEED + 2)
res["G3_pre2020"] = {"n": int(len(pre)), "mean": float(pre["pnl"].mean()), "ci": [plo, phi]}
res["G3_post2020"] = {"n": int(len(post)), "mean": float(post["pnl"].mean()), "ci": [qlo, qhi]}
res["G3_pass"] = bool(pre["pnl"].mean() > 0 and post["pnl"].mean() > 0
                      and (plo > 0 or qlo > 0) and not (phi < 0) and not (qhi < 0))

m16 = T[yr >= 2016]
res["G4_2016_2026_mean"] = float(m16["pnl"].mean()); res["G4_pass"] = m16["pnl"].mean() > 0

P = build_placebo()
pllo, plhi = boot_iid(P["pnl"], SEED + 3)
res["G5_placebo"] = {"n": int(len(P)), "mean": float(P["pnl"].mean()), "ci": [pllo, plhi]}
res["G5_pass"] = bool(pllo <= 0 and T["pnl"].mean() > P["pnl"].mean())

variants = {"T2_T3_primary": (2, 3), "T1_T3": (1, 3), "T2_T2": (2, 2)}
plat = {}
for name, (a, b) in variants.items():
    tt = build_events(a, b)
    plat[name] = {"n": int(len(tt)), "mean": float(tt["pnl"].mean())}
res["G6_plateau"] = plat
res["G6_pass"] = all(v["mean"] > 0 for v in plat.values())

absnet = abs(res["net_total"])
srt = T["pnl"].sort_values(ascending=False)
k1 = max(1, int(0.01 * len(T)))
res["G7_top1pct_share"] = float(srt.head(k1).sum() / absnet)
res["G7_max_winner_share"] = float(srt.iloc[0] / absnet)
res["G7_max_loser_share"] = float(abs(srt.iloc[-1]) / absnet)
res["G7_worst"] = float(srt.iloc[-1]); res["G7_best"] = float(srt.iloc[0])
res["G7_worst_dates"] = {str(T.loc[i, "entry"].date()): float(T.loc[i, "pnl"])
                         for i in T["pnl"].nsmallest(5).index}
res["G7_pass"] = (res["G7_top1pct_share"] <= 0.50 and res["G7_max_winner_share"] <= 0.25
                  and res["G7_max_loser_share"] <= 0.25)

led = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                               "HTFDIR01_DIRECTIONAL_TILT", "out", "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
# daily attribution: spread event pnl across held days proportional to daily close moves? Spec
# says daily ledger overlap; use per-day mark-to-market of the held position (long 1 NQ):
pos_days = {}
for _, r in T.iterrows():
    gi = days.get_loc(r["entry"]); go = days.get_loc(r["exit"])
    for k in range(gi + 1, go + 1):
        d0, d1 = days[k - 1], days[k]
        pos_days[d1] = pos_days.get(d1, 0.0) + (close.loc[d1] - close.loc[d0]) * PV
mtm = pd.Series(pos_days)
j = pd.DataFrame({"tom": mtm, "solar": led["B_SYM"]}).dropna()
res["G8_overlap_days"] = int(len(j))
res["G8_corr_full"] = float(j["tom"].corr(j["solar"])) if len(j) > 10 else None
losing = j[j["solar"] < 0]
res["G8_corr_losing"] = float(losing["tom"].corr(losing["solar"])) if len(losing) > 10 else None
res["G8_net_on_solar_losing"] = float(losing["tom"].sum()) if len(losing) else 0.0
res["G8_pass"] = (res["G8_corr_losing"] is None) or (res["G8_corr_losing"] <= 0.25)

Ts = T.copy()
Ts["pnl"] = Ts["pnl"] + COMM_RT - 3 * COMM_RT - (2 * (2.0 - 1.0)) * TICK * PV  # widen to 2t/side, 3x comm
slo, shi = boot_iid(Ts["pnl"], SEED + 4)
sylo, syhi = boot_yearblock(Ts, SEED + 4)
yrs = pd.to_datetime(Ts["entry"]).dt.year
res["G9_stress"] = {"mean": float(Ts["pnl"].mean()), "ci_iid": [slo, shi],
                    "ci_yearblock": [sylo, syhi],
                    "pre2020_mean": float(Ts.loc[yrs < 2020, "pnl"].mean()),
                    "post2020_mean": float(Ts.loc[yrs >= 2020, "pnl"].mean())}
res["G9_pass"] = bool(slo > 0 and sylo > 0 and res["G9_stress"]["pre2020_mean"] > 0
                      and res["G9_stress"]["post2020_mean"] > 0)

res["per_year_net"] = {str(y): float(T.loc[yr == y, "pnl"].sum()) for y in sorted(yr.unique())}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = all(bool(res[k]) for k in gates)

T.to_csv(os.path.join(OUT, "tomflow01_events.csv"), index=False)
P.to_csv(os.path.join(OUT, "tomflow01_placebo.csv"), index=False)
with open(os.path.join(OUT, "tomflow01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
