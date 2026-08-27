# WE_W91 — FUSION vs INDEPENDENT RISK BUDGETS · REPORT

Preregistered (`spec.yaml`). Owner directive §3 — the main mechanistic hypothesis.

> ## **The owner's hypothesis is SUPPORTED (portfolio wins 2 of 3 legs) — and the four-way
> ## decomposition says the reason is NOT the one the hypothesis names.**
> ##
> ## Holding the ingredients fixed, **the combiner change on its own is worth −$501/week of
> ## money and +$1,029 of WORSE drawdown.** The portfolio's entire advantage is that
> ## **fusion is long-only by construction and therefore cannot hold B-MOM's short leg.**

---

## 1. The ladder (`FACT`) — five objects, same two ingredients

| object | trades | ctrRT/wk | **contract-minutes** | net $ | pts/session |
|---|---|---|---|---|---|
| SOLAR (empty OR slot) | 1,890 | 10.43 | 188,969 | $130,876 | **6.64** |
| **P1 (fused)** | 2,002 | 11.12 | 220,039 | $280,131 | **13.73** |
| X9a (fused, other channel) | 1,946 | 10.79 | 221,327 | $233,781 | 11.52 |
| **BMOM_std** (direct, L+S) | 1,043 | 4.90 | **275,497** | $252,258 | 12.14 |
| BMOM_L_std (direct, long only) | 677 | 3.18 | 174,275 | $130,808 | 6.32 |

- **Fusion is worth 7.09 pts/session** (13.73 − 6.64), i.e. **52 % of P1's production** —
  `REPRODUCED`, W67 measured 51 % by a different route.
- `CORRECTION` W67 reported Solar alone at **7.26** pts/session; on the corrected extended
  substrate it is **6.64**. The 46 sessions W76 recovered were bad ones. W67's number was
  computed on the truncated substrate and is superseded, not wrong-at-the-time.
- **BMOM_std carries MORE contract-minutes than P1** (275,497 vs 220,039) from a quarter of the
  round turns — it latches and holds. "One contract of BMOM" is **not** one unit of exposure,
  which is why every comparison below is matched in contract-minutes and not in contracts.

## 2. PHASE 1 — the decision rule (`FACT`)

Matched in contract-minutes to P1:

| object | scale | weekly $ | wk + % | streak | max DD | **top-5 DD** | worst week | wk$ @ fixed DD | eff |
|---|---|---|---|---|---|---|---|---|---|
| SOLAR | 1.16 | $539 | 47.4 % | 9 | $26,194 | $18,019 | −$10,296 | $417 | 0.052 |
| **P1 (FUSED)** | 1.00 | **$1,154** | 52.6 % | 8 | $27,292 | $18,436 | **−$7,579** | **$856** | **0.152** |
| X9a | 0.99 | $935 | 52.1 % | 8 | $26,492 | $17,658 | −$8,763 | $715 | 0.107 |
| BMOM_std | 0.80 | $895 | 56.8 % | 4 | $35,624 | $22,200 | −$13,554 | $509 | 0.066 |
| **PORT_SB (Solar+BMOM)** | 0.95 | $750 | **55.9 %** | **4** | **$24,134** | **$12,718** | −$8,482 | $629 | 0.088 |
| PORT_SBL (Solar+BMOM_L) | 1.21 | $627 | 53.5 % | 6 | $35,769 | $19,465 | −$12,133 | $355 | 0.052 |
| **PORT_XB (X9a+BMOM 2:3)** | 0.91 | $917 | **57.7 %** | 7 | **$15,693** | **$10,373** | −$7,871 | **$1,183** | 0.116 |

**PORT_SB vs P1 — same two ingredients, two combiners:**

| leg | portfolio | fused | winner |
|---|---|---|---|
| weekly $ at fixed DD | $629 | **$856** | FUSED |
| positive-week % | **55.9 %** | 52.6 % | PORTFOLIO |
| raw mean top-5 DD | **$12,718** | $18,436 | PORTFOLIO |

