# R2 — NT8 REALTIME ORDER / POSITION RECONCILIATION

Run: `G2_LIVE_HARDENING_20260830` · Author: R2 subagent · Date 2026-08-30
Scope: **research / documentation only.** No order placed, no strategy enabled, disabled or
redeployed, no certified file modified, no git invoked. `WeeklyEdgeP1PCT_v1.cs` and
`WeeklyEdgeXMConflict_v2.cs` were opened **read-only**.

Evidence tags: **VERIFIED(source)** = quoted from the cited NT8 help page, from reflection against
*this* install (NT8 8.1.8.1, CrossTrade add-on v1.13.9), or from a file on this machine.
**INFERRED(reasoning)** = my deduction from those facts. Web content is treated as data.

---

## 0. Why this matters — the measured defect in the two certified strategies

**VERIFIED(local grep, 2026-08-30).** Neither certified file contains any of the tokens
`OnOrderUpdate`, `OnExecutionUpdate`, `OnPositionUpdate`, `PositionAccount`, `Position.MarketPosition`,
`Position.Quantity`, `StartBehavior`, `RealtimeErrorHandling`, `ConnectionLossHandling`,
`DisconnectDelaySeconds`, `SetOrderQuantity`, `IsAdoptAccountPositionAware`, `TraceOrders`,
`StopTargetHandling`, `IgnoreOverfill`. Zero hits in both files. They therefore run entirely on
NT8 defaults and never read NT8's own position.

**VERIFIED(`WeeklyEdgeP1PCT_v1.cs` L260–276).** The ledger is advanced by *assumption*:

```csharp
// ---- 0. settle any order submitted on the previous bar; it filled at THIS open ----
if (pendingAct == ACT_EXIT)
{
    sessPnl += (Open[0] - myEntryPx) * Instrument.MasterInstrument.PointValue
             - CommissionRT;
    myQty = 0;
    if (UseSessionBox && (sessPnl <= -HaltDollars || sessPnl >= TargetDollars))
        sessStopped = true;
}
else if (pendingAct == ACT_ENTER)
{
    myEntryPx = Open[0]; myQty = pendingSize;
}
pendingAct = ACT_NONE;
```

**VERIFIED(`WeeklyEdgeXMConflict_v2.cs` L242–257).** Same shape, `realizedPnl` / `myPos` /
`Opens[NQ][0]`.

There is no branch for *not filled*. The consequences, all **INFERRED(from the code + the NT8
semantics documented below)**:

| Real-world event | What NT8 does | What the ledger does | Divergence |
|---|---|---|---|
| Order **Rejected** | `RealtimeErrorHandling.StopCancelClose` (default) stops the strategy, cancels, flattens | sets `myQty = pendingSize`, books P&L | ledger says LONG, account is FLAT and strategy is DISABLED |
| **Partial** fill (2 requested, 1 filled) | strategy position = 1 | `myQty = 2` | subsequent `ExitLong(2)` is reduced by the managed layer; `sessPnl` is booked on 2 |
| Order **Cancelled** by platform / session expiry | position unchanged | ledger flips anyway | permanent, silent, one-way drift |
| Fill price ≠ `Open[0]` (any real slippage) | real avg fill | `Open[0]` | `sessPnl` drifts → `HaltDollars` / `TargetDollars` session box latches at the wrong bar → *the research economics are not reproduced even when nothing goes wrong* |
| Managed-approach **internal rule** silently ignores the order | order never submitted | ledger flips | see §3.4 — NT8 logs only the *first* such violation |

The last row is the nastiest. **VERIFIED(Managed Approach page):** *"To prevent excessive logging
which could degrade performance, you will only be notified of the very first order which has
violated an order handling rule. Subsequent orders which violate a rule will not be notified
through the error log."*

**VERIFIED(`mcp__crosstrade__ListDeployedStrategies`, 2026-08-30).** Both are live and Flat right now:
`dep_306e11dfc8eb` = `WeeklyEdgeP1PCT_v1`, `dep_5a914d070687` = `WeeklyEdgeXMConflict_v2`, both
`DEMO8383477` / `NQ 09-26` / 1-Minute, both `state: Realtime`, `is_trading: true`,
`active_order_count: 0`, `position: Flat`. `ListPositions(DEMO8383477)` returns `[]`.
**Nothing in this report requires touching them.**

---

## 1. OnOrderUpdate vs OnExecutionUpdate

### 1.1 Exact signatures — VERIFIED(reflection, `NinjaTrader.NinjaScript.StrategyBase`, this install)

```csharp
protected void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
        int filled, double averageFillPrice, OrderState orderState, DateTime time,
        ErrorCode error, string comment)

protected void OnExecutionUpdate(Execution execution, string executionId, double price,
        int quantity, MarketPosition marketPosition, string orderId, DateTime time)

protected void OnPositionUpdate(Position position, double averagePrice, int quantity,
        MarketPosition marketPosition)

public  Order GetRealtimeOrder(Order historicalOrder)
public  void  CancelOrder(Order order)
```

### 1.2 Which fires when — VERIFIED

