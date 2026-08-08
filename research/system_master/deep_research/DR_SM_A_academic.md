# DR-SM-A — Academic / Quant-Finance Hypothesis Expansion
## Trend-quality and regime features CONDITIONAL on an existing trend signal (Solar R5-E10)

Date: 2026-08-08. Author: INDICATOR_SCOUT deep-research pass A (one of three independent passes).
Status: HYPOTHESIS CATALOG ONLY. Nothing here is a result. Every idea below requires a new
preregistered spec, its own sequence number, and passage through the SYSTEM_MASTER duplicate
filter before any data is read.

### Binding constraints honored throughout
1. **Right-tail hard gate** (README §Inherited): top 1% of Solar trades ≈ 160% of net. Any state
   down-weighted below m=1 must show top-1% P&L share ≤ its session share (C01 global gate).
   Default design here is therefore **up-weight-only exposure shaping (m ≥ 1)** unless stated.
2. **Threshold engineering is closed as a class** (DR03-H2 + T0-9). No idea below touches S,
   k·sigma, entry/exit thresholds, or flip logic.
3. **Suppression-style monetization is closed** (C01T1_ML): no bet/no-bet, no probability-ranked
   trade cuts. Admissible channels: continuous exposure scaling of the EXISTING position,
   portfolio-level allocation across sleeves, and complementary-engine gating.
4. **Day-level regime conditioning of Solar (vol/trend/day-type) is closed** (w8roleb, SW05,
   wave-index). Ideas that condition Solar must be mechanically different: intraday-updated
   state (not prior-close day tags), up-weight-only, or aimed at sleeves other than Solar.
5. Data on hand: NQ 1-min OHLCV 2006-01→2026-05 (`substrate/minute/NQ/nq1m_2005_202605.parquet`),
   NQ 3-min 2022-01→2026-07 (`runs/AUDIT03_BARS/`), 13 member ledgers, E10 daily vectors,
   announcement calendars 2005-2021 + 2022-2026. No options data, no L2 history, tick ≈ 12 mo.
6. Virgin data ≥ 2026-08-01 untouchable; scalping-lab holdout ≥ 2026-06-01 sealed.

**EVI scale**: 5 = decision-critical information, cheap to obtain, high prior of surviving gates;
1 = expensive or low prior or mostly redundant.

