# REPO_CONSOLIDATION_20260827 — inventory, dispositions, deletion manifest

_Owner directive 2026-08-27 (operational reset §§4–14, 30–34) + the root/IA amendment (§§1–18).
Executed 2026-08-27. **One-time record. Do not append future cleanups here.**_

## 1. Guiding split

> **Historical evidence is not clutter. Operational duplication is clutter.**
> Nothing was deleted for being old. Files were moved **out of the bootstrap path**, not destroyed.

## 2. Root disposition table — executed

| file | words | disposition | destination |
|---|---|---|---|
| `README.md` | 857 | **REWRITE_ROOT** | landing page only, tiered read path |
| `CLAUDE.md` | 499 | **REWRITE_ROOT** | current agent bootstrap; no campaign-#1/#3 narrative |
| `AGENTS.md` | 66 | **REWRITE_ROOT** | 11-line pointer |
| `BASELINE_MODELS.md` | 6,108 | **MOVE_ARCHIVE** | `research/archive/campaign3_system_master/BASELINE_MODELS.md` |
| `MAP.md` | 1,589 | **MERGE_THEN_DELETE** | → `research/INDEX.md` (structure only, current) |
| `NEXT_HANDOFF_CAMPAIGN1_CLOSED.md` | 743 | **MOVE_ARCHIVE** | `research/archive/closed_handoffs/` |
| `OWNER_QUEUE.md` | 1,317 | **MOVE_CURRENT + PRUNE** | `research/operational/OWNER_QUEUE.md` |
| `RESEARCH_HANDOFF.md` | 2,658 | **MOVE_ARCHIVE** | `research/archive/closed_handoffs/RESEARCH_HANDOFF_20260818.md` |
| `STATE_OF_RESEARCH_20260818.md` | 1,497 | **MOVE_ARCHIVE** | `research/archive/state_snapshots/` |
| `reports/` (22 files) | — | **MOVE_ARCHIVE** | `research/archive/campaign1_solar_wave/reports/` |

**Nothing at root was deleted outright.** `MAP.md` is the only removal, and its current content was
merged into `research/INDEX.md` first.

## 3. Link-integrity check (§12), run before any move

- **`git grep` for every filename**: inbound references are 65 (`BASELINE_MODELS`), 56 (`MAP`),
  14 (`RESEARCH_HANDOFF`), 12 (`STATE_OF_RESEARCH`), 10 (`OWNER_QUEUE`), 3 (`NEXT_HANDOFF`).
- **Almost all are inside immutable `runs/*/REPORT.md` and closed-campaign docs.** Per §12 these are
  **not rewritten for cosmetics** — a historical report citing the path that existed when it was
  written is *correct*, and git history preserves that layout.
- **Code dependency: NONE.** Every `.py` hit is prose in a comment (verified by inspection; no code
  opens a root `.md`). Nothing to update or test.
- **Current-doc references repointed: 1** — `MONITORING_CALENDAR.md`'s pointer to
  `/BASELINE_MODELS.md` → `research/archive/campaign3_system_master/BASELINE_MODELS.md`.
- `research/system_master/BASELINE_MODELS.md` is a 222-byte pointer stub, **not** a duplicate of the
  44,599-byte root file. Left in place.

## 4. Deleted (regenerable, unreferenced)

| path | count | reason | source of truth |
|---|---|---|---|
| `**/__pycache__/` | 9 dirs | Python bytecode cache, already gitignored | the `.py` files |

**That is the entire deletion list.** A repo-wide sweep for `*.tmp`, `*.bak`, `*.stackdump`,
`Thumbs.db`, `desktop.ini` and zero-byte files returned **nothing**. The tree had **zero untracked
non-ignored files** before and after.

**Deliberately NOT deleted:** a handful of empty `out/` and `red_team/` directories inside immutable
run dirs. Git does not track empty directories, so they cost nothing, and removing one that a
generator expects would be a regression for zero benefit.

## 5. Large files — reviewed, nothing removed from git (§34)

Working tree: `research/` 3.7 GB, `runs/` 2.1 GB, `.git/` 1.1 GB. **The bulk is raw data that is
already gitignored and must never be deleted** — `research/scalping_lab/substrate/` (3.1 GB of
tick/minute parquet), `probe_ticks.csv` exports, and the 58 MB `xm_reference_bars.csv`.

**Largest tracked files are ~0.19 MB `.cs` sources.** There is no oversized committed artifact to
extract. **No file was removed from git to save space** — §34's "do not optimize repo size at the
expense of reproducibility" governs.

**New gitignore entries** (regenerable, 200 MB+ each, fully reproducible from the run's own
`spec.yaml`): `runs/WE_XM_PARITY_20260827/out/we_xm_*.csv`, `runs/*/out/we_p1pct_*.csv`. The
committed artifact is the **per-session** reduction (`nt8_decisions*.csv`), not the per-bar ledger.

## 6. NT8 active strategy set (§§12–14, 31)

