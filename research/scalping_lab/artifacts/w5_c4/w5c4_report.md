# W5-C4 — FSS-6 compression->expansion + FSS-7 velocity/low-retracement — readout

- Spec: `research/scalping_lab/specs/W5_programs_wave.md` section C4 (frozen before readout,
  2026-08-08). Thresholds frozen; nothing tuned.
- Code: `research/scalping_lab/src/python/w5_c4_compression.py`;
  verification: `src/python/w5_c4_verify.py`. Seed 20260808, 1000 bootstrap reps,
  session (day-clustered) resampling, episode-count weighted.
- Data: 37 L2 discovery sessions, sechilo+grid1s merge, RTH [09:30, 16:00) ET,
  quote-alive (trailing-60s bid_upd+ask_upd > 0) decision seconds, sequential episode
  simulation PER FAMILY (long+short share one timeline per family x bracket),
  conservative same-second-both-crossed -> adverse, cap 300s -> MTM, cooldown 60s,
  C1 = 2.872t RT, C2 = 4.872t.
- Artifacts: `w5c4_by_session.csv` (296 rows = 37 sessions x 8 configs),
  `w5c4_pooled.csv` (8 configs), `w5c4_baseline_echo.csv` (census surface rows used),
  `w5c4_stdout.txt` (full run log), `w5c4_verify.txt` (independent verification pass;
  every number quoted below appears in these files).
- Note: s20250902 has 23,400 RTH rows but 0 quote-alive seconds (dead L2 RTH day),
  so the effective discovery set is 36 active sessions — consistent with days=36 in
  the W4 readouts. Total decision seconds pooled: 818,965 (w5c4_verify.txt).

## VERDICT: BOTH FAMILIES KILLED — 0 / 8 configs pass the frozen rule

- **FSS-6: KILL by structural non-occurrence (no-fire).** The compression
  precondition (trailing-120s hi-lo range <= 8t) covers **336 of 818,965** decision
  seconds (**0.041%**); only **5** of those also have 10s |ret| >= 6t, and all 5 break
  the boundary and fire — **2 long + 3 short trigger seconds in 37 sessions, every one
  of them on s20250901 (the 2025 Labor Day holiday session)**. 5 episodes per bracket
  (10 total), 0 targets. Net C1: -4.372 to -6.122 t/trade; the bootstrap CI is
  degenerate (single-session support: CI_lo = CI_hi = point estimate). The frozen pass
  rule fails (net C1 < 0), but the substantive finding is that this setup effectively
  does not exist in the current high-vol NQ regime — there is no plateau to assess and
  no support on any regular session.
- **FSS-7: DEFINITIVE KILL (robust, not fragile).** Massive support — **18,962
  episodes** over 36 days (124.00–138.25 epi/day per cell) — and essentially **zero
  lift over the unconditional excursion surface**: lift = **-0.79 to +0.53 pp**
  across the 4 (bracket x dir) cells. P(target) 0.2347–0.2578 vs unconditional
  0.2328–0.2525; the C1 break-even gap barely moves (family gap 6.95–9.88 pp remaining
  vs 7.03–9.09 pp unconditional). Net C1 range **[-3.156, -2.604] t/trade** with all
  bootstrap CI **upper** bounds <= **-2.121 t**. The velocity/low-retracement state
  carries no incremental information about barrier outcomes: conditioning on "the
  market is already moving fast and hasn't retraced" (~16% of all RTH quote-alive
  seconds trigger: 136,885 long / 131,730 short trigger seconds) reproduces the
  unconditional surface at full cost.

Plateau logic (family verdict = plateau): FSS-7's entire 4-cell surface is uniformly
and significantly negative — a robust kill with no isolated positives to flag as
FRAGILE. FSS-6 has no plateau (no support). No neighbor selection was performed.

## FACT — pooled results (w5c4_stdout.txt / w5c4_pooled.csv)

