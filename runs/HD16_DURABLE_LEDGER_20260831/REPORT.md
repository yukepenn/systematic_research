# HD-16 DURABLE LEDGER CHALLENGERS — `P1PCT_v3` / `XMConflict_v4` — PARITY CERTIFIED

2026-08-31. Owner approved "修" (fix it). **Paper only. LIVE real money = NO. `INCUMBENT CHANGE`: the
decision logic is byte-identical; only a realtime-only I/O flush was added.**

## ⚠️ FIRST: A CORRECTION TO MY OWN DIAGNOSIS

I reported *"the export has written 0 bytes in 106 minutes — the per-bar decision ledger is not
producing a durable record"* and called Tier 0 not closed. **That was WRONG, and the error was mine.**

Measured on the **unfixed** class: `we_xm_xm2.csv` = **46,313,472 bytes / 353,766 rows**, current to
the minute. The export was working the entire time.

**A directory-reported size of 0 while a file handle is open is a METADATA ARTIFACT.** Windows does
not update the directory entry until flush/close. `Get-ChildItem`'s `Length` is not evidence about
file contents. **Never diagnose a writer from it again — read the file.**

### What the real exposure was, correctly stated

`StreamWriter` spills its user-space buffer to the OS continuously, so essentially all rows were
already safe. The genuine exposure is only the **un-flushed user-space tail** (~KB, tens of rows),
lost when the process is **killed** rather than closed — i.e. exactly the *"NT8 restart wiped the
strategies"* event already on record. **Worth removing. Not the catastrophe I first claimed.**

## THE CHANGE — one line each

```csharp
// inside  else if (State == State.Realtime)   [HD-16]
if (export != null) { try { export.AutoFlush = true; } catch (Exception) { } }
```

**Placed inside the `State.Realtime` block on purpose.** This file's own M1 claim (header, and
`:834-836`) is that **`Transition`/`Realtime` never occur in a Strategy Analyzer backtest**, with
`HARDENING-STATE-MARK` shipped as the falsifier. Two consequences, both deliberate:

1. **Historical replay stays buffered and fast** — no per-row flush across 353k warm-up bars.
2. **The change is inert in backtest BY CONSTRUCTION**, so trade-for-trade identity is *guaranteed*,
   not merely hoped for — and it is independently verified below.

## PARITY CERTIFICATION — run TWICE (the second time after correcting the comment)

Same engine, window, bars, hours, fill and commission template as the certified runs.
Compared on **7 fields**: entry ts, entry px, qty, P&L, exit ts, exit px, signal name.

| challenger | vs certified | trades | **row differences** | net | **delta** |
|---|---|---:|---:|---:|---:|
| `WeeklyEdgeP1PCT_v3` | `_v2` | 2,439 | **0** | $354,575.96 | **$0.000000** |
| `WeeklyEdgeXMConflict_v4` | `_v3` | 378 | **0** | $182,776.92 | **$0.000000** |

**`HARDENING-STATE-MARK` lines in the backtest output: 0** — the M1 falsifier holds, confirming
`State.Realtime` never fired and the new code was never reached.

Certified source hashes (sha256, first 32):
`WeeklyEdgeP1PCT_v3.cs` **A9CCC2331D78AEA43B1EEFEFF24189D0** ·
`WeeklyEdgeXMConflict_v4.cs` **0360F894724CFD1FE59EB2A3A14D434B**

Bonus finding: the Analyzer's isolated instance does **not** inherit the deploy-time `ExportDir`, so
**backtests cannot contaminate the live forward logs** — verified, mtimes unchanged across four runs.

## DEPLOYED

| leg | class | deployment_id | strategy_id |
|---|---|---|---|
| P1 | `WeeklyEdgeP1PCT_v3` | **`dep_9c51536a7045`** | 399562877 |
| XM | `WeeklyEdgeXMConflict_v4` | **`dep_27ff47e7e3b7`** | 399562878 |

Both warm-up `verdict=GO` (P1 7/7 gates incl. `qual_entries 438/250`; XM `xm_hist ES/RTY/YM 258` each).
`HD05 primary OK … want=NQ 09-26`. Superseded: `dep_8307c94764fd`, `dep_51bf1a7382cb`,
`dep_61ae0a04b910`.

**Swapped ONE LEG AT A TIME**, each verified before touching the next — the lesson from the earlier
half-down incident, where a permitted stop on one leg and a denied stop on the other left the book
running on a single leg for ~3 minutes.