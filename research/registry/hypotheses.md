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

## DR05-H1 — overshoot / failed-flip calibration (Wave B01a, 2026-08-07)

**Verdict: FAIL on arm (b); arm (a) PASS.** Preregistered constants (DR-05.md,
frozen 2026-08): theta=179 ticks, failure < 0.25*theta within 60 min, 10-tick
margin. Arm (a): yearly mean overshoot 204.7–217.9 ticks, inside [0.5, 1.5]*theta
all five years — FX scaling-law unit transfers to NQ 1-min DC. Arm (b): failed
flips' median 60-min continuation −3.0 vs unconditional −1.0 ticks (diff −2.0,
required ≤ −10); worse in 3/5 years (required ≥4); pooled one-sided Mann-Whitney
p = 0.171 (required < 0.05). Consequence (binding, preregistered): DR05-H2 is
killed unbuilt; Wave B01 proceeds to B01c (ORB failure + value reacceptance),
which is not H1-conditional. Instrumentation seq 0; no R1 trial consumed.
Driver src/analytics/b01a_h1.py @ commit (pre-result).

## WAVE C01 Tier-0 (2026-08-07, instrumentation — 0 R1 trials; spec research/04_complementary_family/C01_WAVE_SPEC.md committed 6be945d BEFORE any read)

