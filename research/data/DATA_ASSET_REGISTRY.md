# DATA ASSET REGISTRY

**GENERATED FROM MEASUREMENT by `research/data/build_registry.py` at `d013f62`. Do not hand-edit — regenerate.**

---

## ⚠️ The standing rule this registry exists to enforce

> ### **INSTRUMENT-DATES ARE NOT DISTINCT USABLE SESSIONS.**

Three counts for NQ tick were circulating, all *correct about different populations* — which is exactly how a power claim goes wrong:

| figure | definition | class | may be used for |
|---:|---|---|---|
| **310** | dates with ≥ 1 `Last` `.ncd` file, pre-seal | **FILE PRESENCE** | planning extraction |
| **262** | the above minus the 48 already extracted (runlist rows) | **FILE PRESENCE** | planning extraction |
| **243** | of those, `last_frac ≥ 0.90` of required session hours | **USABLE SESSION** | **power** |
| **99** | quote-complete ≥ 90 % | **USABLE SESSION** | **power, quote features only** |

`310 − 48 = 262` exactly. **Only the USABLE SESSION class may enter a power calculation.** A stale `139` also circulated: it was the pre-correction date-level `bbo_complete=False` count and is **retired**.

## ⚠️ Corrections this measurement forced

- **Truncated old-substrate files: 15, not 17.** The 17 came from the old MANIFEST's `capped` column, which was computed over 61 rows including `_rth` supplements. Measuring the 48 session parquets directly gives **15**. Earlier statements of 17 are wrong.

## ⚠️ CORRECTION 2026-08-27 — multi-market depth is 2009, not 2016

The `Multi-market DAILY via connection` row below says **"2016 probe"**. That was the INVENTORY's
own probe grid (2016/2019/2022/2025), **not a measured floor** — nothing beneath 2016 was ever asked.
Measured directly (`runs/TSMOM_DEPTH_CHRONOLOGY_20260827/`): **21 of 25 roots serve December 2009**,
and ES returns nothing at 2007 or 2008. **Usable history is ~17.6 years, not 10.**

Two mechanics that must travel with that row:
- **continuous contracts do not exist here** — `ES ##-##` and bare `ES` both return 0 bars, so every
  market is assembled contract by contract and a causal roll is mandatory;
- **the returned `instrument` field is decade-ambiguous** — `ES 12-06` and `ES 12-16` both display
  as `ESZ6`. Depth must be read from returned **bar dates**, never from the symbol.

## Materialization status

- **NQ quote-FULL materialized: 98 of a 99 ceiling** — this lane is essentially exhausted on this disk.
- **NQ Last-usable materialized: 102 of a 243 ceiling** — 141 sessions remain extractable for the signed-flow lane.

## Registry

> 🔴 **PATCHED 2026-09-05 — the machine census is the authority, this table is a VIEW.**
> `research_sdk/data_census.py` + `research/data/NT8_CAPABILITY_CENSUS.csv` (51,936 rows) are
> authoritative (`research/data/DATA_VERDICT_20260831.md`); any absence claim must cite the census,
> never this table. Known rows this table still under-reports (per the census):
> **MNQ tick** ~186 dates Last-only 2026-01-01→08-05 (128 pre-burn, 0 extracted) ·
> **NQ minute Bid/Ask** 81 sessions 2026-05-10→08-11 (0 extracted, spread-capable) ·
> **NQ full-BBO unextracted remainder** ~129 pre-seal sessions ·
> certified daily VIX-complex/VX-settlements/COT-TFF assets in `runs/GENESIS_FREEDATA_CBOE_20260828/certified/`.

