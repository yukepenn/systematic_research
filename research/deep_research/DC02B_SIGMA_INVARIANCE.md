# DC02b — U4 resolved: the overshoot ratio is SIGMA-INVARIANT

_2026-08-07, owner-directed reopening. Zero config burn (instrumentation; no strategy executed,
no trial consumed — same class as DC01/DC02 and B01a arm (a)). Scripts:
`src/analytics/u4_overshoot_invariance.py`, `u4_check_1m.py`, `u4_t2c_full.py`.
Data: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (540,232 engine-exact 3-min bars) and
`runs/B01A_BARS_1M/nq_1m_2022_2026.csv` (cross-check). Engine: `src/analytics/dc_overshoot.dc_segments`
reused verbatim. 155,655 DC segments across a 9-point θ grid (60→740 ticks)._

## Question (U4, Empirical Update §6)

Is the DC overshoot ratio r = E[ω]/θ scale-invariant in **tick** space or in **σ** space?
DC01/DC02 had shown vol normalization halves across-year drift of r (0.116→0.058); this
measurement extends that to the full functional form.

## Result: SIGMA-INVARIANT — r ≈ f(θ/σ), a year-stable declining function

1. **Tick space is NOT scale-free.** Pooled r(θ) declines monotonically 1.614 → 1.117 across
   θ = 60 → 740 ticks. r > 1 everywhere (every θ, every year 2022–2026) — the edge is pervasive
   at segment level but thins with θ.
2. **The θ-dependence collapses onto θ/σ.** Within a pooled θ/σ decile, r differs across θ groups
   by only ~0.00–0.15, versus the raw 1.61→1.12 span across θ (T2c). Nearly all θ-dependence of
   r is a θ/σ effect.
3. **σ parameterization halves year-to-year dispersion.** CV of yearly r: fixed tick-θ mean 0.052
   (n-weighted 0.065); fixed θ/σ bands mean 0.031 (n-weighted 0.025); the mass-carrying bands
   θ/σ ∈ [2.0, 9.4] (103k segments) sit at CV 0.013–0.020.
4. **Mechanism visible directly:** yearly σ went 28.5→17.8→22.4→31.1→43.4 ticks/bar (2022→2026);
   fixed θ=179's effective θ/σ went 5.9→9.6→7.5→5.1→3.8 and its r tracked it (1.24→1.22→1.26→
   1.33→1.36). A fixed-tick threshold silently becomes a different strategy as the vol regime
   moves.
5. **Cross-check:** on 1-min bars at θ=179 the known DR05-H1 band reproduces exactly (yearly mean
   ω 204.9–217.9 ticks, r 1.145–1.218). 3-min ω runs ~5–10% higher (resolution effect: coarse
   closes skip marginal low-ω segments), direction and stability identical.

## Implications

- **R5's design is the scientifically correct parameterization.** θ = k·σ pins r, trade rate and
  per-segment economics to a constant operating point across regimes; fixed-tick R4 members carry
  regime beta instead. This is the first evidence that separates the two families on mechanism
  rather than on executability — it does NOT reopen the H-006 performance claim (still
  INCONCLUSIVE, P(diff≤0)=0.358), and it does not permit any new parameter mining.
- **MONITOR-01 should monitor r in θ/σ bands**, not at fixed tick-θ: the σ-banded statistic is
  ~2× more stable, so a genuine decay of the edge (r → 1.0) separates from vol-regime drift far
  sooner.
- The residual trade-off (r per segment falls with θ/σ while flip frequency and cost rise as
  (σ/θ)²) is stationary in σ units — the k-grid 6–30 already spans it; nothing new to tune.
