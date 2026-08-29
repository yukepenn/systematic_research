# G2 WORLD DISCOVERY WAVE 1 — MECHANISM CARDS (B1 dedup + family tree)

Built 2026-08-28 from the 16 scout reports in `runs/G2_WORLDSCAN_W1_20260828/partial_snapshot/g2w1_a*.md`.
Gated against `research/genesis2/FAILURE_MEMORY.md` (closed list AND not-closed guard).
37 cards. Owned-data vocabulary for falsifiers: NQ 1-min 2006-2026, ES/RTY/YM 1-min 2022+,
internals minute 2022+, certified VIX/VXN/VX daily, limited 2025-26 NQ/ES tick+BBO, multi-market daily.
Evidence classes used: PEER-REVIEWED > IN-HOUSE-PREREG > CODED-BACKTEST > LARGE-N-DESCRIPTIVE > EXAMPLES > TESTIMONY.

---

[CARD id=MC-01]
NAME: Opening range breakout (continuation)
FAMILY: OPENING
MECHANISM: The opening auction concentrates overnight information and fresh flow; a confirmed break of the first N-minute range marks an unresolved imbalance that tends to continue intraday (volatility-expansion / trend-day onset).
MERGED-LEADS: A2-01/-06/-07/-08/-09/-15; A3 (reddit ORB cluster 1rrn609/1saburp/1spd5nf/1j9pxsr); A4-03 (Ruggiero, ET 295572)/A4-09/A4-11; A6-01 (github.com/giovannibrusco/zarattini-2023-orb-qqq)/A6-13; A7 (oxfordstrat.com/trading-strategies/opening-range-breakout/); A11-01 (SSRN 4416622)/A11-02 (SSRN 4729284, RVOL "stocks in play"); A15 (GENESIS_BASELINES B3 control).
INDEPENDENT-SOURCES: 4+ genuinely independent lines — Crabel 1990 (pit era); Holmberg/Lönnbark/Lundström FRL 2013 (crude futures, peer-reviewed); Zarattini & Aziz 2023 SSRN 4416622 with independent GitHub/reddit replications; in-house B3 control. Ruggiero counter-claim (dead for futures post pit-close) + Mesfin arXiv 2605.04004 (ORB fails on MNQ at 2-pt friction) are the negatives.
EVIDENCE-BEST: PEER-REVIEWED (FRL 2013) + IN-HOUSE MEASURED control: B3 = $1,043/wk net, t=2.19, 2022-2026 at $18.80/ctrRT.
OBSERVABLES: first 5/15/30-min H/L, first-bar direction, OR volume/RVOL, 1-min close confirms.  DATA-CAPABLE-NOW: YES (NQ 1-min 2006-2026).
NOVELTY-VS-REPO: RAW-INFO — FAILURE_MEMORY's NOT-closed guard explicitly keeps ORB alive as a mechanism-motivated candidate; only the un-preregistered baseline control is non-promotable, and the ORB-failure FADE (FB01/B01c) is the falsified side.
HORIZON: entry 09:45-10:30 ET, exit EOD.  COST-SENSITIVITY: MED (giovannibrusco: QQQ edge dies at ~2.2c/sh slippage; NQ needs points-scale edge vs ~4t RT).
CHEAPEST-FALSIFIER: fresh preregistered H4-family spec on NQ 1-min 2006-2026: 15-min OR, close-confirmed break, EOD exit, era-split 2006-13/14-21/22-26, session-shift null + MIRROR_CONTINUATION_CONTROL + portfolio-marginal gate.
PRIOR: HIGH — three independent modern sightings including our own measured control; main risks are cost and 2022-concentration of profits in several sources.
[/CARD]

[CARD id=MC-02]
NAME: Volatility-scaled open bands (Stretch / Dual Thrust / noise-area)
FAMILY: OPENING
MECHANISM: Calibrate a "noise" band around the open from prior days' volatility (optionally time-of-day-resolved); price beyond the band = abnormal imbalance, followed trend-side; inside = untradable equilibrium zone.
MERGED-LEADS: A7 (Crabel Stretch = SMA10(min(H-O,O-L))x2, oxfordstrat; Williams GSV; mypivots stretch def); A5 (Lizard noise-band ORB); A6-09 (je-suis-tm Dual Thrust; QC SPY Sharpe -0.17); A6-07/A11-03 (Zarattini "Beat the Market" SSRN 4824172; Ascensao + alienblack replications); A2-03 (ATR-tiered stops variant).
INDEPENDENT-SOURCES: 3 — Crabel/Williams (1980s-90s), Concretum 2024 (SPY, Sharpe 1.33 net claim), Dual Thrust lineage (QC re-test NEGATIVE on SPY hourly). Replications split: Ascensao "aligns closely", alienblack "weak Sharpe on 2024".
EVIDENCE-BEST: CODED-BACKTEST of an SSRN paper with two independent replications (one confirming, one weak).
OBSERVABLES: per-minute |move from open| averaged over prior 14 days, band = Open*(1±avg); prior-day range for Dual Thrust.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: REPRESENTATION — time-of-day-resolved noise band echoes the parked TOD-normalized-threshold-clock idea; no closed scope covers it (H4B closed only the first→last half-hour geometry).
HORIZON: intraday, band-cross to EOD.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: implement the noise-area rule verbatim on NQ 1-min 2006-2026, costs on, era-split, with plain 15-min ORB (MC-01 spec) as the matched control in the same wave — does the band beat the range?
PRIOR: MED — one strong author family + one weak replication; mechanism coherent with MC-01.
[/CARD]

[CARD id=MC-03]
NAME: Opening gap fill/continuation by size and location
FAMILY: OPENING
MECHANISM: Small gaps are overnight noise in thin liquidity and revert (fill); large gaps beyond prior value are genuine repricing and continue. The conditioning variables (gap/ATR, open location vs prior range/value) carry the information, not the gap per se.
MERGED-LEADS: A9 (Steenbarger gap studies N=962/2,375; Hanna mid-gap studies; tradingstats.net/when-do-gaps-fill fill-by-ATR tier 78%→8%; nqstats rth_breaks); A4 (thegapguy, futures.io 55593); A7 (Hanna ≥2% gap-down → 69% close above open); A11 (Mesfin: naive gap FADE fails on MNQ t=-0.44..-0.59; gap-continuation N=22 fails N-gate).
INDEPENDENT-SOURCES: 5 — Steenbarger (SPY 1997-2009), Hanna, tradingstats (2020-25), thegapguy (2005+), Mesfin (modern MNQ negative on the fade).
EVIDENCE-BEST: LARGE-N-DESCRIPTIVE from multiple independent computations agreeing on the size-monotone fill gradient.
OBSERVABLES: 09:30 open vs prior 16:00 close and prior RTH H/L; gap/14d-ATR; fill time.  DATA-CAPABLE-NOW: YES (NQ 1-min 2006-2026).
NOVELTY-VS-REPO: RAW-INFO — gap state has never been a conditioner in this repo; no closed scope covers it (W118 closed endogenous-trigger reversal, not open-gap conditioning).
HORIZON: open → noon.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: NQ gap-size × open-location fill table 2006-2026 era-split (descriptive), then ONE preregistered use as a day-type conditioner on an existing engine vs matched unconditional control — NOT a standalone fade (Mesfin killed that at modern costs).
PRIOR: MED.
[/CARD]

[CARD id=MC-04]
NAME: Initial Balance auction conditioning
FAMILY: PROFILE
MECHANISM: The first hour is the auction's two-sided search; where the IB closes (vs midpoint), which extreme formed first, and IB width vs ATR encode which side lost the auction → directional extension probabilities for the rest of the session.
MERGED-LEADS: A2-11/-12/-13/-14 (edgeful morning + afternoon IB, NQ Stats, Dan Cooke IB25 entry); A3/A9 (nqstats.com/ib_breaks.html N=2,571: either side 96.1% by close, combined conditionals 74-84%; tradingstats.net IB trilogy: breakout 96-98%, retest continue-vs-reverse crossover ≈1.40-1.50 ext, IB-VPOC adds ~zero over IB direction); A5 (DGT IB Auction Intelligence, open-source 5-state machine, tradingview.com/script/ks2QGulb).
INDEPENDENT-SOURCES: 3 stat shops with different definitions/periods (nqstats wick-basis 2016-25; tradingstats close-basis 2014-26; edgeful rolling 6-mo) + Dalton lineage claims (correlated).
EVIDENCE-BEST: LARGE-N-DESCRIPTIVE, two anonymous sites agreeing at base-rate level; unaudited.
OBSERVABLES: 09:30-10:30 H/L, IB close vs midpoint, first-extreme timing, IB range/ATR, extension multiples.  DATA-CAPABLE-NOW: YES (NQ 1-min 2006-2026).
NOVELTY-VS-REPO: RAW-INFO — market-profile/auction claims are explicitly NOT closed (never tested here); distinct from ONRANGE quadrants (overnight range, different object).
HORIZON: 10:30 → EOD.  COST-SENSITIVITY: MED (limit entry at IB retrace reduces paid spread).
CHEAPEST-FALSIFIER: replicate the IB conditional table on NQ 1-min 2006-2026 era-split; if base rates hold, preregister ONE entry policy (IB25 limit toward the favored break) vs matched unconditional control; print the IB-VPOC-style increment test for any added conditioner.
PRIOR: MED — base rates near-certain to replicate; tradability unproven, and tradingstats' own VPOC null shows added conditioners can be empty.
[/CARD]

