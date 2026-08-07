# Campaign trial-accounting rule (preregistered)

_Written 2026-08-07, **before** any figure is recomputed under it. Binding on every past and
future wave. Motivated by the red-team finding that the published DSR figures paired
`n_trials = 255` with a variance pool drawn only from surviving cells — an internally inconsistent
combination that inflated every deflated Sharpe in the campaign._

## Why a rule is needed at all

The Deflated Sharpe Ratio needs two inputs: the number of trials `N` and the cross-sectional
dispersion `V` of trial Sharpes. Both were being chosen ad hoc, and the choice moved the answer
from 0.16 to 0.83 — a range wide enough to decide any promotion either way. That is not a
statistic, it is a dial. This document fixes the dial.

Two facts make the naive choice wrong in *both* directions:

- **Counting every configuration as an independent trial over-deflates.** The Wave-2 trials have a
  mean pairwise daily-P&L correlation of 0.295; the participation-ratio effective number of bets
  is 6.6. Treating 81 correlated sweeps of one parameter as 81 independent shots at the target
  implies a benchmark expected-max Sharpe of 1.42 — higher than anything ever observed in the
  campaign, i.e. it declares the entire research programme indistinguishable from noise by
  construction.
- **Drawing the variance only from survivors under-deflates**, because the rejected trials are
  exactly the low-Sharpe tail. Survivor-only dispersion was 0.216; the honest pool is 0.40–0.50.

Bailey and López de Prado explicitly recommend clustering correlated trials. The rule below does
that, and — critically — it is stated before the answer is known.

## The rule

**R1 — What counts as a trial.** Every configuration whose daily P&L vector was computed and
inspected, including rejected ones, including sweep iterations, including instrumentation runs
that were *also* read as results. Renaming a strategy class never resets the count. Runs that were
never inspected as candidate performance (pure parity gates, exporters, null-control machinery)
do not count, and each such exclusion must be named in the wave report.

**R2 — Clustering.** Trials are clustered by correlation of their daily P&L vectors on the union
calendar, using average-linkage agglomerative clustering on distance `d = sqrt(0.5·(1 − ρ))`, cut
at the number of clusters `K` given by the participation ratio of the correlation matrix
eigenvalues:

```
K = round( (Σ λ_i)² / Σ λ_i² )
```

This is the effective-number-of-bets estimator. It is a deterministic function of the data, so it
cannot be tuned after the fact.

**R3 — Effective trial count.** `N_eff = K`, computed over **all** trials from R1, campaign-wide,
not per wave. `N_eff` is recomputed from scratch each time it is quoted, and the wave report must
print both `N` (raw) and `N_eff`.

**R4 — Variance.** `V` is the variance of **cluster-representative** Sharpes, where each cluster's
representative is the equal-weight mean daily P&L of its members. Using cluster means rather than
individual cells is what makes `V` consistent with `N_eff`: both are computed on the same objects.
The pool includes clusters containing only rejected trials.

**R5 — Reporting.** Every DSR figure must be published as
`DSR(N_eff = k, V = v, pool = <description>)` with all three stated inline. A bare "DSR = x" is not
acceptable in any campaign document.

**R6 — Secondary haircut, always reported alongside.** Harvey–Liu Bonferroni and BHY at the raw
`N` from R1, reported as a haircut Sharpe. This is deliberately the harshest reasonable standard.
A candidate that clears R2–R4 but fails R6 is reported as "clears the clustered standard, fails
the Bonferroni standard" — never as simply passing.

**R7 — Promotion bar.** No result is promoted on a deflated Sharpe alone. DSR is a veto, not a
credential: `DSR < 0.90` under R2–R5 blocks promotion; `DSR ≥ 0.90` permits it only if the result
also clears the campaign's structural gates (connected region, ensemble form, positive-year
balance, right-tail retention, exposure normalisation, and an independent red-team pass).

## What this rule does NOT do

It does not rescue the withdrawn figures. It is expected to place the campaign's ensembles
somewhere near 0.85 under R2–R4 and to fail R6 outright, because a t-statistic near 2.0 over 4.6
years cannot survive a Bonferroni correction at N in the hundreds. **If that is the outcome, the
honest conclusion is that the historical record is too short to certify this edge by deflation,
and promotion must rest on structure, mechanism and out-of-sample portability instead.** That
conclusion is written here in advance so it cannot later be presented as a surprise or negotiated
away.

## Applies to

Every DSR/PSR figure in `WAVE1C_report.md`, `WAVE2_AXES_report.md`, `CAMPAIGN_STATE.md`,
`reports/*`, and all future waves. Implementation: `src/analytics/trials.py`.
