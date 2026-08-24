# OTRIMG-0115

## A FILE IDENTITY
- image_id: OTRIMG-0115
- filename: 20260824_172534345_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Feb 6, 3:46 PM (macOS menu bar)
- taskbar_date: 3:46 PM 2/6/2026 (Windows taskbar)
- social_post_date: none visible
- report_start_date: 2/1/2026
- report_end_date: 2/6/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window titled "mimi" (THIRD distinct remote machine after "hp" and "dev"), NT8 Strategy Analyzer, Display = "Summary ($)".

## D STRATEGY IDENTITY
- No strategy name visible. "template" link above Run.

## E DATA SERIES
- Instrument box blank/cropped; Value = 1 → 1-minute bars (INFERRED; min==bars 35.27).

## F PARAMETERS (right-edge Settings pane, top to bottom)
1. [num] 75
2. [num] 20
3. [num] 46
4. [num] 30
5. [bool] checked
6. [bool] checked
7. SEP (▼ ...)
8. [num] 1
9. SEP (▼ ...)
10. [bool] checked
11. [num] 80
12. SEP (▼ ...)
13. [bool] checked
14. [num] 0
15. [num] 2
16. SEP (▼ ...)
17. [text/num] blank/empty box (Instrument, value cropped)
18. [dropdown] ▼ (Price based on)
19. [dropdown] tiny sliver + ▼ (Type)
20. [num] 1 (Value)
21. SEP (▼ ...)
22. [dropdown] calendar-icon sliver + ▼ (Start date)
23. [dropdown] calendar-icon sliver + ▼ (End date)
24. [dropdown] ▼ (Trading hours)
25. [bool] checked (Break at EOD)
26. SEP (▼ ...)
27. [bool] unchecked (Include commission)
28. [dropdown, grayed] ▼ (Commission — disabled)
29. [dropdown] ▼ partially cut (Maximum bars look back)
30. "template" text link
31. Run button
- Identical parameter state to OTRIMG-0113 (1/30) — the post-mid-January configuration is stable across machines: same ...75/20/46/30 + ✓✓, [1], ✓/80, ✓/0/2 blocks now shown on "mimi".

## G ENGINE SETTINGS
- Include commission: unchecked → $0.00. Slippage 0.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $6,680.00 | ($40.00) | $6,720.00 |
| Gross profit | $66,995.00 | $26,910.00 | $40,085.00 |
| Gross loss | ($60,315.00) | ($26,950.00) | ($33,365.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.11 | 1.00 | 1.20 |
| Max. drawdown | ($20,055.00) | ($18,895.00) | ($6,285.00) |
| Sharpe ratio | -1.51 | -1.51 | 1.54 |
| Sortino ratio | -5.02 | -5.00 | 1.00 |
| Ulcer index | 0.02 | 0.02 | 0.01 |
| R squared | 0.56 | 0.67 | 0.01 |
| Probability | 32.68% | 49.42% | 29.09% |
| Start date | 2/1/2026 | | |
| End date | 2/6/2026 | | |
| Total # of trades | 111 | 55 | 56 |
| Percent profitable | 36.94% | 38.18% | 35.71% |
| # of winning trades | 41 | 21 | 20 |
| # of losing trades | 70 | 34 | 36 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $60.18 | ($0.73) | $120.00 |
| Avg. winning trade | $1,634.02 | $1,281.43 | $2,004.25 |
| Avg. losing trade | ($861.64) | ($792.65) | ($926.81) |
| Ratio avg. win / avg. loss | 1.90 | 1.62 | 2.16 |
| Max. consec. winners | 4 | 3 | 2 |
| Max. consec. losers | 7 | 8 | 6 |
| Largest winning trade | $9,070.00 | $8,640.00 | $9,070.00 |
| Largest losing trade | ($2,600.00) | ($1,990.00) | ($2,600.00) |
| Avg. # of trades per day | 26.80 | 13.28 | 13.52 |
| Avg. time in market | 35.27 min | 40.82 min | 29.82 min |
| Avg. bars in trade | 35.27 | 40.82 | 29.82 |
| Profit per month | $33,956.67 | ($203.33) | $34,160.00 |
| Max. time to recover | (cut off by window bottom — not visible) | | |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a (watermark only)

## K FORENSIC INTERPRETATION
- Direct facts: THIRD remote machine "mimi". Week 2/1–2/6/2026: +$6,680 on a huge 111 trades (26.8/day), all profit from shorts (+$6,720 vs long −$40). Much shorter avg hold (35.27 min vs 60–100 min prior weeks) and big intraweek max DD −$20,055 with largest win $9,070 — a high-volatility week traded much more actively.
- macOS menu bar shows 搜狗拼音 (Sogou Pinyin Chinese input method) icon — the macOS operator uses a Chinese IME. Windows taskbar bottom-left shows weather widget "54°F Mostly clear"; a Windows-taskbar button labeled "Jump Desktop" (Jump Desktop Connect app running inside the remote machine).
- Same parameter template as "dev" late-January state → the same strategy build is deployed/tested across at least 3 machines (hp, dev, mimi).
- Open questions: whether machines run the same NinjaTrader license/user; whether "mimi" is a new VPS.
