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

## Round 3 confirmed fetches (2026-08-28, later pass)
26. nqstats.com — anonymous free "solo research project", NQ-only, 2016-2025, ~2,470-2,570 sessions/module.
    Seven modules fetched individually:
    - ib_breaks.html: IB = 09:30-10:30 ET; breach = wick >= 1 tick. By 12:00: IBH 47.0%, IBL 39.8%,
      either 82.5%. By 16:00: IBH 62.9%, IBL 54.9%, either 96.1% (n=2,571). Conditional: IB closes
      above mid AND low set first -> high break 74.0% by noon / 84.0% by close (n=1,114); mirror
      67.9%/78.0% (n=974).
    - noon_curve.html: TBR 08:00-16:00; AM(8-12)/PM(12-16). Opposite-side sessions (one extreme AM,
      other PM) 72.81% (1,805/2,479); both-AM 21.82%; both-PM 5.37%. Q2(10-12) breaks Q1(8-10) high ->
      "AM low / PM high" in 82.12% of opposite-side sessions (794); Q1 low break -> mirror 72.42% (631).
    - aln_sessions.html: Asia 20:00-02:00, London 02:00-08:00, NY 08:00-16:00. Four engulf patterns;
      NY breaks London high 68.6-81.1% / low 65.5-75.0% depending on pattern (n=2,542).
    - am_tbr.html: 08:00 open + / - 0.25 SDEV bands (rolling 20-day sample stdev of the AM TBR); touch ->
      reversion to 08:00 open: +band 74.0%, -band 74.6%; touches inside 8am hour: 78.4%/79.6%.
      MAE ~0.55 sigma mean; MFE ~0.8-0.9 sigma continuation past open (n=2,572, 27 no-touch).
    - hour_stats.html: prior-hour range breach (>=1 tick) during NY hours -> reversion 61.5% overall,
      17,701 breach events; per-hour tables JS-only (not extracted).
    - rth_breaks.html: at 09:30 open vs prior-day RTH range: gap up 26.3%, gap down 14.6%, inside 59.1%
      (n=2,488). Gap-up days: close above pRTH high 69.9%, opposite side untouched 88.1%. Gap-down:
      close below pRTH low 59.5%, opposite untouched 90.4%. Inside opens: exactly one side broken 74.0%,
      neither 17.7%, both 8.3%.
    - 1h_continuation.html: table PLACEHOLDER (dashes) — unusable, excluded from leads.
27. threadreaderapp.com/user/AdamMancini4 — two unrolled threads with real status URLs:
    2021-01-18 twitter.com/AdamMancini4/status/1350512433614495744 ("Above 3770 needed to trigger
    upside to 3800, breakout lvl 3900" level-to-level method); 2022-01-18 .../status/1483429081744277504.
28. threadreaderapp.com/user/jam_croissant — threads 2021-08-23 (windows of weakness, Jackson Hole),
    2021-09-27 (JHEQX EOQ flows; "100k+ es 10/20 margin puts sold"), 2021-12-29 (quarterly delta-neutral
    ITM-call collar mechanics), 2022-03-09 (fixed-strike vol pain trade). Threadreader's per-thread URL
    extraction unreliable (same status id shown for 3 threads) -> cite user page + dates.
29. threadreaderapp.com/user/FuturesTrader71 — philosophy/auction threads only; no concrete VWAP
    first-touch rules -> FT71 dropped as a lead (no citable rule).
30. github.com/yuvrajsingh1097/ICT-Silver-Bullet-Strategy-Backtester (created 2026-03-26) — sweep->FVG->
    entry 3-state machine, one 60-min window, 5-min bars, 2:1 RR, ~2h timeout. api.github.com search:
    ICT ecosystem repos STAR-EA-v11.20 (29 stars, Judas Swing/Silver Bullet/AMD/CRT), sb-watchbot (NQ),
    10AM-Silver-Bullet, BAKOME MQL5 EAs — all 2026-era derivatives of one guru source.
31. quantifiableedges.com/blog/ (Rob Hanna) — 2026-06-07 "A TICK TomOscillator Study Suggesting a Monday
    Bounce": TomOscillator %Rank < 1% -> "23 of 25 instances closing up the next day". Uses NYSE $TICK
    (repo owns $TICK back to ~2013).
32. traderfeed.blogspot.com/search?q=VWAP (Steenbarger, 2008-2018 posts): prior-day pivot touched "about
    75% of the time"; R1/S1 ~70%, R2/S2 ~50%, R3/S3 ~33%; "85% of all trading days are not inside days";
    adjusted TICK +/-500 trending vs +/-200 range thresholds.
33. spotgamma.com/how-to-trade-gex-levels/ — call wall/put wall/zero gamma; positive gamma "moves get
    dampened, ranges compress"; negative gamma "moves extend and accelerate"; explicit: NO quantified
    stats in article. Blog index also fetched (Aug 2026 posts, incl. GEX Levels for SPY QQQ ES NQ Aug 17).
34. lindaraschke.net/wp-content/uploads/2026/01/august1997.pdf (AIQ Opening Bell, Aug 1997, PDF read in
    full): Holy Grail rules (ADX14 > 30 rising; pullback to 20-EMA; buy stop above prior bar high; stop at
    new swing low; claimed top-in-place odds "only 5% to 10%"). Three-Day Unfilled Gap Reversal rules
    (unfilled gap down; buy stop 1 tick above gap-day high for 3 sessions; stop at gap-day low).
35. Nitter status re-checked this round: nitter.net dead — X Corp cease-and-desist 2026-08-24; xcancel.com
    dead same C&D. No live tweet mirrors exist as of 2026-08-28. Threadreader user pages are the only
    working X archive surface found.

## Round 3 independence additions
- nqstats: ONE anonymous author for all six stat modules — six leads, one source; concepts descend from
  Market Profile (Steidlmayer IB) but numbers independently computed.
- Raschke/Connors 1995-97 is the pre-social root of the stop-run-reversal family later rebranded by ICT
  (turtle soup) and Mancini (failed breakdown).
- Karsan and SpotGamma: same dealer-hedging school, not independent of each other; both amplified on X.
- NY Fed, Hanna, Steenbarger, nqstats, reddit ORB posters: mutually independent lineages.

## Final lead set: a3-01..a3-17 delivered to orchestrator (blocks in final message).
