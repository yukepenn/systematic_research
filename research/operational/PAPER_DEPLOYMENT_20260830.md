# PAPER DEPLOYMENT RECORD — {P1/PCT + XM_v2} @ M_11 on DEMO8383477

**Deployed 2026-08-30 ~06:16 ET** under the owner instruction recorded in
`OWNER_DECISION_20260830.md`. **Paper account only. LIVE (real money) ENABLED = NO.** — ⚠️ **true for THIS deployment and on the day it was written.** A separate real-money book was enabled on `2047681` on 2026-09-01; this document does not describe it. See `CURRENT_LIVE_TRUTH.md`.

## ⚠️ COLD-START DEFECT FOUND AND FIXED (same morning, before the first session)

The FIRST deployment (`dep_46b904d97604` / `dep_01b21182696c`) loaded only **5,518 bars ≈ 4
sessions** of history. That is a real fidelity defect, not a cosmetic one:
`WeeklyEdgeP1PCT_v1.cs:467` gates quality sizing on `if (qCount >= QualMinHist)` with
**QualMinHist = 100 entries** and a **250-entry** rolling window — so a cold deployment would
have traded **size 1 only for ~3 months** and been out of steady state for ~7. XM's 60-session
sigma and P1's 14-day B-MOM band were likewise unfilled.
**Fix:** every state in both engines is a ROLLING window (460 bars / 50 / 14 days / 250 entries)
— none is cumulative-since-inception — so a warm-up longer than the longest window reproduces
steady state exactly. Both legs were stopped (account verified flat) and redeployed with
**`DaysToLoad = 365`** (`StrategyBase.DaysToLoad`, settable via the deploy `parameters` block).
**Corroboration that the fix worked:** the redeployed instances processed **352,670 bars
(~255 sessions)** and their historical-simulation P&L tracks the certified backtest — XM's
warm-up shows **$43,705** against a Strategy-Analyzer 2026 Jan–Aug figure of **$42,997**.

## What is running (current)

| leg | class | deployment_id | strategy_id | instrument | warm-up | state |
|---|---|---|---|---|---|---|
| P1 | `WeeklyEdgeP1PCT_v1` | **`dep_306e11dfc8eb`** | 399550060 | NQ 09-26 (NQU6) 1-min | **365 days / 352,670 bars** | **Realtime, is_trading=true, flat** |
| XM | `WeeklyEdgeXMConflict_v2` | **`dep_5a914d070687`** | 399550061 | NQ 09-26 + ES/RTY/YM 09-26 1-min | **365 days / 352,670 bars** | **Realtime, is_trading=true, flat** |

⚠️ **Any future redeploy MUST pass `DaysToLoad = 365`** (or more). A default-warm-up deployment
is NOT the certified object. Superseded deployments: `dep_46b904d97604`, `dep_01b21182696c`
(stopped and removed from the registry; they never traded — the shadow runner's watermarks were
unchanged at 584/852 throughout).

## NT8 strategy folder cleaned (2026-08-30)

Kept: `WeeklyEdgeP1PCT_v1.cs`, `WeeklyEdgeXMConflict_v2.cs` (the book), `WeeklyEdgeP1_v3.cs`
(P1/ABS, shadow-roster control), NT8's own `@Sample*`/`@Strategy`.
Moved to `bin/Custom/_quarantined_strategies/` (reversible, not deleted): six dormant data-export
utilities `SWBarExport_v1/v2/v3`, `SWContractFetch_v1`, `SWScalpTickExport_v4`,
`SWScalpTickExportAllow_v1`. `SWContractFetch_v1.cs` had **no repo copy** and was archived first
to `research/archive/ninjascript_utilities/`. ⚠️ NT8 keeps compiled types in
`NinjaTrader.Custom.dll` until it restarts and recompiles — quarantining the source does not
immediately remove the type.

- Account **DEMO8383477** (verified paper: connection "Simulation", flat, $0 balances).
- Trading hours template `CME US Index Futures ETH` on both (23-hour session — correct for P1,
  which places 61.7% of its entries outside RTH).
- All frozen parameters are the certified SetDefaults values (P1: VolPeriod 460, Entry 3.0 /
  Exit 1.0, box −$1,300/+$1,000, quality sizing ON; XM: 09:31 anchor / 09:45 decision / 15:45
  exit, σ 60 sessions, qty 1, **DisasterStopPoints = 0 (OFF, as certified)**).
