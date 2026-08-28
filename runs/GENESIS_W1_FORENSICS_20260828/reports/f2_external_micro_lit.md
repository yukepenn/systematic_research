# F2 — External literature: microstructure, order flow, volatility surface (PROJECT GENESIS)

Date: 2026-08-28. Author: TEAM F2 (external-research subagent).
Session constraint disclosed up front: the shared WebSearch budget was already exhausted (200/200)
when this task started (RAW FACT — tool refusal observed this session). All external evidence below
was gathered via WebFetch on arXiv abstracts and the OpenAlex API (raw JSON responses saved in this
scratchpad: `oa_results.txt`, `oa_results2.txt`), plus a small number of direct page fetches.

## Evidence-tag legend (used on every claim)

- **VERIFIED-ABSTRACT** — I fetched the paper's abstract/metadata this session and the claim is in it
  (raw fact about what the source says; not a replication).
- **MODEL KNOWLEDGE** — quantitative detail from my training (paper widely known), NOT re-verified
  this session. Treat as a pointer to check before preregistering anything on it.
- **RECORDED CLAIM (repo)** — a repo document says it; cited as file:line.
- Nothing in this report is a claim that any effect exists in THIS project's data.

---

## 1. Order-flow imbalance (OFI): how far ahead does it predict?

**Canonical citation.** Cont, Kukanov, Stoikov, "The Price Impact of Order Book Events," *Journal of
Financial Econometrics* 2013, doi:10.1093/jjfinec/nbt003, 300 cites (VERIFIED-ABSTRACT via OpenAlex).
Abstract states: over short intervals price changes are **mainly driven by OFI defined at the best bid
and ask only**; the relation is **linear with slope inversely proportional to market depth**; robust to
intraday seasonality, "stable across time scales and across stocks"; the volume–price "square-root"
relation is noisier and derivative of OFI (VERIFIED-ABSTRACT). Note carefully: this is a
**contemporaneous** explanatory result, not a forecast — the arXiv page (1011.6402) framing likewise
says price changes "are mainly driven by" OFI (VERIFIED-ABSTRACT).
MODEL KNOWLEDGE: their windows are ~10-second aggregates on 50 NYSE stocks, R² of the
contemporaneous regression is high (order 65–70% average); no tradeable forecast is claimed.

**Predictive (not contemporaneous) OFI.** Cont, Cucuringu, Zhang, "Cross-Impact of Order Flow
Imbalance in Equity Markets" (arXiv 2112.13213, published Quant. Finance 2023)
(VERIFIED-ABSTRACT): an **integrated multi-level OFI** (combining deeper book levels) explains
contemporaneous impact better than best-level OFI; cross-asset terms add nothing contemporaneously;
**lagged (cross-)OFI does add forward-looking predictive power but "mainly manifests at short-term
horizons and decays rapidly in time."** Abstract does not quantify horizons or costs
(VERIFIED-ABSTRACT). MODEL KNOWLEDGE: their forward-looking R² is one to two orders of
magnitude below the contemporaneous R² (single-digit % and below at minute scale), and the paper's
own cost discussion does not establish net profitability.

**Supporting evidence on the horizon question.**
- Takahashi, "Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects"
  (arXiv 2508.06788): 1-second VAR; **shocks "dissipate almost entirely within a second"**
  (VERIFIED-ABSTRACT via arXiv API listing). This is the cleanest recent statement that plain
  return↔OFI dynamics at high frequency are nearly memoryless beyond seconds.
- Xu et al., "Multi-Level Order-Flow Imbalance in a Limit Order Book" (arXiv 1907.06230):
  out-of-sample fit **improves with each additional price level** in the MLOFI vector
  (VERIFIED-ABSTRACT).
- Hu/Chen, CSI 300 index futures OFI (arXiv 2505.17388): regime-dependent memory,
  horizon-dependent forecast power in an index-futures book (VERIFIED-ABSTRACT).
- Cartea, Donnelly, Jaimungal, *Applied Mathematical Finance* 2018 (VERIFIED-ABSTRACT): L1
  **volume imbalance predicts the sign of the NEXT market order** and the price change immediately
  after it; used to boost a market-making strategy — i.e., the edge monetizes at the
  next-event/seconds horizon, inside the spread.
