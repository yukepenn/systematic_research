# INCIDENT 2026-09-03 — THE GHOST POSITION, and the exit that OPENED a naked short

**Account `2047681`, live, real money. No loss: the accidental short closed +$105.**
**Every number below is read from the machine record, not reconstructed.**

Sources: `Documents/NinjaTrader 8/trace/trace.20260903.00000.txt`,
`log/log.20260903.00000.txt`, `C:\NT8_ForwardLogs\mnq\diag\we_p1pct_hardening_20260903Z.csv`,
CrossTrade `ListOrders` / `ListExecutions` / `GetAccount` (all read-only).

---

## 1 · WHAT HAPPENED — account position, from `Cbi.Account.PositionUpdateCallback`

| ET | actor | order | ACCOUNT MNQU6 | P1's ledger |
|---|---|---|---:|---:|
| 11:05:00 | **P1** | `L` buy 6 @ 29440.875 (3+3) | `Long 6` | `+6` ✅ |
| 11:16:16 | **owner, by hand** | sell 6 @ 29467.50 | **`Flat`** | **`+6`** ❌ |
| 15:57:00 | **P1** | `XL` sell 6 @ 29516.5417 | **`Short 6`** | `0` |
| 16:48:42 | **Tradovate** | `AutoLiq` buy 6 @ 29507.7917 | `Flat` | `0` |

The account was **short 6 MNQ for 51 minutes**, and no human placed that trade.

## 2 · THE MECHANISM, IN ONE SENTENCE

**"Sell 6" closes a long 6 and opens a short 6 with the same bytes on the wire; only the ACCOUNT
distinguishes them, and the strategy never looks at the account.**

P1's exit was correct as an instruction and wrong as an outcome, because the position it was
written to close no longer existed. NT8 does not tell a strategy about fills it did not submit:
`Position` / `Positions[]` are *"position related information that pertains to an instance of a
strategy"*, not the account.

## 3 · WHY EVERY GUARD PASSED — the fourth instance of the standing pattern

`AssertLedgerMatchesStrategyPosition` runs a **three-way** check:

| witness | at 11:17 | what it actually measures |
|---|---:|---|
| the certified ledger `myQty` | `+6` | what this instance **decided** |
| `Positions[EXEC]` | `+6` | what this instance **submitted** |
| `shNetQty` (execution shadow) | `+6` | what this instance's orders **filled** |
| **`PositionsAccount[EXEC]`** | **`0`** | **what the account HOLDS** — `LOG ONLY`, gates nothing |

All three witnesses agreed **because all three describe the same thing**: what this instance did.
The one surface that would have disagreed was deliberately excluded, and the source says why —
`WeeklyEdgeP1PCTMnq_v1.cs:443-447`:

> *"PositionAccount is the REAL ACCOUNT net, which on this account holds P1 + XM + anything
> manual, so neither ledger would match it on most bars of a two-leg book."*

**That reasoning was correct and the conclusion was still wrong.** Correct: the raw account level
cannot be compared to one leg's ledger. Wrong: the answer is not "exclude it from the invariant",
it is "subtract the other leg first". That is HD-23.

⭐ This is the same shape the 2026-09-01 clean-set named, now for the fourth time:
**a guard reported truthfully on the thing it measured, and the thing it measured was not the
thing that mattered.**

## 4 · WHY THE 16:39 FORCED FLATTEN DID NOT SAVE IT

After 15:57 P1's ledger read `myQty = 0`. `ForcedFlatMin` inspects **its own ledger**, found flat,
and had nothing to do. **The instance built a position it could not see.**

## 5 · THE AUTO-LIQUIDATION — Tradovate's, not ours, and not new

Raw payload, `trace.20260903.00000.txt:7575-7591`:

```json
{ "id": 18930731125, "commandType": "New", "senderId": -1,
  "autoLiqTransactionId": 18930731124, "isAutomated": true }
{ "id": 18930731125, "orderQty": 6, "orderType": "Market", "text": "AutoLiq" }
```

`senderId: -1`, `isAutomated: true`, `text: "AutoLiq"`. NT8's side is `Cbi.Account.CreateOrder` —
it **learned of** the order, it did not send it.

