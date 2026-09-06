# NT8 PRODUCTION OPERATING MODEL — contract roll, restart persistence, and the roll-block trap

**Written 2026-08-30 evening**, from a 7-agent audit plus two adversarial skeptics, after the owner
asked: *"doesn't NinjaTrader auto-select the active contract? do we really redeploy after every
restart? what is the correct way? what do other systematic traders do?"*

Supersedes the relevant lines of `NT8_RUNBOOK.md` and corrects two rules recorded earlier the same
day. ⚠️ **Written for the paper book. As of 2026-09-01 it ALSO governs the 🔴 LIVE real-money book
on account `2047681`** — see `research/operational/CURRENT_LIVE_TRUTH.md` for the live-specific
deltas: the **MNQ execution series**, `ExpectMnq`, `MnqPerNq = 3`, and the separate
`C:\NT8_ForwardLogs\mnq\` log tree.

---

## 🔴 0. THE FINDING THAT MATTERS MOST: the roll fail-safe LATCHES, and the roll plan I gave would have killed the book

Earlier today this repo recorded *"roll both legs by Friday 2026-09-04."* **That instruction is
withdrawn. Following it would have produced a permanently dead book that passes every health check.**

`ResolveRollDates` runs **once**, on the first realtime bar, and never recomputes
(`WeeklyEdgeP1PCT_v2.cs:444` — `if (State != State.Realtime || rollResolved) return;`). It sets

```
rollBlockFrom = min over series( MasterInstrument.GetNextRolloverDate(now) ) - RollLeadDays(8)
```

and `RollBlocked()` is **monotone in date** (`:478` — `return HdBarTime().Date >= rollBlockFrom.Date;`).

**`GetNextRolloverDate` is a ROOT-level lookup. It cannot tell that you already rolled.** So a
strategy re-enabled *after* its block date recomputes the *same* block date and is blocked
**immediately and permanently**:

| leg | re-enabled anywhere in… | resulting `blockFrom` | outcome |
|---|---|---|---|
| P1 (paper, 1 series) | **2026-09-08 → 09-16** | 2026-09-08 | **blocked instantly, forever** |
| 🔴 **P1 (LIVE, NQ+MNQ)** | **2026-09-08 → 09-18** | 09-08, then **09-10** after NQ rolls | **blocked instantly, forever** |
| XM | **2026-09-06 → 09-18** | 09-06/07/08/10 | **blocked instantly, forever** |

The book would read **Enabled · Realtime · bars advancing · warm-up GO · flat** and take **zero
trades indefinitely.** Every item in the obvious acceptance checklist passes.

### ✅ Safe re-enable: **BOTH legs on/after 2026-09-19**

> 🔴 **CORRECTION 2026-09-01 — "P1 on/after 2026-09-17" is WITHDRAWN.** It was derived from
> NQ's 09-16 rollover alone, which was correct for the **single-series paper** P1. The **live**
> P1 carries a second series, `MNQU6`, whose stored rollover is **2026-09-18**, and
> `ResolveRollDates` takes the **MIN over every loaded series**. A P1 restart on 09-17 resolves
> `earliest = 09-18` → `rollBlockFrom = 09-10` → **blocked on the first bar.**
> Authority: `research/operational/CURRENT_LIVE_TRUTH.md` §ROLL.

(Both legs wait for the latest of their series — `YM 09-18` **and** `MNQ 09-18`.)

⭐ **And do not trust this date either.** It is stale the moment a series is added or the
December schedule differs. The durable rule is mechanical: **restart, read the new `ROLL-PLAN`
line, and if `blockNewEntriesFrom` is not in the future, stop that leg immediately.**
`research_sdk/live_readiness_check.py` R1 already asserts exactly that and is date-generic.

### And the cost of waiting is ZERO

The reasoning that produced the bad plan was *"don't trade a dying contract."* **Wrong direction:
the strategies already refuse new entries from 09-06 / 09-08 by design.** Nothing enters between
09-08 and 09-19 under any plan. Waiting forfeits **nothing**; rolling early forfeits **everything**.

⚠️ **Consequence to accept: a ~13-day new-entry gap (09-06/08 → 09-19) in the forward evidence
stream.** Exits are never gated. This is the fail-safe working, not a fault — but the shadow ledger
must record the gap so it is never mistaken for a signal drought.

⚠️ **Design defect recorded:** the roll guard is root-level and has no notion of "already rolled."
It cannot distinguish *"you are late"* from *"you are done."* Any future revision should compare
against the **bound series' own expiry**, not the root's next rollover.

---

## 1. Q1 — does NT8 auto-select the active contract? **NO.**

- **There is no continuous contract to trade.** Of **1,857** MasterInstruments in
  `db\NinjaTrader.sqlite`, **zero** contain `#` and zero are described "continuous".
