# DATA_CONTRACT — GENESIS_FREEDATA_CBOE_20260828

Certification layer for the free Cboe volatility complex + CFTC COT. **DATA-CAPABLE
certification only — no return predictability computed, no join to NQ returns, no strategy
object.** All certified tables are mechanically truncated to **< 2026-08-01** by
`research_sdk.seal_guard.truncate_presealed` and asserted by `assert_presealed`
(12 frames asserted, 0 SealError, 463 post-seal rows dropped blind — counts and assertions
printed in `out/gate_table.txt`; the dropped values were never inspected or printed).
Raw quarantine: `raw/` (contains post-seal rows; parse-only, never inspected).
Provenance for every file (exact URL, sha256, bytes, UTC retrieval time, Last-Modified
header, HTTP status): `raw/_MANIFEST.json` — 300 files, 16,298,607 bytes total, 0 unreachable,
caps respected (100 MB total / 30 MB per file). Retrieval date: 2026-08-28 (UTC).
Programs: `out/download_all.py`, `out/certify.py`, `out/diagnose_g6.py`.
Gate verdicts: `out/gate_table.txt` — **8/9 PASS; G6 FAIL recorded** (see §4, not adjusted).

Evidence-status tag for every number quoted below: computed by `certify.py` from the
certified (< 2026-08-01) layer, printed in `gate_table.txt` / `out/contract_stats.json`.

---

## 1. Cboe daily index histories (8 series)

**Files** `certified/idx_{SYM}_daily.parquet` (native columns) + `certified/indices_close_long.parquet`
(long form: symbol, date, close).

| SYM | certified span | rows | columns | weekday gaps in span |
|---|---|---|---|---|
| VIX | 1990-01-02 .. 2026-07-31 | 9,241 | date,open,high,low,close | 303 |
| VIX3M | 2009-09-18 .. 2026-07-31 | 4,242 | date,open,high,low,close | 159 |
| VIX9D | 2011-01-04 .. 2026-07-31 | 3,916 | date,open,high,low,close | 148 |
| VXN | 2009-09-14 .. 2026-07-31 | 4,248 | date,open,high,low,close | 157 |
| VVIX | 2006-03-06 .. 2026-07-31 | 5,073 | date,vvix (close only) | 252 |
| SKEW | 1990-01-02 .. 2026-07-31 | 9,196 | date,skew (close only) | 348 |
| OVX | 2009-09-18 .. 2026-07-31 | 4,240 | date,ovx (close only) | 161 |
| GVZ | 2009-09-18 .. 2026-07-31 | 4,240 | date,gvz (close only) | 161 |

- **Source URLs**: `https://cdn.cboe.com/api/global/us_indices/daily_prices/{SYM}_History.csv`
  (sha256 per file in manifest; Last-Modified headers 2026-08-28, i.e. updated daily).
- **Timestamp semantics (vendor citation)**: the Cboe VIX historical-data page
  (`cboe.com/tradable_products/vix/vix_historical_data/`, fetched 2026-08-28) describes the
  files as *"daily closing values of the Cboe Volatility Index"*. One row per exchange
  trading date; the date is a **trading-day label, no intraday time**. The exact clock time
  at which the daily close is struck (4:00 vs 4:15 p.m. ET) is **NOT stated on the fetched
  page — UNRESOLVED-DETAIL**; do not build anything that needs minute-level close timing
  from these files without resolving it against Cboe index methodology documents.
- **Units**: index points (annualized implied-vol percentage points for vol indices; SKEW is
  a 100-centered index, not a vol level).
- **Revision policy — evidence, not assumption**: the vendor page states no revision policy;
  its disclaimer says data is *"furnished without responsibility for accuracy"*. Treat as
  **restate-capable**. Known one-time restatement class: the VIX methodology change (2003)
  retro-computed history — the 1990-2003 rows in `VIX_History.csv` are back-calculated under
  the current methodology, not as-published values. Mechanical drift detection: the sha256
  baseline recorded today allows any future re-fetch to prove/disprove silent restatement.
- **Missingness**: weekday gaps ≈ US market holidays (~9/yr; VIX 303 gaps over 36.6 yr is
  holiday-consistent). 0 duplicate dates in every series. VIX9D contains 0 null closes;
  OHLC nulls per series recorded in `out/contract_stats.json`.
