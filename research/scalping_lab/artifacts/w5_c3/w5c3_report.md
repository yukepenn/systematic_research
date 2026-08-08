# W5-C3 — FSS-3 failed-opposite-probe state machine: readout

**Spec:** `research/scalping_lab/specs/W5_programs_wave.md` section C3 (frozen before readout).
**Code:** `research/scalping_lab/src/python/w5_c3_failedprobe.py`
**Data:** 37 L2 discovery sessions (s20250814 -> s20260520), sechilo + grid1s,
1s clock, RTH, quote-alive. Seed 20260808, 1000 session-bootstrap reps (day-clustered),
C1 = 2.872t, C2 = 4.872t RT.

## Verdict: KILL — 0 / 36 configs pass; uniformly negative plateau; negative lift everywhere

Frozen pass rule: net C1 > 0 AND CI_lo > -0.5t. No config comes close: the best cell in the
entire (ctx x probe x dir x bracket) grid is ctx=24, P=6, long
+24/-8 at net C1 = -2.950t with CI [-3.316, -2.579] —
its CI upper bound is more than 2.5t below zero. The plateau view is flat and deeply negative
(net C1 range -3.702 to -2.950t across all 36 cells), so this is a clean
family-level kill, not a boundary case. Lift vs the unconditional census excursion surface is
NEGATIVE in every cell (range -2.17 to -0.41 pp): conditioning on
"context + failed opposite probe" selects entry seconds whose target-first odds are slightly
WORSE than picking any RTH second unconditionally.

## Frozen state machine (implemented exactly; LONG side shown, SHORT symmetric sign-flipped)

1. **Context** (decision seconds only = RTH & quote-alive): ret120 = mid(t) - mid(t-120) >= CTX,
   CTX in (16 primary; 12, 24 neighbors) ticks.
2. **Probe**: PH = running max of mid from the context second t0; probe triggers at the first
   second t1 in (t0, t0+30] with PH - mid >= P, P in (6 primary; 4, 8). PH frozen at t1;
   probe-low L = mid(t1); depth = PH - L. No probe within 30s -> resume scan at t0+31.
3. **Failure** (window (t1, t1+30], on mid_last): undercut mid < L - 2t cancels (the probe
   *succeeded*); undercuts <= 2t are tolerated without updating L; recovery mid >= L + 0.5*depth
   -> probe **failed** -> market entry LONG at that second's mid (delay 0). A crossing on a dead
   second kills the setup (no chase). Neither within 30s -> setup expires.
4. **Brackets** (24,8), (32,10) on mid_high/mid_low, same-second both-crossed -> adverse
   (conservative); cap 300s -> exit at mid; cooldown 60s after each trade; sequential;
   one trade per probe (holds by construction).

Interpretation choices (documented pre-run in the code header, house conventions from W4-A):
state machine runs on mid_last only; mid_high/mid_low reserved for barrier resolution; entries
only on decision seconds; cooldown applies after trades only.

## Results — all 36 configs

