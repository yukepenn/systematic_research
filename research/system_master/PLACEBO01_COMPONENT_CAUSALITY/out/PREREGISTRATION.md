# PLACEBO01 sizing placebo -- PREREGISTRATION

Written before any data load or placebo randomization. See `preregistration.json` for
the machine-readable version (identical content).

- N randomizations: **500**
- Seed family: **seed_i = 20260810 + i, for i in range(0, 500)**
- Null construction: within-stratum permutation of |target_exposure_A| (direction x session_phase x vol tercile x Solar-conviction tercile); direction/timing and the global size histogram are preserved exactly.
- Metrics: PnL/contract, PnL/exposure-hour, marginal-exposure-value WLS gradient.
- Comparison: empirical percentile of the real system within its own null distribution, for each metric separately.
- Correctness gate: loop_exec on the real target_exposure_A path must reproduce the certified canonical net (177924.4) to within $1 and be bit-identical to U0's own bar_pnl_A_dollars column.