| asset | symbol | resolution | series | first | last | usable_sessions | extraction | cost | evidence_class | seal |
|---|---|---|---|---|---|---|---|---|---|---|
| NQ 1-minute bars (nq1m_base) | NQ | 1-minute | Last OHLCV | 2006-01-05 08:59:00 | 2026-05-29 16:59:00 | 6223 | MATERIALIZED | $0 | STRUCTURAL | pre-2026-08-01 only |
| NQ 1-minute bars (nq1m_ext) | NQ | 1-minute | Last OHLCV | 2022-01-02 18:01:00 | 2026-07-31 16:59:00 | 1427 | MATERIALIZED | $0 | STRUCTURAL | pre-2026-08-01 only |
| NQ tick+BBO (OLD scalping_lab v1) | NQ | tick | Last+Bid+Ask (bip 0/1/2) | 2025-08-11 | 2026-05-20 | 48 | MATERIALIZED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| NQ tick+BBO (NEW v2) | NQ | tick | Last+Bid+Ask (bip 0/1/2) | 2025-10-15 | 2026-07-31 | 58 | MATERIALIZED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| NQ tick+BBO (UNION, materialized) | NQ | tick | Last+Bid+Ask | 2025-08-11 | 2026-07-31 | 104 | MATERIALIZED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| NQ grid1s (1-sec L1 grid, has sflow) | NQ | 1-second | derived L1 | 2025-08-11 | 2026-05-20 | 48 | MATERIALIZED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| NQ sechilo (per-sec mid hi/lo) | NQ | 1-second | derived L1 | 2025-08-14 | 2026-05-20 | 45 | MATERIALIZED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| ES tick+BBO (OLD) | ES | tick | Last+Bid+Ask | 2025-08-14 | 2026-05-20 | 39 | MATERIALIZED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| Market internals $TICK | $TICK | 1-minute | OHLC index (NO volume) | **2012-12-31** (extended, CAPPROBE02) | 2026-07-31 15:59:00 | **3,402 payload** (was 1147; 99.25 % of 2013-21 NYSE cal) | MATERIALIZED | $0 | spans eras — 2013-21 slice PRE-FROZEN/UNSPENT, era-stratified use only (ERABREAK01 forbids pooling) | pre-2026-08-01, hard-dropped at build |
| Market internals $TRIN | $TRIN | 1-minute | OHLC index (NO volume) | **2013-01-02** (extended, CAPPROBE02) | 2026-07-31 15:59:00 | **3,400 payload** (99.43 % of 2013-21 NYSE cal) | MATERIALIZED | $0 | spans eras — same PRE-FROZEN rule as $TICK | pre-2026-08-01, hard-dropped at build |
| Market internals $VIX | $VIX | 1-minute | OHLC index (NO volume) | 2022-01-03 09:32:00 | 2026-07-31 15:59:00 | 1147 | MATERIALIZED | $0 | REGIME-LOCAL (2022+) | pre-2026-08-01, hard-dropped at build |
| NQ tick store (UNEXTRACTED remainder) | NQ | tick | Last (+Bid/Ask where present) | 2025-08-12 | 2026-05-08 | 141 | ON DISK, NOT EXTRACTED | $0 | MICROSTRUCTURE-CURRENT | pre-2026-08-01 |
| ES 1-minute store | ES | 1-minute | Last OHLCV | 2021-12-30 | 2026-07-31 | 1486 | **EXTRACTED** (`runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet`) — this row previously said NOT EXTRACTED, stale | $0 | unclassified | pre-2026-08-01 |
| CL 1-minute store | CL | 1-minute | Last OHLCV | 2022-01-02 | 2026-07-31 | 1481 | ON DISK, NOT EXTRACTED | $0 | unclassified | pre-2026-08-01 |
| MNQ 1-minute store | MNQ | 1-minute | Last OHLCV | 2021-12-30 | 2026-07-31 | 1479 | ON DISK, NOT EXTRACTED | $0 | unclassified | pre-2026-08-01 |
| RTY 1-minute store | RTY | 1-minute | Last OHLCV | 2021-12-30 | 2026-07-31 | 1472 | **EXTRACTED** (`runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet`) — this row previously said NOT EXTRACTED, stale | $0 | unclassified | pre-2026-08-01 |
| YM 1-minute store | YM | 1-minute | Last OHLCV | 2021-12-30 | 2026-07-31 | 1458 | **EXTRACTED** (`runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet`) — this row previously said NOT EXTRACTED, stale | $0 | unclassified | pre-2026-08-01 |
| ZB 1-minute store | ZB | 1-minute | Last OHLCV | 2023-01-02 | 2026-07-31 | 1161 | ON DISK, NOT EXTRACTED | $0 | unclassified | pre-2026-08-01 |
| 6J 1-minute store | 6J | 1-minute | Last OHLCV | 2025-12-30 | 2026-07-31 | 185 | ON DISK, NOT EXTRACTED | $0 | unclassified | pre-2026-08-01 |
| ZN 1-minute store | ZN | 1-minute | Last OHLCV | 2025-12-30 | 2026-07-31 | 185 | ON DISK, NOT EXTRACTED | $0 | unclassified | pre-2026-08-01 |
| MGC 1-minute store | MGC | 1-minute | Last OHLCV | 2025-12-30 | 2026-07-31 | 184 | ON DISK, NOT EXTRACTED | $0 | unclassified | pre-2026-08-01 |
| Multi-market DAILY via connection | 24 roots: 6A,6B,6C,6E,6J,6S,CL,ES,GC,HG,HO,NG,NQ,RB,SI,YM,ZB,ZC,ZF,ZL,ZM,ZN,ZT,ZW | daily | Last OHLCV | 2016 probe (>=15y reachable: ES 12-11, ZN 12-16 served) | 2026-07-31 | ~250/yr/root, contract-level | INVENTORIED ONLY | $0 | STRUCTURAL (candidate) | n/a |
| SEALED forward pool | all | all | all | 2026-08-01 | ongoing | ~19 as of 2026-08-27 | **DO NOT READ** | $0 | GLOBAL VIRGIN | **VIRGIN** |
| BURNED window | all | all | all | 2026-05-31 | 2026-07-31 |  |  |  | BURNED | **BURNED** |

