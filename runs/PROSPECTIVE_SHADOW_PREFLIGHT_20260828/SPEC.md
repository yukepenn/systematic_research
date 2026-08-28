# SPEC — `PROSPECTIVE_SHADOW_PREFLIGHT`

**COMMIT B. `ENGINEERING_ONLY`.** Zero alpha budget.

> ## ⛔ **THIS RUN MAY NOT RECORD A REAL PROSPECTIVE OUTCOME.**
> `SHADOW_START = 2026-09-01 18:00 ET` has **not arrived** (today is 2026-08-28). Every ledger this
> run writes is a **TEST ARTIFACT** in its own `out/` directory, named `_preflight_*`, and **no
> row it writes may ever enter the real shadow ledger.** The real ledger does not exist yet and this
> run does not create it.

**Purpose:** prove *mechanically* that the shadow apparatus is ready — and that each of its guards
**can actually reject**. A guard that cannot fire is worthless.

---

## 1. Roster — recovered from repo truth, not from the directive

Read from `research/operational/PROSPECTIVE_SHADOW.md`. For each object record: source path ·
source sha256 · parity status · evidence class · decision schedule · cost convention · account
safety state. ⛔ **No object joins because it is historically interesting.**

## 2. Tests — each must demonstrate it can FAIL

| # | test | requirement |
|---|---|---|
| **S0-1** | **START GUARD** | a decision timestamp **before**, **exactly at**, and **after** `SHADOW_START` must be handled exactly per the frozen no-backfill contract. The first two must be **REJECTED**, and the test asserts the rejection |
| **S0-2** | **DECISION FIRST** | a decision is written before its outcome exists; outcome rows reference an immutable decision id; **no decision row may later be edited to carry its result** — attempting it must be refused or detected |
| **S0-3** | **HASH CHAIN** | tamper with a written row; `verify()` **must fail**. Asserted, not assumed |
| **S0-4** | **CLOCK** | timezone and ET/DST handling · `session_id` assignment · **18:00 → 17:00** session semantics · strictly monotonic decision timestamps · strict row ordering. Uses `research_sdk/test_session_unit.py`, the guard built after Program B |
| **S0-5** | **QUALITY FAIL-CLOSED** | absent or bad input must produce a **recorded `BLOCKED` decision with a reason**, never a silent omission. **A silently dropped row creates a selected sample**, which is the failure mode the ledger exists to prevent |
| **S0-6** | **ZERO ORDER PATH** | **structural** proof: no brokerage/order call, no order submission, no strategy enablement, no Sim→Live switch, no external order path — verified by **AST import and call analysis**, not by grep |

## 3. WRITE vs READ — made mechanical

| | |
|---|---|
| **WRITE** | prospective decision/outcome logging. **Permitted from `SHADOW_START` onward** |
| **READ** | performance interpretation. **Governed** — `LOCKED_FORWARD.md` / `MONITORING_CALENDAR.md` for the incumbent NQ objects; **S26/S52/S104 are specified but NOT ARMED** because no weekly candidate exists |

**Allowed before an authorised read:** process alive · decision count · blocked-row count ·
data-quality status · hash integrity · source continuity · clock continuity · missingness.
⛔ **Not allowed:** P&L · hit rate · Sharpe · equity curve · cumulative net · "looks good" ·
any discretionary peek. **The preflight ships a `health()` function that can only return the allowed
set** — the restriction is code, not a promise.

## 4. Deliverables

`out/preflight.txt` · `out/preflight.json` · `out/roster.csv` · `REPORT.md`.
**`LIVE ENABLED = NO`.**
