# W5-C5 — Predictability-ceiling test (Amendment 6 §8)

**MEASUREMENT, not a strategy.** Frozen spec: `specs/W5_programs_wave.md` §C5 (committed
before readout). Code: `src/python/w5_c5_ceiling.py`. Run 2026-08-07, seed 20260808,
1000 session-bootstrap reps. Full stdout: `w5c5_stdout.txt`; all numbers below appear in
`w5c5_metrics.csv`, `w5c5_calibration.csv`, `w5c5_fold_lifts.csv`,
`w5c5_perm_importance.csv`, `w5c5_dataset_summary.csv`.

## Question

Can ANY causal feature set from our own library, under honest chronological validation,
concentrate P(target-first) enough to close the C1 economic gap of the excursion surface
(8.73/9.09 pp for ±24/∓8 long/short; 7.03/7.37 pp for ±32/∓10)?

## Design (frozen-spec interpretation notes)

- **Clock**: every 30th quote-alive RTH second (`dec_idx[::30]`) — the exact census
  excursion-surface clock. Reproduction check: 27,299 clock rows pooled, and per-label
  base P(target) over decided rows = 0.2525 / 0.2361 / 0.2488 / 0.2328 — identical (4 dp)
  to `artifacts/census/excursion_surface.csv` p_target. The gap comparison is therefore
  apples-to-apples.
- **Features**: the 27-column census causal library rebuilt exactly per
  `opportunity_census.py` (ret5/10/30/60/300, rv60/300, tv60, eff60, range300,
  dist_hi/lo, secs_since_hi/lo, trades10/60, vol10/60, upd10/60, sflow10/60, act_accel,
  nsflow60, spread, spread60, tod). Trailing windows only. Rows with t<300 or NaN
  features: **0 dropped** (RTH rows always have ≥15.5 h of prior session history).
- **Labels**: target-first booleans, per-second hi/lo scan starting at **t+1**, cap 600 s,
  conservative same-second-both-crossed → adverse. Neither-hit rows excluded per label:
  35 (0.13%) long_24_8, 119 (0.44%) long_32_10, 47 (0.17%) short_24_8, 175 (0.64%)
  short_32_10.
- **Models**: L2 logistic (StandardScaler fit inside each fold on training rows only,
  C=1.0 fixed — no tuning) and `HistGradientBoostingClassifier(max_depth=3,
  early_stopping=True, max_iter=300)` (its early-stopping holdout is a random 10% of
  TRAINING rows only). **pyGAM not importable in this environment → skipped, per spec.**
- **Validation**: chronological session-grouped expanding 5-fold. 37 sessions sorted by
  date → 5 consecutive blocks (8/8/7/7/7); blocks 2–5 are the 4 validation folds; train =
  all strictly-earlier sessions. No pooled-then-split preprocessing anywhere.
- **Data note**: s20250902 contributes 0 rows (dead quote feed → zero quote-alive RTH
  seconds; identical handling to the census). 36 sessions carry rows; s20250901 and
  s20251128 are holiday-shortened (420/450 rows), s20251117 has a partial outage (689).

## Leakage guard rails (both printed in stdout)

1. **ASSERTION 1 PASSED** — empirical no-overlap test: perturbing `mid_high`/`mid_low`
   at the decision second t by ±1000 ticks left every label unchanged for 800 row-label
   checks (200 rows × 4 labels, session s20260123). Features end at t; labels start t+1.
2. **ASSERTION 2 PASSED** — in all 4 folds the train/validation session sets are
   disjoint AND every training session is strictly earlier than every validation session.

## Results (pooled over 4 validation folds; 22,142–22,190 rows per label)

