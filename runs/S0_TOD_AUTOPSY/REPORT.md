# S0_TOD_AUTOPSY — RESULTS

Run against `spec.yaml` (frozen, committed `3a21a82`, BEFORE `W19R1_SELECTIVITY` was executed or
read, per owner instruction that S0's design must carry zero hindsight from W19R1's P&L). Purely
descriptive — no gate, no verdict, no promotion. Code: `src/run.py`.

## Process note: a real bug, caught by the mandatory self-check, fixed, not hidden

The first run failed its own reconciliation self-check (spec §4 requires block totals to match
known full-sample figures exactly): 1,095 bars were silently unassigned to any block. Root cause:
bars timestamped exactly 17:00 (bar-end convention → the session-close/forced-flatten bar, one per
normal-length session) satisfied neither `EVENING_ASIA`'s wrap condition nor `CLOSING_APPROACH`'s
exclusive upper bound — a genuine gap in the naive `[a,b)` partition at the wraparound seam. Fixed
by remapping to minutes-elapsed-since-session-open (a non-wrapping 0–1380 scale) with an inclusive
upper bound only on the final block. **No boundary was moved to change any P&L outcome** — this is
a partition-coverage fix, not a re-fit; the fix is in the code with a dated comment, not hidden.
Post-fix: net P&L, member-flip count, and bar count all reconcile exactly (`reconciliation_selfcheck.json`).

## SOLAR_E10 — full-ETH incumbent, by block

| block | window (ET) | net P&L | share | dd-episode | worst-5% days | CDaR days | flip share |
|---|---|---:|---:|---:|---:|---:|---:|
| EVENING_ASIA | 18:00–02:00 | −$5,658 | −4.8% | −$5,150 | −$21,185 | −$2,484 | 12.4% |
| **EUROPE_PREUS** | **02:00–08:00** | **−$28,914** | **−24.3%** | **−$48,939** | −$37,942 | −$5,488 | 16.6% |
| US_OPEN | 08:00–10:00 | +$46,197 | +38.8% | −$3,196 | −$43,808 | −$10,248 | 17.2% |
| LATE_MORNING | 10:00–12:00 | +$49,671 | +41.7% | −$42,426 | **−$46,381** | **−$12,028** | **22.7%** |
| LUNCH | 12:00–13:30 | +$1,001 | +0.8% | −$35,934 | −$9,443 | −$4,040 | 10.3% |
| **AFTERNOON** | **13:30–15:45** | **+$53,330** | **+44.8%** | **+$11,324** | −$35,059 | −$3,194 | 15.0% |
| CLOSING_APPROACH | 15:45–17:00 | +$3,382 | +2.8% | −$35,887 | −$19,242 | −$6,335 | 5.8% |

Sums reconcile exactly to the full-sample control (net $119,008.90, 58,701 member flips, 519,714
bars — `reconciliation_selfcheck.json`, `PASS`).

### Three structural findings (descriptive; none of these is a rule, none is promoted)

