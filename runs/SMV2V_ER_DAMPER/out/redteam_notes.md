# Red-team notes — SMV2V_ER_DAMPER

Scope: `runs/SMV2V_ER_DAMPER/{spec.yaml, smv2v.py, REPORT.md, out/*.csv}`.
Verdict: **ISSUES** (numerics and gate/kill logic fully verified and CONFIRMED;
two verifiable factual mischaracterizations in the run's own methodology
narrative, neither of which changes any gate outcome or the KILLED verdict).

## 1. Spec letter-exactness — PASS

- spec.yaml committed at `547d2d4` ("Wave-4 specs FROZEN before any read") strictly
  before `smv2v.py`/`REPORT.md`/`out/*` were written (all still untracked). No
  other tracked file was touched by this run (`git status --porcelain -- runs/SMV2V_ER_DAMPER/`
  shows only the three new paths).
- Cells tested: exactly `{0.65, 0.75, 0.85}`, center `0.75` — matches spec verbatim,
  no extra cells, no post-hoc selection.
- Gate battery (1–6) implemented with formulas byte-for-byte identical to
  `runs/SMV2N_WINDFALL_POLICY/smv2n.py` for gates 1–5 (`cdar95`, `tuw_longest`,
  RTC = `pol[top_idx].sum()/twin[top_idx].sum()`, retention, LOYO ≥4/5 +
  leave-2022-out) — confirmed by diffing the gate-construction code side by side.
  Gate 6 is correctly labeled "extra, this spec" and is not cell-specific
  (shared state/relationship construction), as coded.
- Kill rule applied mechanically: gates 1 and 2 both fail (both sub-conditions)
  at all three cells → `all_gates_pass=False` everywhere → **KILLED**, exactly
  per spec's "any gate fails → family killed... hypothesis CLOSED."

## 2. Independent recomputation (>=3 load-bearing numbers) — ALL MATCH

Recomputed from raw `out/*.csv` artifacts, independent of `smv2v.py`:

- **STEP0 repro**: leg reconciliation err, dev twin battery (net/sharpe/CDaR5/TUW/
  maxDD) — recomputed via `cdar95`/`tuw_longest` reimplementation on
  `policy_daily.csv["twin_unscaled"]` → matches `repro_check.csv` and
  `cells.csv` exactly (net $179,288.70, Sharpe 1.185764, CDaR $14,151.47, TUW 133).
- **All 3 cells' dCDaR/dTUW/net_retention/RTC**: recomputed directly from
  `policy_daily.csv` columns `twin_s0.65/0.75/0.85` → exact match to `cells.csv`
  (e.g. s=0.75: dCDaR $239.234, dTUW 0, retention 1.018462, RTC 0.977774).
- **Placebo thresholds**: recomputed median+2·IQR of `dcdar_s*/dtuw_s*` over the
  200-row `placebo.csv` (feasible=200/200) → exact match to `cells.csv`'s
  `placebo_*_thresh` columns at all 3 cells.
- **Gate 6 dev-side OLS**: rebuilt the Newey-West dummy regression from
  `state_dev.csv["agree"]` + `SM01_SUBSTRATE/out/e10_daily_py.csv` independently
  → β=-371.1107, t_NW=-2.1454, n=880 — exact match to `oldregime.csv`.
- **Dev state counts**: `state_dev.csv` → 1139 sessions, 881 burn-in-eligible,
  216 agreement days — matches spec/REPORT claims exactly.
- **House bootstrap**: re-ran `sm_metrics.block_bootstrap_delta` on
  `policy_daily.csv` columns with the stated seed/block/n_boot → exact match to
  `cells.csv`'s `house_boot_*` columns at all 3 cells (the identical
  `p_leq_0=0.2561` across all 3 cells is a genuine, verified consequence of the
  bootstrap statistic scaling linearly in `(s-1)` for a fixed seed — sign of the
  delta on every resample is scale-invariant across cells since 0.65/0.75/0.85
  are all <1 — not a computation error).

No discrepancy found in any recomputed load-bearing number.

