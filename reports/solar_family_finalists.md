# Solar family finalists — full metric sheet

_2026-08-07 · 3-minute NQ 09-26 back-adjusted · 2022-01-01 → 2026-07-31 · real NT8 slippage of
1 tick per execution · NinjaTrader Brokerage Lifetime commission ($4.36/RT) · all-days daily Sharpe
on the **1,424-session NQ campaign calendar** · strict 1/N ensembles with flat days counted as zero
(`src/analytics/ensembles.py`) · every figure regenerated from the committed execution ledgers._

All three finalists are **ensembles**. None is a single cell, and none may be reduced to one —
PBO for that choice runs 0.48–0.90.

## Head-to-head

| | **R5** adaptive | **R4** fixed | anchor ccHL |
|---|--:|--:|--:|
| members | 13 (`VolMult` 6…30) | 21 (`SM` 170…290) | 10 (`SM`) |
| **daily Sharpe** | **0.977** | 0.892 | 0.912 |
| Sortino | **1.980** | 1.710 | 1.483 |
| Calmar | **0.896** | 0.791 | 0.798 |
| PSR | **0.9929** | 0.9865 | 0.9863 |
| **P(Sharpe ≤ 0)** block bootstrap | **0.0020** | 0.0051 | 0.0102 |
| net | $198,059 | $159,424 | **$215,137** |
| **max drawdown** | −$39,126 | **−$35,669** | −$47,698 |
| expected shortfall (5 % of days) | −$3,594 | −$3,594 | −$5,373 |
| **time under water** | **216 d** | 400 d | 688 d |
| worst quarter | **−$8,613** | −$8,203 | −$21,438 |
| positive quarters | **89 %** | 74 % | 68 % |
| positive years | 5/5 | 5/5 | 5/5 |
| avg trade (per ensemble unit) | **$5.80** | $2.20 | $2.80 |
| profit factor | **1.107** | 1.069 | 1.058 |
| win rate | 39.6 % | 39.5 % | 39.0 % |
| turnover (trades/session) | **1.84** | 2.43 | 5.39 |
| exposure (days with P&L) | 93.5 % | 90.7 % | 92.8 % |
| **ensemble beats its own members** | **13 / 13** | 18 / 21 | 6 / 10 |

**R5 wins on every risk-adjusted measure, on turnover, and on the significance of its absolute
edge.** It loses on gross net profit to the anchor family, which pays for that profit with 22 %
more drawdown, 3× the time under water, 3× the turnover, and a much worse worst quarter.

## Per-year net

| | 2022 | 2023 | 2024 | 2025 | 2026 (part) |
|---|--:|--:|--:|--:|--:|
| **R5** | $41,066 | $12,160 | $29,301 | $60,459 | $55,073 |
| **R4** | $38,556 | $2,583 | $33,622 | $42,944 | $41,719 |
| anchor | $7,023 | $14,621 | $59,781 | $72,313 | $61,399 |

R5 is the most evenly distributed and has by far the best worst year. Note that 2022 is the bear
year — all three are positive in it, which is the strongest temporal evidence the campaign has.

## Long / short decomposition

| | long n | long net | long PF | short n | short net | short PF |
|---|--:|--:|--:|--:|--:|--:|
| **R5** | 15,071 | $147,453 | 1.178 | 19,077 | $50,606 | 1.049 |
| **R4** | 34,398 | $128,392 | 1.119 | 38,200 | $31,032 | 1.025 |
| anchor | 37,056 | $159,604 | 1.090 | 39,751 | $55,534 | 1.029 |

**The long side carries every finalist.** Shorts trade more often and earn a third as much. The
short side has no standalone edge: excluding 2022 and 2025 it is net negative (−$8,397,
Sharpe −0.113). This is a structural dependence, not a tuning opportunity — do not "fix" it by
adding a directional filter without re-checking right-tail retention.

## Concentration and right-tail dependence — read this before scaling

| | top 1 % of trades as share of net | net ex top 10 trades | **net ex top 10 days** |
|---|--:|--:|--:|
| **R5** | **160 %** | $176,771 | **$71,923** (36 % retained) |
| **R4** | 214 % | $149,921 | $55,835 (35 % retained) |
| anchor | 223 % | $200,935 | $103,036 (48 % retained) |

