# Statistical red-team review — SMV2T_NOFAST_R2 (seq 389)

Reviewer pass over `runs/SMV2T_NOFAST_R2/` (spec.yaml, step0_verify.py, gate_AD.py, gate_B.py,
gate_C.py, gate_E.py, REPORT.md, and all `out/*` artifacts). Verdict: **ISSUES** — the 5-gate
mechanical evaluation, the overall FAIL/kill decision, and every gate-determining number
independently reproduce exactly; one narrative (non-gate-determining) count in the Gate C
INFERENCE prose is wrong and should be corrected. Nothing found changes the reported decision.

## 1. Spec letter-exactness — PASS

- `spec.yaml` was committed at `547d2d4` (2026-08-08 13:48:10 -0400) **before** any of the run's
  execution scripts existed (file mtimes: spec.yaml 13:47, step0_verify.py 14:15, gate_AD.py
  14:16, gate_B.py/gate_C.py 14:17, gate_E.py 14:19, REPORT.md 14:22). All execution scripts and
  `out/` artifacts are untracked (`git status --porcelain`), i.e. genuinely produced after the
  spec freeze, not retrofitted.
- Bootstrap parameters (`block=5, B=10000, seed=20260808`, moving-block circular index
  construction) match the spec text exactly in `gate_AD.py`, and the resulting `P(dSharpe>0)`
  and `P(dCDaR>0)` are exactly reproducible by rerunning the identical algorithm against the
  committed `out/curves.csv` (see §2).
- Gate C executor constants (`TICK=0.25, COMM=2.18, PV=20.0`, ops windows `hm==1639` /
  `1630<=hm<1803`) are byte-identical to `runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_b.py`'s
  `run_policy_hist`, confirming the "same conventions as SMV2H2 gate B" claim.
- Gate E's SIG re-derivation (`SIG_new = DUAL_NOFAST.std(ddof=1)`) matches
  `runs/SMV2H_ONECONTRACT/rerank.py`'s own `SIG = DUAL.std(ddof=1)` / `vm(x): x*(SIG/x.std())`
  definition verbatim — confirmed by reading `rerank.py` directly. This is not an invented rule;
  spec.yaml's own gate-E text explicitly authorizes "re-derived scalars documented."
- Member-count discrepancy: spec prose says "10-member (no vm6-12)"; the mechanical rule
  `(no vm6-12)` removes vm{6,8,10,12} (4 of 13), leaving 9 members (vm14..vm30) — confirmed via
  `step0_verify.json` (`n_nofast_members: 9`, list = [14,16,18,20,22,24,26,28,30]), identical to
  SMV2R sub_383's own no-FAST arm (`FAST=[6,8,10,12]` in gate_C.py matches). Disclosed
  transparently in Step 0 and REPORT.md, not silently resolved. The "10" is genuinely a labeling
  slip in the spec prose (off-by-one from the unambiguous member list), and the resolution
  (use the list, not the prose count) is the only mechanically defensible reading.
- Gate C's "rebuild both cores" (no DUAL/HTF overlay) vs Gates A/D/E's DUAL-transformed
  "decision object" is a real distinction drawn in spec.yaml's own `object_under_test` prose
  ("the DECISION object, not the raw core"); Gate C testing the raw cores is a correct reading
  of the spec's own language, not an improvised softening.
- Gate B's "LOYO dSharpe same sign >= 4/5 years" is implemented as "dominant sign is positive
  AND >=4/5 of years share it" (`gate_B.py` lines 40-42), rather than a symmetric
  either-direction reading. This is the only sensible reading for a promotion gate (a gate that
  would "pass" on 4/5 years favoring the *incumbent* makes no sense as a promotion bar for the
  challenger), and — important for bias-checking — it is not outcome-favorable window-dressing:
  the actual data is 4/5 positive either way, so both the literal and the intent-based readings
  agree here. No grid/cell was added or dropped; all 5 gates specified were run, no more, no
  fewer; no post-hoc gate selection or reweighting.
- Verified all cited **reference artifacts are pre-existing, previously-committed files**, not
  fabricated in this run: `runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz`,
  `daily_cohort_no_FAST.csv`, `e10_daily_dev_incumbent.csv`;
  `runs/SMV2H2_ONELOT_CONFIRM/out/tdd_dev_from_tgt.npy`;
  `runs/SMV2H_ONECONTRACT/out/solar_dual_htf_daily.csv`, `rerank_curves.csv`,
  `rerank_portfolios.csv`; `runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet`,
  `e10_daily_hist.csv`; `runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet` — all
  confirmed via `git log` to be committed in prior waves (140f76c, 0f16e48, fa44763), unmodified
  (`git status` clean on each).
