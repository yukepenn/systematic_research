# VAR01_VARIANCE_SIGNATURE — multi-scale realized-variance signature vs Solar13 cohort structure

**Directive:** Master v3 sec37-43. **Frozen spec:** `runs/VAR01_VARIANCE_SIGNATURE/spec.yaml`
(written and committed before any result was computed). **Status: CLOSED this wave —
NO_LARGE_EFFECT_DETECTED.** Diagnostic-only family; no policy, exposure rule, entry/exit, or
weighting change was constructed or proposed.

## 0. What this family is and is not

Not another indicator grid. Motivated by trend-following convexity theory (Dao/Nguyen/Deremble/
Lempériere/Bouchaud/Potters: trend P&L ≈ long-term variance − short-term variance of the
underlying). The question: does a **multi-scale realized-variance signature**, built at horizons
derived from Solar13's own fast/slow VolMult cohort structure, carry information about
Product-B's forward economics beyond what sigma460 (the existing vol-level control) already
captures?

This is explicitly **not** a repeat of the already-killed single-horizon Lo-MacKinlay Variance
Ratio (SMV2J: VR 9 cells + ER 3 cells, 0/12 reach `|t_NW|>2` vs next-session Product-B/E10 PnL;
SMV2Y: the same VR series is 0/12 again vs a *different* target, next-week downside — VR has now
failed at two frequencies against two outcome definitions). VAR01 differs in construction on
three axes: (i) **multiple simultaneous horizons**, not one `(q,N)` pair; (ii) measures realized-
variance **level/amplitude** (a regime signature), not the serial-correlation **ratio** VR
computes; (iii) horizons are **empirically derived from Solar13's own measured member hold-times**
(fast_member/slow_member sign-run lengths), not arbitrary round numbers picked independently of
the system under study.

## 1. Prior reading (Step 1, done before construction)

- `DR_V2_PASS_B_DSP.md` "H1. Rolling Variance Ratio state" — RANK 1, proposed but the version
  actually executed (SMV2J) was single-horizon; multi-scale was never tried.
- `DR_SM_A_academic.md` "A-5. Intra-session variance ratio" — CLEAR-WITH-CONSTRAINTS verdict;
  its own text requires any VR-family construction to be strictly intraday-causal, respected here.
- `INDICATOR_FRONTIER.md` SMV2J/SMV2O/SMV2Y — VR/ER/Kalman-whiteness/BOCPD all KILLED against
  next-session PnL; VR alone re-tested and killed again against next-week downside. States were
  confirmed orthogonal to deployed controls (`|corr| ≤ 0.14`), i.e. a genuine no-signal result,
  not collinearity being mistaken for absence of signal.
- `STRUCTURE_MAP.md` Solar13 row — VM 6..30 step 2, **adjacent**-VM correlation 0.77 vs **far**-VM
  correlation 0.025: redundancy is local, which is why a small number of genuinely-separated
  horizons (not a dense grid) is the right design here.
- `runs/SA0_SYSTEM_STRUCTURE/src/02_ensemble.py` — canonical cohort definition reused verbatim:
  FAST = VM{6,8,10,12}, MID = VM{14..22}, SLOW = VM{24,26,28,30}.
- SMV2R/SMV2T — the FAST cohort (VM6-12) is a live "removable-candidate" lead that **failed** R2
  confirmation (13-member incumbent retained): FAST members are not safely dismissed as noise,
  so their own characteristic timescale is treated here as real information, not discarded.

## 2. Construction (Step 2)

**Substrate:** `runs/U0_UNIFIED_STATE/out/u0_state_table.parquet`, canonical dev window only
(`is_health_only_bar==False`, 519,714 bars, 2022-01-03..2026-05-29). No bar ≥2026-08-01 touched.

**Correctness gate (PASS):** `sum(bar_pnl_B_nq_dollars)` over the dev window = **$301,915.92**,
exactly the certified Product-B NQ net. The substrate reproduces the certified number before any
new state was built on top of it.

**Horizon derivation (empirical, from the existing certified `fast_member`/`slow_member` columns
— PEND[:,0]=VM6, PEND[:,-1]=VM30 — not a new backtest):**

| member | median sign-run | mean sign-run |
|---|---|---|
| fast_member (VM6) | 17 bars (51 min) | 31.8 bars (95 min) |
| slow_member (VM30) | 185 bars (555 min / 9.25h) | 310.3 bars (930 min / 15.5h) |

**Frozen horizons (3-min bars):** SHORT=5 (~15min, sub-fast-member noise floor), **FAST=20
(~60min, matches VM6's own median hold)**, **SLOW=310 (~930min/15.5h, matches VM30's own mean
hold)**, SESSION=460 (~23h, sigma460's own VolPeriod — the directive's own licensed round-number
anchor).

