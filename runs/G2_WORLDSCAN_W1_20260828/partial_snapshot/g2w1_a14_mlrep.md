# G2W1 A14-MLREP — Representation / ML scout — full notes (2026-08-28)

## Method note
WebSearch budget was exhausted (200/200) before this agent ran. All discovery was done via
WebFetch on site-native endpoints: arXiv export API (`export.arxiv.org/api/query`), arXiv abs
pages, Hudson & Thames site search (`?s=`), CrossRef API (`api.crossref.org`), OpenAlex API
(`api.openalex.org`), NBER paper pages. SSRN returned 403; Semantic Scholar API persistently 429;
pm-research.com is auth-walled (302 to idp.sams-sigma.com). Every URL cited below was actually
fetched this session.

## Harsh domain verdict
1. Almost nothing in the "alternative representation" literature reports a real OOS result on
   INDEX futures. Directional change = FX; signatures = synthetic + options hedging; meta-labeling
   journal series = controlled/synthetic experiments; info-bar comparisons = crypto.
2. The single directly-on-target paper found (MNQ 5-min regime classifier, arXiv 2605.11423) is a
   NEGATIVE result: regime structure is real but "does not translate into a robust standalone
   trading signal under realistic execution assumptions." That is the most credible datapoint in
   the whole domain and it is a caution, not an opportunity.
3. The one index-futures meta-labeling test that exists in public (Hudson & Thames 2019, E-mini
   S&P dollar bars) is a blog-grade backtest with admitted weak primary models and no bet sizing.

## Sources visited (all 2026-08-28)
- arXiv API queries: "directional change"+"intrinsic time"; "dollar bars"/"volume bars"; abs:"directional change"+trading; abs:"meta-labeling"/"triple-barrier"; signature+trading+q-fin; hidden Markov+futures+q-fin; Hurst+trading+q-fin; mixture of experts+q-fin; entropy+trading strategy+q-fin; meta-labeling (all-domain — zero finance hits, term collision); regime+intraday+futures; imbalance/run bars (zero finance hits); Hurst+futures.
- https://arxiv.org/abs/2605.11423 — Mesfin, "A Validated Volatility-Volume-Gap Classifier for Regime Identification in MNQ Intraday Data" (v2 2026-07-20). MNQ 5-min, 947 days 2021-2025. Features: overnight gap, first-30-min return, first-bar volume vs 20-day baseline. Expanding-window thresholds, walk-forward, net-of-cost, cross-year consistency gates. Trading conclusion negative. Quote: "The observed structure does not translate into a robust standalone trading signal under realistic execution assumptions."
- https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/ (2019-04-30). Primary models: 20/50 SMA crossover, 1.5σ Bollinger. S&P 500 E-mini dollar bars, OOS 2018-2019. MR precision 0.17→0.20, accuracy 17%→63%; TF precision 0.48→0.54. Quote: "All the metrics have improved across the board." Admits primaries "don't provide the best signals"; no bet sizing.
- https://hudsonthames.org/meta-labeling-a-toy-example/ (2019-04-23) — synthetic.
- CrossRef: JFDS trilogy verified — Joubert "Meta-Labeling: Theory and Framework" JFDS 4(3):31-44 2022, doi 10.3905/jfds.2022.1.098; Meyer/Joubert/Alfeus "Meta-Labeling Architecture" JFDS 4(4):10-24 2022, doi 10.3905/jfds.2022.1.108; Meyer/Barziy/Joubert "Meta-Labeling: Calibration and Position Sizing" JFDS 5(2):23-40 2023, doi 10.3905/jfds.2023.1.119. Volume Clock: JPM 2012, doi 10.3905/jpm.2012.39.1.019 (SSRN 10.2139/ssrn.2034858).
- OpenAlex (api.openalex.org filter by DOI): abstracts confirm — theory paper = "controlled experimentation" on strategy features (Sharpe/MDD improvements); architecture paper = feature-driven vs strategy-driven + inverse meta-labeling; calibration paper = six position-sizing algorithms, calibrated vs uncalibrated probabilities, "calibration significantly improves fixed position sizing performance" (Sharpe, MDD). No real index-futures OOS named in any abstract.
- https://arxiv.org/abs/2608.26158 — Fayyaz/Jabbar/Qureshi/Jalil, "A Frequency-Controlled Comparison of Tick- and Minute-Based Information Bars for Cryptocurrency Markets" (2026-07-07). Six bar types (dollar, volume, volatility, range, Renko, hybrid) from Binance aggTrade ticks vs 1-min OHLCV, BTCUSDT perp 2020-2025, shared adaptive EMA calibration, matched-frequency robustness. "tick volatility bars reduce serial dependence by 69% relative to the minute baseline"; "tick advantage is bar-type-specific." Statistical quality metrics only, no PnL.
- https://arxiv.org/abs/2309.00875 — Fanelli/Fontana/Rotondi, HMM stat-arb crude futures (v3 2026-02-13). Regime-switching mean-reverting spread, online filters; Brent/WTI/Shanghai. "statistical arbitrage strategies involving the Shanghai crude oil futures are profitable even under conservative levels of transaction costs and over different time periods."
- https://arxiv.org/abs/2308.15135 — Futter/Horvath/Wiese, "Signature Trading" (2023). Linear functionals on path signatures, mean-variance with exogenous signals; synthetic + unspecified market data; momentum and pairs examples. No futures OOS specifics in abstract. Follow-up seen in API listing: arXiv 2507.10701 Kernel Learning for Mean-Variance Trading Strategies (Futter/Muca Cirone/Horvath, 2025).
- https://arxiv.org/abs/0809.1040 — Glattfelder/Dupuis/Olsen, 12 scaling laws, Quantitative Finance 11(4) 2011. 13 FX pairs, purely descriptive. "the length of the price-curve coastline... surprisingly long."
- https://arxiv.org/abs/2309.15383 — Wu/Han, improved DC (asymmetric thresholds w/ decay, Bayesian opt) + RCD-HMM; forex tick; "significant increase in profit and reduction in risk"; OOS design unspecified. Quote: "DC is an alternative approach to sampling price data."
- https://www.nber.org/papers/w7613 — Lo/Mamaysky/Wang 2000 (JF). Kernel-regression pattern automation, US stocks 1962-1996; conditional vs unconditional distributions; "several technical indicators do provide incremental information"; informativeness only, no profits.
- https://arxiv.org/abs/1110.1727 — Schoeffel, DAX futures H=0.54±0.04, Euro futures H=0.51±0.03; Gaussian regime ≥8h, t(ν≈3) <1h; no trading.
- Also in Hurst API listing (not fetched abs): 0707.3321 Bartolozzi multi-scale correlations 1-min futures 2003-04; 0712.2910.
- https://arxiv.org/abs/2406.08742 — Ong/Herremans, DeepUnifiedMom (MMoE multi-task TSMOM across timeframes); equity indexes, FI, FX, commodities; "consistently outperforms benchmark models, even after factoring in transaction costs."
- https://arxiv.org/abs/2305.08241 — Press, NYSE 1-min ~1,000 stocks 2018-2022; H=0.465; ~60%/~100% annualized "if zero transaction costs."
- https://arxiv.org/abs/2503.06251 — Gupta et al., entropy-assisted pattern identification; "low local entropy" patterns; no instrument/period in abstract, no OOS.
- MoE listing also gave: 2111.15365 Expert Aggregation for Financial Forecasting (equities); 2207.07578 AlphaMix (US/China stocks); 2501.09636 LLMoE (stocks).
- Mixed/failed endpoints: papers.ssrn.com 403; api.semanticscholar.org 429 x5; pm-research.com auth redirect; quantresearch.org frameset (content not reachable in one hop).

