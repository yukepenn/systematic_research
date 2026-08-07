# Latest — 2026-08-06

**SW00_BASELINE_PARITY_COST: PASS.** Pipeline is deterministic (7 bit-identical canonical runs, incl. 2 concurrent); the Type-1 edge survives realistic costs (slip-1: net $118.6k, avg trade $40.83, PF 1.106, daily Sharpe 1.39; slip-3 still +$66.3k). Central discovery: **session-close exits (279 trades, PF 10.8) carry +$189.6k while Solar-trailing exits net −$42.8k** — the edge is concentrated in trends still running at the close, and the median trade gives back >100% of its MFE before the trailing exit fires. Execution modes benchmarked: native optimization sweeps validated bit-identical → Tier-1 discovery at ~4 s/combination.

Full report: `research/00_truth/SW00_report.md`. Next: SW01 signal/episode ledger exporter (read-only clone, no logic changes).