| ctx | P | dir | brk | n_ctx | n_probe | n_cancel | epi | epi/day | days | P(tgt) | P(unc) | lift(pp) | netC1 | 95% CI (C1) | netC2 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 6 | long **\*** | +24/-8 | 10224 | 9978 | 5420 | 4551 | 126.4 | 36 | 0.2407 | 0.2525 | -1.18 | -3.160 | [-3.549, -2.755] | -5.160 | fail |
| 16 | 6 | long **\*** | +32/-10 | 9697 | 9459 | 5144 | 4309 | 119.7 | 36 | 0.2271 | 0.2361 | -0.90 | -3.279 | [-3.822, -2.746] | -5.279 | fail |
| 16 | 6 | short **\*** | +24/-8 | 10170 | 10022 | 5617 | 4401 | 122.2 | 36 | 0.2377 | 0.2488 | -1.11 | -3.263 | [-3.773, -2.775] | -5.263 | fail |
| 16 | 6 | short **\*** | +32/-10 | 9725 | 9583 | 5361 | 4218 | 117.2 | 36 | 0.2238 | 0.2328 | -0.90 | -3.439 | [-4.097, -2.773] | -5.439 | fail |
| 16 | 4 | long | +24/-8 | 10110 | 10066 | 5093 | 4972 | 138.1 | 36 | 0.2379 | 0.2525 | -1.46 | -3.247 | [-3.630, -2.879] | -5.247 | fail |
| 16 | 4 | long | +32/-10 | 9581 | 9540 | 4875 | 4663 | 129.5 | 36 | 0.2280 | 0.2361 | -0.81 | -3.219 | [-3.690, -2.811] | -5.219 | fail |
| 16 | 4 | short | +24/-8 | 10054 | 10031 | 5252 | 4776 | 132.7 | 36 | 0.2366 | 0.2488 | -1.22 | -3.293 | [-3.713, -2.897] | -5.293 | fail |
| 16 | 4 | short | +32/-10 | 9569 | 9545 | 5002 | 4541 | 126.1 | 36 | 0.2281 | 0.2328 | -0.47 | -3.255 | [-3.789, -2.754] | -5.255 | fail |
| 16 | 8 | long | +24/-8 | 10343 | 9633 | 5546 | 4080 | 113.3 | 36 | 0.2348 | 0.2525 | -1.77 | -3.350 | [-3.848, -2.797] | -5.350 | fail |
| 16 | 8 | long | +32/-10 | 9859 | 9190 | 5294 | 3890 | 108.1 | 36 | 0.2253 | 0.2361 | -1.08 | -3.360 | [-4.050, -2.700] | -5.360 | fail |
| 16 | 8 | short | +24/-8 | 10141 | 9662 | 5616 | 4043 | 112.3 | 36 | 0.2365 | 0.2488 | -1.23 | -3.305 | [-3.814, -2.876] | -5.305 | fail |
| 16 | 8 | short | +32/-10 | 9763 | 9308 | 5423 | 3882 | 107.8 | 36 | 0.2245 | 0.2328 | -0.83 | -3.429 | [-4.150, -2.725] | -5.429 | fail |
| 12 | 6 | long | +24/-8 | 10911 | 10593 | 5776 | 4809 | 133.6 | 36 | 0.2451 | 0.2525 | -0.74 | -3.023 | [-3.427, -2.626] | -5.023 | fail |
| 12 | 6 | long | +32/-10 | 10279 | 9976 | 5419 | 4549 | 126.4 | 36 | 0.2303 | 0.2361 | -0.58 | -3.131 | [-3.694, -2.623] | -5.131 | fail |
| 12 | 6 | short | +24/-8 | 10867 | 10656 | 5979 | 4666 | 129.6 | 36 | 0.2383 | 0.2488 | -1.05 | -3.239 | [-3.706, -2.771] | -5.239 | fail |
| 12 | 6 | short | +32/-10 | 10333 | 10136 | 5661 | 4464 | 124.0 | 36 | 0.2249 | 0.2328 | -0.79 | -3.389 | [-4.033, -2.740] | -5.389 | fail |
| 12 | 4 | long | +24/-8 | 10724 | 10666 | 5392 | 5271 | 146.4 | 36 | 0.2388 | 0.2525 | -1.37 | -3.219 | [-3.632, -2.838] | -5.219 | fail |
| 12 | 4 | long | +32/-10 | 10127 | 10070 | 5137 | 4929 | 136.9 | 36 | 0.2307 | 0.2361 | -0.54 | -3.116 | [-3.581, -2.700] | -5.116 | fail |
| 12 | 4 | short | +24/-8 | 10684 | 10634 | 5533 | 5096 | 141.6 | 36 | 0.2395 | 0.2488 | -0.93 | -3.197 | [-3.584, -2.855] | -5.197 | fail |
| 12 | 4 | short | +32/-10 | 10080 | 10034 | 5201 | 4830 | 134.2 | 36 | 0.2265 | 0.2328 | -0.63 | -3.321 | [-3.891, -2.816] | -5.321 | fail |
| 12 | 8 | long | +24/-8 | 11110 | 10263 | 5930 | 4321 | 120.0 | 36 | 0.2378 | 0.2525 | -1.47 | -3.257 | [-3.748, -2.777] | -5.257 | fail |
| 12 | 8 | long | +32/-10 | 10581 | 9794 | 5666 | 4119 | 114.4 | 36 | 0.2266 | 0.2361 | -0.95 | -3.295 | [-3.949, -2.719] | -5.295 | fail |
| 12 | 8 | short | +24/-8 | 10889 | 10291 | 6016 | 4264 | 118.4 | 36 | 0.2372 | 0.2488 | -1.16 | -3.281 | [-3.740, -2.883] | -5.281 | fail |
| 12 | 8 | short | +32/-10 | 10439 | 9867 | 5772 | 4084 | 113.4 | 36 | 0.2225 | 0.2328 | -1.03 | -3.512 | [-4.249, -2.810] | -5.512 | fail |
| 24 | 6 | long | +24/-8 | 8901 | 8733 | 4779 | 3951 | 109.8 | 36 | 0.2475 | 0.2525 | -0.50 | -2.950 | [-3.316, -2.579] | -4.950 | fail |
| 24 | 6 | long | +32/-10 | 8520 | 8357 | 4577 | 3777 | 104.9 | 36 | 0.2290 | 0.2361 | -0.71 | -3.226 | [-3.693, -2.734] | -5.226 | fail |
| 24 | 6 | short | +24/-8 | 8846 | 8737 | 4897 | 3837 | 106.6 | 36 | 0.2365 | 0.2488 | -1.23 | -3.302 | [-3.795, -2.855] | -5.302 | fail |
| 24 | 6 | short | +32/-10 | 8478 | 8367 | 4668 | 3696 | 102.7 | 36 | 0.2246 | 0.2328 | -0.82 | -3.427 | [-3.985, -2.961] | -5.427 | fail |
| 24 | 4 | long | +24/-8 | 8786 | 8765 | 4444 | 4319 | 120.0 | 36 | 0.2405 | 0.2525 | -1.20 | -3.170 | [-3.511, -2.819] | -5.170 | fail |
| 24 | 4 | long | +32/-10 | 8353 | 8334 | 4230 | 4101 | 113.9 | 36 | 0.2243 | 0.2361 | -1.18 | -3.401 | [-3.904, -2.905] | -5.401 | fail |
| 24 | 4 | short | +24/-8 | 8751 | 8738 | 4586 | 4150 | 115.3 | 36 | 0.2364 | 0.2488 | -1.24 | -3.301 | [-3.774, -2.837] | -5.301 | fail |
| 24 | 4 | short | +32/-10 | 8393 | 8379 | 4395 | 3983 | 110.6 | 36 | 0.2287 | 0.2328 | -0.41 | -3.242 | [-3.794, -2.734] | -5.242 | fail |
| 24 | 8 | long | +24/-8 | 8889 | 8393 | 4801 | 3587 | 99.6 | 36 | 0.2308 | 0.2525 | -2.17 | -3.475 | [-3.947, -3.003] | -5.475 | fail |
| 24 | 8 | long | +32/-10 | 8610 | 8128 | 4675 | 3449 | 95.8 | 36 | 0.2177 | 0.2361 | -1.84 | -3.702 | [-4.323, -3.108] | -5.702 | fail |
| 24 | 8 | short | +24/-8 | 8740 | 8427 | 4864 | 3559 | 98.9 | 36 | 0.2333 | 0.2488 | -1.55 | -3.408 | [-3.930, -2.945] | -5.408 | fail |
| 24 | 8 | short | +32/-10 | 8473 | 8175 | 4747 | 3424 | 95.1 | 36 | 0.2249 | 0.2328 | -0.79 | -3.415 | [-4.074, -2.820] | -5.415 | fail |

