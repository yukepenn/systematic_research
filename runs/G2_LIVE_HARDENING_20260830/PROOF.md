# PROOF — `WeeklyEdgeP1PCT_v2` / `WeeklyEdgeXMConflict_v3` are safe to run

**Run** `G2_LIVE_HARDENING_20260830` · **Role** PROVER · **Executed** 2026-08-30 (13:15–13:25 UTC)
**Objects proved** the two hardened shadow classes built under `BUILD_NOTES.md`.
**Verdict** TEST 1 **PASS** · TEST 2 **PASS** · TEST 3 **PASS with two flagged residuals** · TEST 4 **PASS**.
**Recommendation: CONDITIONAL GO** — see §6. Two configuration items must be settled first; neither is
a code defect and neither can block an exit inside a running strategy.

**Compliance.** No git command was run. No order was placed, modified or cancelled. No strategy was
deployed, enabled, disabled, stopped or redeployed. The two running paper deployments were read
**read-only** (`ListDeployedStrategies`, `ListStrategies`) and are untouched. `WeeklyEdgeP1PCT_v1.cs`
and `WeeklyEdgeXMConflict_v2.cs` were opened read-only. Every backtest ran on NT8's isolated
**Backtest** account. All writes went to
`runs/G2_LIVE_HARDENING_20260830/` (`PROOF.md` + `out/proof/`).
No web content was consulted; every claim is tagged **VERIFIED(source)** or **INFERRED(reasoning)**.

---

## 0. Artefacts produced

| file | what it is |
|---|---|
| `out/proof/rowcmp.py` | the row-identity comparator; prints the gate table from the program |
| `out/proof/inertness_audit.py` | TEST 2; enumerates every hardening block and classifies every read of a blocking flag |
| `out/proof/P1_ROWIDENTITY.txt`, `out/proof/XM_ROWIDENTITY.txt` | the two gate tables |
| `out/proof/TEST2_INERTNESS.txt` | the inertness table |
| `out/proof/{P1,XM}_{cert,hard}.csv` | the 2439 / 378 trade rows, both classes, 14 fields each |
| `out/proof/raw_*.json` | the six raw NT8 results (4 identity + 2 negative-test) |

---

## 1. TEST 1 — ROW IDENTITY (the load-bearing proof) — **PASS**

### 1.1 Method note that changes how the headline number is read — VERIFIED

The certified baselines quoted in the task (`2439 / $354,575.96`, `378 / $182,776.92`) are the
**sum of the closed trade rows**, not NT8's `performance.all.NetProfit`. On this data window
`NetProfit` is larger for P1 (`$356,317.24`) because it carries a **2440th, still-open** position
(`TradesCount = 2440`, `exec_count = 4879 = 2·2439 + 1`) and is *smaller* for XM (`$179,072.56`).
Both interpretations are reported below and both match. **This is not a discrepancy** — it is the
same distinction, measured.

Because `to = 2026-08-30T21:59:59Z` is later today and the NQ 09-26 series is still forming, the
certified classes were **re-run at the same moment** as the hardened ones rather than compared to a
number recorded earlier in the session. Four runs, same ten-minute window, identical settings.

### 1.2 Settings — identical across all four runs, VERIFIED from each run's own trace

`instrument NQ 09-26` (resolved `NQU6`) · `Minute/1` · `from 2022-01-03T00:00:00Z` ·
`to 2026-08-30T21:59:59Z` · `CME US Index Futures ETH` ·
`Standard / 0 slippage / NinjaTrader Brokerage Lifetime` · account `Backtest (isolated, reset)` ·
**`loaded 1647698 bars` in all four runs** · engine `nt8_strategy_analyzer`, NT8 `8.1.8.1`,
fingerprint `sha256:b4255f1b0dd7fba1`.

### 1.3 P1PCT — `WeeklyEdgeP1PCT_v1` vs `WeeklyEdgeP1PCT_v2`

