# WE_W95 — IS THE SESSION BOX WORTH HAVING ON A PORTFOLIO? · REPORT

Preregistered (`spec.yaml`). B1 control reproduced first: P1 boxed = **2,002 trades, 13.7266
pts/session, $280,131** against the committed reference 2,002 / 13.73 / $280,131. **REPRODUCED.**

> ## **H1 FAILS as stated — and the truth underneath it is more useful than the hypothesis.**
> ## The box's value is not "single object vs portfolio". **It tracks how TWO-SIDED the object
> ## is**, monotonically, across four objects — and W28's own null agrees.
> ##
> ## **H3 is FALSIFIED and mechanism law 6 does not explain this** — but the test was
> ## confounded and I say so rather than claiming a counterexample.
> ##
> ## **W91's box-free observation is CONFIRMED on its own object** (3 of 3 with the score
> ## defect fixed) **and does not generalise to either challenger.**

---

## 1. The six arms, matched in contract-minutes

| arm | trades | scale | weekly $ | wk + % | streak | max DD | top-5 DD | worst week | wk$ @ fixed DD |
|---|---|---|---|---|---|---|---|---|---|
| **A** P1 + box | 2,002 | 1.000 | $1,154 | 52.6 % | 8 | **$27,292** | $18,436 | **−$7,579** | **$856** |
| **B** P1 no box | 2,945 | 0.695 | $1,198 | **56.8 %** | 7 | $36,436 | **$18,151** | −$14,749 | $665 |
| **C** pair 2:3 + boxes | 7,924 | 1.000 | **$5,063** | 57.7 % | 7 | **$86,651** | **$57,274** | −$43,462 | **$1,183** |
| **D** pair 2:3 no box | 11,558 | 0.723 | $4,569 | **60.1 %** | **4** | $86,813 | $62,981 | **−$40,962** | $1,065 |
| **E** NETFUSE_1 + box | 3,893 | 1.000 | **$1,233** | **58.7 %** | 5 | **$23,366** | **$15,611** | **−$9,730** | **$1,068** |
| **F** NETFUSE_1 no box | 6,414 | 0.673 | $750 | 54.5 % | 5 | $46,742 | $22,879 | −$22,078 | $325 |

**H1 as stated: FAIL.** It required *"box helps the single object AND hurts the portfolio"*.
Neither half holds: the box wins **1 of 3** legs on P1, and the **portfolios prefer the box**
(no-box wins 1/3 on the pair, **0/3** on NETFUSE_1).

## 2. What is actually true — the box tracks TWO-SIDEDNESS

| object | direction | box wins | verdict |
|---|---|---|---|
| **SOLAR + BMOM** (§4) | long-only + latched ±1, weakest object (6.64 pts/session) | **0 / 3** | box **hurts** |
| **P1** | long-only | **1 / 3** | box hurts on consistency, wins on money |
| **{BMOM, X9a} 2:3** | one two-sided sleeve of two | **2 / 3** | box helps |
| **NETFUSE_1** | fully two-sided | **3 / 3** | box helps decisively |

And W28's own circular-shift null — session *s* boxed according to session *(s+k)*'s box events,
so the frequency and intraday timing of interventions are preserved and only *which session they
hit* changes — says the same thing independently:

| object | leg | real | null mean | **percentile** |
|---|---|---|---|---|
| **P1** (long, size 1) | weekly $ at fixed DD | $718 | $451 | **92.0 %** |
| | positive-week % | 54.9 | 53.0 | **80.5 %** |
| | raw mean top-5 DD | $16,573 | $17,547 | **70.0 %** |
| **NETFUSE_1** | weekly $ at fixed DD | **$1,068** | $353 | **100.0 %** |
| | positive-week % | **58.7** | 51.8 | **99.5 %** |
| | raw mean top-5 DD | **$15,611** | $24,366 | **100.0 %** |

> ## `FACT` — **the session box's PLACEMENT is nearly worthless on a long-only object
> ## (70th percentile on drawdown) and near-perfect on a two-sided one (100th / 99.5th / 100th).**
>
> `INFERENCE`, and it is legible: on a **long-only** book in a rising market, halting after a loss
> mostly forfeits a recovery that market drift would have supplied — W73 measured P1's drift term
> at **+$33,365**. On a **two-sided** book, halting after a loss stops you flipping back into the
> same chop; there is no drift to bail you out. **The box is a chop-protection device, and chop
> only costs you if you can trade both ways.**
>
> ⚠️ This does not overturn W28. W28 certified the **HALT alone** at the 98th percentile; this
> scores the **whole box** on three legs the campaign adopted later. On the money leg P1 still
> sits at the 92nd. But **the drawdown leg at the 70th is new information and it is unflattering.**

