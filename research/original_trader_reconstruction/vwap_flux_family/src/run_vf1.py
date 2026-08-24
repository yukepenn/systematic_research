"""OTR_VF1: documented VWAP Flux architecture, bounded interpretations (see spec)."""
import csv
import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_VF1_FLUX_ARCH", "out")
os.makedirs(OUT, exist_ok=True)

TA = {"trades": 183, "trades_per_day": 18.3, "win_rate_pct": 37.70, "pf": 0.95,
      "avg_hold_min": 39.84, "avg_win": 1236.16, "avg_loss": -783.77, "max_dd": -12700.0, "net": -4055.0}
SC = {"trades": 0.075 * 183, "trades_per_day": 0.075 * 18.3, "win_rate_pct": 2.0, "pf": 0.075,
      "avg_hold_min": 0.15 * 39.84, "avg_win": 0.15 * 1236.16, "avg_loss": 0.15 * 783.77,
      "max_dd": 0.20 * 12700.0, "net": 0.15 * 4055.0}
PRIM = ["trades", "trades_per_day", "win_rate_pct", "pf", "avg_hold_min", "avg_win", "avg_loss", "max_dd"]
LEVEL_PCTS = (5, 25, 50, 75, 95)  # Lowest..Highest


def ema(x, period):
    a = 2.0 / (period + 1.0)
    out = np.empty_like(x, dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def layer_levels(time_arr, close, volume, mode="L_C", amount=5):
    """Per-bar 5 levels from anchored 60-min VWAP layers."""
    n = len(close)
    hours = time_arr.astype("datetime64[h]")
    lv = np.full((n, 5), np.nan)
    completed = []          # list of layer VWAPs
    pv = 0.0
    v = 0.0
    cur = None
    for i in range(n):
        h = hours[i]
        if h != cur:
            if cur is not None and v > 0:
                completed.append(pv / v)
                if len(completed) > amount:
                    completed.pop(0)
            cur = h
            pv = 0.0
            v = 0.0
        pv += close[i] * volume[i]
        v += volume[i]
        if mode == "L_C":
            layers = completed[-amount:]
        else:  # L_E: current evolving + last (amount-1) completed
            layers = completed[-(amount - 1):] + ([pv / v] if v > 0 else [])
        if len(layers) >= amount:
            lo, hi = min(layers), max(layers)
            rng = hi - lo
            for k, pct in enumerate(LEVEL_PCTS):
                lv[i, k] = lo + pct / 100.0 * rng
    return lv


def run_vf(bars, trend_def="T_B", exit_rule="XA", loss_limit=None,
           max_sig=3, split=5, close_thr=0.10):
    n = bars["n"]
    close, opn, high, low = bars["close"], bars["open"], bars["high"], bars["low"]
    t = bars["time"]
    last_bar = bars["last_bar"]
    lv = bars["levels"]
    e20 = bars["ema20"]
    LOW, P25, MED, P75, HIGH = (lv[:, k] for k in range(5))

    trades = []
    pos, entry_px, entry_i = 0, 0.0, -1
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
        if pend_x and pos != 0:
            close_trade(i, opn[i], "rule")
            pend_x = False
        if pend_e != 0 and pos == 0:
            pos = pend_e
            entry_px, entry_i = opn[i], i
        pend_e = 0

        if np.isnan(lv[i, 0]) or np.isnan(lv[i - 1, 0]):
            continue

        # trend update
        prev_trend = trend
        if trend_def == "T_B":
            if close[i] > HIGH[i]:
                trend = 1
            elif close[i] < LOW[i]:
                trend = -1
        else:  # T_A
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

        # exits first
        if pos != 0:
            if loss_limit is not None and pos * (close[i] - entry_px) * 20.0 <= -loss_limit:
                pend_x = True
                continue
            if exit_rule in ("XA", "XC"):
                hit = (pos > 0 and close[i] < LOW[i]) or (pos < 0 and close[i] > HIGH[i])
            else:  # XB: profit at re-break beyond entry-side extreme OR trend-flip stop
                hit = ((pos > 0 and (close[i] > HIGH[i] or close[i] < LOW[i])) or
                       (pos < 0 and (close[i] < LOW[i] or close[i] > HIGH[i])))
            if hit:
                pend_x = True
                continue

        # entries: pullback INTO cloud with trend intact
        if pos == 0 and trend != 0 and sig_count < max_sig:
            rng = high[i] - low[i]
            sig = 0
            if trend > 0 and close[i - 1] > HIGH[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
                if rng <= 0 or (high[i] - close[i]) / rng >= close_thr:
                    sig = 1
            elif trend < 0 and close[i - 1] < LOW[i - 1] and LOW[i] <= close[i] <= HIGH[i]:
                if rng <= 0 or (close[i] - low[i]) / rng >= close_thr:
                    sig = -1
            if sig != 0 and (i - last_sig_i[sig]) >= split:
                pend_e = sig
                sig_count += 1
                last_sig_i[sig] = i
    return trades


def slice_fp(trades, d0, d1, ndays):
    lo = np.datetime64(d0) + np.timedelta64(18, "h")
    hi = np.datetime64(f"{d1}T17:00:00")
    wt = [x for x in trades if lo <= np.datetime64(x["entry_time"]) <= hi]
    if not wt:
        return {"trades": 0}
    pnl = np.array([x["pnl"] for x in wt])
    wins = pnl > 0
    gl = pnl[~wins].sum()
    eq = np.cumsum(pnl)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return {"trades": len(wt), "trades_per_day": round(len(wt) / ndays, 2),
            "net": round(float(pnl.sum()), 0), "win_rate_pct": round(float(wins.mean() * 100), 2),
            "pf": round(float(pnl[wins].sum() / -gl), 3) if gl < 0 else None,
            "avg_hold_min": round(float(np.mean([x["hold_min"] for x in wt])), 1),
            "avg_win": round(float(pnl[wins].mean()), 0) if wins.any() else None,
            "avg_loss": round(float(pnl[~wins].mean()), 0) if (~wins).any() else None,
            "max_dd": round(float(dd.min()), 0),
            "largest_loss": round(float(pnl.min()), 0),
            "loss_tail": sorted([round(float(x), 0) for x in pnl[pnl < 0]])[:5]}


def dscore(fp):
    errs = {k: (abs(fp.get(k) - TA[k]) / SC[k] if fp.get(k) is not None else 99.0) for k in PRIM + ["net"]}
    return round(float(np.mean([errs[k] for k in PRIM]) + 0.5 * errs["net"]), 3)


print("[VF1] loading parquet ...", flush=True)
df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= "2026-02-20") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
t = df["time"].values.astype("datetime64[s]")
fb = np.zeros(len(df), bool); fb[0] = True
fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
lb = np.zeros(len(df), bool); lb[:-1] = fb[1:]; lb[-1] = True
e20 = ema(df["close"].values, 20)
print("[VF1] layers ...", flush=True)
LEVELS = {m: layer_levels(t, df["close"].values, df["volume"].values, mode=m) for m in ("L_C", "L_E")}

SEC = [("W20260308", "2026-03-08", "2026-03-13"), ("W20260322", "2026-03-22", "2026-03-27"),
       ("W20260419", "2026-04-19", "2026-04-24")]
results = []
for lm in ("L_C", "L_E"):
    bars = {"n": len(df), "time": t, "open": df["open"].values, "high": df["high"].values,
            "low": df["low"].values, "close": df["close"].values, "last_bar": lb,
            "levels": LEVELS[lm], "ema20": e20}
    for td in ("T_B", "T_A"):
        for xr, ll in (("XA", None), ("XB", None), ("XC", 2500)):
            cid = f"{lm}|{td}|{xr}"
            trades = run_vf(bars, trend_def=td, exit_rule=("XA" if xr == "XC" else xr), loss_limit=ll)
            fpA = slice_fp(trades, "2026-05-10", "2026-05-22", 10)
            D = dscore(fpA)
            sec = {w[0]: slice_fp(trades, w[1], w[2], 5) for w in SEC}
            results.append({"cell": cid, "D": D, "windowA": fpA, "secondary": sec})
            print(f"[VF1] {cid:14s} D={D:8.3f} A: n={fpA.get('trades',0):4d} net={fpA.get('net',0):8.0f} "
                  f"WR={fpA.get('win_rate_pct',0):6.2f} PF={fpA.get('pf')} hold={fpA.get('avg_hold_min',0)} "
                  f"aw={fpA.get('avg_win')} al={fpA.get('avg_loss')} worst={fpA.get('largest_loss')}", flush=True)

results.sort(key=lambda r: r["D"])
json.dump({"targetA": TA, "results": results}, open(os.path.join(OUT, "sweep_results.json"), "w"), indent=1)
with open(os.path.join(OUT, "scorecard.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell", "D", "A_trades", "A_net", "A_wr", "A_pf", "A_hold", "A_avg_win", "A_avg_loss", "A_dd", "A_worst"])
    for r in results:
        a = r["windowA"]
        w.writerow([r["cell"], r["D"], a.get("trades"), a.get("net"), a.get("win_rate_pct"), a.get("pf"),
                    a.get("avg_hold_min"), a.get("avg_win"), a.get("avg_loss"), a.get("max_dd"), a.get("largest_loss")])
print("[VF1] best:", results[0]["cell"], results[0]["D"], flush=True)
print("[VF1] best secondary:", json.dumps(results[0]["secondary"]), flush=True)
