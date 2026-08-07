# C01 T1-ML — Tier-1 ML Overlay Arms (runs/C01T1_ML)

_Executed 2026-08-07 against the frozen `runs/C01T1_ML/spec.yaml` (committed before execution).
Counts as trials: 3 (seq 288–290, one per arm; registry rows left to the wave orchestrator per
the T0-2 concurrent-write precedent). All estimates are in-sample-era outer-fold estimates; no
OOS claim. Harness script archived in the session scratchpad as `c01_t1ml_harness.py`; every
implementation decision was declared in its preregistration header before any arm read._

**VERDICT: REJECT — all three pass conditions fail. The honest branch fires: the no-ML vol
control dominates the ML sizing arm, so the ML overlay closes. But vol targeting itself does NOT
beat the take-all baseline consistently and cuts the right tail to 49% — nothing is promoted.
Champion unchanged.**

## 1. Engine validation (required first — rerun, penny-exact, before any arm read)

T0-2's counterfactual engine was rebuilt from the 13 raw member ledgers
`runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__*.csv`. 0%-filter reproduces every member's ledger signed
cash flow **to the penny (max |diff| = $0.000000, all 13 members)** and engine trades = fills/2 =
header execs/2 for all 13 (full table: `c01_t1ml_engine_validation.csv`). Fixed session index:
1,183 sessions, 2022-01-03 → 2026-07-31, frozen across all arms.

Population: T0-6 cache (34,147 of 34,148 engine trades; the 1 unmatched vm14 trade, net
+$525.64, is identified and excluded — 99.997% match, matching T0-6's validated rate). Outer
folds rebuilt with T0-6's exact code (test sizes 6,850/6,851/6,800/6,857/6,789; purge 0 —
structurally vacuous as asserted; embargo 69/35/57/67/0). Complete-case rule dropped 14 trades
(NaN prev_os/eff120; net −$11,146.04) uniformly from all arms and the baseline → 34,133 trades.
Baseline net $198,875.78 reconciles exactly with T0-2's $198,058.82 (− vm14 $525.64/13
+ dropped $11,146.04/13).

## 2. Nested purged CV (5 frozen features only, nothing chosen on outer test)

Per outer fold: inner 4-fold day-grouped chronological CV (2-day embargo) chose C by weighted
inner-OOF log-loss (**C = 0.1 in all 5 folds**), isotonic calibration fit on pooled inner-OOF,
ARM_A threshold by inner-OOF logG over grid {0.40…0.60 step .02} (**hit the 0.40 grid floor in
all 5 folds** — the optimizer wanted lower; caveat noted).

| fold | C | thr_A | OOS AUC (w) | Brier (w) | ECE (w) | mean p | base rate | keep_A | mean size_B | mean size_C |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.1 | 0.40 | 0.5749 | 0.2166 | 0.0145 | 0.335 | 0.326 | 3.5% | 0.000 | 0.824 |
| 1 | 0.1 | 0.40 | 0.5734 | 0.2206 | 0.0095 | 0.338 | 0.338 | 30.1% | 0.000 | 1.375 |
| 2 | 0.1 | 0.40 | 0.5628 | 0.2225 | 0.0089 | 0.338 | 0.339 | 26.1% | 0.009 | 1.320 |
| 3 | 0.1 | 0.40 | 0.5559 | 0.2203 | 0.0164 | 0.338 | 0.332 | 4.6% | 0.010 | 0.864 |
| 4 | 0.1 | 0.40 | 0.5650 | 0.2224 | 0.0184 | 0.328 | 0.341 | 10.9% | 0.001 | 0.649 |

Real but tiny OOS signal (AUC 0.556–0.575), well calibrated (mean p ≈ base rate every fold,
ECE 0.9–1.8%). Coefficient stability across folds (standardized final refits,
`c01_t1ml_coefficients.csv`): consensus +5/5 (≈+0.17, the only strong continuous feature),
prev_os −5/5, volvol +5/5, eff120 4/5 (≈0, sign-flips), sessbkt dummies 4–5/5 (late-day +0.29
to +0.34, overnight −0.17 to −0.21 — the T0-6 session pattern reproduced).

## 3. Arm results (pooled 1/N outer-test book on the full 1,183-session index)

| arm | net $ | logG ($100k) | Sharpe | maxDD $ | MAR | top-1% P&L kept | top-1% trades kept |
|---|---|---|---|---|---|---|---|
| BASELINE (take-all) | 198,875.78 | 1.6284 | 1.069 | −39,853.39 | 1.091 | 100% | 100% |
| ARM_A (binary) | 35,833.99 | 0.3157 | 0.560 | −13,695.35 | 0.572 | 10.4% | 11.7% |
| ARM_B (sizing map) | −851.78 | −0.0087 | −0.231 | −1,794.01 | −0.104 | 0.25% | 3.8% |
| ARM_C (vol control) | 141,441.57 | 1.2017 | 0.992 | −22,837.99 | 1.355 | 49.4% | 100% |

