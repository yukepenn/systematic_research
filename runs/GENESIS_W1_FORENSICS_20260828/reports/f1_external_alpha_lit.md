# F1 — External Literature: Predictability in Equity Index Futures (NQ/ES class), Intraday-to-Weekly Horizons

**PROJECT GENESIS · TEAM F1 · 2026-08-28**

## 0. Method and evidence-status convention

- The session's WebSearch budget was already exhausted (200/200) before this task began. All verification was done by direct WebFetch of open metadata APIs: **Crossref REST API** (api.crossref.org), **Semantic Scholar Graph API** (api.semanticscholar.org), **arXiv export API**, and **IDEAS/RePEc** article pages. SSRN, NY Fed, Alpha Architect, and Quantpedia block anonymous fetches (403/500).
- **RAW FACT** = I fetched the paper's metadata/abstract from a primary index THIS session and the number/claim quoted appears in that fetched text.
- **RECORDED CLAIM** = standard literature knowledge or a detail (e.g., an in-text number not in the abstract) that I could not re-verify this session. These are flagged and should be re-verified before any figure is used in a spec.
- No repository file was opened for this task except CLAUDE.md context supplied by the environment; no repo writes; no CrossTrade calls; no data reads.

---

## 1. Intraday momentum (first half-hour → last half-hour)

**Anchor paper (RAW FACT, abstract verbatim via ideas.repec.org/a/eee/jfinec/v129y2018i2p394-414.html):**
Gao, Han, Li, Zhou, "Market Intraday Momentum," *Journal of Financial Economics* 2018 (DOI 10.1016/j.jfineco.2018.05.009; 207 citations per Crossref). Sample: **SPY high-frequency data 1993–2013**. Claim: "the first half-hour return on the market as measured from the previous day's market close predicts the last half-hour return. This predictability … is stronger on more volatile days, on higher volume days, on recession days, and on major macroeconomic news release days." Also present in ten other liquid ETFs (incl. QQQ). Mechanisms named in the abstract: Bogousslavsky (2016) infrequent portfolio rebalancing, and late-informed trading near the close.
- RECORDED CLAIM (in-text, not re-verified): predictive R² ≈ 1.6–2.6%; a timing strategy (trade last half-hour in the sign of the first half-hour) earns ~6.5%/yr with Sharpe ≈ 1 before costs; win rate ~54–57%.

**Mechanism paper (RAW FACT via Crossref):** Baltussen, Da, Lammers, Martens, "Hedging Demand and Market Intraday Momentum," *JFE* Oct 2021 (DOI 10.1016/j.jfineco.2021.04.029; 94 citations). **60+ futures across asset classes, 1974–2020.** Abstract (working-paper version): "hedging short gamma exposure requires trading in the direction of price movements, thereby creating price momentum"; significant intraday predictability that **reverts within days**; attributed to gamma hedging by option market makers and leveraged-ETF rebalancing. This is the best mechanism-anchored intraday result in the entire literature for index futures.

**International out-of-sample replication (RAW FACT via Crossref):** Li, Sakkas, Urquhart, "Intraday Time Series Momentum: Global Evidence and Links to Market Characteristics," *Journal of Financial Markets* 2022 (DOI 10.1016/j.finmar.2021.100619; 20 citations): ITSM "economically sizable and statistically significant both in- and out-of-sample in most countries" across **16 developed markets**; strengthens with **low liquidity, high volatility, discrete information events**. Also Jin, Kearney, Li, Yang (China, SSRN 3493927): first half-hour predicts last half-hour "across all four futures" (RAW FACT via Crossref abstract).

**Post-publication decay — the critical new evidence (RAW FACT via Crossref):** Paz, "Out-of-Sample Evaluation of an Intraday Momentum Strategy for the S&P 500 ETF (SPY)," 2026, DOI 10.2139/ssrn.7290621. Replicates a 1-minute SPY intraday momentum strategy (evidently the Zarattini/Aziz 2024 variant — RECORDED CLAIM): **in-sample Sharpe 1.34 (2015–2024) confirmed; out-of-sample May 2024–Mar 2026: total return 9.4% vs 29.5% buy-and-hold, Sharpe 0.39**. Candidate causes named: microstructure change, 0DTE options growth.

