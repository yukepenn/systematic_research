# G2W1 A13-CROSSMKT — full notes (2026-08-28)

## Method / constraints hit
- WebSearch budget was EXHAUSTED (200/200) before this agent ran a single query. Per instructions, fell back
  to WebFetch on site-native search/API endpoints: arXiv export API, Crossref REST API, Semantic Scholar API
  (429 rate-limited, abandoned), GitHub search API, WordPress-native `?s=` searches, Cboe CDN CSV endpoints,
  TradingView symbol/ideas pages (server-rendered), Bing HTML (mostly junk), DuckDuckGo HTML (captcha).
- Dead ends: reddit.com (blocked by tool), web.archive.org (blocked by tool), elitetrader.com 403,
  futures.io 403, quantifiedstrategies.com bot-wall, allstarcharts.com 403, imf.org blog 403,
  school.stockcharts.com SSL handshake failure, faculty.chicagobooth.edu PDF 404 (used Crossref DOI instead),
  BIS site search JS-only (direct pub page worked), Quantpedia ?s= returns pagination shell only.
- All URLs below were actually fetched and verified 2026-08-28 unless marked "(via listing)".

## Verified sources (fetch log)
1. arXiv API q-fin lead-lag list — got Huth-Abergel 1111.7103, Zhang et al 2305.06704, Li & Ferreira 2501.07135, etc.
2. arXiv API VIX+intraday — Ferreira & Medeiros 2112.15108 ("VIX strongest candidate predictor for intraday
   market returns"); Farokhnia & Osterrieder 2206.13138 (HF causality VIX & derivatives).
3. Crossref: Mourey/Shahrour/Șoiman 2025 FRL 10.1016/j.frl.2025.108661 "A crypto-stock weekend effect:
   Predicting Monday stock returns using weekend cryptocurrency returns" (metadata confirmed via
   api.crossref.org/works/10.1016/j.frl.2025.108661; abstract not in Crossref).
4. Crossref: Hasbrouck 2003 JF 10.1046/j.1540-6261.2003.00609.x "Intraday Price Formation in U.S. Equity
   Index Markets" (+ SSRN 10.2139/ssrn.252304 2001 WP version).
5. Crossref: Hong/Torous/Valkanov 2007 JFE 10.1016/j.jfineco.2005.09.010 "Do industries lead stock markets?";
   Tse 2015 JEmpFin 10.1016/j.jempfin.2015.10.003 reexamination.
6. Crossref: Marshall/Nguyen/Visaltanachoti 2013 JBF 10.1016/j.jbankfin.2013.05.014 "ETF arbitrage:
   Intraday evidence" (SSRN 1709599, 2010).
7. Crossref works/10.1093/qje/qjv027: Budish/Cramton/Shim QJE 2015 confirmed w/ abstract:
   "correlations completely break down" at HF; mechanical arb rents persist.
8. nber.org/papers/w20071: Ben-David/Franzoni/Moussawi "Do ETFs Increase Volatility?" — ETF ownership
   +1 SD -> ~16% higher daily vol; arbitrage layer is the mechanism; stronger where arbitrage is cheap.
9. bis.org/publ/work592.htm: Avdjiev/Du/Koch/Shin (fetch summary garbled one author name; canonical author
   list is Avdjiev, Du, Koch, Shin), 2016-11-15. "the dollar as proxy for the shadow price of bank leverage".
10. ijcb.org/journal/ijcb05q2a2.htm: Gürkaynak/Sack/Swanson 2005 IJCB — two factors (target + path);
    "statements having a much greater impact on longer-term Treasury yields".
11. michaeldbauer.com -> USMPD: U.S. Monetary Policy Event-Study Database (Bauer w/ Acosta, Ajello, Loria,
    Miranda-Agrippino), hosted at frbsf.org/research-and-insights/data-and-indicators/us-monetary-policy-event-study-database/
    — HF intraday-window changes around FOMC events: money-mkt futures, OIS, Treasuries/TIPS, stock indexes,
    USD FX; updated after every FOMC meeting. FREE.