- Gould & Bonart, "Queue imbalance as a one-tick-ahead price predictor" (arXiv 1512.03492)
  (VERIFIED-ABSTRACT): L1 queue imbalance predicts direction of the **next mid-price move**;
  effect **strongest for large-tick assets** (ES/NQ are large-tick futures). One-tick-ahead only.
- Sirignano & Cont (arXiv 1803.06917) (VERIFIED-ABSTRACT): a **universal, stationary** price-formation
  map from order-flow history to next-move direction exists across assets; **history over many past
  observations beats a book snapshot**. Direction-of-next-move target; no net-of-cost claim.

**Bottom line (F2 synthesis).** The literature's consistent answer: OFI is a superb *explainer* at
seconds-scale, a *statistically* significant predictor at next-tick-to-a-few-minutes, and its
predictive component decays within seconds-to-minutes. Every monetization demonstrated in print is a
market-making/execution overlay (capture inside the spread), not a taker strategy.

**Data requirement.** Best-level OFI: **L1 BBO with sizes** (event-stamped). Multi-level/integrated
OFI: **MBP-10**. None of the canonical results need MBO. (Tag: synthesis of the above
VERIFIED-ABSTRACT items.)

**Retail implementability at 1-contract NQ.** Costs from repo: $4.36/ctRT commission + P1 modelled
spread $14.44/ctRT (RECORDED CLAIM — CLAUDE.md §6). ≈$18.80 round turn ≈ **3.8 NQ ticks**. A signal
whose payoff is a fraction of one tick over seconds cannot cross that bar as a taker, and capturing
it as a maker requires queue economics (below) that retail latency does not have. As a *conditioner*
(e.g., minute-bar signed-flow regime input to a slower system), implementable.

**Decay evidence.** Cross-impact/lagged-OFI alphas are the classic HFT crowded trade; the published
predictive R²s are small and post-2017 samples show no free lunch surviving costs (MODEL
KNOWLEDGE). No published claim of a persistent taker-implementable OFI edge was found.

---

## 2. Depth / book-slope information content

- Kalev & Duong, "Order Book Slope and Price Volatility" (SSRN 2007, doi:10.2139/ssrn.1009549)
  (VERIFIED existence/metadata): book slope relates negatively to subsequent volatility. MODEL
  KNOWLEDGE: the slope→volatility family (Næs & Skjeltorp 2006 JFM is the standard cite) finds
  flatter/thinner books → higher volatility; explanatory horizon daily/intraday, modest R².
- Kang, Kwon, Kim, *J. Futures Markets* 2019, KOSPI 200 futures (VERIFIED-ABSTRACT): VPIN-style flow
  toxicity predicts short-term volatility; HFT participation is negatively related to toxicity in
  normal times, positively in stress — depth/participation composition matters by regime.
- Flash-crash evidence: depth withdrawal precedes/accompanies liquidity events (Kirilenko, Kyle,
  Samadi, Tuzun, *JF* 2017 — MODEL KNOWLEDGE; supported by Braun et al. 2018 PLoS ONE
  (VERIFIED-ABSTRACT): ≥60% of mini flash crashes are triggered by a **single large market order**,
  <40% fully recover — i.e., displayed depth is informative about fragility, but the trigger is flow).
- Easley, López de Prado, O'Hara, *RFS* 2012 (VPIN) (VERIFIED-ABSTRACT) vs. **Andersen & Bondarenko
  2013** (VERIFIED-ABSTRACT, RePEc): when VPIN is built from *accurate* classification it behaves
  **diametrically opposite** to BVC-VPIN, and BVC-VPIN's volatility forecast power comes from
  **systematic classification errors correlated with volume/volatility**; controlling for trading
  intensity and volatility, **no incremental predictive power**. The VPIN dispute (Easley et al.
  rejoinder 2013; Andersen & Bondarenko "Reflecting on the VPIN Dispute" 2013; LBL "big data" test
  2013 reporting 7% false-positive rates under tuned parameters) is all VERIFIED-metadata.

