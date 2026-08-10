# Batch 1 protected-pool export log

Pipeline: byte-for-byte replication of `research/scalping_lab/runs/EXPORT01/` (40-session
discovery export). Same strategy family (`SWScalpTickExport_v3`, staged in repo, deployed to
NT8 live NinjaScript folder this run), same output dirs
(`research/scalping_lab/runs/EXPORT01/out` -> `research/scalping_lab/substrate/raw/NQ` ->
`research/scalping_lab/substrate/grid1s/NQ`), same conversion scripts
(`csv_to_parquet.py`, `build_grid1s.py`), unmodified.

Per-session date-range convention verified against `runs/EXPORT01/runlist_40.csv`: frm =
`<date>T09:00:00Z` (constant), to = `<date>T21:00:00Z` (EDT dates) or `<date>T22:00:00Z` (EST
dates) i.e. always 17:00 ET close, cross-checked against
`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`'s `contract_month_folder(s)` column for instrument.
Full runlist: `batch1_runlist.csv` in this dir.

Preflight (2026-08-10):
- Verified `runs/W5_PROTECTED_CONFIRMATION/` preregistration bundle is git-committed
  (2eabcad) before any pool data touched, and Batch-1 session selection is git-committed
  (7c601a1), seeded/disclosed, chosen before any outcome seen. This export step is pure file
  materialization (no statistic/diagnostic computed) -- consistent with FAILURE_RULES.md's
  "opened" definition and its "runs to completion in one uninterrupted pass" requirement once
  the actual confirmation bundle is opened (a separate, later step).
- `SWScalpTickExport_v3.cs` (repo copy) was NOT present in NT8's live
  `Documents\NinjaTrader 8\bin\Custom\Strategies` (only current SolarWave-campaign strategies
  were loaded there). Verified compile in-memory (clean, 0 errors/warnings), wrote it to NT8
  live folder via WriteNinjaScriptFile (compile_engine=file_only, i.e. reflection auto-recompile
  unavailable this session -- expected fallback per tool docs). Ran a 1-minute smoke-test
  backtest against a previously-exported discovery date (2025-08-11, already public/used) with a
  throwaway ExportDir/Tag outside the real substrate: class resolved
  (`NinjaTrader.NinjaScript.Strategies.SWScalpTickExport_v3`), ran to `Finalized`, and the CSV
  materialized correctly (401,811 rows, header `bip,time,price,volume`) -- confirms NT8 had
  already picked up the compiled type despite the `file_only` warning. No protected-pool data
  was touched by this smoke test.