```
GATE                       SPEC                                                OBSERVED                 VERDICT
G1  trade count            hardened == certified                               2439 vs 2439             PASS
G2  core row identity      0 mismatches on (entry_t,exit_t,qty,entry_px,       0 mismatched of 2439     PASS
                           exit_px,pnl)
G3  extended row identity  0 mismatches incl. signal names, order actions,     0 mismatched of 2439     PASS
                           commission, MAE, MFE
G4  closed-trade net       identical to the cent                               354575.96 vs 354575.96   PASS
G5  total commission       identical                                           12814.04 vs 12814.04     PASS
G6  total quantity         identical                                           2939 vs 2939             PASS
G7  engine NetProfit       identical (incl. the open 2440th)                   356317.24 vs 356317.24   PASS
G8  engine TradesCount     identical                                           2440 vs 2440             PASS
G9  bars loaded            identical bar set                                   1647698 vs 1647698       PASS
G10 equity curve           identical point-for-point                           0/2439 points differ     PASS
OVERALL: PASS
```

**Offending rows: none.** All 2439 rows identical across all 14 compared fields.
**Against the task's stated baseline: 2439 trades (spec 2439) and $354,575.96 (spec $354,575.96) — exact.**

### 1.4 XMCONFLICT — `WeeklyEdgeXMConflict_v2` vs `WeeklyEdgeXMConflict_v3`

```
G1  trade count            378 vs 378                 PASS      G6  total quantity     378 vs 378                PASS
G2  core row identity      0 mismatched of 378        PASS      G7  engine NetProfit   179072.56 vs 179072.56    PASS
G3  extended row identity  0 mismatched of 378        PASS      G8  engine TradesCount 379 vs 379                PASS
G4  closed-trade net       182776.92 vs 182776.92     PASS      G9  bars loaded        1647698 vs 1647698        PASS
G5  total commission       1648.08 vs 1648.08         PASS      G10 equity curve       0/378 points differ       PASS
OVERALL: PASS
```

**Offending rows: none.** All 378 rows identical across all 14 fields. Long 198 / short 181 in both.
**Against the task's stated baseline: 378 trades (spec 378) and $182,776.92 (spec $182,776.92) — exact.**

### 1.5 The identity result is not vacuous — a falsification test — VERIFIED

A 100 % match is also what dead code produces. Two independent checks that the hardening is live:

**(a) The added HD-05 guard has teeth.** Re-running the hardened XM with
`EsInstrument = "ES 12-26"` (a wrong contract month) gives **0 trades, 0 executions** — the added
clause fires, sets `instrumentMismatch`, and blocks every entry for four years.
**(b) The certified class does not catch it.** The *certified* `WeeklyEdgeXMConflict_v2` with the
**same** parameter still produces **378 trades / $182,776.92** — its guard tests the root only
(`got.StartsWith(want[i].Split(' ')[0])`), so it silently traded a wrong-month composite.

So the hardening changes behaviour exactly where it is supposed to, and nowhere else. It also closes
a real silent-wrong-data hole in the certified object. (This same mechanism is residual **R2** in §5.)

### 1.6 The M1 claim, measured rather than asserted — VERIFIED

`Print("HARDENING-STATE-MARK …")` output is not returned by the MCP surface, so the builder's V2c
falsifier could not be read directly. A stronger engine-side witness was used instead: NT8's own
per-bucket performance split. In **all four** runs

`performance.realtime.TradesCount = 0`, `realtime.NetProfit = 0.00`, `realtime.TotalQuantity = 0`,
final `state = "Finalized"`.

Every one of the 2439 / 378 trades landed in the historical bucket and none in the realtime bucket —
the engine's own record that the strategy never executed in a realtime state, which is precisely
what M1 depends on.

