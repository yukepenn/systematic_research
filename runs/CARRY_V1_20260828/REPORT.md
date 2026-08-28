# CARRY_V1 — **FAILED C6 and C7. CLOSED.** The "multi-sector carry premium" is one pair.

| | |
|---|---|
| **verdict** | ❌ **DEVELOPMENT FAILED — `CARRY_V1` CLOSED.** Validation and final holdout **NOT READ** |
| spec committed | `82ecb58`, **before** any carry P&L |
| gates | **6 of 8 PASS** · **C6 FAIL (84.1 % vs 40 %)** · **C7 FAIL (98.5 % vs 50 %)** |
| headline that does **not** count | net **$71,413**, Sharpe **0.719**, **7 of 9** positive years, cost drag **7.9 %** |
| **why it does not count** | **SI alone is 84.1 % of positive root contribution; metals is 98.5 % of positive sector contribution.** The other three sectors sum to **$240** of a $71,413 net |

> ### This is the failure mode C6/C7 were written for, and it is the tempting kind. Sharpe 0.72,
> ### 7 of 9 positive years, 7.9 % cost drag and a clean two-sided causality probe are all genuinely
> ### good numbers. **They describe a silver-versus-gold pair trade wearing a four-sector costume.**

---

## 1. Result

| arm | gross | cost | net | Sharpe |
|---|---:|---:|---:|---:|
| **PRIMARY (1 tick)** | $77,578 | $6,165 | **$71,413** | **0.719** |
| **STRESS (2 ticks)** | $77,578 | $11,219 | $66,359 | 0.668 |

**Cost drag 7.9 %**, mean daily turnover 0.1198 units — a genuinely cheap strategy, and the sharpest
contrast with TSMOM V1, which was gross-positive and economically dead at **47.2 %** drag.
421 rebalances, 3,421 root-weeks, mean **3.30** live sectors.

| gate | observed | |
|---|---:|---|
| C1 PRIMARY net > 0 | $71,413 | PASS |
| C2 Sharpe ≥ 0.30 | **0.719** | PASS |
| C3 ≥ 6 of 9 positive years | **7 of 9** | PASS |
| C4 STRESS net > 0 | $66,359 | PASS |
| C5 cost drag ≤ 50 % | **7.9 %** | PASS |
| **C6 top root ≤ 40 %** | **84.1 %** | ⛔ **FAIL** |
| **C7 top sector ≤ 50 %** | **98.5 %** | ⛔ **FAIL** |
| C8 not a disguised long | signed equity exposure **−0.006** | PASS |
| causality, **both** clauses | future 0.000e+00 · past 2.5e−01 | PASS |

## 2. Where the money actually came from

| sector | net | | root | net |
|---|---:|---|---|---:|
| **metals** | **$71,174** | | **SI** | **$73,058** |
| ags | $852 | | ZN | $12,210 |
| rates | $212 | | ZL · ZW · YM | $1,378 · $92 · $88 |
| equity_index | −$824 | | ZC · ZM · ES · GC | −$243 · −$374 · −$912 · −$1,884 |
| | | | **ZB** | **−$11,998** |

**Six of ten roots lost money.** `ZB −$11,998` is close to the mirror of `ZN +$12,210`, which is
what a two-root sector produces by construction.

## 3. The causality probe passed — and it had teeth this time

| clause | observed | |
|---|---:|---|
| corrupt **future** (≥ t) carry → weights must **not** move | **0.000e+00** | PASS |
| corrupt **past** (< t) carry → weights **must** move | **2.5e−01** | PASS |

The second clause is the one that matters and it is why this was written two-sided. **A one-sided
probe cannot distinguish a causal engine from one that ignores its inputs entirely** — and it would
have passed happily on an engine that had silently stopped reading the curve. The basis-invariance
and no-roll telescoping unit tests both passed at `0.000e+00` as well, so the roll is not leaking
the futures basis into P&L.

## 4. ⚠️ Integrity check on SI before accepting the number

A single root carrying 84 % of a result is exactly the shape of a data defect, so it was checked
rather than assumed. **It is not an artifact:**

| check | finding |
|---|---|
| top-10 largest SI days | contribute **−49.2 %** of SI's net — the biggest days are *losses* |
| largest single day | **−10.2 %** of net. No day makes the result |
| yearly spread | 2009 $10.1k · **2010 $30.5k** · 2012 $12.5k · 2014 $9.9k · 2017 $13.1k, with 2016 and 2018 negative |
| slope sanity | median **−0.0225 $/oz/month**, range [−0.090, +0.063]. Silver in contango, correct sign and plausible magnitude; **zero** days above 1.0 $/oz/month |

So the effect is real within this window and this specification. **It is still not promotable** — it
is one root out of ten searched, and the gate that rejects it was fixed in advance precisely so that
"but the concentrated thing is real" could not become an argument.

## 5. A design finding worth carrying forward — **n = 2 degenerates the rank**

With `n_sector = 2` the centred rank `2(i−1)/(n−1) − 1` can only take the values **−1 and +1**.
**Three of the four sectors — equity_index, rates, metals — have exactly two roots**, so in those
sectors "relative carry" is not a graded tilt at all: it is a **binary long-one / short-the-other
switch at full weight**, flipping whenever the two carries cross. Only ags, with four roots,
produces intermediate weights.

That is a **structural property of this universe**, not a tuning parameter, and it was visible in
`CARRY00`'s coverage table before the P&L existed — it simply was not reasoned through. Any future
curve work on this substrate must either secure ≥3 roots per sector or use a construction that does
not degenerate at n = 2.

> **This does not rescue anything and is not offered as one.** It explains the mechanism of the
> concentration; it does not change that the preregistered gates failed.

## 6. What is now forbidden, and it is worth naming explicitly

SPEC §10 pre-committed the list, and after a result like this every one of them is tempting:

> ~~monthly rebalance~~ · ~~2-week rebalance~~ · ~~3-month slope~~ · ~~second-vs-third contract~~ ·
> ~~long-only~~ · ~~commodity-only~~ · ~~drop metals~~ · ~~drop ags~~ · ~~thresholded carry~~ ·
> ~~blended carry/trend~~ · ~~a second rank transform~~ · ~~metals-only carry~~ · ~~SI/GC pair~~

**Especially "metals-only".** The data has just been shown to contain a profitable silver-gold curve
relationship in 2009–2018. Fitting a strategy to that now would be selecting a subpopulation *after*
seeing which subpopulation won, on the same data, and calling the result a discovery. It would carry
a multiplicity of at least ten and an unpayable selection debt, and this repo has a rule against
exactly it.

## 7. Status

| | |
|---|---|
| **evidence class** | **DEVELOPMENT-ONLY, DISCOVERY-CONSUMED.** Carry is **CLOSED at this specification** |
| **not closed** | curve/term-structure information **in general**, other maturity pairs, other normalisations, a universe with ≥3 roots per sector. This tested **one** frozen object |
| **pools consumed** | 2009–2018 carry development |
| **pools NOT consumed** | **2019–2022 validation and 2023–2026-05-30 final holdout were never read** — the runner truncates the panel at 2019-01-01 and asserts it |
| seal | **untouched** |
| next | **ES ↔ NQ sub-minute**, per SPEC §10's fixed continuation |
