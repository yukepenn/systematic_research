# OTRIMG-0032

## A FILE IDENTITY
- image_id: OTRIMG-0032
- filename: 20260824_171707000_iOS.png
- source path: D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\original_screenshot\20260824_171707000_iOS.png

## B DATE EVIDENCE
- screen_capture_date: none visible for the iPhone itself
- screen_capture_time: 1:17 (iPhone status bar, location arrow active)
- taskbar_date: 3/3/2025, 10:03 PM — Windows 11 taskbar clock INSIDE the embedded desktop screenshot (the post's attached image was captured on that PC at that time)
- social_post_date: 3/4/2025 (with "United States" location tag)
- report_start_date: none visible (post title implies a 2-day window ending ~3/3/2025)
- report_end_date: none visible (implied ~3/3/2025 from embedded taskbar clock)
- contract_date_clue: none visible

## C SOURCE TYPE
SOCIAL_THREAD — rednote post page showing the BOTTOM STRIP of an embedded Windows/NinjaTrader Strategy Analyzer screenshot (image 2 of 2 in carousel), plus post title, date, and both comments.

## D STRATEGY IDENTITY
- No strategy/template/account name visible. Right edge of embedded Analyzer shows an italic label "template" above a "Run" button (Strategy Analyzer right-hand settings column, mostly cropped).

## E DATA SERIES
- Instrument referenced in post title: NQ. No contract month/bar type visible in the embedded strip.

## F PARAMETERS
Right-edge settings column of embedded NT Strategy Analyzer (severely cropped, only rightmost sliver visible, top to bottom):
1. dropdown chevron [enum/dropdown] — value unreadable (cropped)
2. checkbox CHECKED [bool] — label cropped
3. "..." expander row with collapse triangle [unknown] — cropped
4. dropdown chevron [enum/dropdown] — value unreadable (cropped)
5. dropdown chevron [enum/dropdown] — value unreadable (cropped)
6. italic label "template" [dropdown label] — value cropped
7. button "Run"
- Bottom-left of embedded window: tab "Analyzer" + "+" (Strategy Analyzer tab strip)

## G ENGINE SETTINGS
- None visible.

## H PERFORMANCE (embedded Analyzer bottom rows; columns = All / Long / Short as per NT layout)
| Metric | Col1 (All) | Col2 (Long) | Col3 (Short) |
|---|---|---|---|
| Max. consec. winners | 3 | 2 | 2 |
| Max. consec. losers | 4 | 4 | 2 |
| Largest winning trade | $5,259.32 | $2,069.32 | $5,259.32 |
| Largest losing trade | ($1,435.68) | ($1,435.68) | ($1,340.68) |
| Avg. # of trades per day | 18.83 | 10.14 | 8.69 |
| Avg. time in market | 44.69 min | 56.93 min | 30.42 min |
| Avg. bars in trade | 44.69 | 56.93 | 30.42 |
| Profit per month | $65,915.38 | ($61,145.18) | $127,060.56 |
- Note: rows above "Max. consec. winners" are cut off by the phone screenshot's crop of the carousel image. Column headers not visible; All/Long/Short assignment is the standard NT order (INFERRED from layout, high confidence).
- Post title states total profit for the two days: $4672.

## I GRAPH MORPHOLOGY
- n/a

## J SOCIAL CONTENT (verbatim)
- App chrome: back chevron; avatar + "mac studio"; "Following"; share icon.
- Carousel dots: 2 dots, 2nd highlighted red (this is image 2 of 2).
- POST TITLE (AUTHOR "mac studio"): 这两天NQ交易结果，盈利$4672
- "Translate" link
- Post meta: "3/4/2025 United States" | "Dislike" button
- "2 comment(s)"
- Input row: avatar + "Share your thoughts..." + mic + image icons
- COMMENT 1 — COMMENTER "日照索隆" (avatar: blonde person holding something green): 价格行为吗，
  - date 3/4/2025 | Reply | Translate | heart (no count) | badge "First comment"
- REPLY 1a — AUTHOR (mac studio) [red "Author" badge]: 纯价格，没有成交量
  - date 3/4/2025 | Reply | Translate | heart (no count)
- "- The end -"
- Bottom bar: "Say something..." | heart "Like" (no count) | star "Save" | comment bubble 2

## Embedded desktop details (Windows taskbar inside the post image)
- Windows 11 taskbar: Start, Search box (with small image in it), Task View, File Explorer, Edge, NinjaTrader icon (orange/red "NT"-style icon), Chrome, Notepad. Tray: ^, ENG, Wi-Fi, speaker, battery/pen icon, clock "10:03 PM 3/3/2025", notification icon.
- Language: ENG. OS: Windows 11 (centered taskbar).

## K FORENSIC INTERPRETATION
- DIRECT FACTS: Post of 3/4/2025 claims two-day NQ trading profit of $4,672. Embedded Analyzer strip (screenshot taken 10:03 PM 3/3/2025 on a Windows 11 PC with NinjaTrader in the taskbar) shows the 2-day run stats: 18.83 trades/day overall, avg time in market 44.69 min, largest win $5,259.32, largest loss ($1,435.68); Long side losing (profit/month extrapolated ($61,145.18)) while Short side winning ($127,060.56). Asked if it is price action ("价格行为吗"), the author replies "纯价格，没有成交量" (pure price, no volume) — the strategy uses ONLY price data, no volume inputs.
- IMPLICATIONS: 2-day window ending 3/3/2025 was the early-March 2025 selloff; short side dominating is consistent with a trend/momentum reversal system in a down move. "Avg. bars in trade" 44.69 equals "Avg. time in market" 44.69 min in the All column, implying 1-minute bars (bars ≈ minutes; same equality holds in Long 56.93 and Short 30.42 columns) — STRONG clue the data series is 1-minute bars. ~18.8 trades/day over 2 days is far above the canonical baseline's ~5.8/day average, suggesting a high-volatility period or a different/faster variant.
- OPEN QUESTIONS: Which strategy/parameters produced this run (settings column cropped); whether "Profit per month" figures are NT's extrapolation from 2 days (almost certainly yes, INFERRED); what image 1 of the carousel shows (likely the upper half of the same Analyzer summary).
