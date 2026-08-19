# Research Data Substrate — build once, reuse forever (owner directive 2026-08-07)

Principle (governing): raw tick/BBO data is exported from NT8 EXACTLY ONCE per session,
then every study reuses the substrate. No per-idea re-exports, no per-idea rescans of
hundreds of millions of quote rows.

## Layer 0 — raw archive (one-time)
Per session, per instrument: `substrate/raw/{instrument}/{session}.parquet` (zstd), columns
bip(0=Last,1=Bid,2=Ask), time(ns), price, volume. Source: `SWScalpTickExport_v1` one run
per session (single unadjusted contract per session; contract chosen by cached-file date
ranges). CSV deleted after parquet conversion + row-count check. ~205 dev sessions ≈
3.2M rows × 205 ≈ 0.7B rows ≈ 8-12 GB compressed. The 40-session instrumentation sample
(`artifacts/instrumentation/session_sample_40.csv`, seed 20260807) is built first; the
remainder backfills opportunistically.

## Layer 1 — causal state grid (derived, one-time per grid)
Per session: snapshot tables at Δ ∈ {250ms, 1s, 5s} —
last, bid, ask, mid, spread, ret_1Δ, trade_count_Δ, volume_Δ, quote_updates_Δ,
tick-rule signed flow_Δ, velocity (time-to-move-N-ticks state), rolling range, session
clock, vol regime. All features CAUSAL (computed from data ≤ t). Stored
`substrate/grid{Δ}/{instrument}/{session}.parquet`. Most Tier-0 event studies run here.

## Layer 2 — event registries (derived, per study)
Each preregistered event definition materializes an event table (event time, state vector)
+ forward excursion outcomes (P(+A before −B) grid per Amendment §7, MFE/MAE, fixed-horizon
returns under BBO_EXEC + C1). Finalists ONLY may drop to Layer 0 for exact sequencing.

## Rules
- Layer 0 is append-only; a session is never re-exported unless its file fails integrity.
- Holdout sessions (2026-06-01 → 2026-07-31) are NOT exported until a Tier-3 read is
  authorized — absence of the file is the enforcement mechanism.
- Every layer records producer code version + row counts in a manifest
  (`substrate/MANIFEST.csv`).
- Engine session-keying: `from` ET calendar date == session END date (see pilot report).

## Appended notes (2026-08-18)
- The holdout window above was **consumed 2026-08-08 by system_master SM11** (owner-authorized
  joint read; CONTAMINATION_LEDGER entry). The no-export enforcement stays in force for this
  campaign's substrate — the window is research-consumed either way; only ≥2026-08-01 is virgin.
- Exporter lineage: `SWScalpTickExport_v1` (original substrate) → v2 (BUGGED, single-arg
  AddDataSeries, never produced data) → **v3** (fixed; compiled+deployed 2026-08-10; produced the
  8 batch-1 pool exports). `substrate/MANIFEST.csv`'s `src` column is hardcoded to v1 by
  `csv_to_parquet.py` and its `capped` flag uses the v1-era 12M rule — see
  `substrate/MANIFEST_NOTES.md` for the correct per-row reading.
