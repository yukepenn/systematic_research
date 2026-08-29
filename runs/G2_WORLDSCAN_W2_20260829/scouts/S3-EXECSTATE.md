# S3 EXECUTION-STATE SCOUT — GENESIS II WORLD SCAN WAVE 2 (2026-08-29)

DOMAIN SUMMARY (3 lines):
Liquidity/spread-STATE conditioning is best documented at the close: the 15:50 ET auction-imbalance publication (NYSE every 1s; Nasdaq NOII 3:50-4:00) is a real, timestamped information event with peer-reviewed evidence (Jegadeesh-Wu; Bogousslavsky-Muravyev; Cushing-Madhavan 2000) that prices react to imbalance information — the futures-spillover leg is unmeasured in public work and is our cheapest original test. Depth/spread-state execution economics are solidly documented (Cont-Kukanov-Stoikov impact slope ~ 1/depth; Muravyev-Picard within-minute trade clustering; BestEx time-of-day cost effect; futures-specific Pulse TCA), i.e., POLICY leads that monetize EXEC01's 2-6 tick spread states as cost savings, not alpha. Direct "intraday Amihud state → next-interval index-futures return" tradability is a genuine literature GAP — nobody credible shows it as a standalone signal; toxicity-state work (VPIN) survives only as a contested vol/liquidity-transition forecaster, not return alpha.

METHOD NOTE (constraint compliance): WebSearch quota was exhausted session-wide (200/200) before this scout ran; per instructions I fell back to WebFetch on site-native search/API URLs (Crossref API, OpenAlex API, arXiv API, Semantic Scholar API) plus direct page fetches. DuckDuckGo (captcha), Bing (irrelevant results), Mojeek/SSRN/Wiley/AlphaArchitect (HTTP 403) were unusable; abstracts on Elsevier/SSRN were not retrievable, so several CLAIM fields are title/venue-level with the access limitation flagged inline. Every URL below was actually fetched today except where marked (doi.org resolver links given for verified DOIs).

---

[LEAD id=S3-01]
SOURCE: https://www.nyse.com/auctions (fetched, dissemination table) + https://www.nasdaqtrader.com/Trader.aspx?id=OpenClose (fetched) | ACCESSED: 2026-08-29 | AUTHOR: NYSE / Nasdaq (exchange documentation) | DATE: current exchange rules
TYPE: vendor
CLAIM: NYSE begins closing-auction imbalance publication at the 3:50 p.m. ET MOC/LOC cutoff and disseminates every 1 second until the auction completes (fields: Indicative Match Price, Total Imbalance, Market Imbalance, Paired Quantity, Auction Collar, Reference Price); Nasdaq disseminates Closing Cross Net Order Imbalance information between 3:50 and 4:00 p.m. ET.
EVIDENCE: audited-code (exchange rule/spec pages, literal)
MARKET: US equities (spills to index futures) HORIZON: 15:50-16:00 ET, minutes
MECHANISM: A scheduled public release of net auction demand creates a known information event; index-level aggregation of imbalances should move index futures within the following minutes as arbitrageurs pre-position.
OBSERVABLES: event time 15:50:00 ET; per-second imbalance feed (not owned); proxy = NQ/ES 1-min return, range, volume in 15:49-16:00 vs matched earlier windows
NOVELTY: RAW-INFO
PRIOR: MED - the feed itself is real and timestamped; whether the INDEX-level aggregate is big enough to move NQ after $33/RT is unmeasured publicly.
CHEAPEST-FALSIFIER: On NQ 1-min 2006-2026 (pre-burn window), test for a structural break in |return|, volume, and 1-min autocorrelation exactly at 15:50 ET vs 15:40/15:45 controls (same-session shared null, circular shifts); if no event signature exists at the minute level, the spillover is not tradable at our cost floor and the lead dies without buying imbalance data.
INDEPENDENCE: exchange primary sources; no strategy copied.
[/LEAD]