- Confirmed `vote_state_3m_hist.parquet` really does store only aggregate columns
  (`vote_pos`, `vote_pend`, no per-member columns) — the claim that per-member votes had to be
  regenerated for Gate C (rather than reused) is accurate, not a pretext for extra work.
- Confirmed SMV2R sub_383's cited "DISCLOSED PRIOR" figures (Sharpe 0.768 vs 0.709, retention
  105.9%, CDaR margin 1.5%, raw-core boot `p(d<=0)=0.179` ⇒ `P(d>0)=0.821`) against
  `runs/SMV2R_SOLAR_CORE_1/REPORT.md` directly — all match exactly.
- No writes outside the run dir: `git status --porcelain | grep -v SMV2T_NOFAST_R2` shows only
  unrelated Wave-4 sibling tracks (SMV2U, SMV2V) from the same spec-freeze commit; no
  CAMPAIGN_STATE.md / frontier.yaml / registry changes, confirming the report's own caveat.

## 2. Independent recomputation of load-bearing numbers — 4 of 4 exact matches

Recomputed from committed `out/` artifacts, independent of the gate scripts' own printed
output (fresh Python session, same public inputs):

1. **Gate A bootstrap** — rebuilt the identical moving-block bootstrap (seed 20260808, block=5,
   B=10000) from `out/curves.csv`'s `DUAL_ALL`/`DUAL_NOFAST` columns:
   `P(dSharpe>0) = 0.8033`, `P(dCDaR>0) = 0.3895`, point Sharpe 0.8992/1.0335, point
   CDaR5 20447.47/18336.84 — **all match `out/gate_A.csv` exactly** (deterministic given the
   seed, as expected).
2. **Gate B LOYO + fit/eval** — recomputed per-year `d_sharpe` from `out/curves.csv` directly:
   2022 +0.3091, 2023 −0.2533, 2024 +0.0140, 2025 +0.0329, 2026 +0.6489 — **matches
   `out/gate_B_loyo.csv` exactly** (4/5 positive).
3. **Gate D retention** — recomputed top-10-day retention from `out/curves.csv`:
   top10_ALL_sum=113,139.50, NOFAST-on-those-days=121,024.90, retention=1.069696...,
   overlap=7 — **matches `out/gate_D.csv` exactly**.
4. **Gate E portfolio rebuild** — rebuilt the full pipeline (BM ledger →
   `vm()`/SIG re-derivation → `dd_battery` → champion-curve reindex) from
   `runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet`,
   `runs/SMV2H_ONECONTRACT/out/rerank_curves.csv`, and `out/curves.csv`:
   SIG_old=2143.2802, SIG_new=2420.0820, `d_sharpe=+0.0869661...`, `d_CDaR=−1653.2061...` —
   **matches `out/gate_E.csv` exactly** to full float precision.
5. (Bonus, bit-for-bit) Loaded `out/tpp_all_dev.npy` and
   `runs/SMV2H2_ONELOT_CONFIRM/out/tdd_dev_from_tgt.npy` directly and compared: **identical on
   all 519,714 dev bars**, confirming the report's "bit-for-bit" claim independent of the gate
   script's own self-check.

All gate pass/fail booleans (A fail, B pass, C fail, D pass, E fail) reproduce from these
numbers exactly as tabulated in REPORT.md's decision table.

## 3. Confirmed discrepancy (non-dispositive) — Gate C narrative year count

REPORT.md's Gate C INFERENCE paragraph states: *"no-FAST wins 9 of 16 years on d_net
(`out/gate_C_yearly.csv`)."* Recomputing `sign(d_net)` directly from the committed
`out/gate_C_yearly.csv`:

- Positive `d_net` (no-FAST wins): 2006, 2009, 2010, 2012, 2013, 2015, 2016, 2018, 2019, 2021
  → **10 years**, not 9.
- Negative `d_net` (ALL wins): 2007, 2008, 2011, 2014, 2017, 2020 → 6 years.
- 10 + 6 = 16, consistent with `n_years=16` in `out/gate_C.csv`.