* `OnOrderUpdate` — **VERIFIED(onorderupdate.htm):** *"An event driven method which is called each
  time an order managed by a strategy changes state."* Fires on quantity / price / state change.
* `OnExecutionUpdate` — **VERIFIED(onexecutionupdate.htm):** *"called on an incoming execution of
  an order managed by a strategy"*; *"an order can generate multiple executions"*.
* Ordering — **VERIFIED(onorderupdate.htm):** *"OnExecutionUpdate() is always triggered after
  OnOrderUpdate()."* **VERIFIED(onexecutionupdate.htm code comment):** *"OnExecution() is called
  after OnOrderUpdate() which ensures your strategy has received the execution which is used for
  internal signal tracking."*
* `OnPositionUpdate` fires after `OnExecutionUpdate`. **VERIFIED(onpositionupdate.htm).**

### 1.3 Which is authoritative for FILLS — VERIFIED

**`OnExecutionUpdate`.** **VERIFIED(onorderupdate.htm):** *"If you want to drive your strategy logic
based on order fills you must use OnExecutionUpdate() instead."*

`OnOrderUpdate` is authoritative for **lifecycle / terminality / rejection reason** (it is the only
callback carrying `OrderState` and `ErrorCode`). Use both, for different jobs:

> **fills and fill prices → `OnExecutionUpdate`. Terminal state and error → `OnOrderUpdate`.**

### 1.4 The "assign order objects in OnOrderUpdate" rule — VERIFIED

**VERIFIED(onorderupdate.htm):** *"OnOrderUpdate() will run inside of order methods such as
EnterLong()... attempting to assign an order object outside of OnOrderUpdate() may not return as
soon as expected."*

**VERIFIED(advanced_order_handling.htm):** *"the assignment is not gauranteed to be complete if it
is referenced immediately after submitting."* [sic — vendor typo preserved]

Canonical shape — **VERIFIED(onorderupdate.htm, verbatim):**

```csharp
private Order entryOrder = null;

protected override void OnBarUpdate()
{
  if (entryOrder == null && Close[0] > Open[0])
      EnterLong("entryOrder");
}

protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
        int filled, double averageFillPrice, OrderState orderState, DateTime time,
        ErrorCode error, string nativeError)
{
  // check if the current order matches the orderName passed in "EnterLong"()
  // Assign entryOrder in OnOrderUpdate() to ensure the assignment occurs when expected.
  // This is more reliable than assigning Order objects in OnBarUpdate, as the assignment is not
  // guaranteed to be complete if it is referenced immediately after submitting
  if (order.Name == "entryOrder")
      entryOrder = order;

  if (entryOrder != null && entryOrder == order)
  {
      Print(order.ToString());
      if (order.OrderState == OrderState.Cancelled)
      {
          // Do something here
          entryOrder = null;
      }
  }
}
```

Two further rules:

* **Match by `order.Name` (signal name), never by `OrderId`.** **VERIFIED(order.htm):** *"The
  property `<Order>.OrderId` is NOT a unique value, since it can change throughout an order's
  lifetime"*.
* **`order.OrderState` (current) ≠ the `orderState` parameter (this particular update).**
  **VERIFIED(onorderupdate.htm, verbatim):**
  ```csharp
  Print("The most current order state is: " + order.OrderState);   // OrderState.PartFilled
  Print("This particular order update state is: " + orderState);   // OrderState.Working
  ```
  For a state machine, branch on `order.OrderState`. Log `orderState`.

### 1.5 Thread-safety / passed-by-value rule — VERIFIED

**VERIFIED(onexecutionupdate.htm):** *"It's best practice to only work with the passed by value
parameters."*
**VERIFIED(onpositionupdate.htm):** *"When using a NinjaScript strategy it is best practice to only
work with passed by value data from OnExecution. Instances of multiple fills at the same time for
the same instrument might result in an incorrect OnPositionUpdate, as sequence of events are not
guaranteed"* (called out for Rithmic and Interactive Brokers).
**VERIFIED(onexecutionupdate.htm, Example 2 comment):** *"Use execution.Name to identify the order,
so we are not using execution.Order, which may not be up to date if an ExecutionUpdate is seen
before an OrderUpdate in a partial fill"*.

**INFERRED:** these three statements together mean the *only* quantity you may trust inside
`OnExecutionUpdate` is `execution.Quantity` / `execution.Price` / `execution.Name`. Accumulate them
yourself. Do not read `Position.Quantity` from inside a fill callback.

### 1.6 Lifecycle states — VERIFIED(reflection, `NinjaTrader.Cbi.OrderState`, this install)

`Accepted, Cancelled, Filled, Initialized, PartFilled, CancelSubmitted, ChangeSubmitted, Submitted,
TriggerPending, Rejected, Working, CancelPending, ChangePending, Suspended, AcceptedByRisk, Unknown`

Note `Suspended` and `AcceptedByRisk` exist in the assembly and are **not** listed on the public
help page — do not write a `switch` that assumes 14 values.

**VERIFIED(order.htm):** *"In a historical backtest, orders will always reach a 'Working' state. In
real-time, some stop orders may only reach 'Accepted' state if they are simulated/held on a brokers
server"* — i.e. **`Working` is not a reliable live milestone.** Treat only
`Filled / Rejected / Cancelled` (and `PartFilled` + `Cancelled`) as terminal.

