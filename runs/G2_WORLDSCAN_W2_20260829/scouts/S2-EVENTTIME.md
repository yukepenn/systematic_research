# S2 EVENT-TIME / PATH-TOPOLOGY SCOUT — GENESIS II WORLD SCAN WAVE 2 (2026-08-29)

DOMAIN SUMMARY (3 lines):
The directional-change (DC) / intrinsic-time literature is the one event-time family with real published OOS numbers (Essex/Olsen lineage: ~30% ann. after spread on FX, >18% avg total return across 220 equity datasets, DC clock beating physical-time clock for the SAME learner), plus public audited code (Alpha Engine, Java, GPL-3, 117 stars) — but every positive number is FX/equities, none is a costed single-instrument index-futures result, and a new 2025 paper argues DC intrinsic time is a memoryless renewal process (DC-share = 1-1/e = 0.632), which would gut duration-based timing while making DEVIATIONS from 0.632 the interesting observable. The volume-clock idea splits cleanly into a verified representation claim (event bars have much better statistics: tick-Renko |VR(4)-1|=0.020, lag-1 AC=0.002, 69% serial-dependence reduction vs minute bars) and a refuted information claim (Gillemot/Farmer/Lillo + Murphy/Izzeldin: holding volume/transaction rate fixed does NOT remove clustering or heavy tails). Method note: WebSearch budget was already exhausted (200/200) when this scout started; all sourcing below was done via WebFetch on arXiv/its API, OpenAlex API, GitHub API, and site pages directly — SSRN, MDPI, Springer, DuckDuckGo, web.archive.org, core.ac.uk and kar.kent.ac.uk all refused fetches, noted per-lead where it limited claim detail.

Resolution reality across all leads: DC events at threshold delta >= ~0.1% are computable from owned NQ 1-min; delta < ~0.05% and all ACD/inter-trade work needs the owned 2025-26 NQ/ES tick+BBO only. Nothing below requires purchasing data.

---

[LEAD id=S2-01]
SOURCE: https://arxiv.org/abs/0809.1040 (published Quant. Finance 11(4):599-614, 2011) | ACCESSED: 2026-08-29 | AUTHOR: J.B. Glattfelder, A. Dupuis, R.B. Olsen | DATE: 2008-09-05 (rev. 2010-06-22)
TYPE: paper
CLAIM: Twelve independent empirical scaling laws in FX "hold for close to three orders of magnitude and across 13 currency exchange rates", derived in an event-based (directional-change) framework; they permit estimating the length of the price "coastline". The lineage's central operational law (basis of all Olsen-school trading) is that the average overshoot after a DC confirmation is commensurate with the DC threshold itself.
EVIDENCE: peer-reviewed
MARKET: 13 FX spot rates, tick data. HORIZON: intraday to multi-day, threshold-dependent (delta 0.01%-10%).
MECHANISM: Markets self-organize around discrete event scales; after a trend flips by delta, the crowd continues into an overshoot of the same order because liquidity provision/consumption is threshold-symmetric.
OBSERVABLES: DC event series at threshold delta (confirmation timestamps, direction), overshoot magnitude omega per event, event counts N(delta), coastline length. Computable from NQ 1-min closes for delta >= ~0.1%.
NOVELTY: REPRESENTATION
PRIOR: MED - laws replicated repeatedly on FX and crypto, but never audited on a single trended equity-index future in our shop; the banked ON-extreme touch (95.3% vs 90.0%) and IB extension (96.8% vs 91.6%) anomalies are exactly what an overshoot law would predict, which raises the prior that a unifying event-scale structure exists on NQ.
CHEAPEST-FALSIFIER: Frozen spec: on NQ 1-min 2006 -> 2026-05-31 (pre-burn only), build DC series at delta in {0.1,0.2,0.4,0.8,1.6}%, measure (a) mean(omega)/delta with bootstrap CI per era (2006-15 / 16-22 / 23-26), (b) log N(delta) vs log delta slope. PASS = mean(omega)/delta in [0.8,1.2] stable across eras (law transfers); FAIL = era-unstable or far from 1 (FX law does not describe NQ). No trading, no burned data, ~1 day.
INDEPENDENCE: Root of the whole Olsen/Essex lineage (S2-02..08 all descend from this); itself descends from Guillaume et al. 1997 "intrinsic time".
[/LEAD]