**Calibration meta-prior (EXTERNAL PRIOR)**: a 2026 systematic falsification study of OHLCV-only
intraday signals on MNQ reports that essentially all classic intraday OHLCV signal families fail
after realistic costs ([arXiv 2605.04004](https://arxiv.org/pdf/2605.04004)) — consistent with
this repo's own Zone-F and Program-B record. That prior argues for spending EVI on *conditioning
an existing edge* (exposure shape, allocation) rather than on new standalone OHLCV entry engines,
which is exactly the mandate of this file.

---

## RANKED IDEAS

### A-1. Slow/fast member-agreement phase state ("Momentum Turning Points" mapped onto the VolMult ladder) — EVI 4
- **Mechanism**: Garg–Goulding–Harvey–Mazzoleni (JFE 2023) partition return history into
  Bull / Correction / Bear / Rebound by the agreement/disagreement of slow vs fast time-series
  momentum signals; the phase carries conditional-mean information, including predictably negative
  returns when both signals are negative, and intermediate-speed blends earn positive
  unconditional alpha ([SSRN 3489539](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3489539),
  [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P158_Momentum_turning_points.pdf),
  [Alpha Architect summary](https://alphaarchitect.com/trendfollowing-momentum-turning-points/)). EXTERNAL PRIOR.
- **What it adds conditional on Solar**: the 13 members ARE a speed ladder (VolMult 6..30).
  Fast-member (vm6-vm10) vs slow-member (vm22-vm30) sign agreement is a phase state computable
  at every 3-min bar with zero new infrastructure. This refines the already-load-bearing
  `consensus` feature (5/5 fold-stable, only full-alignment bin P&L-positive, T0-6) by giving it
  an academically documented four-phase structure and an alpha-decomposition story, instead of a
  single scalar. Phase → continuous exposure multiplier m ∈ [1, m_max] on the E10 target
  (up-weight Bull/Bear full-agreement phases; never below 1 in Correction/Rebound).
- **Expected sign**: higher realized P&L per unit exposure in agreement phases; T0-6 already
  shows hit-rate 0.266→0.387 monotone in consensus, and profit concentrates in high-concurrency
  episodes (uniqueness-weighting inversion) — up-weighting agreement is tail-ALIGNED, not
  tail-adverse.
- **Data needed**: member position streams (already exported per bar in `e10m_v1_bars.csv`
  p6..p30). Nothing new.
- **EVI 4/5**: cheapest possible test of the strongest surviving feature; directly feeds Track 3
  (ensemble-internal confidence → exposure shape).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Consensus is explicitly NOT killed
  (C01 open door: "ensemble-consensus confidence scaling was NOT itself tested as an exposure
  rule"). What IS killed: logistic-overlay suppression (C01T1_ML) and any bet/no-bet channel.
  Mechanical difference: continuous m ≥ 1 scaling of the existing physical target, no trade ever
  suppressed, no probability ranking.

### A-2. HMM / regime-posterior as an ALLOCATOR for regime-local sleeves (not a Solar gate) — EVI 4
- **Mechanism**: Gaussian-mixture HMMs on daily return/RV features identify persistent vol/trend
  regimes; regime-adaptive allocation beats static allocation in index-futures studies 2006-2023
  (EXTERNAL PRIOR: [QuantStart](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/),
  [QuantifiedStrategies](https://www.quantifiedstrategies.com/hidden-markov-model-market-regimes-how-hmm-detects-market-regimes-in-trading-strategies/),
  [LSEG dev article](https://developers.lseg.com/en/article-catalog/article/market-regime-detection)).
  Filtered (causal) state probabilities are the online object; smoothing is look-ahead and must
  never be used for trading decisions.
- **What it adds conditional on Solar**: nothing is applied TO Solar. The system's actual open
  problem is that its best challenger (B-MOM: +$319k 2022-26, Sharpe 1.26 in-sample) is verdict
  REGIME-LOCAL — it "never statistically existed pre-2022." A sleeve that only works in one
  regime needs an explicit, causal regime tag to be portfolio-admissible at all. The W8 report
  itself names "a Solar-residual-weighted or regime-gated variant aimed at the rho_full term"
  as the sanctioned successor path. HMM filtered state = candidate gate/weight for B-MOM (and for
  the B1 overnight sleeve, whose edge is 2018+-loaded), with Solar's allocation left untouched.
- **Expected sign**: B-MOM weight ↑ in high-vol/high-dispersion state; portfolio rho_full vs
  Solar should FALL when B-MOM is inactive in the (calm) states where its P&L co-moves with
  Solar. Falsifiable: if regime-gated B-MOM rho stays ≥ 0.3, the construction dies.
- **Data needed**: 1-min → daily features 2006-2026 (RV, |ret|, overnight/intraday split);
  sleeves' daily P&L ledgers (already committed).
- **EVI 4/5**: it attacks the single named blocker of the only strong challenger; 20 years of
  data to fit regimes out-of-sleeve-sample (2006-2021 is unmined for B-MOM by construction).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Day-level regime conditioning OF SOLAR
  is closed; this conditions a *different sleeve's allocation*, which no prior experiment tested.
  Constraint inherited from W8: any successor variant aimed at the rho gate requires a NEW
  preregistered spec (anti-tuning clause) — the HMM state definition must be frozen on
  pre-2022 data before any 2022+ B-MOM overlap is read.

### A-3. Deterministic time-of-day exposure profile (intraday seasonality of trend quality) — EVI 4
- **Mechanism**: intraday vol/volume follow the universal U-shape in index futures
  ([Örebro WP 2025](https://www.oru.se/globalassets/oru-sv/institutioner/hh/workingpapers/workingpapers2025/wp-14-2025.pdf),
  [intraday trading invariance in ES](https://pages.nes.ru/aobizhaeva/ABKO-intradayinv.pdf));
  intraday momentum concentrates in the last half-hour (Gao-Han-Li-Zhou, JFE 2018,
  [SSRN 2440866](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866)); a plausible
  post-2022 amplifier is 0DTE gamma concentration into the trading day
  ([Cboe research](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf),
  [Dim et al., 0DTEs and vol propagation](https://westernfinance-portal.org/viewpaper?n=950096)). EXTERNAL PRIOR.
- **What it adds conditional on Solar**: local evidence already exists and survived fold
  screening: `sessbkt` is 5/5 fold-stable — 15:00-17:00 ET is the best bucket in every fold
  (weighted hit 0.421) and overnight 18:00-02:00 the worst (0.303). A **static clock profile**
  m(t) ≥ 1 (e.g., 1.0 baseline, ramp to 1.25-1.5× on 13:30-16:42 bars when a position exists)
  monetizes this WITHOUT prediction, regime tags, or suppression. It is the simplest untested
  exposure shape in the whole program.
- **Expected sign**: positive ΔlogG from concentrating exposure where per-trade expectancy is
  highest; tail-safe because late-day is where trend-day P&L accrues (top-10 days are RTH trend
  days per DAY_MARGIN evidence).
- **Data needed**: none new — E10 bar/fill ledgers + 3-min bars.
- **EVI 4/5**: one parameter-light rule, directly testable against the C01 exposure-gate
  machinery (ΔlogG, Romano-Wolf, split-half, tail retention) that already exists.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Not announcement conditioning (closed),
  not day-type conditioning (closed), not the 16:45-17:00 window question (closed — flatten
  adopted; profile must respect the 16:44 v2 flatten). Down-weighting overnight would require the
  tail test first (overnight bucket's share of top-1% P&L is unmeasured) — the preregistered
  primary arm must be up-weight-only; an overnight down-weight arm may run only as a gated
  secondary with the C01 tail constraint.

### A-4. Segment-anchored path efficiency (event-anchored Kaufman ER of the CURRENT trend leg) — EVI 3
- **Mechanism**: Kaufman's Efficiency Ratio = |net change| / Σ|bar changes| measures trend
  smoothness; standard usage filters chop on fixed lookbacks (EXTERNAL PRIOR:
  [TrendSpider primer](https://trendspider.com/learning-center/kaufman-efficiency-ratio/),
  [QuantifiedStrategies backtest](https://www.quantifiedstrategies.com/efficiency-ratio/)).
  Proposed variant: compute ER **anchored at the current Solar trend-birth extreme** (event time,
  not fixed window), so the statistic describes THIS leg's quality, resetting at each flip.
- **What it adds conditional on Solar**: eff120 (fixed 120-bar window) was only a borderline
  4/5 "passenger" in T0-6; the hypothesis is that the fixed window mixes legs and dilutes the
  signal, while an anchored ER is the natural sufficient statistic for "is this leg orderly or
  churny." Channel: continuous m ≥ 1 up-weight when anchored ER is high AND members agree
  (interaction with A-1), or as a state variable for the PORT-02 router
  (PERSISTENCE / FAILED_PERSISTENCE / AMBIGUOUS), which is an explicitly open door.
- **Expected sign**: high anchored-ER legs → higher continuation P&L per unit exposure
  (consistent with the r>1 overshoot economics living in orderly legs).
- **Data needed**: 3-min bars + flip timestamps from member ledgers. Nothing new.
- **EVI 3/5**: cheap; moderate prior (eff120's borderline result cuts both ways).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Fixed-window eff120 was screened
  (passed weakly) and its suppression monetization died with C01T1_ML; chop VETOES are killed
  (SW05 inverted). Mechanical differences: event-anchored (resets at flips), continuous up-weight
  channel, router-state usage. Any veto-style use is barred.

### A-5. Intra-session variance ratio (Lo-MacKinlay VR on trailing intraday window) — EVI 3
- **Mechanism**: VR(q) > 1 ⇒ positive serial correlation at horizon q; VR is the classical
  persistence statistic with a known null distribution
  ([Lo-MacKinlay overview](https://breakingdownfinance.com/finance-topics/finance-basics/variance-ratio-test/),
  [vrtest R docs](https://rdrr.io/cran/vrtest/man/Lo.Mac.html)). EXTERNAL PRIOR. High-frequency
  literature finds intraday returns often anti-persistent on average
  ([EuroStoxx futures persistence study](https://www.tandfonline.com/doi/full/10.1080/23322039.2024.2302639)),
  which is exactly why a *conditional* persistence state could separate trend hours from fade hours.
- **What it adds conditional on Solar**: T0-9 proved r ≈ 1.29 is a WITHIN-session property and
  that cross-session sequencing is empty — i.e., the persistence signal, if usable at all, must
  be measured *inside* the session. A trailing 2-3h VR(q=5..10) on 3-min returns, updated bar by
  bar, is the direct causal implementation. Channel: m ≥ 1 exposure tilt when VR is high while
  holding a position; also a candidate router state variable (≤3 state variables allowed).
- **Expected sign**: VR-high states → better continuation; VR ≈ or < 1 states carry no tilt
  (m=1), never suppression.
- **Data needed**: 3-min bars 2022-2026 (2006+ for structure checks). Nothing new.
- **EVI 3/5**: cheap; the T0-9 result is genuinely encouraging for within-session conditioning,
  but the day-level closure means the design must prove it is intraday-causal, not a day tag.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Distinct from the overshoot-r monitor
  (diagnostic only) and from CUSUM-k threshold engineering (killed — VR never touches thresholds).
  Day-level VR tags would be a duplicate of killed day-type conditioning; the spec must compute VR
  strictly intraday with same-session data only.

### A-6. Realized semivariance asymmetry / signed-jump variation conditional on position sign — EVI 3
- **Mechanism**: Patton–Sheppard: decomposing RV into upside/downside semivariance and signed
  jump variation improves vol forecasts; negative-jump variation predicts higher future vol,
  positive-jump variation lower ([Patton-Sheppard REStat 2015](https://public.econ.duke.edu/~ap172/Patton_Sheppard_REStat_2015.pdf),
  [working version](https://public.econ.duke.edu/~ap172/Patton_Sheppard_Realized%20Semivariance_11feb11.pdf)). EXTERNAL PRIOR.
- **What it adds conditional on Solar**: all prior vol conditioning here used TOTAL RV (HAR level,
  U-surprise) — both closed. Semivariance asymmetry is different data content: the SIGN split.
  Conditional hypothesis: a long Solar position accompanied by predominantly *upside*
  semivariance (orderly buying) has different continuation odds than one accompanied by downside
  semivariance spikes. Channel: m ≥ 1 when RSV asymmetry aligns with position direction; also a
  candidate risk-normalization input for Track 7 (sizing on downside semivariance rather than
  total sigma is a documented improvement in the vol-targeting literature).
- **Expected sign**: alignment (long + upside-dominated, short + downside-dominated) → up-weight
  earns; misalignment carries m=1.
- **Data needed**: 1-min or 3-min returns; per-session RSV+/RSV− computable causally intraday.
- **EVI 3/5**: new information axis (sign) on old machinery (RV pipeline exists from T0-4).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Must state difference vs the killed
  vol-surprise terciles: (i) sign decomposition not level/surprise; (ii) intraday-updated, not
  lag-1 session tags; (iii) up-weight-only primary. If a session-level lagged version is ever
  proposed it inherits the C01T1_EXPOSURE mechanism requirement (post-2024-only effects are
  presumed overfit without a mechanism).

### A-7. Trend-slope significance scaling (directional R² / slope t-statistic over trailing window) — EVI 3
- **Mechanism**: regressing price on time over a trailing window yields slope and R²; the slope
  t-stat is a self-normalizing trend-quality measure with a known sampling distribution — the
  regression cousin of the Kalman slope/uncertainty ratio (see DR-SM-C-1). Used widely in
  momentum research as "trend clarity" (EXTERNAL PRIOR — generic; see e.g.
  [Macrosynergy on trend/mean-reversion detection](https://macrosynergy.com/research/detecting-trends-and-mean-reversion-with-the-hurst-exponent/)).
- **What it adds conditional on Solar**: Solar members output only {-1,0,+1}; the ensemble mean
  adds coarse confidence (A-1); slope-t adds CONTINUOUS trend-clarity from the price path itself,
  orthogonal to member agreement by construction (members share one price stream but quantize
  it). Channel: m ≥ 1 multiplicative tilt when slope-t direction matches the physical position.
- **Expected sign**: positive interaction with position direction.
- **Data needed**: 3-min closes. Nothing new.
- **EVI 3/5**: cheap; some redundancy risk with A-4/A-5 and with C-file Kalman idea — the
  preregistered spec should test at most ONE of {slope-t, Kalman slope ratio} to conserve trials.
- **Duplicate-check verdict**: **CLEAR.** No prior experiment used regression-quality scaling;
  no threshold contact; no suppression.

### A-8. Market intraday momentum (first half-hour → last half-hour) as a LATE-DAY agreement feature — EVI 2
- **Mechanism**: Gao–Han–Li–Zhou (JFE 2018): first half-hour return (from prior close) predicts
  last half-hour return in SPY and 10 major ETFs; stronger on volatile, high-volume, news days
  ([SSRN 2440866](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866),
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351));
  hedging/gamma demand is the leading mechanism
  ([Baltussen-Da et al., hedging demand and intraday momentum](https://www3.nd.edu/~zda/intramom.pdf)). EXTERNAL PRIOR.
- **What it adds conditional on Solar**: NOT a new engine (that died locally — see rejected list).
  Sole admissible form: a binary agreement feature — "first-half-hour sign == current Solar
  position sign" — that up-weights the 15:00-16:42 exposure (interacts with A-3's profile).
- **Expected sign**: positive on agreement days, especially high-vol days (the paper's own
  conditioning), which are also Solar's tail days — tail-aligned.
- **Data needed**: 1-min/3-min bars. Nothing new.
- **EVI 2/5**: the local kill of the standalone version (H-A1: decayed post-2022, t≈1.0) is a
  strong negative prior; only the conditional-agreement version is worth one arm, bundled into
  the A-3 spec rather than its own wave.
- **Duplicate-check verdict**: **HIGH-RISK / CONDITIONALLY CLEAR.** H-A1/H-D5 killed rest-of-day
  AND first-30-min predictors of the last 30 min as standalone trades (net -4.5 to -10.3
  ticks/day after C1). B-MOM (always-monitoring open-anchored breakout) is regime-local and its
  retuning is barred. Mechanical difference that must hold: no standalone position is ever
  taken; the feature only scales an existing Solar position upward (m ≥ 1) late-day. If the
  duplicate filter reads this as H-A1 territory anyway, drop it — hence EVI 2.

### A-9. Overnight/intraday return decomposition as a structure feature (not a sleeve) — EVI 2
- **Mechanism**: overnight (close→open) carries most index risk premium; intraday carries almost
  none (EXTERNAL PRIOR: [NY Fed overnight drift / inventory-management explanation, Boyarchenko-Larsen-Whelan](https://elmwealth.com/night-moves-overnight-drift/),
  [Robot Wealth decomposition](https://robotwealth.com/revisiting-overnight-vs-intraday-equity-returns/),
  [news attribution study](https://arxiv.org/pdf/2507.04481)). The 2-3am ET component died
  2021-2025 (already in local evidence).
- **What it adds conditional on Solar**: a session-morphology feature: sessions where overnight
  and prior-intraday returns DISAGREE (inventory imbalance) may open with correction pressure,
  and sessions where they agree may trend. Feeds the B-file trend-day classifier (DR-SM-B-1)
  and the A-2 regime features rather than standing alone. Local caution: `gap_atr` failed T0-6
  fold-stability (3/5) — the raw gap is likely too noisy; the decomposition (gap SIGN × prior
  intraday sign, cumulative overnight range share) is a richer but related object.
- **Expected sign**: agreement mornings → mild up-weight of early exposure; disagreement → m=1.
- **Data needed**: 1-min 24h bars 2006-2026. Nothing new.
- **EVI 2/5**: cheap but the nearest local screen (gap_atr) already failed; treat as a feature
  candidate inside other specs, not its own wave.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** B1 overnight sleeve (hold overnight) is
  a separate frozen candidate — untouched here; T0-7 overnight sleeve deferred — untouched;
  gap FADES closed — no fading anywhere in this idea.

### A-10. Realized-vol term-structure slope (fast-RV / slow-RV ratio) as an expansion/contraction state — EVI 2
- **Mechanism**: HAR-family evidence that short-horizon RV vs long-horizon RV encodes vol regime
  transitions; multiplicative-component GARCH work isolates intraday periodicity from daily vol
  ([Bloomberg intraday vol model](https://assets.bbhub.io/professional/sites/10/intraday_volatility-3.pdf),
  [multiplicative GARCH](https://arxiv.org/pdf/2111.02376)). EXTERNAL PRIOR.
- **What it adds conditional on Solar**: Solar's edge lives at delta/sigma ≈ 10-18 with a fixed
  dollar friction floor (preregistered invalidation criterion 3: persistent vol compression kills
  the edge). A causal fast/slow RV ratio is the natural early indicator of expansion onset —
  candidate up-weight state for the first hours of expansion regimes, and a portfolio-level
  risk-normalization input (Track 7).
- **Expected sign**: expansion onset (ratio rising through 1) → up-weight earns; compression → m=1
  (never suppression — the low-vol friction-ratio eligibility idea S04 remains just a note).
- **Data needed**: 3-min bars. Nothing new.
- **EVI 2/5**: overlaps the closed vol-level/vol-surprise territory closely enough that the
  duplicate filter may reject; only the RATIO-of-horizons framing (term structure, not level,
  not surprise) is new. One arm max, bundled with A-6.
- **Duplicate-check verdict**: **HIGH-RISK.** Vol-LEVEL terciles (ARM_C) and vol-SURPRISE terciles
  (ARM_A/B) both failed C01 gates; ARM_C also failed the tail gate. Mechanical difference claimed:
  term-structure ratio ≠ level ≠ surprise, intraday-causal, up-weight-only. If the filter judges
  it the same U/level signal (corr(U, logRV)≈0.7 warns most vol features are one signal), drop.

### A-11. Local Hurst / DFA persistence monitoring (structural telemetry, not a trade) — EVI 1
- **Mechanism**: rolling-window Hurst/DFA exponents track persistence drift; intraday index data
  are usually anti-persistent, dailies near random walk (EXTERNAL PRIOR:
  [EuroStoxx futures persistence](https://www.tandfonline.com/doi/full/10.1080/23322039.2024.2302639),
  [heavy-tail estimation caveats](https://arxiv.org/pdf/1201.4786)).
- **What it adds conditional on Solar**: a second, independent estimator family for the SAME
  quantity MONITOR-01 tracks via overshoot-r (the preregistered early-warning statistic). Value
  is purely diagnostic: corroborating (or disputing) a future r→1.0 alarm with a method that has
  different small-sample pathologies.
- **Expected sign**: n/a (monitoring).
- **Data needed**: 3-min/1-min bars. Nothing new.
- **EVI 1/5**: no trade rule can come from it (day-level conditioning closed); zero config burn;
  add to the MONITOR-01 quarterly report only.
- **Duplicate-check verdict**: **CLEAR** as telemetry; would be a DUPLICATE (killed day-level
  persistence conditioning) if ever converted into a Solar gate.

---

## REJECTED-DUPLICATE — attractive academic ideas filtered out, and why

1. **Optimal CUSUM reference value k > 0 (Moustakides / Lam-Yam optimality)** — academically the
   most natural "improvement" to Solar's k=0 CUSUM structure. KILLED: DR03-H2 (retrace speed
   carries no next-trade information, p=0.35, rank-inverted) and T0-9 (surrogates reproduce
   r≈1.29) close **threshold engineering as a class**. No re-proposal.
2. **HAR-RV vol-surprise exposure terciles (and any lag-1 vol-state session tag)** — C01T1_EXPOSURE
   REJECTED (H1 sign negative, RW p ≥ 0.05, effect post-mid-2024 only). Revival requires a
   MECHANISM for post-2024-only existence (0DTE named as candidate); a bare re-run is barred.
3. **Announcement-day (FOMC/CPI/NFP) exposure conditioning, either direction** — C01-T0-5 closed
   BOTH directions; 24.2% of top-1% P&L sits on announcement days, so down-weights violate the
   tail gate and the up-weight failed its gate. The academically documented FOMC drift
   (pre-2015) is dead anyway ([Lucca-Moench pre-FOMC drift](https://www.bostonfed.org/-/media/Documents/conference/PDF/Lucca_preFOMCDrift.pdf), died post-2015 per DR-E).
4. **Meta-labeling / ML episode filters (López de Prado-style) on member trades** — C01T1_ML
   closed for suppression-style monetization: real AUC 0.556-0.575 exists, every
   probability-ranked cut is tail-adverse. Only non-suppression channels (A-1 style) are open.
5. **Standalone intraday momentum engines (first-half-hour, noon, last-hour)** — H-A1/H-D5 killed
   locally (decayed post-2022); B-MOM regime-local and gate-failed; the Gao et al. effect is
   admitted only as the A-8 agreement feature.
6. **Opening-gap fade / gap-fill statistics as an entry engine** — B01e/B02 axis CLOSED (90.1% of
   net in top 1% of trades, stopless left tail). Gap statistics survive only as inputs to a
   trend-day classifier (DR-SM-B-1).
7. **Variance risk premium / VIX-implied features (Family E)** — ON HOLD by prior registry
   decision, low priority, requires new preregistration with Bonferroni-significant condition (b)
   as FIRST gate; not re-proposed here (also: no options data on hand).
8. **Day-type / trend-vs-chop day classification applied as a Solar veto or day filter** — the
   general axis "day-level regime conditioning of Solar (vol/trend/day-type)" is closed
   (w8roleb, SW05 inverted chop veto would have deleted 74% of profit). Everything in this file
   that touches day structure is therefore routed to up-weight-only exposure shaping or to
   NON-Solar sleeves.
9. **Short-side regime gating via academic bear-market indicators (200d MA, vol percentile)** —
   SOLAR-01 closed with wrong sign (ungated shorts +$204,626); shorts stay symmetric as crisis
   insurance. May not be re-tuned with different constants.
10. **More NQ resampling / bootstrap "new OOS" claims** — thesis §20 ban; resampling 4.6y of NQ
    is exhausted; only genuinely forward data or cross-instrument mechanism tests move truth.
