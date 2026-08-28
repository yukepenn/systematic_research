# TEAM D1 — EXECUTION / COST / FILL / SESSION AUDIT (PROJECT GENESIS)

Date: 2026-08-28. Read-only audit of `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research`.
No repo file modified. No mcp__crosstrade__* call. No data ≥ 2026-08-01 read (only file/row metadata of committed pre-seal outputs).

Legend: **RAW** = verified in this session by reading code/output directly. **REC** = a repo document's recorded claim.

---

## 1. Commission

| item | value | evidence | status |
|---|---|---|---|
| Canonical commission | **$4.36 / contract round turn** (NQ Lifetime template, $2.18/side) | `research/weekly_edge/src/run_we_w01.py:36` (`COMM_RT = 4.36`); identical constant in `runs/CARRY_V1_20260828/src/carry_v1.py:49`, `runs/TSMOM_TAIL_H1_20260828/src/tail_h1.py:43`, `runs/ESNQ_V1_20260828/src/esnq_batch.py:45`, `runs/MSBBO_V1_20260828/src/bbo_v1.py:40`, `runs/VOLUME_LIQUIDITY_V1_20260828/src/vl_primary.py:47`, `runs/MSLAST_CONTRACT_20260827/src/costmodel.py:47`, `research/multi_market/src/tsmom_v1.py:47`, `research/system_master/KDJMA01_5M_LADDER/src/01_kdjma01.py:22` | RAW |
| Charged **inside** the fill engine, per contract (`COMM_RT * u`) | `run_we_w98.py:74` | RAW |
| **Legacy $4.18** commission | `research/original_trader_reconstruction/solar_family/src/run_r13_strict_master.py:29` (`COMM = 4.18`). `run_we_w01.py:384` deliberately reruns the frozen 2023 artifact at `comm=4.18` for the harness check, then re-runs at 4.36 for real use | RAW |
| MNQ $0.65/side; scalping-lab table C0/C1/C2 | `research/scalping_lab/EXECUTION_MODEL.md:3-17` (incl. a documented 2026-08-08 correction of a double-counted MNQ slippage cell) | REC |

Consistent everywhere in active code; the only deviation (4.18) is quarantined to reproducing a frozen campaign-#6 artifact.

## 2. Modelled spread — where P1 $14.44 and XM $12.50 come from

**Source data (RAW):** `runs/WE_W82_FILLAUDIT` built a per-minute **median** spread profile from the 1-second BBO grid `research/scalping_lab/substrate/grid1s/NQ` — 48 files, 3 excluded for missing quotes, **3,689,792 two-sided second-bars, 2025-08-13 → 2026-05-20** (`out/fillaudit.txt` head; `run_we_w82.py:49-87`). Committed as `runs/WE_W82_FILLAUDIT/out/spread_by_minute.csv`. I verified the CSV: **1,380 of 1,440 minutes; the only hole is 1020–1079 (17:00–17:59, CME break)**; sp_tk mean 2.851, min 2.0, max 8.0 (RAW, computed this session). `we_lab.spread_profile()` fills the hole from the 16:59 value (`we_lab.py:44-47`, RAW) and `rate()` falls back to 3.0 ticks for an uncovered minute (`we_lab.py:171`, RAW).

**Charging convention (RAW):** one full spread per round turn ("a round turn crosses once: buy the ask, sell the bid"). Two implementations:
- `we_lab.rate()` (`we_lab.py:161-171`): candidate-average $/ctrRT = tick-value × spread profile weighted by the candidate's own entry **and** exit minute distribution (contract-weighted). Subtracted **post-hoc**: `series()` returns `session_pnl − rate × contracts` (`we_lab.py:174-180`). The engine itself charges commission only.
- W102 XM per-trade: `cst = COMM_RT + TICKV × (prof[entry_min] + prof[exit_min]) / 2` (`run_we_w102.py:157-158`, RAW).

