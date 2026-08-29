# G2W1 A9-PROFILE — Market Profile / Auction Scout — Full Notes
Date: 2026-08-28. Agent: A9-PROFILE, GENESIS II WORLD DISCOVERY WAVE 1.

## Method / access log
- WebSearch budget was EXHAUSTED (200/200) before this agent ran a single query. Fell back to
  WebFetch on site-native search/browse/API endpoints per constraints.
- BLOCKED routes (all attempted, all failed): DuckDuckGo html+lite (CAPTCHA), Bing (served canned
  generic results ignoring query, HTML and RSS), Mojeek 403, Ecosia 403, searx.be CAPTCHA,
  Marginalia (redirect → docs page, query param not honored), Yep 403, medium.com/search 403,
  futures.io 403 (entire site), reddit.com blocked by infra, web.archive.org blocked by infra,
  api.stackexchange.com blocked by infra, api.semanticscholar.org 429 twice, shadowtrader.net
  (301 → .com with bad cert), quantifiedstrategies.com bot-gate, elitetrader.com/et/tags 403,
  cisco-futures.com dead (ECONNREFUSED), sierrachart.com TPO doc URLs 404/timeout,
  atas.net /?s= search broken (only sitemap worked), claude-in-chrome not connected.
- WORKING routes: Blogspot native search (traderfeed, quantifiableedges), WordPress ?s= on some
  sites (optimusfutures, jigsawtrading, axiafutures, cxoadvisory, convergenttrading), Yoast
  sitemaps (atas.net), api.github.com repo search, archive.org advancedsearch JSON + item pages,
  Wikipedia, TradingView script/tag pages (marketprofile, initialbalance, singleprints, npoc,
  poorhigh), mypivots.com dictionary, nqstats.com (fully open static stat pages), windotrader.com.
- futures.io is almost certainly the richest MP-stats venue and is hard-403'd to this fetcher;
  flag for a browser-equipped wave.

## Sources actually visited + what they yielded

### nqstats.com (single best find; free, static, 10yr NQ 2016–2025, ~2,500 sessions; all pages fetched 2026-08-28)
- /ib_breaks.html — N=2,571; IB=09:30–10:30 ET; breach = wick ≥1 tick beyond level.
  Either side breached by noon 82.5%, by 16:00 close 96.1%. High by close 62.9%, low 54.9%.
  IB close above midpoint (54.6% of days): IB-high breach 70.1% by noon / 82.3% by close.
  IB close below midpoint: IB-low breach 65.8% / 76.5%.
  Low-set-first→high-last: high breach 68.2%/80.9%. High-first: low breach 57.8%/71.2%.
  Combined (close>mid + low first, N=1,114): high breach 74.0% noon / 84.0% close.
  Combined (close<mid + high first, N=974): low breach 67.9% / 78.0%.
- /rth_breaks.html — N=2,488. Open location vs prior RTH range:
  Gap up above pRTH-high 26.3% of days → closes above pRTH-high 69.9%; never touches pRTH-low 88.1%.
  Gap down below pRTH-low 14.6% → closes below 59.5%; avoids pRTH-high 90.4%.
  Inside open 59.1% → one-side-only breach 74.0%; BOTH sides 8.3%; neither 17.7%.
- /aln_sessions.html — N=2,542. Asia 20:00–02:00, London 02:00–08:00, NY 08:00–16:00 ET.
  P1 London engulfs Asia 22.0% → London H broken 71.5% / L 70.4% / both 42.5% ("coin flip").
  P2 Asia engulfs London 6.9% → H 81.1% / L 74.9% / both 56.0% / neither 0.
  P3 partial engulf up 41.0% → H 80.8% / L 65.5%; neither 1.2%.
  P4 partial engulf down 30.2% → L 75.0% / H 68.6%; neither 1.0%.
- /noon_curve.html — N=2,479, 08:00–16:00 TBR split at noon.
  Day's two extremes on opposite sides of noon 72.81%; both in AM 21.82%; both in PM 5.37%.
  AM extremes mean formation 10:12 (σ=72min); PM 14:04 (σ=88min).
  If Q2 (10–12) breaks Q1 high (44% of opposite-side days): AM-low/PM-high configuration 82.12%.
  If Q2 breaks Q1 low (35%): AM-high/PM-low 72.42%.
