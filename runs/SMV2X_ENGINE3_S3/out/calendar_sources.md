# Calendar sources — SMV2X_ENGINE3_S3 (seq 396-398)

All three engines trigger on a hardcoded, deterministic public calendar (not derived from the
price substrate). This file documents provenance and confidence for every date list used. The
raw lists live in `calendars.py` (FOMC_DATES, CPI_DATES); engine 398's expiration dates are
computed programmatically (rule given below), not hardcoded as a literal list, because the rule
itself is deterministic and simpler to verify than a hand-typed date table.

## FOMC (engine 397, FOMC cell)

**Source**: `federalreserve.gov/monetarypolicy/fomccalendars.htm` ("Meeting calendars,
statements, and minutes"), fetched live 2026-08-08. Date used = the SECOND day of each two-day
meeting (2:00pm ET statement release).

35 of the 37 dates fetched fall inside the dev window (2022-01-01..2026-05-31); all 35 produced
a usable event (clean 3m-bar coverage around 14:00-14:30 ET and a session close). The two 2026
dates beyond dev end (2026-06-17, 2026-07-29) are listed in `calendars.py` for completeness but
are never used in this run's computation.

Confidence: **HIGH** — fetched directly from the primary source at run time, not reconstructed
from memory.

## CPI (engine 397, "CPI/NFP/PCE" cell — SCOPE NOTE, read this)

**SCOPE DECISION (disclosed, not a silent drop)**: the frozen spec names three release families
("CPI/NFP/PCE") pooled into one cell, with an estimated count of "~48" events over the dev
window. Literally pooling all three monthly series (CPI + NFP + PCE, ~12/yr each, ~53 months of
dev) would yield roughly 150-160 events — about 3x the spec's own estimate — and NFP/PCE do not
have as clean a single fetchable schedule as CPI (the BLS Employment Situation deviates from a
naive "first Friday" rule in specific months; the BEA Personal-Income-and-Outlays/PCE release
has no fixed day-of-month rule at all). Hand-verifying ~100 additional dates across two more
series, each with its own idiosyncratic scheduling exceptions, was judged to exceed this run's
reasonable evidence budget.

**This run implements the cell as CPI-ONLY.** N = 52, which lands almost exactly on the spec's
own "~48" estimate — mild post-hoc evidence that a single-series cadence (not a 3-series pool)
is what was actually intended. NFP and PCE are **DEFERRED, not silently dropped**: flagged here
and in REPORT.md as a named scope limitation, to be picked up in a follow-up wave if e397 proves
interesting enough to warrant Stage-2 characterization (it does not, per REPORT.md's gate
results — see there).

**Source / verification trail**:
- 2025-2026: fetched live from `usinflationcalculator.com/inflation/consumer-price-index-release-schedule/`
  and `cpiinflationcalculator.com/cpi-release-schedule/` (both mirror the official BLS schedule),
  cross-referencing the 2025 government-shutdown disruption directly against
  `bls.gov/bls/092025-cpi-reschedule-notice.htm` and CNBC's 2025-10-10 shutdown-data coverage.
  Spot-verified against the canonical BLS archive URL pattern
  (`bls.gov/news.release/archives/cpi_MMDDYYYY.htm`) for 2025-01-15, 2025-04-10, 2025-05-13,
  2026-01-13 — all landed exactly on the predicted date.
- 2022-2024: reconstructed from confident training-data knowledge of the well-publicized "2nd
  Tuesday-ish of month, 8:30am ET" BLS schedule (several of these dates are widely-cited market
  events, e.g. the 2022-09-13 and 2022-10-13 and 2022-11-10 prints). Spot-verified against live
  BLS archive URLs for 2022-10-13, 2022-11-10, 2024-02-13, 2024-09-11 — all four confirmed exact,
  with no drift from the predicted list.
  **CAVEAT (declared, not silently guessed)**: `bls.gov/schedule/news_release/cpi.htm` and
  `bls.gov/bls/news-release/cpi.htm` (the two canonical full-year-schedule pages) both returned
  HTTP 403 to automated fetch, so the 2022-2024 list is NOT independently verified date-by-date
  against a single canonical source the way 2025-2026 is. Confidence is HIGH given the spot
  checks landed exactly, but this is disclosed as reconstructed-and-spot-verified rather than
  fully independently sourced.

**2025 shutdown-period detail** (load-bearing for correctness, so spelled out): Aug-2025-ref CPI
released on schedule 2025-09-11. Sep-2025-ref CPI delayed 9 days to 2025-10-24 (from a normal
~10-15 slot) so SSA could compute the 2026 COLA. **Oct-2025-ref CPI was canceled outright and
never published** — there is no calendar entry for that slot (not a guess; BLS explicitly did
not produce it). Nov-2025-ref CPI rescheduled to 2025-12-18 (from a normal ~12-10 slot). Dec-
2025-ref CPI returned to a normal cadence on 2026-01-13.

## NFP / PCE (engine 397)

Not included — see the CPI scope-decision note above.

## Index-option expiration (engine 398)

**Rule** (per the task brief, not a fetched one-off list): 3rd Friday of every calendar month.
The quarterly triple/quad-witching dates (Mar/Jun/Sep/Dec) are the *same* 3rd-Friday date —
quarterly expiration just additionally carries index-future expiration on top of the standard
monthly index-option expiration, so no separate date list is needed for "quarterly."

**Implementation**: computed programmatically via pandas' `WOM-3FRI` date offset over the dev
window, then cross-checked bar-by-bar against the actual NQ 3m session calendar (not assumed to
always be a trading day). 53 candidate dates were generated (2022-01 .. 2026-05); **2 were
flagged as NOT a trading session and excluded**, both Good Friday market holidays landing on the
month's 3rd Friday: **2022-04-15** and **2025-04-18**. Both are correctly-known, well-documented
NYSE/CME holiday closures (Good Friday), not calendar-math errors — flagged rather than silently
substituted with an adjacent day. Full flag list: `out/e398_expiry_calendar.csv`
(`in_session_calendar` column).

Confidence: **HIGH** (deterministic rule, verified against the run's own authoritative session
calendar rather than an external holiday table).
