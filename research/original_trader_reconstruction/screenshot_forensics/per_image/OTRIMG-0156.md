# OTRIMG-0156

## A FILE IDENTITY
- id: OTRIMG-0156
- filename: 20260824_173126628_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Jun 26, 7:39 PM (macOS menu bar; year not shown)
- taskbar_date: 7:39 PM / 6/26/2026 (Windows taskbar bottom right, partially obscured by watermark)
- social_post_date: none visible
- report_start_date: 6/21/2026
- report_end_date: 6/26/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop to "hp", NinjaTrader 8 Strategy Analyzer Summary ($), Settings pane cropped at right edge (same template as 0142/0148 but scrolled two rows higher, exposing values 3/10/5 at top).

## D STRATEGY IDENTITY
- No strategy name visible. Machine "hp". Tab "Analyzer" + "+". "template" label above Run.

## E DATA SERIES
- Not directly visible. Avg time in market 39.97 min == avg bars in trade 39.97 → 1-minute bars INFERRED.

## F PARAMETERS (right-edge cropped Settings stack, top to bottom)
1. [numeric] "3" (top box partially cut by header; digit legible as 3, MEDIUM confidence)
2. [numeric] "10"
3. [numeric] "5"
4. SEP (triangle + "...")
5. [unknown] empty-looking grayed box (cropped; likely Instrument cell — INFERRED)
6. [dropdown] "v"
7. [dropdown] "v"
8. [numeric] "1"
9. SEP (triangle + "...")
10. [date/dropdown] picker glyph "⋮v"
11. [date/dropdown] picker glyph "⋮v"
12. [dropdown] "v"
13. [bool] checkbox CHECKED
14. SEP (triangle + "...")
15. [bool] checkbox UNCHECKED
16. [dropdown] grayed/disabled "v"
17. [dropdown] "v"
18. [numeric] "20"
19. SEP (triangle + "...")
20. [dropdown] "v"
21. [bool] checkbox UNCHECKED
22. [numeric] "0"
23. SEP (triangle + "...")
24. [numeric] "2"
25. [dropdown] "v"
26. [bool] checkbox CHECKED
27. SEP (triangle + "...")
28. [unknown] wide grayed box with horizontal line (cropped)
29. label "template"; [button] "Run"
- ALIGNMENT NOTE (hypothesis, labeled): top values 3 / 10 / 5 match OTRIMG-0146's last three strategy parameters (Signal Quantity Per Trend=3, Signal Close Threshold (%)=10, Signal Split (Bars)=5), and the following groups match Data Series (Instrument/Price based on/Type/Value=1) and Time frame (Start/End/Trading hours/Break at EOD=checked). This ties 0156 (and 0142/0148) to the SAME anchored-VWAP strategy template with the SAME signal parameters.

## G ENGINE SETTINGS
- Commission $0.00 all columns; Total slippage 0 → zero-cost backtest.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $42,765.00 | $4,430.00 | $38,335.00 |
| Gross profit | $73,635.00 | $18,445.00 | $55,190.00 |
| Gross loss | ($30,870.00) | ($14,015.00) | ($16,855.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 2.39 | 1.32 | 3.27 |
| Max. drawdown | ($5,130.00) | ($6,845.00) | ($3,095.00) |
| Sharpe ratio | 1.69 | 1.56 | 1.66 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.00 | 0.01 | 0.00 |
| R squared | 0.72 | 0.00 | 0.85 |
| Probability | 1.33% | 30.02% | 1.35% |
| Start date | 6/21/2026 | | |
| End date | 6/26/2026 | | |
| Total # of trades | 71 | 29 | 42 |
| Percent profitable | 45.07% | 34.48% | 52.38% |
| # of winning trades | 32 | 10 | 22 |
| # of losing trades | 39 | 19 | 20 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $602.32 | $152.76 | $912.74 |
| Avg. winning trade | $2,301.09 | $1,844.50 | $2,508.64 |
| Avg. losing trade | ($791.54) | ($737.63) | ($842.75) |
| Ratio avg. win / avg. loss | 2.91 | 2.50 | 2.98 |
| Max. consec. winners | 4 | 4 | 5 |
| Max. consec. losers | 4 | 8 | 3 |
| Largest winning trade | $22,560.00 | $4,125.00 | $22,560.00 |
| Largest losing trade | ($2,200.00) | ($1,300.00) | ($2,200.00) |
| Avg. # of trades per day | 17.14 | 7.00 | 10.14 |
| Avg. time in market | 39.97 min | 46.48 min | 35.48 min |
| Avg. bars in trade | 39.97 | 46.48 | 35.48 |
| Profit per month | $217,388.75 | $22,519.17 | $194,869.58 |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: best week in the series — 6/21–6/26/2026 net +$42,765 on 71 trades, PF 2.39, this time SHORT-dominated (+$38,335, PF 3.27). A single short trade won $22,560 (≈1,128 NQ points at $20/pt if 1 contract — likely a large trend day or multiple contracts; open question).
- Parameter continuity: exposed top-of-stack values 3/10/5 exactly match 0146's Signal Quantity Per Trend / Signal Close Threshold(%) / Signal Split(Bars) → same strategy family and unchanged signal-exit parameters as of late June.
- Same Friday-evening review pattern (screenshot on report end date 6/26, 7:39 PM). Machine "hp".
- macOS dock has grown vs earlier frames (adds an orange pencil-style icon, a blue chart icon, a green bar-chart icon) — active tool installation over the weeks.
- Watermark "rednote ID: 1384856832" (partially obscured; consistent with fully-legible OTRIMG-0154).
- Direction dominance flip-flops weekly (long-dominant 5/3–5/29, short-dominant 5/31–6/5 and 6/21–6/26) → the strategy trades both directions and week P&L concentration follows the week's trend direction (hypothesis).
- Open questions: contract quantity (2? — the "2" numeric in the lower settings group might be an order quantity); whether the $22,560 winner is one contract.
