# GENESIS III — OPEN STATE

**Recorded 2026-08-31 ~14:10 ET, entirely from the machine.** Where this disagrees with any
repository prose, the machine is recorded as correct and the disagreement is named below.

`LIVE REAL MONEY = NO. $0 spent. No order placed by this campaign.`

---

## 🔴 FINDING 0 — THE BOOK IS NOT M_11. IT IS RUNNING P1 TWICE.

`ListDeployedStrategies` returns **three** strategies alive on `DEMO8383477`, not two:

| deployment_id | strategy_id | class | state | position | deployed (UTC) |
|---|---|---|---|---|---|
| `dep_9c51536a7045` | 399562877 | `WeeklyEdgeP1PCT_v3` | Realtime, is_trading | Flat | 2026-08-31 16:31:51 |
| **`dep_61ae0a04b910`** | **399562876** | **`WeeklyEdgeP1PCT_v3`** | **Realtime, is_trading** | **Flat** | **2026-08-31 16:28:08** |
| `dep_27ff47e7e3b7` | 399562878 | `WeeklyEdgeXMConflict_v4` | Realtime, is_trading | Flat | 2026-08-31 16:32:27 |

Both P1 objects are distinct `Strategy` instances on the same account and the same instrument, each
with `bars_required_to_trade = 20` and `current_bar ≈ 353,853`. **The effective book is
`P1 ×2 + XM ×1`.** The duplicate is not a registry artifact — the machine wrote **two** P1 warm-up
certificates today, `warmup_p1pct_20260831_162811Z.csv` and `warmup_p1pct_20260831_163153Z.csv`.

### It is worse than a doubling: the duplicate trades but cannot log

There is exactly **one** P1 export file. Its integrity was tested rather than assumed:

```
we_p1pct_p1pct.csv   353,878 rows   353,878 distinct timestamps   0 duplicates   0 non-monotonic
```

A second writer appending to the same path would produce duplicate or out-of-order timestamps. There
are none. So the second P1 instance's `StreamWriter` lost the race for the file handle, `export` is
null in that instance, and **its decisions are invisible to the forward ledger while its orders are
fully visible to the account.** The ledger therefore *understates* the book's true exposure.

### ✅ RESOLVED 2026-08-31 14:25 ET — the duplicate is gone and M_11 is restored

`DisableStrategy` and `StopStrategy` were refused twice by the permission classifier. I did not route
around the refusal; the owner authorised the correction in chat, and it was then applied.

A second, unrelated defect surfaced during the fix and is worth recording: **`DisableStrategy` does
not accept `current_strategy_id`.** `DisableStrategy(account=DEMO8383477, strategyId=399562876)`
returned `strategy_not_found` **while `GetDeployedStrategyState` was simultaneously reporting that
same id as `Realtime, is_trading`.** The two tools use different id spaces. The call that works on an
MCP-deployed strategy is `StopStrategy(deployment_id=...)`.

```
StopStrategy(dep_61ae0a04b910) -> success:true, strategy_id 399562876, removed_from_registry:true
```

Verified after, from the machine, not asserted:

| check | result |
|---|---|
| live strategies on `DEMO8383477` | **2** — `399562877` (P1) and `399562878` (XM) |
| both states | `Realtime`, `is_trading`, **Flat**, 0 active orders |
| account positions | none, on all five accounts |
| ledger still owned by the survivor | ✅ `we_p1pct_p1pct.csv` last row `14:26:00` at 14:26:21 local |

Both legs were flat before and after; **no position was created or orphaned**. The stale rows
`dep_8307c94764fd`, `dep_51bf1a7382cb`, `dep_55403f7de5f5` remain in the registry but report
`strategy_not_in_account_collection` — they are records, not running objects.

**Evidence-class consequence, which does not go away:** for the window 2026-08-31 16:28 → 18:25 UTC
the book ran at P1 ×2 with only 1× logged. Any P1 observation inside that ~2-hour window is
`FORWARD_OPERATIONAL_ONLY` and may not be used as forward decision evidence. No trade occurred in it
(`trade_count = 0` on both P1 instances throughout), so nothing of value was lost.

---

## 1. REPOSITORY

| | |
|---|---|
| branch | `main` |
| HEAD | `6698e188e6bd21fff494708beb901f6bada2340b` |
| worktree | **clean** |
| remote | up to date (`git pull` = "Already up to date") |

## 2. THE EXECUTABLE OBJECTS

`sha256`, NT8 working copy and repo copy compared and **identical**:

| class | sha256 | NT8 path == repo path |
|---|---|---|
| `WeeklyEdgeP1PCT_v3.cs` | `a9ccc2331d78aea43b1eefeff24189d0277a4cdfb718f2b817f56f7ef60f6be6` | ✅ identical |
| `WeeklyEdgeXMConflict_v4.cs` | `0360f894724cfd1fe59eb2a3a14d434b6e8a082eb2f25ba483e97ff2b854bae8` | ✅ identical |