[CARD id=MC-05]
NAME: 80% rule (value-area rotation)
FAMILY: PROFILE
MECHANISM: Open outside prior day's value area followed by re-entry + acceptance (two consecutive 30-min periods inside) implies the market rejected the open as unfair → rotation across the full value area to the other edge.
MERGED-LEADS: A4-01 (ET 95941 incl. skeptic reply "isn't anywhere close to 80%"); A9/A10 (mypivots.com/dictionary/definition/25/80-rule — states the rule AND self-reports ~60% on ES; shadowtrader.com/glossary/eighty-percent-rule/; vtrender; quantopian-archive thread, Harlin manual 28/33).
INDEPENDENT-SOURCES: 1 lineage (Dalton/CBOT "Profile Reports") + 2 informal tests that DISAGREE (~60% vs ~85% small-N manual).
EVIDENCE-BEST: informal tests, conflicting; no audited backtest anywhere.
OBSERVABLES: prior-day value area (70% volume or TPO), open location, 30-min re-entry/acceptance sequence.  DATA-CAPABLE-NOW: YES (VA from NQ 1-min volume-at-price approximation).
NOVELTY-VS-REPO: RAW-INFO — profile constructs never tested here (NOT-closed guard names market-profile/auction claims explicitly).
HORIZON: intraday, hours.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: mechanical 80%-rule detector on NQ 1-min 2006-2026: P(full VA traverse | acceptance) vs P(traverse | open outside, no acceptance) matched control — settles the branded number definitively.
PRIOR: LOW — the only concrete test on record contradicts the brand; still cheap to own the real number.
[/CARD]

[CARD id=MC-06]
NAME: Poor-structure repair (single prints, poor highs/lows, naked POC)
FAMILY: PROFILE
MECHANISM: Auction anomalies — un-auctioned single-print zones, flat un-excessed extremes, untested prior POCs — are unfinished business the market returns to repair; they act as magnets/targets.
MERGED-LEADS: A9 (tradingstats.net/single-prints-market-profile-research/ N=3,847 zones: D+5 fill 63-67%, unfilled-7d → ever-fill <50%; shadowtrader poor-high glossary; TPO TradingView scripts e6y9zmfW, aXGqvR8l; ATAS Dalton article).
INDEPENDENT-SOURCES: 1 quantified (tradingstats) + Dalton-lineage qualitative restatements (correlated). A9 notes poor-high repair RATES exist nowhere as published numbers — we would produce the first.
EVIDENCE-BEST: LARGE-N-DESCRIPTIVE, single source.
OBSERVABLES: TPO/1-min single-print zones (interior, ≥2 ticks, 2-25% of range), flat extremes, prior-day POC.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: RAW-INFO — never tested here; NOT-closed guard covers profile claims.
HORIZON: 1-5 days for fills; intraday for targets.  COST-SENSITIVITY: LOW-MED (used as targets, not entries).
CHEAPEST-FALSIFIER: single-print-zone detector on NQ 1-min; fill-rate vs distance-matched random zones (matched control in same wave); survivorship curve vs tradingstats' published decay.
PRIOR: MED.
[/CARD]

[CARD id=MC-07]
NAME: Reference-level magnetism (PDH/PDL/ONH/ONL first-touch)
FAMILY: PROFILE
MECHANISM: Stop and target clusters at prior-session and overnight extremes make them high-probability visit points; open location relative to those levels (e.g., vs ON midpoint) sets which side is hit first — overnight-inventory correction.
MERGED-LEADS: A4 (eminiman414 n=186 hand-tally: break either 90.3%); A9/A3 (nqstats rth_breaks; tradingstats overnight-breakout N=2,827: ≥1 ON level hit 94.2%, open-vs-ON-midpoint → first-break side 75-76%; pdh-pdl-sweep asymmetry PDH 56.8% > PDL 43.4%, 11/12 years); A11 (Steenbarger: >90% of days take out ON H or L; ~85-88% not inside days); A3 (shadowtrader overnight-inventory glossary).
INDEPENDENT-SOURCES: 4 — Steenbarger (SPY/ES 2005-09), nqstats, tradingstats, forum hand-tally; convergent base rates.
EVIDENCE-BEST: LARGE-N-DESCRIPTIVE, independently computed and convergent.
OBSERVABLES: PDH/PDL, ON H/L (18:00-09:30), open vs ON midpoint, first-touch timing.  DATA-CAPABLE-NOW: YES (NQ 1-min 2006-2026, ETH included).
NOVELTY-VS-REPO: RAW-INFO — ONRANGE closed overnight-range QUADRANT day-types; visit/first-touch base rates conditioned on open location are a different observable and decision role (target selection).
HORIZON: open → noon mostly (median first ON-level break 11 min after open).  COST-SENSITIVITY: LOW-MED (informs targets/stops more than entries).
CHEAPEST-FALSIFIER: conditional first-touch table on NQ 1-min (open vs ON midpoint × which level first), era-split; then one preregistered target policy on an existing engine vs its current targets.
PRIOR: MED.
[/CARD]

[CARD id=MC-08]
NAME: Stop-run reversal at reference extremes (sweep-and-reclaim)
FAMILY: PATH
MECHANISM: A push through a well-watched prior extreme fires resting stops; if no genuine initiative follows (no follow-through, absorption present), trapped breakout traders plus consumed stop liquidity produce a reversal back inside — the reclaim earns the unwind. The follow-through/absorption discriminator IS the hypothesis.
MERGED-LEADS: A3 (Raschke-Connors 1995 Turtle Soup → ICT turtle soup → Mancini failed-breakdown three-generation lineage; reddit FBD threads); A7 (turtle soup exact rules, newtraderu/tradersmastermind; luxalgo attribution); A4-04/-10 + A7 (Taylor 1950 buy-day = test of prior low then rally); A8-14 (bookmap.com stop-hunt vs breakout criteria); A11 (TradingView Session Breakout/Sweep policy-fork script; Big Daddy Max failed-ORB reversal branch); A2 (liquidity-sweep models in FTS/Lab/BNQ); A4 (MES double-break note).
INDEPENDENT-SOURCES: 4 eras — Taylor (1950s), Connors/Raschke (1995), ICT/Mancini (2010s-20s, derivative of each other), order-flow vendors (2010s-20s). Genuine multi-era rediscovery → raises prior per protocol.
EVIDENCE-BEST: EXAMPLES/TESTIMONY only — no audited statistics found anywhere despite the enormous footprint.
OBSERVABLES: sweep of PDH/PDL/ONH/ONL/IB extreme (wick beyond, close back inside within k bars); follow-through classifier; optional absorption from signed ticks.  DATA-CAPABLE-NOW: YES for price-only version (NQ 1-min); PARTIAL for absorption discriminator (2025-26 tick+BBO; depth variants blocked by DOM pause).
NOVELTY-VS-REPO: RAW-INFO — must clear: seven 2022-era fade geometries (closed; mirror of live momentum), W118 event-driven reversal at ENDOGENOUS triggers (closed; continuation won), W40 sweep-and-reclaim (parked for absorption visibility). Material difference: trigger is an EXOGENOUS pre-existing reference level with an explicit reclaim/follow-through classifier — different observable and causal timing from W118's endogenous move-triggers.
HORIZON: 5-120 min.  COST-SENSITIVITY: HIGH (reversal entries pay the spread at the extreme).
CHEAPEST-FALSIFIER: sweep events at PDH/PDL/ONH/ONL on NQ 1-min 2006-2026: classify reclaim-within-3-bars vs acceptance; conditional forward returns vs matched non-sweep control + MIRROR_CONTINUATION_CONTROL (continuation must be the printed alternative).
PRIOR: MED — independence raises it; repo's fade closures and the total absence of quantified evidence cap it.
[/CARD]

[CARD id=MC-09]
NAME: Fair-value-gap / displacement-imbalance retracement
FAMILY: PATH
MECHANISM: A three-bar displacement leaves a one-sided price void (FVG); price retraces into it and the original initiative resumes (resting interest of the displacing party). ICT's core entry object.
MERGED-LEADS: A2-02/-04/-10/-18 (DionTrades FTS, Trader Kane Lab, Percoco NY-open FVG, BionicNQ iFVG/SMT); A2-05 (Trader Zan 10-yr mechanical test: 25.7% WR at 3R ≈ breakeven, NEGATIVE); A6-03 (nq-strategy-b-bot nested 5m/15m FVG: +$17,187 MNQ but WR drifts 46.5→68.1% by year — red flag); A6-05 (lokus-research SMC "Perfect Confluence" CLOSED no edge after fees, prereg-grade); A6-06 (mes-smc 77-79% WR at 2R = implausible); A11 (FVG detector scripts CantoLab/LunqFX).
INDEPENDENT-SOURCES: 1 (all trace to Michael Huddleston/ICT); the tests are derivative of one guru claim. Test results: the two most rigorous (lokus prereg w/ Bonferroni + sealed holdout; Zan 10-yr) are null/negative; one positive has a rising-WR-by-year artifact.
EVIDENCE-BEST: CODED-BACKTEST, conflicting; best-governed run = NULL.
OBSERVABLES: 3-bar imbalance (low[t] > high[t-2] and mirror), mitigation tracking, HTF nesting.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: REPRESENTATION — imbalance-zone geometry is new here; nothing closed covers it, but the world's own best tests already failed it.
HORIZON: minutes-hours, NY session.  COST-SENSITIVITY: HIGH.
CHEAPEST-FALSIFIER: re-run b-bot's exact nested-FVG spec on NQ 1-min 2006-2026 era-split — its 2023-26 rising WR predicts collapse out-of-era; one shot, no tuning.
PRIOR: LOW.
[/CARD]

