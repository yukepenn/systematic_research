# SMV2I_CURVE_READS — REPORT (seq 361-365)

Run class: PORTFOLIO_TEST + DIAGNOSTIC (V4 s41). Spec frozen 2026-08-08 (`spec.yaml`).
Executor scripts: `smv2i_lib.py`, `step0_repro.py`, `step1_cp1.py`, `step2_cp3.py`,
`step3_cp4.py`, `step4_cp7.py`, `step5_report.py` (this dir). All numbers below come from
files in `out/`. Seed 20260808 everywhere. Dev window: 1,139 sessions 2022-01-03..2026-05-29
(<= 2026-05-31). No input touches data >= 2026-08-01 (asserted in `smv2i_lib.load_legs`;
ledger max sess 2026-05-29).

## Step 0 — Mandatory reproduction gate: PASSED (exact)

Legs rebuilt exactly as `runs/SMV2H_ONECONTRACT/rerank.py`: DUAL from
`solar_dual_htf_daily.csv`; BMOM E2 = per-sess sum(`net_c1_ticks`)x5.0 from
`ledger_E2_next_open.parquet`, reindexed to DUAL calendar, 0-filled; SIG = std(DUAL, ddof=1)
= 2143.280220; vm(x) = x*SIG/std(x); champion = vm(0.60*DUAL + 0.40*vm(BM)).

FACT (`out/repro_check.csv`): max|diff| vs published `rerank_curves.csv` = **0.0** on 60_40
(gate atol 1e-6), and 0.0 on DUAL, BM_E2, 80_20, 70_30, 50_50. Calendar match TRUE, n=1139.

## Seq 361 — C-P1 static blend frontier: NO ADOPTION, champion 60/40 unchanged

Grid w_solar in {0.35..0.65 step 0.05}, portfolios on the rerank equal-vol basis
(outer vm to SIG, identical to champion construction). Fit 2022-01-01..2024-12-31,
eval 2025-01-01..2026-05-31. (`out/c_p1_frontier.csv`, `out/c_p1_verdict.csv`)

