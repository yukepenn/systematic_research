# DR-V4 Solar-CORE mechanism expansion (2026-08-08) — READ-ONLY, NO ADOPTION

Scope: genuinely new adaptive/data-driven mechanisms for the SOLAR **core state machine itself**
(anchor/flip rule, threshold S, SlowdownScan/WeakWeakSplit, the bar clock) — the same class of
object VolMult already improved once (`sigma460` replacing the fixed `StopMultiplier=179`). This
is explicitly **not** an allocator/exposure-overlay pass (`DR_SM_A/B/C`, dated the same day,
already cover that space exhaustively and self-scope OUT of touching the flip rule — see §0.2).
Nothing here is tested, scored, adopted, or preregistered. Output is a ranked candidate list for
a future wave's frozen spec.

## 0. What was read before any candidate was drafted

### 0.1 Core mechanics (what VolMult actually replaced, and what's left fixed)
- `research/03_reverse_engineering/SOLARWAVE_MATH.md` — the recovered five-line core: one state
  variable (anchor `a_t`, the running extreme of the **close**), one threshold `S`, flip on strict
  close-cross of `a_t ∓ S`. `TrendVector`/T2/T3/wave-counter are cosmetic to the Type-1 core. §5
  documents the ORIGINAL design flaw VolMult fixed (fixed-tick `S` desensitizes 41% as NQ's price
  doubled 2023→2025) and §6 lists the open knobs the vendor never exposed: (1) `S` need not be
  constant [DONE — VolMult], (2) the anchor need not be the close extreme, (3) reversal and exit
  distance need not be equal, (4) the wave/leg counter is unused free information.
- `src/analytics/sm01_solarsim.py` — canonical simulator. `resolve_s(t)`: `S =
  clamp(vol_mult*sigma[t], 40t, 1200t)`, `sigma` = causal trailing-460-bar mean `|dClose|`,
  resampled ONLY at flips. 13 members = 13 values of `vol_mult` (6..30 step 2), voted into E10.

### 0.2 What is explicitly OUT OF SCOPE / already covered by sibling passes
`DR_SM_A_academic.md` / `DR_SM_B_practitioner.md` / `DR_SM_C_dsp_control.md` (same-day, same
program) produced a 29-candidate hypothesis catalog for EXPOSURE/ALLOCATOR overlays (Kalman
slope-clarity, HMM regime allocator, consensus-proportional sizing, l1-trend/SSA trend-clarity,
morning classifiers, VWAP-persistence, etc.) and explicitly self-restrict: *"no idea below
modifies detection statistics, reference values, thresholds, bands, or flip logic"* (DR_SM_C
preamble) because *"threshold engineering as a class is permanently closed"* (DR03-H2 retrace-speed
test + T0-9 ARL-surrogate test, both on the flip rule's **price-threshold geometry** — CUSUM drift
allowance / hysteresis-band asymmetry / ARL-optimized reference values). That closure is about
**recalibrating where/how the SAME kind of threshold fires** on price alone. It is a narrower
claim than "no new volatility/efficiency ESTIMATOR may ever feed S" — VolMult itself is proof a
different estimator swap (vol-adaptive vs. fixed) changed the outcome; H-014 is on record as *"the
campaign's only clean significance result"* (volatility-proportional beats price-proportional,
+0.728 Sharpe, p=0.009). Candidates below that touch `S` are flagged against this tension
explicitly (§ per-candidate) rather than silently avoided, per the task's brief.

Also explicitly avoided as **already dead / banned**, verified in the sources named:
- Raw High/Low anchors, price-proportional thresholds, wave-index filters, more Type-2/3
  combinations, split exit/reversal without a genuinely new mechanism, optimized minute windows —
  all banned, thesis §20 ("What not to research next").
- Wave-index conditioning specifically: REJECTED, non-monotone 0.54–0.93 in-engine
  (`research/01_diagnostics/TYPE0_ATTRIBUTION_REPORT.md`, `CAMPAIGN_STATE.md`).
- T2/T3 signal layer: zero incremental info conditional on the ensemble's own position state
  (`runs/SMV2R_SOLAR_CORE_1/REPORT.md` §384, seq 384) — **any T2/T3-adjacent proposal below is
  flagged**, per the task's explicit instruction.
