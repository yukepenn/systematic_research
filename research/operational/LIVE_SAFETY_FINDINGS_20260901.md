# LIVE SAFETY FINDINGS — adversarial review of the live book, 2026-09-01

Produced by a dedicated live-safety prosecution of the real-money book on `2047681`, **after**
the day's clean-up, specifically to attack work I had just done. **Every finding below was
re-verified by me against source before being recorded.** Nothing live was touched.

---

## 🔴 F-A1 — A SECOND LATCHING BUG IN THE LIVE P1 SOURCE. This one blocks TRADING, not evidence.

**Same class as the export-handle bug — a state variable reset on only one path — but the
consequence is that the leg stops taking entries, permanently, on a bogus reason string.**

### The mechanism, verified line by line

`ResetShadow()` (`WeeklyEdgeP1PCTMnq_v1.cs:320`) is called from **exactly one place** — the last
line of `ObserveSettlement`, `:439`. And `ObserveSettlement` returns before it whenever there is
nothing to settle:

```csharp
:428   if (actJustSettled == ACT_NONE) return;      // <-- ResetShadow() never runs
```

The session-close safety net submits a **real order** and then clears the settle flag:

```csharp
:1332  if (lastBar && myQty > 0)
:1337      ExitLong(EXEC, myQty * MnqPerNq, "XLsess", "L");
:1342      myQty = 0; pendingAct = ACT_NONE;          // <-- NOT ACT_EXIT
```

`"XLsess"` **is** an owned order name (`IsMine`, `:635`: `n == "L" || n == "XL" || n == "XLsess"`),
so its fill increments the shadow counter at `:364` — `shFilled += q`. Nothing then zeroes it:
the next bar calls `ObserveSettlement(hdAct0 = ACT_NONE, …)` (the only call site, `:1124`) and
early-returns at `:428`.

### The failure

| step | `shFilled` |
|---|---|
| `XLsess` flattens 3 MNQ at the session's last bar | `3` — **leaked, never reset** |
| next session's entry fills 3 MNQ | `6` |
| settlement bar runs `ObserveSettlement(ACT_ENTER, reqQty = 3, …)` | `:432` `shFilled != reqQty` → |

```csharp
:432  else if (shFilled != reqQty) Halt("PARTIAL-FILL " + shFilled + "/" + reqQty + "; no research semantics");
```

→ **`Halt("PARTIAL-FILL 6/3")` → `haltEntries = true`, a one-way latch (`:314-318`). New entries
blocked for the life of the instance. Exits still work.** The reason string sends the investigator
to the broker and to fill quality. **The cause is in our code.**

### Scope and attribution

- **Reachable when a position survives to the session's last bar.** `ForcedFlatMin = 21` normally
  exits at 16:39 via `"XL"` (`:1346`), which *does* set `ACT_EXIT` and resets correctly. `XLsess`
  is the safety net: **early-close sessions and truncated/gappy sessions.** Low frequency,
  permanent consequence, real money.
- 🔴 **It is NOT an MX01 defect.** The identical structure is in the paper leg
  `WeeklyEdgeP1PCT_v3.cs` (`ResetShadow` `:268`, sole call `:385`, `XLsess` in `IsMine` `:573`,
  `myQty = 0; pendingAct = ACT_NONE;` `:1168`). **It entered with the HD-03 hardening**, and the
  parity-certified base `WeeklyEdgeP1PCT_v1.cs` has no shadow machinery at all. **Both P1 legs,
  live and paper, carry it.**
- ✅ **XM does not.** Every XM exit path sets `pendingAct = ACT_EXIT` (`:1272`, `:1283`), so
  `ResetShadow` always runs.

### What to do — and what NOT to do

**Do not hot-fix it.** Editing a file in `bin/Custom/Strategies` recompiles `NinjaTrader.Custom.dll`
against a running real-money book. The fix (`ResetShadow()` on the `XLsess` path, or making
`ObserveSettlement` reset unconditionally) is one line and belongs in the **next named challenger**,
built and certified offline, deployed only in a window with both legs stopped and flat.

**Meanwhile it is detectable**: `Halt` writes `LogErr` into `Documents\NinjaTrader 8\log\log.*.txt`.
Grep for `PARTIAL-FILL` and `ENTRIES LATCHED`. See F-A2 — that is currently the *only* channel.

## 🔴 F-A2 — A latched leg has no machine-readable surface. The standing watch item is a manual grep.

`HdEnvRows()` (`:672-699`) is the only structured self-report — it feeds the warm-up certificate and
the `TEMPLATE` log line. It emits `bars_count`, `instrument`, `roll_block_from`, `config_fault`,
`mnq_per_nq`, `exec_instrument`… and **does not emit `haltEntries`, `haltReason`, `warmupBlocked`
or `mxExecBlocked`.**

