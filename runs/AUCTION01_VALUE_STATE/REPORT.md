# AUCTION01_VALUE_STATE — causal running POC/VWAP: real diagnostic signal on absolute expansion (D4), migration-conditioning (D6) underpowered/null

**Disposition: USEFUL_STATE_ONLY.** Step 0 gate PASSED (genuine trade-at-price data exists, in
`raw/NQ`, not in `grid1s/NQ`). D4 (concentration -> subsequent absolute expansion) shows a real,
moderate, confound-checked effect on all 37 (36 usable) BBO-confirmed sessions. D6 (POC migration
x incumbent direction) is underpowered by construction (the since-session-open running POC is
extremely sticky; "migration" events are a <1.2% rare-event flag, session-concentrated, and their
point estimates run counter to the naive continuation hypothesis) — reported honestly as a clean
small-n null for **that specific construction**, not as evidence against value-migration as an
idea. Diagnostic-only per addendum instruction: **no trading policy, filter, or candidate is
proposed this pass.**

Spec: `runs/AUCTION01_VALUE_STATE/spec.yaml` (frozen before results). Code:
`runs/AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py`,
`runs/AUCTION01_VALUE_STATE/src/03_diagnostics.py`. Outputs: `out/poc_1s_full.parquet` (3,027,377
rows, 37 sessions), `out/decision_points_30s.parquet` (27,299 RTH/liquid decision points, 36
sessions — `20250902` has zero BBO updates specifically during RTH, a real additional gap beyond
the 3 documented zero-BBO sessions, correctly dropped by the liquidity filter, not fabricated
around), `out/decision_outcomes.parquet`, `out/diagnostics_summary.json`.

## STEP 0 — mandatory gate (addendum D1-D2)

**Question:** does `grid1s/NQ/*.parquet` (or the underlying `raw/NQ/*.parquet`) contain genuine
trade-at-price volume, or only a 1-second OHLC-style aggregate?

**`grid1s/NQ` alone: FAILS D1.** `build_grid1s.py`'s Layer-1 aggregator computes only
last-price/trade-count/volume-sum per 1-second bucket (`.last()`/`.size()`/`.sum()` on a 1s-floor
groupby) — it discards the intra-second price distribution entirely. Building POC from grid1s
would require faking it off the bucket's last/typical price, which the addendum explicitly
prohibits.

**`raw/NQ` PASSES D1.** `raw/NQ/*.parquet` (what grid1s is built *from*) preserves genuine
per-trade prints: `bip==0` (Last) rows come from `SWScalpTickExport_v1/v3.cs`
(`Calculate.OnEachTick`, exporter comment "Last/Bid/Ask 1-tick events", same `Tick=1` granularity
as the explicit Bid/Ask `AddDataSeries` calls). Direct inspection of `s20251002.parquet` confirms
this empirically, not just from the code comment: 413,850 Last rows at millisecond timestamps,
volume distribution is single-print-sized (median=1, mean=1.09, IQR=[1,1] — not a monotonically
accumulating within-bar total), and **28,699 of 43,545 seconds (66%) contain more than one
distinct traded price within that second** (up to 57 distinct prices in a single second — e.g.
`2025-10-01T18:00:00.024-.244` alone prints at 25009.25, 25007.25, 25006.75, 25006.00, 25004.75).
This is structurally impossible for a 1-second-aggregate-only source.

