# G2W1 A8-SCALPING — Full Notes (Modern NQ Scalping + Order-Flow Scout)

Date accessed: 2026-08-28. Agent: A8-SCALPING, GENESIS II WORLD DISCOVERY WAVE 1.

## Method note (constraint hit)
WebSearch budget was already exhausted (200/200) before this subagent's first call. All discovery
was done via WebFetch on site-native surfaces: sitemap XML files (atas.net, jigsawtrading.com,
bookmap.com/blog.bookmap.com, tradingriot.com), blog index pages (axiafutures.com/blog,
optimusfutures.com/blog, topstep.com/blog), the arXiv export API
(export.arxiv.org/api/query), and the GitHub search API (api.github.com/search/repositories).
Blocked/failed surfaces: futures.io (403 on / and /sitemap.xml), nexusfi.com (403),
old.reddit.com (fetch refused by tool), quantifiedstrategies.com (bot-verification wall),
tradingriot.com blog (site pivoted to macro/systematic content; order-flow guides no longer in
sitemap). YouTube not probed (JS-heavy, low yield without search).

Consequence: no funded-trader content with *individually verified* stats could be reached
(futures.io/nexusfi journals were the main candidates). Closest reachable item is Topstep's
self-reported aggregate payout stats (lead A8-14, framed as a base-rate anchor, not an edge).
"Microcomposite levels" (FT71/Convergent Trading vocabulary) had no reachable primary source
this wave — flagged as a gap, not covered by a lead.

## Our data reality (for the falsifier lines)
- NQ 1-min 2006-2026; multi-market daily; VIX/VXN certified.
- Limited 2025-26 tick/BBO store (incl. MNQ tick 187 dates / 128 pre-burn). Trades + BBO =>
  aggressor-signed trades (bid/ask test), volume-at-price footprints, per-bar delta, CVD,
  best-quote OFI. NO depth beyond BBO, NO MBO. DOM/L2 collection is PAUSED (owner risk-control
  2026-08-12) — any depth-dependent lead is blocked until owner re-authorization; Databento
  GLBX.MDP3 MBO is owner-gated.
- Cost bar: NQ ~3.8 ticks/RT (research convention: $4.36/ctrRT commission + modelled spread).
- Governance: ≥2026-08-01 VIRGIN; 2026-05-31→07-31 BURNED. Falsifiers here target the pre-burn
  slice of the 2025-26 tick store under normal prereg discipline.

## Sources visited (chronological)
1. atas.net sitemap_index.xml -> blog-sitemap.xml, blog-sitemap2.xml (translations mostly)
2. atas.net/blog/imbalance-why-the-size-matters/ — Andrey Rinas, 2018-02-22. Stacked imbalances
   = consecutive imbalances across price levels; institutional activity; S/R zones; aligned =
   continuation, contra price = trapped traders. No stats. Quote: "Institutional traders care
   little about what happens under the huge wheels of their big trades."
3. atas.net/blog/cumulative-delta-indicator/ — ATAS Team, 2021-05-06. CVD direction change +
   big cluster prints -> reversal; trapped-trader exit mechanism. No stats. Quote: "If the price
   moved against big prints, then, perhaps, the seller or buyer got into a trap."
4. atas.net/blog/delta-indicator-patterns/ — ATAS Team, 2021-04-13. Two patterns: delta
   "engulfing" (big delta, no price progress = absorption at S/R -> reversal) and trend
   confirmation (delta+price+OI aligned). Effort-vs-reward frame. No stats.
5. atas.net/blog/cluster-search-indicator/ — Danil Solovyov, 2021-03-09. Cluster Search flags
   price levels where volume/delta exceeds threshold across joined levels; claimed S/R and
   absorption-at-end-of-move reversals. 6E example. No stats. Quote: "There were much more market
   buys than market sells but limit sell orders prevented the price from sharp increase."
6. jigsawtrading.com sitemaps -> post-sitemap3.xml, page-sitemap.xml.
7. jigsawtrading.com/blog/spotting-absorption-reduced-liquidity-market/ — admin, 2014-10-31.
   Thin/promotional; absorption via videos only. Used only as context, not a lead.
8. jigsawtrading.com/blog/choppy-market-trade-using-high-volume-nodes/ — admin, 2016-06-08.
   HVN play in choppy summer market; video only, no rules. Weak lead (LVN/HVN coverage).
9. jigsawtrading.com/free-order-flow-analysis-lessons/ — Peter Davies, course from 2011.
   11 lessons: tape reader setup, summary/reconstructed tape, depth & sales, practical CVD,
   order flow setup, icebergs. Core principle: "A change in order flow comes BEFORE a change
   in price."
10. blog.bookmap.com/post-sitemap.xml (bookmap.com/post-sitemap.xml 301s there).
11. bookmap.com/blog/detecting-stop-runs-using-cvd-and-iceberg-absorption-for-strategic-trading/
    — Bookmap, 2024-09-13. Iceberg absorption at level + CVD divergence -> stop-run spike then
    reversal; rules: repeated executions w/o visible orders, price holds despite volume, CVD
    divergence, enter after break of absorption level. Stocks examples. No stats.
