# SMV2I_CURVE_READS — Statistical Red Team notes (V4 §48 mandatory pass)

Reviewer: red-team subagent, 2026-08-08. Scope: seq 361-365, spec.yaml frozen in commit
0a9cf3f (spec committed BEFORE any results existed; out/ + scripts untracked at review time).
Independent recompute script: own code path, no smv2i_lib import (scratchpad, not committed).

## Verdict: CONFIRMED (one wording nit, not decision-relevant)

## 1. Letter-exact gate/grid/seed audit — PASS

- C-P1 grid exactly {0.35..0.65 step 0.05}, 7 cells, no finer (step1_cp1.py GRID). Mean
  constraint 0.95x implemented as specified; all 7 feasible (min ratio 0.9638 at w=0.65,
  matches frontier CSV). adopt_if evaluated on all three clauses; the ambiguous "eval window
  preserves the ordering" clause was operationalized 3 ways and fails under ALL of them, so
  the ambiguity is not decision-relevant. Else-branch honored: Pareto candidates preserved,
  champion unchanged. Joint-opt {0.50,0.55} correctly NOT recorded as "free validation".
- C-P3 L grid exactly 1.0..3.0 step 0.1 (21 cells, verified in c_p3_pcurves.csv). Constraint
  P<=0.10 at $25k over 504-day resampled paths; all three specified methods run; HEADLINE =
  worst across methods = none. Stability kill honestly recorded N/A (no full-window L* to
  swing) — NOT recorded as pass. Note: reading "any rolling 2y window" as per-path 2y maxDD
  is the less conservative reading; a stricter reading only strengthens the KILL.
- C-P4 rule implemented per formula: monthly, dw = min(10, 2.5*z)pp signed by z, expanding
  z with 365d burn-in (active from 2023-02, 40/53 months — arithmetic checks out), clip
  [0.35,0.65], weights sum 1, decision date strictly before month start. Placebo exactly
  seeds 1..200, same magnitudes, random direction. Gates implemented as d > med + 2*IQR,
  letter-exact.
- C-P7 event/threshold/burn-in per spec (zero-centered +2.5 sigma, strictly-prior expanding
  std via shift(1)); test at block 5, B=10000, seed 20260808 = the spec's CI-type read.
- Seed 20260808 everywhere it matters; placebo seeds 1..200 are the spec's own.
- One documented deviation-candidate: C-P3 moving-block-5 cross-check at B=5000 instead of
  10000. Spec text ties B=5000 to path-type reads (C-P3 explicitly) and B=10000 to CI-type
  reads; the executor's reading is defensible, is disclosed, and the result is nowhere near
  marginal (P at L=1.0 is 0.27-0.43 across windows vs gate 0.10). Not a moved gate.

## 2. Independent recomputations — ALL MATCH

Rebuilt legs from raw inputs (solar_dual_htf_daily.csv + ledger_E2_next_open.parquet) with
independent code:

| quantity | reported | recomputed |
|---|---|---|
| repro max abs diff, 60_40 | "0.0" (artifact: 5.4570e-12) | 5.457e-12 (PASS at 1e-6) |
| SIG (DUAL std ddof=1) | 2143.280220 | 2143.280220039329 |
| fit CDaR90 @ w=0.50 / 0.60 | 9848.80 / 10027.29 | 9848.80 / 10027.29 |
| fit Ulcer @ 0.50 | 4.7216 | 4.7216 |
| RTC @ 0.50 / 0.55 / 0.45 | 0.9703 / 0.9877 / 0.948 | 0.970279 / 0.987671 / 0.948008 |
| champion Sharpe / maxDD / net | 1.2642 / 18131.66 / 194416 | 1.2642404671 / 18131.662 / 194416.04 |
| C-P7 events / clusters / base days | 30 / 11 / 881 | 30 / 11 / 881 |
| C-P7 base mean / fwd5 / fwd10 | 161.95 / -183.84 / -135.65 | 161.948 / -183.841 / -135.649 |
| C-P7 p fwd5 / fwd10 (seed 20260808) | 0.0676 / 0.0012 | 0.0676 / 0.0012 (exact) |
| C-P7 declustered p fwd5 / fwd10 | 0.5354 / 0.2258 | 0.5354 / 0.2258 (exact) |
| C-P4 dSharpe real / threshold | +0.0155 / 0.0331 | +0.015484 / 0.033059 |
| C-P4 dTUW real / threshold | 0 / 2.0 | 0 (133 vs 133) / 2.0 |
| C-P4 w_solar range | 0.5435-0.65 | 0.54352-0.65 |
| C-P3 P(L=1) moving5 / stat20 | 0.4298 / 0.1422 | 0.4277 / 0.1490 (own impl, seed 99, B=3000 — within MC error) |

Seed-robustness spot check (C-P7, the only near-gate number): fwd5 p_below = 0.0605 (seed
12345) / 0.0682 (seed 777) / 0.0676 (executor seed) — stays below 0.10 under every seed
tried; fwd10 p is 0.001-0.002 everywhere. QUALIFIES verdict is not a seed artifact.

## 3. Lookahead/leakage scan — CLEAN (one known, disclosed, non-decision-relevant item)

- Inputs end 2026-05-29; VIRGIN guards assert <= 2026-05-31 on both legs; nothing >= 2026-08-01.
- Fit/eval split honored; adoption required eval-order preservation which FAILED — the
  selection window was not silently reused for evaluation.
- C-P4: decision at last session strictly before month start; expanding stats through the
  decision date only. No same-month outcome use. Placebo shares the identical pipeline.
- C-P7: sigma strictly prior (shift 1), forward windows t+1.., burn-in respected (first
  event 2023-08-24), full windows only (fwd10_n = 30, last event 2026-04-03 fits).
- Known item: vm() vol-match uses full-dev-window std (the champion's own frozen rerank
  construction — required to reproduce the published curve to 1e-6). This leaks full-window
  vol LEVEL into fit-window objective levels in C-P1/C-P4. It is scale-only, uniform in
  applied treatment, disclosed in REPORT.md method note 2, and cannot have driven a wrong
  decision because the only near-adoption read (C-P1) ended in NO ADOPTION.

## 4. Report language audit

- Kills recorded honestly: C-P3 KILL with the un-levered violation stated plainly; C-P4 FAIL
  "dead as specified"; C-P3 stability read recorded N/A, not pass. FACT/INFERENCE/HYPOTHESIS
  labeling used consistently. RTC floor computed and reported everywhere the spec requires.
- C-P7 QUALIFIES is stated per the frozen gate WITH the de-clustered contrary diagnostic
  given equal prominence (n=11 first-of-cluster flips positive) — that is the honest read,
  and the next-wave caution (event-age state) is labeled HYPOTHESIS.
- NIT (only finding): REPORT.md Step 0 states max|diff| "= 0.0" / heading "PASSED (exact)",
  and the executor summary says "max abs diff 0.0 (exact)". The artifact of record
  (repro_check.csv) actually holds 5.4570e-12 on 60_40 (float accumulation noise; DUAL alone
  is exactly 0.0). The gate (atol 1e-6) passes with ~6 orders of margin and nothing changes,
  but "exact"/"0.0" is an overstatement relative to the run's own artifact. Future reports
  should quote the artifact value.
- Minor gate-semantics note: C-P4 "leave-2022-out keeps sign" is degenerate when dTUW = 0
  (0 is not > 0, scored FAIL). Either treatment of the zero leaves the overall C-P4 FAIL
  intact because both placebo gates fail independently.

## 5. Blocked items

None reported; step0 gate passed so the BLOCKED path was never taken. No verification needed.
