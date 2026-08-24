# OTRIMG-0053

## A FILE IDENTITY
- id: OTRIMG-0053
- filename: 20260824_171809753_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Jul 25, 2:02 PM (macOS menu bar)
- taskbar_date: 7/25/2025 2:02 PM (Windows taskbar; time partly under watermark, "2:0? PM" + "7/25/2025", MEDIUM confidence on minutes)
- social_post_date: none visible
- report_start_date: 7/20/2025
- report_end_date: 7/25/2025
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "hp" window, NT8 Strategy Analyzer, Display = "Summary ($)". Taller window than prior images; Settings pane cropped at right edge; visible "Run" button.

## D STRATEGY IDENTITY
- No strategy name visible. Italic annotation text near bottom right: "new session (from Strategy B)" (attribution UNKNOWN — appears to be an overlay/annotation, not NT UI). This labels the run as coming from a "Strategy B".

## E DATA SERIES
- Not directly visible (settings labels cropped). Numeric "1" box in Data-series position; avg bars = avg minutes ⇒ 1-minute bars (INFERRED).

## F PARAMETERS (Settings pane, right edge, top-to-bottom)
1. numeric: "1" (top of pane; likely last strategy parameter, cf. "Q...=1" in OTRIMG-0051)
2. SEP (group separator)
3. box: appears empty (Instrument position; value not visible)
4. dropdown: "v" glyph, value unreadable
5. dropdown: "v" glyph (small mark left of glyph), value unreadable
6. numeric: "1"
7. SEP
8. date/spin control: spinner glyph ("I v"), value unreadable
9. date/spin control: spinner glyph, value unreadable
10. dropdown: "v", value unreadable
11. checkbox: CHECKED
12. SEP
13. checkbox: UNCHECKED
14. dropdown: greyed/disabled "v", value unreadable
15. dropdown: "v", value unreadable
16. numeric: "20"
17. SEP
18. dropdown: "v", value unreadable
19. checkbox: UNCHECKED
20. numeric: "0"
21. SEP
22. numeric: "1"
23. dropdown: "v", value unreadable
24. checkbox: CHECKED
25. SEP
26. dropdown: "v", value unreadable
27. dropdown: "v", value unreadable
28. italic label: "template"
29. button: "Run" (dark, clearly legible here)
(Structure identical to NT8 backtest-properties stack mapped in OTRIMG-0051: Data series / Time frame / Setup / Historical fill processing / Order handling / Order properties — INFERRED.)

## G ENGINE SETTINGS
- Commission $0.00 (all columns); include-commission checkbox UNCHECKED (position 13); Slippage numeric 0 (position 20); Exit-on-session-close-position checkbox CHECKED; Bars required to trade 20.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($3,615.00) | ($3,050.00) | ($565.00) |
| Gross profit | $6,605.00 | $3,020.00 | $3,585.00 |
| Gross loss | ($10,220.00) | ($6,070.00) | ($4,150.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.65 | 0.50 | 0.86 |
| Max. drawdown | ($6,435.00) | ($5,510.00) | ($2,795.00) |
| Sharpe ratio | -1.51 | -1.51 | -1.83 |
| Sortino ratio | -5.00 | -5.02 | -6.08 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.56 | 0.88 | 0.03 |
| Probability | 81.83% | 89.29% | 57.85% |
| Start date | 7/20/2025 | | |
| End date | 7/25/2025 | | |
| Total # of trades | 24 | 15 | 9 |
| Percent profitable | 29.17% | 26.67% | 33.33% |
| # of winning trades | 7 | 4 | 3 |
| # of losing trades | 17 | 11 | 6 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($150.63) | ($203.33) | ($62.78) |
| Avg. winning trade | $943.57 | $755.00 | $1,195.00 |
| Avg. losing trade | ($601.18) | ($551.82) | ($691.67) |
| Ratio avg. win / avg. loss | 1.57 | 1.37 | 1.73 |
| Max. consec. winners | 2 | 1 | 2 |
| Max. consec. losers | 7 | 4 | 4 |
| Largest winning trade | $2,360.00 | $1,800.00 | $2,360.00 |
| Largest losing trade | ($1,245.00) | ($985.00) | ($1,245.00) |
| Avg. # of trades per day | 5.79 | 3.62 | 2.61 |
| Avg. time in market | 153.38 min | 214.87 min | 50.89 min |
| Avg. bars in trade | 153.38 | 214.87 | 50.89 |
| Profit per month | ($18,376.25) | ($15,504.17) | ($3,446.50) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark bottom right: "rednote ID: 1384856832" — FULLY LEGIBLE in this image (HIGH confidence). Italic annotation "new session (from Strategy B)" beneath/right of watermark, attribution UNKNOWN.

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Third consecutive Friday capture (7/11, 7/18, 7/25 of 2025), same "hp" machine; report = that week (7/20–7/25/2025); losing week net ($3,615.00), PF 0.65.
- Complete rednote (Xiaohongshu) ID recovered: 1384856832.
- BOTTOM EDGE: a code editor window behind the Analyzer shows one partial NinjaScript line in colored monospace: "if (Bars.IsFirstBarOfSession)" (closing characters cut; MEDIUM confidence). The strategy source code was open on the same machine.
- Bottom-left: macOS browser window edge with circular profile badge "JG" and a "+" (new tab) button — browser profile initials "JG".
- macOS menu bar this day shows extra items: game-controller icon, mic icon, translation icon, shopping-cart icon with "12", badge "29" on mail-like icon.
- Annotation "new session (from Strategy B)" suggests the collection curator (or poster) distinguishes multiple strategies (A/B...); this run is attributed to "Strategy B".
IMPLICATIONS:
- The trader/author edits NinjaScript (Bars.IsFirstBarOfSession is session-boundary logic — consistent with a session-anchored strategy).
- Weekly walk-forward style evaluation continues; results alternate win/lose weeks.
OPEN QUESTIONS:
- Is the annotation by the original poster or by the evidence collector? What is "Strategy B" vs "Strategy A"?
