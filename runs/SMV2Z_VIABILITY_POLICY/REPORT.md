# SMV2Z_VIABILITY_POLICY — REPORT

Frozen spec: `runs/SMV2Z_VIABILITY_POLICY/spec.yaml` (committed `fdd0e65`, read before any
write). Class: PORTFOLIO_TEST (R1, bounded). seq 403 (policy cells), 404 (placebo), 405
(chronology + old-regime proxy). Script: `runs/SMV2Z_VIABILITY_POLICY/smv2z.py`.

**VERDICT: KILLED** — every one of the 3 frozen cells (s=0.5, 0.7, 0.85) fails gates 1, 2, 4
and 5. This is the **third consecutive policy failure** built on a joint-loss/downside
viability diagnostic (after SMV2N and SMV2V — the frozen spec.yaml's kill clause itself says
"SECOND," an off-by-one in the spec text since it names two priors; correcting here, this does
not affect any gate computation or the KILLED verdict, confirmed by red-team as immaterial).
Per spec's own kill clause, the V4.1 §21
"viability state → policy" escalation is **EXHAUSTED for the sigma460/ER150 pair**. The
underlying SMV2Y diagnostic finding (sigma460/ER150 forecast next-week downside) still stands
as **INFORMATION**, unaffected by this policy's failure.

## FACT: what was built and how it reproduces the parent runs

1. **States reused verbatim** — `runs/SMV2Y_JOINTLOSS_VIABILITY/out/target_series.csv` columns
   `state_399_sigma460` / `state_400_ER150` (SMV2Y's own per-ISO-week snapshot at week t's
   last session), 230 weeks, week_key 202201–202622. No state was recomputed from
   `states_dev.csv`.
2. **Tercile machinery verified before use** (`out/step0_quintile_repro.csv`): SMV2Y's
   `expanding_quintile` function was copied verbatim and given an `n_bins` parameter. Run with
   `n_bins=5` on the raw sigma460/ER150 columns, it reproduces SMV2Y's own
   `harness_results.csv` q1..q5 mean-downside and q1_n/q5_n cell values **bit-for-bit** (max
   abs diff ≤1e-6) for both states — confirms the reused rank machinery is correct before
   trusting it for terciles.
3. **Tercile sanity check** (`out/tercile_sanity_check.csv`, 12 checkpoints across the burn-in
   eligible window, both states): at every checkpoint, the raw-value cutoff at the tercile
   boundary (rank-percentile 2/3) sits between the raw-value cutoffs of SMV2Y's own Q3/Q4
   (rp=0.6) and Q4/Q5 (rp=0.8) quintile boundaries, as expected for a monotone rank
   transform. 12/12 pass.
4. **Champion curve reproduces SMV2M/SMV2Y exactly**: `parity_daily_aligned.csv` "nt" column,
   truncated to dev (≤2026-05-31), 2023-04-05/06 boundary pair merged identically to
   `smv2q.py` lines 49-55 / `smv2y.py` section A — n_days=1138, merged value=$2,366.20,
   both matching SMV2Y's `meta.json` exactly.
5. **Old-regime "net" cross-check**: `states_hist.csv`'s `net` column and SM06's own
   `e10_daily_hist.csv` `net` column are identical (max abs diff = 0.0 over 4,130 common
   sessions) — confirms `states_hist.csv` carries the same E10-only hist curve
   `smv2y.py` section I actually used, per the CODE MAP instruction.
6. **VIRGIN guard**: `parity_daily_aligned.csv` index max (2026-07-31) < 2026-08-01; all dev
   objects asserted ≤2026-05-31 before any use. No row ≥2026-08-01 was ever read for policy
   construction.

## FACT: the AND-gate policy construction

- Burn-in: `week_last_session >= first_week_last_sess + 1yr` = **2023-01-07**, identical to
  SMV2Y's own `burn_end_dev`. 177/230 weeks burn-eligible.
- Top tercile = expanding-rank bucket 3 of 3 (n_bins=3), same core bisect-insort machinery as
  SMV2Y's quintiles.
