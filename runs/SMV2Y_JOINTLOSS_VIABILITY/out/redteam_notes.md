# Red-team review — SMV2Y_JOINTLOSS_VIABILITY (seq 399-402)

**Verdict: CONFIRMED** (letter-exact to frozen spec 51dbc45; all recomputations match)

## What was checked

### 1. Spec letter-exactness
- `spec.yaml` (frozen 51dbc45) vs `smv2y.py`: states (399 sigma460, 400 ER150, 401 flip_rate,
  402 VR_q26_N780), targets (primary = next-week min(0, cumsum) downside; secondary = binary
  joint-loss on leg_solar/leg_bmom), seeds (20260808), bootstrap params (B=10000, block=4 weeks),
  NW lag (2), gate (`|t_NW|>2` AND monotonicity ≤1 inversion) all match the spec text verbatim.
- Verdict logic (`smv2y.py:284`, `verdict = "KEEP" if (t1_pass and t2_pass) else "KILL"`) uses
  only the two formally-gated tests; test_3/test_4 correctly excluded from the gate per spec
  ("reported for context only, not a fresh gate" / "NOT RUN for the joint-loss/portfolio target").
- No extra state/target cells were computed beyond the 4×2 spec grid. Controls correctly omit
  `z(sigma460)` when sigma460 is the tested state (`is_sigma` branch, code + CSV `controls` column
  confirm: sigma460 row has `controls=htf` only, other three have `z_sigma460+htf`).
- Cluster rule implemented exactly as specified and correctly did not fire (see below).
- **402_VR_q26_N780 selection is not post-hoc for this run**: independently pulled all 9 VR cells
  from `runs/SMV2J_STATE_HARNESS/out/harness_results.csv` — `|t_state_NW|` values are
  1.114, 0.369, 0.017, 0.114, 1.091, 0.680, 1.055, **1.653**, 0.983. VR_q26_N780 (row 7) is indeed
  the max, confirming "best-plateaued dev cell" was chosen on a *prior* target (daily Solar PnL)
  before this run's target existed — genuinely not cherry-picked for this run's outcome.
- **400_ER150's n=150 window is independently justified**, not a best-of-family pick: SMV2J's own
  ER family shows ER_n460 (|t|=1.744) actually beats ER_n150 (|t|=1.060) on the old daily-PnL
  target, so n=150 was clearly *not* chosen for SMV2J performance — it was chosen to match
  `runs/SMV2R_SOLAR_CORE_1/sub385_majobs.py` line 46
  (`er[150:] = |close[t]-close[t-150]| / sum(|dclose|, trailing 150)`), which I confirmed is
  algebraically identical to smv2q.py's `er150` construction (line 173). Selection criterion
  documented and independent of this test's result.

### 2. Week-boundary construction vs SMV2Q
- `wkey()` in `smv2y.py:64-66` is byte-identical to `smv2q.py:85-87`.
- Boundary-pair merge (`smv2y.py:73-77`) is logically identical to `smv2q.py:49-55`
  (confirmed by reading both; only variable names differ).
- Independently recomputed `merged_val` directly from `parity_daily_aligned.csv`:
  129,340.30 + (−126,974.10) = **2,366.20** — matches `meta.json` exactly.
- Independently recomputed ISO-week counts: champion/leg calendars both give **230** weeks over
  dev (matches SMV2Q's own reported total); hist calendar (`states_hist.csv`, 2006-2021) gives
  **834** weeks (matches the claimed `n_hist_weeks_old_regime`).
- Independently rebuilt the leg-based joint-loss week set from `target_series.csv`
  (`joint_loss_t==1` → 50 weeks) and diffed against `runs/SMV2Q_DIAGNOSTICS/out/joint_loss_periods.csv`
  (freq=weekly, 50 rows): **exactly 42/50 overlap**, matching the report's claimed distinction
  that the two 50-week sets are not the same weeks (8 weeks differ each direction, confirmed by
  listing the symmetric differences). The "coincidental count match, not the same weeks" framing
  is accurate, not a rationalization.
- Verified no gaps in the 230-week dev sequence (all 229 consecutive week-to-week deltas equal 1
  ISO week), so `shift(-1)` alignment genuinely maps week t → week t+1 with no silent skips.

### 3. Independent recomputation of load-bearing numbers
Full independent rebuild of `target_series.csv` → harness (not just re-running the same script):
recomputed expanding-quintile means, OLS-HAC(lag2) beta/t, and the moving-block bootstrap
(same seed, same block size) from scratch for **all 4 states**:

| state | recomputed t_NW | reported t_NW | recomputed boot_same_sign | reported |
|---|---|---|---|---|
| 399_sigma460 | −2.2971198 | −2.2971198 | 0.9900 | 0.99 |
| 400_ER150 | −3.0467664 | −3.0467664 | 0.9979 | 0.998 |
| 401_flip_rate | +1.5271557 | +1.527 | 0.9224 | 0.922 |
| 402_VR_q26_N780 | −0.7524455 | −0.752 | 0.7802 | 0.78 |

All exact matches (bit-for-bit on the ones with visible decimals). Also independently rebuilt the
full old-regime proxy pipeline from `states_hist.csv` for all 3 states — spreads and t-stats
matched to 2-3 decimal places (e.g. sigma460 t=−7.133, ER150 t=−3.141, VR t=−1.118 vs reported
−7.13/−3.14/−1.12). Quintile means for sigma460/ER150 primary target also reproduced exactly.
Monotonicity/inversion counts for 401 and 402 hand-verified from the reported quintile means
(1 inversion each, matches CSV).

### 4. Lookahead / leakage scan
- Every state column is assigned from `sd.loc[last, ...]` where `last` = week t's actual last
  session (`smv2y.py:161-169`) — a genuine point-in-time snapshot, no forward information.
- `flip_rate` is a mean strictly over week t's own sessions (`wdays_wk` filtered to
  `first_session..last_session` of week t) — no next-week bar leaks in.
