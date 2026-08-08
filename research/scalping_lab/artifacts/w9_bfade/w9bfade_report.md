# W9-3 — B-FADE pre-2022 CONFIRMATION (run 2026-08-07)

**VERDICT: UNCONFIRMED-POSSIBLY-RECENT** (parked, NOT closed — per the amended
four-way rule). No promotion; no candidate freeze.

Spec: `research/scalping_lab/specs/W9_nq_minute_resolutions.md` §W9-3 **including
the 2026-08-08 decay AMENDMENT** (four-way verdict replaces the binary rule; both
frozen before any readout). Rule identical to W8-2 (`specs/W8_programs_final.md`
§W8-2, construction mirrors `src/python/w8_bfade.py`). Code:
`research/scalping_lab/src/python/w9_bfade_confirm.py`. All numbers below appear in
`w9bfade_stdout.txt` and the CSVs in this directory.

## Setup facts

- Data: `substrate/minute/NQ/nq1m_2005_202605.parquet`, rows stamped
  `>= 2022-01-01` **dropped at load** (1,558,497 rows unread); kept range
  2006-01-05 08:59 → 2021-12-31 17:00 ET (4,908,286 rows). The amendment's nominal
  "2005-2021" window is realized as **2006-2021** — the export contains no 2005
  bars (data fact, not a choice). 2022+ appears ONLY via committed w8 artifacts.
- Calendar: `data/hist_calendar_2005_2021.csv` (BLS primary-source, all 08:30 ET);
  408 rows, of which 24 are 2005 (find no bars, dropped). 2006-2021: **384 release
  days** (192 NFP, 192 CPI, 0 same-day overlaps).
