# G2_F11_MC54LEG2_VOLFORECAST_20260906 — REPORT

**Card:** MC-54 leg 2 (frozen-profile OOS vol forecast) · **Ledger trial:** G00052
**Stage:** DIAGNOSTIC (RISK-SPECIFICATION lane; not alpha, not a strategy)
**Seed:** 20260906 · **Program:** `src/run_mc54leg2.py` · **Program-printed gates:** `out/gate_table.txt`

## VERDICT: NOT-IDENTIFIED

The preregistered G5 rule fired: **VIF(deseason_early) = 92.86 > 10** (corr(raw_early,
deseason_early) = **0.9946**). Per spec, "the incremental term is not separately identified and
the verdict is NOT-IDENTIFIED, not PASS/FAIL." The G3 arithmetic on its own passed — HAC(5)
t = 3.842, p = 0.0001, OOS incremental adjR² = 0.01855 (> MDE 0.00776; bootstrap 95 % CI
[0.00285, 0.04587] excludes 0) — but with a fixed one-hour window, removing the deterministic
diurnal clock is almost a monotone reweighting of the same 60 squared returns, so "raw" and
"deseasonalized" first-hour logRV are the same regressor to 99.5 %. The nested design cannot
attribute the increment to the *state* component specifically. Decision rule → **FAILURE_MEMORY
row** (what dies: *this identification design*; the anti-rescue scope "deseasonalized first-hour
vol as an incremental RV forecaster on NQ" is NOT cleanly closed by a NOT-IDENTIFIED — the spec
reserves closure for a NULL, and this is neither a NULL nor a PASS).

## G1 sentence (as printed by the program)

> G1 SEMANTIC: population = TEST-era (2025-01-01..2026-05-29) NQ RTH sessions (N=349); event =
> whether DESEASONALIZED first-hour log RV adds forecast power for rest-of-day (10:30-16:00)
> log RV beyond prior-day log RV and RAW first-hour log RV (partial contribution in a nested
> HAC(5) OLS).

## Numbers (all DISCOVERY_CONSUMED)

| quantity | value |
|---|---|
| N (TEST sessions used) | 349 (dropped 39/1030 incomplete era-wide, 0 zero-RV) |
| TRAIN sessions (profile freeze) | 668, 2022-06-01..2024-12-31, no smoothing |
| RAW model R² / adjR² | 0.5972 / 0.5949 |
| FULL model R² / adjR² | 0.6169 / 0.6135 |
| **MDE (80 % power), printed BEFORE observed** | ΔR² 0.00886 (adjusted units **0.00776**) |
| Observed OOS incremental adjR² | **0.01855**, bootstrap 95 % CI [0.00285, 0.04587] |
| deseason_early HAC(5) t / p | **3.842 / 0.0001** ; β = 1.548, CI [0.708, 2.287] |
| corr(raw_early, deseason_early) / VIF | **0.9946 / 92.86** → NOT-IDENTIFIED |

Gate table (program-printed, GATE/SPEC/OBSERVED/PASS-FAIL): `out/gate_table.txt` — G0 PASS,
G1 PASS, G2 PASS (barrier line before observed), G3 PASS, G4 PASS (n/a, G3 passed),
G5 **NOT-IDENTIFIED**. Full regressions: `out/regression_summary.txt`; per-session rows:
`out/sessions_test.csv`.

## Seal / era

G0 hard assert PASSED inside the program: every bar entering any computation is
2022-06-01 09:31 ET .. 2026-05-29 16:00 ET; regression rows 2025-01-02..2026-05-29. No pre-2022-06
data touched, nothing ≥ 2026-08-01 read (substrate ends 2026-05-29).

## Hand-checked session: 2025-03-05

Independent recomputation (explicit per-bar loop, loop-rebuilt frozen profile, separate code
path from the vectorized program):

| quantity | hand value | program row | match |
|---|---|---|---|
| n_fh / n_rod | 60 / 330 | 60 / 330 | exact |
| raw_early = log(1.107219e-04) | −9.108489 | −9.10848862195474 | <1e−9 |
| deseason_early = log(2.371870e+02) | 5.468849 | 5.468848788828856 | <1e−9 |
| y = log(rod RV 1.752174e-04) | −8.649483 | −8.649482854385496 | <1e−9 |
| prior_day_logRV (2025-03-04 full-day) | −8.107537 | −8.10753737001702 | <1e−9 |

## Implementation choices (recorded in the program header before the OOS read)

End-stamped bars → RTH stamps (09:30, 16:00]; first hour = stamps 09:31..10:30; rest-of-day =
10:31..16:00. First RTH bar's return = its own open→close (no overnight contamination); later
bars close-to-close. Diurnal profile NOT smoothed. Completeness filter ≥54/60 fh and ≥297/330
rod bars. HAC = Newey-West maxlags 5, z-based p. MDE from N and RAW model only:
λ=(z₀.₉₇₅+z₀.₈₀)²=7.849, f²=λ/N, converted to adjusted units. Stationary circular block
bootstrap, geometric mean block 10 sessions, B=2000, `default_rng(20260906)`.

## What this buys

The mechanism question ("does the stochastic state component of early vol forecast the rest of
the day beyond raw?") is not answerable with a *fixed-window* deseasonalization: the transform
is too close to affine in logs. A future leg would need a design where the clock and the state
separate — e.g., varying-window or minute-resolution functional predictors — and that is a NEW
spec, not a rescue of this one. No sizing overlay is licensed by this run.

**Evidence status: DISCOVERY_CONSUMED (every number above).**
