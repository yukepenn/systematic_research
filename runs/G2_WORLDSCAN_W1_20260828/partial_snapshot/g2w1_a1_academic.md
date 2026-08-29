# G2W1 A1-ACADEMIC — full notes (accessed 2026-08-28)

## Method / trail
- WebSearch budget was exhausted (200/200) before this agent ran a single query. Fell back to WebFetch
  on site-native/API endpoints as permitted: arXiv Atom API (export.arxiv.org), Crossref REST API
  (api.crossref.org), Liberty Street Economics, Quantpedia site search (did not render results),
  DuckDuckGo html endpoint (CAPTCHA-blocked, abandoned), Semantic Scholar API (429-throttled, abandoned).
- SSRN abstract pages and alphaarchitect.com and newyorkfed.org staff-report pages return 403 to WebFetch;
  all SSRN identifications below come from Crossref metadata (title/author/DOI/URL), which is reliable.
- Every citation below was returned by a live API/page fetch this session. No URL invented.

## Verified sources (raw citations)
1. Baltussen, Da, Lammers, Martens, "Hedging Demand and Market Intraday Momentum", JFE 142(1) 2021,
   DOI 10.1016/j.jfineco.2021.04.029; SSRN 3760365 (DOI 10.2139/ssrn.3760365). Crossref-quoted abstract
   phrase: "the return during the last 30 minutes before the market close is positively predicted by the
   return during the rest of the day." International index futures incl. US; mechanism = hedging demand
   (leveraged ETFs + option dealers rebalance near close).
2. Boyarchenko, Larsen, Whelan, "The Overnight Drift", RFS 36(9) 2023, DOI 10.1093/rfs/hhad020;
   SSRN 3546173. Follow-up: "The Disappearing Overnight Drift", Liberty Street Economics 2026-07-01,
   DOI 10.59576/lse.20260701, URL https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/
   Fetched full post: original claim = ES drift concentrated 2:00-3:00am ET (European open), ~3.7%/yr,
   >60% of daily gains; 2021-2025 that window "averaged close to zero"; mechanism for disappearance =
   "compression in end-of-day imbalance dispersion" (closing order imbalance sd 6.5% -> 2.9%);
   NightShares ETFs closed after 14 months.
3. Hazelkorn, Moskowitz, Vasudevan, "Beyond Basis Basics: Liquidity/Leverage Demand and Deviations from
   the Law of One Price", NBER w26773 (DOI 10.3386/w26773), SSRN 3658560 & 3264926. (Published JF.)
   Equity index futures-cash basis deviations = leverage/liquidity demand; predicts futures returns;
   activity concentrated around quarterly rolls.
4. Etula, Rinne, Suominen, Vaittinen, "Dash for Cash: Monthly Market Impact of Institutional Liquidity
   Needs", RFS 33(1) 2020, 75-111, DOI 10.1093/rfs/hhz054; SSRN WP 2528692 (2014).
5. Kurov, Sancetta, Strasser, Wolfe, "Price Drift Before U.S. Macroeconomic News: Private Information
   about Public Announcements?", JFQA 2019, DOI 10.1017/s0022109018000625; SSRN 2637528. Crossref-quoted:
   prices "move in the 'correct' direction approximately 30 minutes before the release time"; ~40% of
   total adjustment happens pre-release.
6. Neuhierl, Weber, "Monetary Momentum", NBER w24748 (June 2018), https://www.nber.org/papers/w24748
   (fetched): drift up ~25 days before expansionary surprises; expansionary-minus-contractionary cum.
   return ~2.5% by announcement day, >4.5% within 15 days post-meeting; market-wide; Sharpe x4 claim.
7. Bogousslavsky, Muravyev, "Who trades at the close? Implications for price discovery and liquidity",
   Journal of Financial Markets, Nov 2023, DOI 10.1016/j.finmar.2023.100852; earlier WP "Should We Use
   Closing Prices? Institutional Price Pressure at the Close", SSRN 3485840.
8. Jegadeesh, Wu, "Closing Auctions: Nasdaq versus NYSE", JFE 143(3) 2022 1120-1139,
   DOI 10.1016/j.jfineco.2021.12.003. Also Goyal, Jegadeesh, Wu, "Price Impact: Continuous Trading,
   Closing Auctions, and Opening Auctions", SSRN 4300417 (2022), DOI 10.2139/ssrn.4300417.
9. Barbon, Buraschi, "Gamma Fragility", SSRN 3725454 (2020), DOI 10.2139/ssrn.3725454 — "large aggregate
   dealers' gamma imbalances and intraday momentum/reversal of stock returns".
   Barbon, Beckmeyer, Buraschi, Moerke, "The Role of Leveraged ETFs and Option Market Imbalances on
   End-of-Day Price Dynamics", SSRN 3925725 (2021), DOI 10.2139/ssrn.3925725.
   Shum, Hejazi, Haryanto, Rodier, "Intraday Share Price Volatility and Leveraged ETF Rebalancing",
   Review of Finance 2016, DOI 10.1093/rof/rfv061 — EOD volatility correlated with ratio of potential
   rebalancing trades to volume; "largest during the most volatile days".
