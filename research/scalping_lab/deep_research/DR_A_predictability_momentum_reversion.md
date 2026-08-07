# DR-A — Short-Horizon Predictability, Intraday Momentum, and Micro Mean-Reversion in Index Futures

**Workstreams:** DR-S01 (short-horizon predictability in futures), DR-S06 (intraday momentum, seconds-to-minutes and session-anchored), DR-S07 (micro mean-reversion, bid-ask bounce, failed-impulse snapback)
**Author:** MICROSTRUCTURE_SCIENTIST (deep-research agent) | **Date:** 2026-08-07
**Status:** Literature/mechanism review with attached experiments. No data analysis was run for this document.

---

## 0. Scope, method, and the cost lens

All findings below are evaluated against the campaign's retail cost floor for NQ market-order round trips:

- **C1 = $14.36 per round trip ≈ 2.872 ticks** (= $4.36 commission + 2 × 1-tick spread crossings at $5/tick). This assumes the book is 1 tick wide and we get filled at the touch; slippage beyond the touch (thin books, news windows) is **extra**.
- NQ point = $20, tick = 0.25 pt = $5. At an index level of ~25,000, contract notional ≈ $500k, so **1 tick ≈ 0.1 bp of notional** and **C1 ≈ 0.29 bp**.
- Conversion table (memorize this — it is the whole game):

| Literature effect size | In NQ ticks | Clears C1 = 2.87 ticks? |
|---|---|---|
| 0.1 bp (typical per-event HFT edge) | ~1 tick | No |
| 0.5 bp | ~5 ticks | Marginal (1.7× cost) |
| 1 bp | ~10 ticks | Yes (3.5× cost) |
| 5 bp (typical session-anchored intraday-momentum spread) | ~50 ticks | Yes (17× cost) |

**Consequence:** the literature's statistical findings split cleanly into (a) sub-second/sub-minute effects worth fractions of a tick to ~1 tick gross — real, replicable, and **unharvestable at C1**; and (b) session-anchored effects (30-min blocks, open/close, announcement windows) worth 1–10+ bp per trade at 1–2 trades/day — the only zone where retail-cost expectancy is arithmetically possible. Everything in this report is organized around that split.

---

## 1. What the literature actually establishes

### 1.1 DR-S01 — Short-horizon predictability in general (order flow, efficiency convergence, latency)

**1.1.1 Order-flow imbalance moves prices linearly; the effect is real but lives at event scale.**
- *The Price Impact of Order Book Events* — Rama Cont, Arseniy Kukanov, Sasha Stoikov (J. Financial Econometrics, 2014; arXiv 2010). https://arxiv.org/pdf/1011.6402 and https://academic.oup.com/jfec/article-abstract/12/1/47/816163
  Over short intervals, price changes are driven by **order-flow imbalance (OFI)** — net change in supply/demand at the best bid/ask. The relation is **linear**, with slope **inversely proportional to market depth**; stable across stocks and timescales; subsumes the square-root volume-impact relation. Implication for NQ: deep book ⇒ small slope ⇒ a given imbalance moves NQ *less* than a thin instrument; OFI is a *contemporaneous impact* model as much as a forecasting model.
- *Deep Order Flow Imbalance: Extracting Alpha at Multiple Horizons from the Limit Order Book* — Petter N. Kolm, Jeremy Turiel, Nicholas Westray (Mathematical Finance, 2023; SSRN 3900141). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3900141
  115 Nasdaq stocks, full-depth order flow, deep nets. Key number: **the effective forecast horizon is ≈ 2 average price changes** — beyond that, alpha decays to noise. OFI-derived (stationary) features beat raw LOB snapshots. For NQ in RTH, the mid-price changes on the order of once per second or faster ⇒ **the OFI alpha horizon in NQ is seconds**. Forecast target is mid-price direction, gross of costs — the paper does not claim net profitability.
- *The short-term predictability of returns in order book markets: a deep learning perspective* — Lucchese, Pakkanen, Veraart (Int. J. Forecasting, 2024; arXiv 2211.13777). https://arxiv.org/pdf/2211.13777 — same qualitative picture: mid-price predictability at horizons of ~10–100 events, monotonically decaying, never converted to net-of-cost P&L.
- *Order Flow Imbalances and Amplification of Price Movements: Evidence from U.S. Treasury Markets* — Federal Reserve FEDS Note, Nov 2025. https://www.federalreserve.gov/econres/notes/feds-notes/order-flow-imbalances-and-amplification-of-price-movements-evidence-from-u-s-treasury-markets-20251103.html — official-sector corroboration that OFI-driven amplification operates in futures/cash rates markets at intraday horizons.

