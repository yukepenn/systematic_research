# OTRIMG-0014

## A FILE IDENTITY
- id: OTRIMG-0014
- filename: 20260824_171539028_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Thu Feb 13, 6:48 PM (macOS menu bar)
- taskbar_date: 2/13/2025 (Windows taskbar; time obscured by watermark, "6:4? PM" partially visible — LOW confidence on minutes)
- social_post_date: none visible
- report_start_date: 2/12/2025 (table; settings Start date 02/12/2025)
- report_end_date: 2/13/2025 (table; settings End date 02/13/2025)
- contract_date_clue: Instrument "NQ MAR25"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)", full Settings panel SCROLLED DOWN (General/Strategy row scrolled out; panel starts at A2). NEW parameter "LossLimit" visible.

## D STRATEGY IDENTITY
- Strategy name NOT visible (panel scrolled past the General group). Machine name "creator".

## E DATA SERIES
- Instrument: NQ MAR25; Price based on: Last; Type: Minute; Value: 1; Tick Replay: unchecked
- Trading hours: "<Use instrument se..."; Break at EOD: UNCHECKED (checkbox empty in this frame — differs from other frames; MEDIUM-HIGH confidence it is unchecked)

## F PARAMETERS (Settings panel as scrolled, top to bottom)
1. A2 [numeric]: 179
2. A3 [numeric]: 5
3. A4 [numeric]: 10
4. A5 [numeric]: 10
5. LossLimit [numeric]: 4000
6. Quantity [numeric]: 1
7. SEP — Data Series
8. Instrument [enum]: NQ MAR25
9. Price based on [enum]: Last
10. Type [enum]: Minute
11. Value [numeric]: 1
12. Tick Replay [bool]: UNCHECKED
13. SEP — Time frame
14. Start date [date]: 02/12/2025
15. End date [date]: 02/13/2025
16. Trading hours [enum]: <Use instrument se...
17. Break at EOD [bool]: UNCHECKED
18. SEP — Setup
19. Include commission [bool]: CHECKED
20. Maximum bars look... [enum]: 256
21. Bars required to trade [numeric]: 20
22. SEP — Historical fill proces...
23. Order fill resolution [enum]: Standard (Fastest)
24. Fill limit orders on t... [bool]: UNCHECKED
25. Slippage [numeric]: 0
26. SEP — Order handling
27. Entries per direction [numeric]: 1
28. (next row label "Entry handling"-like, cut off at panel bottom; value box partially visible "All..?" — cropped)
29. "template"; "Run" button (under watermark)
- A1 presumed above scroll (not visible). NEW: LossLimit = 4000 sits between A5 and Quantity.
- Still NO "Commission template" row in Setup as of Feb 13.

## G ENGINE SETTINGS
- Include commission checked ($83.60 / 20 trades = $4.18/trade); Slippage 0; Standard (Fastest); Break at EOD unchecked (this frame).

## H PERFORMANCE (All / Long / Short), 2/12/2025–2/13/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | $5,956.40 | $6,264.02 | ($307.62) |
| Gross profit | $10,725.66 | $8,506.56 | $2,219.10 |
| Gross loss | ($4,769.26) | ($2,242.54) | ($2,526.72) |
| Commission | $83.60 | $45.98 | $37.62 |
| Profit factor | 2.25 | 3.79 | 0.88 |
| Max. drawdown | ($1,463.36) | ($929.18) | ($1,401.72) |
| Sharpe ratio | 5.08 | 5.10 | -4.57 |
| Sortino ratio | 1.00 | 1.00 | -15.17 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.87 | 0.89 | 0.14 |
| Probability | 7.55% | 3.19% | 56.56% |
| Start date | 2/12/2025 | | |
| End date | 2/13/2025 | | |
| Total # of trades | 20 | 11 | 9 |
| Percent profitable | 65.00% | 72.73% | 55.56% |
| # of winning trades | 13 | 8 | 5 |
| # of losing trades | 7 | 3 | 4 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $297.82 | $569.46 | ($34.18) |
| Avg. winning trade | $825.05 | $1,063.32 | $443.82 |
| Avg. losing trade | ($681.32) | ($747.51) | ($631.68) |
| Ratio avg. win / avg. loss | 1.21 | 1.42 | 0.70 |
| Max. consec. winners | 4 | 4 | 2 |
| Max. consec. losers | 2 | 1 | 2 |
| Largest winning trade | $2,510.82 | $2,510.82 | $1,375.82 |
| Largest losing trade | ($1,074.18) | ($929.18) | ($1,074.18) |
| Avg. # of trades per day | 14.48 | 7.97 | 6.52 |
| Avg. time in market | 57.05 min | 66.36 min | 45.67 min |
| Avg. bars in trade | 57.05 | 66.36 | 45.67 |
| Profit per month | $90,835.10 | $95,526.31 | ($4,691.21) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" bottom right + blurred circular stamp over Run button.
- Windows 11 taskbar visible: Start, Search box with seasonal icon, widgets/apps: mail, File Explorer, NinjaTrader (orange N, active), Edge, calculator-like icon, media icon, Chrome, Excel, green-circle app, stacked-windows icon, gear (Settings), another utility, notepad; tray: hidden-icons chevron, network/volume/battery cluster, ENG language indicator, date 2/13/2025.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: By Feb 13 the strategy grew a NEW "LossLimit" parameter set to 4000; window 2/12-2/13 produced +$5,956.40 over 20 trades. Break at EOD unchecked in this frame.
- IMPLICATIONS: Active development iteration mid-February: the trader added a dollar loss-limit (4000) to the SelTime variant after the losing 2/9-2/11 stretch — HYPOTHESIS on motivation, parameter presence is fact. LossLimit position (between A5 and Quantity) differs from OTRIMG-0016 ordering (Quantity then LossLimit) — suggests a differently compiled/named class between the two dates.
- OPEN QUESTIONS: strategy class name for this run (scrolled out); A1 value (presumed 90, not visible); whether LossLimit is per-day or per-position; why Break at EOD is off here.
