# G2W1 A10-VWAP — full scouting notes (accessed 2026-08-28)

## Method note (constraint fallback)
WebSearch budget was already exhausted (200/200) at session start. Per instructions, fell back to
WebFetch on site-native search/browse URLs and API endpoints:
- WORKED: arXiv API (export.arxiv.org), GitHub search API (api.github.com), WordPress site
  searches (alphatrends.net/?s=, quantifiableedges.com/?s=, smbtraining.com/blog/?s=,
  alvarezquanttrading.com/?s=, cxoadvisory.com/?s=, quantpedia.com/blog/?s=), Bing HTML
  (intermittently useful, often junk), direct article fetches (concretumgroup.com, thevwap.com,
  tradeproacademy.com, wikipedia).
- BLOCKED: SSRN (403), NY Fed (403), DuckDuckGo html (CAPTCHA), Mojeek (403),
  quantifiedstrategies.com (bot check), warriortrading.com (403), futures.io (403),
  masterthegap.com (SSL fail), investiquant.com/blog (404; homepage has no stats),
  school.stockcharts.com (SSL fail).

## Coverage gaps found (valuable in themselves)
1. **VWAP first-touch probability**: no fetchable public source quantifies "how often price
   returns to session VWAP intraday" for index futures. Every vendor asserts S/R behavior with
   zero N. We own NQ 1-min 2006-2026 → this table is cheap to build in-house and appears to be
   genuinely unpublished.
2. **Gap-fill rate by gap size table**: the canonical practitioner source (Scott Andrews /
   MasterTheGap / InvestiQuant) is offline or stat-free now; Quantifiable Edges has 151 gap
   articles but they are small-N conditional studies, not a size-binned fill table. Also cheap
   to build in-house.
3. **Market Profile "80% rule"** (value-area re-entry traverses the VA): could NOT locate a
   fetchable source stating it concretely (Wikipedia Market_profile page does NOT contain it;
   search engines blocked/junk). NOT submitted as a lead — unverified. Flagged here only.
4. Overnight-VWAP vs RTH-VWAP crosses: no concrete public source found; nearest is
   thevwap.com's anchored-VWAP-at-prior-day-open. Folded into A10-06.

## Sources fetched and what they said (raw)

### Concretum Group (Carlo Zarattini cluster) — papers page https://concretumgroup.com/papers/
1. "Volume Weighted Average Price (VWAP) The Holy Grail for Day Trading Systems" (Apr 2024;
   Zarattini & Aziz; SSRN 4631351 linked from page).
   https://concretumgroup.com/volume-weighted-average-price-vwap-the-holy-grail-for-day-trading-systems/
   - QQQ + TQQQ, Jan 2 2018 – Sep 28 2023. Rule: long when price above session VWAP, short
     when below (trend-following ON the VWAP side, NOT a fade). Claims: QQQ $25k→$192,656
     (671%), MaxDD 9.4%, Sharpe 2.1; TQQQ $25k→$2,085,417. "net of commissions".
     Quote: "capture short-term momentum and price imbalances that often occur during intraday
     trading sessions".
2. "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)" (May 2024;
   Zarattini, Barbon, Aziz; SSRN 4824172).
   https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/
   - SPY 2007–early 2024; enters trend positions on "abnormal demand and supply imbalances"
     (noise-area band framework) with dynamic trailing stops; 1,985% total, 19.6% ann,
     Sharpe 1.33, net of commissions+slippage.
3. "Can Day Trading Really Be Profitable?" (Apr 2024; Zarattini & Aziz).
   https://concretumgroup.com/can-day-trading-really-be-profitable/
   - 5-min ORB, QQQ (and leveraged), 2016–2023: 1,484% vs 169% passive QQQ.
   - Companion: "A Profitable Day Trading Strategy For The U.S. Equity Market" (stocks in play,
     5-min ORB) https://concretumgroup.com/a-profitable-day-trading-strategy-for-the-u-s-equity-market/
