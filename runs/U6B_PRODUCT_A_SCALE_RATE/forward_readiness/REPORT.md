# U6B forward-readiness panel — CONTROL / F0.5 / F0.7 (genuine MNQ pricing)

Master Directive v4 sec8, Wave 5. Output location: `runs/U6B_PRODUCT_A_SCALE_RATE/forward_readiness/`.
Script: `forward_readiness/src/01_build_panel.py`. All outputs: `forward_readiness/out/`.

**Purpose and scope of this document.** This is an uncertainty-quantification panel, not a new
adjudication. U6B's standing disposition — **NOT PROMOTED** (`runs/U6B_PRODUCT_A_SCALE_RATE/REPORT.md`,
both grid cells trigger the preregistered falsification condition on the 2022-2025-only delta being
under 1% of CONTROL's 2022-2025 net) — is unchanged by anything below. What this panel adds is: every
forward-looking number here carries an explicit interval (bootstrap or a stated reason it can't), so a
reader never has to take a single point estimate ("F0.5's Sharpe is 1.186") as a fact about the future.

**Reproduce everything:**
```
python3 "runs/U6B_PRODUCT_A_SCALE_RATE/forward_readiness/src/01_build_panel.py"
```
Deterministic (`SEED=20260809`, `N_BOOT=1000`). Full run log saved at
`forward_readiness/out/run_log.txt`. Consolidated single-file JSON of every section:
`forward_readiness/out/00_consolidated_panel.json`.

**Absolute-rule compliance (FACT, double-gated):** the script asserts every input series'
max date `< 2026-08-01` before doing anything else (it passes: source CSVs stop at
2026-07-31), and independently, `primary_objective_v2.load_daily_pnl` raises on any date
`>= 2026-08-01` as a second, library-level gate. Neither gate was ever triggered — no
locked-forward data was touched.

**Date convention used throughout (FACT, verified directly against the CSVs):** canonical
window = 2022-01-03 .. 2026-05-29 (the row immediately following 2026-05-29 in all three
`*_daily_GENUINE_MNQ.csv` files is 2026-06-01, confirming no ambiguity). Health-only extension
= 2026-06-01 .. 2026-07-31.

---

## 1. Full history (canonical, 2022-01-03 .. 2026-05-29), with Sharpe bootstrap CI

Source: `forward_readiness/out/01_full_history_canonical.csv`. Battery = this campaign's standing
`smv2_common.dd_battery` (same function used to build every other U6B artifact this wave); Sharpe
CI = session-block bootstrap, 1000 resamples with replacement, 2.5/97.5 percentiles.

| Candidate | n | Net | Sharpe | **Sharpe 95% CI** | Sortino | Calmar | maxDD_eod | CDaR95 | pos_day_pct |
|---|---:|---:|---:|:---:|---:|---:|---:|---:|---:|
| CONTROL | 1,139 | $178,687.40 | 1.1819 | **[0.320, 2.036]** | 2.3490 | 2.3160 | $17,069.90 | $14,254.11 | 44.25% |
| F0.5 | 1,139 | $178,988.70 | 1.1858 | **[0.317, 2.047]** | 2.3689 | 2.2771 | $17,390.80 | $14,217.43 | 44.16% |
| F0.7 | 1,139 | $179,302.30 | 1.1873 | **[0.318, 2.045]** | 2.3654 | 2.3367 | $16,977.30 | $14,187.36 | 44.25% |

**INFERENCE:** the three candidates' point-estimate Sharpe differences (1.1819 vs 1.1858 vs
1.1873, a spread of 0.005) are two orders of magnitude smaller than the width of any one
candidate's own 95% CI (roughly ±0.86 around the point estimate). A reader who only saw the point
estimates would see "F0.7 > F0.5 > CONTROL"; a reader who sees the CIs sees three heavily
overlapping intervals that cannot distinguish the three candidates from session-resampling noise
alone. This is consistent with (not proof of, since the CI is on each series' *own* uncertainty,
not on the *paired* delta) the underlying effect being small, exactly as the original U6B
construction report already concluded from the dollar deltas.

**LIMITATION:** this CI is on each candidate's *unpaired* Sharpe, not on the CONTROL-vs-candidate
*difference* — a difference-CI would be tighter (paired resampling shares session draws), but
building one wasn't in this panel's brief; the existing dollar-delta wash test (below, §2) is
this campaign's standing paired comparison and remains the authoritative test for promotion.