- XM's four data series loaded and verified (NQ+ES+RTY+YM); its instrument-mismatch hard-block
  did not fire.
- ⚠️ P1's live panel shows `net_profit_currency 4410` with `trade_count 0` — that is **internal
  historical-bar simulation**, not account activity. Confirmed: the shadow runner ingested
  **zero** order/execution rows after deployment (watermarks unchanged at 584/852).

## Shadow logging

`GENESIS_ShadowRunner` scheduled task registered — **daily 17:10 ET**, next run 2026-08-30 17:10.
Ingests the paper account's order/execution stream into the hash-chained ledger.

## The two clocks — deliberately different

| clock | starts | meaning |
|---|---|---|
| **paper trading** | **tonight, Sun 2026-08-30 18:00 ET** (next session open) | the strategies trade every session from now on |
| **formal shadow ledger** | **2026-09-01 18:00 ET** (preregistered, UNCHANGED) | the research evidence clock |

The ~2-session gap is **kept on purpose and is a feature**: it is a plumbing shakedown. If a fill,
a data series, or the runner is broken, it surfaces in `spillover.jsonl` during the warm-up
instead of contaminating day 1 of the evidence ledger. Warm-up trades are **recorded, not lost**
— they are simply not prospective-evidence rows. Moving `SHADOW_START` earlier was considered and
**declined**: a preregistered boundary that moves when it becomes convenient is worth less than
the two sessions it would buy.

## Operational watch items

1. **NT8 must be running and the "Simulation" connection connected** for both trading and
   logging. After any NT8 restart, verify both strategies are still enabled
   (`ListDeployedStrategies`) — account-hosted strategies do not always survive a restart.
2. ⚠️ **CONTRACT ROLL ~2026-09-10** (Sept expiry is the 18th; volume rolls ~8 days prior). Both
   legs must be redeployed on **NQ 12-26**, and XM's `EsInstrument`/`RtyInstrument`/`YmInstrument`
   parameters must be set to **ES 12-26 / RTY 12-26 / YM 12-26** at redeploy — they default to
   09-26 and stale series would degrade the composite. Added to `MONITORING_CALENDAR.md`.
3. ⛔ **XM v1 must never be deployed** (holiday defect, −$225/trade on 15 early closes). Only v2.
4. Sim economics ≠ research economics (NT8 template commission, zero modeled spread). The sim
   stream is **execution evidence**, and it does not restate the research headline.

## REDEPLOY 2026-08-30 ~09:46 ET — after an NT8 restart wiped both strategies

Owner restarted NT8. **Both strategies were gone** (NT8 list AND CrossTrade registry both empty) —
see the runbook's persistence section; this is now a recorded platform fact, not a hypothesis.
Redeployed identically:

| leg | deployment_id | strategy_id | warm-up | state |
|---|---|---|---|---|
| P1 | **`dep_68588bacd445`** | 399562865 | 365 days / 352,670 bars | Realtime, flat |
| XM | **`dep_7f22307847c2`** | 399562866 | 365 days / 352,670 bars | Realtime, flat |

Warm-up P&L reproduced exactly ($70,585 / $43,705), confirming the restored instances are in the
same state as before the restart. Superseded: `dep_306e11dfc8eb`, `dep_5a914d070687` (never traded).

## ⭐ SWAP TO HARDENED CLASSES — 2026-08-30 ~09:51 ET (before the first session)

| leg | class | deployment_id | strategy_id | state |
|---|---|---|---|---|
| P1 | **`WeeklyEdgeP1PCT_v2`** | **`dep_55403f7de5f5`** | 399562867 | Realtime, flat, 352,670 bars |
| XM | **`WeeklyEdgeXMConflict_v3`** | **`dep_0274eec46398`** | 399562868 | Realtime, flat, 352,670 bars |

**Why this is safe: the hardened classes are trade-for-trade IDENTICAL to the certified ones.**
Proven twice on the certified window (2022-01-03 → 2026-08-30, same instrument/bars/fill/hours):
**P1 2439 trades $354,575.96 — 0 of 2439 rows differ; XM 378 trades $182,776.92 — 0 of 378.**
14 fields compared; exported CSVs byte-identical. Confirmed a third time in production: the
deployed hardened instances report warm-up P&L **$70,585 / $43,705 — the same values the certified
instances reported.**

