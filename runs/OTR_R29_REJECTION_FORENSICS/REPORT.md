# OTR_R29_REJECTION_FORENSICS — report

Spec preregistered before readout (`spec.yaml`). Directive v5.0 §19/§20/§25/§39/§40.
Code: `vwap_flux_family/src/run_r29_rejection.py`. Model frozen to the incumbent leader; no
parameter varied; nothing promoted into any model (§13).

Harness reproduced the R27 state exactly: **2,730 signals emitted, 1,705 wrapper trades,
baseline §40 mean distance 0.4768.**

---

## 1. A base correction to a number that has been quoted repeatedly

The chain "2,730 → 1,705 → 1,214" mixes two different bases and overstates the gap:

| quantity | value |
|---|---|
| Layer-A signals emitted, 2026-01-11 … 2026-05-29 | 2,730 |
| wrapper trades, whole span | 1,705 |
| **wrapper trades falling INSIDE the 17 report windows** | **1,512** |
| trades in the inter-window gaps (not in any report) | 193 |
| **the trader, same 17 windows** | **1,214** |

**Like-for-like excess is 298 trades (+24.5 %), not 491 (+40 %).** The corrected chain is
**2,730 emitted → 1,512 traded in-window → 1,214 his.** No conclusion changes, but
`PURCHASE_GATE_v2`, `VF_ARCHITECTURE_REOPEN.md` and the campaign memory all quote the mixed-base
figure and are corrected accordingly.

---

## 2. The preregistered decision rule fired — and it was wrong

**Literal result.** Two filters beat their per-window-matched null at the 0.0th percentile
(0 of 200 null draws reached their distance):

| filter | kept | §40 distance | null median | null pct |
|---|---|---|---|---|
| `dist_fv_rails` keep_above 0.16 | 1,023 | 0.4293 | 0.4753 | **0.0** |
| `atr14` keep_above 9.36 | 854 | 0.4651 | 0.5310 | **0.0** |
| `dist_fv_rails` keep_above 0.11 | 1,193 | **0.4216** | 0.4527 | 1.5 |

By the rule as written — "declare CONCENTRATED only at percentile ≤ 1" — that is RIVAL A.

**The rule was under-specified, and the correction reverses it.** 111 filters were tested. At a
1 % threshold the expected number of chance hits is **1.11**. Observed: **2**. That is not
distinguishable from noise.

The per-feature view settles it. Each feature received up to 10 thresholds; the statistic that is
not threshold-shopped is the feature's *mean* percentile, which under the null should sit at ~50:

| feature | thresholds | **mean pct** | best pct |
|---|---|---|---|
| sig_idx_in_trend | 1 | 7.5 | 7.5 |
| clock_hour | 10 | 28.1 | 7.5 |
| trend_age | 4 | 30.6 | 4.0 |
| trades_today | 10 | 42.2 | 5.0 |
| **dist_fv_rails** | 10 | **50.9** | 0.0 |
| **atr14** | 10 | **53.5** | 0.0 |
| tod_min | 10 | 56.5 | 3.0 |
| direction | 2 | 87.8 | 75.5 |

Both "winners" sit **exactly on the null** across their own threshold range. Their 0.0 hits are
purchased with ten tries each. No feature's mean percentile is remarkable.

### Corrected verdict: **RIVAL B — DIFFUSE**

No observable entry-state feature among the seventeen localises the 298-trade excess beyond what
random thinning achieves. Recorded as a negative result under §44; the flawed decision rule is
recorded rather than rewritten.

**This converges with R23.** For the 2023 era, with *exact* trade labels, no 2-feature threshold
rule over 15 observable features reached ≤ 2 errors. Two eras, two entirely different methods
(exact inverse labels vs null-calibrated aggregate filtering), same answer: **his suppression is
not a simple observable-state entry filter.**

---

## 3. The finding that actually matters: the residual is not in the COUNT