**V2e also passes:** with `WarmupCertDir` and `DiagDir` at their `""` defaults, a filesystem sweep of
the NinjaTrader tree and the repo found **no** `warmup_<tag>_*Z.csv` and **no** `*_hardening_*.csv`.
(The one `warmup_convergence.csv` hit belongs to the unrelated run `W18R1_M1_VOLSEASON`.)

---

## 2. TEST 2 — INERTNESS AUDIT — **PASS**

Generated by `out/proof/inertness_audit.py`, not assembled by hand. Full table in
`out/proof/TEST2_INERTNESS.txt`. Mechanism codes are `HARDENING_SPEC.md` §0.1.

### 2.1 Blocks whose **first executable statement** is the M1 gate

`WeeklyEdgeP1PCT_v2` — **13 of 32** methods in the hardening region:

| block | line | gate |
|---|---|---|
| `HdAlert` | 250 | `if (State != State.Realtime) return;` |
| `EntriesAllowed` | 275 | `if (State != State.Realtime) return true;` |
| `NoteBlockedEntry` | 285 | `if (State != State.Realtime) return;` |
| `OnExecutionUpdate` | 303 | `if (State != State.Realtime) return;` |
| `OnOrderUpdate` | 324 | `if (State != State.Realtime) return;` |
| `OnPositionUpdate` | 358 | `if (State != State.Realtime) return;` |
| `ObserveSettlement` | 371 | `if (State != State.Realtime) return;` |
| `AssertLedgerMatchesStrategyPosition` | 398 | `if (State != State.Realtime) return;` |
| `ResolveRollDates` | 442 | `if (State != State.Realtime \|\| rollResolved) return;` |
| `RollBlocked` | 474 | `if (State != State.Realtime) return false;` |
| `HdDiagRow` | 541 | `if (State != State.Realtime) return;` |
| `HdRealtimeBarHook` | 703 | `if (State != State.Realtime) return;` |
| `HdSessionEndStaleCheck` | 737 | `if (State != State.Realtime) return;` |

`WeeklyEdgeXMConflict_v3` — **15 of 34**: the same thirteen (lines 217, 242, 252, 270, 291, 325, 338,
365, 409, 441, 508, 757, 810) **plus** `HdDeadSeriesObserver` (728) and `HdXmAgeRow` (787), both
`if (State != State.Realtime) return;`.

### 2.2 Blocks with no M1 gate — each justified, none able to alter a decision

| block | mech | why it is still inert in `State.Historical` |
|---|---|---|
| `HdPrefix` `LogInfo` `LogWarn` `LogErr` | — | `Log`/`Print` only, in `try/catch`; the `Alert` they call **is** M1 |
| `Halt` | M1-by-consumer | writes `haltEntries`, which is read as a branch condition **only inside `EntriesAllowed()`** (M1) |
| `ResetShadow` | — | writes added shadow fields only; no certified field |
| `WarmRow` `TryParseWanted` | — | `static` string formatter / parser |
| `BuildWarmupTable` `ReportWarmup` `HdLogTemplate` | M1-by-caller | every call site is the `State.Transition` / `State.Realtime` branch or `HdRealtimeBarHook` (M1) |
| `WriteWarmupCertificate` | M4 + `""` default | `if (string.IsNullOrEmpty(WarmupCertDir)) return;` |
| `HdCloseWriters` | — | closes a writer that is `null` unless `DiagDir` is set |
| `IsMine` `HdBarTime` `HdBarTimeString` `HdEnvRows` `HdAccountPositionString` | — | read-only, `try/catch` |
| **`HdConfigAssert`** | **M4** | **runs in a backtest** (`State.DataLoaded`); writes `configFault` and `haltEntries`; `haltEntries` is read only inside `EntriesAllowed()` → cannot change a backtest trade. This is the builder's §5(a) tension and it resolves in the conservative direction. |
| **`HdInstrumentGuard`** | **M4** | **runs in a backtest.** P1: returns at once (`ExpectInstrument` default `""`). **XM: the one place added code writes a *certified* field (`instrumentMismatch`).** See §2.4. |