- **C01-T0-1 (SOLAR-01 short-regime separability): REJECT.** Ungated-state shorts are POSITIVE (+$204,626, t +0.35 — gate required t≤−2), G3-cell sign flips yearly (2023 −$57k / 2025 +$316k / 2026 −$233k), strict crisis retention 40.6% < 80%. Fallback sizing arm fails 2025 retention (63.9%). **Verdict: shorts are crisis insurance; keep symmetric. SOLAR-01 closed at Tier 0.**
- **C01-T0-2 (ML oracle capacity bound): PASS.** Counterfactual engine penny-exact at 0% filter (13/13 members). Gate cell ε=0.45 (~AUC 0.55): DD −72.7% at net −(−48.8%) [a gain]; 25/25 seeds pass; empirical break-even ε≈0.475 (analytic 0.4746). Capacity is generous because gross:net ≈ 13:1. **ML program proceeds to T0-6 feature screens** — capacity ≠ achievability; regime-clustered real errors are harsher than iid flips.
- **C01-T0-3 (DR03-H2 CUSUM drift allowance, stage 1): REJECT — DR03-H2 CLOSED.** State machine reproduced 99.997% (34,147/34,148 fills). Speed-tercile P&L profile insignificant (T3−T1 p=0.35), non-monotone for longs (V-shape), Spearman rank-inverted (+0.017). No k is warranted; flips are impulse-dominated (median fast-tercile age 4 bars).
- **C01-T0-4 (vol-surprise decomposition, SW08 refinement): PASS — Tier-1 exposure-rule sim unlocked.** Lag-1 U tercile hi−lo = +$396/session (p=0.0177 one-sided), same sign both halves, level does not subsume U (though ρ(U,level)=0.70 — Tier-1 must carry a vol-level control arm). Right-tail gate: top-1% P&L share in down-weight state 4.0% vs 30.8% session share — wide pass. Disclosed fragility: H1 economically zero; effect concentrated 2024+.
- **C01-T0-5a (announcement calendar): BUILT & COMMITTED ea6fe17** before any P&L read (145 events, official BLS/Fed sources, 2025 shutdown displacements captured). T0-5 analysis unblocked.
- **C01-T0-7 (overnight/intraday, Family D stage 1): GATE-DIVERGENCE RULING.** Execution packet's stricter t≥2 gate FAILS (conditional r_on t=1.20; conditioning adds nothing over base, Welch p=0.51); committed spec's letter (sleeve Sharpe ≥0.3, ≥3/5 yrs, corr ≤.25, no month >40%) nominally passes (0.64 / 4-of-5 / +0.066 / 27.5%). **Controller ruling: the committed spec governs preregistration, so Tier-1 eligibility stands formally, but is DEFERRED to last priority** given the packet fragilities (2025 net ≈ $0 with a −$20.3k month; unconditional NY-Fed falsifier upheld). No axis closure.
- **C01-T0-8 (VRP proxies, Family E gate): LITERAL PASS 2/3 (SVXY short-VX, VIX−RV) / Bonferroni-strict 0/3 on condition (b).** Controller ruling: formal unlock recorded, but any Family-E design phase requires a NEW preregistration whose first gate is condition (b) at proper significance, plus the asymmetric-sizing warning (all proxies' worst-decile days overlap E10 best-decile days 1.8–2.6×). Status: HOLD, low priority.
- **C01-T0-9 (surrogate ARL null): FAIL against the frozen gate.** 500/500 session-block surrogates; every registered statistic inside its band (drift p=0.09–0.34; net $/cycle 94.6th pct, p=0.054); surrogates reproduce r≈1.29 almost exactly → **r>1 is a within-session property; cross-session sequencing carries no information; threshold engineering permanently deprioritized** (frozen consequence — consistent with H-007/H-010/H-011/T0-3). Does not contradict SW01b (which tests entry timing within the real path).
- **C01-T0-10 (day-of-week negative control): EXPECTED NULL — no calibration alarm** (min p across six tests 0.115; alarm needed p<.05 in both halves). Pipeline does not manufacture significance. 4 DoF charged to control budget.
- **C01-T0-5 (announcement-day conditioning): REJECT — axis closed BOTH directions.** Effect exists but INVERTED vs hypothesis: announcement sessions −$138 vs +$214 matched control; FOMC significantly negative both halves (−$1,013 vs matched, p=0.014); paths trend MORE (r 1.352 vs 1.264) while P&L is worse — release-driven flips are badly timed churn (post-release −$111/trade vs pre +$74). NOT actionable: 20.5% of top-1% trades (24.2% of top-1% P&L) sit on announcement days (1.68× share) — any down-weight violates the hard right-tail constraint. Up-weight premise failed the gate. 0 trials.
- **C01-T0-6 (feature stability screens): PASS — Tier-1 ML arms unlock.** 5/8 fold-stable on the frozen hit-rate gate: consensus 5/5 (hit 0.266→0.387), prev-segment overshoot/θ 5/5 NEGATIVE (over-extended dying segments precede the worst entries, +$72→−$301), session bucket 5/5 (15:00–17:00 best 0.421, 18:00–02:00 worst 0.303), eff120 4/5, volvol 4/5 (both borderline). NOT stable: age, σ460, gap/ATR (3/5 each; reported, not selected out). Calibration caveat: 4/5-sign rule passes a null feature p≈0.375 — the PASS is carried by the three 5/5 features. Key structural finding: uniqueness-weighted mean trade is −$140 vs +$75 unweighted — profit lives in high-concurrency episodes; consensus is the load-bearing feature.

## WAVE C01 Tier-1 verdicts (2026-08-07; specs a0b8335 committed before execution; 6 R1 trials, seq 285-290)

- **C01T1_EXPOSURE: REJECT** (2 independent gate failures per arm). ARM_B (1.5×/0.5× on lag-1 U terciles): ΔlogG +0.554 but RW p=0.0556 (>0.05) and H1 sign NEGATIVE (−0.0035) — the effect exists only post-mid-2024, exactly the fragility T0-4 disclosed. For the record: both U-arms beat the vol-LEVEL control (surprise ≠ level confirmed), ARM_B improves Sharpe 0.950→1.132 / MAR 0.897→1.223 at only +9% DD — but regime-concentrated and insignificant. **Revival requires a mechanism explaining post-2024-only existence** (candidate: 0DTE-era vol-surprise dynamics), not a re-run.
- **C01T1_ML: REJECT — the honest branch fired.** Real, fold-stable signal EXISTS (OOS AUC 0.556–0.575 in 5/5 folds, well calibrated, coefficients stable: consensus +, prev_os −, volvol +) but is NOT monetizable via episode suppression: every probability-ranked cut is tail-adverse in the real error structure (ARM_A keeps 10.4% of top-1% tail, ARM_B 0.25%; T0-2's iid tail-neutrality did not transfer — its own disclosed caveat). Vol control dominates the ML sizing arm (p≈0.0075) but itself fails vs take-all (net −29%, tail retention 49.4% violates the hard right-tail gate). **Champion unchanged. ML overlay closed for suppression-style monetization; the AUC-0.56 state signal is knowledge, not a trade.**

**WAVE C01 CONCLUSION: closed with NO Pareto improvement — champion R5-E10 unchanged and further hardened.** 12 preregistered items, 6 R1 trials of the ≤10 budget consumed, 4 axes permanently closed (short gating, CUSUM-k, announcement conditioning, threshold engineering as a class), 2 deferred/hold (overnight sleeve — spec-letter eligible but fragile, ranked last and not run within this wave; Family E VRP — needs condition-(b) significance in a fresh preregistration). The wave's yield is scientific: σ-invariance (DC02b), within-session locality of the edge (T0-9), shorts-as-crisis-insurance (T0-1), the untradable-but-real FOMC drag (T0-5), and a real-but-unmonetizable AUC-0.56 state signal (T1-ML). This is a sixth consecutive wave without a Pareto improvement — the original convergence verdict is reinforced.

## Doors 1+2 execution (2026-08-07; specs 689da40 committed before execution; 0 R1 trials)

- **E10MASTER_V1: PASS — V1 EXACT / V2 CLOSE_WITHIN_TOLERANCE / V3 EXACT.** The champion now runs as ONE NinjaScript strategy (src/ninjascript/SolarWaveE10Master_v1.cs). Target parity: 0 diffs across 540,232 bars vs the audited simulator. Engine vs audited daily vector: corr 0.999921, net $181,079.10 = +0.96% (MNQ-vs-NQ back-adjust print basis, the preregistered tolerance). Costs to the cent: 52,126 contracts × $0.65/side exactly. Red-team objection #17 (sim-to-strategy gap) is CLOSED. Engine jobs: compile 28e3d162fee14c2e, full d1649fa25ab0453e.
- **MONITOR-01 reading #1 (baseline, window 2025-08..2026-07): NO ALARM.** Banded r 1.1966–1.2558, all ≫ 1.05 floor; drift inside 3×CV for the three mass bands; thin band (2.0,3.0] at −8.7% (1.1 SE) logged WATCH. Pipeline validated against DC02b exactly. Log: research/operational/monitor01_log.csv. Reading #2 due ≥2026-11-01 (fresh export).
- **C01T2_KSCALE: NO CLAIM — the director's own fee-arithmetic hypothesis FALSIFIED by the frozen rule.** K=1 anchor reproduced $179,361.36 to the cent first. K=2 per-NQ-eq Sharpe 0.7768 (−0.19 vs required ≥ +0.03): the trunc-block rule makes NQ/MNQ legs churn against each other at ±10-unit boundaries (+$29,657/NQ-eq vs the all-MNQ E20 counterfactual) — MORE than the theoretical max commission saving (~$22,454); and NQ slippage per unit equals MNQ's, so blocks can only ever recover commission, never slippage. Consequence: at K>1 the correct implementation is ALL-MNQ scaling (fee drag unchanged, linear); a hysteresis block rule is a NEW hypothesis with a ceiling of ~$22k/NQ-eq at K=2 and real churn risk — parked, fresh prereg required.
