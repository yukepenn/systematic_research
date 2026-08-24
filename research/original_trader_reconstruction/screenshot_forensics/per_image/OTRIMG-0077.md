# OTRIMG-0077

## A FILE IDENTITY
- id: OTRIMG-0077
- filename: 20260824_171931864_iOS.jpg
- resolution: 1440 x 936

## B DATE EVIDENCE
- screen_capture_date: Fri Oct 17 (macOS menu bar "Fri Oct 17 5:42 PM"; year not shown)
- screen_capture_time: 5:42 PM
- taskbar_date: 10/17/2025, 5:42 PM (remote Windows taskbar) — supplies year
- social_post_date: none visible
- report_start_date: 10/12/2025
- report_end_date: 10/17/2025
- contract_date_clue: Instrument dropdown in Settings shows "N(" (right-cropped; reads as start of "NQ …" — contract month not visible)
- other date clue: macOS dock Calendar icon "OCT 17"

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_SUMMARY — Jump Desktop window titled "dev" (DIFFERENT remote machine than the "hp" of earlier images), NinjaTrader 8 Strategy Analyzer, Display = "Summary ($)". Settings pane slightly wider here: truncated parameter LABELS are visible.

## D STRATEGY IDENTITY
- No strategy name visible. Orange "Strategy Analyzer" tab; bottom tab "Analyzer" + "+". Italic "template" at Settings footer.

## E DATA SERIES (from Settings pane "D…" group — Data series)
- I… (Instrument): dropdown value "N(" → visibly begins "N" + rounded glyph, consistent with "NQ …" (right-cropped; INFERRED NQ, reason: glyph shape + campaign context) [LOW on full value]
- P… (Price based on): dropdown "L.." → consistent with "Last" (cropped)
- T… (Type): dropdown "M." → consistent with "Minute" (cropped)
- V… (Value): numeric "1"
- Ti… (Time frame) group: S… (Start date) calendar dropdown, E… (End date) calendar dropdown, T… (Trading hours?) dropdown "<.." (consistent with "<Use instrument settings>"), B… (Break at EOD?) CHECKED
- → 1-minute series; Avg. bars = Avg. time in minutes in the report confirms 1-min bars.

## F PARAMETERS (right-edge pinned Settings pane, top to bottom, truncated labels verbatim)
1. Header: "Settings" + pin + scroll arrows
2. "E…" checkbox: CHECKED
3. "D…" numeric: "4500" [full — resolves the "450?" crops of sibling images]
4. "M…" numeric: "2000" [full — resolves "200?"]
5. SEP — group header "St…"
6. "I…" numeric: "65"
7. "T…" numeric: "30"
8. "I…" numeric: "65"
9. "M…" numeric: "20"
10. SEP — group header "Tr…"
11. "Q…" numeric: "1"
12. SEP — group header "U…"
13. "E…" checkbox: CHECKED
14. "E…" numeric: "80"
15. SEP — group header "D…" (Data series)
16. "I…" dropdown: "N(" (cropped; likely NQ…)
17. "P…" dropdown: "L.." (likely Last)
18. "T…" dropdown: "M." (likely Minute)
19. "V…" numeric: "1"
20. SEP — group header "Ti…" (Time frame)
21. "S…" calendar dropdown (value not visible)
22. "E…" calendar dropdown (value not visible)
23. "T…" dropdown: "<.." (likely <Use instrument settings>)
24. "B…" checkbox: CHECKED
25. SEP — group header "Se…" (Setup?)
26. "I…" checkbox: UNCHECKED (likely Include commission = OFF)
27. "C…" dropdown: DISABLED/greyed, empty (likely Commission, disabled because I… unchecked)
28. "M…" dropdown: "2.." (likely Maximum bars look back = 256)
29. "P…"/"R…" numeric (label glyph unclear): "20" bottom-cropped ["20?" LOW]
30. italic "template" (cropped)
31. Button: "Run"

## G ENGINE SETTINGS
- Include commission checkbox UNCHECKED, Commission dropdown greyed → commission intentionally OFF (report Commission $0.00).
- Total slippage 0. Trading hours dropdown "<.." (default instrument settings). "B…" (Break at EOD) checked.

