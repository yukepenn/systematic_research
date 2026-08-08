# Red Team Notes — SMV2AC_ML_LEVEL1 (seq 413–414)

Verdict: **CONFIRMED**

Spec: `runs/SMV2AC_ML_LEVEL1/spec.yaml`. Script: `runs/SMV2AC_ML_LEVEL1/smv2ac.py`.
Report: `runs/SMV2AC_ML_LEVEL1/REPORT.md`. All checks below were performed with fresh,
independently-written code (not by re-running or importing `smv2ac.py`'s own functions),
reading only the frozen `out/` artifacts and the upstream source files the script itself reads.

## 1. Spec letter-exactness — PASS

- 5 features exactly as spec'd: sigma460, ER150, flip_rate, VR_q26_N780, HTF_agree. No new
  feature engineering (verified by reading `smv2ac.py` section A: features are renamed columns
  pulled directly from `target_series.csv`, only transform applied is the spec-mandated
  z-scoring).
- Outer CV: walk-forward expanding window, 6 folds, 60-week minimum initial training window
  (spec's stated lower bound — a legitimate in-bound design choice to maximize OOF N, correctly
  flagged as INFERENCE in REPORT.md §2), 1-week embargo — matches spec exactly.
- Inner CV: 3-fold chronological `TimeSeriesSplit`, C grid `{0.01, 0.1, 1.0, 10.0}` — matches
  spec exactly (verified in code and reproduced numerically, §3 below).
- `random_state=20260808` used in every `LogisticRegression` call (4 call sites checked via
  grep: inner-grid fits, final per-fold fit, both context-only full-sample fits). Alt seeds
  {1,2,3} used only for the seed-stability check, as spec'd.
- PASS bar for the promotion gate: code has `PASS_BAR = 0.85`, matching spec's
  "P(improvement>0)>=0.85" verbatim. Gate not relaxed or moved.
- `class_weight=None` in all 4 `LogisticRegression` instantiations — spec's explicit
  "do NOT rebalance" instruction honored (grep-verified, no contradicting call anywhere in the
  file).

## 2. CV/embargo splitter — independently reconstructed, LEAKAGE-FREE — PASS

Wrote a fresh fold-builder (not copy-pasted from `smv2ac.py`) from the spec's own text (60wk
min train, 6 folds, 1wk embargo, tiling the sample) and cross-checked every one of the 6 folds'
train/embargo/test week ranges against `out/cv_splitter.csv`: **exact match on all fields**
(train_start/end week, train_n, embargo_week_key, test_start/end week, test_n) for all 6 folds.
Independently confirmed:
- Every fold's train→embargo→test transition is contiguous with exactly 1 embargo week between
  train-end and test-start (gap=1 for all 6 folds) — no training row within the embargo window
  of that fold's own test rows.
- The 6 test windows are chronologically ordered, non-overlapping, and (together with the 60
  initial-train-only weeks and 6 single-week embargo gaps) tile the full N=220 sample with no
  gaps or double-counts. Total OOF = 154, matching `meta.json`.