**What the hardening adds (all realtime-gated, provably inert historically):** shadow fill ledger
from `OnExecutionUpdate`; `OnOrderUpdate` reject/cancel/partial latch; the ledger-vs-`Position`
invariant that closes hazard H1 (blocks ENTRIES on divergence, never exits); a correct
instrument-month guard (the certified one compares only the root, so `"ESZ6".StartsWith("ES")`
passed — a partial roll could trade Dec NQ against Sept secondaries silently); a fail-safe roll
block N days before expiry; and a **warm-up certificate**.

**Warm-up certificate, printed at go-realtime (NT8 log 09:51:30 / 09:51:38):** both
`verdict=GO blocked=False`. P1 — qual_entries **437 / 250 required**, volnorm 240/240, bmom 256/14,
tilt 257/51, rng 200/60, atr 14/14, sigma 460/460. XM — ES/RTY/YM history **257 sessions each,
60 required.** The cold-start hazard is now machine-verified at every start, not inferred.

**Orchestrator override recorded:** the build had declared `ConnectionLossHandling = StopStrategy`
and `NumberRestartAttempts = 0`. Both were REMOVED — with no stop on either leg, StopStrategy on a
disconnect abandons an open position with nothing to exit it, while the platform default keeps the
strategy alive to run its own exits, and the new H1 invariant covers the risk that default used to
carry. NT8's own enable-time read-back then **proved the certified install runs
`ConnectionLossHandling = Recalculate`, `MaxRestarts = 4`** — so the revert lands the hardened
classes exactly on certified platform values.

Superseded: `dep_68588bacd445`, `dep_7f22307847c2` (certified v1/v2; never traded).

---

## ✅ FULL PRE-SESSION VERIFICATION — 2026-08-30 ~10:25 ET (owner request: "confirm the strategy list, delete what we don't want, make manual backtest correct, guarantee tonight")

### A. NT8 Strategies folder — cleaned to EXACTLY the deployed book

Four non-deployed classes were moved to `bin/Custom/_quarantined_strategies/` (**moved, not deleted**;
each was SHA-256-verified byte-identical to its repo copy in `research/weekly_edge/ninjascript/`
**before** the move, so all four are restorable in one copy):

| removed from Strategies | sha256[0:12] | why it went |
|---|---|---|
| `WeeklyEdgeP1_v3.cs` (P1/ABS) | `E8BB9CAFACE3` | removed from the shadow roster the same day (`runs/G2_ABS_VS_PCT_20260830/`) — nothing uses it |
| `WeeklyEdgeP1PCT_v1.cs` | `EE4C765BC5CA` | certified original; `_v2` is proven row-identical (0/2439 rows differ). Keeping both is a wrong-object deploy hazard and a backtest ambiguity |
| `WeeklyEdgeXMConflict_v2.cs` | `2EC00DD4D0A1` | same, vs `_v3` (0/378) |
| `WeeklyEdgeBookM11_v1.cs` | `9499F19D0C39` | self-documented **NOT parity-certified**; it *nets* the two legs, so its trade list is a different economic object. A trap for anyone manually verifying the book |

**Remaining:** `WeeklyEdgeP1PCT_v2.cs`, `WeeklyEdgeXMConflict_v3.cs`, and NT8's own `@Sample*`. Nothing else.

**Deployments survived the file move** — same strategy ids `399562867` / `399562868`, both still
`Realtime`, flat, same warm-up P&L ($70,585 / $43,705). No recompile was triggered.

### B. ⚠️ THE FOLDER IS CLEAN; NT8's IN-MEMORY TYPE LIST IS NOT (until the next restart)

`SearchNinjaScriptSymbols` proves NT8 still resolves **all six** WeeklyEdge classes, each in **three
assembly generations** (`NinjaTrader.Custom`, `d938f577…` = the running one, `eaaad6fa…`). Compiled
types are never unloaded from the AppDomain — quarantining source does not remove them.

⇒ **Strategy Analyzer's dropdown will still list the four retired names today.** Pick only
`WeeklyEdgeP1PCT_v2` / `WeeklyEdgeXMConflict_v3`. The stale names disappear on the next NT8 restart
(which also wipes the deployments and requires a redeploy — see the persistence rule above).

**The duplicate generations were tested, not assumed:** both reference backtests below reproduced
their certified numbers **to the cent**, which proves the resolver is binding the current code and
not a stale generation.

