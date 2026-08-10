# W5_PROTECTED_CONFIRMATION — Consolidated Report

**One-shot confirmation-pool run, all 3 families, executed to completion before any
interpretation.** Pool opened: 8 sessions (`20250819, 20250912, 20251028, 20251125, 20260217,
20260302, 20260422, 20260512`) from the AMENDMENT_3 protected pool. All frozen bundle files
verified byte-unchanged against `SPEC_HASHES.md` before use (all 16 hashes matched exactly).
Governance assertions (8-date whitelist only, no session outside the 8, no data ≥2026-08-01) are
baked into every driver script and passed at runtime — verified in logs, not just claimed.

Scripts: `runs/W5_PROTECTED_CONFIRMATION/results/src/00-07_*.py` (8 scripts). Outputs:
`runs/W5_PROTECTED_CONFIRMATION/results/out/*` (parquet/CSV/JSON + one log per stage).

## Correctness gates (all PASSED before any confirmation statistic was trusted)

- Product-A legacy canonical net = **$177,924.40** (certified) — reproduced exactly in scripts 03,
  06, 07 (bar-for-bar position match against `u0_state_table.parquet` also confirmed in script 06).
- Product-B NQ canonical net = **$301,915.92** (certified) — reproduced exactly in scripts 03 and
  07.
- `VOTE_THRESH` reproduced = **6.000000** (script 05), `CUT_FAR_TICKS` used verbatim =
  **315.3333333333333** (script 06) — neither recomputed.
- A data-limitation discovered *during* the build, not tuned around: **2 of the 8 sessions
  (20251125, 20260512) have ZERO Bid/Ask updates during RTH** — same failure mode AUCTION01's
  discovery pass documented for `20250902`. Correctly auto-excluded by the liquidity filter
  everywhere downstream, not adjusted for. **Effectively only 6 of 8 sessions contribute to every
  RTH-liquid diagnostic below.**

---

## Family 1 (PRIMARY) — AUCTION01 D4 diagnostic replication

Causal running-POC construction reused character-for-character, re-pointed at the 8 confirmation
sessions. 4,680 decision points survive RTH+liquid, but only across **6 sessions**. Session-block
bootstrap therefore resamples from **only 6 clusters** — very low resolution, noted honestly.

| predictor | outcome | confirm ρ | confirm 95% CI (n_sess=6) | discovery ρ | discovery CI | sign match | CI excl. 0? |
|---|---|---:|---|---:|---|:---:|:---:|
| poc_share | abs_markout_15 | −0.200 | [−0.325, 0.106] | −0.197 | [−0.274,−0.101] | yes | no |
| poc_share | range_15 | −0.339 | [−0.504, 0.240] | −0.350 | [−0.461,−0.194] | yes | no |
| poc_share | abs_markout_60 | −0.199 | [−0.325, 0.090] | −0.201 | [−0.275,−0.106] | yes | no |
| poc_share | range_60 | −0.350 | [−0.523, 0.212] | −0.353 | [−0.462,−0.193] | yes | no |
| poc_share | abs_markout_300 | −0.181 | [−0.305, 0.148] | −0.221 | [−0.302,−0.109] | yes | no |
| poc_share | range_300 | −0.351 | [−0.551, 0.210] | −0.367 | [−0.483,−0.202] | yes | no |
| \|value_dist\| | abs_markout_15 | +0.193 | [−0.031, 0.279] | +0.135 | [0.064,0.205] | yes | no |
| \|value_dist\| | range_15 | +0.347 | **[0.0015, 0.451]** | +0.229 | [0.101,0.332] | yes | **yes** |
| \|value_dist\| | abs_markout_60 | +0.205 | **[0.014, 0.279]** | +0.132 | [0.056,0.199] | yes | **yes** |
| \|value_dist\| | range_60 | +0.354 | [−0.055, 0.460] | +0.232 | [0.110,0.349] | yes | no |
| \|value_dist\| | abs_markout_300 | +0.166 | [−0.055, 0.258] | +0.138 | [0.046,0.220] | yes | no |
| \|value_dist\| | range_300 | +0.361 | [−0.027, 0.494] | +0.245 | [0.114,0.357] | yes | no |

