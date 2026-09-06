# WAVE H — CAUSAL MICRO/EXECUTION SURFACE CENSUS (2026-09-06)

**Run class: metadata/inventory only.** No price content read from any frozen pool; no frozen-pool
file opened. Only timestamp/session columns were read from already-materialized, governance-clean
substrate parquets; everything else comes from committed manifests, registries and governance memos.
Sources: `research/data/DATA_ASSET_REGISTRY.md` (@d013f62 + 2026-09-05 patch),
`runs/G2_WAVE5_CARDS_20260906/BBO_GOVERNANCE_MEMO.md`,
`research/operational/ALPHA_EVIDENCE_CLASSIFICATION.md`, `research/operational/COST_MODEL.md`,
`runs/NQ1M_BIDASK_EXTRACT_20260906/MANIFEST.md`, `runs/FLOWSUB_CENSUS_V1_20260831/out/`,
`runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/split.txt`, `research/genesis2/FAILURE_MEMORY.md`.

## §0 Program-printed seal gate (verbatim output of `wave_h_census.py`, metadata columns only)

```
surface                          rows  time col             first ts              last ts  max session  seal<2026-08-01
NQ 1-min ext (SM1M)         1,620,044      time  2022-01-02 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
ES 1-min (SM1M_ES)          1,620,385      time  2022-01-02 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
RTY 1-min (SM1M_RTY)        1,568,111      time  2022-01-02 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
YM 1-min (SM1M_YM)          1,595,378      time  2022-01-02 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
ZB 1-min (SM1M_ZB)          1,086,151      time  2022-12-26 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
CL 1-min (SM1M_CL)          1,608,018      time  2022-01-02 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
MNQ 1-min (SM1M_MNQ)        1,627,987      time  2021-12-26 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS
NQ 1-min BBO (minute)          90,358      time  2026-04-30 18:01:00  2026-07-31 16:59:00   2026-07-31             PASS

GATE  SPEC: every surface max session < 2026-08-01   OBSERVED: all pass   PASS
```

