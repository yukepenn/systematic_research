# LEVERAGE_ROBUSTNESS — DD-constrained growth under long-dependence resampling (SMV2F)

_2026-08-08 audit. $100k base, compounded daily, 2,000 paths/method, seed 20260808.
Methods: moving blocks L=5/20/60/120, stationary(60), quarter-block, year-block.
f* = max exposure multiple with P(maxDD > threshold) ≤ 5%. Code `runs/SMV2F_LEVERAGE_ROBUST/`._

## Headline correction (supersedes SM09's single-method claim)

The old "22.5%/yr at P(DD>25%)≤5%" for PORT_TILT_532 came from the L5 bootstrap alone.
Under the frozen honesty rule (headline = WORST method):

| object | f* range (P(DD>25%)≤5%) | median growth range | **honest headline (worst)** |
|---|---|---|---|
| Solar E10 | 0.32 – 0.48 | 8.0% – 11.7% | **8.0%/yr** |
| Day-only tilt+BMOM (C) | 0.38 – 0.62 | 19.5% – 32.0% | **19.5%/yr** |
| PORT_TILT_532 (E) | 0.46 – 0.77 | 21.4% – 35.5% | **21.4%/yr** |
| OneLot 1 NQ (G) | 0.25 – 0.37 | 16.3% – 24.3% | **16.3%/yr** |

- Unexpected direction: **L5 is the CONSERVATIVE method here, not the optimistic one.**
  Longer blocks (which preserve the real curves' loss→recovery alternation) give
  HIGHER sustainable exposure; free reshuffling at L5 manufactures loss-streak paths
  the actual dependence structure resists. The old claims were therefore near the
  bottom of the model-risk band, not the top — they survive with a small trim
  (22.5% → 21.4% worst-method).
- The ORDERING is stable across all seven methods: PORT > day-only C > OneLot NQ >
  Solar — every method, every threshold. The portfolio-beats-components conclusion is
  method-robust (this was the actual question; answered YES).
- Sensitivity: quarter/year blocks have only 18/5 distinct blocks on dev — wide CIs;
  they agree with L60-120 anyway.
- These are dev-window, current-regime numbers on $100k; regime death (SM06) is not
  in any resampling scheme. Leverage is never alpha; this table only prices DD risk.
