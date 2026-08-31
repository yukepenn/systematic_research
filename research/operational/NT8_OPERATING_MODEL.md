# NT8 PRODUCTION OPERATING MODEL — contract roll, restart persistence, and the roll-block trap

**Written 2026-08-30 evening**, from a 7-agent audit plus two adversarial skeptics, after the owner
asked: *"doesn't NinjaTrader auto-select the active contract? do we really redeploy after every
restart? what is the correct way? what do other systematic traders do?"*

Supersedes the relevant lines of `NT8_RUNBOOK.md` and corrects two rules recorded earlier the same
day. **Paper book only. LIVE real money = NO.**

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
| P1 | **2026-09-08 → 09-16** | 2026-09-08 | **blocked instantly, forever** |
| XM | **2026-09-06 → 09-18** | 09-06/07/08/10 | **blocked instantly, forever** |

The book would read **Enabled · Realtime · bars advancing · warm-up GO · flat** and take **zero
trades indefinitely.** Every item in the obvious acceptance checklist passes.

### ✅ Safe re-enable dates: **P1 on/after 2026-09-17 · XM on/after 2026-09-19**

(XM waits for YM's 09-18, the latest of its four series; it then resolves to RTY 2026-12-08 →
`blockFrom` 2026-11-30.)

### And the cost of waiting is ZERO

The reasoning that produced the bad plan was *"don't trade a dying contract."* **Wrong direction:
the strategies already refuse new entries from 09-06 / 09-08 by design.** Nothing enters between
09-08 and 09-19 under any plan. Waiting forfeits **nothing**; rolling early forfeits **everything**.

⚠️ **Consequence to accept: a ~10-day new-entry gap (09-06/08 → 09-17/19) in the forward evidence
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
| 1 | **P1's instrument guard is DISABLED** — `ExpectInstrument=""` and `:682` returns immediately when empty. P1's *only* roll protection is the latching block. **Set `ExpectInstrument="NQ 12-26"` at the roll.** XM's guard is armed and **fired for real today** (09:20:21 `CROSS-SERIES-MISMATCH`). | VERIFIED |
| 2 | **December minute history does not exist locally**: `NQ 12-26` **has no directory**, `ES 12-26` has **0 files**, `RTY/YM 12-26` no directory. All four legs must download ~365 days at roll time, and Sep→Dec offsets are NaN until NT8 computes them. **Pre-flight days ahead** with a throwaway chart. | VERIFIED |
| 3 | **No resting protective orders anywhere.** Zero `SetStopLoss`/`SetProfitTarget` in either file; `DisasterStopPoints = 0`. **Every stop is synthetic**, computed in code and fired as a market order at bar close by the live strategy. ⇒ if NT8 dies holding a position the position is **naked**, and *"never restart while positioned"* is **load-bearing, not hygiene**. | VERIFIED |
| 4 | **NT8's own backup has NEVER run** (`LastTimeBackup 01/01/1800`). There is no snapshot to recover a wiped grid from. A manual copy of `db\NinjaTrader.sqlite` was taken 2026-08-30 20:20. | VERIFIED |
| 5 | **Cached login token expires 2026-08-30 23:46.** A restart after expiry may require interactive login — an independent reason no host here is self-restoring. | VERIFIED |
| 6 | `ConnectionLossHandling=Recalculate`, 4 restarts/5 min. A >10 s feed loss **silently stops and recalculates** a strategy, after which the row still reads `isEnabled=true / state=Realtime` and passes a naive check. Today's log shows four HDS cycles (10:16–10:26) and two price-feed losses (11:08, 17:21). | VERIFIED |
| 7 | Two **stale DB rows** (399562865 `WeeklyEdgeP1PCT_v1`, 399562866 `WeeklyEdgeXMConflict_v2`) exist in `db\NinjaTrader.sqlite` but **NOT** in the grid (`ListAllStrategies(includeTerminal=true)` = 2). They cannot be removed via the UI. Risk: if a restore surfaces them, a human could arm a **superseded version** distinguished only by a suffix. | VERIFIED |

## 6. Acceptance set — what to assert after ANY enable

A naive *"is something enabled?"* check passes a permanently-blocked book **and** a 20-lot on the
wrong instrument. Assert all of:

1. `account == DEMO8383477` (a second Provider-50 account `2047681` exists on this box — never omit this)
2. exactly **2** rows; class names exactly `WeeklyEdgeP1PCT_v2`, `WeeklyEdgeXMConflict_v3`
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
