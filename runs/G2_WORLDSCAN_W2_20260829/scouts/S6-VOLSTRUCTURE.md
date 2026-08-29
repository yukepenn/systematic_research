# S6 INTRADAY VOL-STRUCTURE SCOUT — GENESIS II WORLD SCAN WAVE 2 (2026-08-29)

DOMAIN SUMMARY (3 lines):
Intraday vol structure as TIMING has a deep, replicated academic spine (diurnal U-shape in index futures since Chan-Chan-Karolyi 1991; multiplicative diurnal x daily x stochastic GARCH decomposition with OOS evidence since Engle-Sokalska), a clean second-moment event family (post-FOMC vol crush, peer-reviewed, distinct from our dead pre-FOMC *drift*), and a 2023-26 0DTE-era layer where implied intraday moves are documented as overstated (Perz iron-condor minute-level backtest; Beckmeyer retail-loss ledger) while Brogaard vs Cboe disagree on whether 0DTE flow reshaped realized intraday vol at all — an era-split diurnal-profile test on our own NQ 1-min is the cheapest arbiter. Weakest link found: "lunch compression -> afternoon expansion" exists only as the unconditional U-shape plus halt-market evidence; no published conditional odds table located, so that lead is a power-check-first design. Method note: WebSearch was refused (session budget 200/200 exhausted), so per fallback rules all discovery ran through WebFetch on site-native search/API URLs (Crossref REST API, arXiv export API, Semantic Scholar API, Bing/Mojeek/DDG HTML — the latter three mostly blocked or junk) plus direct site fetches (cboe.com, quantifiableedges.com); SSRN abstract pages 403 hard-block, so SSRN papers were verified through Crossref DOI records (which carry abstracts for several).

---

[LEAD id=S6-01]
SOURCE: Engle & Sokalska (2012), "Forecasting intraday volatility in the US equity market. Multiplicative component GARCH", J. Financial Econometrics, https://doi.org/10.1093/jjfinec/nbr005 (verified via https://api.semanticscholar.org/graph/v1/paper/search?query=forecasting+intraday+volatility+US+equity+multiplicative+component+GARCH); working-paper version Engle, Sokalska & Chanda (2005), https://doi.org/10.2139/ssrn.676248; index-futures confirmation: Rossi & Fantazzini (2009), "Long Memory and Periodicity in Intraday Volatility of Stock Index Futures", https://doi.org/10.2139/ssrn.1460625 (E-mini S&P 500 hourly; abstract verified via https://api.crossref.org/works/10.2139/ssrn.1460625) | ACCESSED: 2026-08-29 | AUTHOR: R. Engle, M. Sokalska; E. Rossi, D. Fantazzini | DATE: 2012 / 2005 / 2009
TYPE: paper
CLAIM: Intraday conditional variance is well described as (daily component) x (deterministic diurnal periodic component) x (intraday stochastic GARCH), and forecasting deseasonalized intraday vol with this decomposition works out-of-sample on US equities; on E-mini S&P 500 hourly returns the seasonal pattern is strong, statistically significant, and long-memory persistent (periodic EGARCH).
EVIDENCE: peer-reviewed (Engle-Sokalska JFEC with OOS evaluation; Rossi-Fantazzini SSRN preprint on E-mini)
MARKET: US equities (10-min), E-mini S&P 500 (hourly) HORIZON: next 10-60 min to rest-of-session
MECHANISM: Vol has a deterministic clock (open/close auctions, macro release times, global session handoffs); conditioning on raw RV without removing the clock mixes phase with state and destroys forecast power.
OBSERVABLES: NQ 1-min squared returns by minute-of-session; frozen diurnal profile (median |ret| per minute, train era); deseasonalized RV_t = RV_t / diurnal_t; daily component = prior-day RV or HAR.
NOVELTY: REPRESENTATION
PRIOR: MED — decomposition itself is HIGH-replicated; conversion to a *timing* edge net of $33/RT is unproven, and our day-level RV terciles were 5.5x under MDE (this is phase-conditional, a different object, but the power lesson stands).
CHEAPEST-FALSIFIER: Fit diurnal profile on NQ 1-min 2006-2019 (frozen); OOS 2020->pre-burn: does deseasonalized first-60-min vol forecast rest-of-day RV better than (a) raw first-60-min RV and (b) prior-day RV, circular-shift null, MDE computed before looking? Fail = no incremental OOS R2 over both controls.
INDEPENDENCE: none (primary literature)
[/LEAD]

