# WE_W56 — BREADTH · REPORT

Preregistered. Intersection window **2022-07-05 → 2026-05-29, 204 common weeks**.
Every portfolio rescaled to the incumbent's own max drawdown **$20,245**, so the headline
column answers the owner's question directly: *how many dollars a week, for the same worst
drawdown.*

**VERDICT: NOTHING ADOPTED — but this wave found the largest number in the campaign and
located exactly what it depends on.**

---

## 1. The headline, and it is large

| portfolio | **weekly $ at $20,245 max DD** | wk + % | worst week | mean top-5 DD | Ulcer | ann Sharpe | CVaR-eff | P1 contracts | B-MOM contracts |
|---|---|---|---|---|---|---|---|---|---|
| **P1 incumbent** | **$1,475** | 58.3 % | −$7,418 | $14,266 | $6,183 | 2.26 | 0.273 | 1.27 | — |
| P1 + B-MOM w=0.20 | $1,826 | 59.8 % | −$8,056 | $13,528 | $5,917 | 2.29 | 0.299 | 1.39 | 0.17 |
| **P1 + B-MOM w=0.30** | **$2,114 (+43 %)** | **59.3 %** | −$10,084 | **$14,178** | **$6,071** | **2.26** | **0.290** | 1.48 | 0.30 |
| P1 + B-MOM w=0.40 | **$2,310 (+57 %)** | 59.8 % | −$13,780 | $16,182 | $6,163 | 2.20 | 0.266 | 1.47 | 0.47 |
| P1 + axis B w=0.30 | $1,713 (+16 %) | 59.3 % | −$9,869 | $14,751 | $6,274 | 2.25 | 0.259 | 1.33 | — |
| P1 + BREADTH01 w=0.05 | $1,404 (−5 %) | 59.8 % | −$7,012 | $14,037 | $6,245 | 2.26 | 0.269 | 1.20 | — |

`FACT`: at **w = 0.30**, the combination clears every part of the preregistered adoption bar
except the nulls — more money (+43 %), a *better* drawdown distribution (mean top-5 $14,178 vs
$14,266, Ulcer $6,071 vs $6,183), a higher positive-week rate, identical annualised Sharpe, and
better CVaR-efficiency, at 1.48 P1 contracts plus 0.30 B-MOM contracts. Both are NQ at $20/point,
so that is reachable in integer terms at roughly 5 : 1.

## 2. The correlations against P1 — computed here for the first time

Every published correlation for these sleeves was against the **system_master E10 / Solar-v1**
object on a 3-minute substrate, never against weekly_edge P1. Measured directly:

| sleeve | weekly mean | weekly σ | ann Sharpe | **ρ vs P1** | ρ inside P1's worst decile | **ρ of the underwater curves** |
|---|---|---|---|---|---|---|
| axis B | $325 | $4,209 | 0.56 | **+0.060** | −0.205 ± 0.24 | −0.006 |
| **B-MOM** | **$1,291** | $7,758 | **1.20** | **+0.371** | −0.051 ± 0.24 | **−0.171** |
| BREADTH01 | (fractional) | 4.25 % ann | 0.36 | +0.129 | +0.141 ± 0.24 | +0.217 |
| P1 | $1,475 | $4,703 | 2.26 | 1.000 | — | — |

- The published shelf numbers **replicate**: axis B's +0.01 → +0.060, its worst-decile −0.25 →
  −0.205; B-MOM's 0.344 vs E10 → 0.371 vs P1. The substitution I refused to make turns out to
  have been approximately safe — which is knowable only now that it has been checked.
- The worst-decile column conditions on **P1 alone** being extreme, not on the sum, so it does
  not carry the selection artifact I created and caught in W53. But it is 20 weeks:
  **SE(ρ) ≈ 0.24, and not one of these is distinguishable from zero.** They should not be
  quoted as tail-hedging evidence, and they are not used as such here.
- The number that actually matters for a drawdown claim is the **underwater-curve
  correlation**, and B-MOM's is **−0.171**: when P1 is under water, B-MOM tends not to be.
  That is the mechanism behind the table in §1.

## 3. The nulls — all three fail, and the failure means something specific

| sleeve | real best | N1 circular shift (mean, pct) | N3 synthetic sleeve (mean, pct) | verdict |
|---|---|---|---|---|
| axis B | $1,713 | $1,626, 72.5 % | $1,645, 66.5 % | fail |
| **B-MOM** | **$2,310** | **$2,071, 77.0 %** | $1,919, 86.5 % | fail |
| BREADTH01 | $1,404 | $1,631, **4.0 %** | $1,597, 4.5 % | fail |

Both nulls keep the sleeve's mean and volatility and destroy only its **alignment** with P1.
A circularly-shifted B-MOM still delivers **$2,071/week (+40 %)**. So:

> **The gain is B-MOM's own expectancy, not its timing relative to P1.** Adding a profitable,
> loosely-correlated sleeve raises money-at-fixed-drawdown by portfolio arithmetic. That
> arithmetic is real; it is Markowitz, not a fitted result. What is *not* demonstrated is that
> B-MOM earns specifically when P1 does not.

### A defect in my own spec, recorded

The spec says of these nulls: *"Both are legitimate, they are different claims"* — and then
sets the adoption bar at ≥ 95th percentile on both, which silently requires the **alignment**
claim. That is inconsistent. The expectancy claim alone is sufficient for a portfolio benefit
and does not need an alignment null to be valid.

I am **not** using that inconsistency to adopt, because the binding objection is elsewhere and
is worse. But the bar is recorded as mis-specified so it is not applied unexamined next time.

## 4. What the whole thing actually rests on

| B-MOM | sessions | net | daily mean ± SE | **t** |
|---|---|---|---|---|
| 2006–2021 | 4,077 | $18,156 | $4.5 ± $16.8 | **0.27** |
| 2022–2026 | 1,122 | $319,123 | $284.4 ± $106.8 | **2.66** |
| in this window (weekly) | 204 weeks | — | $1,291 ± $543 | **2.38** |

`FACT`: **B-MOM is a four-year result with t ≈ 2.4, preceded by sixteen years of nothing
(t = 0.27), and 2022–2026 is its own development sample.**

Charter Amendment 1 says recency is not disqualifying by itself, and it is not. But §2(b)
requires a **causal regime variable** separating the eras, and **none is named anywhere in the
record**. Without one, the honest description is not "a regime" — it is "a 4-year in-sample
result". §2(a)'s sample-adequacy question therefore answers itself: t = 2.38 in-sample is not
enough to carry a +43 % claim.

BREADTH01 fails on its own terms too: in-window weekly mean t = **0.71**, and its portfolio
contribution sits at the **4th percentile of its own null** — worse than noise. Axis B behaves
exactly as W43's law predicted: near-zero expectancy (+$114/wk stress-net standalone), so
despite genuine decoupling it buys only +16 %, of which the nulls say ~95 % is arithmetic.
**Decoupling is necessary and not sufficient — third confirmation.**

## 5. What is now true, and what to do about it

`FACT` — **portfolio arithmetic is the largest lever measured in this campaign.** Sixteen causal
features inside the object found nothing (W55, best |ρ| = 0.108); one loosely-correlated
profitable sleeve at w = 0.30 is worth **+43 % money at a slightly better drawdown**. The
structure of the answer is settled; only the ingredient is in doubt.

`UNKNOWN`, and now the single highest-value question in the repo — **is B-MOM's edge real?**
If it is, it is worth +43 % at the same drawdown. If it is not, the campaign has no second
engine and the falsifier of this spec fires: *this repo currently holds no engine that
diversifies P1, model concentration is the binding constraint, and the next move is to build
or buy a genuinely different information source.*

Two ways to attack it that do not require new money, ranked:
1. **Extend B-MOM through June–July 2026.** Its series stops 2026-05-29, but 3-minute NQ data
   through 2026-07-31 exists in the repo (`runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, used by
   system_master with `HEALTH_END = 2026-07-31`). That is roughly 40 genuinely
   post-development sessions at zero cost and without touching the ≥ 2026-08-01 seal.
2. **The sealed forward sample.** Data ≥ 2026-08-01 is virgin by owner instruction. It is a
   one-shot resource governed by `research/operational/LOCKED_FORWARD.md` and
   `MONITORING_CALENDAR.md`, and it is not to be opened without reading that protocol first
   and, if it requires it, owner authorisation.

## 6. Infrastructure fixed
`out/p1_daily.csv` (607 sessions, sha 9bc2d7f7000653b4) and `out/axisb_daily.csv` (1,010
sessions, 4,236 trades) are now on disk. Across all 55 prior `runs/WE_*` directories there was
no P1 daily or weekly series; every wave regenerated it and threw it away. No future wave pays
that cost again.

## 7. Excluded before testing
**HTFDIR01 ARM_LONGONLY.** Correlation with the Solar incumbent, computed directly from its own
ledger: **ρ = 0.994 daily over 1,139 sessions**, the two columns differing on 129 of 1,139 rows.
It is a 7 % perturbation of Solar, not a second engine; adding it at constant risk re-sizes
Solar. Excluded, and the reason is recorded rather than discovered later.

## 8. Files
`out/breadth.txt` `out/p1_daily.csv` `out/axisb_daily.csv` `out/corr.csv` `out/wscan.csv`
`out/nulls.csv` `out/frontier.csv` · code `research/weekly_edge/src/run_we_w56.py`
