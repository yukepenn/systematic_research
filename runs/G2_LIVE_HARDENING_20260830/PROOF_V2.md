# PROOF V2 — re-proof of `WeeklyEdgeP1PCT_v2` / `WeeklyEdgeXMConflict_v3` after the connection-loss revert

**Run** `G2_LIVE_HARDENING_20260830` · **Role** RE-PROVER · **Executed** 2026-08-30 13:38–13:50 UTC
**Why this exists** the fixer removed `ConnectionLossHandling` and `NumberRestartAttempts` from both
hardened shadows (BUILD_NOTES.md §CONNLOSS REVERT). **A property change is a new build**, so the
identity proof in `PROOF.md` — which measured the *pre-revert* bytes — no longer certifies the object
on disk. `PROOF.md` is not amended; it stands as the record of the build it measured.

**Verdict** TEST 1 **PASS** · TEST 2 **PASS** · TEST 3 **FAIL — but not by this build, and not by
this role.** The two paper deployments were destroyed at 13:41 UTC by an involuntary feed disconnect
and a NinjaTrader/CrossTrade process restart. **Recommendation: GO on the code, with the swap
re-scoped as a fresh deploy.** See §5.

**Compliance.** No git command was run. No order placed, modified or cancelled. No strategy deployed,
enabled, disabled, stopped or redeployed — the add-on logs every deliberate stop as
`Disabling NinjaScript strategy …` and there is **no such line after 10:47:35 UTC**, which predates
this role by nearly an hour. No compile was triggered by this role. `WeeklyEdgeP1PCT_v1.cs` and
`WeeklyEdgeXMConflict_v2.cs` were opened read-only and re-hashed unchanged. Every backtest ran on
NT8's isolated **Backtest** account. All writes went to `runs/G2_LIVE_HARDENING_20260830/PROOF_V2.md`
and `out/proof_v2/`; **nothing under `out/proof/` was overwritten.**

---

## 0. Artefacts

| file | what it is |
|---|---|
| `out/proof_v2/{P1,XM}_ROWIDENTITY.txt` | the two TEST 1 gate tables, printed by `rowcmp.py` |
| `out/proof_v2/{P1,XM}_{cert,hard}.csv` | the 2439 / 378 trade rows, 14 fields, both classes |
| `out/proof_v2/raw_{P1_v1,P1_v2,XM_v2,XM_v3}.json` | the four raw NT8 results |
| `out/proof_v2/TEST2_INERTNESS.txt` | TEST 2, re-generated against the post-revert sources |
| `out/proof_v2/BUILD_WITNESS.txt` | the assembly-level proof that the compiled build is post-fix |
| `out/proof_v2/ENV_WITNESS.txt` | verbatim activity-log evidence for §3 and §4 |
| `out/proof_v2/{rowcmp,inertness_audit}.py` | copied unmodified from `out/proof/` — same comparator |
| `out/proof_v2/build_witness.py` | new; written for this pass |

---

## 1. The problem this pass had to solve first — VERIFIED

The reverted properties are **realtime-only**. Neither can influence a Strategy Analyzer run, so
**no backtest can distinguish the pre-fix build from the post-fix build behaviourally.** A green
identity table is therefore necessary but, on its own, silent about *which bytes ran*. CLAUDE.md §6
makes this concrete: NT8 cannot unload a type, the class names were **not** changed by the revert, and
a stale type would produce exactly the same green table.

So the build question was answered at the **assembly** level, not the behaviour level.
A C# `X = value;` on a property compiles to `call … set_X(…)`, which places the name `set_X` in the
assembly's metadata string heap. Removing the only assignment site removes it. `build_witness.py`
prints the table; the **A1 control rows are the load-bearing part** — the three sibling properties the
files still declare must be PRESENT, or an ABSENT result would prove nothing.

