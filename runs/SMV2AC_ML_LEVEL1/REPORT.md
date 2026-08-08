# SMV2AC_ML_LEVEL1 — Level-1 interpretable ML screen (seq 413–414)

Frozen spec: `runs/SMV2AC_ML_LEVEL1/spec.yaml` (committed `2bf5a4f`, read before any write).
Script: `runs/SMV2AC_ML_LEVEL1/smv2ac.py`. All numbers below are FACT and trace to a file under
`runs/SMV2AC_ML_LEVEL1/out/` unless explicitly marked INFERENCE or HYPOTHESIS.

## Verdict: **KILL**

FACT — `out/promotion_test.csv` row `PROMOTION_TEST_PASS = False`. The joint 5-feature model's
OOF log-loss does **not** beat the ER150-only baseline at the program's 0.85-confidence bar:
`bootstrap_P_improvement_gt_0 = 0.6256` (paired moving-block bootstrap, block=4 weeks, B=10000,
seed=20260808). Per the spec's own `kill_or_keep` rule this is a clean KILL — "Level 1
interpretable modeling adds nothing beyond the single best state already found" — and per V4
s30/33 the escalation ladder **stops here**; no trees/DL/GAM follow-on is licensed by this
result.

---

## 1. Data and feature construction (FACT)

- Target: `runs/SMV2Y_JOINTLOSS_VIABILITY/out/target_series.csv`, column `joint_loss_next`
  (binary next-week joint-loss). Column presence verified programmatically before use
  (`out/run_log.txt` line 1-2), including a cross-check of `runs/SMV2J_STATE_HARNESS/out/
  states_dev.csv`'s `VR_q26_N780` / `htf` / `ER_n150` / `sigma460` columns that
  `target_series.csv` was itself built from.
- Features (5, all pre-computed, no new engineering): `state_399_sigma460`,
  `state_400_ER150`, `state_401_flip_rate`, `state_402_VR_q26_N780`, `control_htf`
  (renamed `sigma460`/`ER150`/`flip_rate`/`VR_q26_N780`/`HTF_agree` internally).
- **N discrepancy vs spec's illustrative estimate (FACT)**: the spec's features/cv_design text
  guesses "~230 weeks" / "roughly 230-60=~170 OOF weeks". `target_series.csv` has 230 rows, but
  `control_htf` is NaN for the first 9 weeks (202201-202209, trailing-50-session SMA warm-up)
  and `joint_loss_next` is NaN for the last row (202622, no realized next week). After dropping
  these 10 rows the usable modeling population is **N=220** (week_key 202210-202621,
  2022-03-07 to 2026-05-22). This is reported per the spec's own instruction to "report exact
  N" rather than forced to match the illustrative ~230/~170 figures. Source: `out/meta.json`
  (`N_full_target_series=230`, `N_dropped_missing=10`, `N_usable=220`).
- Base rate on the usable population: 49/220 = 0.2227 (spec's stated program-level base rate
  was 50/230 = 0.217 on the full, undropped population — consistent, not a substantive
  difference).
- **Z-scoring convention (FACT + documented divergence)**: the spec's features section states
  z-scoring must use "EXPANDING statistics only (no full-sample scaling, matching every prior
  JOB1 test in this program)". `smv2y.py`'s own OLS regression (the file the spec's CODE MAP
  points to for "the expanding-rank/z-score machinery") actually used a **static** full-sample
  (post-burn-in) `zsc()` for its regression z-scores — not an expanding one; only its quintile
  bucketing (`expanding_quintile`) was genuinely expanding. This is a real inconsistency in the
  source file. This run follows the SMV2AC spec's own explicit, unambiguous features-section
  text (expanding, no full-sample scaling) rather than replicating smv2y.py's static
  implementation, since a full-sample scaler would inject future-distribution information into
  early-fold training rows — exactly the kind of leak the CV design's embargo is built to
  prevent elsewhere. Implemented as a causal running (Welford) mean/std at each week t using
  only weeks <= t, generalizing smv2y.py's `expanding_quintile` bisect-insort convention (rank ->
  quantile) to a continuous transform (rank -> z-score). Computed once, globally, upfront — not
  refit per outer fold — which is leakage-safe for every fold because at any week t only weeks
  <= t are used regardless of which fold t later falls into.