Governance-status vocabulary: **FREE** (materialized, no pool membership, usable under normal
prereg rules) · **FROZEN-POOL** (do not read; the pool's own protocol governs) ·
**BURNED-WINDOW** (2026-05-31→07-31; usable, evidence tag BURNED/LEGACY_DIAGNOSTIC —
engineering/cost use is the honest purpose) · **SEALED** (≥2026-08-01; VIRGIN, do not read) ·
**DISCOVERY-CONSUMED** (materialized AND outcome-consumed; results are discovery-grade only).

## §1 1-minute Last substrates (all FREE; all additively BACK-ADJUSTED ⇒ POINT diffs only, DELEV01)

| surface | path | sessions/rows | range | causality ceiling | governance |
|---|---|---|---|---|---|
| NQ 1-min ext | `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` | 1,620,044 bars | 2022-01-02→2026-07-31 | END-stamped minute bars; decide at bar-t close + latency, act t+1; **no quotes ⇒ no executable bid/ask PnL — cost = commission + measured/modelled spread from COST_MODEL** | FREE (05-31→07-31 slice BURNED-WINDOW) |
| NQ 1-min deep | `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` | 6,223 sessions | 2006-01-05→2026-05-29 | same; the only multi-era minute surface (STRUCTURAL) | FREE |
| ES 1-min | `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet` | 1,620,385 bars | 2022→2026-07-31 | same; read-only context instrument | FREE |
| RTY 1-min | `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet` | 1,568,111 bars | 2022→2026-07-31 | same | FREE |
| YM 1-min | `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` | 1,595,378 bars | 2022→2026-07-31 | same | FREE |
| ZB 1-min | `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet` | 923 sessions | 2022-12-27→2026-07-31 | same; 1/32 grid exactly restored | FREE |
| CL 1-min | `runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet` | 1,182 sessions | 2022-01-03→2026-07-31 | same; **CL holdout frozen** (`CL_HOLDOUT_FREEZE_20260906`) — respect that boundary | FREE (holdout-split) |
| MNQ 1-min | `runs/SM1M_MNQ_SUBSTRATE/out/mnq_1m_2022_2026.parquet` | 1,189 sessions | 2021-12-27→2026-07-31 | same; the live book's execution instrument at minute-Last resolution | FREE |
| Internals $TICK/$TRIN | `research/data_internals/` (registry rows) | 3,402/3,400 payload days | 2012-12-31→2026-07-31 | 1-min, **RTH-only (35.7 % of P1's clock)**; 2013–21 slice PRE-FROZEN/UNSPENT, era-stratified use only | FREE (era rules) |
| $VIX 1-min | registry row | 1,147 | 2022→2026-07-31 | 1-min RTH conditioner | FREE |

## §2 NQ minute-BBO (the only executable-PnL bar substrate)

`runs/NQ1M_BIDASK_EXTRACT_20260906/out/nq_1m_bidask_202605_202607.parquet` — 90,358 rows,
**66 sessions 2026-05-01→2026-07-31**, minute-close Bid+Ask OHLC (quote-series bars; `*_vol` is
quote-event volume, NOT trade volume), 0 crossed closes, END-stamped ET, seal-asserted at build.

- **Causality ceiling:** minute-close BBO; decide at bar t, fill `Ask_t→Bid_{t+h}` (long) /
  `Bid_t→Ask_{t+h}` (short) — the ALPHA_EVIDENCE §"admission object" basis. Says nothing about
  depth, within-minute quote path, or fill quality; it is a quote-width series, not an
  effective-spread series.
- **Governance:** 21 sessions PRE_BURN (05-01→05-29), 45 BURNED-WINDOW ⇒ the whole extract is
  honest for **engineering/cost/execution** work, not alpha evidence. 🔴 **Five sessions are
  frozen-pool members whose minute-close SPREAD content is now exposed** — 2026-05-04, 05-05
  (BBO_BLIND_POOL + ESNQ + MICRO + W5), 05-07, 05-08, 05-25. Recorded and owner-flagged; the
  pools' RETURNS-falsifier status is preserved, but any future SPREAD-conditioned falsifier on
  `2026-05-05` is compromised. **Any Wave-H spread-state work must list these 5 dates in its spec
  and report with/without them.**
- Measured first-look (BASIS SPREAD_ONLY, MEASURED): RTH median 3 ticks ($15.00/ctrRT),
  all-hours median 4 ticks ($20.00), p90 7; roll session 06-12 median 10 ticks; evening/overnight
  systematically wider than RTH. Convergent with EXEC01's measured $20.65 all-hours.
- **No ES minute-BBO exists**; provider-side minute-BBO depth (pre-2026-04-30) is unprobed — one
  $0 probe job is flagged in the manifest as worth running before anyone buys quote data.

## §3 Tick stores

**Materialized (all DISCOVERY-CONSUMED — outcome-consumed; results discovery-grade only):**

| store | files/sessions | range (file names) | causality ceiling | governance |
|---|---|---|---|---|
| NQ tick+BBO v2 | `research/data_microstructure_v2/raw/NQ`, 58 quote-FULL | 2025-10-15→2026-07-31 | sub-second, with source-ts discipline (int64 ns — the MS-BBO int32 overflow is the recorded failure mode); no truncation (25M cap) | DISCOVERY-CONSUMED (MS01/MS01A read it) |
| NQ tick+BBO v1 | `research/scalping_lab/substrate/raw/NQ`, 61 files / 48 sessions | 2025-08-11→2026-05-20 | sub-second; **15 files truncated at exactly 12,000,000 rows — tail-dependent features need the mask; DO NOT MERGE with v2** | DISCOVERY-CONSUMED (AUCTION01-04, FLOW01, ACTIONMAP01, U9/U9B) |
| ESNQ dev pairs | `research/data_esnq/parquet/{NQ,ES}`, 44+44 | 2025-08-14→2026-07-15 | sub-second paired ES+NQ; 200 ms-embargo grade | DISCOVERY-CONSUMED (ESNQ_V1 dev) |
| ES tick+BBO old | `research/scalping_lab/substrate/raw/ES`, 39 | 2025-08-14→2026-05-20 | sub-second; truncation unaudited | PARTLY CONSUMED; **20 ES sessions genuinely unread** outside any blind set |
| grid1s / sechilo | `research/scalping_lab/substrate/{grid1s,sechilo}/NQ`, 48/45 | 2025-08-11→2026-05-20 | 1-second L1 grid — 🔴 `grid1s.last` has a recorded **LOOKAHEAD defect** (AUCTION04): spread/cost audit only until fixed | DISCOVERY-CONSUMED + defect |

**Unextracted / frozen (metadata only — none opened):**

| object | n | governance |
|---|---|---|
| `MICRO_BLIND_CONFIRMATION_POOL` (Last-only lane) | **141 sessions**, 2025-08-12→2026-05-08 | **FROZEN-POOL** — the only genuine blind pool in the micro lane; one shot, mechanism frozen without reading it; owner/prereg-gated |
| `BBO_BLIND_POOL` | 19 RTH-complete BBO sessions | **FROZEN-POOL, falsifier-grade** — MDE $2,996/session at n=19 (can falsify, cannot confirm); 17 pristine, `2025-08-13` metadata-exposed, `2026-05-05` SPREAD-content-exposed |
| `ESNQ_BLIND_15 / EFFECTIVE_14` | 15 paired sessions | **FROZEN-POOL**, unspent |
| W5 PROTECTED 168-pool (160 untouched) | supersets the above | **FROZEN-POOL** (AMENDMENT_3 protocol) |
| NQ full-BBO tick, unextracted remainder | **57 sessions** (not "~129" — Sunday-fold + 3-substrate union corrected it) | **55 BLOCKED (pool members) · 2 SAFE: 2026-06-19, 2026-07-03** (holiday early-closes, BURNED-WINDOW, GO-ruled for extraction; engineering/cost use) |
| NQ Last-usable unextracted | 141 | = the MICRO pool — free in dollars ≠ free in governance |
| **MNQ tick store (Last-only)** | 1,177+1,469+890 files ≈1.3 GB, 2026-01-01→**2026-08-05** (128 pre-burn dates), **never read** | FREE-but-unbuilt: all `.Last.ncd` (trade prints, NO quotes); **no tick-`.ncd` parser exists in the repo**; any build must hard-drop ≥2026-08-01 and intersect pool registers first (standing Wave-5 rule) |
| ≥ 2026-08-01, everything | — | **SEALED / VIRGIN** |

**BBO-lane blind-confirmation truth (split.txt):** all 104 materialized NQ tick sessions are
outcome-consumed ⇒ **no valid blind BBO pool exists except the 19-session falsifier pool**. Any
new BBO-lane result is discovery-grade by construction and must be declared so in advance.

## §4 Measured cost/spread surfaces (execution ground truth)

| object | content | status |
|---|---|---|
| `research_sdk/cost_model.py` + `COST_MODEL.md` | NQ commission $4.36 MEASURED; MNQ $1.30 MEASURED (n=704); P1 spread $14.44 MODELLED / **$20.65 MEASURED (5.1 % coverage)** / $24.00 BOUND / $28.69 hostile-era; XM $12.50/$18.42; era-tagged | authority; every figure carries BASIS + EVIDENCE tags |
| NQ minute-BBO first-look (§2) | RTH median $15.00, all-hours $20.00, roll-day $50.00 | MEASURED, burned-window |
| `research/operational/roll_quotes/quotes.csv` | 4 rows, one timepoint 2026-09-01 05:46 ET: NQ front 4 ticks / MNQ front **1 tick** / NQ back 10 / MNQ back 11 | live operational sampling (execution-cost use only, never alpha); the 09-06→09-22 4-hourly crossover cron must be recreated every session (perishable) |
| 🔴 **MNQ spread** | **ASSUMED, never measured** — the live book's one unmeasured input; band −$5.6…+$76.3/wk at MnqPerNq=3 (−1 %…+28 % of the live edge) | open; closure paths = crossover GetQuote sampling + Roll-estimator on the MNQ tick store |

## §5 Graveyard cross-check — what is closed AT SCOPE (and what is not)

**MS-BBO is VOID as a *representation instance*, not as causal microstructure.** The coverage
matrix cell reads exactly: `CLOSED@SCOPE (MS-BBO +2.065s VOID; causal reps untested)`.

Closed at exact scope (micro/execution rows of FAILURE_MEMORY + inherited):
1. **MS-BBO-CANDIDATE-1** — sub-second BBO 30-offset feature vector → 60 s NQ return, Ridge:
   int32 overflow made 15/30 offsets read **+2.065 s into the future**; the corrected causal
   object is **−$1,785.88/session, OOF corr 0.0072**. Closes THAT object; "not repaired in place."
2. **MS-LAST-V1** — order-invariant Last-only family @60 s, frozen Ridge/GBM: null-closed
   **narrowly** — does NOT close Last-only alpha generally, other horizons, or other feature classes.
3. **ESNQ_V1** — ES↔NQ sub-minute joint quote state, 11 features @60 s: −$503/session, closed at
   exact scope; blind EFFECTIVE_14 unspent.
4. **W122** — cross-market intraday 1-min support at P1's decision events: all 4 gates fail
   (−$157 vs $503 family bar); what existed was NQ momentum wearing a cross-market label.
5. **W111** — 1-min afternoon participation fade: anti-predictive. **W121** — turnover as causal
   state: 0.0th pctile vs random-halt placebo.
6. **G2_F3_EXECSTATE01** — second-of-minute execution timing on NQ: NULL, powered (0.003 vs 0.25 tk).
7. **Order flow → P1 action value** — CLOSED-BY-POWER twice at local coverage (998 needed);
   RR_W002A ⇒ **MC-35 meta-labeling/sizing on P1 with EXISTING surfaces is BLOCKED-AS-RESCUE.**
8. Dead external effects (need a decay story to touch): seconds-scale OFI taking (≤1 s, 3.8-tick
   bar) · 1-min ES/NQ lead-lag (ms-arbitraged) · VPIN/BVC.
9. Surface defect: `grid1s.last` lookahead — causally unusable until rebuilt.

**Explicitly NOT closed** (FAILURE_MEMORY over-generalization guard): path/event-time
representations (never tested) · ES tick/BBO → NQ short horizon at TICK level (W122's null was a
1-minute family) · VWAP/market-profile (never tested) · spread state as EXECUTION ·
**re-entry/exit/sizing POLICY novelty on existing engines (never searched systematically)** ·
causal micro representations on NQ (matrix: "untested"). Adjacent lead, different column:
LIQREV01 (regime-local stress reversal, 8/8 gates, shadow reads 2026-11-01) — calendar-gated,
not a Wave-H object.

## §6 Causality-ceiling summary

| decision timing wanted | honest surface | PnL basis available |
|---|---|---|
| sub-second | tick v2 (58 s, discovery-grade only) | executable bid/ask, source-ts discipline mandatory |
| 1-second | grid1s/sechilo — **blocked** by `last` lookahead until rebuilt | spread/cost audit only |
| minute, executable-quote PnL | NQ minute-BBO 66 sessions (burned; 5 pool dates flagged) | Ask→Bid direct |
| minute, 2022+ cross-market | SM1M seven-instrument family | Last + COST_MODEL spread |
| minute, multi-era | NQ deep 2006→2026-05 | Last + COST_MODEL spread |
| live/forward execution cost | GetQuote sampling (roll_quotes) | direct quotes, ops-only |
