# TYPE2_RECOVERY_REPORT — RE02: **COMPLETE**

_2026-08-07 · Spec: `TYPE2_RECOVERY_SPEC.md` (preregistered before any export was read) ·
Reference implementation: `solar_wave_full()` in `src/analytics/solarwave.py`_

## Result

**The RenkoKings Solar Wave RK indicator is fully recovered.** Every published series, every
signal symbol, exact on every bar of every probe:

| probe | bars | TrailingStop | TrendVector | **Signal_Trade** | Signal_Trend | Signal_Wave |
|---|---|---|---|---|---|---|
| canonical 1m (TM90/SM179/SS5/WWS10/PE true/PS10) | 737,707 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| CONTROL (6-month window) | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| PullbackSplit = 3 | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| PullbackSplit = 25 | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| PullbackEarly = false | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| TrendMultiplier = 45 | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| StopMultiplier = 240 | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| SlowdownScan 8 / WeakWeakSplit 15 | 177,021 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |
| 3-minute bars | 59,015 | 1.000000 | 1.000000 | **1.000000** | 1.000000 | 1.000000 |

**1,436,860 bars. Nine parameter configurations. Zero mismatches on any series.**
Type-2 events specifically: **45,825 events, 0 false positives, 0 false negatives**, all signs
correct, across ten probe files.

Excluded by preregistered decision: `TrendMultiplier > StopMultiplier/2` (see §4). Type 2 is
exact there too; only `TrendVector` and Type-3 *timing* differ, and no campaign experiment uses
that regime.

## 1. Method

Preregistered in the spec, then executed without deviation:

1. **Instrument.** `SolarWaveRKLedgerV2` — read-only exporter, trades nothing, binds the vendor
   indicator through its **public generated wrapper via reflection** so the file carries no
   compile-time vendor reference and compiles in the MCP sandbox. The same public wrapper method
   and the same public `Series<double>` indexers execute.
2. **Integrity gate before decoding.** The new canonical export row-aligns with the frozen
   `sw01_bar_ledger.csv` at 1.000000 on every shared column across all 737,707 bars, and OHLC
   sanity holds on 100 % of bars. The added High/Low columns *extend* the existing ground truth
   rather than replacing it.
3. **Nine controlled probes** varying one dimension at a time (the table above).
4. **Adversarial decode.** Four independent agents attacked the residual from different angles —
   state-machine enumeration, price-geometry alternatives, wave-layer coupling, and
   learn-then-simplify. Two converged on the same rule, in different words, both at 0/0.
5. **Adjudication.** The rule was then re-derived and re-scored from scratch, independently of
   the agents' code, before being accepted. That pass is what produced the table above.

## 2. The complete recovered model

Core ladder (previously recovered, unchanged): one state variable `a` = running extreme of the
**close** since the trend began; `TrailingStop = a ∓ S`, `TrendVector = a ∓ V`; flip on a
**strict** break of the stop.

Wave layer (previously recovered, unchanged): `SlowdownScan` bars without a new extreme declare
the trend weak; a new extreme while weak increments the wave and emits Type 3;
`WeakWeakSplit` is the anti-chatter re-arm.

**Type 2 — new.** Two state variables, matching the vendor's own decompiled field names
`hasCrossedTrendVector` and `nextPullbackBar`. Let `TV` be TrendVector at the **end** of bar *t*,
and "beyond" mean the counter-trend side of it. **Every comparison is strict: a bar that merely
touches `TV` leaves the latch unchanged.**

```
on a FLIP bar:   armed = True ; nextPB = -inf ; no Type-2 evaluation
                 (Type 1 owns the plot slot on that bar)

PullbackEarly = TRUE      basis: the bar's own HIGH/LOW
    fire  <=>  extreme strictly beyond TV  and  armed  and  t > nextPB
    then   extreme strictly beyond TV -> armed = False
           extreme strictly inside TV -> armed = True

PullbackEarly = FALSE     basis: the CLOSE, with a transient OPEN arming
    fire  <=>  (not armed or Open strictly beyond TV)
               and Close strictly inside TV  and  t > nextPB
    then   Close strictly beyond TV -> armed = False
           Close strictly inside TV -> armed = True
    The Open can only enable a fire on its own bar; it never persists into `armed`.

on fire:          nextPB = t + PullbackSplit      (so the minimum gap is PS + 1 bars)
on a TYPE-3 bar:  armed = True                    (end of bar)

plot priority:    Type 1 > Type 2 > Type 3
```

### Why the close-only ledger could never have settled this
Type 2 is triggered by the bar's **High/Low**, not its close. Only 70.5 % of Type-2 bars have the
close beyond `TrendVector`; 100 % have the high or low beyond it. The original exporter emitted
closes only, which is why the first pass stalled at "the retrace distribution implies High/Low"
without being able to prove it. One re-export with three extra columns closed it.