- **`Strategy2Instrument` stores a resolved `Instrument` row carrying an Expiry.** Both legs are
  pinned to contract month 2026-09 (P1: 1 series; XM: 4).
- **Root resolution exists but is ADD-TIME, not a live binding.** `MarketInfo(root="NQ")` does return
  NQU6 — but `MarketInfo(instrument="NQ")` returns **the US equity** (Eastern, 09:30–16:00, Closed;
  reproduced live). `ES` resolves to three instruments including *Eversource Energy*. Either way NT8
  stores one concrete row and **never re-resolves**.
- **NT8's Auto Rollover cannot reach a strategy.** Its own resource text: rollover *"will update the
  expiry of the instruments across all instrument lists and windows using the instruments on all open
  workspaces"* and *"Any open positions or orders will need to be manually rolled."* The help guide:
  *"NinjaScript strategies are not rolled forward and must be manually rolled over."* Our legs are
  account-hosted and **headless — they live in no workspace window.**

⇒ **The quarterly re-point is unavoidable. It is ~4 planned outages a year, not "every time".**

## 2. Q2 — must we redeploy after every restart? **Re-ADDING should be avoidable. Re-ENABLING is not.**

### 2a. Why the book vanished this morning — LEADING HYPOTHESIS, **n = 1, not verified**

NT8 logs `Workspace Default Yuke not saved` at **2026-08-30 09:40:38** — the shutdown that wiped us.
Strategy-grid membership is *pending workspace state* (NT8's `Workspace` class carries
`NewStrategy2Workspace` / `RemovedStrategy2Workspace`), so declining the save plausibly rolls the
additions back and deletes the rows. The pre-restart ids 399550057/58/60/61 have zero rows left.

⚠️ **A competing hypothesis fits every observation identically:** *NT8 deletes the workspace's
strategy rows at shutdown regardless of the save answer.* **Nothing on this machine distinguishes
them.**

⚠️ **The "7 declined saves in two weeks" framing is wrong and is corrected here.** Seven of the last
nine shutdowns did decline the save — but **the first strategy-enable event in the entire retained
log history is 2026-08-30 06:15:38**, so six of those shutdowns had **zero strategies deployed**.
**The failure has been observed exactly ONCE.**

⇒ **Until the experiment is run, plan for a FULL redeploy after any restart.**

**The decisive experiment** (cheap, must be done at a flat, market-closed moment with exactly the two
live rows present): save the workspace → restart → observe. Rows present ⇒ two-click re-arm is real.
Rows absent ⇒ this whole section collapses and the model is "full redeploy, always."

### 2b. Even if rows persist, they come back **DISABLED**. Always. No setting changes this.

The serialized `Userdata` blob for strategy 399562867 (11,348 B → UTF-16 → XML) holds `DaysToLoad=365`,
`Calculate=OnBarClose`, `StartBehavior=WaitUntilFlat` and every input — and **zero** occurrences of
`enable`/`state`/`active`. The `Strategies` schema has **no enabled column**. NT8's ATI exposes eight
commands, all order/position level. `Tools > Options > Strategies` has no resume setting
(*"Number of restart attempts"* is **connection-loss only** — do not misread it).

⇒ **There is no configuration in which NT8 comes back trading by itself.** An unattended
Windows-update reboot at 03:00 leaves the book **dead until a human arms it.**

## 3. Q3 — the correct model

1. **One dedicated always-on host.** The goal is not graceful restarts; it is **rare** restarts.
2. **Restarts are scheduled, checklisted, and ALWAYS FLAT.** Weekly at most, after Friday's close.
3. **One workspace, saved after every change.** Rule: **UNSAVED = UNDEPLOYED.**
4. **Account-hosted headless is correct** — we already have it. It does *not* buy restart survival;
   that is not the axis. Do not switch hosting mode hoping for durability.
5. **The re-arm is a machine-verified checklist**, never a glance. See §5.
6. **An external drift detector** — CrossTrade already drives the real grid, so a supervisor can diff
   desired-vs-actual and **ALERT**. ⛔ **Detect-and-alert only.** Auto-enabling is a live-trading
   action requiring explicit recorded owner authorization (CLAUDE.md §1).