[LEAD id=S6-02]
SOURCE: Fernandez-Perez, Frijns & Tourani-Rad (2017), "When no news is good news — The decrease in investor fear after the FOMC announcement", Journal of Empirical Finance 41:187-199, https://doi.org/10.1016/j.jempfin.2016.07.013 (record verified via https://api.crossref.org/works/10.1016/j.jempfin.2016.07.013; SSRN 2014 version https://doi.org/10.2139/ssrn.2525991) | ACCESSED: 2026-08-29 | AUTHOR: A. Fernandez-Perez, B. Frijns, A. Tourani-Rad | DATE: 2017 (SSRN 2014)
TYPE: paper
CLAIM: The VIX (investor fear) decreases significantly after scheduled FOMC announcements — resolution of uncertainty produces a systematic post-announcement implied/realized vol contraction concentrated in the announcement aftermath, regardless of the direction of the policy surprise.
EVIDENCE: peer-reviewed (abstract text not retrievable through Crossref; magnitude figures not re-verified this session — treat magnitudes as unquoted)
MARKET: VIX / SPX options; transfers to index futures RV HORIZON: 14:00 ET announcement -> close, FOMC days (8/yr)
MECHANISM: Scheduled binary uncertainty resolves at a known clock time; vol priced for the event exits immediately after, so second-moment (not first-moment) behavior is the predictable object.
OBSERVABLES: FOMC announcement dates/times 2006-2026 (public calendar); NQ 1-min RV in 14:00-15:30 vs matched window on matched non-FOMC weekdays; certified VIX daily close-to-close change on FOMC vs non-FOMC days.
NOVELTY: RAW-INFO (event-clocked second-moment state) + POLICY (post-14:00 FOMC: suppress breakout/expansion entries, favor contraction-consistent tactics)
PRIOR: MED-HIGH the RV contraction exists on NQ; MED that any NQ-only policy clears $33/RT — N is ~160 events over 20y, so gate MDE first (the macro-surprise N-bound lesson applies: ~8/yr events are power-hungry).
CHEAPEST-FALSIFIER: One frozen table: NQ RV(14:05-15:30)/RV(12:00-13:30) ratio on FOMC days vs the same ratio on all matched Tue/Wed non-FOMC days 2006-2026, one shared circular-shift null per family; secondary: certified VIX daily ΔVIX on FOMC days. Distinct from dead pre-FOMC *drift* (first moment); if the contraction ratio is not separated from control at pre-set MDE, record dead.
INDEPENDENCE: none (primary literature)
[/LEAD]