**The numbers (REC unless noted):**
| figure | object | wave |
|---|---|---|
| $14.65/RT = 2.93 tk (trade-weighted, P1) | W82 headline | `out/fillaudit.txt` (RAW read) |
| $14.52 P1 · $14.55 X9a · **$12.99 BMOM** (contract-weighted; BMOM cheaper because 100 % RTH) | W89 | `runs/WE_W89_CANDCOST/REPORT.md` §2; p75 sensitivity **$18.88** |
| **$14.44 P1_PCT** · $14.46 X9a_PCT · $13.02 BMOM · **$12.50 XM_CONFLICT** | W103 (canonical, quoted in CLAUDE.md / CURRENT_BASELINE) | `runs/WE_W103_CONSOLIDATE/REPORT.md:47-51` |

$14.44 vs $14.65 vs $14.52 are the **same methodology on different trade populations/weightings** — documented in W89 §2 ("residual is contract-weighting vs W82's trade-weighting"). Not silent drift, but three numerals for one quantity circulate.

**Measured-vs-assumed status — the critical caveats (all REC, from `runs/WE_W82_FILLAUDIT/amendment_1.yaml` and `amendment_2.yaml`, read RAW this session):**
1. The first **direct** per-fill validation was **void**: 100 % of simulated opens sat outside the quote because **the 1-minute substrate is back-adjusted continuous (+282.25-pt offset on 2026-05-20) while the 1-second grid is raw front month**, plus a T-60s vs T-59s alignment bug. Fourth cross-substrate alignment defect in repo history (W44, W52, W76, W82).
2. The corrected direct estimate (`fillaudit_b.txt`, RAW read): 118 overlapping fills, **open inside the quote on only 29.7 %**; on those 35, omitted cost **$24.00/RT** — recorded as "pessimistic bound, not the headline."
3. Frozen-feed defect: 6.0 % of second-quotes sat in >60 s forward-filled runs; medians survived, means/p90 corrected.
4. **Scope (19a):** the quote sample overlaps **2.5 %** of P1's contract RTs, entirely at NQ 23,036–29,479. All deep-history (2006-21) applications **withdrawn**; 2022-26 re-quotes stand.
5. **Direction adjustment (19b) UNRESOLVED** (n = 13/22 fills): could be 0.925 or 1.085 spreads/RT ($13.55–$21.70).

**Other campaigns' spread/slippage evidence basis:**
| campaign | model | basis |
|---|---|---|
| Scalping lab | C1 = comm + 1 tick/side ($14.36 = 2.872 tk); C2 = +2 ticks; **BBO_EXEC** fills buys at prevailing Ask / sells at Bid with latency grid | C1 assumed (standardized); BBO_EXEC measured; `EXECUTION_MODEL.md` (REC). CAMPAIGN_STATE notes 1-tick spread present only 2-7 % of the time → "C1 mildly optimistic" (REC) |
| MSLAST (microstructure Last-only) | **frozen hour-of-day cost schedule** = median quoted crossing cost + $4.36 + proxy surcharge (rounded UP to ¼ tick) if the Last-print proxy flatters true Ask→Bid fills; +1/+2 tick stress ladders frozen before any alpha | measured on 58 dual Last+BBO sessions; `runs/MSLAST_CONTRACT_20260827/src/costmodel.py` (RAW) — best-governed cost model in the repo |
| MSBBO / ESNQ (2026-08-28) | true executable fills: `long_gross = (bid_out − ask_in) × DPP`, + commission + explicit extra-tick slip stress | measured BBO (`bbo_v1.py:154,166-170` RAW) |
| TSMOM / CARRY multi-market | one-way = **1 tick assumed** (PRIMARY) / 2 ticks (STRESS) × per-root tick value + comm/2; **roll close+reopen charged** on carried position | ASSUMED, no per-root quote evidence; `tsmom_v1.py:17-19,97-99` (RAW) |
| system_master / OTR | commission-only headline + 2-tick stress line | assumed; e.g. `01_kdjma01.py:191,221` (RAW) |
| WEEKLY_EDGE pre-W82 | $0 spread headline + $10/RT "2-tick" stress (`STRESS_RT`, `run_we_w01.py:37`) | assumed, superseded by W82 (RAW) |

