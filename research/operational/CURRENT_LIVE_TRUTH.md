# CURRENT_LIVE_TRUTH — 2026-09-01 05:10 ET

## 🔴 THE STATUS CHANGED: THE BOOK IS NOW ON REAL MONEY.

**Owner enabled the MNQ book on live account `2047681` on 2026-09-01.**
`LIVE = YES.` Account flat, **$10,206.86**, zero trades so far, zero commission paid.
Re-verified 05:04 ET from `ListAllStrategies` / `ListOrders` / `ListExecutions` — all three
independently report no order and no fill has ever been placed on this account.

This file is the **authoritative live-state document**. Verified from the machine, not asserted.
Build record: `runs/MX01_MNQ_EXECUTION_PORT_20260831/`.

> ## 🔴 OPEN OWNER ACTION — the live P1 leg's decision ledger is DEAD
> `WeeklyEdgeP1PCTMnq_v1` / `399562885` is **trading correctly** but has written **zero** rows
> since **2026-09-01 00:41 ET**. Its export handle was lost to a startup collision and nulled by
> the silent catch at `:992`, which has **no retry path**. Every health check still reports green.
> Trading, sizing and guards are unaffected — this is an evidence defect.
> **Full forensics, measured cost and the exact restart procedure:
> [`OWNER_ACTION_20260901_P1_LEDGER_DEAD.md`](OWNER_ACTION_20260901_P1_LEDGER_DEAD.md).**
> Detect it any time with `python -m research_sdk.writer_watchdog` (read-only; exit 1 = alarm).

---

## THE TWO BOOKS

| account | connection | legs | class | id | state |
|---|---|---|---|---|---|
| **`2047681`** | **Live** | **P1 MNQ** | `WeeklyEdgeP1PCTMnq_v1` | `399562885` | Realtime, flat |
| **`2047681`** | **Live** | **XM MNQ** | `WeeklyEdgeXMConflictMnq_v1` | `399562886` | Realtime, flat |
| `DEMO8383477` | Simulation | P1 NQ | `WeeklyEdgeP1PCT_v3` | `399562881` | Realtime, flat |
| `DEMO8383477` | Simulation | XM NQ | `WeeklyEdgeXMConflict_v4` | `399562882` | Realtime, flat |

**The paper NQ book is the FORWARD-EVIDENCE book and is unchanged.** Its decisions remain
`FORWARD_DECISION_FIRST`; its fills remain `SIMULATED_FILL_NON_EVIDENTIAL` (Tradovate server-side
demo — see `G3_FEEDSEM_01`). **The live book's fills are the first real execution evidence this
campaign has ever had.**

The two extra MNQ legs (`399562883` / `399562884`) were removed on 2026-09-01 after they had served
their purpose.

> 🔴 **CORRECTION 2026-09-01 05:10 — this section previously read "Removing them is also what
> cleared the export-handle collision." That is BACKWARDS, and it was load-bearing.**
> The NT8 log shows `399562883` was enabled at `00:30:58` and **won** the P1 file handle;
> `399562885` — the surviving live leg — was enabled 3 s later at `00:31:01` and **silently failed
> to open it**. Disabling `399562883` at `00:40:56` therefore removed the *only* P1 writer rather
> than clearing anything. **XM recovered only by accident**: `399562886` was disabled at `00:40:57`
> and *re-enabled* at `00:41:32` while fixing an unrelated `DaysToLoad = 5` misconfiguration, and
> that restart re-opened its handle. **P1 got no such restart and is still mute.**
> The original claim generalised one observed recovery (XM) to both legs without checking P1.

## THE LIVE OBJECT — verified from its own warm-up certificate

`C:\NT8_ForwardLogs\mnq\warmup\warmup_xm2_20260901_044132Z.csv` and the P1 pair at `0430`/`0431`:

```
env,DaysToLoad,365                     P1 verdict GO (7/7)   XM verdict GO (3/3, obs 258 vs spec 60)
env,instrument,NQU6                    <- the DECISION instrument
env,exec_instrument,MNQU6              <- the EXECUTION instrument
env,series_0_instrument,NQU6           env,series_4_instrument,MNQU6
env,mnq_per_nq,3   env,qty_nq_units,1  -> 3 MNQ = 0.30 NQ-equivalent
env,instrument_mismatch,False          env,config_fault,none
```

Live series depth: P1 `[354452, 353199]`, XM `[354452, 354391, 348172, 349385, 353199]` — every
series carries a full 365-day load.

