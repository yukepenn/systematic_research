#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONRANGE01 -- 00_diagnostic.py (DIAGNOSTIC, zero alpha budget)
Owner claim to verify: "NQ RTH breaks the non-RTH (overnight) high or low ~95% of the time."
STRICT SCOPE: break frequencies, sides, timing, open-position stats ONLY.
NO post-break return/P&L statistic is computed here (strategy spec freezes first).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "research", "system_master", "ONRANGE01_OVERNIGHT_BREAK", "out")
os.makedirs(OUT, exist_ok=True)

print("[ONRANGE01] loading minute substrate ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df["d"] = df["time"].dt.date
hm = df["time"].dt.hour * 100 + df["time"].dt.minute
df["hm"] = hm

rth = df[(hm >= 930) & (hm <= 1558)]
nb = rth.groupby("d").size()
valid_days = sorted(nb[nb >= 200].index)
print(f"[ONRANGE01] RTH days: {len(valid_days)}", flush=True)

# overnight window for day D: bars(date=D-1cal, hm>=1800) + bars(date=D, hm<930)
by_date = dict(tuple(df.groupby("d")))
rows = []
for D in valid_days:
    Dprev = D - pd.Timedelta(days=1)
    prev = by_date.get(Dprev.date() if hasattr(Dprev, "date") else Dprev)
    prev = prev[prev["hm"] >= 1800] if prev is not None else None
    cur_on = by_date[D]
    cur_on = cur_on[cur_on["hm"] < 930]
    parts = [p for p in (prev, cur_on) if p is not None and len(p)]
    if not parts:
        continue
    on = pd.concat(parts)
    if len(on) < 60:
        continue
    onh, onl = on["high"].max(), on["low"].min()
    r = by_date[D]
    r = r[(r["hm"] >= 930) & (r["hm"] <= 1558)].sort_values("time")
    ropen = r["open"].iloc[0]
    hi_break = r["high"].gt(onh)
    lo_break = r["low"].lt(onl)
    t_hi = r.loc[hi_break, "time"].iloc[0] if hi_break.any() else None
    t_lo = r.loc[lo_break, "time"].iloc[0] if lo_break.any() else None
    if t_hi is not None and t_lo is not None:
        first = "HIGH" if t_hi < t_lo else "LOW"
        t_first = min(t_hi, t_lo)
    elif t_hi is not None:
        first, t_first = "HIGH", t_hi
    elif t_lo is not None:
        first, t_first = "LOW", t_lo
    else:
        first, t_first = "NONE", None
    rows.append({
        "day": str(D), "on_bars": len(on), "on_high": onh, "on_low": onl,
        "on_range_pts": onh - onl, "rth_open": ropen,
        "open_in_range": bool(onl <= ropen <= onh),
        "open_above": bool(ropen > onh), "open_below": bool(ropen < onl),
        "broke_high": bool(hi_break.any()), "broke_low": bool(lo_break.any()),
        "broke_either": bool(hi_break.any() or lo_break.any()),
        "broke_both": bool(hi_break.any() and lo_break.any()),
        "first_break": first,
        "first_break_hm": int(t_first.hour * 100 + t_first.minute) if t_first is not None else None,
    })

T = pd.DataFrame(rows)
T["year"] = pd.to_datetime(T["day"]).dt.year

res = {"n_days": int(len(T)),
       "P_break_either": float(T.broke_either.mean()),
       "P_break_high": float(T.broke_high.mean()),
       "P_break_low": float(T.broke_low.mean()),
       "P_break_both": float(T.broke_both.mean()),
       "P_first_HIGH": float((T.first_break == "HIGH").mean()),
       "P_first_LOW": float((T.first_break == "LOW").mean()),
       "P_none": float((T.first_break == "NONE").mean()),
       "P_open_in_range": float(T.open_in_range.mean()),
       "P_open_above": float(T.open_above.mean()),
       "P_open_below": float(T.open_below.mean()),
       "P_break_either_GIVEN_open_in_range": float(T.loc[T.open_in_range, "broke_either"].mean()),
       "P_break_both_GIVEN_open_in_range": float(T.loc[T.open_in_range, "broke_both"].mean()),
       "on_range_pts_median": float(T.on_range_pts.median()),
       "on_range_pts_p25_p75": [float(T.on_range_pts.quantile(.25)), float(T.on_range_pts.quantile(.75))],
       "first_break_time_median_hm": float(T.first_break_hm.dropna().median()),
       "first_break_by_1030_frac": float((T.first_break_hm.dropna() <= 1030).mean()),
       "per_year_P_either": {str(y): float(g.broke_either.mean()) for y, g in T.groupby("year")},
       "per_year_P_both": {str(y): float(g.broke_both.mean()) for y, g in T.groupby("year")}}

T.to_csv(os.path.join(OUT, "onrange_daily_facts.csv"), index=False)
with open(os.path.join(OUT, "diagnostic.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1), flush=True)
