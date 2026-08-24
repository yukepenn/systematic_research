# OTRIMG-0037

## A FILE IDENTITY
- id: OTRIMG-0037
- filename: 20260824_171725742_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Mar 7 (macOS menu bar) — year not shown; time 11:07 PM
- taskbar_date: 3/7/2025 (Windows taskbar; time obscured by watermark)
- social_post_date: none visible
- report_start_date: 3/6/2025
- report_end_date: 3/7/2025
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop ("creator"), NT8 Strategy Analyzer "Summary ($)", 2-day losing window 3/6–3/7/2025, commission excluded.

## D STRATEGY IDENTITY
- No strategy name visible.
- Settings strip TOP shows two CHECKED checkboxes above the first group separator — i.e., the last two strategy parameters in view are booleans set to true (different from the numeric tail A4/A5/Quantity seen in OTRIMG-0024). See F.

## E DATA SERIES
- Not directly readable; PnL in round dollars (multiples of $5), NQ-consistent.

## F PARAMETERS (Settings strip, top to bottom, right halves only)
1. [bool] CHECKED (topmost, strategy parameter)
2. [bool] CHECKED (strategy parameter)
3. SEP — group triangle
4. [unknown] blank/empty box (Instrument position)
5. [dropdown] "v"
6. [dropdown] ". v"
7. [numeric] 1
8. [bool] unchecked
9. SEP — group triangle
10. [dropdown w/ calendar icon] "v"
11. [dropdown w/ calendar icon] "v"
12. [dropdown] "v"
13. [bool] checked
14. SEP — group triangle
15. [bool] checked
16. [dropdown] "v"
17. [numeric] 20
18. SEP — group triangle
19. [dropdown] "v"
20. [bool] unchecked
21. [numeric] 0
22. SEP — group triangle
23. [numeric] 1
24. [dropdown] "v"
25. [bool] checked
26. SEP — group triangle
27. [dropdown] "v"
28. Text "template"; Run button (watermarked)
INFERRED mapping: 4–8 Data Series; 10–13 Time frame; 15–17 Setup (one dropdown row possibly unresolved, cf. OTRIMG-0035); 19–21 Historical fill; 23–25 Order handling; 27 trailing group (only one dropdown visible this time).

## G ENGINE SETTINGS
- Commission $0.00 all columns (excluded). Slippage 0.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($2,280.00) | ($4,180.00) | $1,900.00 |
| Gross profit | $17,990.00 | $6,385.00 | $11,605.00 |
| Gross loss | ($20,270.00) | ($10,565.00) | ($9,705.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.89 | 0.60 | 1.20 |
| Max. drawdown | ($12,290.00) | ($7,130.00) | ($5,370.00) |
| Sharpe ratio | -2.99 | -4.28 | 3.13 |
| Sortino ratio | -9.91 | -14.19 | 1.00 |
| Ulcer index | 0.02 | 0.01 | 0.01 |
| R squared | 0.31 | 0.27 | 0.13 |
| Probability | 62.36% | 85.09% | 37.04% |
| Start date | 3/6/2025 | | |
| End date | 3/7/2025 | | |
| Total # of trades | 47 | 23 | 24 |
| Percent profitable | 27.66% | 21.74% | 33.33% |
| # of winning trades | 13 | 5 | 8 |
| # of losing trades | 34 | 18 | 16 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($48.51) | ($181.74) | $79.17 |
| Avg. winning trade | $1,383.85 | $1,277.00 | $1,450.63 |
| Avg. losing trade | ($596.18) | ($586.94) | ($606.56) |
| Ratio avg. win / avg. loss | 2.32 | 2.18 | 2.39 |
| Max. consec. winners | 2 | 1 | 2 |
| Max. consec. losers | 8 | 7 | 6 |
| Largest winning trade | $3,430.00 | $2,025.00 | $3,430.00 |
| Largest losing trade | ($1,495.00) | ($1,025.00) | ($1,495.00) |
| Avg. # of trades per day | 22.69 | 16.66 | 11.59 |
| Avg. time in market | 31.11 min | 20.50 min | 41.27 min |
| Avg. bars in trade | 31.11 | 20.52 | 41.25 |
| Profit per month | ($23,180.00) | ($63,745.00) | $19,316.67 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a — watermark only: "rednote ID: 1384856832".

## K FORENSIC INTERPRETATION
- Direct facts: second documented losing window (net −$2,280 gross of commission; 3/6–3/7/2025, a high-volatility tariff-news period). Captured Fri Mar 7 11:07 PM. Longs badly negative (PF 0.60), shorts positive (PF 1.20).
- The two checked boolean strategy parameters at the strip top are a NEW parameter-tail signature vs OTRIMG-0024 (numeric A4/A5/Quantity tail) — suggests either a different strategy variant or a scrolled pane showing bool params that sit between the numerics and Data Series.
- Honest-loss documentation again — trader records bad days too (supports authenticity of the series).
- Avg. bars ≈ avg. minutes (31.11/31.11) → 1-minute bars.