[LEAD id=S2-02]
SOURCE: https://github.com/AntonVonGolub/Code (code) + https://doi.org/10.1201/9781315372006-3 (chapter, High-Performance Computing in Finance, 2018; SSRN preprint id 2951348) | ACCESSED: 2026-08-29 | AUTHOR: Anton Golub, James B. Glattfelder, Richard B. Olsen | DATE: 2017 (preprint) / 2018 (chapter)
TYPE: paper + code
CLAIM: "The Alpha Engine" — a parsimonious counter-trend agent that opens/scales positions at DC events and manages inventory using the scaling laws — "yields profitable automated trading strategies" that provide liquidity, with "no a priori restrictions on the amount of assets managed". Full working Java implementation (incl. a limit-order variant) is public, GPL-3.0, 117 stars.
EVIDENCE: audited-code (public implementation) + backtest in chapter. NOTE: exact Sharpe/return figures could NOT be verified this session — SSRN (403), DuckDuckGo (captcha), Bing (no hits), web.archive.org (blocked) all refused; OpenAlex abstract confirms only the qualitative profitability claim. Treat any specific number quoted elsewhere as unverified.
MARKET: 23 FX rates, tick data, 2006-2014 per lineage descriptions. HORIZON: minutes-days, multi-scale (multiple deltas run in parallel).
MECHANISM: Counter-trend liquidity provision sized by event-scale inventory rules: overshoots mean-revert in intrinsic time, so fading DC overshoots with geometric position scaling harvests the spread between event scales.
OBSERVABLES: DC confirmations at several deltas simultaneously, overshoot extent, inventory state, asymmetric up/down thresholds; probability-indicator from the 1-1/e structure (see S2-04).
NOVELTY: POLICY
PRIOR: LOW - on a single trending index future at $25-33/RT all-in, a counter-trend liquidity-provision engine designed for 23-pair FX diversification and near-zero spread very likely dies to costs; the DEAD list (TICK fade, sweep-and-reclaim) already killed cheaper mean-reversion cousins.
CHEAPEST-FALSIFIER: Port the public Java coastline logic (single-delta simplification) to the Python substrate; run on NQ 1-min 2006 -> 2026-05-31 at delta calibrated to >= 1 trade/day; charge $33/RT; gate = net expectancy > 0 AND beats matched always-flat and circular-shift nulls. Expect FAIL; the informative output is at WHICH delta the gross edge peaks, feeding S2-01's structure map.
INDEPENDENCE: Same authors as S2-01; code independently starred/forked but no independent replication with published numbers found this session.
[/LEAD]

[LEAD id=S2-03]
SOURCE: https://arxiv.org/abs/2204.02682 | ACCESSED: 2026-08-29 | AUTHOR: James B. Glattfelder, Anton Golub | DATE: 2022-04-06
TYPE: paper
CLAIM: An analytic relationship links intrinsic (event) time and physical time, and "a novel empirical scaling law is presented, relating to the variability of ... overshoots"; verified on Brownian motion, tick crypto, and tick fiat-FX data.
EVIDENCE: examples (working paper; tri-dataset empirical verification)
MARKET: crypto + FX tick; Brownian control. HORIZON: threshold-dependent intraday.
MECHANISM: If overshoot variability (not just its mean) scales lawfully, the full conditional distribution of post-DC excursions is parameterized by delta alone — a one-parameter family for exits/targets.
OBSERVABLES: per-event overshoot omega, its variance vs delta, DC/OS segment durations; Brownian-motion null values for each (the paper supplies the analytic benchmark — deviations from it are the signal).
NOVELTY: REPRESENTATION
PRIOR: MED - having the exact Brownian null in closed form is precisely our house methodology (matched control in the same wave); cheap to test and self-controlling.
CHEAPEST-FALSIFIER: Same run as S2-01 extended: for each delta record var(omega); compare NQ's (mean, var) overshoot pair against the paper's Brownian-motion analytic values computed on volatility-matched simulated paths (circular-shift preserved). PASS if NQ deviates from Brownian in a stable signed direction (exploitable structure); FAIL if indistinguishable (geometry, like PDH/PDL).
INDEPENDENCE: Olsen lineage (S2-01/02 authors).
[/LEAD]

