# Campaign State

_Last updated: 2026-08-06 (initialization)_

## Current phase
**Phase 0 — Establish truth** (SW00_BASELINE_PARITY_COST in progress)

## Frozen baseline
SolarWaveRKReplicaV0 · Type 1 · 90/179/5/10/true/10 · 1-min Last · NQU6 back-adjusted · Lifetime commission · Standard fill · slip 0 · window 2023-01-01T06:00:00Z → 2025-02-02T22:59:59Z · Net $146,440.60 · 2,915 trades · DD −$22,066.60 · PF 1.132213. UI parity verified (see research/solar_wave_parity/).

## Completed experiments
- PARITY (pre-campaign): UI-vs-MCP exact parity — PASS. Evidence: research/solar_wave_parity/type1_2023_2025/.

## Active experiments
- SW00_BASELINE_PARITY_COST — spec preregistered in research/00_truth/SW00_spec.md; runs SW00_R01–R13.

## Pending (frontier order)
SW01 (episode/exit attribution — needs signal-ledger exporter), SW02 (catastrophe stop + session-close), SW03 (single Type-3 re-entry), SW04 (selective Type 2), SW05 (chop veto), SW06 (timeframe portability), SW07 (major/minor context), SW08 (vol sizing), FB01 (failed opening breakout), portfolio phase.

## Decisions
- 2026-08-06: Campaign structure initialized; specs preregistered before result reads; benchmark integrated into SW00 (determinism reruns double as slippage-0 baseline).
- 2026-08-06: Optimization-machinery benchmark uses a provably inert sweep (StartTime with UseTimeFilter=false) — zero information leak.
- 2026-08-06: 3m/2m/5m anchors NOT run during benchmarking to avoid contaminating Phase 5 preregistration; scaling measured via window length instead.
- 2026-08-06: Playback/reload signal audit DEFERRED — requires connection changes prohibited by the safety boundary; user must run Playback manually if desired. High fill resolution probed via MCP instead.

## Unresolved integrity issues
- None currently. (Known benign artifact: boundary-adjacent session-close trade may be absent from serialized trade list; engine totals correct.)

## Tested-config count
- Search-space configs consumed: **1** (canonical Type 1 anchor; parity runs). SW00 cost/fill/window variations are cost-model probes of the same config, individually logged in registry/tested_configs.csv.

## Compute usage
- Backtest jobs run to date: 3 (parity A/B + 1 rejected commission-template attempt). SW00 adds ~13.

## Pareto frontier
- Seeded with canonical baseline only (see reports/leaderboard.md).

## Next highest-value action
Complete SW00 ingestion + gates → if PASS, build SW01 signal/episode ledger exporter (read-only clone strategy writing per-bar state CSV; new class name, never touching baseline).
