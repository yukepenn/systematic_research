# C01T2_KSCALE — capital-scale fee-structure curve (K = 1, 2, 3 NQ-equivalents)

Run: `runs/C01T2_KSCALE/` (spec frozen before execution; descriptive, no selection,
`counts_as_trial: no`). Script: `src/analytics/c01_t2_kscale.py`.

## Setup

Frozen member set: the 13 audited R5 ledgers (`runs/AUDIT02_V3_SWEEP_B/ledgers/`,
byte-identical to `research/05_open_axes/h006/`). Member positions, fill re-timing,
raw-price recovery and TRUE_MTM session sampling reused verbatim from the audited
simulator (`src/analytics/audit04_executable.py`); 3-min bars
`runs/AUDIT03_BARS/nq_3m_2022_2026.csv`; raw-price max cross-member spread 0.25 (in cap bound).

Frozen block rule: `units = round(10·K·mean_pos)` clamped to `[-10K, 10K]`
(clamp never binds; mean_pos ∈ [-1, 1]); NQ blocks = `trunc(units/10)`, MNQ = remainder.
Costs: NQ $2.18/side + 1 tick ($5.00) per contract per execution; MNQ $0.65/side +
1 tick ($0.50) per contract per execution. All results divided by K (per-NQ-eq).

**Anchor verified first:** K=1 (= audited E10, via the audited `simulate()` itself)
reproduced net **$179,361.36** to the cent, Sharpe 0.9671, maxDD −$41,252.20,
corr(E0) 0.9985 — all matching `research/audit/executable_ensemble_metrics.csv` —
before any K=2/K=3 number was read.

## The K-curve (per NQ-equivalent; E0_session net = $198,058.82)

| K | Net | Sharpe | MaxDD | Commission | Slippage | Fee drag (% of E0 net) | corr E0_session | NQ / MNQ contracts |
|---|-----------:|------:|-----------:|---------:|---------:|------:|-------:|------------------:|
| 1 | 179,361.36 | 0.9671 | −41,252.20 | 33,881.90 | 26,063.00 | 30.27% | 0.99849 | 0 / 52,126 |
| 2 | 144,125.19 | 0.7768 | −43,170.32 | 45,169.19 | 44,259.50 | 45.15% | 0.99963 | 5,726 / 119,778 |
| 3 | 151,261.82 | 0.8137 | −42,844.42 | 41,626.28 | 43,682.00 | 43.07% | 0.99980 | 10,528 / 156,812 |

Full columns: `c01_t2kscale_curve.csv` (also `runs/C01T2_KSCALE/results.csv`).

## Claim rule (preregistered)

Claim "cost-structure Sharpe gain" only if Sharpe(K=2) − Sharpe(E10) ≥ +0.03 with
corr(E0) ≥ 0.998 maintained.

- ΔSharpe(K2 − K1) = **−0.1903** (needed ≥ +0.03) — **FAIL**
- corr(K2, E0_session) = 0.99963 ≥ 0.998 — pass

**Verdict: NO CLAIM.** The hypothesis that the E10 fee penalty (a pure MNQ fee
multiple) shrinks at K > 1 via cheap NQ blocks is **falsified under the frozen
trunc-block rule** — the curve bends the wrong way.

## Why: block-boundary churn swamps the NQ fee saving

The audited **E20** variant is the exact all-MNQ counterfactual for K=2: its target
is the *identical* `round(20·mean_pos)` unit path, only the leg decomposition differs.

| K=2 variant | Net/NQ-eq | Sharpe | Commission | Slippage | Executions |
|---|-----------:|------:|---------:|---------:|-----------:|
| E20 (all-MNQ, audited) | 173,782.63 | 0.9353 | 33,783.75 | 25,987.50 | 103,950 |
| K=2 blocks (this run) | 144,125.19 | 0.7768 | 45,169.19 | 44,259.50 | 125,504 |

Every crossing of a ±10-unit boundary makes the legs trade *against each other*
(e.g. units 9→10: sell 9 MNQ, buy 1 NQ = 10 executions where the all-MNQ book
needs 1). Unit turnover is 177,038 unit-moves vs E20's 103,950 — 73,088 offsetting
unit-moves of pure churn, costing +$18,272 slippage and +$11,385 commission per
NQ-eq versus E20 — a +$29,657 total penalty that exceeds even the theoretical
maximum commission saving of a hypothetical all-NQ book
(33,784 × (1 − 0.218/0.65) ≈ $22,454). K=3 is milder only because the
finer 30-unit grid crosses block boundaries relatively less often; it still sits
far below K=1.

Slippage, not commission, is the larger loss term: per unit-move, NQ slippage
($5/tick per 10 units = $0.50/unit) equals MNQ's, so blocks save nothing on
slippage even before churn — the block rule can only ever recover commission
(≤ $0.432/side/unit) while every boundary crossing spends whole extra
executions of both.

## Notes

- Exposure identical across K (mean |exposure| ≈ 0.27–0.28 NQ-eq, max 1.0);
  position-path corr ≥ 0.9974 everywhere — this is purely a re-pricing of the
  same frozen positions, as specified.
- corr with E0 *rises* with K (finer grid tracks the fractional target better)
  even as net falls — granularity and cost-structure are separable effects.
- Any "smarter" block rule (hysteresis, no-unwind bands) would be a new
  preregistered experiment; nothing was tuned here.