## 2. CV splitter — built and verified BEFORE any model fitting (FACT)

Full detail: `out/cv_splitter.csv`, `out/cv_splitter_log.txt`. Design: outer walk-forward
expanding window, 6 folds, 60-week minimum initial training window (the spec's stated lower
bound, used exactly to maximize OOF sample size — INFERENCE: a deliberate design choice, not
forced by the spec), 1-week embargo immediately before each fold's test start.

| fold | train weeks | train n | embargo week | test weeks | test n |
|---|---|---|---|---|---|
| 1 | 202210-202317 (2022-03-07 -> 2023-04-28) | 60 | 202318 | 202319-202344 (2023-05-08 -> 2023-11-03) | 26 |
| 2 | 202210-202344 (-> 2023-11-03) | 87 | 202345 | 202346-202419 (2023-11-13 -> 2024-05-10) | 26 |
| 3 | 202210-202419 (-> 2024-05-10) | 114 | 202420 | 202421-202446 (2024-05-20 -> 2024-11-15) | 26 |
| 4 | 202210-202446 (-> 2024-11-15) | 141 | 202447 | 202448-202521 (2024-11-25 -> 2025-05-23) | 26 |
| 5 | 202210-202521 (-> 2025-05-23) | 168 | 202522 | 202523-202547 (2025-06-02 -> 2025-11-21) | 25 |
| 6 | 202210-202547 (-> 2025-11-21) | 194 | 202548 | 202549-202621 (2025-12-01 -> 2026-05-22) | 25 |

Verified programmatically (asserted in `smv2ac.py`, logged in `out/cv_splitter_log.txt`):
- **Embargo enforced**: every fold's gap between its last training week and its first test week
  is exactly 2 weeks (1 embargo week sits between), for all 6 folds — `embargo_gap_weeks=1` in
  `out/cv_splitter.csv` for every row.
- **Chronological, non-overlapping test folds**: the concatenation of all 6 folds' test indices
  is strictly increasing with no duplicates.
- **Full coverage, no silent gaps**: train union embargo union test indices across all 6 folds
  exactly tile the full N=220 index range with no double-counting.
- **Total OOF weeks = 154** (`out/meta.json: total_oof_n`), fold sizes [26,26,26,26,25,25]. This
  is lower than the spec's illustrative "~170" because the real usable population is N=220, not
  230 (see section 1) — documented as FACT, not adjusted to hit the illustrative number.
- **Inner CV containment**: `out/inner_cv_containment_check.csv` records every one of the 6
  outer folds' 3 inner `TimeSeriesSplit` train/val week ranges; each was asserted
  programmatically to be a subset of that outer fold's own training indices (never touching
  embargo or test indices of that fold, and never touching any other fold).

## 3. Model fit (413) (FACT)

L2-logistic (`sklearn.LogisticRegression`, `penalty='l2'`, `class_weight=None`,
`solver='lbfgs'`, `random_state=20260808`), C selected per outer fold from
{0.01, 0.1, 1.0, 10.0} by lowest mean inner (3-fold chronological `TimeSeriesSplit`) log-loss,
refit on the full outer training window, evaluated once on that fold's test window. Full detail:
`out/fold_coefficients.csv`.

- **Selected C**: every one of the 6 outer folds (full model) and 5 of 6 folds (baseline)
  selected **C=0.01**, the smallest (most-regularized) value on the grid; baseline fold 1
  selected C=0.1. This means the CV procedure itself is telling us the data cannot support
  fitting non-trivial coefficients without overfitting inner validation folds — a signal
  consistent with the eventual KILL, not an artifact of the grid choice.
- **Coefficients are uniformly small** across all folds and both models (typically
  |coef| < 0.06 on z-scored features), reflecting the aggressive regularization the inner CV
  selected.

### Coefficient stability (honest, not averaged away) — `out/coefficient_stability.csv`

