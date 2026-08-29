# G2W1 A5-VENDORS — Commercial Indicator Scout — full notes
Accessed: 2026-08-28. Read-only public browsing. WebSearch budget was exhausted (200/200)
after 1 call; fell back to WebFetch on site-native search/browse/sitemap/robots URLs per
constraints (noted in final summary).

## Coverage log (what was actually visited)

| Target | URL | Result |
|---|---|---|
| ninZa.co | https://ninza.co/ , /sitemap.xml , /product/ | HTTP 403 (Cloudflare) on all content pages; robots.txt fetched OK (allows /product/, /blog/; sitemap listed but 403). Only artifacts reachable: free ninZaATR + ninZaRenko listings on NinjaTrader Ecosystem. NO LEAD — access blocked. |
| SharkIndicators | https://sharkindicators.com/ , /products/bloodhound/ , /products/advanced-strategy-packs/ | OK. BloodHound = no-code node logic engine; BlackBird = trade management (high-water-mark profit protection, pre-programmed order movement, scaling, exposure limits). Strategy packs (Breakout Legends / Trend Riders / Reversal Kings) pages carry NO concrete rules publicly, no performance. |
| LizardIndicators | homepage, /blog/, /revisited-trading-the-opening-range/, /the-ttm-squeeze/, /camarilla-pivots/ | OK. 145+ indicators, $195 lifetime. Blog gives genuinely concrete rules (best public-rule density of any vendor visited). |
| Indicator Warehouse | https://indicatorwarehouse.com/ | OK but homepage has zero concrete logic, no product names visible without JS. NO LEAD. |
| Jigsaw | homepage, /blog/ (JS-empty), ?s=trapped, /blog/master-trade-management-using-order-flow/ | OK. Concrete order-flow management rules found in 2022 article. daytradr, Journalytix (40M trades analyzed claim), Market Intelligence. |
| Bookmap | bookmap.com/addons 403; marketplace.bookmap.com = JS SPA (title only); sitemap/robots 404 | Marketplace itself unreachable without JS/login. Substituted third-party public description tradersentiments.com/bookmap (fetched OK) for the heatmap/liquidity-wall claim. Bing search confirmed marketplace exists behind login. |
| MotiveWave | docs.motivewave.com/studies/a-b, /llms.txt, dom-power.md, speed-of-tape.md | OK. Docs are markdown-accessible with condensed calculation logic. Volume & Order Flow guide: Big Trades, Speed of Tape, Delta, Cum Delta, TPO, Volume Imprint, Order Heatmap (DOM history), DOM Power, Speed Gauges. |
| Sierra Chart | StudiesReference.php, NumbersBars.php, StudiesReference.php&ID=390 | OK. Numbers Bars: per-price bid/ask vol, diagonal comparisons, threshold defaults .25/.50/.75 (pct) and 100/200/300 (volume); needs 1-tick data with bid/ask trade volume, no depth needed. LVTI (ID=390): single-trade volume >= threshold, bid/ask dominant coloring, tick-by-tick required. |
| TradingView | /scripts/editors-picks/ OK; /scripts/?q=smart money concepts 403 | Editors' picks yielded: DGT Initial Balance Auction Intelligence (fetched script page — full rule set public, open source), QuantAlgo Time-of-Day/Session Performance Stats, Zeiierman LTF Volume Microburst Bubbles, LuxAlgo Universal Signal Backtester. |
| LuxAlgo | luxalgo.com, docs.luxalgo.com | OK but only marketing-level: Signals & Overlays / Oscillator Matrix / Price Action Concepts named, no concrete rules reachable without JS. NO LEAD (PAC rules not verifiable today). |
| NinjaTrader Ecosystem | /user-app-share-download-category/strategy/, ?s=ninza | OK. Strategy category: SLN Quantum Freya (no performance), Digital Ninja Systems ORB (no performance). **No NQ strategy with published performance found in the public category pages.** |

## Key vendor-claim → observable → transformation maps (basis for leads)

1. Lizard noise-band ORB: prior-4-week avg volatility → open ± noise bands; targets at
   pre-session low / 50% pre-session expansion band. Lineage: Fisher ACD, Crabel stretch.
2. DGT IB Auction: IB (5/10/15/30-min) → 5-state machine (Accepted/Failed Above-Below,
   Continuation, Rejection, Two-Sided) + 0.5/1.0/1.5× IB projections; alerts on confirmed
   transitions; pressure score −100..+100. Open source = full clean-room already public.
3. Camarilla (Lizard): R/S = Close ± Range×1.1/{12,6,4,2}, R5=(H/L)×C; open inside S3/R3
   → fade to S1-3/R1-3, open outside → breakout-after-retrace. Examples on 5-min NQ.
4. TTM Squeeze (Lizard): BB inside Keltner; min 3 squeeze bars; valid signal ≤5 bars after
   release; thrust bar = close beyond prior high/low; "13-bar momentum filter" mentioned.
5. BlackBird: policy family only — HWM profit protection, staged order movement, scaling,
   exposure caps. Pure RISK-SPEC/EXECUTION transformation, no information claim.
6. Jigsaw: exit when order flow supports the move against you; strength-meter market-order
   imbalance (example 1427 sell vs 850 buy); trapped traders; absorption circles; claim
   "reduce losses by 50%" vs fixed stops (anecdote).
7. Numbers Bars: diagonal ask(p) vs bid(p−1) imbalance, thresholds 25/50/75%; POC; needs
   only aggressor-side tick volume (we own 2025-26 tick/BBO).
8. LVTI: single prints ≥ N lots with side dominance. Institutional lot-size footprint.
9. Speed of Tape: count/volume/delta per N-sec window; signal = cross above SMA of itself.
10. DOM Power: total bid depth − total ask depth ("delta ... total bid size and the total
    ask size") as S/R. Needs L2 — our DOM collection is PAUSED; degenerate BBO-size test only.
11. Bookmap heatmap (via tradersentiments.com): resting-liquidity heatmap claimed to be a
    "leading indicator"; liquidity walls = reaction zones. Needs book depth history (MBO).
12. QuantAlgo ToD stats: rank hours/sessions by range, volume, bias, drift.
13. Zeiierman Microburst: intra-candle LTF volume bursts = unusually strong activity.
14. Freya (Ecosystem): risk-reward entry filter + ATR/anti-chop + trailing; internals opaque,
    Telegram control; no performance published → marketplace evidence-quality datum.

## Clean-room reconstruction flags
- Fully reconstructable from public rules: DGT IB (open source), Camarilla, TTM Squeeze,
  Lizard noise-band ORB (band definition stated), Numbers Bars, LVTI, Speed of Tape,
  QuantAlgo ToD (methodology described).
- Partially (behavioral, from videos/screenshots with timestamps): Jigsaw daytradr signals,
  Bookmap heatmap reactions, BlackBird management behavior.
- Not reconstructable publicly: ninZa paid indicators (site blocked), LuxAlgo PAC internals,
  Freya internals, Shark strategy-pack internals.

## Marketplace performance-publication answer
NinjaTrader Ecosystem public strategy listings inspected carry NO published performance
(both entries checked). TradingView editors' picks are logic-transparent but performance-free.
No vendor visited today publishes an audited or even screenshot backtest on its public pages;
SharkIndicators explicitly disclaims testimonials. Evidence grade across the domain: none →
anecdote → examples. Nothing above 'examples' anywhere.
