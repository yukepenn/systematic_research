# DR-SM-C — Signal Processing / Control / State Estimation Hypothesis Expansion
## Causal filters, regime detection with known delay, sizing control theory, ensemble uncertainty

Date: 2026-08-08. Author: INDICATOR_SCOUT deep-research pass C (one of three independent passes).
Status: HYPOTHESIS CATALOG ONLY. All external claims labeled EXTERNAL PRIOR. Every idea requires
a new preregistered spec and duplicate-filter pass before any data read.

### Standing engineering facts this file must respect
- Solar's flip rule IS a one-sided CUSUM with k=0 (Lam-Yam identification, DR-03), and
  **threshold engineering as a class is permanently closed** (DR03-H2 + T0-9). Therefore NO idea
  below modifies detection statistics, reference values, thresholds, bands, or flip logic.
  Admissible outputs are: exposure multipliers on the existing E10 target, portfolio/sleeve
  allocation weights, leverage/drawdown policy, and monitoring statistics.
- Suppression is closed (C01T1_ML); vol-level and vol-surprise session tags are closed
  (C01 ARM_A/B/C, tail gate); day-level regime conditioning of Solar is closed. DR-E s.2:
  vol-informed sizing is admissible ONLY as continuous fractional-Kelly-style scaling — anything
  that zeroes trades re-enters the falsified axis.
- Right-tail hard gate: any state with m < 1 must prove top-1% P&L share ≤ session share.
  Default below: m ∈ [1, m_max].
- Leverage is gated by thesis §21 (14 preconditions); all sizing work below is research-scenario
  only. Kelly full ≈ 1 NQ per ~$85k at Sharpe ≈ 0.97 (DR-E Lane C); scalp-lab robust-sizing
  frontier delivered safe c = 0.15. Amendment 6: Kelly sizing is "a frontier, not a certain win."
- Data: NQ 1-min 2006-2026, NQ 3-min 2022-2026, member/E10 ledgers, daily P&L vectors.

**EVI scale**: 5 = decision-critical, cheap, high prior; 1 = expensive/low prior/redundant.

---

## RANKED IDEAS

