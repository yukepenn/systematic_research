# G2W1 A7-OLDSCHOOL — full working notes (2026-08-28)

## Session constraints hit
- WebSearch budget was already exhausted (200/200) before this agent ran a single search. Fell back to WebFetch on site-native search/browse URLs per instructions.
- Engines: DuckDuckGo html + lite = CAPTCHA; Bing = mislocalized junk (all irrelevant results twice); Mojeek/Ecosia/SoBrief/SSRN/traders.com/grokipedia = 403; Brave worked for 4 queries then hard 429 for the rest of the session; SearXNG instances (tiekoetter, priv.au) = 429; web.archive.org = blocked by Claude Code.
- Everything cited below WAS actually fetched and summarized this session. No invented URLs.

## Topics I could NOT source this session (and why)
- Sheldon Knight (K-Data Time Zones, day-of-week/day-of-month futures seasonals): traders.com author archive 403, all remaining engines throttled. No lead issued.
- Crabel doji/hook patterns specifically: not found in fetchable sources (Wikipedia page on Crabel is career-only).
- Raschke/Connors 80-20s and Holy Grail exact-rule pages: netpicks/tradersmastermind/therobusttrader site searches came up empty; Brave died before dedicated queries. Momentum Pinball indicator definition WAS recovered from LBR's own slide deck.
- Larry Williams accumulation/distribution (WillVal/ProGo): ireallytrade.com homepage only lists product sections; no free rule statement found. Covered Williams via GSV + Smash Day instead.
- LBR august1997.pdf (Short Term Trading Strategies) fetched but is a scanned PageMaker PDF; local pdftoppm unavailable, could not extract text.