**VERIFIED(reflection, `NinjaTrader.Cbi.ErrorCode`):** `NoError, LogOnFailed, OrderRejected,
UnableToCancelOrder, UnableToChangeOrder, UnableToSubmitOrder, UserAbort, OrderRejectedByRisk,
LoginExpired, Panic`.

### 1.7 Historical → realtime transition — VERIFIED, and it applies to us

**VERIFIED(advanced_order_handling.htm):**
```csharp
if (entryOrder != null && entryOrder.IsBacktestOrder && State == State.Realtime)
    entryOrder = GetRealtimeOrder(entryOrder);
```
*"If you DO NOT update a historical order reference, and then attempt to cancel/change that order
after it has been submitted in real-time, your strategy will be disabled with a message similar to:
'Strategy has been disabled because it attempted to modify a historical order that has transitioned
to a live order.'"*

**VERIFIED(getrealtimeorder.htm):** returns `null` when no match exists (Filled / Cancelled /
Rejected / Unknown); call it **once** per order object, inside `OnOrderUpdate`.

**INFERRED:** both deployments load 365 days of history and cross `Historical → Realtime` at
startup, so any hardened build that *holds* an `Order` reference must include this guard.

---

## 2. Rejected / partially filled / platform-cancelled — detection and reaction

### 2.1 Detection

| Event | Detect | Where |
|---|---|---|
| Rejected | `order.OrderState == OrderState.Rejected`; `error` param = `ErrorCode.OrderRejected` or `OrderRejectedByRisk`; `comment` = broker text | `OnOrderUpdate` |
| Partially filled | `order.OrderState == OrderState.PartFilled`; cumulative `sum(execution.Quantity) < requested` | `OnExecutionUpdate` (quantity), `OnOrderUpdate` (state) |
| Partial **then** cancelled | `order.OrderState == OrderState.Cancelled && order.Filled > 0` | `OnOrderUpdate` |
| Cancelled, nothing filled | `order.OrderState == OrderState.Cancelled && order.Filled == 0` | `OnOrderUpdate` |
| Overfill | fill arrives after cancel was requested | see §2.4 |
| Silently ignored by the managed layer | **no callback at all** | only detectable by the §6 invariant check |

**VERIFIED(onexecutionupdate.htm)** — the documented partial-fill test, verbatim:
```csharp
if (execution.Order.OrderState == OrderState.Filled
 || execution.Order.OrderState == OrderState.PartFilled
 || (execution.Order.OrderState == OrderState.Cancelled && execution.Order.Filled > 0))
{
    sumFilled += execution.Quantity;   // "We sum the quantities of each execution making up the entry order"
}
```

### 2.2 Documented reaction to a rejection

**Platform-level (default, no code):** `RealtimeErrorHandling.StopCancelClose`.
**VERIFIED(realtimeerrorhandling.htm):** *"Defines the behavior of a strategy when a strategy
generated order is returned from the broker's server in a 'Rejected' state."* — stops execution,
cancels working orders, closes open positions.

**Strategy-level (only if you opt out of the default):**
**VERIFIED(realtimeerrorhandling.htm, verbatim):**
```csharp
protected override void OnStateChange()
{
  if (State == State.Configure)
    RealtimeErrorHandling = RealtimeErrorHandling.IgnoreAllErrors;
}

protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
        int filled, double averageFillPrice, OrderState orderState, DateTime time,
        ErrorCode error, string nativeError)
{
  // Assign stopLossOrder in OnOrderUpdate() to ensure the assignment occurs when expected.
  if (order.Name == "myStopLoss" && orderState == OrderState.Filled)
    stopLossOrder = order;

  if (stopLossOrder != null && stopLossOrder == order)
  {
    if (order.OrderState == OrderState.Rejected)
    {
        // Stop loss order was rejected !!!!
        // Do something about it here
    }
  }
}
```
**VERIFIED(realtimeerrorhandling.htm):** *"Setting this property value to IgnoreAllErrors can have
serious adverse affects on a running strategy unless you have programmed your own order rejection
handling in the OnOrderUpdate() method"*, and *"Advanced rejection handling requires experienced
programmers only."*

**INFERRED:** NT8's recommended reaction to a rejection *for a strategy that has not implemented its
own rejection handling* is precisely the default — stop, cancel, close. That is our case.

### 2.3 Documented reaction to a partial fill

**VERIFIED(managed_approach.htm):** *"the order quantity will be reduced as the strategy position
reduces"* — the managed layer auto-trims exit orders. It does **not** trim your private ledger.
**VERIFIED(onexecutionupdate.htm):** submit / size protective orders on `PartFilled` using
`execution.Order.Filled` and the running `sumFilled`; recompute the average entry price from the
executions (Example 2 keeps a `List<double>` of fill prices precisely because broker event ordering
is not guaranteed).

### 2.4 Overfill — VERIFIED(ignoreoverfill.htm)

