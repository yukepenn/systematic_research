# SM1M_MNQ_SUBSTRATE — MANIFEST

**Run class:** $0 DATA EXTRACTION (data materialization with a MANIFEST, SM1M pattern; no
hypothesis, no preregistration, no signal, no P&L). Built 2026-09-06.

Closes the DATA_VERDICT_20260831 gap: *"MNQ 1-min — not extracted — hidden by a hard-coded
`symbol="NQ"` in build_registry.py"*.

## Object

| | |
|---|---|
| parquet | `runs/SM1M_MNQ_SUBSTRATE/out/mnq_1m_2022_2026.parquet` (29,133,369 bytes) |
| **sha256** | `94fa4b12c78eff8eccb9b2453b44986cc6c4cb3305a0e1fdf862a862f2f71c25` (identical across two independent builds) |
| **rows** | **1,627,987** |
| **sessions** | **1,189** (18:00→17:00 ET label rule, `src/analytics/runlib.py` `session_date`) |
| bar range | 2021-12-26 18:01:00 → 2026-07-31 16:59:00 (END-stamped ET, **no shift**) |
| session range | **2021-12-27 → 2026-07-31** |
| schema | `time, open, high, low, close, volume` — byte-identical column set to the NQ/ES/RTY/YM SM1M substrates (drop-in fifth member) |
| series | "MNQ 09-26" **merge back-adjusted front-month chain** (same construction as the other four substrates; prices before the last roll carry cumulative roll offsets — measured medians +765 pts in late 2025 → +3,378 pts in early 2022; volume is the true front contract's own, verified below) |

## Provenance

1. `SWMinuteExport_v1` (`research/scalping_lab/src/ninjascript/`, sha256
   `48c21a775326b69a731fea27945c9b41b99ccec4553992bee5f75acd92cdc89d`) re-installed via the
   CLAUDE.md §6 **local path** (file copied to `bin/Custom/Strategies/`, picked up by NT8
   **without F5**, resolved in fresh assembly `40daedcc00a24a0ba7d83631d1c25d80`; repo copy and
   NT8 copy sha256-identical). No source ever left the machine.
2. CrossTrade `RunStrategyBacktest` job `7c80c101b6dd471a` (engine `nt8_strategy_analyzer`,
   NT8 8.1.8.1, fingerprint `sha256:b4255f1b0dd7fba1`, isolated Backtest account, zero orders):
   instrument **MNQ 09-26**, Minute/1 Last, `from 2021-12-24T00:00:00Z`,
   `to 2026-07-31T21:59:59Z` = `session_close_boundary_utc(2026-07-31)` — **the §5 seal was
   applied at the export boundary**, before any row existed. Loaded 1,629,368 bars.
3. Raw CSV `Documents/NinjaTrader 8/out/mnq1m_2022_2026_1m.csv`
   (sha256 `65d47e38a20fb3f40206d298a00e544be04f12b021bd27b6c887c6755b6c7743`, kept outside the
   repo per the SM1M pattern).
4. `src/build_mnq_substrate.py` → gates, session labels, hard seal drop, parquet.
   Full program output: `out/build_log.txt`.

## SEAL assertion (program output, verbatim)

```
SEAL RULE (CLAUDE.md s5 / LOCKED_FORWARD): HARD-DROP session >= 2026-08-01
  rows dropped at build time             0   (export was already capped at the s5 boundary; 0 expected)
  max retained session date              2026-07-31
  ASSERT max retained session < 2026-08-01   PASS
```

Independent verification (fresh re-open): rows 1,627,987, sessions 1,189, max session
2026-07-31 < 2026-08-01 **PASS**.

## Gates and cross-checks (from `out/build_log.txt`)

- time strictly increasing / no stamps in (17:00,18:00] ET / OHLC sanity / volume ≥ 0 — all PASS.
- **Bar-stamp grid vs NQ substrate** (`runs/SM1M_SUBSTRATE`): sessions 2023-06-15, 2025-03-12,
  2026-06-10 → stamp-set Jaccard **1.0000 / 1.0000 / 1.0000** (1,380 bars each). The
  END-stamped convention matches the NQ substrate bar-for-bar; **no ±1-minute shift anywhere**.
- **Cross-source volume vs the TRUE unmerged day store** (`ncd_day.py`, format validated
  against GetBars): 2023-02-15 `MNQ 03-23` **exact** (1,058,855 = 1,058,855); 2024-05-14
  `MNQ 06-24` **exact**; 2025-11-18 `MNQ 12-25` rel diff 0.0005%. The merged minute series
  carries the true front contract's own volume, not a copy.

## Census reconciliation (spot-check vs expectation)

Census (`research/data/NT8_CAPABILITY_CENSUS.csv`) shows 1,453 MNQ minute-Last PAYLOAD
calendar-date files (1,429 distinct pre-seal dates), span 20211230→20260824 — the "~1,449
sessions" in DATA_VERDICT. That is a **calendar-date file count**: it includes 235 Sundays
(Sunday-evening bars belong to Monday's session) and roll-window duplicate dates across
contract dirs. The matching session-level object is this parquet's **1,189 trading sessions**
over 2021-12-27→2026-07-31 (≈252/yr × 4.6yr ✓); sealed dates ≥2026-08-01 were never read.
Spot-check: session 2026-06-10 = 1,380 bars = full CME ETH grid = NQ substrate same session.

## 5-row sample

```
                   time      open      high       low     close  volume
0   2021-12-26 18:01:00  19682.25  19716.25  19682.25  19706.75    1044
1   2021-12-26 18:02:00  19708.25  19711.75  19704.75  19708.50     444
2   2021-12-26 18:03:00  19709.25  19709.50  19698.75  19703.25     455
-3  2026-07-31 16:58:00  28311.50  28317.50  28295.75  28302.00     867
-1  2026-07-31 16:59:00  28300.00  28312.00  28294.75  28305.75     585
```

## Notes

- The file name follows the SM1M pattern (`_2022_2026`); the parquet additionally retains the
  four owned pre-2022 sessions (2021-12-27 → 2021-12-31) rather than discarding owned data.
- No local minute-`.ncd` decode exists or was attempted: `runs/VOLUME00_20260828` proved the
  minute store is not the fixed 48-byte day-record layout ("MINUTE LAYOUT NOT RESOLVED",
  `out/volume00.txt:104`). The NT8-side export is the validated extraction tooling.
- Side effects outside this run dir (for the coordinator): `SWMinuteExport_v1.cs` re-copied to
  `Documents/NinjaTrader 8/bin/Custom/Strategies/` (repo-identical copy of existing tooling);
  export CSVs + three small `probe_*` CSVs in `Documents/NinjaTrader 8/out/`. Nothing in the
  repo outside `runs/SM1M_MNQ_SUBSTRATE/`, `runs/SM1M_ZB_SUBSTRATE/`,
  `runs/NQ1M_BIDASK_EXTRACT_20260906/` was touched. No orders, no strategy enablement, no
  connection changes; backtests ran on the isolated Backtest account only.
