# TEAM G1 — Adversarial verification of Program C "free tier is not exhausted" findings

Date of work: 2026-08-28 (evening; NT8 db probe residue from the census run is timestamped 17:34–17:39 same day).
Method: read-only inspection of the repo and `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db` (file names, counts, sizes, mtimes only — no data values read, no sealed values touched, no crosstrade tool called), plus public-web metadata checks (HTML pages and HTTP HEAD only, no data files downloaded).

Legend: **RAW FACT** = verified by me this session. **RECORDED CLAIM** = a repo document asserts it; I verified only the assertion's existence/provenance.

---

## CLAIM 1 — "VX/VXM futures daily + 1-min OHLCV, multiple contract months, already in NT8"

Claim text: `research/information_frontier/CURRENT_INFORMATION_MAP.md` §2 row F3; `runs/INFORMATION_FRONTIER_00_20260828/REPORT.md` §1 F3 ("NT8 already holds VX/VXM daily *and* 1-minute OHLCV for multiple contract months, at $0"); propagated verbatim to `research/router/RESEARCH_FRONTIER.md:103` and `:447`, and `research/information_frontier/ACQUISITION_DECISION_PACKET.md` A2.

**VERDICT: PARTIALLY VERIFIED, MATERIALLY OVERSTATED. The VXM half has zero disk evidence; the VX disk evidence is probe residue created BY the census run itself, is 2026-only, and one deep-history probe failed empty and went unrecorded.**

RAW FACTS:
- The only VX presence in the entire db tree: `day/VX 09-26` (1 file, `2026.Last.ncd`, 1,324 B), `day/VX 12-26` (1 file, `2026.Last.ncd`, 316 B), `minute/VX 08-26` (2 files: `20260531`, `20260601`), `minute/VX 09-26` (3 files: `20260727..29`), `minute/VX 03-06` (**0 files**).
- **Every one of these files/dirs is mtime 2026-08-28 17:39** — written during the census probe, not a pre-existing store. "Already in NT8" therefore means "the connection serves it on request", not "a store exists".
- **No `VXM` directory exists anywhere** under `db/day`, `db/minute`, or `db/tick`. The sole VXM evidence is an instrument *definition*: `MasterInstruments` in `db/NinjaTrader.sqlite` (read-only query) contains `('VX','CBOE Volatility Index Futures')` and `('VXM','CBOE Mini Volatility Index Futures')` (plus `('VIX','CBOE Volatility Index')`). Defined ≠ subscribed ≠ served.
- **`minute/VX 03-06` (a March-2006 contract) was created today with 0 files** — a deep-history 1-min probe that returned nothing. This negative result is **not recorded** in REPORT.md. Demonstrated VX 1-min coverage is exactly 5 session files, all mid-2026 (and 20260531/0601 are in the BURNED window). Demonstrated daily coverage: two 2026 year-files of ~40 and ~9 daily bars (by size).
- Practical consequence: the deep VX term-structure history the packet's A2 implies comes from the **free Cboe files (verified below), not from NT8**. The NT8 leg is demonstrated only for recent months.

## CLAIM 2 — "$TICK 1-min served back to ~2013; local store starts 2022"

Claim text: map §2 F2 ("Probe returns bars at 2013-01-02 and 2015-01-02 … ~9–13 extra years"); REPORT.md F2; RESEARCH_FRONTIER.md:103.

**VERDICT: RECORDED CLAIM (connection cannot be probed this wave) with strong RAW disk corroboration for exactly two dates; the "~2013 continuous backfill" extent remains undemonstrated.**

RAW FACTS:
- `minute/^TICK` holds 1,419 files: `20130102.Last.ncd` (3,398 B, mtime 2026-08-28 17:35), `20150102.Last.ncd` (3,537 B, 17:35), `20180709/20180710.Last.ncd` (mtime 2026-08-27 16:20 — the DATA_CAPABILITY_AUDIT day), then a continuous run `20220103 → 20260828` (post-2026-07-31 names counted only, never opened). `day/^TICK` holds `2015.Last.ncd` (268 B) and `2026.Last.ncd` (316 B), also today's residue. `minute/^TRIN` similarly holds `20150102` then 2022+.
- Non-trivial file sizes imply the 2013/2015 probes returned actual bars. The probe dates on disk match the doc's dates exactly.
- "Store starts 2022" is confirmed: `research/data_internals/MANIFEST.csv` — $TICK/$TRIN/$VIX parquet all `first=2022-01-03`, `last=2026-07-31 15:59` (RTH-only, 445,625 / 445,235 / 444,640 bars).
- **No probe log artifact exists**: `runs/INFORMATION_FRONTIER_00_20260828/` contains only `SPEC.md` and `REPORT.md` (no `out/`). Two single-day probes (2013-01-02, 2015-01-02) do not establish a continuous 2013→2021 backfill; nothing between 2015 and 2018 was probed. The "~9–13 years" figure is extrapolation.

