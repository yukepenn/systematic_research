# HARDENING SPEC — `WeeklyEdgeP1PCT_v2` and `WeeklyEdgeXMConflict_v3`

**Run** `G2_LIVE_HARDENING_20260830` · **Role** HARDENING ARCHITECT · **Written** 2026-08-30
**Inputs read:** `R1_ROLLOVER.md`, `R2_REALTIME.md`, `R3_DIVERGENCE.md`, `R4_WARMUP.md`,
`R5_PERSISTENCE_PROBE.md`, `research/operational/NT8_RUNBOOK.md`,
`runs/G2_NT8_OPS_20260830/STRATEGY_AUDIT.md`, and both certified sources
(`WeeklyEdgeP1PCT_v1.cs`, `WeeklyEdgeXMConflict_v2.cs`) — **read-only, not modified**.

**Compliance:** no git. No order, enable, disable, deploy, stop, flatten or account action. The two
running paper deployments (`dep_306e11dfc8eb`, `dep_5a914d070687`) were **not touched** and are not
touched by anything in this plan. Only read-only reflection (`LookupNinjaScriptSymbol`,
`SearchNinjaScriptSymbols`) was called. This document is the only file written.

Every claim is tagged **VERIFIED(source)** or **INFERRED(reasoning)**. Web content is treated as
data; URLs are cited in §8.

---

# 0. THE GOVERNING CONSTRAINT

> ## Every hardening in these two classes must be **INERT IN A STRATEGY ANALYZER BACKTEST**, so that
> ## the new class's backtest is **TRADE-FOR-TRADE IDENTICAL** to the certified class over the full
> ## certified window. **That row-identity is the proof that no trading logic changed.**

Corollaries, binding on the builder:

1. **The bar is identity, not the parity band.** CLAUDE.md §6's `≥99 %` decision agreement / `2 %`
   trade-count band describes *a different object being compared to a reference*. Here the two
   objects are meant to be **the same object**. The acceptance bar is **100.000 %, zero differing
   rows, zero differing trades, zero differing dollars.** A 99.9 % result is a **FAIL** and means a
   hardening item leaked into the decision path; find it and remove it. Do not "explain" a mismatch.
2. **Anything that would alter historical behaviour is not allowed in these classes.** If it is
   important, it is listed in §6 *"requires re-certification, not in scope"* — including several
   items R2 and R4 proposed in good faith that do not survive this constraint (§6 RC-01, RC-02).
3. **The certified decision stack is copied byte-for-byte.** No reformatting, no "tidying", no
   renamed locals, no reordered statements inside `OnBarUpdate`. The hardened file is the certified
   file **plus** additions, at the insertion points named in §3.
4. **Exits are never gated.** Every gate in this document blocks *new entries only*. A strategy that
   refuses to close is a worse failure than the one being prevented (R4 §1.2).
5. **Nothing self-corrects.** On any detected divergence the classes **halt new entries and log
   loudly**. They never silently rewrite the ledger to match reality, and never rewrite reality to
   match the ledger.

## 0.1 The four inertness mechanisms — and which one each item uses

Every item in §3 must name one of these. Nothing else counts as a proof of inertness.

| # | Mechanism | Why it is inert | Evidence |
|---|---|---|---|
| **M1** | **`State == State.Realtime` gate.** The code path is entered only when `State` is `Realtime`. | A Strategy Analyzer backtest never leaves `State.Historical`; `Transition (6)` and `Realtime (7)` are reached only by a strategy enabled on an account, *after* historical processing completes. | VERIFIED(onstatechange.htm: `Transition` is *"called once as the object has finished processing historical data but before it starts to process realtime data"*; R4 claim 8 — live probe returns `"State": 7` ⇄ `"Realtime"` on the enabled deployment) + **INFERRED** for the Analyzer, which is why **V2c** below makes it a falsifier rather than an assumption |
| **M2** | **Event that never fires in backtest.** The handler exists but no such event is generated historically (order rejection, broker cancel, connection loss, restart). | Historical orders in the Analyzer always reach `Working` and then fill deterministically at the next bar's open; no broker exists to reject, cancel or disconnect. | VERIFIED(order.htm: *"In a historical backtest, orders will always reach a 'Working' state"*; R3 §3.1) |
| **M3** | **Platform property with realtime-only semantics.** Declaring it changes nothing historically because the platform only consults it in a live/paper session. | `RealtimeErrorHandling`, `ConnectionLossHandling`, `DisconnectDelaySeconds`, `NumberRestartAttempts`, `RestartsWithinMinutes`, `StartBehavior` are all defined in terms of broker rejections, connection loss and strategy start on an **account**. | VERIFIED(realtimeerrorhandling.htm, connectionlosshandling.htm, disconnectdelayseconds.htm, startbehavior.htm) — see the ⚠ on `StartBehavior` and `SetOrderQuantity` in §4 |
| **M4** | **Condition that is provably false for the certified parameter set over the certified window.** The branch exists and is not state-gated, but it cannot be reached with the certified inputs. | Used only where M1–M3 do not apply: the instrument-month guard (HD-05) and the configuration self-assertion (HD-11). Inertness is **conditional on the certified parameters** and is discharged by V2 (identity) plus V3 (a negative test that proves the branch *can* fire). | INFERRED, verified by test |

**M1 is the workhorse.** Prefer it. Use M4 only where a guard's whole purpose is to be checked at
configuration time.

## 0.2 The inversion rule (why R4's warm-up design had to be flipped)

R4 §1.3 arms at `State.Transition` and gates entries on `armed`. In a Strategy Analyzer backtest
`State.Transition` **never occurs**, so `armed` would stay `false` and the identity run would produce
**zero trades**. R4 patched this with an operator-set `RequireWarmup = false`, which makes row-identity
depend on remembering a flag.

**Corrected design, binding here:** every gate flag defaults to **"not blocking"** and is only ever
*set* to blocking inside an M1 gate.

```csharp
private bool haltEntries = false;         // default: NOT blocking. Only ever set true under M1.
private bool EntriesAllowed()
{
    if (State != State.Realtime) return true;   // M1 — provably inert in any backtest
    return !haltEntries;
}
```

There is no `RequireWarmup` property and no operator flag anywhere in the entry path. In a backtest
the gate is a compile-time-visible no-op on every bar; in paper/live it is fully armed with no
configuration. **A hardening that can be defeated by forgetting a checkbox is not a hardening.**

---

# 1. THE OBJECTS

| | certified (READ-ONLY, never edited) | hardened (new) |
|---|---|---|
| P1 | `WeeklyEdgeP1PCT_v1.cs` · sha256 `ee4c765b…` | **`WeeklyEdgeP1PCT_v2.cs`**, class `WeeklyEdgeP1PCT_v2` |
| XM | `WeeklyEdgeXMConflict_v2.cs` · sha256 `2ec00dd4…` | **`WeeklyEdgeXMConflict_v3.cs`**, class `WeeklyEdgeXMConflict_v3` |

Rules that follow from CLAUDE.md §6 and STRATEGY_AUDIT §1:

- **New file, new class name, new `Name` string.** Never rename a parity-certified class; never edit
  one. Deleting a `.cs` does not remove the type from `NinjaTrader.Custom.dll`, so verification is by
  **resolving the class**, not by trusting a compile flag.
- **`Tag` defaults are unchanged** (`"p1pct"`, `"xm2"`) so the per-bar export filenames
  (`we_p1pct_p1pct.csv`, `we_xm_xm2.csv`) are identical between old and new. The identity diff is then
  a byte-compare of two identically-named files in two different `ExportDir`s.
- **The existing export format is frozen.** No column is added, removed or reordered. Every new
  diagnostic goes to a **separate** file (§3 HD-13), written only under M1.
- The hardened classes are **NOT certified**. Until §7 passes they are shadows, not replacements, and
  nothing in this plan deploys, enables or replaces anything.

---

# 2. HAZARD → ITEM MAP

| Hazard | Source | Closed by |
|---|---|---|
| H1 internal ledger never reconciled with fills | RUNBOOK, AUDIT §5, R2 §0 | **HD-01, HD-02, HD-03, HD-04** |
| Order rejection / partial fill / platform cancel | R2 §2, R3 D13 | **HD-02, HD-03, HD-10** |
| Instrument-month guard defect (root-only compare) | RUNBOOK 🐛, AUDIT §6.3(c) | **HD-05** |
| No expiry awareness; nothing announces the roll | R1 §5, AUDIT §6 | **HD-06** |
| Warm-up not proven; under-warm P1 *over*-trades, under-warm XM trades a *different* signal | R4 §1.1 | **HD-07, HD-08** |
| H5 connection-loss posture inherited/untested; `Recalculate` re-triggers H1 | R2 §4, AUDIT H5 | **HD-09** |
| H4 XM staleness gate sits above the exit path | AUDIT H4, R3 §6.3 | **HD-12** |
| D1 XM cross-market realtime race (34 % of net) | R3 §6.2 | **HD-13** (measure only; the fix is RC-04) |
| D7 mutable holiday table; E2 trading-hours template unverified | R3 §4.3, AUDIT E2 | **HD-14** |
| D10 late bar close / empty minutes | R3 §2.2 | **HD-13** |
| D12 `Calculate` mode silently degrades historically | R3 §2.3 | **HD-11** |
| P1 `sessionEndTs` stuck on a missed 18:01 bar → silent all-day outage | AUDIT H2 sub-item | **HD-15** |
| H2 no platform flatten when the process is dead; H3 no resting stop | AUDIT H2/H3 | **NOT CLOSABLE IN CODE — §5** |

---