- AND-gate trigger weeks (both sigma460 AND ER150 top tercile at week t's close): **23/177**
  burn-eligible weeks (13.0%; near the ~11% expected for two independent ~33% flags — sigma460/
  ER150 dev-week correlation is −0.036 per SMV2Y meta.json).
- Policy applied to week t+1 (next row): **23 receiver weeks, 113 scaled sessions** out of
  1,138 dev sessions (9.9% of days).

## FACT: the policy's mechanical effect — it concentrates in the strategy's BEST weeks, not its worst

`out/policy_daily.csv`: the 113 scaled days carry **30.3% of total dev net PnL** ($53,641 of
$177,315) despite being only 9.9% of days — mean PnL on scaled days ($474.70) is ~3.0x the
overall mean ($155.81). The AND-gate flags weeks that, per SMV2Y's regression-controlled
diagnostic, carry elevated *next-week downside tail risk* — but on raw, unconditional averages
in this specific 4.5-year dev sample, those flagged weeks were disproportionately **strong**
weeks for the champion curve. Scaling every day of a disproportionately profitable week by
s<1 removes far more upside than the diagnostic's tail-risk finding would predict downside
saved — this is the direct mechanical cause of every gate failure below.

## FACT: gate-by-gate results (`out/policy_cells.csv`)

| s | net retention | CDaR₀.₉₅ Δ | TUW Δ | RTC | placebo gate (CDaR/TUW) | LOYO | old-regime proxy | ALL PASS |
|---|---|---|---|---|---|---|---|---|
| 0.50 | 0.849 (need ≥0.97) | **−$1,485** (worse) | 0 | 0.890 (need ≥0.97) | FAIL/FAIL | 5/5, PASS | PASS | **FAIL** |
| 0.70 (center) | 0.909 (need ≥0.97) | **−$464** (worse) | 0 | 0.934 (need ≥0.97) | FAIL/FAIL | 4/5, PASS | PASS | **FAIL** |
| 0.85 | 0.955 (need ≥0.97) | **−$96** (worse) | 0 | 0.967 (need ≥0.97) | FAIL/FAIL | 3/5, **FAIL** | PASS | **FAIL** |

- **Gate 1 (CDaR/TUW improve) — FAILS for all 3 cells.** CDaR₀.₉₅ gets strictly *worse*
  (higher) at every s (e.g. $14,905→$16,390 at s=0.5); TUW is unchanged (131 days) at every s.
  Mechanically consistent with the finding above: damping a disproportionate share of large
  positive/recovery days lengthens time spent below the running peak rather than shortening
  it.
- **Gate 2 (placebo threshold) — FAILS for all 3 cells**, trivially, since the real ΔCDaR/ΔTUW
  are negative (worse than baseline) while 200/200 placebo seeds were feasible and the
  threshold (median+2·IQR of placebo improvements) is a comparison among *improvements*; a
  negative real delta cannot clear it.
- **Gate 3 (LOYO) — passes for s=0.5, 0.7; fails for s=0.85.** Read with caution: the full-
  sample ΔSharpe is *negative* at every s (policy underperforms unscaled on Sharpe overall);
  "LOYO agree ≥4/5" here mostly confirms the **harm is consistently signed** across years
  (2022, 2023, 2024, 2026 all show negative ΔSharpe at s=0.7; only 2025 flips positive), not
  that the policy helps. This is *not* a favorable read despite the boolean PASS.
- **Gate 4 (RTC ≥0.97) — FAILS for all 3 cells** (0.890 / 0.934 / 0.967), confirming the top-
  decile-day retention: the champion's biggest days are disproportionately represented inside
  scaled weeks.
- **Gate 5 (net retention ≥0.97) — FAILS for all 3 cells** (0.849 / 0.909 / 0.955), the
  clearest single number: this policy taxes the core edge far beyond the house 3% tolerance
  even at the mildest cell (s=0.85, 15% haircut on 9.9% of days costs 4.5% of total net).
- **Gate 6 (old-regime AND-gate proxy) — PASSES for all cells** (not cell-specific):
  `out/oldregime_proxy.csv`, E10-only 2006-2021 curve (834 hist weeks, 781 burn-eligible, own
  12mo burn-in from 2007-01-06). AND-gate weeks (both top tercile, n=184) show mean next-week
  downside of −$835.6 vs −$490.1 for non-flagged weeks (diff −$345.5, Welch t=−4.29,
  p<0.0001) — same sign as the dev-side finding (higher-risk state ⇒ more negative next-week
  downside), classified SAME_SIGN, no reversal. This is the diagnostic's own confirmation
  surviving into the old regime; it does **not** rescue the policy, since gates 1/2/4/5 already
  kill it independently.

## INFERENCE: old-regime AND-gate base rate is skewed — a disclosed, inherited limitation, not a bug

In the 2006-2021 proxy, top-tercile frequency for sigma460 alone is **60.2%** (not ~33%), for
ER150 alone **38.8%**, giving the 23.6% AND-gate rate. This mirrors a skew already present in
SMV2Y's own quintile-based old-regime proxy (`old_regime_proxy.csv`: sigma460 n_q5=376/780 =
48.2% vs the nominal 20%). Root cause (INFERENCE): the expanding-rank machinery ranks each week
against the *entire* history from the absolute start of the 2006-2021 series; if sigma460's
level trended upward over that 16-year span (non-stationary mean), later weeks are compared
against a distribution anchored partly on an earlier, lower-level regime, inflating their rank.
This is identical machinery to what SMV2Y itself used for its own proxy (no independent choice
made here), and does not affect gate 6's REVERSAL/SAME_SIGN classification test, which is a
sign check, not a base-rate calibration check — but it does mean the old-regime AND-gate
"23.6% of weeks flagged" should not be read as validating the dev-side ~13% trigger rate; the
two regimes' tercile calibrations are not directly comparable in level, only in relative sign.

