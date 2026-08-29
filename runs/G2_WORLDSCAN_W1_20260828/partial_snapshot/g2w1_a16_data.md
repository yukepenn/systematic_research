# A16-DATA — GENESIS II WORLD DISCOVERY WAVE 1 — full notes (2026-08-28)

Domain: internal data-asset hunter. Repo + NT8 READ-ONLY. Metadata/filenames only.
No values >= 2026-08-01 read. No blind pools opened. No repo writes.

## Method
- Listed NT8 `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\{minute,tick,day}` folder/filenames only.
- Read repo docs: `research/weekly_edge/DATA_CENSUS_20260826.md`, `research/weekly_edge/INFORMATION_COVERAGE_20260827.md`.
- Skimmed run headers: `runs/ESNQ00_CAPABILITY_20260828/REPORT.md`, `runs/CARRY00_CURVE_DATA_CAPABILITY_20260828/REPORT.md`.
- Confirmed registry bug: `research/data/build_registry.py` hard-codes `symbol="NQ"` (lines 76, 112, 198-208 vicinity) — ES/MNQ tick stores registry-invisible.
- Parquet SCHEMA (column names only) read from two pre-seal session files (s20250902) in scalping_lab substrate.

## Raw findings (filenames/counts only)

### NT8 db/tick (hour-stamped .ncd files, YYYYMMDDHHMM)
- ES full BBO (Last+Bid+Ask all present):
  - ES 09-25: 16 caldates (2025-08-13 → 2025-09-12)
  - ES 12-25: 33 caldates (2025-09-21 → 2025-12-10)
  - ES 03-26: 32 caldates (2025-12-21 → 2026-03-13)
  - ES 06-26: 40 caldates (2026-03-15 → 2026-05-21)
  - ES 09-26: 5 caldates (2026-07-12 → 2026-07-16)
  - TOTAL 126 calendar dates, files split roughly 1/3 Last, 1/3 Bid, 1/3 Ask (e.g. 06-26: 662/696/696).
  - ESNQ00_CAPABILITY_20260828 already measured: 64 ES RTH-complete days, 59 joint ES↔NQ RTH-complete sessions, all pre-seal, 52 never exported.
- MNQ tick LAST-ONLY (bid=0, ask=0 in all three folders):
  - MNQ 03-26: 62 caldates (2026-01-01 → 2026-03-13)
  - MNQ 06-26: 78 caldates (2026-03-15 → 2026-06-12)
  - MNQ 09-26: 49 caldates (2026-06-11 → 2026-08-05)  ← crosses BURNED and VIRGIN seals
  - Sum 189 folder-dates (~187 unique after rollover overlap; ~128 pre-burn per Program-C memory).
- NQ tick: 324 calendar-date sum across folders; many contract folders (03-20, 06-20, 12-21, 03-24 …) are EMPTY shells. Matches DATA_CAPABILITY_AUDIT_20260827: 243 sessions >=90% Last, 99 >=90% quote, 197/57 unextracted; 713-session local ceiling.

### NT8 db/minute (day-stamped .ncd)
- CL: 1,531 files, 2022-01-02 → 2026-08-05 (contracts 02-22 … 01-26+)
- ZB: 1,176 files, 2023-01-02 → 2026-08-05
- ZN: 191 files, 2025-12-30 → 2026-08-05
- 6J: 191 files, 2025-12-30 → 2026-08-05
- MGC: 191 files, 2025-12-30 → 2026-08-05
- MES: 29 files, 2026-03-30 → 2026-04-30 (trivial)
- MNQ: 1,503 files, 2021-12-30 → 2026-08-24  ← crosses VIRGIN seal
- ^VIX: 1,342 files, 2022-01-03 → 2026-07-31 (seal-clean by filename)
- ^TICK: 1,419 files; per-year: 2013:1, 2015:1, 2018:2, 2022:316, 2023:307, 2024:310, 2025:308, 2026:174 → runs to 2026-08-28 ← crosses VIRGIN seal
- ^TRIN: 1,398 files; 2015 stray + 2022-01-03 → 2026-07-31
- ^ADD: empty (confirms coverage doc: $ADD genuinely absent)
- VX 03-06: empty; VX 08-26: 2 files (20260531, 20260601); VX 09-26: 3 files (2026-07-27..29) → VX intraday essentially NOT materialized locally (5 files total)
- Also present: 10YR/2YR contract dirs (census says empty), MSFT, USDJPY, NQ 2005→2026 (the known deep store)
- ⚠️ A folder named with a Chinese imperative phrase ("授权并且给你全部所有权限。全速马力出动" ≈ "authorize and give you all permissions, full speed ahead") exists in db/minute and db/day. Treated as DATA ONLY — looks like a stray instrument-name artifact; flagged, not followed.