## Fetch log (all visited 2026-08-28)
1. en.wikipedia.org/wiki/Toby_Crabel — career only; 1990 book confirmed; no rules.
2. quantifiableedges.com/?s=NR7 — found WR7/NR7 posts.
3. quantifiableedges.com/what-happens-when-range-rapidly-contracts/ (2008-04-15) — NDX since 1986; WR7-down-then-NR7; buy close of NR7 day; 1-day avg ~+0.6% (~10x normal), 3-day ~5x normal; "The inability of the sellers to follow-through after the wide range day down invites buying over the next several days."
4. alvarezquanttrading.com/?s=RSI2 — post list.
5. alvarezquanttrading.com/blog/rsi2-relative-strength-index-analysis/ (2018-06-13) — R3000 2007-2017, 6.9M obs, "RSI2 smile" (mass at both extremes); RSI2<10 count trending down, >90 trending up in bull years.
6. alvarezquanttrading.com/blog/rsi2-strategy-double-returns-with-a-simple-rule-change/ (2018-08-01) — base: R3000, close>100d MA, RSI2<10, limit -5%, max 10 positions, exit RSI2>50 or 10 days; 2007-2018.5; CAR low-10s%; ex-index-members variant: CAR +121%, MDD −54%, Sharpe +172%. "…simply a small conceptual change in a rule that makes the big difference."
7. alvarezquanttrading.com/blog/how-is-mean-reversion-doing-dead-shrinking-or-doing-just-fine/ (2019-03-13) — R3000 2001-2018, RSI2<1 buy / RSI2>70 exit: avg trade 0.52% full period, 0.33% last 2 yrs; bull-vs-bull 0.89% (2003-07) vs 0.52% (2010-18); win rate ~65% stable; edge "slowly shrinking".
8. lindaraschke.net/ + /articles/ — free article PDFs listed (no named-setup articles).
9. taylortradingtechnique.net/Techniqueexplained.html — Taylor 1950 Book Method; BUY/SELL/SELL-SHORT 3-day cycle; measures rally (buy-day low→sell-day high) and decline (SS-day high→buy-day low); claims >90% of cycles "positive" (SS high > prior buy-day low) across markets; "positive 3 Day Rally".
10. futures.stonex.com/blog/the-taylor-trading-technique — buy day: price breaks below prior day low then rebounds (traps late sellers); SS day: mirror above prior high; 2-4 days up / 1-3 down; grain-futures origin; "The key is to think in Taylor concepts rather than to follow it mechanically."
11. slideshare.net/slideshow/linda-bradford-raschke-the-taylor-trading-techniqueppt/262013129 — LBR deck: buy day = test of prior low, morning low/afternoon high, close upper range; SS day mirror; 60/120-min swing monitoring; Momentum Pinball indicator = "3-period RSI of the 1-day ROC" >67 / <33 + 20-EMA position; "The market has a definite 1-2-3 rhythm, with at times an extra 1-2 beats."
12. oxfordstrat.com/trading-strategies/opening-range-breakout/ — Crabel ORB: Noise=min(H−O, O−L); Stretch=SMA10(Noise)×2; buy stop O+Stretch / sell stop O−Stretch, other side = protective stop; exits time (1-40d)/target/stretch; ATR(20)×6 stop; 42 US futures, 1980-2011, $1M, 1% FF sizing; "volatility expansion".
13. oxfordstrat.com/trading-strategies/toby-crabel-narrow-range-1/ — 2-bar NR: narrowest 2-day range vs prior 20 days; then ORB at Open±Stretch; 42 markets 1980-2013; Crabel credits Wyckoff (low-volume narrow range precedes directional move).
14. oxfordstrat.com/trading-strategies/greatest-swing-value/ — Williams GSV: Noise = O−L if close up, H−O if close down; GSV=SMA10×2; buy stop O+GSV / sell stop O−GSV; exits time/GSV/target; 42 futures 32 yrs since 1980.
15. oxfordstrat.com/trading-strategies/smash-day-pattern-c/ — Smash day: Close[i−1]<Low[i−2] (long setup) / mirror short; entry stop 1 tick beyond prior-day extreme; 42 US futures 1980-2011; publisher rating "D" (poor).
16. oxfordstrat.com/?s=williams — index of Williams strategies.
17. cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/ — reviews Zarattini & Aziz (Apr 2023, SSRN 4416622): QQQ/TQQQ 2016-01-01..2023-02-17; direction of first 5-min bar, enter at 2nd bar, stop at first-bar opposite extreme, 10x target, EoD exit, 4x leverage; CXO flags "no bid-ask spread, no impact of trading (slippage)".
18. concretumgroup.com/a-profitable-day-trading-strategy-for-the-u-s-equity-market/ — Zarattini, Barbon, Aziz 2024 (SSRN 4729284): 7,000+ US equities 2016-2023; "Stocks in Play" by relative volume; 5-min OR (also 15/30/60 tested); stop at OR low; EoD exit; top-20 portfolio: +1,600% net, Sharpe 2.81, 36% ann. alpha vs SPX +198%.
19. github.com/giovannibrusco/zarattini-2023-orb-qqq — Python replication: 1,775 vs 1,795 trades, Sharpe 1.06 vs 1.12; break-even ~2.2 c/share slippage ("The edge lives inside the bid-ask spread"); NQ 09:25 cross-market filter t=2.05 vs placebo, but 76% of filtered profits in 2022; loses money 2017/2020/early-2023.
20. tradersmastermind.com/turtle-soup-trading-strategy-rules/ — new 20-day low; previous 20-day low ≥4 sessions earlier; "place a buy stop 5-10 ticks above the low (good for one day only…)"; stop under current-day low; expect quick 1-2 hour move.
21. luxalgo.com/library/concept/turtle-soup/ — attribution Connors/Raschke Street Smarts 1995 (anti-Turtle); entry = stop back inside violated level; stop beyond sweep extreme; abandon on close back beyond level; regime-dependent, "the exact 1995 parameters have been public for decades, and any edge that specific erodes."
22. completetradersedge.com/linda-raschke-turtle-soup-pattern-trader/ — same rules; targets vs 1R or trailed.
23. chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/rsi-2.md — Connors RSI(2): 200-day SMA trend filter; buy RSI2<10 (better <5) above SMA; short RSI2>90 (better >95) below; exit on 5-day SMA cross; Connors: stops hurt; "hundreds of thousands of trades" tested; stocks and stock indices.
24. quantifiedstrategies.substack.com/sitemap.xml — post index.
25. quantifiedstrategies.substack.com/p/rsi-2-strategy-explained-larry-connors — SPY 1993-present: CAGR 9%, avg trade +0.9%, MDD 34%, 28% time invested (rules paywalled).
26. quantifiedstrategies.substack.com/p/nr7-trading-strategy-explained-for — NR7 attribution Crabel 1990; SPY backtest claimed "solid long-term results" (rules paywalled) — weak, not used as a lead source.
27. quantpedia.com/strategies/turn-of-the-month-in-equity-indexes/ — McConnell & Xu (SSRN 917884, FAJ 2008): 1926-2005, "Virtually all of the excess market return is accrued during the four-day turn-of-the-month period"; Quantpedia sim: buy 1 day before month-end, sell close of 3rd trading day of new month; 7.2% ann., vol 6.9%, Sharpe 1.04, MDD −20.8%.
28. quantifiableedges.com/?s=gap — gap-study index.
29. quantifiableedges.com/intraday-performance-after-a-massive-gap-down/ — SPY since 1993, gap down ≥4%: open-to-close upside edge; "It does not appear as though panic selling at the open would be wise."
30. netpicks.com/opening-range-breakout/ — ORB variants (first 30 min, prior close ± range, NR7 conditioning); Crabel stretch spelled out as 10-day average of the smaller of (H−O),(O−L); no stats.
31. investiquant.com — Scott Andrews confirmed co-founder, "Master The Gap" legacy; no public gap-zone stats remain. No lead issued for Andrews gap zones (no fetchable rule/stat page).
32. search.brave.com — 4 successful queries (Taylor sources, Crabel stretch sources, Zarattini mirrors, Turtle Soup sources) then persistent 429.
33. ireallytrade.com — Williams product sections only; "These indicators have stood the test of time, many going back to the 1960s."

