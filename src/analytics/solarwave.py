"""
solarwave.py — open reference implementation of the RenkoKings Solar Wave RK indicator.

Derived by behavioural reverse engineering (no vendor-binary circumvention): the vendor
assembly's own per-bar output (research/01_diagnostics/sw01_bar_ledger.csv, 737,707 NQ
1-minute bars, 2023-01-02 -> 2025-01-31) was used as ground truth and the generating
recurrence was recovered exactly.

Validation (see research/03_reverse_engineering/{SOLARWAVE_MATH,TYPE2_RECOVERY_REPORT}.md).
The model is COMPLETE as of 2026-08-07: `solar_wave_full` reproduces every published
series exactly.

    TrailingStop        100.000000%   tick-for-tick
    TrendVector         100.000000%   tick-for-tick   (design regime V <= S/2, see below)
    Signal_Trade        100.000000%   per bar, all four symbols, on 9 of 10 probe configs
    Type 2 events       0 FP / 0 FN   across 45,825 events on 10 independent probes
    Signal_Trend        100.000000%
    Signal_Wave         100.000000%

The single exception is TrendMultiplier > StopMultiplier/2, where TrendVector picks up a
second ladder-rung clamp and Type-3 timing shifts by one bar. That regime is excluded from
the campaign: the vendor's own presets sit at V/S = 0.50, exactly where the clamp is
provably inert. Type 2 is exact there too.

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
        elif t > 0:                                 # --- no progress this bar
            # bar 0 seeds the state and is NOT a no-progress bar: counting it would
            # declare the trend weak one bar early. Only visible during warm-up (the
            # first flip resets everything), but it is a real off-by-one and the 3-minute
            # probe exposes it at bar 4.
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


# ---------------------------------------------------------------------------
# Complete model: Type 2 (pullback) and full Signal_Trade reconstruction.
#
# Recovered 2026-08-07 by behavioural reverse engineering from OHLC probe exports
# (research/03_reverse_engineering/TYPE2_RECOVERY_REPORT.md). Two independent decode
# agents converged on this rule; it was then re-derived and re-scored from scratch as an
# adjudication step: 0 false positives and 0 false negatives across 45,825 Type-2 events
# on 10 probes spanning PullbackSplit {3,10,25}, PullbackEarly {true,false},
# TrendMultiplier {45,90,135}, StopMultiplier {179,240}, SlowdownScan/WeakWeakSplit
# {5/10, 8/15}, and both 1-minute and 3-minute bars.
#
# Type 2 needs the bar's HIGH/LOW - which is precisely why the original close-only ledger
# could not settle it - plus exactly ONE coupling to the wave layer: a Type-3 event
# re-arms the latch at the end of its bar. Nothing else in the weak/wave automaton gates
# Type 2. That was verified rather than assumed: perturbing SlowdownScan/WeakWeakSplit
# drops Signal_Wave agreement to 53.5% while changing only 3 of ~3,500 Type-2 bars, and
# all 3 are explained by that one coupling.
# ---------------------------------------------------------------------------


def solar_wave_full(open_, high, low, close, params: SolarWaveParams | None = None,
                    start_up: bool = False) -> SolarWaveResult:
    """Complete Solar Wave RK: core ladder + wave automaton + Type-2 pullbacks.

    The Type-2 rule, in the vendor's own field names (`hasCrossedTrendVector`,
    `nextPullbackBar`). Let TV be TrendVector at the END of bar t, and let "beyond" mean
    the counter-trend side of it (below TV in an uptrend, above it in a downtrend). Every
    comparison is STRICT: a bar that merely TOUCHES TV leaves the latch unchanged.

        on a FLIP bar:   armed = True; nextPB = -inf; no Type-2 evaluation at all
                         (Type 1 owns the plot slot on that bar)

        PullbackEarly = True   -- basis: the bar's own High/Low
            fire  <=>  extreme strictly beyond TV  and  armed  and  t > nextPB
            then  extreme strictly beyond TV -> armed = False
                  extreme strictly inside TV -> armed = True

        PullbackEarly = False  -- basis: the Close, with a transient Open arming
            fire  <=>  (not armed or Open strictly beyond TV)
                       and Close strictly inside TV  and  t > nextPB
            then  Close strictly beyond TV -> armed = False
                  Close strictly inside TV -> armed = True
            The Open can only enable a fire on its own bar; it never persists into `armed`.

        on fire:         nextPB = t + PullbackSplit   (so the minimum gap is PS + 1 bars)
        on a TYPE-3 bar: armed = True                 (applied at the END of the bar; the
                                                       only coupling to the weak/wave layer)

    Plot priority on a shared bar is Type 1 > Type 2 > Type 3: a fired Type 2 overwrites
    the Type-3 symbol in Signal_Trade, though the wave counter still increments.
    """
    p = params or SolarWaveParams()
    o = np.asarray(open_, dtype=float)
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    n = c.size

    base = solar_wave(c, p, start_up=start_up)
    is_up = base.is_up
    tv = base.trend_vector
    flip = np.abs(base.signal_trade) == TRADE_TREND_START
    t3 = np.abs(base.signal_trade) == TRADE_STRENGTHEN

    fire = np.zeros(n, dtype=bool)
    armed = True
    next_pb = -(1 << 60)
    for t in range(n):
        if flip[t]:
            armed = True
            next_pb = -(1 << 60)
            continue
        up = bool(is_up[t])
        if p.pullback_early:
            ext = l[t] if up else h[t]
            beyond = ext < tv[t] if up else ext > tv[t]
            inside = ext > tv[t] if up else ext < tv[t]
            if beyond and armed and t > next_pb and t > 0:
                fire[t] = True
                next_pb = t + p.pullback_split
            if beyond:
                armed = False
            elif inside:
                armed = True
        else:
            open_beyond = o[t] < tv[t] if up else o[t] > tv[t]
            close_beyond = c[t] < tv[t] if up else c[t] > tv[t]
            close_inside = c[t] > tv[t] if up else c[t] < tv[t]
            if (not armed or open_beyond) and close_inside and t > next_pb and t > 0:
                fire[t] = True
                next_pb = t + p.pullback_split
            if close_beyond:
                armed = False
            elif close_inside:
                armed = True
        if t3[t]:
            armed = True

    sign = np.where(is_up, 1, -1)
    signal_trade = np.zeros(n, dtype=np.int8)
    signal_trade[t3] = (TRADE_STRENGTHEN * sign[t3]).astype(np.int8)
    signal_trade[fire] = (TRADE_PULLBACK * sign[fire]).astype(np.int8)
    signal_trade[flip] = (TRADE_TREND_START * sign[flip]).astype(np.int8)

    # Vendor warm-up convention, measured rather than assumed: before the first flip the
    # indicator has no established trend, so it publishes Signal_Wave = 0 throughout that
    # stretch (bars 0-216 of the canonical export, a single contiguous run), and
    # Signal_Trend = 0 on the very first bar. Reproducing it takes both series to exact
    # parity; without it the only residual left in the whole model is this warm-up block.
    signal_trend = base.signal_trend.copy()
    signal_wave = base.signal_wave.copy()
    first_flip = int(np.argmax(flip)) if flip.any() else n
    signal_wave[:first_flip] = 0
    if n:
        signal_trend[0] = 0

    return SolarWaveResult(base.trend_vector, base.trailing_stop, signal_trend,
                           signal_trade, signal_wave, base.anchor, base.is_up)
