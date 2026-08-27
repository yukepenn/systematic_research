# RR_W006 — BOOK COVERAGE IS NOT A GAP, AND NOW IT IS MEASURED

| | |
|---|---|
| **run class** | **DIAGNOSTIC** — no hypothesis selected, no threshold chosen, nothing promoted |
| date | 2026-08-27 |
| code | `run_rr_w006_coverage.py` |
| reproduction | `out/coverage.txt` · `out/no_engine_sessions.csv` |
| seal | untouched |

> ### **The coverage gap, correctly scoped, is 4 sessions out of 1,058 — 0.38 %.**
> ### **COVERAGE moves from UNMEASURED to CLOSED.** No dollar figure is attached to any absence.

---

## 1. Why this was open

`RR_W000` withdrew W119's *"`E_NO_ENGINE` = 0, so coverage is genuinely not the gap"*: that lens was
counted inside a population its own definition excludes, so it was **empty before any data was
read**. On the raw mask there are **32** sessions where neither leg held a position while the
session's \|RTH move\| was in its own top decile (≥ 295 pts). Coverage was therefore recorded
**UNMEASURED**, not closed — and this measures it.

## 2. Two questions decide it, and neither needs a model

### Direction — `P1/PCT` is long-only

| | n | share | mean \|move\| |
|---|---:|---:|---:|
| top-decile move **UP** | **9** | 28.1 % | 357.3 pts |
| top-decile move **DOWN** | **23** | **71.9 %** | 489.3 pts |

**A long-only engine declining a large DOWN session is the design working, not a miss.** Pricing
those 23 would require a short engine that does not exist — and the short sleeve's own history is
that its edge is an RTH phenomenon that has never survived promotion. **The coverage question
concerns at most the 9 UP sessions.**

### Signal versus policy — did the engine's signal fire, or never fire?

Of the **24** sessions that matched the substrate by date:

| | n | share | what it is |
|---|---:|---:|---|
| signal **fired** but no trade resulted | **16** | 66.7 % | **POLICY**, not coverage |
| signal **never fired** all session | **8** | 33.3 % | genuine coverage absence |

Restricting to the **7 matched UP sessions** — the only ones a long-only book could ever own:

| | n |
|---|---:|
| signal fired but no trade | 3 |
| **signal never fired — THE ACTUAL COVERAGE GAP** | **4** |

## 3. The verdict, and it is robust to the one limitation

**4 sessions out of 1,058 — 0.38 %.**

⚠️ **8 of the 32 sessions did not match the substrate by date** and are excluded from the
signal/policy split. That is a real limitation and it is not hidden. **It does not change the
conclusion:** even in the worst case where *all eight* were UP sessions on which the signal never
fired, the gap would be **12 of 1,058 = 1.1 %** — still far too few to support a new engine, and
still unpriceable.

**No dollar figure is attached.** Pricing an absence requires knowing the direction in advance, which
makes any such figure `EX_POST_EXECUTION_FEASIBLE_ORACLE` — **level 2, not available money.**
`OPPORTUNITY_LANGUAGE.md` is binding on precisely this, and it is the reason W50's "4.46 % capture"
is retired.

**The rest of the raw mask is not a coverage question at all.** It is either a DOWN move a long-only
book is right to decline (23 of 32), or a session where the signal **did** fire and policy suppressed
it (16 of 24 matched) — and the policy half was closed one wave earlier by `RR_W005`, which showed
every uniform relaxation of the box is 16–41 % worse at fixed drawdown.

## 4. What this closes

**Coverage: `UNMEASURED` → `CLOSED`.** W119's original conclusion — *"coverage is not the gap"* — turns
out to have been **right for the wrong reason**. The lens that reported it was a tautology, and
`RR_W000` was correct to withdraw it. Measured properly, on the raw mask and split by direction and
by signal presence, the conclusion survives: **coverage is not the gap.**

> This is what re-measuring a withdrawn claim is supposed to look like. The claim came back, but it
> came back **with an argument instead of an artifact of masking**, and the number attached to it is
> now 0.38 % rather than a structurally guaranteed zero.

## 5. Continuation

| | |
|---|---|
| **outcome** | coverage **CLOSED** at 0.38 % · frontier row 1 closed |
| **runnable rows remaining** | **none** |
| **what is left** | owner-gated acquisition (order flow, options, a wider event calendar), calendar-gated forward reads, and owner capital decisions |
| **promoted / demoted** | **nothing** |
