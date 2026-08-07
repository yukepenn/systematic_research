# Open-model validation — summary

_2026-08-07 · full document: [`research/00_truth/OPEN_MODEL_VALIDATION.md`](../research/00_truth/OPEN_MODEL_VALIDATION.md)_

**45 / 45 property tests pass** (`python src/analytics/test_solarwave.py`, exit code 0).

| | result |
|---|---|
| Vendor parity | **2,035,869 bars · 9 configurations · zero mismatches** on every published series |
| Type-2 events | 45,825 · 0 false positives · 0 false negatives |
| Strategy parity | `SolarWaveOpenV1` reproduces the frozen baseline exactly (`runs/RE01_open_parity/`) |
| Vendor dependency | **none** — the open model needs no RenkoKings assembly |
| Known gap | `V > S/2` TrendVector tie-break — **unresolved**, bounded, and provably outside every campaign experiment |

## The gap, stated honestly

At `V/S = 0.754` the model and the vendor disagree on 1.41 % of `Signal_Trade` bars. **None of
those disagreements involves a Type-1 signal** — `TrailingStop` and all 1,077 Type-1 flips remain
100.000 % exact. Since R5 and every promoted candidate trade Type-1 only, and since the vendor's
own presets sit at V/S ≈ 0.50, no campaign result depends on the unresolved rung.

## Correction

Earlier campaign documents reported vendor parity as "1,436,860 bars". That number was wrong and
**understated** the evidence. The correct count, printed by the suite from the committed ledgers,
is **2,035,869**. All affected documents have been corrected.

## Not established

Cross-language Python↔C# series diffing is covered only indirectly, by strategy-level gate checks
against the frozen baseline. A direct series-level diff is the cleanest remaining hardening step
and has **not** been done.
