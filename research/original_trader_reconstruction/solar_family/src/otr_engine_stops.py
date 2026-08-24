"""Stop-group extension of the certified OTR engine (R2). New module; base engine untouched.

Adds NT8-style intrabar protective stops to the bar-close decision loop:
- initial stop: fixed points from entry px; checked intrabar every bar including the
  entry-fill bar (after the fill); fills AT the stop price, or at the bar's open if
  the open gaps through the stop.
- trailing stop: trail_pts behind the best favorable extreme since entry ('extreme')
  or behind entry ('entry'); optional activation after +activation_pts of favorable
  excursion. The tighter of initial/trailing governs once active.
Engine exit conventions (TS-line touch at close, flips, session close) still apply.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from otr_engine import POINT_VALUE, BARS_REQUIRED, WrapperPolicy


@dataclass
class StopCfg:
    initial_pts: Optional[float] = None
    trail_pts: Optional[float] = None
    trail_mode: str = "extreme"          # 'extreme' | 'entry'
    activation_pts: float = 0.0          # favorable excursion required to arm trail


def run_wrapper_stops(bars: dict, pol: WrapperPolicy, sc: StopCfg) -> dict:
    n = bars["n"]
    st = bars["signal_trade"]
    close, opn, high, low = bars["close"], bars["open"], bars["high"], bars["low"]
    last_bar, first_bar = bars["last_bar"], bars["first_bar"]
    time_arr = bars["time"]
    ts_arr = bars["trailing_stop"]

    trades = []
    pos = 0
    entry_px = 0.0
    entry_i = -1
    best = 0.0            # best favorable extreme since entry
    pend_entry = 0
    pend_exit = False
    pend_reverse = 0

    def close_trade(i_exit, px_exit, kind):
        nonlocal pos
        pnl = pos * (px_exit - entry_px) * POINT_VALUE - 2 * pol.comm_side
        trades.append({"dir": pos, "entry_i": entry_i, "exit_i": i_exit,
                       "entry_time": str(time_arr[entry_i]), "exit_time": str(time_arr[i_exit]),
                       "entry_px": entry_px, "exit_px": px_exit, "pnl": pnl, "exit_kind": kind,
                       "hold_min": float((time_arr[i_exit] - time_arr[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    def stop_level(i):
        """Current protective stop level, or None."""
        if pos == 0:
            return None
        lvls = []
        if sc.initial_pts is not None:
            lvls.append(entry_px - pos * sc.initial_pts)
        if sc.trail_pts is not None:
            ref = best if sc.trail_mode == "extreme" else entry_px
            fav = (best - entry_px) * pos
            if fav >= sc.activation_pts:
                lvls.append(ref - pos * sc.trail_pts)
        if not lvls:
            return None
        return max(lvls) if pos > 0 else min(lvls)

    for i in range(n):
        if pend_exit and pos != 0:
            close_trade(i, opn[i], "flip")
            pend_exit = False
        if pend_reverse != 0:
            if pos != 0:
                close_trade(i, opn[i], "flip")
            pos = pend_reverse
            entry_px, entry_i = opn[i], i
            best = entry_px
            pend_reverse = 0
        if pend_entry != 0 and pos == 0:
            pos = pend_entry
            entry_px, entry_i = opn[i], i
            best = entry_px
            pend_entry = 0
        pend_entry = 0

        # --- intrabar protective stop on this bar ---
        if pos != 0:
            lvl = stop_level(i)
            if lvl is not None:
                hit = low[i] <= lvl if pos > 0 else high[i] >= lvl
                if hit:
                    gap = (opn[i] <= lvl) if pos > 0 else (opn[i] >= lvl)
                    close_trade(i, opn[i] if gap else lvl, "stop")
            if pos != 0:
                best = max(best, high[i]) if pos > 0 else min(best, low[i])

        sig = st[i]

        if last_bar[i]:
            if pos != 0:
                close_trade(i, close[i], "session_close")
            pend_exit = False
            pend_entry = 0
            pend_reverse = 0
            continue

        if pos != 0:
            line = ts_arr[i]
            if not np.isnan(line):
                hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
                if hit:
                    if pol.reverse_on_flip and sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED:
                        pend_reverse = sig
                    else:
                        pend_exit = True
                    continue

        if pos == 0 and sig != 0 and i >= BARS_REQUIRED:
            if abs(sig) in pol.entry_types:
                pend_entry = 1 if sig > 0 else -1

    return trades
