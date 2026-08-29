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
