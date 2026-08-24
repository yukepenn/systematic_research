"""OTR_VF4: anchored-cumulative 5-layer architecture (image-fidelity selected)."""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_vf1 import ema, slice_fp, dscore, TA  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_VF4_ANCHORED_LAYERS", "out")
os.makedirs(OUT, exist_ok=True)
STOP = 130.0
PCTS = (5, 25, 50, 75, 95)


def anchored_levels(time_arr, close, volume, amount=5, quantile_mode=False):
    """5 anchored-cumulative VWAP layers -> 5 levels per bar."""
    n = len(close)
    hours = time_arr.astype("datetime64[h]")
    lv = np.full((n, 5), np.nan)
    anchors = []  # list of [pv, v]
    cur = None
    for i in range(n):
        h = hours[i]
        if h != cur:
            cur = h
            anchors.append([0.0, 0.0])
            if len(anchors) > amount:
                anchors.pop(0)
        pv_add = close[i] * volume[i]
        for a in anchors:
            a[0] += pv_add
            a[1] += volume[i]
        if len(anchors) == amount and all(a[1] > 0 for a in anchors):
            vals = sorted(a[0] / a[1] for a in anchors)
            if quantile_mode:
                lv[i] = np.quantile(vals, [p / 100 for p in PCTS])
            else:
                lo, hi = vals[0], vals[-1]
                rng = hi - lo
                lv[i] = [lo + p / 100.0 * rng for p in PCTS]
    return lv


