# CROSS-ASSET DATA / ROLL / COST INVENTORY — Wave 0

**Built 2026-09-06 · run `runs/CROSSASSET_WAVE0_INVENTORY_20260906/` · READ-ONLY census, $0, no
extraction, no seal touched.** Foundation for the cross-asset campaign
(`research/cross_asset/CAMPAIGN_STATE.md`). Every cell below is measured from an actual file, not
inherited from a provisional table. Authorities: `research/data/NT8_CAPABILITY_CENSUS.csv`
(51,936 file rows, `research_sdk/data_census.py`), the six SM1M parquets opened directly, and the
SM1M `build_meta.json` / `MANIFEST.md`. Raw per-root counts:
`runs/CROSSASSET_WAVE0_INVENTORY_20260906/roots_seen.csv`.

> **What the census measures.** `data_census.py` reads file *names, sizes, mtimes* under
> `~/Documents/NinjaTrader 8/db/{day,minute,tick,replay}` — it never opens a `.ncd` for content, so
> running it consumes no data seal. A `minute` PAYLOAD row = a calendar-date `.ncd` with real bars
> on disk; it is **file presence, not a trading session**. Session counts below come from opening the
> extracted parquets. **Calendar-date file counts run higher than trading sessions** (Sundays,
> roll-window duplicate dates across contract dirs) — this is the single most common miscount in the
> provisional table.

---

## 1. Master table

Legend — **1-min extracted?** = materialized to a repo parquet. **1-min on-disk** = `.ncd` bars
present in NT8 db but not extracted. **daily on-disk** = per-contract day `.ncd` present in NT8 db
(NOT a repo parquet). tick$/pt$ MEASURED only for NQ/MNQ; all others **MODELED-STANDARD** CME spec.

