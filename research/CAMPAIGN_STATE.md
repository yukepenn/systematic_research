# Campaign State

_Last updated: 2026-08-07 (Solar Wave RK **fully** recovered; ensemble promoted over parameter
selection; H-006 downgraded to INCONCLUSIVE and all DSR figures withdrawn after independent
red-team review - see section 8)_

## 1. Vendor independence — COMPLETE (RE01 + RE02)

The RenkoKings Solar Wave RK indicator is **fully reverse-engineered**. Every published series,
every signal symbol, exact on every bar:

**1,436,860 bars · 9 parameter configurations · zero mismatches on any series.**
Type 2 specifically: 45,825 events, 0 false positives, 0 false negatives.

Reference implementation `solar_wave_full()` in `src/analytics/solarwave.py`; derivation in
`research/03_reverse_engineering/{SOLARWAVE_MATH.md, TYPE2_RECOVERY_SPEC.md,
TYPE2_RECOVERY_REPORT.md}`. Method: behavioural observation of the indicator's own published
output. **No decryption, unpacking, patching or memory dumping was performed; the vendor assembly
was not modified or redistributed** (constitution: never bypass vendor protections).

Recovered model in one place:
- **Core:** one state variable `a` = running extreme of the CLOSE since trend start.
  `TrailingStop = a ∓ S`, `TrendVector = a ∓ V`. Flip on a **strict** break of the stop.
- **Wave layer:** pure bar counter. `SlowdownScan` bars of no new extreme ⇒ weak; a new extreme
  while weak increments the wave and emits Type 3; `WeakWeakSplit` is anti-chatter re-arm.
- **Type 2:** an edge-triggered latch on an **intrabar High/Low** excursion beyond `TrendVector`,
  spaced by `PullbackSplit`, re-armed by a full-bar clear, by a flip, and — the only coupling to
  the wave layer — by a Type-3 event. `PullbackEarly` switches the basis from the excursion
  (High/Low) to close-confirmed return. Touching `TrendVector` is not a cross (sticky latch).
- **New:** `TrendVector` carries a second ladder-rung clamp that is **provably inert when
  `V ≤ S/2`** — exactly where the vendor's own presets sit (90/179 = 0.503, 60/120 = 0.500).
  `V > S/2` is a characterised ambiguity, excluded from all experiments.

`SolarWaveOpenV1` (no vendor reference) reproduces the frozen canonical baseline exactly
(`runs/RE01_open_parity/`). `SolarWaveOpenX2` adds a fill-level ledger; `SolarWaveOpenV3` adds the
three new axes. All gate-checked against the baseline to the penny before use.

## 2. Current phase

**WAVE 2 — open-model axes.** Historical research only (no live-sim / paper / forward monitoring
ever, unless explicitly requested). Research universe = all data 2022-01 → 2026-07-31; no clean
OOS remains and none is claimed.

## 3. The central result: the deliverable is a region, not a parameter

CSCV over 16 chronological blocks (12,870 splits, 1,318 trading days): **PBO 0.56–0.66** with a
**negative** in-sample→out-of-sample slope (−1.03, r = −0.79). Walk-forward argmax selection earns
**$16,131 on 1-minute where the median config earns $121,373**. StopMultiplier is **not
selectable** from in-sample performance.

What works instead - hold the whole connected profitable range at equal risk, **without choosing
its boundary**. The red team showed the original 8-cell "plateau" boundary was itself an in-sample
selection, so the honest reference is every fixed cell actually tested. All figures are all-days
Sharpe on the 1,370-session union calendar, produced by `src/analytics/ensembles.py`:

| | **R4: fixed, ALL 21 cells** | 8-cell plateau (as originally published) | best single (unknowable ex ante) |
|---|---|---|---|
| net | $159,424 | $180,479 | $249,934 |
| daily Sharpe | **+0.910** | +0.788 | +0.947 |
| max drawdown | **-$35,669** | -$53,689 | -$71,395 |
| worst year | +$2,583 | +$7,796 | - |
| positive in all 5 years | **yes** | yes | - |

The full-range ensemble beats the hand-drawn plateau on both Sharpe and drawdown - which is what
one expects if the boundary added only selection. Both are positive every year when only 3 of the
8 plateau members are, and neither is an exposure artifact (gross exposure ratio 1.000).

**The absolute edge is statistically real:** circular block bootstrap P(Sharpe <= 0) = 0.0066 for
R4-21, 0.0147 for the 8-cell version, 0.0032 for the adaptive family. What is *not* established is
any comparative ranking between families - see section 8.

(The DSR figure and the "$216,922 exposure-matched" figure originally quoted here are both
**withdrawn** - see section 8. The latter came from a daily-tilt convention; a minute-level
reconstruction puts it near $188k, and it should never have been presented as achievable dollars.)

