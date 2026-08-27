# WE_W120 — is W118's mirror continuation a new engine, or more of what P1 owns? · REPORT

Preregistered (`spec.yaml`, committed at `5677472` before any code was written).
POST-W118 owner directive §§23, 24, 26, 28, LANE C. Object frozen exactly as W118 built it, direction
flipped, **nothing else changed**.

> ## **FAILS the preregistered four-gate test — on gate 2, and gate 2 only. Classification: NOT a diversifying candidate.**
> ## But it is **by a distance the strongest portfolio candidate this campaign has produced**, and it passes **both gates FOLLOW_MORNING failed**. Adding it takes the book's max drawdown **$11,489 → $8,143 (−29 %)** and fixed-DD weekly **$2,012 → $2,414**, positive at *both* weighting conventions.
> ## **The mechanism is TAIL, not average.** Session-level it is *pro*-cyclical — **+$1,315 when the book wins, −$297 when the book loses**. Weekly, in the book's worst decile, its **tail beta is −1.861 at the 0.9th percentile** of a circular-shift null. It is unhelpful in the middle of the distribution and strongly helpful in the tail.

## 1. Standalone dashboard (§29)

R = 0.50, gate = 0.50 — W118's primary cell, direction flipped. **347 trades, $407/trade, net $141,162.**

| window | N | $/trade | edge pp | hit % | net $ | wk $ |
|---|---|---|---|---|---|---|
| t3m | 41 | **$1,243** | **+13.22** | 63.4 % | $50,971 | $238 |
| t6m | 65 | $884 | +5.17 | 55.4 % | $57,487 | $269 |
| **t12m** | 108 | **$811** | **+10.87** | 61.1 % | $87,554 | $409 |
| YTD 2026 | 75 | $844 | +8.44 | 58.7 % | $63,278 | $296 |
| prior yr 2025 | 92 | $417 | +4.13 | 54.3 % | $38,374 | $179 |
| t24m | 219 | $337 | +3.19 | 53.4 % | $73,710 | $344 |
| 2022-current | 347 | $407 | +5.50 | 55.6 % | $141,162 | $660 |
| *2006–2021 (diagnostic)* | 1,394 | **−$14** | — | 47.3 % | −$20,118 | — |

**Recency is strong and strengthening** — t12m $811 against a full-window $407. ⚠️ **t3m and t6m sit
inside the BURNED span** (2026-05-31 → 07-31) and are not independent evidence; **t12m is the
defensible recent figure.** And it is absent in 2006–2021, consistent with every other continuation
measurement in this campaign.

## 2. Redundancy — session level says pro-cyclical

Trades on **347 of 1,058** sessions (32.8 %). ρ with P1/PCT **0.388**, with XM **0.258**, with the
book **0.450**.

| slice *(ex-post diagnostic, never an input)* | N | MIRROR $/trade | unconditional | difference |
|---|---|---|---|---|
| all MIRROR trade sessions | 347 | $407 | $407 | — |
| … where **P1/PCT lost** that session | 129 | $277 | $407 | −$130 |
| … where **XM lost** that session | 50 | **−$1,048** | $407 | −$1,455 |
| … where the **BOOK lost** that session | 138 | **−$297** | $407 | **−$704** |
| … where the **BOOK won** that session | 126 | **+$1,315** | $407 | **+$908** |

> **At session resolution it is redundant in the plain sense**: it makes its money on the same
> sessions the book makes money, and loses on the same sessions the book loses. On the 50 sessions
> where XM lost, it lost **−$1,048** — the two share their worst days.

## 3. Portfolio — and here it reverses