---

## 2. 2022-2025-only (LOYO / wash-test slice)

Source: `forward_readiness/out/02_2022_2025_only.csv`.

| Candidate | n | Net | Sharpe | Sharpe 95% CI |
|---|---:|---:|---:|:---:|
| CONTROL | 1,033 | $167,884.20 | 1.2616 | [0.394, 2.182] |
| F0.5 | 1,033 | $168,743.40 | 1.2701 | [0.417, 2.208] |
| F0.7 | 1,033 | $168,867.80 | 1.2705 | [0.408, 2.201] |

**FACT (cross-check against existing artifact):** F0.5 delta = +$859.20 (+0.5118%), F0.7 delta =
+$983.60 (+0.5859%) — both **exact matches** to `u6b_mnq_repricing_recon.json`'s own
`genuine_delta_2022_2025` figures. This is a correctness check on this panel's own loader, not a
new finding: both fall under the preregistered 1% wash threshold, the falsification condition
that already produced the NOT PROMOTED verdict.

---

## 3. 2026 research-consumed (Jan-May canonical + Jun-Jul health-only extension)

Source: `forward_readiness/out/03_2026_consumed.csv`. Reported as three separate rows per
candidate — canonical-only, extension-only, and combined — per the family brief's instruction to
flag the extension separately even when discussing "2026" as a whole. **The combined row is
observational only and is never used for promotion**, matching spec.yaml's own standing
convention for this extension.

| Candidate | Segment | n | Net | Sharpe | Sharpe 95% CI |
|---|---|---:|---:|---:|:---:|
| CONTROL | 2026 canonical (Jan-May) | 106 | $10,803.20 | 0.6110 | [-2.554, 3.560] |
| CONTROL | 2026 extension (Jun-Jul, health-only) | 45 | $34,970.10 | 3.4228 | [-1.128, 7.602] |
| CONTROL | 2026 combined (research-consumed) | 151 | $45,773.30 | 1.6208 | [-0.768, 3.933] |
| F0.5 | 2026 canonical (Jan-May) | 106 | $10,245.30 | 0.5802 | [-2.563, 3.555] |
| F0.5 | 2026 extension (Jun-Jul, health-only) | 45 | $35,118.90 | 3.4526 | [-1.116, 7.604] |
| F0.5 | 2026 combined (research-consumed) | 151 | $45,364.20 | 1.6104 | [-0.759, 3.892] |
| F0.7 | 2026 canonical (Jan-May) | 106 | $10,434.50 | 0.5905 | [-2.568, 3.555] |
| F0.7 | 2026 extension (Jun-Jul, health-only) | 45 | $35,201.40 | 3.4556 | [-1.098, 7.602] |
| F0.7 | 2026 combined (research-consumed) | 151 | $45,635.90 | 1.6183 | [-0.770, 3.909] |

**LIMITATION (explicit, not silent):** every CI in this section straddles zero and is very wide —
n=45-151 sessions is simply too little data to bound a forward Sharpe with any precision, whether
canonical-only, extension-only, or combined. The high point-estimate Sharpe on the 45-session
extension (3.4+) is **not** a reliable read of a "current-regime edge"; its own CI runs from
roughly -1.1 to +7.6. Treat point estimates in this section as directional color only.

---

## 4. Year-by-year, with added bootstrap CI

`forward_readiness/out/04_year_by_year_reused.csv` **reuses** `u6b_mnq_year_by_year.csv` verbatim
(not recomputed). `forward_readiness/out/04_year_by_year_bootstrap_ci.csv` is the **new** addition:
a session-block bootstrap Sharpe CI per candidate-year.

