# OTRIMG-0016

## A FILE IDENTITY
- id: OTRIMG-0016
- filename: 20260824_171544966_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Tue Feb 18, 10:18 PM (macOS menu bar)
- taskbar_date: 2/18/2025 (Windows taskbar; time obscured by watermark, "10:1? PM" partial — LOW confidence on minutes)
- social_post_date: none visible
- report_start_date: 2/15/2025 (table; settings Start date 02/15/2025)
- report_end_date: 2/18/2025 (table; settings End date 02/18/2025)
- contract_date_clue: Instrument "NQ MAR25"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)", full Settings panel from top. NEW strategy name and NEW "Commission template" row present.

## D STRATEGY IDENTITY
- Strategy dropdown (verbatim, right-clipped): "RKSelTimeDSTMa" (text ends at box edge; almost certainly continues — record as RKSelTimeDSTMa? truncated)
- Machine name "creator".

## E DATA SERIES
- Instrument: NQ MAR25; Price based on: Last; Type: Minute; Value: 1; Tick Replay: unchecked
- Trading hours: "<Use instrumen..." (truncated); Break at EOD: CHECKED

## F PARAMETERS (full Settings panel, top to bottom)
1. SEP — General
2. Backtest type [enum]: Backtest
3. Strategy [enum]: RKSelTimeDSTMa? (right-truncated)
4. SEP — Parameters
5. A1 [numeric]: 90
6. A2 [numeric]: 179
7. A3 [numeric]: 5
8. A4 [numeric]: 10
9. A5 [numeric]: 10
10. Quantity [numeric]: 1
11. LossLimit [numeric]: 2500
12. SEP — Data Series
13. Instrument [enum]: NQ MAR25
14. Price based on [enum]: Last
15. Type [enum]: Minute
16. Value [numeric]: 1
17. Tick Replay [bool]: UNCHECKED
18. SEP — Time frame
19. Start date [date]: 02/15/2025
20. End date [date]: 02/18/2025
21. Trading hours [enum]: <Use instrumen...
22. Break at EOD [bool]: CHECKED
23. SEP — Setup
24. Include commiss... [bool]: UNCHECKED
25. Commission te... [enum]: (blank/greyed dropdown — disabled because commission unchecked)
26. Maximum bars l... [enum]: 256
27. Bars required to... [numeric]: 20
28. "template"; "Run" button (under watermark)
- NOTE: parameter order here is Quantity THEN LossLimit (=2500); on Feb 13 (OTRIMG-0014) it was LossLimit (=4000) THEN Quantity. LossLimit value changed 4000 → 2500.
- FIRST frame where a "Commission template" row exists in Setup → NinjaTrader was updated (8.1.2+ layout) or panel differs, between Feb 11 and Feb 18.

## G ENGINE SETTINGS
- Include commission: UNCHECKED (Commission row in results = $0.00; PnL values are round to $5: $95.00, ($910.00)).

## H PERFORMANCE (All / Long / Short), 2/15/2025–2/18/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | ($2,555.00) | ($910.00) | ($1,645.00) |
| Gross profit | $95.00 | $0.00 | $95.00 |
| Gross loss | ($2,650.00) | ($910.00) | ($1,740.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.04 | 0.00 | 0.05 |
| Max. drawdown | ($2,650.00) | ($910.00) | ($1,740.00) |
| Sharpe ratio | -4.42 | -8.92 | -4.48 |
| Sortino ratio | -14.64 | -29.60 | -14.85 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.86 | 0.00 | 0.65 |
| Probability | 97.99% | 0.00% | 93.73% |
| Start date | 2/15/2025 | | |
| End date | 2/18/2025 | | |
| Total # of trades | 4 | 1 | 3 |
| Percent profitable | 25.00% | 0.00% | 33.33% |
| # of winning trades | 1 | 0 | 1 |
| # of losing trades | 3 | 1 | 2 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($638.75) | ($910.00) | ($548.33) |
| Avg. winning trade | $95.00 | $0.00 | $95.00 |
| Avg. losing trade | ($883.33) | ($910.00) | ($870.00) |
| Ratio avg. win / avg. loss | 0.11 | 0.00 | 0.11 |
| Max. consec. winners | 1 | 0 | 1 |
| Max. consec. losers | 3 | 1 | 2 |
| Largest winning trade | $95.00 | $0.00 | $95.00 |
| Largest losing trade | ($910.00) | ($910.00) | ($910.00) |
| Avg. # of trades per day | 2.90 | 1.45 | 2.17 |
| Avg. time in market | 114.75 min | 30.00 min | 143.00 min |
| Avg. bars in trade | 114.75 | 30.00 | 143.00 |
| Profit per month | ($38,963.75) | ($27,755.00) | ($25,086.25) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" + blurred circular stamp over Run button.
- Windows 11 taskbar: Start, Search (with small avatar icons), mail, File Explorer, Edge, NinjaTrader (active), Visual Studio Code icon (blue), Chrome, notepad; tray: ENG, network/volume/battery, 2/18/2025. VS CODE PRESENCE = development environment on the remote machine.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: New strategy class visible: "RKSelTimeDSTMa…" (truncated) with LossLimit=2500, commission excluded, backtest over the 2/15-2/18 holiday-shortened window: 4 trades, ($2,555.00). The $910.00 repeated largest-loss = 45.5 NQ points, consistent with a fixed stop distance at zero commission.
- IMPLICATIONS: Name fragment "DSTMa" strongly suggests a Daylight-Saving-Time-aware variant ("DST" + "Ma…" possibly "Max"/"Managed"/"Martingale"?) — HYPOTHESIS; DST handling matters for a 04:00-16:00 SelTime window. Iteration cadence (SolarWindRK → SolarWindRKSelTime → +LossLimit → RKSelTimeDSTMa…) tracks the trader's February 2025 development arc. VS Code on taskbar + NT panel layout change (Commission template row) between Feb 11 and Feb 18 = active NinjaScript development and possible NT update in that window.
- OPEN QUESTIONS: full strategy class name; whether LossLimit 2500 vs 4000 was tuning or per-variant default; why commission was toggled off for this run.