- /am_tbr.html — N=2,572. ±0.25·σ20 band from 08:00 open, window 08:00–12:00.
  Touch rate 98.95%. Reversion to open after touch ~74.3% overall.
  By touch time: 08:00–08:29 ~83%; 09:30–09:59 ~69%; 10:00–10:59 40%; 11:00+ ~9%.
  Non-reverted MAE mean +1.62σ / −2.01σ. MFE after reversion ~0.8–0.9σ opposite side.
- /1h_continuation.html — methodology page fetched; numbers are JS-populated placeholders, not
  extracted. 6PM-hour and 9AM-hour direction → session-close continuation framework.

### mypivots.com Day Trading Dictionary
- /dictionary/definition/25/80-rule — THE 80% Rule stated concretely: open (or move) outside VA,
  then back inside for two consecutive 30-min bars (first closes inside, second opens inside) →
  "high probability of completely filling the value area"; entry itself reports an informal test:
  succeeds "only about 60% of the time" on ES — "should be called the 60% rule".
- /dictionary/definition/220/value-area-va — VA defined as 1σ around most-traded price; TPO/half
  hour letter construction; claim: VAH intraday resistance / VAL support "more likely... when the
  market opens inside the value area".
- Open-type entries exist (Open Drive item 757, Open Test Drive 758, Open Rejection Reverse 759,
  OAIR 760, OAOOR 761) under /dictionary/browse/o.

### TraderFeed (Brett Steenbarger, PhD — blogspot, quantified studies, 2006–2009 era)
- /2007/10/opening-price-gaps-and-reversions-to.html — SPY since 2004, N=962: opening gap closed
  same day 70% (696/962); gaps <0.35% fill ~80%; >0.35% fill <50%; <0.10% fill 90%+.
- /2006/11/do-opening-gaps-tend-to-fill.html — gaps >40% of prior day range: ~50% fail to fill
  same day (N=180 since May 2003); small gaps <40% of range fill 80–90%; large gaps bullish
  next-day bias +0.18% avg.
- /2006/08/opening-gaps-in-sp-500-index-part-one.html — N=2,375 from Mar 1997; median gap 0.29%;
  ~75% of days eventually filled; gap size scales with VIX.
- /2006/08/opening-gaps-in-sp-500-index-part-two.html — down gaps ≤−0.50%: +0.43% avg open-to-close
  (N=123 since Mar 1996), next-day +0.66%.
- Also: /2009/05/large-opening-gaps-to-upside-what-comes.html (N=74: +0.47% O-C),
  /2007/07/when-markets-gap-down-what-happens-next.html (N=45 weak opens: −0.19% avg, 31/45
  extended −0.30%), /2007/01/trading-opening-gaps-to-upside.html, /2009/05/what-we-can-learn-from-
  large-and-small.html (gap size corr 0.30 with day's relative range; large gaps → 138% of avg range).
- /2007/07/stock-market-reversals-gravitational.html — checked: conceptual only, VA = "region in
  which 2/3 of all volume has been transacted"; no stats. Not used as a stat lead.

### Quantifiable Edges (Rob Hanna — blogspot)
- /2008/04/mid-sized-gaps-up.html — SPY 1993-11-17→2008-04-16 (3,626 days). Mid gaps 0.25–0.75%:
  uptrend N=613, fill 58% (356/613), ~breakeven O-C; downtrend N=223, fill 73% (165/223), avg
  −0.3% O-C (long); "mid-sized gaps are a different animal".
- /2008/04/mid-sized-gaps-down.html (companion), /2009/01/when-market-gaps-up-continues-higher.html
  (large unfilled up-gaps: ~70% closed below trigger within 3 days), /2013/04/the-impact-of-
  breakaway-gap.html, /2013/03/large-gaps-down-when-market-was-near.html — permalinks captured.

### TradingView script pages (rules stated in descriptions; unaudited)
- /script/mtbb3Y9x-Initial-Balance-Breaks-NQ-stats-x-CantoLab/ — quotes nqstats numbers: IB breaks
  83% before noon, 96% by 16:00; IB close upper half → high breaks 82%; lower half → low 76%;
  "10 years of NQ data"; explicitly credits nqstats.com. Derivative of nqstats (independence note).
- /script/xB4JV02s-Nick-s-IB-Break-Extension-Retest-v3/ — NickMcD, 12-year NQ IB study "per
  TradingStats research"; tracks post-10:30 IB breaks, extensions 1.1×–1.5× of IB range, retests;
  displays "historical continuation base rate for the extension that was reached"; author caveat:
  reach/continuation rates, not win rates.
- /script/e6y9zmfW-TPO-Levels-VAH-POC-VAL-with-Poor-H-L-Single-Prints-NPOCs/ — benb1122. Poor
  H/L = flat extreme with ≥2 TPOs at extreme price; claim: poor structure "often signal a high
  probability that price will eventually break that high or low". No repair-rate numbers.
- /script/aXGqvR8l-TPO-Single-Prints-nPOC/ — jxriedel; single prints & naked POC "price magnets
  that may get 'filled'"; no numbers.
- /script/WPtTm8fg-IB-ORB-Statistical-Mapper-hardcoded/ + /script/4NCjPLzS-IB-ORB-Live-Stats/
  (lucymatos) — formed-first vs broke-first cross-tabs; /script/R0XeM5sL-Smooths-IB-Map/.
- Tag pages used: /scripts/marketprofile/, /scripts/initialbalance/, /scripts/singleprints/,
  /scripts/npoc/, /scripts/poorhigh/.

### ATAS blog
- /blog/analyzing-tpo-5-important-elements-in-jim-daltons-opinion/ — Danil Solovyov, 2020-07-23.
  Dalton-derived qualitative claims: (1) overlapping bell-shaped VAs = balance = accumulation zone;
  (2) POC migration = S/R + price attractor; (3) single prints mark acceleration, trend intact
  while "not erased"; (4) every completed session should have excess (tails) both ends, missing
  tail = incomplete auction; (5) spikes/ledges act as S/R. No percentages.

### WindoTrader (MP-specialist vendor)
- /market-profile/market-profile-glossary-index/ — glossary: VA = "first standard deviation…
  approximately 68%"; IB = first hour; Part-02 open types (Open-Drive, Open Test-Drive, Open
  Rejection-Reverse, OAIR, OAOOR); Part-03 day types (Normal, Normal-Variation, Neutral,
  Non-Trend, Trend, Trend Multi-Distribution). No 80% rule, no poor-H/L entries.