## Per-asset detail — completeness, truncation, and what each may be used for

### NQ 1-minute bars (nq1m_base)

- **location** `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: N/A - Last only
- **known truncation**: none
- **missing intervals**: 2014-01-27..31 whole week + scattered weekdays (2009-03-27, 2009-06-19, 2013-07-12)
- **full vs partial**: see MANIFEST_NOTES: 46 days have 261-379 RTH bars
- ✅ **suitable for**: P1/PCT, XM, any bar-level intraday study
- ❌ **unsuitable for**: anything needing signed flow, quotes, or sub-minute timing

### NQ 1-minute bars (nq1m_ext)

- **location** `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: N/A - Last only
- **known truncation**: none
- **missing intervals**: 2014-01-27..31 whole week + scattered weekdays (2009-03-27, 2009-06-19, 2013-07-12)
- **full vs partial**: see MANIFEST_NOTES: 46 days have 261-379 RTH bars
- ✅ **suitable for**: P1/PCT, XM, any bar-level intraday study
- ❌ **unsuitable for**: anything needing signed flow, quotes, or sub-minute timing

### NQ tick+BBO (OLD scalping_lab v1)

- **location** `research/scalping_lab/substrate/raw/NQ` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: 3 sessions carry no quotes at all
- **known truncation**: **15 files sit at exactly 12,000,000 rows = v1 cap = TRUNCATED mid-session**
- **missing intervals**: non-contiguous sample of the store
- **full vs partial**: 42 quote-FULL of 48
- ✅ **suitable for**: fill-cost/spread audit (W82/W89 used 45)
- ❌ **unsuitable for**: any feature needing the session tail on a truncated file

### NQ tick+BBO (NEW v2)

- **location** `research/data_microstructure_v2/ (parquet gitignored)` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: min bid/ask coverage 0.9993/0.9993
- **known truncation**: none - 25M cap, largest session 22.8M rows
- **missing intervals**: s20260525 quarantined (Memorial Day, 19.0h span)
- **full vs partial**: 58 quote-FULL of 58
- ✅ **suitable for**: signed flow, microprice, quote imbalance, spread state, absorption
- ❌ **unsuitable for**: any structural/multi-era claim

### NQ tick+BBO (UNION, materialized)

- **location** `two directories, deliberately not merged` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: lane-dependent - DO NOT MERGE the two lanes
- **known truncation**: 15 old files truncated; mask required for tail-dependent features
- **missing intervals**: store ceiling: 99 quote-FULL, 243 Last-usable
- **full vs partial**: **98 quote-FULL**, 102 Last-usable
- ✅ **suitable for**: standalone microstructure alpha (regime-local)
- ❌ **unsuitable for**: P1 full-horizon action-value routing - CLOSED-BY-POWER, 998 sessions needed, 713 exist

### NQ grid1s (1-sec L1 grid, has sflow)

- **location** `research/scalping_lab/substrate/grid1s/NQ` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: inherits v1
- **known truncation**: inherits v1 truncation; grid1s `last` has a recorded LOOKAHEAD defect (AUCTION04 01_build_clean_substrate.py:17-21)
- **missing intervals**: inherits v1 gaps
- **full vs partial**: derived from OLD v1 raw only
- ✅ **suitable for**: spread/cost audit
- ❌ **unsuitable for**: anything causal using grid1s `last` unfixed

