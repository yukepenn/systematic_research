# WE_W22 — TAIL · REPORT

## ADOPTED: the session halt on the vote — the campaign's best single improvement

| variant | wk mean | % pos | **worst week** | **Sharpe** |
|---|---|---|---|---|
| E5 base (vote ≥0.5, 1 contract) | $1,118 | 59.6 % | −$17,440 | 0.214 |
| **E5 + session halt $1,300** | $1,131 | 57.6 % | **−$8,769** | **0.273** |
| E5 + session halt $2,600 | $1,028 | 57.1 % | −$11,952 | 0.220 |
| E5+S1 (reference, ≤2) | $2,495 | 58.0 % | −$26,850 | 0.241 |
| **E5halt1300 + S1** | $2,508 | 59.5 % | **−$21,514** | **0.259** |
| E5+S1+ASIA (≤3) | $2,662 | 60.0 % | −$27,375 | 0.251 |

**The halt cuts the worst week in half AND raises Sharpe.** Both adoption conditions are met
with room to spare, which almost never happens — every other tail mechanism in this campaign
traded Sharpe for tail. This is the W09 lesson (truncate the loss-accumulation process at the
session level) applied to the object that survived the W21 audit.

## V1 threshold curve is FLAT — the 0.5 result was not luck

| threshold | 0.30 | 0.40 | **0.50** | 0.60 | 0.70 | 0.80 |
|---|---|---|---|---|---|---|
| Sharpe | 0.202 | 0.214 | **0.214** | 0.200 | 0.200 | 0.222 |

No peak at the chosen value; the plateau spans 0.40–0.50 and the extremes lose little.

## V2 conviction sizing: LEVERAGE AGAIN (rejected)
Size 2 on ≥75 % agreement nearly doubles the money ($1,999/wk) and nearly doubles the tail
(−$42,632) while Sharpe *falls* to 0.207. Third time this pattern has appeared (W06 pyramid,
W10 range-sizing, now vote-conviction). Recorded as a standing law of this system:
**any exposure rule that scales with a signal we already trade is leverage, not edge.**

## V5 concentration cap: honest no-op
E5 is long-only 1 contract and S1 is ±1, so the pair already caps at 2 long; the rule binds
only in the reference case. Reported as a no-op rather than fabricated as a finding.

## Current best objects
- **1 contract**: `E5 + session halt $1,300` — $1,131/wk, 57.6 % weeks, worst −$8,769,
  Sharpe 0.273, no runtime parameter selection.
- **≤2 contracts**: `E5halt1300 + S1` — $2,508/wk, 59.5 % weeks, worst −$21,514, Sharpe 0.259.