**Decision identity to the certified object is EXACT, not approximate**: the per-bar decision
exports are byte-identical, same `sha256`, over 61,600 bars (MX01 gates G1–G6, all PASS).

## LOG DIRECTORY MAP — ⚠️ read before deploying anything else

| path | owner |
|---|---|
| `C:\NT8_ForwardLogs\export\` | paper `DEMO8383477`, certified NQ book |
| **`C:\NT8_ForwardLogs\mnq\`** | **LIVE `2047681`, the MNQ book** — misleading name, correct content |
| `C:\NT8_ForwardLogs\mx01\` | one-off MX01 parity backtests, not live |
| `C:\NT8_ForwardLogs\live_mnq\` | **EMPTY and unused.** Holds `READ_ME_WRONG_DIR.txt` |

🔴 **THE TRAP:** every P1 class writes `we_p1pct_<Tag>.csv` and every XM class writes
`we_xm_<Tag>.csv`, opened with `append:false`. Only one handle can hold each file. The second
strategy to open it **throws into a silent catch, sets `export = null`, and then runs with no
ledger and no diagnostics while every health check still reports green.** Give any new MNQ book its
own directory. Never point one at `\mnq\`.

## 🔴 THE UNVERIFIED PATH — the standing watch item

`AssertLedgerMatchesStrategyPosition` is `State.Realtime`-gated, so **no backtest has ever
exercised it.** It is the guard the unindexed-`Position` defect would have broken, and the fix
(`Positions[EXEC]` / `Positions[MNQ]`) is verified by compile, by IL and by review — **not by a
fill.** The paper MNQ book was removed before it took one, so the **first real fill will be on the
live account with real money.**

> **On the first live entry, read the NT8 log for `RECONCILE-BREAK` or `PARTIAL-FILL`.**
> Neither should appear. Either one means the leg has latched: entries stop, exits still work, and
> it must be looked at before re-enabling.

`DiagDir` is set, so `EXEC` / `ORDER` / `FILLPX` / `POS` / `MXEXEC` rows will land in
`C:\NT8_ForwardLogs\mnq\diag\` on the first realtime event.

## 🔴 ROLL — **this section is the single roll authority.** Every other doc points here.

✅ **The `ROLL-PLAN` line is CONFIRMED from the machine** (`log.20260901.00000.txt`, `00:31:00.664`
and again `00:32:05.580`). The certificate's `roll_block_from = never` was indeed a write-time
artifact, not a defect — `ResolveRollDates` runs on the first realtime *bar*, after the certificate.
**That open item is closed.**

```
[P1] ROLL-PLAN blockNewEntriesFrom=2026-09-08 leadDays=8 earliestStoredRollover=2026-09-16
                                            [s0=NQU6:2026-09-16 s1=MNQU6:2026-09-18]
[XM] ROLL-PLAN blockNewEntriesFrom=2026-09-06 leadDays=8 earliestStoredRollover=2026-09-14
       [s0=NQU6:2026-09-16 s1=ESU6:2026-09-14 s2=RTYU6:2026-09-15 s3=YMU6:2026-09-18 s4=MNQU6:2026-09-18]
