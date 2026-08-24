# OTRIMG-0121

## A FILE IDENTITY
- id: OTRIMG-0121
- filename: 20260824_172603716_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Feb 27, 8:56 PM (macOS menu bar top right; year not shown in menu bar)
- taskbar_date: 8:56 PM / 2/27/2026 (Windows taskbar clock bottom right inside remote session)
- social_post_date: none visible
- report_start_date: 2/22/2026 (Start date row)
- report_end_date: 2/27/2026 (End date row)
- contract_date_clue: none visible (no instrument/contract shown)
- other: macOS dock Calendar icon shows "FEB 27"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — macOS Jump Desktop window titled "hp" connected to a Windows machine, NinjaTrader 8 Strategy Analyzer maximized, Display = "Summary ($)", full performance table with All/Long/Short columns, right-edge pinned Settings pane.

## D STRATEGY IDENTITY
- No strategy name, template name, or account name visible anywhere. The Analyzer left tree/toolbar is not visible (window shows only Display dropdown + table + Settings pane).
- Settings pane bottom shows italic word "template" (partially cropped label of the template control) above a "Run" button.

## E DATA SERIES
- Instrument/contract: not visible.
- Bar type/value: not visible.
- Trading hours: not visible.
- Report window: 2/22/2026 → 2/27/2026 (5 calendar days; 53 trades over it → Avg # of trades per day 12.79 implies ~4.1 trading days).

## F PARAMETERS (Settings pane, right edge, top-to-bottom; labels are cut off by window edge — only value boxes visible)
1. [partial] box bottom-edge only, cut by scroll viewport top — unreadable
2. numeric: 20 — fully visible
3. dropdown: value unreadable (glyph only)
4. numeric: 95 — fully visible
5. numeric: 75 — fully visible
6. numeric: 50 — fully visible
7. numeric: 25 — fully visible
8. numeric: 5 — fully visible
9. numeric: 3 — fully visible
10. numeric: 10 — fully visible
11. numeric: 5 — fully visible
12. SEP (collapse triangle + "...")
13. numeric/text box: EMPTY (blank)
14. dropdown: value unreadable
15. dropdown: tiny dark text at left edge of box, unreadable, then "v" glyph
16. numeric: 1 — fully visible
17. SEP (collapse triangle + "...")
18. dropdown with small colored glyph (likely color/brush picker): unreadable
19. dropdown with small colored glyph (likely color/brush picker): unreadable
20. dropdown: value unreadable
21. bool checkbox: CHECKED
22. SEP (collapse triangle + "...")
23. bool checkbox: UNCHECKED
24. dropdown: DISABLED (grayed)
25. dropdown: value unreadable
26. numeric: 20 — fully visible
27. SEP (collapse triangle + "...")
28. dropdown: value unreadable
29. italic label text: "template" (right-cropped; likely "template" label of Template row)
30. Button: "Run"

## G ENGINE SETTINGS
- Commission row in report = $0.00 (no commission applied).
- Total slippage row = 0.
- No other engine settings visible.

## H PERFORMANCE (Summary ($), verbatim)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $5,260.00 | ($5,305.00) | $10,565.00 |
| Gross profit | $32,530.00 | $11,060.00 | $21,470.00 |
| Gross loss | ($27,270.00) | ($16,365.00) | ($10,905.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.19 | 0.68 | 1.97 |
| Max. drawdown | ($13,465.00) | ($10,795.00) | ($6,530.00) |
| Sharpe ratio | 1.57 | -1.82 | 1.58 |
| Sortino ratio | 1.00 | -6.05 | 1.00 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.38 | 0.00 | 0.52 |
| Probability | 35.75% | 77.08% | 18.48% |
| Start date | 2/22/2026 | | |
| End date | 2/27/2026 | | |
| Total # of trades | 53 | 28 | 25 |
| Percent profitable | 35.85% | 28.57% | 44.00% |
| # of winning trades | 19 | 8 | 11 |
| # of losing trades | 34 | 20 | 14 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $99.25 | ($189.46) | $422.60 |
| Avg. winning trade | $1,712.11 | $1,382.50 | $1,951.82 |
| Avg. losing trade | ($802.06) | ($818.25) | ($778.93) |
| Ratio avg. win / avg. loss | 2.13 | 1.69 | 2.51 |
| Max. consec. winners | 3 | 2 | 3 |
| Max. consec. losers | 9 | 6 | 7 |
| Largest winning trade | $8,595.00 | $3,420.00 | $8,595.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($1,300.00) |
| Avg. # of trades per day | 12.79 | 8.11 | 6.04 |
| Avg. time in market | 65.21 min | 66.39 min | 63.88 min |
| Avg. bars in trade | 65.19 | 66.36 | 63.88 |
| Profit per month | $26,738.33 | ($32,360.50) | $53,705.42 |

## I GRAPH MORPHOLOGY
n/a (no graph in view)

## J SOCIAL CONTENT
n/a (no social UI). Watermarks only — see K.

## K FORENSIC INTERPRETATION
Direct facts:
- macOS Jump Desktop session titled "hp" (remote Windows machine name "hp"), menu bar shows Chinese Sogou Pinyin input (搜狗拼音) — Chinese-language user environment.
- Watermark: large gray "rednote ID: 1384856832" across the bottom, plus a 小红书 (rednote/Xiaohongshu) logo watermark — the screenshot was reposted/saved from a Xiaohongshu post by user ID 1384856832.
- Report window 2/22/2026–2/27/2026 (one trading week ending the capture day, Fri 2/27/2026); macOS clock and remote Windows taskbar clock agree (8:56 PM, 2/27/2026) — a live end-of-week run, not a stale screenshot.
- Commission = $0.00 and slippage = 0: raw-edge backtest, no friction applied.
- Settings values readable: 20, ?, 95, 75, 50, 25, 5, 3, 10, 5 | (blank), ?, ?, 1 | (styling group) | unchecked, disabled, ?, 20 | ? — a parameter stack of ~10 numerics in group 1.
- Windows taskbar shows NinjaTrader icon, Chrome, folders; macOS dock includes TradingView icon, Chrome, Mail, WeChat(?), Telegram(?), and other apps.
Implications (hypotheses):
- The 10-numeric first group (20/?/95/75/50/25/5/3/10/5) does NOT match the known SolarWave 90/179/5/10 pattern; this looks like a different (or differently-tuned) strategy — possibly thresholds (95/75/50/25/5) resembling percentile/level bands.
- Long side is strongly negative, short side strongly positive over this week — direction asymmetry consistent with a falling week.
- Largest winning trade $8,595 on a $5,260 net implies the week's profit hinged on one short trade.
Open questions:
- Which strategy? No name visible. Whether the partial top box above "20" holds another parameter.
- What instrument (dollar sizes ~ $5 gross moves per trade look like NQ-scale point values but unconfirmed).
