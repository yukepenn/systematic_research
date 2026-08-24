"""OTR_R3_VF2026: VF4 clone + wrapper grid (stop microstructure x head-window) vs Jan-May 2026 weeklies."""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_vf4 import anchored_levels  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R3_VF2026", "out")
os.makedirs(OUT, exist_ok=True)

tgt = [r for r in csv.DictReader(open(os.path.join(
    ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
    "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))
    if r["report_end"] and "2026" in r["report_end"]]
tgt = [r for r in tgt if pd.Timestamp(r["report_end"]) <= pd.Timestamp("2026-05-29")
       and "EXECUTION" not in (r.get("notes") or "")]

df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= "2026-01-18") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
t = df["time"].values.astype("datetime64[s]")
fb = np.zeros(len(df), bool); fb[0] = True
fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
lb = np.zeros(len(df), bool); lb[:-1] = fb[1:]; lb[-1] = True
print("[R3] anchored layers ...", flush=True)
LV = anchored_levels(t, df["close"].values, df["volume"].values, quantile_mode=True)
mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)

BARS = {"n": len(df), "time": t, "open": df["open"].values, "high": df["high"].values,
        "low": df["low"].values, "close": df["close"].values, "last_bar": lb, "levels": LV}

WINDOWS = {"none": None, "1015_1600": (615, 960), "0915_1600": (555, 960), "0300_1200": (180, 720)}


def run_vf(bars, sig_mode, exit_rule, stop_pts, qty, win, max_sig=3, split=5, close_thr=0.10):
    n = bars["n"]
    close, opn, high, low = bars["close"], bars["open"], bars["high"], bars["low"]
    tt = bars["time"]; last_bar = bars["last_bar"]; lv = bars["levels"]
    LOW, P25, MED, P75, HIGH = (lv[:, k] for k in range(5))
    wmask = None if win is None else ((mod >= win[0]) & (mod < win[1]))
    trades = []
    pos, entry_px, entry_i = 0, 0.0, -1
    stop_px = np.nan
    trend, sc = 0, 0
    lsi = {-1: -10**9, 1: -10**9}
    pe, px_ = 0, False

    def ct(i, p, kind):
        nonlocal pos
        pnl1 = pos * (p - entry_px) * 20.0
        for _ in range(qty):
            trades.append({"entry_time": str(tt[entry_i]), "pnl": pnl1, "exit_kind": kind,
                           "hold_min": float((tt[i] - tt[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    for i in range(1, n):
        if px_ and pos != 0:
            ct(i, opn[i], "rule"); px_ = False
        if pe != 0 and pos == 0:
            pos = pe; entry_px, entry_i = opn[i], i
            stop_px = entry_px - stop_pts if pos > 0 else entry_px + stop_pts
        pe = 0
        if pos != 0:
            if pos > 0 and low[i] <= stop_px:
                ct(i, opn[i] if opn[i] <= stop_px else stop_px, "stop")
            elif pos < 0 and high[i] >= stop_px:
                ct(i, opn[i] if opn[i] >= stop_px else stop_px, "stop")
        if np.isnan(lv[i, 0]) or np.isnan(lv[i - 1, 0]):
            continue
        pt_ = trend
        if close[i] > HIGH[i]:
            trend = 1
        elif close[i] < LOW[i]:
            trend = -1
        if trend != pt_:
            sc = 0
        if last_bar[i]:
            if pos != 0:
                ct(i, close[i], "sc")
            px_ = False; pe = 0
            continue
        # forced flat outside window
        if wmask is not None and pos != 0 and not wmask[i]:
            px_ = True
            continue
        rng = high[i] - low[i]
        sig = 0
        if sig_mode == "SIG1":
            if trend > 0 and close[i - 1] > HIGH[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
                sig = 1
            elif trend < 0 and close[i - 1] < LOW[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
                sig = -1
        else:
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
            else:
                hit = sig == -pos
            if hit:
                px_ = True
                continue
        if pos == 0 and sig != 0 and sc < max_sig and (i - lsi[sig]) >= split:
            if wmask is None or wmask[i]:
                pe = sig; sc += 1; lsi[sig] = i
    return trades


def wstats(trades, d0, d1):
    lo = np.datetime64(pd.Timestamp(d0) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
    hi = np.datetime64(pd.Timestamp(d1)) + np.timedelta64(17, "h")
    wt = [x for x in trades if lo <= np.datetime64(x["entry_time"]) <= hi]
    if not wt:
        return None
    p = np.array([x["pnl"] for x in wt])
    w = p > 0
    gl = p[~w].sum()
    return {"n": len(wt), "net": round(float(p.sum())), "wr": round(float(w.mean() * 100), 1),
            "pf": round(float(p[w].sum() / -gl), 2) if gl < 0 else None,
            "hold": round(float(np.mean([x["hold_min"] for x in wt])), 1),
            "LL": round(float(p.min())), "n2600": int(np.sum(np.isclose(p, -2600, atol=0.5))),
            "n1300": int(np.sum(np.isclose(p, -1300, atol=0.5)))}


def num(s):
    import re
    if not s: return None
    m = re.search(r"-?[\d,]+(?:\.\d+)?", str(s).replace("(", "-").replace(")", ""))
    return float(m.group().replace(",", "")) if m else None


cells = []
for sm in ("SIG1", "SIG2"):
    for xr in ("X_FLIP", "X_MED", "X_OPP"):
        for stop_pts, qty, sname in ((130.0, 1, "S130x1"), (65.0, 2, "S65x2")):
            for wname, win in WINDOWS.items():
                trades = run_vf(BARS, sm, xr, stop_pts, qty, win)
                errs = []
                per = {}
                for r in tgt:
                    s = wstats(trades, r["report_start"], r["report_end"])
                    per[r["report_end"]] = s
                    tn, th = num(r["trades_all"]), num(r["avg_time_min_all"])
                    tw = num(r["wr_all"])
                    if s and tn:
                        errs.append(abs(s["n"] - tn) / tn + (abs(s["hold"] - th) / th if th else 0)
                                    + (abs(s["wr"] - tw) / 25 if tw else 0))
                    else:
                        errs.append(3.0)
                score = round(float(np.mean(errs)), 3)
                cells.append({"cell": f"{sm}|{xr}|{sname}|{wname}", "score": score,
                              "total_trades": len(trades), "per": per})
                print(f"[R3] {sm}|{xr}|{sname}|{wname:9s} score={score:6.3f} n={len(trades)}", flush=True)

cells.sort(key=lambda c: c["score"])
with open(os.path.join(OUT, "r3_grid.json"), "w") as f:
    json.dump(cells[:12], f, indent=1, default=str)
print("\nBEST CELLS:")
for c in cells[:5]:
    print(c["cell"], c["score"])
best = cells[0]
print("\nper-window best cell vs targets:")
for r in tgt:
    s = best["per"][r["report_end"]]
    print(f'  {r["report_start"]}->{r["report_end"]}: tgt n={r["trades_all"]} net={r["net_all"]} hold={r["avg_time_min_all"]} LL={r["largest_loss_all"]} | '
          f'sim {s}')