**Before: 25 strategy sources. After: 8** (5 of which are NT8's own `@Sample*` built-ins).

| disposition | class |
|---|---|
| **KEEP ACTIVE** | `WeeklyEdgeP1PCT_v1` — executable single baseline |
| **KEEP ACTIVE** | `WeeklyEdgeXMConflict_v2` — active portfolio component |
| **KEEP ACTIVE** | `WeeklyEdgeP1_v3` — required comparator (§38) |
| **KEEP** | `@SampleAtmStrategy`, `@SampleMACrossOver`, `@SampleMultiInstrument`, `@SampleMultiTimeFrame`, `@Strategy` — NT8 built-ins, not ours |
| **ARCHIVED (17)** | `SolarWaveSMMaster_v4`, `SolarWaveSMMaster_Canonical_v1`, `SolarWaveOneContractNQ_v5`, `SolarWaveOneContractNQ_v6_R2CONFIRM`, `SolarWaveOneContractNQ_B1_v1`, `SolarWaveOneContractNQ_Canonical_v1`, `SolarWaveOneContractMNQ_v5`, `SolarWaveOneContractMNQ_B1_v1`, `SolarWaveOneContractMNQ_Canonical_v1`, `SolarWaveRKReplicaV0`, `OriginalTraderSolarCAND2_v2`, `SWMinuteExport_v1`, `SWScalpTickExport_v3`, `W18CompileTrigger`, `WeeklyEdgeP1_v1`, `WeeklyEdgeP1_v2`, `WeeklyEdgeXMConflict_v1` |

**Archive location:** `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\_archived_strategies\` —
deliberately **outside** `bin/Custom`, so NT8 does not auto-compile it. **Moved, not deleted**, and
fully reversible.

**Every archived class was verified to have a preserved repo source before the move.** The single
exception, `W18CompileTrigger` (797 bytes, a debug compile-trigger stub with no repo copy and no
research content), was moved rather than deleted for exactly that reason.

### ⚠️ §13 — stale compiled types, measured rather than assumed

**A probe after the removals showed `WeeklyEdgeXMConflict_v1` STILL RESOLVING** from
`NinjaTrader.Custom.dll` with its `.cs` gone. **NT8 rebuilds on file ADD, not on file REMOVE.**

A rebuild was then forced through the supported path — writing one transient strategy
(`WeRebuildTrigger_v1`), confirming it resolved, then removing it. **No DLL was deleted or touched
manually**, per §13.

> **Residual, stated plainly:** NT8 cannot unload a type already loaded into its AppDomain, so
> classes resolved earlier in this session may remain resolvable **until NT8 is next restarted**.
> This is a documented platform limitation, not a repo state. It is **hygiene, not risk**: the
> sources are archived, and `EXECUTION_MANIFEST.md` names the only three strategies that may be run.
> An ordinary NT8 restart clears it; no owner action is required for correctness.

## 7. Archive structure created

```
research/archive/
    campaign1_solar_wave/reports/          22 campaign-#1 report files
    campaign3_system_master/BASELINE_MODELS.md
    state_snapshots/STATE_OF_RESEARCH_20260818.md
    closed_handoffs/RESEARCH_HANDOFF_20260818.md
                    NEXT_HANDOFF_CAMPAIGN1_CLOSED.md
```

**Whole research trees were NOT mechanically relocated.** Closed campaigns whose existing locations
are already coherent (`research/system_master/`, `research/scalping_lab/`,
`research/original_trader_reconstruction/`, `research/0N_*`) stayed where they are — §11 warns
against busywork. `research/INDEX.md` names them and flags that their "current" docs describe
campaigns that have ended.

## 8. Documentation duplication audit (§16)

| fact | authoritative source | who else states it |
|---|---|---|
| active campaign | `README.md` | `CLAUDE.md`, `AGENTS.md` — one line each, as pointers |
| research baselines A/B + economics | **`CURRENT_BASELINE.md` §0** | `README.md` names the *objects* only, no numbers |
| executable baselines C/D | **`EXECUTION_MANIFEST.md`** | `CURRENT_BASELINE.md` §0 links; `README.md` names objects |
| operating rules | **`CLAUDE.md`** | nowhere else |
| repo structure | **`research/INDEX.md`** | nowhere else |
| open owner actions | **`OWNER_QUEUE.md`** | `README.md` links |
| data seals | **`LOCKED_FORWARD.md`** | `CLAUDE.md` §5 states the two dates (safety-critical, deliberate) |
| DOM pause | **`DOM_PAUSE_CLEANUP_20260812.md`** | `CLAUDE.md` §1 (safety-critical, deliberate) |

**Before, six documents independently explained current state** (README, MAP, STATE_OF_RESEARCH,
RESEARCH_HANDOFF, CLAUDE, CURRENT_BASELINE). **After, five logical roles with no overlap**, and the
only deliberate duplications are two safety facts kept in `CLAUDE.md` so an agent cannot miss them.

## 9. Before / after (§18)

| | before | after |
|---|---|---|
| **root markdown files** | **9** | **3** |
| root markdown bytes / words | 118,459 / 15,334 | 12,398 / 1,585 |
| **bootstrap set** | README + MAP + STATE_OF_RESEARCH + RESEARCH_HANDOFF + CLAUDE + CURRENT_BASELINE | **README + CLAUDE + CURRENT_BASELINE** |
| bootstrap words | ~10,600 (~14k tokens) | **~4,900 (~6.5k tokens)** |
| NT8 active strategies | 25 | **8** (3 ours) |
| root directories | 5 (`reports`, `research`, `research_sdk`, `runs`, `src`) | **4** |

`CURRENT_BASELINE.md` was itself consolidated from 31,504 to ~14,800 bytes — the per-wave changelog
was removed and replaced with links to the `runs/WE_W*/REPORT.md` files that already hold it.

## 10. What deliberately remains (§7)

The full correction record is untouched and must stay: **W108's withdrawn interpretation, W115's
defect evidence, W116's null defect, W118's gate defect (including the preserved
`reversal_DEFECTIVE_gate_at_1200.txt`), W121's half-implemented falsifier, the seven dead fade
families, the turnover family, W122's cross-market null, W123's tail asymmetry** — and, added today,
**`WeeklyEdgeXMConflict_v1`**, which failed its parity gate and is retained precisely because it is
the version that found the early-close defect.