4. "QuanTip: Improving Performance with Fast Alphas; A Tactical Overlay for Intraday Trend
   Trading" (Feb 2026; Pagani & Zarattini).
   https://concretumgroup.com/quantip-improving-performance-with-fast-alphas-a-tactical-overlay-for-intraday-trend-trading/
   - Streak-based mean-reversion indicator from 5-min data on SPY 2007–2026. Not tradable
     standalone net of fees, but as an execution-timing overlay on the intraday trend strategy:
     +~200bp net CAGR, Sharpe 0.87→0.99. Quote: "fast alpha signals may contain valuable
     information even when they are not directly tradable".
   - NOTE: this maps exactly onto our campaign's EXECUTION vs NEW-INFORMATION classification.

### AlphaTrends / Brian Shannon
- https://alphatrends.net/when-where-why-to-set-anchored-vwap/ (no byline/date on page; site is
  Brian Shannon's). Anchors: first trade of year (S&P futures), weekly open (Sunday night),
  major swing highs/lows, reversals, news events (earnings, FOMC). Claim: AVWAP levels act as
  supply/demand concentration → S/R; polarity flip. Quote: "What was once prior resistance now
  seems to have become support." Site search also surfaced podcast pages (where/what/alone/
  thinkorswim). Book context: "Maximum Trading Gains with Anchored VWAP" (Wiley, 2023).

### TheVWAP.com (vendor, TheVWAP LLC, copyright 2025)
- https://thevwap.com/vwap/ and https://thevwap.com/vwap-strategy/
- SD bands create "zones" acting as S/R; four trade types (2 trend continuation, 2 countertrend
  reversion, long+short each); anchored VWAPs at prior day's open, earnings, recent lows;
  VWAP slope discussed. Explicitly calls the "VWAP acts as a magnet" idea a common myth
  needing nuance. Quote: "Price tends to behave differently at varying distances, with VWAP and
  the deviation bands serving as the barriers separating those contrasting regions." No stats.

### SMB Capital blog (search https://www.smbtraining.com/blog/?s=vwap)
- "Using VWAP to gain a trading edge" (Bella/Mike Bellafiore, 2016-05-12)
  https://www.smbtraining.com/blog/using-vwap-to-gain-a-trading-edge
  Quote: "If a stock is holding considerably above VWAP, and for time, this may be evidence we
  should get long the stock for a swing trade." Also VWAP as relative-strength-vs-market tool.
- "Using the VIX to Position Size a VWAP Trade" (Andrew, 2016-07-29)
  https://www.smbtraining.com/blog/using-the-vix-to-position-size-a-vwap-trade
  Quote: "using the VIX to adjust position size of a VWAP strategy helps improve the risk
  adjusted returns". No numbers.
- Other hits: "Why You NEED VWAP For Your Intraday Trading" (2014), "How to use VWAP to buy a
  Pullback in a Meme Stock" (2021), anchored VWAP FB trade (2019).

### TRADEPRO Academy (vendor; author "Faisal", Toronto)
- https://tradeproacademy.com/vwap/ — three uses: (1) intraday trend filter above/below VWAP;
  (2) VWAP as equilibrium → mean-reversion S/R; (3) momentum shift: "waiting for breakouts
  above VWAP after failed attempts" (≈ the VWAP-reclaim setup). No win-rate claims.
  Quote: "If the market is trading below VWAP during a session we can define the intraday
  trend as bearish."

### Quantifiable Edges (Rob Hanna) — site search 151 gap articles
- https://quantifiableedges.com/when-the-market-gaps-down-huge-during-a-long-term-uptrend/
  (2020-02-24): SPY gaps down >2% while in long-term uptrend — 16 instances since SPY
  inception (>2.5%: 5). "Most of the time in the past we have seen a decent bounce at some
  point in the next few days." No formal win-rate table in this one.
- Others: "A Big Gap Up That Wipes Out A Big Loss Yesterday" (2020-05-20), "Big Gaps Down In
  Already Bad Markets" (2020-03-08), "2 Unfilled Up Gaps And A 50-Day High" (2019-11-05),
  "When QQQ Gaps Down Big From A High" (2019-05-06).

