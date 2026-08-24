# OTRIMG-0146

## A FILE IDENTITY
- id: OTRIMG-0146
- filename: 20260824_173049582_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Sat May 23, 10:01 PM (macOS menu bar; year not shown)
- taskbar_date: 10:01 PM / 5/23/2026 (Windows taskbar, bottom right, partially obscured by watermark)
- social_post_date: none visible
- report_start_date: 5/10/2026 (Summary table) — also Settings "Start date" = 05/10/2026
- report_end_date: 5/22/2026 (Summary table) — also Settings "End date" = 05/22/2026
- contract_date_clue: Instrument "NQ JUN26" (June 2026 contract)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop (remote machine "dev"), NinjaTrader 8 Strategy Analyzer Summary ($) with the Settings pane FULLY EXPANDED and labels readable (key image of the JD series).

## D STRATEGY IDENTITY
- No strategy name row visible (Settings pane is scrolled; first visible row is "Volume Base" — rows above it, including the strategy selector, are scrolled out of view).
- "template" label above Run button; no template value shown.

## E DATA SERIES
- Instrument: NQ JUN26
- Price based on: Last
- Type: Minute
- Value: 1
- Trading hours: <Use instrument settings>
- Break at EOD: CHECKED

## F PARAMETERS (Settings pane, exact vertical order, labels + values fully visible)
1. Volume Base [dropdown] = "BidAskPrice_RealVolume"
2. Anchor Period (Minutes) [numeric] = 60
3. VWAP Amount [numeric] = 5
4. Trend Period [numeric] = 20
5. Trend MA Type [dropdown] = "EMA"
6. Max Percent [numeric] = 95
7. Upper Percent [numeric] = 75
8. Median Percent [numeric] = 50
9. Lower Percent [numeric] = 25
10. Min Percent [numeric] = 5
11. Signal Quantity Per Trend [numeric] = 3
12. Signal Close Threshold (%) [numeric] = 10
13. Signal Split (Bars) [numeric] = 5
14. SEP — "Data Series" group header
15. Instrument [dropdown] = "NQ JUN26"
16. Price based on [dropdown] = "Last"
17. Type [dropdown] = "Minute"
18. Value [numeric] = 1
19. SEP — "Time frame" group header
20. Start date [date] = 05/10/2026
21. End date [date] = 05/22/2026
22. Trading hours [dropdown] = "<Use instrument settings>"
23. Break at EOD [bool] = CHECKED
24. SEP — "Setup" group header
25. Include commission [bool] = UNCHECKED
26. Commission template [dropdown] = grayed/disabled, empty
27. Maximum bars look back [numeric] = 256
28. label "template"; [button] "Run"

## G ENGINE SETTINGS
- Include commission: UNCHECKED; Commission template disabled/empty → commission $0 in results.
- Maximum bars look back: 256. Trading hours: <Use instrument settings>. Break at EOD: checked.
- Slippage: results show Total slippage 0 (no slippage control visible).

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($4,055.00) | $4,645.00 | ($8,700.00) |
| Gross profit | $85,295.00 | $49,945.00 | $35,350.00 |
| Gross loss | ($89,350.00) | ($45,300.00) | ($44,050.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.95 | 1.10 | 0.80 |
| Max. drawdown | ($12,700.00) | ($10,260.00) | ($11,370.00) |
| Sharpe ratio | 0.71 | 0.71 | 0.71 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.01 |
| R squared | 0.54 | 0.00 | 0.46 |
| Probability | 59.43% | 34.46% | 76.17% |
| Start date | 5/10/2026 | | |
| End date | 5/22/2026 | | |
| Total # of trades | 183 | 94 | 89 |
| Percent profitable | 37.70% | 41.49% | 33.71% |
| # of winning trades | 69 | 39 | 30 |
| # of losing trades | 114 | 55 | 59 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($22.16) | $49.41 | ($97.75) |
| Avg. winning trade | $1,236.16 | $1,280.64 | $1,178.33 |
| Avg. losing trade | ($783.77) | ($823.64) | ($746.61) |
| Ratio avg. win / avg. loss | 1.58 | 1.55 | 1.58 |
| Max. consec. winners | 5 | 5 | 3 |
| Max. consec. losers | 7 | 7 | 8 |
| Largest winning trade | $4,225.00 | $4,130.00 | $4,225.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,270.00) |
| Avg. # of trades per day | 20.39 | 10.47 | 9.92 |
| Avg. time in market | 39.84 min | 48.99 min | 30.17 min |
| Avg. bars in trade | 39.84 | 48.99 | 30.17 |
| Profit per month | ($9,513.65) | $10,897.88 | ($20,411.54) |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: THE key parameter-template image of this batch. Full strategy parameter list with values: BidAskPrice_RealVolume volume base, 60-min anchored VWAP, VWAP Amount 5, Trend Period 20 EMA, percentile bands 95/75/50/25/5, Signal Quantity Per Trend 3, Signal Close Threshold 10%, Signal Split 5 bars. This identifies the strategy family as an anchored-VWAP / volume-profile percentile-band system with real-volume bid/ask classification.
- Data series: NQ JUN26, 1-Minute Last bars, instrument default trading hours, Break at EOD on, no commission, 256 bars look-back.
- Backtest window 5/10/2026–5/22/2026 (2 weeks): net −$4,055 over 183 trades; long side mildly positive, short side negative (recurring long/short asymmetry across the JD series).
- Screenshot taken Sat May 23, 10:01 PM — the day after the report window ends (5/22/2026 is Friday).
- Avg time in market equals avg bars in trade (39.84 = 39.84) → consistent with 1-minute bars as configured.
- Watermark bottom right: "...ednote ID: 1384856832" (partially cut at left; very likely "rednote ID" = Xiaohongshu/RED user-ID watermark; digits LOW confidence — could be 1384856832 or 1334856832). Same style watermark seen on OTRIMG-0142.
- Remote machine "dev". macOS dock similar to OTRIMG-0142 (TradingView, Telegram, Terminal with badge 1, Windows App, etc.); Windows taskbar shows NinjaTrader, Chrome, notes app, a monitor-style icon, gear/settings icon.
- Open questions: strategy name (scrolled off above "Volume Base"); whether additional parameter rows exist above Volume Base.
