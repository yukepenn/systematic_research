# CAPITAL_FRONTIER — capital vs growth/ruin for both current baselines

**Frozen 2026-08-10.** Master Directive v4 sec31. Covers Product A (`SolarWaveSMMaster_v4`) and
Product B (`SolarWaveOneContractNQ_v5`/`_MNQ_v5`) — the only two objects with canonical status as
of this wave (U6B was NOT PROMOTED, see `runs/U6B_PRODUCT_A_SCALE_RATE/adversarial_review/
REPORT.md`; no challenger is promoted this wave). All figures reuse `primary_objective_v2`
directly (never a new implementation), `n_boot=2000`, `seed=20260808`, R1=25% absorbing ruin
barrier, λ≈1.3677/yr (module-derived). Product A uses genuine-MNQ execution economics throughout
(source: `runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/out/part2_capital_frontier.csv`, `CONTROL` row
— CONTROL is byte-identical to unmodified Product A, per `runs/U6B_PRODUCT_A_SCALE_RATE/
adversarial_review/REPORT.md`'s own code-structure proof that price/mechanism never touch the
decision layer). Product B uses each instrument's own certified series (source:
`runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/out/part2_context_productB_frontier.csv`).

## Product A (`SolarWaveSMMaster_v4`)

| capital | J (mixture) | J_worst (Γ-minimax) | CE_g (ann.) | P_ruin |
|---:|---:|---:|---:|---:|
| $50,000 | −1.1744 | −1.1872 | 0.1436 | 96.4% |
| $75,000 | −0.3377 | −0.7277 | 0.3118 | 47.5% |
| $100,000 | +0.0594 | −0.2146 | 0.3051 | 18.0% |
| **$150,000** | **+0.1970** | **+0.1312** | 0.2319 | 2.6% |
| $200,000 | +0.1727 | +0.1581 | 0.1798 | 0.5% |
| $300,000 | +0.1231 | +0.1222 | 0.1231 | ~0% |
| $500,000 | +0.0753 | +0.0748 | 0.0753 | ~0% |

**Shape**: hump-shaped, peaks at **$150,000** (both aggregation conventions agree on the peak
location). Below ~$75k the ruin penalty dominates and J is deeply negative despite positive raw
growth; above ~$200k CE_g's own decline (less effective leverage) dominates. **Marginal benefit of
extra capital**: essentially all of the practical benefit is captured by $150k–$200k; doubling
capital again to $300k–$500k trades away growth for ruin-safety that was already near-zero at
$200k.

**Intraday caveat (critical, from the same risk panel)**: at the **$100,000** headline capital
specifically, the single REALIZED (non-bootstrapped) worst bar-level intraday drawdown already
consumes **32.6%–32.9%** of capital — past the 25% ruin threshold with zero resampling. At
$150,000 the realized bar-level drawdown (21.7%–21.9%) stays under 25%, though the bootstrap still
reads a non-trivial ~4% intraday P_ruin there (resampling explores orderings worse than what
actually happened). **$150,000, not $100,000, is the better-supported minimum operating capital
for Product A** once intraday (not just end-of-day) risk is accounted for.

## Product B-NQ (`SolarWaveOneContractNQ_v5`)

| capital | J (mixture) | J_worst (Γ-minimax) | CE_g (ann.) | P_ruin |
|---:|---:|---:|---:|---:|
| $50,000 | −1.3374 | −1.3521 | 0.0304 | 100% |
| $100,000 | −1.1502 | −1.2134 | 0.1453 | 94.7% |
| $150,000 | −0.6824 | −0.7998 | 0.2203 | 66.0% |
| $200,000 | −0.1923 | −0.3388 | 0.2376 | 31.4% |
| **$300,000** | **+0.1306** | +0.0745 | 0.1953 | 4.7% |
| $500,000 | +0.1226 | +0.1204 | 0.1239 | 0.1% |

**Product B-NQ needs materially more capital than Product A to reach positive owner-utility** —
its certified EOD maxDD ($59,717.44) is roughly 3.5× Product A's, so J only turns positive around
**$300,000**, not $100k–$150k. This directly reproduces and extends O2's original capital-
mismatch finding (`runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md`): quoting a single-capital
owner-utility figure for Product B-NQ without stating this is meaningless.

## Product B-MNQ (`SolarWaveOneContractMNQ_v5`)

| capital | J (mixture) | CE_g (ann.) | P_ruin |
|---:|---:|---:|---:|
| $50,000 | +0.1150 | 0.1168 | 0.13% |
| $75,000 | +0.0795 | 0.0795 | ~0% |
| $100,000 | +0.0602 | 0.0602 | ~0% |
| $150,000–$500,000 | +0.012 to +0.041 | declining | ~0% |

**Product B-MNQ is positive and low-ruin at every grid point tested**, including the thinnest
($50k) — its own maxDD ($6,050.70 certified) is small enough relative to any of these capital
levels that ruin risk never materially binds. J declines monotonically past $50k as CE_g falls
with progressively lower effective leverage — **$50,000 is the capital-efficient operating point
for Product B-MNQ specifically**, the opposite pattern from Product B-NQ.

## Cross-object comparison caveat (repeated deliberately)

**Do not compare J/CE_g/P_ruin figures across Product A, Product B-NQ, and Product B-MNQ as if
picking "the best" from one table.** These are three different products with three different risk
scales and three different natural capital footprints — the point of this document is to show
each object's OWN capital-appropriate operating range, not to rank them against each other at one
shared capital level (that comparison is exactly the artifact O2 first exposed for Product B-NQ).
A/B portfolio-level capital efficiency is a separate question, addressed in `PORT01_AB_PORTFOLIO_
SYNTHESIS` (zero drawdown-diversification benefit found — see that run for detail) and not
re-derived here.

## Alternative capital-normalization disagreement (disclosed, not resolved)

`runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/REPORT.md` §2.4 found that funding Product A at its own
single-path maxDD/25% (~$68k) rather than the shared $50k–$500k grid gives J≈−0.53 to −0.54 —
deeply negative at that thin a capital level, for the SAME object shown positive at $150k above.
This is not a contradiction: it demonstrates that a single historical maxDD is a noisy estimate of
the capital a 25%-drawdown-budget rule would actually imply (the bootstrapped tail is routinely
worse than any one realized path — `research/system_master/DRAWDOWN_FRONTIER.md`'s own standing
finding). **The $50k–$500k shared-grid table above, not a single-maxDD-derived capital figure, is
the more defensible read of "how much capital does this object need."**

## Source data (reproduce)

`runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/out/part2_capital_frontier.csv` (Product A, CONTROL
row), `part2_context_productB_frontier.csv` (Product B-NQ/MNQ), `part2_alt_normalization_
equalDDfrac.csv` (the alternative normalization). Reproduce script:
`runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/src/02_capital_frontier.py`.