[LEAD id=S2-04]
SOURCE: https://arxiv.org/abs/2511.14408 | ACCESSED: 2026-08-29 | AUTHOR: Thomas Houweling | DATE: 2025-11-18
TYPE: paper
CLAIM: DC intrinsic time "can be modeled as a memoryless exponential hazard process": the proportion of directional changes to total intrinsic events stabilizes near 1 - 1/e = 0.632, "matching the probability that a Poisson process completes one mean interval", making market activity a renewal process in intrinsic time and 0.632 a heuristic boundary between scaling regimes.
EVIDENCE: examples (single-author working paper; datasets not visible from abstract page)
MARKET: unspecified in abstract (framework-level). HORIZON: all thresholds.
MECHANISM: If event arrivals in intrinsic time are memoryless, duration-since-last-event carries NO information — a structural null for every "time-between-events" timing idea; conversely, pockets where the DC-share leaves 0.632 are non-Poisson pockets, i.e., the only places event-timing edge can live.
OBSERVABLES: rolling DC-share = #DC / (#DC + #OS-events) per threshold; deviation d(t) = DC-share - 0.632; segment durations in intrinsic time.
NOVELTY: REPRESENTATION
PRIOR: MED - as a NULL it is highly credible (consistent with our repeated deaths of timing conditioners); as a SIGNAL (deviation trading) untested anywhere.
CHEAPEST-FALSIFIER: On NQ 1-min pre-burn: compute rolling 250-event DC-share at delta=0.2% and 0.4%; (a) unconditional mean vs 0.632 with block-bootstrap CI; (b) preregister ONE conditional: sessions in top/bottom decile of |d(t)| vs matched unconditional control, next-session RV and 11:48-family-style continuation stats. PASS only if the deviation deciles separate beyond the control; the likeliest outcome (confirms 0.632, no conditional lift) is itself a bankable structural null closing the duration-timing axis cheaply.
INDEPENDENCE: Independent author, but works entirely inside the Olsen DC framework.
[/LEAD]

[LEAD id=S2-05]
SOURCE: https://doi.org/10.1007/s10462-022-10307-0 (Artificial Intelligence Review 56:5619-5644) | ACCESSED: 2026-08-29 (via OpenAlex record; Springer page itself 303-redirects to cookie wall) | AUTHOR: Adesola Adegboye, Michael Kampouridis, Fernando E.B. Otero | DATE: 2022/2023
TYPE: paper
CLAIM: Genetic-algorithm-optimized MULTI-threshold directional-change trading strategies "statistically significantly outperform all DC and non-DC benchmarks in terms of both return and risk" on forex data. Companion result (same group, Int. J. Intelligent Systems 36(12):7609-7640, doi 10.1002/int.22601): across 20 FX pairs x 10 months x 1000 datasets, ML-classified DC trend-reversal prediction "leads to ... higher profit and statistically outperform[s] all other trading strategies" tested.
EVIDENCE: peer-reviewed (backtests with statistical testing; no forward period)
MARKET: FX (20 pairs, 10-min to tick resolutions). HORIZON: intraday-to-daily event horizon.
MECHANISM: Combining several DC thresholds captures trend structure at multiple event scales simultaneously; reversal is predicted from overshoot statistics rather than clock-time indicators.
OBSERVABLES: per-threshold DC state, overshoot-so-far as fraction of delta (OSV), time-adjusted return of DC (TMV), predicted reversal point; GA weights across thresholds.
NOVELTY: REPRESENTATION
PRIOR: MED - one of the few event-time families with consistent cross-author positive results and significance testing, but all FX, spread-only costs, and heavy search (GA/GP -> selection-luck risk is real; their own controls are DC-internal).
CHEAPEST-FALSIFIER: NO learner. Preregister the single fixed rule the family reduces to: at DC confirmation (delta=0.4%) enter WITH the new trend, exit at overshoot = delta or opposite DC, NQ 1-min pre-burn, $33/RT, vs (a) matched always-long control at same timestamps, (b) circular-shift null with shared family draw. If the fixed rule shows nothing, the GA layer is not worth importing (LEVERAGE/SELECTION-LUCK classification), and the axis dies for <2 days' work.
INDEPENDENCE: Essex lineage (Kampouridis is Tsang-adjacent); descends from S2-01 representation.
[/LEAD]

