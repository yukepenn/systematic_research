#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOSEREV01 -- 01_closerev01.py
Runs the FROZEN SPEC.md (committed be9b993 BEFORE this executed). Post-cash-close
price-pressure reversion, 16:00->16:14 ET, on the 20-year NQ minute substrate.
Cost model frozen by the pre-outcome BBO audit: 1.5 ticks/side + $4.36/RT commission
(stress: 2.0 ticks/side + 3x commission). Run from repo root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "research", "system_master", "CLOSEREV01_POSTCLOSE_REVERSION", "out")

SEED = 20260820
NB = 10_000
TICK = 0.25
PV = 20.0
SLIP_T = 1.5           # primary, frozen by BBO audit
COMM_RT = 4.36
Z_TRIG = 2.0
SIG_WIN = 63

print("[CLOSEREV01] loading minute substrate ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
df["hm"] = df["time"].dt.hour * 100 + df["time"].dt.minute

# per-day anchor closes
need = {1530: "c1530", 1545: "c1545", 1550: "c1550", 1600: "c1600", 1614: "c1614"}
piv = {}
for hm_v, name in need.items():
    s = df[df["hm"] == hm_v].groupby("d")["close"].last()
    piv[name] = s
day = pd.DataFrame(piv).dropna(subset=["c1545", "c1600", "c1614"])
day.index = pd.to_datetime(pd.Index(day.index))
day = day.sort_index()
n = len(day)
print(f"[CLOSEREV01] usable days: {n} ({day.index[0].date()} .. {day.index[-1].date()})", flush=True)


def trades_for(win_col, z_trig, slip_t=SLIP_T, comm_rt=COMM_RT):
    imp = day["c1600"] - day[win_col]
    sig = imp.rolling(SIG_WIN).std().shift(1)
    z = imp / sig
    t = pd.DataFrame({"z": z, "imp": imp}).dropna()
    t = t[t["z"].abs() >= z_trig]
    side = -np.sign(t["imp"]).astype(int)
    e = day.loc[t.index, "c1600"] + side * slip_t * TICK
    x = day.loc[t.index, "c1614"] - side * slip_t * TICK
    pnl = side * (x - e) * PV - comm_rt
    return pd.DataFrame({"date": t.index, "z": t["z"].values, "side": side.values,
                         "pnl": pnl.values}).reset_index(drop=True)


def placebo_for(win_col, slip_t=SLIP_T, comm_rt=COMM_RT):
    imp = day["c1600"] - day[win_col]
    sig = imp.rolling(SIG_WIN).std().shift(1)
    z = imp / sig
    t = pd.DataFrame({"z": z, "imp": imp}).dropna()
    t = t[t["z"].abs() < 1.0]
    side = -np.sign(t["imp"]).astype(int)
    side = side.replace(0, 1)  # zero-impulse days: long by convention (rare, disclosed)
    e = day.loc[t.index, "c1600"] + side * slip_t * TICK
    x = day.loc[t.index, "c1614"] - side * slip_t * TICK
    pnl = side * (x - e) * PV - comm_rt
    return pd.DataFrame({"date": t.index, "pnl": pnl.values})


def boot_iid(x, seed):
    rng = np.random.default_rng(seed)
    xn = np.asarray(x); m = np.empty(NB)
    for k in range(NB):
        m[k] = xn[rng.integers(0, len(xn), len(xn))].mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_episode(T, seed):
    sess = {d: i for i, d in enumerate(day.index)}
    td = T.sort_values("date").reset_index(drop=True)
    si = td["date"].map(lambda d: sess[d]).to_numpy()
    eps, cur = [], [0]
    for j in range(1, len(td)):
        if si[j] - si[j - 1] <= 5:
            cur.append(j)
        else:
            eps.append(cur); cur = [j]
    eps.append(cur)
    pnl = td["pnl"].to_numpy()
    arrs = [pnl[e] for e in eps]
    rng = np.random.default_rng(seed)
    m = np.empty(NB); ne = len(arrs)
    for k in range(NB):
        pick = rng.integers(0, ne, ne)
        m[k] = np.concatenate([arrs[p] for p in pick]).mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), ne


res = {"seed": SEED, "n_boot": NB, "cost_primary": "1.5t/side + $4.36 RT",
       "n_usable_days": int(n)}

T = trades_for("c1545", Z_TRIG)
res["G1_N"] = int(len(T)); res["G1_pass"] = len(T) >= 150
res["net_total"] = float(T["pnl"].sum()); res["net_per_trade"] = float(T["pnl"].mean())
res["n_long"] = int((T["side"] == 1).sum()); res["n_short"] = int((T["side"] == -1).sum())
res["net_long_cell"] = float(T.loc[T["side"] == 1, "pnl"].sum())
res["net_short_cell"] = float(T.loc[T["side"] == -1, "pnl"].sum())

ilo, ihi = boot_iid(T["pnl"], SEED)
elo, ehi, ne = boot_episode(T, SEED)
res["G2_ci_iid"] = [ilo, ihi]; res["G2_ci_episode"] = [elo, ehi]; res["G2_n_episodes"] = ne
res["G2_pass"] = (ilo > 0) and (elo > 0)