**Verdict.** Depth-as-regime-indicator is real but mostly a *volatility* forecaster, i.e., a risk
conditioner, not directional alpha. VPIN specifically is **discredited as an information measure** by
the best-identified study (ES futures with near-perfect classification). Data requirement: L1 sizes
(large-tick futures concentrate information at the top of book — Gould-Bonart VERIFIED-ABSTRACT);
MBP-10 only for slope-across-levels variants. Retail: usable as a filter; horizon minutes-to-daily.

---

## 3. Trade classification in futures (no NBBO)

- **The decisive fact for this project:** CME futures need no Lee-Ready analogue at all if the feed
  carries aggressor side. Andersen & Bondarenko built **(near) perfect classification from CME BBO
  files** for ES and report the **plain tick rule applied to individual transactions is superior to
  BVC** (VERIFIED-ABSTRACT). MODEL KNOWLEDGE: CME MDP 3.0 trade messages carry an explicit
  aggressor-side field (Databento `trades` schema exposes it as `side`), so bought depth data
  would come pre-classified; and tick-rule accuracy on ES-type books is ≈95%+ at the transaction
  level when quotes are available.
- Chakrabarty, Pascual, Shkilko, *JFM* 2015 (VERIFIED-metadata; MODEL KNOWLEDGE for numbers):
  trade-level BVC accuracy is materially below tick rule / Lee-Ready in equities too; BVC's appeal
  is only computational.
- Hasbrouck *JFQA* 2004 (VERIFIED-ABSTRACT): the pre-electronic problem (pit data without quotes)
  was solved with Bayesian/MCMC inference — historical interest only.

**Verdict.** For NT8-exported NQ tick+BBO the quote rule (trade at ask = buy) plus tick-rule
fallback is the literature-endorsed method; expected accuracy is high in a large-tick book (MODEL
KNOWLEDGE, anchored on Andersen-Bondarenko VERIFIED-ABSTRACT). **BVC on 1-min bars is explicitly the
method the best futures study rejects** — do not build a signed-flow research lane on BVC.

---

## 4. Queue position / passive liquidity provision economics at retail scale

- Moallemi & Yuan, "A Model for Queue Position Valuation in a Limit Order Book" (SSRN 2996221, 2016)
  (VERIFIED-metadata; MODEL KNOWLEDGE: in large-tick names queue position is worth a meaningful
  fraction of the half-spread; front-of-queue fills earn, back-of-queue fills are adversely selected).
- Donnelly & Gan, *Applied Math. Finance* 2018 (VERIFIED-ABSTRACT): accounting for queue position in
  an optimal LO strategy yields **+2.5% mean at equal risk (or −8.8% std at equal mean)** vs.
  position-blind — the marginal value of queue awareness is real but single-digit percent for an
  optimized professional strategy.
- Budish, Cramton, Shim, *QJE* 2015 (VERIFIED-ABSTRACT): continuous-time serial processing gives
  fast traders mechanical sniping rents against resting orders — the structural reason a
  retail-latency resting order in ES/NQ is systematically picked off on public-information moves.

**Verdict.** At 1-contract NQ with retail latency and no queue engineering, passive quoting is a
negative-expectation lane per this literature; the honest use of these results is **execution-cost
modeling** (when a limit entry actually fills, conditional on adverse selection), not a strategy.
Data requirement: genuine queue research needs **MBO** (order-level, to reconstruct position).
Execution-cost calibration needs only tick+BBO.

---

## 5. VIX term structure as a conditioner; VIX-basis trade and its decay

- Simon & Campasano, "The VIX Futures Basis: Evidence and Trading Strategies," *J. Derivatives* 2014
  (doi:10.3905/jod.2014.21.3.054; SSRN 2094510, 2012) (VERIFIED-metadata; the OpenAlex record for the
  JoD DOI carries a mis-attached unrelated abstract — noted as a data-quality flag). MODEL
  KNOWLEDGE: rule = when the front basis is in steep contango, short VIX futures hedged with mini
  S&P futures (and reverse in backwardation); sample ~2006–2011; economically large returns. The
  basis predicts **VIX futures** returns (roll-down), *not* VIX changes and not S&P direction.
