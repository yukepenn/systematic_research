# MS-LAST — the certified trade-flow family carries no 60-second information, and the blind pool is unspent

| | |
|---|---|
| **run class** | **DISCOVERY — closed NULL.** No candidate produced, no promotion |
| date | 2026-08-27 |
| code | `src/contract.py` · `src/costmodel.py` · `src/substrate.py` · `src/discover.py` · `src/power.py` |
| data | **104 consumed sessions**, 139,371 decisions. `≥ 2026-08-01` untouched (max date used **2026-07-31**) |
| **blind pool** | ✅ **NOT SPENT.** Intersection with the 141-session pool asserted **= 0**. It remains available for a future candidate |

> ### **The 60-second NQ move is a martingale with respect to every order-invariant Last-only
> ### feature this export can support.** Out-of-fold `r = −0.0016`, session-clustered
> ### 95 % CI **`[−0.0115, +0.0089]`**, `R² = −0.002`. Well powered, not closed by power.

---

## 1. The data contract — and it rejected the obvious features

MS01A established that within-millisecond sequence is unrecoverable. §4B therefore requires every
admitted feature to be **invariant to permutation of rows sharing a timestamp**, or built only from
**prior distinct timestamps**. The solution is structural: collapse each distinct timestamp into one
bucket using order-invariant aggregates (`sum`, `vwap`, `count`, `max`, `min`, `nunique`), then
build everything from the **sequence of buckets**, whose order is well defined by construction.

Verified rather than assumed — every feature computed on the natural order and again on a random
permutation *inside* each tied-timestamp group, on 12 sessions:

| feature family | max relative change | verdict |
|---|---:|---|
| all 10 **bucket** features (`signed_flow`, `displacement`, `realized_vol`, `vol_concentration`, …) | **`0.000e+00`** | **ADMISSIBLE** |
| `rowwise_signed_flow` — the classic tick rule | **`2.736e+00`** | **DROPPED** |
| `rowwise_realized_vol` | `6.430e-01` | DROPPED |
| `rowwise_uptick_frac` | `2.799e-01` | DROPPED |
| `rowwise_abs_flow` | `2.982e-01` | DROPPED |
| `rowwise_displacement` | `1.266e-02` | DROPPED |

> ### **The textbook tick-rule signed flow changes by 274 % of its own value when rows inside a
> ### millisecond are shuffled.** On this export it is substantially a function of file ordering,
> ### which carries no exchange information. It is not repaired — it is replaced.

**Scope correction, recorded rather than buried.** MS01A's **81.1 %** same-millisecond rate was
measured across *all* events. For **Last events alone** — the population this lane actually uses —
it is **46–54 %**. Both are correct about different populations; only the second governs this lane.

## 2. ⚠️ A material correction to MS01A: the quote-location result was contaminated

MS01A reported trades printing **69.57 % inside** the spread, with effective/quoted = **0.604**, and
read it as *"the median trade prints at the mid of a wide quoted spread."*

`audit.py:65` uses `np.searchsorted(tb, tl, side="right") - 1` — which admits quotes **from the
same millisecond as the trade**. That is precisely the ambiguity MS01A itself identified. In a tied
millisecond the quote has already moved *in response to* the trade, so the trade appears to sit
inside a spread that only exists post-trade.

Both constructions, identical data, RTH only:

| construction | at bid | at ask | **inside** | outside | eff/quoted |
|---|---:|---:|---:|---:|---:|
| **MS01A** — same ms admitted | 11.50 % | 11.75 % | **69.61 %** | 7.14 % | 0.604 |
| **corrected** — strictly prior ms | 30.83 % | 29.53 % | **8.90 %** | 30.74 % | **1.478** |

The first row reproduces MS01A's published figures (69.57 / 11.21 / 11.31) to within rounding, which
is how the cause was isolated rather than guessed.

> **The corrected picture is the textbook one**: trades occur at the touch, and **31 % print
> *beyond* the last causally-available quote** — latency and adverse selection, not price
> improvement.
>
> **MS01A's premise is corrected; its CONCLUSION survives and is now better founded.** It concluded
> the quoted spread is the right cost for a strategy that must cross. That is right — and the real
> reason is stronger than the one given: you do not print at the mid, you print at or beyond the
> touch.

## 3. The cost model, frozen before any blind read (§4E)

The blind sessions are Last-only — 101 of 141 carry no quotes at all — so their scores can never use
post-hoc Ask/Bid labels. The schedule is therefore built **entirely from consumed BBO** and frozen.

**A Last price is not a mid.** Using a trade print as both entry and exit embeds bid-ask bounce,
which manufactures negative autocorrelation a reversal strategy would happily "exploit". That is
undetectable from Last-only data alone, so it was measured on the 58 consumed sessions that carry
**both**:

| side | proxy mean | true `Ask→Bid` mean | **bias** | corr | sign agreement |
|---|---:|---:|---:|---:|---:|
| long | −$27.572 | −$29.168 | **+$1.596** | 0.9946 | 95.6 % |
| short | −$26.367 | −$27.961 | **+$1.595** | 0.9946 | 95.6 % |

