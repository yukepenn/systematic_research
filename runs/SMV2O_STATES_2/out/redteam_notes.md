# RED TEAM NOTES — SMV2O_STATES_2 (V4 §48 mandatory statistical pass)

Reviewer: independent red-team agent, 2026-08-08. Scope: seq 375 (Kalman innovation whiteness,
9 cells) + seq 376 (BOCPD regime age, 3 cells), SMV2J frozen harness. Verdict under review:
double KILL, DSP JOB1 branch exhausted.

## VERDICT: CONFIRMED

Letter-exact spec application, exact reproduction of every load-bearing number (many at 1e-9 or
better), no lookahead found, no policy language, kills recorded honestly.

## 1. Spec applied letter-exact

- Grids: q/r {1e-4,1e-3,1e-2} x M {50,100,200} = 9 KAL cells; lambda {100,250,500} = 3 BOC cells.
  harness_results.csv has exactly 12 rows; states_dev/hist dumps contain exactly the 12 state
  columns + Q columns + controls. No extra cells anywhere.
- Harness "EXACTLY SMV2J": verified by line-for-line comparison of smv2o.py vs
  runs/SMV2J_STATE_HARNESS/smv2j.py — expanding_quintile, boot_beta_state, zsc, quintile_stats,
  welch_t, tests 1-4, plateau rel-range, and family-verdict logic are identical. Seed 20260808,
  B=10000, block=5, NW lag 5, |t|>2 + boot same-sign >=0.975, plateau both rel-ranges <0.30,
  monotonicity <=1 inversion, REVERSAL (=sign flip with |Welch t|>=1) kill — all as in SMV2J.
