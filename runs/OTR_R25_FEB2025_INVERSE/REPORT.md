# OTR_R25_FEB2025_INVERSE — report

Spec preregistered before readout. Directive v4.0 §19 and the §45 Q28 next experiment.
Log: `out/r25_log.txt`, grid: `out/r25_grid.csv`.

## Target recovery (and a free cross-check)

Both days' cropped `gross_loss` cells resolve uniquely on the $5-tick lattice **and are then
confirmed independently by the reported net**, which was not used to derive them:

| day | n | nW | gross profit | gross loss (recovered) | net check |
|---|---|---|---|---|---|
| 2025-02-26 | 15 | 8 | 4,889.56 | **−1,564.76** | 4889.56 − 1564.76 = **3,324.80** ✓ |
| 2025-02-27 | 90 | 35 | 29,306.20 | **−18,222.40** | 29306.20 − 18222.40 = **11,083.80** ✓ |

MAE/MFE sums land on the lattice as expected: 2,855 / 10,435 and 30,770 / 64,480 — all exact
multiples of $5. Commission $5.68/RT (85.20/15 and 511.20/90 both exact).
The two rows chain through `cum_net` (3,324.80 → 14,408.60), so they are **one backtest**,
not two runs. That constraint does most of the work below.

## P1 — FAILED. The 2023 mechanism does not survive into Feb-2025

`2025-02-26` (an ordinary 15-trade day) is **IMPOSSIBLE under T1-only** — both exit rules,
with and without the documented 65-point stop, search run to **exhaustion**, zero paths.

This is the first cent-level proof that the 2023 and 2025 builds are genuinely different
objects rather than the same strategy under different market conditions. Until now the era
split rested on aggregate weekly residuals.

## P2 — HELD, and sharpened. What the 2/27 anomaly actually is

The report needs **90 trades** on 2025-02-27. The day contains only **29 T1 flips**, so
T1-only is structurally impossible there for any search budget — no wrapper can turn 29
flips into 90 single-position trades.

Two candidate explanations were tested and one is eliminated:

**A faster StopMultiplier is eliminated.** Sweeping A2 shows ~90 flips needs A2 ≈ 70 ticks
(17.5 pts) — but the *same* setting produces 86 flips on 2025-02-26, where the report says
15. Since both days are one backtest, no single A2 explains both:

| A2 | 02-26 flips | 02-27 flips | (targets 15 / 90) |
|---|---|---|---|
| 179 (panel value) | 27 | 29 | |
| 100 | 58 | 56 | |
| **70** | 86 | **91** | fits 02-27, breaks 02-26 |
| 40 | 168 | 197 | |

**The real signature is TAKE RATE, not signal supply.** With the panel value A2 = 179 the
total Solar signal supply is almost the same on both days, and it is the fraction consumed
that differs by a factor of five:

| day | T1 | T2 | T3 | total signals | trades taken | take rate |
|---|---|---|---|---|---|---|
| 2025-02-26 | 27 | 56 | 21 | 104 | 15 | **14 %** |
| 2025-02-27 | 29 | 63 | 32 | 124 | 90 | **73 %** |

So 2025-02-27 is **not a faster engine**. It is the same signal stream with the suppression
layer almost entirely absent — and 90 of 124 available signals requires T2 and/or T3 entries,
because T1 alone supplies 29.

Contextual observation, recorded as such: 02-27's day range was **871 points** against
354 on 02-26, the largest in the surrounding week.

## What was NOT completed

The T1+T2 / T1+T3 / T1+T2+T3 cells for 2025-02-27 exceeded the node budget and were stopped:
solving for 90 trades out of 124 candidates is combinatorially far larger than anything in
the 2023 window (16 out of 52 was the worst case there). Those cells are recorded as
**BUDGET_EXCEEDED, i.e. inconclusive** — not as impossible. Closing them needs a different
algorithm (the day-sealing prune that made the 2023 joint problem tractable does not help
inside a single 90-trade day), not more evidence.

## Status changes

| claim | before | after |
|---|---|---|
| 2023 mechanism generalises to 2025 | assumed | **FALSIFIED** at cent level (02-26 infeasible) |
| 2025-02-27 = "a faster build" | INFERENCE | **narrowed**: not faster signal generation; a ~5× higher take rate on an ordinary signal supply |
| 2025-02-27 = "one-off experiment" | INFERENCE | still INFERENCE; no mechanism identified |
| 2025-02-27 explicable by T1 entries | open | **impossible** (29 flips vs 90 trades) |
| a single A2 explains both Feb days | open | **FALSIFIED** |

## Next

The 2/27 cell needs a solver that exploits the *within-day* structure (e.g. sealing on
cumulative sub-totals, or a DP over the tick lattice) rather than DFS over 124 candidates.
That is an engineering step with no new evidence required, and it is the cheapest remaining
route to the oldest open anomaly in the campaign.
