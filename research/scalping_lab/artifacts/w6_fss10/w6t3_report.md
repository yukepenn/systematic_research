# W6-T3 ES-led lag rule (FSS-10, KPI A) — READOUT: NEGATIVE, 0/12 pass (2026-08-07)

Spec: `specs/W6_fss10_redteam.md` §T3 (frozen, committed 58a97a3 before this run).
Code: `src/python/w6_t3_leadlag.py`. Seed 20260808, 1000 session-bootstrap reps,
day-clustered CIs. Tables: `t3_summary.csv`, `t3_by_session.csv`, `t3_episodes.csv`;
full stdout `t3_stdout.txt`. Registry: W6 block (S22–S24, orchestrator).

## Construction (frozen, implemented literally)

- 1s RTH (09:30–16:00 ET) quote-alive clock on the NQ grid1s+sechilo frame (house
  frame construction, w31/census pattern).
- JOIN: ES sechilo merged on time; `es_mid_last` ffilled with staleness limit 5s
  (grid verified contiguous 1s per session, assert in code); ES-feature-NaN seconds
  are not decision seconds; es hi/lo never ffilled (unused — barriers are NQ).
- Z-NORM: z_ret60 = ret60 / rolling-600s std of 1s Δmid, per instrument, trailing,
  min 300s history.
- Trigger: es_z_ret60 − nq_z_ret60 ≥ θ (θ=1.0 primary, 1.5 neighbor) AND
  |es_z_ret60| ≥ 0.5; direction = sign(es_ret60); long if ES up, short if ES down
  (the symmetric construction — both directions from the single inequality).
- One sequential book per (θ, bracket): entry at the trigger second's NQ mid_last,
  brackets (24,8) and (32,10) NQ ticks, cap 300s (cap exit at mid, gross MTM),
  cooldown 60s after resolution, same-second-both-crossed → adverse (house
  conservative convention).
- Sessions: 36 = intersection of NQ sechilo (37) and ES archive (39) minus
  s20250902 (NQ quote-dead in RTH). Costs C1=2.872t, C2=4.872t.

## FACT — all 12 cells fail the pass rule (net C1 > 0 AND CI_lo > −0.5t)

Pooled, 36 sessions; epi/day = episodes/36; P(tgt) = tgt/(tgt+adv), cap excluded;
baseline = unconditional census excursion surface (30s clock, same barrier machinery):

| θ | bracket | dir | epi | epi/day | days | P(tgt) [95% CI] | base | lift | net C1 [95% CI] | net C2 | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.0 | +24/−8 | long | 3955 | 109.9 | 36 | 0.2496 [0.2352,0.2640] | 0.2525 | −0.29pp | −2.851 [−3.313,−2.405] | −4.851 | FAIL |
| 1.0 | +24/−8 | short | 3201 | 88.9 | 36 | 0.2291 [0.2140,0.2447] | 0.2488 | −1.97pp | −3.518 [−3.986,−3.017] | −5.518 | FAIL |
| 1.0 | +24/−8 | both | 7156 | 198.8 | 36 | 0.2404 [0.2295,0.2521] | 0.2508 | −1.04pp | −3.149 [−3.486,−2.791] | −5.149 | FAIL |
| 1.0 | +32/−10 | long | 3658 | 101.6 | 36 | 0.2399 [0.2258,0.2540] | 0.2361 | +0.38pp | −2.672 [−3.255,−2.084] | −4.672 | FAIL |
| 1.0 | +32/−10 | short | 2934 | 81.5 | 36 | 0.2296 [0.2152,0.2434] | 0.2328 | −0.32pp | −3.162 [−3.752,−2.601] | −5.162 | FAIL |
| 1.0 | +32/−10 | both | 6592 | 183.1 | 36 | 0.2353 [0.2246,0.2468] | 0.2346 | +0.07pp | −2.890 [−3.339,−2.440] | −4.890 | FAIL |
| 1.5 | +24/−8 | long | 3544 | 98.4 | 36 | 0.2429 [0.2302,0.2546] | 0.2525 | −0.96pp | −3.061 [−3.460,−2.703] | −5.061 | FAIL |
| 1.5 | +24/−8 | short | 2785 | 77.4 | 36 | 0.2371 [0.2208,0.2542] | 0.2488 | −1.17pp | −3.266 [−3.783,−2.714] | −5.266 | FAIL |
| 1.5 | +24/−8 | both | 6329 | 175.8 | 36 | 0.2404 [0.2302,0.2505] | 0.2509 | −1.05pp | −3.151 [−3.462,−2.833] | −5.151 | FAIL |
| 1.5 | +32/−10 | long | 3299 | 91.6 | 36 | 0.2244 [0.2125,0.2380] | 0.2361 | −1.17pp | −3.302 [−3.816,−2.692] | −5.302 | FAIL |
| 1.5 | +32/−10 | short | 2564 | 71.2 | 36 | 0.2266 [0.2111,0.2454] | 0.2328 | −0.62pp | −3.279 [−3.931,−2.491] | −5.279 | FAIL |
| 1.5 | +32/−10 | both | 5863 | 162.9 | 36 | 0.2254 [0.2145,0.2361] | 0.2347 | −0.93pp | −3.292 [−3.737,−2.865] | −5.292 | FAIL |

