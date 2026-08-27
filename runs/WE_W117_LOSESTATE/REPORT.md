# WE_W117 — what does the book lose on, and is anything we own positive there? · REPORT

Preregistered (`spec.yaml`, committed at `f23a020` before any code was written).
POST-W115 owner directive §§22, 26, 27, 29, 37, 44 LANE 4.

> ## **THE SPEC'S OWN STRUCTURAL HYPOTHESIS IS FALSIFIED — and that is the wave's most valuable output.**
> ## I wrote in advance that a long-only P1 plus an opening-auction XM should leave the book short of **downside** exposure, so its losing weeks ought to be **down** weeks. They are not. The share of TREND-DOWN sessions on losing weeks is **0.147 against 0.143 on winning weeks, p = 0.880 — literally no difference** — and **more than half of the book's losing weeks are weeks NQ went UP.**
> ## **The book loses when TREND-UP sessions are SCARCE and REVERSAL sessions are ABUNDANT.** That names the missing engine precisely, and it is **not** a downside engine.
> ## **PART B: nothing we own is positive there.** FOLLOW_MORNING's long leg earns **$482/week unconditionally and −$2 on the book's losing weeks.** It is not merely unhelpful — it is specifically absent exactly then.

## Part A — the losing state, described for the first time

Book = **0.473 × P1/PCT + 0.527 × XM_CONFLICT** (inverse-vol), 213 weeks, **87 losing (40.8 %)**,
$1,142/wk, max DD $11,489, worst week −$7,611, mean loss −$1,649, longest losing streak 5 weeks,
**55.4 % of weeks spent in drawdown**.

| market state | LOSING weeks | WINNING weeks | difference | perm p | |
|---|---|---|---|---|---|
| **NQ weekly return %** | −0.218 | +0.660 | **−0.878** | **0.006** | ✱ |
| **share TREND-UP** | **0.167** | **0.238** | **−0.071** | **0.005** | ✱ |
| **share REVERSAL** | **0.299** | **0.230** | **+0.069** | **0.011** | ✱ |
| share TREND-DOWN | 0.147 | 0.143 | **+0.004** | **0.880** | — |
| share RANGE | 0.283 | 0.258 | +0.025 | 0.361 | — |
| share MIXED | 0.104 | 0.131 | −0.027 | 0.199 | — |
| daily vol % | 0.893 | 0.982 | −0.089 | 0.258 | — |
| weekly range, points | 765.5 | 742.1 | +23.4 | 0.644 | — |
| announcement days | 0.621 | 0.587 | +0.033 | 0.736 | — |

> ### **The book loses when the market stops trending UP — not when it falls.**
> **P(NQ week down ∣ book loses) = 0.471** against an unconditional **0.437.** Barely elevated:
> **53 % of the book's losing weeks are weeks NQ rose.** Correlation of book weekly dollars with
> NQ's weekly return is only **+0.243**. And **TREND-DOWN sessions are no more common on losing
> weeks than on winning ones.**
>
> What separates the two, at p ≈ 0.005–0.011, is the **absence of TREND-UP** (0.167 vs 0.238) and
> the **presence of REVERSAL** (0.299 vs 0.230) — sessions that make their extreme early and close
> back through it. Volatility, range and event density separate **nothing**.

**Which leg lost**, on the 87 losing weeks: **both** 31 (35.6 %), **P1 only** 32 (36.8 %), **XM
only** 24 (27.6 %). No leg dominates — consistent with W110's finding that these two do not fail
together, and a point in the portfolio's favour rather than against it.

## Part B — what is positive there? Nothing.

| candidate | all weeks $ | **LOSING weeks $** | null mean | null p95 | percentile | vs ALWAYS_SHORT |
|---|---|---|---|---|---|---|
| FM_LONG | **$482** | **−$2** | $484 | $1,102 | 9.4th | +$21 |
| FM_SHORT | $356 | **+$69** | $358 | $898 | 18.9th | +$92 |
| ALWAYS_SHORT *(control)* | −$226 | −$23 | −$227 | $422 | 68.9th | — |
| FADE_MORNING | −$974 | −$203 | −$978 | −$80 | 90.1th | −$180 |
| *XM_LONG* ⚠️ | $583 | −$849 | $589 | $992 | 0.0th | −$826 |
| *XM_SHORT* ⚠️ | $333 | −$1,017 | $339 | $790 | 0.0th | −$993 |

**Survivors: NONE.** The best-of-6 bar was therefore not computed.

> ### The sharpest line in the table is FM_LONG's: **$482/week on average, −$2 on the weeks the book loses.** The circular-shift null says a *random* alignment of its own returns with those weeks would have produced **+$484**. It is not failing to help — **it is specifically, systematically absent exactly when it would be needed.** FM_SHORT is the same story at smaller scale (+$69 real vs +$358 random).

### ⚠️ A defect in my own screen

**`XM_LONG` and `XM_SHORT` are inside the book** — XM is 52.7 % of it. Asking whether XM's own legs
are positive on weeks the book (which contains XM) loses is **partly circular**, and their 0.0th
percentiles are close to definitional rather than informative. The screen's honest breadth is
**four independent candidates, not six**. Recorded rather than quietly dropped; it does not change
the verdict, because none of the four outside candidates comes close either.

### Power, as disclosed in the spec beforehand

87 losing weeks. Smallest detectable effect at ~80 % power: **$850–$2,000/week** depending on the
candidate. Observed effects are **−$203 to +$69**. So the wave **cannot rule out** a true effect of
a few hundred dollars a week — but nothing observed is within an order of magnitude of the bar, and
none of the candidates is even directionally interesting.

## Part C — not run

Per the spec: nothing survived Part B, and that is **a result, not a failure**. It names the
information gap precisely.

## Decision

**NOTHING PROMOTED. Two things learned, and the second one re-points LANE 4.**

1. ⭐ **The book's weakness is not directional — it is a MISSING REVERSAL ENGINE.** The
   preregistered downside hypothesis is falsified: TREND-DOWN share is identical on winning and
   losing weeks (p = 0.880), and the book loses on up-weeks as often as down-weeks. What
   distinguishes the losing weeks is **fewer TREND-UP sessions and more REVERSAL sessions.**
   **Anything built to fill the book's hole must earn on sessions that make their extreme early and
   close back through it.**
2. **No object this campaign owns is positive on those weeks** — including the strongest modern
   standalone it has (`FOLLOW_MORNING`, which is *absent* rather than merely small), and including
   the crudest possible downside exposure (`ALWAYS_SHORT`, −$23).

### What this does and does not license

> ⚠️ **REVERSAL is the family this campaign has killed seven times.** But read what was actually
> killed: W108's fades were tested as **afternoon fades at one geometry (11:49 → 15:44)**, and
> W111b then showed they were sitting on the **wrong side of a live momentum effect** at exactly
> that geometry — an unconditional fade there loses $206/trade while its mirror earns $179. **That
> is not a test of whether reversal sessions can be monetised. It is a test of one clock.**
>
> The W51 REVERSAL class is **23–30 % of weeks** and is where the book bleeds. Whether it can be
> monetised is **UNKNOWN**, and the honest cost of finding out is one preregistered wave against a
> matched unconditional control — **not** a return to fade-parameter search, which §26 has parked.

**Next**: a preregistration targeting the reversal session specifically, at a geometry chosen for
the *mechanism* (the early extreme and the return through it) rather than inherited from W108's
midday clock — with the matched unconditional control that W111b made binding, and with the
explicit understanding that the seven prior kills constrain the *clock*, not the *class*.