[CARD id=MC-10]
NAME: Trade-burst self-excitation (tape speed / volume microbursts / Hawkes)
FAMILY: PATH
MECHANISM: Aggressive order arrival is self-exciting; an abnormal activity burst marks initiative that momentarily continues (momentum-ignition claim) — or, per the strongest test, exhausts within the burst bar and REVERSES.
MERGED-LEADS: A11 (neurotrader888 VolatilityHawkes + TrendlineBreakoutMetaLabel repos; Mesfin Asia-session opening-range-expansion: continuation t=-10.96, WR 35.5% — significant reversal); A5 (MotiveWave Speed of Tape, Zeiierman LTF Microburst, Sierra LVTI big-trade prints); A8 (tape-speed lore L4; Takahashi 1-sec SVAR: impact shocks die ~1s).
INDEPENDENT-SOURCES: 3 — vendor lore (correlated family), open-source Hawkes line, Mesfin's preregistered-style negative.
EVIDENCE-BEST: CODED-BACKTEST negative (Mesfin) beats all the unquantified vendor claims.
OBSERVABLES: per-bar volume z vs 20-bar baseline, range expansion multiple, trade-count rate (tick store for sub-minute).  DATA-CAPABLE-NOW: PARTIAL (1-min proxies 2006-26; true burst detection needs 2025-26 tick store).
NOVELTY-VS-REPO: REPRESENTATION — nearby closures: seconds-scale OFI dissipation (dead list), W118 endogenous triggers. Material difference: burst as a VOL/participation STATE feeding sizing or gating, not a direction-taking signal.
HORIZON: 1-60 min.  COST-SENSITIVITY: HIGH if traded; LOW as state.
CHEAPEST-FALSIFIER: 1-min volume+range burst z on NQ: forward return sign AND realized vol by horizon 1-60 min, both directions printed, circular-shift null — adjudicates ignition vs exhaustion in one table.
PRIOR: LOW.
[/CARD]

[CARD id=MC-11]
NAME: Fixed clock-window flows (Silver Bullet 10-11, MOC macro 15:50, hourly turns)
FAMILY: TIMEOFDAY
MECHANISM: Institutional execution clocks (hourly TWAP slices, 10:00 data digestion, 15:50 MOC preparation) allegedly create repeatable within-window liquidity runs toward obvious liquidity pools.
MERGED-LEADS: A3 (ICT silver bullet cluster: innercircletrader.net, backtrex rules, reddit tests 66.67% 1-wk vs 36% larger-N; ICT MOC macro 15:50-16:00; hourly "macros" last-10/first-10 min; nqstats hour_stats: prior-hour-range breach → reversion 61.5%, 17,701 events); A12-18 (NYSE imbalance publication starts 15:50, mechanical anchor).
INDEPENDENT-SOURCES: 1 guru lineage + 1 anonymous stat site + exchange mechanics (real but not an edge claim). Reddit tests conflict.
EVIDENCE-BEST: LARGE-N-DESCRIPTIVE for the hourly-reversion number; conflicting small backtests for the windows.
OBSERVABLES: clock windows, prior-hour H/L, window-relative returns.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: RAW-INFO — H2 closed calendar DAY-types; within-day windows are different causal timing and were never tested as flow states.
HORIZON: within 10-60-min windows.  COST-SENSITIVITY: HIGH.
CHEAPEST-FALSIFIER: all-window scan — return/vol/reversal stats for every 30-min window across NQ 1-min 2006-2026, family-corrected; any named window (10-11, 15:50) must beat the all-window null, not a cherry-picked baseline.
PRIOR: LOW.
[/CARD]

[CARD id=MC-12]
NAME: ETH session-hour structure (European-open drift, Asia/London ranges)
FAMILY: TIMEOFDAY
MECHANISM: Dealer inventory unwind after end-of-day imbalances produced concentrated 2-3am ET returns (1998-2020); session handoffs (Asia→London→NY) structure overnight range formation. The drift's death has a documented cause: closing-imbalance dispersion halved (6.5%→2.9%).
MERGED-LEADS: A1-02/A3/A12-11/-12 (Boyarchenko/Larsen/Whelan RFS 2023 + libertystreeteconomics.newyorkfed.org 2026-07-01 disappearance post); A12-13/-14 (Elm Wealth night-moves; Bondarenko-Muravyev: 4 hours around European open = entire average return, SR 1.6); A9/A3 (nqstats aln_sessions engulf patterns N=2,542); A6-10 (NSQ overnight 00:00-02:30 NT8 bot — implausibly smooth, AI-slop suspicion); A11 (London Breakout script, author self-reports poor results).
INDEPENDENT-SOURCES: 3 — NY Fed team, Bondarenko-Muravyev, Elm Wealth (+ nqstats structural stats). The disconfirmation is by the original authors (strongest kind).
EVIDENCE-BEST: PEER-REVIEWED (RFS 2023) + authors' own 2026 disconfirmation.
OBSERVABLES: hour-of-session returns 18:00-09:30, session-block H/L (Asia 20-02, London 02-08), EOD imbalance dispersion proxy.  DATA-CAPABLE-NOW: YES (NQ 1-min ETH 2006-2026 — can replicate both the rise and the fall).
NOVELTY-VS-REPO: RAW-INFO — NIGHT overnight channel closed at 88th pctile (bar 95th); overnight drift on the dead-effects list, so any use REQUIRES a decay story: the imbalance-dispersion mechanism supplies a measurable revival trigger. Overnight friction tax $5.25/RT stands.
HORIZON: overnight hours.  COST-SENSITIVITY: HIGH (overnight spreads).
CHEAPEST-FALSIFIER: replicate hour-of-night NQ mean returns by era (1998-2020 vs 2021+ shape); register the dispersion proxy as a MONITOR-only revival trigger — no build.
PRIOR: LOW — dead by its own authors; value is the monitor.
[/CARD]

[CARD id=MC-13]
NAME: Late-day hedging-demand momentum
FAMILY: MOMENTUM
MECHANISM: Option dealers and leveraged-ETF rebalancers must trade WITH the day's move near the close; the return over the rest of the day predicts the last-30-minute return, scaled by the size of outstanding hedging demand.
MERGED-LEADS: A1-01 (Baltussen/Da/Lammers/Martens JFE 2021, DOI 10.1016/j.jfineco.2021.04.029); A1-09 (Barbon-Buraschi Gamma Fragility SSRN 3725454; Barbon et al LETF/EOD SSRN 3925725; Shum et al RoF 2016); A12-16; A13 (Woo loop-gain arXiv 2608.22768 LETF feedback); A6-08 (QC Gao-style replication: Sharpe -0.63 2015-2020 — decayed); A15 (MOM01: Baltussen-style diagnostic did NOT replicate on NQ; H4B closure context).
INDEPENDENT-SOURCES: 3 academic teams (Baltussen; Barbon/Buraschi; Shum) with one identified mechanism; LETF AUM is public data.
EVIDENCE-BEST: PEER-REVIEWED (JFE 2021, RoF 2016).
OBSERVABLES: 09:30-15:30 return sign/size, last-30-min return, LETF AUM x |move| demand proxy, (gamma proxies owner-gated).  DATA-CAPABLE-NOW: PARTIAL (price geometry YES on NQ 1-min; LETF AUM = $0 public build; gamma needs owner-gated options data).
NOVELTY-VS-REPO: RAW-INFO — H4B closed the UNCONDITIONAL first→last geometry (dead ~2014 on NQ) and MOM01 found the Baltussen diagnostic doesn't replicate; the live branch is demand-proxy-CONDITIONED last-30-min momentum — different observable and decision role, and exactly the evidence class A15 says would strengthen FOLLOW_MORNING.
HORIZON: 15:30-16:00.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: rest-of-day sign → last-30-min NQ return conditioned on LETF-AUM x |move| terciles vs the unconditional control (which is expected NULL per MOM01), era-split, shared-draw nulls.
PRIOR: MED — mechanism is real and peer-reviewed; our own diagnostic non-replication is the standing caution.
[/CARD]

[CARD id=MC-14]
NAME: Pullback entry into established trend (second entry / Holy Grail / IB25 / ORB-retrace)
FAMILY: MOMENTUM
MECHANISM: Once initiative establishes direction, the first countertrend swing is supplied by profit-taking rather than new initiative (visibly lower countertrend volume); joining at the pullback improves entry price and stop geometry versus chasing the break.
MERGED-LEADS: A3/A7 (Raschke Holy Grail: ADX14>30 rising + pullback to 20-EMA, AIQ 1997 PDF); A11 (Adam Grimes: 5 years live OOS pullback signals, adamhgrimes.com 2024-10-02); A6-02 (dws-data nas-orb-backtester: ORB + retrace-to-VP-level entry, +21.2R/yr no costs); A2-14 (Dan Cooke IB25 limit entry); A8-12 (Jigsaw rule: countertrend swings show "way lower" volume); A5 (Wizdough second-entry, Angelo Muru two-legged pullback).
INDEPENDENT-SOURCES: 4 — Raschke (1990s), Grimes (live, unaudited), order-flow line (Jigsaw), multiple independent retrace implementations.
EVIDENCE-BEST: TESTIMONY of 5-yr live OOS + CODED-BACKTEST without costs.
OBSERVABLES: trend qualifier (ADX/IB direction/VWAP side), pullback depth (25%/50% of range), countertrend volume ratio.  DATA-CAPABLE-NOW: YES (NQ 1-min; volume ratio too).
NOVELTY-VS-REPO: POLICY — entry-policy novelty on breakout/momentum engines; the NOT-closed guard says entry/exit policy search was never done systematically. Distinct from closed trend-day→FADE (this is trend-day→JOIN).
HORIZON: minutes-hours.  COST-SENSITIVITY: LOW-MED (limit entries earn the spread).
CHEAPEST-FALSIFIER: on the SAME preregistered ORB/IB spec (MC-01/MC-04), matched-pair comparison of break-chase vs fixed-retrace limit entry (25%, 50%), identical signals, costs on — pure policy A/B.
PRIOR: MED.
[/CARD]

