# G2W1 A3-SOCIAL — working notes
Date: 2026-08-28. Agent: A3 X/Twitter/Social scout.

## Method log / constraint notes
- WebSearch budget was ALREADY EXHAUSTED (200/200) at session start -> fell back to WebFetch on
  search-engine and site-native URLs, as instructed.
- DuckDuckGo html endpoint: CAPTCHA-walled ("select all squares containing a duck").
- Bing no-JS fallback: returns generic/irrelevant results for quoted queries; unusable for niche queries.
- Mojeek: 403. Ecosia: 403. Marginalia: redirects to marginalia-search.com (not yet retried).
- Brave search: WORKS well but rate-limits at >2 parallel calls (429). Throttled to 1-2 calls, spaced.
- X itself: login-walled. xcancel.com: dead (cease-and-desist notice). nitter not tried after xcancel death signal.
- threadreaderapp.com/search: JS-only, no results server-side.
- reddit.com AND old.reddit.com: WebFetch hard-blocked ("unable to fetch"). Reddit-source claims are cited
  from Brave search snippets of the crawled pages; marked as such in leads. URLs are real (crawled by Brave).
- adammancini.substack.com: renders as generic Substack shell (JS), no content server-side.
- quantifiedstrategies.com: bot-verification wall.
- SSRN: 403.

## Confirmed fetches (full page read)
1. libertystreeteconomics.newyorkfed.org/2021/05/the-overnight-drift-in-us-equity-returns/
   - Boyarchenko, Larsen, Whelan; May 26 2021. S&P futures overnight; largest gains 2-3am ET (European open),
     ~3.6% annualized for that hour; full overnight session (4:15pm-9:30am) 2.6% ann. of 4.3% close-to-close;
     sample 1998-2019; mechanism = market-maker inventory risk compensation after end-of-day imbalances.
2. libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/
   - Same authors; Jul 1 2026. Drift prominent 1998-2020, FLAT 2021-2025. 2-3am window flat.
     Attributed to compression in end-of-day imbalance dispersion (std of closing imbalances 6.5% -> 2.9%);
     "limit orders posted at the close have become smaller".
3. spotgamma.com/gex-levels-spy-qqq-futures/ (Aug 17 2026)
   - GEX levels from SPX/SPY & NDX/QQQ options transfer to ES/NQ; positive gamma -> mean reversion,
     negative gamma -> extension ("a 20-point ES move that mean-reverts in positive gamma extends to 60
     in negative gamma"); pinning where SPX+SPY walls align; needs strike-level OI, expirations, basis.
4. smbtraining.com blog search "opening drive" — 8 posts 2011-2016, equities-focused opening drive play
   (direction from "intraday fundamentals", consolidation-above-VWAP variant). Era 2011-2016.
5. Brave SERP: ICT silver bullet — innercircletrader.net/tutorials/ict-silver-bullet-strategy/;
   backtrex.com/en/blog/ict-silver-bullet-strategy-trading-guide; reddit 16p0a7z (1-week ES backtest
   66.67% WR, +76.25 pts, 5-min FVG entries in 10-11am window); reddit 1obzw74 (36% WR larger backtest);
   howtotrade.com/trading-strategies/ict-silver-bullet/ ("Some months were exceptional... some were abysmal").
6. Brave SERP: Mancini failed breakdown — reddit 1izqyv2 ("3 conditions for FBD", critical thread
   "how Adam Mancini went..."); youtube joMvAGVLcJo (Dalton Grados May 2025); esgameplan.substack.com
   (4 yrs, daily ES plans, "Failed Breakdown execution scenarios" per snippet); whop.com/pro-education-access/
   ("built around ... the Adam Mancini-style Failed Breakdown in ES futures"); scribd 885947011 (FBDs + "acceptance").
7. Brave SERP: ORB on NQ reddit backtests —
   - 1rrn609 r/Daytrading: MNQ ORB 2019-2026, proper rollover, Sharpe ~1.4 IS, ~1.10 OOS (2023-26),
     "does not beat buy & hold in absolute return".
   - 1qcyt3h r/InnerCircleTraders: NQ ORB 2016-2025 stop-placement study: 25%-of-range stops +1971R vs
     wide stops -698R, ~30% WR.
   - 1j9pxsr r/algotrading: S&P500 CFD 15-min ORB, 5yr, "most of the profits came from the first couple of hours".
   - 1saburp r/algotrading: MNQ 4 strategies 2021-2026; ORB 40.7% WR, PF 1.18, 943 trades.
   - 1spd5nf r/algotrading: 17 strategies dead on MNQ/NQ; "the raw ORB edge on NQ looks extremely thin" after costs.
   - 1qqh9mp r/Daytrading: one respondent: >50% WR, PF 4.89 over 6 years (ORB/PMRB), "many nuances".
8. esgameplan.substack.com homepage: "in-depth knowledge & Analysis to trade successfully $ES Futures", 4 years old.
9. Brave SERP items for silver bullet also surfaced nqbacktest.online (10+ yr 1-min NQ replay tool) — vendor.

## Independence map (who copied whom)
- ICT (Michael Huddleston) is the ROOT for: silver bullet 10-11am window, Judas swing / overnight
  liquidity sweep language, killzones, FVG. All reddit/YouTube/blog "backtests" are derivative tests of
  the same guru claim — NOT independent discoveries. Independent evidence = only the numeric backtests.
- Mancini's "failed breakdown" is HIS branding (via his X @AdamMancini4 + newsletter); esgameplan/whop/
  YouTube channels are derivative. But the underlying object (sweep of a prior low then reclaim) is the
  SAME object as ICT's "turtle soup" (which itself is branded from Connors/Raschke Street Smarts 1995
  "Turtle Soup" — pre-social era). So: Raschke/Connors 1995 -> ICT turtle soup -> Mancini FBD is a
  three-generation lineage of ONE underlying pattern: stop-run reversal at prior session extremes.