- Cheng, "The VIX Premium," *RFS* 2019 (VERIFIED-ABSTRACT): ex-ante premium **predicts ex-post VIX
  futures returns with coefficient near one**; the premium *falls* when risk rises; falling premium
  predicts increasing market risk — i.e., the conditioning content is real and state-dependent.
- Frijns, Tourani-Rad, Webb, *JFM* 2016 (VERIFIED-ABSTRACT): intraday, **VIX futures lead the VIX
  index** (bi-directional but futures-dominant, strengthening over 2008–2014; strongest on down/high-VIX
  days) — the VX curve is the causal locus, spot VIX is partly derivative.
- Yoon, Ruan, Zhang, *JFM* 2022 (VERIFIED-ABSTRACT): VIX-option IV slope predicts VIX futures
  returns **next day to one month**, beating existing proxies (needs VIX options data — not owned).
- **Decay/crash evidence:** Augustin, Cheng, Van den Bergen, "Volmageddon and the Failure of Short
  Volatility Products," *FAJ* 2021 (VERIFIED-ABSTRACT): 2018-02-05 destroyed naive short-vol via
  hedge/leverage rebalancing feedback in a concentrated complex. MODEL KNOWLEDGE: post-2018 and
  post-2020 the unconditional short-VX carry Sharpe is far below the 2006–2011 in-sample figures;
  the surviving use in the literature is **contango/backwardation state as a risk-on/off regime
  flag** (daily horizon), which is exactly the conditioner use-case.

**Data requirement:** daily VX settlements (already free — Cboe CDN files, RECORDED CLAIM:
`research/information_frontier/CURRENT_INFORMATION_MAP.md:34`) or the VX/VXM 1-min+daily already
reachable in NT8 (RECORDED CLAIM: same file, line 29 — "never named in any repo data document").
Retail-implementable: yes, trivially, at daily/half-day horizon. This is the highest
evidence-to-cost mechanism in this entire report.

---

## 6. Realized-vs-implied variance premium (VRP) timing

- Bollerslev, Tauchen, Zhou *RFS* 2009 (MODEL KNOWLEDGE): IV²−RV² predicts equity returns at
  3–6-month horizon, R² mid-single-digit quarterly.
- Kılıç & Shaliastovich, *Mgmt Sci* 2018 (VERIFIED-ABSTRACT): good/bad decomposition predicts 1–2y
  returns, **R² ≈10% equities, 20% corporate bonds**, opposite signs on components.
- Martin, *QJE* 2017 SVIX (VERIFIED-ABSTRACT): option-implied lower bound on the equity premium —
  high-stress periods = high expected short-run returns; usable as a floor-style conditioner.
- Andersen, Fusari, Todorov, *JF* 2017 weekly options (VERIFIED-ABSTRACT): short-dated options
  isolate a **negative jump-tail factor not spanned by volatility level** that predicts returns.

**Verdict.** VRP is a slow (weeks-months) conditioner. Computable today: RV from owned 1-min NQ bars
+ VIX/VIX3M free history (RECORDED CLAIM: CURRENT_INFORMATION_MAP.md:34). No depth data involved.
Decay: the premium is a risk premium, persistent by nature but with crash episodes; timing overlays
degrade the Sharpe more than harvesting (MODEL KNOWLEDGE).

---

## 7. Dealer gamma (Barbon–Buraschi, GEX) — and its evidence quality

- Barbon & Buraschi, "Gamma Fragility," SSRN 3725454, 2020 (VERIFIED-metadata; **cites=1 on the
  OpenAlex SSRN record** — the visible academic footprint is thin). MODEL KNOWLEDGE: negative dealer
  gamma ⇒ hedging amplifies moves (intraday momentum, higher close volatility); positive gamma ⇒
  damping/pinning. Sign of dealer inventory is **imputed from open interest plus assumptions about
  who is short/long**, not observed.
- **The one validated link:** Ni, Pearson, Poteshman, White, "Does Option Trading Have a Pervasive
  Impact on Underlying Stock Prices?" *RFS* 2021 (hhaa082) (VERIFIED-ABSTRACT): a
  **noninformational channel — market-maker hedge rebalancing — affects stock return volatility and
  the probability of large moves**. MODEL KNOWLEDGE: this paper (and Ni-Pearson-Poteshman *JFE*
  2005 expiration-pinning; Golez & Jackwerth, "Pinning in the S&P 500 futures," *JFE* 2012,
  VERIFIED-metadata, 43 cites) uses actual market-maker position data/expiration identification, so
  the *mechanism* is validated. What is NOT validated anywhere in the academic literature is the
  **practitioner GEX recipe**: EOD open interest × assumed uniform dealer sign.