**Nothing about auto-liquidation changed.** It is Tradovate account-level risk control, it has
always been on, it is not configured by us and not visible in our source. It had never fired
because **the account had never held a position across the overnight margin boundary** — the
strategy's own 15:45 exit and 16:39 flatten always got there first. Today was the first time, and
the position it liquidated was the ghost.

Arithmetic: 6 MNQ overnight initial margin ≈ **$4,649.23 × 6 = $27,895** against a
`netLiquidation` of ≈ $10,150. (The $4,649.23/contract figure is measured — `GetAccount`
2026-09-01 reported `initialMargin 13,947.69` on 3 contracts.)

**The accidental short made money**: 29516.5417 → 29507.7917 = 8.75 pt × 6 × $2 = **+$105.00**,
confirmed to the cent by the three `Cbi.Account.OnAddTrade` rows (18 + 70 + 17).

## 6 · THE $231 THAT DID NOT ADD UP — ✅ RESOLVED, by the owner

**The question:** 11:23 ET `netLiquidation 10,278.34`, account flat. 19:01 ET `10,047.32`,
account flat. Between them the only fills were the ghost round trip:
`grossRealizedProfitLoss` **+$105.00**, `weeklyProfitLoss` **+$47.32**. Every commission that day
at the measured MNQ rate (68 MNQ sides + 2 NQ sides) is ≈ **$48**. **≈$278 was unaccounted for**,
and no fee or commission posting appeared in any adapter payload in the log.

> ✅ **ANSWER, 2026-09-03, owner: a cash WITHDRAWAL plus a Tradovate AUTO-LIQUIDATION FEE.**
>
> **Evidence class: `OWNER_TESTIMONY`, not machine-verified.** Both components are real and
> neither is visible anywhere in NT8: a withdrawal is a cash-ledger event the adapter never
> pushes, and the auto-liq fee is billed by Tradovate outside the fill stream. **This closes the
> question and does NOT convert it into a measured number** — the split between the two is
> unknown and the Tradovate cash statement remains the only source that could apportion it.

⭐ **The durable lesson is about `netLiquidation`, not about $231:** it is a **cash balance**, so
**owner deposits, withdrawals and out-of-band fees move it and no trading record explains them.**
Any performance figure taken by differencing `netLiquidation` across time is therefore **wrong by
construction on this account**. Use `grossRealizedProfitLoss` and the fill record, never the
balance. Recorded because P&L-by-balance-difference is the obvious shortcut and it is invalid here.

⚠️ **Also noted:** `realizedProfitLoss` reset 367.82 → 0.00 across the 18:00 ET session rollover.
Expected; recorded so it is never mistaken for the item above.

🔴 **The auto-liq fee is a real, recurring cost of the HD-23 defect.** It is charged for a
liquidation the strategy caused and would not otherwise have incurred, and it is **not in
`COST_MODEL.md`** — it cannot be, because it is not a per-trade cost. It is a **penalty for
letting a position cross the overnight boundary**, and the correct response is the fix, not a
cost line.

## 7 · SECOND FINDING THE SAME DAY — XM had been latched since 2026-09-01, silently

`writer_watchdog --halts` returned **1,218** `HALT RECONCILE-BREAK` lines across 09-01/09-02:

```
2026-09-01 13:22:01  WARNING ROLL-PLAN blockNewEntriesFrom=2026-09-06 ...   <- once per Realtime
2026-09-01 13:23:00  ERROR   HALT RECONCILE-BREAK ledger=-3 strategyPosition=-3 execImplied=0
```

`ROLL-PLAN` is emitted exactly once, on entering `State.Realtime`. **XM restarted at 13:22 while
holding short 3 and halted on the very next bar.**

**Root cause, mechanical:** `shNetQty` is incremented ONLY inside `OnExecutionUpdate`, which
returns immediately unless `State == State.Realtime`. On any (re)start it is therefore **0**,
including a restart that carries a position. The warm-up carry branch
(`AssertLedgerMatchesStrategyPosition:466-476`) compares only `nt8` to `ledgerQty` — both `-3`,
so it logged `WARMUP-CARRY-FLAT` (a misleading name: they agreed at −3, nothing was flat) and
**returned without ever looking at the third witness**. One bar later the unguarded three-way
check fired on `shNetQty != ledgerQty` and latched.