## 3. Fill logic

**WEEKLY_EDGE canonical contract (RAW, uniform):** decision computed at bar close *i* → position applied from bar *i+1* → **fill at bar i+1's OPEN**, zero slippage; if still in position on a session's last bar, forced exit at that bar's **CLOSE** (`run_we_w01.py:322-338`; `sfills` `run_we_w38.py:43-75`; `gfills` `run_we_w98.py:59-90`; `fills_daily` `run_we_w26.py:32-76`). `gfills(per_ctr=False) == sfills` **byte-for-byte** asserted in-program (W98 B1 harness H-A, RAW code / REC PASS).

**Session box (−$1,300 halt / +$1,000 target):** accumulates **only realized trade P&L at trade close** — it can never truncate a trade mid-flight (`run_we_w98.py:74-78` RAW; confirmed in parity REPORT §5c REC). **P1 has no per-trade stop; XM_CONFLICT has no stop at all** (`CURRENT_BASELINE.md:109` REC).

**Intrabar exits, where they exist:**
- OTR `layer_b_exit` (`run_r30c_exitfamilies.py:57-94`, RAW): 130-pt stop checked **before** the discretionary exit each bar (stop wins ties — conservative); stop fills at the level, or at the **open if gapped through**; targets fill at target-or-better. Resolution from bar OHL only — true intrabar path unknown, but ordering is biased against the strategy.
- W102 XM stop arms: exit at "the breaching bar's open or the level, **whichever is worse for us**" (`run_we_w102.py:145`, RAW). XM TIME exit fills at the 15:45 bar **close** (`:139`) while entry is next-bar-open — an asymmetric convention **declared and costed** in `LIVE_READINESS.md:65-70` (REC).
- `fills_daily` partial-profit leg: touch-fill at target price (`run_we_w26.py:47-53`, RAW) — mildly optimistic (touched ≠ filled), used in legacy P1 lineage.
- Scalping lab: brackets evaluated **on the tick stream, never bar OHLC**, stops fill at the through-print, passive fills never assumed (`EXECUTION_MODEL.md:49-55`, REC).

**Partial fills / market impact:** modeled **nowhere** (RAW: no engine has size-dependent fill logic). Sizes are 1–2 contracts (portfolio peak 3, `EXECUTION_MANIFEST.md:90-92` REC) on NQ — low but non-zero risk, unquantified.

## 4. Latency

- WEEKLY_EDGE: implicit only — decision at bar close, fill at next minute's open (0–60 s). No further latency modelled (RAW).
- Scalping lab: explicit grid {0, next-event, 250 ms, 500 ms, 1 s, 2 s, 5 s}; ~4 ms timestamp fidelity confirmed by DATAPROBE01 (REC).
- Defect class on record: `research_sdk/timegrid.py:1-21` (RAW) documents the 2026-08-28 int32-overflow bug in `bbo_v1.py:119` where features read up to **2.065 s past the decision instant** — flipped a result from +$5,124/session (t 6.76) to **−$1,786/session** when corrected. Sub-second causality errors are the live wire in the newest lane.

## 5. Session-time semantics

- Sessions 18:00 → 17:00 ET; **bars END-stamped**; `sess_end = last_bar_stamp + 60 s`; NT8 `to` = one second before the next 18:00 ET open. `research_sdk/session_boundary.py` derives every boundary via `zoneinfo` (no seasonal branch) after the recorded EQV04 one-hour DST error (RAW code; REC incident). Tests exist (`test_session_boundary.py`, `test_session_unit.py`).
- **Python sessions are inferred, not calendared**: a new session begins wherever consecutive 1-min stamps gap > 60 min (`run_we_w01.py:50-52`, RAW). Consequences: a >60-min data hole or trading halt silently splits a session, resets the box, and grants a flat exit at the pre-gap close. Known instance: **2026-07-17 truncated at 10:53** (`CURRENT_BASELINE.md:333`, REC).
- P1 flattens 21 min before session end (`flatm`, `we_lab.py:82`); blocked from new entries 30 min before (RAW). NT8 parity found the flatten lands one bar earlier in NT8 (16:40 vs 16:41) on 88 trades — isolated cost **−$1.60/week** (parity REPORT §5b, REC).