## CLAIM 3 — "MNQ tick 187 dates / 128 pre-burn, hidden by hard-coded symbol=\"NQ\" at build_registry.py:197-206"

**VERDICT: CONFIRMED — counts exact; the hard-code is real (line 198; cited span off by ~2 lines); the actual path is `research/data/build_registry.py`, not `research/registry/`. Additional hiding filters found (below).**

RAW FACTS:
- `db/tick/` MNQ contract dirs: `MNQ 03-26` (1,177 hourly `.Last.ncd`, 20260101→20260313), `MNQ 06-26` (1,469, 20260315→20260612), `MNQ 09-26` (890, 20260611→20260805). **Unique dates = 187; dates < 20260531 = 128; 4 dates ≥ 20260801 (names only, sealed).** Dir mtimes 2026-08-05 — the data predates the census. Last-only (no Bid/Ask files), matching the candidates table caveat.
- `research/data/build_registry.py:198` — `add(asset="NQ tick store (UNEXTRACTED remainder)", symbol="NQ", ...)`; the add() call spans lines 198–208. Line 197 defines regex `NCD` which is **dead code — never referenced anywhere in the file**.
- Deeper mechanism than the doc states: the registry **never scans `db/tick` at all**. Its tick population comes from `runs/ORDERFLOW_EXPAND_20260827/out/bbo_hourly_truth.csv` (line 93; 310 rows; columns session,date,…,cls — **no symbol column, NQ-only by construction**). So MNQ tick and the local **ES tick dirs (`ES 03-26, 06-26, 09-25, 09-26, 12-25` — RAW, present)** are structurally invisible regardless of the `symbol=` label.
- Other hard-coded filters that hide data (all RAW):
  - **line 211**: `(kind=="minute") & (series=="Last") & (distinct_usable > 100)` — hides **MES minute (29 usable sessions, row present in retention_matrix.csv)** and NQ minute Bid/Ask (72 usable, 2026-05-10→07-31, rows present).
  - **lines 213-214**: `if root=="NQ": continue` (deliberate).
  - **Upstream whitelist**: `runs/DATA_CAPABILITY_AUDIT_20260827/out/retention_matrix.csv` contains **no rows at all** for VX, ^TICK/^TRIN/^VIX/^ADD, 2YR/10YR, USDJPY, or MSFT minute — the audit itself was root-whitelisted, so the registry could never see them.
  - **No section scans `db/day`** (the multi-decade daily contract store enters only as the connection-probe inventory, `runs/MULTIMARKET_INVENTORY_20260827/out/inventory.csv`).
- Registry output confirms the blindness: `research/data/DATA_ASSET_REGISTRY.md` has NO MNQ tick row (MNQ appears only as a 1-minute store row, line 62).

## CLAIM 4 — "nine unextracted 1-min futures stores: ES, CL, MNQ, RTY, YM, ZB, 6J, ZN, MGC"

**VERDICT: LIST AND MECHANISM CONFIRMED; "unextracted" is FALSE for 3 of the 9 (ES, RTY, YM) — they are already materialized as repo parquet and alpha-consumed, per Program C's own map. Genuinely new surfaces: CL, ZB, 6J, ZN, MGC (+ MNQ minute).**

RAW FACTS:
- The "nine" is exactly the `distinct_usable > 100` minute/Last rows of retention_matrix.csv minus NQ: ES 1486 (2021-12-30→2026-07-31), CL 1481, MNQ 1479, RTY 1472, YM 1458, ZB 1161, 6J 185, ZN 185, MGC 184. `DATA_ASSET_REGISTRY.md:60-68` lists precisely these nine as "ON DISK, NOT EXTRACTED / unclassified". Spot-check `minute/6J 03-26`: 64 session files 20251230→20260312 — real data.
- **Contradiction**: `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet`, `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet`, `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` exist (Glob, RAW). The map's own R1 row lists `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` and its R4 row records ES/YM/RTY 1-min as owned, 1,058 common sessions, "used in XM_CONFLICT_v2, W122". So ES/RTY/YM are extracted AND alpha-consumed — `evidence_class=unclassified` and "NOT EXTRACTED" are wrong for them, and counting them in "the largest untested intraday surface" double-counts consumed surfaces.
- **Cross-census conflict to adjudicate**: `runs/ASSET_CENSUS_20260828/REPORT.md` §1 says NT8 minute store "261 dirs, outcome-consumed 261, genuinely unread 0" while Program C calls the nine "unaudited/untested". Both are same-day documents. At minimum CL/ZB/6J/ZN/MGC were never read by any repo code I can find; the ASSET_CENSUS "0 unread" row and the Program C "never touched" framing cannot both be right as stated.
- A tenth store (MES, 29 sessions) is hidden by the >100 filter; seal hazard is real — several stores run to 2026-08-05/08-27 by retention-matrix `last` (names only).

