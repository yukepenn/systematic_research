"""
solarwave.py — open reference implementation of the RenkoKings Solar Wave RK indicator.

Derived by behavioural reverse engineering (no vendor-binary circumvention): the vendor
assembly's own per-bar output (research/01_diagnostics/sw01_bar_ledger.csv, 737,707 NQ
1-minute bars, 2023-01-02 -> 2025-01-31) was used as ground truth and the generating
recurrence was recovered exactly.

Validation (see research/03_reverse_engineering/SOLARWAVE_MATH.md):
    TrailingStop   100.000000%   exact tick-for-tick
    TrendVector    100.000000%   exact tick-for-tick
    Signal_Trend    99.9999%     (1 bar: the ledger's uninitialised first bar)
    Signal_Trade   100%          on Type 1 (all 5,405 trend starts)
    Signal_Wave     99.9736%
    Type 3          100% recall  (200 bars where a Type-2 pullback overwrites the plot slot)

The model has exactly ONE price state variable: `anchor`, the running extreme of the
CLOSE since the current trend began. Everything else is an affine offset of it or a
bar-counter on top of it. There is no moving average, no volatility estimate, no
smoothing and no lookback window anywhere in the core.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

# Signal_Trade alphabet (sign = direction: + long/up, - short/down)
TRADE_TREND_START = 1   # "Up"/"Down"  — the trend flipped on this bar
TRADE_PULLBACK    = 2   # "Pb"         — counter-trend excursion (see note below)
TRADE_STRENGTHEN  = 3   # "Str"        — trend resumed after a pause

# Signal_Trend alphabet: sign = direction, magnitude 2 = strong, 1 = weak (slowing)
TREND_STRONG = 2
TREND_WEAK   = 1


@dataclass
class SolarWaveParams:
    """Vendor parameter names, with the units recovered empirically.

    offset_multiplier_trend / offset_multiplier_stop are counts of TICKS, not
    multiples of any volatility measure. On NQ (tick = 0.25) the canonical
    179 => 44.75 index points; 90 => 22.50 points.
    """
    offset_multiplier_trend: float = 90.0   # TrendVector offset, in ticks
    offset_multiplier_stop: float = 179.0   # TrailingStop offset + reversal threshold, in ticks
    slowdown_scan: int = 5                  # bars without a new extreme => trend declared "weak"
    weak_weak_split: int = 10               # min bars between consecutive "weak" declarations
    pullback_early: bool = True             # (Type-2 only; not modelled here)
    pullback_split: int = 10                # (Type-2 only; not modelled here)
    tick_size: float = 0.25


@dataclass
class SolarWaveResult:
    trend_vector: np.ndarray
    trailing_stop: np.ndarray
    signal_trend: np.ndarray
    signal_trade: np.ndarray
    signal_wave: np.ndarray
    anchor: np.ndarray = field(default=None)
    is_up: np.ndarray = field(default=None)


def solar_wave(close, params: SolarWaveParams | None = None,
               start_up: bool = False) -> SolarWaveResult:
    """Compute the Solar Wave RK series from a close-price array.

    The recurrence, in full:

        S = offset_multiplier_stop  * tick_size      (reversal / stop distance)
        V = offset_multiplier_trend * tick_size      (early-warning distance)

        anchor_0 = close_0,  is_up_0 = start_up

        for each bar t > 0:
            if is_up:
                if close_t >= anchor:        anchor <- close_t            (extend)
                elif close_t <  anchor - S:  is_up <- False; anchor <- close_t   (FLIP)
            else:
                if close_t <= anchor:        anchor <- close_t            (extend)
                elif close_t >  anchor + S:  is_up <- True;  anchor <- close_t   (FLIP)

            TrailingStop_t = anchor -/+ S        (minus in an uptrend, plus in a downtrend)
            TrendVector_t  = anchor -/+ V

    Note the FLIP test is a STRICT inequality: touching the stop exactly does not
    reverse the trend; the close must trade through it. This was verified against
    4,682 bars where a non-strict rule diverges.

    `start_up` sets the initial trend. The vendor seeds this from its own warm-up;
    on a long series the state is self-correcting (the first flip erases it), so the
    choice only affects the leading bars.
    """
    p = params or SolarWaveParams()
    c = np.asarray(close, dtype=float)
    n = c.size
    S = p.offset_multiplier_stop * p.tick_size
    V = p.offset_multiplier_trend * p.tick_size

    trend_vector = np.empty(n)
    trailing_stop = np.empty(n)
    signal_trend = np.zeros(n, dtype=np.int8)
    signal_trade = np.zeros(n, dtype=np.int8)
    signal_wave = np.zeros(n, dtype=np.int16)
    anchor_out = np.empty(n)
    is_up_out = np.zeros(n, dtype=bool)

    is_up = bool(start_up)
    anchor = c[0]
    weak = False
    bars_since_extreme = 0
    next_weak_bar = -(1 << 60)
    wave = 1

    for t in range(n):
        px = c[t]
        event = 0                                   # 0 none, 1 new extreme, 2 flip
        if t > 0:
            if is_up:
                if px >= anchor:
                    if px > anchor:
                        event = 1
                    anchor = px
                elif px < anchor - S:
                    is_up, anchor, event = False, px, 2
            else:
                if px <= anchor:
                    if px < anchor:
                        event = 1
                    anchor = px
                elif px > anchor + S:
                    is_up, anchor, event = True, px, 2

        if event == 2:                              # --- trend flip: a new trend is born
            weak = False
            bars_since_extreme = 0
            wave = 1
            signal_trade[t] = TRADE_TREND_START if is_up else -TRADE_TREND_START
            next_weak_bar = t + p.weak_weak_split
        elif event == 1:                            # --- trend extended to a new extreme
            bars_since_extreme = 0
            if weak:                                # ...after a pause => a new wave leg
                wave += 1
                weak = False
                signal_trade[t] = TRADE_STRENGTHEN if is_up else -TRADE_STRENGTHEN
                next_weak_bar = t + p.weak_weak_split
        else:                                       # --- no progress this bar
            bars_since_extreme += 1
            if (not weak) and bars_since_extreme >= p.slowdown_scan and t >= next_weak_bar:
                weak = True
                next_weak_bar = t + p.weak_weak_split

        sign = 1 if is_up else -1
        trailing_stop[t] = anchor - S if is_up else anchor + S
        trend_vector[t] = anchor - V if is_up else anchor + V
        signal_trend[t] = sign * (TREND_WEAK if weak else TREND_STRONG)
        signal_wave[t] = sign * wave
        anchor_out[t] = anchor
        is_up_out[t] = is_up

    return SolarWaveResult(trend_vector, trailing_stop, signal_trend,
                           signal_trade, signal_wave, anchor_out, is_up_out)


def solar_wave_adaptive(close, vol, k_stop: float, k_trend_ratio: float = 90.0 / 179.0,
                        tick_size: float = 0.25, start_up: bool = False,
                        slowdown_scan: int = 5, weak_weak_split: int = 10) -> SolarWaveResult:
    """Volatility-normalised variant: the reversal distance becomes S_t = k_stop * vol_t
    instead of a constant tick count.

    The vendor indicator's offset is a FIXED number of ticks, so its effective
    aggressiveness drifts with both the price level and the volatility regime. `vol`
    should be a causal (lagged) volatility estimate in price units - e.g. ATR - with
    NO look-ahead. The stop distance is frozen for the life of each trend (sampled at
    the trend's birth bar) so that the trailing stop stays monotone, exactly as the
    fixed-offset version does.
    """
    c = np.asarray(close, dtype=float)
    v = np.asarray(vol, dtype=float)
    n = c.size
    trend_vector = np.empty(n); trailing_stop = np.empty(n)
    signal_trend = np.zeros(n, dtype=np.int8); signal_trade = np.zeros(n, dtype=np.int8)
    signal_wave = np.zeros(n, dtype=np.int16)
    anchor_out = np.empty(n); is_up_out = np.zeros(n, dtype=bool)

    is_up = bool(start_up); anchor = c[0]
    S = max(k_stop * (v[0] if np.isfinite(v[0]) else 0.0), tick_size)
    weak = False; bars_since_extreme = 0; next_weak_bar = -(1 << 60); wave = 1

    for t in range(n):
        px = c[t]
        event = 0
        if t > 0:
            if is_up:
                if px >= anchor:
                    if px > anchor: event = 1
                    anchor = px
                elif px < anchor - S:
                    is_up, anchor, event = False, px, 2
            else:
                if px <= anchor:
                    if px < anchor: event = 1
                    anchor = px
                elif px > anchor + S:
                    is_up, anchor, event = True, px, 2

        if event == 2:
            vt = v[t] if np.isfinite(v[t]) else 0.0
            S = max(k_stop * vt, tick_size)          # resample vol at trend birth only
            weak = False; bars_since_extreme = 0; wave = 1
            signal_trade[t] = TRADE_TREND_START if is_up else -TRADE_TREND_START
            next_weak_bar = t + weak_weak_split
        elif event == 1:
            bars_since_extreme = 0
            if weak:
                wave += 1; weak = False
                signal_trade[t] = TRADE_STRENGTHEN if is_up else -TRADE_STRENGTHEN
                next_weak_bar = t + weak_weak_split
        else:
            bars_since_extreme += 1
            if (not weak) and bars_since_extreme >= slowdown_scan and t >= next_weak_bar:
                weak = True; next_weak_bar = t + weak_weak_split

        sign = 1 if is_up else -1
        V = S * k_trend_ratio
        trailing_stop[t] = anchor - S if is_up else anchor + S
        trend_vector[t] = anchor - V if is_up else anchor + V
        signal_trend[t] = sign * (TREND_WEAK if weak else TREND_STRONG)
        signal_wave[t] = sign * wave
        anchor_out[t] = anchor; is_up_out[t] = is_up

    return SolarWaveResult(trend_vector, trailing_stop, signal_trend,
                           signal_trade, signal_wave, anchor_out, is_up_out)


if __name__ == "__main__":
    import sys, pandas as pd
    ledger = sys.argv[1] if len(sys.argv) > 1 else (
        r"research/01_diagnostics/sw01_bar_ledger.csv")
    df = pd.read_csv(ledger)
    r = solar_wave(df.close.to_numpy(), SolarWaveParams())
    def pct(a, b): return float(np.mean(a == b)) * 100.0
    print(f"bars                 : {len(df):,}")
    print(f"trailing_stop  exact : {np.mean(np.isclose(r.trailing_stop, df.trailing_stop))*100:.6f}%")
    print(f"trend_vector   exact : {np.mean(np.isclose(r.trend_vector, df.trend_vector))*100:.6f}%")
    print(f"signal_trend   exact : {pct(r.signal_trend, df.signal_trend.to_numpy()):.6f}%")
    print(f"signal_wave    exact : {pct(r.signal_wave, df.signal_wave.to_numpy()):.6f}%")
    t1s, t1a = np.abs(r.signal_trade) == 1, np.abs(df.signal_trade.to_numpy()) == 1
    print(f"Type-1 signals exact : {pct(t1s, t1a):.6f}%  ({int(t1a.sum()):,} trend starts)")
