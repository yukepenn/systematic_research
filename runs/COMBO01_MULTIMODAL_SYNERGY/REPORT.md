# COMBO01_MULTIMODAL_SYNERGY — AUCTION x FLOW preregistered interaction: NO LARGE EFFECT DETECTED (HOLD-group interaction is a well-powered clean null on both cut variables/both horizons/both statistical formulations; PRE_EXIT interaction data-limited)

**Disposition: NO_LARGE_EFFECT_DETECTED** (family-level, mirroring FLOW01's own precedent for
combining a clean null with a data-limited group). **HOLD group (primary, n=2,757 checkpoints /
47 trades / 31 sessions): CLEAN_NULL for the interaction specifically** — FLOW01's own
unconditional clean null on `signed_flow_aligned_60s` does **not** become a conditional signal
once split by AUCTION01's value-state (`|value_dist_ticks|` or `poc_share`). All 4 preregistered
HOLD cells, tested two ways each (OLS interaction coefficient `b3` and a rank-based near/far
bucket split), with dual (session-block + trade-block) clustered bootstrap, show CIs comfortably
spanning zero. A 3-bucket robustness variant (all rows, mid tercile included) agrees. **PRE_EXIT
group (secondary/exploratory, n=22-24 matched checkpoints): DATA_LIMITED**, as expected going in
— point estimates swing widely (one cell's `b3` point estimate is −4.0) but every CI is enormous
and crosses zero; not treated as evidence of absence, just as unresolved. No candidate, filter,
or trading policy is proposed — diagnostic only, per the addendum's own scope instruction and
this wave's standing practice.

Spec: `runs/COMBO01_MULTIMODAL_SYNERGY/spec.yaml` (frozen before results). Code:
`runs/COMBO01_MULTIMODAL_SYNERGY/src/01_build_merged_substrate.py`,
`runs/COMBO01_MULTIMODAL_SYNERGY/src/02_interaction_analysis.py`. Outputs:
`out/merged_checkpoints.csv` (6,221 rows, every FLOW01 checkpoint with matched AUCTION01
value-state + rth/liquid/matched flags), `out/build_summary.json`, `out/combo01_results.json`,
`out/build_log.txt`, `out/analysis_log.txt`.

## The interaction hypothesis (preregistered, frozen before any outcome-touching computation)

Per the addendum's own stated top-priority combination and its G1 principle (a modality may enter
COMBO01 even with a small standalone effect, provided it has a strong economic mechanism and
valid causal data): does aggressive same-direction order flow (`signed_flow_aligned_60s`, FLOW01's
tick-rule-classified signed flow aligned to the held position's side — unconditionally a CLEAN
NULL against forward markout in FLOW01's own HOLD-checkpoint test) carry **different** forward
information depending on where price sits relative to the session's running value area (AUCTION01's
`poc_share`/`|value_dist_ticks|` — a real, modest, confound-checked predictor of subsequent
absolute price expansion on its own)? The economic story: flow far from value may be more likely
genuinely information-driven / trend-extending, while the same flow near an already-balanced value
area may be closer to noise. The statistical test is symmetric — does the flow→outcome **slope**
differ by auction-state bucket — not a one-sided bet on which side wins.

## Merge / alignment method

**Source substrates.** `runs/FLOW01_AGGRESSIVE_PARTICIPATION/out/checkpoint_features.csv` (6,221
raw in-position checkpoints, 37-session universe) merged onto
`runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet` (3,027,377 rows, full-session 1-second causal
value-state layer, same 37 sessions) — `poc_1s_full` used in preference to the coarser,
RTH-only, liquidity-pre-filtered `decision_points_30s.parquet` because FLOW01's checkpoints are
3-minute-bar-aligned and span the full session (including pre-market/overnight), and because
`poc_1s_full` retains sessions (e.g. `20250902`) that `decision_points_30s` dropped for its own RTH
liquidity gate.

