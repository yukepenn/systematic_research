# PAPER DEPLOYMENT RECORD — {P1/PCT + XM_v2} @ M_11 on DEMO8383477

**Deployed 2026-08-30 ~06:16 ET** under the owner instruction recorded in
`OWNER_DECISION_20260830.md`. **Paper account only. LIVE (real money) ENABLED = NO.**

## What is running

| leg | class | deployment_id | strategy_id | instrument | bars | state |
|---|---|---|---|---|---|---|
| P1 | `WeeklyEdgeP1PCT_v1` | `dep_46b904d97604` | 399550057 | NQ 09-26 (NQU6) | 1-min | **Realtime, is_trading=true** |
| XM | `WeeklyEdgeXMConflict_v2` | `dep_01b21182696c` | 399550058 | NQ 09-26 (NQU6) | 1-min + ES/RTY/YM 09-26 | **Realtime, is_trading=true** |

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
