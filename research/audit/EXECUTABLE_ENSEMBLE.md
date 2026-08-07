# Executable ensemble construction — POST_CAMPAIGN_AUDIT_01, AUDIT-A06

_2026-08-07 · driver `src/analytics/audit04_run.py` (+ `audit04_executable.py`) ·
verified member ledgers (AUDIT-02 EXACT) · validated bar series (AUDIT-03) ·
MNQ Lifetime commission **$0.65/side ($1.30/RT), verified empirically** in
`runs/AUDIT04_MNQ_PROBE` (constant across 704 fills) · NQ $2.18/side · 1-tick
slippage per execution per contract on net target changes · all results
session-basis TRUE_MTM._

## Headline verdict

**R5 is executable: the E10 implementation (target = round(10 × mean member
position) MNQ, max 10) passes the preregistered gates — by a thin 0.003-Sharpe
margin on the session basis, and the pass is robust to the unpreregistered
micro-choices (second red team): round and floor(-toward-zero) rules pass on BOTH
the session and calendar bases (margins 0.003–0.012); only the cost-maximizing
ceil rule fails. Sensitivity table: `e10_sensitivity.csv`; committed daily
vectors: `e_variant_daily_vectors.csv`.**
**R4 is NOT executable at acceptable cost: every discrete R4 variant fails the
Sharpe gate by 0.17–0.24 — a wide margin.** The R4-vs-R5 question that p = 0.358
could not settle is settled asymmetrically by execution economics: R5's lower
turnover survives the MNQ fee schedule (marginally), R4's does not (decisively).
Disclosure: the thesis prescribed one "MNQ-discretized target"; the audit computed
three discretizations (E13/E10/E20) and designates E10 — the direct reading of the
thesis's target-then-round prescription — as the implementation. The alternates
are published above with FAIL verdicts; the designation itself is recorded as a
design-choice event in `SECOND_RED_TEAM.md`.

## Results (strict gates: ΔSharpe ≥ −0.10, net ≥ 80%, DD ≤ +20%, top-10 retained, no hidden leverage)

### R5 adaptive 13-member (E0 reference: net $198,059, Sharpe 1.0642, DD −$39,853)

| variant | net | vs E0 | Sharpe | Δ | max DD | corr | top-10 ret. | commission | slippage | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| E1 continuous (diagnostic) | $198,724 | 100.3% | 1.0678 | +0.004 | −$39,797 | 1.000 | 100.0% | $11,238 | $25,775 | PASS |
| E13 (13 MNQ, 1/member) | $176,455 | 89.1% | 0.9479 | −0.116 | −$41,269 | 1.000 | 99.9% | $33,507 | $25,775 | FAIL (Sharpe, by 0.016) |
| **E10 (round(10·mean) MNQ)** | **$179,361** | **90.6%** | **0.9671** | **−0.097** | **−$41,252** | **0.9985** | **98.6%** | **$33,882** | **$26,063** | **PASS** |
| E20 (granularity diag., /2) | $173,783 | 87.7% | 0.9353 | −0.129 | −$41,299 | 0.9997 | 99.6% | $33,784 | $25,988 | FAIL (Sharpe) |
| E3 mixed NQ/MNQ (naive) | $163,113 | 82.4% | 0.8835 | −0.181 | −$41,723 | 0.9984 | 98.0% | $40,880 | $35,314 | FAIL (Sharpe) |

### R4 fixed 21-member (E0 reference: net $159,424, Sharpe 0.9704, DD −$36,360)

| variant | net | vs E0 | Sharpe | Δ | verdict |
|---|---:|---:|---:|---:|---|
| E1 continuous (diagnostic) | $160,414 | 100.6% | 0.9765 | +0.006 | PASS |
| E21 (21 MNQ, 1/member) | $131,178 | 82.3% | 0.7981 | −0.172 | FAIL |
| E10 | $130,022 | 81.6% | 0.7894 | −0.181 | FAIL |
| E20 | $131,780 | 82.7% | 0.8023 | −0.168 | FAIL |
| E3 (naive) | $119,222 | 74.8% | 0.7262 | −0.244 | FAIL (Sharpe + net) |

## Cost decomposition — where the executable penalty comes from

1. **Rounding/granularity is a non-issue.** E10's mean rounding error is 0.024
   NQ-equivalents (max 0.046); daily corr with theory 0.9985; position-path corr
   0.9974; top-10-day retention 98.6%. The fractional-member objection to R5 is
   answered: a 10-MNQ ladder tracks the 13-member mean almost perfectly.
2. **The MNQ commission multiple is the entire economic penalty.** Ten MNQ cost
   $13.00/RT where one NQ costs $4.36/RT (2.98×). E10 commission $33,882 vs the
   theoretical $11,453 — a ~$22.4k drag ≈ 11% of net ≈ 0.10 Sharpe. Slippage per
   NQ-equivalent is identical ($26.1k vs $26.3k).
3. **Internal netting is real but small at this scale**: E1 saves ~2% of costs
   (members rarely oppose each other; mean |ensemble position| = 0.27 NQ-eq,
   max 1.0). Netting savings would grow with capital scale (multiple NQ-equivalents
   → whole-NQ blocks at $4.36).
4. **E3 as implemented is a lower bound**, not the optimum: its naive 10-MNQ↔1-NQ
   conversion churns. A hysteresis-band mixed policy is future optimization work,
   out of audit scope; it cannot beat E1's cost floor.
5. **Scale note (not a result, arithmetic):** at K NQ-equivalents the fixed-fee
   penalty shrinks: whole-NQ blocks carry the $4.36 rate and only the fractional
   remainder pays micro rates. The E10 numbers are the worst case (all-micro at
   1 NQ-equivalent average).

## Consequences for the campaign

- **Family-A executable reference = R5-E10**, frozen as:
  `13 × SolarWaveOpenV3 (StartUp=false, ThresholdMode 1, VolMult 6..30) virtual
  members → target = round(10 × mean position) MNQ, max 10, net-change execution,
  session-close flatten` with the measured cost stack above. TRUE_MTM Sharpe 0.9671,
  net $179,361, bar-level intraday DD −$41,252 (2022-01→2026-07).
- **R4 remains a theoretical robustness reference only.** Its executable forms fail
  preregistered gates; it must not be quoted as a deployable alternative without a
  cost-engineering breakthrough.
- The published R5 "avg trade $5.80/ensemble-unit" statistic should never again be
  compared with full-contract costs; the executable statistics above replace it.

## Files

`executable_ensemble_metrics.csv` (full table incl. ES/TUW/worst-day),
`netting_cost_attribution.csv`, `position_rounding_diagnostics.csv`;
simulation code `src/analytics/audit04_executable.py` (physical-instant timeline,
open-phase vs session-close-phase execution, slippage-cap-aware raw prices).
