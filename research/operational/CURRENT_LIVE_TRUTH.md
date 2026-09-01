# CURRENT_LIVE_TRUTH — 2026-09-01 05:10 ET

## 🔴 THE STATUS CHANGED: THE BOOK IS NOW ON REAL MONEY.

**Owner enabled the MNQ book on live account `2047681` on 2026-09-01.**
`LIVE = YES.` Account flat, **$10,206.86**, zero trades so far, zero commission paid.
Re-verified 05:04 ET from `ListAllStrategies` / `ListOrders` / `ListExecutions` — all three
independently report no order and no fill has ever been placed on this account.

This file is the **authoritative live-state document**. Verified from the machine, not asserted.
Build record: `runs/MX01_MNQ_EXECUTION_PORT_20260831/`.

> ## ✅ RESOLVED 2026-09-01 09:34 ET — the live P1 ledger is writing again
> The owner disabled `399562885` at `09:33:28.486` and re-enabled it at `09:34:05.206` — same id,
> single row. **All four writers now ALIVE** (`writer_watchdog` exit 0, halt scan clean).
> Verified from the machine, not asserted:
> `WARMUP START verdict=GO` · `DaysToLoad 365` · `config_fault none` · `instrument NQU6` ·
> `exec_instrument MNQU6` · `mnq_per_nq 3` · `WARMUP-CARRY-FLAT ledger=0 strategyPosition=0` ·
> **`ROLL-PLAN blockNewEntriesFrom=2026-09-08 [NQU6:09-16 MNQU6:09-18]`** re-resolved on the first
> realtime bar at `09:35:00.062` — **identical to the pre-restart plan and in the future**, so the
> guard is live and did **not** fail open (see §ROLL on why `never` would have been ambiguous).
>
> ⭐ **Less was lost than forecast.** The restart truncates and regenerates (`append:false`), and
> the 365-day warm-up **replayed the outage window**: the ledger now holds **354,989 rows** against
> **354,453** in the pre-restart backup — **exactly the 536 minutes 00:41 → 09:36**. The decision
> rows for the blind window **exist**. ⚠️ **Their evidence class is downgraded**: they were written
> by historical replay, not at decision time, so they cannot support a committed-before-outcome
> claim. **Immaterial here — zero fills occurred in the window**, so there were no outcomes for
> them to precede. Recorded as a `WRITER_RESTORED` row in `forward_v2/gaps.csv` (chain verifies).
>
> History and forensics: [`OWNER_ACTION_20260901_P1_LEDGER_DEAD.md`](OWNER_ACTION_20260901_P1_LEDGER_DEAD.md).
> Re-check any time: `python -m research_sdk.writer_watchdog --halts` (read-only; exit 1 = alarm).

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
ledger while every health check still reports green.** Give any new MNQ book its own directory.
Never point one at `\mnq\`.

⚠️ **CORRECTED 2026-09-01: this said "no ledger AND NO DIAGNOSTICS". Diagnostics survive.**
`hdDiag` is a **separate** writer, opened lazily in **append** mode, and it re-enters the open
path on every call while it is null — so it self-heals the moment the other holder releases.
Believing otherwise means writing off the diag tree as expected-dead, and it is the only place
`EXEC`/`ORDER`/`FILLPX`/`POS`/`MXEXEC` rows land. ⚠️ **But it retries the OPEN, not the WRITE**:
if the open succeeds and a later `Flush` throws, the catch swallows it and leaves the handle
non-null — permanently silent. And `RECONCILE-BREAK` reaches you via **NT8's own log**, which is
independent of both writers, not via `hdDiag`.

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
> `RTY 12-26`, `YM 12-26` — **all five series moved together.**
>
> 🔴 **THE PARAMETERS THAT SELECT THE CONTRACTS ARE NOT THE ONES THAT GUARD THEM**, and an
> earlier version of this section named only the guards:
>
> | parameter | role | default on a fresh deploy |
> |---|---|---|
> | `MnqInstrument` | **SELECTS** the execution series | 🔴 **`"MNQ 09-26"`** — an EXPIRED contract |
> | `EsInstrument` / `RtyInstrument` / `YmInstrument` | **SELECT** XM's secondaries | 🔴 September strings |
> | `ExpectInstrument` / `ExpectMnq` | only **CHECK** the choice | `""` = guard **DISABLED** |
> | `ExportDir` / `DiagDir` / `WarmupCertDir` | evidence writers | `""` = **write nothing** |
>
> **An empty box is visibly wrong. `MNQ 09-26` is a plausible pre-filled value a redeployer
> scrolls past** — and post-roll it names a dead contract. The failure is quiet: `MxExecReadiness`
> sets `NO-BAR`, entries are refused, exits are not, and one `LogErr` per bar goes to a log nobody
> is grepping. **Set all eight. Then run the acceptance check below.**
>
> ✅ **ACCEPTANCE, after any redeploy — the check that does not go stale:**
> 1. `ListAllStrategies` → P1 `instruments` = `NQZ6` **+ `MNQZ6`**; XM = `NQZ6/ESZ6/RTYZ6/YMZ6`
>    **+ `MNQZ6`**. A live check that does not see `MNQZ6` has verified nothing about execution.
> 2. **Read the new `ROLL-PLAN` line in the NT8 log and ABORT if `blockNewEntriesFrom` is not in
>    the future.** Every hardcoded date in this repo has gone stale; this check cannot.
> 3. 🔴 `roll_block_from = never` is **AMBIGUOUS**. It is benign at startup (the certificate is
>    written before the first realtime bar) **and it is also what a FAILED resolve prints**:
>    `rollResolved` latches *before* the `try`, so one throw disables the roll guard permanently
>    and fail-OPEN. **The discriminator is the log**: `ROLL-PLAN …` = healthy,
>    `ROLL-RESOLVE-FAILED …` = the guard does not exist. The December schedule has never been probed.
> 4. `python -m research_sdk.writer_watchdog --halts` → exit 0.
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
| 🔴 **drawdown** | **See the distribution below.** The old single line — *0.30 × $51,891 = $15,567 = 152.5 %* — is one draw from it, and not the middle one |

### 🔴 THE DISTRIBUTION — `CAP01`, 2026-09-01

`runs/CAP01_CAPITAL_RUIN_20260901/` — stationary bootstrap, sessions resampled as whole units,
20,000 draws, MEASURED cost basis. All four gates reproduce the repo's own recorded
$51,891 / $36,943 / $537,353 exactly. `EVIDENCE STATUS: DISCOVERY_CONSUMED` — in-sample and
post-selection, so **every figure is a LOWER BOUND on risk.**

🔴 **CORRECTED 2026-09-01 — an earlier version of this table said "P(2-yr DD > the whole
account) = 66.2 %" and called it P(losing the account). THAT IS NOT WHAT IT MEANT**, and the
bound beneath it was inverted. `maxDD` is measured peak-to-trough and the modelled path carries
the drift, so a path that makes +$40k and gives back $11k has `maxDD > equity` and has lost
nothing. Full correction: `runs/CAP01B_RUIN_CORRECTION_20260901/`.

**TRUE 2-year horizon (376 traded sessions — CAP01's "504" was 2.68 years), MEASURED basis,
MNQ commission charged:**

| `MnqPerNq` | p50 DD | p90 DD | P(DD > account) | **P(RUIN — equity reaches zero)** | P(margin call) |
|---|---:|---:|---:|---:|---:|
| **1** | 36 % | 58 % | 0.004 | **0.001** | 0.001 |
| **2** | 71 % | 115 % | 0.195 | **0.019** | 0.024 |
| 🔴 **3 — LIVE NOW** | **108 %** | **175 %** | 0.576 | 🔴 **0.065** | **0.082** |

> 🔴 **AND THE ANSWER IS DOMINATED BY THE ASSUMED EDGE, which the first run never varied.**
> At `MnqPerNq = 3`, P(RUIN) over a true two years is **5.4 %** at the honest HIGH edge
> ($1,900/wk), **9.7 %** at the central ($1,450), **21.6 %** at the low ($900) — and
> **60.4 % if the edge is zero.** The campaign's own estimate is a ~70 % chance two years of
> live data cannot distinguish this book from zero, which is why that last row is not academic.
> **The defensible band is 6 %–22 %.**

⚠️ **`P(margin call)` is the operative number, and it is HIGHER than ruin.** Peak exposure of
9 MNQ needs $900 of day margin, so below ~$900 of equity the book cannot post margin and is
liquidated, locking the loss in. Machine-confirmed: `dailyLossLimit = 0`,
`trailingMaxDrawdown = 0` — **no broker-side limit stops it earlier** — and **every stop in this
book is synthetic and dies with the strategy.** There is no structural bound.

⚠️ The un-warmed 37-session cold start is in the pool above. Dropping it (the live book runs
`DaysToLoad = 365`, so it is configured not to reproduce it) gives P(RUIN) **0.017** at 3 MNQ —
**but the warm cut is defined exactly at the trough of the drawdown it removes.** Both are in
the run; neither is quoted alone.

**The comparison nobody had made:** the repo's own **corrected** capital plan is **$75,000–90,000
at full size** (set 2026-08-31, when `$45,000` was retired for being a sample maximum). At 0.30
scale that is **$22,500–$27,000 against a $10,206.86 account** — **the live book is funded at
38–45 % of its own recommended plan.** At `MnqPerNq = 1` the plan needs $7,500–9,000, which the
account does fund, and CAP01 independently agrees (2-yr `P(>100 %) = 0.4 %`).

**Diversification is worth less than it looks:** P1 alone $26,318, XM alone $34,193, sum $60,511,
combined $51,891 — **the pair saves 14 %**. ρ = 0.242 overall, and the five worst sessions in the
record are all joint-loss days.

**Cost eats the RETURN, not the RISK:** NT8 → HOSTILE drops net 18 % ($537k → $442k) and raises
max DD only 4 %.

**No size is recommended by CAP01** — it reports the risk of each. `MnqPerNq` is a deployable
input: resizing needs no rebuild, no recompile and no re-verification, because MX01's G1–G6 hold
for any value. **This is an owner decision and remains open.**

## COSTS — authority is `research/operational/COST_MODEL.md`

**Commission is MEASURED. The spread half of the MNQ estimate is ASSUMED.** Do not quote one
number for both.

| | | evidence |
|---|---|---|
| NQ commission | **$4.36**/ctr RT | MEASURED, Lifetime template |
| MNQ commission | **$1.30**/ctr RT | MEASURED, n = 704 fills |
| per unit of exposure | micros **2.98× dearer** ($13.00 vs $4.36 per NQ-equivalent) | arithmetic |
| 🔴 MNQ **spread** | **NEVER MEASURED** | 🔴 **ASSUMED** equal to NQ in ticks |

> 🔴 **The shipped "≈ $35/wk at 3 MNQ" is the COMMISSION penalty ALONE.** It contains no spread
> term. `research_sdk/cost_model.py` reproduces it exactly and shows the band the unmeasured
> spread leaves open: **−$5.6/wk (MNQ 2 ticks tighter) to +$76.3/wk (2 ticks wider)** — that is
> **−1 % to +28 %** of the $270–570/wk live expectation, decided by an input nobody has measured.
> Evidence points **both ways**: `EXECUTION_REALITY.md:6-7` says MNQ is *wider in ticks at times*;
> one live snapshot on 2026-09-01 05:17 ET measured **NQ 5 ticks vs MNQ 3** — n=1, overnight,
> asynchronous. **UNRESOLVED.** Cheapest closure: poll `GetQuote` on both through one RTH session.

✅ **Closed 2026-09-01:** the `GENESIS_III_VERDICT.md` §H/§I "$20.65 all-in" error **was already
corrected at `cf6f7e8`**; this file previously said "not yet applied", which was stale. $20.65 is
**spread only**; all-in is **$25.01**. ⚠️ A *residual* defect remains one row below it — §H deducts
commission from a baseline that already nets it. See `research/operational/COST_MODEL.md` §4.

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
- ⚠️ **THE FOUR DEPLOYED `.cs` HEADERS STILL SAY `NOT CERTIFIED / NOT DEPLOYED / NOT ENABLED`.**
  That is **false for all four** and it is **deliberately unfixed**: editing a file in
  `bin/Custom/Strategies` triggers a `NinjaTrader.Custom.dll` recompile against a **running
  real-money book**. **The deployment tables in THIS file are authoritative over the source
  comments.** Fix the comments at the next window with both legs stopped and flat.
- ⚠️ **`EmergencyFlattenOnDeadSeries` is ON by default on XM** and submits a **real order**:
  on a dead secondary series it flattens the MNQ position and then deliberately latches
  `RECONCILE-BREAK` with the ledger unadjusted. **That is the design, not a fault** — but until
  2026-09-01 it appeared in no operational document, so an unexplained MNQ exit plus a permanent
  RECONCILE-BREAK would have read as a defect.
- ⚠️ **A green health check does not mean the evidence writer is alive.** Run
  `python -m research_sdk.writer_watchdog` (read-only, exit 1 = alarm). It checks the **last data
  row inside each file** — never file length or `LastWriteTime`, both of which lie
  (`WeeklyEdgeP1PCTMnq_v1.cs:1010-1021`).
- **Never hot-edit a production object.** Every alternative is a new named challenger.
- ⚠️ **`ListStrategies(account)` can return an incomplete set** — on 2026-09-01 it returned 2 of 4
  rows and the 2 it returned were stale empty shells, which produced a wrong audit. **Use
  `ListAllStrategies` for any state judgement**, and prefer the warm-up certificate's own
  `env,DaysToLoad` line over inference from bar counts.
