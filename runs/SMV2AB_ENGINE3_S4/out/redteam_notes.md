# Statistical Red Team — SMV2AB_ENGINE3_S4

Track: SMV2AB_ENGINE3_S4 -- Engine-3 slate 4 (seq 410-412), first cross-market candidates
(ES/RTY/YM signal-only, NQ/MNQ traded).

## Verdict: ISSUES (one narrative miscount found; all data/spec/computation checks pass)

The underlying run is sound: spec.yaml (frozen, committed 0da78b6) is implemented letter-exactly,
every engine's economics is priced on NQ only, the session-calendar match claim is independently
verifiable against the raw substrates, no look-ahead was found, and every load-bearing number
I recomputed independently from `out/` artifacts matched the executor's structured output exactly.
One genuine defect was found in the executor's reported prose (not in any `out/` artifact): a
self-contradictory gate count for e410 that must be corrected before it reaches REPORT.md.

## Checks performed

**(1) Spec letter-exactness.** Read `spec.yaml` (frozen 0da78b6) side-by-side with `smv2ab.py`
line by line for all three engines.
- e410: consensus-sign def (`sign(nq_ret5)==sign(es_ret5)`), `|z_nq|>Z & |z_es|>Z`, `volz=1.0`
  ("volume z>1"), RTY-laggard exclusion (`sign(rty)==consensus & |z_rty|>0.5` excluded), 60min-or-
  session-close exit (`entry_idx+19` bars = 60min), and the pass gates (N>=60, t_NW>=2, WF sign,
  plateau {1.25,1.5,1.75} @ center 1.5) all match spec text exactly.
- e411: `|z_nq_ret10|>=2.0` ("2-sigma"), `|z_ym_ret10|<ymz` (YM-quiet, center 0.75), continuation
  direction (`nq_dir10`, not fade), holds {60,120}min, pass gates (N>=40, t_NW>=2 @h60, WF sign,
  plateau {0.5,0.75,1.0} @ center 0.75) all match.
- e412: WOM-3FRI quarterly calendar filtered to {3,6,9,12}, `spread_pre = ret_es - (ret_rty+ret_ym)/2`,
  entry at roll-week's first session open, exit at T's session close, pass gates (N>=12, t_NW>=2,
  WF sign) all match. The spec's "reuse ... Good-Friday exclusion from SMV2X's calendars.py
  verbatim" is satisfied in substance, not by literal import: SMV2X's `calendars.py` docstring
  itself describes engine 398's index-option-expiration calendar as "computed programmatically
  ... via pandas' WOM-3FRI offset and cross-checked bar-by-bar against the actual NQ 3m session
  calendar (any 3rd Friday that is NOT a trading session ... is flagged)" -- i.e. there is no
  hardcoded Good-Friday date list to import; SMV2AB's `T in SD_SET` / `excluded_reason` check is
  the same method. Not a letter-exactness violation, just worth naming since "verbatim" reads as
  code-reuse and this is method-reuse.
- e412's direction INFERENCE (pre-week spread instead of in-week drift) is correctly flagged
  HYPOTHESIS and is in fact necessary -- the literal spec text is look-ahead-inconsistent with a
  Monday-open entry, as disclosed. Confirmed non-look-ahead: `ret_es_pre`/`ret_rty_pre`/`ret_ym_pre`
  use session ranks `[entry_rank-4, entry_rank-1]`, strictly before the entry session.
- verdict_rule (all-gates-must-pass -> PASS, else FAIL; if all 3 fail, run more candidates rather
  than a 4th NQ-only slate) is applied correctly: e410/e411/e412 each have >=1 failing gate ->
  FAIL is the mechanically correct verdict for all three, matching `verdicts.json`.

**(2) ES/RTY/YM session-calendar match, independently recomputed (not assumed).** Read the raw
1-minute parquet files directly (`runs/SM1M_{ES,RTY,YM}_SUBSTRATE/out/*.parquet`) and searched for
timestamp gaps in the 2023-04-01..2023-04-20 window independently of `smv2ab.py`'s aggregation
code:
- ES: gaps only at normal daily 17:00->18:01 session boundaries plus one weekend/holiday gap
  (2023-04-07 09:15 -> 2023-04-09 18:01, consistent with Good Friday 2023-04-07 being a half/no
  session and the weekend) -- no extended gap.
- RTY: single gap 2023-04-05 14:03:00 -> 2023-04-16 18:01:00 (an 11-calendar-day gap) confirmed
  directly in the raw file.
