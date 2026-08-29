# G2W1 A11-BREAKOUT — full scout notes (2026-08-28)

## Method / constraints trail
- WebSearch budget was already exhausted at session start (200/200). Fell back to WebFetch on
  site-native endpoints, per constraints.
- Blocked surfaces: SSRN abstract pages (403), duckduckgo html endpoint (CAPTCHA), Mojeek (403),
  quantifiedstrategies.com (CAPTCHA), priceactionlab.com (403), mypivots dictionary (400),
  old.reddit (fetcher refuses), Bing (serves junk/generic results to the fetcher — unusable),
  tradingriot.com/market-profile (404), blog.quantinsti.com/london-breakout-strategy (404),
  axiafutures search (no results).
- Worked: concretumgroup.com (papers index + PDFs), arXiv API, quantifiableedges.com ?s= search,
  adamhgrimes.com ?s= search, traderfeed.blogspot.com native search, github.com (repo pages +
  server-side search), diva-portal.org, buildalpha.com ?s= search.
- Concretum PDFs downloaded by WebFetch as binaries; extracted locally with pypdf:
  - webfetch-1787966825288-thao51.txt = "Can Day Trading Really Be Profitable?" (18 pp)
  - webfetch-1787966827744-ia9850.txt = "Beat the Market" (43 pp)
  - webfetch-1787966829559-bzdur6.txt = "A Profitable Day Trading Strategy" (26 pp)

## Verified content extracts (key facts)

### Zarattini & Aziz — Can Day Trading Really Be Profitable? (first ver. 2023-04-24, this ver. 2025-09-22)
- 5-min ORB on QQQ, Jan 1 2016 – Feb 17 2023. Direction = direction of first 5-min candle
  (skip doji days). Stop = low(first candle) for longs / high for shorts; R = entry-stop distance;
  target 10R else exit EoD. Size = 1% account risk per trade, max 4x leverage, $25k start,
  $0.0005/share commission. Result: annualized alpha 33% net; TQQQ variant total 1,484% vs 169% QQQ B&H.
- Quote: "produced an annualized alpha of 33%".
- The later "Beat the Market" paper notes: earlier ORB papers found HIGHER Monday profitability
  (day-of-week conditioner) — intraday momentum did not show it.

### Zarattini, Barbon, Aziz — A Profitable Day Trading Strategy For The U.S. Equity Market (2024-02-16)
- 7,000+ US stocks 2016–2023, 5-min ORB (also 15/30/60-min comparison).
- Relative Volume conditioner: RVOL_t,j = OR volume today / (1/14 · sum of OR volumes prior 14 days),
  computed on the FIRST 5 MINUTES. Figure 4: average PnL (in R) of 5-min ORB grouped by OR RVOL —
  claimed increasing in RVOL. Top-20 "Stocks in Play" portfolio: >1,600% net, Sharpe 2.81, annualized alpha 36%.
- References verified from its bibliography:
  - [13] U. Holmberg, C. Lönnbark, C. Lundström, "Assessing the profitability of intraday opening
    range breakout strategies", Finance Research Letters 10:27–33, 2013. Their description: volatility
    ORB on US crude futures 1983–2011; significantly profitable but "mostly generated in the last
    decade (2000-2011)".
  - [16] C. Lundström, "Day trading returns across volatility states", Umeå Economic Studies 861,
    2013, revised 2017-03-03. Their description: ORB profitability grows with the volatility of the
    underlying asset (crude + S&P 500 futures).
  - [11] T. Crabel, "Day trading with short term price patterns and opening range breakout", 1990.
    Description in paper: Crabel "combined previous days' volatility with current opening prices.
    The strategy did not use any intraday data information to define the opening range."
  - Also cited: Connors & Raschke, Street Smarts (1995); Schulmeister (intraday shift of TA
    profitability); Tsai et al. 2018 (ORB most effective when OR length within 5 min of open);
    Wu et al. 2020 (GA-optimized ORB).

### Zarattini, Aziz, Barbon — Beat the Market (SPY intraday momentum; first ver. 2024-05-10, this ver. 2025-09-22)
- Data: SPY + VIX 1-min OHLCV from IQFeed, May 2007 – Apr 2024. Matlab.
- Noise Area: boundaries time-of-day dependent, from avg |move from open| over previous 14 days:
  move_{t-i,9:30→HH:MM} = |Close_{t-i,HH:MM}/Open_{t-i,9:30} − 1|, averaged i=1..14; band = Open·(1±avg)
  (also anchored variant to prev close). Price outside band = abnormal imbalance → trend-following
  entry; dynamic trailing stop at opposite noise boundary (weakness: trend-reversal days, e.g.
  2022-01-20 example). Results: total 1,985% net, 19.6% ann., Sharpe 1.33.
- VIX conditioner: Sharpe rises with VIX-at-open threshold (consistent with Rosa). Day-of-week:
  Monday NOT significant for this strategy (contrast with their ORB Monday effect).
- Quote: "an equilibrium zone where markets do not exhibit any exploitable intraday trend".

### Holmberg/Lönnbark/Lundström 2013 (via [13] above; journal-published, peer-reviewed)
- Volatility-scaled ORB, US crude oil futures 1983–2011; profitable; era concentration 2000–2011.

### Lundström — Day trading returns across volatility states
- DiVA record: http://www.diva-portal.org/smash/record.jsf?pid=diva2%3A732318 (Umeå, 2017; also
  IFTA Journal vol 19 pp 76–89, 2019). Fetched 2026-08-28.
- Key quantified claim: "an average difference in returns between the highest and the lowest
  volatility state of around 200 basis points per day for crude oil, and of around 150 basis points
  per day for the S&P 500."