| Candidate | Year | n | Sharpe (recomputed, matches reused file) | Sharpe 95% CI | Note |
|---|---|---:|---:|:---:|---|
| CONTROL | 2022 | 258 | 1.2731 | [-0.785, 3.049] | |
| CONTROL | 2023 | 258 | 0.8265 | [-1.176, 2.503] | |
| CONTROL | 2024 | 259 | 1.2735 | [-0.708, 2.945] | |
| CONTROL | 2025 | 258 | 1.6026 | [-0.373, 3.244] | |
| CONTROL | 2026 | 106 | 0.6110 | [-2.554, 3.560] | **partial year (Jan-May only)** |
| F0.5 | 2022 | 258 | 1.2699 | [-0.787, 3.021] | |
| F0.5 | 2023 | 258 | 0.8036 | [-1.179, 2.484] | |
| F0.5 | 2024 | 259 | 1.2870 | [-0.717, 2.965] | |
| F0.5 | 2025 | 258 | 1.6345 | [-0.351, 3.273] | |
| F0.5 | 2026 | 106 | 0.5802 | [-2.563, 3.555] | **partial year (Jan-May only)** |
| F0.7 | 2022 | 258 | 1.2695 | [-0.785, 3.029] | |
| F0.7 | 2023 | 258 | 0.8096 | [-1.186, 2.495] | |
| F0.7 | 2024 | 259 | 1.2879 | [-0.711, 2.952] | |
| F0.7 | 2025 | 258 | 1.6325 | [-0.346, 3.281] | |
| F0.7 | 2026 | 106 | 0.5905 | [-2.568, 3.555] | **partial year (Jan-May only)** |

**LIMITATION (honest, as instructed):** every single-year CI is wide (≈±1.5-2.0 around the point
estimate) even for the four ~258-session full years — a single calendar year is inherently thin
for Sharpe-CI purposes at daily granularity. The 2026 row is additionally a *partial* year (106
sessions, Jan-May only), visibly the widest of the five and the least precise; it is not "too
thin to compute" (1000 reps ran fine) but should be weighted as the least reliable of the five
year-rows, not excluded.

---

## 5. Quarter-by-quarter (canonical window, new cut)

Source: `forward_readiness/out/05_quarter_by_quarter.csv` (54 rows = 18 quarters × 3 candidates),
computed directly from the daily CSVs (not present elsewhere in the campaign before this panel).
CONTROL shown; F0.5/F0.7 follow the same shape (all three candidates' quarterly nets differ from
each other by low hundreds of dollars per quarter, dwarfed by quarter-to-quarter variation itself):

| Quarter | n | Net | Sharpe | Partial? |
|---|---:|---:|---:|:---:|
| 2022Q1 | 64 | $11,999.90 | 1.217 | |
| 2022Q2 | 64 | $13,578.10 | 1.201 | |
| 2022Q3 | 66 | $9,477.00 | 1.204 | |
| 2022Q4 | 64 | $13,080.00 | 1.524 | |
| 2023Q1 | 64 | -$3,277.40 | -0.696 | |
| 2023Q2 | 65 | $5,137.80 | 0.964 | |
| 2023Q3 | 65 | $7,311.60 | 1.313 | |
| 2023Q4 | 64 | $7,570.10 | 1.613 | |
| 2024Q1 | 63 | -$3,361.20 | -0.754 | |
| 2024Q2 | 65 | $12,103.50 | 2.316 | |
| 2024Q3 | 66 | $9,112.10 | 1.025 | |
| 2024Q4 | 65 | $14,310.80 | 2.398 | |
| 2025Q1 | 63 | $11,829.00 | 1.064 | |
| 2025Q2 | 64 | $17,451.20 | 1.333 | |
| 2025Q3 | 66 | $8,488.40 | 1.581 | |
| 2025Q4 | 65 | $33,073.30 | 2.562 | |
| 2026Q1 | 63 | $25,370.50 | 2.167 | |
| 2026Q2 | 43 | -$14,567.30 | -2.579 | **yes — canonical cutoff (2026-05-29) lands mid-quarter, only ~43 of a normal ~64 sessions** |

**FACT:** two calendar quarters (2023Q1, 2024Q1) had negative net for CONTROL; only 2026Q2 is a
genuinely truncated quarter (43 sessions vs the ~63-66 typical of a full quarter — every other
quarter is a complete calendar quarter within the observation window, not a data gap). 2026Q2 is
also the single worst quarter in the whole 18-quarter canonical history (-$14,567.30 CONTROL,
Sharpe -2.579) — this is the same Jan-May-2026 weakness already visible in §3/§11.

---

## 6. LOYO (leave-one-year-out, 2022-2025)

Source: `forward_readiness/out/06_loyo_delta_vs_control.csv`. Cross-checked first against the
existing artifact, then extended with the finer drop-one-year cut that wasn't already present.