[LEAD id=S3-02]
SOURCE: https://doi.org/10.2139/ssrn.3732955 (Crossref+OpenAlex verified; SSRN page 403) | ACCESSED: 2026-08-29 | AUTHOR: Narasimhan Jegadeesh, Yanbin Wu | DATE: 2020 (SSRN WP)
TYPE: paper
CLAIM: "Closing Auctions: Information Content and Timeliness of Price Reaction" — the closing-auction imbalance information disseminated pre-close carries price-relevant information and the paper measures how quickly continuous-market prices react to it. (Title/venue-level; abstract not fetchable through any open API today.)
EVIDENCE: peer-reviewed lineage (companion "Closing auctions: Nasdaq versus NYSE", Journal of Financial Economics 2022, DOI 10.1016/j.jfineco.2021.12.003, Crossref-verified)
MARKET: US single stocks, NYSE+Nasdaq HORIZON: 15:50-16:00 ET
MECHANISM: Imbalance dissemination reveals inelastic MOC demand (index funds); prices drift toward the indicative match price before the cross.
OBSERVABLES: NOII/NYSE imbalance fields (not owned); indicative match price vs last sale; paired quantity
NOVELTY: RAW-INFO
PRIOR: MED - peer-reviewed team, real information event; transfer to NQ futures untested and index-aggregation may dilute the signal below cost.
CHEAPEST-FALSIFIER: Same falsifier as S3-01 (the two share one test and must share one null family); additionally condition the 15:50-16:00 NQ drift sign on the 15:30-15:50 NQ return sign (rebalancing-pressure proxy) with the matched unconditional control in the same wave.
INDEPENDENCE: independent of Bogousslavsky-Muravyev (different team, different data).
[/LEAD]

[LEAD id=S3-03]
SOURCE: https://doi.org/10.1016/j.finmar.2023.100852 (Crossref+OpenAlex verified: Journal of Financial Markets 66, 2023) | ACCESSED: 2026-08-29 | AUTHOR: Vincent Bogousslavsky, Dmitriy Muravyev | DATE: 2023
TYPE: paper
CLAIM: "Who trades at the close? Implications for price discovery and liquidity" — documents who supplies/demands liquidity in the closing auction and the consequences for end-of-day price discovery and dislocations. (Title/venue-level; Elsevier abstract not retrievable via OpenAlex/S2 — abstract_inverted_index null.)
EVIDENCE: peer-reviewed
MARKET: US equities HORIZON: last minutes of RTH + overnight reversal
MECHANISM: Concentrated, largely price-inelastic auction flow (indexing) can push the 4pm print away from continuous-market value; deviations should revert when elastic capital returns.
OBSERVABLES: closing price vs 15:55-16:00 midquote; auction volume share; overnight return
NOVELTY: REPRESENTATION (close-dislocation state)
PRIOR: MED - highly cited (61 cites), mechanism is capacity-limited but real; NQ transfer is a proxy test only.
CHEAPEST-FALSIFIER: On NQ 1-min 2006-2026 pre-burn: define dislocation = (16:00 price − 15:55 price); test whether it mean-reverts over 16:00→18:00 and →next 09:30 beyond the unconditional control, with dependence-preserving nulls; dead if reversion < cost floor at every dislocation decile.
INDEPENDENCE: independent team; conceptual descendant of Cushing-Madhavan (S3-04).
[/LEAD]

[LEAD id=S3-04]
SOURCE: https://doi.org/10.1016/s1386-4181(99)00012-9 (Crossref-verified: Journal of Financial Markets, 2000) | ACCESSED: 2026-08-29 | AUTHOR: David Cushing, Ananth Madhavan | DATE: 2000
TYPE: paper
CLAIM: "Stock returns and trading at the close" — end-of-day returns are strongly affected by MOC order-flow pressure; last-minutes price moves associated with order imbalances partially reverse subsequently (the original close-pressure/reversal documentation).
EVIDENCE: peer-reviewed
MARKET: US large-cap stocks, 1990s HORIZON: final 15 minutes + next open
MECHANISM: Inelastic institutional demand at the close pays a liquidity premium to guarantee the closing print; the premium is the counterparty's expected reversal.
OBSERVABLES: last-15-min return, imbalance proxies, next-day open return
NOVELTY: REPRESENTATION
PRIOR: LOW-MED - era is pre-decimalization and pre-auction-modernization (2005-2022 vs 2023-2026 regime question is severe); mechanism persists but magnitude unknown.
CHEAPEST-FALSIFIER: Folded into the S3-03 falsifier as its historical-era leg: run the same dislocation-reversal test separately on 2006-2015 and 2016-2026 pre-burn NQ to see if the effect era-decays like most close-pressure results.
INDEPENDENCE: primary source for the family; S3-02/S3-03 are its modern heirs.
[/LEAD]