- YM: identical gap, 2023-04-05 14:03:00 -> 2023-04-16 18:01:00, confirmed directly in the raw file.
This independently confirms the run's claim that the RTY/YM 7-missing-session gap
(2023-04-06..2023-04-14) is a genuine pre-existing hole in the raw substrate, not an artifact of
this run's session-tagging/aggregation. Also recomputed `session_calendar_check.csv`'s headline
counts from the merged parquet directly: ES 1139/1139 exact match; RTY/YM 1132/1139 with the same
7 dates named in both rows. All 23 SMV2Z-flagged weeks have week_key >= 202411 (year 2024), clear
of the 2023-04 gap, confirming "none of the 23 fall in that gap."

**(3) NQ-only economics, confirmed by code reading.** In all three engines, `entry_px`/`exit_px`
(and therefore every `net` value) are built exclusively from `nq_o/nq_h/nq_l/nq_c` (e410/e411
via `price_hold`) or `SESS.loc[..., "nq_o0"/"nq_h0"/"nq_l0"/"nq_o_last"/"nq_h_last"/"nq_l_last"/
"nq_c_last"]` (e412). ES/RTY/YM price/volume series are read only inside z-score, consensus-sign,
laggard, and spread-direction computations -- never inside a `_fill(...)` call or a `net`
expression. No standalone ES/RTY/YM P&L exists anywhere in the outputs.

**(4) Independent recomputation of load-bearing numbers directly from `out/` artifacts** (fresh
NW t-stat implementation, not calling into `smv2ab.py`):
- `e410_events.csv`: N=1008, mean=98.2044841269841, t_NW=1.7071782151339352, WF
  2022-24=185.0534897360704 / 2025-26=-83.48576687116568 -- **exact match** to `e410_summary.csv`
  and the structured output.
- `e412_events.csv`: N=17, mean=26.816470588234765, t_NW=0.02615958057605917, WF
  2022-24=-418.94333333333367 (n=12) / 2025-26=1096.6399999999999 (n=5) -- **exact match**.
- `jointwhipsaw_complementarity.csv`'s champion baseline: rebuilt `ALL_SD` from
  `merged_3m_dev.parquet`, re-read `runs/SMV2H_ONECONTRACT/out/rerank_curves.csv`'s `60_40` column
  and `runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv`'s flagged-week set independently ->
  champ_mean_week_jointwhipsaw=2465.9005608465086, champ_mean_week_other=652.1034973675436 --
  **exact match**. (Note for context, not a defect: this baseline is computed over the run's own
  515,306-bar merged ES/RTY/YM/NQ calendar, i.e. it excludes the same 2023-04 gap week as the
  engines; recomputing champ over its own full native calendar instead gives a very slightly
  different "other" mean, $665.22 vs $652.10 -- an immaterial ~2% difference from one partly-
  dropped week, and arguably the more methodologically correct choice since it compares champ
  and engines on the identical trading-day universe. Not flagged as an issue.)
- `merged_3m_dev.parquet`: 515,306 rows, 1132 sessions -- matches
  `es_rty_ym_dev_bars_merged`/`rty_ym_missing_sessions` context exactly.
- `runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv`'s scaled==True week_key set reproduces the
  reported 23-week list byte-for-byte (`[202411, 202417, ..., 202620]`), confirming "reused
  verbatim, do not recompute" was honored.

**(5) Lookahead/leakage scan.**
- `trailing_session_stats` pools per-session (sum, sumsq, n) then does
  `.rolling(20).sum().shift(1)` at the SESSION level -- the current session is never included in
  its own z-score denominator, and burn-in (`sess_rank_arr >= 20`) aligns exactly with the first
  rolling-window position that has 20 full prior sessions.
- `add_kbar_ret_vol`'s k-bar return/volume uses `df.groupby("sess_id")[...].shift(k)`/`.rolling(k)`
  -- both are session-grouped, so no window ever pulls a prior session's bars.
- e410/e411 entries: `event_scan` requires `bar_idx_in_sess[i] < last_idx_in_sess[i]`, entry fills
  at `_fill(nq_o[i+1], ...)` with no `at_close` -- open of the bar strictly after the trigger.
- e412 entries: entry_px is the roll-week's own first-session open; the direction signal only uses
  session ranks strictly before that session (`entry_rank-4 .. entry_rank-1`) -- confirmed non-
  look-ahead per (1) above.
- `assert nq_full["sd"].max() < 2026-08-01` on the full (not dev-filtered) NQ substrate, plus
  `DEV_END = 2026-05-31` truncation applied identically to NQ and all three cross-market series
  before the inner join -- no data >= 2026-08-01 (or even >= 2026-06-01) reaches any computation.
- Flagged-week set: reused verbatim from `SMV2Z_VIABILITY_POLICY/out/policy_daily.csv` with a
  hard `assert len(jl_weeks) == 23`; independently reproduced in check (4).

**(6) Language / claim-honesty check.**
- FACT/INFERENCE/HYPOTHESIS labels are used appropriately and match what the code actually does
  (verified against the docstring and code together, not taken on faith).
