# SMV2J_STATE_HARNESS -- JOB1 information test (seq 366 VR, seq 367 ER)

Class: DIAGNOSTIC (V4 s27 -- no policy, no exposure rule). Spec frozen 2026-08-08.
Executor: smv2j.py (this dir). Artifacts: out/harness_results.csv,
out/state_correlations.csv, out/states_dev.csv, out/states_hist.csv, out/meta.json.
Every number below is read from those artifacts.

## Verdict

| seq | family | verdict | one line |
|-----|--------|---------|----------|
| 366 | B-H1 variance-ratio (9 cells) | KILL | 0/9 cells reach abs(t_NW)>2; t-values flip sign across the frozen grid (plateau rel-range 5.43 vs <0.30 required) |
| 367 | B-H3 efficiency-ratio (3 cells) | KILL | 0/3 cells reach abs(t_NW)>2 (best ER_n460 t=-1.74, boot same-sign 0.970 < 0.975); plateau rel-range 3.60 |

FACT -- clean kill. No trend-quality cell adds significant incremental information about
next-session SOLAR_DUAL_HTF PnL beyond sigma460 + HTF. Cluster rule moot (both families dead;
abs(corr(best VR, best ER)) = 0.179 anyway). Per DR sequencing, the Kalman/BOCPD queue advances.
No JOB2 policy spec is triggered.

## Harness sample (FACT, from meta.json)

- Dev: 880 sessions, 2023-01-03 -> 2026-05-28 (state at t predicts PnL of t+1; last usable t
  predicts 2026-05-29). Burn-in: 12 mo expanding-rank history from first session 2022-01-03.
  Dev substrate hard-filtered to sess_date <= 2026-05-31 before any computation (519,714 bars).
- Old regime: 3,872 sessions, 2007-01-05 -> 2021-12-30 (12-mo burn-in from 2006-01-05).
- Identical regression sample across all 12 cells (asserted). Sessions taken from the daily PnL
  files; substrate/primary/secondary session date-sets match exactly (asserted in executor).
- Leakage check (FACT): every state window is trailing and ends at the last 3m bar of session t
  (r[k-N:k], absd[k-n:k] end at bar k = session-t close); outcome is the PnL of the next row
  in the PnL file's own session sequence.

## Results -- 12 preregistered cells (primary outcome = next-session SOLAR_DUAL_HTF $)

| cell | t_NW(state) | boot P(beta>0) | Q5-Q1 sprd $ | inv | test1 | hist sprd $ | hist t | test4 |
|------|------------|----------------|--------------|-----|-------|-------------|--------|-------|
| VR_q6_N390   | +1.11 | 0.872 | +189.9 | 1 | pass | -11.1 | -0.35 | FLAT |
| VR_q6_N780   | -0.37 | 0.359 |  +60.1 | 3 | fail | -32.5 | -1.00 | FLAT |
| VR_q6_N1950  | +0.02 | 0.478 | -179.3 | 1 | pass | +20.3 | +0.63 | FLAT |
| VR_q12_N390  | +0.11 | 0.567 |   -3.4 | 2 | fail |  -4.5 | -0.15 | FLAT |
| VR_q12_N780  | -1.09 | 0.139 | -146.6 | 2 | fail | -38.0 | -1.17 | SAME_SIGN |
| VR_q12_N1950 | -0.68 | 0.245 | -248.6 | 1 | pass |  -8.7 | -0.27 | FLAT |
| VR_q26_N390  | -1.05 | 0.158 | -124.1 | 1 | pass | -66.6 | -1.89 | SAME_SIGN |
| VR_q26_N780  | -1.65 | 0.050 | -218.8 | 2 | fail | -51.3 | -1.60 | SAME_SIGN |
| VR_q26_N1950 | -0.98 | 0.168 | -228.7 | 2 | fail | -48.7 | -1.59 | SAME_SIGN |
| ER_n60       | +0.74 | 0.730 | +282.3 | 1 | pass | +36.8 | +1.09 | SAME_SIGN |
| ER_n150      | -1.06 | 0.136 | -236.8 | 1 | pass | -49.8 | -1.52 | SAME_SIGN |
| ER_n460      | -1.74 | 0.030 | -387.7 | 1 | pass | -67.7 | -1.88 | SAME_SIGN |

Full columns (quintile means, betas, secondary-outcome t, Welch t on spreads, plateau stats,
pass flags) in out/harness_results.csv.

### Test-by-test (FACT)

1. Monotonicity: 7/12 cells pass (<=1 adjacent inversion), but the passing direction is not
   even consistent within the VR family (q6 cells trend positive, q12/q26 negative).
2. Incremental t (the decisive gate): 0/12 cells reach abs(t_NW) > 2 (Newey-West lag 5,
   controls z(sigma460) + HTF). Best cells: ER_n460 t = -1.744 (boot same-sign 0.970, below the
   0.975 confirm bar), VR_q26_N780 t = -1.653 (boot 0.950). Secondary outcome (E10 dev,
   report-only): best abs(t) = 2.02 (VR_q26_N780, -2.024) -- the gate is preregistered on primary.
