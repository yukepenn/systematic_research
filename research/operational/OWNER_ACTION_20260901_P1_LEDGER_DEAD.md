# 🔴 OWNER ACTION — the live P1 leg is trading with a DEAD decision ledger

**Raised 2026-09-01 05:10 ET. Machine-verified, reproducible, not inferred.**
**Live account `2047681`. Strategy `WeeklyEdgeP1PCTMnq_v1`, strategy id `399562885`.**

---

## THE ONE LINE

> P1 on the live account is **trading correctly** but has written **zero** rows to its decision
> ledger since **2026-09-01 00:41 ET**, and will write none until it is restarted. Every health
> check reports green. This is the exact failure mode `CURRENT_LIVE_TRUTH.md` warned about — it
> was believed cleared, and it was not.

**This is an EVIDENCE defect, not a TRADING defect.** `export` is write-only and is never read by
a decision. Orders, sizing, guards and the session box are unaffected.

---

## §1 THE EVIDENCE

Two observations, 3 minutes 42 seconds apart, on four writers that share one code path:

| writer | file | last row @05:00:28 | last row @05:04:10 | verdict |
|---|---|---|---|---|
| **LIVE-MNQ P1** | `C:\NT8_ForwardLogs\mnq\export\we_p1pct_p1pct.csv` | **`00:40:00`** | **`00:40:00`** | 🔴 **DEAD** |
| LIVE-MNQ XM | `C:\NT8_ForwardLogs\mnq\export\we_xm_xm2.csv` | `05:00:00` | `05:04:00` | ✅ healthy |
| PAPER P1 | `C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv` | `05:00:00` | `05:04:00` | ✅ healthy |
| PAPER XM | `C:\NT8_ForwardLogs\export\we_xm_xm2.csv` | `05:00:00` | `05:04:00` | ✅ healthy |

File length is byte-frozen at `33,550,010` across both reads while its three siblings advance.

This was **not** diagnosed from `LastWriteTime` or file length — the source comment at
`WeeklyEdgeP1PCTMnq_v1.cs:1012-1021` explicitly warns that a previous such diagnosis was wrong.
It is diagnosed from **the last data row inside the file**, cross-checked against a sibling
running identical code with `AutoFlush = true` that is current to the minute.

Meanwhile the strategy itself reports, from `ListAllStrategies`:
`state: Realtime` · `isEnabled: true` · `position: Flat` · `currentBars: [354708, 353455]`.
**It is processing bars normally. Only the writer is gone.**

## §2 THE MECHANISM — exact, from source

```csharp
// WeeklyEdgeP1PCTMnq_v1.cs:988
export = new StreamWriter(Path.Combine(ExportDir, "we_p1pct_" + Tag + ".csv"), false);
// :992
catch (Exception) { export = null; }          // ← SILENT. No log line. No health-check effect.
// :1361
if (export != null) { export.WriteLine(...); }   // ← skipped forever after
```

`append:false` means **one process may hold the handle**. There is **no retry** anywhere in the
class: once `export` is null at `State.DataLoaded`, it is null for the life of the instance.

## §3 THE FORENSIC TIMELINE — from `Documents\NinjaTrader 8\log\log.20260901.00000.txt`

| time (ET) | event | consequence |
|---|---|---|
| `00:30:58.588` | Enable `WeeklyEdgeP1PCTMnq_v1/`**`399562883`** — GO, `DaysToLoad 365` | **wins** the P1 file handle, writes normally |
| `00:31:00.660` | Enable `WeeklyEdgeXMConflictMnq_v1/`**`399562884`** — GO, 365 | **wins** the XM file handle |
| `00:31:01.219` | Enable `WeeklyEdgeP1PCTMnq_v1/`**`399562885`** — GO, 365 | 🔴 **collides. `export = null`. Silent.** |
| `00:31:04.014` | Enable `WeeklyEdgeXMConflictMnq_v1/`**`399562886`** — **`NO-GO`**, `DaysToLoad 5`, `xm_hist 3 < 20` | collides *and* was misconfigured |
| `00:40:55.044` | **Disable** `399562884` | releases the XM handle |
| `00:40:56.416` | **Disable** `399562883` | 🔴 **releases the P1 handle — and removes the only P1 writer** |
| `00:40:57.362` | **Disable** `399562886` | — |
| `00:41:32.494` | **Enable** `399562886` — GO, `DaysToLoad 365` | ✅ **re-opens the XM handle. XM recovers.** |
| — | **`399562885` was never restarted** | 🔴 **P1 stays mute. Still mute now.** |