10. Brogaard, Han, Won, "Does 0DTE Options Trading Increase Volatility?", SSRN 4426358 (2023),
    DOI 10.2139/ssrn.4426358 — 1 sd more 0DTE trading -> +9.10% vol relative to mean.
    Adams, Fontaine, Ornthanalai, "The Market for 0-Days-to-Expiration: The Role of Liquidity Providers
    in Volatility Attenuation", SSRN 4881008 (2024) — counterpoint (attenuation).
    Fagerlid, Skarpnes, "The Rise and Impacts of Zero Days-to-Expiration Options", SSRN 4724972 (2024).
11. Beckmeyer, Branger, Gayda, "Retail Traders Love 0DTE Options... But Should They?", SSRN 4404704
    (2023), DOI 10.2139/ssrn.4404704 — >75% of retail SPX option trades are 0DTE; retail loses.
12. Andersen, Thyrsgaard, Todorov, "Time-Varying Periodicity in Intraday Volatility", JASA 2019,
    DOI 10.1080/01621459.2018.1512864. Follow-ups: Andersen, Tan, Todorov, Zhang, "Testing mean
    stationarity of intraday volatility curves", Quantitative Economics 2025, DOI 10.3982/qe2644;
    Todorov, Andersen, Tan, Zhang, "On-Line Detection of Changes in the Shape of Intraday Volatility
    Curves", SSRN 5154142 (2025).
13. Muravyev, Ni, "Why do option returns change sign from day to night?", JFE Apr 2020,
    DOI 10.1016/j.jfineco.2018.12.006; SSRN 2820264. Index option (delta-hedged straddle) returns:
    ~-1% overnight vs +0.3% intraday per day — variance risk premium is earned in the DAY session;
    implied vs realized vol split day/night is systematically mispriced.
14. Mesfin, "Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures", arXiv 2605.04004v2
    (May 2026) — 14 signal families, 5-min MNQ 2021-2025, "none of the tested strategies satisfied all
    of these requirements" under ~2-point round-trip friction.
15. Lou, Polk, Skouras, "A tug of war: Overnight versus intraday expected returns", JFE 2019,
    DOI 10.1016/j.jfineco.2019.03.011 (context only; cross-sectional equities).
16. Boon Chuan Lim, "Overnight Adverse Selection: Evidence from Blue Ocean ATS and NASDAQ Regular
    Trading Hours", SSRN 6610883 (2026); same author SSRN 6651000 (order-size round-number anchoring
    overnight). Context: overnight session microstructure is thin/adversely selected — relevant risk
    note for any overnight-execution policy; not led separately.
17. Wysocki, "Harvesting the Volatility Risk Premium: A Learning-to-Rank Approach", arXiv 2608.24786v1
    (Aug 2026) — 0DTE SPX short-put ranking, OOS Sharpe 4.31-5.76 (options, not futures; not led).
18. Zhang, Cucuringu, Shestopaloff, Zohren, "Robust Detection of Lead-Lag Relationships in Lagged
    Multi-Factor Models", arXiv 2305.06704v3 (2023) — modern lead-lag detection on US equities minute
    data. Huth & Abergel arXiv 1111.7103 (classic). Not led as a block: minutes-scale cross-asset
    lead-lag is NOT falsifiable on data we own (NQ-only minute history; multi-market is daily-only) —
    noted as a data-gap flag instead of a lead.

## Domain-coverage notes / why some hunt areas have no lead
- Opening-auction imbalance: best post-2015 anchor found via Crossref is Goyal-Jegadeesh-Wu SSRN 4300417
  (opening vs closing auction price impact). Nasdaq opening-cross imbalance feeds are proprietary; folded
  the open into lead A1-10 rather than a stand-alone raw-data lead.
- Minutes-scale lead-lag with mega-cap baskets: literature exists (Huth-Abergel; Zhang et al 2023) but the
  repo owns no minute-level data for anything except NQ, so no cheap falsifier exists; flagged as data gap.
- Quantpedia search endpoint did not render server-side; no Quantpedia-only lead was needed since all
  candidate effects were traceable to primary papers.

## Cross-cutting warnings for the orchestrator
- Regime fragility is the theme of the 2023-2026 era: overnight drift (per NY Fed) and index-add effect
  (Greenwood-Sammon w30748, SSRN 4294297 "The Disappearing Index Effect", verified via Crossref) have both
  decayed post-publication. Any pre-2015-discovered intraday flow effect must be era-split at ~2020 and
  ~2022 (0DTE launch of Tue/Thu SPX expiries Nov 2022 completing the daily grid).
- Mesfin arXiv 2605.04004 is a direct negative prior on OHLCV-only intraday signals in exactly our
  instrument+cost regime; treat any lead whose falsifier is OHLCV-only with that prior.
