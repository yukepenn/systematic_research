# TEAM C1 — Incumbent Anatomy: P1/PCT and XM_CONFLICT_v2

Session date 2026-08-28. Read-only survey of
`D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research` (hereafter REPO).
Every claim is tagged **RAW FACT** (verified in-session by reading the named file/line) or
**RECORDED CLAIM** (a repo document asserts it; not independently recomputed). No CrossTrade tool was
called; no data ≥ 2026-08-01 was read; no repo file was touched.

---

## 0. Authoritative definition documents (RAW FACT — all read this session)

| doc | owns |
|---|---|
| `research/weekly_edge/CURRENT_BASELINE.md` | research truth: economics, evidence tags, caveats |
| `research/weekly_edge/FROZEN_INCUMBENT_20260827.md` | the frozen champion definition, hashes, env, reference values |
| `research/operational/EXECUTION_MANIFEST.md` | execution truth, Analyzer settings, portfolio semantics |
| `research/weekly_edge/THE_STRATEGY.md` (2026-08-25) | narrative anatomy + parameter rationale (predates PCT freeze wording; see §8 risks) |
| `research/weekly_edge/ninjascript/LIVE_READINESS.md` | NinjaScript design, parity protocol, XM conventions, risk limits |
| `research/weekly_edge/WHAT_P1_ACTUALLY_DELIVERS.md` | honest decision table, friction line |

Four-baseline split (RAW FACT, `CURRENT_BASELINE.md:24-29`): A `P1/PCT` (RESEARCH_SINGLE), B
`{P1/PCT + XM_CONFLICT}` inverse-vol (RESEARCH_PORTFOLIO_FRONTIER), C `WeeklyEdgeP1PCT_v1`
(EXECUTABLE_SINGLE, parity-certified), D `WeeklyEdgeP1PCT_v1 + WeeklyEdgeXMConflict_v2`
(EXECUTABLE_COMPONENT_SET — explicitly NOT an executable implementation of B; integer-contract
mapping unselected, owner decision OQ-6). LIVE ENABLED: NO, everywhere.

---

## 1. WHAT P1/PCT IS — the exact object

**One sentence (RECORDED CLAIM, THE_STRATEGY.md §0):** a selection-free majority vote of 32
volatility-scaled trend-reversal ("Solar ratchet") detectors on NQ 1-minute bars, long-only,
throttled out of quiet intraday regimes, truncated both ways at the session level by a
per-contract dollar box, sized 2 on entries whose causal quality score ≥ 3.

**The closed-form arming identity (RAW FACT).** The certified NinjaScript states and implements it:

- `research/weekly_edge/ninjascript/WeeklyEdgeP1PCT_v1.cs:48-49` (comment):
  `vote = nMemLong * nThrottlePass * (1 + deltaGate) / 32`; `vote >= 0.5 <=> nMemLong * nThrottlePass * (1 + deltaGate) >= 16`.
- `WeeklyEdgeP1PCT_v1.cs:452` (code): `bool voteOK = (nMemLong * nThr * (1 + dL)) >= 16;`
- Python equivalent: `research/weekly_edge/src/run_we_w97.py:84-96` — 32 voters = 4 member-sets ×
  4 throttle settings (`QS = [None, 0.7, 0.8, 0.9]`, `run_we_w19.py:29`) × delta-gate {on, off};
  long when the voter mean ≥ 0.5. The 32 configs never exist separately in the .cs — the header
  says the collapse was verified bar-for-bar over 1,558,497 bars, max |difference| 0.0 (RECORDED CLAIM, .cs:45).

**Member sets (RAW FACT, `run_we_w19.py:26-28`):** prefixes of one VolMult ladder —
narrow5 [6,8,10,12,14] · narrow6 [+16] · narrow7 [+18] · all13 [6..30 step 2]. Only 13 shared
ratchet members exist (`.cs:97-99`: `VOLM = {6..30}`, `SETLEN = {5,6,7,13}`).

