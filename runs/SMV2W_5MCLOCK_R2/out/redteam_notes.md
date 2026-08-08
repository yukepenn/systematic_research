# Red team notes — SMV2W_5MCLOCK_R2 (seq 395)

Reviewer: statistical red team subagent. Scope: letter-exactness vs spec.yaml, independent
recomputation of load-bearing numbers from `out/` artifacts, lookahead/leakage scan,
honest-language check, mechanical decision check.

## Verdict: CONFIRMED

## 1. Spec letter-exactness

- `spec.yaml` was committed in `7abeb79` (message: "...5m TIME-MATCHED clock EARNS R2
  confirmation... -> SMV2W frozen...") — confirmed via `git show 7abeb79 --stat` (spec.yaml,
  +38 lines). All code/out/ artifacts for this run are untracked in the working tree
  (`git status --short runs/SMV2W_5MCLOCK_R2/`), i.e. produced strictly after the spec was
  frozen, matching REPORT.md's "committed 7abeb79 before any read/execution" claim.
- Gate A: spec requires paired moving-block bootstrap, block=5, B=10000, seed=20260808,
  P(dSharpe>0)>=0.85 AND P(dCDaR>0)>=0.85, on the DUAL-transformed daily diff. `gate_AD.py`
  implements exactly this (both prongs AND-required, `gateA_pass = P_dSharpe_gt0>=0.85 and
  P_dCDaR_gt0>=0.85`). No extra cells, no alternate seed/block tried.
- Gate B: spec requires LOYO same-sign >=4/5 years AND fit(2022-24)->eval(2025-26)
  point-positive. `gate_B.py` implements per-calendar-year Sharpe deltas (5 years present,
  as required by data — not a cherry-picked subset) and the fit/eval split exactly as
  specified; `gateB_pass = loyo_same_sign_pass and fit_eval_pass` (AND-required, matches
  spec). The LOYO construction requires the dominant sign specifically to be POSITIVE
  (favors the challenger) rather than merely "same sign either way" — this is inherited
  verbatim from SMV2T_NOFAST_R2's template per the campaign's "do not redesign the gates"
  rule, and is explicitly disclosed as a caveat in REPORT.md. It has no effect on this run's
  outcome: the actual split is 3 positive / 2 negative, so `max(0.6,0.4)=0.6 < 0.8` fails
  under either a positive-required or a sign-agnostic reading — verified independently below.