3. Plateau: fails for both families by an order of magnitude. Rel-range of t across the
   family's own grid: VR 5.43, ER 3.60 (spread rel-range 4.39 / 5.87) vs < 0.30 required.
   t-values change SIGN across both grids -- the opposite of a plateau.
4. Old regime (2006-2021, E10 outcome): zero sign reversals. 8 SAME_SIGN / 4 FLAT under the
   preregistered reading (FLAT = abs(Welch t) < 1; REVERSAL = opposite sign AND abs(t) >= 1).
   The three opposite-sign cells (VR_q6_N390, VR_q6_N780, VR_q6_N1950) all have hist abs(t) < 1,
   so no cell is a reversal under any threshold up to abs(t)>=2 -- the kill decision is not
   sensitive to this reading.

### Correlations / cluster rule (FACT, out/state_correlations.csv)

- abs(corr(best VR = VR_q26_N780, best ER = ER_n460)) = 0.179 -> cluster rule not triggered (and
  moot, both families KILL). Note the DR-pass prior that H1/H3 form one cluster is NOT borne out
  at these frozen grids: the two families are nearly orthogonal here.
- All 12 states are nearly orthogonal to the deployed states: abs(corr with sigma460) <= 0.066,
  abs(corr with HTF) <= 0.14 (matrix in artifact). The kill is therefore not "explained away by
  collinearity with existing controls" -- the states are new directions that simply carry no
  significant signal.

## Interpretation

- INFERENCE: Under the frozen harness, trend-quality (VR or ER form) at session close adds no
  statistically defensible incremental information about next-session Solar economics. The
  in-family sign instability (test 3) plus 0/12 on the t-gate indicates noise fit, not a weak
  true effect at the wrong grid point.
- INFERENCE (pattern worth recording, not actionable): the longer-window cells
  (q26 VR; ER_n150/460) show a weakly NEGATIVE spread -- high measured trendiness at t ->
  lower next-session DUAL_HTF PnL -- with the SAME sign in 2006-2021 (hist t up to -1.9). It is
  sub-significant everywhere in dev, and dies on plateau.
- HYPOTHESIS: that faint anti-trend-quality pattern could be a real but small mean-reversion-
  of-trendiness effect; if it ever matters it would surface in the Kalman/BOCPD queue with a
  properly filtered state, not by re-gridding these estimators (no re-grid is authorized).

## Preregistered readings where the spec left details implicit (disclosed, none decision-critical)

1. VR state = Lo-MacKinlay heteroskedasticity-consistent statistic psi*(q) =
   sqrt(T)*(VR-1)/sqrt(theta*), theta* = sum_j (2(q-j)/q)^2 * delta_j (CLM 1997 eq. 2.4.43-44)
   (spec: "heteroskedasticity-consistent centering"); raw VR values archived in states_dev.csv.
   The quintile tests are rank-based, so VR vs psi* differ only through the time-varying
   theta normalization.
2. Bootstrap "confirm" = same-sign fraction >= 0.975 (two-sided-5% analogue of abs(t)>2). Moot:
   no cell passed the primary t-gate.
3. Plateau stat = (max-min)/abs(family mean) for both t and spread; fail if either >= 0.30.
4. FLAT/REVERSAL threshold as stated above; verified insensitive.
5. HTF control = sign(close_t - SMA50 of session closes at t) -- exactly the value the deployed
   DUAL_HTF strategy uses during session t+1 (smv2h.py applies it via shift(1) to session t+1
   bars).
6. Hist substrate has 128 pre-2012 sess_dates containing two NT sessions; state computed at the
   last bar per sess_date (guidance-sanctioned option: "is_last_of_sess in the substrate or last
   bar per sess_date"), matching the one-row-per-date keying of e10_daily_hist.csv. On dev the
   two definitions coincide exactly (1139 sessions, one last-flag each; asserted).

## Machinery (frozen, for reproduction)

- OLS: statsmodels 0.14.1, cov_type=HAC, maxlags=5. Bootstrap: moving-block over regression rows,
  block=5, B=10000, seed=20260808, identical block draws reused for all 12 cells.
- Quintiles: expanding rank inclusive of current value, quintile = ceil(5*rank_pct), 12-mo
  burn-in, no full-sample scaling anywhere.
- z-scores in the regression are sample-affine transforms only (t-stats invariant); no
  full-sample scaling enters any ranked/bucketed quantity.
- Outcomes taken as-published from runs/SMV2H_ONECONTRACT (DUAL_HTF daily $), runs/SM01_SUBSTRATE
  (E10 dev), runs/SM06_SOLAR_HISTORY (E10 hist). No re-simulation performed. No data dated
  >= 2026-06-01 used anywhere (dev filter asserted; primary outcome file ends 2026-05-29).