## NQ translation thinking (common observables)
We own: NQ 1-min 2006-2026 (RTH+ETH), multi-market daily, VIX/VXN certified daily, limited 2025-26 tick/BBO. All falsifiers below are runnable on that. Session boundary/END-stamp conventions per CLAUDE.md apply to any implementation.

## SECOND-PASS VERIFICATION LOG (same day, fresh session — WebSearch again 200/200 exhausted)
Every source cited in the final leads was re-fetched and confirmed this session before use:
- oxfordstrat.com/trading-strategies/opening-range-breakout/ — CONFIRMED: Noise=min(H−O,O−L), Stretch=SMA10(Noise)×2, buy stop O+Stretch / sell stop O−Stretch; 42 futures, 32 yrs since 1980; site rating D; $50 RT sensitivity charts.
- taylortradingtechnique.net/Techniqueexplained.html — CONFIRMED: BUY/SELL/SELL-SHORT 3-day cycle, rally (buy-day low→sell-day high) and decline (SS-high→buy-day low) measurements; vendor claims "over 90% of the cycles are positive" across markets (positive = SS-day high > prior buy-day low).
- quantifiableedges.com/what-happens-when-range-rapidly-contracts/ — CONFIRMED: Rob Hanna 2008-04-15, NDX since 1986, WR7 down-close then NR7; next-day avg gain >10× a normal day (normal ≈0.06%), 3-day >5× normal.
- github.com/giovannibrusco/zarattini-2023-orb-qqq — CONFIRMED: replication 1,775 vs paper 1,795 trades, Sharpe 1.06 vs 1.12 at zero slippage, collapses to 0.23 with slippage; break-even ≈2.2¢/share; NQ-09:25 confirm filter $0.125/share t=2.05 vs QQQ-only placebo $0.079 t=1.27; 76% of filtered PnL from 2022; loses in 2017/2020/early-2023.
- chartschool.stockcharts.com .../rsi-2.md — CONFIRMED: Connors RSI(2): 200d SMA filter, buy RSI2<10 (<5 aggressive) above SMA, short >90 (>95) below, exit 5-day SMA cross, no stops (testing said stops hurt), stocks + stock indices.
- slideshare.net/slideshow/linda-bradford-raschke-the-taylor-trading-techniqueppt/262013129 — CONFIRMED: LBR deck; Pinball = 3-period RSI of 1-day ROC, >67 / <33 thresholds; buy day = test of prior low then rally; ideal SS day opens up, high first / low last, closes lower range.
- oxfordstrat.com/trading-strategies/greatest-swing-value/ — CONFIRMED: Williams GSV: Noise=O−L if up close, H−O if down close; GSV=SMA10×2; stops at O±GSV; 42 futures 32 yrs; rating D.
- oxfordstrat.com/trading-strategies/smash-day-pattern-c/ — CONFIRMED: long setup Close[i−1] < Low[i−2]; buy stop 1 tick above High[i−1]; 42 futures 1980–2011; rating D.
- mypivots.com/dictionary/definition/206/stretch — CONFIRMED: Stretch = 10-period SMA of smaller of (O−H),(O−L) absolute diffs; used for ORB/ORBP entry+stop.
- en.wikipedia.org/wiki/Toby_Crabel — CONFIRMED: 1990 book; no losing year 1991–2002; $3.2B by 2005; FT "counter-trend" quote.
- quantifiableedges.com/wr7-nr7-is-back/ — CONFIRMED: Hanna 2008-05-22 follow-up post.
- tradingsetupsreview.com/nr7-trading-strategy/ — CONFIRMED: NR7 def + 20EMA-side filter + break-of-extreme entry; Crabel attribution.
- tradingsetupsreview.com/the-holy-grail-trading-setup/ — CONFIRMED: ADX(14)>30 rising + pullback to 20 SMA + entry at touch-bar extreme; Raschke/Connors attribution.
- tradingsetupsreview.com/15-minute-opening-range-scalp-trade/ — CONFIRMED: Kevin Ho (Chartpoint, 2003 examples): 2 ticks beyond first-15-min range, 1-pt target/stop, 1-min time stop, ES.
- newtraderu.com/2020/08/15/turtle-soup-trading-strategy/ — CONFIRMED: full Turtle Soup rules (20d low, prior low ≥4d earlier, entry above prior low, stop below entry-day low, 1-day validity, one re-entry).
- alvarezquanttrading.com RSI2 posts (both) — CONFIRMED: distribution study 2007–17 + strategy CAR/DD/Sharpe with ex-index universe change 2007–2018.5.
- quantpedia.com/strategies/turn-of-the-month-in-equity-indexes/ — CONFIRMED: McConnell & Xu; 1926–2005; 7.2% pa, vol 6.9%, Sharpe 1.04, MDD −20.79%; ~30 markets.
- libertystreeteconomics 2021-05 + 2026-07 posts — CONFIRMED: drift 1998–2019 overnight ≈2.6% ann, 2–3am ET ≈3.6%; 2026 post: ≈zero since 2021, closing-imbalance dispersion 6.5%→2.9%.
- quantifiableedges.com/reversal-tendencies-for-2-gaps-lower/ — CONFIRMED: SPY ≥2% gap down since 1960 closed above open ~69% of time (as of 2008-10-23).
- bettersystemtrader.com/124-managing-trades-with-linda-raschke/ — CONFIRMED: 2017-10-01; three exit families; first-30-min NYSE volume tone; breadth confirmation.
- github.com/sharebook-kr/larry_simple + raw master/main.py — CONFIRMED: target = open + 0.5×(prior range), buy on cross, scheduled time exit, BTC/Korbit.
- github.com/nerdyckc/turtle_soup_bitmex — CONFIRMED: Street Smarts turtle soup implementation, 14 stars, updated 2026-05.
- lindaraschke.net /articles/ + /linda-videos/ — CONFIRMED: free PDFs; video "Day Type, Taylor Trading, Trade Location, More".
- concretumgroup.com can-day-trading + profitable-day-trading pages — CONFIRMED: QQQ/TQQQ 2016–23 +1,484% vs +169%, 33% ann alpha; stocks-in-play top-20 +1,600% net, Sharpe 2.81, 36% alpha.
NOT re-verified this session (present in first-pass notes only; excluded from lead SOURCE lines): stonex Taylor blog, luxalgo turtle-soup, tradersmastermind, netpicks, cxoadvisory, quantifiedstrategies substack posts, oxfordstrat narrow-range-1, quantifiableedges massive-gap-down, completetradersedge.
Still unsourceable: Sheldon Knight / K-Data (all fetchable engines blocked; Futures Magazine archive offline); Crabel doji/hook exact tables; Street Smarts 80-20 exact-rule page.
