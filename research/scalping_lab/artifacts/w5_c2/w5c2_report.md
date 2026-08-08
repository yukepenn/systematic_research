# W5-C2 — fast FSS-2 breakout-acceptance (15s/30s completed bars) — READOUT

Spec: `research/scalping_lab/specs/W5_programs_wave.md` §C2 (frozen before readout).
Code: `research/scalping_lab/src/python/w5_c2_fastfss2.py`. Seed 20260808, 1000 bootstrap
reps, day-clustered (session-resampled) 95% CIs. 37 L2 discovery sessions
(s20250814 → s20260520), RTH, quote-alive, conservative same-second-both-crossed →
adverse barrier, sequential episode simulation, C1 = 2.872t / C2 = 4.872t RT.
Mechanical distinction from killed 1-min S2a: 4-8x faster clock, acceptance-close
grammar (no pullback-bar requirement).

## Verdict: KILL — 0 / 16 configs pass; the whole (clock × acceptance) plateau is negative

Frozen pass rule: net C1 > 0 AND CI_lo > −0.5t. No config comes close: every one of
the 16 cells has net C1 between **−2.457t** and **−4.281t** per trade, and every 95%
CI upper bound is below zero (best CI_hi = **−0.762t**, K=30 acc=2 short 32/10). Gross
per trade (before costs) spans −1.409t to +0.415t — the family barely clears zero
gross in its best cell, so no plausible cost regime rescues it. Family verdict is a
plateau judgment: uniformly negative across both clocks, both acceptance grammars,
both brackets, both directions.

## Pooled results (from `w5c2_pooled.csv` / `w5c2_stdout.txt`)

| K | acc | dir | brk | episodes | epi/day | days | P(tgt) | BE_C1 | net C1 | CI_lo | CI_hi | net C2 | pass |
|---|-----|-----|-----|---------|---------|------|--------|-------|--------|-------|-------|--------|------|
| 15 | 1 | long | 24/8 | 816 | 22.67 | 36 | 0.2355 | 0.3397 | −3.317 | −4.029 | −2.555 | −5.317 | fail |
| 15 | 1 | long | 32/10 | 802 | 22.28 | 36 | 0.2156 | 0.3065 | −3.745 | −4.949 | −2.710 | −5.745 | fail |
| 15 | 1 | short | 24/8 | 679 | 18.86 | 36 | 0.2257 | 0.3397 | −3.656 | −4.437 | −2.840 | −5.656 | fail |
| 15 | 1 | short | 32/10 | 669 | 18.58 | 36 | 0.2162 | 0.3065 | −3.725 | −4.826 | −2.612 | −5.725 | fail |
| 15 | 2 | long | 24/8 | 615 | 17.08 | 36 | 0.2622 | 0.3397 | −2.457 | −3.552 | −1.307 | −4.457 | fail |
| 15 | 2 | long | 32/10 | 608 | 16.89 | 36 | 0.2292 | 0.3065 | −3.154 | −4.359 | −1.902 | −5.154 | fail |
| 15 | 2 | short | 24/8 | 505 | 14.03 | 36 | 0.2321 | 0.3397 | −3.451 | −4.567 | −2.448 | −5.451 | fail |
| 15 | 2 | short | 32/10 | 503 | 13.97 | 36 | 0.2008 | 0.3065 | −4.281 | −5.469 | −3.119 | −6.281 | fail |
| 30 | 1 | long | 24/8 | 438 | 12.17 | 36 | 0.2506 | 0.3397 | −2.777 | −3.842 | −1.631 | −4.777 | fail |
| 30 | 1 | long | 32/10 | 435 | 12.08 | 36 | 0.2297 | 0.3065 | −3.144 | −4.483 | −1.549 | −5.144 | fail |
| 30 | 1 | short | 24/8 | 347 | 9.64 | 36 | 0.2261 | 0.3397 | −3.627 | −4.919 | −2.314 | −5.627 | fail |
| 30 | 1 | short | 32/10 | 346 | 9.61 | 36 | 0.2122 | 0.3065 | −3.947 | −5.671 | −2.348 | −5.947 | fail |
| 30 | 2 | long | 24/8 | 314 | 8.72 | 36 | 0.2540 | 0.3397 | −2.683 | −4.125 | −1.137 | −4.683 | fail |
| 30 | 2 | long | 32/10 | 314 | 8.72 | 36 | 0.2355 | 0.3065 | −2.918 | −4.611 | −1.322 | −4.918 | fail |
| 30 | 2 | short | 24/8 | 254 | 7.06 | 36 | 0.2362 | 0.3397 | −3.313 | −4.946 | −1.505 | −5.313 | fail |
| 30 | 2 | short | 32/10 | 253 | 7.03 | 36 | 0.2262 | 0.3065 | −3.376 | −5.754 | −0.762 | −5.376 | fail |

(BE_C1 = target probability needed to break even at C1: (B+C1)/(A+B). CI on net C1;
net C2 CI = net C1 CI − 2.000t exactly, since costs are constants. 36 unique days:
s20250902 produced zero episodes in every config. 7,898 episodes total across configs.)

## Reading

- P(target) sits 8-13pp BELOW break-even everywhere (0.20-0.26 achieved vs 0.34/0.31
  needed). The acceptance-close grammar does not select continuation: after a
  20-bar-high breakout close with CL ≥ 0.7 plus 1-2 accepting closes plus a further
  1s-mid push through the acceptance high +1t, the move is spent — asymmetric 3:1
  brackets then bleed on the 8t/10t stop.
- Direction of the internal gradients (reported, never selected on): acc=2 ≥ acc=1
  and K=30 ≥ K=15 in most cells — more confirmation loses less — but even the most
  filtered corner is ≈ −2.5t/trade at C1. The gradient points toward "trade never",
  not toward a tunable edge.
- Funnel: 61.6-77.3% of completed acceptances produce an entry within 120s; attrition
  is dominated by no-cross cancels (~25-35%), dead-second kills are negligible (0-3
  per config). So the loss is not an artifact of a starving entry gate — the family
  trades 7-23 times/day and loses steadily.
- This is the same failure shape as killed 1-min S2a and W4-A FSS-1 rebreak: NQ
  breakout-continuation at scalp horizons is adversely selected at every clock now
  tested (60s → 30s → 15s bars). The 4-8x clock speed-up and the grammar change moved
  nothing.

## Frozen-interpretation notes (decided before readout, documented in code header)

- Bars wall-clock-aligned (bar id = floor(tod/K)); only completed K-second bars are
  eligible as breakout or acceptance bars; broken level = strict max of the prior 20
  bar highs (full 20-bar history required); zero-range bars skipped.
- Breakout AND each acceptance bar must close on a decision second (RTH & quote-alive).
- Acceptance-phase high = max mid-bar high over the acceptance bars only; entry
  trigger = 1s mid ≥ AH + 1t (the 1t buffer supplies crossing strictness), scanned
  strictly after the acceptance close, ≤ 120s; crossing on a dead second kills the
  setup (house W4-A convention); market entry at the crossing second's mid, delay 0;
  barriers from entry+1s.
- Sequential + one-trade-per-breakout via a 1s busy pointer (cancel points and
  resolve+60s cooldown advance it; breakout bars closing before it are skipped).

## Artifacts

- `w5c2_by_session.csv` — per-session × config funnel counts and gross sums
- `w5c2_pooled.csv` — the 16-config pooled table (source of every number above)
- `w5c2_stdout.txt` — full run log (37 sessions, pooled tables, funnel, plateau view)