### C. ⭐ MANUAL BACKTEST RECIPE — verified reproducible, with the exact numbers to expect

Run in Strategy Analyzer with **these** settings; anything else changes the answer.

| setting | value | why it matters |
|---|---|---|
| Strategy | `WeeklyEdgeP1PCT_v2` / `WeeklyEdgeXMConflict_v3` | the deployed objects |
| Instrument | `NQ 09-26` | XM pulls ES/RTY/YM 09-26 itself from its own parameters |
| Bars | **1 Minute** | |
| Session template | **CME US Index Futures ETH** | 23-hour. P1 places 61.7% of entries outside RTH — RTH silently deletes them |
| From / To | **2022-01-03 → 2026-08-30** | Analyzer **ignores `DaysToLoad`**; the ≥1yr warm-up must be *inside* the window |
| Account | **Backtest** (template `NinjaTrader Brokerage Lifetime`, verified installed) | supplies the $4.36/ctrRT. A template-less account reports GROSS |
| Fill / slippage | `Standard` / **0 ticks** | |
| Max bars look back | **Infinite** | the 256 default silently truncates |

**Verified 2026-08-30 through the real Strategy Analyzer engine (NT8 8.1.8.1, `RunStrategyBacktest`,
fingerprint `sha256:b4255f1b0dd7fba1`):**

| leg | closed trades | **sum of closed-trade P&L** | certified reference | match |
|---|---:|---:|---:|:--:|
| `WeeklyEdgeP1PCT_v2` | **2,439** (`shape_errors 0`) | **$354,575.96** | $354,575.96 | ✅ exact |
| `WeeklyEdgeXMConflict_v3` | **378** (`shape_errors 0`) | **$182,776.92** | $182,776.92 | ✅ exact |

⚠️ **Read the CLOSED-TRADE SUM, not the summary `Net profit` box.** NT8's `NetProfit` also counts a
position still open at the window edge, so it reports **$356,317.24 (2,440)** for P1 and
**$179,072.56 (379)** for XM. **This finally identifies the $1,741.28 "window-edge artifact"**
seen in the earlier BookM11 analysis: it is P1's open trade at the right edge, nothing more.

⚠️ **An NT8 net is still not the research headline.** NT8 charges the commission template and **zero
slippage**; research additionally charges a modelled spread (P1 $14.44/ctrRT). Same object, two
different quantities — never quote one for the other.

### D. Manual-backtest correctness hazards checked and cleared

1. **No commission double-count.** `IncludeCommission = true` (NT8 charges the template once);
   the strategies' `CommissionRT = 4.36` feeds **only** the internal W98 per-contract session box
   (`:918`), which is certified signal logic, not a P&L report. Verified: $4.36 charged per trade.
2. **The hardening is provably inert in a backtest.** Every added hook opens with
   `if (State != State.Realtime) return;` (the "M1" gate, ~15 call sites). Confirmed empirically by
   the exact reproduction above.
3. **The roll fail-safe cannot distort a backtest.** `RollBlocked()` returns `false` whenever
   `State != State.Realtime` (`:476`), and `ResolveRollDates` is never called historically (`:444`).

### E. Tonight (Sun 2026-08-30 18:00 ET) — live-readiness check

| check | result |
|---|---|
| Connection `Simulation` | **Connected**, up 39 min, user `rainazur` |
| Account `DEMO8383477` | **Connected, flat**, cash $90,335, status Enabled — **paper; LIVE real money = NO** |
| Open positions / working orders | **none** (`ListPositions` empty, `active_order_count 0` both legs) |
| P1 `dep_55403f7de5f5` | Realtime, is_trading, flat, 352,670 bars |
| XM `dep_0274eec46398` | Realtime, is_trading, flat, 352,670 bars, all 4 series live (NQU6/ESU6/RTYU6/YMU6 — **all September, no partial roll**) |
| Warm-up certificates | both `verdict=GO blocked=False` (NT8 log 09:51:30 / 09:51:38) |
| Frozen parameters | read back from NT8 and matched against the certified SetDefaults — all match |
| `GENESIS_ShadowRunner` | scheduled task **Ready**, daily 17:10 ET |
| Trades so far | **0** on both — the $70,585 / $43,705 are internal historical simulation, not account activity |

### F. Open items (neither blocks tonight)

