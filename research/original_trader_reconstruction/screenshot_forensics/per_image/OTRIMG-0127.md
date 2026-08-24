# OTRIMG-0127

## A FILE IDENTITY
- id: OTRIMG-0127
- filename: 20260824_172642960_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Sat Mar 21, 7:59 PM (macOS menu bar; year not shown)
- taskbar_date: 7:59 PM / 3/21/2026 (Windows taskbar inside remote session)
- social_post_date: none visible
- report_start_date: 3/15/2026
- report_end_date: 3/20/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "MAR 21"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window titled "hp" (back to the hp machine), NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)".

## D STRATEGY IDENTITY
- No strategy/template/account name visible. "template" label + "Run" button at pane bottom.

## E DATA SERIES
- Not visible. Report window 3/15/2026 → 3/20/2026 (captured Sat 3/21/2026, day after week end).

## F PARAMETERS (Settings pane, scrolled to bottom section; labels cropped, no group initials visible at this pane width)
1. numeric: 5 — fully visible (tail of parameters group)
2. SEP (collapse triangle + "...")
3. numeric/text box: EMPTY/blank (unreadable)
4. dropdown: value unreadable
5. dropdown: tiny mark then "v", unreadable
6. numeric: 1 — fully visible
7. SEP
8. dropdown with small grid/calendar glyph: unreadable (date picker?)
9. dropdown with small grid/calendar glyph: unreadable (date picker?)
10. dropdown: unreadable
11. bool checkbox: CHECKED
12. SEP
13. bool checkbox: UNCHECKED
14. dropdown: DISABLED (grayed)
15. dropdown: unreadable
16. numeric: 20 — fully visible
17. SEP
18. dropdown: unreadable
19. bool checkbox: UNCHECKED
20. numeric: 0 — fully visible
21. SEP
22. numeric: 2 — fully visible
23. dropdown: unreadable
24. bool checkbox: CHECKED
25. SEP
26. dropdown: unreadable
27. dropdown: unreadable
28. italic label "template"; Button "Run"

Note: item 27 (second dropdown in final group) is newly visible vs OTRIMG-0125, where the pane cut off after one dropdown — the final group has at least two dropdowns.

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0. Possible Slippage spinbox = 0 (item 20). Nothing else readable.

## H PERFORMANCE (Summary ($), verbatim)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $9,285.00 | $11,220.00 | ($1,935.00) |
| Gross profit | $48,900.00 | $32,980.00 | $15,920.00 |
| Gross loss | ($39,615.00) | ($21,760.00) | ($17,855.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.23 | 1.52 | 0.89 |
| Max. drawdown | ($12,765.00) | ($13,125.00) | ($7,445.00) |
| Sharpe ratio | 1.57 | 1.56 | 1.54 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.00 | 0.03 | 0.35 |
| Probability | 25.01% | 15.38% | 59.93% |
| Start date | 3/15/2026 | | |
| End date | 3/20/2026 | | |
| Total # of trades | 67 | 34 | 33 |
| Percent profitable | 40.30% | 35.29% | 45.45% |
| # of winning trades | 27 | 12 | 15 |
| # of losing trades | 40 | 22 | 18 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $138.58 | $330.00 | ($58.64) |
| Avg. winning trade | $1,811.11 | $2,748.33 | $1,061.33 |
| Avg. losing trade | ($990.38) | ($989.09) | ($991.94) |
| Ratio avg. win / avg. loss | 1.83 | 2.78 | 1.07 |
| Max. consec. winners | 3 | 2 | 2 |
| Max. consec. losers | 8 | 5 | 5 |
| Largest winning trade | $8,920.00 | $8,920.00 | $3,720.00 |
| Largest losing trade | ($2,600.00) | ($2,130.00) | ($2,600.00) |
| Avg. # of trades per day | 16.17 | 8.21 | 7.97 |
| Avg. time in market | 53.67 min | 57.41 min | 49.82 min |
| Avg. bars in trade | 53.64 | 57.38 | 49.79 |
| Profit per month | $47,198.75 | $57,035.00 | ($9,836.25) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" + 小红书 logo.

## K FORENSIC INTERPRETATION
Direct facts:
- Fourth consecutive weekly run (2/22, 3/1, 3/8, 3/15 weeks), back on machine "hp"; capture Saturday evening after the Friday close.
- BACKGROUND WINDOW LEAK: a macOS window behind Jump Desktop shows one line of a recruiter-style job listing: "...a week onsite PAY RATE: $75/hr on W2 (LOCATIO..." with "BANNER HEALTH" to the right, and a snippet starting "Syn..." at far left. Banner Health is a US (Arizona-based) healthcare system; "W2 rate" phrasing is US IT-contracting recruiter language — the poster appears to be a US-based IT contractor/consultant receiving healthcare-sector job mails.
- Long DD ($13,125) exceeds All-trades DD ($12,765) — normal NT8 artifact of per-side DD computation.
- Largest losses again pinned near ($2,600): all/short = ($2,600.00), long = ($2,130.00) — recurring fixed-dollar stop signature.
- Sharpe ≈1.54-1.57 in all three columns while short side is net negative — NT8 weekly Sharpe is not informative here; transcribed verbatim.
- Menu bar shows an item with "8" (unidentified glyph + 8), U.S. keyboard active.
Implications (hypotheses):
- The final settings group has ≥2 dropdowns (consistent with NT8 "Order properties": Set order quantity / Time in force).
- Week was long-favorable; strategy again symmetric-entry with direction PnL following the week's trend.
Open questions:
- The "Syn..." window (Synergy? Synapse?) — email client or job board unidentifiable from one line.
