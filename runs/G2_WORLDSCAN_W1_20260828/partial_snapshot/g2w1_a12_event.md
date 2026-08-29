# G2W1 A12-EVENT — full scout notes (2026-08-28)

## Method / constraints log
- WebSearch refused (session budget 200/200 exhausted) on first call. Fell back to WebFetch on
  site-native endpoints, as authorized by the task constraints:
  - api.crossref.org (bibliographic search + DOI lookups) — primary academic verification
  - api.openalex.org (DOI lookups w/ abstract reconstruction)
  - export.arxiv.org API (native search)
  - Direct page fetches: nber.org, libertystreeteconomics.newyorkfed.org, nyse.com/auctions,
    elmwealth.com, quantifiableedges.com (native ?s= search + posts), buildalpha.com
- Blocked/failed hosts (attempted, recorded): api.semanticscholar.org (429 x3),
  www.newyorkfed.org sr917 (403), papers.ssrn.com (403), quantifiedstrategies.com (bot wall),
  html.duckduckgo.com (CAPTCHA x3), ideas.repec.org / econpapers search forms (form-only pages),
  nasdaqtrader.com ClosingCrossFAQs (404 redirect), bing.com (generic results only).
- DOI-only sources: metadata (title/authors/venue/year/DOI) verified via api.crossref.org or
  api.openalex.org fetches on 2026-08-28; full texts not fetched (paywalled). Marked in leads.

## Verified source registry
1. NBER w24748 Monetary Momentum (Neuhierl & Weber, June 2018). Fetched nber.org page directly.
   Quote captured: "Stock returns start drifting up 25 days before expansionary monetary policy
   surprises, whereas they decrease before contractionary surprises." Drift continues
   post-announcement; cumulative return differences >4.5% within 15 days after meetings.
   Crossref: never journal-published (only 10.3386/w24748, ssrn 3043071/3030126).
2. Marchal, "Risk & returns around FOMC press conferences: a novel perspective from computer
   vision", arXiv 2012.06573 (2020-12-11, v2 2021-01-15). Via arXiv API. Quote: "complex
   discussions are associated with higher equity returns and a drop in realized volatility".
   (Same author's SSRN 3747172 blocked 403.)
3. Lucca & Moench, "The Pre-FOMC Announcement Drift", J. Finance 2015, DOI 10.1111/jofi.12196
   (Crossref-verified; also SSRN 1923197/2024459 lineage).
4. Cieslak, Morse, Vissing-Jorgensen, "Stock Returns over the FOMC Cycle", J. Finance 74(5) 2019,
   DOI 10.1111/jofi.12818. OpenAlex-verified w/ claim: "the equity premium is earned entirely in
   weeks 0, 2, 4, and 6" in FOMC-cycle time; attributed to informal Fed communication.
5. Kurov, Sancetta, Strasser, Wolfe, "Price Drift Before U.S. Macroeconomic News: Private
   Information about Public Announcements?", JFQA 2018, DOI 10.1017/s0022109018000625
   (Crossref-verified; 2015/2016 SSRN lineage 2637528/2778549).
6. Ederington & Lee, "How Markets Process Information: News Releases and Volatility",
   J. Finance 1993, DOI 10.1111/j.1540-6261.1993.tb04750.x (Crossref-verified).
7. Lou, Yan, Zhang, "Anticipated and Repeated Shocks in Liquid Markets", RFS 2013,
   DOI 10.1093/rfs/hht034. Abstract quote via Crossref: "Treasury security prices in the secondary
   market decrease significantly in the few days leading up to Treasury auctions and recover
   shortly thereafter, even though the time and amount of each auction are announced in advance."
8. Boyarchenko, Larsen, Whelan, "The Overnight Drift", RFS 2023, DOI 10.1093/rfs/hhad020
   (Crossref-verified; SSRN 3546173 2020 lineage; NY Fed sr917 page itself 403).
9. Boyarchenko, Larsen, Whelan, "The Disappearing Overnight Drift", Liberty Street Economics,
   2026-07-01, DOI 10.59576/lse.20260701 →
   https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/
   Fetched directly. Original drift 2:00–3:00am ET (European open), 1998–2020, ~3.7%/yr;
   Jan 2021–Dec 2025 "the 2:00–3:00 window...is flat"; quote: "the overnight drift...has averaged
   close to zero since 2021".
10. Haghani, Ragulin, Dewey, "Night Moves: Is the Overnight Drift the Grandmother of All Market
    Anomalies?", Elm Wealth, 2022-06-20, https://elmwealth.com/night-moves/ (fetched directly;
    SSRN 4139328 lineage via Crossref). Claims: virtually all equity returns accrue market-closed
    hours; L/S overnight-pattern portfolio ~38%/yr gross 1995–2022; pronounced in retail
    "attention stocks"; mechanism = retail at-open orders + deeper closing liquidity.