### Books verified on archive.org (citable primary Dalton/Steidlmayer material)
- archive.org/details/isbn_9780934380539 — Dalton, "Mind Over Markets" (1999 ed.) — day types,
  open types, value-area rule origin.
- archive.org/details/steidlmayeronmar0000stei — Steidlmayer & Hawkins, "Steidlmayer on Markets:
  Trading with Market Profile" (Wiley 2003, ISBN 0471215562).

### Wikipedia
- en.wikipedia.org/wiki/Market_profile — VA = central 70% of activity ±1σ around POC; day-type
  counts (3 → 4 types; Mind Over Markets lists 9); IB = first hour; references to dead
  cisco-futures.com pages (Steidlmayer's data firm) only via web.archive (blocked to this fetcher).

### GitHub (api.github.com repo search)
- bfolkens/py-market-profile — 404★ Python, "calculate Market Profile (aka Volume Profile)…from a
  Pandas DataFrame", updated 2026-08-25.
- EarnForex/MarketProfile — 197★ MQL4/5/cTrader MP indicator, updated 2026-08-26.

## Cross-checks / independence map
- nqstats.com is ONE author/site; its 5 stat pages are a correlated family; CantoLab TV script is
  a straight copy of it; NickMcD cites "TradingStats" (possibly same family). Treat all IB-break
  numbers as one source until replicated.
- Steenbarger and Hanna are independent of each other and of nqstats; both are SPY-era-1
  (1993–2009), so era-2 replication on NQ is genuinely out-of-sample in both instrument and time.
- Dalton/Steidlmayer books, WindoTrader, ATAS, mypivots all descend from the same CBOT teaching
  lineage — their CLAIMS are not independent, only their test results would be.
- The mypivots 80%-rule entry is the only place found that both states the rule mechanically AND
  reports a test (~60% on ES, no code shown).

## Gaps / what I could not get
- futures.io thread stats (FT71 value-area studies, IB threads) — 403.
- No peer-reviewed test of any MP construct located via reachable routes (Semantic Scholar 429,
  SSRN/scholar unreachable). arXiv API untried for q-fin MP terms — candidate for next wave.
- Poor-high repair RATES and single-print revisit RATES exist nowhere reachable as numbers — all
  sources state the claim qualitatively. These two are pure falsifier opportunities: we would be
  producing the first numbers we've seen.
- eminiplayer.net open-type stats (open in/above/below value → day odds) — site dead, archive
  blocked. The RTH-breaks page of nqstats is the closest live equivalent.