| root | class | 1-min EXTRACTED (parquet / sessions / span) | 1-min ON-DISK unextracted (files / span) | daily ON-DISK (span) | roll treatment | tick / tick$ / point$ | commission RT | micro pair | prior-consumed? | freeze candidate? |
|---|---|---|---|---|---|---|---|---|---|---|
| **NQ** | equity idx | ✅ **spine** `scalping_lab/.../nq1m_2005_202605.parquet` 2006-01-05→2026-05-29 (6,223 sess) **+ ext** `SM1M_SUBSTRATE` **1,184 sess** 2022-01-02→2026-07-31 (1,620,044 rows) | (files to 2026-08-31 = sealed, unread) | ✅ 2009–2026 (71 ctr) | merge back-adjusted additive (ext) | 0.25 / $5.00 / $20 | **$4.36 (MEASURED)** | MNQ | 🔴 ANCHOR — live P1, exhaustively consumed | ❌ (anchor) |
| **ES** | equity idx | ✅ `SM1M_ES_SUBSTRATE` **1,184 sess** 2022-01-02→2026-07-31 (1,620,385 rows) | 1,770 files 2021-01-03→2026-08-31 | ✅ 2009–2026 (71 ctr) | merge back-adj additive (**inferred** — see §3) | 0.25 / $12.50 / $50 | ~$4.36 (MODELED) | MES | 🟠 DISCOVERY_CONSUMED — Engine-3 cross-mkt slates (dev 2022-25) + ES tick in ESNQ_V1 + XINST01 now | ❌ pre-seal burned; blind ES∩NQ 15 sess UNSPENT (tick) |
| **RTY** | equity idx | ✅ `SM1M_RTY_SUBSTRATE` **1,177 sess** 2022-01-02→2026-07-31 (1,568,111 rows) | 1,763 files 2021-01-03→2026-08-31 | ✅ 2009–2026 (12 ctr day) | merge back-adj additive (**inferred**) | 0.10 / $5.00 / $50 | ~$4.36 (MODELED) | M2K (absent) | 🟠 DISCOVERY_CONSUMED — Engine-3 dispersion catch-up (killed) + XINST01 now | ❌ pre-seal burned |
| **YM** | equity idx | ✅ `SM1M_YM_SUBSTRATE` **1,177 sess** 2022-01-02→2026-07-31 (1,595,378 rows) | 1,764 files 2021-01-03→2026-08-31 | ✅ 2009–2026 (71 ctr) | merge back-adj additive (**inferred**) | 1.0 / $5.00 / $5 | ~$4.36 (MODELED) | MYM (day only) | 🟠 DISCOVERY_CONSUMED — Engine-3 slate-5 Europe(YM)→NQ lead (FAIL) + XINST01 now | ❌ pre-seal burned |
| **MNQ** | equity idx (micro) | ✅ `SM1M_MNQ_SUBSTRATE` **1,189 sess** 2021-12-27→2026-07-31 (1,627,987 rows) — extracted 2026-09-06 | 1,453 files 2021-12-30→2026-08-24 | ✅ 2019–2026 (30 ctr) | merge back-adj additive (offsets +765→+3,378 pt; vol = true front, exact vs day store) | 0.25 / $0.50 / $2 | **$1.30 (MEASURED)** | (is the micro of NQ) | 🟠 = NQ twin; live execution instrument (MX01), fresh as research surface | ❌ not orthogonal to NQ |
| **ZB** | rates (30Y) | ✅ `SM1M_ZB_SUBSTRATE` **923 sess** 2022-12-27→2026-07-31 (1,086,151 rows) — extracted 2026-09-06, 1/32 grid restored | 1,124 files 2023-01-02→2026-08-05 | ✅ 2009–2026 (71 ctr) | merge back-adj additive (median −41/32nds; vol = true front, exact vs day store) | 1/32 = 0.03125 / $31.25 / $1,000 | ~$4.36 (MODELED, CBOT) | (micro UB none) | 🟠 DISCOVERY_CONSUMED — G2_F13 MC-57 ZB→NQ RV (FAIL, today) + XINST01 now | ❌ pre-seal burned today |
| **CL** | energy | ❌ | ✅ **1,475 files** 2022-01-02→2026-08-05 (deep) | ✅ 2009–2026 (213 ctr) | (unbuilt — will be merge back-adj on extract) | 0.01 / $10.00 / $1,000 | ~$4.36 (MODELED, NYMEX) | MCL (day only) | 🟢 **UNTOUCHED** — inventory mentions only, 0 experiments | ✅ **PRIME** deep-intraday holdout (extract & freeze) |
| **ZN** | rates (10Y) | ❌ | ⚠️ 190 files 2025-12-30→2026-08-05 (thin ~6mo) | ✅ 2009–2026 (71 ctr) | (unbuilt) | 1/64 = 0.015625 / $15.625 / $1,000 | ~$4.36 (MODELED) | — | 🟢 untouched (thin) | daily holdout; intraday too thin |
| **6J** | FX (JPY) | ❌ | ⚠️ 190 files 2025-12-30→2026-08-05 (thin) | ✅ 2009–2026 (71 ctr) | (unbuilt) | 0.0000005 / $6.25 / — | ~$4.36 (MODELED) | — | 🟢 untouched (thin) | daily holdout; intraday too thin |
| **MGC** | metals (micro) | ❌ | ⚠️ 187 files 2025-12-30→2026-08-03 (thin) | ✅ 2016–2026 (52 ctr) | (unbuilt) | 0.10 / $1.00 / $10 | ~$1.30 (MODELED) | (micro of GC) | 🟢 untouched (thin) | daily holdout; intraday too thin |
| **MES** | equity idx (micro) | ❌ | ⚠️ **28 files** 2026-03-30→2026-04-30 (negligible) | ✅ 2026 (1 ctr) | (unbuilt) | 0.25 / $1.25 / $5 | ~$1.30 (MODELED) | (micro of ES) | 🟢 untouched | too thin to freeze |
| **GC** | metals | ❌ **1-min ABSENT** | ❌ **none** (only MGC) | ✅ 2009–2026 (91 ctr) | per-contract (day store) | 0.10 / $10.00 / $100 | ~$4.36 (MODELED) | MGC | 🟢 untouched | **DAILY-ONLY** holdout |
| **6E** | FX (EUR) | ❌ **1-min ABSENT** | ❌ **none** (only 6J) | ✅ 2009–2026 (71 ctr) | per-contract (day store) | 0.00005 / $6.25 / $125,000 | ~$4.36 (MODELED) | — | 🟢 untouched | **DAILY-ONLY** holdout |
| **SI** | metals | ❌ | ❌ none | ✅ 2009–2026 (89 ctr) | per-contract | 0.005 / $25.00 / $5,000 | ~$4.36 (MODELED) | SIL (absent) | 🟢 untouched | DAILY-ONLY |
| **HG** | metals | ❌ | ❌ none | ✅ 2016–2025 (16 ctr) | per-contract | 0.0005 / $12.50 / $25,000 | ~$4.36 (MODELED) | MHG (1 day) | 🟢 untouched | DAILY-ONLY (shallow) |
| **NG** | energy | ❌ | ❌ none | ✅ 2009–2026 (213 ctr) | per-contract | 0.001 / $10.00 / $10,000 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **6A** | FX (AUD) | ❌ | ❌ none | ✅ 2009–2026 (71 ctr) | per-contract | 0.0001 / $10.00 / $100,000 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **6B** | FX (GBP) | ❌ | ❌ none | ✅ 2009–2026 (71 ctr) | per-contract | 0.0001 / $6.25 / $62,500 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **6C** | FX (CAD) | ❌ | ❌ none | ✅ 2009–2026 (71 ctr) | per-contract | 0.00005 / $5.00 / $100,000 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **6S** | FX (CHF) | ❌ | ❌ none | ✅ 2009–2026 (71 ctr) | per-contract | 0.0001 / $12.50 / $125,000 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **ZF** | rates (5Y) | ❌ | ❌ none | ✅ 2009–2026 (71 ctr) | per-contract | 0.0078125 / $7.8125 / $1,000 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **ZT** | rates (2Y) | ❌ | ❌ none | ✅ 2009–2026 (71 ctr) | per-contract | 0.0078125 / $7.8125 / $2,000 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **ZC** | ags (corn) | ❌ | ❌ none | ✅ 2009–2026 (89 ctr) | per-contract | ¼¢ = 0.25 / $12.50 / $50 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **ZW** | ags (wheat) | ❌ | ❌ none | ✅ 2009–2026 (89 ctr) | per-contract | ¼¢ = 0.25 / $12.50 / $50 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **ZS** | ags (soybean) | ❌ | ❌ none | ⚠️ 2016–2026 (5 ctr, sparse) | per-contract | ¼¢ = 0.25 / $12.50 / $50 | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY (sparse; Sep never resolves) |
| **ZL** | ags (soy oil) | ❌ | ❌ none | ✅ 2009–2026 (134 ctr) | per-contract | 0.0001 / $6.00 / 60k lb | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **ZM** | ags (soy meal) | ❌ | ❌ none | ✅ 2009–2026 (134 ctr) | per-contract | 0.10 / $10.00 / 100 ton | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY |
| **HO** | energy | ❌ | ❌ none | ✅ 2016–2025 (32 ctr) | per-contract | 0.0001 / $4.20 / 42k gal | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY (shallow) |
| **RB** | energy | ❌ | ❌ none | ✅ 2016–2025 (32 ctr) | per-contract | 0.0001 / $4.20 / 42k gal | ~$4.36 (MODELED) | — | 🟢 untouched | DAILY-ONLY (shallow) |
| **VX** | volatility | ❌ | ⚠️ 4 files 2026-06-01→07-29 (negligible) | ✅ 2026 (2 ctr) | per-contract | 0.05 / $50.00 / $1,000 | ~$4.36 (MODELED) | VXM (absent) | 🟢 untouched | see CBOE settlements (below) |

