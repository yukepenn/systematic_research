"""OTR_V1_PROXY: bounded Track-V proxy mechanism sweep."""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v_proxy_engine import ema, ladder_series, run_v_proxy  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_V1_PROXY", "out")
os.makedirs(OUT, exist_ok=True)

TA = {"trades": 183, "trades_per_day": 18.3, "win_rate_pct": 37.70, "pf": 0.95,
      "avg_hold_min": 39.84, "avg_win": 1236.16, "avg_loss": -783.77, "max_dd": -12700.0, "net": -4055.0}
SC = {"trades": 0.075 * 183, "trades_per_day": 0.075 * 18.3, "win_rate_pct": 2.0, "pf": 0.075,
      "avg_hold_min": 0.15 * 39.84, "avg_win": 0.15 * 1236.16, "avg_loss": 0.15 * 783.77,
      "max_dd": 0.20 * 12700.0, "net": 0.15 * 4055.0}
PRIM = ["trades", "trades_per_day", "win_rate_pct", "pf", "avg_hold_min", "avg_win", "avg_loss", "max_dd"]

WA = ("2026-05-10", "2026-05-22")
SECONDARY = [("W20260308", "2026-03-08", "2026-03-13", {"trades": 76, "net": 9325, "wr": 38.16, "hold": 49.83}),
             ("W20260322", "2026-03-22", "2026-03-27", {"trades": 92, "net": -42235, "wr": 28.26, "hold": 33.66}),
             ("W20260419", "2026-04-19", "2026-04-24", {"trades": 47, "net": 9215, "wr": 42.55, "hold": 72.04})]

print("[V1] loading parquet ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= "2026-02-20") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
t = df["time"].values.astype("datetime64[s]")
first_bar = np.zeros(len(df), bool); first_bar[0] = True
first_bar[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
last_bar = np.zeros(len(df), bool); last_bar[:-1] = first_bar[1:]; last_bar[-1] = True
print(f"[V1] bars {len(df)}, computing ladder ...", flush=True)
lad = ladder_series(t, df["close"].values, df["volume"].values)
bars = {"n": len(df), "time": t, "open": df["open"].values, "close": df["close"].values,
        "last_bar": last_bar, "ladder": lad, "ema20": ema(df["close"].values, 20)}


def slice_fp(trades, d0, d1):
    lo = np.datetime64(f"{d0}T18:00:00") - np.timedelta64(24, "h")
    lo = np.datetime64(f"{d0}") + np.timedelta64(18, "h")
    hi = np.datetime64(f"{d1}T17:00:00")
    wt = [x for x in trades if lo <= np.datetime64(x["entry_time"]) <= hi]
    if not wt:
        return {"trades": 0}
    pnl = np.array([x["pnl"] for x in wt])
    wins = pnl > 0
    gl = pnl[~wins].sum()
    eq = np.cumsum(pnl)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    n_days = 10 if d0 == WA[0] else 5
    return {"trades": len(wt), "trades_per_day": round(len(wt) / n_days, 2),
            "net": round(float(pnl.sum()), 0), "win_rate_pct": round(float(wins.mean() * 100), 2),
            "pf": round(float(pnl[wins].sum() / -gl), 3) if gl < 0 else None,
            "avg_hold_min": round(float(np.mean([x["hold_min"] for x in wt])), 1),
            "avg_win": round(float(pnl[wins].mean()), 0) if wins.any() else None,
            "avg_loss": round(float(pnl[~wins].mean()), 0) if (~wins).any() else None,
            "max_dd": round(float(dd.min()), 0)}


def dscore(fp):
    errs = {}
    for k in PRIM + ["net"]:
        v = fp.get(k)
        errs[k] = abs(v - TA[k]) / SC[k] if v is not None else 99.0
    return round(float(np.mean([errs[k] for k in PRIM]) + 0.5 * errs["net"]), 3)


def w0416(m):
    return (m >= 240) & (m < 960)


CELLS = []
for ef in ("M_BRK", "M_REV"):
    for td in ("T_LVL", "T_SLP"):
        for xr in ("X_MED", "X_OPP"):
            CELLS.append((f"{ef}|{td}|{xr}", dict(entry_family=ef, trend_def=td, exit_rule=xr)))

results = []
for cid, kw in CELLS:
    trades = run_v_proxy(bars, **kw)
    fpA = slice_fp(trades, *WA)
    D = dscore(fpA)
    sec = {w[0]: slice_fp(trades, w[1], w[2]) for w in SECONDARY}
    results.append({"cell": cid, "D": D, "windowA": fpA, "secondary": sec})
    print(f"[V1] {cid:22s} D={D:8.3f} A: n={fpA.get('trades',0):4d} net={fpA.get('net',0):8.0f} "
          f"WR={fpA.get('win_rate_pct',0):6.2f} PF={fpA.get('pf')} hold={fpA.get('avg_hold_min',0)} "
          f"aw={fpA.get('avg_win')} al={fpA.get('avg_loss')}", flush=True)

results.sort(key=lambda r: r["D"])
for r in results[:2]:
    cid = r["cell"]
    kw = dict(CELLS)[cid]
    trades = run_v_proxy(bars, entry_time_mask=w0416, **kw)
    fpA = slice_fp(trades, *WA)
    D = dscore(fpA)
    results.append({"cell": cid + "|W0416", "D": D, "windowA": fpA,
                    "secondary": {w[0]: slice_fp(trades, w[1], w[2]) for w in SECONDARY}})
    print(f"[V1] {cid+'|W0416':22s} D={D:8.3f} A: n={fpA.get('trades',0):4d} net={fpA.get('net',0):8.0f} "
          f"WR={fpA.get('win_rate_pct',0):6.2f} hold={fpA.get('avg_hold_min',0)}", flush=True)

results.sort(key=lambda r: r["D"])
with open(os.path.join(OUT, "sweep_results.json"), "w") as f:
    json.dump({"targetA": TA, "results": results}, f, indent=1)
with open(os.path.join(OUT, "scorecard.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell", "D", "A_trades", "A_net", "A_wr", "A_pf", "A_hold", "A_avg_win", "A_avg_loss", "A_dd"])
    for r in results:
        a = r["windowA"]
        w.writerow([r["cell"], r["D"], a.get("trades"), a.get("net"), a.get("win_rate_pct"),
                    a.get("pf"), a.get("avg_hold_min"), a.get("avg_win"), a.get("avg_loss"), a.get("max_dd")])
print("[V1] best:", results[0]["cell"], results[0]["D"], flush=True)
