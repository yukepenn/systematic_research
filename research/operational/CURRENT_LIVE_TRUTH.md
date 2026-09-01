# CURRENT_LIVE_TRUTH — 2026-09-01 00:45 ET

## 🔴 THE STATUS CHANGED: THE BOOK IS NOW ON REAL MONEY.

**Owner enabled the MNQ book on live account `2047681` on 2026-09-01.**
`LIVE = YES.` Account flat, **$10,206.86**, zero trades so far, zero commission paid.

This file is the **authoritative live-state document**. Verified from the machine, not asserted.
Build record: `runs/MX01_MNQ_EXECUTION_PORT_20260831/`.

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

The two paper MNQ validation legs (`399562883` / `399562884`) were removed on 2026-09-01 after they
had served their purpose. Removing them is also what cleared the export-handle collision.

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

## 🔴 ROLL — red zone `2026-09-06 → 2026-09-18`

The certificate reports `roll_block_from = never`, which is **expected at that instant, not a
defect**: `ResolveRollDates` runs from `HdRealtimeBarHook` on the first realtime *bar*, which is
after the certificate is written. The real ROLL-PLAN line appears in the NT8 log. **Confirm it on
the next session.**

> **Do not re-enable either leg inside 2026-09-06 → 2026-09-18** — the fail-safe latches and blocks
> new entries *permanently* while every health check still reports green.
> Safe re-enable: **P1 ≥ 2026-09-17, XM ≥ 2026-09-19**, on `NQ 12-26` **and** `MNQ 12-26`, all
> series moved together, `ExpectInstrument = "NQ 12-26"`, `ExpectMnq = "MNQ 12-26"`.
> `MxInstrumentGuard` hard-halts if the decision and execution contracts ever differ in month.

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
- To stop: **`StopStrategy(deployment_id)`**, not `DisableStrategy(strategyId)` — the latter returns
  `strategy_not_found` on a strategy simultaneously reported as `Realtime`. Different id spaces.
- **Never hot-edit a production object.** Every alternative is a new named challenger.
- ⚠️ **`ListStrategies(account)` can return an incomplete set** — on 2026-09-01 it returned 2 of 4
  rows and the 2 it returned were stale empty shells, which produced a wrong audit. **Use
  `ListAllStrategies` for any state judgement**, and prefer the warm-up certificate's own
  `env,DaysToLoad` line over inference from bar counts.
