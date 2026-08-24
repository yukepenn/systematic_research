# OTRIMG-0138

## A FILE IDENTITY
- id: OTRIMG-0138
- filename: 20260824_172721243_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Wed Apr 29, 1:15 PM (macOS menu bar; year not shown)
- taskbar_date: 1:16 PM / 4/29/2026 (Windows taskbar; one minute ahead of Mac clock)
- social_post_date: none visible
- report_start_date: 4/19/2026
- report_end_date: 4/24/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "APR 29". Report covers the PRIOR week, captured mid-week Wednesday.

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "dev", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)".

## D STRATEGY IDENTITY
- No strategy name visible, BUT the Settings pane content is structurally DIFFERENT from every earlier capture in this series (see F) — different parameter set → likely a different strategy or a heavily revised version.

## E DATA SERIES
- Not visible. Report window 4/19/2026 → 4/24/2026.

## F PARAMETERS (Settings pane — NEW STRUCTURE, top-to-bottom)
1. SEP (collapse triangle + "...") at very top
2. dropdown: value unreadable
3. dropdown: value unreadable
4. SEP
5. bool checkbox: CHECKED
6. numeric: 10 — fully visible
7. numeric: 20 — fully visible
8. numeric: 14 — fully visible
9. numeric: 198? — digits flush to box edge; may continue (e.g. 1980), confidence LOW
10. numeric: 180? — same flush condition, could be 1800; confidence LOW
11. numeric: 140? — same flush condition, could be 1400; confidence LOW
12. bool checkbox: CHECKED
13. numeric: 16 — fully visible
14. numeric: 6 — fully visible
15. numeric: 9 — fully visible
16. SEP
17. bool checkbox: CHECKED
18. numeric: 13 — fully visible
19. numeric: 0 — fully visible
20. numeric: 13 — fully visible
21. numeric: 30 — fully visible
22. numeric: 15 — fully visible
23. numeric: 0 — fully visible
24. numeric: 15 — fully visible
25. numeric: 30 — fully visible
26. SEP
27. bool checkbox: UNCHECKED
28. bool checkbox: CHECKED
29. italic label "template"; Button "Run"

Structure note: groups of [enable-checkbox + numeric block] — unlike the flat 16-numeric stack of OTRIMG-0121→0136. The 16/6/9 triplet echoes values (16, 9) seen in the older stack.

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0. Engine-settings groups (Data series/Set up/etc.) are scrolled out of view.

## H PERFORMANCE (Summary ($), verbatim)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $9,215.00 | $7,655.00 | $1,560.00 |
| Gross profit | $36,120.00 | $20,320.00 | $15,800.00 |
| Gross loss | ($26,905.00) | ($12,665.00) | ($14,240.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.34 | 1.60 | 1.11 |
| Max. drawdown | ($9,615.00) | ($5,950.00) | ($4,965.00) |
| Sharpe ratio | 1.59 | 1.92 | 1.54 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.73 | 0.80 | 0.48 |
| Probability | 21.20% | 18.39% | 41.62% |
| Start date | 4/19/2026 | | |
| End date | 4/24/2026 | | |
| Total # of trades | 47 | 23 | 24 |
| Percent profitable | 42.55% | 52.17% | 33.33% |
| # of winning trades | 20 | 12 | 8 |
| # of losing trades | 27 | 11 | 16 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $196.06 | $332.83 | $65.00 |
| Avg. winning trade | $1,806.00 | $1,693.33 | $1,975.00 |
| Avg. losing trade | ($996.48) | ($1,151.36) | ($890.00) |
| Ratio avg. win / avg. loss | 1.81 | 1.47 | 2.22 |
| Max. consec. winners | 11 | 6 | 5 |
| Max. consec. losers | 7 | 3 | 5 |
| Largest winning trade | $3,710.00 | $3,390.00 | $3,710.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,210.00) |
| Avg. # of trades per day | 11.35 | 6.66 | 5.79 |
| Avg. time in market | 72.04 min | 105.13 min | 40.33 min |
| Avg. bars in trade | 72.00 | 105.04 | 40.33 |
| Profit per month | $46,842.92 | $46,695.50 | $7,930.00 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" + 小红书 logo.

## K FORENSIC INTERPRETATION
Direct facts:
- Week 4/19–4/24/2026 on "dev", captured Wednesday 4/29 midday; both sides profitable, +$9,215 net.
- The Settings pane no longer matches the long-running flat parameter stack: it now shows checkbox-gated parameter blocks ([✓]10/20/14/198?/180?/140?, [✓]16/6/9, [✓]13/0/13/30/15/0/15/30, then [ ]/[✓]). This is the first structural change of the strategy's parameter panel in the series — a different strategy or a major new version between 4/17 and 4/29.
- 198?/180?/140? boxes may hold longer values cut by the pane edge (e.g. 1980/1800/1400 — session-time-like numbers).
- Largest losing trade again ($2,600.00) — the fixed-stop signature SURVIVES the strategy revision.
- 13/0/13/30/15/0/15/30 octet looks like two time pairs (13:00-13:30? 15:00-15:30?) — time-window parameters (hypothesis).
- Max consec winners 11 (all trades) — unusually streaky week.
- Mac clock 1:15 PM vs remote Windows 1:16 PM — small clock skew visible.
Implications (hypotheses):
- If 13:0-13:30 and 15:0-15:30 are ET/CT time filters, the revised strategy adds intraday session windows; 1980/1800/1400 could be tick/point distances or ms timers.
- The 16/6/9 triplet may carry over the old 16/…/9 parameters into a new grouping.
Open questions:
- Whether a strategy name distinguishes this from the earlier one; whether 198?/180?/140? are 3- or 4-digit values.
