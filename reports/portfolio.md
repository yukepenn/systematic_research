# Portfolio — NOT BUILT

_2026-08-07 · This is a statement of absence, not a placeholder for work in progress._

**There is no portfolio.** The campaign produced exactly one qualified strategy family (Solar /
directional persistence). A portfolio of one family is not a portfolio, and the signal-conflict
router specified in the mandate (§17) has nothing to route between.

## Why

Families B–E (failed persistence, value reacceptance, session/inventory, other directional) were
**never built** — see [`complementary_families.md`](complementary_families.md) for the full
account. The campaign hit its formal stop condition (§23(B)) before Family B was started: three
consecutive waves produced no robust Pareto improvement, so the governance rule fired.

That is a legitimate reason to stop. It does not convert the gap into a result, and this is
recorded as **the largest gap between the campaign mandate and what was delivered.**

## What multiple Solar variants are *not*

Holding R5 and R4 together is **not** diversification. They are the same mechanism at different
threshold parameterisations, on the same instrument, in the same direction, drawing on the same
right tail. Their daily P&L correlation is high by construction — the campaign's own trial-clustering
found a participation-ratio effective number of bets of roughly **7** across ~316 configurations,
mean pairwise ρ = 0.295. Any "portfolio" of Solar cells is one bet held in several fonts.

The single family risk cap in the mandate (§17: *all Solar variants share one persistence-family
budget*) is therefore the operative constraint, and it is trivially satisfied by holding one
ensemble.

## What exists for future portfolio work

- Daily mark-to-market equity for every family under `research/**/[family]/*.csv`, poolable via
  `src/analytics/ensembles.py` on the 1,424-session campaign calendar.
- The frozen baseline's daily equity at `runs/SW00_R01/daily_equity.parquet`.
- `src/analytics/trials.py`, which already implements correlation clustering and the
  effective-number-of-bets estimator — the machinery a real portfolio study would need.

## Preconditions before this file should contain anything

1. At least one complementary family with an **independent mechanism** and **standalone**
   expectancy — not merely a blend improvement.
2. It must be tested on **both** a fixed and an adaptive Solar core. The C2 failure established
   that a sleeve can improve one core and reverse sign on the other.
3. It must be checked for **Solar right-tail retention**. An engine that fires during Solar's ten
   best days is not a complement; it is a hedge funded out of the only profitable trades in the
   system.
4. Preregister all three conditions before running.
