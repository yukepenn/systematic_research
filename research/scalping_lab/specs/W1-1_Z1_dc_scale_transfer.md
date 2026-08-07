# W1-1 — Z1: DC-Overshoot Scale Transfer (Tier-0 event study, preregistered)

Date: 2026-08-07. Hypothesis Z1 (HOUSE). Zone: MICRO / STRUCTURAL_SCALP (by θ).
Status: spec frozen BEFORE any tick-level DC statistic is read. Gated on the W1-0/I-5
export pipeline; runs on the DEVELOPMENT tick window only.

## Question
Family A's engine is the σ-banded within-session overshoot ratio r = E[ω]/δ ≈ 1.29 at
θ = 179 ticks (3-min closes). Does r(θ) remain > 1 at micro θ on tick data, and is there
any θ where net-per-cycle SURVIVES REAL FRICTION under BBO_EXEC?

## Frozen design
- **Price stream: causal MID = (Bid+Ask)/2** from the L2 series, sampled at quote updates.
  Rationale (frozen a priori): trade-price DC at small θ is mechanically contaminated by
  bid-ask bounce (Roll); mid-price DC is not. Trade-price r(θ) is ALSO computed as a
  diagnostic column — the (trade − mid) r gap is itself a bounce measurement cross-check
  for I-2. No selection between the two streams: mid is primary by this spec.
- **θ grid (frozen): {5, 10, 20, 40, 80, 160} ticks.** No interpolation, no refinement of
  the grid after readout (a finer grid = new spec, new wave).
- Per θ: DC ladder (existing `dc_overshoot` semantics, fixed-tick θ), within-session only
  (cycles crossing session boundaries dropped, as in T0-9). Report: cycles/day, E[ω], r,
  r by session-σ band (DC02b banding), inter-event durations (median, p90).
- **Economics per cycle under BBO_EXEC**: entry at causal Ask/Bid at flip + 250ms, exit at
  next flip + 250ms; commission $2.18/side; residual slippage stress 0 and +1 tick reported
  side by side. BENCHMARK_C1 column alongside. Latency decay: repeat at L ∈ {next-event,
  250ms, 1s, 5s} for the single most economic θ only (frozen: chosen by net/cycle at 250ms
  — this is a reporting choice inside one preregistered readout, not iterative tuning).
- **Inference**: day-clustered bootstrap (1,000 resamples, seed 20260807) on net/cycle;
  report raw cycle count, independent days, effective N.

## Frozen interpretation rules
- r(θ) ≤ 1.02 across the micro grid → Z1 CLOSED for standalone direction (scale transfer
  fails); the σ-invariance story stays a 3-min-scale property.
- r(θ) > 1 but net/cycle < 0 at every θ under both cost models → Z1 CLOSED as standalone
  (information without economics); r(θ) curve still published as campaign reference and Z1
  re-registered ONLY as a role-B/C feature candidate (Amendment §2) in a future spec.
- net/cycle > 0 with day-clustered 95% CI excluding 0 at any θ → escalate that θ to Tier-1
  (new spec, R1-equivalent trial accounting).
- Mixed/marginal → record, no escalation, no grid refinement.

DoF charged: 6 θ × 1 stream (mid primary) = 6; diagnostics don't gate.
Deliverables: research/scalping_lab/artifacts/z1/z1_r_curve.csv, z1_economics.csv,
z1_report.md; registry rows seq-assigned at readout.