*"An overfill is categorized as when an order returns a 'Filled' or 'PartFilled' state after the
order was already marked for cancellation."* Default `IgnoreOverfill = false` (NT8 handles it).
*"Setting this property value to true can have serious adverse affects on a running strategy unless
you have programmed your own overfill handling"*. **Recommendation: leave `false`.**

---

## 3. RealtimeErrorHandling

**VERIFIED(reflection, `NinjaTrader.NinjaScript.RealtimeErrorHandling`, this install) — 4 values,
not 3:**

| Value | Documented meaning | Source |
|---|---|---|
| `StopCancelClose` | **Default.** Stops the strategy, cancels working orders, closes open positions | VERIFIED(realtimeerrorhandling.htm) |
| `IgnoreAllErrors` | *"Ignores any order errors received by the strategy and will continue running"* | VERIFIED(realtimeerrorhandling.htm) |
| `StopCancelCloseIgnoreRejects` | Default behaviour for all errors **except** order rejections | VERIFIED(realtimeerrorhandling.htm) |
| `IgnoreAllErrorsNoAlert` | present in `NinjaTrader.Core` on this install; **not documented** on the help page | VERIFIED(reflection) / meaning INFERRED from the name — do not use |

**Where to set it — VERIFIED(realtimeerrorhandling.htm):** *"should ONLY be set from the
OnStateChange() method during State.SetDefaults or State.Configure."*

**Recommendation for our unattended strategies: `StopCancelClose`, declared explicitly.**
**INFERRED(reasoning):** it is already the effective value (neither file assigns it), but declaring
it makes the contract auditable and immune to a future edit of Tools → Options. `IgnoreAllErrors`
is only defensible once the §6 ledger reconciler exists *and* has been proven; today it would let a
rejected order silently poison `sessPnl` forever. `StopCancelCloseIgnoreRejects` is the worst of
both for us — it keeps running through exactly the event our ledger cannot survive.

