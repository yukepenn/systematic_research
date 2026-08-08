# STATISTICAL RED TEAM — SMV2R_SOLAR_CORE_1 (V4 §48 mandatory pass)

Reviewer: independent red-team agent, 2026-08-08. Scope: seq 381-385, dev <= 2026-05-31.
All recomputations below were done with reviewer-written code (scratchpad script), not the
exec agent's code, reading only `out/` artifacts, the committed raw bars CSV, and the
committed SM01 substrate/e10 references.

VERDICT: **ISSUES** — everything verdict-bearing is letter-exact and recomputes exactly;
two prose errata in REPORT.md must be corrected before the run is committed as frozen
truth. No gate was moved, no number that feeds a KEEP/FAIL/KILL verdict is wrong, and no
re-run is needed.

---

## 1. Spec letter-exactness — PASS

- spec.yaml frozen in commit `58dc2d2` (2026-08-08 13:14:29 -0400, spec-only commit, 7
  spec files, zero results) BEFORE every `out/` artifact (13:21-13:28) and REPORT.md
  (13:33). Verified via `git show --stat`.
- STEP ZERO gate as written: committed simulator (`src/analytics/sm01_solarsim.py`)
  verified >= 99.99% vote_pend match before any variant ran; achieved 100.0000%
  (0/519,714), so no subtrack was improperly unblocked, and the BLOCKED escape hatch was
  not needed (nothing improvised).
- 381: per-member x per-year clamp distribution, exactly the spec's per-bar hypothetical
  k*sigma convention (exec disclosed the at-flip alternative separately in
  vol_memory.csv). <1% rule applied per bound.
- 382: exactly N in {230, 460, 920}; verdict rule coded exactly as frozen
  (neighbor dominates iff Sharpe > 1.2x incumbent AND CDaR5 < 0.8x incumbent). No extra
  arms.
- 383: exactly the 4 spec arms (ALL / no-FAST / no-SLOW / MID-only) with target =
  round(10*mean over arm members); 3-prong REMOVABLE-CANDIDATE rule coded exactly
  (Sharpe improves AND CDaR improves AND >= 95% top-10-day retention). MID-only correctly
  denied any verdict under the single-cohort rule.
- 384/385: DIAGNOSTIC only, |t_NW| > 2 bar as spec'd, NO POLICY anywhere. Spec-silent
  conventions (dedup, session truncation, NW lag = horizon, ER top-tercile reading,
  warmup = agree) are disclosed in REPORT/exec caveats and are reasonable.
- No post-hoc selection observed: every arm in the code appears in the artifacts and
  REPORT; no discarded cells found in out/ or scripts.

## 2. Independent recomputation — PASS (all match)

Recomputed with reviewer code from daily CSV artifacts (Sharpe = mean/sd*sqrt(252),
ddof=1; CDaR5 = mean of top 5% positive EOD drawdowns; top-10-day sum; ES5):

| arm | net $ | Sharpe | maxDD $ | CDaR5 $ | matches |
|---|---|---|---|---|---|
| N230 | 71,917.6 | 0.4422 | -50,884.4 | 31,505.7 | yes |
| N460/ALL/incumbent | 119,008.9 | 0.7092 | -40,207.6 | 27,161.8 | yes |
| N920 | 117,623.3 | 0.6993 | -35,312.6 | 23,980.8 | yes |
| no-FAST | 146,122.6 | 0.7680 | -40,473.6 | 26,742.6 | yes |
| no-SLOW | 116,147.2 | 0.6599 | -56,588.9 | 36,355.4 | yes |
| MID-only | 168,336.0 | 0.8352 | -53,221.6 | 34,562.0 | yes |

