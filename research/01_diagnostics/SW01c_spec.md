# SW01c_2022_REGIME_COMPLEMENT — Preregistered Spec

_Committed before results are read. 2026-08-06. Red-team-originated (SW00 §7). Zero new DoF._

## Hypothesis (H-002)
The canonical Type-1 configuration retains positive after-cost expectancy in the 2022 bear/high-volatility regime — data never examined by us and outside the vendor-replication window. If the "edge" is repackaged 2023-25 bull drift, 2022 should expose it (longs should fail; if the signal is real, shorts should carry the year).

## Config
Identical to SW00 canonical except window: `from 2022-01-01T06:00:00Z` → `to 2022-12-31T00:00:00Z` (last session ends Fri 2022-12-30 17:00 ET; boundary in weekend gap; no overlap with the 2023-25 research window). Runs: R01 slip-0, R02 slip-1 (Standard fill, Lifetime commission). Strategy source sha256 `221d1e13…` (unchanged).

## Preregistered gates
- **PASS:** slip-1 net > 0.
- **INCONCLUSIVE:** slip-1 net in (−$15,000, $0] — thin-edge regime sensitivity, logged, campaign continues with downgraded forward prior.
- **FAIL:** slip-1 net ≤ −$15,000 — the baseline's edge is regime-dependent; forward-profit prior materially downgraded; no rescue tuning permitted (constitution §12); finding feeds SW05/SW08 design instead.
- Secondary (directional mechanism check, reported not gated): 2022 short-side slip-0 PF > 1.0 expected if the trend signal is real; long-side losses expected and acceptable.
- Data-integrity precondition: trace must show ~330–350k bars loaded (full year of 1-min data). If 2022 data is absent/partial → run is void, report data gap, request user download via NT8 UI.

## Consumption note
Running this consumes 2022 as research data (logged in registry). 2022 remains available for later WFO extension but is no longer "never-seen".
