# SMV2AD_VOLMULT_CEILING — REPORT

_Frozen spec: `runs/SMV2AD_VOLMULT_CEILING/spec.yaml` (committed 2b2f88a before any read).
Authored by the orchestrator from the execution agent's structured output — the subagent's
Write tool refused a direct REPORT.md write (same restriction seen on prior runs); every
number below traces to a committed `out/` artifact, independently reproduced by red-team
(verdict: CONFIRMED-with-corrections, both corrections applied below)._

seq [415, 416, 417]. class R1_FAMILY_TEST + DIAGNOSTIC. Dev window 2022-01-03 → 2026-05-29
(1,139 sessions, identical to SMV2R/SMV2T/SMV2U). Simulator: `src/analytics/sm01_solarsim.py`
`member_states()`/`member_trades()`/`e10_target()`/E10 MNQ executor, **UNMODIFIED** except the
explicit `smax_ticks` sweep and member-list changes the spec calls for. Step-0 integrity check:
the committed simulator reproduces the SM01 dev substrate's `vote_pend` on **100.00%** of
519,714 3-min bars and the committed `e10_daily_py.csv` to **1.8e-12 $** max deviation for the
1200t/13-member control — full parity, independently re-derived by red-team to max|dev|=0.0.

## Motivation (from spec)
SMV2R sub_381 found the 1200-tick/300pt upper clamp on the slowest member (VolMult=30) binds
10.93% of dev bars overall but is sharply regime-concentrated (9.83%/0.16%/3.93%/18.26%/39.21%
across 2022/2023/2024/2025/Jan–May 2026) — more binding right now than any full historical
year on file. This spec asks: does unclamping the existing slow member help (sub_415), and
does adding a genuinely slower cohort beyond VolMult=30 help (sub_416)?

## sub_415 — ceiling sweep (4 arms, 13-member VMS unchanged, smax_ticks varied)

| arm | smax(t) | net $ | Sharpe | maxDD $ | CDaR₀.₉₅ $ | top10-day $ | turnover %bars | vm30 %@ceiling | retention vs control top10 | CEILING-CANDIDATE |
|---|---|---|---|---|---|---|---|---|---|---|
| control | 1200 | 119,009 | 0.709 | 40,208 | 27,162 | 117,986 | 7.236 | 10.93 | 100.0% | — |
| challenger | 1600 | 128,802 | 0.750 | 44,461 | 28,492 | 125,516 | 7.256 | 3.22 | 96.2% | **No** |
| challenger | 2000 | 133,018 | 0.799 | 44,211 | 28,415 | 120,491 | 7.259 | 1.08 | 94.4% | **No** |
| challenger | 2400 | 145,071 | 0.863 | 44,272 | 28,447 | 124,103 | 7.260 | 0.57 | 93.4% | **No** |

Diminishing-returns check: raising the ceiling genuinely relieves the binding mechanically
(vm30 %-bars-at-ceiling falls 10.93%→3.22%→1.08%→0.57%) — it does not blow past 2400t the way
it blows past 1200t.

**Verdict rule** (Sharpe AND CDaR₀.₉₅ improve, top-10-day retention ≥95%): **zero arms
qualify**. Sharpe improves monotonically at every ceiling raise, but CDaR₀.₉₅ (tail drawdown
risk) gets **worse in all three challengers** (+4.9% to +5.0% vs control) — the unclamped slow
member produces rarer, larger trend trades that fatten tail-drawdown even as they lift average
risk-adjusted return. Only 1600t clears the 95% top-10-day retention bar; 2000t/2400t fall
short. **CEILING-CANDIDATEs: none.**

## sub_416 — extended cohort (2 arms; smax_ticks = 2000t disclosed default)

**HYPOTHESIS / interpretive call (disclosed)**: sub_415 produced zero CEILING-CANDIDATEs, so
per the spec's own fallback instruction this sub-test uses 2000t (the mid-sweep value) applied
to the entire member set in each arm — an interpretive choice, not a re-optimization.

| arm | n_members | smax(t) | net $ | Sharpe | maxDD $ | CDaR₀.₉₅ $ | top10-day $ | turnover %bars | retention vs control top10 | EXTENSION-CANDIDATE |
|---|---|---|---|---|---|---|---|---|---|---|
| control (1200t/13) | 13 | 1200 | 119,009 | 0.709 | 40,208 | 27,162 | 117,986 | 7.236 | 100.0% | — |
| arm_ADD (13+5 slow, 18 members) | 18 | 2000 | 103,723 | 0.698 | 37,991 | 24,783 | 115,478 | 6.112 | 85.4% | **No** |
| arm_REPLACE (drop 5 fast, +5 slow, 13 members) | 13 | 2000 | 108,424 | 0.664 | 38,686 | 27,885 | 126,343 | 2.350 | 84.9% | **No** |

Both arms underperform the true incumbent's standalone Sharpe outright, which alone fails the
AND rule regardless of CDaR. **EXTENSION-CANDIDATEs: none.**

**Red-team correction (applied here)**: the execution agent's original prose described the new
slowest member (VolMult=50 at smax=2000t) sitting at its ceiling **10.93% of dev bars** — the
"numerically identical" value to vm30's original 1200t/VolMult=30 bind rate — and framed this
as a reproduced empirical phenomenon. Red-team confirmed the number is correct but is **not**
an independent empirical finding: `1200/30 = 2000/50 = 40`, so the two clamp-bind conditions
are the same distribution evaluated at the same effective threshold-per-sigma ratio by
construction of the chosen parameters (2000t was picked as "mid-sweep default," and 50 happens
to preserve the ratio). It is a correct but **tautological** restatement, not a fresh discovery
that "slower cohorts reproduce the same problem" — that broader claim is not established by
this number alone. Treat as a mechanical note, not as independent evidence.