## 6. NT8 Strategy Analyzer vs Python substrate

| dimension | Python research | NT8 |
|---|---|---|
| commission | $4.36/ctrRT in-engine | Lifetime template ($4.36) |
| spread/slippage | + modelled spread post-hoc (P1 $14.44, XM $12.50) | **zero slippage**, Standard fill |
| fill | next-bar-open (code) | `Calculate.OnBarClose` + market order = next-bar-open (`WeeklyEdgeP1PCT_v1.cs:24,60,172`, RAW) |
| data | back-adjusted continuous parquet (`runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet`), 1,620,044 bars | NQ 09-26 MergeBackAdjusted, CME US Index Futures ETH, 1,620,098 bars (REC) |
| parity basis | **commission-only on both sides** (`EXECUTION_MANIFEST.md:73-78`, REC) — $14.44 = 2.888 tk is not an integer per side so deliberately NOT pushed into `slippage_ticks` |

Parity result (REC, `runs/WE_P1PCT_PARITY_20260827/REPORT.md`): 2,131 vs 2,137 trades, net −1.05 %, matched 99.672 %, 1,908/2,124 matched trades to $0.00. Residuals fully classified except **8 early-exit trades (2022-12-11→2023-01-23), recorded UNRESOLVED**. Neither `.cs` uses SetStopLoss/SetProfitTarget (RAW grep) — so NT8's Standard fill is currently safe; `LIVE_READINESS.md:163-164` (REC) warns that any future intrabar order (e.g. `DisasterStopPoints > 0`) requires High (1-tick) fill resolution.

## 7. Consistency verdict across campaigns

- **Within WEEKLY_EDGE:** one fill contract, machine-asserted (`gfills == sfills` byte-for-byte). No silent divergence found (RAW).
- **Across campaigns:** cost models genuinely differ (commission-only+stress → C1 → measured-median spread → frozen hourly BBO schedule → true Ask/Bid fills) but each difference is **documented and deliberate**, and CLAUDE.md/EXECUTION_MANIFEST state the NT8-vs-research inequality explicitly. The residual inconsistencies are cosmetic-but-confusing: three circulating P1 spread numerals (14.44/14.52/14.65), a `shadow_ledger.py` docstring example using 14.44 as `expected_costs` on an XM-shaped (15:45-exit) trade whose own rate is 12.50 (`research_sdk/shadow_ledger.py:215,245`, RAW), and the legacy 4.18 commission inside frozen OTR artifacts.

## 8. Master table

