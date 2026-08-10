# FAILURE_CRITERIA — predefined, percentile/mechanism-based, not tuned after future data arrives

**Frozen 2026-08-10.** Master Directive v4 sec31. These thresholds are fixed now, from already-
observed historical distributions, precisely so they cannot be retroactively adjusted once new
data arrives. Reuses Product B's own existing taxonomy (`research/system_master/CURRENT_EDGE_
HEALTH.md`) for consistency across both objects: **HEALTHY** (>50th historical percentile),
**NORMAL_WEAK_REGIME** (25th-50th), **WATCH** (10th-25th), **POSSIBLE_DECAY** (5th-10th),
**STRUCTURAL_BREAK_EVIDENCE** (<5th, or a mechanism-level trigger below).

## Product B — already has a live, quarterly-updated version of this

`research/system_master/CURRENT_EDGE_HEALTH.md`'s own rolling-60/rolling-120 Sharpe percentile
bands, giant-winner arrival rate, current-drawdown percentile, and state-mix stability checks
already implement exactly this discipline, on a live cadence (next reading due alongside
MONITOR-01, per `research/system_master/SM13_BMOM_DECAY_RULE.md`'s own standing schedule — no new
schedule invented here). **Reused by reference, not rebuilt.** This document adds nothing new for
Product B beyond pointing to that existing, already-percentile-based framework.

## Product A — first percentile-based failure criteria this campaign has built for it

Derived from `runs/U6B_PRODUCT_A_SCALE_RATE/forward_readiness/out/07_rolling_window_
distributions.csv` (CONTROL, byte-identical to unmodified Product A). **Disclosed precision
limit**: only min/p25/median/p75/max were computed this pass, not finer 5th/10th percentile cuts —
the WATCH/POSSIBLE_DECAY bands below use the observed min as a proxy anchor for the low tail
rather than a precisely-computed 5th/10th percentile; a future pass with a larger rolling-window
sample could sharpen these bands, and should, before they're relied on for anything beyond a
coarse first read.

| window | historical range (min .. p25 .. median .. p75 .. max) | HEALTHY (>p50) | NORMAL_WEAK_REGIME (p25-p50) | WATCH (near-min, below p25) |
|---|---|---|---|---|
| rolling-60 Sharpe | −3.01 .. 0.50 .. 1.36 .. 2.00 .. 4.75 | >1.36 | 0.50–1.36 | <0.50, approaching −3.01 |
| rolling-120 Sharpe | −0.47 .. 0.88 .. 1.26 .. 1.63 .. 3.02 | >1.26 | 0.88–1.26 | <0.88, approaching −0.47 |
| rolling-252 Sharpe | 0.36 .. 0.95 .. 1.23 .. 1.51 .. 2.17 | >1.23 | 0.95–1.23 | <0.95, approaching 0.36 |

**POSSIBLE_DECAY / STRUCTURAL_BREAK_EVIDENCE triggers (mechanism-based, not percentile-based,
since the percentile tail itself isn't finely resolved)**:
- A rolling-252 Sharpe reading **below the historical minimum (0.36)** — i.e. outside the entire
  observed range to date — is `POSSIBLE_DECAY` at minimum; two consecutive such readings is
  `STRUCTURAL_BREAK_EVIDENCE`.
- Top-20-all-time-block retention: if a future 6-month stretch produces **zero** new entries into
  the all-time top-20 block list while the strategy remains active, flag `WATCH` on right-tail
  arrival specifically (mirrors Product B's own "giant-winner arrival rate" indicator, not yet
  built as a live-updating check for Product A — flagged as a follow-up infrastructure item, not
  built this pass).
- Exposure-band monotonicity break (already flagged `POSSIBLE_DECAY` in `runs/H0_PRODUCT_A_
  HEALTH/REPORT.md`: the 10-13 contract exposure band flipped negative on a thin 331-bar sample) —
  **if this flip is still present and the sample has grown past ~1,000 bars at the next reading,
  escalate to `STRUCTURAL_BREAK_EVIDENCE`**; if it reverts, downgrade back to `HEALTHY`. This is
  the one live-tracked mechanism-level flag already open for Product A going into Wave 6.

## What would NOT count as a failure signal (stated explicitly, to prevent future over-reaction)

Per this wave's own forward-readiness panel: a rolling-20-session Sharpe anywhere in **[−5.92,
+7.94]** (Product A) is within normal historical variation and should not, by itself, trigger any
flag. A single bad quarter (2 of 18 canonical quarters were already negative) is not evidence of
anything by itself. The 2026 Jan-May weak stretch, on its own, is `NORMAL_WEAK_REGIME` at worst —
both objects' own existing evidence (this document's Product-B section, and the rolling-window
context above for Product A) is consistent with ordinary variation, not decay, as of this freeze
date.

## Review cadence

Tied to Product B's existing MONITOR-01 quarterly cadence for consistency — Product A's own
percentile bands above should be refreshed at the same reading, both to sharpen the currently-
coarse tail estimates and to re-check the two live-tracked mechanism flags.