[LEAD id=S2-06]
SOURCE: https://doi.org/10.1109/access.2025.3599677 (IEEE Access 13:151001-151015) | ACCESSED: 2026-08-29 (via OpenAlex record) | AUTHOR: Xinpeng Long, Michael Kampouridis, Panagiotis Kanellopoulos | DATE: 2025
TYPE: paper
CLAIM: The SAME genetic-programming trader run under a directional-change event clock ("GP-DC") vs under physical time achieved "average total return over 18%" across 220 datasets from 10 international markets and "statistically significantly outperforms" the physical-time version and benchmarks.
EVIDENCE: peer-reviewed (large-N backtest, significance-tested; no forward period)
MARKET: 10 international equity markets, 220 datasets, multi-year. HORIZON: daily-ish event horizon.
MECHANISM: Pure representation test — holding the learner fixed and swapping the clock isolates the value of event-time sampling itself, which is exactly the "representation-shifted" question of this wave.
OBSERVABLES: DC-clock-resampled OHLC series; identical GP grammar under both clocks; per-dataset return differential (DC minus physical).
NOVELTY: REPRESENTATION
PRIOR: MED - the clean same-learner/two-clocks design is the strongest published evidence that the CLOCK carries information, not the indicators; equities not futures, and GP still invites selection luck.
CHEAPEST-FALSIFIER: Clock-swap our own dead conditioners: rebuild NR7-style compression and RV-tercile features in DC event counts per session (events/session = activity in intrinsic time) instead of clock-time ranges, NQ 1-min pre-burn, same preregistered gates that killed them. PASS only if the DC-clock version clears the ORIGINAL gate the clock-time version failed; anything less = representation adds nothing here.
INDEPENDENCE: Same Kampouridis lab as S2-05 (not independent of it).
[/LEAD]

[LEAD id=S2-07]
SOURCE: https://doi.org/10.3390/a11110171 (Algorithms 11(11):171, open access; PDF: https://www.mdpi.com/1999-4893/11/11/171/pdf — MDPI HTML page 403'd this session, record verified via OpenAlex) | ACCESSED: 2026-08-29 | AUTHOR: Amer Bakhach, V.L. Raju Chinthalapati, Edward P.K. Tsang, Abdul Rahman El Sayed | DATE: 2018-10-28
TYPE: paper
CLAIM: The "Intelligent Dynamic Backlash Agent" (IDBA) — the Essex backlash DC strategy plus order-sizing and risk-management layers — "generate[s] annualized returns about 30% after deducting the bid and ask spread" on forex, substantially outperforming the original DBA and another DC-based strategy. Sister result (TSFDC, doi 10.1002/isaf.1425, 2018): contrarian DC-forecast strategy beat buy-and-hold and rival DC strategies on 8 FX pairs.
EVIDENCE: peer-reviewed (backtest net of spread only — no commission/impact)
MARKET: FX pairs, tick/minute. HORIZON: hours-days per DC episode.
MECHANISM: "Backlash": after a confirmed DC, price tends to continue to a forecastable overshoot extent; sizing by forecast confidence converts the overshoot law (S2-01) into P&L.
OBSERVABLES: DC confirmation, forecast of overshoot magnitude (their OSV regression), position size schedule, stop at opposite DC.
NOVELTY: POLICY
PRIOR: LOW-MED - 30% ann. on FX net of spread is the single largest audited-lineage number in this domain, but FX spread ~0.5-1bp vs our $33/RT (~1.4bp on NQ at 24k) plus a trending single instrument = most of it should evaporate; worth one shot because the mechanism (overshoot continuation) matches our banked IB-extension anomaly direction.
CHEAPEST-FALSIFIER: Identical run to S2-05's fixed rule but with the IDBA exit (exit at FORECAST overshoot from a rolling pre-burn-trained OSV median, not at delta) — one extra column in the same wave; same nulls, same $33/RT gate. Direct head-to-head answers whether overshoot-forecasting adds anything over the raw law.
INDEPENDENCE: Essex/Tsang lineage; not independent of S2-01/05/08.
[/LEAD]

