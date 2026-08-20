#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BREADTH02 -- 01_breadth02.py
Runs the FROZEN SPEC.md (commit dd8f08e). Bond slope carry + equity div-yield carry.
Sizing/execution/costs reused verbatim from BREADTH01. Analysis mask <= 2026-05-31.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "breadth_lab", "BREADTH02_CARRY")
B1DATA = os.path.join(ROOT, "research", "breadth_lab", "BREADTH01_TSMOM_REPLICATION", "data")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED, NB = 20260819, 10_000
MASK_END = pd.Timestamp("2026-05-31")
COST_SIDE = 0.0005
BOND = ["TLT", "IEF"]
EQ = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
UNIVERSE = BOND + EQ


def load_px(sym, col="adjclose"):
    df = pd.read_parquet(os.path.join(B1DATA, sym + ".parquet"))
    df["date"] = pd.to_datetime(df["date"])
    return df[df.date <= MASK_END].set_index("date")


curve = pd.read_parquet(os.path.join(RUN, "data", "treasury_curve.parquet"))
curve["Date"] = pd.to_datetime(curve["Date"])
curve = curve[curve.Date <= MASK_END].set_index("Date").sort_index()
slope = (curve["10 Yr"] - curve["3 Mo"]).dropna()

rf_df = pd.read_parquet(os.path.join(B1DATA, "_RF_TREAS13W.parquet"))
rf_df["date"] = pd.to_datetime(rf_df["date"])
rf_df = rf_df[rf_df.date <= MASK_END].set_index("date")
rf_ann = rf_df["rate"] / 100.0
rf_daily = rf_ann / 252.0

adj = pd.DataFrame({s: load_px(s)["adjclose"] for s in UNIVERSE}).sort_index()
cls = pd.DataFrame({s: load_px(s)["close"] for s in UNIVERSE}).sort_index()
adj = adj[adj.index >= rf_df.index[0]]
cls = cls.reindex(adj.index)
ret = adj.pct_change()
pxret = cls.pct_change()
rf = rf_daily.reindex(ret.index).ffill().fillna(0.0)
exret = ret.sub(rf, axis=0)

ewvar = ret.pow(2).ewm(com=60, min_periods=30).mean()
sigma_ann = np.sqrt(ewvar * 252)

# trailing-252d realized dividend yield per equity ETF: prod(1+r_adj)/prod(1+r_px) - 1
div12 = ((1 + ret[EQ]).rolling(252).apply(np.prod, raw=True)
         / (1 + pxret[EQ]).rolling(252).apply(np.prod, raw=True) - 1)

cal = ret.index
sig_dates = pd.Series(cal, index=cal).groupby(cal.to_period("M")).max()

pos = pd.DataFrame(0.0, index=cal, columns=UNIVERSE)
for i, sd in enumerate(sig_dates.values):
    sd = pd.Timestamp(sd)
    nxt = cal[cal > sd]
    if len(nxt) == 0:
        continue
    eff_start = nxt[0]
    end = sig_dates.values[i + 1] if i + 1 < len(sig_dates) else cal[-1]
    nxt2 = cal[cal > pd.Timestamp(end)]
    eff_end = nxt2[0] if len(nxt2) else cal[-1]
    mask = (cal > eff_start) & (cal <= eff_end)
    # bond sleeve: sign of curve slope at sd (last available <= sd); half weight each ETF
    sl = slope.loc[:sd]
    if len(sl):
        bsig = np.sign(sl.iloc[-1])
        for s in BOND:
            vol = sigma_ann[s].loc[:sd].dropna()
            hist = adj[s].loc[:sd].dropna()
            if bsig != 0 and len(vol) and vol.iloc[-1] > 0 and len(hist) > 252:
                pos.loc[mask, s] = 0.5 * bsig * float(np.clip(0.10 / vol.iloc[-1], -4, 4))
    # equity sleeve: sign(div12 - rf_ann) at sd
    rf_now = rf_ann.reindex([sd], method="ffill").iloc[0]
    for s in EQ:
        d12 = div12[s].loc[:sd].dropna()
        vol = sigma_ann[s].loc[:sd].dropna()
        if len(d12) and len(vol) and vol.iloc[-1] > 0:
            esig = np.sign(d12.iloc[-1] - rf_now)
            if esig != 0:
                pos.loc[mask, s] = esig * float(np.clip(0.10 / vol.iloc[-1], -4, 4))

# bond sleeve counts as ONE bet (already half-weighted); live-stream count for averaging:
live_eq = pos[EQ].abs().gt(0).sum(axis=1)
live_bond = (pos[BOND].abs().sum(axis=1) > 0).astype(int)  # 1 if bond bet on
n_live = live_eq + live_bond
stream = pos * exret
book_gross = stream.sum(axis=1) / n_live.replace(0, np.nan)
turn = pos.diff().abs().sum(axis=1) / n_live.replace(0, np.nan)
book_net = (book_gross - turn * COST_SIDE).dropna()
book_net = book_net[n_live.reindex(book_net.index) >= 2]


def sharpe(x):
    return float(x.mean() / x.std(ddof=1) * np.sqrt(252))


def year_block_ci(x, seed):
    yr = x.index.year
    groups = [x[yr == y].to_numpy() for y in sorted(set(yr))]
    rng = np.random.default_rng(seed)
    m = np.empty(NB); ng = len(groups)
    for k in range(NB):
        pick = rng.integers(0, ng, ng)
        m[k] = np.concatenate([groups[p] for p in pick]).mean()
    return float(np.percentile(m, 2.5) * 252), float(np.percentile(m, 97.5) * 252)


