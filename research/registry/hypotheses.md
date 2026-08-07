# Hypothesis log (append-only)

## H-001 (SW00) — 2026-08-06 — SUPPORTED (PASS; see research/00_truth/SW00_report.md)
The canonical Type-1 baseline's historical edge survives realistic execution friction, and the MCP backtest pipeline is deterministic. Falsified if: reruns are non-identical, or 1-tick/execution slippage eliminates positive expectancy. Mechanism: costs are additive per execution (~$10/RT/tick on NQ); the edge (avg trade $50.24 incl. commission) must clear them. Preregistered gates: research/00_truth/SW00_spec.md.

## H-002 (SW01c) — 2026-08-06 — SUPPORTED-THIN (slip1 +$11,385.72 > 0; shorts carried bear year; forward prior downgraded)
Canonical config retains positive slip-1 expectancy in the never-examined 2022 bear regime. Falsified if slip-1 net <= -$15k. Gates: research/01_diagnostics/SW01c_spec.md.

## H-003 (SW01b) — 2026-08-06 — NULL REJECTED p=0.0323 (entry timing real; machinery alone = median $58.6k in-regime)
NULL to reject: Type-1 entry timing adds nothing beyond exit machinery + drift (random matched-frequency entries, identical exits). Rejection: baseline > all 30 mode-0 seeds (p<=0.032). Gates: research/01_diagnostics/SW01b_spec.md.

## H-004 (SW01) — 2026-08-06 — PASS (byte-identical export; 100% signal-trade match)
Deterministic bar/state ledger joins cleanly to the trade ledger and localizes PnL/giveback/loss clusters. Integrity-falsified if export nondeterministic or signals inconsistent with executed trades. Gates: research/01_diagnostics/SW01_spec.md.

## H-005 (SW02a) — 2026-08-06 — REGISTERED (next)
The close-bucket edge survives replacing exit-on-session-close with an explicit timed market exit at 16:55 ET (same fill mechanism backtest and live). Falsified if the 279-trade close-bucket net collapses (>50% loss) at 16:55 — which would mark the absolute edge as a last-print artifact. Ladder: 16:58/16:55/16:45/16:30. Origin: external review §3.1.

## H-006 (RE01 / Wave 2) — 2026-08-07 — REGISTERED
Solar Wave RK's reversal distance is a CONSTANT tick count, so its effective selectivity drifts with the market: 44.75 NQ points was 17.8 per-bar-vol units in 2023 but only 10.4 in 2025 (−41%), and fell from 0.255% to 0.196% of price. HYPOTHESIS: replacing the constant S with a causal, trend-birth-frozen volatility-scaled distance S_t = k·sigma_t produces (a) more even per-year P&L distribution and (b) a flatter, wider robust plateau in k than the fixed-tick StopMultiplier plateau, because k is regime-invariant where ticks are not. Falsified if, on dense matched-trade-count scans through the NT8 pipeline over 2022→2026, the adaptive family shows no improvement in worst-year net, positive-year %, or neighbourhood stability versus fixed-tick. Prior evidence (close-fill Python screen, ledger window only): NOT a free win in aggregate — fixed and adaptive trade blows at matched trade counts, both dominated by path noise — but adaptive k=14 spread P&L $85k/$46k/$29k across 2023/24/25 vs fixed-179's $26k/$116k/$24k (70% in one year). Instrument: solar_wave_adaptive() in src/analytics/solarwave.py; NinjaScript variant required for the real test. Origin: research/03_reverse_engineering/SOLARWAVE_MATH.md §5.

## H-007 (Wave 2) — 2026-08-07 — REGISTERED
In the vendor design ONE distance does two jobs: it is simultaneously the trailing exit and the entry trigger for the opposite side, which is why the strategy skips ~46% of signals (it exits on the flip bar and returns before entering). HYPOTHESIS: splitting them — reverse at S_r, exit at S_x != S_r — is a genuinely new degree of freedom unreachable with the vendor binary, and a wider exit than reversal distance improves net after costs by reducing forced round-trips. Falsified if the best (S_r, S_x) surface has its optimum on the diagonal S_x = S_r within neighbourhood noise. Reachable only because of RE01.
