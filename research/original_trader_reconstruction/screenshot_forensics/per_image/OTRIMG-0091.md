# OTRIMG-0091

## A FILE IDENTITY
- id: OTRIMG-0091
- filename: 20260824_172409695_iOS.jpg
- resolution: 1440 x 1636 (taller than siblings — a ZOOMED/enlarged capture of the window; text much larger)

## B DATE EVIDENCE
- screen_capture_date: none visible (macOS menu bar visible but clock area outside the frame/zoom)
- screen_capture_time: none visible
- taskbar_date: none visible (remote taskbar outside frame)
- social_post_date: none visible
- report_start_date: 11/23/2025
- report_end_date: 11/28/2025
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — zoomed Jump Desktop window titled "dev", NT8 Strategy Analyzer, Display = "Summary ($)". Settings pane almost entirely cropped (only "Set…" header sliver and collapse triangles visible at right edge).

## D STRATEGY IDENTITY
- No strategy name visible. Orange "Strategy Analyzer" tab (top-left, partially cut); bottom tab "Analyzer" + "+".

## E DATA SERIES
- Not visible. NOTE: Avg. bars in trade (46.03) ≠ Avg. time in market (56.14 min) for All trades in this frame (Long 59.69 bars vs 77.67 min; Short equal 28.46/28.46) — long trades include non-bar clock time (e.g. session-break spanning), indirect evidence of 1-min bars with a session gap.

## F PARAMETERS
- Settings pane cropped out; only 8 SEP collapse-triangles visible along the right edge (group structure only, no values). "Set" header text visible top-right.

## G ENGINE SETTINGS
- Commission $0.00 (report). Total slippage 0.

## H PERFORMANCE (Summary ($); All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($15,365.00) | ($1,085.00) | ($14,280.00) |
| Gross profit | $21,410.00 | $15,845.00 | $5,565.00 |
| Gross loss | ($36,775.00) | ($16,930.00) | ($19,845.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.58 | 0.94 | 0.28 |
| Max. drawdown | ($16,680.00) | ($6,345.00) | ($14,280.00) |
| Sharpe ratio | -1.44 | -1.53 | -1.45 |
| Sortino ratio | -4.77 | -5.06 | -4.80 |
| Ulcer index | 0.02 | 0.01 | 0.02 |
| R squared | 0.73 | 0.06 | 0.91 |
| Probability | 96.22% | 57.19% | 99.42% |
| Start date | 11/23/2025 | | |
| End date | 11/28/2025 | | |
| Total # of trades | 64 | 36 | 28 |
| Percent profitable | 25.00% | 36.11% | 10.71% |
| # of winning trades | 16 | 13 | 3 |
| # of losing trades | 48 | 23 | 25 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($240.08) | ($30.14) | ($510.00) |
| Avg. winning trade | $1,338.13 | $1,218.85 | $1,855.00 |
| Avg. losing trade | ($766.15) | ($736.09) | ($793.80) |
| Ratio avg. win / avg. loss | 1.75 | 1.66 | 2.34 |
| Max. consec. winners | 3 | 2 | 1 |
| Max. consec. losers | 10 | 5 | 12 |
| Largest winning trade | $4,280.00 | $2,605.00 | $4,280.00 |
| Largest losing trade | ($1,490.00) | ($1,300.00) | ($1,490.00) |
| Avg. # of trades per day | 15.45 | 8.69 | 6.76 |
| Avg. time in market | 56.14 min | 77.67 min | 28.46 min |
| Avg. bars in trade | 46.03 | 59.69 | 28.46 |
| Profit per month | ($78,105.42) | ($5,515.42) | ($72,590.00) |
| Max. time to recover | 4.75 days | 4.73 days | 4.61 days |
| Longest flat period | 1.09 days | 1.23 days | 1.70 days |
| Avg. MAE | $750.08 | $672.78 | $849.46 |
| Avg. MFE | $930.00 | $1,085.14 | $730.54 |
| Avg. ETD | $1,170.08 | $1,115.28 | $1,240.54 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Faint watermark "rednote ID: 13848…" bottom-right (mostly cut/faded); faint round watermark bubble at right edge.

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Thanksgiving week 11/23→11/28/2025 on "dev": WORST week in the series — net −$15,365, PF 0.58; short side catastrophic (−$14,280, PF 0.28, 3 winners of 28, 12 consecutive losers).
- The zoomed view exposes three metric rows unseen in the 936-px frames: Avg. MAE / Avg. MFE / Avg. ETD (values above).
- Longest flat period ~1.09-1.70 days and only 15.45 trades/day over 64 trades — consistent with the holiday-shortened, thin-liquidity week.
- Avg. bars < avg. minutes for longs (59.69 vs 77.67) while equal for shorts — some long trades spanned no-data periods (session break), i.e. held across the 17:00-18:00 ET maintenance hour.
IMPLICATIONS (hypotheses):
- This capture is likely from Fri Nov 28, 2025 (capture clock not visible; report ends that Friday, matching the series' Friday-evening ritual).
- After three winning weeks, this large loss week may have triggered the next parameter change (compare with later frames).
OPEN QUESTIONS:
- Whether the trader zoomed intentionally to read MAE/MFE — suggests attention to excursion metrics after losses.