**Cross-check (FACT):** this panel's own recomputation of the full-4-year 2022-2025 delta
(CONTROL=$167,884.20, F0.5=$168,743.40, F0.7=$168,867.80) reproduces
`u6b_mnq_repricing_recon.json`'s `genuine_delta_2022_2025` **exactly** (F0.5 $859.20/0.5118%,
F0.7 $983.60/0.5859% — MATCH, asserted in the script).

**New: drop-one-year-at-a-time (recomputed, not present elsewhere):**

| Dropped year | F0.5 delta vs CONTROL | F0.5 delta % | F0.7 delta vs CONTROL | F0.7 delta % |
|---|---:|---:|---:|---:|
| (none — full 4yr) | +$859.20 | +0.512% | +$983.60 | +0.586% |
| 2022 | +$979.60 | +0.818% | +$1,151.40 | +0.962% |
| 2023 | +$1,341.90 | +0.888% | +$1,339.30 | +0.886% |
| 2024 | +$651.10 | +0.480% | +$711.80 | +0.525% |
| **2025** | **-$395.00** | **-0.407%** | **-$251.70** | **-0.259%** |

**INFERENCE:** 6 of 8 drop-one-year cells stay positive — directionally consistent, as the
original REPORT.md's "full LOYO battery shows a consistent, small, favorable direction on nearly
every metric" already stated. But dropping 2025 specifically **flips the sign for both
candidates** — the edge is not spread evenly across 2022-2025, it is disproportionately carried by
2025 (the year with the single largest quarter, 2025Q4, in §5). This is a genuine finding new to
this panel: "consistent direction across LOYO cells" is true in a headcount sense (6/8) but
conceals that the magnitude is unevenly distributed and the sign is not robust to removing the
single best year.

---

## 7-8. Rolling 20/60/120/252-session windows: distribution + worst observed

Sources: `forward_readiness/out/07_rolling_window_distributions.csv` (distribution),
`08_worst_rolling_windows.csv` (worst, dated), `07b_rolling_series_w60.csv` /
`07b_rolling_series_w252.csv` (full raw series for audit). **Disclosed methodological choice:**
computed on the **full available series** (canonical + health-only extension, 2022-01-03 ..
2026-07-31), not canonical-only — this deliberately includes the most recent evidence in the
"how much does a same-length future window plausibly vary" picture (per sec32's instruction to
give recent evidence high interpretive weight), at the cost of a few of the longer windows
technically spanning the canonical/extension boundary (flagged in the `overlaps_extension` /
`n_windows_overlapping_extension` columns; none of this feeds any promotion-relevant statistic).

**Rolling Sharpe distribution (CONTROL; F0.5/F0.7 are visually identical shape, see CSV for exact
figures):**

| Window | n_windows | min | p25 | median | p75 | max |
|---|---:|---:|---:|---:|---:|---:|
| 20 | 1,165 | -5.92 | -0.58 | 1.17 | 2.78 | 7.94 |
| 60 | 1,125 | -3.01 | 0.50 | 1.36 | 2.00 | 4.75 |
| 120 | 1,065 | -0.47 | 0.88 | 1.26 | 1.63 | 3.02 |
| 252 | 933 | 0.36 | 0.95 | 1.23 | 1.51 | 2.17 |

**Rolling net $ distribution (CONTROL):**

| Window | min | p25 | median | p75 | max |
|---|---:|---:|---:|---:|---:|
| 20 | -$12,796 | -$1,033 | $2,412 | $6,686 | $35,703 |
| 60 | -$15,846 | $3,348 | $9,586 | $15,247 | $39,766 |
| 120 | -$4,059 | $11,027 | $17,547 | $27,369 | $58,559 |
| 252 | $9,588 | $22,778 | $33,386 | $54,459 | $97,706 |

**INFERENCE (this is what "uncertainty around forward Sharpe" concretely means):** a rolling
20-session Sharpe is essentially uninformative in isolation — it has historically ranged from
-5.9 to +7.9 for CONTROL, with the interquartile range alone spanning -0.58 to +2.78. Even the
252-session ("roughly annual") rolling Sharpe has ranged 0.36 to 2.17 historically — a future
252-session stretch reading anywhere in that band would be unremarkable, not evidence of
regime change. Rolling net (dollar) distributions are more legible for the shorter windows: a
future 60-session stretch losing $15-16k is not unprecedented, it has already happened.

