# D_WINNER_AUTOPSY -- RESULTS

Descriptive only, per frozen spec.yaml. Reference system: SOLAR_E10 control (same object used
as control throughout S0/S1/S2/M3/M4/P4). Zigzag threshold (100 pts) fixed from a swing-count
diagnostic alone, before any position/PnL data was consulted. Code: `src/run.py`.

## D-WINNER-1: missed winners -- the system already captures most of the big ones

3,835 swings >=100 pts total in the dev window.

| taxonomy | top 50 (share) | top 200 (share) |
|---|---:|---:|
| CAPTURED_FULL | 18 (36%) | 60 (30%) |
| CAPTURED_PARTIAL | 25 (50%) | 102 (51%) |
| MISSED_FLAT | 5 (10%) | 18 (9%) |
| MISSED_WRONG_SIDE | 0 (0%) | 11 (5.5%) |
| MIXED_OTHER | 2 (4%) | 9 (4.5%) |

**86% of the top-50 swings and 81% of the top-200 swings are captured full or partial** -- the
incumbent ensemble is not leaving the largest moves on the table in any wholesale way. The
system's own realized P&L during the top-200 swing spans sums to **$507,812.55** (i.e. it is
net strongly positive exactly where the biggest moves happen, consistent with a real trend-
following edge, not a lucky-timing artifact). MISSED_WRONG_SIDE is rare (0/50, 11/200 = 5.5%)
and MISSED_FLAT is the larger of the two miss categories (18/200 = 9%) -- when the system does
miss a big swing, it is usually because it was flat/undecided, not because it was leaning the
wrong way. 11 wrong-side events and 18 flat-miss events over 4.5 years is too small a population
to support a new gated hypothesis without material overfitting risk -- **no new construction is
proposed from D-WINNER-1.**

## D-WINNER-2: give-back -- small on average, but strongly duration-dependent

16,383 total winning position-blocks; top decile (1,638 blocks) by net P&L:

| statistic | give-back ratio |
|---|---:|
| mean | 10.5% |
| median | **0.0%** |
| p90 | 42.1% |

Over half of top-decile winners are exited at or essentially at their peak open profit (median
give-back = 0). The mean is pulled up by a tail: p90 = 42%. Breaking this down by how long the
block was held:

| holding duration | mean give-back |
|---|---:|
| short (<=5 bars, <=15 min) | 1.7% |
| medium (6-20 bars) | 9.8% |
| long (>20 bars, >1 hour) | **22.3%** |

**Give-back is heavily concentrated in the longest-held winners** -- a real, structurally
plausible finding (trends that run long enough to become top-decile winners also run long enough
to round-trip a meaningful fraction of their open profit before the system's exit condition
fires). This is a genuine candidate mechanism for a FUTURE wave (an asymmetric, profit-only
trim/trail rule for long-held winners -- distinct from the closed loss-triggered de-risking
family, since it never conditions on a prior loss). It is **not** one of the 8 named families
in the FINAL OPTIMIZATION DIRECTIVE, so per the directive's own bounding discipline (no
open-ended new hypothesis spawning this wave, "no more open-ended research queue" at close-out),
**it is disclosed here and in the final owner report as an identified-but-untested open axis,
not spun into a new gated family this wave.**

## Disposition

Diagnostic complete, both sub-questions answered with disclosed, non-outcome-fit thresholds.
No promotion, no new family opened. D-WINNER-1 finds no material missed-winner problem worth
chasing (population too small, structurally rare). D-WINNER-2 finds a real but out-of-scope-for-
this-wave give-back pattern, carried forward as a note for future work, not acted on now.
