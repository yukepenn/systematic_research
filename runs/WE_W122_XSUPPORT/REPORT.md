# WE_W122 — cross-market intraday support at the P1 decision event · REPORT

Preregistered (`spec.yaml`, committed at `b351fe4` before any code was written).
POST-W121 owner directive §§12–19, 23, 25–29, LANE A. **STAGE A ONLY — no policy tested.**
Artifact: `out/decision_quality_ledger.csv`, **2,131 P1 entry events**, inputs and outcomes
separated, every input from bars **strictly before** the fill.

> ## **NO INCREMENTAL INFORMATION. All four preregistered gates FAIL.**
> ## The primary — `B_SUPPORT_MAG` at 15m, matched Q5−Q1 — is **−$157/entry**, at the **22.1st percentile** of its own null, **−$227** prequential with 2 of 7 blocks positive, and **below the LEVEL-2 NQ-only control ($90)**.
> ## **The matched-vs-pooled column is the whole story.** Pooled differences are small and mostly positive ($12–$183). Once NQ's own pre-entry move, time-of-day and entry ordinal are held fixed, they scatter around zero. **What little the cross-market features carried was NQ momentum wearing a cross-market label** — exactly what §15 said to test for.

## 1. The grid — pooled vs matched

2,071 of 2,131 events fall in **58 matched strata** (NQ-move quintile × 4 time buckets × 3 ordinal
buckets). Same-session feature availability: 5m **98.1 %**, 15m **97.2 %**, 30m **96.1 %**.

| primitive | window | n Q1 | n Q5 | POOLED Q5−Q1 | **MATCHED Q5−Q1** | matched/pooled |
|---|---|---|---|---|---|---|
| **A_SIGN_BREADTH** | 5/15/30m | 452/523/590 | **0/0/0** | — | — | ⚠️ **UNTESTED** |
| B_SUPPORT_MAG | 5m | 418 | 417 | $105 | −$58 | −0.55 |
| **B_SUPPORT_MAG** | **15m** *(primary)* | 414 | 414 | **$12** | **−$157** | −13.17 |
| B_SUPPORT_MAG | 30m | 409 | 409 | $82 | $48 | 0.59 |
| C_DISPERSION | 5m | 418 | 417 | $98 | $19 | 0.19 |
| C_DISPERSION | 15m | 414 | 414 | $183 | $68 | 0.37 |
| C_DISPERSION | 30m | 409 | 409 | $51 | $251 | 4.95 |
| **D_NQ_IDIO** | 5m | 418 | 417 | $76 | **$122** | 1.62 |
| **D_NQ_IDIO** | 15m | 414 | 414 | $167 | **$131** | 0.78 |
| **D_NQ_IDIO** | 30m | 409 | 409 | $172 | **$262** | 1.52 |
| E_DELAYED_CONF | 5m | 418 | 417 | −$203 | −$244 | 1.20 |
| E_DELAYED_CONF | 15m | 414 | 414 | $97 | $19 | 0.19 |
| E_DELAYED_CONF | 30m | 409 | 409 | −$38 | −$102 | 2.70 |

**LEVEL-2 control** — NQ's *own* standardised 15m pre-entry move, same quintile statistic:
**pooled Q5−Q1 = $90/entry.** (Matched is undefined for it: it *is* the strata.)

### ⚠️ `A_SIGN_BREADTH` is UNTESTED, not null

It is an **integer 0–3**, so `qcut` into quintiles produces **zero Q5 members**. This is the
W107b/W111 lesson in its third appearance — *a discrete variable cannot be quantile-binned* — and
per the standing rule it is reported as **UNTESTED with its acceptance rate printed**, never folded
into the family as a null. Sign breadth as a construct remains unmeasured at this geometry.

## 2. The primary and its nulls

| | |
|---|---|
| REAL matched Q5−Q1 | **−$157/entry** |
| own-cell null (outcome permutation) | mean $0, **p95 $343** → **22.1st percentile** |
| **dependence-preserving FAMILY null** | **p95 $503** — one outcome permutation shared by all 15 cells, so cross-feature and cross-window correlation is retained |