Then it propagated: the 15:45 exit `XM_X` filled +3 into a shadow that had never seen the −3
entry, so `execImplied` stuck at **+3** while ledger and strategy position both read 0 — the
second signature, 1,031 of the 1,218 lines.

**Consequence:** XM refused every entry from 13:23 on 09-01 onward and its writer died 09-02
10:40 — while `ListAllStrategies` reported it `Realtime`, `isEnabled: true`, healthy, and the
account showed nothing wrong. **Any restart holding a position reproduces this. It is not rare.**

## 8 · THIRD EVENT, 19:06:41 — NT8 disabled everything itself

```
19:06:41:722  Strategy 'WeeklyEdgeP1PCT_v3/399562881' lost price connection more than
              4 times in the past 5 minutes and will be disabled.
19:06:41:723  Disabling NinjaScript strategy 'WeeklyEdgeP1PCTMnq_v1/399562885'
```

Eight `Price feed=Connection lost` / `Connected` flaps between 19:05:39 and 19:06:54 tripped
`NumberRestartAttempts = 4` / `RestartsWithinMinutes = 5`. **This is correct NT8 behaviour, the
account was flat, and no position was stranded.** Recorded because it is the reason the book is
not running, and because a restart from here is exactly the scenario section 7 describes — with
the difference that everything is flat, so the carry path is not exercised.

## 9 · WHAT WAS BUILT IN RESPONSE

Four fixes, offline, in four new classes. **Nothing was copied into NT8.**
Build `research/weekly_edge/src/build_hd23_challenger.py`,
certify `verify_hd23_challenger.py` (**32/32**), deploy `DEPLOY_HD23_20260921.md`.

| id | fixes | status before today |
|---|---|---|
| **HD-20** | warm-up shadow seed — section 7 | **firing in production, 1,218 lines** |
| **HD-21** | `XLsess` shadow leak — halts the next entry on a bogus `PARTIAL-FILL` | latent, P1 only |
| **HD-22** | export writer: fail loud + retry — killed the live ledger 09-01 | **fired, silently** |
| **HD-23** | account witness + position bus — sections 1–4 | **fired today** |

## 10 · THE LIMIT OF HD-23, STATED WITH IT

**From the account alone it is provably impossible to distinguish "my 6 were closed by someone
else" from "someone else opened 6 against me."** They are the same account event; FIFO
attribution is a broker convention, not a fact. The position bus removes the *other leg* from the
sum by having each leg publish its own position. **It cannot remove manual trading.**

Therefore:

* **`ENFORCE`** (clamp the exit so it cannot open a position) is correct **only on an account no
  human trades by hand.**
* **`DETECT`** (log at `ERROR`, change no order) is the only honest setting on this account today,
  and it is **the default**.
* The structurally correct fix is **a dedicated account per book** — an owner/broker action, not
  a code change. With it, `account == sum(legs)` exactly and `ENFORCE` becomes unambiguous.

**A guard that would misfire is worse than no guard**, which is why the default does not gate.

---

## 11 · FOURTH EVENT, 22:23–22:25 — NT8 fully restarted and **all strategy rows are gone**

```
22:23:02  Live/Simulation: Primary connection=Disconnecting          <- session .00000 ends
22:23:13  Session Break (Version 8.1.8.1)                            <- session .00001
22:24:18  NinjaTrader successfully restored the backup archive file 'workspaces.nt8bk'
22:24:20  Unhandled exception: Object reference not set to an instance of an object.
22:24:51  vendor assemblies reloaded                                 <- session .00002
22:25:01  Live: Primary connection=Connected, Price feed=Connected
```

`ListAllStrategies` at 22:25: **`count: 0`**, `2047681` `strategyCount 0`, `DEMO8383477`
`strategyCount 0`. All four export writers still frozen at `19:06:02`.

🔴 **THE RESTART REMOVED EVERY STRATEGY ROW. Re-enabling is a FULL REDEPLOY, not a checkbox** —
and the eight parameters in §12 do **not** survive it, with defaults that are actively wrong
(September contract strings, and `""` for `ExportDir` / `DiagDir` / `ExpectInstrument` /
`ExpectMnq`, where `""` means *write nothing* and *guard disabled*).

