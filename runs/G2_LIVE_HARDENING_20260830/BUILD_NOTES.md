# BUILD NOTES — `WeeklyEdgeP1PCT_v2` and `WeeklyEdgeXMConflict_v3`

**Run** `G2_LIVE_HARDENING_20260830` · **Role** BUILDER · **Built** 2026-08-30
**Implements** `HARDENING_SPEC.md` (this directory), all sections.
**Status of the artefacts: NOT CERTIFIED, NOT DEPLOYED, NOT ENABLED.** Shadows only.

**Compliance record.** No git command was run. No order, enable, disable, deploy, stop, flatten or
account action was taken. The two running paper deployments were verified **still `Realtime` /
`is_trading: true` after the build** (`ListDeployedStrategies`, read-only) — see §7. The certified
sources were opened **read-only** (`open(..., "rb")` in the builder) and their sha256 digests are
**identical before and after** the build (§1). Writes went only to
`runs/G2_LIVE_HARDENING_20260830/` and the two new `.cs` files.

Every claim below is tagged **VERIFIED(source)** or **INFERRED(reasoning)**. No web content was
consulted for this build; all API facts come from reflection against **this install** via
`LookupNinjaScriptSymbol` / `SearchNinjaScriptSymbols` (§6), and all behavioural facts come from the
certified sources and from `HARDENING_SPEC.md`.

---

## 1. Objects and digests

| file | sha256 | lines | bytes |
|---|---|---|---|
| `…\Strategies\WeeklyEdgeP1PCT_v1.cs` (certified, **untouched**) | `ee4c765bc5cab23096f4009943ef6a79e03c3d2d7c671a2285f6cec2676e87b2` | 555 | 28,809 |
| `…\Strategies\WeeklyEdgeXMConflict_v2.cs` (certified, **untouched**) | `2ec00dd4d0a11b999b649dcf358b63f92bc09f4edf1d2cec77c076b64c910dde` | 369 | 20,994 |
| **`…\Strategies\WeeklyEdgeP1PCT_v2.cs` (new)** | `ff3405c69bc53257dd2131233dd84051677ea45d0ad9bb3a138f2fabb3a80709` | 1,223 | 70,524 |
| **`…\Strategies\WeeklyEdgeXMConflict_v3.cs` (new)** | `2d229168a469a6e4f479956ae671bf9964d68de84835b6107a3eaba551d574a3` | 1,131 | 66,057 |

