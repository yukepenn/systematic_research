# DR-SM-B — Practitioner / Futures / Auction-Structure Hypothesis Expansion
## Opening structures, day types, volatility transitions, and event-day structure for a trend engine

Date: 2026-08-08. Author: INDICATOR_SCOUT deep-research pass B (one of three independent passes).
Status: HYPOTHESIS CATALOG ONLY. Practitioner claims are anecdotal unless a study is cited; ALL
external claims below are EXTERNAL PRIOR and carry lower evidentiary weight than the repo's own
ledgers. Every idea requires a new preregistered spec and duplicate-filter pass before data read.

### Framing
The single most valuable object for this program is an **early (by ~10:30 ET) classifier of
trend days**, because: (i) Solar's P&L is right-tail dominated (top 1% of trades ≈ 160% of net;
top 10 days = 64% of net) and those days are overwhelmingly RTH trend days; (ii) the hard
right-tail gate makes UP-weighting on likely trend days the one structurally tail-SAFE
conditioning direction; (iii) trend days are ~5-10% of sessions per practitioner lore
([FTMO Market Profile day anatomy](https://ftmo.com/en/blog/market-profile-types-of-opens-and-the-anatomy-of-a-trading-day/)),
so even a weak classifier concentrates exposure where the entire edge lives.

Constraints honored: no suppression/vetoes on Solar (closed), no announcement-day session tags
(closed both directions), no threshold contact (closed as class), no gap fades / ORB-failure
fades (closed), no seconds-scale level plays (FSS-9/FSS-10 closed), up-weight-only defaults.
Data: NQ 1-min OHLCV 2006-2026, NQ 3-min 2022-2026, E10 ledgers, announcement calendars. No
market-internals (TICK/ADD), no depth, no options positioning data — every classifier below must
be computable from OHLCV alone.

**EVI scale**: 5 = decision-critical, cheap, high prior; 1 = expensive/low prior/redundant.

---

## RANKED IDEAS

### B-1. Morning trend-day classifier v1: open location + initial-balance narrowness + early range extension — EVI 5
- **Mechanism** (auction theory, Dalton/Steidlmayer): trend days begin out of balance — open
  outside prior day's range/value, overnight inventory 100% skewed, narrow initial balance (IB =
  first 60 min range) that extends early and one-sidedly; the ideal trend day closes near the
  extreme opposite its open. EXTERNAL PRIOR:
  [FTMO day anatomy](https://ftmo.com/en/blog/market-profile-types-of-opens-and-the-anatomy-of-a-trading-day/),
  [TRADEPRO IB usage](https://tradeproacademy.com/how-to-use-the-initial-balance/),
  [Jim Dalton overnight inventory](https://jimdaltontrading.com/livedata/overnight-inventory/),
  [Aspen day structures](http://www.aspenres.com/documents/aspengraphics4.0/Day_Structures.htm).
  Quantified NQ-specific priors exist: open outside prior range is the second-strongest predictor
  of non-reversion after gap size; large gaps (>40% of prior range) rarely fill same-day
  ([TradingStats NQ 12-year opening-range stats](https://tradingstats.net/opening-range-close-probability/),
  [TradingStats NQ gap-fill 2015-2025](https://tradingstats.net/gap-fill-strategy/),
  [QuantifiedStrategies gap backtests](https://www.quantifiedstrategies.com/gap-fill-trading-strategies/)).
- **Definition sketch (all OHLCV-causal by 10:30 ET)**: features = {open vs prior RTH range/close,
  gap as % of prior range, overnight inventory skew (share of overnight bars above/below prior
  close), IB width / 20d median IB width, IB extension flag by 10:30, % of 1-min bars closing in
  gap direction}. Output: P(trend day) or a 3-state tag {TREND-CANDIDATE, BALANCE, UNCLEAR}.
- **What it adds conditional on Solar**: on TREND-CANDIDATE mornings, scale E10 exposure m ∈
  [1, 1.5] for the rest of the session (never below 1 elsewhere). Solar is stop-and-reverse and
  already in the market — the classifier only concentrates size on the days that create the tail.
  Secondary consumer: the PORT-02 router and the B-MOM allocator (B-MOM is a breakout engine —
  its good days should be exactly classifier-positive days; measurable rho reduction if gated).
- **Expected sign**: positive interaction: classifier-positive ∧ Solar-position-aligned-with-gap
  → higher P&L per unit exposure; tail retention IMPROVES by construction (up-weight on tail days).
- **Data needed**: 1-min OHLCV (have 2006-2026). Classifier can be FROZEN on 2006-2021 (data
  never mined for exposure rules) and evaluated once on 2022+ — a clean two-stage design few
  ideas here can match.
- **EVI 5/5**: attacks the tail-concentration structure directly; cheap; unique freeze-then-test
  data geometry; feeds three tracks (2/3 exposure shape, 5 B-MOM, 7 portfolio).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Closed neighbors: day-level regime
  conditioning of Solar (vol/trend/day-type — those were suppress/veto designs evaluated from
  PRIOR-day state); SW05 chop veto (inverted); announcement tags (closed). Mechanical
  differences: (i) computed INTRA-day from the developing session, not prior-day tags;
  (ii) up-weight-only — no trade suppressed, no size ever < 1×; (iii) goal is tail
  CONCENTRATION not avoidance. Gap-fade and ORB-fade kills are untouched (no fading).
  B01c's Solar-alignment veto (failed) was a fade-engine component, not an up-weight state.

### B-2. Opening type taxonomy (Open-Drive / Open-Test-Drive / Open-Rejection-Reverse / Open-Auction) as a 10:00 ET conviction tag — EVI 4
- **Mechanism**: Market Profile open types grade opening conviction by whether price drives
  one-sidedly from the bell without returning to the open (Open-Drive: highest trend-day odds),
  tests one side then drives (OTD), or rotates around the open (Open-Auction: balance likely).
  EXTERNAL PRIOR: [FTMO types of opens](https://ftmo.com/en/blog/market-profile-types-of-opens-and-the-anatomy-of-a-trading-day/),
  [Marketcalls profile day types](https://www.marketcalls.in/market-profile/market-profile-different-types-of-profile-days.html),
  [Topstep auction-theory intro](https://www.topstep.com/blog/intro-to-auction-market-theory-and-market-profile/).
- **Definition sketch**: from 09:30-10:00 1-min bars: does price ever trade back through the
  09:30 open (drive vs test), max adverse rotation in ticks, % one-directional closes, open
  position within first-30-min range. Deterministic tag, zero fitted parameters possible.
- **What it adds conditional on Solar**: an EARLIER (10:00 vs 10:30) and cheaper conviction tag
  than B-1; natural interaction: Open-Drive in the direction of the current Solar position →
  early up-weight; Open-Auction → m=1 (no penalty). Also a candidate feature for when B-MOM's
  breakout day works (Open-Drive days are its natural habitat).
- **Expected sign**: Open-Drive agreement days carry outsized continuation (practitioner
  consensus; must be verified on 2006-2021 first).
- **Data needed**: 1-min OHLCV. Nothing new.
- **EVI 4/5**: near-zero engineering cost, freezable pre-2022, high interpretability (auditable
  state variable for PORT-02, which caps at ≤3 state variables).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS** — same constraint set as B-1. Distinct
  from killed ORB entries (no breakout ENTRY is taken; the tag scales an existing position).

### B-3. Afternoon confirmation state: one-sided range extension without IB re-entry ("confirmed trend day") for a 13:30-16:42 exposure ramp — EVI 4
- **Mechanism**: once IB extends and price never re-enters the IB (no rotation back through IB
  mid), the day is a confirmed trend day; late-day continuation is then amplified by (a)
  documented last-half-hour momentum ([Gao-Han-Li-Zhou JFE 2018](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866)),
  (b) hedging/rebalancing demand ([Baltussen-Da, hedging demand and intraday momentum](https://www3.nd.edu/~zda/intramom.pdf)),
  and (c) post-2022, 0DTE gamma concentration that can intensify one-sided afternoons
  ([Cboe 0DTE research](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf),
  [Dim et al. 0DTE gamma risk](https://westernfinance-portal.org/viewpaper?n=950096)). EXTERNAL PRIOR.
- **What it adds conditional on Solar**: local evidence already points here: sessbkt 15:00-17:00
  is the best bucket in every T0-6 fold (0.421 weighted hit). This idea converts B-1's morning
  FORECAST into an afternoon STATE (no forecasting needed): if confirmed-trend-day ∧ Solar
  position agrees with the day's drive direction → ramp m toward 1.5 until the 16:42 flatten
  decision bar; else m=1. The 0DTE mechanism note matters beyond this idea: it is the named
  candidate mechanism class for post-2022-only effects, which the vol-surprise revival clause
  requires.
- **Expected sign**: positive; concentrates exposure into exactly the sessions/hours that
  produced the top-10 days (98.6% of which E10 already retains — this makes them bigger, not
  fewer).
- **Data needed**: 1-min/3-min OHLCV; E10 position stream. Nothing new.
- **EVI 4/5**: state-based (no prediction error), tail-aligned, trivially preregisterable with
  the existing C01 exposure-gate machinery (ΔlogG, RW p, split-half, tail retention).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Not the killed last-30-min standalone
  momentum trade (H-A1) — no new position, no entry, scaling only; not the closed 16:45-17:00
  window question (respects v2 16:44 flatten); not announcement conditioning.

### B-4. VWAP-side persistence day tag (price holds one side of session VWAP for N consecutive 3-min bars) — EVI 3
- **Mechanism**: practitioners define trend days as "one side of VWAP all day" — VWAP is the
  institutional execution benchmark, and persistent one-sided deviation means initiative flow is
  absorbing all responsive selling/buying. EXTERNAL PRIOR (practitioner convention; e.g.
  [Vtrender profile/day-type guides](https://vtrender.com/posts/market-profile-day-types),
  [GoCharting Market Profile guide](https://gocharting.com/blog/market-profile-indicator/market-profile-complete-guide)).
- **What it adds conditional on Solar**: a running, causal "one-sidedness" counter that is
  mechanically independent of Solar's anchor/threshold machinery, usable as (i) a third input to
  the B-1/B-3 classifier, (ii) the PERSISTENCE leg of the PORT-02 router state.
- **Expected sign**: long streaks above VWAP + long Solar position → up-weight earns.
- **Data needed**: 1-min OHLCV + volume for session-anchored VWAP (volume exists in the minute
  parquet; back-adjust volume caveat near rolls is on record and bounded).
- **EVI 3/5**: cheap; correlated with B-2/B-3 (spend at most one arm on it inside their spec).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** FSS-9 killed VWAP sweep-reclaim at
  SECONDS scale as an entry engine — this is a session-scale STATE, no entry, no reclaim logic.
  B-MOM's VWAP+noise-band breakout construction is a different (entry) object; its anti-tuning
  clause is not touched because no B-MOM parameter is reused or refit. Any deterioration of this
  tag into a fade/reversion entry at VWAP would be a DUPLICATE (VWAP-magnet reversion rejected in
  DR-05 lore review).

### B-5. Daily compression → expansion setup (NR7 / inside-day / multi-day range contraction) as a NEXT-day up-weight prior — EVI 3
- **Mechanism**: Crabel: narrow-range and inside days mark contractions that precede range
  expansion; NR7 is the classic operationalization. EXTERNAL PRIOR:
  [StockCharts NR7](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/narrow-range-day-nr7),
  [QuantifiedStrategies NR7 backtest](https://www.quantifiedstrategies.com/nr7-trading-strategy-toby-crabel/),
  [Crabel NR4/NR7/ID notes](https://time-price-research-astrofin.blogspot.com/2023/09/nr4-nr7-narrow-range-4-7-id-inside-days.html).
- **What it adds conditional on Solar**: expansion days are where a stop-and-reverse trend engine
  earns; a compression tag known at yesterday's close raises next-session expected range without
  saying anything about direction (direction comes from Solar itself). Channel: next-session
  m ∈ [1, 1.25] up-weight; also feeds B-1 as a prior.
- **Expected sign**: positive on expansion realization; neutral cost when expansion fails (m≥1
  keeps baseline).
- **Data needed**: daily bars derivable from 1-min (2006-2026). Nothing new.
- **EVI 3/5**: cheap, 20 years of events, direction-free (avoids forecasting).
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** FSS-6 compression→expansion at
  SECONDS scale was reclassified ABSENT-IN-REGIME (not falsified) — different clock entirely
  (daily vs seconds), and this is a sizing prior, not an entry. It is PRIOR-day information, so
  it brushes the closed "day-level conditioning" axis: the mechanical difference is up-weight-only
  sizing (the closed axis was veto/suppression); the spec must say this explicitly.

### B-6. FOMC 14:00 day STRUCTURE at ≥30-min horizons (the un-tested announcement clock) — EVI 3
- **Mechanism**: practitioner and academic evidence agree FOMC days have a stereotyped intraday
  shape: pre-announcement quiet/drift-less since 2015, a 14:00 spike, a whipsaw phase, then a
  "resolution" trend from ~14:45-15:00 into the close; the first 5-min move direction is
  reversed by the close 60-70% of the time in 2019-2025 samples. EXTERNAL PRIOR:
  [tosindicators 4-stage FOMC pattern](https://tosindicators.com/research/fomc-volatility-stages-day-trading-guide),
  [Lucca-Moench pre-FOMC drift (dead post-2015)](https://www.bostonfed.org/-/media/Documents/conference/PDF/Lucca_preFOMCDrift.pdf),
  [post-FOMC drift in bonds, NBER w25127](https://www.nber.org/system/files/working_papers/w25127/revisions/w25127.rev1.pdf),
  [Fed FEDS 2026 note](https://www.federalreserve.gov/econres/feds/files/2026023pap.pdf).
- **What it adds conditional on Solar**: everything tested locally was 08:30 releases (NFP/CPI):
  continuation at 09:30 is anti-edge (E1), the 09:30 fade is PARKED (B-FADE, OOS 1/30th of IS),
  and FOMC 14:00 days were EXCLUDED from those constructions. The 14:45-16:00 resolution window
  is therefore genuinely unexamined here at the ≥30-min horizon. Two admissible forms:
  (i) complementary micro-sleeve: enter WITH the 14:45-15:15 established post-whipsaw direction,
  exit 16:00-16:42, ~8 events/yr — low n, so pool 2006-2026 (calendar exists to 2021 + dev
  calendar 2022+); (ii) information-only: measure whether Solar flip P&L in 14:00-16:00 on FOMC
  days differs enough to justify a future spec. Form (ii) is free of gate risk and should run first.
- **Expected sign**: resolution-window continuation positive (practitioner prior); pre-2015
  pre-drift NOT expected to return.
- **Data needed**: FOMC dates 2006-2026 (public; the 2022+ calendar exists in
  `c01_announcement_calendar.csv`, pre-2022 FOMC dates must be added — BLS calendar covers only
  NFP/CPI); 1-min bars.
- **EVI 3/5**: small-n but 20 years pooled ≈ 160 events; the one event-clock never touched.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Announcement-day EXPOSURE conditioning
  of Solar is closed BOTH directions — form (i) is a separate sleeve with its own book, NOT a
  Solar multiplier, and form (ii) reads ledgers without trading. B-FADE's anti-tuning/parked
  status is untouched (different release time, different entry clock, continuation-not-fade).
  If the duplicate filter reads any Solar-exposure variant into this, only form (i)/(ii) as
  written may proceed.

### B-7. Gap-and-go continuation tag (large unfilled gap = trend-day evidence, never an entry) — EVI 2
- **Mechanism**: NQ-specific practitioner statistics: gaps > ~40% of prior day range rarely fill
  same-day; unfilled gaps by 10:00-10:30 tend to run (go-with rule); gap-up days continue while
  gap-down days are absorbed by the secular bid. EXTERNAL PRIOR:
  [TradingStats NQ gap-fill 2,791 days](https://tradingstats.net/gap-fill-strategy/),
  [ShadowTrader/Dalton gap rules](https://jimdaltontrading.com/livedata/expected-inside-opening/),
  [QuantifiedStrategies gap studies](https://www.quantifiedstrategies.com/gap-fill-trading-strategies/).
- **What it adds conditional on Solar**: one binary feature for B-1 ("large gap still unfilled at
  10:30 in Solar's direction"), sharpening the trend-candidate tag on the ~15% of sessions with
  material gaps.
- **Expected sign**: positive interaction with Solar position alignment.
- **Data needed**: 1-min OHLCV. Nothing new.
- **EVI 2/5**: real but small marginal value over B-1's open-location features (gap size and
  open location are correlated); gap_atr already failed T0-6 fold stability as a raw feature —
  the conditional (unfilled-by-10:30) version is the only variant worth carrying.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Gap FADES are closed (B01e/B02) — this
  never fades; F06 "gap continuation vs rejection" sits in the deprioritized-but-not-closed
  Family-B list — proposing it ONLY as a classifier feature (not an engine) avoids that lane.

### B-8. Overnight inventory skew as an early-correction warning (go-with-after-correction logic) — EVI 2
- **Mechanism**: Dalton: when overnight inventory is 100% long/short (entire overnight session
  one side of prior close), odds of an early morning correction rise before any trend resumes;
  correction-then-resume is the trend-day-compatible path. EXTERNAL PRIOR:
  [Jim Dalton overnight inventory](https://jimdaltontrading.com/livedata/overnight-inventory/),
  [ShadowTrader market-profile primers](https://www.shadowtrader.net/market-profile-analysis-of-sp-futures-05-14-19-2/).
- **What it adds conditional on Solar**: timing refinement for B-1's up-weight: on 100%-skewed
  overnights, delay the exposure ramp until the first correction completes (e.g., first touch of
  the overnight midpoint or 10:00, whichever first) instead of ramping at 09:30. Reduces the
  chance that the up-weight buys the open's inventory flush.
- **Expected sign**: fewer adverse first-hour excursions on ramped days; net effect small.
- **Data needed**: 1-min 24h OHLCV. Nothing new.
- **EVI 2/5**: refinement of B-1, not standalone; test only as a B-1 arm.
- **Duplicate-check verdict**: **CLEAR** (no fade, no suppression, no threshold contact; B1
  overnight-hold sleeve untouched).

### B-9. Balanced-day tag for a complementary responsive engine (Track 6, NOT Solar) — EVI 2
- **Mechanism**: auction lore: non-trend days (majority) rotate around value; responsive
  mean-reversion at range extremes works ONLY on balanced days; the 80% value-area rule is the
  classic form. EXTERNAL PRIOR: [Vtrender day types](https://vtrender.com/posts/market-profile-day-types),
  [Dalton expected inside opening](https://jimdaltontrading.com/livedata/expected-inside-opening/).
- **What it adds conditional on Solar**: Solar bleeds on chop (TUW 1,112/1,184 sessions is
  mostly chop bleed); a complementary engine that earns on B-1-negative (balance) days is the
  textbook diversifier — IF it can clear costs, which every fast responsive family so far
  failed. The honest framing: this is a Track-6 factory candidate with a LOW prior, admissible
  only at ≥30-min holds, entries at IB/prior-value extremes on days tagged BALANCE by 10:30,
  exits at session midpoint/VWAP, hard n≥150-event gate.
- **Expected sign**: positive on balance days by construction of the tag; correlation to Solar
  losing days should be NEGATIVE (that is the entire value proposition and the first gate).
- **Data needed**: 1-min OHLCV 2006-2026. Nothing new.
- **EVI 2/5**: high strategic value if it survives, but every neighboring family (F07
  balanced-value reversion) inherits negative evidence and sits deprioritized; cost floor at
  30-min holds is clearable in principle (median 30-min |move| ≈ 116t vs 3.5t friction) but the
  fade-family record here is 0-for-everything.
- **Duplicate-check verdict**: **HIGH-RISK.** F07 (balanced-value reversion) is explicitly listed
  as deprioritized-not-closed; B01c ORB-failure fade and B02 gap fade are CLOSED and must not be
  reproduced inside this engine (no failed-breakout entries, no gap logic). Only a genuinely
  responsive value-rotation construction at ≥30-min holds, preregistered fresh, avoids the
  duplicate label. Proceed only if Track 6 has budget after higher-EVI items.

### B-10. OPEX / quarterly expiry calendar as a structure covariate (measurement first, never a weight) — EVI 1
- **Mechanism**: practitioner consensus holds monthly/quarterly option expiries pin indexes and
  suppress trend; post-2022 the 0DTE share (≈47-59% of SPX volume by 2024-25) may have diluted
  classic OPEX pinning ([Optionalpha 0DTE volume trends](https://optionalpha.com/blog/the-rise-of-spx-0dte-trading-analyzing-volume-trends),
  [ION 0DTE surge](https://iongroup.com/blog/markets/0dte-options-surge-why-investors-are-betting-big-on-same-day-expiries/)). EXTERNAL PRIOR, weak.
- **What it adds conditional on Solar**: measurement only: does Solar flip-P&L differ on
  OPEX/quad-witching days 2006-2026? If a stable drag exists it informs the LEVERAGE_FRONTIER
  stress calendar; it must NOT become a down-weight (announcement-conditioning precedent shows
  calendar down-weights hit the tail gate).
- **Expected sign**: mild drag on OPEX days pre-2022, attenuating post-2022.
- **Data needed**: expiry calendar (deterministic 3rd Fridays); ledgers.
- **EVI 1/5**: information only; no admissible trade channel identified in advance.
- **Duplicate-check verdict**: **CLEAR as measurement**; any exposure rule from it would land in
  the closed announcement/day-tag territory and is pre-declared out of scope.

---

## REJECTED-DUPLICATE — attractive practitioner ideas filtered out, and why

1. **Opening range breakout as a standalone engine (5-min/15-min/30-min ORB)** — the celebrated
   Zarattini-Barbon-Aziz results ([QQQ ORB](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284),
   [stocks-in-play ORB](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/))
   are seductive, but locally "breakout continuation at ANY clock" is killed with the explicit
   retry clause *"different mechanism class only, not another clock"* — a 30-min ORB is another
   clock. Also ORB's own base rate (~17% win / 83% stop-out, right-tail-carried) duplicates the
   tail-fragility profile the program already owns. Only the CLASSIFIER use of opening structure
   (B-1/B-2, no breakout entry) is proposed.
2. **ORB-failure / failed-auction fades** — B01c closed (net -$22,534 slip-1, PF 0.839, adverse
   2.4:1 stop distance). No reacceptance-fade re-tune.
3. **Opening gap fades (any flavor: fill plays, half-gap targets)** — B01e/B02 axis CLOSED
   (top-1% = 90.1% of net, stopless left tail); a stopped variant explicitly may not be built by
   adjusting the read result.
4. **VWAP touch/reclaim, PDH/PDL sweep-reclaim entries** — FSS-9 killed 0/120 at seconds scale;
   VWAP-magnet reversion has no peer-reviewed support (DR-05). VWAP appears above only as a
   session-scale side-persistence STATE.
5. **08:30 release-day continuation OR re-tuned fade** — continuation is anti-edge (E1: -53t@15min);
   the fade is PARKED (B-FADE: OOS 1/30th of IS) and may only be resolved by forward data or a
   Tier-3 sealed holdout — not by a new backtest variant. FOMC 14:00 (B-6) is the only
   announcement clock not consumed.
6. **Announcement-day up/down exposure weighting (CPI/NFP/FOMC session tags)** — C01-T0-5 closed
   both directions; 24.2% of top-1% P&L sits on announcement days.
7. **Chop-day vetoes / "stand aside on inside days" rules** — SW05 chop veto INVERTED (would
   delete 74% of profit); all suppression forms closed. Every day-structure idea above is
   up-weight-only for this reason.
8. **Last-30-minutes momentum trade ("power hour" standalone)** — H-A1/H-D5 killed, decayed
   post-2022. Late-day strength survives only as the B-3 exposure ramp on an existing position.
9. **Pinning/max-pain trades and 0DTE-flow front-running** — no options data on hand, and the
   documented intraday 0DTE effects are episodic and flow-conditional
   ([Cboe](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf)); without
   positioning data this is untestable here. 0DTE enters only as a MECHANISM annotation.
10. **Market-internals trend-day tells (cumulative TICK, ADD, breadth thrust)** — data not in the
    inventory (no internals history); mandate forbids paid data. Listed so nobody re-proposes it
    without first solving the data gap.
11. **B-MOM band-window or gate re-tuning to pass the rho gate** — explicitly barred by the W8
    anti-tuning clause; the only sanctioned successor is a NEW preregistered regime-gated /
    Solar-residual-weighted spec (see DR-SM-A-2).