[CARD id=MC-15]
NAME: Early trend-day classification → hold to close
FAMILY: MOMENTUM
MECHANISM: A minority of sessions are one-way auctions identifiable early (open-drive, one-sided IB, persistent TICK/breadth skew, gap-and-go); the rational response is to stop fading and hold with the move into the close.
MERGED-LEADS: A3 (Steenbarger "Six Ways to Identify a Trend Day", TICK trend-day posts 2007-09); A6 (Ernie Chan trend-day late-entry, quantrocket/trend-day repo); A11 (Beat-the-Market Table 5: yesterday-was-trend-day → -2bps, negative carryover conditioning); A9 (Dalton day-type + open-type taxonomy, WindoTrader/mypivots); A2-11 (edgeful: bullish IB sequence → NY close green 76%).
INDEPENDENT-SOURCES: 3 — Steenbarger, Chan, Dalton lineage (+ edgeful numbers).
EVIDENCE-BEST: quantified blog studies (2006-09) + book-published rule; no modern audited test.
OBSERVABLES: 10:30 snapshot: IB one-sidedness, open type, TICK skew (2022+), gap status, range vs ATR.  DATA-CAPABLE-NOW: YES (NQ 1-min; internals minute 2022+ for the breadth version).
NOVELTY-VS-REPO: RAW-INFO/POLICY — trend-day detector→FADE policies are closed (selectivity ≈ exposure); the continuation/hold branch is untested; also distinct from W111's closed afternoon-participation fade.
HORIZON: 10:30 → 16:00.  COST-SENSITIVITY: LOW-MED (one entry, long hold).
CHEAPEST-FALSIFIER: trend-day score at 10:30 (IB one-sided + gap direction [+ TICK skew 2022+]); forward 10:30→close return vs matched unconditional control WITH the selectivity-vs-exposure decomposition printed (the exact stat that killed the fade version).
PRIOR: MED.
[/CARD]

[CARD id=MC-16]
NAME: Session-VWAP side/slope as intraday trend state
FAMILY: VWAP
MECHANISM: VWAP is the institutional execution benchmark; when price holds one side with slope, benchmark-pegged flows reinforce the move; side flips are cheap regime flips. Trend-following ON the VWAP side, not a fade.
MERGED-LEADS: A10-01 (Zarattini-Aziz "VWAP Holy Grail" SSRN 4631351: QQQ long-above/short-below, 671% claim); A6-11 (Conti DriftVwapPullback: VWAP-side drift + first countertrend 5m candle entry; replication PF 1.38 below its own gate); A2-15 (Bull Barbie VWAP-slope filter on ORB); A2-14 (anchored 09:30 VWAP as longs-only filter); A10 (TRADEPRO/SMB trend-filter restatements); A4 (Steenbarger VWAP-slope day-structure posts).
INDEPENDENT-SOURCES: 2-3 — Zarattini family (one effective source), Conti (ex-Nordea MM testimony + partial replication), retail convergence (correlated folklore).
EVIDENCE-BEST: CODED-BACKTEST (SSRN, net-of-commission claim) + independent replication that FAILED its own acceptance gate.
OBSERVABLES: session VWAP (typical-price x volume from 1-min), slope, price side, time-above-VWAP.  DATA-CAPABLE-NOW: YES (NQ 1-min; 2025-26 tick store bounds the 1-min VWAP approximation error).
NOVELTY-VS-REPO: REPRESENTATION — "VWAP anything" is explicitly NOT closed (never tested here).
HORIZON: intraday, EOD flat.  COST-SENSITIVITY: MED (side flips churn on flat-VWAP days).
CHEAPEST-FALSIFIER: NQ 1-min session-VWAP side rule 2006-2026, costs on, era-split, vs a price-only anchor control (e.g., side of 09:30 open / MA) — does VWAP beat a plain price anchor at all?
PRIOR: MED.
[/CARD]

[CARD id=MC-17]
NAME: Intraday anchor magnetism and band reversion (VWAP bands, session-open anchor)
FAMILY: VWAP
MECHANISM: Deviations from consensus anchors (session VWAP, session open, 08:00 open) revert as passive institutional interest accumulates against stretched prices — an intraday fair-value magnet with distance-dependent behavior zones.
MERGED-LEADS: A10 (einc58-netizen/vwap-mean-reversion-futures: ZN |z|≥2.5σ entry Sharpe 0.97 walk-forward, 6E LOSES with identical machinery; WhiteRabbit ES 1-session prototype; ojeology crypto; thevwap 4 trade types; TradingSim ≥0.4% separation claim); A2-03 (JJ Simon 09:30/14:00 fair-value reversion windows); A9 (nqstats am_tbr: ±0.25σ band touch → reversion to 08:00 open ~74%, time-decaying 83%→9%); A10 gap-flag (VWAP first-touch table apparently unpublished anywhere).
INDEPENDENT-SOURCES: 4 — einc58 (futures, honest cross-instrument negative), nqstats, JJ Simon (hand-tested), vendor folklore (correlated).
EVIDENCE-BEST: CODED-BACKTEST with walk-forward + prop-sim (ZN) including a same-machinery negative (6E) — the calibration point that stat-MR ≠ P&L.
OBSERVABLES: VWAP ±kσ bands, distance from 09:30/08:00 open in σ units, touch times.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: REPRESENTATION — VWAP not closed; distinct from the seven closed 2022-era fade geometries (anchor-relative distance, not move-relative fade).
HORIZON: minutes-hours, morning-weighted.  COST-SENSITIVITY: HIGH (fade entries).
CHEAPEST-FALSIFIER: build the NQ VWAP first-touch + band-reversion table 2006-2026 era-split as a DESCRIPTIVE deliverable before any strategy prereg — cheap, and apparently the first such table anywhere.
PRIOR: LOW for NQ trading (index intraday trendiness per MC-16 evidence; 6E warning) — the diagnostic table is worth owning regardless.
[/CARD]

[CARD id=MC-18]
NAME: Short-horizon oversold mean reversion in uptrend (RSI2 lineage)
FAMILY: MEANREV
MECHANISM: Multi-day pullbacks in uptrending equity indices revert (liquidity provision to impatient sellers); documented mostly in stocks, with its own authors reporting decay.
MERGED-LEADS: A7 (Connors RSI2 chartschool rules; Alvarez studies incl. edge shrinking 0.52%→0.33%/trade; quantifiedstrategies SPY CAGR 9%); A10 (Grant/Wolf/Yu JBF 2005 "Intraday price reversals in US stock index futures, 15-year study" — title-level; QuanTip streak-MR as overlay only).
INDEPENDENT-SOURCES: 2 — Connors/Alvarez family; Grant et al (peer-reviewed, futures).
EVIDENCE-BEST: PEER-REVIEWED (JBF 2005, title-level) + long-sample practitioner studies on stocks.
OBSERVABLES: RSI(2) on daily closes, 200-day MA filter, n-day exit.  DATA-CAPABLE-NOW: YES (NQ daily from 1-min or multi-market daily).
NOVELTY-VS-REPO: RAW-INFO — daily-horizon pullback MR is not in the closed list (closed intraday fades and daily TSMOM are different objects/signs).
HORIZON: 1-10 days.  COST-SENSITIVITY: LOW (daily).
CHEAPEST-FALSIFIER: RSI2<10 above 200d-MA on NQ daily 2006-2026 → next-3-day return vs circular-shift null; single shot, family-corrected.
PRIOR: LOW — instrument transfer weak and decay documented by its own proponents.
[/CARD]

