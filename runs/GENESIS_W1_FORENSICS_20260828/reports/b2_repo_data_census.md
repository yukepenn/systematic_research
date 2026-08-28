# TEAM B2 — Independent repo data census (PROJECT GENESIS)

Date: 2026-08-28. Scope: data files inside `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research` only. Method: recursive extension sweep (2,774 matching files), parquet FOOTER metadata only (schema / num_rows / row-group min-max stats — no data values), CSV heads (first ≤3 rows, all pre-2026-08-01 content), git ls-files / check-ignore, git grep for references. NT8 directory not entered. No mcp__crosstrade__* calls. Nothing under `research/data_forward_sealed` was opened except listing names (it contains only 3 .md governance files). No blind-pool data file exists in the repo to open (see §5).

Evidence tags: **RAW** = verified this session by me. **CLAIM** = a repo document says it.

---

## 1. Primary substrate stores (the research-usable raw data)

### 1.1 research/data_esnq/parquet/ — paired ES+NQ tick+BBO sessions (newest store)
- **RAW**: 44 NQ + 44 ES session parquets, identical session-date sets (s20250814 … s20260715, non-contiguous). Schema `[bip, time, price, volume]` (bip 0=Last,1=Bid,2=Ask per store convention — CLAIM in registry). NQ: 473,477,355 rows / 1,442.5 MB. ES: 407,792,033 rows / 1,034.3 MB. Footer time span 2025-08-13 18:00:00 → 2026-07-15 16:59:59 (both instruments). All pre-seal.
- **RAW**: governed by allowlist `research/data_esnq/ALLOWLIST_DEV_44.txt` (0.4 KB, n_allowed=44, "FAIL_CLOSED" policy — `research/data_esnq/raw/NQ/_allowlist_status.txt`). `_skipped_sessions.txt` lists refused dates including all 15 blind dates (20250813 appears twice in NQ list — refused twice).
- **RAW**: gitignored (`.gitignore:52 research/data_esnq/parquet/`) — on-disk only, NOT in git.
- Reference status: **1** non-run md names the store (`research/genesis/GENESIS_CHARTER.md`); run-level docs `ESNQ_V1`/`ESNQ00` 16 md refs. It is absent from `research/weekly_edge/DATA_CENSUS_20260826.md` (predates store). **Barely-documented newest asset.**

### 1.2 research/data_microstructure_v2/raw/NQ/ — NQ tick+BBO v2 (25M cap, no truncation)
- **RAW**: 58 session parquets, 780,167,968 rows, 2,464 MB, same `[bip,time,price,volume]` schema, span 2025-10-14 18:00:00.016 → 2026-07-31 16:59:59.944. **Distribution is lopsided: only 3 sessions predate 2026-05-13** (s20251015, s20260122, s20260219); the other 55 are contiguous 2026-05-13..07-31 (file names + committed MANIFEST.csv).
- **RAW**: MANIFEST.csv committed with per-session rows/contract/coverage(0.9993)/sha256; quality/qa.csv present. Parquets gitignored (`.gitignore:38`).
- s20260525 (Memorial Day) correctly absent from this store (quarantined — CLAIM, DATA_ASSET_REGISTRY row 5); its raw CSV sits in runs/ORDERFLOW_EXPAND (see §3.3).
- Referenced: 6 md (DATA_ASSET_REGISTRY.md, GENESIS_CHARTER.md, …).

### 1.3 research/scalping_lab/substrate/ — v1 (OLD) tick store + derivatives + deep-history minute
- **raw/NQ** — RAW: 61 parquets = 48 full sessions + 13 `s*_rth.parquet` partials, 531,611,712 rows, 1,610 MB, 2025-08-10 18:00 → 2026-05-20 16:59. CLAIM (registry row 4): 15 files truncated at exactly 12,000,000 rows (v1 cap), 42 of 48 quote-FULL, 3 sessions no quotes.
- **raw/ES** — RAW: 39 sessions + MANIFEST.csv, 328,858,165 rows, 544 MB, 2025-08-13 → 2026-05-20. CLAIM: ARCHIVE_ONLY.
- **grid1s/NQ** — RAW: 48 parquets, 3,938,190 rows, schema `[time,last,trades,vol,sflow,bid,bid_upd,ask,ask_upd,mid,spread_t,ret1s_t]` (the only store with signed flow `sflow`). CLAIM: grid1s `last` carries a recorded LOOKAHEAD defect (registry row 7, fix in AUCTION04).
- **sechilo** — RAW: NQ 45 / ES 39 parquets, `[time,mid_last,mid_high,mid_low,n_ev]`.
- **minute/NQ/nq1m_2005_202605.parquet** — RAW: 6,466,783 rows, 2006-01-05 08:59 → 2026-05-29 16:59, `[time,open,high,low,close,volume]`, 57.9 MB. The deep-history substrate (filename says 2005; content starts 2006-01-05 — registry itself records 2006). Referenced in 27 md files.
- **RAW git status**: raw/ and minute/ gitignored; **grid1s + sechilo parquets ARE git-tracked** (deliberate, per .gitignore comment).

