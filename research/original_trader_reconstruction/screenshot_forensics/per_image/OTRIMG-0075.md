# OTRIMG-0075

## A FILE IDENTITY
- id: OTRIMG-0075
- filename: 20260824_171926444_iOS.jpg
- resolution: 1440 x 936

## B DATE EVIDENCE
- screen_capture_date: Fri Oct 10 (macOS menu bar, "Fri Oct 10 2:54 PM"; year not shown)
- screen_capture_time: 2:54 PM
- taskbar_date: 10/10/2025, 2:54 PM (remote Windows taskbar clock bottom right) — supplies the year
- social_post_date: none visible
- report_start_date: 10/5/2025
- report_end_date: 10/10/2025
- contract_date_clue: none visible
- other date clue: macOS dock Calendar icon shows "OCT 10"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — same Jump Desktop "hp" remote window, NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", right-edge pinned Settings pane cropped.

## D STRATEGY IDENTITY
- No strategy name visible. Orange "Strategy Analyzer" tab; bottom tab "Analyzer" + "+". Italic "template" label at Settings pane footer (right-cropped). No account name visible.

## E DATA SERIES
- Instrument/contract/bar type/hours: not visible.
- Avg. bars in trade equals Avg. time in market in minutes (86.03/117.63/63.05) → 1-MINUTE bars (inference, same as batch siblings).

## F PARAMETERS (right-edge pinned Settings pane, top to bottom; labels cut off outside frame)
1. Header: "Settings" + pin icon + scroll arrows
2. partial box, top cut by header (only bottom edge visible) [unknown, crop: top]
3. numeric spinbox: "10" [full]
4. SEP (triangle + "...")
5. checkbox: CHECKED
6. numeric spinbox: "450?" (right-cropped) 
7. numeric spinbox: "200?" (right-cropped)
8. SEP
9. numeric spinbox: "65" [full]
10. numeric spinbox: "30" [full]
11. numeric spinbox: "65" [full]
12. numeric spinbox: "20" [full]
13. SEP
14. numeric spinbox: "1" [full]
15. SEP
16. checkbox: CHECKED
17. numeric spinbox: "80" [full]
18. SEP
19. text/numeric box: appears EMPTY [unknown]
20. dropdown: unreadable [enum]
21. dropdown: unreadable, faint leading dot [enum]
22. numeric spinbox: "1" [full]
23. SEP
24. dropdown: unreadable, tiny icon at left [enum]
25. dropdown: unreadable, tiny icon at left [enum]
26. dropdown: unreadable [enum]
27. checkbox: CHECKED
28. SEP
29. checkbox: UNCHECKED
30. partial grey box at bottom [unknown]
31. italic label "template" (right-cropped)
32. Button: "Run"

## G ENGINE SETTINGS
- Commission: $0.00 (not applied). Total slippage: 0.

## H PERFORMANCE (Summary ($); All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $5,790.00 | $375.00 | $5,415.00 |
| Gross profit | $22,525.00 | $6,820.00 | $15,705.00 |
| Gross loss | ($16,735.00) | ($6,445.00) | ($10,290.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.35 | 1.06 | 1.53 |
| Max. drawdown | ($7,815.00) | ($2,770.00) | ($6,290.00) |
| Sharpe ratio | 1.89 | 1.84 | 1.89 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.21 | 0.07 | 0.24 |
| Probability | 24.22% | 45.83% | 23.12% |
| Start date | 10/5/2025 | | |
| End date | 10/10/2025 | | |
| Total # of trades | 38 | 16 | 22 |
| Percent profitable | 44.74% | 43.75% | 45.45% |
| # of winning trades | 17 | 7 | 10 |
| # of losing trades | 21 | 9 | 12 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $152.37 | $23.44 | $246.14 |
| Avg. winning trade | $1,325.00 | $974.29 | $1,570.50 |
| Avg. losing trade | ($796.90) | ($716.11) | ($857.50) |
| Ratio avg. win / avg. loss | 1.66 | 1.36 | 1.83 |
| Max. consec. winners | 3 | 2 | 2 |
| Max. consec. losers | 5 | 2 | 4 |
| Largest winning trade | $5,315.00 | $1,825.00 | $5,315.00 |
| Largest losing trade | ($1,360.00) | ($1,300.00) | ($1,360.00) |
| Avg. # of trades per day | 11.01 | 4.63 | 6.37 |
| Avg. time in market | 86.03 min | 117.63 min | 63.05 min |
| Avg. bars in trade | 86.03 | 117.63 | 63.05 |
| Profit per month | $35,319.00 | $2,287.50 | $33,031.50 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark present (see K).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Same remote machine "hp", one week after OTRIMG-0073 (Oct 10 vs Oct 3), same weekly-backtest pattern (Sun→Fri window 10/5→10/10/2025).
- This week is NET POSITIVE $5,790 with shorts carrying the profit (short net $5,415, PF 1.53) — opposite of the Oct 3 week where shorts lost.
- Settings stack DIFFERS from OTRIMG-0073: the 4-number group reads 65/30/65/20 here vs 65/30/90/65 there, and an additional group [checked checkbox + "80"] exists between the "1" spinbox group and the empty-box/dropdown group, which is absent in OTRIMG-0073. Also pane is scrolled one-plus row down (a cut-off box above the "10").
- macOS menu bar shows an ACTIVE (red/orange) microphone indicator — mic in use during capture (possible ongoing call/recording); WeChat menu-bar icon shows badge "1".
- Remote taskbar shows one more pinned icon than 0073 (an extra blue app icon at right end of taskbar icon row).
- Watermark over dock: "ednote ID: 4384856832" (leading letters cropped; INFERRED "rednote ID:", i.e. Xiaohongshu; first digit 4 vs 1 LOW confidence — could read 1384856832).
- Bottom-left background fragment: word "Free" visible over dark backdrop.
IMPLICATIONS (hypotheses):
- The trader ran this analyzer weekly (Friday afternoon) on the just-ended week, live-tuning parameters between weeks (90→65, 65→20 change; a new enabled toggle with value 80 added — suggests strategy code was updated between Oct 3 and Oct 10, adding a parameter group).
- Consistent $0 commission, 1-min bars, weekly windows: same testing protocol across the JD series.
OPEN QUESTIONS:
- Whether the [checked+80] group is new code or a group that was collapsed/hidden in 0073.
- Full values of 450?/200?; identity of dropdown groups.