### 2.3 Structural claims — checked mechanically, not by eye

```
C1  every read of haltEntries              P1 L264=LATCH-GUARD  L278=BLOCKING(in EntriesAllowed)  L852=LOG-ONLY(Realtime branch)   PASS
C1  every read of warmupBlocked            P1 L279=BLOCKING(in EntriesAllowed)  L708=REARM(HdRealtimeBarHook, M1)                  PASS
C1  every read of entriesBlockedUntilAgree P1 L280=BLOCKING(in EntriesAllowed)  L416=REARM(AssertLedger…, M1)                      PASS
C1  the same three, XM                     L231/245/942, L246/762, L247/383 — same classification                                   PASS
C2  the gate wraps only entry order sites  P1 wrap at L1164 (one site) · XM wrap at L1080 (one site)                                PASS
C3  added order sites are M1-gated         P1 3 order sites, 0 added · XM 4 order sites, 1 added and it is inside an M1 method      PASS
C4  NO exit is behind EntriesAllowed()     gated exit sites: none, in either file                                                   PASS
TEST 2 VERDICT: PASS
```

**No gate can be true during `State.Historical`.** The chain is short and total: the only construct
in either file that can suppress a certified action is `EntriesAllowed()`, whose *first* statement is
`if (State != State.Realtime) return true;`. Every blocking flag (`haltEntries`, `warmupBlocked`,
`entriesBlockedUntilAgree`, `RollBlocked()`) is read as a branch condition **only** there. Everything
else that mentions those flags is a latch write-guard, a log line inside the `State.Realtime` branch,
or a re-arm inside an M1 method.

### 2.4 The one exception, stated plainly — VERIFIED

`WeeklyEdgeXMConflict_v3.HdInstrumentGuard()` runs at `State.DataLoaded`, which **does** execute in a
backtest, and it can write the certified field `instrumentMismatch` (lines 676, 685, 693, 698, 702,
707, 711). This is the single path by which added code reaches certified behaviour, and its inertness
rests on **M4 (parameter values)**, not on M1 (state). It is safe because:

1. it is **monotone** — the guard only ever sets `instrumentMismatch = true`, never false, so it can
   only be *stricter* than the certified loop it follows (which is left byte-identical);
2. `instrumentMismatch` is read at exactly **one** site, line 1074, the **entry** predicate. Neither
   exit (L1095 disaster stop, L1105 alpha exit) reads it. **VERIFIED by grep across both files.**
   It therefore cannot block an exit;
3. with the deployed parameters it does not fire — the 378-row identity run is that measurement.

### 2.5 Blocking an entry does not corrupt the research object — VERIFIED

The classic failure mode of an entry gate is that the certified accumulators stop advancing, so the
strategy silently becomes a *different* object. Checked at source:

- P1: `qCount++` and all five `q*` accumulator writes are at **L1136–1137**; the gate is at
  **L1159–1166**. The accumulators run first and are never gated.
- XM: `hist[i].Add(r)` is at **L1054**, in the 09:45 decision block; the gate is at **L1080**.
- When blocked, neither `pendingAct`/`pendingSize` (P1) nor `pendingAct`/`pendingDir` (XM) is written,
  so the ledger stays self-consistent and no phantom settlement occurs on the next bar.

---

## 3. TEST 3 — REALTIME PATH REVIEW

Legend: **E-BLOCK** = can block an entry (acceptable) · **X-BLOCK** = can block an exit
(unacceptable) · **X-HELP** = removes an exit blocker.
All of §3 is **INFERRED(reasoning over the source + documented NT8 semantics)** except where marked;
none of it can be measured in the Strategy Analyzer, which is exactly why M1 makes the whole set inert there.

### 3.1 Order rejected