### C-1. Consensus-proportional exposure (ensemble model-averaging posterior as a continuous sizing signal) — EVI 5
- **Mechanism**: in model averaging / deep-ensemble practice, inter-member agreement is the
  canonical epistemic-confidence signal: low disagreement ⇒ high-confidence prediction; variance
  across members flags unreliable states (EXTERNAL PRIOR:
  [Lakshminarayanan et al., deep ensembles](https://arxiv.org/pdf/1612.01474),
  [deep-ensembles overview](https://www.emergentmind.com/topics/deep-ensembles),
  [ensemble-RL variance filtering for trading](https://arxiv.org/html/2502.17518v3)). The 13
  VolMult members are precisely a model-averaged posterior over trend state at 13 scales; |mean
  member position| ∈ {0, 1/13, ..., 1} is its concentration.
- **What it adds conditional on Solar**: the single strongest surviving local fact: consensus is
  5/5 fold-stable, hit 0.266→0.387 monotone, only the full-alignment bin is P&L-positive, and
  C01 explicitly recorded that **consensus-scaling as an exposure rule was never tested** (only
  suppression channels died). Proposal: physical target = round(10·mean·g(|mean|)) with g
  monotone, g(low)=1, g(1)=m_max ∈ [1.25, 1.5], capped at ±10+Δ MNQ. Up-weight-only ⇒ tail-safe
  by construction; and because profit concentrates in high-concurrency episodes (T0-6
  uniqueness-inversion), g up-weights exactly the episodes that carry the right tail.
- **Expected sign**: ΔlogG > 0 with tail retention ≥ 100% of baseline (up-weight of tail states).
- **Data needed**: none new — member position streams per bar exist (`e10m_v1_bars.csv`).
- **EVI 5/5**: the program's highest-confidence untested exposure shape; one free function g
  (preregister 2 candidate shapes max); evaluable with the existing C01 gate machinery.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** Killed neighbors: ML suppression
  (C01T1_ML — different channel), E-variant rounding menu (E10 frozen — this creates a NEW
  configuration with its own spec/sequence, comparator stays R5-E10), member reweighting H-013
  (not run, superseded — this does NOT reweight members, it scales the aggregate). Note the E10
  cap: g must respect margin arithmetic and the 16:44 flatten; max exposure rises above 10 MNQ
  only if the spec says so explicitly.

### C-2. Kalman local-linear-trend filter: slope/uncertainty ratio as a continuous trend-clarity multiplier — EVI 4
- **Mechanism**: a 2-state Kalman filter (level + slope) on 3-min closes yields at every bar a
  slope estimate AND its posterior variance — a self-calibrating trend signal-to-noise ratio
  z_t = slope/√var(slope); state-space trend extraction is standard and strictly causal
  (EXTERNAL PRIOR: [Benhamou, "Trend without hiccups — a Kalman filter approach"](https://arxiv.org/pdf/1808.03297),
  [Alpha Architect trend-following filters series](https://medium.com/@alphaarchitect/trend-following-filters-part-5-ef99d0a6e122),
  [EViews local linear trend via Kalman](https://blog.eviews.com/2024/08/estimation-of-local-linear-trend-via.html),
  [distributionally-robust KF under vol uncertainty](https://arxiv.org/pdf/2302.05993)).
- **What it adds conditional on Solar**: Solar quantizes trend state to ±1 per member; z_t adds a
  continuous, uncertainty-weighted clarity measure from the same price stream, with honest lag
  determined by the (preregistered, not fitted) Q/R noise ratio. Channel: m = 1 + c·max(0,
  sign-match(z_t, position))·min(|z_t|, z_cap)/z_cap, i.e., continuous fractional-Kelly-style
  scaling exactly in the DR-E-admissible form. Also supplies the slope-uncertainty input C-7's
  Kelly haircut needs.
- **Expected sign**: position-aligned high-|z| states carry higher expectancy per unit exposure.
- **Data needed**: 3-min closes. Nothing new. Q/R must be FROZEN from 2006-2021 data or set by
  a stated rule (e.g., to match a chosen group delay), never tuned on 2022+.
- **EVI 4/5**: cheap, continuous, orthogonal channel to consensus (price-path vs member-vote);
  at most ONE of {C-2, DR-SM-A-7 slope-t} should be specced to conserve trials.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** No threshold contact (never feeds the
  flip rule); not vol-level session tags (intraday, continuous, up-weight-only). A Kalman-based
  REPLACEMENT of Solar's filter would be new-Solar-parameter-mining — banned; this is scaffolding
  on top of the frozen engine only.

### C-3. Sequential decay/change detection on SLEEVE P&L (CUSUM/GLR with preregistered ARL) — formalizing MONITOR-01 into an allocator input — EVI 4
- **Mechanism**: sequential change-point tests (Page CUSUM, GLR) provide known average-run-length
  (ARL) tradeoffs: detection delay vs false-alarm rate chosen IN ADVANCE; BOCPD gives the
  Bayesian run-length-posterior version (EXTERNAL PRIOR:
  [Adams-MacKay BOCPD](https://arxiv.org/abs/0710.3742),
  [BOCPD paper PDF](https://lips.cs.princeton.edu/pdfs/adams2007changepoint.pdf)). Applied to
  STRATEGY daily P&L (not prices), this is the classic "is the edge dead?" monitor with an
  auditable delay guarantee.
- **What it adds conditional on Solar**: the program already committed to MONITOR-01 (quarterly
  overshoot-r reads, alarm ⇒ freeze + attribution). A CUSUM on E10 daily P&L (drift = 0 null vs
  historical mean, k = half-shift per Moustakides applied to the P&L stream — NOT to prices)
  plus the same on B-MOM/B1 sleeves turns ad-hoc quarterly reads into a control chart with
  preregistered ARL, and gives the PORT allocator a principled de-allocation trigger for
  REGIME-LOCAL sleeves (B-MOM's central risk is silent decay). This is where detection theory is
  actually admissible in this program — on P&L streams, where threshold-engineering closure does
  not apply.
- **Expected sign**: n/a for Solar P&L (monitoring); for the portfolio, earlier de-allocation of
  a dying regime-local sleeve strictly improves geometric growth in the decay scenario.
- **Data needed**: committed daily vectors (E10_round_session, w8bmom daily, w9b1 nightly).
  Nothing new. Calibrate ARL on pre-2022 surrogate/blocked resamples.
- **EVI 4/5**: cheap; converts two standing owner-level worries (Solar decay, B-MOM
  regime-locality) into one auditable mechanism; no gate risk (monitoring + portfolio layer).
- **Duplicate-check verdict**: **CLEAR.** Distinct from killed CUSUM-k threshold engineering
  (that operated on PRICE changes to move flip thresholds; this operates on strategy P&L and
  moves ALLOCATION). DSR-as-promotion-criterion was abandoned — this replaces nothing in
  promotion; it is an operations trigger.

### C-4. Risk-constrained Kelly for the two-sleeve portfolio (Busseti-Ryu-Boyd) as the LEVERAGE_FRONTIER engine — EVI 4
- **Mechanism**: maximize long-run growth subject to a convex drawdown-risk constraint
  P(W_min < α) < β; convex program, solvable exactly for discrete return scenarios; the
  drawdown-constrained analog of fractional Kelly with an explicit risk knob (EXTERNAL PRIOR:
  [Busseti-Ryu-Boyd, Risk-Constrained Kelly Gambling](https://web.stanford.edu/~boyd/papers/pdf/kelly.pdf),
  [Grossman-Zhou drawdown-constrained growth](https://arxiv.org/pdf/1206.2305),
  [IBKR risk-constrained Kelly series](https://www.interactivebrokers.com/campus/ibkr-quant-news/the-risk-constrained-kelly-criterion-from-the-foundations-to-trading-part-i/)).
- **What it adds conditional on Solar**: Track 7 must output LEVERAGE_FRONTIER numbers with
  drawdown/TUW as first-class objectives — exactly this program's objective function. Feed it
  the joint daily scenario set (E10 × B-MOM × B1, block-bootstrapped with the committed block=5
  convention, bar-level DD floors from MTM_RECONCILIATION), get the growth-vs-DD frontier and
  the sleeve weights at each risk budget. Report in MNQ units against the 16:44-flatten margin
  floor ($1k/contract intraday, $43.4k→ full margin overnight — already documented).
- **Expected sign**: n/a (frontier construction); prior from DR-E: MNQ at 0.25-0.4 Kelly is
  "pure arithmetic improvement" territory, full Kelly ≈ 1 NQ/$85k.
- **Data needed**: committed daily vectors; bar-level DD series for the DD constraint (exists).
- **EVI 4/5**: this is the required machinery for Track 7's deliverable; convex, deterministic,
  no data mining, no gate risk (no history is "tested" — a policy is computed).
- **Duplicate-check verdict**: **CLEAR.** Leverage DEPLOYMENT stays gated by thesis §21;
  "margin relief is not a license for leverage" (16:44 flatten record) is respected because the
  binding constraint here IS the Kelly/drawdown wall, not margin. Naive NQ-block scaling stays
  dead (all-MNQ linear scaling is the recorded correct K>1 form).

### C-5. Kelly under parameter uncertainty: Bayesian shrinkage of the growth-optimal fraction — EVI 3
- **Mechanism**: the Kelly fraction is hypersensitive to mean-estimate error; Bayesian/resampling
  treatments shrink the bet toward zero as posterior uncertainty grows (fractional Kelly emerges
  as the certainty-equivalent policy) (EXTERNAL PRIOR:
  [Bayesian Grossman-Zhou rule, SSRN 6942459](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6942459),
  [practical Kelly implementation](https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2020.577050/full)).
- **What it adds conditional on Solar**: the program's own history (DSR judgment-dominated,
  comparative tests all inconclusive) says mean estimates here carry wide posteriors. This idea
  produces the DEFENSIBLE c in "c × Kelly": posterior over (μ, Σ) of sleeve daily returns via
  block bootstrap → distribution of Kelly weights → certainty-equivalent fraction. Complements
  C-4 (which takes returns as given); together they bound the leverage recommendation from
  theory and from estimation risk.
- **Expected sign**: c well below 0.5; consistency check against the scalp-lab safe c = 0.15 and
  DR-E's 0.25-0.4 heuristic band.
- **Data needed**: committed daily vectors only.
- **EVI 3/5**: cheap, no gate risk; value is credibility of the leverage number, not new alpha.
- **Duplicate-check verdict**: **CLEAR.** Nothing adjacent was tested; deployment gating per §21
  unchanged.

### C-6. Hidden semi-Markov (explicit-duration) vol-state model with preregistered detection delay — the engineering-grade allocator state — EVI 3
- **Mechanism**: HSMMs replace the HMM's geometric dwell times with explicit duration
  distributions, materially improving volatility-clustering realism and transition timing;
  duration modeling is the difference between a regime tag that flickers and one an allocator
  can act on (EXTERNAL PRIOR: [duration/interval HMM](https://arxiv.org/pdf/1508.04928),
  [HMM intraday momentum with side information](https://arxiv.org/pdf/2006.08307),
  [regime-switching with momentum and mean-reversion](https://www.sciencedirect.com/science/article/pii/S0264999323000494)).
- **What it adds conditional on Solar**: the engineering upgrade of DR-SM-A-2 (same target: the
  B-MOM/B1 allocator, never Solar): (i) dwell-time posteriors give expected regime remaining-life
  — an allocator that knows "high-vol states last ~N sessions" sizes a regime-local sleeve
  rationally; (ii) filtered-state DETECTION DELAY is measurable on 2006-2021 and must be quoted
  in the spec (honest-lag discipline this file demands of every filter); (iii) run-length
  posterior doubles as a C-3 input.
- **Expected sign**: as A-2: gated B-MOM keeps most of its 2022+ P&L while cutting rho_full
  below 0.3 — that is the falsifiable claim.
- **Data needed**: daily features from 1-min 2006-2026; sleeve ledgers. Nothing new.
- **EVI 3/5**: higher build cost than A-2's plain HMM; run only if the plain-HMM pilot shows
  state-dependent sleeve P&L worth refining.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS** — identical constraint set to A-2
  (allocator-only, freeze state definition pre-2022, W8 anti-tuning clause for anything aimed at
  the rho gate).

### C-7. Vol-targeting at the PORTFOLIO layer — test honestly against the tail gate, expect partial failure — EVI 3
- **Mechanism**: scaling exposure by 1/σ̂ raises Sharpe for "risk assets" and cuts left-tail
  severity, but the effect is asset/strategy-dependent and near-zero for already-vol-managed
  futures books (EXTERNAL PRIOR:
  [Harvey-Hoyle-Korgaonkar-Rattray-Sargaison-van Hemert, The Impact of Volatility Targeting](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf),
  [Man Group summary](https://www.man.com/insights/the-impact-of-volatility-targeting),
  [conditional vol targeting](https://www.tandfonline.com/doi/full/10.1080/0015198X.2020.1790853)).
- **What it adds conditional on Solar**: local evidence is already adverse at the SIGNAL layer
  (ARM_C vol control: −29% net, 49.4% tail retention — failed the hard gate). The untested
  question is the PORTFOLIO layer: normalizing the COMBINED book (Solar + B-MOM + B1) to a
  ~constant forecast vol, where sleeve diversification changes the tail geometry. Honest prior:
  partial failure — right-tail clipping will appear here too; the experiment's value is the
  measured tradeoff curve (MAR/TUW improvement vs tail retention), which Track 7 needs to make
  the risk-normalization decision with numbers instead of ideology. Design must include the
  asymmetric variant (cap leverage in low-vol, never cut below 1× in high-vol) which the
  Harvey et al. mechanism (vol-targeting ≈ momentum overlay) suggests keeps most benefit with
  less tail damage.
- **Expected sign**: symmetric targeting: MAR ↑, tail retention < 100% (likely gate-fail);
  asymmetric (cap-only) variant: smaller MAR gain, tail-safe.
- **Data needed**: daily vectors + RV pipeline (exists).
- **EVI 3/5**: Track 7 cannot ship LEVERAGE_FRONTIER without this curve; cheap.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS.** ARM_C killed vol targeting as a
  Solar-signal-layer PROMOTION; the portfolio layer on a multi-sleeve book is a different object
  and RISK-01/P04 was always the designated (never-built) home. The tail gate applies in full;
  the cap-only variant is the pre-declared fallback.

### C-8. l1 trend filtering (online) as a piecewise-linear trend-age/kink detector — EVI 2
- **Mechanism**: Kim-Koh-Boyd l1 trend filtering yields piecewise-linear trends whose knots are
  sparse, interpretable trend-change points ([Kim-Koh-Boyd, l1 Trend Filtering, SIAM Review](https://web.stanford.edu/~boyd/papers/pdf/l1_trend_filter.pdf),
  [project page](https://stanford.edu/~boyd/papers/l1_trend_filter.html)). Streaming variants
  exist only as windowed re-solves; the endpoint estimate is unstable (last-segment slope changes
  as data arrives), which IS the honest-lag cost and must be measured, not assumed. EXTERNAL PRIOR.
- **What it adds conditional on Solar**: a second, non-Bayesian estimate of "current leg slope
  and age" for cross-validation of C-2's Kalman state; possible feature: agreement between l1
  last-segment slope sign and Solar position as an up-weight condition. Marginal over C-2.
- **Expected sign**: same direction as C-2; mostly redundant.
- **Data needed**: 3-min closes; windowed convex solves (cheap at this scale).
- **EVI 2/5**: fund only if C-2 shows signal and a robustness twin is wanted.
- **Duplicate-check verdict**: **CLEAR** (same constraints as C-2: no flip-rule contact, no
  suppression). Knot-triggered ENTRY logic would be new-engine territory requiring its own spec
  and is not proposed.

### C-9. SSA (singular spectrum analysis), causal variant, as a model-free trend/noise separator — EVI 2
- **Mechanism**: SSA decomposes a series into trend + oscillation + noise without a parametric
  model; causal/last-point variants exist but suffer well-documented endpoint distortion
  (EXTERNAL PRIOR: [Zhigljavsky SSA encyclopedia entry](https://ssa.cf.ac.uk/zhigljavsky/pdfs/SSA/SSA_encyclopedia.pdf),
  [Hassani-Thomakos review for economic/financial series](https://www.semanticscholar.org/paper/A-review-on-singular-spectrum-analysis-for-economic-Hassani-Thomakos/f88a7f1039a608981966c3863655277afb950c2d),
  [SSA trend extraction](https://arxiv.org/pdf/0804.3367)).
- **What it adds conditional on Solar**: third opinion in the trend-clarity family (C-2, C-8,
  A-4/A-7); the only distinctive contribution is its oscillation components — a causal estimate
  of "chop energy" (sum of mid-frequency component variance) as a NEGATIVE-quality state. But a
  chop DOWN-weight immediately meets the tail gate, so the admissible form is again alignment
  up-weighting only.
- **Expected sign**: as C-2.
- **Data needed**: 3-min closes.
- **EVI 2/5**: redundant with cheaper estimators; endpoint instability is a real cost.
- **Duplicate-check verdict**: **CLEAR-WITH-CONSTRAINTS** (chop-veto framing banned — SW05
  inversion; alignment up-weight only).

### C-10. CPPI-style drawdown floor on the PORTFOLIO equity curve — include for completeness, expect rejection — EVI 2
- **Mechanism**: CPPI scales risk exposure by a multiple of the cushion above a floor; known
  failure modes are gap risk (floor breach between rebalances) and cash-lock (permanent
  de-risking after drawdown) (EXTERNAL PRIOR:
  [AXA-IM CPPI/TIPP primer](https://core.axa-im.com/document/9914/view),
  [Gaspar-Sousa, "Design risk: the curse of CPPIs"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4595818),
  [CPPI with jumps](http://www.planchet.net/EXT/ISFA/1226.nsf/0/9034828ca6162f07c12577ae00246cb3/$FILE/cppi%20in%20presence%20of%20jumps%20in%20asset%20price.pdf)).
- **What it adds conditional on Solar**: an explicit alternative to C-4 for the drawdown
  objective. Honest prior: BAD here — equity-curve-reactive de-risking is structurally
  tail-adverse for a right-tail strategy (it cuts size after losses, i.e., often just before the
  tail days that pay for everything), and cash-lock is fatal for a system whose TUW is already
  1,120/1,184 sessions. Its value is as the documented STRAW MAN in LEVERAGE_FRONTIER: show the
  growth/DD frontier of C-4 dominates CPPI at every risk budget, so the owner never has to
  relitigate "why not a simple equity stop."
- **Expected sign**: dominated by C-4; cash-lock frequency material in block-bootstrap paths.
- **Data needed**: daily vectors.
- **EVI 2/5**: cheap; decision value is closing a perennial design argument with numbers.
- **Duplicate-check verdict**: **CLEAR as comparison arm.** Any LIVE use would collide with the
  right-tail gate and the equity-curve-suppression analogy to killed axes; pre-declared as a
  reference policy only.

### C-11. Particle-filter / regime-conditional slope with fat-tailed observation noise — EVI 1
- **Mechanism**: replacing Gaussian KF noise with Student-t / mixture observation models makes
  the slope estimate robust to the exact 8-sigma event days that dominate this book; sequential
  Monte Carlo handles the non-Gaussian posterior (EXTERNAL PRIOR — standard SMC literature; see
  the robust-KF thread in [distributionally robust Kalman filtering](https://arxiv.org/pdf/2302.05993)).
- **What it adds conditional on Solar**: robustness refinement of C-2 only. The Gaussian KF
  treats trend-day jumps as noise spikes and shrinks slope exactly when the tail is paying;
  a t-noise filter does not. This matters only if C-2 works but misbehaves on tail days —
  a diagnosable, second-generation fix.
- **Expected sign**: better tail-day behavior of the multiplier than C-2.
- **Data needed**: 3-min closes.
- **EVI 1/5**: premature until C-2 has a verdict.
- **Duplicate-check verdict**: **CLEAR** (inherits C-2 constraints).

---

## REJECTED-DUPLICATE — attractive DSP/control ideas filtered out, and why

1. **Optimal CUSUM reference value k = δ/2 on PRICES (Moustakides), drift-allowance variants,
   ARL-optimized flip thresholds** — the textbook "fix" for Solar's k=0 CUSUM, and the single
   most tempting idea in this domain. KILLED: DR03-H2 (C01-T0-3: retrace speed carries no
   next-trade information, p=0.35, rank-inverted) + T0-9 (500/500 surrogates reproduce r≈1.29)
   ⇒ threshold engineering closed AS A CLASS. C-3 uses the same mathematics on P&L streams for
   allocation — that is the only admissible descendant.
2. **Dixit hysteresis band optimization / F^(1/4) band scaling** (DR-03 theory) — same closure:
   it prescribes threshold geometry. Recorded as theory context only.
3. **Split exit/reverse thresholds from control theory (asymmetric switching costs ⇒ α/β
   bands)** — H-007/DR03-H1 falsified: "early exits amputate the right tail"; monotone
   degradation both directions. Its "dependents" (cost-elasticity, side-asymmetric bands) were
   pre-banned in C01 §0.
4. **Resting stop/limit orders at filter-implied levels** (execution control) — H-011: negative
   10/10 cells (−$1.88M); close-basis crossing excess (89% of friction) is NOT recoverable.
   Patient/passive execution also failed on own tick data (W8-3 Arms A and B).
5. **Timed exits / optimal stopping of the session hold** — 16:30 timed-exit dominance FALSE;
   16:45-17:00 window axis closed (flatten adopted); any exit-time change is a new-population
   experiment by rule and carries no open hypothesis.
6. **ML/probabilistic episode gating (meta-labeling, classifier-driven bet sizing)** —
   C01T1_ML closed for suppression-style monetization; every probability-ranked cut was
   tail-adverse. C-1 is the sanctioned non-suppression descendant.
7. **Vol-surprise (HAR-residual) exposure states** — C01T1_EXPOSURE rejected; revival requires a
   post-2024 mechanism (0DTE candidate) with a NEW spec — that is a mechanism-research task, not
   a filter re-run, and it is not proposed here.
8. **Kalman/filter-based REPLACEMENT of the Solar engine (filter crossover entries, smoother
   stop-and-reverse)** — Solar parameter optimization is CLOSED and new Solar-family mining is
   banned; C-2/C-8/C-9 exist strictly as overlays above the frozen engine.
9. **Member reweighting by trailing performance (inverse-vol / trailing-Sharpe weights on the 13
   members)** — H-013 recorded not-run/superseded: no comparative claim is separable from noise
   on 4.6y; strict 1/N stands on complexity grounds. C-3's sleeve-level decay detection at the
   PORTFOLIO layer is the admissible cousin.
10. **Equity-curve trading stops ("turn the system off after X% drawdown")** — suppression of the
    whole book; structurally identical to CPPI cash-lock (C-10's documented failure mode) and
    presumptively tail-adverse; only the C-10 comparison arm is allowed to quantify this, never a
    live rule proposal.
