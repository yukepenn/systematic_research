# PROTECTED_EVIDENCE_BUDGET

**Date:** 2026-08-10. Reconstructed directly from machine artifacts per Master Directive v4/
next-phase §0/§6 ("do not trust prose numbers — reconstruct from manifests"). Every count below
was recomputed in this session from the files listed, not copied from prior REPORT.md prose.

## Repo/HEAD state at reconstruction time

```
HEAD            = 04e4c44a0a01929b69f560ffa14dee4e023281a2
origin/main     = 04e4c44a0a01929b69f560ffa14dee4e023281a2   (in sync, verified via git ls-remote)
working tree    = clean (git status --short, only untracked scratch/output dirs pre-existing
                  from prior sessions — no uncommitted tracked changes)
```

## Session universe reconciliation

| Set | Count | Source file | SHA-256 |
|---|---:|---|---|
| Tick+BBO development window | 208 | `runs/W5_PROTECTED_CONFIRMATION/manifest_work/dev_window_208_dates.txt` | `85808bf6...331ed7` |
| Discovery subset (Tier-0) | 40 | `runs/W5_PROTECTED_CONFIRMATION/manifest_work/discovery_40_dates.txt` | `be999e44...2424c4` |
| Internal confirmation pool | 168 | `runs/W5_PROTECTED_CONFIRMATION/manifest_work/confirmation_pool_168_dates.txt` | `d3ce41fb...68ebcb` |
| Batch 1 consumed (this campaign) | 8 | `runs/W5_PROTECTED_CONFIRMATION/manifest_work/batch1_export_sessions.txt` | `c4d411b2...314c7b` |

Identity check: `208 − 40 = 168` ✓ (exact, recomputed via Python set subtraction, not `comm`).
`8 ⊂ 168` ✓ (all 8 batch-1 dates are members of the 168-pool set).

## Metadata-only eligibility manifest (168-pool, zero outcome values read)

Source: `runs/W5_PROTECTED_CONFIRMATION/ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`
(SHA-256 `3a8beed0...47cc1c6ff70`), file-existence/count checks only.

| State | Count | Definition |
|---|---:|---|
| `eligible_for_tick_bbo_confirmation=True` (both Last+BBO cached) | 52 | Has local `.ncd` for both Last and Bid/Ask |
| Last-only (Last cached, no BBO) | 116 | Would need a fresh NT8 export before any BBO-dependent test |
| Neither cached | 0 | — |
| **Total** | **168** | ties out exactly |

Contract-month distribution among the 52 eligible: `NQ 12-25`=16, `NQ 06-26`=16, `NQ 03-26`=13,
`NQ 09-25`=7.

## Consumption ledger — per-session state (one state each, no overlaps)

| State | Count | Detail |
|---|---:|---|
| `DISCOVERY_CONSUMED` | 40 | Tier-0 discovery set. Of these, 37 have usable RTH Bid/Ask (3 — `20250811`, `20250924`, `20260430` — have zero RTH BBO and are excluded from every BBO-dependent diagnostic; still consumed for selection-contamination purposes). |
| `CONFIRMATION_CONSUMED` | 8 | Batch 1, W5_PROTECTED_CONFIRMATION (`2026-08-10`): `20250819, 20250912, 20251028, 20251125, 20260217, 20260302, 20260422, 20260512`. Of these, 6 have usable RTH Bid/Ask (`20251125` and `20260512` have zero RTH BBO in the actual export, verified directly from `decision_outcomes_CONFIRM.parquet.sess_tag.unique()` = 6 distinct tags). All 8 are within the 52-eligible set. |
| `PROTECTED_UNTOUCHED` (eligible, cached, never opened) | 44 | `52 − 8` |
| `PROTECTED_UNTOUCHED` (pool member, not yet locally cached — Last-only or would need export) | 116 | Would require a fresh NT8 export before any BBO-dependent use |
| `PROTECTED_UNTOUCHED` total | **160** | `168 − 8`, matches CONTAMINATION_LEDGER.md's own figure exactly |
| `GLOBAL_FORWARD_VIRGIN` | — (not date-bounded here) | Everything `>= 2026-08-01`, per `research/operational/LOCKED_FORWARD.md` and CONTAMINATION_LEDGER.md's standing seal. Dominates every other rule in this document. Unaffected by AMENDMENT_3 status either way. |
| `DATA_UNUSABLE` | 3 (subset of DISCOVERY_CONSUMED) | `20250811, 20250924, 20260430` — zero RTH BBO, documented since Wave 4/U9B. |

Reconciliation: `40 (discovery) + 168 (pool) = 208 (dev window)` ✓. Within the pool:
`8 (confirmation-consumed) + 160 (protected-untouched) = 168` ✓. Within protected-untouched:
`44 (eligible-cached-untouched) + 116 (not-locally-cached) = 160` ✓.

## What this means for the current research phase

- Per governance (CONTAMINATION_LEDGER.md, AMENDMENT_3), the 8 `CONFIRMATION_CONSUMED` sessions
  are burned **only** for the three specific constructions already tested against them (AUCTION01
  D4 diagnostic, AUCTION02 Product-A rate-limiter policy, FLOW01 PRE_EXIT). They remain usable for
  genuinely different future hypotheses (e.g. a new AUCTION03 mechanism never tested against them).
- Mechanism-decomposition work (AUCTION03) proceeds on **already-consumed data only** — the 37
  BBO-usable discovery sessions (`runs/AUCTION01_VALUE_STATE/out/decision_outcomes.parquet`,
  `runs/AUCTION02_ACTION_RELEVANCE/out/action_substrate.parquet`) plus the 6 BBO-usable
  confirmation sessions (`runs/W5_PROTECTED_CONFIRMATION/results/out/*_CONFIRM.parquet`). **No
  session outside this 43-session union is read for this phase.**
- Any future opening of additional protected sessions requires a new frozen preregistration bundle
  (per the standing AMENDMENT_3 protocol) — not performed in this document, not performed until an
  AUCTION03 candidate mechanism is frozen.
- `>= 2026-08-01` is untouched and will remain untouched regardless of any AMENDMENT_3 activity.

*Reproduce: session-set arithmetic and hashes recomputed via `python3`/`sha256sum` directly on the
files listed above; commands available in this session's shell history, not re-serialized here
since every input file already carries its own hash for exact verification.*