`OnOrderUpdate` → `order.OrderState == Rejected` → `Halt("REJECT …")` → `haltEntries = true`.
`haltEntries` is read only in `EntriesAllowed()`, and `EntriesAllowed()` wraps only the entry site.
→ **E-BLOCK, no X-BLOCK.** Exits at P1 L1146/L1155 and XM L1095/L1105 remain reachable on every
subsequent bar. Platform layer: `RealtimeErrorHandling = StopCancelClose` means NT8 additionally
stops the strategy and **closes** the position on an order error — that *closes*, it does not strand.

### 3.2 Partial fill

`PartFilled` is deliberately not treated as terminal, so `shTerminal` stays false; on the next bar
`ObserveSettlement` sees `!shTerminal` → `Halt("NON-TERMINAL …")`, or `shFilled != reqQty` →
`Halt("PARTIAL-FILL …")`. → **E-BLOCK, no X-BLOCK.** The certified ledger books an assumed *full*
fill while the account holds part; the later `ExitLong(myQty, …)` therefore asks to exit more than is
held. That mismatch **already exists in the certified class** — the hardening does not create it and
does not worsen it; it makes it loud and latched instead of silent. Under the managed approach NT8
reduces such an exit to the actual position rather than reversing. **Net improvement.**

### 3.3 Connection loss — **RESIDUAL R1, the one place I would not sign without an owner decision**

`ConnectionLossHandling = StopStrategy` (builder records this as a **change from `Recalculate`**),
`DisconnectDelaySeconds = 10`, `NumberRestartAttempts = 0` (**change from 4**).

After a 10-second disconnect NT8 **stops the strategy**. `StopStrategy` cancels the strategy's
working orders and stops it; per NT8's documented semantics it does **not** close the position, and
with `NumberRestartAttempts = 0` nothing restarts it. If the disconnect happens while a position is
open, the strategy that would have flattened it at its session clock is no longer running.

This is not an X-BLOCK *inside* a running strategy — `EntriesAllowed()` is not involved and no
hardening branch suppresses an exit. It is an **operational exit-coverage gap**: the exit mechanism
is removed for a class of realtime events that the certified configuration would have survived
(`Recalculate` resumes calculation on reconnect). Under the certified defaults a transient
disconnect self-heals; under the hardened settings it produces a **stopped strategy holding an
orphaned position until a human intervenes.**

Direction of the trade-off, stated fairly: `StopStrategy` is fail-closed against *trading on stale
data*, which is the right instinct. But paired with `NumberRestartAttempts = 0` it is fail-closed on
entries and **fail-open on an open position.** On a DEMO paper account the loss is bounded and the
learning is real; the setting should not be carried to anything funded without an owner decision.

**Verification status:** I could **not** confirm that `Recalculate` and `4` are this install's
effective certified defaults. `ListStrategies` exposes `calculate`, `startBehavior`,
`entriesPerDirection`, `entryHandling` (all four **match** the hardened declarations — no delta) but
**not** `ConnectionLossHandling`, `NumberRestartAttempts` or `RealtimeErrorHandling`. The
"change from" claims are the builder's, carried forward **UNVERIFIED-BY-PROVER**. Inducing a
disconnect to test this would mean touching the running deployments, which is forbidden.

### 3.4 Restart while flat

`State.Realtime` → `BuildWarmupTable()`; if a gate is below its `min`, `warmupVerdict = "NO-GO"` →
`warmupBlocked = true` → **E-BLOCK** until `HdRealtimeBarHook` re-arms it (L708/L762), which it can
do because the accumulators are never gated (§2.5). `AssertLedgerMatchesStrategyPosition` on the
first realtime bar sees ledger 0 == `Position` 0 → `WARMUP-CARRY-FLAT`, no block. `StartBehavior =
WaitUntilFlat` — **VERIFIED identical** to what both live certified strategies report today, so no
delta. → **E-BLOCK only. Safe.**

### 3.5 Restart while holding

