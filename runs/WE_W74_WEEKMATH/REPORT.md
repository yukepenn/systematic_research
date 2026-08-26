# WE_W74 — WHAT 76 % POSITIVE WEEKS ACTUALLY REQUIRES · REPORT

Spec preregistered + amendment 1 (which corrects two defects in my own read-1 verdict logic
and was committed before the corrected arms ran). No new data, no engine runs, no parameter
search — every number comes from daily series already persisted on disk.
**Nothing adopted. This is a planning instrument, and it changes what the rest of the campaign
should be doing.**

---

## 0. Why this wave exists

`CAMPAIGN_STATE.md` fixes the campaign's success criterion and it is not the one I had been
working to:

> positive-week rate **> 76 %**, mean weekly net **> $8,583**, worst week materially better than
> **−$42,235**

We are at **58.3 %** positive weeks (61.9 % over the trailing two years). W71 measured all 216
halt × target × period cells and **the best of them reaches 63.2 %**. Seventy-three waves have
attacked this by looking for better signals. **None had asked what the target requires
arithmetically** — and that question has an answer that does not depend on finding anything.

## 1. `CORRECTION` — my own falsifier was the wrong statistic (amendment 1)

Read 1 tested whether the positive-week rate follows from the weekly moments, with a falsifier of
*"mean absolute error > 5 pp"*. It returned MAE 3.84 pp (normal model) and 3.31 pp
(Cornish-Fisher), so the falsifier did not fire — **and both models have negative R²** (−1.087
and −0.531) with large opposite biases (+3.40 and −2.65 pp).

Negative R² means each model is worse than predicting the sample mean. **A low-MAE threshold
cannot detect a predictor that simply sits near the middle of a tight distribution**, so my
stopping rule measured the wrong thing. This is the third time in this campaign one of my own
stopping rules has been mis-specified and had to be tightened before use (W55, W57, now W74).

> `RECORDED`: **the positive-week rate is NOT a function of the first three weekly moments here.**
> P1's weekly distribution has skew **+2.11** and excess kurtosis **+8.97** — P1 is not even
> inside the |skew| < 2 band my own spec used to select the fit set. Every Cornish-Fisher number
> in read 1 is **withdrawn**, including its phase-3 verdict that the short sleeve carries
> "genuine shape/dependence value" — that discrepancy was model error, not sleeve value.

## 2. What survives, and it survives a hold-out (`FACT`)

The empirical cross-sectional relation, fitted on the **216 W59 cells only**:

> **wk+% = 48.07 + 45.41 × weekly Sharpe − 2.99 × weekly skew**

Validated on the **19 objects the fit never saw** (P1, the short sleeve, five blends, twelve W72
channel arms): **MAE 2.83 pp, bias −0.74 pp, R² +0.277.** It is used as algebra — a conversion
between units the owner cares about — never as evidence any object will achieve anything.

**The exchange rate the campaign has been trading blind:**

| lever | what it buys |
|---|---|
| +0.10 of weekly Sharpe | **+4.54 pp** of positive weeks |
| −1.0 of weekly skew | **+2.99 pp** of positive weeks |

This prices the conflict `CAMPAIGN_STATE` and W64 have been holding at the same time.
CAMPAIGN_STATE records *"positive skew IS his money structure"*; W64 concluded P1's skew is a
weakness. **Both cannot be simply true, because positive skew is exactly what depresses the
positive-week rate.** P1's +2.11 skew is costing **6.3 pp of positive weeks** right now. That is
the number the disagreement was missing.

## 3. THE REQUIREMENT (`FACT`)

| | weekly Sharpe needed for 76 % | multiple of ours (0.314) |
|---|---|---|
| at P1's current skew (+2.11) | **0.754** | **2.40×** |
| at zero skew | 0.615 | 1.96× |
| at skew −1.0 | 0.549 | 1.75× |

And the same requirement expressed the way it can actually be bought — **independent streams of
our own quality**, by bootstrap from P1's own 204 empirical weeks with a Gaussian copula, so
every stream has P1's exact marginal distribution and no normal or Cornish-Fisher assumption
enters anywhere:

| streams K | ρ = 0.0 | ρ = 0.1 | ρ = 0.2 | ρ = 0.3 |
|---|---|---|---|---|
| **1** | 58.4 % | 59.0 % | 58.1 % | 58.2 % |
| 2 | 64.4 % | 64.2 % | 62.3 % | 62.0 % |
| 4 | 72.8 % | 69.8 % | 67.6 % | 65.8 % |
| **6** | **78.2 %** | 73.4 % | 69.3 % | 67.5 % |
| 10 | 85.3 % | **76.8 %** | 72.2 % | 69.2 % |
| 16 | 91.1 % | 79.5 % | 73.8 % | 70.1 % |
| 24 | 95.4 % | 81.5 % | 74.8 % | 70.5 % |