**Non-futures daily surfaces already materialized to parquet** (not in the table — not tradable
roots, but usable predictors, strict-chronology): CBOE vol-index complex `VIX/VIX3M/VIX9D/VXN/VVIX/
GVZ/OVX/SKEW` (VIX back to 1990), `vx_settlements_daily`, `cfe_voloi_daily`, `cot_tff_futures_only`
— all in `runs/GENESIS_FREEDATA_CBOE_20260828/certified/`. ETF/index proxies (`SPY QQQ IWM TLT GLD
SLV USO UNG DBC EEM EFA FXE FXY UUP IEF`, treasury curve, `SVXY VIXY`) in `research/breadth_lab/*/
data/` — these belong to the **CLOSED_FAIL** BREADTH01/02/03 replications and are ETF proxies, **not
the futures roots**.

---

## 2. Classification — INTRADAY-READY / DAILY-ONLY / NEEDS-EXTRACTION / ABSENT

- **INTRADAY-READY** (extracted 1-min parquet, deep, seal-clean, back-adjusted, opened & verified):
  **NQ, ES, RTY, YM, MNQ, ZB.** Six substrates, identical schema `time,open,high,low,close,volume`,
  END-stamped ET, no ±1-min shift, all end 2026-07-31 (seal-respecting). NQ additionally has the
  2006+ spine.