- VR, Kaufman ER150 (fixed-window), Kalman innovation whiteness, BOCPD regime age — all 16/16
  cells KILLED as univariate predictors of next-**session** SOLAR_DUAL_HTF PnL
  (`research/system_master/CURRENT_TRUTH.md` wave-6/7/8; `INDICATOR_FRONTIER.md` SMV2J/O). The
  SAME sigma460+ER150 pair only passes against a DIFFERENT target (next-**week** portfolio
  downside, SMV2Y) — diagnostic only, no policy yet. σ-percentile exposure filters separately
  falsified (non-monotone, `INDICATOR_FEATURE_FRONTIER.md`).
- Fixed-time clock family: 1m KILLED decisively (friction 102–128% of gross,
  `runs/SMV2U_CLOCK_CHALLENGE`); 5m bar-matched near-miss; 5m time-matched earned an R2 spec but
  FAILED confirmation at the same 0.85-confidence bar (`runs/SMV2W_5MCLOCK_R2`) — **3m remains
  incumbent, having survived 5 challenges**. Candidates below are explicitly a DIFFERENT clock
  axis (event/volume-driven, not a different fixed-time granularity) — the task's own framing.
- Member reweighting by trailing performance: deprioritized (H-013 not-run/superseded,
  `DR_SM_C_dsp_control.md` item 9); static cohort ablation (FAST removable-candidate, SLOW
  load-bearing) failed its own R2 confirmation (`SMV2T`, closed, no re-test without new
  hypothesis) — candidates below avoid this shape.
- Per-trade ML/feature-screen axis (`c01_t06_feature_screens.md`, `C01T1_ML`): `age` (bars since
  trend-birth extreme) and `sig460` (ticks/bar) FAILED fold-stability as **post-hoc trade-quality
  predictors**; `volvol` (std/mean|dclose|, 460b) and `eff120` (path efficiency) passed only
  BORDERLINE (4/5, weak) and the entire per-trade-suppression channel is closed
  (right-tail-adverse). Where a candidate below reuses these series, it is explicitly for a
  DIFFERENT mechanical role (threshold construction, not a post-hoc bet filter) and the weak
  prior is disclosed, not hidden.

---

## 1. Ranked candidates