## H PERFORMANCE (Summary ($); All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $11,105.00 | $11,585.00 | ($480.00) |
| Gross profit | $46,550.00 | $26,330.00 | $20,220.00 |
| Gross loss | ($35,445.00) | ($14,745.00) | ($20,700.00) |
| Commission | $0.00 | $0.00 | $0.00 |
| Profit factor | 1.31 | 1.79 | 0.98 |
| Max. drawdown | ($11,070.00) | ($5,315.00) | ($6,230.00) |
| Sharpe ratio | 1.61 | 1.61 | -1.83 |
| Sortino ratio | 1.00 | 1.00 | -6.08 |
| Ulcer index | 0.01 | 0.00 | 0.01 |
| R squared | 0.32 | 0.58 | 0.02 |
| Probability | 16.71% | 7.55% | 52.45% |
| Start date | 10/12/2025 | | |
| End date | 10/17/2025 | | |
| Total # of trades | 83 | 42 | 41 |
| Percent profitable | 40.96% | 45.24% | 36.59% |
| # of winning trades | 34 | 19 | 15 |
| # of losing trades | 49 | 23 | 26 |
| # of even trades | 0 | 0 | 0 |
| Total slippage | 0 | 0 | 0 |
| Avg. trade | $133.80 | $275.83 | ($11.71) |
| Avg. winning trade | $1,369.12 | $1,385.79 | $1,348.00 |
| Avg. losing trade | ($723.37) | ($641.09) | ($796.15) |
| Ratio avg. win / avg. loss | 1.89 | 2.16 | 1.69 |
| Max. consec. winners | 6 | 3 | 3 |
| Max. consec. losers | 10 | 5 | 6 |
| Largest winning trade | $4,040.00 | $3,730.00 | $4,040.00 |
| Largest losing trade | ($1,300.00) | ($1,295.00) | ($1,300.00) |
| Avg. # of trades per day | 20.04 | 10.14 | 11.88 |
| Avg. time in market | 41.76 min | 49.98 min | 33.34 min |
| Avg. bars in trade | 41.76 | 49.98 | 33.34 |
| Profit per month | $56,450.42 | $58,890.42 | ($2,928.00) |

## I GRAPH MORPHOLOGY
n/a

## J SOCIAL CONTENT
n/a. Watermark present (see K).

## K FORENSIC INTERPRETATION
DIRECT FACTS:
- Remote machine name is "dev" — a SECOND machine distinct from "hp" (OTRIMG-0073/0075). Its Windows taskbar has a different, smaller icon set (Start, Search, widget, folder, NinjaTrader, Chrome, Edge, Notepad) and includes Microsoft Edge which the "hp" taskbar did not show.
- Weekly Friday-evening run again: 10/12/2025 → 10/17/2025.
- Settings labels visible (truncated): confirms group structure and RESOLVES cropped values from sibling images: D…=4500, M…=2000 (previously read as 450?/200?).
- Strategy user parameters: E[✓], D=4500, M=2000 | St: I=65, T=30, I=65, M=20 | Tr: Q=1 | U: E[✓], E=80 — identical values to OTRIMG-0075 (Oct 10, machine hp), i.e. both machines run the same strategy version/params.
- Data series group: Instrument starts with "N", price "L..", type "M.", value 1 → NQ, Last, 1 Minute (inference from truncations, consistent with campaign).
- Include-commission unchecked with greyed commission dropdown — commission deliberately excluded.
- Trade count 83 in the week (20.04/day), double the prior week's 38, holding time halved (41.76 min avg) — same params, more volatile week.
- Shorts roughly flat (net −$480, PF 0.98); longs made all profit ($11,585).
- Red/orange active-microphone indicator in macOS menu bar again; WeChat badge "1".
- Watermark over dock: "ednote ID: 4384856832" (leading letters cropped; INFERRED "rednote ID:"; first digit 4 vs 1 LOW). Faint white watermark ("小红书"-style) also overlaps the remote taskbar clock area.
IMPLICATIONS (hypotheses):
- Trader operates at least two NT8 machines ("hp", "dev") with the same strategy and identical parameter template; both accessed from the same Mac via Jump Desktop.
- The "Se…" group behavior (unchecked include-commission disabling the commission dropdown) matches NT8 Strategy Analyzer's Setup block — reinforces this is stock NT8 Analyzer, no custom skin.
OPEN QUESTIONS:
- Exact instrument contract month; exact label words behind the truncations (St…, Tr…, U…).
- Bottom "20" row's label (Bars required to trade?).