- Baltussen, Da, Lammers, Martens, "Hedging Demand and Market Intraday Momentum," *JFE* 2021, 96
  cites (VERIFIED-metadata; author page confirms citation, Vol 142, 377-403): MODEL KNOWLEDGE —
  first-half-hour → last-half-hour momentum in index futures worldwide, strongest when
  gamma-hedging demand (options + leveraged ETFs) is large; the hedging-flow footprint concentrates
  in the **last half hour** — tradeable at 1-min resolution.
- Direct 0DTE-hedging channel in futures: Ladia, "Opening-Range Reversal in Dow Jones Futures:
  Evidence Consistent with 0DTE Hedging Pressure," SSRN 7124578, 2026, 0 cites (VERIFIED-metadata
  only — untested, but shows the lane is active).
- Repo's own audit agrees and is sharper than the literature on the data problem: **"OI is EOD and
  ≥1 session stale ... the dealer sign is a free parameter that flips the entire signal. 0DTE — the
  loudest claim — is the part the data covers worst, since same-day-opened-and-closed positions
  largely never enter OI"** (RECORDED CLAIM: `research/information_frontier/ACQUISITION_DECISION_PACKET.md:53`).

**Verdict.** Mechanism: real (RFS-validated). Practitioner GEX products: **sign-assumption-driven;
never validated against observed dealer books; classify as marketing** unless a validated position
source exists. The *tradeable residue* that survives scrutiny is time-of-day hedging-flow
concentration (last-half-hour effects) — testable on owned 1-min bars.

---

## 8. 0DTE and intraday index dynamics (2022+)

- Brogaard, Han, Won, "Does 0DTE Options Trading Increase Volatility?" SSRN 4426358, 2023, 12 cites
  (VERIFIED-metadata). MODEL KNOWLEDGE: finds a positive association between 0DTE activity and
  intraday volatility. Opposed by dealer/exchange research (Cboe, Mandy Xu 2023: net 0DTE dealer
  positioning small and two-sided, no Volmageddon-style loop) — the question is **openly contested**.
- Beckmeyer, Branger, Gayda, "Retail Traders Love 0DTE Options... But Should They?" SSRN 4404704,
  2023, 10 cites (VERIFIED-metadata). MODEL KNOWLEDGE: retail 0DTE buyers lose on average;
  economically large negative expected returns — the strategy content for us is on the SELL side or
  none.
- Pricing frontier exists: Bandi, Fusari, Renò "0DTE Option Pricing" (SSRN 4503344); Almeida,
  Freire, Hizmeri "0DTE Asset Pricing" (4701401); Vilkov "0DTE Trading Rules" (4641356); Egebjerg,
  *J. Financial Stability* 2026 (VERIFIED-ABSTRACT): 0DTE now **dominate SPX option volume**; deep
  hedging beats BS delta at 0DTE horizon (all VERIFIED-metadata unless noted).
- NQ relevance: NDX/QQQ 0DTE exist but SPX is the studied complex; spillover to ES/NQ futures via
  hedging is the plausible channel (MODEL KNOWLEDGE).

**Verdict.** Effects on intraday dynamics are real enough to condition on time-of-day/expiration
calendar (0DTE-heavy days, last-hour flows), but the direct signal (dealer 0DTE positioning) is
**unobservable in any purchasable dataset** (OI cadence problem — RECORDED CLAIM at
ACQUISITION_DECISION_PACKET.md:53). No depth purchase fixes this.

---

## 9. Intraday momentum (bonus mechanism — cheapest strong effect found)

- Gao, Han, Li, Zhou, "Market Intraday Momentum," *JFE* 2018, 221 cites (VERIFIED-metadata).
  MODEL KNOWLEDGE: first half-hour (and penultimate half-hour) return predicts last half-hour, SPY
  1993–2013, out-of-sample R² ~2%, monetizable at one trade/day; strongest on high-volatility,
  high-volume, recession days.
