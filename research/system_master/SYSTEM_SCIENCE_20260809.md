# SYSTEM_SCIENCE_20260809 — closing report, SYSTEM ARCHITECTURE SCIENCE + ALPHA OPTIMIZATION
# MEGA DIRECTIVE (+ CURRENT-REGIME HEALTH ADDENDUM)

Written 2026-08-09 at the close of the full priority queue: SA0 → R3 → R2B → R4 → R5 → R6 → PA0 →
PA1 → SYN (this document), plus the current-regime-health addendum layered in mid-campaign. Every
family closed to a disposition; the stop condition (directive sec60) is met. This is the entry
point for "what did this campaign learn" — full evidence lives in each `runs/<FAMILY>/REPORT.md`
and in `research/system_master/STRUCTURE_MAP.md` / `CURRENT_EDGE_HEALTH.md`.

## Outcome in one line

**Zero promotions. Both `SolarWaveSMMaster_v4` (Product A) and `SolarWaveOneContractNQ_v5` /
`SolarWaveOneContractMNQ_v5` (Product B) remain UNCHANGED.** This campaign's contribution is
understanding, not a version bump — a genuinely different, and in several places more valuable,
outcome than another marginal parameter tweak would have been (per directive sec52).

---

## Answers to the 23 standing questions (directive sec53 + addendum sec20)

**1. Why does Product A work?** A 13-member volatility-normalized directional-change ensemble
(Solar13) generates a base trend signal; an HTF (50-session SMA) tilt amplifies agreement with the
longer trend; a short-halving overlay (c1_50) reduces short conviction when fighting an up daily
trend; B-MOM (an independent RTH VWAP/band-breakout engine) adds a second, largely orthogonal
signal that both amplifies strong Solar entries and occasionally redirects/prevents weak ones;
continuous sizing (0-13 MNQ contracts) scales exposure with genuine conviction — PA0 proved this
sizing captures real information (P&L per contract rises monotonically from -$0.04/bar at 1-3
contracts to +$1.88/bar at 10-13 contracts) rather than being blind leverage.

**2. Why does Product B work?** The same Solar13+HTF+B-MOM decision core, discretized to
`{-1,0,+1}` via a hysteresis(3,1) dead-band that prevents chatter at unit sizing. SA0 quantified
the dead-band's net value directly: +$54,053 (+17.9%) vs a no-gap policy, at the cost of slightly
higher tail risk (CDaR95 $44,518 vs $33,574) — a real, disclosed, two-sided tradeoff, not a free
improvement.