`…\Strategies\` = `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\`.

The two certified digests match the ones recorded in `HARDENING_SPEC.md` §1 (`ee4c765b…`,
`2ec00dd4…`). **VERIFIED(hash, before and after the build).**

Line endings are preserved per file: P1 is **CRLF**, XM is **LF**, no BOM in either.
**VERIFIED(byte count of `\r\n` before and after).** The builder normalises to `\n` internally and
restores the original convention on write, so certified lines are byte-identical *including* their
line terminator.

Build artefacts written to this run directory:

- `src/build_hardened.py` — the deterministic builder. Re-running it reproduces both files exactly.
- `WeeklyEdgeP1PCT_v2.diff.txt`, `WeeklyEdgeXMConflict_v3.diff.txt` — unified diffs vs the certified
  files (`n=2` context).

---

## 2. METHOD — why the diff is "additions only"

The instruction was: start from a byte copy, change **only** the class name, the `Name`/`Description`
strings, and **add** the hardening blocks; every existing line of trading logic stays
character-identical, checked by a line diff.

`HARDENING_SPEC.md` asks for three things that naively require *editing* certified lines. Each was
implemented by **wrapping** rather than rewriting, so no certified line moves:

| spec item | naive edit | what was built instead |
|---|---|---|
| **HD-07 TRAP 1** — gate the order site | append `&& EntriesAllowed()` to the `else if` header (P1 `:496`, XM `:320`) | keep the header **verbatim**; insert `if (!EntriesAllowed()) { NoteBlockedEntry(); } else {` **before** the certified order statement and a closing `}` **after** it. Same semantics, zero certified lines touched. |
| **HD-05** — fix the instrument-month guard | "replace the certified loop body" (XM `:178-187`) | leave the certified loop **verbatim** and run `HdInstrumentGuard()` **after** it. The certified loop only ever *sets* `instrumentMismatch = true`, so a strictly stronger test appended afterwards is logically identical to replacing it with the conjunction — and strictly stronger. |
| **HD-12** — dead-secondary escape hatch | replace `for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;` (XM `:235`) | leave that line **verbatim** and insert `HdDeadSeriesObserver()` on the line **before** it. The observer evaluates all three `i`, logs, optionally flattens, and then falls through to the untouched certified `return` — on exactly the same bars. |

Same trick for `ExportStampUtc` (HD-13): the certified `new StreamWriter(..., "we_p1pct_" + Tag +
".csv")` / `"we_xm_" + Tag + ".csv"` statement is wrapped in an `if (ExportStampUtc) { … } else {`
… `}` so that at the default `false` the certified statement is the one that runs, verbatim.

### 2.1 The diff result — measured, not asserted

`difflib.SequenceMatcher` over the certified vs hardened line lists, treating any `replace`/`delete`
opcode as "a certified line was not preserved":

| file | certified lines **not** preserved byte-identically | added lines | removed lines |
|---|---|---|---|
| `WeeklyEdgeP1PCT_v2.cs` | **2** | **668** | **0** |
| `WeeklyEdgeXMConflict_v3.cs` | **2** | **762** | **0** |

The four non-preserved lines are exactly the four the instruction permits:

```
P1  cert L71   -  public class WeeklyEdgeP1PCT_v1 : Strategy          ->  ..._v2 : Strategy
P1  cert L171  -  Name = "WeeklyEdgeP1PCT_v1";                        ->  ..._v2";
XM  cert L86   -  public class WeeklyEdgeXMConflict_v2 : Strategy     ->  ..._v3 : Strategy
XM  cert L136  -  Name                      = "WeeklyEdgeXMConflict_v2";  ->  ..._v3";
```

**`Description` was NOT edited.** Both certified `Description = …` statements are byte-identical; the
hardening note is appended on an **added** line (`Description = Description + "  HARDENED SHADOW …"`)
inside `SetDefaults`. This keeps the certified string literal intact while still changing the
displayed description as instructed.

`Tag` defaults are unchanged (`"p1pct"`, `"xm2"`), so the per-bar export filenames
(`we_p1pct_p1pct.csv`, `we_xm_xm2.csv`) are identical between the certified and hardened classes and
the V2a byte-compare works as the spec designed it.

---

## 3. EVERY ADDED BLOCK, WITH LINE RANGES

Line numbers are **in the new files**. `certL` is the certified line the block was anchored to.
Mechanism codes are `HARDENING_SPEC.md` §0.1: **M1** State.Realtime gate · **M2** event that never
fires historically · **M3** platform property with realtime-only semantics · **M4** branch
unreachable with the certified parameter set.

### 3.1 `WeeklyEdgeP1PCT_v2.cs` (1,223 lines; 668 added, 2 changed, 0 removed)

| # | new lines | cert anchor | item | mech | what it is |
|---|---|---|---|---|---|
| 1 | **1–22** | before L1 | header | — | New provenance header. The certified header follows at L23–47, unmodified. |
| 2 | *93* (**changed**) | L71 | identity | — | `public class WeeklyEdgeP1PCT_v2 : Strategy` |
| 3 | **118–125** | after L95 | HD-05/06/08/09/13 inputs | — | `RollLeadDays`(8) `WarmupCertDir`("") `DiagDir`("") `ExportStampUtc`(false) `TraceOrdersLive`(false) `ExpectInstrument`("") |
| 4 | **194–751** | after L163 | THE HARDENING REGION | — | fields + all methods; broken out in §3.3 |
| 5 | *759* (**changed**) | L171 | identity | — | `Name = "WeeklyEdgeP1PCT_v2";` |
| 6 | **776–810** | after L187 | HD-09/HD-10 + defaults | M3 | `Description +=` note; the six new inputs' defaults; the eight declared platform properties; the explicit **omissions** as comments |
| 7 | **817–818** | after L193 | HD-11, HD-05 | M4 | `HdConfigAssert(); HdInstrumentGuard();` in `State.DataLoaded` |
| 8 | **824–828, 830** | around L199 | HD-13 | M4 | `ExportStampUtc` wrapper; certified `StreamWriter` line at 829 verbatim |
| 9 | **836–853** | before L205 | HD-07/08/14 + **V2c falsifier** | M1 | `else if (State == State.Transition)` and `else if (State == State.Realtime)` branches; each opens with `Print("HARDENING-STATE-MARK " + State)` |
| 10 | **857** | after L207 | HD-13 | — | `HdCloseWriters();` in `State.Terminated` |
| 11 | **897–898** | after L246 | HD-06/07/13 | M1 | `HdRealtimeBarHook();` — first statement after the certified `BarsInProgress` guard |
| 12 | **912–913** | before L260 | HD-03 | — | `int hdAct0 = pendingAct, hdSize0 = pendingSize, hdQty0 = myQty;` — **copies taken before** the certified settlement block |
| 13 | **931–934** | after L276 | HD-03, HD-04 | M1 | `ObserveSettlement(hdAct0, …, Open[0]); AssertLedgerMatchesStrategyPosition(myQty);` |
| 14 | **941** | after L282 | HD-15 | M1 | `HdSessionEndStaleCheck(pyTs, firstBar);` |
| 15 | **1143–1144** | after L483 | HD-13 | M1 | `HdDiagRow("SESSFLAT", …)` as the first statement of the certified `lastBar && myQty > 0` branch |
| 16 | **1159–1164, 1166** | around L498 | **HD-04/06/07/11 — THE GATE** | M1 | `if (!EntriesAllowed()) { NoteBlockedEntry(); } else {` … `}` wrapping the certified `EnterLong` statement at 1165, verbatim |

### 3.2 `WeeklyEdgeXMConflict_v3.cs` (1,131 lines; 762 added, 2 changed, 0 removed)

| # | new lines | cert anchor | item | mech | what it is |
|---|---|---|---|---|---|
| 1 | **1–22** | before L1 | header | — | New provenance header; the certified v2-diff note and header follow at L23–94, unmodified. |
| 2 | *108* (**changed**) | L86 | identity | — | `public class WeeklyEdgeXMConflict_v3 : Strategy` |
| 3 | **125–131** | after L102 | inputs | — | `RollLeadDays`(8) `WarmupCertDir`("") `DiagDir`("") `ExportStampUtc`(false) `TraceOrdersLive`(false) `EmergencyFlattenOnDeadSeries`(**true**) |
| 4 | **158–823** | after L128 | THE HARDENING REGION | — | §3.3 |
| 5 | *831* (**changed**) | L136 | identity | — | `Name = "WeeklyEdgeXMConflict_v3";` |
| 6 | **854–873** | after L158 | HD-09/HD-10 + defaults | M3 | as P1 #6 |
| 7 | **881** | after L165 | HD-09 | M4 | `TraceOrders = TraceOrdersLive;` inside the **existing** `State.Configure` branch, after the three `AddDataSeries` calls |
| 8 | **905–907** | after L188 | **HD-05**, HD-11 | M4 | `HdInstrumentGuard(); HdConfigAssert();` — **after** the certified verification loop, which is untouched |
| 9 | **913–915, 917** | around L194 | HD-13 | M4 | `ExportStampUtc` wrapper; certified `StreamWriter` line at 916 verbatim |
| 10 | **926–943** | before L203 | HD-07/08/14 + **V2c falsifier** | M1 | Transition / Realtime branches |
| 11 | **947** | after L205 | HD-13 | — | `HdCloseWriters();` |
| 12 | **977–978** | after L234 | **HD-12** | M1 | `HdDeadSeriesObserver();` — **immediately before** the certified `for (…) if (CurrentBars[i] < 1) return;` at 979 |
| 13 | **980–981** | after L235 | HD-06/07/13 | M1 | `HdRealtimeBarHook();` |
| 14 | **988–989** | before L242 | HD-03 | — | `int hdAct0 = pendingAct, hdQty0 = Math.Abs(myPos) * Qty;` |
| 15 | **1006–1008** | after L257 | HD-03, HD-04 | M1 | `ObserveSettlement(…, Opens[NQ][0]); AssertLedgerMatchesStrategyPosition(myPos * Qty);` |
| 16 | **1019** | after L267 | HD-15 | M1 | `HdSessionEndStaleCheck(ts, firstBar);` |
| 17 | **1025** | after L272 | HD-13 `XMAGE` | M1 | `HdXmAgeRow("ANCHOR", ts);` inside the 09:31 anchor branch |
| 18 | **1040** | after L286 | HD-13 `XMAGE` | M1 | `HdXmAgeRow("DECISION", ts);` inside the 09:45 decision branch |
| 19 | **1076–1080, 1083** | around L322–323 | **THE GATE** | M1 | `if (!EntriesAllowed()) { NoteBlockedEntry(); } else {` … `}` wrapping the two certified order statements at 1081–1082, verbatim |
| 20 | **1103–1104** | after L342 | HD-13 `SESSFLAT` | M1 | `HdDiagRow("SESSFLAT", …)` as the first statement of the certified clock-exit branch |

### 3.3 Inside the hardening region (P1 194–751 / XM 158–823)

Contents are identical in both files except where noted. Every method's **first executable
statement** is its inertness gate.

| block | item | mech | notes |
|---|---|---|---|
| shadow-ledger fields `shFilled shAvgPx shTerminal shState shError shNetQty` | HD-01 | M1 | none of these is a certified field |
| latch fields `haltEntries haltReason firstRealtimeBarSeen entriesBlockedUntilAgree configFault hdBlockedLoggedFor` | HD-02/03/04/11 | — | **all default to NOT BLOCKING** (spec §0.2 inversion rule) |
| `rollBlockFrom(MaxValue) rollResolved rollAlertedFor` | HD-06 | — | |
| `warmupBlocked(false) warmupRows warmupVerdict("GO")` | HD-07 | — | default not blocking |
| `hdDiag hdDiagDay hdStaleLoggedFor` | HD-13/15 | — | |
| `hdDeadFlattenSubmitted` (**XM only**) | HD-12 | — | one-shot guard so the flatten is submitted at most once |
| `HdPrefix / LogInfo / LogWarn / LogErr` | HD-08 | — | `Log(string, LogLevel)` primary, `Print` secondary — the Control Center Log tab is the only reviewable-after-the-fact channel for a headless account strategy |
| `HdAlert` | HD-08 | M1 | returns unless `State.Realtime` (alert.htm: calls in any other State are silently ignored) |
| `Halt` | HD-02/03/04/11 | — | one-way latch on `haltEntries`; **blocks new entries only** |
| `ResetShadow` | HD-01 | — | |
| **`EntriesAllowed()`** | the gate | **M1** | `if (State != State.Realtime) return true;` then `haltEntries`, `warmupBlocked`, `entriesBlockedUntilAgree`, `RollBlocked()` |
| `NoteBlockedEntry` | HD-13 | M1 | one log line per bar, never more |
| `OnExecutionUpdate` override | HD-01 | M1 | matches on `execution.Name`; uses only passed-by-value `quantity`/`price`/`marketPosition`; never reads `Position.Quantity` |
| `OnOrderUpdate` override | HD-02 | M1 + M2 | `IsBacktestOrder` → `GetRealtimeOrder`; branches on `order.OrderState`, logs the `orderState` parameter; only Filled/Rejected/Cancelled treated terminal; **partial fill latches, never adjusts** |
| `OnPositionUpdate` override | HD-13 | M1 | log only, never drives logic |
| `ObserveSettlement` | HD-03 | M1 | qty mismatch → `Halt`; **price mismatch → log only** |
| `AssertLedgerMatchesStrategyPosition` | HD-04 | M1 | compares against **`Position`**; `PositionAccount` appears **in the log string only**; three-way ledger/Position/`shNetQty`; first realtime bar blocks-until-agree (self-healing), later mismatches latch |
| `HdAccountPositionString` | HD-04 | — | try/catch around `PositionAccount` |
| `ResolveRollDates(DateTime)` | HD-06 | M1 | **never called in a backtest**, so `GetNextRolloverDate` is never invoked; takes the **minimum** rollover date across `BarsArray` and subtracts `RollLeadDays` |
| `RollBlocked()` | HD-06 | M1 | short-circuits on `State` |
| `WarmRow / ReportWarmup / WriteWarmupCertificate` | HD-07/08 | M1 + `""` default | GATE/SPEC/MIN/OBSERVED/PASS table **printed by the program**; certificate filename UTC-stamped so restarts cannot overwrite |
| `HdDiagRow / HdCloseWriters` | HD-13 | M1 + `""` default | separate `we_<Tag>_hardening_<yyyyMMdd>Z.csv`; the certified export format is untouched |
| `IsMine` | HD-01/02 | — | P1: `"L" "XL" "XLsess"` · XM: `"XM_L" "XM_S" "XM_X" "XM_DIS"` |
| `HdBarTime / HdBarTimeString` | — | — | P1 uses `Time[0]`; **XM uses `Times[NQ][0]`** — the certified file's ban on unindexed accessors is respected throughout the hardening code |
| `BuildWarmupTable` | HD-07 | — | **P1**: `sigma_diffs`(460/30) `tilt_sessions`(51/51) `bmom_rth_days`(14/14) `rng_sessions`(60/20) `atr_bars`(14/14) `volnorm_bars`(240/30) **`qual_entries`(QualWindow 250 / QualMinHist 100, observed `qCount`)** · **XM**: `xm_hist_ES/RTY/YM`, each `SigmaLookback 60 / SigmaMinHist 20`, observed `hist[i].Count` — **per series, never aggregated** |
| `HdEnvRows / HdLogTemplate` | HD-08/14 | — | history measured with `Bars.Count`, `Bars.GetTime(0)`, `CurrentBar(s)` — **never deep bar indexing**; logs `TradingHours.Name` (closes AUDIT E2 from the inside), per-series instrument + expiry for XM |
| `HdConfigAssert` | HD-11 | M4 | `Calculate`, `EntriesPerDirection`, `IsUnmanaged`, 1-Minute period (XM also every `BarsArray[i]`); latches through `haltEntries`, so **exits still run** |
| `TryParseWanted` | HD-05 | — | `"ES 09-26"` → root/mm/yy; `"ES"` alone is *not parseable* and is a fault |
| `HdInstrumentGuard` | HD-05 | M4 | **XM**: clause (a) `MasterInstrument.Name` equality, (b) `Expiry.Month`/`Year % 100`, (c) every secondary on the **same contract month as the primary**; emits one report line naming all four series and their expiries (this is the V2d artefact). **P1**: clause (b) only, against `ExpectInstrument`, default `""` = disabled |
| `HdDeadSeriesObserver` (**XM only**) | HD-12 | M1 | logs, then flattens **only if** `myPos != 0 && EmergencyFlattenOnDeadSeries`; **the ledger is deliberately not adjusted**, so a permanent `RECONCILE-BREAK` is the intended visible state |
| `HdRealtimeBarHook` | HD-06/07/13 | M1 | `ResolveRollDates` → warm-up re-arm → `LATE` diagnostic (>90 s) → one `ROLL-BLOCK` error per date |
| `HdXmAgeRow` (**XM only**) | HD-13 | M1 | per-series timestamp, age in minutes, close, at the anchor and the decision — the D1 measurement |
| `HdSessionEndStaleCheck` | HD-15 | M1 | **detect only**; `sessionEndTs` is never re-derived |

---

## 4. §4 PLATFORM PROPERTIES — what was declared and what was deliberately omitted

Declared in `State.SetDefaults` (both files):

```csharp
RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;   // NT8 default, explicit
ConnectionLossHandling      = ConnectionLossHandling.StopStrategy;     // CHANGE from Recalculate
DisconnectDelaySeconds      = 10;                                      // install default, explicit
NumberRestartAttempts       = 0;                                       // CHANGE from 4
StartBehavior               = StartBehavior.WaitUntilFlat;             // NT8 default, explicit
IsAdoptAccountPositionAware = false;
IsUnmanaged                 = false;
IgnoreOverfill              = false;
```

and in `State.Configure`: `TraceOrders = TraceOrdersLive;` (property defaults **false**).

**Omitted, on purpose, each recorded as a comment in the source:**

| property | why omitted |
|---|---|
| **`SetOrderQuantity`** | Spec §4 gates it on a **confirmed read-back** of the effective value. That read-back was not obtained. Both strategies pass explicit quantities (`EnterLong(size,"L")`, `EnterLong(Qty,"XM_L")`), so a wrong declaration would silently re-size every trade. *"An undeclared property cannot break identity."* **The V0 gate therefore FAILS-CLOSED to omission.** |
| **`RestartsWithinMinutes`** | `NumberRestartAttempts = 0` already disables restarts; no reason to risk a validation failure. **VERIFIED(reflection): it carries only `BrowsableAttribute` — no `RangeAttribute` — so `0` would in fact have been accepted, but it is still unnecessary.** |
| **`MaximumBarsLookBack`** | Spec HD-16 default recommendation: omit. Not M1/M2/M3, and the equivalent control belongs in the Analyzer's own settings. |
| `Slippage`, `IncludeTradeHistoryInBacktest`, `EntriesPerDirection`, `EntryHandling`, `IsExitOnSessionCloseStrategy`, `IncludeCommission`, `BarsRequiredToTrade`, `Calculate` | **DO NOT TOUCH** — every one is part of the certified object. |

New `[NinjaScriptProperty]` inputs and their inert defaults:

| property | P1 | XM | default | effect at default |
|---|---|---|---|---|
| `RollLeadDays` (int) | ✓ | ✓ | `8` | inert — HD-06 is M1-gated |
| `WarmupCertDir` (string) | ✓ | ✓ | `""` | certificate off |
| `DiagDir` (string) | ✓ | ✓ | `""` | diagnostics off |
| `ExportStampUtc` (bool) | ✓ | ✓ | `false` | certified export filename preserved |
| `TraceOrdersLive` (bool) | ✓ | ✓ | `false` | `TraceOrders` stays at the NT8 default |
| `ExpectInstrument` (string) | ✓ | — | `""` | HD-05 identity check disabled |
| `EmergencyFlattenOnDeadSeries` (bool) | — | ✓ | `true` | inert — M1-gated |

---

## 5. TWO SPEC TENSIONS RESOLVED, AND HOW

Recorded rather than silently decided.

**(a) HD-11 vs §0.2.** HD-11's *"Test"* row hopes a backtest with `Calculate = OnEachTick` produces
**0 trades**. But §0.2 (binding) says every gate flag may only *block* inside an M1 gate, and §0
(governing) requires the backtest to be trade-for-trade identical. Those cannot both hold: a gate
that can stop a backtest is a gate that can break identity.

**Resolution: §0/§0.2 win.** `HdConfigAssert()` runs at `State.DataLoaded` (M4) and **does** emit its
`CONFIG-FAULT` error log in a backtest, but it blocks through `EntriesAllowed()`, which is
M1-gated — so a mis-configured *backtest* still trades while a mis-configured *paper/live* session
does not. **V3-b is therefore verifiable by log inspection, not by trade count.** This is the
conservative direction: the only thing lost is a backtest-visible trade-count signal; the thing
protected is the 100.000 % identity bar. **INFERRED(reasoning), flagged here for the verifier.**

**(b) HD-05's "replace the certified loop body" vs "every certified line character-identical".**
Resolved by appending a strictly stronger guard instead of replacing (see §2). The observable
behaviour is the same — `instrumentMismatch` is `true` iff the certified test **or** the new test
fails — and V3-a's negative test (`EsInstrument="ES 12-26"`) still fires, because clause (b)
compares `Expiry.Month`/`Year` and `"ES 12-26"` resolves to a December contract while the primary is
September. **INFERRED(reasoning); V3-a is its test.**

---

## 6. API FACTS VERIFIED BY REFLECTION AGAINST THIS INSTALL (2026-08-30)

All via `LookupNinjaScriptSymbol` / `SearchNinjaScriptSymbols`, NT8 8.1.8.1, CrossTrade add-on
v1.13.9 (`GetMcpCapabilities`, `fingerprint sha256:b4255f1b0dd7fba1`).

- `StrategyBase` → `RealtimeErrorHandling`, `ConnectionLossHandling`, `DisconnectDelaySeconds`,
  `NumberRestartAttempts`, `RestartsWithinMinutes`, `StartBehavior`, `IsAdoptAccountPositionAware`,
  `IsUnmanaged`, `IgnoreOverfill`, `TraceOrders`, `SetOrderQuantity`, `DaysToLoad` — **all present,
  read/write.** `NumberRestartAttempts` and `RestartsWithinMinutes` carry **only**
  `BrowsableAttribute` (**no `RangeAttribute`**). **VERIFIED.**
- `StrategyBase.GetRealtimeOrder(Order historicalOrder)` → `Order`. **VERIFIED.**
- `OnExecutionUpdate` / `OnOrderUpdate` / `OnPositionUpdate` are **virtual** on `StrategyBase` with
  exactly the signatures used. **VERIFIED.**
- `NinjaTrader.Cbi.OrderState` enum values: `Accepted, Cancelled, Filled, Initialized, PartFilled,
  CancelSubmitted, ChangeSubmitted, Submitted, TriggerPending, Rejected, Working, CancelPending,
  ChangePending, Suspended, AcceptedByRisk, Unknown` — **`Suspended` and `AcceptedByRisk` do exist on
  this install and are absent from the public docs**, which is why no exhaustive `switch` was
  written. **VERIFIED.**
- `NinjaTrader.Cbi.Order` → `Name`, `OrderState`, `Filled`, `Quantity`, `AverageFillPrice`,
  **`IsBacktestOrder` (bool, read-only)**. `IsBacktestOrder` is **only visible with
  `include_inherited:true` and a raised `max_members`** — a truncated reflection dump makes it look
  absent. **VERIFIED (noted because it is an easy false negative).**
- `NinjaTrader.Cbi.Execution` → `Name`, `Quantity`, `Price`, `MarketPosition`. **VERIFIED.**
- `NinjaScript.Log(string, LogLevel)` is **static**; `Print(object)` instance.
  `NinjaTrader.Cbi.LogLevel` = `Alert, Information, Warning, Error`. **VERIFIED.**
- `NinjaScriptBase.Alert(string id, Priority priority, string message, string soundLocation,
  int rearmSeconds, Brush backBrush, Brush foregroundBrush)` — the two `Brush` parameters are
  `System.Windows.Media.Brush`, referenced fully-qualified in the source to avoid any `using`
  ambiguity. `Priority` is **`NinjaTrader.NinjaScript.Priority`** (`High, Medium, Low`), already in
  scope via the certified `using NinjaTrader.NinjaScript;`. **VERIFIED.**
- `MasterInstrument.GetNextRolloverDate(DateTime)` → `DateTime`, public. **VERIFIED.**
- `MasterInstrument.GetInstrumentByDate(Instrument, DateTime, bool, bool, IProgress)` is **static
  with five parameters**, including an `IProgress`. Spec HD-06 says it *"may"* be used for the alert
  text; it was **not used**, to avoid a five-argument call with a progress sink inside a
  realtime hot path. The `ROLL-PLAN` line instead prints each series' `FullName` and its own
  `GetNextRolloverDate`. **VERIFIED(signature) + INFERRED(decision).**
- `Bars` → `Count`, `FromDate`, `ToDate`, `TradingHours`, `GetTime(int)`, `BarsPeriod`,
  `Instrument`. **VERIFIED.**
- `ConnectionLossHandling` = `KeepRunning, Recalculate, StopStrategy`;
  `RealtimeErrorHandling` = `IgnoreAllErrors, IgnoreAllErrorsNoAlert, StopCancelClose,
  StopCancelCloseIgnoreRejects`; `StartBehavior` = `AdoptAccountPosition, ImmediatelySubmit,
  ImmediatelySubmitSynchronizeAccount, WaitUntilFlat, WaitUntilFlatSynchronizeAccount`. Every value
  assigned exists. **VERIFIED.** (`IgnoreAllErrorsNoAlert` exists and is undocumented — **not used**.)

---

## 7. COMPILE RESULT

**Pre-check (local, cheap iteration, not the deliverable).** `csc.exe` v4.0.30319,
`-langversion:5`, referencing `D:\NinjaTrader8\bin\NinjaTrader.Core.dll`,
`NinjaTrader.Gui.dll`, `…\Custom\NinjaTrader.Custom.dll`, `PresentationCore/Framework`,
`WindowsBase`. Both files compiled together → **0 errors, 0 warnings**, `probe.dll` produced.
**VERIFIED(local compile of the exact on-disk bytes).**

**The deliverable: CrossTrade sandbox compile** (`CompileNinjaScript`, `in_memory: true` — writes no
`.dll`, does **not** rebuild `NinjaTrader.Custom.dll`, and therefore cannot disturb a running
deployment).

| class | job id | status | `compiled` | errors | warnings | referenced asm |
|---|---|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v2` | `f56de3c002b04191` | completed (644 ms) | **true** | **0** | **0** | 133 |
| `WeeklyEdgeXMConflict_v3` | `89ae590a4a2b4acf` | completed (619 ms) | **true** | **0** | **0** | 133 |

