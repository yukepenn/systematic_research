
# EVIDENCE01 — Report Traceability Audit

**Family:** EVIDENCE01_REPORT_TRACEABILITY (Master Directive v4 sec29)
**Run directory:** `runs/EVIDENCE01_REPORT_TRACEABILITY/`
**Scope:** pure verification. No construction, no candidate, no modification of any audited run's own files.
**Disposition: CLEAN** — all 4 runs' headline numbers reproduce within tolerance (no >0.5% relative mismatch, no sign flip, anywhere).

## Purpose

Wave 4 repeatedly built `REPORT.md` files from subagent-returned text rather than the orchestrating
session independently recomputing headline numbers. This is an avoidable audit weakness. This run
checks whether it introduced any actual errors, by independently recomputing the stated headline
number(s) of 4 prior runs directly from their own `out/*.csv` / `out/*.json` / `out/*.parquet` /
`src/*.py` — never by reading and trusting `REPORT.md` prose.

## STEP 1 — selection method for the 2 additional (non-mandatory) runs

**Method (fixed, disclosed, non-cherry-picked, fully mechanical):**

1. Read `research/system_master/TESTING_LEDGER.csv` (40 data rows, one per family).
2. Remove the 2 mandatory rows: `U6B_PRODUCT_A_SCALE_RATE`, `AUCTION01_VALUE_STATE`.
3. Remove every row whose `hypothesis_class` column literal value equals `"infrastructure"`. This
   is a mechanical filter on an *existing CSV column* rather than a per-row judgment call, and it
   reproduces the directive's own 3 named examples of "pure infrastructure/audit-only" rows
   exactly (`WAVE4_TRUTH_AUDIT`, `DATA02_MICROSTRUCTURE_INVENTORY`, `WAVE4_FRONTIER_O2_GAMMA_AUDIT`)
   plus 3 more that satisfy the same criterion: `U0_UNIFIED_STATE`, `WAVE1_SYNTHESIS`, `WAVE2_EVI`.
   Verified independently: `WAVE1_SYNTHESIS` and `WAVE2_EVI` have no `runs/<family>/` directory on
   disk at all; `U0_UNIFIED_STATE` has a run directory but its own key_finding is a shared-state-
   table-construction confirmation, not a standalone tested hypothesis with its own headline number
   — consistent with "no single headline number to recompute."
4. Sort the remaining 32 family names alphabetically (Python default string sort).
5. `random.seed(20260809); random.sample(sorted_list, 2)`.

**Reproduce:** `python runs/EVIDENCE01_REPORT_TRACEABILITY/src/01_select_families.py`
**Full sorted candidate list + picks:** `runs/EVIDENCE01_REPORT_TRACEABILITY/out/step1_selection.json`

Excluded as `hypothesis_class=="infrastructure"`: `DATA02_MICROSTRUCTURE_INVENTORY`,
`U0_UNIFIED_STATE`, `WAVE1_SYNTHESIS`, `WAVE2_EVI`, `WAVE4_FRONTIER_O2_GAMMA_AUDIT`,
`WAVE4_TRUTH_AUDIT`.

Sorted 32-family candidate pool (index → family):

```
0  ADD01_PARTICIPATION_EXPANSION       16 SPEC01_SESSION_LEAK_AUDIT
1  COMBO01_MULTIMODAL_SYNERGY          17 U1B_SESSION_HOLD_POLICY
2  EXP01_MARGINAL_EXPOSURE_SHAPE       18 U1_SESSION_HETEROGENEITY
3  FLOW01_AGGRESSIVE_PARTICIPATION     19 U2_DATA_AUDIT
4  H0_PRODUCT_A_HEALTH                 20 U3_HOLD_EXPOSURE_CONTINUATION
5  ICT0102_EVENT_SEQUENCE              21 U4B_SHORT_DECAY_DERISK
6  LEV01_VOLATILITY_ASYMMETRY          22 U4_SHORT_MECHANISM
7  LEV02_TRAILING_REGIME               23 U5_SOFT_WEIGHTING
8  MOM01_INTRADAY_MOMENTUM             24 U6_PRODUCT_A_PATH_DEPENDENCE
9  O2_OWNER_UTILITY_READJUDICATION     25 U7_2026_TIMING_REGIME
10 PORT01_AB_PORTFOLIO_SYNTHESIS       26 U8B_ORGANIZATION_TRANSITION
11 PRICE01_PRODUCT_A_GENUINE_MNQ       27 U8_PATH_ORGANIZATION
12 REL01_CONDITIONAL_CROSSMARKET       28 U9B_MICROSTRUCTURE_ALPHA
13 SHADOW01_SETUP_COMPATIBILITY        29 U9_TRUE_MICROSTRUCTURE
14 SKEW01_RETURN_SKEWNESS              30 VAR01_VARIANCE_SIGNATURE
15 SOFT01_CONTINUOUS_WEIGHTING_AUDIT   31 WIN01_WINNER_EXIT_RELAXATION
```