> **Portfolio 2 / 3 → the owner's hypothesis is `SUPPORTED`.**
> Stated without spin: **fusion makes more money; the portfolio is more consistent and has a
> 31 % smaller drawdown.** That is a real trade-off and this is the first time the campaign has
> separated it, because until now the two combiners had never been run on identical ingredients.

## 3. PHASE 3 — ⚠️ THE ATTRIBUTION, and it inverts the story

`PORT_SBL` is the portfolio with a **long-only** B-MOM. It is the exact long-only counterpart of
the fused object, so the difference `PORT_SBL − P1` is **the combiner and nothing else**, and the
difference `PORT_SB − PORT_SBL` is **the short leg and nothing else**.

| | weekly $ | wk + % | top-5 DD | wk$ @ fixed DD | worst week |
|---|---|---|---|---|---|
| P1 (fused, long-only) | $1,154 | 52.6 % | $18,436 | **$856** | −$7,579 |
| PORT_SBL (portfolio, long-only) | $627 | 53.5 % | $19,465 | $355 | −$12,133 |
| PORT_SB (portfolio, both sides) | $750 | **55.9 %** | **$12,718** | $629 | −$8,482 |

| isolated effect | money @ fixed DD | positive weeks | top-5 DD |
|---|---|---|---|
| **E_c — B-MOM's SHORT LEG** | **+$274** | **+2.35 pp** | **−$6,747 (better)** |
| **E_b/E_a — THE COMBINER ITSELF** | **−$501** | +0.94 pp | **+$1,029 (worse)** |

> ## `FACT` — **splitting the fused object into sleeves, holding the ingredients constant,
> ## LOSES $501/week of risk-adjusted money and makes the drawdown WORSE.**
> ## **Every bit of the portfolio's advantage — and more — comes from the short leg, which the
> ## fused long-only architecture is structurally incapable of holding.**

This is a materially different story from the one the campaign has been telling. The value is not
"independent risk budgets are a better way to combine". It is: **the OR-gate throws away one third
of B-MOM's net ($83,691, W90) and all of its counter-directional behaviour, and the portfolio form
is simply the only container we have that can keep it.**

`INFERENCE` and it is actionable: **a long-AND-short fused object has never been built.** The
OR-gate fires on `chan == +1`; nothing in the architecture forbids a mirrored `chan == −1` short
gate on the same Solar ensemble. Every short attempt this campaign made (W38/W39/W61/W75/W78) was
a mirrored *ratchet vote*, never a mirrored *OR gate*. That is a new object, it is cheap to build,
and it is the natural next wave.

⚠️ **Tension with W90, stated rather than smoothed.** In this basket the short leg improves the
top-5 drawdown by $6,747; in the `{X9a, BMOM}` basket W90 found it makes the drawdown *worse* and
sits at the 73rd percentile of its own null. The underwater matrix explains it: X9a is already
**−0.171** with BMOM_std and **−0.191** with BMOM_L_std, so it gets its offset from B-MOM's *long*
side; SOLAR is **+0.225 / +0.150** and gets none. **The short leg matters when the long partner
does not already hedge you.** Both measurements stand; neither is retracted.

## 4. PHASE 4 — E_a (independent risk budgets) `FALSIFIED`, and a surprise

| PORT_SB | weekly $ | wk + % | top-5 DD | wk$ @ fixed DD | worst week |
|---|---|---|---|---|---|
| TWO budgets (one box per sleeve) | $750 | 55.9 % | $12,718 | $629 | −$8,482 |
| ONE budget (portfolio-level box) | $330 | 54.5 % | $11,869 | $332 | −$6,644 |
| **NO budget (control)** | $735 | **60.1 %** | **$11,750** | **$923** | −$10,092 |
| vs FUSED P1 | $1,154 | 52.6 % | $18,436 | $856 | −$7,579 |