- **Coverage caveat**: free VXN history starts **2009-09-14** (the index existed from 2001;
  the free CDN file does not carry it back). Same 2009-09 left edge for VIX3M/OVX/GVZ.
- 19-20 post-seal rows were blind-dropped per file (exact per-file counts in gate_table.txt).

## 2. VX futures daily settlements, per contract (monthly contracts)

**File** `certified/vx_settlements_daily.parquet` — 46,412 rows, 272 contract files certified,
span 2004-03-26 .. 2026-07-31 (first certified trade date = VX launch date), 0 duplicate
(trade_date, contract, era) rows. Columns: trade_date, contract_label, contract_year,
contract_month, expiry_date_file, era, open, high, low, close, settle, change, total_volume,
efp, open_interest, source_file, legacy_scale_flag.

- **Source URLs**: modern era (expiries 2013-01 .. 2027-05, 173 files):
  `https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{expiry-date}.csv`;
  archive era (2004-2012, 100 files):
  `https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_{monthcode}{yy}_VX.csv`.
  Vendor page labels these *"CFE Price and Volume Detail for Select Futures Products from
  2013 to Current"* and the settlement archive *"from 2004 - 2013"*.
- **Contract identity (gated, G4)**: monthly contracts only, identified two independent ways
  and cross-checked per file with **0 mismatches over 272 files**: (a) filename — modern files
  are named by final-settlement date generated from the 30-days-before-next-month's-3rd-Friday
  rule (166 files at the computed Wednesday, 7 at Wednesday−1 = holiday-shifted Tuesday);
  archive files by month code; (b) the in-file `Futures` label, format `F (Jan 2013)` (modern)
  / `F (Jan 05)` (archive). Pure month codes only — **no weekly contract was captured**.
  `expiry_date_file` is populated for the modern era; NaT for archive (expiry not in file).
  Contract-months with no file: 2004-01..04 (pre-launch), 2004-12, 2005-04, 2005-07, 2005-09
  (early listing gaps — HTTP-probed absent, recorded in manifest); 2027-06.. (not yet listed).
  One file (VX_2027-05-18) had 0 pre-seal rows and certified empty.
- **Timestamp semantics**: `Trade Date` = CFE business date (one row per contract per trading
  day). Settle = the exchange daily settlement price for that date. CFE regular trading hours
  per the VX spec page (fetched 2026-08-28): *"Regular 8:30 a.m. to 3:00 p.m."* (Chicago time;
  the page does not print the timezone label — Cboe futures docs are Chicago-time —
  UNRESOLVED-DETAIL flagged). The precise daily-settlement window/procedure is in the CFE
  Rulebook, **not machine-quotable this session — UNRESOLVED-DETAIL**; the settlement page
  states settlements can be discretionary: *"Indicates that Exchange exercised discretionary
  authority to determine daily settlement price."*
- **Units — CRITICAL 10× TRAP (measured, not assumed)**: modern prices are VIX points,
  **$1000/point** (spec page: "VIX Symbol 1000 Multiplier"). Archive rows **before 2007-03-26
  are on the legacy 10× price basis**: certify.py measured median(front-contract settle /
  VIX close) = **10.30 pre-2007-03-26 vs 1.01 after** (printed in gate_table.txt). Every such
  row carries `legacy_scale_flag = "LEGACY_10X_SUSPECT"` (3,942 rows). No values were altered.
- **Revision policy**: no vendor statement; settlement prices are exchange records and in
  practice final once published, but discretionary re-marks exist (quote above). sha256
  baseline recorded for drift detection. Ragged trailing fields in archive files were
  truncated at parse (156 lines across 4 archive files; all extra fields empty — none dropped
  data).
- **Missingness**: median 9 contracts quoted per trade date; early archive years are sparse
  (see listing gaps above). Zero-volume rows retain OHLC semantics of the vendor file.

## 3. CFE daily volume + open interest by product (cfevoloi)

**File** `certified/cfe_voloi_daily.parquet` — 5,624 rows × 89 columns,
span 2004-03-26 .. 2026-07-31, 0 duplicate dates, 207 weekday gaps (holidays).

