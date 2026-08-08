# W4-C — FSS-5: level sweep -> reclaim (Zone F/S) — readout

Date: 2026-08-08. Spec: `specs/W4_alpha_wave1.md` section "W4-C" (frozen before readout).
Code: `src/python/w4c_fss5.py`. Seed 20260808, 1000 session-bootstrap reps (day-clustered).
Data: 37 L2 discovery sessions, sechilo+grid1s merge, decisions on RTH & quote-alive
seconds only, conservative same-second-both-crossed->adverse barrier, sequential episode
simulation, C1=2.872t / C2=4.872t RT.

## VERDICT: KILL (definitive B). 0 of 144 configs pass the frozen rule.

Pass rule (frozen, as W4-A): net C1 > 0 AND CI lower bound > -0.5t.
FACT: 144 configs simulated (4 levels x pierce {1,2,4}t x window {30,60,120}s x
brackets {(16,6),(24,8)} x {reclaim, continuation}). Passing configs: reclaim 0/72,
continuation 0/72. Zero configs have net C1 > 0; zero configs have CI_lo > -0.5t.
Plateau logic is moot — there is no passing config to be an island or a plateau.

## Primary configs (pierce=2t, window=60s) — FACT (w4c_extra_stats.txt / w4c_stdout.txt)

RECLAIM side (spec primary):

| level | dir | bracket | sweeps | trades | epi/d | days | P(tgt) | BE_C1 | net C1 [95% CI] | net C2 |
|-------|-----|---------|--------|--------|-------|------|--------|-------|-----------------|--------|
| ONL | long | +16/-6 | 2443 | 168 | 4.54 | 18 | 0.3036 | 0.4033 | -2.193 [-3.445,-1.021] | -4.193 |
| ONL | long | +24/-8 | 2437 | 165 | 4.46 | 18 | 0.2727 | 0.3397 | -2.145 [-3.550,-0.669] | -4.145 |
| OR15L | long | +16/-6 | 3533 | 250 | 6.76 | 23 | 0.2800 | 0.4033 | -2.712 [-3.553,-1.882] | -4.712 |
| OR15L | long | +24/-8 | 3523 | 247 | 6.68 | 23 | 0.2348 | 0.3397 | -3.358 [-4.499,-2.229] | -5.358 |
| ONH | short | +16/-6 | 4437 | 296 | 8.00 | 24 | 0.2804 | 0.4033 | -2.703 [-3.839,-1.759] | -4.703 |
| ONH | short | +24/-8 | 4430 | 294 | 7.95 | 24 | 0.2687 | 0.3397 | -2.273 [-3.282,-1.061] | -4.273 |
| OR15H | short | +16/-6 | 5671 | 295 | 7.97 | 26 | 0.2136 | 0.4033 | -4.174 [-4.999,-3.282] | -6.174 |
| OR15H | short | +24/-8 | 5663 | 287 | 7.76 | 26 | 0.1958 | 0.3397 | -4.609 [-6.005,-3.197] | -6.609 |

Primary reclaim net C1 range: -4.609 to -2.145 t/trade; max CI upper bound -0.669
(every primary reclaim CI sits entirely below zero). Cap-outcome trades: 0-1 per config.

CONTINUATION mirror (frozen diagnostic — enter sweep direction on failure to reclaim):