- `downside_next`/`joint_loss_next` are `shift(-1)` of week t's own value — confirmed this
  correctly lands on week t+1 given the verified gap-free week sequence.
- Burn-in: `burn_end = first_week_last_sess + 1yr` = 2023-01-07, matches meta.json; regression
  sample only includes weeks with `week_last_session >= burn_end`, i.e. ≥12 months of expanding
  history before any quintile rank is used. Same construction for the hist/old-regime proxy
  (burn_end_h = first hist week + 1yr).
- VIRGIN floor (2026-08-01): every source file's date range was checked directly —
  `parity_daily_aligned.csv` and `vote_state_3m.parquet` do extend to 2026-07-31 (before the
  floor but after DEV_END), and both are explicitly sliced to `<= DEV_END` (2026-05-31) before
  any computation touches them; `leg_daily.csv` and `states_dev.csv` already end at/before
  2026-05-29. No row ≥2026-08-01 was read. (Minor code-quality note, not a leakage bug: the
  `assert al.index.max() < VIRGIN_FLOOR or True` on line 71 is a no-op due to `or True` — it
  doesn't actually enforce anything, though the subsequent `.loc[... <= DEV_END]` slice makes the
  computation correct regardless.)

### 5. Old-regime proxy honesty
Confirmed the proxy is honestly scoped everywhere it appears: `old_regime_proxy.csv`'s own `note`
column states "PROXY ONLY: E10-only curve (no pre-2022 B-MOM/champion substrate); not full
old-regime validation of the joint-loss/portfolio target itself" for all 3 rows; `flip_rate` is
correctly excluded from this section entirely (spec disclosed vote_pos has no old-regime
substrate); the report's framing ("supportive context, not a formal old-regime pass/fail")
matches the actual statistical content — it doesn't claim the champion/joint-loss target itself
was validated pre-2022, which would be false (B-MOM has no pre-2022 substrate, confirmed absent
from the repo).

### 6. Language / labeling
- FACT vs INFERENCE labels are used correctly: the ER150 forward-vs-concurrent sign discrepancy
  is flagged INFERENCE and left open rather than resolved either way. Independently verified this
  discrepancy is real: `runs/SMV2Q_DIAGNOSTICS/REPORT.md` Q10 reports joint-loss weeks have
  **lower** concurrent ER(150) (0.0855 vs 0.0960, t=−6.5), while SMV2Y's forward regression finds
  **higher** ER150 this week predicts **worse** downside next week (direction=−1) — a genuine,
  correctly-flagged sign tension between a concurrent and a forward-looking relationship, not
  glossed over.
- The claim that `SMV2M_MASTER_BUILD/parity.py` does not contain the boundary-merge logic was
  independently verified: the file's only use of "merge" is an unrelated `pd.merge` join; no
  `2023-04-05`/`04-06` boundary-pair code exists there. The merge logic genuinely only lives in
  `smv2q.py:49-55`, confirming the report's provenance correction was accurate, not an excuse.
- Kills are honestly reasoned: 401/402 both pass monotonicity but fail the formal `|t_NW|>2`
  gate, and both show weak bootstrap same-sign fractions (0.922, 0.780) — consistent, not cherry
  picked to make the kill look worse or better than the numbers show.
- The REPORT.md BLOCKED claim is a genuine tool-level restriction (this reviewer's own Write tool
  carries the identical "no report/summary/findings .md files" restriction referenced in the
  claim), not a fabricated excuse. All four required CSV/JSON artifacts were in fact produced.

## Recomputation script (for reference, not persisted elsewhere)
Ad hoc Python was run against `out/target_series.csv`, `out/harness_results.csv`,
`out/old_regime_proxy.csv`, `out/meta.json`, and the upstream source files
(`SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv`, `SMV2Q_DIAGNOSTICS/out/leg_daily.csv`,
`SMV2Q_DIAGNOSTICS/out/joint_loss_periods.csv`, `SMV2J_STATE_HARNESS/out/states_dev.csv`,
`SMV2J_STATE_HARNESS/out/states_hist.csv`, `SMV2J_STATE_HARNESS/out/harness_results.csv`,
`SMV2R_SOLAR_CORE_1/sub385_majobs.py`, `SMV2M_MASTER_BUILD/parity.py`) — all read-only, no writes
outside this run's `out/` directory, no NinjaTrader/CrossTrade tools touched.

## Bottom line
No discrepancies found between the executor's reported numbers/claims and the underlying
artifacts. Target/state construction, week-boundary handling, harness math, cluster-rule
non-trigger, old-regime proxy, and all four verdicts (399/400 KEEP, 401/402 KILL) are letter-exact
to the frozen spec and fully reproducible from the persisted CSVs.
