# OTRIMG-0051

## A FILE IDENTITY
- id: OTRIMG-0051
- filename: 20260824_171804649_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Fri Jul 18, 2:32 PM (macOS menu bar)
- taskbar_date: 7/18/2025 2:32 PM (Windows taskbar, remote desktop)
- social_post_date: none visible
- report_start_date: 7/13/2025
- report_end_date: 7/18/2025
- contract_date_clue: none visible (Instrument dropdown shows "NQ?" cropped — see F)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window "hp", NinjaTrader Strategy Analyzer, Display = "Summary ($)". Settings pane cropped at right edge but here shows partial GROUP LABELS (more of the pane than OTRIMG-0049).

## D STRATEGY IDENTITY
- No strategy name visible. Tab "Analyzer". Settings pane bottom: italic "template" label; dark Run-type button under watermark.

## E DATA SERIES
- Instrument dropdown (label "In..."): visible value "N?" — RAW_VISIBLE_TEXT "NC/NQ" ambiguous, second glyph partially cropped; INFERRED "NQ …" (reason: NQ is the only common CME symbol starting with N with round second letter). Confidence LOW.
- "P..." (Price based on): dropdown "L..." → INFERRED "Last". Confidence MEDIUM.
- "T..." (Type): dropdown "M..." → INFERRED "Minute". Confidence MEDIUM.
- "V..." (Value): 1 → with Minute type = 1-minute bars (consistent with avg bars = avg minutes in H).
- "Tr..." (Trading hours): dropdown "<..." → INFERRED "<Use instrument settings>". Confidence LOW.
- "B..." (Break at EOD): checkbox CHECKED.

## F PARAMETERS (Settings pane, right edge, top-to-bottom; labels truncated after 1-2 chars)
1. "Q..." numeric: "1" (likely Quantity — INFERRED)
2. SEP "D..." (group: Data series — INFERRED)
3. "In..." dropdown: "N?" (see E; cropped)
4. "P..." dropdown: "L..."
5. "T..." dropdown: "M..."
6. "V..." numeric: "1"
7. SEP "Ti..." (group: Time frame — INFERRED)
8. "S..." date picker (calendar glyph), value not visible
9. "E..." date picker (calendar glyph), value not visible
10. "Tr..." dropdown: "<..."
11. "B..." checkbox: CHECKED
12. SEP "Se..." (group: Setup? — INFERRED; NT8 backtest properties group)
13. "In..." checkbox: UNCHECKED (likely "Include commission" — INFERRED; consistent with $0.00 commission)
14. "C..." dropdown: greyed/disabled, value not visible (likely "Commission" template, disabled — INFERRED)
15. "M..." dropdown: "2..." (likely "Maximum bars look back: TwoHundredFiftySix" — INFERRED)
16. "B..." numeric: "20" (likely "Bars required to trade" — INFERRED)
17. SEP "Hi..." (group: Historical fill processing — INFERRED)
18. "O..." dropdown: "S..." (likely "Order fill resolution: Standard" — INFERRED)
19. "Fi..." checkbox: UNCHECKED
20. "Sl..." numeric: "0" (Slippage — INFERRED)
21. SEP "O..." (group: Order handling — INFERRED)
22. "E..." numeric: "1" (Entries per direction — INFERRED)
23. "E..." dropdown: "A..." (Entry handling: AllEntries — INFERRED)
24. "E..." checkbox: CHECKED (Exit on session close — INFERRED)
25. SEP "O..." (group: Order properties — INFERRED)
26. "S..." dropdown: "S..." (Set order quantity: Strategy — INFERRED)
27. "Ti..." dropdown: "G..." (Time in force: GTC — INFERRED)
28. italic label "template"
29. dark button (Run-type) under watermark

## G ENGINE SETTINGS
- Include-commission-type checkbox UNCHECKED, commission dropdown disabled; Commission $0.00 in results; Slippage 0; Exit-on-session-close-type checkbox CHECKED; Break at EOD CHECKED.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $4,805.00 | $3,805.00 | $1,000.00 |
| Gross profit | $11,675.00 | $8,385.00 | $3,290.00 |
| Gross loss | ($6,870.00) | ($4,580.00) | ($2,290.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.70 | 1.83 | 1.44 |
| Max. drawdown | ($2,070.00) | ($1,650.00) | ($1,075.00) |
| Sharpe ratio | 1.57 | 1.56 | 2.32 |
| Sortino ratio | 1.00 | 1.00 | 1.00 |
| Ulcer index | 0.00 | 0.00 | 0.00 |
| R squared | 0.78 | 0.74 | 0.60 |
| Probability | 17.97% | 20.25% | 33.08% |
| Start date | 7/13/2025 | | |
| End date | 7/18/2025 | | |
| Total # of trades | 22 | 13 | 9 |
| Percent profitable | 45.45% | 46.15% | 44.44% |
| # of winning trades | 10 | 6 | 4 |
| # of losing trades | 12 | 7 | 5 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $218.41 | $292.69 | $111.11 |
| Avg. winning trade | $1,167.50 | $1,397.50 | $822.50 |
| Avg. losing trade | ($572.50) | ($654.29) | ($458.00) |
| Ratio avg. win / avg. loss | 2.04 | 2.14 | 1.80 |
| Max. consec. winners | 5 | 3 | 3 |
| Max. consec. losers | 4 | 3 | 2 |
| Largest winning trade | $3,230.00 | $3,230.00 | $2,140.00 |
| Largest losing trade | ($1,100.00) | ($1,100.00) | ($650.00) |
| Avg. # of trades per day | 5.31 | 3.14 | 3.26 |
| Avg. time in market | 136.05 min | 176.62 min | 77.44 min |
| Avg. bars in trade | 136.05 | 176.62 | 77.44 |
| Profit per month | $24,425.42 | $19,342.08 | $7,625.00 |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark bottom right: "rednote ID: 1384856???" (trailing digits cut, LOW confidence). Second faint watermark over Run button (Chinese glyphs, illegible).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Same "hp" machine via Jump Desktop; screenshot 7/18/2025 2:32 PM, report window 7/13–7/18/2025 (the week AFTER OTRIMG-0049's week). Weekly cadence of runs.
- WINNING week: net $4,805.00, PF 1.70, 22 trades, no commission.
- Settings pane confirms 1-minute-type data series (V=1, T="M...") and the standard NT8 backtest properties stack; commission unchecked; slippage 0.
- macOS browser tabs partially visible behind Jump Desktop: one tab title contains "Claude … Message Limi…" (LOW confidence), another "Learn the Latest Tech Skills…", another "7,047 unread - jsh…@Outl…" (an Outlook mailbox with 7,047 unread; account prefix appears to start "jsh"/"jsha", LOW confidence).
- Menu-bar mail-like badge shows "27" (was "24" in OTRIMG-0049).
IMPLICATIONS:
- Weekly re-test ritual on Fridays (both screenshots are Fridays at end of the report week).
- Same parameter panel structure as OTRIMG-0049 but scrolled DOWN (strategy parameters above; only last param "Q...=1" visible here).
OPEN QUESTIONS:
- Strategy name; instrument contract month; whether "Q...=1" is DefaultQuantity or a strategy parameter.
