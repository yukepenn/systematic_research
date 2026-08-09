# SMV2AK_VOLUME_BARS — REPORT

_Frozen spec: `runs/SMV2AK_VOLUME_BARS/spec.yaml` (committed 6633114 before any read).
Authored by the orchestrator from the execution agent's structured output — subagent Write
tool refused REPORT.md; every headline number independently reproduced exactly by red-team
(verdict: CONFIRMED-with-corrections, three disclosure-completeness corrections applied
below, none numeric — the CONFIRMED-NOT-BENEFICIAL verdict itself is unaffected)._

## Verdict
**CONFIRMED-NOT-BENEFICIAL.** Volume bars (bars that close on cumulative volume, not
elapsed time), at this pre-registered calibration, are closed — no adoption, no second bite
at this specific threshold without a genuinely new mechanism (dollar-volume or tick-imbalance
bars would count as new; a re-tune of this same threshold would not).

## Motivation
SMV2U/W inferred that 5-minute bars nearly beat 3-minute via turnover-damping, not faster
information — the real axis being information-per-bar, not minutes-per-bar. Volume bars
implement that axis directly. This spec tests it for the first time as a standalone clock.

## sub_438 — volume bar construction
Built from the committed 1-minute NQ substrate. Session-tagged with the identical gap-
heuristic `sm01_solarsim.resample_3m()` uses internally; volume bars close the instant
cumulative volume since the bar's own open reaches threshold V, session-bounded (never spans
18:00 ET).

**Threshold (pre-registered, frozen before sub_440 ran)**: V = incumbent 3-minute bar's own
average volume-per-bar = 667,169,740 / 519,714 = **1,283.72**.

**Session-calendar note (red-team-corrected)**: the 1-minute-tagged calendar carries **two**
distinct artifacts relative to the 3m control's 1,139-session calendar (not one, as
originally reported) — (1) 2022-11-06, a 60-minute DST-transition gap-split, and (2) a raw
1-minute-feed gap around 2025-11-27/28 (Thanksgiving week) that splits one continuous 3m
session into two 1-minute `sess_id` chunks BOTH labeled `sess_date=2025-11-27` — this second
artifact never showed up in the original `cal_1m − cal_3m` set-difference check (since it
doesn't add a new date) and was omitted from the original report despite being named in the
run's own code comments. Both artifacts are genuine raw-feed data-quality limitations (not
tagging bugs), consistent with this campaign's already-known boundary irregularities. All
downstream comparisons correctly use the control's 1,139-session calendar; neither artifact
changes any reported standalone/portfolio number.

**Bar-count distribution**: 423,340 volume bars total, mean 371.0/session (p10=292,
p50=377, p90=465) vs the incumbent's actual 456.3 3m-bars/session (full 18:00–17:00 ET
session, not the RTH-only ~130 the spec's illustrative figure referenced — disclosed, the
correct full-session figure is used throughout). Volume bars run at ~81% of the incumbent's
average bar count.

**Real-time width distribution**: median 1.00 min, p90=10.00 min, mean=3.68 min (fixed
incumbent = always 3.00 min) — heavily right-skewed, since intraday volume itself is
right-skewed: over half of all volume bars are a single 1-minute bar, with a long quiet-
period tail. The mean width sits close to the 3.00-min calibration target; the median bar is
far narrower.