First realtime bar: `!firstRealtimeBarSeen` → if `Position` disagrees with the rebuilt ledger,
`entriesBlockedUntilAgree = true` and a `WARMUP-CARRY-NONFLAT` warning. That flag is **self-healing**
(L416/L383 clear it the moment the two agree) and is read only in `EntriesAllowed()`.
→ **E-BLOCK, no X-BLOCK.** The exit path runs on the very first realtime bar if the certified clock
says so. This is a genuine improvement: the certified class carries a silent ledger/position
disagreement with no signal at all.

### 3.6 Contract within N days of expiry

`ResolveRollDates` (first realtime bar only) sets
`rollBlockFrom = min(GetNextRolloverDate over BarsArray) − RollLeadDays(8)`. From that date
`RollBlocked()` is true → **E-BLOCK**, with an explicit source comment and a once-per-date
`ROLL-BLOCK` error log stating *"EXITS ARE NOT GATED"*. Confirmed mechanically by claim **C4**.
→ **E-BLOCK only. Safe.**

**Sub-residual (minor):** `rollResolved` latches on the first call, so `rollBlockFrom` is computed
once at strategy start and never refreshed. After a roll the block never clears by itself and the
strategy will refuse entries until it is restarted. Loud, entry-side, recoverable by redeploy.

### 3.7 A stale added series (XM only) — the one added order

`HdDeadSeriesObserver` runs **immediately before** the certified
`for (int i=1;i<4;i++) if (CurrentBars[i] < 1) return;`. That certified early return sits *above* the
exit logic, so a dead secondary makes `OnBarUpdate` return and **the NQ exit path never runs** —
the ability to close an NQ position is coupled to three unrelated feeds, silently. The observer logs,
and if `myPos != 0 && EmergencyFlattenOnDeadSeries` submits `ExitLong`/`ExitShort` once
(`hdDeadFlattenSubmitted`), then `Halt`s.

→ **X-HELP. This is the single most valuable item in the build** and the only added order site in
either file (claim **C3**: 4 order sites in XM, 1 added, and it is inside an M1 method). It removes
an exit blocker rather than creating one. It is an **exit**, never an entry.

Three bounded caveats:
- It triggers only on `CurrentBars[i] < 1` — a series that never produced a bar. A series that goes
  **stale mid-session** (last bar hours old, `CurrentBars > 1`) does not trigger it — but it does not
  trigger the certified early return either, so the exit path runs normally. **Not a regression**; the
  stale case is measured by `HdXmAgeRow` (log only). *(Today's live `currentBars` are
  `[352670, 352609, 346437, 347670]` — all four series healthy. **VERIFIED**, read-only.)*
- One-shot: if the emergency flatten is itself rejected there is no retry. Still strictly better than
  the certified class, which submits nothing at all.
- The ledger is deliberately not adjusted, so `myPos` stays non-zero and `RECONCILE-BREAK` latches
  permanently — the intended loud state. If the feed later recovers, the certified exit fires a second
  `ExitLong` against a now-flat position; under the managed approach NT8 ignores an exit with no
  position and does **not** reverse. **LOW.**

### 3.8 Could any hardening block throw and abort `OnBarUpdate` before the exit?

This is the only *real* X-BLOCK vector, because `HdRealtimeBarHook` (P1 L897 / XM L981) and
`HdDeadSeriesObserver` (XM L977) are called at the **top** of `OnBarUpdate`, above the exit logic.
Audited call by call:

| call | protected? |
|---|---|
| `ResolveRollDates` | whole body in `try/catch` |
| `(DateTime.Now - Time[0])` late check | `try/catch` |
| `RollBlocked()` → `HdBarTime()` | `try/catch` |
| `LogInfo/Warn/Err` → `Log`/`Print`, `HdAlert` → `Alert` | `try/catch` each |
| `HdDiagRow` | whole body in `try/catch` |
| **`BuildWarmupTable()`** | **not** in `try/catch` — so its inputs were checked directly |