def run_vf4(bars, sig_mode="SIG1", exit_rule="X_FLIP", max_sig=3, split=5, close_thr=0.10):
    n = bars["n"]
    close, opn, high, low = bars["close"], bars["open"], bars["high"], bars["low"]
    t = bars["time"]
    last_bar = bars["last_bar"]
    lv = bars["levels"]
    LOW, P25, MED, P75, HIGH = (lv[:, k] for k in range(5))

    trades = []
    pos, entry_px, entry_i = 0, 0.0, -1
    stop_px = np.nan
    trend = 0
    sc = 0
    lsi = {-1: -10**9, 1: -10**9}
    pe, px_ = 0, False

    def ct(i, p, kind):
        nonlocal pos
        trades.append({"entry_time": str(t[entry_i]), "pnl": pos * (p - entry_px) * 20.0,
                       "exit_kind": kind,
                       "hold_min": float((t[i] - t[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    for i in range(1, n):
        if px_ and pos != 0:
            ct(i, opn[i], "rule")
            px_ = False
        if pe != 0 and pos == 0:
            pos = pe
            entry_px, entry_i = opn[i], i
            stop_px = entry_px - STOP if pos > 0 else entry_px + STOP
        pe = 0

        if pos != 0:
            if pos > 0 and low[i] <= stop_px:
                ct(i, opn[i] if opn[i] <= stop_px else stop_px, "stop130")
            elif pos < 0 and high[i] >= stop_px:
                ct(i, opn[i] if opn[i] >= stop_px else stop_px, "stop130")

        if np.isnan(lv[i, 0]) or np.isnan(lv[i - 1, 0]):
            continue

        pt = trend
        if close[i] > HIGH[i]:
            trend = 1
        elif close[i] < LOW[i]:
            trend = -1
        if trend != pt:
            sc = 0

        if last_bar[i]:
            if pos != 0:
                ct(i, close[i], "sc")
            px_ = False
            pe = 0
            continue

        # signal detection
        rng = high[i] - low[i]
        sig = 0
        if sig_mode == "SIG1":
            if trend > 0 and close[i - 1] > HIGH[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
                sig = 1
            elif trend < 0 and close[i - 1] < LOW[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
                sig = -1
        else:  # SIG2: touch of band edge while close holds beyond median
            if trend > 0 and low[i] <= HIGH[i] and close[i] >= MED[i] and close[i - 1] > HIGH[i - 1]:
                sig = 1
            elif trend < 0 and high[i] >= LOW[i] and close[i] <= MED[i] and close[i - 1] < LOW[i - 1]:
                sig = -1
        if sig == 1 and rng > 0 and (high[i] - close[i]) / rng < close_thr:
            sig = 0
        if sig == -1 and rng > 0 and (close[i] - low[i]) / rng < close_thr:
            sig = 0

        if pos != 0:
            if exit_rule == "X_FLIP":
                hit = trend == -pos
            elif exit_rule == "X_MED":
                hit = (pos > 0 and close[i] < MED[i]) or (pos < 0 and close[i] > MED[i])
            else:  # X_OPP
                hit = sig == -pos
            if hit:
                px_ = True
                continue

        if pos == 0 and sig != 0 and sc < max_sig and (i - lsi[sig]) >= split:
            pe = sig
            sc += 1
            lsi[sig] = i
    return trades


print("[VF4] loading ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= "2026-02-20") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
t = df["time"].values.astype("datetime64[s]")
fb = np.zeros(len(df), bool); fb[0] = True
fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
lb = np.zeros(len(df), bool); lb[:-1] = fb[1:]; lb[-1] = True
print("[VF4] anchored layers ...", flush=True)
LV = anchored_levels(t, df["close"].values, df["volume"].values)
bars = {"n": len(df), "time": t, "open": df["open"].values, "high": df["high"].values,
        "low": df["low"].values, "close": df["close"].values, "last_bar": lb, "levels": LV}

SEC = [("W20260308", "2026-03-08", "2026-03-13"), ("W20260322", "2026-03-22", "2026-03-27"),
       ("W20260419", "2026-04-19", "2026-04-24")]
results = []
for sm in ("SIG1", "SIG2"):
    for xr in ("X_FLIP", "X_MED", "X_OPP"):
        cid = f"ANC|{sm}|{xr}|stop130"
        trades = run_vf4(bars, sig_mode=sm, exit_rule=xr)
        fpA = slice_fp(trades, "2026-05-10", "2026-05-22", 10)
        D = dscore(fpA)
        sec = {w[0]: slice_fp(trades, w[1], w[2], 5) for w in SEC}
        results.append({"cell": cid, "D": D, "windowA": fpA, "secondary": sec})
        print(f"[VF4] {cid:24s} D={D:8.3f} A: n={fpA.get('trades',0):4d} net={fpA.get('net',0):8.0f} "
              f"WR={fpA.get('win_rate_pct',0):6.2f} PF={fpA.get('pf')} hold={fpA.get('avg_hold_min',0)} "
              f"aw={fpA.get('avg_win')} al={fpA.get('avg_loss')} worst={fpA.get('largest_loss')}", flush=True)

# quantile-levels disclosure on best cell
results.sort(key=lambda r: r["D"])
best = results[0]["cell"]
sm, xr = best.split("|")[1], best.split("|")[2]
LVq = anchored_levels(t, df["close"].values, df["volume"].values, quantile_mode=True)
bars_q = dict(bars); bars_q["levels"] = LVq
trades = run_vf4(bars_q, sig_mode=sm, exit_rule=xr)
fpA = slice_fp(trades, "2026-05-10", "2026-05-22", 10)
D = dscore(fpA)
results.append({"cell": best + "|QLEV", "D": D, "windowA": fpA,
                "secondary": {w[0]: slice_fp(trades, w[1], w[2], 5) for w in SEC}})
print(f"[VF4] {best+'|QLEV':24s} D={D:8.3f} A: n={fpA.get('trades',0):4d} net={fpA.get('net',0):8.0f} "
      f"WR={fpA.get('win_rate_pct',0):6.2f} hold={fpA.get('avg_hold_min',0)}", flush=True)

results.sort(key=lambda r: r["D"])
json.dump({"targetA": TA, "results": results}, open(os.path.join(OUT, "sweep_results.json"), "w"), indent=1)
with open(os.path.join(OUT, "scorecard.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell", "D", "A_trades", "A_net", "A_wr", "A_pf", "A_hold", "A_avg_win", "A_avg_loss", "A_dd", "A_worst"])
    for r in results:
        a = r["windowA"]
        w.writerow([r["cell"], r["D"], a.get("trades"), a.get("net"), a.get("win_rate_pct"), a.get("pf"),
                    a.get("avg_hold_min"), a.get("avg_win"), a.get("avg_loss"), a.get("max_dd"), a.get("largest_loss")])
print("[VF4] best:", results[0]["cell"], results[0]["D"], flush=True)
print("[VF4] best secondary:", json.dumps(results[0]["secondary"]), flush=True)