`dropped_for_dedupe` in both: `NinjaTrader.Vendor`, `CrossTrade`, the six `NinZa*` assemblies,
`RenkoKings_SolarWaveRK_NT8`, and six GUID-named snippet assemblies — the sandbox's documented
reference-dedup behaviour, not a defect. `dropped_tmp_artifacts` and `dropped_guid_named` both empty.

**Scope note, stated plainly:** the sandbox compile was submitted with the source **stripped of
comment blocks** (the code is identical). This was deliberate: transcribing 1,200 lines of
comment-heavy source by hand into a tool argument introduces transcription risk with no compile
value, whereas the local `csc` run compiled the **exact bytes now on disk**. Together the two runs
cover both properties — *the real file compiles* (csc, exact bytes) and *this code compiles inside
the NT8 AppDomain against the live assembly set* (CrossTrade, 133 references).
**VERIFIED(both jobs) + INFERRED(equivalence of the comment-stripped source).**

**No NT8 recompile was triggered.** The files are on disk in the Strategies folder; the types are
**not yet in `NinjaTrader.Custom.dll`**. That is intentional — forcing a full Custom rebuild while
`dep_306e11dfc8eb` and `dep_5a914d070687` are live is not a risk this build was authorised to take.
Resolving the classes (`LookupNinjaScriptSymbol("WeeklyEdgeP1PCT_v2")`) is **spec step V1** and
belongs to the verifier, at a moment of their choosing, per CLAUDE.md §6 *"verify by resolving the
class, not by trusting a compile flag."*

