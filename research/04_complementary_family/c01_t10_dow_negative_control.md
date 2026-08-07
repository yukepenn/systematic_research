# C01 T0-10 — Day-of-Week Negative Control (pipeline calibration)

_Run 2026-08-07. Frozen per `C01_WAVE_SPEC.md` item T0-10. 4 DoF charged to the control
budget. Expected result: nothing significant. Alarm condition: any weekday partition with
p < 0.05 in BOTH halves → CALIBRATION_ALARM (audit the wave's testing machinery)._

## Data

- `research/audit/e_variant_daily_vectors.csv`, column `E10_round_session` (NaN = flat, excluded).
- 1,184 trading sessions, session_dates 2022-01-03 → 2026-07-31 (Mon 235 / Tue 239 / Wed 237 /
  Thu 237 / Fri 236 — no weekend leakage; session-date roll is correct).
- Halves: H1 = 2022-07-01 → 2024-06-30 (n=516), H2 = 2024-07-01 → 2026-06-30 (n=517).
- Tests: Kruskal-Wallis across the 5 weekdays; max pairwise weekday mean diff with 10,000
  label-permutation p (seed 20260807).

## Results

| Period | n | KW H (4 dof) | KW p | Max pair diff | Pair | Perm p |
|---|---|---|---|---|---|---|
| FULL (2022-01 → 2026-07) | 1184 | 3.608 | **0.462** | $550.14 | Thu−Wed | **0.115** |
| H1 2022-07 → 2024-06 | 516 | 5.314 | **0.257** | $511.02 | Thu−Wed | **0.200** |
| H2 2024-07 → 2026-06 | 517 | 3.650 | **0.455** | $476.11 | Thu−Wed | **0.779** |

Full-period weekday means ($/session): Mon +7, Tue +191, Wed −68, Thu +482, Fri +144.
Thursday is nominally best in both halves and Wednesday nominally worst, but the gap is far
inside the permutation null (perm p 0.20 / 0.78 in H1 / H2) and the omnibus KW never
approaches significance in any window.

## Verdict

**PASS (expected null; no alarm).** No test reaches p < 0.05 in the full period or in either
half — the alarm condition (p < 0.05 in both halves) is nowhere near triggered. The Tier-0
pipeline does not manufacture significance on a known-null partition of the E10 daily vector;
other C01 Tier-0 results are not discredited by this control. No day-of-week effect exists to
exploit (and none was sought — this item is a control, not a candidate).

Per-weekday per-period stats and test rows: `c01_t10_dow_control.csv` (same directory).
Analysis script (scratchpad, session wf journal): `t010_dow.py` — pandas + scipy.stats.kruskal,
10,000 permutations.
