# Statistical red team — SMV2N_WINDFALL_POLICY (seq 372–374) — V4 §48 mandatory pass

Reviewer: independent red-team agent, 2026-08-08. Verdict: **CONFIRMED**.

## 1. Spec letter-exactness — PASS

- spec.yaml frozen in commit 58dc2d2 (2026-08-08 13:14:29 ET), byte-identical to the working
  copy (`git diff 58dc2d2 -- spec.yaml` empty). out/ artifacts written 13:22–13:23, REPORT.md
  13:26 — spec frozen before any result was read.
- Cells: exactly {0.7, 0.8, 0.9}, 3 rows in policy_cells.csv, no extra cells, center 0.8
  decides (smv2n.py line 345). No threshold search on 2.5σ / 5d / pctl-85 — all hard-coded.
- Trigger form verified IDENTICAL to the parent pre-test (SMV2I step4_cp7.py): zero-centered
  r5 > 2.5·σ, σ = expanding std (ddof=1, min_periods=20) of r5 through t−1 via .shift(1),
  burn-in ≥ 365 calendar days. The spec's "expanding mean/std" phrasing matches the pre-test's
  literal zero-centered reading; no_moves honored.
- All 5 spec gates implemented as written; gate 2 applied to BOTH CDaR and TUW (the stricter of
  the two defensible readings; outcome identical under the laxer CDaR-only reading since 1b and
  2a fail independently). Kill rule "any gate fails" applied to the center cell as specified.
- Spec-silent choices (suspension lag, placebo durations = post-suspension scaled runs, LOYO
  anchor, TUW tie) are documented in REPORT §7 and in the smv2n.py docstring, fixed before
  results; none is outcome-determining (see §4 below).

## 2. Independent recomputation — PASS (exact, zero mismatches)

Re-implemented from scratch (own metric code, own bars parse without load_bars_3m, own
trigger/window/suspension logic) and compared against out/ artifacts. ~120 checks, 0 failures:

- Repro gate: n=1139, net $179,288.70, Sharpe 1.185764, CDaR_0.95 $14,151.47, TUW 133,
  maxDD $16,821.20 — all match twin_battery.csv MASTER_TWIN_dev within stated tolerances.
- Triggers: 28 days, 11 de-clustered clusters (gap > 5), first 2023-08-24, last 2026-04-03,
  clusters/year 2023:1 2024:2 2025:6 2026:2 — all reproduce; triggers.csv dates match exactly.
- Windows: 74 designed days, 12 suspended, 62 scaled in 10 runs [5,3,5,9,5,7,5,5,11,7] — exact.
- Vol series: independent last-bar-per-session parse of nq_3m_2022_2026.csv reproduces closes,
  vol20, expanding inclusive percentile (max |Δ| 1.4e-14) and all suspension flags; 92 sessions
  with pctl > 85 confirmed; session calendar identical to twin calendar.
- Policy cells (all 3): net, retention (1.0231/1.0154/1.0077), CDaR_0.95, dCDaR
  (268.91/220.50/131.55), TUW (133 in every cell), maxDD (unchanged), Sharpe, RTC
  (0.9714/0.9810/0.9905) — all reproduce to 1e-6 or better.
- Placebo battery: 200/200 feasible, all 62 days; medians/IQRs/thresholds reproduce
  (841.98/568.33/317.82); real percentiles 73.0/76.5/77.5 confirmed (strict and inclusive
  identical); 7 spot seeds (1,2,3,4,5,100,200) independently regenerated from the documented
  algorithm — dCDaR values match to 1e-6 and no placebo window overlaps any designed-window day.
- Chronology: all full/LOYO dSharpe values reproduce to 1e-9; 5/5 sign agreement at every s
  including leave-2022-out (+0.0618 at s=0.8); per-year diagnostic 0 / +0.009 / +0.050 /
  +0.102 / +0.035 confirmed.
- Scaled-day facts: sum −$13,832.70, mean −$223.11/day vs +$157.41 all-day — confirmed.
- Gate scorecard re-adjudicated independently: 1a P / 1b F / 2a F / 2b F / 3 P / 4 P / 5 P in
  every cell → KILL at policy level is the mechanically correct verdict under the frozen spec.

## 3. Lookahead / leakage scan — CLEAN

- σ strictly prior (.shift(1)); trigger at close of t scales only t+1..t+5; suspension of day u
  uses the vol percentile at close of u−1 (causal); expanding percentile at t includes vol20_t,
  which is known at close of t and only ever applied to t+1 — no contemporaneous use.
- RTC uses full-sample top-decile of the UNSCALED curve — a pre-registered diagnostic gate, not
  a trading decision; no leakage. Placebo placement uses knowledge of real windows — null
  construction, appropriate.
- Data hygiene: twin_daily.csv max 2026-07-31, bars max 2026-07-31 16:57 — no data
  ≥ 2026-08-01 exists in either input; both truncated to ≤ 2026-05-31 before any computation
  (policy_daily max session 2026-05-29 verified). CONSUMED June–July 2026 rows never entered
  any statistic. VIRGIN window untouched.

## 4. Adversarial robustness probe (red-team addition, not a finding)

The one spec-silent choice with any conceivable bias is that placebo windows may land on
vol-suspended days the real policy avoids, potentially inflating placebo dCDaR spread and
making gate 2 unfairly hard. Re-ran the 200-path battery restricting placebos to non-suspended
days: IQR shrinks ~35% (s=0.8: 276→178, threshold 568→356) but real dCDaR 220.50 STILL fails
at every s (real percentile rises only to 82.5–88.5, far from the ~med+2·IQR bar), and gate 1b
(TUW 133→133) fails under any placebo construction whatsoever. **The kill is not an artifact of
the placebo design.**

## 5. Report language and scope — PASS

- FACT / INFERENCE / HYPOTHESIS labels used correctly; the kill is recorded as a kill with no
  hedging; the surviving information result is labeled INFERENCE with the power caveat
  (N=11 de-clustered, LOW POWER PREREGISTERED) restated, and the revival path is explicitly
  gated on a NEW pre-registered test ("not a re-read") — no adoption language, no policy
  promotion of the surviving inference. No BLOCKED items claimed (repro gate passed; code
  would have hard-exited otherwise).
- Exec-agent summary numbers cross-checked against artifacts — all match.

## Verdict

**CONFIRMED.** Letter-exact to the frozen spec, every recomputed number matches exactly,
no lookahead, kill honestly recorded, and the kill is robust to the only ambiguous
methodological choice. C-P7 KILLED at policy level stands; the information result stands as
an inference only.