**Running deployments after the build** (`ListDeployedStrategies`, read-only, post-write):

| deployment | class | live state | is_trading | position | active orders |
|---|---|---|---|---|---|
| `dep_306e11dfc8eb` | `WeeklyEdgeP1PCT_v1` | **Realtime** | **true** | Flat 0 | 0 |
| `dep_5a914d070687` | `WeeklyEdgeXMConflict_v2` | **Realtime** | **true** | Flat 0 | 0 |

Both untouched. **VERIFIED.**

---

## 8. WHAT THE VERIFIER MUST STILL DO (not done here)

Nothing in `HARDENING_SPEC.md` §7 beyond V1's file-write was performed. Specifically **not** done:
no `RunStrategyBacktest`, no identity run, no negative test, no `spec.yaml`, no diagnostic build.

Carry-forward notes for whoever runs V0–V5:

1. **V0.1 is still open and it is a gate.** `SetOrderQuantity`'s effective value on this install was
   not confirmed, so it is **omitted** from both classes. If a future read-back confirms `Strategy`,
   declaring it is a *new* build and a *new* identity run — not an edit to these files.
2. **V2c has a concrete falsifier in the code**: both classes `Print("HARDENING-STATE-MARK " +
   State)` on entering `State.Transition` and `State.Realtime`. **The backtest output must contain
   zero such lines.** One line falsifies M1 and invalidates every M1-gated item.