| label | model | Brier | baseline Brier | skill | base P | top-decile P | LIFT (pp) | lift 95% CI (pp) | C1 gap (pp) | fold lifts (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| long 24/8 | logit | 0.18955 | 0.18751 | −0.011 | 0.2498 | 0.2416 | **−0.83** | [−2.37, +0.97] | 8.73 | +0.53 +0.35 −2.69 −1.59 |
| long 24/8 | hgb | 0.19088 | 0.18751 | −0.018 | 0.2498 | 0.2668 | **+1.69** | [+0.21, +3.21] | 8.73 | +0.36 +1.08 +2.99 +2.40 |
| long 32/10 | logit | 0.18152 | 0.17939 | −0.012 | 0.2342 | 0.2201 | **−1.41** | [−3.21, +0.36] | 7.03 | +0.17 +0.71 −3.24 −3.35 |
| long 32/10 | hgb | 0.18100 | 0.17939 | −0.009 | 0.2342 | 0.2378 | **+0.36** | [−0.77, +1.44] | 7.03 | +1.31 −1.31 +1.15 −0.05 |
| short 24/8 | logit | 0.18923 | 0.18802 | −0.006 | 0.2509 | 0.2662 | **+1.53** | [−0.36, +3.86] | 9.09 | +1.56 +2.27 +1.26 +1.03 |
| short 24/8 | hgb | 0.18853 | 0.18802 | −0.003 | 0.2509 | 0.2751 | **+2.42** | [+0.15, +4.63] | 9.09 | +4.66 −0.04 +2.00 +2.94 |
| short 32/10 | logit | 0.18200 | 0.18052 | −0.008 | 0.2361 | 0.2479 | **+1.17** | [−0.83, +3.13] | 7.37 | +0.59 +1.42 +0.42 +2.31 |
| short 32/10 | hgb | 0.18318 | 0.18052 | −0.015 | 0.2361 | 0.2388 | **+0.27** | [−1.42, +1.97] | 7.37 | −1.49 +1.60 +0.97 +0.11 |

(LIFT = pooled top-decile realized P − pooled validation base P; top decile taken within
each fold at its own 90th-percentile predicted-probability threshold; CI = day-clustered
session bootstrap of the lift, 1000 reps, seed 20260808.)

Key facts:

- **Brier skill is negative for all 8 (label, model) pairs**: every model predicts
  out-of-sample WORSE than a constant at the training base rate. Best skill −0.0027
  (short 24/8 hgb), worst −0.018 (long 24/8 hgb).
- **Calibration is flat** (`w5c5_calibration.csv`): predicted probabilities span
  ~0.12–0.36 across deciles, realized stays pinned at ~0.22–0.27 in every bin, for every
  model — the models manufacture spread that reality does not honor. Logistic top bins
  are systematically overconfident (e.g. short 32/10 logit b9: predicted 0.303 →
  realized 0.263; long 24/8 logit b9: 0.364 → 0.249).
- **Best lift anywhere: +2.42 pp** (short 24/8 hgb), CI [+0.15, +4.63] — a real but tiny
  signal, 6.67 pp SHORT of its 9.09 pp economic gap, and unstable across folds
  (+4.66/−0.04/+2.00/+2.94). Only two combos have lift CIs excluding 0 (long 24/8 hgb
  +1.69, short 24/8 hgb +2.42); both are far below 5 pp.
- **No lift comes within 6.2 pp of its C1 gap** (`lift_minus_gap` column: −9.56 to
  −6.20 pp).
- Permutation importances are dominated by activity/volatility level (trades60, vol60,
  rv, tv60) for logistic and by position-in-session-range (dist_hi, secs_since_hi) plus
  activity for HGB — i.e., the models mostly learn vol regime, which shifts P(both
  barriers) but not direction. Full table in `w5c5_perm_importance.csv`.

## Frozen verdict

Frozen rule (spec §C5): no label/model with top-decile lift ≥ 5 pp (CI excluding 0) →
information set declared insufficient; any ≥ 7 pp stable → conversion spec next wave.

**NO label/model reaches top-decile lift ≥ 5 pp** (best +2.42 pp, CI [+0.15, +4.63]).
The ≥ 7 pp branch is moot.

> **The information set is declared INSUFFICIENT.** Under honest chronological
> validation, the full causal feature library recovers at most ~a quarter of the
> smallest economic gap. The predictability ceiling of this feature set on the 30 s
> decision clock is ~2–2.5 pp of target-first lift — the C1 cost wall is 3–4× higher.
> This is a major input to the Amendment 6 §9 closure decision.

## Caveats

- Ceiling is relative to THIS information set (27 causal features, 30 s clock, 36
  effective sessions) and these two model families (pyGAM absent). A richer library
  (deep book, cross-asset) or event-conditioned clocks are outside this measurement.
- Expanding folds give early folds only 8–16 training sessions; fold-1 estimates are
  noisier. The fold-lift instability of the best combo is reported, not smoothed away.
- Top-decile thresholds are set within each validation fold from validation predictions
  (rank-based selection, not tuning); a deployed rule would need a threshold chosen from
  training data only, which can only lower realized lift.

## Artifacts

- `w5c5_stdout.txt` — full run log (assertions, per-session rows, all metric blocks)
- `w5c5_metrics.csv` — headline per (label, model) row incl. CIs and pass flags
- `w5c5_calibration.csv` — 10-bin predicted-vs-realized per (label, model)
- `w5c5_fold_lifts.csv` — per-fold n/base/top/lift/Brier (stability)
- `w5c5_perm_importance.csv` — all 27 features ranked per (label, model)
- `w5c5_dataset.parquet`, `w5c5_dataset_summary.csv` — the modeling rows and per-session counts
- `w5c5_oof_predictions.parquet` — every out-of-fold prediction (session, t, fold, y, p)
