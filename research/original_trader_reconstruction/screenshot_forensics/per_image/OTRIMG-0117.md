# OTRIMG-0117

## A FILE IDENTITY
- image_id: OTRIMG-0117
- filename: 20260824_172551790_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Feb 13, 8:58 PM (macOS menu bar)
- taskbar_date: 8:58 PM 2/13/2026 (Windows taskbar)
- social_post_date: none visible
- report_start_date: 2/8/2026
- report_end_date: 2/13/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "hp" (back to the first machine), NT8 Strategy Analyzer, Display = "Summary ($)".

## D STRATEGY IDENTITY
- No strategy name visible. "template" link above Run.

## E DATA SERIES
- Instrument box blank/cropped; Value = 1 → 1-minute bars (INFERRED; min==bars 57.37).

## F PARAMETERS (right-edge Settings pane, top to bottom) — NEW LAYOUT vs all earlier captures
1. [unknown] partial box at very top, cut by scroll — unreadable
2. [bool] UNCHECKED
3. [bool] checked
4. [num] 15
5. [dropdown] ▼ (value cropped)
6. [num] 60
7. [num] 5
8. [num] 20
9. [dropdown] ▼ (value cropped)
10. [num] 95
11. [num] 75
12. [num] 50
13. [num] 25
14. [num] 5
15. [num] 3
16. [num] 10
17. [num] 5
   (items 2–17 form ONE long custom group with NO separators — different structure from the Dec–Jan multi-group 65/30/75... template)
18. SEP (▼ ...)
19. [text/num] blank/empty box (Instrument, value cropped)
20. [dropdown] ▼ (Price based on)
21. [dropdown] tiny sliver + ▼ (Type)
22. [num] 1 (Value)
23. SEP (▼ ...)
24. [dropdown] calendar-icon sliver + ▼ (Start date)
25. [dropdown] calendar-icon sliver + ▼ (End date)
26. [dropdown] ▼ (Trading hours)
27. [bool] checked (Break at EOD)
28. SEP (▼ ... — Setup group header; contents cut at pane bottom)
29. "template" text link
30. Run button
- Row identifications in parentheses INFERRED from OTRIMG-0104 layout.

## G ENGINE SETTINGS
- Commission $0.00 all columns; Total slippage 0.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $7,860.00 | ($2,875.00) | $10,735.00 |
| Gross profit | $42,040.00 | $16,740.00 | $25,300.00 |
| Gross loss | ($34,180.00) | ($19,615.00) | ($14,565.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.23 | 0.85 | 1.74 |
| Max. drawdown | ($16,155.00) | ($12,555.00) | ($6,465.00) |
| Sharpe ratio | 1.58 | -1.50 | 1.61 |
| Sortino ratio | 1.00 | -4.99 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.21 | 0.68 | 0.64 |
| Probability | 29.15% | 65.63% | 16.78% |
| Start date | 2/8/2026 | | |
| End date | 2/13/2026 | | |
| Total # of trades | 62 | 31 | 31 |
| Percent profitable | 38.71% | 29.03% | 48.39% |
| # of winning trades | 24 | 9 | 15 |
| # of losing trades | 37 | 22 | 15 |
| # of even trades | 1 | 0 | 1 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $126.77 | ($92.74) | $346.29 |
| Avg. winning trade | $1,751.67 | $1,860.00 | $1,686.67 |
| Avg. losing trade | ($923.78) | ($891.59) | ($971.00) |
| Ratio avg. win / avg. loss | 1.90 | 2.09 | 1.74 |
| Max. consec. winners | 3 | 3 | 7 |
| Max. consec. losers | 8 | 7 | 3 |
| Largest winning trade | $8,490.00 | $8,490.00 | $5,910.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,200.00) |
| Avg. # of trades per day | 14.97 | 7.48 | 7.48 |
| Avg. time in market | 57.37 min | 60.84 min | 53.90 min |
| Avg. bars in trade | 57.37 | 60.84 | 53.90 |
| Profit per month | $39,955.00 | ($14,614.58) | $54,569.58 |
| Max. time to recover | (cut off by window bottom — not visible) | | |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a (watermark only)

## K FORENSIC INTERPRETATION
- Direct facts: back on machine "hp". Week 2/8–2/13/2026: +$7,860, 62 trades, shorts carried it (+$10,735 vs long −$2,875). Largest win $8,490.
- MAJOR: the Settings pane shows a COMPLETELY DIFFERENT parameter layout — one long group (☐, ✓, 15, ▼, 60, 5, 20, ▼, 95, 75, 50, 25, 5, 3, 10, 5) with two enum dropdowns, going straight into Data series. Either a heavily refactored new strategy version (params consolidated into one group) or a different strategy. The 95/75/50/25 descending set and 5/3/10/5 tail are a new fingerprint not seen in any earlier capture.
- macOS menu bar shows input-source switcher displaying "A U.S." (U.S. keyboard active) — together with OTRIMG-0115's 搜狗拼音 icon, confirms a Chinese-input-capable macOS operator toggling IMEs.
- Open questions: whether this new layout is the same strategy rewritten (weekly cadence and trade profile remain similar) or a second product; values behind the two dropdowns.
