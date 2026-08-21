#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDJMA01 -- 01_kdjma01.py
Runs the FROZEN SPEC.md (commit 0df8a1b). 5m MA+KDJ entries, 20pt stop at 1m resolution,
fractal-5 ladder exits, session-close flat. Run from repo root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "system_master", "KDJMA01_5M_LADDER")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED, NB = 20260821, 10_000
TICK, PV, COMM = 0.25, 20.0, 4.36
STOP_PTS = 20.0

print("[KDJMA01] loading 1m substrate ...", flush=True)
m1 = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
m1["time"] = pd.to_datetime(m1["time"])
m1 = m1.sort_values("time").reset_index(drop=True)
# session id: bars >= 18:00 belong to the NEXT calendar day's session
sess_shift = (m1["time"] - pd.Timedelta(hours=18)).dt.date
m1["sess"] = sess_shift

# 5m bars, label = window end, within session
m1["w5"] = m1["time"].dt.floor("5min")
g5 = m1.groupby(["sess", "w5"])
b5 = pd.DataFrame({"open": g5["open"].first(), "high": g5["high"].max(),
                   "low": g5["low"].min(), "close": g5["close"].last(),
                   "t_end": g5["time"].last()}).reset_index()
b5 = b5.sort_values("t_end").reset_index(drop=True)
print(f"[KDJMA01] 5m bars: {len(b5)}", flush=True)

# indicators on the continuous 5m series (as a chartist would see them)
c = b5["close"].to_numpy(); h = b5["high"].to_numpy(); lo = b5["low"].to_numpy()
ma120 = pd.Series(c).rolling(120).mean().to_numpy()
ma127 = pd.Series(c).rolling(127).mean().to_numpy()
h9 = pd.Series(h).rolling(9).max().to_numpy()
l9 = pd.Series(lo).rolling(9).min().to_numpy()
rsv = np.full(len(c), np.nan)
den = h9 - l9
valid = den > 0
rsv[valid] = 100.0 * (c[valid] - l9[valid]) / den[valid]
K = np.full(len(c), 50.0); D = np.full(len(c), 50.0)
for i in range(1, len(c)):
    r_ = rsv[i] if np.isfinite(rsv[i]) else (K[i - 1] * 3 - 2 * D[i - 1] if False else np.nan)
    if not np.isfinite(r_):
        r_ = K[i - 1]  # RSV carries forward via K when H9==L9 or warmup
    K[i] = (2.0 / 3.0) * K[i - 1] + (1.0 / 3.0) * r_
    D[i] = (2.0 / 3.0) * D[i - 1] + (1.0 / 3.0) * K[i]
gold = (K > D) & (np.roll(K, 1) <= np.roll(D, 1)); gold[0] = False
death = (K < D) & (np.roll(K, 1) >= np.roll(D, 1)); death[0] = False

# fractal-5 swings (confirmed 2 bars later)
swing_low = np.zeros(len(c), bool); swing_high = np.zeros(len(c), bool)
for i in range(2, len(c) - 2):
    if lo[i] < lo[i - 1] and lo[i] < lo[i - 2] and lo[i] < lo[i + 1] and lo[i] < lo[i + 2]:
        swing_low[i] = True
    if h[i] > h[i - 1] and h[i] > h[i - 2] and h[i] > h[i + 1] and h[i] > h[i + 2]:
        swing_high[i] = True

sess_arr = b5["sess"].to_numpy()
open5 = b5["open"].to_numpy()
t_end = b5["t_end"].to_numpy()

# 1m arrays per session for stop evaluation
m1s = dict(tuple(m1.groupby("sess")))

sess_last_idx = {}
for i, s in enumerate(sess_arr):
    sess_last_idx[s] = i  # last 5m bar index of each session


