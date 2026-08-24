# OTRIMG-0062

## A FILE IDENTITY
- id: OTRIMG-0062
- filename: 20260824_171846246_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Aug 22, 10:04 PM (macOS menu bar) — a LATE-NIGHT capture, unlike prior afternoon captures
- taskbar_date: 8/22/2025 10:04 PM (Windows taskbar)
- social_post_date: none visible
- report_start_date: 8/17/2025
- report_end_date: 8/22/2025
- contract_date_clue: macOS dock Calendar icon shows "AUG 22"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "hp", NT8 Strategy Analyzer, Display = "Summary ($)". Settings pane scrolled to expose the LONGEST strategy-parameter stack of the series.

## D STRATEGY IDENTITY
- No strategy name visible. "Analyzer" tab; "template" + "Run". "Percent profitable" row is highlighted/selected (grey band).

## E DATA SERIES
- Not directly readable; Value "1"; avg bars = avg minutes ⇒ 1-minute bars (INFERRED).

## F PARAMETERS (Settings pane, right edge, top-to-bottom — most complete parameter fingerprint in the batch)
1. numeric: "18?" — RAW "18"+partial round glyph, cropped (INFERRED possibly 180). LOW confidence 3rd digit.
2. numeric: "14?" — RAW "14"+partial round glyph, cropped (INFERRED possibly 140). LOW confidence 3rd digit.
3. SEP
4. numeric: "90"
5. numeric: "17?" — RAW "17"+third glyph ambiguous (5/9 confusable, partially cropped). Candidates 175/179. LOW confidence.
6. numeric: "5"
7. numeric: "10"
8. numeric: "10"
9. SEP
10. checkbox: CHECKED
11. numeric: "45?" (INFERRED possibly 450; LOW)
12. numeric: "20?" (INFERRED possibly 200; LOW)
13. SEP
14. numeric: "65"
15. numeric: "30"
16. numeric: "65"
17. SEP
18. numeric: "1"
19. SEP
20. box: appears empty (Instrument position)
21. dropdown: "v", value unreadable
22. dropdown: "v", value unreadable
23. numeric: "1"
24. SEP
25. date/spin control: spinner glyph, value unreadable
26. date/spin control: spinner glyph, value unreadable
27. dropdown: "v", value unreadable
28. italic label: "template"
29. button: "Run"

## G ENGINE SETTINGS
- Commission $0.00 all columns; slippage 0.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($5,315.00) | ($8,080.00) | $2,765.00 |
| Gross profit | $15,700.00 | $3,225.00 | $12,475.00 |
| Gross loss | ($21,015.00) | ($11,305.00) | ($9,710.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.75 | 0.29 | 1.28 |
| Max. drawdown | ($7,900.00) | ($8,470.00) | ($3,245.00) |
| Sharpe ratio | -1.79 | -1.76 | 1.87 |
| Sortino ratio | -5.93 | -5.84 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.00 | 0.82 | 0.44 |
| Probability | 75.58% | 99.35% | 33.68% |
| Start date | 8/17/2025 | | |
| End date | 8/22/2025 | | |
| Total # of trades | 48 | 23 | 25 |
| Percent profitable | 29.17% | 26.09% | 32.00% |
| # of winning trades | 14 | 6 | 8 |
| # of losing trades | 34 | 17 | 17 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($110.73) | ($351.30) | $110.60 |
| Avg. winning trade | $1,121.43 | $537.50 | $1,559.38 |
| Avg. losing trade | ($618.09) | ($665.00) | ($571.18) |
| Ratio avg. win / avg. loss | 1.81 | 0.81 | 2.73 |
| Max. consec. winners | 3 | 2 | 2 |
| Max. consec. losers | 12 | 11 | 4 |
| Largest winning trade | $4,900.00 | $1,385.00 | $4,900.00 |
| Largest losing trade | ($1,490.00) | ($1,300.00) | ($1,490.00) |
| Avg. # of trades per day | 13.90 | 6.66 | 7.24 |
| Avg. time in market | 67.29 min | 56.52 min | 77.20 min |
| Avg. bars in trade | 67.29 | 56.52 | 77.20 |
| Profit per month | ($32,421.50) | ($49,288.00) | $16,866.50 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark: "rednote ID: 1384856832" across taskbar/dock (legible; last digits overlap dock icons).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Seventh Friday capture (8/22/2025, 10:04 PM); report 8/17–8/22/2025; losing week net ($5,315.00); long side crushed (PF 0.29), short side positive.
- FULLEST parameter fingerprint of the batch: 18?/14? | 90/17?/5/10/10 | [checked]/45?/20? | 65/30/65 | 1.
- HYPOTHESIS (clearly labeled): the sub-sequence 90 / 17? / 5 / 10 / [checked] / 10 closely resembles the Solar Wave replication baseline parameter set "90/179/5/10/true/10" known to this research program. If the ambiguous third digit is 9 (179), this strongly suggests the strategy is a SolarWave-family system. The third digit is NOT cleanly legible (5/9 confusable) — treat as candidate only.
- 48 trades this week (13.90/day) — highest frequency of the series; avg holding 67 min.
- macOS dock further expanded (TradingView-like "TV" icon appears; Settings badge now "2"); menu bar has WeChat-like icon, boxed-"A" icon, PDF tools. Late-night session.
IMPLICATIONS:
- Settings pane scroll position reveals the parameter list has at least 2 more numerics (18?/14?) ABOVE the 90/17? group, i.e., ≥10 strategy parameters + groups.
OPEN QUESTIONS:
- Exact values of 18?/14?/45?/20?/17?; strategy name; whether trade-frequency jump reflects changed params or market volatility.
