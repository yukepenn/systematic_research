# W4-E — CLEAN_MOVE labels + path ordering (labels only)

- Spec: `research/scalping_lab/specs/W4_alpha_wave1.md` section W4-E (frozen before readout). No trade rule, no P&L in this family.
- Code: `research/scalping_lab/src/python/w4e_cleanmove.py`. Seed 20260808. Horizon H=60s, path over (t, t+60], per-second `mid_high`/`mid_low` scan, conservative same-second-both-crossed -> MAE-violated (not clean).
- Data: 37 discovery sechilo sessions merged with grid1s (house merge pattern); decisions on RTH & quote-alive seconds only.
- Evidence: every number below appears in `w4e_stdout.txt`, `w4e_freqmap.csv`, `w4e_pathorder_summary.csv`, `w4e_features.csv`, `w4e_clean_by_session.csv`, `w4e_pathorder_by_session.csv`, or `s20250902_exclusion_note.txt` in this directory.

## FACT — data coverage

- 37 sessions enumerated; **36 pooled**. `s20250902` is excluded by the standing quote-alive filter: its sechilo file ends 2025-09-01 23:59:59 (16,379 rows) and its RTH quote updates (bid_upd+ask_upd) = **0** (evening updates 205,651), so the session has 0 decision seconds (`s20250902_exclusion_note.txt`).
- Internal consistency check: tt-based plain label (MFE>=20 within 60s) vs census `fwd_extrema` logic, both directions, all decision seconds: **mismatches = 0** (stdout line 39).

## FACT — CLEAN(H=60s) frequency map (pooled, 36 sessions)

clean_raw/plain_raw = flagged decision seconds; episodes = refractory 60s; epi/day over 36 sessions; block mix = clean EPISODE starts per time block; cfrac = clean/plain.

| dir | M | K | clean_raw | clean_epi | epi/day | udays | plain_raw | plain_epi | cfrac_raw | cfrac_epi | b0930 | b1030 | b1200 | b1400 |
|----|----|---|-----------|-----------|---------|-------|-----------|-----------|-----------|-----------|-------|-------|-------|-------|
| up | 16 | 6 | 214132 | 10796 | 299.89 | 36 | 478330 | 11532 | 0.4477 | 0.9362 | 1952 | 2680 | 3191 | 2973 |
| up | 16 | 8 | 257176 | 10944 | 304.00 | 36 | 478330 | 11532 | 0.5377 | 0.9490 | 1976 | 2714 | 3242 | 3012 |
| up | 20 | 6 | 175261 | 9829 | 273.03 | 36 | 413152 | 10574 | 0.4242 | 0.9295 | 1865 | 2469 | 2887 | 2608 |
| up | 20 | 8 | 212183 | 9969 | 276.92 | 36 | 413152 | 10574 | 0.5136 | 0.9428 | 1893 | 2499 | 2923 | 2654 |
| up | 24 | 6 | 145846 | 8920 | 247.78 | 36 | 356918 | 9632 | 0.4086 | 0.9261 | 1790 | 2307 | 2565 | 2258 |
| up | 24 | 8 | 177290 | 9052 | 251.44 | 36 | 356918 | 9632 | 0.4967 | 0.9398 | 1817 | 2336 | 2597 | 2302 |
| up | 32 | 6 | 102836 | 7274 | 202.06 | 36 | 266289 | 7884 | 0.3862 | 0.9226 | 1622 | 1932 | 2001 | 1719 |
| up | 32 | 8 | 125669 | 7363 | 204.53 | 36 | 266289 | 7884 | 0.4719 | 0.9339 | 1643 | 1953 | 2022 | 1745 |
| dn | 16 | 6 | 212933 | 10717 | 297.69 | 36 | 474629 | 11449 | 0.4486 | 0.9361 | 1932 | 2653 | 3206 | 2926 |
| dn | 16 | 8 | 256542 | 10866 | 301.83 | 36 | 474629 | 11449 | 0.5405 | 0.9491 | 1959 | 2680 | 3257 | 2970 |
| dn | 20 | 6 | 174269 | 9756 | 271.00 | 36 | 410939 | 10511 | 0.4241 | 0.9282 | 1861 | 2456 | 2861 | 2578 |
| dn | 20 | 8 | 211441 | 9895 | 274.86 | 36 | 410939 | 10511 | 0.5145 | 0.9414 | 1889 | 2495 | 2895 | 2616 |
| dn | 24 | 6 | 144920 | 8771 | 243.64 | 36 | 356092 | 9497 | 0.4070 | 0.9236 | 1778 | 2265 | 2500 | 2228 |
| dn | 24 | 8 | 176781 | 8896 | 247.11 | 36 | 356092 | 9497 | 0.4964 | 0.9367 | 1803 | 2297 | 2536 | 2260 |
| dn | 32 | 6 | 103150 | 7125 | 197.92 | 36 | 268134 | 7775 | 0.3847 | 0.9164 | 1599 | 1877 | 1939 | 1710 |
| dn | 32 | 8 | 126531 | 7232 | 200.89 | 36 | 268134 | 7775 | 0.4719 | 0.9302 | 1622 | 1910 | 1964 | 1736 |