## Gaps found (negative knowledge worth recording)
- Directional-change with a stated OOS PROFIT result on EQUITY INDEX FUTURES: none found on arXiv q-fin.
- Efficiency-ratio (Kaufman) as a state variable: zero academic tests surfaced via arXiv search.
- Imbalance/run bars: zero standalone arXiv papers (search hit only physics); the only quantitative comparison found is the crypto 2608.26158 paper.
- Hurst intraday on index futures: measured H≈0.5 (Schoeffel) — the representation itself argues against an exploitable fractal edge at these frequencies.

## SECOND PASS (same agent, continued 2026-08-28) — additional verified fetches
- arXiv API "momentum transformer + futures" -> 2601.05975 DeePM (Wood/Roberts/Zohren, submitted
  2026-01-09): 50 diversified futures, OOS 2010-2025, "net risk-adjusted returns roughly twice"
  classical trend following, ~50% over Momentum Transformer; directed-delay causal sieve, macro
  graph prior, EVaR-proxy distributionally-robust objective, strictly lagged cross-sectional
  attention; daily closes only. Also 2412.12516 (Mason et al 2024, equities extension).
- arXiv id_list 2112.08534 + 2105.13727: Momentum Transformer (Wood/Giegerich/Roberts/Zohren,
  2021-12-16) "outperforms benchmark time-series momentum and mean-reversion trading strategies"
  incl. costs, interpretable attention regimes; Slow Momentum with Fast Reversion (2021-05-28):
  backtest 1995-2020, CPD module improved Sharpe by ~1/3 overall and ~2/3 during 2015-2020.
- github.com/kieranjwood/trading-momentum-transformer: official code both papers; Quandl continuous
  futures, 100 tickers thru Dec 2021; full replication scripts; "Sample results will be made
  available soon" (results not bundled with repo).
- arXiv API "hidden Markov + intraday + trading" -> 2006.08307 Christensen/Godsill/Turner (2020)
  "Hidden Markov Models Applied To Intraday Momentum Trading With Side Information": IOHMM, 2-3
  latent momentum states, vol-ratio + seasonality side info; abs page confirms NO instruments and
  NO OOS trading results in abstract — methodology only.
