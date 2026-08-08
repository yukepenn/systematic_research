# SMV2AE_1MIN_RESCALE — REPORT

_Frozen spec: `runs/SMV2AE_1MIN_RESCALE/spec.yaml` (committed 2b2f88a before any read).
Authored by the orchestrator from the execution agent's structured output — the subagent's
Write tool refused both `REPORT.md` and its fallback `REPORT_DRAFT.md` (a stricter block than
prior runs hit); every number below traces to a committed `out/` artifact, independently
reproduced bit-for-bit by red-team (verdict: CONFIRMED, no numeric corrections needed)._

seq [418, 419]. class R1_FAMILY_TEST + DIAGNOSTIC.

## Motivation (from spec)
SMV2U tested 1-minute bars but reused the 3-minute VMS=[6..30] constants and [40,1200]-tick
clamp bounds **verbatim** across two sigma-window conventions (bar-matched 460 bars,
time-matched 1380 bars ≈ 23h) — both failed, friction consuming 102–128% of gross P&L. The
sigma *time window* was already correctly rescaled; the VolMult *point-scale* itself never was
— 1-minute |Δclose| is not point-comparable to 3-minute |Δclose| even over an identical
real-time window. This spec measures the actual empirical rescale ratio and re-tests with it.

## sub_418 — scale ratio R
R_t = sigma460(3m) / sigma1380(1m, time-matched), inner-joined on exact 3m-bar-close timestamp
(519,489/519,714 = 99.957% match rate). 519,459 valid rows after excluding burn-in.

| scope | n_obs | mean R | p1 | p10 | **p50 (median)** | p90 | p99 |
|---|---:|---:|---:|---:|---:|---:|---:|
| whole_dev | 519,459 | 1.7294 | 1.5684 | 1.6413 | **1.7301** | 1.8160 | 1.8856 |
| 2022 | 117,599 | 1.7414 | 1.5922 | 1.6571 | 1.7424 | 1.8233 | 1.8856 |
| 2023 | 117,699 | 1.7198 | 1.5497 | 1.6306 | 1.7210 | 1.8085 | 1.8845 |
| 2024 | 118,313 | 1.7290 | 1.5643 | 1.6408 | 1.7305 | 1.8129 | 1.8900 |
| 2025 | 117,509 | 1.7291 | 1.5624 | 1.6357 | 1.7296 | 1.8211 | 1.8858 |
| 2026 (partial) | 48,339 | 1.7257 | 1.5873 | 1.6473 | 1.7256 | 1.8077 | 1.8696 |

The ratio is tight (p1–p99 span 1.57–1.89) and regime-stable (per-year medians 1.721–1.742, a
~1.2% band across 5 calendar years) — a single scalar rescale is a reasonable model.

**R_SELECTED = 1.730064** (whole-dev median, pre-registered per spec, used regardless of the
per-year spread — read programmatically by sub_419, never hardcoded or re-picked after seeing
results; red-team independently confirmed file mtimes show R was written to disk by sub_418
before sub_419's script existed).

## sub_419 — rescaled ensemble
`VMS_1m = [v × 1.730064 for v in {6,8,...,30}]` = [10.38, 13.84, 17.30, 20.76, 24.22, 27.68,
31.14, 34.60, 38.06, 41.52, 44.98, 48.44, 51.90]. Clamp bounds unchanged [40,1200] ticks;
fallback 179t unchanged; sigma window 1380 bars (time-matched) unchanged; execution/cost/
session-flatten rules unchanged from SMV2U.

**Before/after comparison (this is the finding):**

| arm | net $ | Sharpe | CDaR5 $ | maxDD $ | friction share | tgt chg/day | contracts (dev) |
|---|---:|---:|---:|---:|---:|---:|---:|
| SMV2U seq 390 (unscaled, ground truth) | −3,163.4 | −0.0184 | 52,924.4 | 66,744.6 | 1.0200 | 99.0 | 140,526 |
| **SMV2AE seq 419 (rescaled, R=1.7301)** | **77,747.9** | **0.4394** | **35,633.4** | **44,849.9** | **0.4695** | **44.4** | **59,824** |
| 3m incumbent (reference only) | 119,008.9 | 0.7092 | 27,161.8 | — | 0.3256 | — | 49,964 |
| delta (rescaled − unscaled) | +80,911.3 | +0.4577 | −17,291.0 | −21,894.7 | −0.5505 | −54.6 | −80,702 |

Full battery: Sortino 0.7352, Calmar 0.3835, worst day −$27,211.3, worst month −$19,914.1,
top10-day sum $116,688.1, positive-day fraction 40.1%, longest time-underwater 170 days,
n_target_changes 50,598.

Bonus mechanism check (INFERENCE, not spec-required): clamp-bind rate — unscaled 0.17%
lower/0.30% upper; rescaled 0.006% lower/3.78% upper. In both cases >96% of bars are governed
by `VolMult × sigma`, not the clamp — the improvement traces to the multiplier/sigma product
moving into a better-calibrated range (turnover roughly halved, 99.0→44.4 target-changes/day),
not to clamp relief.

## screen_gate verdict
Rule (frozen in spec, not chosen after seeing results): PASS-SCREEN if standalone Sharpe > 0
AND friction_share < 0.60. **Sharpe 0.4394 > 0, friction share 0.4695 < 0.60 → PASS-SCREEN**,
with a comfortable margin on both legs (not borderline). This queues an R2_CONFIRMATION spec
(full bootstrap/LOYO/old-regime/portfolio-contribution battery, SMV2T-style) for a later wave
— **this wave does not attempt or claim promotion.**

## Honest scope limits
- The rescaled arm still trails the 3m incumbent on every headline metric (net, Sharpe, CDaR5,
  friction share). No adoption/promotion claim is made here.
- Not tested (deferred to the queued R2_CONFIRMATION): bootstrap significance, LOYO robustness,
  portfolio-level (blend vs B-MOM) contribution, right-tail retention, old-regime behavior.
  PASS-SCREEN means a confirmatory battery is warranted, not that the arm would survive one.
- No data ≥2026-06-01 read anywhere (dev window identical to SMV2U).

## Red-team disposition
Verdict: **CONFIRMED**. Every number (scale-ratio table/meta, rescaled-ensemble metrics,
friction share, before/after comparison, screen-gate JSON, and the bonus clamp-bind aside) was
independently re-derived from raw/cached inputs by red-team and matched — in most cases
byte-for-byte — the committed outputs. The R-selection rule was genuinely pre-registered
(confirmed via file mtimes) rather than picked post-hoc; the screen threshold came from the
frozen spec; the portfolio/old-regime layer was correctly and explicitly excluded from this
run's claims rather than silently assumed; the executor code was genuinely reused (same import
path, same friction formula as SMV2U) rather than reimplemented. The only deviation from the
spec's letter was this missing REPORT.md file (a tooling-constraint artifact, now corrected by
this write) — no numeric or methodological correction was required.

## Files
`out/scale_ratio.csv`, `out/scale_ratio_meta.json`, `out/rescaled_ensemble.csv`,
`out/friction_share.csv`, `out/comparison_vs_smv2u.csv`, `out/screen_gate_verdict.json`.
Code: `step1_scale_measurement.py` (sub_418), `step2_rescaled_ensemble.py` (sub_419).