[CARD id=MC-19]
NAME: Vol-stress next-day reversal (liquidity-provision premium)
FAMILY: MEANREV
MECHANISM: In high-realized-vol states, large one-day moves overshoot because risk-bearing capacity is scarce; providing liquidity (fading the move into the next session) earns a premium concentrated in stress regimes.
MERGED-LEADS: A15 (LIQREV01 dossier: 8/8 preregistered gates passed on the letter, N=455, $579/trade net, matched-placebo state spread ~$740/trade; red-team veto was REGIME-LOCALITY — a doctrine the owner has since REVOKED post-W115; the frozen shadow was silently dropped from MONITORING_CALENDAR = atlas fix #1); A13 (Hanna VIX-spike ≥30% above 10d-MA → bounce; SPX-up+VIX-up → pullback); A9/A7 (Steenbarger/Hanna large-gap-down reversion studies).
INDEPENDENT-SOURCES: 3 — in-house preregistered result, Hanna, Steenbarger (+ the academic liquidity-provision frame).
EVIDENCE-BEST: IN-HOUSE-PREREG 8-gate pass — the strongest evidence class in this entire wave.
OBSERVABLES: trailing rv5 percentile ≥0.90, prior-63-day return quantiles, next-session close-to-close.  DATA-CAPABLE-NOW: YES (already built; NQ 1-min substrate).
NOVELTY-VS-REPO: RAW-INFO — already repo-resident; the ACTION is restoring the LIQREV01 shadow to MONITORING_CALENDAR (cheapest high-value fix per atlas), not a new test. Distinct from closed CLOSEREV01/TOMFLOW.
HORIZON: next session.  COST-SENSITIVITY: LOW ($14.36/RT on a ~$580 gross edge).
CHEAPEST-FALSIFIER: none needed — restore the frozen shadow; the forward ADVANCE gate (net>0 AND ≥0 on Solar's forward losing days) is already defined.
PRIOR: HIGH — with the honest caveat the veto documented: all statistical weight is post-2020, effective N ≈ 5 macro clusters.
[/CARD]

[CARD id=MC-20]
NAME: Range compression → expansion (NR7/NR4/inside-day/triangle conditioning)
FAMILY: VOL
MECHANISM: Narrow daily ranges mark finished two-sided auctions (Wyckoff via Crabel); the next directional move launches from compression — and the strongest modern datum is that intraday momentum strategies earn MORE after compression days.
MERGED-LEADS: A7 (Hanna WR7→NR7: next-day ~10x unconditional NDX mean; oxfordstrat NR patterns; tradingsetupsreview NR7); A11 (Beat-the-Market Table 5: NR4 22bps t=5.14 SR 3.2 vs 12bps unconditional; NR7 t=3.07; Triangle t=3.19; Bulkowski: NR7 weak STANDALONE on stocks); A9/A3 (tradingstats: IB<0.5xATR → 98.7% breakout, median extension 74.8% vs 22.3% for wide IB).
INDEPENDENT-SOURCES: 4 — Crabel (1990), Hanna (2008), Zarattini et al (2024), tradingstats (+Bulkowski's standalone negative sharpening the "conditioner not signal" reading).
EVIDENCE-BEST: CODED-BACKTEST conditional t-stats in an SSRN paper + convergent independent computations.
OBSERVABLES: daily range ranks (NR4/NR7), inside/outside day, triangle (2-day nested), IB/ATR ratio.  DATA-CAPABLE-NOW: YES (NQ daily + 1-min).
NOVELTY-VS-REPO: RAW-INFO — daily compression state as a conditioner for intraday engines; no closed scope covers it (H2 closed calendar day-types, not price-pattern states).
HORIZON: next session intraday.  COST-SENSITIVITY: LOW (conditioner, adds no trades).
CHEAPEST-FALSIFIER: NR4/NR7/inside/triangle flags on NQ daily → condition (a) next-day realized range, (b) the B3-ORB control net, (c) FOLLOW_MORNING net; matched unconditional controls in the same wave, shared-draw nulls across the pattern family.
PRIOR: HIGH — multiple independent sources, coherent mechanism, near-zero cost, and it conditions engines already owned.
[/CARD]

[CARD id=MC-21]
NAME: Opening volatility → day-range/day-type forecast
FAMILY: VOL
MECHANISM: First-30-minute volatility and gap size set the scale of the entire session (intraday vol-curve shape persistence); quiet opens → compressed days, active opens → expanded ranges. A risk-specification signal, not a directional one.
MERGED-LEADS: A11 (Steenbarger 2006: first-30-min |move| ≤0.05% → median day range 0.61% vs 0.75%; gap size ↔ day relative range corr 0.30); A1-12 (Andersen/Thyrsgaard/Todorov JASA 2019 periodicity + 2025 curve-shape change detection); A14-03 (Mesfin VVG classifier: regimes REAL, standalone trading NEGATIVE).
INDEPENDENT-SOURCES: 3 — Steenbarger, Andersen academic line, Mesfin.
EVIDENCE-BEST: PEER-REVIEWED (JASA 2019) for the periodicity object.
OBSERVABLES: 09:30-10:00 realized vol, overnight gap, first-bar volume vs 20d baseline.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: REPRESENTATION as RISK SPECIFICATION — explicitly NOT closed ("vol-state as sizing"); must never masquerade as information alpha (leverage rule): hold gross exposure fixed in any test.
HORIZON: same session.  COST-SENSITIVITY: LOW.
CHEAPEST-FALSIFIER: first-30-min vol tercile → rest-of-day realized-range forecast skill on NQ 1-min 2006-2026; then a size-throttle variant of one existing engine with gross exposure held constant.
PRIOR: MED.
[/CARD]

[CARD id=MC-22]
NAME: High-VIX gate on intraday momentum
FAMILY: VOL
MECHANISM: Intraday trend/ORB profits concentrate in high-volatility states — more rebalancing flow and trapped inventory, and wider noise bands finally clear the cost bar; low-vol days are cost-dominated chop.
MERGED-LEADS: A11 (Beat-the-Market VIX conditioner: Sharpe monotone in VIX-at-open; Lundström "Day trading returns across volatility states": ~150bp/day S&P spread between vol states, IFTA-published; Holmberg et al FRL 2013 vol-ORB); A12-15 (Gao JFE: stronger on high-vol/announcement days); A6-08 (QC replication profitable ONLY in the 2020 crash window: Sharpe 1.45 vs -1.47 elsewhere — accidental confirmation); A10 (SMB VIX position-sizing).
INDEPENDENT-SOURCES: 4 — Zarattini family, Lundström (peer-reviewed lineage), Gao et al (JFE), QC's unintended era decomposition.
EVIDENCE-BEST: PEER-REVIEWED (JFE 2018; FRL 2013) + consistent SSRN conditioning tables.
OBSERVABLES: VIX/VXN at open (certified daily), realized-vol percentile, engine nets by vol tercile.  DATA-CAPABLE-NOW: YES (certified VIX/VXN daily + NQ 1-min; internals minute 2022+ for intraday variant).
NOVELTY-VS-REPO: RAW-INFO — H1 closed DAILY VX-basis/ratio terciles → next-session MEAN; this gates INTRADAY strategy nets on vol LEVEL (different observable, horizon, and decision role); intraday VIX/VXN and vol-state-as-sizing are both explicitly NOT closed.
HORIZON: same session.  COST-SENSITIVITY: LOW (gate).
CHEAPEST-FALSIFIER: VIX-at-open tercile split of the B3-ORB control net and FOLLOW_MORNING net, matched unconditional controls, era-split, one shared draw per family.
PRIOR: HIGH — three independent quantified sources agree on direction; test is nearly free.
[/CARD]

[CARD id=MC-23]
NAME: Breadth/TICK internals conditioning
FAMILY: INTERNALS
MECHANISM: One-sided NYSE TICK/breadth = market-wide program initiative, separating conviction moves from local NQ noise; persistent skew marks trend days, extremes mark exhaustion/washouts.
MERGED-LEADS: A3 (Steenbarger: adjusted TICK ±500 trending vs ±200 range thresholds, cumulative adjusted TICK construction, TICK trend-day posts; Hanna TomOscillator %Rank<1% → 23/25 next-day up; Raschke first-30-min NYSE volume tone + breadth confirmation); A2/A11 (TICK-validated ORB folklore); A16-06/-07/-08 (internals 1-min store 2022-01→2026-07 acquired, information test UNRUN — the flagged prereg).
INDEPENDENT-SOURCES: 3 — Steenbarger, Hanna, Raschke; plus our own unopened dataset.
EVIDENCE-BEST: quantified blog studies (2007-2020) + one small-N modern study (TomOscillator).
OBSERVABLES: $TICK 1-min (own 2022+; NT8 claims back to ~2013 unmaterialized), $TRIN, TICK skew/extreme states.  DATA-CAPABLE-NOW: YES (internals minute 2022+; RTH-only, covers ~36% of P1 decisions per registry).
NOVELTY-VS-REPO: RAW-INFO — internals setups on 2022+ minute data explicitly NOT closed (only regime-labels tested); must avoid the shape of W111's closed afternoon-participation fade.
HORIZON: 5-60 min conditional windows.  COST-SENSITIVITY: LOW (gate/conditioner).
CHEAPEST-FALSIFIER: the already-flagged internals prereg: TICK skew/extreme states → conditional NQ forward returns at 5-60 min, 2022→pre-burn, matched unconditional controls, one family.
PRIOR: MED — data owned, untested, three independent practitioner lineages converge.
[/CARD]

[CARD id=MC-24]
NAME: ES↔NQ agreement/divergence state (minute-scale confirmation)
FAMILY: CROSSMKT
MECHANISM: Common flow moves both indexes; divergence isolates NQ's idiosyncratic (mega-cap/duration) component. HF lead-lag is arbitraged away (Budish), but agreement at decision points survives as a STATE that confirms initiative.
MERGED-LEADS: A6-01 (giovannibrusco: NQ-09:25-agreement filter on QQQ ORB, t=2.05 vs placebo t=1.27 — but 76% of filtered PnL from 2022); A2-04/-18 (ICT SMT divergence folklore); A13 (Hasbrouck 2003 JF price discovery; Budish QJE 2015; NinjaTrader ES-vs-NQ divergence idea; honoreaa ES-NQ spread MR — full-sample beta lookahead, cautionary); A16-01 (59 joint ES↔NQ RTH-complete BBO sessions; 121 joint tick dates pre-burn).
INDEPENDENT-SOURCES: 3 — academic price-discovery line, coded replication with placebo, ICT folklore (independent restatement).
EVIDENCE-BEST: CODED-BACKTEST with placebo control (t=2.05).
OBSERVABLES: ES 1-min direction/return vs NQ at decision bars; sign agreement; divergence magnitude.  DATA-CAPABLE-NOW: YES (ES/RTY/YM 1-min 2022+; joint tick+BBO 2025-26).
NOVELTY-VS-REPO: RAW-INFO — closed: ES↔NQ SUB-MINUTE state (-$503/session) and 1-min lead-lag (ms-arbitraged, dead list). Material difference: minute-scale sign AGREEMENT as an entry GATE (state/confirmation role, not lead-lag prediction).
HORIZON: at entry decisions, intraday.  COST-SENSITIVITY: LOW (gate).
CHEAPEST-FALSIFIER: add an ES-direction-agreement gate to the B3-ORB control on 2022+ joint 1-min data; matched ungated control; print the 2022-concentration check that flagged the source.
PRIOR: MED.
[/CARD]

[CARD id=MC-25]
NAME: Cross-asset risk-state conditioners (dollar, rates shocks, BTC weekend, implied correlation)
FAMILY: CROSSMKT
MECHANISM: NQ's duration and mega-cap concentration make it differentially sensitive to dollar-funding stress, rate-path shocks, and index-correlation regimes; weekend crypto acts as a risk-appetite thermometer while equities are closed.
MERGED-LEADS: A13 (BIS work592/work695 dollar-as-risk-barometer; Gürkaynak/Sack/Swanson 2005 target+path factors; FRBSF USMPD free intraday FOMC event windows; Mourey/Shahrour/Șoiman FRL 2025 BTC-weekend→Monday, negative-side only, regime shift post-LUNA 2022-05; Cboe COR3M/VXN CSVs $0 from 2006; RTY floating-rate divergence ideas).
INDEPENDENT-SOURCES: 4 — BIS, Fed/GSS-USMPD, Mourey et al (peer-reviewed), Cboe data surface.
EVIDENCE-BEST: PEER-REVIEWED (FRL 2025; IJCB 2005).
OBSERVABLES: DXY daily, 2s10s/FOMC-window shocks (USMPD), BTC Sat-Sun return, COR3M level.  DATA-CAPABLE-NOW: PARTIAL (multi-market daily owned; COR3M/USMPD/BTC are $0 acquisitions; virgin-seal discipline applies to any pull).
NOVELTY-VS-REPO: RAW-INFO — H1 (VX daily basis) and H7 (COT terciles) closures show daily-conditioner→next-session-mean is a hard family; BTC-weekend is Monday-specific, sign-asymmetric, and era-fragile — must preregister the post-2022-05 era explicitly.
HORIZON: next session / next week.  COST-SENSITIVITY: LOW.
CHEAPEST-FALSIFIER: one shot: BTC weekend-return sign → Monday NQ session return on multi-market daily 2017-2026, era-split at 2022-05, H1/H2-style shared-draw nulls, family-corrected with the other conditioners in this card.
PRIOR: LOW.
[/CARD]

[CARD id=MC-26]
NAME: Dealer gamma / 0DTE positioning states
FAMILY: CROSSMKT
MECHANISM: Dealers' net gamma sign flips the market between mean-reversion (positive gamma: hedging against moves) and extension (negative: hedging with moves); 0DTE concentrates this intraday; charm/vanna flows allegedly pin price into the close.
MERGED-LEADS: A3 (SpotGamma GEX levels/call-put walls, vanna-charm posts — explicitly NO quantified evidence; Karsan threads; squeezemetrics); A1-09/-10/-11 (Barbon-Buraschi Gamma Fragility SSRN 3725454; 0DTE volatility papers pro and con; retail 0DTE loses); A12 (Brogaard 0DTE +9.1% vol).
INDEPENDENT-SOURCES: 2 — academic line (Barbon/Buraschi et al), vendor school (Karsan/SpotGamma/SqueezeMetrics — internally correlated, one theory family).
EVIDENCE-BEST: SSRN working papers (contested — an attenuation counter-paper exists).
OBSERVABLES: strike-level OI, dealer-sign inference, gamma-flip level, 0DTE volume share.  DATA-CAPABLE-NOW: NO (needs options positioning data — GAMMA00 owner-gated purchase).
NOVELTY-VS-REPO: RAW-INFO — GEX dashboards are DEAD-LISTED (dealer-sign free parameter, OI staleness); a material difference requires identified-sign positioning (academic method), not a dashboard replica. Blocked on data regardless.
HORIZON: intraday to EOD.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: none on owned data — parked pending owner GAMMA00 decision. Weak $0 diagnostic only: |return| damping near round-strike levels on NQ 1-min, stated as descriptive.
PRIOR: LOW (as runnable here).
[/CARD]

[CARD id=MC-27]
NAME: Minute-scale order-flow imbalance as gate (aggregated OFI / true CumDelta)
FAMILY: ORDERFLOW
MECHANISM: Net aggressor flow at the best quotes moves price linearly (slope ∝ 1/depth) — a replicable fact; the open question is whether MINUTE-aggregated signed flow carries state that improves existing engines' decisions after costs.
MERGED-LEADS: A8-01 (Cont/Kukanov/Stoikov arXiv 1011.6402, J Fin Econometrics 2014); A8-02 (Takahashi: around macro news price impact rises, flow impact falls); A8-03/-04 (multi-level + lagged cross-asset OFI; regime/horizon dependence); A15 (parked "CumDelta as delta gate with TRUE tick delta" row; W54/W55 intrabar-unlock rows); A16 (grid1s NQ/ES second-grid stores with sflow column; MNQ tick last-only caveat).
INDEPENDENT-SOURCES: 3+ academic groups, peer-reviewed core.
EVIDENCE-BEST: PEER-REVIEWED (2014) for the contemporaneous relation; predictive-net-of-cost version untested at minute scale here.
OBSERVABLES: signed trades (bid/ask test) → per-minute delta/CVD, best-quote OFI, spread state.  DATA-CAPABLE-NOW: PARTIAL (2025-26 NQ/ES tick+BBO pre-burn slice incl. 40 stratified dev sessions; not the 20-year history).
NOVELTY-VS-REPO: RAW-INFO — closed: sub-minute BBO taking (MS-BBO -$1,786/session) and seconds-scale OFI (dead list, dissipates ≤1s). Material difference: minute-scale OFI as a GATE on existing engines' decision bars (state role, no new taking), which is exactly the parked CumDelta-gate idea.
HORIZON: gate at decision bars, minutes.  COST-SENSITIVITY: LOW (gate adds no trades).
CHEAPEST-FALSIFIER: 1-min signed-flow z as gate on P1/B-MOM decision bars over the pre-burn tick store; matched ungated control; contemporaneous-OFI replication printed as the sanity row (expected to replicate, NOT an edge).
PRIOR: MED.
[/CARD]

[CARD id=MC-28]
NAME: Footprint absorption / stacked imbalance / CVD divergence
FAMILY: ORDERFLOW
MECHANISM: High traded volume without price progress = passive absorption (initiative failing → reversal risk); stacked diagonal bid/ask imbalances mark institutional levels (S/R); CVD-vs-price divergence at range breaks flags trapped traders.
MERGED-LEADS: A8-06..A8-16 (Sierra Numbers Bars diagonal definitions + thresholds 25/50/75%; NT8 volumetric defaults, UpDownTick fallback; ATAS stacked-imbalance/CVD/FRVP; Bookmap CVD-divergence + stop-run posts; Jigsaw 2011 tape-first lessons; Grady "DOM ≈ 20% of the story"); A2-16 (Futures Flow delta-trap grading); A5 (orderflows.com Turns; LVTI large-lot prints; ATAS named setups).
INDEPENDENT-SOURCES: effectively 1 — a single MarketDelta-era (~2005-2010) folklore family restated by ~6 vendors; zero quantified evidence anywhere in the corpus (A8's explicit cross-cutting finding). Treat as ONE correlated source for null design.
EVIDENCE-BEST: EXAMPLES only.
OBSERVABLES: volume-at-price with aggressor side, per-bar delta, CVD, diagonal imbalance ratios ≥1.5-3.0.  DATA-CAPABLE-NOW: PARTIAL (computable from 2025-26 signed ticks; iceberg/depth variants BLOCKED — DOM pause, no MBO).
NOVELTY-VS-REPO: REPRESENTATION — new observables here; nothing closed covers footprint constructs; doubles as the absorption discriminator MC-08 needs.
HORIZON: 5-30 min.  COST-SENSITIVITY: HIGH if traded standalone; LOW as discriminator.
CHEAPEST-FALSIFIER: define absorption events (volume z>2, |Δprice|<k ticks, at swing extreme) on the pre-burn tick store; forward 5-30-min returns vs volume-matched control events — the first quantified test of the whole folklore family.
PRIOR: LOW — no numbers exist anywhere; infrastructure value is real.
[/CARD]

[CARD id=MC-29]
NAME: Pre-scheduled-release drift (30-minute correct-direction positioning)
FAMILY: EVENT
MECHANISM: Informed or faster-processing flow positions ahead of macro releases; prices drift in the eventual announcement direction ~30 minutes pre-release, accounting for ~40-50% of total adjustment (Kurov). The pre-FOMC 2pm drift is the famous (and decayed) special case.
MERGED-LEADS: A1-05/A12-08 (Kurov/Sancetta/Strasser/Wolfe JFQA 2019, 7 of 21 releases); A12-01 (Lucca-Moench JF 2015 pre-FOMC 49bp); A12-09 (Hanna NFP open→close streak).
INDEPENDENT-SOURCES: 3 academic teams.
EVIDENCE-BEST: PEER-REVIEWED (JFQA 2019, JF 2015).
OBSERVABLES: release calendar+times (must build), NQ 1-min path -120..0 min, release-direction proxy.  DATA-CAPABLE-NOW: PARTIAL (prices owned; calendars are a $0 build; using realized outcomes for direction is hindsight — honest test correlates pre-drift with post-move).
NOVELTY-VS-REPO: RAW-INFO — pre-FOMC drift is DEAD-LISTED (2015) so the FOMC branch needs a decay story; H2 closed day-MEANS; event PATHS are explicitly NOT closed — the pre-release WINDOW path is the live object.
HORIZON: -30..0 min around releases.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: event-anchored average path ±120 min around CPI/NFP/FOMC on NQ 1-min 2010-2026 era-split; vol and |drift| first; direction only with a preregistered pre-release proxy.
PRIOR: MED for the path/vol object; LOW for tradable directional drift.
[/CARD]

[CARD id=MC-30]
NAME: Post-release response path (fast adjustment, independent continuation, vol decay)
FAMILY: EVENT
MECHANISM: Scheduled news is absorbed largely within the first minute; volatility stays elevated ~15 min and decays as a power law; subsequent direction is INDEPENDENT of the initial jump (Ederington-Lee) — the null-shape any "post-CPI continuation/fade" claim must beat.
MERGED-LEADS: A12-06/-07 (Ederington-Lee JF 1993; Omori-law vol decay after rate shocks, Petersen arXiv 0903.0010); A8-02 (Takahashi 1-sec SVAR around macro news); A12-19 registry (Build Alpha event windows, kept as registry not lead).
INDEPENDENT-SOURCES: 3 academic.
EVIDENCE-BEST: PEER-REVIEWED (JF 1993).
OBSERVABLES: release timestamps, 1/5/15/60-min post-release returns conditional on initial 1-min move sign/size, vol curve.  DATA-CAPABLE-NOW: PARTIAL (calendar build; NQ 1-min owned).
NOVELTY-VS-REPO: RAW-INFO — event response PATHS/vol explicitly NOT closed (only day-means tested in H2); W118 caution noted: at ENDOGENOUS triggers continuation won — this is the exogenous-trigger version.
HORIZON: 0-60 min post-release.  COST-SENSITIVITY: MED-HIGH.
CHEAPEST-FALSIFIER: post-release continuation-vs-reversal table conditional on initial 1-min move, CPI/NFP/FOMC 2010-2026, vs matched non-event minutes; Ederington-Lee independence is the null.
PRIOR: MED.
[/CARD]

[CARD id=MC-31]
NAME: Fed-cycle multi-day drift (monetary momentum, even weeks)
FAMILY: EVENT
MECHANISM: Informal Fed communication cadence structures the equity premium in FOMC-cycle time (weeks 0/2/4/6); returns drift for ~25 days before signed policy surprises.
MERGED-LEADS: A1-06/A12-02 (Neuhierl-Weber NBER w24748); A12-03 (Cieslak/Morse/Vissing-Jorgensen JF 2019); A12-04 (Kroencke et al FOMC risk shift JME 2021).
INDEPENDENT-SOURCES: 3 academic teams.
EVIDENCE-BEST: PEER-REVIEWED (JF 2019).
OBSERVABLES: FOMC calendar, cycle-week index, daily NQ.  DATA-CAPABLE-NOW: YES (daily + free calendar).
NOVELTY-VS-REPO: RAW-INFO — H2 closed FOMC-cycle DAY-TYPES → session mean at the family bar; the even-week object is materially the same population sliced at a longer horizon → HIGH rescue risk. Only admissible form: cycle-week as a conditioner on an intraday engine (different decision role), stated in advance.
HORIZON: multi-day.  COST-SENSITIVITY: LOW.
CHEAPEST-FALSIFIER: cycle-week × existing-engine net decomposition with matched controls — explicitly NOT a re-test of H2's closed population.
PRIOR: LOW.
[/CARD]

[CARD id=MC-32]
NAME: Scheduled flow events (opex, index rebalance, Treasury auctions, month-end)
FAMILY: EVENT
MECHANISM: Pre-announced mechanical flows — expiration unwinds, index reconstitution, auction supply digestion, month-end institutional rebalancing — create anticipatable price-pressure paths with post-event recovery.
MERGED-LEADS: A12-10/-19/-20/-21/-22 (Lou/Yan/Zhang RFS 2013 auction cycle; Stoll-Whaley expiration; Hanna opex-Friday last-30-min weak since 2018; Franz NDX rebalance intraday SSRN 3459744 metadata-only; Russell recon $217B close volume); A1-03/-04 (Hazelkorn basis/rolls; Etula dash-for-cash); A3 (Karsan JHEQX quarterly collar threads).
INDEPENDENT-SOURCES: 4+ academic teams (auction result is Treasuries, not equities — transfer assumption explicit).
EVIDENCE-BEST: PEER-REVIEWED (RFS 2013).
OBSERVABLES: opex/recon/auction/month-end calendars (must build), day-anchored intraday paths.  DATA-CAPABLE-NOW: PARTIAL (prices owned, calendars $0 build).
NOVELTY-VS-REPO: RAW-INFO — H2 closed OPEX-week and ToM DAY-TYPE means; index-add effect decayed per Greenwood-Sammon. Live branch: intraday PATH on those days + NDX-specific reconstitution (never tested here).
HORIZON: specific days, intraday paths.  COST-SENSITIVITY: MED.
CHEAPEST-FALSIFIER: NDX reconstitution dates (public) → close-anchored intraday path day-before/day-of on NQ 1-min vs matched control days.
PRIOR: LOW.
[/CARD]

[CARD id=MC-33]
NAME: Day-of-week × strategy interaction
FAMILY: EVENT
MECHANISM: Flow composition differs by weekday (Monday gap digestion, Friday de-risking), modulating STRATEGY nets even where raw day-of-week means are flat — an interaction claim, not a level claim.
MERGED-LEADS: A2-01 (Monday structurally -$13K in a 6-yr NQ ORB); A2-07 (Unger/Crabel: Friday-only shorts avg trade $30→$155, stable 4 sub-periods); A11 (Zarattini: Monday BETTER for ORB, n.s. for intraday momentum; Wed/Thu/Fri significant).
INDEPENDENT-SOURCES: 3 coded tests, partially contradictory (Monday bad vs Monday good — different strategies).
EVIDENCE-BEST: CODED-BACKTEST, in-sample flavored.
OBSERVABLES: weekday × engine net.  DATA-CAPABLE-NOW: YES.
NOVELTY-VS-REPO: POLICY — raw DOW means are doubly closed (H2 NULL 0/11; dead list 2004/re-measured 2026). Only the interaction-with-engine form is admissible, with the raw-mean control printed; extreme selection-luck hazard, 5-way family correction mandatory.
HORIZON: conditioner.  COST-SENSITIVITY: LOW.
CHEAPEST-FALSIFIER: DOW × B3-ORB-control net decomposition, 5-way corrected, descriptive unless it survives the family bar.
PRIOR: LOW.
[/CARD]

[CARD id=MC-34]
NAME: Event-time / information-time representations and regime models
FAMILY: ML
MECHANISM: Sampling by activity (volume/dollar/imbalance bars) or latent regime (HMM/classifier states) aligns observations with information arrival, improving signal stationarity versus clock bars — a substrate claim, not a directional edge.
MERGED-LEADS: A14-01/-02 (VPIN volume clock + Andersen-Bondarenko rebuttal: TR-VPIN exceeded on 71 prior days); A14-03 (Mesfin VVG MNQ classifier: regimes real, trading NEGATIVE); A14-11 (freq-controlled bar comparison, crypto: tick vol bars -69% serial dependence, no PnL); A14-12 (DC+HMM, FX); A14-17 (IOHMM methodology-only); A15 (parked rows: event-based segmentation; efficiency-chop "idea right, estimator wrong").
INDEPENDENT-SOURCES: 3-4 academic/practitioner lines; the only on-instrument test (MNQ) is NEGATIVE for standalone trading.
EVIDENCE-BEST: PEER-REVIEWED statistical-quality comparison (no PnL); best on-target datapoint is a negative.
OBSERVABLES: volume/dollar bar construction from ticks (2025-26) or 1-min proxies (2006-26); regime state series.  DATA-CAPABLE-NOW: YES (proxies) / PARTIAL (true tick bars).
NOVELTY-VS-REPO: REPRESENTATION — matches the parked event-based-segmentation row; VPIN is DEAD-LISTED, so any VPIN-flavored test must carry the Andersen-Bondarenko realized-vol matched control.
HORIZON: substrate.  COST-SENSITIVITY: LOW (no trades of its own).
CHEAPEST-FALSIFIER: rebuild ONE existing engine's decision series on volume bars vs clock bars at matched decision counts — does anything leave the noise band?
PRIOR: LOW as standalone; value is substrate for other cards.
[/CARD]

[CARD id=MC-35]
NAME: Overlay policies on existing engines (meta-labeling, calibrated sizing, fast-alpha timing)
FAMILY: POLICY
MECHANISM: Keep the primary engine's signals; add a secondary layer that (a) filters/sizes trades by predicted success probability (meta-labeling + probability calibration) or (b) times entries with a fast mean-reversion signal that is not tradable standalone but improves execution timing (QuanTip: +~200bp CAGR as overlay).
MERGED-LEADS: A14-08/-09/-10 (Hudson & Thames ES E-mini test: MR precision 0.17→0.20, accuracy 17%→63%; JFDS trilogy 2022-23 incl. "calibration significantly improves fixed position sizing"; SAE+triple-barrier); A10-04 (Pagani-Zarattini QuanTip, SPY 2007-26, Sharpe 0.87→0.99); A5 (BlackBird trade-management policy family); A15 (NOT-closed policy-novelty guard).
INDEPENDENT-SOURCES: 3 — Lopez-de-Prado/JFDS school, Hudson & Thames (blog-grade ES OOS), Concretum overlay paper.
EVIDENCE-BEST: journal-published (JFDS 2022-23), though largely controlled experiments; one on-futures blog backtest.
OBSERVABLES: own engines' trade ledgers + 3-5 pre-frozen features; calibrated probabilities; sizing maps.  DATA-CAPABLE-NOW: YES (entirely in-house).
NOVELTY-VS-REPO: POLICY — exactly the NOT-closed "re-entry/exit/sizing POLICY novelty on existing engines never searched systematically". Must dodge two closures: state-veto-on-P1 (all 8 cells worse → use probabilistic SIZING not binary veto, or target non-P1 engines) and the leverage-masquerade rule (hold gross exposure fixed in every comparison).
HORIZON: per-trade overlay.  COST-SENSITIVITY: LOW.
CHEAPEST-FALSIFIER: meta-label FOLLOW_MORNING (or B-MOM) trades with 3 pre-frozen features; calibrated-sizing vs fixed-sizing at fixed gross exposure, LOYO folds, matched-control printed.
PRIOR: HIGH — quantified world evidence + the repo's own guard says this lane was never searched.
[/CARD]

[CARD id=MC-36]
NAME: Stop/target geometry on breakout engines (wide-vs-tight, asymmetry, trailing, MAE-informed)
FAMILY: POLICY
MECHANISM: A fixed-signal engine's P&L is reshaped by exit geometry, and the world's coded studies CONTRADICT each other — wider stops uniformly better (A2-01 grid) vs 25%-of-range tight stops +1971R vs wide -698R (reddit NQ study) vs half-target/full-stop 69% WR but EV-max at full/full (1.17M-trade grid). The disagreement itself is the finding: geometry interacts with entry type and instrument, and is cheaply decidable per engine.
MERGED-LEADS: A2-01 (16-combo grid, 75SL/100TP best); A2-06 (TOS Indicators 1,178,668 ORB trades); A3 (reddit 1qcyt3h stop-placement study); A2-03 (ATR-tiered stops); A5 (BlackBird HWM protection); A8 (Jigsaw 5 exit rules); A15 (W42: winners' median MAE 0.86 ATR ≈ stop level — stop cuts winners; W55 hold-duration prize; both name intrabar/tick data as the unlock).
INDEPENDENT-SOURCES: 3+ coded studies, mutually contradictory; plus the repo's own W42/W55 measured rows.
EVIDENCE-BEST: LARGE-N coded grids (in-sample) + in-house measured MAE diagnostics.
OBSERVABLES: per-trade MAE/MFE paths (tick store for intrabar truth), stop/target multiples, trailing rules.  DATA-CAPABLE-NOW: YES (engines + 2025-26 tick store for intrabar paths; 1-min approximation flagged).
NOVELTY-VS-REPO: POLICY — same NOT-closed policy guard; W42/W55 explicitly say intrabar information is the unlock, and the tick store now exists.
HORIZON: per-trade.  COST-SENSITIVITY: LOW (policy change).
CHEAPEST-FALSIFIER: MAE/MFE distribution study on an existing engine's trades using tick-store intrabar paths (the exact W42 unlock), then ONE preregistered stop-policy change vs current policy.
PRIOR: MED.
[/CARD]

[CARD id=MC-37]
NAME: Backtest-realism battery (bar construction, fills, latency, optimizer leakage)
FAMILY: EXECUTION
MECHANISM: Not an edge — a defense. Renko/Heikin-Ashi backtests inflate results (same SMA cross: $1,987 on 1-min vs $10,200 Renko vs $22,300 HA); 1-min bars cannot sequence intra-bar stop-vs-target; a 1-bar delay flips published edges (Mesfin London signal t +5.15 → -3.56); "live optimizers" displayed in indicators are in-sample selection.
MERGED-LEADS: A2-17 (Sosikian NT8 demo); A6-15 (gbBacktester fill mechanics: limit fills on penetration not touch, stops trigger on last fill at quote); A6 (robbyrobaz 1-min sequencing caveat; LuxAlgo ATR-trail "optimizer" = live in-sample selection); A11 (Mesfin delay sensitivity); A14 (domain evidence-grade map).
INDEPENDENT-SOURCES: 4 independent demonstrations.
EVIDENCE-BEST: reproducible demonstrations (strongest possible for a methods claim).
OBSERVABLES: harness checks, not market data.  DATA-CAPABLE-NOW: YES.
NOVELTY-VS-REPO: POLICY (harness) — consistent with existing B1-harness discipline and the W52 phase-error history; adds three world-sourced checks: delay+1 sensitivity, intrabar path check on the tick store, no displayed-optimizer parameters.
HORIZON: n/a.  COST-SENSITIVITY: n/a.
CHEAPEST-FALSIFIER: standing checklist appended to every new engine's gate table: (1) delay+1 rerun, (2) intrabar stop/target sequencing check on tick store, (3) optimizer-provenance audit.
PRIOR: HIGH that these effects corrupt naive tests (methods card, not an alpha card).
[/CARD]

---

# STRATEGY FAMILY TREE

- OPENING — MC-01 (ORB continuation) · MC-02 (vol-scaled open bands) · MC-03 (gap fill/continuation)
- PROFILE — MC-04 (IB conditioning) · MC-05 (80% rule) · MC-06 (poor-structure repair) · MC-07 (reference-level magnetism)
- PATH — MC-08 (sweep-and-reclaim reversal) · MC-09 (FVG retracement) · MC-10 (trade-burst self-excitation)
- TIMEOFDAY — MC-11 (fixed clock windows) · MC-12 (ETH session-hour structure)
- MOMENTUM — MC-13 (late-day hedging-demand momentum) · MC-14 (pullback entry in trend) · MC-15 (trend-day classification → hold)
- VWAP — MC-16 (VWAP side/slope trend state) · MC-17 (anchor magnetism / band reversion)
- MEANREV — MC-18 (RSI2 daily pullback MR) · MC-19 (vol-stress next-day reversal)
- VOL — MC-20 (compression → expansion) · MC-21 (opening vol → day range) · MC-22 (high-VIX gate on intraday momentum)
- INTERNALS — MC-23 (TICK/breadth conditioning)
- CROSSMKT — MC-24 (ES↔NQ agreement state) · MC-25 (cross-asset risk conditioners) · MC-26 (dealer gamma/0DTE, data-gated)
- ORDERFLOW — MC-27 (minute-scale OFI gate) · MC-28 (footprint absorption/CVD)
- EVENT — MC-29 (pre-release drift) · MC-30 (post-release response path) · MC-31 (Fed-cycle drift) · MC-32 (scheduled flow events) · MC-33 (DOW × strategy interaction)
- ML — MC-34 (event-time bars & regime models)
- POLICY — MC-35 (overlay policies: meta-label/sizing/timing) · MC-36 (stop/target geometry)
- EXECUTION — MC-37 (backtest-realism battery)

Cross-links: MC-28 supplies the discriminator MC-08 needs; MC-20/MC-22/MC-23/MC-24/MC-33 are conditioners whose natural test bed is MC-01's control; MC-34 is substrate for MC-27/MC-28; MC-36/MC-37 apply to every engine.

---

# SOURCE GRAPH — lead-clusters that are one source copied around

1. **ICT / Michael Huddleston cluster (largest single-guru copy network, ~18 leads across 5 scouts).** Original: Inner Circle Trader (Huddleston) — itself a rebrand of Connors/Raschke "Street Smarts" 1995 Turtle Soup for the sweep object. Derivatives found: A2-02/-04/-05/-10/-18 (DionTrades, Trader Kane, Trader Zan, Percoco, BionicNQ), A3 silver-bullet cluster (backtrex, howtotrade, reddit tests, GitHub STAR-EA/sb-watchbot/yuvrajsingh/BAKOME), A6-03/-04/-06 (b-bot, ict-cameron, mes-smc), TradingView LunqFX/CantoLab FVG scripts. Adam Mancini's "failed breakdown" is a parallel rebrand of the same underlying object (per A3's three-generation lineage). Only the NUMERIC backtests are independent evidence; the claims are one source.
2. **Crabel/ORB cluster (largest mechanism network overall).** Original: Toby Crabel 1990 (crediting Wyckoff); modern re-igniter: Zarattini & Aziz 2023 SSRN 4416622. Copies/tests: A2-01/-06/-07/-08/-09/-15, A3 reddit ORB posters (genuinely independent numerics), A4-03/-09/-11, A6-01/-02/-13 + 3 more GitHub replications, A7 oxfordstrat/netpicks, A11 census. Two roots, dozens of derivative restatements.
3. **Zarattini/Concretum author family.** Five papers + QuanTip (ORB QQQ 4416622, stocks-in-play 4729284, SPY momentum 4824172, VWAP 4631351, QuanTip) = ONE effective source amplified on fintwit; GitHub replications (giovannibrusco, Ascensao, alienblack) are independent tests of it.
4. **Dalton/Steidlmayer CBOT profile lineage.** Original: Steidlmayer (CBOT, 1980s), popularized by Dalton "Mind Over Markets". Restaters: mypivots, ShadowTrader, Vtrender, WindoTrader, ATAS TPO article, howtotrade, edgeful, the IB folklore in A2. Claims correlated; only the (rare) computed numbers are independent.
5. **nqstats.com — one anonymous author, six stat modules**; the CantoLab TradingView script is a verbatim copy of it; NickMcD's "TradingStats research" likely = tradingstats.net (a SECOND, distinct anonymous stat site — different N, periods, definitions).
6. **Footprint folklore family.** MarketDelta-era (~2005-2010) order-flow lore restated by ATAS, Bookmap, Jigsaw, Axia, Optimus, orderflows.com (+ Sierra/NT8 vendor docs supplying definitions only). ONE correlated family, zero quantified evidence anywhere.
7. **Dealer-hedging school.** Cem Karsan + SpotGamma + SqueezeMetrics + MenthorQ — one theory family amplified on X; the academic Barbon/Buraschi line is separate.
8. **NY Fed overnight-drift.** One author team (Boyarchenko/Larsen/Whelan) for both the effect and its 2026 disconfirmation; Elm Wealth and NightShares are amplifiers, Bondarenko-Muravyev an independent adjacent computation.
9. **Taylor TTT.** George Taylor 1950 book → taylortradingtechnique.net vendor, mypivots condensation, LBR slide deck, StoneX blog.
10. **Independent one-man quant-blog lineages** (mutually independent, widely quoted downstream): Steenbarger (TraderFeed) and Hanna (Quantifiable Edges) — their numbers back MC-03/07/15/19/20/21/23.

Scout usability: all 16 scouts contributed usable leads. Weakest inputs: A5 (vendor domain — zero performance evidence exists anywhere in it; ninZa/LuxAlgo/Bookmap internals blocked; leads usable only as rule/observable definitions) and A3's reddit-sourced numbers (carried via Brave SERP snippets, pages not directly fetched — flagged as such in MC-01/MC-08/MC-36).

