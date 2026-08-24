# OTRIMG-0142

## A FILE IDENTITY
- id: OTRIMG-0142
- filename: 20260824_172732904_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri May 8, 4:03 PM (macOS menu bar, top right; year not shown)
- taskbar_date: 4:03 PM / 5/8/2026 (Windows taskbar clock, bottom right of remote session; partially covered by watermark)
- social_post_date: none visible
- report_start_date: 5/3/2026 (Strategy Analyzer "Start date" row)
- report_end_date: 5/8/2026 (Strategy Analyzer "End date" row)
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — macOS Jump Desktop window (remote machine "dev") showing NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", with pinned Settings pane cropped at right edge.

## D STRATEGY IDENTITY
- No strategy name visible. Window title of remote session: "dev". Analyzer tab at bottom left: "Analyzer" (+ a "+" tab button).
- Bottom-right of Settings pane shows the word "template" (label above Run button), no template value readable.

## E DATA SERIES
- No instrument/contract/bar-type text visible (Settings pane is cropped so labels are cut off; only control boxes visible).

## F PARAMETERS (right-edge pinned Settings pane, top to bottom; all labels cropped off, only right-hand halves of controls visible)
1. [numeric] "5" — spinbox, half-cropped
2. SEP (collapse triangle + "...")
3. [unknown] empty-looking box, cropped
4. [dropdown] "v" glyph, value unreadable
5. [dropdown] "v" glyph with leading dot, value unreadable
6. [numeric] "1"
7. SEP (collapse triangle + "...")
8. [dropdown] box with list/scroll glyph + "v", value unreadable
9. [dropdown] box with list/scroll glyph + "v", value unreadable
10. [dropdown] "v" glyph, value unreadable
11. [bool] checkbox CHECKED
12. SEP (collapse triangle + "...")
13. [bool] checkbox UNCHECKED
14. [dropdown] grayed/disabled "v" (disabled control)
15. [dropdown] "v" glyph, value unreadable
16. [numeric] "20"
17. SEP (collapse triangle + "...")
18. [dropdown] "v" glyph, value unreadable
19. [bool] checkbox UNCHECKED
20. [numeric] "0"
21. SEP (collapse triangle + "...")
22. [numeric] "2"
23. [dropdown] "v" glyph, value unreadable
24. [bool] checkbox CHECKED
25. SEP (collapse triangle + "...")
26. [dropdown] "v" glyph, value unreadable
27. [dropdown] "v" glyph, value unreadable
28. label text: "template"
29. [button] "Run"
- Settings pane header: "Settings" with pin icon; up/down spinner arrows at very top right ("5" box likely part of a spin control).

## G ENGINE SETTINGS
- Commission row in results = $0.00 (all columns) → commission NOT configured for this run.
- Total slippage row = 0. No other engine settings visible.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($2,205.00) | $14,285.00 | ($16,490.00) |
| Gross profit | $33,790.00 | $27,525.00 | $6,265.00 |
| Gross loss | ($35,995.00) | ($13,240.00) | ($22,755.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.94 | 2.08 | 0.28 |
| Max. drawdown | ($14,790.00) | ($4,120.00) | ($16,835.00) |
| Sharpe ratio | 1.54 | 1.61 | -1.74 |
| Sortino ratio | 1.00 | 1.00 | -5.77 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.17 | 0.74 | 0.96 |
| Probability | 58.71% | 8.43% | 99.91% |
| Start date | 5/3/2026 | | |
| End date | 5/8/2026 | | |
| Total # of trades | 56 | 27 | 29 |
| Percent profitable | 33.93% | 44.44% | 24.14% |
| # of winning trades | 19 | 12 | 7 |
| # of losing trades | 37 | 15 | 22 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($39.38) | $529.07 | ($568.62) |
| Avg. winning trade | $1,778.42 | $2,293.75 | $895.00 |
| Avg. losing trade | ($972.84) | ($882.67) | ($1,034.32) |
| Ratio avg. win / avg. loss | 1.83 | 2.60 | 0.87 |
| Max. consec. winners | 2 | 2 | 1 |
| Max. consec. losers | 7 | 5 | 6 |
| Largest winning trade | $5,930.00 | $5,930.00 | $1,995.00 |
| Largest losing trade | ($2,600.00) | ($2,030.00) | ($2,600.00) |
| Avg. # of trades per day | 13.52 | 6.52 | 8.40 |
| Avg. time in market | 70.34 min | 102.70 min | 40.21 min |
| Avg. bars in trade | 70.34 | 102.70 | 40.21 |
| Profit per month | ($11,208.75) | $72,615.42 | ($100,589.00) |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: 5-day backtest window 5/3/2026–5/8/2026 (Sun–Fri), 56 trades, net −$2,205, zero commission/slippage. Long side strongly positive (+$14,285, PF 2.08), short side strongly negative (−$16,490, PF 0.28). Avg time in market 70.34 min equal to avg bars in trade 70.34 → 1-minute bars INFERRED (min per trade == bars per trade).
- Screenshot taken at 4:03 PM on the report end date itself (5/8/2026), i.e. same-day review of a just-finished week.
- Point sizes: largest win $5,930, avg magnitudes in $5 multiples → consistent with NQ ($20/pt) or similar; $2,205/56 style numbers all divisible by 5.
- Watermark bottom right over dock: partially readable "...te ID: 1234856832" (digits LOW confidence; likely a remote/meeting ID watermark, possibly "remote ID"). A second faint circular watermark fragment above the taskbar right corner (unreadable).
- Remote machine name "dev" (Jump Desktop title). Windows 11 taskbar: Start, Search, File Explorer icon, NinjaTrader icon (orange NT), Chrome, a notes-style icon, Brave(?) shield icon.
- macOS dock includes: Finder, Launchpad, Safari, Mail, Calendar (showing MAY 8), Reminders/Notes-type apps, App Store, a black-wave icon app, a photos-like app, Settings (badge "1"), TradingView (black tv icon), a screen-mirroring/display app, Microsoft/Windows App (blue), a globe/green app, Telegram, Terminal, more notes apps, and trash. Presence of TradingView on the Mac dock is notable.
- Hypothesis (labeled): the Settings pane control stack (5 / [] / v / v / 1 / ... / 20 / ... / 0 / 2 / checked boxes) is the strategy's parameter column; matches the same cropped Settings layout seen across the JD-series screenshots, so cross-image alignment can recover the parameter template.
- Open questions: strategy name and instrument not visible; which parameter each cropped box maps to.
