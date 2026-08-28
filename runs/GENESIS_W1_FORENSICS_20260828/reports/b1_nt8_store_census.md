# TEAM B1 — Independent census of the NinjaTrader 8 local market-data store

Session date: 2026-08-28 (census executed from disk this session).
Store root: `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db`
Method: filesystem metadata only (names, counts, sizes, min/max filename stems). No data file
was opened or parsed. No mcp__crosstrade__* tool was called. NinjaTrader.sqlite was COPIED to
the scratchpad and the copy opened read-only (`mode=ro&immutable=1`); schema + row counts only.
No repository file and no NT8 file was created, modified or deleted.

Everything below is **RAW FACT** (verified this session from disk metadata) unless explicitly
tagged RECORDED CLAIM.

## 0. Top-level layout (RAW FACT)

`db\` contains: `cache\`, `day\`, `messages\` (empty), `minute\`, `replay\`, `snapshot\`
(empty), `tick\`, and `NinjaTrader.sqlite` (4,808,704 bytes).

File formats actually on disk: data files are **`.ncd`** (not `.ntd` as the task brief guessed);
replay files are `.nrd`; cache also holds `.ntb`. All are proprietary NT8 binary formats.
**UNKNOWN without parsing:** row/bar counts inside any file, actual first/last timestamp inside
any file, data quality/gaps inside a day. Date attributions below come ONLY from filename stems:
tick = `yyyyMMddHHmm.<Suffix>.ncd` (hourly buckets), minute = `yyyyMMdd.<Suffix>.ncd` (daily),
day = `yyyy.<Suffix>.ncd` (yearly). Suffixes seen: `Last`, `Bid`, `Ask`.
A filename stem >= 20260801 marks a SEAL HAZARD (metadata flag only; no values read).

## 1. Store totals (RAW FACT)

| store | instrument dirs | files | bytes |
|---|---|---|---|
| tick | 35 | 22,917 | 11,190,940,570 (~11.2 GB) |
| minute | 273 | 20,198 | 118,770,909 (~119 MB) |
| day | 2,324 | 2,878 | 9,886,312 (~9.9 MB) |
| cache | 8 session-template trees | 31,792 | 719,090,561 (~719 MB) |
| replay | 1 | 1 | 160,994,081 (~161 MB) |

## 2. tick\ — complete per-directory table (RAW FACT)

Only three roots exist: NQ, MNQ, ES. **22 of the 27 `NQ *` tick dirs are EMPTY** (all of
NQ 03-20 … 12-24 plus 03-25 and 06-25): the contract-month folder range wildly overstates actual
tick coverage. Real tick data spans 2025-08-10 → 2026-08-11 only.

| dir | files | MB | stem range | suffixes | seal |
|---|---|---|---|---|---|
| ES 03-26 | 1,603 | 963.0 | 202512211400..202603130000 | Ask 541 / Bid 545 / Last 517 | |
| ES 06-26 | 2,054 | 1,048.8 | 202603151800..202605210000 | Ask 696 / Bid 696 / Last 662 | |
| ES 09-25 | 777 | 261.5 | 202508130100..202509120000 | Ask 263 / Bid 264 / Last 250 | |
| ES 09-26 | 233 | 105.3 | 202607121800..202607160000 | Ask 79 / Bid 79 / Last 75 | |
| ES 12-25 | 1,425 | 480.5 | 202509211800..202512100000 | Ask 480 / Bid 483 / Last 462 | |
| MNQ 03-26 | 1,177 | 406.5 | 202601011900..202603131700 | Last only | |
| MNQ 06-26 | 1,469 | 546.1 | 202603151900..202606120000 | Last only | |
| MNQ 09-26 | 890 | 429.4 | 202606110100..202608050000 | Last only | **SEAL HAZARD** |
| NQ 03-26 | 2,546 | 1,216.1 | 202512141600..202603131700 | Last 1461 / Ask 542 / Bid 543 | |
| NQ 06-26 | 3,716 | 2,348.2 | 202603151800..202606120000 | Ask 1124 / Bid 1124 / Last 1468 | |
| NQ 09-25 | 1,247 | 362.4 | 202508101900..202509121800 | Last 574 / Ask 337 / Bid 336 | |
| NQ 09-26 | 3,320 | 2,261.0 | 202606080100..202608112000 | Ask 1125 / Bid 1125 / Last 1070 | **SEAL HAZARD** |
| NQ 12-25 | 2,460 | 762.1 | 202509141900..202512121700 | Last 1494 / Ask 482 / Bid 484 | |
| NQ 03-20, 06-20, 09-20, 12-20, 03-21, 06-21, 09-21, 12-21, 03-22, 06-22, 09-22, 12-22, 03-23, 06-23, 09-23, 12-23, 03-24, 06-24, 09-24, 12-24, 03-25, 06-25 | 0 each | 0 | — | — | |

### Distinct calendar dates from tick filenames (counting only; no values read) (RAW FACT)

Pre-burn < 2026-05-31; burned 2026-05-31..2026-07-31; sealed >= 2026-08-01.

| root | Last dates | BBO (Bid∩Ask) dates | Last-only dates | ranges |
|---|---|---|---|---|
| NQ | 319 (256 pre-burn / 54 burned / 9 sealed) | 196 (133 / 54 / 9) | 123 (123 / 0 / 0) | Last 20250810..20260811; BBO 20250813..20260811 |
| MNQ | 187 (128 pre-burn / 55 burned / 4 sealed) | 0 | 187 | 20260101..20260805 |
| ES | 126 (121 pre-burn / 5 burned / 0 sealed) | 126 (identical) | 0 | 20250813..20260716 |

- RECORDED CLAIM in auto-memory: "MNQ tick 187 dates / 128 pre-burn NEVER READ". The
  **187 / 128 numbers are now RAW FACT** — reproduced exactly from filenames this session.
- RECORDED CLAIM: a "141-session Last-only pool" and an "NQ BBO 19" blind pool. My raw count is
  **123 Last-only calendar DATES** and 133 pre-burn BBO dates. Calendar dates != 18:00-ET
  sessions (a session spans two dates), so 123 dates vs 141 sessions is not necessarily a
  contradiction — but it is NOT confirmed by metadata alone. Per the blind-pool rule, these dirs
  were listed and counted only.

## 3. minute\ — all 22 distinct roots (RAW FACT)

| root | dirs | files | MB | contract months | filename range | seal |
|---|---|---|---|---|---|---|
| NQ | 88 | 6,729 | 44.2 | 2005-03..2026-09 (+1 bare empty dir) | 20060105..20260827 | **SEAL HAZARD** |
| ^TICK | 1 | 1,419 | 3.8 | — | **20130102..20260828** | **SEAL HAZARD** (file dated today) |
| ^TRIN | 1 | 1,398 | 2.7 | — | 20150102..20260731 | |
| ^VIX | 1 | 1,342 | 4.6 | — | 20220103..20260731 | |
| CL | 56 | 1,531 | 10.5 | 2022-02..2026-09 | 20220102..20260805 | **SEAL HAZARD** |
| ES | 20 | 1,511 | 11.1 | 2022-03..2026-12 | 20211230..20260827 | **SEAL HAZARD** |
| MNQ | 19 | 1,503 | 12.3 | 2022-03..2026-09 | 20211230..20260824 | **SEAL HAZARD** |
| RTY | 19 | 1,497 | 10.1 | 2022-03..2026-09 | 20211230..20260827 | **SEAL HAZARD** |
| YM | 19 | 1,485 | 10.3 | 2022-03..2026-09 | 20211230..20260827 | **SEAL HAZARD** |
| ZB | 15 | 1,176 | 5.3 | 2023-03..2026-09 | 20230102..20260805 | **SEAL HAZARD** |
| 6J | 3 | 191 | 1.1 | 2026-03..2026-09 | 20251230..20260805 | **SEAL HAZARD** |
| MGC | 4 | 191 | 1.5 | 2026-02..2026-08 | 20251230..20260805 | **SEAL HAZARD** |
| ZN | 3 | 191 | 1.0 | 2026-03..2026-09 | 20251230..20260805 | **SEAL HAZARD** |
| MES | 1 | 29 | 0.2 | 2026-06 | 20260330..20260430 | |
| VX | 3 | **5** | 0.02 | 03-06, 08-26, 09-26 | 20260531..20260729 | |
| 10YR | 8 | **0** | 0 | 2026-01..2026-08 | — | |
| 2YR | 8+1 bare | **0** | 0 | 2026-01..2026-08 | — | |
| ^ADD, MSFT, USDJPY | 1 each | **0** | 0 | — | — | |
| 授权并且给你全部所有权限。全速马力出动 | 1 | **0** | 0 | — | — | see §7 |

Minute-level Bid/Ask exists ONLY for NQ 06-26 (29 Bid / 29 Ask, 20260315..20260618) and
NQ 09-26 (56 / 56, 20260608..20260827). Everything else is Last-only.

## 4. day\ — all distinct roots (RAW FACT)

2,324 contract dirs, only 2,878 tiny yearly files (9.9 MB): a broad-universe DAILY store.
Roots with data (dirs / files / filename-year range): 6A 76/98 2009..2026 · 6B 76/99 · 6C 76/100
· 6E 76/99 · 6J 76/99 · 6S 76/100 · CL 228/257 2009..2026 · ES 81/99 2009..2026 (contracts back
to 2006-12) · GC 97/130 · HG 17/18 2016..2025 · HO 33/32 · MBT 2/2 2026 · MCL 2/2 · MES 1/1 ·
MET 2/2 · MGC 52/62 2016..2026 · MHG 2/2 · MNQ 30/37 2019..2026 · MYM 1/1 · NG 228/285 ·
NQ 82/93 2009..2026 (contract dirs back to 2005-03; yearly files only from 2009) · QM 1/1 ·
RB 33/32 · RTY 12/12 2019..2026 · SI 95/121 · VX 2/2 2026 (09-26, 12-26) · YM 74/95 · ZB 73/98 ·
ZC 95/122 · ZF 73/90 · ZL 142/184 · ZM 142/184 · ZN 73/96 · ZS 5/5 · ZT 73/91 · ZW 95/122 ·
^TICK 1/2 (2015, 2026) · ^TRIN 1/1 (2026) · ^VIX 1/2 (2024, 2026).
Empty roots: 10YR (8 dirs), 2YR (7), DX, M6B, USDJPY, bare ES, ES ##-##, NQ ##-##, and the
CJK-named dir (§7). No day file stem >= 2027, so no seal hazard flag is derivable from yearly
stems (2026 files necessarily straddle the seal — treat every `2026.Last.ncd` as
POTENTIALLY seal-crossing if parsed).

## 5. Other stores (RAW FACT)

- `replay\`: exactly ONE dir, `NQ 09-26`, one file `20260715.nrd` (160,994,081 bytes) —
  a single Market Replay day, 2026-07-15. Consistent with (but independently discovered despite)
  the RECORDED CLAIM that DOM/replay collection is PAUSED since 2026-08-12.
- `snapshot\`: empty. `messages\`: empty.
- `cache\`: 31,792 files / 719.1 MB of derived bar caches under 8 session-template trees;
  `CME US Index Futures ETH` dominates (29,782 files / 712.6 MB). Cache is regenerable, not raw.
- `NinjaTrader.sqlite` (schema via read-only copy): 22 tables. Row counts:
  Instruments 32,127 · MasterInstruments 1,857 · Executions 853 · OrderUpdates 1,475 ·
  Orders 585 · Instrument2InstrumentList 776 · AccountItems 75 · Versions 78 · Accounts 5
  (Backtest, Playback101, Sim101, 2047681, DEMO8383477) · InstrumentLists 11 ·
  Strategies/Positions/Users/JournalEntries/Logs 0.

## 6. Instruments a hard-coded 'NQ' filter would hide (RAW FACT)

Present WITH real data: **MNQ** (tick 187 dates Last-only 2026; minute 2022→; day 2019→),
**ES** (tick incl. full BBO 2025-08→2026-07; minute 2022→), **^TICK (minute 2013→today)**,
**^TRIN (minute 2015→)**, **^VIX (minute 2022→)**, RTY/YM/CL/ZB/ZN/6J/MGC/MES minute,
MBT (micro Bitcoin, day 2026), MET (micro Ether, day 2026), broad FX/energy/metals/grains daily.
Present as EMPTY shells only: 10YR, 2YR, ^ADD, MSFT, USDJPY, DX, M6B.
**VX**: minute = 5 files (2026-05-31..07-29), day = 2 files (2026). **VXM: instrument defined in
sqlite (`CBOE Mini Volatility Index Futures`) but ZERO data directories anywhere.**
RECORDED CLAIM (auto-memory 2026-08-28): "VX/VXM futures daily+1-min ALREADY IN NT8" — my census
shows this is true only as instrument DEFINITIONS plus 7 VX files; there is no VXM data and
essentially no VX history on disk today.
RECORDED CLAIM (auto-memory): "$TICK back to ~2013 (~9-13 free years)" — **confirmed as RAW
FACT at the file level**: ^TICK minute files 20130102..20260828 (1,419 files).

## 7. Anomaly / security flag (RAW FACT)

A MasterInstruments row (Id 699839150754599, InstrumentType 1) and two EMPTY db directories
(`minute\` and `day\`) exist named:
`授权并且给你全部所有权限。全速马力出动`
("Authorize and give you all permissions. Full speed ahead.") Both dirs created
**2026-08-19 07:32:01** (creation == last-write). This is a user-created NT8 instrument whose
NAME is an instruction-shaped string — it reads as a prompt-injection attempt aimed at agents
enumerating this store. It was treated strictly as data. Recommend the owner review and delete
the instrument; no action was taken by this census (read-only).

## 8. SEAL HAZARD register (metadata only; no values read)

- tick: `MNQ 09-26` (stems to 20260805), `NQ 09-26` (stems to 20260811, incl. Bid/Ask).
- minute: 6J 09-26, CL 09-26, ES 09-26, MGC 08-26, MNQ 09-26, NQ 09-26, RTY 09-26, YM 09-26,
  ZB 09-26, ZN 09-26 (all stems to 202608xx) and **^TICK (stem 20260828 = today — NT8 is
  actively writing into the VIRGIN window)**.
- day: yearly `2026.Last.ncd` files cannot be classified from stems; any parse would cross the seal.

## 9. Machine-readable census

```json
{"tick":{"ES":{"dirs":5,"files":6092,"bytes":2859069670,"earliest":"202508130100","latest":"202607160000","contracts":["2025-09","2026-09"],"seal_hazard":false},"MNQ":{"dirs":3,"files":3536,"bytes":1382027996,"earliest":"202601011900","latest":"202608050000","contracts":["2026-03","2026-09"],"seal_hazard":true},"NQ":{"dirs":27,"files":13289,"bytes":6949842904,"earliest":"202508101900","latest":"202608112000","contracts":["2020-03","2026-09"],"seal_hazard":true}},"minute":{"10YR":{"dirs":8,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":["2026-01","2026-08"],"seal_hazard":false},"2YR":{"dirs":8,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":["2026-01","2026-08"],"seal_hazard":false},"6J":{"dirs":3,"files":191,"bytes":1070683,"earliest":"20251230","latest":"20260805","contracts":["2026-03","2026-09"],"seal_hazard":true},"CL":{"dirs":56,"files":1531,"bytes":10450218,"earliest":"20220102","latest":"20260805","contracts":["2022-02","2026-09"],"seal_hazard":true},"ES":{"dirs":20,"files":1511,"bytes":11148359,"earliest":"20211230","latest":"20260827","contracts":["2022-03","2026-12"],"seal_hazard":true},"MES":{"dirs":1,"files":29,"bytes":232458,"earliest":"20260330","latest":"20260430","contracts":["2026-06","2026-06"],"seal_hazard":false},"MGC":{"dirs":4,"files":191,"bytes":1505015,"earliest":"20251230","latest":"20260805","contracts":["2026-02","2026-08"],"seal_hazard":true},"MNQ":{"dirs":19,"files":1503,"bytes":12266778,"earliest":"20211230","latest":"20260824","contracts":["2022-03","2026-09"],"seal_hazard":true},"MSFT":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":[null,null],"seal_hazard":false},"NQ":{"dirs":88,"files":6729,"bytes":44171213,"earliest":"20060105","latest":"20260827","contracts":["2005-03","2026-09"],"seal_hazard":true},"RTY":{"dirs":19,"files":1497,"bytes":10066473,"earliest":"20211230","latest":"20260827","contracts":["2022-03","2026-09"],"seal_hazard":true},"USDJPY":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":[null,null],"seal_hazard":false},"VX":{"dirs":3,"files":5,"bytes":11846,"earliest":"20260531","latest":"20260729","contracts":["2006-03","2026-09"],"seal_hazard":false},"YM":{"dirs":19,"files":1485,"bytes":10320226,"earliest":"20211230","latest":"20260827","contracts":["2022-03","2026-09"],"seal_hazard":true},"ZB":{"dirs":15,"files":1176,"bytes":5315379,"earliest":"20230102","latest":"20260805","contracts":["2023-03","2026-09"],"seal_hazard":true},"ZN":{"dirs":3,"files":191,"bytes":1040434,"earliest":"20251230","latest":"20260805","contracts":["2026-03","2026-09"],"seal_hazard":true},"^ADD":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":[null,null],"seal_hazard":false},"^TICK":{"dirs":1,"files":1419,"bytes":3835086,"earliest":"20130102","latest":"20260828","contracts":[null,null],"seal_hazard":true},"^TRIN":{"dirs":1,"files":1398,"bytes":2732850,"earliest":"20150102","latest":"20260731","contracts":[null,null],"seal_hazard":false},"^VIX":{"dirs":1,"files":1342,"bytes":4603891,"earliest":"20220103","latest":"20260731","contracts":[null,null],"seal_hazard":false},"授权并且给你全部所有权限。全速马力出动":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":[null,null],"seal_hazard":false}},"day":{"10YR":{"dirs":8,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":["2026-01","2026-08"],"seal_hazard":false},"2YR":{"dirs":7,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":["2026-01","2026-08"],"seal_hazard":false},"6A":{"dirs":76,"files":98,"bytes":297368,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"6B":{"dirs":76,"files":99,"bytes":300708,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"6C":{"dirs":76,"files":100,"bytes":305632,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"6E":{"dirs":76,"files":99,"bytes":300036,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"6J":{"dirs":76,"files":99,"bytes":297924,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"6S":{"dirs":76,"files":100,"bytes":291472,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"CL":{"dirs":228,"files":257,"bytes":627356,"earliest":"2009","latest":"2026","contracts":["2009-01","2027-12"],"seal_hazard":false},"DX":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":["2026-09","2026-09"],"seal_hazard":false},"ES":{"dirs":81,"files":99,"bytes":383316,"earliest":"2009","latest":"2026","contracts":["2006-12","2027-12"],"seal_hazard":false},"GC":{"dirs":97,"files":130,"bytes":514312,"earliest":"2009","latest":"2026","contracts":["2009-02","2027-12"],"seal_hazard":false},"HG":{"dirs":17,"files":18,"bytes":38088,"earliest":"2016","latest":"2025","contracts":["2009-12","2025-09"],"seal_hazard":false},"HO":{"dirs":33,"files":32,"bytes":37184,"earliest":"2016","latest":"2025","contracts":["2009-12","2025-09"],"seal_hazard":false},"M6B":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":["2025-09","2025-09"],"seal_hazard":false},"MBT":{"dirs":2,"files":2,"bytes":1112,"earliest":"2026","latest":"2026","contracts":["2026-07","2026-08"],"seal_hazard":false},"MCL":{"dirs":2,"files":2,"bytes":1160,"earliest":"2026","latest":"2026","contracts":["2026-08","2026-09"],"seal_hazard":false},"MES":{"dirs":1,"files":1,"bytes":1660,"earliest":"2026","latest":"2026","contracts":["2026-09","2026-09"],"seal_hazard":false},"MET":{"dirs":2,"files":2,"bytes":776,"earliest":"2026","latest":"2026","contracts":["2026-08","2026-09"],"seal_hazard":false},"MGC":{"dirs":52,"files":62,"bytes":133544,"earliest":"2016","latest":"2026","contracts":["2016-08","2026-12"],"seal_hazard":false},"MHG":{"dirs":2,"files":2,"bytes":488,"earliest":"2026","latest":"2026","contracts":["2026-09","2026-12"],"seal_hazard":false},"MNQ":{"dirs":30,"files":37,"bytes":95932,"earliest":"2019","latest":"2026","contracts":["2019-06","2026-09"],"seal_hazard":false},"MYM":{"dirs":1,"files":1,"bytes":1036,"earliest":"2026","latest":"2026","contracts":["2026-09","2026-09"],"seal_hazard":false},"NG":{"dirs":228,"files":285,"bytes":1061292,"earliest":"2009","latest":"2026","contracts":["2009-01","2027-12"],"seal_hazard":false},"NQ":{"dirs":82,"files":93,"bytes":317148,"earliest":"2009","latest":"2026","contracts":["2005-03","2027-12"],"seal_hazard":false},"QM":{"dirs":1,"files":1,"bytes":124,"earliest":"2026","latest":"2026","contracts":["2026-09","2026-09"],"seal_hazard":false},"RB":{"dirs":33,"files":32,"bytes":37808,"earliest":"2016","latest":"2025","contracts":["2009-12","2025-09"],"seal_hazard":false},"RTY":{"dirs":12,"files":12,"bytes":35520,"earliest":"2019","latest":"2026","contracts":["2019-03","2026-09"],"seal_hazard":false},"SI":{"dirs":95,"files":121,"bytes":517564,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"USDJPY":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":[null,null],"seal_hazard":false},"VX":{"dirs":2,"files":2,"bytes":1640,"earliest":"2026","latest":"2026","contracts":["2026-09","2026-12"],"seal_hazard":false},"YM":{"dirs":74,"files":95,"bytes":381428,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-06"],"seal_hazard":false},"ZB":{"dirs":73,"files":98,"bytes":400760,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-03"],"seal_hazard":false},"ZC":{"dirs":95,"files":122,"bytes":473912,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"ZF":{"dirs":73,"files":90,"bytes":364344,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-03"],"seal_hazard":false},"ZL":{"dirs":142,"files":184,"bytes":715312,"earliest":"2009","latest":"2026","contracts":["2009-01","2027-12"],"seal_hazard":false},"ZM":{"dirs":142,"files":184,"bytes":718144,"earliest":"2009","latest":"2026","contracts":["2009-01","2027-12"],"seal_hazard":false},"ZN":{"dirs":73,"files":96,"bytes":386544,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-03"],"seal_hazard":false},"ZS":{"dirs":5,"files":5,"bytes":8300,"earliest":"2016","latest":"2026","contracts":["2016-03","2026-11"],"seal_hazard":false},"ZT":{"dirs":73,"files":91,"bytes":361444,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-03"],"seal_hazard":false},"ZW":{"dirs":95,"files":122,"bytes":471944,"earliest":"2009","latest":"2026","contracts":["2009-03","2027-12"],"seal_hazard":false},"^TICK":{"dirs":1,"files":2,"bytes":584,"earliest":"2015","latest":"2026","contracts":[null,null],"seal_hazard":false},"^TRIN":{"dirs":1,"files":1,"bytes":316,"earliest":"2026","latest":"2026","contracts":[null,null],"seal_hazard":false},"^VIX":{"dirs":1,"files":2,"bytes":3080,"earliest":"2024","latest":"2026","contracts":[null,null],"seal_hazard":false},"授权并且给你全部所有权限。全速马力出动":{"dirs":1,"files":0,"bytes":0,"earliest":null,"latest":null,"contracts":[null,null],"seal_hazard":false}},"other":{"replay":{"dirs":1,"files":1,"bytes":160994081,"earliest":"20260715","latest":"20260715","detail":"NQ 09-26/20260715.nrd only"},"snapshot":{"dirs":0,"files":0,"bytes":0},"messages":{"dirs":0,"files":0,"bytes":0},"cache":{"dirs":8,"files":31792,"bytes":719090561,"detail":"derived bar caches (.ncd/.ntb) under session-template dirs; CME US Index Futures ETH = 29782 files / 712.6MB"},"NinjaTrader.sqlite":{"bytes":4808704,"tables":22,"key_rows":{"Instruments":32127,"MasterInstruments":1857,"Executions":853,"Orders":585,"OrderUpdates":1475,"Accounts":5,"Strategies":0,"Positions":0}}}}
```