| PORT_XB | weekly $ | wk + % | top-5 DD | wk$ @ fixed DD | worst week |
|---|---|---|---|---|---|
| TWO budgets | $917 | 57.7 % | $10,373 | **$1,183** | −$7,871 |
| ONE budget | $167 | 54.5 % | $13,485 | $157 | −$5,783 |
| **NO budget (control)** | $810 | **61.5 %** | $10,881 | $1,110 | −$7,611 |

`CORRECTION` recorded against myself: the first draft of this phase layered an **extra**
portfolio box on top of the per-sleeve boxes, which tests *three* budgets, not one. It was
discarded before anything was written down. The sleeves are now genuinely re-simulated box-free
(SOLAR 3,090 / X9a 2,886 / BMOM 1,450 / BMOM_L 713 trades) before the shared box is applied.

- **E_a is FALSIFIED.** Collapsing to one budget is not neutral, it is *catastrophic* — money at
  fixed drawdown falls 47 % (PORT_SB) and 87 % (PORT_XB), because a loss in the sleeve that
  trades first halts the sleeve that trades later, and W89 established the two sleeves are
  **temporally disjoint** (BMOM 100 % RTH, X9a 62.6 % overnight). So separate budgets are
  *necessary* — but they do not *create* the advantage, they only avoid destroying it.

- ⚠️ **THE SURPRISE, and it is queued rather than claimed: at matched contract-minutes the
  portfolio is BETTER WITH NO SESSION BOX AT ALL** — 60.1 % vs 55.9 % positive weeks, $923 vs
  $629 at fixed drawdown, and a *smaller* max drawdown ($16,124 vs $24,134, implied).
  The session box is one of this campaign's best-evidenced components (W22, W26, W28 — the halt
  clears its own circular-shift null at the **98th percentile**) — but **all of that evidence is
  on the FUSED object and none of it is on a portfolio.** It is also exactly what mechanism
  law 6 predicts (*anything that reduces the number of events worsens the tail faster than it
  improves per-event quality*): box-free sleeves produce 63 % more trades, and at matched
  exposure more roughly-independent events buys a better tail.
  **This is an `OBSERVATION` with no null. It gets its own preregistered wave (W93).**

## 5. PHASE 2 — E_b, overlap and timing (`FACT`)

| pair | both-session % | **minute Jaccard** | A solo | B solo | **OPPOSED** |
|---|---|---|---|---|---|
| SOLAR / BMOM_std | 46.7 % | **4.4 %** | 87.8 % | 93.5 % | **34.2 %** |
| X9a / BMOM_std | 54.7 % | 8.2 % | 80.5 % | 87.7 % | 13.6 % |
| SOLAR / X9a | 76.0 % | **75.6 %** | 6.1 % | 20.5 % | 0.0 % |
| P1 / BMOM_std | 60.5 % | 8.7 % | 79.2 % | 87.0 % | 2.8 % |

Entry minute-of-day:

| | median | IQR | RTH share |
|---|---|---|---|
| SOLAR | 09:43 | 05:44 – 15:24 | 31.5 % |
| P1 | 09:40 | 06:06 – 14:35 | 35.0 % |
| X9a | 09:40 | 05:55 – 15:46 | 32.6 % |
| **BMOM_std** | **09:34** | **09:33 – 09:39** | **100 %** |
| BMOM_L_std | 09:36 | 09:33 – 09:54 | 100 % |

> `FACT` **B-MOM's entire interquartile entry range is six minutes wide: 09:33 – 09:39.** It is
> an opening-drive engine that then holds. The Solar family enters across the whole 24 hours.
> **The two sleeves share a position in only 4.4 % of minutes** — E_b is confirmed as a
> *description* (they are almost disjoint) but §3 shows the disjointness is not what pays.

