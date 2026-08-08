# SMV2J_STATE_HARNESS — Statistical Red Team notes (V4 §48 mandatory pass)

Date: 2026-08-08. Reviewer: red-team subagent (adversarial verification; nothing modified).
Scope: spec.yaml + smv2j.py + REPORT.md + all out/ artifacts. Verdict: **CONFIRMED** (both KILLs stand).

## 1. Freeze / letter-exactness of gates, grids, seed

- spec.yaml committed in 0a9cf3f at 2026-08-08 12:09:17 -0400; out/ artifacts written 12:19, REPORT.md 12:22.
  Spec frozen BEFORE any result was read. PASS.
- Grid in executor == spec exactly: VR q∈{6,12,26} × N∈{390,780,1950} (9 cells), ER n∈{60,150,460}
  (3 cells). harness_results.csv has exactly 12 rows, no extra cells, no re-grid anywhere in smv2j.py. PASS.
- Seed 20260808, B=10000, block=5, NW maxlags=5, |t|>2 gate, cluster threshold 0.7 — all in code and
  meta.json exactly as spec. PASS.
- Verdict logic: family KEEP requires its best-|t| cell to pass tests 1–4. Selecting the best cell is
  anti-conservative toward KEEP, yet both families still KILL; with 0/12 cells passing the t-gate no
  selection rule could flip the verdict. No post-hoc selection risk. PASS.
- The four disclosed implicit readings (psi* form, boot 0.975, plateau rel-range, FLAT=|t|<1) are all
  gap-fills where the spec was silent, disclosed in REPORT §"Preregistered readings", and none is
  decision-critical (t-gate 0/12 kills both families on its own; plateau fails by >10x with sign flips
  under any sane reading of "vary < 30%"). PASS.

## 2. Independent recomputations (from out/ artifacts + raw upstream files, own code)

All matched, most to machine precision:

| quantity | artifact | recomputed |
|---|---|---|
| n dev sample / range | 880, 2023-01-03..2026-05-28 | 880, same (only 1 post-burn row dropped: 2026-05-29, next-PnL NaN — no silent trimming) |
| n hist sample / range | 3872, 2007-01-05..2021-12-30 | 3872, same |
| t_NW ER_n460 (primary) | -1.7440 | -1.7440 (statsmodels HAC5) and -1.7440 hand-rolled Bartlett NW |
| t_NW VR_q26_N780 | -1.6531 | -1.6531 |
| t_NW ER_n150 / VR_q6_N390 | -1.0600 / +1.1143 | -1.0600 / +1.1143 |
| e10 secondary t VR_q26_N780 | -2.0241 | -2.0241 |
| Q5-Q1 dev ER_n460 / VR_q26_N780 | -387.75 / -218.85 | exact match (incl. Welch t -1.837 / -1.090, bucket counts) |
| Q5-Q1 hist ER_n460 (Welch t) | -67.65 (-1.875) | exact match; also VR_q26_N390, VR_q6_N780 |
| plateau rel-ranges | VR 5.4322/4.3881, ER 3.6013/5.8742 | exact match |
| bootstrap same-sign (frozen seed replicated) | ER_n460 0.9705, VR_q26_N780 0.9498 | 0.9705 / 0.9498 exact — draws reproduce under default_rng(20260808) |
| expanding quintiles (own bisect impl) | Q_ER_n460, Q_VR_q26_N780 | 0 mismatches over all 881 non-NaN rows |
| cross-corr best VR vs best ER | 0.1794 | 0.1794; max \|corr,sigma460\| 0.0660, max \|corr,htf\| 0.0910 (report's ≤0.14 is conservative) |
| t-gate | 0/12, max\|t\|=1.744 | confirmed |
| test1 passes | 7/12 (VR 4, ER 3) | confirmed |
| test4 reversals | 0 | confirmed (3 opposite-sign cells all hist \|t\|<1: -0.354, -0.996, +0.632 — kill insensitive to the FLAT threshold up to \|t\|≥2, as claimed) |

## 3. Leakage / lookahead scan — CLEAN

- **Truncated-substrate test (strongest check):** recomputed ER_n460 and VR_q26_N780 (psi* and raw VR)
  from the raw parquet using ONLY bars ≤ session t's last bar, at 4 dev dates (2023-03-15, 2024-06-14,
  2025-09-10, 2026-05-28) and 2 hist dates (2010-06-15, 2015-10-01). All 12 values match states_dev/
  states_hist to ~1e-9 rtol. No future bar enters any state.
