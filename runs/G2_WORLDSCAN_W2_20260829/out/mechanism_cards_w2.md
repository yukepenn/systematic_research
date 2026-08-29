# G2 WORLD DISCOVERY WAVE 2 — MECHANISM CARDS (TRIAGE dedup + family tree additions)

Built 2026-08-29 from the 6 scout reports in `runs/G2_WORLDSCAN_W2_20260829/scouts/`
(S1 short-native, S2 event-time/path-topology, S3 execution-state, S4 overnight, S5 regime/sizing,
S6 intraday vol-structure; 75 leads total). Gated against `research/genesis2/FAILURE_MEMORY.md`
(closed list AND not-closed guard) and `research/genesis2/SOURCE_GRAPH.md`.
**19 new cards (MC-38..MC-56)** + reinforcement updates to 7 Wave-1 cards (no new ids for those).
Card format identical to `runs/G2_WORLDSCAN_W1_20260828/out/mechanism_cards.md`.
Owned-data vocabulary: NQ 1-min 2006-2026, ES/RTY/YM 1-min 2022+, internals minute 2022+,
certified VIX/VXN/VX daily, 2025-26 NQ/ES tick+BBO (pre-burn slices), multi-market daily;
VX/VXM 1-min sit in NT8 unextracted ($0 but an extraction task).
Evidence classes: PEER-REVIEWED > IN-HOUSE-PREREG > CODED-BACKTEST > LARGE-N-DESCRIPTIVE > EXAMPLES > TESTIMONY.
Method note carried from all six scouts: WebSearch budget was exhausted before the wave ran; all
sourcing was WebFetch on direct/API URLs — several CLAIM fields are title/venue-level and are
flagged as such inside the scout files.

---

[CARD id=MC-38]
NAME: Sharper realized-vol state (downside semivariance, overnight terms, HAR, cross-market commonality)
FAMILY: VOL
MECHANISM: The volatility state variable every gate conditions on can be measured much better than trailing daily RV: the persistent component of vol is carried almost entirely by DOWNSIDE moves (Patton-Sheppard signed jumps), overnight return/RV is a distinct input RTH-only RV misses, HAR on 1-min RV beats daily GARCH out-of-sample, and cross-market (ES/RTY/YM + internals) first-30-min RV denoises the common component. A less noisy, sign-aware vol state improves every downstream sizing/flatten/gate decision — RISK SPECIFICATION by construction, never information alpha.
MERGED-LEADS: S1-01 (Patton-Sheppard RS−/signed-jump, REStat 2015); S4-05 (Ahoniemi-Lanne / Todorova / Kambouroudis overnight-RV-in-HAR family); S4-08 (Lachance: ON-vs-RTH risk-per-hour asymmetry — beta/variance per hour, tail ratios); S6-07 (Martens 2002 / Noh-Kim 2006: intraday RV beats daily GARCH OOS on index futures; VXN add-on); S6-08 (Zhang/Cucuringu intraday vol commonality, pooled beats single-asset).
INDEPENDENT-SOURCES: 4+ genuinely independent academic lines (Patton-Sheppard; Engle-lineage HAR/realized-measures; overnight-RV family; Oxford ML-commonality) — the best-replicated corner of financial econometrics.
EVIDENCE-BEST: PEER-REVIEWED with OOS forecast evaluations (REStat 2015; JFM 2002; JFEC lineage).
OBSERVABLES: daily RS− = Σ r_1min²·1(r<0), RS+, signed jump ΔJ²; ON RV (18:00-09:30) and ON return terms in HAR; per-hour variance/kurtosis/left-tail ON vs RTH by VIX tercile; ES/RTY/YM + TICK/ADD first-30-min RV.  DATA-CAPABLE-NOW: YES (all from owned 1-min stores + certified VIX/VXN daily).
NOVELTY-VS-REPO: REPRESENTATION as RISK SPECIFICATION — explicitly NOT-closed lane ("vol-state as sizing"). Distinct decision role from the closed RV-tercile ORB conditioner (that was a signal test, 5.5x under MDE). §4 rule binds: a reduced risk denominator must never masquerade as alpha; gross exposure held fixed in any comparison.
HORIZON: next-session to 1-month vol forecasts; per-hour risk pricing for any hold-through-night policy.  COST-SENSITIVITY: LOW (no trades of its own).
CHEAPEST-FALSIFIER: one pre-frozen OOS horse race on NQ 1-min 2006→pre-burn: HAR-RV vs HAR-RS− vs HAR+ON-terms vs daily GARCH for next-day RV (QLIKE/RMSE, Diebold-Mariano, frozen split); cross-market increment (S6-08) as a nested add-on 2022+; per-hour ON/RTH variance table (S4-08) printed as pure measurement in the same wave.
PRIOR: MED-HIGH — the forecast improvements are near-certain to replicate; policy value is MED (only pays where a gate currently binds on a noisy vol estimate) and the classification is locked to RISK SPECIFICATION.
[/CARD]

[CARD id=MC-39]
NAME: Intraday VX-spike → equity-close spillover (vol-ETP NAV rebalancing)
FAMILY: CROSSMKT
MECHANISM: Leveraged AND inverse VIX ETPs must both BUY VIX futures after an intraday vol rise, concentrated before the 16:15 NAV strike — short-gamma in VOL space. An intraday front-VX spike therefore mechanically begets more vol buying into the close, pricing NQ down via the vol-spillover channel (Feb-5-2018: ~116k VX contracts in one minute at 16:08). Post-2018 the ETP complex deleveraged (XIV dead), so era structure is part of the hypothesis.
MERGED-LEADS: S1-04 (BIS Quarterly Review March 2018 Box A, official-sector reconstruction).
INDEPENDENT-SOURCES: 1 primary (BIS) + episode-level public record; mechanism family shared with the LETF equity leg (MC-13) — S1 declares S1-02/03/04 ONE hypothesis family for the null.
EVIDENCE-BEST: audited-code (BIS official-sector reconstruction from market data).
OBSERVABLES: front VX %change by 15:00 ET from VX/VXM 1-min (IN NT8, never extracted — $0 extraction task); NQ 15:00→16:15 return; era flags 2010–Feb2018 / Mar2018–2022 / 2023–26.  DATA-CAPABLE-NOW: PARTIAL — needs the VX 1-min extraction; certified VX daily owned as fallback.
NOVELTY-VS-REPO: RAW-INFO — first in-house use of intraday VX; explicitly NOT-closed ("intraday VIX/VXN — only DAILY basis tested"). Distinct observable from the dead daily VX-basis terciles (GENESIS_H1).
HORIZON: 15:00→16:15 ET on vol-spike days; spillover 1-2 sessions.  COST-SENSITIVITY: MED (short entries in stressed tape).
CHEAPEST-FALSIFIER: days with front-VX ≥ +5% by 15:00 ET: NQ 15:00→16:15 short vs matched same-size-down-day control WITHOUT the VX spike (control in same wave), era-split, circular-shift null sharing one draw with the MC-13 family.
PRIOR: MED — mechanism episode-verified and NQ-relevant; post-2018 structural change is the live risk; the observable is genuinely new in-house.
[/CARD]

