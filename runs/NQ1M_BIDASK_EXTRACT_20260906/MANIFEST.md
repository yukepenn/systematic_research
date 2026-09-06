# NQ1M_BIDASK_EXTRACT_20260906 — MANIFEST

**Run class:** $0 DATA EXTRACTION + one ENGINEERING/COST first-look (no hypothesis, no
signal, no P&L). Built 2026-09-06.

> 🔴 **GOVERNANCE EXPOSURE FOUND & RECORDED 2026-09-06 (Wave-5 governance check).** This run's
> date set (verified: 80 sessions 2026-04-30 → 2026-07-31) includes **`2026-05-05`, a member of
> the 19-session `BBO_BLIND_POOL`** (falsifier-grade, frozen by NAME), plus a handful in the
> larger nested pools (141 / 160-of-168). The extraction materialized minute-close **bid/ask
> (SPREAD)** on those dates — **NOT returns/outcomes** — so per the `2025-08-13` metadata precedent
> the pools' RETURNS-falsifier status is preserved, but a SPREAD/cost-conditioned falsifier on
> `2026-05-05` is compromised. **This was not intentional** — a $0 spread reader cannot see a
> name-only freeze. **Recorded, owner-flagged (`OWNER_QUEUE.md`), pool row annotated
> (`ALPHA_EVIDENCE_CLASSIFICATION.md`). Standing rule: any BBO/tick extraction must FIRST
> intersect its date list against the frozen-pool registers** (the Wave-5 governance check,
> `runs/G2_WAVE5_CARDS_20260906/BBO_GOVERNANCE_MEMO.md`). The evidence is not deleted (deleting
> research evidence is barred); it is quarantined-by-annotation.

Materializes the DATA_VERDICT_20260831 item *"NQ minute Bid/Ask — 81 sessions — 0 extracted,
never recorded anywhere"* — the only owned object that can check the modelled NQ spread
($12.50–$14.44/ctrRT family, `research/operational/COST_MODEL.md`) at 1-minute resolution.

## Object

| | |
|---|---|
| parquet | `runs/NQ1M_BIDASK_EXTRACT_20260906/out/nq_1m_bidask_202605_202607.parquet` (3,107,799 bytes) |
| **sha256** | `4b32e1bf1d0195d6b12200348c70c96696b6769e1adeca03f9f3186fbe685dc0` (identical across two independent builds) |
| **rows** | **90,358** |
| **sessions** | **66** |
| bar range | 2026-04-30 18:01:00 → 2026-07-31 16:59:00 (END-stamped ET, no shift) |
| session range | **2026-05-01 → 2026-07-31** (30 sessions on `NQ 06-26`, 36 on `NQ 09-26`) |
| columns | `time, session, contract, bid_open, bid_high, bid_low, bid_close, bid_vol, ask_open, ask_high, ask_low, ask_close, ask_vol` |
| coverage vs census | **every one of the 72 pre-seal census Bid∧Ask calendar dates is covered** (12 of those are Sundays folding into Monday sessions); the extract additionally recovered 2026-05-01 → 05-09 from provider history, before the local store's 2026-05-10 start |

**What the store/provider carries (documented, not guessed):** each side is an NT8 minute BAR
series built from the Bid (resp. Ask) quote stream — OHLC are quote prices. `bid_vol` /
`ask_vol` is NT8's quote-series volume aggregate for the minute, **not trade volume**; it is
carried through unmodified. Prices are F2-exact (NQ tick 0.25). Bars are the front contract's
own unadjusted quotes: the leg split at the 2026-06-11/12 session boundary matches the local
store's contract handoff, and each contract is the anchor (unadjusted) segment of its own
request window — verified via a Last-series probe whose volumes matched the NQ substrate
bar-for-bar and whose prices were the true 06-26 contract prices.

## Provenance

Four CrossTrade `RunStrategyBacktest` jobs (SWMinuteExport_v1, `nt8_strategy_analyzer`, NT8
8.1.8.1, fingerprint `sha256:b4255f1b0dd7fba1`, isolated Backtest account, zero orders),
Minute/1 with `bars_period.market_data_type = Bid | Ask`:

| leg | instrument | series | job | window (UTC) | CSV sha256 (first 16) |
|---|---|---|---|---|---|
| A | NQ 06-26 | Bid | `edd5edb579d648c0` | 2026-04-30T22:00:00Z → 2026-06-11T21:59:59Z | `722bb3dad426143f` |
| A | NQ 06-26 | Ask | `ccdce820493a4f72` | same | `eb521cc0e6a1abc7` |
| B | NQ 09-26 | Bid | `0d67c94b4a744416` | 2026-06-11T22:00:00Z → 2026-07-31T21:59:59Z | `e2cdf191f1dbcae3` |
| B | NQ 09-26 | Ask | `26e74ef6d05a4c23` | same | `b04b71a5b04b33b6` |

Windows are `session_boundary.py` boundaries; `to` = `session_close_boundary_utc(2026-07-31)`
— the §5 seal applied at the export. Bid↔Ask timestamp join: **0 unmatched** stamps per leg.
Plumbing was proven before the full runs: Bid/Ask/Last probes over one window produced three
distinct series with bid < ask throughout. Build: `src/build_nq_bidask.py`; full output
`out/build_log.txt`.

## SEAL assertion (program output, verbatim)

```
SEAL RULE (CLAUDE.md s5 / LOCKED_FORWARD): HARD-DROP session >= 2026-08-01
  rows dropped at build time             0
  max retained session date              2026-07-31
  ASSERT max retained session < 2026-08-01   PASS
```

Independent verification (fresh re-open): rows 90,358, sessions 66, max session 2026-07-31 <
2026-08-01 **PASS**. The census's 9 sealed BBO dates (2026-08-01→08-11) were never requested:
the export `to` predates them.

## Gates

Strictly increasing time across legs / leg sessions disjoint / no stamps in (17:00,18:00] ET /
bid OHLC sanity / ask OHLC sanity — all PASS. Crossed minute-closes (ask < bid): **0 of
90,358**.

## 5-row sample

```
                 time    session  contract  bid_open  bid_high   bid_low  bid_close  bid_vol  ask_open  ask_high   ask_low  ask_close  ask_vol
0 2026-04-30 18:01:00 2026-05-01  NQ 06-26  27630.25  27638.75  27613.50   27621.50     7802  27633.00  27643.25  27614.75   27623.50     5283
1 2026-04-30 18:02:00 2026-05-01  NQ 06-26  27621.75  27630.25  27619.75   27623.75     1821  27623.25  27632.00  27620.50   27625.00     2778
2 2026-04-30 18:03:00 2026-05-01  NQ 06-26  27623.00  27623.25  27610.75   27616.00     1390  27624.75  27624.75  27613.25   27617.25     1679
- 2026-07-31 16:58:00 2026-07-31  NQ 09-26  28311.00  28315.75  28293.25   28299.75     7200  28314.50  28318.00  28296.50   28302.75    10118
- 2026-07-31 16:59:00 2026-07-31  NQ 09-26  28299.50  28310.25  28292.25   28303.50     4872  28302.75  28314.75  28295.75   28305.50     5615
```

## FIRST-LOOK — NQ minute-close BBO spread, per session, in ticks (tick = 0.25)

**BASIS: SPREAD_ONLY, EVIDENCE: MEASURED (minute-close BBO, burned window).**
Engineering/cost measurement on ≤ 2026-07-31 data (sessions < 2026-05-31 PRE_BURN, ≥
2026-05-31 BURNED). Not forward evidence, not a cost-model verdict. `median`/`p90` are over
all ~1,380 session bars; `medRTH` over END-stamps 09:31–16:00 ET. Caveat: minute-close BBO
weights every minute equally (quiet evening minutes included) and says nothing about depth or
fill quality — it is a quote-width series, not an effective-spread series.