- **NEEDS-EXTRACTION** (deep 1-min ON DISK, unextracted; local-path recompile per CLAUDE.md §6):
  **CL** — the only deep unextracted intraday surface (1,475 datefiles, 2022-01→2026-08). Prime.
- **NEEDS-EXTRACTION but THIN** (only ~6 months on disk, 2025-12+): **ZN, 6J, MGC** (~190 files
  each); **MES** (28 files, ~1 month) and **VX** (4 files) are negligible.
- **DAILY-ONLY** (no usable local 1-min; per-contract day `.ncd` on disk 2009–2026, unextracted):
  **GC, 6E, SI, NG, 6A, 6B, 6C, 6S, ZF, ZT, ZC, ZW, ZL, ZM** (deep); **HG, HO, RB, ZS** (shallow/
  sparse). Legit for daily-swing native engines — never fake intraday history here.
- **1-MIN ABSENT (surprises vs the roots-to-check list):** **GC has NO minute data** (only its micro
  MGC, thin); **6E has NO minute data** (only 6J, thin); **SI / HG / NG have NO minute data**
  (daily only). Conversely, two roots **not** on the check-list are present intraday: **MES** (micro
  S&P, 28 files) and **VX** (VIX future, 4 files) — both too thin to use.

---

## 3. Roll / back-adjustment treatment (CRITICAL — the fake-alpha axis)

**All six extracted substrates were built the same way:** `SWMinuteExport_v1` requesting the
NT8 symbol `"<ROOT> 09-26"` over a multi-year window via `RunStrategyBacktest`. Because a single
delivery month trades only for months, a 4.6-year × ~1.6M-bar series can only be NT8's
**merge back-adjusted continuous front-month chain** (Merge Policy = *Merge Back Adjusted*, which is
**additive / difference-based**, not ratio).

| substrate | roll treatment | documentation | evidence |
|---|---|---|---|
| NQ (ext) | merge back-adj **additive** | `build_meta.json`: "NQ 09-26 (merge back-adjusted)" | explicit |
| MNQ | merge back-adj **additive** | MANIFEST: cumulative offsets **+765 pt** (late-25) → **+3,378 pt** (early-22) | explicit; vol = true front, **exact** vs day store |
| ZB | merge back-adj **additive** | MANIFEST: anchor offset ≈ −1/32; median **−41/32nds** late-25 | explicit; vol **exact** vs day store; 1/32 grid restored |
| **ES** | merge back-adj additive | build_meta says only **"resolved ESU6"** — **NOT annotated** | **INFERRED** (4.6yr/1.62M bars ⇒ continuous chain). **FLAG: document before any level/return use.** |
| **RTY** | merge back-adj additive | build_meta says only **"resolved RTYU6"** | **INFERRED** — same flag |
| **YM** | merge back-adj additive | build_meta says only **"resolved YMU6"** | **INFERRED** — same flag |

**Roll-artifact flags (what can fake alpha, and what cannot):**