```
=== W5-C4 pooled — sequential per (family, bracket), 60s cooldown, cap 300s ===
  fam   A   B   dir |   trig   epi    e/d days |  P(tgt)  cap   P_unc lift_pp |   netC1   CI_lo   CI_hi |   netC2 |  BE_C1    gapF PASS
 FSS6  24   8  long |      2     2   2.00    1 |  0.0000    1  0.2525  -25.25 |  -5.122  -5.122  -5.122 |  -7.122 | 0.3397 +0.3397 fail
 FSS6  24   8 short |      3     3   3.00    1 |  0.0000    2  0.2488  -24.88 |  -4.372  -4.372  -4.372 |  -6.372 | 0.3397 +0.3397 fail
 FSS6  32  10  long |      2     2   2.00    1 |  0.0000    1  0.2361  -23.61 |  -6.122  -6.122  -6.122 |  -8.122 | 0.3065 +0.3065 fail
 FSS6  32  10 short |      3     3   3.00    1 |  0.0000    2  0.2328  -23.28 |  -5.039  -5.039  -5.039 |  -7.039 | 0.3065 +0.3065 fail
 FSS7  24   8  long | 136885  4977 138.25   36 |  0.2578    5  0.2525   +0.53 |  -2.604  -3.119  -2.121 |  -4.604 | 0.3397 +0.0819 fail
 FSS7  24   8 short | 131730  4920 136.67   36 |  0.2409    5  0.2488   -0.79 |  -3.156  -3.536  -2.814 |  -5.156 | 0.3397 +0.0988 fail
 FSS7  32  10  long | 136885  4601 127.81   36 |  0.2370   31  0.2361   +0.09 |  -2.837  -3.345  -2.356 |  -4.837 | 0.3065 +0.0695 fail
 FSS7  32  10 short | 131730  4464 124.00   36 |  0.2347   12  0.2328   +0.19 |  -2.987  -3.566  -2.486 |  -4.987 | 0.3065 +0.0718 fail
(P_unc/BE_C1 from canonical census surface; lift_pp = 100*(P(tgt)-P_unc); gapF = BE_C1 - P(tgt), positive = still below break-even; PASS = net_c1>0 AND CI_lo_c1>-0.5t; CI_C2 = CI_C1 - 2.000t exactly)
```

Unconditional baseline = canonical census surface (`artifacts/census/
excursion_surface.csv`, 30s RTH clock, same 37 sessions), echoed to
`w5c4_baseline_echo.csv`: (24,8) long/short P(tgt) 0.2525/0.2488 (gap_c1
0.0873/0.0909); (32,10) 0.2361/0.2328 (gap_c1 0.0703/0.0737).

## FACT — the FSS-6 funnel and the 5 events (w5c4_verify.txt)

Funnel over all decision seconds: 818,965 -> compression(range<=8t) 336 (0.041%) ->
compression AND |ret10|>=6t: 5 -> full trigger (boundary break): 5 (2 long, 3 short).
All five on s20250901 (Labor Day), between 10:10 and 12:39 ET, with compression ranges
7.0–8.0t and ret10 from -8.0t to +9.5t. On the two brackets these produced 0 targets,
2 adverse, 3 cap exits (per-direction detail in w5c4_by_session.csv). In this sample's
volatility regime (census: median 60s forward MFE = 20t), a 120s two-sided range of
<= 8t essentially only occurs on a holiday-thinned tape.

## Verification (w5c4_verify.txt)

1. FSS-6 triggers re-derived for all 37 sessions with an independent numpy
   sliding_window_view path: **0/37** session mismatches vs the main pandas-rolling run;
   pooled trigger counts cross-check True (long 2==2, short 3==3).
2. FSS-7 independently re-simulated in pure Python (back-scan sign-flip move-start +
   slice extremes, independent sequential loop) for the two heaviest sessions
   (s20260303, s20260519), both brackets, both dirs: **8/8 cells exact match** on
   episodes, tgt/adv/cap counts, and gross ticks (MATCH=True, ALL MATCH = True).
3. Pooled CSV cross-footed from the by-session CSV: **0/8** failures (episodes, net C1,
   P(tgt), unique days, and net C2 = net C1 - 2.000t all reproduce).

## Frozen-spec interpretation choices (documented, not tuned)

- FSS-6 compression window = trailing 120s ENDING AT t-1 (shift-1, full window
  required). Including t would make a boundary break logically impossible
  (mid_last[t] <= mid_high[t] <= window max).
- FSS-6 break is strict (mid_last[t] > comp_high, resp. < comp_low) and the 10s ret
  must agree in sign with the break direction. Entry = market at mid_last[t] at the
  trigger second (delay 0, house convention).
- FSS-7 move start = first second of the current same-sign ret20 regime ("last second
  where the 20s ret sign flipped"); zero or NaN ret20 resets both regimes. Running
  extreme, base, retrace, displacement all on mid_last (hi/lo reserved for barrier
  evaluation, house convention); displacement > 0 required.
- Sequential per family: long and short share one timeline per (family, bracket); an
  open episode blocks all entries; the 60s cooldown applies to both directions.
  Long/short triggers are mutually exclusive by construction in both families.

## Consequences

- FSS-6 and FSS-7 close out the FSS ladder branches allocated to C4: compression->
  expansion is unavailable in this regime (support ~= 0), and velocity/low-retracement
  continuation is informationless vs the unconditional surface. Neither warrants a
  neighbor wave or a passive-entry variant (FSS-7's deficit, 2.6–3.2t, exceeds the
  1.0t passive cost saving by >1.1t even at the best CI upper bound, -2.121t; FSS-6
  has nothing to enter).
- Registry: two family rows (FSS-6 KILL/no-fire; FSS-7 KILL/robust) from the wave's
  S14–S21 allocation; sequence numbers assigned at wave close by the orchestrator.