**Sign replication: 12/12 (100%)** — every cell points the same direction as discovery, and every
point estimate clears the |ρ|≥0.10 economic-relevance floor (range 0.17–0.36). **CI-excludes-zero
replication: 2/12.** Per `MULTIPLE_TESTING_PLAN.md`'s frozen threshold (≥9=REPLICATED, 6–8=PARTIAL,
<6=NOT REPLICATED), this is **NOT REPLICATED**.

**Read honestly, not as evidence of absence.** A 6-cluster session-block bootstrap has almost no
resolving power by construction. The 100%-sign-consistency and point estimates sitting right in
the discovery pass's own 0.13–0.37 range are themselves informative and inconsistent with a null
effect — the formal "NOT REPLICATED" label here is a **power artifact of n=6 clusters**, not a
finding that the D4 relationship reversed or vanished.

---

## Family 2 (SECONDARY) — AUCTION02 frozen Product-A policy confirmation

### Step a — diagnostic replication (primary endpoints 1–2)

Product A: n=673 analysis_ok bars / 16 trades / 6 sessions. Product B: n=522 / 7 trades / 5
sessions.

| endpoint | product | confirm point est. | confirm CI (sess / trade) | discovery point est. | discovery CI (sess / trade) | sign | stat-sig replicated | econ-relevance |
|---|---|---:|---|---:|---|:---:|:---:|---|
| H=3 signed_markout ρ | A | −0.058 | [−0.177,0.028] / [−0.172,0.060] | −0.054 | [−0.104,−0.011] / [−0.106,−0.009] | match | **NO** | modest but n-limited |
| P(large aligned), far−near | A | +0.123 | [−0.137,0.260] / [−0.154,0.263] | +0.116 | [0.018,0.217] / [0.024,0.206] | match | NO | — |
| P(large adverse), far−near | A | +0.292 | **[0.146,0.371] / [0.140,0.389]** | +0.198 | [0.097,0.300] / [0.100,0.288] | match | **YES** | large, both dual-CI |
| P(large aligned), far−near | B | +0.144 | [−0.189,0.307] / [−0.147,0.326] | +0.157 | [0.036,0.262] / [0.050,0.261] | match | NO | — |
| P(large adverse), far−near | B | +0.316 | **[0.171,0.633] / [0.225,0.624]** | +0.223 | [0.118,0.320] / [0.126,0.320] | match | **YES** | large, both dual-CI |

