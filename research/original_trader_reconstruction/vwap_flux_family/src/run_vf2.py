"""OTR_VF2: Flux pullback entries + intrabar 130-pt stop + run-letting exits."""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_vf1 import ema, layer_levels, slice_fp, dscore, TA  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_VF2_STOP130", "out")
os.makedirs(OUT, exist_ok=True)
STOP_PTS = 130.0


def run_vf2(bars, trend_def="T_B", exit_rule="Y2", max_sig=3, split=5, close_thr=0.10):
    n = bars["n"]
    close, opn, high, low = bars["close"], bars["open"], bars["high"], bars["low"]
    t = bars["time"]
    last_bar = bars["last_bar"]
    lv = bars["levels"]
    e20 = bars["ema20"]
    LOW, P25, MED, P75, HIGH = (lv[:, k] for k in range(5))

    trades = []
    pos, entry_px, entry_i = 0, 0.0, -1
    stop_px = np.nan
    trend = 0
    sig_count = 0
    last_sig_i = {-1: -10**9, 1: -10**9}
    pend_e, pend_x = 0, False

    def close_trade(i, px, kind):
        nonlocal pos
        pnl = pos * (px - entry_px) * 20.0
        trades.append({"dir": pos, "entry_time": str(t[entry_i]), "exit_time": str(t[i]),
                       "entry_px": entry_px, "exit_px": px, "pnl": pnl, "exit_kind": kind,
                       "hold_min": float((t[i] - t[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    for i in range(1, n):
        # fills from previous bar decisions
        if pend_x and pos != 0:
            close_trade(i, opn[i], "rule")
            pend_x = False
        if pend_e != 0 and pos == 0:
            pos = pend_e
            entry_px, entry_i = opn[i], i
            stop_px = entry_px - STOP_PTS if pos > 0 else entry_px + STOP_PTS
        pend_e = 0

        # intrabar protective stop (checked on every bar while in position, incl. entry bar)
        if pos != 0:
            if pos > 0 and low[i] <= stop_px:
                close_trade(i, min(opn[i], stop_px) if opn[i] <= stop_px else stop_px, "stop130")
                pend_x = False
            elif pos < 0 and high[i] >= stop_px:
                close_trade(i, max(opn[i], stop_px) if opn[i] >= stop_px else stop_px, "stop130")
                pend_x = False

        if np.isnan(lv[i, 0]) or np.isnan(lv[i - 1, 0]):
            continue

        prev_trend = trend
        if trend_def == "T_B":
            if close[i] > HIGH[i]:
                trend = 1
            elif close[i] < LOW[i]:
                trend = -1
        else:
            if e20[i] > MED[i] and close[i] > MED[i]:
                trend = 1
            elif e20[i] < MED[i] and close[i] < MED[i]:
                trend = -1
        if trend != prev_trend:
            sig_count = 0

        if last_bar[i]:
            if pos != 0:
                close_trade(i, close[i], "session_close")
            pend_x = False
            pend_e = 0
            continue

        # detect Flux pullback signal this bar (used for entries and Y1 exits)
        sig = 0
        rng = high[i] - low[i]
        if trend > 0 and close[i - 1] > HIGH[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
            if rng <= 0 or (high[i] - close[i]) / rng >= close_thr:
                sig = 1
        elif trend < 0 and close[i - 1] < LOW[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
            if rng <= 0 or (close[i] - low[i]) / rng >= close_thr:
                sig = -1

        # close-based exits
        if pos != 0:
            if exit_rule == "Y1":
                hit = sig == -pos
            elif exit_rule == "Y2":
                hit = (pos > 0 and close[i] < LOW[i]) or (pos < 0 and close[i] > HIGH[i])
            else:  # Y3
                hit = (pos > 0 and close[i] > HIGH[i]) or (pos < 0 and close[i] < LOW[i])
            if hit:
                pend_x = True
                continue

        # entries
        if pos == 0 and sig != 0 and sig_count < max_sig and (i - last_sig_i[sig]) >= split:
            pend_e = sig
            sig_count += 1
            last_sig_i[sig] = i
    return trades


print("[VF2] loading ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= "2026-02-20") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
t = df["time"].values.astype("datetime64[s]")
fb = np.zeros(len(df), bool); fb[0] = True
fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
lb = np.zeros(len(df), bool); lb[:-1] = fb[1:]; lb[-1] = True
lv = layer_levels(t, df["close"].values, df["volume"].values, mode="L_C")
bars = {"n": len(df), "time": t, "open": df["open"].values, "high": df["high"].values,
        "low": df["low"].values, "close": df["close"].values, "last_bar": lb,
        "levels": lv, "ema20": ema(df["close"].values, 20)}

SEC = [("W20260308", "2026-03-08", "2026-03-13"), ("W20260322", "2026-03-22", "2026-03-27"),
       ("W20260419", "2026-04-19", "2026-04-24")]
results = []
for td in ("T_B", "T_A"):
    for xr in ("Y1", "Y2", "Y3"):
        cid = f"L_C|{td}|{xr}|stop130"
        trades = run_vf2(bars, trend_def=td, exit_rule=xr)
        fpA = slice_fp(trades, "2026-05-10", "2026-05-22", 10)
        D = dscore(fpA)
        sec = {w[0]: slice_fp(trades, w[1], w[2], 5) for w in SEC}
        nstops = sum(1 for x in trades if x["exit_kind"] == "stop130")
        results.append({"cell": cid, "D": D, "windowA": fpA, "secondary": sec, "stop_exits_total": nstops})
        print(f"[VF2] {cid:22s} D={D:8.3f} A: n={fpA.get('trades',0):4d} net={fpA.get('net',0):8.0f} "
              f"WR={fpA.get('win_rate_pct',0):6.2f} PF={fpA.get('pf')} hold={fpA.get('avg_hold_min',0)} "
              f"aw={fpA.get('avg_win')} al={fpA.get('avg_loss')} worst={fpA.get('largest_loss')} tail={fpA.get('loss_tail')}", flush=True)

results.sort(key=lambda r: r["D"])
json.dump({"targetA": TA, "results": results}, open(os.path.join(OUT, "sweep_results.json"), "w"), indent=1)
with open(os.path.join(OUT, "scorecard.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell", "D", "A_trades", "A_net", "A_wr", "A_pf", "A_hold", "A_avg_win", "A_avg_loss", "A_dd", "A_worst"])
    for r in results:
        a = r["windowA"]
        w.writerow([r["cell"], r["D"], a.get("trades"), a.get("net"), a.get("win_rate_pct"), a.get("pf"),
                    a.get("avg_hold_min"), a.get("avg_win"), a.get("avg_loss"), a.get("max_dd"), a.get("largest_loss")])
print("[VF2] best:", results[0]["cell"], results[0]["D"], flush=True)
print("[VF2] best secondary:", json.dumps(results[0]["secondary"]), flush=True)
