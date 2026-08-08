# W5-B1 — Overnight 16:44→09:30 premium, first pass + measured Solar correlation

Date: 2026-08-08 wave (run 2026-08-07). Spec: `research/scalping_lab/specs/W5_programs_wave.md` §B1 (frozen before readout).
Code: `research/scalping_lab/src/python/w5_b1_overnight.py`. Artifacts: this directory
(`w5b1_nightly.csv`, `w5b1_summary.csv`, `w5b1_correlation.csv`, `w5b1_stdout.txt`).
Seed 20260808, 10,000 bootstrap draws, NQ tick = 0.25 pt = $5.

## VERDICT (frozen rule): **NOT PROMISING**

| Frozen criterion | Value | Result |
|---|---|---|
| Unconditional net(2.0t) ≥ +4 t/night | **+17.211 t/night** | PASS |
| Day-clustered 95% CI_lo > 0 | **−17.008 t** | **FAIL** |
| &#124;ρ&#124; vs Solar daily P&L < 0.3 | **0.0149** | PASS |

The premium is economically large in point estimate (+17.2 t ≈ +4.3 NQ pts ≈ $86/night
before the 2.872t stress case) and essentially uncorrelated with Solar — but it is not
statistically established: per-night σ = 577.6 t (≈144 pts) gives SE ≈ 17.5 t on 1,092
nights, so the mean is ≈1 SE from zero and the CI spans [−17.0, +51.0]. Per the frozen
rule the **2005+ extension is NOT triggered**. Reported honestly both ways: the point
estimate would clear the +4t bar more than 4×; the sample cannot distinguish it from 0.

## Frozen implementation decisions (stated per spec)

- **Bars**: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, end-stamped exchange-ET 3-min bars
  (first session bar stamped 18:03). The 16:42–16:45 bar is the bar stamped 16:45:00.
- **Entry**: long 1 NQ at the 16:45:00-stamped bar CLOSE. **Exit**: next session's first
  bar with stamp ≥ 09:30 (and ≤ 17:00, RTH guard), at its **CLOSE** — the spec's frozen
  choice. 1,091/1,092 exits are stamped exactly 09:30:00 (verified in stdout; the guard
  excludes one spec-invalid pairing at the dev-cutoff tail, see contamination note).
- **Night labeling / Solar alignment**: a night is labeled by its exit session date; the
  overnight hold 16:45 D → 09:30 D+1 lives inside Solar session D+1 (18:00 D → 17:00
  D+1), so the join is `exit_session_date == sess`. Overlap: 1,092/1,092 nights.
- **Prior-RTH conditional (the ONE frozen conditional)**: prior RTH return = entry-day
  16:45 bar close − entry-day first ≥09:30 bar close (same reference prices as the
  trade); condition is < 0. Defined on 1,092/1,092 nights.
- **Post-2024** = exit session ≥ 2025-01-01 (348 nights); per-year table shows 2024 separately.
- **CI**: each night is one day-cluster; nights resampled with replacement (10,000×, seed
  20260808), percentile 95% CI on the mean.
