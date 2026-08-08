# Statistical Red Team — SMV2Z_VIABILITY_POLICY

Verdict: **CONFIRMED**

Scope: independent recomputation from `out/` artifacts and raw upstream sources, not a re-read
of the exec's own summary text. All numbers below were computed fresh in this review session
using differently-written code (independent bucket/percentile algorithm using `count(hist<=x)`
instead of `bisect.insort`/`bisect_right`) so the check is not just "the script agrees with
itself."

## 1. Spec letter-exactness

- `spec.yaml` (frozen 2026-08-08): AND-gate = sigma460 top tercile AND ER150 top tercile at week
  t's close, expanding-rank, >=12mo burn-in, applied to week t+1 at the weekly level. `smv2z.py`
  section 3/5 implements exactly this — verified by independent reimplementation (§2 below),
  not just code reading.
- Tercile machinery: `expanding_rank_bucket` in `smv2z.py` is `expanding_quintile` from
  `runs/SMV2Y_JOINTLOSS_VIABILITY/smv2y.py:183-195` copied verbatim with the hardcoded `5.0`
  replaced by a parameter — confirmed by direct diff of the two functions (identical
  `bisect.insort` / `bisect_right(hist,x)/len(hist)` / `math.ceil(n_bins*rp)` body). Not a
  reimplementation.
- Cells: `CELLS = [0.5, 0.7, 0.85]`, `CENTER = 0.7` — matches spec exactly, all 3 reported, no
  extra cells computed or dropped.
- Seeds: placebo uses `N_PLACEBO=200` non-overlapping same-count trigger-week draws, seeds
  1..200 — matches spec's "200 random ... draws." House bootstrap (`block_bootstrap_delta`,
  seed=20260808, block=5 daily / block=4 weekly) is explicitly labeled non-gating supplementary
  context in both the code docstring and REPORT.md, and is not a spec item at all in
  `spec.yaml`; it is however an established convention already used identically (same seed,
  same helper) in the direct predecessor `runs/SMV2V_ER_DAMPER/smv2v.py` (`HOUSE_SEED=20260808`,
  `block_bootstrap_delta`). It does not affect any gate or the KILLED verdict — confirmed
  non-gating by inspection of `all_gates_pass` construction (only g1–g6 feed it).
- No gates moved/renamed/relaxed: all 6 gates in `spec.yaml` ("gates_all_required") map 1:1 to
  `gate1_cdar_improve/gate1_tuw_improve`, `gate2_cdar_gt_placebo/gate2_tuw_gt_placebo`,
  `gate3_loyo`, `gate4_rtc`, `gate5_retention`, `gate6_oldregime_proxy` in `policy_cells.csv`,
  and `all_gates_pass` requires all of them True (`bool(g1_c and g1_t and g2_c and g2_t and g3
  and g4 and g5 and g6)`, `smv2z.py:530`).
- No continuous-score sneak-in: the policy is a binary flag (`flag_t`) times a fixed scalar `s`
  from the 3 frozen cells — no fitted weighting, no smooth function of the two states anywhere
  in the code path that produces `policy_cells.csv`/`policy_daily.csv`.
- Minor, non-attributable note: `spec.yaml`'s own kill clause calls this run "the SECOND policy
  attempt ... after SMV2N's failure and SMV2V's failure," which reads arithmetically odd (two
  named prior failures would suggest "third"). This wording is verbatim in the **frozen spec
  itself** (predates this run) and `REPORT.md` simply echoes it — not something the exec
  introduced, and it has no effect on any gate computation or the KILLED verdict. Flagging for
  visibility only, not as a defect of this run.

## 2. Independent re-derivation of the tercile/AND-gate machinery