**One ratchet member (RAW FACT, `.cs:318-345`):** anchor ratchets with price; flip when price
crosses anchor ∓ S, where `S = clamp(VolMult × σ, 40, 1200 ticks)` and σ = trailing mean |Δclose|
over 460 one-minute bars (`.cs:216-223`, `VolPeriod=460`, `SMinTicks=40`, `SMaxTicks=1200`). A
member also carries a pending-position layer (`mPend`) that exits at the ratchet's own exit level.

**Combiner + hysteresis M ≥ 3.0 (RAW FACT).** Per member set:
`T = clip(round(sum/len*10), ±10)`; tilt agreement multiplies by `TiltMult 1.25`; rescale
`TiltRescale 0.9026`; `Tp = clip(round(T*mm*0.9026), ±13)`; **`M = 0.7086*Tp + 2.83*bmom`**
(`WSolar=0.7086`, `WBmom=2.83`). Hysteresis: enter long when `M >= 3.0` (`EntryLevel`), flip when
`M <= −3.0`, exit to flat when `M <= 1.0` (`ExitLevel`); new entries blocked in the last 30 min
(`EntryBlockMin`), forced flat 21 min before session end (`ForcedFlatMin`).
Locations: `.cs:179-184` (defaults), `.cs:400-437` (logic); Python `run_we_w97.py:59-82`
(`hyst()` with the literals 3.0 / −3.0 / 1.0 / −1.0; blocked = last 30 min; flat = last 21 min).
Note the doc phrase "OR-gated with the B-MOM channel" (CURRENT_BASELINE §1) is, in code, an
ADDITIVE term: bmom=+1 contributes 2.83, so bmom alone does not arm (2.83 < 3.0) but bmom + any
Tp ≥ 1 does, and Tp ≥ 5 arms without bmom. (RAW FACT from the code; the "OR" wording is shorthand.)

**Tilt (RAW FACT, `.cs:386-398`):** sign of session close minus 50-session SMA of session closes
(`TiltSma=50`), updated at each session's last bar.

**B-MOM channel (RAW FACT, `.cs:347-384`):** RTH-only. Anchor = open of the bar stamped 09:31
(= the 09:30:00 print). Running RTH vwap. Per-minute slot history of |px − open0930| capped at 60
sessions; band = mean of last 14 (`BmomBandDays=14`, needs ≥ 14 RTH days); bmom=+1 when
`px > max(open0930+band, vwap)`, −1 when `px < min(open0930−band, vwap)`; active 09:31–15:54
(sticky), zeroed ≥ 15:57 and at last bar. Python side is produced by
`run_we_w01.sm14_1m(D, 460, volmults=L13, return_members=True)` and cached as
`runs/WE_W76_FORWARD2026/out/mem_ext.npz` (arrays `mem` [n×13 member positions], `bmom`, `tilt`) —
RAW FACT, `run_we_w76.py:90-96`; every downstream wave loads the cache.

**Range throttle (RAW FACT, `.cs:439-448`):** per bar, `ratio = (prev-bar session realised range) /
(trailing 60-session median of same-minute-of-day ranges, ≥ 20 obs, 200 kept)`; voters at q ∈
{none, 0.7, 0.8, 0.9} pass when `ratio ≥ q` (or no norm). `nThr` ∈ {1..4}.

**Delta gate (RAW FACT, `.cs:450`, `CacheLagged`):** `dL = 1` iff lagged session cumulative
tick-sign × volume delta ≥ 0. Long-side voters only.

**Causal quality sizing (RAW FACT, `.cs:454-479`; `run_we_w37.causal_score`):** at a genuine
entry, five lagged features — (close−sessOpen)/ATR14, prev session return (contrarian, ≤ 1/3
quantile), signed run length (≥ 0.9 quantile), (close−vwap)/ATR14, |cumDelta|/avgVol240 — scored
against quantiles of the trailing 250 prior entries (`QualWindow=250`, `QualMinHist=100`);
**size = 2 when score ≥ 3, else 1** (~20 % of entries). CRITICAL reproduction subtlety (RAW FACT,
`run_we_w103.py:98-105` and `run_we_w98.py:152-167`): the Python score history is built on the
**size-1 `fills_daily` entry schedule** (halt 1300 / target 1000, ABS), then sizes are applied in
`gfills`; the .cs accumulates history at its own entries. The parity run showed this warm-up
difference produces symmetric size disagreements decaying to 0 by 2026.