# 3. THE HARDENING ITEMS

Notation: **P1** = applies to `WeeklyEdgeP1PCT_v2`; **XM** = applies to `WeeklyEdgeXMConflict_v3`.
Line numbers refer to the certified files.

---

## HD-01 · Shadow fill ledger from executions (observer, never a replacement) — P1, XM

**Hazard:** H1. The certified ledger advances by *assumption* — `myQty = pendingSize`,
`myEntryPx = Open[0]`, `sessPnl += (Open[0] − myEntryPx)·PV − CommissionRT`
(`P1PCT_v1.cs:260-276`; `XMConflict_v2.cs:242-257`). There is no branch for *not filled*.
**VERIFIED(source).**

**Mechanism.** Add `OnExecutionUpdate` and `OnOrderUpdate` overrides whose **first statement** is the
M1 gate. They maintain a *parallel* set of fields and **never write to any certified field**
(`myQty`, `myEntryPx`, `sessPnl`, `sessStopped`, `myPos`, `realizedPnl`, `pendingAct`, `pendingSize`,
`pendingDir` are untouched by the hardening code).

```csharp
// ---------- shadow reconciliation state (realtime only) ----------
private int        shFilled   = 0;      // cumulative executed qty for the order in flight
private double     shAvgPx    = 0.0;    // qty-weighted avg fill price
private bool       shTerminal = false;  // Filled / Rejected / Cancelled seen
private OrderState shState    = OrderState.Unknown;
private ErrorCode  shError    = ErrorCode.NoError;
private int        shNetQty   = 0;      // signed running position implied by executions alone
private bool       haltEntries = false; // one-way latch
private string     haltReason  = "";

private static bool IsMine(string n)    // P1: "L","XL","XLsess"   XM: "XM_L","XM_S","XM_X","XM_DIS"
{ return n == "L" || n == "XL" || n == "XLsess"; }

protected override void OnExecutionUpdate(Execution execution, string executionId, double price,
        int quantity, MarketPosition marketPosition, string orderId, DateTime time)
{
    if (State != State.Realtime) return;                 // M1
    if (execution == null || !IsMine(execution.Name)) return;
    int q = execution.Quantity; double p = execution.Price;   // passed-by-value discipline
    shAvgPx  = (shFilled + q) > 0 ? (shAvgPx * shFilled + p * q) / (shFilled + q) : 0.0;
    shFilled += q;
    shNetQty += (marketPosition == MarketPosition.Long ? q : -q);
}
```

