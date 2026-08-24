"""Track-V PROXY engine: 60-min anchored volume-percentile ladder + EMA20 trend.

PROXY: volume is assigned to the 1m bar's close price (bid/ask real volume unavailable).
Causal: ladder values at bar i use volume accumulated through bar i within the current
clock-hour anchor. Percentiles undefined (NaN) until >=5 bars in the anchor.
"""
from __future__ import annotations

import numpy as np

POINT_VALUE = 20.0
TICK = 0.25
PCTS = (5, 25, 50, 75, 95)


def ema(x: np.ndarray, period: int) -> np.ndarray:
    a = 2.0 / (period + 1.0)
    out = np.empty_like(x, dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def ladder_series(time_arr, close, volume):
    """Per-bar percentile ladder of the running anchored volume-at-price histogram."""
    n = len(close)
    hours = time_arr.astype("datetime64[h]")
    lad = np.full((n, len(PCTS)), np.nan)
    hist = {}
    bars_in_anchor = 0
    cur_hour = None
    for i in range(n):
        h = hours[i]
        if h != cur_hour:
            cur_hour = h
            hist = {}
            bars_in_anchor = 0
        p = round(close[i] / TICK) * TICK
        hist[p] = hist.get(p, 0.0) + volume[i]
        bars_in_anchor += 1
        if bars_in_anchor >= 5:
            prices = sorted(hist)
            vols = np.array([hist[q] for q in prices])
            cum = np.cumsum(vols) / vols.sum()
            for k, pc in enumerate(PCTS):
                j = int(np.searchsorted(cum, pc / 100.0))
                lad[i, k] = prices[min(j, len(prices) - 1)]
    return lad


def run_v_proxy(bars, entry_family="M_BRK", trend_def="T_LVL", exit_rule="X_MED",
                entry_time_mask=None, comm_side=0.0,
                max_sig_per_trend=3, split_bars=5):
    n = bars["n"]
    close, opn = bars["close"], bars["open"]
    time_arr = bars["time"]
    last_bar = bars["last_bar"]
    lad = bars["ladder"]
    e20 = bars["ema20"]
    P5, P25, P50, P75, P95 = (lad[:, k] for k in range(5))

    if trend_def == "T_LVL":
        up = close > e20
    else:
        up = np.concatenate([[False] * 5, e20[5:] > e20[:-5]])

    mod = ((time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    entry_ok = entry_time_mask(mod) if entry_time_mask is not None else np.ones(n, bool)

    trades = []
    pos, entry_px, entry_i = 0, 0.0, -1
    sig_count = 0
    last_sig_i = -10**9
    trend_now = None
    pend_entry, pend_exit = 0, False

    def close_trade(i, px, kind):
        nonlocal pos
        pnl = pos * (px - entry_px) * POINT_VALUE - 2 * comm_side
        trades.append({"dir": pos, "entry_i": entry_i, "exit_i": i,
                       "entry_time": str(time_arr[entry_i]), "exit_time": str(time_arr[i]),
                       "entry_px": entry_px, "exit_px": px, "pnl": pnl, "exit_kind": kind,
                       "hold_min": float((time_arr[i] - time_arr[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    for i in range(1, n):
        if pend_exit and pos != 0:
            close_trade(i, opn[i], "rule")
            pend_exit = False
        if pend_entry != 0 and pos == 0:
            pos = pend_entry
            entry_px, entry_i = opn[i], i
        pend_entry = 0

        t_now = bool(up[i])
        if trend_now is None or t_now != trend_now:
            trend_now = t_now
            sig_count = 0

        if last_bar[i]:
            if pos != 0:
                close_trade(i, close[i], "session_close")
            pend_exit = False
            pend_entry = 0
            continue

        if np.isnan(lad[i, 0]) or np.isnan(lad[i - 1, 0]):
            continue

        # exits first (early return)
        if pos != 0:
            if exit_rule == "X_MED":
                hit = (pos > 0 and close[i] < P50[i]) or (pos < 0 and close[i] > P50[i])
            else:  # X_OPP: profit-take at the extreme band in trade direction, stop at opposite extreme
                hit = ((pos > 0 and (close[i] >= P95[i] or close[i] <= P5[i])) or
                       (pos < 0 and (close[i] <= P5[i] or close[i] >= P95[i])))
            if hit:
                pend_exit = True
                continue

        # entries
        if pos == 0 and entry_ok[i] and sig_count < max_sig_per_trend and (i - last_sig_i) >= split_bars:
            sig = 0
            if entry_family == "M_BRK":
                if t_now and close[i - 1] <= P75[i - 1] and close[i] > P75[i]:
                    sig = 1
                elif (not t_now) and close[i - 1] >= P25[i - 1] and close[i] < P25[i]:
                    sig = -1
            else:  # M_REV
                if t_now and close[i - 1] >= P25[i - 1] and close[i] < P25[i]:
                    sig = 1
                elif (not t_now) and close[i - 1] <= P75[i - 1] and close[i] > P75[i]:
                    sig = -1
            if sig != 0:
                pend_entry = sig
                sig_count += 1
                last_sig_i = i
    return trades