[LEAD id=S6-03]
SOURCE: Donninger (2015), "Trading the Patience of Mrs. Yellen. A Short Vix-Futures Strategy for FOMC Announcement Days", https://doi.org/10.2139/ssrn.2544445 (abstract verified via https://api.crossref.org/works/10.2139/ssrn.2544445) | ACCESSED: 2026-08-29 | AUTHOR: Chrilly Donninger | DATE: 2015
TYPE: paper (practitioner working paper, Sir-Bondalot series)
CLAIM: Because "the VIX and VIX-Futures decrease significantly after the announcements of the meeting" (his words, citing the S6-02 literature), a rule that shorts VX futures on FOMC announcement day and covers after the announcement is profitable as a standalone overlay.
EVIDENCE: examples (paper contains a backtest; performance figures not retrievable through Crossref metadata — unaudited practitioner backtest)
MARKET: VX futures HORIZON: intraday-to-1-day, FOMC days only
MECHANISM: Same uncertainty-resolution vol crush as S6-02, expressed directly in the vol instrument rather than via delta-one RV.
OBSERVABLES: Certified VX daily settles + FOMC calendar: FOMC-day close-to-close ΔVX distribution vs non-FOMC days; sign consistency by year 2013-2026.
NOVELTY: POLICY
PRIOR: MED for sign on VX daily; LOW as a directly executable object for this program (we trade NQ, and VX execution is out of campaign scope) — value is as a certified-daily-data confirmation layer for the S6-02 NQ policy.
CHEAPEST-FALSIFIER: Certified VX daily: mean/median FOMC-day ΔVX vs matched non-FOMC weekday ΔVX, all available history, one table, sign + MDE gate. If VX shows no FOMC-day contraction on our own certified data, both S6-02's policy leg and this lead die together cheaply.
INDEPENDENCE: explicitly builds on the VIX-decline literature (Fernandez-Perez et al lineage) — not independent of S6-02.
[/LEAD]

[LEAD id=S6-04]
SOURCE: Perz (2026), "Profitability of Selected 0DTE index options strategies", https://doi.org/10.2139/ssrn.7162898 (abstract verified via https://api.crossref.org/works?query.bibliographic=Retail+Traders+Love+0DTE+Options — same Crossref result set); Beckmeyer, Branger & Gayda (2023), "Retail Traders Love 0DTE Options... But Should They?", https://doi.org/10.2139/ssrn.4404704 (abstract via same Crossref query; SSRN page itself 403) | ACCESSED: 2026-08-29 | AUTHOR: P. Perz; H. Beckmeyer, N. Branger, L. Gayda | DATE: 2026 / 2023
TYPE: paper
CLAIM: SPX 0DTE implied volatility systematically overstates realized intraday volatility: Perz tests iron-condor variants on 12 months of minute-level SPX 0DTE data, finds both variants profitable and "confirmed the existence of the phenomenon of overstatement of implied volatility" vs realized; Beckmeyer et al find >75% of retail SPX option trades are 0DTE and retail sustains substantial losses (i.e., the short-premium side collects).
EVIDENCE: examples (minute-level backtest in Perz preprint; large transaction-level dataset in Beckmeyer; neither peer-reviewed yet)
MARKET: SPX 0DTE options, 2022-2026 era HORIZON: open -> same-day close
MECHANISM: Retail lottery demand for same-day options bids intraday IV above fair variance; the overstated opening implied move is the sellable object.
OBSERVABLES: We own no options data, so the futures-shadow observables are: certified VIX/VXN daily close -> next-day expected 1-day sigma; NQ realized RTH range/RV vs that sigma; frequency and stability of P(realized < k*sigma); behavior of NQ after touching +/-1 implied-sigma late in the session.
NOVELTY: POLICY (futures-shadow: after 14:00, fade extensions beyond the VXN-implied 1-day sigma instead of chasing them; sizing gate keyed to implied-vs-realized gap)
PRIOR: MED — the IV-overstatement evidence is real and recent, but a futures-only expression captures just the residual RV-undershoot shadow, and our dead list warns that late-day fade families (TICK fade, sweep-reclaim) have died at gates; the implied-sigma conditioning is the materially new observable.
CHEAPEST-FALSIFIER: NQ 1-min + certified VXN daily 2006-2026: (1) P(RTH range < VXN-implied 1-day sigma) by era; (2) conditional on price beyond +/-1 sigma at 14:00 ET, distribution of 14:00->close continuation vs reversion, against the matched unconditional 14:00->close control in the same wave. Net-of-$33/RT expectancy gate preregistered. Fail = beyond-sigma state carries no reversion information over control.
INDEPENDENCE: Perz and Beckmeyer are independent teams; both are 0DTE-era literature, not copied from each other.
[/LEAD]