**Deseasonalization (disclosed approximation):** per-bar squared log return `r2[t]`; the first
bar of every session (1,139 bars, 0.22% of dev) is flagged as an overnight/roll gap and excluded
from both the seasonal profile and the RV windows. A causal (`expanding().shift(1)`, same-
`session_phase`-bucket-only, strictly trailing) seasonal profile is built across the 7
`session_phase` buckets and used to deseasonalize: `r2_adj[t] = r2[t] / (trailing_phase_mean[t] /
trailing_grand_mean[t])`. 99.75% of dev bars produce a usable `r2_adj`. Limitation disclosed: this
corrects the *average* diurnal level per phase-bucket only, not finer within-phase time-of-day
structure, and the first ~90 sessions have noisier seasonal estimates with no explicit burn-in
trim applied.

**RV and spread:** `RV_H[t]` = trailing mean of `r2_adj` over the last H valid bars (causal,
require ≥80% coverage). **Primary (preregistered) object:**
`SPREAD_FAST_SLOW[t] = ln(RV_SLOW[t]) − ln(RV_FAST[t])` — the direct multi-scale analogue of the
Bouchaud/Potters long-minus-short variance driver, anchored to Solar13's own cohort timescales.
`SPREAD_SHORT_SESSION` (round-number anchor pair) computed as a secondary robustness check only.

**Non-redundancy check (new, not in the frozen spec but cheap and informative):** daily
session-close `SPREAD_FAST_SLOW` correlated against all 9 previously-tested VR cells, all 3 ER
cells, `sigma460`, and `htf` from the already-run `SMV2J_STATE_HARNESS` (1,139-session overlap).
**Max `|corr| = 0.099`** (vs. ER_n460); everything else is smaller; vs. sigma460 `corr=-0.013`,
vs. htf `corr=-0.042`. VAR01's state is confirmed genuinely orthogonal to every state this
program has already tested and killed, and to the deployed controls — the result below is not a
relabeled duplicate. (`runs/VAR01_VARIANCE_SIGNATURE/out/var01_crosscorr_vs_priorstates.csv`)

## 3. Results (Step 3 — the key falsifiable question)

### 3a. Persistence / autocorrelation

| test | value |
|---|---|
| daily (session-close) lag-1 autocorrelation | **0.199** (n=1,138 sessions) |
| bar-level ACF at lag=FAST (20 bars) | **0.429** |
| bar-level ACF at lag=SLOW (310 bars) | **-0.047** |

The spread is genuinely persistent at short/daily horizons and decays to roughly zero by its own
SLOW horizon — behaves like a real (if modest) variance-regime state, not white noise.

### 3b. Incremental value vs. sigma460 (bucket-residualize + ΔR², R4/R5/EXP01/ICT0102
methodology; target = forward Product-B PnL over a non-overlapping bar sample, unconditional on
position — same framing as SMV2J's "does the environment predict near-future strategy P&L")

| horizon | n | R² base (σ460 tercile) | R² ext (+spread) | ΔR² | spread coef | HAC t | resid. Spearman | years same-sign |
|---|---|---|---|---|---|---|---|---|
| **FAST** (20 bars, ~1hr fwd) | 25,953 | 0.000004 | 0.000318 | **+0.000313** | +13.86 | **+2.461** | 0.0271 | **5/5** |
| **SESSION** (460 bars, ~1 session fwd) | 1,127 | 0.000080 | 0.000161 | +0.000081 | +34.20 | **+0.308** | 0.0042 | 3/5 |

**Dollar-denominated (quintile) view, FAST horizon:** background forward-1hr Product-B PnL has
mean $11.42 / std $782 per non-overlapping window. Residualized quintile means by spread rank are
**cleanly monotonic**: Q1 −$17.64, Q2 −$11.09, Q3 −$2.02, Q4 +$7.45, Q5 +$23.30 (Q5−Q1 = **+$40.94**).
Year-by-year residualized Spearman: 2022 +0.041, 2023 +0.008, 2024 +0.050, 2025 +0.043, 2026(partial)
+0.023 — same sign every year.

**Dollar-denominated (quintile) view, SESSION horizon:** quintile means are **not monotonic**
(Q1 −$123.5, Q2 +$21.5, Q3 **+$397.8**, Q4 −$143.3, Q5 −$151.3; Q5−Q1 = **−$27.8**). Year-by-year
sign flips in 2/5 years (2023, 2024 negative vs. 2022/2025/2026 positive).

**Secondary spread (SHORT/SESSION round-number pair), robustness only:** residualized Spearman
0.0112 (FAST horizon) and −0.0050 (SESSION horizon) — weaker than the primary cohort-anchored
spread on both counts; no support for a different horizon pairing.