**Leftover-volume-fraction** (session-final bar's volume as % of V, not asserted immaterial):
mean 0.59, median 0.60; 91.9% of session-final bars are true partial bars, 8.1% had the
session's very last 1-minute bar alone push volume past V.

## sub_439 — scale measurement (same discipline as SMV2AE/SMV2AI)
N (sigma window in volume bars) re-derived from the bars' own average elapsed-time width
(not assumed =460): N = round(1380 min / 3.68 min mean width) = **375** volume bars.
R_volbar (whole-dev median) = **0.775006**, regime-stable across 5 years (0.757–0.810),
pre-registered before sub_440's results were read.

## sub_440 — ensemble test: volume bars vs 3m-incumbent control
VMS_volbar = VMS_3m × 0.775006, clamp [40,1200]t unchanged, sigma window = 375 volume bars.

| metric | 3m incumbent (control) | volume bars (challenger) | Δ |
|---|---:|---:|---:|
| net $ | 119,008.9 | 74,200.0 | −44,808.9 |
| Sharpe | 0.7092 | 0.4305 | −0.2788 (worse) |
| maxDD (eod) $ | 40,207.6 | 45,490.2 | +5,282.6 (worse) |
| CDaR₀.₉₅ $ | 27,161.8 | 34,249.5 | +7,087.7 (worse) |
| tgt-changes/day | 33.02 | 39.23 | +6.21 (more churn) |
| friction share | 0.3256 | 0.4586 | worse |

Top-10-day retention = **0.9421** (< 0.95 threshold). **All three legs of the AND-rule fail**
(Sharpe worse, CDaR worse, retention short) — not a marginal miss.

Portfolio blend (DAYONLY_DUAL6040 60/40): control-leg rebuild reproduces the committed
incumbent champion exactly (net $194,416.04 both sides — a strong independent cross-check).
Volume-bar arm's portfolio: net $176,536.8, Sharpe 1.0877 (vs champion 1.2642), CDaR5
$18,043.1 (vs champion $14,322.2, worse) — does not beat the champion.

## sub_441 — old-regime screen: NONE_QUALIFIED
sub_440 produced zero candidates, so per spec this screen is explicitly N/A (disclosed, not
silently skipped). The confirmed-available native 1-minute 2006-2021 substrate was not
touched. Rebuild machinery is retained for a future wave.

## sub_442 — turnover mechanism note (always reported)

| clock | tgt-changes/day | total contracts |
|---|---:|---:|
| 5m bar-matched (SMV2U) | 20.34 | 33,100 |
| 5m time-matched (SMV2U) | 19.62 | 31,682 |
| 3m incumbent (control) | 33.02 | 49,964 |
| volume bars (this run) | 39.23 | 54,650 |

**The motivating hypothesis's pattern does not hold.** Volume-bar turnover is HIGHER than the
3m incumbent's, the opposite direction from both 5-minute arms (which are damped below 3m).
Root cause: at this V calibration, the bar-width distribution's median (1.00 min) sits well
below the 3-minute fixed cadence — because V was calibrated to the incumbent's AVERAGE
3m-bar volume, and intraday volume itself is right-skewed, so most bars close in ≤1 minute
during normal/elevated activity, with only the quiet tail stretching wide. Net effect at this
calibration: higher churn, not damping. A genuinely informative negative finding about *why*
the mechanism didn't help here, not just that it didn't.

## kill_or_keep
**CONFIRMED-NOT-BENEFICIAL.** The sub_440 arm failed all three AND-rule legs decisively.
Recorded, closed. No second bite at V=1,283.72 without a genuinely new threshold-selection
mechanism (dollar-volume or tick-imbalance bars would count as new).

## Red-team disposition
Verdict: **CONFIRMED-with-corrections**. Every headline number (bar construction, scale
measurement, ensemble test, portfolio blend, turnover comparison) independently reproduced
exactly; construction verified strictly causal (no lookahead, no cross-session volume
leakage); V and R_volbar both confirmed genuinely pre-registered (and are formula-determined,
leaving no discretionary room to re-pick); the AND-rule verdict applied mechanically and
honestly. Three corrections, all disclosure/completeness, none numeric: (1) the session-
calendar disclosure above, corrected from one artifact to two (the second Thanksgiving-week
split was present in code comments but omitted from the original report); (2) a latent,
confirmed-present-but-not-triggered bug flagged in shared executor code
(`common.py::e10_exec`'s `daily` dict keys by `sess_date` not `sess_id`, so two same-date
session fragments would silently overwrite rather than sum — did not affect this run's
numbers since the overwritten fragment had exactly $0.00 net, but is a real fragility for any
future run reusing this code on a collision date); (3) this REPORT.md itself, resolving the
missing-deliverable gap red-team flagged.

## Files
`out/volume_bar_construction.csv`, `out/bar_width_distribution.csv`, `out/bar_width_meta.json`,
`out/bars_per_session_meta.json`, `out/leftover_volume_meta.json`, `out/V_frozen.json`,
`out/V_frozen.npy`, `out/volbars_dev.parquet`, `out/scale_ratio_volbar.csv`,
`out/scale_ratio_volbar_meta.json`, `out/sigma_volbar_dev.npy`, `out/ensemble_test.csv`,
`out/sub440_verdict.json`, `out/daily_control_3m.csv`, `out/daily_volbar_arm_full.csv`,
`out/daily_volbar_arm_aligned.csv`, `out/portfolio_blend.csv`, `out/old_regime_screen.csv`,
`out/turnover_comparison.csv`, `out/turnover_mechanism_meta.json`, `out/gates.csv`.
Code: `src/common.py`, `src/step1_volume_bars.py`, `src/step2_scale_measurement.py`,
`src/step3_ensemble_test.py`, `src/step4_old_regime.py`, `src/step5_turnover_note.py`,
`src/finalize.py`.