[LEAD id=S6-05]
SOURCE: Brogaard, Han & Won (2023), "Does 0DTE Options Trading Increase Volatility?", https://doi.org/10.2139/ssrn.4426358 (abstract verified via Crossref result set, same query as S6-04) — versus Cboe, Mandy Xu (2023-09-08), "Volatility Insights: Evaluating the Market Impact of SPX 0DTE Options", https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/ (visited, full stats extracted) | ACCESSED: 2026-08-29 | AUTHOR: J. Brogaard, J. Han, P.Y. Won; M. Xu (Cboe) | DATE: 2023
TYPE: paper + vendor
CLAIM: Direct contradiction in print about whether the 0DTE era changed intraday vol structure. Brogaard et al: increased 0DTE trading raises intraday volatility, driven by speculative retail flow. Cboe/Xu: no distortion — 0DTE is ~43-50% of SPX volume (~$500bn notional/day, >1.23M contracts), yet MM net gamma is only $170-670mm (0.04-0.17% of S&P futures liquidity), the close-to-close minus intraday vol spread is 2.7 vol pts (equal to its 10-yr average), and there is no rise in 2-sigma intraday moves or final-hour vol.
EVIDENCE: examples (Brogaard: panel regressions, preprint) / vendor (Cboe: concrete published statistics, conflicted party)
MARKET: SPX/ES complex, 2016-2023 HORIZON: structural (era regime), expressed intraday
CLAIM-NOVELTY note: for us this is not "trade 0DTE" — it is "did the NQ diurnal vol profile structurally shift after daily expirations launched (May 2022), and must every intraday vol gate be era-split?"
MECHANISM: If 0DTE hedging flow is material, MM gamma turns vol into a function of strike geography and expiry clock (pinning into 16:00, expansion after opening range sets); if Cboe is right, pre-2022 diurnal profiles still transfer.
OBSERVABLES: NQ 1-min RV by minute-of-session, era-split 2016-2019 vs 2023-2026 pre-burn; share of daily RV in 09:30-10:30, 14:00-16:00, last 30 min; frequency of 2-sigma 30-min moves by era.
NOVELTY: REPRESENTATION (era-aware diurnal profile; decides whether 2006-2022 vol-structure statistics are even admissible priors for 2023+ NQ)
PRIOR: MED — someone is wrong in print; either answer is decision-relevant for every other S6 lead.
CHEAPEST-FALSIFIER: One frozen table on owned NQ 1-min: minute-of-session RV profile and last-30-min RV share, 2016-2019 vs 2023-2026, structural-break test at 2022-05 (daily-expiry launch), shared null. Cheap, no new data, and it re-prices the transferability of S6-01/-06 profiles.
INDEPENDENCE: Brogaard academic vs Cboe in-house (Cboe has a commercial interest in "no impact" — treat as conflicted vendor).
[/LEAD]

