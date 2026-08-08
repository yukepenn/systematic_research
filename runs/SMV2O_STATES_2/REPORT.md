# SMV2O_STATES_2 -- JOB1 information test (seq 375 Kalman whiteness, seq 376 BOCPD regime age)

Class: DIAGNOSTIC (V4.1 s2C -- no policy, no exposure rule). Spec frozen 2026-08-08 at 58dc2d2.
Executor: smv2o.py (this dir; SMV2J harness reused verbatim, states swapped). Artifacts:
out/harness_results.csv, out/state_correlations.csv, out/states_dev.csv, out/states_hist.csv,
out/meta.json. Every number below is read from those artifacts.

## Extra kill rule checked FIRST: |corr(state, sigma460)| > 0.7 (FACT, out/state_correlations.csv)

NOT TRIGGERED for any of the 12 cells. Max |corr(state, sigma460)| on the 880-session regression
sample = 0.183 (BOC_lam100; the other BOCPD cells -0.153/-0.155, all nine Kalman cells <= 0.072
in absolute value). The DR-pass-B worry that BOCPD regime age is a vol transition in disguise is
NOT borne out at these frozen cells: the correlation is mild and negative (older regime -> slightly
lower sigma460), nowhere near the 0.7 kill bar. Max |corr(state, HTF)| = 0.142. The kills below
are therefore NOT collinearity artifacts -- these are new directions that carry no significant
incremental signal.

## Verdict

| seq | family | verdict | one line |
|-----|--------|---------|----------|
| 375 | Kalman innovation whiteness (9 cells) | KILL | 0/9 cells reach abs(t_NW)>2 (best +1.33); t flips sign across the frozen grid, plateau rel-range 3.25 vs <0.30 required; one old-regime REVERSAL cell |
| 376 | BOCPD regime age (3 cells) | KILL | 0/3 cells reach abs(t_NW)>2 (best BOC_lam250 t=+1.83, boot same-sign 0.965 < 0.975); Q5-Q1 spread flips sign across the grid (spread rel-range 4.23) |

FACT -- clean kill, both families. Cluster rule moot (abs(corr(best KAL, best BOC)) = 0.132).
Per the frozen spec: with BOTH dead, the DSP JOB1 branch is exhausted per DR sequencing
(EMD rank 5 remains optional and requires a new EVI case). No JOB2 soft-weight spec is triggered.

## Harness sample (FACT, out/meta.json)

- Dev: 880 sessions, 2023-01-03 -> 2026-05-28, identical to SMV2J's sample (asserted in the
  executor -- reproduction check PASSED). Burn-in: 12 mo expanding-rank history from first
  session 2022-01-03. Dev substrate hard-filtered to sess_date <= 2026-05-31 before any
  computation (519,714 bars). No data >= 2026-06-01 touched anywhere.
- Old regime: 3,872 sessions, 2007-01-05 -> 2021-12-30 (12-mo burn-in from 2006-01-05),
  identical to SMV2J's hist sample.
- Identical regression sample across all 12 cells; bootstrap = moving-block over regression rows,
  block=5, B=10000, seed=20260808, identical draws reused for all 12 cells (SMV2J machinery).
- Leakage check (FACT): Kalman is a forward filter (innovation at bar k uses bars <= k); the LB
  window is the last M innovations ending at the last 3m bar of session t. BOCPD is a forward
  filter over blocks; the state is read after the last completed block of session t. beta0 uses
  only the first 12 months of each series, fully known before the quintile burn-in ends, so every
  state consumed by the harness is a function of data <= t only.

## Results -- 12 preregistered cells (primary outcome = next-session SOLAR_DUAL_HTF $)

