# OTRIMG-0022

## A FILE IDENTITY
- id: OTRIMG-0022
- filename: 20260824_171602469_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Mon Feb 24, 2:59 PM (macOS menu bar)
- taskbar_date: 2/24/2025 (Windows taskbar; time obscured by watermark, "2:5? PM" partial — LOW confidence on minutes)
- social_post_date: none visible
- report_start_date: 2/23/2025 (table; settings Start date 02/23/2025)
- report_end_date: 2/24/2025 (table; settings End date 02/24/2025)
- contract_date_clue: Instrument "NQ MAR25"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)", full Settings panel scrolled to start at Data Series; Order properties group fully visible at bottom.

## D STRATEGY IDENTITY
- Strategy name NOT visible (General group scrolled out). Machine name "creator".

## E DATA SERIES
- Instrument: NQ MAR25; Price based on: Last; Type: Minute; Value: 1; Tick Replay: unchecked
- Trading hours: "<Use instrument se..."; Break at EOD: CHECKED

## F PARAMETERS (Settings panel as scrolled, top to bottom)
1. SEP — Data Series
2. Instrument [enum]: NQ MAR25
3. Price based on [enum]: Last
4. Type [enum]: Minute
5. Value [numeric]: 1
6. Tick Replay [bool]: UNCHECKED
7. SEP — Time frame
8. Start date [date]: 02/23/2025
9. End date [date]: 02/24/2025
10. Trading hours [enum]: <Use instrument se...
11. Break at EOD [bool]: CHECKED
12. SEP — Setup
13. Include commission [bool]: CHECKED
14. Commission template [enum]: "NinjaTrader Broker..." (right-truncated)
15. Maximum bars look... [enum]: 256
16. Bars required to trade [numeric]: 20
17. SEP — Historical fill proces...
18. Order fill resolution [enum]: Standard (Fastest)
19. Fill limit orders on t... [bool]: UNCHECKED
20. Slippage [numeric]: 0
21. SEP — Order handling
22. Entries per direction [numeric]: 1
23. Entry handling [enum]: All entries
24. Exit on session close [bool]: CHECKED
25. SEP — Order properties
26. Set order quantity [enum]: Strategy
27. Time in force [enum]: GTC
28. "template"; "Run" button (under watermark)
- A-parameters/Quantity/LossLimit not visible (scrolled above frame).

## G ENGINE SETTINGS
- Include commission checked, template "NinjaTrader Broker..."; commission $45.44 on 8 trades = $5.68/trade (DIFFERENT from the $4.18/trade of all earlier frames). Slippage 0; Standard (Fastest); Exit on session close checked; Set order quantity = Strategy; TIF = GTC.

## H PERFORMANCE (All / Long / Short), 2/23/2025–2/24/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | $8,229.56 | ($147.72) | $8,377.28 |
| Gross profit | $9,741.60 | $818.64 | $8,922.96 |
| Gross loss | ($1,512.04) | ($966.36) | ($545.68) |
| Commission | $45.44 | $22.72 | $22.72 |
| Profit factor | 6.44 | 0.85 | 16.35 |
| Max. drawdown | ($947.04) | ($600.68) | ($545.68) |
| Sharpe ratio | 5.28 | -4.59 | 12.39 |
| Sortino ratio | 1.00 | -15.21 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.86 | 0.52 | 0.92 |
| Probability | 6.45% | 56.82% | 4.13% |
| Start date | 2/23/2025 | | |
| End date | 2/24/2025 | | |
| Total # of trades | 8 | 4 | 4 |
| Percent profitable | 62.50% | 50.00% | 75.00% |
| # of winning trades | 5 | 2 | 3 |
| # of losing trades | 3 | 2 | 1 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $1,028.70 | ($36.93) | $2,094.32 |
| Avg. winning trade | $1,948.32 | $409.32 | $2,974.32 |
| Avg. losing trade | ($504.01) | ($483.18) | ($545.68) |
| Ratio avg. win / avg. loss | 3.87 | 0.85 | 5.45 |
| Max. consec. winners | 3 | 2 | 3 |
| Max. consec. losers | 1 | 1 | 1 |
| Largest winning trade | $4,904.32 | $619.32 | $4,904.32 |
| Largest losing trade | ($600.68) | ($600.68) | ($545.68) |
| Avg. # of trades per day | 5.79 | 2.90 | 5.79 |
| Avg. time in market | 116.13 min | 101.75 min | 130.50 min |
| Avg. bars in trade | 116.00 | 101.50 | 130.50 |
| Profit per month | $125,500.79 | ($2,252.73) | $255,507.04 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" + blurred circular stamp over Run area.
- Windows 11 taskbar: Start, Search (whale-like seasonal icon), mail, File Explorer, Edge, NinjaTrader (active), Chrome, Excel, notepad, gear/utility; tray: ENG, network/volume/battery, 2/24/2025.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: Sun-Mon window 2/23-2/24/2025: 8 trades, +$8,229.56, shorts produced nearly all profit (+$8,377.28). Per-trade commission $5.68 (= 2 × $2.84) — trade PnLs end in .32/.68 instead of the earlier .82/.18, PROVING a commission-rate change (from $4.18/RT to $5.68/RT) between Feb 21 and Feb 24 while still using a "NinjaTrader Broker..." template. Order properties finally visible: Set order quantity = Strategy, TIF = GTC.
- IMPLICATIONS: $5.68/RT ≈ NinjaTrader Brokerage Free-plan-style commission with exchange fees at a higher rate; the campaign's frozen $4.36/RT Lifetime template matches NEITHER February rate — reconstruction parity must model $4.18/RT before ~Feb 21 and $5.68/RT after — HYPOTHESIS pending template identification. "Set order quantity = Strategy" implies the strategy code, not the dialog, controls position size (relevant to the 3-lot anomaly in OTRIMG-0010).
- OPEN QUESTIONS: strategy name/parameters for this run; exact commission template variant; whether 2/23 (Sunday evening session) contributed trades.
