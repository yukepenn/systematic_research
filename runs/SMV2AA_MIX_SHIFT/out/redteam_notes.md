# SMV2AA_MIX_SHIFT — Statistical Red-Team Notes

**Track**: SMV2AA_MIX_SHIFT (seq 406–409). **Verdict: CONFIRMED.**

## Scope

406 is a mandatory diagnostic gate (leg-asymmetry test on Solar vs B-MOM during SMV2Z's
23 sigma460+ER150-flagged weeks); 407–409 are the conditional mix-shift policy cells,
licensed only if 406 passes. This review checks the diagnostic's letter-exactness against
`spec.yaml`, independently re-derives the flagged week-set and every load-bearing number
from `runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv` and `runs/SMV2Z_VIABILITY_POLICY/out/`
(not from `smv2aa.py`'s own code), and confirms 407–409 were genuinely not executed.

## 1. Spec letter-exactness

- `spec.yaml` in the run dir diffs byte-identical against the version committed at `f6fb7d1`
  (`git diff f6fb7d1 -- runs/SMV2AA_MIX_SHIFT/spec.yaml` → empty). Frozen-spec requirement holds.
- Gate (a) threshold: spec says `>= 1.3`; code and REPORT.md apply `>= 1.3` verbatim. No
  threshold was moved.
- Gate (b): the spec deliberately leaves "materially worse" numerically undefined. The
  executor adopted `sign_flip(+→−) OR (sharpe_all − sharpe_flagged) > 1.0` and stated this
  explicitly, up front, as a pre-committed mechanical rule (not tuned post-hoc). Critically,
  **this choice is moot to the final verdict**: gate (a) fails decisively on its own (1.041 vs
  required 1.3), and per spec text ("if license_rule fails on (a) or (b)") either failure alone
  kills the license — so there was no result-dependent incentive to pick a lenient or strict
  gate-(b) rule. Independently, gate (b)'s actual numbers are not even close to a judgment
  call: the stable leg's flagged-week Sharpe (1.7656) is *higher* than its unconditional
  Sharpe (1.1378), i.e. `drop = -0.628` (an improvement, not a degradation) — this passes gate
  (b) under essentially any non-perverse definition of "materially worse."
- Gate (c): spec says `N >= 15` per leg; both legs report N=113 (23 weeks × avg ~4.9
  trading days/week). Matches.
- LICENSED = gate_a AND gate_b AND gate_c = False AND True AND True = **False**. Correctly
  computed and correctly reported.
- Policy cells 407–409 genuinely NOT run: confirmed by (i) absence of `policy_cells.csv`,
  `placebo.csv`, `chronology.csv` in `out/` (directory listing shows only
  `leg_asymmetry.csv`, `license_decision.json`, `run_log.txt`), (ii) `smv2aa.py` contains a
  hard `sys.exit(0)` immediately after writing the DIAGNOSTIC KILL REPORT.md, before any
  code that would construct `CELLS = [("A", ...), ("B", ...), ("C", ...)]` mix cells runs, and
  (iii) `run_log.txt`'s final line is the DIAGNOSTIC KILL message, not a "406 LICENSED —
  proceeding" message. Not run-and-hidden.

## 2. Flagged week-set identity vs SMV2Z's own 23 weeks

Independently re-read (not trusting `smv2aa.py`'s own assertion) directly from
`runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv` (`scaled==True` rows' `week_key`) and
separately parsed from `runs/SMV2Z_VIABILITY_POLICY/out/run_log.txt`'s
`trigger_week_keys=[...]` line:

```
policy_daily.csv-derived: [202411, 202417, 202437, 202440, 202452, 202502, 202507, 202513,
  202514, 202515, 202526, 202535, 202542, 202545, 202547, 202551, 202552, 202607, 202609,
  202612, 202614, 202618, 202620]   (n=23)
run_log.txt-derived:      identical, set-diff both directions = {} (empty)
```

Both independently match the 23 keys reported in this run's `license_decision.json` and
REPORT.md exactly (list-equality, not just count). `n_flagged_days` recomputed independently
against `leg_daily.csv`'s own ISO week key = 113, matching SMV2Z's champion-calendar
`scaled.sum()` = 113. Boundary week 202314 confirmed absent from the flagged set (verified
directly, not just asserted). **Week-set identity: CONFIRMED exact, not merely count-matched.**

## 3. Equal-vol reweight verification

N/A — 407–409 (which contain the equal-vol reweight mechanic) did not run, per §1. No
reweight claim exists in this run's outputs to verify.

## 4. Independent recomputation of load-bearing numbers

Rebuilt from raw `leg_daily.csv` + `policy_daily.csv` in a standalone script (own ISO-week
key, own flagged/unflagged split, own vol/mean/Sharpe formulas — no import of `smv2aa.py`):

| quantity | independently recomputed | claimed (license_decision.json) | match |
|---|---|---|---|
| leg_solar + leg_bmom − twin, max abs err | 9.094947e-13 | 9.095e-13 | exact |
| vol_ratio_solar (flagged/unflagged std) | 1.757055 | 1.757055 | exact |
| vol_ratio_bmom | 1.687701 | 1.687701 | exact |
| asymmetry_ratio (max/min) | 1.041094 | 1.041094 | exact |
| gate_a_pass | False | False | match |
| stable_leg | leg_bmom | leg_bmom | match |
| stable_leg sharpe_all / sharpe_flagged | 1.137765 / 1.765551 | 1.137765 / 1.765551 | exact |
| gate_b_pass | True | True | match |
| n_flagged (each leg) | 113 / 113 | 113 / 113 | exact |
| gate_c_pass | True | True | match |
| LICENSED | False | False | match |
| contribution_share_solar_of_flagged_twin_pnl | 0.633870 | 0.633870 | exact |
| contribution_share_bmom_of_flagged_twin_pnl | 0.366130 | 0.366130 | exact |
| twin_flagged_share_of_twin_total_pnl | 0.301057 | 0.301057 | exact |

15/15 fields match to full float precision. Sensitivity check: recomputing vol ratios with
population std (`ddof=0`) instead of the spec's implicit sample std (`ddof=1`) gives
asym_ratio = 1.0411 — same conclusion, gate (a) still fails, confirming the FAIL is not an
artifact of the ddof convention.

Cross-check of the SMV2Z-parent 30.3% figure: SMV2Z's own prior red-team notes
(`runs/SMV2Z_VIABILITY_POLICY/out/redteam_notes.md`, line 76) independently confirmed
30.252% ("exact" match to REPORT's "30.3%") on the champion `nt` curve. This run's `twin`-based
figure (30.11%) is close but explicitly and correctly labeled in REPORT.md as a plausibility
check, not a reproduction, citing the documented nt/twin correlation of 0.9992 — verified
against its source, `runs/SMV2M_MASTER_BUILD/REPORT.md` line 11 ("0.9992 dev, all days").

## 5. Lookahead / leakage scan

- The flagged week-set (trigger week *t* → receiver week *t+1*) was computed upstream by
  SMV2Z from a purely backward-looking sigma460/ER150 AND-gate and is reused verbatim here
  (not recomputed) — SMV2AA introduces no new signal-construction step, so it cannot
  introduce new lookahead into the flag itself.
- 406 is a descriptive/diagnostic partition of already-realized daily PnL into
  flagged/unflagged buckets to compute vol, mean, and Sharpe — this is retrospective
  analysis of history, not a forward-applied trading rule, so there is no live-decision
  lookahead to assess at this stage (that concern would attach only to 407–409's policy,
  which did not run).
- Dev/virgin boundary respected: `leg.index.max()` = 2026-05-29 ≤ DEV_END (2026-05-31) and
  `< VIRGIN_FLOOR` (2026-08-01); `policy_daily.csv["sess"].max()` = 2026-05-29, same bound.
  Both confirmed independently, not just via the script's own assertions.
- No use of the eventual 406 result to retroactively redefine the flag or reselect the
  week-set (the week-set was fixed by SMV2Z before this run existed).

## 6. Language / process discipline

- REPORT.md correctly labels the diagnostic table and gate pass/fail as **FACT**, and the
  "why the mechanism does not exist" causal narrative (tying to SMV2Q's Q10 whipsaw finding)
  as **INFERENCE**, consistent with campaign convention.
- "DIAGNOSTIC KILL" is an honest, pre-registered stopping point per the spec's own
  `kill:` clause — REPORT.md says so explicitly and does not overstate 406's result as a
  general negative on mix-shift ideas beyond "this flag definition."
- No BLOCKED language is used, and none was warranted — every required input file was
  present, VIRGIN floor was respected, and the run completed its designed scope (406 only).

## Hard-boundary / scope check

`git status --porcelain=v1 --untracked-files=all` shows exactly four new paths, all under
`runs/SMV2AA_MIX_SHIFT/`: `REPORT.md`, `out/leg_asymmetry.csv`, `out/license_decision.json`,
`out/run_log.txt`, `smv2aa.py`. `git diff --stat` (tracked files) is empty — nothing existing
was modified. `git log` shows no commit beyond the pre-existing spec-freeze at `f6fb7d1`
(one unrelated handoff-note commit `5d6b82c` follows it, not touching this run) — consistent
with "no git commands were run" for this execution. No CrossTrade/NinjaTrader tool use in any
artifact. No data ≥ 2026-08-01 referenced anywhere in `leg_daily.csv`, `policy_daily.csv`, or
the run's own asserted bounds.

## Overall

All five checks in the assignment pass: spec letter-exactness holds (with the one open
threshold in gate (b) shown to be outcome-irrelevant and non-borderline), the flagged
week-set is exactly identical to SMV2Z's (list-for-list, not just count), the equal-vol
reweight claim is not applicable (correctly not run), 15 independently recomputed
load-bearing numbers all match to full float precision, no lookahead/leakage found, and the
report's FACT/INFERENCE labeling and honest-kill language are accurate.

**CONFIRMED.**
