# ⚠️ SUPERSEDED — this run's BANDS are not current

**Superseded 2026-08-27 by `runs/FWD_BOOTSTRAP_V2_20260827/`, same day, before any seal read.**

Two defects in the ESTIMATOR, neither of them in the data:

1. **The "primary" and "sensitivity" p01 at the same block length were two independent draws.**
   The primary loop created one RNG and consumed it sequentially across CPA → CPB → CPC; the
   sensitivity loop reset the seed in every cell. CPA agreed to the cent (it is drawn first, while
   the stream is fresh) which is precisely what disguised it. At CPC the two disagreed by **$832**
   while the block-length effect the table claimed to measure was **$568** — so that cell was
   reporting its own Monte-Carlo noise.

2. **`B = 40,000` was never validated.** Measured directly with 40 independent batches, the MC sd
   of p01 reaches **$444**. Every published band carried ±$200–450 of undisclosed simulation noise.

**V2 fixes both**: deterministic child seeds keyed by `(checkpoint, block_length)` with a blocking
equality assertion, and `B = 600,000` set by a tolerance (MC SE ≤ $250) declared before measurement.

**What survives unchanged:** the empirical-over-Gaussian finding (stronger at V2's precision —
the Gaussian INVALIDATION band is $5,185 / $6,173 / $7,736 too loose), and the *conclusion* that
p01 must be carried as a range. **That conclusion was right; this run's evidence for it was not.**

The `$4,099` maximum spread quoted here is withdrawn — it came from the pre-canonical weekly
series. The correct figure is **$2,869**, at CPA.

The `out/` files below are left exactly as produced, for the record.