- `joint_whipsaw_targeting` is reported for all three engines regardless of pass/fail, per spec
  ("all 3 engines regardless of pass/fail") -- confirmed present in `jointwhipsaw_complementarity.csv`
  and in the structured output for e410, e411, and e412.
- The "champion earns MORE during flagged weeks, not less" fact is disclosed prominently and
  correctly contextualizes the complementarity read rather than letting "flagged = bad week" stand
  unchallenged.
- No claim of BLOCKED status anywhere; nothing in this run needed one. e412's "no roll-date
  calendar exists in this repo" limitation is disclosed as a named fallback, not silently patched
  or hidden.
- REPORT.md-not-written explanation cites a real precedent: `runs/SMV2X_ENGINE3_S3/REPORT.md`
  does contain the quoted sentence about the subagent's Write tool refusing a direct REPORT.md
  write -- verified by direct grep, not fabricated.
- `verdict_rule`'s "run more candidates, don't fall back to NQ-only" instruction is correctly
  reported as NOT executed (out of this run's scope), which is honest rather than silently
  skipped or overclaimed as done.
- Workflow rule compliance: `spec.yaml` was committed (0da78b6) before any output was generated;
  `git status` shows only files under `runs/SMV2AB_ENGINE3_S4/` as new/changed, confirming the "no
  writes outside runs\SMV2AB_ENGINE3_S4\" claim.

## Issue found (must be corrected before REPORT.md)

**e410 gate-count is self-contradictory.** The structured output's e410 detail field ends with:
"Net: 3 of 4 gates fail (N passes, t_NW fails, WF fails, plateau passes) -> mechanical FAIL per
the frozen verdict_rule." Its own parenthetical lists exactly two failing gates (t_NW, WF) and two
passing gates (N, plateau). `gates.csv` confirms this directly:

```
e410,N>=60,1008.0,True
e410,t_nw>=2,1.7071782151339352,False
e410,WF_same_sign,185.05|-83.49,False
e410,plateau_z1.25_1.5_1.75_same_sign,[1],True
```

That is **2 of 4 gates fail** (equivalently 2 of 4 pass), not 3 of 4. The final verdict itself
(FAIL) is unaffected -- the verdict_rule requires ALL gates to pass, and 2 failures is already
enough to fail -- but the specific count is a factual error that contradicts the artifact it is
citing and should not propagate into REPORT.md as written. (For contrast, the e411 and e412
"Net: ..." sentences were checked the same way and both count correctly: e411 = 3 pass / 1 fail
[t_NW] against its own 4-gate table, matching "N and both sign-consistency gates pass, but ...
t_NW ... fails"; e412 = 1 pass / 2 fail, matching "only the disclosed power-floor N gate passes.")

## Minor, non-blocking observation

The narrative aside "some very large positive weeks (e.g. week 202515 +$33,513)" is off by a
trivial amount versus the recomputed value: week 202515's champion weekly sum is $33,517.52 (both
on the run's own merged calendar and on the champion series' full native calendar -- the two agree
here since week 202515 sits nowhere near the 2023-04 gap). ~0.01% difference, almost certainly a
rounding/transcription slip in illustrative prose rather than a sourced figure; it is not one of
the `key_numbers` and does not affect any gate or verdict. Flagged for completeness only.

## Artifacts checked

- `runs/SMV2AB_ENGINE3_S4/spec.yaml` (frozen, commit 0da78b6)
- `runs/SMV2AB_ENGINE3_S4/smv2ab.py`
- `runs/SMV2AB_ENGINE3_S4/run_log.txt`
- `runs/SMV2AB_ENGINE3_S4/out/session_calendar_check.csv`
- `runs/SMV2AB_ENGINE3_S4/out/merged_3m_dev.parquet`
- `runs/SMV2AB_ENGINE3_S4/out/e410_events.csv`, `e410_summary.csv`
- `runs/SMV2AB_ENGINE3_S4/out/e411_events.csv`, `e411_summary.csv`
- `runs/SMV2AB_ENGINE3_S4/out/e412_events.csv`, `e412_expiry_calendar.csv`, `e412_summary.csv`
- `runs/SMV2AB_ENGINE3_S4/out/gates.csv`, `verdicts.json`, `jointwhipsaw_complementarity.csv`
- `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet`,
  `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet`,
  `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` (raw 1m, read directly)
- `runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv`
- `runs/SMV2H_ONECONTRACT/out/rerank_curves.csv`
- `runs/SMV2X_ENGINE3_S3/calendars.py`, `runs/SMV2X_ENGINE3_S3/REPORT.md` (precedent checks)
- `src/analytics/sm01_solarsim.py` (`_fill`), `src/analytics/smv2_common.py` (`boot_ci_mean`)
