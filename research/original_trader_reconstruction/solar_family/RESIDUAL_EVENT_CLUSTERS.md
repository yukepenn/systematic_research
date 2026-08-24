# RESIDUAL_EVENT_CLUSTERS — the CAND2 residual after R5 (directive v3.0 §5, C2)
2026-08-24. Scope: master (+247 trades / −$27.2k) + weekly-validation residuals.

## What R5 changed about the residual's identity
The residual is NOT one thing. It decomposes into:

1. **The hp-build gap (dominant in weekly data)**: hp-machine weeks show 20-70%
   FEWER trades than the raw CAND2 stream with longer holds and larger winners.
   This is a SIBLING BUILD's suppression + winner-extension, not a CAND2 defect.
   Event signature: our excess vs hp targets is concentrated in mid-session
   churn (holds too short by 10-47 min in Jul-Oct) — consistent with the
   FEB2025 fast layer's inverse: where his build waits through pullbacks, ours
   flips. Clustering the actual events requires HIS trade lists (weekly
   aggregates cannot label which of our trades are extra) — label-blocked.
2. **The dev-build thin-edge gap**: on dev weeks counts fit (±7%) but net runs
   −3.4k..−5.2k/week low. Same signature as the master −27.2k over 2 years:
   his adds are FEW and PROFITABLE (a sparse pullback/resume layer), our
   excess is noise-flips. Direct §5 clustering again needs per-trade labels.
3. **Calendar stand-downs**: 12/21 Christmas week (tgt 9 vs sim 17) — a
   holiday suppression CAND2 lacks. Cheap to encode; not yet promoted (single
   observation; would be tuning without a second holiday label).
4. **Known unmodeled panel changes**: entries/direction=2 (1/18+), the 46/36
   St rows, the [0/2] group — bounded, documented, not chased.

## §5 question checklist (answered with available labels)
- Same-direction re-entry after stop? — untestable at weekly granularity; the
  3-bar cooldown + stop interplay reproduces label days, no contradiction.
- Near-T2/pullback states? — YES by inference: A3-A5 retune invisibility
  (R5 finding 2) proves an active pullback layer in his build; the master
  cent-exact days already showed a late-mode T2 trade (1/17 20:48) our T1-only
  stream lacks.
- After session-equity transitions? — the D-gate covers the labeled cases
  (42/42); no NEW equity-state pattern emerges from weekly errors.
- Short-side asymmetry? — YES: master residual is short-concentrated; era-B
  short-stop time-variance (65↔75) found; directional gating beyond the stop
  remains possible but unidentifiable from aggregates.
- Chop-month concentration? — YES (2024-08, 2025-01 master; Jul-Oct-2025
  weekly): consistent with churn-suppression/pullback-qualification we lack.

## Verdict
Residual mechanism = the trader's own sparse pullback/qualification layer
(plus a sibling hp build), NOT missing time filters or a broader alpha engine.
Per-trade event clustering is LABEL-BLOCKED until any of: another per-day
Analyzer table (any era), an hp-machine settings frame diff, or June-2026
minute data + TP overlay. Do not reopen broad hypothesis search on aggregates.