`BuildWarmupTable` is the only unprotected call. **VERIFIED** that it cannot throw a
`NullReferenceException`: P1's `diffs` (L142), `sessCloses` (L146), `rngHist` (L168), `trQ` (L177),
`volQ` (L178) are all initialised **at declaration**, `rthDays`/`qCount` are `int`, and the `rngHist`
loop null-checks `kv.Value`; XM's `hist` is `new List<double>[4]` at L144 and the read is guarded
`(hist != null && hist[i] != null)`. **No exception vector into the exit path.**

### 3.9 TEST 3 summary

| scenario | class | verdict |
|---|---|---|
| order rejected | both | E-BLOCK · safe |
| partial fill | both | E-BLOCK · safe, net improvement |
| **connection loss** | both | **no X-BLOCK in code, but an operational exit-coverage gap — RESIDUAL R1** |
| restart while flat | both | E-BLOCK · safe |
| restart while holding | both | E-BLOCK, self-healing · improvement |
| contract near expiry | both | E-BLOCK · safe (minor latch sub-residual) |
| stale / dead added series | XM | **X-HELP** · removes a real exit blocker |
| exception aborting `OnBarUpdate` | both | none found · safe |

**No hardening block can block an exit.** Claim C4 proves it structurally; §3.8 proves no
exception path reaches it. The only exit-related concern is R1, which lives in the platform
properties, not in the hardening logic.

---

## 4. TEST 4 — REGRESSION ON THE RUNNING PAPER STRATEGIES — **PASS**

`ListDeployedStrategies` (read-only), 13:18 UTC, after all four backtests had run:

| deployment | class | live state | is_trading | position | active orders | current_bar |
|---|---|---|---|---|---|---|
| `dep_306e11dfc8eb` | `WeeklyEdgeP1PCT_v1` | **Realtime** | **true** | **Flat 0** | **0** | 352670 |
| `dep_5a914d070687` | `WeeklyEdgeXMConflict_v2` | **Realtime** | **true** | **Flat 0** | **0** | 352670 |

Both on `DEMO8383477`, `NQ 09-26`, Minute/1, `DaysToLoad 365`, `last_error: null`, unchanged
`current_strategy_id` (`399550060` / `399550061`) and unchanged `last_deployed_utc` (10:48 UTC) —
i.e. **neither was redeployed by this work.** `ListStrategies` additionally confirms
`isEnabled: true`, `calculate OnBarClose`, `startBehavior WaitUntilFlat`, `entriesPerDirection 1`,
`entryHandling AllEntries`, and for XM all four series live (`NQU6 ESU6 RTYU6 YMU6`).
**Nothing was stopped, disabled, redeployed or modified. VERIFIED.**

Note the mechanism that makes this safe: `RunStrategyBacktest` runs on the isolated **Backtest**
account, and the new classes are *new type names*, so resolving them cannot displace the live types.
Each run's trace confirms the resolved type by name — no stale-type risk (CLAUDE.md §6).

---

## 5. RESIDUALS — what a GO would be accepting