### NQ sechilo (per-sec mid hi/lo)

- **location** `research/scalping_lab/substrate/sechilo/NQ` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: inherits v1
- **known truncation**: inherits v1 truncation; grid1s `last` has a recorded LOOKAHEAD defect (AUCTION04 01_build_clean_substrate.py:17-21)
- **missing intervals**: inherits v1 gaps
- **full vs partial**: derived from OLD v1 raw only
- ✅ **suitable for**: spread/cost audit
- ❌ **unsuitable for**: anything causal using grid1s `last` unfixed

### ES tick+BBO (OLD)

- **location** `research/scalping_lab/substrate/raw/ES` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: n/a
- **known truncation**: unaudited
- **missing intervals**: none recorded
- **full vs partial**: manifest marks ARCHIVE_ONLY
- ✅ **suitable for**: cross-market microstructure (directive s32)
- ❌ **unsuitable for**: 1-minute cross-market conclusions (W122 tested a different family)

### Market internals $TICK

- **location** `research/data_internals/ (parquet gitignored)` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: no overnight session at all
- **full vs partial**: RTH only, 09:31-15:59
- ✅ **suitable for**: RTH breadth/vol state; covers 764 of 2,139 P1 decisions (35.7 %)
- ❌ **unsuitable for**: the 64 % of P1 decisions that are overnight - permanent ceiling

### Market internals $TRIN

- **location** `research/data_internals/ (parquet gitignored)` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: no overnight session at all
- **full vs partial**: RTH only, 09:31-15:59
- ✅ **suitable for**: RTH breadth/vol state; covers 764 of 2,139 P1 decisions (35.7 %)
- ❌ **unsuitable for**: the 64 % of P1 decisions that are overnight - permanent ceiling

### Market internals $VIX

- **location** `research/data_internals/ (parquet gitignored)` · **status** MATERIALIZED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: no overnight session at all
- **full vs partial**: RTH only, 09:31-15:59
- ✅ **suitable for**: RTH breadth/vol state; covers 764 of 2,139 P1 decisions (35.7 %)
- ❌ **unsuitable for**: the 64 % of P1 decisions that are overnight - permanent ceiling

### NQ tick store (UNEXTRACTED remainder)

- **location** `~/Documents/NinjaTrader 8/db/tick` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: mostly Last-only
- **known truncation**: none - would use v4 exporter
- **missing intervals**: none recorded
- **full vs partial**: 1 quote-FULL remain
- ✅ **suitable for**: signed-flow lane expansion
- ❌ **unsuitable for**: quote features

### ES 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### CL 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### MNQ 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### RTY 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### YM 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### ZB 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### 6J 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### ZN 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### MGC 1-minute store

- **location** `~/Documents/NinjaTrader 8/db/minute` · **status** ON DISK, NOT EXTRACTED · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: unaudited
- **full vs partial**: unaudited
- ✅ **suitable for**: cross-market intraday
- ❌ **unsuitable for**: —

### Multi-market DAILY via connection

- **location** `provider on demand; NOT materialized` · **status** INVENTORIED ONLY · **cost** $0
- **quote completeness**: N/A
- **known truncation**: none
- **missing intervals**: RTY pre-2017 (CME listing); ZS September never resolves
- **full vs partial**: 6 sectors: equity index, rates, FX, energy, metals, ags
- ✅ **suitable for**: multi-market TSMOM/carry - slow signals NEED long history
- ❌ **unsuitable for**: anything intraday

### SEALED forward pool

- **location** `not read` · **status** **DO NOT READ** · **cost** $0
- **quote completeness**: n/a
- **known truncation**: none
- **missing intervals**: none recorded
- **full vs partial**: n/a
- ✅ **suitable for**: WEEKLY_EDGE_FORWARD_PROTOCOL checkpoints only
- ❌ **unsuitable for**: everything else

### BURNED window

- **location** `` · **status**  · **cost** 
- **quote completeness**: n/a
- **known truncation**: none
- **missing intervals**: none recorded
- **full vs partial**: n/a
- ✅ **suitable for**: reporting only
- ❌ **unsuitable for**: any fresh-evidence claim