⚠️ **`workspaces.nt8bk` was restored from backup** and one session logged an unhandled
`NullReferenceException`. Neither is known to have damaged anything — the account is flat and
correct — but the workspace is not necessarily the one that was running this morning.

---

## 12 · REDEPLOY PARAMETER SHEET — the eight that do not survive a restart

Reconstructed from the last **verified-Realtime** rows (`ListAllStrategies`, 2026-09-03 11:19 ET)
and from the warm-up certificates in `C:\NT8_ForwardLogs\mnq\warmup\`.

| parameter | **LIVE `2047681`** | **PAPER `DEMO8383477`** | default if not typed |
|---|---|---|---|
| `ExportDir` | `C:\NT8_ForwardLogs\mnq\export` | `C:\NT8_ForwardLogs\export` | 🔴 `""` = writes nothing |
| `DiagDir` | `C:\NT8_ForwardLogs\mnq\diag` | `C:\NT8_ForwardLogs\diag` | 🔴 `""` |
| `WarmupCertDir` | `C:\NT8_ForwardLogs\mnq\warmup` | `C:\NT8_ForwardLogs\warmup` | 🔴 `""` |
| `ExpectInstrument` (P1) | `NQ 09-26` | `NQ 09-26` | 🔴 `""` = **guard disabled** |
| `ExpectMnq` (both, live only) | `MNQ 09-26` | *n/a* | 🔴 `""` = **guard disabled** |
| `MnqInstrument` (both, live only) | `MNQ 09-26` | *n/a* | `MNQ 09-26` ✅ |
| `EsInstrument`/`RtyInstrument`/`YmInstrument` (XM) | `ES 09-26` / `RTY 09-26` / `YM 09-26` | same | September ✅ **until the roll** |
| `MnqPerNq` (live only) | **`3`** | *n/a* | `3` ✅ |
| `Tag` | `p1pct` / `xm2` | `p1pct` / `xm2` | ✅ |
| **`DaysToLoad`** | **`365`** | **`365`** | 🔴 `5` — convergence needs ~9 months |

**Then read the machine's own line and abort if it is wrong:**

```
grep ROLL-PLAN in the NT8 log, per leg
```
Expected **today, on September contracts**: P1 `blockNewEntriesFrom=2026-09-08`,
XM `blockNewEntriesFrom=2026-09-06`. 🔴 **Both are in the future, so entries work — but only for
a few days.** After those dates each leg refuses new entries and that is the fail-safe working,
not a fault. December redeploy is `≥ 2026-09-19` (practically Mon 09-21) —
**`CURRENT_LIVE_TRUTH.md` §ROLL is the authority, never a date remembered from here.**

Expect one **`WARMUP-CARRY-AGREE`** (currently `WARMUP-CARRY-FLAT`) line per leg with
`ledger=0 strategyPosition=0`. The account is flat, so the HD-20 carry path is **not** exercised
by this restart.

Verify within one bar: `python research_sdk/writer_watchdog.py --halts` → four writers **ALIVE**.

---

## 13 · OWNER ACTIONS

1. 🔴 **The redeploy did not take — nothing is running.** `ListAllStrategies` = 0 at 22:25.
   Use §12; do not re-enable from memory.
2. 🔴 **Do not trade MNQ by hand on `2047681` while a leg holds a position.** Until HD-23 ships,
   the strategy cannot see it, and §1–§5 show what that costs. A manual trade in a **different**
   instrument is harmless.
3. ⚠️ **Never compute this book's P&L by differencing `netLiquidation`** — §6. Withdrawals and
   out-of-band fees move it and no trading record explains them.
4. 🔴 **Deploy the challenger at the 2026-09-21 roll window** — `DEPLOY_HD23_20260921.md`.
   Both legs are down for the roll anyway, so the recompile costs nothing extra.
5. ⚠️ **Run the syntax probe (`ProbeHd23Constructs_v1.cs`) only when nothing is about to be
   enabled.** A compile error blocks every subsequent build until the file is removed.
