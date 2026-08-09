# ENGINE3_SLATE5_CROSSMARKET -- RESULTS

Frozen spec.yaml implemented exactly, no threshold touched after seeing a result. Reused slate
4's committed `merged_3m_dev.parquet` (515,306 bars, 1,132 sessions) verbatim -- no substrate
rebuild. Code: `src/run.py`.

## Candidate 1 -- Europe (YM) -> US (NQ) session lead: FAIL

| YMZ | N | mean | t_nw |
|---:|---:|---:|---:|
| 1.00 | 46 | $438.57 | 0.80 |
| **1.25 (center)** | **21** | **$445.40** | **1.00** |
| 1.50 | 13 | $302.56 | 0.61 |

Directionally positive at all 3 grid cells (a mild plateau in sign, at least), but every cell
fails the N>=40 power floor and t_nw never approaches 2 -- a mild, statistically unconvincing
effect, not evidence of a real Europe-to-US information-diffusion lead worth trading.

## Candidate 2 -- NDX-100 annual special-rebalance: FAIL (power floor, as pre-registered)

Only 4 December-3rd-Friday events fall in the dev window (2022-2025) -- exactly the N<=4
outcome the spec pre-registered before the code ran. Mean net **-$558.11**, t_nw -0.14. This
was run to formally clear the ledger's "D1 rank 4" item, not because it had a realistic chance
of passing the N>=12 floor; disclosed as a designated cheap kill in the frozen spec itself, so
this is confirmatory, not a surprise or a p-hacking risk.

## Candidate 3 -- weekend information-diffusion lag: FAIL (fails its own head-to-head control's spirit)

| series | N | mean | t_nw |
|---|---:|---:|---:|
| weekend (Fri consensus -> Mon) | 168 | -$65.73 | -0.18 |
| any-gap control (all other weekday gaps) | 665 | -$362.02 | -1.91 |

The mandatory head-to-head gate technically passes in isolation (-$65.73 > -$362.02, i.e. the
weekend effect is less negative than the generic any-gap consensus-continuation effect), but
this is not a meaningful pass: the weekend series itself is statistically indistinguishable from
zero (t_nw -0.18, N=168 well above the floor but the mean is flat) and slightly negative, not
positive. The interesting fact this run surfaces is that the ANY-GAP control itself is mildly,
though not quite significantly, negative (t_nw -1.91) -- i.e. 3-instrument consensus-agreement
gaps trend to FADE on ordinary weekday gaps, not continue, which is a different (and itself
uninteresting after this one look) finding from what was being tested. Neither series is
tradeable.

## Disposition: 3/3 FAIL. Engine-3 cross-market axis now 15/15 failed across 5 slates.

No candidate reaches the inherited promotion standard (positive CI_lo, t_nw>=2, N floor,
plateau, WF chronology) -- complementarity-vs-champion was not evaluated for any candidate since
none cleared the primary gates to warrant it. Per the frozen spec's own bounding clause, **no
slate 6 is opened this wave.** The NQ-only and now the first-round cross-market Engine-3 search
spaces are both exhausted under this campaign's remaining named-family budget; a materially new
data source (e.g. options/dealer-positioning data, which this repo does not have) or a genuinely
new mechanism class -- not a re-spec of any of these 15 -- would be required before a future
attempt. No red team required (clean negative across all 3, no promotion proposed).
