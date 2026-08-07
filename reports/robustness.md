# Robustness — final, 2026-08-07

_Two layers: the frozen baseline (Phase 0, unchanged and still valid) and the finalist ensembles
(current). All finalist figures on the 1,424-session NQ campaign calendar, real slip-1._

## 1. Determinism — the foundation

7 bit-identical canonical runs (5 serial + 2 concurrent); ledger hash `fe395c148444abba…`.
Optimization-sweep iterations bit-identical to standalone runs. **Attacked by the red team and
held.** The open model adds 45/45 passing property tests including no-look-ahead, parameter
isolation and bit-identical reruns ([`open_model_validation.md`](open_model_validation.md)).

## 2. Cost stress — the frozen baseline (canonical Type 1, 1-minute)

| slip | net | PF | Sharpe(d) | Calmar | worst Q | max TUW |
|--:|--:|--:|--:|--:|--:|--:|
| 0 | $146,440.60 | 1.132 | 1.72 | 3.59 | −$2,427 | 69 d |
| 1 | $118,645.60 | 1.106 | 1.39 | 2.56 | −$4,885 | 133 d |
| 2 | $91,935.60 | 1.081 | 1.08 | 1.67 | −$8,155 | 160 d |
| 3 | $66,300.60 | 1.058 | 0.78 | 1.04 | −$11,250 | 160 d |

NT8 slippage is bar-capped: ~95 % of executions realize the full tick, so **1 tick is the honest
basis** and every finalist figure in this repository already includes it. Slip-2 roughly halves
net; slip-3 would erase it. This is the sharpest economic sensitivity in the system.

## 3. Finalist robustness

| | **R5** | **R4** | anchor |
|---|--:|--:|--:|
| daily Sharpe | **0.977** | 0.892 | 0.912 |
| Sortino | **1.980** | 1.710 | 1.483 |
| max drawdown | −$39,126 | **−$35,669** | −$47,698 |
| expected shortfall (worst 5 % of days) | −$3,594 | −$3,594 | −$5,373 |
| **time under water** | **216 d** | 400 d | 688 d |
| worst quarter | **−$8,613** | −$8,203 | −$21,438 |
| positive quarters | **89 %** | 74 % | 68 % |
| positive years | 5/5 | 5/5 | 5/5 |
| P(Sharpe ≤ 0), block bootstrap | **0.0020** | 0.0051 | 0.0102 |
| ensemble beats its members | **13/13** | 18/21 | 6/10 |

**Temporal stability.** All three are positive in every calendar year 2022–2026, including the
2022 bear year. R5's spread is $41k/$12k/$29k/$60k/$55k — the most even, and the best worst year.

**Parameter-neighbourhood stability.** R5 member Sharpes span 0.479–0.955 (median 0.707) — the
tightest cluster, so the 1/N choice matters least there. Independently, every σ-estimator lag from
0.13 to 7.96 sessions gives 0.769–1.494 with 11/13 cells positive in all five years (H-012), so the
460-bar choice is not load-bearing.

**Tail-risk modelling.** Block-vs-iid 5th-percentile drawdown ratio **0.987** — the iid assumption
was not hiding tail risk (DR06-H5 falsified).

## 4. Known fragilities — carry these into every review

1. **Right-tail dependence is the dominant risk.** Top 1 % of trades supply **160 %** (R5) /
   **214 %** (R4) of net profit — the bottom 99 % lose money in aggregate. Removing the top 10
   **days** leaves 36 % / 35 % of net. Trade-level removal is far too gentle a stress here; use
   day-level. **Any filter, veto, profit target or position cap must be checked for right-tail
   retention before anything else.**
2. **The short side has no standalone edge.** Excluding 2022 and 2025 it is net negative
   (−$8,397, Sharpe −0.113). Every finalist leans long (R5 long PF 1.178 vs short 1.049).
3. **Exit-reason concentration.** On the frozen baseline all net edge sits in session-close-exited
   trades; Solar-exit trades net negative. The edge lives in trends still running at the close —
   which is also why H-007 and the 16:30 exit both failed.
4. **Time under water doubles at realistic costs** on the baseline (69 d → 133 d at slip-1).
5. **The edge is ~3 % from a no-alpha null.** No version of this has a margin of safety.
6. **No clean historical out-of-sample window remains.** ~316 configurations consumed.

## 5. Validation that was run — and what it concluded

| method | result |
|---|---|
| CSCV / PBO | **0.48–0.90** with a negative IS→OOS slope in every family → parameter selection is not learnable |
| walk-forward argmax | earned **$16,131** where the median config earned $121,373 |
| circular block bootstrap, absolute edge | P(Sharpe ≤ 0) = 0.0020 / 0.0051 / 0.0102 → **the edge is real** |
| paired block bootstrap, comparative | R5 vs R4 P(Δ ≤ 0) = 0.358 → **no ranking is established** |
| DSR under the preregistered rule | 0.45–0.55 vs a 0.90 bar; Harvey–Liu haircut Sharpe 0.000; alternative pool gives 0.96 → **cannot adjudicate** |
| ES portability | ensemble Sharpe −0.329, P(Sharpe ≤ 0) = 0.829 → **failed** |

**The pattern across all six: absolute-edge tests pass, every comparative test fails.** On 4.6
years of one instrument the data supports "something is here" and refuses to say "this version is
better than that one." That is the campaign's central statistical finding and the reason the
deliverable is an unselected ensemble.
