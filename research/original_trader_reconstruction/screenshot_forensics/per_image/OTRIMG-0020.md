# OTRIMG-0020

## A FILE IDENTITY
- id: OTRIMG-0020
- filename: 20260824_171554877_iOS.jpg
- batch: jd1

## B DATE EVIDENCE
- screen_capture_date: Fri Feb 21, 4:04 PM (macOS menu bar)
- taskbar_date: 2/21/2025 (Windows taskbar; time obscured by watermark — LOW confidence on minutes)
- social_post_date: none visible
- report_start_date: 2/21/2025
- report_end_date: 2/21/2025
- contract_date_clue: none readable (settings collapsed; instrument box cropped)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Strategy Analyzer "Summary ($)", single-day report, Settings pane COLLAPSED to cropped right-edge strip (same pinned state as OTRIMG-0002/0003).

## D STRATEGY IDENTITY
- None visible. Machine name "creator".

## E DATA SERIES
- Cropped. Data Series group shows empty-looking instrument box, two dropdown glyphs, value 1, unchecked checkbox (all right-clipped).

## F PARAMETERS (settings strip, right edge, top to bottom; all boxes right-cropped)
1. SEP (triangle + "…") [General]
2. dropdown [v]
3. dropdown [v]
4. SEP [Parameters]
5. num: 90
6. num: 179? (right-clipped "17S"-like; INFERRED 179 per full panels)
7. num: 5
8. num: 10
9. num: 10
10. num: 1
11. SEP [Data Series]
12. empty-looking box
13. dropdown [v]
14. dropdown [. v]
15. num: 1
16. checkbox: UNCHECKED
17. SEP [Time frame]
18. date box [≡ v]
19. date box [≡ v]
20. dropdown [v]
21. checkbox: CHECKED
22. SEP [Setup]
23. checkbox: CHECKED
24. dropdown [v]  (Commission template row — present in this later-February layout)
25. dropdown [v]
26. num: 20
27. SEP [Historical fill...]
28. "template"; "Run" button (under watermark)
- Parameters group shows exactly six numeric boxes (90/179?/5/10/10/1): NO LossLimit box → non-LossLimit strategy variant selected — INFERENCE from box count.
- Setup group now has FOUR rows (checked, v, v, 20) vs three in OTRIMG-0002 → Commission template row present (post-update layout), consistent with OTRIMG-0018 (Feb 20).

## G ENGINE SETTINGS
- Commission $12.54 on 3 trades = $4.18/trade → commission ON.

## H PERFORMANCE (All / Long / Short), 2/21/2025 single day
| Row | All | Long | Short |
|---|---|---|---|
| Total net profit | $3,517.46 | ($408.36) | $3,925.82 |
| Gross profit | $4,351.64 | $425.82 | $3,925.82 |
| Gross loss | ($834.18) | ($834.18) | $0.00 |
| Commission | $12.54 | $8.36 | $4.18 |
| Profit factor | 5.22 | 0.51 | 99.00 |
| Max. drawdown | ($834.18) | ($834.18) | $0.00 |
| Sharpe ratio | 10.35 | -9.07 | 10.50 |
| Sortino ratio | 1.00 | -30.08 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.55 | 1.00 | 0.00 |
| Probability | 15.98% | 68.60% | 0.00% |
| Start date | 2/21/2025 | | |
| End date | 2/21/2025 | | |
| Total # of trades | 3 | 2 | 1 |
| Percent profitable | 66.67% | 50.00% | 100.00% |
| # of winning trades | 2 | 1 | 1 |
| # of losing trades | 1 | 1 | 0 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $1,172.49 | ($204.18) | $3,925.82 |
| Avg. winning trade | $2,175.82 | $425.82 | $3,925.82 |
| Avg. losing trade | ($834.18) | ($834.18) | $0.00 |
| Ratio avg. win / avg. loss | 2.61 | 0.51 | 3925.82 |
| Max. consec. winners | 2 | 1 | 1 |
| Max. consec. losers | 1 | 1 | 0 |
| Largest winning trade | $3,925.82 | $425.82 | $3,925.82 |
| Largest losing trade | ($834.18) | ($834.18) | $0.00 |
| Avg. # of trades per day | 4.35 | 2.90 | 1.45 |
| Avg. time in market | 129.67 min | 155.50 min | 78.00 min |
| Avg. bars in trade | 129.67 | 155.50 | 78.00 |
| Profit per month | $107,282.53 | ($12,454.98) | $119,737.51 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
- Watermark: "rednote ID: 1384856832" + blurred stamp over Run area.
- Windows 11 taskbar: Start, Search (two small avatar icons), mail, File Explorer, Edge, NinjaTrader (active), Chrome; tray: ENG, network/volume/battery, 2/21/2025.

## K FORENSIC INTERPRETATION
- DIRECT FACTS: Friday 2/21/2025 intraday check (captured 4:04 PM Mac time, i.e., just after the 4 PM session close ET): day's backtest = 3 trades, +$3,517.46, dominated by one short worth $3,925.82 net (~197 NQ points).
- IMPLICATIONS: Capture at 4:04 PM implies the trader closes/evaluates the day right at the 16:00 boundary (fits SelTime 04:00-16:00 window hypothesis). Six-box parameter group (no LossLimit) implies they reverted from the LossLimit build for this check, consistent with OTRIMG-0018 the previous day.
- OPEN QUESTIONS: strategy name; whether the same run underlies the Feb 20 and Feb 21 frames.