```
GATE                                  SPEC                                             OBSERVED   VERDICT
A1 control set_RealtimeErrorHandling   PRESENT (still declared -> search is sensitive)  PRESENT    PASS
A1 control set_DisconnectDelaySeconds  PRESENT (still declared -> search is sensitive)  PRESENT    PASS
A1 control set_StartBehavior           PRESENT (still declared -> search is sensitive)  PRESENT    PASS
A2 removed set_ConnectionLossHandling  ABSENT  (no assignment site in the assembly)     ABSENT     PASS
A2 removed set_NumberRestartAttempts   ABSENT  (no assignment site in the assembly)     ABSENT     PASS
A3 types WeeklyEdge{P1PCT_v1,P1PCT_v2,XMConflict_v2,XMConflict_v3}  PRESENT             PRESENT    PASS
S1 0 non-comment declaration sites in either hardened file                              0 / 0      PASS
S2 hardened sha256 == the fixer's recorded post-revert digests                          match      PASS
S3 certified sha256 UNCHANGED (ee4c765b… / 2ec00dd4…)                                   match      PASS
BUILD WITNESS: PASS - the on-disk compiled assembly is the POST-FIX build
```

**And the stale-type risk was removed for me by the environment.** `NinjaTrader.Custom.dll` was
**rebuilt at 13:41:49 UTC** (file mtime; it read 13:29:58 UTC when I first looked at 13:39, so the
rebuild happened during the 13:41:05 process restart). Every backtest in §2 ran at **13:42:07 UTC or
later**, i.e. against an assembly compiled from the post-revert sources **in a freshly started
process**. There is no surviving pre-fix assembly in that AppDomain to resolve to.

---

## 2. TEST 1 — ROW IDENTITY, RE-RUN — **PASS**

### 2.1 Method — unchanged from `PROOF.md`, deliberately

Same comparator (`rowcmp.py`, copied byte-identical), same four settings, and — because
`to = 2026-08-30T21:59:59Z` is later today and the NQ 09-26 series is still forming — the **certified
classes were re-run in the same batch**, not compared against numbers recorded earlier. Four runs
inside a **106-second window**, 13:42:07 → 13:44:19 UTC.

Settings, identical across all four and read back from each run's own trace:
`NQ 09-26` (resolved `NQU6`) · `Minute/1` · `from 2022-01-03T00:00:00Z` · `to 2026-08-30T21:59:59Z` ·
`CME US Index Futures ETH` · `Standard / 0 slippage / NinjaTrader Brokerage Lifetime` ·
account `Backtest (isolated, reset)` · **`loaded 1647698 bars` in all four** ·
engine `nt8_strategy_analyzer`, NT8 `8.1.8.1`, fingerprint `sha256:b4255f1b0dd7fba1`.

### 2.2 The four (trades, net) pairs — the answer to the question asked

`closed_sum` is the sum of the closed trade rows; `NetProfit` is NT8's engine figure, which also
carries the still-open trade (P1's 2440th, XM's 379th). Both are reported because they are different
quantities, as `PROOF.md` §1.1 established.