1. ✅ **Intraday continuity is CLEAN.** Additive back-adjustment removes the roll gap *inside* the
   series, so there is no spurious roll jump between sessions. Verified by opening every parquet:
   max intrasession |Δclose| is a genuine volatility event (NQ 481 pt, YM 903 pt, ES 130 pt), p99.99
   ≤ ~2–3 % of level — **no anomalous mid-session stitch discontinuities**. So intraday
   bar-to-bar/return signals are **not** contaminated by roll seams.
2. 🔴 **Absolute price LEVELS in history are shifted** by the cumulative offset (largest far from the
   anchor: MNQ early-2022 ≈ +3,378 pt above true). Therefore **% returns / ratio features / level
   thresholds computed on back-adjusted price are WRONG** (denominator is a shifted level). Use
   **point differences** or roll-aware returns. `G2_F13` did this correctly (ZB *points* state).
   Any candidate whose edge depends on absolute price level or naive pct-return on these series is
   **invalid** until re-derived on points/true prices.
3. ✅ No series goes negative (all min-close > 0), so additive offset did not distort sign.
4. 🔴 **The daily multi-market store is per-contract, NOT continuous** — "continuous contracts do not
   exist here" (`ES ##-##` and bare `ES` both return 0 bars). Every daily study must roll
   contract-by-contract with a **causal** roll, and the returned `instrument` symbol is
   decade-ambiguous (`ES 12-06` and `ES 12-16` both show `ESZ6`) — read depth from bar dates, never
   the symbol.

---

## 4. Contract economics + cost

- **MEASURED (Lifetime template, `research/operational/COST_MODEL.md`):** NQ **$4.36/ctr RT**,
  MNQ **$1.30/ctr RT**. Research adds a modelled spread on top for traded candidates (P1 $14.44,
  XM $12.50 — NQ-specific).
- 🔴 **Everything else is MODELED-STANDARD and FLAGGED.** The repo has **no measured commission and
  no measured spread for any non-NQ instrument.** Tick size / tick value / point value in §1 are the
  published CME/CBOT/NYMEX/COMEX contract specs (reliable); the commission column is a modelled
  Lifetime-template proxy (~$4.36 full-size, ~$1.30 micro) and must be re-measured or bounded before
  any cost-sensitive cross-asset claim. **Never call a modelled non-NQ cost "all-in."**
- Per campaign discipline: every candidate needs optimistic/base/conservative/stress cost bands and
  must survive +1 tick; a rates/ag/FX instrument's spread and commission can dominate its thin edge.
