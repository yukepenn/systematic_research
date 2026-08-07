# DR-B: Order-Flow and Book-State Predictability (DR-S02, DR-S03, DR-S04, DR-S09)

**Author:** ORDER_FLOW_RESEARCHER (deep literature + mechanism research; no data analysis performed)
**Date:** 2026-08-07
**Instrument context:** NQ (E-mini Nasdaq-100), tick = 0.25 pts = $5.00. Retail cost floor for a market-order round trip C1 = $14.36 ≈ **2.872 ticks**. Decision-to-fill latency **250 ms – 2 s**. Historical bid/ask/depth availability in NinjaTrader 8 is **still under audit** (see `research/scalping_lab/DATA_INVENTORY.md`); every finding below states its minimum data level.

**Data-level taxonomy used throughout:**

| Level | Content |
|---|---|
| L1 | Last-trade events (price, size, time) |
| L2 | BBO quotes (bid/ask **prices**) |
| L3 | Top-of-book **sizes** (bid/ask queue lengths at BBO) |
| L4 | Multi-level depth (MBP-10) or order-by-order (MBO) |

---

## 1. Established findings, with citations and magnitudes

### 1.1 DR-S02 — Order-flow imbalance (OFI) and price impact

**Anchor: Cont, Kukanov & Stoikov, "The Price Impact of Order Book Events," J. Financial Econometrics 12(1):47–88 (2014); arXiv:1011.6402.**
- OFI sums, over a window, the signed contributions of *every* best-level event — limit-order arrivals, cancellations, and trades — treating a market sell and a bid-side cancellation identically (both deplete the bid queue):
  `e_n = 1{P^B_n ≥ P^B_{n−1}}·q^B_n − 1{P^B_n ≤ P^B_{n−1}}·q^B_{n−1} − 1{P^A_n ≤ P^A_{n−1}}·q^A_n + 1{P^A_n ≥ P^A_{n−1}}·q^A_{n−1}`
- **Contemporaneous** mid-price change is *linear* in OFI: average **R² ≈ 65%** across 50 US stocks at 10-second windows (April 2010 TAQ). Trade imbalance (signed trade volume only) achieves **R² ≈ 32%** — half the explanatory power.
- The impact coefficient scales inversely with depth: β ≈ c/AD^λ with **λ̂ ≈ 0.98** (λ = 1 not rejected for 35/50 stocks). Price impact per contract of imbalance is ~1/(2×average best-level depth) — this is a *mechanical* consequence of queue depletion, not information.
- The linear law holds from ~10 quote updates (<0.5 s) up to ~10 min; fit *improves* with window length. Crucially, this is **contemporaneous explanation, not forecasting**.

**Follow-up: Cont, Cucuringu & Zhang, "Cross-Impact of Order Flow Imbalance in Equity Markets," Quantitative Finance (2023); arXiv:2112.13213.** Top-100 S&P500 names, Nasdaq ITCH via LOBSTER, 2017–2019, 10 book levels:
- Contemporaneous 1-min out-of-sample R²: best-level OFI **64.6%**; PCA-integrated multi-level OFI **83.8%** (in-sample 71.2% / 87.1%). Multi-level depth adds ~19 points of R² over best-level.
- **Forecasting** future 1-min returns with lagged OFI: R² collapses by roughly two orders of magnitude relative to contemporaneous fits (single-percent territory, as is standard in this literature); cross-asset lagged OFI adds a small increment that "mainly manifests at short-term horizons and decays rapidly in time."

**Deep-learning extension: Kolm, Turiel & Westray, "Deep Order Flow Imbalance," Mathematical Finance 33(4):1044–1081 (2023); SSRN 3900141.** 115 Nasdaq stocks, order-book at most granular level:
- Stationary OFI-derived inputs **beat raw LOB states** as features; fancy architectures add little over off-the-shelf networks once inputs are stationary.
- The alpha term structure peaks at an *intermediate* horizon and the **effective horizon of stock-specific forecasts ≈ 2 average price changes** — i.e., the information in order flow is exhausted after about two ticks' worth of price movement. "Information-rich" (actively quoted) names forecast better.

**Futures-specific: structural VAR on E-mini S&P 500 BBO data, 2008–2013, 1-second sampling (arXiv:2508.06788, 2025):**
- Impulse responses of returns to order-flow shocks **die out within ~1 second**; lag-1 return autocorrelation is *negative* in 95% of interval estimates (1-second reversal).
- Price impact per unit imbalance varies intraday by a factor of ~5 and scales with **inverse depth (elasticity ≈ 0.5)**; market-activity variables explain ~54% of the variation in the impact coefficient.
- Around scheduled macro announcements: depth falls, spreads widen, order-submission (flow volatility) *drops*, and the **price-impact coefficient rises before the release** — liquidity is withdrawn ahead of public information (direct DR-S09 link).