The correct count is **no-FAST wins 10 of 16 years**, not 9. This is a genuine off-by-one error
in a claim that cites its own artifact and is directly checkable — it belongs in the corrections
list. It does **not** change any gate verdict: Gate C's mechanical pass/fail rests entirely on
`c1` (net gap −$16,676.4 vs the −$10k floor, independently recomputed and confirmed correct) and
`c2` (maxDD ratio 0.9605, confirmed), neither of which uses the yearly win-count. It also does
not bias the report's framing in the challenger's favor — if anything the correct count (10/16)
is slightly *more* favorable to the no-FAST challenger than what was reported (9/16), so this is
an accuracy slip, not a cherry-pick to strengthen a preferred narrative. Recommend REPORT.md be
corrected to "10 of 16."

## 4. Lookahead / leakage scan — clean

- Dev cutoff: `DEV_END = 2026-05-31` in `step0_verify.py`/`gate_AD.py`/`gate_E.py`; last actual
  dev session used is 2026-05-29 (confirmed via `out/curves.csv`'s max `sess`), well inside the
  "no data ≥ 2026-08-01" bound and well before the current date (2026-08-08). Note: the
  underlying raw substrate `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` itself extends to
  2026-07-31 — more recent data physically exists in the file — but every gate script applies
  the `sess_date <= DEV_END` filter before any statistic is computed, so no forward data leaks
  into any gate. Confirmed by inspecting `sm01_solarsim.load_bars_3m` (`sess_date` = date of
  the session's **last** bar, i.e. the 17:00 ET close date, matching the project's session
  convention) and each gate script's filter line.
- Gate C hist substrate: filtered `time < 2022-01-01` (verbatim SM06 convention), entirely
  pre-2022 — no VIRGIN-rule exposure.
- HTF regime signal (`sign(close - SMA50(close)).shift(1)`) is causal: the prior *completed*
  session's regime state is applied to the current session, never same-session information.
- `sigma_series` (CausalSigma) is as-of-bar-t (expanding mean pre-`vol_period`, rolling window
  after), with values before `min_count=30` bars forced to NaN and handled via a deterministic
  fallback constant in `member_states` — no forward-looking window.
- `e10_target` is a pointwise (no window) transform of the per-bar member-position matrix.
- All three executors used (`common_exec.e10_exec`, `gate_C.py`'s `run_policy_hist`,
  `gate_E.py`'s `rerank_sim`) implement next-bar fills: the target/pending position computed as
  of bar t's close is only executed at bar t+1's open/close price, never filled at the same bar
  that generated the signal. Confirmed by reading all three fill loops directly.

## 5. Language / claim labeling — mostly good, one slip

- FACT vs INFERENCE labeling is used consistently and appropriately throughout REPORT.md; the
  bottom line is stated as an honest kill ("does NOT become CHAMPION-CANDIDATE... lead is
  CLOSED... no third bite without a new mechanism") rather than spun as a near-miss win, even
  though every point estimate in every gate favors the challenger — the report is explicit that
  point-estimate direction and statistical/robustness significance are different things, which
  is the correct framing here.
- No BLOCKED status is claimed anywhere in this run; all 5 gates were fully computed, consistent
  with the artifacts present.
- The one factual slip is the Gate C "9 of 16" year count addressed in §3 — it sits inside a
  paragraph labeled INFERENCE but is itself a directly-checkable count that should have been
  exact. Everything else checked (point deltas, bootstrap quantiles, SIG values, BM rescale
  factors, maxDD deltas, overlap counts, worst-year figures) matches its source artifact to the
  reported precision.

## 6. Decision mechanics — applied correctly

Per spec: "pass ALL → promote; fail ANY → incumbent retained, lead closed." Gates: A fail
(P(dSharpe>0)=0.8033<0.85, P(dCDaR>0)=0.3895<<0.85), B pass, C fail (net gap −$16,676.4 <
−$10k floor; c2 alone passing does not save it since both prongs are AND-required), D pass,
E fail (dCDaR point-negative −$1,653.2, despite dSharpe passing). 3 of 5 gates fail →
mechanically the decision is FAIL → incumbent 13-member core retained, no master rebuild
triggered, lead recorded CLOSED. This is exactly what REPORT.md concludes; no cherry-picking of
a subset of gates, no reweighting, no exception carved out for the passing gates (B, D).

## Verdict

**ISSUES** (not REJECTED — the mechanical decision, all 5 gate verdicts, and every
gate-determining number are independently confirmed correct and letter-exact to spec; the one
finding is a non-dispositive, non-outcome-biasing narrative miscount that should be corrected in
REPORT.md text, not a computational or procedural defect).

### Action item
- Correct REPORT.md's Gate C section: "no-FAST wins 9 of 16 years on d_net" → "no-FAST wins 10
  of 16 years on d_net" (per `out/gate_C_yearly.csv`).