- Verdict rules re-evaluated independently: N230/N920 dominate = False/False -> PLATEAU
  TRUE; no-FAST 3-prong = True (retention 1.0586 on ALL's top-10 days); no-SLOW = False.
  Identical to exec verdicts.
- Bootstrap: reviewer reimplementation reproduces every boot_deltas.csv row with the
  house seed (noFAST p=0.1788) and is stable under an alternate seed (0.1780); MIDonly
  0.0916 -> 0.0944, N230 0.9492 -> 0.9484.
- Clamp audit recomputed from raw bars with reviewer-written sigma: vm6 lower 0.1251%,
  vm18 upper 1.0760%, vm30 upper 10.9336% — match clamp_audit.csv and REPORT.
- From-scratch reviewer E10 executor run on the cached target reproduces
  e10_daily_dev_incumbent.csv to max |dev| 4.1e-10 $ over 1,139 sessions; target formula
  (round-half-away-from-zero(10*mean pend), clamp +-10) verified bar-exact; all 13 member
  pend columns match the committed SM01 substrate 100%; artifact daily == committed
  runs/SM01_SUBSTRATE/out/e10_daily_py.csv exactly on all 1,139 dev sessions.
- 384: T2-short expectancy/t recomputed from signal_events.parquet with reviewer NW code:
  -2.611/-3.469/-4.439 $, t -3.234/-2.918/-2.212 — match. Full signal_layer.csv is
  consistent with the REPORT claims (the only |t_NW|>2 cells have negative means; T3-short
  overlap 72.3%, T1-long 47.4%). Conditional table max |t| = 0.7041 across the 9 cells
  (exec rounded to "<= 0.70"; rounding only).
- 385: every JOB A/B/C/D number quoted in REPORT matches ma_jobs.csv (MA30/59 dNet
  -26,222.6, tail retention 0.938, 52,829/81,567 gated; ER150|HTF -206.0/sd t -3.27;
  JOB C all placebo-indistinguishable; JOB D -123.5/-563.1/-292.1 with t -10.9/-5.2/-13.6).

## 3. Lookahead / leakage scan — PASS

- Raw input `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` spans 2022-01-02 18:03 ->
  2026-07-31 16:57: the file contains NO data >= 2026-08-01 at all, and every script
  truncates to sess_date <= 2026-05-31 before any computation (dev = 519,714 bars,
  1,139 sessions, last bar 2026-05-29 17:00 — reviewer-verified from the raw file).
- Simulator causality: sigma_t uses |dClose| through bar t only (expanding until
  t > 460, NaN < 30 with 179t fallback); member/E10 decisions at bar t close fill at
  bar t+1 open (executor loop fills the PREVIOUS decision before making the new one);
  session flatten at last-bar close; S resampled only at flips. No same-session outcome
  feeds any decision.
- 384 forward windows session-truncated; entries next-bar open with adverse slip;
  last-bar events dropped (105).
- In-sample elements that exist and are disclosed: ER150 tercile breakpoints and JOB B
  z-scores use the full dev distribution — legitimate for information reads, flagged by
  the exec itself as not-for-policy; nothing was adopted.
- JOB C placebo seeded (20260808), count-matched; JOB D re-entry size approximation
  disclosed. Diagnostic-grade, acceptable.

## 4. Report language — PASS with errata (see below)

FACT/INFERENCE/HYPOTHESIS labels used throughout; both kills (384, 385) recorded as
KILL with the negative cells shown, not buried; the FAST result is stated as
REMOVABLE-CANDIDATE with its own contrary evidence (boot p=0.179 unresolved, ES5/day
worse) in the same section. No BLOCKED items claimed; the Part-2 deferral (1m/5m clock
challenge) is the spec's own scope note, not laziness.

## 5. Policy/adoption creep — NONE

"NO adoption this wave" / "NOTHING ADOPTED; incumbent language unchanged: CURRENT ROBUST
SOLAR INCUMBENT" present; FAST removal explicitly gated on a future R2 confirmation spec;
the ER150 negative read logged as HYPOTHESIS with "NO POLICY". Clean.

---

## ISSUES (must fix in REPORT.md prose before commit; no re-run required)

1. **ER150 tercile breakpoints wrong in REPORT text.** REPORT.md §385 says "dev
   breakpoints 0.0329/0.0781". The values actually computed and used (ma_jobs_meta.json,
   reviewer-recomputed from raw bars: identical) are **0.050160 / 0.113819**. A full-file
   (through July 2026) variant gives 0.0503/0.1135, so the REPORT numbers match no
   computable variant — stale draft values. All ER-based results (JOB A/B/C/D) reflect
   the correct breakpoints, so no verdict changes; but the wrong numbers would poison any
   future ER-damper spec drafted from the frozen REPORT.
2. **381 by-year prose incomplete.** REPORT says vm30 upper-clamp binding "concentrates
   in high-vol years (2022, 2025)". The CSV shows partial-2026 (Jan-May) is the HIGHEST:
   2026 39.2%, 2025 18.3%, 2022 9.8%, 2024 3.9%, 2023 0.2%. The omission of 2026
   understates how binding the cap currently is — relevant context for the "active
   regularizer" inference. Artifact is correct; prose should name 2026.

## Notes (no action by exec required)

- FAST's CDaR prong margin is thin (26,742.6 vs 27,161.8, a 1.5% improvement); the rule
  is deterministic and correctly applied, and REPORT already carries the right caveats —
  the R2 confirmation spec should treat the CDaR prong as fragile.
- Registry (research/registry/tested_configs.csv ends at seq 371) and the run dir are
  uncommitted; exec caveat correctly assigns both to the parent orchestrator — do not
  lose seq 381-385 registration when committing.
- Exec's "all 9 cells |t_NW| <= 0.70" is 0.7041 unrounded — rounding, not an error.
