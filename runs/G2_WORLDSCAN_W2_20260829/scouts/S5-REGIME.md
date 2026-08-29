# S5-REGIME — Cross-Asset Regime Scout (GENESIS II World Scan Wave 2)

DOMAIN SUMMARY (3 lines):
The sizing literature splits cleanly: vol-targeting the MARKET index is the one policy that survives peer-reviewed critique (Moreira-Muir alpha; Cederburg's out-of-sample failure applies to factor portfolios, and Barroso-Detzel show the market version survives transaction costs), and "act only in the extremes" (Bongaerts) survives with far less turnover — directly relevant to sizing the incumbent at ~$25-33/RT. Regime states with documented performance impact and observables we already own: Mahalanobis turbulence (Kritzman), VIX-premium decline (Cheng), VIX term-structure slope as a variance-risk state (Johnson), stock-bond correlation regime (Molenaar/FAJ 2024), and daily risk-appetite composites (Bekaert-Engstrom-Xu, downloadable). Drawdown-throttling is the honest negative: the Man/JPM "Drawdowns" work finds it cuts risk AND expected return — geometric-growth benefit must be demonstrated, not assumed.

METHOD NOTE: WebSearch was refused (session budget exhausted at 200/200), so per constraints all sourcing fell back to WebFetch on canonical/mirror pages (NBER, IDEAS/RePEc, Crossref API, Man Institute, author sites). SSRN, DuckDuckGo, Bing, Brave, Mojeek, AQR.com and pm-research.com were blocked (403/captcha/paywall); every URL cited below was actually fetched and returned the described content on 2026-08-29.

---

[LEAD id=S5-01]
SOURCE: https://www.nber.org/papers/w22208 (Moreira & Muir, "Volatility Managed Portfolios", NBER WP 22208; published J. Finance 72(4), 2017) | ACCESSED: 2026-08-29 | AUTHOR: Alan Moreira, Tyler Muir | DATE: April 2016 / JF 2017
TYPE: paper
CLAIM: Portfolios that scale exposure down when recent realized volatility is high (and up when low) earn large alphas and substantially higher Sharpe ratios on the market factor (plus value, momentum, profitability, carry), because changes in volatility are not offset by proportional changes in expected returns.
EVIDENCE: peer-reviewed
MARKET: US equity market factor + equity factors + FX carry HORIZON: monthly rebalance, multi-decade sample
MECHANISM: Vol is highly forecastable at 1-month horizon while expected return is not, so risk/return ratio deteriorates in high-vol states; de-levering there raises the portfolio's realized Sharpe and mean-variance utility.
OBSERVABLES: previous-month realized variance of the index (computable from NQ 1-min); exposure weight proportional to c/RV², leverage-capped.
NOVELTY: POLICY
PRIOR: MED — strongest-pedigree sizing result in the literature, but factor-level results died out-of-sample (see S5-03); the market-index version is the survivor.
CHEAPEST-FALSIFIER: NQ daily series built from owned 1-min 2006-2026: weight_t = min(2, c/RV²_{prev 21d}), monthly rebalance with a no-trade band, $33/RT on rebalancing contracts; compare geometric growth + Sharpe vs constant-exposure control at matched mean exposure; frozen era split 2006-2022 / 2023-2026; circular-shift null for the timing component.
INDEPENDENCE: Root of the whole vol-managed family; S5-02/03/04/06 all descend from it.
[/LEAD]

[LEAD id=S5-02]
SOURCE: https://www.man.com/maninstitute/the-impact-of-volatility-targeting | ACCESSED: 2026-08-29 | AUTHOR: Campbell R. Harvey, Russell Korgaonkar (Man Group; JPM 45(1) 2018 paper with Hoyle, Rattray, Sargaison, van Hemert) | DATE: 2018-05-30
TYPE: vendor
CLAIM: Across 60+ assets with daily data from 1926, volatility targeting improves Sharpe ratios for RISK assets (equities, credit) and balanced/risk-parity portfolios, but is negligible for bonds, currencies, commodities; it reduces the likelihood of extreme returns and maximum drawdowns for all asset classes because the leverage effect makes vol-scaling embed short-term momentum.
EVIDENCE: backtest-screenshot (practitioner-journal backtest across 60+ assets, 1926-2017)
MARKET: global multi-asset incl. US equity index futures HORIZON: daily vol estimate, ~monthly effective turnover
MECHANISM: Negative return-vol correlation (leverage effect) in equities means cutting size after vol spikes both avoids left tail and implicitly rides short-term momentum.
OBSERVABLES: EWMA/rolling realized vol of NQ (1-min or daily); target = k/sigma-hat with leverage cap.
NOVELTY: POLICY
PRIOR: MED-HIGH for tail/drawdown reduction (replicated many times); MED for net Sharpe gain after our cost reality.
CHEAPEST-FALSIFIER: Same harness as S5-01 but EWMA-20d sigma target; gate on three preregistered clauses: (1) Sharpe delta ≥ 0 net of $33/RT, (2) 1%-tail of monthly returns improves, (3) max drawdown improves — with the always-long constant-exposure control in the same wave; both eras.
INDEPENDENCE: Same family as S5-01; Man Group also authored S5-11.
[/LEAD]

[LEAD id=S5-03]
SOURCE: https://ideas.repec.org/a/eee/jfinec/v138y2020i1p95-117.html (Cederburg, O'Doherty, Wang, Yan, "On the performance of volatility-managed portfolios", JFE 138(1) 2020) | ACCESSED: 2026-08-29 | AUTHOR: Scott Cederburg, Michael S. O'Doherty, Feifei Wang, Xuemin Yan | DATE: 2020
TYPE: paper
CLAIM: Across 103 equity strategies, volatility-managed portfolios show significantly positive spanning-regression alphas yet do NOT systematically outperform head-to-head; real-time implementations generally earn LOWER certainty-equivalent returns and Sharpe ratios than unmanaged buy-and-hold, due to structural instability in the spanning regressions.
EVIDENCE: peer-reviewed
MARKET: 103 US equity anomaly/factor portfolios HORIZON: monthly, real-time out-of-sample design
MECHANISM: The in-sample scaling constant is not knowable ex ante; parameter instability converts paper alpha into realized underperformance — a pure overfitting/implementation-gap mechanism.
OBSERVABLES: none new — this is the mandatory control design (expanding-window real-time scaling constant) for any S5-01/02 test.
NOVELTY: POLICY (negative control — defines the falsifier standard)
PRIOR: HIGH that the critique is real — it is the reason any vol-sizing test here must be real-time, not full-sample.
CHEAPEST-FALSIFIER: In the S5-01 harness, estimate the scaling constant c only from expanding past data (no full-sample c); PASS requires the real-time version to beat unmanaged on certainty-equivalent — exactly the clause their 103-strategy evidence says usually fails except for the market portfolio.
INDEPENDENCE: Direct response to Moreira-Muir (S5-01).
[/LEAD]

[LEAD id=S5-04]
SOURCE: https://ideas.repec.org/a/eee/jfinec/v140y2021i3p744-767.html (Barroso & Detzel, "Do limits to arbitrage explain the benefits of volatility-managed portfolios?", JFE 140(3) 2021) | ACCESSED: 2026-08-29 | AUTHOR: Pedro Barroso, Andrew Detzel | DATE: 2021
TYPE: paper
CLAIM: After transaction costs, volatility management of asset-pricing factors OTHER than the market produces zero abnormal returns and significantly reduces Sharpe ratios; the volatility-managed MARKET strategy outperforms and is robust to costs — though its edge concentrates when sentiment is high.
EVIDENCE: peer-reviewed
MARKET: US equity market + factors HORIZON: monthly, cost-adjusted, multi-decade
MECHANISM: Vol-scaling the index is cheap to trade (futures), so the alpha survives; factor legs are cost-heavy; sentiment traders underreact to vol shifts, creating the window.
OBSERVABLES: same as S5-01 plus explicit turnover accounting in contracts.
NOVELTY: POLICY
PRIOR: MED-HIGH — it is the peer-reviewed answer to "what survived" the Cederburg critique: index-level vol management, net of costs.
CHEAPEST-FALSIFIER: Add to the S5-01 harness a preregistered turnover clause: measure contracts traded per year, charge $33/RT, and PASS only if net-of-cost Sharpe ≥ unmanaged; report gross vs net side by side so cost drag is never hidden (method rule: leverage/sizing must not masquerade as information alpha).
INDEPENDENCE: Same family; responds to S5-01 and S5-03.
[/LEAD]

[LEAD id=S5-05]
SOURCE: https://ideas.repec.org/a/taf/ufajxx/v76y2020i4p54-71.html (Bongaerts, Kang, van Dijk, "Conditional Volatility Targeting", FAJ 76(4) 2020) | ACCESSED: 2026-08-29 | AUTHOR: Dion Bongaerts, Xiaowei Kang, Mathijs van Dijk | DATE: 2020
TYPE: paper
CLAIM: Conventional vol targeting improves performance inconsistently across global equity markets; adjusting risk exposure ONLY in the extreme high- and low-volatility states consistently enhances Sharpe ratios and reduces drawdowns/tail risks with LOW turnover and leverage.
EVIDENCE: peer-reviewed
MARKET: major global equity indices + momentum HORIZON: daily vol states, infrequent trades
MECHANISM: The risk-return tradeoff is only reliably broken in vol extremes; trading only there captures most of the benefit while avoiding the cost drag that kills continuous targeting.
OBSERVABLES: realized-vol state deciles (NQ 1-min RV); de-lever only in top decile, re-lever only in bottom decile.
NOVELTY: POLICY
PRIOR: MED-HIGH — purpose-built for a $25-33/RT cost reality; the most implementable form of the family for sizing the 11:48 incumbent.
CHEAPEST-FALSIFIER: NQ 2006-2026 daily: exposure 0.5x when 21d RV in top decile (expanding-window deciles), 1.5x in bottom decile, 1x otherwise, leverage cap 2x; compare net geometric growth/Sharpe/maxDD vs (a) buy-and-hold, (b) continuous vol targeting from S5-02, in the same wave; both eras; count round-trips explicitly.
INDEPENDENCE: Response to S5-01/S5-02 family.
[/LEAD]

[LEAD id=S5-06]
SOURCE: https://ideas.repec.org/a/oup/rfinst/v22y2009i11p4463-4492.html (Bollerslev, Tauchen, Zhou, "Expected Stock Returns and Variance Risk Premia", RFS 22(11) 2009) | ACCESSED: 2026-08-29 | AUTHOR: Tim Bollerslev, George Tauchen, Hao Zhou | DATE: 2009
TYPE: paper
CLAIM: The variance risk premium (model-free implied variance minus realized variance from high-frequency data) positively predicts aggregate stock-market returns, with the strongest predictability at the quarterly horizon, dominating P/E, default spread, and consumption-wealth ratio.
EVIDENCE: peer-reviewed
MARKET: S&P 500 aggregate HORIZON: 1-3 months (quarterly strongest)
MECHANISM: VRP proxies aggregate risk aversion / economic uncertainty premia; when compensation for variance risk is high, subsequent equity returns are high — a sizing tilt, not a directional trade.
OBSERVABLES: VIX²/VXN² (certified daily) minus trailing realized variance from owned NQ/ES 1-min; monthly series.
NOVELTY: REPRESENTATION
PRIOR: MED — heavily replicated in-sample, horizon (quarterly) is long relative to campaign cadence; use only as a monthly sizing state.
CHEAPEST-FALSIFIER: Build VRP_t = VXN²_t − RV_t(22d, NQ 1-min) monthly 2006-2026; predictive regression of next-month and next-quarter NQ excess return on VRP with circular-shift null and era split; PASS = positive slope stable across eras at preregistered MDE; then one sizing overlay test (exposure ∝ VRP tercile) vs unconditional control in the same wave.
INDEPENDENCE: VIX-complex family with S5-08/S5-13 (share observables); distinct from the dead in-house daily-VX-basis direction test — different observable (implied minus realized variance, not futures-minus-spot) and different use (sizing tilt).
[/LEAD]

[LEAD id=S5-07]
SOURCE: https://ideas.repec.org/a/taf/ufajxx/v66y2010i5p30-41.html (Kritzman & Li, "Skulls, Financial Turbulence, and Risk Management", FAJ 66(5) 2010) | ACCESSED: 2026-08-29 | AUTHOR: Mark Kritzman, Yuanzhen Li | DATE: 2010
TYPE: paper
CLAIM: Financial turbulence measured as the Mahalanobis distance of cross-asset daily returns (extreme moves + correlation breakdown) identifies 1987/9-11/2008-type episodes; returns to risky strategies are substantially lower and turbulence PERSISTS for weeks, so scaling risk exposure down when turbulence is high is a documented risk-management use.
EVIDENCE: peer-reviewed
MARKET: multi-asset (global equities, bonds, FX, commodities) HORIZON: daily measure, multi-week persistence
MECHANISM: Turbulence persistence means today's cross-asset statistical irregularity forecasts elevated near-term risk, while returns in turbulent states are lower — asymmetry a throttle can harvest.
OBSERVABLES: rolling mean/covariance of owned multi-market daily returns; Mahalanobis distance of today's return vector.
NOVELTY: REPRESENTATION
PRIOR: MED — mechanism is persistence of vol/correlation (real), but overlaps heavily with plain RV scaling; must beat the univariate-vol control (RV-tercile conditioning already measured DEAD as a signal — the test here is sizing, and the control must be univariate vol sizing).
CHEAPEST-FALSIFIER: Turbulence index from owned multi-market daily returns (60d rolling cov, expanding thresholds); NQ exposure 0.5x when turbulence > 90th percentile; compare geometric growth vs constant AND vs RV-only throttle (matched design) in the same wave — PASS only if the cross-asset term adds beyond univariate RV; both eras.
INDEPENDENCE: Same shop as S5-12 (Kritzman/State Street).
[/LEAD]

[LEAD id=S5-08]
SOURCE: https://ideas.repec.org/a/oup/rfinst/v32y2019i1p180-227..html (Cheng, "The VIX Premium", RFS 32(1) 2019) | ACCESSED: 2026-08-29 | AUTHOR: Ing-Haw Cheng | DATE: 2019
TYPE: paper
CLAIM: The premium of VIX futures over a statistical forecast of VIX at settlement predicts VIX-futures returns with coefficient near one, and — counterintuitively — the premium FALLS or stays flat as risk rises; a falling premium forecasts INCREASING market volatility and risk ahead (falling hedging demand drives it).
EVIDENCE: peer-reviewed
MARKET: VIX futures / S&P 500 complex HORIZON: days-weeks
MECHANISM: Hedgers withdraw as risk builds, compressing the premium before vol events — an early-warning state for de-risking rather than a directional signal.
OBSERVABLES: certified VX daily settle minus a frozen econometric forecast of VIX at expiry (AR-type, from certified VIX daily); NOT the raw basis.
NOVELTY: REPRESENTATION
PRIOR: LOW-MED — in-house daily VX basis is already dead as an NQ signal; this survives only if the forecast-adjusted premium contains information beyond the raw basis, which is exactly the falsifier.
CHEAPEST-FALSIFIER: 2006-2026: compute premium_t = VX1_t − Ê[VIX_expiry] (expanding AR(5) on log VIX, frozen spec); sort into deciles; test next-5d NQ realized vol and next-5d NQ return per decile, with raw basis as the matched control in the same wave — PASS only if premium adds signal orthogonal to raw basis (else record the whole VX-derived family closed).
INDEPENDENCE: VIX-complex family with S5-06/S5-13; explicitly adjacent to the dead in-house daily-VX-basis test.
[/LEAD]

[LEAD id=S5-09]
SOURCE: https://ideas.repec.org/a/taf/ufajxx/v80y2024i3p17-36.html (Molenaar, Sénéchal, Swinkels, Wang, "Empirical Evidence on the Stock-Bond Correlation", FAJ 80(3) 2024; also Crossref DOI 10.1080/0015198X.2024.2317333 via https://api.crossref.org/works?query.bibliographic=Empirical+evidence+on+the+stock-bond+correlation+Molenaar+Swinkels&rows=5) | ACCESSED: 2026-08-29 | AUTHOR: Roderick Molenaar, Edouard Sénéchal, Laurens Swinkels, Zhenping Wang | DATE: 2024
TYPE: paper
CLAIM: The stock-bond correlation shows abrupt regime shifts after long stable periods, driven by inflation, real rates, and government creditworthiness; INCREASES in the correlation are associated with higher multi-asset portfolio risk and higher bond risk premia.
EVIDENCE: peer-reviewed
MARKET: US + international stocks/bonds, long histories HORIZON: regime scale (months-years), measurable daily
MECHANISM: When rates and equities sell off together (inflation-driven regime, e.g. 2022), bonds stop hedging equities, total portfolio vol rises, and equity drawdowns deepen — a slow risk-state for structural sizing.
OBSERVABLES: rolling 60d correlation of NQ daily returns vs Treasury-futures daily returns (owned multi-market daily); sign/level regime flag.
NOVELTY: REPRESENTATION
PRIOR: MED — regime is real and 2022 is the in-sample poster child; the open question is whether it forecasts NQ vol/drawdowns beyond lagged NQ vol itself.
CHEAPEST-FALSIFIER: 2006-2026: state = sign of trailing 60d NQ-vs-bond-futures correlation; compare next-month NQ realized vol and vol-targeted-overlay performance across states vs the matched unconditional control in the same wave; PASS = positive-corr state carries higher forward NQ vol after controlling for lagged RV (nested regression, circular-shift null); eras split (positive-corr regime is concentrated 2022+ — check old-regime count first, N-bound gate before running).
INDEPENDENCE: Parallel to AQR's Brixton et al JPM 2023 (10.3905/jpm.2023.1.459, paywalled — located via Crossref, not fetched); claims taken from Molenaar page only.
[/LEAD]

[LEAD id=S5-10]
SOURCE: https://www.nancyxu.net/risk-aversion-index and https://www.nber.org/papers/w25673 (Bekaert, Engstrom, Xu, "The Time Variation in Risk Appetite and Uncertainty", Management Science 2022) | ACCESSED: 2026-08-29 | AUTHOR: Geert Bekaert, Eric C. Engstrom, Nancy R. Xu | DATE: NBER WP March 2019; Mgmt Sci 2022; index data updated 2026-07-05
TYPE: paper
CLAIM: A daily risk-aversion index built as an optimal (GMM-estimated) combination of six financial variables — detrended earnings yield, Baa-Aaa spread, term spread, equity realized variance, corporate-bond realized variance, equity risk-neutral variance — separates risk appetite from economic uncertainty; the model's risk premiums outperform standard instruments for forecasting excess returns on equities and corporate bonds.
EVIDENCE: peer-reviewed
MARKET: US equities + corporate bonds HORIZON: daily index, monthly-quarterly forecasting
MECHANISM: Risk-neutral variance moves with risk aversion while credit spreads/corporate-bond vol track uncertainty; disentangling the two gives a cleaner risk-on/off state than any single input (this is the credit+vol composite the domain brief asks for).
OBSERVABLES: index is downloadable (Excel, daily+monthly) from the page; in-house analog computable from owned data: z-composite of VXN level, NQ realized variance, cross-asset correlation state.
NOVELTY: REPRESENTATION
PRIOR: MED — pedigree high, but forecasting horizon long and components (credit spreads, earnings yield) are not in owned data; treat the downloadable index as an owner-gated acquisition (free in dollars ≠ free in governance).
CHEAPEST-FALSIFIER: Owned-data analog first: monthly z-composite of {VXN, 21d NQ RV, 60d NQ-bond correlation} 2006-2026; sizing tilt by tercile vs unconditional control, circular-shift null, era split — run before any request to import the official index.
INDEPENDENCE: Independent of the vol-managed family; overlaps S5-06 (risk-neutral variance component).
[/LEAD]

[LEAD id=S5-11]
SOURCE: https://www.man.com/maninstitute/drawdowns ("Drawdowns", Man Institute; JPM 2020 version by van Hemert, Ganz, Harvey, Rattray, Sanchez Martin, Yawitch) | ACCESSED: 2026-08-29 | AUTHOR: Campbell R. Harvey, Eva Sanchez Martin, Darrel Yawitch (page byline) | DATE: 2020-09-01
TYPE: vendor
CLAIM: Drawdown-based de-risking rules are usable as a risk-reduction technique but affect BOTH expected return and risk; the paper's main contribution is quantifying the probability of hitting a given drawdown level under various return-distribution properties (i.e., drawdown throttles are not a free geometric-growth lunch).
EVIDENCE: backtest-screenshot (practitioner-journal simulation study)
MARKET: generic strategies / multi-asset HORIZON: strategy-level, months
MECHANISM: With near-zero return autocorrelation, past strategy drawdown carries little forward information, so cutting after drawdown mostly locks in lower exposure at random times; benefit exists only if returns have persistence (regime autocorrelation).
OBSERVABLES: running equity-curve drawdown of the incumbent 11:48 strategy and of always-long NQ.
NOVELTY: POLICY
PRIOR: LOW-MED for a geometric-growth IMPROVEMENT (the source itself is skeptical); HIGH value as the control that stops us adopting a folklore throttle.
CHEAPEST-FALSIFIER: Preregistered grid {5,10,15}% drawdown triggers, halve exposure until new high, applied to (a) always-long NQ daily 2006-2026 and (b) the 11:48 incumbent's daily P&L stream; PASS only if GEOMETRIC growth improves vs constant sizing at matched mean exposure — expected outcome per source is FAIL, which closes the axis cheaply.
INDEPENDENCE: Same shop as S5-02 (Man Group / Harvey).
[/LEAD]

[LEAD id=S5-12]
SOURCE: https://ideas.repec.org/a/taf/ufajxx/v68y2012i3p22-39.html (Kritzman, Page, Turkington, "Regime Shifts: Implications for Dynamic Strategies", FAJ 68(3) 2012) | ACCESSED: 2026-08-29 | AUTHOR: Mark Kritzman, Sébastien Page, David Turkington | DATE: 2012
TYPE: paper
CLAIM: Two-state Markov-switching models fitted to market turbulence, inflation, and economic growth identify "normal" vs "event" regimes; dynamically switching exposures based on forecast regime outperformed constant exposures and static allocation across stocks/bonds/cash — especially for investors who seek to avoid large losses.
EVIDENCE: peer-reviewed
MARKET: US multi-asset HORIZON: monthly regime forecasts
MECHANISM: Event regimes have persistently higher volatility and worse risk-adjusted returns; a hidden-Markov filter converts that persistence into an exposure state machine rather than a point forecast.
OBSERVABLES: 2-state HMM on turbulence (S5-07 index) or on NQ daily RV; filtered event-regime probability.
NOVELTY: POLICY
PRIOR: MED — regime persistence in vol is one of the most robust facts in finance; the risk is that HMM-on-RV collapses to RV-tercile conditioning, which is dead as a signal — must beat that control in sizing space.
CHEAPEST-FALSIFIER: Expanding-window 2-state Gaussian HMM on NQ daily RV 2006-2026 (spec frozen: 2 states, refit monthly); exposure 1x in normal state, 0.5x when P(event) > 0.7; geometric growth + maxDD vs constant AND vs the S5-05 decile throttle in the same wave; both eras.
INDEPENDENCE: Same shop as S5-07 (turbulence input).
[/LEAD]

[LEAD id=S5-13]
SOURCE: https://ideas.repec.org/a/cup/jfinqa/v52y2017i06p2461-2490_00.html (Johnson, "Risk Premia and the VIX Term Structure", JFQA 52(6) 2017; author page http://www.travislakejohnson.com/ also visited) | ACCESSED: 2026-08-29 | AUTHOR: Travis L. Johnson | DATE: 2017
TYPE: paper
CLAIM: The shape of the VIX term structure reflects the price of variance risk rather than expected future VIX; its second principal component (SLOPE) economically significantly predicts excess returns of S&P variance swaps, VIX futures, and S&P straddles at all maturities — i.e., an inverted/flat curve is a priced variance-risk state, not a VIX forecast.
EVIDENCE: peer-reviewed
MARKET: S&P 500 variance complex HORIZON: days-months
MECHANISM: Slope compresses/inverts when variance risk is expensively priced under stress; that state maps to elevated forward realized vol — usable as a vol-forecast input to a sizing throttle, not as an NQ direction signal.
OBSERVABLES: certified VX daily curve (VX1-VX2 slope or PC2 across maturities) + certified VIX/VXN daily.
NOVELTY: REPRESENTATION
PRIOR: LOW-MED — adjacent to the dead in-house daily-VX-basis direction test; alive only in the vol-forecasting/sizing lane, and must add beyond lagged RV.
CHEAPEST-FALSIFIER: 2006-2026 daily: slope_t = VX2−VX1 (certified); nested forecast of next-5d NQ realized vol from {lagged RV} vs {lagged RV + slope}; preregistered incremental-R² MDE with circular-shift null; if it passes, one sizing overlay (de-lever on inversion) vs RV-only throttle control in the same wave; both eras.
INDEPENDENCE: VIX-complex family with S5-06/S5-08; explicitly flagged against the dead daily-VX-basis test.
[/LEAD]

[LEAD id=S5-14]
SOURCE: https://www.philosophicaleconomics.com/2016/01/gtt/ ("Growth and Trend: A Simple, Powerful Technique for Timing the Stock Market") | ACCESSED: 2026-08-29 | AUTHOR: Philosophical Economics blog (pseudonymous; posts as philosophicalecon@gmail.com) | DATE: 2016-01-18
TYPE: trader
CLAIM: "Growth-Trend Timing" adds a macro growth filter to a monthly moving-average trend rule on US equities: obey the trend signal only when the growth indicators are deteriorating, stay long otherwise; the post's charts show the strategy's cumulative outperformance vs buy-and-hold ratcheting up in near-synchrony with a perfect-foresight recession-timing benchmark.
EVIDENCE: backtest-screenshot (long-history charts; exact percentages truncated on fetched page)
MARKET: S&P 500 total return, ~1930s-2015 HORIZON: monthly
MECHANISM: Trend rules pay for crash protection with whipsaw losses in non-recessionary corrections; gating the trend rule on macro deterioration removes most whipsaws while keeping recession exits — a geometric-growth policy, not a return signal.
OBSERVABLES: monthly MA state of NQ (owned); macro leg (retail sales/industrial production/employment growth) requires free FRED series — NOT in owned data (acquisition = owner-gated even though $0).
NOVELTY: POLICY
PRIOR: LOW-MED — widely read, never peer-reviewed, monthly cadence, and the macro leg is untestable on currently owned data; the trend leg alone is testable now.
CHEAPEST-FALSIFIER: Partial, owned-data-only: 10-month MA rule on NQ daily 2006-2026 net of $33/RT vs buy-and-hold, geometric growth and maxDD, era split — this bounds the trend leg's standalone value; the growth-filter increment is only testable after a free-FRED acquisition decision and goes to OWNER_QUEUE, not into this wave.
INDEPENDENCE: None (original to that blog; later popularized by allocation sites).
[/LEAD]