- Gate C: spec's contingency ("IF derivable... ELSE BLOCKED-BY-DATA, require unanimous
  A/B/D/E") is followed exactly. `gate_C_determination.py` reads the actual committed SM06
  substrate (columns, bar-spacing mode) rather than just asserting the spec's parenthetical,
  and additionally flags a second, independent scope reason (this spec's own `data:` field
  only authorizes `nq_1m_2022_2026.parquet`, not SM06's separate pre-2022 raw file). Verified:
  `has_per_member_cols=False`, `dt_mode_seconds=180.0` (3-minute) — both consistent with the
  file actually inspected. This is a genuine determination, not a rubber-stamped assumption.
- Gate D: spec bar is >=0.90 (this run's own frozen spec, deliberately different from
  SMV2T's 1.00 bar per REPORT.md's caveat) — confirmed present verbatim in spec.yaml line 27
  ("top-10-day retention of the 5m-DUAL curve vs the incumbent 3m-DUAL curve >= 0.90"), i.e.
  not a post-hoc loosening; the bar was frozen before execution.
- Gate E: spec requires dSharpe AND dCDaR point-positive at the full portfolio level, plus a
  reconciliation against SMV2U's already-committed portfolio numbers before trusting the new
  bootstrap-based gates. `gate_E.py` does Part 1 (raw-leg reconciliation, 4/4 fields exact)
  before Part 2 (the actual DUAL-transformed rebuild) — matches spec's ordering intent.
- Decision rule applied exactly as spec states: "fail any available gate -> incumbent
  retained, lead closed." A and B fail -> incumbent retained. No selective gate-dropping, no
  softening because Gate E (the "exciting" portfolio number) passed. The report explicitly
  states Gate E passing does not override A/B failing — correct mechanical application.
- No moves/extra cells: only the single 5m-clock challenger vs the single 3m incumbent is
  tested throughout; no alternate VolPeriod, no alternate transform parameters, no gate
  reruns with different seeds are present in any output file.

## 2. Independent recomputation (>=3 load-bearing numbers, done from `out/` artifacts only)

All recomputed directly from `out/curves.csv` (DUAL_ALL, DUAL_5M daily nets) using the exact
formulas documented in `gate_AD.py`/`gate_B.py`, run independently in this review session:

1. **Standalone battery** (net/Sharpe/CDaR5 for both legs, k=56 worst days): recomputed
   net_ALL=138,280.00, net_5M=152,668.60, Sharpe_ALL=0.899201, Sharpe_5M=0.969087,
   CDaR5_ALL=20,447.47, CDaR5_5M=14,893.10 — **exact match** to `out/gate_A.csv`.
2. **Gate A bootstrap** (independently re-run: seed=20260808, block=5, B=10000, identical
   circular moving-block index construction): P(dSharpe>0)=**0.642**, P(dCDaR>0)=**0.5487**
   — **exact match** to `out/gate_A.csv` / REPORT.md, confirming the FAIL verdict is not a
   transcription or seed error.
3. **Gate B LOYO per-year signs**: recomputed d_sharpe for all 5 years directly from
   `curves.csv`: 2022 −0.0324 (neg), 2023 −0.0688 (neg), 2024 +0.2115 (pos), 2025 +0.0149
   (pos), 2026 +0.3751 (pos) → 3/5 positive — **exact match** to `out/gate_B_loyo.csv`,
   confirming 3/5 < 4/5 bar (FAIL) independent of the positive-vs-sign-agnostic reading noted
   above (0.6 < 0.8 either way).
4. **Gate D retention**: recomputed top-10-day sum of DUAL_ALL = $113,139.50, DUAL_5M's PnL
   on those same 10 days = $104,587.30, retention = 0.92441, overlap = 7/10 days — **exact
   match** to `out/gate_D.csv` and `out/gate_D_top10_detail.csv` (also verified the 10 detail
   rows sum correctly to the reported totals).
5. **Gate E cross-check**: confirmed `rerank_portfolios.csv` row `DAYONLY_DUAL_BMOM_60_40`
   (net=194,416.04, sharpe=1.264240) and `rerank_curves.csv` column `60_40` sum
   (194,416.04) match `gate_E.csv`'s incumbent-champion reconstruction fields exactly, and
   `portfolio_contrib.csv` row `5m_time_matched_portfolio` matches `gate_E_reconciliation.csv`
   to <6e-11 — both pre-existing, previously-committed artifacts, not fabricated for this run.

All five recomputations landed at float-noise-level agreement (0 to 1e-11), no discrepancies
found anywhere in the numeric chain from raw curves through gate verdicts to REPORT.md prose.

## 3. Lookahead / leakage scan

- Dev bars (`bars_5m_dev.parquet`, reused from SMV2U) run 2022-01-03 -> 2026-05-29 only
  (verified directly from the parquet file's `sess_date` min/max) — consistent with spec's
  `dev <= 2026-05-31` and REPORT's "no data >= 2026-08-01" claim; well clear of the current
  date (2026-08-08).
- DUAL_HTF's HTF state is built as `sign(prior_session_close - SMA50(session_closes))
  .shift(1)` (step1_dual_htf.py line 59) — genuinely causal: day D's HTF state depends only
  on session closes through D−1. No same-day or future information enters the transform.
- Session-close equality between the 3m and 5m bar files was verified bar-for-bar
  (`max|dev|=0.0`) rather than assumed, which is the correct way to justify reusing one
  clock's session-level HTF state for the other clock's execution — this is not a leakage
  shortcut, since session close is a genuinely clock-invariant quantity (both bar series
  aggregate from the same underlying 1-minute ticks up to the same session boundary).
- Gate C's would-be old-regime (2006-2021) computation was never touched (no raw pre-2022
  file was opened) — confirmed by the determination script's own file list (only
  `vote_state_3m_hist.parquet` and `run_hist.py` source text were read, both from the
  already-committed SM06 output, no raw 1-minute file access) and by REPORT's own explicit
  statement to that effect. No locked-forward data was used for tuning at any stage; VolPeriod
  and all transform parameters (tilt 1.25/c1_50/0.9026/clip13) were carried over unchanged
  from prior, already-frozen waves, not fit on this run's dev window.
- Calendar years used in Gate B's LOYO (2022–2026) are the genuinely available calendar years
  in the frozen dev window, not a fitted or cherry-picked subset — confirmed by session counts
  per year (258/258/259/259/106) summing to exactly 1,139, matching the full dev calendar.

## 4. Language check

- REPORT.md and the exec summary consistently label claims as FACT (directly measured/
  reproduced) vs INFERENCE (interpretive judgment) — e.g., Gate A's "unlike SMV2U's R1
  screen... the house bootstrap bar is materially harder to clear" is correctly tagged
  INFERENCE, not asserted as fact.
- The kill is genuine, not softened: despite Gate E (portfolio-level) and Gate D (right-tail)
  both passing outright, and every point estimate favoring the challenger, the report does
  not talk itself into a pass — it states plainly "2 of 4 available gates fail (A, B)... the
  3m incumbent clock is retained... this R2 lead is CLOSED." No hedging language ("mostly
  passes," "close enough") is used to paper over the two bootstrap/chronology failures.
- BLOCKED-BY-DATA for Gate C is a genuine block, not a disguised pass or fail: the
  determination script actually inspects the committed substrate rather than asserting the
  spec's parenthetical, gives two independent grounds, and the report correctly applies the
  spec's own contingency (unanimous A/B/D/E required, not met) rather than either silently
  dropping Gate C or letting it swing the decision on its own.
- Caveats section is candid about interpretive choices (LOYO sign convention inherited
  verbatim, Gate D's bar differing from SMV2T's, the REPORT.md filename workaround) rather
  than hiding them.

## 5. Mechanical decision check

Per spec: "pass all AVAILABLE gates (A/B/D/E; C per its own contingency) -> CHAMPION-
CANDIDATE; fail any available gate -> incumbent retained, lead closed." Gate results: A=FAIL,
B=FAIL, C=BLOCKED-BY-DATA (contingency not met since A/B fail), D=PASS, E=PASS. Two of four
available gates fail -> rule mechanically yields "incumbent retained, lead closed," exactly
the reported outcome. No discretionary override, no re-weighting of gates, no exception
carved out for the fact that Gate E (the highest-profile number, portfolio Sharpe/CDaR) came
back positive.

## Minor observations (non-blocking)

- Gate B's LOYO "same sign" construction requires the dominant sign to be positive rather
  than being genuinely direction-agnostic; this is a template inheritance choice explicitly
  disclosed in both `gate_B.py`'s docstring and REPORT.md's caveats, and does not change this
  run's verdict (3/5 either way is below the 4/5 bar). Flagged only for awareness if a future
  wave wants a stricter, direction-agnostic true-LOYO redesign — not a defect in this run.
- `gate_E_summary.json` and `gate_B_summary.json` exist in `out/` but were not listed in the
  exec summary's `artifacts` array; both are harmless supplementary JSON summaries duplicating
  numbers already in the corresponding CSVs, not missing/hidden required outputs.

## Checks performed

1. Read `spec.yaml` and confirmed it was frozen in commit `7abeb79`, prior to any code/out/
   artifact in this run (all of which remain untracked in the working tree).
2. Read all five gate scripts (`gate_AD.py`, `gate_B.py`, `gate_C_determination.py`,
   `gate_E.py`, plus `step0_verify.py`/`step1_dual_htf.py`) end-to-end and compared their
   logic line-by-line against spec.yaml's gate definitions.
3. Independently recomputed, in a fresh Python process reading only `out/curves.csv`: the
   standalone Sharpe/CDaR/net battery for both legs, the full Gate A bootstrap (same
   seed/block/B), Gate B's per-year LOYO signs, and Gate D's top-10-day retention — all landed
   at float-noise-level agreement with the committed `out/*.csv` files.
4. Cross-checked Gate E's reconciliation and champion-curve reconstruction against the
   underlying previously-committed reference files (`SMV2U/out/portfolio_contrib.csv`,
   `SMV2H_ONECONTRACT/out/rerank_portfolios.csv`, `rerank_curves.csv`) directly, confirming
   those reference numbers are genuine pre-existing artifacts, not fabricated for this run.
5. Verified the dev bar substrate's actual date range (2022-01-03 to 2026-05-29) directly
   from the parquet file, and inspected the DUAL_HTF causal construction (`.shift(1)`) for
   lookahead.
6. Verified `git status` shows all of this run's code/out/ as untracked (no commits made),
   matching the exec summary's "no git commands were run" caveat.