**1.1.2 Predictability horizons have collapsed over time (efficiency convergence).**
- *Evidence on the Speed of Convergence to Market Efficiency* (JFE 2005) and *Liquidity and Market Efficiency* (JFE 2008) — Tarun Chordia, Richard Roll, Avanidhar Subrahmanyam. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=794264 and https://www.sciencedirect.com/science/article/abs/pii/S0304405X07001833
  Mid-1990s NYSE: lagged 5-minute order imbalance significantly predicted 5-minute returns; predictability **shrank with tick size and spreads** — prices converged to random-walk behavior within ~5–15 minutes in the decimal regime vs ~30–60 minutes earlier. Short-horizon predictability from order flow is an **inverse indicator of market efficiency**, harvested away by arbitrageurs as liquidity improves. Extrapolation to 2020s CME index futures (deepest, tightest instruments in existence): the exploitable-by-humans window from simple L1/L2 flow signals is plausibly **under one minute and under one tick**.

**1.1.3 The fastest layer is a pure latency race that retail cannot enter.**
- *The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response* — Eric Budish, Peter Cramton, John Shim (QJE, 2015). https://academic.oup.com/qje/article/130/4/1547/1916146
  ES–SPY arbitrage: median opportunity duration fell **97 ms (2005) → 7 ms (2011)**; per-opportunity profit roughly constant; ES/SPY correlation ≈ 1 at minutes, ≈ 0 at milliseconds. NQ–QQQ is the same race.
- *Quantifying the High-Frequency Trading "Arms Race"* — Matteo Aquilina, Eric Budish, Peter O'Neill (QJE, 2022). https://academic.oup.com/qje/article/137/1/493/6368348
  Message-data on LSE: latency races ~**1 per minute per symbol**, modal race lasts **5–10 microseconds**, average race worth ≈ **half a tick**, races = ~20% of volume, top 6 firms win >80%. This calibrates the sub-second zone precisely: the marginal value of the fastest signals is ~½ tick, contested in microseconds. **Nothing in this zone is retail-relevant except as a warning.**

**1.1.4 Trade-sign persistence is NOT return predictability.**
- *Fluctuations and response in financial markets: the subtle nature of "random" price changes* — Jean-Philippe Bouchaud, Yuval Gefen, Marc Potters, Matthieu Wyart (Quantitative Finance, 2004); *long memory of order flow* also Lillo & Farmer (2004). Overview: https://arxiv.org/pdf/0903.2428
  Trade signs are autocorrelated over **hours-to-days** (metaorder fragmentation), yet prices remain nearly diffusive because impact is transient/liquidity-asymmetric. **Warning:** an L1 feature like "recent trades were mostly buys" is strongly persistent and will *appear* to predict flow — but the market has already priced that persistence; naive backtests on Last-trade data can mistake flow persistence + bounce for return alpha.

**1.1.5 Announcement windows are the exception where minutes-scale conditional means exist.**
- *Micro Effects of Macro Announcements: Real-Time Price Discovery in Foreign Exchange* — Torben Andersen, Tim Bollerslev, Francis Diebold, Clara Vega (AER, 2003; companion JIE 2007 covers S&P futures). https://www.aeaweb.org/articles?id=10.1257/000282803321455151
  Surprises produce **conditional-mean jumps completed within minutes**; volatility (not mean) persists for hours; bad news moves prices more than good news.