12. quantifiableedges.com/?s=VIX (Rob Hanna):
    - /vix-spike-often-followed-by-quick-market-bounce/ (2018-06-26): VIX >=30% above 10-day MA -> near-term bounce.
    - /the-vix-spx-action-is-suggesting-a-brief-pullback/ (2019-07-16): SPX up + VIX up together -> brief pullback.
    - /highly-unusual-behavior-between-spx-and-vix/ (2018-01-18): both at 40-day highs, rare.
13. cdn.cboe.com/api/global/us_indices/daily_prices/COR3M_History.csv — real CSV, DATE/OHLC, starts 2006-01-03
    (fetch view truncated at 2013; file continues). Same pattern works for VXN_History.csv (starts 2009 in
    truncated view; canonical file is 2001+). cboe.com/us/indices/dashboard/cor3m/ exists (thin JS shell).
14. tradingview.com/chart/NQ1!/76ZVKa1c-ES-vs-NQ-Divergence-What-It-Really-Means/ — NinjaTrader official
    channel video idea, ~2026-08-24 ("4 days ago" on 2026-08-28): divergence drivers = "sector rotation,
    rate sensitivity, and NQ's mega-cap concentration"; framed as market-health/risk-appetite gauge.
15. tradingview.com/symbols/CME_MINI-RTY1!/ideas/ listing: evolutionqc "Russell 2000: The Market's Risk
    Thermometer" (chart/RTY1!/FDeA0Sfw), RTY as "one of the clearest gauges of genuine risk appetite";
    EdgeClear RTY-breakout divergence idea; mintdotfinance small-cap-surge idea (2026).
16. arXiv 2501.07135 Li & Ferreira "Follow the Leader: Enhancing Systematic Trend-Following Using Network
    Momentum" — lead-lag network momentum spillover improves futures trend strategies.

## Coverage vs brief
- NQ/ES ratio regime: lead 13 (NinjaTrader/TradingView) + falsifier on owned ES daily + NQ 1-min.
- RTY/NQ breadth: lead 14 (evolutionqc) — anecdote-grade, flagged.
- Semis lead NQ: HTV 2007 + Tse 2015 (academic, with decay caution).
- 2s10s/rates shock -> NQ duration: GSS 2005 + USMPD (free intraday event windows). NQ-vs-ES differential
  response is the duration-concentration test.
- DXY risk state: BIS WP592.
- BTC weekend -> Monday: Mourey et al 2025 FRL — exactly on target, peer-reviewed, Dec-2025 issue.
- VIX/VXN intraday: Ferreira-Medeiros (intraday VIX as predictor) + QE spike/divergence rules; VXN daily
  OHLC free from Cboe CDN -> HIGH-based spike measures capture intraday extremes without buying intraday data.
- Mega-cap divergence: Cboe COR1M/COR3M implied-correlation regime (free 2006+); NBER w20071 ETF-layer vol.
- QQQ premium/discount + cash-futures basis: Marshall 2013 JBF, Hasbrouck 2003, Budish 2015 (the "dead at
  1-min" ceiling-setter — cross-market info survives as state, not tick prediction).

## Notes on falsifier design (owned data: NQ 1-min 2006-2026, multi-market daily, VIX/VXN daily certified,
2025-26 limited tick/BBO)
- Everything phrased as regime/veto/router gates on NQ 1-min strategy families with matched unconditional
  controls in the same wave (CLAUDE.md §4), circular-shift nulls, shared draws within family.
- BTC daily includes Sat/Sun rows -> weekend return computable from daily data if BTC-USD is in the
  multi-market daily store; else it is a $0 acquisition (note: governance — do not touch >=2026-08-01 virgin window).
- USMPD/COR3M/VXN CSVs are $0 acquisitions; check LOCKED_FORWARD seals before any conditional test crosses
  the burn boundary.