**Selected: `ICT0102_EVENT_SEQUENCE` and `U6_PRODUCT_A_PATH_DEPENDENCE`.**

So the 4 audited runs are:

| # | Run | Selection |
|---|---|---|
| 1 | U6B_PRODUCT_A_SCALE_RATE | mandatory |
| 2 | AUCTION01_VALUE_STATE | mandatory |
| 3 | ICT0102_EVENT_SEQUENCE | seeded pick |
| 4 | U6_PRODUCT_A_PATH_DEPENDENCE | seeded pick |

## STEP 2/3 — independent recomputation

Recompute script (produces all values below in one run):
`python runs/EVIDENCE01_REPORT_TRACEABILITY/src/02_recompute_headline_numbers.py`
Raw results: `runs/EVIDENCE01_REPORT_TRACEABILITY/out/step2_3_recompute_results.json`

### 1. U6B_PRODUCT_A_SCALE_RATE

`REPORT.md`: `runs/U6B_PRODUCT_A_SCALE_RATE/REPORT.md`

| Metric | REPORT VALUE | RECOMPUTED VALUE | ABS DIFF | REL DIFF | SOURCE ARTIFACT | REPRODUCE COMMAND |
|---|---:|---:|---:|---:|---|---|
| CONTROL canonical net | $177,924.40 | $177,924.40 | $0.00 | 0.000% | `runs/U6B_PRODUCT_A_SCALE_RATE/out/u6b_summary.json` (`canonical_net.CONTROL`); cross-checked by independently summing `out/u6b_year_by_year.csv`'s `net` column across `CONTROL_2022..CONTROL_2026` | `python -c "import pandas as pd; d=pd.read_csv('runs/U6B_PRODUCT_A_SCALE_RATE/out/u6b_year_by_year.csv'); print(d[d.candidate=='CONTROL'].net.sum())"` |
| F0.5 canonical net | $178,213.70 | $178,213.70 | $0.00 | 0.000% | same, `candidate=='F0.5'` | same pattern |
| F0.7 canonical net | $178,531.30 | $178,531.30 | $0.00 | 0.000% | same, `candidate=='F0.7'` | same pattern |
| F0.5 delta, 2022-2025-only | +$843.20 (+0.503%) | +$843.20 (+0.503%) | $0.00 / 0.000pp | 0.000% | `out/u6b_summary.json` (`delta_2022_2025_vs_control.F0.5`); independently re-derived as `sum(F0.5, years 2022-2025) − sum(CONTROL, years 2022-2025)` from `out/u6b_year_by_year.csv` | `python runs/EVIDENCE01_REPORT_TRACEABILITY/src/02_recompute_headline_numbers.py` |
| F0.7 delta, 2022-2025-only | +$970.10 (+0.579%) | +$970.10 (+0.579%) | $0.00 / 0.000pp | 0.000% | same | same |

**Result: exact match on every figure, both direct JSON-read and fully independent re-derivation from the year-by-year CSV.**

### 2. AUCTION01_VALUE_STATE

`REPORT.md`: `runs/AUCTION01_VALUE_STATE/REPORT.md`