**And the honest note for the owner's own objective:** on P1 the box **costs 4.2 pp of positive
weeks** (52.6 % vs 56.8 %) to buy +29 % of money-at-fixed-drawdown and half the worst week
(−$7,579 vs −$14,749). Charter amendment 2 ranks **consistency first**. `UNKNOWN` whether that
trade is worth making; it has never been posed as a choice before and it is now on the table.

## 3. H3 `NOT SUPPORTED` — and the test was confounded, which I state rather than bury

A 31-cell grid over halt × target on NETFUSE_1:

| corr | value | law 6 predicts |
|---|---|---|
| corr(trade count, raw top-5 drawdown) | **+0.630** | negative |
| corr(trade count, weekly $ at fixed DD) | **−0.612** | positive |

Both signs are backwards. **But this is not a counterexample to mechanism law 6**, and calling it
one would be exactly the quantifier error the charter exists to prevent. Law 6's three instances
(W42/W45/W47) are about **removing entries at constant risk per event**. Loosening the halt raises
the trade count **and** the per-session risk budget simultaneously — the two are confounded by
construction, so this grid cannot separate them. **Verdict: the mechanism is `UNKNOWN`, and law 6
is neither supported nor refuted here.**

## 4. `CONFIRMED` — W91 §4's observation, retested on its own object with the defect fixed

W91's box-free arm built the causal quality score from a **box-limited** entry set. Rebuilt so the
score comes from the same box regime the arm trades under, on the exact object W91 measured:

| | trades | scale | weekly $ | wk + % | max DD | top-5 DD | wk$ @ fixed DD |
|---|---|---|---|---|---|---|---|
| PORT_SB (Solar+BMOM) with boxes | 2,933 | 1.000 | $792 | 55.9 % | $25,472 | $13,422 | $629 |
| **PORT_SB NO box** | 4,540 | 0.706 | **$821** | **60.1 %** | **$17,112** | **$12,375** | **$971** |

**Box-free wins 3 of 3 — W91's observation is CONFIRMED, and it does not generalise.** The same
test on `{BMOM, X9a}` and on NETFUSE_1 goes the other way. `{SOLAR, BMOM}` is the weakest object
in the comparison (SOLAR alone is 6.64 pts/session and 47.4 % positive weeks) and it is the one
the box hurts most — consistent with §2's reading.

## 5. `CORRECTION` — the grid's argmax is scan noise

The grid peaks at `(halt 2000, target 1000)`: **$1,423 against the incumbent `(1300, 1000)`'s
$1,068, an uplift of +33.2 %.** W93's walk-forward independently chose `halt = 2000` in **7 of 12**
refits. That is two signals pointing the same way, so it needed the scan-matched null the repo has
required since W53:

Running the **same 31-cell scan** on 40 session-shuffled versions of the target and recording each
scan's own winner:

> **A best-of-31 scan on structureless data produces uplifts with p95 = +317 %.
> The real +33.2 % sits at the 87.5th percentile. Bar is 95th. NOT SIGNIFICANT.**

⚠️ **The statistic is unstable and I am not hiding that**: the uplift is a *ratio* whose
denominator (the shuffled object's own `(1300, 1000)` score) can approach or cross zero, giving a
null distribution with mean −405 % and median −32 %. The percentile is therefore indicative, not
precise. **What is robust regardless: a 31-cell scan routinely manufactures uplifts far larger
than +33 %, so +33 % is not evidence.** `(1300, 1000)` stays.

## 6. Verdict

| | |
|---|---|
| **H1** (box helps single, hurts portfolio) | **FAIL** — the real axis is two-sidedness, not single-vs-portfolio |
| **H2** (box effect is specific) | **PASS on NETFUSE_1** (100/99.5/100), **WEAK on P1** (92/80.5/**70**) |
| **H3** (event reduction explains it) | **NOT SUPPORTED**, and the test was confounded — mechanism `UNKNOWN` |
| W91 §4 retest | **CONFIRMED on `{SOLAR, BMOM}`**, does not generalise |
| grid argmax `(2000, 1000)` | **scan noise** — 87.5th percentile against a 95th bar |

**NOTHING IS ADOPTED.** The box is not removed from P1 (W28's 98th-percentile halt certification
is not overturned by a portfolio measurement), the constants are not changed, and no new object is
created. What changes is the *description*: **the session box is a two-sided-object device**, and
the campaign has been carrying it on a long-only object where its drawdown leg sits at the 70th
percentile of arbitrary placement.

## 7. Files
`out/boxless.txt` · `out/w95b.txt` · `out/arms.csv` · `out/box_null.csv` · `out/box_grid.csv` ·
`out/scan_null.csv` · code `research/weekly_edge/src/run_we_w95.py`, `run_we_w95b.py`