| statistic vs the book | REAL | null mean | null p95 | percentile |
|---|---|---|---|---|
| ρ, all weeks | +0.145 | −0.001 | +0.099 | 99.5th |
| **ρ ∣ book losing** | **−0.158** | +0.001 | +0.173 | 7.5th ✅ |
| P(cand<0 ∣ book<0) | 0.310 | 0.329 | 0.379 | 24.5th ✅ |
| **worst-decile overlap** | **0.019** | 0.011 | 0.023 | 80.2nd ✅ |
| **$ on book-losing weeks** | **+$614** | **+$663** | +$1,247 | **42.9th** ❌ |
| **tail beta** (book's worst decile) | **−1.861** | +0.009 | +1.014 | **0.9th** ✅ |

| book | convention | wk $ | max DD | **wk$@fixDD** | pos wk % | CVaR5 |
|---|---|---|---|---|---|---|
| P1/PCT + XM | inv-vol | $1,142 | $11,489 | $2,012 | 59.2 % | −$4,737 |
| **+ MIRROR_CONT** | inv-vol | $971 | **$8,143** | **$2,414** | **62.4 %** | **−$4,112** |
| P1/PCT + XM | income | $1,105 | $12,533 | $1,785 | 60.1 % | −$4,971 |
| **+ MIRROR_CONT** | income | $904 | **$9,014** | **$2,030** | **62.4 %** | −$4,691 |

**Incremental fixed-DD: +$402 (inverse-vol), +$245 (income-matched) — positive at BOTH conventions,
range +$245 to +$402.**

## 4. The four gates, applied identically to W116's

| gate | **MIRROR_CONT** | *FOLLOW_MORNING (W116)* |
|---|---|---|
| earns > 0 on book-losing weeks | **PASS** — +$614 | *$66, borderline* |
| **beats its circular-shift null there** | **FAIL** — 42.9th | ***FAIL — 9.9th*** |
| incremental fixed-DD > 0 at either convention | **PASS** — +$402 / +$245 | *marginal — +$74 / −$291* |
| worst-decile overlap ≤ the null's 95th | **PASS** — 80.2nd | ***FAIL — 95.8th*** |

> ### **Preregistered verdict: gate 2 fails, so it is NOT classified as a diversifying candidate.** The falsifier was a disjunction and I am not softening it.
> ### But the shape of the failure is different from FOLLOW_MORNING's and the difference matters. FOLLOW_MORNING earned **$66 where chance gives $842** — *specifically absent* when needed. MIRROR_CONT earns **$614 where chance gives $663** — *exactly average*. It is not absent; it simply is not **selectively** helpful.

### Why the session and weekly readings disagree — and both are right

Session-level it is pro-cyclical (**−$297** on book-losing sessions). Weekly it cuts the book's max
drawdown by **29 %** and its tail beta is **−1.861 at the 0.9th percentile**. Those are different
slices: "book-losing weeks" is ~40 % of weeks; "tail beta" is the **bottom decile**. **The object is
unhelpful across ordinary losing weeks and strongly offsetting in the deepest ones.**
⚠️ The bottom decile is **21 weeks**. That is a small sample carrying the most favourable statistic
in the wave, and it must be quoted with its n.

## 5. Decision

**NOTHING PROMOTED. NOT built as an engine.** §23 and §24 are satisfied: redundancy was determined
before any engineering.

| axis | verdict |
|---|---|
| classification | **Neither cleanly REDUNDANT nor DIVERSIFYING** — the preregistered binary did not anticipate 3-of-4. It fails the average-case gate and passes the tail gates |
| regime | **`CURRENT_REGIME_UNEXPLAINED`** — −$14/trade on 2006–2021, and W115 found no causal driver for the continuation regime |
| book status | **WATCHLIST**, alongside FOLLOW_MORNING — but ahead of it on every gate |
| engineering | **none.** No `.cs` exists and none is written by this wave |

**What it also earns, per §7:** MIRROR_CONT becomes the standing **`MIRROR_CONTINUATION_CONTROL`** —
the same-trigger, same-clock, same-cost, opposite-direction control that every future fade or
reversal proposal must now carry.

**What would change the verdict**, recorded now:

1. **Forward evidence** on sealed ≥2026-08-01 data. It is parameter-light and needs no refit.
2. **A tail-specific re-test with more observations.** The whole portfolio case rests on 21 weeks of
   bottom-decile behaviour. That is the number to distrust and the number to re-read forward.
3. **It does NOT get another retracement grid or exit time.** §39's stop rule: one clean primary
   test, and this was it.
