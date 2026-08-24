# OTRIMG-0005

## A FILE IDENTITY
- id: OTRIMG-0005
- filename: 20260824_171457853_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Mon Feb 3, 5:35 PM (macOS menu bar)
- taskbar_date: 5:35 PM 2/3/2025 (remote Windows taskbar; time partially under watermark blur, "5:3? PM" visible with 2/3/2025 beneath — LOW confidence on minutes)
- social_post_date: none visible
- report_start_date: 2/3/2025 ("Start date" row)
- report_end_date: 2/3/2025 ("End date" row)
- contract_date_clue: "NQ MAR25" in bottom tab label
- background email time: "6:48 PM" not visible here; background browser instead

## C SOURCE TYPE
NT_TRADE_PERFORMANCE — orange tab reads "Strategy Performance" (NOT "Strategy Analyzer"): this is NinjaTrader's Strategy Performance window for a RUNNING/APPLIED strategy, Display = "Summary ($)", single day 2/3/2025. Bottom tab: "SolarWindRK - NQ MAR25".

## D STRATEGY IDENTITY
- Bottom tab label (verbatim): "SolarWindRK - NQ MAR25"
- Machine name: "creator" (Jump Desktop title)

## E DATA SERIES
- Instrument/contract: NQ MAR25 (from tab label). No data-series panel in this window type.

## F PARAMETERS
- None visible (Strategy Performance window has no settings pane).

## G ENGINE SETTINGS
- Commission present: $146.30 on 35 trades = $4.18/trade.

## H PERFORMANCE (All / Long / Short), 2/3/2025 single session
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | ($616.30) | $4,579.76 | ($5,196.06) |
| Gross profit | $14,038.20 | $11,690.74 | $2,347.46 |
| Gross loss | ($14,654.50) | ($7,110.98) | ($7,543.52) |
| Commission | $146.30 | $75.24 | $71.06 |
| Profit factor | 0.96 | 1.64 | 0.31 |
| Max. drawdown | ($6,735.98) | ($3,100.90) | ($5,779.34) |
| Sharpe ratio | -4.55 | 4.97 | -4.22 |
| Sortino ratio | -15.09 | 1.00 | -14.00 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| Probability | 53.55% | 21.28% | 98.61% |
| Start date | 2/3/2025 | | |
| End date | 2/3/2025 | | |
| Total # of trades | 35 | 18 | 17 |
| Percent profitable | 28.57% | 38.89% | 17.65% |
| # of winning trades | 10 | 7 | 3 |
| # of losing trades | 25 | 11 | 14 |
| # of even trades | 0 | 0 | 0 |
| Avg. trade | ($17.61) | $254.43 | ($305.65) |
| Avg. winning trade | $1,403.82 | $1,670.11 | $782.49 |
| Avg. losing trade | ($586.18) | ($646.45) | ($538.82) |
| Ratio avg. win / avg. loss | 2.39 | 2.58 | 1.45 |
| Max. consec. winners | 3 | 2 | 1 |
| Max. consec. losers | 11 | 5 | 7 |
| Largest winning trade | $3,825.82 | $3,825.82 | $1,150.82 |
| Largest losing trade | ($1,034.18) | ($1,024.18) | ($1,034.18) |
| Avg. # of trades per day | 25.35 | 13.04 | 12.31 |
| Avg. time in market | 38.71 min | 46.94 min | 30.00 min |
| Profit per month | ($9,398.58) | $69,841.34 | ($79,239.92) |
| Max. time to recover | 0.28 days | 0.26 days | 0.76 days |
| Longest flat period | 0.00 min | 86.00 min | 209.00 min |
| Avg. MAE | $646.29 | $683.89 | $606.47 |
Note: no "R squared", "Total slippage", "Avg. bars in trade" rows visible in this window's row set (differs from Analyzer summary); table scrolled to show MAE row at bottom.

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" + blurred circular logo (also blurred stamp over taskbar clock area).
- Background browser fragments (behind NT): "People also ask :" and "5426 pts Account Start order 5426 pts Account" (search results page fragment, verbatim as visible). Left edge: "Sent" (mail folder remnant).

## K FORENSIC INTERPRETATION
- DIRECT FACTS: On Monday 2/3/2025 (first trading day after the 2/2 backtest screenshots) a strategy named "SolarWindRK" was RUNNING/applied on NQ MAR25 and produced 35 live/sim trades, net ($616.30), longs +$4,579.76 vs shorts ($5,196.06), 11 consecutive losers max.
- IMPLICATIONS: First direct sighting of the strategy family name "SolarWindRK" and contract NQ MAR25. 35 trades in one day vs backtest average 8.26/day implies this live day was far more active than the backtest profile (possible different variant, or the high-frequency regime of that day) — HYPOTHESIS. "Strategy Performance" window implies real-time (Sim or live) execution rather than Strategy Analyzer backtest.
- OPEN QUESTIONS: account (Sim vs funded) not visible; whether "SolarWindRK" here is identical to the "SolarWindRKSelTime" analyzer strategy seen 2 days later (OTRIMG-0007).
