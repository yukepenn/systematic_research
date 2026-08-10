# AUCTION02_ACTION_RELEVANCE — action-relevance of AUCTION state on the incumbent's already-chosen direction: ONE frozen Product-A speed mapping (primary f=0.5 / sensitivity f=0.7), Product-B and both Step-4 combination candidates NOT frozen

**Disposition: FROZEN_POLICY_SPEC (Product-A only), awaiting a later, separate confirmation-pool
test.** Step 1 found a real, small, causally clean, non-time-of-day-confounded, sign-stable
SIGNED relationship between the causal running-POC distance (`value_dist_ticks`) and the forward
quality of the incumbent's own already-chosen direction. Step 2 showed this is genuinely
non-redundant with U6B's own frozen quality state and adds real incremental information. Step 4
found no evidence for either of two a priori combination candidates. Step 3 explicitly declines to
build a Product-B construction (a valid, complete outcome per the task's own instruction). This is
**not** a strong finding — the effect size is comparable to or smaller than U6B's own effect,
which itself failed U6B's promotion bar — but it is real enough, and non-redundant enough, to
freeze a conservative, U6B-style candidate for a fair confirmation-pool test.

Spec: `runs/AUCTION02_ACTION_RELEVANCE/spec.yaml` (frozen before any confirmation-pool contact).
Code: `runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py` (build),
`02_step1_diagnostics.py` (Step 1), `03_step2_redundancy_check.py` (Step 2),
`04_step4_combination_sandbox.py` (Step 4), `stats_lib_auction02.py` (shared
bucket-residualization/Δ R² + dual-clustered-bootstrap library, adapted from
`U8_PATH_ORGANIZATION/src/stats_lib.py`). Outputs: `out/action_substrate.parquet` (13,064
in-direction rows, 37 sessions), `out/step1_results.json`, `out/step2_redundancy_results.json`,
`out/step4_results.json`, plus `*_log.txt` run logs for each stage.

## Governance confirmation (read first)

Only two files were read: `runs/U0_UNIFIED_STATE/out/u0_state_table.parquet` (read-only;
correctness-gated by reproducing the certified canonical Product-A net $177,924.40 and Product
B-NQ net $301,915.92 exactly before trusting any other column) and
`runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet` (an already-built, already-reported,
discovery-only derivative of `raw/NQ`). No script in this family opens `raw/NQ`, `grid1s/NQ`, or
`sechilo/NQ` directly except to read `sechilo/NQ`'s own file *list* (not contents) as a sanity
check that the 37-session universe matches AUCTION01's. **The ~168-session AMENDMENT_3 protected
confirmation pool was never read, requested, enumerated, or examined.** Session tags used range
`20250814`..`20260520`, entirely inside the canonical window, far short of the `2026-08-01` sealed
boundary (verified by assertion in the build script that `is_health_only_bar` is `False`
throughout this substrate).

## Data construction

`01_build_action_substrate.py` takes U0's own 3-minute bar grid, restricted to the 37 BBO-confirmed
sessions, filtered to bars where the incumbent already has a nonzero direction
(`position_B != 0` OR `target_exposure_A != 0`) — 13,064 such bars. For horizons H ∈ {1, 3, 20}
bars (matching this campaign's `fwd1_pnl`/`fwd3_pnl`-style forward-markout convention, extended to
a longer 20-bar/60-minute look), it computes, fully vectorized (no lookahead, session-boundary-safe,
NaN if the forward window would cross a session close):

- `signed_markout_H` = `sign(direction) * (close[t+H] - close[t]) / TICK`
- `mfe_H` / `mae_H` = side-adjusted maximum favorable / adverse excursion over `close[t+1..t+H]`'s
  high/low range, in ticks (identical convention to AUCTION01's own D6 diagnostic)
- `fwd_pnl_H` = sum of the incumbent's own certified `bar_pnl_{A,B}_dollars` over the same window
  (FLOW01/COMBO01's own convention, kept as a cross-check, not used as a primary endpoint here)

`value_dist_ticks` / `poc_share` are then merged on via `pandas.merge_asof(direction='backward',
by=session, tolerance=2s)` from `poc_1s_full.parquet` — identical mechanics to
`COMBO01_MULTIMODAL_SYNERGY/src/01_build_merged_substrate.py`. Match rate 99.75%. The analysis
universe is further restricted to RTH `[09:30,16:00)` ET **and** a reconstructed
trailing-60s(bid_upd+ask_upd)>0 liquidity gate (same construction as COMBO01), because AUCTION01's
own value-state finding was only confound-checked inside that exact domain — this is the same
disclosed, material restriction COMBO01 used (33.5% of in-direction bars survive: **n=4,374**
Product-A bars / 89 trades / 36 sessions; **n=2,786** Product-B bars / 47 trades / 31 sessions —
the Product-B count reproduces COMBO01's own HOLD-group-plus-ENTRY total almost exactly, a good
independent sanity check).

## Step 1 — action-relevance diagnostics

**Preregistered tercile cuts** (computed once from each product's own analysis-ok marginal
distribution, before any outcome was touched): Product A `|value_dist_ticks|` tercile =
[104.0, 282.33] ticks, `poc_share` tercile = [0.002618, 0.004032]; Product B `|value_dist_ticks|`
tercile = [107.0, 291.0] ticks, `poc_share` tercile = [0.002526, 0.003630].

**Bucket-residualization + Δ R² methodology** (`stats_lib_auction02.py`, adapted from this
campaign's own U8/R4/R5/EXP01/VAR01 shared framework — bucket on `|M|` tercile × `sigma460`
tercile, compare raw vs bucket-residualized Spearman ρ, and OLS baseline vs extended Δ R²). Because
this substrate spans ~9 months of sessions rather than multiple calendar years, "year-by-year sign
stability" is replaced by a first-half/second-half chronological session split (H1:
`20250814`–`20260123`, H2: `20260206`–`20260520`, 18 sessions each) — the same adaptation
AUCTION01's own D4 diagnostic already made on this identical substrate.

### Headline: signed continuation of the incumbent's own direction

| product | H (bars) | raw ρ | resid ρ | Δ R² | half-stable | session-block CI | trade-block CI | both exclude 0? |
|---|---:|---:|---:|---:|---:|---|---|---|
| A | 1 | −0.029 | −0.021 | +0.0019 | 2/2 | [−0.064, 0.006] | [−0.058, 0.001] | no |
| A | 3 | **−0.054** | −0.040 | +0.0058 | 2/2 | **[−0.104, −0.011]** | **[−0.106, −0.009]** | **YES** |
| A | 20 | −0.085 | −0.041 | +0.0193 | 2/2 | [−0.198, 0.015] | [−0.183, 0.002] | no |
| B | 1 | −0.029 | −0.032 | +0.0023 | 2/2 | [−0.069, 0.007] | [−0.071, 0.007] | no |
| B | 3 | −0.054 | −0.063 | +0.0074 | 2/2 | [−0.113, 0.007] | [−0.122, 0.003] | no |
| B | 20 | −0.091 | −0.108 | +0.0244 | 2/2 | [−0.213, 0.017] | [−0.204, 0.007] | no |

Sign is **negative and consistent at every horizon, for both products, both chronological halves**
— being far from the running POC predicts a *worse* forward markout in the direction the
incumbent has already committed to (a mean-reversion-flavored finding, the opposite of a naive
"value migration confirms direction" story, but consistent with AUCTION01's own framing of
`value_dist` as an *expansion*, not a directional-edge, signal). Only Product A at H=3 clears this
lineage's own strict "both session-block AND trade-block CI exclude zero" bar (the exact standard
COMBO01 itself used). Product B never quite clears it at any single horizon (closest at H=3,
trade-block upper bound +0.003) — smaller sample (fewer, longer-held trades) is the likely reason,
not a sign disagreement.

`mae_H` shows a much larger *raw* correlation (+0.15 to +0.24) that collapses substantially after
bucket-residualization (+0.01 to +0.09 for A, +0.09 to +0.16 for B) — most of the raw MAE
relationship is going through the `|M|`/volatility confound, not a clean directional signal, exactly
the caution AUCTION01's own D4 already flagged. `mfe_H` residualized correlations are small and not
half-stable (1/2 or 0/2) — not treated as informative.

### Large-move probabilities (H=3, `value_dist_ticks` far vs near tercile)

| product | indicator | P(far) | P(near) | diff | session CI | trade CI | both exclude 0? |
|---|---|---:|---:|---:|---|---|---|
| A | P(large aligned move) | 0.567 | 0.451 | +0.116 | [0.018, 0.217] | [0.024, 0.206] | **YES** |
| A | P(large adverse move) | 0.605 | 0.406 | +0.198 | [0.097, 0.300] | [0.100, 0.288] | **YES** |
| B | P(large aligned move) | 0.595 | 0.438 | +0.157 | [0.036, 0.262] | [0.050, 0.261] | **YES** |
| B | P(large adverse move) | 0.614 | 0.391 | +0.223 | [0.118, 0.320] | [0.126, 0.320] | **YES** |

("Large" = exceeding the pooled median MFE/MAE at that horizon within each product's own
in-direction population, computed once before any bucket split — A: 61.0/61.0 ticks, B: 68.0/67.0
ticks.) **All four cells clear the dual-CI-excludes-zero bar, for both products.** Far-from-value
predicts a bigger move happening in general (echoing AUCTION01's original absolute-expansion
finding), with the *adverse*-move-probability increase consistently larger than the
aligned-move-probability increase — directionally consistent with the negative `signed_markout`
finding above.

### Too-good-to-be-true confound checks (matching AUCTION01/COMBO01 precedent)

`value_dist_ticks_abs` vs `sigma460_atr_proxy_pts`: ρ=+0.304 (A) / +0.279 (B) — modest, and the
signed-markout relationship *survives* bucket-residualization on this exact variable, so it is not
explaining the effect away. vs `minutes_since_session_open`: ρ=+0.010 (A) / −0.035 (B) —
negligible, confirms this is not a time-of-day artifact. `poc_share` vs `sigma460`: ρ=−0.736 (A) /
−0.737 (B) — **reproduces COMBO01's ρ=−0.705 finding almost exactly** on this independently
constructed sample, reinforcing that `poc_share` must stay secondary/sensitivity-only, never
primary (consistent with AUCTION01/COMBO01's own conclusion).

### Concentration check

Far-tercile bucket: Product A 64 trades / 32 sessions, top-4-session-share 25.4%, top-4-trade-share
23.5%; Product B 39 trades / 28 sessions, top-4-session-share 32.8%, top-4-trade-share 29.6%. Near
bucket comparable (22.5–34.2%). No small-n concentration artifact (comparable to COMBO01's own
32–34% "clean" benchmark).

## Step 2 — redundancy vs U6B's own quality state (not tuning U6B)

`VOTE_THRESH` was **reproduced exactly** (=6.0, on the full canonical ENTRY+SCALE_IN population,
n=11,620 — byte-identical to U6B's own reported constant; asserted in code). At Product-A scale-up
bars (`action_A` ∈ {ENTRY, SCALE_IN}) within the RTH+liquid+matched domain: **346** such bars exist
in the 37-session in-direction universe, **171** survive the RTH+liquid+matched filter (55 trades,
33 sessions) — `quality_high_u6b` rate on this subset is 81.3% (vs U6B's own full-population 70.4%;
different composition, not alarming, disclosed).

**Redundancy:** `abs_value_dist_ticks` vs `quality_high_u6b` (binary): ρ=−0.069 (p=0.37, not
significant). vs `vote_dispersion_aligned` (continuous): ρ=+0.233. `poc_share` vs
`quality_high_u6b`: ρ=+0.146 (p=0.056, borderline). **Auction state is essentially uncorrelated
with U6B's own quality state at scale-up bars — not redundant.**

**Incremental value** (OLS: `signed_markout_H` ~ `quality_high_u6b` alone vs +
`abs_value_dist_ticks`):

| H | R²(quality only) | R²(quality+auction) | Δ R²(auction\|quality) | Δ R²(quality\|auction) | auction coef | session-block CI |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.0044 | 0.0045 | +0.0001 | +0.0045 | −0.003 | [−0.073, 0.044] |
| 3 | 0.0103 | 0.0118 | +0.0014 | +0.0092 | +0.018 | [−0.055, 0.108] |
| 20 | 0.0088 | **0.0841** | **+0.0753** | +0.0167 | **−0.337** | **[−0.586, −0.111]** |

At the 20-bar horizon, Auction state adds substantial, statistically real incremental information
beyond U6B's own quality signal (n=171 only — a real but small-sample result, flagged
transparently). At shorter horizons the incremental contribution is small but directionally
present in both directions (each signal adds something on top of the other), consistent with two
genuinely distinct, complementary information sources rather than one subsuming the other.

## Step 4 — combination-discovery sandbox (2 candidates only, simple linear interaction)

Per sec17, restricted to states already marked `reusable_as_state`/`reusable_for_interaction` ∈
{YES, MAYBE} in `research/system_master/STATE_INFORMATION_LIBRARY.csv`. Two a priori,
economically-motivated 2-way candidates were tested (OLS interaction term `b3` + Δ R², session-block
bootstrap, matching COMBO01's own methodology — no 3-way attempted, no black-box search):

| candidate | cell | n | Δ R² | b3 | session-block CI | excludes 0? |
|---|---|---:|---:|---:|---|---|
| Auction-far × U6B-quality-low (Product-A scale-up bars) | H=3 | 171 | +0.0067 | −59.3 | [−163.4, 49.0] | no |
| Auction-far × U6B-quality-low | H=20 | 171 | +0.0118 | +203.1 | [−204.2, 543.3] | no |
| Auction-far × \|M\|-strong (Product A, broader) | H=3 | 4,374 | +0.0001 | −5.2 | [−32.6, 21.4] | no |
| Auction-far × \|M\|-strong | H=20 | 4,348 | +0.0019 | +52.8 | [−37.8, 139.3] | no |
| Auction-far × \|M\|-strong (Product B, broader) | H=3 | 2,786 | +0.0010 | −17.2 | [−56.5, 14.3] | no |
| Auction-far × \|M\|-strong | H=20 | 2,786 | +0.0050 | −86.6 | [−194.6, 25.1] | no |

**Neither candidate clears the session-block-CI-excludes-zero bar in any cell.** Candidate 1
(n=171) is DATA_LIMITED, not a confident null — the point estimates swing widely with the sign
even flipping between H=3 and H=20, consistent with an under-resolved 4-parameter interaction model
on 171 rows. Candidate 2 (n=2,700–4,400) is closer to a genuine null (tighter CIs, smaller point
estimates). **Zero combination candidates are frozen this pass** — both are flagged as follow-ups
for a future pass with more data, not baked into the frozen spec.

## Step 3 — Product-B action layer (diagnostic only, EVI-selected)

The four candidate frames were: immediate-entry-vs-brief-wait, HOLD persistence, reversal caution,
re-entry timing. **"HOLD persistence" is the EVI-selected candidate** — it is literally what the
Step-1 Product-B test already is (2,757 of 2,786 analysis-ok Product-B bars are `action_B==HOLD`):
does being far from value while already holding a position predict worse continuation / a riskier
excursion profile? Evidence: the large-move-probability effect is clean (both P(large aligned) and
P(large adverse) dual-CIs exclude zero, diff pattern consistent with A), but the
`signed_markout`/continuation-value CIs never fully exclude zero at any single horizon (closest at
H=3, [−0.113, 0.007] session / [−0.122, 0.003] trade). Per Step 3's own explicit instruction,
**no Product-B construction is built this pass** — this is reported as the valid, complete outcome
it is, not forced. Auction remains Product-A-only in the frozen spec.

## Frozen construction (Product A only) — see `spec.yaml` for the complete, mechanical spec

Mirrors U6B's own rate-limiter mechanism exactly (`runs/U6B_PRODUCT_A_SCALE_RATE/spec.yaml`'s
construction discipline: never-block, minimum-step-of-1 floor, asymmetric to scale-up bars only,
never touches HOLD/EXIT/SCALE_DOWN/FLIP/FLAT), with the trigger swapped from
htf_agree/vote_dispersion to `value_dist_ticks`:

- **Bar selection:** identical to U6B — `is_scaleup = (tgt!=0) AND ((p==0) OR (sign(tgt)==sign(p)
  AND abs(tgt)>abs(p)))`.
- **Frozen cut point:** `CUT_FAR_TICKS = 315.3333` — the 67th-percentile tercile cutoff of
  `|value_dist_ticks|` on this discovery pass's own n=171 Product-A scale-up population, computed
  once, non-circularly, before any outcome was touched — must be reused verbatim on the
  confirmation pool, never re-derived (same discipline as U6B's `VOTE_THRESH=6.0`).
- **Quality state:** `quality_low_auction = (RTH+liquid domain) AND (|value_dist_ticks| >=
  CUT_FAR_TICKS)`; **FALSE by definition whenever the auction signal is unavailable** (outside
  RTH+liquid, or on any date without tick coverage — the overwhelming majority of Product A's
  history) — the mechanism never restricts when its own input doesn't exist.
- **Mechanism:** at a scale-up bar with `quality_low_auction==TRUE`: `gap = tgt - p`,
  `step_mag = max(1, floor(f * |gap|))`, `tgt_final = p + sign(gap)*step_mag`. Otherwise
  `tgt_final = tgt` unchanged.
- **Grid:** f ∈ {0.5 primary, 0.7 sensitivity} — identical to U6B's own grid, for direct
  comparability, not re-optimized. CONTROL (f=None) must reproduce the certified canonical
  Product-A net exactly as the correctness gate.

**Critical disclosed scope limitation:** `value_dist_ticks` requires genuine tick data, available
for only 37 (discovery) + up to ~168 (protected pool) sessions total. U6B's own report puts the
full-history scale-up-bar population at 12,085–12,603 bars; this discovery pass's tick-covered
scale-up population is 346 bars pre-filter (171 post-RTH/liquidity-filter) — roughly **2.8% of
all-time scale-up bars**, rising to a still-minority ~15% (rough extrapolation) once the protected
pool is added. A full-history net/Sharpe/DD battery in U6B's own style is **explicitly not
meaningful** here and is not part of the validation plan; `spec.yaml`'s `confirmation_procedure`
instead specifies a coverage-restricted constructed-P&L delta (summed only over tick-covered
dates) plus diagnostic-replication and redundancy-replication endpoints, with an exact,
preregistered falsification condition adapting U6B's own 1%-wash / right-tail / sign-flip /
redundancy-drift criteria to this coverage reality.

## What was tested and explicitly NOT frozen

- Product-B construction (Step 3) — diagnostic evidence suggestive but not clean enough; no
  Product-B mapping built.
- `poc_share` as a primary or standalone trigger — entangled with `sigma460` (ρ≈−0.74, both
  products, reproducing COMBO01); kept secondary/sensitivity-only.
- Both Step-4 combination candidates (Auction × U6B-quality; Auction × |M|-magnitude) — neither
  cleared the session-block-CI-excludes-zero bar; flagged as follow-ups, not frozen.

## Files

- `runs/AUCTION02_ACTION_RELEVANCE/spec.yaml` — the complete frozen policy spec for confirmation-pool testing
- `runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py` — causal merge of U0's incumbent-direction bars with AUCTION01's `value_dist_ticks`/`poc_share`, forward-markout construction (session-boundary-safe, vectorized)
- `runs/AUCTION02_ACTION_RELEVANCE/src/02_step1_diagnostics.py` — bucket-residualized Spearman/Δ R², dual-clustered bootstrap, large-move probabilities, confound/concentration checks
- `runs/AUCTION02_ACTION_RELEVANCE/src/03_step2_redundancy_check.py` — U6B `VOTE_THRESH` reproduction, redundancy correlation, incremental-R² test
- `runs/AUCTION02_ACTION_RELEVANCE/src/04_step4_combination_sandbox.py` — 2-candidate interaction sandbox
- `runs/AUCTION02_ACTION_RELEVANCE/src/stats_lib_auction02.py` — shared stats library (adapted from `U8_PATH_ORGANIZATION/src/stats_lib.py`)
- `runs/AUCTION02_ACTION_RELEVANCE/out/action_substrate.parquet`, `step1_results.json`,
  `step2_redundancy_results.json`, `step4_results.json`, `*_log.txt`
