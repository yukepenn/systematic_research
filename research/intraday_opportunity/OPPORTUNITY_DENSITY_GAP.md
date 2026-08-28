# OPPORTUNITY-DENSITY GAP — reference trader vs the incumbent

**Directive §5 / §32.** Decomposition, not a strategy.
Reproducible: `src/opportunity_gap.py` · `src/incumbent_density.py`.

> # ⚠️ **THIS DOCUMENT'S FIRST VERSION CONTAINED A MATERIAL ERROR, AND IT PROPAGATED INTO THE OWNER'S DIRECTIVE.**
> It asserted **"`P1/PCT` is RTH only, flat at every session close"** and divided P1's dollars by
> **6.5 hours**. **FALSE.** Measured from the ledger's own decision timestamps, **`P1/PCT` places
> entries in 23 of 24 hours — every hour except 17:00, the CME maintenance break. 61.7 % of its
> entries and 45.7 % of its net fall OUTSIDE 09:00–15:59 ET.**
> The phrase *"flat at every session close"* means the **17:00 SESSION close**, not the 16:00 RTH
> close. I read it as RTH without checking. **The consequence is that GAP B — "P1 uses only 6.5 of
> 23 hours" — IS FALSE AND IS RETRACTED (§7).**

---

## 1. Side by side

| quantity | REFERENCE (backtest) | `P1/PCT` (research) |
|---|---:|---:|
| trades | 4,351 | 2,131 |
| sessions | 526.8 (NT8 implied) | **1,058 total · 638 active** |
| trades per session | **8.26** | 2.014 calendar · **3.340 active** |
| net | $292,172.82 | $296,910.84 |
| **NET PER TRADE** | **$67.15** | **$139.33** |
| net per session | $554.62 | $465.38 active |
| win rate | 40.29 % | ~35 % |
| mean hold | 94.15 min | 86.92 min (median 24) |
| direction | 2,166 L / 2,185 S — **two-sided** | 2,131 L / 0 S — **long-only** |
| max drawdown | $32,677.42 | **$22,930.67** |
| **slippage charged** | **$0.00 — NONE** | **$14.44/ctrRT modelled spread** |

## 2. ⭐ It is EXPOSURE TIME, not operating window

Both objects have the same 23-hour session available and **both use essentially all of it.**

| | REFERENCE | `P1/PCT` | |
|---|---:|---:|---|
| **in-market hours per session** | **12.96** | **4.84** | reference exposed **2.68× longer** |
| trades per **available** hour (23 h) | 0.359 | 0.145 | reference **2.47×** |
| net $ per **available** hour | $24.11 | $20.23 | reference **1.19×** |
| **net $ per IN-MARKET hour** | **$42.79** | **$96.18** | **P1 2.25×** |
| same, reference **re-costed** | **$33.47** | **$96.18** | **P1 2.87×** |

> ### **The reference stands in the market 2.7× longer and earns less than half as much per hour of
> ### exposure. On a common cost model, P1 earns 2.87× more per in-market hour.**

## 3. Equalize the cost model

| | |
|---|---:|
| reference net as posted | $292,172.82 |
| less P1's modelled spread, $14.44/ctrRT × 4,351 | **−$62,828.44** |
| less commission top-up | −$783.18 |
| **= reference net on P1's cost model** | **$228,561.20 (−21.8 %)** |
| **reference net per trade, re-costed** | **$52.53** vs P1's **$139.33** |

**Charging him the spread P1 pays removes 21.5 % of his entire net** — turnover is what friction
taxes, and he has 2× the turnover on half the edge.

## 4. Common fixed drawdown

| | weekly $ | maxDD | k | **@ fixed $20,245 DD** |
|---|---:|---:|---:|---:|
| REFERENCE as posted (0 slippage) | $2,773.09 | $32,677.42 | 0.6195 | **$1,718.04** |
| REFERENCE re-costed on P1's model | $2,169.34 | $32,677.42 | 0.6195 | **$1,343.99** |
| **`P1/PCT`** | $1,393.57 | $22,930.67 | 0.8829 | **$1,230.36** |

**As posted 1.40× · re-costed `1.09×`** ← the honest number.

> ⚠️ **And 1.09× still flatters him:** his maxDD spans **~2.1 years** vs P1's **~4.1** (drawdown grows
> with observation length) · paying the spread would have **deepened** it · and his parameters were
> **re-tuned every 1–3 weeks** with the master run made the night before deployment, so the grid is
> **in-sample to himself**.