[LEAD id=S6-06]
SOURCE: Chan, Chan & Karolyi (1991), "Intraday Volatility in the Stock Index and Stock Index Futures Markets", Review of Financial Studies 4(4):657-684, https://doi.org/10.1093/rfs/4.4.657 (record verified via https://api.crossref.org/works?query.bibliographic=lunch+effect+intraday+volatility+stock+index); supporting: Ito & Lin (1992), "Lunch break and intraday volatility of stock returns", Economics Letters, https://doi.org/10.1016/0165-1765(92)90106-9; Andersen & Bollerslev (1997), "Intraday periodicity and volatility persistence in financial markets", J. Empirical Finance, https://doi.org/10.1016/s0927-5398(97)00004-2 | ACCESSED: 2026-08-29 | AUTHOR: K. Chan, K.C. Chan, G.A. Karolyi; T. Ito, W-L. Lin; T.G. Andersen, T. Bollerslev | DATE: 1991 / 1992 / 1997
TYPE: paper
CLAIM: Intraday volatility in S&P index and index futures follows a persistent U-shape — elevated at the open, trough at midday, rising into the close — and this periodicity is strong enough that ignoring it distorts all intraday vol persistence estimates (Andersen-Bollerslev). Ito-Lin show the lunch-break vol drop is partly trading-halt-mechanical (Tokyo), implying the US midday trough is behavioral/flow-driven rather than mechanical.
EVIDENCE: peer-reviewed (RFS / Econ Letters / JEF)
MARKET: S&P 500 index + futures (1980s), FX and equities (1990s) HORIZON: phase-of-session
MECHANISM: Institutional order flow clusters at open/close (information + benchmark/rebalancing flow); midday is flow-starved, so vol troughs — but the OPEN QUESTION we would actually trade is whether an abnormally deep lunch trough predicts an abnormally large afternoon expansion, and no published conditional odds table was found this session (searched Quantpedia native search, Quantifiable Edges archive, Crossref) — the unconditional shape is HIGH-confidence, the conditional claim is unsourced folklore.
OBSERVABLES: NQ 1-min RV 12:00-13:30 (lunch), diurnal-adjusted z of lunch RV; PM expansion ratio RV(13:30-16:00)/diurnal expectation; matched unconditional control in same wave.
NOVELTY: REPRESENTATION (phase-conditional vol state, not day-level RV terciles)
PRIOR: LOW-MED — pattern existence HIGH, but the tradable conditional version is exactly the shape of thing our dead list punishes (RV terciles 5.5x under MDE; NR7 wrong direction). MDE must be computed before the table is looked at.
CHEAPEST-FALSIFIER: Frozen two-way table on NQ 1-min 2006-2026: lunch diurnal-adjusted RV quintile vs PM expansion ratio, WITH the matched unconditional PM-expansion control in the same wave, circular-shift null, preregistered MDE. If conditional PM expansion odds do not separate from the unconditional diurnal expectation, record dead and ban the folklore version permanently.
INDEPENDENCE: none (primary literature); conditional-version folklore circulates in trader spaces with no stats found — flagged as unsourced.
[/LEAD]

[LEAD id=S6-07]
SOURCE: Martens (2002), "Measuring and forecasting S&P 500 index-futures volatility using high-frequency data", Journal of Futures Markets, https://doi.org/10.1002/fut.10016; Noh & Kim (2006), "Forecasting volatility of futures market: the S&P 500 and FTSE 100 futures using high frequency returns and implied volatility", Applied Economics, https://doi.org/10.1080/00036840500391229 (both verified via https://api.crossref.org/works?query.bibliographic=Measuring+and+forecasting+S%26P+500+index+futures+volatility+using+high-frequency+data+Martens) | ACCESSED: 2026-08-29 | AUTHOR: M. Martens; J. Noh, T-H. Kim | DATE: 2002 / 2006
TYPE: paper
CLAIM: Realized measures built from intraday index-futures returns materially improve daily volatility forecasts over daily-return GARCH on S&P 500 futures; implied volatility contributes additional forecast information on S&P 500 and FTSE 100 futures.
EVIDENCE: peer-reviewed (both with out-of-sample forecast comparisons)
MARKET: S&P 500 futures (1990s data), FTSE 100 futures HORIZON: next-day vol
MECHANISM: Intraday sampling shrinks measurement error in the vol state variable; a less noisy state improves any downstream vol-conditioned decision.
OBSERVABLES: NQ 1-min RV -> HAR forecast of next-day RV; benchmark GARCH(1,1) on daily returns; certified VIX/VXN daily as the implied-vol add-on regressor.
NOVELTY: REPRESENTATION (a sharper vol gate — explicitly RISK SPECIFICATION, not information alpha; must be classified as such under §4)
PRIOR: HIGH for the forecast improvement (one of the most replicated results in financial econometrics); MED for any net policy value — a better vol forecast only pays if some gate currently binds on a noisy vol estimate.
CHEAPEST-FALSIFIER: NQ 2006-2026: OOS QLIKE/RMSE of HAR-RV(1-min) vs daily GARCH(1,1), VXN add-on tested last; then one preregistered application — regate the live 11:48 morning-continuation shadow's vol filter (if any) with HAR state vs raw prior-day RV and compare net expectancy. If HAR does not beat GARCH OOS on NQ, the entire "better vol clock" family deprioritizes.
INDEPENDENCE: none (primary literature)
[/LEAD]