[LEAD id=S2-08]
SOURCE: https://doi.org/10.1002/isaf.1552 (Intelligent Systems in Accounting, Finance and Management 31(1), 2024) | ACCESSED: 2026-08-29 (via OpenAlex record; Wiley page not fetched) | AUTHOR: Edward P.K. Tsang, Shuai Ma, V.L. Raju Chinthalapati | DATE: 2024
TYPE: paper
CLAIM: "Nowcasting directional change in high frequency FX markets": data-driven methods can recognize a directional change BEFORE its confirmation point in real time — i.e., the pre-confirmation path (partial retracement depth, elapsed intrinsic duration) predicts whether the delta-threshold will complete.
EVIDENCE: examples (peer-reviewed but 1 citation, small study)
MARKET: high-frequency FX. HORIZON: intra-event (minutes).
MECHANISM: If DC completion is predictable mid-flight, the confirmation lag — the DC framework's main cost — can be partially bought back; equivalently, durations/paths between events carry information (direct tension with S2-04's memorylessness claim — testing both at once is a free either-way result).
OBSERVABLES: since-extreme retracement fraction x (0 < x < delta), time-in-retracement, prior overshoot size; label = does retracement reach delta before a new extreme.
NOVELTY: RAW-INFO
PRIOR: MED - it is a well-posed conditional-probability question with a built-in control (unconditional completion rate), and either outcome is informative given S2-04.
CHEAPEST-FALSIFIER: On NQ 1-min pre-burn, delta=0.4%: for every retracement crossing x in {0.25,0.50,0.75}*delta, record P(complete DC | x, elapsed bars) vs the unconditional completion rate at that x (the geometric control — mandatory, cf. PDH/PDL death). PASS = elapsed-time term shifts completion probability beyond the geometric control with stable sign across eras. Feeds directly into whether S2-05/07 entries can be advanced pre-confirmation.
INDEPENDENCE: Tsang lineage (S2-07).
[/LEAD]

[LEAD id=S2-09]
SOURCE: https://www.nber.org/papers/w7613 (published J. Finance 55(4):1705-1765, 2000) | ACCESSED: 2026-08-29 | AUTHOR: Andrew W. Lo, Harry Mamaysky, Jiang Wang | DATE: 2000-03
TYPE: paper
CLAIM: A fully "systematic and automatic approach to technical pattern recognition using nonparametric kernel regression" (smoothed local extrema sequences — i.e., an HH/HL swing-topology automaton) applied to US stocks 1962-1996 finds that "several technical indicators do provide incremental information": conditional return distributions after detected patterns (head-and-shoulders, double bottoms, etc.) differ significantly from unconditional ones.
EVIDENCE: peer-reviewed (the canonical audited swing-topology result; effect = distributional information, NOT demonstrated net trading profit)
MARKET: US individual stocks, daily, 1962-1996. HORIZON: days-weeks.
MECHANISM: Sequences of smoothed swing extrema (the topology, not the levels) encode crowd positioning; patterns are a grammar over the HH/HL/LH/LL alphabet.
OBSERVABLES: kernel-smoothed price, ordered local extrema e1..e5, boolean pattern grammar over extrema, post-pattern k-day return distribution.
NOVELTY: REPRESENTATION
PRIOR: LOW-MED - 26-year-old daily-stock evidence, information not profit, and our sweep-and-reclaim / PDH-PDL deaths show topology-at-levels carries nothing on modern NQ; but a pure extrema-SEQUENCE automaton (levels discarded, order kept) has not been run in-house and is nearly free.
CHEAPEST-FALSIFIER: On NQ RTH 1-min pre-burn: zigzag extrema at 0.3% reversal; encode last 4 extrema as one of {HH-HL, LH-LL, mixed}; compare next-60-min return/RV distribution per state vs matched unconditional control (same timestamps, KS + circular-shift family null). One wave, no learner, kills or promotes the whole swing-automaton axis.
INDEPENDENCE: Fully independent of the Olsen/Essex DC lineage (different formalism, same "event-defined path skeleton" idea).
[/LEAD]