3. **V2e**: with `WarmupCertDir` and `DiagDir` at their `""` defaults the hardened runs must produce
   **no** `warmup_*.csv` and **no** `*_hardening_*.csv`.
4. **V2d**: XM's `HD05 …` log line is emitted at `State.DataLoaded` in *every* run, backtest
   included, and names all four series with their `Expiry` dates — that is the V2d artefact.
   With the certified parameters it must end `-> instrumentMismatch=False`.
5. **V3-b** cannot show 0 trades in a backtest by design — see §5(a). Verify it by the
   `CONFIG-FAULT` log line instead, and record that deviation from the spec's expectation.
6. `runs/G2_LIVE_HARDENING_20260830/src/build_hardened.py` reproduces both files byte-for-byte from
   the certified sources. Re-running it is the cheapest way to confirm the diff claim in §2.1
   independently.

---

*Builder role only. No git command run. No strategy deployed, enabled, disabled, stopped or
redeployed. No order placed. No account touched. No certified file modified — both certified sha256
digests are unchanged. The two new `.cs` files and this run directory are the only things written.*

---

## CONNLOSS REVERT 2026-08-30

**Role** FIXER · **Applies to** the two hardened shadows only. The certified files were opened
**read-only** and are byte-unchanged (digests re-verified below). No git command was run. No order,
enable, disable, deploy, stop, flatten or account action was taken. The two running paper
deployments were verified still `Realtime` / `is_trading: true` **after** the edit (read-only
`ListDeployedStrategies`) and still run the **certified** classes `WeeklyEdgeP1PCT_v1` /
`WeeklyEdgeXMConflict_v2` — the swap is the orchestrator's, not this role's.