P1's file's last row is `00:40:00`; `399562883` was disabled at `00:40:56`. Exactly consistent.

## §4 🔴 A LOAD-BEARING CLAIM IN `CURRENT_LIVE_TRUTH.md` IS BACKWARDS

> `CURRENT_LIVE_TRUTH.md:27-28` — *"The two paper MNQ validation legs (`399562883` / `399562884`)
> were removed on 2026-09-01 … **Removing them is also what cleared the export-handle collision.**"*

**Removing them did not clear the collision. For P1 it is what caused the outage.**
`399562883` was the *handle holder*; deleting it left the survivor `399562885` — which had already
silently failed to open — as the only instance, with no writer and no retry path.

XM recovered **only** because `399562886` happened to be disabled *and re-enabled* at `00:41:32`
while fixing its unrelated `DaysToLoad = 5` misconfiguration. **P1 got no such accidental restart.**

The belief that the collision was cleared came from observing XM recover and generalising it.
That is the same one-instance-generalisation error recorded in `STATE_20260901.md` §8.

## §5 WHAT IS ACTUALLY LOST — measured, not adjectival

Measured from the orphaned ledger itself (260 sessions, 354,452 rows, 2025-08-31 → 2026-09-01):

| | |
|---|---|
| P1 entry events | **438** |
| **entries per session** | **1.68** |
| bars in position | 42,846 = **12.09 %** of bars |
| entry size mix | 365 × 1 NQ-unit, 73 × 2 NQ-units (16.7 % at size 2) |
| sessions the box stopped | 121 / 260 = **46.5 %** |

At 1.68 entries/session, **the campaign's first real-money fill is more likely than not to occur
today**, and its per-bar decision context would not be recorded by the live leg.

### What is NOT lost — the honest scoping

