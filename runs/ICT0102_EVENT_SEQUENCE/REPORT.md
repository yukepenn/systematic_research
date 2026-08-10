# ICT01+ICT02 — event-sequence science (sweep/MSS, PDH/PDL): CLEAN NULL, no construction

**Disposition: CLOSED — REDUNDANT / NO INCREMENTAL INFORMATION, both sub-families.** Per
`research/system_master/CONTINUOUS_EVOLUTION_WAVE4_PLAN.md`'s addendum row "ICT01+ICT02: Event-
sequence science (sweep/MSS/FVG, PDH/PDL)" — `NQ_OHLCV` information class, no new data. ICT02
(prior-day high/low objective) was run to completion as instructed (cheap, high-confidence).
ICT01 (sweep/MSS first pass) was scoped to exactly SWEEP-ONLY vs SWEEP+MSS as instructed, and
**does not extend to the fuller ablation (displacement/FVG/retracement) because sweep/MSS alone
already show no signal** — the addendum's own stopping rule for this case.

## Correctness gate (passed)

Both scripts independently load `u0_state_table.parquet`, slice to the canonical window
(`is_health_only_bar==False`), sum `bar_pnl_B_nq_dollars`, and hard-assert exact equality to the
certified canonical net **$301,915.92** before computing any ICT feature. Both reproduced it
exactly (`301915.92`). `sign(position_B)==sign(M)` agrees on 99.68% of in-position canonical
bars, confirming `position_B` (used throughout as the "M direction" conditioning variable, per
the addendum's own "position_B sign or sign of M" phrasing) is a faithful proxy for `M`'s sign.

## ICT02 — PDH/PDL objective (run to completion)

**Construction.** At every bar, PDH/PDL = the high/low of the most recently FINISHED session
(grouped by `sess_date`, shifted by one session) — never the current session's own high/low.
Sweep state uses a strictly causal intraday running max/min (`cummax`/`cummin` within the current
`sess_date`) against the fixed prior-session PDH/PDL. 460 first-session bars (no PDH/PDL) dropped.

**Descriptive.** Over all 539,772 bars with a defined PDH/PDL: `state_pdh` = not_swept 68.11% /
accepted 16.96% / rejected 14.93%; `state_pdl` = not_swept 73.55% / rejected 13.60% / accepted
12.85%. Sweep rate rises through the day (ETH_ASIA 19.3%/15.6% PDH/PDL → RTH_CLOSE 53.9%/47.0%),
as expected mechanically (more elapsed time = more chances to sweep a level fixed since the prior
close). `dist_to_pdh_atr`/`dist_to_pdl_atr` (ATR-normalized distance to the level) run consistently
negative/large (−13 to −32 ATR units to PDH; +19 to +43 to PDL) across every `M`-sign × vol-tercile
cell — this reflects unit scale, not a bug: `sigma460_atr_proxy_pts` is a short (~6.8-point mean)
per-bar-ish vol proxy while a full session's range averages ~359 points, so a session-anchored
level sitting many ATR-units away from the average bar's close is expected, not anomalous
(verified directly: session-range mean 359.4 pts vs sigma460 mean 6.8 pts).

**Forward-value test** (194,292 canonical `position_B≠0` bars, trade-direction-aligned features,
outcome = forward-20-bar `bar_pnl_B_nq_dollars`, EXP01's exact convention):

| feature | raw Spearman | resid. Spearman | ΔR² vs M/vol baseline | coef sign |
|---|---:|---:|---:|---|
| dist_favorable_atr | −0.0261 | −0.0244 | +0.00000 | + |
| dist_unfavorable_atr | +0.0210 | +0.0180 | +0.00015 | − |
| swept_favorable | +0.0176 | +0.0171 | +0.00000 | − |
| swept_unfavorable | −0.0027 | −0.0051 | +0.00002 | + |
| accepted_favorable | +0.0243 | +0.0231 | +0.00000 | + |
| rejected_favorable | −0.0077 | −0.0065 | +0.00003 | − |
| **full 6-feature block** | — | — | **+0.00045** | — |

Baseline R² (fwd20_pnl ~ |M|-tercile + vol-tercile) = 0.00056; full PDH/PDL block raises it to only
0.00100. Every single-feature ΔR² is ≤0.00015 — essentially zero incremental information.

**Chronology.** The strongest feature (`dist_favorable_atr`, resid. Spearman −0.0244) is **not
stable**: 2022 −0.0575, 2023 −0.0149, 2024 −0.0325, **2025 +0.0080 (sign flip)**, 2026 −0.0006
(near zero). No candidate was constructed, so there is no candidate-vs-control net delta to
report; 2022-2025 reference sum of forward-20-bar P&L over the test population is $5,118,647.50
(173,821 bars) — an observational baseline only, not a policy comparison.

**Right-tail audit.** PDH/PDL sweep-state at ENTRY of the top-20 (n=19, one early block has no
recorded ENTRY transition) vs bottom-20 all-time Product-B blocks: both dominated by `not_swept`
(top 13/19 PDH, 11/19 PDL; bottom 17/20 PDH, 10/20 PDL) — no meaningful differentiation.

**ICT02 verdict: CLOSED — REDUNDANT.** PDH/PDL distance/sweep/rejection state adds no stable,
economically meaningful information beyond the incumbent M-strength × vol-tercile state.

## ICT01 — sweep/MSS first pass (scoped, not the full ablation)

**Swing definition** (preregistered, single value, K=5 bars = 15 min, no sweep): bar i is a swing
high iff `high[i]` strictly exceeds all K bars to its left and is not exceeded by any of the K
bars to its right; causally knowable starting bar i+K+1 (one bar after the K-bar right-side
confirmation resolves — an extra-conservative buffer against same-bar lookahead ambiguity).
Computed on the continuous `t_idx` series (not session-reset, matching this table's own
`roll_hi20`/`roll_lo20` precedent). 32,560 swing-high and 32,547 swing-low candidates found
(~6% of bars each); known-swing coverage reaches 540,182/540,232 bars.

**SWEEP** = intrabar breach of the most recently known opposite swing point (transition-edge
flag, fires once per fresh breach). **MSS/BOS** = the identical breach CONFIRMED BY THE SAME
BAR'S CLOSE (`close[t]` beyond the level) — a strict subset of SWEEP (every MSS bar is also a
SWEEP bar). This same-bar design was deliberately chosen over an N-bar forward "confirmation
window" specifically to keep the predictor's measurement window and the forward-20-bar outcome
window (t+1..t+20) fully disjoint — the exact overlap/sunk-P&L confound class this campaign's
too-good-to-be-true gate has caught twice before (U5, LEV01); it is checked and clean here
(moot in the end, since no result here was strong enough to warrant suspicion).

Across all bars: 21,124 sweep_up events, 19,704 sweep_dn events; 51.4-51.7% of sweep events are
MSS-confirmed (close beyond) vs wick-only. Restricted to `position_B≠0` canonical bars with a
complete forward window: **14,064 sweep events** (7,533 continuation-type "with position," 6,531
adverse "against position"; 51.4% MSS-confirmed).

| test | ΔR² | resid. Spearman | n |
|---|---:|---:|---:|
| baseline (M/vol) | — R²=0.00068 — | — | 14,064 |
| **SWEEP-ONLY** (with- vs against-position) | +0.00053 | −0.0147 | 14,064 |
| **SWEEP+MSS** (add confirmed_mss) | +0.00003 (vs SWEEP-ONLY) | +0.0018 (controlling for sweep dir.) | 14,064 |
| SWEEP+MSS+interaction | +0.00005 (vs SWEEP-ONLY) | — | 14,064 |

SWEEP-ONLY's residualized Spearman is small AND wrong-signed relative to the naive "a sweep that
continues in your own direction is good" expectation (coefficient negative). MSS confirmation adds
essentially zero incremental information beyond sweep direction alone (ΔR²=+0.00003, Spearman
+0.0018) — **this directly answers the addendum's required question: MSS confirmation does NOT
add information beyond sweep alone, in this first pass.**

**Chronology.** SWEEP-ONLY's sign is negative in 4/5 years (2022 −0.0157, 2023 −0.0088, 2024
−0.0368, 2025 −0.0342, 2026 +0.0553 on a small n=1,528 partial-year sample) — directionally
quasi-stable but never exceeding |0.04|, i.e. present but economically negligible throughout.
2022-2025 event count 12,536, observational reference sum $557,374.08 (no policy built, no
candidate-vs-control comparison applicable).

