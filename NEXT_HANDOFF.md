# NEXT_HANDOFF — POST_CAMPAIGN_AUDIT_01 + post-audit waves complete; CONVERGENCE

_2026-08-07. Superseding note: after the audit passed, three further preregistered
waves ran to completion the same day — WAVE B01 (Family B: all arms negative, 3
trials), PORTABILITY-01 (0/3: YM/RTY/CL all negative → NQ-specific alpha
confirmed, 39 trials), DM01 (day-margin variant measured: 95.2% net retention,
13 trials). The campaign has reached formal convergence
(`research/CAMPAIGN_STATE.md` §15). Final package: `reports/FINAL_*.md` +
`reports/DAY_MARGIN_VARIANT.md`. Sections below describe the audit phase._

## A. Git

- Branch: `post_campaign_audit`, created from campaign HEAD `e5079e1`
  (`research-campaign` untouched — verified diff-empty over all campaign evidence).
- Constitution v2 committed at `3bc5a3a` before any execution; every audit run
  preregistered (`runs/AUDIT*/spec.yaml`, `runs/B01A_BARS_1M/spec.yaml`) in a
  commit preceding its execution (chronology adversarially verified).
- All audit evidence committed with SHA-256 manifests
  (`research/audit/audit_evidence_hashes.json`).

## B. Task scope

POST_CAMPAIGN_AUDIT_01 executed in full: registry reconstruction, R5/V4 exact
re-execution, V3/V4 verdict, true-MTM reconciliation, executable ensembles
(E0/E1/E13/E10/E20/E3 both families), MNQ commission verification, slip-2 stress,
High-fill-resolution audit, tail-day inspection, finalist requalification,
independent second red team (4 lenses), day-margin rules verification.
**Zero new R1 trials.**

## C. Files changed (curated)

- `research/audit/` — 20 artifacts (verdicts, certificates, metrics, hashes).
- `runs/AUDIT_GATE_R01,R02, AUDIT02_*, AUDIT03_BARS, AUDIT04_MNQ_PROBE,
  AUDIT05_*, B01A_BARS_1M` — specs + evidence.
- `src/analytics/audit*.py` (6 new modules), `src/ninjascript/AuditBarExport1.cs`.
- Corrections: `src/ninjascript/README.md` (StartUp), `reports/final_system_design.md`
  §7 (StartUp), `research/CAMPAIGN_STATE.md` §14, `research/frontier.yaml`,
  `research/registry/experiments.yaml` (append), `.gitignore` (vendor guard).
- `research/04_complementary_family/B01_WAVE_SPEC.md` (Wave B01 preregistration).
- `research/operational/day_margin_variant/MARGIN_RULES.md`.

## D. Validation

Determinism gates exact (5/5 frozen numbers, vendor and vendor-free); 13/13 V3 +
13/13 V4 fill-by-fill certificates; MTM identity 0.000000 for 34 members; red
team recomputed every headline independently — all exact; remediations applied
same-day (see `research/audit/SECOND_RED_TEAM.md` §2).

## E. Research results

See `research/audit/AUDIT_EXECUTIVE.md`. Headlines: R5 reproduced exactly
(recipe StartUp defect fixed); published V3/V4 comparison was StartUp-confounded
(conclusion survives clean rerun); executable R5-E10 passes preregistered gates
(margin thin, robust to micro-choices); all discrete R4 variants fail; intraday
DD deeper than published dailies; slip-2 retains 87.4%; no fill artifact; MNQ
commission $0.65/side verified.

## F. Explicit non-runs

No new Solar parameter search; no Type-2/3/wave/anchor/exit research; no
portfolio weighting or vol targeting; no leverage; no live/Sim/paper/shadow
activity; no vendor-binary access; no history rewrite; no Playback runs
(judged nil-information for market-only orders — disclosed in
FILL_AND_TAIL_AUDIT.md §4).

## G. Risks / caveats

1. **RESOLVED (2026-08-07, owner-directed)**: vendor blob erased from local history
   via git filter-repo (verified 0 vendor objects; audit-tip tree bit-identical;
   SHA map at `research/audit/history_rewrite_commit_map.txt`). Owner closed the
   governance track (risk accepted — assembly unusable without a registration key).
   Remaining mechanical step: owner force-pushes both rewritten branches. Record:
   `research/audit/VENDOR_BINARY_REMEDIATION.md` §7. Old doc SHAs are historical
   names — resolve via the commit map.
2. E10's gate margin is thin (0.003–0.012); re-verify MNQ commissions if the
   broker plan changes.
3. POST_AUDIT_TRANSITION's "compare Family B against BOTH executable R4 and R5"
   is satisfiable only as: executable R5-E10 primary + **theoretical** R4
   secondary, because executable R4 failed its gates. This interpretation is
   preregistered in B01_WAVE_SPEC.md; flag if you want a different resolution.
4. Tick-level intraday excursion unmeasured (3-minute bar-close bound).
5. All standing campaign caveats (no OOS, ES failure, tail concentration, DSR
   inconclusive) unchanged.

## H. Recommended next step (post-convergence: all decisions are the owner's)

1. **Force-push the rewritten branches** (the one step left of the vendor track,
   now otherwise CLOSED — §G.1):
   `git push --force origin research-campaign post_campaign_audit`
   (do not fetch/pull first).
2. If the program resumes: the only research doors left open are (a) a
   locked-forward freeze of R5-E10 with quarterly overshoot-r monitoring
   (MONITOR-01, free), (b) a genuinely new Family-B event definition (the
   falsified ones may not be re-tuned), (c) a NinjaScript master-strategy
   implementation of E10 with engine-level validation against the audited
   simulator. None may start without a new explicit instruction.