| cost/fill component | implementation | evidence basis | campaigns affected | risk if wrong |
|---|---|---|---|---|
| Commission $4.36/ctrRT | in-engine, per contract | **measured** (broker template, "verified to the cent" REC) | all active | negligible |
| P1/X9a/BMOM/XM spread ($14.44/$14.46/$13.02/$12.50) | post-hoc candidate-average $/ctrRT (we_lab) or per-trade minute pair (W102) | **measured but narrow**: 45 clean sessions, one price era, 2.5 % fill overlap; direct bound $24/RT; direction factor unresolved | WEEKLY_EDGE headline A & B | ~$10/RT × 11.15 ctrRT/wk ≈ **$110/wk ≈ 9 %** of P1's $1,230 fixed-DD weekly if $24 is truer than $14.44 |
| Zero-slippage next-bar-open fill | all Python engines + NT8 Standard fill | **assumed**; only check found open inside quote 29.7 % of 118 fills | all bar-based campaigns, both sides of parity | headline erosion; parity can't detect it (shared assumption) |
| Session box, realized-only; no per-trade stop | gfills; certified .cs | design choice, disclosed | WEEKLY_EDGE | intrabar MAE unbounded; live disaster-stop would change behavior AND invalidate Standard fill |
| Intrabar stop/target ordering | stop-first, worse-of(open, level) | conservative convention, OHL-resolution | OTR, W102 arms, legacy P1 lineage | biased against strategy (safe direction); partial-profit touch-fill mildly optimistic |
| Session = >60-min gap heuristic | run_we_w01.load | assumed | all 1-min campaigns | halts/holes silently split sessions, free flat at pre-gap close |
| Spread profile 17:00–17:59 hole filled from 16:59; 3.0 tk fallback | we_lab | assumed (market closed then; low exposure) | WEEKLY_EDGE | negligible |
| 1-tick spread all roots | TSMOM/CARRY V1 | **assumed** — no quote evidence per root/era | multi_market | same error class W82's amendment withdrew for NQ deep history |
| Roll handling | WEEKLY_EDGE: flat daily, N/A; TSMOM: roll close+reopen charged; NT8 MergeBackAdjusted | mixed | multi_market; parity | small; NT8-vs-Python roll-date differences absorbed into 54-bar count gap (REC) |
| Latency | 0–60 s implicit (bar clock); scalping grid explicit | assumed / measured | all | timegrid incident shows sub-second sign-flips in BBO-lane results |
| Partial fills / impact | none | assumed away | all | low at 1–3 NQ contracts, unquantified |

## 9. Ranked five weakest execution assumptions

1. **Spread-model external validity.** The $14.44/$12.50 figures are per-minute *medians* from 45 clean quote sessions covering 2.5 % of P1's fills at one price era; the only direct per-fill measurement (n=35, selected) gave **$24.00/RT**, and the direction-adjustment (0.925–1.085 spreads/RT) is unresolved. The gap between $14.44 and $24 is ≈9 % of P1's weekly fixed-DD headline.
2. **Bar-open zero-impact fills, shared by both parity sides.** The simulated open was inside the prevailing quote on only 29.7 % of the 118 verifiable fills; size-2 market orders at the 18:00 open are assumed filled at the open print. Because NT8 mirrors the same assumption, parity certification provides zero evidence on it.
3. **No intrabar risk control in the certified objects.** P1 has no per-trade stop, XM no stop at all, and the session box counts only realized P&L at trade close — model and .cs alike. All risk statistics (maxDD $22,931 etc.) are bar-close/weekly aggregates; true intrabar MAE is unmeasured, and adding a live disaster stop would both change behavior and require a fill-resolution upgrade.
4. **Session-integrity-by-gap heuristic.** A >60-min hole or halt fabricates a session boundary, resets the box, and exits at the pre-gap close — precisely in the crash/halt scenarios where that exit is least available (2026-07-17 is a live example in-sample).
5. **Assumed 1-tick friction in the new multi-market lane** (TSMOM/CARRY, 2009-2018 dev, all roots) — the identical transportability error the W82 amendment formally withdrew for NQ's own deep history, now applied to instruments with no local quote evidence at all.

Honorable mentions: three circulating P1 spread numerals; legacy $4.18 in frozen OTR artifacts; XM's close-vs-next-open exit asymmetry (declared, costed); the int32 timegrid class for any sub-second lane.

## 10. What is genuinely strong

- One fill contract per campaign, asserted in-program (W98 H-A byte-identity; W89 §0 join assertions to 0.0 diff).
- Conservative intrabar conventions (stop-first, worse-of fills) where intrabar exits exist.
- MSLAST's frozen, proxy-surcharged, stress-laddered hourly cost schedule is exemplary and could back-port to other lanes.
- `session_boundary.py` (zoneinfo, raising guards) and END-stamp discipline eliminate two previously-paid error classes.
- Cost-model differences between research and NT8 are loudly documented in three authoritative places, with parity defined commission-only.