| class | start (UTC) | **trades** | **net (closed rows)** | net (engine `NetProfit`) | `TradesCount` | commission | qty |
|---|---|---|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v1` — **certified** | 13:42:07 | **2439** | **$354,575.96** | $356,317.24 | 2440 | $12,814.04 | 2939 |
| `WeeklyEdgeP1PCT_v2` — **hardened** | 13:42:44 | **2439** | **$354,575.96** | $356,317.24 | 2440 | $12,814.04 | 2939 |
| `WeeklyEdgeXMConflict_v2` — **certified** | 13:43:17 | **378** | **$182,776.92** | $179,072.56 | 379 | $1,648.08 | 378 |
| `WeeklyEdgeXMConflict_v3` — **hardened** | 13:43:53 | **378** | **$182,776.92** | $179,072.56 | 379 | $1,648.08 | 378 |

### 2.3 P1PCT gate table — printed by `rowcmp.py`, not assembled by hand

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

**Differing rows: 0 of 2439.** PASS required 0.

### 2.4 XMCONFLICT gate table

```
G1  trade count            378 vs 378                 PASS      G6  total quantity     378 vs 378                PASS
G2  core row identity      0 mismatched of 378        PASS      G7  engine NetProfit   179072.56 vs 179072.56    PASS
G3  extended row identity  0 mismatched of 378        PASS      G8  engine TradesCount 379 vs 379                PASS
G4  closed-trade net       182776.92 vs 182776.92     PASS      G9  bars loaded        1647698 vs 1647698        PASS
G5  total commission       1648.08 vs 1648.08         PASS      G10 equity curve       0/378 points differ       PASS
OVERALL: PASS
```

**Differing rows: 0 of 378.** PASS required 0.

### 2.5 Byte-level closing checks

```
cmp P1_cert.csv P1_hard.csv          -> identical
cmp XM_cert.csv XM_hard.csv          -> identical
cmp P1_hard.csv ../proof/P1_hard.csv -> identical   (post-fix hardened == pre-fix hardened)
cmp XM_hard.csv ../proof/XM_hard.csv -> identical
```

The last two are worth stating plainly: the post-revert build reproduces the **pre-revert** trade
table byte for byte as well. That is the expected result for a change confined to two realtime-only
properties, and it is a second, independent way of saying the revert altered nothing historical.

### 2.6 One thing this run could not repeat, recorded rather than glossed

`PROOF.md` §1.5 defended the identity result against the "dead code also matches" objection with a
falsification test — the hardened XM run with `EsInstrument = "ES 12-26"` returned 0 trades while the
certified class still returned 378. **I did not re-run it.** The revert touched no guard logic
(§3 shows the inertness audit is structurally unchanged), and the environment had already dropped one
backtest, so I chose not to spend another 1.65 M-bar request on a claim the source diff already
settles. The falsification evidence for the *guard* therefore carries forward from `PROOF.md`,
**tagged as such**, and is not re-asserted as measured today.

---

## 3. TEST 2 — the hardening is still inert, and the declarations are gone — **PASS**

### 3.1 The declarations, from the source

`grep` over both hardened files, comment lines excluded from the code test:

```
WeeklyEdgeP1PCT_v2.cs        ConnectionLossHandling / NumberRestartAttempts code sites: 0
                             surviving COMMENT-only mentions: 2   (L519, L793)
WeeklyEdgeXMConflict_v3.cs   ConnectionLossHandling / NumberRestartAttempts code sites: 0
                             surviving COMMENT-only mentions: 1   (L486)
```

A whole-tree scan of `bin/Custom` finds no other `.cs` assigning either property, and §1's A2 rows
confirm the compiled assembly contains no setter call for either. **Both properties now take the
platform default in both hardened classes.**

The three surviving mentions are comments. The fixer already flagged the P1 L793 one
(`// … NumberRestartAttempts = 0 already disables restarts …`) as **stale** — it describes a
declaration that no longer exists. It is a documentation defect, not a behaviour defect, and it
remains open; see R6.

### 3.2 Every hardening block still realtime-gated or event-driven

`inertness_audit.py` re-run **unmodified** against the post-revert sources:

```
WeeklyEdgeP1PCT_v2.cs        32 methods in region; 13 gated M1 at the first executable statement; 19 justified otherwise.
WeeklyEdgeXMConflict_v3.cs   34 methods in region; 15 gated M1 at the first executable statement; 19 justified otherwise.

C1 P1: every read of haltEntries               L264=LATCH-GUARD  L278=BLOCKING(EntriesAllowed)  L850=LOG-ONLY   PASS
C1 P1: every read of warmupBlocked             L279=BLOCKING     L708=REARM                                     PASS
C1 P1: every read of entriesBlockedUntilAgree  L280=BLOCKING     L416=REARM                                     PASS
C1 XM: the same three                          L231/245/940, L246/762, L247/383 — same classification            PASS
C2 the gate wraps only entry order sites       P1 wrap at L1162 (one site) · XM wrap at L1078 (one site)         PASS
C3 added order sites are M1-gated              P1 3 sites, 0 added · XM 4 sites, 1 added, inside an M1 method    PASS
C4 NO exit is behind EntriesAllowed()          gated exit sites: none, in either file                            PASS
TEST 2 VERDICT: PASS
```