**Universality note:** Sirignano & Cont ("Universal features of price formation," Quantitative Finance 2019) show the order-flow → price-change mapping is largely universal and stationary across assets, which supports transferring equity-calibrated functional forms to NQ — while transferring *none* of the tradability conclusions.

### 1.2 DR-S03 — Queue imbalance and the micro-price

**Anchor: Avellaneda, Reed & Stoikov, "Forecasting Prices from Level-I Quotes in the Presence of Hidden Liquidity," Algorithmic Finance 1(1) (2011); SSRN 1691401.** Diffusion model for the two BBO queues gives P(next move up | bid size, ask size), with hidden/iceberg liquidity acting as a *damping* parameter: the more hidden size, the flatter the imbalance→probability curve. Used to rank venues by quote informativeness and to estimate hidden liquidity. Requires **L3**.

**Anchor: Lipton, Pesavento & Sotiropoulos, "Trade arrival dynamics and quote imbalance in a limit order book," arXiv:1312.0514 (2013).**
- Closed form: `P_up(x,y) = ½·[1 − arctan(√((1+ρ)/(1−ρ))·(y−x)/(y+x)) / arctan(√((1+ρ)/(1−ρ)))]` for bid queue x, ask queue y, queue correlation ρ (typically slightly negative).
- Calibrated on VOD.L (2012Q1): expected next move conditional on a highly imbalanced book is **up to ~⅓ of the spread**; highly imbalanced books also predict that a trade/price move arrives *sooner* (characteristic scale: seconds). The authors' own caveat: imbalance "does not by itself offer an opportunity for straightforward statistical arbitrage."

**Anchor: Gould & Bonart, "Queue Imbalance as a One-Tick-Ahead Price Predictor," Market Microstructure & Liquidity (2016); arXiv:1512.03492.** 10 Nasdaq stocks, logistic regression of next mid move on I = (b−a)/(b+a):
- **Large-tick stocks: P(up) ≈ 0.8–0.9 at I ≈ +1** (symmetric ≈ 0.1–0.2 at I ≈ −1); out-of-sample binary-classification improvement over the always-50% null: **50–60% for large-tick**, only **10–30% for small-tick** names; probabilistic-score improvement 20–30% vs 2–6%.
- Horizon is *event time*: "one tick ahead," i.e., until the next mid change — sub-second to seconds in liquid names. No cost/tradability analysis is offered.
- **NQ translation caution:** NQ is not a large-tick instrument in the ES/ZN sense — RTH spread is frequently >1 tick and best-level queues are thin (tens of contracts, vs thousands for ES). Expect the NQ imbalance→probability curve to sit between Gould–Bonart's large- and small-tick cases, i.e., meaningfully flatter than ES folklore suggests.

**Anchor: Stoikov, "The Micro-Price: A High Frequency Estimator of Future Prices," Quantitative Finance 18(12) (2018); SSRN 2970694.**
- Micro-price = mid + Σ g_i(imbalance, spread), constructed so the result is a **martingale** — the fair value conditional on book state. Adjustments converge in ~6 recursions and are **bounded by the half-spread**.
- Empirically (BAC = large-tick, CVX = small-tick) the micro-price beats both the mid and the size-weighted mid as a predictor of the mid a few price-changes ahead. The weighted mid *overshoots* for large-tick assets (imbalance is noisy when queues are long); the micro-price corrects this.
- Magnitude: the exploitable content is by construction **≤ ½ spread ≈ ≤ 1 NQ tick** — an execution-reference signal, not a standalone alpha.

**Queue-position economics: Moallemi & Yuan, "The Value of Queue Position in a Limit Order Book" (Columbia working paper, 2014-).** For large-tick assets, front-of-queue position is worth the **same order of magnitude as the half-spread**. This is why passive capture of imbalance signals is itself competitive: by the time an imbalance is visible, joining the favored queue puts you at the back, where fills arrive disproportionately when the queue is about to lose (adverse selection).

### 1.3 DR-S04 — CME Globex matching and data mechanics (NQ-specific facts)

Sources: CME Client Systems Wiki "Supported Matching Algorithms" / "Matching Algorithm Steps"; CME "Market by Order (MBO)" FAQ; Databento "CME matching algorithms explained"; Zotikov (Devexperts/dxFeed), "CME Iceberg Order Detection and Prediction," arXiv:1909.09495.

