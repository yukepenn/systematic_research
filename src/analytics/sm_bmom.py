"""sm_bmom.py — SYSTEM_MASTER re-implementation of the FROZEN W8-1 B-MOM rule.

Rule (frozen 2026-08-08 in scalping-lab W8, verbatim semantics):
  END-stamped 3-min RTH bars (stamps 09:33..16:00; the first RTH bar's open is
  the 09:30 open). Noise band: upper/lower = open0930 +/- m_tod, where m_tod =
  trailing 14-day mean of |close(slot) - open0930| for the SAME slot-of-day,
  prior days only. RTH-anchored VWAP = cum(close*volume)/cum(volume) including
  the current bar. LONG when close > max(upper, VWAP); SHORT when close <
  min(lower, VWAP); otherwise hold. Entries/flips on stamps 09:33..15:54 only;
  force-flat at the last RTH bar stamped <= 15:57. Fills at signal-bar close.
  1 NQ. C1 = 2.872 ticks/RT, C2 = 4.872. First 14 sessions excluded (band
  history); NaN-band decision bars take no signal. Sessions whose first RTH
  stamp is not 09:33 are dropped (W10 convention).

Purpose: certified generator for (a) NT8 master parity, (b) the single joint
holdout read. Reconciled against the committed W8 ledger before use.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TICK = 0.25
TICK_USD = 5.0
C1_TICKS = 2.872
C2_TICKS = 4.872
BAND_DAYS = 14


def rth_3m(bars3: pd.DataFrame) -> pd.DataFrame:
    """3-min bars (time end-stamped, sess_date column) -> RTH slice with slot ids."""
    t = pd.to_datetime(bars3["time"])
    hm = t.dt.hour * 100 + t.dt.minute
    m = (hm >= 933) & (hm <= 1600)
    out = bars3.loc[m].copy()
    out["hm"] = hm[m]
    out["date"] = t[m].dt.date
    return out


def bmom_trades(bars3: pd.DataFrame) -> pd.DataFrame:
    """Run frozen B-MOM on a 3-min bar frame (needs time/open/high/low/close/volume).
    Returns the trade ledger. Sessions keyed by calendar date of the RTH day."""
    r = rth_3m(bars3)
    days = []
    for d, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue  # W10 drop rule
        days.append((d, g))

    # per-slot trailing band history
    hist: dict[int, list[float]] = {}
    day_count = 0
    trades = []
    for d, g in days:
        open0930 = g["open"].iloc[0]
        close = g["close"].to_numpy()
        vol = g["volume"].to_numpy()
        hm = g["hm"].to_numpy()
        vwap = np.cumsum(close * vol) / np.maximum(np.cumsum(vol), 1e-9)

        pos = 0
        entry_px = np.nan
        entry_hm = None
        last_entry_ok = 1554
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None

        def book(exit_px, exit_hm, reason):
            nonlocal pos, entry_px, entry_hm
            pts = (exit_px - entry_px) * pos
            gross_t = pts / TICK
            trades.append({
                "sess": d, "side": "L" if pos > 0 else "S",
                "entry_hm": entry_hm, "exit_hm": exit_hm,
                "entry_px": entry_px, "exit_px": exit_px, "exit_reason": reason,
                "pts": pts, "gross_ticks": gross_t,
                "net_c1_ticks": gross_t - C1_TICKS, "net_c2_ticks": gross_t - C2_TICKS,
            })
            pos = 0; entry_px = np.nan; entry_hm = None

        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    if pos != 0:
                        book(close[i], h, "closeout")
                    break
                if h > 1554:
                    continue
                past = hist.get(h)
                if past is None or len(past) < 1:
                    continue
                m_tod = float(np.mean(past[-BAND_DAYS:]))
                upper, lower = open0930 + m_tod, open0930 - m_tod
                sig = 0
                if close[i] > max(upper, vwap[i]):
                    sig = 1
                elif close[i] < min(lower, vwap[i]):
                    sig = -1
                if sig != 0 and sig != pos:
                    if pos != 0:
                        book(close[i], h, "flip")
                    pos = sig
                    entry_px = close[i]
                    entry_hm = h
            else:
                # no flat bar hit inside loop (shouldn't happen on regular days)
                if pos != 0:
                    book(close[-1], int(hm[-1]), "closeout")

        # update band history AFTER trading the day (prior-days-only bands)
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close[i] - open0930))
        day_count += 1

    return pd.DataFrame(trades)


def bmom_daily(trades: pd.DataFrame, cost: str = "net_c1_ticks") -> pd.Series:
    d = trades.groupby("sess")[cost].sum() * TICK_USD
    d.index = pd.to_datetime(d.index)
    return d