**Per-contract session box — the PCT in the name (RAW FACT, `run_we_w98.py:59-104` `gfills` +
`arm_kw("PCT") = dict(halt=1300.0, target=1000.0, per_ctr=True)`; `.cs:260-271, 481-499`):**
session P&L accumulates `pnl/u` (per contract, commission included per contract); once
≤ −$1,300 or ≥ +$1,000 the sleeve stops for the rest of the session. Fills: decision at bar
close, market fill at NEXT bar open; open positions flattened at the session's last-bar close.
Long-only: `p == −1` on 0.00 % of bars (RECORDED CLAIM, FROZEN_INCUMBENT §4). The box is frozen —
every uniform relaxation is 16–41 % worse at fixed DD (RECORDED CLAIM, `runs/RR_W005_BOX_LATCH_VALUE/`).

---

## 2. WHAT XM_CONFLICT IS

(RAW FACT from `run_we_w103.py:119-152`, `export_xm_reference.py`, `WeeklyEdgeXMConflict_v2.cs`
parameter block; RECORDED CLAIM for the narrative in CURRENT_BASELINE §2, `runs/WE_W101_DIRECTION/`,
`runs/WE_W102_XMENGINE/`.)

- Minute-of-day keys (Python, bar-END stamps): ANCH=571 (09:31 bar — its OPEN is the 09:30:00 RTH
  open print), DEC=585 (09:45 close), ENTM=586 (09:46 open), EXITM=945 (15:45 close, research) /
  EXITNB=946 (15:46 open, NT8 convention). `.cs` defaults: AnchorHm 93100, DecisionHm 94500,
  ExitHm 154500, SigmaLookback 60, SigmaMinHist 20, MaxStaleMinutes 3, ForcedFlatMin 21,
  CommissionRT 4.36, DisasterStopPoints 0 (OFF), Qty 1.
- `drive = sign(close@09:45 − open of the 09:31 bar)` on NQ.
- Composite: for each of ES, RTY, YM, `r = log(close@09:45 / close@09:31)`, z-scored by that
  market's own trailing 60-session std (ddof=1, ≥ 20 sessions, today excluded — appended AFTER
  use); composite = mean of available z's; `xs = sign(composite)`.
- **Trade only when `xs != 0 and drive != 0 and xs != drive`** ("NQ moves alone", ~34 % of
  sessions). Direction = `drive` (NQ's own drive, not the composite). Fill 09:46 open, hold to
  15:45/15:46, size 1, **no stop** — the only intra-trade risk control is the clock. Sessions with
  a missing/stale (>3 min) secondary bar at anchor or decision are disqualified (6 of 1,058).
- Three trade counts exist and are reconciled (RAW FACT, LIVE_READINESS §3): 342 = superseded
  09:30-stamp anchor (W101/W102); **348 = canonical vectorised** (pandas rolling(60,20).shift(1);
  W102c/W103 headline); **346 = sequential loop = what the reference and the C# do** (diff: 2
  sessions, 2023-04-10 / 2023-05-03, pandas tolerates a NaN inside the window). Sequential ref mix:
  176 long / 170 short.
- `_v1` → `_v2` defect (RAW FACT, `runs/WE_XM_PARITY_20260827/REPORT.md`): v1 armed on 15
  early-close holiday sessions the research object silently drops (no 15:45 bar ⇒ `take` mask
  false); those 15 trades were −$225/trade. v2 adds one causal guard (`exitBarExists` computed
  from the session template at 09:45). v1 must not be run.
- Selection caveat (RECORDED CLAIM): the cell was best-of-27 (9 predictors × 3 decision times,
  W101) and the combination best-of-6 (W103); it cleared rate-matched (99.6th) and
  |drive|-decile-matched (99.7th) nulls, but the selections happened. N=348 in a
  DISCOVERY_CONSUMED window; REGIME_LOCAL by data availability (ES/RTY/YM substrates start
  2022-01); ~20 of 348 trades carry 85 % of the money; last 3 months t = 0.25.

---

## 3. GENERATING CODE PATHS (all RAW FACT)

Python (all under `research/weekly_edge/src/`; per-wave scripts import earlier waves' functions —
there is no single package):