### 1.4 research/data_internals/ — $TICK/$TRIN/$VIX 1-minute
- **RAW**: TICK_1m.parquet 445,625 rows; TRIN_1m 445,235; VIX_1m 444,640 (total 1,335,500 — **exactly matches committed MANIFEST.csv**, sha256s recorded). Span 2022-01-03 09:31 → 2026-07-31 15:59, RTH-only OHLC, volume absent (index). Parquets gitignored; MANIFEST tracked.
- CLAIM: ≥2026-08-01 hard-dropped at build. Consistent with RAW tmax 2026-07-31 15:59.
- Raw acquisition source on disk: see §3.2 (unreferenced 61.8 MB CSV).

### 1.5 research/multi_market/out/ — multi-market daily economic returns
- **RAW**: `economic_returns.parquet` 89,843 rows, 2009-03-31 → 2026-07-31, schema `[date, old_contract, target_contract, overnight, intraday, ret_points, rolled, root, sector, point_value, ret_usd, eligible, obs_idx]` (24 roots — CLAIM registry row 23). Gitignored.
- **RAW**: ROLL_LEDGER.csv (168 KB, volume-crossover roll decisions from 2009-03-30), tsmom_v1_dev_daily.csv (157 KB, daily net from 2010-03-23), contract_truth.csv, substrate_summary.csv, fetch_batches*.json — tracked. export/ holds 46 tiny fetch stubs + 2 test bar CSVs.

## 2. Bar caches in runs/ that are really substrate (git-TRACKED)

- **runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet** — RAW: 1,620,044 rows, 2022-01-02 18:01 → 2026-07-31 16:59 OHLCV. Registry row 3 = "nq1m_ext". TRACKED.
- **runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet** — RAW: 1,620,385 rows, same span. TRACKED.
- **runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet** — RAW: 1,595,378 rows. TRACKED.
- **runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet** — RAW: 1,568,111 rows. TRACKED.
- **runs/B01A_BARS_1M/nq_1m_2022_2026.csv** — RAW: 90.6 MB, head 2022-01-02T18:01, cols `time,open,high,low,close,volume,first_bar_of_session`; spec.yaml bounds to 2026-07-31T21:59:59Z (CLAIM; tail not read by policy). TRACKED (90 MB CSV in git).
- **runs/W18_XINST_BARS/{es,rty,ym}_3m_2022_2026.csv** — RAW: 27.5/26.4/24.9 MB, head 2022-01-02T18:03; spec.yaml: 3-minute Last, dev window ends 2026-05-29 (deliberate). TRACKED.
- **runs/AUDIT03_BARS/nq_3m_2022_2026.csv** — 30.5 MB (companion NQ 3m, to 2026-07-31 per W18 spec note).

### ⚠ Registry contradiction (finding b)
`research/data/DATA_ASSET_REGISTRY.csv` rows 14/17/18 list **ES / RTY / YM 1-minute stores as "ON DISK, NOT EXTRACTED"** (location `~/Documents/NinjaTrader 8/db/minute`) — while **materialized, git-tracked ES/YM/RTY 1m parquets covering exactly the claimed 2022→2026-07-31 span sit in runs/SM1M_*_SUBSTRATE/out** (RAW, footer-verified above). The registry names SM1M_SUBSTRATE for NQ only. Fourth instance of the "not extracted" pattern being false for in-repo assets. The registry likewise omits the W18_XINST 3m ES/RTY/YM CSVs and AUDIT03/B01A NQ 3m/1m CSVs.

## 3. On-disk, gitignored, and/or unreferenced data (finding a)

