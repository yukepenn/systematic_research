# OTRIMG-0100

## A FILE IDENTITY
- image_id: OTRIMG-0100
- filename: 20260824_172443672_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Dec 26, 3:44 PM (macOS menu bar top right)
- taskbar_date: 3:44 PM 12/26/2025 (Windows taskbar clock inside remote desktop) — fixes year = 2025
- social_post_date: none visible
- report_start_date: 12/21/2025
- report_end_date: 12/26/2025
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "hp", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", with right-edge pinned Settings pane.

## D STRATEGY IDENTITY
- No strategy/template/account name visible. Analyzer tab "Analyzer" + "+". "template" link above Run button in Settings pane.

## E DATA SERIES
- Instrument/contract: not visible.
- Bar type: Avg. time in market (min) = Avg. bars in trade (113.78/177.75/62.60) → 1-minute bars (INFERRED).
- Trading hours: not visible.

## F PARAMETERS (right-edge pinned Settings pane, top to bottom; labels cropped)
1. [num] 9
2. SEP (▼ ...)
3. [bool] checked
4. [num] RAW_VISIBLE_TEXT "45" + partial round glyph clipped by box edge → INFERRED 450 (third digit half-visible, round shape; confidence MEDIUM) → record "45?"
5. [num] RAW_VISIBLE_TEXT "20" + partial round glyph → INFERRED 200 (confidence MEDIUM) → record "20?"
6. SEP (▼ ...)
7. [num] 65
8. [num] 30
9. [num] 75
10. [num] 20
11. [num] 46
12. [num] 36
13. SEP (▼ ...)
14. [num] 1
15. SEP (▼ ...)
16. [bool] checked
17. [num] 80
18. SEP (▼ ...)
19. [text/num] empty-looking box
20. [dropdown] ▼ glyph only
21. [dropdown] ▼ glyph only
22. [num] 1
23. SEP (▼ ...)
24. [dropdown] thin sliver of value + ▼
25. [dropdown] thin sliver of value + ▼
26. [dropdown] ▼ glyph only
27. [bool] checked
28. SEP (▼ — bottom group collapsed against "template"; its contents not visible at this scroll position)
29. "template" text link
30. Run button
- Same numeric fingerprint block 65/30/75/20/46/36 | 1 | ✓/80 as OTRIMG-0097; this scroll position additionally reveals a top group: 9 | SEP | ✓ | 45?(450) | 20?(200).

## G ENGINE SETTINGS
- Commission $0.00 all columns; Total slippage 0. Nothing else visible.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($90.00) | $740.00 | ($830.00) |
| Gross profit | $2,750.00 | $2,545.00 | $205.00 |
| Gross loss | ($2,840.00) | ($1,805.00) | ($1,035.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.97 | 1.41 | 0.20 |
| Max. drawdown | ($2,320.00) | ($1,505.00) | ($845.00) |
| Sharpe ratio | -1.84 | 1.85 | -1.83 |
| Sortino ratio | -6.10 | 1.00 | -6.07 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.05 | 0.59 | 0.68 |
| Probability | 51.24% | 38.13% | 87.34% |
| Start date | 12/21/2025 | | |
| End date | 12/26/2025 | | |
| Total # of trades | 9 | 4 | 5 |
| Percent profitable | 22.22% | 25.00% | 20.00% |
| # of winning trades | 2 | 1 | 1 |
| # of losing trades | 7 | 3 | 4 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($10.00) | $185.00 | ($166.00) |
| Avg. winning trade | $1,375.00 | $2,545.00 | $205.00 |
| Avg. losing trade | ($405.71) | ($601.67) | ($258.75) |
| Ratio avg. win / avg. loss | 3.39 | 4.23 | 0.79 |
| Max. consec. winners | 1 | 1 | 1 |
| Max. consec. losers | 3 | 2 | 3 |
| Largest winning trade | $2,545.00 | $2,545.00 | $205.00 |
| Largest losing trade | ($850.00) | ($850.00) | ($805.00) |
| Avg. # of trades per day | 2.61 | 1.16 | 1.45 |
| Avg. time in market | 113.78 min | 177.75 min | 62.60 min |
| Avg. bars in trade | 113.78 | 177.75 | 62.60 |
| Profit per month | ($549.00) | $4,514.00 | ($5,063.00) |
| Max. time to recover | 2.76 days | 2.70 days | 4.01 days |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a (watermark only)

## K FORENSIC INTERPRETATION
- Direct facts: one-week report 12/21–12/26/2025, captured on its end date (both clocks 12/26/2025 3:44 PM). Only 9 trades in the week vs 77 the prior week (OTRIMG-0097) — drastically lower trade frequency with the same 65/30/75/20/46/36 core parameter block visible; the newly visible top group (✓, 450?, 200?) suggests an enabled feature with two large numeric thresholds (e.g. a time window or point/tick filter). Trade counts long 4 / short 5.
- Watermark: 小红书 logo + "rednote ID: 1384856832".
- Machine "hp"; Windows 11 taskbar shows NinjaTrader, File Explorer, Chrome plus two additional app icons (image viewer/paint-like). Background macOS window fragment at bottom left: "Sent" (likely Mail sidebar). Bottom-right fragment of dark text under taskbar (unreadable).
- Open questions: whether "9" (item 1) is the bottom of the previous group or its own parameter; exact values of the two right-cropped numbers (450/200 inferred).
- Hypothesis (labeled): the week of 12/21 was a holiday-shortened, low-volatility week (Christmas), which may explain few trades if a volatility/size filter (450/200?) gates entries.