**Method.** `pandas.merge_asof(direction='backward', by='sess_tag', tolerance=2s)`, keyed on the
shared `time` column both parent families already established sit on the same ET session clock.
Strictly causal by construction: the matched `poc_share`/`value_dist_ticks` row's own timestamp is
always ≤ the FLOW01 checkpoint's timestamp, within the same session.

**Match rate: 6,188/6,221 (99.5%).** 33 checkpoints (0.5%) failed to find a match within the 2s
tolerance, confined to two sessions (`20251117`, `20260519`) that are otherwise fully present in
`poc_1s_full` — a small (<2s), structurally-expected grid-gap artifact, dropped rather than
imputed.

**Analysis-universe restriction (disclosed, material).** The merged sample is further restricted
to RTH `[09:30,16:00)` ET **and** a reconstructed trailing-60s(bid_upd+ask_upd)>0 liquidity gate
(computed directly from `poc_1s_full`'s own `bid_upd`/`ask_upd` columns, replicating AUCTION01's
own decision-point filter). This is necessary because AUCTION01's D4 finding — the
`poc_share`/`value_dist_ticks` → outcome relationship this whole interaction test leans on — was
only established and confound-checked inside that exact RTH+liquid domain; FLOW01's raw checkpoint
universe spans the full session, and extending value-state semantics to thinner-liquidity
pre-market/overnight periods would be an untested extrapolation. This is a real, disclosed sample
reduction, not a data-quality problem:

| group | raw checkpoints | raw trades | raw sessions | matched | matched & RTH | **matched & RTH & liquid (final)** | final trades | final sessions |
|---|---|---|---|---|---|---|---|---|
| HOLD | 6,158 | 63 | 33 | 6,125 | 2,829 | **2,757** | 47 | 31 |
| PRE_EXIT | 63 | 63 | 33 | 61 | 35 | **33** | 33 | 22 |

(HOLD retains 45% of its raw checkpoint count after the RTH+liquid gate; PRE_EXIT retains 52%.)

## Preregistered cut points (justified from the predictor's own marginal distribution, not the outcome)

Computed once, from the final HOLD/RTH/liquid analysis sample (n=2,757), **before** any
flow↔outcome relationship was inspected — tercile cuts at the 33rd/67th percentile of each
predictor's own marginal distribution:

| predictor | 33rd pct (near/low → mid) | 67th pct (mid → far/high) |
|---|---|---|
| `\|value_dist_ticks\|` | 106.0 ticks | 288.0 ticks |
| `poc_share` | 0.0025264 | 0.0036274 |

Tercile bucket sizes are near-exactly equal (≈918-920 checkpoints/bucket), 39-42 distinct trades
and 27-28 distinct sessions per bucket for `value_dist_ticks`, 24-28 trades / 19-24 sessions per
bucket for `poc_share`. Correlation between the two predictors in this sample: **ρ = −0.308**
(related, in the expected direction — larger distance from POC associates with lower local
concentration — but not redundant; both are kept as independently preregistered cuts).

`|value_dist_ticks|` was designated the **primary** cut variable (matches the addendum's own
"far from value area" framing, and AUCTION01 found it to be the *less* time-of-day-confounded of
the two predictors). `poc_share` is the **secondary/confirmatory** cut — see the sigma460 confound
finding below, which weakens its interpretability as an independent auction-state signal in this
specific analysis.

## Primary test — HOLD group (n=2,757 / 47 trades / 31 sessions)

Additive model `outcome ~ b0 + b1·flow + b2·bucket` vs. interaction model
`outcome ~ b0 + b1·flow + b2·bucket + b3·(flow·bucket)`, near-vs-far tercile contrast (mid
dropped for the primary cut), 1000-rep session-block (primary) and trade-block (secondary)
clustered bootstrap on both `b3` and the rank-based `rho_far − rho_near` split:

