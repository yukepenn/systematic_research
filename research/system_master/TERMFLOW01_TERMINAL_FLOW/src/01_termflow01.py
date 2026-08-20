#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TERMFLOW01 -- 01_termflow01.py
Runs the FROZEN SPEC.md. Step 0 convention audit writes out/convention_audit.json BEFORE any
P&L is computed. Run from repo root.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "research", "system_master", "TERMFLOW01_TERMINAL_FLOW", "out")
os.makedirs(OUT, exist_ok=True)

SEED = 20260819
NB = 10_000
TICK = 0.25
PV = 20.0
COMM_RT = 4.36

print("[TERMFLOW01] loading minute substrate ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
hm = df["time"].dt.hour * 100 + df["time"].dt.minute
rth = df[(hm >= 930) & (hm <= 1558)]
nb_ = rth.groupby("d").size()
valid = set(nb_[nb_ >= 200].index)
days = pd.to_datetime(sorted(valid))
print(f"[TERMFLOW01] trading days: {len(days)} ({days[0].date()}..{days[-1].date()})", flush=True)

# per-day label->price lookup for the labels we need
need = [1530, 1535, 1540, 1545, 1550, 1551, 1552, 1559]
sub = df[df["d"].isin(valid) & (hm.isin(need))]
px = {}
for lbl in need:
    s = sub[sub["time"].dt.hour * 100 + sub["time"].dt.minute == lbl]
    px[lbl] = {"o": s.set_index("d")["open"], "c": s.set_index("d")["close"]}

# ---------- step 0: convention audit (pre-outcome) ----------
audit = {"n_trading_days": int(len(days))}
for lbl in need:
    audit[f"label_{lbl}_coverage"] = float(len(px[lbl]["c"]) / len(days))
# label semantics probe: how many bars carry labels 1559/1600/1601 across the file
hm_all = df["time"].dt.hour * 100 + df["time"].dt.minute
audit["bars_labeled_1559"] = int((hm_all == 1559).sum())
audit["bars_labeled_1600"] = int((hm_all == 1600).sum())
audit["bars_labeled_1601"] = int((hm_all == 1601).sum())
with open(os.path.join(OUT, "convention_audit.json"), "w") as f:
    json.dump(audit, f, indent=1)
print("[TERMFLOW01] convention audit written:", json.dumps(audit), flush=True)

# ---------- flags ----------
dser = pd.Series(days, index=days)
month_grp = dser.groupby([days.year, days.month])
last_of_month = set(month_grp.max())
third_fridays = set()
for (y, m), g in month_grp:
    fr = [d for d in g if d.weekday() == 4]
    if len(fr) >= 3:
        third_fridays.add(fr[2])
flagged = sorted(last_of_month | third_fridays)
flag_kind = {}
for d in flagged:
    kinds = []
    if d in last_of_month:
        kinds.append("month_end")
        if d.month in (3, 6, 9, 12):
            kinds.append("quarter_end")
    if d in third_fridays:
        kinds.append("opex")
        if d.month in (3, 6, 9, 12):
            kinds.append("quad_witch")
        if d.month == 12:
            kinds.append("ndx_recon")
    flag_kind[d] = "+".join(kinds)


def event_pnl(day, lb_lbl=1530, ent_lbl=1551, slip_ticks=1.0, comm=COMM_RT):
    d0 = day.date()
    try:
        c_lb = px[lb_lbl]["c"].loc[d0]
        c_1550 = px[1550]["c"].loc[d0]
        x_exit = px[1559]["c"].loc[d0]
    except KeyError:
        return None
    r_pre = c_1550 - c_lb
    if r_pre == 0:
        return None
    direction = 1.0 if r_pre > 0 else -1.0
    try:
        e_in = px[ent_lbl]["o"].loc[d0] if ent_lbl == 1551 else px[ent_lbl]["c"].loc[d0]
    except KeyError:
        e_in = c_1550
    gross = direction * (x_exit - e_in) * PV
    return gross - comm - 2 * slip_ticks * TICK * PV


rows = []
for d in flagged:
    p = event_pnl(d)
    if p is None:
        continue
    d0 = d.date()
    c_lb = px[1530]["c"].loc[d0]; c_1550 = px[1550]["c"].loc[d0]
    try:
        o930 = df[(df["d"] == d0) & (hm == 930)]["open"].iloc[0]
    except IndexError:
        o930 = np.nan
    rows.append({"day": d, "kind": flag_kind[d], "pnl": p,
                 "dir": 1 if c_1550 > c_lb else -1,
                 "mom_dir": np.sign(c_1550 - o930) if np.isfinite(o930) else np.nan})
T = pd.DataFrame(rows)
res = {"seed": SEED, "n_boot": NB, "n_flagged_calendar": len(flagged)}
res["G1_N"] = int(len(T)); res["G1_pass"] = len(T) >= 400
res["net_total"] = float(T.pnl.sum()); res["net_per_event"] = float(T.pnl.mean())


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
        m[k] = np.concatenate([groups[p] for p in pick]).mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


ilo, ihi = boot_iid(T.pnl, SEED)
ylo, yhi = boot_yearblock(T, SEED)
res["G2_ci_iid"] = [ilo, ihi]; res["G2_ci_yearblock"] = [ylo, yhi]
res["G2_pass"] = bool(res["net_total"] > 0 and ilo > 0 and ylo > 0)

yr = pd.to_datetime(T["day"]).dt.year
pre, post = T[yr < 2020], T[yr >= 2020]
plo, phi = boot_iid(pre.pnl, SEED + 1); qlo, qhi = boot_iid(post.pnl, SEED + 2)
res["G3_pre2020"] = {"n": int(len(pre)), "mean": float(pre.pnl.mean()), "ci": [plo, phi]}
res["G3_post2020"] = {"n": int(len(post)), "mean": float(post.pnl.mean()), "ci": [qlo, qhi]}
res["G3_pass"] = bool(pre.pnl.mean() > 0 and post.pnl.mean() > 0
                      and (plo > 0 or qlo > 0) and not (phi < 0) and not (qhi < 0))

h1, h2 = T[yr <= 2015], T[yr >= 2016]
res["G4_halves"] = {"h1_mean": float(h1.pnl.mean()), "h2_mean": float(h2.pnl.mean())}
res["G4_pass"] = bool(np.sign(h1.pnl.mean()) == np.sign(h2.pnl.mean()))
res["G4_second_half_stronger"] = bool(h2.pnl.mean() > h1.pnl.mean())


def t_nw(x, lag=5):
    x = np.asarray(x, float); n_ = len(x); xb = x.mean(); z = x - xb
    S = float((z ** 2).sum())
    for l in range(1, min(lag, n_ - 1) + 1):
        S += 2.0 * (1.0 - l / (lag + 1.0)) * float((z[l:] * z[:-l]).sum())
    return xb / (np.sqrt(S) / n_)


rng = np.random.default_rng(SEED)
flag_set = set(T.day)
unflagged_by_year = {y: [d for d in days if d.year == y and d not in flag_set]
                     for y in sorted(yr.unique())}
ctrl_rows = []
for d in T.day:
    pool = unflagged_by_year[d.year]
    picks = rng.choice(len(pool), size=min(3, len(pool)), replace=False)
    for i in picks:
        p = event_pnl(pool[i])
        if p is not None:
            ctrl_rows.append({"flag_day": d, "day": pool[i], "pnl": p})
C = pd.DataFrame(ctrl_rows)
res["G5_flagged_tnw"] = float(t_nw(T.pnl))
res["G5_ctrl_mean"] = float(C.pnl.mean()); res["G5_ctrl_n"] = int(len(C))
diff_series = T.pnl.to_numpy() - C.groupby("flag_day").pnl.mean().reindex(T.day).to_numpy()
diff_series = diff_series[np.isfinite(diff_series)]
res["G5_diff_tnw"] = float(t_nw(diff_series))
res["G5_pass"] = bool(res["G5_flagged_tnw"] >= 2 and res["G5_diff_tnw"] >= 2)

plat = {}
for ent, elbl in [("1545", 1545), ("1550", 1551), ("1552", 1552)]:
    for lb in [1530, 1535, 1540]:
        pnls = [event_pnl(d, lb_lbl=lb, ent_lbl=elbl) for d in flagged]
        pnls = [p for p in pnls if p is not None]
        plat[f"e{ent}_lb{lb}"] = float(np.mean(pnls))
res["G6_plateau"] = plat
res["G6_pass"] = bool(len({np.sign(v) for v in plat.values()}) == 1)

absnet = abs(res["net_total"])
srt = T.pnl.sort_values(ascending=False)
k1 = max(1, int(0.01 * len(T)))
res["G7_top1pct_share"] = float(srt.head(k1).sum() / absnet)
res["G7_max_win_share"] = float(srt.iloc[0] / absnet)
res["G7_max_loss_share"] = float(abs(srt.iloc[-1]) / absnet)
res["G7_pass"] = bool(res["G7_top1pct_share"] <= 0.5 and res["G7_max_win_share"] <= 0.25
                      and res["G7_max_loss_share"] <= 0.25)

led = pd.read_csv(os.path.join(ROOT, "research", "system_master",
                               "HTFDIR01_DIRECTIONAL_TILT", "out", "daily_ledgers_dev.csv"),
                  index_col=0, parse_dates=True)
j = pd.DataFrame({"tf": T.set_index("day").pnl, "solar": led["B_SYM"]}).dropna()
losing = j[j.solar < 0]
res["G8_overlap_days"] = int(len(j)); res["G8_losing_days"] = int(len(losing))
res["G8_corr_losing"] = float(losing.tf.corr(losing.solar)) if len(losing) > 10 else None
res["G8_net_on_solar_losing"] = float(losing.tf.sum()) if len(losing) else 0.0
res["G8_pass"] = (res["G8_corr_losing"] is None) or (res["G8_corr_losing"] <= 0.25)

mom_match = (T["dir"] == T["mom_dir"]).mean()
res["G9_mom_match_rate"] = float(mom_match)
res["G9_pass"] = bool(mom_match <= 0.70)

Ts = T.pnl + COMM_RT + 2 * TICK * PV - 3 * COMM_RT - 2 * 2 * TICK * PV
slo, shi = boot_iid(Ts, SEED + 3)
res["G10_stress"] = {"mean": float(Ts.mean()), "ci_iid": [slo, shi]}
res["G10_pass"] = bool(Ts.sum() > 0 and slo > 0)

res["per_kind"] = {k: {"n": int(g.pnl.count()), "mean": float(g.pnl.mean()),
                       "net": float(g.pnl.sum())} for k, g in T.groupby("kind")}
res["per_year_net"] = {str(y): float(T.loc[yr == y, "pnl"].sum()) for y in sorted(yr.unique())}
gates = [k for k in res if k.endswith("_pass")]
res["ALL_GATES_PASS"] = bool(all(res[k] for k in gates))

T.to_csv(os.path.join(OUT, "termflow01_events.csv"), index=False)
C.to_csv(os.path.join(OUT, "termflow01_control.csv"), index=False)
with open(os.path.join(OUT, "termflow01_results.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str), flush=True)