### GitHub (via api.github.com search, then repo pages)
- https://github.com/einc58-netizen/vwap-mean-reversion-futures (Jupyter, upd 2026-08-14)
  ZN (10y note) + 6E (EuroFX). Enter at |z| ≥ 2.5σ from intraday VWAP, exit z→1.0σ, stop 5.0σ.
  ZN: ~484 trades, EV ~$76/trade, $36,875 total, Sharpe 0.97 (10 contracts). Monte Carlo
  10,000 Student-t sims under Apex prop drawdown rules → "~56% pass rate"; regime filters
  (vol percentile, yield-move restrictions) matter. **6E consistently loses despite same
  statistical mean-reversion pattern** — stat-significance ≠ profitability. Data: Databento
  commercial license, cross-validated vs Rithmic, corrected calendar-spread contamination.
- https://github.com/ojeology/mean-reversion-vwap-lab (Python, upd 2026-08-03)
  13 crypto pairs, MEXC 1-min. Session VWAP ±2σ bands; long = touch lower band + green candle
  closing back above band + body >50% ATR + RSI<40 (mirror for shorts); per-pair optimized
  %TP/%SL; avoids bad hours near session open/close. Claims E14: PF 2.01, Sharpe 15.44
  (implausibly high — red flag), WF daily avg $3.61, win rate 54% IS / 44–47% OOS.
  Paper-trading only, zero real capital.
- Also seen: 0zean/VWAP-Mean-Reversion (R, 3 stars), LiangChen219/Mean-Reversion-Strategy,
  toniker10/3-VWAP-Mean-Reversion, mengrenman/btcusdt-perp-signals (OFI+VWAP reversion).

### arXiv API (export.arxiv.org, query all:"VWAP", 25 results)
- Choi, Larsen, Seppi, "Equilibrium Effects of Intraday Order-Splitting Benchmarks"
  (arXiv:1803.08336, 2018, v6): models how "VWAP trading reduces market liquidity and
  increases price volatility" vs terminal strategies → theoretical mechanism for VWAP
  attracting/structuring institutional flow.
- Guéant & Royer, "VWAP execution and guaranteed VWAP" (arXiv:1306.2832, 2013, SIAM J Fin
  Math): guaranteed-VWAP contracts priced/hedged — evidence institutional VWAP-benchmarked
  products exist at scale (dealer hedging anchors flow to the running VWAP).
- Kato "VWAP Execution as an Optimal Strategy" (1408.6118); Busseti & Boyd (1509.08503);
  Barzykin & Lillo (1901.02327); many RL-execution papers (Genet 2025 crypto VWAP exec).
- arXiv has ZERO results for "opening range breakout" and for "intraday momentum"+"first
  half-hour" — those literatures live on SSRN (blocked).

### Alvarez Quant Trading (Cesar Alvarez, ex-Connors Research) — site search ?s=rsi2
- https://alvarezquanttrading.com/blog/rsi2-strategy-double-returns-with-a-simple-rule-change/
  (2018-08-01): "I doubled the compounded annual growth rate and cut the maximum drawdown in
  half"; CAR "from lows 10's to the low 20's". Stocks.
- https://alvarezquanttrading.com/blog/rsi2-relative-strength-index-analysis/ (2018-06-13):
  "the RSI2 smile" indicator behavior study.
- Origin of RSI2 family: Connors & Alvarez, "Short-Term Trading Strategies That Work" (2008).

### Quantpedia blog search — no VWAP articles; found "Lunch Effect in the U.S. Stock Market
  Indices" (2024-08-21) — intraday seasonality adjacent, not taken as a lead.

## Repo-relevance notes (for the parent)
- All VWAP leads are REPRESENTATION/POLICY vs our data: session/anchored VWAP is computable
  from NQ 1-min OHLCV (typical-price × volume approximation); 2025-26 tick/BBO can bound the
  approximation error of 1-min VWAP vs true VWAP before trusting fade stats near bands.
- einc58 repo's 6E negative result is the single most useful calibration point: identical
  z-score MR machinery, statistically mean-reverting, still loses net. Prior for NQ (an
  equity index that trends intraday per Zarattini) should be LOWER than for ZN.
