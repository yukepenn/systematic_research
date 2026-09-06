# SM1M_ZB_SUBSTRATE — MANIFEST

**Run class:** $0 DATA EXTRACTION (data materialization with a MANIFEST, SM1M pattern; no
hypothesis, no preregistration, no signal, no P&L). Built 2026-09-06.

Closes the DATA_VERDICT_20260831 gap: *"ZB 1-min — 1,113 sessions, 2023-01-02 → — not
extracted"* — the surface external mining flagged as the only genuinely new raw information
surface.

## Object

| | |
|---|---|
| parquet | `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet` (13,309,415 bytes) |
| **sha256** | `ae04d0a7cdc745cc3cf1ab734666104108207543c4d16ead4e1f058363ffef39` (identical across two independent builds) |
| **rows** | **1,086,151** |
| **sessions** | **923** (18:00→17:00 ET label rule; per-session bar counts median 1,193 / p10 1,074 / max 1,380 — ZB prints no bar in zero-trade minutes, unlike NQ/MNQ) |
| bar range | 2022-12-26 18:01:00 → 2026-07-31 16:59:00 (END-stamped ET, **no shift**) |
| session range | **2022-12-27 → 2026-07-31** |
| schema | `time, open, high, low, close, volume` — same column set as the other SM1M substrates |
| series | "ZB 09-26" **merge back-adjusted front-month chain** (anchor segment offset ≈ −1/32 settle-noise; earlier segments carry cumulative roll offsets, e.g. median −41/32nds during late-2025 — the expected merged construction, same as all SM1M substrates) |

## ⭐ ZB-specific: PRICE-GRID RESTORATION (read before using prices)

`SWMinuteExport_v1` formats prices `ToString("F2")`. ZB ticks in **1/32 = 0.03125**, so the CSV
carried prices rounded to 0.01. This is **exactly invertible**: true prices lie on the 1/32 ⊂
1/64 grid (spacing 0.015625); the F2 error is ≤ 0.005 < half-spacing 0.0078125, so
nearest-1/64 snapping recovers the true price uniquely regardless of formatter tie-breaking.
Measured on the full file: max |csv − snapped| = 0.005000 (PASS), and **100.000000% of
restored prices sit on the coarser 1/32 grid** — the parquet stores exact on-grid prices.
(NQ/MNQ/ES/RTY/YM are F2-exact by tick size; ZB is the first sub-cent-grid instrument through
this exporter.)

## Provenance

1. `SWMinuteExport_v1` (sha256 `48c21a77…cdc89d`), installed via the CLAUDE.md §6 local path,
   fresh assembly `40daedcc00a24a0ba7d83631d1c25d80`. No source left the machine.
2. CrossTrade `RunStrategyBacktest` job `58daa58aab60476e` (`nt8_strategy_analyzer`, NT8
   8.1.8.1, fingerprint `sha256:b4255f1b0dd7fba1`, isolated Backtest account, zero orders):
   instrument **ZB 09-26**, Minute/1 Last, `from 2022-12-24T00:00:00Z`,
   `to 2026-07-31T21:59:59Z` = `session_close_boundary_utc(2026-07-31)` — seal applied at the
   export boundary. Loaded 1,087,287 bars.
3. Raw CSV `Documents/NinjaTrader 8/out/zb1m_2023_2026_1m.csv`
   (sha256 `ed8a90f8713ce679ee8a9a3237dcea2febe740811cb7749aa893f3fb4d4c60b8`, outside repo).
4. `src/build_zb_substrate.py` → grid restoration, gates, session labels, hard seal drop,
   parquet. Full program output: `out/build_log.txt`.

## SEAL assertion (program output, verbatim)

```
SEAL RULE (CLAUDE.md s5 / LOCKED_FORWARD): HARD-DROP session >= 2026-08-01
  rows dropped at build time             0   (export was already capped at the s5 boundary; 0 expected)
  max retained session date              2026-07-31
  ASSERT max retained session < 2026-08-01   PASS
```

Independent verification (fresh re-open): rows 1,086,151, sessions 923, max session
2026-07-31 < 2026-08-01 **PASS**.

## Gates and cross-checks (from `out/build_log.txt`)

- time strictly increasing / no stamps in (17:00,18:00] ET / OHLC sanity (post-restoration) /
  volume ≥ 0 — all PASS.
- **Cross-source volume vs the TRUE unmerged day store** (`ncd_day.py`): 2023-08-15 `ZB 09-23`
  **exact** (308,984 = 308,984); 2024-05-14 `ZB 06-24` **exact**; 2025-10-15 `ZB 12-25`
  rel 0.0155%. True front-contract volume, not a merged copy.
- Restored closes land on the same 1/32 grid as day-store closes (differences are whole
  32nds — see back-adjustment profile in the log), corroborating exact grid restoration.

## Census reconciliation (spot-check vs expectation)

Census: 1,124 ZB minute-Last PAYLOAD calendar-date files (1,109 distinct pre-seal dates),
span 20230102→20260805 — DATA_VERDICT's "1,113 sessions". Calendar-date file counts include
Sundays and roll-window duplicates; the session-level object is this parquet's **923 trading
sessions** 2022-12-27→2026-07-31 (≈256/yr × 3.6yr ✓). The export also recovered late-Dec-2022
sessions from provider history that predate the local store's 2023-01-02 start. Spot-check:
session 2024-05-14 = 1,114 bars (sparse minutes are genuine zero-trade minutes; volume sum for
that session matches the day store exactly).

## 5-row sample

```
                   time       open       high        low      close  volume
0   2022-12-26 18:01:00  127.37500  127.37500  127.31250  127.31250     111
1   2022-12-26 18:02:00  127.34375  127.37500  127.34375  127.34375     101
2   2022-12-26 18:03:00  127.34375  127.34375  127.31250  127.31250      21
-3  2026-07-31 16:58:00  108.37500  108.40625  108.34375  108.37500    1867
-1  2026-07-31 16:59:00  108.37500  108.40625  108.37500  108.40625    1013
```

## Notes

- File name follows the SM1M pattern (`_2023_2026`); the parquet retains the three owned
  late-Dec-2022 sessions rather than discarding data.
- CBOT 30Y session is 18:00→17:00 ET like the index substrates; same label rule applies.
- Side effects outside run dirs: see `runs/SM1M_MNQ_SUBSTRATE/MANIFEST.md` §Notes (shared).
