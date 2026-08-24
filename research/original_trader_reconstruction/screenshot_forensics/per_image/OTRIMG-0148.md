# OTRIMG-0148

## A FILE IDENTITY
- id: OTRIMG-0148
- filename: 20260824_173103492_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri May 29, 4:44 PM (macOS menu bar; year not shown)
- taskbar_date: 4:44 PM / 5/29/2026 (Windows taskbar bottom right, partially obscured by watermark)
- social_post_date: none visible
- report_start_date: 5/24/2026
- report_end_date: 5/29/2026
- contract_date_clue: none visible in this frame

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop to remote machine "hp" (NOTE: different machine than "dev"), NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)", Settings pane pinned/collapsed and cropped at right edge.

## D STRATEGY IDENTITY
- No strategy name visible. Remote machine title: "hp". Tab: "Analyzer" + "+".
- "template" label above Run button, value not visible.

## E DATA SERIES
- Not directly visible (Settings pane cropped). Avg time in market (75.87 min) == avg bars in trade (75.82, ~equal) → 1-minute bars INFERRED.

## F PARAMETERS (right-edge cropped Settings stack, top to bottom)
1. [numeric] top box cut by header — partial digit, looks like "5" (LOW confidence; by template alignment with OTRIMG-0146 likely Signal Split (Bars)=5 — INFERRED)
2. SEP (triangle + "...")
3. [unknown] empty-looking grayed box (cropped; likely Instrument cell with text cropped off — INFERRED)
4. [dropdown] "v"
5. [dropdown] "v"
6. [numeric] "1"
7. SEP (triangle + "...")
8. [date/dropdown] box with picker glyph "⋮v"
9. [date/dropdown] box with picker glyph "⋮v"
10. [dropdown] "v"
11. [bool] checkbox CHECKED
12. SEP (triangle + "...")
13. [bool] checkbox UNCHECKED
14. [dropdown] grayed/disabled "v"
15. [dropdown] "v"
16. [numeric] "20"
17. SEP (triangle + "...")
18. [dropdown] "v"
19. [bool] checkbox UNCHECKED
20. [numeric] "0"
21. SEP (triangle + "...")
22. [numeric] "2"
23. [dropdown] "v"
24. [bool] checkbox CHECKED
25. SEP (triangle + "...")
26. [dropdown] "v"
27. [dropdown] "v"
28. label "template"; [button] "Run"
- Identical stack pattern to OTRIMG-0142 → same Settings template/scroll position.

## G ENGINE SETTINGS
- Commission $0.00 (all columns); Total slippage 0. Checkbox states as in F (Include commission likely the unchecked box in group after Time frame — INFERRED by template alignment).

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $17,400.00 | $21,405.00 | ($4,005.00) |
| Gross profit | $39,155.00 | $28,180.00 | $10,975.00 |
| Gross loss | ($21,755.00) | ($6,775.00) | ($14,980.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.80 | 4.16 | 0.73 |
| Max. drawdown | ($4,890.00) | ($2,580.00) | ($7,655.00) |
| Sharpe ratio | 1.93 | 1.93 | -1.83 |
| Sortino ratio | 1.00 | 1.00 | -6.08 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.84 | 0.92 | 0.21 |
| Probability | 6.41% | 0.50% | 69.96% |
| Start date | 5/24/2026 | | |
| End date | 5/29/2026 | | |
| Total # of trades | 45 | 23 | 22 |
| Percent profitable | 42.22% | 47.83% | 36.36% |
| # of winning trades | 19 | 11 | 8 |
| # of losing trades | 25 | 11 | 14 |
| # of even trades | 1 | 1 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $386.67 | $930.65 | ($182.05) |
| Avg. winning trade | $2,060.79 | $2,561.82 | $1,371.88 |
| Avg. losing trade | ($870.20) | ($615.91) | ($1,070.00) |
| Ratio avg. win / avg. loss | 2.37 | 4.16 | 1.28 |
| Max. consec. winners | 4 | 5 | 2 |
| Max. consec. losers | 6 | 4 | 3 |
| Largest winning trade | $6,080.00 | $6,080.00 | $3,335.00 |
| Largest losing trade | ($2,600.00) | ($1,430.00) | ($2,600.00) |
| Avg. # of trades per day | 13.04 | 6.66 | 6.37 |
| Avg. time in market | 75.87 min | 95.74 min | 55.09 min |
| Avg. bars in trade | 75.82 | 95.70 | 55.05 |
| Profit per month | $106,140.00 | $130,570.50 | ($24,430.50) |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a

## K FORENSIC INTERPRETATION
- Direct facts: profitable week 5/24–5/29/2026: net +$17,400 on 45 trades, PF 1.80, driven ENTIRELY by longs (+$21,405, PF 4.16) while shorts lost −$4,005 (PF 0.73) — the recurring long/short asymmetry again.
- Machine change: title is "hp" here, vs "dev" on OTRIMG-0142/0146 → trader runs the same setup on at least two Windows machines via Jump Desktop.
- Screenshot Fri May 29 4:44 PM = report end date itself (same-day weekly review pattern).
- Windows taskbar differs from "dev": icons include File Explorer, NinjaTrader (NT), a folder, Chrome, and a pen/notes icon; dock bottom-right area shows a PDF (red Adobe-style) icon among watermark digits.
- Watermark bottom right: "rednote ID: 13?4856832" — the word "rednote" is clearly readable in this frame (Xiaohongshu/RED watermark); middle digits obscured by dock icons (LOW confidence, consistent with "1384856832"/"1334856832" seen on other frames).
- Largest losing trade −$2,600 appears again (same value in 0142 and 0146 windows) → possible fixed stop ≈ 130 NQ points at $20/pt (hypothesis).
- Hypothesis: identical cropped Settings stack as 0142 → same strategy template, same parameter values as fully-visible OTRIMG-0146 (60-min anchored VWAP family).
- Open questions: why probability row (6.41%) is so different; whether "hp" and "dev" run identical NinjaTrader installs.