[CARD id=MC-40]
NAME: Forced-deleveraging continuation band (mid-magnitude drops; margin/fire-sale spiral with self-limiting reversal)
FAMILY: SHORTSIDE
MECHANISM: Short-side continuation is non-monotonic in drop size. Mid-magnitude drops (≈2.5-5%, bear regime) are large enough to trigger vol-target/margin de-risking follow-through but not the capitulation dynamics that bounce extremes; margin spirals (losses + vol spikes raise margins, forcing further selling) extend the move over 1-5 days; but fire-sale pressure is SELF-LIMITING — once constrained accounts are flushed, prices revert, so any cascade short must monetize into the acceleration, never hold past flow exhaustion. Extreme gap-downs are the boundary case: the forced flow completes overnight and RTH bounces (entry VETO, see MC-03 update). At the minutes scale the same immediacy-absorption physics shows as volume-spike down-cascades where high volume is NOT liquidity.
MERGED-LEADS: S1-09 (Hanna: 2.5-5% bear-regime drops, 84% touch below trigger within 3d; his own ≥5% studies bounce); S1-11 (Brunnermeier-Pedersen liquidity spirals + BCBS-CPMI-IOSCO 2022 procyclical margin evidence); S1-12 (Bian-He-Shue-Zhou account-level fire-sale continuation-then-REVERSAL); S1-05 (Kirilenko-Kyle-Samadi-Tuzun flash-crash immediacy-absorption cascade, minutes leg); S1-10 (gap-down bounce = the veto clause; also logged as MC-03 update).
INDEPENDENT-SOURCES: 4 — Hanna (trader, two eras), Brunnermeier-Pedersen + official-sector margin data, Bian et al (account-level causal), Kirilenko et al (audit-trail). Convergent on "continuation exists, is band-limited, and reverses late".
EVIDENCE-BEST: PEER-REVIEWED (RFS 2009; JF 2017; NBER/account-level) for the mechanism; LARGE-N blog tables for the tradable band.
OBSERVABLES: daily drop buckets [1.5,2.5)/[2.5,5)/≥5% × bear filter (200d MA); VIX jump ≥20% + close ≤10th pct of range; 2-day drops ≥4% with volume >1.5x 20d; MFE/MAE path of a 3-day short (hours 0-72); 5-min volume >4σ AND return <−kσ events (minutes leg).  DATA-CAPABLE-NOW: YES (NQ 1-min 2006-2026; 2022 bear in-sample).
NOVELTY-VS-REPO: RAW-INFO — short-side mechanisms explicitly NOT closed (only mechanical mirrors tested). Must dodge: "dead short legs recur" pattern (this is state-conditioned continuation, not a fade), W118 (endogenous-trigger reversal — here the claim IS continuation), rare-event regime collapse (TICK lesson: print event counts per era before gating).
HORIZON: 1-3 days (band), 0-72h MFE path (spiral), next-15-min (cascade leg).  COST-SENSITIVITY: MED (daily-scale entries; $33/RT small vs points at these magnitudes).
CHEAPEST-FALSIFIER: one frozen wave on NQ 2006-2026: (a) bear-filtered drop-size buckets → P(touch below trigger close within 3d) vs circular-shift null AND vs the same table unfiltered (matched unconditional control); (b) median MFE path of 3-day shorts after 2-day ≥4% high-volume drops — the claim predicts positive MFE early, negative tail late; (c) volume-spike down-cascade next-15-min drift vs matched UP-spike control. One family, shared draw.
PRIOR: MED — mechanism chain is canonical and causally evidenced; blog-grade band numbers, 2015-China transfer gap, and effective-N concentration in 2008/2020/2022 clusters cap it.
[/CARD]

[CARD id=MC-41]
NAME: Failed-rally breadth divergence (short-native internals asymmetry)
FAMILY: SHORTSIDE
MECHANISM: A price rally without broad participation is distribution — large-cap marking-up masking net selling — and resolves lower over 1-4 days; symmetrically-weak-breadth DOWN days show one-way trending structure (downside range targets hit far above geometric base rates, dip-buyers absent). The short signal is weak breadth on UP days, not down-day continuation — a direction-asymmetric internals divergence, which is exactly the shape the S1 domain summary flags as the live short-native observable.
MERGED-LEADS: S1-07 (Steenbarger 2006: SPY +1% with weak Adjusted TICK → −0.24% next 4d vs +0.39% with strong TICK, N=32/774); S1-08 (Steenbarger 2007: cumulative Adjusted TICK <−300 → S1 pivot hit 80% vs 25% R1 — an 80-vs-13pp conditional spread, too wide to be all geometry).
INDEPENDENT-SOURCES: 1 (both Steenbarger — one observable family, one author); MC-23's other lineages (Hanna, Raschke) are corroborating context, not this specific divergence claim.
EVIDENCE-BEST: backtest-screenshot (his reported stats, 2003-07 era, no code).
OBSERVABLES: Adjusted TICK = daily mean of minute TICK re-centered to zero (internals minute 2022+ owned); intraday cumulative adjusted TICK by 11:00 ET; up-day ≥1% × bottom-tercile breadth flag; P(afternoon takes out morning low), close-location quartile.  DATA-CAPABLE-NOW: YES 2022+ (internals minute); $TICK back to ~2013 is a flagged free-unacquired extension (owner-gated acquisition — free in dollars ≠ free in governance).
NOVELTY-VS-REPO: REPRESENTATION — internals setups on 2022+ minute data explicitly NOT closed (only regime-labels tested); this is the exact "flagged internals prereg" lane of MC-23 with a short-native, direction-asymmetric hypothesis. Must not drift into W111's closed afternoon-participation fade shape (different: day-horizon conditioning, not intraday participation fade). MDE check FIRST — up-days ≥1% × bottom tercile on ~4.5y of data is a small N.
HORIZON: next 1-4 days (S1-07 leg); rest-of-session (S1-08 leg).  COST-SENSITIVITY: LOW-MED (few, day-scale entries).
CHEAPEST-FALSIFIER: rebuild adjusted TICK from owned internals 2022→pre-burn; (a) up-days ≥1% × breadth tercile → next 1-4d table vs matched unconditional up-day control; (b) 11:00 cumulative-TICK terciles → P(afternoon < morning low) vs unconditional table; circular-shift null, one family with the MC-23 prereg.
PRIOR: MED — 20-year-old small-N evidence from one author, but the 2022 bear supplies in-sample events, the observable is owned and unopened, and the direction-asymmetry is a sharp, cheap discriminator.
[/CARD]

[CARD id=MC-42]
NAME: End-of-day short-covering headwind (exit-before-15:30 policy for shorts)
FAMILY: SHORTSIDE
MECHANISM: Short sellers systematically de-risk into the close (documented at the single-stock level as end-of-day reversal favoring intraday LOSERS, driven by covering plus attention-driven retail buying), so holding index shorts into 15:30-16:00 faces a structural covering headwind that may have grown in the modern era. If the index-level down-day last-30-min continuation coefficient weakens or flips sign 2023-26, every short candidate inherits an exit-before-15:30 rule; if not, the MC-13 flow channel still dominates.
MERGED-LEADS: S1-14 (Baltussen-Da-Soebhag "End-of-Day Reversal" WP 2025 — deliberate self-correction within the same author family as the intraday-momentum result).
INDEPENDENT-SOURCES: 1 (Baltussen-Da family — the SAME family whose JFE 2021 paper anchors MC-13; this is their own boundary condition, which raises credibility as adversarial-to-own-interest).
EVIDENCE-BEST: peer-reviewed-grade working paper (EFMA-presented) at stock level; index-level version untested anywhere.
OBSERVABLES: down-day 15:30→16:00 continuation coefficient by era (2006-15/16-22/23-26) — one extra column in the MC-13/S1-02 regression harness.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: MECHANISM-POLICY — short-side exit policy; NOT-closed guard covers both short-side mechanisms and exit-policy novelty. No closed scope touches last-30-min ERA structure of down-days (H4B closed the first→last half-hour geometry, different object).
HORIZON: 15:30-16:00 ET.  COST-SENSITIVITY: LOW (a policy clause, no standalone trades).
CHEAPEST-FALSIFIER: free rider on the MC-13-update harness: print the down-day 15:30→16:00 coefficient by era; a 2023-26 sign flip = adopt exit-before-15:30 for all short candidates; either outcome is bankable.
PRIOR: MED — nearly free, both outcomes actionable, and the source family arguing against its own headline result is the good kind of evidence.
[/CARD]