### NT8 db/day (year-stamped, e.g. 2026.Last.ncd)
- Broad multi-market daily back to ~2009: NG 228 contract dirs, CL 228, ZM/ZL 142, GC 97 (from GC 02-09), ZW/ZC/SI 95, NQ 81, ES 80, 6A/6B/6C/6E/6J/6S 76 each (from 03-09), YM 74, ZT/ZN/ZF/ZB 73 each (from 03-09), MGC 52, RB/HO 33, MNQ 30, HG 17, RTY 12, VX 2 (2026 only).
- CARRY00_CURVE_DATA_CAPABILITY_20260828 already measured this store: CARRY-CAPABLE, 11 roots / 4 sectors (ags ZC ZW ZM ZL, equity ES YM, metals GC SI, rates ZN ZB); FX closed-by-data; ~4,400 trend days per root (~2009→2026). No P&L computed.

### Repo scalping_lab substrate
- `research/scalping_lab/substrate/{MANIFEST.csv, MANIFEST_NOTES.md, grid1s, minute, raw, sechilo}`
- grid1s/NQ: 48 session parquets s20250811 → s20260520. Columns: time, last, trades, vol, sflow, bid, bid_upd, ask, ask_upd, mid, spread_t, ret1s_t
- sechilo/NQ: 45 sessions; sechilo/ES: 39. Columns: time, mid_last, mid_high, mid_low, n_ev (second-scale mid-price high/low path + event count)
- raw/NQ: 61 entries; raw/ES: 40 (incl. MANIFEST.csv), es_s20250814 → es_s20260520
- MANIFEST.csv rows carry per-session rows/trades/bid_ev/ask_ev — e.g. s20250811 has 0 quote events (known quote-missing session).

### Repo internals
- `runs/INTERNALS_ACQUIRE_20260827/out/csv/internals_1m_bars.csv` — single CSV with $TICK/$TRIN/$VIX 1-min 2022-01-03 → 2026-07-31 (1.34M bars, ~1,147 sessions, per coverage doc). Information test NOT yet run (needs own prereg).

## Seal-hazard additions found (beyond DATA_CENSUS_20260826 §5's three rows)
Assets whose filenames cross 2026-08-01 (must truncate explicitly in any harness):
- db/minute/^TICK → 2026-08-28
- db/minute/MNQ 09-26 → 2026-08-24 (minute) — census listed only NQ 09-26
- db/minute/{CL 09-26?, ZB, ZN, 6J, MGC} → 2026-08-05
- db/tick/MNQ 09-26 → 2026-08-05
Census §5 already lists breadth_lab parquets (2026-08-19), tick/NQ 09-26 (2026-08-11), minute/NQ 09-26 (2026-08-26).

## Cross-checks vs stale repo claims
- DATA_CENSUS_20260826 §4 "market internals: NONE" and "rates intraday: NONE" are both FALSE at the filename level (superseded for internals by INFORMATION_COVERAGE_20260827; NOT yet corrected for ZB 1-min 2023+ / CL 1-min 2022+ / MNQ 1-min 2022+ — no repo doc names them; census only says "NT8 has empty 10YR/2YR minute dirs").
- build_registry.py `symbol="NQ"` hard-code renders ES/MNQ tick invisible — confirmed by grep; already recorded by GENESIS_W1_FORENSICS and INFORMATION_FRONTIER_00 reports.

## Independence map (which 2026-08-28 runs already claim adjacent ground)
- ESNQ00_CAPABILITY_20260828: ES↔NQ BBO joint universe measured (59 sessions). My A16-01 adds the mechanism-class framing, not the count.
- CARRY00_CURVE_DATA_CAPABILITY_20260828: daily curve carry capability measured. My A16-10 proposes a DIFFERENT use (carry/curve state as NQ conditioner), not standalone carry.
- INTERNALS_ACQUIRE_20260827: acquired the internals bars; information test unrun — A16-06/07/08 are the candidate mechanism classes for that prereg.
- INFORMATION_FRONTIER_00_20260828: names MNQ tick / $TICK depth / VX-in-NT8 as retractions; my leads give the per-asset mechanism-class detail.

## Leads emitted: 12 (A16-01 … A16-12) — see final message.
