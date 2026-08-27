# Active parameter map — which vendor parameter drives which output

_Regenerated and re-verified 2026-08-07 against 177,021 real NQ 1-minute bars using the recovered
model `solar_wave_full()`. This is a **derived** map, not a measured correlation: the recursion is
known exactly, and this table confirms the derivation empirically rather than substituting for it._

## The map

| parameter | TrailingStop | TrendVector | **Type-1 flips** | Type-2 | Type-3 | Signal_Trend | Signal_Wave |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **StopMultiplier** | ● | ● | **●** | ● | ● | ● | ● |
| TrendMultiplier | · | ● | **·** | ● | ● | · | · |
| SlowdownScan | · | · | **·** | ● | ● | ● | ● |
| WeakWeakSplit | · | · | **·** | ● | ● | ● | ● |
| PullbackSplit | · | · | **·** | ● | ● | · | · |
| PullbackEarly | · | · | **·** | ● | ● | · | · |

● = at least one tested value changes this output · = bit-identical across every tested value

Values swept: StopMultiplier {150, 179, 240, 300}; TrendMultiplier {45, 90, 135};
SlowdownScan {3, 5, 8, 12}; WeakWeakSplit {5, 10, 15, 20}; PullbackSplit {3, 10, 25};
PullbackEarly {true, false}.

## The load-bearing claim, tested directly

> **The Type-1 flip sequence is a function of the price series and StopMultiplier only.**

Swept **480 combinations** of TrendMultiplier × SlowdownScan × WeakWeakSplit × PullbackSplit ×
PullbackEarly (5 × 4 × 4 × 3 × 2) against the canonical baseline on 177,021 bars.

**Type-1 flip sequence identical in 480 / 480. CONFIRMED.**

This is why the entire campaign collapsed to a one-dimensional search. It is not an empirical
regularity that might break at untested settings — it follows from the recovered recursion, in
which the Type-1 rule reads only the running close extreme and `S = StopMultiplier × tick`. The
sweep is a check on the derivation, not the evidence for it.

**State it precisely.** These four parameters are *inert for the Type-1 flip rule*. They are
**not** universally inert — every one of them moves Type-2 and Type-3, and two of them move
Signal_Trend and Signal_Wave. Calling them "inert" without the qualifier is wrong, and earlier
campaign documents that did so have been corrected.

## Reading the non-obvious cells

- **TrendMultiplier moves TrendVector but not TrailingStop.** They are parallel offsets from the
  same anchor; only the offset differs. This is also why TrendMultiplier reaches Type-2 (which
  tests excursions against TrendVector) but never Type-1.
- **PullbackSplit and PullbackEarly appear to move Type-3.** They do not move the underlying
  Type-3 *state machine*; they change which bars a Type-2 occupies, and Type-2 overwrites the
  `Signal_Trade` display slot on collision. This is a plot-slot artifact of the published series,
  documented in `research/03_reverse_engineering/TYPE2_RECOVERY_REPORT.md`, and it is exactly why
  Type-3 could not be fully verified until Type-2 was recovered.
- **SlowdownScan and WeakWeakSplit reach Signal_Trend and Signal_Wave** because they define the
  weak/strong state and the wave counter, which is the layer Type-3 is emitted from.

## Scope limit

Every result above holds `V ≤ S/2`, where `V = TrendMultiplier × tick`. Above that ratio the
TrendVector ladder takes a second rung whose tie-break could not be resolved from published output.
That regime is characterised, bounded and excluded — see
[`open_model_validation.md`](open_model_validation.md) §4. The vendor's own presets sit at
V/S = 0.503 and 0.500, inside the resolved regime.

Reproduce: the sweep above is `test_G` plus the map generator described in
`research/00_truth/OPEN_MODEL_VALIDATION.md`; the model is `src/analytics/solarwave.py`.
