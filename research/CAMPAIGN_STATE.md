# Campaign State

_Last updated: 2026-08-07, after the reports integrity audit (section 13). **Campaign CLOSED** at
the formal stop condition — see section 9b. Entry point for everything: [`../README.md`](../README.md);
decision package: [`../reports/final_system_design.md`](../reports/final_system_design.md)._

## 1. Vendor independence — COMPLETE (RE01 + RE02)

The RenkoKings Solar Wave RK indicator is **fully reverse-engineered**. Every published series,
every signal symbol, exact on every bar:

**2,035,869 bars · 9 parameter configurations · zero mismatches on any series.**
Type 2 specifically: 45,825 events, 0 false positives, 0 false negatives.

> _Corrected 2026-08-07: this was previously reported as "1,436,860 bars". That figure was wrong
> and **understated** the evidence. The count above is the row total of the committed ledgers,
> printed by the test suite itself. The configuration count (9) was always right._

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

**CLOSED.** All waves complete (Phase 0 → Wave 3), stop condition reached and declared in section
9b, decision package delivered. Historical research only — no live-sim, paper trading or forward
monitoring was ever performed, and none may be without an explicit new instruction. Research
universe = all data 2022-01 → 2026-07-31; **no clean OOS remains and none is claimed.**

## 3. The central result: the deliverable is a region, not a parameter

CSCV over 16 chronological blocks (12,870 splits, 1,318 trading days): **PBO 0.56–0.66** with a
**negative** in-sample→out-of-sample slope (−1.03, r = −0.79). Walk-forward argmax selection earns
**$16,131 on 1-minute where the median config earns $121,373**. StopMultiplier is **not
selectable** from in-sample performance.

What works instead - hold the whole connected profitable range at equal risk, **without choosing
its boundary**. The red team showed the original 8-cell "plateau" boundary was itself an in-sample
selection, so the honest reference is every fixed cell actually tested. All figures are all-days
Sharpe on the **1,424-session NQ campaign calendar** (the union over every NQ family evaluated,
fixed so that rejecting a candidate can never move the basis), produced by
`src/analytics/ensembles.py`:

| | **R4: fixed, ALL 21 cells** | 8-cell plateau (as originally published) | best single (unknowable ex ante) |
|---|---|---|---|
| net | $159,424 | $180,479 | $249,934 |
| daily Sharpe | **+0.892** | +0.773 | +1.236 |
| max drawdown | **-$35,669** | -$53,689 | -$71,395 |
| worst year | +$2,583 | +$7,796 | - |
| positive in all 5 years | **yes** | yes | - |

> _Sharpe basis corrected 2026-08-07. Earlier revisions quoted +0.910 here, +0.917 in section 8,
> and +0.908 in the Pareto file — three numbers for one object, each on a different calendar. All
> Sharpes in this document are now on the single 1,424-session campaign calendar. **Net, drawdown
> and worst year are calendar-invariant and did not change, and no ranking changed.**_

The full-range ensemble beats the hand-drawn plateau on both Sharpe and drawdown - which is what
one expects if the boundary added only selection. Both are positive every year when only 3 of the
8 plateau members are, and neither is an exposure artifact (gross exposure ratio 1.000).

**The absolute edge is statistically real:** circular block bootstrap P(Sharpe <= 0) = **0.0051**
for R4-21, 0.0170 for the 8-cell version, **0.0020** for the adaptive family (1,424-session basis;
previously 0.0066 / 0.0147 / 0.0032 on the narrower calendar - the conclusion is unchanged and
slightly stronger). What is *not* established is any comparative ranking between families - see
section 8.

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
family reaches Sharpe 0.892** (quoted as 0.917 in the original red-team text, on that reviewer's
narrower calendar), and the adaptive advantage falls from +0.210 to **+0.087** with a
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
the cross-family calendar is the **union** over every NQ family evaluated — **1,424 sessions** —
not the archived 1,285-day matrix. (This was written as 1,348 when only four families existed and
1,370 after the combo family was added; it is now pinned to the full campaign union so that adding
or rejecting a candidate cannot move the basis again.)

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

**Counted, not asserted, as of the 2026-08-07 audit** (`registry/tested_configs_backfill.csv`,
method and caveats in `registry/REGISTRY_GAP_NOTE.md`):

| basis | count |
|---|--:|
| Wave 1 + 1b, contemporaneously registered (seq 1–90) | 90 |
| Waves 1c–3, distinct parameter sets (seq 91–229) | 139 |
| **campaign total, rule-R1 basis** | **229** |
| upper bound, counting every ledger including slip re-runs | 383 |
| *previously asserted here as ≈255, later ≈316* | *assertion, now superseded* |

