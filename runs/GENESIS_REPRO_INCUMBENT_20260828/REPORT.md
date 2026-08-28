# GENESIS_REPRO_INCUMBENT — RESULT: **PASS (G1·G2·G3)**

Executes `spec.yaml` (committed `0440f30` before results). Trial `G00000`. Program-printed
evidence in `out/` (gate_table, repro_components, population_reconciliation, run_provenance).

## Verdict

> **The incumbent headline upgrades from RECORDED CLAIM to REPRODUCED FACT** — about a backtest.
> Evidence class stays `DISCOVERY_CONSUMED`; nothing here is forward evidence.

- **G1** P1_PCT reproduces to machine precision: raw **$1,393.573663/wk** (Δ 0.0), fixed-DD
  **$1,230.356720/wk** (Δ 0.0), maxDD $22,930.665853 (Δ 3.6e-12), t 4.163612 (Δ 8.9e-16).
- **G2** all four circulating populations reconcile programmatically: 2,401 = incl. 2022-H1
  warm-up · 2,139 = entry-ts filter · 2,131 = session-start filter · 2,137 = NT8 parity under the
  **entry-ts** filter (its actual generating definition, `run_p1pct_parity.py:107`).
  ⭐ **New finding:** the recorded parity "+6 trades" gap was **filter-asymmetric** (Python
  session-filtered vs NT8 ts-filtered); apples-to-apples the engine disagreement is **0.09%**
  either way.
- **G3** XM reproduces (Δ ≤ 1.1e-13); 348 vectorised / 346 sequential reconciled — the two
  disagree on exactly the recorded sessions 2023-04-10 / 2023-05-03 (pandas rolling σ tolerates an
  interior NaN; the sequential loop disqualifies).

## Honest notes

- First driver execution recorded **G2 FAIL**; cause was the reconciliation program's definition
  mapping for 2,137, corrected after reading the parity script. No spec/gate/tolerance/pipeline
  change; both filter variants printed.
- Cache concordance mode: `mem_ext.npz` (`22ea3227…`, mtime 2026-08-26) used as recorded; the
  optional scratch rebuild was not performed — so this certifies **code+cache → artifact**, not a
  from-scratch member recomputation.
- Wall 33 s, peak 2.31 GB; all 7 inputs sha256-streamed; seal asserted; `runs/WE_*` untouched
  (mtimes verified).

**`LIVE ENABLED = NO` · $0.**
