# OTRIMG-0152

## A FILE IDENTITY
- id: OTRIMG-0152
- filename: 20260824_173113599_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Jun 12, 5:57 PM (macOS menu bar; year not shown)
- taskbar_date: 5:57 PM / 6/12/2026 (Windows taskbar bottom right)
- social_post_date: none visible
- report_start_date: 6/7/2026 (Start date row; also left date picker "06/07/2026")
- report_end_date: 6/12/2026 (End date row; also right date picker "06/12/2026")
- contract_date_clue: none visible

## C SOURCE TYPE
NT_TRADE_PERFORMANCE — NinjaTrader 8 "Trade Performance" window (NOT Strategy Analyzer): orange tab "Trade Performance", Display "Summary ($)", filter funnel icon, two date pickers (06/07/2026, 06/12/2026) and a "Generate" button; bottom tab named "Report". Jump Desktop to machine "hp".

## D STRATEGY IDENTITY
- No strategy or account name visible. Machine "hp".

## E DATA SERIES
- Not visible (Trade Performance shows account/execution results, not a data series).

## F PARAMETERS
- No settings pane in this window type. Toolbar controls: Display [dropdown]="Summary ($)"; filter icon; date picker [06/07/2026]; date picker [06/12/2026]; button "Generate".

## G ENGINE SETTINGS
- Commission row NON-ZERO: $141.20 all / $73.96 long / $67.24 short → these are real recorded executions (live/sim/playback account), not a zero-commission backtest. All dollar values carry cents (non-multiples of $5) → real fill prices.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $11,860.30 | $8,624.54 | $3,235.76 |
| Gross profit | $59,890.58 | $31,718.16 | $28,172.42 |
| Gross loss | ($48,030.28) | ($23,093.62) | ($24,936.66) |
| Commission | $141.20 | $73.96 | $67.24 |
| Profit factor | 1.25 | 1.37 | 1.13 |
| Max. drawdown | ($18,278.30) | ($9,821.54) | ($10,350.02) |
| Sharpe ratio | 1.67 | 1.62 | 1.58 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| Probability | 7.48% | 8.11% | 24.25% |
| Start date | 6/7/2026 | | |
| End date | 6/12/2026 | | |
| Total # of trades | 136 | 69 | 67 |
| Percent profitable | 50.00% | 53.62% | 46.27% |
| # of winning trades | 68 | 37 | 31 |
| # of losing trades | 68 | 32 | 36 |
| # of even trades | 0 | 0 | 0 |
| Avg. trade | $87.21 | $124.99 | $48.29 |
| Avg. winning trade | $880.74 | $857.25 | $908.79 |
| Avg. losing trade | ($706.33) | ($721.68) | ($692.69) |
| Ratio avg. win / avg. loss | 1.25 | 1.19 | 1.31 |
| Max. consec. winners | 12 | 9 | 5 |
| Max. consec. losers | 11 | 10 | 7 |
| Largest winning trade | $6,798.82 | $5,383.82 | $6,798.82 |
| Largest losing trade | ($3,046.18) | ($2,122.36) | ($3,046.18) |
| Avg. # of trades per day | 32.83 | 16.66 | 16.17 |
| Avg. time in market | 20.49 min | 24.51 min | 16.35 min |
| Profit per month | $60,289.86 | $43,841.41 | $16,448.45 |
| Max. time to recover | 1.46 days | 0.85 days | 1.63 days |
| Longest flat period | 832.97 min | 991.65 min | 832.97 min |
| Avg. MAE (row cut at bottom edge) | $793.42? | $794.37? | $792.43? |
- Note: no "R squared", "Total slippage", "Avg. bars in trade" rows visible in this window's layout; "Avg. MAE" label and values are half-cut by the window bottom (values marked "?").

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: this is EXECUTION evidence, not a backtest: Trade Performance report for 6/7–6/12/2026 with commission $141.20 and cent-level P&L. Net +$11,860.30 on 136 trades (50.00% win), both sides positive. 32.83 trades/day with avg 20.49 min in market — far more active and shorter-hold than the earlier backtests (13–20 trades/day, 40–76 min holds).
- Commission $141.20 / 136 trades ≈ $1.04 per trade — far below retail NQ round-turn rates (≈$4.36 Lifetime); suggests either a partial-commission template, micro contracts on some fills, or a sim account with a token commission setting (open question).
- Trader reviewed results the same Friday evening (5:57 PM on 6/12/2026): consistent weekly Fri/Sat review ritual across the whole JD series.
- Largest win $6,798.82 / largest loss −$3,046.18 with cents → real fills; loss magnitude ≈ prior backtest stop region ($2,600–$3,000).
- Machine "hp"; watermark "rednote ID: 13?4856832" again (digits obscured); Windows taskbar shows NinjaTrader, Chrome, notes app; macOS dock calendar shows JUN 12.
- Hypothesis: by 6/7–6/12/2026 the trader had moved from backtesting to live/sim execution of the strategy (or is auditing sim-account performance of the strategy that the Analyzer screenshots develop).
- Open questions: which account (Sim/live) and which strategy generated these executions; whether "Report" tab aggregates multiple strategies.
