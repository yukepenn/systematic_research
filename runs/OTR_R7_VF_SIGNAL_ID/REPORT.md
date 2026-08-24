# OTR_R7 report — VF signal structural identification, pass 1 (2026-08-24)

144 members × 17 windows (out/r7_grid.csv, out/r7_summary.csv). §40 distance,
no free constants, DQ if profitable in the 3/22-27 −42,235 failure week.

## Pass-1 verdicts
1. **Close-threshold reading H1a (signal candle closes in the extreme 10%
   TOWARD the signal) dominates**: the entire top-15 is H1a. H1b (extreme
   AGAINST) is degenerate (near-zero trades; bottom of the table) — REJECTED.
2. Best member T_C|P_MED|C_DIR|H1a|X_OPP (trend = close-vs-FairValue + EMA20
   slope agreement; pullback to Median; directional close; SAR on opposite
   signal): mean 0.476, worst 0.905, failure week −9,730 (right sign, 23% of
   magnitude), 1,722 trades vs ~1,214 target total.
3. DQ rule fired: T_C|P_MED|C_REC|H1a|X_OPP (mean 0.479) is PROFITABLE
   (+2,970) in the failure week → disqualified per §32 despite rank 2.
4. Residual remains structural: best mean distance 0.476 ≈ the R3 clone
   plateau; trigger-level composition still not matched.

## Why a pass 2 is preregistered (amendment 1)
Public recon (same-day) changed the hypothesis space:
- The vendor manual's verbatim orientation is the INVERSE of H1a: for a sell,
  "(Close − Low) ≥ T%" → at the trader's T=10 the filter barely binds (H1c,
  ≈90% of candles pass). H1c was not in the pass-1 grid and must be tested
  against H1a rather than assumed either way.
- Official changelog: Signal_Trend upgraded 2-state→4-state (±2/±1 strength)
  on 2026-02-24 — mid-sample; Signal_Cum_Delta added 2026-02-09; staff forum
  teaches VF-direction + delta-confirmation composition. → version-aware
  strength/delta gating members are motivated by evidence, not tuning.
