# RR_W000 — AUDIT of the W119 `BOOK_LOSS_LEDGER` denominators

| | |
|---|---|
| **run class** | **AUDIT** — post-hoc, forensic, reads only a committed artifact |
| date | 2026-08-27 |
| artifact audited | `runs/WE_W119_BOOKLOSS/out/book_loss_ledger.csv` (1,058 × 25) |
| reproduction | `audit_w119_denominators.py` → `out/audit.txt` |
| alpha budget | **zero.** No hypothesis selected, no population redefined, no candidate promoted |
| provenance | found during Phase 0 onboarding of the causal-monetization campaign, while reading W119 as the closest existing analogue to the planned ACTION-VALUE LEDGER |

> **No preregistration is claimed and none is owed.** This selects nothing. It re-derives figures
> that `CURRENT_BASELINE.md` quotes and checks which mask each was computed on. Writing a
> "prediction" after the answer was already computed would be dishonest, so this is labelled for
> what it is: an audit, in the same category as `runs/O2_NUMERIC_PROVENANCE_AUDIT/` and
> `runs/EVIDENCE01_REPORT_TRACEABILITY/`.

---

## Finding 1 — the "winning sessions" denominator is contaminated by structurally flat sessions

W119 contrasts losing sessions against `~(book_pnl < 0)`. That complement is **not** "winning
sessions" — it is winning **plus flat**:

| | n |
|---|---:|
| `book_pnl < 0` — LOSING | **405** |
| `book_pnl > 0` — WINNING | **371** |
| `book_pnl == 0` — FLAT | **282** |
| `~(book_pnl < 0)` — the denominator actually used | **653** |

**All 282 flat sessions have `p1_trades == 0` and `xm_active == 0`** — verified, 282 of 282. A
session in which neither leg holds a position cannot have a non-zero P&L, so those rows are
*guaranteed* to contribute zero trades. Including them in the comparison bucket mechanically drags
its trade count toward zero.

| statistic | LOSING | NOT-LOSING *(used)* | WINNING *(correct)* | quoted ratio | correct ratio |
|---|---:|---:|---:|---:|---:|
| P1 trades / session | 3.0420 | **1.3767** | **2.4232** | 2.210× | **1.255×** |
| P1 contract-minutes | 199.0 | 242.1 | 426.1 | 0.822× | **0.467×** |
| \|RTH move\| pts | 116.54 | 168.03 | 175.36 | 0.694× | 0.665× |
| RTH range pts | 268.17 | 281.58 | 293.14 | 0.952× | 0.915× |

> ### **The turnover contrast is 3.04 vs 2.42, not 3.04 vs 1.38 — overstated ~1.75×.**
> The contract-minute claim moves further and in the *opposite* direction from how it was read:
> losing sessions carry **53 %** fewer contract-minutes than winning ones, not 18 % fewer than
> not-losing ones. **The session-move figure barely moves** (31 % → 34 % less) and survives intact.

**Every number in the LOSING column is unchanged.** The defect is in the comparator, not the
measurement.

## Finding 2 — `E_NO_ENGINE = 0` is forced by construction and measured nothing

W119's spec defines the lens as *"neither leg held a position while the session's absolute RTH move
was in its own top decile. Opportunity absent rather than mishandled."*

The lens was then evaluated **inside the losing-session population**:

| mask | n |
|---|---:|
| neither leg active | 282 |
| … **and** in the top-decile \|RTH move\| (≥ 295.0 pts) | **32** ← the raw mask |
| … **and also** `book_pnl < 0` | **0** ← what the report printed |

Distinct `book_pnl` on the raw mask: **`[0.0]`** — the only value it can take.

> ### **A session with no position has `book_pnl == 0` and can never satisfy `book_pnl < 0`.**
> **The cell was empty before any data was read.** It is not a measurement of coverage; it is a
> tautology. The correct raw count is **32 sessions**, mean \|RTH move\| **452.2 pts**, mean RTH
> range **587.9 pts**.

Those 32 sessions are **absences, not losses**. Attaching a dollar figure to them requires knowing
the direction in advance, which makes any such figure `EX_POST_EXECUTION_FEASIBLE_ORACLE` — **level
2, not available money.** `OPPORTUNITY_LANGUAGE.md` is binding on precisely this, so this audit
prices nothing.

---

## What changes, and what does not

**CHANGES**

1. *"`E_NO_ENGINE` = 0 sessions — coverage is genuinely not the gap"* is **not supported by this
   artifact.** Coverage was never measured on that lens. The honest status of book coverage is
   **UNMEASURED**, not closed. 32 top-decile-move sessions had no engine present.
2. The turnover contrast is overstated ~1.75× by the denominator.

**DOES NOT CHANGE**

3. **Turnover stays dead.** W121 killed the *inference* on independent evidence — entry-count caps
   lose at every K and sit at the **0.0/4.0/1.0/0.0th percentile** of a count-matched random-halt
   placebo, and the 4th entry is the *best* cell. The corrected, **weaker** contrast (1.255× rather
   than 2.210×) is *more* consistent with W121, not less. **This does not reopen turnover.**
4. **No object changes status, no result is reversed, nothing is promoted or demoted.**
5. **W119's `REPORT.md` is not rewritten.** It is immutable evidence. The correction lands in the
   state document, which is what state documents are for.

## Consequence for the campaign

Book **coverage** returns to the frontier as an **open but low-EVI** question rather than a closed
one — low because P1/PCT is **long-only** and declines to trade for stated mechanical reasons, so
"no engine was present" is frequently the correct behaviour rather than a miss. It is recorded in
`research/router/RESEARCH_FRONTIER.md` and is **not** the next wave.

**Method note this audit adds to the standing list:** *a lens counted inside a population that its
own definition excludes will report zero, and zero will read as evidence of absence.* Any future
"the engine was absent" category must be counted on its **raw** mask first, and only then intersected
— with the intersection labelled as a subset, never as the measurement.
