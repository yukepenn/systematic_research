#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIQREV01 -- 01_liqrev01.py
Runs the FROZEN SPEC.md (committed 9775c0a BEFORE this executed). Stress-gated daily
liquidity-provision reversal on the 20-year NQ minute substrate. All constants from the spec;
nothing tuned here. Run from repo root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "research", "system_master", "LIQREV01_STRESS_REVERSAL", "out")
os.makedirs(OUT, exist_ok=True)

SEED = 20260819
NB = 10_000
TICK = 0.25
PV = 20.0
COMM_SIDE = 2.18
RT_COST = 2 * COMM_SIDE          # commission per round turn
STRESS_PCT = 0.90
QLO, QHI = 0.20, 0.80
VOL_WIN, PCT_WIN, RET_WIN = 5, 252, 63

print("[LIQREV01] loading minute substrate ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
hm = df["time"].dt.hour * 100 + df["time"].dt.minute
rth = df[(hm >= 930) & (hm <= 1558)].copy()

g = rth.groupby("d")
nbars = g.size()
valid_days = nbars[nbars >= 200].index
sess_close = g["close"].last().loc[valid_days]

# per-day realized variance from 1-min point returns (within RTH)
def day_rv2(sub):
    r = sub["close"].diff().dropna()
    return float((r * r).sum())

rv2 = g.apply(day_rv2, include_groups=False).loc[valid_days]

D = pd.DataFrame({"close": sess_close, "rv2": rv2}).sort_index()
D.index = pd.to_datetime(pd.Index(D.index))
D["ret"] = D["close"].diff()
D["rv5"] = np.sqrt(D["rv2"].rolling(VOL_WIN).sum())

# trailing-252 percentile rank of rv5 (window ends at d, inclusive)
rv5 = D["rv5"].to_numpy()
n = len(D)
pct = np.full(n, np.nan)
for i in range(PCT_WIN - 1, n):
    w = rv5[i - PCT_WIN + 1:i + 1]
    if np.isnan(w).any():
        continue
    pct[i] = (w <= rv5[i]).mean()
D["rv5_pct"] = pct

# prior-63-session quantile thresholds (shift 1)
D["q20"] = D["ret"].rolling(RET_WIN).quantile(QLO).shift(1)
D["q80"] = D["ret"].rolling(RET_WIN).quantile(QHI).shift(1)

# overnight-gap roll flag (W10 convention, |z|>6 vs trailing 120 shift(1))
gap = D["close"].diff()  # close-to-close in points == ret; overnight component not separable at
# daily grain -- use ret z as the gap proxy per spec's robustness intent
mu = D["ret"].rolling(120, min_periods=40).mean().shift(1)
sd = D["ret"].rolling(120, min_periods=40).std().shift(1)
D["gap_flag"] = ((D["ret"] - mu).abs() / sd) > 6

# release-day set (NFP/CPI 2005-2021 committed + w8bfade 2022+ release rows)
rel = set()
cal = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "data",
                               "hist_calendar_2005_2021.csv"))
rel |= set(pd.to_datetime(cal["date"]).dt.normalize())
try:
    w8 = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "artifacts",
                                  "w8_bfade", "w8bfade_trades.csv"))
    w8r = w8[w8["group"].astype(str).str.lower() != "placebo"]
    rel |= set(pd.to_datetime(w8r["date"]).dt.normalize())
    rel_src = "hist_calendar(2005-2021) + w8bfade release rows (2022+)"
except Exception as e:
    rel_src = f"hist_calendar only (w8bfade load failed: {e})"