`haltEntries` is announced once, at `:1030`, and **only if it was already set at start**. A halt
latched *after* start — `RECONCILE-BREAK`, `PARTIAL-FILL`, a reject, or F-A1 — surfaces only as a
one-off `LogErr` plus a per-signal `NoteBlockedEntry` warning, both in the raw NT8 log.

Meanwhile: `ListAllStrategies` shows `Realtime / isEnabled: true / Flat`.
`writer_watchdog` shows **ALIVE** — the export keeps writing; only entries stop.
Every acceptance check in `DEPLOY_LIVE.md` passes.

> **At 1.68 entries/session, a latched leg is indistinguishable from a quiet week for as long as
> nobody greps.** `CURRENT_LIVE_TRUTH.md`'s instruction to "read the NT8 log for `RECONCILE-BREAK`
> or `PARTIAL-FILL`" is a **manual watch on a channel with no alarm.**

**Cheap external fix, no recompile:** extend `research_sdk/writer_watchdog.py` to scan the NT8 log
for `HALT`/`PARTIAL-FILL`/`RECONCILE-BREAK`/`ENTRIES LATCHED`/`MX-EXEC-BLOCKED`/`ROLL-BLOCK` and
exit non-zero. **Done — see `--halts` in that module.**

## 🔴 F-A3 — `roll_block_from = never` has a SECOND cause, and it is fail-OPEN

I declared this benign this morning. It is benign **for the case I checked** and not in general.

```csharp
:506   rollResolved = true;                       // set BEFORE the try
       try { ... }
       catch (Exception e) {
:531       LogErr("ROLL-RESOLVE-FAILED " + e.Message);
:532       rollBlockFrom = DateTime.MaxValue;     // <-- guard DISABLED
       }
:539   if (rollBlockFrom == DateTime.MaxValue) return false;   // never blocked
```

`rollResolved` latches **before** the `try`, so **a single throw disables the roll guard
permanently for that run** and prints `roll_block_from = never` — the same string the benign
write-time artifact prints. The same `never` also appears if NT8's rollover collection has no
December entry (`:519` filters `MinValue`/`MaxValue` out, leaving `earliest == MaxValue`).

> **The discriminator is the NT8 log**: a healthy start prints `ROLL-PLAN blockNewEntriesFrom=…`;
> a failed one prints `ROLL-RESOLVE-FAILED`. **Reading only the certificate cannot tell them apart.**
> This matters most at the **2026-09-21 redeploy**, where the December schedule has never been probed.

## 🔴 F-A4 — The redeploy checklist names the guards but not the parameters that CHOOSE the contracts

`CURRENT_LIVE_TRUTH.md` §ROLL said: re-enter `ExpectInstrument`, `ExpectMnq`, `ExportDir`,
`DiagDir`, `WarmupCertDir` — *"all of them revert to `""` on a fresh deploy."*

**Two errors.**

1. **The series are not selected by those.** They are selected by `MnqInstrument` (P1 `:939`, XM
   `:1006`) and `EsInstrument` / `RtyInstrument` / `YmInstrument` (XM `:995-1006`). The doc named
   only the **guards**, which *check* the choice and do not *make* it.
2. **"all revert to `""`" is FALSE for exactly those.** They revert to hard-coded **September**:
   ```csharp
   MnqInstrument = "MNQ 09-26"; MnqPerNq = 3; ExpectMnq = "";     // P1 :939, XM :1006
   ```
   **An empty box is visibly wrong. `MNQ 09-26` is a plausible pre-filled value a redeployer scrolls
   past** — and after the roll it names an expired contract. Fail-closed but quiet: `MxExecReadiness`
   sets `why = "NO-BAR"` → entries refused, exits ungated, one `LogErr` per bar into the log nobody
   is grepping (F-A2).

Corrected in `CURRENT_LIVE_TRUTH.md` §ROLL.

## ⚠️ F-A5 — Corrections to my own OWNER_ACTION document

- **The restart procedure had no abort clause.** Step 2 was a bare *"Untick Enabled."* Disabling a
  **positioned** leg does not flatten it, and every stop in this book is synthetic — an untick while
  long leaves a naked 3–6 MNQ position with no stop and no 16:39 flatten. The precondition existed
  two documents away; it is now **in the Steps block**.
- **"before 09:30 ET" implied a safety boundary that does not exist.** P1 can and does enter
  overnight — entries are gated only from 30 minutes before session end, and the book is in
  position on **12.09 %** of all bars. Replaced with the real precondition: **flat, now, whenever.**