| cut variable | outcome | b3 (point) | session-block 95% CI | trade-block 95% CI | ΔR² (point) | rho_far−rho_near (point) | session-CI | trade-CI | signal? |
|---|---|---|---|---|---|---|---|---|---|
| `\|value_dist\|` tercile | fwd1_pnl | +0.052 | [−0.533, 0.651] | [−0.499, 0.712] | 0.0000143 | +0.011 | [−0.071, 0.093] | [−0.070, 0.096] | no |
| `\|value_dist\|` tercile | fwd3_pnl | +0.380 | [−0.906, 1.540] | [−0.706, 1.464] | 0.000285 | +0.011 | [−0.066, 0.102] | [−0.081, 0.109] | no |
| `poc_share` tercile | fwd1_pnl | +0.483 | [−0.088, 1.319] | [−0.044, 1.220] | 0.00159 | +0.060 | [−0.050, 0.159] | [−0.057, 0.171] | no |
| `poc_share` tercile | fwd3_pnl | +0.220 | [−0.432, 1.084] | [−0.588, 1.222] | 0.000125 | +0.012 | [−0.054, 0.068] | [−0.077, 0.097] | no |

**0 of 8 (4 cells × 2 statistics) session-block-AND-trade-block CI pairs exclude zero.** ΔR² point
estimates are all ≤0.0016 (i.e. the interaction term explains at most 0.16% of additional outcome
variance over the additive model) — not merely "not significant," numerically negligible. As an
internal consistency check, the OLS-interaction (`b3`) and rank-split (`rho_far−rho_near`)
formulations agree in direction and magnitude-of-nothing on every cell: no functional-form choice
rescues a signal here.

**3-bucket robustness variant** (all 2,757 HOLD rows, mid tercile included, bucket coded ordinally
0/1/2, linear-in-bucket interaction): all 4 cells again show `b3` CIs spanning zero on both
clustering schemes (session-block CIs e.g. `[−0.272,0.301]`, `[−0.394,0.677]`,
`[−0.048,0.609]`, `[−0.305,0.543]`). Consistent with the primary near-vs-far result — the tercile
contrast is not concealing a monotonic dose-response the ordinal model would pick up.

**For context — the unconditional (no interaction) relationship in this exact RTH+liquid HOLD
subsample:** Spearman ρ(flow, fwd1_pnl) = −0.022, ρ(flow, fwd3_pnl) = −0.007 — reproducing FLOW01's
own unconditional clean null (|ρ|≤0.015 on the full 6,125-checkpoint sample) inside this smaller,
RTH+liquid-restricted cut. The interaction test is not rescuing signal from a sample where the
main effect had somehow shifted.

## Secondary/exploratory test — PRE_EXIT group (n=22-24 / 17-22 sessions)

Preregistered as expected-underpowered going in (per spec.yaml), reported for completeness only,
per this campaign's DATA_LIMITED convention — a wide CI here is not evidence of absence:

| cut variable | outcome | n | b3 (point) | session-CI | trade-CI |
|---|---|---|---|---|---|
| `\|value_dist\|` tercile | fwd1_pnl | 22 | +0.0012 | [−0.174, 0.144] | [−0.195, 0.168] |
| `\|value_dist\|` tercile | fwd3_pnl | 22 | **−2.826** | [−9.036, 0.584] | [−11.26, 1.022] |
| `poc_share` tercile | fwd1_pnl | 24 | +0.042 | [−0.086, 0.605] | [−0.080, 0.310] |
| `poc_share` tercile | fwd3_pnl | 24 | **−4.013** | [−13.88, 0.267] | [−12.54, 0.175] |

The two fwd3_pnl point estimates look numerically large, but both CIs span zero by a wide margin
on both clustering schemes (e.g. session-block CI width of ~9-14 units against a point estimate of
2.8-4.0) — this is 8-15 checkpoints per bucket, well below any of this campaign's own
defensible-verdict floors. **Verdict: DATA_LIMITED, not a null.** This question would need the
governance-walled confirmation pool (not accessible to this family) to resolve either way.

