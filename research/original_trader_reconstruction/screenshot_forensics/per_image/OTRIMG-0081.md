# OTRIMG-0081

## A FILE IDENTITY
- id: OTRIMG-0081
- filename: 20260824_171943122_iOS.jpg
- resolution: 1440 x 936

## B DATE EVIDENCE
- screen_capture_date: Fri Oct 31 (macOS menu bar "Fri Oct 31 7:49 PM")
- screen_capture_time: 7:49 PM
- taskbar_date: 10/31/2025, 7:49 PM (remote Windows taskbar) — supplies year
- social_post_date: none visible
- report_start_date: 10/26/2025
- report_end_date: 10/31/2025
- contract_date_clue: none readable (instrument box value not legible at this scroll/width)
- other date clue: macOS dock Calendar "OCT 31"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop "hp", NT8 Strategy Analyzer, Display = "Summary ($)". Settings pane scrolled to BOTTOM, exposing engine groups (Data series → Order properties).

## D STRATEGY IDENTITY
- No strategy name visible. Orange "Strategy Analyzer" tab; "Analyzer" + "+"; italic "template" footer.

## E DATA SERIES
- "D." (Data series) group visible but pane narrow: instrument value box unreadable (only left edge/possible text cursor visible); two dropdowns ". v"; numeric "1" (Value=1). Avg bars = avg minutes in report → 1-minute series.
- "T.." (Time frame): Start calendar dd, End calendar dd, dropdown ". v" (trading hours), checkbox CHECKED.

## F PARAMETERS (Settings pane top-to-bottom as visible; labels collapsed to "..")
1. Header "Settings" + pin + arrows
2. ".." numeric: "80" (last item of the U… strategy group seen in siblings)
3. SEP — group "D." (Data series)
4. ".." instrument box: value unreadable (left sliver only, possible edit cursor) [enum/unknown]
5. ".." dropdown: ". v" unreadable [enum]
6. ".." dropdown: ". v" unreadable [enum]
7. ".." numeric: "1"
8. SEP — group "T.." (Time frame)
9. ".." calendar dropdown (Start date; value not shown)
10. ".." calendar dropdown (End date; value not shown)
11. ".." dropdown: ". v" (trading hours; unreadable)
12. ".." checkbox: CHECKED (Break at EOD)
13. SEP — group "S.." (Setup)
14. ".." checkbox: UNCHECKED (Include commission OFF)
15. ".." dropdown: greyed/DISABLED (Commission)
16. ".." dropdown: ". v" (Maximum bars look back; unreadable)
17. ".." numeric: "20" (Bars required to trade — INFERRED label, NT8 default 20)
18. SEP — group "H." (Historical fill processing)
19. ".." dropdown: ". v" (Order fill resolution; unreadable)
20. ".." checkbox: UNCHECKED
21. ".." numeric: "0" (Slippage = 0)
22. SEP — group "O." (Order handling)
23. ".." numeric: "1" (Entries per direction = 1)
24. ".." dropdown: ". v" (Entry handling; unreadable)
25. ".." checkbox: CHECKED (Exit on session close — INFERRED, matches NT8 layout)
26. SEP — group "O." (Order properties)
27. ".." dropdown: ". v" (unreadable)
28. ".." dropdown: ". v" (unreadable)
29. italic "template"
30. Button "Run"

## G ENGINE SETTINGS
- Include commission ☐ (Commission dropdown disabled) → $0.00 commission in report.
- Slippage numeric 0; a fill-processing checkbox unchecked; order-fill-resolution dropdown value unreadable.
- Entries per direction 1; exit-on-session-close style checkbox CHECKED; Break-at-EOD style checkbox CHECKED.

## H PERFORMANCE (Summary ($); All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | ($3,330.00) | ($325.00) | ($3,005.00) |
| Gross profit | $19,460.00 | $11,090.00 | $8,370.00 |
| Gross loss | ($22,790.00) | ($11,415.00) | ($11,375.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 0.85 | 0.97 | 0.74 |
| Max. drawdown | ($9,740.00) | ($6,540.00) | ($6,505.00) |
| Sharpe ratio | -2.25 | -2.29 | -2.26 |
| Sortino ratio | -7.47 | -7.61 | -7.48 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.71 | 0.36 | 0.63 |
| Probability | 68.53% | 52.30% | 74.72% |
| Start date | 10/26/2025 | | |
| End date | 10/31/2025 | | |
| Total # of trades | 50 | 25 | 25 |
| Percent profitable | 34.00% | 40.00% | 28.00% |
| # of winning trades | 17 | 10 | 7 |
| # of losing trades | 33 | 15 | 18 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | ($66.60) | ($13.00) | ($120.20) |
| Avg. winning trade | $1,144.71 | $1,109.00 | $1,195.71 |
| Avg. losing trade | ($690.61) | ($761.00) | ($631.94) |
| Ratio avg. win / avg. loss | 1.66 | 1.46 | 1.89 |
| Max. consec. winners | 2 | 3 | 2 |
| Max. consec. losers | 9 | 7 | 5 |
| Largest winning trade | $2,340.00 | $2,340.00 | $1,990.00 |
| Largest losing trade | ($1,540.00) | ($1,540.00) | ($1,300.00) |
| Avg. # of trades per day | 18.11 | 9.05 | 9.05 |
| Avg. time in market | 69.52 min | 80.76 min | 58.28 min |
| Avg. bars in trade | 69.52 | 80.76 | 58.28 |
| Profit per month | ($25,391.25) | ($2,478.13) | ($22,913.13) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark present (see K).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Fourth weekly Friday run on "hp": 10/26→10/31/2025 (Halloween evening, 7:49 PM).
- LOSING week overall (−$3,330) and BOTH sides negative (long −$325, short −$3,005) — first frame in the series where longs also lose.
- Settings scrolled to bottom, exposing NT8 engine blocks: Setup (include-commission ☐, commission disabled, max-bars-lookback dd, "20"), Historical fill processing (fill-resolution dd, unchecked box, Slippage 0), Order handling ("1" entries-per-direction, entry-handling dd, checked box = exit on session close), Order properties (2 dropdowns).
- 9 consecutive losers (All) this week; trades/day 18.11.
- Background window fragment below taskbar: "-Assassin's Creed® Shadows Digital Deluxe Edition (Full Download Details ARV:" — sweepstakes/marketing email text ("ARV" = approximate retail value), i.e. a Mac email/browser window behind Jump Desktop.
- Watermark "rednote ID: 1384856832" over dock (leading digits confirmed 1-3-8 in sibling 0079).
IMPLICATIONS (hypotheses):
- Engine settings match the campaign's frozen NT8 conventions (slippage 0, exit on session close ON, entries/direction 1, no commission) — consistent template across weeks.
- The trader continued weekly evaluation despite two consecutive losing weeks (Oct 24, Oct 31) — suggests forward-testing discipline rather than curve-fit abandonment; parameters unchanged (80 still visible; other values presumably same as 0079).
OPEN QUESTIONS:
- Whether the instrument box was being edited at capture (faint cursor) or just render truncation.
