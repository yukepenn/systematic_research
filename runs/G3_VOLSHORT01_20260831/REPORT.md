# G3_VOLSHORT01 — RESULT: **DO NOT SPEND THE WINDOW. IT REMAINS UNSPENT.**

**Evidence status `DISCOVERY_CONSUMED` · verdict FAIL-CLOSED · promotions: 0 · `LIVE = NO` · `$0`**

The owner authorised consuming `GENESIS_H1`'s pristine one-shot confirmation window
(`2022-01-01 → 2026-07-31`, read ONCE). **The authorisation was used to decide NOT to spend it.
The window is still sealed and still available exactly once.**

---

## 🔴 THE WALL HELD — verified independently by the orchestrator, not accepted from the agents

```
panel_pre2022.parquet   4,106 rows   max session_date = 2021-12-31
rows on or after 2022-01-01: 0
vix_asof / vxn_asof / vix9d_asof / vix3m_asof / vvix_asof / skew_asof  — all max 2021-12-30
```

Asserted separately on the raw 1-minute bars (max stamp `2021-12-31 17:00`, 0 bars past the wall),
on all six Cboe frames at load (**5,919 post-wall rows dropped unread**), and on `session_date`,
`prev_session_date` and every `*_asof` column. Every check raises rather than warns.
**Substrate self-test 47/47**, including a future-shuffle leak test: shuffling `x[301:]` leaves all
301 earlier `causal_tercile` outputs bit-identical, plus a non-vacuity check that the shuffle did
change the future.

## THE MECHANISM'S SIGN IS BACKWARDS ON NQ — nine states, nine times

The theory: the variance premium is compensated **overnight** and extracted **intraday**, so high
ex-ante implied variance should carry **negative** intraday drift.

| specification | high-state RTH drift | baseline |
|---|---:|---:|
| VXN terciles (reference) | **+1.777 pts** | ~+1.31 (LOW tercile +2.508) |
| VIX terciles | +1.589 | +1.21 (states non-monotone: +1.79 / −0.08 / +1.59) |
| ex-ante variance / VRP | +1.74 / **+2.62** | |
| VIX/VIX3M · VIX9D/VIX · VVIX/VIX | +2.15 / +2.69 / **+3.18** | +1.70 / +1.87 / +1.22 |
| 1-day change in VXN | 🔴 **+6.39** | +1.69 |

**4 axes, 2 underlyings, 14 windows/thresholds, 14/14 non-inverted robustness variants — all the
same sign, and it is the wrong one.** High-implied-variance sessions carry **more** positive intraday
drift than baseline, not less.

**This is not a magnitude problem.** The short leg fights NQ's ≈ +1.2 pt/session intraday drift with
a 1.0325-pt cost floor stacked on top, and **every arm S stays negative at the $4.36 commission-only
FLOOR** (−$34,231 / −$43,343 / −$17.56 per session). No execution improvement rescues any of them.

## THE EXPOSURE-GATE READING FAILS TOO

`BASE` always-long nets **$36,650** ($13.057/valid session); `FILTER` (long, high-VXN sessions merely
removed) nets **$23,878** ($8.507). **Removing the high-volatility sessions COSTS $12,772.**
The eleventh consecutive member of the closed anti-filter family — and this time it fails in the
*opposite* direction from the usual: the state we were told to avoid is the profitable one.

## INFERENCE — and a prior that did not survive contact

| | |
|---|---|
| placebo percentiles (exhaustive rate-matched circular shift) | **49.0 · 37.7 · 50.1 · 72.7 · 24.9 · 17.5 · 0.9 · 44.2** — best 72.7, bar is 95 |
| block-bootstrap CI on arm S (VXN) | **[−$145.32, +$24.38]/session — contains zero, p = 0.169** |
| leave-one-episode-out | **0 of 53 folds stay positive** |
| years net-positive | 1 of 12 |

⚠️ **The "8–14 independent episodes" prior in the spec was wrong** and the agent said so: at
`gap_days = 10` there are **53** episodes, 33 at gap 21, **18 at gap 42** — still above the prior.
But `rho_bar = 0.0259` → `K_eff = 22.59`, and **the five largest episodes carry 50.5% of all
high-state sessions**, so 53 badly overstates independence and must never be quoted alone.

## WHY NOT SPEND IT ANYWAY — the asymmetry is the argument

| outcome if spent on the least-bad candidate | probability | value |
|---|---:|---|
| decisive **negative** | 85–90% | **uninformative** — rejects what nine pre-2022 tests already rejected |
| **positive** | 10–15% | 🔴 **the worst outcome available** |

Nearly all of that 10–15% mass sits on **2022 specifically**: 2022 was a sustained high-VXN drawdown
year in NQ, so a "short when VXN is high" mask would have been right there **for pure regime
coincidence, not the priced-variance mechanism.** That is *a spurious pass on a corpse, burning the
window AND creating a promotion claim with no mechanism behind it.*

## THE SIGN-INVERTED ARM IS EXPLICITLY REFUSED

Long on a high 1-day VXN change prints well. It is **not** promoted, for three stated reasons:
post-hoc sign selection; **47.9% single-episode concentration**; and it is dominated by a prior-day
**price-reversal** signal that contains no implied-vol information at all. Nothing in this wave
licenses freezing it.

## THE DECISION'S OWN FALSIFIER — and it costs ZERO window

Re-opening this requires **all four** clauses to pass, **entirely on pre-2022 data**:

| | clause | observed |
|---|---|---|
| **F1** | some causal ex-ante-variance state has **negative** high-state drift | +1.777, +1.589, +1.74, +2.62, +2.15, +2.69, +3.18, +1.35, +6.39 — **nine for nine positive. FAIL** |
| **F2** | `mean_pts(high) ≤ −1.0325` and net(S) > 0 at $25.01 | every arm negative at all three cost lines. **FAIL** |
| **F3** | net(S) beats the p95 of the exhaustive circular-shift null, family-wise over ≥ 20 definitions | best percentile 72.7. **FAIL** |
| **F4** | whole-episode block bootstrap `ci_lo > 0` | CI contains zero. **FAIL** |

**F1 is load-bearing:** until some state definition produces a *negative* mean intraday drift
pre-2022, there is nothing to confirm, and no threshold, cost model or execution improvement can
manufacture one.

**The strongest objection to this decision, named by the agent against itself:** VXN specs begin
2010-09 (inception + a 252-session burn-in) and therefore **never see 2008**. But the VIX arms span
**2007–2021 including 2008** and agree in sign (−1.589 gross pts/short, −$62,874). The absence of
2008 is not what is killing this.

## THE RECORDED NEGATIVE CONSTRAINT

> Ex-ante implied variance — VIX/VXN level, VIX9D/VIX, VIX/VIX3M, VVIX/VIX, VRP against both RTH and
> close-to-close realised, and 1d/5d/z21 changes — is **neither a signed intraday SHORT trigger nor
> an exposure gate** for NQ RTH 09:30→16:00 on 2006–2021. High-implied-variance sessions carry
> **more** positive intraday drift than baseline on 4 axes, 2 underlyings and 14 variants, without
> exception.

`confirmation_one_shot` remains **UNSPENT and SEALED**. Its status in `LOCKED_FORWARD.md` is
unchanged. The G3_VOLSHORT01 wave terminates at discovery.