- Baltussen et al. 2021 (above) ties it to hedging demand — index futures, global (VERIFIED-metadata).
- Related cross-checks: Lou, Polk, Skouras *JFE* 2019 overnight/intraday clientele split
  (VERIFIED-metadata); Heston, Korajczyk, Sadka *JF* 2010 half-hour periodicity (VERIFIED-ABSTRACT).
- Decay: post-publication evidence mixed (MODEL KNOWLEDGE); the hedging-demand version has an
  identified flow driver that has *grown* (options/LETF AUM), which is the right kind of decay story.
- Data requirement: **1-min bars only.** Retail 1-contract NQ: one round turn/day ≈ $18.80 ≈ 3.8
  ticks/day hurdle — a last-half-hour NQ move is routinely 20–100+ ticks, so the cost bar does not
  kill the mechanism class (arithmetic; costs RECORDED CLAIM CLAUDE.md §6).

---

## 10. Answers to the three commissioned questions

### (a) Testable with data the project ALREADY has (1-min OHLCV, limited tick/BBO, VX curve access)

1. **VX term-structure conditioner** (contango/backwardation state; Cheng-style premium; Frijns
   futures-lead) — daily + 1-min VX already reachable at $0 (RECORDED CLAIM:
   CURRENT_INFORMATION_MAP.md:29,34). Strongest evidence-per-dollar in this report.
2. **VRP / RV-vs-IV timing** — RV from owned 1-min NQ; VIX/VIX3M free history. Weeks-scale
   conditioner.
3. **Intraday momentum & last-half-hour hedging-flow effects** (Gao et al.; Baltussen et al.;
   0DTE-day calendar splits) — 1-min bars only.
4. **Signed order flow at minute scale** — the owned 104 NQ tick + BBO sessions support quote-rule
   classification (the literature-correct method per Andersen-Bondarenko) → per-minute signed
   volume/OFI conditioners on a *limited but real* sample. NOT sufficient for seconds-scale OFI
   research at scale, but sufficient for a pilot falsifier.
5. **Depth-as-volatility-conditioner (L1 version)** — BBO sizes on the owned sessions;
   large-tick concentration argument (Gould-Bonart) says L1 carries most of it.
6. **Trade-classification validation itself** — a one-session check of quote-rule vs tick-rule
   agreement on owned data would replicate the Andersen-Bondarenko design at zero cost.

### (b) Genuinely require depth history (the Databento question)

1. **Queue-position / passive-fill economics research** — requires **MBO** (order-level IDs;
   GLBX.MDP3 MBO from 2017-05-21, RECORDED CLAIM: ACQUISITION_DECISION_PACKET.md:32). But the
   literature verdict (§4) is that the retail payoff of this lane is execution-cost calibration,
   not alpha — a **narrow slice, not a history buy**.
2. **Multi-level/integrated OFI, book slope across levels, MLOFI** — requires **MBP-10**
   (GLBX.MDP3 from 2010-06-06, same RECORDED CLAIM). Expected payoff: better *contemporaneous*
   explanation and second-to-minute predictors that the cost bar (§1) likely neutralizes at
   1-contract retail latency. If a pilot is bought, buy **MBP-10, one instrument, bounded slice**
   (matches the repo's own minimum-viable-pilot spec, ACQUISITION_DECISION_PACKET.md:35) with a
   preregistered falsifier of the form "does adding L2–L10 beat L1-only on *minute-scale*
   out-of-sample prediction, net of the 3.8-tick cost bar."
3. **Flash-crash / fragility microforensics** — MBO; research interest, not an edge.

### (c) Marketing (buys nothing testable at this scale)

1. **GEX / dealer-gamma dashboards** — dealer sign is an unvalidated free parameter; OI cadence
   makes 0DTE (the loudest channel) invisible; no academic validation of the practitioner recipe
   exists (§7; RECORDED CLAIM: ACQUISITION_DECISION_PACKET.md:53 independently reached the same
   verdict). The validated *mechanism* is testable via time-of-day effects on data already owned.
2. **VPIN / "flow toxicity" products** — the best-identified futures study finds its forecast power
   is a classification artifact (§2, VERIFIED-ABSTRACT).
3. **BVC-based signed flow at bar level** — explicitly inferior to tick rule in ES
   (VERIFIED-ABSTRACT); do not buy or build.
4. **Seconds-horizon OFI "alpha" for takers** — real in-sample, structurally unmonetizable at
   retail latency/cost (3.8-tick bar); products claiming otherwise are selling the contemporaneous
   R².
5. **Macro-surprise vendors** — N-bound, per the repo's own gate math (RECORDED CLAIM:
   ACQUISITION_DECISION_PACKET.md:45); unrelated to depth but listed for completeness.

