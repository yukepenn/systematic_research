# Leaderboard — final, 2026-08-07

_Ranked by **daily Sharpe**, never by net profit. 3-minute NQ, real slip-1, Lifetime commission,
all-days Sharpe on the 1,424-session NQ campaign calendar, strict 1/N ensembles with flat days
counted as zero. Regenerated from the committed execution ledgers; machine-readable copy in
[`final_pareto.csv`](final_pareto.csv)._

**Every entry is an ensemble. No single cell is promotable** — PBO for that choice runs 0.48–0.90
with a negative in-sample→out-of-sample slope in every family.

| # | candidate | status | Sharpe | net | max DD | Calmar | worst yr | pos yrs | P(SR ≤ 0) |
|--:|---|---|--:|--:|--:|--:|--:|--:|--:|
| **1** | **R5** adaptive `S = k·σ`, 13 cells | **RECOMMENDED** | **0.977** | $198,059 | −$39,126 | 0.896 | +$12,160 | 5/5 | **0.0020** |
| 2 | anchor close-confirmed HL, 10 cells | PASS but redundant with R5 | 0.912 | $215,137 | −$47,698 | 0.798 | +$7,023 | 5/5 | 0.0102 |
| 3 | **R4** fixed, all 21 cells | reference | 0.892 | $159,424 | −$35,669 | 0.791 | +$2,583 | 5/5 | 0.0051 |
| — | C2 T1 core + one T3 re-entry, 8 cells | **REJECTED** | 0.850 | $233,628 | −$47,413 | 0.872 | +$19,801 | 5/5 | 0.0074 |
| — | R4b fixed plateau, 8 cells | superseded by R4 | 0.773 | $180,479 | −$53,689 | 0.595 | +$7,796 | 5/5 | 0.0170 |

**Read the ranking carefully.** The two highest *net profit* entries are rejected or redundant.
C2 would top a profit-ranked table and it is the campaign's clearest rejection: it failed its
interaction test (−0.402 Sharpe on an adaptive core, P = 0.879). This is exactly why the campaign
constitution forbids ranking by net profit.

## Why R5 over the anchor family

The anchor family earns 9 % more gross and pays for it with 22 % more drawdown, **3× the time
under water** (688 d vs 216 d), 3× the turnover, a much worse worst quarter (−$21,438 vs −$8,613),
and a weaker absolute-edge significance. It is also **redundant**: once the threshold is
volatility-normalised, the anchor refinement adds nothing (combo 1.011 vs adaptive-alone 1.010).
Both axes scale filter sensitivity to bar volatility. The simpler model is promoted.

## What R5 is *not* shown to be

R5 over R4 is **not statistically established**: ΔSharpe +0.087, P(Δ ≤ 0) = 0.358; ex-2025 it is
+0.046. R5 is ranked first on point estimates plus a mechanism confirmed by a preregistered control
(H-014, p = 0.009) — not because it was demonstrated to be better.

## Mapped out and dead

| | evidence |
|---|---|
| single-cell selection (any family) | PBO 0.48–0.90; walk-forward argmax earned $16,131 where the median config earned $121,373 |
| 1-minute vs 3-minute | 3m dominates after costs at every comparable threshold |
| SM ≤ 160 on 1m | negative after costs |
| unconditional Type 2 / Type 0 cores | cost-fragile; C4 costs 0.33 Sharpe; raw Type-0 ≈$123k vs Type-1 ≈$162k |
| raw High/Low anchor | Sharpe 0.527 — the ladder chases wicks |
| split exit ≠ reversal (H-007) | monotone degradation; no-split best everywhere |
| stop-order execution (H-011) | negative in 10/10 cells, −$1.88M |
| price-proportional threshold (H-014 control) | Sharpe 0.250, p = 0.999 vs volatility |
| 16:30 timed exit | wins 4/28 matched pairs, median −$12,476 |
| wave-index conditioning | 0.54–0.93, non-monotone |
| flip-count chop veto (SW05) | inverted — would delete 74 % of profit |
| **ES portability** | ensemble Sharpe −0.329, P(Sharpe ≤ 0) = 0.829 |

Full detail per finalist: [`solar_family_finalists.md`](solar_family_finalists.md).
The case against all of it: [`final_red_team.md`](final_red_team.md).