**The bottom 99 % of trades lose money in aggregate.** Removing the ten best *days* costs R5
roughly two-thirds of its profit. This is not a defect — DC01 predicted it from the exponential
overshoot distribution, and it is the mechanical signature of a directional-change system. But it
is the dominant risk, and it means:

- any profit target, position cap, filter or volatility veto **must** be checked for right-tail
  retention before anything else;
- individual trade removal is *not* the right stress test here — daily removal is, and it is much
  harsher;
- fill degradation attacks exactly the trades that carry the system.

## Neighbourhood stability

| | member Sharpe min | median | max |
|---|--:|--:|--:|
| **R5** | 0.479 | 0.707 | 0.955 |
| **R4** | 0.226 | 0.613 | 1.236 |
| anchor | 0.282 | 0.850 | 1.083 |

**R5's ensemble Sharpe (0.977) exceeds its own best member (0.955).** R4's does not — its best
member reaches 1.236 — but that member is unknowable ex ante, which is the whole point: walk-forward
argmax selection earned $16,131 where the median config earned $121,373.

R5's members are also the tightest cluster (range 0.48), meaning the 1/N choice is least
consequential there. Sigma-estimator robustness (H-012) independently confirms this: every
estimator lag from 0.13 to 7.96 sessions gives 0.769–1.494 with 11/13 cells positive in all five
years, so the 460-bar choice is not load-bearing.

## Exact specification of the recommended finalist (R5)

```
Engine     : SolarWaveOpenV3, ThresholdMode = 1        (open model, zero vendor dependency)
             NOT V4 - V4 snaps S to the tick grid and is a different strategy.
             See research/10_v3v4_equivalence/V3_V4_EQUIVALENCE.md
Instrument : NQ 09-26 back-adjusted, 3-minute bars, Last
Core       : anchor = running extreme of the CLOSE since trend start
             flip when close STRICTLY breaks anchor -/+ S
             S = VolMult * sigma, sampled ONCE at trend birth, clamped [40, 1200] ticks
             sigma = causal mean |close - close[1]| over the trailing 460 bars
Entries    : Type-1 flips only (EntrySignalType = 1), long and short
Exits      : the trailing level, plus flat at session close
Ensemble   : equal risk across VolMult = 6, 8, 10, ..., 30 (13 members, 1/N each)
             DO NOT select a VolMult - PBO for that choice is 0.898
Costs      : $4.36/RT commission, 1 tick/execution slippage ($9.5352/RT realised on NQ)
Inert      : TrendMultiplier, SlowdownScan, WeakWeakSplit, PullbackSplit do not enter the
             Type-1 flip rule at all - derived, and verified across 480 combinations
```

## Reasons to accept R5

1. Best Sharpe, Sortino, Calmar, PSR, time under water, worst quarter, turnover and avg trade.
2. Strongest absolute-edge significance: **P(Sharpe ≤ 0) = 0.0020**.
3. Positive in all five calendar years including the 2022 bear year.
4. Beats **all 13** of its own members — the ensemble is doing real work, not averaging.
5. Its mechanism was confirmed by a **preregistered control**: volatility normalisation beats price
   normalisation by +0.728 Sharpe, **p = 0.009** — the campaign's only clean significance result.
6. Fully open implementation with zero vendor dependency.

## Strongest reasons it may fail

1. **Right-tail dependence.** 160 % of net from the top 1 % of trades; 64 % of net from the top 10
   days. Any degradation there destroys it.
2. **It is not statistically separable from R4.** ΔSharpe +0.087, P(Δ ≤ 0) = 0.358; ex-2025 it is
   +0.046. R5 is ranked first on point estimates plus a confirmed mechanism, **not** because it was
   shown to be better.
3. **It does not travel.** ES ensemble Sharpe −0.329, P(Sharpe ≤ 0) = 0.829. Shape transfers
   (Spearman 0.780), level does not.
4. **Deflation cannot certify it.** DSR 0.45–0.55 against a 0.90 bar under the preregistered rule;
   Harvey–Liu haircut Sharpe 0.000.
5. **No clean historical out-of-sample window remains.** ~316 configurations consumed; everything
   through 2026-07-31 was examined during discovery.
6. **The short side is dead weight** and the whole system leans long.
7. **The edge is ~3 % from a no-alpha null.** There is no version of this with a margin of safety.