| function | file | role |
|---|---|---|
| `load_deep(a, b, extend=True)` | `run_we_w17.py:28-70` | substrate: base parquet + extension, bit-exact overlap assert, session split by >60-min gap, END-stamped `t`, `sess_end = last bar + 60 s`, ISO week labels |
| `sm14_1m(D, 460, volmults=L13, return_members=True)` | `run_we_w01.py:84+` | 13 member positions, bmom, tilt (cached `runs/WE_W76_FORWARD2026/out/mem_ext.npz`, 349,535 B, 2026-08-26) |
| `votes(D, mem, bmom, tilt, ctx, chan)` | `run_we_w97.py:48-96` | 4 combiners × hysteresis (±3.0 / ±1.0) → 32-voter mean ≥ 0.5; `chan = bmom` for P1 |
| `fast_build_context(D)` | `we_fastctx.py` | ctx: `norm`, `ratio`, `dL`, `dS`, quality features |
| `fills_daily(D, p, halt=1300, target=1000)` | `run_we_w26.py:32+` | size-1 schedule; source of causal-score entry history |
| `causal_score(X, ee, window=WIN)` | `run_we_w37.py:34+`, `WIN=250` (`run_we_w38.py:39`, re-exported by `run_we_w39`) | 5-feature trailing-250 quantile score |
| `gfills(D, p, sizes, **arm_kw("PCT", 1.183))` | `run_we_w98.py:59-104` | THE fill engine: next-open fills, per-contract box, commission $4.36 inside |
| `spread_profile()` | `we_lab.py:42-47` | W82 per-minute spread ticks (`runs/WE_W82_FILLAUDIT/out/spread_by_minute.csv`), 17:00–17:59 filled from 16:59 |
| economics assembly | `run_we_w103.py` (`obj()`, `net_series()`, XM block, `pan()`) | canonical A/B numbers; ISO week on session date; fixed-DD $20,245 |
| XM reference | `export_xm_reference.py` | sequential 346-trade reference, per-session decision CSV |
| parity comparators | `run_p1pct_parity.py` (imports `gfills`, not a re-implementation), `run_xm_parity_v2.py` | trade/decision matching vs NT8 job JSON |

Constants (`run_we_w01.py:19-38`): `PV = 20.0`, `COMM_RT = 4.36`, TICKV = 5.0 (per-wave), window
A=2022-07-01, B=2026-08-01, DDT=20245.0.

NinjaScript (repo `research/weekly_edge/ninjascript/`): `WeeklyEdgeP1PCT_v1.cs`
(sha256[0:16] `ee4c765bc5cab230`), `WeeklyEdgeXMConflict_v2.cs` (`2ec00dd4d0a11b99`), both
certified at git `fc8cf85`, installed copies verified identical (RECORDED CLAIM,
EXECUTION_MANIFEST + FROZEN_INCUMBENT §2). `WeeklyEdgeP1_v3` (`e8bb9caface37462`) is the kept
comparator; `WeeklyEdgeXMConflict_v1` (`8013196e5ea1ff40`) is superseded evidence, must not run.

## 4. INPUT DATA (RAW FACT — files stat'ed this session, values not read)

| file | size | role |
|---|---|---|
| `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` | 60,667,927 B | NQ 1-min base, ends 2026-05-29 16:59 |
| `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` | 26,146,451 B | NQ extension (`extend=True`) |
| `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet` | 24,777,057 B | XM secondary |
| `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet` | 23,505,635 B | XM secondary |
| `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` | 23,957,927 B | XM secondary |
| `runs/WE_W76_FORWARD2026/out/mem_ext.npz` | 349,535 B | cached mem/bmom/tilt |
| `runs/WE_W82_FILLAUDIT/out/spread_by_minute.csv` | 12,701 B | modelled spread profile |

Population: load 2022-01-01 → 2026-07-31 17:00 (Jan–Jun 2022 warm-up only); analysis window
2022-07-01 → 2026-08-01 = **1,058 sessions / 213 weeks**. Seals: ≥ 2026-08-01 VIRGIN;
2026-05-31 → 07-31 BURNED. Known holes: 2026-07-17 truncated (ends 10:53, Python side);
2023-04-05 NT8-side afternoon gap; spread profile lacks the 17:00–17:59 CME break (filled).
XM cross-alignment verified at lag 0 (RECORDED CLAIM, W101 §0: ES +0.9316 / RTY +0.7459 /
YM +0.7650 at lag 0, two orders above ±1).

