# research/INDEX.md — repository structure

_Structural map only. It does not restate current state; `CURRENT_BASELINE.md` and
`EXECUTION_MANIFEST.md` own that. Current 2026-08-27._

## Top level

| path | what |
|---|---|
| `research/weekly_edge/` | **campaign #7 — the only live campaign** |
| `research/operational/` | cross-campaign operational truth: execution manifest, owner queue, data seals, monitoring calendar |
| `research/archive/` | closed-campaign material pulled out of the bootstrap path |
| `runs/` | immutable experiment directories, one per run: `spec.yaml` + `REPORT.md` + `out/` |
| `src/` | campaign-#1/#3 Python and NinjaScript sources (historical) |
| `research_sdk/` | shared guards: `prereg_guard.py`, `session_boundary.py` |

## Campaign #7 — `research/weekly_edge/`

| file | role |
|---|---|
| `CURRENT_BASELINE.md` | **current research state** (authoritative) |
| `ninjascript/` | `WeeklyEdgeP1PCT_v1.cs`, `WeeklyEdgeXMConflict_v2.cs` (+ `_v1` superseded), `WeeklyEdgeP1_v1..v3.cs` comparators, `WeeklyEdgeBmom_v1.cs`, `WeeklyEdgeX9a_v1.cs` |
| `ninjascript/LIVE_READINESS.md` | NinjaScript design, risk limits, parity protocol |
| `ninjascript/reference/` | Python decision references for parity |
| `INFORMATION_COVERAGE_20260827.md` | information surfaces: measured / null / blocked |
| `MECHANISM_COVERAGE_20260826.md` | mechanisms closed and why |
| `DATA_CENSUS_20260826.md` | what data exists |
| `OPPORTUNITY_LANGUAGE.md` | **binding** vocabulary for ceiling figures |
| `src/run_we_w*.py` | one script per wave, W01 → W123 |
| `src/we_harness.py` (under `research/weekly_edge/`) | validation harness (7/7) |

Runs: `runs/WE_W<n>_<NAME>/` for waves, `runs/WE_*_PARITY_*/` for reconciliations,
`runs/DATAGATE_*/` for data-gate determinations.

## Operational — `research/operational/`

`EXECUTION_MANIFEST.md` (what is installed/compiled/certified) · `OWNER_QUEUE.md` (open owner
actions only) · `LOCKED_FORWARD.md` (data seals) · `MONITORING_CALENDAR.md` (scheduled forward
reads) · `REPO_CONSOLIDATION_20260827.md` (this cleanup's inventory and deletion manifest).

## Archive — `research/archive/`

| path | campaign |
|---|---|
| `campaign1_solar_wave/reports/` | #1 report set (`latest.md`, `leaderboard.md`, `robustness.md`, `portfolio.md`, finals) |
| `campaign3_system_master/BASELINE_MODELS.md` | **#3 shipped baselines** — Product A `SolarWaveSMMaster_v4.cs`, Product B `SolarWaveOneContractNQ_v5.cs` / `MNQ_v5.cs`. Still authoritative *for those three objects only* |
| `state_snapshots/STATE_OF_RESEARCH_20260818.md` | dated cross-campaign snapshot |
| `closed_handoffs/` | `RESEARCH_HANDOFF_20260818.md`, `NEXT_HANDOFF_CAMPAIGN1_CLOSED.md` |

## Closed campaigns still living in place

These keep their own state documents. **They say "current" about campaigns that have ended.**

| campaign | state doc |
|---|---|
| #1 Solar Wave (closed 2026-08-07) | `research/CAMPAIGN_STATE.md`, `research/SOLAR_WAVE_CAMPAIGN_README.md` |
| #2 independent audit (closed 2026-08-07) | `research/audit/AUDIT_EXECUTIVE.md` |
| #3 SYSTEM_MASTER (closed 2026-08-21) | `research/system_master/CURRENT_TRUTH.md` |
| #4 Scalping Lab (dormant) | `research/scalping_lab/CAMPAIGN_STATE.md` |
| #5 complementary families | `research/04_complementary_family/` |
| #6 OTR / VWAP Flux | `research/original_trader_reconstruction/CURRENT_TRUTH.md` |

Numbered `research/0N_*` directories are campaign-#1/#3 topic areas (diagnostics, solar
refinements, reverse engineering, execution, open axes, sleeves).
