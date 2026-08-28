# FWD_BOOTSTRAP_V2 — the forward bands were reported with more precision than they had

| | |
|---|---|
| **run class** | **ESTIMATOR REPAIR** — pre-read, no promotion, frozen strategy untouched |
| date | 2026-08-27 |
| code | `src/bootstrap_v2.py` · `out/bootstrap_v2.txt` · `out/checkpoint_bands_v2.csv` · `out/block_sensitivity_v2.csv` |
| seal | **untouched** — no `≥ 2026-08-01` data is read, which is why this repair is legal now |
| supersedes | `runs/FWD_BOOTSTRAP_20260827/` — **bands only**. That run's *qualitative* findings survive |

> ### **`FWD_BOOTSTRAP` reported a "primary" p01 and a "sensitivity" p01 at the same block
> ### length that were two independent Monte-Carlo draws, and at CPC they disagreed by `$832`
> ### while the block-length effect it claimed to measure was `$568`.**
> ### **The dependence-sensitivity table was, at that checkpoint, reporting its own noise.**

---

## 1. The defect, found by provenance and not by nearest-number matching

The **SOURCE-PROVENANCE GATE** was applied in order: locate the generating artifact → locate the
generating code → locate its convention → reproduce → *only then* consider alternatives. The cause
is four lines apart in one file and needed no search over candidate explanations.

```python
# runs/FWD_BOOTSTRAP_20260827/src/bootstrap.py — PRIMARY (line 98)
rng = np.random.default_rng(SEED)          # created ONCE...
for cp, sess in CHECKPOINTS.items():       # ...then consumed SEQUENTIALLY by A -> B -> C
    starts = rng.integers(0, n, size=(B, nb))

# same file — SENSITIVITY (line 161)
for cp, sess in CHECKPOINTS.items():
    for L2 in (3, 6, 12):
        r2 = np.random.default_rng(SEED)   # created FRESH in EVERY cell
```

Re-running both code paths literally:

| checkpoint | V1 "primary" L=6 | V1 "sensitivity" L=6 | difference |
|---|---:|---:|---:|
| **CPA** | −$14,532.45 | −$14,532.45 | **$0.00** |
| CPB | −$12,777.46 | −$12,880.56 | $103.10 |
| **CPC** | −$2,436.60 | −$1,605.09 | **−$831.51** |

> **CPA agrees to the cent — and that is what hid the defect.** CPA is drawn *first*, while the
> primary stream is still fresh, so it is genuinely the same draw. By CPC the primary stream has
> been advanced by 280,000 prior integers while the sensitivity loop has reset to `SEED`. The two
> "L = 6" numbers were never one estimator.

## 2. Why it matters more than a reproducibility nit

**V1's own CPC block-length spread was `$568`. Two independent 40,000-replicate estimates of the
*same* CPC quantity differ by `$832`.** A sensitivity analysis whose reported signal is smaller
than its own measurement error cannot support a conclusion — in either direction.

So the first thing V2 does is **measure** the Monte-Carlo error instead of assuming it away:
**40 independent batches** of `B = 40,000` per (checkpoint, block length).

| checkpoint | L | MC **sd** of p01 at B = 40,000 |
|---|---:|---:|
| CPA | 3 / 6 / 12 | $210 / $244 / $352 |
| CPB | 3 / 6 / 12 | $245 / **$386** / $282 |
| CPC | 3 / 6 / 12 | $367 / **$444** / $398 |

**Every band V1 published carried ±$200–450 of pure simulation noise that was never disclosed.**
`B = 40,000` was not enough, and "40,000 resamples reduce Monte-Carlo noise" — V1's own words —
was true but unquantified, which is the problem.

**Declared before measurement:** MC standard error of every reported percentile ≤ **$250**
(≈1.2 % of the $20,245 risk budget, far below the smallest gap between adjacent bands). The rule
fixes `B`, so `B` cannot be chosen to land a threshold somewhere convenient. It gives
**`B = 600,000`** — **15× V1**.

## 3. The corrected bands

**Empirical, `L = 6`, `B = 600,000`, MC SE ≤ $250 by construction.**

| checkpoint | expected | **INVALIDATION** < p01 | **WATCH** p05 | **HEALTHY** ≥ p25 | P(cum < 0) |
|---|---:|---:|---:|---:|---:|
| **CPA** — 60 sessions | $14,764 | **−$14,805** | −$6,786 | $5,118 | **13.9 %** |
| **CPB** — 126 sessions | $30,759 | **−$13,231** | −$1,134 | $16,786 | 5.7 % |
| **CPC** — 252 sessions | $61,518 | **−$1,688** | $15,837 | $41,868 | 1.2 % |

Movement from V1: CPA **−$273**, CPB **−$454**, CPC **+$749**. Small in the tail that matters, but
they are now *reproducible*, which the old ones were not.

## 4. The block-length effect is REAL — and V1 could not have known that

Now that the noise floor is measured, the comparison is meaningful for the first time:

| checkpoint | L=3 | L=6 | L=12 | spread | MC sd | spread / MC sd | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| CPA | −$14,159 | −$14,805 | −$11,936 | **$2,869** | $69 | **41.4×** | REAL |
| CPB | −$12,284 | −$13,231 | −$12,848 | $948 | $79 | 12.1× | REAL |
| CPC | −$601 | −$1,688 | −$1,631 | $1,087 | $104 | 10.4× | REAL |

> **V1's conclusion — carry p01 as a RANGE, never a single number — was CORRECT.
> V1's evidence for it was not.** At CPC the claimed spread was smaller than the noise;
> the right call was reached through a measurement that could not support it.
> The `$4,099` figure V1 quoted is withdrawn: it came from the pre-canonical weekly series.
> **The correct maximum spread is `$2,869`, at CPA.**

## 5. A second defect the noise measurement exposed: a degenerate cell

CPA/L=12 showed an MC sd of **$961 on p05** while its p25 sd was only **$48** — a shape that noise
alone does not produce. The support size explains it:

| checkpoint | L | blocks | distinct paths | status |
|---|---:|---:|---:|---|
| CPA | 6 | 2 | **45,369** | enumerable |
| CPA | **12** | **1** | **213** | **degenerate** |
| all others | | | ≥ 9.7 M | ample |

**At CPA with L = 12 the "bootstrap" is not a bootstrap.** One block of 12 weeks covering a
12-week horizon means each replicate is a single contiguous historical window, so the sampler is
enumerating the **213 twelve-week windows in the record**. Its percentiles are *quantized*: the
tail estimate hops between adjacent atoms, and **no number of replicates fixes it** — that is a
property of the design, not the data.

Where the support is enumerable the exact percentile is computable with **zero** Monte-Carlo error,
which also **validates the sampler**:

| cell | EXACT p01 | sampled at B = 600,000 | error |
|---|---:|---:|---:|
| CPA, L = 6 (45,369 atoms) | −$14,792.61 | −$14,805.01 | **$12.40** |
| CPA, L = 12 (213 atoms) | −$11,926.91 | −$11,936.22 | **$9.31** |

**The CPA range is therefore driven by its degenerate cell**, and that is disclosed rather than
quietly kept: −$11,937 is the 2nd-worst of 213 historical 12-week windows, not a resampled tail.

## 6. The blocking assertion

```
A    primary $-14,805.0066   sensitivity $-14,805.0066   IDENTICAL
B    primary $-13,231.3850   sensitivity $-13,231.3850   IDENTICAL
C    primary $ -1,688.0330   sensitivity $ -1,688.0330   IDENTICAL
```

Both paths resolve to the deterministic child seed `[SEED, checkpoint_ordinal, block_length]`, so
they are the same draw **by construction rather than by luck of ordering**. The script **aborts**
if they ever diverge. This is the permanent guard the directive asked for.

## 7. What survives from V1, unchanged

**The Gaussian is the wrong instrument, and it is wrong in the dangerous direction.** Re-measured
at `B = 600,000`, the Gaussian INVALIDATION band is too **loose** at every checkpoint — meaning a
genuinely broken strategy could have passed it:

| checkpoint | empirical p01 | Gaussian p01 | **Gaussian error** |
|---|---:|---:|---:|
| CPA | −$14,805 | −$19,990 | **$5,185 TOO LOOSE** |
| CPB | −$13,231 | −$19,404 | **$6,173 TOO LOOSE** |
| CPC | −$1,688 | −$9,424 | **$7,736 TOO LOOSE** |

Skew **+1.888**, excess kurtosis **8.717**, Jarque-Bera p ≈ **1.2e-174**. The empirical bootstrap
stays primary.

---

## Verdict

| | |
|---|---|
| **what was measured** | the Monte-Carlo error of the forward checkpoint bands, and whether the reported block-length sensitivity exceeds it |
| **what passed** | the empirical-over-Gaussian finding; V1's *conclusion* that p01 must be a range; the sampler itself (validated to $12 against exact enumeration) |
| **what failed** | V1's **estimator**: "primary" and "sensitivity" at L=6 were independent draws; `B = 40,000` carried undisclosed ±$200–450 noise; CPC's claimed dependence effect was smaller than that noise; the `$4,099` spread was from the pre-canonical series |
| **what changed** | bands move by −$273 / −$454 / +$749; `B` 40,000 → 600,000; max block spread $4,099 → **$2,869**; P(losing quarter) 13.8 % → **13.9 %**; a permanent equality assertion now guards the design |
| **what did NOT change** | the frozen strategy, the weekly series, `k = 0.882879`, the ISO-week convention, the checkpoint calendar, the primary block length, the sensitivity grid |
| **evidence class** | **RESEARCH-INTERNAL / PRE-FROZEN.** Bands are properties of the historical series, not forward evidence |
| **ladder status** | no promotion, no demotion. This makes an existing threshold *reproducible*; it does not make the incumbent better or worse |
| **data pool burned** | **NONE.** No sealed data read; no new discovery performed |
| **next** | amend `WEEKLY_EDGE_FORWARD_PROTOCOL` before any checkpoint read, then return to alpha |