## 3. Lookahead / leakage scan — PASS

- VIRGIN guard: `leg_daily.csv` max date 2026-05-29 (< DEV_END 2026-05-31 < today
  2026-08-08). `SM01_SUBSTRATE/vote_state_3m.parquet` raw file extends to
  2026-07-31 but `build_agree_table` filters `sess_date <= dev_end` *before* any
  computation — verified the filtered set is exactly the 1139 dev sessions, no
  bar past 2026-05-31 enters the expanding tercile, ER150, or agreement calc.
  `SM06_SOLAR_HISTORY` substrate itself only contains 2006-01-05..2021-12-31
  (verified directly), used only for gate 6 sign/structure, never for tuning.
- Expanding tercile: `pool = er[ER_WIN:t+1]` at each session's close bar uses
  only bars up to and including that session's own close — causal, no
  cross-session future leakage.
- Position lag: `pos_close = vote_pos[last_idx-1]` (bar immediately before the
  session's literal last bar) — verified as FACT, not a convenient assumption:
  `vote_pos` is identically 0 at all 1139 `is_last_of_sess` bars in the dev
  substrate (confirms the report's degeneracy claim), and the underlying
  flatten mechanic in `sm01_solarsim.py` lines 251–260 does force `p=0` at
  `last_of_sess`. The chosen "one bar before" reading is real, not fabricated.
  `close_t`/ER150[t] are evaluated at the literal last bar as claimed (pure
  price data, unaffected by the flatten).
- Policy application `scaled[u]=agree[u-1]` is next-bar-only (single-day
  window), confirmed by direct comparison of `state_dev.csv["agree"]` shifted
  by one against `policy_daily.csv["scaled"]` — exact match, 216 True days.
- Burn-in: independently applied per substrate from each substrate's own first
  date (dev floor 2022-01-03, old-regime floor 2006-01-05), 365-day convention
  identical to SMV2N — confirmed in code and in `state_dev.csv`/`state_oldregime.csv`.
- No data on/after 2026-08-01 found anywhere in the touched inputs.

## 4. Language / honesty issues found

### 4a. Placebo "non-overlapping with each other" claim is factually false
(minor — doesn't affect gate validity or the kill decision)

Both `smv2v.py`'s docstring ("200 seeds 1..200, same scaled-day COUNT,
non-overlapping with each other and with the real scaled days") and
`REPORT.md` Gate 2 text ("200/200 feasible, non-overlapping with the real 216
scaled days **and with each other**") claim the 200 placebo draws are mutually
non-overlapping. This is verifiably false and, given the numbers, could not be
true: the burn-in-eligible feasible pool (excluding the real 216 trigger days)
has only 664 slots (`lo=259`, `n=1139`); each seed draws 216 of them without
replacement, so any 4 seeds together already exceed the pool by pigeonhole.
Directly enumerated all C(200,2)=19,900 seed pairs against `placebo.csv`'s
implied draws (reconstructed with the exact `np.random.default_rng(seed)`
calls used in the script): **every single pair overlaps** (19900/19900).
What actually holds (and is correctly implemented): each individual seed's
216-day draw avoids the real 216 scaled days, and — because of `replace=False`
— avoids duplicating an index within its own draw. The methodology itself
(200 independent same-count random controls vs. the real trigger set, used to
build a null median/IQR) is standard and not invalidated by this — but the
report's explicit textual claim of cross-seed non-overlap is wrong and should
be corrected or dropped.

### 4b. "146 calendar dates with duplicate is_last_of_sess flags" mislabels the number
(minor — the underlying fix is verified correct)

`smv2v.py` (comment) and `REPORT.md` §6 state: "the pre-2012 early-close
handling... produces **146 calendar dates** with more than one `sess_id`-last
bar in the old-regime substrate (4276 flagged bars vs 4130 unique dates)."
Recomputed directly from `SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet`:
4276 flagged bars, 4130 unique `sess_date` values — both confirmed — but the
number of calendar dates that actually carry more than one flagged bar is
**128** (112 with 2 flags, 14 with 3, 2 with 4), not 146. 146 is the total
*excess* flagged-bar count (4276−4130=146) summed across those 128 duplicated
dates, not a count of dates. The grouping fix itself (`groupby("sess_date")
["idx"].max()`) is correct regardless of this mislabeling, and the "verified a
no-op on the modern SM01/dev substrate" claim was independently confirmed
(the calendar-group method and the raw `is_last_of_sess` flag pick out the
identical 1139 bar indices on the dev substrate). Only the "146 calendar
dates" figure in the prose is wrong; should read "128 calendar dates
(146 excess flagged bars)."

### 4c. Minor: mischaracterization of sub385's "undefined = agree" convention
(very minor, does not affect SMV2V's own — independently defensible — choice)

`REPORT.md`/`smv2v.py` state that sub385's "undefined MA state = AGREE (no
gating)" convention "applied to MA sign-match tests only" and that ER150
"undefined" has no sensible default-to-agree. Reading
`SMV2R_SOLAR_CORE_1/sub385_majobs.py` line 56 directly: sub385's own
`agree_fn` for ER150 is `return (s == 2) or (s == -1)` — i.e., sub385's
*gating* convention (used in its JOB A executor / episode-conflict search)
ALSO defaults undefined ER150 to agree, exactly like the MA states. This
contradicts the "MA only" claim. That said, the actual JOB B regression that
produced the cited FACT coefficient (-$206/sd, t=-3.27) does not use
`agree_fn` at all — it uses a directly-constructed continuous `day.aer`
(fraction of within-session, position-nonzero bars with `st_er==2`), which
has no sign-match condition and no explicit undefined-defaulting logic. So
SMV2V's own choice (undefined ER ⇒ not agree) remains independently
reasonable and is not invalidated by this; only the specific "MA only"
attribution is inaccurate, and readers should not treat this run's
undefined-handling choice as forced by sub385's actual code.

Additionally, relatedly: the spec's own hypothesis prose describes the FACT as
top-tercile-agreement "aligned with the ensemble position at session close"
— but the JOB B `aer` regressor that actually produced the -$206/sd, t=-3.27
coefficient has no sign/position-alignment term at all (only `a1`/`a2`, the MA
states, carry sign-match terms in JOB B). The sign-alignment condition in
SMV2V's "agreement day" definition is therefore a genuinely NEW construction
motivated by, but not a literal reproduction of, the cited FACT — which the
run's documentation does disclose ("built fresh... NOT in sub385 at all"), so
this is flagged for completeness rather than as an undisclosed deviation.

### 4d. Very minor: old-regime "3872 burn-in-eligible sessions" label

`REPORT.md` §"Gate 6" says "1028 agreement days / 3872 burn-in-eligible
sessions." Recomputed from `state_oldregime.csv`: `burn_ok.sum()=3873` (the
actual burn-in-eligible session count), while 3872 is the gate-6 regression's
sample size after `dropna()` drops the final session (no next-day PnL to
regress against) — the same off-by-one pattern correctly kept distinct on the
dev side (881 burn-in-eligible vs. 880 regression days). Cosmetic only; no
numbers computed from n=3872 vs n=3873 are materially different (1028/3873 =
26.55% vs 1028/3872 = 26.55%).

## 5. Overall assessment

The statistical work is sound and reproduces exactly: every gate value, every
threshold, the repro check, the OLS coefficients, and the house bootstrap all
independently recompute to the reported precision. The KILL verdict is
correctly and mechanically derived from the spec's gate battery, and is
decisive (gates 1 & 2 fail by wide margins at all three cells, not a
borderline center-cell call) — nothing above changes that conclusion. The
issues logged in §4 are documentation/language inaccuracies in the run's own
narrative (one methodological overclaim about the placebo battery's
cross-seed independence, one date-count/excess-count mislabel, one
mischaracterization of a reused function's semantics, one sample-size
off-by-one) that should be corrected in `REPORT.md`/`smv2v.py` comments but do
not require rerunning or reopening the (closed, killed) hypothesis.
