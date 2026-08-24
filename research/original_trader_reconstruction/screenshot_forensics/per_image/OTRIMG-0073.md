# OTRIMG-0073

## A FILE IDENTITY
- id: OTRIMG-0073
- filename: 20260824_171921110_iOS.jpg
- resolution: 1440 x 936

## B DATE EVIDENCE
- screen_capture_date: Fri Oct 3 (macOS menu bar top-right, "Fri Oct 3 4:21 PM"; year not shown in menu bar)
- screen_capture_time: 4:21 PM
- taskbar_date: 10/3/2025, 4:21 PM (remote Windows taskbar clock, bottom right) — supplies the year for the macOS clock
- social_post_date: none visible
- report_start_date: 9/28/2025 (Strategy Analyzer "Start date" row)
- report_end_date: 10/3/2025 (Strategy Analyzer "End date" row)
- contract_date_clue: none visible (no instrument/contract shown)
- other date clue: macOS dock Calendar icon shows "OCT 3"; background email row shows "9/24/25"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — macOS Jump Desktop window (title "hp") showing a remote Windows machine running NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", with pinned Settings pane cropped at right edge.

## D STRATEGY IDENTITY
- No strategy name visible. Window shows only orange "Strategy Analyzer" tab header; bottom tab strip shows "Analyzer" + "+" tab. No account name visible.
- Right pane footer shows italic text "template" (label cropped, likely "template" link/row of the Settings pane).

## E DATA SERIES
- Instrument/contract: not visible
- Bar type/value: not visible
- Trading hours: not visible

## F PARAMETERS (right-edge pinned Settings pane, top to bottom; ALL labels are cut off outside the frame — only the value boxes are visible)
1. Header: "Settings" with pin icon and scroll up/down arrows
2. numeric spinbox: "179?" (right-cropped; visible digits 1,7,9 — more digits may follow) [crop: right edge]
3. numeric spinbox: "5" [full]
4. numeric spinbox: "10" [full]
5. numeric spinbox: "10" [full]
6. SEP (collapse triangle + "...")
7. checkbox: CHECKED [bool]
8. numeric spinbox: "450?" (right-cropped; visible 4,5,0 — more digits may follow) [crop: right edge]
9. numeric spinbox: "200?" (right-cropped; visible 2,0,0 — more digits may follow) [crop: right edge]
10. SEP (collapse triangle + "...")
11. numeric spinbox: "65" [full]
12. numeric spinbox: "30" [full]
13. numeric spinbox: "90" [full]
14. numeric spinbox: "65" [full]
15. SEP (collapse triangle + "...")
16. numeric spinbox: "1" [full]
17. SEP (collapse triangle + "...")
18. text/numeric box: appears EMPTY (grey, no visible glyph) [unknown]
19. dropdown: value unreadable (only "v" glyph visible) [enum]
20. dropdown: value unreadable, faint leading dot/char (only "v" glyph clear) [enum]
21. numeric spinbox: "1" [full]
22. SEP (collapse triangle + "...")
23. dropdown: value unreadable, tiny icon-like glyph at left (looks like a stacked/lines icon) [enum]
24. dropdown: value unreadable, tiny icon-like glyph at left [enum]
25. dropdown: value unreadable [enum]
26. checkbox: CHECKED [bool]
27. SEP (collapse triangle + "...")
28. checkbox: UNCHECKED [bool]
29. partially visible grey box at bottom cut by Run button area [unknown]
30. italic label "template" (right-cropped)
31. Button: "Run"

## G ENGINE SETTINGS
- Commission row in report: $0.00 (all columns) — commission NOT applied in this run
- Slippage: Total slippage = 0 (all columns)
- No other engine settings visible

