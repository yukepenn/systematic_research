"""
sm01_solarsim.py — SYSTEM_MASTER canonical pure-Python Solar member + E10 simulator.

Replicates, from 3-minute bars alone, the exact NT8 behavior of the 13 R5-E10
members (SolarWaveOpenV3, StartUp=false, ThresholdMode=1, VolPeriod=460,
clamp [40,1200] ticks, VolMult k, EntrySignalType=1, ExitMultiplier=0,
UseTimeFilter=false, BarsRequiredToTrade=20, exit-on-session-close, slip 1 tick,
Lifetime $2.18/side NQ) and the E10 aggregation
(target = round(10 * mean member pos) clamped +/-10 MNQ, net-change fills at
next bar open, 1 tick slip per contract, $0.65/side MNQ).

Parity gates (runs/SM01_SUBSTRATE/spec.yaml):
  GATE_A per-bar member positions vs runs/E10MASTER_V1/out/e10m_v1_bars.csv
  GATE_B fills vs runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__*.csv
  GATE_C daily E10 net vs runs/E10MASTER_V2/out/daily_v1_v2.csv net_v1

Conventions replicated (verified against src/ninjascript/SolarWaveOpenV3.cs and
SolarWaveE10Master_v2.cs, both transplanted-verbatim V3 arithmetic):
  - OnBarClose: state updated on every bar close (UpdateVol FIRST, so sigma at a
    flip bar includes that bar's |dClose|); orders decided on bar t fill at bar
    t+1 OPEN with 1-tick adverse slippage capped by the fill bar's range;
    session-close exits fill AT the session's last bar CLOSE (same cap rule).
  - sigma_t = NaN for t < 30, else mean(|dClose| over last min(t,460) diffs).
  - S = clamp(k * sigma, 40*0.25, 1200*0.25); fallback 179*0.25 when sigma NaN;
    S resampled ONLY at trend flips (and at bar 0 seed).
  - Flip: strict close cross of anchor -/+ S. Anchor = running close extreme.
  - Trading: entry only when flat AND Type-1 flip on this bar (EST=1);
    exit when (long and close <= anchor - S | trend flipped down) or mirror;
    exit and entry never both submitted on the same bar (exit returns first);
    no orders before CurrentBar 20; StartUp=false.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TICK = 0.25
NQ_TICK_VALUE = 5.0
NQ_POINT_VALUE = 20.0
NQ_COMM_SIDE = 2.18
MNQ_POINT_VALUE = 2.0
MNQ_COMM_SIDE = 0.65
VMS = list(range(6, 31, 2))  # 13 members


# ---------------------------------------------------------------- data loading

def load_bars_3m(path="runs/AUDIT03_BARS/nq_3m_2022_2026.csv") -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    df["time"] = pd.to_datetime(df["time"])
    df = df.reset_index(drop=True)
    df["sess_id"] = df["first_bar_of_session"].cumsum()
    # session date = date of the 17:00 close = date of the LAST bar of the session
    last_time = df.groupby("sess_id")["time"].transform("max")
    df["sess_date"] = last_time.dt.date
    df["is_last_of_sess"] = df["time"].eq(last_time)
    return df


def resample_3m(df1m: pd.DataFrame) -> pd.DataFrame:
    """1-min END-stamped bars -> 3-min END-stamped bars (bucket end = ceil(t/3min)),
    with NT8-style session ids (18:00 ET roll; handles pre-2012 early closes by
    keying sessions on >=17:00 gaps)."""
    t = pd.to_datetime(df1m["time"])
    end = t.dt.ceil("3min")
    g = df1m.groupby(end)
    out = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(),
        "volume": g["volume"].sum(),
    })
    out.index.name = "time"
    out = out.reset_index()
    gap = out["time"].diff() > pd.Timedelta(hours=1)
    out["first_bar_of_session"] = gap | (out.index == 0)
    out["sess_id"] = out["first_bar_of_session"].cumsum()
    last_time = out.groupby("sess_id")["time"].transform("max")
    out["sess_date"] = last_time.dt.date
    out["is_last_of_sess"] = out["time"].eq(last_time)
    return out


# ------------------------------------------------------------- state machines

def sigma_series(close: np.ndarray, vol_period: int = 460,
                 min_count: int = 30) -> np.ndarray:
    """Exact V3 CausalSigma per bar (value as of that bar's close)."""
    n = close.size
    d = np.abs(np.diff(close, prepend=close[0]))
    d[0] = 0.0
    csum = np.cumsum(d)
    sig = np.full(n, np.nan)
    t = np.arange(n)
    # volCount at bar t equals t (increments from bar 1)
    expanding = t.astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        exp_mean = csum / np.where(expanding > 0, expanding, np.nan)
    roll = np.full(n, np.nan)
    if n > vol_period:
        rs = csum[vol_period:] - csum[:-vol_period]
        roll[vol_period:] = rs / vol_period
    sig = np.where(t <= vol_period, exp_mean, roll)
    sig[t < min_count] = np.nan
    return sig


def member_states(close: np.ndarray, sigma: np.ndarray, vol_mult: float,
                  stop_mult_ticks: float = 179.0, smin_ticks: float = 40.0,
                  smax_ticks: float = 1200.0, start_up: bool = False):
    """V3 state machine (AnchorMode 0, ThresholdMode 1). Returns
    (is_up, flip, s_eff, anchor) arrays; flip in {0, +1, -1} on trend-start bars."""
    n = close.size
    lo, hi = smin_ticks * TICK, smax_ticks * TICK
    fallback = stop_mult_ticks * TICK

    def resolve_s(t):
        s = sigma[t]
        if not np.isfinite(s) or s <= 0:
            return fallback
        return min(max(vol_mult * s, lo), hi)

    is_up = np.zeros(n, dtype=bool)
    flip = np.zeros(n, dtype=np.int8)
    s_eff = np.empty(n)
    anchor_out = np.empty(n)

    up = bool(start_up)
    anchor = close[0]
    S = resolve_s(0)
    is_up[0] = up; s_eff[0] = S; anchor_out[0] = anchor

    for t in range(1, n):
        px = close[t]
        if up:
            if px >= anchor:
                anchor = px
            elif px < anchor - S:
                up = False
                S = resolve_s(t)
                anchor = px
                flip[t] = -1
        else:
            if px <= anchor:
                anchor = px
            elif px > anchor + S:
                up = True
                S = resolve_s(t)
                anchor = px
                flip[t] = 1
        is_up[t] = up; s_eff[t] = S; anchor_out[t] = anchor
    return is_up, flip, s_eff, anchor_out


# ------------------------------------------------------------------ execution

def _fill(open_, high, low, side, at_close=None):
    """1-tick adverse slip capped by the fill bar's range. side=+1 buy, -1 sell."""
    base = at_close if at_close is not None else open_
    px = base + side * TICK
    return min(px, high) if side > 0 else max(px, low)


def member_trades(bars: pd.DataFrame, is_up, flip, s_eff, anchor,
                  bars_required: int = 20,
                  comm_side: float = NQ_COMM_SIDE,
                  point_value: float = NQ_POINT_VALUE) -> tuple[pd.DataFrame, np.ndarray]:
    """Simulate the V3 trading layer for one member. Returns (fills, pos)
    where pos[t] = position held at bar t's close (+1/0/-1)."""
    n = len(bars)
    close = bars["close"].to_numpy()
    open_ = bars["open"].to_numpy()
    high = bars["high"].to_numpy()
    low = bars["low"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    times = bars["time"].to_numpy()

    pos = np.zeros(n, dtype=np.int8)
    pend_pos = np.zeros(n, dtype=np.int8)  # position after NEXT bar's open fills
    fills = []  # (bar, time, name, action, price, pos_after)
    p = 0
    pending = 0  # order to execute at next bar open: +1 enter long, -1 enter short,
                 # +2 exit short (buy to cover), -2 exit long (sell)

    for t in range(n):
        # 1. execute pending order at this bar's open
        if pending != 0:
            if pending == 1:
                px = _fill(open_[t], high[t], low[t], +1)
                p = 1
                fills.append((t, times[t], "Long", "Buy", px, p))
            elif pending == -1:
                px = _fill(open_[t], high[t], low[t], -1)
                p = -1
                fills.append((t, times[t], "Short", "SellShort", px, p))
            elif pending == -2:
                px = _fill(open_[t], high[t], low[t], -1)
                p = 0
                fills.append((t, times[t], "L-SolarExit", "Sell", px, p))
            elif pending == 2:
                px = _fill(open_[t], high[t], low[t], +1)
                p = 0
                fills.append((t, times[t], "S-SolarExit", "BuyToCover", px, p))
            pending = 0

        # 2. OnBarClose decision on this bar
        if t >= bars_required:
            xl = anchor[t] - s_eff[t] if is_up[t] else anchor[t] + s_eff[t]
            decided = False
            if p == 1 and close[t] <= xl:
                pending = -2; decided = True
            elif p == -1 and close[t] >= xl:
                pending = 2; decided = True
            # NT8 drops market entries submitted on the session's last bar
            # (verified: 2025-06-05 17:00 down-flip produced no 18:03 fill).
            if not decided and p == 0 and flip[t] != 0 and not last_of_sess[t]:
                pending = 1 if flip[t] > 0 else -1

        # 3. session close: flatten AT this bar's close; cancel pending exits
        #    (position is gone) but keep pending entries? NT8 semantics resolved
        #    by parity: orders submitted on the last bar fill at next session open.
        if last_of_sess[t] and p != 0:
            side = -1 if p == 1 else +1
            px = _fill(open_[t], high[t], low[t], side, at_close=close[t])
            fills.append((t, times[t], "Exit on session close",
                          "Sell" if p == 1 else "BuyToCover", px, 0))
            p = 0
            if pending in (-2, 2):
                pending = 0
        pos[t] = p
        if pending == 1:
            pend_pos[t] = 1
        elif pending == -1:
            pend_pos[t] = -1
        elif pending in (2, -2):
            pend_pos[t] = 0
        else:
            pend_pos[t] = p

    f = pd.DataFrame(fills, columns=["bar", "time", "name", "order_action",
                                     "price", "pos_after"])
    f["commission"] = comm_side  # per side, qty 1
    return f, pos, pend_pos




def fills_to_trades(fills: pd.DataFrame,
                    point_value: float = NQ_POINT_VALUE,
                    comm_side: float = NQ_COMM_SIDE) -> pd.DataFrame:
    """Pair entry/exit fills into round-trip trades with net P&L."""
    rows = []
    entry = None
    for r in fills.itertuples():
        if r.name in ("Long", "Short"):
            entry = r
        elif entry is not None:
            side = 1 if entry.name == "Long" else -1
            pts = (r.price - entry.price) * side
            rows.append({
                "entry_bar": entry.bar, "exit_bar": r.bar,
                "entry_time": entry.time, "exit_time": r.time,
                "side": side, "entry_px": entry.price, "exit_px": r.price,
                "exit_reason": r.name, "points": pts,
                "net": pts * point_value - 2 * comm_side,
            })
            entry = None
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ E10 layer

def e10_target(member_pos: np.ndarray, mult: int = 10, cap: int = 10) -> np.ndarray:
    """member_pos: (n_bars, n_members) -> integer MNQ target per bar.
    round-half-away-from-zero(mult * mean), clamped to +/-cap (C# Math.Round
    MidpointRounding.AwayFromZero semantics assumed; parity-checked)."""
    m = member_pos.mean(axis=1) * mult
    tgt = np.sign(m) * np.floor(np.abs(m) + 0.5)
    return np.clip(tgt, -cap, cap).astype(int)


def e10_sim(bars: pd.DataFrame, tgt: np.ndarray,
             comm_side: float = MNQ_COMM_SIDE,
             point_value: float = MNQ_POINT_VALUE,
             flatten_1644: bool = False) -> pd.DataFrame:
    """Execute the E10 net-change layer: at bar t close compute tgt[t]; trade the
    difference at bar t+1 open (1 tick adverse slip per contract, capped);
    flatten at session close (fill at last bar close). Returns daily net by
    session date."""
    n = len(bars)
    open_ = bars["open"].to_numpy(); high = bars["high"].to_numpy()
    low = bars["low"].to_numpy(); close = bars["close"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    sess_date = bars["sess_date"].to_numpy()

    cash = 0.0
    p = 0
    daily = {}
    prev_equity = 0.0
    pend = 0

    for t in range(n):
        # execute pending net change at open
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(open_[t], high[t], low[t], side)
            cash -= d * px * point_value
            cash -= abs(d) * comm_side
            p = pend
        # session close flatten at close price
        if last_of_sess[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(open_[t], high[t], low[t], side, at_close=close[t])
            cash += p * px * point_value
            cash -= abs(p) * comm_side
            p = 0
            pend = 0
        else:
            pend = tgt[t]
        # mark equity at session end
        if last_of_sess[t]:
            eq = cash + p * close[t] * point_value
            daily[sess_date[t]] = eq - prev_equity
            prev_equity = eq
    return pd.DataFrame({"sess": list(daily.keys()), "net": list(daily.values())})
