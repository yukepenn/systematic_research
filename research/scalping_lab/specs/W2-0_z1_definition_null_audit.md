# W2-0 — Z1_DEFINITION_AND_NULL_AUDIT (Amendment 4 §2, P0)

Status: FROZEN before any null statistic is read. Date: 2026-08-08.
Mandate: MANDATE_AMENDMENT_4_FAST_STRUCTURAL.txt §2 (mandatory).
Class: verification/instrumentation audit — no selection content, no DoF charge; results
bind interpretation of all past and future DC statistics.

## Established FACT (read from code before this spec, no computation involved)

`src/python/z1_dc_ladder.py` lines 24/30: `amps[k] = abs(ext - prev_ext)` — the variable
ω ("amp") is the **extremum-to-extremum segment amplitude = TOTAL MOVEMENT (TM)**,
not the overshoot. The W1-1 report's "martingale null r = 1" framing is therefore
suspect: for a driftless Brownian motion the expected overshoot beyond the DC
confirmation equals θ, hence E[TM] = 2θ and the correct null for r = E[ω]/θ is ≈ 2,
not 1. This audit quantifies the correct null empirically and re-baselines every claim.

## Formal definitions (frozen)

- θ: DC threshold in ticks.
- Extremum (ext): running max (up mode) / running min (down mode) of event-level mid.
- DCC (directional-change confirmation): first event where price retraces ≥ θ from ext.
  The DC leg = the θ move from ext to the confirmation level.
- OS (overshoot): move from the DCC level to the NEXT extremum (where the following
  reversal will be measured from). By construction TM = θ + OS, i.e. OS = ω − θ.
- TM (total movement) = |ext − prev_ext| = what z1_dc_ladder.py records as ω.
- Worked example (θ=5, ticks): path 100 → 90 (min, prev_ext) → 95 (DCC up at 95)
  → 108 (max, ext) → 103 (DCC down at 103). Up-segment TM = 108−90 = 18; DC leg = 5;
  OS = 108−95 = 13. r_TM = 18/5 = 3.6 for this segment; r_OS = 13/5 = 2.6.
- Flip-to-flip algebraic capture per cycle = ω − 2θ (enter at DCC of the new trend at
  ext∓θ, exit at next DCC at next_ext±θ). Under any martingale E[capture] = 0 by
  optional stopping ⇒ E[TM] = 2θ ⇒ null r_TM = 2 (continuous case; discrete/jump
  processes measured empirically below).

## Nulls (frozen; seed 20260808; exact `dc_segments` detector, unmodified)

- NULL-1: discrete symmetric ±1-tick random walk, 5,000,000 steps × 8 seeds.
- NULL-2: Gaussian random walk, per-session σ matched to each of the 37 L2 discovery
  sessions' event-level mid increments (same length as the session's event count),
  1 replicate per session.
- NULL-3 (primary, leakage-safe): for each of the 37 sessions take the empirical
  event-level mid increment sequence Δm_i (same construction as z1_dc_ladder.py:
  bid-event-keyed asof mid, in ticks), multiply each by an iid random sign, and
  cumulate. Preserves the magnitude/volatility-clustering sequence exactly;
  destroys sign predictability (martingale-ized).

For each null and each θ ∈ {5,10,20,40,80,160}: E[TM]/θ, E[OS]/θ = r−1, mean
flip-to-flip capture (ω−2θ). Empirical comparison: per-session r_emp − r_null3
(paired, same session), day-clustered bootstrap 95% CI (seed 20260808).

## Parity test (frozen)

Direct entry→exit P&L independent of the ω algebra: at each flip event i enter the new
direction at the ACTUAL mid at the confirmation event (`mid[flips[k]]`, includes trigger
gap/jump), exit at the next flip's actual mid. Per-cycle direct gross vs algebraic
(ω − 2θ), on the 37 real sessions, θ grid. Expectation (stated before run): direct ≤
algebraic because discrete jumps overshoot the trigger level; if direct differs from
algebraic by > 0.5t/cycle at any θ, the published economics table must be restated on
the direct basis.

## Frozen interpretation rules

1. If ω = TM (established): all published "r vs null 1" framing is WRONG and must be
   corrected openly (z1_report.md correction banner + corrected findings; CAMPAIGN_STATE;
   FRONTIER Q2; memory). A persistence claim may only be made as
   excess = (r_emp − r_null) · θ ticks/cycle against the MATCHED null (NULL-3 primary),
   at θ values where the day-clustered 95% CI excludes 0.
2. The economic closure is re-evaluated on the DIRECT parity P&L: if direct flip-to-flip
   net C1 < 0 at all θ (day-clustered CI), **Z1 standalone stays CLOSED** (a fortiori if
   direct ≤ algebraic). Role-B/C eligibility unchanged.
3. If NULL-3 r differs from 2.0 materially (jumps/discreteness), the null table becomes
   the campaign reference null curve for ALL future DC statistics.
4. No re-tuning of the θ grid; no new economic claims from this audit.

Artifacts: `artifacts/z1/z1_null_audit.csv`, `artifacts/z1/z1_null_audit_report.md`,
corrections in place. Code: `src/python/z1_null_audit.py`.
