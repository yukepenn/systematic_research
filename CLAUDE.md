# Systematic Research — NQ Solar Wave Campaign

Autonomous research program: robust portfolio-level geometric growth on NQ.
Primary thesis: `research/Research_Thesis.txt` (kept there; do not duplicate).
Constitution and phase gates: thesis §17 + `research/CAMPAIGN_STATE.md`.

## Hard safety boundary (never violate)
- Research/backtest accounts only. Never place/modify/cancel orders, never enable/deploy strategies, never touch Sim101 or real accounts, never alter connections/credentials/licensing, never modify the licensed RenkoKings vendor assembly.
- Never delete raw research evidence, erase failed experiments, rewrite historical results, or use locked-forward data for tuning.
- No force-push. No history rewrites.

## Frozen truth (do not change)
- Baseline: `SolarWaveRKReplicaV0`, Type 1, 90/179/5/10/true/10, 1-min Last, NQ 09-26 (NQU6, back-adjusted merge), NinjaTrader Brokerage Lifetime commission ($4.36/RT), Standard fill, exit-on-session-close, DefaultQuantity=1.
- Canonical window: 2023-01-01T06:00:00Z → 2025-02-02T22:59:59Z.
- Canonical result: Net $146,440.60 | 2,915 trades | DD −$22,066.60 | PF 1.132213 | commission $12,709.40.
- UI/MCP parity: research/solar_wave_parity/type1_2023_2025/parity_report.md.

## Conventions that bite
- NT8 Analyzer "To = D" = last session ENDING ≤ D. For CME index futures pass `to` = one second before the next 18:00 ET open (22:59:59Z EST / 21:59:59Z EDT). Never "end of day D".
- Timestamps in payloads are exchange-session time (ET). Sessions 18:00 → 17:00 ET; strategy is flat at every session close, so daily realized PnL = daily MTM, and no trade ever spans a roll gap.
- Commission templates installed: "NinjaTrader Brokerage Free/Lifetime/Monthly" (no plain "NinjaTrader Brokerage").
- NT8 counts a position open at data end in TradesCount/NetProfit; a session-close exit exactly at the data boundary may be missing from the serialized trade list (engine totals unaffected).
- HOT-RELOAD: if a strategy class is recompiled, rename the class per iteration (…_v1, _v2) — NT8 may resolve the stale type (v1.13.3+ prefers freshest, still safer to version).

## Workflow
- Every run: immutable dir under `runs/<run_id>/` with spec.yaml written and committed BEFORE results are read. Never overwrite a run dir.
- Ingestion/analytics: `src/analytics/runlib.py` (payload → raw/metrics/trades.parquet/daily_equity.parquet/hashes + integrity audits).
- Registry: `research/registry/` (experiments.yaml, tested_configs.csv, hypotheses.md, rejected_ideas.md). Every tested config gets a sequence number.
- State: `research/CAMPAIGN_STATE.md` + `research/frontier.yaml` after every experiment.
- Reports: `reports/latest.md`, `leaderboard.md` (never ranked by net profit alone), `robustness.md`, `portfolio.md`.
