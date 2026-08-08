# W2-1 FAST_STRUCTURAL_OPPORTUNITY_CENSUS — READOUT (2026-08-08)

Spec: `specs/W2-1_fast_opportunity_census.md` (frozen 1025569 before readout).
Data: 37 L2 discovery sessions, per-second mid hi/lo substrate (`substrate/sechilo/NQ`,
union Bid+Ask event stream) + grid1s features. RTH decision clock, quote-alive filter.
Tables: `census_counts.csv`, `census_features.csv`, `census_updown.csv`,
`excursion_surface.csv`, `census_mfemae.csv`. Labels are RETROSPECTIVE — nothing here is
a strategy; any rule must be preregistered before P&L (done: W3-1). Registry S6/S7.

## FACT — owner-scale moves are abundant, not rare

- Median 60s forward MFE (30s RTH clock, long side) = **20.0 ticks = exactly 5 NQ
  points**; median 120s MFE = 28.5t. The owner's "several points in tens of seconds" is
  the MEDIAN path excursion of this (high-vol 2025-08→2026-05) sample, not a rare event.
- Episodes/day/direction at (H=60s, M≥20t): **~292** (near the 60s-refractory ceiling of
  390); even M≥32t within 60s: ~218/day. Time-of-day mix is flat (midday slightly higher
  than open — the map is not an open-auction artifact).
- time-to-MFE at H=60: p50 = 29s — moves develop over tens of seconds, matching the
  owner's discretionary hold scale.
- MAE quantiles are symmetric to MFE (60s MAE p50 = 20t): raw timing without stops is a
  coin flip on a big amplitude. Opportunity abundance is NOT the constraint —
  **direction + retention is the entire problem.**

## FACT — the excursion surface: the viability gap SHRINKS with bracket size

Unconditional P(target first), 30s RTH clock, cap 600s (p_neither ≈ 0):

| Bracket (+A/−B) | p long | p short | BE @C1 | BE @C2 | gap to C1 |
|---|---|---|---|---|---|
| +8/−4 | 0.331 | 0.323 | 0.573 | 0.739 | 24.2–25.0pp |
| +12/−4 | 0.256 | 0.252 | 0.430 | 0.555 | 17.3–17.8pp |
| +16/−6 | 0.276 | 0.275 | 0.403 | 0.494 | 12.7–12.9pp |
| +20/−8 | 0.289 | 0.285 | 0.388 | 0.460 | 9.9–10.3pp |
| +24/−8 | 0.253 | 0.249 | 0.340 | 0.402 | 8.7–9.1pp |
| +32/−10 | 0.236 | 0.233 | 0.307 | 0.354 | **7.0–7.4pp** |

**This is the central economics of Zone F:** fixed friction shrinks relative to bracket
size, so the conditional-lift a state must deliver falls from ~25pp (micro brackets,
already shown unreachable in W1-1/W2-0) to **~7–10pp at 24–32t brackets**. A state that
lifts P(target-first) by 7–10pp on big brackets is economically viable. That is the
quantified target for all FSS families. (Long p > short p uniformly — sample drift;
treat direction symmetry with care at Tier-1.)

## FACT — pre-state of big moves: activity/vol dominates, and it is NOT a discovery

Top effects vs rv60-quintile-matched controls (H60/M20; |median diff/IQR| 0.77–0.86):
upd60/upd10, range300, tv60, rv60/rv300, trades, vol, spread60 — all volatility/activity
proxies, for BOTH directions. Per the frozen honesty rule: **"high-activity periods move
more" — volatility proxy, not a discovery.** Quintile matching is too coarse to fully
remove it; treated as confound floor, not signal.

Cost-relevant side-fact: mean prior-60s spread at opportunity moments is **2.42t vs
1.78–1.80t at matched controls** — friction is elevated exactly when opportunities
exist. C1 (1t/side) is most optimistic precisely in-state; C2 stress is mandatory for
any FSS candidate.

## FACT — the only strong DIRECTIONAL precursor is contrarian, at 5–30s horizon

UP-opportunities vs DOWN-opportunities (H60/M20), the direct directional read:

| feature | median before UP-opp | median before DOWN-opp | effect | 95% CI |
|---|---|---|---|---|
| ret5 | **−5.0t** | **+5.0t** | −0.56 | [−10.0, −9.5] |
| ret10 | −6.0t | +6.0t | −0.50 | [−13.0, −12.0] |
| ret30 | −6.5t | +6.5t | −0.33 | [−14.0, −12.0] |
| sflow10 | −3.0 | +3.0 | −0.29 | [−7.0, −6.0] |
| ret60 / ret300 / eff60 / rv60 … | ~0 separation | | ≤0.07 | mixed |

A ≥20t up-move within 60s is typically preceded by a 5–10t DOWN move (and negative
tick-rule flow) in the prior 5–30s; symmetric for down-moves. Momentum-style precursors
at 60–300s carry essentially zero directional information at this label scale.

## INFERENCE

1. At the owner scale (10–30t / 5–120s), NQ mid structure is **snapback-flavored**:
   fast counter-moves precede large moves. This aligns with FSS-4 (failed
   breakout/snapback) and with W2-0's finding that flip-FOLLOWING gross is negative
   (following fails ⇒ fading the fast move is the coherent same-coin hypothesis).
   It is NOT Roll bounce (mid is clean per I-2) and not the ±0.5pp micro-bracket
   excess (different scale, opposite sign — scale-dependent regime).
2. The distance-to-viability at +24/−8 and +32/−10 (~7–9pp) is plausibly within reach
   of a contrarian trigger whose univariate separation is this strong. Must be tested
   FORWARD as a preregistered rule — the census conditional P(drop|move) does not equal
   the rule's P(move|drop).
3. HYPOTHESIS (for W3): "after a fast 10–30s counter-move of ~8–16t, entering toward
   the snapback with a large asymmetric bracket clears break-even under C1."

## Caveats (binding)

- mid_high/mid_low are quote-mid extremes; fleeting-flicker inflation is possible though
  small relative to 20–32t thresholds. Candidate rules get tick-stream re-evaluation
  before any promotion.
- 1s barrier evaluation uses the conservative same-second-ambiguity→adverse rule.
- Discovery subset only (37 sessions, 2025-08→2026-05, high-vol regime); nothing here is
  OOS; day-clustered CIs with 37 clusters.
- Label saturation at small M means "conditioning on any move" ≈ "conditioning on time":
  states must be judged by DIRECTIONAL lift, not by opportunity presence.