1. 🔴 **The roll deadline is ~09-02, not ~09-10** — see `MONITORING_CALENDAR.md`. The fail-safe
   blocks NEW ENTRIES from `stored rollover − 8 days`; **exits are never gated**, so it fails safe.
   The exact date resolves on tonight's first realtime bar and is logged as
   `ROLL-PLAN blockNewEntriesFrom=…`. **Read that log line and pin the calendar row.**
   (It has not resolved yet: it is Sunday, no realtime bar has arrived.)
2. **Connection-drop behaviour (H5) is still untested** in production.
3. **After ANY NT8 restart: both strategies are gone.** Redeploy with `DaysToLoad = 365` and
   re-verify. A restart is also the only way to flush the stale types in §B.
---

## ⭐ WARM-UP CONVERGENCE — MEASURED, and it CORRECTS an overstatement made earlier today

**The claim recorded this morning was too strong.** This file said every state is a rolling window,
"so a warm-up longer than the longest window reproduces steady state **exactly**." That is true of
the rolling-window states but **not of all of P1's state**:

- **Rolling-window states — exact once filled:** sigma 460 bars, tilt SMA 50, B-MOM band 14 days,
  range 60 sessions, ATR 14; XM's sigma 60 sessions.
- **NOT a rolling window:** P1's **13 shared ratchet members** (`mUp`/`mAnchor`/`mS`, `:131-134`).
  A ratchet's anchor is **path-dependent with no fixed lookback** — it persists until price moves
  far enough to flip it. There is no window whose expiry guarantees agreement.
- **Also not a time window:** the quality-sizing window is the last **250 ENTRIES** — an
  event count, so the calendar time needed to fill it varies with trade frequency.

So convergence had to be **measured, not derived**. Two Strategy Analyzer runs of the identical
class, differing ONLY in start date (2022-01-03 vs 2025-08-30), compared trade-by-trade on
`entry time | entry price | qty | P&L` over their common tail:

| warm-up elapsed at the cut | trades (short vs full) | **differing rows** | net difference |
|---|---:|---:|---:|
| 0.6 mo | 436 vs 419 | **101** | −$49.36 |
| 4.1 mo | 285 vs 285 | **10** | −$858.08 |
| 7 mo | 168 vs 168 | **2** | +$499.36 |
| **9 mo** | **107 vs 107** | **0** | **$0.00** |
| 11 mo | 39 vs 39 | **0** | $0.00 |

### What this establishes

1. ✅ **`DaysToLoad = 365` is now empirically justified, not assumed.** Full convergence lands at
   **~9 months**; 12 months clears it with ~3 months of margin. This is the first direct evidence
   for the number — it had been chosen on a rolling-window argument that is now known to be
   incomplete.
2. ⛔ **A cold start is not a cosmetic defect.** In its first month the under-warmed instance took
   **17 extra trades** and differed on 101 rows. It is a different object, exactly as feared.
3. **Convergence is complete, not merely asymptotic** — 0 differing rows, $0.00, sustained over the
   last two windows. The ratchet does re-synchronise; it just does so by re-flipping against price
   rather than by a window expiring.
4. **Aggregate P&L is far more robust than composition.** Even at 0.6 months, where 101 rows differ,
   the net differs by only −$49.36. Path differences largely wash; do not read a small net agreement
   as evidence that two instances are in the same state.

### What it does NOT establish

**This does not mean the live instance will track a backtest.** Warm-up equalises the *state*; it
cannot equalise *fills*. Once a live fill differs from the modelled fill, the ratchet has **no
resynchronisation point**, so live-vs-backtest tracking error can only grow. That doctrine is
unchanged: **judge forward performance on economics, never on path-matching.**
---

## ⭐ WHY WARM-UP MATTERS, QUANTIFIED: quality sizing carries **87 %** of P1's edge

The cold-start defect was described earlier as "trades size-1-only for ~3 months." That understated
it. Splitting all 2,439 certified trades by contract size:

| size | trades | share of trades | **net** | share of net |
|---|---:|---:|---:|---:|
| **qty 1** | 1,939 | 79.5 % | **$46,005.96** | 13.0 % |
| **qty 2** | 500 | **20.5 %** | **$308,570.00** | **87.0 %** |

**A fifth of the trades carry seven-eighths of the money.** Quantity 2 is reached only through causal
quality sizing, which requires `qCount >= QualMinHist (100)` and a filled `QualWindow` of **250 prior
entries** — precisely the state a cold start does not have.