Rewrote the expanding-rank bucketing from scratch (percentile rank via `count(history <= x) /
len(history)`, not `bisect_right`) against `runs/SMV2Y_JOINTLOSS_VIABILITY/out/target_series.csv`
columns `state_399_sigma460` / `state_400_ER150`, same burn mask (`week_last_session >=
2023-01-07`):
- n_burn_eligible = 177/230 — matches.
- AND-gate trigger (t) weeks = 23 — matches.
- Receiver (t+1, scaled) week_key set: `[202411, 202417, 202437, 202440, 202452, 202502, 202507,
  202513, 202514, 202515, 202526, 202535, 202542, 202545, 202547, 202551, 202552, 202607,
  202609, 202612, 202614, 202618, 202620]` — **exact match**, in the same order, against both
  `run_log.txt`'s printed `trigger_week_keys` and the `scaled=True` week_key set independently
  pulled from `out/policy_daily.csv`.
- STEP0 (n_bins=5 reproduction of SMV2Y's own quintiles): not just re-trusted — the
  `expanding_quintile` source in `smv2y.py` was diffed line-for-line against
  `expanding_rank_bucket`'s body; identical logic, parameter substitution only.

## 3. Independent recomputation of load-bearing numbers (>=3 required, did 9)

All computed fresh from `out/policy_daily.csv`, `out/placebo.csv`, and raw
`states_hist.csv`/`e10_daily_hist.csv`/`parity_daily_aligned.csv` — not copied from
`policy_cells.csv`:

| quantity | independent recompute | artifact value | match |
|---|---|---|---|
| net_retention s=0.50/0.70/0.85 | 0.848742 / 0.909245 / 0.954623 | same | exact |
| CDaR₀.₉₅ policy s=0.50/0.70/0.85 | 16390.0438 / 15369.1354 / 15001.3472 | same | exact |
| TUW policy (all cells) | 131 | 131 | exact |
| RTC s=0.50/0.70/0.85 | 0.889625 / 0.933775 / 0.966887 | same | exact |
| scaled-day pct of net PnL | 0.30252 (30.3%) | "30.3%" in REPORT.md | exact |
| scaled-day mean vs overall mean ratio | 474.70 / 155.81 = 3.05x | "~3.0x" in REPORT.md | consistent |
| gate6 flagged/baseline means, t-stat | −835.60 / −490.11, t=−4.293, p=2.48e-5 | −835.6/−490.1, t=−4.29, p<0.0001 | exact |
| gate6 n_flag/n_baseline | 184 / 596 | 184 / 596 | exact |
| placebo pool size / need | 153 / 23 | "pool_size=153, need=23" in run_log.txt | exact |
| placebo dcdar/dtuw median+2·IQR thresholds, all 3 cells | recomputed from `placebo.csv` directly | same (to full float precision) | exact |
| old-regime AND-gate base rates | sigma460 60.18%, ER150 38.80%, AND 23.56% | "60.2%", "38.8%", "23.6%" | exact |
| LOYO per-year signs at s=0.7 | loyo_2022/23/24/26 = −1, loyo_2025 = +1 (agree=4) | REPORT.md: "2022, 2023, 2024, 2026 ... negative ... 2025 flips positive" | exact |

## 4. Lookahead / leakage scan

- `parity_daily_aligned.csv` index max = **2026-07-31** (raw file, checked directly) — genuinely
  `< 2026-08-01`; the code's `VIRGIN_FLOOR` assert is not vacuous.
- `states_hist.csv` index max = **2021-12-31** (raw file) — genuinely `< 2022-01-01`; the
  "old-regime" substrate does not leak into the dev regime.
- `target_series.csv` `week_last_session` max = **2026-05-29** (raw file) — respects `dev <=
  2026-05-31` with margin (not exactly at the boundary, no edge-case ambiguity).
- AND-gate flag at row `i` (week t, using data through week t's last session, per SMV2Y's own
  causal state construction — verified in `smv2y.py`'s spec: "states measured using ONLY data
  through the last session of week t") is applied to row `i+1` (week t+1) only; the loop
  explicitly stops at `n_weeks - 1` so the last row can never be misread as having a "next"
  week. No same-week or backward application found.
- No file read anywhere in `smv2z.py` has a max date >= 2026-08-01; both hard VIRGIN asserts
  (`al.index.max() < VIRGIN_FLOOR`, `WK["week_last_session"].max() <= DEV_END`) are backed by
  data that actually satisfies them (not just asserted and never tested against real content).

## 5. Old-regime section labeling

Confirmed labeled a PROXY, not a validation, in three independent places: (a) `spec.yaml` gate 6
itself: "old-regime is a PROXY ONLY"; (b) the `oldregime_proxy.csv` row's own `note` field:
"PROXY ONLY: E10-only curve (no pre-2022 B-MOM/champion substrate) ... not full old-regime
validation of the champion twin AND-gate policy"; (c) `REPORT.md` gate 6 discussion and the
"INFERENCE" section explicitly caveat that the old-regime AND-gate base rate (23.6%) is "not ...
calibration-comparable to the dev-side ~13% trigger rate." The gate 6 pass is also correctly
described as insufficient to rescue the policy ("does not rescue the policy, since gates 1/2/4/5
already kill it independently") — no overclaiming of what a same-sign proxy result buys.

## 6. Language / honesty check

- REPORT.md's FACT/INFERENCE labeling is applied consistently and correctly: every FACT traces
  to a named `out/*.csv` (verified in §3); the two INFERENCE claims (mechanical concentration
  explanation's causal interpretation, and the old-regime base-rate non-stationarity mechanism)
  are both flagged as unverified interpretation, not fact, in the closing "Honesty labels"
  section.
- Kill/pass language is honest and matches the mechanical gate table exactly (cross-checked
  against `policy_cells.csv` boolean columns in §3 — no gate was described more favorably than
  its stored boolean).
- Gate 3 (LOYO) "PASS" is explicitly annotated as a non-favorable read ("mostly confirms the
  harm is consistently signed... not that the policy helps") rather than silently reported as a
  clean pass — this is the correct honest framing given the underlying per-year signs (§3 last
  row) are all negative except one.
- No BLOCKED state was invoked (STEP0 and tercile-sanity checks both passed on first run, no
  `BLOCKED.txt` was written) and none is falsely claimed — the run's actual terminal state
  (KILLED) is a genuine mechanical gate-battery outcome, not a disguised block.
- The reported workaround for writing `REPORT.md` (Write tool refused a direct "report"-pattern
  filename; content was written to another path and copied into place via `cp`) was checked:
  `runs/SMV2Z_VIABILITY_POLICY/REPORT.md` exists, its content is exactly the report reviewed
  above, and this is consistent with the established convention in this exact run family — the
  three direct predecessors (`SMV2N`, `SMV2V`, `SMV2Y`) all also ship a `REPORT.md` as one of
  their named spec outputs. No restricted-write bypass of campaign state/registry files
  occurred: `git status` on `research/registry/`, `research/CAMPAIGN_STATE.md`, and
  `research/frontier.yaml` shows no changes, and `research/registry/tested_configs.csv` has no
  rows for seq 403–405 yet, consistent with the disclosed caveat that registry updates are left
  for the orchestrator.

## Net assessment

Every load-bearing number I recomputed independently (tercile buckets via a differently-coded
percentile algorithm, net retention, CDaR, TUW, RTC, old-regime t-stat and base rates, placebo
thresholds, LOYO per-year signs) reproduced the artifact values exactly. The AND-gate and
tercile machinery are genuinely reused (verbatim function body, not reimplemented) and verified
correct, not merely asserted. No lookahead: causal state timing (t predicts t+1) holds by
construction and by data-boundary checks. The old-regime section is honestly a proxy, labeled as
such in three places. The report's language is appropriately hedged (FACT vs INFERENCE), the
KILLED verdict is the mechanically correct output of the frozen gate battery, and no dishonest or
inflated claim was found.