## 5. Attribution of the posted $1,379.52/wk gap

| term | worth | direction |
|---|---:|---|
| **EXPOSURE TIME** — 12.96 in-market h/day vs P1's 4.84 | **$1,737.81/wk** | creates his advantage |
| **COST MODEL** — his backtest charges no spread | **$603.75/wk** | creates his advantage |
| ~~SESSION LENGTH~~ | **RETRACTED** | P1 already trades 23 of 24 hours |
| **EDGE PER TRADE** — $139.33 vs $67.15 | 2.07× | **P1** |
| **EDGE PER IN-MARKET HOUR** — $96.18 vs $42.79 ($33.47 re-costed) | 2.25–2.87× | **P1** |
| **RISK** — maxDD $22,931 vs $32,677 | 1.43× | **P1** |

⚠️ **Exposure time is not free.** It is a hold-time and trade-count property, and it carries
**overnight gap risk and off-hours spread that his zero-slippage backtest never paid.**

## 6. ⭐ The incumbent's marginal-trade economics — the overtrading story is dead

Session-clustered (§28), 5,000 resamples of sessions:

| ordinal | n | mean/trade | 95 % CI | P(mean>0) |
|---|---:|---:|---:|---:|
| 1st | 638 | $146.76 | [17, 285] | 0.989 |
| 2nd | 460 | $147.22 | [−19, 363] | 0.953 |
| **3rd** | 335 | **$66.40** | [−73, 218] | 0.811 |
| 4th–5th | 371 | $145.60 | [9, 300] | 0.982 |
| **6th+** | 327 | **$181.33** | **[24, 375]** | **0.989** |

**Ordinals 5–8 earn $180.88/trade on 17 % of decisions.** The only bad tail is **ordinal ≥ 9** —
4.7 % of decisions, −$112.70/trade. Hold time **shrinks** with ordinal (37 → 10 min). **Capping at
any K < 8 loses money** (cap 3 costs −$113,312).

⚠️ **Not a lever** — `WE_W121` found entry-count caps at the **0.0 / 4.0 / 1.0 / 0.0th percentile** of
a count-matched random-halt placebo: *removing the same number of entries at random does better than
removing them by the rule.* ⛔ **No cap is selected here (§31, §42).**

## 7. So where IS the incumbent sparse? — one gap, not two

| | |
|---|---|
| ⛔ **not** re-entry | 3.340 trades/active session, median 3, p90 7, **max 19** |
| ⛔ **not** later-trade decay | ordinals 5–8 are its **best** bucket |
| ⛔ **not** coverage of big moves | **0.38 %** (`RR_W006`) |
| ⛔ **not** turnover policy | caps are **worse than random** |
| ⛔ ~~**not** session length~~ | **RETRACTED — it already trades 23 of 24 hours** |
| ✅ **the arming condition is rare** | **`P1/PCT` is COMPLETELY FLAT on 420 of 1,058 sessions = 39.7 %** |
| 🔶 secondary, and not free | it is **in-market 4.84 h** per active session vs the reference's 12.96 |

> # **THE ANSWER TO "WHY CAN'T WE TRADE BACK AND FORTH ALL DAY?"**
> ## **We already do — around the clock, on the days we trade at all, and those re-entries pay.**
> ## **The one real hole is that on four sessions in ten we never arm at all.**
> The reference trader does not out-trade us per hour of exposure — he earns **less than half** as
> much per in-market hour, on a backtest that charges **no slippage**. What he has is **2.7× more
> time in the market**.

## 8. What this licenses, and what it forbids

**One live lane:** the **39.7 % flat-session gap** — is there a causally-armable state on sessions
where `P1/PCT` never fires? Largest single term, **untested**.

**One lane closed by measurement, before any economics:** ⛔ **the off-hours lane. There is no
off-hours coverage gap** — the premise was my own error.
🔶 What survives of it is a **different and harder** question — *in-market time*, i.e. hold length
and trade count — which is **not** a window property and cannot be had for free.

⛔ **Forbidden:** treating **8.26 trades/day** as a target · treating **$10k weeks** as an
expectation (his own worst week is **−$42,235**) · using his numbers to validate anything · any
claim about *his* later-trade economics, which is **UNKNOWABLE** from a corpus of 13 daily rows and
no per-trade record.

**LIVE ENABLED = NO.**