| cell | corr s460 | t_NW(state) | boot P(b>0) | Q5-Q1 sprd $ | inv | test1 | hist sprd $ | hist t | test4 |
|------|-----------|-------------|-------------|--------------|-----|-------|-------------|--------|-------|
| KAL_qr1e-4_M50  | +0.02 | +0.83 | 0.761 |  +88.7 | 1 | pass |  +38.8 | +1.00 | FLAT |
| KAL_qr1e-4_M100 | +0.04 | +0.81 | 0.768 | +232.5 | 2 | fail |  +22.6 | +0.67 | FLAT |
| KAL_qr1e-4_M200 | +0.02 | +0.31 | 0.628 | +105.0 | 1 | pass |  -52.0 | -1.57 | REVERSAL |
| KAL_qr1e-3_M50  | +0.01 | +0.31 | 0.589 |  -10.9 | 2 | fail |   -4.6 | -0.14 | FLAT |
| KAL_qr1e-3_M100 | +0.05 | +0.40 | 0.627 | +214.8 | 1 | pass |  +32.0 | +0.98 | FLAT |
| KAL_qr1e-3_M200 | +0.03 | +1.08 | 0.851 | +344.0 | 2 | fail |  +23.4 | +0.68 | FLAT |
| KAL_qr1e-2_M50  | +0.06 | -0.39 | 0.343 |  -41.2 | 2 | fail |  -35.6 | -0.95 | FLAT |
| KAL_qr1e-2_M100 | +0.07 | +0.06 | 0.529 |  -58.4 | 1 | pass |  +23.6 | +0.66 | FLAT |
| KAL_qr1e-2_M200 | +0.05 | +1.33 | 0.896 | +230.2 | 2 | fail |  +21.7 | +0.70 | FLAT |
| BOC_lam100      | -0.18 | +1.65 | 0.935 |  -30.1 | 2 | fail |  +14.4 | +0.36 | FLAT |
| BOC_lam250      | -0.15 | +1.83 | 0.965 |  +11.0 | 1 | pass |  +19.9 | +0.51 | FLAT |
| BOC_lam500      | -0.15 | +1.72 | 0.960 | +138.9 | 1 | pass |  +13.5 | +0.34 | FLAT |

Full columns (quintile means, betas, secondary-outcome t, Welch t on spreads, plateau stats,
pass flags) in out/harness_results.csv.

### Test-by-test (FACT)

1. Monotonicity: KAL 4/9 pass, BOC 2/3 pass -- but passing directions are inconsistent within
   the KAL grid (qr1e-2_M100 negative spread, neighbors positive).
2. Incremental t (the decisive gate): 0/12 cells reach abs(t_NW) > 2 (Newey-West lag 5, controls
   z(sigma460) + HTF). Best cells: BOC_lam250 t = +1.835 (boot same-sign 0.965, below the 0.975
   confirm bar), KAL_qr1e-2_M200 t = +1.326 (boot 0.896). Secondary outcome (E10 dev,
   report-only): BOC_lam250 t = +2.13 and BOC_lam500 t = +2.03 do cross 2 there, but the gate is
   preregistered on the primary outcome and the family fails plateau regardless (see 3).
3. Plateau: KAL fails on both stats (t rel-range 3.25, spread rel-range 3.28; t changes sign
   across the grid). BOC passes the t rel-range (0.104 -- the t is remarkably stable in lambda)
   but fails the spread rel-range (4.23: Q5-Q1 flips from -30.1 at lam100 to +138.9 at lam500).
   Preregistered rule requires BOTH < 0.30 -> both families fail.
4. Old regime (2006-2021, E10 outcome): one REVERSAL -- KAL_qr1e-4_M200 (dev spread +105.0, hist
   -52.0 with Welch t -1.57). All other 11 cells FLAT (abs(hist t) < 1). Neither family's best
   cell reverses, but the reversal cell confirms the KAL family's sign instability.

### Correlations / cluster rule (FACT, out/state_correlations.csv)

- abs(corr(best KAL = KAL_qr1e-2_M200, best BOC = BOC_lam250)) = 0.132 -> cluster rule not
  triggered (and moot, both families KILL). Whiteness and regime age are near-orthogonal here.
- Extra kill rule: see top of report -- not triggered, max abs(corr with sigma460) = 0.183.

## Interpretation

- INFERENCE: Under the frozen harness neither "is the local level+trend model currently adequate"
  (LB whiteness of Kalman innovations) nor "how old is the current return regime" (BOCPD expected
  run length) adds statistically defensible incremental information about next-session Solar
  economics beyond sigma460 + HTF. With SMV2J's VR/ER kill, all four DSP JOB1 states are now dead;
  the branch is exhausted per DR sequencing.
- INFERENCE (pattern worth recording, not actionable): BOCPD regime age is the strongest loser in
  this program so far -- t is stable across the entire hazard grid (+1.65/+1.83/+1.72, rel-range
  0.104) and crosses 2 on the secondary E10 outcome. Direction: OLDER regime -> better
  next-session PnL, consistent with the campaign finding that the edge lives in established
  trends. But its quintile spread is grid-unstable and sub-significant on the primary gate, and
  the old regime is FLAT (hist t <= 0.51 everywhere) -- regime-local at best.
