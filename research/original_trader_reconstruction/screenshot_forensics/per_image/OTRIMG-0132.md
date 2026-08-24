# OTRIMG-0132

## A FILE IDENTITY
- id: OTRIMG-0132
- filename: 20260824_172701576_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Thu Apr 2, 3:11 PM (macOS menu bar; year not shown)
- taskbar_date: 3:11 PM / 4/2/2026 (Windows taskbar inside remote session)
- social_post_date: none visible
- report_start_date: 3/29/2026
- report_end_date: 4/2/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "APR 2". Captured THURSDAY afternoon — a partial week (Sun 3/29 → Thu 4/2), not the usual Friday/Saturday full-week report.

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "dev", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)".

## D STRATEGY IDENTITY
- No strategy/template/account name visible. "template" + "Run" at pane bottom.

## E DATA SERIES
- Not visible. Report window 3/29/2026 → 4/2/2026.

## F PARAMETERS (Settings pane scrolled NEAR THE TOP — reveals the upper parameter stack for the first time)
1. numeric: 30? — TOP-CROPPED (bottom half of digits visible, reads like 30; confidence LOW; rows may exist above)
2. numeric: 16 — fully visible
3. numeric: 0 — fully visible
4. numeric: 10 — fully visible
5. numeric: 15 — fully visible
6. dropdown: value unreadable
7. numeric: 60 — fully visible
8. numeric: 5 — fully visible
9. numeric: 20 — fully visible
10. dropdown: value unreadable
11. numeric: 95 — fully visible
12. numeric: 75 — fully visible
13. numeric: 50 — fully visible
14. numeric: 25 — fully visible
15. numeric: 5 — fully visible
16. numeric: 3 — fully visible
17. numeric: 10 — fully visible
18. numeric: 5 — fully visible
19. SEP
20. numeric/text box: EMPTY/blank
21. dropdown: unreadable
22. dropdown: tiny mark + "v", unreadable
23. numeric: 1 — fully visible
24. SEP
25. dropdown with grid/calendar glyph: unreadable
26. dropdown with grid/calendar glyph: unreadable
27. dropdown: unreadable
28. bool checkbox: CHECKED (bottom-cropped)
29. italic label "template"; Button "Run"

CUMULATIVE STACK (combining OTRIMG-0121/0123/0125/0127/0129/0132): strategy parameter group =
[30?], 16, 0, 10, 15, [dd], 60, 5, 20, [dd], 95, 75, 50, 25, 5, 3, 10, 5
then groups: D.(blank,[dd],[dd],1) | T.([dd-date],[dd-date],[dd],checked) | S.(unchecked,[dd-disabled],[dd],20) | H.([dd],unchecked,0) | O.(2,[dd],checked) | O.([dd],[dd],...)

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0.

## H PERFORMANCE (Summary ($), verbatim) — STRONG WINNING PARTIAL WEEK
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $26,385.00 | $17,675.00 | $8,710.00 |
| Gross profit | $54,535.00 | $32,640.00 | $21,895.00 |
| Gross loss | ($28,150.00) | ($14,965.00) | ($13,185.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.94 | 2.18 | 1.66 |
| Max. drawdown | ($4,800.00) | ($3,545.00) | ($5,080.00) |
| Sharpe ratio | 5.96 | 5.78 | 4.25 |
| Sortino ratio | 1.00 | 1.00 | 20.52 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.89 | 0.88 | 0.21 |
| Probability | 3.02% | 6.02% | 13.39% |
| Start date | 3/29/2026 | | |
| End date | 4/2/2026 | | |
| Total # of trades | 58 | 30 | 28 |
| Percent profitable | 44.83% | 46.67% | 42.86% |
| # of winning trades | 26 | 14 | 12 |
| # of losing trades | 31 | 16 | 15 |
| # of even trades | 1 | 0 | 1 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $454.91 | $589.17 | $311.07 |
| Avg. winning trade | $2,097.50 | $2,331.43 | $1,824.58 |
| Avg. losing trade | ($908.06) | ($935.31) | ($879.00) |
| Ratio avg. win / avg. loss | 2.31 | 2.49 | 2.08 |
| Max. consec. winners | 4 | 5 | 5 |
| Max. consec. losers | 5 | 4 | 3 |
| Largest winning trade | $8,370.00 | $8,370.00 | $5,940.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($1,990.00) |
| Avg. # of trades per day | 16.80 | 8.69 | 8.11 |
| Avg. time in market | 43.31 min | 35.33 min | 51.86 min |
| Avg. bars in trade | 43.28 | 35.30 | 51.82 |
| Profit per month | $160,948.50 | $107,817.50 | $53,131.00 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" + 小红书 logo.

## K FORENSIC INTERPRETATION
Direct facts:
- Sixth weekly window (3/29–4/2/2026), machine "dev", Sogou Pinyin input; captured Thursday 3:11 PM — report window ends the same day (partial week; Friday 4/3/2026 was Good Friday, market closed, which explains the Thursday cut).
- Settings pane scrolled to (near) the top: parameter stack now readable as [30?],16,0,10,15,[dd],60,5,20,[dd],95,75,50,25,5,3,10,5 — 16 visible numerics + 2 dropdowns before the first group separator.
- Best week in the series: +$26,385, PF 1.94, both directions profitable, DD only −$4,800; the week right after the −$42,235 disaster (OTRIMG-0129).
- Largest losing trade again exactly ($2,600.00) all/long — recurring hard stop signature.
- The parameter values are IDENTICAL where they overlap with every earlier capture → the poster did NOT re-tune after the losing week; same settings, wildly different weekly outcomes.
Implications (hypotheses):
- 95/75/50/25 look like level/percentile thresholds; 60 and 15/16 could be period lengths in minutes; the trailing 5,3,10,5 unknown.
- 0 among the top numerics (row 3) — a disabled feature or offset parameter.
Open questions:
- What sits above the "30?" box (scroll arrow still present).
- Dropdown values remain unreadable at this resolution in every capture.