## 4. Frozen baseline (unchanged)
SolarWaveRKReplicaV0 · T1 · 90/179/5/10/true/10 · 1m Last · NQU6 · Lifetime · canonical window.
slip0 $146,440.60 / 2,915 trades / DD −$22,066.60 / PF 1.132213. Reproduced exactly by
`SolarWaveOpenV1`, `SolarWaveOpenX2` and `SolarWaveOpenV3` at their default settings — that
three-way gate is run before any new axis result is read.

## 5. Completed

- **PARITY, SW00, SW01, SW01b, SW01c, SW02a** — as before (see git history).
- **RE01** — open reconstruction reproduces the vendor baseline, all deltas zero.
- **RE02** — Type 2 and the full indicator recovered exactly (§1).
- **Wave 1 / 1b** — Type-1 core collapses to `f(StopMultiplier, timeframe, exit)`; profitable
  plateau 1m [170,280], 3m [180,260]; 3-minute is the stronger timeframe.
- **Wave 1c** — 80 configs, real slip 0/1/2, full history; PBO/CSCV, DSR/PSR, walk-forward,
  block bootstrap (`research/02_solar_refinements/WAVE1C_report.md`).
- **DR-01…DR-07** — seven deep-research packets, 32 falsifiable hypotheses
  (`research/deep_research/`).
- **DC01/DC02** — directional-change decomposition (`research/deep_research/DC01_DC02_RESULTS.md`).

## 6. Falsified this wave (each with evidence, none deleted)

| claim | verdict | evidence |
|---|---|---|
| 16:30 timed exit dominates the session close | **FALSE** on full history | wins 4/28 matched pairs, median −$12,476. SW02a's collapse test still stands; only its bonus finding is withdrawn |
| the 46 % untaken Type-1 signals are an opportunity set (SW03 premise) | **FALSE** | taking them costs **−$9.04/marginal trade** over 54,151 trades |
| H-011: stop orders at the ladder level recover the 89 % friction | **FALSE** | negative in 10/10 cells; close-based state and intrabar fills desynchronise |
| H-007 / DR03-H1: splitting exit from reversal distance helps | **FALSE** | monotone degradation as the split widens; ratio 1.00 (no split) is best at every point |
| DR06-H5: iid shuffling understates tail risk | **FALSE** | block-vs-iid 5th-percentile drawdown ratio 0.987 |
| SW05 original chop veto | **INVERTED** (earlier wave) | would delete 74 % of profit |

## 7. Confirmed this wave

- **DR06-H4** — neighbourhood-smoothed selection dominates argmax on both timeframes.
- **DC01** — the overshoot ratio `r = E[ω]/δ` exceeds the martingale null at every threshold
  (t = 31 → 2.1). The edge is real but is a **~3 % deviation of r from 1.0**, i.e. thin by
  construction.
- **DC01 cost structure** — the close-basis crossing excess is ~23.5 ticks = **$117.57 per
  segment = 89 % of all friction**, four times commission plus 1-tick slippage combined.
- **DC02** — volatility normalisation halves the across-year drift of `r` (0.116 → 0.058);
  price normalisation is intermediate (0.085). **Red-team caveat:** the "2025" cell is January 2025
  only (the canonical ledger ends 2025-01-31); recomputed the ordering narrows to 0.118/0.099/0.079,
  so vol-normalisation still leads but its margin over *price*-normalisation is small. H-014 is the
  decisive control.

## 8. Wave 2 verdicts, after independent red-team review

Full detail: `research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md`. Four independent reviewers; every
severe claim re-verified by the controller with its own code.

| hypothesis | verdict |
|---|---|
| **H-006** adaptive threshold `S = k*sigma` | **INCONCLUSIVE** (downgraded from PASS) |
| **H-007** split exit != reversal | **FAILED** - monotone at both reversal distances |
| **H-008** raw High/Low anchor | **FAILED** - Sharpe 0.527, the ladder chases wicks |
| **H-008** close-confirmed High/Low anchor | PASS standalone, **redundant** with H-006 |
| **H-011** stop-order execution | **FAILED** - negative in 10/10 cells |
| **H-012** sigma-estimator robustness | **PASS** - every lag >= ~1 session works |

**Why H-006 was downgraded.** The fixed family had been scored as two separate half-range
ensembles while the adaptive family got its full sweep. Scored fairly, the **full 21-cell fixed
family reaches Sharpe 0.917**, and the adaptive advantage falls from +0.210 to **+0.087** with a
paired block-bootstrap **P(delta <= 0) = 0.358**. Excluding 2025 alone leaves +0.046. The entire
effect sits in one calendar year, and adaptive *underperforms* fixed in the low-volatility tercile
- the opposite of its claimed mechanism.

