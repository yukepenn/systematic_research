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