[LEAD id=S3-05]
SOURCE: https://doi.org/10.1016/j.jfineco.2021.04.029 (Crossref+OpenAlex verified: JFE 142(1) 377-403; SSRN 3760365) | ACCESSED: 2026-08-29 | AUTHOR: Guido Baltussen, Zhi Da, Sten Lammers, Martin Martens | DATE: 2021
TYPE: paper
CLAIM: "Hedging demand and market intraday momentum" — last-half-hour index momentum is driven by mechanical hedging demand (leveraged ETF rebalancing / option-dealer gamma), so the late-day continuation strengthens with the magnitude of the day's move-to-date and with hedging-demand proxies. (Title+venue verified; abstract not retrievable — claim wording from the paper's established thesis.)
EVIDENCE: peer-reviewed (96 citations, 98.5th pct impact per OpenAlex)
MARKET: S&P 500 futures + international index futures HORIZON: ~15:30-16:00 ET
MECHANISM: Leveraged ETFs and short-gamma dealers must trade WITH the day's move near the close; the flow is calendar-predictable in sign and increasing in |return-to-date|.
OBSERVABLES: day return 09:30→15:30 (sign and magnitude); leveraged-ETF AUM era; last-30-min NQ return
NOVELTY: MECHANISM-POLICY (⚠️ Gao half-hour geometry is DEAD in-house — this survives ONLY as the hedging-demand-conditioned version: the |move|-scaling and era-scaling are the materially different observables, not the raw first-half-hour→last-half-hour correlation)
PRIOR: MED - strong publication, mechanical flow story; but our Gao-geometry kill and 2023-26 0DTE-era gamma changes could have inverted it.
CHEAPEST-FALSIFIER: NQ 1-min 2006-2026 pre-burn: regress 15:30→16:00 return on sign(09:30→15:30 return)×|move| terciles with matched unconditional control; PASS requires monotonicity in |move| AND era-stability 2016+ AND net of $33/RT at realistic sizing; else dead.
INDEPENDENCE: distinct from Gao-Han-Li-Zhou 2018 (which it subsumes mechanistically); Robeco-affiliated authors.
[/LEAD]

[LEAD id=S3-06]
SOURCE: https://doi.org/10.1093/rfs/hhs053 (Crossref-verified: RFS 2012; SSRN 1695596) + critique https://doi.org/10.1016/j.finmar.2013.05.005 (Andersen-Bondarenko, JFM 2014, Crossref-verified) + https://doi.org/10.1002/fut.22062 (Kang et al., J. Futures Markets 2019, KOSPI 200 futures, OpenAlex-verified) | ACCESSED: 2026-08-29 | AUTHOR: David Easley, Marcos López de Prado, Maureen O'Hara | DATE: 2012
TYPE: paper
CLAIM: "Flow Toxicity and Liquidity in a High-frequency World" — VPIN (volume-synchronized probability of informed trading) measures order-flow toxicity and elevated VPIN precedes liquidity withdrawal and short-horizon volatility (famously claimed elevated before the 2010 flash crash in ES). Andersen-Bondarenko ("VPIN and the flash crash", JFM 2014) contest this: predictive power largely disappears under proper controls; Kang et al. 2019 find toxicity-volatility links in KOSPI 200 futures.
EVIDENCE: peer-reviewed AND peer-reviewed-contested (both sides in print)
MARKET: ES futures (original), KOSPI 200 futures HORIZON: minutes-hours
MECHANISM: When flow becomes one-sided/informed, market makers widen or withdraw, so a toxicity state forecasts the spread/vol state transition — an execution-timing input, not a return signal.
OBSERVABLES: bulk-volume-classified signed volume in fixed-volume buckets; VPIN percentile; subsequent RV and spread state
NOVELTY: REPRESENTATION (toxicity state) + POLICY (when NOT to execute)
PRIOR: LOW-MED - the alpha claim is contested in print; the exec-policy claim (avoid entering during top-decile toxicity) is weaker-form and more plausible. ⚠️ RV-tercile RETURN conditioning is dead in-house; frame strictly as spread/vol-state forecasting for cost policy.
CHEAPEST-FALSIFIER: Compute bulk-volume VPIN from NQ 1-min price+volume 2006-2026 pre-burn; test whether top-decile VPIN predicts next-hour spread-state deterioration (using 2025-26 NQ tick+BBO overlap for ground truth) better than lagged RV alone; if VPIN adds nothing over RV, drop.
INDEPENDENCE: Easley/O'Hara school; Kang et al. independent replication team; Andersen-Bondarenko independent adversaries.
[/LEAD]