- Net C1 range −2.672 to −3.518 t/trade; **CI_hi < −2.0t in every cell** — nowhere
  near the gate (net C1 > 0, CI_lo > −0.5t). Net C2 −4.67 to −5.52t.
- Lift vs unconditional baseline: **−1.97 to +0.38pp**, indistinguishable from zero,
  vs the frozen decision constant of **+8.7–9.1pp needed at (24,8), +7.0–7.4pp at
  (32,10)**. The ES-led divergence state conditions almost nothing.
- Coherent NEGATIVE plateau: primary θ=1.0 and neighbor θ=1.5, both brackets, both
  directions and the combined book all fail together; no fragile isolated positive.

## FACT — the trigger is a near-permanent state, not a setup

- Trigger seconds/day (pre-sequential): mean 6,884 at θ=1.0 and 5,516 at θ=1.5 of
  ~22,137 decision-seconds/day — the gate is on **31% / 25% of all RTH seconds**;
  the sequential book saturates at ~163–199 episodes/day (cooldown-bound).
- Unit note (diagnostic, not a spec deviation): z_ret60 divides a 60s return by the
  **1s** Δmid std, so a random-walk-typical 60s move is |z| ≈ √60·0.8 ≈ 6. Median
  |es_z| at entry is 4.4–5.0 — θ ∈ {1.0, 1.5} and the |es_z| ≥ 0.5 gate are weak
  thresholds in these units. This mirrors the W3-1 finding: the conditioned state is
  too common to carry selection power.
- Directional anatomy of the literal frozen rule (from `t3_episodes.csv` medians,
  24/8): longs fire with es_z ≈ +5.0, nq_z ≈ +3.1 — the genuine "NQ lags an ES
  up-move" catch-up trade; shorts fire with es_z ≈ −4.4, nq_z ≈ −6.3 — NQ has
  already fallen *more* than ES (gap ≥ θ with both negative puts NQ below ES), i.e.
  the short side is momentum-continuation on an NQ-led down-move, not an ES-led lag.
  Both sides are decisively negative, so no reading of the construction survives.
- Entries are spread across the day (p25/p50/p75 ≈ 10.9/12.4/14.1 ET-h); outcome mix
  across all cells tgt=6,080 adv=19,712 cap=148 (cap mean gross +11.2t).

## Caveats (recorded, none material to the verdict)

- ES afternoons truncated on 3 sessions (ES-fresh seconds end early; those seconds
  are correctly non-decision by the staleness rule): s20260303 ES ends 12:51:44
  (12,110 dec-secs), s20260312 ends 14:59:24 (19,770), s20260519 ends 14:43:22
  (18,808 — the known capped/truncated ES file). Overall ES-fresh coverage is
  ~97.3% of RTH-alive seconds (22,137/22,749); within covered spans the max ES gap
  is 1s (no >5s staleness holes).
- s20251128 is a 13:00 half-day (13,500 dec-secs); s20251117 NQ-alive ends ~15:14.
- Baseline census P(tgt) was computed with cap 600s on a 30s clock vs cap 300s
  here; census p_neither ≤ 0.6% so the comparison bias is negligible.
- The literal frozen ffill(limit=5) leaves >5s ES holes as NaN in the Δmid series
  (they drop out of the rolling std rather than counting as zero-change seconds);
  bias direction is to slightly raise es_sd and shrink |es_z| — conservative on
  trigger frequency, and moot given the trigger is already near-permanent.

## Verdict (T3 slice of FSS-10; family verdict is the orchestrator's, T2 decisive)

**T3 NEGATIVE — KILL for this realization.** The ES-led 60s z-divergence lag rule
adds no conditional lift (−2.0 to +0.4pp vs +7.0–9.1pp required) and loses
2.7–3.5t/trade at C1 with CI_hi < −2.0t across the full frozen grid — a coherent
negative plateau under the plateau logic. Per the §9 verdict logic this satisfies
the "T3 negative" leg of the closure test. Scope guard: this kills the *trade-rule
realization* (60s z-divergence, θ∈{1.0,1.5}, 24/8 & 32/10, market-at-mid entry,
retail-lag clock); the decisive family-level measurement of whether ES carries any
material information for NQ at these lags is T2's ceiling increment, not this test.