⚠ **VERIFIED(this install's `Config.xml`):** `CancelEntriesOnStrategyDisable = false` and
`CancelExitsOnStrategyDisable = false`. **INFERRED:** a *manual* disable therefore leaves working
orders alive on `DEMO8383477`. `StopCancelClose` covers the rejection path but not the human path.
Flag for the owner; changing a global option is out of scope for this run.

---

## 4. ConnectionLossHandling

**VERIFIED(reflection, `NinjaTrader.NinjaScript.ConnectionLossHandling`):** exactly
`KeepRunning`, `Recalculate`, `StopStrategy`.

| Value | Documented meaning (VERIFIED, connectionlosshandling.htm) | What happens to *our* internal state (INFERRED) |
|---|---|---|
| `Recalculate` | **Default.** *"Strategies will attempt to recalculate its strategy position when a connection is reestablished."* | The strategy re-runs its historical path. Private fields (`myQty`, `myEntryPx`, `sessPnl`, `sessStopped`, `realizedPnl`, the `qDist*` quantile queues) are **rebuilt from the assumed-fill simulation**, discarding every real fill price observed before the drop. The session box silently resets to a synthetic value. **This is the single most dangerous default for us.** |
| `KeepRunning` | *"Keeps the strategy running. When the connection is reestablished the strategy will resume as if no disconnect occurred."* | Private state survives intact — but so does any drift accrued while blind. Orders submitted into a dead order feed may have been rejected unseen. |
| `StopStrategy` | *"Automatically stops the strategy when disconnected for more than DisconnectDelaySeconds. No action will be taken when a connection is reestablished."* | Strategy stops. State is frozen at the last good bar. Restart is an explicit decision, and the ledger can be reconciled against NT8 before it. |

**Trigger conditions — VERIFIED(connectionlosshandling.htm).** Recalculation applies only when the
strategy was stopped due to: a data-feed disconnect exceeding `DisconnectDelaySeconds`; an
order-feed disconnect while placing orders during the disconnection; or both feeds disconnected
beyond `DisconnectDelaySeconds`. *"If connection restores before stopping conditions are met, the
strategy continues without recalculating."*

**`DisconnectDelaySeconds` — VERIFIED(disconnectdelayseconds.htm):** *"the amount of time a
disconnect would have to last before connection loss handling takes action."* Default **10**.
Set in `State.SetDefaults`.

**`RestartOnConnectionLoss` — VERIFIED(reflection): NO SUCH NinjaScript PROPERTY EXISTS on
`StrategyBase` in NT8 8.1.8.1.** A search for `Restart` across all NinjaTrader assemblies returns
only two writable strategy properties:

```
NinjaTrader.NinjaScript.StrategyBase.NumberRestartAttempts : int
NinjaTrader.NinjaScript.StrategyBase.RestartsWithinMinutes : int
```

These are the NinjaScript surface of the UI's "Restart on connection loss" block.
**VERIFIED(this install's `Config.xml` → `StrategiesOptions`):** the machine-wide defaults in force
right now are `ConnectionLossHandling = Recalculate`, `DisconnectDelaySeconds = 10`,
`NumberRestartAttempts = 4`, `RestartsWithinMinutes = 5`.

**INFERRED:** with the defaults as shipped, a >10 s NQ feed hiccup can auto-restart our strategies
up to 4 times in 5 minutes, each restart re-running history and rewriting `sessPnl` from assumed
fills. That is a live-vs-research divergence mechanism nobody has budgeted for.

**Recommendation: `ConnectionLossHandling = ConnectionLossHandling.StopStrategy`,
`DisconnectDelaySeconds = 10`, `NumberRestartAttempts = 0`.** Restart becomes an owner decision, and
the ledger is reconcilable at that moment.

---

## 5. `Position` vs `PositionAccount` — and two strategies on one account

### 5.1 The three objects — VERIFIED(reflection, `StrategyBase`)

```
Position         : Position      (read-only)   // THIS strategy instance's virtual position
Positions        : Position[]    (read-only)   // per added data series
PositionAccount  : Position      (read-only)   // the real account position for this instrument
PositionsAccount : Position[]    (read-only)
```
Both are the same *type* (`NinjaTrader.Cbi.Position`) — the difference is only which book they
report. Nothing prevents you reading the wrong one; the compiler will not help.

* **VERIFIED(position.htm):** `Position` *"represents position related information that pertains to
  an instance of a strategy."*
* **VERIFIED(positionaccount.htm):** `PositionAccount` *"Represents position related information
  that pertains to real-world account (live or simulation)."*

### 5.2 Which one do we compare our ledger against?

**`Position` — the strategy position. Never `PositionAccount`.**

**VERIFIED(onpositionupdate.htm):** *"You will NOT receive position updates for manually placed
orders, or orders managed by other strategies"* — the per-strategy book is attributed to the
strategy instance and is exactly what our ledger is a mirror of.

**INFERRED(reasoning):** `myQty` in P1 is "how many contracts *this* signal owns". On
`DEMO8383477 / NQ 09-26`, `PositionAccount.Quantity` is the **net of P1 + XM + anything manual**.
If P1 is long 2 and XM is short 1, `PositionAccount` reads Long 1 and *neither* ledger matches it.
Comparing a per-strategy ledger to `PositionAccount` would produce a false break on every bar the
two legs disagree — which is, by construction, most of the time for a two-leg portfolio.

`PositionAccount` still belongs in the *log line* (it is the only view of aggregate exposure and
therefore of margin), but it must never gate a decision. This is the same
`EXECUTABLE_COMPONENT_SET` distinction CLAUDE.md §3 already draws, expressed at runtime.

### 5.3 How NT8 attributes positions per strategy — VERIFIED

Each enabled strategy instance keeps its own virtual position, fed only by its own executions.
**VERIFIED(`ListDeployedStrategies`, 2026-08-30):** NT8 reports a separate `position` and
`performance` block per `current_strategy_id` (`399550060` P1, `399550061` XM) on the one account.
**VERIFIED(order.htm):** *"The `Oco` property receives a suffix during historical-to-live
transitions to ensure uniqueness across strategies"* — NT8 explicitly namespaces OCO groups so two
strategies on one account+instrument do not collide.

### 5.4 Documented pitfalls for our exact configuration

* **VERIFIED(syncing_account_positions.htm):** *"Placing manual trades or running multiple
  strategies on the same instrument can also lead to your Account Position being out of sync from
  your Strategy Position."*
* **VERIFIED(syncing_account_positions.htm):** *"These options will only help you sync your Account
  Position to your Strategy Position once on startup. These options will not guarantee your Account
  Position remains in sync afterward."*
* **VERIFIED(syncing_account_positions.htm):** *"The reconciliatory market order is submitted
  outside of the strategy so your strategy will not be able to manage it from methods like
  OnOrderUpdate(), OnExecution(), etc."* — a synchronize order is **invisible** to our ledger.
* **VERIFIED(syncing_account_positions.htm), AdoptAccountPosition:** *"Only one strategy with this
  setting can be started at a time for an individual account and instrument"* and *"The account and
  instrument the strategy is started on must not have any working orders which were submitted
  outside of the strategy, or by another instance of the same strategy."*
* **VERIFIED(syncing_account_positions.htm):** the manual "Synchronize All Strategies" command
  aggregates strategy positions across all enabled strategies **not** set to "Wait until flat" and
  fires one market order. **INFERRED:** if either of our strategies is ever set to anything other
  than `WaitUntilFlat`, a stray right-click on the Strategies tab can fire a live market order on
  `DEMO8383477` that neither ledger will ever see.

**Bottom line for P1 + XM on `DEMO8383477 / NQ 09-26`:** any `*SynchronizeAccount` or
`AdoptAccountPosition` mode is disqualified — not by preference, by the documented one-strategy
restriction and by the fact that reconciliatory orders bypass our callbacks entirely.

---

## 6. StartBehavior

**VERIFIED(reflection, `NinjaTrader.NinjaScript.StartBehavior`):** `AdoptAccountPosition`,
`ImmediatelySubmit`, `ImmediatelySubmitSynchronizeAccount`, `WaitUntilFlat`,
`WaitUntilFlatSynchronizeAccount`. Default `WaitUntilFlat`
**VERIFIED(startbehavior.htm).**

| Value | Exact documented semantics — VERIFIED(syncing_account_positions.htm) | Verdict for us |
|---|---|---|
| **`WaitUntilFlat`** (default) | *"Least disruptive in terms of handling your current Account Position."* Cancels pre-existing orders the strategy generated; assumes sync only once **both** strategy and account reach flat. If the account is not flat when the strategy position reaches flat, they stay out of sync — but **no live order is sent to force it**. | ✅ **ADOPT.** The only mode that (a) inherits nothing, (b) submits no reconciliatory order, (c) leaves the other leg's position alone. |
| `WaitUntilFlatSynchronizeAccount` | Cancels pre-existing orders, then **submits reconciliatory market orders to flatten any non-flat Account Position** before proceeding. | ❌ Would flatten **XM's** position when P1 starts. Catastrophic for a two-leg component set. |
| `ImmediatelySubmit` | Begins executing immediately; cancels unmatched pre-existing orders, maps matching ones; **assumes** the two positions are already synchronized. *"Unsuitable if Account Position differs from Strategy Position."* | ❌ Assumes exactly the thing our ledger cannot guarantee. |
| `ImmediatelySubmitSynchronizeAccount` | As above **plus** market orders to force the account onto the strategy position. | ❌ Same fatal objection as row 2. |
| `AdoptAccountPosition` | *"disregard the historical virtual Strategy Position and to start in the same position as the real-world Account Position."* Requires `IsAdoptAccountPositionAware = true` **VERIFIED(startbehavior.htm + reflection: the property exists on `StrategyBase`)**. Cancels non-matching strategy orders (40 s confirmation window or the strategy will not start); maps matching ones; submits the remainder live; then syncs. **One strategy per account+instrument; no externally-submitted working orders allowed.** | ❌ **Disqualified twice over:** it is the definition of *inheriting a foreign position* (on a shared account, the "account position" contains XM's contracts), and only one strategy per account+instrument may use it. |

**Answer to "which is right for a strategy that must not inherit a foreign position":**
**`StartBehavior.WaitUntilFlat`, with `IsAdoptAccountPositionAware = false`.** It is already the
effective value — declare it so it cannot drift.

---

## 7. THE PATTERN WE MUST ADOPT

Written against P1's shape; XM is the same with `myPos * Qty` in place of `myQty`.
**These are code shapes for a NEW class** (`WeeklyEdgeP1PCT_v2` / `WeeklyEdgeXMConflict_v3`) —
CLAUDE.md §6 forbids renaming a parity-certified class and R2's hard rule 1 forbids editing the
certified files. The hardened build must be re-parity-certified against the certified decision
series before it replaces anything.

### 7.1 Reconciliation state

```csharp
// ---------- realtime reconciliation state ----------
private Order      workOrder     = null;                 // the single live order this signal owns
private int        workFilled    = 0;                    // cumulative executed qty (from executions)
private double     workAvgPx     = 0.0;                  // qty-weighted avg fill price (from executions)
private bool       workTerminal  = false;                // Filled / Rejected / Cancelled seen
private OrderState workState     = OrderState.Unknown;
private ErrorCode  workError     = ErrorCode.NoError;
private bool       reconcileHalt = false;                // one-way latch: ledger no longer trustworthy

private static bool IsMine(string n)   // every signal name this strategy submits
{ return n == "L" || n == "XL" || n == "XLsess"; }

private void ResetWork()
{ workOrder = null; workFilled = 0; workAvgPx = 0.0; workTerminal = false;
  workState = OrderState.Unknown; workError = ErrorCode.NoError; }
```

### 7.2 `OnOrderUpdate` — ownership, transition, terminality

```csharp
protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
        int filled, double averageFillPrice, OrderState orderState, DateTime time,
        ErrorCode error, string comment)
{
    if (order == null || !IsMine(order.Name)) return;      // match by NAME; OrderId is not stable

    // (1) assign HERE, never in OnBarUpdate  [onorderupdate.htm]
    workOrder = order;

    // (2) historical -> realtime, exactly once  [advanced_order_handling.htm]
    if (workOrder.IsBacktestOrder && State == State.Realtime)
    {
        Order rt = GetRealtimeOrder(workOrder);
        if (rt != null) workOrder = rt;
    }

    // (3) branch on order.OrderState (current), LOG orderState (this update)
    workState = order.OrderState;
    workError = error;

    if (order.OrderState == OrderState.Rejected)
    {
        reconcileHalt = true; workTerminal = true;
        Print(string.Format("[{0}] REJECT name={1} err={2} comment={3}", Time[0], order.Name, error, comment));
    }
    else if (order.OrderState == OrderState.Cancelled)
    {
        workTerminal = true;                                // order.Filled may be 0 OR partial
        Print(string.Format("[{0}] CANCELLED name={1} filled={2}", Time[0], order.Name, order.Filled));
    }
    else if (order.OrderState == OrderState.Filled)
    {
        workTerminal = true;
    }
    // Working / Accepted / PartFilled / Suspended / AcceptedByRisk: not terminal, do nothing.
}
```

### 7.3 `OnExecutionUpdate` — the only source of fill truth

```csharp
protected override void OnExecutionUpdate(Execution execution, string executionId, double price,
        int quantity, MarketPosition marketPosition, string orderId, DateTime time)
{
    // execution.Name, NOT execution.Order — execution can arrive before the order update on a
    // partial fill  [onexecutionupdate.htm Example 2]
    if (execution == null || !IsMine(execution.Name)) return;

    // passed-by-value only  [onexecutionupdate.htm / onpositionupdate.htm]
    int    q = execution.Quantity;
    double p = execution.Price;

    workAvgPx  = (workFilled + q) > 0 ? (workAvgPx * workFilled + p * q) / (workFilled + q) : 0.0;
    workFilled += q;
}
```

### 7.4 Settlement — replaces "it filled at THIS open"

```csharp
// call at the top of OnBarUpdate, where the old block was
private void SettlePending()
{
    if (pendingAct == ACT_NONE) return;

    // (a) still working across a bar boundary: research assumed an instantaneous next-open fill
    //     and live did not deliver one. Do not guess — latch.
    if (!workTerminal) { reconcileHalt = true; return; }

    if (pendingAct == ACT_ENTER)
    {
        if (workFilled == 0)                        // rejected, or cancelled with nothing done
        { pendingAct = ACT_NONE; ResetWork(); return; }   // LEDGER UNCHANGED — still flat
        myEntryPx = workAvgPx;                      // REAL average fill, never Open[0]
        myQty     = workFilled;                     // honours a partial fill
        if (workFilled != pendingSize) reconcileHalt = true;   // partial: research had no such state
    }
    else if (pendingAct == ACT_EXIT)
    {
        if (workFilled == 0)
        { pendingAct = ACT_NONE; ResetWork(); return; }   // LEDGER UNCHANGED — still in the trade
        sessPnl += (workAvgPx - myEntryPx) * Instrument.MasterInstrument.PointValue * workFilled / myQty
                 - CommissionRT;                    // keep the W98 per-contract box convention
        myQty -= workFilled;
        if (myQty != 0) reconcileHalt = true;       // partial exit leaves a residue
        if (UseSessionBox && (sessPnl <= -HaltDollars || sessPnl >= TargetDollars)) sessStopped = true;
    }
    pendingAct = ACT_NONE; ResetWork();
}
```
⚠ The `* workFilled / myQty` term reproduces the certified per-contract box only for the full-fill
case. **A partial fill has no defined research semantics** — that is why it also latches
`reconcileHalt`. Do not invent one; record it and stop.

### 7.5 The invariant — one line that would have caught every failure above

```csharp
private void AssertLedgerMatchesStrategyPosition()
{
    int nt8  = (Position.MarketPosition == MarketPosition.Long)  ?  Position.Quantity
             : (Position.MarketPosition == MarketPosition.Short) ? -Position.Quantity : 0;
    int mine = myQty;                       // P1 long-only. XM: myPos * Qty
    if (nt8 != mine)
    {
        reconcileHalt = true;
        Print(string.Format("[{0}] RECONCILE-BREAK ledger={1} strategyPosition={2} accountPosition={3}({4})",
              Time[0], mine, nt8,
              PositionAccount.Quantity, PositionAccount.MarketPosition));
    }
}
```
Compare against **`Position`**. Log `PositionAccount` — never gate on it (§5.2).
Call it once per bar, **after** `SettlePending()` and **before** any new submission.

### 7.6 The gate

```csharp
// no new risk is taken while the ledger is not provably equal to NT8's book
if (reconcileHalt)
{
    if (myQty > 0) { ExitLong(myQty, "XL_RECON", "L"); pendingAct = ACT_EXIT; }
    return;                                   // submit nothing else, ever, this session
}
```
**INFERRED:** flatten-then-stop is the conservative reaction and mirrors what
`RealtimeErrorHandling.StopCancelClose` does at the platform level. The alternative — latch and hold
— is defensible only if the owner wants the position kept. **This is an owner decision, not mine.**

### 7.7 `OnPositionUpdate` — optional, log-only

```csharp
protected override void OnPositionUpdate(Position position, double averagePrice, int quantity,
        MarketPosition marketPosition)
{
    Print(string.Format("[{0}] POS {1} {2} @ {3}", Time[0], marketPosition, quantity, averagePrice));
}
```
**VERIFIED(onpositionupdate.htm):** event ordering is not guaranteed on simultaneous fills for some
providers. Use it for the audit trail only; never drive logic from it.

---

## 8. PROPERTY SETTINGS TO DECLARE

Add to `State.SetDefaults` of the hardened classes. Every one is currently **absent** from both
certified files, so each is a real change of contract even where it equals the NT8 default —
declaring it removes the dependency on Tools → Options.

```csharp
// ---- realtime hardening -------------------------------------------------
RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;   // NT8 default, made explicit
ConnectionLossHandling      = ConnectionLossHandling.StopStrategy;     // CHANGE from Recalculate
DisconnectDelaySeconds      = 10;                                      // install default, explicit
NumberRestartAttempts       = 0;                                       // CHANGE from 4
RestartsWithinMinutes       = 0;                                       // CHANGE from 5
StartBehavior               = StartBehavior.WaitUntilFlat;             // NT8 default, made explicit
IsAdoptAccountPositionAware = false;                                   // explicit refusal to inherit
SetOrderQuantity            = SetOrderQuantity.Strategy;               // sizing stays in the strategy
IsUnmanaged                 = false;                                   // managed approach retained
IgnoreOverfill              = false;                                   // NT8 handles overfills
TraceOrders                 = true;                                    // paper/DEMO only
```

| Property | Value | Default | Status | Why |
|---|---|---|---|---|
| `RealtimeErrorHandling` | `StopCancelClose` | same | no behaviour change | Only safe value until §7 is proven. VERIFIED(realtimeerrorhandling.htm) |
| `ConnectionLossHandling` | `StopStrategy` | `Recalculate` | **behaviour change** | `Recalculate` rebuilds `sessPnl` from assumed fills. INFERRED §4 |
| `DisconnectDelaySeconds` | `10` | `10` | no change | VERIFIED(disconnectdelayseconds.htm) |
| `NumberRestartAttempts` / `RestartsWithinMinutes` | `0` / `0` | `4` / `5` (this install) | **behaviour change** | Auto-restart re-runs history and rewrites the session box. INFERRED §4 |
| `StartBehavior` | `WaitUntilFlat` | same | no change | Only mode that inherits nothing and sends no reconciliatory order. VERIFIED §6 |
| `IsAdoptAccountPositionAware` | `false` | `false` | no change | Makes `AdoptAccountPosition` inoperable by construction. VERIFIED(startbehavior.htm) |
| `SetOrderQuantity` | `Strategy` | `Strategy` | no change | VERIFIED(setorderquantity.htm) |
| `IsUnmanaged` | `false` | `false` | no change | Do not mix approaches. VERIFIED(GetNinjaScriptHelp feature_matrix) |
| `IgnoreOverfill` | `false` | `false` | no change | VERIFIED(ignoreoverfill.htm) |
| `TraceOrders` | `true` | `false` | **new output** | Order lifecycle to the Output window; the audit trail for the first live break. Reconsider for production. |

**VERIFIED(realtimeerrorhandling.htm, setorderquantity.htm, ignoreoverfill.htm):** these must be set
in `State.SetDefaults` or `State.Configure` only.

⚠ **`RestartOnConnectionLoss` does not exist** as a NinjaScript property in NT8 8.1.8.1
(VERIFIED, reflection). Anyone writing it will get CS0103. Use `NumberRestartAttempts` /
`RestartsWithinMinutes`.

⚠ **INFERRED:** `mcp__crosstrade__DeployStrategy`'s `parameters` map is reflected onto public
properties after `SetState(SetDefaults)`. All eleven above are public read/write on `StrategyBase`,
so they *could* be injected at deploy time — **but that is untested and the docs restrict assignment
to `SetDefaults`/`Configure`.** Declare them in the `.cs`. Do not rely on the deploy map.

---

## 9. Owner-gated items (recorded, not acted on)

1. `CancelEntriesOnStrategyDisable=false` / `CancelExitsOnStrategyDisable=false` in `Config.xml` —
   a manual disable leaves working orders alive. Global option; owner decision.
2. `Synchronize All Strategies` (right-click, Strategies tab) fires a live market order on
   `DEMO8383477`. Neither ledger would see it. Operational hazard; brief the owner.
3. Flatten-vs-hold on `reconcileHalt` (§7.6) is an owner decision.
4. The hardened classes must be **re-parity-certified** (CLAUDE.md §6 bands: decision agreement
   ≥99 %, trade counts within 2 %) before they replace anything. Adding callbacks does not change
   the decision series in backtest — but that is a claim to be *measured*, not asserted.

---

## 10. Sources

All NT8 pages served from `ninjatrader.com/support/helpGuides/nt8/…` (301 → `ninjatrader-live.ninjatrader.com`):

- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/onorderupdate.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/onexecutionupdate.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/onpositionupdate.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/realtimeerrorhandling.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/connectionlosshandling.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/disconnectdelayseconds.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/startbehavior.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/syncing_account_positions.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/position.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/positionaccount.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/order.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/advanced_order_handling.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/getrealtimeorder.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/managed_approach.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/setorderquantity.htm
- https://ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/ignoreoverfill.htm

Pages returning HTTP 500 on this vendor host (not consulted): `orderstate.htm`,
`restartonconnectionloss.htm`, `strategy_properties.htm`, `strategies.htm`, `account.htm`,
`strategy_position_vs_account_position.htm`. Enumerations for those topics were obtained by
reflection instead, which is stronger evidence for *this* install.

Local / live evidence:
- Reflection via `mcp__crosstrade__LookupNinjaScriptSymbol` / `SearchNinjaScriptSymbols`
  (NT8 8.1.8.1, add-on v1.13.9): `StrategyBase`, `ConnectionLossHandling`, `RealtimeErrorHandling`,
  `StartBehavior`, `Cbi.OrderState`, `Cbi.ErrorCode`.
- `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\Config.xml` → `<StrategiesOptions>`.
- `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\WeeklyEdgeP1PCT_v1.cs` (read-only).
- `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\WeeklyEdgeXMConflict_v2.cs` (read-only).
- `mcp__crosstrade__ListDeployedStrategies`, `mcp__crosstrade__ListPositions` (2026-08-30).
