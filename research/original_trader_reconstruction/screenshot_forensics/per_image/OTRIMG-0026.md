# OTRIMG-0026

## A FILE IDENTITY
- id: OTRIMG-0026
- filename: 20260824_171615977_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: Thu Feb 27 (macOS menu bar, top right) — year not shown; time 3:15 PM
- taskbar_date: 2/27/2025 (Windows taskbar bottom right; time partially obscured by watermark)
- social_post_date: none visible
- report_start_date: 2/26/2025 (first row of Daily analysis table; also graph x-axis left label)
- report_end_date: 2/27/2025 (last row of Daily analysis table; graph x-axis right label)
- contract_date_clue: none visible (instrument dropdown cropped in the settings strip)

## C SOURCE TYPE
NT_STRATEGY_ANALYZER_ANALYSIS — Jump Desktop ("creator") showing NinjaTrader 8 Strategy Analyzer, Display = "Analysis ($)", Period = Daily, with Cumulative Net Profit graph below; Settings pane mostly cropped off the right edge (thin strip visible).

## D STRATEGY IDENTITY
- No strategy name visible.

## E DATA SERIES
- Not readable (settings strip too narrow); no instrument text visible in the analysis table.

## F PARAMETERS (right-edge Settings strip, top to bottom; only right halves of controls visible)
Toolbar row: Display [Analysis ($)]; Period [Daily]; Long/Short [All]; W/L [All]; Time base [Exit Time]; Graph [Cumulative Net Profit].
Settings strip ("Settings" header + pin icon at top):
1. SEP — group triangle (label cropped)
2. [unknown] empty-looking box (right half only)
3. [dropdown] glyph "v" (value cropped)
4. [dropdown] glyph with tiny icon + "v" (value cropped)
5. [numeric] "1"
6. [bool] unchecked
7. SEP — group triangle
8. [dropdown with small icon] (calendar-like) "v" (value cropped)
9. [dropdown with small icon] (calendar-like) "v" (value cropped)
10. [dropdown] "v" (value cropped)
11. [bool] checked
12. SEP — group triangle
13. [bool] checked
14. [dropdown] "v" (value cropped)
15. [dropdown] "v" (value cropped)
16. [numeric] "20"
17. SEP — group triangle
18. [dropdown] "v" (value cropped)
19. [bool] unchecked
20. [numeric] "0"
21. SEP — group triangle
22. [numeric] "1"
23. [dropdown] "v" (value cropped)
24. [bool] checked
25. SEP — group triangle
26. [dropdown] "v" (value cropped)
27. [dropdown] "v" (value cropped)
28. Text "template"
29. Run button (partially covered by red watermark characters)
INFERRED mapping (reason: same pane layout as OTRIMG-0024): items 2–6 ≈ Data Series (Instrument/Price based on/Type/Value=1/Tick Replay unchecked); 8–11 ≈ Time frame (Start/End date, Trading hours, Break at EOD checked); 13–16 ≈ Setup (Include commission checked, Commission template, Max bars look back, Bars required 20); 18–20 ≈ Historical fill (Order fill resolution, Fill limit unchecked, Slippage 0); 22–24 ≈ Order handling (Entries 1, Entry handling, Exit on session close checked). Items 26–27 form an additional group BELOW Order handling not present in OTRIMG-0024's pane — unexplained (possibly strategy-specific or scrolled differently).

## G ENGINE SETTINGS
- Only inferable from strip (see F): slippage-like "0", "20", Entries "1", checkboxes as listed. Values cropped, low confidence.

## H PERFORMANCE (Analysis Daily table; columns partially truncated headers)
Columns: Period | # | Cum. net p… | Net profit | Gross profit | Gross lo… | Commissi… | Cum. max. | Max. draw… | % Win | Avg. trade | Avg. winn… | Avg. loser | Lrg. winne… | Lrg. loser | MTR | Avg. MAE | Avg. MFE | Avg. ETD | % Trade
- Row 2/26/2025: # 15 | Cum. net $3,324.80 | Net $3,324.80 | Gross profit $4,889.56 | Gross loss ($1,564.? cropped) | Comm $85.20 | Cum. max. ($721.36) | Max. draw ($721.36) | % Win 53.33% | Avg. trade $221.65 | Avg. winner $611.20 | Avg. loser ($223.54) | Lrg. winner $2,089.32 | Lrg. loser ($405.68) | MTR 55.00 | Avg. MAE $190.33 | Avg. MFE $695.67 | Avg. ETD $474.01 | % Trade 14.29%
- Row 2/27/2025: # 90 | Cum. net $14,408.6? (cropped) | Net $11,083.80 | Gross profit $29,306.20 | Gross loss ($18,22?.?? cropped) | Comm $511.20 | Cum. max. ($1,872.92) | Max. draw ($1,872.92) | % Win 38.89% | Avg. trade $123.15 | Avg. winner $837.32 | Avg. loser ($331.32) | Lrg. winner $5,029.32 | Lrg. loser ($865.68) | MTR 333.00 | Avg. MAE $341.89 | Avg. MFE $716.44 | Avg. ETD $593.29 | % Trade 85.71%

## I GRAPH MORPHOLOGY
Cumulative Net Profit (green filled area), x-axis 2/26/2025 → 2/27/2025, y-axis $0–$14,000. Curve starts ≈$3,300 at the left (2/26 cumulative) and rises as a single straight segment to ≈$14,400 at 2/27 (endpoint dot at top right ~$14,000+ gridline). NOTE: with Period=Daily there are only two data points, so the perfect linearity is an artifact of interpolation between 2 daily points, not tick-level smoothness.

## J SOCIAL CONTENT
n/a — watermark only: "rednote ID: 1384856832" bottom right.

## K FORENSIC INTERPRETATION
- Direct facts: 2-day run, 2/26/2025 (15 trades, +$3,324.80) and 2/27/2025 (90 trades, +$11,083.80), cumulative ≈$14,408.60; capture on Feb 27 3:15 PM (same day as last data). 90 trades in one day is very high frequency for this strategy family. Commission $511.20 on 90 trades = $5.68/trade (matches OTRIMG-0024's $5.68 rate, not the $4.36 Lifetime rate).
- % Trade column (14.29%/85.71%) implies total trades 105 (15/105=14.29%, 90/105=85.71%) — consistent.
- Implication: same "creator" machine, next calendar day after OTRIMG-0024; the trader appears to run/backtest daily and screenshot same-day results.
- Open questions: which strategy/parameters produced 90 trades/day; whether this is the same strategy as OTRIMG-0024 (which traded ~9-18/day) with different settings, or a different strategy. The extra settings group below Order handling (items 26-27) is unexplained.