11. Gao, Han, Li, Zhou, "Market intraday momentum", JFE 2018, DOI 10.1016/j.jfineco.2018.05.009
    (Crossref-verified; SSRN 2440866 2014 lineage). First half-hour (incl. overnight) predicts
    last half-hour.
12. Heston, Korajczyk, Sadka, "Intraday Patterns in the Cross-Section of Stock Returns",
    J. Finance 2010, DOI 10.1111/j.1540-6261.2010.01573.x (Crossref-verified).
13. Bogousslavsky & Muravyev, "Who trades at the close? Implications for price discovery and
    liquidity", J. Financial Markets 66 (2023), DOI 10.1016/j.finmar.2023.100852
    (Crossref+OpenAlex-verified; abstract not exposed; earlier title "Should We Use Closing
    Prices? Institutional Price Pressure at the Close", SSRN 3485840).
14. NYSE Auctions page, https://www.nyse.com/auctions (fetched directly): NYSE closing-auction
    imbalance publication begins 3:50 p.m., "every 1 second until auction is complete";
    NYSE Arca / Texas begin 3:00 p.m.
15. Franz, "The Index Effect Minute by Minute: Intraday Returns at NASDAQ-100 and MSCI U.S.
    Rebalancings", SSRN 2019, DOI 10.2139/ssrn.3459744 (Crossref-verified metadata only;
    SSRN page 403; abstract NOT verified — title/metadata lead only).
16. Stoll & Whaley, "Program Trading and Expiration-Day Effects", FAJ 1987, DOI
    10.2469/faj.v43.n2.16; and "Expiration-Day Effects: What Has Changed?", FAJ 1991,
    DOI 10.2469/faj.v47.n1.58 (Crossref-verified).
17. Quantifiable Edges (Rob Hanna), "An updated look at Thanksgiving Week Stats", 2025-11-24,
    https://quantifiableedges.com/an-updated-look-at-thanksgiving-week-stats/ (fetched directly).
    Wednesday before Thanksgiving: 76.9% win rate, avg +0.3%; quote "Wednesday has had the most
    consistent gains"; Friday half-day historically bullish but underperformed last 15 years;
    Monday after "given back a good chunk of the gains" (worst −9% in 2008; ~breakeven since).
    Related posts found via native search: a-long-term-look-at-the-wednesday-before-thanksgiving/
    (2023-11-21), fed-day-readings/ (2010-03-16, "Fed Days have had a substantial upside bias").
18. Jiang, Likitapiwat, McInish, "Information Content of Earnings Announcements: Evidence from
    After-Hours Trading", JFQA 2012, DOI 10.1017/s002210901200049x (Crossref-verified). Related:
    Berkman & Truong, "Event Day 0? After-Hours Earnings Announcements", SSRN 2005,
    DOI 10.2139/ssrn.747004.
19. Build Alpha (David Bergstrom), "News Event Trading",
    https://www.buildalpha.com/news-event-trading/ (fetched directly). Example windows "2 PM on
    Fed Days," "8:30 AM on NFP Days," "8:30 AM on CPI Days"; two example strategies w/ equity
    curves (ES GDP, gold NFP, data to 2005); author states they should "not be considered a
    standalone edge". Kept as registry entry, NOT shipped as a lead (claim content too weak).

## Coverage vs domain brief
- post-CPI/FOMC drift-vs-reversal by initial reaction: A12-01 (surprise-sign continuation),
  A12-05 (pre-release drift), A12-06 (response shape/speed). No CPI-specific academic intraday
  paper found through available endpoints (arXiv "CPI announcement" = 0 hits; SSRN blocked).
- Powell presser: A12-02 (presser-window risk/return, communication features). The popular
  "stocks fall during Powell Q&A" press statistic could not be sourced through non-blocked
  endpoints — NOT shipped (refuse-to-invent rule).
- 10:00 data fade: covered as pre/post response-shape (A12-05, A12-06); a specific post-10:00
  fade claim was not found from a fetchable source.
- Treasury auction 13:00: A12-07 (auction-cycle, day-level; intraday 13:00 transmission is the
  falsifier design).
- 15:50 MOC: A12-13 (+NYSE 3:50pm timing anchor).
- Closing ramp/fade + lunch MR: A12-11, A12-12 (periodicity covers both ends).
- 18:00 reopen / overnight: A12-08, A12-09, A12-10 (incl. 2021+ disappearance — era-split
  critical).
- Holiday half-day: A12-16.
- Quarterly expiration: A12-15. Index rebalance: A12-14.
- Mega-cap AH earnings → next-session NQ: A12-17.

## Repo-side falsifier assets assumed
NQ 1-min 2006–2026 (END-stamped, ET, 18:00 session opens), multi-market daily, VIX/VXN
certified, limited 2025–26 tick/BBO. Event calendars (FOMC dates/times, CPI/NFP schedule,
Treasury auction dates, triple-witching dates, Nasdaq-100 reconstitution dates, earnings dates)
are public/free but must be built — flagged per-lead in OBSERVABLES.
