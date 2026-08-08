# NEXT_RESEARCH_QUEUE (priority order; refreshed 2026-08-08 end of V2 wave-1)

1. **One-contract confirmation wave (SMV2H2)**: preregister ΔSharpe/ΔCDaR bootstrap
   gate (P≥0.85) for A-dominant(≥5/≥7/≥9) vs SM14; add old-regime stress (2006-2021,
   Solar-only mode with B silent) and leave-one-year-out chronology. If passed →
   becomes ONE_CONTRACT_FINAL and gets SolarWaveSMOneLot_v2.cs.
2. **NT8 parity for OneLot v1** (Track D, blocked on F5 rebuild): Strategy Analyzer
   run + trade-by-trade reconcile vs canonical replay (NINJATRADER_PARITY.md).
3. **DAYONLY_DUAL6040 master build**: E10Master_v2 + tilt map + short-halving + BMOM
   virtual engine (~60-line delta on the F2 path per NINJATRADER_MASTER_SPEC.md).
4. **Third engine factory** (Track I short-list, each needs preregistered spec):
   VALUE-1 failed-trend VWAP reacceptance; VOL-1 compression→expansion day filter as
   B-MOM eligibility state; REL-1 ES/NQ relative state (ES 1-min substrate exists);
   MOM-6 morning-impulse→afternoon-continuation (distinct from B-MOM's anytime band).
5. **Winner-drought quantification** (directive §28): waiting-time distribution between
   top-decile Solar winners; DD conditional on drought; does 60/40 shorten TUW tails?
6. **Component risk contribution** (§23) for DAYONLY_DUAL6040: which leg owns the
   remaining −$18k DD; marginal CDaR contributions.
7. **Leverage re-run** for DAYONLY_DUAL6040 exact curve (SMV2F grid).
8. **Morning-state conditioning** (§27): loss concentration by time-of-day × side ×
   HTF across ALL years (not just 2026) before any exposure rule is proposed.
9. **ML trade-quality screen** (§29): logistic P(loss) on causal state features,
   nested chronological CV, distill-if-real.
10. Quarterly: MONITOR-01 #2 + SM13 B-MOM decay reading (≥2026-11-01, NOT a blocker).

## Deep-research passes A/B/C landed 2026-08-08 (Track I complete) — consolidated wave-2 picks
Full slates: deep_research/DR_V2_PASS_{A_AUCTION,B_DSP,C_RISK}.md. All EXTERNAL PRIORS;
local data decides; every item needs its own frozen spec + registry seq before any read.
- **W2-1 (curve reads, cheapest)**: C-P1 CDaR/EDaR/Ulcer static blend LP (validates or
  moves 60/40); C-P3 DD-constrained Kelly cap L*; C-P4 drought-tilt + placebo; C-P7
  windfall give-back event-study pre-test. [C-P2 normalizer leak-check DONE: no leak —
  vm scales are frozen constants.]
- **W2-2 (states, shared harness)**: B-H1 variance-ratio state + B-H3 efficiency ratio
  (keep one of the cluster); then B-H2 Kalman innovation-whiteness, B-H4 BOCPD regime age.
- **W2-3 (engine #3 candidates)**: A-H1 failed range-break fade + A-H3 small-gap fade
  (highest prior × cheapest falsification); A-H5 overnight drift as designated cheap kill;
  B-H10 OU fade gated by the VR state (cost pre-gate 3× friction BEFORE backtest).
- **W2-4 (convexity)**: C-P5 long-gamma NQ breakout sleeve (adds right tail; smile test).
