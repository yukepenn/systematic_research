# OTRIMG-0010

## A FILE IDENTITY
- id: OTRIMG-0010
- filename: 20260824_171524160_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: none visible (macOS menu bar cropped out; only window traffic lights + "creator" title bar visible)
- taskbar_date: none visible (no Windows taskbar in frame)
- social_post_date: none visible
- report_start_date: 2/6/2025
- report_end_date: 2/8/2025
- contract_date_clue: none visible (no settings pane, no tab label with contract)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)" (orange "Strategy Analyzer" tab), window stretched wide; Settings pane fully hidden. Full row set visible down to Avg. ETD.

## D STRATEGY IDENTITY
- None visible. Machine name "creator".

## E DATA SERIES
- None visible.

## F PARAMETERS
- None visible (settings pane closed/off-frame).

## G ENGINE SETTINGS
- Commission $50.16 on 4 trades = $12.54/trade (3× the $4.18 seen elsewhere — suggests multi-contract fills or different template; see K).

## H PERFORMANCE (All / Long / Short), 2/6/2025–2/8/2025
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | $6,864.84 | $1,429.92 | $5,434.92 |
| Gross profit | $11,239.92 | $1,637.46 | $9,602.46 |
| Gross loss | ($4,375.08) | ($207.54) | ($4,167.54) |
| Commission | $50.16 | $25.08 | $25.08 |
| Profit factor | 2.57 | 7.89 | 2.30 |
| Max. drawdown | ($4,167.54) | ($207.54) | ($4,167.54) |
| Sharpe ratio | 9.94 | 9.35 | 9.77 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.85 | 1.00 | 1.00 |
| Probability | 22.87% | 18.26% | 28.80% |
| Start date | 2/6/2025 | | |
| End date | 2/8/2025 | | |
| Total # of trades | 4 | 2 | 2 |
| Percent profitable | 50.00% | 50.00% | 50.00% |
| # of winning trades | 2 | 1 | 1 |
| # of losing trades | 2 | 1 | 1 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $1,716.21 | $714.96 | $2,717.46 |
| Avg. winning trade | $5,619.96 | $1,637.46 | $9,602.46 |
| Avg. losing trade | ($2,187.54) | ($207.54) | ($4,167.54) |
| Ratio avg. win / avg. loss | 2.57 | 7.89 | 2.30 |
| Max. consec. winners | 2 | 1 | 1 |
| Max. consec. losers | 1 | 1 | 1 |
| Largest winning trade | $9,602.46 | $1,637.46 | $9,602.46 |
| Largest losing trade | ($4,167.54) | ($207.54) | ($4,167.54) |
| Avg. # of trades per day | 5.79 | 2.90 | 2.90 |
| Avg. time in market | 33.75 min | 51.50 min | 16.00 min |
| Avg. bars in trade | 33.75 | 51.50 | 16.00 |
| Profit per month | $209,377.62 | $43,612.56 | $165,765.06 |
| Max. time to recover | 0.06 days | 0.09 days | 0.01 days |
| Longest flat period | 0.00 min | 22.00 min | 77.00 min |
| Avg. MAE | $2,073.75 | $1,845.00 | $2,302.50 |
| Avg. MFE | $5,576.25 | $4,357.50 | $6,795.00 |
| Avg. ETD | $3,860.04 | $3,642.54 | $4,077.54 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" bottom right + faint blurred circular logo. No background windows visible.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: 2-3 day window (Thu 2/6 – Sat 2/8/2025) with only 4 trades, net +$6,864.84; a single short won $9,602.46 (~480 NQ points gross? — $9,602.46+comm ≈ 480.5 pts at $20/pt if 1 contract) and a single loss ($4,167.54).
- ANOMALY: per-trade values here end in .46/.54 (e.g., 1,637.46 / 207.54) vs .82/.18 in sibling images, and commission is $12.54/trade (= 3 × $4.18) → CONSISTENT WITH 3-CONTRACT position sizing (Quantity=3 or 3 entries), or MNQ multi-lot — HYPOTHESIS: quantity was 3, since $x.46 = n×$20-grid minus 3×$4.18-style commission adjustments.
- Extreme Sharpe 9.94 / PF 2.57 on 4 trades is small-sample noise. Avg MAE $2,073 vs avg win $5,620 suggests wide stops / big excursion tolerance.
- OPEN QUESTIONS: which strategy/params produced this run (no settings visible); why the analyzer window was widened/settings hidden for this capture; whether end date 2/8 (Saturday) implies "to end of week" habit.