**What other traders actually do:** they get up and arm it. The minority who automate use
GUI-scripting or an unsupported add-on. Shops that refuse a human in the loop don't run a desktop GUI
as production at all — they run a supervised headless process against the FCM gateway with persisted
position state and a broker reconciliation loop on every start.
⚠️ *That last sentence is INFERRED industry background, not sourced this session — re-research before
it justifies any stack decision.*

## 4. Back-adjustment: the concern was right to raise, and the answer is **it is safe — do not "fix" it**

Global merge policy is **MergeBackAdjusted**; all four roots defer to it. The offsets are real and
large — the last four NQ splices sum to **+985.00 points (~$19,700/contract)** at the one-year edge.

**But every price-level state in this book is consumed through differences or ranks, so a constant
offset cancels exactly:**

- P1's 460-bar sigma runs over a **queue of diffs** (the warm-up gate is literally `sigma_diffs`).
- P1's ratchet compares `px` against `mAnchor ± mS` — **same series, both shifted**.
- P1's quality window uses distances/run-lengths against **quantiles of their own history** (rank-based).
- XM is **not** difference-based — it is a **log-ratio** composite (`Math.Log(Closes[i][0]/anchorX[i])`)
  over three back-adjusted series. It survives for a *different* reason: `z = r/sigma` with sigma the
  trailing-60-session std of the same ratio, so common multiplicative compression cancels; the
  residual is a **<1 % scale transient** over the ~60 sessions straddling each splice.

⛔ **DO NOT switch to MergeNonBackAdjusted.** It would insert a real ~282-point jump at each splice
directly into the diffs queue feeding the 460-bar sigma. It looks like a fix and is active harm.
**Stronger reason still:** the research substrate was itself exported from NT8 under
MergeBackAdjusted (`runs/SM1M_ES_SUBSTRATE/build_meta.json`, 1,620,385 bars) and the Python never
re-derives the convention — it inherits NT8's. Changing it makes the live series **a different object
from the one all the evidence was measured on.**

Also: NT8 re-warms from bar 0 on every enable, so the re-based history at a roll yields an
**equivalent** state, not a corrupted one. No stale anchor survives a re-point.

## 5. Standing defects and pre-roll work

| # | item | status |
|---|---|---|
| 1 | ✅ **CLOSED for the live P1 leg (the only deployed leg since 2026-09-03)** — `ExpectInstrument="NQ 09-26"` **and** `ExpectMnq="MNQ 09-26"` are armed and logged (`HD05 primary OK` / `MX01 exec OK`). ⚠️ **Standing requirement: these are DEPLOY-TIME inputs. They revert to `""` = DISABLED on every redeploy and MUST be re-passed at the roll** (`ExpectInstrument="NQ 12-26"`, `ExpectMnq="MNQ 12-26"`). Historical: P1's guard shipped disabled through the whole first forward window; XM's fired for real on 2026-08-30 (09:20:21 `CROSS-SERIES-MISMATCH`). **Set `ExpectInstrument="NQ 12-26"` at the roll.** XM's guard is armed and **fired for real today** (09:20:21 `CROSS-SERIES-MISMATCH`). | VERIFIED |
| 2 | **December minute history does not exist locally**: `NQ 12-26` **has no directory**, `ES 12-26` has **0 files**, `RTY/YM 12-26` no directory. All four legs must download ~365 days at roll time, and Sep→Dec offsets are NaN until NT8 computes them. **Pre-flight days ahead** with a throwaway chart. | VERIFIED |
| 3 | **No resting protective orders anywhere.** Zero `SetStopLoss`/`SetProfitTarget` in either file; `DisasterStopPoints = 0`. **Every stop is synthetic**, computed in code and fired as a market order at bar close by the live strategy. ⇒ if NT8 dies holding a position the position is **naked**, and *"never restart while positioned"* is **load-bearing, not hygiene**. | VERIFIED |
| 4 | **NT8's own backup has NEVER run** (`LastTimeBackup 01/01/1800`). There is no snapshot to recover a wiped grid from. A manual copy of `db\NinjaTrader.sqlite` was taken 2026-08-30 20:20. | VERIFIED |
| 5 | **Cached login token expires 2026-08-30 23:46.** A restart after expiry may require interactive login — an independent reason no host here is self-restoring. | VERIFIED |
| 6 | `ConnectionLossHandling=Recalculate`, 4 restarts/5 min. A >10 s feed loss **silently stops and recalculates** a strategy, after which the row still reads `isEnabled=true / state=Realtime` and passes a naive check. Today's log shows four HDS cycles (10:16–10:26) and two price-feed losses (11:08, 17:21). | VERIFIED |
| 7 | Two **stale DB rows** (399562865 `WeeklyEdgeP1PCT_v1`, 399562866 `WeeklyEdgeXMConflict_v2`) exist in `db\NinjaTrader.sqlite` but **NOT** in the grid (`ListAllStrategies(includeTerminal=true)` = 2). They cannot be removed via the UI. Risk: if a restore surfaces them, a human could arm a **superseded version** distinguished only by a suffix. | VERIFIED |