The family bar of **$503** is what §28 requires and what W116b's correction earned. The best cell in
the entire grid is `D_NQ_IDIO` at 30m with **$262** — **barely half the bar.** Nothing is close.

## 3. Prequential — §27

Eight chronological blocks, quintile cuts taken from **prior events only**:

| block | events | dates | matched Q5−Q1 |
|---|---|---|---|
| 1 | 266 | 2023-01-31 → 2023-07-10 | −$648 |
| 2 | 267 | 2023-07-10 → 2023-12-22 | −$459 |
| 3 | 266 | 2023-12-22 → 2024-05-09 | −$2 |
| 4 | 266 | 2024-05-09 → 2024-10-29 | **+$1,507** |
| 5 | 267 | 2024-10-29 → 2025-05-02 | −$864 |
| 6 | 266 | 2025-05-02 → 2025-12-11 | −$1,211 |
| 7 | 267 | 2025-12-14 → 2026-07-29 | +$86 |

**Prequential mean −$227/entry, 2 of 7 blocks positive.** The one large positive block is not a
trend; it is the shape W115 already taught us to distrust.

## 4. Gates — every clause checked in code (§29)

| gate | spec | observed | |
|---|---|---|---|
| **G1** | matched Q5−Q1 > 0 | −$157 | **FAIL** |
| **G2** | > family-null p95 ($503), dependence-preserving | −$157 | **FAIL** |
| **G3** | survives prequential (mean > 0) | −$227 | **FAIL** |
| **G4** | beats LEVEL-2 NQ-only control ($90) | −$157 | **FAIL** |

**STAGE-A VERDICT: NO INCREMENTAL INFORMATION.**

*(W121's defect does not recur: all four clauses are coded assertions and the table is printed by
the program, not assembled by hand.)*

## 5. The one loose thread, flagged rather than promoted

The preregistered secondary — the same statistic split by session outcome:

| slice | n | matched Q5−Q1 |
|---|---|---|
| P1 **losing** sessions | 1,257 | **+$202/entry** |
| P1 **winning** sessions | 814 | **−$726/entry** |

> ⚠️ **This conditions on an EX-POST session outcome and is therefore not a usable state**, and it
> was not a gate. The sign flip is large enough to record but it is exactly the shape a spurious
> post-hoc slice takes: the two halves are constrained to average to the pooled −$157, so an
> extreme in one forces an extreme in the other. **No follow-up wave is bought by this.** It is
> written down so a future reader does not rediscover it and mistake it for a lead.

## 6. Decision

**NOTHING PROMOTED. STAGE B IS NOT REACHED** — §23 is binding, and W113 and W121 both showed what
optimising policy before proving information costs.

1. **`CROSS-MARKET INTRADAY SUPPORT` is CLOSED for the P1 decision-quality target.** Five
   primitives × three predeclared windows, matched on the controls §15 names, against a
   dependence-preserving family null and a prequential arm. The verdict is not "promising, needs
   tuning" — the spec fixed that phrasing out in advance.
2. **What *little* signal existed was NQ momentum relabelled.** Pooled differences of $12–$183
   collapse to scatter around zero under matching, and the NQ-only control ($90) beats the primary.
   That is precisely the §15 failure mode, and the matched-strata design is what exposed it.
3. **`D_NQ_IDIO` is the one directionally coherent primitive** — NQ moving *alone* is the most
   positive cell at every window ($122 / $131 / $262), which is the same mechanism `XM_CONFLICT`
   monetises at the opening auction. **It does not clear the family bar** (best $262 vs $503), so
   it is an observation, not a result. Recorded because it is the only place in the grid where a
   mechanism and a sign agree.
4. **Combined with the order-flow data gate** (`runs/DATAGATE_ORDERFLOW_20260827/`: 71 of 2,131
   entries covered, MDE $564/entry = 4× the mean), the honest campaign-level statement is:

   > ### **P1 entry quality is not separable by any information source we currently hold.** Cross-market support is measured and null; participation/order-flow is unmeasurable at the required resolution. The next real move on this target requires **data we do not own** — which is an owner acquisition decision, not a research task.
5. **`A_SIGN_BREADTH` needs a non-quantile treatment** if it is ever revisited — its own levels, as
   W107b prescribed for discrete variables. That is a specification note, not an open lead.