- **`hdDiag` retries the OPEN, not the WRITE.** `:610` re-enters the open path only while
  `hdDiag == null`. If the open succeeds and a later `WriteLine`/`Flush` throws, `catch (Exception) {}`
  at `:625` swallows it and leaves `hdDiag` **non-null** — permanently silent thereafter. My claim
  "it retries on every call" was true of the open and overstated for the write.
- **`RECONCILE-BREAK` survives via the NT8 LOG, not via `hdDiag`.** `Halt` → `LogErr` → NT8's own
  log file, independent of both writers. I justified the watch item through the weaker channel.

## ⚠️ F-A6 — `EmergencyFlattenOnDeadSeries` is ON by default, submits a real order, and is in no operational doc

`WeeklyEdgeXMConflictMnq_v1.cs:1004` — `EmergencyFlattenOnDeadSeries = true;` — firing at `:812-818`
to `ExitLong`/`ExitShort` on the MNQ series and then `Halt("DEAD-SERIES flatten submitted; ledger
deliberately NOT adjusted")`.

The design is sound and the permanent `RECONCILE-BREAK` is intended. But the parameter appears
**only** in two Tier-2 run directories and in **no** file under `research/operational/`. An operator
seeing an unexplained MNQ exit plus a permanent RECONCILE-BREAK on XM would be told by
`CURRENT_LIVE_TRUTH.md` that the leg "has latched … must be looked at" — true, and it would not tell
them **the strategy flattened on purpose.** Now recorded in `CURRENT_LIVE_TRUTH.md`.

## ⚠️ F-A7 — Three current docs still instruct a STOP through an id that does not exist

`StopStrategy(deployment_id)` cannot be used on these legs —
`ListDeployedStrategies(account="2047681")` returns `total: 4, deployments: []`. I corrected
`CURRENT_LIVE_TRUTH.md` and claimed "corrected in place", but three others still route through it:
`NT8_RUNBOOK.md` (step 3 of the **live** roll procedure), `GENESIS_III_VERDICT.md` (filed under
**failure recovery**, and it explicitly forbids the working alternative), and
`GENESIS_III_OPEN_STATE.md`. Corrected.

## ⚠️ F-A8 — `DEPLOY_LIVE.md`'s acceptance check tells the reader to STOP a healthy live leg

*"`ls C:\NT8_ForwardLogs\live_mnq\export\` → two files … **If either is missing, the handle collided
and that leg is running blind — stop it.**"* The live book writes to `\mnq\`; `live_mnq\` is empty
**by design**. So the check **always** fires and its remedy is a live action on a healthy leg.
The next check reads the same empty directory for `MXEXEC blocked=1`, so it can never see a genuine
execution outage either. Corrected.

## ⚠️ F-A9 — `"never recomputed"` is true within a run, not across a restart

`CURRENT_LIVE_TRUTH.md` states the roll guard "resolves once at strategy start — it is never
recomputed." True **within one run**. An NT8 auto-restart on connection loss re-runs the state cycle
and **re-resolves `ResolveRollDates` with a new `now`**. Harmless in September (a mid-window restart
resolves the same block date) but it is stated as an invariant and is not one. Related: the source
comment at `:950` claims *"`NumberRestartAttempts = 0` already disables restarts"*, and **neither
that property nor `ConnectionLossHandling` is declared anywhere in either live file** — the
deployment record says both were removed. **The platform default governs.**

---

## WHAT SURVIVED THE ATTACK

Recorded because a review that only lists faults is not a review.

- ✅ **`≥ 2026-09-19` is CORRECT**, verified operator by operator. `RollBlocked` `:540` is `>=`, so
  the block date itself is blocked; `ResolveRollDates` `:512-520` takes a strict `rd < earliest` MIN
  across `BarsArray`; `:522` subtracts 8. Boundary table checked from 09-07 through 09-19. The only
  soft spot is **09-18**, where `GetNextRolloverDate`'s `>` vs `>=` on the day itself is unverified
  — and the instruction already forbids 09-18, so it is conservative in the safe direction.
- ✅ **`export` has no reopen path**, confirmed independently: assigned only at `State.DataLoaded`
  `:978-993`; `State.Realtime` `:1028` touches it only if already non-null; every write is guarded.
  Identical in XM. **Nothing short of a strategy-state cycle restores it.**
- ✅ **Truncation on restart is not data loss** — `export` opens at `State.DataLoaded`, *before*
  `State.Historical`, so the 365-day replay rewrites the full ledger.
- ✅ Nothing in the repo instructs an agent to **enable or size** anything.
