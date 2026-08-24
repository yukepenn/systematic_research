# OTRIMG-0012

## A FILE IDENTITY
- id: OTRIMG-0012
- filename: 20260824_171529572_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Tue Feb 11, 9:07 PM (macOS menu bar)
- taskbar_date: none visible (Windows taskbar not in frame; NT window fills remote screen)
- social_post_date: none visible
- report_start_date: 2/9/2025 (table; settings Start date 02/09/2025)
- report_end_date: 2/11/2025 (table; settings End date 02/11/2025)
- contract_date_clue: Instrument "NQ MAR25"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)" with FULL Settings panel, scrolled to show Order handling group as well.

## D STRATEGY IDENTITY
- Strategy dropdown (verbatim): "SolarWindRKSelTime"
- Machine name: "creator". Bottom tab "Analyzer" (+).

## E DATA SERIES
- Instrument: NQ MAR25; Price based on: Last; Type: Minute; Value: 1; Tick Replay: unchecked
- Trading hours: "<Use instrument se..."; Break at EOD: checked

## F PARAMETERS (full Settings panel, top to bottom)
1. SEP — General
2. Backtest type [enum]: Backtest
3. Strategy [enum]: SolarWindRKSelTime
4. SEP — Parameters
5. A1 [numeric]: 90
6. A2 [numeric]: 179
7. A3 [numeric]: 5
8. A4 [numeric]: 10
9. A5 [numeric]: 10
10. Quantity [numeric]: 1
11. SEP — Data Series
12. Instrument [enum]: NQ MAR25
13. Price based on [enum]: Last
14. Type [enum]: Minute
15. Value [numeric]: 1
16. Tick Replay [bool]: UNCHECKED
17. SEP — Time frame
18. Start date [date]: 02/09/2025
19. End date [date]: 02/11/2025
20. Trading hours [enum]: <Use instrument se...
21. Break at EOD [bool]: CHECKED
22. SEP — Setup
23. Include commission [bool]: CHECKED
24. Maximum bars look... [enum]: 256
25. Bars required to trade [numeric]: 20
26. SEP — Historical fill proces...
27. Order fill resolution [enum]: Standard (Fastest)
28. Fill limit orders on t... [bool]: UNCHECKED
29. Slippage [numeric]: 0
30. SEP — Order handling
31. Entries per direction [numeric]: 1
32. Entry handling [enum]: All entries
33. Exit on session close [bool]: CHECKED (checkbox partially under watermark blur — MEDIUM confidence)
34. SEP — Order properties (group header visible; rows below cut off)
35. "template"; "Run" button (under watermark)
Note: still NO "Commission template" row and NO LossLimit parameter as of Feb 11.

## G ENGINE SETTINGS
- Include commission checked ($41.80 / 10 trades = $4.18/trade); Slippage 0; Standard (Fastest); Entries per direction 1; Entry handling All entries; Exit on session close checked; Break at EOD checked.

## H PERFORMANCE (All / Long / Short), 2/9/2025–2/11/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | ($891.80) | $838.28 | ($1,730.08) |
| Gross profit | $3,312.46 | $2,361.64 | $950.82 |
| Gross loss | ($4,204.26) | ($1,523.36) | ($2,680.90) |
| Commission | $41.80 | $16.72 | $25.08 |
| Profit factor | 0.79 | 1.55 | 0.35 |
| Max. drawdown | ($2,860.08) | ($769.18) | ($2,651.72) |
| Sharpe ratio | -3.04 | 4.66 | -3.01 |
| Sortino ratio | -10.07 | 1.00 | -9.98 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.22 | 0.21 | 0.06 |
| Probability | 63.25% | 32.97% | 85.23% |
| Start date | 2/9/2025 | | |
| End date | 2/11/2025 | | |
| Total # of trades | 10 | 4 | 6 |
| Percent profitable | 30.00% | 50.00% | 16.67% |
| # of winning trades | 3 | 2 | 1 |
| # of losing trades | 7 | 2 | 5 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($89.18) | $209.57 | ($288.35) |
| Avg. winning trade | $1,104.15 | $1,180.82 | $950.82 |
| Avg. losing trade | ($600.61) | ($761.68) | ($536.18) |
| Ratio avg. win / avg. loss | 1.84 | 1.55 | 1.77 |
| Max. consec. winners | 2 | 1 | 1 |
| Max. consec. losers | 3 | 1 | 4 |
| Largest winning trade | $1,800.82 | $1,800.82 | $950.82 |
| Largest losing trade | ($1,104.18) | ($769.18) | ($1,104.18) |
| Avg. # of trades per day | 4.83 | 2.90 | 2.90 |
| Avg. time in market | 107.70 min | 136.25 min | 88.67 min |
| Avg. bars in trade | 107.70 | 136.25 | 88.67 |
| Profit per month | ($9,066.63) | $12,783.77 | ($17,589.15) |
| Max. time to recover | 1.89 days | 0.82 days | 1.64 days |
| Longest flat period | 642.00 min | 967.00 min | 1113.00 min |
| Avg. MAE | $574.00 | $522.50 | $608.33 |
| Avg. MFE | $846.00 | $1,242.50 | $581.67 |
| Avg. ETD | $935.18 | $1,032.93 | $870.01 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" (bottom right, over Run/template area) + blurred circular logo over Exit-on-session-close checkbox region.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: Same SolarWindRKSelTime 90/179/5/10/10/1 config re-run for 02/09–02/11/2025: 10 trades, net ($891.80). Order-handling settings now visible: Entries per direction 1, All entries, Exit on session close ON.
- IMPLICATIONS: Confirms the operator's routine: after each trading day/two, backtest the same fixed config over the immediately-past dates (walk-forward verification of live behavior). Exit-on-session-close ON matches campaign's frozen-truth engine assumptions.
- OPEN QUESTIONS: Order properties group contents (cut off); whether Trading hours template is instrument default (CME US Index Futures ETH) or custom.