## Portfolio blend (DAYONLY_DUAL6040 60/40, per sub_415/sub_416 arm)

Construction reused **verbatim** from `runs/SMV2T_NOFAST_R2/gate_AD.py`+`gate_E.py` (red-team
independently confirmed byte-identical scalars: 1.25/0.5/0.9026/±13 clip, B-MOM leg unchanged).
Champion reconstruction cross-check: the 1200t-control rebuild reproduces the incumbent
`60_40` curve exactly (d_Sharpe=0.0, d_CDaR=0.0, matched to 1e-10 by red-team).

Champion (incumbent) portfolio: net $194,416 | Sharpe 1.2642 | CDaR5 $14,322 | maxDD $18,132.

| sub-test | arm | net $ | Sharpe | CDaR5 $ | maxDD $ | d_Sharpe | d_CDaR | beats champion (both) |
|---|---|---|---|---|---|---|---|---|
| 415 | smax_1600t | 200,411 | 1.2674 | 16,622 | 22,176 | +0.0031 | −2,300 | No |
| 415 | smax_2000t | 200,544 | 1.3182 | 14,832 | 22,060 | +0.0539 | −510 | No |
| 415 | smax_2400t | 207,271 | 1.3527 | 14,762 | 21,940 | +0.0885 | −440 | No |
| 416 | arm_ADD | 170,476 | 1.2695 | 13,674 | 18,782 | +0.0053 | **+648** | **Yes** |
| 416 | arm_REPLACE | 187,104 | 1.2534 | 15,445 | 22,964 | −0.0108 | −1,122 | No |

**Flagged observation (does not change the formal verdict)**: arm_ADD's portfolio blend beats
the champion on both Sharpe and CDaR, even though arm_ADD failed the sub_416 *standalone*
verdict rule. The spec's verdict rule is explicitly standalone-Solar-leg-based; per that rule
arm_ADD is correctly **not** a CANDIDATE this wave. Red-team specifically checked and confirmed
this was not used to override the frozen rule. Worth carrying forward as context only if this
lead is revisited under a new mechanism (an 18-member, 6.11%-turnover core that individually
underperforms but diversifies well against B-MOM).

## sub_417 — old-regime screen (DIAGNOSTIC, non-adoption)
Zero arms qualified in sub_415 or sub_416, so per spec ("for EVERY arm... that qualifies") this
screen is explicitly **N/A this wave** — `out/old_regime_screen.csv` records
`status=NONE_QUALIFIED` with full reasoning, not a silent skip. The SM06 2006–2021 rebuild
machinery (SMV2T gate-C convention, floor net ≥ incumbent −$10k / maxDD ≤1.25× incumbent) is
retained parameterized in `src/sub417_old_regime.py::CANDIDATE_SCREEN()` for a future wave.

## kill_or_keep

**Result: zero arms qualified (0/3 sub_415, 0/2 sub_416).**

**VERDICT: CONFIRMED-OPTIMAL-IN-RANGE.** The 1200-tick/300pt clamp ceiling and the VolMult
6–30 member range are confirmed optimal within this design space (a fixed higher ceiling, or a
fixed-parameter slower cohort). This lead is closed per house convention — no third bite at a
*fixed*-ceiling/cohort extension without a genuinely new mechanism. (Note: this does NOT close
the *adaptive*-ceiling idea ranked #1 in the same-day mechanism-expansion pass — that is a
structurally different proposal, a percentile/rolling cap rather than a fixed higher constant,
and remains open.)

**Why it fails, precisely**: raising the ceiling mechanically relieves the clamp bind and lifts
Sharpe monotonically, standalone and at the portfolio level — but every ceiling raise
simultaneously fattens tail drawdown risk (CDaR₀.₉₅), because the unclamped slow member
produces rarer, larger trend trades. Adding an even-slower cohort (sub_416) does not sidestep
this trade-off: both cohort arms underperform the incumbent's own standalone Sharpe outright.
The 1200t/VMS-6-30 design is a genuine local optimum on the Sharpe/CDaR frontier tested here,
not an arbitrary historical accident.

## Red-team disposition
Verdict: **CONFIRMED-with-corrections**. All numeric claims, verdict-rule arithmetic, the
zero-candidates conclusion, the conditional skip of sub_417, and the code-reuse claims for the
old-regime/portfolio-blend machinery independently reproduced by red-team (in several cases
bit-exact). No evidence of post-hoc threshold selection — the governing rule was frozen in
spec.yaml before any results existed. Two corrections applied above: (1) this REPORT.md itself
(was missing from the run dir, a tooling-constraint artifact, now written), (2) the vm50
ceiling-bind-rate framing corrected from "reproduced empirical phenomenon" to "algebraic
identity by construction of the chosen ratio-matched parameters."

## Files
`out/ceiling_sweep.csv`, `out/extended_cohort.csv`, `out/old_regime_screen.csv`,
`out/portfolio_blend.csv` (+ `portfolio_blend_415.csv`/`_416.csv`), `out/gates.csv`,
`out/step0_verify.json`, `out/sub415_verdict.json`, `out/sub416_verdict.json`,
`out/daily_ceiling_*.csv`, `out/daily_cohort_*.csv`, `out/portfolio_curves_415.csv`,
`out/portfolio_curves_416.csv`, `out/cache_control_1200.npz`, `out/e10_daily_dev_control_1200.csv`,
`out/sigma460_dev.npy`. Code: `src/common.py`, `src/step0_verify.py`, `src/sub415_ceiling.py`,
`src/sub416_cohort.py`, `src/sub417_old_regime.py`, `src/finalize.py`.
