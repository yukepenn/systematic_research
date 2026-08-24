# OTRIMG-0111

## A FILE IDENTITY
- image_id: OTRIMG-0111
- filename: 20260824_172523188_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Sun Jan 25, 1:20 AM (macOS menu bar)
- taskbar_date: 1:20 AM 1/25/2026 (Windows taskbar)
- social_post_date: none visible
- report_start_date: 1/18/2026
- report_end_date: 1/23/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "dev", NT8 Strategy Analyzer, Display = "Summary ($)". Captured late Saturday night/early Sunday after the week ending Fri 1/23.

## D STRATEGY IDENTITY
- No strategy name visible. "template" link above Run.

## E DATA SERIES
- Instrument box blank/cropped; Type sliver; Value = 1 → 1-minute bars (INFERRED; also min==bars 61.63).

## F PARAMETERS (right-edge Settings pane, top to bottom)
1. [num] 80 (tail of the ✓/80 "U..." group; checkbox row scrolled off above)
2. SEP (▼ ...)
3. [bool] checked
4. [num] 0
5. [num] 2
   (same new ✓/0/2 group first seen in OTRIMG-0109)
6. SEP (▼ ...)
7. [text/num] blank/empty box (Instrument, value cropped)
8. [dropdown] ▼ (Price based on)
9. [dropdown] tiny sliver + ▼ (Type)
10. [num] 1 (Value)
11. SEP (▼ ...)
12. [dropdown] calendar-icon sliver + ▼ (Start date)
13. [dropdown] calendar-icon sliver + ▼ (End date)
14. [dropdown] ▼ (Trading hours)
15. [bool] checked (Break at EOD)
16. SEP (▼ ...)
17. [bool] unchecked (Include commission)
18. [dropdown, grayed] ▼ (Commission — disabled)
19. [dropdown] ▼ (Maximum bars look back)
20. [num] 20 (Bars required to trade)
21. SEP (▼ ...)
22. [dropdown] ▼ (Order fill resolution)
23. [bool] unchecked (Fill limit orders on touch)
24. [num] 0 (Slippage)
25. SEP (▼ ...)
26. [num] 2 — Entries per direction = 2 (was 1 in OTRIMG-0104 on 1/2/2026). Clearly legible; HIGH confidence digit, INFERRED row identity.
27. [dropdown] ▼ (Entry handling; Exit-on-session-close row cut off below)
28. "template" text link
29. Run button
- Row identifications in parentheses INFERRED from the decoded layout of OTRIMG-0104.

## G ENGINE SETTINGS
- Include commission: unchecked (grayed Commission dropdown) → $0.00. Slippage 0. Bars required to trade 20. Entries per direction now 2.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $3,515.00 | $1,680.00 | $1,835.00 |
| Gross profit | $38,315.00 | $19,910.00 | $18,405.00 |
| Gross loss | ($34,800.00) | ($18,230.00) | ($16,570.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.10 | 1.09 | 1.11 |
| Max. drawdown | ($8,905.00) | ($6,080.00) | ($4,280.00) |
| Sharpe ratio | 1.55 | 1.54 | 1.54 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.01 | 0.00 | 0.00 |
| R squared | 0.54 | 0.40 | 0.43 |
| Probability | 37.71% | 41.29% | 40.98% |
| Start date | 1/18/2026 | | |
| End date | 1/23/2026 | | |
| Total # of trades | 76 | 41 | 35 |
| Percent profitable | 34.21% | 36.59% | 31.43% |
| # of winning trades | 26 | 15 | 11 |
| # of losing trades | 50 | 26 | 24 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $46.25 | $40.98 | $52.43 |
| Avg. winning trade | $1,473.65 | $1,327.33 | $1,673.18 |
| Avg. losing trade | ($696.00) | ($701.15) | ($690.42) |
| Ratio avg. win / avg. loss | 2.12 | 1.89 | 2.42 |
| Max. consec. winners | 5 | 6 | 2 |
| Max. consec. losers | 7 | 4 | 6 |
| Largest winning trade | $4,970.00 | $4,970.00 | $4,935.00 |
| Largest losing trade | ($1,300.00) | ($1,300.00) | ($1,300.00) |
| Avg. # of trades per day | 18.35 | 9.90 | 8.45 |
| Avg. time in market | 61.63 min | 72.20 min | 49.26 min |
| Avg. bars in trade | 61.63 | 72.20 | 49.26 |
| Profit per month | $17,867.92 | $8,540.00 | $9,327.92 |
| Max. time to recover | (cut off by window bottom — not visible) | | |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a (watermark only)

## K FORENSIC INTERPRETATION
- Direct facts: winning week +$3,515, 76 trades (frequency back up from 54), 1/18–1/23/2026. Both sides profitable. Max DD −$8,905.00 numerically identical to the all-trades DD in OTRIMG-0097 (different week — coincidence, but noted).
- Engine-settings row "Entries per direction" now shows 2 (was 1 on 1/2/2026, OTRIMG-0104) — either changed by the user or this run uses a different template. Combined with OTRIMG-0109's added checkboxes and 36→30 change, the operator is actively iterating on both strategy parameters and engine settings through January 2026.
- The ✓/0/2 custom group (first seen 1/17) persists.
- Windows taskbar includes a gear (Settings) icon this time. Watermark unchanged ("rednote ID: 1384856832").
- Open question: whether trade count 76 vs 54 is due to Entries per direction 2 or market conditions.