- next_pnl_dual[t] == pnl_dual[t+1] for every row; pnl_dual matches as-published SMV2H file bit-for-bit.
  Outcome files not re-simulated. PASS.
- htf control: recomputed sign(close_t − SMA50 of session closes incl. t); matches all 1090 non-NaN rows;
  this is the value the deployed strategy uses during session t+1 (shift(1)) — control at t, outcome t+1,
  no same-session outcome use. PASS.
- z-scores are full-sample affine transforms with intercept present → t-stats invariant; all bucketed
  quantities use expanding inclusive ranks with 12-mo burn-in (dev 2022-01-03→2023-01-03,
  hist 2006-01-05→2007-01-05, both verified). No full-sample scaling in any ranked quantity. PASS.
- Data bounds: dev substrate hard-filtered to sess_date ≤ 2026-05-31 BEFORE any computation (raw file has
  540,232 bars through 2026+; post-filter 519,714 == meta; max sess 2026-05-29). Primary outcome ends
  2026-05-29. Hist ends 2021-12-31. Nothing ≥ 2026-06-01 anywhere, well clear of the 2026-08-01 lock. PASS.
- Dev is_last_of_sess vs last-bar-per-sess_date: verified identical (1139 == 1139, same index sets),
  so REPORT's coincidence claim is TRUE (even though the assert is not in the committed smv2j.py — see
  minor issue M2).

## 4. Report language

- FACT / INFERENCE / HYPOTHESIS labeling used correctly; both kills recorded honestly with the best
  (adverse-to-kill) numbers shown; secondary-outcome near-miss (e10 t=-2.02) disclosed rather than buried;
  the residual negative pattern is explicitly HYPOTHESIS with "no re-grid authorized". PASS.
- RTC/right-tail checks: not required — DIAGNOSTIC class, no policy/equity curve produced (spec §class).
- No BLOCKED items were reported; the Write-tool caveat for REPORT.md is moot (file exists and matches
  artifacts except M1 below).

## 5. Minor issues found (documented, decision-IRRELEVANT — do not affect either KILL)

- **M1 (prose tally error):** REPORT.md test 4 line says "8 SAME_SIGN / 4 FLAT"; the artifact tally is
  **7 SAME_SIGN / 5 FLAT** (VR: 4 SAME_SIGN + 5 FLAT; ER: 3 SAME_SIGN). The executor's own per-family
  counts (4/5 and 3/0) are correct; only the summed prose is wrong, and it is internally inconsistent
  with the same paragraph's (correct) statement that the 3 opposite-sign cells are FLAT. Zero reversals
  either way; FLAT is not a kill trigger; verdicts unchanged.
- **M2 (imprecise wording):** REPORT says the hist substrate has "128 pre-2012 sess_dates containing two
  NT sessions". The count 128 is exact, but 18 of those dates are 2012+ (through 2020-03-16). The
  handling (state at last bar per sess_date, keyed one-row-per-date like e10_daily_hist.csv) applies
  uniformly to all dates and my truncated recompute at 2015-10-01 (post-double-session era) matches
  exactly, so the method claim stands; only "pre-2012" should read "mostly pre-2012". Also the
  "asserted" for the dev is_last_of_sess coincidence is not a literal assert in the committed script —
  I verified the underlying claim independently and it is true.

## Bottom line

Gates applied letter-exactly to the frozen 12-cell grid; every load-bearing number reproduces
independently (including the frozen-seed bootstrap and from-raw truncated-data state recomputation);
no lookahead, no locked-data touch, no post-hoc selection. KILL (seq 366) and KILL (seq 367) are
**CONFIRMED**. Two immaterial prose errors in REPORT.md noted above (M1, M2).