[LEAD id=S2-10]
SOURCE: https://arxiv.org/abs/2608.26158 | ACCESSED: 2026-08-29 | AUTHOR: Muhammad Toheed Fayyaz, Abdul Jabbar, Faheem Ahmad Qureshi, Syed Qaisar Jalil | DATE: 2026-07-07 (arXiv Aug-2026 batch)
TYPE: paper
CLAIM: In a frequency-controlled design (adaptive EMA calibration so every bar type emits the same bar rate; resolution is the only variable), on Binance BTCUSDT perp tick data 2020-2025, "tick Renko bars achieve the smallest random-walk deviation recorded (|VR(4)-1| = 0.020, lag-1 autocorrelation = 0.002)" and tick volatility bars "reduce serial dependence by 69% relative to the minute baseline", across 8 quality metrics and 6 bar types (dollar, volume, volatility, range, Renko, hybrid).
EVIDENCE: examples (working paper; careful matched-frequency controls, no trading P&L)
MARKET: BTCUSDT perpetual futures. HORIZON: bar-construction level (any downstream horizon).
MECHANISM: Sampling in event units (price bricks / volatility / volume) subordinates returns to activity, whitening microstructure autocorrelation and stabilizing variance — the input distribution every downstream model actually sees.
OBSERVABLES: per-bar-type VR(4), lag-1 AC, Ljung-Box, normality stats; bar-frequency matching parameters; brick size for Renko.
NOVELTY: REPRESENTATION
PRIOR: MED - the frequency-matching control is exactly what earlier bar-type folklore (Lopez de Prado's AFML claims) lacked; the honest question for us is whether better-behaved bars move any PREREGISTERED gate, not whether the statistics improve (they will).
CHEAPEST-FALSIFIER: Two stages, pre-burn NQ only. (1) Statistical: build volume bars and Renko bricks from NQ 1-min (2006-2026) and true tick (2025-26 owned), frequency-matched to 1-min; reproduce VR(4)/lag-1/kurtosis table — cheap, no governance risk. (2) Only if (1) reproduces: rerun ONE dead-signal family (RV-tercile conditioning) on volatility-bar sampling under its ORIGINAL gate. Gate unchanged, population predefined; a representation that cannot resurrect a 5.5x-under-MDE corpse under its own gate is banked as "statistics-only".
INDEPENDENCE: Methodologically descends from Lopez de Prado's bar taxonomy (S2-11 lineage); authors independent.
[/LEAD]

[LEAD id=S2-11]
SOURCE: https://doi.org/10.3905/jpm.2012.39.1.019 (J. Portfolio Mgmt 39(1):19-29, 2012; open SSRN preprint doi 10.2139/ssrn.2034858) + https://doi.org/10.1111/0022-1082.00286 (Ané & Geman, J. Finance 55(5):2259-2284, 2000) | ACCESSED: 2026-08-29 (both via OpenAlex records; SSRN page 403'd) | AUTHOR: David Easley, Marcos López de Prado, Maureen O'Hara; Thierry Ané, Hélyette Geman | DATE: 2012 / 2000
TYPE: paper
CLAIM: Easley-LdP-O'Hara: "speed is not the defining characteristic" of HFT — HFTs operate on a VOLUME clock, and low-frequency traders are exploited precisely through structural weaknesses of the chronological clock. Ané-Geman: "normality of asset returns can be recovered through a stochastic time change", with cumulative TRADE COUNT (not volume) as the effective clock (435 citations).
EVIDENCE: peer-reviewed (paradigm papers; Ané-Geman's specific moment-recovery later challenged — see S2-12)
MARKET: US equities/futures microstructure (Volume Clock explicitly discusses E-mini). HORIZON: intraday.
MECHANISM: Information arrives in activity units; the wall clock aliases it, so any signal computed on clock bars competes against agents who see the un-aliased activity series.
OBSERVABLES: cumulative volume, cumulative trade count, bar boundaries in each clock; distributional moments of returns per clock.
NOVELTY: REPRESENTATION
PRIOR: MED for the clock-as-lens (supported by S2-10), LOW for "normality is recovered" (refuted, S2-12).
CHEAPEST-FALSIFIER: On owned 2025-26 NQ tick+BBO: sample returns every N trades and every V contracts (N,V matched to 1-min rate); test excess kurtosis and lag-1 AC vs 1-min bars, plus the Murphy-Izzeldin check (are trade-count-conditioned returns actually Gaussian? expected: no). Pure measurement, one day, calibrates exactly how much (little) the clock swap buys on OUR instrument before any S2-10 stage-2 spend.
INDEPENDENCE: Root lineage Mandelbrot-Taylor (1967) -> Clark (1973) -> Ané-Geman -> Easley/LdP/O'Hara; S2-10 descends from it.
[/LEAD]

[LEAD id=S2-12]
SOURCE: https://arxiv.org/abs/physics/0510007 (published Quant. Finance, 2006) + Murphy & Izzeldin working paper "A Comment on Ané and Geman (2000)" (2005, located via OpenAlex, no DOI) | ACCESSED: 2026-08-29 | AUTHOR: László Gillemot, J. Doyne Farmer, Fabrizio Lillo | DATE: 2005-10-02
TYPE: paper
CLAIM: NEGATIVE CONTROL for the volume clock's information content: "only a small fraction of volatility fluctuations are explained" by volume/transaction time — volatility stays strongly clustered when volume or transaction count is held constant; return distributions conditioned on fixed volume/trade rate keep their heavy tails; "the long-memory of volatility is dominated by factors other than transaction frequency or total trading volume". Murphy-Izzeldin add: "returns conditioned on the recentered number of trades are not Gaussian" — the Ané-Geman recovery fails in replication.
EVIDENCE: peer-reviewed
MARKET: US and LSE equities, transaction-level. HORIZON: intraday-daily.
MECHANISM: Tail risk and clustering are driven by liquidity granularity (gaps in the book), not by the arrival rate that the volume clock removes — so clock-swapping cleans statistics without transferring alpha.
OBSERVABLES: volatility per fixed-volume window, per fixed-trade-count window, conditioned return distributions.
NOVELTY: REPRESENTATION (as a bound on what S2-10/11 can deliver)
PRIOR: HIGH - directly matches our house doctrine (never let a risk-denominator change masquerade as information); predicts S2-10 stage-2 fails.
CHEAPEST-FALSIFIER: Same run as S2-11's falsifier — it IS the matched test of both sides; record the conditional-kurtosis panel as the deliverable, whichever way it lands.
INDEPENDENCE: Farmer/Lillo econophysics school; fully independent of both Olsen lineage and LdP lineage — that independence is why it is the credible referee.
[/LEAD]

[LEAD id=S2-13]
SOURCE: https://arxiv.org/abs/2309.15383 | ACCESSED: 2026-08-29 | AUTHOR: Bing Wu, Xiangzu Han | DATE: 2023-09-27
TYPE: paper
CLAIM: A modified DC threshold-selection technique (decay-coefficient thresholds tuned by Bayesian optimization) plus HMM-based regime-change detection produced "a significant increase in profit and reduction in risk of DC-based trading strategies" on tick-level forex across multiple pairs.
EVIDENCE: examples (arXiv only; no stated OOS split visible from abstract; no numbers in abstract)
MARKET: FX tick, multiple pairs. HORIZON: intraday.
MECHANISM: A fixed delta is wrong across regimes; letting the event threshold adapt to volatility state keeps the event rate (and hence the overshoot law) stationary.
OBSERVABLES: volatility-scaled delta(t), HMM regime state, DC event rate stability.
NOVELTY: MECHANISM-POLICY (adaptive threshold = risk-specification layer on S2-01)
PRIOR: LOW - two stacked tuners (BO + HMM) on FX with no visible holdout is a selection-luck profile; only the underlying idea (delta proportional to regime volatility) is worth keeping.
CHEAPEST-FALSIFIER: Zero new tests. Fold into S2-01's run as one extra variant: delta(t) = c * rolling 20-day ATR% (no optimizer, c fixed in spec) and check whether overshoot-law stability (S2-01 gate) improves vs fixed delta. If adaptive delta does not stabilize the law, the whole adaptive-threshold literature is skippable for NQ.
INDEPENDENCE: Copies Essex/Olsen DC framework; authors otherwise unknown to the lineage.
[/LEAD]

[LEAD id=S2-14]
SOURCE: https://doi.org/10.1016/s0927-5398(97)00006-6 (Engle & Russell, J. Empirical Finance 4(2-3):187-212, 1997; companion Econometrica 66(5):1127-1162, 1998) | ACCESSED: 2026-08-29 (via OpenAlex record) | AUTHOR: Robert F. Engle, Jeffrey R. Russell | DATE: 1997/1998
TYPE: paper
CLAIM: Inter-event durations (quote changes / trades) are strongly clustered and forecastable by the ACD model — "forecasting the frequency of changes in quoted FX prices" — with duration dynamics mirroring GARCH; the follow-on literature (Zhang/Russell/Tsay 2001, JoE 104:179-207, nonlinear ACD, 329 cites) confirms duration predictability is robust across assets.
EVIDENCE: peer-reviewed (foundational; forecastability of DURATIONS is established — profitable trading on it is NOT claimed)
MARKET: FX quotes, NYSE trades, transaction-level. HORIZON: seconds-minutes.
MECHANISM: Information arrival is autocorrelated: short durations breed short durations, and duration innovations lead volatility — so expected-duration is a real-time activity forecast available before the volatility prints.
OBSERVABLES: inter-trade / inter-quote-revision durations, ACD conditional expected duration psi(t), duration surprises (actual/expected), diurnal-adjusted durations.
NOVELTY: RAW-INFO
PRIOR: MED for volatility-forecast value on NQ tick (well-established elsewhere), LOW for direct return prediction (S2-04's memorylessness result applies at DC scale). Tension with S2-04 is the interesting part: ACD says durations cluster in CLOCK time; Houweling says intrinsic-time events are memoryless — both can be true, and the difference is measurable.
CHEAPEST-FALSIFIER: On owned 2025-26 NQ tick: diurnally adjust inter-trade durations; (a) Ljung-Box on adjusted durations (expect massive rejection = clustering present); (b) preregistered conditional: bottom-decile expected-duration (fast-arrival) periods vs matched time-of-day control for next-5-min RV and signed return. RV lift without signed-return lift = risk-specification information only — classify accordingly, do not promote.
INDEPENDENCE: Econometrics lineage, fully independent of Olsen school; VPIN (excluded per brief) is a descendant, this is the clean ancestor.
[/LEAD]

---
COVERAGE NOTE: eras 2000-2018 (S2-01/02/07/09/11/12/14) and 2022-2026 (S2-03/04/05/06/08/10/13) both represented. Path-signature trading was scouted (Futter/Horvath/Wiese arXiv 2308.15135 "Signature Trading", verified 2026-08-29, and Kalsi/Lyons/Perez-Arribas arXiv 1905.00728 optimal execution) but NOT issued as leads: both report framework/synthetic results without concrete audited market OOS statistics in accessible text, failing this wave's "concrete results, not methodology ads" bar. Renko/range-bar GitHub scan (GitHub API, 2026-08-29) found no repo with audited results (best candidates all 0-star hobby scripts) — the S2-10 paper is the only credible renko-family evidence located.