⇒ **A default-warm-up deployment does not "differ slightly" from the certified object; it discards
87 % of the edge for roughly its first three months.** `DaysToLoad = 365` is not hygiene, it is the
strategy.

August 2026 shows the same split in miniature: **qty 1 lost −$14,463.36 (26 trades) while qty 2 made
+$26,116.64 (13 trades).**

## Evidence status of the August 2026 window — ⚠️ it is NOT out-of-sample validation

August was sealed (`≥2026-08-01 VIRGIN`) until the owner granted a read this session; it has now been
consumed for `P1/PCT` and `XM_CONFLICT_v2`. Headline vs the discovery window (NT8 cost basis):

| leg | discovery 2022 → 2026-07-31 | **August 2026** |
|---|---:|---:|
| P1/PCT | $1,436.54/wk (2,400 trades) | **$3,546.65/wk** (39 trades) |
| XM_CONFLICT | $742.83/wk (373 trades) | **$2,735.31/wk** (5 trades) |

**Do not read this as confirmation.** The apparent outperformance is **one trade per leg**:

- **P1: the single best trade is +$26,951.28 = 231 % of the month's net. Ex-top-1 August is −$15,298.00**;
  ex-top-3 is −$20,440.56. **August win rate 25.6 %, BELOW its own history.**
- **XM: top trade $10,755.64 = 115 % of net. Ex-top-1 is −$1,377.44** (on 5 trades total).

The big trade was checked for a data artifact and is **genuine**: 2026-08-04, long 2 @ 29,146.50 at
07:17, out 14:02 @ 29,820.50 — a 674-point (2.3 %) NQ trend day, MAE only $280. Real trade, real
regime, but N=1. This is the known tail-carried structure (top 10 % of trades = 236.8 % of net), not
new evidence.

⇒ **~3 weeks and 39/5 trades cannot validate anything.** The forward paper stream starting tonight is
the only clean prospective evidence, which is exactly why the shadow ledger exists.
---

## 🟢 SESSION 1 IS LIVE — first realtime bars 2026-08-30 18:00:00 ET

Verified at **18:28 ET**, 28 minutes into the first session. Paper account. **LIVE real money = NO.**

| check | observed |
|---|---|
| Market | **open** (`isMarketOpen: true`), NQU6 bid 29,475.00 / ask 29,476.50, last 29,475.50, volume 5,532 @ 18:28:13 ET |
| P1 bars | 352,670 → **352,699 (+29)** — advancing with the clock |
| XM bars | `currentBars [352699, 352638, 346466, 347699]` — **series 0 (NQ) is in lockstep with P1**. ⚠️ The registry's scalar `current_bar` shows **346,466**, which looks like a 6,204-bar REGRESSION but is just the RTY series index on a 4-series strategy. Read `currentBars[0]`, never the scalar, on XM |
| Positions / orders | both **Flat**, 0 trades, `activeOrderCount 0` |
| H1 invariant at the transition | `WARMUP-CARRY-FLAT ledger=0 strategyPosition=0` on **both** legs — reconciled, nothing carried, entries not blocked |

**Full warm-up gate table (logged 09:51, all PASS):** P1 — sigma_diffs 460/460, tilt 257/51,
bmom 256/14, rng 200/60, atr 14/14, volnorm 240/240, **qual_entries 437 (spec 250, min 100)**.
XM — xm_hist_ES/RTY/YM **257 sessions each** (spec 60, min 20). ⇒ **quality sizing is armed from
bar one**, so the 87 %-of-edge qty-2 trades are reachable tonight.

### ⭐ ROLL DEADLINE RESOLVED — the estimate was wrong, the machine is authoritative

```
P1  ROLL-PLAN blockNewEntriesFrom=2026-09-08 leadDays=8 earliestStoredRollover=2026-09-16 [s0=NQU6:2026-09-16]
XM  ROLL-PLAN blockNewEntriesFrom=2026-09-06 leadDays=8 earliestStoredRollover=2026-09-14
                                     [s0=NQU6:09-16 s1=ESU6:09-14 s2=RTYU6:09-15 s3=YMU6:09-18]
```

