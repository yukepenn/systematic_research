# OTRIMG-0109

## A FILE IDENTITY
- image_id: OTRIMG-0109
- filename: 20260824_172515788_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Sat Jan 17, 12:42 AM (macOS menu bar)
- taskbar_date: 12:42 AM 1/17/2026 (Windows taskbar)
- social_post_date: none visible
- report_start_date: 1/11/2026
- report_end_date: 1/16/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "dev", NT8 Strategy Analyzer, Display = "Summary ($)". Captured just after midnight following the Friday session.

## D STRATEGY IDENTITY
- No strategy name visible. "template" link above Run.

## E DATA SERIES
- Instrument box blank/cropped; Type dropdown sliver; Value = 1. Avg time (min) == Avg bars (72.33) → 1-minute bars (INFERRED).

## F PARAMETERS (right-edge Settings pane, top to bottom)
1. SEP (▼ ...)
2. [num] 65
3. [num] 30
4. [num] 75
5. [num] 20
6. [num] 46
7. [num] 30  ← NOTE: this slot read 36 in Dec captures (OTRIMG-0097/0100); now 30. Clearly legible; confidence HIGH.
8. [bool] checked — NEW row not present in this group in Dec captures
9. [bool] checked — NEW row not present in this group in Dec captures
10. SEP (▼ ...)
11. [num] 1
12. SEP (▼ ...)
13. [bool] checked
14. [num] 80
15. SEP (▼ ...)
16. [bool] checked — NEW group vs Dec captures
17. [num] 0
18. [num] 2
19. SEP (▼ ...)
20. [text/num] blank/empty box (Instrument, value cropped)
21. [dropdown] ▼ (Price based on)
22. [dropdown] tiny sliver + ▼ (Type)
23. [num] 1 (Value)
24. SEP (▼ ...)
25. [dropdown] calendar-icon sliver + ▼ (Start date)
26. [dropdown] calendar-icon sliver + ▼ (End date)
27. [dropdown] ▼ (Trading hours)
28. [bool] checked (Break at EOD; row partially clipped at pane bottom)
29. "template" text link
30. Run button
- Row identifications in parentheses are INFERRED from the decoded layout of OTRIMG-0104.

## G ENGINE SETTINGS
- Commission $0.00 all columns; Total slippage 0.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($2,185.00) | ($4,100.00) | $1,915.00 |
| Gross profit | $23,570.00 | $10,125.00 | $13,445.00 |
| Gross loss | ($25,755.00) | ($14,225.00) | ($11,530.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.92 | 0.71 | 1.17 |
| Max. drawdown | ($9,455.00) | ($8,080.00) | ($4,990.00) |
| Sharpe ratio | -1.82 | -1.80 | 1.86 |
| Sortino ratio | -6.03 | -5.98 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.37 | 0.91 | 0.23 |
| Probability | 60.74% | 77.37% | 36.70% |
| Start date | 1/11/2026 | | |
| End date | 1/16/2026 | | |
| Total # of trades | 54 | 26 | 28 |
| Percent profitable | 37.04% | 38.46% | 35.71% |
| # of winning trades | 20 | 10 | 10 |
| # of losing trades | 34 | 16 | 18 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($40.46) | ($157.69) | $68.39 |
| Avg. winning trade | $1,178.50 | $1,012.50 | $1,344.50 |
| Avg. losing trade | ($757.50) | ($889.06) | ($640.56) |
| Ratio avg. win / avg. loss | 1.56 | 1.14 | 2.10 |
| Max. consec. winners | 3 | 2 | 5 |
| Max. consec. losers | 9 | 4 | 8 |
| Largest winning trade | $3,830.00 | $3,830.00 | $2,345.00 |
| Largest losing trade | ($1,305.00) | ($1,305.00) | ($1,260.00) |
| Avg. # of trades per day | 15.64 | 7.53 | 8.11 |
| Avg. time in market | 72.33 min | 97.62 min | 48.86 min |
| Avg. bars in trade | 72.33 | 97.62 | 48.86 |
| Profit per month | ($13,328.50) | ($25,010.00) | $11,681.50 |
| Max. time to recover | (cut off by window bottom — not visible) | | |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a (watermark only)

## K FORENSIC INTERPRETATION
- Direct facts: second consecutive losing week (−$2,185, 54 trades, PF 0.92), 1/11–1/16/2026, captured 12:42 AM Sat 1/17.
- STRATEGY EVOLUTION EVIDENCE: the six-number parameter group changed 65/30/75/20/46/**36** → 65/30/75/20/46/**30**, AND two new checkbox rows were appended to that group, AND a new group (✓/0/2) appeared before the Data-series section. Between 1/2/2026 and 1/16/2026 the strategy either (a) was recompiled with added parameters and a tuned value, or (b) is a different variant. The developer is actively iterating (hypothesis: tuning after the 1/4–1/9 losing week).
- Windows taskbar now includes an Adobe Acrobat icon and a Notepad-style icon alongside NinjaTrader/Explorer/Chrome.
- Open questions: whether 46→46 stayed while 36→30 changed due to tuning; identity of ✓/0/2 group (e.g. re-entry/stop settings with values 0 and 2).
