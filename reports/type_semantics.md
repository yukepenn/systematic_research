# Signal semantics — exact meaning of Type 0 / 1 / 2 / 3

_2026-08-07 · derived from the fully recovered model, verified on 2,035,869 bars across 9
configurations with zero mismatches. Derivation:
[`research/03_reverse_engineering/SOLARWAVE_MATH.md`](../research/03_reverse_engineering/SOLARWAVE_MATH.md)
and [`TYPE2_RECOVERY_REPORT.md`](../research/03_reverse_engineering/TYPE2_RECOVERY_REPORT.md)._

## 0. The one-line summary

The indicator is a **fixed-threshold directional-change filter on closes**. One state variable
does all the work: `a`, the running extreme of the close since the current trend began. Everything
published is either a parallel offset from `a` or a counter layered on top of it.

```
S = StopMultiplier x tick        (the reversal / trailing distance)
V = TrendMultiplier x tick       (a second, parallel offset)
a = running extreme of the CLOSE since the trend began

uptrend:    TrailingStop = a - S      TrendVector = a - V
downtrend:  TrailingStop = a + S      TrendVector = a + V
```

A flip requires the close to break the stop **strictly**. Touching it exactly does not flip. This
strictness is tested directly and is not a rounding detail — it is the rule.

## 1. Type 1 — trend transition

**Meaning:** the directional-change threshold was breached; the trend has reversed.

```
uptrend  and close <  a - S   ->  direction = down, a = close, emit -1
downtrend and close >  a + S  ->  direction = up,   a = close, emit +1
```

**Depends on:** the close series and `StopMultiplier`. **Nothing else.** Verified across 480
combinations of every other parameter — see [`active_parameter_map.md`](active_parameter_map.md).

This is the campaign's entire tradable core. R5, R4 and every promoted candidate use Type 1 only.

## 2. Type 3 — trend resumption after a pause

**Meaning:** the trend paused long enough to be marked *weak*, then made a **new close extreme**.
It is an impulse-leg boundary, not a new trend.

```
on flip:            weak = false; wave = 1; rearm = bar + WeakWeakSplit
on a new extreme:   if weak: wave += 1; weak = false;
                             rearm = bar + WeakWeakSplit; emit Type 3
on no new extreme:  if bars_without_progress >= SlowdownScan and bar >= rearm:
                             weak = true; rearm = bar + WeakWeakSplit
```

`SlowdownScan` sets how long a pause must be to count. `WeakWeakSplit` is anti-chatter re-arm.
**Signal_Wave** is simply the impulse-leg count inside the current trend; it resets to 1 on every
flip and increments only on a Type 3.

## 3. Type 2 — counter-trend pullback

The last piece recovered, and the reason the model was incomplete until Wave 2.

**Meaning:** an **edge-triggered latch** on an excursion beyond `TrendVector`, on the counter-trend
side.

- Basis is the **intrabar High/Low**, not the close — this is what made it hard to see.
- Spaced by `PullbackSplit` bars.
- Re-armed by a full-bar clear, by a flip, **and by a Type-3 event** — the only coupling from the
  wave layer back into Type 2.
- Touching `TrendVector` is not a cross. The latch is sticky.
- `PullbackEarly = false` switches the basis from the High/Low excursion to a close-confirmed
  return.

**Verified:** 45,825 events, 0 false positives, 0 false negatives.

## 4. Type 0 — *not* a signal

`Signal_Trade = 0` means **no new event on this bar.** It is the absence of a signal.

The strategy wrapper's `EntrySignalType = 0` is a different thing entirely: it means
**"take the first non-zero signal while flat."** It is a path-dependent, first-eligible-wins state
machine, and therefore:

```
PnL(Type 0)  !=  PnL(Type 1) + PnL(Type 2) + PnL(Type 3)
```

Whichever signal arrives first while flat occupies the position and **suppresses** the others until
the next exit. Attribution requires replaying the state machine, not summing components — see
[`type0_attribution.md`](type0_attribution.md).

## 5. Priority and the plot-slot collision

When two signals land on the same bar, the published `Signal_Trade` series shows only one.
Observed priority: **Type 1 > Type 2 > Type 3.**

This is a *display* artifact of a single-slot output series, not a state-machine property: the
underlying Type-3 state still advances on a bar where Type 2 occupies the slot. This is precisely
why Type 3 could not be fully verified before Type 2 was recovered, and why changing
`PullbackSplit` appears to move Type-3 events in the parameter map when it does not move the
Type-3 machine.

## 6. Economic reading

| type | event | campaign verdict |
|---|---|---|
| **1** | trend reverses past the threshold | **the edge.** The only signal in any promoted candidate |
| **3** | trend resumes after a pause | +$24.89/marginal trade but block-bootstrap P(mean ≤ 0) = 0.115 → **not established**; sleeve rejected on interaction |
| **2** | counter-trend pullback | **cost-fragile.** Adding it costs 0.33 Sharpe (C4); avg $22.61 at a 28 % win rate |
| **0** | no event | not a signal; the wrapper's first-eligible mode is a distinct architecture |

The asymmetry is mechanical, from DC01: the payoff is a fat right tail over a median-losing
distribution. Type 1 catches whole trends. Types 2 and 3 add trades inside trends, which pays more
friction for a smaller slice of the same tail.
