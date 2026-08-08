# W6 T1 — ES-state conditioning lift on the NQ excursion surface

- Spec: `specs/W6_fss10_redteam.md` §T1 (frozen, committed 58a97a3). Descriptive lift table only — no rule P&L.
- Code: `src/python/w6_t1_es_lift.py`. Seed 20260808, 1000-rep session bootstrap, day-clustered, paired with census per-session counts for the lift CI.
- Clock/label: 30s RTH quote-alive clock (census convention), brackets (24,8) and (32,10), both candidate directions, cap 600s, conservative same-second-both-crossed->adverse barrier on NQ per-second hi/lo (`barrier()` verbatim from `opportunity_census.py`).
- Join (frozen): ES sechilo merged onto the NQ per-second frame on time; `es_mid_last` ffilled with 5s staleness limit (older -> ES features NaN at that second, excluded). ES hi/lo not ffilled (not used in T1).
- Z-norm (frozen): `z_ret60 = ret60 / rolling-600s std of 1s dmid`, per instrument, trailing, min 300s history.
- Baseline: `artifacts/census/excursion_surface.csv` matched on bracket+dir. C1 gap constants (pp): 8.73 / 9.09 (24/8 L/S), 7.03 / 7.37 (32/10 L/S).
- Sessions: 36 (NQ-L2-usable ∩ ES availability; s20250902 skipped quote-dead). REPRO CONTROL: unconditional per-session surface recomputed under the ES-joined frame matches `excursion_surface_by_session.csv` exactly — max |deviation| = 0 across all 144 session×bracket×dir rows.
- ES-feature validity on the 30s clock: 26,572 / 27,299 starts (97.34%).

## Cell definitions (frozen)

| Cell | Condition at t (on valid ES+NQ features) | Candidate dir |
|---|---|---|
| CONFIRM | sign(es_ret60) = candidate dir AND \|es_z_ret60\| >= 0.5 | long and short |
| NONCONF | sign(es_ret60) = −candidate dir AND \|es_z_ret60\| >= 0.5 | long and short |
| NQ_LED | nq_z_ret60 − es_z_ret60 >= +1.0 | both tested on same start set |
| ES_LED | es_z_ret60 − nq_z_ret60 >= +1.0 | ES direction (long rows = subset with es_ret60 > 0, short rows = subset with es_ret60 < 0) |

Note: CONFIRM/long and NONCONF/short condition on the identical ES-up-strong state (12,403 starts); the tested NQ direction differs. Same for CONFIRM/short vs NONCONF/long (11,980 starts).

## FACT — T1 lift table (`t1_lift_table.csv`)

| cell | dir | A/B | n_starts | sessions | occ % | P(target) | P 95% CI | baseline | lift (pp) | lift 95% CI (pp) | gap (pp) | lift − gap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONFIRM | long | 24/8 | 12,403 | 36 | 45.43 | 0.2425 | [0.2333, 0.2515] | 0.2525 | −1.00 | [−1.66, −0.30] | 8.73 | −9.73 |
| CONFIRM | long | 32/10 | 12,403 | 36 | 45.43 | 0.2273 | [0.2193, 0.2361] | 0.2361 | −0.88 | [−1.53, −0.22] | 7.03 | −7.91 |
| CONFIRM | short | 24/8 | 11,980 | 36 | 43.88 | 0.2412 | [0.2303, 0.2523] | 0.2488 | −0.76 | [−1.41, −0.13] | 9.09 | −9.85 |
| CONFIRM | short | 32/10 | 11,980 | 36 | 43.88 | 0.2241 | [0.2116, 0.2363] | 0.2328 | −0.87 | [−1.52, −0.23] | 7.37 | −8.24 |
| NONCONF | long | 24/8 | 11,980 | 36 | 43.88 | 0.2624 | [0.2527, 0.2713] | 0.2525 | +0.99 | [+0.32, +1.71] | 8.73 | −7.74 |
| NONCONF | long | 32/10 | 11,980 | 36 | 43.88 | 0.2448 | [0.2353, 0.2533] | 0.2361 | +0.87 | [+0.25, +1.52] | 7.03 | −6.16 |
| NONCONF | short | 24/8 | 12,403 | 36 | 45.43 | 0.2547 | [0.2461, 0.2630] | 0.2488 | +0.59 | [−0.04, +1.18] | 9.09 | −8.50 |
| NONCONF | short | 32/10 | 12,403 | 36 | 45.43 | 0.2396 | [0.2270, 0.2517] | 0.2328 | +0.68 | [+0.03, +1.32] | 7.37 | −6.69 |
| NQ_LED | long | 24/8 | 9,143 | 36 | 33.49 | 0.2512 | [0.2428, 0.2606] | 0.2525 | −0.13 | [−0.92, +0.68] | 8.73 | −8.86 |
| NQ_LED | long | 32/10 | 9,143 | 36 | 33.49 | 0.2407 | [0.2315, 0.2502] | 0.2361 | +0.46 | [−0.34, +1.27] | 7.03 | −6.57 |
| NQ_LED | short | 24/8 | 9,143 | 36 | 33.49 | 0.2510 | [0.2415, 0.2608] | 0.2488 | +0.22 | [−0.54, +0.98] | 9.09 | −8.87 |
| NQ_LED | short | 32/10 | 9,143 | 36 | 33.49 | 0.2354 | [0.2244, 0.2475] | 0.2328 | +0.26 | [−0.40, +0.87] | 7.37 | −7.11 |
| ES_LED | long | 24/8 | 4,679 | 36 | 17.14 | 0.2423 | [0.2287, 0.2577] | 0.2525 | −1.02 | [−2.40, +0.38] | 8.73 | −9.75 |
| ES_LED | long | 32/10 | 4,679 | 36 | 17.14 | 0.2215 | [0.2063, 0.2382] | 0.2361 | −1.46 | [−2.87, +0.01] | 7.03 | −8.49 |
| ES_LED | short | 24/8 | 3,680 | 36 | 13.48 | 0.2367 | [0.2197, 0.2533] | 0.2488 | −1.21 | [−2.50, +0.05] | 9.09 | −10.30 |
| ES_LED | short | 32/10 | 3,680 | 36 | 13.48 | 0.2166 | [0.1990, 0.2329] | 0.2328 | −1.62 | [−2.67, −0.59] | 7.37 | −8.99 |

