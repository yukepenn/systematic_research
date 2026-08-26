# WE_W30 — WHERE PRODUCTION IS LOST · REPORT

Objective corrected by amendment 1: **maximise profit**, not a capture ratio. Primary unit is
points/session (exposure- and price-neutral).

## Q1 — we are in the market 12.9 % of the time

| object | % bars in position | % sessions traded | pts/session | **pts per bar in position** |
|---|---|---|---|---|
| **E5 box (1 contract)** | **12.90 %** | 60.0 % | 10.62 | **0.0603** |
| S1 | 60.73 % | 99.1 % | 14.04 | 0.0169 |
| either | 64.24 % | — | — | — |

**E5's edge density is 3.6× S1's, on one fifth of the time.** That is the structural reason for
~10 points/session: not a weak edge, a rarely-expressed one.

## Q2 — 95.5 % of the absence is the vote itself

| cause of not holding | share of absent bars |
|---|---|
| **vote below 0.5** | **95.5 %** |
| session box already fired | 4.1 % |
| range throttle | 0.2 % |
| wanted in, between fills | 0.1 % |

But lowering the threshold does **not** buy production: W22 measured vote ≥ 0.30 at $1,112/week
against ≥ 0.50's $1,118 with a worse tail. **The bars between 0.3 and 0.5 agreement are not
profitable** — the absence is protective, not wasteful. Time-in-market must be bought
elsewhere.

## Q3 — CONCURRENT INDEPENDENT SLEEVES: the production lever that works

Four member-sets run as **separate sleeves**, each with its own entries, exits and session box
(this is not pyramiding one trade — that was rejected three times as leverage):

| object | contracts | **pts/session** | weekly | % weeks + | worst week | Sharpe |
|---|---|---|---|---|---|---|
| E5 box | 1 | 10.62 | $1,060 | 59.1 % | −$7,487 | 0.305 |
| 4 member sleeves | 4 | 37.97 | $3,771 | 60.3 % | −$32,358 | 0.268 |
| **4 member sleeves + S1** | 5 | **52.01** | **$5,140** | 57.6 % | **−$29,767** | **0.298** |

**It is not merely leverage.** Five copies of the single sleeve would give $5,300/week with a
worst week of −$37,435; the five *independent* sleeves give $5,140 with **−$29,767** — the same
Sharpe at **22 % better efficiency per unit of tail**, because the sleeves enter and exit at
different times.

Translation for the stated goal: **$5,140/week at 5 contracts today; ~$10,000/week needs ~10
contracts with a worst week near −$60,000.** That is an exposure decision with an explicit
price, not a research claim.

## Q4 — the ceiling decomposition (bound, not target)

| | pts/session |
|---|---|
| our object today | 10.6 |
| our entries/exits **with perfect knowledge of each session's direction** | **31.6** |
| perfect-foresight single trade | 321.1 |

**Perfect direction is worth only 3×.** The remaining ~10× lives in time-in-market and exit
geometry, not in knowing which way the day goes. This reorders the research queue: direction
prediction (already failed in W07) is not where the production is.

## What this wave changes
The production question is now precise: **raise time-in-market at E5's density, or raise
density at S1's time.** Concurrency (Q3) buys the first at a proportional exposure cost; the
open research question is whether any signal in our own repository raises either term without
paying for it linearly.
