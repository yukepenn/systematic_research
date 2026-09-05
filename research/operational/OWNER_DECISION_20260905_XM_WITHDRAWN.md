# OWNER DECISION 2026-09-05 — XM withdrawn from the EXECUTABLE set, placed on OBSERVATION

**Owner instruction, recorded verbatim in intent:** *"我觉得 xm 现在不太行,所以从 executable
strategies 拿出去了观望"* — XM is taken out of the executable strategies and put on watch.

**Status: EXECUTED.** XM is not deployed on any account. The live book is **P1 alone**.

---

## 1 · WHAT THIS CHANGES, AND WHAT IT MUST NOT

| baseline | owner | effect |
|---|---|---|
| `RESEARCH_SINGLE` | `CURRENT_BASELINE.md` §0 | 🔒 **UNCHANGED** |
| `RESEARCH_PORTFOLIO_FRONTIER` | `CURRENT_BASELINE.md` §0 | 🔒 **UNCHANGED** |
| `EXECUTABLE_SINGLE` | `EXECUTION_MANIFEST.md` | unchanged (P1) |
| **`EXECUTABLE_PORTFOLIO`** | `EXECUTION_MANIFEST.md` | 🔴 **SUSPENDED** — `M_11` has no second leg |

🔴 **This is an OPERATIONAL withdrawal, not a research falsification.** `CLAUDE.md` §3 forbids
collapsing the four baselines, and §4 records the owner doctrine that *old-regime failure is a
RISK CLASSIFICATION, not a promotion veto.* **XM's research status is untouched.** Nothing in
`CURRENT_BASELINE.md` may be edited on account of this decision.

## 2 · WHAT XM's LIVE RECORD ACTUALLY SUPPORTS — read this before quoting it

> ### 🔴 CORRECTION, 2026-09-05, same day: **THE FIRST VERSION OF THIS SECTION WAS WRONG.**
> It reported a completed round trip of **−$192.50** and an execution **$11.50 better** than the
> model. **Both figures are WITHDRAWN.** They were computed from an exit that **never reached the
> broker.** Found by an adversarial reader I commissioned, then verified independently below.

**XM's ENTIRE live evidence is ONE ENTRY AND ZERO EXITS.**

```
2026-09-01 09:45:00   XM_S   Order 18930730071/2047681   MNQU6  SellShort 3   FILLED @ 29081.9167
2026-09-01 15:45:00   XM_X   Order 581992641276/DEMO8383477  NQU6  BuyToCover 1  <- PAPER ONLY
                      grep "name='XM_X'" every trace, filtered to (Live)  ->  0 rows
```

🔴 **No `XM_X` order was ever created on account `2047681`, on any day.** The exit the strategy's
own diag recorded (`EXEC name=XM_X;q=3;px=29114`) was matched against NT8's *internal* strategy
position and **never submitted to Tradovate.**

🔴 **XM's short 3 was closed by the OWNER, at 12:20:46, three and a half hours earlier:**

```
12:20:46  CreateOrder  18930730255/2047681  name=''  MNQU6  Buy 9  Market  -> account FLAT
          (covering 6 manually-added shorts from 10:27 and 10:31, plus XM's 3)
```

Account MNQU6 position on 09-01, from `Cbi.Account.PositionUpdateCallback` — the whole story:

| ET | qty | who |
|---|---|---|
| 09:45:00 | **Short 3** @ 29081.9167 | **XM** (the only strategy order on this account, ever) |
| 10:27:31 | Short 6 | owner, manual |
| 10:31:03 | Short 9 | owner, manual |
| **12:20:46** | **FLAT** | **owner, manual Buy 9 — this is what closed XM's position** |

> ### ⇒ **THERE IS NO SCOREABLE XM LIVE P&L. `−$192.50` IS NOT A REALISED NUMBER.**
> The exit price 29114 never occurred on this account. Anyone quoting it is quoting a fill that
> did not happen.

