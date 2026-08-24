# OTRIMG-0029

## A FILE IDENTITY
- id: OTRIMG-0029
- filename: 20260824_171658660_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Feb 28 (macOS menu bar) — year not shown; time 6:50 PM
- taskbar_date: 2/28/2025 (Windows taskbar bottom right; time obscured by watermark)
- social_post_date: none visible
- report_start_date: 2/28/2025
- report_end_date: 2/28/2025 (single-day report)
- contract_date_clue: none visible (instrument box cropped/blank in settings strip)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop ("creator"), NinjaTrader 8 Strategy Analyzer "Summary ($)", single-day LOSING report; Settings pane partially visible showing the numeric parameter stack.

## D STRATEGY IDENTITY
- No strategy name visible. Parameter value stack visible (see F).

## E DATA SERIES
- Instrument box in settings strip appears blank/cropped (unreadable). No instrument text elsewhere.
- PnL granularity: all top-line totals are multiples of $5 (e.g. $2,830.00, $12,285.00, $1,130.00, $1,750.00) — consistent with NQ ($5 per 0.25 tick).

## F PARAMETERS (Settings strip, top to bottom; left halves cropped)
1. SEP — group triangle (label cropped)
2. [dropdown] "v" (value cropped)
3. [dropdown] "v" (value cropped)
4. SEP — group triangle (label cropped)
5. [numeric] 90
6. [numeric] 179 (last digit partly at box edge; read as 179, confidence MEDIUM)
7. [numeric] 5
8. [numeric] 10
9. [numeric] 10
10. [numeric] 1
11. SEP — group triangle
12. [unknown] blank/empty box (likely Instrument, value cropped)
13. [dropdown] "v"
14. [dropdown] ". v"
15. [numeric] 1
16. [bool] unchecked
17. SEP — group triangle
18. [dropdown w/ calendar icon] "v"
19. [dropdown w/ calendar icon] "v"
20. [dropdown] "v"
21. [bool] checked
22. SEP — group triangle
23. [bool] UNCHECKED
24. [dropdown, GREYED/disabled] "v"
25. [dropdown] "v"
26. [numeric] 20
27. SEP — group triangle
28. Text "template"
29. Run button (covered partly by red watermark)
INFERRED mapping (reason: layout matches OTRIMG-0024 full pane): 5–10 = strategy numeric params + Quantity → params ≈ 90 / 179 / 5 / 10 / 10, Quantity 1; 12–16 = Data Series (Value=1 Minute, Tick Replay unchecked); 18–21 = Time frame (Break at EOD checked); 23–26 = Setup: Include commission UNCHECKED with Commission template DISABLED (explains Commission $0.00), Max bars look back, Bars required to trade 20.

## G ENGINE SETTINGS
- Commission $0.00 in all columns; settings strip shows an unchecked checkbox followed by a greyed dropdown = Include commission OFF (INFERRED, high confidence).
- Slippage row "Total slippage 0".

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($9,455.00) | ($4,855.00) | ($4,600.00) |
| Gross profit | $2,830.00 | $995.00 | $1,835.00 |
| Gross loss | ($12,285.00) | ($5,850.00) | ($6,435.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.23 | 0.17 | 0.29 |
| Max. drawdown | ($9,455.00) | ($4,855.00) | ($5,030.00) |
| Sharpe ratio | -3.92 | -4.23 | -4.25 |
| Sortino ratio | -13.02 | -14.04 | -14.10 |
| Ulcer index | 0.01 | 0.01 | 0.01 |
| R squared | 0.92 | 0.90 | 0.80 |
| Probability | 99.65% | 98.58% | 96.03% |
| Start date | 2/28/2025 | | |
| End date | 2/28/2025 | | |
| Total # of trades | 21 | 10 | 11 |
| Percent profitable | 38.10% | 40.00% | 36.36% |
| # of winning trades | 8 | 4 | 4 |
| # of losing trades | 13 | 6 | 7 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($450.24) | ($485.50) | ($418.18) |
| Avg. winning trade | $353.75 | $248.75 | $458.75 |
| Avg. losing trade | ($945.00) | ($975.00) | ($919.29) |
| Ratio avg. win / avg. loss | 0.37 | 0.26 | 0.50 |
| Max. consec. winners | 3 | 2 | 2 |
| Max. consec. losers | 5 | 2 | 5 |
| Largest winning trade | $1,130.00 | $760.00 | $1,130.00 |
| Largest losing trade | ($1,750.00) | ($1,370.00) | ($1,750.00) |
| Avg. # of trades per day | 15.21 | 7.24 | 7.97 |
| Avg. time in market | 19.62 min | 9.20 min | 29.09 min |
| Avg. bars in trade | 19.62 | 9.20 | 29.09 |
| Profit per month | ($144,188.75) | ($74,038.75) | ($70,150.00) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a — watermark only: "rednote ID: 1384856832".

## K FORENSIC INTERPRETATION
- Direct facts: single-day backtest of 2/28/2025 showing a heavy LOSS (−$9,455, PF 0.23, 21 trades), captured that evening (Fri Feb 28 6:50 PM). Commission excluded ($0.00; Include-commission checkbox unchecked, template greyed).
- KEY: the visible numeric parameter stack reads 90 / 179 / 5 / 10 / 10 (+ Quantity 1). This matches the known Solar Wave baseline parameter set "90/179/5/10/true/10" (SolarWaveRKReplicaV0 Type 1) — strong evidence the original trader's strategy is the same parameter family. (Hypothesis label: PARAMETER-MATCH; the "true" bool is not visible in this crop.)
- Avg time in market 19.62 min here vs 81.39 min in OTRIMG-0024 — different behavior; either different params or different market day/regime.
- This is honest-loss evidence: the trader kept/captured a losing day; useful for reconstructing true out-of-sample behavior.
- Open question: whether the 2 dropdowns above the numeric stack (items 2–3) are strategy enum/bool params (e.g. the "true" flag rendered as dropdown) — not readable here.
