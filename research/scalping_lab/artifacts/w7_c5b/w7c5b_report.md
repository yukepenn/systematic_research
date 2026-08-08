# W7-1 — C5b augmented predictability ceiling (decisive measurement)

Spec: `research/scalping_lab/specs/W7_rt2_discharge.md` §W7-1 (frozen @ 1d76c14).
Code: `research/scalping_lab/src/python/w7_c5b_ceiling.py`. Seed 20260808, 1000
session-bootstrap reps, day-clustered CIs, discovery substrate only, LOCAL ONLY.
Every number below appears in `w7c5b_stdout.txt` / the CSVs in this directory.

## FROZEN VERDICT

**NO augmented cell reaches top-decile lift >= 5pp with CI_lo > 0 -> the
AUGMENTED information set (census 27 + VWAP + prior-day levels + event flags +
ES signed flow) is ALSO insufficient.** (Input to the Amendment 6 §9 closure
condition via W7: the W7-1 leg of the closure conjunction is satisfied.)

Best augmented cell: short_32_10 / logit, lift **+3.21pp [+0.93, +5.00]**
(CI > 0 but below the 5pp bar; its paired delta vs baseline is +1.74pp
[-1.51, +5.12] — not distinguishable from zero).

## Protocol (C5 EXACT, reused verbatim)

- Same 30s quote-alive RTH decision clock, same 4 target-first labels
  (+24,-8)/(+32,-10) x long/short, cap 600s, conservative
  same-second-both-crossed -> adverse; scan starts t+1.
- Same chronological session-grouped expanding 5 folds built from the same
  37-tag list; same 2 models (L2 logistic w/ StandardScaler fit inside folds;
  HistGradientBoostingClassifier(max_depth=3, early_stopping=True)).
- Leakage guards both PASSED and printed: ASSERTION 1 (800 row-label
  perturbation checks on s20260123 — labels invariant to hi/lo at the decision
  second t); ASSERTION 2 (all 4 folds train/validation disjoint, training
  strictly earlier).

## Baseline-matrix verification (frozen instruction)

Rebuilt pre-drop matrix == committed `artifacts/w5_c5/w5c5_dataset.parquet`:
**rows 27,299**; all 27 features allclose; all 4 labels identical; per-session
rows and neither-counts match `w5c5_dataset_summary.csv`. Per-label base rates
(rebuilt == committed): long_24_8 0.2525, long_32_10 0.2361, short_24_8 0.2488,
short_32_10 0.2328.

## The 13 new features (4 frozen blocks)

1. **VWAP** (grid1s last+vol; grid `last` POINTS -> x4 to ticks): `vwap_dist`
   (mid - RTH-anchored running VWAP from 09:30, ticks), `vwap_slope60` (t/min),
   `vwap_dist_full` (mid - full-session VWAP anchored 18:00).
2. **Prior-day levels** (3-min CSV, back-adjusted; frozen offset rule
   offset_s = CSV 09:30 bar close x4 - sechilo mid_last @ 09:30:00; actual
   level = CSV level - offset_s; per-session offsets in `w7c5b_offsets.csv` —
   they cluster by contract segment (~+3940t Sep-era, ~+2990t Dec-era,
   ~+1990t Mar-era, ~+1150t Jun-era), exactly as back-adjustment predicts;
   documented ~1t Last-vs-mid error: measured median |last*4 - mid_last| =
   1.0t): `pdh_dist`, `pdl_dist`, `pclose_dist` (ticks), `on_gap`
   (CSV-space difference, offset-free), `prior_day_ret_sign`.