### 1. The decision, recorded verbatim

> the build declared `ConnectionLossHandling = ConnectionLossHandling.StopStrategy` and
> `NumberRestartAttempts = 0`. REVERT BOTH to NT8's defaults (i.e. REMOVE the declarations so the
> platform default applies). Rationale: neither strategy has a stop; StopStrategy on a >10s
> disconnect disables the strategy and ORPHANS any open position with nothing to exit it, whereas
> the platform default keeps the strategy alive to run its own exits — and the danger the default
> used to carry (internal ledger diverging from reality on reconnect) is exactly what this build's
> HD-04 invariant now detects, blocking entries while never blocking exits. Fewer declared
> deviations is also fewer ways to differ from the certified object.

This **supersedes the two `// CHANGE from …` rows in §4** of these notes. §4's table is left as the
historical record of what the builder declared; the effective state of the files is this section.

### 2. What was removed — exactly two lines per file, nothing else

Line numbers are **pre-edit**, in the hardened files.

| file | line | removed text |
|---|---|---|
| `WeeklyEdgeP1PCT_v2.cs` | **788** | `ConnectionLossHandling      = ConnectionLossHandling.StopStrategy;    // CHANGE from Recalculate` |
| `WeeklyEdgeP1PCT_v2.cs` | **790** | `NumberRestartAttempts       = 0;                                      // CHANGE from 4` |
| `WeeklyEdgeXMConflict_v3.cs` | **865** | `ConnectionLossHandling      = ConnectionLossHandling.StopStrategy;    // CHANGE from Recalculate` |
| `WeeklyEdgeXMConflict_v3.cs` | **867** | `NumberRestartAttempts       = 0;                                      // CHANGE from 4` |