- Stamp convention (verified empirically in-run on 2006-02-03, 2013-07-05,
  2021-11-05): bars are END-stamped; the release-reaction volume spike sits in the
  **08:31**-stamped bar and the RTH-open volume spike in the **09:31**-stamped bar;
  close(09:30-stamp) ≈ open(09:31-stamp). Therefore: pre-release close =
  **08:29-stamped close** (last close strictly before 08:30, guard ≥ 08:00; the
  1-min analogue of the 3-min 08:27 stamp) and entry = **09:30-stamped close**
  (= price at the 09:30:00 RTH open, the same price point as W8-2's 3-min entry).
- Fade rule: at the 09:30-stamped close enter AGAINST sign(09:30c − 08:29c);
  exits at the last stamps ≤ +15/+30/+60 min; C1 = 2.872 t/RT; NQ tick 0.25 pt
  ($5, context). Placebo = same rule on all non-release weekdays (n=3,625; the
  pre-2022 calendar has no FOMC rows, so FOMC days sit inside the placebo —
  harmless for an 08:29→10:30 trade; disclosed difference vs W8-2's carve-out).
- Stats: seed 20260808, 1,000 bootstrap reps, day-clustered CIs (1 trade/day).

## Sample accounting

**371 of 384** release days traded (task expectation "~380"; the gap is 13
itemized days, `w9bfade_excluded.csv`): 2 full exchange holidays (Good-Friday CPI
2017-04-14, 2020-04-10), 5 Good-Friday NFP shortened sessions with no 09:30 bar
(2007/2010/2012/2015/2021-04-02 area), 2 early-2006 mornings with no pre-08:30 bar
(2006-03-10, 2006-05-17), and 4 rule-mandated zero-reaction no-trades
(2011-01-07, 2012-04-13, 2015-09-16, 2019-02-13).

## Primary results (all traded release days; roll-gap exclusions = 0)

| scope | h | n | net C1 (t) | 95% CI | gross (t) | win% |
|---|---|---|---|---|---|---|
| **full 2006-2021, release** | **15** | **371** | **+1.683** | **[−6.433, +9.644]** | +4.555 | 52.6 |
| full 2006-2021, release | 30 | 371 | +5.964 | [−6.527, +19.616] | +8.836 | 49.1 |
| full 2006-2021, release | 60 | 371 | +9.220 | [−6.539, +26.569] | +12.092 | 49.9 |
| full 2006-2021, placebo | 15 | 3625 | −1.230 | [−3.754, +1.176] | +1.642 | 48.8 |
| sub 2015-2021, release | 15 | 162 | −1.483 | [−18.669, +17.036] | +1.389 | 45.7 |
| sub 2006-2014, release | 15 | 209 | +4.138 | [+0.319, +8.100] | +7.010 | 57.9 |

## Verdict (frozen four-way rule, PRIMARY = 15-min exit)

- CONFIRMED requires full-window net > 0 with CI_lo > 0 AND 2015-2021 point > 0:
  **FAIL** (CI_lo = −6.433 < 0; 2015-2021 point = −1.483 ≤ 0).
- PARTIALLY-SUPPORTED requires 2015-2021 CI_lo > 0: **FAIL** (−18.669).
- REFUTED requires full-window CI_hi < 0: **NO** (+9.644).
- → **UNCONFIRMED-POSSIBLY-RECENT**: pre-2022 is flat (not significantly
  negative). Per spec: **parked, not closed** — the effect may be a post-2020/2022
  regime product; resolution only via forward data or a Tier-3 holdout with a
  frozen candidate. Placebo is flat (CI covers 0) — the original binary rule's
  placebo clause would have passed; its main clause would not have.

## Decay/regime texture (context, not verdict)

- By 4-year era, net15 (t): 2006-2009 **+3.55** [−1.59,+8.84] · 2010-2013 **+3.24**
  [−2.67,+8.61] · 2014-2017 **−4.76** [−14.06,+4.08] · 2018-2021 **+4.73**
  [−25.89,+36.53] (era vol explodes post-2018).
- A small genuine early-era fade edge existed: 2006-2014 is positive with CI_lo>0
  at 15 and 30 min (+4.14 [+0.32,+8.10]; +5.95 [+0.30,+11.41]) — then decays
  through 2014-2017. The recent window is dominated by huge two-sided years:
  2019 **−42.5** t/trade @15min (CI_hi < 0) vs 2021 **+47.9** t/trade (and 2021
  CI_lo > 0 at 30/60min). The 2021 profile resembles the 2022+ dev sample —
  consistent with the "possibly-recent" reading, and equally with in-sample
  inflation (W8-2 honesty clause: the fade direction was observed on the dev data).
- NFP vs CPI @15min: NFP +1.73 [−10.68,+14.43] (n=185); CPI +1.63 [−9.65,+12.73]
  (n=186). No event-type separation pre-2022.
- Concentration @15min: total +624.5 t; top-5 winners +1,993.6 t = 319% of total
  net (22.5% of gross wins) — top-5 and bottom-5 dates are ALL 2019-2021. Worst
  trade −422.9 t (2020-10-13 CPI). Max DD −2,591.7 t.
- Rolling 3-year mean of net15 (`w9bfade_rolling_3y.csv`): min −30.70 t
  (2020-07-02), max +7.02 t (2008-09-16), last +4.04 t (2021-12-10); 39.4% of
  rolling observations below zero.

## Roll-gap guard — design record (full disclosure)

- Pass 1 (pooled 16-year sigma of 1-min diffs in TICKS, flag > 8σ = 129.8 t) was
  computed first and **rejected as a roll detector**: with a ~5x price-level rise
  it is a recency-biased volatility filter — it excluded 100 trades at 15min
  (27 of 371 release, 73 of 3,625 placebo), all genuine macro minutes
  (2020 COVID, 2018 Volmageddon, 08:31 reaction bursts),
  including 17 of 23 traded 2021 release days, i.e. precisely the reactions under
  test. Kept as **sensitivity B**.
- Corrected detector: candidate 8σ jump = 1-min fractional return > 8× trailing
  90-weekday local σ AND > 8× same-day isolation σ. **55 candidate days**, every
  one at a macro stamp (33× 08:31 release burst, 6× 10:01 data/Fed, 09:30/09:31
  RTH open, ...). Max same-day isolation z in the whole sample = **19.2** (p99.9 =
  14.9); a true back-adjustment splice (permanent one-minute re-basing on an
  otherwise ordinary day) would print z ≫ 20. Structurally, the NT8 back-adjusted
  merge splices at a roll SESSION BOUNDARY (17:00/18:00 ET), which an intra-session
  08:29→10:30 window can never span. **Detected roll-gap jumps spanning a trade
  window: 0. Trades excluded: 0** (count reported per spec; scan in
  `w9bfade_guard_scan.csv`).
- Verdict robustness: the verdict class is IDENTICAL under all three treatments —
  primary (n=371: +1.68 [−6.43,+9.64]), sensitivity A extreme-vol days excluded
  (n=341: −0.35 [−8.69,+8.50]), sensitivity B pass-1 filter (n=344: −3.74
  [−10.28,+2.91]). All: full CI straddles 0, 2015-2021 point ≤ 0 →
  UNCONFIRMED-POSSIBLY-RECENT in every case.

## Reconciliation vs committed W8 artifacts (2022+, IN-SAMPLE — context only, never pooled)

| window | h | n | net C1 (t) | 95% CI |
|---|---|---|---|---|
| w8 2022-2026-05 (IS) | 15 | 102 | +47.255 | [−5.366, +91.983] |
| **w9 2006-2021 (OOS)** | 15 | 371 | +1.683 | [−6.433, +9.644] |
| w8 2022-2026-05 (IS) | 30 | 102 | +42.001 | [−22.783, +107.474] |
| w9 2006-2021 (OOS) | 30 | 371 | +5.964 | [−6.527, +19.616] |
| w8 2022-2026-05 (IS) | 60 | 102 | +98.991 | [+12.155, +183.797] |
| w9 2006-2021 (OOS) | 60 | 371 | +9.220 | [−6.539, +26.569] |

The 16-year out-of-sample effect is ~1/30th of the in-sample 2022+ point estimate
at 15min. Sixteen unseen years decline to confirm the dev-window fade; they also
decline to refute it.

## Artifacts

`w9bfade_stdout.txt` (full run log), `w9bfade_trades.csv` (371 release + 3,625
placebo trades, per-horizon P&L and sensitivity flags), `w9bfade_summary.csv`
(every table above), `w9bfade_rolling_3y.csv`, `w9bfade_excluded.csv`,
`w9bfade_concentration.csv`, `w9bfade_guard_scan.csv`. Code:
`src/python/w9_bfade_confirm.py`. No git commit from this run (per task).