| feature | folds + | folds - | sign-consistent all 6 | folds with abs(coef)<0.05 | verdict |
|---|---|---|---|---|---|
| z_sigma460 | 4 | 2 | **NO** | 6/6 | NOT STABLE |
| z_ER150 | 5 | 1 | **NO** | 6/6 | NOT STABLE |
| z_flip_rate | 0 | 6 | YES | 5/6 | NOT STABLE (near-zero) |
| z_VR_q26_N780 | 5 | 1 | **NO** | 6/6 | NOT STABLE |
| z_HTF_agree | 5 | 1 | **NO** | 4/6 | NOT STABLE |

**Zero of the 5 features is a stable, non-trivial, sign-consistent contributor across all 6
outer folds.** `z_flip_rate` is sign-consistent (negative in all 6 folds) but is near-zero
(|coef|<0.05) in 5 of 6 folds, so it does not clear the "non-trivial" bar either. `z_sigma460`,
`z_ER150`, `z_VR_q26_N780`, and `z_HTF_agree` all flip sign at least once across the 6 folds
AND are near-zero in every fold. (The 0.05 near-zero threshold is a descriptive convention
chosen for this report, not a spec-mandated number — INFERENCE — but the qualitative picture
(uniformly tiny, frequently sign-flipping coefficients) does not depend on where exactly that
line is drawn.)

### Seed-stability check — `out/meta.json`, `out/diagnostics.csv`

Refit with 3 additional seeds {1,2,3} against the primary seed 20260808: **AUC is bit-identical
across all 4 seeds** (0.453061224489796 in every case; variance = 0.0, range = 0.0). This is
the **correct, expected** result, not a null check that silently passed: `solver='lbfgs'` (the
sklearn default for `penalty='l2'`) does not consume `random_state` for anything — no data
shuffling, no stochastic optimizer step — per sklearn's own documentation, `random_state` only
affects the `'sag'`, `'saga'`, and `'liblinear'` solvers. Documented as FACT so it is not
mistaken for an unexplored source of variance.

## 4. OOF diagnostics (413, NOT promotion criteria per V4 s32) — `out/diagnostics.csv`

| model | OOF N | OOF AUC | OOF Brier | OOF mean log-loss | OOF base rate |
|---|---|---|---|---|---|
| full5 (5-feature joint) | 154 | 0.4531 | 0.1770 | 0.5402 | 0.2273 |
| baseline_ER150 (1-feature) | 154 | 0.4370 | 0.1773 | 0.5414 | 0.2273 |

Both models' OOF AUC is **below 0.5** (worse than a random ranking on these OOF weeks). The
calibration decile table (`out/calibration_deciles.csv`) shows both models' predicted
probabilities compress into a narrow band (approx 0.17-0.24, tracking the aggressive C=0.01
shrinkage toward the intercept/base-rate) with realized decile rates that do not move
monotonically with predicted probability (e.g. full5 decile 6 predicts 0.220 but realizes
0.125, while decile 7 predicts 0.225 and realizes 0.333) — consistent with a model that has
been regularized down to something close to a constant, on OOF data where it has no real
discriminative signal.

## 5. Secondary correlation check (informational, not a gate)

OOF `P(joint-loss)` from the full model vs. the continuous `downside_next` target on the same
154 OOF weeks (`out/promotion_test.csv`): Pearson r = -0.1490 (p=0.065), Spearman r = -0.0794
(p=0.328). The sign is in the expected direction (higher P(joint-loss) weakly associates with
more negative next-week downside) but neither is significant at conventional levels, and this
was never a gate — reported for context per the spec.

## 6. Promotion test (414, THE gate) — `out/promotion_test.csv`

Paired moving-block bootstrap on the per-week OOF log-loss difference (baseline minus full),
block=4 weeks, B=10000, seed=20260808, reusing `src/analytics/sm_metrics.py:
block_bootstrap_delta` verbatim per the spec's CODE MAP instruction.

- Mean OOF log-loss: baseline_ER150 = 0.54144, full5 = 0.54017.
- Point-estimate delta (baseline minus full) = **+0.001275** (full model marginally lower log-loss
  on average) — but bootstrap 95% CI = [-0.00440, +0.00828], straddling zero.