def build_trades(stress_pct, qlo, qhi, stress=True, hold=1):
    """Returns trade table. thresholds from prior-window quantiles at (qlo,qhi)."""
    ql = D["ret"].rolling(RET_WIN).quantile(qlo).shift(1)
    qh = D["ret"].rolling(RET_WIN).quantile(qhi).shift(1)
    in_state = (D["rv5_pct"] >= stress_pct) if stress else (D["rv5_pct"] < stress_pct)
    sig_long = in_state & (D["ret"] <= ql)
    sig_short = in_state & (D["ret"] >= qh)
    rows = []
    closes = D["close"].to_numpy()
    idx = D.index
    for i in range(n - hold):
        if not (sig_long.iloc[i] or sig_short.iloc[i]):
            continue
        side = 1 if sig_long.iloc[i] else -1
        entry = closes[i] + side * TICK          # adverse fill
        exitp = closes[i + hold] - side * TICK   # adverse fill
        pnl = side * (exitp - entry) * PV - RT_COST
        rows.append({"entry_date": idx[i], "exit_date": idx[i + hold], "side": side,
                     "pnl": pnl, "gap_flag_window": bool(D["gap_flag"].iloc[i + 1:i + hold + 1].any()),
                     "release_entry": idx[i].normalize() in rel})
    return pd.DataFrame(rows)


def boot_ci_iid(x, seed=SEED):
    rng = np.random.default_rng(seed)
    m = np.empty(NB)
    xn = np.asarray(x)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def episodes_of(trades):
    """maximal runs of stress trades with entry gaps <= 5 sessions"""
    dates = pd.to_datetime(trades["entry_date"]).sort_values().to_numpy()
    sess = {d: i for i, d in enumerate(D.index)}
    eps, cur = [], [0]
    td = trades.sort_values("entry_date").reset_index(drop=True)
    si = td["entry_date"].map(lambda d: sess[d]).to_numpy()
    for j in range(1, len(td)):
        if si[j] - si[j - 1] <= 5:
            cur.append(j)
        else:
            eps.append(cur); cur = [j]
    eps.append(cur)
    return td, eps


def boot_ci_episode(trades, seed=SEED):
    td, eps = episodes_of(trades)
    pnl = td["pnl"].to_numpy()
    ep_arrays = [pnl[e] for e in eps]
    rng = np.random.default_rng(seed)
    m = np.empty(NB)
    ne = len(ep_arrays)
    for k in range(NB):
        pick = rng.integers(0, ne, ne)
        s = np.concatenate([ep_arrays[p] for p in pick])
        m[k] = s.mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), ne


print("[LIQREV01] building primary trades ...", flush=True)
T = build_trades(STRESS_PCT, QLO, QHI, stress=True, hold=1)
res = {"seed": SEED, "n_boot": NB, "release_source": rel_src,
       "n_sessions": int(n), "first_tradable": str(T["entry_date"].min().date()) if len(T) else None}

res["G1_N"] = int(len(T)); res["G1_pass"] = len(T) >= 300
res["net_total"] = float(T["pnl"].sum()); res["net_per_trade"] = float(T["pnl"].mean())
res["n_long"] = int((T["side"] == 1).sum()); res["n_short"] = int((T["side"] == -1).sum())
res["net_long"] = float(T.loc[T["side"] == 1, "pnl"].sum())
res["net_short"] = float(T.loc[T["side"] == -1, "pnl"].sum())

lo_ep, hi_ep, n_ep = boot_ci_episode(T)
lo_iid, hi_iid = boot_ci_iid(T["pnl"])
res["G2_ci_episode"] = [lo_ep, hi_ep]; res["G2_n_episodes"] = n_ep
res["G2_ci_iid"] = [lo_iid, hi_iid]
res["G2_pass"] = lo_ep > 0

clusters = {"2008-09": [2008, 2009], "2010": [2010], "2011": [2011],
            "2015-16": [2015, 2016], "2018": [2018], "2020": [2020], "2022": [2022]}
yr = pd.to_datetime(T["entry_date"]).dt.year
cl = {k: float(T.loc[yr.isin(v), "pnl"].sum()) for k, v in clusters.items()}
res["G3_clusters"] = cl
res["G3_pass"] = sum(v > 0 for v in cl.values()) >= 5

