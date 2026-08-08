"""SMV2X_ENGINE3_S3 hardcoded event calendars (deterministic; NOT derived from the price
substrate). Full source list and per-date confidence notes are written to
out/calendar_sources.md by smv2x.py. Summary of provenance:

FOMC (engine 397): statement/release day of each 2022-2026 FOMC meeting (2:00pm ET), the
  SECOND day of each two-day meeting. Source: federalreserve.gov "Meeting calendars, statements,
  and minutes" page (fetched live 2026-08-08). 2026 dates only published by the Fed through
  July 2026 as of fetch time; dev window only needs through 2026-05-31 (Jan/Mar/Apr 2026),
  which are covered.

CPI (engine 397, "CPI/NFP/PCE" cell -- SCOPE NOTE: implemented as CPI-ONLY, see caveat below):
  Consumer Price Index news release day (8:30am ET). 2025-2026 dates fetched live from BLS-
  sourced mirrors (usinflationcalculator.com, cpiinflationcalculator.com) and spot-verified
  directly against bls.gov archive URLs (pattern cpi_MMDDYYYY.htm) for several months incl. the
  2025 government-shutdown schedule disruption (Sep-2025-reference-month CPI delayed to
  2025-10-24; Oct-2025-reference-month CPI CANCELED/never published -- no calendar entry for
  that slot; Nov-2025-reference-month CPI rescheduled to 2025-12-18). 2022-2024 dates
  reconstructed from confident training-data knowledge of the well-publicized "2nd Tuesday-ish
  of month" BLS schedule and spot-verified against live bls.gov archive URLs for several
  widely-cited months (2022-10-13, 2022-11-10, 2024-02-13, 2024-09-11) -- all confirmed exact.
  CAVEAT (declared, not silently guessed): the 2022-2024 list is NOT independently fetched
  month-by-month from a single canonical schedule page (bls.gov/schedule/news_release/cpi.htm
  and bls.gov/bls/news-release/cpi.htm both returned HTTP 403 to automated fetch); confidence is
  HIGH given the spot-checks landed exactly on the predicted dates with no drift, but this is
  disclosed as reconstructed-and-spot-verified rather than fully independently sourced line by
  line.

NFP / PCE (engine 397, "CPI/NFP/PCE" cell): NOT INCLUDED. SCOPE DECISION (disclosed, not a
  silent drop): the spec names three release families pooled into one cell with an estimated
  count of "~48" events over the dev window. Literally pooling all three monthly series
  (CPI+NFP+PCE, ~12/yr each, ~53 months of dev) yields ~150-160 events, ~3x the spec's own
  estimate, and NFP/PCE lack a single clean, automatable-fetch schedule page the way CPI does
  (BLS Employment Situation shifts off the naive "first Friday" rule in specific months; BEA
  PCE/Personal-Income-and-Outlays has no fixed day-of-month rule at all) -- hand-verifying ~100
  additional dates across two more series was judged to exceed this run's reasonable evidence
  budget. The engine is therefore implemented and reported as CPI-ONLY, N ~= 48-52 (matches the
  spec's own estimate almost exactly), with NFP/PCE explicitly DEFERRED (not silently dropped)
  as a named scope limitation in REPORT.md and flagged for a follow-up wave if e397 is
  interesting enough to warrant Stage-2 characterization.

Index-option expiration (engine 398): 3rd Friday of every month (monthly equity-index option
  expiration; the quarterly triple/quad-witching dates in Mar/Jun/Sep/Dec are the SAME 3rd-
  Friday date, just additionally carrying quarterly futures/index expiration) -- this is a
  deterministic calendar rule (not a published one-off schedule), computed programmatically in
  smv2x.py via pandas' WOM-3FRI offset and cross-checked bar-by-bar against the actual NQ 3m
  session calendar (any 3rd Friday that is NOT a trading session, e.g. a market holiday, is
  flagged rather than silently used -- see out/calendar_sources.md for the flag list, expected
  to be empty or near-empty for 2022-2026).
"""

# FOMC statement/release dates (2:00pm ET), 2022-01-01 .. 2026-07-29 (full published range at
# fetch time; the executor filters to dev <= 2026-05-31 itself).
FOMC_DATES = [
    # 2022
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15",
    "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
    # 2023
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14",
    "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
    # 2024
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12",
    "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
    # 2025
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
    "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    # 2026 (as published by the Fed at fetch time; only Jan/Mar/Apr fall inside dev)
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29",
]

# CPI release dates (8:30am ET). CPI-ONLY implementation of the spec's "CPI/NFP/PCE" cell --
# see the scope-decision caveat in this file's module docstring and in REPORT.md.
CPI_DATES = [
    # 2022
    "2022-01-12", "2022-02-10", "2022-03-10", "2022-04-12", "2022-05-11", "2022-06-10",
    "2022-07-13", "2022-08-10", "2022-09-13", "2022-10-13", "2022-11-10", "2022-12-13",
    # 2023
    "2023-01-12", "2023-02-14", "2023-03-14", "2023-04-12", "2023-05-10", "2023-06-13",
    "2023-07-12", "2023-08-10", "2023-09-13", "2023-10-12", "2023-11-14", "2023-12-12",
    # 2024
    "2024-01-11", "2024-02-13", "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12",
    "2024-07-11", "2024-08-14", "2024-09-11", "2024-10-10", "2024-11-13", "2024-12-11",
    # 2025 (Nov-13 normal slot MISSING: Oct-2025-reference-month CPI was canceled outright by
    # the Oct-Nov 2025 government-shutdown data backlog; Sep-2025-ref CPI delayed to 10-24;
    # Nov-2025-ref CPI rescheduled to 12-18)
    "2025-01-15", "2025-02-12", "2025-03-12", "2025-04-10", "2025-05-13", "2025-06-11",
    "2025-07-15", "2025-08-12", "2025-09-11", "2025-10-24", "2025-12-18",
    # 2026 (through dev end 2026-05-31; 2026-02-13 itself was a reschedule of the normal early-
    # Feb slot, a lingering effect of the 2025 shutdown backlog)
    "2026-01-13", "2026-02-13", "2026-03-11", "2026-04-10", "2026-05-12",
]