- **Solar ledger used**: `runs/E10MASTER_V2/out/daily_v1_v2.csv`, column **net_v1** —
  E10MASTER_**V1** (hold-to-17:00), the **frozen research champion** per
  `runs/E10MASTER_V2/results.md` ("v1 remains the frozen research champion for analytics
  continuity"). v2 (Flatten1644) was not used for the correlation baseline.

## Contamination compliance

Dev window ends 2026-05-31: 20,399 rows with stamps ≥ 2026-06-01 dropped at load before
any analysis (519,833 of 540,232 rows kept; last kept stamp 2026-05-31 23:57, which is
Sunday-evening Globex of the sealed 2026-06-01 session — no trade uses it: the RTH guard
prevents the 2026-05-29 entry from pairing with it, so the last night exits 2026-05-29
09:30). Solar ledger truncated at the same cutoff (1,139 sessions kept).

## Results — per-night expectancy (ticks/night)

Full table with both frictions and CIs: `w5b1_summary.csv`. Net of 2.0t primary friction:

| Group | n | mean net2.0 (t) | 95% CI | hit rate | median (t) |
|---|---|---|---|---|---|
| ALL nights (unconditional) | 1092 | **+17.21** | [−17.01, +50.97] | 0.525 | +27.0 |
| year 2022 | 249 | −49.84 | [−118.09, +20.04] | 0.442 | −65.0 |
| year 2023 | 246 | +5.62 | [−35.20, +46.20] | 0.524 | +20.0 |
| year 2024 | 249 | **+67.04** | [+1.22, +130.95] | 0.570 | +71.0 |
| year 2025 | 247 | +40.61 | [−48.35, +128.47] | 0.563 | +101.0 |
| year 2026 (→05-31) | 101 | +30.68 | [−120.69, +186.56] | 0.525 | +64.0 |
| post-2024 (≥2025-01-01) | 348 | +37.73 | [−37.66, +113.95] | 0.552 | +92.5 |
| COND prior RTH ret < 0 | 500 | **+28.37** | [−27.78, +84.06] | 0.530 | +36.0 |
| complement (prior RTH ≥ 0) | 592 | +7.79 | [−33.51, +49.58] | 0.520 | +21.0 |

Stress friction 2.872t shifts every mean by −0.872 t (see CSV; unconditional +16.34 t,
CI [−18.66, +49.94]) and changes no conclusion.

Reading: the sign flips by year — 2022 (the bear year) was strongly negative, 2024
strongly positive (the only subsample whose CI excludes 0, and it is 1 of 5 year-cells,
uncorrected for selection). The down-prior-day conditional goes the direction the
literature suggests (+28.4 vs +7.8 t) but its CI also spans 0. Nothing here survives the
frozen inference bar.

## Roll-gap / outlier audit

The CSV is a back-adjusted merge; nights spanning a quarterly roll could embed an
adjustment step. Frozen detector: |gross| > 8σ = 4,620.9 t. **Zero nights flagged**, so
with/without-outlier rows in `w5b1_summary.csv` and `w5b1_correlation.csv` are identical
to the primary rows. The largest nights (from `w5b1_nightly.csv`) are genuine macro
events, none on a mid-Mar/Jun/Sep/Dec roll date:

| entry → exit | gross (t) |
|---|---|
| 2024-08-02 → 08-05 (yen-carry unwind weekend) | −3852 |
| 2025-05-09 → 05-12 (weekend) | +3151 |
| 2026-04-07 → 04-08 | +3139 |
| 2025-01-24 → 01-27 (weekend) | −3109 |
| 2025-04-04 → 04-07 (tariff weekend) | −2349 |

224/1092 nights are weekend/holiday spans (>24 h hold); they are kept per spec (the
16:44 program would hold them).

## Measured Solar correlation (nightly net-2.0t $ vs net_v1 $)

| Subset | n | Pearson ρ | Spearman ρ |
|---|---|---|---|
| Full overlap | 1092 | **+0.0149** | +0.0717 |
| Solar losing days (net_v1 < 0) | 644 | **+0.1624** | +0.1782 |

The diversification property is real: ρ ≈ 0.01 full-sample, and even on Solar's losing
days only +0.16 (mildly positive, i.e. very slightly unhelpful, but well inside the
frozen |ρ| < 0.3 gate). Correlation was never the problem — the problem is that the
premium itself is not statistically established in 4.4 years of nights.

## Honest bottom line

An overnight long premium of ≈ +17 t/night net exists in-sample with near-zero Solar
correlation, but per-night volatility of ≈ 578 t means 1,092 nights give no significant
CI, the sign is regime-dependent (2022 negative), and the frozen rule therefore returns
**NOT PROMISING — do not extend to 2005+, build nothing from this pass**. If Program B
is ever revisited, it must be via a NEW frozen spec (e.g., longer history first as a
measurement study), not by retuning this one.
