# Campaign State

_Last updated: 2026-08-06 (SW00 complete)_

## Current phase
**Phase 1 — Understand the baseline** (SW01 active; Phase 0 gate passed)

## Frozen baseline
SolarWaveRKReplicaV0 · Type 1 · 90/179/5/10/true/10 · 1-min Last · NQU6 back-adjusted · Lifetime commission · Standard fill · window 2023-01-01T06:00:00Z → 2025-02-02T22:59:59Z · slip0: Net $146,440.60, 2,915 trades, DD −$22,066.60, PF 1.132213 · **honest cost basis (slip1): Net $118,645.60, avg $40.83, PF 1.106, daily Sharpe 1.39, Calmar 2.56**. Source sha256 `221d1e13…`, ledger hash `fe395c14…`.

## Completed experiments
- PARITY (pre-campaign) — PASS. research/solar_wave_parity/.
- **SW00_BASELINE_PARITY_COST — PASS** (all 7 preregistered gates). research/00_truth/SW00_report.md. Key: deterministic pipeline (7 bit-identical runs incl. concurrent); slip1/2/3 all positive; session-close exits carry the entire net edge (+$189.6k, PF 10.8) while Solar-trailing exits net −$42.8k; median MFE giveback 1.34×; High fill = no-op for market-order strategies; native optimization sweeps validated bit-identical (Tier-1 mode).

## Active experiments
- SW01_EPISODE_AND_EXIT_ATTRIBUTION — next: build read-only ledger exporter `SolarWaveRKLedgerV1` (new class; zero trading-logic changes; per-bar Signal_Trade/Trend/Wave/TrailingStop + episode reconstruction), join to R01 trade ledger, produce full decomposition incl. episode/wave/flip/efficiency tags.

## Pending (frontier order)
SW02 (catastrophe stop + session-close counterfactual — now high-stakes given exit-reason finding), SW03 (single Type-3 re-entry), SW04 (selective Type 2), SW05 (chop veto), SW06 (timeframes), SW07 (context), SW08 (vol sizing), FB01, portfolio, locked-forward.

## Decisions
- 2026-08-06: SW00 PASS → Solar promotion proceeds. Campaign execution modes fixed: Tier 1 = native optimization sweeps (validated bit-identical, ~4 s/combination, summary payload); Tier 2 = individual full-payload runs; Tier 3 = High-fill (stop-order candidates) + manual Playback (user-run only). Determinism-critical runs serial; concurrency safe but ≤2 and modest gain.
- 2026-08-06: 1-tick slippage adopted as the honest reporting basis for all future candidate comparisons; 2-tick checked at every promotion.
- Earlier init decisions: see git history of this file.

## Unresolved integrity issues
- None blocking. Playback/reload audit remains a deferred manual item (safety boundary). Benign known artifacts documented in SW00_report §1 gate 5.

## Tested-config count
- Search-space configs consumed: **1** (canonical anchor). 16 backtest jobs run total (3 pre-campaign + 13 SW00). Every job logged in registry/tested_configs.csv.

## Compute usage
- ~75 s total NT8 engine time; ~40 MB raw payloads archived under runs/.

## Pareto frontier
- reports/leaderboard.md — baseline reference row only.

## Next highest-value action
Phase 1 triple, in order of information value per unit work:
1. **SW01c** — canonical config on never-examined 2022 (bear-regime complement; one Tier-2 run + one slip-1 run; red-team-originated, zero DoF).
2. **SW01b** — drift-matched control: time-shifted/random entries with identical session-close machinery vs the baseline's close-bucket and long-side edge (null-hypothesis test for drift beta; zero DoF).
3. **SW01** — `SolarWaveRKLedgerV1` read-only exporter (new class, in-memory compile first, vendor assembly untouched) → episode/wave/flip/efficiency attribution that SW02/SW03/SW05 gates depend on.
Red-team standing items for every future promotion: Thursday/quarterly concentration, short-side cost fragility, session-close survivorship confound, slip-2 as event-day honest floor.
