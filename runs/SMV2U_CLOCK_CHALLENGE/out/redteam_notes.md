# Statistical red team — SMV2U_CLOCK_CHALLENGE (seq 390-392)

Verdict: **ISSUES** (one confirmed factual inconsistency in REPORT.md prose; everything else —
spec letter-exactness, artifact numbers, independent recomputation, leakage scan, and language
discipline — checks out clean).

## 1. Spec letter-exactness (spec.yaml vs step0/step1/step2 vs REPORT.md)

- spec.yaml committed at 547d2d4 ("Wave-4 specs FROZEN before any read"), zero diff since —
  confirmed via `git diff 547d2d4 -- spec.yaml` (empty). Verdict rule, cells, and seeds were
  frozen before any output was generated.
- Cells match exactly: 1m {bar-matched VolPeriod=460, time-matched VolPeriod=1380} x 5m
  {bar-matched VolPeriod=460, time-matched VolPeriod=276} = 4 challenger arms + 3m incumbent
  reference (reused verbatim, not recomputed) — confirmed in `step1_clock_arms.py` CONFIGS list
  and `out/clock_arms.csv` (5 rows, exactly these 5 labels, no extra cells).
- 13-member V3 ensemble (VMS=6..30 step 2) and E10 executor (`e10_target`,
  `common_exec.e10_exec`) are byte-identical imports from `runs/SMV2R_SOLAR_CORE_1` — read the
  source directly (`sm01_solarsim.py`, `common_exec.py`); confirmed unmodified, called only with
  the bars-frame/vol_period varying, matching the spec's "verbatim" claim.
- Friction constant: TICK($0.25) x MNQ_POINT_VALUE($2.00) + MNQ_COMM_SIDE($0.65) = $1.15/side,
  confirmed by reading `sm01_solarsim` constants directly — matches REPORT.md §3's derivation.
- Portfolio blend: `step1_clock_arms.py`'s `portfolio_blend`/`vm_series` functions reproduce
  `runs/SMV2H_ONECONTRACT/rerank.py`'s `vm()`/blend formula exactly (SIG = leg's own std,
  `vm(x)=x*(SIG/x.std())`, `p=vm(ws*leg+wb*vm(bm))` at ws=0.6/wb=0.4) — confirmed by reading both
  files side by side. BM source (`ledger_E2_next_open.parquet`, `net_c1_ticks * 5.0`) is identical
  in both. The "leg = own plain-E10 curve, no DUAL_HTF layer" caveat is applied identically to the
  incumbent's portfolio row (`inc_port = portfolio_blend(inc_series, ...)` using the same
  plain-E10 `inc_series`), so the comparison is internally apples-to-apples as claimed.
- verdict_rule implemented mechanically: `standalone_beats = (sharpe > inc.sharpe) and
  (CDaR5 < inc.CDaR5)`, `portfolio_beats` identical at the portfolio level, `earns_R2_spec =
  standalone_beats and portfolio_beats` — pure boolean AND of the frozen rule, no discretion.
  Recomputed independently from `clock_arms.csv`/`portfolio_contrib.csv`: exactly one arm (5m
  time-matched) satisfies all four conditions — matches REPORT.md §7 exactly.
- Bootstrap/NW convention (seed=20260808, B=10000, block=5, HAC maxlags=5, |t_NW|>2, boot
  same-sign >=0.975) matches the established house convention from
  `runs/SMV2J_STATE_HARNESS/out/redteam_notes.md` line 12 verbatim — not an invented threshold.
- seq 392 preregistered as "3 reads" in spec.yaml (R1/R2/R3); `out/mtf_reads.csv` correctly
  contains exactly 6 rows (3 reads x 2 frozen 1m conventions), matching "TWO frozen memory
  conventions per clock (no other variants)" from spec.yaml — no extra cells were read. **See
  Issue 1 below**: REPORT.md's own prose miscounts this as "7" in two places.
- No adoption/promotion language anywhere outside explicit "NOT an adoption decision" disclaimers
  (grep-verified) — consistent with spec's "NO adoption from this run."

## 2. Independent recomputation (>=3 load-bearing numbers, from raw substrate / cache, not by
   re-reading the same CSV cell twice)