**The delta against the pre-fix audit was measured, not eyeballed.** Diffing the two
`TEST2_INERTNESS.txt` files with line numbers masked leaves exactly **two** differing lines — the C2
wrap-site line numbers, `1164 → 1162` and `1080 → 1078`. Both shifted by **exactly −2**, which is the
two deleted lines per file. **No block changed classification, no claim changed verdict.** The
previous proof's §2.4 exception (XM's `HdInstrumentGuard` writing `instrumentMismatch` at
`State.DataLoaded`, monotone, read only in the entry predicate) is unchanged and still the only
non-M1 path to certified behaviour.

### 3.3 NT8's own witness — `performance.realtime.TradesCount = 0` in each run

| run | `realtime.TradesCount` | `realtime.NetProfit` | `realtime.TotalQuantity` | final `state` |
|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v1` | **0** | 0.00 | 0 | `Finalized` |
| `WeeklyEdgeP1PCT_v2` | **0** | 0.00 | 0 | `Finalized` |
| `WeeklyEdgeXMConflict_v2` | **0** | 0.00 | 0 | `Finalized` |
| `WeeklyEdgeXMConflict_v3` | **0** | 0.00 | 0 | `Finalized` |

All 2439 / 378 trades landed in the historical bucket and none in the realtime bucket — the engine's
own record that no strategy executed in a realtime state, which is exactly what the M1 gate depends
on. **PASS in all four.**

---

## 4. TEST 3 — the running paper deployments — **FAIL (state changed; cause external)**

TEST 3 asked me to confirm `dep_306e11dfc8eb` and `dep_5a914d070687` are still Realtime, flat, with
the same strategy ids. **They are not. Both deployments no longer exist.** Read-only, 13:45–13:46 UTC:

```
ListDeployedStrategies()                     -> total 0, deployments []
GetDeployedStrategyState(dep_306e11dfc8eb)   -> not_found: "not in registry"
GetDeployedStrategyState(dep_5a914d070687)   -> not_found: "not in registry"
ListAllStrategies(includeTerminal=true)      -> count 0; DEMO8383477 connected to 'Simulation',
                                                strategyCount 0
GetAllPositions(includeFlat=false)           -> [] (0)
GetAllOrders(activeOnly=true)                -> [] (0)
```

`ListAllStrategies` queries NT8's `Account.Strategies` directly, not the add-on's registry, so this is
not merely a registry that forgot — the strategies are gone from NT8 as well.

### 4.1 What happened, from the add-on's own log (verbatim in `ENV_WITNESS.txt`)

```
13:40:38.9Z  (this role) RunStrategyBacktest WeeklyEdgeP1PCT_v1 submitted
13:40:43.6Z  [Connection] Status changed for provider 'Simulation' to Disconnecting
13:40:43.6Z  job -> bars_request_failed  "NT8 BarsRequest reported error: Aborted due to disconnect"
13:40:45.1Z  [Connection] Connection 'Simulation' lost.                                   (Warning)
13:40:45.1Z  [Auto-Reconnect] Involuntary disconnect detected for 'Simulation'
             (Unexpected disconnect (no API intent)). Triggering recovery.