| id | item | severity | who decides |
|---|---|---|---|
| **R1** | `ConnectionLossHandling = StopStrategy` + `NumberRestartAttempts = 0`: a >10 s disconnect while holding leaves a stopped strategy with an orphaned position. The "changed from `Recalculate`/`4`" claim is **UNVERIFIED-BY-PROVER** — the tool surface does not expose those properties. | **MEDIUM** | owner |
| **R2** | XM's HD-05 clause (c) requires every secondary on the **same contract month as the primary**. At the Sep→Dec roll, updating only the deployment's instrument leaves `EsInstrument/RtyInstrument/YmInstrument` at `"… 09-26"` and **all entries stop**. Measured: hardened = 0 trades, certified = 378 trades on the same input (§1.5). Fail-closed and loud, but it is a new entry-stopping condition and a roll-day checklist item. | **LOW-MED** | operator checklist |
| **R3** | `rollResolved` latches at start; `rollBlockFrom` never refreshes, so a post-roll entry block clears only on restart (§3.6). | **LOW** | operator |
| **R4** | `SetOrderQuantity` remains undeclared (builder's V0.1, deliberately fail-closed to omission). Correct call; it stays open. | **LOW** | owner |
| **R5** | This run directory has **no `spec.yaml`**, which CLAUDE.md §4 requires *before results exist*. I did not write one — backdating a pre-registration after the results are in would be worse than recording the gap. **Recorded as a governance debt, not repaired.** | **process** | owner |

---

## 6. RECOMMENDATION — **CONDITIONAL GO**

**On the evidence, the hardened classes are safe to run.** The load-bearing question — *does the
hardening change the traded object?* — is answered with the strongest available measurement:
**2439/2439 and 378/378 rows identical across all 14 fields, identical to the cent, identical
equity curves, on a same-moment control.** The inertness claim is not a comment in the source; it is
a short, total chain (§2.3, C1–C4) verified mechanically, and the falsification test (§1.5) shows the
code is live rather than dead. Nothing in either class can block an exit, structurally (C4) or by
exception (§3.8). The running paper deployments are untouched (§4).

**Swap the paper deployment to the hardened classes — after two decisions:**

1. **R1 must be an explicit owner choice.** Either accept `StopStrategy` + `NumberRestartAttempts = 0`
   knowing that a transient disconnect can strand an open position on the DEMO account, **or** set
   `ConnectionLossHandling = Recalculate` to match the certified behaviour. My recommendation:
   **on a paper account, deploy as built and let it teach you** — an orphaned DEMO position is
   cheap and observable, and `StopStrategy` is the right instinct for anything funded, where the
   correct pairing is a monitored flatten procedure rather than a silent `Recalculate`.
   Whichever is chosen, changing that property is a **new build and a new identity run**, not an edit.
2. **R2 must enter the roll-day checklist** before the September roll: the three secondary instrument
   strings must be updated together with the primary, or XM stops entering.

**Do not** treat this as parity certification. These are new class names carrying new behaviour in
realtime; §1 certifies **historical identity only**, which is the necessary condition, not the
sufficient one. **EXECUTABLE, PARITY-CERTIFIED and LIVE-ENABLED remain three separate statuses**
(CLAUDE.md §3), and nothing here authorises live enablement.

---

## 7. CLOSING CHECKS — after everything above had run

**Trade tables byte-identical.** `cmp P1_cert.csv P1_hard.csv` and `cmp XM_cert.csv XM_hard.csv` both
return clean — the exported 14-field tables are identical byte for byte, not merely equal
field by field. **VERIFIED.**

**Certified sources unmodified.** Re-hashed at 13:26 UTC, after all six backtests:

```
ee4c765bc5cab23096f4009943ef6a79e03c3d2d7c671a2285f6cec2676e87b2  WeeklyEdgeP1PCT_v1.cs
2ec00dd4d0a11b999b649dcf358b63f92bc09f4edf1d2cec77c076b64c910dde  WeeklyEdgeXMConflict_v2.cs
```

Both match `HARDENING_SPEC.md` §1 and `BUILD_NOTES.md` §1 exactly. **VERIFIED.**

**Deployments re-read at 13:26 UTC, after everything:** both still `Realtime` / `is_trading: true` /
`Flat 0` / `active_order_count 0`, `last_error: null`, with **unchanged** `current_strategy_id`
(`399550060`, `399550061`) and **unchanged** `last_deployed_utc` (10:48 UTC) — the direct evidence
that no redeploy occurred at any point in this work. **VERIFIED.**

---

*PROVER role only. No git command run. No order placed. No account touched beyond the isolated
Backtest account. No running strategy stopped, disabled, redeployed or modified. Neither certified
`.cs` file was written to.*