**All DSR figures published in Wave 1c and Wave 2 are WITHDRAWN.** They paired `n_trials = 255`
with a variance estimated only from surviving cells (std 0.216 against an honest 0.40-0.50). Under
an honest pool the adaptive ensemble's DSR at N = 255 is 0.16-0.38, and it fails a Harvey-Liu
haircut at N = 1000 outright. A clusters-as-trials rule (effective N ~ 7, mean pairwise rho 0.295)
would give ~0.85 and is defensible - **but it must be preregistered and applied campaign-wide
before any number computed under it is used.**

**Two risk disclosures the reports had not made.** (a) The **top 1% of trades contribute 160%
(adaptive) / 248% (fixed) of net P&L** - the bottom 99% lose money in aggregate, and removing the
top 10 days takes the adaptive ensemble from $198,059 to $71,923. Every future filter or veto must
be checked for right-tail retention first. (b) The **short side has no standalone edge**: excluding
2022 and 2025 it is net negative (-$8,397, Sharpe -0.113). The long side carries the system.

**Conventions fixed going forward:** Sharpe is computed on **all days**, not ensemble-active days;
the cross-family calendar is the **union** (1,348 sessions), not the archived 1,285-day matrix.

## 9. Wave 3 verdicts — the frontier is closed

Full detail: `research/07_h014_price/WAVE3_report.md`; decision package:
`reports/final_system_design.md`.

| hypothesis | verdict |
|---|---|
| **H-014** volatility vs price normalisation | **PASS** — vol beats price by +0.728 Sharpe, **p = 0.009**; the mechanism is volatility-specific, not generic time-variation. The campaign's first clean significance result |
| **ES portability** | **FAIL** — blind transfer loses money (ES ensemble Sharpe −0.329). Shape travels (Spearman 0.780), level does not. Constitution §16 overfitting penalty applied |
| **C2** Type-1 + one Type-3 re-entry | **FAIL** — looked strong on a fixed core (+29 % net, smaller DD), then cost **0.40 Sharpe** on the adaptive core (P = 0.879) and broke the every-year-positive property. A sleeve whose sign flips with the core is an interaction, not an effect |
| **C4** adding Type-2 | **FAIL** — −0.33 Sharpe |
| **wave-index conditioning** | **FAIL** — non-monotone, 0.54–0.93 across MinWave 1–8. The wave counter describes structure but is not an edge |
| **DSR as a promotion criterion** | **ABANDONED** — under the preregistered rule every candidate scores 0.45–0.55 against a 0.90 bar with a Harvey–Liu haircut Sharpe of 0.000; a defensible alternative variance pool gives 0.96. The answer is dominated by a judgement call, not the data |

**Every sleeve and conditioning axis is now closed. R5 — the volatility-normalised ensemble,
Type-1 signals only — stands alone and unimproved.** That is a cleaner outcome than a stack of
marginal enhancements would have been, and it is consistent with the campaign's dominant finding:
on 4.6 years of one instrument almost nothing is separable from noise, and the additions that look
helpful are the ones most likely to be fitting the specific core they were tested against.

## 9b. Stop condition reached

Constitution §23(B): three consecutive properly designed research waves failed to produce a new
robust Pareto improvement (Wave 2's H-006 downgraded to inconclusive; Wave 3's sleeves and
conditioning all rejected; the red team's own follow-ups all negative), and the remaining frontier
is **data-limited rather than method-limited**. Resampling 4.6 years of one instrument is
exhausted. The campaign therefore closes with the decision package in
`reports/final_system_design.md` rather than continuing to burn configurations.

Remaining work that would genuinely move things forward, in order:
1. **A third instrument** (RTY, YM, CL) — portability is the only promotion criterion still open,
   and one ES failure is a data point, not a distribution.
2. **Complementary families** (failed persistence, DR-05) — the only route to a portfolio that
   does not simply hold more of the same factor.
3. **Genuinely forward data after a strategy freeze.**
4. **Quarterly monitoring of the overshoot ratio `r`** — free, requires no trading, and is the
   system's own early-warning statistic.

## 10. Config accounting

Wave 1 + 1b ≈ 90 · Wave 1c 80 · H-011 30 · open axes ≈ 55 → **≈ 255** campaign-to-date.
DSR in the Wave-1c report used n_trials = 170 (the count at that time); it must be re-run at the
current total before any promotion decision.

## 11. Unresolved integrity issues

None. Benign notes: the exporter emits 737,707 of 737,708 bars (boundary bar); the vendor
publishes `Signal_Wave = 0` before the first flip and treats bar 0 as a seed rather than a
no-progress bar — both now reproduced exactly.

## 12. Next highest-value action

Finish the H-006 confound control (fixed thresholds at matched turnover). If adaptive still wins
at matched turnover *and* at matched exposure, it is the first genuine improvement over the vendor
design; if not, the correct conclusion is "wider is better and normalisation is cosmetic", which
is equally publishable inside the campaign and much cheaper to run.
