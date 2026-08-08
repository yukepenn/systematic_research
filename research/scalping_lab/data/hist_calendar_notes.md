# Historical macro release calendar 2005-2021 — sources and verification

Companion to `hist_calendar_2005_2021.csv` (schema matches
`research/04_complementary_family/c01_announcement_calendar.csv`: `date,event,time_et,source`).
Covers exactly two event types: `NFP` (Employment Situation) and `CPI` (Consumer Price Index),
release dates 2005-01-01 .. 2021-12-31, all at 08:30 ET.
Compiled 2026-08-07 by a data-compilation agent. Not derived from any first-Friday rule —
every date was extracted from a BLS source page.

## Primary sources (all years, both events)

Live bls.gov blocks non-browser clients (Akamai), so BLS pages were retrieved as
**archive.org (Wayback Machine) snapshots of bls.gov** — recorded here per the task rule:

| Source | Snapshot | Covers |
|---|---|---|
| BLS "Employment Situation Archived News Releases" (`bls.gov/bls/news-release/empsit.htm`) | `web.archive.org/web/20220531080706/https://www.bls.gov/bls/news-release/empsit.htm` | NFP, all 17 years (primary) |
| BLS "Consumer Price Index Archived News Releases" (`bls.gov/bls/news-release/cpi.htm`) | `web.archive.org/web/20220529091004/https://www.bls.gov/bls/news-release/cpi.htm` | CPI, all 17 years (primary) |
| BLS schedule-archive page (`bls.gov/schedule/archives/empsit_nr.htm`) | `web.archive.org/web/20160907125444/http://www.bls.gov:80/schedule/archives/empsit_nr.htm` | NFP 2005-2015 (independent-snapshot cross-check) |
| BLS schedule-archive page (`bls.gov/schedule/archives/cpi_nr.htm`) | `web.archive.org/web/20160925080048/http://www.bls.gov:80/schedule/archives/cpi_nr.htm` | CPI 2005-2015 (independent-snapshot cross-check) |

Extraction method: each listing entry links the archived release file whose filename embeds the
**actual release date** (`empsit_MMDDYYYY.*` / `cpi_MMDDYYYY.*`), with the reference month as link
text. All entries with release date inside the window were taken. These are *actual* release dates
(the archived-release record), not the ex-ante schedule — which is what a study gate needs, and is
why the Oct-2013 shutdown displacement appears correctly.

Note: BLS's `/schedule/archives/*_nr.htm` pages resolve to the same archived-news-release listing
(BLS reorganized its schedule archive into the release archive), so the 2016 snapshots serve as an
independently-captured copy of the same underlying record, six years apart.

## Verification results

**(a) Count check** — 12 NFP + 12 CPI per release-year for every year 2005-2021
(204 + 204 = 408 rows). Reference-month continuity: NFP covers ref months Dec-2004..Nov-2021 with
no gaps or duplicates; CPI likewise Dec-2004..Nov-2021. PASS.

**(b) Day-of-week check** —
NFP: 198 Friday, 5 Thursday, 1 Tuesday. Every non-Friday NFP with reason:

| Date | Day | Reason |
|---|---|---|
| 2008-07-03 | Thu | Independence Day holiday Fri 2008-07-04 |
| 2009-07-02 | Thu | Independence Day observed Fri 2009-07-03 (Jul 4 = Sat) |
| 2013-10-22 | Tue | Sep-2013 report delayed 18 days by federal government shutdown (orig. sched. 2013-10-04) |
| 2014-07-03 | Thu | Independence Day holiday Fri 2014-07-04 |
| 2015-07-02 | Thu | Independence Day observed Fri 2015-07-03 (Jul 4 = Sat) |
| 2020-07-02 | Thu | Independence Day observed Fri 2020-07-03 (Jul 4 = Sat) |

CPI: all 204 releases Tue-Fri (Wed 76, Fri 48, Thu 45, Tue 35); zero Monday/weekend releases;
no anomalies. The shutdown also displaced CPI: Sep-2013 CPI released 2013-10-30 (normally
mid-October) and Oct-2013 CPI on 2013-11-20. PASS.

**Cross-snapshot check** — every in-window entry in the 2016 snapshots matches the 2022 snapshots
exactly: 0 mismatches, 0 entries present in one and missing from the other. PASS.

**(c) 8-date spot-check against second sources** — all 8 sampled dates were verified against the
**actual archived BLS release documents** (embargo header states day-of-week, date, and the
08:30 a.m. ET release time), and 6 of 8 additionally against **independent non-BLS news archives**
(archive.org copies of same-day CNN Money / CNBC coverage; URL date-stamps and headlines):

| Date | Event | Release-document embargo line (via archive.org) | Independent news check |
|---|---|---|---|
| 2005-02-04 | NFP | "embargoed until 8:30 A.M. (EST), Friday, February 4, 2005" | CNN Money 2005/02/04 "Job growth again disappoints..." MATCH |
| 2008-07-03 | NFP | "embargoed until 8:30 A.M. (EDT), Thursday, July 3, 2008" | CNN Money 2008/07/03 "Job losses continue for sixth straight month" MATCH |
| 2013-10-22 | NFP | "8:30 a.m. (EDT) Tuesday, October 22, 2013" (USDL-13-2035) | CNN Money 2013/10/22 "September jobs report... delayed 18 days by the government shutdown" MATCH |
| 2020-07-02 | NFP | "8:30 a.m. (ET) Thursday, July 2, 2020" | CNBC 2020/07/02 "Record jobs gain of 4.8 million in June" MATCH |
| 2005-06-15 | CPI | "EMBARGOED UNTIL 8:30 A.M. (EDT) Wednesday, June 15, 2005" | (no fetchable independent article found; doc-level only) |
| 2013-10-30 | CPI | "8:30 a.m. (EDT) Wednesday, October 30, 2013" (USDL-13-2076) | (no fetchable independent article found; doc-level only) |
| 2016-08-16 | CPI | "8:30 a.m. (EDT) August 16, 2016" | CNBC 2016/08/16 "US Consumer Price Index unchanged in July" MATCH |
| 2021-12-10 | CPI | "8:30 a.m. (ET) December 10, 2021" | CNBC 2021/12/10 "Inflation surged 6.8% in November... said Friday" MATCH |

8/8 document-level PASS (each confirms date, weekday, and 08:30 ET); 6/8 independent-news PASS,
0 mismatches anywhere. (WebSearch quota was exhausted this session; independent checks used
direct archive.org fetches of date-stamped news URLs instead. ALFRED/FRED blocked automated
fetches with 403 and could not be used.)

**(d) 2013 shutdown canary** — the Sep-2013 Employment Situation appears as released
**2013-10-22 (Tuesday)**, exactly as required (delayed from 2013-10-04 by the Oct 2013 federal
government shutdown), sourced from the BLS archive filename `empsit_10222013.htm`, the release
document itself, and same-day CNN coverage. CANARY PASS.

**time_et = 08:30** — confirmed in all 8 sampled release documents spanning 2005-2021; both
releases were issued at 8:30 a.m. ET throughout the window (no release-time regime change).

## Gaps

None. All 17 years x 12 months x 2 events are present from source pages; no year required
`source=UNAVAILABLE`; no date was inferred or guessed.

## Confidence caveats

- All rows trace to BLS archive listings; the 396 rows outside the 8-entry document-level sample
  rest on the filename-embedded date convention. That convention was validated 8/8 against the
  documents' embargo headers (plus 6 independent news matches) with zero exceptions, and the two
  BLS snapshots taken six years apart agree on 100% of overlapping rows.
- No individual row is flagged low-confidence.
