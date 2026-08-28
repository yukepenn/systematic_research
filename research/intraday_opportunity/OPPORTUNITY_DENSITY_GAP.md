# OPPORTUNITY-DENSITY GAP — reference trader vs the incumbent

**Directive §5 / §32.** Decomposition, not a strategy. Reproducible:
`src/opportunity_gap.py` · `src/incumbent_density.py`.

> # **THE HEADLINE**
> ## **Per hour of available market, `P1/PCT` already trades MORE OFTEN (1.43×) and earns ~3× MORE than the reference trader's own posted backtest.**
> ## **His edge per trade is `$67.15`. `P1/PCT`'s is `$139.33` — 2.07× — and P1 pays a spread his backtest never charged.**
> ## **Re-cost his own backtest on P1's cost model and normalize to P1's drawdown, and his advantage collapses from 1.40× to `1.09×`.**

---

## 1. Side by side

| quantity | REFERENCE (backtest) | `P1/PCT` (research) |
|---|---:|---:|
| trades | 4,351 | 2,131 |
| sessions | 526.8 (NT8 implied) | **1,058 total · 638 active** |
| **trades per session** | **8.26** | **2.014 calendar · 3.340 active** |
| net | $292,172.82 | $296,910.84 |
| **NET PER TRADE** | **$67.15** | **$139.33** |
| net per session | $554.62 | $465.38 active · $280.63 calendar |
| win rate | 40.29 % | ~35 % |
| mean hold | 94.15 min | 86.92 min (**median 24**) |
| direction | 2,166 L / 2,185 S — **two-sided** | 2,131 L / 0 S — **long-only** |
| max drawdown | $32,677.42 | **$22,930.67** |
| **slippage charged** | **$0.00 — NONE** | **$14.44/ctrRT modelled spread** |

## 2. ⭐ The session-length artifact — the single biggest term

```
reference in-market minutes/day = 8.26 trades × 94.15 min = 777.7 min = 13.0 HOURS
RTH is 390 min (6.5 h)          →  RTH-ONLY IS ARITHMETICALLY IMPOSSIBLE
```

His panel carried `TradingHours = "Use instrument settings"` — the **full 1,380-minute
18:00 → 17:00 ET session** — and a measured overnight hold exists (a long 21:39 → 06:44,
**+$2,270.82**). **`P1/PCT` is flat at every session close.**

| per **available market hour** | REFERENCE | `P1/PCT` | ratio |
|---|---:|---:|---:|
| trades per hour | 0.359 | **0.514** | **1.43× in P1's favour** |
| **net dollars per hour** | $24.11 | **$71.60** | **2.97× in P1's favour** |

> ### **He is not finding more opportunities per unit of market. He is standing in front of the
> ### market 3.5× longer.**

## 3. Equalize the cost model — a high-turnover object is far more exposed to friction

| | |
|---|---:|
| reference net as posted | $292,172.82 |
| less P1's modelled spread, $14.44/ctrRT × 4,351 | **−$62,828.44** |
| less commission top-up ($4.36 − $4.18)/RT | −$783.18 |
| **= reference net on P1's cost model** | **$228,561.20 (−21.8 %)** |
| **reference net per trade, re-costed** | **$52.53** vs P1's **$139.33** |

**Charging him the spread P1 pays removes 21.5 % of his entire net** — because turnover is the thing
friction taxes, and he has 2× the turnover on half the edge.

## 4. Common fixed drawdown

| | weekly $ | maxDD | k | **@ fixed $20,245 DD** |
|---|---:|---:|---:|---:|
| REFERENCE as posted (backtest, 0 slippage) | $2,773.09 | $32,677.42 | 0.6195 | **$1,718.04** |
| REFERENCE re-costed on P1's cost model | $2,169.34 | $32,677.42 | 0.6195 | **$1,343.99** |
| **`P1/PCT`** (research, spread included) | $1,393.57 | $22,930.67 | 0.8829 | **$1,230.36** |

| | ratio to P1 |
|---|---:|
| as posted | **1.40×** |
| **re-costed** | **1.09×** ← the honest number |

> ### ⚠️ **AND 1.09× STILL FLATTERS HIM, for three reasons that are not corrected above:**
> **(a)** his maxDD spans **~2.1 years**, P1's **~4.1** — drawdown grows with observation length, so
> the shorter window gets the smaller denominator and the larger fixed-DD figure.
> **(b)** paying the spread would have **deepened** his drawdown, lowering `k` further.
> **(c)** his parameters were **re-tuned every 1–3 weeks** and the master run was made the night
> before deployment — the grid is **in-sample to himself**. P1's window is discovery-consumed too,
> but P1's figure is at least a walk-forward-refit object.
>
> **A defensible reading is that the reference sleeve and `P1/PCT` are economically comparable, and
> that the visible difference is session length, friction accounting and drawdown tolerance.**