**Worst observed, dated (item 8):**

| Candidate | Window | Metric | Worst value | Window | Overlaps extension? |
|---|---:|---|---:|---|:---:|
| CONTROL | 20 | Sharpe | -5.92 | 2025-07-03 .. 2025-07-30 | No |
| CONTROL | 20 | Net | -$12,796 | 2025-04-25 .. 2025-05-22 | No |
| CONTROL | 60 | Sharpe | -3.01 | 2024-01-10 .. 2024-04-03 | No |
| CONTROL | 60 | Net | -$15,846 | **2026-03-10 .. 2026-06-01** | **Yes** |
| CONTROL | 120 | Sharpe/Net | -0.47 / -$4,059 | 2023-02-09 .. 2023-07-26 | No |
| CONTROL | 252 | Sharpe/Net (min, not negative) | 0.36 / $9,588 | 2022-06-06 .. 2023-05-25 | No |
| F0.5 | 20 | Sharpe | **-6.01 (worst of the three)** | 2026-04-03 .. 2026-04-30 | No |
| F0.5 | 60 | Net | **-$16,426 (worst of the three)** | 2026-03-10 .. 2026-06-01 | Yes |
| F0.7 | 20 | Sharpe | -5.98 | 2025-07-03 .. 2025-07-30 | No |
| F0.7 | 60 | Net | -$16,242 | 2026-03-10 .. 2026-06-01 | Yes |

Full per-candidate/window worst rows (all 24 = 3 candidates × 4 windows × 2 metrics) are in
`08_worst_rolling_windows.csv`.