[CARD id=MC-43]
NAME: Directional-change intrinsic-time structure on NQ (overshoot law, variability law, 0.632 memoryless null)
FAMILY: EVENTTIME
MECHANISM: In event time (price reversals of threshold δ define the clock), FX shows stable scaling laws: average overshoot after a DC confirmation ≈ δ, overshoot VARIABILITY scales lawfully (with closed-form Brownian benchmarks), and — per the 2025 renewal-process result — the DC-share of intrinsic events stabilizes at 1−1/e = 0.632, making duration-since-last-event uninformative EXCEPT where the share deviates. Whether this structure exists on a single trending index future has never been audited anywhere; our banked ON-touch (95.3% vs 90.0%) and IB-extension (96.8% vs 91.6%) anomalies are exactly what an overshoot law would predict.
MERGED-LEADS: S2-01 (Glattfelder-Dupuis-Olsen 12 scaling laws, QF 2011); S2-03 (Glattfelder-Golub overshoot-variability law with analytic Brownian null); S2-04 (Houweling 2025: DC intrinsic time as memoryless exponential hazard, 0.632 boundary — the structural null for ALL event-timing ideas); S2-13 (adaptive threshold δ(t) ∝ regime vol — kept only as the no-optimizer variant).
INDEPENDENT-SOURCES: 2 — Olsen lineage (S2-01/03 same school) and Houweling (independent author inside the same framework). The Brownian analytic null makes the family partially self-controlling.
EVIDENCE-BEST: PEER-REVIEWED (QF 2011, replicated on FX/crypto) for the laws; working-paper for the 0.632 null.
OBSERVABLES: DC event series at δ ∈ {0.1,0.2,0.4,0.8,1.6}% from NQ 1-min closes; per-event overshoot ω, mean(ω)/δ, var(ω); log N(δ) vs log δ slope; rolling 250-event DC-share and deviation d(t) = share − 0.632; δ(t) = c·20d-ATR% variant.  DATA-CAPABLE-NOW: YES (δ ≥ ~0.1% from 1-min; finer needs 2025-26 tick).
NOVELTY-VS-REPO: REPRESENTATION — path/event-time representations explicitly NOT closed (never tested here). This is measurement, not trading: it decides whether the whole EVENTTIME family has anything to stand on for NQ.
HORIZON: threshold-dependent, intraday to multi-day.  COST-SENSITIVITY: n/a (no trades).
CHEAPEST-FALSIFIER: frozen spec on NQ 1-min 2006→2026-05-31: (a) mean(ω)/δ with bootstrap CI per era — PASS = in [0.8,1.2] stable; (b) var(ω) vs volatility-matched Brownian analytic values (circular-shift preserved); (c) DC-share vs 0.632 with block-bootstrap CI + ONE preregistered conditional (top/bottom-decile |d(t)| sessions vs matched control). Likeliest outcome — law holds, 0.632 confirmed, no conditional lift — is itself a bankable structural null that closes duration-timing cheaply.
PRIOR: MED — replicated laws elsewhere + our two banked anomalies pointing the same direction; zero prior NQ audit anywhere is the opportunity and the risk.
[/CARD]