## 5. COST MODEL (RAW FACT in code; RECORDED CLAIM for the frozen statement)

Research: $4.36/ctrRT commission INSIDE `gfills`, PLUS a modelled spread applied at the
weekly-series level as a per-trade rate from the trade-time-weighted per-minute profile —
**P1 $14.44/ctrRT** (components.csv: 14.436), **XM $12.50** (= TICKV × (spread@09:46 +
spread@15:45)/2). NT8: Lifetime commission template only, 0 slippage. Parity was
commission-only on both sides. $14.44 = 2.888 NQ ticks RT — deliberately NOT pushed into NT8
slippage. A research headline and an NT8 net are never the same quantity.

## 6. RECORDED ECONOMICS (RAW FACT from `runs/WE_W103_CONSOLIDATE/out/components.csv` +
`base_recency.csv`; tags: A and B are DISCOVERY_CONSUMED)

| component | trades* | $/ctrRT spread | wk$ | wk$@fixDD($20,245) | wk+% | maxDD | top5 | worst wk | t |
|---|---|---|---|---|---|---|---|---|---|
| P1_PCT | 2,401* | 14.44 | 1,393.57 | **1,230.36** | 56.34 | 22,930.67 | 17,835 | −9,221 | 4.16 |
| XM_CONFLICT | 348 | 12.50 | 915.51 | 917.51 | 48.83 | 20,200.80 | 16,652 | −14,577 | 3.05 |
| X9a_PCT | 2,342 | 14.46 | 1,201.63 | 974.29 | 55.87 | 24,969 | — | — | 3.77 |
| BMOM | 1,152 | 13.02 | 1,120.57 | 508.83 | 57.28 | 44,584 | — | — | 2.42 |
| PAIR23 | (2B+3X9a)/5 | — | 1,169.21 | 1,308.67 | 60.56 | 18,088 | — | — | 4.36 |

*2,401 = all `gfills` trades over the 2022-01 load INCLUDING warm-up; the in-window count is
**2,131** (parity run) ≈ 10.0 entries/wk, 11.15 ctrRT/wk (W82). Do not chase the 270-trade gap.

B (inverse-vol P1+XM): **$2,011.70/wk at fixed DD, maxDD $11,489, 59.2 % positive, t 4.90** —
RECONCILED to 0.000000 on all five figures, but weights are a single full-sample in-sample std
(`run_we_w103.py:235` caution — actual line: `sd_ = {k: 1.0/max(WKS[k].std(ddof=1),1e-9)}` at
`run_we_w103.py:270` in the current file) and P1+XM was best-of-six (preregistered primary
P1+PAIR+XM = $1,765.99; see `base_recency.csv` FULL row 1,765.99). Selection-adjusted causal B ≈
$1,750–1,800/wk (RECORDED CLAIM, `runs/PORTFOLIO_B_RECONCILIATION_20260827/`).

Mix/hold/exposure: P1 100 % long; mean position size while holding 1.27; in-market 187,010 min
(8.7 % of all minutes; ⇒ ≈ 88 min mean hold per in-window trade, derived); size-2 share 19.9 %.
XM: 176L/170S (sequential), mean hold 359 min, MAE mean −$2,033 / worst −$10,865 (543 pts), ~1.6
trades/wk. Both-in-market 0.9 % of minutes; max gross = max net = 3 contracts; a master strategy
is NOT required (RECORDED CLAIM, EXECUTION_MANIFEST §26). MaxDD is week-label sensitive: ISO week
on session date $22,931 vs Sunday-ending $24,213 (+5.6 %) — ISO on session date is the convention.

## 7. NT8 PARITY STATUS (RECORDED CLAIM from the two run REPORTs, both read in full)

