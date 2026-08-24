# OTRIMG-0123

## A FILE IDENTITY
- id: OTRIMG-0123
- filename: 20260824_172608921_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Mar 6, 7:47 PM (macOS menu bar; year not shown)
- taskbar_date: 7:47 PM / 3/6/2026 (Windows taskbar clock inside remote session)
- social_post_date: none visible
- report_start_date: 3/1/2026
- report_end_date: 3/6/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "MAR 6"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — same setup as OTRIMG-0121: Jump Desktop window "hp", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", All/Long/Short table, pinned Settings pane at right edge.

## D STRATEGY IDENTITY
- No strategy/template/account name visible. Italic "template" label + "Run" button at bottom of Settings pane.

## E DATA SERIES
- Instrument/contract/bar type/hours: not visible.
- Report window: 3/1/2026 → 3/6/2026 (the following trading week after OTRIMG-0121's window).

## F PARAMETERS (Settings pane, top-to-bottom; labels cut off by window edge)
1. numeric: 15 — fully visible (scroll-up arrow above; rows above may exist)
2. dropdown: value unreadable
3. numeric: 60 — fully visible
4. numeric: 5 — fully visible
5. numeric: 20 — fully visible
6. dropdown: value unreadable
7. numeric: 95 — fully visible
8. numeric: 75 — fully visible
9. numeric: 50 — fully visible
10. numeric: 25 — fully visible
11. numeric: 5 — fully visible
12. numeric: 3 — fully visible
13. numeric: 10 — fully visible
14. numeric: 5 — fully visible
15. SEP (collapse triangle + "...")
16. numeric/text box: EMPTY (blank)
17. dropdown: value unreadable
18. dropdown: tiny dark mark then "v", unreadable
19. numeric: 1 — fully visible
20. SEP (collapse triangle + "...")
21. dropdown with colored glyph (brush/color style): unreadable
22. dropdown with colored glyph (brush/color style): unreadable
23. dropdown: unreadable
24. bool checkbox: CHECKED
25. SEP (collapse triangle + "...")
26. bool checkbox: UNCHECKED
27. dropdown: DISABLED (grayed)
28. (further rows scrolled out of view below; scrollbar thumb visible)
29. italic label text: "template" (fixed at pane bottom, right-cropped)
30. Button: "Run"

Note: this scroll position reveals 4 rows ABOVE what OTRIMG-0121 showed: 15, [dropdown], 60, 5 precede the 20/[dropdown]/95/75/50/25/5/3/10/5 stack.

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0. Nothing else visible.

## H PERFORMANCE (Summary ($), verbatim)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $4,090.00 | ($5,170.00) | $9,260.00 |
| Gross profit | $48,780.00 | $23,360.00 | $25,420.00 |
| Gross loss | ($44,690.00) | ($28,530.00) | ($16,160.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.09 | 0.82 | 1.57 |
| Max. drawdown | ($12,100.00) | ($13,950.00) | ($3,815.00) |
| Sharpe ratio | -1.53 | -1.50 | 1.56 |
| Sortino ratio | -5.07 | -4.97 | 1.00 |
| Ulcer index | 0.01 | 0.02 | 0.01 |
| R squared | 0.33 | 0.49 | 0.26 |
| Probability | 36.92% | 71.77% | 11.49% |
| Start date | 3/1/2026 | | |
| End date | 3/6/2026 | | |
| Total # of trades | 94 | 51 | 43 |
| Percent profitable | 36.17% | 29.41% | 44.19% |
| # of winning trades | 34 | 15 | 19 |
| # of losing trades | 60 | 36 | 24 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $43.51 | ($101.37) | $215.35 |
| Avg. winning trade | $1,434.71 | $1,557.33 | $1,337.89 |
| Avg. losing trade | ($744.83) | ($792.50) | ($673.33) |
| Ratio avg. win / avg. loss | 1.93 | 1.97 | 1.99 |
| Max. consec. winners | 3 | 2 | 4 |
| Max. consec. losers | 7 | 10 | 5 |
| Largest winning trade | $4,360.00 | $4,360.00 | $3,630.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($1,300.00) |
| Avg. # of trades per day | 22.69 | 12.31 | 10.38 |
| Avg. time in market | 35.14 min | 33.29 min | 37.32 min |
| Avg. bars in trade | 35.13 | 33.29 | 37.30 |
| Profit per month | $20,790.83 | ($26,280.83) | $47,071.67 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" + 小红书 logo.

## K FORENSIC INTERPRETATION
Direct facts:
- Same machine ("hp"), same Settings stack, one week later than OTRIMG-0121 (3/1–3/6/2026, captured Fri 3/6/2026 7:47 PM — again a live end-of-week run).
- The scroll position exposes 4 parameters above the OTRIMG-0121 view: 15, [dropdown], 60, 5, then 20, [dropdown], 95, 75, 50, 25, 5, 3, 10, 5.
- Avg. time in market 35.14 min (vs 65.21 min in 0121's week) and trades/day 22.69 (vs 12.79) — trade cadence roughly doubled week-over-week.
- Sharpe -1.53 displayed with positive net $4,090 (weekly-scale artifacts of NT's Sharpe calc).
- Long side again net negative, short side again carries the entire profit; largest-losing-trade values (-$2,600 long / -$1,300 short) IDENTICAL to previous week — consistent with a fixed stop of the same dollar size, possibly 2 contracts long-stop vs 1 short-stop or an asymmetric stop parameter.
Implications (hypotheses):
- $2,600 / $1,300 = exactly 2:1; if NQ ($20/pt), $1,300 = 65 pts — could be a fixed 65-point stop with 2x size on longs, or a doubled stop on longs.
- Cadence doubling with identical settings values suggests the strategy is volatility/condition-driven rather than re-parameterized weekly (settings shown match 0121 where overlapping).
Open questions:
- Rows above "15" may exist (scroll arrow present).
- Still no strategy name or instrument visible.