P CI = day-clustered bootstrap CI on conditional P(target-first); lift CI = paired day-clustered bootstrap of (conditional − unconditional) pooled on the same resampled sessions. All 16 rows: n_boot_ok = 1000/1000. p_neither <= 0.0079 everywhere (cap 600s almost always resolves).

## FACT — occupancy (fraction of 30s clock seconds in each cell)

| Cell/dir | n | occ % |
|---|---|---|
| CONFIRM/long (= NONCONF/short state) | 12,403 | 45.43 |
| CONFIRM/short (= NONCONF/long state) | 11,980 | 43.88 |
| NQ_LED (both dirs, same set) | 9,143 | 33.49 |
| ES_LED/long | 4,679 | 17.14 |
| ES_LED/short | 3,680 | 13.48 |

Denominator = all 27,299 clock starts. ES-valid starts: 26,572 (97.34%).

## Verdict

- Cells with lift >= gap AND lift CI excluding 0: **0**.
- Cells with lift >= 5pp: **0**. Largest positive lift anywhere: NONCONF/long 24/8 at +0.99pp [+0.32, +1.71] — an order of magnitude below the 8.73pp C1 gap.
- **T1 is NEGATIVE.** ES-state conditioning moves the excursion surface by at most ~±1.6pp against required gaps of 7.0–9.1pp.
- Directional reading (descriptive, small): CONFIRM lifts are uniformly *negative* (−0.76 to −1.00pp, all four lift CIs entirely below 0) and NONCONF lifts uniformly *positive* (+0.59 to +0.99pp, 3 of 4 CIs excluding 0) — i.e. entering NQ *against* a strong ES move does marginally better than entering with it, consistent with the campaign's established mean-reversion/snapback character. ES_LED (enter NQ in ES direction after ES out-runs NQ) is the *worst* cell (down to −1.62pp [−2.67, −0.59]), which is directly unfavorable for the T3 lag-rule hypothesis.

## Caveats

1. **Frozen z-scale is wide.** z_ret60 divides a 60s return by the std of 1s dmid, so under near-iid increments its natural scale is ~sqrt(60) ≈ 7.75, not 1: pooled median |es_z| = 4.53 (p90 11.73), median |nq_z| = 4.75 (p90 12.18). The |es_z| >= 0.5 "strong" gate therefore passes 91.76% of valid seconds and the CONFIRM/NONCONF cells are weak conditioners (occupancy 44–45%). Definitions and thresholds applied exactly as frozen, symmetrically to both instruments; a re-scaled gate (e.g. 0.5·sqrt(60) = 3.87, passing 56.45%) was NOT run and would be a new spec.
2. **ES truncated afternoons.** Beyond the flagged es_s20260519 (ES ends 14:43:22 ET; 627/780 = 80.4% valid clock starts), s20260303 also has an early ES end (12:51:44 ET; 404/780 = 51.8% valid), with s20260312 (84.5%) and s20260211 (91.4%) partial. No intra-RTH staleness gaps >5s before the truncation points in the two audited sessions. Truncated seconds are excluded by the frozen 5s staleness rule, not imputed.
3. **ES_LED construction.** Spec literal: cell = es_z − nq_z >= +1.0, candidate = ES direction. Implemented as: long rows = cell ∩ {es_ret60 > 0}, short rows = cell ∩ {es_ret60 < 0}; the two rows partition the cell (up to es_ret60 = 0 exactly). A mirror-symmetric variant (short = nq_z − es_z >= 1.0 ∩ ES down) was NOT run here; T3 owns the symmetric trade-rule construction.
4. Baseline p_base taken from the frozen census CSV (4-decimal); the paired bootstrap recomputes both legs from per-session counts (pooled recomputation matches, repro deviation = 0).

Artifacts: `t1_lift_table.csv`, `t1_by_session.csv`, `t1_occupancy.csv`, `t1_stdout.txt` (incl. appended diagnostics), this report. Discovery substrate only; no holdout/confirmation dates touched; no git commit.