## House bootstrap (non-gating context, `out/policy_cells.csv`)

`block_bootstrap_delta`, seed=20260808. Daily (block=5): mean policy−unscaled delta is
negative at every s (e.g. −$23.57/day at s=0.5, 95.5% of bootstrap draws ≤0). Weekly
(block=4, matching SMV2Y's own `BLOCK_WEEKS`): same sign, −$116.61/week at s=0.5, 95.0%
of draws ≤0. Both confirm the negative-retention finding is not a small-sample artifact of
the point estimate.

## Honesty labels

Every number in the tables above traces to `out/policy_cells.csv`, `out/placebo.csv`,
`out/chronology.csv`, `out/oldregime_proxy.csv`, `out/policy_daily.csv`,
`out/step0_quintile_repro.csv`, or `out/tercile_sanity_check.csv` = **FACT**. The mechanical
explanation ("policy concentrates in the strategy's best weeks") is a **FACT** about the data
(30.3% of net PnL in 9.9% of days) combined with an **INFERENCE** about causal interpretation
(why the AND-gate correlates with strong weeks — not tested here, out of scope for a bounded
policy run). The old-regime base-rate skew explanation is **INFERENCE** (plausible
non-stationarity mechanism, not independently verified against a segmented/rolling-window
re-estimate, which would itself be a threshold-search move barred by `no_moves`). No
HYPOTHESIS-level claims are made; this is a mechanical gate-battery run per a frozen spec.

## no_moves compliance

No threshold search on the tercile cut (fixed n_bins=3 throughout), no AND-gate logic
variants, no s outside {0.5, 0.7, 0.85}, no continuous-score variant. All 3 cells tested and
reported; kill decision applied mechanically per the frozen gate battery — no gate was
re-run, relaxed, or reinterpreted after seeing results.

## Outputs

`out/policy_cells.csv`, `out/placebo.csv`, `out/chronology.csv`, `out/oldregime_proxy.csv`
(the 4 spec-named artifacts), plus `out/policy_daily.csv`, `out/step0_quintile_repro.csv`,
`out/tercile_sanity_check.csv`, `out/run_log.txt` (supplementary, supporting every claim
above). `runs/SMV2Z_VIABILITY_POLICY/smv2z.py` is the single source script for all outputs.
