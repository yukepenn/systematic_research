# LEV01 — leverage-effect volatility asymmetry: real market-structure finding, refuted
trade-level mechanism, suggestive regime-level connection

**Disposition: DIAGNOSTIC COMPLETE, no candidate constructed.** Three distinct results, each
with a different confidence level — reported plainly rather than blended into one verdict.

## Test 1 — does NQ exhibit the leverage effect? **CONFIRMED, robust**

Engle-Ng-style sign-asymmetry regression (session-level, canonical window, n=1,130 usable
sessions): forward volatility change (mean `sigma460` over the next 5 sessions minus current)
regressed on the trailing session's ATR-normalized return plus an interaction with a
negative-return dummy.

| term | coef | se | t |
|---|---:|---:|---:|
| session_ret_atr | +0.0104 | 0.0033 | 3.19 |
| **ret_x_neg (asymmetry term)** | **−0.0281** | 0.0059 | **−4.73** |

Negative coefficient = the classic leverage-effect signature: forward volatility rises more
after a negative return than it falls after a positive return of equal magnitude. Non-parametric
corroboration: positive-return sessions show mean forward vol_change = −0.069 (vol tends to
calm down after gains); negative-return sessions show +0.084 (vol tends to rise after losses) —
opposite signs, as expected, on comparable-magnitude average returns (29.7 vs −26.2 ATR-norm
points).

**Year-by-year (correct sign in all 5 canonical years):** 2022 −0.041 (t=−4.66), 2023 −0.011
(t=−1.99, weakest), 2024 −0.015 (t=−1.55), 2025 −0.030 (t=−1.48), 2026 −0.068 (t=−2.39,
**second-strongest of all 5 years**, only 2022 is comparable). NQ's own volatility structure
genuinely exhibits the finance literature's standard leverage-effect asymmetry, and it has
been notably stronger in 2022 and 2026 than in the intervening years.

## Test 2 — does the leverage effect mechanistically explain the short/long Sharpe gap?
**REFUTED — the apparent finding was a complete sunk-P&L confound**

Initial test regressed Product-B block outcomes on post-entry volatility change (measured over
the 5 sessions following entry) interacted with a short-side dummy. Result looked compelling:
unification term coef=+258.2, **t=4.45**, cross-product-corroborated in Product A (t=3.33).

**Too-good-to-be-true gate triggered** (per this campaign's standing discipline, directly citing
`runs/U5_SOFT_WEIGHTING/REPORT.md`'s own precedent): checked whether the outcome (block P&L) and
the predictor (forward vol change) overlap in time. They do, completely: **100% of the 1,890
canonical Product-B blocks close within the SAME session-window used to measure "post-entry" vol
change** (median sessions-to-close = 0). Re-testing with a forward-ONLY outcome (P&L accrued
strictly after the vol-change measurement window ends) collapses the unification term to
**exactly 0.000** — there is no "forward" remainder left to test, because every block has already
fully resolved before the predictor variable's measurement window even completes. This is the
same class of artifact that killed U5's `vwap_disp_atr` finding, now confirmed even more starkly
(complete collapse to zero, not a partial one) for a different feature and a different family.

**Side finding, disclosed honestly (contradicts this family's own a priori assumption):** shorts
are NOT mechanically entered following negative-return sessions more than longs — the data shows
the reverse (P(prior session negative | short entry)=0.384 vs P(prior session negative | long
entry)=0.683). This campaign's trend/breakout-following construction apparently enters shorts
more often after a REBOUND session, not a continuation-down session — an interesting mechanical
fact, not investigated further here (out of this family's scope).

## Test 3 — does the STRENGTH of the leverage effect track U7's loss-severity finding across
calendar years? **Suggestive, small-sample (n=5), methodologically clean, NOT proof**

Test 1's own year-by-year asymmetry coefficients and U7's own independently-derived big-loser
severity figures (`runs/U7_2026_TIMING_REGIME/REPORT.md` — both series computed from entirely
different underlying data: session-level price/volatility here, trade-level loss outcomes
there, so this comparison is not self-referential or confounded the way Test 2 was):

| year | leverage-effect asymmetry coef | big-loser mean severity ($) |
|---|---:|---:|
| 2022 | −0.041 | −1,712 |
| 2023 | −0.011 (weakest) | −1,062 (mildest) |
| 2024 | −0.015 | −1,324 |
| 2025 | −0.030 | −1,800 |
| 2026 | −0.068 (strongest) | −2,432 (worst) |

Spearman correlation across these 5 year-level pairs: **ρ=0.90, p=0.037**. Both series hit their
minimum in 2023 and their maximum in 2026, with a consistent rise in between. **This is
suggestive corroborating evidence for the literature-motivated mechanism** (a strengthening
leverage effect coinciding with, and plausibly contributing to, the rising loss severity U7
documented) — but n=5 is a genuinely small sample for any correlation, and this cannot
distinguish "the leverage effect strengthening CAUSES worse loss severity" from "both series
independently reflect the same broader 2022-2026 market regime" (which external literature —
`research/system_master/LITERATURE_SCOUT_20260809.md` — already independently corroborates as a
real, market-wide whipsaw regime for trend-followers in 2024-2025, not specific to this system).

## Right-tail / chronology / redundancy

Test 1's finding is a market-STRUCTURE fact (about NQ's own volatility, not about any specific
trade), so a right-tail check in the usual sense doesn't apply — there is no filter being
proposed. Test 2's finding is refuted outright, so its own right-tail properties are moot. Test
3's small-n year-level correlation has no meaningful right-tail decomposition at n=5. Chronology
is Test 1's own year-by-year table (correct sign every year) and Test 3's own construction (a
year-level comparison by definition).

## Verdict

**No candidate constructed — none was ever in scope for this diagnostic-only run.** The honest
summary: NQ genuinely exhibits the leverage effect (a real, externally-grounded market-structure
fact, robust across 5 years), but the SPECIFIC trade-level mechanism this family hypothesized to
unify short-side weakness with the leverage effect is REFUTED by a clean, complete confound
collapse — an important methodological result in its own right, demonstrating the too-good-to-
be-true gate catching a cross-product-corroborated, seemingly strong (t=4.45/3.33) finding before
it could be mistaken for real. What survives is a more modest, regime-level (not trade-
actionable) suggestive connection between leverage-effect strength and loss severity across
calendar years — worth keeping in mind as context for future waves, but not itself a construction
candidate, and explicitly not strong enough evidence (n=5) to build anything on. Product A and
Product B remain unchanged.