[LEAD id=S6-08]
SOURCE: Zhang, Zhang, Cucuringu & Qian (2022), "Volatility forecasting with machine learning and intraday commonality", arXiv:2202.08962, https://arxiv.org/abs/2202.08962 (verified via arXiv export API http://export.arxiv.org/api/query?search_query=all:%22intraday+volatility%22+AND+all:%22forecasting%22) | ACCESSED: 2026-08-29 | AUTHOR: C. Zhang, Y. Zhang, M. Cucuringu, Z. Qian | DATE: 2022 (v2)
TYPE: paper
CLAIM: Intraday realized-volatility forecasts improve significantly when models exploit commonality across assets and include market-wide volatility proxies, beyond each asset's own history — neural nets and pooled models beat single-asset benchmarks for intraday RV.
EVIDENCE: peer-reviewed (published version in a quant finance journal; OOS panel evaluation on US equities)
MARKET: US large-cap equities, intraday RV HORIZON: next intraday interval (minutes-hours)
MECHANISM: Index-level vol shocks propagate to every member with a lag/shrinkage structure; cross-sectional pooling denoises the common component faster than any single series reveals it.
OBSERVABLES: ES/RTY/YM 1-min RV (owned 2022+) first-30-min and rolling 30-min; NQ rest-of-day RV; internals minute data 2022+ as market-wide proxy.
NOVELTY: RAW-INFO (cross-market vol information into an NQ vol state — information the NQ series alone does not carry)
PRIOR: MED — commonality in vol is robust; the question is whether ES/RTY/YM add anything BEYOND NQ's own intraday RV (correlations ~0.9+, so the incremental channel is narrow) and whether any gate downstream monetizes it.
CHEAPEST-FALSIFIER: 2022->pre-burn owned 1-min: regress NQ rest-of-day RV on NQ first-30-min RV alone vs + ES/RTY/YM first-30-min RV (and TICK/ADD minute internals), OOS by year, shared null; require preregistered incremental R2 MDE. Fail = cross-market terms add nothing after NQ's own state.
INDEPENDENCE: none (primary literature)
[/LEAD]

