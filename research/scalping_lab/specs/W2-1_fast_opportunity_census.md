# W2-1 — FAST_STRUCTURAL_OPPORTUNITY_CENSUS + wide excursion surface (Amendment 4 §5–6, P1+P2)

Status: FROZEN before any census statistic is read. Date: 2026-08-08.
Mandate: MANDATE_AMENDMENT_4_FAST_STRUCTURAL.txt §0, §5, §6. Zone F (FAST_STRUCTURAL_SCALP).
Class: census/instrumentation — produces LABELS and descriptive conditional
distributions only. **No trading rule may be evaluated for P&L from this census; any rule
suggested by it must be preregistered in a NEW spec first (Amendment 4 §5).** Registry rows
logged as census; DoF charging begins when a rule is selected from these tables.

## Data (frozen)

- 37 L2 sessions of the Tier-0 DISCOVERY subset (the 3 L1-only sessions s20250811,
  s20250924, s20260430 are excluded — no mid reconstruction).
- New supplementary substrate `substrate/sechilo/NQ/<tag>.parquet`: per-second
  mid_last / mid_high / mid_low from the UNION event stream (all Bid and Ask events
  sorted by time, other side forward-filled, mid = (bid+ask)/2 in ticks). This is a
  Layer-1 derivative (build-once, reusable); build script `src/python/build_sechilo.py`.
- Existing `substrate/grid1s/NQ/` for activity/spread/flow features.
- Decision clock: every whole second t with 09:30:00 ≤ t < 16:00:00 ET.

## Opportunity labels (frozen)

- Horizons H ∈ {5,10,20,30,45,60,90,120,180,300} s; magnitudes M ∈ {8,12,16,20,24,32} t.
- UP-opportunity(H,M) at t: max over (t, t+H] of mid_high − mid_last(t) ≥ M.
  DOWN symmetric with mid_low. Labels are retrospective — never tradeable as-is.
- Episode logic: within each (H,M,dir), consecutive/overlapping flagged seconds collapse —
  an episode starts at the first flagged second and blocks new episodes for H seconds.
  Report raw flagged seconds, episodes, episodes/day, unique days.

## Census deliverable 1 — the opportunity map

Counts and rates for the full (H,M,dir) surface, overall and by time-of-day block
{09:30–10:30, 10:30–12:00, 12:00–14:00, 14:00–16:00}. Answers: how often does the
owner-scale move (~10–30t in 5–120s) actually exist, and when?

## Census deliverable 2 — pre-state characterization (frozen to 3 labels to limit DoF)

Primary label (H=60s, M=20t); secondary (H=30s, M=12t) and (H=120s, M=24t).
Causal features at t (trailing only):
- Path (sechilo mid): ret_5s/10s/30s/60s/300s (t); rv60, rv300 (std of 1s Δmid);
  TV60 = Σ|Δmid|; eff60 = |ret_60|/TV60; range300; dist from causal session high/low (t);
  minutes since session high/low.
- Activity (grid1s): trades_10s/60s, vol_10s/60s, upd_10s/60s (bid_upd+ask_upd),
  activity acceleration = trades_10s/(trades_60s/6).
- Flow (grid1s, tick-rule): sflow_10s/60s and normalized sflow_60s/vol_60s.
- Spread (grid1s): spread_t at t, mean spread_60s.
- Context: time-of-day block.
Missing-value rule: any feature with insufficient trailing history (session start) → row
excluded from characterization (kept in counts).

Matched controls: for each primary/secondary episode, 4 control seconds (seed 20260808)
drawn from the same time-of-day block (any discovery session) with pooled-RTH rv60 in the
same quintile, that are NOT flagged for any (same-H, M≥8) label in either direction and
whose forward |move| within H is < M/2. Comparisons reported: median difference,
robust effect = median diff / pooled IQR, day-clustered bootstrap 95% CI. Also
UP-episodes vs DOWN-episodes on the same features (directional information content).

Frozen honesty rule: any feature whose effect disappears within the rv60-matched control
comparison is reported as "volatility proxy — not a discovery" (Amendment 4 §31).

## Excursion surface (P2, frozen)

Seed pairs (A,B) ∈ {(8,4),(12,4),(16,6),(20,6),(20,8),(24,8),(32,10)}, both directions.
Unconditional baseline: decision clock every 30s in RTH (decorrelation), entry ref =
mid_last(t), evaluated on the per-second hi/lo path, cap 600s.
- Same-second ambiguity rule (conservative): if target and adverse are first crossed in
  the SAME second, count adverse-first.
- Report P(target first), P(adverse first), P(neither in cap), by pair, pooled +
  day-clustered CI; break-even win rate after costs: p* = (B+c)/(A+B) with
  c = 2.872 (C1) and 4.872 (C2) ticks; neither-hit reported separately.
- MFE/MAE distributions at H ∈ {5,10,20,30,45,60,90,120} s (quantiles 50/75/90/95/99),
  time-to-MFE, path efficiency — from the same per-second arrays.
- Purpose: (a) redundancy pruning of the pair grid via MFE/MAE (Amendment 4 §6);
  (b) baseline against which every conditional state will be measured. 1s hi/lo
  evaluation is an approximation (intra-second ordering unknown); candidate-level
  results will be re-evaluated on the tick stream before promotion.

Artifacts: `artifacts/census/census_counts.csv`, `census_features.csv`,
`census_updown.csv`, `excursion_surface.csv`, `census_report.md`.
Code: `src/python/build_sechilo.py`, `src/python/opportunity_census.py`.