- **runs/INTERNALS_ACQUIRE_20260827/out/csv/internals_1m_bars.csv** — RAW: 61.8 MB long-format `symbol,time,open,high,low,close,volume` starting `$TICK,2022-01-03 09:31`. **0 md references by filename** (run name referenced in 2 md). Gitignored. This is the raw source of the three data_internals parquets.
- **runs/ORDERFLOW_EXPAND_20260827/out/csv/s20260525_ticks.csv** — RAW: 87.0 MB NQ tick+BBO for the quarantined Memorial-Day session (head `0,2026-05-24 18:00:00.092`), untracked, **0 references by filename**. Exists nowhere else in the repo; not in MSv2 MANIFEST.
- **probe_ticks leftovers** — RAW: 5 CSVs ≈703 MB: `research/scalping_lab/runs/DATAPROBE01/out/` + `out_depthcheck/` (140.7 MB each, head 2026-07-14 ticks — an NQ session not in any parquet store), `EXPORT01/{p20260506,p20260123,p20250910_on}/probe_ticks.csv`, and `EXPORT01/es20260715/probe_ticks.csv` (139 MB ES ticks 2026-07-15, likely the source of data_esnq ES s20260715). All gitignored.
- **runs/WE_XM_PARITY_20260827/out/we_xm_xm2.csv + we_xm_xmparity.csv** — RAW: 209.2 MB each, bar-by-bar XM decision dumps (`timestamp,nq_*,es_close,…,decision_ready,…,realized_pnl`) from 2022-01-02; untracked, 0 filename references.
- **research/weekly_edge/ninjascript/reference/xm_reference_bars.csv** — RAW: 56 MB, same XM schema, starts 2025-08-01 00:00 (2025, not sealed). Gitignored; 2 md refs (LIVE_READINESS).
- **Duplication** — RAW: several sessions exist in 2–3 tick stores at once (e.g. s20260518/19/20 in data_esnq NQ AND msv2 raw AND scalping raw; s20250814… in data_esnq and scalping raw). data_esnq and msv2 copies of s20260518 are byte-similar (55.55 MB each); scalping v1 copies differ (v1 exporter).

## 4. Seal audit (finding c)

- **RAW**: Across every parquet store, max footer timestamp = **2026-07-31 16:59:59.944** (msv2 s20260731). Internals tmax 2026-07-31 15:59. economic_returns tmax 2026-07-31. **No repo dataset content reaches 2026-08-01** by metadata.
- **RAW**: No data file carries a name-date ≥ 20260801 (the only ≥-Aug-2026 filename matches are report .md files and OTR screenshots).
- **RAW**: `research/data_forward_sealed/` contains only `DOM01/{DOM01_DATA_GOVERNANCE.md, DOM01_PROSPECTIVE_PROTOCOL.md, README.md}` — **zero data files**. The "SEALED forward pool ~19 sessions" (registry row 24 — CLAIM) lives in the NT8-side store, not in the repo.
- CSVs written post-2026-08-01 (WE_XM_PARITY 2026-08-27, ORDERFLOW_EXPAND) contain historical content only per heads/specs; tails not read by policy.

## 5. Blind pools — listed/counted only, never opened

- **ESNQ_BLIND_15**: manifest `runs/ESNQ_V1_20260828/manifests/ESNQ_BLIND_15.csv` — RAW: 15 dates 2025-08-13 → 2026-05-05 with contracts, plus `ESNQ_BLIND_EFFECTIVE_14.{csv,json}` (14 after the 2025-08-13 incident quarantine — CLAIM, INCIDENT_BLIND_EXPORT_20260828.md). **RAW: none of these session dates exist as files in any repo store** (all in `_skipped_sessions.txt` refusal lists). The one accidental export (s20250813_ticks.csv) is documented deleted-unread (CLAIM).
- **NQ BBO-19 blind pool** (BBO_COMPLETENESS_RECENSUS_V1_20260828 verdict B — CLAIM) and **141-session Last-only pool** (registry row 13 — CLAIM): both live in `~/Documents/NinjaTrader 8/db/tick`, **not in the repo**. Not touched.

## 6. Secondary / derived / legacy data (characterized, not exhaustively schema'd)