- **NQ (and ES, all CME equity-index futures) match strict FIFO (Algorithm F)** — price, then time priority; no pro-rata component, no LMM allocation. (FIFO covers ~70% of CME volume — Databento.) Pro-rata / threshold pro-rata / split algorithms exist on other complexes (STIRs, some Treasury products, many options) — irrelevant for NQ execution but a warning against importing queue intuitions across products.
- **FIFO implications:** queue position is earned only by arriving early at a price. Modifying an order's price, or increasing its size, re-timestamps it (new PriorityID → back of queue); decreasing size preserves priority. At 250 ms–2 s latency we will essentially **always join at the back of the visible queue**.
- **Icebergs / display quantity:** displayed quantity must meet the product minimum; on refresh the replenished clip keeps its OrderID (native iceberg) but receives a **new PriorityID — i.e., goes to the back of the queue** at its price. Refreshes never regain TOP status. Consequence: persistent refills at one price are *detectable* in MBO data as the same OrderID reappearing (Zotikov 2019 builds a detector on exactly this), and hidden size systematically flattens the informativeness of visible queue imbalance (Avellaneda–Reed–Stoikov's damping).
- **MBO vs MBP (MDP 3.0):** MBP disseminates **10 aggregated price levels** (total qty + order count per level). MBO (since 2017) disseminates **every resting order** with anonymous OrderID + PriorityID at all levels. CME trade summary messages carry the **aggressor side flag** — on modern CME data, signed trade flow is *exact*, no classification rule needed. Retail feeds differ in what they pass through: NinjaTrader real-time L1 marks trades at bid/ask (quote-rule equivalent); whether historical NT8 series retain BBO sizes is the open item in our data audit (probe run `runs/DATAPROBE01`).
- **Speed context: Aquilina, Budish & O'Neill, "Quantifying the High-Frequency Trading Arms Race," QJE 137(1) (2022).** Message-level evidence (LSE): latency races occur ~once per minute per liquid symbol, the **modal race lasts 5–10 microseconds**, races are ~20% of volume, the average prize is **~half a tick**, and the top 6 firms win >80% of races. Whatever book-state alpha exists at sub-100 ms is consumed by co-located firms **4–5 orders of magnitude faster than our 250 ms–2 s loop**. Latency arbitrage ≈ 0.5 bp tax ≈ ⅓ of effective spread.

### 1.4 DR-S09 — Volatility bursts and liquidity withdrawal

- **Farmer, Gillemot, Lillo, Mike & Sen, "What really causes large price changes?" Quantitative Finance 4 (2004).** Large price moves are caused by **gaps in the book**, not by large trade volumes: the size of the price change from a market order is essentially independent of its volume and is instead the gap to the next occupied level. Large moves are *liquidity events*. Minimum data to see the mechanism: L4; to see the symptom (spread widening, quote flicker): L2/L3.
- **Kirilenko, Kyle, Samadi & Tuzun, "The Flash Crash," J. Finance 72(3) (2017)** and the **CFTC–SEC joint report (2010)** — E-mini evidence: HFT inventories stayed <3,000 contracts with a ~2-minute half-life and they demanded immediacy during the crash rather than absorbing it; between 2:35–2:46 pm buy-side depth fell to ~25% and sell-side to ~15% of midday levels, and by 2:45:28 resting buy depth was <1,050 contracts — **<1% of the morning level**. Depth evaporates *nonlinearly* and *fast*; a depth-based risk trigger must react in seconds-to-minutes, which is within our latency budget.
- **Marcaccioli, Bouchaud & Benzaquen, "Exogenous and Endogenous Price Jumps Belong to Different Dynamical Classes," JSTAT (2022); arXiv:2106.07040.** With news-synchronized order-book data on 300 stocks: **exogenous (news) jumps arrive abruptly and relax by a fast power law; endogenous jumps show an accelerating volatility *foreshock* and a slower power-law relaxation**. The two classes are separable from price/volatility data alone — no news feed needed. Practical reading: no-news spikes mean-revert more; scheduled-news moves continue/settle at the new level.
- **arXiv:2508.06788 (ES, above):** liquidity is withdrawn *ahead of* scheduled announcements (depth ↓, spread ↑, submissions ↓, impact coefficient ↑) — the burst is partially predictable in the clock, and its amplification is a state of the *book*, not of the news.
- **Nagel, "Evaporating Liquidity," RFS 25(7) (2012).** Returns to liquidity provision (short-horizon reversal strategies) rise sharply with VIX: liquidity withdrawal in stress is systematic and *compensated* — fading endogenous dislocations is a risk premium, not a free lunch.

---

## 2. Honest transfer assessment: what survives at 250 ms–2 s on CME index futures

**The core arithmetic.** The monetizable content of best-level book-state signals (queue imbalance, micro-price, best-level OFI) is bounded by roughly the half-spread to ⅓ of the spread per event (Stoikov; Lipton et al.), with an effective horizon of ~1–2 price changes (Kolm et al.) — on NQ that is **≤ ~1 tick of edge with a sub-second-to-seconds half-life**. Our market-order round trip costs **2.872 ticks**. Aggressively harvesting top-of-book signals is therefore **structurally unprofitable for us by ~2+ ticks per round trip, before latency decay** — and at 250 ms–2 s we additionally land on the wrong side of the documented 1-second reversal in index futures (arXiv:2508.06788): chasing flow at our speed systematically buys the top of micro-impulses. The microsecond arms-race evidence (Budish et al.) says the residual left for anyone slower than ~10 μs in these races is approximately zero.

**What is genuinely dead for us (declare and move on):**
1. Directional scalping of queue imbalance / micro-price / best-level OFI with marketable orders at horizons < 1 min. Cost floor 2.872 ticks vs ≤ 1 tick of signal.
2. Latency-sensitive passive capture (posting to capture the imbalance-favored side): FIFO puts us at the back of the queue, where Moallemi–Yuan queue-value logic and adverse selection eat the theoretical edge.
3. Anything requiring reaction inside ~100 ms (iceberg-refill sniping, race participation, spoof-following).

**What plausibly survives (three channels):**
- **Channel A — Execution overlay (cost reduction, not alpha).** For trades our slower strategies were going to do anyway, book state can decide *when* and *how* to execute: enter passively when micro-price is on our side of mid, cross the spread only when imbalance is against us, delay marketable entries ~1–3 s after a same-direction flow burst (reversal). Literature magnitudes (⅓ spread per event; micro-price ≤ ½ spread) imply plausible savings of **0.2–0.7 ticks per execution** — equivalently, cutting C1 by 7–25%. This compounds across every trade of every strategy and is the *highest-value* use of book data for us.
- **Channel B — Volatility/fragility state detection (risk filter, not direction).** Depth thinning + spread widening + submission drying up predict *amplified impact* and burst risk at 1–10 min horizons (Farmer gaps; ES pre-announcement withdrawal; flash-crash depth decay). Detecting a fragile book needs only seconds-scale reaction — comfortably inside our latency. Use: stand aside, halve size, or widen stops for scalp entries when the book is fragile. This monetizes as *avoided* cost, which is not spread-bounded.
- **Channel C — Minutes-horizon flow features (weak conditioning signal).** Aggregated signed flow over 1–30 min windows carries small but real forward information (predictive R² ~ low single-digit % in the equity literature; decays within minutes). At NQ's minutes-scale volatility (~10–40 ticks), even 1% R² can shift conditional means by more than C1 in high-volatility states. This is ensemble-member material — consistent with the campaign finding that ensembles beat parameter selection — never a standalone strategy.
- **Channel C′ — Event-scale mean reversion of endogenous spikes.** NQ air-pocket moves are 20–100+ ticks; the Marcaccioli et al. class separation says no-news spikes revert more. Magnitude clears the 2.872-tick floor by an order of magnitude; the open questions are hit rate and tail risk (Nagel: this is compensated risk, expect occasional large losses).

**One-line verdict:** at our latency the order book is a *cost model and a risk sensor*, not an alpha source; flow becomes alpha-relevant only when aggregated to minutes and combined with volatility state.

---

## 3. L1-proxy assessment: what is recoverable from last-trade data alone

**Decomposition benchmark (CKS 2014):** trade-only imbalance explains **R² ≈ 32%** of short-horizon price variation vs **≈ 65%** for full best-level OFI — i.e., **signed trade flow alone recovers roughly half of the contemporaneous explanatory power** of the best-level order-flow signal. The missing half is limit-order placement/cancellation dynamics, which are invisible at L1 by definition. Queue imbalance and micro-price are **0% recoverable at L1** (they are pure book-state quantities).

**Signing trades without an aggressor flag:**
- Tick rule (uptick = buy): ~77.7% per-trade accuracy on Nasdaq equities (Ellis–Michaely–O'Hara 2000); Lee–Ready (quote rule + tick tie-break): ~85% (Lee & Ready 1991), 81% (EMO).
- **Futures-specific ground truth:** using CME's true aggressor flags, tick-based rules classify **~90–91% of E-mini volume** correctly and Lee–Ready ~92.6%, while Easley–López de Prado–O'Hara bulk volume classification (BVC) is *worse* (~79.7%) — Chakrabarty, Pascual & Shkilko, J. Financial Markets (2015); Andersen & Bondarenko's perfect-classification VPIN critique (2015) reaches the same ranking on ES and shows VPIN's volatility "prediction" is largely BVC misclassification artifact. **Do not adopt BVC/VPIN as an L1 toxicity metric.**
- Attenuation math: signing accuracy a shrinks a flow signal's correlation by factor (2a−1): 0.82 at a=91%, 0.70 at a=85%. Classification noise is a *modest* haircut, not a blocker — the binding constraint is the missing cancel/placement half of OFI, not signing error.
- Practical note: CME MDP3 disseminates the aggressor side; NinjaTrader real-time tags trades at bid/ask, and NT8 **Tick Replay** exposes the prevailing bid/ask price at each historical trade (quote-rule signing, no tie-break needed except mid-trades). If the audit confirms Tick Replay bid/ask on our historical NQ tick data, we effectively have **L1+L2 historically**, upgrading signing accuracy to ~quote-rule levels and adding spread + BBO-price-change events (queue *depletion* events are partially inferable: a bid price downtick = bid queue emptied — a coarse, signed, cancel-inclusive event usable as a "poor-man's OFI" term).
- **L3/L4 (BBO sizes, depth) are almost certainly not reconstructable historically in NT8**; they exist only in live recordings (Market Replay) or external data (Databento MBP-10/MBO, CME DataMine). If any Section-4 hypothesis at L3+ survives triage, the cheap unblock is to **start a live L3 recorder now** so that a dataset exists in 3–6 months, and/or buy a bounded MBP-10 sample for validation.

**Bottom line by data level:** L1 alone ≈ half the flow information with a ~0.8 attenuation on top → roughly **40% of best-level OFI content**; L1+L2 (Tick Replay) ≈ 55–70% including depletion events, spread state, and quote volatility; L3 unlocks imbalance/micro-price (execution overlay); L4 adds ~19 R² points of contemporaneous impact fit (Cont–Cucuringu–Zhang) plus iceberg/absorption detection — a luxury, not a necessity, for our latency class.

---

## 4. Testable hypotheses

Numbering continues the scalping-lab DR-B series. Costs: all PnL statements are net of C1 = $14.36 RT unless stated. "Markout(h)" = signed mid-price move h after fill/event.

### H-B1. Signed-flow burst reversal penalty (the anti-chase rule)
At 250 ms–2 s latency, marketable NQ entries placed immediately after a same-direction signed-flow burst suffer a systematically worse effective price than entries delayed 1–3 s, because index-futures micro-impulses reverse within ~1 s (arXiv:2508.06788; CKS impact + Kolm ~2-price-change horizon).
- **ECONOMIC MECHANISM:** transient (mechanical) component of price impact rebounds after the burst; slow traders who chase pay the transient component twice.
- **OBSERVABLE VARIABLES:** 250 ms–1 s signed trade volume (tick/quote-rule), trade intensity; entry markouts at +1 s, +5 s, +30 s conditioned on pre-entry burst sign.
- **EXPECTED HORIZON:** 0.5–5 s (reversal window).
- **EXPECTED SIGN:** entries *with* the burst have negative short-horizon markout vs entries *against* or *delayed*; expected difference 0.3–1.0 tick.
- **REQUIRED DATA:** L1 (better with L2 Tick Replay signing).
- **RETAIL EXECUTABILITY:** high — it is a *timing rule* applied to trades we already take; no new latency demands.
- **SIMPLE NULL:** markout after entry is independent of pre-entry 1 s signed-flow state (test vs shuffled burst labels).
- **FALSIFICATION EXPERIMENT:** on historical NQ tick data, simulate entries triggered by an existing scalp signal, executed (a) instantly, (b) delayed 1 s, (c) delayed until flow-neutral; compare cost per trade with block bootstrap CIs; kill if delay saves <0.15 tick or hurts fill rate enough to offset.
- **PRIORITY:** 1

### H-B2. Aggregated signed-flow imbalance as a minutes-horizon conditioning feature
Cumulative signed trade volume (normalized by rolling volume) over 5–30 min windows predicts the sign of the next 5–30 min NQ return with small but exploitable conditional mean shift in high-volatility states (Channel C; CKS trade-imbalance R² 32% contemporaneous, single-digit % predictive per Cont–Cucuringu–Zhang decay pattern).
- **ECONOMIC MECHANISM:** slow propagation of institutional metaorder flow (order splitting) creates autocorrelated flow whose impact is not fully instantaneous.
- **OBSERVABLE VARIABLES:** tick-rule/quote-rule signed volume aggregates; realized volatility; forward 5/15/30-min returns.
- **EXPECTED HORIZON:** 5–30 min, decaying toward zero by ~1 h.
- **EXPECTED SIGN:** positive (flow continuation) — but expected to *flip to reversal at extreme quantiles* (exhaustion); test both.
- **REQUIRED DATA:** L1. **L1 proxy quality:** ~40% of full-OFI content — acceptable at these horizons.
- **RETAIL EXECUTABILITY:** high — minutes-scale rebalancing, limit or market entry; conditional move must exceed 2.872 ticks, plausible only when 30-min vol > ~20 ticks.
- **SIMPLE NULL:** forward return ⊥ lagged flow imbalance (predictive R² ≤ 0 OOS; conditional means within bootstrap bands of unconditional).
- **FALSIFICATION EXPERIMENT:** decile analysis of forward return vs lagged normalized flow, split by volatility tercile, 2023–2025 in-sample only with locked-forward validation per campaign constitution; kill if top-vs-bottom decile spread < C1 in every vol state or unstable across years.
- **PRIORITY:** 1

### H-B3. Book-fragility state predicts burst risk (risk filter, direction-free)
A fragility index built from spread widening, BBO flicker rate, and (if L3 available) depth depletion predicts elevated |return| and worse scalp outcomes over the next 1–10 min (Farmer gaps; ES pre-announcement withdrawal; flash-crash depth decay).
- **ECONOMIC MECHANISM:** thin/gappy books amplify a given flow into larger price moves (impact ∝ 1/depth, elasticity ~0.5–1); market makers withdraw before uncertainty, so fragility is observable *before* the burst.
- **OBSERVABLE VARIABLES:** L2: spread level/changes, quote-update intensity, mid volatility; L3: best-level sizes, depth depletion rate; scheduled-news clock as covariate.
- **EXPECTED HORIZON:** 1–10 min.
- **EXPECTED SIGN:** fragility ↑ ⇒ |Δp| ↑ (no directional claim); scalp PnL conditional on fragility ↓.
- **REQUIRED DATA:** L2 minimum (spread/flicker); L3 preferred. L1-only proxy: trade intensity + range acceleration (weaker; see H-B5).
- **RETAIL EXECUTABILITY:** high — filter/size governor with seconds-scale reaction time; no fast execution needed.
- **SIMPLE NULL:** forward |return| ⊥ fragility index after controlling for time-of-day and trailing volatility.
- **FALSIFICATION EXPERIMENT:** regress forward 5-min |return| on fragility index + controls; then A/B an existing scalp strategy with/without the fragility veto; kill if the veto does not improve net expectancy or reduce tail losses out-of-sample.
- **PRIORITY:** 1

### H-B4. Micro-price/queue-imbalance execution overlay (cost reduction)
For entries generated by a slower signal, posting on the imbalance-favored side when the micro-price is beyond mid toward our direction — and crossing only when imbalance is adverse — reduces effective entry cost by 0.2–0.7 ticks per execution vs always-market (Stoikov micro-price ≤ ½ spread; Lipton ⅓-spread conditional move; Gould–Bonart directional skew).
- **ECONOMIC MECHANISM:** book state predicts the *next* mid move; being passive when the move is toward us converts predicted drift into spread capture instead of spread payment; FIFO back-of-queue position is acceptable because we only need fills when flow comes *toward* us.
- **OBSERVABLE VARIABLES:** BBO sizes (imbalance, micro-price), fill markouts at 1 s/5 s, fill ratio, opportunity cost of unfilled entries.
- **EXPECTED HORIZON:** signal half-life sub-second to ~5 s; applied at each execution.
- **EXPECTED SIGN:** effective cost ↓; adverse-selection markout of passive fills less negative when imbalance-favored.
- **REQUIRED DATA:** L3 (live going forward; historical L3 likely unavailable in NT8 — start recorder / consider MBP-10 sample). Not L1-proxyable.
- **RETAIL EXECUTABILITY:** medium — needs live L3 and order management at ~1 s granularity (NT8 capable); main risk is unfilled-entry opportunity cost in trending bursts.
- **SIMPLE NULL:** entry cost and fill markouts are independent of book state at decision time (overlay saves 0 net of missed fills).
- **FALSIFICATION EXPERIMENT:** live-sim (Market Replay) A/B on the same signal stream: always-market vs overlay; metric = all-in cost per completed round trip including penalized missed entries; kill if net saving < 0.15 tick/RT.
- **PRIORITY:** 2

### H-B5. Endogenous vs exogenous spike classification and conditional fade
NQ spikes ≥ N ticks (N ≈ 20–40) with *accelerating* volatility foreshock and no scheduled news (endogenous class) mean-revert over 2–30 min materially more than spikes on scheduled releases (exogenous), per Marcaccioli–Bouchaud–Benzaquen dynamical classes.
- **ECONOMIC MECHANISM:** endogenous spikes are self-excited liquidity vacuums (Farmer gaps) with no information content; price relaxes as liquidity refills. News moves reprice fundamentals and do not refill.
- **OBSERVABLE VARIABLES:** 1 s–1 min bars: spike magnitude, pre-spike volatility growth curvature, scheduled-news calendar flag; forward 2/10/30-min retracement fraction.
- **EXPECTED HORIZON:** 2–30 min.
- **EXPECTED SIGN:** endogenous class retraces more (target: ≥ 30% median retracement of spike vs materially less for news class).
- **REQUIRED DATA:** L1 + news calendar (fully L1-viable; L2 spread confirms the vacuum).
- **RETAIL EXECUTABILITY:** high on magnitude (spikes 20–100 ticks ≫ 2.872-tick floor), but tail-risk heavy (Nagel: compensated risk); execution via resting limits into the spike, seconds latency fine.
- **SIMPLE NULL:** retracement distribution is identical across classes and no better than unconditional post-spike behavior.
- **FALSIFICATION EXPERIMENT:** classify all ≥N-tick 2023–2025 NQ spikes by foreshock shape + calendar; compare retracement distributions (KS test, bootstrap); then backtest a limit-fade with fixed disaster stop; kill if class separation is absent or net expectancy of fade ≤ 0 with stop included.
- **PRIORITY:** 1

### H-B6. Impact-state dependence: flow signals only pay in thin books
The conditional forward-return response to flow imbalance (H-B2) is amplified in low-depth/high-fragility states (impact ∝ 1/depth; ES intraday impact varies ×5), concentrating any tradable flow edge in specific sessions (Globex overnight, lunch, pre-news).
- **ECONOMIC MECHANISM:** same flow moves price further when the book is thin; if flow autocorrelates, expected continuation scales with the impact state.
- **OBSERVABLE VARIABLES:** flow imbalance (L1), fragility/depth state (L2/L3), time-of-day; interaction term in forward-return regression.
- **EXPECTED HORIZON:** 5–30 min.
- **EXPECTED SIGN:** positive interaction (flow × thinness → forward return); flow edge ≈ 0 in thick RTH books.
- **REQUIRED DATA:** L1 + L2 (spread as thinness proxy); L3 sharpens.
- **RETAIL EXECUTABILITY:** medium-high — implies *session selection*, which is free; overnight spreads of 1–2+ ticks raise effective cost, must net against C1.
- **SIMPLE NULL:** interaction coefficient = 0 (flow effect homogeneous across book states).
- **FALSIFICATION EXPERIMENT:** H-B2 decile analysis re-run within spread/depth terciles; kill if the edge does not concentrate (or concentrates only where spread cost erases it).
- **PRIORITY:** 2

### H-B7. Quote-depletion events as a poor-man's OFI (L2 upgrade test)
Adding BBO price-change events (bid downtick = bid-side depletion; ask uptick = ask replenishment failure) to signed trade flow recovers a materially larger share of the CKS OFI information than trades alone (target: close the 32%→65% R² gap by half) on NQ.
- **ECONOMIC MECHANISM:** best-level cancels/placements are half of OFI; BBO *price* transitions are the visible footprint of queue depletion/replenishment even without sizes.
- **OBSERVABLE VARIABLES:** Tick Replay bid/ask price series; counts of signed BBO transitions per window; contemporaneous + forward 10 s–5 min returns.
- **EXPECTED HORIZON:** contemporaneous fit at 10 s–1 min; forward test at 1–5 min.
- **EXPECTED SIGN:** depletion-augmented flow explains more contemporaneous variance than trades alone; any forward increment is small but should not be negative.
- **REQUIRED DATA:** L2 (pending audit — this hypothesis doubles as the audit's payoff test).
- **RETAIL EXECUTABILITY:** n/a directly (feature engineering); feeds H-B2/H-B3/H-B6.
- **SIMPLE NULL:** depletion counts add no R² over signed trade volume (ΔR² ≈ 0).
- **FALSIFICATION EXPERIMENT:** nested regression comparison (trades-only vs trades+depletion) on 2023–2025 NQ, OOS by year; kill the L2 feature program if ΔR² < 5 points contemporaneous.
- **PRIORITY:** 2

### H-B8. Iceberg/absorption at a level predicts stall-and-reverse (aspirational, external data)
Repeated same-price refills absorbing aggressive flow (MBO OrderID reappearance, or L4 depth replenishment after trades) mark informed passive interest; price stalls and reverses off absorbed levels more often than off ordinary levels (Zotikov 2019 detectability; Moallemi–Yuan queue-value logic implies only confident traders keep refilling).
- **ECONOMIC MECHANISM:** an agent repeatedly refreshing hidden size at one price is providing liquidity against the trend with conviction; their inventory absorbs the aggressor flow that would otherwise gap the book.
- **OBSERVABLE VARIABLES:** MBO refills / MBP-10 level-quantity replenishment vs trade volume at level; forward 1–10 min return relative to the level.
- **EXPECTED HORIZON:** 1–10 min after absorption episode.
- **EXPECTED SIGN:** reversal away from the absorbed level (bounce off absorbed bid).
- **REQUIRED DATA:** **L4 (MBO ideal, MBP-10 partial)** — not available in NT8 historicals; requires Databento/DataMine purchase or long live recording. No L1/L2 proxy exists.
- **RETAIL EXECUTABILITY:** medium — minutes horizon and multi-tick targets clear C1, but data cost/engineering is the real price.
- **SIMPLE NULL:** post-episode return distribution identical to matched non-absorption levels (same trend/vol state).
- **FALSIFICATION EXPERIMENT:** on a purchased 3–6 month NQ MBP-10/MBO sample, event-study absorbed vs matched control levels; kill if reversal excess < 4 ticks median or hit-rate lift < 5 points.
- **PRIORITY:** 3

---

## 5. Data-level bottleneck summary (input to the NT8 audit)

| Use | Min level | Status |
|---|---|---|
| Signed trade flow (tick rule ~90% accurate on CME) | L1 | Have historically |
| Quote-rule signing, spread state, depletion events (H-B1/2/3/5/6/7) | L2 | **Pivot of audit — Tick Replay bid/ask** |
| Queue imbalance, micro-price, execution overlay (H-B4) | L3 | Live-only in NT8; start recorder now |
| Multi-level OFI, iceberg/absorption (H-B8) | L4 | External data purchase only |

The practical bottleneck is **L2 historical (bid/ask at trade)**: it upgrades ~40% of best-level OFI content to ~55–70%, enables the three Priority-1 hypotheses in full, and costs nothing if the audit confirms Tick Replay. L3 is the second bottleneck and is solvable prospectively (live recording) rather than retrospectively.

---

## 6. Sources

- Cont, Kukanov & Stoikov (2014), *The Price Impact of Order Book Events*, J. Fin. Econometrics 12(1). arXiv:1011.6402. https://arxiv.org/abs/1011.6402
- Cont, Cucuringu & Zhang (2023), *Cross-Impact of Order Flow Imbalance in Equity Markets*, Quant. Finance. arXiv:2112.13213. https://arxiv.org/abs/2112.13213
- Kolm, Turiel & Westray (2023), *Deep Order Flow Imbalance*, Math. Finance 33(4):1044–1081. SSRN 3900141.
- Stoikov (2018), *The Micro-Price*, Quant. Finance 18(12). SSRN 2970694. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2970694
- Avellaneda, Reed & Stoikov (2011), *Forecasting Prices from Level-I Quotes in the Presence of Hidden Liquidity*, Algorithmic Finance 1(1). SSRN 1691401.
- Lipton, Pesavento & Sotiropoulos (2013), *Trade arrival dynamics and quote imbalance in a limit order book*. arXiv:1312.0514. https://arxiv.org/abs/1312.0514
- Gould & Bonart (2016), *Queue Imbalance as a One-Tick-Ahead Price Predictor*, Mkt. Microstructure & Liquidity. arXiv:1512.03492. https://arxiv.org/abs/1512.03492
- Briola, Bartolucci & Aste (2024), *Deep Limit Order Book Forecasting*. arXiv:2403.09267. https://arxiv.org/abs/2403.09267
- Sirignano & Cont (2019), *Universal features of price formation in financial markets*, Quant. Finance 19(9).
- Anonymous (2025), *Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News* (ES structural VAR). arXiv:2508.06788. https://arxiv.org/abs/2508.06788
- Aquilina, Budish & O'Neill (2022), *Quantifying the High-Frequency Trading "Arms Race"*, QJE 137(1). https://academic.oup.com/qje/article/137/1/493/6368348
- Moallemi & Yuan (2014+), *The Value of Queue Position in a Limit Order Book*, Columbia working paper.
- Farmer, Gillemot, Lillo, Mike & Sen (2004), *What really causes large price changes?*, Quant. Finance 4. arXiv:cond-mat/0312703.
- Kirilenko, Kyle, Samadi & Tuzun (2017), *The Flash Crash*, J. Finance 72(3).
- CFTC–SEC (2010), *Findings Regarding the Market Events of May 6, 2010*. https://www.sec.gov/news/studies/2010/marketevents-report.pdf
- Marcaccioli, Bouchaud & Benzaquen (2022), *Exogenous and Endogenous Price Jumps Belong to Different Dynamical Classes*, JSTAT. arXiv:2106.07040.
- Nagel (2012), *Evaporating Liquidity*, RFS 25(7).
- Lee & Ready (1991), *Inferring Trade Direction from Intraday Data*, J. Finance 46(2). Ellis, Michaely & O'Hara (2000), JFQA 35(4).
- Chakrabarty, Pascual & Shkilko (2015), *Evaluating trade classification algorithms: BVC vs tick rule and Lee–Ready*, J. Fin. Markets. Andersen & Bondarenko (2015), *Assessing VPIN via perfect trade classification*, J. Fin. Markets. Easley, López de Prado & O'Hara (2016), *Discerning information from trade data*, JFE.
- CME Group Client Systems Wiki: *Supported Matching Algorithms*; *Matching Algorithm Steps*; *MDP 3.0 MBP/MBO documentation*; *Market by Order FAQ*. https://cmegroupclientsite.atlassian.net/wiki/display/EPICSANDBOX/Supported+Matching+Algorithms
- Databento (2023), *CME matching algorithms explained*. https://databento.com/blog/cme-matching-algorithms-explained
- Zotikov (2019), *CME Iceberg Order Detection and Prediction*. arXiv:1909.09495.