`*` = primary (ctx=16, P=6). CI = 95% session bootstrap (resample sessions, episode-weighted),
seed 20260808, 1000 reps. P(unc) and lift from `artifacts/census/excursion_surface.csv`
(unconditional P(target-first), same A/B/dir). One session (s20250902) produced zero episodes
in the primary long +24/-8 config; every config realized episodes on 36 unique days.

## Primary configs (ctx=16, P=6)

- long +24/-8: 4551 episodes, P(tgt) 0.2407 vs 0.2525 unconditional, net C1 -3.160t, CI [-3.549, -2.755], net C2 -5.160t
- long +32/-10: 4309 episodes, P(tgt) 0.2271 vs 0.2361 unconditional, net C1 -3.279t, CI [-3.822, -2.746], net C2 -5.279t
- short +24/-8: 4401 episodes, P(tgt) 0.2377 vs 0.2488 unconditional, net C1 -3.263t, CI [-3.773, -2.775], net C2 -5.263t
- short +32/-10: 4218 episodes, P(tgt) 0.2238 vs 0.2328 unconditional, net C1 -3.439t, CI [-4.097, -2.773], net C2 -5.439t

## Why it fails (mechanism, from the state-machine counters)

- The setup is near-vacuous: 97.3% of context detections produce a probe
  within 30s (a ~6t counter-move after a 16t/120s advance is ordinary 1s noise), and
  54.9% of probes cancel on the >2t undercut. What survives still fires
  ~96-146 times per day per config — this is an unconditional noise-fade, not a selective state.
- The entry is structurally late: by definition it buys only after price has already recovered
  >= 50% of the probe depth, i.e. at a locally rich price seconds after a local low — the
  subsequent (A, B) barrier race starts from adverse territory. Gross expectancy sits near
  -0.3t before costs in most cells (net C1 ~ -3.2t = gross ~ -0.3t minus 2.872t), and the
  conditional P(target) is below the unconditional surface in all 36 cells.
- Neighbor structure confirms no hidden ridge: tightening/loosening context (12/24) or probe
  (4/8) moves net C1 by well under 1t in either direction; long/short symmetry holds.

## Registry / campaign implications

- FSS-3 joins the falsified list: "failed opposite probe" carries no exploitable continuation
  information at 1s/RTH granularity on NQ under C1 costs. Per Amendment 6 section 7C no variant
  of this family should be retuned; any future probe-failure idea must state a mechanical
  distinction from this state machine.
- Consistent with the W5 family picture: conditioning states built from short-horizon
  price-path grammar alone do not clear the ~3t cost floor; the census C1 gap for 24/8
  (gap_c1 = 0.0873) remains unbridged by this family.

## Artifacts

- `w5c3_by_session.csv` — 1,332 rows (37 sessions x 36 configs), per-session counters and gross.
- `w5c3_pooled.csv` — 36 pooled config rows (source of every number above).
- `w5c3_stdout.txt` — full run stdout (pooled table + plateau view).
