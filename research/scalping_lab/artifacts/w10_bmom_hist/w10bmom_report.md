# W10 — B-MOM frozen rule on unseen 2006–2021: REGIME-LOCAL

Spec: `research/scalping_lab/specs/W10_bmom_history.md` (frozen e4e73a8). Rule: W8-1
B-MOM, FROZEN, zero changes — the run imports `w8_bmom.py` and executes its
`build_bands` / `run_rule` / leakage asserts / bootstrap functions verbatim
(code: `research/scalping_lab/src/python/w10_bmom_hist.py`). 14-day slot-of-day
noise band around the 09:30 open (prior days only), RTH-anchored VWAP, LONG
close>max(upper,VWAP), SHORT close<min(lower,VWAP), hold to opposite signal or
15:57 flat, 1 NQ, C1 = 2.872 t/RT, C2 = 4.872 t/RT stress. Seed 20260808,
1000 day-clustered bootstrap reps. Neighbors NOT run. No promotion from this wave.

**Verdict (frozen four-way): REGIME-LOCAL.** No era passes daily-net C1 CI_lo > 0,
and the full pre-2022 CI straddles zero (so neither STRUCTURAL nor CONTRADICTED).
The W8-1 2022–26 result stands alone, in-sample.

## 1. Data and bar basis