## Too-good-to-be-true gate

**Trigger condition (per spec.yaml): none of the 8 primary/secondary cells had both the
session-block AND trade-block CI exclude zero on `b3` — the gate's residualization/
concentration-check machinery was never triggered.** The following checks were nonetheless run
because they are cheap and directly bear on interpreting the null:

1. **Lookahead re-verification.** `merge_asof(direction='backward', tolerance=2s)` guarantees the
   matched value-state row's timestamp is ≤ the checkpoint's timestamp within-session. Both parent
   features are independently already-verified causal by code inspection in their own REPORT.md
   (`signed_flow_aligned_60s`: trailing 60s window ending at T; `poc_share`/`value_dist_ticks`:
   causal running cumsum/cummax as of T). The join adds no new lookahead.
2. **sigma460 volatility-regime confound check (always computed, not just gate-triggered).**
   Correlation of the bucket predictor with `sigma460_atr_proxy_pts` in the HOLD/RTH/liquid
   sample: `\|value_dist_ticks\|` → **+0.304** (modest); `poc_share` → **−0.705** (strong). This is
   a real, disclosed finding independent of the null result: **`poc_share` in this specific merged
   sample is heavily entangled with the prevailing volatility regime** (consistent with AUCTION01's
   own observation that `poc_share` correlates with minutes-since-open, itself correlated with
   realized vol). Practically it means `poc_share` is the weaker of the two cuts for isolating an
   independent "value-state" mechanism here — `\|value_dist_ticks\|` (only 0.30 correlated with
   sigma460) is the cleaner cut, and it is also the one designated primary. Since no cell showed a
   signal to residualize away, this is reported as a caveat for future work reusing `poc_share` as
   an interaction term, not as an explanation of anything found here.
3. **Session/trade concentration check** (both bucket extremes, `value_dist_ticks` cut, HOLD
   group): far bucket = 40 trades / 28 sessions, top-4-session share of the bucket = 32.3%,
   top-4-trade share = 29.5%; near bucket = 39 trades / 27 sessions, top-4-session share = 33.8%,
   top-4-trade share = 32.2%. Neither bucket is dominated by a small handful of sessions or trades
   the way AUCTION01's D6 "favor" cells were (40-60% from 3-4 sessions there) — this null is not
   an artifact of concentration hiding a real signal in a diluted average, and (had a signal been
   found) it would not have been a small-n concentration artifact either.
4. **Trade-collapsed sanity check:** not run — FLOW01 already documented and rejected this
   specific construction's sunk-P&L confound for the unconditional relationship on this exact
   checkpoint universe; re-deriving it here (with no interaction signal to sanity-check in the
   first place) would only re-litigate a closed finding, which the spec explicitly rules out.

## Effective independent n (mandatory)

| group | raw checkpoints | analysis-sample checkpoints (RTH+liquid+matched) | distinct trades | distinct sessions |
|---|---|---|---|---|
| HOLD | 6,158 | 2,757 | 47 | 31 |
| PRE_EXIT | 63 | 33 | 33 | 22 |

HOLD checkpoints average ~59 per trade in the analysis sample (2,757/47) — still far from
independent-observation data, which is exactly why every statistic above is dual-clustered
(session-block primary, trade-block secondary per addendum C7) rather than checkpoint-pooled.
31 sessions clears this wave's own established ≥25-session floor (used by FLOW01/AUCTION01) for
treating a null as well-powered rather than merely small-sample.

## Scope and disposition