```
session     era      contract   bars  median     p90  medRTH
2026-05-01  PRE_BURN NQ 06-26   1380    3.00    5.00    2.00
2026-05-04  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-05-05  PRE_BURN NQ 06-26   1380    3.00    5.00    2.00
2026-05-06  PRE_BURN NQ 06-26   1380    3.00    4.00    2.00
2026-05-07  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-05-08  PRE_BURN NQ 06-26   1380    3.00    5.00    2.00
2026-05-11  PRE_BURN NQ 06-26   1380    3.00    4.00    2.00
2026-05-12  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-05-13  PRE_BURN NQ 06-26   1380    3.00    4.00    2.00
2026-05-14  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-05-15  PRE_BURN NQ 06-26   1380    4.00    5.00    3.00
2026-05-18  PRE_BURN NQ 06-26   1380    4.00    6.00    3.00
2026-05-19  PRE_BURN NQ 06-26   1380    4.00    6.00    3.00
2026-05-20  PRE_BURN NQ 06-26   1380    5.00    7.00    3.00
2026-05-21  PRE_BURN NQ 06-26   1380    5.00    8.00    3.00
2026-05-22  PRE_BURN NQ 06-26   1380    4.00    6.00    3.00
2026-05-25  PRE_BURN NQ 06-26   1140    4.00    5.00    3.00
2026-05-26  PRE_BURN NQ 06-26   1380    3.00    5.00    2.00
2026-05-27  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-05-28  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-05-29  PRE_BURN NQ 06-26   1380    3.00    5.00    3.00
2026-06-01  BURNED   NQ 06-26   1380    3.00    4.00    3.00
2026-06-02  BURNED   NQ 06-26   1380    3.00    5.00    2.00
2026-06-03  BURNED   NQ 06-26   1380    3.00    4.00    3.00
2026-06-04  BURNED   NQ 06-26   1380    4.00    5.00    2.00
2026-06-05  BURNED   NQ 06-26   1380    4.00    5.00    3.00
2026-06-08  BURNED   NQ 06-26   1380    4.00    7.00    3.00
2026-06-09  BURNED   NQ 06-26   1380    5.00    7.00    4.00
2026-06-10  BURNED   NQ 06-26   1380    7.00   10.00    5.00
2026-06-11  BURNED   NQ 06-26   1379    7.00    9.00    5.00
2026-06-12  BURNED   NQ 09-26   1380   10.00   15.00   11.00
2026-06-15  BURNED   NQ 09-26   1380    5.00    8.00    3.00
2026-06-16  BURNED   NQ 09-26   1380    4.00    6.00    3.00
2026-06-17  BURNED   NQ 09-26   1380    4.00    6.00    4.00
2026-06-18  BURNED   NQ 09-26   1380    4.00    6.00    3.00
2026-06-19  BURNED   NQ 09-26   1140    6.00    8.00    4.00
2026-06-22  BURNED   NQ 09-26   1380    4.00    6.00    3.00
2026-06-23  BURNED   NQ 09-26   1380    5.00    7.00    4.00
2026-06-24  BURNED   NQ 09-26   1380    6.00    7.00    4.00
2026-06-25  BURNED   NQ 09-26   1380    5.00    7.00    5.00
2026-06-26  BURNED   NQ 09-26   1380    7.00   10.00    5.00
2026-06-29  BURNED   NQ 09-26   1380    7.00   10.00    3.00
2026-06-30  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-01  BURNED   NQ 09-26   1380    4.00    6.00    3.00
2026-07-02  BURNED   NQ 09-26   1380    5.00    7.00    4.00
2026-07-03  BURNED   NQ 09-26   1140    6.00    8.00    4.00
2026-07-06  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-07  BURNED   NQ 09-26   1380    5.00    6.00    4.00
2026-07-08  BURNED   NQ 09-26   1380    6.00    8.00    4.00
2026-07-09  BURNED   NQ 09-26   1380    5.00    8.00    3.00
2026-07-10  BURNED   NQ 09-26   1380    4.00    6.00    3.00
2026-07-13  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-14  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-15  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-16  BURNED   NQ 09-26   1380    6.00    8.00    4.00
2026-07-17  BURNED   NQ 09-26   1380    5.00    8.00    4.00
2026-07-20  BURNED   NQ 09-26   1380    6.00    9.00    3.00
2026-07-21  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-22  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-23  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-24  BURNED   NQ 09-26   1380    5.00    6.00    3.00
2026-07-27  BURNED   NQ 09-26   1380    5.00    6.00    4.00
2026-07-28  BURNED   NQ 09-26   1380    5.00    7.00    3.00
2026-07-29  BURNED   NQ 09-26   1380    6.00    9.00    4.00
2026-07-30  BURNED   NQ 09-26   1380    6.00    8.00    3.00
2026-07-31  BURNED   NQ 09-26   1379    5.00    7.00    3.00
------------------------------------------------------------
ALL                            90358    4.00    7.00    3.00
```