## 6. Acceptance set — what to assert after ANY enable

A naive *"is something enabled?"* check passes a permanently-blocked book **and** a 20-lot on the
wrong instrument. Assert all of:

0. 🔴 **Assert the account explicitly, PER BOOK — there are now TWO.** `2047681` is the **LIVE
   real-money** book; `DEMO8383477` is the paper forward-evidence book. Never assert one and assume
   the other. **Run the whole set twice, once per account.** Use `ListAllStrategies` — `ListStrategies`
   returned 2 of 4 rows on 2026-09-01 and both were stale shells.
1. 🔴 **ACCEPTANCE-LIVE (updated 2026-09-05):** `account == 2047681`; exactly **1** row; class
   name exactly `WeeklyEdgeP1PCTMnq_v1` (`399562885`); **two** series (NQ decision + **MNQ as the
   execution series**); `mnq_per_nq = 3`; `ExpectInstrument` **and** `ExpectMnq` both armed and
   matching in contract month. 🔴 **A second row on `2047681` is a DEFECT — XM was WITHDRAWN TO
   OBSERVATION 2026-09-05** (`OWNER_DECISION_20260905_XM_WITHDRAWN.md`).
2. **ACCEPTANCE-PAPER:** `account == DEMO8383477`; **0 rows expected while the paper book is
   down (since 2026-09-03 19:06)**; if the owner restores it: exactly **2** rows, the HD
   challenger classes per `DEPLOY_HD23_20260921.md`.
