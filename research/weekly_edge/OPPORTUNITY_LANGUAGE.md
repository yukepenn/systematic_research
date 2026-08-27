# OPPORTUNITY LANGUAGE — the four levels, and which one every number belongs to

_Binding as of **2026-08-27** (owner directive V4 amendment, §2). Every capture, ceiling or
"opportunity" figure produced in campaign #7 must name its level. A number without a level is not
quotable. This file governs `CURRENT_BASELINE.md`, `runs/WE_W99_CAPTURE2/`,
`runs/WE_W103_CONSOLIDATE/` and everything after._

---

## The hierarchy

| level | what it knows | what it respects | what it is |
|---|---|---|---|
| **1. `EX_POST_PATH_ORACLE`** | the entire future path | nothing — unlimited turnover | a **diagnostic only**. W99's `oracle1` (best single swing per segment, 841.7 pts/session) and `zigzag10` live here. Ratios to this number are not capture rates; W50's "4.46 % capture" was one and it is retired. |
| **2. `EX_POST_EXECUTION_FEASIBLE_ORACLE`** | **the future direction of each segment** | turnover (one entry, one exit per segment) and the minute's own friction | **an UPPER BOUND after execution constraints. NOT causally available money.** W99b's `SIGN_ORACLE` lives here — and *only* here. |
| **3. `CAUSAL_MODEL_FRONTIER`** | only information available at decision time | turnover and friction | **UNKNOWN and unknowable in general.** It is bounded *below* by any real causal rule we can build and *above* by level 2. Nothing in this repo measures it directly. |
| **4. `REAL_SYSTEM_CAPTURE`** | what our objects actually knew | everything | what the base actually earned. |

## ⚠️ The rule this file exists to enforce

> ### `SIGN_ORACLE` KNOWS THE FUTURE SEGMENT DIRECTION.
> ### It is **level 2**. It must **never** be called causal, executable-in-advance, available,
> ### or "opportunity" without the qualifier. Phrases like *"$1,744/session available in MORN"*
> ### are wrong on their own; the correct form is
> ### *"$1,744/session of EX_POST_EXECUTION_FEASIBLE_ORACLE in MORN"*.

The gap between level 2 and level 4 is **not** money we failed to collect. It is money that would
have been collectable *if we had known the direction*, which is the entire problem.

## What W99 actually established, stated in a form that survives

The durable, quotable finding from W99/W99b is **not** the ceiling. It is the **bar**:

> **For the particular one-trade-per-segment geometry — one entry at the segment's open, one exit
> at its close, one contract — break-even directional accuracy is approximately 50.5 %–51.4 %,
> with MORN at approximately 50.48 %.**
>
> `p* = ½ · (1 + cost / E|net move|)`

### The three qualifiers that must travel with it

1. **It is geometry-specific.** It applies to *that* trade shape. A strategy that turns over ten
   times per segment faces a bar ten times further from 0.5; one that holds three days faces a
   lower one. **Do not generalise p\* to all strategy geometries.**
2. **It assumes move size is independent of being right.** A forecaster systematically right on
   small moves and wrong on large ones faces a higher real bar. p\* is a floor on the requirement.
3. **It is measured on 2022-07 → 2026-08.** E|move| has risen 83 % over that window, so p\* is not
   a constant of nature; it falls as volatility rises.

## Restating the current ledger in the correct language

From `runs/WE_W103_CONSOLIDATE/` — the base takes 0.2 %–5.1 % **of level 2**, not of anything
causally available:

| segment | `EX_POST_EXECUTION_FEASIBLE_ORACLE` $/session | `REAL_SYSTEM_CAPTURE` | ratio | p\* (that geometry) |
|---|---|---|---|---|
| MORN | $1,744 | $78 | 4.4 % | 0.5048 |
| ON_EU | $1,224 | $18 | 1.5 % | 0.5078 |
| MID | $1,197 | $19 | 1.6 % | 0.5059 |
| AFT | $1,170 | $3 | 0.3 % | 0.5058 |
| ON_ASIA | $1,026 | $39 | 3.8 % | 0.5139 |

**The right reading of that table** is not "we are leaving 95 % on the table". It is:
*a perfect once-a-segment direction call would have earned this much after friction, we earn a few
per cent of it, and the level-3 frontier between those two numbers has never been measured.*

W104 gives one datum on where level 3 sits: a real causal rule at the RTH open
(`XM_CONFLICT`, 54.6 % hit) earns **$560/trade** where level 2 for that geometry is $2,683 of
E|move| — i.e. a genuinely good causal signal recovers **on the order of 20 %** of the
execution-feasible oracle for its own trade shape. That is the only calibration of level 3 this
campaign has, it comes from one object, and it should not be treated as a constant either.