- arXiv API "triple barrier" q-fin.TR -> 2404.01866 Bieganowski/Slepaczuk (2024) supervised
  autoencoder MLP + triple-barrier, S&P 500 / EURUSD / BTCUSD, 2010-2022, Sharpe/IR framing;
  admin-note overlap with 2411.12753 (crypto-only twin).
- Wikipedia 2010_flash_crash (fetched): VPIN original claim (JPM 37(2) Winter 2011, pp 118-128)
  "highest reading of 'toxic order imbalance' in previous history" one hour pre-crash; Andersen &
  Bondarenko rebuttal (J. Financial Markets, 2013/2014): pre-crash TR-VPIN surpassed on 71 prior
  days (11.7% of sample); BVC-VPIN exceeded on 189 days (31.2%). SSRN pages 403'd; used Wikipedia
  as citation carrier.
- IDEAS/RePEc fip/fedlwp/2001-021: Dueker & Neely -> J. Banking & Finance 31(2) 2007 279-296;
  Markov-switching + technical rules, OOS "excess returns modestly exceed those of standard
  technical rules", FX; forecast-accuracy stats mixed. (Not used as a lead — FX, superseded by
  better HMM-on-futures sources — kept as background.)
- NBER w7613 re-verified: Lo/Mamaysky/Wang 2000, kernel-smoothed patterns, stocks 1962-1996,
  informativeness only.
- arXiv id 0809.1040 re-verified: Glattfelder/Dupuis/Olsen 12 scaling laws, 13 FX pairs, ~3 orders
  of magnitude, Quantitative Finance 2011; descriptive only.
- arXiv API "E-mini + regime": 2605.11423 VVG/MNQ re-confirmed (947 days 5-min MNQ 2021-2025,
  expanding-window walk-forward with costs; regimes real; "None of the evaluated strategies satisfy
  the same validation criteria"). Hawkes pair 1302.1405 vs 1308.6756 noted, ceded to
  microstructure domain.
- arXiv API "mixture of experts + trading": 2501.09636 LLMoE (stocks+news, LLM router),
  2508.02686 Vallarino (30 US stocks, MSE only), 2409.15161 KAMoE (crypto/real estate) — none on
  futures; DeepUnifiedMom (2406.08742) remains the only MoE-on-futures paper found.
- arXiv id_list 2309.00875,2406.08742,1110.1727,2503.06251 — all four re-verified directly:
  * 2309.00875 Fanelli/Fontana/Rotondi HMM stat-arb: Brent/WTI/Shanghai crude futures, profitable
    "under conservative levels of transaction costs", multiple periods.
  * 2406.08742 DeepUnifiedMom (Ong/Herremans 2024): MMoE multi-task TSMOM; equity indexes, FI, FX,
    commodities; "consistently outperforms benchmark models" net of costs.
  * 1110.1727 Schoeffel (2011): DAX futures H=0.54±0.04, Euro futures H=0.51±0.03; universal
    statistical features; no trading.
  * 2503.06251 Gupta et al (2025): entropy-assisted pattern ID; claims "substantial predictive
    power" but no instrument, period, or OOS in abstract — methodology marketing; kept as dry-hole
    evidence, not a lead.
- Crossref re-verified both JFDS DOIs independently: 10.3905/jfds.2022.1.098 (Joubert 2022),
  10.3905/jfds.2023.1.119 (Meyer/Barziy/Joubert 2023).
- Hudson & Thames: my fetch of https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy/
  returned the full article (ES E-mini tick/dollar bars; SMA 20/50 + Bollinger 1.5sd primaries; RF
  meta-model; MR accuracy 17%->63%, precision 0.17->0.20; TF accuracy 48%->55%, precision
  0.48->0.54; "Meta-labeling improves the performance of the strategies"). Prior pass logged a
  longer URL variant; both resolve to the same article content.

## FINAL LEAD SET (18): 01 VPIN volume-clock, 02 Andersen-Bondarenko critique, 03 MNQ VVG negative,
04 SlowMom+CPD, 05 Momentum Transformer, 06 DeePM, 07 DeepUnifiedMom MMoE, 08 H&T meta-label ES,
09 JFDS calibration trilogy, 10 SAE+triple-barrier, 11 freq-controlled bars, 12 Wu/Han DC+HMM,
13 Glattfelder scaling laws, 14 HMM crude stat-arb, 15 Schoeffel Hurst futures, 16 Lo/Mamaysky/Wang,
17 Christensen IOHMM methodology-only, 18 Signature Trading theory-only.
Campaign cautions: calibration/sizing leads must hold gross exposure fixed (LEVERAGE masquerade
rule); any VPIN test must carry the Andersen-Bondarenko realized-vol control as its matched
unconditional control.
