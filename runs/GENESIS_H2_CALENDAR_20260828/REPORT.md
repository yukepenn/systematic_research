# GENESIS_H2_CALENDAR — RESULT: **NULL (0 of 11 day-types survive the family-wise bar)**

Executes `spec.yaml` (committed `b1bf75c` before results). Trial `G00011`. Program-printed gate
table in `out/gate_table.txt`; 19 resolutions frozen pre-computation; family null distribution in
`out/family_null_distribution.csv` (500 shared-draw circular shifts).

## Verdict

> **No calendar/flow day-type carries detectable conditional NQ session-return information at the
> family-wise 5% level, 2006 → 2026-07** (5,305 sessions). Family-wise bar max-|t| q95 = **2.849**;
> largest real |t| = 2.296 (Friday, negative).

| day-type | diff %/session | t | note |
|---|---:|---:|---|
| FOMC_DAY (163) | **+0.137** | +1.73 | right sign, needed +0.225% — under bar |
| NFP_DAY (246) | −0.107 | −1.67 | **contra** expectation |
| CPI_DAY (244) | +0.062 | +1.03 | |
| TOM (986) | −0.008 | −0.28 | contra the McConnell-Xu prior |
| FOMC_CYCLE (2,796) | −0.004 | −0.17 | Cieslak effect absent here |
| OPEX_WEEK (1,230) | −0.022 | −0.81 | |
| DOW Fri (worst) | | −2.30 | under bar |

- ⭐ **The day-of-week "closure" is now a TESTED fact, not an inherited assumption** — G3 PASS:
  zero DOW survivors, exactly as preregistered (this resolves prior-research-atlas
  over-generalization #4 by direct measurement).
- Published-effect decay reads as expected: the two strongest externally-documented effects
  (announcement-day, FOMC-cycle) are respectively under-bar and sign-flat on NQ futures sessions.

## Closure scope

CLOSED: *these 11 day-type dummies → same-session close-to-close mean return, 2006–2026-07, at
family-wise 5% with the printed MDEs (0.07–0.23%/session).* NOT closed: day-type × state
interactions (barred this wave by spec), vol/variance day-type effects (only means were tested),
intraday geometry on event days.

## Process integrity

FOMC dates: 167 scheduled meetings parsed from 16 federalreserve.gov pages (1.61 MB, hashed;
37/37 exact against the repo's 2022+ calendar). BLS 2005–2021 calendar found at
`research/scalping_lab/data/hist_calendar_2005_2021.csv`. Seal: substrates 0 sealed rows; 3
post-seal FOMC meetings truncated with the count printed. No search, no git, no CrossTrade.
**`LIVE ENABLED = NO` · $0 · evidence: DISCOVERY_CONSUMED.**
