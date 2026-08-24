# OTRIMG-0035

## A FILE IDENTITY
- id: OTRIMG-0035
- filename: 20260824_171718599_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Wed Mar 5 (macOS menu bar) — year not shown; time 7:20 PM
- taskbar_date: 3/5/2025 (Windows taskbar; time obscured by watermark)
- social_post_date: none visible
- report_start_date: 3/4/2025
- report_end_date: 3/5/2025
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop ("creator"), NT8 Strategy Analyzer "Summary ($)", 2-day window 3/4–3/5/2025, 70 trades, commission excluded.

## D STRATEGY IDENTITY
- No strategy name visible.

## E DATA SERIES
- Not directly readable. PnL totals are round dollars (multiples of $5), commission $0.00 → commission excluded; NQ-consistent tick math.

## F PARAMETERS (Settings strip, top to bottom, right halves only)
1. [numeric] 1 (topmost, partially clipped at pane top)
2. SEP — group triangle
3. [unknown] blank/empty box
4. [dropdown] "v"
5. [dropdown] ". v"
6. [numeric] 1
7. [bool] unchecked
8. SEP — group triangle
9. [dropdown w/ calendar icon] "v"
10. [dropdown w/ calendar icon] "v"
11. [dropdown] "v"
12. [bool] checked
13. SEP — group triangle
14. [bool] checked
15. [dropdown] "v" (only ONE dropdown visible here between the checkbox and "20" — vs two in OTRIMG-0024's full pane; possible greyed/disabled template dropdown not resolved at this resolution; confidence LOW)
16. [numeric] 20
17. SEP — group triangle
18. [dropdown] "v"
19. [bool] unchecked
20. [numeric] 0
21. SEP — group triangle
22. [numeric] 1
23. [dropdown] "v"
24. [bool] checked
25. SEP — group triangle
26. [dropdown] "v"
27. [dropdown] "v"
28. Text "template"; Run button (watermarked)
INFERRED mapping as before: 3–7 Data Series; 9–12 Time frame; 14–16 Setup; 18–20 Historical fill; 22–24 Order handling; 26–27 the recurring unexplained trailing dropdown pair.

## G ENGINE SETTINGS
- Commission $0.00 in all columns despite a checked box in the Setup-group position — either Include commission is OFF (and I misaligned rows) or a zero-rate template is selected. Confidence LOW; contrast with OTRIMG-0029 where the unchecked box + greyed template was clearly visible.
- Slippage 0.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $1,130.00 | $3,300.00 | ($2,170.00) |
| Gross profit | $33,025.00 | $19,485.00 | $13,540.00 |
| Gross loss | ($31,895.00) | ($16,185.00) | ($15,710.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.04 | 1.20 | 0.86 |
| Max. drawdown | ($13,000.00) | ($8,160.00) | ($7,145.00) |
| Sharpe ratio | 3.10 | 3.18 | -2.99 |
| Sortino ratio | 1.00 | 1.00 | -9.91 |
| Ulcer index | 0.02 | 0.01 | 0.01 |
| R squared | 0.23 | 0.39 | 0.03 |
| Probability | 45.75% | 33.05% | 61.90% |
| Start date | 3/4/2025 | | |
| End date | 3/5/2025 | | |
| Total # of trades | 70 | 37 | 33 |
| Percent profitable | 38.57% | 40.54% | 36.36% |
| # of winning trades | 27 | 15 | 12 |
| # of losing trades | 43 | 22 | 21 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $16.14 | $89.19 | ($65.76) |
| Avg. winning trade | $1,223.15 | $1,299.00 | $1,128.33 |
| Avg. losing trade | ($741.74) | ($735.68) | ($748.10) |
| Ratio avg. win / avg. loss | 1.65 | 1.77 | 1.51 |
| Max. consec. winners | 8 | 5 | 4 |
| Max. consec. losers | 6 | 11 | 4 |
| Largest winning trade | $5,655.00 | $3,740.00 | $5,655.00 |
| Largest losing trade | ($2,440.00) | ($1,250.00) | ($2,440.00) |
| Avg. # of trades per day | 33.80 | 17.86 | 15.93 |
| Avg. time in market | 31.77 min | 33.41 min | 29.94 min |
| Avg. bars in trade | 31.77 | 33.41 | 29.94 |
| Profit per month | $11,488.33 | $33,550.00 | ($22,061.67) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a — watermark only: "rednote ID: 1384856832".

## K FORENSIC INTERPRETATION
- Direct facts: near-breakeven 2-day run (net +$1,130 before commission, PF 1.04, 70 trades) on 3/4–3/5/2025, a high-volatility period; # of winning trades check: 27×$1,223.15 ≈ $33,025 ✓. Captured evening of last report day (pattern continues).
- Anomaly note: Long max consec losers 11 > All max consec losers 6 — an NT8 column quirk (long-only sequence vs interleaved all-trade sequence), not a transcription error.
- Trade frequency ~34/day is between OTRIMG-0029's ~21/day and OTRIMG-0026's 90/day — parameters or filters were being varied across days.
- Commission excluded here ($0.00), included on other days ($5.68/trade) — the trader toggles commission inclusion between runs.
- Open question: exact Setup-group row alignment in the strip (see F item 15).
