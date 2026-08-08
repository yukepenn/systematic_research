# Deep-research pass C (portfolio/downside-risk engineering), 2026-08-08 — EXTERNAL PRIORS, local data decides

Constraints honored: no trade-level stops, no post-loss exposure cuts (post-loss expectancy above base locally), no binary year-fitted regime filters. Shared machinery: stationary bootstrap (Politis-Romano) mean block ≈20d on the JOINT 2-engine daily vector (preserves the 0.04 losing-day corr); variants: within-year blocks; joint-loss blocks oversampled 2× (correlation-breakdown stress). Adopt only if median improvement AND ≥55-60% path win-rate AND LOYO sign stability AND plateau. **Right-tail capture (RTC) hard floor: policy PnL over champion's top-decile up-days ≥ 0.97× champion's own.**

## Ranked policies

**P1. CDaR-optimal static blend (EDaR/Ulcer cross-check) — rank 1.** LP: min CDaR₀.₉₀ over w ∈ [0.35,0.65] on vol-matched legs s.t. mean ≥ 95% of 60/40. Adopt only if CDaR/EDaR/Ulcer optima agree within ±7 pts. Fit 2022-24, evaluate 2025-26. If optimum ≈ 60/40, that's free validation of the champion. (Chekhlov-Uryasev-Zabarankin; Cajas EDaR.)

**P2. De-reactivize the vol-match normalizer — rank 2 (hygiene).** If vm() used trailing PnL vol, losses raise vol → hidden post-loss deleveraging. LOCAL CHECK 2026-08-08: our scales are FROZEN dev constants (0.6588/0.8270/0.9904/1.431), never trailing — the leak does NOT exist in the current construction. Standing rule: any future dynamic normalizer must be sign-blind range-vol (Garman-Klass/Parkinson) or frozen-while-underwater.

**P3. Drawdown-constrained Kelly base leverage (static) — rank 3.** L* = max L s.t. bootstrap P(maxDD$ over 2y > owner cap $25k) ≤ 10%; cross-check Busseti-Ryu-Boyd risk-constrained Kelly. Constant within year; kill if L* swings >25% under ±6mo perturbation. Anchors P9/P10.

**P4. Drought-tilt cross-engine reallocation — rank 4.** Monthly: tilt Δw = min(10, 2.5·z_TUW) pts TOWARD the engine deeper in drought (floors 0.35, total exposure unchanged). Monetizes post-loss-expectancy-above-base at the allocation layer + rebalancing premium (Willenbrock). Placebo control: random-sign tilts must show no comparable gain; leave-2022-out must keep sign. Expected TUW −10-25%.

**P5. Long-gamma NQ sleeve (discrete lookback-straddle replica) — rank 5.** 5-10% risk to an always-armed dual N-day breakout on MNQ (N ∈ [3,10]), session flatten, designed bleed ≤ $500/mo. The only line item that ADDS right tail. Pass: positive quadratic coefficient on weekly NQ returns (smile), negative corr to portfolio worst-decile days, CDaR cut net of bleed ≥60% path win-rate. (Fung-Hsieh lookback straddles; TSMOM smile; Harvey Best-of-Strategies.)

**P6. Latched sign-blind vol normalization — rank 6.** m_t = clip(σ*/σ̂,0.7,1.3), σ̂ = 20d RANGE vol (no PnL input); decreases only take effect after first non-negative day since signal (latch); hard floor m=1.0 when σ̂ pct >85 (never underweight into a spike). Conditional-vol-targeting evidence (Bongaerts et al. FAJ 2020); always-on version has the weakest OOS record — extremes-only is the defensible form.

**P7. Windfall give-back trim (gain-conditional only) — rank 7.** If trailing 5d PnL > +2.5σ: scale 0.8 for 5d; suspended when σ̂ pct >85. CHEAP PRE-TEST FIRST: event study — forward 5-10d PnL after +2.5σ windfalls vs base; if not below base, dead before building. Post-GAIN trims are locally untested (killed list covers post-loss only).

**P8. Continuous vol-percentile composition tilt — rank 8.** w_intraday = 0.5 + A·(logistic((p−c)/s)−0.5), exposure-constant, floors 0.35. Kill trigger: fitted s → 0 (logistic → step = the dead binary filter in disguise). (Gao-Han-Li-Zhou intraday momentum stronger on volatile days.)

**P9. Correlation-triggered defensive re-weight — rank 9 (insurance).** While rolling 60d losing-day ρ̂ > 0.25 (base 0.04): min-CDaR weights, suspend leverage add-ons; never below base. ~0 in-sample value — it's insurance against the diversification statistic being regime-local. Must fire <10% of days.

**P10. Up-only leverage ratchet, calendar decay — rank 10.** +5% steps on new equity highs when σ̂ pct <70, cap 1.2·L₀, month-end decay toward L₀; never removed on losses. Calmar objective (growth), low rank under owner DD hierarchy.

**P11. Dead-zone threshold rebalancing — rank 11 (enabler).** Rebalance at ±6 pt drift or month-end; kills churn, quantizes into MNQ contracts.

## Sequencing
P2 leak-check (DONE — no leak, scales frozen) → P1+P3 (static foundation, one bootstrap harness) → P4 + P7 pre-test (pure reads of existing daily curves) → P5 sleeve → P6/P8 only if static layer leaves >$15k maxDD. Cross-cutting cautions: always-on vol targeting weakest OOS; any policy acting near equity highs needs the vol-spike suspension because right-tail-concentrated engines put highs and spikes on the same days.

Key sources: Chekhlov-Uryasev-Zabarankin CDaR; Cajas EDaR; Harvey et al. vol targeting; Bongaerts-Kang-van Dijk conditional vol targeting; Moreira-Muir; Busseti-Ryu-Boyd risk-constrained Kelly; Fung-Hsieh; Moskowitz-Ooi-Pedersen; Kaminski-Greyserman; Willenbrock diversification return; Politis-Romano stationary bootstrap; AQR rebalancing; Goyal-Wahal.
