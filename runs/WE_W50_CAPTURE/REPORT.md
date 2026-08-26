# WE_W50 — CAPTURE AUDIT · REPORT

Spec preregistered. **B1 PASS** (14.74 pts/session over 1,012 sessions). Nothing is adopted
here; the output is a ranked agenda. Two of the four phases came out unreliable and are marked
as such rather than quietly used.

---

## 1. PHASE 1 — the answer to "what do we actually capture" (`FACT`, and decisive)

| session class | share of sessions | share of available | **our pts/session** | **capture** | in-market |
|---|---|---|---|---|---|
| **TREND-UP** | 20.9 % | 22.7 % | **+88.68** | **24.60 %** | 22.8 % |
| TREND-DOWN | 13.9 % | 18.0 % | **−21.89** | −5.09 % | 5.4 % |
| REVERSAL | 26.0 % | 26.4 % | +0.56 | 0.17 % | 9.4 % |
| RANGE | 27.1 % | 22.0 % | −4.86 | −1.79 % | 10.7 % |
| MIXED | 12.1 % | 10.9 % | +4.19 | 1.39 % | 9.6 % |
| **ALL** | 100 % | 100 % | **14.86** | **4.46 %** | 12.0 % |

Weighting each class by its share reconciles to the total (18.53 − 3.04 + 0.15 − 1.32 + 0.51 =
14.83 ≈ 14.86 ✓), so this decomposition is exact, not indicative.

> **The entire system is one thing: it earns +18.5 pts/session on the 21 % of days that trend
> up, and gives back 3.7 of them on the other 79 %.**

Two things follow immediately:

**(a) On the days it is built for, it is not weak.** 24.60 % capture on TREND-UP days is the
same order as the original trader's ~24.8 % *global* capture figure. The engine does its job.

**(b) The largest identified leak needs no new edge at all.** TREND-DOWN costs −21.89
pts/session on 13.9 % of days (−3.04 overall) and RANGE costs −4.86 on 27.1 % (−1.32 overall).
**Simply being FLAT on those two classes is worth +4.36 pts/session — a 29 % increase in
production — and it requires no signal that predicts anything except "do not be long today".**
Note the shape of the TREND-DOWN loss: we are in the market only 5.4 % of those bars and still
lose 21.89 points, so the damage is concentrated in a few bad entries, not in broad exposure.

## 2. PHASE 3 — the answer to "is risk mitigation complete" (`FACT`)

Worst 20 weeks of 204: mean **−$4,514**, total −$90,271.

| | worst-decile weeks | all sessions |
|---|---|---|
| REVERSAL | **30 %** | 26 % |
| RANGE | **25 %** | 27 % |
| TREND-DOWN | **23 %** | 14 % |
| MIXED | 14 % | 12 % |
| TREND-UP | **7 %** | 21 % |

**The worst weeks are built out of exactly the classes where we have no edge** — TREND-DOWN is
over-represented 23 % vs 14 %, and TREND-UP is nearly absent (7 % vs 21 %).

Inside those weeks: **69 losing sessions out of 99**, mean −$1,417, worst single session
−$3,159 — which is only **3.5 %** of the whole worst-decile loss.

> **The tail is ACCUMULATION, not catastrophe** — confirmed on the current object, which
> W02 only established on the pre-vote object. And it says risk mitigation is **not** complete:
> the session box (−$1,300) catches losing sessions one at a time while a bad week bleeds
> through many of them. Nothing in the object acts at the MULTI-SESSION level on a REGIME
> variable. W01's weekly loss limit failed, but that was a P&L-symptom rule, and this
> campaign's own law is to throttle the regime variable, not the symptom.

## 3. Two phases that did NOT work, stated rather than buried

**PHASE 2 (leakage ledger) is unreliable as constructed.** The attribution closes to **126 %**
of available movement, i.e. the buckets double-count — a session can be simultaneously "entered
late" and "exited early" over overlapping windows. The class-level *pattern* (large
"never entered" in TREND-DOWN, large "chopped" in RANGE and REVERSAL) is suggestive, but no
number in that table may be quoted. Fixing the attribution requires a disjoint decomposition
along the session's time axis, which W51 will do properly if the buckets are needed.

**PHASE 4's verdict rule was badly calibrated and is vacuous.** It compares an open-to-close
ceiling (≈ 285 points on NQ at 20,000+) against a 1-point threshold, so every class returns
"OPPORTUNITY". The threshold should have been a fraction of the class's available movement, not
an absolute point count. The **ranked agenda** below is computed from the same data and is
still informative; the verdict column is not.

## 4. RANKED AGENDA (the preregistered output)

| class | un-captured pts/session | simple-rule ceiling | current capture |
|---|---|---|---|
| REVERSAL | 87.93 | 40.20 | 0.17 % |
| RANGE | 74.70 | 9.34 | −1.79 % |
| TREND-DOWN | 62.98 | 45.27 | −5.09 % |
| TREND-UP | 56.95 | 59.63 | 24.60 % |
| MIXED | 35.88 | 14.52 | 1.39 % |

Read with phase 1, the agenda is **not** "build a reversal engine". It is:

1. **STOP LOSING on TREND-DOWN and RANGE days — worth +4.36 pts/session (+29 %) with no new
   edge.** This is a causal REGIME-CLASSIFICATION problem, and it is the only item on this list
   whose prize is already measured rather than hypothetical. W07 attacked direction prediction
   and failed; W09's range throttle is a partial solution that already works. Neither was aimed
   at this target, because this target had never been measured.
2. **REVERSAL is the largest un-captured pool (87.93 pts/session, 26 % of all sessions) and we
   take 0.17 % of it** — but W40 tested fade-as-an-event and it lost −11.4 pts/session, so the
   pool is not obviously reachable. It stays on the list as a measured size, not as a plan.
3. TREND-UP is already worked: 24.60 % capture, and W48 showed the remaining 56.95 is not
   reachable by trade-level risk control.

## 5. What this changes about the object's description

> The object is **not** "a system that makes money on NQ". It is **a long trend-capture engine
> that earns on one fifth of days and pays a toll on the rest**. Its Sharpe of 2.25 annualised
> and MAR of 3.77 are produced entirely by TREND-UP sessions net of a −3.7 pts/session drag.
> The largest measured improvement available is not a better entry — it is **not trading on the
> days it cannot win.**