- **`WeeklyEdgeP1PCT_v1` CERTIFIED** (`runs/WE_P1PCT_PARITY_20260827/`): 2,131 Py vs 2,137 NT8
  (+0.28 %), matched 99.672 %, net −1.05 %, weekly ρ 0.9852, 1,908/2,124 matched trades = $0.00.
  Residuals fully classified: 123 qty disagreements (score-window warm-up, $27 net, decays to 0 by
  2026); 92 one-bar exit differences all at the 16:41/16:40 forced-flat boundary (−$1.60/wk,
  disclosed convention); **8 unresolved multi-minute exit gaps, all 2022-12-11 → 2023-01-23**,
  consistent-with-not-confirmed-as slow-member σ warm-up. Control `WeeklyEdgeP1_v3`: 2,011 trades.
- **`WeeklyEdgeXMConflict_v2` VALIDATED** (`runs/WE_XM_PARITY_20260827/`): desired_direction
  99.715 %, 347 vs 346 (+0.29 %), broad_composite max |diff| 0.000000, 175L/172S. Dollars:
  $192,937 vs $199,436; the −3.3 % gap is two data-hole sessions (−$5,739); excluding them −0.38 %
  (the priced exit convention, −$0.95/trade). v1 FAILED as preregistered (98.387 %) — the 15
  early-close-holiday extension; 100.0000 % agreement on the 1,012 normal sessions.
- Verdict bands (binding, W52): ≥ 99 % decisions + counts within 2 % = VALIDATED; 90–99 % classify
  every mismatch; < 90 % = not the object. Compare decisions before dollars.
- Analyzer config: NQ 09-26 (NQU6), 1-Minute Last, CME US Index Futures ETH, Lifetime commission,
  Standard fill 0 slippage, Backtest account, from 2022-01-03T00:00:00Z, to 2026-07-31T21:59:59Z.
  XM secondaries ES/RTY/YM 09-26 in FIXED AddDataSeries order (part of the freeze).

---

## 8. REPRODUCTION PLAN (mapping only — nothing run)

### 8.1 Minimal inputs
The five parquets + spread_by_minute.csv of §4. `mem_ext.npz` is a CACHE — an independent
implementation must REBUILD mem/bmom/tilt from `sm14_1m` semantics and may use the cache only as a
comparison target. NT8 side additionally needs the NT8 data store (its own series; note it differs
from the parquet on 2026-07-17 and 2023-04-05).

### 8.2 Build order and intermediate artifacts to compare, in this order
1. **Substrate**: bar count (Python 1,620,044 / NT8 1,620,098 over the parity load), session count
   1,058 in-window, session boundaries (>60-min gap rule vs the ETH template), END-stamped times.
2. **σ and 13 member states**: per-bar member position matrix vs `mem_ext.npz['mem']` (13 cols);
   then `bmom`, `tilt` arrays. The .cs export CSV (`ExportDir` → `we_p1pct_<tag>.csv`) carries
   `sig0/pend0/anch0/s0` for member 0 plus `tilt, bmom` per bar.
3. **Four combiner targets after hysteresis** (`tgtPrev[0..3]` in the export) — this is where the
   M ≥ 3.0 / exit ≤ 1.0 machinery either matches or nothing downstream will.
4. **Vote components** per bar: `nMemLong, nThr, dL, ratio, voteOK` (the ≥ 16 identity).
5. **Entry schedule + quality score/size**: entries of the size-1 `fills_daily` schedule; the
   5-feature vectors; score; size series (expect warm-up-dependent flips near the score-3 boundary).
6. **Trade list** from `gfills(per_ctr=True)`: (entry ts, exit ts, direction, qty, $pnl) —
   commission-only. Target: ≥ 99 % matched, counts within 2 %, most matched trades $0.00.
7. **Session P&L → ISO-week series → maxDD / fixed-DD weekly** — must bucket by ISO week on
   session date or the DD threshold is on a different convention.
8. **XM**: per-session (anchor_px, decision_px, entry_px, exit prices, nq_drive, broad_composite,
   conflict_flag, desired_direction, disqualified) vs
   `ninjascript/reference/xm_reference_decisions.csv`; broad_composite should match to 0.000000;
   then the 346-trade sequential list; then dollars last, never as a gate.

