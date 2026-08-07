# TYPE2_RECOVERY_REPORT — RE02

_Status: **IN PROGRESS**. Core rule identified and 95.3 % exact; residual decode running.
Spec: `TYPE2_RECOVERY_SPEC.md` (preregistered before any export was read)._

## 1. Instrumentation

`SolarWaveRKLedgerV2` (new class; V1 untouched) — read-only exporter, trades nothing.
It binds the vendor indicator through its **public generated wrapper via reflection**, so the
file carries no compile-time vendor-assembly reference and compiles in the MCP sandbox; the
same public wrapper method and the same public `Series<double>` indexers execute, so the
observed output is identical to a direct-typed call. Columns:

`time,bar,open,high,low,close,volume,first_bar_of_session,signal_trade,signal_trend,signal_wave,trailing_stop,trend_vector`

**Integrity check (mandatory before any decode):** the new canonical export row-aligns with the
frozen `sw01_bar_ledger.csv` at **1.000000** on `time`, `close`, `signal_trade`, `signal_trend`,
`signal_wave`, `trailing_stop` and `trend_vector` across all 737,707 bars. OHLC sanity
(`high ≥ max(open,close)`, `low ≤ min(open,close)`) holds on 100 % of bars. The added columns
therefore extend the existing ground truth rather than replacing it.

### Export matrix executed

| Probe | TM | SM | SS | WWS | PE | PS | TF | Window | T2 events |
|---|---|---|---|---|---|---|---|---|---|
| E1 canonical | 90 | 179 | 5 | 10 | true | 10 | 1m | 2023-01-01 → 2025-02-02 | 16,324 |
| CONTROL | 90 | 179 | 5 | 10 | true | 10 | 1m | 2024-01-01 → 2024-07-01 | 3,516 |
| PEfalse | 90 | 179 | 5 | 10 | **false** | 10 | 1m | probe | 2,708 |
| PS3 | 90 | 179 | 5 | 10 | true | **3** | 1m | probe | 4,646 |
| PS25 | 90 | 179 | 5 | 10 | true | **25** | 1m | probe | 2,609 |
| TM45 | **45** | 179 | 5 | 10 | true | 10 | 1m | probe | 4,628 |
| TM135 | **135** | 179 | 5 | 10 | true | 10 | 1m | probe | 2,687 |
| SM240 | 90 | **240** | 5 | 10 | true | 10 | 1m | probe | 3,097 |
| SS8WWS15 | 90 | 179 | **8** | **15** | true | 10 | 1m | probe | 3,515 |
| 3m | 90 | 179 | 5 | 10 | true | 10 | **3m** | probe | — |

## 2. Established facts about Type 2 (each verified exactly)

1. **Type 2 is a with-trend event.** `sign(Signal_Trade) == sign(trend)` on **100.0000 %** of
   the 16,324 canonical Type-2 bars. It marks a counter-trend *pullback inside* the trend, not a
   counter-trend signal.
2. **The trigger is intrabar, against `TrendVector`.** On **100.0000 %** of Type-2 bars the
   bar's low (uptrend) or high (downtrend) is beyond `TrendVector`; only 70.5 % have the *close*
   beyond it. This settles the question the close-only ledger could not: Type 2 tests **High/Low**.
   A `TrendVector` cross is necessary but far from sufficient — the level condition alone fires on
   225,874 bars of which only 7.2 % are Type 2.
3. **It is an edge trigger, not a level trigger.** A `hasCrossedTrendVector` latch fires once per
   excursion and re-arms only on a bar entirely on the trend side of `TrendVector`. Re-arming on
   *close* recovery instead is decisively worse (FP 2,224 vs 76 in the teacher-forced test).
4. **`PullbackSplit` is the minimum bar spacing between consecutive Type-2 events.** Verified by
   its signature in the inter-event gap histogram: with PS=10 the gap distribution has a sharp
   step at 11; with PS=3 the mass moves to 4–5; with PS=25 it moves to 26–27. Same mechanism as
   `WeakWeakSplit` in the weak-state layer. The comparison is strict (`t > lastFire + PS`).
5. **A new extreme resets the latch, and the reset is applied *after* the trigger check.** All 8
   residual false negatives of the pre-fix machine sat exactly one bar after a bar that was
   simultaneously a new extreme and a counter-trend excursion (a Type-3 bar). Ordering matters:
   reset-before would fire Type 2 *on* the Type-3 bar; reset-after reproduces the observed
   next-bar firing.
6. **Signal priority confirmed on real collisions:** Type 1 > Type 2 > Type 3 for the plot slot.
   10,524 modelled Type-3 events − 200 Type-2 collisions = 10,324 observed, exactly.