**The one real execution datum is the ENTRY, and it was ADVERSE:** the model assumed selling at
29084; the fill sold at 29081.9167 — **2.083 pts lower, and lower is worse for a short** =
**−$12.50 on 3 MNQ.** (My earlier "+$11.50 better" was the phantom exit's arithmetic. Withdrawn.)

🔴 **THIS IS THE SAME GHOST-POSITION DEFECT AS 2026-09-03 — AND IT FIRED HERE FIRST, TWO DAYS
EARLIER, ON XM.** Owner closes a strategy's position by hand → NT8 never tells the strategy →
the strategy's ledger and the account diverge silently. On 09-03 that made P1's exit *open* a
naked short. Here on 09-01 it made XM's exit *evaporate*, and it destroyed the only live trade
record XM will ever have from that deployment. See
[`INCIDENT_20260903_GHOST_POSITION.md`](INCIDENT_20260903_GHOST_POSITION.md) §14.
**HD-23 is therefore fixing a defect with n=2, not n=1.**

🔴 **Everything after that trade is an INSTRUMENT FAILURE, not a performance record.** XM
latched at 2026-09-01 13:23 (HD-20: any restart holding a position guarantees
`RECONCILE-BREAK`) and refused **every** entry for the next two days — 1,218 error lines — while
`ListAllStrategies` reported it Realtime, enabled and healthy. Its live writer then died on
09-02 10:40 (HD-22). See `INCIDENT_20260903_GHOST_POSITION.md` §7 and `forward_v2/gaps.csv`
seq 3–4.

> ### ⚠️ THEREFORE: **"XM is underperforming" is NOT a conclusion this data can carry.**
> **It is weaker than n = 1 — it is n = 0 completed trades.** There is one entry, no exit, and
> no realised P&L; the two days that followed contain **zero** decisions because the leg was
> structurally disabled. Recording the withdrawal as an evidence-based demotion would put a
> false research claim into the repo that a later reader would inherit.
> **It is recorded as a PRECAUTIONARY WITHDRAWAL.**

## 3 · THE REASONS THAT DO HOLD

Independent of the (non-existent) live P&L, five documented facts support standing XM down:

1. 🔴 **XM carries a latching defect that has already fired in production.** HD-20 blocks every
   entry after any restart that carries a position, silently, with all health surfaces green.
   Fixed offline in `WeeklyEdgeXMConflictMnq_v2`; **not deployed.**
2. 🔴 **Its evidence writer is dead** (HD-22, silent catch, no retry). A leg that produces no
   forward evidence cannot earn promotion no matter how it trades.
3. 🔴 **Its only live position was silently destroyed by the ghost-position defect** (§2), so
   the deployment produced **no scoreable evidence at all** — which is itself a reason to stand
   the leg down until HD-23 ships.
4. ⚠️ **The "hedge" is a mixture, and it inverts.** ρ(P1, XM) = **+0.408 when XM is long** vs
   **−0.204 when XM is short**, and XM's long share reached **63.3 %** in 2026. Since P1 is
   long-only, the pair becomes *doubling-up* exactly when XM goes long. This is an identity,
   not a forecast, and it was known before this decision.
5. ✅ **`CAP02B` (6/6 gates PASS): P1 alone is ~2.4× less likely to wipe the account than the
   pair at the same `MnqPerNq = 3`** — 2-yr P(ruin) **0.025 vs 0.061** (full pool), 0.008 vs
   0.017 (warm). The n=1 realised-path anchor points the same way: at 3 MNQ the pair would have
   been **wiped out** (trough $14,380 = 140 % of equity, March 2022); P1 alone **survived**
   (trough $7,077 = 69 %).

⚠️ **And the cost of the decision, stated beside the benefit:** dropping a leg drops its return
too. `CAP02B` measured *ruin*, not *return*, and deliberately recommends no size and takes no
position on whether the pair is the better investment.

## 4 · CONDITIONS TO REVISIT

XM returns to the executable set only when **all** of these hold:

1. `WeeklyEdgeXMConflictMnq_v2` is deployed (HD-20 + HD-22 fixed) — `DEPLOY_HD23_20260921.md`.
2. Its forward writer is verified **ALIVE** by `writer_watchdog` across a full session.
3. It accumulates a live decision record large enough to say anything at all. **One entry with
   no exit is not a record**, and the campaign's own power analysis says ~70 % of the time two years cannot
   separate this edge from zero.
4. The owner re-authorises. **Enabling remains an owner action in the NT8 UI, always.**

## 5 · WHAT IS LIVE RIGHT NOW

`WeeklyEdgeP1PCTMnq_v1/399562885` on `2047681`, `MnqPerNq = 3`, Realtime, flat.
🔴 **Its roll guard blocks new entries from 2026-09-08** (`ROLL-PLAN`, resolved 09-03 22:28:03).
Exits are never gated. December redeploy on/after **2026-09-21** —
`CURRENT_LIVE_TRUTH.md` §ROLL is the authority.

**Live risk of the object that is actually running:**
`runs/CAP02B_P1_ONLY_RUIN_CORRECTED_20260905/` — 2-yr P(ruin) at 3 MNQ **0.025** full pool,
honest band **~2 %–20 %**, **0.483 if the edge is zero**. `DISCOVERY_CONSUMED`, a lower bound.
🔴 **Never quote `CAP01B`'s 6.5 % for this book — that is the PAIR's number.**
