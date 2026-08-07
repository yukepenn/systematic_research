# Robustness — baseline reference (SW00, 2026-08-06)

## Determinism
7 bit-identical canonical runs (5 serial + 2 concurrent) + 1 extra observation; ledger hash `fe395c148444abba…`. Optimization-sweep iterations bit-identical to standalone runs.

## Cost stress (canonical Type 1)
| Slip | Net | PF | Sharpe(d) | Calmar | Worst Q | Max TUW |
|---|---|---|---|---|---|---|
| 0 | $146,440.60 | 1.132 | 1.72 | 3.59 | −$2,427 | 69d |
| 1 | $118,645.60 | 1.106 | 1.39 | 2.56 | −$4,885 | 133d |
| 2 | $91,935.60 | 1.081 | 1.08 | 1.67 | −$8,155 | 160d |
| 3 | $66,300.60 | 1.058 | 0.78 | 1.04 | −$11,250 | 160d |

NT8 slippage is bar-capped: ~95% of executions realize the full tick → treat 1-tick figures as the honest basis, check 2-tick at every promotion.

## Temporal stability (slip 0)
Positive every calendar year (2023 PF 1.10 / 2024 PF 1.14 / 2025-Jan PF 1.24); 77.8% of quarters positive; both directions positive (Long PF 1.20, Short PF 1.07).

## Concentration / right tail
Top-decile winners = 32.7% of gross profit; net after removing top 1/3/5/10 trades: $139.1k/$124.7k/$112.7k/$87.4k; top-5 winners span 5 distinct months and both directions.

## Known fragilities (carry into every review)
1. Exit-reason concentration: all net edge sits in session-close-exited trades; Solar-exit trades net negative → refinements must attack giveback without amputating runners.
2. Long/short asymmetry (PF 1.20 vs 1.07) — diagnose, don't parameterize yet.
3. TUW doubles at realistic costs — drawdown-duration risk is cost-sensitive.
4. Pending: WFO fold evaluation, DSR/PBO accounting (starts when candidates exist; registry counts every config from seq 1).
