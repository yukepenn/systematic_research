# OTRIMG-0164

## A FILE IDENTITY
- id: OTRIMG-0164
- filename: 20260824_173154534_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Aug 14, 1:47 PM (macOS menu bar; year not shown)
- taskbar_date: 1:47 PM / 8/14/2026 (Windows taskbar bottom right, partially obscured)
- social_post_date: none visible
- report_start_date: 8/2/2026
- report_end_date: 8/14/2026
- contract_date_clue: none visible

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop to "hp", NinjaTrader 8 Strategy Analyzer Summary ($); Settings pane cropped at right edge but scrolled to the TOP of the parameter list, exposing the full numeric value stack (60/5/20/95/75/50/25/5/3/10/5).

## D STRATEGY IDENTITY
- No strategy name visible. Machine "hp". Tab "Analyzer" + "+". "template" label above Run.

## E DATA SERIES
- Cropped, but by alignment with OTRIMG-0146: Data Series group visible as [Instrument box, dropdown, dropdown, "1"] → NQ 1-Minute Last INFERRED. Avg time 62.07 min == avg bars 62.06 supports 1-minute bars.

## F PARAMETERS (right-edge cropped Settings stack, top to bottom)
1. [unknown] topmost box half-cut by header — unreadable (possibly a numeric; cannot read)
2. [bool] checkbox CHECKED  ← row ABOVE Volume Base, not visible in OTRIMG-0146 (new information: at least one bool parameter precedes Volume Base)
3. [dropdown] "v" (= Volume Base by alignment — INFERRED)
4. [numeric] "60" (= Anchor Period (Minutes) — INFERRED)
5. [numeric] "5" (= VWAP Amount — INFERRED)
6. [numeric] "20" (= Trend Period — INFERRED)
7. [dropdown] "v" (= Trend MA Type — INFERRED)
8. [numeric] "95" (= Max Percent — INFERRED)
9. [numeric] "75" (= Upper Percent — INFERRED)
10. [numeric] "50" (= Median Percent — INFERRED)
11. [numeric] "25" (= Lower Percent — INFERRED)
12. [numeric] "5" (= Min Percent — INFERRED)
13. [numeric] "3" (= Signal Quantity Per Trend — INFERRED)
14. [numeric] "10" (= Signal Close Threshold (%) — INFERRED)
15. [numeric] "5" (= Signal Split (Bars) — INFERRED)
16. SEP (triangle + "...")
17. [unknown] empty-looking grayed box (Instrument cell, text cropped)
18. [dropdown] "v"
19. [dropdown] "v" (with leading dot)
20. [numeric] "1"
21. SEP (triangle + "...")
22. [date/dropdown] picker glyph "⋮v"
23. [date/dropdown] picker glyph "⋮v"
24. [dropdown] "v"
25. [bool] checkbox CHECKED
26. SEP (triangle + "...")
27. [bool] checkbox UNCHECKED
28. [dropdown] grayed/disabled "v"
29. label "template"; [button] "Run"
- RAW_VISIBLE_TEXT of numerics in order: 60, 5, 20, 95, 75, 50, 25, 5, 3, 10, 5, 1. All match OTRIMG-0146's labeled values EXACTLY → parameters unchanged from 5/23 through 8/14/2026.

## G ENGINE SETTINGS
- Commission $0.00; Total slippage 0 → zero-cost backtest. Include-commission checkbox (row 27) UNCHECKED; Commission template disabled.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $24,145.00 | $25,970.00 | ($1,825.00) |
| Gross profit | $90,410.00 | $62,585.00 | $27,825.00 |
| Gross loss | ($66,265.00) | ($36,615.00) | ($29,650.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.36 | 1.71 | 0.94 |
| Max. drawdown | ($26,730.00) | ($21,370.00) | ($9,340.00) |
| Sharpe ratio | 0.71 | 0.72 | -0.71 |
| Sortino ratio | 1.00 | 1.00 | -2.34 |
| Ulcer index | 0.01 | 0.01 | 0.01 |
| R squared | 0.00 | 0.00 | 0.32 |
| Probability | 11.96% | 7.92% | 58.98% |
| Start date | 8/2/2026 | | |
| End date | 8/14/2026 | | |
| Total # of trades | 102 | 50 | 52 |
| Percent profitable | 39.22% | 36.00% | 42.31% |
| # of winning trades | 40 | 18 | 22 |
| # of losing trades | 62 | 32 | 30 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $236.72 | $519.40 | ($35.10) |
| Avg. winning trade | $2,260.25 | $3,476.94 | $1,264.77 |
| Avg. losing trade | ($1,068.79) | ($1,144.22) | ($988.33) |
| Ratio avg. win / avg. loss | 2.11 | 3.04 | 1.28 |
| Max. consec. winners | 4 | 5 | 3 |
| Max. consec. losers | 10 | 7 | 7 |
| Largest winning trade | $13,870.00 | $13,870.00 | $5,430.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,600.00) |
| Avg. # of trades per day | 11.36 | 5.57 | 5.79 |
| Avg. time in market | 62.07 min | 83.38 min | 41.58 min |
| Avg. bars in trade | 62.06 | 83.36 | 41.58 |
| Profit per month | $56,647.88 | $60,929.62 | ($4,281.73) |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: 8/2–8/14/2026 (2 weeks), net +$24,145 on 102 trades (PF 1.36), long-dominated this time (+$25,970 vs −$1,825 short). Largest losing trade EXACTLY −$2,600 in ALL THREE columns — the strongest single confirmation of a fixed $2,600 (=130 NQ pts × $20) stop loss in the whole series (stop-size hypothesis now very strong).
- Parameter stability: exposed numeric stack 60/5/20/95/75/50/25/5/3/10/5/1 identical to OTRIMG-0146 (5/23) → the anchored-VWAP strategy ran with UNCHANGED parameters from at least 5/23/2026 to 8/14/2026; weekly runs only changed the date window.
- New template detail: a CHECKED checkbox row (plus one unreadable box) exists ABOVE Volume Base — the parameter list has at least 1–2 rows not captured in 0146's scroll position.
- 8/14/2026 is a Friday; capture 1:47 PM ET-zone-consistent — before the 4:00 close?? (If Mac clock is ET, report includes that Friday; NT "To" convention note applies.)
- Trade cadence halved vs June (11.36 trades/day vs ~20) with longer holds (62 min) — market-regime dependent behavior, parameters constant.
- Watermark "rednote ID: 1384856832" partially visible (canonical from OTRIMG-0154). Machine "hp"; dock includes Adobe PDF, green chart app, blue App-Store-like icon, iPhone-mirroring style icon; menu bar shows an additional purple/blocky icon set vs May frames.
- Open questions: identity of the checked parameter above Volume Base; the topmost cut numeric.