P = build_trades(STRESS_PCT, QLO, QHI, stress=False, hold=1)
plo, phi = boot_ci_iid(P["pnl"], seed=SEED + 1)
res["G4_placebo_n"] = int(len(P)); res["G4_placebo_net_per_trade"] = float(P["pnl"].mean())
res["G4_placebo_ci_iid"] = [plo, phi]
res["G4_pass"] = plo <= 0

plateau = {}
for sp in (0.85, 0.90, 0.95):
    for q in (0.20, 0.25, 0.30):
        t = build_trades(sp, q, 1 - q, stress=True, hold=1)
        plateau[f"s{int(sp*100)}_q{int(q*100)}"] = {"n": int(len(t)),
                                                    "net_per_trade": float(t["pnl"].mean())}
res["G5_plateau"] = plateau
res["G5_pass"] = all(v["net_per_trade"] > 0 for v in plateau.values())

absnet = abs(res["net_total"])
srt = T["pnl"].sort_values(ascending=False)
k1 = max(1, int(0.01 * len(T)))
res["G6_top1pct_share"] = float(srt.head(k1).sum() / absnet) if absnet > 0 else np.nan
res["G6_max_single_share"] = float(srt.iloc[0] / absnet) if absnet > 0 else np.nan
res["G6_worst_trade"] = float(srt.iloc[-1])
res["G6_es5"] = float(srt.tail(max(1, int(0.05 * len(T)))).mean())
res["G6_pass"] = (res["G6_top1pct_share"] <= 0.50) and (res["G6_max_single_share"] <= 0.25)

# G7 correlation vs certified Solar B ledger
led = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                               "HTFDIR01_DIRECTIONAL_TILT", "out", "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
mine_daily = T.set_index("exit_date")["pnl"].groupby(level=0).sum()
join = pd.DataFrame({"liqrev": mine_daily, "solar": led["B_SYM"]}).dropna()
res["G7_overlap_days"] = int(len(join))
res["G7_corr_full"] = float(join["liqrev"].corr(join["solar"])) if len(join) > 10 else None
losing = join[join["solar"] < 0]
res["G7_corr_losing"] = float(losing["liqrev"].corr(losing["solar"])) if len(losing) > 10 else None
res["G7_liqrev_net_on_solar_losing_days"] = float(losing["liqrev"].sum()) if len(losing) else 0.0
res["G7_pass"] = (res["G7_corr_losing"] is None) or (res["G7_corr_losing"] <= 0.25)

# G8 robustness reads
noRel = T[~T["release_entry"]]
res["G8a_exrelease"] = {"n": int(len(noRel)), "net_per_trade": float(noRel["pnl"].mean())}
post16 = T[pd.to_datetime(T["entry_date"]) >= "2016-01-01"]
p16lo, p16hi = boot_ci_iid(post16["pnl"], seed=SEED + 2)
res["G8b_2016_2026"] = {"n": int(len(post16)), "net_per_trade": float(post16["pnl"].mean()),
                        "ci_iid": [p16lo, p16hi]}
res["G8b_pass"] = p16hi > 0  # must not be significantly negative
T2 = build_trades(STRESS_PCT, QLO, QHI, stress=True, hold=2)
res["G8c_hold2"] = {"n": int(len(T2)), "net_per_trade": float(T2["pnl"].mean())}
noFlag = T[~T["gap_flag_window"]]
res["G8e_exgapflag"] = {"n": int(len(noFlag)), "net_per_trade": float(noFlag["pnl"].mean())}

res["per_year_net"] = {str(y): float(T.loc[yr == y, "pnl"].sum()) for y in sorted(yr.unique())}
gates = ["G1_pass", "G2_pass", "G3_pass", "G4_pass", "G5_pass", "G6_pass", "G7_pass", "G8b_pass"]
res["ALL_GATES_PASS"] = all(bool(res[g]) for g in gates)

T.to_csv(os.path.join(OUT, "liqrev01_trades.csv"), index=False)
P.to_csv(os.path.join(OUT, "liqrev01_placebo_trades.csv"), index=False)
with open(os.path.join(OUT, "liqrev01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
