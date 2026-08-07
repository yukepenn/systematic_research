# Finalist scorecards — POST_CAMPAIGN_AUDIT_01, AUDIT-A11

_2026-08-07. Classifications use the preregistered vocabulary. All figures
2022-01→2026-07-31, NQ 3-minute, Lifetime commission, slip-1 base unless noted.
Bases labeled REALIZED_ONLY / TRUE_MTM per constitution §10 (AUDIT-03 proved the
two coincide at session granularity for all flat-at-close members)._

## Canonical open reference (SolarWaveOpenV1, Type 1, 90/179, 1-minute)

**Classification: `REFERENCE` — re-verified.** Reproduces the frozen five-number
baseline to the penny on today's engine and data (AUDIT_GATE_R01/R02), with and
without the vendor indicator. Anchors all determinism claims.

## R5 theoretical (SolarWaveOpenV3, ThresholdMode 1, VolMult 6–30, strict 1/N)

**Classification: `STRONG_HISTORICAL_CANDIDATE — REPRODUCED`.**
- 13/13 members reproduced **fill-by-fill exactly** (AUDIT-02); the published
  recipe's `StartUp=true` is a documentation defect (actual: `StartUp=false`).
- Session TRUE_MTM: net $198,059, Sharpe 1.0642, DD −$39,853 (daily),
  **−$42,204 bar-level intraday**, ES5 −$3,983, TUW 1,112 of 1,184 sessions.
- Slip-2 stress: 87.4% net retained, paths unchanged ("halves net" claim corrected).
- Fill-resolution: no artifact (≤1.1% net effect, favorable on balance).
- Standing weaknesses (untouched by this audit): no clean OOS; ES portability
  failed; top-1% ≈ 160% of net; short side has no standalone edge; DSR
  inconclusive by preregistered rule.

## R5 executable — E10 (round(10 × mean member position) MNQ, max 10)

**Classification: `STRONG_HISTORICAL_CANDIDATE — EXECUTABLE, Family-A reference`.**
- Passes ALL preregistered AUDIT-04 gates: net $179,361 (90.6% of theory), Sharpe
  0.9671 (Δ −0.097 ≥ −0.10), DD −$41,252 daily (+3.5%), daily corr 0.9985,
  top-10-day retention 98.6%, mean |exposure| 0.278 NQ-eq (no hidden leverage).
- Verified cost stack: MNQ $0.65/side (empirical), 52,126 contracts traded,
  commission $33,882, slippage $26,063 at 1 tick.
- The margin: passing by 0.003 Sharpe is thin, and is reported as thin. The E13
  variant (perfect tracking) fails by 0.016. The economics, not the tracking,
  are the binding constraint; both facts go forward together.

## R5 executable — V4 flavor (tick-snapped S)

**Classification: `PERFORMANCE_SIMILAR_ONLY` sensitivity datapoint.** Not a
separate candidate. Matched-StartUp ensembles indistinguishable (corr 0.9952,
ΔSharpe +0.019, P=0.33); individual cells move up to −49%. Published V3/V4
comparison was StartUp-confounded (V3_V4_VERDICT.md); conclusion survives.

## R4 theoretical (fixed 21-cell, SM 170–880, strict 1/N)

**Classification: `SIMPLE ROBUST REFERENCE — NOT EXECUTABLE AT ACCEPTABLE COST`.**
- Session TRUE_MTM: net $159,424, Sharpe 0.9704, DD −$36,360 daily, −$39,494
  bar-level. Still the smallest max DD of the set at every granularity.
- Members not individually re-executed this audit (evidence: committed ledgers +
  engine determinism gates); flagged, not certified fill-by-fill.
- Every discrete executable variant fails the Sharpe gate (−0.17 to −0.24):
  the 21-member, higher-turnover structure pays ~3× commission under the MNQ
  schedule. R4 stays on the frontier as the simplicity/robustness anchor and as
  the challenger benchmark — not as a deployable implementation.

## ccHL anchor ensemble

**Classification: `INCONCLUSIVE — NOT RE-AUDITED`.** No re-execution or MTM/
executable work was performed on it in this audit (out of scope; historically
"PASS but redundant with R5"). Its published numbers remain campaign-reported.

## C2 sleeve

**Classification: `REJECTED` (unchanged).** Nothing in this audit touches the
interaction-test rejection.

## Cross-candidate verdict

The audit **separates R5 from R4 on executability** — the first ranking-relevant
separation between them that does not rest on a statistically insignificant point
estimate. Family-A reference for POST_AUDIT_TRANSITION = **R5-E10 executable**
with the R5 theoretical ensemble as its research proxy (corr 0.9985).
