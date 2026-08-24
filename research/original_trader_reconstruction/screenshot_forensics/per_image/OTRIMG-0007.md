# OTRIMG-0007

## A FILE IDENTITY
- id: OTRIMG-0007
- filename: 20260824_171511211_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Wed Feb 5, 8:43 PM (macOS menu bar)
- taskbar_date: 8:43 PM 2/5/2025 (Windows taskbar; time partially under watermark blur — MEDIUM confidence, date 2/5/2025 clear)
- social_post_date: none visible
- report_start_date: 2/4/2025 (table row; settings Start date 02/04/2025)
- report_end_date: 2/5/2025 (table row; settings End date 02/05/2025)
- contract_date_clue: Instrument "NQ MAR25" (settings panel)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer, Display "Summary ($)", with FULL Settings panel expanded on right (highest-value frame: complete parameter names/values legible).

## D STRATEGY IDENTITY
- Strategy dropdown (verbatim): "SolarWindRKSelTime" (right edge of text at box border; possibly further characters clipped — visible text exactly "SolarWindRKSelTime")
- Machine name: "creator". Bottom tab "Analyzer" (+).

## E DATA SERIES
- Instrument: NQ MAR25
- Price based on: Last
- Type: Minute
- Value: 1
- Tick Replay: unchecked
- Trading hours: "<Use instrument se..." (truncated dropdown text)
- Break at EOD: checked

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
18. Start date [date]: 02/04/2025
19. End date [date]: 02/05/2025
20. Trading hours [enum]: <Use instrument se...
21. Break at EOD [bool]: CHECKED
22. SEP — Setup
23. Include commission [bool]: CHECKED
24. Maximum bars look... [enum]: 256
25. Bars required to trade [numeric]: 20
26. SEP — Historical fill proces...
27. Order fill resolution [enum]: Standard (Fastest)
28. "template" link; "Run" button
Note: NO "Commission template" row in Setup group (contrast with OTRIMG-0016/0018/0022 — panel layout changed later in February). NO LossLimit parameter (contrast with OTRIMG-0014/0016).

## G ENGINE SETTINGS
- Include commission: checked (commission $125.40 on 30 trades = $4.18/trade)
- Order fill resolution: Standard (Fastest); Tick Replay off; Break at EOD on; slippage row = 0.

## H PERFORMANCE (All / Long / Short), 2/4/2025–2/5/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | ($3,805.40) | $1,722.30 | ($5,527.70) |
| Gross profit | $9,564.84 | $6,965.74 | $2,599.10 |
| Gross loss | ($13,370.24) | ($5,243.44) | ($8,126.80) |
| Commission | $125.40 | $62.70 | $62.70 |
| Profit factor | 0.72 | 1.33 | 0.32 |
| Max. drawdown | ($5,587.86) | ($3,760.08) | ($5,527.70) |
| Sharpe ratio | -2.94 | 3.12 | -2.89 |
| Sortino ratio | -9.76 | 1.00 | -9.59 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.76 | 0.00 | 0.75 |
| Probability | 77.77% | 32.95% | 97.96% |
| Start date | 2/4/2025 | | |
| End date | 2/5/2025 | | |
| Total # of trades | 30 | 15 | 15 |
| Percent profitable | 40.00% | 46.67% | 33.33% |
| # of winning trades | 12 | 7 | 5 |
| # of losing trades | 18 | 8 | 10 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($126.85) | $114.82 | ($368.51) |
| Avg. winning trade | $797.07 | $995.11 | $519.82 |
| Avg. losing trade | ($742.79) | ($655.43) | ($812.68) |
| Ratio avg. win / avg. loss | 1.07 | 1.52 | 0.64 |
| Max. consec. winners | 2 | 3 | 3 |
| Max. consec. losers | 3 | 3 | 4 |
| Largest winning trade | $3,255.82 | $3,255.82 | $885.82 |
| Largest losing trade | ($1,024.18) | ($1,004.18) | ($1,024.18) |
| Avg. # of trades per day | 14.48 | 7.24 | 7.24 |
| Avg. time in market | 69.50 min | 69.60 min | 69.40 min |
| Avg. bars in trade | 69.50 | 69.60 | 69.40 |
| Profit per month | ($38,688.23) | $17,510.05 | ($56,198.28) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" + blurred circular logo over Run button area.
- Background window fragments (bottom, behind NT): ChatGPT UI — "Unlimited access, team..." (left) and "ChatGPT can make mistakes. Check important info." (center); "?" help bubble right. Below screen edge: spreadsheet-like fragments "Formula SUM Formula SUM M2-M233" (verbatim as visible; LOW confidence on "M2-M233") and right side "Height 20 pt", "Fit".

## K FORENSIC INTERPRETATION
- DIRECT FACTS: THE decisive settings frame — strategy "SolarWindRKSelTime", parameters A1=90 A2=179 A3=5 A4=10 A5=10 Quantity=1, NQ MAR25, 1-Minute Last, no Tick Replay, Include commission on, Standard (Fastest) fill, Break at EOD on, backtest 02/04→02/05/2025 losing ($3,805.40) over 30 trades.
- IMPLICATIONS: Generic parameter labels "A1..A5" indicate an obfuscated/renamed strategy export. The 90/179/5/10/10 stack matches the campaign's Solar Wave family (90/179/5/10/true/10) — direct corroboration that the original trader's strategy is the same family as OTR-S-CAND1 ("SelTime" in the name supports the SelTime 04:00-16:00 hypothesis). Two-day live-window backtest right after trading days suggests daily verification habit.
- OPEN QUESTIONS: Whether the Strategy dropdown text is clipped (could be "SolarWindRKSelTime..." with more chars); which trading-hours template underlies "<Use instrument se..."; whether the A-parameters map 1:1 to the known 90/179/5/10/10 semantic order.