- **bootstrap_P_improvement_gt_0 = 0.6256**, well short of the **0.85** house bar.
- **PROMOTION_TEST_PASS = False.**
- OOF AUC delta (full minus baseline) = +0.0161 (full model marginally higher pooled AUC, but both
  are below 0.5 — not economically meaningful).
- Fold-level AUC sign-stability (`out/fold_auc_detail.csv`): only **3 of 6** outer folds favor
  the full model (folds 4, 5, 6); folds 1, 2, 3 favor the baseline, and fold 3's gap is large in
  the baseline's favor (delta AUC = -0.286). This is not a stable pattern in either direction.
- Context-only full-sample nested LR diagnostic (NOT the gate — see note below):
  LR stat = 3.775, df=4, chi-squared p-value = 0.437 — not significant, consistent with the
  bootstrap verdict.

**Note on the "likelihood-ratio test" framing (INFERENCE)**: the spec's section 414 prose calls
this a "likelihood-ratio test" but its own "PASS bar" sentence defines the actual gate as the
paired bootstrap on OOF log-loss differences at the 0.85 confidence bar — the same house
convention used throughout this program. A classical chi-squared likelihood-ratio test is not
strictly valid here because the reported OOF predictions are pooled across 6 different per-fold
model fits (not one single MLE fit), so the standard asymptotic distribution does not formally
apply to the pooled OOF quantity. This report therefore computes the classical nested-model
chi-squared LR statistic as a **context-only, informational** number (full-sample refit, both
models, single fit, not CV/OOF), and treats the paired bootstrap on OOF log-loss — exactly as
the spec's "PASS bar" sentence specifies — as the actual, formal promotion gate. Both numbers
point the same direction (no significant improvement), so this interpretive choice is not doing
any work in the final verdict.

## 7. Kill/Keep (per spec's `kill_or_keep` rule)

**KILL.** `bootstrap_P_improvement_gt_0 = 0.6256 < 0.85`. Per the frozen spec: "if the joint
model does NOT beat the ER150-only baseline at the 0.85 bar -> KILL (Level 1 interpretable
modeling adds nothing beyond the single best state already found; V4 s30/33's escalation ladder
STOPS HERE — do not proceed to trees/DL on this target without a new reason)." Every supporting
diagnostic is consistent with this verdict: OOF AUC below 0.5 for both models, no stable
sign-consistent non-trivial coefficient across the 6 outer folds, inner CV collapsing to the
maximum-regularization grid cell in 11/12 fold-by-model fits, and fold-level AUC sign-stability
split 3-3 against the joint model on 3 of the 6 outer test windows.

## 8. Caveats (all INFERENCE/definitional, none change the verdict)

1. Usable modeling population is N=220, not the spec's illustrative ~230; total OOF is 154, not
   the spec's illustrative ~170 (section 1, section 2). This is a population-definition fact,
   not a modeling choice, and the spec explicitly asked for the exact N rather than the
   estimate.
2. The expanding (not full-sample-static) z-scoring convention was chosen to follow the SMV2AC
   spec's own literal features-section text over a real inconsistency found in `smv2y.py`'s
   OLS-regression z-scoring (section 1).
3. The 60-week (spec minimum) initial training window was used to maximize OOF sample size — a
   design choice within the spec's stated bound, not a deviation from it.
4. "Non-trivial coefficient" (|coef|<0.05 => near-zero) is a descriptive threshold chosen for
   this report, not a number the spec specifies; the qualitative finding (uniformly tiny,
   frequently sign-flipping coefficients) is robust to where exactly that line is drawn.
5. The spec's "likelihood-ratio test" language is interpreted as descriptive framing for the
   paired-bootstrap gate its own "PASS bar" sentence defines; a classical chi-squared LR
   statistic is additionally reported as context-only information (section 6).

## Outputs

`out/cv_splitter.csv`, `out/cv_splitter_log.txt`, `out/inner_cv_containment_check.csv`,
`out/oof_predictions.csv`, `out/fold_coefficients.csv`, `out/coefficient_stability.csv`,
`out/calibration_deciles.csv`, `out/diagnostics.csv`, `out/fold_auc_detail.csv`,
`out/promotion_test.csv`, `out/meta.json`, `out/run_log.txt`, this `REPORT.md`.