yr = pd.to_datetime(T["date"]).dt.year
pre = T[yr < 2020]; post = T[yr >= 2020]
plo_, phi_ = boot_iid(pre["pnl"], SEED + 1) if len(pre) > 5 else (np.nan, np.nan)
qlo_, qhi_ = boot_iid(post["pnl"], SEED + 2) if len(post) > 5 else (np.nan, np.nan)
res["G3_pre2020"] = {"n": int(len(pre)), "mean": float(pre["pnl"].mean()), "ci": [plo_, phi_]}
res["G3_post2020"] = {"n": int(len(post)), "mean": float(post["pnl"].mean()), "ci": [qlo_, qhi_]}
res["G3_pass"] = (pre["pnl"].mean() > 0 and post["pnl"].mean() > 0
                  and (plo_ > 0 or qlo_ > 0) and not (phi_ < 0) and not (qhi_ < 0))

e1 = T[yr <= 2015]; e2 = T[yr >= 2016]
se1 = e1["pnl"].std(ddof=1) / np.sqrt(len(e1)) if len(e1) > 2 else np.nan
res["G4_2006_2015"] = {"n": int(len(e1)), "mean": float(e1["pnl"].mean()), "se": float(se1)}
res["G4_2016_2026"] = {"n": int(len(e2)), "mean": float(e2["pnl"].mean())}
res["G4_pass"] = e2["pnl"].mean() >= e1["pnl"].mean() - se1

P = placebo_for("c1545")
pl, ph = boot_iid(P["pnl"], SEED + 3)
res["G5_placebo"] = {"n": int(len(P)), "mean": float(P["pnl"].mean()), "ci": [pl, ph]}
res["G5_pass"] = pl <= 0

plateau = {}
for zz in (1.5, 2.0, 2.5):
    for wc in ("c1530", "c1545", "c1550"):
        tt = trades_for(wc, zz)
        plateau[f"z{zz}_{wc}"] = {"n": int(len(tt)), "mean": float(tt["pnl"].mean())}
res["G6_plateau"] = plateau
res["G6_pass"] = all(v["mean"] > 0 for v in plateau.values())

absnet = abs(res["net_total"])
srt = T["pnl"].sort_values(ascending=False)
k1 = max(1, int(0.01 * len(T)))
res["G7_top1pct_share"] = float(srt.head(k1).sum() / absnet) if absnet > 0 else np.nan
res["G7_max_winner_share"] = float(srt.iloc[0] / absnet) if absnet > 0 else np.nan
res["G7_max_loser_share"] = float(abs(srt.iloc[-1]) / absnet) if absnet > 0 else np.nan
res["G7_worst_trade"] = float(srt.iloc[-1]); res["G7_best_trade"] = float(srt.iloc[0])
res["G7_pass"] = (res["G7_top1pct_share"] <= 0.50 and res["G7_max_winner_share"] <= 0.25
                  and res["G7_max_loser_share"] <= 0.25)

led = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                               "HTFDIR01_DIRECTIONAL_TILT", "out", "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
mine = T.set_index("date")["pnl"].groupby(level=0).sum()
j = pd.DataFrame({"cr": mine, "solar": led["B_SYM"]}).dropna()
res["G8_overlap_days"] = int(len(j))
res["G8_corr_full"] = float(j["cr"].corr(j["solar"])) if len(j) > 10 else None
losing = j[j["solar"] < 0]
res["G8_corr_losing"] = float(losing["cr"].corr(losing["solar"])) if len(losing) > 10 else None
res["G8_net_on_solar_losing"] = float(losing["cr"].sum()) if len(losing) else 0.0
res["G8_net_on_solar_winning"] = float(j.loc[j["solar"] >= 0, "cr"].sum()) if len(j) else 0.0
res["G8_pass"] = (res["G8_corr_losing"] is None) or (res["G8_corr_losing"] <= 0.25)

Ts = trades_for("c1545", Z_TRIG, slip_t=2.0, comm_rt=3 * COMM_RT)
silo, sihi = boot_iid(Ts["pnl"], SEED + 4)
selo, sehi, _ = boot_episode(Ts, SEED + 4)
yrs = pd.to_datetime(Ts["date"]).dt.year
pre_s = Ts[yrs < 2020]; post_s = Ts[yrs >= 2020]
res["G9_stress"] = {"net_per_trade": float(Ts["pnl"].mean()), "ci_iid": [silo, sihi],
                    "ci_episode": [selo, sehi],
                    "pre2020_mean": float(pre_s["pnl"].mean()),
                    "post2020_mean": float(post_s["pnl"].mean())}
res["G9_pass"] = (silo > 0 and selo > 0 and pre_s["pnl"].mean() > 0 and post_s["pnl"].mean() > 0)

res["per_year_net"] = {str(y): float(T.loc[yr == y, "pnl"].sum()) for y in sorted(yr.unique())}
gates = [g for g in res if g.endswith("_pass")]
res["ALL_GATES_PASS"] = all(bool(res[g]) for g in gates)

T.to_csv(os.path.join(OUT, "closerev01_trades.csv"), index=False)
P.to_csv(os.path.join(OUT, "closerev01_placebo_trades.csv"), index=False)
with open(os.path.join(OUT, "closerev01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