- **Fills are recoverable.** NT8 records executions independently (`ListExecutions`, `GetExecution`).
- **Diagnostics still work.** `hdDiag` (`HdDiagRow`, `:603-624`) is a **separate** writer, opened
  **lazily** in **append** mode inside a try/catch that does **not** null it permanently.
  `C:\NT8_ForwardLogs\mnq\diag\` is empty only because no realtime diagnostic event has fired yet.
  ⚠️ **CORRECTED 2026-09-01: it retries the OPEN, not the WRITE.** The reopen is gated on
  `hdDiag == null`, so if the open succeeds and a later `WriteLine`/`Flush` throws, `:625`
  swallows it and leaves the handle **non-null** — permanently silent thereafter. "It retries on
  every call" was true of the open and overstated for the write.
- 🔴 **`RECONCILE-BREAK` reaches you via NT8's OWN LOG, not via `hdDiag`.** `Halt` → `LogErr` →
  `Documents\NinjaTrader 8\log\log.*.txt`, independent of both writers. This document originally
  justified the watch item through the weaker channel. **Scan it mechanically:**
  `python -m research_sdk.writer_watchdog --halts` (read-only; exit 1 on any halt or latch).
- **A decision-identical proxy exists.** The paper book's `WeeklyEdgeP1PCT_v3` (`399562881`) runs the
  same parameters on the same `NQ 09-26` feed, and MX01 G3 proved the two classes' decision exports
  byte-identical over 61,600 bars. `C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv` is a valid
  reconstruction source for the live leg's decisions.

**So this is a same-day housekeeping action, not an emergency.** Nothing is at risk; evidence
quality is.

## §6 WHAT I ALREADY DID (safe, no live interaction)

The orphaned ledger is preserved before any restart truncates it (`append:false` rewrites the file):

```
C:\NT8_ForwardLogs\_evidence_backup\we_p1pct_p1pct_ORPHANED_writer_399562883_upto_20260901T0040ET.csv
sha256 177F1779447307B30D59AA4797FE211E0F36215C9189051D7F4E2503F3710C4C
354,453 rows   2025-08-31 18:01:00 → 2026-09-01 00:40:00
```

Truncation on restart is **not** data loss — the 365-day warm-up regenerates the whole historical
ledger — but the backup makes that a verifiable claim rather than a hope.

---

## §7 🔴 THE OWNER ACTION

**Restart the P1 leg on the live account, today, while it is flat and before 09:30 ET.**
Everything below is an owner action in the NT8 UI. **I will not enable, disable or restart a live
strategy, and I have not.**

### Preconditions — all currently true, re-check before acting
- Account `2047681` is **flat**: `positions: []`, `ListOrders → []`, `ListExecutions → []`.
- P1 `399562885` `position: Flat`, `activeOrderCount: 0`.
- Today is **2026-09-01**, which is **before** P1's `blockNewEntriesFrom = 2026-09-08`, so the
  restart resolves an unblocked roll plan. *(See §8 — this is the last clean window.)*

### Steps
1. In **Control Center → Strategies**, find the row `WeeklyEdgeP1PCTMnq_v1` on account `2047681`
   whose parameters are populated (`ExportDir = C:\NT8_ForwardLogs\mnq\export`,
   `ExpectInstrument = NQ 09-26`, `ExpectMnq = MNQ 09-26`).
2. 🔴 **STOP IF THE LEG IS NOT FLAT AT THIS MOMENT.** Disabling a **positioned** leg does
   **not** flatten it, and every stop in this book is synthetic and dies with the strategy — an
   untick while long leaves a naked 3–6 MNQ position with no stop and no 16:39 forced flatten.
   Re-check `ListAllStrategies` → `position: Flat`, `activeOrderCount: 0` **immediately before
   unticking**, not once at the top of the procedure.
   ⚠️ **"Before 09:30 ET" is NOT a safety window.** P1 enters overnight — it is in position on
   **12.09 %** of all bars and entries are gated only from 30 minutes before session end. The
   real precondition is **flat, checked now.**
3. **Untick Enabled.** Wait for the log line `Disabling NinjaScript strategy '…/399562885'`.
4. **Re-tick Enabled** on the *same* row, so the saved parameters are reused.
5. ⚠️ **Enable exactly ONE P1 row.** A second enabled instance re-creates this exact bug. There are
   two stale `Finalized` shells of each class visible to `ListAllStrategies` (see §9) — do not
   enable those.

### Verification (I will run this on request, or you can eyeball it)
- NT8 log shows a fresh `WARMUP START verdict=GO` with `env,DaysToLoad,365` for `p1pct`.
- NT8 log shows `ROLL-PLAN blockNewEntriesFrom=2026-09-08 … [s0=NQU6:2026-09-16 s1=MNQU6:2026-09-18]`.
- Within ~1 minute, `C:\NT8_ForwardLogs\mnq\export\we_p1pct_p1pct.csv` has a **last row at the
  current minute**. That, not file size and not a green health check, is the proof.

### If you would rather not touch it
That is defensible. The cost is bounded and stated: ~4 trading sessions (Sep 1–4; **Sep 7 is Labor
Day**) × ~1.7 entries = **~6–7 real-money entries** recorded without their own decision rows,
reconstructable from the paper proxy. From **2026-09-08** P1 stops taking new entries anyway
(§8), and the post-roll redeploy gives it a fresh writer regardless.

---

## §8 🔴 SEPARATE, SAME-DAY: THE ROLL DATES IN EVERY CURRENT DOC ARE WRONG FOR P1

The machine printed its own roll plan at `00:31:00.664` and again at `00:32:05.580`. This
**closes** the open item "confirm the `ROLL-PLAN` line in the NT8 log" — it is confirmed:

```
[P1] ROLL-PLAN blockNewEntriesFrom=2026-09-08 leadDays=8 earliestStoredRollover=2026-09-16
                                            [s0=NQU6:2026-09-16 s1=MNQU6:2026-09-18]
[XM] ROLL-PLAN blockNewEntriesFrom=2026-09-06 leadDays=8 earliestStoredRollover=2026-09-14
       [s0=NQU6:2026-09-16 s1=ESU6:2026-09-14 s2=RTYU6:2026-09-15 s3=YMU6:2026-09-18 s4=MNQU6:2026-09-18]
