# Evidence map — POST_CAMPAIGN_AUDIT_01

_2026-08-07. Every audit claim → its artifact chain. Branch `post_campaign_audit`
from `e5079e1` (campaign final HEAD). Constitution: `research/Research_Thesis.txt`
(committed 3bc5a3a, before any audit execution)._

| # | Claim | Evidence chain |
|---|---|---|
| 1 | Repository was PUBLIC again on 2026-08-07; set PRIVATE by this audit | `VENDOR_BINARY_REMEDIATION.md` §2 (gh queries logged there) |
| 2 | Vendor files were still tracked at HEAD; untracked at tip | commit `1f169ae` (removals + .gitignore guard); files intact on disk |
| 3 | Engine/data determinism | `runs/AUDIT_GATE_R01`, `R02` (specs at `b811a21` pre-execution; payloads + runlib ingests; five frozen numbers exact, vendor and vendor-free) |
| 4 | R5 members reproduce fill-by-fill | specs `b811a21`/`124af95` → `runs/AUDIT02_V3_SWEEP{,_B}` ledgers → `v3_reproduction_diff.csv` (13/13 EXACT) → `R5_REPRODUCTION.md` |
| 5 | README recipe StartUp defect | A-arm failure + first-fill signatures + vm30 dollar-exact gap decomposition (`R5_REPRODUCTION.md` §2) |
| 6 | Committed V4 evidence reproduces; published V3/V4 comparison was StartUp-confounded | `runs/AUDIT02_V4_SWEEP_C` (13/13 EXACT) + first-fill signature match + `V3_V4_VERDICT.md` |
| 7 | Clean tick-snap comparison: paths NOT_EQUIVALENT, ensembles similar | `runs/AUDIT02_V4_SWEEP_B` + `v3_v4_trade_diff.csv`, `v3_v4_daily_diff.csv` + driver `audit02_v3v4.py` |
| 8 | Bar series = engine series; fill semantics (open ±1 tick capped by range; session-close at close) | spec `2a125a4` → `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` → validation in AUDIT-02 commit `f865dc4` message + `audit_mtm.py` |
| 9 | session_REALIZED == session_TRUE_MTM for all 34 members | `audit03_mtm_run.py` assertions (run logged) → `mtm_reconciliation_metrics.csv` → `MTM_RECONCILIATION.md` |
| 10 | Bar-level intraday DD deeper than published dailies | same chain, `bar_level_TRUE_MTM` rows |
| 11 | MNQ Lifetime commission $0.65/side | spec `2a125a4` → `runs/AUDIT04_MNQ_PROBE/raw_payload.json` (704 fills, constant) |
| 12 | R5-E10 executable passes preregistered gates; R4 discrete fails | gates in thesis AUDIT-04 §9 (committed `3bc5a3a`) → `audit04_executable.py`/`audit04_run.py` → `executable_ensemble_metrics.csv`, `netting_cost_attribution.csv`, `position_rounding_diagnostics.csv` → `EXECUTABLE_ENSEMBLE.md` |
| 13 | Slip-2 retains 87.4% (claim correction); paths slippage-invariant | spec `2a125a4` → `runs/AUDIT05_V3_SLIP2/` ledgers + `sweep_summary.json` |
| 14 | No fill-resolution artifact; tails fill-model-independent | spec `2a125a4` → `runs/AUDIT05_V3_HIGHRES/` ledgers → `FILL_AND_TAIL_AUDIT.md` |
| 15 | Registry reconciliation 90/229/316/383; strict-relabel 295–335 | `reconstructed_trials.csv` (computed totals), `REGISTRY_GAP_ASSESSMENT.md`, `candidate_lineage.json` |
| 16 | Zero new R1 trials consumed by the audit | every audit spec carries `counts_as_trial: no` with reason; the E-variant menu and the E10 designation are recorded as a design-choice event in `SECOND_RED_TEAM.md` §3, with micro-choice sensitivity in `e10_sensitivity.csv` |
| 16b | Audit rerun evidence integrity | all 72 rerun ledgers/exports/payloads SHA-256-manifested in `audit_evidence_hashes.json` and committed; C-arm certificate `v4c_reproduction_diff.csv` |
| 17 | Day-margin 16:45 ET cutoff verified (operational subproject) | `research/operational/day_margin_variant/MARGIN_RULES.md` (official-source citations) |

Chronology guarantee: every `runs/AUDIT*/spec.yaml` is committed in a parent
commit of the commit that first contains its results (verify:
`git log --oneline --follow -- runs/<id>/spec.yaml`).