Note on cfrac_epi (~0.92–0.95): after 60s refractory collapse the plain stream is so dense that nearly every plain episode window contains at least one clean second; the honest clean fraction is **cfrac_raw** (0.38–0.54).

## FACT — path ordering (every-30s RTH clock, horizon 60s)

Long side (+8 favorable / −4 adverse), n_starts = 27299:
- P(fav 8t first) = 0.3291 [day-clustered 95% CI 0.3202, 0.3379]; P(adv 4t first) = 0.6310; P(same-sec tie -> adverse) = 0.0358; P(neither in 60s) = 0.0040.
- tt(fav8) given reached (n=21220): p25=2s p50=5s p75=15s p90=33s. tt(adv4) given reached (n=23928): p25=1s p50=2s p75=7s p90=20s.
- Reach +20t within 60s: n=13807 (0.5058 of starts). Pre-target drawdown (ticks, touch-second included, conservative): p25=2.50 p50=7.50 p75=16.50 p90=29.50 p95=40.50. P(dd<6 | reach20)=0.4264; P(dd<8 | reach20)=0.5137.
- Time-underwater fraction over 60s: mean=0.4838, p25=0.1167 p50=0.4667 p75=0.8333 p90=0.9833.

Short side (−8 favorable / +4 adverse), n_starts = 27299:
- P(fav 8t first) = 0.3210 [CI 0.3121, 0.3291]; P(adv 4t first) = 0.6389; P(tie) = 0.0357; P(neither) = 0.0044.
- tt(fav8) given reached (n=20903): p25=2s p50=5s p75=15s p90=32s. tt(adv4) given reached (n=24182): p25=1s p50=2s p75=7s p90=20s.
- Reach −20t within 60s: n=13736 (0.5032). Pre-target drawdown: p25=2.50 p50=7.50 p75=16.00 p90=29.00 p95=39.50. P(dd<6 | reach20)=0.4263; P(dd<8 | reach20)=0.5138.
- Time-underwater: mean=0.4977, p25=0.1333 p50=0.5000 p75=0.8500 p90=0.9833.

Cross-check: P(dd<6 | reach20) on the 30s clock (0.4264 long / 0.4263 short) matches cfrac_raw(20,6) on all decision seconds (0.4242 up / 0.4241 dn).

## FACT — directional pre-state, (M=20, K=6) episodes

Groups (episode starts, refractory 60s): up_clean n=9829, dn_clean n=9756, up_dirty n=9225, dn_dirty n=9082; each on 36 sessions. Effect = median diff / pooled IQR; day-clustered 95% CI, 500 reps; `*` = CI excludes 0. Full tables in `w4e_features.csv` / stdout; significant rows:

up_clean vs dn_clean (A=up_clean):
| feature | med_A | med_B | effect | ci_lo | ci_hi | sig |
|---------|-------|-------|--------|-------|-------|-----|
| ret5 | -9.0 | 9.0 | -0.878 | -18.5 | -17.0 | * |
| ret10 | -11.5 | 11.0 | -0.8182 | -24.0 | -22.0 | * |
| ret30 | -15.0 | 15.0 | -0.7059 | -31.5 | -28.5 | * |
| ret60 | -10.0 | 9.5 | -0.3545 | -20.1313 | -18.0 | * |
| sflow10 | -6.0 | 7.0 | -0.5652 | -13.525 | -12.0 | * |
| sflow60 | -4.0 | 7.0 | -0.1833 | -13.0 | -9.0 | * |

