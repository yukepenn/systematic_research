# CROSSASSET_WAVE0_INVENTORY_20260906 — MANIFEST

**Run class:** $0 READ-ONLY INVENTORY (no hypothesis, no signal, no P&L, no extraction, no seal
read). Built 2026-09-06 for the cross-asset campaign Wave 0.

## What this run produced

| file | description |
|---|---|
| `roots_seen.csv` | raw census-derived per-root counts: one row per (root, semantic_class, kind, series) present in `research/data/NT8_CAPABILITY_CENSUS.csv`, with PAYLOAD/SPARSE/EMPTY file counts, distinct-contract count, and PAYLOAD date span. 65 rows. |
| (deliverable, outside this dir) | `research/cross_asset/DATA_INVENTORY.md` — the master inventory table + roll/cost/freeze analysis. |

## Method / provenance (fully reproducible, consumes no seal)

1. **Census** `research/data/NT8_CAPABILITY_CENSUS.csv` (51,936 file rows, produced by
   `research_sdk/data_census.py` which reads file names/sizes/mtimes only — never `.ncd` content).
   `roots_seen.csv` is a pure PAYLOAD-only aggregation of it.
2. **Extracted parquets opened directly** (rows / min-max time / session count via 18:00→17:00 ET
   label rule / columns / min-close / intrasession Δclose):
   - `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` — 1,620,044 rows, **1,184 sess**
   - `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet` — 1,620,385 rows, **1,184 sess**
   - `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet` — 1,568,111 rows, **1,177 sess**
   - `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` — 1,595,378 rows, **1,177 sess**
   - `runs/SM1M_MNQ_SUBSTRATE/out/mnq_1m_2022_2026.parquet` — 1,627,987 rows, **1,189 sess**
     (matches its MANIFEST exactly)
   - `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet` — 1,086,151 rows, **923 sess**
     (matches its MANIFEST exactly)
3. **Roll treatment** from each `build_meta.json` + the MNQ/ZB `MANIFEST.md`.
4. **Daily materialized parquet** from `runs/GENESIS_FREEDATA_CBOE_20260828/certified/` and
   `research/breadth_lab/*/data/` (enumerated, not re-opened for sealed content).
5. **Prior-consumption** from run dirs `ESNQ_V1_20260828`, `ENGINE3_SLATE5_CROSSMARKET`,
   `REL01_CONDITIONAL_CROSSMARKET`, `G2_F13_MC57_ZBSTATE_20260906`, `XINST01_WEEKLY_EDGE_PORT_20260906`
   (specs/reports read; no data files opened).

## Seal compliance

Nothing dated ≥ 2026-08-01 was read. The census exposes sealed-window *file presence* (names/sizes)
only; all six extracted parquets terminate at 2026-07-31. No extraction, no NT8 recompile, no git,
no touch of `research/genesis/SEARCH_LEDGER.jsonl`.
