# OTRIMG-0049

## A FILE IDENTITY
- id: OTRIMG-0049
- filename: 20260824_171759660_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Jul 11, 5:03 PM (macOS menu bar, top right)
- taskbar_date: 7/11/2025 5:03 PM (Windows taskbar clock, bottom right of remote desktop)
- social_post_date: none visible
- report_start_date: 7/6/2025 (Strategy Analyzer "Start date" row)
- report_end_date: 7/11/2025 (Strategy Analyzer "End date" row)
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — macOS Jump Desktop window ("hp") showing NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", full three-column performance table with pinned Settings pane cropped at right edge.

## D STRATEGY IDENTITY
- No strategy name visible (Strategy Analyzer tab bar shows only "Analyzer" tab + "+"). The orange tab label reads "Strategy Analyzer".
- Settings pane bottom shows italic label "template" (value cut off / not visible) above a dark "Run"-style button partially obscured by a watermark.

## E DATA SERIES
- Instrument/contract: not visible (settings pane cropped past labels)
- Bar type/value: not visible
- Trading hours: not visible

## F PARAMETERS (Settings pane, right edge, top-to-bottom; every box half-cropped by window edge — only the leftmost part of each control is visible; labels NOT visible)
1. numeric spinbox: "5" (fully legible digit)
2. numeric spinbox: "10"
3. numeric spinbox: "10"
4. SEP (group separator triangle "▼ ...")
5. checkbox: CHECKED
6. numeric spinbox: "45?" — visible "45" + a partial rounded glyph (likely 0), cropped; RAW_VISIBLE_TEXT "45C"-like; INFERRED possibly 450 (reason: partial third glyph is round). Confidence LOW on 3rd digit.
7. numeric spinbox: "20?" — visible "20" + partial rounded glyph, cropped; INFERRED possibly 200. Confidence LOW on 3rd digit.
8. SEP (group separator triangle)
9. numeric spinbox: "65"
10. numeric spinbox: "30"
11. numeric spinbox: "65"
12. SEP (group separator triangle)
13. numeric spinbox: "1"
14. SEP (group separator triangle)
15. box: appears empty (blank field, cropped)
16. dropdown: glyph "v" visible, value unreadable
17. dropdown: glyph "v" visible, value unreadable (a small mark/period left of glyph)
18. numeric spinbox: "1"
19. SEP (group separator triangle)
20. dropdown/spin control: spinner glyph visible ("I v" style), value unreadable
21. dropdown/spin control: spinner glyph visible, value unreadable
22. dropdown: "v" glyph, value unreadable
23. checkbox: CHECKED
24. SEP (group separator triangle)
25. checkbox: UNCHECKED
26. dropdown: "v" glyph, greyed/disabled appearance, value unreadable
27. dropdown: "v" glyph, value unreadable
28. italic text label: "template" (value cropped/not visible)
29. dark button (Run-type), overlapped by semi-transparent watermark glyphs (appears Chinese, illegible)

## G ENGINE SETTINGS
- Commission row in results: $0.00 (all columns) — indicates commission NOT configured for this run.
- Total slippage: 0. No other engine settings visible (settings labels cropped).

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($7,475.00) | ($5,960.00) | ($1,515.00) |
| Gross profit | $6,775.00 | $2,055.00 | $4,720.00 |
| Gross loss | ($14,250.00) | ($8,015.00) | ($6,235.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.48 | 0.26 | 0.76 |
| Max. drawdown | ($7,785.00) | ($5,960.00) | ($3,010.00) |
| Sharpe ratio | -1.48 | -1.78 | -1.52 |
| Sortino ratio | -4.92 | -5.90 | -5.05 |
| Ulcer index | 0.01 | 0.01 | 0.00 |
| R squared | 0.64 | 0.80 | 0.04 |
| Probability | 96.23% | 98.47% | 69.29% |
| Start date | 7/6/2025 | | |
| End date | 7/11/2025 | | |
| Total # of trades | 29 | 14 | 15 |
| Percent profitable | 24.14% | 14.29% | 33.33% |
| # of winning trades | 7 | 2 | 5 |
| # of losing trades | 22 | 12 | 10 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($257.76) | ($425.71) | ($101.00) |
| Avg. winning trade | $967.86 | $1,027.50 | $944.00 |
| Avg. losing trade | ($647.73) | ($667.92) | ($623.50) |
| Ratio avg. win / avg. loss | 1.49 | 1.54 | 1.51 |
| Max. consec. winners | 1 | 1 | 1 |
| Max. consec. losers | 8 | 6 | 4 |
| Largest winning trade | $1,505.00 | $1,490.00 | $1,505.00 |
| Largest losing trade | ($1,140.00) | ($1,140.00) | ($995.00) |
| Avg. # of trades per day | 7.00 | 4.06 | 3.62 |
| Avg. time in market | 111.59 min | 119.50 min | 104.20 min |
| Avg. bars in trade | 111.59 | 119.50 | 104.20 |
| Profit per month | ($37,997.92) | ($36,356.00) | ($7,701.25) |

## I GRAPH MORPHOLOGY
n/a (no graph in view)

## J SOCIAL CONTENT
n/a. Watermark text (bottom right, semi-transparent, partially cropped): "rednote ID: 1384856???" — visible "rednote ID: 13848568??", trailing digits cut/blurred, LOW confidence past "1384856". A second faint watermark overlaps the Run button (appears to contain Chinese glyphs, illegible).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Remote machine name (Jump Desktop window title): "hp". macOS host, Jump Desktop client.
- 1-week backtest window 7/6/2025–7/11/2025; screenshot taken same day as report end (7/11/2025 5:03 PM both clocks).
- Strongly LOSING run: net ($7,475.00), PF 0.48, 29 trades, zero commission configured.
- Avg. bars in trade = avg. time in market in minutes (111.59) → 1-minute bars (each bar = 1 minute). INFERRED, reason: exact numeric equality of bars and minutes in all three columns.
- Settings numeric stack begins 5/10/10 then checked-box, 45?/20?, then 65/30/65, then 1 — a distinctive parameter fingerprint.
- Windows taskbar shows NinjaTrader icon, Chrome, Edge, Excel-like icon, Notepad-like icon; background email window edge ("Inbox…") bottom-left.
- Watermark "rednote ID: 1384856???" ties the screenshot to a Xiaohongshu (rednote) account.
IMPLICATIONS:
- This looks like a live/forward-week test or a recent-week backtest evaluated the same day it ended.
- The 65/30/65 pattern is consistent with an oscillator-style threshold triple (e.g., overbought/oversold levels); HYPOTHESIS only.
OPEN QUESTIONS:
- Which strategy/template produced this run (no name visible)?
- Full values of cropped 45?/20? boxes and all dropdown values.