**3. What does Solar13 contribute?** ~45% of standalone net dollars when isolated (SOLAR_ONLY
ablation: $134,499 of FULL's $301,916), with genuine but non-monotonic member-level structure:
participation ratio 3.66/13 (real diversity, not collapsed), adjacent-VM members correlate 0.77
while far members correlate 0.025 (redundancy is local, not global), and leave-one-member-out
shows the slower members (VM20-30) are disproportionately load-bearing (-$32k to -$64k each if
removed) while one member (VM12) is actually a net drag (+$27,869 if removed).

**4. What does HTF contribute?** A modest, real, asymmetric edge: +$8,289 net (2.7%), entirely
from the long side (+$31,051 long, -$21,912 short) — HTF is a long-favoring amplifier, not a
symmetric one, and it fires on only 35% of bars.

**5. What does B-MOM contribute?** Architecturally, B-MOM can NEVER independently trigger an entry
(`|WBMOM·B| ≤ 2.83 < EntryLevel 3.0`, a structural fact, not an empirical one) — yet its own
standalone signal has Sharpe 1.26 (independently cross-checked against `SMV2B_BMOM_EXEC_AUDIT`),
comparable to the full combined system. Its actual role is a 30.4%-of-fresh-entries decisive
gating/redirecting effect; entries where it's engaged average +$484 vs -$739 when not — the
single strongest conditional split found in the entire SA0 pass.

**6. What does hysteresis contribute?** See Q2. Additionally: it is the mechanism directly behind
the April-2026 flagged losses being ~$1,750/$1,150 worse than a no-gap policy would have made
them on those two specific trades — a real, small, disclosed cost of a mechanism that is net
strongly beneficial overall.

**7. Why do the largest losses happen?** Two independent, converging lines of evidence:
(a) `giveback_ratio` (P0, generalized): positions that never become meaningfully profitable
account for 903/1,151 (78.5%) of all loser blocks and 100% of the worst decile; (b) SA0's
exit-reason atlas: `REVERSAL` exits (4.4% of blocks) average -$2,315 at 12% win rate, far worse
than `FLAT_EXIT`'s +$275/43%; short-duration entries (<3h) are net negative in aggregate
(-$831,772 combined) while long-duration entries (>3h) are strongly positive (+$1,147,843
combined). SA0's matched-control test (sec15) found NO entry-state signal distinguishes the
20 largest losers from same-state peers (matched-winner-rate 43% ≈ unconditional 41.8%) — **the
losses are not a distinguishable, fixable entry-quality defect; they are the cost of running many
small trial positions to find the few that develop into giant winners** (independently confirmed
from the Product A side too: PA0's exposure-band analysis shows the same pattern, 1-3-contract
positions are a net drag mechanically inseparable from the entries that scale up).

**8. Why do the largest winners happen?** Sustained, high-conviction, long-duration holds:
top-20 winners require both high initial consensus (entry vote-dispersion 8.0/13 vs 6.75/13 for
bottom-20 losers, though both are elevated vs the population) and patience (PA0: forward-20-bar
value of SCALE_IN contracts is +$14.43, 7x fresh entries' +$2.03 — the system's own conviction
genuinely rises as good trades develop, and scaling into that is real, not noise).

**9. Are longs and shorts structurally different?** Yes, decisively, in BOTH products. Product B:
long Sharpe 1.54 vs short 0.18, short maxDD ($81,894) alone exceeds the combined system's own
maxDD ($59,717), but shorts carry 9.7x higher tail concentration (19.8% vs 2.0% top-decile share)
— a crisis-insurance signature, not simple weakness. Product A: same qualitative pattern (long
Sharpe 1.38 vs short 0.40). **No short-side suppression is implemented** — SA0/PA0 explicitly did
not construct one, per the crisis-insurance framing and the standing prohibition on filtering
without understanding first.

**10. Does time-of-day contain incremental information?** R3's central, mechanistic finding: S2's
own diagnostic motivation (bar-level P&L bleed in 02:00-08:00 ET) is a HOLD-TIME phenomenon
(positions entered elsewhere, held through the window), not an entry-quality one — entries
commenced IN that window are actually net POSITIVE (+$79,925, 4/5 years). This explains WHY S2's
blanket entry-block construction failed its own right-tail gate. No state-conditioned entry
eligibility rule survived construction (the one promising lead, weak-M-strength filtering, was
right-tail-vetoed: 8/20 top winners are weak-M-tercile entries).

**11/12. Which New Horizon / new-information features survived?** None survived to construction
with a clean right-tail profile. R4 found close-location-value (CLV) is a real, stable (5/5 years),
incremental signal (residualized Spearman 0.106) — but 15% of top-20 winners have "poor" CLV.
R5 found `direction_x_volume` has the STRONGEST aggregate correlation in the whole pass
(residualized Spearman 0.129, 5/5 years) — but it fails the right-tail check even more decisively
(45% of BOTH top-20 winners AND bottom-20 losers show "bad" values: real bulk predictive power,
zero tail-discriminating power). Both are recorded as disclosed, well-evidenced leads for a future
soft-weighting/sizing study, not hard filters — this campaign's finite queue did not build and
validate that more complex construction. R2B (pullback→reclaim) is mechanistically distinct from
R2's closed fixed-delay axis and found a real diagnostic effect, but its constructed candidate
showed the identical 2026-stub-only chronology failure R2V1 already found for confirm_bars — now
independently replicated by a second, structurally different mechanism, strengthening rather than
narrowing that finding.

**13. Is a genuine Engine #3 available?** No. R6 audited this session's own findings against the
prior 15-candidate/5-slate/0-survivor record (which already explicitly killed VWAP-reversion and
fade mechanisms) and found nothing this session clears the "genuinely new idea" bar. Axis remains
exhausted at 15/15; no candidate manufactured to fill the slot.

**14. Can Product A sizing be improved?** Not demonstrably, this pass. PA0/PA1 found the CURRENT
linear-rounded sizing scheme is well-validated by its own data (P&L per contract rises
monotonically with size; scale-in is more valuable than fresh entries) and the ±13 clamp is
mathematically proven to never bind (dead code under current weights) — there is no diagnosed
defect to fix. The one numerically negative band (1-3 contracts) is mechanically inseparable from
the entries that later develop into profitable size, so no filter was constructed.

**15. Which candidates were rejected and exactly why (one line each)?**
- R2 (confirm_bars fixed delay): 2022-2025-only delta -$4,431 (a wash), entire headline from the
  2026 stub.
- R2B (pullback→reclaim, adaptive): the SAME 2026-stub-only pattern, independently replicated
  (2022-2025-only delta -$4,551).
- R3 (state-conditioned SelTime): entries in S2's flagged window are net positive; weak-M filter
  destroys 8/20 top winners.
- R4-A (slope): redundant with existing state (ΔR²≈0).
- R4-B (CLV) / R5 (direction_x_volume, vwap, short-term-vol, failed-breakout): real signals, all
  deferred (not hard-filter-safe for the right tail; direction_x_volume additionally tail-blind
  in the bulk).
- R6: no candidate, axis exhausted.
- PA1: no candidate, sizing already validated as informative.
- R1 (prior wave, giveback exit): net tail-dollar-negative, chronologically unstable.

**16. What is the best defensible architecture now?** Unchanged: `SolarWaveSMMaster_v4` (Product
A) and `SolarWaveOneContractNQ_v5` / `SolarWaveOneContractMNQ_v5` (Product B), exactly as
documented in `BASELINE_MODELS.md`. This campaign's evidence strengthens, rather than weakens,
confidence in that architecture: every structural component (Solar13 diversity, HTF's modest
asymmetric edge, B-MOM's gating role, hysteresis's net-positive dead-band, the sizing scheme's
conviction-tracking, even the never-binding ±13 clamp) was found to be doing something coherent
and defensible when examined directly, not merely assumed.

**17. Is each baseline currently healthy?** Product B: **HEALTHY** overall per
`CURRENT_EDGE_HEALTH.md`, with one WATCH flag (rolling-120 Sharpe, mechanically explained by
still containing the weak Jan-May 2026 stretch). Rolling-20/60-session Sharpe (3.2 / 1.3) sit at
the 78th-86th percentile of history. Product A was not separately extended to the current-health
window this pass (PA0 stayed on the canonical window matching its own certified figures, a
disclosed scope limitation) — its Solar13/HTF/B-MOM building blocks are identical to Product B's,
so the same qualitative health read plausibly transfers, but this is inference, not independently
measured, and is flagged as a concrete next step rather than asserted.

**18. Why has 2026 differed from earlier years?** Not opportunity-mix (SA0/CURRENT_EDGE_HEALTH:
`P(M-strength tercile | year)` is stable across all 5 years) and not conditional-edge decay
(same-state payoffs in 2026 are mid-range vs 2022-2025, not degraded). The Jan-May 2026 stretch
was substantially a SHORT-SIDE-localized phenomenon (-$557/trade) that reversed sharply in the
newly-available June-July data (+$1,003/trade, n=43).

**19. Opportunity-frequency shift or payoff-relation decay?** Neither, per Q18's evidence — this
is the disclosed, tested answer, not an assumption. Giant-winner arrival rate in 2026 is actually
the HIGHEST of any year on record (44.70 per 250 sessions annualized), directly refuting a
"right tail stopped arriving" story.

**20. Is the present drawdown/stagnation historically unusual?** No. Current drawdown ($5,625) is
at the 34th percentile of all historical daily drawdown readings — unremarkable.

**21. What historical regimes resemble current conditions?** A 5-feature rolling-60-session state
vector finds the current regime's nearest historical analogs are overwhelmingly April 2025 (the
already-documented tariff-crash volatility period). Forward-60-session performance following those
analogs was negative on average, but this is disclosed as a small, autocorrelated sample (7 of 10
analog dates within one 8-day span) with partial-window truncation for the most recent analogs —
a real, moderate-confidence signal, not a confident forecast.

