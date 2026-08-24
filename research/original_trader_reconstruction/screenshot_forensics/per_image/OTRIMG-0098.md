# OTRIMG-0098

## A FILE IDENTITY
- image_id: OTRIMG-0098
- filename: 20260824_172433000_iOS.png
- source path: D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\original_screenshot\20260824_172433000_iOS.png

## B DATE EVIDENCE
- screen_capture_date: none visible
- screen_capture_time: 1:24 (iPhone status bar, location arrow active)
- taskbar_date: none visible
- social_post_date: 12/19/2025 (with "United States" location tag)
- report_start_date: 12月14日 (Dec 14, from post title — trading-result window start)
- report_end_date: 12月19日 (Dec 19, from post title — trading-result window end)
- contract_date_clue: none visible

## C SOURCE TYPE
SOCIAL_THREAD — rednote post page (title + full 4-comment thread). Contains the pivotal commission-methodology admission by the author.

## D STRATEGY IDENTITY
- None by name. Author states he runs SEVERAL strategies simultaneously ("同时run了几个strategy").

## E DATA SERIES
- Instrument: NQ (from post title). Nothing else visible.

## F PARAMETERS
- n/a

## G ENGINE SETTINGS (as stated verbally by author)
- Posted Strategy Analyzer reports use commission = 0 (he must manually select a commission rate each time and skipped it from the very first post onward).
- Real commission: "大约是$2一个来回" (about $2 per round turn).
- Slippage exists in live trading; author's rule of thumb: actual profits ≈ 0.9× posted, actual losses ≈ 1.1× posted.

## H PERFORMANCE
- Post title: profit $1245 for NQ trading 12/14–12/19 (2025).

## I GRAPH MORPHOLOGY
- n/a

## J SOCIAL CONTENT (verbatim)
- App chrome: back chevron; avatar + "mac studio"; "Following"; share icon.
- POST TITLE (AUTHOR "mac studio"): 12月14日至12月19日，NQ交易结果，盈利$1245
- "Translate" link
- Post meta: "12/19/2025 United States" | "Dislike" button
- "4 comment(s)"
- Input row: avatar + "Share your thoughts..." + mic + image icons
- COMMENT 1 — COMMENTER "小皮球" (avatar: brown poodle/toy dog): Commission 0?　其他的就不问了、 就想问佣金0怎么做到的 很神奇
  - date 12/20/2025 | Reply | Translate | heart (no count)
- REPLY 1a — AUTHOR (mac studio) [red "Author" badge]: 同时run了几个strategy，所以只有通过strategy analyzer来分析单个strategy performance, 每次都要手动选择commission rate, 大约是$2一个来回, 另外还有slippage, 所以实际上的盈利是贴出来的 0.9左右，亏损是1.1左右。
  - date 12/20/2025 | Reply | Translate | heart (no count)
- REPLY 1b — COMMENTER "小皮球": Reply mac studio: 谢谢回复
  - date 12/21/2025 | Reply | Translate | heart (no count)
- REPLY 1c — AUTHOR (mac studio) [red "Author" badge]: Reply 小皮球: 你是第一个发现这个问题的，当时第一次贴的时候，偷懒了一下，所以就一直懒下去了。
  - date 12/21/2025 | Reply | Translate | heart (no count)
- "—— Hide"
- "- The end -"
- Bottom bar: "Say something..." | heart 7 | star "Save" | comment bubble 4

## K FORENSIC INTERPRETATION
- DIRECT FACTS: (1) Author runs MULTIPLE strategies live at the same time; the weekly "trading result" posts are produced by re-running each strategy in NinjaTrader Strategy Analyzer to isolate per-strategy performance. (2) ALL his posted Analyzer reports use commission = 0 — he admits he skipped selecting the commission template from the first post and never fixed it ("你是第一个发现这个问题的...偷懒了...一直懒下去了"). (3) His real commission is ~$2 per round turn; with slippage, real profit ≈ 0.9× posted, real loss ≈ 1.1× posted. (4) Weekly result 12/14–12/19/2025: +$1,245 on NQ.
- IMPLICATIONS: CRITICAL for reconstruction parity — every performance screenshot in this corpus should be matched with COMMISSION = $0, not the NinjaTrader Lifetime $4.36/RT template. The "$2 per round turn" figure is the author's own approximation of his actual cost (NT lifetime NQ commission is $2.18/side = $4.36/RT; his "$2/round turn" may be loose recollection or a different plan — do NOT treat as exact). Also confirms the posted reports are BACKTEST/Analyzer re-runs of live-traded strategies, so posted trade lists may differ slightly from live fills (slippage excluded).
- OPEN QUESTIONS: Whether "$2一个来回" means per-side or per-round-turn (he says 来回 = round trip; taken verbatim); which/how many strategies are running concurrently; whether $1245 is the Analyzer zero-commission figure (by his own admission, yes — INFERRED).