[LEAD id=S3-07]
SOURCE: https://arxiv.org/abs/1011.6402 (fetched via arXiv API) | ACCESSED: 2026-08-29 | AUTHOR: Rama Cont, Arseniy Kukanov, Sasha Stoikov | DATE: 2010-11-29 (later J. Financial Econometrics 2014)
TYPE: paper
CLAIM: "The Price Impact of Order Book Events" — literal from abstract: a "linear relation between order flow imbalance and price changes, with a slope inversely proportional to the market depth"; i.e., the SAME net flow moves price ~2-3x more when depth is thin.
EVIDENCE: peer-reviewed (published version), audited methodology on TAQ/order-book data
MARKET: US equities order books; mechanism generic to CLOB futures HORIZON: seconds-minutes
MECHANISM: Price change ≈ OFI/(2·depth): depth state is the gain of the flow→price transfer function, so liquidity state mechanically scales both impact cost and the profitability of any flow-based signal.
OBSERVABLES: top-of-book depth, OFI, our EXEC01 spread states (2-6 ticks by hour/vol)
NOVELTY: POLICY (execution-cost state model; also a scaling correction for any in-house flow signal)
PRIOR: HIGH - one of the most replicated microstructure regularities; near-certain to hold on NQ.
CHEAPEST-FALSIFIER: On 2025-26 NQ tick+BBO: estimate the 10s OFI→mid-change slope within each EXEC01 spread/depth state; confirm inverse-depth scaling; then quantify $ saved by shifting a fixed hypothetical 5-lot schedule from thin-state to deep-state minutes within the same hour (pure cost policy, no seal risk).
INDEPENDENCE: none copied; foundational.
[/LEAD]

[LEAD id=S3-08]
SOURCE: https://doi.org/10.1111/fima.12405 (Crossref-verified: Financial Management 2022; SSRN 2496669; abstract behind Wiley/SSRN 403s) | ACCESSED: 2026-08-29 | AUTHOR: Dmitriy Muravyev, Joerg Picard | DATE: 2022
TYPE: paper
CLAIM: "Does Trade Clustering Reduce Trading Costs? Evidence from Periodicity in Algorithmic Trading" — algorithmic executions cluster at periodic, predictable times (round times within the minute/hour), and the paper measures whether trading inside these clusters carries different trading costs. (Title/venue-level; the sign of the answer was not verifiable through any open source today — do not assume the direction.)
EVIDENCE: peer-reviewed
MARKET: US equities HORIZON: sub-minute
MECHANISM: TWAP/VWAP child-order schedules fire on clock marks; liquidity supply and adverse selection at :00 seconds differ from mid-interval seconds, so WHEN within the minute you cross the spread is a free policy variable.
OBSERVABLES: trade timestamp second-of-minute; effective spread, depth, short-horizon markout by second-of-minute
NOVELTY: POLICY (entry-timing within the minute — directly actionable for every in-house strategy that enters on 1-min bar close)
PRIOR: MED-HIGH - clock-mark clustering is easily verifiable on our own tick data regardless of the paper's sign.
CHEAPEST-FALSIFIER: On 2025-26 NQ tick+BBO: compute volume share, effective spread, and 5s/30s markouts by second-of-minute; if second-0/second-30 states differ by ≥0.25 tick in expected cost, re-time our 11:48 continuation entry off the bar boundary and measure the saving; costs nothing and touches no seal.
INDEPENDENCE: Muravyev also co-authors S3-03 — treat the two leads as same-author but different mechanisms.
[/LEAD]

