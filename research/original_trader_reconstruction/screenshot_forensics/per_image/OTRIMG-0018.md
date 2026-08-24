# OTRIMG-0018

## A FILE IDENTITY
- id: OTRIMG-0018
- filename: 20260824_171550244_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Thu Feb 20, 6:18 PM (macOS menu bar)
- taskbar_date: 2/20/2025 (Windows taskbar; time obscured by watermark — LOW confidence on minutes)
- social_post_date: none visible
- report_start_date: 2/19/2025 (table; settings Start date 02/19/2025)
- report_end_date: 2/20/2025 (table; settings End date 02/20/2025)
- contract_date_clue: Instrument "NQ MAR25"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)", full Settings panel scrolled (starts at A5) through Order properties group header.

## D STRATEGY IDENTITY
- Strategy name NOT visible (scrolled). Machine name "creator".

## E DATA SERIES
- Instrument: NQ MAR25; Price based on: Last; Type: Minute; Value: 1; Tick Replay: unchecked
- Trading hours: "<Use instrument se..."; Break at EOD: CHECKED

## F PARAMETERS (Settings panel as scrolled, top to bottom)
1. A5 [numeric]: 10 (top row, half-clipped by panel edge — value box reads 10)
2. Quantity [numeric]: 1
3. SEP — Data Series
4. Instrument [enum]: NQ MAR25
5. Price based on [enum]: Last
6. Type [enum]: Minute
7. Value [numeric]: 1
8. Tick Replay [bool]: UNCHECKED
9. SEP — Time frame
10. Start date [date]: 02/19/2025
11. End date [date]: 02/20/2025
12. Trading hours [enum]: <Use instrument se...
13. Break at EOD [bool]: CHECKED
14. SEP — Setup
15. Include commission [bool]: CHECKED
16. Commission template [enum]: "NinjaTrader Broker..." (right-truncated)
17. Maximum bars look... [enum]: 256
18. Bars required to trade [numeric]: 20
19. SEP — Historical fill proces...
20. Order fill resolution [enum]: Standard (Fastest)
21. Fill limit orders on t... [bool]: UNCHECKED
22. Slippage [numeric]: 0
23. SEP — Order handling
24. Entries per direction [numeric]: 1
25. Entry handling [enum]: All entries
26. Exit on session close [bool]: CHECKED
27. SEP — Order properties (group header; rows below cut off at "Set order quantity"-like row, illegible)
28. "template"; "Run" button (under watermark)
- NO LossLimit between A5/Quantity and Data Series → this run's strategy appears to lack LossLimit (back to a SelTime-type class) — INFERENCE from layout.

## G ENGINE SETTINGS
- Include commission checked with Commission template "NinjaTrader Broker..." selected; $41.80 / 10 trades = $4.18/trade. Slippage 0; Standard (Fastest); Exit on session close checked.

## H PERFORMANCE (All / Long / Short), 2/19/2025–2/20/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | $1,848.20 | ($876.72) | $2,724.92 |
| Gross profit | $4,533.28 | $415.82 | $4,117.46 |
| Gross loss | ($2,685.08) | ($1,292.54) | ($1,392.54) |
| Commission | $41.80 | $16.72 | $25.08 |
| Profit factor | 1.69 | 0.32 | 2.96 |
| Max. drawdown | ($1,240.90) | ($888.36) | ($804.18) |
| Sharpe ratio | 4.74 | -4.53 | 4.80 |
| Sortino ratio | 1.00 | -15.04 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.55 | 0.07 | 0.61 |
| Probability | 28.74% | 83.74% | 18.92% |
| Start date | 2/19/2025 | | |
| End date | 2/20/2025 | | |
| Total # of trades | 10 | 4 | 6 |
| Percent profitable | 40.00% | 25.00% | 50.00% |
| # of winning trades | 4 | 1 | 3 |
| # of losing trades | 6 | 3 | 3 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $184.82 | ($219.18) | $454.15 |
| Avg. winning trade | $1,133.32 | $415.82 | $1,372.49 |
| Avg. losing trade | ($447.51) | ($430.85) | ($464.18) |
| Ratio avg. win / avg. loss | 2.53 | 0.97 | 2.96 |
| Max. consec. winners | 3 | 1 | 2 |
| Max. consec. losers | 2 | 2 | 1 |
| Largest winning trade | $3,130.82 | $415.82 | $3,130.82 |
| Largest losing trade | ($879.18) | ($879.18) | ($804.18) |
| Avg. # of trades per day | 7.24 | 2.90 | 4.35 |
| Avg. time in market | 75.30 min | 73.75 min | 76.33 min |
| Avg. bars in trade | 75.30 | 73.75 | 76.33 |
| Profit per month | $28,185.05 | ($13,369.98) | $41,555.03 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" + blurred circular stamp over Run area.
- Windows 11 taskbar: Start, Search (cupcake-like seasonal icon), mail, File Explorer, Edge, NinjaTrader (active), VS Code, notepad, green-circle app; tray: ENG, network/volume/battery, 2/20/2025.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: Two-day verification run 2/19-2/20 with commission back ON via a "NinjaTrader Broker..." commission template; net +$1,848.20 on 10 trades; per-trade commission $4.18.
- IMPLICATIONS: First direct sighting of the commission-template NAME family ("NinjaTrader Broker…") — ties to the known NinjaTrader Brokerage template convention, but the arithmetic implies a $4.18/RT rate rather than the $4.36/RT Lifetime rate used in the campaign's frozen baseline (Free template = $2.09/side = $4.18/RT — HYPOTHESIS: they use the Free/older rate template).
- OPEN QUESTIONS: which strategy class ran here (no LossLimit visible → SelTime variant? name scrolled out); full commission template name.
