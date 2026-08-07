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

---

## Wave 2 registrations and verdicts (2026-08-07)

- **H-006 - volatility-normalised threshold.** `S_episode = k*sigma_birth`, sigma causal, frozen at
  trend birth, clamped. **PASS.** Ensemble Sharpe 1.010 vs fixed 0.814, DD -$39,126 vs -$53,689,
  Calmar 0.958 vs 0.659, DSR 0.832 vs 0.677, positive every year. Confound controlled by a
  fixed-threshold sweep to SM 880 (Sharpe 0.805 - wider is NOT better) and by turnover-matched
  cell comparison. Survives the exposure check (32% less exposure but 61% more net per unit).
  Predicted in advance by DC02 from the price series alone. -> reference architecture **R5**.
- **H-007 - split exit != reversal distance.** **REJECT.** Monotone degradation at both SM 230 and
  SM 180; ratio 1.00 (no split) best everywhere. Mechanism: DC01 showed the payoff is a fat right
  tail over a median-losing distribution, so early exits amputate the only profit source while
  paying another ~$131 round trip. Also falsifies **DR03-H1**.
- **H-008 - anchor definition.** Raw High/Low extreme: **REJECT** (Sharpe 0.527 - the ladder
  chases wicks). Close-confirmed High/Low extreme: **PASS standalone** (0.947) but **redundant**
  with H-006 (combo 1.011 vs adaptive-alone 1.010). Both axes scale filter sensitivity to bar
  volatility; once the threshold is normalised the anchor refinement adds nothing. Simpler model
  promoted.
- **H-011 - resting stop orders at the ladder level.** **REJECT.** Negative in 10/10 cells
  (-$1.88M across the plateau). Close-based ladder state and intrabar fills desynchronise. Taken
  with H-008-mode-1's failure this establishes that the close-basis crossing excess (89% of all
  friction per DC01) is **not recoverable** - the close basis is a noise filter and the excess is
  what it costs.
- **H-012 (new, open) - sigma-estimator robustness.** Only one estimator (mean |dclose| over 460
  bars) and one clamp pair were tested for H-006. DR04-H3 predicts non-monotonic sensitivity to
  estimator lag. Falsifiable: at matched event count, sub-daily and multi-week estimators should
  both underperform a ~1-session estimator. Must be run before R5 is promotable.
- **H-013 (new, open) - ensemble weighting.** Everything so far uses 1/N. Preregistered
  alternatives: inverse-volatility, plateau-width weighting, and dropping members whose pairwise
  daily correlation exceeds 0.95. Pass condition: outer-fold Sharpe improvement that survives at
  equalised exposure; otherwise 1/N stands on complexity grounds.

**Standing conclusion (Wave 1c + Wave 2): parameter selection is not learnable in this family.**
PBO by family - fixed 0.631, anchor 0.689, adaptive 0.898, combo 0.481 - with a negative
in-sample -> out-of-sample slope in every case. Ensembles are the only defensible holding form,
and no finalist may be a single cell.