3. **Event flags** (c01 calendar, 139 releases < 2026-06-01; NFP/CPI 08:30,
   FOMC 14:00): `min_since_release`, `min_to_release`, clipped: value if <= 120
   min else 999. Verified: on NFP day s20250905 min_since = 60.0 at the 09:30
   open (the spec's RTH clock note). 4 release-day sessions in-sample
   (s20250905 NFP, s20250911 CPI, s20251029 FOMC, s20260211 NFP).
4. **ES signed flow** (raw ES trades bip==0, tick-rule sign, per-second signed
   volume; >5s trade-staleness -> NaN as in W6): `es_sflow10`, `es_sflow60`,
   `es_zsflow60` (= sflow60 / rolling-600s std of 1s signed volume, min 300
   obs — the W6 z-norm house pattern).

HOLDOUT GUARD: 3-min CSV filtered 540,232 -> 519,833 rows (< 2026-06-01)
before any read; calendar filtered 145 -> 139 (provably immaterial: every
session second is > 120 min from any June+ release).

## Same-sample rule (rows dropped from BOTH runs)

27,299 C5-equivalent rows -> dropped 1,435 new-block-NaN rows -> **25,864
modeling rows** (both runs, paired). Per-block NaN (overlapping): vwap = 72
(vwap_slope60 undefined in the first 60s of RTH — the 09:30:00/09:30:30 clock
rows of all 36 sessions), prior_day = 0, event = 0, es_flow = 1,365 (ES >5s
trade-staleness / z-warmup; concentrated in s20250901 Labor-Day half-session
398, s20260303 376, s20260519 truncated-feed afternoon 153, s20260312 121 —
full table in `w7c5b_drops.csv`). The spec's anticipated "first CSV session
has no prior day" drop does NOT arise: the CSV starts 2022-01 and every
modeled session (2025-08-14..2026-05-20) has a prior RTH day and a 09:30 bar
(prior days of s20250902/s20251128 are early-close half-days; their 13:00
close is used as prior RTH close — documented, not dropped). Post-drop
neither-hit exclusions <= 0.24% per label; base rates 0.2526/0.2374/0.2495/
0.2340.

## Results — top-decile lift, baseline vs augmented (pp), paired delta

| label / model | base lift [CI] | aug lift [CI] | delta [CI] | Brier skill base -> aug | pass5 aug |
|---|---|---|---|---|---|
| long_24_8 logit | -0.07 [-1.74,+1.80] | -2.05 [-4.27,-0.55] | -1.97 [-4.94,+0.22] | -0.0138 -> -0.0447 | NO |
| long_24_8 hgb | -1.88 [-3.59,-0.15] | +0.22 [-1.73,+1.99] | +2.10 [+0.45,+3.82] | -0.0127 -> -0.0225 | NO |
| long_32_10 logit | -1.33 [-3.47,+1.31] | -0.90 [-2.77,+0.45] | +0.42 [-2.43,+2.70] | -0.0117 -> -0.0432 | NO |
| long_32_10 hgb | -0.34 [-2.29,+1.88] | +0.74 [-1.44,+3.05] | +1.08 [-0.52,+2.63] | -0.0178 -> -0.0410 | NO |
| short_24_8 logit | +1.46 [-0.37,+3.97] | +2.26 [-0.15,+4.22] | +0.80 [-2.56,+3.51] | -0.0077 -> -0.1443 | NO |
| short_24_8 hgb | +1.41 [-0.35,+3.29] | -0.66 [-2.09,+1.82] | -2.06 [-3.63,-0.15] | -0.0060 -> -0.0134 | NO |
| short_32_10 logit | +1.47 [-0.88,+3.83] | +3.21 [+0.93,+5.00] | +1.74 [-1.51,+5.12] | -0.0079 -> -0.0759 | NO |
| short_32_10 hgb | -0.68 [-2.77,+1.73] | -0.04 [-1.72,+1.82] | +0.64 [-1.83,+2.87] | -0.0127 -> -0.0335 | NO |

Reading: the two deltas whose CIs exclude 0 point in OPPOSITE directions
(long_24_8 hgb +2.10pp; short_24_8 hgb -2.06pp) — augmentation reshuffles
noise across cells rather than adding information. Every augmented Brier skill
is NEGATIVE and every one is worse than its baseline (worst: short_24_8 logit
-0.0077 -> -0.1443): the added level/flow features degrade calibration —
extra capacity without extra signal.

## Permutation importance of the new blocks (augmented run)

Full table `w7c5b_perm_importance.csv`; block means in stdout. Pattern: in the
LOGIT the prior-day/VWAP level features take large importances (e.g. pdl_dist
225.8e-4 in short_24_8) — but that model's lift did NOT clear the bar and its
Brier collapsed, i.e. the linear model leans hard on levels and mis-calibrates.
In the HGB (the better-regularized model) every new-block mean importance is
<= 0.4e-4 and mostly negative — the trees find essentially nothing in VWAP,
prior-day, event, or ES-flow blocks beyond the census 27. es_sflow60's best
showing is rank 7/40 at 0.23e-4 (long_24_8 hgb) — negligible.

## Reproduction diagnostic (baseline vs original C5, W6 tolerances)

7/8 cells within tolerance (|dlift| <= 2pp, |dskill| <= 0.02, no pass_5pp
flip). ONE cell outside: long_24_8 / hgb, lift C5 +1.69pp -> base -1.88pp
(d -3.57pp) — the 1,435-row sample change (5.3%, concentrated in specific
sessions) moves this one HGB cell's fold-boundary behavior; flagged per
protocol. The decisive W7-1 readout is UNAFFECTED: baseline and augmented are
paired on identical rows, and no cell in EITHER run approaches the 5pp bar.
Full table `w7c5b_repro_comparison.csv`.

## Caveats

- ~1t systematic error on all prior-day converted levels (CSV Last vs sechilo
  mid), documented above; immaterial at the 5pp/24t scale of the readout.
- s20250901 retains only 22 modeling rows after ES-staleness drops (holiday
  half-session); it contributes almost nothing to fold 1 training.
- The event block has only 4 release days in-sample; W7-1 measures its
  incremental predictive value at this sample size (near-zero HGB importance),
  not the event mechanism itself — that is W7-3's job.
- Ceiling caveats inherited from C5/W6 apply: library/clock-relative — this
  bounds THESE 40 features on THIS 30s clock, not all possible information.

## Artifacts

w7c5b_stdout.txt (full log), w7c5b_dataset.parquet (25,864 x 27+13+labels),
w7c5b_dataset_summary.csv, w7c5b_drops.csv, w7c5b_offsets.csv (per-session
offset audit), w7c5b_metrics.csv (16 run/label/model rows),
w7c5b_delta.csv (8 paired deltas), w7c5b_fold_lifts.csv, w7c5b_calibration.csv,
w7c5b_perm_importance.csv (640 rows), w7c5b_repro_comparison.csv,
w7c5b_oof_predictions.parquet.
