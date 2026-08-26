# WE_W31 — SESSION-OPEN RESTORE · REPORT

**FALSIFIER FIRED, decisively — and it produced the campaign's most important mechanistic
finding.**

| arm | % bars in position | **pts/session** | **pts per bar in position** | $/trade | Sharpe |
|---|---|---|---|---|---|
| **R0 baseline** | 12.90 % | **10.62** | **0.0603** | $103.9 | **0.305** |
| R1 restore | 20.68 % | 0.70 | 0.0025 (**4 %** of base) | $4.0 | 0.018 |
| R2 restore + validity check | 20.68 % | 0.70 | 0.0025 | $4.0 | 0.018 |
| R3 Type-3 strengthen entries | 23.90 % | 3.93 | 0.0120 (20 %) | $18.4 | 0.095 |
| R4 both | 23.95 % | 3.66 | 0.0112 (19 %) | $15.6 | 0.089 |

Restoring exposure does exactly what the mining predicted to **time in market** (12.9 % →
20.7–24.0 %) and the opposite of what was hoped to **production**: points per session fall from
10.62 to 0.70–3.93 because per-bar density collapses to 4–20 % of baseline.

## The finding: the edge is in the FLIP EVENT, not the trend STATE

Holding long *because the ratchet's leg is nominally up* earns **0.0025 points per bar**.
Holding long *because the ratchet has just flipped up* earns **0.0603** — **24×**. The state is
a lagging descriptor; the flip is the event that carries information.

This unifies a result that had stood alone since W25: **Donchian breakout — a STATE rule
("close above the N-bar high") — loses −0.34 on the same instrument where the ratchet earns.**
Both are "trend following"; the difference is event versus state. Two independent negatives now
have one explanation.

## What it closes

W30 measured that we are in the market only 12.9 % of the time and asked whether that absence
could be bought back. **It cannot — not with this signal.** The absence is not a defect to be
engineered away; it is the edge's natural rarity. Any future proposal of the form "hold the
position longer / re-enter sooner / stay in the trend" is answered by this table unless it
changes *where flips occur* rather than *whether state is held*.

## Correction to the prior evidence

The mining cited campaign #1's `OTR_S1_ARBITRATION` (+42 % trades at unchanged expectancy when
Type-3 was admitted). That result was measured on a **different object**: a single 2023-era
Solar strategy with its own wrapper, not a 32-configuration vote with a throttle, a delta gate
and a session box. Inside a vote, restoring members raises the voting *fraction* toward the
64 % up-leg share, so the portfolio holds through every sideways stretch the ratchet has not
yet flipped out of. **The prior did not transfer, and the reason is structural.**

## Still live from the mining, because they change WHERE flips happen
- TOD-normalised threshold clock (measured 19.95× intraday spread on our own substrate;
  campaign #1 H-014 gave +0.728 Sharpe at p = 0.009)
- Multi-clock members (campaign #1: 3-min $27.18/trade vs 1-min $15.76, daily Sharpe 1.08 vs
  0.63; mixed 1m+3m ensemble 0.786 vs 0.717)