- **research/03_reverse_engineering/ledgers/** — 10 tracked CSVs, 186 MB: t2_canonical_1m.csv (62 MB, NQU6 1m 2023-01-02→, OHLCV + vendor signal columns `signal_trade,signal_trend,signal_wave,trailing_stop,trend_vector`), 8 parameter-probe variants, t2_probe_3m.
- **research/original_trader_reconstruction/data/** — nq0626_jun2026_1m.csv (1.45 MB) + nq0926_junjul2026_1m.csv (2.77 MB): NQ 06-26/09-26 contract 1m bars, June–July 2026 (head 2026-05-24 18:01). Tracked; referenced by OTR R30/R31.
- **Feature/state tables (tracked)**: runs/U0_UNIFIED_STATE/out/u0_state_table.parquet (540,232 rows × 77 cols, 2022→2026-07-31; 17 md refs); runs/U4_SHORT_MECHANISM (5 parquets); runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet + decision_points_30s + decision_outcomes (3.08 M rows total, 2025-08-13→2026-05-20); runs/MSLAST_CONTRACT_20260827/out/discovery_substrate.parquet (139,371 rows, 60s/300s microstructure features; parquet gitignored); runs/ESNQ_V1_20260828/out/feat_{batch,stream}.parquet (14,564 rows each).
- **Campaign-#1 result CSVs** (execution/trade ledgers, not substrate): 02_solar_refinements/wave1c (92 files, 90.5 MB), 04_execution/h011 (31), 05_open_axes (h006/h007/h008/h012/combo/gate), 07_h014_price, 08_es_portability, 09_sleeves, 10_v3v4_equivalence, 01_diagnostics (sw01_bar_ledger.csv 36.5 MB, sw01_trades_tagged.parquet 2,914 rows).
- **Registries (tracked)**: research/registry/tested_configs.csv (103 KB) + tested_configs_backfill.csv (91 KB) + RUNS_INDEX.csv; research/breadth_lab/REGISTRY.csv; scalping_lab/registry/*; system_master TESTING_LEDGER.csv + STATE_INFORMATION_LIBRARY.csv; OTR CLAIM_REGISTRY*.csv.
- **research/scalping_lab/data/hist_calendar_2005_2021.csv** (17 KB); scalping_lab/artifacts (141 small analysis files, 31.6 MB).
- **NT8 raw JSON payloads** in runs/FH_*, SW0*, AUDIT_GATE_* (raw_result.json up to 12.6 MB) — backtest evidence blobs.

## 7. Machine-readable inventory

```json
{
 "research/data_esnq/parquet/NQ": {"bytes": 1442500000, "files": 44, "rows": 473477355, "cols": ["bip","time","price","volume"], "freq": "tick", "instrument": "NQ", "start": "2025-08-13T18:00:00", "end": "2026-07-15T16:59:59", "git": "ignored", "referenced": "weak (1 md + ESNQ run docs)"},
 "research/data_esnq/parquet/ES": {"bytes": 1034300000, "files": 44, "rows": 407792033, "cols": ["bip","time","price","volume"], "freq": "tick", "instrument": "ES", "start": "2025-08-13T18:00:00", "end": "2026-07-15T16:59:59", "git": "ignored", "referenced": "weak"},
 "research/data_microstructure_v2/raw/NQ": {"bytes": 2464200000, "files": 58, "rows": 780167968, "cols": ["bip","time","price","volume"], "freq": "tick", "instrument": "NQ", "start": "2025-10-14T18:00:00", "end": "2026-07-31T16:59:59", "git": "ignored", "referenced": true, "note": "only 3 sessions before 2026-05-13"},
 "research/scalping_lab/substrate/raw/NQ": {"bytes": 1610100000, "files": 61, "rows": 531611712, "cols": ["bip","time","price","volume"], "freq": "tick", "instrument": "NQ", "start": "2025-08-10T18:00:00", "end": "2026-05-20T16:59:59", "git": "ignored", "referenced": true, "note": "48 full + 13 _rth; 15 truncated at 12M rows (CLAIM)"},
 "research/scalping_lab/substrate/raw/ES": {"bytes": 544400000, "files": 39, "rows": 328858165, "cols": ["bip","time","price","volume"], "freq": "tick", "instrument": "ES", "start": "2025-08-13T18:00:00", "end": "2026-05-20T16:59:59", "git": "ignored", "referenced": true},
 "research/scalping_lab/substrate/grid1s/NQ": {"bytes": 60200000, "files": 48, "rows": 3938190, "cols": ["time","last","trades","vol","sflow","bid","bid_upd","ask","ask_upd","mid","spread_t","ret1s_t"], "freq": "1s", "instrument": "NQ", "start": "2025-08-10", "end": "2026-05-20", "git": "tracked", "referenced": true, "note": "recorded lookahead defect in last (CLAIM)"},
 "research/scalping_lab/substrate/sechilo/NQ": {"bytes": 39200000, "files": 45, "rows": 3177752, "cols": ["time","mid_last","mid_high","mid_low","n_ev"], "freq": "1s", "instrument": "NQ", "start": "2025-08-13", "end": "2026-05-20", "git": "tracked", "referenced": true},
 "research/scalping_lab/substrate/sechilo/ES": {"bytes": 27800000, "files": 39, "rows": 2743804, "cols": ["time","mid_last","mid_high","mid_low","n_ev"], "freq": "1s", "instrument": "ES", "start": "2025-08-13", "end": "2026-05-20", "git": "tracked", "referenced": true},
 "research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet": {"bytes": 60700000, "rows": 6466783, "cols": ["time","open","high","low","close","volume"], "freq": "1m", "instrument": "NQ", "start": "2006-01-05T08:59", "end": "2026-05-29T16:59", "git": "ignored", "referenced": true},
 "research/data_internals/{TICK,TRIN,VIX}_1m.parquet": {"bytes": 16800000, "files": 3, "rows": 1335500, "cols": ["time","open","high","low","close"], "freq": "1m RTH-only", "instrument": "$TICK/$TRIN/$VIX", "start": "2022-01-03T09:31", "end": "2026-07-31T15:59", "git": "ignored", "referenced": true},
 "research/multi_market/out/economic_returns.parquet": {"bytes": 1200000, "rows": 89843, "cols": ["date","old_contract","target_contract","overnight","intraday","ret_points","rolled","root","sector","point_value","ret_usd","eligible","obs_idx"], "freq": "daily", "instrument": "24 roots", "start": "2009-03-31", "end": "2026-07-31", "git": "ignored", "referenced": true},
 "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet": {"bytes": 26100000, "rows": 1620044, "cols": ["time","open","high","low","close","volume"], "freq": "1m", "instrument": "NQ", "start": "2022-01-02T18:01", "end": "2026-07-31T16:59", "git": "tracked", "referenced": true},
 "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet": {"bytes": 24800000, "rows": 1620385, "cols": ["time","open","high","low","close","volume"], "freq": "1m", "instrument": "ES", "start": "2022-01-02T18:01", "end": "2026-07-31T16:59", "git": "tracked", "referenced": "yes but registry says NOT EXTRACTED"},
 "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet": {"bytes": 24000000, "rows": 1595378, "cols": ["time","open","high","low","close","volume"], "freq": "1m", "instrument": "YM", "start": "2022-01-02T18:01", "end": "2026-07-31T16:59", "git": "tracked", "referenced": "yes but registry says NOT EXTRACTED"},
 "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet": {"bytes": 23500000, "rows": 1568111, "cols": ["time","open","high","low","close","volume"], "freq": "1m", "instrument": "RTY", "start": "2022-01-02T18:01", "end": "2026-07-31T16:59", "git": "tracked", "referenced": "yes but registry says NOT EXTRACTED"},
 "runs/B01A_BARS_1M/nq_1m_2022_2026.csv": {"bytes": 94990000, "cols": ["time","open","high","low","close","volume","first_bar_of_session"], "freq": "1m", "instrument": "NQ 09-26", "start": "2022-01-02T18:01", "end": "2026-07-31 (spec CLAIM)", "git": "tracked", "referenced": true},
 "runs/W18_XINST_BARS/{es,rty,ym}_3m_2022_2026.csv": {"bytes": 82600000, "files": 3, "cols": ["time","open","high","low","close","volume","first_bar_of_session"], "freq": "3m", "instrument": "ES/RTY/YM 09-26", "start": "2022-01-02", "end": "2026-05-29 (spec CLAIM)", "git": "tracked", "referenced": true},
 "runs/INTERNALS_ACQUIRE_20260827/out/csv/internals_1m_bars.csv": {"bytes": 64820000, "cols": ["symbol","time","open","high","low","close","volume"], "freq": "1m", "instrument": "$TICK/$TRIN/$VIX", "start": "2022-01-03T09:31", "end": "2026-07-31 (derived parquets confirm)", "git": "ignored", "referenced": false},
 "runs/ORDERFLOW_EXPAND_20260827/out/csv/s20260525_ticks.csv": {"bytes": 91240000, "cols": ["bip","time","price","volume"], "freq": "tick", "instrument": "NQ", "start": "2026-05-24T18:00", "end": "2026-05-25 session", "git": "untracked", "referenced": false, "note": "quarantined Memorial-Day session, only copy in repo"},
 "runs/WE_XM_PARITY_20260827/out/we_xm_{xm2,xmparity}.csv": {"bytes": 438700000, "files": 2, "cols": ["timestamp","nq_open","nq_high","nq_low","nq_close","es_close","es_move","rty_close","rty_move","ym_close","ym_move","nq_drive","broad_composite","conflict_flag","desired_direction","decision_ready","entry_request","exit_request","position","realized_pnl"], "freq": "1m", "start": "2022-01-02", "end": "unknown-by-policy", "git": "untracked+ignored", "referenced": false},
 "research/weekly_edge/ninjascript/reference/xm_reference_bars.csv": {"bytes": 58690000, "cols": "same XM decision schema", "freq": "1m", "start": "2025-08-01T00:00", "end": "unknown-by-policy", "git": "ignored", "referenced": true},
 "research/scalping_lab/runs/*/probe_ticks.csv leftovers": {"bytes": 737000000, "files": 5, "cols": ["bip","bar","time","price","volume"], "freq": "tick", "instrument": "NQ x4, ES x1 (es20260715)", "git": "ignored", "referenced": true, "note": "superseded by parquet conversions"},
 "research/03_reverse_engineering/ledgers": {"bytes": 186000000, "files": 10, "freq": "1m/3m", "instrument": "NQU6", "start": "2023-01-02", "git": "tracked", "referenced": true},
 "research/original_trader_reconstruction/data": {"bytes": 4200000, "files": 2, "cols": ["time","open","high","low","close","volume"], "freq": "1m", "instrument": "NQ 06-26 / NQ 09-26", "start": "2026-05-24", "end": "2026-07 (name CLAIM)", "git": "tracked", "referenced": true},
 "runs/U0_UNIFIED_STATE/out/u0_state_table.parquet": {"bytes": 86800000, "rows": 540232, "ncols": 77, "freq": "1m-decision", "instrument": "NQ", "start": "2022-01-02T18:03", "end": "2026-07-31T16:57", "git": "tracked", "referenced": true},
 "runs/AUCTION01_VALUE_STATE/out (3 parquets)": {"bytes": 81400000, "rows": 3081975, "freq": "1s/30s", "instrument": "NQ", "start": "2025-08-13", "end": "2026-05-20", "git": "tracked", "referenced": true},
 "runs/MSLAST_CONTRACT_20260827/out/discovery_substrate.parquet": {"bytes": 13900000, "rows": 139371, "freq": "event/60s+300s features", "instrument": "NQ", "git": "ignored", "referenced": true},
 "research/data_forward_sealed": {"bytes": 37000, "files": 3, "note": "ONLY .md governance docs, ZERO data files", "referenced": true}
}
```

## 8. Answers to the three key questions

**(a) Datasets no current-truth document names:** `internals_1m_bars.csv` (raw internals source, 0 refs), `s20260525_ticks.csv` (only repo copy of the quarantined session, 0 refs), the 5 probe_ticks leftovers (~703 MB incl. an ES 2026-07-15 tick session and NQ 2026-07-14 probe), we_xm_* parity dumps (419 MB), and — as named assets — the git-tracked ES/YM/RTY 1m + 3m bar substrates in runs/ that DATA_ASSET_REGISTRY misclassifies (§2). `data_esnq` itself is named only by GENESIS_CHARTER among non-run docs.

**(b) Claimed datasets that don't exist / differ:** DATA_ASSET_REGISTRY rows 14/17/18 claim ES/RTY/YM 1m are "NOT EXTRACTED" — false as stated: extracted 2022→2026-07-31 parquets exist and are tracked (SM1M_ES/YM/RTY). `research/data_forward_sealed` contains no data despite the name (governance only). Everything else checked matched claims: internals row counts match MANIFEST exactly; store session counts (44/44, 58, 48, 39, 45) match registry; nq1m rows/range match.

**(c) Content ≥ 2026-08-01:** none, anywhere in the repo, by parquet footer stats, CSV heads, and filename scan. Max observed data timestamp: 2026-07-31 16:59:59.944 (metadata). No seal hazard inside the repo; the virgin pool exists only NT8-side.

## 9. Census totals

RAW: 2,774 files matching {parquet,csv,db,sqlite,feather,pkl,json.gz,h5,npz,duckdb} (no .db/.sqlite/.feather/.h5 data stores found — repo data is parquet+csv+json). Aggregate ≈ 9.6 GB, of which the four tick stores ≈ 6.55 GB, probe/tick CSV leftovers ≈ 0.93 GB, bar substrates ≈ 0.45 GB, everything else run outputs/ledgers/registries.
