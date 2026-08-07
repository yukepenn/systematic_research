# Hypothesis Frontier — living document

Status key: SEED (from mandate) | HOUSE (our own, from first principles / Solar findings) |
DR (from deep research) | T0/T1/T2/T3 (tier reached) | BLOCKED_BY_DATA | REJECTED (→ REJECTED_IDEAS.md)

## Seed families (mandate §14 — starting points, not a menu)
S1 micro momentum · S2 breakout/pullback/rebreak · S3 velocity/impulse burst ·
S4 failed break/snapback · S5 compression→expansion · S6 liquidity vacuum (data-gated) ·
S7 absorption (data-gated) · S8 queue/microprice (data-gated) · S9 OFI/trade-flow (data-gated) ·
S10 spread/liquidity state (data-gated) · M1 VWAP/value · M2 opening auction/ORB ·
M3 overnight inventory · X1 ES→NQ lead-lag · X2 NQ/ES relative state · X3 cross-index
confirmation · T1 session conditioning · E1 scheduled-event state

## HOUSE hypotheses (added at bootstrap, 2026-08-07 — before any data was read)

**Z1 — DC-overshoot scale transfer.** We hold a validated in-house scaling law nobody else
has: NQ directional-change overshoot ratio r = E[ω]/δ ≈ 1.29 at θ=179 ticks, σ-banded and
within-session (DC02b, T0-9). Question: what is r(θ) for θ ∈ {5..80} ticks, and does net
$/cycle after C1 turn positive anywhere? At θ=179 net was +$10.91/cycle (94.6th pct of
surrogate null, sub-threshold). Small θ → more cycles/day (scalp frequency) but friction is
fixed per cycle. Existing tooling: `src/analytics/dc_overshoot.py`, numba DC ladder.
Mechanism: same within-session continuation that funds Family A, harvested at micro scale.
Falsifier: r(θ)−1 shrinks below friction-implied breakeven for all θ<100.

**Z2 — Speed-conditional continuation.** Time-to-travel-N-ticks as the state variable:
moves that cover N ticks unusually fast (vs same-session σ) continue; unusually slow
grinds revert. Mechanism: fast traverse = one-sided liquidity consumption; slow traverse =
two-sided rotation. Price-only, Level-1 sufficient. Distinct from S3 (conditions on
duration percentile, not raw velocity).

**Z3 — Grid/round-number microstructure.** NQ 25/100-point levels as resting-liquidity
magnets: approach dynamics (accept/reject) at these levels at second-scale. Mechanism:
human/algo order clustering at round numbers. Price-only. Risk: folklore; needs matched
null at pseudo-levels (e.g. xx37.5) to survive.

**Z4 — Cash-close mechanical window.** 15:45–16:00 ET (US cash equity close, MOC imbalance
processing) creates mechanical index-arb flow in NQ. Test conditional drift/reversal around
15:50 imbalance-proxy moves. Calendar-causal, repeats daily.

**Z5 — RTH-open liquidity transition.** First seconds/minutes after 09:30 ET: overnight
inventory unwind meets cash-open price discovery. Separate continuation vs failure of the
overnight direction (links M2/M3 but at second-scale with explicit latency surface).

**Z6 — Session-open (18:00 ET) micro-drift.** Globex reopen after the 17:00–18:00 halt:
gap-settle dynamics in the first minutes; thin book → measurable but possibly untradable
(spread state must be checked — honest C1 accounting will likely kill it; cheap to test).

## Discovery queue (DR agents append below with mechanism/observable/horizon/falsifier)
