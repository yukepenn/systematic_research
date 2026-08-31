# CURRENT_LIVE_TRUTH — 2026-08-31 15:05 ET

**Paper account `DEMO8383477`. LIVE real money = NO. $0 spent. No order placed by GENESIS III.**

This file is the **authoritative live-state document**. The previous version (2026-08-31 10:31 ET)
named `WeeklyEdgeP1PCT_v2` / `dep_8307c94764fd` and `WeeklyEdgeXMConflict_v3` / `dep_51bf1a7382cb`;
the machine now reports both of those as `strategy_not_in_account_collection` — **they no longer
exist.** Campaign context and the full open-state record live in
`research/operational/GENESIS_III_OPEN_STATE.md`.

---

## THE BOOK — verified from the machine, not asserted

| leg | class | deployment_id | strategy_id | state |
|---|---|---|---|---|
| P1 | `WeeklyEdgeP1PCT_v3` | `dep_9c51536a7045` | **399562877** | Realtime, **flat**, 0 active orders |
| XM | `WeeklyEdgeXMConflict_v4` | `dep_27ff47e7e3b7` | **399562878** | Realtime, **flat**, 0 active orders |

`NQ 09-26`, 1-min, `CME US Index Futures ETH`, `DaysToLoad = 365`.
Source `sha256`, NT8 working copy **identical** to the repo copy:

```
WeeklyEdgeP1PCT_v3.cs      a9ccc2331d78aea43b1eefeff24189d0277a4cdfb718f2b817f56f7ef60f6be6
WeeklyEdgeXMConflict_v4.cs 0360f894724cfd1fe59eb2a3a14d434b6e8a082eb2f25ba483e97ff2b854bae8
```

**Every certified parameter is still its `SetDefaults` value. `INCUMBENT CHANGE: NONE`.**

Stale registry rows that are **not** running: `dep_8307c94764fd`, `dep_51bf1a7382cb`,
`dep_55403f7de5f5`. They are records, not objects.

### ⚠️ A ~2-hour window in which the book was NOT M_11

Between **2026-08-31 16:28 and 18:25 UTC** a **second** `WeeklyEdgeP1PCT_v3` (`399562876`) was also
Realtime on the same account and instrument — the book ran at **P1 ×2 + XM ×1**. Worse, only one
export writer can hold the file, so the duplicate **traded without logging**. It was removed after
owner authorisation; both legs were flat throughout and `trade_count = 0` on both P1 instances, so
nothing was lost. **Any P1 observation inside that window is `FORWARD_OPERATIONAL_ONLY`.**

**Operational lesson, and it cost two blocked tool calls to learn:**
`DisableStrategy(strategyId=…)` returned `strategy_not_found` **while `GetDeployedStrategyState` was
simultaneously reporting that same id as `Realtime, is_trading`.** The two tools use different id
spaces. **For an MCP-deployed strategy the call that works is `StopStrategy(deployment_id=…)`.**

## 🔴 ROLL GUARD — read from the machine

```
P1  ROLL-PLAN blockNewEntriesFrom=2026-09-08  earliestStoredRollover=2026-09-16
XM  ROLL-PLAN blockNewEntriesFrom=2026-09-06  earliestStoredRollover=2026-09-14
```

**Both in the future — neither leg is latched dead.** The guard **latches**: re-enabling inside the
window blocks new entries *permanently* while every health check still reports green.

> **Red zone 2026-09-06 → 2026-09-18. Safe re-enable: P1 ≥ 2026-09-17, XM ≥ 2026-09-19**, on
> `NQ 12-26`, all four XM series moved together, `DaysToLoad = 365`,
> `ExpectInstrument = "NQ 12-26"`.

## INSTRUMENTATION

| path | state |
|---|---|
| `C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv` | live, current to the minute, 353,937 rows |
| `C:\NT8_ForwardLogs\export\we_xm_xm2.csv` | live, current to the minute, 353,936 rows |
| `C:\NT8_ForwardLogs\diag\` | **empty — expected**, see below |
| `C:\NT8_ForwardLogs\warmup\` | 3 certificates from today's redeploys |
| `C:` free space | 23 GB — **monitor**, `NumberRestartAttempts = 4` can trigger repeated warm-ups |

⭐ **The export is not realtime-scoped.** It contains the whole `DaysToLoad = 365` warm-up replay —
353,937 rows of the executable's own per-bar internal state. That is the substrate
`G3_EXECTRUTH_01/02` consume, and nobody had recorded it existed.

⚠️ **`diag/` is empty for a mundane reason**: `HdDiagRow` and `HdXmAgeRow` are `State.Realtime`-gated
and every deployment so far began **after** 09:31 ET, so XM's anchor/decision blocks have never once
executed in Realtime. **The first live observation of the cross-market staleness margins is
2026-09-01 at 09:31 ET.**

## 🔴 WHAT FORWARD OBSERVATIONS ON THIS ACCOUNT ARE WORTH

`G3_FEEDSEM_01` decoded `Provider31`: it is **Tradovate**, and `DEMO8383477` is a **server-side**
demo account, not local Sim101.

| | verdict |
|---|---|
| market data | ✅ **REAL** live CME L1 |
| order fill | ⚠️ **broker-side simulated** |
| slippage / fill quality | ⛔ **`SIMULATED_FILL_NON_EVIDENTIAL`** |

Decisive: across 5,156 NQU6 BBO samples the top of book has median size **2**, max bid **46**, max
ask **20** — and a 100-lot market order filled `lastQty=100, lastPx=avgPx=29577.25`, one fill at one
price. **P(top of book ≥ 100) = 0.00%.**

> **Decisions stay `FORWARD_DECISION_FIRST`** — real data, genuinely prospective.
> **Fills, fill prices, slippage and P&L are zero-information about real execution.** Not
> low-power — zero. 500 more paper fills give 500 observations of the engine, not of the market.

## STANDING CONSTRAINTS

- 🔴 **Do not re-enable either leg inside 2026-09-06 → 2026-09-18.**
- **Never restart while positioned** — every stop in this book is synthetic and dies with the strategy.
- **Never hot-edit a production object.** Every alternative is a new named challenger.
- Capital plan: **$75–90k**. `$21,740` and `$45,000` stay **retired as capital figures**.
  Separately, M_11's realised max drawdown is **$45,138**, and 100% of it is one 12-week episode
  (2022-W05 → 2022-W17) that earlier windows excluded — see `runs/G3_INCUMBENT_BASELINE_00_20260831`.
- No real-money order without an explicit recorded owner instruction.

## TWO FORWARD CLOCKS — neither is rewritten

| clock | value |
|---|---|
| `OWNER_FORWARD_START` | 2026-08-30 18:00 ET |
| `LEGACY_FORMAL_SHADOW_START` | 2026-09-01 18:00 ET (`shadow_runner.py:34`) |

## NEXT SESSION CHECKLIST (2026-09-01)

1. Confirm exactly **two** strategies on `DEMO8383477`, both Realtime, and the account flat at open.
2. After 09:46 ET read `C:\NT8_ForwardLogs\diag\` for XM's `ANCHOR` / `DECISION` rows and record
   `ESAgeMin` / `RTYAgeMin` / `YMAgeMin` — the **first ever live check** of the staleness guard.
3. Confirm both ledgers are still advancing and `C:` free space is still comfortable.
4. `research_sdk/live_readiness_check.py` R1–R8, and `shadow_runner.py` begins its hash chain at
   18:00 ET.
