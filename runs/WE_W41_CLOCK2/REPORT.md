# WE_W41 — MULTI-CLOCK ON THE TRUE ENGINE · REPORT

Spec + amendments 1 and 2, each appended before its own arm was read.
**B1a/B1b/B1c all PASS** — in particular **B1c: the clock harness at k = 1 reproduces the
incumbent vote BAR FOR BAR**, which is exactly the check W32 lacked and the reason its verdict
was provisional. Net $4.36/RT, stress $14.36/RT, window 2022-07 → 2026-08.

**Two results: W32 is overturned, and the campaign has its first adopted diversification —
with a scale qualification that must travel with it.**

---

## 1. W32 is overturned (`REPRODUCED`, on the true engine)

| clock | bars | pts/session | **$/trade** | Sharpe | corr vs long | **corr in long's worst-decile weeks** |
|---|---|---|---|---|---|---|
| 1-min base vote + box | 1,558,497 | 10.62 | $103.9 | 0.305 | 0.89 | 0.55 |
| **3-min time** | 520,576 | 9.40 | **$170.8** | 0.228 | **0.48** | **0.12** |
| 5-min time | 312,761 | 5.68 | $122.4 | 0.123 | 0.47 | 0.33 |
| **volume (=3-min rate)** | 355,362 | 8.95 | $166.7 | 0.197 | **0.44** | 0.22 |
| **range (=3-min rate)** | 172,501 | 8.74 | **$236.5** | 0.203 | **0.32** | **0.16** |
| 3-min, σ = 460 bars | 520,576 | 7.87 | $114.6 | 0.193 | 0.47 | **0.02** |

W32's simplified engine scored 3.84 (3-min) against its own 4.85 (1-min) and concluded
"coarser clocks are worse". The **true** engine scores 9.40 against 10.62 — an 11 % production
difference, not a collapse — and per-trade economics move the *other* way ($170.8 and $236.5
against $103.9). What survives of W32 is "coarser clocks produce slightly less per session",
not a rejection of the axis.

## 2. The measurement W32 never made, and the mechanism behind it

Every clock sleeve clears **BOTH** nulls at the **100th percentile** (one at the 99th).
And the weekly P&L correlations are far lower than a "same rule, coarser data" intuition
predicts — 0.32–0.48 against the 1-min base object's 0.89, and **0.02–0.33 inside the long
object's worst-decile weeks**, which is the number that decides whether a sleeve is
diversification or decoration.

**Mechanism (`INFERENCE`, derived from an established prior rather than invented):** W31
established that the edge lives in the **flip EVENT**, not the trend state. A different bar
clock is therefore *not* a smoothed version of the same signal — it is a **different event
generator**: the anchor updates at different times and the threshold is crossed in different
places, so the flips are different events.

⚠️ **This is SAMPLING diversification, not MODEL diversification.** Every clock is still the
same Solar ratchet; a decay in the ratchet takes all of them together. The model-concentration
risk is unchanged.

## 3. Per year — the test that withdrew W40's axis B (`FACT`)

| sleeve | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| 3-min | $1,275 | $634 | $477 | $1,437 | $1,370 |
| 5-min | $208 | $551 | $326 | $674 | $1,431 |
| volume | $115 | $533 | $946 | $837 | $2,897 |
| range | $1,357 | $898 | $135 | $1,035 | $2,091 |

**Every clock sleeve is positive in every year, and stress-net positive in every year.** That
is a categorically stronger record than axis B's (negative in 2023 and 2024), and it is why
this adoption survives the standing per-year policy while B's did not.

## 4. The adopted basket (continuous weights)

`w = 0.03 each: long quality + 3-min + range`, at constant total exposure:

| | weekly | wk + % | worst week | CVaR5 | Sharpe | eff | cvEff |
|---|---|---|---|---|---|---|---|
| long quality alone | $1,470 | 58.6 % | −$7,418 | −$5,398 | 0.311 | 0.198 | 0.272 |
| **basket** | $1,459 | 57.1 % | **−$6,968** | **−$5,171** | **0.318** | **0.209** | **0.282** |

A four-way improvement — eff +5.6 %, CVaR-efficiency +3.7 %, Sharpe +2.3 %, worst week 6.1 %
better — for 0.7 % less money. Per year the basket beats long-alone-at-matched-exposure on eff
in **4 of 5 years** (2026 is the exception, 0.227 vs 0.240).

**Binding count-matched null: 95.0th percentile, p = 0.050 → EVIDENCE — by the smallest
possible margin** (null mean 0.199, p95 = 0.209 = the real value exactly). Stated plainly:
this clears the bar, and it clears it by nothing.

## 5. The qualification that must travel with it (amendment 2)

Continuous weights are not orders. Measured exposures: long 212,193 contract-minutes, 3-min
160,589, range 138,553 — so **w = 0.03 is 0.04 contracts**, and the clock sleeve only rounds
to one contract when the base sleeve runs at ~22–25×.

| integer ratio (long : 3-min : range) | weekly | eff vs matched long-alone | cvEff vs matched | verdict |
|---|---|---|---|---|
| 24 : 1 : 1 | $37,098 | **0.209 vs 0.198** | **0.281 vs 0.272** | both improve |
| 16 : 1 : 1 | $25,342 | **0.203 vs 0.198** | **0.285 vs 0.272** | both improve |
| 12 : 1 : 1 | $19,463 | 0.195 vs 0.198 | 0.287 vs 0.272 | CVaR only |
| 8 : 1 : 1 | $13,585 | 0.183 vs 0.198 | 0.289 vs 0.272 | CVaR only |
| 4 : 1 : 1 | $7,707 | 0.158 vs 0.198 | 0.288 vs 0.272 | CVaR only |
| 2 : 1 : 1 | $4,767 | 0.132 vs 0.198 | 0.261 vs 0.272 | neither |
| 1 : 1 : 1 | $3,298 | 0.111 vs 0.198 | 0.218 vs 0.272 | neither |

**The improvement is a scale feature.** At ≥16 : 1 : 1 (≈ $25,000/week) both metrics improve.
Between 4 : 1 : 1 and 12 : 1 : 1 the basket improves Sharpe and CVaR-efficiency — it smooths
the *typical* bad week — while making the *single worst* week and eff worse: the clocks remove
many moderately bad weeks and add a few very bad ones. Below 4 : 1 : 1 there is no benefit at
all. **At the owner's current 2–9 contract scale, the tradeable clock basket is a
CVaR-and-Sharpe trade, not an eff improvement.**

## 6. Status
- **ADOPTED** at continuous weights and at ≥16 : 1 : 1, with the null's razor-thin margin and
  the scale qualification recorded as part of the adoption, not as a footnote.
- **W32's clock axis: reopened and resolved.** Its verdict was an artifact of a defective
  harness, exactly as its own disclosure suspected.
- The model-concentration risk is **not** reduced by this: sampling diversification is not
  model diversification.
