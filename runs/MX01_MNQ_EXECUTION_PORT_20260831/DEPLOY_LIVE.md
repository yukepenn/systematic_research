# DEPLOY_LIVE — the exact live-account step, for the owner to run

**Status: NOT RUN. The live account `2047681` has zero deployments and is flat with $10,206.86.**

Everything below is verified and ready. Enabling real-money orders is an owner action; this agent
prepares it and does not perform it. Nothing here executes until you run it.

---

## BEFORE YOU RUN IT — three decisions, in order of how much they matter

### 1. `MnqPerNq` — the size

| value | exposure | 0.30-scaled maxDD | as % of $10,206.86 |
|---:|---|---:|---:|
| 1 | 0.10 NQ-eq | $5,189 | 50.8 % |
| 2 | 0.20 NQ-eq | $10,378 | 101.7 % |
| **3** | **0.30 NQ-eq** | **$15,567** | 🔴 **152.5 %** |

3 is what you asked for and it is what the parameters below say. The arithmetic says a repeat of
M_11's **own already-observed** worst episode (2022-W05 → 2022-W17) ends the account at 3, and very
nearly ends it at 2. Changing the number is a one-word edit below — no rebuild, no recompile, and
gates G1–G6 hold for any value.

### 2. The roll red zone — `2026-09-06 → 2026-09-18`

Deploying **now** is fine. What is not fine is **re-enabling inside the window**: the fail-safe
latches and blocks new entries *permanently* while every health check still reports green.

> Safe re-enable: **P1 ≥ 2026-09-17, XM ≥ 2026-09-19**, on `NQ 12-26` **and** `MNQ 12-26`, all
> series moved together, `ExpectInstrument = "NQ 12-26"`, `ExpectMnq = "MNQ 12-26"`.

The `MxInstrumentGuard` cross-series clause hard-halts if the decision contract and the execution
contract are ever on different months, so a partial roll fails loudly rather than silently trading
the wrong pair.

### 3. Log directories

Use `C:\NT8_ForwardLogs\live_mnq\` — **not** `\export\` (the live NQ paper book holds that handle)
and **not** `\mnq\` (the paper MNQ book holds that one). A collision makes the second `StreamWriter`
throw into a silent catch, and the leg then runs with **no ledger and no diagnostics at all**.

```powershell
mkdir C:\NT8_ForwardLogs\live_mnq\export
mkdir C:\NT8_ForwardLogs\live_mnq\diag
mkdir C:\NT8_ForwardLogs\live_mnq\warmup
```

---

## THE TWO CALLS

Deploy P1 first, confirm it reaches `Realtime` and `flat`, then deploy XM.

```
DeployStrategy(
  account        = "2047681",
  strategy_class = "WeeklyEdgeP1PCTMnq_v1",
  instrument     = "NQ 09-26",
  period_type    = "Minute",
  period         = 1,
  parameters = {
    "DaysToLoad":       365,
    "ExportDir":        "C:\\NT8_ForwardLogs\\live_mnq\\export",
    "DiagDir":          "C:\\NT8_ForwardLogs\\live_mnq\\diag",
    "WarmupCertDir":    "C:\\NT8_ForwardLogs\\live_mnq\\warmup",
    "ExpectInstrument": "NQ 09-26",
    "MnqInstrument":    "MNQ 09-26",
    "MnqPerNq":         3,
    "ExpectMnq":        "MNQ 09-26"
  })
```

```
DeployStrategy(
  account        = "2047681",
  strategy_class = "WeeklyEdgeXMConflictMnq_v1",
  instrument     = "NQ 09-26",
  period_type    = "Minute",
  period         = 1,
  parameters = {
    "DaysToLoad":    365,
    "ExportDir":     "C:\\NT8_ForwardLogs\\live_mnq\\export",
    "DiagDir":       "C:\\NT8_ForwardLogs\\live_mnq\\diag",
    "WarmupCertDir": "C:\\NT8_ForwardLogs\\live_mnq\\warmup",
    "EsInstrument":  "ES 09-26",
    "RtyInstrument": "RTY 09-26",
    "YmInstrument":  "YM 09-26",
    "MnqInstrument": "MNQ 09-26",
    "MnqPerNq":      3,
    "ExpectMnq":     "MNQ 09-26"
  })
```

**`DaysToLoad = 365` is not optional.** Convergence was measured at ~9 months; P1's binding warm-up
gate (`qual_entries`) is **event-driven**, not calendar-driven — it counts entries, so no amount of
calendar warm-up guarantees it and it must be read from the certificate.

---

## ACCEPTANCE CHECKS — run these, do not assume

1. `GetDeployedStrategyState(deployment_id)` on each leg → `state = "Realtime"`, `is_trading = true`,
   `position.market_position = "Flat"`, `active_order_count = 0`.
2. Read the newest certificate in `C:\NT8_ForwardLogs\live_mnq\warmup\`. Require:
   - verdict **`GO`** on every row (`DEGRADED` or `NO-GO` means it is trading a different object)
   - `env,instrument,NQU6` and `env,exec_instrument,MNQU6` — **decision on NQ, fills on MNQ**
   - `env,mnq_per_nq,<the value you chose>`
   - XM only: `env,series_4_instrument,MNQU6` and `series_0..3` = NQU6/ESU6/RTYU6/YMU6
3. `ls C:\NT8_ForwardLogs\live_mnq\export\` → **two** files, both non-zero and advancing.
   If either is missing, the handle collided and that leg is running blind — stop it.
4. `ls C:\NT8_ForwardLogs\live_mnq\diag\` → any row containing `MXEXEC blocked=1` means the MNQ
   execution series is unavailable or stale and **entries are being refused**. Exits are never gated.
5. `GetAccount("2047681")` → confirm cash and that margin is what you expect once a position opens.

## 🔴 THE FIRST REAL FILL IS THE REAL TEST

`AssertLedgerMatchesStrategyPosition` is `State.Realtime`-gated, so **no backtest has ever exercised
it.** It is the guard that the unindexed-`Position` defect would have broken, and the fix
(`Positions[EXEC]`) is verified by compile, by code reading and by independent review — but not yet
by an actual fill.

**On the first entry, check the NT8 log for `RECONCILE-BREAK` or `PARTIAL-FILL`.** Neither should
appear. If either does, the leg has latched: entries stop, exits still work, and it needs a look
before it is re-enabled. The paper MNQ book (`dep_7d762d9965fe`, `dep_b2ce1f1a4d6f`) is running for
exactly this reason and will hit a real fill first if you let it.

## IF YOU NEED TO STOP IT

`StopStrategy(deployment_id = ...)` — **not** `DisableStrategy(strategyId = ...)`, which returns
`strategy_not_found` on an MCP-deployed strategy that `GetDeployedStrategyState` simultaneously
reports as `Realtime`. Different id spaces. This cost two blocked calls to learn once already.

**Never stop a leg while it holds a position** — every stop in this book is synthetic and dies with
the strategy.