### Quantifiable Edges (Rob Hanna)
- https://quantifiableedges.com/what-happens-when-range-rapidly-contracts/ (2008-04-15):
  WR7 (widest range of last 7, close down) followed next day by NR7 (narrowest of last 7), NDX since
  1986 → next-day avg gain ~0.6% (~10x the 0.06% unconditional daily avg), 3-day ~5x unconditional;
  "strongly bullish" short-term. Quote: "The high win rate and average win size consistently higher
  than the average loss make this setup intriguing." (N not stated on page.)
- https://quantifiableedges.com/wr7-nr7-is-back/ (2008-05-22): pattern recurrence note; "appears to
  be bullish for the Nasdaq 100".
- Inside-day studies (via ?s=inside+day, all with quantified tables per site's style):
  - "Does An Inside Day After An Outside Day Provide a Directional Edge?" (2009-12-08)
  - "Inside Days" (2010-08-19)
  - "An Unfilled Up Gap / Inside Day Pattern" (2013-09-18)
  - "Another Look At A Potentially Bearish Inside Day" (2014-01-15)
  - "Unfilled Gaps Up That Are Also Inside Days" (2014-07-20)

### TraderFeed (Brett Steenbarger) — exact post URLs verified via native search
- https://traderfeed.blogspot.com/2007/05/favorite-trading-pattern.html (2007-05-10):
  "Since 2005 in the S&P 500 Index (SPY; N = 588 trading days), we've had 81 inside days. That means
  that over 85% of the time, the market has either taken out its prior day's high, low, or both."
- https://traderfeed.blogspot.com/2007/01/price-targets-for-short-term-trades.html (2007-01-15):
  ~87% of days not inside days; >90% of HIGH VOLUME days are not inside days (volume conditioner).
- https://traderfeed.blogspot.com/2007/10/intraday-movement-in-s-500-index.html (2007-10-26):
  832 of 961 days break prior day's range.
- https://traderfeed.blogspot.com/2006/04/first-half-hour-as-volatility.html (2006-04-04):
  first 30-min |move| ≤0.05% → median daily range 0.61%, 13/33 days ≥0.70%; active open >0.05% →
  median 0.75%, 31/54 days ≥0.70%.
- https://traderfeed.blogspot.com/2009/12/trading-process-key-price-levels-and.html (2009-12-29):
  "odds are very, very high that we will take out either the overnight high or low".
- Native search page https://traderfeed.blogspot.com/search?q=opening+range (posts 2006-2008):
  valid ORBs require expanded volume + broad participation (NYSE TICK distribution, sector breadth);
  low-volume breakouts revert. Also gap stats: gaps >0.35% filled only 97/211 (<half); small gaps fill ~80%.

### Adam Grimes
- https://www.adamhgrimes.com/five-years-of-data-proving-the-real-edge-in-a-pullback-trading-tool/
  (2024-10-02): MarketLife pullback buy/sell signals, launched 2019, unchanged algorithm, 5 years
  live out-of-sample across equities → claims statistically + economically significant edge.
  Quote: "it works."

### neurotrader888 (GitHub, public code + YouTube)
- https://github.com/neurotrader888/TrendlineBreakoutMetaLabel (updated 2023-06-14, 121 stars):
  automated trendline fit (trendline_automation.py), breakout trades, meta-label filter, walk-forward
  test scripts, BTCUSDT hourly data. Video https://www.youtube.com/watch?v=jCBnbQ1PUkE
- https://github.com/neurotrader888/VolatilityHawkes (updated 2023-04-18, 69 stars): "A simple
  trading strategy based on a hawkes process applied to candle ranges." Video
  https://www.youtube.com/watch?v=wdsiZBIhAFw

### Build Alpha (Dave Bergstrom)
- https://www.buildalpha.com/opening-range-breakout/ (2026-03-27): 5 ORB variations (breakout, fade,
  S/R, HTF filter, automated discovery); conditioners recommended: OR/ATR ratio, 1-2 trades/day cap,
  200-day MA trend filter, volatility thresholds, day-of-week, forced EoD exit. No performance
  numbers published on page. Quote: "Most ORB strategies look great in backtests and fail live."

### GitHub search (server-side, verified listing)
- https://github.com/search?q=%22opening+range+breakout%22&type=repositories → 146 repos; notable:
  vedntp/pj_orb_backtester (py, 11★), adnansaify/ORB (rust, 8★),
  Mrshahidali420/ORB-Multi-Model-Indicator (Pine v6, "9 ORB models for the NY session", 13★).

## Sub-areas that yielded no verifiable lead (and why)
- London-open / overnight-range-breakout-at-London: general search engines all blocked/CAPTCHA'd for
  the fetcher; the only reachable candidate URLs 404'd (quantinsti). Nothing verifiable — not invented.
- Donchian intraday on futures: no reachable concrete-rule source (quantpedia search results not
  server-rendered; engines blocked).
- Momentum-ignition (aggressive-burst) detection: zero arXiv hits for "momentum ignition"; industry
  notes (Credit Suisse AES) not reachable without search engines. Nearest covered by Hawkes-range and
  trendline-break leads.
- Initial Balance (60-min) extension statistics: mypivots/tradingriot/axia all blocked/404/empty.
  Partial coverage via Steenbarger first-30-min volatility post + prior-day-range pierce stats.

## Independence graph (for the orchestrator)
- A11-01/02/03 same author group (Concretum/Zarattini et al.); Lundström appears in both A11-04 and
  A11-05; A11-08/09/10 all Steenbarger; A11-12/13 both neurotrader888; A11-14 vendor independent;
  A11-06/07 same blog (Hanna); A11-11 independent; A11-15 (Crabel) is the common ancestor of the
  whole ORB/NR7 genre (Hanna, Concretum, Build Alpha all cite him).