### 1. Percentile/rolling-adaptive clamp ceiling (replace fixed 1200-tick cap) — **EVI 5**
**Mechanism & evidence.** The clamp's floor (40t) is bound-irrelevant, but the 1200t ceiling
ACTIVELY binds — and binds MORE for slow members over time (vm30: 10.9% of all dev bars,
**39.2% in partial-2026**, `SMV2R_SOLAR_CORE_1` seq 381 + `INDICATOR_FRONTIER.md`). This is
*exactly* the mechanism `SOLARWAVE_MATH.md` §5 diagnosed for the original fixed `StopMultiplier`:
a fixed absolute constant desensitizing as NQ's price/volatility level drifts — except now it is
the SAFETY CAP, not the base threshold, that is fixed and drifting out of calibration. The cap
is currently a hard-coded constant nobody has ever re-derived from data; `INDICATOR_FRONTIER.md`
explicitly flags "its binding rate is itself a candidate vol-regime state" but nothing has acted
on that flag. **Where it plugs in**: `sm01_solarsim.member_states.resolve_s`, replace the literal
`hi = smax_ticks * TICK` with a trailing quantile of realized `vol_mult*sigma` (e.g. p97.5 over a
long causal window, frozen at each trend's birth like `S` itself) — one line, same call signature.
**Why different from killed leads**: this is not "find one best StopMultiplier" (a fixed-point
search, PBO 0.898) — it is a THIRD level of the SAME already-validated mechanism (a fixed
constant → a data-adaptive one), applied to the regularizer rather than the base threshold, and
was never itself audited as an adaptive object (381 only measured that the fixed cap binds, it
did not test an alternative). **EVI rationale**: reuses the exact `vol_memory`-style harness
(`runs/SMV2R_SOLAR_CORE_1/out/vol_memory.csv` comparator machinery) with zero new data; cheapest
candidate on this list to screen; strong, specific, dated evidentiary trail (SMV2R-381 +
SOLARWAVE_MATH §5 + the partial-2026 binding-rate trend all point the same direction).

### 2. Volume bars (activity/information clock, replacing fixed-time 3m bars) — **EVI 5**
**Mechanism & evidence.** `SMV2U_CLOCK_CHALLENGE`'s own INFERENCE is that 5m beats 3m NOT because
it reacts earlier, but because coarser bars damp whipsaw in the SAME anchor/flip mechanism — i.e.
the right question is not "how many minutes" but "how much information per bar." A volume bar
(new bar every N contracts traded) equalizes information content directly: during high-activity
regimes (news, opens, trend days) bars form fast — the ensemble reacts as quickly as the 1m clock
without 1m's friction problem, because activity-triggering means real flips are triggered by real
volume, not idle 1-minute ticks; during quiet/thin regimes (holidays, overnight lulls — the exact
2022-11-06 thin-liquidity gap `SMV2U` had to build session logic around) bars form slowly,
directly implementing the turnover-damping effect that made 5m win. This is a mechanistically
DIFFERENT clock (event-driven, not a different fixed-time granularity) — not a re-skin of the
already-tested-3x 1m/3m/5m family. **Where it plugs in**: replace `resample_3m`'s
`t.dt.ceil('3min')` grouping key with a cumulative-volume threshold grouping (same OHLC
aggregation, same `sess_id`/session-boundary logic); everything downstream (`sigma_series`,
`member_states`, E10) is unchanged. **Why different from killed leads**: SMV2U/W tested three
points on ONE axis (bar duration); this is a different axis (bar information-content) entirely —
literature framing is Easley/López de Prado/O'Hara's "volume clock," never invoked in this repo.
**EVI rationale**: the `volume` column already exists in the committed 3m/1m bar substrate (zero
new data); the SMV2U/W comparator harness (standalone + portfolio + LOYO + friction-share) is
directly reusable with one substrate-construction change; a threshold-volume parameter needs a
single, principled, pre-registered choice (e.g. calibrate to match the incumbent's average bars/
session, exactly as SMV2U's "bar-matched" vs "time-matched" convention split already precedents).

### 3. Range-based (ATR-style) threshold estimator, blended with or replacing sigma460 — **EVI 4**
**Mechanism & evidence.** `sigma460` is close-only by construction (`SOLARWAVE_MATH.md` §1: "no
high, low, open, volume or time is used" in the core, and `sigma_series` in `sm01_solarsim.py`
computes `mean(|dClose|)` only). On a 3-minute bar, a large intrabar wick that reverses before the
close is real realized movement the anchor/threshold literally cannot see — the estimator
UNDERSTATES true range precisely on the volatile bars where the threshold's calibration matters
most. Wilder ATR (uses H/L, still causal, still trend-birth-frozen exactly like `sigma460`) is the
standard microstructure fix and costs nothing new: ATR14 is ALREADY a computed series in this repo
(`c01_t06_feature_screens.md`'s `gap_atr` feature, Wilder EWM α=1/14 on daily bars) — only needs
recomputation at the 3m-bar cadence VolMult actually uses. **Where it plugs in**: `resolve_s`'s
`sigma[t]` argument — swap the series or test a blend `sigma_blend = w*sigma460 + (1-w)*ATR_3m`.
**Why different from killed leads**: `gap_atr` (signed overnight gap / ATR14) was tested and
FAILED (3/5 fold-stability) as a **per-trade predictive feature** in a completely different
harness (T0-6's post-hoc classifier population) — that says nothing about whether ATR is a
BETTER or WORSE proxy for "how far the market actually moved" when used as the threshold-scaling
input itself, which is a construction question, not a prediction question. This is squarely
inside the "genuinely different volatility ESTIMATOR" territory the task invites (§0.2's framing
of what's actually closed vs. open). **EVI rationale**: same-cadence data exists (H/L columns are
already in the 3m bar substrate); same `vol_memory`-style comparator; single clean swap, easy to
run as 2-3 blend weights rather than a search.

### 4. Volume-scaled threshold confidence (widen S during thin-liquidity bars) — **EVI 3**
**Mechanism & evidence.** Nothing in the whole program has ever used the `volume` column as a
SIGNAL (only as bar/session metadata) — genuinely unexplored territory, distinct from every
sigma/VR/ER/Kalman/BOCPD state tested so far (all price-only). `SMV2U_CLOCK_CHALLENGE`'s own
substrate notes document real thin-liquidity artifacts already present in the raw feed — the
2022-11-06 ~10.5h thin-liquidity gap, and "thin-liquidity zero-print minutes... scattered singly"
in the 1m feed used for MTF reads — i.e. the campaign has already observed that low-volume bars
produce noisy, potentially spurious closes. First-principles mechanism: a directional-change
detector that treats a close print on 50 contracts identically to one on 5,000 is over-sensitive
exactly when it should be least trusting the tape. **Where it plugs in**: multiply `S` by a
monotone-decreasing function of a trailing volume-percentile at the flip bar (e.g.
`S_eff = S * g(vol_percentile)`, `g` low→high mapped to e.g. [1.15, 0.95], floor/cap-respecting) —
same `resolve_s` call site as candidates 1 and 3, purely additive to (not a replacement of)
VolMult's existing scaling. **Why different from killed leads**: not a session-level exposure
filter (the killed σ-percentile / VR / ER family, all of which gate EXPOSURE conditional on a
state predicting aggregate next-session/next-week PnL) — this changes the FLIP RULE ITSELF at the
bar level using an input series (volume) none of those studies touched. **EVI rationale**: data
on file (volume column); requires one new percentile-window design decision and a companion
robustness check that it isn't just re-deriving time-of-day (overnight bars are structurally
thinner) — moderate design care, still no new data collection.

### 5. Tick/dollar-imbalance bars (informational, not just activity, clock) — **EVI 3**
**Mechanism & evidence.** A refinement of candidate 2: rather than sampling on raw traded volume,
sample when SIGNED order-flow imbalance (buys minus sells, EWMA-thresholded) accumulates —
López de Prado's imbalance-bar family. Mechanistically closer to what a directional-change system
actually cares about: a market accumulating one-sided pressure fast should get MORE decision
points exactly when a real trend is forming (helping the whipsaw-vs-timeliness tradeoff candidate
2 targets more crudely); two-sided churn on equal volume would NOT trigger fast sampling under
imbalance bars even though it would under plain volume bars — a sharper version of the same
turnover-damping mechanism SMV2U's own 5m result is attributed to. **Where it plugs in**: same
substrate-construction site as candidate 2. **Why different from killed leads**: distinct from the
fixed-time clock family (as candidate 2 is) and a genuinely finer mechanism than plain volume
bars, not a duplicate of it. **Caveat / EVI discount**: the repo has NO tick-level signed-trade
data (`nq_3m/1m` substrates are OHLCV-only, `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` columns
verified: `open/high/low/close/volume` only) — a true imbalance bar needs either a new tick-level
NT8 export or a Lee-Ready-style tick-rule proxy (sign of bar-to-bar close change applied to the
bar's own volume) which is a real approximation, not the genuine microstructure object. Ranked
below candidate 2 for exactly this reason: candidate 2 is a strict subset that needs zero new
data and zero approximation.

### 6. Realized semivariance (up/down-asymmetric) threshold estimator — **EVI 2**
**Mechanism & evidence.** `sigma460` (mean absolute close-to-close change) is symmetric — it
cannot distinguish "460 bars of grinding chop" from "460 bars split between a sharp selloff and a
sharp rally," even though these imply very different appropriate reversal distances for a LONG
vs. a SHORT position specifically. Realized semivariance (Barndorff-Nielsen/Kishore-style split of
`sigma` into up-move and down-move components) is a standard, causal, well-understood estimator.
First-principles motivation: Solar's single economic bet (`SOLARWAVE_MATH.md` §4) is that a
44.75-point-scale retracement predicts continuation; if the market's realized DOWNSIDE variance is
currently elevated relative to upside (crash-risk-skewed), a LONG position's stop-out threshold
arguably should be calibrated against the downside estimator specifically, not a pooled symmetric
one. **Where it plugs in**: `resolve_s`, computing two `sigma` series (`sigma_down`, `sigma_up`)
and selecting/blending by current trend direction. **Why different from killed leads**: distinct
from VR (autocorrelation-based) and from ER150/eff120 (path-efficiency-based) — this is a
moment-asymmetry estimator, a different statistical object entirely, and it modifies the flip
RULE, not an exposure overlay (unlike `DR_SM_A`'s A-6 "signed-jump variation," which is explicitly
scoped as an allocator feature, never touching the flip rule). **EVI rationale**: data exists
(close series only, cheap to compute); ranked below 1-5 because the causal story for WHY
directional asymmetry in the threshold should help is more speculative than 1-4's — it introduces
2 new degrees of freedom (which side, how much blend) with no direct campaign precedent pointing a
sign, unlike VolMult's own H-014-confirmed mechanism.

### 7. Current-leg (segment-anchored) path efficiency as a threshold-width modulator — **EVI 2, flagged**
**Mechanism & evidence.** `SOLARWAVE_MATH.md` §6 explicitly notes "leg 1 of a trend is a different
animal from leg 8" as unused free information — but the ONE prior test of that intuition
(wave-index CONDITIONING of entry ELIGIBILITY, a bar-COUNT filter) is REJECTED (non-monotone,
`TYPE0_ATTRIBUTION_REPORT.md`). The candidate here is mechanically distinct: use a CONTINUOUS
Kaufman-efficiency-ratio computed over the CURRENT trend leg (net displacement / path length since
the anchor was last reset) to scale `S` directly — e.g. a highly efficient (low-noise) ongoing
leg gets a SMALLER reversal threshold (faster to declare a real reversal, since the leg's own
recent behavior has been clean), a choppy leg gets a LARGER one (more retracement required before
trusting a flip, directly targeting whipsaw). This is inside the flip rule, not an eligibility
filter and not a fixed-window predictor. **Why flagged / why ranked low**: it sits closest of any
candidate here to three separate killed/closed neighbors — wave-index conditioning (REJECTED),
ER150 as a fixed-window viability state (KILLED, 0/12 cells, `SMV2J`), and `DR_SM_A`'s A-4
"segment-anchored path efficiency" (already catalogued, same-day, explicitly scoped to the
ALLOCATOR layer only). The ONLY distinguishing feature that survives all three comparisons is the
plug-in point (inside `resolve_s`, changing what counts as a flip, vs. an overlay on top of a flip
that already happened) — a real distinction, but a narrow one, and the campaign's own priors
(wave-index non-monotone, ER150 null on the aggregate-PnL target) argue for tempered expectations.
Include only with this framing explicit in any future spec; a strong case could be made this is a
re-skin the campaign would reasonably decline to fund.

### 8. Vol-of-vol (dispersion of sigma460 itself) as a second multiplicative term on S — **EVI 2, flagged**
**Mechanism & evidence.** `volvol` (std/mean of `|dclose|` over 460 bars) already exists as a
computed series (`c01_t06_feature_screens.md`) and passed BORDERLINE (4/5 folds, weak: top decile
P&L +$17/trade only) as a **per-trade classifier feature** in the closed C01T1_ML pipeline. The
candidate here changes its ROLE: rather than a post-hoc bet filter (closed axis — suppression is
tail-adverse by the program's own repeated finding), use it as a second multiplicative factor
inside the threshold formula itself — `S = clamp(VolMult * sigma460 * (1 + β·volvol_z), 40, 1200)`
— i.e. widen the threshold specifically when realized volatility is itself unstable (vol-of-vol
high), a distinct regime object from the LEVEL of volatility sigma460 already captures. This is
the closest analogue on this list to what VolMult itself did (multiply an existing threshold
formula by a new causal volatility-family estimator). **Why flagged**: the existing evidence base
for `volvol` specifically is weak and mixed (borderline pass, tiny effect size, one fold
sign-flips) — this is not a null prior, but it is a soft one, and the mechanism-family
(volatility-of-volatility) heavily overlaps conceptually with the ALREADY-killed VR family (both
target "is the current regime turbulent/unstable," `SMV2J`'s 0/12 result), even though the
specific statistical object and the plug-in point (threshold construction, not exposure gating)
differ. Rank reflects real duplication risk that a red team would likely press hard on.

### 9. Vol-scaled SlowdownScan/WeakWeakSplit (adaptive T2/T3 trigger constants) — **EVI 1, heavily flagged**
**Mechanism & evidence.** `SlowdownScan=5` and `WeakWeakSplit=10` are fixed bar-counts
(`SOLARWAVE_MATH.md` §2) that gate ONLY the `Signal_Trend` strong/weak cosmetic and the Type-2/3
branch — exactly the two consumers already tested. `SMV2R_SOLAR_CORE_1` seq 384 found T2/T3 event
dummies carry **zero** incremental information conditional on the ensemble's own position state
(9 type×horizon cells, all `|t_NW| ≤ 0.70`) — this is a strong, direct kill of the entire
consumption path these constants feed. Per the task's explicit instruction, this candidate is
flagged: making the constants themselves volatility-adaptive (5 bars of no-progress means
something very different on a violent day vs. a quiet one — the same fixed-vs-adaptive logic that
motivated VolMult) does NOT resurrect informational content in a signal already shown to carry
none, UNLESS the target metric changes. The one narrow surviving angle: SMV2R seq 383 found the
FAST cohort's specific weakness is churn/whipsaw cost (not forward-return sign) — an adaptive
`SlowdownScan` was never tested against a TURNOVER-REDUCTION target (only against forward-PnL
information, which is a different question T0-6/384 already answered). **Why ranked last**: this
narrow angle is real but thin, requires reviving the T2/3 apparatus explicitly (the task's own
red flag), and the more direct turnover-reduction levers (candidates 1-2, which the program's own
evidence already ties to turnover) dominate it on cost and directness. Include only as the
explicit, honest closure of this specific open question, not as a promising lead.

---

## 2. Sequencing note (not a recommendation, an observation)
Candidates 1-3 share one property the rest don't: each is a single, cheap, one-line change to
`resolve_s`/bar-construction inside the ALREADY-VERIFIED `sm01_solarsim.py` harness, each reuses
an existing R2-confirmation-style comparator (`vol_memory.csv` for 1/3/4/6/7/8/9;
`clock_arms.csv`/`portfolio_contrib.csv`/LOYO for 2/5), and each has a specific, dated, in-repo
evidentiary trail rather than a general microstructure prior. If this list is picked up, 1 and 2
are the natural first frozen spec (they do not compete for the same mechanism and can share one
run's infrastructure); 3 is the natural second (same harness family, new estimator not new
clock). 5-9 either need new data/approximation machinery (5) or carry real duplication risk
against already-closed leads (6-9) and should wait on 1-3's results before consuming trial budget.

## 3. Files read (full list)
`research/system_master/CURRENT_TRUTH.md` (wave 1-9, full) · `research/registry/rejected_ideas.md`
(full) · `research/03_reverse_engineering/SOLARWAVE_MATH.md` (full) ·
`src/analytics/sm01_solarsim.py` (full) · `runs/SMV2U_CLOCK_CHALLENGE/REPORT.md` (full) ·
`runs/SMV2R_SOLAR_CORE_1/REPORT.md` (seq 381-385 + synthesis) ·
`research/system_master/INDICATOR_FRONTIER.md`, `INDICATOR_FEATURE_FRONTIER.md`,
`NEXT_RESEARCH_QUEUE.md` (full) · `research/system_master/deep_research/DR_SM_A_academic.md`,
`DR_SM_B_practitioner.md`, `DR_SM_C_dsp_control.md` (headers + C-family full) ·
`research/system_master/deep_research/DR_V4_EXPANSION_PASSES_20260808.md` (full, confirms
Engine-3 exclusion) · `research/04_complementary_family/c01_t06_feature_screens.md` (full) ·
`research/01_diagnostics/TYPE0_ATTRIBUTION_REPORT.md`, `research/CAMPAIGN_STATE.md`,
`research/frontier.yaml`, `research/registry/hypotheses.md` (wave-index cross-refs) ·
`research/Research_Thesis.txt` §20 (banned-axes list) · `research/system_master/EVIDENCE_MAP_RAW.md`
(spot greps: volvol/eff120/ATR/wave-index/H-013/H-014) · `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`
(column check, confirms OHLCV-only, no tick/signed-volume data).
