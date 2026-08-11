# _archive — superseded top-level docs, moved not deleted

Created 2026-08-11 during a repo-wide cleanup audit. Every file here is a plain `git mv` from
`research/system_master/` — zero content edits, full git history preserved (`git log --follow
<path>` reaches every prior commit). Nothing was deleted; this folder exists because a growing
number of top-level docs in that directory had been superseded by later work but were never moved
out of the way, making it hard to tell current truth from historical snapshots at a glance.

**For current state, read these instead** (all still live at `research/system_master/`):
`CURRENT_TRUTH.md`, `ACTIVE_RESEARCH_QUEUE.md`, `RESEARCH_FRONTIER.md`,
`FINAL_OWNER_DECISION_20260809.md`, `BASELINE_MODELS.md` (stub pointing to repo-root
`/BASELINE_MODELS.md`), `SUPERSEDED_CONCLUSIONS.md`, `KNOWN_ERRORS_AND_CORRECTIONS.md`.

## What's here and why each was archived

| File | Why archived | Current successor |
|---|---|---|
| `CLAIM_LEDGER.md` | Stale since Wave 4-8 per `FINAL_CAMPAIGN_BASELINE.md` | `CURRENT_TRUTH.md` |
| `CURRENT_STATE.md` | Named PORT_TILT_532 as winner; retired by `SUPERSEDED_CONCLUSIONS.md` row 1 | `CURRENT_TRUTH.md` |
| `FINAL_NQ_SYSTEM.md` | Same PORT_TILT_532 claim, same supersession | `DAY_ONLY_FRONTIER.md`, `SUPERSEDED_CONCLUSIONS.md` |
| `FINAL_NQ_SYSTEM_RED_TEAM.md` | Adversarial review of the above; archived as a pair | — |
| `FINAL_PACKAGE_SPEC.md` | Source of the now-retired "B1 is a CORE leg" claim | `B1_ABLATION.md` |
| `HYPOTHESIS_LEDGER.md` | Never updated past initial registration (SM01-08 stuck "pending") | `CURRENT_TRUTH.md` |
| `LEVERAGE_FRONTIER.md` | Superseded by its own sibling doc's stated correction | `LEVERAGE_ROBUSTNESS.md` |
| `NEXT_HANDOFF.md` | Wave-14/15 "resume here" snapshot, long since resolved | `FINAL_OWNER_DECISION_20260809.md`, `CURRENT_TRUTH.md` |
| `NEXT_RESEARCH_QUEUE.md` | 2026-08-08 queue; role now filled by the rolling queue | `ACTIVE_RESEARCH_QUEUE.md` |
| `NINJATRADER_MASTER_SPEC.md` | Documents pre-C4-compliance-fix architecture | repo-root `/BASELINE_MODELS.md` |
| `NINJATRADER_PARITY.md` | Own manifest entry: pre-C4-fix objects only | `runs/V1R4_NT8_PARITY/`, `/BASELINE_MODELS.md` |
| `RESEARCH_INDEX.md` | Self-disclosed staleness banner (unedited since wave-1) | `CURRENT_TRUTH.md` |
| `OWNER_DIRECTIVE_V4_RECONCILIATION.md` | Point-in-time 2026-08-08 planning snapshot | `CURRENT_TRUTH.md` |
| `WAVE1_RESULTS_RAW.md` | Orphaned raw transcript dump, zero inbound references | `ALPHA_THROUGHPUT.md` and siblings |
| `LITERATURE_SCOUT_20260809.md` | One-time scout; both hypotheses closed same wave | `RESEARCH_FRONTIER.md` |
| `COLD_NAVIGATION_TEST_20260809.md` | One-time completed verification test | — |
| `TOKEN_BUDGET_AUDIT_BEFORE.json` | One-time before/after snapshot, disclosed as approximate | — |
| `OWNER_DIRECTIVE_20260808.txt` (V1) | Superseded by V2/V4/V4.1 and later unsaved directive waves | (later waves not saved as files here) |
| `OWNER_DIRECTIVE_V2_20260808.txt` | Superseded by V4/V4.1 | — |
| `OWNER_DIRECTIVE_V4_20260808.txt` | Superseded by V4.1 same day | — |
| `OWNER_DIRECTIVE_V4_1_20260808.txt` | Last saved directive text; program has since run through MEGA PROMPT V5-V7 and Master Directive v2-v4, none saved as files | `CURRENT_TRUTH.md` wave headers |
| `FINAL_CAMPAIGN_BASELINE.md` | Named `SolarWaveSMMaster_v3` current; superseded same-day by the DEFECT-3 fix (`_v4`) | repo-root `/BASELINE_MODELS.md` |
| `REPO_CONSOLIDATION_MANIFEST.csv` | 2026-08-09 inventory snapshot, doesn't cover files added 2026-08-10+ | this cleanup pass |

**Known gap, not fixed by this cleanup:** `CURRENT_TRUTH.md`'s own wave headers reference several
owner-directive waves (MEGA PROMPT V5/V6/V7, Master Directive v2/v3/v4) that were apparently never
saved as files anywhere in this repo — only V1/V2/V4/V4.1 (all 2026-08-08) exist as committed text.
If verbatim directive preservation matters going forward, those later directives should be saved,
not just referenced by section number in prose.
