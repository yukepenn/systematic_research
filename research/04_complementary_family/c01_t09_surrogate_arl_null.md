# C01 T0-9 — Surrogate ARL Null (epistemic hardening)

_Executed 2026-08-07 under the frozen preregistration in `C01_WAVE_SPEC.md` (item T0-9).
No constant was adjusted after any result was read. Instrumentation class: 0 R1 trials._

## Verdict: **FAIL** (mechanism not distinguishable from ARL noise sampling under this null)

- Post-flip drift exceeded the surrogate 97.5th percentile at **0 of 3** horizons (gate required ≥2).
- Net $/cycle fell **inside** the 95% surrogate band (one-sided p = 0.054; 27/500 surrogates ≥ real).
- Every registered statistic fell inside its band. Per the frozen consequence clause:
  **threshold engineering is permanently deprioritized.**

## Frozen design

| Element | Value |
|---|---|
| Flip rule | DC ladder (exact `dc_overshoot.dc_segments` semantics), fixed θ = 179 ticks = 44.75 pts, on 3-min closes |
| Data | `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, 540,232 bars, 2022-01-02 18:03 → 2026-07-31 16:57 ET (4.575 yr) |
| Surrogates | 500 stationary block bootstraps (Politis–Romano) of 3-min log returns, geometric blocks, mean 460 bars (~1 session), price rebuilt from the real starting close |
| Costs | $4.36 RT commission + 1 tick slip per execution (2 executions/cycle → $10.00) = $14.36/cycle |
| Drift | mean over flips of dirn × (close[i_flip+H] − close[i_flip]) in ticks, H ∈ {20, 80, 460}; truncated flips excluded |
| Per-cycle P&L | gross = mean(ω − drop) × $20 (drop = θ + excess); ω−θ reported separately in ticks |
| Seed / N | 20260807 / **500 completed (no reduction)** |

Implementation validation: numba ladder vs `src/analytics/dc_overshoot.py::dc_segments` on the
first 120k bars — exact match (3,412 segments, identical indices, directions, extremes).

## Real-data reference (θ = 179 ticks, full 2022–2026)

- Flips: 14,593 → **3,189.9 flips/yr**
- Inter-flip bars: **median 16** (48 min), **p90 91** (~4.6 h)
- Mean overshoot ω = 231.54 ticks → **r = ω/θ = 1.2935** (consistent with DC01/DC02 instrumentation)
- **ω − θ = +52.54 ticks**; mean crossing excess = 47.49 ticks
- Gross $/cycle = $25.27 → **net $/cycle = +$10.91** after $14.36 costs
- Post-flip drift: **+1.81 ticks @20b (1h), +0.99 @80b (4h), +2.88 @460b (~1 session)**
  (n = 14,593 / 14,589 / 14,567)

## Real vs surrogate bands (500 surrogates)

| Statistic | Real | p2.5 | p50 | p97.5 | Position | frac surr ≥ real |
|---|---:|---:|---:|---:|---|---:|
| flips/yr | 3,189.9 | 2,039.4 | 4,073.6 | 7,843.2 | INSIDE | 0.766 |
| inter-flip median bars | 16 | 7 | 13 | 25 | INSIDE | 0.302 |
| inter-flip p90 bars | 91 | 34 | 70 | 153 | INSIDE | 0.236 |
| drift @20b (ticks) | 1.81 | −2.55 | 0.12 | 3.00 | INSIDE | 0.146 |
| drift @80b (ticks) | 0.99 | −2.70 | 0.24 | 3.22 | INSIDE | 0.342 |
| drift @460b (ticks) | 2.88 | −2.12 | 0.84 | 3.77 | INSIDE | 0.090 |
| mean ω (ticks) | 231.54 | 217.85 | 235.48 | 265.99 | INSIDE | 0.622 |
| r = ω/θ | 1.2935 | 1.2171 | 1.3156 | 1.4860 | INSIDE | 0.622 |
| ω − θ (ticks) | 52.54 | 38.85 | 56.48 | 86.99 | INSIDE | 0.622 |
| mean excess (ticks) | 47.49 | 37.75 | 53.70 | 87.76 | INSIDE | 0.748 |
| gross $/cycle | 25.27 | −14.52 | 8.19 | 28.58 | INSIDE | 0.054 |
| net $/cycle | 10.91 | −28.88 | −6.17 | 14.22 | INSIDE | 0.054 |

Full per-surrogate statistics: `c01_t09_surrogate_stats.csv`; band table: `c01_t09_real_vs_surrogate_bands.csv`.

## Gate evaluation (frozen)

1. Real post-flip drift > surrogate p97.5 at ≥2 of 3 horizons: **0/3** → fail
   (one-sided p: 0.146 @20b, 0.342 @80b, 0.090 @460b).
2. Real net $/cycle outside the 95% band: **no** ($10.91 vs band [−$28.88, $14.22], p = 0.054) → fail.

**Both clauses fail → T0-9 FAIL.** Statistics inside the band: all of them (drift ×3, net $/cycle,
flips/yr, inter-flip median/p90, ω−θ, r, excess, gross $/cycle).

## Honest interpretation and limits (no gate bearing)

- **What this null is.** With mean block ≈ 1 session, the bootstrap preserves essentially all
  within-session dependence (vol clustering AND intraday trend persistence up to the block scale)
  while destroying cross-session ordering. The finding is therefore: **the DC flip edge at θ=179
  requires no cross-session trend sequencing** — session-scrambled surrogates reproduce r ≈ 1.29
  and frequently reproduce the per-cycle economics. The median surrogate is still net-negative
  (−$6.17/cycle) while real is +$10.91 at the 94.6th percentile — directionally suggestive,
  short of the preregistered bar.
- The overshoot ratio r is matched almost exactly by the surrogate median (1.316 vs 1.294 real):
  r > 1 by itself is a property of the within-session return structure, not evidence of an
  exploitable multi-session mechanism. This retroactively weakens r-based mechanism claims and
  strengthens the case that the ensemble's edge (per campaign findings) lives elsewhere
  (episode/tail structure), not in threshold placement.
- Fixed tick-denominated θ on bootstrap-rebuilt price levels lets surrogate price wander from the
  real level, widening bands (flips/yr band 2,039–7,843). This makes the gate conservative; the
  design was frozen and is reported as run.
- Consequence per spec: threshold engineering (any further θ/ARL tuning) is **permanently
  deprioritized**. This is consistent with, and hardens, the DR03/H-006 line: fixed-θ behavior is
  adequately explained without invoking a tunable trend-persistence mechanism at the flip scale.

## Reproducibility

Script: session scratchpad `t09_surrogate_arl.py` (numba DC ladder, exact-match validated;
seed 20260807; runtime 15.5 s for 500 surrogates). Outputs committed alongside this report.
