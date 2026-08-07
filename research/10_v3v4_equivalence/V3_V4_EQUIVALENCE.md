# V3 vs V4 equivalence at ThresholdMode = 1 — the gap, and what closing it found

_2026-08-07 · 13-cell sweep, `SolarWaveOpenV4`, ThresholdMode 1, VolMult 6…30, 3-minute NQ 09-26,
2022-01-01 → 2026-07-31, real slip-1, Lifetime commission. Ledgers in this directory. Compared
fill-by-fill against the `SolarWaveOpenV3` ledgers in `research/05_open_axes/h006/` that produced
the published R5._

## Result: NOT equivalent. The design document was wrong.

`reports/final_system_design.md` §7 specified R5 as **`SolarWaveOpenV4, ThresholdMode = 1`**. The
published R5 numbers were measured on **`SolarWaveOpenV3`**. They are different strategies.

| VolMult | V3 fills | V4 fills | V3 net | V4 net |
|--:|--:|--:|--:|--:|
| 6 | 16,984 | 17,180 | $166,145 | $84,023 |
| 8 | 11,076 | 11,246 | $170,549 | $187,574 |
| 10 | 8,072 | 8,170 | $150,033 | $97,069 |
| 12 | 6,166 | 6,266 | $138,883 | $162,530 |
| 14 | 4,918 | 4,978 | $241,924 | $207,763 |
| 16 | 4,066 | 4,124 | $228,891 | $223,960 |
| 18 | 3,360 | 3,408 | $246,515 | $269,936 |
| 20 | 2,938 | 2,950 | $245,125 | $235,689 |
| 22 | 2,598 | 2,614 | $245,446 | $238,881 |
| 24 | 2,320 | 2,346 | $193,737 | $194,501 |
| 26 | 2,108 | 2,138 | $132,860 | $127,579 |
| 28 | 1,904 | 1,920 | $165,399 | $181,049 |
| 30 | 1,786 | 1,794 | $249,257 | $253,484 |

Zero cells match. V4 produces slightly more fills in every cell.

## Cause: one line

```csharp
// SolarWaveOpenV4.cs, ResolveS(), line 225
return Math.Round(s / TickSize) * TickSize;     // snap S to the tick grid
```

V3 returns `S = VolMult × sigma` **unrounded**. V4 snaps it to the nearest tick. Everything else —
the sigma estimator, the clamp, the state machine, the call order, the warm-up guard — is
byte-identical between the two files. I read both.

The threshold difference is at most **half a tick ($2.50 on NQ)**. But the flip rule is a *strict*
inequality, so a half-tick shift changes which bars flip; once one flip differs the two paths
separate and never fully re-converge. The first divergence is the very first trade: V3 enters long
at bar 39, V4 does not, and from there the two run the same signal structure one position apart.

Agreement is nonetheless high — 97.1 % of V3's fills appear in V4 at the same timestamp and side.

## What this costs, and the unplanned robustness test it produced

Because the two differ *only* by a half-tick perturbation of the threshold, comparing them is a
free sensitivity test of a parameter nobody chose deliberately.

| | V3 (continuous S) | V4 (S snapped to tick) |
|---|--:|--:|
| daily Sharpe | 1.010 | 0.981 |
| net | $198,059 | $189,541 |
| max drawdown | −$39,126 | **−$36,275** |
| PSR | 0.9929 | 0.9912 |
| P(Sharpe ≤ 0) | 0.0024 | 0.0026 |
| positive years | 5/5 | 5/5 |

*(1,333-session union of the two runs, so the Sharpe differs slightly from the 1,424-session
campaign basis.)*

```
observed dSharpe (V3 - V4)        +0.029
paired block bootstrap P(d <= 0)   0.247
daily P&L correlation              0.9949
```

**The two are statistically indistinguishable**, and V4 actually has the *smaller* drawdown. So
this is good news for R5: the result does not depend on a half-tick implementation detail nobody
reasoned about. It is a genuine robustness datapoint, obtained by accident.

It is emphatically **not** a reason to now prefer whichever version scores higher. Picking V3 over
V4 on +0.029 Sharpe at P = 0.247 would be precisely the selection behaviour this campaign spent
three waves proving does not work.

## Resolution

1. **The specification is corrected to name `SolarWaveOpenV3`**, which is what actually produced
   every published R5 figure. No R5 number changes, because none was ever measured on V4.
2. The V4 run is kept as evidence and as the half-tick sensitivity test above.
3. Neither version is declared "correct". They are two defensible discretisations of the same rule,
   and the honest statement is that R5 is insensitive to the choice.

## Why this was worth doing

The gap was a **documentation** error — the spec named a strategy that had never been run — but it
would have been invisible to anyone reproducing the work, who would have followed the spec, used
V4, got different numbers per cell, and reasonably concluded the campaign was irreproducible.

It also demonstrates something the campaign asserts repeatedly and can now show: on this data, two
implementations that differ by a rounding decision produce per-cell nets differing by up to 44 %
(VolMult 6: $166k vs $84k) while being statistically identical at the ensemble level. That is the
single-cell fragility argument, made accidentally and from the inside.