Paired circular day-block bootstrap (block=5, 10,000 draws, seed 20260807), one-sided
P(mean diff ≤ 0): **ARM_B − ARM_C p = 0.9925** (C beats B, p≈0.0075 the other way);
ARM_B − BASELINE p = 0.9963; ARM_C − BASELINE p = 0.9262; ARM_A − ARM_B p = 0.0839.

Both-halves signs, arm − baseline (primary = wave-standard split 2022-07→2024-06 / 2024-07→2026-06;
chronological split gives identical sign patterns):

| arm | logG H1/H2 | MAR H1/H2 |
|---|---|---|
| ARM_A | − / − (−0.315, −0.777) | − / − (−1.335, −0.877) |
| ARM_B | − / − (−0.390, −0.903) | − / − (−1.664, −1.734) |
| ARM_C | + / − (+0.133, −0.472) | + / − (+0.499, −0.291) |

## 4. Spec gate, applied verbatim

1. ARM_B beats ARM_C paired p<0.05 — **FAIL** (p = 0.9925; ARM_C is significantly better).
2. ARM_B beats take-all on logG or MAR with same sign both halves — **FAIL** (−/− on both).
3. ARM_B top-1% right-tail retention ≥ 90% — **FAIL** (0.25%).

**REJECT.** Spec branch "if ARM_C ≈ ARM_B: vol targeting suffices, ML overlay closes honestly"
applies a fortiori — the no-ML vol control strictly dominates the ML sizing arm, so the ML
overlay family closes. Honest completion of that branch: ARM_C itself is **not** a pass — it
costs 29% of net and logG (1.20 vs 1.63), improves MAR only overall (+0.26) with a **negative
H2 half**, and retains just 49.4% of top-1% trade P&L, violating the wave's hard right-tail
constraint for down-weighted states. Vol targeting "suffices" only relative to the ML overlay,
not relative to the take-all baseline. **No promotion. Champion unchanged.**

## 5. ARM_A > ARM_B flag — audit performed (spec-required before believing)

ARM_A (logG 0.32) materially exceeds ARM_B (−0.01). Audit verdict: **not miscalibration** —
per-fold calibration is good (§2). The cause is the frozen ARM_B map itself:
clip((p−0.45)/0.15, 0, 1) has its dead-zone floor at 0.45 while the calibrated-p distribution
sits at median 0.347 (quantiles 1%/25%/75%/99% = 0.247/0.295/0.392/0.475); only **2.30%** of
trades have p > 0.45 (0.01% above 0.50). The map was frozen against an implicit ≈50% win-rate
prior; the book's uniqueness-weighted base rate is 0.335 (unweighted 0.396, winners larger than
losers). ARM_B is therefore a near-empty book by construction — an honest frozen-spec outcome,
reported as such; per the spec, the map may not be adjusted after reads. ARM_A's own failure is
substantive, not cosmetic: at AUC ≈ 0.56 the p>0.40 slice keeps 3–30% of trades and forfeits
90% of the right tail — consistent with T0-2's caveat that feature-conditional, serially
correlated errors degrade far faster than the i.i.d. noisy-oracle bound (which needed only
AUC ≈ 0.525 to break even but assumed noise uncorrelated with trade size and regime).

## 6. What this closes and what it does not

- Closes: FAMILY_A ML overlay (L2-logistic on the 5 fold-stable features) as a sizing/filter
  layer on the 13-member pooled book. The T0-6 monotonicities are real (AUC ≈ 0.56 OOS,
  stable coefficients) but not monetizable through episode suppression/scaling — the edge
  lives in the right tail, and every probability-ranked cut is tail-adverse in practice
  (ARM_A keeps 10% of tail P&L; the i.i.d. bound's tail-neutrality does not transfer).
- Does not close: session-bucket structure as an analysis lens (strongest, most stable
  coefficients); any future ML idea would need a different monetization channel than
  bet/no-bet on member episodes, and a new preregistered spec.
- Not tested here (out of scope by spec): engine-level confirmation of any arm; leverage;
  anything touching the champion.

## Artifacts

- `research/04_complementary_family/c01_t1ml_arm_metrics.csv` — per-arm metrics incl. both
  half-splits and tail retention.
- `research/04_complementary_family/c01_t1ml_fold_diagnostics.csv` — per-fold C, threshold,
  AUC, Brier, ECE, base rates, mean sizes.
- `research/04_complementary_family/c01_t1ml_coefficients.csv` — per-fold standardized
  coefficients of the final refits.
- `research/04_complementary_family/c01_t1ml_engine_validation.csv` — penny-exact 0%-filter
  validation table (13/13).
- Scratchpad: `c01_t1ml_harness.py` (frozen preregistration header + full harness),
  `c01_t1ml_daily.csv` (per-session per-arm pooled P&L), `c01_t1ml_pcal.npy`,
  `c01_t1ml_summary.json`.