FACT — mean constraint (fit mean >= 0.95x champion's) holds at every grid point
(min ratio 0.9638 at w=0.65). Fit-window optima among feasible w:

| objective (fit) | optimum w | value at opt | value at 0.60 |
|---|---|---|---|
| CDaR_0.90 | **0.50** | 9,848.80 | 10,027.29 |
| EDaR_0.90 | **0.55** | 10,876.52 | 11,132.38 |
| Ulcer ($100k base, %) | **0.50** | 4.7216 | 4.8062 |

- FACT: the three fit optima agree within +-0.07 (spread 0.05) -> first adopt_if clause met.
- FACT: the eval window does NOT preserve the ordering: eval optima are 0.60 (CDaR90),
  0.55 (EDaR90), 0.65 (Ulcer); fit-opt beats 0.60 on eval only for EDaR (1 of 3); Spearman
  fit<->eval rank corr per objective = 0.286 / 0.464 / 0.214. Second adopt_if clause FAILS
  under every read computed.
- FACT: RTC floor (policy sum over champion top-decile up-days >= 0.97x): holds at w=0.50
  (0.9703) and w=0.55 (0.9877); fails at w<=0.45 (0.948 at 0.45, 0.891 at 0.35).
- FACT: joint fit optimum {0.50, 0.55} is not entirely within {0.55, 0.60, 0.65} -> no
  "free validation of 60/40 zone" record.

VERDICT (per spec else-branch): **no forced single weight; champion unchanged.** Pareto
candidates preserved: w=0.50 (CDaR/Ulcer fit-opt, RTC 0.9703) and w=0.55 (EDaR fit-opt,
RTC 0.9877). INFERENCE: the fit frontier is extremely flat (CDaR90 varies < 2% across
0.45-0.60); the eval reversal is consistent with noise on a flat frontier, not with a
genuine risk improvement below 0.60 solar.

## Seq 362 — C-P3 DD-constrained leverage: KILL — no headroom, L* below grid floor

Base = reproduced champion curve. B=5000 paths of 504 days per method, seed 20260808,
maxDD scales linearly in L. (`out/c_p3_lstar.csv`, `out/c_p3_pcurves.csv`,
`out/c_p3_stability.csv`)

FACT — P(maxDD over resampled 2y path > $25k) at **L=1.0, full window**:
stationary(20) 0.1422 | moving-block(5) 0.4298 | joint-loss-2x 0.1568 — all > 0.10.
Median resampled 2y maxDD: 18,238 / 23,627 / 18,596 $.

- FACT: no L in the frozen grid {1.0..3.0} satisfies P <= 0.10 for any method on the full
  window -> L* per method = none; HEADLINE L* (worst across methods) = **none (< 1.0)**.
- FACT: trims — drop-first-6mo: still no L* under any method (P at L=1.0: 0.180/0.388/0.188).
  Drop-last-6mo: stationary L*=1.1, joint-loss L*=1.0, moving-5 still none (P=0.266 at
  L=1.0) -> headline still none. Stability-kill read N/A (no full-window L* to swing).
- Method note: B=5000 used for all three variants (spec ties B=5000 to path-type reads;
  the moving-block-5 cross-check inherits it — stated, not tuned).

VERDICT: **C-P3 KILL (clean).** FACT: the un-levered champion already violates the
$25k/2y/10% constraint under every resampling method. INFERENCE: the realized dev-path
maxDD (18.1k on the eval half) understates resampled 2y tail risk because the actual path's
calm stretches are not exchangeable; the moving-block(5) variant is worst because short
blocks destroy the compensating serial structure. Research-only read per V4 s39 — and the
answer is that there is no leverage recommendation to make: headroom <= 0.

## Seq 363/364 — C-P4 drought tilt: FAIL (placebo gate), parked

Rule as frozen: monthly dw = min(10, 2.5*z_TUW) pp toward the deeper-in-drought engine,
z from expanding mean/std of the daily TUW gap (solar - bmom legs), >= 365d burn-in,
w_solar clipped to [0.35, 0.65], exposure sum 1, memoryless around the 0.60 baseline
(interpretation documented in `step3_cp4.py` header). 53 months, 40 tilt-active.
Realized w_solar range 0.5435-0.65; mean |tilt| 1.9 pp. (`out/c_p4_tilt.csv`,
`out/c_p4_placebo.csv`, `out/c_p4_summary.csv`)

FACT (full dev window, equal-vol basis): champion sharpe 1.2642, longest TUW 133d,
maxDD 18,131.66, net 194,416. Tilt policy: sharpe 1.2797, longest TUW 133d,
maxDD 18,010.02, net 196,797.

| gate | real | pass threshold | result |
|---|---|---|---|
| TUW reduction > placebo med + 2*IQR | 0 days | > 2.0 days (med 0.0, IQR 1.0) | **FAIL** |
| dSharpe > placebo med + 2*IQR | +0.0155 | > +0.0331 (med -0.0017, IQR 0.0174) | **FAIL** |
| leave-2022-out keeps sign | dTUW 0 (not >0); dSharpe +0.0206 | both > 0 | **FAIL** |
| RTC floor >= 0.97 | 0.99996 | >= 0.97 | pass |

VERDICT: **C-P4 FAIL — dead as specified.** FACT: the real tilt beats the 200-seed
random-direction placebo median on Sharpe but by less than the 2xIQR bar, and produces zero
reduction in longest TUW. INFERENCE: with magnitudes averaging 1.9 pp on a frontier this
flat (see C-P1), the tilt cannot move TUW/Sharpe beyond direction-noise; the drought signal
adds nothing distinguishable from a coin flip of the same size.

## Seq 365 — C-P7 windfall pre-test: QUALIFIES per frozen gate — with a material caveat

Event: trailing 5d PnL of DUAL6040 > +2.5 sigma, sigma = expanding std of the 5d-sum series
using strictly-prior obs (through t-1), >= 365d burn-in, zero-centered threshold (literal
spec reading; a mean-centered variant would give 26 vs 30 events — count reported only).
Base = mean daily PnL over the 881 burn-in-eligible days = +161.95/day. One-sided
moving-block bootstrap (block 5, B=10000, seed 20260808) over event-level (fwd - base),
base treated as fixed (881-day estimate; its s.e. is second-order vs the 30-event mean).
(`out/c_p7_events.csv`, `out/c_p7_summary.csv`)

FACT: 30 event days in 11 clusters (largest: 2025-04-08..15, 6 days).
- Forward 5d mean: **-183.84/day** (diff -345.79 vs base), one-sided p(below) = **0.0676**.
- Forward 10d mean: **-135.65/day** (diff -297.60), p = **0.0012**.

VERDICT (frozen gate): forward PnL IS below base at one-sided p < 0.10 on both horizons ->
**C-P7 QUALIFIES for a bounded policy spec next wave.** No policy built this run.

CAVEAT (diagnostic, labeled in `step4_cp7.py`, not the spec verdict): de-clustered to the
first event of each cluster (n=11), forward means flip positive: fwd5 +183.78 (p=0.535),
fwd10 +84.01 (p=0.226). INFERENCE: the post-windfall giveback is concentrated in
continuation days deep inside windfall clusters, not at the first +2.5-sigma crossing.
HYPOTHESIS for the next-wave spec: any bounded de-risking rule will need the event age /
consecutive-day count in state, otherwise it will trigger at first crossing where the
forward drift is not negative; this must be tested against the multiplicity cost.

## Artifact index (`out/`)

repro_check.csv | c_p1_frontier.csv | c_p1_verdict.csv | c_p1_curves.csv |
c_p3_lstar.csv | c_p3_pcurves.csv | c_p3_stability.csv | c_p4_tilt.csv |
c_p4_placebo.csv | c_p4_summary.csv | c_p4_curves.csv | c_p7_events.csv | c_p7_summary.csv

## Method notes (spec-silent choices, all documented in script headers)

1. EDaR_0.90 solved by bounded 1-D minimization over log z (scipy, logsumexp-stabilized);
   sanity EDaR >= CDaR asserted at every grid point. Ulcer base: fixed $100k notional,
   d_pct = 100*dd$/100k.
2. C-P1/C-P4 curves use the rerank outer vol-match to SIG (full-dev std) — the champion's
   own construction; scale-only, applied uniformly, so orderings are unaffected except
   through second-order vol-of-mix differences.
3. C-P4 tilt read as memoryless around the 0.60 baseline (not cumulative drift); with the
   10 pp cap and the 0.65 ceiling this bounds w_solar to [0.50, 0.65] in practice.
4. C-P7 sigma strictly prior (shift 1), events not de-overlapped for the spec test; block-5
   event bootstrap carries the within-cluster dependence.
