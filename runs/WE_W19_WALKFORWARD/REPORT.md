# WE_W19 — WALK-FORWARD · REPORT

17 quarterly refits, trailing-12-month fit, 64 configs per refit, traded only on the next
quarter. This is the campaign's first genuine out-of-sample evidence obtained without waiting.

| object | weeks | net | wk mean | % pos | worst | **Sharpe** | trades |
|---|---|---|---|---|---|---|---|
| **WF walk-forward** | 203 | **$207,669** | $1,023 | 58.1 % | −$23,537 | **0.171** | 3,373 |
| FIXED (narrow6, q0.8, delta, both) | 205 | $341,300 | $1,665 | 61.0 % | −$24,417 | 0.249 | 3,641 |
| NAIVE (narrow6, no gates, both) | 205 | $251,821 | $1,228 | 59.0 % | −$37,318 | 0.150 | 6,595 |
| BESTFIXED (narrow5, q0.8, delta, **long**) | 204 | $278,916 | $1,367 | 60.3 % | **−$14,543** | 0.279 | 1,954 |

## PREREGISTERED VERDICT: **WEAK**

WF (0.171) beats NAIVE (0.150) but falls short of 0.8 × FIXED (0.200). Translation, without
softening: **the campaign's fixed-calibration numbers overstate what the method delivers
forward by roughly 30 %, and quarterly parameter selection buys only +0.021 Sharpe over doing
nothing at all.**

## The diagnostic that matters more than the verdict

**Choice instability: 14 distinct configurations across 17 refits — 88 % of boundaries changed
the choice.** Quarter-to-quarter parameter selection is essentially noise. The trailing-window
Sharpe that drives it rose from 0.167 to 0.473 and back to 0.398 while the out-of-sample
quarters swung from +0.501 to −0.238 with no relation to the fit score.

Three consequences, all actionable:

1. **Stop selecting.** When selection is noise, the correct response is aggregation, not a
   better selector. Campaign #1 reached the same conclusion by a different route ("ensembles
   beat parameter selection", PBO 0.48–0.90). W20 tests aggregation directly.
2. **Long-only surfaces a third time.** BESTFIXED is long-only, with by far the best worst
   week (−$14,543 vs −$23.5k…−$37.3k). W17 (deep history) and W16 (both-sides split) pointed
   the same way. This is now the most replicated finding in the campaign.
3. The WF equity is still positive and beats naive — so the machinery is not worthless; it is
   *worth less than advertised*, and the advertisement was mine.

## Method note
Every sleeve is session-flat, so a config's trade list computed once over the whole period can
be sliced by quarter without error. That made 17 × 64 refits cheap; the same trick should be
reused for all future walk-forward work.