def iid_ci(x, seed):
    rng = np.random.default_rng(seed)
    xn = x.to_numpy(); m = np.empty(NB)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5) * 252), float(np.percentile(m, 97.5) * 252)


res = {"seed": SEED, "spec_commit": "dd8f08e"}
res["G1_book_years"] = float((book_net.index[-1] - book_net.index[0]).days / 365.25)
sleeve_bond = (pos[BOND] * exret[BOND]).sum(axis=1)
sleeve_eq = (pos[EQ] * exret[EQ]).sum(axis=1) / live_eq.replace(0, np.nan)
res["G1_pass"] = bool(res["G1_book_years"] >= 18)

res["ann_ret"] = float(book_net.mean() * 252)
res["ann_vol"] = float(book_net.std(ddof=1) * np.sqrt(252))
res["sharpe"] = sharpe(book_net)
ylo, yhi = year_block_ci(book_net, SEED)
res["G2_ci_yearblock"] = [ylo, yhi]
res["G2_pass"] = bool(res["ann_ret"] > 0 and ylo > 0)

pre, post = book_net[book_net.index < "2020-01-01"], book_net[book_net.index >= "2020-01-01"]
plo, phi = iid_ci(pre, SEED + 1); qlo, qhi = iid_ci(post, SEED + 2)
mid = book_net.index[len(book_net) // 2]
h1, h2 = book_net[book_net.index <= mid], book_net[book_net.index > mid]
res["G3_era"] = {"pre_mean_ann": float(pre.mean() * 252), "pre_ci": [plo, phi],
                 "post_mean_ann": float(post.mean() * 252), "post_ci": [qlo, qhi],
                 "halves_sharpe": [sharpe(h1), sharpe(h2)]}
res["G3_pass"] = bool(pre.mean() > 0 and post.mean() > 0
                      and np.sign(sharpe(h1)) == np.sign(sharpe(h2))
                      and not (phi < 0) and not (qhi < 0))


def solar_ledger():
    h = pd.read_csv(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out", "e10_daily_hist.csv"),
                    index_col=0, parse_dates=True)
    d = pd.read_csv(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "e10_daily_py.csv"),
                    index_col=0, parse_dates=True)
    hcol = h.columns[0]; dcol = d.columns[0]
    s = pd.concat([h[hcol], d[dcol]])
    return s[~s.index.duplicated(keep="last")].sort_index()


sol = solar_ledger()
j = pd.DataFrame({"carry": book_net, "solar": sol}).dropna()
losing = j[j.solar < 0]
res["G5"] = {"overlap_days": int(len(j)), "rho_full": float(j.carry.corr(j.solar)),
             "rho_losing": float(losing.carry.corr(losing.solar)),
             "carry_on_solar_losing_ann": float(losing.carry.mean() * 252)}
res["G5_pass"] = bool(res["G5"]["rho_full"] <= 0.25 and res["G5"]["rho_losing"] <= 0.25
                      and losing.carry.mean() >= 0)

sv, cv = j.solar.std(ddof=1), j.carry.std(ddof=1)
blend = 0.5 * j.solar / sv + 0.5 * j.carry / cv
sol_n = j.solar / sv


def cdar5(x):
    eq = x.cumsum(); dd = eq.cummax() - eq
    k = max(1, int(0.05 * len(x)))
    return float(np.sort(dd.to_numpy())[::-1][:k].mean())


res["G6"] = {"sharpe_solar_alone": sharpe(j.solar), "sharpe_blend": sharpe(blend),
             "cdar5_solar": cdar5(sol_n), "cdar5_blend": cdar5(blend)}
res["G6_pass"] = bool(res["G6"]["sharpe_blend"] > res["G6"]["sharpe_solar_alone"]
                      and res["G6"]["cdar5_blend"] <= res["G6"]["cdar5_solar"] * 1.02)

book_stress = (book_gross - turn * COST_SIDE * 3).dropna()
book_stress = book_stress[n_live.reindex(book_stress.index) >= 2]
slo, shi = year_block_ci(book_stress, SEED + 10)
res["G7_stress"] = {"ann_ret": float(book_stress.mean() * 252), "ci": [slo, shi]}
res["G7_pass"] = bool(book_stress.mean() > 0 and slo > 0)

res["sleeve_sharpes"] = {"bond": sharpe(sleeve_bond.dropna()),
                         "equity": sharpe(sleeve_eq.dropna())}
res["sleeve_corr"] = float(sleeve_bond.corr(sleeve_eq))
b1 = pd.read_csv(os.path.join(ROOT, "research", "breadth_lab", "BREADTH01_TSMOM_REPLICATION",
                              "out", "book_daily_full.csv"), index_col=0, parse_dates=True)["book_net"]
jj = pd.DataFrame({"carry": book_net, "tsmom": b1}).dropna()
res["corr_vs_closed_tsmom_book"] = float(jj.carry.corr(jj.tsmom))
res["per_year"] = {str(y): float(book_net[book_net.index.year == y].sum())
                   for y in sorted(set(book_net.index.year))}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates))

book_net.to_frame("book_net").to_csv(os.path.join(OUT, "book_daily_carry.csv"))
with open(os.path.join(OUT, "breadth02_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