| quantity | value |
|---|---|
| baseline §40 distance, all trades | 0.4768 |
| median distance after count-matching alone (random thinning to his counts) | 0.4696 |
| **gain from getting the trade count exactly right** | **+0.0072** |

**P3 REFUTED.** I predicted count-matching would dominate. It buys essentially nothing —
removing 25 % of our trades to match his per-window counts moves the distance by 0.7 %.

Illustration: `dist_fv_rails ≥ 0.07` keeps **1,198** in-window trades against his **1,214** — a
1.3 % count match — and scores an unremarkable 6.5th percentile against its null.
**Matching his trade count does not make them his trades.**

So the ~0.45–0.48 floor is not caused by trading too often. It is in the **geometry** of the
trades — their win/loss sizes and holds. §4 below shows the same thing from a completely
different direction.

---

## 4. The March catastrophe decomposed (§24A, §55 Q20)

His worst week, 2026-03-22 → 03-27, −$42,235, against our model on the same bars:

| | **his** | **ours** |
|---|---|---|
| trades | 92 | **95** |
| win rate | 28.3 % | **25.3 %** |
| worst loss | −$2,600 | **−$2,600** |
| **avg loss** | **−$998** | −$608 |
| **avg win** | **$909** | $1,425 |
| **payoff** | **0.91** | 2.34 |
| avg hold | 33.7 min | 60.1 min |
| net | **−$42,235** | −$9,000 |

We reproduce his trade count to 3 %, his win rate to 3 points, and his worst loss exactly. We
miss his net by 4.7×. **Entry selection is right; geometry is wrong.**

**His risk control did not fail.** Across all 24 windows of 2026 his avg loss ranges −$704 to
−$1,359; the catastrophe week's −$998 is utterly ordinary, and the worst single loss sits exactly
on the −$2,600 cap. Nothing broke.

**What collapsed was his winners.** Avg win $909 against a 2026 median of ~$1,780, and the lowest
of all 22 backtest weeks by a wide margin (next lowest $1,109). The catastrophe week is the
**only week in all of 2026 with a payoff ratio below 1.0** — 0.91 against a median of 1.83 and a
next-worst of 1.25. Its win rate, 28.26 %, is also the lowest of the 24 (next lowest 33.93 %).

Arithmetic closes exactly: 26 × $909 − 66 × $998 = −$42,234.

Combined with R28's finding that the panel changed by **−4.0 rows (−0.58σ)** that week — no build
change at all — this settles §24A:

> **The March catastrophe is a regime event, not a build regression.** A trend system with a
> 130-point stop, ordinary ~50-point average losses and a 2:1 payoff produces exactly this when
> sustained runs disappear for a week (his holds collapsed to 33.7 min, second-shortest of 24).
> There is no bug in his March build to find.

Our model does **not** reproduce the hold collapse (60.1 min vs his 33.7) and therefore does not
reproduce the winner collapse. That is the specific, localised mismatch.

---

## 5. Where this leaves the program

Two independent lines this run point the same way, and away from where §19 pointed:

1. Count-matching buys +0.0072; no entry-state feature beats its null → **the residual is not in
   which signals are accepted.**
2. In his worst week we match count, win rate and stop exactly, and miss avg-win by 57 % →
   **the residual is in exit geometry and hold duration.**

Combined with R23 (2023, exact labels, no entry rule found) and R28 (panel decoupled from
behaviour, 84 % of the mature panel never photographed), the entry-filter hypothesis has now
failed on three independent attacks.

**Recommended next axis: exit geometry.** Our X_OPP "reverse on opposite signal" holds ~60–88 min
against his 20–123 min, and systematically longer in 12 of 17 windows. That is a testable,
free, preregisterable rival set. It is *not* run here and nothing from this run is promoted.

## 6. What this run did NOT establish
- It did not identify any suppression rule, and now argues one is unlikely to be a simple filter.
- `dist_fv_rails` and `atr14` are **not** endorsed; their apparent significance is threshold-shopped.
- It did not test exit rules at all.
- It says nothing about any vendor component (§5, §43).