- Two additions only, both spec-mandated or inert: (a) the extra sigma460 kill rule (threshold
  0.7, computed BEFORE the harness pass, wired into best-cell selection; not triggered, so the
  best-cell rule reduces exactly to SMV2J's max-|t_NW|); (b) the SMV2J reproduction assert
  (880 / 2023-01-03..2026-05-28), a check, not a gate move.
- Spec frozen BEFORE results: spec.yaml committed 58dc2d2 at 2026-08-08 13:14:29 -0400; out/
  artifacts written 13:25-13:26.
- No moved gates: BOC secondary E10 t crosses 2 (2.13 / 2.03) but is reported-only; the primary
  gate was applied as preregistered. No post-hoc selection observed.

## 2. Independent recomputations (own code, from out/ artifacts + raw substrate)

Regression layer (from states_dev.csv / states_hist.csv, own HAC OLS + own bootstrap):
- All 12 cells: t_NW, t_e10, Q5-Q1 spreads, hist Welch t, corr(state, sigma460), inversion
  counts — every value matches harness_results.csv to <1e-9 (spreads <1e-6).
- Plateau: KAL t rel-range 3.2543 / spread 3.2784; BOC 0.1044 / 4.2317 — match.
- Bootstrap with independently reconstructed frozen-seed draws (default_rng(20260808)):
  KAL_qr1e-2_M200 same-sign 0.8963, BOC_lam250 same-sign 0.9646 — exact match, so the frozen
  seed was genuinely used.
- Cross-corr(best KAL, best BOC) = -0.13233 (match); max |corr(state, sigma460)| = 0.18328 at
  BOC_lam100 (match); extra-kill not triggered anywhere.
- Quintile columns re-derived with independent expanding-rank code for 3 cells — exact match;
  confirms no full-sample scaling in the bucketing.
- Rebuilt regression sample from the dump: 880 sessions 2023-01-03..2026-05-28; hist 3,872
  sessions 2007-01-05..2021-12-30 — identical to SMV2J's meta.json (reproduction claim TRUE).

State-generation layer (from raw parquet, deliberately different implementations):
- Matrix-form Kalman (vs executor's scalar recursion) + statsmodels Ljung-Box:
  KAL_qr1e-2_M200 dev column max |diff| = 4.3e-10 over all 1,139 sessions.
- scipy.stats.t.logpdf BOCPD (vs executor's gammaln form): BOC_lam250 dev column max |diff|
  = 1.2e-12; finite everywhere (post-fix math verified stable, and the fa-normalized merge is
  algebraically identical to the mass-weighted merge — incident fix claim TRUE).
- Dev blocks 51,956; beta0_dev 5.435244454e-06; hist blocks 174,623; beta0_hist 3.103480233e-07;
  dev bars after filter 519,714 — all match meta.json.
- Session keying: dumped sess_close and sigma460 equal the last-bar parquet values (no
  off-by-one-session shift).

## 3. Lookahead / leakage scan of smv2o.py — CLEAN

- Kalman: strictly forward filter; innovation at bar j uses bars <= j; LB window e[k-M:k] ends
  at the session-close bar k. Causal.
- BOCPD: forward filter over blocks; state read after the last COMPLETED block of session t
  (hist up to 9 bars before close — uses less info, never more). beta0 uses only the first
  12 months of each series, fully known before the >=12mo quintile burn-in ends and hence
  before any regression-sample session. Causal.
- Quintiles: expanding rank inclusive of current value; HTF control = trailing SMA50 sign;
  outcome alignment via shift(-1) (state t -> PnL t+1). No same-session outcome use.
- z-scores over the regression sample are sample-affine transforms only: t-stats and bootstrap
  beta SIGNS are invariant, so no effective full-sample leakage into any gate.
- Data hygiene: dev parquet extends to 2026-07-31 but is hard-filtered to sess_date <=
  2026-05-31 BEFORE any computation (519,714 bars, verified); e10_daily_py.csv extends to
  2026-07-31 but is filtered at load; primary outcome file ends 2026-05-29; regression sample
  ends 2026-05-28. No data >= 2026-06-01 in any computed quantity; nothing near 2026-08-01.
- RMAX=2000 truncation (spec-implicit, disclosed): NEVER binds — max E[run length] is 416.6
  (dev) / 875.0 (hist), p99 <= 465. Not decision-relevant.

## 4. Report language / class discipline

- Claims labeled FACT / INFERENCE / HYPOTHESIS correctly; every FACT traced to an artifact.
- Kills recorded honestly, including the unfavorable-to-kill details (BOC secondary t>2, grid-
  stable BOC t) AND the unfavorable-to-keep details (spread sign flip, reversal cell). No
  BLOCKED items claimed. The 7 spec-implicit readings are disclosed and none is decision-
  critical (verified for the cap and the FLAT/REVERSAL threshold; the reversal cell holds for
  any threshold up to 1.5 and is not a family best).
- DIAGNOSTIC class respected: no policy/adoption/exposure language; JOB2 explicitly NOT
  triggered; "no such cell is authorized here" for the hypothesized transform. Correct.
- Exec-agent summary numbers all trace to artifacts (0.965 = 0.9646 rounded; 1.326/1.835/
  3.254/0.104/4.232/-0.132 all exact).

## 5. Minor notes (non-verdict-changing)

1. The failed first run's log was overwritten by the rerun (same run_log.txt path). The failure
   is documented in REPORT.md and debug_nan.py is preserved, and the failed run produced no
   read results — acceptable, but future executors should suffix logs (run_log_attempt1.txt)
   so crash evidence survives verbatim.
2. spec.yaml omits RMAX, R=1, P0, and block-construction details that smv2o.py fixes; all are
   disclosed in REPORT.md and none moves a verdict (cap never binds; standardized innovations
   depend only on q/r). For future state specs, put truncation/init constants in the spec.
3. Registry: seq 375/376 not yet in research/registry/tested_configs.csv (last entry 371) and
   no registry/state files were modified — consistent with the executor's no-writes caveat.
   Parent must record the two KILLs.

Recomputation scripts (scratchpad, session-local): redteam_recompute.py (regression layer),
redteam_states.py (state-generation layer). Not part of the run record.