**1. EUROPE_PREUS (02:00–08:00 ET) is the single worst block by every loss measure in this table** —
worst net P&L (−$28,914, a quarter of total net given back), and by far the worst drawdown-episode
contributor (−$48,939, more than a third larger in magnitude than the next worst). This refines,
rather than confirms, D4's Wave-18 finding: D4's coarser 3-bucket split flagged EVENING
(18:00–23:59) as NQ's worst cohort. At 7-block granularity, the damage is concentrated later, in
the low-liquidity pre-US window, not the immediate post-close reopen — EVENING_ASIA here (which
covers D4's EVENING plus the first part of its OVERNIGHT bucket) is only mildly negative. A
directional-change detector losing money specifically in the lowest-liquidity, choppiest part of
the global session (Asia close through pre-London) is a market-structure-plausible mechanism, not
merely a P&L pattern — this is the strongest single candidate boundary for S2's Arm A/B.

**2. LATE_MORNING (10:00–12:00 ET) is simultaneously the best-average and highest-tail-risk block.**
Best net P&L (+$49,671) but also the single worst worst-5%-days and CDaR-episode contributor, and
the highest member-flip share (22.7% of all flips in 8.7% of the bars) — the most actively-traded
block by a wide margin. High average return co-located with high tail contribution is the
signature of a high-conviction, high-variance block, not an unambiguously "good" one; a SelTime
rule that simply favors LATE_MORNING would buy both the best average day and a disproportionate
share of the worst days.

**3. AFTERNOON (13:30–15:45 ET) is the largest raw net contributor AND the only block with a
positive drawdown-episode contribution** (+$11,324 — every other block is negative during the
episodes that make up the sample's own maxDD path). This is the closest thing in the partition to
a block that is both profitable and genuinely defensive, not merely less bad.

## BMOM — trade-level, entry-time attribution (different object type; see spec §3 note)

| block | entries | net P&L | share | win rate |
|---|---:|---:|---:|---|
| EVENING_ASIA | 0 | $0 | — | — |
| EUROPE_PREUS | 0 | $0 | — | — |
| US_OPEN | 895 | +$292,093 | **91.5%** | 50.8% |
| LATE_MORNING | 300 | +$81,197 | 25.4% | 53.7% |
| LUNCH | 57 | −$11,364 | −3.6% | 50.9% |
| **AFTERNOON** | 73 | **−$44,253** | **−13.9%** | 43.8% |
| CLOSING_APPROACH | 8 | +$1,525 | 0.5% | 62.5% |

**B-MOM never enters outside RTH-adjacent hours** (zero entries before 08:00 ET — a mechanical
property of its own construction, not a finding), and **91.5% of its entire net P&L comes from
US_OPEN alone**. Sharpest first-pass divergence from Solar: **AFTERNOON is B-MOM's single worst
block (−$44,253) and Solar's single best (+$53,330)** — the two engines' time-of-day P&L structure
looks close to opposite in this one block. This is exactly the kind of pattern S2's Arm B
(sleeve-by-time eligibility) exists to test formally with proper chronology; it is reported here
as a first-pass descriptive observation, not evidence, and must not be converted into a rule from
this run alone (spec §0, explicitly forbidden).

## Day-only overlay context (Solar leg only, descriptive approximation — not a Track-E parity claim)

| block | full-ETH net | day-only net | Δ |
|---|---:|---:|---:|
| CLOSING_APPROACH | +$3,382 | −$11,875 | **−$15,257** |
| EVENING_ASIA | −$5,658 | +$1,404 | +$7,062 |
| EUROPE_PREUS | −$28,914 | −$27,558 | +$1,356 |
| US_OPEN..AFTERNOON | ≈unchanged | ≈unchanged | ≈$0 |

The C4 day-only overlay's forced-flat/no-new-entry window has a real, quantified cost concentrated
almost entirely in CLOSING_APPROACH (−$15,257) — this is the price of the non-negotiable margin
requirement (C3), not an inefficiency to trade around, and is reported for completeness, not as an
actionable finding.

## Retained for visualization only (per spec, explicitly non-actionable)

`out/slot_profile_3min.csv` — 480-slot net P&L / bar-count profile. Not read as a selection
criterion here; available for S2's diagnostics if S2 needs a visual, not a rule source.

## What this hands to S2

1. **EUROPE_PREUS (02:00–08:00 ET) is the strongest single candidate for an entry-eligibility test**
   (S2 Arm A) — worst on both net P&L and drawdown-episode contribution, market-structure
   plausible (lowest global liquidity window), and a genuine refinement of D4 rather than a
   restatement of it.
2. **LATE_MORNING must not be naively favored** by any S2 construction without accounting for its
   disproportionate tail contribution — a rule that simply increases exposure there would be
   selecting the best average day and the worst tail day at once.
3. **Solar/B-MOM's AFTERNOON divergence is S2 Arm B's natural first test case**, to be evaluated
   with proper chronology gates, not adopted from this descriptive pass.