## H PERFORMANCE (Display: Summary ($); columns All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($2,205.00) | $1,645.00 | ($3,850.00) |
| Gross profit | $9,580.00 | $7,480.00 | $2,100.00 |
| Gross loss | ($11,785.00) | ($5,835.00) | ($5,950.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.81 | 1.28 | 0.35 |
| Max. drawdown | ($4,695.00) | ($3,020.00) | ($5,180.00) |
| Sharpe ratio | -5.01 | 5.24 | -5.32 |
| Sortino ratio | -8.97 | 1.00 | -11.70 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.01 | 0.53 | 0.68 |
| Probability | 65.76% | 35.99% | 94.96% |
| Start date | 9/28/2025 | | |
| End date | 10/3/2025 | | |
| Total # of trades | 29 | 15 | 14 |
| Percent profitable | 34.48% | 40.00% | 28.57% |
| # of winning trades | 10 | 6 | 4 |
| # of losing trades | 19 | 9 | 10 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($76.03) | $109.67 | ($275.00) |
| Avg. winning trade | $958.00 | $1,246.67 | $525.00 |
| Avg. losing trade | ($620.26) | ($648.33) | ($595.00) |
| Ratio avg. win / avg. loss | 1.54 | 1.92 | 0.88 |
| Max. consec. winners | 2 | 2 | 3 |
| Max. consec. losers | 6 | 3 | 6 |
| Largest winning trade | $4,010.00 | $4,010.00 | $1,125.00 |
| Largest losing trade | ($1,150.00) | ($1,035.00) | ($1,000.00) |
| Avg. # of trades per day | 8.40 | 4.35 | 4.06 |
| Avg. time in market | 94.72 min | 143.47 min | 42.50 min |
| Avg. bars in trade | 94.72 | 143.47 | 42.50 |
| Profit per month | ($13,450.50) | $10,034.50 | ($23,485.00) |

## I GRAPH MORPHOLOGY
n/a (Summary table view, no graph)

## J SOCIAL CONTENT
n/a (no social content). Watermark present, see K.

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Jump Desktop remote session titled "hp" (remote machine name, lowercase).
- Capture moment Oct 3 2025 4:21 PM, remote Windows clock agrees (10/3/2025 4:21 PM) — local and remote in same timezone at capture.
- Backtest window is very short: 9/28/2025 → 10/3/2025 (≈1 trading week), 29 trades, net NEGATIVE ($2,205) with commission $0.
- Long side profitable (PF 1.28), short side deeply unprofitable (PF 0.35) in this week.
- Avg. bars in trade numerically equals Avg. time in market minutes (94.72 / 143.47 / 42.50) → the data series is 1-MINUTE bars.
- Watermark across dock: white text "ednote ID: 4384856832" (leading letter(s) cropped; INFERRED full text "rednote ID: 4384856832" — rednote = Xiaohongshu/小红书 screenshot watermark; first digit 4 vs 1 LOW confidence, and digits partially obscured by dock icons).
- Settings pane top group (179?, 5, 10, 10), then checked box + (450?, 200?), then (65, 30, 90, 65), then 1, then empty box + 2 dropdowns + 1, then 3 dropdowns + checked box, then unchecked box.
- macOS dock includes: Finder, Safari, Mail, Calendar (OCT 3), Settings (badge 1), TradingView, Chrome, Books, Obsidian, Photos, printer utility, WeChat, Telegram, a ZIP file, Trash — user has TradingView, WeChat, Telegram, Obsidian installed.
- Background bottom-left: macOS Mail/notification fragment "1 new message"; an email list row "GEICO ... 9/24/25" partially visible.
IMPLICATIONS (hypotheses):
- The screenshot was originally posted to Xiaohongshu (rednote) by user ID 4384856832 and this file is a re-download/re-capture of that post (watermark burned in).
- The parameter stack (65/30/90/65 + 179?) resembles oscillator-style thresholds; group structure suggests a strategy with ~7 parameter groups.
- $0 commission and 1-min bars matches the OTR original-trader run style seen elsewhere in the campaign.
OPEN QUESTIONS:
- Full values of the right-cropped numbers (179?, 450?, 200?).
- Strategy name, instrument, contract (not visible in this view).