Reading aids (measurement only, still BASIS: SPREAD_ONLY): 1 tick = $5.00/NQ contract, so the
all-hours median minute-close quote width is 4 t = $20.00 and the RTH median is 3 t = $15.00
per contract. Two structural features are visible and real: (a) evening/overnight minutes are
systematically wider than RTH (median column vs medRTH column); (b) the 2026-06-12 roll
session — the first session after the front handoff — printed a 10-tick median while
liquidity migrated, and 06-10/06-11 (last two pre-roll sessions) were already elevated.
Sessions of 1,140 bars are genuine early-close holidays (Memorial Day 05-25, Juneteenth
observed 06-19, July-4th 07-03).

## FEASIBILITY NOTE — the ~129 unextracted pre-seal NQ full-BBO **tick** sessions

*(Requested survey only; nothing was extracted.)*

- **What exists to do it with.** The complete tooling is already in the repo and proven at
  scale (119 session parquets on disk from the August waves):
  `research/scalping_lab/src/ninjascript/SWScalpTickExport_v4.cs` — exports Last + Bid + Ask
  1-tick series (`AddDataSeries` with `MarketDataType.Bid/Ask`, `Calculate.OnEachTick`,
  historical-only, no orders) and **rolls the output file per session date**, which was built
  precisely to kill the 12,000,000-row single-file truncation that silently clipped 17 v1-era
  files — plus `research/scalping_lab/src/python/csv_to_parquet.py` (CSV → zstd parquet +
  MANIFEST.csv row; `bip` 0=trade, 1=bid, 2=ask). Driver = the same local-path +
  `RunStrategyBacktest` flow used by this run. `SWScalpTickExport_v4` is **not currently
  compiled** into `NinjaTrader.Custom.dll` (only the WeeklyEdge classes and, since today,
  `SWMinuteExport_v1` are); the same file-drop pickup that worked today (no F5, fresh
  assembly) would be needed first.
- **Inventory.** DATA_VERDICT_20260831: 187 owned pre-seal NQ full-BBO tick sessions
  (2025-08-13 → 2026-07-31, hourly-chunked `db/tick` files, median 23/23 hour-slots and
  2.43 MB Last per session) minus ~58 already-extracted ⇒ **~129 to extract**. These are
  local recordings; provider tick-history depth was not probed in this run.
- **Size / time estimate.** Existing full-BBO session parquets measure median **34.7 MB**
  (mean 34.2, max 71.2, n=119) ⇒ ~**4.5 GB** for 129 sessions. Transient CSVs are a few
  hundred MB each but `csv_to_parquet.py` deletes each after conversion. Engine time: minute
  jobs loaded ~1.6M bars in ~15 s; tick sessions are ~2–4M events × 3 series, so plan
  roughly **1–3 min/session ⇒ ~3–6 hours** of NT8 engine + conversion, runnable in a few
  multi-session backtest windows thanks to the per-session file roll.
- **Blockers.** Technical: none identified. **Governance: one real one.** The frozen blind
  pools are defined over exactly this kind of session (memory + 
  `research/operational/BLIND_POOL_FREEZE_DEFECT_20260901.md`: pools are frozen **by name,
  not content**, and a prior lesson was that "141 extractable sessions ARE the frozen blind
  pool — free in dollars ≠ free in governance"). Before any of the 129 are extracted, the
  session list must be intersected against `research/operational/LOCKED_FORWARD.md` and the
  blind-pool registers, and pool-member sessions handled under the pools' own rules — an
  extraction job that merely *materializes* pool sessions could still consume or contaminate
  a frozen pool. That check is a precondition, not part of this run.

## Notes

- Side effects outside run dirs: shared list in `runs/SM1M_MNQ_SUBSTRATE/MANIFEST.md` §Notes.
- The deeper question this extract cannot answer: NT8 served minute BBO back to at least
  2026-04-30 from the provider (before the local store's 05-10 start). How far back
  provider-side **minute** BBO reaches was not probed (scope); if it reaches years, a much
  longer NQ minute-spread history is available for the same $0 — worth one probe job before
  anyone buys quote data.
