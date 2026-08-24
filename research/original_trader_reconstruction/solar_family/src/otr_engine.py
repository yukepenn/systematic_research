"""OTR Track-S engine: NT8-convention trading loop over the canonical bar ledger.

Conventions certified against the frozen canonical Type-1 result (see
runs/OTR_S0_TYPE1_REPRO/spec.yaml):
  - decisions at bar close; market fills at NEXT bar open, slippage 0
  - exit checked before entry with early return (never share a bar)
  - position open at a session's last bar exits at that bar's CLOSE (session-close fill)
  - entries signaled on a session's last bar are dropped
  - no entries before bar index BARS_REQUIRED (NT8 BarsRequiredToTrade)
  - commission per side constant (NinjaTrader Brokerage Lifetime: $2.18/side NQ)

The wrapper-policy layer (S1..S6) plugs into run_wrapper() via a WrapperPolicy;
S0 uses the V0 baseline policy (EntrySignalType=1, opposite-flip exit).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

POINT_VALUE = 20.0
COMM_SIDE = 2.18
BARS_REQUIRED = 20


def load_ledger(path: str) -> dict:
    """Load t2_canonical_1m.csv (skips '# params' comment line)."""
    times, o, h, l, c, vol, fbos, st, wave = [], [], [], [], [], [], [], [], []
    with open(path, newline="") as f:
        rdr = csv.reader(f)
        header = None
        for row in rdr:
            if not row or row[0].startswith("#"):
                continue
            if header is None:
                header = row
                idx = {name: i for i, name in enumerate(row)}
                continue
            times.append(row[idx["time"]])
            o.append(float(row[idx["open"]]))
            h.append(float(row[idx["high"]]))
            l.append(float(row[idx["low"]]))
            c.append(float(row[idx["close"]]))
            vol.append(float(row[idx["volume"]]))
            fbos.append(int(row[idx["first_bar_of_session"]]))
            st.append(int(float(row[idx["signal_trade"]])))
            wave.append(int(float(row[idx["signal_wave"]])))
    n = len(times)
    time_arr = np.array(times, dtype="datetime64[s]")
    fbos_arr = np.array(fbos, dtype=bool)
    # last bar of session = bar before next first_bar_of_session (or EOF)
    last_bar = np.zeros(n, dtype=bool)
    last_bar[:-1] = fbos_arr[1:]
    last_bar[-1] = True
    session_id = np.cumsum(fbos_arr) - 1
    return {
        "time": time_arr,
        "open": np.array(o), "high": np.array(h), "low": np.array(l),
        "close": np.array(c), "volume": np.array(vol),
        "first_bar": fbos_arr, "last_bar": last_bar, "session_id": session_id,
        "signal_trade": np.array(st, dtype=np.int64),
        "signal_wave": np.array(wave, dtype=np.int64),
        "n": n,
    }


@dataclass
class WrapperPolicy:
    """Bounded wrapper hypothesis. Defaults = V0 canonical baseline (S0)."""
    name: str = "V0_EST1"
    # which signal_trade magnitudes may ENTER (when flat): subset of {1,2,3}
    entry_types: tuple = (1,)
    # event policies within a trend (evaluated on entry signals only):
    #   None = no limit; k = allow at most k entries per trend leg (trend = span between flips)
    max_entries_per_trend: Optional[int] = None
    # only allow T3 entry if a T2 fired earlier in the same trend
    t3_requires_t2: bool = False
    # only the FIRST pullback (T2) per trend may enter
    first_pullback_only: bool = False
    # reverse directly on opposite flip (stop-and-reverse) instead of exit-then-wait
    reverse_on_flip: bool = False
    # time selection: callable minutes_of_day(int array) -> bool array of allowed ENTRY times
    # (bar stamp = bar END time, ET). None = no time filter.
    entry_time_mask: Optional[Callable[[np.ndarray], np.ndarray]] = None
    # force-flat window: exit any open position when bar-end time enters the blocked zone
    flat_time_mask: Optional[Callable[[np.ndarray], np.ndarray]] = None
    long_enabled: bool = True
    short_enabled: bool = True
    comm_side: float = COMM_SIDE


def _minutes_of_day(time_arr: np.ndarray) -> np.ndarray:
    secs = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64)
    return (secs // 60).astype(np.int64)


def run_wrapper(bars: dict, pol: WrapperPolicy) -> dict:
    """Sequential single-contract loop under NT8 conventions. Returns trades + fingerprint."""
    n = bars["n"]
    st = bars["signal_trade"]
    close, opn = bars["close"], bars["open"]
    last_bar, first_bar = bars["last_bar"], bars["first_bar"]
    time_arr = bars["time"]
    mod = _minutes_of_day(time_arr)
    entry_ok_t = pol.entry_time_mask(mod) if pol.entry_time_mask is not None else np.ones(n, bool)
    flat_t = pol.flat_time_mask(mod) if pol.flat_time_mask is not None else np.zeros(n, bool)

    trades = []
    pos = 0            # -1/0/+1
    entry_px = 0.0
    entry_i = -1
    entries_this_trend = 0
    t2_seen_this_trend = False
    pend_entry = 0     # direction of market entry order to fill at next bar open
    pend_exit = False
    pend_reverse = 0   # direction to reverse into at next bar open

    def close_trade(i_exit: int, px_exit: float, kind: str):
        nonlocal pos, entry_px, entry_i
        pnl = pos * (px_exit - entry_px) * POINT_VALUE - 2 * pol.comm_side
        trades.append({
            "dir": pos, "entry_i": entry_i, "exit_i": i_exit,
            "entry_time": str(time_arr[entry_i]), "exit_time": str(time_arr[i_exit]),
            "entry_px": entry_px, "exit_px": px_exit, "pnl": pnl, "exit_kind": kind,
            "hold_min": float((time_arr[i_exit] - time_arr[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0,
        })
        pos = 0

    for i in range(n):
        # --- fills from orders submitted at previous bar close ---
        if pend_exit and pos != 0:
            close_trade(i, opn[i], "flip")
            pend_exit = False
        if pend_reverse != 0:
            if pos != 0:
                close_trade(i, opn[i], "flip")
            pos = pend_reverse
            entry_px, entry_i = opn[i], i
            pend_reverse = 0
        if pend_entry != 0 and pos == 0:
            pos = pend_entry
            entry_px, entry_i = opn[i], i
            pend_entry = 0
        pend_entry = 0  # unfilled entry orders do not persist

        sig = st[i]
        if sig == 1 or sig == -1:  # flip bar: new trend leg
            entries_this_trend = 0
            t2_seen_this_trend = False

        # --- decisions at this bar close ---
        # 1) session close: position open at session's last bar exits at its CLOSE
        if last_bar[i]:
            if pos != 0:
                close_trade(i, close[i], "session_close")
            pend_exit = False
            pend_entry = 0
            pend_reverse = 0
            continue

        # 1b) forced-flat time window
        if pos != 0 and flat_t[i]:
            pend_exit = True
            continue

        # 2) exit first, early return (no entry on same bar)
        if pos != 0 and sig == -pos and abs(sig) == 1:
            if pol.reverse_on_flip and (pol.long_enabled if sig > 0 else pol.short_enabled) \
               and entry_ok_t[i] and i >= BARS_REQUIRED:
                pend_reverse = sig
            else:
                pend_exit = True
            continue

        # 3) entry when flat
        if pos == 0 and sig != 0 and i >= BARS_REQUIRED and entry_ok_t[i]:
            mag = abs(sig)
            if mag not in pol.entry_types:
                continue
            if not (pol.long_enabled if sig > 0 else pol.short_enabled):
                continue
            if pol.max_entries_per_trend is not None and entries_this_trend >= pol.max_entries_per_trend:
                continue
            if mag == 3 and pol.t3_requires_t2 and not t2_seen_this_trend:
                continue
            if mag == 2:
                if pol.first_pullback_only and t2_seen_this_trend:
                    t2_seen_this_trend = True
                    continue
            pend_entry = 1 if sig > 0 else -1
            entries_this_trend += 1
        if abs(sig) == 2:
            t2_seen_this_trend = True

    return {"trades": trades, "fingerprint": fingerprint(trades, bars)}


def fingerprint(trades: list, bars: dict) -> dict:
    if not trades:
        return {"trades": 0}
    pnl = np.array([t["pnl"] for t in trades])
    dirs = np.array([t["dir"] for t in trades])
    holds = np.array([t["hold_min"] for t in trades])
    wins = pnl > 0
    gross_w = pnl[wins].sum() if wins.any() else 0.0
    gross_l = pnl[~wins].sum() if (~wins).any() else 0.0
    eq = np.cumsum(pnl)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    n_sessions = int(bars["first_bar"].sum())
    out = {
        "trades": len(trades),
        "net": round(float(pnl.sum()), 2),
        "pf": round(float(gross_w / -gross_l), 6) if gross_l < 0 else None,
        "win_rate_pct": round(float(wins.mean() * 100), 4),
        "max_dd": round(float(dd.min()), 2),
        "avg_trade": round(float(pnl.mean()), 2),
        "avg_win": round(float(pnl[wins].mean()), 2) if wins.any() else None,
        "avg_loss": round(float(pnl[~wins].mean()), 2) if (~wins).any() else None,
        "wl_ratio": round(float(pnl[wins].mean() / -pnl[~wins].mean()), 3) if wins.any() and (~wins).any() else None,
        "avg_hold_min": round(float(holds.mean()), 2),
        "trades_per_day": round(len(trades) / n_sessions, 3),
        "largest_win": round(float(pnl.max()), 2),
        "largest_loss": round(float(pnl.min()), 2),
        "long_trades": int((dirs > 0).sum()),
        "short_trades": int((dirs < 0).sum()),
        "long_net": round(float(pnl[dirs > 0].sum()), 2),
        "short_net": round(float(pnl[dirs < 0].sum()), 2),
        "commission_total": round(2 * COMM_SIDE * len(trades), 2),
        "n_sessions": n_sessions,
    }
    return out