```

The guard, from source (`ResolveRollDates`, `:504-533`; `RollBlocked`, `:536-541`):

```csharp
DateTime rd = BarsArray[i].Instrument.MasterInstrument.GetNextRolloverDate(now);  // per series
if (rd < earliest) earliest = rd;                                    // MIN over ALL series
rollBlockFrom = earliest.Date.AddDays(-Math.Max(0, RollLeadDays));   // leadDays = 8
...
return HdBarTime().Date >= rollBlockFrom.Date;      // resolved ONCE, never recomputed
```

**`earliest` is the MINIMUM over every loaded series.** P1 now has **two** series, and `MNQ`'s
stored rollover is **2026-09-18** — two days *after* `NQ`'s.

Therefore, restarting P1 on **2026-09-17**:
`GetNextRolloverDate(09-17)` → NQ = December (09-16 passed), **MNQ = 09-18 (not passed)** →
`earliest = 09-18` → `rollBlockFrom = 09-10` → `09-17 >= 09-10` → 🔴 **BLOCKED ON ARRIVAL.**

> ### The correction
> | | repo currently says | machine-verified truth |
> |---|---|---|
> | P1 safe re-enable | **`≥ 2026-09-17`** ❌ | **`≥ 2026-09-19`** (practically **Mon 2026-09-21**) |
> | XM safe re-enable | `≥ 2026-09-19` ✅ | `≥ 2026-09-19` (practically **Mon 2026-09-21**) |
> | P1 block starts | 09-06 (that is XM's date) | **`2026-09-08`** |
> | XM block starts | 09-06 ✅ | `2026-09-06` |
>
> **Both legs: redeploy on or after Monday 2026-09-21**, onto `NQ 12-26`, `MNQ 12-26`, `ES 12-26`,
> `RTY 12-26`, `YM 12-26` — all series together — and **re-enter `ExpectInstrument = "NQ 12-26"`
> and `ExpectMnq = "MNQ 12-26"`**, which revert to `""` (guard **disabled**) on a fresh deploy.
> `2026-09-19` is a Saturday; the September contracts expire `2026-09-18`, so this is a **redeploy
> onto December**, never a re-enable on September.

`≥ 09-17` was correct for the single-series certified P1. **It became wrong the moment MX01 added
the MNQ execution series, and nobody re-derived it.**

## §9 ⚠️ A SECOND LIVE TRAP — the stale `Finalized` shells

`ListAllStrategies` returns **four** rows for `2047681`: the two live `Realtime` instances **and**
two `Finalized` shells carrying the same ids with **empty parameters**:

```
ExportDir: ""   ExpectInstrument: ""   ExpectMnq: ""   DiagDir: ""   WarmupCertDir: ""
MnqInstrument: "MNQ 09-26"   MnqPerNq: 3
```

If one of these is ever enabled it would **trade real money with both identity guards disabled
(`ExpectInstrument`/`ExpectMnq` empty = guard off), no ledger, no diagnostics and no warm-up
certificate** — and `ListStrategies(account)` returns *these* rows preferentially, which is what
produced the wrong audit recorded in `STATE_20260901.md` §8.

## §10 ⚠️ `StopStrategy(deployment_id)` IS NOT AVAILABLE FOR THESE LEGS

`CURRENT_LIVE_TRUTH.md:115-116` instructs: *"To stop: `StopStrategy(deployment_id)`, not
`DisableStrategy(strategyId)`."* But `ListDeployedStrategies(account="2047681")` returns
`total: 4, deployments: []` — **the MCP deployment registry holds no entry for either live leg**,
because they were enabled through the NT8 UI rather than via `DeployStrategy`. There is no
`deployment_id` to pass. **The NT8 Control Center is the only route.** Corrected in place.

---

## §11 THE DURABLE FIX — offline, no live change

Restarting cures this instance; it does not prevent the next one. Two changes belong in the *next*
challenger class (never a hot edit to a running production object):

1. **Fail loud.** `catch (Exception) { export = null; }` should `LogErr` and set a
   `config_fault` that the warm-up certificate prints. A silent catch on the evidence path is the
   root cause; the collision is only the trigger.
2. **Retry.** Re-attempt the open on the first realtime bar of each session, so an orphaned
   survivor heals itself without an owner action.

Until then, the substitute is external and I am building it: a read-only writer-liveness watchdog
(`research_sdk/writer_watchdog.py`) that compares each export's **last data row** against wall
clock and the strategy's own `currentBar`, and fails loudly. It touches nothing live.