**Right-tail audit.** Sweep-event incidence within lifetime bars of the top-20 vs bottom-20
all-time Product-B blocks: top-20 blocks see 65.6% continuation-type sweeps (326 events total)
vs bottom-20's 41.8% (122 events) — winners see more same-direction sweeps than losers, but this
is consistent with survivorship (a winning block by construction spends more time with price
moving in its own favor, generating more same-direction sweep events along the way) rather than
evidence of forward-predictive power, given the pooled regression above shows a near-zero-to-
negative relationship. MSS-confirmation rate is similar in both tails (58.0% top vs 53.3%
bottom) — no meaningful discrimination.

**ICT01 verdict: CLOSED — REDUNDANT, first pass.** Neither SWEEP-ONLY nor SWEEP+MSS shows a
stable, economically meaningful, incremental relationship to forward Product-B P&L. Per the
addendum's own instruction, **the fuller 5-level ablation (+displacement/+FVG/+retracement) is
explicitly NOT attempted** — sweep/MSS alone already show no signal, reported honestly rather
than forced.

## Overall disposition

**CLEAN_NULL, both sub-families.** No candidate constructed; Product B's existing entry/exit/hold
logic is unchanged. Consistent with this campaign's broader (though not universally conclusive —
per WAVE4 plan sec0's own caution against over-generalizing from individual OHLCV-transform
closures) pattern that local single-feature transforms of the same NQ_OHLCV path show diminishing
marginal information once the incumbent M-strength/vol-tercile state is already controlled for.

## Artifacts

- `runs/ICT0102_EVENT_SEQUENCE/src/01_ict02_pdhpdl.py` — ICT02 PDH/PDL construction + test
- `runs/ICT0102_EVENT_SEQUENCE/src/02_ict01_sweep_mss.py` — ICT01 sweep/MSS first-pass construction + test
- `runs/ICT0102_EVENT_SEQUENCE/out/ict02_features.csv`, `ict02_summary.json`, `ict02_top20_states.csv`, `ict02_bottom20_states.csv`
- `runs/ICT0102_EVENT_SEQUENCE/out/ict01_events.csv`, `ict01_summary.json`