- Finding: for this add-on's Tick-period backtests, the intraday time-of-day portion of
  from/to does not sub-window a session -- NT8 loads/replays the full trading-day tick series
  associated with the requested date regardless (a 1-minute window still produced the entire
  day's ticks). This matches why EXPORT01's own runlist always uses a single per-day from/to
  bracket rather than intraday slicing, and is why the same convention is reused here unchanged.

Status legend: OK = parquet+grid produced, structurally sane. CAPPED = hit the 20,000,000-row
v3 cap, RTH second pass needed. FAIL = blocked, see notes.

## Sessions

### 1. s20250819 (2025-08-19, NQ 09-25) -- OK
- Backtest started 2026-08-10T10:07:01Z, finished 2026-08-10T10:07:19Z (~18s engine time incl.
  first-touch historical data fetch). job_id=4bd9cb7f56484531.
- Raw CSV: 268,776,670 bytes, header `bip,time,price,volume`.
- MANIFEST.csv: rows=6,398,798, capped=0 (well under the 20M v3 cap; no RTH second pass
  needed). t_min=2025-08-18 18:00:00.012 (ET), t_max=2025-08-19 16:59:59.476 (ET) -- confirms
  actual exported coverage is the full CLAUDE.md-convention session (18:00 ET prior day ->
  17:00 ET labeled day), independent of the narrower from/to sub-window passed to the backtest
  call (NT8 loads/replays the whole trading-day tick series for Tick-period backtests
  regardless of intraday from/to; only the calendar date, not the time-of-day, matters -- see
  preflight note above).
- `research/scalping_lab/substrate/raw/NQ/s20250819.parquet`: 6,398,798 rows, cols
  [bip, time, price, volume].
- `research/scalping_lab/substrate/grid1s/NQ/s20250819.parquet`: 82,800 rows (full session,
  matches other complete non-holiday sessions in grid_log.txt), cols [time, last, trades, vol,
  sflow, bid, bid_upd, ask, ask_upd, mid, spread_t, ret1s_t].
- No errors.

### 2. s20250912 (2025-09-12, NQ 09-25) -- OK
- Backtest 10:08:43Z -> 10:08:55Z (~12.5s). job_id=46c5f0ca01a846a9.
- MANIFEST.csv: rows=4,975,621, capped=0. t_min=2025-09-11 18:00:00.012 ET, t_max=2025-09-12
  16:59:59.900 ET (full session).
- raw parquet + grid1s parquet both produced. No errors.

### 3. s20251028 (2025-10-28, NQ 12-25 -> resolved NQZ5) -- OK
- Backtest 10:09:31Z -> 10:09:46Z (~15s). job_id=df789bb3f0304091.
- MANIFEST.csv: rows=6,808,344, capped=0. t_min=2025-10-27 18:00:00.012 ET, t_max=2025-10-28
  16:59:59.444 ET (full session).
- raw parquet + grid1s parquet both produced. No errors.

### 4. s20251125 (2025-11-25, NQ 12-25 -> resolved NQZ5) -- OK
- Backtest 10:10:20Z -> 10:10:29Z (~9.6s). job_id=5a29cba4ae124783.
- MANIFEST.csv: rows=1,159,069, capped=0. t_min=2025-11-24 18:00:00.032 ET, t_max=2025-11-25
  16:59:59.408 ET (full session; low volume day, well under cap).
- raw parquet + grid1s parquet both produced. No errors.

### 5. s20260217 (2026-02-17, NQ 03-26 -> resolved NQH6) -- OK (not actually capped, see note)
- Backtest 10:10:54Z -> 10:11:30Z (~36s, slower -- first-touch data fetch for a denser day).
  job_id=ff178b4e66524cb9.
- MANIFEST.csv: rows=15,830,526, MANIFEST's `capped` column shows 1 -- **but this is a stale
  false positive**: `csv_to_parquet.py`'s `capped` column is `int(n>=12000000)`, a hardcoded
  threshold left over from `SWScalpTickExport_v1`'s 12M cap; it does not know about v3's actual
  20,000,000 cap. 15,830,526 is well under 20M and is not a round/truncated-looking number (a
  genuine v3 truncation would read exactly 20,000,000, the same signature the 12 v1-era capped
  sessions showed at exactly 12,000,000). grid1s has the full 82,800-row session (no early
  cutoff). **No RTH second pass needed** for this session -- treating MANIFEST's `capped` label
  as informational/stale for any v3-exported row going forward.
- t_min=2026-02-16 18:00:00.000 ET, t_max=2026-02-17 16:59:59.316 ET (full session).
- raw parquet (15,830,526 rows) + grid1s parquet (82,800 rows) both produced, structurally
  verified (columns as expected). No errors.

### 6. s20260302 (2026-03-02, NQ 03-26 -> resolved NQH6) -- OK (not actually capped)
- Backtest 10:13:09Z -> 10:13:39Z (~30s). job_id=5eb9848386a84cbc.
- MANIFEST.csv: rows=13,190,774, `capped` shows 1 (same stale >=12M heuristic as session 5, not
  a real v3 truncation -- not a round number, well under the 20M cap). t_min=2026-03-01
  18:00:00.160 ET, t_max=2026-03-02 16:59:59.856 ET (full session). grid1s has full 82,800 rows.
  No RTH second pass needed.
- raw parquet (13,190,774 rows) + grid1s parquet (82,800 rows) both produced. No errors.

### 7. s20260422 (2026-04-22, NQ 06-26 -> resolved NQM6) -- OK
- Backtest 10:14:33Z -> 10:15:02Z (~29s). job_id=43320e6db2324a28.
- MANIFEST.csv: rows=9,366,357, capped=0. t_min=2026-04-21 18:00:00.012 ET, t_max=2026-04-22
  16:59:59.992 ET (full session).
- raw parquet + grid1s parquet both produced. No errors.

### 8. s20260512 (2026-05-12, NQ 06-26 -> resolved NQM6) -- OK
- Backtest 10:15:46Z -> 10:15:54Z (~8.3s). job_id=3fe1fbd355114092.
- MANIFEST.csv: rows=1,456,564, capped=0. t_min=2026-05-11 18:00:00.032 ET, t_max=2026-05-12
  16:59:57.376 ET. grid1s=82,798 rows (2s short of the full 82,800 -- a natural end-of-session
  data gap, same benign pattern seen in the original 40-session grid_log.txt, e.g. s20250924=
  82,799, s20260430=82,799; not a truncation).
- raw parquet + grid1s parquet both produced. No errors.

## Final verification (all 8 sessions, post-hoc structural pass)

`research/scalping_lab/runs/EXPORT01/out/` is empty (all 8 CSVs converted and removed by
`csv_to_parquet.py`, same cleanup behavior as the original 40-session run). All 8 sessions
confirmed present in both substrate layers with matching row counts and expected columns:

| session | raw rows | grid1s rows | capped(stale flag) | true v3 cap hit? |
|---|---|---|---|---|
| s20250819 | 6,398,798 | 82,800 | 0 | no |
| s20250912 | 4,975,621 | 82,800 | 0 | no |
| s20251028 | 6,808,344 | 82,800 | 0 | no |
| s20251125 | 1,159,069 | 82,800 | 0 | no |
| s20260217 | 15,830,526 | 82,800 | 1 (stale, see note) | no |
| s20260302 | 13,190,774 | 82,800 | 1 (stale, see note) | no |
| s20260422 | 9,366,357 | 82,800 | 0 | no |
| s20260512 | 1,456,564 | 82,798 | 0 | no |

No session reached the actual v3 truncation signature (exactly 20,000,000 raw rows), so **no RTH
second pass was required for any of the 8 sessions**. `research/scalping_lab/substrate/raw/NQ/`
and `research/scalping_lab/substrate/grid1s/NQ/` now hold all 8 protected-pool Batch-1 sessions
in the exact same file layout/schema as the 40 discovery sessions, so `AUCTION01`/`AUCTION02`/
`FLOW01`/`COMBO01` scripts can read them unmodified once/if the confirmation bundle is actually
opened (a separate, later step -- not performed here).

## Summary

8/8 sessions exported successfully. No failures, no blockers, no RTH second pass needed (v3's
20M cap was never reached; the highest-volume session, s20260217, used 15.83M of the 20M
budget). Total wall-clock for all 8 backtests: ~3 minutes (NT8 already had usable historical
tick+BBO coverage cached/fast-fetchable for all 8 dates; no session needed the hours-scale
first-touch download the task brief anticipated as a possibility).

One deployment step was required that the task brief didn't fully anticipate: `SWScalpTickExport_v3`
existed only in this repo's mirror copy, not in NT8's live NinjaScript folder (it had been
`Stage`d per the referenced commit but never actually deployed/exercised). It was written to
NT8 via `WriteNinjaScriptFile` and validated with a smoke-test backtest against an
already-public discovery date before being used on any protected-pool date.

Files touched by this batch: `research/scalping_lab/substrate/raw/NQ/{8 new}.parquet`,
`research/scalping_lab/substrate/grid1s/NQ/{8 new}.parquet`, `research/scalping_lab/substrate/
MANIFEST.csv` (8 new rows appended), plus this log, `batch1_runlist.csv`,
`batch1_convert_log.txt`, `batch1_grid_log.txt` in this dir. Nothing was committed to git by
this task -- left for the user/next step to review and commit.
