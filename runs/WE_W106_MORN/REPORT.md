# WE_W106 — LANE A, THE MORN RESIDUAL · REPORT

Preregistered (`spec.yaml`, committed before any result was read). Owner amendment §6 LANE A.

> ## **THE PRIMARY FAILS. −$56/trade, 18.0th percentile of its coin null (bar $55).**
> ## None of the five participation mechanisms carries directional information about the late
> ## morning at this geometry. And one of the five was **mis-specified and effectively untested.**

## 1. The outcome-blind calibration worked — and it exposed a mis-specification

Feature distributions were printed **before any economics**, as the amendment requires. That is
what made the next line visible before it could contaminate anything.

| mechanism | sessions defined | **non-zero direction** | verdict on the specification |
|---|---|---|---|
| **VOL_DECAY** | 1,058 | **3** | ⚠️ **MIS-SPECIFIED — effectively UNTESTED** |
| EFFORT_NO_RES | 1,058 | 1,047 | fine |
| DISP_PER_VOL | 1,051 | 1,050 | fine |
| VOL_SURPRISE | 1,058 | 1,057 | fine |
| OPEN_ACCEPT | 1,058 | 818 | fine |

> ⚠️ `DEFECT`, mine. `VOL_DECAY` required a run of ≥ 2 same-sign bars with **strictly** falling
> volume **ending exactly at the decision bar**. That fires on **3 of 1,058 sessions**.
>
> **This is the W100 lesson repeating in mirror image** — W100's gates accepted 92 % and could not
> separate anything; this one accepts 0.3 % and cannot be measured at all. **The monotone
> volume-decay exhaustion mechanism, which `MECHANISM_COVERAGE_20260826.md` ranks #1, remains
> UNTESTED.** It needs a specification that fires at a usable rate, and per the spec that is a new
> wave, not an edit to this one.

## 2. Economics — decide 10:01, fill 10:02, hold to 11:29, size 1, no stop

1,050 eligible sessions. p\* for this horizon = **0.5056**, computed not assumed.

| mechanism | rate | N | hit % | vs p\* | **$/trade** | net $ | t |
|---|---|---|---|---|---|---|---|
| **EFFORT_NO_RES** | 0.25 | 267 | **52.43 %** | +1.88 | **$166** | $44,368 | 1.33 |
| EFFORT_NO_RES | 0.50 | 531 | 50.66 % | +0.10 | $9 | $4,972 | 0.11 |
| EFFORT_NO_RES | 0.75 | 786 | 50.51 % | −0.05 | $17 | $13,018 | 0.25 |
| DISP_PER_VOL | 0.25 | 283 | 51.59 % | +1.03 | −$73 | −$20,766 | −0.53 |
| DISP_PER_VOL | 0.50 | 536 | 51.49 % | +0.94 | −$50 | −$26,952 | −0.53 |
| DISP_PER_VOL | 0.75 | 795 | 50.44 % | −0.12 | −$40 | −$32,104 | −0.53 |
| **VOL_SURPRISE** | 0.25 | 258 | **46.51 %** | **−4.04** | $14 | $3,570 | 0.10 |
| VOL_SURPRISE | 0.50 | 509 | 47.15 % | −3.40 | −$85 | −$43,062 | −0.86 |
| VOL_SURPRISE | 0.75 | 746 | 49.87 % | −0.69 | −$53 | −$39,623 | −0.66 |
| OPEN_ACCEPT | 0.25 | 286 | 48.25 % | −2.30 | −$102 | −$29,222 | −0.87 |
| OPEN_ACCEPT | 0.50 | 550 | 49.45 % | −1.10 | −$100 | −$54,958 | −1.07 |
| OPEN_ACCEPT | 0.75 | 817 | 50.55 % | −0.00 | −$102 | −$83,625 | −1.25 |

**PRIMARY** — equal-weight mean of $/trade across the five mechanisms at the 50 % arm:

| | |
|---|---|
| real | **−$56/trade** |
| coin null, same statistic | mean −$18, sd $45, **p95 $55** |
| **percentile** | **18.0th** |
| **verdict** | **FAILS** |

Best-of-12 bar for individual cells: **$266. Nothing clears it.** `EFFORT_NO_RES` at the 25 % arm
clears its own p\* (52.43 % against 50.56 %, $166/trade) and is therefore **WEAK** — one cell of
twelve, at the acceptance rate that trades least.

## 3. One directional finding, recorded and deliberately not acted on

> `VOL_SURPRISE` hit rates are **below 50 %**, and they get **worse as acceptance tightens** —
> 46.51 % at the 25 % arm against 49.87 % at 75 %. High morning participation predicts the late
> morning going **against** the opening drive, not with it. **My hypothesis had the sign backwards.**
>
> **The sign is NOT flipped here.** The spec forbids re-choosing anything after seeing P&L, and
> flipping a sign post hoc is the purest form of that. It is written down as a hypothesis for a
> separate preregistration, where it will have to clear its own null from scratch.

## 4. By session class, 50 % arm ($/trade)

| mechanism | TREND-UP | TREND-DOWN | REVERSAL | RANGE | MIXED |
|---|---|---|---|---|---|
| EFFORT_NO_RES | +$91 | −$109 | +$78 | −$182 | +$296 |
| DISP_PER_VOL | +$60 | +$506 | −$94 | −$350 | −$142 |
| VOL_SURPRISE | −$219 | +$248 | +$88 | −$36 | −$681 |
| OPEN_ACCEPT | +$122 | +$189 | −$178 | −$346 | −$160 |

Every mechanism loses on RANGE sessions. Nothing here is a range mechanism.

## 5. Decision

**Nothing promoted.** The MORN residual — **$1,667/session of `EX_POST_EXECUTION_FEASIBLE_ORACLE`
at p\* = 0.5048**, still the largest single-segment gap in the ledger — is **untouched by this lane.**

What the wave bought:

1. Four of five participation mechanisms carry no usable directional information about the late
   morning at this geometry. The volume column of the coverage matrix gets four more TESTED-NULL
   cells, with the quantifier attached: *as a direction, at 10:01, held to 11:29*.
2. **Volume decay is still untested**, and now we know why — the specification must be written to
   fire at a measurable rate, which is a constraint the next attempt inherits.
3. A signed, falsifiable hypothesis for a future wave: morning participation surprise predicts
   **reversal**, not continuation.