**22. What evidence would make us believe the edge is actually decaying?** Per the standing
R2V1 standard (excellent-recent/no-2022-2025-improvement = NOT PROMOTED, applied symmetrically
here to health monitoring): a finding would need to (a) generalize beyond a single recent window,
(b) show same-state conditional payoffs degrading across multiple years, not just one, and
(c) survive out-of-sample as genuinely new data arrives — none of which is currently observed.

**23. What should be monitored going forward?** The 8 edge-health indicators in
`CURRENT_EDGE_HEALTH.md` sec8 (rolling-60/120 Sharpe, current drawdown percentile, giant-winner
arrival rate, conditional edge at strong-M, short-side rolling health, state-mix stability,
rolling-window positivity rate) — re-run this same dashboard as genuinely new (non-locked-forward)
data accumulates, watching specifically whether the June-July short-side recovery holds.

---

## Baseline update decision (directive sec54)

**PRODUCT A: UNCHANGED.** **PRODUCT B: UNCHANGED.** No construction from SA0/R3/R2B/R4/R5/R6/PA1
passed its own promotion/construction gate. This is recorded as a genuine, well-evidenced negative
result, not a failure to find one — the campaign directly strengthened understanding of why the
current architecture works and found no defect that a fix would clearly repair without new,
comparably-sized right-tail risk.

## What this campaign leaves for a future wave (disclosed, not silently dropped)

1. R4/R5's CLV and vwap-displacement leads (real, stable, right-tail-safe-if-used-as-soft-weight,
   not hard filters) — a genuinely different construction shape than anything tried this campaign.
2. R3's identified hold-time (not entry-eligibility) mechanism for the 02:00-08:00 ET bar-level
   bleed — a different layer (exit/hold, per directive sec37) than R3 itself was scoped to test.
3. Product A's own current-health extension through the latest available data (this pass only
   extended Product B).
4. The regime-analog forward-return signal (sec21 above) with a larger, less-autocorrelated
   sample, once more calendar time has passed.

## Campaign stop condition

Met. SA0, R3, R2B, R4, R5, R6, PA0/PA1 all closed to a disposition; no family remains queued.
Per directive sec16/sec60, this document is the final deliverable — the campaign is closed.