3. XM's `instruments[]` = NQU6 **and** ESU6/RTYU6/YMU6, **all the same contract month**
   (⚠️ XM's scalar `instrumentName` reports a *secondary* series — read `instruments[]`/`currentBars[0]`, never the scalar)
4. `state=Realtime`, `isEnabled=true`, position **Flat**, `activeOrderCount=0`
5. `currentBars[0]` **monotonically increasing** (never a hard-coded literal)
6. warm-up certificate `verdict=GO` with `qual_entries ≥ 250`, `xm_hist_* ≥ 60`
7. 🔴 **the `ROLL-PLAN` line, and assert `blockNewEntriesFrom` falls in the NEXT quarter.** This is
   the check that catches §0 and it is the one everyone omits.
8. alert on any `ROLL-BLOCK` or `ENTRY-BLOCKED … roll=True` line
9. record `ordersCount`/`activeOrderCount` and reconcile **strategy position vs account position** —
   sync happens **once** at start and nothing ever re-checks it

## 7. What NT8 cannot do (stop looking for the setting)

Unattended auto-arm · automatic roll of a running strategy · a continuous tradable symbol · ongoing
strategy↔account position reconciliation · crash-safe strategy state · process supervision.

The architectural exit, if these ever become unacceptable, is to demote NT8 to an **execution
endpoint** (ATI is already enabled here, port 36973) with signals from the Python substrate. Cost:
we would own position state, bracket management and broker reconciliation ourselves.

---

## 8. EXECUTION PLAN — the one deliberate restart

**Owner authorized (2026-08-30 night): restart permitted, full permissions, a brief trading pause is
acceptable.** The plan below needs **no pause at all**, which is strictly better.

### Timing: **Monday 2026-08-31, 17:00–18:00 ET** — the daily session break

Not tonight. The restart buys two things — flushing the retired types from NT8's in-memory image, and
running the persistence experiment — and **neither is urgent**, because the code currently executing
is already the correct code. Doing it in the daily 17:00–18:00 break costs **zero** trading time,
whereas restarting mid-session costs real P1 overnight exposure. Both legs are also **structurally
flat** at session end (P1 `ForcedFlatMin=21` + last-bar exit; XM `ExitHm` 15:45), which satisfies the
load-bearing rule *never restart while positioned*. ~18 hours of runway before the 09-06 block.

*(Minor accepted cost: `CachedTokenExpiration` is 2026-08-30 23:46, so Monday's restart will likely
prompt an interactive login. The owner is at the machine; this is an annoyance, not a risk, and it is
not worth losing a session to avoid.)*

### December data pre-flight — DONE 2026-08-30 23:04 ET, and it confirms "do not roll early"

`GetBars(NQ 12-26)` **succeeded** — NQZ6 minute data downloads fine, so the roll will not be blocked
by a missing-history surprise. ✅ Item 2 of §5 is cleared for NQ.

But the liquidity comparison is stark and independently confirms §0:

| | NQU6 (Sept) | NQZ6 (Dec) |
|---|---|---|
| session volume | **5,532** | **262** (~5 %) |
| bid/ask | 29475.00 / 29476.50 (**6 ticks**) | 29650.50 / 29654.00 (**14 ticks**) |
| per-minute volume | — | 1, 2, 4 |

**Rolling early would put the paper book on a contract with ~5 % of the liquidity and a >2× spread**,
contaminating exactly the execution evidence the shadow ledger exists to collect.

### Sequence

| step | who | action |
|---|---|---|
| 0 | me | Confirm both legs **Flat**, `activeOrderCount 0`, session closed. Fresh `db\NinjaTrader.sqlite` backup. Snapshot the grid for comparison. |
| 1 | **owner** | Control Center → **Workspaces → Save Workspace**. *This is the experiment.* |
| 2 | **owner** | **File → Exit.** If prompted *"Do you want to save workspace 'Default Yuke'?"* → **YES**. Relaunch NT8, log in if asked, wait for **Simulation** connected. |
| 3 | me | **Read the experiment result.** `ListAllStrategies`: rows present ⇒ persistence confirmed, future restarts are a 2-click re-arm. Rows absent ⇒ hypothesis dead, the model becomes *full redeploy, always*. **Either result is a win — it ends the guessing.** |
| 4 | me | Verify the cleanup landed: read the DLL TypeDef table and `SearchNinjaScriptSymbols` — expect **only 2** WeeklyEdge types in **ONE** assembly (today there are 6 across 3). |
| 5 | me | Re-arm both on **NQ 09-26** (⛔ *not* December), `DaysToLoad=365`, **plus one improvement: set P1 `ExpectInstrument="NQ 09-26"`** — this arms HD-05, which is currently disabled and is P1's only guard besides the latching roll block. Safe: `Instrument.Expiry` is the month marker 2026-09-01, so it matches. |
| 6 | me | Full §6 acceptance set. **The check that matters: `ROLL-PLAN blockNewEntriesFrom` must read 2026-09-08 (P1) / 2026-09-06 (XM) — i.e. in the FUTURE.** If either reads a past date, the book is latched-dead: stop and do not trade. |

### Then the calendar

- **09-08 (P1)** — the book stops taking **new entries**. **Expected, not a fault.**
  Record it in the shadow ledger as a *structural gap* so it is never read as a signal drought.
  *(XM's 09-06 date is moot — withdrawn to observation 2026-09-05.)*
- **2026-09-19 (practically Mon 2026-09-21) — redeploy the LIVE P1 leg ONLY**, per
  `DEPLOY_HD23_20260921.md` (the HD challenger class).
  🔴 **LIVE `2047681`**: re-point P1's **TWO** series (NQ + MNQ) to **12-26**, and set **both**
  `ExpectInstrument="NQ 12-26"` **and** `ExpectMnq="MNQ 12-26"` — the MNQ default is `MNQ 09-26`
  and `MxInstrumentGuard` hard-halts on a month mismatch. `MnqPerNq` — owner's decision (OQ-7
  open); carry 3 forward only if unchanged. Then re-enable and **assert the new `ROLL-PLAN`
  points at the December roll (~2026-11-30)**. Re-run the December pre-flight for **`MNQ 12-26`**
  first — only NQ has been cleared, and **`MNQ 12-26` has never been probed.**
  **PAPER `DEMO8383477`** (only if the owner restores the forward-evidence book): re-point all
  four series to **12-26**, set `ExpectInstrument="NQ 12-26"` (+ ES/RTY/YM 12-26 on paper XM).
  **XM on the LIVE account is NOT redeployed** unless the owner reverses the withdrawal.
- ⛔ **No restarts between 09-06 and 09-18 inclusive.** Pointless (the book is already blocked) and it invites
  a re-enable inside the latch window.

### Standing rules this establishes

1. **Never restart while positioned.** Every stop in this book is synthetic and dies with the
   strategy — a dead strategy holding a position leaves it **naked**.
2. **UNSAVED = UNDEPLOYED.**
3. **After every enable, run the acceptance set — including the ROLL-PLAN assertion.**
4. Restarts are **scheduled, flat, and in the 17:00–18:00 break.** Never ad-hoc mid-session.