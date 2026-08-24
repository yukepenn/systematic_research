# OTRIMG-0083

## A FILE IDENTITY
- id: OTRIMG-0083
- filename: 20260824_171948142_iOS.jpg
- resolution: 1440 x 936

## B DATE EVIDENCE
- screen_capture_date: Fri Nov 7 (macOS menu bar "Fri Nov 7 7:06 PM")
- screen_capture_time: 7:06 PM
- taskbar_date: 11/7/2025, 7:06 PM (remote Windows taskbar) — supplies year
- social_post_date: none visible
- report_start_date: 11/2/2025
- report_end_date: 11/7/2025
- contract_date_clue: none readable
- other date clue: macOS dock Calendar "NOV 7"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "hp", NT8 Strategy Analyzer, Display = "Summary ($)", Settings pane mid-scroll.

## D STRATEGY IDENTITY
- No strategy name visible. Orange "Strategy Analyzer" tab; "Analyzer" + "+"; italic "template" footer.
- Note: the "# of even trades" table row is highlighted/selected (grey band) — cursor was on it.

## E DATA SERIES
- "D." group: instrument box left sliver only (unreadable), 2 dropdowns unreadable, Value = "1". 1-minute bars confirmed by avg-bars == avg-minutes.
- "T.." (Time frame): Start/End calendar dropdowns (values not shown), lower rows cut.

## F PARAMETERS (Settings pane top-to-bottom; labels collapsed to "..")
1. Header "Settings" + pin + arrows
2. ".." numeric: "3"
3. ".." numeric: "6"
4. ".." numeric: "9"
5. SEP — group "M."
6. ".." checkbox: CHECKED
7. ".." numeric: "450" (box border visible; sibling OTRIMG-0077 read this parameter as 4500 with labels — likely display-clipped "4500"; RAW here = "450", INFERRED 4500) [LOW]
8. ".." numeric: "200" (same caveat; RAW "200", INFERRED 2000) [LOW]
9. SEP — group "S.."
10. ".." numeric: "65"
11. ".." numeric: "30"
12. ".." numeric: "65"
13. ".." numeric: "20"
14. ".." numeric: "46"  ← NEW parameter vs earlier frames
15. ".." numeric: "36"  ← NEW parameter vs earlier frames
16. SEP — group "T.."
17. ".." numeric: "1"
18. SEP — group "U."
19. ".." checkbox: CHECKED
20. ".." numeric: "80"
21. SEP — group "D." (Data series)
22. ".." instrument box: unreadable left sliver
23. ".." dropdown: ". v"
24. ".." dropdown: ". v"
25. ".." numeric: "1"
26. SEP — group "T.." (Time frame)
27. ".." calendar dropdown
28. ".." calendar dropdown
29. partially cut box (bottom of scroll view)
30. italic "template"
31. Button "Run"

## G ENGINE SETTINGS
- Commission $0.00 in report; slippage 0. Engine rows below Time frame not visible at this scroll.

## H PERFORMANCE (Summary ($); All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $18,545.00 | $3,315.00 | $15,230.00 |
| Gross profit | $43,965.00 | $17,780.00 | $26,185.00 |
| Gross loss | ($25,420.00) | ($14,465.00) | ($10,955.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.73 | 1.23 | 2.39 |
| Max. drawdown | ($9,850.00) | ($9,460.00) | ($2,900.00) |
| Sharpe ratio | 1.65 | 1.87 | 1.63 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.48 | 0.09 | 0.77 |
| Probability | 4.67% | 31.53% | 3.19% |
| Start date | 11/2/2025 | | |
| End date | 11/7/2025 | | |
| Total # of trades | 62 | 29 | 33 |
| Percent profitable | 41.94% | 31.03% | 51.52% |
| # of winning trades | 26 | 9 | 17 |
| # of losing trades | 36 | 20 | 16 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $299.11 | $114.31 | $461.52 |
| Avg. winning trade | $1,690.96 | $1,975.56 | $1,540.29 |
| Avg. losing trade | ($706.11) | ($723.25) | ($684.69) |
| Ratio avg. win / avg. loss | 2.39 | 2.73 | 2.25 |
| Max. consec. winners | 4 | 2 | 5 |
| Max. consec. losers | 7 | 11 | 4 |
| Largest winning trade | $5,310.00 | $2,815.00 | $5,310.00 |
| Largest losing trade | ($1,445.00) | ($1,445.00) | ($1,300.00) |
| Avg. # of trades per day | 14.97 | 8.40 | 7.97 |
| Avg. time in market | 65.48 min | 66.90 min | 64.24 min |
| Avg. bars in trade | 65.48 | 66.90 | 64.24 |
| Profit per month | $94,270.42 | $20,221.50 | $77,419.17 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark present (see K).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Fifth weekly Friday run: 11/2→11/7/2025. BEST week in the series: net +$18,545, PF 1.73, and this time SHORTS dominate (+$15,230, PF 2.39).
- PARAMETER EVOLUTION: top group now reads 3/6/9 (previously ../A5=10 style with 5/10/10 values), and the "S.." group now has SIX numerics 65/30/65/20/46/36 (previously four) — the strategy gained two parameters (46, 36) and top-group values changed between Oct 31 and Nov 7. This is at least the third distinct strategy version in the JD series (v1: Oct 3 [90/65, no U-group]; v2: Oct 10–31 [65/20 + U:80]; v3: Nov 7 [+46/36, top 3/6/9]).
- "M." group unchanged: ✓, 450(0?), 200(0?). "U." unchanged: ✓, 80. Quantity group "T..": 1.
- WeChat menu-bar badge now 6; battery indicator low/red-ish; same rednote watermark "rednote ID: 1384856832".
IMPLICATIONS (hypotheses):
- Ongoing active development: the trader iterates strategy code roughly weekly, appending parameters; consistent with an evolving personal system rather than a fixed vendor product.
- Probability field 4.67% (All) — NT8's probability-of-luck metric; very low = strong week unlikely by chance under its test.
OPEN QUESTIONS:
- Whether "450/200" here are literally 450/200 or display-clipped 4500/2000 (labels not visible this frame).
- What the two new parameters (46, 36) control.
