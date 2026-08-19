# Registry map — where experiment registration actually lives (written 2026-08-18)

This repo has run four campaigns; registration moved twice. Reading any single file as "the
registry" undercounts. The map:

| Era | Registry of record | Coverage |
|---|---|---|
| Campaign #1/#2 (Solar + audit, → 2026-08-07) | `experiments.yaml` (15 entries, ends DAY_MARGIN_VARIANT) + `tested_configs.csv` seq 1–284 + `tested_configs_backfill.csv` (seq 91–229, reconstructed, `reconstructed=yes`) | Waves through DM01; the Wave-1c–3 lapse is disclosed in `REGISTRY_GAP_NOTE.md` |
| Campaign #3 early (SYSTEM_MASTER, 2026-08-08→08-09) | `tested_configs.csv` seq 285–498 (**column drift from seq 320**: the experiment tag sits in the `date` column and the date moves last — parse positionally per row era, or use `RUNS_INDEX.csv`) | SM/SMV2 series through the 2026-08-09 SYN stop-condition row |
| Campaign #3 since 2026-08-09 | **`../system_master/TESTING_LEDGER.csv`** (family-level rows, no seq numbers) | Structural-invariance waves, EQV, DOM01, DATA03, HTFMECH01 (catch-up row 2026-08-14/18) |
| Campaign #4 (Scalping Lab) | `../scalping_lab/registry/tested_configs.csv` (S1–S35) + `hypothesis_ledger.csv` | Complete; see that directory's own `README.md` |

Trial-count bracket for multiple-testing math: **499–653** (`HASH01_BEHAVIORAL_POLICY_REGISTRY/
REPORT.md` §1.3), superseding this directory's older 229–383 bracket; TESTING_LEDGER family rows
are NOT yet re-expressed at per-config level (disclosed, open).

Machine-readable dir-level index of all `runs/` directories: **`RUNS_INDEX.csv`** (generated
2026-08-18; best-effort era classification, see its header comment).

Preregistration enforcement: `research_sdk/prereg_guard.py` (spec commit must strictly precede
result commit). Four historical spec-only dirs (`B01C_ORB_FAIL`, `B02_GAP_ESCALATION`,
`C01T1_EXPOSURE`, `C01T1_ML`) have in-dir `STATUS.md` pointers to their off-dir outcomes.
