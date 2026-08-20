#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BREADTH01 -- 01_breadth01.py
Runs the FROZEN SPEC.md (commit f0bd917). MOP-2012 verbatim TSMOM on the 15-ETF universe.
Analysis mask <= 2026-05-31. No parameter may deviate from spec.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "breadth_lab", "BREADTH01_TSMOM_REPLICATION")
DATA = os.path.join(RUN, "data")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED, NB = 20260819, 10_000
MASK_END = pd.Timestamp("2026-05-31")
COST_SIDE = 0.0005  # 5 bps per side of traded notional
UNIVERSE = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD", "SLV", "USO", "UNG",
            "DBC", "FXE", "FXY", "UUP"]


def load(sym):
    df = pd.read_parquet(os.path.join(DATA, sym.replace("^", "_") + ".parquet"))
    df["date"] = pd.to_datetime(df["date"])
    df = df[df.date <= MASK_END].set_index("date")
    return df


# rf: official 13-week bill coupon-equivalent (disclosed substitute for ^IRX, see MANIFEST)
rf_df = pd.read_parquet(os.path.join(DATA, "_RF_TREAS13W.parquet"))
rf_df["date"] = pd.to_datetime(rf_df["date"])
rf_df = rf_df[rf_df.date <= MASK_END].set_index("date")
rf_series = rf_df["rate"] / 100.0 / 252.0
px = pd.DataFrame({s: load(s)["adjclose"] for s in UNIVERSE}).sort_index()
px = px[px.index >= rf_series.index[0]]  # book clipped to rf coverage (2002-01)
ret = px.pct_change()
rf = rf_series.reindex(ret.index).ffill().fillna(0.0)
exret = ret.sub(rf, axis=0)

# ex-ante vol: EWMA(com=60) of daily returns, annualized, as of each day
ewvar = ret.pow(2).ewm(com=60, min_periods=30).mean()
sigma_ann = np.sqrt(ewvar * 252)

# monthly signal dates = last trading day of month per the pooled calendar
cal = ret.index
month_key = cal.to_period("M")
sig_dates = pd.Series(cal, index=cal).groupby(month_key).max()

# build daily position matrix
pos = pd.DataFrame(0.0, index=cal, columns=UNIVERSE)
for i, sd in enumerate(sig_dates.values):
    sd = pd.Timestamp(sd)
    # effective from close of FIRST trading day of next month -> returns accrue from day after
    nxt = cal[cal > sd]
    if len(nxt) == 0:
        continue
    eff_start = nxt[0]  # position effective at this day's close
    end = sig_dates.values[i + 1] if i + 1 < len(sig_dates) else cal[-1]
    # window over which this month's position earns returns: (eff_start, next eff_start]
    nxt2 = cal[cal > pd.Timestamp(end)]
    eff_end = nxt2[0] if len(nxt2) else cal[-1]
    for s in UNIVERSE:
        hist = px[s].loc[:sd].dropna()
        if len(hist) < 253:
            continue
        r12 = hist.iloc[-1] / hist.iloc[-253] - 1.0
        r12 = r12 - (rf.loc[hist.index[-253]:sd].sum())  # excess 12m
        sig = np.sign(r12)
        if sig == 0:
            continue
        vol = sigma_ann[s].loc[:sd].dropna()
        if not len(vol) or vol.iloc[-1] <= 0:
            continue
        w = float(np.clip(0.10 / vol.iloc[-1], -4.0, 4.0)) * sig
        mask = (cal > eff_start) & (cal <= eff_end)
        pos.loc[mask, s] = w

live = pos.abs().gt(0)
n_live = live.sum(axis=1)
stream = pos * exret
book_gross = stream.sum(axis=1) / n_live.replace(0, np.nan)
turn = pos.diff().abs().sum(axis=1) / n_live.replace(0, np.nan)
book_net = (book_gross - turn * COST_SIDE).dropna()
book_net = book_net[n_live.reindex(book_net.index) >= 3]


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


def gate_battery(bk, label, seed):
    res = {"label": label, "n_days": int(len(bk)),
           "first": str(bk.index[0].date()), "last": str(bk.index[-1].date()),
           "ann_ret": float(bk.mean() * 252), "ann_vol": float(bk.std(ddof=1) * np.sqrt(252)),
           "sharpe": sharpe(bk)}
    ylo, yhi = year_block_ci(bk, seed)
    res["G2_ci_yearblock_annret"] = [ylo, yhi]
    res["G2_pass"] = bool(res["ann_ret"] > 0 and ylo > 0)
    pre, post = bk[bk.index < "2020-01-01"], bk[bk.index >= "2020-01-01"]
    plo, phi = iid_ci(pre, seed + 1); qlo, qhi = iid_ci(post, seed + 2)
    res["G3_pre2020"] = {"mean_ann": float(pre.mean() * 252), "ci": [plo, phi]}
    res["G3_post2020"] = {"mean_ann": float(post.mean() * 252), "ci": [qlo, qhi]}
    res["G3_pass"] = bool(pre.mean() > 0 and post.mean() > 0
                          and (plo > 0 or qlo > 0) and not (phi < 0) and not (qhi < 0))
    mid = bk.index[len(bk) // 2]
    h1, h2 = bk[bk.index <= mid], bk[bk.index > mid]
    res["G4_halves_sharpe"] = [sharpe(h1), sharpe(h2)]
    res["G4_pass"] = bool(np.sign(sharpe(h1)) == np.sign(sharpe(h2)))
    res["per_year"] = {str(y): float(bk[bk.index.year == y].sum()) for y in sorted(set(bk.index.year))}
    return res


def solar_ledger():
    h = pd.read_csv(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out", "e10_daily_hist.csv"),
                    index_col=0, parse_dates=True)
    d = pd.read_csv(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "e10_daily_py.csv"),
                    index_col=0, parse_dates=True)
    hcol = h.columns[0] if h.shape[1] == 1 else [c for c in h.columns if "net" in c.lower() or "pnl" in c.lower() or "e10" in c.lower()][0]
    dcol = d.columns[0] if d.shape[1] == 1 else [c for c in d.columns if "net" in c.lower() or "pnl" in c.lower() or "e10" in c.lower()][0]
    s = pd.concat([h[hcol], d[dcol]])
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s


