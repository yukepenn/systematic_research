# SMV2N_WINDFALL_POLICY — R2 of the C-P7 windfall pre-test (seq 372–374)

**Verdict: C-P7 KILLED AT POLICY LEVEL.** The center cell (s = 0.8) fails Gate 1 (TUW does not
improve: 133 → 133) and Gate 2 (neither the CDaR_0.95 nor the TUW improvement clears
placebo median + 2×IQR). The kill is plateau-wide: s = 0.7 and s = 0.9 fail the identical
gates. Gates 3 (LOYO), 4 (RTC) and 5 (net retention) pass in every cell — the **information
result stands** (post-windfall sessions remain bad sessions) but the frozen de-risking policy
does not beat random de-risking of the same total duration. Per spec: recorded, killed.

- Spec: `spec.yaml` (frozen at 58dc2d2). Parent: SMV2I seq 365 (pre-test PASSED p=0.0012 fwd10,
  de-clustered N=11 — LOW POWER PREREGISTERED).
- Curve: `runs/SMV2M_MASTER_BUILD/out/twin_daily.csv`, truncated to sessions <= 2026-05-31.
  No data >= 2026-08-01 was read or used anywhere in this run.
- Executor: `smv2n.py`. Artifacts: `out/policy_cells.csv`, `out/placebo.csv`,
  `out/chronology.csv`, plus `out/repro_check.csv`, `out/triggers.csv`, `out/vol_suspension.csv`,
  `out/policy_daily.csv`, `out/extras.csv`. Every number below is from these artifacts.

## 0. Reproduction gate — PASS (FACT)

Dev truncation of twin_daily.csv reproduces the committed `twin_battery.csv` MASTER_TWIN_dev row
exactly (`out/repro_check.csv`): n=1139 sessions (2022-01-03 → 2026-05-29), net $179,288.70
(|Δ| < 1e-6), Sharpe 1.185764, CDaR_0.95 $14,151.47, longest TUW 133, maxDD $16,821.20.

## 1. Constructions (FACT — frozen form, no threshold search)

- **Trigger** (identical code path to pre-test `step4_cp7.py`): r5 = 5-session rolling sum of
  twin daily PnL; sigma = expanding std (ddof=1, min_periods=20) of r5 through t-1 (`.shift(1)`,
  strictly prior); burn-in >= 365 calendar days from first session; event at close of t iff
  r5_t > +2.5*sigma_t (zero-centered). Scale sessions t+1..t+5 by s; retrigger extends (union
  of windows); no compounding.
- **Vol-spike suspension** (construction stated per spec): session closes = close of the last
  3-min bar of each session from `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` via
  `sm01_solarsim.load_bars_3m` (sessions <= 2026-05-31; calendar asserted identical to the twin
  calendar); r_t = ln(C_t/C_{t-1}); vol20 = rolling 20-day std (ddof=1); percentile = expanding
  percentile rank (inclusive, 100*frac<=) of vol20 over all prior valid values. Session u is
  **not scaled** when the percentile at the close of session u-1 exceeds 85 (causal: exposure
  for u is set with information through u-1; the spec is silent on the lag, causality forces it).
  92 of 1139 sessions sat above the 85th percentile (`out/extras.csv`).
- **Triggers found**: 28 trigger days, **de-clustered count 11** (clusters split at gaps > 5
  trading days) — honestly low, same order as the pre-test's N=11; first 2023-08-24, last
  2026-04-03; clusters by year 2023:1, 2024:2, 2025:6, 2026:2. Designed window days 74;
  12 suspended by the vol rule; **62 sessions actually scaled** in 10 contiguous runs
  (lengths 5,3,5,9,5,7,5,5,11,7) (`out/triggers.csv`, `out/policy_cells.csv`).

## 2. Seq 372 — policy cells (`out/policy_cells.csv`)

| metric (dev, 1139 d) | unscaled | s=0.7 | s=0.8 (center) | s=0.9 |
|---|---|---|---|---|
| Net $ | 179,288.70 | 183,438.51 | 182,055.24 | 180,671.97 |
| Net retention | — | 1.0231 | 1.0154 | 1.0077 |
| CDaR_0.95 $ | 14,151.47 | 13,882.56 | 13,930.98 | 14,019.92 |
| dCDaR (improvement) | — | 268.91 | 220.50 | 131.55 |
| Longest TUW (days) | 133 | 133 | 133 | 133 |
| maxDD $ | 16,821.20 | 16,821.20 | 16,821.20 | 16,821.20 |
| Sharpe | 1.1858 | 1.2525 | 1.2312 | 1.2089 |
| RTC (top-decile, k=114) | — | 0.9714 | 0.9810 | 0.9905 |

FACT: the 62 scaled sessions sum to **-$13,832.70** (mean -$223.11/day vs +$157.41 all-day
mean, `out/extras.csv`) — so de-risking them *adds* net (retention > 1) and raises Sharpe.
Direction fully consistent with the pre-test. maxDD and the longest underwater spell are
untouched by the policy in every cell.

## 3. Seq 373 — placebo battery (`out/placebo.csv`)

