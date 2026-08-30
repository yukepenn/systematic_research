# PAPER DEPLOYMENT RECORD — {P1/PCT + XM_v2} @ M_11 on DEMO8383477

**Deployed 2026-08-30 ~06:16 ET** under the owner instruction recorded in
`OWNER_DECISION_20260830.md`. **Paper account only. LIVE (real money) ENABLED = NO.**

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