[LEAD id=S3-09]
SOURCE: https://bestexresearch.com/insights/the-time-of-day-effect-a-breakthrough-in-trading-cost-optimization (fetched) | ACCESSED: 2026-08-29 | AUTHOR: BestEx Research | DATE: 2025-07-14
TYPE: vendor
CLAIM: Literal: "executing the same order in the final hour of the trading session is consistently less costly than executing it earlier in the day" — measured as market-impact cost for Russell 2000 constituents at fixed order size (1% ADV) and fixed 15% participation, i.e., a pure time-of-day liquidity-state effect, not a volume effect.
EVIDENCE: backtest-screenshot (vendor figure; methodology described, numbers not disclosed publicly)
MARKET: US equities (execution) HORIZON: intraday scheduling
MECHANISM: Late-day depth/volume states absorb the same participation with less permanent impact — liquidity-state elasticity varies by hour even at constant participation.
OBSERVABLES: hour-of-day, participation rate, impact per unit size; our EXEC01 hourly spread states
PRIOR: MED - vendor selling schedulers, but the direction matches EXEC01's measured 2-6 tick hourly spread states on NQ.
NOVELTY: POLICY
CHEAPEST-FALSIFIER: On 2025-26 NQ tick+BBO: simulate an identical 5-lot aggressive schedule at 10:00 vs 15:00 within matched-vol days; if late-session all-in cost is not lower by ≥0.5 tick/contract, the effect does not transfer to tick-constrained NQ (BestEx's own Pulse piece warns equity models mistransfer to futures).
INDEPENDENCE: none copied; complements S3-10.
[/LEAD]

[LEAD id=S3-10]
SOURCE: https://bestexresearch.com/insights/a-novel-transaction-cost-model-addressing-the-microstructural-complexities-of-futures-trading (fetched) | ACCESSED: 2026-08-29 | AUTHOR: BestEx Research | DATE: 2025-09-10
TYPE: vendor
CLAIM: Futures transaction costs cannot be modeled with equity-style volume/volatility inputs; their futures model ("Pulse") is built on "market depth and bid-offer spread" states and addresses "shadow liquidity, large tick sizes, intraday liquidity variations, and execution data biases", splitting cost into market impact vs order-placement cost, validated "across diverse futures products ... varying times of day ... and different trading conditions".
EVIDENCE: backtest-screenshot (abridged public abstract; full paper client-only)
MARKET: CME futures incl. equity index HORIZON: execution
MECHANISM: In tick-constrained books (NQ), the spread/depth STATE — not volume — is the sufficient statistic for expected cost, so cost-optimal behavior is state-conditional (passive in wide-spread states, aggressive in deep states).
OBSERVABLES: top-of-book depth, spread state, queue position, time-of-day
NOVELTY: POLICY
PRIOR: MED-HIGH - independently corroborates exactly what EXEC01 measured in-house (NQ spread states 2-6 ticks by hour/vol); vendor validation of our representation.
CHEAPEST-FALSIFIER: Extend EXEC01 on 2025-26 NQ tick+BBO: fit expected cost per contract as f(spread state, depth state, hour); verify the two-component (impact + placement) decomposition beats a volume/vol-only model out-of-sample on held-out sessions.
INDEPENDENCE: same vendor as S3-09 (count as one source family for correlation purposes).
[/LEAD]

[LEAD id=S3-11]
SOURCE: https://www.quantitativebrokers.com/blog/navigate-volatility-with-confidence (fetched) | ACCESSED: 2026-08-29 | AUTHOR: Chin Huang (Quantitative Brokers) | DATE: 2025-05-09
TYPE: vendor
CLAIM: In the April 2025 selloff, E-mini S&P 500 liquidity was "at levels not seen since the 2020 COVID selloff"; QB's futures algos respond to the liquidity state by placing passive orders "deeper in the book" in unfavorable volatility regimes and modulating pace (Strobe) on real-time liquidity/volatility conditions.
EVIDENCE: anecdote (vendor chart of Striker slippage vs benchmark; no public numbers)
MARKET: CME equity index futures HORIZON: execution, regime-scale
MECHANISM: Depth evaporates in vol regimes faster than spreads widen, so queue placement depth (not just aggressiveness) is the state-conditional control variable.
OBSERVABLES: book depth by level, vol regime flag, fill-probability by queue depth
NOVELTY: POLICY
PRIOR: LOW-MED - concrete tactic, zero disclosed measurement; useful mainly as corroboration that professional futures execution is depth-STATE-keyed.
CHEAPEST-FALSIFIER: On 2025-26 NQ tick+BBO (contains the April 2025 depth collapse): measure fill probability and adverse selection of a synthetic passive order at book level 1 vs level 2-3 across vol-regime states; if deeper placement doesn't improve net cost in thin states, the tactic is not real for our size.
INDEPENDENCE: independent vendor (QB), different from BestEx family.
[/LEAD]

[LEAD id=S3-12]
SOURCE: https://doi.org/10.1016/j.jfineco.2019.03.011 (OpenAlex-verified: JFE 2019) | ACCESSED: 2026-08-29 | AUTHOR: Dong Lou, Christopher Polk, Spyros Skouras | DATE: 2019
TYPE: paper
CLAIM: "A tug of war: Overnight versus intraday expected returns" — overnight and intraday return components are systematically different and negatively related across firms/strategies because different investor clienteles dominate the overnight session vs the trading day (the session HANDOFF itself carries return structure).
EVIDENCE: peer-reviewed
MARKET: US equities cross-section (index-level implications) HORIZON: session-level decomposition
MECHANISM: The 9:30 open is a clientele handoff (overnight/foreign/retail positioning unwound by intraday institutions), so the open is a liquidity-transition time with predictable component flips.
OBSERVABLES: NQ overnight component (18:00→09:30) vs first-30-min and rest-of-day components
NOVELTY: REPRESENTATION (⚠️ overlap risk: "overnight drift" harvesting is DEAD in-house — the only admissible new observable is the SIGN RELATION between the overnight component and the post-open component, i.e., handoff continuation-vs-reversal, NOT unconditional overnight longs)
PRIOR: LOW-MED - strong paper, but the index-level tradable residue after our overnight-drift kill may be nil.
CHEAPEST-FALSIFIER: NQ 1-min 2006-2026 pre-burn: corr(ON return, 09:30-10:00 return) and its stability by era and by ON-range state, against the always-flat and always-long controls in the same wave; if no state gives |effect| ≥ MDE at $33/RT, close the handoff axis for good.
INDEPENDENCE: independent of all above; LSE/Athens team.
[/LEAD]

[LEAD id=S3-13]
SOURCE: https://doi.org/10.2139/ssrn.3229719 (Crossref-verified SSRN DOI; SSRN page 403 today) | ACCESSED: 2026-08-29 | AUTHOR: Andrea Frazzini, Ronen Israel, Tobias Moskowitz | DATE: 2018
TYPE: paper
CLAIM: "Trading Costs" — measures realized transaction costs and market-impact functions from a large institutional manager's own live executions (AQR), showing implementable cost curves as functions of size, participation, and liquidity conditions. (Title/DOI verified; details from broad literature knowledge — abstract not fetchable today, flagging per honesty rule.)
EVIDENCE: live-verified (proprietary execution database; the rare non-simulated cost measurement)
MARKET: global equities (methodology transfers) HORIZON: execution
MECHANISM: Real impact costs are state- and patience-dependent, and are much better estimated from own fills than from quoted spreads — the empirical warrant for maintaining our own EXEC01-style cost model rather than adopting textbook constants.
OBSERVABLES: own-fill effective spread vs decision price by state (once any strategy trades), participation, liquidity state
NOVELTY: POLICY
PRIOR: MED - not directly an NQ result; its value here is methodological licensing for state-conditional cost modeling.
CHEAPEST-FALSIFIER: No new falsifier needed on price data; the in-house analog is: when the shadow book (starts 2026-09-01) accumulates fills, fit cost vs EXEC01 state and compare against our modeled $25-33/RT — divergence >20% forces a cost-model revision.
INDEPENDENCE: AQR house research; independent of microstructure school above.
[/LEAD]

---

NEGATIVE SPACE (explicitly searched, not found — do not cite me as having found these):
- No credible public work showing intraday Amihud/illiquidity-STATE → next-interval INDEX-FUTURES return as a standalone tradable signal (searched Crossref, OpenAlex, arXiv, S2 under multiple phrasings). The closest are stock-level (Amihud 2002 lineage) or toxicity-state (S3-06). This is a gap EXEC01 data could publish into, but it is alpha-thin by construction — impact scaling (S3-07) says thin states raise costs exactly when the signal fires.
- No public paper measuring the 15:50 imbalance-publication spillover INTO index futures specifically (S3-01/S3-02 falsifier is therefore an original test).
- Goyal-Jegadeesh-Wu "Price Impact: Continuous Trading, Closing Auctions, and Opening Auctions" (SSRN 4300417, 2022, Crossref-verified) exists as a further auction-vs-continuous impact reference; abstract unreachable today, so left as a pointer rather than a full lead.