- **Micro pairs (data reality):** NQ/**MNQ** ✅ both extracted (deep). ES/**MES** — MES 1-min is
  negligible (28 files); use ES for research, MES only for capital-efficiency sizing math. GC/**MGC**
  — GC 1-min absent, MGC thin. CL/**MCL** — MCL day only. RTY/M2K, YM/MYM, SI/SIL: micro effectively
  absent locally.

---

## 5. Pristine-data freeze audit

**Global seal binds every instrument.** `≥ 2026-08-01` is VIRGIN for all roots (CLAUDE.md §5). The
census shows sealed-window *files on disk* (e.g. NQ minute to 2026-08-31, CL/ZB to 2026-08-05) but
their **contents were never read** — every extracted parquet stops at 2026-07-31, and the census
only reads names/sizes. The `2026-05-31→07-31` window is BURNED. The virgin forward pool is the
cleanest cross-instrument holdout available.

**Per-instrument pre-seal consumption (what has been *read into an experiment*, not merely
extracted):**

| root | consumed by | pre-seal holdout still clean? |
|---|---|---|
| NQ | live P1 + the entire campaign history | none (anchor) |
| ES | Engine-3 cross-market slates (SMV2K/P/X/AB + slate-5, `merged_3m_dev` 2022-25 dev) · ES tick/BBO in `ESNQ_V1` (44 dev sess) · `XINST01` running now | 1-min pre-seal **burned**; the **ESNQ_V1 blind ES∩NQ 15-session tick pool is UNSPENT** (`mu_claim=0`, power 0, withheld) |
| RTY | Engine-3 dispersion catch-up (killed) · `XINST01` now | 1-min pre-seal **burned** |
| YM | Engine-3 slate-5 Europe(YM)→NQ lead (FAIL) · `XINST01` now | 1-min pre-seal **burned** |
| ZB | `G2_F13` MC-57 ZB→NQ RV forecast (DISCOVERY_CONSUMED, FAIL, 364 test sess, **today**) · `XINST01` now | 1-min pre-seal **burned today** (points state) |
| MNQ | extracted today; is NQ's twin / live execution port | not orthogonal — no independent holdout value |
| **CL** | **nothing** — appears only in inventory/atlas docs, 0 experiments | ✅ **entire 2022→2026 pre-seal 1-min is UNTOUCHED** — the best deep-intraday holdout in the book (freeze at extraction) |
| ZN, 6J, MGC, MES, VX | nothing | untouched but thin (≤~6 mo intraday) |
| daily multi-market (GC, 6E, SI, NG, ags, FX, rates …) | only the TSMOM depth-chronology *probe*; the closed BREADTH01-03 used **ETF proxies**, not these futures | ✅ the per-contract daily `.ncd` store (2009→2026) is **effectively untouched** for the actual futures roots — freezable, but per-contract/causal-roll |

**Freeze recommendation.** (1) The `≥2026-08-01` virgin pool for every instrument. (2) **CL** as the
one clean *deep-intraday* single-instrument holdout — extract it under a MANIFEST, then freeze a
chronological block before any CL discovery. (3) The daily multi-market store for slow-signal
holdouts. ES/RTY/YM/ZB pre-seal intraday should be treated as **DISCOVERY_CONSUMED** — not usable as
a fresh holdout without a forward window.

---

## 6. Corrections to `CAMPAIGN_STATE.md` §"Data reality (PROVISIONAL)" (report only — coordinator integrates)

1. **ES** "✅ 1,427 sess" → **1,184 trading sessions** (parquet, 18:00→17:00 ET rule). 1,770 is the
   census calendar-date file count.
2. **RTY** "✅ 1,419 sess" → **1,177 sessions**.
3. **YM** "✅ 1,419 sess" → **1,177 sessions**.
4. **ZB** "✅ 1,114 sess 2022-12+" → **923 trading sessions**, span 2022-12-27→2026-07-31 (1,124 =
   census file count; 1,114 was DATA_VERDICT's estimate). Confirmed additive back-adj, 1/32 grid
   restored exactly.
5. **NQ** SM1M ext is **1,184 sessions** (not "1,427"); the deep spine is separate (2006+).
6. **MNQ** is now **EXTRACTED** (1,189 sess, 2021-12→2026-07) — add it as INTRADAY-READY (micro-NQ
   twin, not orthogonal).
7. **CL** "1,481 sess ON DISK" → 1,475 minute-Last PAYLOAD datefiles 2022-01-02→2026-08-05; still
   unextracted; **UNTOUCHED** → mark as the prime intraday freeze candidate.
8. **GC** "❓ not confirmed local" → **RESOLVED: GC 1-min ABSENT** locally (only micro MGC, thin).
   GC = DAILY-ONLY.
9. **6E** "❓ not confirmed local" → **RESOLVED: 6E 1-min ABSENT** locally (only 6J, thin). 6E =
   DAILY-ONLY.
10. **ZN** "~185 sess only" → confirmed 190 datefiles 2025-12-30→2026-08-05, on disk, unextracted,
    thin (~6 mo). Daily-only for practical intraday purposes.
11. Provisional "MGC/6J/SI/HG/NG/6B/6A/ZF thin/absent 1-min" → precisely: MGC(187)/6J(190) thin-
    present; **SI/HG/NG/6B/6A/ZF have NO 1-min at all** (daily only). Add **MES**(28)/**VX**(4) as
    present-but-negligible surprises.
12. Reframe the "daily (inventory)" column: futures daily is **ON DISK** as per-contract NT8 day
    `.ncd` (2009–2026), **not merely "via connection"** — but **NOT extracted to parquet**.
    Materialized daily parquet exists only for the CBOE vol-index complex + COT + VX settlements, and
    (closed) ETF proxies — none are the futures roots.