```

The guard (`ResolveRollDates` `:504-533`, `RollBlocked` `:536-541`) takes the **MINIMUM** of
`MasterInstrument.GetNextRolloverDate(now)` **over every loaded series**, subtracts
`RollLeadDays = 8`, and **resolves once at strategy start — it is never recomputed.** It refuses
**new entries only**; exits are never gated.

| | date | why |
|---|---|---|
| XM blocks new entries from | **2026-09-06** | min series rollover = `ES 09-14`, −8 |
| P1 blocks new entries from | **2026-09-08** | min series rollover = `NQ 09-16`, −8 |
| **both legs safe again** | **≥ 2026-09-19**, practically **Mon 2026-09-21** | last series rollover is `MNQ`/`YM` `09-18` |

> 🔴 **CORRECTION 2026-09-01 — "P1 ≥ 2026-09-17" was WRONG and is withdrawn.**
> It was correct for the *single-series* certified P1. **MX01 added the MNQ execution series, whose
> stored rollover is `2026-09-18` — two days after NQ's — and nobody re-derived the date.**
> Restarting P1 on 09-17: `GetNextRolloverDate(09-17)` → NQ = December (09-16 passed), **MNQ = 09-18
> (not passed)** → `earliest = 09-18` → `rollBlockFrom = 09-10` → `09-17 >= 09-10` → **blocked on
> arrival, permanently, with every health check green.**
>
> **Do not re-enable either leg inside `2026-09-06 → 2026-09-18`.**
> **Redeploy both legs on or after Monday `2026-09-21`**, onto `NQ 12-26`, `MNQ 12-26`, `ES 12-26`,
> `RTY 12-26`, `YM 12-26` — **all five series moved together** — and **re-enter
> `ExpectInstrument = "NQ 12-26"` and `ExpectMnq = "MNQ 12-26"`**, plus `ExportDir`, `DiagDir` and
> `WarmupCertDir`: all of them revert to `""` on a fresh deploy, and an empty `ExpectInstrument` /
> `ExpectMnq` means the identity guard is **DISABLED**, not lenient.
> `2026-09-19` is a Saturday and the September contracts expire `2026-09-18`, so this is a
> **redeploy onto December**, never a re-enable on September.
> `MxInstrumentGuard` hard-halts if the decision and execution contracts ever differ in month.

**The blackout is the largest single execution cost in the book (~$437/wk full-size).** Trading it
rather than sitting it out is a design problem, not an operational one — see `GENESIS_III_VERDICT.md`
and the successor-roll work; it must never be a hot fix to a running class.

## CAPITAL — the priced risk, recorded

| | |
|---|---|
| account | $10,206.86 |
| max simultaneous exposure | 9 MNQ (P1 size 2 = 6, plus XM = 3), 0.51 % of bars |
| day margin needed | 9 × $100 = **$900** — covered 11.3× |
| initial margin | **never applies**: `ForcedFlatMin = 21` flattens at **16:39 ET**, six minutes inside NinjaTrader's 16:45 ET cutoff. Measured: 0 exposure on all 5,228 bars from 16:40–17:59 across a full year |
| 🔴 **drawdown** | 0.30 × $51,891 = **$15,567 = 152.5 % of the account**. A repeat of the book's own already-observed worst episode (2022-W05 → W17) ends it. **1 MNQ = 50.8 %, 2 MNQ = 101.7 %.** `MnqPerNq` is a deployable input; resizing needs no rebuild and G1–G6 hold for any value |

## MEASURED COSTS

NQ **$4.36**/ctr RT · MNQ **$1.30**/ctr RT → micros are 3.35× cheaper per *contract*, **2.98× dearer
per unit of exposure**. Spread does not degrade (same 0.25 tick, point value scales exactly 1/10),
so all-in ≈ **1.35×**, roughly **$35/wk** at 3 MNQ.

⚠️ Recorded, not yet applied: `GENESIS_III_VERDICT.md` §H/§I treat **$20.65/ctrRT as all-in**; it is
**spread only**. True all-in is **$25.01**, understating NQ friction by ~$59/wk.

## STANDING CONSTRAINTS

- **Never restart a leg while it holds a position** — every stop in this book is synthetic and dies
  with the strategy.
- ⚠️ **There is no `deployment_id` for either live leg.** This section previously said *"To stop:
  `StopStrategy(deployment_id)`, not `DisableStrategy(strategyId)`."* But
  `ListDeployedStrategies(account="2047681")` returns `total: 4, deployments: []` — the MCP
  deployment registry holds **no entry** for either leg, because both were enabled through the NT8
  UI rather than via `DeployStrategy`. **There is no id to pass. The NT8 Control Center is the only
  route**, and starting/stopping is an owner action regardless.
- ⚠️ **Four rows, two strategies.** `ListAllStrategies` returns the two live `Realtime` instances
  **plus two stale `Finalized` shells** carrying the same ids with **empty parameters**
  (`ExportDir ""`, `ExpectInstrument ""`, `ExpectMnq ""`, `DiagDir ""`, `WarmupCertDir ""`).
  🔴 **Enabling a shell would trade real money with both identity guards DISABLED, no ledger, no
  diagnostics and no warm-up certificate.** Always enable the row whose parameters are populated.
- ⚠️ **A green health check does not mean the evidence writer is alive.** Run
  `python -m research_sdk.writer_watchdog` (read-only, exit 1 = alarm). It checks the **last data
  row inside each file** — never file length or `LastWriteTime`, both of which lie
  (`WeeklyEdgeP1PCTMnq_v1.cs:1010-1021`).
- **Never hot-edit a production object.** Every alternative is a new named challenger.
- ⚠️ **`ListStrategies(account)` can return an incomplete set** — on 2026-09-01 it returned 2 of 4
  rows and the 2 it returned were stale empty shells, which produced a wrong audit. **Use
  `ListAllStrategies` for any state judgement**, and prefer the warm-up certificate's own
  `env,DaysToLoad` line over inference from bar counts.
