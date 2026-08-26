# WEEKLY_EDGE — PRINCIPLES (原理存档, kept current; started 2026-08-25)

Owner asked that the principles be saved for later research ("记得保存原理"). This file is the
mechanism record: WHAT each component is, WHY it should make money, and WHAT the evidence
says. Every claim carries its run. Corrections are appended, never erased.

## 0. What we did NOT build

**VWAP Flux was NOT reconstructed.** Two different things exist and must not be conflated:
- the clean-room VF *geometry approximation* (campaign #6) — fit to reproduce the trader's
  2026 weekly stats; as a money system it is DOES_NOT_EXIST at stress frictions (W01);
- the **delta proxy** — one documented INPUT CONCEPT from the VF manual (the
  `UpDownTick_RealVolume` volume-classification mode) implemented at 1-min bar granularity
  (signed volume by close direction, session-anchored cumsum). A concept, not the product.
  The vendor's Fair Value engine and `Signal_Trade` trigger remain purchasable only.

## 1. Architecture (first principles)

```
information engines (state machines)          risk & exposure           composition
────────────────────────────────────          ───────────────           ───────────
S1  Solar T1 flip + D-gate (2023-derived)     session-level $ halt      integer weights
S4  Solar13 ensemble + tilt + hysteresis      (h1300/h2600)             over weekly-
S5  B-MOM RTH breakout (decayed)              context gates (lagged):   independent
CD  cum-delta transition (marginal)             flow-side (delta),      sleeves
MO  osc-overlap reversal (dead)                 value-side (FV)
```
Money = engine expectancy × risk truncation × diversification across ENGINES (never across
exits of the same entries — W01 P4).

## 2. Mechanisms and their evidence (post W03-amendment-1, all lag-correct)

| mechanism | why it should work | measured |
|---|---|---|
| **Session-level $ halt** | our losses accumulate intra-week/intra-session (W02 measured: tail ≠ single trades) → truncate the accumulation process, not the trade | the ONLY mechanism that puts a config under −$15k worst week while keeping ≥55 % pos (W03: S4.all13.h1300.gdl, −$12,915) |
| **Delta context gate** | trade only with the session's realized flow direction; flow leads price at 1-min | **+0.02–0.03 Sharpe** portfolio marginal, real but modest (the 0.355 version was look-ahead, VOID) |
| **Hysteresis (3,1)** | entry conviction ≠ exit conviction; asymmetric bands suppress churn | +0.03–0.04 Sharpe, +$12.8/trade vs no-hysteresis (W04) |
| **HTF tilt (50-session)** | trade bigger with the higher-timeframe wind | +0.03 Sharpe, +$12.0/trade vs no-tilt (W04) |
| **D-gate (S1)** | stop trading after the session turns hostile | +$42k over the master window, −646 trades (r13 archive) |
| Ensemble averaging | diversify threshold noise | weak alone (0.028 Solar-only vs best atom 0.106) — averaging is NOT where expectancy comes from (W04) |
| Bolt-on skew exits | "let winners run" | **FALSIFIED** on our entries (W01 F2: every variant destroys $/trade) |
| Per-trade $ caps | his −$2,600 unit | **inert on our sleeves** (W02: 142/13,301 trades touched) — risk units do not transplant across architectures |
| Weekly loss limit | truncate bad weeks | regime-dependent; locks in losses, kills hit rate on dev (W01) |

## 3. The money, explained (as far as it is)

Honest 4.4-year frozen capability (net, stress-surviving): **~57–62 % positive weeks,
$1.2–2.7k/wk per 1–2 contracts, worst week −$13k…−$27k** depending on where you sit on the
tail-vs-mean frontier. Per-trade expectancy of the bar-clearing config **$110.5 > his $103**.
The remaining gap to "比他多比他稳" is the LEFT TAIL of portfolios (halts fix members, not
yet combinations) and the fact that no candidate has passed an untouched out-of-sample test —
the 9-week holdout is exhausted (4 reads) and June–July 2026 was a favourable regime.

## 4. Standing epistemic rules (each bought with a real mistake)

1. Gates/masks carry **decision-bar information only** (W03 am.1: close-at-open look-ahead).
2. **Explainability review before any freeze** — asking "where does the money come from"
   caught the look-ahead.
3. Never quote dev-sorted holdout rows as expectations (R34; W03 §multiplicity).
4. Session-flat conventions, $4.36/RT base, C1 stress line on everything.
5. Corrections propagate to every citing document, with the original preserved.

## 5. Open questions for the next researcher (possibly us, later)

- Can the halt be made regime-aware without becoming a fitted parameter?
- Does true tick delta (48-session substrate) agree with the 1-min proxy where they overlap?
  If yes, the proxy is validated backward; if no, the gate's real value may be higher.
- Would the official VF `Signal_Trend/Signal_Cum_Delta` (if purchased) beat the proxy gate?
- Portfolio-level tail: same-direction concentration cap (never yet implemented cleanly).

---

## 6. MAJOR REVISION 2026-08-25 (waves W17-W20) — what we actually own

Three results forced a rewrite of everything above:

**W17 deep history.** The frozen stack run on 2006-2021 (sixteen untouched years) is
**pooled Sharpe -0.001, 9/16 positive years**. The 2022-2026 numbers do not replicate. The
price-scale alibi fails: 2021, at modern levels and adjacent to the calibration sample, is the
worst year. Owner accepted a regime-conditional stance (only the current regime matters), which
is legitimate for a non-stationary market -- but it moves the burden: the supporting regime is
~4.5 years old and our calibration consumed all of it.

**W19 walk-forward.** Refitting quarterly on a trailing year and trading only the next quarter
gives **Sharpe 0.171 vs the fixed-calibration 0.249 and naive 0.150**. Verdict WEAK: the fixed
numbers overstate by ~30 %, and quarterly selection buys +0.021 over doing nothing.
**14 distinct configs across 17 refits (88 % churn) -- selection is noise.**

**W20 ensemble.** The correct response to selection noise is aggregation.
**E5 = a one-contract majority vote across the 32 LONG-ONLY configurations** gives Sharpe
**0.214**, beats walk-forward (0.171) and naive (0.150), worst week **-$17,440** against
naive's -$37,318 on less than half the trades, and is **positive in every year**
(0.260/0.271/0.307/0.113/0.315). It performs **no runtime parameter selection**, so it is
structurally immune to the W19 failure.

### The single most replicated finding: LONG-ONLY
Favoured independently by W16 (side split: 0.229 vs 0.210, worst -$15.1k vs -$24.4k),
W17 (the ONLY finding to replicate on 2006-2021: +0.072 vs -0.008), W19 (BESTFIXED is
long-only, worst week -$14,543) and W20 (E5 0.214 > E4 0.200). Shorts earn ~1/3 the per-trade
rate of longs on every sleeve measured.

### Corrected honest description
A **selection-free, long-only, volatility-regime-throttled trend harvester on NQ**. It earns
in active-range sessions (16.8 % of sessions carry ~all P&L), stands aside in quiet ones
(three independent attempts to trade the quiet regime failed: W11, W18 build, W18 modern),
and is NQ-specific (the same engine loses on ES/RTY/YM). Out-of-sample within the regime it
is worth roughly **Sharpe 0.21, ~$1,100/week per contract, 59-60 % positive weeks, worst week
about -$17k** -- not the 0.28/$3,400 that fixed calibration advertised.

## W38 — two narrowings of existing claims (both bought with measurement, 2026-08-25)

**1. "Sizing on new information is edge" is narrowed to "the score grades LONG flips."**
The identical construction on short entries behaves like leverage: +27 % production for +51 %
worst week, efficiency 0.079 -> 0.066 on EVAL after rising in-sample. The law is not repealed
on the long side (W34/W37 nulls stand); its DOMAIN is now measured rather than assumed.

**2. "Shorts are insurance" is WITHDRAWN as a description.** At matched exposure the short
sleeve widens the tail (efficiency 0.348 -> 0.220) and lowers the daily positive rate; what it
actually buys is +4.4 pp of weekly positive rate. Long and short drawdowns CO-OCCUR. Running
the long object at 2 contracts dominates long+short at 1+1 on production, tail, CVaR, Sharpe
and daily hit rate simultaneously; only the weekly positive rate favours the pair.
Consequence: the short sleeve moves to the CONSISTENCY corner of the Pareto frontier and is
priced there, instead of being described as risk reduction.

**3. An hour-of-day P&L pattern is not an hour effect until it survives a shift null.**
The short side's negative hours (06/10/15/18/20/21 ET) looked like a clean, mechanistic
restriction and produced +1.76 pts/session; arbitrary shifted schedules did the same
(65th percentile, p = 0.350). Exposure reduction masquerades as selection.

## W39 — what the quality layer actually is, and why more features do not help (2026-08-25)

**1. The layer is NOT leverage, and it is not just the rule's shape.** It had only ever faced
circular-shift nulls. Two count-matched controls, 100 draws each, full window:

| | pts/session | eff | Sharpe |
|---|---|---|---|
| base, all size 1 | 10.62 | 0.142 | 0.305 |
| C1 null - a RANDOM 20 % sized up | 12.03 | 0.141 | 0.279 |
| C2 null - five RANDOM features, identical rule | 12.62 | 0.152 | 0.284 |
| the real layer | **14.72** | **0.198** | 0.311 |
| percentile vs C1 / C2 | 97.0 / 95.0 | **100.0 / 97.0** | 94 / 90 (weak) |

Reading: pure exposure explains 12.03; the rule's SHAPE with arbitrary features adds only
0.6 more; the SPECIFIC five add the remaining 2.1. **The features carry most of the gain.**
Residual caveat (`WEAK`): those five were selected on the full window in W33, so part of the
97th-percentile margin is that selection. What is independent of it: W36's walk-forward kept
the same five and refit only thresholds, reaching 14.41.

**2. Feature information is unstable, so feature CHOICE must be fixed, not re-chosen.**
Quarterly re-selection churns 62 % (top-5) and 80 % (t >= 2 admission, which admits ZERO
features in 2 of 12 quarters), and every re-selection scheme loses to the fixed five
(eff 0.163 and 0.138 vs 0.229). My own hypothesis - that the churn was an artifact of forcing
a rank-5 pick among near-ties - was refuted by the threshold arm churning worse.

**3. Aggregation is scoped, not universal.** W20 aggregated 32 configs and won; W39 aggregated
42 features and lost (eff 0.180 vs 0.229). The distinction:
> aggregation helps when the members are noisy estimates of the SAME quantity, and hurts when
> they are candidates for DIFFERENT quantities, because the informative few get diluted.

**4. A fourth confirmation of the leverage law in a new form**: continuous size (cap 3) is the
highest-production arm ever measured here (21.44 pts/session) at avg 2.00 contracts, with
eff 0.201 against the incumbent's 0.229 at 1.19. Size RESOLUTION buys exposure, not edge.

**5. N1 and N2 are not interchangeable.** The short continuous arm passed the circular-shift
null at the 100th percentile and FAILED count-matched random sizing at the 69th. For any
SIZING rule the count-matched control is the binding one; alignment nulls cannot separate
"sized the right trades" from "sized some trades". Every sizing claim from now on reports both.

**6. Two method corrections.** A worst-week gate expressed in absolute dollars is
exposure-naive and will reject arms that beat their reference at matched exposure; eff and
CVaR efficiency are the criteria and the absolute worst week is reported, not gated. Exposure
matching is time-weighted (contract-minutes), not trade-count-weighted.

## W40 — the second-model search, and a third full-sample-quantile casualty (2026-08-25)

**1. Four non-ratchet mechanisms, no adoption.** Fade-as-an-EVENT (-11.4 pts/session),
sweep-and-reclaim (-3.08), a complement-set ridge over the 83 % of bars where Solar is flat
(stress-net -$55/wk despite 2.7 % overlap), and a volatility-expansion event sleeve. The
complement-set result is the substantive one: those bars are POOR, not merely unexploited.

**2. What axis B does establish (`SUPPORTED`)**: a non-Solar engine that is positive after
frictions AND decoupled inside our drawdowns EXISTS - corr +0.01 overall, **-0.25 inside the
long object's worst-decile weeks**, 5.7 % bar overlap. W25/W27's orthogonal engines all lost
money; this one does not. It is parked for failing the binding count-matched null (92nd, needs
95th) and for a per-year record of 2 poor years in 4, not for being fake.

**3. THIRD full-sample-quantile casualty, and this one had already produced a promotion.**
B's regime dependence looked decisive: the high-volatility band was stress-net positive in BOTH
modern halves (+$12,015 and +$75,665) while the low band was negative in both - the
preregistered promotion condition, met. The band was cut at the FULL-SAMPLE median. Re-cut at
the TRAILING-250-session median, B-gated gets WORSE than B-ungated ($200/wk vs $323/wk, weekly
positive rate 32 % vs 53.7 %). After W03's gate and W37's score thresholds this is now a
standing rule:
> ANY threshold or quantile cut on the measurement sample must be re-derived causally before
> it can support a conclusion - including thresholds that only appear in a DIAGNOSTIC.

**4. An arbitrary allocation is not a diversification verdict.** W40's first read paired each
axis with the long object at ONE CONTRACT EACH, silently handing a sleeve of efficiency 0.065
a 34 % share of a book whose main sleeve runs at 0.229, and read that as a failure to
diversify. Diversification questions must scan WEIGHT at CONSTANT TOTAL EXPOSURE, measured in
time-weighted contract-minutes.

**5. Full-window and per-year re-measurement is now a precondition for any adoption.** B
cleared all five preregistered conditions on 2023-07 -> 2026-08 - a window chosen in W39 for a
different comparison - and the adoption was withdrawn on the full-window read. A window chosen
for one purpose will flatter something else.

## W42 — the payoff's own shape, and why exits cannot be engineered here (2026-08-25)

**1. What we actually own (`FACT`, measured for the first time).** 37.8 % of trades win; the
median trade gives back MORE than its entire MFE (1.384); winners keep only 41.4 % of theirs.
It is a LOW-HIT-RATE, HIGH-PAYOFF object whose winners pay for everything else.

**2. The quality score forecasts EXCURSION SIZE, not hit rate.** Win rate is flat at 35-40 %
across every score; MFE goes 1.30-1.51 ATR at score 0-1 to 3.10-5.45 ATR at score 3-4, at
similar MAE. That is the mechanism behind sizing, and it explains why FILTERING on the score
destroyed production (W34) while SIZING on it works: the score is not finding likelier winners,
it is finding bigger ones.

**3. Early adversity predicts failure and it is decided by BAR 5.** P(win | MAE <= -1 ATR by
bar 5) = 24.0 % against 37.8 % unconditional, monotone in the threshold and FLAT in the horizon.
Knowing this is not the same as being able to trade it - see 4.

**4. Stops are structurally incompatible with this payoff, and phase 1 predicts it.** WINNERS'
median MAE is 0.86 ATR: the trades that eventually work routinely go a full ATR against us
first. Any stop at the level winners endure cuts the winners, and the winners are the whole
P&L. Causally implemented: MAE stop 6.03 pts/session (eff 0.080), give-back stop 2.38
(eff 0.024), partial 10.96 (0.146), high-score-only stops 7.66 (0.139) - all against the
incumbent's 14.72 / 0.198. The exits are not badly tuned; they are the wrong instrument.

**5. The largest look-ahead the campaign has found.** Updating MAE/MFE with bar i's own high
and low and exiting at bar i's open turned 6.03 pts/session into 18.08 and Sharpe 0.179 into
0.465 - the campaign's highest-ever number, entirely artificial. Standing addition:
> a stop or trailing rule must be a RESTING ORDER at a level known before the bar trades, and
> every stop arm must be reported beside its RE-ENTRY-ALLOWED control - without that control a
> "stop" can silently be nothing but a one-bar skip.

**6. The incumbent 23-bar cut is now null-tested** against randomised stop distances:
100th percentile, p = 0.000.

## W41 — W32 overturned, and the first adopted diversification (2026-08-25)

**1. A defective harness produced a wrong verdict, and the disclosure was right to suspect it.**
W32's re-implemented ratchet scored 3.84 (3-min) vs 4.85 (1-min) and closed the clock axis
provisionally. The SHIPPED engine on aggregated bars scores 9.40 vs 10.62, and per-trade
economics reverse: $170.8 (3-min) and $236.5 (range) against $103.9 (1-min). B1c - the clock
harness at k=1 reproducing the incumbent vote BAR FOR BAR - is the check that made this
testable.

**2. A different clock is a different EVENT GENERATOR (`INFERENCE`, derived from W31).**
Because the edge lives in the flip EVENT and not the trend state, changing the sampling changes
WHICH events exist rather than smoothing the same ones. Measured consequence: weekly P&L
correlation with the long object of 0.32-0.48 (the 1-min base object is 0.89) and 0.02-0.33
inside its worst-decile weeks. All four clocks clear BOTH nulls at the 100th percentile and
every one is positive and stress-positive in EVERY year.

**3. SAMPLING diversification is not MODEL diversification.** Every clock is the same Solar
ratchet. The basket lowers the tail; it does not reduce the risk that the ratchet itself decays.
Nothing in W41 changes the model-concentration prior.

**4. Adopted, and honest about how much.** `w = 0.03 each: long + 3-min + range` improves eff
0.198 -> 0.209, CVaR-eff 0.272 -> 0.282, Sharpe 0.311 -> 0.318 and the worst week -$7,418 ->
-$6,968, for 0.7 % less money, and beats matched long-alone on eff in 4 of 5 years. Its binding
count-matched null is the 95.0th percentile, p = 0.050 - it clears the bar by nothing at all.

**5. CONTINUOUS WEIGHTS ARE NOT ORDERS - a new standing check.** w = 0.03 is 0.04 contracts;
the clock sleeve only rounds to one contract when the base sleeve runs at ~22-25x. Converted to
integer ratios: >= 16 : 1 : 1 (about $25,000/week) improves both metrics; 4 : 1 : 1 to
12 : 1 : 1 improves Sharpe and CVaR-efficiency but WORSENS eff and the single worst week (the
clocks remove many moderately bad weeks and add a few very bad ones); below 4 : 1 : 1 there is
no benefit. Every portfolio adoption from now on reports its smallest tradeable integer form.

## W44 — the independent check the campaign had never run (2026-08-26)

**1. Every B1 check since W01 validated new code AGAINST the port, never the port.** NinjaTrader
can run the original C# through its own Strategy Analyzer engine. It had never been done.

**2. The data was proven identical first**, so any difference is logic: NT8's NQ 06-26 prices
differ from our back-adjusted parquet by a CONSTANT -282.25 points, standard deviation 0.00,
and every quantity in the ratchet is a price DIFFERENCE.

**3. The shipped C# runs its decision stack on a 3-MINUTE secondary series**
(`AddDataSeries(..., BarsPeriodType.Minute, 3)`; `if (BarsInProgress != 1) return;`) and uses
the primary series only for execution. `sm14_1m` runs it on 1-MINUTE bars - a declared W01 port
choice whose magnitude was never measured: **285 flips against the C#'s 92, i.e. 3.1x as active**.

**4. On the correct clock the ratchet is FAITHFUL.** 3-minute port vs C#: direction agreement
**99.3 %** whenever both hold a position. The threshold, tilt, combiner and hysteresis are
transcribed correctly, and sigma counted in BARS (460) beats the wall-clock equivalent (153),
resolving a W01 ambiguity in favour of what the code does.

**5. What is NOT faithful is EXPOSURE MANAGEMENT**: in market 36 % vs 52 %, 140 flips vs 92,
even on the right clock. The residual is WHEN to hold, not WHICH WAY - most likely the port's
session-close flatten and its inability to re-enter without a fresh flip.

**6. Quantifier correction, binding on every document.** The object is NOT "our shipped product
ported to 1-minute bars". It is **a Solar-family ratchet transcribed from the product and run on
a 3x finer clock**. The research RESULTS stand unchanged - they measure a well-defined object
with causal construction, both nulls, walk-forwards and per-year re-measurement, none of which
assumed replica fidelity. Deployment, however, must implement the PYTHON object and validate
against it; running the existing C# would trade a materially different system.

**7. It closes a loop with W41.** W41 found, from the data side and before this check, that a
3-minute clock is a genuinely different event generator (correlation 0.48 with the 1-minute
version, 0.12 inside its worst-decile weeks) and worth owning in the portfolio. That clock is
the product's own. The campaign rediscovered the product's clock without knowing it.

## W43 — "NQ-specific" is now supported rather than assumed (2026-08-26)

**1. W11 did not test what it claimed.** Its clamp is [40, 1200] TICKS, which is [3.07, 92.22]
x sigma on NQ (never binds, since VolMults are 6-16 sigma) but [13.9, 416] on ES, [8.9, 266] on
RTY and [7.8, 233] on YM - the LOWER bound collapses VolMult 6, 8 and 10 onto a single
threshold. W11 ran a 3-to-4-member engine on the other instruments, not the 6-member one.

**2. Re-derived properly, it still does not travel.** Clamp as the same multiple of each
instrument's own sigma, box as the same fraction of its own median session dollar range: the
tail improves markedly (ES worst week -$13,139 -> -$5,243, eff 0.019 -> 0.036) and the sleeves
still fail frictions - ES +$92/wk stress-net on 2,008 trades, RTY -$87, YM -$9. The claim
"the edge is NQ-specific" is now SUPPORTED instead of being an artifact.

**3. DECOUPLING IS NECESSARY AND NOT SUFFICIENT - the cleanest example the campaign has.**
RTY and YM correlate 0.10 with NQ overall and **0.04 and 0.03 inside NQ's worst-decile weeks**,
better decoupling than any other sleeve ever measured here (axis B -0.25, the clocks 0.12-0.33).
The equal-risk basket still loses badly: eff 0.095 against NQ alone at the same total weekly
sigma at 0.188. A sleeve with no expectancy cannot help however uncorrelated it is.

**4. A built-in identity check earned its keep.** Read 1's NQ arm gave $1,529/wk against the
incumbent's $1,470 and the run was VOID. The re-derivation arithmetic was right; the fill layer
conflated direction and size, so a bar where the vote had just turned off suppressed an entry.
The identity is now a HARD GATE that aborts the run. Design every cross-context wave so that
one of its arms MUST reproduce a known result exactly.