Also present in `bin/Custom/Strategies` (compiled into the assembly, **not** deployed):
`WeeklyEdgeP1PCT_v2.cs`, `WeeklyEdgeXMConflict_v3.cs`, `WeeklyEdgeBookM11_v1.cs`, 5 NT8 samples.

Deployed parameters (both legs): `DaysToLoad=365`, `DiagDir=C:\NT8_ForwardLogs\diag`,
`WarmupCertDir=…\warmup`, `ExportDir=…\export`. P1 also `ExpectInstrument="NQ 09-26"`.
XM also `EsInstrument="ES 09-26"`, `RtyInstrument="RTY 09-26"`, `YmInstrument="YM 09-26"`.

## 3. ACCOUNT, FEED AND CONTRACT

| | |
|---|---|
| account | `DEMO8383477`, provider `Provider31`, connection **`Simulation`** (user `rainazur`) |
| connection uptime | established 2026-08-31 13:21:22 UTC |
| cash value | **$93,536.28** · realized week P&L **$3,201.28** · gross realized $3,210.00 |
| commission implied | $8.72 on the week = 2 × $4.36 ⇒ one 2-lot round turn, consistent with the record |
| positions | **none** (`GetAllPositions` count 0, all five accounts flat) |
| active orders | 0 on every deployment |
| bound contract | `NQ 09-26` (`NQU6`), session 2026-08-30 22:00 → 2026-08-31 21:00 UTC, **open** |
| other accounts | `Backtest` (isolated, $100k), `Sim101` ($100k, untouched), `Playback101`, `2047681` |

⚠️ **§7 of the directive is NOT yet answered.** `Simulation` tells us the *connection name*, not
whether the quote stream is real market data and not whether fills are simulator-generated. Those are
three separate questions and they are resolved in `G3_FEEDSEM_01` (open), not here. Until then **no
fill or slippage observed on this account may be quoted as market execution evidence.**

## 4. WARM-UP CERTIFICATES (this session's redeploy)

| file | when (UTC) | leg |
|---|---|---|
| `warmup_p1pct_20260831_162811Z.csv` | 16:28:11 | P1 — **the duplicate** |
| `warmup_p1pct_20260831_163153Z.csv` | 16:31:53 | P1 — the retained instance |
| `warmup_xm2_20260831_163233Z.csv` | 16:32:33 | XM |

Both legs logged `WARMUP-CARRY-FLAT ledger=0 strategyPosition=0` — reconciled, nothing carried.
P1 `HD05 primary OK instrument=NQU6 expiry=2026-09-01 want=NQ 09-26`.
XM `HD05 … ES/RTY/YM all NQU6/ESU6/RTYU6/YMU6 → instrumentMismatch=False`.

## 5. 🔴 ROLL GUARD — read from the machine, not from prose

```
2026-08-31 12:32  [HD WeeklyEdgeP1PCT_v3    p1pct] ROLL-PLAN blockNewEntriesFrom=2026-09-08
                                                   leadDays=8 earliestStoredRollover=2026-09-16
                                                   [s0=NQU6:2026-09-16]
2026-08-31 12:33  [HD WeeklyEdgeXMConflict_v4 xm2] ROLL-PLAN blockNewEntriesFrom=2026-09-06
                                                   leadDays=8 earliestStoredRollover=2026-09-14
                                                   [s0=NQU6:2026-09-16 s1=ESU6:2026-09-14
                                                    s2=RTYU6:2026-09-15 s3=YMU6:2026-09-18]
```

**Both block dates are in the future, so neither leg is latched dead.** The guard latches: a
re-enable *inside* the window blocks new entries permanently while every health check still reports
green. **Red zone 2026-09-06 → 2026-09-18. Safe re-enable: **both legs ≥ 2026-09-19** (practically Mon 2026-09-21) — P1's MNQ series rolls **09-18**, two days after NQ's.**
🔴 **"P1 ≥ 09-17" WITHDRAWN 2026-09-01.** §5's quoted ROLL-PLAN is the **PAPER** book's (four
series); the LIVE book has five and P1 has two. Roll on `NQ 12-26` **and `MNQ 12-26`**, all series
together, `DaysToLoad=365`, `ExpectInstrument="NQ 12-26"`, **`ExpectMnq="MNQ 12-26"`**.
Authority: `research/operational/CURRENT_LIVE_TRUTH.md` §ROLL.

## 6. LEDGER HEALTH — verified by READING the files, never by directory metadata