| level | dir | bracket | trades | epi/d | days | P(tgt) | net C1 [95% CI] | net C2 |
|-------|-----|---------|--------|-------|------|--------|-----------------|--------|
| ONL | short | +16/-6 | 1133 | 30.62 | 15 | 0.2665 | -3.008 [-3.684,-2.228] | -5.008 |
| ONL | short | +24/-8 | 1088 | 29.41 | 15 | 0.2647 | -2.401 [-3.144,-1.599] | -4.401 |
| OR15L | short | +16/-6 | 1638 | 44.27 | 19 | 0.2772 | -2.774 [-3.275,-2.234] | -4.774 |
| OR15L | short | +24/-8 | 1574 | 42.54 | 19 | 0.2548 | -2.720 [-3.443,-2.147] | -4.720 |
| ONH | long | +16/-6 | 1958 | 52.92 | 20 | 0.2764 | -2.790 [-3.162,-2.406] | -4.790 |
| ONH | long | +24/-8 | 1816 | 49.08 | 20 | 0.2452 | -3.008 [-3.441,-2.576] | -5.008 |
| OR15H | long | +16/-6 | 2506 | 67.73 | 25 | 0.2622 | -3.095 [-3.392,-2.747] | -5.095 |
| OR15H | long | +24/-8 | 2319 | 62.68 | 25 | 0.2409 | -3.120 [-3.483,-2.775] | -5.120 |

Primary continuation net C1 range: -3.120 to -2.401; max CI upper bound -1.599.

## Neighbors (pierce {1,4}t, window {30,120}s) — FACT

All 128 neighbor configs fail. Best config anywhere in the family:
ONL reclaim long, pierce=4t, W=120s, +24/-8: n=159, net C1 = -1.010
[-2.452, +0.610], net C2 = -3.010 — still a negative point estimate, still fail.
Max CI upper bound across all 144 configs: +0.703 (ONL reclaim pierce=4, W=30, +24/-8,
net C1 -1.010). ONL reclaim is the least-bad corner of the family; OR15H reclaim short
is the worst (net C1 ~ -4.2 to -4.6).

## What the diagnostic answered (the census/DR priors could not tell which side wins)

FACT: NEITHER side wins. At these frictions both the reclaim fade and the sweep-direction
continuation lose roughly -2.4 to -4.6 t/trade at C1, with every primary CI entirely
below zero. P(target) sits 6-16 pp below break-even on every primary config
(BE 0.4033 for +16/-6, 0.3397 for +24/-8).

FACT (episode structure): only ~5.1-7.1% of sweep episodes reclaim within 60s
(reclaim_rate column, primary configs); ~76-82% of continuation-mode episodes end in
failure-to-reclaim and produce a continuation entry. INFERENCE: an ON/OR15 level break
in this sample is overwhelmingly a pass-through, not a stop-hunt reversal — but chasing
the pass-through 60s late is also dead: the move's edge is spent before the failure is
even confirmed. This is consistent with the standing campaign finding that post-event
entries at C1 frictions bleed roughly the spread+commission with P(tgt) below barrier
break-even.

## Implementation notes (spec-ambiguity resolutions, documented not tuned)

- Re-arm "price must first move >= 8t away from the level" implemented literally as
  |mid_last - L| >= 8t on either side. Consequence (FACT, visible in trade counts):
  on sessions trending beyond a level, the continuation config re-triggers every few
  minutes (cont totals 126,099 trades vs 17,833 reclaim across all configs); trades
  concentrate on 15-26 unique days per config.
- Reclaim may occur in the sweep second itself (mid_low pierces, mid_last closes >=
  L+1t); entry at that second's close, barriers from the next second.
- Sweep detection and entry seconds both require RTH & quote-alive (dec); cooldown 60s
  from trade exit blocks new sweep episodes for that config.
- Running RTH high/low is a listed causal level in the spec but the frozen trade sets
  are exactly {ONL, OR15L} long-side and {ONH, OR15H} short-side, so it was not traded.
- All four levels defined on 37/37 sessions (w4c_levels.csv).
- Prior-day levels unavailable (non-contiguous discovery sample) — spec-documented
  limitation.

## Artifacts

- `w4c_stdout.txt` — full run log, pooled tables for all 144 configs
- `w4c_results.csv` — 5,328 per-session x config rows
- `w4c_pooled.csv` — 144 pooled config rows with CIs and pass flags
- `w4c_levels.csv` — per-session ONH/ONL/OR15H/OR15L values and window row counts
- `w4c_extra_stats.txt` — derived stats (reclaim rates, cap fractions, best config)