200 paths, seeds 1..200, each placing the same number (10) and durations (62 days total) of
scaling windows at uniform-random positions in the burn-in-eligible region; windows overlap
neither each other nor any real designed-window day (all 200 paths feasible; no suspension
applied to placebos — their durations already equal the real post-suspension scaled runs).

| s | real dCDaR | placebo median | placebo IQR | gate threshold (med+2*IQR) | real pctl of placebo | pass |
|---|---|---|---|---|---|---|
| 0.7 | 268.91 | 14.98 | 413.50 | 841.98 | 73.0 | **NO** |
| 0.8 | 220.50 | 16.31 | 276.01 | 568.33 | 76.5 | **NO** |
| 0.9 | 131.55 | 11.41 | 153.20 | 317.82 | 77.5 | **NO** |

TUW: real dTUW = 0 in all cells; placebo median 0, IQR 1–2 → thresholds 2–4; 29–44% of *random*
paths improve TUW while the real policy improves it by zero. **Fails in all cells.**

INFERENCE: random 62-day de-risking of this curve produces CDaR improvements with an IQR
(276–414) larger than the real policy's entire effect (132–269). The real effect sits at only
the ~73–78th placebo percentile — windfall timing adds nothing distinguishable from generic
exposure reduction at the pre-registered 2-IQR specificity bar.

## 4. Seq 374 — chronology battery (`out/chronology.csv`)

dSharpe (policy - unscaled), gate anchored on the full-sample sign (+):

- s=0.8: full +0.0454; LOYO: -2022 +0.0618, -2023 +0.0520, -2024 +0.0448, -2025 +0.0235,
  -2026 +0.0437 → **5/5 same sign, leave-2022-out keeps sign — PASS** (also 5/5 at s=0.7, 0.9).
- Per-year diagnostic (not the gate): 2022 exactly 0 (policy inactive pre-burn-in), 2023 +0.009,
  2024 +0.050, 2025 +0.102, 2026 +0.035 — positive in all four active years.

## 5. Gate scorecard and verdict

| gate (all required) | s=0.7 | s=0.8 (decides) | s=0.9 |
|---|---|---|---|
| 1a. CDaR_0.95 improves | PASS | PASS | PASS |
| 1b. TUW improves | **FAIL** (133→133) | **FAIL** (133→133) | **FAIL** (133→133) |
| 2a. dCDaR > placebo med+2*IQR | **FAIL** (220 needed >568 at center) | **FAIL** | **FAIL** |
| 2b. dTUW > placebo med+2*IQR | **FAIL** (0 > 2) | **FAIL** | **FAIL** |
| 3. LOYO >=4/5 + leave-2022-out | PASS (5/5) | PASS (5/5) | PASS (5/5) |
| 4. RTC >= 0.97 | PASS (0.9714, marginal) | PASS (0.9810) | PASS (0.9905) |
| 5. Net retention >= 0.97 | PASS (1.0231) | PASS (1.0154) | PASS (1.0077) |

**FACT: center cell s=0.8 fails gates 1b, 2a, 2b → C-P7 KILLED at the policy level.** The
plateau read confirms the kill is not a cell-boundary artifact: all three cells fail the same
three gates and pass the same four.

## 6. What stands, honestly labeled

- FACT: on the dev twin curve, the 62 post-windfall scaled sessions lost $13,833 in aggregate;
  scaling them by 0.8 would have added ~$2,767 net, +0.045 Sharpe, -$220 CDaR_0.95.
- INFERENCE: the C-P7 *information* result (post-windfall sessions are below-average) survives
  its second look — sign-stable across all LOYO folds and all active years, and it passes the
  net-retention and RTC floors. What died is the *policy*: with only 11 de-clustered clusters
  the risk-reduction it buys is statistically indistinguishable from de-risking random windows
  of the same total duration, and it never touches the curve's dominant risk features (maxDD,
  longest TUW).
- HYPOTHESIS (not tested here, no action): the windfall effect is a mean effect on ~5% of days,
  too small and too sparse to move tail-risk functionals; any future revival would need either
  more history or a different objective — and would be a NEW pre-registered test, not a re-read.

## 7. Caveats / ambiguity resolutions (all fixed before results were read)

- LOW POWER PREREGISTERED (spec parent line): 11 de-clustered clusters; reported honestly.
- Suspension lag: spec is silent; day u uses the vol percentile at close of u-1 (causality).
  Suspension is day-wise (a suspended day inside a window is simply not scaled).
- Placebo durations = the real policy's *actually-scaled* runs (post-suspension), placement
  excludes the full designed-window union (superset) — the conservative choice on both sides.
- Gate 2 was applied to BOTH improvement metrics (the spec's "improvement" follows Gate 1's
  "CDaR and TUW both"); note the gate outcome is unchanged under the laxer CDaR-only reading.
- TUW tie (133 = 133) counted as "not improved" — mechanical reading of "improve".
- twin_daily.csv contains June–July 2026 rows (CONSUMED); they were truncated before any
  computation and no session after 2026-05-29 entered any statistic in this run.