- HYPOTHESIS: if a JOB2-grade regime-age state exists, it is not E[run length] at these hazards;
  a monotone transform (e.g. P(run length < k)) might bucket better. No such cell is authorized
  here (12 cells, no extras) and nothing in this table justifies spending a new EVI case on it.

## Preregistered readings where the spec left details implicit (disclosed, none decision-critical)

1. Kalman: F=[[1,1],[0,1]], H=[1,0], R=1, Q=(q/r)*I2 -- standardized innovations depend on the
   q/r ratio only, so fixing R=1 loses nothing. Diffuse-ish init level=logc[0], trend=0,
   P0=1e7*I2; innovations start at bar 2 of the series; LB windows require k >= M (earliest
   session already qualifies; 12-mo burn-in makes the init transient irrelevant).
2. Ljung-Box: statsmodels acorr_ljungbox (0.14.1), lags=[10], Q statistic (spec-mandated
   function); state = lb_stat over the last M standardized innovations.
3. BOCPD blocks: within each session, consecutive non-overlapping 10-bar groups anchored at the
   session's first bar; block return = logc[last bar of group] - logc[anchor], anchor = previous
   session's last bar for the first group (overnight gap included), else the previous group's
   last bar. Trailing <10-bar remainders dropped (dev: 25/1139 sessions; hist: most sessions,
   so the hist state is read up to 9 bars = 27 min before the close -- still causal). Dev blocks
   51,956; hist blocks 174,623.
4. BOCPD prior: kappa0=1, alpha0=2, mu0=0; beta0 = variance (ddof=1) of block returns over the
   first 12 months of each series (dev 5.435e-06, hist 3.103e-07) -- under IG(alpha0,beta0),
   E[sigma^2] = beta0/(alpha0-1) = beta0, i.e. prior expected variance = empirical first-12mo
   variance ("scale from first 12mo").
5. Run-length truncation at 2000: cap bin = "run length >= 2000"; growth into the cap is merged
   mass-weighted on mu/beta (weights normalized before multiplying -- see incident below);
   kappa/alpha at the cap are pinned at their r=2000 values. E[run length] uses r=2000 for the
   cap bin.
6. Extra-kill correlation = Pearson corr of daily state vs sigma460 on the 880-session regression
   sample (same matrix as the cluster rule; written to out/state_correlations.csv).
7. FLAT/REVERSAL threshold as in SMV2J (FLAT = abs(Welch t) < 1). The single REVERSAL cell
   (KAL_qr1e-4_M200, hist t = -1.57) stays a reversal for any threshold up to abs(t) >= 1.5 and
   is not the family's best cell; no verdict is sensitive to this reading.

## Numerical incident (disclosed; fixed before any results were read)

The first execution of smv2o.py died on the preregistered reproduction check (regression sample
truncated to 595 sessions ending 2025-04-22 instead of SMV2J's 880 ending 2026-05-28). Root
cause, found with debug_nan.py (this dir): in the BOCPD cap-bin merge, the raw mass weights of
the two merging hypotheses are denormal-tiny during the April-2025 vol shock, so
(wa*beta_a + wb*beta_b)/tot underflowed to beta_cap = 0 exactly -> predictive scale 0 ->
inf - inf = NaN at block 38,930 (session 2025-04-23), permanently poisoning the recursion. Fix:
normalize the weights BEFORE multiplying (fa = wa/tot; beta_cap = fa*beta_a + (1-fa)*beta_b) --
identical mathematics, numerically stable. No gates, grids, priors, or data were changed; the
rerun passed the reproduction check (880 sessions, dates matching SMV2J exactly) with no
numerical warnings. No results from the failed run were read beyond the crash traceback.

## Machinery (frozen, for reproduction)

- OLS: statsmodels 0.14.1, cov_type=HAC, maxlags=5. Bootstrap: moving-block over regression rows,
  block=5, B=10000, seed=20260808, identical block draws reused for all 12 cells.
- Quintiles: expanding rank inclusive of current value, quintile = ceil(5*rank_pct), 12-mo
  burn-in, no full-sample scaling anywhere. z-scores in the regression are sample-affine
  transforms only (t-stats invariant).
- Outcomes taken as-published from runs/SMV2H_ONECONTRACT (DUAL_HTF daily $), runs/SM01_SUBSTRATE
  (E10 dev), runs/SM06_SOLAR_HISTORY (E10 hist). No re-simulation performed. No data dated
  >= 2026-06-01 used anywhere (dev filter asserted; primary outcome file ends 2026-05-29).
