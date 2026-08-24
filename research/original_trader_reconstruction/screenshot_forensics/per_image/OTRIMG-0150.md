# OTRIMG-0150

## A FILE IDENTITY
- id: OTRIMG-0150
- filename: 20260824_173108291_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Jun 5, 8:19 PM (macOS menu bar; year not shown)
- taskbar_date: 8:19 PM / 6/5/2026 (Windows taskbar bottom right, partially obscured)
- social_post_date: none visible
- report_start_date: 5/31/2026
- report_end_date: 6/5/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop to "dev", NinjaTrader 8 Strategy Analyzer Summary ($), Settings pane cropped at right edge but with a DIFFERENT (larger) parameter stack than OTRIMG-0142/0148.

## D STRATEGY IDENTITY
- No strategy name visible. Machine "dev". Tab "Analyzer" + "+". "template" label above Run.

## E DATA SERIES
- Not visible. Avg time in market 49.06 min ≈ avg bars in trade 49.05 → 1-minute bars INFERRED.

## F PARAMETERS (right-edge cropped Settings stack, top to bottom — NOTE: different template than 0142/0148)
1. [numeric] "30"
2. [numeric] "70"
3. [numeric] "2"
4. [numeric] "20"
5. SEP (triangle + "...")
6. [bool] checkbox UNCHECKED
7. [bool] checkbox CHECKED
8. [bool] checkbox CHECKED
9. [bool] checkbox CHECKED
10. [numeric] "14"
11. [numeric] "6"
12. [bool] checkbox CHECKED
13. [numeric] "30"
14. [numeric] "16"
15. [numeric] "0"
16. SEP (triangle + "...")
17. [numeric] "3"
18. [numeric] "0"
19. [numeric] "12"
20. [numeric] "0"
21. SEP (triangle + "...")
22. [bool] checkbox CHECKED
23. [bool] checkbox UNCHECKED
24. [bool] checkbox CHECKED
25. [bool] checkbox CHECKED
26. [bool] checkbox UNCHECKED
27. [numeric] "5"
28. [bool] checkbox CHECKED
29. label "template"; [button] "Run"
- The stack begins mid-group (rows above "30" scrolled out of view). Group sizes visible: [≥4 numerics] / [10 rows: 4 bools + 14,6 + bool + 30,16,0] / [4 numerics: 3,0,12,0] / [≥7 rows: bools + 5 + bool].

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0. No engine-settings labels visible.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $14,540.00 | ($1,315.00) | $15,855.00 |
| Gross profit | $49,750.00 | $16,790.00 | $32,960.00 |
| Gross loss | ($35,210.00) | ($18,105.00) | ($17,105.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.41 | 0.93 | 1.93 |
| Max. drawdown | ($13,130.00) | ($9,705.00) | ($7,105.00) |
| Sharpe ratio | 4.34 | 4.48 | 1.89 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.01 |
| R squared | 0.00 | 0.06 | 0.00 |
| Probability | 10.53% | 57.27% | 4.41% |
| Start date | 5/31/2026 | | |
| End date | 6/5/2026 | | |
| Total # of trades | 82 | 36 | 46 |
| Percent profitable | 39.02% | 33.33% | 43.48% |
| # of winning trades | 32 | 12 | 20 |
| # of losing trades | 50 | 24 | 26 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $177.32 | ($36.53) | $344.67 |
| Avg. winning trade | $1,554.69 | $1,399.17 | $1,648.00 |
| Avg. losing trade | ($704.20) | ($754.38) | ($657.88) |
| Ratio avg. win / avg. loss | 2.21 | 1.85 | 2.50 |
| Max. consec. winners | 4 | 3 | 4 |
| Max. consec. losers | 7 | 7 | 4 |
| Largest winning trade | $8,410.00 | $3,265.00 | $8,410.00 |
| Largest losing trade | ($1,890.00) | ($1,890.00) | ($1,790.00) |
| Avg. # of trades per day | 19.79 | 8.69 | 13.33 |
| Avg. time in market | 49.06 min | 64.19 min | 37.22 min |
| Avg. bars in trade | 49.05 | 64.19 | 37.20 |
| Profit per month | $73,911.67 | ($6,684.58) | $96,715.50 |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: week 5/31–6/5/2026 net +$14,540 on 82 trades (PF 1.41), and this time SHORTS carried the profit (+$15,855, PF 1.93) while longs lost — the long/short dominance FLIPPED vs prior weeks (0142/0146: long-dominant; 0148: long-dominant).
- The settings stack (30/70/2/20, many checkboxes, 14, 6, 30, 16, 0, 3, 0, 12, 0, ..., 5) does NOT match the 0142/0148 stack nor the 13-parameter VWAP template of 0146 → a different (or heavily extended) strategy version was being tested by early June 2026. "30/70" smells like RSI-style overbought/oversold thresholds (hypothesis only).
- Same-week review habit: screenshot Fri Jun 5 8:19 PM = report end date.
- Machine "dev" again. Watermark "rednote ID: 13?4856832" (digits partially blocked by dock icons; "rednote" clearly legible). macOS dock: Calendar shows JUN 5; a new black camera/photo-booth style icon appears; Chrome badge visible.
- Largest loss −$1,890 (differs from earlier −$2,600 cap) → stop distance may have changed or volatility differed (open question).
- Open questions: strategy name; mapping of the numeric stack to labels; whether this is an evolution of the VWAP strategy or a separate system.