## 4. Interpretation

The FAST-horizon result is **real but economically negligible**, and matches an exact precedent
already closed in this program: `SHADOW01_SETUP_COMPATIBILITY` found a residualized correlation
that was "statistically real (bootstrap CI excludes 0)... but ΔR² 0.0002-0.0019 is 5-10x below
R4/R5's own already-modest findings — economically negligible, null not practically rejected."
VAR01's FAST-horizon ΔR² (**0.000313**) sits inside that identical closed range. The HAC t-stat
(2.46) is nominally similar in magnitude to this program's one PASSING state (SMV2Y: t=-2.30/
-3.05), but SMV2Y additionally cleared a ≥0.99 moving-block-bootstrap same-sign bar at weekly,
decision-relevant frequency; VAR01's ΔR² and dollar quintile spread ($41 on a $782 background std)
are an order of magnitude too small to plausibly clear that same bar even before running the
bootstrap, so the bootstrap was not run (disclosed limitation — the practical verdict would not
change; a statistically-tighter confirmation of an already economically negligible effect is not
worth the trial budget).

Critically, the **SESSION-horizon** test — the timescale that actually matters for any real
policy question (a position's session-to-multi-session forward economics, which is what Step 4's
fast-vs-slow cohort question would need to operate on) — is a **clean statistical and
chronological null**: t=0.31, ΔR²=0.00008, non-monotonic quintiles, only 3/5 years same-sign. This
directly parallels SMV2J/SMV2Y's own session/week-level VR kills: multi-scale realized-variance
LEVEL, like the single-horizon variance-correlation RATIO before it, adds no usable information
beyond sigma460 at the horizon where it would actually matter.

**Too-good-to-be-true gate:** not triggered — the result is uniformly weak-to-null, the opposite
of surprisingly strong; no lookahead is possible by construction (RV windows strictly trailing
and end at bar t; forward targets are strictly `(t, t+H]`, verified via the `forward_sum` helper's
shift/rolling/shift construction; overlap-induced autocorrelation is avoided by using a
non-overlapping bar subsample for the regression, not by any target/feature leakage).

**Right-tail audit:** not triggered — no entries/exits/holds were constructed or modified; this
is a pure descriptive-state test on the already-certified Product-B decision sequence.

**Chronology (2022-2025-only wash threshold, LOYO):** not applicable in the standard sense — no
policy or exposure change is proposed, so there is no control-vs-challenger net P&L to wash-test.
Year-by-year sign-stability (the diagnostic-test analogue, matching R4/EXP01's own convention) is
reported above and is the basis for the FAST-vs-SESSION distinction driving this closure.

## 5. Step 4 — explicitly not run

Step 4 (does the variance-spread state differentially predict the FAST vs. SLOW Solar13 cohort's
own forward value) is a positional/holding-period question and would need to operate at the
SESSION or SLOW timescale, not the FAST 1-hour microstructure scale where the only detectable
effect lives. Since the SESSION-horizon test of the *pooled* effect is already a clean null
(non-monotonic quintiles, statistically insignificant, chronologically unstable), slicing that
already-null pooled effect by cohort is very unlikely to produce a real result and would spend
trial budget without plausible payoff. Per the directive's own instruction ("If Steps 2-3 show no
residual value beyond sigma460 [at the decision-relevant horizon], that is a complete, valid,
honestly-reported closure — do not force Step 4"), Step 4 is skipped.

## 6. Disposition

**NO_LARGE_EFFECT_DETECTED.** A genuinely new, non-redundant (max `|corr|=0.099` vs. every
previously-tested state), persistent (daily lag-1 autocorr 0.20) multi-scale variance-spread
signature was built and tested. It carries a real but economically negligible short-horizon
signal (same order of magnitude as this program's own already-closed SHADOW01 finding) and no
detectable signal at all at the session horizon that would matter for any real policy. This
closes the VAR01 family for this wave: the multi-scale variance-LEVEL axis, like the
single-horizon variance-RATIO axis before it (SMV2J/SMV2Y), does not add usable information
beyond sigma460 for Product B. No promotion, no deployment, no Step 4 cohort test.

## Evidence

All scripts and raw output: `runs/VAR01_VARIANCE_SIGNATURE/src/01_variance_signature.py`,
`runs/VAR01_VARIANCE_SIGNATURE/out/` (`var01_results.json`, `var01_incremental_summary.csv`,
`var01_bar_features_{FAST,SESSION}*.csv`, `var01_year_by_year_*.csv`,
`var01_secondary_spread_summary.csv`, `var01_crosscorr_vs_priorstates.csv`). Frozen spec:
`runs/VAR01_VARIANCE_SIGNATURE/spec.yaml` (written to disk before any result was computed).
