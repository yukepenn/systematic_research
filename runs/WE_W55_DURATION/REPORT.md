# WE_W55 — THE DURATION PRIZE IS NOT REACHABLE · REPORT

Preregistered with a stopping rule; amendment 1 **tightened** that rule before it was applied.
**The wave stopped at phase 1, as designed, for the cost of one script.** Nothing adopted, no
arm built, no backtest spent.

---

## 1. What was being chased

W54 measured, by exact accounting on 1,942 trades, that the incumbent's trades held under 37
minutes cost **−15.02 pts/session** and are 60 % of all trades, while trades held over 4 hours
earn +21.56. That is the largest number this campaign has produced. W54 also measured that
**duration is strongly forecastable at entry** (runlen Spearman +0.404, delta_mag +0.367) while
**P&L is not, by the same features, with the sign reversed** (runlen −0.101).

This wave was not allowed to build anything until that contradiction was resolved.

## 2. X1 — the size confound is `ELIMINATED`

| feature at entry | ρ vs duration | ρ vs $ sized | ρ vs $ **per unit** | ρ vs $ flat-lot object |
|---|---|---|---|---|
| runlen | **+0.404** | −0.101 | −0.098 | −0.094 |
| delta_mag | +0.367 | −0.080 | −0.056 | −0.059 |
| dist_open | +0.226 | −0.008 | +0.026 | +0.017 |
| path_eff | +0.204 | −0.006 | −0.004 | −0.006 |
| bar_range_rel | +0.197 | −0.031 | −0.024 | −0.029 |
| mom_align | +0.169 | −0.038 | −0.023 | −0.023 |
| dist_vwap | +0.160 | −0.018 | +0.013 | +0.003 |
| ratio | +0.134 | −0.037 | −0.050 | −0.050 |
| or_pos | +0.130 | −0.035 | −0.008 | −0.004 |
| **atr_l** | −0.068 | −0.089 | **−0.108** | −0.096 |
| **vote_margin** | −0.059 | +0.021 | **+0.022** | +0.021 |
| churn60 | −0.010 | +0.062 | +0.067 | +0.068 |
| bars_since_open | −0.124 | −0.038 | −0.040 | −0.038 |
| rv_expansion | −0.048 | −0.044 | −0.049 | −0.043 |
| sess_extension | +0.041 | +0.043 | +0.061 | +0.040 |
| prev_ret | −0.055 | −0.037 | −0.040 | −0.037 |

Per-unit and sized correlations are essentially identical, so the flat P&L column is not a
sizing artifact. (Per-unit P&L is +$51 at size 1 and +$307 at size 2 — the quality layer
working, not distorting the diagnostic.)

### Two new facts fall straight out of this table

**`FACT` — across 16 causal features available at entry, not one predicts per-unit P&L with
|ρ| above 0.11.** The strongest is `atr_l` at −0.108: a higher ATR at the entry bar is
associated with *worse* per-unit P&L. The second is `runlen` at −0.098, whose sign is the
opposite of its +0.404 correlation with duration.

**`FACT` — `vote_margin`, the object's own closed-form signal strength (nMem × nThr × (1+dL),
lagged to the entry bar), correlates +0.022 with per-unit P&L and −0.059 with duration.** How
strongly the object votes says nothing about whether the trade makes money. That is mechanism
law 5 measured head-on, rather than inferred from four failed sizing constructions.

## 3. X2 — `CONFIRMED`, and it partially retracts W54's own headline

| Spearman(duration, per-unit P&L) | value |
|---|---|
| on the **raw pairs** | **+0.249** |
| on the ten **decile means** | **+0.750** |

W54 presented the duration→profitability relation through decile means — win rate climbing
18.5 % → 81.1 %. That table is arithmetically correct and it is **largely a binning effect**.
Pair by pair the relation is three times weaker. **The −15.02 pts/session remains an exact
accounting fact; the *strength* of the relation was overstated in W54's report and is corrected
here.** A feature that predicts duration at ρ = 0.404 therefore inherits very little of a
relation that is itself only 0.249 pair-wise.

## 4. X3 — `RECORDED`. The stopping rule fired.

77 causal trailing-rank buckets (16 features × 5 buckets, those with n ≥ 100). Every entry
ranked against the **prior 250 entries only**. The worst bucket of each feature by per-unit P&L:

| | best-case bucket | n | P(hold < 37 min) | per-unit $ |
|---|---|---|---|---|
| baseline (all trades) | — | 1,942 | **59.7 %** | **+$98** |
| dist_vwap, bucket 2 | middle | 332 | 61.7 % | −$63 |
| prev_ret, bucket 4 | top | 367 | 59.7 % | −$18 |
| ratio, bucket 0 (highest P(short)) | bottom | 326 | **69.6 %** | **+$33** |

Two things kill it:

**(a) The features that predict duration do not concentrate short trades in any bucket.** The
highest P(short) any causal bucket achieves is 69.6 %, against a 59.7 % baseline — a 10 pp
lift — and that bucket is *profitable* (+$33/unit).

**(b) The two negative buckets are fewer than chance produces.** Amendment 1's permutation
multiplicity check, 500 draws, bucket memberships held fixed and per-unit P&L permuted:

| | observed | permuted (structureless) |
|---|---|---|
| negative buckets (n ≥ 100) | **2** | **3.0 on average**, 5th–95th pct 0–6 |
| most negative bucket | −$63/unit | −$34 on average, 5th pct −$82 |
| | | **p = 0.776** and **p = 0.128** |

> **The scan found less structure than noise would have produced.**

## 5. The mechanism sentence

> **Duration is forecastable at entry; profitability is not.** The ratchet's own features
> predict how long it will stay flipped — which is a statement about the *signal*, not about
> the *market*. The −15.02 pts/session in short trades is real money, but it is a property of
> what happened, not of anything observable when the decision is made. A trade is short
> *because* the market turned, and nothing available at the flip bar knows that in advance.

This is mechanism law 3 — *throttle the regime variable, not the P&L symptom* — appearing in a
new form: duration is a P&L symptom, and it turns out to be an unusually convincing one.

## 6. What this closes, and what it costs

- The duration axis is closed as an **entry filter**. Filed in `PARKED_NOT_DEAD.md`.
- The event-count law was **not** tested at scale after all — phase 4 never ran, because there
  was no arm to run it with. The law still stands at 4 instances.
- Cost: one script, 45 seconds, no backtest, no adoption. The stopping rule did its job, and
  amendment 1 is the reason it did — the rule as originally written would have authorised a
  full wave on two buckets that noise produces more of.

## 7. Where the search goes instead

Nothing inside the object's own feature set forecasts profitability. `FACT`: sixteen tries,
best |ρ| = 0.108. That is the strongest available argument that the next gain is **not** a
better filter or a better score on this engine — it is **breadth**: a second engine whose
errors are not this engine's errors. Under Charter Amendment 1 there are now three shelved
candidates with real decoupling evidence, and that is the next wave.

## 8. Files
`out/duration2.txt` `out/contradiction.csv` `out/buckets.csv` ·
code `research/weekly_edge/src/run_we_w55.py`
