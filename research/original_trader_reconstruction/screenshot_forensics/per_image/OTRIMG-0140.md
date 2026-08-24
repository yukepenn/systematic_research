# OTRIMG-0140

## A FILE IDENTITY
- id: OTRIMG-0140
- filename: 20260824_172727394_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Sat May 2, 5:26 PM (macOS menu bar; year not shown)
- taskbar_date: 5:26 PM / 5/2/2026 (Windows taskbar inside remote session)
- social_post_date: none visible
- report_start_date: 4/26/2026
- report_end_date: 5/1/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "MAY 2".

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "dev", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)".

## D STRATEGY IDENTITY
- No strategy name visible. Settings pane shows the ORIGINAL flat parameter stack again (the OTRIMG-0121→0136 structure), i.e. NOT the checkbox-gated structure of OTRIMG-0138.

## E DATA SERIES
- Not visible. Report window 4/26/2026 → 5/1/2026 (captured Sat 5/2/2026 evening).

## F PARAMETERS (Settings pane, top-to-bottom)
1. numeric: 5? — TOP-CROPPED (bottom half visible, reads like 5; consistent with the known stack where 5 precedes 20; confidence LOW-MEDIUM)
2. numeric: 20 — fully visible
3. dropdown: value unreadable
4. numeric: 95 — fully visible
5. numeric: 75 — fully visible
6. numeric: 50 — fully visible
7. numeric: 25 — fully visible
8. numeric: 5 — fully visible
9. numeric: 3 — fully visible
10. numeric: 10 — fully visible
11. numeric: 5 — fully visible
12. SEP
13. numeric/text box: EMPTY/blank
14. dropdown: unreadable
15. dropdown: tiny mark + "v", unreadable
16. numeric: 1 — fully visible
17. SEP
18. dropdown with grid/calendar glyph: unreadable
19. dropdown with grid/calendar glyph: unreadable
20. dropdown: unreadable
21. bool checkbox: CHECKED
22. SEP
23. bool checkbox: UNCHECKED
24. dropdown: DISABLED (grayed)
25. dropdown: unreadable
26. numeric: 20 — fully visible
27. SEP
28. [partial box cut by pane bottom]
29. italic label "template"; Button "Run"

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0.

## H PERFORMANCE (Summary ($), verbatim)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($1,135.00) | $7,715.00 | ($8,850.00) |
| Gross profit | $32,755.00 | $22,005.00 | $10,750.00 |
| Gross loss | ($33,890.00) | ($14,290.00) | ($19,600.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.97 | 1.54 | 0.55 |
| Max. drawdown | ($19,425.00) | ($6,035.00) | ($14,540.00) |
| Sharpe ratio | 4.23 | 4.61 | -4.29 |
| Sortino ratio | 1.00 | 1.00 | -8.16 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.03 | 0.38 | 0.50 |
| Probability | 54.17% | 22.10% | 88.03% |
| Start date | 4/26/2026 | | |
| End date | 5/1/2026 | | |
| Total # of trades | 44 | 23 | 21 |
| Percent profitable | 40.91% | 47.83% | 33.33% |
| # of winning trades | 18 | 11 | 7 |
| # of losing trades | 26 | 12 | 14 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($25.80) | $335.43 | ($421.43) |
| Avg. winning trade | $1,819.72 | $2,000.45 | $1,535.71 |
| Avg. losing trade | ($1,303.46) | ($1,190.83) | ($1,400.00) |
| Ratio avg. win / avg. loss | 1.40 | 1.68 | 1.10 |
| Max. consec. winners | 3 | 2 | 2 |
| Max. consec. losers | 7 | 3 | 10 |
| Largest winning trade | $9,050.00 | $9,050.00 | $2,845.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,600.00) |
| Avg. # of trades per day | 10.62 | 5.55 | 5.07 |
| Avg. time in market | 80.75 min | 90.87 min | 69.67 min |
| Avg. bars in trade | 80.73 | 90.83 | 69.67 |
| Profit per month | ($5,769.58) | $39,217.92 | ($44,987.50) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" + 小红书 logo.

## K FORENSIC INTERPRETATION
Direct facts:
- Week 4/26–5/1/2026 on "dev", captured Saturday evening; roughly breakeven (−$1,135), long side +$7,715, short side −$8,850.
- The Settings pane shows the ORIGINAL flat stack (…5?, 20, [dd], 95, 75, 50, 25, 5, 3, 10, 5 | …1 | … | …20) — i.e., 3 days after OTRIMG-0138 displayed a structurally different checkbox-gated panel, the original strategy panel is back. Either two strategies coexist (0138 was a different strategy's backtest) or the revision was reverted.
- The top-cropped box above "20" reads like "5", consistent with the fuller stack …60, 5, 20 seen in 0123/0132/0136.
- Largest losing trade ($2,600.00) in ALL columns — 9 out of 9 captures now share this fixed-stop signature across both panel structures.
- Trade cadence 10.62/day with 80.75 min avg hold — closer to the post-retune (0136) profile than the early-March churn.
Implications (hypotheses):
- The trader appears to run/compare at least two strategy variants on the same week-by-week Xiaohongshu reporting cadence; the $2,600 stop is common to both.
Open questions:
- Whether 0138's panel belongs to a second strategy that continues in parallel; strategy names remain unseen throughout the series.
