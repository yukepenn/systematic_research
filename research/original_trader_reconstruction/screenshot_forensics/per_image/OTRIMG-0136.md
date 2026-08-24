# OTRIMG-0136

## A FILE IDENTITY
- id: OTRIMG-0136
- filename: 20260824_172714886_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Apr 17, 3:22 PM (macOS menu bar; year not shown)
- taskbar_date: Windows taskbar is NOT visible in this capture (Jump Desktop window covers it; macOS dock at bottom instead)
- social_post_date: none visible
- report_start_date: 4/12/2026
- report_end_date: 4/17/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "APR 17". Background macOS Finder window "temp" behind the dock shows a file row "Apple" with a date reading like "4/1/26" (partially occluded, LOW confidence).

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "hp", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)". Window is taller/scrolled so THREE additional metric rows are visible beyond prior captures (Max. time to recover, Longest flat period, and a half-cut Avg. MAE row).

## D STRATEGY IDENTITY
- No strategy/template/account name visible.

## E DATA SERIES
- Not visible. Report window 4/12/2026 → 4/17/2026 (captured Friday 3:22 PM — before session close).

## F PARAMETERS (Settings pane; parameter stack from 2nd row down)
1. numeric: 16 — fully visible (a row above exists, scrolled off: the "30?" box seen in OTRIMG-0132)
2. numeric: 0 — fully visible
3. numeric: 9 — fully visible (NOTE: this position read "10" in OTRIMG-0132; see K)
4. numeric: 15 — fully visible
5. dropdown: unreadable
6. numeric: 60 — fully visible
7. numeric: 5 — fully visible
8. numeric: 20 — fully visible
9. dropdown: unreadable
10. numeric: 95 — fully visible
11. numeric: 75 — fully visible
12. numeric: 50 — fully visible
13. numeric: 25 — fully visible
14. numeric: 5 — fully visible
15. numeric: 3 — fully visible
16. numeric: 10 — fully visible
17. numeric: 5 — fully visible
18. SEP
19. numeric/text box: EMPTY/blank
20. dropdown: unreadable
21. dropdown: tiny mark + "v", unreadable
22. numeric: 1 — fully visible
23. SEP
24. dropdown with grid/calendar glyph: unreadable
25. dropdown with grid/calendar glyph: unreadable
26. dropdown: unreadable
27. bool checkbox: CHECKED
28. SEP
29. bool checkbox: UNCHECKED
30. dropdown: DISABLED (grayed, bottom-cropped)
31. italic label "template"; Button "Run" (partially covered by 小红书 watermark)

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0.

## H PERFORMANCE (Summary ($), verbatim)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $11,370.00 | $24,910.00 | ($13,540.00) |
| Gross profit | $35,840.00 | $33,885.00 | $1,955.00 |
| Gross loss | ($24,470.00) | ($8,975.00) | ($15,495.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.46 | 3.78 | 0.13 |
| Max. drawdown | ($10,160.00) | ($6,015.00) | ($13,540.00) |
| Sharpe ratio | 1.60 | 1.66 | -1.76 |
| Sortino ratio | 1.00 | 1.00 | -5.85 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.46 | 0.78 | 0.95 |
| Probability | 20.20% | 2.00% | 99.90% |
| Start date | 4/12/2026 | | |
| End date | 4/17/2026 | | |
| Total # of trades | 33 | 19 | 14 |
| Percent profitable | 45.45% | 63.16% | 21.43% |
| # of winning trades | 15 | 12 | 3 |
| # of losing trades | 18 | 7 | 11 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $344.55 | $1,311.05 | ($967.14) |
| Avg. winning trade | $2,389.33 | $2,823.75 | $651.67 |
| Avg. losing trade | ($1,359.44) | ($1,282.14) | ($1,408.64) |
| Ratio avg. win / avg. loss | 1.76 | 2.20 | 0.46 |
| Max. consec. winners | 3 | 7 | 1 |
| Max. consec. losers | 4 | 4 | 5 |
| Largest winning trade | $7,390.00 | $7,390.00 | $1,280.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,600.00) |
| Avg. # of trades per day | 7.97 | 4.59 | 4.06 |
| Avg. time in market | 123.09 min | 147.74 min | 89.64 min |
| Avg. bars in trade | 123.00 | 147.58 | 89.64 |
| Profit per month | $57,797.50 | $126,625.83 | ($82,594.00) |
| Max. time to recover | 1.19 days | 1.19 days | 4.34 days |
| Longest flat period | 667.01 min | 1027.01 min | 1338.00 min |
| Avg. MAE (row half-cut at bottom edge) | $1,194.00 (LOW conf) | $1,030.79 (LOW conf) | $1,415.71 (LOW conf) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" + 小红书 logo (overlapping the Run button).

## K FORENSIC INTERPRETATION
Direct facts:
- Week 4/12–4/17/2026, machine "hp", captured Friday 3:22 PM (intraday).
- PARAMETER CHANGE DETECTED: position 3 of the visible stack reads 9 here vs 10 in OTRIMG-0132 (4/2/2026 capture). Sequence now 16, 0, 9, 15, [dd], 60, 5, 20 (was [30?], 16, 0, 10, 15, [dd], 60, 5, 20). Either the poster tuned one parameter between 4/2 and 4/17, or one of the two reads is wrong; both digits were individually crisp — change is the stronger reading.
- Trade profile transformed this week: only 33 trades (7.97/day, roughly half of usual) and avg time in market 123 min (2-4x usual) — consistent with a parameter change altering holding behavior, not just market conditions.
- Longs +$24,910 with PF 3.78; shorts destroyed (PF 0.13, 3 winners of 14). Largest loss again exactly ($2,600.00) everywhere.
- New rows visible: Max. time to recover, Longest flat period, half-cut Avg. MAE (~$1,194 all-trades).
- Background macOS Finder window "temp" with a file "Apple" (date like 4/1/26) behind the dock.
Implications (hypotheses):
- If the changed parameter (10→9) is a signal length/threshold, it coincides with halved trade frequency and doubled hold time — a material re-tune after two poor weeks (0129, 0134).
Open questions:
- Identity of the changed parameter; whether the topmost hidden box still reads 30.