**Diagnostic-only — no trading policy, filter, sizing rule, or candidate is proposed.** The
addendum's top-priority AUCTION×FLOW interaction was tested exactly as preregistered: 4 primary
cells (2 cut variables × 2 outcome horizons) in the well-powered HOLD group, each tested two
statistically independent ways (OLS interaction coefficient and rank-based bucket split), each
with dual session-/trade-block clustered bootstrap, plus a 3-bucket ordinal robustness variant.
**Every angle agrees: FLOW01's unconditional clean null on `signed_flow_aligned_60s` does not
become conditionally informative once split by AUCTION01's value-state, in either direction, at
either horizon, under either cut variable.** This is a genuine, well-powered, multi-angle-confirmed
absence of the hypothesized interaction — not an artifact of low power (31 sessions, 47 trades,
2,757 checkpoints, ΔR² ≤0.0016 on every cell) and not explained by a lookahead defect, a
session-concentration artifact, or (for the primary `value_dist_ticks` cut specifically) a
volatility-regime confound. The `poc_share` secondary cut carries a real, disclosed interpretive
caveat (heavy sigma460 entanglement, ρ=−0.705) that future interaction work reusing `poc_share`
should account for. The PRE_EXIT group remains genuinely unresolved (DATA_LIMITED, n=22-24) and
should not be read as either a confirming or disconfirming result.

**Family disposition: NO_LARGE_EFFECT_DETECTED**, following FLOW01's own established convention
for a family that combines a well-powered clean null (HOLD) with a data-limited group (PRE_EXIT).
Per G1's own logic (small standalone effects can still earn a place if the mechanism is strong and
the data is valid) — the mechanism and the data were both genuinely defensible here, and the test
was run cleanly; it simply did not find the hypothesized conditional effect. This closes the
addendum's specific top-priority AUCTION×FLOW question for the `signed_flow_aligned_60s` /
`poc_share` / `\|value_dist_ticks\|` HOLD-checkpoint construction — it does not close AUCTION01's
own `poc_share`/`value_dist_ticks` main-effect finding (still `USEFUL_STATE_ONLY`, unaffected by
this result) nor FLOW01's PRE_EXIT question (still `DATA_LIMITED`), and it does not preclude a
different interaction construction (e.g. a shorter-lookback POC, a different flow classification,
or testing against ENTRY-event features rather than HOLD-checkpoint features) from being tried in
a future family.

## Follow-ups flagged, not built this pass

- A shorter-lookback / rolling POC (AUCTION01's own flagged follow-up) would make `value_dist_ticks`
  a more locally-relevant "distance from recent value" measure and could plausibly interact with
  flow differently than the since-session-open running POC used here — worth trying before
  concluding the AUCTION×FLOW mechanism itself is dead, since only one specific POC construction
  was tested.
- `poc_share`'s heavy entanglement with `sigma460_atr_proxy_pts` (ρ=−0.705) in this sample was not
  previously quantified in AUCTION01's own report (which only checked `poc_share` against
  minutes-since-open) — flagged for `STATE_INFORMATION_LIBRARY.csv` as an additional confound note
  on `poc_share` specifically, for any future family that reuses it as an interaction term.
- Re-running against ENTRY-event checkpoints (U9B's own event set) rather than HOLD checkpoints
  was out of scope this pass (FLOW01 never built an ENTRY-checkpoint feature table with
  `signed_flow_aligned_60s`) — not applicable without a new build.

## Files

- `runs/COMBO01_MULTIMODAL_SYNERGY/spec.yaml` — frozen spec (this run)
- `runs/COMBO01_MULTIMODAL_SYNERGY/src/01_build_merged_substrate.py` — causal merge_asof of
  FLOW01 checkpoints onto AUCTION01's `poc_1s_full`, RTH/liquidity flag reconstruction, filter
  cascade disclosure
- `runs/COMBO01_MULTIMODAL_SYNERGY/src/02_interaction_analysis.py` — additive-vs-interaction OLS,
  rank-split check, 3-bucket robustness variant, dual clustered bootstrap, too-good-to-be-true gate
- `runs/COMBO01_MULTIMODAL_SYNERGY/out/merged_checkpoints.csv`, `build_summary.json`,
  `combo01_results.json`, `build_log.txt`, `analysis_log.txt`
