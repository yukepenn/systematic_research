#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BREADTH03 -- 01_breadth03.py
Runs the FROZEN SPEC.md (commit c5266a8). Downloads VIXY/^VIX/^VIX3M/SVXY (manifest),
then executes the Simon-Campasano contango-conditional short-VIXY rule. Mask <= 2026-05-31.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import time
import urllib.request

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "breadth_lab", "BREADTH03_VRP")
DATA = os.path.join(RUN, "data")
OUT = os.path.join(RUN, "out")
os.makedirs(DATA, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

SEED, NB = 20260819, 10_000
MASK_END = pd.Timestamp("2026-05-31")
COST_SIDE = 0.0005
BORROW = 0.05 / 252.0
BORROW_STRESS = 0.10 / 252.0


def fetch(sym):
    p2 = int(time.time())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}"
           f"?period1=631152000&period2={p2}&interval=1d&events=div%2Csplit")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    j = json.loads(urllib.request.urlopen(req, timeout=30).read())
    r = j["chart"]["result"][0]
    ts = r["timestamp"]; q = r["indicators"]["quote"][0]
    adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    df = pd.DataFrame({"date": [datetime.datetime.utcfromtimestamp(t).date() for t in ts],
                       "close": q["close"], "adjclose": adj})
    return df.dropna(subset=["adjclose"]).drop_duplicates("date").sort_values("date")


manifest = []
for s in ["VIXY", "^VIX", "^VIX3M", "SVXY"]:
    fn = s.replace("^", "_") + ".parquet"
    if os.path.exists(os.path.join(DATA, fn)):  # idempotent: keep verified downloads
        print(s, "exists, skipping", flush=True)
        continue
    df = fetch(s)
    df.to_parquet(os.path.join(DATA, fn), index=False)
    h = hashlib.sha256(open(os.path.join(DATA, fn), "rb").read()).hexdigest()[:16]
    manifest.append({"symbol": s, "file": fn, "rows": len(df), "first": str(df.date.iloc[0]),
                     "last": str(df.date.iloc[-1]), "sha256_16": h, "source": "Yahoo v8 chart"})
    print(s, len(df), df.date.iloc[0], "->", df.date.iloc[-1], flush=True)
    time.sleep(0.5)
if manifest:
    json.dump(manifest, open(os.path.join(DATA, "MANIFEST.json"), "w"), indent=1)


def load(fn):
    df = pd.read_parquet(os.path.join(DATA, fn))
    df["date"] = pd.to_datetime(df["date"])
    return df[df.date <= MASK_END].set_index("date")


vixy = load("VIXY.parquet")["adjclose"]
vix = load("_VIX.parquet")["close"]
vix3m = load("_VIX3M.parquet")["close"]
ret = vixy.pct_change()
cal = ret.index
sigma_ann = np.sqrt(ret.pow(2).ewm(com=60, min_periods=30).mean() * 252)

sig_dates = pd.Series(cal, index=cal).groupby(cal.to_period("M")).max()
pos = pd.Series(0.0, index=cal)
for i, sd in enumerate(sig_dates.values):
    sd = pd.Timestamp(sd)
    nxt = cal[cal > sd]
    if not len(nxt):
        continue
    eff_start = nxt[0]
    end = sig_dates.values[i + 1] if i + 1 < len(sig_dates) else cal[-1]
    nxt2 = cal[cal > pd.Timestamp(end)]
    eff_end = nxt2[0] if len(nxt2) else cal[-1]
    v = vix.reindex([sd], method="ffill").iloc[0]
    v3 = vix3m.reindex([sd], method="ffill").iloc[0]
    if not (np.isfinite(v) and np.isfinite(v3)):
        continue
    if v3 > v:  # contango -> short VIXY
        vol = sigma_ann.loc[:sd].dropna()
        if len(vol) and vol.iloc[-1] > 0:
            w = -float(np.clip(0.10 / vol.iloc[-1], 0, 4.0))
            pos.loc[(cal > eff_start) & (cal <= eff_end)] = w

gross = pos * ret
turn = pos.diff().abs()
book = (gross - turn * COST_SIDE - pos.abs() * BORROW).dropna()
book = book[book.index >= pos[pos != 0].index[0]] if (pos != 0).any() else book
book_stress = (gross - turn * COST_SIDE * 3 - pos.abs() * BORROW_STRESS).dropna()
book_stress = book_stress.reindex(book.index)


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


res = {"seed": SEED, "spec_commit": "c5266a8"}
res["G1_book_years"] = float((book.index[-1] - book.index[0]).days / 365.25)
res["G1_pass"] = bool(res["G1_book_years"] >= 15)
res["ann_ret"] = float(book.mean() * 252); res["ann_vol"] = float(book.std(ddof=1) * np.sqrt(252))
res["sharpe"] = sharpe(book)
ylo, yhi = year_block_ci(book, SEED)
res["G2_ci_yearblock"] = [ylo, yhi]
res["G2_pass"] = bool(res["ann_ret"] > 0 and ylo > 0)

