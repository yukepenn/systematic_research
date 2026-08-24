# OTRIMG-0024

## A FILE IDENTITY
- id: OTRIMG-0024
- filename: 20260824_171607775_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Wed Feb 26 (macOS menu bar, top right) — year not shown; time 3:41 PM
- taskbar_date: 2/26/2025 (Windows taskbar clock, bottom right; taskbar time partially obscured by watermark)
- social_post_date: none visible
- report_start_date: 2/25/2025 (Summary table "Start date")
- report_end_date: 2/26/2025 (Summary table "End date")
- contract_date_clue: NQ MAR25 (Settings pane Instrument dropdown)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — macOS Jump Desktop window ("creator") showing a Windows NinjaTrader 8 Strategy Analyzer Summary ($) with pinned Settings pane fully visible on the right.

## D STRATEGY IDENTITY
- No strategy name visible anywhere (Strategy Analyzer tab bar shows only "Analyzer" tab; no strategy dropdown in view).
- Parameter names visible in Settings pane: "A4", "A5" (suggests parameters named A1..A5 style; row above A4 is cropped at the pane top showing only a spinbox with value 10).

## E DATA SERIES
- Instrument: NQ MAR25
- Price based on: Last
- Type: Minute
- Value: 1
- Tick Replay: unchecked
- Trading hours: "<Use instrument se..." (truncated; = Use instrument settings)
- Break at EOD: checked

## F PARAMETERS (Settings pane, top to bottom, exact order)
1. [numeric, top-cropped row, label not visible] value "10" (only bottom half of box visible)
2. A4 [numeric] = 10
3. A5 [numeric] = 10
4. Quantity [numeric] = 1
5. SEP — "Data Series" group header (collapse triangle)
6. Instrument [dropdown] = NQ MAR25
7. Price based on [dropdown] = Last
8. Type [dropdown] = Minute
9. Value [numeric] = 1
10. Tick Replay [bool] = unchecked
11. SEP — "Time frame" group header
12. Start date [date] = 02/25/2025
13. End date [date] = 02/26/2025
14. Trading hours [dropdown] = <Use instrument se... (truncated)
15. Break at EOD [bool] = checked
16. SEP — "Setup" group header
17. Include commission [bool] = checked
18. Commission template [dropdown] = NinjaTrader Broker... (truncated)
19. Maximum bars look... [dropdown] = 256
20. Bars required to trade [numeric] = 20
21. SEP — "Historical fill proces..." group header (truncated)
22. Order fill resolution [dropdown] = Standard (Fastest)
23. Fill limit orders on t... [bool] = unchecked
24. Slippage [numeric] = 0
25. SEP — "Order handling" group header
26. Entries per direction [numeric] = 1
27. Entry handling [dropdown] = All entries
28. Exit on session close [bool] = checked
29. Text "template" (link/label at bottom right of pane)
30. Run button (bottom right, partially covered by red Chinese watermark characters)

## G ENGINE SETTINGS
- Include commission: checked; Commission template: "NinjaTrader Broker..." (truncated)
- Order fill resolution: Standard (Fastest); Fill limit orders on t...: unchecked; Slippage: 0
- Entries per direction: 1; Entry handling: All entries; Exit on session close: checked
- Maximum bars look back: 256; Bars required to trade: 20; Break at EOD: checked

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $4,582.76 | $838.88 | $3,743.88 |
| Gross profit | $10,965.24 | $3,701.60 | $7,263.64 |
| Gross loss | ($6,382.48) | ($2,862.72) | ($3,519.76) |
| Commission | $102.24 | $51.12 | $51.12 |
| Profit factor | 1.72 | 1.29 | 2.06 |
| Max. drawdown | ($2,984.08) | ($1,556.36) | ($3,118.40) |
| Sharpe ratio | 3.22 | 3.09 | 4.89 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.33 | 0.54 | 0.06 |
| Probability | 21.86% | 34.72% | 24.17% |
| Start date | 2/25/2025 | | |
| End date | 2/26/2025 | | |
| Total # of trades | 18 | 9 | 9 |
| Percent profitable | 38.89% | 55.56% | 22.22% |
| # of winning trades | 7 | 5 | 2 |
| # of losing trades | 11 | 4 | 7 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $254.60 | $93.21 | $415.99 |
| Avg. winning trade | $1,566.46 | $740.32 | $3,631.82 |
| Avg. losing trade | ($580.23) | ($715.68) | ($502.82) |
| Ratio avg. win / avg. loss | 2.70 | 1.03 | 7.22 |
| Max. consec. winners | 2 | 3 | 1 |
| Max. consec. losers | 4 | 2 | 5 |
| Largest winning trade | $4,824.32 | $1,219.32 | $4,824.32 |
| Largest losing trade | ($1,325.68) | ($1,325.68) | ($1,295.68) |
| Avg. # of trades per day | 8.69 | 4.35 | 6.52 |
| Avg. time in market | 81.39 min | 126.22 min | 36.56 min |
| Avg. bars in trade | 81.39 | 126.22 | 36.56 |
| Profit per month | $46,591.39 | $8,528.61 | $57,094.17 |

## I GRAPH MORPHOLOGY
n/a (no graph shown)

## J SOCIAL CONTENT
n/a — only a watermark: "rednote ID: 1384856832" overlaid at bottom right (xiaohongshu/rednote export watermark; not a post).

## K FORENSIC INTERPRETATION
- Direct facts: 2-day backtest window 2/25/2025–2/26/2025 on NQ MAR25, 1-Minute Last bars; capture made the same day as the report end (Feb 26, 3:41 PM Mac clock; Windows taskbar 2/26/2025). Machine name "creator" (Jump Desktop title). Commission $102.24 on 18 trades = $5.68/RT? No: 18 trades × $5.68 = $102.24 → $5.68 per round turn per contract (NOT the $4.36 Lifetime rate; consistent with NinjaTrader Brokerage Monthly/Free rate tier), template dropdown shows "NinjaTrader Broker...".
- Parameter clue: visible parameter names A4=10, A5=10 (plus one cropped 10 above) imply a strategy whose public parameters are named A1..A5 (or similar letter+digit scheme) — generic obfuscated names.
- Avg. bars in trade equals avg. time in market in minutes (81.39) — confirms 1-minute bars.
- Watermark "rednote ID: 1384856832" ties this image to a xiaohongshu (rednote) account; red Chinese characters partially overlay the Run button (watermark, mostly illegible).
- Hypothesis (labeled): the Settings pane is fully expanded here (not cropped), so this image gives the complete lower half of the parameter stack; only rows above "A4" are cut off at pane top.
- Open question: strategy name and count/values of parameters above A4.