- Overnight drift: NY Fed academic, amplified on fintwit (NightShares ETFs launched off it); 2026 update
  kills it 2021-25. Distinct object from sweep patterns.
- SpotGamma/Menthor Q/Tier1Alpha: vendor cluster, common root = dealer-hedging theory (Cem Karsan
  @jam_croissant popularized vanna/charm on X).
- ORB: root = Toby Crabel (1990 book), re-popularized 2023-24 by Zarattini & Aziz QQQ paper on fintwit,
  retested by many redditors independently (numeric results genuinely independent of each other).

## Additional confirmed fetches (round 2)
10. backtrex.com/en/blog/ict-silver-bullet-strategy-trading-guide (Jul 4 2026) — Silver Bullet rules:
    killzones 3-4am / 10-11am (most reliable) / 2-3pm NY; FVG entry aligned w/ H4-daily bias + MSS/BOS;
    stop beyond FVG; target >=5 handles then liquidity; NQ/ES named. "The three Silver Bullet entry
    conditions applied in strict sequence".
11. concretumgroup.com/papers/ — full paper list w/ SSRN ids: ORB QQQ 4416622; ORB stocks-in-play 4729284;
    intraday momentum SPY 4824172; VWAP day-trading 4631351.
12. concretumgroup.com/can-day-trading-really-be-profitable/ — Zarattini/Aziz, QQQ/TQQQ 2016-2023,
    "1,484% between 2016 and 2023" vs 169% passive, 33% ann. alpha net of commissions. Leverage via TQQQ.
13. concretumgroup.com/beat-the-market-...-spy/ — Zarattini/Aziz/Barbon 2024: SPY 2007-early2024 intraday
    momentum, 1,985% net, 19.6% ann., Sharpe 1.33, "abnormal demand and supply imbalances", trailing stops.
14. alphatrends.net ?s=anchored+vwap — Shannon AVWAP posts: when-where-why-to-set-anchored-vwap;
    podcast posts Jun 2026; "gives context to price by showing the average price paid since a specific event".
15. investiquant.com (masterthegap.com 301-redirects here) — Scott Andrews + David Skowron; gap-stat detail
    no longer public; "39% 2022 Bear Mkt Avg Return (Net)" marketing claim.
16. traderfeed.blogspot.com search TICK+trend day — 16 posts 2007-2020 w/ URLs; key: 2008/02 "NYSE TICK:
    Using Sentiment to Trade Trend Days"; 2009/01 "Six Ways to Identify a Trend Day"; 2008/02 ORB using
    TICK + first 15 min of ES; 2008/12 cumulative adjusted TICK construction (zero-mean vs 20-day MA).
17. squeezemetrics.com/monitor/dix — "When GEX is high, the option market is implying that volatility will
    be low..." (vol-level claim, not directional).
18. spotgamma.com/?s=charm — vanna-charm post list incl. spotgamma.com/vanna-and-charm-explained/
    (Apr 28 2026) and options-vanna-charm (Nov 5 2020).
19. spotgamma.com/vanna-and-charm-explained/ — claims: vanna rallies as IV declines; EOD strike pinning
    ("Charm Pressure is often the force that leads to the End of Day Pin"); 0DTE effects intensify final
    two hours. NO empirical evidence given.
20. innercircletrader.net/tutorials/ — tutorial list incl. ict-market-on-close-macro (MOC macro).
21. innercircletrader.net/tutorials/ict-market-on-close-macro/ (upd Aug 6 2026) — 3:50-4:00pm ET window,
    "the algorithm frequently delivers one last repricing into liquidity before the cash market closes";
    targets HOD/LOD; bias from post-1:30pm structure; stops beyond post-3:50 swing; index futures "respect
    the close most cleanly"; macros generically = last-10/first-10 min of each hour.
22. innercircletrader.net/tutorials/practical-ict-strategies-7th-edition/ (Aug 15 2026) — names Judas
    Swing + Power of 3 but rules PAYWALLED (promo page only).
23. howtotrade.com/trading-strategies/ — has ict-silver-bullet + opening-range-breakout guides; NO judas
    swing page (guess-verify of /ict-judas-swing/ returned 404).
24. lindaraschke.net/articles/ — 11 free article PDFs (Trade Trends, Omega, Active Trader etc.);
    trend-day/turtle-soup items not individually listed on this page.
25. smbtraining.com — 8 opening-drive posts 2011-2016 (equities; direction from intraday fundamentals).

## Dead ends / blocks (round 2)
- Brave: hard rate-limit after first 3 queries; repeated 429 for rest of session.
- searx.be: browser-verification wall. lite.duckduckgo.com: same duck CAPTCHA. menthorq.com/blog/: 404.
- Bing no-JS fallback degraded to irrelevant/spam results for niche quoted queries — abandoned.
- SSRN direct: 403 (used concretum article pages instead).
- Reddit (www + old): WebFetch hard-blocked; all reddit claims carried via Brave SERP snippets (URLs real,
  crawled; marked "via Brave snippet" in leads).

## Final lead set: a3-01..a3-15 (see final report text delivered to orchestrator; same blocks).