[LEAD id=S6-09]
SOURCE: Baltussen, Da, Lammers & Martens (2021), "Hedging demand and market intraday momentum", Journal of Financial Economics 142(1):377-403, https://doi.org/10.1016/j.jfineco.2021.04.029 (record verified via https://api.crossref.org/works/10.1016/j.jfineco.2021.04.029; abstract not retrievable through Crossref — findings characterized from title, reference structure, and known JFE publication) | ACCESSED: 2026-08-29 | AUTHOR: G. Baltussen, Z. Da, S. Lammers, M. Martens | DATE: 2021
TYPE: paper
CLAIM: Late-day index-futures momentum (day's return predicting the last half-hour) is driven by mechanical hedging/rebalancing demand — leveraged-ETF rebalancing and option-hedging flows that scale with the SIZE of the day's move — i.e., the effect is a flow phenomenon concentrated on large-|move| (high-vol) days, not a uniform return pattern.
EVIDENCE: peer-reviewed (JFE)
MARKET: S&P 500 futures + international index futures HORIZON: ~15:30 -> 16:00 ET
MECHANISM: Leveraged ETFs must rebalance in the direction of the day's move before the close, and the required flow is proportional to (daily return) x (AUM x leverage) — a vol-scaled, sign-following, clock-anchored demand.
OBSERVABLES: NQ return 09:30->15:30 (sign and magnitude terciles); last-30-min NQ return; era split at leveraged-ETF AUM growth (and 2022+ 0DTE hedging era).
NOVELTY: POLICY (trade only the interaction: sign x large-|move| tercile x 15:30 clock), flagged adjacent-to-dead
PRIOR: LOW-MED — in-house "Gao half-hour geometry" is DEAD, and this is its descendant. The materially different observable required by the dead-list rule is the |move|-scaled hedging-demand interaction (flow mechanism), not the bare first-half-hour return. If the interaction term does not carry the effect on modern NQ, this whole branch is closed for good.
CHEAPEST-FALSIFIER: NQ 1-min 2006-2026: last-30-min return regressed on sign(09:30->15:30 return) x |return| tercile, era-split pre/post-2018 and pre/post-2022, against BOTH always-flat and the unconditional (already-dead) Gao specification in the same wave; require the interaction, not the base term, to be the carrier at preregistered MDE net of $33/RT.
INDEPENDENCE: Successor to Gao/Han/Li/Zhou "Market Intraday Momentum" (SSRN 2440866 — same Crossref result set) — mechanism paper, not copied from trader sources.
[/LEAD]

[LEAD id=S6-10]
SOURCE: Martins, Virbickaite, Nguyen & Lopes (2026), "Volume-Driven Time-of-Day Effects in Intraday Volatility Models", https://doi.org/10.2139/ssrn.5795584 (record verified via https://api.crossref.org/works/10.2139/ssrn.5795584; abstract not carried in Crossref — title-level claim only); adjacent evidence: Kearney, Shang & Zhao (2023), "Intraday FX Volatility-Curve Forecasting with Functional GARCH Approaches", arXiv:2311.18477, https://arxiv.org/abs/2311.18477 (functional models of the whole intraday vol curve improve forecasts, FX) | ACCESSED: 2026-08-29 | AUTHOR: I.F.B. Martins, A. Virbickaite, H. Nguyen, H.F. Lopes; F. Kearney, H.L. Shang, Y. Zhao | DATE: 2026 / 2023
TYPE: paper
CLAIM: The time-of-day pattern in intraday volatility is substantially volume-driven, and intraday vol models improve when the diurnal effect is tied to (or the clock is deformed by) volume rather than calendar minutes; functionally modeling the entire intraday vol curve (rather than pointwise vol) improves day-ahead intraday forecasts.
EVIDENCE: examples (2026 SSRN preprint, title-level only through Crossref; Kearney et al arXiv with OOS forecast comparisons on FX)
MARKET: equities/FX intraday HORIZON: phase-of-session, day-ahead intraday curve
MECHANISM: Vol per unit of volume is far more stationary than vol per unit of clock time; a volume clock removes the deterministic diurnal component and makes "abnormal" vol states identifiable in real time.
OBSERVABLES: NQ 1-min volume (owned, full history); cumulative-volume session phase; banked structural stats (IB extension 96.8%, ON-extreme touch 95.3%) recomputed in volume-time.
NOVELTY: REPRESENTATION (volume-time as the vol clock — a representation shift squarely in this wave's mandate)
PRIOR: LOW-MED — clock deformation is classic (Ané-Geman lineage) and cheap to test, but it must beat the calendar-time diurnal profile of S6-01, which already absorbs most of the same structure.
CHEAPEST-FALSIFIER: Recompute the S6-01 falsifier with volume-time bucketing instead of minute-of-session on the same frozen eras: if volume-time deseasonalization does not beat calendar-time deseasonalization OOS for rest-of-day RV (same MDE, same null), the representation adds nothing here and is recorded dead in one run.
INDEPENDENCE: Kearney et al independent of Martins et al; both independent of Engle-Sokalska lineage in method though not in spirit.
[/LEAD]