Primary endpoint (1) (Product-A H=3 signed_markout) does **not** clear the dual-CI bar on
confirmation (sign matches, CI too wide at n=673 vs discovery's n=4,374). Primary endpoint (2)
**partially replicates cleanly**: the "large adverse move" cell, for **both** products, clears
both session- and trade-block CIs with the same sign and even a larger point estimate than
discovery — this is the strongest surviving evidence in the whole bundle. The "large aligned
move" side does not clear (wide CI, matches sign only).

### Step b — redundancy replication (primary endpoint 3)

n=22 scale-up analysis_ok bars (13 trades, 6 sessions). `abs_value_dist_ticks` vs
`quality_high_u6b`: ρ=**−0.168** (p=0.456) vs discovery's −0.069. **|ρ|<0.2 holds on
confirmation** (well under the falsification threshold of ≥0.4) — non-redundancy replicates.

### Step c — coverage-restricted constructed P&L delta (primary endpoint 4)

Full-history simulator rebuilt byte-identical-in-shape to U6B's `product_a_exec_ratelimited`,
trigger swapped to `quality_low_auction` (domain-gated, `CUT_FAR_TICKS` reused verbatim). Only
**780 bars** across the whole ~540k-bar history fall in the RTH+liquid confirmation-pool domain;
only **23 in-domain scale-up bars** ever see the trigger evaluated; the rate limiter actually
*fires* on **19 (F0.5) / 18 (F0.7)** of those.

| candidate | net over 8 tick-covered dates | Δ vs CONTROL | 1%-wash threshold | contracts Δ | commission Δ |
|---|---:|---:|---:|---:|---:|
| CONTROL | −$6,151.10 | — | — | — | — |
| F0.5 | −$6,179.30 | **−$28.20** | $61.51 | −2 | −$1.30 |
| F0.7 | −$6,234.60 | **−$83.50** | $61.51 | 0 | $0.00 |

Both grid cells show a **negative** delta → **falsification condition (a) triggers on both
cells.** (Descriptive Sharpe/maxDD were also computed on the 8-day series — not meaningful
statistics on an 8-observation series, reported only for completeness.)

### Step d — right-tail check

Non-trivial intersection found (not the expected N/A): **2 of U6's own bottom-20 canonical loser
blocks** start on confirmation-pool dates — block 7234 (2025-11-25, U6-published net −$4,934.45)
and block 7709 (2026-02-17, −$2,741.80). Zero top-20 blocks intersect.

| block | date | CONTROL window pnl | F0.5 Δ | F0.7 Δ |
|---|---|---:|---:|---:|
| 7234 | 2025-11-25 | −$4,934.45 | $0.00 | $0.00 |
| 7709 | 2026-02-17 | −$2,741.80 | +$93.80 | −$45.50 |

The rate limiter never engages inside block 7234's window at all. F0.7 shows −$45.50 of
*additional* damage on block 7709.

### Falsification condition (e) — cut-point transport check

`quality_low_auction` realized rate on the pool = **60.9% (14/23)** vs discovery's 33.3%
tercile-construction rate. The 2× band is [16.7%, 66.7%] — 60.9% sits **inside** the band, so (e)
does **not** trigger, though it sits close to the upper edge on n=23.

### Family 2 verdict

Per `spec.yaml`'s own mechanical falsification_condition (OR of 5), **condition (a) is
unambiguously triggered on both grid cells** → **NOT_PROMOTED**.

**This verdict must be read with its statistical weight, not just its label.** The entire step-c
dollar swing (−$28 to −$84) is produced by a rate limiter that fired on fewer than 20 bars across
3 of 8 sessions, against a backdrop of −$6,151 in CONTROL losses over those same 8 days (largely
driven by one bad session, 2025-11-25, that the rate limiter never even touches). This is close to
the smallest sample on which this falsification rule could possibly be evaluated at all.
NOT_PROMOTED is the literal, correctly-computed output of the frozen rule, explicitly flagged as
**low-confidence / fragile** rather than a confident rejection of the underlying construction.

---

## Family 3 (OPTIONAL) — FLOW01 PRE_EXIT confirmation

8-session checkpoint substrate: 1,448 in-position checkpoints, 1,436 HOLD, **12 PRE_EXIT**
checkpoints (12 distinct trades, 7 distinct sessions).

| feature | horizon | ρ | session CI (n=7) | trade CI (n=12) | both excl. 0? |
|---|---|---:|---|---|:---:|
| avg_spread_ticks_60s | fwd1_pnl | +0.743 | [0.499, 0.885] | [0.223, 0.927] | **YES** |
| avg_spread_ticks_60s | fwd3_pnl | +0.743 | [0.467, 0.890] | [0.302, 0.921] | **YES** |
| ret1s_vol_60s | fwd1_pnl | +0.448 | [−0.040, 0.827] | [−0.280, 0.853] | no |
| quote_intensity_60s | fwd1_pnl | +0.306 | [−0.289, 0.770] | [−0.397, 0.818] | no |
| signed_flow_aligned_60s | fwd1_pnl | +0.117 | [−0.378, 0.844] | [−0.495, 0.848] | no |
| flow_persistence_60s | fwd1_pnl | +0.074 | [−0.534, 0.525] | [−0.507, 0.608] | no |
| (remaining 4 cells: ×fwd3_pnl) | | | | | no |

**2 of 10 cells clear the dual-CI-excludes-zero bar** — both are the *same feature*
(`avg_spread_ticks_60s`) at two overlapping/highly-correlated horizons, not two independent
confirmations. Per `MULTIPLE_TESTING_PLAN.md`'s explicit rule, **1–2 clearing cells =
`PROBABLE_MULTIPLE_TESTING_ARTIFACT, NOT A FINDING`**. A supplementary ΔR² check produced
ΔR²=+0.34 to +0.35 — far above the 0.002 floor, but not meaningful at n=12 with a 2-parameter fit
(df=9); such huge ΔR² at this sample size is itself diagnostic of overfitting, reported as
uninformative.

**Family 3 verdict: PROBABLE_MULTIPLE_TESTING_ARTIFACT, NOT A FINDING** — consistent with
discovery's own clean 0/10 null.

---

## Multiplicity across the bundle

26 total cells as planned. No formal Bonferroni/FDR correction applied, per this campaign's
standing convention. Pattern across all three families: **sign consistency is strong everywhere**
(12/12 in Family 1, matching sign in all of Family 2's endpoints), but **CI-excludes-zero
replication is weak almost everywhere** except the two "large adverse move" cells in Family 2 and
the two collinear cells in Family 3 — the shape expected from a real-but-modest underlying effect
tested on a sample an order of magnitude smaller than the plan implicitly assumed.

## INTERNAL PROTECTED CONFIRMATION vs CHRONOLOGICAL/PREQUENTIAL EVIDENCE

This result is **INTERNAL PROTECTED CONFIRMATION only, and explicitly not chronological/forward
evidence.** Discovery sessions span `20250814`–`20260520`. **All 8 confirmation dates fall inside
that same span** — `20250819` sits five days after discovery's earliest date, `20260512` sits
eight days before discovery's latest date, and the other six are interleaved throughout. None of
these 8 sessions are chronologically "after" the discovery set; they were withheld by sampling
design, not by time-ordering. Nothing here should be read as "the strategy held up on new, later
data" — it should be read strictly as "the same construction, applied to a same-era sample that
was never inspected while the construction was designed."

## Pool consumption

Per `FAILURE_RULES.md`, this 8-session slice of the protected pool is now **consumed** for these
three specific constructions (AUCTION01 D4, AUCTION02 Product-A policy, FLOW01 PRE_EXIT)
regardless of the outcomes above. No parameter was adjusted based on any result seen. The
remaining ~160 sessions of the 168-session pool remain untouched and unopened; no session outside
the 8, and no data ≥2026-08-01, was read at any point.

## Files

- Scripts: `runs/W5_PROTECTED_CONFIRMATION/results/src/00_build_sechilo_confirmation.py` through
  `07_flow01_pre_exit_confirmation.py`
- Logs: `runs/W5_PROTECTED_CONFIRMATION/results/out/00_sechilo_log.txt` … `07_flow01_log.txt`
- Data: `poc_1s_full_CONFIRM.parquet`, `decision_points_30s_CONFIRM.parquet`,
  `decision_outcomes_CONFIRM.parquet`, `diagnostics_summary_CONFIRM.json` (Family 1);
  `action_substrate_CONFIRM.parquet`, `step1_results_CONFIRM.json`,
  `step2_redundancy_results_CONFIRM.json`, `step_c_d_summary_CONFIRM.json`,
  `step_c_per_session_CONFIRM.csv`, `step_d_righttail_CONFIRM.csv` (Family 2);
  `checkpoint_features_CONFIRM.csv`, `build_sanity_CONFIRM.json`,
  `flow01_analysis_summary_CONFIRM.json` (Family 3)
- New sechilo cache (8 files only):
  `research/scalping_lab/substrate/sechilo/NQ/s{20250819,20250912,20251028,20251125,20260217,20260302,20260422,20260512}.parquet`
