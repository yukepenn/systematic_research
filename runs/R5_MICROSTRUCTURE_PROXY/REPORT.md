# R5 — OHLCV-derived microstructure proxies — RESULTS

Per `spec.yaml`. **Disposition: CLOSED, no construction.** Genuine order-flow data does not
exist in this campaign (honest inventory below); every feature tested is an OHLCV-derived proxy,
labeled as such throughout.

## Data inventory (directive sec24)

This campaign's price data has exactly: `time, open, high, low, close, volume,
first_bar_of_session, sess_id, sess_date, is_last_of_sess`. **No tick trades, bid/ask, spread,
depth, or direct trade-direction/imbalance fields exist.** `research/scalping_lab/` has genuine
L1/L2/tick data but is a separate, unrelated campaign per `CLAUDE.md`/`RESEARCH_FRONTIER.md` and
is not reused here. Every feature below is honestly labeled as an OHLCV-derived proxy, not
genuine microstructure.

## Results (information-addition framework, same as R4)

| feature | raw Spearman | residualized Spearman | ΔR² | year sign-stability |
|---|---:|---:|---:|---|
| vol_surprise | -0.012 | -0.015 | +0.00003 | 3/5 (unstable) |
| vwap_disp_atr_aligned | 0.079 | 0.071 | +0.00185 | 4/5 |
| short_term_vol_ratio | -0.028 | -0.037 | +0.00044 | **5/5** (small magnitude) |
| **direction_x_volume** | **0.133** | **0.129** | **+0.01184** | **5/5** |
| vol_compression_ratio | -0.019 | -0.016 | +0.00031 | 2/5 (unstable) |

`failed_breakout_rejection` (categorical: did the entry bar break the prior 20-bar extreme but
close back inside it?): rejected entries have worse residual outcome (-$97.05 mean) than
non-rejected (+$45.57) — a real, directionally sensible, but modest split (632 of 1,978 entries,
32%, show rejection).

`vol_surprise` and `vol_compression_ratio` are closed as **NO INFORMATION** (unstable sign,
negligible ΔR²) — volatility compression does NOT predict subsequent trade quality in this data,
contrary to the classical compression→expansion heuristic (directive sec26 explicitly required
testing this rather than assuming it, and it does not survive).

## direction_x_volume — the strongest correlation found in R4+R5, and why it is NOT constructed

`direction_x_volume` (the entry bar's own directional move, oriented to trade side, weighted by
volume surprise) has the single strongest residualized correlation found across both R4 and R5
(0.129, ΔR² +0.0118, positive in all 5 years 0.099-0.152) — stronger than R4's CLV finding.
**Applying this campaign's now-standard right-tail pre-check decisively disqualifies it as a
filter candidate**: **45% of the top-20 all-time winning blocks have a NEGATIVE (below-median)
direction_x_volume** — worse than CLV's 15% failure rate in R4. Critically, **the bottom-20
losers ALSO show 45% negative** — statistically indistinguishable from the top-20's rate. **This
feature has genuine predictive power in the bulk of the outcome distribution but essentially ZERO
discriminating power at either tail** — exactly the property a right-tail-dependent system cannot
safely act on. `direction_x_volume` and CLV are themselves correlated (0.60), both substantially
capturing "did price move decisively in the trade's own favor within the entry bar," which also
limits their combined incremental value beyond either alone.

## Disposition

**R5: CLOSED, no candidate constructed.** `vwap_disp_atr_aligned`, `short_term_vol_ratio`, and
`failed_breakout_rejection` are recorded as modest, real, but small-effect leads (same
"deferred to a future soft-weighting study" status as R4's CLV finding) — not chased further
given the queue remaining. `direction_x_volume`, despite its strong aggregate correlation, is
explicitly **not** a lead: its tail-blindness was checked directly, not assumed, and is the
sharpest evidence yet in this campaign that a feature with genuine bulk predictive power can be
actively dangerous for a right-tail-dependent system. `vol_surprise` and `vol_compression_ratio`
close as no-information. Continuing automatically to R6 per directive priority order.
