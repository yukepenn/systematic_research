# OTRIMG-0104

## A FILE IDENTITY
- image_id: OTRIMG-0104
- filename: 20260824_172500282_iOS.jpg
- resolution: 1440x936

## B DATE EVIDENCE
- screen_capture_date: Fri Jan 2, 7:50 PM (macOS menu bar)
- taskbar_date: 7:50 PM 1/2/2026 (Windows taskbar inside remote desktop) — fixes year = 2026
- social_post_date: none visible
- report_start_date: 12/28/2025
- report_end_date: 1/2/2026
- contract_date_clue: instrument dropdown shows only leading "N" (contract month/year hidden)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window titled "dev" (DIFFERENT remote machine than "hp"), NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)". Settings pane pinned slightly wider than in the "hp" captures: first letters of group headers and row labels are visible.

## D STRATEGY IDENTITY
- No strategy name visible. Analyzer tab "Analyzer" + "+". "template" link above Run.

## E DATA SERIES
- Instrument: dropdown shows RAW_VISIBLE_TEXT "N" + ▼ (rest cropped) → starts with N (NQ or MNQ family; INFERRED, letter only).
- Type: dropdown shows "M" + ▼ → Minute (INFERRED from letter + NT8 standard).
- Value: 1 → 1-minute bars (also confirmed: Avg time in market min == Avg bars in trade).
- Price based on: dropdown "..." (value truncated).
- Trading hours: dropdown "..." (value truncated). Break-at-EOD-position checkbox: checked.

## F PARAMETERS (right-edge Settings pane, top to bottom; row-label first letters visible)
1. [unknown] partial cut box at very top (above first header) — unreadable
2. SEP — group header "▼ U..." (custom group starting with U)
3. "E.." [bool] checked
4. "E.." [num] 80
5. SEP — group header "▼ D..." (INFERRED: Data series)
6. "I.." [dropdown] "N ▼" — Instrument, value starts with N
7. "P.." [dropdown] "... ▼" — Price based on, value truncated
8. "T.." [dropdown] "M ▼" — Type, value starts with M (Minute)
9. "V.." [num] 1 — Value
10. SEP — group header "▼ T..." (INFERRED: Time frame)
11. "S.." [dropdown w/ calendar icon] ▼ — Start date (value hidden)
12. "E.." [dropdown w/ calendar icon] ▼ — End date (value hidden)
13. "T.." [dropdown] "... ▼" — Trading hours (value truncated)
14. "B.." [bool] checked — Break at EOD
15. SEP — group header "▼ S..." (INFERRED: Setup)
16. "I.." [bool] UNCHECKED — Include commission (matches Commission $0.00 rows)
17. "C.." [dropdown, grayed/disabled] "... ▼" — Commission (disabled because Include commission off)
18. "M.." [dropdown] "... ▼" — Maximum bars look back
19. "B.." [num] 20 — Bars required to trade
20. SEP — group header "▼ H..." (INFERRED: Historical fill processing)
21. "O.." [dropdown] "... ▼" — Order fill resolution
22. "F.." [bool] unchecked — Fill limit orders on touch
23. "S.." [num] 0 — Slippage
24. SEP — group header "▼ O..." (INFERRED: Order handling)
25. "E.." [num] 1 — Entries per direction
26. "E.." [dropdown] "... ▼" — Entry handling
27. "E.." [bool] checked — Exit on session close
28. SEP — group header "▼ O" (next group, cut at pane bottom)
29. "template" text link
30. Run button
- NOTE: identifications after the raw letters are INFERRED from the standard NT8 strategy-settings layout; raw visible text is the letters/values quoted above. The strategy's custom numeric groups (65/30/75/... block seen on "hp" captures) are scrolled out of view above; only the tail (U-group: ✓, 80) is visible.

## G ENGINE SETTINGS
- Include commission: UNCHECKED (Commission dropdown grayed) → Commission $0.00.
- Slippage: 0. Order fill resolution: dropdown value truncated. Fill limit orders on touch: unchecked. Entries per direction: 1. Exit on session close: checked. Bars required to trade: 20.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $14,940.00 | $2,970.00 | $11,970.00 |
| Gross profit | $22,935.00 | $7,120.00 | $15,815.00 |
| Gross loss | ($7,995.00) | ($4,150.00) | ($3,845.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 2.87 | 1.72 | 4.11 |
| Max. drawdown | ($3,350.00) | ($1,545.00) | ($1,805.00) |
| Sharpe ratio | 5.92 | 5.44 | 5.81 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.87 | 0.70 | 0.87 |
| Probability | 2.51% | 22.39% | 2.93% |
| Start date | 12/28/2025 | | |
| End date | 1/2/2026 | | |
| Total # of trades | 31 | 15 | 16 |
| Percent profitable | 54.84% | 53.33% | 56.25% |
| # of winning trades | 17 | 8 | 9 |
| # of losing trades | 14 | 7 | 7 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $481.94 | $198.00 | $748.13 |
| Avg. winning trade | $1,349.12 | $890.00 | $1,757.22 |
| Avg. losing trade | ($571.07) | ($592.86) | ($549.29) |
| Ratio avg. win / avg. loss | 2.36 | 1.50 | 3.20 |
| Max. consec. winners | 5 | 2 | 3 |
| Max. consec. losers | 4 | 2 | 3 |
| Largest winning trade | $4,230.00 | $3,275.00 | $4,230.00 |
| Largest losing trade | ($1,040.00) | ($1,020.00) | ($1,040.00) |
| Avg. # of trades per day | 8.98 | 4.35 | 4.63 |
| Avg. time in market | 102.58 min | 103.60 min | 101.63 min |
| Avg. bars in trade | 102.58 | 103.60 | 101.63 |
| Profit per month | $91,134.00 | $18,117.00 | $73,017.00 |
| Max. time to recover | (row cut off by window bottom — not visible) | | |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a (watermark only)

## K FORENSIC INTERPRETATION
- Direct facts: DIFFERENT remote machine — Jump Desktop title "dev" (vs "hp" in OTRIMG-0097/0100). Report week 12/28/2025–1/2/2026, captured on end date 1/2/2026 7:50 PM. Strongly profitable week: +$14,940 on 31 trades, PF 2.87, shorts dominant (+$11,970). Commission explicitly OFF (Include-commission checkbox visibly unchecked — first direct proof of why Commission rows are $0.00 across this screenshot family). Slippage 0. Entries per direction 1, Exit on session close checked, Bars required to trade 20.
- Instrument first letter "N"; Type "M"(inute), Value 1 — first direct sight of the data-series group: 1-minute bars on an N... instrument (NQ/MNQ family most likely; hypothesis).
- This wider pane decodes the anonymous boxes of the "hp" captures: blank box = Instrument, then Price based on, Type=Minute, Value=1; calendar dropdowns = Start/End date; then Trading hours + Break at EOD ✓; then Include commission ☐ / Commission grayed / Max bars look back / Bars required 20; Historical fill processing (Order fill resolution, Fill-on-touch ☐, Slippage 0); Order handling (1, dropdown, ✓).
- Custom parameter group "U..." tail visible: checked + 80 — matches the "✓/80" block seen on hp captures → same strategy parameter template across both machines (hypothesis, strong).
- Open questions: strategy name; full instrument/contract; what "U..." group is (e.g., an enable flag + threshold 80).