**`RestartsWithinMinutes` was never declared** in either file — §4 already records it as deliberately
omitted, and a post-edit scan confirms **zero assignment sites** for it in either file. There was
nothing to remove. Likewise **`SetOrderQuantity`** and **`MaximumBarsLookBack`** remain undeclared.

**`DisconnectDelaySeconds = 10` was deliberately KEPT.** It was not part of the decision, it is the
install default stated explicitly, and the instruction was to remove only the two declarations.

Removal was done at **byte level with `splitlines(keepends=True)`**, so the per-file line-ending
convention survives: P1 stayed **CRLF** (1,223 → 1,221 lines, CRLF count 1,223 → 1,221) and XM
stayed **LF** (1,131 → 1,129 lines, CRLF count 0 → 0). No BOM introduced. No other line was
reformatted, reindented or moved.

### 3. Surviving §4 declaration set (both files, after the revert)

```csharp
RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;   // NT8 default, explicit
DisconnectDelaySeconds      = 10;                                      // install default, explicit
StartBehavior               = StartBehavior.WaitUntilFlat;             // NT8 default, explicit
IsAdoptAccountPositionAware = false;
IsUnmanaged                 = false;
IgnoreOverfill              = false;
```

plus `TraceOrders = TraceOrdersLive;` in `State.Configure` (property defaults **false**).
`ConnectionLossHandling` and `NumberRestartAttempts` now take the **platform default** — nothing in
either file assigns them, so nothing in either file can differ from the certified object on them.