## CLAIM 5 — free Cboe CDN files and CFTC COT

**VERDICT: CONFIRMED RAW (public metadata only; no data files downloaded).**

RAW FACTS (fetched 2026-08-28):
- Cboe VIX historical page: `VIX_History.csv` 1990→ at `cdn.cboe.com/api/global/us_indices/daily_prices/`, plus `vixarchive.xls` (1990-2003). HTTP HEAD 200: `VIX3M_History.csv` (217,387 B), also live.
- CFE historical page: "CFE Daily Volume and Open Interest by Product" — HEAD 200 `cfevoloi.csv` (702,508 B), coverage to 2004; VX price/volume detail "2013 to Current" plus 2004-2013 archive; VXM/IBHY/IBIG named on the page (partly via DataShop note).
- CFTC COT: free; published Fridays 3:30pm ET with the preceding Tuesday's data (3-day lag); Legacy back to 1986-01-15, Disaggregated + TFF back to 2006-06-13; **TFF explicitly covers VIX and stock-index financial futures** — i.e., COT serves both NQ crowding and VX positioning.

## HUNT — free-reachable observables Program C missed

1. **VXN — the Nasdaq-100 volatility index — free on the same Cboe CDN and never named anywhere in the repo.** RAW: HEAD 200 `VXN_History.csv` (217,686 B, updated today). Program C's entire vol family (VIX, VIX3M, VX) is SPX-based; **VXN is the NQ-native implied vol**, same $0, same publication mechanics. Highest-value miss found.
2. **VVIX (108,393 B), VIX9D (199,928 B), SKEW (202,740 B)** — RAW: all HEAD 200 on the same CDN; zero repo mentions (grep VVIX/OVX → no hits). Also OVX/GVZ/VXAPL/VXAZN/VXEEM per the Cboe page. Gives a free vol-of-vol and short-horizon term-structure axis on top of F3.
3. **^ADD (NYSE advance-decline)**: RAW — `minute/^ADD` exists, 0 files, dir mtime 2026-08-27 16:19: probed and returned nothing. Consistent with packet §D "defined-but-unsubscribed — a PRICE question". Not free today; correctly classified by Program C.
4. **MBT/MET (micro Bitcoin / micro Ether)**: RAW — defined in MasterInstruments with 2026 day-file residue (`day/MBT 07-26`, `day/MET 08-26` etc.). `ASSET_CENSUS_20260828` dismisses them as "micros of roots already in the universe" — **questionable: no BTC/ETH root appears in any multi-market universe doc I could find** (grep Bitcoin/BTC in research/multi_market, DATA_CENSUS → nothing). A free crypto-risk-appetite daily observable may be being mis-filed as a duplicate. Needs one-line adjudication.
5. **Kinetick free EOD**: RAW (public page) — "FREE End of Day Data" with NinjaTrader for "Futures, FX & Stock Markets"; per-instrument coverage not itemized on the page. Consistent with packet §D listing Kinetick tiers as UNKNOWN.
6. **2YR/10YR micro-yield futures**: RAW — defined; `minute/`, `day/` dirs all EMPTY (0 files). Already recorded (`research/weekly_edge/DATA_CENSUS_20260826.md:69`, ASSET_CENSUS §3), but note their dismissal there is about carry chronology; as *current-regime intraday rates observables* they remain an unprobed $0 connection question.
7. **Day-store shells**: RAW — much of the giant `db/day` contract listing is empty dirs (e.g., `ES 03-09`, `CL 01-09`, `NQ 03-05` = 0 files) with patchy year-files elsewhere (`ZW 12-09`, `6A 03-15`, `GC 06-20`). The impressive directory listing overstates on-disk daily holdings; the real daily surface is served-on-request (as the map's "INVENTORIED ONLY" row already says).
8. Curiosity, no action: an instrument dir literally named `授权并且给你全部所有权限。全速马力出动` ("authorize and give you all permissions, full speed ahead") exists in `db/day` and `db/minute` — someone typed a chat phrase into an NT8 instrument field. Harmless residue; a census that counts dirs will count it.
9. **Databento F1 figures (~2,300 MBO sessions from 2017-05-21)**: RECORDED CLAIM only — the public dataset/docs pages I could fetch do not state schema start dates; verification requires the metadata API (an account), or should be marked "verify at pilot time via metadata.get_cost/get_range".

## Governance notes
- Seal respected: all ≥2026-08-01 material touched as names/counts only; blind pools listed, never opened; no crosstrade call; no repo/NT8 write. The one blocked action (copying NinjaTrader.sqlite to scratchpad) was replaced by a read-only `mode=ro` sqlite query.
- Date note: the harness clock said 2026-08-18 at session start and 2026-08-28 after; all NT8 mtimes and web Last-Modified headers say 2026-08-28. The map's own metadata note records the same clock anomaly and resolves it to 2026-08-28.
