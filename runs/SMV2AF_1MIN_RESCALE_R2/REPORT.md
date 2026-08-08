# SMV2AF_1MIN_RESCALE_R2 — REPORT

_Frozen spec: `runs/SMV2AF_1MIN_RESCALE_R2/spec.yaml`. seq [420,421,422,423]. class
R2_CONFIRMATION on SMV2AE seq 419's PASS-SCREEN result (rescaled 1-minute VolMult ensemble,
R=1.730064). Authored by the orchestrator from the execution agent's structured output —
subagent Write tool refused REPORT.md again this wave; every number below independently
reproduced bit-for-bit or arithmetic-exact by red-team (verdict: CONFIRMED-with-corrections,
one factual correction applied below, plus this file itself resolving the missing-report gap)._

## Object under test
The exact rescaled construction from SMV2AE seq 419: `VMS_1m = VMS_3m × 1.730064` (13 members,
R reused verbatim, never re-measured), clamp [40,1200] ticks unchanged, sigma window 1380 bars
(time-matched ≈23h), MNQ E10 executor, session flatten.

## Step 0 — reproduction check
Recomputed the dev-period rescaled arm's daily PnL curve from the identical code path SMV2AE
used (SMV2AE never persisted the daily curve, only the aggregate row). Reproduced bit-for-bit:
net $77,747.90, Sharpe 0.4393655569 (both |dev|=0 vs SMV2AE's committed numbers). Red-team
independently re-derived the same values from `dev_daily_curves.csv`, exact match.

## Gate A — dev significance (bootstrap)
Paired moving-block bootstrap (block=5 daily, B=10,000, seed=20260808) on the rescaled arm's
own daily PnL.

| stat | value |
|---|---:|
| point Sharpe | 0.4394 |
| bootstrap Sharpe p5 / p50 / p95 | −0.2439 / 0.4468 / 1.1136 |
| **P(Sharpe>0)** | **0.853** |
| gate bar | ≥0.85 |
| **verdict** | **PASS — thin margin (0.003 above bar)** |

Disclosed (not a gate criterion): Newey-West t-stat (lag 5) on the raw daily mean = 1.084 —
well short of conventional significance, consistent with a real-but-fragile pass, not a robust
one. Red-team independently reran the identical bootstrap from scratch: exact match, bar was
pre-specified in spec.yaml, not adjusted post-hoc.

## Gate B — chronology (LOYO + fit/eval)

| year | n_days | net $ | Sharpe | sign |
|---|---:|---:|---:|---:|
| 2022 | 258 | 30,898.6 | 0.7755 | + |
| 2023 | 258 | −3,967.0 | −0.1673 | − |
| 2024 | 259 | 26,771.7 | 0.8728 | + |
| 2025 | 258 | 33,969.8 | 0.6173 | + |
| 2026 (partial) | 106 | −9,925.2 | −0.4902 | − |

LOYO same-sign: 3/5 years positive (0.600) — **below the ≥4/5 (0.80) bar → FAIL**.
Fit 2022-24 → eval 2025-26: fit Sharpe 0.558 ($53,703/775d); eval Sharpe 0.319 ($24,045/364d) —
point-positive → PASS on this leg alone. Gate B requires BOTH legs. **Verdict: FAIL** (LOYO is
the failing leg). Red-team confirmed this reproduces exactly and the AND-logic matches the
established SMV2T/SMV2W precedent verbatim — not a loosened or gate-shopped rule.

## Gate C — old regime (2006-2021)
**First step (per spec): verified data availability before attempting anything.** The
committed derived "SM06 hist substrate" (`vote_state_3m_hist.parquet`) is confirmed
3-minute-only — same wall SMV2W hit for 5-minute testing. But a **native 1-minute-resolution**
substrate also exists committed (`research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet`,
6,466,783 rows, 2006-2026) — the same raw file SM06's own hist build reads before resampling to
3-minute. Using it directly is not "deriving finer bars from coarser data" (SMV2W's genuinely
blocked case); it's using the native, finest-available resolution directly.

**Flagged interpretive call (disclosed)**: the spec's gate-C text anticipated a BLOCKED-BY-DATA
outcome by analogy to SMV2W. That analogy holds for the derived 3m substrate but not for the
native 1m file, which SMV2W's own spec never had access to test against (SMV2W's spec was
additionally scoped to dev-only data; SMV2AF's spec carries no such restriction). Judged
**NOT BLOCKED** and built the old-regime test rather than mechanically reporting BLOCKED against
available evidence. Red-team independently verified the factual predicate (file resolution,
provenance) is genuinely true and this is a defensible, fully-disclosed reading — not a
fabrication — while still flagging it as a debatable call for a human to bless or override. It
does not change the final decision either way (already CLOSED via gates A+B).

Construction: native 1-minute bars filtered to `time < 2022-01-01`, session-tagged via the same
gap-heuristic `sm01_solarsim.resample_3m()` uses internally, same rescaled VMS/clamp/sigma
window/executor as the dev-period construction. Session-calendar cross-check vs SM06's own 3m
hist calendar: 4,127/4,130 sessions matched (99.93%), 3 sessions diverge (not investigated
further, immaterial to the conclusion).

| metric | 1m rescaled (this run, 2006-2021) | 3m incumbent, SM06's own hist result |
|---|---:|---:|
| n_sessions | 4,127 | 4,110 (SM06's own reported figure, 20-day warmup-excluded) |
| net $ | **−20,582.9** | −8,970.0 |
| Sharpe | **−0.1189** | −0.0511 |
| maxDD (eod) | 61,512.0 | — |
| CDaR5 | 59,215.7 | — |
| friction_share | **1.142** (exceeds gross) | — |
| bootstrap P(Sharpe>0) | 0.306 | — |

**Red-team correction (applied here)**: the execution agent's original table paired SM06's
warmup-excluded net/Sharpe figures (net −$8,970.0/Sharpe −0.0511, n=4,110) with the RAW,
non-warmup-excluded session count (n=4,130). These come from different SM06 artifacts and
should not be paired as if from the same sample. Corrected pairing above uses n=4,110 (matching
the −$8,970.0/−0.0511 figures, per `SM06_SOLAR_HISTORY/out/result.json`'s own 20-day
warmup exclusion). For completeness: the alternative raw/non-excluded framing (n=4,130) gives
net −$10,017.4/Sharpe −0.0569 instead — either framing supports the identical substantive
conclusion below; this was a labeling inconsistency, not a result-changing error.

Per-era Sharpe (1m rescaled): 2006-09 −1.197, 2010-13 −1.123, 2014-17 −0.482, 2018-21 +0.348 —
negative in 3 of 4 eras.

**Gate C outcome (reported, not gated)**: the rescaled 1-minute construction is **not**
structurally validated on the old regime — it loses money over 2006-2021, underperforming even
the mediocre, already-REGIME_LOCAL 3m incumbent hist result under either sample framing, and
friction alone exceeds gross P&L. A genuinely new, informative negative finding.

## Gate D — diversification diagnostic (not pass/fail)

| scope | n_days | corr |
|---|---:|---:|
| full_dev | 1,139 | **0.897** |
| 2022 / 2023 / 2024 / 2025 / 2026 | — | 0.982 / 0.969 / 0.977 / 0.779 / 0.968 |

A priori expectation (disclosed before results): HIGH correlation, since both legs are the same
mechanism at different clocks on the same price series. **Confirmed** — 0.897 full-dev, well
above the pre-disclosed |corr|<0.5 low-correlation threshold.

Exploratory 50/50 equal-vol blend (verbatim `vm()` convention from
`runs/SMV2AD_VOLMULT_CEILING/src/common.py`):

| leg | net $ | Sharpe | CDaR5 $ |
|---|---:|---:|---:|
| 3m incumbent alone | 119,008.9 | 0.7092 | 27,161.8 |
| 1m rescaled alone | 77,747.9 | 0.4394 | 35,633.4 |
| 50/50 vol-matched blend | 98,953.7 | 0.5897 | 28,543.8 |

Blend beats neither Sharpe nor CDaR5 vs the 3m-only leg. Per spec: since correlation is HIGH
(not low) and the blend loses on both metrics, **no new portfolio-blend candidate is flagged
for R3**. Red-team independently rebuilt this blend and reproduced all three legs' numbers
exactly; threshold (0.5) was pre-disclosed in spec.yaml, not chosen post-hoc.

## Decision (per spec's frozen decision rule)
Gate A PASS (thin) / Gate B FAIL (LOYO) / Gate C reported-negative / Gate D reported-negative.
Per spec: **"If gates A or B FAIL → the PASS-SCREEN result is downgraded to NOISE-LEVEL... and
the entire 1-minute question is CLOSED for good, no further bites without a structurally new
signal-generation mechanism."**

**Gate B failed → 1-minute Solar is CLOSED**, under every calibration convention this program
has tried (fixed-StopMultiplier family, VolMult unscaled ×2 sigma-window conventions, VolMult
rescaled). SMV2AE's screen-level Sharpe 0.4394 does not survive the house chronology bar even
though it clears the bootstrap bar by a hair; the newly-built old-regime read shows the
construction losing money 2006-2021; correlation confirms zero diversification value. No
further 1-minute attempts without a structurally new signal-generation mechanism, not a further
recalibration attempt.

## Red-team disposition
Verdict: **CONFIRMED-with-corrections**. All numerics (step 0, gates A/B/C/D, decision logic)
independently reproduced bit-for-bit or arithmetic-exact. No gate-shopping, no post-hoc
threshold picking, no improper BLOCKED-BY-DATA workaround (the gate-C substrate claim is
independently verified true). One factual correction applied above (gate C's mismatched
SM06-sample pairing, does not change the conclusion under either framing); this REPORT.md
itself resolves the missing-deliverable gap flagged by red-team.

## Files
`out/step0_repro_check.json`, `out/dev_daily_curves.csv`, `out/gate_A_bootstrap.csv`,
`out/gate_A_summary.json`, `out/gate_B_loyo.csv`, `out/gate_B_fit_eval.csv`,
`out/gate_B_summary.csv`, `out/gate_B_verdict.json`, `out/gate_C_resolution_check.json`,
`out/gate_C_session_calendar_check.json`, `out/gate_C_old_regime.csv`,
`out/gate_C_old_regime_daily.csv`, `out/gate_C_summary.json`, `out/gate_D_correlation.csv`,
`out/gate_D_blend.csv`, `out/gate_D_summary.json`. Code: `src/step0_recompute_daily.py`,
`src/gate_A.py`, `src/gate_B.py`, `src/gate_C_check_resolution.py`,
`src/gate_C_build_old_regime.py`, `src/gate_C_finish.py`, `src/gate_D.py`.