1. **5m time-matched standalone arm, rebuilt from scratch** from `out/bars_5m_dev.parquet` using
   `sm01_solarsim`/`common_exec` directly (fresh script, VolPeriod=276): net=$136,527.20,
   Sharpe=0.792645, CDaR5=$22,521.0375 — exact match to `clock_arms.csv` row and REPORT.md §2
   ($136,527.2 / 0.793 / $22,521.0). This is the arm that earns the R2 spec, so it was checked
   end-to-end, not just formula-recomputed.
2. **R2 entry-timing (bar-matched), rebuilt from scratch**: independently reran the backward
   asof-join (1m vote -> 3m decision spine) and the episode construction (contiguous nonzero runs
   of `cache_incumbent.npz`'s `bar_pos`) from raw arrays, then NW-OLS regression: n_episodes=4746,
   n_disagree=769, spread=-$77.924, t_NW=-2.0938 — exact match to `mtf_reads.csv` and REPORT.md §8
   (this is the run's single INFORMATIVE cell, so it received the most scrutiny).
3. **Friction share formula**, recomputed from `clock_arms.csv`'s own `net`,
   `total_contracts_traded`, and `friction_per_contract_side_$` columns for all 5 arms
   independently (not reading the `friction_share` column) — reproduces the reported column to
   full float precision for every row (0.325604, 1.282205, 1.019966, 0.227724, 0.210650).
4. **3m incumbent reference metrics**, recomputed directly from
   `runs/SMV2R_SOLAR_CORE_1/out/e10_daily_dev_incumbent.csv` (net/Sharpe/CDaR5 via
   `smv2_common.dd_battery`): $119,008.90 / 0.709234 / $27,161.82 — matches the incumbent row used
   throughout `clock_arms.csv` and `portfolio_contrib.csv`, confirming it actually is the reused,
   unmodified SMV2R artifact (not silently redefined).
5. **LOYO full-sample dSharpe + sign agreement**, recomputed from `loyo_tables.csv`'s raw
   `sign_matches_full` column via groupby/sum: 1m bar -0.904 (5/5), 1m time -0.728 (5/5), 5m bar
   +0.019 (3/5), 5m time +0.083 (5/5) — exact match to REPORT.md §6.
6. Substrate counts (`substrate_verify.json`) match REPORT.md §0 exactly: 1139/1139/1139 sessions,
   519,714/1,558,498/311,849 bars, zero flagged sessions, one documented naive-heuristic false
   split (2022-11-06).
7. Daily-curve correlation-with-incumbent figures (§4 "INFERENCE bonus") recomputed from
   `daily_curves.csv` via `.corr()`: 0.7876/0.7512/0.8821/0.8927 — matches the reported
   0.788/0.751/0.882/0.893 exactly.

All seven independent recomputations match the reported numbers to the reported precision. No
fabricated or silently-adjusted figures found anywhere checked.

## 3. Lookahead / leakage scan

- `sigma_series`, `member_states`, `e10_target`, `e10_exec` are all strictly causal (state at bar
  t uses only data through bar t's close; fills execute at the *next* bar's open) — read the
  source directly, confirmed no forward references.
- R1/R2 MTF reads use the 1m vote resampled onto the 3m spine via `merge_asof(..., direction=
  "backward")` — explicitly causal (state at-or-before the 3m bar's close only); verified the
  `assert merged["vote"].notna().all()` guard is present and 225/519,714 (0.043%) backfilled bars
  are isolated single-minute data gaps, not a systematic lookahead workaround (spot-checked the
  2022-03-09 21:00-23:00 window directly against `bars_1m_dev.parquet`: found 15 missing minutes
  out of 120 there, run-lengths max 2 — confirms the qualitative claim "scattered singly, never
  more than 1-2 consecutive" but the specific count REPORT.md cites for that window, "21 missing
  ... out of ~120," does not reproduce under several reasonable interpretations of the window
  bounds (15-24 depending on inclusive/exclusive endpoints tried) — a minor illustrative-example
  imprecision, not a load-bearing number, noted for completeness).
- R1's "next-3m-bar adverse move" is a legitimate predictive-test construction (X known at bar t,
  y realized at t+1) — not leakage; excludes flat bars, session-final bars, and the file's last
  bar, preventing any cross-session "next bar" (verified against `is_last3`/index-bound logic).
- R2's episode PnL uses the *entry* bar's 1m vote as X and the *full episode's* future realized
  PnL as y — by construction (does information at entry predict subsequent outcome), not a
  leakage artifact.
- R3's burn-in (>=12 months from first dev session, `burn_end = first_sess + DateOffset(years=1)`)
  is present and applied before any regression sample is formed — confirmed in code and in
  `mtf_reads.csv`'s `sample_first`/`sample_last` fields (2023-01-03 to 2026-05-28).
- Dev-only enforcement: every economic-computation script (`step0`, `step1`, `step2`) filters or
  asserts `sess_date <= 2026-05-31` before any P&L/statistic is computed; raw substrate files
  extending to 2026-07-31 are read only for session-boundary bookkeeping in `step0`, never for any
  economic quantity. No timestamp >= 2026-08-01 is read by any economic computation anywhere in
  the three scripts (grep/read-verified).

No lookahead or leakage issues found.

## 4. Language discipline

- FACT / INFERENCE / HYPOTHESIS labeling is used consistently and correctly throughout REPORT.md;
  spot-checked several labeled claims against their underlying numbers (all accurate).
- "NO adoption language" instruction honored: the only occurrences of "adopt"/"promot" in
  REPORT.md are inside explicit disclaimers stating the opposite ("NOT an adoption decision").
  Grep-verified, no false positives.
- "KILLED" applied to the 1m arms (net negative, friction_share > 1, LOYO-robust badness 5/5) is
  an honest, earned kill, not editorializing — matches the campaign's established use of that word
  (`research/registry/tested_configs.csv` row 366 uses "KILLED" identically).
- The 5m bar-matched "near miss" framing is honest and quantitatively supported (portfolio
  Sharpe 1.113 vs 1.120, CDaR5 $19,509.6 vs $19,299.3, LOYO 3/5 sign-flip) rather than rounded up
  to a pass.
- No BLOCKED status claimed anywhere (none was warranted).

## 5. Issues found

### Issue 1 (confirmed, minor): "7 preregistered reads" miscount in REPORT.md prose

REPORT.md §8 states, twice (line 205: "the only INFORMATIVE cell in this run's 7 preregistered
reads"; line 240: "the frozen 7-read budget"), that seq 392 comprises **7** preregistered reads.
This is factually wrong on the run's own terms:

- spec.yaml itself defines seq 392 as **"3 preregistered reads"** (R1, R2, R3), each read at the
  two frozen 1m memory conventions per spec's own "TWO frozen memory conventions per clock (no
  other variants)" rule -> 3 x 2 = **6** cells.
- `out/mtf_reads.csv` contains exactly **6** rows (R1_failed_start x 2, R2_entry_timing x 2,
  R3_agreement_accel x 2) — independently confirmed by reading the artifact.

The correct multiple-testing budget for seq 392 is 6, not 7. This matters because the "1 of 7"
framing is used narratively to contextualize how surprising the single INFORMATIVE result (R2
bar-matched) is against the number of preregistered tests run — "1 of 6" is the number the run's
own artifacts support. This does not change any classification (R2 bar-matched remains the only
cell that clears both the |t_NW|>2 and boot-same-sign>=0.975 bars; the AND-based verdict_rule for
seq 390/391 is unaffected, since seq 392 is a separate DIAGNOSTIC family with no gate to trip) but
it is a real, independently-verifiable inaccuracy in a load-bearing sentence of the delivered
report and should be corrected to "6" in both places.

## 6. What is NOT an issue (checked and cleared)

- The "portfolio leg = plain-E10 curve, not DUAL_HTF" reading (caveat 2) is well-flagged as the
  most material inference in the run and is applied symmetrically to the incumbent — verified in
  code, not just asserted in prose.
- Friction-share "gross" definition (caveat 3) is applied identically to all 5 arms including the
  incumbent — verified by recomputation (§2.3 above).
- The choice of bar-matched-as-primary for the seq 392 reads (caveat 5) is disclosed as INFERENCE,
  and both conventions are fully reported for every read (no results withheld).
- No post-hoc selection: the verdict rule and both memory conventions were frozen in spec.yaml
  before any economic computation ran (git history confirms zero diff on spec.yaml since the
  freeze commit), and every cell the spec calls for is reported, including the ones that failed
  (both 1m arms, 5m bar-matched at the portfolio level, R1 and R3 at both conventions).
