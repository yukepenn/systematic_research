# WAVE C01 — Conditioning, short-side structure, and complement candidates

_Preregistered 2026-08-07 (owner-directed reopening of research after CAMPAIGN_CONVERGENCE_2026_08_07;
instruction: "看看我们基线可以怎么优化进步/可以补充什么策略/可以补充什么变量"). This spec is committed
BEFORE any Tier-0 result is read. Constants below are FROZEN; no adjustment after any read.
Comparator: executable R5-E10 (primary) / theoretical R5 (research proxy, corr 0.9985).
Basis: Lifetime commission + 1 tick/execution; finalists must also pass 2-tick stress.
All risk series TRUE_MTM or explicitly REALIZED_ONLY._

## 0. Sources and forbidden-axis filter

Inputs: four deep-research packets (conditioning, hysteresis/CUSUM, meta-labeling, complements —
digests archived in the session workflow journal, wf_5d54a694-be0) filtered against
`research/registry/rejected_ideas.md` + `research/frontier.yaml`. **Dropped as forbidden before
preregistration:** split exit/reverse thresholds in any α/β form (H-007/DR03-H1 FALSIFIED —
"early exits amputate the right tail"); its dependents (cost-elasticity, recurrent-coordinate,
side-asymmetric bands); any flip-count veto; any gap-fade or failed-flip-fade re-tune; any new
Solar parameter mining; timed-exit dominance re-tests. DC02b (σ-invariance, this commit) is
prior instrumentation, not a wave item.

## 1. Structure: analysis-first

**Tier 0 = zero config burn** — pure analytics on committed ledgers/bars/daily vectors + public
daily series. Consumes 0 R1 trials (instrumentation class, like B01a arm (a)).
**Tier 1 = config burn** — NT8 runs or ML training, entered ONLY through a Tier-0 pass gate.
Wave budget: **≤ 10 R1 trials** (Tier 1). If the budget exhausts without a robust pass, the wave
closes and its axes are marked exhausted.

Global gates for ANY promotion out of this wave (unchanged from B01/thesis):
positive after base costs; survives 2-tick stress; ≥3/5 years positive; split-half same-sign
(2022-07→2024-06 vs 2024-07→2026-06); losing-day corr with Family A ≤ +0.25 for complements;
no month > 40% of sleeve net; **hard right-tail constraint** — for any state down-weighted below
m=1, the share of top-1%-trade P&L in that state must be ≤ its share of sessions (stratified
block bootstrap, block = 5 sessions, 10,000 draws); Romano-Wolf stepdown within each family.

## 2. Tier-0 items (frozen constants; ranked by EVI)

**T0-1 SHORT-SIDE REGIME STRUCTURE (SOLAR-01; highest EVI).** Tag every short fill in the 13
member ledgers with three flags computed from NQ daily closes as of the PRIOR close: G1 = close <
200d SMA; G2 = 20d realized vol > 70th pct (rolling 3y); G3 = G1 OR G2. Report short P&L/Sharpe/
count per cell per year. Pass gate to Tier-1 (gated/sized-short NT8 confirmation): ungated-state
short P&L negative (t ≤ −2) AND gated state retains ≥ 80% of 2022+2025 short net. Reject: not
regime-separable, or crisis retention < 80% → record "shorts are crisis insurance; keep symmetric"
and close. Fallback arm (only if binary gate fails the retention test but separability holds):
continuous w_short = clip(volz20, 0, 2)/2, one functional form, no search. DoF: 3 flags
(Bonferroni α = 0.05/3) + 1 fallback form.

**T0-2 ORACLE CAPACITY BOUND for any ML overlay (kill-or-continue for the whole ML program).**
Build the counterfactual ledger engine first (no-bet ⇒ member flat for that episode; validation:
0% filter must reproduce the canonical five numbers exactly). Then synthetic classifiers: flip
true win/loss labels at ε ∈ {0, .1, .2, .3, .4, .45, .5}; oracle-remove worst k% ∈ {5..50 step 5}.
Pass: AUC-0.55-equivalent (ε≈.45) yields ≥15% DD reduction at ≤10% growth cost → ML program may
proceed to feature screens (T0-6). Reject: needs >AUC-0.60 to break even → ML program CLOSED at
zero training cost. DoF: 0.

**T0-3 CUSUM DRIFT-ALLOWANCE DIAGNOSTIC (DR03-H2 stage 1; the one open threshold-mechanism).**
From existing fill ledgers: for every flip, pre-flip retrace speed = retrace ÷ bars-since-extreme
(σ units); bucket into terciles; mean next-trade P&L + MAE per tercile per side. Pass to Tier-1
(k-sweep, k ∈ {−.5,−.25,−.1,0,+.1,+.25,+.5}·σ_bar, S′ rescaled to hold flips/yr ±15%): monotone
profile significant under block bootstrap. Reject: flat → k irrelevant (flips are impulse-
dominated); DR03-H2 closes. Literature default for our large-h regime is k<0 — the diagnostic
decides, not the default. DoF: 0 (stage 1), 1 (stage 2).