| file | rows | span | integrity |
|---|---:|---|---|
| `export\we_p1pct_p1pct.csv` | 353,878 | 2025-08-31 18:01 → 2026-08-31 14:07 ET | 353,878 distinct ts, 0 dup, 0 non-monotonic |
| `export\we_xm_xm2.csv` | 353,877 | 2025-08-31 18:02 → 2026-08-31 14:05 ET | 353,878 distinct ts, 0 dup |
| `diag\` | **empty** | — | expected: `HdDiagRow` is event-driven and no event has fired since redeploy |
| `research/operational/shadow/` | `runner.log` 310 B, `runner_state.json` 69 B | — | `decisions.csv` / `outcomes.csv` **do not exist yet** — correct, `SHADOW_START` is 2026-09-01 18:00 ET |

⭐ **A capability nobody had recorded:** the export is **not** realtime-scoped. It contains the entire
`DaysToLoad=365` warm-up replay. That is **353,878 rows of the executable object's own internal
per-bar state** — `nMem, nThr, dL, ratio, voteOK, size, score, qty, sessPnl, stopped, tilt, bmom,
t0..t3` — free, already on disk, and exactly the substrate directive §4 requires. `G3_EXECTRUTH_01`
consumes it.

## 7. TWO CLOCKS

| clock | value | meaning |
|---|---|---|
| `OWNER_FORWARD_START` | 2026-08-30 18:00 ET | owner's practical forward start; paper decisions from here |
| `LEGACY_FORMAL_SHADOW_START` | 2026-09-01 18:00 ET | `shadow_runner.py:34`; hash-chain governance begins here |

Neither is rewritten. Nothing is backfilled into either.

## 8. CAPITAL DOCTRINE

🔴 **SUPERSEDED 2026-09-01 — see `CURRENT_LIVE_TRUTH.md`. The live book is NOT the book this section
plans for.** Live: account `2047681`, **$10,206.86**, `MnqPerNq = 3` = **0.30 NQ-equivalent** →
0.30 × $51,891 = **$15,567 = 152.5 % of the account**. A repeat of the book's own already-observed
worst episode ends it. **1 MNQ = 50.8 %, 2 MNQ = 101.7 %.**

**$75,000 – $90,000 is the plan for the 1 NQ + 1 NQ book, which is NOT what is deployed.**
`$45,000` and `$21,740` are RETIRED and must not be requoted (swept at `75b7af3`, `3a94ba2`).
⚠️ The `$93,536.28` cash value formerly cited here is the **SIMULATED** account `DEMO8383477`'s
balance (this file's own line 104, connection `Simulation`) — **it capitalises nothing.**

## 9. EVIDENCE-CLASS MAP AS IT STANDS TODAY

| object | class | why |
|---|---|---|
| the 2,439-trade / 378-trade NT8 histories | `RETROSPECTIVE_RECONSTRUCTION` | Strategy Analyzer, zero slippage, template commission |
| every Python P1 economic figure | `DISCOVERY_CONSUMED` | and now also **object-divergent** — see §10 |
| paper decisions 2026-08-30 18:00 → 2026-08-31 16:28 UTC | `FORWARD_DECISION_FIRST` | decision logged before outcome |
| paper decisions from 2026-08-31 16:28 UTC | 🔴 `FORWARD_OPERATIONAL_ONLY` | duplicate P1 unlogged; exposure ≠ ledger |
| any fill/slippage on `DEMO8383477` | **UNCLASSIFIED pending `G3_FEEDSEM_01`** | "Simulation" not yet decomposed |
| 2026-05-31 → 2026-07-31 | `DIRECTLY_BURNED` | |
| ≥ 2026-08-01 | **VIRGIN / SEALED** | untouched by this campaign |

## 10. 🔴 DISAGREEMENT WITH THE REPOSITORY, RECORDED VISIBLY

**`research/operational/CURRENT_LIVE_TRUTH.md` is stale.** It names the book as
`WeeklyEdgeP1PCT_v2` / `dep_8307c94764fd` / 399562875 and `WeeklyEdgeXMConflict_v3` /
`dep_51bf1a7382cb` / 399562874. The machine reports **both of those deployments as
`strategy_not_in_account_collection`** — they no longer exist. The live objects are `_v3` / `_v4`.
The document is superseded by this file and by the correction of Finding 0.

**A second disagreement, from source rather than prose.** Every P1 economic figure in this repository
was computed by a Python object that is **not** the object that trades. Read directly:

| | direction | quality / size |
|---|---|---|
| C# `WeeklyEdgeP1PCT_v3.cs:1131-1152` + `:1197` (`CacheLagged()` last) | bar `i−2` | bar `i−2` |
| Python `run_we_w98.py:69,74` + `run_we_w37.py:34` + `we_quality.py:44-59` | bar `i−2` | **bar `i−1`** |

The directions agree. **Python's sizing layer reads one bar fresher than the direction that triggered
it** — legal, but a different information set from the one the deployed strategy has. The executable
is the *staler* object. `T2_P1SIZE01` measured the symptom (81.21% score agreement, 99.04% size
agreement) and accepted the 99% as parity; it is not parity, and neither object had been established
as correct. `G3_EXECTRUTH_01` tests this against 353,878 rows the executable wrote about itself, with
the source-derived prediction able to lose to a named control.

---

## OPEN AT THIS MOMENT

| id | question | status |
|---|---|---|
| `G3_EXECTRUTH_01` | which object do we actually trade, bar for bar? | preregistered |
| `G3_XMLAT_01` | is XM's edge causal under executable timing, and does it survive real latency? | preregistered |
| `G3_FEEDSEM_01` | what does "Simulation" mean — data, fills, slippage, separately? | open |
| WAVE B | global external alpha mining → EVI-ranked mechanism families | running |
| 🔴 owner | disable duplicate P1 `399562876` | **blocked on owner** |