**FACT worth flagging at high interpretive weight (sec32):** the single worst 60-session net
stretch on record, for **all three candidates**, is the most recent one — 2026-03-10 to
2026-06-01, which straddles the canonical/extension boundary. F0.5 is the worst of the three
here (-$16,426 vs CONTROL's -$15,846), i.e. the rate limiter modestly *deepened* the campaign's
most recent bad stretch rather than cushioning it. This is genuine, dated, recent evidence and is
reported plainly — but per sec32's other half ("do not let a recent-year backtest alone create a
false promotion [or demotion]"), one overlapping 60-session window is not treated here as proof
the mechanism degrades in the current regime; it is one data point consistent with the
already-established finding (§11 below) that 2026 Jan-May was weak for both candidates.

---

## 9. Tail concentration (reusing this campaign's own top-20/bottom-20 block convention)

Source: `runs/U6B_PRODUCT_A_SCALE_RATE/out/u6b_righttail_top20_winners.csv` /
`u6b_righttail_bottom20_losers.csv` (reused verbatim — these were built once already during the
original U6B construction, not rebuilt here). Summary written to
`forward_readiness/out/09_10_tail_concentration_winner_retention.csv`.

**LIMITATION, explicitly disclosed (as instructed):** these two specific files are **LEGACY
NQ-proxy pricing, not genuine-MNQ-repriced**. `u6b_mnq_repricing_recon.json`'s own
exposure-path-identity finding ("price affects fills only, never the rate-limiter's own
scale-up/quality decisions") means the block *identities* and the `n_scaleup_bars_in_block` /
`frac_quality_low_in_block` columns are pricing-invariant and trustworthy as-is — but the two
`$_window_delta` columns carry legacy fill economics, not genuine-MNQ fill economics. This is
flagged as a minor known limitation of this specific reused table, not silently presented as
genuine-MNQ truth.

| Block set | n | Total CONTROL window $ | F0.5 total delta | F0.7 total delta |
|---|---:|---:|---:|---:|
| Top-20 winners | 20 | $194,687.05 | $0.00 | $0.00 |
| Bottom-20 losers | 20 | -$61,275.40 | -$34.50 | -$34.50 |

---

## 10. Winner retention

Same source files as §9. Per-block improved/damaged/unchanged counts (threshold ±$1 to absorb
floating-point noise):

| Block set | Candidate | Improved (>+$1) | Damaged (<-$1) | Unchanged (±$1) |
|---|---|---:|---:|---:|
| Top-20 winners | F0.5 | 0 | 0 | **20/20** |
| Top-20 winners | F0.7 | 0 | 0 | **20/20** |
| Bottom-20 losers | F0.5 | 1 | 2 | 17/20 |
| Bottom-20 losers | F0.7 | 1 | 2 | 17/20 |

**FACT:** the incumbent's own top-20 all-time blocks are **preserved bit-for-bit** ($0.00 total
delta, 20/20 unchanged) under both grid cells — the asymmetric, never-block-a-scale-up design
works exactly as intended on the campaign's own right-tail benchmark. Bottom-20 losers show a
trivial ($34.50 total, under legacy pricing) net *worsening*, not protective — 2 of 20 blocks
damaged, 1 improved, 17 unchanged. Directionally the wrong sign for a "risk mechanism," but
immaterial in dollars either way.

---

## 11. Current-regime behavior (2026 evidence vs. full-history pattern)

Source: `forward_readiness/out/11_current_regime_comparison.csv`, built from §1/§2/§3 above.

| Candidate | Full-hist canonical delta | 2022-2025 delta | 2026 Jan-May (canonical) delta | 2026 Jun-Jul (extension) delta | Sign-consistent? |
|---|---:|---:|---:|---:|:---:|
| F0.5 | +$301.30 | +$859.20 | **-$557.90** | +$148.80 | **No** |
| F0.7 | +$377.90 | +$983.60 | **-$368.70** | +$231.30 | **No** |

**FACT, given high interpretive weight per sec32:** the most recent canonical-window evidence
(2026 Jan-May) is **negative** for both F0.5 and F0.7 — the rate limiter cost money relative to
CONTROL in the most recent complete data before the health-only extension. The subsequent
health-only extension (Jun-Jul) swings back positive for both, partially offsetting the Jan-May
dip, but per this campaign's own standing rule that extension figure is observational only and
carries no promotion weight.

**INFERENCE, explicitly separated from the fact above:** this is exactly the pattern the original
`REPORT.md` already flagged as this candidate's most distinctive (and most reassuring)
chronology signature relative to prior entry-timing families in this campaign — R2V1/R2B's
"100% of headline was a 2026-stub artifact" pattern would require *positive* 2026 evidence
propping up an otherwise-weak history; here it is the reverse (2022-2025 carries the edge, 2026
Jan-May is a genuine drag). That remains true and is *reconfirmed*, not newly discovered, by this
panel. **Per sec32's other clause, a good recent stretch (the Jun-Jul extension) does not, by
itself, justify anything** — and here there isn't even a good recent stretch to over-read: Jan-May
was bad, Jun-Jul recovered, net effect on the standing verdict is nil. Current-regime evidence is
**neither clearly consistent with nor clearly contradicting** the full-history pattern; it is
noisy in a way fully consistent with an effect this small (sub-1%) and this panel's own wide
confidence intervals throughout §1-§8.

---

## Bonus section: owner-utility forward objective (PO2 — reused infrastructure)

Per the shared task context, `src/analytics/primary_objective_v2.py` (PO2) and its
`leverage_curve` helper are reused directly (not reimplemented), calling convention identical to
`runs/O2_OWNER_UTILITY_READJUDICATION/src/01_dry_run_and_score.py`. This is itself an
uncertainty-aware forward statistic — J/CE_g/P_ruin are mixture-of-bootstrap-method quantities by
construction, and PO2 natively flags when its own bootstrap methods disagree in sign
(`model_determined_sign`). Run on the canonical-window genuine-MNQ series, C=$100,000, L=1.0
fixed_fraction (O2's own headline convention). Outputs: `forward_readiness/out/12_po2_owner_utility.csv`,
`12b_po2_leverage_curve.csv`, and one full raw JSON per candidate (`po2_<candidate>_full_result.json`).

| Candidate | J (mixture) | J (Gamma-minimax / worst-of-3) | CE_g (ann.) | P_ruin (mixture) | Model-determined sign? |
|---|---:|---:|---:|---:|:---:|
| CONTROL | 0.0594 | -0.2146 | 0.3051/yr | 0.1797 | **Yes** |
| F0.5 | 0.0620 | -0.2007 | 0.3063/yr | 0.1787 | **Yes** |
| F0.7 | 0.0621 | -0.2079 | 0.3065/yr | 0.1787 | **Yes** |

**FACT (uncertainty disclosure, not a defect of this candidate specifically):** at the O2 headline
leverage (L=1.0), the objective's sign is **model-determined** for all three candidates
identically — the equal-weight mixture reads positive (~+0.06) while the worst-of-three-methods
(Gamma-minimax) reading is negative (~-0.20 to -0.21). Per PO2's own design, this must not be
quoted as a single number; it means "is Product-A's forward owner-utility positive at L=1.0"
itself does not have a single answer, independent of whether the rate limiter is applied.

**Leverage-curve shape (`12b_po2_leverage_curve.csv`, default grid L ∈ {0, 0.25, ..., 3.0}):** for
all three candidates, `model_determined_sign` is **False** (unambiguous) at L ≤ 0.75 (J positive,
peaking near L=0.75 at J≈0.19) and again False (unambiguously negative) at L ≥ 1.5; the ambiguous
band is L ∈ [1.0, 1.25] for all three candidates alike. **This shape is qualitatively identical
across CONTROL/F0.5/F0.7** — the rate limiter does not change *where* the owner-utility sign
becomes ambiguous, it only nudges the point values by fractions of a percent, consistent with
every other cut in this panel.

---

## Synthesis — what this panel changes and what it doesn't

**Does not change:** U6B's promotion disposition. This was never this panel's remit (item-by-item
brief above is diagnostic), and nothing found here would have overturned it even if reopened —
§1's Sharpe CIs don't separate the three candidates, §6's LOYO cells flip sign when the single
best year (2025) is removed, §11's most-recent canonical evidence is negative not positive, and
even PO2's owner-utility read is sign-ambiguous at deployment leverage for CONTROL exactly as much
as for F0.5/F0.7. Every new cut this panel adds points the same direction as the original
construction report: real, correctly-signed on balance, right-tail-safe by design (§9-10), but too
small to be distinguishable from noise once uncertainty is made explicit.

**Does change:** the *evidentiary standard* available for any future reader. Before this panel,
"F0.5 net is $301.30 higher than CONTROL over the full history" stood alone. Now that number sits
next to: a Sharpe CI wide enough to swallow the difference (§1), a LOYO decomposition showing the
edge is concentrated in one year (§6), a rolling-window distribution showing normal 20-60-session
swings dwarf the effect size by 1-2 orders of magnitude (§7-8), and an owner-utility read that is
itself sign-ambiguous at the deployment leverage regardless of which candidate is used (bonus
section). None of this is a new red flag — it is the uncertainty that was always latent in a
sub-1% effect, now made explicit rather than implicit.

---

## File manifest

All under `runs/U6B_PRODUCT_A_SCALE_RATE/forward_readiness/`:

- `src/01_build_panel.py` — single script, builds every section above; reproduce command at top of this report.
- `out/00_consolidated_panel.json` — single-file rollup of sections 1,2,3,6,9-10,11, and the PO2 bonus section.
- `out/01_full_history_canonical.csv` — §1
- `out/02_2022_2025_only.csv` — §2
- `out/03_2026_consumed.csv` — §3
- `out/04_year_by_year_reused.csv` (reused verbatim) + `04_year_by_year_bootstrap_ci.csv` (new) — §4
- `out/05_quarter_by_quarter.csv` — §5
- `out/06_loyo_delta_vs_control.csv` — §6
- `out/07_rolling_window_distributions.csv`, `07b_rolling_series_w60.csv`, `07b_rolling_series_w252.csv` — §7
- `out/08_worst_rolling_windows.csv` — §8
- `out/09_10_tail_concentration_winner_retention.csv` — §9-10 (reads from `../out/u6b_righttail_{top20_winners,bottom20_losers}.csv`, both LEGACY-priced, reused not rebuilt)
- `out/11_current_regime_comparison.csv` — §11
- `out/12_po2_owner_utility.csv`, `12b_po2_leverage_curve.csv`, `po2_{CONTROL,F0.5,F0.7}_full_result.json` — bonus PO2 section
- `out/run_log.txt` — full stdout of the reproduce command

Upstream artifacts read (not modified): `runs/U6B_PRODUCT_A_SCALE_RATE/out/{CONTROL,F0.5,F0.7}_daily_GENUINE_MNQ.csv`,
`u6b_mnq_year_by_year.csv`, `u6b_mnq_repricing_recon.json`, `u6b_righttail_top20_winners.csv`,
`u6b_righttail_bottom20_losers.csv`; `src/analytics/smv2_common.py` (`dd_battery`);
`src/analytics/primary_objective_v2.py` (`primary_objective`, `leverage_curve`).