**The proxy flatters by ~$1.60 per decision**, so a **0.50-tick ($2.50) surcharge** is carried in
every frozen cost. The check earned its place: without it the lane would have run ~$1.60/decision
optimistic against a true executable fill.

| hours ET | median quoted | **PRIMARY $/RT** | STRESS +1t | STRESS +2t |
|---|---:|---:|---:|---:|
| 11–16 (RTH core) | 3.0 ticks | **$21.86** | $26.86 | $31.86 |
| 9–10 | 4.0 ticks | $26.86 | $31.86 | $36.86 |
| 0–8, 21–23 | 5.0 ticks | $31.86 | $36.86 | $41.86 |
| 18–20 (evening open) | 6.0 ticks | $36.86 | $41.86 | $46.86 |

Both stress ladders were fixed **before any alpha existed**, precisely so a disappointing headline
could not later be rescued by discovering a gentler cost model.

## 4. The discovery result

60-second decision clock, 60-second horizon, information set strictly `< t`, three fixed lookbacks
(60/300/900 s), 23 certified features, expanding-origin **session-block** validation,
training-only normalization. **Two model attempts, both counted.**

| arm | $/session | t | positive sessions | trade rate | directional accuracy |
|---|---:|---:|---:|---:|---:|
| ALWAYS LONG | −$39,495 | −50.4 | | 100 % | |
| ALWAYS SHORT | −$39,518 | −51.6 | | 100 % | |
| RANDOM DIRECTION | −$38,800 | −55.5 | | 100 % | |
| **RIDGE (primary)** | **−$987** | −3.92 | 41.9 % | 2.4 % | **49.4 %** |
| GBM shallow (challenger) | −$214 | −0.77 | 43.0 % | 1.3 % | **50.5 %** |

Against an **activity-matched random-direction placebo** (same trade times, random side, whole
sessions resampled): ridge lands at the **22.4th** percentile, GBM at the **79.2nd**. Neither clears
95. Bonferroni threshold for 2 attempts: |t| > 2.275.

## 5. NULL, not CLOSED-BY-POWER — the distinction is measured, not asserted

| | |
|---|---|
| out-of-fold Pearson `r` | **−0.00156**, session-clustered 95 % CI **[−0.01150, +0.00890]** |
| out-of-fold `R²` | **−0.002079** (worse than predicting the mean) |
| prediction sd vs move sd | $9.30 vs $214.08 — **ratio 0.043** |
| sessions | 86 evaluated (the first block is training-only under expanding origin) |
| per-session P&L sd | $2,332.87 |
| **MDE** ~80 % power | **$704.37/session** — and the always-on arms pay $39,506/session in friction |
| MDE per trade | $22.21, against a mean \|move\| of $316.28 on traded decisions |

**The information question and the economics question both answer NO**, and the second could have
detected an edge an order of magnitude below what would matter.

### The finding underneath the null

| | |
|---|---:|
| per-session lag-1 autocorrelation of the 60 s move | **−0.0065** (session-clustered t **−1.03**) |
| unconditional mean 60 s move | **−$0.015** (session-clustered t **+0.04**) |

> ### **The 60-second NQ move is a martingale.** No drift, no serial dependence, and no
> ### association with any order-invariant trade-flow feature. That is *why* the null, and it is a
> ### stronger statement than "our model failed" — it says where a future predictor must not look.

---

## Verdict

| | |
|---|---|
| **what was measured** | whether certified order-invariant Last-only trade-flow features predict 60 s after-cost executable NQ P&L |
| **what passed** | the **data contract** (10/10 bucket features exactly permutation-invariant); the **cost model** (proxy corr 0.9946, surcharge applied); the **power** of the economic test |
| **what failed** | the alpha. Both arms; both nulls; information and economics alike |
| **what changed** | MS01A's quote-location premise is **corrected** (69.6 % inside → 8.9 %; eff/quoted 0.604 → 1.478) — **its cost conclusion survives and is better founded**. The 81.1 % tie rate is **scoped** to all-events; Last-only is 46–54 %. Five naive tick-rule features are **permanently blocked** |
| **what did NOT change** | the incumbent, the seal, the blind pool, the frozen cost schedule |
| **evidence class** | **FALSIFIED-NULL-CLOSED** for the certified order-invariant trade-flow family at 60 s. **NOT** "microstructure is useless" — BBO-derived state, other horizons, and non-flow constructions are untouched by this |
| **ladder status** | no candidate, no promotion, no demotion |
| **data pool burned** | **104 already-consumed sessions re-read** — re-reading burned data does not burn it further. **The 141-session blind pool is UNSPENT**, asserted programmatically (`intersection = 0`) |
| **next highest-EVI runnable question** | **Multi-market TSMOM V1** — the co-primary lane, and the only one offering economically independent exposure |
