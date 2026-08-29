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
