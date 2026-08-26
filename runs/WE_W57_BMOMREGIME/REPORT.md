# WE_W57 — B-MOM TRACKS A CALENDAR, NOT A REGIME · REPORT

Preregistered; amendment 1 **tightened** the verdict rule before it was applied, because the
first version of my verdict code under-implemented my own spec. Diagnostic wave, nothing
adopted.

**VERDICT: no measurable regime variable separates B-MOM's eras. W56's falsifier fires.**

---

## 1. What was at stake

W56 measured that **P1 + B-MOM at w = 0.30 pays $2,114/week against P1's $1,475 (+43 %) at the
same $20,245 max drawdown, with a slightly better drawdown distribution.** The arithmetic is
sound. Whether it is *available* depends entirely on whether B-MOM's edge is real:

| B-MOM | sessions | net | daily mean ± SE | t |
|---|---|---|---|---|
| 2006–2021 | 4,077 | $18,156 | $4.5 ± $16.8 | **0.27** |
| 2022–2026 | 1,122 | $319,123 | $284.4 ± $106.8 | **2.66** |

2022–2026 is B-MOM's own development sample. Charter Amendment 1 §2(b) admits a
recency-concentrated edge only if it tracks a **measurable causal regime variable** that was
also present earlier — not a date. This wave looked for one, using the 4,077 pre-2022 sessions
where the statistical power actually is.

## 2. The five candidates, and the mechanically obvious one

Every variable causal (lagged), quintiled by **trailing rank against the prior 500 sessions**,
never a full-sample quantile. B-MOM's own saved ledger was re-bucketed; no parameter touched.

| variable, top quintile | pre-2022 n | pre-2022 mean | **pre-2022 t** | post n | post mean | post t | verdict |
|---|---|---|---|---|---|---|---|
| R1 trailing 60-day RTH range (points) | 1,176 | $22 | **0.49** | 439 | $333 | 1.61 | date |
| R1b same, as % of price | 986 | −$3 | −0.08 | 243 | $485 | 1.58 | date |
| R2 price level | 2,586 | $31 | 1.41 | 600 | $326 | 2.47 | date |
| R3 intraday variance ratio | 891 | −$6 | −0.18 | 249 | $362 | 1.95 | date |
| R4 overnight-gap share of range | 971 | −$58 | −1.45 | 300 | $250 | 1.07 | date |
| R5 relative RTH volume | 750 | $84 | **2.13** | 159 | **$15** | **0.04** | date |

**Not one variable qualifies.**

### The mechanism that should have worked, measured directly

B-MOM's friction is a **fixed 2.872 ticks = $14.36 per round turn**. NQ went from a median
daily RTH range of **42.25 points pre-2022 to 259.43 points after** — a 6.1× expansion — so that
fixed friction fell from **1.70 % of the median daily range to 0.28 %**. That is a genuine,
measurable, mechanical regime change and it has exactly the shape needed to explain a
modern-only edge in a breakout rule.

**It does not rescue the pre-2022 era.** In the pre-2022 sessions with the *largest* trailing
ranges — where friction was least binding — B-MOM earned **$22/day at t = 0.49**. The obvious
mechanism was measured and it is not there.

## 3. `FACT` — the quintile structure is indistinguishable from chance

The wave is itself a 6 × 5 × 2 = 60-cell scan, so amendment 1 required a permutation
multiplicity check. B-MOM's daily P&L permuted **within era** 500 times (era means preserved,
regime alignment destroyed), bucket memberships held fixed:

| | observed | permuted |
|---|---|---|
| cells at t ≥ 1.65 | **12** | **10.6 on average**, 5th–95th pct 7–14, **p = 0.340** |

> **Twelve significant-looking cells out of sixty, against a chance expectation of eleven.**

## 4. The correction I had to make to my own verdict

The first run printed *"QUALIFYING VARIABLES: R5_volume"*. That was wrong, and the spec already
said why: it required a **mechanical coherence check** — the variable must have actually moved
between the eras — and the code implemented only the first half of the rule. R5 fails coherence
on every count: its top quintile earns pre-2022 (t = 2.13) and earns **nothing** post-2022
(t = 0.04), and its median moved by a factor of **1.02**. It is a variable whose good state is
in the *old* era; it is the opposite of an explanation for a modern-only edge.

Recorded as amendment 1 with the corrected rule, before the corrected rule was run.

## 5. What is now established

`FACT` — **no measurable regime variable in this list separates B-MOM's eras, and the quintile
structure as a whole is not distinguishable from chance.**

This does **not** prove B-MOM's edge is fake. It establishes that the evidence bar Charter
Amendment 1 §2(b) sets is **not met on present data**, so the honest description of B-MOM is
*a four-year in-sample result*, and the +43 % it would buy is not currently available.

**W56's preregistered falsifier therefore fires, in its own words:**

> this repo holds no engine that diversifies P1 on present evidence; **model concentration is
> the binding constraint on the owner's objective**; and the next move is to **build or buy
> genuinely different information** rather than to recombine what already exists.

## 6. What remains open, and it is not nothing

- **The forward sample.** B-MOM is one of three candidates in `MONITOR-02`, whose rules are
  frozen and whose first eligible read is **≥ 2027-08-01** on data ≥ 2026-08-01. That read, not
  this wave, is B-MOM's real trial. Nothing here touched it and nothing here changes it.
- **The ~40-session June–July 2026 health window** was not opened. Its power was computed in
  the spec before the wave started — expected net $11k ± $23k — and it cannot distinguish
  anything. Opening it would have produced a number with no information content, and a number
  with no information content is worse than no number, because it gets quoted.
- **The portfolio arithmetic itself stands.** W56's finding that a loosely-correlated
  profitable sleeve at w = 0.30 buys +43 % at a slightly better drawdown is a property of the
  combination, not of B-MOM. It is the specification for what to build or buy: an engine with
  a real edge and an underwater curve that is not P1's.

## 7. Files
`out/regime.txt` `out/quintiles.csv` · code `research/weekly_edge/src/run_we_w57.py`