## 3. What was falsified along the way

These are as valuable as the rule itself, because each was a plausible hypothesis held earlier:

- **Strong/weak gating of Type 2 — FALSIFIED.** Requiring a strong trend costs ~2,400 false
  negatives of 3,516 on CONTROL: **68 % of Type-2 events fire while the trend is weak.**
- **Wave index, `countSlowdown`, bars-since-slowdown, `nextWeakTrendBar` — none gate Type 2.**
  Decisive probe: perturbing `SlowdownScan`/`WeakWeakSplit` (8/15 vs 5/10) drops `Signal_Wave`
  agreement to 53.5 % while changing only **3 of ~3,516** Type-2 bars — and all 3 are explained
  by the single coupling below.
- **The one real coupling: a Type-3 event re-arms the latch** at the end of its bar. Required for
  exactness on every `PullbackEarly=true` probe; without it the canonical run leaves 14 FP / 32 FN.
- **`PullbackSplit` does not interact with `SlowdownScan`/`WeakWeakSplit`.** `nextPullbackBar` is
  an independent clock, pushed only by a Type-2 fire, cleared only by a flip.
- **A touch is not a cross.** The latch is *sticky*: `price == TV` neither arms nor disarms. This
  single detail was the source of most of the earlier false positives.
- **`PullbackEarly` is not a filter, it is a change of basis** — High/Low-triggered at the
  excursion (true) versus close-confirmed on the return inside `TV` (false). The two produce
  almost disjoint event sets (95 shared of ~3,000).

## 4. Unplanned discovery: `TrendVector` has a second ladder rung

`TrendVector = anchor ∓ V` is exact at TM ∈ {45, 90} and SM ∈ {179, 240}, on 1m and 3m — but only
0.6976 at TM = 135. The line is additionally bounded by the previous ladder rung `r₁`:

```
uptrend  : TV = max(anchor − V, r₁ + V)        downtrend: TV = min(anchor + V, r₁ − V)
```

Because the flip test is strict, on a tick grid `anchor ≥ r₁ + S + 1 tick`, so
`anchor − V ≥ r₁ + (S − V) + 1 tick`, and the clamp **provably cannot bind whenever `V ≤ S/2`**.
The vendor's own shipped presets sit at V/S = 90/179 = 0.503 and 60/120 = 0.500 — **the product is
designed to live exactly at the boundary where this second rung is inert.**

Adding the `r₁` clamp lifts TM=135 agreement from 0.6976 to 0.8771; adding a further bound from
the rung before it (`r₂`, verified: in every otherwise-unexplained case the implied rung sat
exactly 2V from the extreme two trends back) reaches 0.9559 — while leaving every design-regime
probe at 1.000000. In that regime the vendor also emits Type 3 one bar later than the plain
close-extreme automaton whenever `TV` is ladder-bound (885 bars on TM135).

**Decision, recorded before any result was used:** the open model and the parity gate are defined
on the **design regime `V ≤ S/2`**. `V > S/2` is documented here as a bounded, characterised
ambiguity and is **excluded from every experiment**. This costs the campaign nothing —
`TrendMultiplier` is inert for the Type-1 core and no candidate strategy uses `V > S/2` — and it
is stated here rather than discovered later.

## 5. Two warm-up conventions, measured rather than assumed

Reaching exactly 1.000000 on `Signal_Trend` and `Signal_Wave` required two small corrections that
only a full-series comparison would surface:

1. **`Signal_Wave = 0` until the first flip.** The vendor publishes no wave number before a trend
   is established. On the canonical export this is a single contiguous run, bars 0–216.
2. **Bar 0 is a seed, not a no-progress bar.** Counting it toward `SlowdownScan` declares the
   trend weak one bar early. Invisible on the canonical 1-minute export (an early new extreme
   washes it out) but exposed at bar 4 of the 3-minute probe. A genuine off-by-one, now fixed in
   `solar_wave()`.

Neither affects any trading result — the first flip resets all of it — but both were required to
claim exactness, and the campaign standard is exactness.

## 6. Provenance

Behavioural observation of the licensed indicator's published `Series<double>` output only. **No
decryption, unpacking, patching, memory dumping or any other circumvention of the Agile.NET
protection was performed. The vendor assembly was not modified and is not redistributed.** The
recovered rules are behavioural mathematics, **not** vendor source code.

## 7. Reproduce

```
python - <<'EOF'
import sys; sys.path.insert(0,'src/analytics')
import pandas as pd, numpy as np
from solarwave import solar_wave_full, SolarWaveParams
d = pd.read_csv('research/03_reverse_engineering/ledgers/t2_canonical_1m.csv', comment='#')
r = solar_wave_full(d.open, d.high, d.low, d.close, SolarWaveParams())
print((r.signal_trade == d.signal_trade.to_numpy()).mean())   # -> 1.0
EOF
```
