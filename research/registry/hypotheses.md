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