### 4. Digests

| file | sha256 before revert | sha256 after revert | lines | bytes |
|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v2.cs` | `ff3405c69bc53257dd2131233dd84051677ea45d0ad9bb3a138f2fabb3a80709` | **`a815da3b8d7a22cae9359af8ece069db3bc5362ee202cf8dfe5b16da2caeafb9`** | 1,221 | 70,306 |
| `WeeklyEdgeXMConflict_v3.cs` | `2d229168a469a6e4f479956ae671bf9964d68de84835b6107a3eaba551d574a3` | **`3b8da2e60b2b799321eadace0e2e35f2741a67f6745162ff7ea13b31274419f0`** | 1,129 | 65,841 |

The two *before* digests are byte-identical to the ones §1 recorded at build time, which is the
proof the edit was applied to the expected object in its expected state.

**CERTIFIED FILES — re-hashed after the revert, UNCHANGED:**

| file | sha256 | expected | verdict |
|---|---|---|---|
| `WeeklyEdgeP1PCT_v1.cs` | `ee4c765bc5cab23096f4009943ef6a79e03c3d2d7c671a2285f6cec2676e87b2` | `ee4c765b…` | **UNCHANGED** |
| `WeeklyEdgeXMConflict_v2.cs` | `2ec00dd4d0a11b999b649dcf358b63f92bc09f4edf1d2cec77c076b64c910dde` | `2ec00dd4…` | **UNCHANGED** |

### 5. Line diff vs the certified sources — re-run after the revert

Same `difflib.SequenceMatcher` measurement as §2.1: any `replace`/`delete` opcode counts as a
certified line not preserved byte-identically.

| file | changed | added | removed | added at build (§2.1) |
|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v2.cs` | **2** | **666** | **0** | 668 → 666 (−2) |
| `WeeklyEdgeXMConflict_v3.cs` | **2** | **760** | **0** | 762 → 760 (−2) |

`changed` is still exactly **2 per file**, and they are still exactly the two the instruction
permits — the class name and the `Name` string:

```
P1  cert L71   -  public class WeeklyEdgeP1PCT_v1 : Strategy          ->  ..._v2 : Strategy
P1  cert L171  -  Name = "WeeklyEdgeP1PCT_v1";                        ->  ..._v2";
XM  cert L86   -  public class WeeklyEdgeXMConflict_v2 : Strategy     ->  ..._v3 : Strategy
XM  cert L136  -  Name                      = "WeeklyEdgeXMConflict_v2";  ->  ..._v3";
```

`removed` remains **0** — no certified line was dropped. The whole delta of this revert lands in
`added`, which falls by exactly 2 per file, confirming the edit touched only builder-added lines.

### 6. Compile

**Local pre-check** — `csc.exe` v4.0.30319, `-langversion:5`, same six references as §7, compiling
the **exact bytes now on disk** for both files together → **0 errors, 0 warnings**,
`probe_revert.dll` produced. **VERIFIED(local compile of the exact on-disk bytes).**

**Deliverable — CrossTrade sandbox** (`CompileNinjaScript`, `in_memory: true`: writes no `.dll`,
does **not** rebuild `NinjaTrader.Custom.dll`, cannot disturb a running deployment):

| class | job id | status | `compiled` | errors | warnings | referenced asm |
|---|---|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v2` | `44293d03432a495e` | completed (605 ms) | **true** | **0** | **0** | 133 |
| `WeeklyEdgeXMConflict_v3` | `b24fb30de60f4d0d` | completed (588 ms) | **true** | **0** | **0** | 133 |

`dropped_for_dedupe` identical to §7's list; `dropped_tmp_artifacts` and `dropped_guid_named` both
empty. As at build time the sandbox source was **comment-stripped** (code identical, generated
mechanically by a literal-aware stripper rather than transcribed by eye); the `csc` run is the one
that compiled the exact on-disk bytes. **VERIFIED(both jobs) + INFERRED(equivalence of the
comment-stripped source).**

**No NT8 recompile was triggered**; the types are still not in `NinjaTrader.Custom.dll`. Resolving
the classes remains spec step V1, the verifier's call.

### 7. One residual flagged, not fixed (out of scope by instruction)

`WeeklyEdgeP1PCT_v2.cs` still carries this **comment** in `State.SetDefaults`:

```
// RestartsWithinMinutes: LEFT AT ITS DEFAULT.  NumberRestartAttempts = 0 already
//   disables restarts; there is no reason to risk a validation failure.
```

Its second clause is now **stale** — `NumberRestartAttempts = 0` is no longer declared, so it no
longer disables anything. `WeeklyEdgeXMConflict_v3.cs` has the milder equivalent
(`// RestartsWithinMinutes / SetOrderQuantity / MaximumBarsLookBack: DELIBERATELY NOT DECLARED`),
which remains true. Both are comments and neither affects behaviour or the diff verdict. The
instruction for this pass was *remove only those two declarations, touch nothing else*, so the
comment was **left exactly as it is** and is raised here for the orchestrator to dispose of rather
than silently rewritten.

*Fixer role only. No git command run. No strategy deployed, enabled, disabled, stopped or
redeployed. No order placed. No account touched. No certified file modified — both certified sha256
digests re-verified unchanged after the edit.*
