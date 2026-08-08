# SMV2AA_MIX_SHIFT -- REPORT (seq 406)

**Class**: DIAGNOSTIC (prerequisite). Spec: `runs/SMV2AA_MIX_SHIFT/spec.yaml` (committed f6fb7d1).
**Outcome: DIAGNOSTIC KILL.** Policy cells 407-409 were NOT run, per the spec's explicit
honest-stop instruction ("if license_rule fails on (a) or (b): DIAGNOSTIC KILL... do NOT run
policy cells 407-409"). This is a valid, complete, pre-registered stopping point, not partial work.

Dev window: sessions <= 2026-05-31 (leg_daily.csv: 2022-01-03..2026-05-29,
1139 sessions). No data >= 2026-08-01 (VIRGIN floor) touched anywhere in this run.

## 406 diagnostic result (FACT -- out/leg_asymmetry.csv, out/license_decision.json)

Reused, not recomputed: SMV2Z's exact 23 trigger-week -> 23 receiver(t+1)-week flag set, pulled
directly from `runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv` ('scaled'==True week_keys) and
cross-checked byte-for-byte against SMV2Z's own `run_log.txt` printed `trigger_week_keys` line
(PASS, 23/23 identical): [202411, 202417, 202437, 202440, 202452, 202502, 202507, 202513, 202514, 202515, 202526, 202535, 202542, 202545, 202547, 202551, 202552, 202607, 202609, 202612, 202614, 202618, 202620]

Data: `runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv` columns leg_solar/leg_bmom/twin (leg_solar +
leg_bmom - twin max abs error 9.09e-13, confirming the legs rebuild the twin exactly, as
SMV2Q itself documents).

| leg | vol\_flagged | vol\_unflagged | vol\_ratio | sharpe\_flagged | sharpe\_all | sharpe\_drop | n\_flagged |
|---|---|---|---|---|---|---|---|
| leg_solar | 2459.2 | 1399.6 | 1.7571 | 1.9545 | 0.8754 | -1.0791 | 113 |
| leg_bmom  | 1572.5 | 931.7 | 1.6877 | 1.7656 | 1.1378 | -0.6278 | 113 |

Contribution share of flagged-week twin PnL (context, per spec 406's request; twin != champion
'nt' exactly, corr 0.9992 per SMV2M, so this is a plausibility check on SMV2Z's 30.3%-of-total-nt
figure, not a reproduction of it): leg_solar 63.4%, leg_bmom 36.6% of
flagged-week twin PnL; twin's own flagged-week PnL is 30.1% of twin's
total dev PnL (SMV2Z's nt-based figure was 30.3%).

**license_rule (ALL required to proceed; per spec, ANY of (a)/(b) failing is a DIAGNOSTIC KILL)**:
- (a) asymmetry: max(vol_ratio_solar, vol_ratio_bmom) / min(...) = 1.0411 (need >= 1.3) ->
  **FAIL**
- (b) stable-leg (leg_bmom) not materially worse in flagged weeks: sharpe_all=1.1378,
  sharpe_flagged=1.7656, drop=-0.6278, sign_flip=False
  (rule: materially_worse := sign_flip(+->-) OR drop>1.0, pre-committed and applied mechanically,
  since the spec text leaves the numeric threshold for "materially worse" open) ->
  **PASS**
- (c) power floor: n_flagged_solar=113, n_flagged_bmom=113
  (need >=15 each) -> **PASS**

**Why the mechanism does not exist here (INFERENCE, grounded in the FACTs above)**:
- gate(a) FAILED: asymmetry ratio 1.0411 < 1.3 required -- the two legs do NOT respond asymmetrically to the flag (vol_ratio_solar=1.7571, vol_ratio_bmom=1.6877); both legs scale up together, consistent with SMV2Q's established finding (Q10) that joint-loss/flagged states are a WHIPSAW state where both engines move together, not a state where one engine misbehaves and the other stays calm.

This is consistent with the campaign's own prior finding (SMV2Q_DIAGNOSTICS Q10, FACT): the
flagged (sigma460-top-tercile + ER150-top-tercile) state is characterized as "both sides lose
simultaneously... whipsaw, not directional error" (mtm_short t=-7.5, mtm_long t=-6.7 vs non-flagged
baseline). A mix-SHIFT mechanism requires the two legs to respond asymmetrically to the flag so
that de-weighting one and up-weighting the other has a real basis; a state that hits both legs in
the same whipsaw way at the same time gives a mix-shift nothing to work with -- reallocating weight
between two legs that misbehave together cannot help either, exactly as the spec's own framing
anticipated ("if both legs scale up together, a mix-shift cannot help either, and this spec must
say so and stop").

## Disposition (per spec `kill:` clause)

406 fails -> spec stops here (documented). The mix-shift mechanism itself (not just this specific
weight grid) is now closed on this flag definition, pending a genuinely different mechanism. This
does NOT reopen the parent SMV2Z finding (blanket exposure-cut during flagged weeks FAILED
because those weeks hold 30.3% of total net PnL on 9.9% of days) -- SMV2AA tested a structurally
different response to that same finding and also does not survive its own prerequisite gate.

## Outputs
`out/leg_asymmetry.csv`, `out/license_decision.json`, `out/run_log.txt`, this REPORT.md.
Not produced (per spec, correctly): `out/policy_cells.csv`, `out/placebo.csv`, `out/chronology.csv`
-- these are licensed-only outputs and 406 did not license this run.