**Directly-on-NQ falsification study (RAW FACT via arXiv API):** Mesfin, "Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures: A Systematic Falsification Study," arXiv 2605.04004 (May 2026, rev. Jul 2026). **14 signal families, 5-minute MNQ, 947 trading days 2021–2025**; gates: walk-forward, t ≥ 2.0, ≥30 trades, positive net of a 2-point friction assumption. Headline: gross returns of the signal families ranged ~**0.07–1.50 points per trade, below the 2-point assumed friction**; "no strategies met all requirements," though two signals ("RTH Confluence," "London Session Signal B") are described as passing validation — the abstract is internally tense and the paper should be read before citing either half. Single-author preprint; quality unaudited.

**GENESIS classification:** empirical result (top-journal, replicated internationally OOS) + theoretical mechanism (gamma/rebalancing flows) + documented post-2024 decay in the naive form. The *conditioning* facts (works on high-vol/high-volume/news days) are implementation clues.

---

## 2. Overnight vs intraday split; overnight drift

**Tug of war (RAW FACT via Crossref):** Lou, Polk, Skouras, "A Tug of War: Overnight versus Intraday Expected Returns," *JFE* 2019 (DOI 10.1016/j.jfineco.2019.03.011; 307 citations). (Abstract not served; RECORDED CLAIM: essentially all abnormal returns to momentum stocks accrue overnight, value's accrue intraday; institutional vs retail clientele mechanism.)

**Equity premium accrues overnight (RAW FACT via Crossref abstract):** Cliff, Cooper, Gulen, "Return Differences between Trading and Non-Trading Hours: Like Night and Day" (SSRN 1004081, 2008): "the US equity premium over the last decade is solely due to overnight returns … returns during the day are close to zero and sometimes negative," and the effect "persists across stocks, indexes, and futures." Kelly & Clark, *J. Asset Management* 2011 (DOI 10.1057/jam.2011.2) same direction.

**Overnight drift (RAW FACT via Crossref/S2):** Boyarchenko, Larsen, Whelan, "The Overnight Drift," *Review of Financial Studies* 2023 (DOI 10.1093/rfs/hhad020; 18 citations): large positive U.S. equity **futures** returns concentrated during **European opening hours**, strongly related to **order imbalances at the preceding U.S. close**, asymmetric response to demand shocks (inventory-risk/liquidity-provision mechanism).

**Post-publication death (RAW FACT via S2 + Crossref, abstract verbatim):** Boyarchenko, Larsen, Whelan, "The Disappearing Overnight Drift," Liberty Street Economics, 2026 (DOI 10.59576/lse.20260701): the **2:00–3:00 a.m. ET window that previously generated ~3.7% per annum has averaged close to zero since 2021**. The authors themselves examine which channel (closing order-imbalance dispersion, return variance, liquidity-provider risk capacity) explains the fade.

**GENESIS classification:** the overnight/intraday *split* is a robust structural empirical result; the tradable 2–3 a.m. *drift* is an empirical result now with **author-documented post-publication death**. Session-structure conditioning (where in the 18:00–17:00 ET session returns/variance concentrate) remains an implementation clue.

---

## 3. Time-series momentum, daily/weekly, post-2012

**Original (RAW FACT via Crossref):** Moskowitz, Ooi, Pedersen, "Time Series Momentum," *JFE* 2012 (DOI 10.1016/j.jfineco.2011.11.003; 1,244 citations). Precursor abstract ("Trends," SSRN 1573209): significant trends in **58 liquid futures** (equity index, FX, commodities, bonds), persistence at **1–12 months then partial reversal**.

**Existence critique (RAW FACT via Crossref):** Huang, Li, Wang, Zhou, "Time Series Momentum: Is It There?" *JFE* 2020 (DOI 10.1016/j.jfineco.2019.08.004; 119 citations) — argues much of pooled TSMOM t-stat power comes from unconditional mean returns rather than genuine time-series predictability at the individual-asset level.

**Post-2012 performance:** RECORDED CLAIM (not re-verifiable this session — SSRN/AQR blocked): diversified trend (SG Trend/CTA indices) was roughly flat 2011–2019; AQR's "You Can't Always Trend When You Want" (Babu et al.) attributes this to smaller absolute market moves rather than crowding; equity-index TSMOM specifically is among the weakest sleeves, and 12-month TSMOM on US equity indices had a lost decade post-publication. Georgopoulou & Wang (SSRN 2618243, RAW FACT abstract) already note central-bank-era distortions challenging TSMOM portfolios.

**GENESIS classification:** empirical result at 1–12-month horizons for diversified *cross-asset* baskets; for a **single equity index at daily/weekly horizon it is weak, contested (Huang et al.), and post-publication-degraded**. Not a primary NQ seed.

---

## 4. Opening-range breakout (ORB)

- Holmberg, Lönnbark, Lundström, "Assessing the Profitability of Intraday Opening Range Breakout Strategies," *Finance Research Letters* 2013 (DOI 10.1016/j.frl.2012.09.001; 33 citations) — RAW FACT existence; RECORDED CLAIM: US crude futures, profitable in earlier sample, profitability declines toward the end of sample.
- Tsai et al., "Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets," *IEEE Access* 2019 (DOI 10.1109/access.2019.2899177; 19 citations) — RAW FACT existence (Taiwan index futures; RECORDED CLAIM).
- Zarattini & Aziz, "Can Day Trading Really Be Profitable?" (SSRN 4416622, 2023) — RAW FACT abstract via Crossref: 5-min ORB on QQQ **2016–2023, "33% annualized alpha,"** TQQQ variant 1,484% vs 169% buy-and-hold. Companion papers: VWAP "Holy Grail" (SSRN 4631351: "671% QQQ / 8,242% TQQQ, 2018–2023"), "A Profitable Day Trading Strategy for the U.S. Equity Market" (SSRN 4729284, 2024: 5-min ORB on 7,000+ stocks-in-play, "1,600% total net," 36% ann. alpha).
- Counterweights: the **MNQ OHLCV falsification study** (§1) finds no ORB-family 5-min signal survives a 2-point friction on MNQ 2021–2025 (RAW FACT); Paz 2026 shows the sibling Zarattini intraday-momentum SPY strategy collapsing OOS after May 2024 (RAW FACT); Chuk (SSRN 6355218, 2026, RAW FACT abstract) finds SPY 0DTE ORB "profitability margin remains fragile."
- **GENESIS classification:** the Zarattini series is **practitioner marketing-adjacent** (un-refereed, leverage-amplified headline numbers, costs favorable); the refereed ORB literature is thin and shows decay. Treat ORB as an *hypothesis frame* (breakout-with-trend-day conditioning), not as supported alpha.

---

## 5. Intraday mean reversion after large moves

- Grant, Wolf, Yu, "Intraday Price Reversals in the US Stock Index Futures Market: A 15-Year Study," *Journal of Banking & Finance* 2005 (DOI 10.1016/j.jbankfin.2004.04.006; 47 citations) — RAW FACT existence; RECORDED CLAIM: reversal tendency following large opening gaps in S&P futures, economically marginal after costs in later subperiods.
- Levander (SSRN 7155458, 2026, RAW FACT abstract): support/resistance boundary framework on 5-min candles shows "statistically significant reversal predictability at short lags," decaying as streaks extend.
- Baltussen et al. (§1) note the hedging-demand intraday momentum **reverts within days** — i.e., multi-day mean reversion after flow-driven moves (RAW FACT abstract).
- **GENESIS classification:** empirical result (older, modest, cost-sensitive) + implementation clue (reversion is conditional on *flow-driven*, not news-driven, moves). No strong modern refereed evidence of a standalone large-move fade edge in index futures.

---

## 6. VIX / volatility-state conditioning

- Moreira & Muir, "Volatility-Managed Portfolios," *JF* 2017 (SSRN/NBER verified via Crossref, RAW FACT abstract): scaling exposure by inverse recent variance "produces large alphas, substantially increases factor Sharpe ratios"; risk is lowered in recessions/crises without proportional return loss.
- Cederburg, O'Doherty, Wang, Yan, "On the Performance of Volatility-Managed Portfolios," *JFE* 2020 (DOI 10.1016/j.jfineco.2020.04.015; 154 citations) — RAW FACT existence; RECORDED CLAIM: across ~103 portfolios, real-time implementable versions mostly fail; the **market factor is among the few that retains benefit**, largely via crash-avoidance.
- Bollerslev, Tauchen, Zhou, "Expected Stock Returns and Variance Risk Premia," *RFS* 2009 (DOI 10.1093/rfs/hhp008; ~1,600 citations) — RAW FACT abstracts (working-paper versions): the **variance risk premium (implied minus realized variance) explains >15% of quarterly excess-return variation (1990–2005)**, peaking at quarterly horizon; dominates P/E, cay, etc.
- **GENESIS classification:** vol-managed sizing = robust **risk-specification** improvement for the market factor (per CLAUDE.md language: never let it masquerade as information alpha); VRP = genuine empirical predictor but at monthly-quarterly horizon, weak at ≤1 week.

---

## 7. Calendar effects: day-of-week, turn-of-month, OPEX

- **Day-of-week:** Kohers, Kohers, Pandey, Kohers, "The Disappearing Day-of-the-Week Effect in the World's Largest Equity Markets," *Applied Economics Letters* 2004 (DOI 10.1080/1350485042000203797; 68 citations) — RAW FACT existence; the title is the finding. Later fuzzy-GARCH work (Giovanis 2010, RAW FACT abstract) finds "there isn't the day of the week or the Monday effect." **Dead for developed indices.**
- **Turn-of-month:** McConnell & Xu, "Equity Returns at the Turn of the Month," *Financial Analysts Journal* 2008 (DOI 10.2469/faj.v64.n2.11; 104 citations) — RAW FACT abstract (2006 WP): returns from the **last trading day through the first three days of the month are significantly higher than all other days, in data 1897–2005**, robust across size groups and countries (UK extension FAJ 2009). Post-2005 out-of-sample: RECORDED CLAIM — effect persists but attenuated; month-end institutional flow ("dash for cash", Etula et al. JF 2020) is the leading mechanism.
- **OPEX:** Stivers & Sun, "Returns and Option Activity over the Option-Expiration Week for S&P 100 Stocks," *J. Banking & Finance* 2013 (DOI 10.1016/j.jbankfin.2013.07.030) — RAW FACT abstract: OPEX-week returns "tend to be high," mechanism = **delta-hedge rebalancing (unwinding of short-stock hedges) by option market makers**. Chiang, *J. Empirical Finance* 2014 (DOI 10.1016/j.jempfin.2014.03.003): price impact of liquidity trading on expiration dates. Post-publication status: RECORDED CLAIM — practitioner evidence (0DTE era) suggests the weekly-OPEX cycle weakened as expirations went daily; not formally settled.
- **GENESIS classification:** TOM = durable empirical result with flow mechanism; OPEX = empirical result + mechanism, but structurally altered by 0DTE proliferation post-2022; day-of-week = debunked.

---

## 8. Pre-FOMC announcement drift and FOMC-cycle effects

- Lucca & Moench, "The Pre-FOMC Announcement Drift," *JF* 2015 (WP 2012, DOI 10.2139/ssrn.2024459 — RAW FACT abstract): "excess returns earned in the 24 hours ahead of scheduled FOMC announcements can account for **more than 80% of the equity premium over 17 years**" (1994–2011; RECORDED CLAIM: ~49 bps average per event).
- **Post-publication death (RAW FACT via Crossref):** Kurov, Wolfe, Gilbert, "The Disappearing Pre-FOMC Announcement Drift," *Finance Research Letters* 2021 (DOI 10.1016/j.frl.2020.101781; 19 citations) — documents the drift weakening/disappearing in the post-2015 sample (title is the finding; in-text numbers RECORDED CLAIM).
- **FOMC cycle (RAW FACT via Crossref abstract):** Cieslak, Morse, Vissing-Jorgensen, "Stock Returns over the FOMC Cycle," *JF* 2019 (DOI 10.1111/jofi.12818; 277 citations): "Since 1994, the equity premium is earned entirely in **weeks 0, 2, 4, and 6 in FOMC-cycle time**." Post-publication: RECORDED CLAIM — mixed replications, attenuation reported post-2016; still the strongest *bi-weekly-horizon* calendar structure in the literature.
- **GENESIS classification:** pre-FOMC 24h drift = empirical result, **post-publication dead**; FOMC-cycle weeks = empirical result with policy-communication mechanism, partial decay, cheap to condition on.

---

## 9. Macro-announcement premium and pre-announcement drift

- Savor & Wilson, "How Much Do Investors Care About Macroeconomic Risk?" (*JFQA* 2013; WP RAW FACT abstract): average market excess return **10.6 bps on scheduled announcement days (CPI/NFP/FOMC) vs 1.0 bps on other days**; announcement days supply the bulk of the equity premium. Post-publication: RECORDED CLAIM — announcement-day premium is one of the more durable conditioning facts; Ai & Bansal (Econometrica 2018) supply theory.
- Kurov, Sancetta, Strasser, Wolfe, "Price Drift Before U.S. Macroeconomic News: Private Information about Public Announcements?" *JFQA* 2018 (DOI 10.1017/s0022109018000625; 77 citations) — RAW FACT abstract: prices "begin to move in the 'correct' direction about **30 minutes before the release time**"; drift present in ~9 of 20 releases; **pre-announcement drift ≈ 40% of total price adjustment** in equity index and Treasury futures. Post-publication: RECORDED CLAIM — release procedures/lockups tightened after 2013–2018 scrutiny; unconditional exploitation not possible (requires knowing the surprise sign); use as a *variance/participation* clue.
- Note the repo's own MEMORY doctrine (recorded): macro **surprise magnitude** research is N-bound (~71 sessions) — externally, announcement effects are about *when* variance and premium concentrate, which is N-rich.
- **GENESIS classification:** announcement-day premium = durable empirical result, trivially implementable as calendar conditioning; 30-min pre-release drift = empirical result usable only as timing/vol structure, not directional alpha.

---

## 10. ES–NQ lead-lag and cross-asset (rates → NQ)

- Hasbrouck, "Intraday Price Formation in U.S. Equity Index Markets," *JF* 2003 (DOI 10.1046/j.1540-6261.2003.00609.x; 395 citations) — RAW FACT abstract: "most of the price discovery for both indexes [S&P 500 and Nasdaq-100] occurs in the **E-mini markets**" (data ~2000). I.e., NQ/ES lead their cash/ETF counterparts, not each other.
- Budish, Cramton, Shim, "The High-Frequency Trading Arms Race," *QJE* 2015 (DOI 10.1093/qje/qjv027; 679 citations) — RAW FACT existence/abstract; RECORDED CLAIM details: ES–SPY arbitrage median duration fell from ~97 ms (2005) to ~7 ms (2011); correlation between ES and SPY at 10-ms scale is ~0. Aquilina, Budish, O'Neill (NBER w29011, 2021 — RAW FACT existence; RECORDED CLAIM: races last ~79 microseconds, latency-arb "tax" ~0.4 bps of volume).
- **Implication:** any ES→NQ or rates→NQ lead-lag at 1-minute resolution accessible to this stack is either arbitraged (ms-scale) or a *co-movement regime* fact, not a signal. The **stock-bond correlation literature** (RAW FACT via Crossref survey: Li/Zha/Zhang/Zhou 2021 — positive corr 1971–2000, negative after 2000; Seo 2023 — high trend inflation ⇒ positive stock-bond corr; post-2022 re-flip documented mostly in practitioner work, RECORDED CLAIM) makes rates a **regime/conditioning** input for NQ, especially 2022+, not a lead-lag alpha.
- **GENESIS classification:** lead-lag at accessible latency = debunked for alpha (empirical result, HFT-arbitraged); rates-regime conditioning = theoretical mechanism + empirical result at daily+ horizon.

---

## 11. Volume–volatility relations

- Classics (RECORDED CLAIM, not re-verified this session): Clark 1973 (Econometrica, mixture-of-distributions), Tauchen & Pitts 1983, Andersen 1996 (*JF*) — volume and volatility are jointly driven by information flow; contemporaneous correlation strong, but **volume does not directionally predict returns** at the index level.
- What IS verified and usable: Gao et al. (§1, RAW FACT) — intraday momentum stronger on **higher-volume** days; Li/Sakkas/Urquhart (RAW FACT) — ITSM stronger with **low liquidity, high volatility, discrete information events**; Baltussen et al. (RAW FACT) — flow-driven momentum from hedging demand.
- **GENESIS classification:** theoretical mechanism (MDH) whose practical use is as a **conditioning layer** (regime/participation filters), not a standalone signal.

---

## 12. Ranked shortlist — 8 externally supported mechanisms to seed the hypothesis atlas

Ranking = claimed effect size × post-publication survival × implementability in 1-min NQ futures data. Every entry names its decay status.

1. **Hedging-demand / late-day flow intraday momentum (conditional form).** Gao et al. JFE 2018 + Baltussen et al. JFE 2021 + Li et al. JFM 2022 (16-market OOS). Mechanism-anchored (gamma + leveraged-ETF rebalancing), conditioning variables specified (vol, volume, news days, imbalance). DECAY FLAG: naive SPY version Sharpe 1.34→0.39 after May 2024 (Paz 2026, RAW FACT). Seed the *conditional* version, prereg the decay test.
2. **Scheduled-macro-announcement-day conditioning.** Savor-Wilson: 10.6 vs 1.0 bps/day (RAW FACT). Calendar is public, N-rich, trivially implementable at any bar size; use for exposure/vol budgeting and as an interaction term for #1.
3. **Turn-of-month flow premium.** McConnell-Xu FAJ 2008, 1897–2005, cross-country (RAW FACT). Slow decay at most; weekly-horizon compatible; trivially implementable. Low frequency (12 events/yr) is the main cost.
4. **FOMC-cycle structure (weeks 0/2/4/6).** Cieslak et al. JF 2019 (RAW FACT). Bi-weekly horizon matches WEEKLY_EDGE; partial post-publication attenuation (RECORDED). Cheap to test as a routing/conditioning variable.
5. **Volatility-state position sizing (vol-managed market exposure).** Moreira-Muir JF 2017; survives Cederburg JFE 2020 scrutiny best *for the market factor* (RECORDED). Classify strictly as RISK SPECIFICATION, not information alpha.
6. **OPEX/gamma-flow calendar conditioning.** Stivers-Sun JBF 2013 (RAW FACT) + Baltussen mechanism. Structural break risk from 0DTE era (RECORDED) — test as a *conditioning regime* (dealer-gamma proxy via free Cboe OI already flagged in repo memory), not as a standalone drift.
7. **Overnight/intraday session split as structural allocation.** Cliff-Cooper-Gulen (RAW FACT), Lou-Polk-Skouras JFE 2019. The *split* persists even though the tradable 2–3 a.m. drift is dead (NY Fed 2026, RAW FACT). Decide *which session's risk to hold* — a weekly-horizon design axis, not a signal.
8. **Variance-risk-premium / vol-regime return forecasting at the weekly-to-monthly edge.** Bollerslev-Tauchen-Zhou RFS 2009 (>15% quarterly R², RAW FACT); weak at ≤1 week but the only externally validated *level* predictor compatible with free options/VX data already in NT8 (per repo memory).

**Explicitly demoted / dead:** pre-FOMC 24h drift (dead post-2015, FRL 2021); overnight 2–3 a.m. drift (dead post-2021, authors' own 2026 update); day-of-week (dead since ~2004); ES→NQ or ETF→futures lead-lag at accessible latency (arbitraged to ms); unconditional TSMOM on a single equity index at daily/weekly horizon (contested existence + lost decade); ORB as marketed (un-refereed, leverage-inflated, contradicted net-of-cost on MNQ 2021–2025).

**Cross-cutting law:** McLean & Pontiff, *JF* 2016 (DOI 10.1111/jofi.12365; 1,380 citations — RAW FACT abstract): across 97 published predictors, returns are **26% lower out-of-sample and 58% lower post-publication**. Every effect above must be haircut accordingly *before* EVI ranking; the three anchor intraday effects here already have named post-publication obituaries, which is exactly the pattern McLean-Pontiff predicts.