- Source: `substrate/minute/NQ/nq1m_2005_202605.parquet` — 6,466,783 1-min
  END-stamped ET bars, 2006-01-05 08:59 .. 2026-05-29 16:59, back-adjusted NQ.
  END-stamping verified (each session's first stamp is 18:01, no 18:00 stamps;
  the RTH opening minute's volume sits on the 09:31 stamp).
- 3-min bars built by aggregation to match W8-1's bar basis exactly: a 3-min bar
  END-stamped T aggregates 1-min END stamps T−2m, T−1m, T (bucket end =
  ceil(t/3 min)); RTH slots aligned 09:33, 09:36, …, 16:00.
- Contamination split at load: readout frame = minute rows **strictly <
  2022-01-01** (4,908,286 rows); reconciliation frame = 2022-01-01 .. DEV_END
  2026-05-31 (1,558,497 rows). Never pooled; no minute row stamped >= 2022-01-01
  enters any readout statistic (asserted in code).

## 2. Reconciliation control (2022-01 → 2026-05) — EXACT match

The aggregated substrate bars were run through the identical frozen pipeline on the
W8-1 window and reconciled against the committed artifacts
(`artifacts/w8_bmom/w8bmom_stats.json`, `w8bmom_w14_trades.csv`).
Full table: `w10bmom_recon_vs_w8.csv`.

| metric | recon run | committed W8-1 | diff |
|---|---|---|---|
| sessions total / excluded / included | 1136 / 14 / 1122 | 1136 / 14 / 1122 | 0 |
| n_trades | 1333 | 1333 | 0 |
| C1 total net ticks | 63,824.624 | 63,824.624 | 0 |
| C1 total net USD | 319,123.12 | 319,123.12 | 0 |
| C1 net/trade ticks | 47.880438 | 47.880438 | 0 |
| C1 PF (trade) | 1.214805 | 1.214805 | 0 |
| C1 mean daily USD | 284.423458 | 284.423458 | 0 |
| C1 daily CI95 USD | [78.35, 500.06] | [78.35, 500.06] | 0 |
| C2 total net ticks | 61,158.624 | 61,158.624 | 0 |

Trade-by-trade: 1333/1333 matched on (entry_time, exit_time, side); w8-only 0,
w10-only 0, max |price diff| on matched = 0.0. Verdict: **PASS** (thresholds
0.5% trade count / 1% net; observed 0.000000 on both). The bar-construction
pathway is therefore validated to the tick; the 2022+ control is used for nothing
else.

## 3. Readout window accounting (2006-01 → 2021-12-31 only)

- 4,106 pre-2022 RTH sessions in the substrate; **15 sessions dropped** because
  their first RTH 3-min stamp is not 09:33 (cannot anchor the 09:30 open under the
  frozen rule; W8-1 asserted this precondition and its data always satisfied it).
  Dropped dates (all listed in `w10bmom_stdout.txt`): 2006-02-08, 2006-03-17,
  2006-05-17, 2006-05-29, 2006-05-30, 2006-07-04, 2006-07-18, 2006-09-04,
  2007-01-31, 2007-03-26, 2007-05-28, 2007-06-18, 2007-07-04, 2012-03-21,
  2013-07-15 — thin-holiday/gap sessions concentrated in 2006–07.
- 11 sessions have a thin 09:33 bucket (<3 minutes; open0930 = first traded minute
  of the bucket, i.e., first traded price after 09:30) — listed in stdout.
- Remaining 4,091 sessions; first 14 excluded for band history
  (2006-01-05..2006-01-24, exactly as in W8-1) → **4,077 included sessions**
  (2006-01-25..2021-12-31).
- Early-close / missing-slot handling as in w8_bmom: 140 sessions end before 16:00;
  136 included sessions force-flat at the last RTH bar stamped <= 15:57
  (`early_closeout_days`); 93 NaN-band decision bars skipped after the exclusion
  window (per-slot band uses that slot's prior observations only; half-days simply
  lack afternoon slots). Same-day-leakage asserts re-run on the readout frame:
  PASSED (300 random recomputations, per-slot NaN-head check, perturbation test).
- 4,994 trades (1.225/day; 2,511 long / 2,483 short; 3,794 closeout / 1,200 flip
  exits; 283 zero-trade days).

## 4. Frozen readout (C1 primary; C2 stress)

Full window and 4-year eras (day-clustered bootstrap, seed 20260808, 1000 reps).
Complete table: `w10bmom_era_stats.csv`; yearly: `w10bmom_yearly.csv`.

| scope (C1) | sessions | trades | net/trade t [CI95] | PF(tr) | mean $/day [CI95] | annSh | pass CI_lo>0 |
|---|---|---|---|---|---|---|---|
| **full pre-2022** | 4,077 | 4,994 | +0.727 [−4.478, +6.117] | 1.013 | +4.45 [−27.44, +36.90] | 0.066 | **NO** |
| 2006-09 | 995 | 1,291 | −1.821 [−6.110, +2.327] | 0.936 | −11.81 [−40.05, +14.84] | −0.422 | NO |
| 2010-13 | 1,025 | 1,265 | −0.762 [−4.522, +2.904] | 0.971 | −4.70 [−28.53, +17.46] | −0.194 | NO |
| 2014-17 | 1,026 | 1,215 | +0.375 [−5.989, +7.230] | 1.009 | +2.22 [−35.40, +41.47] | 0.056 | NO |
| 2018-21 | 1,031 | 1,223 | +5.307 [−13.894, +25.467] | 1.040 | +31.48 [−84.91, +146.99] | 0.256 | NO |

Totals (C1): full pre-2022 +3,631.2 t (+$18,156.16) over 16 years, max DD
$73,737.80, top-5-day share 191.5% (the entire 16-year net is smaller than the
best 5 days); 2018-21 alone is +$32,452.72 with top-5 share 107.1%.

C2 stress (full pre-2022): net/trade −1.273 t [−6.478, +4.117], PF 0.978, mean
−$7.80/day [−39.74, +24.84], total −$31,783.84 — the pre-2022 gross edge does not
survive the stress friction at all.

Yearly (C1): only 2018 (+13.72 t/trade, PF 1.144), 2019 (+7.23 t, PF 1.108) and
2021 (+7.06 t, PF 1.040) are clearly positive; 2020 is −6.87 t/trade despite the
COVID trend year; 2006, 2007, 2010, 2011 are the worst (−4.0 to −4.8 t/trade).

Rolling 2-year (504-session) mean daily net C1 (`w10bmom_rolling2y_daily_mean.csv`):
first window −$29.41 (ending 2008-02-01), min −$91.78, max +$87.69, last window
−$4.49 (ending 2021-12-31). The rolling mean never sustains the 2022–26 level
(committed W8-1: +$284.42/day) anywhere in the 16 pre-2022 years.

## 5. Roll-gap audit (8-sigma days)

Overnight gap = open0930 − prior RTH session close; flag if |z| >= 8 on the
full-window z or a trailing-120-session z (`w10bmom_rollgap_audit.csv`). 9 flagged
days: 2010-05-10, 2015-08-24, 2020-02-24, 2020-03-09, 2020-03-12, 2020-03-13,
2020-03-16, 2020-03-18, 2020-03-24. All correspond to genuine market events
(flash-crash aftermath, the 2015-08-24 open, COVID limit moves). 2020-03-12/13
fall inside the March-2020 quarterly roll week, but their gap sizes and signs match
the actual COVID overnight limit moves, so there is no indication of a
back-adjustment splice artifact. Frozen readout keeps them.
Sensitivity (non-frozen), excluding the 9 days: C1 mean +$14.99/day,
CI95 [−17.63, +46.69] — still fails CI_lo > 0; the verdict does not depend on the
flagged days.

## 6. Frozen interpretation

Precedence as documented in the code: STRUCTURAL → CONTRADICTED → REVIVED-REGIME →
REGIME-LOCAL (→ MIXED if none).

- STRUCTURAL (full pre-2022 daily C1 CI_lo > 0): **fails** (CI_lo = −27.44).
- CONTRADICTED (full CI_hi < 0): **fails** (CI_hi = +36.90).
- REVIVED-REGIME (2018-21 passes, earlier eras fail): **fails** (2018-21 CI_lo =
  −84.91, does not pass).
- REGIME-LOCAL (no era passes): **holds** — all four eras fail CI_lo > 0.

**VERDICT: REGIME-LOCAL.** On the decay-shape question the answer is (c): the
B-MOM edge, as a standalone C1 daily edge, never statistically existed pre-2022.
The era gradient is monotone (net/trade −1.82 → −0.76 → +0.38 → +5.31 t; PF 0.936
→ 0.971 → 1.009 → 1.040) and 2018/2019/2021 are individually positive, so the
2022–26 result (+47.88 t/trade, PF 1.215) looks like the continuation of a
late-emerging regime rather than the revival of an old edge — but nothing pre-2022
clears the frozen bar, and 2020 interrupts the gradient. The W8-1 numbers are
in-sample characterization of a 2018+-flavored, primarily 2022+ regime.

Implication for the owner's gate decision on ρ (0.347 vs 0.3): this wave provides
no independent historical confirmation of B-MOM structure; treat the 2022–26 edge
as regime-local when weighing the correlation-gate exception. No promotion, no
parameter changes, per spec.

## 7. Limitations

- 15 dropped sessions and 11 thin opening buckets (data-quality, 2006–13,
  documented above) — negligible fraction of 4,106 sessions.
- C1 = 2.872 t/RT is the 2025-era friction estimate; 2006-era NQ spreads and
  commissions were materially worse, which would only push pre-2022 nets further
  negative — the REGIME-LOCAL verdict is robust to that direction.
- Back-adjusted volume near quarterly rolls can differ from single-contract volume
  (affects VWAP microscopically); the exact 2022+ reconciliation bounds this
  concern at zero observed trade impact on the overlap.

## Artifacts

All in `research/scalping_lab/artifacts/w10_bmom_hist/`: `w10bmom_stdout.txt`
(full run log), `w10bmom_recon_vs_w8.csv` (reconciliation), `w10bmom_era_stats.csv`
(era CSV, C1+C2), `w10bmom_yearly.csv`, `w10bmom_rolling2y_daily_mean.csv`
(rolling CSV), `w10bmom_rollgap_audit.csv`, `w10bmom_trades.csv`,
`w10bmom_daily.csv`, `w10bmom_stats.json` (machine-readable readout + verdict).
Code: `research/scalping_lab/src/python/w10_bmom_hist.py`. Not committed.