- Zarattini cluster (leads 01–04) is one author family — treat as correlated evidence, one
  effective source for null purposes.

---

# SECOND PASS (same day, continuation after interruption) — additional verified sources

WebSearch still 200/200 exhausted; all below via WebFetch fallback. Newly blocked this pass:
tandfonline (403), warriortrading (403), old.reddit (tool-blocked), YouTube results (empty
shell), Bing (degraded junk), Mojeek/Ecosia/DDG html+lite (403/captcha), Semantic Scholar API
(intermittent 429 — two queries succeeded).

## Supersedes prior "coverage gap #3": 80% RULE SOURCE FOUND
- https://www.mypivots.com/dictionary/definition/25/80-rule (found via /dictionary →
  /dictionary/browse/0-9). Exact definition: "If the market opens (or moves outside of the
  value area) and then moves back into the value area for two consecutive 30-min-bars, then
  the 80% rule states that there is a high probability of completely filling the value area."
  SAME PAGE self-reports an E-mini S&P test succeeding only ~60% of the time ("should be
  renamed the 60% Rule"). Now submitted as a lead.

## New verified sources
1. TraderFeed search + https://traderfeed.blogspot.com/2010/03/relevance-of-vwap-in-range-market.html
   (Steenbarger, 2010-03-29, ES): "moves away from value will tend to return back to (and
   usually through) VWAP"; range days = flat VWAP slope; failed VWAP pierce → rotation signal.
   Related slope/day-structure posts 2008-11-16, 2009-02-03, 2009-10-27, 2009-12-30.
2. Crossref API: Gao/Han/Li/Zhou "Market intraday momentum" JFE 129(2) 2018 394-414,
   DOI 10.1016/j.jfineco.2018.05.009 (SSRN preprint 2440866, 2014): "first half-hour return
   ... predicts the last half-hour return".
3. Semantic Scholar API: Grant/Wolf/Yu "Intraday price reversals in the US stock index futures
   market: A 15-year study", JBF 29(5) 2005 1311-1327, DOI 10.1016/J.JBANKFIN.2004.04.006
   (abstract NOT retrievable — claim kept title-level). Also Fung/Mok/Lam 2000 (US + HK index
   futures reversals) DOI 10.1016/S0378-4266(99)00072-2.
4. Crossref API: Caporale & Plastun "Price gaps: Another market anomaly?", Investment Analysts
   Journal 46(4) 2017 279-293, DOI 10.1080/10293523.2017.1333563 (abstract not retrievable;
   tandfonline 403 — claim kept title-level).
5. Crossref API: Madhavan "Volume-Weighted Average Price (VWAP)", Encyclopedia of Quantitative
   Finance 2010, DOI 10.1002/9780470061602.eqf07036 ("a common benchmark used to evaluate
   performance"); Bialkowski/Darolles/Le Fol "Improving VWAP Strategies: A Dynamical Volume
   Approach", DOI 10.2139/ssrn.932699 (2006).
6. https://arxiv.org/abs/1803.08336 fetched directly (Choi/Larsen/Seppi): "intraday
   trajectories of TWAP trading targets cause predictable intraday patterns of price
   pressure"; TWAP+VWAP benchmark trading "reduce market liquidity and increase price
   volatility relative to just terminal trading targets alone."
7. Alphatrends https://alphatrends.net/when-where-why-to-set-anchored-vwap/ re-fetched:
   anchors = first trade of year, weekly Sunday-evening futures open, major swing highs/lows,
   YTD lows; "it lets you see where buyers or sellers have an average cost basis after big
   events". Podcast pages active May-Jun 2026.
8. GitHub API + README: https://github.com/WhiteRabbit-TB/vwap-mean-reversion (upd 2026-05-18)
   — ES tick→1-sec bars, RTH, VWAP ±2σ touch reversion; bootstrap + Bonferroni across
   6 conditions; spread + 1-bar latency modeled; VIX/day-type regime conditioning; sensitivity
   σ 1.5–2.5, windows 5–30 min; SINGLE SESSION (2026-05-12, 80 touches) prototype; claims
   strong reversion at lower band in opening segment.
9. einc58-netizen/vwap-mean-reversion-futures README re-fetched — confirms prior-pass numbers
   plus: "Intraday AR(1) half-life ≈ 19 minutes" (ZN), walk-forward 13 interleaved holdout
   months, ~56% Monte Carlo pass under prop drawdown, 6E uneconomic after costs (tick value
   $6.25 vs $15.625 cited), live Rithmic deployment claimed.
10. TradingSim https://www.tradingsim.com/blog/vwap-indicator (Al Hill, 2021-06-23, upd
    2026-03-29): "more often than not, the price finds support and resistance around this
    level"; ES case study — separations ≥0.4% from VWAP later see "a sharp correction back to
    the indicator"; institutions use VWAP to "reduce market impact while dividing up large
    orders". No win rates.
