# OTRIMG-0134

## A FILE IDENTITY
- id: OTRIMG-0134
- filename: 20260824_172709346_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Mon Apr 13, 2:06 PM (macOS menu bar; year not shown)
- taskbar_date: 2:06 PM / 4/13/2026 (Windows taskbar inside remote session)
- social_post_date: none visible
- report_start_date: 4/5/2026
- report_end_date: 4/10/2026
- contract_date_clue: none visible
- other: macOS dock Calendar icon shows "APR 13". Captured the MONDAY after the report week ended.

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "hp", NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)". Settings pane rendered WIDER than in prior captures: first 1-2 letters of each row label and group label are now visible.

## D STRATEGY IDENTITY
- No strategy name visible. Settings pane shows label initials only (see F). "template" + "Run" at bottom.

## E DATA SERIES
- "D.." group row "I..." (Instrument) dropdown: value begins with a dark mark that could be "N" — UNREADABLE, confidence LOW.
- "P." (Price based on?) dropdown: unreadable. "T.." (Type?) dropdown: unreadable. "V." (Value?) numeric = 1 → consistent with 1-minute bars if Type=Minute (INFERRED, labeled).
- Report window: 4/5/2026 → 4/10/2026.

## F PARAMETERS (Settings pane with label initials — the decoding capture)
1. "S." numeric: 5 — last parameter of the strategy-parameters group (its label starts with S)
2. SEP — group "D.." (= Data series, INFERRED)
3. "I..." dropdown: value unreadable (possible leading "N", LOW confidence) — Instrument (INFERRED)
4. "P." dropdown: ".." unreadable — Price based on (INFERRED)
5. "T.." dropdown: "..." unreadable — Type (INFERRED)
6. "V." numeric: 1 — Value (INFERRED: 1)
7. SEP — group "T.." (= Time frame, INFERRED)
8. "S." dropdown with calendar glyph: unreadable — Start date (INFERRED)
9. "E." dropdown with calendar glyph: unreadable — End date (INFERRED)
10. "T.." dropdown: unreadable — Time zone? (INFERRED, LOW)
11. "B." bool checkbox: CHECKED — Break at EOD? (INFERRED, LOW)
12. SEP — group "S..." (= Set up, INFERRED)
13. "I..." bool checkbox: UNCHECKED — Include commission (INFERRED; matches Commission $0.00)
14. "C." dropdown: DISABLED (grayed) — Commission template (INFERRED; disabled because 13 unchecked)
15. "M" dropdown: unreadable — Maximum bars look back? (INFERRED)
16. "B." numeric: 20 — Bars required to trade? (INFERRED: 20)
17. SEP — group "H.." (= Historical fill processing, INFERRED)
18. "O." dropdown: unreadable — Order fill resolution (INFERRED)
19. "F.." bool checkbox: UNCHECKED — Fill limit orders on touch? (INFERRED)
20. "S." numeric: 0 — Slippage = 0 (INFERRED; matches Total slippage 0)
21. SEP — group "O.." (= Order handling, INFERRED)
22. "E." numeric: 2 — Entries per direction = 2 (INFERRED)
23. "E." dropdown: unreadable — Entry handling (INFERRED)
24. "E." bool checkbox: CHECKED — Exit on session close (INFERRED)
25. SEP — group "O.." (= Order properties, INFERRED)
26. "S." dropdown: unreadable — Set order quantity (INFERRED)
27. "T." dropdown: unreadable — Time in force (INFERRED)
28. italic label "template"; Button "Run"

NOTE: strategy-parameters group is scrolled out of view above except its last item ("S." = 5).

## G ENGINE SETTINGS
- Include-commission-style checkbox UNCHECKED with disabled commission dropdown; Slippage numeric 0; Exit-on-session-close-style checkbox CHECKED; Entries-per-direction-style numeric = 2. (All labels INFERRED from initials; values as visible.)

## H PERFORMANCE (Summary ($), verbatim) — LOSING WEEK
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($8,455.00) | ($695.00) | ($7,760.00) |
| Gross profit | $31,190.00 | $20,200.00 | $10,990.00 |
| Gross loss | ($39,645.00) | ($20,895.00) | ($18,750.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.79 | 0.97 | 0.59 |
| Max. drawdown | ($18,820.00) | ($10,900.00) | ($9,910.00) |
| Sharpe ratio | -1.49 | 1.54 | -1.48 |
| Sortino ratio | -4.94 | 1.00 | -4.92 |
| Ulcer index | 0.01 | 0.01 | 0.01 |
| R squared | 0.75 | 0.01 | 0.87 |
| Probability | 78.39% | 53.47% | 89.52% |
| Start date | 4/5/2026 | | |
| End date | 4/10/2026 | | |
| Total # of trades | 58 | 34 | 24 |
| Percent profitable | 36.21% | 41.18% | 29.17% |
| # of winning trades | 21 | 14 | 7 |
| # of losing trades | 37 | 20 | 17 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($145.78) | ($20.44) | ($323.33) |
| Avg. winning trade | $1,485.24 | $1,442.86 | $1,570.00 |
| Avg. losing trade | ($1,071.49) | ($1,044.75) | ($1,102.94) |
| Ratio avg. win / avg. loss | 1.39 | 1.38 | 1.42 |
| Max. consec. winners | 2 | 2 | 2 |
| Max. consec. losers | 4 | 5 | 8 |
| Largest winning trade | $7,750.00 | $7,750.00 | $3,700.00 |
| Largest losing trade | ($2,600.00) | ($2,600.00) | ($2,600.00) |
| Avg. # of trades per day | 14.00 | 8.21 | 5.79 |
| Avg. time in market | 54.09 min | 60.97 min | 44.33 min |
| Avg. bars in trade | 54.05 | 60.91 | 44.33 |
| Profit per month | ($42,979.58) | ($3,532.92) | ($39,446.67) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermarks: "rednote ID: 1384856832" (crossing the dock) + 小红书 logo.

## K FORENSIC INTERPRETATION
Direct facts:
- Week 4/5–4/10/2026 (window skips the 3/29–4/2 partial week's Friday; Good Friday 4/3 market holiday sits between). Captured Monday 4/13 2:06 PM on "hp"; U.S. keyboard active.
- KEY DECODING IMAGE: pane width finally exposes row-label initials; the group/row skeleton matches the NT8 Strategy Analyzer backtest settings grid (Data series / Time frame / Set up / Historical fill processing / Order handling / Order properties). This retroactively labels the same boxes seen in ALL other jd-series captures.
- Confirms engine config: commission unchecked (=$0), slippage 0, exit-on-session-close checked, entries-per-direction-style value = 2, "Bars required"-style value = 20, data-series Value = 1.
- Second losing week: −$8,455; shorts −$7,760 did the damage; largest loss again exactly ($2,600.00) in all columns.
- Dock shows a PDF file item; TradingView app icon present as in other captures.
Implications (hypotheses):
- Entries per direction = 2 supports the "two units, ~$1,300 stop each" reading of the recurring −$2,600 worst loss ($1,300 = 65 NQ points at $20/pt if NQ).
- Instrument dropdown's possible leading "N" weakly supports an NQ-family instrument; unconfirmed.
Open questions:
- Exact instrument, price-based-on, bar type, entry-handling and TIF values — all still unreadable.