**Verdict: PASS.** Construction proceeds from `raw/NQ/*.parquet`, aligned onto the 1-second grid
for merging (matching `build_grid1s.py`'s own last-observation-per-second + ffill convention). No
session outside the existing 40-on-disk set was requested or touched; the 37-session BBO-confirmed
universe (`sechilo/NQ` file list, same 3 exclusions as U9B: `20250811`, `20250924`, `20260430`) is
reused unchanged.

## Construction (addendum D3)

Causal running POC per session: sort Last prints by time, `tick_id = round(price/0.25)`,
`cum_vol_at_price = groupby(tick_id)[volume].cumsum()` (causal — uses only prints up to and
including the current one), `running_max = cum_vol_at_price.cummax()` (the running cross-bucket
max, valid because per-bucket cumvol is monotone non-decreasing, so the touched bucket's updated
value captures any new global max at each row), POC record set whenever
`cum_vol_at_price[i] >= running_max[i]`, forward-filled between records. This is an *exact*, not
approximate, causal running-POC — no lookahead by construction (verified by code inspection, not
just claimed). `poc_share = running_max_vol / cum_total_vol` (concentration proxy, since full
value-area-band computation isn't reducible to the same O(n) trick and was out of scope this
pass — disclosed simplification). Running VWAP computed but not used as a primary diagnostic
predictor this pass. All merges onto grid1s/sechilo/U0 use `time`; U0's `M`/`position_B` join is
`merge_asof(direction='backward')` — strictly causal (U0 match rate 99.7-99.8% across all 37
sessions). Decision points: RTH `[09:30,16:00)` ET AND trailing-60s(bid_upd+ask_upd)>0 (house
convention, matches W5-C1), sampled every 30s.

**A units bug was caught and corrected before reporting** (too-good-to-be-true discipline in
action): `sechilo/NQ`'s `mid_last/mid_high/mid_low` columns are stored pre-multiplied by 4
(price/0.25, i.e. already tick-denominated — verified directly: `sechilo.mid_last / raw.price ==
4.0000` exactly on a sample). The first diagnostics run divided these by `TICK=0.25` a second
time, inflating all D6 tick magnitudes by 4x (D4's Spearman rho/CI values are unaffected — rank
correlation is invariant to this kind of constant rescaling). All D6 numbers below are corrected
(divided by 4); the raw (uncorrected) run is superseded and not otherwise used.

## D4 — does concentration predict subsequent ABSOLUTE expansion? (addendum D4-D5)

Predictors: `poc_share_t` (running POC volume-share) and `|value_dist_ticks_t|` (|price - running
POC|, in ticks). Outcomes: `abs_markout_H` = |mid(t+H)-mid(t)| and `range_H` = forward realized
range, H in {15s, 60s, 300s}. Spearman rho, pooled, 1000-rep session-block bootstrap CI (36
sessions, resampled with replacement — matches U9B/W5-C1 convention).

| predictor | outcome | n | rho | 95% CI |
|---|---|---|---|---|
| poc_share | abs_markout_15 | 27,299 | −0.197 | [−0.274, −0.101] |
| poc_share | range_15 | 27,299 | −0.350 | [−0.461, −0.194] |
| poc_share | abs_markout_60 | 27,293 | −0.201 | [−0.275, −0.106] |
| poc_share | range_60 | 27,293 | −0.353 | [−0.462, −0.193] |
| poc_share | abs_markout_300 | 27,269 | −0.221 | [−0.302, −0.109] |
| poc_share | range_300 | 27,269 | −0.367 | [−0.483, −0.202] |
| \|value_dist\| | abs_markout_15 | 27,299 | +0.135 | [0.064, 0.205] |
| \|value_dist\| | range_15 | 27,299 | +0.229 | [0.101, 0.332] |
| \|value_dist\| | abs_markout_60 | 27,293 | +0.132 | [0.056, 0.199] |
| \|value_dist\| | range_60 | 27,293 | +0.232 | [0.110, 0.349] |
| \|value_dist\| | abs_markout_300 | 27,269 | +0.138 | [0.046, 0.220] |
| \|value_dist\| | range_300 | 27,269 | +0.245 | [0.114, 0.357] |

**All 12 cells: CI excludes zero, consistent sign at every horizon.** Higher POC concentration
(`poc_share`) -> *lower* subsequent absolute movement (compression/consolidation persists). Larger
distance from the running POC (`|value_dist|`) -> *higher* subsequent absolute movement (price
away from the session's value area keeps moving — both a rejection-continuation and a reversion
story are directionally consistent with "expansion"; this diagnostic deliberately does not
disambiguate direction, per D5). Effect sizes are modest (|rho| 0.13-0.37, `range` outcomes
notably stronger than `abs_markout`), not large.

**Too-good-to-be-true gate — confound check.** Both `poc_share` (decreasing denominator early in
the session) and `range_60` (opening-range volatility) plausibly share a pure time-of-day trend.
Checked: raw correlation of `poc_share` with minutes-since-RTH-open is −0.21, of `range_60` with
minutes-since-open is −0.39 — both real. But **after linearly residualizing both series on
minutes-since-open, the partial correlation is −0.49 (n=27,293) — *stronger*, not weaker, than the
raw pooled estimate.** Same check for `|value_dist|` (raw corr with time-of-day only 0.019, a
non-confound already) gives a partial rho of 0.228, essentially unchanged from the raw 0.232. The
relationship is not a time-of-day artifact.

**Temporal stability (poor-man's chronology check — addendum's year-by-year discipline doesn't
map cleanly onto a single 9-month tick sample, so first-half/second-half session split is used
instead):** 18 earliest vs 18 latest sessions (chronological, `20250814..20260123` vs
`20260206..20260520`). `poc_share` vs `range_60`: H1 rho=−0.266 (n=13,253), H2 rho=−0.122
(n=14,040). `|value_dist|` vs `range_60`: H1 rho=0.233, H2 rho=0.073. **Same sign both halves,
but the effect weakens materially in H2** — reported honestly, not smoothed over. This is
consistent with a real but modest, possibly regime-sensitive effect, not a robust all-weather one.

## D6 — POC migration conditioned on incumbent direction (addendum D6)

`poc_migration_60s_ticks = poc_price_t - poc_price_{t-60s}`, classified up(>=+1t)/down(<=-1t)/flat.
"Favor" = migration in the position's direction (`position_B=+1` & up; `position_B=-1` & down);
"not_favor" = everything else at that side. Outcomes in the position's frame (side-adjusted),
ticks: `signed_markout_H`, `MFE_H`, `MAE_H` (from sechilo mid_high/mid_low); `contprob_H` =
P(signed_markout_H>0).

**The running-since-session-open POC is extremely sticky by construction** — a price level must
out-draw the entire session-to-date cumulative-volume record to become the new POC, so "migration"
within any single 60s window is a rare, late-session-improbable event: only 78/8,406 long
decision-points (0.93%) and 96/8,309 short decision-points (1.16%) qualify as "favor" at all,
concentrated in a handful of sessions (top-4 sessions = 47/78 = 60% of the long "favor" sample;
top-3 = 39/96 = 41% of the short sample) — these are not 78/96 independent observations.

| side | outcome (H) | n_favor | n_not | mean_favor(t) | mean_not(t) | diff(t) | 95% CI |
|---|---|---|---|---|---|---|---|
| long (+1) | signed_markout_15 | 78 | 8,328 | −6.29 | +0.18 | −6.47 | [−11.04, −2.34] |
| long (+1) | signed_markout_60 | 78 | 8,328 | −9.09 | +0.65 | −9.74 | [−35.86, 9.92] |
| long (+1) | signed_markout_300 | 78 | 8,328 | +8.08 | +2.08 | +6.00 | [−67.84, 64.98] |
| long (+1) | contprob_15 | 78 | 8,328 | 0.397 | 0.494 | −0.096 | [−0.157, −0.044] |
| long (+1) | contprob_60 | 78 | 8,328 | 0.513 | 0.495 | +0.018 | [−0.127, 0.147] |
| long (+1) | contprob_300 | 78 | 8,328 | 0.538 | 0.507 | +0.032 | [−0.128, 0.145] |
| short (−1) | signed_markout_15 | 96 | 8,213 | −2.23 | −0.19 | −2.05 | [−9.51, 2.33] |
| short (−1) | signed_markout_60 | 96 | 8,211 | −7.85 | −0.21 | −7.64 | [−20.83, 4.60] |
| short (−1) | signed_markout_300 | 96 | 8,203 | −21.97 | −1.42 | −20.55 | [−51.45, 8.85] |
| short (−1) | contprob_15 | 96 | 8,213 | 0.458 | 0.489 | −0.031 | [−0.156, 0.075] |
| short (−1) | contprob_60 | 96 | 8,211 | 0.427 | 0.489 | −0.062 | [−0.150, 0.009] |
| short (−1) | contprob_300 | 96 | 8,203 | 0.406 | 0.490 | −0.083 | [−0.185, 0.024] |

(Full MFE/MAE table in `diagnostics_summary.json` — every MFE/MAE cell has a positive diff, i.e.
the "favor" cell always shows larger two-sided excursions, exactly what you'd expect from a
volatility-selected subsample regardless of any real directional mechanism, so MFE/MAE are not
treated as informative here.)

**Verdict on D6: no usable conditioning effect established.** Where a CI excludes zero
(long-side 15s signed_markout and contprob), the point estimate runs **opposite** the naive
"migration confirms the incumbent's direction" hypothesis — POC migrating in the position's favor
predicts a *worse* 15s markout and *lower* continuation probability, not better. Combined with
n=78 concentrated in 4 sessions, and the effect not surviving to 60s/300s (CIs widen and cross
zero, sign even flips for the long 300s cell), the honest read is: **this specific
migration-conditioning construction is underpowered and inconsistent, not a discovered edge in
either direction.** The plausible mechanism (POC is a lagging measure — it only "catches up" to a
price level after a move has already partly happened, so by the time migration is observed the
move may be exhausted) is worth naming but is speculation on n<100, not a finding.

## Too-good-to-be-true gate — summary

1. Corrected a real 4x unit-scaling bug in `sechilo`'s pre-tick-denominated columns before
   reporting any D6 magnitude (caught by comparing raw ticks against the campaign's known cost
   hurdle — 89-462 "ticks" MFE/MAE was implausible on its face; corrected values, 16-116 ticks,
   are still large for short horizons but at least physically plausible for NQ RTH microstructure
   and don't change any qualitative conclusion).
2. Checked D4 for a time-of-day confound (both predictor and outcome plausibly session-clock
   driven) — the effect *survives and strengthens* under linear residualization, not explained
   away.
3. Checked D4 for temporal stability via a first-half/second-half session split — same sign both
   halves, but real fading from H1 to H2, reported rather than hidden.
4. Checked D6's "favor" cells for session concentration before treating any CI-excludes-zero cell
   as a finding — found heavy concentration (40-60% of the "favor" sample from 3-4 sessions) and
   a counter-intuitive point-estimate direction, and reported the honest small-n-null verdict
   instead of a false positive.
5. No lookahead: the running-POC record-detection algorithm and all merges are causal by
   construction (verified by code inspection, not asserted).
6. Governance: only the 40-session on-disk substrate was read; the 37-session BBO-confirmed
   subset (minus one further RTH-only BBO gap on `20250902`, correctly auto-excluded by the
   liquidity filter) was used throughout; no session outside this set was requested, exported, or
   examined. Data range used: `20250814`..`20260520`, entirely inside the unsealed development
   window (nothing >=2026-06-01 touched).

## Scope and disposition

**Diagnostic-only, per addendum instruction — no trading policy, filter, or candidate is
constructed or proposed this pass.** D4's finding (running-POC concentration and distance-from-POC
both carry real, modest, non-time-of-day-confounded, directionally-consistent-but-fading
information about subsequent absolute price movement) is genuine residual information from a
previously-untested class (`NQ_VOLUME_AT_PRICE`) and is flagged `reusable_as_state` /
`reusable_for_interaction` for a future sizing/HOLD/interaction construction pass — it has **not**
been tested as a binary filter, entry/exit rule, or sizing input, so no construction-level
disposition (`CLOSED_*`) applies yet. D6's specific migration-conditioning construction is
underpowered on the current 37-session substrate and returns a clean, honestly-reported null —
not evidence the underlying idea (value migrating in the incumbent's favor) is false, just that
this particular <100-event since-session-open 60s-window operationalization of it cannot be
evaluated on the data currently available. Overall family disposition: **USEFUL_STATE_ONLY.**

## Follow-ups flagged, not built this pass

- Full 70% value-area band (not just POC point + share) — would need a different algorithm than
  the O(n) running-max trick used here; deferred given time budget.
- A shorter-lookback (e.g. rolling 15-30min) POC/value-area, which would make "migration" a much
  less rare event and give D6 real statistical power — worth trying before concluding anything
  about value-migration as a mechanism.
- Re-running D6 once the internal confirmation pool is released for a survived candidate (not
  applicable yet — nothing here rose to "candidate").

## Files

- `runs/AUCTION01_VALUE_STATE/spec.yaml` — frozen spec (this run)
- `runs/AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py` — Step 0 evidence generation + causal running-POC/VWAP construction + grid1s/sechilo/U0 merge + decision-point extraction
- `runs/AUCTION01_VALUE_STATE/src/03_diagnostics.py` — D4/D6 forward-outcome construction + session-block bootstrap
- `runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet`, `decision_points_30s.parquet`, `decision_outcomes.parquet`, `diagnostics_summary.json`, `build_log.txt`, `diag_log.txt`