- **Source URL**: `https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/cfevoloi.csv`
  (page label: *"CFE Daily Volume and Open Interest by Product"*, coverage 2004→current).
- **Timestamp semantics**: `Date` = CFE business date; one row per date; per-product
  `{PRODUCT} VOLUME` / `{PRODUCT} OI` column pairs. VX lives in
  `VOLATILITY INDEX VOLUME` / `VOLATILITY INDEX OI` (exact certified column names in
  contract_stats.json). OI is the end-of-day figure as labeled by the vendor; intra-day
  timing not stated — UNRESOLVED-DETAIL.
- **Units**: contracts (volume), open contracts (OI).
- **Revision policy**: none stated; same disclaimer text as §1 (the file leads with it);
  sha256 baseline recorded. Missingness: product columns are empty outside each product's
  listing life (delisted CFE products dominate the 89 columns).

## 4. CFTC COT — Traders in Financial Futures (TFF), futures-only

**File** `certified/cot_tff_futures_only.parquet` — 19,047 rows, 80 markets
(VIX + equity-index name filter `VIX|S&P|NASDAQ|RUSSELL|DOW JONES|DJIA|MSCI|NIKKEI`),
span 2006-06-13 .. 2026-07-28. VIX futures: **982 reports**, 2006-08-29 .. 2026-07-28.

- **Source URLs**: `https://www.cftc.gov/files/dea/history/fut_fin_txt_{2010..2026}.zip`
  (annual) + `fin_fut_txt_2006_2016.zip` (used only for pre-2010 rows; deduped on
  (CFTC_Contract_Market_Code, report_date)).
- **Timestamp semantics — the causality-critical fact (vendor citation)**: cftc.gov COT page
  (fetched 2026-08-28): *"The COT Report is generally published each Friday at 3:30 pm Eastern
  Time (US), using the data from the immediately preceding Tuesday of that week."* The
  `report_date` column here is the **as-of Tuesday**; the numbers are **not knowable until
  Friday 15:30 ET (3-day lag)**. Any future study MUST lag accordingly.
- **As-of weekday evidence (G6 diagnostic, printed)**: 1,009/1,023 distinct as-of dates are
  Tuesdays; the 14 exceptions (13 Mon, 1 Wed) are all holiday weeks (Jul-4, Christmas/New
  Year, 2007-01-03 mourning-day closure, Veterans-Day weeks) — full list in gate_table.txt.
  Row-level Tuesday share 98.81%, which **failed the preregistered G6 clause "≥99% Tuesdays"**.
  The gate is recorded FAIL and not adjusted; the miss is a holiday-shift property of the
  vendor's as-of convention, now documented here, not a data defect.
- **Revision policy (vendor citation)**: *"No, historical data is not updated once published."*
  (cftc.gov COT FAQ, fetched 2026-08-28). Corroborating mechanical evidence: the 2006-2016
  combined file's Last-Modified header is **2018-01-04** — untouched for 8+ years.
- **Missingness**: VIX futures are absent 59 report-weeks in-span (plus 9 holiday-shift weeks
  covered by Monday as-of), concentrated 2008-2010 (23 in 2009, 28 in 2010) — VIX futures
  fell below CFTC reporting standards in that era. By-year table in gate_table.txt.
  Vendor name quirk: `Market_and_Exchange_Names` appears both with and without a trailing
  space (*"VIX FUTURES - CBOE FUTURES EXCHANGE"* / same + space) — strip before grouping.
- **Units**: contracts (positions/OI); TFF categories Dealer / Asset Manager / Leveraged
  Funds / Other Reportables, long/short/spread, futures-only.

## 5. Cross-source sanity (sanity only, NOT alpha)

corr(VIX close, VXN close) levels = **0.9460** on 4,246 overlapping certified days
(2009-09-14 .. 2026-07-31) — printed by certify.py. Plus the §2 10×-era ratio check
(archive front settle / VIX ≈ 10.30 → 1.01 across 2007-03-26).

## 6. What this layer is NOT

Not alpha evidence of any kind; no NQ join performed; no predictive statistic computed.
`evidence_ceiling: DATA-CAPABLE`. Post-2026-07-31 rows exist ONLY inside `raw/` quarantine
and were never read as values. $0 spent; no credential used; no paid endpoint touched.
