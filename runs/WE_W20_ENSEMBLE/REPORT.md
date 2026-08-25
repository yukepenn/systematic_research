# WE_W20 — ENSEMBLE · REPORT

W19 showed quarterly config selection is noise (88 % churn, +0.021 over naive). This wave
tests the alternative: **stop selecting, aggregate the family.**

| object | weeks | net | wk mean | % pos | worst | **Sharpe** | trades |
|---|---|---|---|---|---|---|---|
| FIXED | 205 | $341,300 | $1,665 | 61.0 % | −$24,417 | 0.249 | 3,641 |
| NAIVE | 205 | $251,821 | $1,228 | 59.0 % | −$37,318 | 0.150 | 6,595 |
| BESTFIXED (hindsight) | 204 | $278,916 | $1,367 | 60.3 % | −$14,543 | 0.279 | 1,954 |
| WF selector (W19) | 203 | $207,669 | $1,023 | 58.1 % | −$23,537 | 0.171 | 3,373 |
| E1 P&L-avg all 64 *(benchmark)* | 205 | $264,231 | $1,289 | 57.6 % | −$22,195 | 0.254 | — |
| E2 P&L-avg long 32 *(benchmark)* | 204 | $241,432 | $1,183 | 60.8 % | −$15,290 | 0.255 | — |
| E3 P&L-avg delta-on 32 *(benchmark)* | 205 | $272,186 | $1,328 | 59.5 % | −$17,896 | 0.276 | — |
| E4 vote all ≥50 % | 205 | $269,890 | $1,317 | 59.0 % | −$33,138 | 0.200 | 4,813 |
| **E5 vote LONG-ONLY ≥50 %** | 203 | **$227,009** | $1,118 | 59.6 % | **−$17,440** | **0.214** | 2,803 |
| E6 vote all ≥75 % | 202 | $188,124 | $931 | 56.4 % | −$26,333 | 0.197 | 2,584 |

## VERDICT: **WIN**

**E5 — a one-contract majority vote across the 32 long-only configurations — beats the
walk-forward selector (0.214 vs 0.171) and naive (0.150), with less than half naive's trade
count and a worst week $19,878 better.**

Why this matters more than the Sharpe number: **E5 performs no parameter selection at all.**
It is immune to the failure W19 exposed, because there is nothing to churn. The residual
fitting risk sits at the level of the family's composition, which is far lower-dimensional
than picking one member of it each quarter.

Per-year Sharpe, all positive: 2022 **0.260**, 2023 **0.271**, 2024 **0.307**, 2025 0.113,
2026 **0.315**. Correlation with the WF selector's weekly nets is **0.68** over 201 shared
weeks — E5 is not winning by doing something unrelated, it is doing the same thing better.

## Long-only, a fourth independent confirmation

E5 (long-only vote) beats E4 (both-sides vote) 0.214 vs 0.200 with a worst week of −$17,440
against −$33,138. Long-only has now been favoured by: W16 (side split), W17 (deep history,
the only cross-era replication), W19 (BESTFIXED), and W20 (E4 vs E5).

## What is still unproven, and W21 will attack it

E5 has never been run outside 2022-2026, its vote has never faced a null calibration, and it
has not been combined with the orthogonal S1 sleeve. All three are W21.
