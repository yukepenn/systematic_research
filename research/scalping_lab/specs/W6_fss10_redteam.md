# W6 — FSS-10 (last §9 family) + independent red team (frozen before readout, 2026-08-08)

Purpose: complete the Amendment 6 §9 closure checklist for Zone F. FSS-10 is the final
untested family; the red team then rules on "no major untested causal information family
remains." Only after BOTH may the §34 declaration be made (and only in the "not found in
tested universe" form, never "mathematically impossible").

Common: NQ sechilo/grid1s + NEW `substrate/sechilo/ES/es_<tag>.parquet` (ES ticks,
union-BBO per-second mid_last/hi/lo). Analysis sessions = intersection of NQ-L2 (37) and
ES archive (39) — expect ~36 (NQ s20250902 is quote-dead; ES es_s20260519 capped at 12M
rows — truncated afternoon, keep with caveat). Join ES to NQ per-second frame on time;
ffill ES mid ≤ 5s staleness, else NaN (cross-instrument clock skew guard). Costs, barrier
conventions, sequential sim, day-clustered CIs (seed 20260808) as all prior waves.
Z-normalization for cross-market comparability: z_ret60 = ret60 / (rolling 600s std of
1s Δmid), per instrument, trailing only.

## T1 — ES-state conditioning lift on the excursion surface [descriptive lift table]
30s RTH clock (census convention). For brackets (24,8) and (32,10), both directions,
compute P(target-first) conditional on frozen ES-state cells at t:
- CONFIRM: sign(es_ret60) = candidate direction AND |es_z_ret60| ≥ 0.5.
- NONCONF: sign(es_ret60) = −candidate direction AND |es_z_ret60| ≥ 0.5.
- NQ_LED divergence: nq_z_ret60 − es_z_ret60 ≥ +1.0 (test candidate = long AND short).
- ES_LED divergence: es_z_ret60 − nq_z_ret60 ≥ +1.0 (candidate = ES direction).
Report per cell: n, sessions, P(target), lift vs unconditional census baseline,
day-clustered CI. Decision constant: gap = 8.7–9.1pp (24/8), 7.0–7.4pp (32/10).

## T2 — Ceiling increment [the decisive FSS-10 measurement]
Re-run the C5 predictability-ceiling protocol EXACTLY (same 30s clock, same 4 labels,
same chronological session-grouped expanding 5 folds, same 2 models, same leakage
guards) on: (a) the original 27 NQ features [reproduction control]; (b) 27 NQ + 8 ES
features: es_ret30/60/300, es_z_ret60, es_rv60, nq_es_z_diff60 (=nq_z−es_z), sign-agree
indicator, es_spread_t. Frozen readout: Δ(top-decile lift) between (b) and (a) per
label/model, with day-clustered CI. Interpretation rule: if NO label/model in (b)
reaches the C5 5pp bar, FSS-10 is negative and the ES-information hypothesis is closed
at retail-accessible lags; if any (b) ≥ 5pp where (a) < 5pp, ES adds material
information → conversion spec next wave.

## T3 — ES-led lag rule [the trade-rule realization, KPI A]
Sequential sim, 1s clock: enter NQ in ES direction when es_z_ret60 − nq_z_ret60 ≥ θ
(θ=1.0 primary; 1.5 neighbor) AND |es_z_ret60| ≥ 0.5. Brackets (24,8),(32,10); cap
300s; cooldown 60s; both directions via symmetric construction. Pass rule and plateau
logic as all waves (net C1 > 0 AND CI_lo > −0.5t).

## RT — Independent red team (two lenses, no access to each other's output)
RT-1 "attack the kills": audit the 14 family kills + C5 ceiling for construction flaws
that could mask a real edge (wrong clock, non-binding gates like W5-C1's recovery, label
artifacts, cost double-counting, sample-regime dependence 2025-08→2026-05 high-vol,
conservative-barrier bias magnitude, 1s-grid approximation error vs tick truth). Verdict
per kill: SOUND / FLAWED(name the flaw + what re-test would differ).
RT-2 "what remains untested": enumerate causal information families NOT yet tested in
Zone F against the full mandate list (Amendments 1-6) and the data inventory; for each:
testable-with-current-data? plausible ≥7pp mechanism? Explicitly assess at minimum:
VWAP/volume-acceptance levels (FSS-9 untested beyond ON/OR), opening-drive/first-15min
states, calendar-event-anchored windows with pre-RTH handling, book-size/L3 (data-
blocked?), H-B1 anti-chase (role C), cross-asset beyond ES on minute data, session-gap
conditioned states. Verdict: list of MAJOR untested families (empty list = closure
supported) with EVI ranking.
§9 verdict logic (orchestrator): closure declared ONLY if T1/T2/T3 negative AND RT-1
finds no FLAWED kill that could flip a verdict AND RT-2's major-untested list is empty
or contains only data-blocked items. Otherwise: W7 tests what RT-2 names.

Artifacts: `artifacts/w6_fss10/`, `artifacts/w6_redteam/`. Registry S22-S24.