### Pricing implication for the pending Databento decision

The mechanisms with the strongest external evidence and retail implementability (VX-curve
conditioner, VRP, intraday momentum/hedging-flow timing) need **zero depth data**. The mechanisms
depth actually unlocks (queue economics, multi-level OFI) are the two the literature itself scores
as execution-relevant rather than alpha-relevant at 1-contract scale. External literature therefore
supports: **exhaust the $0 lanes first; if piloting Databento, a bounded MBP-10 slice as an
execution/cost-model and L1-sufficiency test — not an alpha purchase.** This is consistent with,
and independently derived from, the repo's own packet (ACQUISITION_DECISION_PACKET.md:6-11).

---

## Source log (all fetched this session)

- arXiv abstracts fetched: 1011.6402, 2112.13213, 1808.03668, 1512.03492, 1803.06917; arXiv API
  listing for "order flow imbalance" (15 records incl. 2508.06788, 1907.06230, 2505.17388).
- OpenAlex API result dumps: `scratchpad/oa_results.txt` (18 queries), `scratchpad/oa_results2.txt`
  (8 queries + 8 DOI lookups). Notable verified records: Cont-Kukanov-Stoikov JFEconometrics 2013
  (300 cites); Andersen-Bondarenko 2013 (full abstract); Easley-LdP-O'Hara RFS 2012; Chakrabarty-
  Pascual-Shkilko JFM 2015; Simon-Campasano JoD 2014/SSRN 2012; Cheng RFS 2019; Frijns et al. JFM
  2016; Yoon-Ruan-Zhang JFM 2022; Augustin-Cheng-Van den Bergen FAJ 2021; Kılıç-Shaliastovich 2018;
  Martin QJE 2017; Andersen-Fusari-Todorov JF 2017; Ni-Pearson-Poteshman-White RFS 2021 (abstract);
  Golez-Jackwerth JFE 2012; Barbon-Buraschi SSRN 3725454; Baltussen et al. JFE 2021; Gao et al. JFE
  2018; Moallemi-Yuan SSRN 2996221; Donnelly-Gan 2018 (abstract); Budish-Cramton-Shim QJE 2015
  (abstract); Cartea-Donnelly-Jaimungal 2018 (abstract); Gould-Bonart; Brogaard-Han-Won SSRN
  4426358; Beckmeyer-Branger-Gayda SSRN 4404704; Bandi-Fusari-Renò 4503344; Almeida-Freire-Hizmeri
  4701401; Vilkov 4641356; Egebjerg JFS 2026 (abstract); Ladia SSRN 7124578; Kang-Kwon-Kim JFM 2019
  (abstract); Braun et al. PLoS ONE 2018 (abstract); Hasbrouck JFQA 2004 (abstract).
- Blocked/failed this session: WebSearch (budget 200/200 exhausted before start), SSRN direct
  (HTTP 403), DuckDuckGo HTML (CAPTCHA), Bing (irrelevant results), Semantic Scholar API (429),
  moallemi.com (404), Databento docs (JS-rendered SPA, no static content — schema claims left at
  MODEL KNOWLEDGE / repo RECORDED CLAIM level).
- Repo files read (read-only): CLAUDE.md; research/information_frontier/ACQUISITION_DECISION_PACKET.md
  (lines 6-68); research/information_frontier/CURRENT_INFORMATION_MAP.md (lines 1-55). No repo or
  NT8 file was created, modified, or deleted. No mcp__crosstrade__* tool was called. No market-data
  values were read; no sealed/blind-pool file was opened.