Not significant: rv60, eff60, spread_t, spread60, trades10, dist_hi, dist_lo.

up_clean vs up_dirty (A=up_clean) — the clean-vs-dirty contrast, same direction:
| feature | med_A | med_B | effect | ci_lo | ci_hi | sig |
|---------|-------|-------|--------|-------|-------|-----|
| ret5 | -9.0 | -4.0 | -0.303 | -5.5 | -4.5 | * |
| ret10 | -11.5 | -5.0 | -0.2889 | -8.0 | -6.0 | * |
| ret30 | -15.0 | -5.0 | -0.2564 | -11.5 | -8.5 | * |
| ret60 | -10.0 | 2.0 | -0.2286 | -12.5 | -10.0 | * |
| eff60 | 0.1404 | 0.1118 | +0.1883 | +0.0233 | +0.0344 | * |
| sflow10 | -6.0 | -2.0 | -0.1905 | -5.0 | -3.0 | * |
| sflow60 | -4.0 | 2.0 | -0.1017 | -8.0 | -4.0 | * |

Not significant: rv60, spread_t, spread60, trades10, dist_hi, dist_lo.

dn_clean vs dn_dirty (A=dn_clean) — mirror, same significant set:
ret5 +0.3438*, ret10 +0.2889*, ret30 +0.2857*, ret60 +0.2255*, eff60 +0.1748* (0.1365 vs 0.1101), sflow10 +0.25*, sflow60 +0.1*; rv60/spread/trades10/dist not significant.

## INFERENCE

1. **Clean moves are contrarian-born.** UP-clean episodes start after a short-term selloff (median ret30 = −15.0t) with net selling flow (median sflow10 = −6.0); DOWN-clean is the mirror. This is descriptive (label-conditioned), but the direction of the pre-state is unambiguous and symmetric, and it agrees with the campaign's standing finding that the 1s-scale edge is mean-reversion-flavored (W3-1 snapback).
2. **What separates CLEAN from DIRTY in the same direction (key deliverable):** a *deeper* immediately-preceding contrarian move (ret5..ret60 effects −0.23..−0.30, all CI-solid, in both directions), *higher* path efficiency eff60 (0.1404 vs 0.1118 up; 0.1365 vs 0.1101 down; effects ~+0.18, CI-solid), and *more contrarian* order flow (sflow10 effect ~0.19–0.25, CI-solid). Volatility (rv60), spread, activity (trades10), and location vs session extremes (dist_hi/dist_lo) do NOT separate clean from dirty. Effects are modest (|0.1–0.3| IQR units): no single feature is a clean/dirty classifier; a W5 seed should combine a contrarian trigger (deep short-horizon pullback) + eff60 floor + aligned sflow, and should expect enrichment of the clean fraction, not separation.
3. **Adverse-first is the base path shape.** On the 30s clock the −4t excursion precedes the +8t excursion roughly 2:1 (0.631 vs 0.329 long; 0.639 vs 0.321 short), median time-to-adverse-4t is 2s vs 5s to favorable-8t, and the median pre-target drawdown of successful +20t moves is 7.5t — larger than both frozen K bounds (only 42.6% of reachers stay under 6t; 51.4% under 8t). Mean time-underwater is ~0.48–0.50. Implication for W5: market-order chases with tight stops (≤6t) structurally fight the path; pullback/limit entries (the W4-A passive intuition) or stops ≥ ~8t fit the path shape better.
4. **Labels are dense and symmetric.** 198–304 clean episodes/day per config, present on 36/36 days, up/dn frequencies nearly identical (e.g. 273.03 vs 271.00 epi/day at 20/6); by block-count the mix is spread across the day (blocks are 1h/1.5h/2h/2h wide, so the first hour is the densest per unit time). Any W5 rule will be selection-limited, not opportunity-limited.
5. **Caveat.** The clean label conditions on the future path; the pre-state contrasts are enrichment statistics, not a validated predictor. Any tradeable rule seeded from (2)–(3) requires a new frozen spec (per W4-E spec text) and a sequential-episode P&L readout with costs.