7. **`PullbackEarly` selects a different firing point, not a filter.** PE=true and PE=false share
   only 95 of ~3,000 events. On PE=false bars the close is **never** beyond `TrendVector`
   (0.0000) while high/low is beyond on 96.9 %, and PE=false events cluster 1–10 bars *after* the
   corresponding PE=true event. PE=false therefore waits for close confirmation / recovery
   instead of firing at the excursion. (Exact PE=false rule still open.)
8. **`SlowdownScan`/`WeakWeakSplit` are all but inert for Type 2** — SS8/WWS15 shares 3,514 of
   3,516 events with CONTROL. Not exactly zero, so the residual coupling is being checked.

## 3. Current best machine (95.3 % exact, canonical parameters)

```
crossed[t] = is_up ? low[t] <  TrendVector[t]
                   : high[t] > TrendVector[t]           # STRICT

per bar t, after the ladder update:
    if FLIP[t]:            hasCrossed = false ; nextPB = -inf
    if crossed[t] and not hasCrossed and t > nextPB and not FLIP[t]:
                           EMIT Type 2 (sign = trend direction)
                           nextPB = t + PullbackSplit
    hasCrossed = crossed[t]
    if NEW_EXTREME[t]:     hasCrossed = false            # AFTER the trigger check
```

Scored against the vendor's own `trend_vector` column (FP = machine fires / ledger silent,
FN = ledger fires / machine silent; flip bars excluded because Type 1 masks Type 2 there):

| Probe | events | FP | FN | exact |
|---|---|---|---|---|
| CONTROL | 3,516 | 106 | 59 | 95.3 % |
| PS3 | 4,646 | — | — | 95.6 % (203 err) |
| PS25 | 2,609 | — | — | 95.1 % (127 err) |
| SM240 | 3,097 | — | — | 94.4 % (174 err) |
| SS8WWS15 | 3,515 | — | — | 95.3 % (166 err) |
| 3m | — | — | — | 244 err |
| TM45 | 4,628 | — | — | 84.7 % (710 err) |

A **teacher-forced** variant (spacing counter driven by the ledger's own event times, isolating
the local rule from cascade divergence) reaches **FP 76 / FN 8 on 3,516 events** — so the
remaining free-running error is dominated by cascade from a small local-rule defect, not by a
wrong model class. Closing that defect is the open item.

**Per the campaign standard this is NOT accepted.** 95 % with structured residuals is a wrong
rule, not an approximate one. The residual decode is running as a four-angle adversarial search
(state-machine enumeration, price-geometry alternatives, wave-layer coupling, learn-then-simplify),
each scored on exact event sets.

## 4. Unplanned discovery: `TrendVector` has a second ladder rung

`TrendVector = anchor ∓ TrendMultiplier×tick` is exact (1.000000) on the canonical 737,707 bars,
on the 3m probe, at TM=45, and at SM=240 — **but only 0.6976 at TM=135.**

Cause: `TrendVector` is bounded by the *previous* ladder rung as well as the current one.
Writing `r₁` for the extreme of the previous (opposite) trend:

```
uptrend  : TV = max(anchor − V, r₁ + V)
downtrend: TV = min(anchor + V, r₁ − V)
```

The clamp **provably never binds when V ≤ S/2**: the flip test is strict, so on a tick grid
`anchor ≥ r₁ + S + 1 tick`, hence `anchor − V ≥ r₁ + (S − V) + 1 tick ≥ r₁ + V` exactly when
`S − V ≥ V`. The vendor's own shipped templates sit at V/S = 90/179 = 0.503 and 60/120 = 0.500 —
i.e. **the product is designed to sit exactly at the boundary where the second rung is inert.**
TM=135 (V/S = 0.754) is an off-design regime.

Adding the r₁ clamp raises TM=135 agreement 0.6976 → 0.8771; adding a second bound from the
rung *before* that (`r₂`, verified: in every unexplained case the implied rung sat exactly 2V
from the extreme two trends back) reaches **0.9559**, while leaving all design-regime probes at
**1.000000**. The exact TM>S/2 formula is not yet closed.

**Decision (recorded before any result was used):** the open model and the parity gate are
defined on the **design regime V ≤ S/2**, where `TrendVector` is exactly the single-rung formula,
verified on 737,707 + 177,021 + 3m bars and at TM ∈ {45, 90}, SM ∈ {179, 240}. TM > S/2 is
documented as a bounded, characterised ambiguity and is **excluded from every experiment**; the
multi-parameter parity matrix uses TM ∈ {30, 45, 60, 89} instead of 135. This costs the campaign
nothing — `TrendMultiplier` is inert for Type 1 and no candidate strategy uses V > S/2 — and it
is stated here rather than discovered later.

## 5. Provenance

Behavioural observation of the licensed indicator's published `Series<double>` output only.
No decryption, unpacking, patching, memory dumping or any other circumvention of the Agile.NET
protection was performed; the vendor assembly was not modified or redistributed. The recovered
rules are behavioural mathematics, **not** vendor source code.