pre, post = book[book.index < "2020-01-01"], book[book.index >= "2020-01-01"]
plo, phi = iid_ci(pre, SEED + 1); qlo, qhi = iid_ci(post, SEED + 2)
mid = book.index[len(book) // 2]
h1, h2 = book[book.index <= mid], book[book.index > mid]
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
    s = pd.concat([h[h.columns[0]], d[d.columns[0]]])
    return s[~s.index.duplicated(keep="last")].sort_index()


sol = solar_ledger()
j = pd.DataFrame({"vrp": book, "solar": sol}).dropna()
losing = j[j.solar < 0]
res["G5_raw"] = {"overlap_days": int(len(j)), "rho_full": float(j.vrp.corr(j.solar)),
                 "rho_losing": float(losing.vrp.corr(losing.solar)),
                 "vrp_on_solar_losing_ann": float(losing.vrp.mean() * 252)}
# era-wise normalized Solar
sol_n = sol.copy().astype(float)
m_hist = sol_n.index <= "2021-12-31"
sol_n[m_hist] = sol_n[m_hist] / sol_n[m_hist].std(ddof=1)
sol_n[~m_hist] = sol_n[~m_hist] / sol_n[~m_hist].std(ddof=1)
j2 = pd.DataFrame({"vrp": book, "solar": sol_n}).dropna()
lo2 = j2[j2.solar < 0]
res["G5_erawise"] = {"rho_full": float(j2.vrp.corr(j2.solar)),
                     "rho_losing": float(lo2.vrp.corr(lo2.solar)),
                     "vrp_on_solar_losing_ann": float(lo2.vrp.mean() * 252)}
res["G5_pass"] = bool(
    res["G5_raw"]["rho_full"] <= 0.25 and res["G5_raw"]["rho_losing"] <= 0.25
    and losing.vrp.mean() >= 0
    and res["G5_erawise"]["rho_full"] <= 0.25 and res["G5_erawise"]["rho_losing"] <= 0.25
    and lo2.vrp.mean() >= 0)

sv, vv = j.solar.std(ddof=1), j.vrp.std(ddof=1)
blend = 0.5 * j.solar / sv + 0.5 * j.vrp / vv
soln = j.solar / sv


def cdar5(x):
    eq = x.cumsum(); dd = eq.cummax() - eq
    k = max(1, int(0.05 * len(x)))
    return float(np.sort(dd.to_numpy())[::-1][:k].mean())


dev = j.index >= "2022-01-01"
sv_d, vv_d = j.solar[dev].std(ddof=1), j.vrp[dev].std(ddof=1)
blend_d = 0.5 * j.solar[dev] / sv_d + 0.5 * j.vrp[dev] / vv_d
soln_d = j.solar[dev] / sv_d
res["G6"] = {"sharpe_solar_alone": sharpe(j.solar), "sharpe_blend": sharpe(blend),
             "dev_cdar5_solar": cdar5(soln_d), "dev_cdar5_blend": cdar5(blend_d),
             "dev_sharpe_solar": sharpe(j.solar[dev]), "dev_sharpe_blend": sharpe(blend_d)}
res["G6_pass"] = bool(res["G6"]["sharpe_blend"] > res["G6"]["sharpe_solar_alone"]
                      and res["G6"]["dev_cdar5_blend"] <= res["G6"]["dev_cdar5_solar"] * 1.02)

slo, shi = year_block_ci(book_stress.dropna(), SEED + 10)
res["G7_stress"] = {"ann_ret": float(book_stress.mean() * 252), "ci": [slo, shi]}
res["G7_pass"] = bool(book_stress.mean() > 0 and slo > 0)

res["pct_months_contango"] = float((pos[pos != 0].groupby(pos[pos != 0].index.to_period("M")).size() > 0).sum()
                                   / len(sig_dates))
res["episodes"] = {"feb2018": float(book.loc["2018-02-01":"2018-02-28"].sum()),
                   "mar2020": float(book.loc["2020-03-01":"2020-03-31"].sum())}
res["worst_month"] = float(book.groupby(book.index.to_period("M")).sum().min())
res["best_month"] = float(book.groupby(book.index.to_period("M")).sum().max())
res["skew_daily"] = float(book.skew())
res["per_year"] = {str(y): float(book[book.index.year == y].sum()) for y in sorted(set(book.index.year))}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates))

book.to_frame("book_net").to_csv(os.path.join(OUT, "book_daily_vrp.csv"))
with open(os.path.join(OUT, "breadth03_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
