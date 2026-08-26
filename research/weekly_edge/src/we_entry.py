"""Entry-timing fill layer for W54. One function, three modes, all decision-bar causal.

The incumbent's convention, which everything here preserves: the object decides at bar i-1's
close (`pos_arr[i-1]`) and fills at bar i's OPEN. Nothing in this module may read bar i's
high, low or close to decide anything that fills on bar i.

modes
  delay=k        the flip is detected at bar i as usual, but the market entry moves to bar
                 i+k's open. The event survives only if the object still wants to be long
                 there; `lost` counts the flips that did not survive.
  limit_atr=d    a resting BUY is placed at (decision bar's close - d x lagged ATR), a level
                 fully known before bar i trades, valid for `valid` bars. It fills at the limit,
                 or at the bar's open on a gap-through (a buy that gaps below its limit fills
                 better, not worse). If it never fills and the object still wants to be long,
                 the entry happens AT MARKET at bar i+valid's open, so the event is NOT lost -
                 that is deliberate, because the unifying event-count law says losing events is
                 what damages the tail.
  force=True     D1 of the decomposition: take the delayed entry even if the object stopped
                 wanting to be long during the delay. Not tradeable; it exists only to separate
                 the PRICE effect from the EVENT-LOSS effect.
  skip_bars      D2 of the decomposition: refuse entry at these flip bars, original timing.
"""
from __future__ import annotations

import numpy as np

from run_we_w01 import PV, COMM_RT


def fills_entry_timed(D, pos_arr, size_at_entry, score, halt=1300.0, target=1000.0,
                      delay=0, limit_atr=None, atr=None, valid=30, force=False,
                      skip_bars=None):
    t, o, c, h, l = D["t"], D["o"], D["c"], D["h"], D["l"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    lost = 0                       # flips abandoned because the object turned flat first
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    pend = -1                      # bar at which the current pending entry was triggered
    plvl = np.nan                  # resting limit level, or nan for a pure delay
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
            if pend >= 0:
                lost += 1
            pend = -1; plvl = np.nan
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0

        # ---- 1. exits and new triggers at the OPEN ----------------------------------
        if u > 0 and want == 0:
            pnl = u * (o[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            spnl += pnl
            u = 0
            if spnl <= -halt or (target is not None and spnl >= target):
                stopped = True
                if pend >= 0:
                    lost += 1
                pend = -1; plvl = np.nan
        if u == 0 and pend < 0 and want > 0 and not stopped and not lb[i]:
            if skip_bars is not None and skip_bars[i]:
                pass                                   # D2: this flip is dropped
            else:
                pend = i
                plvl = (c[i - 1] - float(limit_atr) * float(atr[i])) \
                    if (limit_atr is not None and i > 0) else np.nan

        # ---- 2. the pending entry ----------------------------------------------------
        if pend >= 0 and u == 0:
            alive = (want > 0) or force
            if not alive:
                lost += 1
                pend = -1; plvl = np.nan
            else:
                fill_px = None
                if np.isfinite(plvl):
                    if i > pend and l[i] <= plvl:      # resting buy, level known before bar i
                        fill_px = min(o[i], plvl)      # gap-through fills better
                    elif i - pend >= valid:            # never touched -> market, event kept
                        fill_px = o[i]
                elif i - pend >= delay:
                    fill_px = o[i]
                if fill_px is not None and not lb[i]:
                    u = int(size_at_entry[i])
                    if u < 1:
                        u = 0
                    else:
                        epx, eti = float(fill_px), i
                    pend = -1; plvl = np.nan
                elif lb[i]:
                    lost += 1
                    pend = -1; plvl = np.nan

        # ---- 3. forced flat at the session's last bar --------------------------------
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
        if lb[i]:
            if pend >= 0:
                lost += 1
            pend = -1; plvl = np.nan
    return trades, lost
