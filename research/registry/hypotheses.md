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
  trend birth, clamped.
  > **SUPERSEDED 2026-08-07 — the verdict below is WRONG. Final verdict: INCONCLUSIVE.**
  > The comparison was not like-for-like: the fixed family was scored as two half-range ensembles
  > while adaptive got its full sweep. Scored fairly the advantage falls from +0.210 to **+0.087**
  > with paired block-bootstrap P(delta <= 0) = 0.358 (ex-2025: +0.046). **The DSR 0.832 quoted
  > below is one of the withdrawn figures** - it paired n_trials = 255 with a survivor-only
  > variance. Under the preregistered rule (`TRIAL_ACCOUNTING_RULE.md`) every candidate scores
  > 0.45-0.55 against a 0.90 bar. The original text is retained below because this log is
  > append-only and the constitution forbids erasing superseded results.
  > See `research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md` and CAMPAIGN_STATE section 8.

  ~~**PASS.**~~ Ensemble Sharpe 1.010 vs fixed 0.814, DD -$39,126 vs -$53,689,
  Calmar 0.958 vs 0.659, ~~DSR 0.832 vs 0.677~~, positive every year. Confound controlled by a
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

---

## Wave 3 registrations and verdicts (2026-08-07) — the frontier closes

- **H-012 - sigma-estimator robustness.** (registered above as open) **PASS.** Every estimator lag
  from 0.13 to 7.96 sessions gives Sharpe 0.769-1.494 with 11/13 cells positive in all five years.
  The 460-bar choice is not load-bearing. R5's remaining promotion gate cleared.
- **H-013 - ensemble weighting.** (registered above as open) **NOT RUN.** Superseded: once no
  comparative claim in the campaign could be separated from noise on 4.6 years, a weighting study
  had no chance of producing a defensible answer, and 1/N stands on complexity grounds as
  preregistered. Recorded as not-run, not as a failure.
- **H-014 - price-proportional vs volatility-proportional threshold.** The decisive control for
  H-006: if a *price*-normalised threshold worked as well, H-006's mechanism claim would be
  generic time-variation rather than volatility. **PASS - volatility wins by +0.728 Sharpe,
  p = 0.009** (price-proportional reaches only Sharpe 0.250; p = 0.999 against it). **The
  campaign's only clean significance result**, and the reason R5 is recommended despite failing to
  separate from R4: its mechanism is confirmed, not merely its point estimates.
- **ES portability.** **FAIL.** Blind transfer loses money (ES ensemble Sharpe -0.329,
  P(Sharpe <= 0) = 0.829). Shape travels (Spearman 0.780 across the threshold grid), level does
  not - the profitable region shifts to k >= 18 on ES, mechanically consistent with ES's $12.50
  tick. Constitution section 16 overfitting penalty applied, not explained away.
- **C2 - Type-1 core + one Type-3 re-entry.** **REJECT.** Best point estimates the campaign
  produced (+29% net, smaller DD, 2.5x better worst year, +$39.23/marginal trade) and still
  rejected on two independent grounds: session-block bootstrap P(mean <= 0) = 0.115, and it
  **reverses sign on an adaptive core** (-0.402 Sharpe, P = 0.879). A sleeve whose sign flips with
  the core is an interaction, not an effect.
- **C4 - adding Type 2 to the core.** **REJECT.** -0.33 Sharpe. Confirms Wave 1's "unconditional
  Type 2 is cost-fragile" from an independent direction.
- **C3 / C5 / C6 - remaining signal architectures.** **NOT BUILT.** With Type-2 dead (C4) and the
  wave selector dead (below), no mechanism remained to test. Recorded as not-run.
- **Wave-index conditioning.** **REJECT.** The Python screen showed clean monotone per-trade
  economics by wave ($26 -> $53 -> $76 -> $151); the engine gave **0.54-0.93, non-monotone**
  across MinWave 1-8. A textbook case of a screen effect dying under real execution, and the
  reason engine confirmation is mandatory before promotion.
- **DSR as a promotion criterion.** **ABANDONED.** Under the preregistered rule every candidate
  scores 0.45-0.55 against a 0.90 bar, with a Harvey-Liu haircut Sharpe of 0.000; a defensible
  alternative variance pool gives 0.96. The answer is dominated by a judgement call rather than by
  the data, so deflation adjudicates nothing here **in either direction**. This conclusion was
  written into `TRIAL_ACCOUNTING_RULE.md` *before* the figures were computed, and is honoured.

**Standing conclusion (Wave 3): every sleeve and conditioning axis is closed. R5 - the
volatility-normalised ensemble, Type-1 signals only - stands alone and unimproved.**

**Campaign-wide statistical pattern, stated as the log's final entry: every absolute-edge test
passed and every comparative test failed.** On 4.6 years of one instrument the data supports
"something is here" and refuses to say "this version is better than that one". That is why the
deliverable is an unselected ensemble and why nothing was promoted.