def run_arm(ma):
    trades = []
    i = 121
    n = len(c)
    while i < n - 1:
        sig = 0
        if np.isfinite(ma[i]):
            if c[i] > ma[i] and gold[i]:
                sig = 1
            elif c[i] < ma[i] and death[i]:
                sig = -1
        if sig == 0:
            i += 1
            continue
        s = sess_arr[i]
        last_i = sess_last_idx[s]
        # no entries in the last 30 min of the session (last 6 5m bars)
        if i + 1 > last_i - 6 or sess_arr[i + 1] != s:
            i += 1
            continue
        ei = i + 1
        entry = open5[ei] + sig * TICK
        stop_lvl = entry - sig * STOP_PTS
        # 1m stop scan + 5m ladder scan until exit
        mm = m1s[s]
        mm_t = mm["time"].to_numpy(); mm_o = mm["open"].to_numpy()
        mm_h = mm["high"].to_numpy(); mm_l = mm["low"].to_numpy()
        start_t = t_end[ei - 1]  # entry at open of bar ei => after end of bar ei-1
        j0 = int(np.searchsorted(mm_t, start_t, side="left"))
        # ladder state: confirmed swings after entry
        exit_i5 = last_i  # default: session close at last 5m bar close
        exit_px = c[last_i] - sig * TICK
        exit_kind = "close"
        # find ladder exit on 5m
        prev_sw = None
        k5 = ei
        ladder_exit_bar = None
        while k5 + 2 <= last_i:
            # swing at bar k5 confirmed at k5+2
            if sig == 1 and swing_low[k5]:
                if prev_sw is not None and lo[k5] < prev_sw:
                    ladder_exit_bar = k5 + 2 + 1  # exit next 5m open after confirm
                    break
                prev_sw = lo[k5]
            if sig == -1 and swing_high[k5]:
                if prev_sw is not None and h[k5] > prev_sw:
                    ladder_exit_bar = k5 + 2 + 1
                    break
                prev_sw = h[k5]
            k5 += 1
        if ladder_exit_bar is not None and ladder_exit_bar <= last_i and sess_arr[ladder_exit_bar] == s:
            exit_i5 = ladder_exit_bar
            exit_px = open5[ladder_exit_bar] - sig * TICK
            exit_kind = "ladder"
        ladder_t = t_end[exit_i5 - 1] if exit_kind == "ladder" else t_end[last_i]
        # stop scan on 1m up to the ladder/close exit time
        j1 = int(np.searchsorted(mm_t, ladder_t, side="right"))
        stopped = False
        for j in range(j0, min(j1, len(mm_t))):
            if sig == 1 and mm_l[j] < stop_lvl:
                px = min(mm_o[j], stop_lvl) - TICK
                exit_px, exit_kind, stopped = px, "stop", True
                exit_t = mm_t[j]
                break
            if sig == -1 and mm_h[j] > stop_lvl:
                px = max(mm_o[j], stop_lvl) + TICK
                exit_px, exit_kind, stopped = px, "stop", True
                exit_t = mm_t[j]
                break
        pnl = sig * (exit_px - entry) * PV - COMM
        trades.append({"sess": s, "side": sig, "entry_t": str(t_end[ei - 1]),
                       "pnl": pnl, "kind": exit_kind})
        # resume scanning after the exit bar
        if exit_kind == "stop":
            nx = int(np.searchsorted(t_end, exit_t, side="left"))
            i = max(nx, ei) + 1
        else:
            i = exit_i5 + 1
    return pd.DataFrame(trades)


print("[KDJMA01] running primary arm MA120 ...", flush=True)
A = run_arm(ma120)
print(f"[KDJMA01] trades: {len(A)}", flush=True)


def boot_iid(x, seed):
    rng = np.random.default_rng(seed)
    xn = np.asarray(x); m = np.empty(NB)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_yearblock(pnl, years, seed):
    groups = [pnl[years == y].to_numpy() for y in sorted(set(years))]
    rng = np.random.default_rng(seed)
    m = np.empty(NB); ng = len(groups)
    for k in range(NB):
        pick = rng.integers(0, ng, ng)
        m[k] = np.concatenate([groups[p] for p in pick]).mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


yr = pd.to_datetime(A["sess"]).dt.year
res = {"seed": SEED, "spec_commit": "0df8a1b"}
res["G1_N"] = int(len(A)); res["G1_pass"] = len(A) >= 5000
res["net_total"] = float(A.pnl.sum()); res["net_per_trade"] = float(A.pnl.mean())
res["gross_per_trade"] = float(A.pnl.mean() + COMM + 2 * TICK * PV)
res["trades_per_day"] = float(len(A) / A.sess.nunique())
res["win_rate"] = float((A.pnl > 0).mean())
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
res["G7_pass"] = bool(res["G7_top1pct_share"] <= 0.5
                      and float(srt.iloc[0] / absnet) <= 0.25
                      and float(abs(srt.iloc[-1]) / absnet) <= 0.25)
led = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                               "HTFDIR01_DIRECTIONAL_TILT", "out", "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
daily = A.groupby("sess").pnl.sum()
daily.index = pd.to_datetime(daily.index)
j = pd.DataFrame({"kdj": daily, "solar": led["B_SYM"]}).dropna()
losing = j[j.solar < 0]
res["G8_corr_losing"] = float(losing.kdj.corr(losing.solar)) if len(losing) > 10 else None
res["G8_net_on_solar_losing"] = float(losing.kdj.sum())
res["G8_pass"] = bool(((res["G8_corr_losing"] is None) or (res["G8_corr_losing"] <= 0.25))
                      and res["G8_net_on_solar_losing"] > -100_000)
stress = A.pnl + COMM + 2 * TICK * PV - 3 * COMM - 2 * 2 * TICK * PV
slo, shi = boot_iid(stress, SEED + 3)
res["G9_stress_mean"] = float(stress.mean()); res["G9_ci_iid"] = [slo, shi]
res["G9_pass"] = bool(stress.sum() > 0 and slo > 0)
res["by_kind"] = {k: {"n": int(g.pnl.count()), "mean": float(g.pnl.mean())}
                  for k, g in A.groupby("kind")}
res["by_side"] = {str(s): {"n": int(g.pnl.count()), "mean": float(g.pnl.mean())}
                  for s, g in A.groupby("side")}
res["per_year_net"] = {str(y): float(A.loc[yr == y, "pnl"].sum()) for y in sorted(set(yr))}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates))

A.to_csv(os.path.join(OUT, "kdjma01_trades.csv"), index=False)
with open(os.path.join(OUT, "kdjma01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
