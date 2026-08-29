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

---------------------------------------------------------------------------------------------------
# SECOND PASS (same day, 2026-08-28) — additional verified sources
The gaps flagged above (London-open breakout, IB/session stats, momentum ignition, NQ-specific
cost-aware falsification, breakout-pullback on NQ) were CLOSED this pass via different fetch routes.

### arXiv 2605.04004v2 — Mesfin, "Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures:
### A Systematic Falsification Study" (v1 2026-05-05, v2 2026-07-13). PDF extracted locally.
- MNQ 5-min RTH (aggregated from NinjaTrader 1-min), Dec 2021–Aug 2025, 947 days; fixed 2.0-pt RT
  friction; gates: walk-forward OOS t>=2.0, N>=30, positive net, consistency across years.
- 14 signal families, "Nothing passed." Gross edge ceiling 0.07–1.50 pts/trade vs 2.0-pt friction.
- ORB table (09:30–09:55 OR): Long bar+1 −0.82 net t=1.17 | Long bar+15 +2.82 t=1.50 | Short bar+1
  −3.45 t=−1.33 | Short bar+15 −2.16 | ORB PULLBACK ENTRY N=83 −4.44 net WR 19.3%. ALL FAIL.
- Asia Session Opening Range Expansion (20:00–02:00 ET, bar range >1.5/2/2.5x rolling 20-bar mean,
  continuation hypothesis): 1.5x b+1 t=−10.96, WR 35.5% — significant REVERSAL ("actively wrong");
  burst consumed within the expansion bar.
- Gap fill fade FAILS at 09:30/09:45/10:00 (t −0.44..−0.59) — MNQ gaps don't reliably fill.
  Gap Continuation Short w/ Kalman velocity>2.5 at 09:30: N=22, +14.52 pts net, t=3.23, WR 68.2% —
  FAIL on N<30; frequency decayed 12→6→4/yr.
- Positive controls (independent research program, pass all gates): RTH Confluence Signal (GMM
  regime "Active Flow" + Markov transition prob>0.15 + 50-bar volume z>0.5; 25-pt ATR-scaled pullback
  entry; exit bar 13; t=5.83 N=538, OOS t=3.11) and London Session Signal B (GMM on 15-min London
  bars 03:00–08:30 ET, transition Regime0 Bearish Chop→Regime2 Bullish Drift, long next open, exit
  60 min or 08:30; N=289 +5.77 net t=5.15 WR 64.7% PF 2.42; 1-bar delay reverses edge to t=−3.56).
- Families: 4.1 ORB, 4.2 Asia ORE, 4.3 Asia liquidity-grab reversal, 4.4 gap fade/continuation,
  4.5 volume signature, 4.6 volatility regime classifier, 4.7 event-day trend, 4.8 MGC MR cross-test.

### Beat the Market — Table 5 conditioning numbers (extracted this pass from PDF)
- Intraday momentum avg PnL by prior-day daily pattern (bps, t, Sharpe):
  Unconditional N=2620: 12bps t=5.34 SR 1.7 | NR4 N=660: 22bps t=5.14 SR 3.2 | NR7 N=367: 16bps
  t=3.07 SR 2.5 | Inside Day N=260: 5bps n.s. | Outside Day N=260: 7bps n.s. | Triangle N=664: 14bps
  t=3.19 SR 2.0 | Trend day N=215: −2bps | Big Tail N=85: 19bps n.s. | Strong/Weak close N=422: 14bps t=2.04.
  Pattern defs: Triangle = high < prior-2 highs AND low > prior-2 lows; Trend day = open<15th pctile
  of range & close>85th & range>14-day avg. Day-of-week: Wed/Thu/Fri significant; Monday n.s. here,
  vs "higher Monday profitability in the 5-minute Opening Range Breakout" in their earlier papers.

### github.com/dws-data/nas-orb-backtester (fetched repo page) — NQ ORB RETRACEMENT
- OR = 09:30–09:45 ET; volume profile (VAH/POC/VAL) computed from OR bars; require 1-min bar CLOSE
  beyond OR extreme + threshold ("no wick entries"); wait for retrace to a VP level inside the range;
  enter on touch; stop at OR extreme; target beyond OR extreme; EoD force-close + entry cutoff.
- NQ.v.0 continuous, 1m OHLCV (Databento), 2021–2026: Long 198 trades WR 42.9% +0.417R; Short 80
  trades WR 42.5% +0.558R; combined ≈ +21.2R/yr at 1% risk/trade.

### traderfeed.blogspot.com/2010/03/defining-effective-price-targets-with.html (2010-03-31)
- "Well over 90% of days take out either their overnight high or low" (futures); only ~12% of days
  are inside days; trade at yesterday's average price (H+L)/2 about 60% of the time; weekly analogues.

### thepatternsite.com/nr7.html (Bulkowski; 1,201 stocks 1990–2013)
- NR7 ranks 11/23 among small patterns; failure rates 46% (bull/up) 47% (bull/down); bear-market
  down breakout best (27% fail, −12% avg move); 43% hit measure-rule target; overall it
  "underperformed benchmarks in most scenarios". Daily-horizon compression-breakout prior: weak.

### TradingView (fetched script/tag pages)
- London BreakOut Classic (xsixs, 909 likes) tradingview.com/script/Fh42LHOM-London-BreakOut-Classic/:
  Tokyo-session (00:00–07:00 UTC) high/low range; trade breakout during London; mid-range stop, 1:1 RR;
  author self-reports "poor results" over 3–6 months of testing and warns against blind use.
- Session Breakout/Sweep with alerts (a_guy_from_wall_street, 1.2K likes)
  tradingview.com/script/SxnXL2QI-Session-Breakout-Sweep-with-alerts/: same session-extreme levels
  traded EITHER as breakout OR as liquidity-sweep reversal — an explicit policy fork.
- FVG tag page tradingview.com/scripts/fairvaluegap/: FVG Detector (UDT) (CantoLab, 683 likes) —
  3-candle displacement imbalance, bullish = current low > high two bars back, with mitigation
  tracking; ICT Entry Model (LunqFX, 844 likes) sequences liquidity sweep → MSS → FVG entry.

### github.com/Mrshahidali420/ORB-Multi-Model-Indicator (fetched)
- 7 active ORB models NY session: M1 classic Crabel; M3 5-min scalper; M4 15-min; M6 FVG-inside-OR;
  M7 gold; M9 Failed-ORB Reversal; M10 "Phase ORB" state machine breakout→retest→bounce.
  3 models removed for 0–26% win rates. "Best results observed on AUDUSD, XAU/USD, US100 on 1-min."

### GitHub API repo census (api.github.com/search/repositories?q=opening+range+breakout)
- 15 top repos listed incl. jefrnc/strategy-orb15-momentum (16★, 2026), vedntp/pj_orb_backtester,
  sam-bateman/trading-orb, dws-data/nas-orb-backtester (above).

### Still unverifiable online (kept as book-citation lead only)
- Dalton/Jones/Dalton "Mind Over Markets": open-type taxonomy (Open-Drive etc.) → conviction ranking
  for range extension/trend days. CME education page timed out; no fetchable stats page found.
- Crabel "stretch" formula: no fetchable definition located (Wikipedia page has none; engines blocked).
  Crabel's model characterized via Concretum stocks-ORB paper: range calibrated from prior days'
  volatility + current open, no intraday data.