## 5. Where the posted gap comes from — attribution

Posted weekly gap, raw and unnormalized: **$1,379.52/wk**.

| term | worth | direction |
|---|---:|---|
| **SESSION LENGTH** — 23 h available vs P1's 6.5 h RTH | **$1,989.39/wk** | creates his advantage |
| **COST MODEL** — his backtest charges no spread | **$603.75/wk** | creates his advantage |
| **EDGE PER TRADE** — $139.33 vs $67.15 | 2.07× | **in P1's favour** |
| **RISK** — maxDD $22,931 vs $32,677 | 1.43× | **in P1's favour** |

**The two terms that create his advantage more than account for the entire posted gap.** The two
terms where P1 is ahead are the two that actually matter for compounding capital.

## 6. ⭐ The incumbent's marginal-trade economics — measured, and it kills the overtrading story

`baseline_trade_net` by entry ordinal, **session-clustered** (§28 — a system taking 8 trades/day does
**not** have 8 independent observations/day; 5,000 resamples of *sessions*):

| ordinal | n | mean/trade | 95 % CI | P(mean>0) |
|---|---:|---:|---:|---:|
| 1st | 638 | $146.76 | [17, 285] | 0.989 |
| 2nd | 460 | $147.22 | [−19, 363] | 0.953 |
| **3rd** | 335 | **$66.40** | [−73, 218] | 0.811 |
| 4th–5th | 371 | $145.60 | [9, 300] | 0.982 |
| **6th+** | 327 | **$181.33** | **[24, 375]** | **0.989** |

Finer split: **ordinals 5–8 earn $180.88/trade on 17 % of decisions**; the only genuinely bad tail is
**ordinal ≥ 9 — 4.7 % of decisions, −$112.70/trade, −$11,383 of a $296,911 book.**
Hold time **shrinks** with ordinal (37 → 10 min). The saturation curve: capping at **any K < 8 loses
money** (cap 3 costs **−$113,312**).

> ### **For the incumbent, later same-day trades do NOT decay. The engine already re-arms, the
> ### re-entries pay, and the 4th entry is the single best cell ($253.53 against a $139.33 mean) —
> ### which independently reproduces `WE_W121`'s published finding.**

⚠️ **This is not a lever, and `WE_W121` already tested it**: entry-count caps lose at every K and sit
at the **0.0 / 4.0 / 1.0 / 0.0th percentile** of a count-matched random-halt placebo —
*removing the same number of entries at random does better than removing them by the rule*. **Trade
ordinal carries negative information about which entry to drop.** ⛔ **Per §31 and §42, no cap is
selected from any curve here.**

## 7. So where IS the incumbent actually sparse?

| | |
|---|---|
| ⛔ **not** re-entry | it takes **3.34 trades per active session**, median 3, p90 7, **max 19** |
| ⛔ **not** later-trade decay | ordinals 5–8 are its **best** bucket |
| ⛔ **not** coverage | correctly scoped, **4 sessions of 1,058 = 0.38 %** |
| ⛔ **not** turnover policy | caps are **worse than random** |
| ✅ **the arming condition is rare** | **`P1/PCT` is COMPLETELY FLAT on 420 of 1,058 sessions = 39.7 %** |
| ✅ **and the day is short** | RTH only, flat at every close, while the instrument trades 23 h |

> # **THE ANSWER TO "WHY CAN'T WE JUST TRADE BACK AND FORTH ALL DAY?"**
> ## **We already do, on the days we trade at all — and those trades pay. What we do not do is
> ## show up on four sessions in ten, or stay past 16:00.**
> **The reference trader does not out-trade us per hour. He is simply present far more hours, on a
> two-sided engine, at half the edge per trade and 1.4× the drawdown — with a backtest that charges
> no slippage.**

## 8. What this licenses, and what it forbids

**Licensed as the next question** — and only as a *question*, requiring its own preregistration:

1. **the 39.7 % flat-session gap** — is there a causally-armable state on sessions where `P1/PCT`
   never fires? This is the largest single term and it is **untested**;
2. **the session-length gap** — the instrument trades 23 h and the incumbent uses 6.5. ⚠️ This is
   where the reference's whole advantage lives, and it is also where **friction and overnight risk
   live**. It must be costed before it is admired.

⛔ **Forbidden by this document:** treating **8.26 trades/day** as a target · treating **$10k weeks**
as an expectation (his own worst week is **−$42,235**) · using his numbers to validate anything —
**he can motivate the hypothesis, he cannot validate it** · any claim about *his* later-trade
economics, which is **UNKNOWABLE** from a corpus that contains 13 daily rows and no per-trade record.

**LIVE ENABLED = NO.**