def g5_g6(bk, seed):
    sol = solar_ledger()
    j = pd.DataFrame({"tsmom": bk, "solar": sol}).dropna()
    out = {"overlap_days": int(len(j)),
           "rho_full": float(j.tsmom.corr(j.solar))}
    losing = j[j.solar < 0]
    out["rho_losing"] = float(losing.tsmom.corr(losing.solar))
    out["tsmom_ret_on_solar_losing_ann"] = float(losing.tsmom.mean() * 252)
    out["G5_pass"] = bool(out["rho_full"] <= 0.25 and out["rho_losing"] <= 0.25
                          and losing.tsmom.mean() >= 0)
    # G6: 50/50 risk blend on overlap
    sv, tv = j.solar.std(ddof=1), j.tsmom.std(ddof=1)
    blend = 0.5 * j.solar / sv + 0.5 * j.tsmom / tv
    sol_n = j.solar / sv
    def cdar5(x):
        eq = x.cumsum(); dd = eq.cummax() - eq
        k = max(1, int(0.05 * len(x)))
        return float(np.sort(dd.to_numpy())[::-1][:k].mean())
    out["G6"] = {"sharpe_solar_alone": sharpe(j.solar), "sharpe_blend": sharpe(blend),
                 "cdar5_solar_alone_volunits": cdar5(sol_n), "cdar5_blend_volunits": cdar5(blend),
                 "maxdd_solar_volunits": float((sol_n.cumsum().cummax() - sol_n.cumsum()).max()),
                 "maxdd_blend_volunits": float((blend.cumsum().cummax() - blend.cumsum()).max())}
    out["G6_pass"] = bool(out["G6"]["sharpe_blend"] > out["G6"]["sharpe_solar_alone"]
                          and out["G6"]["cdar5_blend_volunits"] <= out["G6"]["cdar5_solar_alone_volunits"] * 1.02)
    return out


res = {"seed": SEED, "spec_commit": "f0bd917", "cost_per_side": COST_SIDE}
usable = [s for s in UNIVERSE if (px[s].dropna().index[-1] - px[s].dropna().index[0]).days >= 15 * 365]
res["G1_assets_ge15y"] = len(usable)
res["G1_book_years"] = float((book_net.index[-1] - book_net.index[0]).days / 365.25)
res["G1_pass"] = bool(len(usable) >= 10 and res["G1_book_years"] >= 18)

res["ARM_FULL"] = gate_battery(book_net, "ARM_FULL", SEED)
res["ARM_FULL_G5G6"] = g5_g6(book_net, SEED)

# stress 3x costs
book_stress = (book_gross - turn * COST_SIDE * 3).dropna()
book_stress = book_stress[n_live.reindex(book_stress.index) >= 3]
st = gate_battery(book_stress, "ARM_FULL_STRESS3X", SEED + 10)
res["G7_stress"] = {"G2_pass": st["G2_pass"], "G3_pass": st["G3_pass"],
                    "sharpe": st["sharpe"], "ann_ret": st["ann_ret"],
                    "ci_yearblock": st["G2_ci_yearblock_annret"]}
res["G7_pass"] = bool(st["G2_pass"] and st["G3_pass"])

# ARM_EXUSEQ
ex = [s for s in UNIVERSE if s not in ("SPY", "QQQ", "IWM")]
stream_ex = pos[ex] * exret[ex]
live_ex = pos[ex].abs().gt(0); nlx = live_ex.sum(axis=1)
bg_ex = stream_ex.sum(axis=1) / nlx.replace(0, np.nan)
tn_ex = pos[ex].diff().abs().sum(axis=1) / nlx.replace(0, np.nan)
bn_ex = (bg_ex - tn_ex * COST_SIDE).dropna()
bn_ex = bn_ex[nlx.reindex(bn_ex.index) >= 3]
res["ARM_EXUSEQ"] = gate_battery(bn_ex, "ARM_EXUSEQ", SEED + 20)
res["ARM_EXUSEQ_G5G6"] = g5_g6(bn_ex, SEED + 20)

# stream-level disclosure
res["stream_sharpes"] = {s: (sharpe((pos[s] * exret[s]).dropna())
                             if (pos[s].abs() > 0).sum() > 500 else None) for s in UNIVERSE}
res["mean_monthly_turnover_frac"] = float(turn.replace([np.inf], np.nan).dropna().mean() * 21)

full_gates = [res["G1_pass"], res["ARM_FULL"]["G2_pass"], res["ARM_FULL"]["G3_pass"],
              res["ARM_FULL"]["G4_pass"], res["ARM_FULL_G5G6"]["G5_pass"],
              res["ARM_FULL_G5G6"]["G6_pass"], res["G7_pass"]]
res["ARM_FULL_ALL_PASS"] = bool(all(full_gates))

book_net.to_frame("book_net").to_csv(os.path.join(OUT, "book_daily_full.csv"))
bn_ex.to_frame("book_net").to_csv(os.path.join(OUT, "book_daily_exuseq.csv"))
with open(os.path.join(OUT, "breadth01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