**XM binds first, 2026-09-06**, because it takes the MIN across four series and **ES rolls earliest
(09-14)** — a coupling that only exists on the multi-series leg. P1 binds 09-08.
⇒ ~~**Roll both legs by Friday 2026-09-04.**~~ My earlier ~09-02 figure was a guess built on a
guessed 09-10 rollover; it is superseded.
🔴 **AND SO IS THIS ONE — WITHDRAWN 2026-08-30, MARKED INLINE 2026-09-01.** Rolling on 09-04
would re-enable the book *before* its block dates and then latch it dead from 09-06/09-08 with
every health check green. Recorded as withdrawn in `STATE_20260831.md:42`, but this line was
reachable un-annotated from `MONITORING_CALENDAR.md`. Correct rule: **both legs ≥ 2026-09-19** (practically Mon 2026-09-21) — P1's MNQ series rolls **09-18**, two days after NQ's.
Authority: `research/operational/CURRENT_LIVE_TRUTH.md` §ROLL. Exits are never gated, so a missed roll stops new risk rather
than stranding a position.

### What to expect tonight

**P1 can trade at any hour** (61.7 % of its entries are outside RTH). **XM cannot act until Monday
morning** — it anchors 09:31, decides 09:45 and exits 15:45 ET, so a Sunday-evening session is a
no-op for it by construction. XM showing 0 trades tomorrow before 09:45 ET is correct behaviour,
not a fault.
---

## 🟢 FIRST LIVE TRADE — 2026-08-31 00:58:00 ET

`WeeklyEdgeP1PCT_v2` opened the book's first paper position.

| field | value |
|---|---|
| order id | `581992641240` |
| filled | **2026-08-31 00:58:00 ET** |
| action | **Buy 2** NQU6 @ **29,421.00**, Market, signal `"L"` |
| owner | strategy `399562867` `WeeklyEdgeP1PCT_v2` |
| `isBacktestOrder` | **false** — a real paper order, not historical simulation |

**Two things this confirms, both of which were arguments rather than observations until now:**

1. ⭐ **It sized 2 contracts.** Quality sizing requires a warm 250-entry window; a default-warm-up
   deployment would have taken **1**. The qty-2 bucket is **87 % of P1's historical edge**. So the
   `DaysToLoad = 365` fight paid off on the very first trade.
2. **It entered at 00:58 ET — outside RTH**, exactly as the 61.7 %-of-entries-outside-RTH profile
   predicts, and it validates the `CME US Index Futures ETH` 23-hour session template. An RTH
   template would have deleted this trade entirely.

XM remains flat and correctly so — it cannot act before 09:45 ET by construction.

⚠️ **The book is now POSITIONED.** *Never restart while positioned* is load-bearing here: every stop
in this book is synthetic and dies with the strategy. Monday's planned 17:00–18:00 restart is still
safe because both legs are structurally flat at session end — but verify flat before touching
anything, every time.

`WeeklyEdgeBookM11_v1.cs` was restored to `bin/Custom/Strategies/` at 01:06 on owner request
(recompiled 01:06:34); the live book was verified unaffected. See `OQ6_MAPPING_PACKET.md` for why
the **two-leg sum, not that class**, is the authoritative M_11.
---

## 🟢 FIRST LIVE ROUND TRIP CLOSED — 2026-08-31 03:51 ET, **+$3,210 gross**

| | |
|---|---|
| entry | `581992641240` — 08-31 **00:58:00 ET**, Buy **2** NQU6 @ **29,421.00**, signal `L` |
| exit | `581992641251` — 08-31 **03:51:00 ET**, Sell 2 @ **29,501.25**, signal `XL`, `fromEntrySignal=L` |
| P&L | **+80.25 pts × 2 × $20 = +$3,210.00 gross**; ~$8.72 commission ⇒ **≈ +$3,201 net** |
| hold | 2 h 53 m | 
| flags | both orders `isBacktestOrder: false`; strategy `net_profit_currency` 70,585 → **73,795** |

Exit signal is `XL`, i.e. **the vote fell below the exit threshold** — the engine's own alpha exit,
not the `XLsess` session-box lockout and not a forced flat. The full intended lifecycle ran.

**Two operational arguments were confirmed by the very first trade:**
1. **It sized 2 contracts** — reachable only because the 250-entry quality window was warm. A
   default-warm-up deployment takes 1. This is the `DaysToLoad = 365` fight, paid off immediately.
2. **Entry 00:58 and exit 03:51 — entirely outside RTH.** An RTH session template would have deleted
   this trade completely. This is the `CME US Index Futures ETH` 23-hour template, paid off immediately.

⚠️ **One trade is not evidence about the edge.** It is evidence that the plumbing is correct.