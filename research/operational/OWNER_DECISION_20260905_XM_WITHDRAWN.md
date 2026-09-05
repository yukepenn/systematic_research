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

**XM's ENTIRE live evidence is ONE TRADE.**

```
2026-09-01 09:45   XM_S  SHORT 3 MNQ @ 29081.9167   (filled 2 @ 29082 then 1 @ 29081.75)
2026-09-01 15:45   XM_X  COVER 3 MNQ @ 29114.0000
                   -32.083 pts x 3 x $2  =  -$192.50 gross   /   -$196.34 net
```

⭐ **The execution was $11.50 BETTER than the research assumption.** The strategy assumed a
short from 29084 to 29118 (−34 pts, −$204.00 at 0.30 scale); it got −32.083 pts. **The loss is
the signal's, not the plumbing's** — and the plumbing is the thing MX01 was built to verify.

🔴 **Everything after that trade is an INSTRUMENT FAILURE, not a performance record.** XM
latched at 2026-09-01 13:23 (HD-20: any restart holding a position guarantees
`RECONCILE-BREAK`) and refused **every** entry for the next two days — 1,218 error lines — while
`ListAllStrategies` reported it Realtime, enabled and healthy. Its live writer then died on
09-02 10:40 (HD-22). See `INCIDENT_20260903_GHOST_POSITION.md` §7 and `forward_v2/gaps.csv`
seq 3–4.

> ### ⚠️ THEREFORE: **"XM is underperforming" is NOT a conclusion this data can carry.**
> n = 1. One trade cannot distinguish a broken edge from a coin flip, and the two days that
> followed contain **zero** decisions because the leg was structurally disabled. Recording the
> withdrawal as an evidence-based demotion would put a false research claim into the repo that
> a later reader would inherit. **It is recorded as a PRECAUTIONARY WITHDRAWAL.**

## 3 · THE REASONS THAT DO HOLD

Independent of the n=1 live record, four documented facts support standing XM down:

1. 🔴 **XM carries a latching defect that has already fired in production.** HD-20 blocks every
   entry after any restart that carries a position, silently, with all health surfaces green.
   Fixed offline in `WeeklyEdgeXMConflictMnq_v2`; **not deployed.**
2. 🔴 **Its evidence writer is dead** (HD-22, silent catch, no retry). A leg that produces no
   forward evidence cannot earn promotion no matter how it trades.
3. ⚠️ **The "hedge" is a mixture, and it inverts.** ρ(P1, XM) = **+0.408 when XM is long** vs
   **−0.204 when XM is short**, and XM's long share reached **63.3 %** in 2026. Since P1 is
   long-only, the pair becomes *doubling-up* exactly when XM goes long. This is an identity,
   not a forecast, and it was known before this decision.
4. ✅ **`CAP02B` (6/6 gates PASS): P1 alone is ~2.4× less likely to wipe the account than the
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
3. It accumulates a live decision record large enough to say anything at all. **n = 1 is not a
   record**, and the campaign's own power analysis says ~70 % of the time two years cannot
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