| Metric | REPORT VALUE | RECOMPUTED VALUE | ABS DIFF | REL DIFF | SOURCE ARTIFACT | REPRODUCE COMMAND |
|---|---:|---:|---:|---:|---|---|
| D4 pooled Spearman rho, `poc_share` vs `range_60` | −0.353 (rounded, 3dp) | −0.352739 (full precision) | 0.0000 at reported precision | ~0.00% | `out/diagnostics_summary.json` (`D4.poc_share__range_60.rho` = −0.35273937880166517); independently recomputed with `scipy.stats.spearmanr` run directly on `out/decision_outcomes.parquet`'s `poc_share`/`range_60` columns | `python -c "import pandas as pd; from scipy.stats import spearmanr; d=pd.read_parquet('runs/AUCTION01_VALUE_STATE/out/decision_outcomes.parquet',columns=['poc_share','range_60']).dropna(); print(spearmanr(d.poc_share,d.range_60))"` |
| n | 27,293 | 27,293 | 0 | 0.00% | same | same |

**Result: exact match. Fresh `scipy.stats.spearmanr` run on the raw decision-level parquet (bypassing the run's own bootstrap code entirely) reproduces the JSON's rho to 6 significant digits: −0.352739.**

### 3. ICT0102_EVENT_SEQUENCE (seeded pick)

`REPORT.md`: `runs/ICT0102_EVENT_SEQUENCE/REPORT.md`. Three numbers recomputed: the correctness-gate
canonical net (the check both sub-scripts hard-assert before computing anything), and the two ΔR²
figures the report's own text calls out as answering the addendum's central question.

| Metric | REPORT VALUE | RECOMPUTED VALUE | ABS DIFF | REL DIFF | SOURCE ARTIFACT | REPRODUCE COMMAND |
|---|---:|---:|---:|---:|---|---|
| Correctness-gate canonical B-NQ net | $301,915.92 | $301,915.92 | $0.00 | 0.000% | `runs/U0_UNIFIED_STATE/out/u0_state_table.parquet` (`bar_pnl_B_nq_dollars` summed over `is_health_only_bar==False`) | `python -c "import pandas as pd; u=pd.read_parquet('runs/U0_UNIFIED_STATE/out/u0_state_table.parquet',columns=['is_health_only_bar','bar_pnl_B_nq_dollars']); print(u.loc[~u.is_health_only_bar,'bar_pnl_B_nq_dollars'].sum())"` |
| ICT02 full 6-feature-block ΔR² vs M/vol baseline | +0.00045 (rounded, 5dp) | +0.000446 (full precision 0.00044562733677744, rounds to +0.00045) | 0.0000 at reported precision | ~0.00% | `out/ict02_summary.json` (`full_block_dr2`); independently recomputed with a fresh OLS (`numpy.linalg.lstsq`) implementation run directly on `out/ict02_features.csv` | `python runs/EVIDENCE01_REPORT_TRACEABILITY/src/02_recompute_headline_numbers.py` |
| ICT01 SWEEP+MSS ΔR² vs SWEEP-ONLY | +0.00003 (rounded, 5dp) | +0.0000304 (full precision, rounds to +0.00003) | 0.0000 at reported precision | ~0.00% | `out/ict01_summary.json` (`sweep_mss_dr2_vs_sweep_only`); independently recomputed via fresh OLS on `out/ict01_events.csv` | same |

**Result: exact match on all 3 numbers.** The ΔR² figures are correctly rounded to 5 decimal places
in the prose (a legitimate reporting-precision convention for effect sizes this small, not a
transcription error) — the fully independent OLS recompute lands on the same value as the run's own
persisted JSON to 10 significant digits in both cases.

### 4. U6_PRODUCT_A_PATH_DEPENDENCE (seeded pick)

`REPORT.md`: `runs/U6_PRODUCT_A_PATH_DEPENDENCE/REPORT.md`. The report's own **Verdict** section
states explicitly: *"Part 3 is the load-bearing constraint"* — the right-tail check that determines
whether Part 2's statistically-real trajectory-prediction finding is actionable. Recomputed directly
from the raw block table `out/u6_block_table.csv` (not the pipeline's own pre-filtered
`step3_top20_blocks.csv`/`step3_bottom20_blocks.csv`, to make the recheck genuinely independent of
the run's own top/bottom-20 selection code).

| Metric | REPORT VALUE | RECOMPUTED VALUE | ABS DIFF | REL DIFF | SOURCE ARTIFACT | REPRODUCE COMMAND |
|---|---:|---:|---:|---:|---|---|
| n canonical nonzero blocks | 4,809 | 4,809 | 0 | 0.00% | `out/u6_block_table.csv` (`start_is_health_only==False`) | `python runs/EVIDENCE01_REPORT_TRACEABILITY/src/02_recompute_headline_numbers.py` |
| TOP-20 net_pnl range | $6,563.90 – $18,352.15 | $6,563.90 – $18,352.15 | $0.00 | 0.000% | same, `nlargest(20,'net_pnl')` | same |
| BOTTOM-20 net_pnl range | −$4,934.45 – −$2,509.65 | −$4,934.45 – −$2,509.65 | $0.00 | 0.000% | same, `nsmallest(20,'net_pnl')` | same |
| TOP-20 started in 1-3-contract state | 14/20 (70%) | 14/20 (70%) | 0 | 0.00% | same, `abs(start_exposure)<=3` | same |
| BOTTOM-20 started in 1-3-contract state | 15/20 (75%) | 15/20 (75%) | 0 | 0.00% | same | same |

**Result: exact match on every figure**, including a re-derivation of the top-20/bottom-20 block
sets themselves from the raw block table rather than trusting the run's own already-filtered
step-3 output CSVs.

## Investigation of mismatches

**None found.** Every metric across all 4 runs reproduced either exactly (bit-for-bit modulo
ordinary floating-point summation noise at the ~$1e-5–1e-10 level, e.g. `177924.3999999992` vs
`177924.40`) or as a correctly-rounded display of the exact recomputed value (e.g. report shows
"+0.00045", full-precision recompute is `0.00044562733677744`, which rounds to `0.00045` — this is
the "legitimate reporting convention (rounding)" carve-out named in the task instructions, not a
defect). No sign flips occurred anywhere. No relative difference exceeded ordinary floating-point
noise (all effectively 0.00%, well under the 0.5% P0 threshold).

## Disposition: **CLEAN**

All 4 audited runs' headline numbers reproduce within tolerance directly from their own raw output
artifacts, independently of their `REPORT.md` prose:

- **U6B_PRODUCT_A_SCALE_RATE** (mandatory) — CLEAN
- **AUCTION01_VALUE_STATE** (mandatory) — CLEAN
- **ICT0102_EVENT_SEQUENCE** (seeded pick) — CLEAN
- **U6_PRODUCT_A_PATH_DEPENDENCE** (seeded pick) — CLEAN

This 4-run sample found **no evidence** that Wave 4's practice of building `REPORT.md` from
subagent-returned text (rather than the orchestrating session independently recomputing headline
numbers) introduced any actual transcription, staleness, or computation error into these reports.
This is reassuring but explicitly **not** a full-campaign clearance — it is a 4-run sample (2
mandatory + 2 randomly selected from a 32-family pool) out of the full ~40-family
`TESTING_LEDGER.csv`, and does not itself constitute evidence about the other 36 families' reports.

## Files

- `runs/EVIDENCE01_REPORT_TRACEABILITY/spec.yaml` — frozen method spec (STEP 1 selection rule + STEP 2/3 recompute targets, written before this report)
- `runs/EVIDENCE01_REPORT_TRACEABILITY/src/01_select_families.py` — STEP 1 selection script
- `runs/EVIDENCE01_REPORT_TRACEABILITY/src/02_recompute_headline_numbers.py` — STEP 2/3 recompute script (all 4 runs, one execution)
- `runs/EVIDENCE01_REPORT_TRACEABILITY/out/step1_selection.json` — full 32-family sorted candidate list + the 2 seeded picks
- `runs/EVIDENCE01_REPORT_TRACEABILITY/out/step2_3_recompute_results.json` — all recomputed values, report values, for all 4 runs

No files belonging to any of the 4 audited runs (`REPORT.md`, `spec.yaml`, `out/`, `src/`) were
modified. This run's own files are currently untracked in git (not yet committed) since the task
did not request a commit.