11. TradingView https://www.tradingview.com/scripts/vwap/ — ecosystem/crowding evidence:
    Smart Swing VWAP (Zeiierman, 1.9K boosts), Modern VWAP (GBB, "regime-gated mean reversion
    and trend continuation signals", 574 boosts), Range Breakout Pro (VWAP + sd bands),
    Multi-Anchor VWAP & Deviation Bands, VWAP Regime AI (k-means vol regimes adapt bands).
12. Quantifiable Edges WP search (?s=gap, ?s="gap fill") — 69+ tagged posts; specifics in
    first-pass notes; "Intraday Performance After A Massive Gap Down" (2016-06-24) noted.
13. masterthegap.com → 301 → investiquant.com (fetched): Scott Andrews + David Skowron,
    pivoted to autotrading; NO public gap-stat pages ⇒ prior coverage-gap #2 stands.
14. TRADEPRO https://tradeproacademy.com/vwap/ re-fetched (Faisal, 2018-11-15): trend filter /
    MR to equilibrium / "breakouts above VWAP after failed attempts" (≈ reclaim). No stats.
15. thevwap.com/vwap-strategy/ re-fetched: "four primary trade types — two for trend
    continuation and two for countertrend reversion"; "areas of otherwise hidden support and
    resistance"; hypothetical-trades disclaimer, no stats. (Magnet-myth phrasing was on /vwap/
    per first pass; not re-verified — quote only "hidden support and resistance".)
16. Concretum VWAP paper article page re-fetched: rules confirmed — LONG above session VWAP /
    SHORT below (trend-following, NOT fade); QQQ 2018-01-02→2023-09-28, $25k→$192,656 (671%),
    Sharpe 2.1, MaxDD 9.4%; TQQQ $25k→$2,085,417 (8,242%).
17. Alvarez https://alvarezquanttrading.com/blog/rsi2-strategy-double-returns-with-a-simple-rule-change/
    re-fetched (2018-08-01): RSI2 MR on EX-INDEX Russell 3000 stocks; "I doubled the
    compounded annual growth rate and cut the maximum drawdown in half"; exit RSI2>50 or
    10 days. (Stock universe, not futures — weak transfer, included as family exemplar.)
18. SMB blog search re-run: 25 pages VWAP content; "Using VWAP to gain a trading edge"
    (Bella, 2016-05-12) re-fetched — explicitly NO win-rate claims; "holding considerably
    above VWAP, and for time" = swing-long evidence.
19. MenthorQ ?s=vwap: only generic guides (/guide/what-is-vwap-in-trading/), no stats — not a lead.

## Final lead selection (16): see final report. Independence clusters:
- Concretum/Zarattini family: A10-01, A10-14 (+ ORB context) — one effective source.
- Market-Profile/value-auction folklore family: Steenbarger, 80% rule, TradingSim, TRADEPRO,
  thevwap, SMB, TradingView scripts — shared ancestry (Steidlmayer/Dalton + floor folklore);
  independent only in their (rare) numbers.
- Academic exec-benchmark family: Choi et al., Guéant-Royer, Madhavan, Bialkowski — one
  mechanism cluster, distinct models.
- Independent computations: Gao et al., Grant et al., Caporale-Plastun, einc58, WhiteRabbit,
  ojeology, Alvarez.