**T0-4 VOL-SURPRISE DECOMPOSITION of the known high-vol effect (SW08 refinement).** HAR-RV
(RV_d, RV_w, RV_m, expanding window, fixed form) per session from 3-min bars; U = RV − forecast.
2×3 sort (forecast tercile × surprise tercile) of ensemble daily P&L; tradability test on LAG-1
surprise. Pass to Tier-1 (exposure rule m ∈ {0.5, 1.0, 1.5}, session-level, applied to E10):
lag-1 U-conditioning ΔlogG > 0, Romano-Wolf p<.05, both halves, tail gate. Reject: effect only
contemporaneous or subsumed by forecast level. DoF: 2.

**T0-5 EXOGENOUS CALENDAR TEST (announcement days; up-weight-only, structurally tail-safe).**
CPI/NFP (08:30 ET) + FOMC statement (14:00 ET) dates 2022–2026 committed as CSV BEFORE analysis.
Compare ensemble daily P&L and DC overshoot ratio r on announcement vs vol-matched non-announcement
sessions (match on HAR forecast from T0-4); pre/post-release split. Pass: announcement-session
P&L ≥ 2× control after vol matching, p<.05, both halves. DoF: 1.

**T0-6 UNIVARIATE FEATURE SCREENS (only if T0-2 passes).** 8 features fixed: member consensus,
episode age, pre-entry overshoot/θ, path efficiency 120b, σ (460b), vol-of-vol, session bucket
(6 broad bins: 18:00–02:00, 02:00–08:30, 08:30–09:30, 09:30–11:30, 11:30–15:00, 15:00–17:00 ET),
overnight gap/ATR14. Decile-binned hit-rate/P&L monotonicity, fold-stable (Spearman sign agreement
≥4/5 outer folds under the purged-CV harness: day-grouped, purge overlapping label intervals,
2-day embargo, average-uniqueness weights). Pass: ≥2 fold-stable features → Tier-1 ML arms
(L2-logistic only, C ∈ {.01,.1,1}, calibrated sigmoid sizing vs binary filter vs **vol-only
control** — if the vol control matches the classifier, adopt vol targeting and close ML). All 8
registered for multiplicity. DoF: 8 registered tests.

**T0-7 OVERNIGHT/INTRADAY DECOMPOSITION (Family D, first direct NQ evidence).** r_on vs r_id per
session from 1-min bars, 2022–2026; conditional variant: overnight long only after prior RTH
return ≤ 25th pct (rolling 250d). Falsifier built in: NY Fed documents the unconditional drift
≈ 0 since 2021. Pass to Tier-1 sleeve sim (17:59→09:31, $4.36 RT + 2 ticks): conditional
after-cost Sharpe ≥ 0.3, ≥3/5 years, corr ≤ +.25, no month > 40%. DoF: 2.

**T0-8 VRP PROXY STUDY (Family E gate; zero build).** Three preregistered public proxies: Cboe
PUT index daily return; inverted SPVXSP (short-VX1 incl. roll); VIX − 20d realized spread.
Join to E10 daily vector. Pass: for ≥2 of 3 proxies — overall corr ≤ 0 AND positive mean on E10
bottom-quintile days AND proxy worst-decile days overlap E10 best-decile days (asymmetric-sizing
warning). Only then does Family E get an instrument-design phase (out-of-pipeline; separate
decision). DoF: 3 (Bonferroni).

**T0-9 SURROGATE ARL NULL (epistemic hardening).** 500 stationary block bootstraps (block ≈ 1
session) of 3-min log-returns with vol clustering preserved, trend persistence destroyed; run the
baseline flip rule on each. Pass (for the mechanism): real post-flip drift > 97.5th pct of
surrogate band. Fail: flips ≈ ARL noise → threshold engineering permanently deprioritized. DoF: 0.

**T0-10 DAY-OF-WEEK NEGATIVE CONTROL (pipeline calibration).** Weekday partition of E10 daily
P&L, Kruskal-Wallis, both halves, charged to the control budget (4 DoF). If any weekday "passes",
audit the wave's testing pipeline before believing ANY other Tier-0 result.

**T0-11 MONITOR-01 PROTOCOL FREEZE (per DC02b).** Quarterly, free: recompute r on trailing-4-
quarter 1-min DC segments at θ=179 AND in σ bands θ/σ ∈ [2.0,9.4]; alarm thresholds: σ-banded
r below 1.05 for two consecutive quarters, or yearly-CV-equivalent drift > 3× the DC02b band CV
(0.013–0.020). First reading = the DC02b tables (baseline committed with this spec).

## 3. Explicit non-goals

No new Solar parameter search; no α/β threshold splits; no fade re-tunes; no leverage; no
live/sim/paper/forward activity; no cross-instrument transfer re-tests without a new mechanism;
low-priority items parked (gamma proxy — weak instrument; EOD-reversal and lead-lag kill-checks —
may run as 1-regression Tier-0 addenda if time permits, same discipline).

## 4. Accounting

Tier-0: seq 0 instrumentation rows in `tested_configs.csv` (counts_as_trial: no), one row per
item on completion. Tier-1: standard R1 rows, spec.yaml per run committed before execution,
budget ≤ 10. Registry: this spec's hypotheses enter `research/registry/hypotheses.md` as
C01-T0-1 … C01-T0-11 on first read.