13:40:45.1Z  [Reconnect Policy] Using previously captured snapshot of 2 strategies …
13:41:05.6Z  Starting CrossTrade...        <- process restart, same signature as the 10:07:37Z start
13:41:18.7Z  [Connection] Status changed for provider 'Simulation' to Connected
13:41:49.2Z  NinjaTrader.Custom.dll rebuilt
```

**This role did not stop them.** The add-on logs every deliberate stop as
`[NinjaTrader] Disabling NinjaScript strategy '<name>/<id>'`. The last two such lines are **10:47:30Z
and 10:47:35Z** — the orchestrator's own earlier redeploy. There is **no `Disabling` line after
10:47:35Z**. The strategies were not disabled; they were lost with the process.

**Attribution, stated honestly.** The abort arrived 5 s after this role submitted a 1,647,698-bar
request, so a causal contribution cannot be excluded from timing alone. Against that: the add-on
classifies the drop as involuntary with *"no API intent"*; the previous PROVER ran **six**
byte-identical requests between 13:15Z and 13:23Z with no drop; **four** byte-identical requests after
the reconnect all completed; and the same feed already logged
`There was a problem subscribing to tick data for NQ: 'Symbol is inaccessible'` at 12:17:49Z. Weight
of evidence: a provider-side drop of the `Simulation` feed. I record the residual doubt rather than
dismiss it.

### 4.2 Nothing was orphaned

Both strategies were `Flat 0` with `active_order_count 0` at 13:26Z (`PROOF.md` §7), and there is no
open position and no working order on any account now. The loss cost state, not money.

### 4.3 The silver lining — this closes two of `PROOF.md`'s residuals

Hunting the cause surfaced NT8's **own read-back** of the deployed certified strategies' effective
properties, at enable time (10:48:02Z and 10:48:52Z):

```
StartBehavior=WaitUntilFlat  EntryHandling=All entries  EntriesPerDirection=1
StopTargetHandling=Per entry execution
ErrorHandling=Stop strategy, cancel orders, close positions
ExitOnSessionClose=False   SetOrderQuantityBy=Strategy
ConnectionLossHandling=Recalculate   DisconnectDelaySeconds=10
Calculate=On bar close  IsUnmanaged=False  MaxRestarts=4 in 5 minutes
```

This is the measurement `PROOF.md` §3.3 could not obtain and had to carry as
**UNVERIFIED-BY-PROVER** — `ListStrategies` does not expose those properties, but the enable-time log
line does.

- **R1 is CLOSED.** The certified defaults on *this install* are confirmed to be
  `ConnectionLossHandling = Recalculate` and `MaxRestarts = 4 in 5 minutes`. The builder's
  "CHANGE from Recalculate" / "CHANGE from 4" claims were accurate, and the fixer's revert therefore
  lands the hardened classes on **exactly the certified values**. The orphaned-position exposure that
  `PROOF.md` §3.3 flagged as the one item it would not sign is **gone**, by construction.
- **R4 is CLOSED.** `SetOrderQuantityBy=Strategy` is the platform default, and *neither* the certified
  nor the hardened files declare `SetOrderQuantity`. Undeclared in both ⇒ identical in both.
- The surviving declarations in the hardened files — `RealtimeErrorHandling = StopCancelClose`,
  `DisconnectDelaySeconds = 10`, `StartBehavior = WaitUntilFlat`, `IsUnmanaged = false` — each match
  the certified read-back exactly, so they are explicit restatements of the certified configuration,
  not changes to it.

**The cheap confirmation, for whoever performs the deploy:** when the hardened classes are enabled,
NT8 emits the same `Enabling NinjaScript strategy …` line. It must read
`ConnectionLossHandling=Recalculate` and `MaxRestarts=4 in 5 minutes`. That is the definitive
read-back of the reverted properties — and it is the *only* place they can be observed, since no
backtest can witness a realtime-only property. **Check it, and R1 is confirmed empirically as well as
structurally.**

---

## 5. RESIDUALS AND RECOMMENDATION

| id | item | status after this pass |
|---|---|---|
| **R1** | connection-loss handling | **CLOSED.** Declarations removed; platform default confirmed to be `Recalculate`/`4` from NT8's own read-back. Confirm at enable time (§4.3). |
| **R2** | XM's HD-05 requires all secondaries on the primary's contract month; at the Sep→Dec roll, updating only the deployment's instrument stops all entries | **OPEN, unchanged.** Roll-day checklist item. Fail-closed and loud. |
| **R3** | `rollResolved` latches at start; `rollBlockFrom` never refreshes, so a post-roll entry block clears only on restart | **OPEN, unchanged.** LOW, entry-side, recoverable by redeploy. |
| **R4** | `SetOrderQuantity` undeclared | **CLOSED.** Undeclared in certified *and* hardened; read-back is `Strategy` for both. |
| **R5** | no `spec.yaml` in this run directory (CLAUDE.md §4) | **OPEN.** Still not repaired, and deliberately not backdated. Governance debt. |
| **R6** | *new* — `WeeklyEdgeP1PCT_v2.cs` L793 comment still claims `NumberRestartAttempts = 0` disables restarts; the declaration is gone, so the comment is false | **OPEN.** Comment-only, zero behavioural effect. Fix on the next functional edit; not worth a build of its own. |
| **R7** | *new* — the `Simulation` feed dropped involuntarily and the process restarted, destroying both deployments and rebuilding `NinjaTrader.Custom.dll` | **OPEN, environmental.** Not a property of either class. Owner/orchestrator. |

### VERDICT — **GO on the code**

The load-bearing question — *does the reverted build still trade the certified object?* — is answered
with the strongest measurement available: **2439/2439 and 378/378 rows identical across all 14 fields,
identical to the cent, identical equity curves, on a same-moment control**, and — unlike a pure
behaviour test — backed by an **assembly-level witness** that the bytes which produced those rows are
the post-revert bytes. The inertness chain is unchanged apart from a two-line offset. The revert
strictly *reduces* the delta against the certified object: it deletes two declarations and adds
nothing, and both properties now take the value the certified strategies were measured to run at.
**The connection-loss change was the one item `PROOF.md` refused to sign; reverting it removes that
objection rather than trading it for a new one.**

**Two conditions on the GO, and one is not optional:**

1. **This is no longer a swap — it is a fresh deploy.** `dep_306e11dfc8eb` and `dep_5a914d070687` do
   not exist. There is nothing running to swap *from*, and no strategy is currently trading on
   `DEMO8383477`. Whoever proceeds must re-verify the environment first (NT8 up, `Simulation`
   connected and stable, `NinjaTrader.Custom.dll` current) and then deploy the hardened classes as new
   deployments — not issue a swap against dead ids.
2. **R2 must enter the roll-day checklist** before the September roll: `EsInstrument`,
   `RtyInstrument` and `YmInstrument` must be updated together with the primary, or XM stops entering.

**Do not read this as parity certification.** §2 certifies **historical identity only** — the
necessary condition, not the sufficient one. These are new class names carrying new behaviour in
realtime. **EXECUTABLE, PARITY-CERTIFIED and LIVE-ENABLED remain three separate statuses**
(CLAUDE.md §3), and nothing here authorises live enablement on any funded account.

---

## 6. CLOSING CHECKS — after everything above had run

**Certified sources unmodified**, re-hashed 13:47 UTC after all four backtests:

```
ee4c765bc5cab23096f4009943ef6a79e03c3d2d7c671a2285f6cec2676e87b2  WeeklyEdgeP1PCT_v1.cs
2ec00dd4d0a11b999b649dcf358b63f92bc09f4edf1d2cec77c076b64c910dde  WeeklyEdgeXMConflict_v2.cs
```

Both match `HARDENING_SPEC.md` §1, `BUILD_NOTES.md` §1 and `PROOF.md` §7 exactly. **VERIFIED.**

**Hardened sources** match the digests the fixer recorded post-revert:
`a815da3b…afb9` (P1, 70,306 bytes) and `3b8da2e6…19f0` (XM, 65,841 bytes). **VERIFIED.**

**No account touched** beyond the isolated `Backtest` account; `GetAllPositions` and `GetAllOrders`
both empty across every account.

---

*RE-PROVER role only. No git command run. No order placed. No account touched beyond the isolated
Backtest account. No strategy stopped, disabled, deployed or redeployed. Neither certified `.cs` file
was written to. `PROOF.md` and everything under `out/proof/` left untouched.*