12. bookmap.com/blog/key-order-flow-strategies-breakouts-trends-trapped-traders-and-stop-runs/
    — Bookmap, 2025-02-05. Breakout valid = aggressive market orders + sustained passive
    liquidity + follow-through; stop runs = surge through stop level then immediate reversal.
    Quote: "Large passive orders holding against aggressive order flow indicate a potential
    reversal." No stats.
13. bookmap.com/blog/stop-hunt-or-just-noise-how-to-read-the-real-intent-behind-a-move/ —
    Bookmap, 2025-07-08. Sweep-and-reclaim discrimination: stop hunt = spike + rapid reversal,
    no follow-through, no new bids/offers, absorption clustering; genuine breakout = sustained
    aggression + liquidity stacking. ES + stocks. Advice: wait for confirmation, fade fakeouts.
    Quote: "Real moves are backed by two things: aggressive market orders and passive liquidity."
    No quantified rules.
14. axiafutures.com/blog/ index.
15. axiafutures.com/blog/volume-delta-reversal-trade-strategy/ — Axia Futures, 2022-07-10.
    False-break reversal: price breaks range low while CVD rises; higher lows/wedge confirm;
    DAX + 6E examples, 1-min. Quote: "Volume delta never works in isolation, it is about what
    happens next, how the price reacts." Two example trades, no stats.
16. axiafutures.com/blog/how-to-trade-iceberg-using-a-price-ladder/ — Axia Futures, 2022-09-09.
    Iceberg = large absorption at a ladder level; enter on break of the level; post-break
    checklist: pace change, LVN left behind, JUMP price action, no renewed selling, sticky bid.
    CL 73.00 and ES 3800.00 examples. No stats.
17. sierrachart.com/index.php?page=doc/NumbersBars.html — vendor doc. Bid Trades / Ask Trades
    definitions (exchange designation preferred, else at-or-below bid / at-or-above ask, tick
    rule fallback); Diagonal Dominant Side = bid vol at P vs ask vol at P+1 (and mirror);
    diagonal difference columns; POC and highlight settings.
18. arxiv.org/abs/1011.6402 — Cont, Kukanov, Stoikov, "The Price Impact of Order Book Events."
    NYSE TAQ, 50 stocks. Short-horizon price change ~ linear in best-quote order flow imbalance
    (OFI), slope inversely proportional to depth; explains sqrt volume-impact as derived effect.
    Peer-reviewed (J. Financial Econometrics 2014).
19. export.arxiv.org API "iceberg orders" -> arxiv.org/abs/1909.09495 — Zotikov & Antonov,
    2019-09-20, "CME Iceberg Order Detection and Prediction": detect native (exchange-managed)
    and synthetic icebergs on CME futures from MBO discrepancies; survival analysis predicts
    remaining size.
20. api.github.com/search/repositories?q=orderflow+footprint — top repos:
    murtazayusuf/OrderflowChart (249*, plotly footprints), tiagosiebler/orderflow (81*, crypto
    footprint service), srlcarlg/srl-python-indicators (50*, order flow ticks / volume+TPO
    profile in python), dawolowo/Orderflow-Backtest (reshape T&S into footprint for bots),
    mahmoud20138/OrderFlow-Analysis-Pro (43*).
21. optimusfutures.com/blog/how-to-read-a-footprint-chart-futurestrading/ — 2026-08-18. DeepCharts
    footprint mechanics; NO numeric imbalance thresholds; delta/POC/absorption vocabulary.
22. optimusfutures.com/blog/backtest-order-flow-in-deepcharts-futurestrading/ — 2026-08-18.
    Tick-by-tick replay rebuilds footprints ("Deep Replay"); practice/execution focus, ES.
23. topstep.com/blog/is-topstep-legit — 2026-08-14. Self-reported: "$1.4B+" all-time payouts;
    "33.3% of all individual participants at the Funded Level received a payout" in 2025. NOT
    independently audited.
24. ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/order_flow_cumulative_delta.htm —
    NT8 vendor doc: delta modes Bid/Ask (at-or-below bid vs at-or-above ask; inside-spread ->
    previous tick's category) vs UpDownTick; session/bar reset; requires historical bid/ask
    stamped tick data; volume-bar fragmentation caveat.

## Cross-cutting assessment
- The entire retail order-flow scalping corpus (ATAS, Bookmap, Jigsaw, Axia, Optimus) states
  ZERO quantified evidence. Every claim is example-based. The value is a small set of coherent,
  repeatedly-restated mechanisms, most of which ARE computable from our signed-tick proxy:
  (a) CVD/delta divergence at false breaks; (b) absorption = high volume at price w/o progress;
  (c) stacked diagonal imbalances as S/R; (d) sweep-and-reclaim classified by follow-through.
- The only peer-reviewed, high-prior item is best-quote OFI (Cont et al.) — and it is the one
  thing our BBO store supports natively. Predictive (lagged) OFI net of 3.8 ticks RT is the
  honest tradability test; the contemporaneous linear relation is expected to replicate and is
  NOT an edge by itself.
- Iceberg/depth-dependent leads (Bookmap 2024, Zotikov-Antonov, Jigsaw DOM lessons) are blocked
  by the DOM pause + missing MBO; do not soft-proxy them into pass/fail claims.
- Independence caution: ATAS/Bookmap/Axia/Optimus all restate one common footprint folklore
  (MarketDelta-era, ~2005-2010). Treat as ONE correlated family for null design, not 6
  independent confirmations.
