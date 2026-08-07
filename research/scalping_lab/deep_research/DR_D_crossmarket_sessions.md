# DR-D — Cross-Market Structure (DR-S05) & Session Transitions (DR-S08)

**Agent:** CROSS_MARKET_RESEARCHER · **Date:** 2026-08-07 · **Method:** literature/mechanism research only (no data analysis performed).
**Cost context (frozen, EXECUTION_MODEL.md):** C1 ≈ 2.872 NQ ticks/RT = $14.36; decision-to-fill latency 250 ms–2 s. Anything requiring sub-second reaction is labeled **NON_RETAIL**.
**Scope:** DR-S05 (NQ/ES lead-lag, cross-impact, index price discovery) and DR-S08 (09:30 cash open, 16:00 cash close / MOC machinery, 16:15–16:30 halt, 17:00–18:00 maintenance, 18:00 reopen, European overlap, weekends/holidays).

---

## 1. Established findings (citations, magnitudes, horizons)

### 1.1 Where price discovery happens in the US index complex

- [Hasbrouck (2003, *Journal of Finance* 58:2375–2400), "Intraday Price Formation in U.S. Equity Index Markets"](https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1540-6261.2003.00609.x): for both the **S&P 500 and the Nasdaq-100, most price discovery occurs in the E-mini futures** (ES, NQ), not the ETF (SPY, QQQ), estimated at up to 1-second resolution. The futures are the information anchor; the cash/ETF complex adjusts to them.
- Corollary for us: **NQ is itself the price-discovery venue for Nasdaq-100 risk.** There is no slower "upstream" instrument we can watch to front-run NQ; the only candidate upstream signal is *another risk factor* (broad-market flow via ES) — not a stale copy of the same factor.
- Caveat: Hasbrouck's data are 1999–2000. The 2020s complex adds 0DTE index options as a material price-discovery/flow venue (see §1.5); no clean modern information-share decomposition for NQ vs QQQ vs options was found in this pass — treat the "E-mini dominates" result as directionally robust but dated.
- [Huth & Abergel (2014, *J. Empirical Finance*), "High-frequency lead/lag relationships — empirical facts"](https://www.sciencedirect.com/science/article/abs/pii/S0927539814000048) (Hayashi–Yoshida on tick data): **the more liquid asset leads**; futures→stock lead-lag is strong and asymmetric, stock↔stock lead-lag is weak; lags are sub-second to seconds and show intraday seasonality (regime changes at macro releases and the US cash open). ES is materially more liquid than NQ in notional/depth terms, so *if* any ES→NQ lead exists it should be at these (sub-)second scales — exactly where HFT lives (§1.2).

### 1.2 The speed race: what is definitively gone (NON_RETAIL, with evidence)

- [Budish, Cramton & Shim (2015, *QJE* 130:1547), "The High-Frequency Trading Arms Race"](https://academic.oup.com/qje/article/130/4/1547/1916146): ES–SPY arbitrage opportunities: **median duration fell from 97 ms (2005) to 7 ms (2011)**; the ES–SPY 1-second correlation is near 1 but the **millisecond-scale correlation is near 0** — the canonical demonstration that naive lead-lag exists only inside the race window. Per-opportunity profit stayed roughly constant (~$79 median), ~800 opportunities/day, ~$75M/yr prize in ES-SPY alone; competition shrinks the *window*, not the *profit per event*.
- [Aquilina, Budish & O'Neill (2022, *QJE* 137:493), "Quantifying the High-Frequency Trading Arms Race"](https://academic.oup.com/qje/article/137/1/493/6368348) (exchange message data): latency races occur **~once per minute per liquid symbol; modal race duration 5–10 microseconds; ~20% of volume trades in races; top 6 firms win/lose >80% of races**; latency arbitrage ≈ a 0.5 bp tax on trading, ~$5B/yr in global equities.
- [Laughlin, Aguirre & Grundfest (2014), "Information Transmission Between Financial Markets in Chicago and New York"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2227519) ([arXiv:1302.5966](https://arxiv.org/abs/1302.5966)): documented a **3 ms decline in one-way Chicago↔NJ latency (2010–2012)** from latency-optimized fiber then 6–11 GHz microwave; **>$500M** infrastructure/5-yr-ops spend; modern microwave runs within a few percent of the vacuum-light limit (~3.94 ms one-way).
- [Dobrev & Schaumburg (Fed, 2015–2018), "High-Frequency Cross-Market Trading: Model-Free Measurement and Applications"](https://www.atlantafed.org/-/media/documents/news/conferences/2018/1018-financial-stability-implications-of-new-technology/papers/dobrev-schaumburg_high-frequency-cross-market-trading.pdf): substantial fractions of trades in US equity index and Treasury markets are **cross-market events** — trades in one venue triggered within milliseconds by activity in another; cross-market arbitrageurs actively enforce alignment between cash and futures.
- **Critical structural fact for ES↔NQ specifically:** both contracts match on the *same* CME Globex engine (same facility, same clock). There is no geographic latency between them at all — cross-contract alignment is enforced by co-located firms at microsecond scale. Any *price-level* lead-lag between ES and NQ at sub-second horizons is inside the race and unreachable at 250 ms–2 s latency. (This same fact is what makes the timestamp-sync audit in §3 a known-answer test.)

### 1.3 What plausibly survives: cross-impact of *order flow*, not price

- [Cont, Cucuringu & Zhang (2023, *Quantitative Finance* 23(10)), "Cross-Impact of Order Flow Imbalance in Equity Markets"](https://www.tandfonline.com/doi/abs/10.1080/14697688.2023.2236159) ([arXiv:2112.13213](https://arxiv.org/abs/2112.13213)); top-100 S&P stocks, 2017–2019, LOBSTER/ITCH, 10:00–15:30 sample: (i) an **integrated multi-level OFI** explains contemporaneous impact so well that *contemporaneous* cross-impact terms add nothing; but (ii) **lagged cross-asset OFI significantly improves out-of-sample forecasts of future returns at horizons of ~1 to several minutes**, with predictability **decaying rapidly** (tested out to 30 min; R² gains small — order sub-1% — but significant at 1% across stocks).
- Interpretation that matters for us: **price levels are arbitraged in microseconds; order-flow information diffuses across assets over seconds-to-minutes.** The mechanism (gradual portfolio rebalancing, correlated-flow propagation, slower multi-asset execution algos) is not a race — the marginal counterparty is not competing on speed. This is the only DR-S05 channel with published, recent, out-of-sample support at horizons a 250 ms–2 s pipeline can reach.
- Honest transfer caveat: the evidence is for *single stocks*; ES↔NQ is a far tighter arbitrage pair, so cross-impact between them should be weaker/faster than stock-to-stock. This is a hypothesis to test, not a fact (→ H-DR-D1, D2).

### 1.4 Overnight vs intraday decomposition; the overnight drift and its death

- [Cooper, Cliff & Gulen (2008), "Return Differences between Trading and Non-Trading Hours: Like Night and Day"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1004081): the US equity premium in their sample is **entirely overnight** (night returns per stock ≈ +2.8 to +4.8 bp; day ≈ −2.9 to +0.2 bp, S&P 500 stocks 1993–2006); holds for index futures; partially driven by **high opens that decay in the first hour** of the cash session.
- [Lou, Polk & Skouras (2019, *JFE*), "A Tug of War: Overnight vs Intraday Expected Returns"](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19300650): of 14 known strategies, profits accrue **either entirely overnight (momentum) or entirely intraday (value-type), with opposite signs across components** — investor-clientele driven, persistent for years.
- [Boyarchenko, Larsen & Whelan (2023, *RFS* 36(9)), "The Overnight Drift"](https://www.newyorkfed.org/research/staff_reports/sr917): 1998–2019/2020, ES futures earn **~3.6–3.7%/yr in the single hour 02:00–03:00 ET (European open) — >60% of the E-mini's entire 5.9% annualized return**. Mechanism: dealers absorb end-of-day (cash-close) order imbalance, carry inventory overnight, unwind into fresh European liquidity; effect is **asymmetric — strong positive rebound after down-closes/sell imbalance, weak after rallies**.
- [NY Fed Liberty Street Economics (July 2026), "The Disappearing Overnight Drift"](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/): **the 02:00–03:00 drift has averaged ≈ zero since 2021.** Decomposition E[R_ON] ∝ imbalance × variance / risk-capacity: the collapse is attributed to **compression of closing order imbalances** (σ of end-of-day relative signed volume fell 6.5% → 2.9%; extreme-imbalance days much rarer), while variance and dealer risk capacity are ~unchanged. ⇒ **The unconditional European-open long is dead; the conditional (extreme-imbalance-day) version is the open question** (→ H-DR-D4).
- [Bogousslavsky (2021, *JFE*), "The Cross-Section of Intraday and Overnight Returns"](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21000854): overnight margin/lending-fee constraints make arbitrageurs cut positions before the close — a structural reason why late-day and overnight flows are *mechanical* rather than informational.

### 1.5 Intraday momentum, close-window flows, and the 0DTE-era caveat

- [Gao, Han, Li & Zhou (2018, *JFE*), "Market Intraday Momentum"](https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351): SPY 1993–2013 — the **first half-hour return (prev-close→10:00) positively predicts the last half-hour (15:30–16:00)**; slope 6.94 (×100), **R² ≈ 1.6%**, stronger on high-volatility, high-volume, recession, and macro-news days; replicates in 10 other liquid ETFs (QQQ included).
- [Baltussen, Da, Lammers & Martens (2021, *JFE*), "Hedging Demand and Market Intraday Momentum"](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21001598): **60+ futures (equities, bonds, commodities, FX), 1974–2020 — last-30-min return is positively predicted by the rest-of-day return**; attributed to **short-gamma hedging** by option market makers and leveraged-ETF rebalancing (both must trade *with* the day's move into the close); the effect **reverts over subsequent days** (it is flow pressure, not information).
- [Baltussen, Da & Soebhag, "End-of-Day Reversal"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009): *cross-sectional* — the day's biggest losing stocks outperform winners in 15:30–16:00 (attention-driven retail buying + short-seller risk management; explicitly *not* gamma). Cross-sectional, so only indirectly relevant to NQ index-level, but it confirms the last half-hour is structurally flow-dominated.
- **0DTE-era conditionality:** [Dim, Eraker & Vilkov, "0DTEs: Trading, Gamma Risk and Volatility Propagation"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4692190): SPX market-maker net gamma from 0DTE is on average **positive**, and **positive dealer gamma strengthens intraday reversal / mutes momentum** (negative gamma does the opposite); [Cboe research](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf) and Adams-Fontaine-Ornthanalai (2024) find lower realized vol on 0DTE-active days. ⇒ Published pre-2020 last-half-hour momentum results plausibly **weakened or became regime-dependent after ~2021-2023**; any retest must split the sample by era and, ideally, condition on a gamma-regime proxy (→ H-DR-D5).

### 1.6 Auction and session mechanics — the mechanical clock (all times ET)

**US cash close (the machinery behind Z4/M3-type hypotheses):**
- **Nasdaq closing cross** (NQ's constituent listing venue — most relevant to NQ): Net Order Imbalance Indicator (**NOII**) disseminated from **15:50 (every 10 s), then from 15:55 every 1 s** until the 16:00 cross; MOC entry until ~15:55 (no modify/cancel after 15:50); LOC accepted to ~15:58 subject to reference-price constraints. [Nasdaq closing cross FAQ](https://www.nasdaqtrader.com/content/productsservices/Trading/ClosingCrossfaq.pdf), [Nasdaq crosses fact sheet](https://www.nasdaqtrader.com/content/productsservices/trading/crosses/fact_sheet.pdf).
- **NYSE**: MOC/LOC entry cutoff **15:50**; MOC/LOC **Regulatory Imbalance published at 15:50**, informational imbalance updated every 1 s; after 15:50 MOC/LOC only on the offsetting side; floor-broker **D-Orders until 15:59:50** and these are ~**60% of auction volume** (MOC and LOC ~20% each). [NYSE closing process fact sheet](https://www.nyse.com/publicdocs/nyse/NYSE_Auctions_Closing_Process_Fact_Sheet.pdf).
- **Scale**: closing auctions matched **$55.5B/day = 9.44% of total US notional in Q2 2024 (record)**; NYSE closing auction ≈ 10.5% of NYSE-listed volume and still growing through 2025–26. [BMLL](https://www.bmlltech.com/news/market-insight/into-the-close-unpacking-u-s-closing-auction-dynamics-and-the-impact-of-the-russell-reconstitution), [NYSE research](https://beta.nyse.com/data-insights/nyse-closing-auction-price-discovery-opportunities-reach-new-highs).
- **Transmission to NQ**: index-arb desks hedge auction exposure in futures during 15:50–16:00, so a large one-sided imbalance in Nasdaq-listed names should leak into NQ *during the publication window*. Academic support is indirect (the overnight-drift paper's close-imbalance channel; practitioner sources like [SpotGamma's MOC documentation](https://support.spotgamma.com/hc/en-us/articles/15249378625555-MOC-Market-on-Close)). Direct "NOII → ES/NQ 15:50–16:00 drift" studies were **not found in peer-reviewed form** — this is a genuine gap, i.e., a testable hypothesis rather than settled science (→ H-DR-D3).

**Futures session skeleton (CME equity index):** cash open 09:30; cash close 16:00; **futures halt 16:15–16:30**; daily maintenance **17:00–18:00 (Mon–Thu)**; Globex reopen **18:00** (pre-open order entry with indicative price, then opening match); weekly close Fri 17:00; Sunday reopen 18:00. Overnight liquidity is far thinner: 1–2 tick slippage on market orders is normal, spreads widen, and RTH carries the overwhelming share of volume. [CME trading-hours references](https://www.cmegroup.com/education/files/eq-trading-hours.pdf), [session guides](https://proptradingvibes.com/blog/futures-market-hours).

**European overlap:** Eurex derivatives open 02:00 ET (08:00 CET), LSE cash 03:00 ET. This is exactly the Boyarchenko et al drift window (02:00–03:00) — now flat unconditionally (§1.4) but still the hour where overnight NQ volume/volatility steps up materially; it functions as a *regime boundary* even if the drift is gone (→ H-DR-D8).

**Weekend/day-of-week:** the classical weekend effect (negative Mon) weakened/reversed already by the late 1990s ([Boston Fed WP 98-6](https://www.bostonfed.org/-/media/Documents/Workingpapers/PDF/wp98_6.pdf); [Review of Quant. Finance 2004 "Reversing Weekend Effect"](https://link.springer.com/article/10.1023/B:REQU.0000006183.42549.50)); no credible 2020s evidence of an exploitable unconditional day-of-week effect in index futures was found. Treat day-of-week only as a *conditioning/nuisance variable* (T1), never as a standalone edge.

### 1.7 Opening-range breakout (ORB) — the honest read

- [Zarattini & Aziz (2023), "Can Day Trading Really Be Profitable?"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622) and [Zarattini, Barbon & Aziz (2024)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284): 5-min ORB on QQQ/TQQQ (2016–2023) claims ~33%/yr alpha net of commissions; the stocks version uses relative-volume "stocks in play."
- Replication reality check: independent reruns ([QuantConnect](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/), [CXO](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/), lay replications) find results **highly sensitive to data vendor (>3× dispersion from phantom highs/lows, stale bars, tick-to-bar assignment), stop-fill assumptions, and slippage**; the edge concentrates in fast conditions where realistic slippage is worst. Verdict: the *statistical tendency* (open initiates daily-range extension; first-hour direction informative) is plausibly real; the *published magnitudes* are not trustworthy at C1 with conservative fills. Our M2/Z5 tests must be built from our own NQ data with the C1/C2 grid, not from these papers' assumptions.

---

## 2. Dead vs plausibly alive at 250 ms–2 s latency

| Mechanism | Verdict | Evidence |
|---|---|---|
| ES↔SPY / ES↔NQ / NQ↔QQQ **price-level** lead-lag at sub-second horizons | **NON_RETAIL — definitively arbitraged** | BCS 2015 (7 ms median by 2011); ABO 2022 (races 5–10 µs, 20% of volume); same-engine co-location for ES/NQ |
| Geographic (Chicago↔NJ) latency arb, index basis sniping | **NON_RETAIL** | Laughlin et al 2014; >$500M microwave infrastructure at light-speed limit |
| Reacting to NOII/imbalance feed ticks in <1 s | **NON_RETAIL** | Feeds consumed co-located; 1-s update frequency 15:55–16:00 already institutionalized |
| Opening-print/auction sniping at 09:30 or 18:00 reopen first-tick | **NON_RETAIL** | Auction mechanics + race evidence above |
| **Lagged cross-asset order-flow impact at ~30 s–5 min** (ES flow state → NQ) | **Plausibly alive, weak** (sub-1% R² in stocks; untested on ES/NQ) | Cont-Cucuringu-Zhang 2023 |
| **Conditional close-imbalance → overnight/Euro-open rebound** (extreme days only) | **Plausibly alive, conditional**; unconditional version **dead since 2021** | Boyarchenko et al 2023; NY Fed 2026 |
| **First half-hour → last half-hour index momentum** (daily horizon) | **Plausibly alive, regime-dependent** (0DTE-era weakening likely) | Gao et al 2018; Baltussen et al 2021; Dim-Eraker-Vilkov |
| **15:50–16:00 mechanical flow window in NQ** | **Plausible, under-documented academically** — genuine gap | §1.6 mechanics; indirect channel evidence |
| Cash-open (09:30) gap-fade / first-hour decay of high opens | **Plausibly alive, era-sensitive** | Cooper-Cliff-Gulen 2008; ORB literature (contested) |
| 18:00 reopen micro-drift | **Unknown; friction-hostile** (thin book, wide spread) | §1.6; no direct literature found |
| Unconditional day-of-week / weekend effects | **Dead / unstable** | §1.6 weekend refs |

Why the "alive" set survives speed competition: none of them are races. They are **risk-bearing or capacity phenomena** — dealer inventory compensation, hedging-flow pressure, slow diffusion of correlated order flow — where the profit accrues to whoever is willing to hold the risk for minutes-to-hours, not to whoever reacts first. That is precisely the niche a 250 ms–2 s retail pipeline can occupy; the residual question is only whether the effect clears **2.872 ticks/RT**.

---

## 3. Data requirements & the timestamp-sync audit

**What each class of hypothesis needs:**

| Hypothesis class | Series | Bar/tick resolution | Cross-instrument sync tolerance |
|---|---|---|---|
| D1 (ES flow → NQ, 30 s–5 min) | ES + NQ, synchronized | 1-s bars or tick (bid/ask-stamped ticks strongly preferred for signed flow) | **≤ 250 ms** constant skew; *stable* skew matters more than small skew |
| D2 (relative-state, minutes) | ES + NQ | 1-s to 1-min bars | ≤ 1 s |
| D3, D5, D6 (session windows, RTH) | NQ alone (ES optional confirm) | 1-min bars (1-s for D3) | ≤ 1 s (single-instrument mostly immune) |
| D4, D8 (overnight/Euro-open) | NQ alone | 1-min bars | immune (window boundaries only need clock correctness to ~seconds) |
| D7 (18:00 reopen) | NQ + spread state | tick with bid/ask | immune cross-instrument; needs honest spread data |

**Known NT8 facts (from vendor forum evidence, to be verified by our own audit):** NT8 historical tick data via NinjaTrader/Continuum servers carries **millisecond timestamps stamped by the provider**, and recorded-live vs historical Continuum ticks matched closely in one user comparison; **Kinetick historical data had a documented millisecond-truncation inconsistency** (ms components with leading zeros mangled vs live). Local PC clock matters only for live recording, not for provider-stamped history. ([NT forum: Continuum ms](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/93566-continuum-historical-data-not-showing-milliseconds), [Kinetick timestamp issues](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1200306-timestamp-issues-with-kinetick-data-live-versus-historical).)

**The single biggest sync risk:** ES and NQ history are downloaded as **separate per-instrument streams**; any constant or state-dependent offset between the two series (vendor batching, snapshot cadence, ms truncation, or 1-s granularity fallback on older history) will **manufacture spurious sub-minute "lead-lag" in whichever direction the offset points** — and it will look beautifully significant, because the two contracts are ~0.9 correlated at minute scale.

**Mandatory known-answer test (KAT) before any DR-S05 analysis:** compute the tick-scale (or 1-s) ES↔NQ return cross-correlation function on our NT8 data. Because both contracts match on the same Globex engine and are policed by co-located arbitrage, **the true peak must sit at lag ≈ 0 (within ~10 ms)**. Wherever our measured peak sits *is our effective cross-feed skew*, and its day-to-day dispersion is our skew stability. Rule: no ES→NQ hypothesis may be tested at horizons shorter than ~10× the measured skew + its dispersion. If the data only supports 1-s granularity, the floor for cross-market horizons is ~30 s–1 min.

---

## 4. Testable hypotheses

Naming: H-DR-D#. Seed-family mapping per `HYPOTHESES.md` (X1/X2/X3, M2, M3, Z4, Z5, Z6, T1). Costs at **C1 = 2.872 NQ ticks/RT** unless stated.

---

### H-DR-D1 — Lagged ES order-flow state predicts NQ continuation at 30 s–5 min (X1, S9)

Trailing ES signed-flow/return-innovation state (e.g., 1–5 min ES signed volume imbalance, or ES return minus beta-implied NQ-consistent return) predicts the **next 1–5 min NQ return** with positive sign, over and above NQ's own lagged flow/returns. This is the ES/NQ transfer of Cont-Cucuringu-Zhang: price levels are arbitraged instantly but *flow pressure* propagates slowly.

- **ECONOMIC MECHANISM:** multi-asset execution algos and index-complex rebalancers split correlated parent orders across ES, NQ, SPY, QQQ over minutes; the portion already executed in ES reveals pressure not yet fully expressed in NQ. Not a race: the counterparty is a scheduled algo, not an HFT.
- **OBSERVABLE VARIABLES:** ES signed volume / uptick-downtick imbalance over trailing 1–5 min; ES return innovation orthogonalized on contemporaneous NQ return; NQ forward returns 30 s–5 min.
- **EXPECTED HORIZON:** predictor window 1–5 min; forecast horizon 30 s–5 min; decay to zero within ~10 min.
- **EXPECTED SIGN:** positive (continuation in the direction of ES flow).
- **REQUIRED DATA:** synchronized ES + NQ, 1-s bars minimum (bid/ask-stamped ticks preferred for signed flow); **sync KAT from §3 passed first**; skew ≤ 250 ms stable.
- **RETAIL EXECUTABILITY:** yes at ≥30 s horizons with 250 ms–2 s latency; market orders; the question is purely whether conditional edge > 2.872 ticks.
- **SIMPLE NULL:** NQ forward return regressed on NQ's own lagged flow/returns only; ES terms add no out-of-sample R²/PnL. Also: shuffled-day ES series (preserves NQ autocorrelation, kills cross link).
- **FALSIFICATION EXPERIMENT:** rolling OOS regression / simple tercile-conditioned entry on 2+ years of RTH data; kill if ES-conditioned tercile spread at best horizon < C1, or if incremental OOS R² ≤ 0 in a majority of quarters, or if the effect exists only at horizons below the measured sync floor (then it is a timestamp artifact by construction).
- **PRIORITY:** 1

---

### H-DR-D2 — NQ/ES beta-adjusted divergence: state variable, weak reversion (X2/X3)

Minute-scale divergence of NQ from its rolling-beta ES-implied path is (a) at best weakly mean-reverting as a standalone signal, but (b) a useful **conditioning state**: NQ-side moves *unconfirmed* by ES are more likely to fail (feeds S4 failed-break family); ES-confirmed moves continue.

- **ECONOMIC MECHANISM:** true ES↔NQ price arb is instantaneous (§1.2), so minute-scale divergence is mostly *genuine* tech-vs-broad repricing — a random walk — except when driven by transient single-market flow pressure, which reverts. Confirmation splits the two cases.
- **OBSERVABLE VARIABLES:** z-score of (NQ return − β·ES return) over trailing 5–30 min windows; interaction with breakout/impulse triggers from S-families.
- **EXPECTED HORIZON:** state windows 5–30 min; effect on trade outcomes at the host strategy's horizon (minutes).
- **EXPECTED SIGN:** standalone: weakly negative (reversion) at best; as filter: ES-confirmed breakouts > unconfirmed breakouts in continuation rate.
- **REQUIRED DATA:** synchronized ES + NQ 1-s or 1-min bars; sync ≤ 1 s (minute-horizon tolerant).
- **RETAIL EXECUTABILITY:** yes — it is a filter on strategies we already execute; adds no latency demand.
- **SIMPLE NULL:** divergence z-score is a martingale (no reversion); filter permutation test: randomly reassign confirmed/unconfirmed labels across trades.
- **FALSIFICATION EXPERIMENT:** (i) variance-ratio / OU half-life test on the divergence series — if half-life is not materially < 1 day with stable sign, standalone version dies; (ii) run one existing S-family backtest split by confirmation state — kill filter if outcome difference < 0.5 tick per trade or unstable across years.
- **PRIORITY:** 2

---

### H-DR-D3 — Cash-close mechanical window: 15:50–16:00 continuation of imbalance-proxy moves (Z4, M2-close)

During 15:50–16:00 ET, NQ drifts in the direction of the move that occurs in the **imbalance-publication window** (15:50–15:55), because that move is caused by index-arb hedging of the published Nasdaq/NYSE closing imbalances, and the MOC flow itself completes at 16:00 in the same direction.

- **ECONOMIC MECHANISM:** NOII/NYSE regulatory imbalances become public at 15:50 (§1.6); index-arb desks and closing-auction liquidity providers hedge in futures between publication and the 16:00 cross; D-orders (60% of NYSE auction volume) arrive until 15:59:50, extending the pressure. Gamma-hedging flow (Baltussen et al 2021) pushes the same direction on trend days.
- **OBSERVABLE VARIABLES:** NQ return and volume 15:50→15:55 (imbalance proxy; we have no NOII feed in NT8), rest-of-day return (for the Gao/Baltussen overlay), NQ forward return 15:55→16:00.
- **EXPECTED HORIZON:** 5-min predictor, 5-min forecast; hard daily clock — repeats every session.
- **EXPECTED SIGN:** positive (continuation of the 15:50–15:55 move into 16:00), amplified when aligned with the rest-of-day direction.
- **REQUIRED DATA:** NQ 1-s or 1-min bars with reliable session clock (ET); no cross-instrument sync needed. Optional upgrade: actual NOII data (Nasdaq TotalView) — **not available in NT8**; flag as a paid-data fork only if the proxy version shows signal.
- **RETAIL EXECUTABILITY:** yes — one decision at 15:55, exit 16:00 (before the 16:15 halt and within intraday margin, flat by 16:00 < 16:44 constraint); 250 ms latency irrelevant at 5-min horizon.
- **SIMPLE NULL:** the 15:55→16:00 return is unconditionally zero-mean and independent of the 15:50–15:55 move (test vs matched pseudo-windows, e.g., 14:50–14:55 → 14:55–15:00).
- **FALSIFICATION EXPERIMENT:** event-window study over 2+ years; condition on 15:50–15:55 move size terciles × sign; kill if top-tercile conditional mean < C1 (14.36 $/RT) after slippage stress C2, or if pseudo-window placebo shows the same pattern (then it's just generic momentum, already covered by S-families).
- **PRIORITY:** 1

---

### H-DR-D4 — Conditional overnight inventory rebound (extreme close-pressure days only) (M3)

On days with **extreme negative close-window pressure** (bottom decile of 15:30–16:00 signed move/volume state), NQ earns a positive rebound overnight, concentrated in the 02:00–03:00 ET European-open hour. The unconditional overnight drift is dead (≈0 since 2021, NY Fed); the *conditional, asymmetric* dealer-inventory mechanism is the survivor candidate.

- **ECONOMIC MECHANISM:** dealer/LP inventory absorbed at the close must be re-distributed; the first deep liquidity arrives at the European open; compensation for inventory risk = rebound. NY Fed 2026 shows the drift died because *average* imbalances compressed — not because the mechanism broke — so extreme days should still pay. Asymmetry (sell-offs rebound; rallies don't) is documented in the RFS paper.
- **OBSERVABLE VARIABLES:** close-pressure proxy (15:30–16:00 NQ return, downside semivolume, range position at close); overnight NQ returns segmented 18:00→02:00, 02:00→03:00, 03:00→09:30.
- **EXPECTED HORIZON:** condition set at 16:00; position held hours (entry 18:00 or 01:55, exit 03:00–09:30). Low frequency: ~25 trades/yr at decile conditioning.
- **EXPECTED SIGN:** positive after extreme down-pressure closes; ~zero after up-pressure closes (asymmetry is itself a testable prediction).
- **REQUIRED DATA:** NQ 1-min bars covering full Globex sessions, correct ET session template; no cross-instrument sync. Must span pre/post-2021 to reproduce the published regime break as a validity check.
- **RETAIL EXECUTABILITY:** yes, but **overnight margin applies** ($43.4k initial NQ; MNQ version at 6.6-tick C1 friction still viable at multi-hour horizons since expected move ≫ friction); thin-book slippage at 18:00 entry must use C2.
- **SIMPLE NULL:** overnight return is independent of close-window pressure (bootstrap the conditioning labels across days); post-2021 conditional mean = post-2021 unconditional mean.
- **FALSIFICATION EXPERIMENT:** decile-conditioned event study 2019–2026 split pre/post-2021; kill if post-2021 bottom-decile 02:00–03:00 (and 18:00→09:30) conditional mean is not positive and > C2 with t > 2, or if the asymmetry prediction fails (rallies rebound as much as sell-offs → mechanism wrong).
- **PRIORITY:** 2

---

### H-DR-D5 — NQ market intraday momentum: first half-hour → last half-hour, 2020s retest (M2/T1)

The prev-close→10:00 NQ return positively predicts the 15:30–16:00 NQ return (Gao et al: R²≈1.6% on SPY 1993–2013; Baltussen et al: 60+ futures via gamma-hedging demand). Prediction: still present in NQ but **weaker post-2021 and conditional on the dealer-gamma regime** (0DTE-era positive dealer gamma mutes it).

- **ECONOMIC MECHANISM:** short-gamma hedgers (option MMs, leveraged-ETF rebalancing — Nasdaq has the largest leveraged-ETF complex: TQQQ/SQQQ) must trade in the direction of the day's move into the close; day-trader position unwinding adds same-direction flow.
- **OBSERVABLE VARIABLES:** r₁ = prev-close→10:00 return; optionally r_rest = 10:00→15:30; target r₁₃ = 15:30→16:00 return; regime split by year and by realized-vol tercile (proxy for gamma regime without options data).
- **EXPECTED HORIZON:** one decision/day at 15:30, exit 16:00.
- **EXPECTED SIGN:** positive slope r₁→r₁₃ (and r_rest→r₁₃ per Baltussen); attenuated in low-vol/positive-gamma regimes.
- **REQUIRED DATA:** NQ 1-min bars, RTH windows only; no sync requirement. Optional: VIX1D or QQQ 0DTE share as gamma proxy (external data; defer).
- **RETAIL EXECUTABILITY:** yes — trivially; 30-min holding, one RT/day, C1 screen straightforward.
- **SIMPLE NULL:** r₁₃ unpredictable from r₁ (slope = 0 OOS); sign-only test: P(sign(r₁₃)=sign(r₁)) = 0.5.
- **FALSIFICATION EXPERIMENT:** rolling regression + sign-conditioned strategy 2019–2026; kill if post-2021 conditional mean |edge| < C1 on volatility-filtered days (the literature says it concentrates on high-vol days — if it fails *there*, it is gone), or slope sign is unstable across years.
- **PRIORITY:** 1

---

### H-DR-D6 — 09:30 open transition: gap-fade vs gap-continuation regime (Z5, M2)

The overnight gap (18:00-session move into 09:30) resolves in the first 30–60 min of RTH with a **fade bias when the open is extended** (Cooper-Cliff-Gulen: high opens decay in the first hour) and a **continuation bias only when the gap breaks the overnight range with elevated early volume** (the honest residue of the ORB literature).

- **ECONOMIC MECHANISM:** overnight prices are set in thin books by inventory-constrained LPs (§1.4/§1.6); the 09:30 liquidity flood repricing corrects overnight over-extension; genuine information gaps (range-break + volume) instead initiate daily-range extension.
- **OBSERVABLE VARIABLES:** gap = 09:30 open vs 16:00 prior close; gap position within overnight high-low range; first-5/15-min RTH volume vs 20-day same-window average; forward return 09:30+k→10:30.
- **EXPECTED HORIZON:** minutes to 1 hour after open.
- **EXPECTED SIGN:** negative (fade) for large gaps *inside* the overnight range; positive (continuation) for gaps at/beyond overnight extremes with high relative volume.
- **REQUIRED DATA:** NQ 1-min bars, correct session template (18:00–17:00 ET, RTH sub-window); no sync requirement.
- **RETAIL EXECUTABILITY:** yes; entries after 09:30–09:35 avoid the opening race; C1–C2 screening mandatory because open-window slippage is the worst of RTH (ORB replication literature shows vendor/fill assumptions flip the sign of net results).
- **SIMPLE NULL:** first-hour return independent of gap size/position (block-bootstrap days); ORB-style entries no better than random-time entries with matched holding period.
- **FALSIFICATION EXPERIMENT:** two-way conditioning (gap-in-range vs gap-beyond-range × volume tercile) on 2+ years; kill any cell whose conditional mean < C2 or whose sign flips between the two halves of the sample.
- **PRIORITY:** 2

---

### H-DR-D7 — 18:00 Globex reopen settle drift (Z6)

After the 17:00–18:00 halt, the first minutes of the new session drift toward the 16:00–17:00 late-afternoon reference (gap-settle), but the thin book means the effect, even if statistically real, dies at honest C1/C2.

- **ECONOMIC MECHANISM:** reopen prints in a near-empty book overshoot; early liquidity providers re-anchor to the pre-halt reference; also first wave of overnight inventory adjustment (Asia pre-open).
- **OBSERVABLE VARIABLES:** 18:00:00–18:01 print deviation from 16:45–17:00 VWAP; forward return 18:01→18:30; live spread state at 18:00–18:05.
- **EXPECTED HORIZON:** 1–30 min after reopen.
- **EXPECTED SIGN:** negative on the deviation (reversion toward pre-halt VWAP).
- **REQUIRED DATA:** NQ tick or 1-s data with bid/ask through the reopen; spread measurement essential (this is where the "1 tick slip" C1 assumption is least defensible → C2 mandatory).
- **RETAIL EXECUTABILITY:** marginal — mechanics fine at our latency, but spread + slippage in a thin book likely consume the edge; also crosses into overnight margin unless closed same evening (intraday margin runs to 16:45 only — this trade sits entirely in overnight-margin territory).
- **SIMPLE NULL:** post-reopen return independent of reopen deviation; deviation itself ~0 on average.
- **FALSIFICATION EXPERIMENT:** cheap event study; kill unless top-quartile |deviation| days show reversion > C2 (≈4.9 ticks) — pre-registered expectation: **likely killed**; value of the test is mapping reopen spread state for all other overnight hypotheses.
- **PRIORITY:** 3

---

### H-DR-D8 — European-open regime clock (02:00–03:00 ET) as session conditioning (T1, M3-adjacent)

The 02:00 ET Eurex open is a structural regime boundary: NQ realized volatility, volume, and continuation behavior shift measurably at 02:00–03:00. Use as a **conditioning clock for other overnight strategies** (e.g., Family-A-style within-session continuation should behave differently before vs after 02:00), not as a standalone drift (which is dead unconditionally since 2021).

- **ECONOMIC MECHANISM:** first arrival of deep two-sided liquidity after the US close; European hedging/rebalancing flow interacts with residual US close inventory (§1.4).
- **OBSERVABLE VARIABLES:** NQ realized vol / volume / trade intensity by 30-min bucket across the Globex session; conditional continuation stats (e.g., sign-persistence of 15-min moves) before vs after 02:00; DST-shift alignment check (window moves with European clocks — a built-in placebo: the boundary should track CET, not ET).
- **EXPECTED HORIZON:** regime windows of hours; effects measured on minute-scale statistics within them.
- **EXPECTED SIGN:** vol/volume step-up at 02:00–03:00; continuation statistics shift (direction itself is exploratory — this is a mapping hypothesis, pre-registered as descriptive).
- **REQUIRED DATA:** NQ 1-min full-session bars, multi-year; correct ET/CET calendar incl. the 2-week DST misalignment windows (spring/fall) — those fortnights are the natural experiment identifying the European clock as the cause.
- **RETAIL EXECUTABILITY:** yes (it is conditioning, not execution).
- **SIMPLE NULL:** intraday vol/volume profile is smooth through 02:00 (no discontinuity vs neighboring hours); continuation stats identical across the boundary.
- **FALSIFICATION EXPERIMENT:** changepoint/discontinuity test at 02:00 CET-linked boundary incl. DST-shift weeks; if no discontinuity survives the DST placebo, drop European-open conditioning from the campaign permanently.
- **PRIORITY:** 2

---

## 5. Source list (primary)

- Hasbrouck (2003) *JF* — [Intraday Price Formation in U.S. Equity Index Markets](https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1540-6261.2003.00609.x)
- Budish, Cramton, Shim (2015) *QJE* — [The HFT Arms Race](https://academic.oup.com/qje/article/130/4/1547/1916146)
- Aquilina, Budish, O'Neill (2022) *QJE* — [Quantifying the HFT Arms Race](https://academic.oup.com/qje/article/137/1/493/6368348)
- Laughlin, Aguirre, Grundfest (2014) — [Chicago–NY Information Transmission](https://arxiv.org/abs/1302.5966)
- Dobrev, Schaumburg (Fed) — [High-Frequency Cross-Market Trading](https://www.atlantafed.org/-/media/documents/news/conferences/2018/1018-financial-stability-implications-of-new-technology/papers/dobrev-schaumburg_high-frequency-cross-market-trading.pdf)
- Cont, Cucuringu, Zhang (2023) *QF* — [Cross-Impact of OFI](https://arxiv.org/abs/2112.13213)
- Huth, Abergel (2014) *JEF* — [High-Frequency Lead/Lag](https://arxiv.org/abs/1111.7103)
- Cooper, Cliff, Gulen (2008) — [Like Night and Day](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1004081)
- Lou, Polk, Skouras (2019) *JFE* — [A Tug of War](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19300650)
- Boyarchenko, Larsen, Whelan (2023) *RFS* — [The Overnight Drift](https://www.newyorkfed.org/research/staff_reports/sr917)
- NY Fed Liberty Street (2026) — [The Disappearing Overnight Drift](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/)
- Bogousslavsky (2021) *JFE* — [Cross-Section of Intraday and Overnight Returns](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21000854)
- Gao, Han, Li, Zhou (2018) *JFE* — [Market Intraday Momentum](https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351)
- Baltussen, Da, Lammers, Martens (2021) *JFE* — [Hedging Demand and Intraday Momentum](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21001598)
- Baltussen, Da, Soebhag — [End-of-Day Reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009)
- Dim, Eraker, Vilkov — [0DTEs: Trading, Gamma Risk and Volatility Propagation](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4692190)
- Nasdaq — [Closing Cross FAQ](https://www.nasdaqtrader.com/content/productsservices/Trading/ClosingCrossfaq.pdf), [Crosses fact sheet](https://www.nasdaqtrader.com/content/productsservices/trading/crosses/fact_sheet.pdf)
- NYSE — [Closing Process Fact Sheet](https://www.nyse.com/publicdocs/nyse/NYSE_Auctions_Closing_Process_Fact_Sheet.pdf), [Closing auction research](https://beta.nyse.com/data-insights/nyse-closing-auction-price-discovery-opportunities-reach-new-highs)
- BMLL — [US closing auction dynamics](https://www.bmlltech.com/news/market-insight/into-the-close-unpacking-u-s-closing-auction-dynamics-and-the-impact-of-the-russell-reconstitution)
- Zarattini, Aziz (2023) — [Can Day Trading Really Be Profitable?](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622); replication critiques: [QuantConnect](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/), [CXO Advisory](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/)
- NinjaTrader forum (timestamp fidelity) — [Continuum ms timestamps](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/93566-continuum-historical-data-not-showing-milliseconds), [Kinetick live-vs-historical inconsistency](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1200306-timestamp-issues-with-kinetick-data-live-versus-historical)