- Match by **`execution.Name`**, never `execution.Order` (an execution can arrive before the order
  update on a partial fill) and never `OrderId` (*"is NOT a unique value, since it can change
  throughout an order's lifetime"*). **VERIFIED(onexecutionupdate.htm Example 2; order.htm).**
- Work only with the **passed-by-value** parameters. **VERIFIED(onexecutionupdate.htm,
  onpositionupdate.htm).** Never read `Position.Quantity` from inside a fill callback.
- `OnExecutionUpdate` is authoritative for fills: *"If you want to drive your strategy logic based on
  order fills you must use OnExecutionUpdate() instead."* **VERIFIED(onorderupdate.htm).**

**Why inert historically:** **M1**. The callbacks *do* fire during historical processing — the
override exists — but the first line returns before touching anything. No certified field is
reachable from this code at all. **INFERRED** that merely declaring the overrides does not perturb the
Analyzer's fill engine; that inference is discharged by **V2** (row-identity), which is exactly the
measurement that would expose it.

**Test:** V2 (identity), V3-c (the diagnostic build exercises the bodies), and on the eventual paper
run the `_hardening.csv` (HD-13) must show `shFilled` and `shAvgPx` populated on every real fill.

---

## HD-02 · Order-lifecycle observer: rejection, cancel, partial, non-terminal — P1, XM

**Hazard:** every row of R2 §0's divergence table. A rejected entry still sets `myQty = pendingSize`
(phantom long); a rejected exit orphans a real position; a partial fill leaves the ledger claiming a
size the account does not hold; a managed-approach **silent** refusal produces *no callback at all*
and is only findable by HD-04.

**Mechanism.**

```csharp
protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
        int filled, double averageFillPrice, OrderState orderState, DateTime time,
        ErrorCode error, string comment)
{
    if (State != State.Realtime) return;                 // M1
    if (order == null || !IsMine(order.Name)) return;

    // historical -> realtime conversion, once, defensively: we never Cancel/Change an order,
    // so the "modified a historical order" disable cannot occur, but the guard costs nothing.
    if (order.IsBacktestOrder) { Order rt = GetRealtimeOrder(order); if (rt != null) order = rt; }

    shState = order.OrderState;                          // branch on CURRENT state
    shError = error;                                     // log THIS update's state + error

    if (order.OrderState == OrderState.Rejected)
        Halt("REJECT name=" + order.Name + " err=" + error + " comment=" + comment);
    else if (order.OrderState == OrderState.Cancelled)
    {   shTerminal = true;
        if (order.Filled == 0) Halt("CANCELLED-UNFILLED name=" + order.Name);
        else                   Halt("CANCELLED-PARTIAL name=" + order.Name + " filled=" + order.Filled);
    }
    else if (order.OrderState == OrderState.Filled)
        shTerminal = true;
    // Working / Accepted / PartFilled / Suspended / AcceptedByRisk / TriggerPending: not terminal.
}
```

- Branch on `order.OrderState` (current); **log** the `orderState` parameter (this update).
  **VERIFIED(onorderupdate.htm — the two differ; the doc's own example prints `PartFilled` vs
  `Working`).**
- Do **not** write a `switch` over 14 states: `Suspended` and `AcceptedByRisk` exist in
  `NinjaTrader.Cbi.OrderState` on this install and are absent from the public page.
  **VERIFIED(reflection, R2 §1.6).**
- `Working` is not a reliable live milestone (*"in real-time, some stop orders may only reach
  'Accepted' state"*). Treat only `Filled` / `Rejected` / `Cancelled` as terminal.
  **VERIFIED(order.htm).**
- **Partial fill: latch, do not adjust.** The research object has **no** defined semantics for a
  partial fill. Inventing one here would be an unrecorded parameter. Record and stop.
- Assign the order object **inside** `OnOrderUpdate`, never in `OnBarUpdate` — *"the assignment is not
  gauranteed to be complete if it is referenced immediately after submitting"* [sic].
  **VERIFIED(onorderupdate.htm, advanced_order_handling.htm).**

**Why inert historically:** **M1** *and* **M2** — in the Analyzer no order is ever rejected or
broker-cancelled, so even without M1 these branches are unreachable. **VERIFIED(order.htm; R3 §3.1).**

**Test:** V2; V3-c exercises the branches in the diagnostic build; a real rejection on paper is the
only true end-to-end test and is recorded as an open observation, not a gate.

---

## HD-03 · Non-terminal order across a bar boundary — P1, XM

**Hazard:** the certified settlement assumes an instantaneous next-open fill. If the order is still
`Working` when the next bar's `OnBarUpdate` runs, the research assumption has already failed, and the
certified code will book a fill that did not happen.

**Mechanism.** In `OnBarUpdate`, **immediately after** the untouched certified settlement block
(P1 `:260-276`, XM `:242-257`), call an observer:

```csharp
private void ObserveSettlement(int actJustSettled, int reqQty)
{
    if (State != State.Realtime) return;                          // M1
    if (actJustSettled == ACT_NONE) return;
    if (!shTerminal)            Halt("NON-TERMINAL order at settlement; ledger booked an assumed fill");
    else if (shFilled == 0)     Halt("ZERO-FILL settlement; ledger moved, account did not");
    else if (shFilled != reqQty) Halt("PARTIAL-FILL " + shFilled + "/" + reqQty + "; no research semantics");
    else if (Math.Abs(shAvgPx - assumedFillPx) > 1e-9)
        LogInfo("FILLPX assumed=" + assumedFillPx + " actual=" + shAvgPx);  // record, do NOT halt
    ResetShadow();
}
```

`assumedFillPx` is a **copy** of the `Open[0]` the certified code used — taken by reading `Open[0]`
again, not by changing the certified line. A fill-price difference is **logged, not halted**: real
slippage is expected (R3 D6) and halting on it would stop the book on every ordinary tick of drift.
A *quantity* difference is halted, because it makes the ledger structurally wrong.

**Why inert historically:** **M1**, plus the fact that the observer takes `actJustSettled` and
`reqQty` as *copies* and writes nothing back.

**Test:** V2; the fill-price delta series is the first genuine measurement of D6/D3 on paper.

---

## HD-04 · The invariant: ledger vs NT8's **strategy** position (never `PositionAccount`) — P1, XM

**Hazard:** H1 in its general form, including the *undetectable* case — the managed layer silently
declining to submit an order (*"you will only be notified of the very first order which has violated
an order handling rule"* — **VERIFIED(managed_approach.htm)**). No callback fires; only a position
comparison finds it.

**Mechanism.** Called once per bar, **after** `ObserveSettlement` and **before** the order block:

```csharp
private void AssertLedgerMatchesStrategyPosition(int ledgerQty)
{
    if (State != State.Realtime) return;                          // M1
    int nt8 = (Position.MarketPosition == MarketPosition.Long)  ?  Position.Quantity
            : (Position.MarketPosition == MarketPosition.Short) ? -Position.Quantity : 0;

    if (!firstRealtimeBarSeen)                                    // transition carry, see below
    {   firstRealtimeBarSeen = true;
        if (nt8 != ledgerQty)
        {   entriesBlockedUntilAgree = true;
            LogWarn("WARMUP-CARRY-NONFLAT ledger=" + ledgerQty + " strategyPosition=" + nt8); }
        return;
    }
    if (entriesBlockedUntilAgree)
    {   if (nt8 == ledgerQty) { entriesBlockedUntilAgree = false; LogInfo("CARRY-RESOLVED"); }
        return;                                                   // self-healing, one-way to armed
    }
    if (nt8 != ledgerQty || (shNetQty != ledgerQty))
        Halt("RECONCILE-BREAK ledger=" + ledgerQty + " strategyPosition=" + nt8
           + " execImplied=" + shNetQty
           + " accountPosition=" + PositionAccount.Quantity + "(" + PositionAccount.MarketPosition + ")");
}
```

`ledgerQty` = `myQty` for P1 (long-only), `myPos * Qty` for XM.

- **Compare against `Position`, never `PositionAccount`.** `Position` is *"position related
  information that pertains to an instance of a strategy"*; `PositionAccount` is the **real account**
  net, which on `DEMO8383477 / NQ 09-26` contains **P1 + XM + anything manual**. If P1 is long 2 and
  XM is short 1, `PositionAccount` reads Long 1 and *neither* ledger matches it — a false break on
  most bars of a two-leg book. **VERIFIED(position.htm, positionaccount.htm; reasoning R2 §5.2.)**
- `PositionAccount` goes **in the log line only** — it is the only view of aggregate exposure and
  therefore of margin — and **never gates a decision**. This is CLAUDE.md §3's
  `EXECUTABLE_COMPONENT_SET` distinction expressed at runtime.
- **Three-way check.** `ledgerQty` vs `Position` vs `shNetQty` (executions). Two independent
  witnesses against the ledger.
- **The transition-carry case is real and must not be a false alarm.** The warm-up replay ends with
  whatever *virtual* position the last replayed bar left. Both objects flatten at every session end
  (P1 `:482`, XM `:341`), so starting between sessions gives a flat virtual position — but a
  mid-session start does not. **VERIFIED(R4 §4.4).** The first realtime bar therefore *blocks entries
  until the two agree* (self-healing) instead of latching a permanent halt. Every subsequent
  mismatch latches.

**Why inert historically:** **M1**.

**Test:** V2 (must not perturb identity); on paper, the log must contain exactly one
`WARMUP-CARRY-*` or nothing on start, and no `RECONCILE-BREAK` under normal operation.

---

## HD-05 · Instrument-month guard — the certified defect, fixed — XM (identity part also P1)

**Hazard (the defect, quoted from `XMConflict_v2.cs:183-186`):**

```csharp
string got = BarsArray[i].Instrument.FullName;
if (... || !got.StartsWith(want[i].Split(' ')[0], StringComparison.OrdinalIgnoreCase))
```

`want[i].Split(' ')[0]` reduces `"ES 09-26"` to `"ES"`, and **`"ESZ6".StartsWith("ES")` is true**, so
**the contract month is never checked**. Roll NQ to December while any secondary stays on September
and the guard stays `false`: the strategy trades **December NQ against September secondaries** and
reports itself healthy. **VERIFIED(source; RUNBOOK 🐛; AUDIT §6.3(c)).** This is precisely the failure
class the guard was written to prevent (W44: −$24,269 vs +$8,326), at the one moment it is most likely
— a partial manual roll.

**Mechanism — compare the *object*, not the string.** String formatting of `FullName` is
symbology-dependent (`Instrument.GetFullName(UserSymbologySetting, bool legacy)` exists —
**VERIFIED(reflection, this install)**), so a full-string equality test is brittle. Compare the two
facts that actually matter, taken from the `Instrument` object:

```csharp
// helpers
private static bool TryParseWanted(string want, out string root, out int mm, out int yy)
{
    root = null; mm = 0; yy = 0;
    if (string.IsNullOrEmpty(want)) return false;
    string[] parts = want.Trim().Split(' ');
    if (parts.Length < 2) return false;                 // "ES" alone -> not parseable
    root = parts[0];
    string[] my = parts[1].Split('-');
    if (my.Length != 2) return false;
    return int.TryParse(my[0], out mm) && int.TryParse(my[1], out yy) && mm >= 1 && mm <= 12;
}

// State.DataLoaded, replacing the certified loop body (structure preserved)
for (int i = 1; i < 4; i++)
{
    if (BarsArray[i] == null || BarsArray[i].Instrument == null
        || BarsArray[i].Instrument.MasterInstrument == null) { instrumentMismatch = true; break; }

    string wRoot; int wMm, wYy;
    if (!TryParseWanted(want[i], out wRoot, out wMm, out wYy)) { instrumentMismatch = true; break; }

    // (a) ROOT — against MasterInstrument.Name, not a StartsWith on a formatted string
    if (!string.Equals(BarsArray[i].Instrument.MasterInstrument.Name, wRoot,
                       StringComparison.OrdinalIgnoreCase)) { instrumentMismatch = true; break; }

    // (b) CONTRACT MONTH — the half that was missing
    DateTime ex = BarsArray[i].Instrument.Expiry;
    if (ex.Month != wMm || (ex.Year % 100) != wYy) { instrumentMismatch = true; break; }

    // (c) CROSS-SERIES: every secondary must be on the SAME contract month as the PRIMARY.
    //     This is the partial-roll case the certified guard cannot see.
    DateTime px = Instrument.Expiry;
    if (ex.Month != px.Month || ex.Year != px.Year) { instrumentMismatch = true; break; }
}
```

- `Instrument.Expiry` (`DateTime`, readable) and `MasterInstrument.Name` (`string`) both exist on this
  install. **VERIFIED(reflection, 2026-08-30: `NinjaTrader.Cbi.Instrument` → `Expiry`, `FullName`,
  `MasterInstrument`; `NinjaTrader.Cbi.MasterInstrument` → `Name`).**
- On this install the four live rows carry `Expiry = 2026-09-01` for ES/NQ/RTY/YM U6 —
  **VERIFIED(R1 §1.2, DB read-only copy: ticks `639238176000000000`)** — i.e. `Expiry` is the
  **contract-month marker (first of month), not the last trading day.** Clauses (b)/(c) use only
  `Month`/`Year`, which is exactly what that value supports.
  ⚠️ **TRAP: never use `Instrument.Expiry` as a trading deadline.** For U6 it is 2026-09-01, *before*
  the roll and *before* the 2026-09-01 shadow start — a "stop trading at Expiry" rule would silently
  kill the book on day one. Expiry is for **identity**; HD-06 owns the **clock**.
- **P1** is single-series and has no such guard at all. It gets clause (b) only, against a new
  `[NinjaScriptProperty] string ExpectInstrument` **defaulting to `""` = check disabled**, so P1's
  default behaviour is byte-identical and the check is opt-in at deployment.

**Why inert historically:** **M4**. With the certified parameters (`ES 09-26`, `RTY 09-26`,
`YM 09-26`, primary `NQ 09-26`, all four `Expiry` = 2026-09-01), clauses (a), (b) and (c) all pass,
`instrumentMismatch` stays `false`, and the order block at `:320` is unchanged. Inertness here is
**conditional on the certified parameter set** and must be *demonstrated*, not assumed — that is V2,
and V3-a proves the branch can fire.

**Test:**
- **V2** — identity with the certified params.
- **V3-a (the negative test that proves the defect is closed)** — run `_v3` with
  `EsInstrument="ES 12-26"` and everything else certified → expect `instrumentMismatch = true`,
  **0 trades**, and one `Log(..., LogLevel.Error)` naming the mismatching series and both expiries.
  Then run `_v2` with the same parameters → it still trades. **That difference is the defect, and it
  is the only intentional non-identity anywhere in this spec.** It occurs outside the certified
  parameter set, so it does not violate §0.

---

## HD-06 · Expiry awareness / fail-safe roll — refuse NEW entries near the roll — P1, XM

**Hazard:** R1 §5 / AUDIT §6.3(a). *"NinjaScript strategies are not rolled forward and must be
manually rolled over"* **VERIFIED(rolling_over_a_futures_contrac.htm)**, a restart does **not**
re-resolve (the expiry is a frozen FK — **VERIFIED(R1 §1.2, schema + rows)**), and
`MasterInstruments.AutoLiquidation = 0` for all four instruments — **VERIFIED(R1 §5, DB query)**. In
the window **2026-09-10 → 09-18** U6 still prints, so **no existing guard fires**, while liquidity
drains to Z6: *"this is the only window in which the system trades on bad data rather than simply
stopping"* (AUDIT §6.3(a)). After expiry it fails safe but **silently** (XM disqualifies every
session; P1 stops receiving bars — and, per R1 §5, a position open at that moment can never be exited
by the strategy's own logic).

**Mechanism — computed lazily on the first realtime bar, never in a backtest.**

```csharp
private DateTime rollBlockFrom = DateTime.MaxValue;
private bool     rollResolved  = false;
[NinjaScriptProperty] public int RollLeadDays { get; set; }   // default 8

private void ResolveRollDates()
{
    if (State != State.Realtime || rollResolved) return;      // M1 — never called in a backtest
    rollResolved = true;
    try
    {
        DateTime earliest = DateTime.MaxValue;
        // primary + (XM) every added series: four legs, four different roll dates
        for (int i = 0; i < BarsArray.Length; i++)
        {
            DateTime rd = BarsArray[i].Instrument.MasterInstrument.GetNextRolloverDate(Time[0]);
            if (rd > DateTime.MinValue && rd < DateTime.MaxValue && rd < earliest) earliest = rd;
        }
        if (earliest < DateTime.MaxValue)
            rollBlockFrom = earliest.Date.AddDays(-Math.Max(0, RollLeadDays));
        LogWarn("ROLL-PLAN blockNewEntriesFrom=" + rollBlockFrom.ToString("yyyy-MM-dd")
              + " leadDays=" + RollLeadDays);
    }
    catch (Exception e) { LogErr("ROLL-RESOLVE-FAILED " + e.Message); rollBlockFrom = DateTime.MaxValue; }
}

private bool RollBlocked()
{ return State == State.Realtime && Time[0].Date >= rollBlockFrom.Date; }   // M1
```

**Where N comes from (R1's roll-date semantics).**
`MasterInstrument.GetNextRolloverDate(DateTime)` exists and is public on this install —
**VERIFIED(reflection, 2026-08-30)** — and the rollover date is *"the date to roll **into** the
selected contract month and **NOT** out of"*, with the eligibility rule *"today's date is greater then
or equal to the rollover date defined for the instruments next contract month"* [sic].
**VERIFIED(editing_instruments.htm, rolling_over_a_futures_contrac.htm).** The stored table on this
install — **VERIFIED(R1 §2.4, blob decode)** — gives, for contract month 2026-12:

| | ES | RTY | NQ | YM |
|---|---|---|---|---|
| stored rollover date | **2026-09-14** | **2026-09-15** | **2026-09-16** | **2026-09-18** |

The CME equity-index volume roll is the Thursday **eight days** before the third-Friday expiry =
**2026-09-10** (**VERIFIED(AUDIT §6.2)**), i.e. **earlier than every stored NT8 date**. So a guard on
the NT8 date alone leaves 4–8 days of the dangerous window open.

⇒ **`RollLeadDays = 8`, applied to the *earliest* rollover date across all series.**
XM: `min(09-14, 09-15, 09-16, 09-18) − 8 = 2026-09-06`. P1: `09-16 − 8 = 2026-09-08`. Both are at or
before the 09-10 volume roll, erring early — the correct direction for a fail-safe.
**INFERRED(calibration)**; `RollLeadDays` is a `[NinjaScriptProperty]` so an owner override is a
recorded decision. **The four legs' four different dates are exactly why the minimum is taken**
(R1 §2.4 consequence 2: *"a single 'roll day' for that strategy does not exist"*).

**Behaviour when blocked:** refuse new entries; **exits untouched**; emit one
`Log(..., LogLevel.Error)` + `Alert(Priority.High)` per session naming the block date and the
contract that should be active (`MasterInstrument.GetInstrumentByDate(...)` — **VERIFIED(reflection)**
— may be used for the alert text, inside the same try/catch). The strategy does **not** disable
itself, does not flatten, and does not roll: *"an auto-roll that disagrees with the research substrate
would be an unrecorded parameter"* (`XMConflict_v2.cs:66-69`).

**Why inert historically:** **M1**, twice over. `ResolveRollDates()` is *never called* in a backtest,
so `GetNextRolloverDate` is never invoked and no rollover-collection side effect is possible
(`UpdateRolloverCollection` and `GetInstrumentByDate(..., suppressCalculateRollOvers)` show NT8 has
recomputation paths in this area — **VERIFIED(reflection)** — and we simply never enter them).
`rollBlockFrom` stays `DateTime.MaxValue`, and `RollBlocked()` short-circuits on `State`.

**Test:** V2 (identity, and the diagnostic build must show `ResolveRollDates` was never entered);
V3-c exercises the arithmetic with an injected date; on paper the `ROLL-PLAN` line must appear once
per start and must read `2026-09-06` (XM) / `2026-09-08` (P1) with today's stored table.

---

## HD-07 · Warm-up assertion — block entries until the windows are provably full — P1, XM

**Hazard:** R4 §1.1. `BarsRequiredToTrade = 20` is **not** the warm-up requirement. An under-warm
**P1 fails OPEN** — `rngHist[tod].Count < 20 ⇒ norm = 0 ⇒` all three throttle clauses pass `⇒ nThr = 4
⇒` the vote threshold is far easier, so it **trades MORE than the certified object**
(**VERIFIED(source `:442-448`)**) while `qCount < 100` makes the 2-lot impossible
(**VERIFIED(source `:458,467-478`)**). An under-warm **XM trades a different signal** — a market whose
sigma is NaN is skipped, so `comp = acc/cnt` is the mean over a *subset* of {ES, RTY, YM}, silently
(**VERIFIED(source `:296-302`)**). **Both look exactly like a working strategy.**

**Mechanism — the gate list, evaluated from the accumulators themselves.**

P1 (`spec` = research length, `min` = degeneracy floor):

| gate | spec | min | observed |
|---|---|---|---|
| `sigma_diffs` | `VolPeriod` = 460 | 30 | `diffs.Count` |
| `tilt_sessions` | `TiltSma + 1` = 51 | 51 | `sessCloses.Count` |
| `bmom_rth_days` | `BmomBandDays` = 14 | 14 | `rthDays` |
| `rng_sessions` | 60 | 20 | `min` over populated `rngHist[tod].Count` |
| `atr_bars` | 14 | 14 | `trQ.Count` |
| `volnorm_bars` | 240 | 30 | `volQ.Count` |
| **`qual_entries`** | **`QualWindow` = 250** | **`QualMinHist` = 100** | **`qCount`** |

**`qual_entries` is the binding gate and it is event-driven, not calendar-driven** — `qCount`
increments once per *entry*, not per bar or per session, so no amount of calendar warm-up guarantees
it (**VERIFIED(source `:458,478)`**; ≈128 sessions ≈183 calendar days at the historical activity rate,
**INFERRED**). It must be **measured**. This is the technical heart of the owner's question.

XM — **per series, never in aggregate** (an aggregate hides the subset-composite failure):
`xm_hist_ES`, `xm_hist_RTY`, `xm_hist_YM`, spec `SigmaLookback` = 60 / min `SigmaMinHist` = 20,
observed `hist[i].Count`.

**Verdicts:** `GO` (every gate ≥ spec) → armed. `DEGRADED` (every gate ≥ min, at least one < spec) →
**entries blocked**, `LogLevel.Warning` + `Alert(Priority.High)`. `NO-GO` (any gate < min) → entries
blocked, `LogLevel.Error` + `Alert(Priority.High)`.
**There is no `AllowDegradedWarmup` property.** R4 proposed one; it is dropped, because a property
that lets a non-object trade is a checkbox standing between the book and a known-bad state. Running
short is a *redeployment* decision (change `DaysToLoad`), not a runtime toggle.

**Wiring (the inversion rule, §0.2):**

```csharp
private bool warmupBlocked = false;                      // default NOT blocking
// OnStateChange:
else if (State == State.Transition) { warmupRows = BuildWarmupTable();
                                      warmupBlocked = (Classify(warmupRows) != "GO"); }
else if (State == State.Realtime)   { ReportWarmup("START"); }   // Log + Alert + certificate
// OnBarUpdate, top of the BIP-0 path:
if (State == State.Realtime && warmupBlocked)            // M1, one-way re-arm
{   warmupRows = BuildWarmupTable();
    if (Classify(warmupRows) == "GO") { warmupBlocked = false; ReportWarmup("REARM"); } }
```

**Two traps, both from R4 §1.3(b), both binding:**
- ⚠️ **TRAP 1 — gate the order site, not the predicate.** In P1 `wantLong` is read at `:492`
  (**the exit**) and `:496` (the entry). Writing `wantLong = wantLong && armed` **inverts the exit**
  whenever the gate is shut. Gate the `else if` at `:496` only. XM: gate the `if` at `:320` only.
- ⚠️ **TRAP 2 — never gate the accumulator writes.** P1's `qCount++` is at `:478`, *upstream* of the
  order site; XM's `hist[i].Add(r)` is at `:300`, likewise. Gating there freezes the counters and a
  strategy one entry short of 250 stays disarmed **forever** — a deadlock. Gating only the order site
  is both correct and the only placement that preserves the self-healing re-arm.

**Why inert historically:** **M1 + the inversion rule.** `State.Transition` never occurs in a
Strategy Analyzer run, so `warmupBlocked` stays `false` for the entire backtest and the added
conjunct at the order site is a constant `true`. **This is the item the constraint most easily breaks;
V2c is its falsifier.**

**Test:** V2 (identity — a single blocked entry would change the trade list); V2c (zero
Transition/Realtime markers in the backtest output); paper: the certificate must show
`qual_entries` observed ≥ 250 and every XM series ≥ 60.

---

## HD-08 · The warm-up certificate (the auditable artifact) — P1, XM

**Hazard:** an assertion nobody can read after an unattended overnight is not an assertion.

**Mechanism.** A `[NinjaScriptProperty] string WarmupCertDir` (default `""` = off). At
`State.Realtime` and on every re-arm, write

```
<WarmupCertDir>\warmup_<Tag>_<yyyyMMdd_HHmmss>Z.csv     # UTC-stamped: a restart must NEVER overwrite
strategy,tag,utc,verdict,gate,spec,min,observed,pass
...one row per gate, PRINTED BY THE PROGRAM...
env,DaysToLoad,<DaysToLoad>          env,bars_count,<Bars.Count>
env,bars_first_time,<Bars.GetTime(0)>  env,current_bar,<CurrentBar>
env,trading_hours,<Bars.TradingHours.Name>          # also closes AUDIT E2 — see HD-14
env,series_i_count,<BarsArray[i].Count>             # XM: one row per added series
env,series_i_first_time,<BarsArray[i].GetTime(0)>
env,series_i_instrument,<BarsArray[i].Instrument.FullName>
env,series_i_expiry,<BarsArray[i].Instrument.Expiry:yyyy-MM-dd>
```

The GATE/SPEC/OBSERVED/PASS-FAIL table is **printed by the program**, never assembled by hand
(CLAUDE.md §4). UTC stamping matters: with `NumberRestartAttempts = 4` a flaky connection can trigger
four full warm-up replays in five minutes (**VERIFIED(R2 §4, this install's `Config.xml`)**), and four
certificates must not overwrite each other. Measure history with `Bars.GetTime(0)` / `Bars.Count` /
`CurrentBars[]`, **never** by deep bar indexing — `MaximumBarsLookBack = TwoHundredFiftySix` on the
live deployment would throw on `Close[300]`. **VERIFIED(R4 §2.4).**

Channels, for a **headless** account strategy (`isChartHosted:false`, `ChartPanel:null` —
**VERIFIED(R4 §1.3(c), runtime probe)**): `Log(string, LogLevel)` is **primary** (the Control Center
Log tab is the only reviewable-after-the-fact channel); `Print` secondary; `Alert(...)` for
DEGRADED/NO-GO only and **only from `State.Realtime`** — *"Calls to this method in any other State
will be silently ignored"* **VERIFIED(alert.htm)**; **`Draw.*` is useless here — no chart surface
exists.**

**Why inert historically:** **M1** (written only at `Transition`/`Realtime`) **and** the empty-string
default. Two independent reasons.

**Test:** V2; paper start produces exactly one certificate file per lifecycle.

---

## HD-09 · Declared platform properties — see §4 for the full table and the flags

**Hazard:** H5. Neither certified file sets any of them, so both run on whatever Tools → Options says
today. The machine-wide defaults in force are `ConnectionLossHandling = Recalculate`,
`DisconnectDelaySeconds = 10`, `NumberRestartAttempts = 4`, `RestartsWithinMinutes = 5`
(**VERIFIED(this install's `Config.xml` → `StrategiesOptions`)**) — meaning a >10 s feed hiccup can
auto-restart the book **four times in five minutes**, each restart re-running history and **rebuilding
`sessPnl` from assumed fills**. That is H1 triggered by an ordinary network event.

**Full table, values, defaults, inertness classification and the two flagged items: §4.**

---

## HD-10 · Overfill and the managed approach — leave them alone, declare them — P1, XM

`IgnoreOverfill = false` (NT8 handles overfills; *"Setting this property value to true can have
serious adverse affects … unless you have programmed your own overfill handling"*
**VERIFIED(ignoreoverfill.htm)**) and `IsUnmanaged = false` (do not mix approaches). Both equal the
current effective value; declaring them removes the dependency on a future option change. **M3.**

---

## HD-11 · Configuration self-assertion — P1, XM

**Hazard:** D12 — *"State.Historical data processes OnBarUpdate() only on the close of each historical
bar even if this property is set to OnEachTick or OnPriceChange"* **VERIFIED(calculate.htm)**. A
`Calculate` change would **test clean and fail live**. Same class of risk: a deploy-time parameter map
setting a different bars period, `EntriesPerDirection`, or `IsUnmanaged`.

**Mechanism.** At `State.DataLoaded`, verify and latch (do not throw):

```csharp
if (Calculate != Calculate.OnBarClose)                      configFault = "Calculate=" + Calculate;
else if (EntriesPerDirection != 1)                          configFault = "EPD=" + EntriesPerDirection;
else if (IsUnmanaged)                                       configFault = "IsUnmanaged";
else if (BarsPeriod.BarsPeriodType != BarsPeriodType.Minute
      || BarsPeriod.Value != 1)                             configFault = "period=" + BarsPeriod;
// XM additionally: every BarsArray[i].BarsPeriod is 1-Minute
if (configFault != null) { haltEntries = true; haltReason = "CONFIG " + configFault; }
```

Blocking is via the same `EntriesAllowed()` gate, so **exits still run** — a wrong-config strategy
must still be able to close.

**Why inert historically:** **M4.** With the certified configuration (`OnBarClose`, EPD 1, managed,
1-Minute on all four series — **VERIFIED(source + AUDIT §0/§2/§3)**) `configFault` stays `null`.
Conditional on the certified configuration; discharged by V2 and by V3-b.

**Test:** V2; V3-b — if the tool surface allows injecting `Calculate = OnEachTick` into a backtest,
expect 0 trades + one Error log; if it does not, record that and verify by inspection in the
diagnostic build.

---

## HD-12 · H4 — the dead-secondary early return no longer strands an NQ position — XM

**Hazard:** `XMConflict_v2.cs:235` — `for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;` —
sits **above the exit logic**, so a secondary that never produces a first bar (lapsed subscription,
unavailable contract after a roll) makes the entire `OnBarUpdate` return and **the exit path never
runs**, coupling the ability to close an **NQ** position to the health of three unrelated feeds, with
no error and no alert. **VERIFIED(source; AUDIT H4).**

**Mechanism — structurally identical control flow, with a realtime-only escape hatch:**

```csharp
bool secReady = true;
for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) secReady = false;
if (!secReady)
{
    if (State == State.Realtime)                                   // M1
    {
        LogErr("DEAD-SERIES currentBars=[" + ... + "] myPos=" + myPos);
        if (myPos != 0 && EmergencyFlattenOnDeadSeries)
        {
            if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");
            Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");
        }
    }
    return;
}
```

Note the deliberate asymmetry: the certified loop returns on the *first* failing `i`, this one
evaluates all three. `CurrentBars[i]` is a pure read with no side effects, so the two are equivalent;
the *return* is reached on exactly the same bars.

**The ledger is deliberately not adjusted.** The resulting permanent `RECONCILE-BREAK` (HD-04) is the
intended visible state: loud, halted, operator-resolved. This is the **one** place a hardened class
submits an order the certified class would not — realtime only, only with a dead feed and an open
position, behind `[NinjaScriptProperty] bool EmergencyFlattenOnDeadSeries` (default **true**).

**Why inert historically:** **M1**. In a backtest the branch is a bare `return`, on the same bars, in
the same order.

**Test:** V2 (identity — the `return` path is exercised on the first bars of the series, which is
precisely where a control-flow change would show up); V3-c exercises the flatten in the diagnostic
build.

---

## HD-13 · Realtime-only diagnostics — the measurements R3 asks for, without changing behaviour — P1, XM

**Hazard:** R3's three largest exposures (D1, D4, D5) are **invisible to every backtest we can run**
(§7 of R3: High fill resolution is silently broken on XM, Tick Replay is not for strategy backtests
and is provably not set by our tool surface, and Playback would disconnect the running paper book on
Market-Replay data whose collection is **PAUSED by owner risk-control**). *"The forward paper run is
the only validation channel."* **VERIFIED(R3 §7).**

**Mechanism.** A `[NinjaScriptProperty] string DiagDir` (default `""` = off). Under **M1 only**,
append one row per event to `<DiagDir>\we_<Tag>_hardening_<yyyyMMdd>Z.csv` — a **separate file**; the
certified per-bar export format at `P1PCT_v1.cs:501-510` / `XMConflict_v2.cs:348-366` is **frozen**.

| tag | what it records | closes |
|---|---|---|
| `XMAGE` (XM) | at the 09:31 anchor and the 09:45 decision: `ts`, and per series `Times[i][0]`, `age` in minutes, `Closes[i][0]` | **D1.** One month converts the 34 %-of-net p5–p95 band into a measured branch probability per secondary. This is R3 §11.1's recommendation, obtained **without** an owner-authorised parameter change on a certified strategy. |
| `LATE` | `DateTime.Now − Time[0]` when it exceeds 90 s | **D10** — the ~15 empty minutes/session where `OnBarUpdate` fires late |
| `FILLPX` | assumed `Open[0]` vs actual `shAvgPx`, per fill (HD-03) | **D3, D6, D13** — the first real measurement of timing cost and partial fills |
| `SESSFLAT` | the `lastBar` flatten path firing (P1 `XLsess` `:482`, XM `lastBar` `:341`) | **D9** — ledger books at the session close, the engine fills at the next session's open, across the 60-minute break |
| `POS` | `OnPositionUpdate` (log-only; never drives logic — event ordering is not guaranteed on simultaneous fills) **VERIFIED(onpositionupdate.htm)** | audit trail |

**D4/D5** (the delta gate pivotal on 9.4 % of bars; the ratchet that never resynchronises) need no new
code: the certified `ExportDir` already emits `dL`, `mAnchor[0]`, `mS[0]`, `tgtPrev[]`. Enabling
`ExportDir` on a paper deployment plus a same-day backtest diff is R3 §11.5's detector. Add
`[NinjaScriptProperty] bool ExportStampUtc` (default **false**) so a live export does not clobber
itself on restart while the parity harness still gets the exact certified filename.

**Why inert historically:** **M1** and the empty-string default.

**Test:** V2; on paper, `XMAGE` must accumulate ≥ 20 sessions before D1 is quoted at all.

---

## HD-14 · Session-calendar and template provenance — P1, XM

**Hazard:** D7 — *"Trade Holidays are automatically updated from the NinjaTrader data server"*
**VERIFIED(using_the_trading_hours_window.htm)**. The trading-hours template is **not frozen with the
strategy**, so a backtest run today over 2023 uses *today's* holiday table. XM v2's **entire certified
difference from v1** is the `exitBarExists` guard computed from `SessionIterator.ActualSessionEnd`; a
server update to an Early Close row silently re-cuts which sessions it declines. Compounding this,
AUDIT **E2** records `tradingHoursName: null` on both deployments — the template every clock in both
files depends on is **unverified**.

**Mechanism.** At `State.Realtime` (and into the HD-08 certificate), log `Bars.TradingHours.Name`,
`Bars.FromDate`/`ToDate`, and for the current session `sessIter.ActualSessionBegin`/`ActualSessionEnd`;
for XM, the same `TradingHours.Name` for each `BarsArray[i]`. **This makes the strategy state its own
template**, closing E2 from the inside.

Code cannot *freeze* the calendar — that stays an operational control (§5 OPS-06).

**Why inert historically:** **M1**.

---

## HD-15 · `sessionEndTs` staleness detector — P1 (and XM by symmetry)

**Hazard:** `sessionEndTs` is refreshed only on `IsFirstBarOfSession` (`P1PCT_v1.cs:278-282`). If the
18:01 first bar is missed, it stays at the *previous* session's end, making `blocked` and `forceFlat`
true all day → **P1 refuses to trade for the entire session and the session box never resets**. Fails
in the safe direction, but it is a **silent all-day outage with no alert**. **VERIFIED(source; AUDIT
H2 sub-item).**

**Mechanism.** Under **M1**: if `Time[0] > sessionEndTs` and no `firstBar` has fired since, emit one
`Log(..., LogLevel.Error)` per session. **Detect only — do not re-derive `sessionEndTs`**, which would
change behaviour.

**Why inert historically:** **M1**.

---

## HD-16 · (FLAGGED, optional) `MaximumBarsLookBack = Infinite`

Removes the Analyzer's documented 256-bar truncation trap (RUNBOOK "manual backtesting" rule 2).
Neither strategy indexes beyond `[0]` — every accumulator is a plain `List`/`Queue`/`Dictionary`
(**VERIFIED(source; R4 §2.4)**) — so this should be behaviourally inert, but it is **not** M1/M2/M3
and it changes a platform property. **Declare it only if V2 passes with it in; otherwise omit.**
Default recommendation: **omit** — the equivalent control belongs in the Analyzer's own settings, and
this document does not spend identity risk on a convenience.

---

# 4. DECLARED PROPERTY SETTINGS (HD-09)

Set in `State.SetDefaults` unless noted. **VERIFIED(realtimeerrorhandling.htm, setorderquantity.htm,
ignoreoverfill.htm):** these must be assigned in `State.SetDefaults` or `State.Configure` only.

```csharp
// ---- realtime hardening (State.SetDefaults) -----------------------------------
RealtimeErrorHandling  = RealtimeErrorHandling.StopCancelClose;   // NT8 default, made explicit
ConnectionLossHandling = ConnectionLossHandling.StopStrategy;     // CHANGE from Recalculate
DisconnectDelaySeconds = 10;                                      // install default, explicit
NumberRestartAttempts  = 0;                                       // CHANGE from 4
StartBehavior          = StartBehavior.WaitUntilFlat;             // NT8 default, made explicit
IsAdoptAccountPositionAware = false;                              // explicit refusal to inherit
IsUnmanaged            = false;                                   // managed approach retained
IgnoreOverfill         = false;                                   // NT8 handles overfills
// State.Configure:
TraceOrders            = TraceOrdersLive;                         // property, default FALSE
```

| Property | Value | Current effective | Backtest impact | Inertness | Why |
|---|---|---|---|---|---|
| `RealtimeErrorHandling` | `StopCancelClose` | same (unset) | **none** | **M3 + M2** | Only safe value until HD-01…04 are proven on paper. `IgnoreAllErrors` is defensible *only after* the reconciler exists and has been measured; today it would let a rejected order poison `sessPnl` forever. `StopCancelCloseIgnoreRejects` is the worst of both — it keeps running through exactly the event the ledger cannot survive. **VERIFIED(realtimeerrorhandling.htm).** ⚠ `IgnoreAllErrorsNoAlert` exists in the assembly and is **undocumented — do not use** (**VERIFIED(reflection)**). |
| `ConnectionLossHandling` | **`StopStrategy`** | `Recalculate` | **none** (no connection exists to lose) | **M3 + M2** | `Recalculate` *"attempt[s] to recalculate its strategy position when a connection is reestablished"* — i.e. it re-runs the historical path and **rebuilds `sessPnl`/`myQty`/the quantile queues from the assumed-fill simulation**, discarding every real fill observed before the drop, and silently resets the session box. **This is the single most dangerous default we have.** `StopStrategy` makes the restart an owner decision at a moment when the ledger can be reconciled. **VERIFIED(connectionlosshandling.htm) + INFERRED(R2 §4).** |
| `DisconnectDelaySeconds` | `10` | `10` | none | **M3** | Explicit. **VERIFIED(disconnectdelayseconds.htm).** |
| `NumberRestartAttempts` | **`0`** | `4` | **none** | **M3 + M2** | Four restarts in five minutes = four full warm-up replays, each rewriting the session box. ⚠ **`RestartsWithinMinutes` is deliberately left at its default** — probe its `RangeAttribute` in **V0** before assigning `0`; `NumberRestartAttempts = 0` alone disables restarts, so there is no reason to risk a validation failure. ⚠ **`RestartOnConnectionLoss` DOES NOT EXIST** on `StrategyBase` in 8.1.8.1; writing it is CS0103. **VERIFIED(reflection, R2 §4).** |
| `StartBehavior` | `WaitUntilFlat` | same | **none expected — ⚠ FLAG** | **M3, to be confirmed by V2** | The only mode that (a) inherits nothing, (b) submits **no reconciliatory order**, (c) leaves the other leg alone. Every `*SynchronizeAccount` mode would **flatten XM's position when P1 starts**; `AdoptAccountPosition` is disqualified twice (it is the definition of inheriting a foreign position on a shared account, and *"Only one strategy with this setting can be started at a time for an individual account and instrument"*). **VERIFIED(startbehavior.htm, syncing_account_positions.htm).** It is not exposed by the Strategy Analyzer, so declaring it should be inert — **that is an inference, and V2 is its test.** |
| `IsAdoptAccountPositionAware` | `false` | `false` | none | **M3** | Makes `AdoptAccountPosition` inoperable by construction. |
| `IsUnmanaged` | `false` | `false` | none | **M3** | Do not mix approaches. |
| `IgnoreOverfill` | `false` | `false` | none | **M3** | See HD-10. |
| **`SetOrderQuantity`** | *(do not declare yet)* | unknown | **could change EVERY fill quantity** | **⚠ FLAGGED** | R2 §8 recommends `SetOrderQuantity.Strategy` and reports it as the default. Both strategies pass explicit quantities (`EnterLong(size,"L")`, `EnterLong(Qty,"XM_L")`), so if the effective value were `DefaultQuantity` this declaration would silently re-size every trade. The property exists on `StrategyBase` (**VERIFIED(reflection, 2026-08-30)**) but its **default was not confirmed on this install**. **Declare it only after V0 confirms the deployed read-back, and only if V2 then passes.** When in doubt, omit — an undeclared property cannot break identity. |
| **`TraceOrders`** | `TraceOrdersLive`, default **false** | `false` | none at default | **M4 (default) + M3** | R2 recommends `true` for the audit trail. Setting it unconditionally would flood a four-year Analyzer run and put a config value in the identity path. Routing it through a property that defaults `false` gives identity for free and the audit trail on the paper deployment. |
| `Slippage`, `IncludeTradeHistoryInBacktest`, `EntriesPerDirection`, `EntryHandling`, `IsExitOnSessionCloseStrategy`, `IncludeCommission`, `BarsRequiredToTrade`, `Calculate` | **DO NOT TOUCH** | — | **would change backtest fills or decisions** | — | `Slippage` in particular directly alters historical fills. Every one of these is part of the certified object. |

**New `[NinjaScriptProperty]` inputs added by this spec** (all defaulting to inert values, all
appearing in `DisplayParameters` and in every `GetStrategyState` probe, so any deviation is recorded):

| property | default | effect at default |
|---|---|---|
| `RollLeadDays` (int) | `8` | inert (HD-06 is M1-gated) |
| `WarmupCertDir` (string) | `""` | certificate off |
| `DiagDir` (string) | `""` | diagnostics off |
| `ExportStampUtc` (bool) | `false` | certified export filename preserved |
| `TraceOrdersLive` (bool) | `false` | `TraceOrders` stays at the NT8 default |
| `EmergencyFlattenOnDeadSeries` (bool, XM) | `true` | inert (M1-gated) |
| `ExpectInstrument` (string, P1) | `""` | identity check disabled |

⚠ **Do not rely on `DeployStrategy`'s `parameters` map to set the platform properties in §4.** They
are public read/write and *could* be injected after `SetState(SetDefaults)`, but that is untested and
the docs restrict assignment to `SetDefaults`/`Configure`. **Declare them in the `.cs`.**
**INFERRED(R2 §8).**

---

# 5. HAZARDS THAT CANNOT BE CLOSED IN CODE — OPERATIONAL CONTROLS ONLY

| # | Hazard | Why code cannot close it | The control |
|---|---|---|---|
| **OPS-01** | **The roll itself.** A restart does not re-resolve; disable/re-enable does not re-resolve; batch rollover explicitly **skips strategies**. NT8 stores a resolved `Instruments.Id` FK carrying a concrete `Expiry` — *"re-resolution is not merely disabled; it is **unrepresentable**"*. **VERIFIED(R1 §1.2/§1.7).** A strategy cannot change its own `Instrument` at runtime, and `AddDataSeries` *"should ONLY be called from OnStateChange() during State.Configure"* with arguments that *"must be hardcoded"*. **VERIFIED(adddataseries.htm).** | The roll is a **reconfigure**: disable → edit instrument (×1 for P1, **×4** for XM) → re-enable. *"Only disabled strategies can be edited."* **VERIFIED(strategies_tab.htm).** | RUNBOOK roll procedure, all four legs together. HD-06 only *announces*; it cannot roll. **The four XM legs roll on four different dates (ES 09-14, RTY 09-15, NQ 09-16, YM 09-18) — there is no single correct day and the owner must choose.** |
| **OPS-02** | **H2 — no platform-level flatten.** If the strategy is disabled, errored, stalled, or the process is dead, `OnBarUpdate` does not run and nothing closes the position (up to 3 contracts gross). `IsExitOnSessionCloseStrategy = false` is the *correct* design and cannot be changed without re-certification. | Code that is not running cannot act. A timer thread could log but must not submit orders. | External monitoring + the flat-before-anything rule. |
| **OPS-03** | **H3 — no resting protective order in the exchange book.** All risk control is market-on-next-bar-open, conditional on the process being alive and receiving data. | Adding a stop is a capital-risk decision the parity runs were explicitly forbidden from making. | Owner decision (RC-05). |
| **OPS-04** | `CancelEntriesOnStrategyDisable = false` / `CancelExitsOnStrategyDisable = false` in `Config.xml` — **a manual disable leaves working orders alive** on `DEMO8383477`. **VERIFIED(this install's Config.xml).** | Global platform options; not reachable from NinjaScript. | Owner decision on the global option; meanwhile never disable while an order is working. |
| **OPS-05** | **"Synchronize All Strategies"** (right-click, Strategies tab) aggregates strategy positions and **fires one live market order**, and *"the reconciliatory market order is submitted outside of the strategy so your strategy will not be able to manage it from methods like OnOrderUpdate(), OnExecution()"*. **VERIFIED(syncing_account_positions.htm).** | Invisible to every callback and to both ledgers by construction. | Never use it on this account. Brief the owner. |
| **OPS-06** | **D7 — the holiday/session table is server-mutable and retroactive.** | Code can log the template (HD-14); it cannot freeze it. | **Snapshot `CME US Index Futures ETH` (sessions + full holiday list) into this run directory now, and again before any re-certification.** |
| **OPS-07** | **D6 — cost model.** NT8 charges the template and **zero slippage** (`TotalSlippage 0.00` measured on both runs); research charges commission **plus** a modelled spread ($14.44 P1, $12.50 XM per ctrRT) = $3,321 (5.6 % of a 7-month P1 net) / $4,350 (2.2 % of XM net). | Not a code defect. | **Never quote an NT8 net as the expectation.** Research is the conservative number. |
| **OPS-08** | **N2 — `fill.type: "High"` on XM returns 0 trades, `success: true`, no error.** Multi-instrument strategies are permanently excluded from order fill resolution. **VERIFIED(understanding_historical_fill_.htm; MEASURED job `d0d5a7c460484c77`).** | A silent empty result that reads as "no signals". | **Never run XM at High.** Recorded so no future wave misreads it. |
| **OPS-09** | **Restart persistence is UNDOCUMENTED**, and R5 found **no on-disk record** of the running configuration — a crash would leave nothing to restore from on either the NT8 or the add-on side. | Nothing in NinjaScript can observe or control it. | Run R4 §4.2 / R5's experiment **while flat**; record the three-way outcome in the RUNBOOK. Until then *"NT8 is running" is a load-bearing precondition*. |
| **OPS-10** | **Two strategies on one account** — `PositionAccount` is a net and *"Placing manual trades or running multiple strategies on the same instrument can also lead to your Account Position being out of sync"*. **VERIFIED(syncing_account_positions.htm).** | HD-04 can log it; it must never gate on it. | Aggregate exposure is monitored externally. |
| **OPS-11** | **D15 — feed identity.** The paper book must be on the `Simulation` connection with `Simulated Data Feed` **disconnected**; a reconnect landing on the built-in random-walk feed would produce a plausible equity curve from synthetic prices. **MEASURED(R3 §5.1).** | Connection identity is not a supported NinjaScript read. | `GetConnections` at every shadow-runner touch — check the **identity**, not just the state. |
| **OPS-12** | **E3 — commission template not verifiable read-only**, and P1's box charges a hard-coded `CommissionRT = 4.36` regardless of the account template. | Not a defect; a reconciliation note. | Confirm `NinjaTrader Brokerage Lifetime` in the UI. |
| **OPS-13** | **MergePolicy** is `UseGlobalSettings (3) → MergeBackAdjusted`, and whether the strategies' loaded history is merged is **INFERRED, not VERIFIED**. | The MCP `GetBars` path ignores its own `mergePolicy` argument and returns contract-native bars. | Run R1 §3.5's volume test on the Backtest account before quoting anything that depends on the loaded history. Restate "MergePolicy=3" in repo docs as *"UseGlobalSettings → MergeBackAdjusted"*. |
| **OPS-14** | **Playback / Tick Replay / High fill are all closed to us** — no backtest configuration reproduces realtime behaviour for XM. Playback *"requires closing all other connections"*, which would stop the running paper book (HARD RULE 3), on Market-Replay data whose collection is **PAUSED by owner risk-control**. | Structural. | The forward paper run **is** the validation channel — which is the argument for HD-13, not for waiting. |
| **OPS-15** | **`EXECUTABLE_COMPONENT_SET` ≠ portfolio.** Certifying both legs does not produce an executable portfolio; the research portfolio is inverse-vol weighted and the integer-contract mapping is unselected. | Governance, not code. | CLAUDE.md §3. Never quote a research portfolio figure for the running pair. |

---

# 6. REQUIRES RE-CERTIFICATION — NOT IN SCOPE FOR THESE TWO CLASSES

Each of these is *worth doing*; none of them can live in a class that must be trade-for-trade
identical.

| # | Change | Why it is excluded |
|---|---|---|
| **RC-01** | **R2 §7.4 `SettlePending()` — driving the ledger from real fills** (`myEntryPx = workAvgPx`, `myQty = workFilled`, `sessPnl += (workAvgPx − myEntryPx)·PV·workFilled/myQty`). | This *replaces* the certified settlement arithmetic. Even where it would coincide with `Open[0]` in a backtest, it changes the ledger's **source of truth** and the box's denominator shape. It is the right long-term design and it is a **new object**. Here the fill-vs-assumption delta is *observed* (HD-03) and *halted on* (HD-02/04), never silently absorbed. |
| **RC-02** | **Defined semantics for a partial fill** (proportional box accounting, residual management). | The research object has none. Inventing one is an unrecorded parameter. HD-02 halts instead. |
| **RC-03** | **Auto-flatten on `reconcileHalt`.** | R2 §7.6 offers flatten-then-stop; it is realtime-only and therefore inert historically, but *"this is an owner decision, not mine"*, and a flatten computed from a ledger already known to be wrong is not reliable (`ExitLong(myQty)` with `myQty` wrong is a no-op or an over-exit). **This spec halts and logs; it does not flatten** — except HD-12's dead-series case, which is a different, unambiguous hazard. |
| **RC-04** | **The D1 fix — reading each secondary by timestamp rather than by index.** | Changes the composite on ~7.8 % of sessions (p5–p95 net band = **34.4 % of the object's entire net**). A new `_v4` and a full re-certification. HD-13 measures the race first, which is the correct order. |
| **RC-05** | **Raising `DisasterStopPoints` above 0**, or adding any stop to P1. | Capital-risk decision; and per R3 §7 **no faithful backtest exists** for it (High fill returns 0 trades on XM). Do not raise it believing it can be validated. |
| **RC-06** | Changing `MaxStaleMinutes`, any `hm` clock, `EntryBlockMin`, `ForcedFlatMin`, `QualWindow`, `SigmaLookback`, or the vote threshold. | These are the object. |
| **RC-07** | Switching to continuous / back-adjusted symbols. | Changes the substrate for all four series; mixing conventions *"corrupts the composite silently"*. |
| **RC-08** | Persisting decision state (`qCount`, `rngHist`, `hist[]`) across restarts. | Creates a **second source of truth** that no backtest reads and that can silently disagree with the replay. *"Do not persist decision state. Persist evidence only."* **(R4 §5.)** HD-08 writes the certificate, never the accumulators. |
| **RC-09** | ⚠️ **Post-roll re-verification.** Both parity specs pin `NQ 09-26` and the three `09-26` secondaries as *"part of the freeze"*. Rolling to Z6 restarts every price-level-dependent accumulator cold (`mAnchor`, `mS`, the tilt SMA, B-MOM's `open0930` slots) — the safe direction, but **the certified parity numbers do not describe the post-roll instance**. | Not a code change; a certification-scope fact that must travel with the roll. |

---

# 7. THE VERIFICATION PLAN — exactly what the next agent runs

Preconditions, non-negotiable: **do not stop, disable or redeploy `dep_306e11dfc8eb` /
`dep_5a914d070687`.** Every backtest runs on the isolated **Backtest** account via
`RunStrategyBacktest`. No git. Write only into
`runs/G2_LIVE_HARDENING_20260830/` and the two new `.cs` files.

**Spec-first (CLAUDE.md §4):** commit `runs/<NEW_RUN_ID>/spec.yaml` — falsifier, windows, parameters,
and the **100.000 % identity bar** — **before any result exists**. Never overwrite a run directory.

**Data seals:** the identity runs reuse the **certified windows**, which end on or before 2026-07-31.
**Do not extend any window into ≥ 2026-08-01 (VIRGIN).** The runs re-read BURNED /
DISCOVERY_CONSUMED data for an *identity* check only; **no P&L figure they produce is quotable at any
level.**

### V0 — read-only pre-flight (no writes, nothing disturbed)

1. `LookupNinjaScriptSymbol("NinjaTrader.NinjaScript.StrategyBase")` → confirm `SetOrderQuantity`'s
   type and any `RangeAttribute` on `RestartsWithinMinutes` / `NumberRestartAttempts`.
2. `GetStrategyState(DEMO8383477, 399550060)` and `(…, 399550061)` → record the live read-back of
   `SetOrderQuantity`, `StartBehavior`, `ConnectionLossHandling`, `RealtimeErrorHandling`,
   `MaximumBarsLookBack`. **Read-only. Do not modify.**
3. Record `Instrument.FullName` / `Instrument.Expiry` for NQU6/ESU6/RTYU6/YMU6 (HD-05 depends on the
   `Month`/`Year` of `Expiry`, which R1 read as 2026-09-01).
4. Read `runs/WE_P1PCT_PARITY_20260827/spec.yaml` and `runs/WE_XM_PARITY_20260827/spec.yaml` and
   **copy the exact window, parameters, session template, fill type and commission template from
   them.** Do not invent a window. Apply CLAUDE.md §6's boundary rule: `to` = one second before the
   next 18:00 ET open.

**Gate:** if `SetOrderQuantity`'s effective value is not confirmed `Strategy`, **omit it** from §4.

### V1 — build and resolve

Write `WeeklyEdgeP1PCT_v2.cs` / `WeeklyEdgeXMConflict_v3.cs` into
`C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\`. Then **verify by resolving the
class** (`LookupNinjaScriptSymbol("WeeklyEdgeP1PCT_v2")`), not by trusting a `compile_engine` flag —
a stale-type resolution has cost this campaign before. Record the sha256 of both new files.

### V2 — THE IDENTITY RUN (the proof)

For each pair, **four backtests**, all parameters identical except the class and `ExportDir`:

| run | class | `ExportDir` |
|---|---|---|
| A | `WeeklyEdgeP1PCT_v1` | `…/out/id_p1_v1/` |
| B | `WeeklyEdgeP1PCT_v2` | `…/out/id_p1_v2/` |
| C | `WeeklyEdgeXMConflict_v2` | `…/out/id_xm_v2/` |
| D | `WeeklyEdgeXMConflict_v3` | `…/out/id_xm_v3/` |

Fixed for all four: the window/params from V0.4; `CME US Index Futures ETH`; **`fill.type: Standard`**
(never `High` — OPS-08); `NinjaTrader Brokerage Lifetime`; `Maximum bars look back = Infinite`.

**Comparisons and the PASS/FAIL table — printed by the program, never assembled by hand:**

| # | check | bar |
|---|---|---|
| **V2a** | `we_p1pct_p1pct.csv` (A) vs (B), and `we_xm_xm2.csv` (C) vs (D) — **byte-identical**, including the header | **0 differing bytes.** This is the strongest test: it compares the decision series bar-by-bar, not just the trades. |
| **V2b** | trade list: count, entry/exit timestamps, prices, quantities, per-trade P&L, `TotalCommission`, `TotalSlippage`, net | **exactly equal, 0 differences** |
| **V2c** | ⭐ **the M1 falsifier.** The hardened classes emit `Print("HARDENING-STATE-MARK " + State)` **once** on entering `State.Transition` or `State.Realtime`. | The backtest output must contain **zero** `HARDENING-STATE-MARK` lines. A single line falsifies M1 and **every M1-gated item in this spec must be re-designed.** |
| **V2d** | XM only: `instrumentMismatch == false` and the HD-05 log line reports all four series on contract month 09-26 | pass |
| **V2e** | the hardened runs produce **no** `_hardening.csv` and **no** `warmup_*.csv` (defaults are `""`) | 0 files |

**Any failure of V2a/V2b is a FAIL of the whole spec.** Do not tune, do not rationalise, do not
appeal to the 99 % band. Find the leaking item, remove it, re-run. Record the failure — a gate that
fails is recorded failed.

### V3 — negative tests (prove each guard can actually fire)

| # | test | expected |
|---|---|---|
| **V3-a** | `_v3` with `EsInstrument="ES 12-26"`, all else certified, same window | `instrumentMismatch = true`, **0 trades**, one Error log naming ES and both expiries. Then `_v2` with the same params → **it still trades**. That contrast **is** the closed defect and is the only intentional non-identity in this work. |
| **V3-b** | If the tool surface can inject `Calculate = OnEachTick`: run `_v2`/`_v3` | HD-11 latches, 0 trades, one Error log. If it cannot be injected, record that and verify in V3-c. |
| **V3-c** | **Diagnostic build.** A **third**, throwaway class per leg (`WeeklyEdgeP1PCT_v2diag`, `WeeklyEdgeXMConflict_v3diag`) in which every `State != State.Realtime` M1 gate is replaced by `false`, so the realtime paths execute in the Analyzer. Run once, short window. | The realtime code paths **execute without throwing**, produce the expected `_hardening.csv` columns, `ROLL-PLAN`, warm-up table and dead-series branch. ⛔ **These builds are never deployed, never certified, and are deleted from the deployment path after the run.** They prove the guard code is *correct*; V2 proves it is *absent* from the certified path. |
| **V3-d** | The realtime-only guards (HD-06 roll block, HD-07 warm-up, HD-04 reconciliation) **cannot be exercised by any backtest, by construction.** | State this plainly. Their end-to-end test is a **supervised paper deployment of the new classes alongside — never replacing — the certified pair**, which is an **owner decision** and is not taken here. |

### V4 — determinism

Re-run V2 runs B and D once more. Byte-identical to the first execution. Guards against Analyzer
non-determinism being mistaken for a hardening bug (or vice versa).

### V5 — record

Into `runs/<NEW_RUN_ID>/`: `spec.yaml` (pre-committed), `REPORT.md` with the program-printed
GATE/SPEC/OBSERVED/PASS-FAIL table, both sha256 digests, every `RunStrategyBacktest` job id and the
backtest fingerprint, the four export files, and the diff summaries. Tag every metric
**LEGACY_DIAGNOSTIC / DIRECTLY_BURNED** as appropriate — **no dollar figure from these runs is
quotable.** Update `NT8_RUNBOOK.md` only with facts these runs established.

### V6 — what must NOT happen

No deployment. No enable. No replacement of a certified class. No parameter change on a running
strategy. The hardened classes remain **shadows** until the owner decides otherwise, and OPS-09's
restart experiment and OPS-06's calendar snapshot are prerequisites for that decision.

---

# 8. SOURCES

**NT8 Help Guide** (`ninjatrader.com/support/helpGuides/nt8/…`, 301 → `ninjatrader-live.ninjatrader.com`) —
`onorderupdate.htm`, `onexecutionupdate.htm`, `onpositionupdate.htm`, `order.htm`,
`advanced_order_handling.htm`, `getrealtimeorder.htm`, `managed_approach.htm`,
`realtimeerrorhandling.htm`, `connectionlosshandling.htm`, `disconnectdelayseconds.htm`,
`startbehavior.htm`, `syncing_account_positions.htm`, `position.htm`, `positionaccount.htm`,
`setorderquantity.htm`, `ignoreoverfill.htm`, `onstatechange.htm`, `state.htm`, `alert.htm`,
`daystoload.htm`, `barsrequiredtotrade.htm`, `calculate.htm`, `adddataseries.htm`,
`multi-time_frame__instruments.htm`, `discrepancies_real-time_vs_bac.htm`,
`understanding_historical_fill_.htm`, `tick_replay.htm`, `playback_connection.htm`,
`sessioniterator.htm`, `isfirstbarofsession.htm`, `islastbarofsession.htm`,
`using_the_trading_hours_window.htm`, `rolling_over_a_futures_contrac.htm`, `editing_instruments.htm`,
`strategies_tab.htm`.

**This install (authoritative for local state).** Reflection 2026-08-30 via
`LookupNinjaScriptSymbol` / `SearchNinjaScriptSymbols` (NT8 8.1.8.1, CrossTrade v1.13.9):
`NinjaTrader.Cbi.Instrument` → `Expiry` (DateTime, r/w), `FullName` (string, r), `MasterInstrument`,
`GetFullName(UserSymbologySetting,bool)`;
`NinjaTrader.Cbi.MasterInstrument` → `Name`, `GetNextRolloverDate(DateTime)`,
`GetNextExpiry(DateTime)`, `GetInstrumentByDate(...)`, `RolloverCollection`, `TradingHours`,
`MergePolicy`, `IsAutoLiquidationEnabled`;
`NinjaTrader.NinjaScript.SetOrderQuantity` (enum) and `StrategyBase.SetOrderQuantity` (r/w) exist.

**Run documents:** `R1_ROLLOVER.md`, `R2_REALTIME.md`, `R3_DIVERGENCE.md`, `R4_WARMUP.md`,
`R5_PERSISTENCE_PROBE.md`, `runs/G2_NT8_OPS_20260830/STRATEGY_AUDIT.md`,
`research/operational/NT8_RUNBOOK.md`.

**Certified sources, read-only:**
`C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\WeeklyEdgeP1PCT_v1.cs`
(sha256 `ee4c765b…`) and `…\WeeklyEdgeXMConflict_v2.cs` (sha256 `2ec00dd4…`).

---

*Architecture only. No `.cs` written, no strategy stopped, started, disabled, enabled or redeployed,
no order placed, no account touched, no git command run. This document is the only file written.*
