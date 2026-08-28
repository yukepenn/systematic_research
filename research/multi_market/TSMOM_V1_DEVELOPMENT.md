# TSMOM V1 — DEVELOPMENT result: FAILS 3 of 6 preregistered gates. Validation stays shut.

| | |
|---|---|
| **verdict** | **GATES FAILED — no tuning, no horizon selection, VALIDATION NOT OPENED** |
| date | 2026-08-27 |
| window | **DEVELOPMENT only**, 2009-03-30 → 2018-12-31 (2,265 trading days) |
| code | `src/ncd_day.py` · `src/roll.py` · `src/contract_truth.py` · `src/build_substrate.py` · `src/tsmom_v1.py` |
| data | 21 CORE roots · 1,230 contracts · **44,608 eligible root-days** · `db/day` unmerged store only |
| touched | **VALIDATION (2019–2022) and FINAL HOLDOUT (2023–2026) NOT READ.** Seal untouched |

---

## 1. The gates, declared before the run and failed by it

| gate | observed | verdict |
|---|---:|---|
| G1 net > 0 at PRIMARY cost | **$10,167** | PASS |
| **G2 annualised Sharpe ≥ 0.30** | **0.226** | **FAIL** |
| **G3 positive in ≥ 6 years** | **5 of 9** | **FAIL** |
| G4 net > 0 at STRESS cost | $2,736 | PASS |
| G5 top root ≤ 50 % of net | 32.4 % (NQ) | PASS |
| **G6 top sector ≤ 60 % of net** | **72.3 % (equity index)** | **FAIL** |

**No gate was invented afterwards and none is being relaxed.** V1 does not proceed.

## 2. What actually happened: costs ate half the edge

| | gross | cost | net | Sharpe | maxDD | cost drag |
|---|---:|---:|---:|---:|---:|---:|
| **PRIMARY** (1 tick + $4.36 RT) | $19,270 | $9,102 | **$10,167** | 0.226 | $17,129 | **47.2 %** |
| **STRESS** (2 ticks + $4.36 RT) | $19,270 | $16,533 | $2,736 | 0.061 | $19,548 | **85.8 %** |

> ### **The cost ratio is SCALE-INVARIANT and therefore a real property, not an artifact of the
> ### risk budget.** Position size, gross P&L, turnover and cost all scale linearly with
> ### `TARGET_RISK_USD`, so 47.2 % would be 47.2 % at any capital level. **A daily-rebalanced
> ### equal-weight TSMOM at this turnover pays roughly half its gross away in friction**, and
> ### under a two-tick spread it pays away 86 %.

Underwater **96.9 %** of days. Positive days 52.9 %.

## 3. Yearly — the shape that fails G3

| year | net | Sharpe |
|---|---:|---:|
| 2010 | **+$5,728** | 1.11 |
| 2011 | +$3,450 | 0.58 |
| 2012 | −$1,252 | −0.34 |
| 2013 | **+$7,862** | 1.71 |
| 2014 | +$4,382 | 0.92 |
| 2015 | −$4,164 | −0.88 |
| 2016 | **−$6,581** | −1.45 |
| 2017 | −$359 | −0.08 |
| 2018 | +$1,101 | 0.17 |

**Five positive years of nine, and the whole net is earned in 2010–2014.** The last four years
contribute **−$10,003**. That is the pattern a decaying or regime-dependent premium leaves, and it
is exactly why G3 exists.

## 4. Concentration — the sector table is the G6 failure

| sector | net | share |
|---|---:|---:|
| equity index | +$7,356 | **72.3 %** |
| metals | +$3,961 | 39.0 % |
| rates | +$2,709 | 26.6 % |
| energy | +$2,602 | 25.6 % |
| fx | +$24 | **0.2 %** |
| **ags** | **−$6,484** | **−63.8 %** |

Long +$10,821 vs short +$923 — **the result is overwhelmingly a long-side, equity-index effect**,
which is the least diversifying thing a book already anchored on NQ could have found.

## 5. ⚠️ The horizon diagnostic, and why it is NOT acted on

| horizon | net | Sharpe |
|---|---:|---:|
| 21d | **−$20,538** | −0.354 |
| 63d | +$5,332 | 0.091 |
| 126d | +$23,298 | 0.411 |
| **252d** | **+$25,757** | **0.479** |

> ### **The 252-day component alone would pass every gate. Selecting it is forbidden and it is
> ### not selected.**
> §8 fixed the equal-weight blend *before* results precisely so that this table could not become a
> decision. A 252-day-only V2 chosen *after* seeing this is a one-of-four pick on the development
> set, and this repo has measured what that does: a scanned best-of costs ~20 % of MAR on data with
> **no structure at all** (discipline rule 22). If a longer-horizon variant is ever built it needs
> its own preregistration and its own multiplicity accounting — **and it must be honest that the
> idea came from here.**

## 6. Honest caveats on the substrate itself

1. **FX and CL never roll on volume.** 6E/6J/6B/6C/6S produce **0** volume-crossover rolls and
   41–42 pre-expiry overrides; CL produces **0 / 127**. Their stored contract lives barely overlap
   (FX median overlap **3 days**), so the roll there is effectively **a fixed pre-expiry rule** —
   which §6 sanctions when volume cannot be trusted, but which must be named rather than implied.
   **FX contributed +$24. Its roll mechanics are the weakest in the book.**
2. **Coverage is 94–99 % per root, not 100 %.** 25–92 gaps per root, largest **51–56 business
   days** (YM, 6A, grains). Handled by the eligibility rule, not by silent interpolation.
3. **The store floor is 2009-03-30**, uniformly across all 21 roots — not 2009-01-01. The
   development window moved for **data availability**, which §3 permits; no return influenced it.
4. **Positions are fractional.** Legitimate for portfolio science (§9); it is **not** an executable
   sizing claim, and integer-contract mapping remains a separate question.

## 7. Verdict

| | |
|---|---|
| **what was measured** | a frozen, boring, equal-weight 21/63/126/252 TSMOM across 21 CORE roots on a causally-rolled, basis-safe economic return series |
| **what passed** | the **data contract** (basis invariance to 8e-13; naive splice books the basis exactly); the **roll causality assertion** on all 1,180 volume rolls; G1, G4, G5 |
| **what failed** | **G2, G3, G6** — Sharpe 0.226, five positive years of nine, 72.3 % equity concentration |
| **what changed** | multi-market TSMOM is **not** a free diversifier at this specification. Its gross edge is real but **friction takes 47 %**, and what survives is long-equity beta |
| **what did NOT change** | the incumbent; the seal; VALIDATION; FINAL HOLDOUT; the 141-session blind pool |
| **evidence class** | **DEVELOPMENT-ONLY, DISCOVERY-CONSUMED.** Not forward, not confirmed |
| **ladder status** | **no candidate.** V1 does not advance to validation |
| **data burned** | the DEVELOPMENT window for this candidate. **VALIDATION and FINAL HOLDOUT remain unspent** |
| **next** | either a preregistered V2 on a **different, declared-in-advance** specification with the horizon question handled as multiplicity, or accept that daily-rebalanced TSMOM at this cost structure is not the second alpha and spend the budget elsewhere. **That is an owner-facing choice, not a tuning exercise.** |