- *Price Drift before U.S. Macroeconomic News: Private Information about Public Announcements?* — Alexander Kurov, Alessio Sancetta, Georg Strasser, Marketa Wolfe (JFQA, 2019). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2637528
  In E-mini index and Treasury futures, for 9 of 20 market-moving announcements prices drift in the "correct" direction starting **~30 min before release**, accounting for **~40% of the total adjustment**. (Note: follow-up "Drift Begone!" (Kurov, Sancetta, Wolfe 2022, https://www.skidmore.edu/economics/documents/Kurov-Sancetta-Wolfe-2022-Drift-Begone.pdf) shows release-policy changes weakened pre-drift in later samples.)

### 1.2 DR-S06 — Intraday momentum

**1.2.1 The canonical session-anchored effect: first half-hour → last half-hour.**
- *Market Intraday Momentum* — Lei Gao, Yufeng Han, Sophia Zhengzi Li, Guofu Zhou (JFE, 2018; SSRN 2440866). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866 and https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351
  SPY 1993–2013. First half-hour return (incl. overnight) predicts last half-hour return: scaled slope **6.94 (t-sig at 1%), R² = 1.6%** — enormous for a daily-frequency predictive regression. Stronger on **high-volatility, high-volume, recession, and macro-news days**. Also present in 10 other liquid ETFs. Mechanisms proposed: late-informed trading and daytrader position-squaring.
- *Hedging Demand and Market Intraday Momentum* — Guido Baltussen, Zhi Da, Sten Lammers, Martin Martens (JFE, 2021; SSRN 3760365). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365 and https://www3.nd.edu/~zda/intramom.pdf
  **The futures version — directly applicable to NQ.** 62 futures (17 equity-index incl. ES/NQ-type contracts, 16 bond, 21 commodity, 8 currency), 1974–2020: last 30 minutes before close is positively predicted by the rest-of-day return, **everywhere**, statistically and economically significant. Mechanism pinned to **gamma-hedging demand** (options market makers and leveraged-ETF rebalancing must trade *with* the day's move near the close). Critical detail: the effect **reverts over the following days** — it is price pressure, not information. Leveraged-ETF rebalancing in Nasdaq-100 products (TQQQ/SQQQ complex) makes NQ arguably the *strongest* candidate among index futures.
- Theory: *Infrequent Rebalancing, Return Autocorrelation, and Seasonality* — Vincent Bogousslavsky (JF, 2016). https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12436 — infrequent rebalancers concentrate flow at particular clock times, flipping autocorrelation sign at the rebalancing horizon; explains why intraday momentum is *clock-anchored* rather than a generic trend effect.

**1.2.2 Intraday periodicity (time-of-day is a real conditioning variable).**
- *Intraday Patterns in the Cross-section of Stock Returns* — Steven Heston, Robert Korajczyk, Ronnie Sadka (JF, 2010). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1107590 and https://arxiv.org/abs/1005.3535
  Splitting the day into 13 half-hours: return **continuation at lags that are exact multiples of one trading day**, persisting **≥ 40 trading days**; magnitude is basis points per half-hour (economically modest per interval, statistically overwhelming). Volume/imbalance/volatility share the periodicity but do not explain it — systematic, clock-scheduled institutional order flow does. Also establishes for DR-S07: **short-lag reversal is driven by temporary liquidity imbalances lasting < 1 hour plus bid-ask bounce.**

**1.2.3 Practitioner replications of intraday momentum on ES/NQ with explicit costs (closest thing to our own setting).**
- *Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)* — Carlo Zarattini, Andrew Aziz, Andrea Barbon (SSRN 4824172, 2024). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172
  Generalizes Gao et al.: trade whenever price exits a "**Noise Area**" (bands = open ± average absolute open-to-HH:MM move over last 14 days, gap-adjusted); exit at close or on re-entry into the band. SPY 2007–2024: **+19.6%/yr net, Sharpe 1.33** under their cost model.
- *Intraday Momentum for ES and NQ* — Quantitativo (2024, practitioner replication with futures costs). https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq
  ES 2010–2024 base: +8.1%/yr, Sharpe 0.91, **win rate 36%, +2 bp/trade expectancy, payoff 2.09** at costs = $0.85 commission + $1.40 fees + **0.5 tick slippage per side**. NQ version: **+24.3%/yr, Sharpe 1.67, win 38%, +6 bp/trade, payoff 2.25** — NQ materially better than ES. Caveats the author states: flat 2010–2017 with gains concentrated post-2018; results sensitive to slippage ("0.5 tick already optimistic"). **+6 bp/trade ≈ 60 NQ ticks ≈ $300/contract — this clears C1 by ~20×, which is why this family is our zone.** Note low win rate: this is a *low-win-rate, high-payoff* family, in tension with the campaign's stated preference for high win rate — the cost-adjusted expectancy is what matters.

**1.2.4 Cross-market confirmation.**
- *Intraday momentum in FX markets: Disentangling informed trading from liquidity provision* — Elaut, Frömmel, Lampaert (J. Financial Markets, 2018). https://www.sciencedirect.com/science/article/abs/pii/S1386418116300313 — same first→last structure in FX.
- *Market intraday momentum: APAC evidence* (RMIT repository, 2024). https://research-repository.rmit.edu.au/articles/journal_contribution/Market_intraday_momentum_APAC_evidence/27573486 — present in China/Japan, weaker elsewhere; the effect is global but regime-dependent.

### 1.3 DR-S07 — Micro mean-reversion, bid-ask bounce, failed-impulse snapback

**1.3.1 The Roll model: sub-minute "reversion" on trade data is mostly an artifact.**
- *A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market* — Richard Roll (JF, 1984). https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1984.tb03897.x
  With trades bouncing between bid and ask, transaction-price changes have first-order autocovariance **cov = −s²/4** (spread s), i.e., spread = 2√(−cov). For NQ with a 1-tick spread, the *mechanical* apparent profit of fading the last tick move is **~½ tick gross — permanently below C1 = 2.87 ticks.** Any sub-minute reversal signal measured on Last-trade data must be re-measured on midquotes before it is believed; empirically, second-level ES returns show exactly this significantly negative ACF at the shortest lags, fading at longer lags (see e.g. S&P 500 microstructure-noise decompositions: Taylor, J. Time Series Analysis 2025, https://onlinelibrary.wiley.com/doi/10.1111/jtsa.12786).

**1.3.2 Reversal after large moves is real but cost-fragile.**
- *Intraday price reversals in the US stock index futures market: A 15-year study* — James Grant, Avner Wolf, Susana Yu (J. Banking & Finance, 2005; SSRN 689282). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=689282
  S&P 500 futures, Nov 1987–Sep 2002: highly significant intraday reversal after large opening moves, **stronger after large up-opens**; but "significance … sharply reduced when gross trading results are adjusted by a bid-ask proxy for transaction costs." This is the cleanest published preview of our own cost problem, in our own asset class.
- *Intraday price reversals for index futures in the US and Hong Kong* — Fung, Mok, Lam (J. Banking & Finance, 2000). https://scispace.com/pdf/intraday-price-reversals-for-index-futures-in-the-us-and-137ieyy6y7.pdf — same finding, two markets.
- *End-of-Day Reversal* — Guido Baltussen, Zhi Da, Amar Soebhag (SSRN 5039009, 2024). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009
  Cross-section of US stocks: intraday **losers beat intraday winners in the last 30 minutes** (3:30–4:00), driven by contrarian retail buying of losers and short-seller risk management; distinct from (and coexists with) market intraday momentum. For a single index future this manifests only via the index aggregate, so expect it to be weaker in NQ — but it warns that the last half-hour hosts *two* opposing flows (index-level momentum from gamma hedging, cross-sectional reversal from retail/shorts).
- *Evaporating Liquidity* — Stefan Nagel (RFS, 2012). https://academic.oup.com/rfs/article/25/7/2005/1602153
  Short-term reversal strategy P&L ≈ compensation for liquidity provision; **scales with VIX**. Regime message for DR-S07: fade-the-move edges are largest exactly when volatility (and our slippage) is highest — cost modeling in high-vol states is not optional.

**1.3.3 Failed-impulse snapback: the mechanism is stop-cascade exhaustion.**
- *Stop-Loss Orders and Price Cascades in Currency Markets* — Carol Osler (J. Int'l Money & Finance, 2005; NY Fed Staff Report 150). https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.pdf
  Stop-loss orders cluster **just beyond round numbers** (~10% of orders at rates ending in 00; SL sells just below, SL buys just above); price moves are unusually **fast** through those levels (cascades), and take-profit clustering *at* round numbers explains support/resistance. This is the only rigorous order-book documentation of the practitioner "liquidity sweep / stop run" concept. It establishes the **impulse** leg (positive feedback through the level). The **snapback** leg — reversion once stop inventory is exhausted and value traders respond — is documented at the extreme in flash events: the 2010 Flash Crash (CFTC-SEC report, 2010, https://www.sec.gov/news/studies/2010/marketevents-report.pdf) and the Oct 15, 2014 Treasury flash rally (Joint Staff Report, 2015, https://home.treasury.gov/system/files/276/joint-staff-report-the-us-treasury-market-on-october-15-2014.pdf) both round-tripped within minutes without fundamental news: uninformed, liquidity-driven impulses mean-revert.
  Heston-Korajczyk-Sadka's finding that short-lag reversal is "temporary liquidity imbalances lasting less than an hour" is the statistical shadow of the same mechanism at ordinary scale.

### 1.4 The 2026 CME MBO preregistered study (SSRN abstract_id 7067778) — retrieval status

**Could not be retrieved or independently verified.** Attempts on 2026-08-07: direct fetch of `papers.ssrn.com/sol3/papers.cfm?abstract_id=7067778` and `ssrn.com/abstract=7067778` → **HTTP 403** (Cloudflare bot wall, both via WebFetch and via curl with browser UA); SSRN content API → 401; no search engine (Google/Bing), Semantic Scholar, or secondary index (EconBiz, RePEc, ResearchGate) has the ID or any matching title indexed; the local Chrome extension was unavailable for an interactive fetch. The claimed headline — **predictability detected in 46/46 instrument-session cells, 0/46 profitable at retail costs, on CME Market-by-Order data** — comes from the campaign brief and is **UNVERIFIED**; its feature set, horizons, and exact cost assumptions could not be extracted. ACTION ITEM: a human with a browser should pull the abstract/PDF and drop it in `research/scalping_lab/deep_research/` so the feature list can be mined for H8. Until then, treat the 46/46-vs-0/46 claim as *consistent with* (and predicted by) the verified literature above (CRS efficiency convergence + Kolm horizon collapse + ABO race economics), not as independent evidence.

---

## 2. What transfers to NQ at retail latency — and what is HFT-only

Retail execution reality (NinjaTrader-class stack, market orders): decision-to-exchange latency ~50–250 ms best case; no queue priority; pay the spread. Three zones:

| Zone | Horizon | Literature effects living here | Gross size | Verdict for us |
|---|---|---|---|---|
| A (HFT-only) | < 1 s | OFI/LOB alpha (Cont et al.; Kolm et al. "2 price changes"; DeepLOB), latency races (ABO ~½ tick in 5–10 µs), ES-SPY / NQ-QQQ lead-lag (BCS, 7 ms) | 0.1–1 tick | **Dead on arrival.** Alpha half-life < our latency; edge < C1 by 3–30×. Do not spend campaign capacity here. |
| B (contested) | ~10 s – 15 min | post-move continuation/reversal, OFI aggregated to minutes, stop-cascade snapbacks (Osler-type), open-drive reversal (Grant-Wolf-Yu) | ~1–10 ticks | **Marginal.** Only survives if (i) conditioned on high-volatility states where moves are 10s of ticks, and (ii) trade frequency is low enough that C1 doesn't compound away the edge. Reversal findings here died of costs in the literature at *higher* cost levels than ours — modern 1-tick spreads + $4.36 commissions are actually more favorable than the 1990s cost regimes in Grant-Wolf-Yu. Worth a small number of preregistered shots. |
| C (transferable) | 30 min – session | market intraday momentum (Gao et al.; **Baltussen et al. in futures**), noise-area breakout (Zarattini; Quantitativo NQ +6 bp/trade), announcement-window dynamics (ADBV; Kurov), time-of-day periodicity (HKS; Bogousslavsky) | 5–100 ticks | **Our zone.** Effects are flow-driven (gamma hedging, rebalancing schedules), documented in futures directly, replicated with futures-level costs, and 1–3 trades/day means C1 is a rounding error. |

**Data-level requirements flagged (L1 = last-trade, L2 = BBO, L3 = top-of-book sizes, L4 = depth/MBO):**
- Zone C effects need only **L1 bars** (intraday returns, session anchors, a volatility estimate, an announcement calendar). Fully compatible with our confirmed data.
- Zone B *measurement* needs **L2 midquotes** to kill the Roll-bounce artifact (any reversal result from L1 trade prices at sub-minute horizons is presumptively bounce until proven otherwise); *sweep vs. fade* discrimination needs **L3/L4**. If the bid/ask audit comes back negative, Zone B hypotheses must be redesigned around bar-level proxies with an explicit +/−1 tick measurement-error budget.
- Zone A needs **L4 + colocation**; listed only to justify exclusion.

---

## 3. Testable hypotheses

Numbering continues the campaign's hypothesis registry conventions; priorities: 1 = run first.

### H1 — NQ market intraday momentum: rest-of-day return predicts the last 30 minutes

The Baltussen et al. futures result specialized to NQ: gamma-hedging and leveraged-ETF rebalancing flows push the close in the direction of the day's move; the Nasdaq-100 complex carries unusually large leveraged-ETF AUM (TQQQ/SQQQ), so NQ should be at the strong end of their 62-market panel. Two nested predictors: first-half-hour return (Gao et al. spec) and rest-of-day return 09:30–15:30 ET (Baltussen spec).

- **ECONOMIC MECHANISM:** dealers short gamma and leveraged-ETF managers must trade in the direction of the day's move near the close (hedging/rebalancing is mechanical, price-insensitive, and clock-anchored); Bogousslavsky-type infrequent rebalancing concentrates the flow in the last half-hour.
- **OBSERVABLE VARIABLES:** r(09:30→10:00) incl. overnight gap; r(09:30→15:30); realized intraday range/vol; day-type flags (macro-news day, OPEX, month-end).
- **EXPECTED HORIZON:** position 15:30→15:55 ET (exit before the equity close auction imbalance window; strategy remains flat at session close per campaign constraints).
- **EXPECTED SIGN:** last-30-min return has the **same sign** as the rest-of-day return (momentum); effect larger on high-vol/high-|ROD| days; expect partial reversal over following days (do not hold overnight).
- **REQUIRED DATA (L1-L4):** **L1 only** (1-min bars we already have).
- **RETAIL EXECUTABILITY:** high — 1 trade/day max, market orders, expected conditional move on trade days is tens of ticks vs C1 = 2.87 ticks.
- **SIMPLE NULL:** last-30-min return is independent of ROD sign; conditional mean net of C1 ≤ 0.
- **FALSIFICATION EXPERIMENT:** on the canonical window (2023-01-01→2025-02-02, locked-forward rules respected), regress r_last30 on r_first30 and r_ROD with Newey-West errors; then event-level sim: enter 15:30 with sign(ROD) filtered to |ROD| above its rolling 60-day median, exit 15:55, C1 per round trip. Falsified if slope ≤ 0 or net expectancy ≤ 0 ticks, or if all P&L concentrates in < 10 days.
- **PRIORITY:** 1

### H2 — Noise-area breakout with close-anchored exit (Zarattini/Quantitativo family on NQ)

Intraday trend positions initiated whenever price exits a gap-adjusted "noise area" (open ± avg abs open-to-time-t move, 14–90-day lookback), exit at session close or re-entry into the band. Independent practitioner replication already reports **+6 bp/trade net on NQ** (Sharpe 1.67, win 38%) at 0.5-tick slippage — our job is adversarial replication under our cost floor and PBO discipline.

- **ECONOMIC MECHANISM:** same hedging/rebalancing feedback as H1 harvested earlier in the day: an abnormal displacement from the open signals a demand/supply imbalance that positive-feedback flows (gamma, trend-followers, stop cascades per Osler) extend until the close.
- **OBSERVABLE VARIABLES:** open price; time-of-day-indexed average absolute displacement (lookback 14 and 90 days); overnight gap; VWAP (trailing stop variant); band-exit events.
- **EXPECTED HORIZON:** minutes-to-hours (entry any time after 09:45, exit at close or band re-entry).
- **EXPECTED SIGN:** continuation in the breakout direction.
- **REQUIRED DATA (L1-L4):** **L1 only** (1-min bars).
- **RETAIL EXECUTABILITY:** high — ~0.5–2 trades/day; published expectancy ≈ 60 ticks/trade vs C1 2.87; the binding risk is slippage on stop exits, not entries.
- **SIMPLE NULL:** entries at random times matched for time-of-day and volatility, with identical exit logic, produce the same expectancy (i.e., the band adds nothing beyond long-vol-at-the-close exposure).
- **FALSIFICATION EXPERIMENT:** replicate the exact published spec (14-day, multiplier 1) on our canonical NQ merge with C1 + 1 extra tick stop-slippage; compare against the time-of-day/vol-matched random-entry null (1,000 bootstrap draws); walk-forward 2010-style parameter set frozen before touching 2023–2025. Falsified if net expectancy ≤ 0, if it fails the matched null, or if PBO of the (lookback, multiplier) grid > 0.5. Pre-registered concern to test: author reports the family was flat 2010–2017 — check regime dependence explicitly.
- **PRIORITY:** 1

### H3 — Bounce artifact control: sub-minute reversal in NQ Last-trade data is Roll noise

Methodological guardrail hypothesis that protects every DR-S07 experiment. Roll (1984): 1-tick spread ⇒ trade-price changes have autocovariance ≈ −s²/4 ⇒ fading the last trade-price tick "earns" ~½ tick gross, which is *mechanically* < C1 and vanishes on midquotes.

- **ECONOMIC MECHANISM:** none — alternation of buyer/seller-initiated trades between bid and ask creates spurious negative autocorrelation in transaction prices (Roll 1984); it is a measurement artifact, not a tradable phenomenon.
- **OBSERVABLE VARIABLES:** tick-by-tick (or 1-s) Last-price changes; first-lag autocovariance; (verification leg) midquote changes if/when L2 is confirmed.
- **EXPECTED HORIZON:** 1 trade to ~1 minute.
- **EXPECTED SIGN:** negative autocorrelation on Last data; **≈ 0 on midquotes**; implied gross edge ≈ ½ tick ≪ C1 = 2.872 ticks.
- **REQUIRED DATA (L1-L4):** **L1** for the artifact measurement; **L2** for the kill-confirmation (this is the single strongest argument for completing the bid/ask data audit).
- **RETAIL EXECUTABILITY:** none — the hypothesis exists to *prove* non-executability and to calibrate how much apparent reversal our L1 data fabricates.
- **SIMPLE NULL:** (inverted use) first-lag autocovariance on Last data equals −s²/4 within confidence bands, and implied round-trip capture < C1.
- **FALSIFICATION EXPERIMENT:** compute lag-1..lag-60 autocovariances of NQ 1-s Last returns over the canonical window, convert to implied ticks-per-round-trip; the "artifact" verdict stands unless implied capture > C1 at some lag structure — in which case (and only then) escalate to an L2 midquote re-measurement before any strategy work. Falsifies (i.e., surprises us) only if reversal net of C1 survives on midquotes.
- **PRIORITY:** 1 (cheap, runs first, gates all other DR-S07 work)

### H4 — Failed-sweep snapback at salient levels in high-volatility states

Osler-type stop clusters sit just beyond round numbers and prior-day extremes; a fast push through such a level that stalls (fails to make new extremes within k bars) indicates the stop inventory is exhausted and the move was liquidity- not information-driven; price snaps back toward the level (HKS: liquidity-imbalance reversal < 1 hour; flash-event round trips at the limit).

- **ECONOMIC MECHANISM:** positive-feedback stop cascades overshoot fundamental value; once triggered inventory is exhausted, liquidity providers reprice back (Nagel: reversal P&L = liquidity-provision compensation, increasing in vol).
- **OBSERVABLE VARIABLES:** salient levels (prior-day high/low, overnight high/low, round 100s/50s in NQ index points); penetration event (range breach ≥ m ticks within ≤ n minutes); failure signature (no new extreme for k bars); realized-vol state; time of day.
- **EXPECTED HORIZON:** 2–30 minutes post-failure.
- **EXPECTED SIGN:** reversion toward (and modestly through) the breached level; conditional expectancy must be ≥ ~6 ticks gross to clear C1 with margin — plausible only when 5-min ranges are ≥ 15–20 ticks, i.e., high-vol regimes and RTH open/close hours.
- **REQUIRED DATA (L1-L4):** **L1** for a bar-based version (breach-and-stall is detectable on 1-min bars); **L3/L4 desirable** to distinguish a true sweep (aggressive volume consuming depth) from a quote fade — flag: without L2+ the false-positive rate on "sweeps" is unknown.
- **RETAIL EXECUTABILITY:** moderate — event frequency ~1–5/day; entries are limit-style near the failed extreme (may miss fills); stop beyond the impulse extreme defines risk of ~equal ticks; slippage in exactly these states is elevated — budget 2 ticks extra.
- **SIMPLE NULL:** conditional on a level breach, subsequent k-bar returns are indistinguishable from time-of-day/vol-matched unconditional returns (levels carry no information; "failure" is just mean-reversion of vol).
- **FALSIFICATION EXPERIMENT:** event study on canonical window: all breaches of prior-day H/L and round-100s; split by failure vs continuation at k ∈ {3,5,10} 1-min bars; measure forward 5/15/30-min returns vs matched null; then cost sim with C1 + 2 ticks state-slippage. Falsified if snapback expectancy net of costs ≤ 0 across all (m,n,k) cells or if significant cells < what FDR control at q=0.1 expects by chance.
- **PRIORITY:** 2

### H5 — Open-drive reversal after extreme opens (Grant-Wolf-Yu modernized)

Large opening displacement (overnight gap + first 15 min beyond a high percentile) partially reverses intraday; published in S&P futures 1987–2002 but killed by that era's costs; our cost floor is lower in real terms and NQ's tick/spread economics are better than 1990s S&P pit costs — the effect deserves one modern preregistered test.

- **ECONOMIC MECHANISM:** overnight/open order imbalances from gap-chasing retail and margin-driven flows overshoot; RTH liquidity supply reprices toward pre-open consensus (overreaction correction, stronger after up-opens per GWY — consistent with short-covering asymmetry).
- **OBSERVABLE VARIABLES:** overnight gap; r(09:30→09:45); percentile thresholds from trailing 250 days; VIX-type vol state; day-of-week.
- **EXPECTED HORIZON:** 30–120 minutes (fade entered 09:45, closed by 11:30 or on reversion to open price).
- **EXPECTED SIGN:** reversal (fade the open drive), stronger after large **up** opens.
- **REQUIRED DATA (L1-L4):** **L1 only.**
- **RETAIL EXECUTABILITY:** high mechanically (≤ 1 trade/day, liquid hours); economically marginal — the literature's gross effect was only a few ticks in normal-vol states; viability likely confined to top-decile gap days where the conditional move is tens of ticks.
- **SIMPLE NULL:** post-09:45 returns conditional on extreme opens equal unconditional time-matched returns; net-of-C1 expectancy ≤ 0.
- **FALSIFICATION EXPERIMENT:** quantile event study of forward 30/60/120-min returns conditional on open-displacement deciles over the canonical window; sim only the top decile with C1. Falsified if the reversal coefficient ≥ 0 (no reversal) or net expectancy ≤ 0; also record whether the GWY up/down asymmetry replicates — a failed asymmetry is evidence the original was sample noise.
- **PRIORITY:** 2

### H6 — Announcement-window continuation: first post-release minute predicts the next 15–30 minutes on high-surprise days

ADBV show conditional-mean jumps complete within minutes, but the *initial* jump direction on large surprises identifies the day's information sign while gamma/rebalancing feedback (H1 mechanism) and slower-moving capital extend it; Kurov et al. show E-mini prices process macro information over ~30-min windows around releases.

- **ECONOMIC MECHANISM:** staggered information incorporation: instantaneous repricing by fast traders is incomplete when surprises are large (inventory limits, vol-scaled position caps), leaving drift as slower capital and hedging flows arrive.
- **OBSERVABLE VARIABLES:** announcement calendar (CPI, NFP, FOMC, PPI, retail sales); surprise magnitude (consensus vs release, normalized); r(release→release+60 s); realized vol in the window.
- **EXPECTED HORIZON:** enter 60–120 s post-release, exit +15 to +30 min.
- **EXPECTED SIGN:** continuation of the first-minute move, monotone in |surprise|; bad-news moves larger (ADBV asymmetry).
- **REQUIRED DATA (L1-L4):** **L1** + external announcement/consensus data.
- **RETAIL EXECUTABILITY:** moderate — a handful of events/month; conditional moves on CPI/NFP days are 40–200 NQ ticks so C1 is small, BUT spread widens to 2–4 ticks and book thins exactly then: cost model must use C1 + 3 ticks, and entries must be ≥ 60 s post-release (never inside the first second — that is Zone A).
- **SIMPLE NULL:** conditional on |surprise| > 1 σ, the post-first-minute return is sign-independent of the first-minute return (all adjustment truly completes within a minute, per strong-form ADBV).
- **FALSIFICATION EXPERIMENT:** event study over all 8:30/10:00/14:00 ET releases in the canonical window: regress r(+1→+30 min) on signed first-minute return × |surprise|; sim with C1 + 3 ticks. Falsified if slope ≤ 0 or net expectancy ≤ 0; separately report FOMC days (known distinct dynamics) to avoid one event class carrying the result.
- **PRIORITY:** 2

### H7 — Time-of-day periodicity in NQ returns and signal efficacy (HKS/Bogousslavsky specialized)

Half-hour-of-day is a first-class conditioning variable: flows (and therefore both momentum and reversal efficacy) recur at daily lags. Concretely: any signal from H2/H4/H5 should have half-hour-of-day-dependent expectancy, and NQ half-hour returns themselves may show same-half-hour continuation across days.

- **ECONOMIC MECHANISM:** institutional order scheduling (TWAP/VWAP calendars, ETF creation/redemption, option-hedge rebalancing) repeats at the same clock time daily (Bogousslavsky's infrequent rebalancing), creating periodic flow pressure.
- **OBSERVABLE VARIABLES:** 13 RTH half-hour returns per day (plus overnight blocks); lagged same-half-hour returns at lags 1–40 days; half-hour dummies interacted with H2/H4/H5 signals.
- **EXPECTED HORIZON:** 30-minute blocks, effects persisting up to 40 trading days of lags (HKS).
- **EXPECTED SIGN:** positive same-half-hour autocorrelation at daily-multiple lags; strongest in first and last half-hours.
- **REQUIRED DATA (L1-L4):** **L1 only.**
- **RETAIL EXECUTABILITY:** as a standalone signal, low (HKS magnitudes are bps-per-half-hour ≈ single-digit NQ ticks — near C1); as a **conditioning layer** on H1/H2/H4/H5 it costs nothing and can materially raise their conditional expectancy.
- **SIMPLE NULL:** half-hour-of-day dummies and daily-lag same-half-hour returns add no explanatory power for NQ half-hour returns (F-test), and do not alter H2/H4/H5 expectancies.
- **FALSIFICATION EXPERIMENT:** panel regression of NQ half-hour returns on same-half-hour lagged returns (lags 1–40) with day and half-hour fixed effects on the canonical window; then re-run H2/H4/H5 event studies with half-hour interactions. Falsified (as conditioning layer) if no half-hour cell shifts net expectancy by ≥ 1 tick.
- **PRIORITY:** 3 (runs as an overlay analysis, not a standalone campaign slot)

### H8 — Minutes-scale order-flow imbalance on L1: preregistered null-confirmation

Signed trade imbalance (tick-rule) over trailing 1–5 min predicts next 1–5 min NQ returns statistically but delivers < 1 tick gross — i.e., we expect to *confirm* the pattern claimed by the unverified SSRN 7067778 study (46/46 predictable, 0/46 profitable) in our own data. Value: calibrates exactly how far inside the cost floor Zone B sits in NQ 2023–2025, and creates the reusable OFI feature stack.

- **ECONOMIC MECHANISM:** inventory-mediated transient impact of persistent metaorder flow (Cont-Kukanov-Stoikov linearity; Bouchaud propagator): aggregated aggressor imbalance forecasts the tail of its own impact, already mostly incorporated.
- **OBSERVABLE VARIABLES:** tick-rule signed volume aggregated over 1/3/5-min windows; trade count imbalance; volume-weighted variants; realized vol normalizer.
- **EXPECTED HORIZON:** 1–5 minutes.
- **EXPECTED SIGN:** positive (continuation) but with gross magnitude ≈ 0.2–1.0 tick per event — **below C1 by construction of our prior**.
- **REQUIRED DATA (L1-L4):** **L1** (tick-rule signing needs trades only; true signing would need L2 — flag signing error ~10–20% without quotes).
- **RETAIL EXECUTABILITY:** expected NONE at market-order costs; the experiment's purpose is to measure the gap (in ticks) between statistical and economic significance in our market, and to leave a calibrated feature library for conditioning other hypotheses.
- **SIMPLE NULL:** OFI coefficient = 0 (we expect to REJECT this) AND net-of-C1 expectancy of the best decile ≤ 0 (we expect NOT to reject this) — the pre-registered prediction is the conjunction.
- **FALSIFICATION EXPERIMENT:** on the canonical window, decile analysis of forward 1/3/5-min returns by trailing OFI; report gross ticks per decile and net-of-C1 P&L of a top/bottom-decile rule. The *interesting* falsification is the top decile clearing C1 net — that would overturn our Zone B verdict and justify escalation to an L2-based version.
- **PRIORITY:** 3 (knowledge/calibration value; strictly time-boxed)

---

## 4. Warnings

1. **The cost floor is the thesis.** Every published sub-minute effect in deep index futures is worth ~0.1–1 tick gross; C1 = 2.872 ticks. The literature that *reports costs* (Grant-Wolf-Yu 2005; the unverified 7067778; Quantitativo's slippage sensitivity) uniformly finds reversal/flow effects die at retail costs while session-anchored flow effects survive. Any scalping-lab result showing net edge at < 5-min horizons on market orders should be presumed a bug (look first for bounce, look-ahead, or fill fantasy).
2. **Bid-ask bounce fabricates reversal on our Last-trade data** (Roll 1984): ~½ tick of fake fade-edge is built into L1 at the shortest lags. H3 must run before any DR-S07 strategy claim is graded.
3. **SSRN 7067778 is unverified** — 403-walled and unindexed everywhere as of 2026-08-07; its 46/46 / 0/46 headline is campaign-brief hearsay until a human fetches it. Do not cite it as evidence in downstream documents; cite this report's §1.4.
4. **Intraday momentum is price pressure, not information** (Baltussen et al.: it reverts over following days) — sizing must assume the edge is regime-dependent (was flat 2010–2017 in the practitioner ES replication) and can invert if gamma positioning flips (dealer long-gamma regimes damp the close instead of amplifying it).
5. **Win-rate preference vs payoff structure:** the best-documented executable family (H1/H2) wins ~36–38% of trades with ~2.2:1 payoff. Cost-adjusted expectancy first; win rate is a preference, not a filter.
6. **Multiple testing:** this document registers 8 hypotheses with explicit nulls; the campaign's own PBO findings (0.48–0.90 on parameter selection) apply with full force to the (lookback, multiplier, threshold) grids in H2/H4/H5 — grids must be declared before contact with the canonical window's out-years.