[CARD id=MC-44]
NAME: DC-event trading policies (clock-swap, backlash/overshoot continuation, pre-confirmation nowcast)
FAMILY: EVENTTIME
MECHANISM: The trading layer of the DC school: enter at DC confirmations and exit at the overshoot (Essex "backlash", 30% ann. claimed on FX net of spread), run multiple thresholds at once, swap the clock under a FIXED learner (GP-DC beat physical time across 220 equity datasets — the cleanest published evidence the CLOCK itself carries information), and buy back the confirmation lag by nowcasting DC completion from mid-flight retracement depth. All positive numbers are FX/equities at near-zero spread; none is a costed single-instrument index-futures result.
MERGED-LEADS: S2-02 (Golub-Glattfelder-Olsen Alpha Engine, public GPL-3 Java — audited code, unverified Sharpe); S2-05 (Adegboye-Kampouridis-Otero GA multi-threshold, FX); S2-06 (Long-Kampouridis GP-DC vs physical clock, 220 datasets, >18% avg); S2-07 (Bakhach-Tsang IDBA backlash, ~30% ann. after spread, FX); S2-08 (Tsang nowcasting DC pre-confirmation — direct tension with MC-43's 0.632 null, testing both is a free either-way result).
INDEPENDENT-SOURCES: ~1.5 — Olsen school and Essex/Tsang-Kampouridis lab are heavily inter-linked (one extended lineage); no independent replication with published numbers located. SOURCE-GRAPH NODE (new): Olsen/Essex DC lineage = one effective root.
EVIDENCE-BEST: PEER-REVIEWED backtests with significance testing (no forward periods; spread-only costs; GA/GP selection-luck exposure).
OBSERVABLES: DC confirmations at fixed δ, overshoot-so-far fraction (OSV), forecast overshoot exit, retracement fraction x with elapsed-bars term, DC-clock-resampled features of our own dead conditioners.  DATA-CAPABLE-NOW: YES (NQ 1-min for δ ≥ 0.1%).
NOVELTY-VS-REPO: POLICY on the MC-43 representation. Anti-selection-luck rule locked in: NO learner imported — each falsifier is the single fixed rule the family reduces to. Counter-trend liquidity-provision variants collide with the dead mean-reversion graveyard (TICK fade, sweep-and-reclaim) — expected FAIL, informative about WHERE gross edge peaks.
HORIZON: hours-days per DC episode.  COST-SENSITIVITY: HIGH ($33/RT vs FX ~0.5-1bp spread — the central reason prior is LOW).
CHEAPEST-FALSIFIER: one wave, NQ 1-min pre-burn, $33/RT: fixed rule (δ=0.4% DC entry WITH trend, exit at overshoot=δ or opposite DC) vs matched always-long control + circular-shift family null; IDBA forecast-exit as one extra column; nowcast completion probability P(complete | x, elapsed) vs the mandatory geometric control; clock-swap check = rebuild RV-tercile/NR7 conditioners in DC event counts under their ORIGINAL gates (a representation that cannot resurrect a corpse under its own gate is banked as statistics-only).
PRIOR: LOW — cost structure and trending-single-instrument transfer are both adverse; kept because the falsifiers are nearly free once MC-43 runs and the clock-swap question is this wave's mandate.
[/CARD]

[CARD id=MC-45]
NAME: Swing-sequence grammar (HH/HL topology automaton, levels discarded)
FAMILY: EVENTTIME
MECHANISM: Sequences of smoothed swing extrema — the ORDER of higher-highs/lower-lows, not the price levels — encode crowd positioning; the canonical audited result (Lo-Mamaysky-Wang JF 2000) found conditional return distributions after detected extrema-patterns differ significantly from unconditional ones (information, not demonstrated profit). Our level-based deaths (PDH/PDL geometry-explained, sweep-and-reclaim NULL) never tested the pure sequence automaton: levels discarded, order kept.
MERGED-LEADS: S2-09 (Lo-Mamaysky-Wang, kernel-regression pattern automaton, US stocks 1962-1996).
INDEPENDENT-SOURCES: 1 primary — but fully independent of the Olsen/Essex DC lineage (different formalism, same "event-defined path skeleton" idea), which is why it earns a separate card from MC-43/44.
EVIDENCE-BEST: PEER-REVIEWED (JF 2000) — distributional information only, 26-year-old daily-stock data.
OBSERVABLES: zigzag extrema at 0.3% reversal on NQ RTH 1-min; last-4-extrema state ∈ {HH-HL, LH-LL, mixed}; next-60-min return/RV distribution per state.  DATA-CAPABLE-NOW: YES.
NOVELTY-VS-REPO: REPRESENTATION — path representations NOT closed; materially different from closed level-magnetism scopes (MC-07 CLOSED; G2_F2_SWEEP01) because the observable carries no levels. KS-vs-matched-control design is mandatory (geometry ate PDH/PDL — the control here is same-timestamps unconditional).
HORIZON: next 60 min per state.  COST-SENSITIVITY: LOW as state/conditioner; HIGH if ever traded standalone.
CHEAPEST-FALSIFIER: one wave, no learner: encode the 3-state automaton on NQ RTH pre-burn; per-state next-60-min return/RV vs matched unconditional control (KS + circular-shift family null). Kills or promotes the whole swing-automaton axis in one table.
PRIOR: LOW-MED — old evidence, information-not-profit, and topology-at-levels is already dead here; kept because the pure-sequence version is untested in-house and nearly free.
[/CARD]

[CARD id=MC-46]
NAME: Closing-auction imbalance information and close-dislocation reversion
FAMILY: EVENT
MECHANISM: The 15:50 ET imbalance publication (NYSE every 1s; Nasdaq NOII 15:50-16:00) is a real, timestamped public information event revealing inelastic MOC demand; single-stock prices drift toward the indicative match price pre-cross (Jegadeesh-Wu), inelastic auction flow can push the 16:00 print away from continuous value, and dislocations revert when elastic capital returns (Cushing-Madhavan 2000 → Bogousslavsky-Muravyev 2023). The futures-spillover leg — does the INDEX-aggregate imbalance move NQ in 15:50-16:00 — is unmeasured in public work (S3 negative-space check confirms), making the falsifier an original test.
MERGED-LEADS: S3-01 (NYSE/Nasdaq dissemination specs — exchange primary sources); S3-02 (Jegadeesh-Wu SSRN 3732955 + JFE 2022 companion); S3-03 (Bogousslavsky-Muravyev JFM 2023 "Who trades at the close?"); S3-04 (Cushing-Madhavan JFM 2000 — historical-era leg).
INDEPENDENT-SOURCES: 3 academic teams + exchange primary documentation; convergent mechanism across 25 years.
EVIDENCE-BEST: PEER-REVIEWED (JFM 2000/2023; JFE-lineage 2022).
OBSERVABLES: proxy only (imbalance feed not owned): NQ 1-min |return|/volume/autocorrelation structural break at exactly 15:50 vs 15:40/15:45 controls; dislocation = 16:00 − 15:55 price, its reversion over 16:00→18:00 and →next 09:30; 15:50-16:00 drift sign conditioned on 15:30-15:50 return.  DATA-CAPABLE-NOW: YES (proxies from NQ 1-min 2006-2026); the per-second imbalance feed itself is an unowned acquisition decided only if the proxy signature exists.
NOVELTY-VS-REPO: RAW-INFO — MC-11 treated 15:50 as guru clock-window folklore; this is the exchange-mechanics information-event version with a dislocation-reversion object. No closed scope covers close-auction structure.
HORIZON: 15:50-16:00 ET; reversion into 18:00 / next open.  COST-SENSITIVITY: MED-HIGH (late-session entries, wide states).
CHEAPEST-FALSIFIER: structural-break test at 15:50 ET on NQ 1-min pre-burn (|ret|, volume, 1-min AC) vs 15:40/15:45 placebo anchors, shared-draw null; then dislocation-decile reversion table with era split 2006-15/16-26 (Cushing-Madhavan era-decay check). If no minute-level event signature exists, the spillover is untradable at our cost floor and dies without buying imbalance data.
PRIOR: MED — the feed and mechanism are certain; index-aggregation dilution below $33/RT is the open question, and the test is free.
[/CARD]

[CARD id=MC-47]
NAME: Liquidity-state execution-cost policy (depth/spread states, within-minute timing, hour-of-day, queue placement)
FAMILY: EXECUTION
MECHANISM: Expected execution cost on a tick-constrained CLOB is a function of the depth/spread STATE, not volume: price impact ≈ OFI/(2·depth) (same flow moves price 2-3x more when depth is thin — one of the most replicated microstructure facts); algorithmic executions cluster on clock marks so cost differs by second-of-minute; impact at fixed participation is systematically lower late-session; depth evaporates faster than spreads widen in vol regimes, making queue-placement depth a control variable; and real cost curves are best fit from OWN fills (AQR). None of this is alpha — it is cost harvested from EXEC01's measured 2-6 tick spread states.
MERGED-LEADS: S3-07 (Cont-Kukanov-Stoikov OFI/depth slope); S3-08 (Muravyev-Picard within-minute trade clustering); S3-09 (BestEx time-of-day impact effect); S3-10 (BestEx Pulse futures cost model — depth/spread states, independently corroborating EXEC01's representation); S3-11 (QB queue-depth placement tactic, April-2025 depth collapse); S3-13 (Frazzini-Israel-Moskowitz own-fill cost curves — methodological license, shadow-book application); S3-06 weak-form leg (toxicity state as when-NOT-to-execute only; VPIN return-alpha remains dead-listed).
INDEPENDENT-SOURCES: 4+ — academic microstructure (Cont et al; Muravyev-Picard), BestEx (one vendor family for S3-09/10), QB (independent vendor), AQR. Convergent with in-house EXEC01.
EVIDENCE-BEST: PEER-REVIEWED (J Fin Econometrics 2014; Financial Management 2022) + live-verified (AQR own-fill database).
OBSERVABLES: top-of-book depth, spread state, 10s OFI→mid slope per EXEC01 state, second-of-minute volume/effective-spread/markout profile, hour-of-day cost at matched vol, fill probability by queue level, shadow-book fills (from 2026-09-01).  DATA-CAPABLE-NOW: YES (2025-26 NQ/ES tick+BBO pre-burn; no seal risk, no new collection — DOM pause untouched).
NOVELTY-VS-REPO: POLICY — pure cost specification; extends EXEC01, sibling of MC-37. The closed MS-BBO scope (sub-minute quote ALPHA, −$1,786/session) does not cover cost-side state conditioning. §4 rule: savings are EXECUTION classification, never information alpha.
HORIZON: per-execution, always-on.  COST-SENSITIVITY: n/a — it IS the cost model.
CHEAPEST-FALSIFIER: three cheap measurements on the owned tick store: (1) OFI→mid slope by EXEC01 state (confirm inverse-depth scaling on NQ); (2) second-of-minute cost profile — if second-0/second-30 differ ≥0.25 tick, re-time 1-min-bar-close entries off the boundary and price the saving; (3) matched-vol 10:00-vs-15:00 aggressive-schedule cost. Then: fit cost = f(spread, depth, hour) and validate against shadow-book fills; >20% divergence from the modeled $25-33/RT forces a cost-model revision.
PRIOR: HIGH — near-certain replication (foundational results + in-house corroboration already exists), zero governance risk, and it directly reprices every candidate's cost floor; the ONLY high-prior card in this wave, and it is a cost card, not an alpha card.
[/CARD]

[CARD id=MC-48]
NAME: Session-handoff sign structure (overnight→open, US-close→Asia-leg)
FAMILY: TIMEOFDAY
MECHANISM: Session boundaries are clientele handoffs: overnight and intraday return components are systematically different and negatively related because different investor populations dominate each session (Lou-Polk-Skouras), and the prior US day's return is the dominant public signal for the Asia leg (Iwanaga 2026, Nikkei). The dead unconditional overnight drift is NOT the object — the only admissible observables are SIGN RELATIONS: corr(ON return, 09:30-10:00 return) by state, and prior-RTH terciles → NQ 18:00-03:00 (Asia) vs 03:00-09:30 (Europe) legs.
MERGED-LEADS: S3-12 (Lou-Polk-Skouras JFE 2019 tug-of-war); S4-10 (Iwanaga 2026, prior-SPX → Nikkei intraday — the US→Asia handoff measured in modern futures data; title-level).
INDEPENDENT-SOURCES: 2 independent academic teams; complements S4-01/MC-12 (whose drift lives in the Europe leg only — decompositions share one wave and one null draw).
EVIDENCE-BEST: PEER-REVIEWED (JFE 2019).
OBSERVABLES: NQ ON component (18:00→09:30) vs first-30-min and rest-of-day components; sign correlation by era and ON-range state; prior-RTH terciles → Asia-window (18:00-03:00) net return.  DATA-CAPABLE-NOW: YES (NQ 1-min ETH).
NOVELTY-VS-REPO: REPRESENTATION — overnight drift is dead-listed (unconditional); ONRANGE closed quadrant day-types. The sign-relation observable and the Asia/Europe leg split are different objects. Overnight friction tax ($5.25/RT) and MC-12's LOW prior both apply as context.
HORIZON: session-scale legs.  COST-SENSITIVITY: HIGH (overnight spreads) if traded; LOW as state.
CHEAPEST-FALSIFIER: one conditional table, NQ pre-burn: prior-RTH-return terciles × {Asia leg, Europe leg, 09:30-10:00 leg} net returns vs always-flat/always-long controls, shared draw with the MC-12-update decomposition; if no state cell clears MDE at $33/RT, close the handoff axis for good.
PRIOR: LOW-MED — strong papers, but the index-level tradable residue after the overnight-drift kill may be nil; the closure value of a clean negative is real.
[/CARD]

[CARD id=MC-49]
NAME: Overnight sub-session partition (Asia/London extremes as separate liquidity pools)
FAMILY: PATH
MECHANISM: ICT "killzone" folklore partitions the overnight into Asia (19:00-00:00 ET) and London (02:00-05:00 ET) sub-sessions and claims their separate highs/lows are where resting stops cluster; an RTH sweep of a SUB-SESSION extreme (vs the whole-night extreme) purportedly reveals which side's liquidity was consumed. The partition is the only thing separating this from the dead whole-range sweep result — that is the entire hypothesis.
MERGED-LEADS: S4-06 (meegol/apex-killzone-engine: public runnable code, +60.6R claimed on MES over 59 days, author self-flags insufficiency; unfiltered signals LOSE on 3 of 4 symbols).
INDEPENDENT-SOURCES: 1 — wholly derivative of the ICT/Huddleston node (SOURCE_GRAPH #1); the four sibling GitHub killzone repos found in the same search are copies. Count against the ICT node, not as new.
EVIDENCE-BEST: backtest-screenshot (self-reported, Yahoo 5-min, 59 days — near-zero weight).
OBSERVABLES: Asia H/L, London H/L, first RTH touch/sweep times 09:30-11:00, forward net return to 12:00.  DATA-CAPABLE-NOW: YES (NQ 1-min).
NOVELTY-VS-REPO: REPRESENTATION (sub-session partition) — must clear G2_F2_SWEEP01 (sweep-and-reclaim of prior-RTH extremes NULL both ways, response is generic post-cross MR) and the MC-07 closure (level magnetism geometry-explained). The materially-different claim is the PARTITION carrying information the whole-ON extreme lacked; no ICT filter stack in v1 (overfit farm).
HORIZON: 09:30-11:00 entries, same-day.  COST-SENSITIVITY: HIGH (reversal-at-extreme entries).
CHEAPEST-FALSIFIER: unconditional table on NQ pre-burn: first-sweep of {Asia-H, Asia-L, London-H, London-L} → net return to 12:00 vs the matched whole-ON-extreme sweep control in the same wave. Kill if the partition adds nothing over the (dead) whole-range version — one table, no filters.
PRIOR: LOW — evidence is folklore-grade, the parent object is freshly closed in-house, and the partition-increment is the narrowest of hypotheses; kept only because it is this wave's cheapest representation-shift test of a dead axis.
[/CARD]

[CARD id=MC-50]
NAME: Event-conditioned overnight holds (macro-release nights; megacap-earnings nights)
FAMILY: EVENT
MECHANISM: Two clienteles pay a premium to whoever holds overnight through scheduled information events. (a) Macro nights: the announcement risk premium (Savor-Wilson class) is earned by holding into the 08:30 print, which sits INSIDE the futures overnight session — Hanna's trader-side shadow claims >9x the day session's profits on employment days. (b) Earnings nights: after large-|surprise| megacap reports, stocks show positive abnormal OVERNIGHT returns for weeks after BOTH positive and negative surprises (attention-driven retail buying + covering), and NDX top-7 concentration (~40%+) makes single-name events index events. The both-signs prediction is the sharp discriminator vs generic momentum.
MERGED-LEADS: S4-07 (Hanna employment-day overnight, 2015, vendor-conflicted); S4-09 (Gamm 2019 SSRN post-earnings overnight drift); cross-ref S4-02 (Kurov pre-release drift = MC-29 update, the 07:30-08:29 leg of the same wave).
INDEPENDENT-SOURCES: 2 for the premium frame (Hanna; Gamm/Lou-Polk-Skouras clientele lineage) — Hanna sells overnight subscriptions (bias flagged); Savor-Wilson academic frame is corroborating context.
EVIDENCE-BEST: peer-reviewed-adjacent working paper (Gamm) + backtest-screenshot (Hanna profit curves, no N).
OBSERVABLES: NFP/CPI dates ($0 calendar build); NQ 18:00→08:29 and 08:29→09:30 legs on release days vs matched same-weekday non-release nights; top-10-NDX-weight earnings dates + after-hours move flags ($0 calendar); NQ ON returns for the 5 following nights, split by surprise sign.  DATA-CAPABLE-NOW: PARTIAL (prices owned; both calendars are $0 builds).
NOVELTY-VS-REPO: RAW-INFO — H2 closed release-DAY same-session MEANS; the overnight-leg population is a different window and event paths are explicitly NOT closed. Pre-FOMC drift (dead, 2015) is a different event class and window. N-discipline: NFP+CPI ≈ 24/yr → ~450 events over the sample (adequate); the earnings cell counts must be printed before gating (macro-surprise N-bound lesson).
HORIZON: 18:00→09:30 holds on flagged nights.  COST-SENSITIVITY: MED (overnight spread tax $5.25/RT + $33/RT on thin events).
CHEAPEST-FALSIFIER: two tables, one family, shared draw, NQ pre-burn: (a) 18:00→08:29 net on NFP/CPI nights vs matched controls, eras split at 2017/2023; (b) mean net ON return, 5 nights after large-|after-hours-move| megacap reports vs matched non-earnings weeks, with the big-NEGATIVE-surprise → positive-ON cell printed separately (the both-signs falsifier).
PRIOR: LOW-MED — real premium frame, stale/conflicted trader evidence, aggregation-to-index risk on the earnings leg; both tables are cheap and the windows are genuinely untested here.
[/CARD]

[CARD id=MC-51]
NAME: Index vol-managed sizing (continuous, extremes-only, real-time constant; drawdown-throttle control)
FAMILY: POLICY
MECHANISM: Vol is forecastable at horizons where expected return is not, so risk/return deteriorates in high-vol states; de-levering there raises realized Sharpe and geometric growth. The literature's own referee reports: the factor-level version DIES out-of-sample (Cederburg — scaling constant not knowable ex ante), the MARKET-index version survives transaction costs (Barroso-Detzel), and acting ONLY in vol extremes captures most of the benefit at a fraction of the turnover (Bongaerts) — purpose-built for a $25-33/RT cost reality. Drawdown-based throttles, by contrast, cut risk AND expected return (Man "Drawdowns") — included as the preregistered expected-FAIL that closes that folklore axis cheaply.
MERGED-LEADS: S5-01 (Moreira-Muir JF 2017); S5-02 (Man/Harvey vol-targeting across 60+ assets); S5-03 (Cederburg real-time failure — the mandatory control design); S5-04 (Barroso-Detzel cost-adjusted survivor); S5-05 (Bongaerts conditional/extremes-only); S5-11 (Man "Drawdowns" negative); S1-13 (duplicate sighting of Moreira-Muir from the short-native scout — folded here).
INDEPENDENT-SOURCES: 3 effective — Moreira-Muir + the two response papers (independent critics), and the Man Group shop (S5-02/S5-11 = one shop). The critics being merged INTO the falsifier is the design.
EVIDENCE-BEST: PEER-REVIEWED (JF 2017; JFE 2020/2021; FAJ 2020) — the strongest-pedigree sizing family in the literature.
OBSERVABLES: 21d realized variance / EWMA-20d sigma from owned 1-min; weight = min(cap, c/RV²) with c from EXPANDING window only; top/bottom-decile RV triggers for the extremes-only variant; running drawdown of always-long NQ and the 11:48 incumbent's P&L stream.  DATA-CAPABLE-NOW: YES.
NOVELTY-VS-REPO: POLICY / RISK SPECIFICATION — vol-state-as-sizing explicitly NOT closed; §4 leverage rule binds (report at matched mean exposure, never book as information alpha). Distinct from the closed RV-tercile SIGNAL scope.
HORIZON: monthly rebalance (continuous) / episodic (extremes-only).  COST-SENSITIVITY: LOW-MED (turnover clause preregistered, contracts counted).
CHEAPEST-FALSIFIER: one harness, NQ daily-from-1-min 2006-2026, both eras: (a) continuous c/RV² with REAL-TIME expanding c (Cederburg clause), (b) EWMA target with 3-clause gate (net Sharpe ≥ unmanaged, 1%-tail improves, maxDD improves), (c) extremes-only 0.5x/1.5x deciles, (d) drawdown-throttle grid {5,10,15}% — all vs constant-exposure control at matched mean exposure, $33/RT on rebalance contracts, circular-shift null on the timing component. PASS clauses per Barroso-Detzel: net-of-cost, real-time, market-index only.
PRIOR: MED-HIGH — survived its own adversarial literature net of costs at the index level; the honest expected outcome is "geometric/tail improvement, RISK SPECIFICATION classification", and the drawdown leg is expected FAIL.
[/CARD]

[CARD id=MC-52]
NAME: Variance-risk-premium and VIX-curve states (forecast-adjusted premium, slope PC2, VRP)
FAMILY: VOL
MECHANISM: The variance complex prices risk, not just expected vol: implied-minus-realized variance (VRP) positively predicts index returns at monthly-quarterly horizons; the VX-futures premium over a statistical VIX forecast predicts VX returns and — counterintuitively — FALLS as risk builds (hedger withdrawal = early-warning state); the term-structure SLOPE reflects the price of variance risk and predicts variance-complex returns. All three are different observables from the dead raw daily VX basis, and all enter only as vol-forecast/sizing states, never as NQ direction signals.
MERGED-LEADS: S5-06 (Bollerslev-Tauchen-Zhou VRP, RFS 2009); S5-08 (Cheng "The VIX Premium", RFS 2019); S5-13 (Johnson VIX term-structure slope, JFQA 2017).
INDEPENDENT-SOURCES: 3 academic teams, one instrument complex — treat as ONE family for nulls (shared observables), per the S5 scout's own flagging.
EVIDENCE-BEST: PEER-REVIEWED (RFS x2, JFQA).
OBSERVABLES: VRP_t = VXN²_t − RV_t(22d, NQ 1-min), monthly; premium_t = VX1_t − Ê[VIX_expiry] (expanding AR(5) on log VIX, frozen spec); slope = VX2 − VX1 (certified daily curve); raw basis as the MANDATORY matched control for every leg.  DATA-CAPABLE-NOW: YES (certified VIX/VXN/VX daily + owned 1-min RV).
NOVELTY-VS-REPO: REPRESENTATION — GENESIS_H1 closed raw daily VX-basis/ratio TERCILES → next-session MEAN. Materially different observables (implied−realized; forecast-ADJUSTED premium; curve PC2), horizons (weekly-quarterly), and decision role (sizing tilt / vol forecast). Each falsifier carries the raw-basis nested control; if nothing adds beyond raw basis, the ENTIRE VX-derived family is recorded closed — a valuable outcome either way.
HORIZON: 5d-quarterly.  COST-SENSITIVITY: LOW (sizing tilt).
CHEAPEST-FALSIFIER: one family wave 2006-2026, era-split, shared draw: (a) VRP → next-month/quarter NQ return slope; (b) premium deciles → next-5d NQ RV and return WITH raw-basis matched control; (c) nested next-5d RV forecast {lagged RV} vs {+ slope}; only a leg that beats BOTH its null and the raw-basis/RV-only control earns a sizing-overlay test.
PRIOR: LOW-MED — heavily replicated in-sample elsewhere, but adjacency to the in-house H1 kill and the long horizons cap it; the family-closure value is real.
[/CARD]

[CARD id=MC-53]
NAME: Cross-asset regime states for sizing (turbulence, HMM, stock-bond correlation, risk appetite, macro-gated trend)
FAMILY: CROSSMKT
MECHANISM: Risk regimes persist for weeks and carry lower risk-adjusted returns, so a regime state machine can throttle exposure: Mahalanobis turbulence (extreme moves + correlation breakdown) persists and precedes poor risky-asset returns; 2-state HMMs on turbulence/RV convert that persistence into exposure states; the stock-bond correlation regime (2022 poster child) flags when bonds stop hedging equities; composite risk-appetite indices (Bekaert-Engstrom-Xu) separate risk aversion from uncertainty; and macro-growth gates on trend rules remove non-recession whipsaws (Philosophical Economics GTT). EVERY leg must beat the univariate-RV throttle control — the whole card dies to plain vol sizing if the cross-asset terms add nothing.
MERGED-LEADS: S5-07 (Kritzman-Li turbulence, FAJ 2010); S5-09 (Molenaar et al stock-bond correlation, FAJ 2024); S5-10 (Bekaert-Engstrom-Xu risk aversion, Mgmt Sci 2022 — downloadable index is an OWNER-GATED $0 acquisition; owned-data analog runs first); S5-12 (Kritzman-Page-Turkington regime shifts, FAJ 2012); S5-14 (GTT trend+macro gate — macro leg needs free FRED, OWNER_QUEUE; trend leg testable now).
INDEPENDENT-SOURCES: 3 effective — Kritzman/State Street shop (S5-07 + S5-12 = one shop), Molenaar/Robeco, Bekaert-Engstrom-Xu; GTT is an independent unreviewed blog lineage.
EVIDENCE-BEST: PEER-REVIEWED (FAJ x3, Mgmt Sci).
OBSERVABLES: Mahalanobis distance on owned multi-market daily (60d rolling cov); 2-state Gaussian HMM on NQ daily RV (frozen: 2 states, monthly refit); 60d NQ-vs-bond-futures correlation sign/level; z-composite {VXN, 21d RV, 60d stock-bond corr}; 10-month MA state.  DATA-CAPABLE-NOW: YES for all owned-data analogs; official BEX index and FRED macro series are owner-gated $0 acquisitions (free in dollars ≠ free in governance).
NOVELTY-VS-REPO: REPRESENTATION for sizing — vol-state-as-sizing NOT closed; RV-tercile SIGNAL closure means the RV-only throttle is the mandatory nested control everywhere. Old-regime concentration check (positive stock-bond corr ≈ 2022+ only) = N-bound gate BEFORE running.
HORIZON: weekly-monthly regime scale.  COST-SENSITIVITY: LOW (infrequent size changes).
CHEAPEST-FALSIFIER: one sizing wave on NQ daily 2006-2026, matched design, both eras: each state (turbulence >90th pct; P(HMM event)>0.7; corr-sign; composite tercile; 10m-MA) throttles 0.5x, all vs (a) constant exposure and (b) the RV-only throttle in the same wave; geometric growth + maxDD gates; PASS only where the cross-asset term adds beyond univariate RV.
PRIOR: MED — regime persistence is among the most robust facts in finance; the honest risk is total collapse into the RV control, which the design pre-prices.
[/CARD]

[CARD id=MC-54]
NAME: Diurnal vol-curve state (deseasonalized phase-conditional vol; 0DTE-era structural break; volume-time clock)
FAMILY: VOL
MECHANISM: Intraday vol has a deterministic clock (U-shape since Chan-Chan-Karolyi 1991; multiplicative daily × diurnal × stochastic decomposition forecasts OOS per Engle-Sokalska); conditioning on raw RV without removing the clock mixes phase with state. Three live questions: (1) does deseasonalized early-session vol forecast rest-of-day RV beyond raw controls; (2) did the diurnal profile structurally break at the May-2022 daily-expiry launch (Brogaard says 0DTE raised intraday vol; Cboe says no distortion — someone is wrong in print, and the answer decides whether ANY pre-2022 vol statistic is an admissible prior); (3) is the diurnal component better removed in volume-time than calendar-time. The lunch-trough→afternoon-expansion conditional is explicitly UNSOURCED folklore — power-check first, matched control mandatory.
MERGED-LEADS: S6-01 (Engle-Sokalska MC-GARCH + Rossi-Fantazzini E-mini periodic EGARCH); S6-05 (Brogaard-Han-Won vs Cboe/Xu 0DTE contradiction — era-break arbiter); S6-06 (Chan-Chan-Karolyi / Ito-Lin / Andersen-Bollerslev U-shape; conditional version unsourced); S6-10 (Martins et al volume-driven diurnal + Kearney functional vol-curve, the volume-time leg).
INDEPENDENT-SOURCES: 4+ academic lines across 35 years for the shape; the 0DTE dispute is academic-vs-conflicted-vendor (Cboe's commercial interest flagged).
EVIDENCE-BEST: PEER-REVIEWED (RFS 1991; JFEC 2012 with OOS).
OBSERVABLES: NQ 1-min squared returns by minute-of-session; frozen train-era diurnal profile; deseasonalized RV; minute-of-session RV profile 2016-19 vs 2023-26 with break test at 2022-05; last-30-min RV share; lunch diurnal-adjusted RV quintile × PM expansion ratio; cumulative-volume phase buckets.  DATA-CAPABLE-NOW: YES (NQ 1-min full history; volume owned).
NOVELTY-VS-REPO: REPRESENTATION — phase-conditional vol is a different object from the closed day-level RV terciles (whose 5.5x-under-MDE power lesson still binds: MDE before looking, everywhere here). Decides transferability for every other vol card — run the era-break leg FIRST.
HORIZON: phase-of-session to next-day.  COST-SENSITIVITY: LOW (state/forecast layer).
CHEAPEST-FALSIFIER: ordered: (1) era-break table (minute-profile + last-30-min share, 2016-19 vs 2023-26, break at 2022-05, shared null) — cheap, re-prices everything; (2) frozen-profile OOS test: deseasonalized first-60-min vol → rest-of-day RV vs raw first-60-min RV and prior-day RV; (3) volume-time rebucketing of (2) — beats calendar-time or is recorded dead in one run; (4) lunch-quintile × PM-expansion table with matched unconditional control, preregistered MDE — folklore banned permanently on failure.
PRIOR: MED — the shape is certain, the era-break answer is decision-relevant either way, and the tradable conditional is exactly the class our dead list punishes (hence the control-first design).
[/CARD]

[CARD id=MC-55]
NAME: Post-FOMC uncertainty-resolution vol crush (second-moment event state)
FAMILY: EVENT
MECHANISM: Scheduled binary uncertainty resolves at a known clock time (14:00 ET); vol priced for the event exits immediately after, producing a systematic post-announcement implied AND realized vol contraction regardless of the surprise's direction (Fernandez-Perez et al; Donninger's short-VX-on-FOMC-day overlay is the practitioner expression). The predictable object is the SECOND moment — explicitly not the dead pre-FOMC first-moment drift, and not H2's closed FOMC-day session-mean.
MERGED-LEADS: S6-02 (Fernandez-Perez-Frijns-Tourani-Rad, JEF 2017); S6-03 (Donninger short-VX FOMC overlay — not independent, builds on the same literature; used as the certified-daily-data confirmation leg).
INDEPENDENT-SOURCES: 1.5 — one academic team plus a practitioner derivative; the mechanism (uncertainty resolution) is textbook-grade.
EVIDENCE-BEST: PEER-REVIEWED (JEF 2017; magnitudes unverified this session — treated as unquoted).
OBSERVABLES: FOMC calendar 2006-2026 ($0); NQ RV(14:05-15:30)/RV(12:00-13:30) ratio on FOMC vs matched Tue/Wed non-FOMC days; certified VIX daily ΔVIX and certified VX daily ΔVX on FOMC vs non-FOMC days.  DATA-CAPABLE-NOW: YES (calendar build + owned data).
NOVELTY-VS-REPO: RAW-INFO — event-clocked second-moment state; H2 closed day-MEANS (first moment), pre-FOMC drift dead-listed (first moment, different window); event PATHS/vol explicitly NOT closed. N ≈ 160 events over 20y → MDE gate BEFORE the table (macro N-bound lesson). Policy expression is a suppression rule (post-14:00 FOMC: suppress breakout/expansion entries), not a new trading engine; VX execution is out of campaign scope.
HORIZON: 14:00→16:00 ET, 8 days/yr.  COST-SENSITIVITY: LOW (gate/suppression policy adds no trades).
CHEAPEST-FALSIFIER: one frozen table, shared null: the RV-contraction ratio FOMC vs matched controls + the certified-data ΔVIX/ΔVX confirmation legs; if the contraction is not separated at pre-set MDE, both leads die together; if it is, one preregistered suppression-policy A/B on an existing engine's FOMC-day trades.
PRIOR: MED-HIGH that the contraction EXISTS on NQ; MED that any policy clears the cost of doing nothing (its natural use is subtractive — not trading expansion tactics into a known crush — which is cheap to adopt).
[/CARD]

[CARD id=MC-56]
NAME: Implied-move overstatement, futures shadow (0DTE-era IV > realized; beyond-sigma late-day state)
FAMILY: VOL
MECHANISM: Retail lottery demand for same-day options bids 0DTE implied vol above fair variance (iron-condor sellers profit across variants on minute-level SPX data; >75% of retail SPX option trades are 0DTE and retail sustains losses — the short-premium side collects). We own no options data, so the tradable shadow is the residual RV-undershoot: realized RTH range chronically below the VXN-implied 1-day sigma, and price beyond ±1 implied sigma late in the session facing reversion rather than continuation. The implied-sigma conditioning is the materially new observable separating this from the dead late-day fade graveyard.
MERGED-LEADS: S6-04 (Perz 2026 iron-condor minute-level backtest; Beckmeyer-Branger-Gayda retail-loss ledger 2023).
INDEPENDENT-SOURCES: 2 independent teams, both 0DTE-era, neither peer-reviewed yet.
EVIDENCE-BEST: EXAMPLES (careful preprints with real data; no audited replication).
OBSERVABLES: certified VXN daily → implied 1-day sigma; P(RTH range < implied sigma) by era; position vs ±1 sigma at 14:00 ET; 14:00→close continuation-vs-reversion vs the matched unconditional 14:00→close control.  DATA-CAPABLE-NOW: YES (certified VXN daily + NQ 1-min).
NOVELTY-VS-REPO: POLICY — late-day fade families are heavily represented in the dead list (TICK fade, sweep-reclaim, seven 2022-era fade geometries), so the bar is explicit: the beyond-sigma STATE must carry reversion information over the matched control or the card dies. Cross-link: MC-54's era-break leg decides which eras are admissible; MC-13/MC-42 own the flow side of the same window.
HORIZON: 14:00→16:00 ET.  COST-SENSITIVITY: HIGH (fade entries at extended prices).
CHEAPEST-FALSIFIER: two frozen tables, NQ 1-min + certified VXN 2006-2026, era-split at 2022-05: (1) P(realized < k·sigma) by era (pure measurement of the overstatement's futures shadow); (2) beyond-±1-sigma-at-14:00 state → 14:00→close distribution vs matched unconditional control, net-of-$33/RT expectancy gate preregistered.
PRIOR: MED — the IV-overstatement evidence is real, recent, and mechanism-coherent; the futures-only expression captures only a residual, and the fade graveyard caps enthusiasm.
[/CARD]

---

# W2 REINFORCEMENT UPDATES TO WAVE-1 CARDS (no new ids; leads folded in place)

- **MC-13 (late-day hedging-demand momentum)** ← S1-02 (Tuzun FEDS 2013 LETF "new portfolio insurers" — adds a genuinely independent Fed source), S1-03 + S3-05 + S6-09 (three scouts independently re-found Baltussen-Da-Lammers-Martens JFE 2021, DOI 10.1016/j.jfineco.2021.04.029 — same DOI already merged in W1 as A1-01; counts as ONE source, now sighted 4x across two waves). Net effect: independent-source count rises by ONE (Tuzun), not four. The W2 falsifier refinements worth keeping: score the SHORT leg separately vs the mirrored long leg (short-native gate), VIX-interaction term, and the MC-42 era column in the same harness. S1's family declaration binds: S1-02/03/04 share one null draw with this card's tests.
- **MC-03 (opening gap fill/continuation)** ← S4-04 (Plastun et al 2020, 1928-2018 peer-reviewed: gap-DAY momentum, "gaps get filled" explicitly unsupported — first peer-reviewed source on this card, upgrades EVIDENCE-BEST) and S1-10 (Hanna: large gap-downs bounce open-to-close in BOTH eras → a standing short-side entry VETO: never short a gap-down open on magnitude alone). New conditioning variable from S4-04: gap position INSIDE vs OUTSIDE the just-formed overnight range.
- **MC-12 (ETH session-hour structure)** ← S4-01 (Boyarchenko-Larsen-Whelan — same NY Fed team as the W1 merge; the W2 increment is the CONDITIONAL claim: post-SELL-OFF nights carry the robust positive 02:00-03:30 reversal while post-rally reversals are modest — a state-conditioned live branch inside a card whose unconditional object is dead by its own authors). Falsifier: prior-day RTH-return terciles × 02:00-03:30 net, sharing the wave and null with MC-48.
- **MC-29 (pre-scheduled-release drift)** ← S4-02 (Kurov-Sancetta-Strasser-Wolfe — DUPLICATE of the W1 merge A1-05/A12-08; second sighting, zero new sources). Keep the W2 refinement: split pre/post-2017 (lockup tightening) and the release-day vs matched-weekday slope design.
- **MC-25 (cross-asset risk conditioners)** ← S4-03 (Mourey-Shahrour-Șoiman BTC-weekend FRL — DUPLICATE of the W1 merge; second sighting. W2 adds the three-leg decomposition: reopen gap vs Sunday-night vs Monday-RTH, which sharpens the existing falsifier).
- **MC-34 (event-time bars & regime models)** ← S2-10 (Fayyaz et al frequency-controlled bar comparison — DUPLICATE of W1's A14-11, same paper, arXiv 2608.26158), S2-11 (Easley-LdP-O'Hara volume clock + Ané-Geman trade-count clock — the paradigm ancestors, now explicitly on the card), S2-12 (Gillemot-Farmer-Lillo NEGATIVE control: holding volume/trade rate fixed does NOT remove clustering or heavy tails; Murphy-Izzeldin: the Ané-Geman normality recovery fails replication — this bounds what any clock swap can deliver and predicts stage-2 failure), S2-14 (Engle-Russell ACD: inter-trade durations cluster and are forecastable on owned 2025-26 tick — RV-lift-only outcome classifies as RISK SPECIFICATION). The S2-11/S2-12 matched test is ONE run (kurtosis/AC of trade-clock vs clock bars on owned tick data) and doubles as the referee between the two.
- **MC-23 (breadth/TICK internals conditioning)** ← cross-reference to MC-41 (the short-native direction-asymmetric sub-hypothesis now has its own card; MC-23's general prereg and MC-41's tables share one family and one null draw).

Known-dead confirmations (no card, logged for the record): S1-06 and S3-06 re-surfaced VPIN — dead-listed (VPIN/BVC toxicity) and already handled inside MC-34/MC-47; only S3-06's weak-form cost-policy leg survives, inside MC-47. S1-13 re-surfaced Moreira-Muir — folded into MC-51.

---

# STRATEGY FAMILY TREE — WAVE 2 ADDITIONS

- SHORTSIDE (new) — MC-40 (forced-deleveraging continuation band) · MC-41 (failed-rally breadth divergence) · MC-42 (EOD short-covering headwind)
- EVENTTIME (new) — MC-43 (DC intrinsic-time structure) · MC-44 (DC-event trading policies) · MC-45 (swing-sequence grammar)
- VOL — add MC-38 (sharper vol state) · MC-52 (variance-risk states) · MC-54 (diurnal vol-curve + 0DTE break) · MC-56 (implied-move overstatement shadow)
- EVENT — add MC-46 (closing-auction imbalance) · MC-50 (event-conditioned overnight holds) · MC-55 (post-FOMC vol crush)
- CROSSMKT — add MC-39 (intraday VX-spike spillover) · MC-53 (cross-asset regime states)
- EXECUTION — add MC-47 (liquidity-state execution-cost policy)
- TIMEOFDAY — add MC-48 (session-handoff sign structure)
- PATH — add MC-49 (overnight sub-session partition)
- POLICY — add MC-51 (index vol-managed sizing)

Cross-links: MC-43 is the substrate MC-44 trades on; MC-54's era-break leg gates admissible priors for MC-38/52/55/56 and every other intraday-vol claim; MC-47 reprices the cost floor of EVERY card; MC-39/MC-42 are the VX-side and counter-flow columns of MC-13's harness; MC-48 shares a wave with the MC-12 update; MC-41 shares a family with MC-23's flagged prereg; MC-51/53 share the matched-exposure sizing harness; S1-10's veto binds any MC-40 entry design.

---

# SOURCE GRAPH — WAVE 2 UPDATES (new duplication clusters + node reinforcements)

11. **Baltussen–Da author family (Robeco/Notre Dame) = ONE node, now the most re-found source in the program.** JFE 2021 (intraday momentum) was independently re-surfaced by THREE W2 scouts (S1-03, S3-05, S6-09) after already anchoring MC-13 in W1; the same family's EOD-reversal WP (S1-14 → MC-42) is their own boundary condition. Any future lead citing "hedging demand and market intraday momentum" counts against this node.
12. **Olsen/Essex directional-change lineage = ~1.5 effective sources for ~8 apparent leads** (S2-01/02/03/05/06/07/08/13). Glattfelder-Golub-Olsen (Olsen school) and Tsang-Kampouridis (Essex lab) are heavily inter-linked; Houweling (S2-04) is a semi-independent author inside the same framework; Lo-Mamaysky-Wang (S2-09) is the only fully independent path-topology line. Count DC leads against this node.
13. **Easley–López de Prado–O'Hara school recurs across waves** (W1 A14-01/-02, W2 S1-06, S2-11, S3-06 — VPIN + volume clock = one program). Independent adversaries (Andersen-Bondarenko; Gillemot-Farmer-Lillo; Murphy-Izzeldin) are the credible referees and are merged into the same cards as controls.
14. **Man Group/Harvey shop = one node** (S5-02 vol-targeting + S5-11 drawdowns). **Kritzman/State Street = one node** (S5-07 turbulence + S5-12 regime shifts). Both flagged inside MC-51/MC-53's independence accounting.
15. **BestEx Research = one vendor family** (S3-09 time-of-day + S3-10 Pulse futures model); Quantitative Brokers is the independent second vendor on MC-47.
16. **Tuzun appears on both legs of the mechanical-flow story** (S1-02 LETF rebalancing sole-author; S1-05 flash-crash co-author) — one author, two genuinely different papers; count as distinct evidence but note the overlap.
17. **ICT killzone GitHub family → existing node #1** (S4-06 meegol repo + four sibling repos named in the same search are all Huddleston-derivative; the partition observable in MC-49 is the only non-folklore content).
18. **Node #10 reinforcement (Steenbarger, Hanna one-man-blog lineages):** W2 adds S1-07/-08 (Steenbarger → MC-41), S1-09/-10, S4-07 (Hanna → MC-40/MC-50/MC-03-update). Still mutually independent of each other; each still counts ONCE regardless of how many posts are cited.
19. **Wave-2 scout self-declared families (binding for null design):** S1-02/03/04 = one last-hour-flow hypothesis family (MC-13 + MC-39 share one draw); S3-01/02 share one test; S5-06/08/13 = one VIX-complex family (MC-52); S6-02/03 = one FOMC family (MC-55); S1-07/08 = one observable family (MC-41).

Scout usability: all 6 scouts contributed. Weakest evidence pockets: S4-06 (59-day self-reported ICT backtest), S6-04 (unreviewed preprints), S3 title-level claims where publishers blocked abstracts (flagged inline by the scout — do not quote magnitudes from those). Negative-space findings worth banking from S3: no credible public work on intraday illiquidity-state → next-interval index-futures return as standalone alpha, and no public measurement of the 15:50 imbalance spillover into index futures (MC-46's falsifier is an original test).