The old ≈316 sits inside the honest 229–383 bracket, so nothing published was inflated by an
undercount. **This changes no downstream figure:** the R6 Harvey–Liu haircut Sharpe is 0.000 at
either end of the bracket, and deflation uses the preregistered `N_eff` (participation ratio ≈ 7),
not the raw count — see `registry/TRIAL_ACCOUNTING_RULE.md`.

## 11. Integrity issues

**Benign, resolved:** the exporter emits 737,707 of 737,708 bars (boundary bar); the vendor
publishes `Signal_Wave = 0` before the first flip and treats bar 0 as a seed rather than a
no-progress bar — both reproduced exactly.

**Open — see section 13.** The configuration registry and the immutable-run convention both
lapsed after Wave 1b. This is the campaign's most serious governance defect.

## 12. Next highest-value action

None inside this campaign — it is closed (section 9b). The ranked list of what would genuinely
move things forward is in section 9b and `reports/final_system_design.md` §10. The cheapest by far
is **quarterly monitoring of the overshoot ratio `r`**: free, requires no trading, no new
configurations and no data licence, and it is the system's own early-warning statistic.

(The action previously listed here — "finish the H-006 confound control" — **was run**, as H-014.
Volatility normalisation beat price normalisation by +0.728 Sharpe, p = 0.009. See section 9.)

## 13. Reports integrity audit — 2026-08-07

A full audit of the *documents* (not the research) after the campaign closed. Eight defects found;
none changed a ranking or a verdict, and all figures below were re-derived from the committed
execution ledgers.

**Fixed:**
- Four of six `reports/` files were stale by a full campaign — rewritten.
- `final_pareto.csv` mixed calendars and its **C2 row used a skipna mean** instead of the binding
  strict-1/N rule; it was the one row not produced by `ensembles.py`. Rebuilt. C2 was the rejected
  candidate, so nothing downstream moved.
- Vendor parity reported as 1,436,860 bars; the true count is **2,035,869** (the error understated
  the evidence).
- R4's Sharpe appeared as 0.910 / 0.917 / 0.908 in three places, each on a different calendar —
  now pinned to one 1,424-session basis.
- `registry/hypotheses.md` still recorded H-006 as PASS with a withdrawn DSR — corrected.
- Eight artifacts required by the mandate were missing (`type_semantics`, `active_parameter_map`,
  `type0_attribution`, `open_model_validation`, `solar_family_finalists`, `complementary_families`,
  `final_red_team`, `TYPE0_ATTRIBUTION_REPORT`) — all now written.

**Found and fixed 2026-08-07 (second pass).** The R5 specification named `SolarWaveOpenV4`; every
published R5 figure was actually measured on `SolarWaveOpenV3`. Verified by re-running all 13 cells
through V4 and comparing fill-by-fill: **not equivalent** — V4's `ResolveS()` snaps `S` to the tick
grid, V3 does not, and a half-tick shift changes which bars flip. Spec corrected to V3; **no
published number changes**, because none was ever measured on V4. The check produced a bonus
result: R5 is **insensitive** to the discretisation (ΔSharpe +0.029, P(Δ ≤ 0) = 0.247, daily
correlation 0.9949) while individual cells move by up to 44 %. Full analysis:
`research/10_v3v4_equivalence/V3_V4_EQUIVALENCE.md`.

**Disclosed, not fixed:** daily P&L is bucketed by calendar date rather than NT8 session date
(18:00 ET roll). The published basis is ~6 % **conservative**; both are now reported in
`final_pareto.csv`.

**Still open — the serious one.** `registry/tested_configs.csv` stopped at Wave 1b (seq 90),
`experiments.yaml` holds 2 of ~12 entries, and the `runs/<run_id>/spec.yaml` convention lapsed
after `RE01_open_parity`; Waves 1c–3 wrote 296 execution ledgers under `research/` instead.

*Partially mitigated:* `registry/tested_configs_backfill.csv` now enumerates all 296 ledgers with
parameters and evidence paths (seq 91–229), every row flagged `reconstructed=yes`. That restores
**auditability of what was run**. It does **not** restore preregistration: there is no record
proving pass/fail criteria were fixed before the numbers were seen in Waves 1c–3, so those waves
rest on researcher discipline rather than on the record, and a reviewer is entitled to discount
them. Full disclosure: `registry/REGISTRY_GAP_NOTE.md`.

*What was genuinely preregistered anyway:* `TRIAL_ACCOUNTING_RULE.md` (written, with its own
expected negative conclusion, before any DSR was recomputed under it), the H-014 pass/fail
criteria, and the red-team review (run by independent agents against results they did not
produce). Those three are on the record.

**Rule for any resumed work: restore the `runs/<run_id>/spec.yaml` convention and demonstrate it
on one throwaway run before adding a single new configuration.**