- `out/inner_cv_containment_check.csv`'s 18 inner train/val week ranges (3 per outer fold × 6
  folds) were independently checked against `out/cv_splitter.csv`'s outer train windows: every
  inner train/val range lies strictly inside its own outer fold's `[train_start_week,
  train_end_week]`, and every inner val range ends strictly before that fold's own embargo/test
  start. Inner CV never touches an outer test week, in any fold. (18/18 checked, 0 violations.)

This is the highest-leakage-risk part of the run and it holds up under independent
reconstruction: no shortcuts, no off-by-one, no fold reabsorbing another fold's test window.

## 3. Independent recomputation of load-bearing numbers — PASS (bit-exact / exact)

- **OOF AUC** (recomputed from `out/oof_predictions.csv` via `sklearn.roc_auc_score`):
  full5 = 0.4530612244897959, baseline_ER150 = 0.4369747899159664 — bit-identical to
  `out/diagnostics.csv` and `out/promotion_test.csv`. Also recomputed Brier and mean log-loss:
  identical to the file (max abs diff between stored `logloss` column and a fresh
  −(y·ln p+(1−y)·ln(1−p)) computation: 4.4e-16, i.e. floating-point noise).
- **Paired moving-block bootstrap** (`sm_metrics.block_bootstrap_delta`, same inputs,
  block=4, B=10000, seed=20260808, called fresh on the OOF log-loss vectors pulled straight
  from `oof_predictions.csv`): delta=0.0012753606576507703, ci=[-0.00440, +0.00828],
  P(improvement>0)=**0.6255999999999999** — bit-identical to `out/promotion_test.csv`'s
  `bootstrap_P_improvement_gt_0`. Confirms PROMOTION_TEST_PASS=False (0.626 < 0.85 bar).
- **Fold coefficients**, refit from scratch twice (fold 1 and fold 3, using an independently
  rebuilt `D` frame, independently rebuilt expanding z-score, independent
  `TimeSeriesSplit`/grid-search loop): both folds' `best_C`, coefficient vectors, and intercepts
  reproduce **bit-exactly** against `out/fold_coefficients.csv`. Fold 3 was chosen deliberately
  because it carries the largest baseline-favoring AUC gap (Δ=−0.286); its independently-refit
  test AUC (full=0.4571428571428572, baseline=0.7428571428571429) also bit-matches
  `out/fold_auc_detail.csv`.
- **Base-rate / N accounting**: independently reloaded `target_series.csv` (230 rows), confirmed
  `control_htf` is NaN for exactly weeks 202201–202209 (9 rows) and `joint_loss_next` is NaN for
  exactly week 202622 (1 row, no overlap with the 9), giving N_usable=220. Of the 50 total
  positives in the raw 230-row file, exactly 1 falls in the 9 dropped early weeks, leaving
  49/220=0.222727... — bit-matches `meta.json`'s `base_rate_joint_loss_next`. The spec's own
  illustrative "50/230=21.7%" is separately confirmed accurate on the raw pre-drop population.

## 4. Expanding (not full-sample) z-scoring — PASS

Independently implemented the expanding Welford z-score and compared it row-by-row against a
static full-sample z-score computed on the same raw series. The two diverge substantially in
early rows (e.g. row 0: expanding z=0.000 vs static z=+0.744; max abs diff across the series =
2.26) and converge toward each other only near the end of the sample, as expected for a
causal expanding statistic approaching the full-sample statistic as the window grows. This
confirms the implementation is genuinely causal/expanding, not a mislabeled full-sample
scaler. Separately, read `runs/SMV2Y_JOINTLOSS_VIABILITY/smv2y.py` lines 223–225 and confirmed
the caveat's factual claim about that file: its `zsc()` helper is `(x−nanmean(x))/nanstd(x)`
computed once over the whole post-burn-in `samp` array — a genuine static full-sample
z-score, used in its OLS regression (lines 256, 261) — while only its `expanding_quintile`
(lines 183–195) is truly expanding. The report's characterization of this as a real
inconsistency in `smv2y.py`, and its choice to follow the SMV2AC spec's own literal
"EXPANDING statistics only" text instead, is accurate and correctly documented as a FACT/
divergence rather than silently conforming to the other file's (leakier) convention.

## 5. class_weight not rebalanced — PASS

Confirmed via grep: all 4 `LogisticRegression(...)` call sites in `smv2ac.py` pass
`class_weight=None` explicitly. No `class_weight='balanced'` or equivalent anywhere in the
file. Matches spec's explicit instruction that the 21.7% base rate is the real economic base
rate and must not be rebalanced.

## 6. Language / honesty — PASS

- Coefficient stability table in REPORT.md §3 (0/5 features stable-and-non-trivial across all 6
  folds; z_flip_rate sign-consistent but near-zero in 5/6 folds) reproduces exactly against
  `out/coefficient_stability.csv` — sign flips are reported per-feature with explicit
  folds-positive/folds-negative counts, not averaged into a single misleading full-sample
  coefficient. This is genuine honest reporting, not spin.
- Kill verdict is correctly derived from the frozen spec's own rule
  (P(improvement>0)=0.626 < 0.85 → KILL) and is not contradicted anywhere else in the report;
  no case of a KILL result being reframed as a soft "inconclusive."
- FACT vs INFERENCE labeling is used consistently and appropriately: the N=220-vs-~230
  discrepancy, the 60-week window choice, the 0.05 near-zero threshold, and the
  "likelihood-ratio test" reframing are all correctly labeled INFERENCE/definitional rather
  than being silently presented as spec requirements.
- No BLOCKED items are claimed; both seq 413 and 414 completed cleanly, consistent with the
  actual artifact set (all `out/` files listed in the exec report exist and are populated).
- The context-only chi-squared LR diagnostic (§6) is correctly caveated as not formally valid
  on pooled multi-fold OOF predictions, and is clearly kept separate from the actual bootstrap
  gate; both point the same direction, so this framing choice does not affect the verdict —
  verified true by recomputing both: bootstrap P(improve>0)=0.626, LR p=0.437, both
  non-significant.

## Overall

Every checked claim — CV/embargo construction, inner-CV containment, OOF AUC/Brier/log-loss,
the paired bootstrap promotion statistic, two independently-refit folds' coefficients, the
expanding-vs-static z-scoring distinction, the N/base-rate accounting, and the class_weight
setting — reproduces exactly (bit-exact for all numeric recomputations) from the frozen `out/`
artifacts and the upstream source files. No leakage found in the CV design. No moved gates. No
overclaiming. **CONFIRMED.**