**And the number that matters for execution: on the minutes they DO share, `SOLAR / BMOM_std`
hold OPPOSITE signs 34.2 % of the time.** A single netted NQ account would cross those internally
and the algebraic sleeve sum would not describe what the account did. That is the whole of the
owner's §6 and it is now quantified: for the actual challenger `X9a / BMOM_std` it is **13.6 % of
shared minutes**, and shared minutes are 8.2 % of occupied minutes.

## 6. PHASE 5 — correlations and regime

Weekly ρ · underwater ρ (W56's criterion):

| | SOLAR | P1 | X9a | BMOM_std | BMOM_L_std |
|---|---|---|---|---|---|
| **weekly** SOLAR | 1.000 | 0.602 | 0.655 | **0.020** | 0.027 |
| P1 | 0.602 | 1.000 | 0.613 | 0.287 | 0.407 |
| X9a | 0.655 | 0.613 | 1.000 | **0.009** | 0.060 |
| **underwater** SOLAR | 1.000 | 0.614 | 0.412 | **+0.225** | +0.150 |
| X9a | 0.412 | 0.576 | 1.000 | **−0.171** | **−0.191** |

Per-year weekly $ (matched contract-minutes):

| | 2022 | 2023 | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|
| SOLAR | $442 | $201 | $467 | $1,069 | $358 |
| P1 | $998 | $140 | $1,753 | $2,103 | $251 |
| X9a | $635 | **−$0** | $1,981 | $623 | $1,430 |
| BMOM_std | $1,265 | $657 | $878 | $1,449 | **$6** |
| PORT_SB | $930 | $472 | $711 | $1,294 | $149 |
| **PORT_XB** | **$921** | **$298** | **$1,481** | **$997** | **$784** |

> **PORT_XB is the only object in the table that is meaningfully positive in all five years.**
> `SUPPORTED` — and the mechanism is legible: X9a's dead year is 2023, B-MOM's is 2026, and
> they are different years. That, not the ρ, is what the pair is buying.

## 7. Weight sensitivity — shape only, nothing selected

| w_BMOM | weekly $ | wk + % | top-5 DD | wk$ @ fixed DD |
|---|---|---|---|---|
| **0.0 (Solar alone)** | $539 | **47.4 %** | **$18,019** | $417 |
| 0.2 | $634 | 56.8 % | $13,233 | $533 |
| **0.3** | $676 | **57.7 %** | **$11,462** | $590 |
| 0.5 (preregistered) | $750 | 55.9 % | $12,718 | $629 |
| 1.0 (BMOM alone) | $895 | 56.8 % | $22,200 | $509 |

**Going from zero B-MOM to 20 % B-MOM buys +9.4 pp of positive weeks and −27 % of top-5
drawdown.** That is the largest single step in the table and it is at the *smallest* weight.
No weight is selected here; a best-of-8 choice would need a family-wise null (repo rule, W53).

## 8. Verdict

| explanation | verdict |
|---|---|
| **(a) independent risk budgets** | `FALSIFIED` as the *source* — but **necessary**: collapsing to one budget costs 47–87 % of risk-adjusted money because the sleeves are temporally disjoint |
| **(b) different entry timing** | `SUPPORTED` as a description (4.4 % minute overlap; B-MOM's IQR is 09:33–09:39) — but the combiner-only effect is **negative**, so timing is not what pays |
| **(c) the discarded short leg** | ✅ **`SUPPORTED` — this is the mechanism.** +$274/wk, +2.35 pp, −$6,747 top-5 DD, and it is the *only* term with the right sign |
| **(d) merely rescaling** | `FALSIFIED` — everything is matched in contract-minutes, and PORT_XB's advantage survives it |

**Nothing is promoted, demoted or created.** The deliverable is the answer, plus two new waves it
generated: a **long-AND-short fused object** (§3) and a **box-free portfolio** (§4).

## 9. Files
`out/fuse.txt` · `out/fuse_vs_port.csv` · `out/overlap.csv` · `out/rho.csv` · `out/per_year.csv` ·
`out/series.csv` · code `research/weekly_edge/src/run_we_w91.py`