> ### `RECORDED` — the campaign's central number.
> **76 % positive weeks needs 6 genuinely independent streams of our current quality. At ρ = 0.1
> it needs 10. At ρ ≥ 0.2 it is NEVER reachable, at any K.**

(The K = 1 row reproduces P1's own 58.3 % in every column, as it must — an earlier draft mixed a
common and an idiosyncratic *draw*, which convolves the distribution and wrongly inflated K = 1
to 64.7 %. That construction is discarded and the copula version replaces it.)

## 4. And contracts cannot buy any of it (`FACT`)

**The positive-week rate is scale-invariant.** Doubling size doubles the wins and the losses and
leaves the hit rate exactly where it was. This is why the money target and the consistency target
behave completely differently:

| | where we are | the target | closable by size? |
|---|---|---|---|
| weekly $ **at his tail tolerance** (−$42,235) | **≈ $8,398 net** (7.2 contracts) | $8,583 **gross** | **already there** |
| positive-week rate | **58.3 %** | 76 % | **never** |

> **The money problem is solved and the consistency problem is not.** Every remaining unit of
> work should go to the second one, and the second one is a *stream count*, not a signal hunt.

## 5. The short sleeve's consistency gain is GENERIC (`FACT`, and it reframes five waves)

W61 measured that adding the short sleeve raises positive weeks 58.3 → 63.7 %, and treated that
as evidence the sleeve is specially decorrelated (daily ρ = −0.003, the best in the repo).

The assumption-free test: randomly re-pair the sleeve's weekly outcomes with P1's — destroying
alignment while preserving **both** marginal distributions exactly — 1,000 draws.

| w | REAL wk+% | shuffled mean | shuffled p95 | percentile | verdict |
|---|---|---|---|---|---|
| 0.10 | 59.3 % | 59.8 % | 61.8 % | 27 % | GENERIC |
| 0.20 | 60.3 % | 60.0 % | 62.3 % | 51 % | GENERIC |
| 0.30 | 61.8 % | 60.4 % | 63.7 % | 73 % | GENERIC |
| 0.40 | 63.2 % | 60.5 % | 63.7 % | 90 % | GENERIC |
| 0.50 | 63.7 % | 60.3 % | 63.7 % | **94 %** | GENERIC (borderline) |

A **randomly re-timed** short sleeve delivers 59.8–60.5 % against the real 59.3–63.7 %. The real
combination never reaches the 95th percentile.

> `RECORDED`: **the short sleeve's consistency value is not its timing against P1 — it is the
> plain fact of being an independent stream with that marginal distribution.** Any stream of that
> shape and size buys the same thing.

This is the third time this campaign has separated "own expectancy" from "alignment with P1" and
found only the first (W56 for B-MOM, W61 for the sleeve's money, W74 for its consistency). It
means **W40, W56, W57, W61 and W65 were all searching for the wrong property.** They screened
candidates on decorrelation. The measurement says decorrelation is a *threshold* condition
(ρ must be low), not a *quality* to be maximised — and once past it, **what matters is how many
streams you have**.

## 6. What this says the campaign should do

1. **Stop hunting for one specially-decorrelated engine.** Six ordinary independent ones beat it,
   and the sixth is worth exactly as much as the second.
2. **Count what we actually have.** P1 and the short sleeve are 2 streams at ρ ≈ 0 — except the
   sleeve is in the worst year of its own history (W61), so call it 1.5.
3. **The skew lever is real but small and cannot do it alone**: at our Sharpe, 76 % would need
   skew −3.00, which no truncation of this object reaches. It is worth ~3 pp per unit, and the
   session target is the only parameter that moves it (§ W59/W71).
4. **ρ ≥ 0.2 is a wall.** Every clock sleeve, every member-set variant and every W72 channel arm
   is far above that against P1. Sampling diversification cannot contribute here **at all** — a
   quantitative restatement of the campaign's own model-risk law.

## 7. Files
`out/weekmath.txt` (read 1, its CF sections withdrawn) · `out/weekmath_b.txt` (the corrected
wave) · `out/objects.csv` `out/heldout.csv` `out/shuffle_null.csv` `out/bootstrap_streams.csv`
`out/cells.csv` `out/phase3.csv` `out/streams_needed.csv` ·
code `research/weekly_edge/src/run_we_w74.py`, `run_we_w74b.py`