### 8.3 Known pitfalls (each one has already cost this campaign a defect)
1. **Bars are END-stamped in BOTH substrates.** The 09:31-stamped bar opens 09:30:00. Applying a
   ±1-minute shift WAS the W52 phase error (bmom agreement 95.3 %, sign inversions). The 342-trade
   XM variant came from anchoring on the 09:30 stamp.
2. **Session = 18:00 → 17:00 ET; `to` = one second before the NEXT 18:00 open**, never "end of
   day D". Python detects sessions by >60-min gaps; NT8 by the ETH template — they can disagree on
   early closes (the v1 XM defect) and on data holes.
3. **Timestamps are exchange-session ET (naive).** A UTC-based reproduction shifts every
   minute-of-day key (571/585/586/945, the throttle's same-minute median, B-MOM slots) across DST
   boundaries. Convert to America/New_York before keying.
4. **Week labels**: ISO week on session date. A Sunday-ending label moves maxDD by +5.6 %
   ($22,931 → $24,213) on the identical trades.
5. **Warm-up is part of the object**: load from 2022-01-03; quality-score window (250 entries,
   min 100) and XM σ history (60/20 sessions per market) must be fed by EVERY loaded session,
   including pre-window months — gating the σ history on the study window cost 4 trades.
6. **The quality score's entry history comes from the size-1 `fills_daily` schedule**, not from
   the final PCT schedule. Reimplementing it on the final schedule is a silent divergence.
7. **Per-contract box**: accumulate `pnl/u` (point term AND commission per contract) at BOTH
   accumulation sites (intra-session exit and session-close flatten). Halving only one is "a third
   convention". Under `per_ctr=True` the schedule is size-invariant (no fixed-point problem).
8. **Cost layering**: commission inside the fill engine; modelled spread applied as a per-trade
   rate at the weekly assembly (`net_series`), not per bar; NT8 nets are commission-only. Never
   quote across models. The B portfolio additionally uses in-sample inverse-vol weights.
9. **XM exit convention**: research = 15:45 bar CLOSE; NT8-consistent = 15:46 bar OPEN
   (−$0.95/trade, measured). The .cs and the certified numbers use the NT8 form.
10. **Sequential vs vectorised σ**: pandas `rolling(60, min_periods=20)` tolerates interior NaNs;
    the causal loop disqualifies — 2 sessions differ (346 vs 348). The loop is the frozen rule.
11. **Class-name staleness in NT8**: deleting a .cs does not remove the type from
    `NinjaTrader.Custom.dll`; verify by resolving the class. Never rename a certified class.
12. **Instruments are parameters**: a hardcoded contract once ran the whole stack on a deferred
    month (−$24,269 vs +$8,326, W44 amendment 2). Same roll convention (MergeBackAdjusted) on all
    four series; fixed AddDataSeries order; indexed accessors (`Closes[i][0]`) only.

### 8.4 Doc-vs-code ambiguities = the reproduction risks
- **THE_STRATEGY.md (2026-08-25) is partially stale**: it narrates "range throttle q = 0.8" and a
  single member set ("narrow6"), while the frozen object votes over q ∈ {none,0.7,0.8,0.9} × 4
  member sets; it also describes the P2 "cut" layer (23-bar hold), which is NOT part of P1/PCT;
  and its §5 delivery table predates the PCT box and the W76 window extension. Use the .cs +
  run_we_w97/w98 as ground truth, THE_STRATEGY.md only for rationale.
- "OR-gated with B-MOM" (CURRENT_BASELINE §1) describes an additive 2.83-weight term, not a
  boolean OR — reproduce the arithmetic, not the phrase.
- components.csv `trades` includes warm-up trades (2,401) vs the in-window 2,131 quoted everywhere
  else.
- The B-reconciliation cites `run_we_w103.py:235` for the in-sample weight caution; in the current
  file the inverse-vol weights are at lines 235-238 (combinations) and 270-272 (primary) — line
  drift, same substance.
- The 8 unresolved P1 exit gaps (2022-12/2023-01) and the 2 XM data-hole sessions are OPEN
  residuals an independent reproduction should expect to hit and must not "fix" silently.
- XM canonical N: quote 348 (canonical vectorised) or 346 (sequential/executable) with the
  implementation named; never mix.
