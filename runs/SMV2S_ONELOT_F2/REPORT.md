# SMV2S_ONELOT_F2 — HTF-GATED DOMINANT one-lot family (seq 386-388)

_2026-08-08. Spec frozen before execution at 58dc2d2: `runs/SMV2S_ONELOT_F2/spec.yaml`.
Seq 386 = HTFG_dom(thr3), 387 = HTFG_dom(thr5) (CENTER), 388 = HTFG_dom(thr7).
Reference = SM14 oldM(3,1) (dev cell 355). Executors: `f2_dev_gates.py`, `f2_gate_c.py`
(this run dir). Every number below comes from files in `out/`._

Policy under test (spec verbatim; side-blind HTF gate on the Solar leg, B-MOM priority):

    pos_t = sign(B_t)        if B_t != 0
          = sign(T_dd_t)     if B_t == 0 AND |T_dd_t| >= thr AND HTF_state == sign(T_dd_t)
          = 0                otherwise

## Verdict

**FAMILY KILLED — all three preregistered gates fail mechanically on the center cell
(thr 5). SM14-form remains ONE_CONTRACT_FINAL holder.**

| Gate | Requirement (center thr5) | Measured | Result |
|---|---|---|---|
| A dev bootstrap | P(dSharpe>0) >= 0.85 AND P(dCDaR>0) >= 0.85, both instruments | MNQ 0.6406 / 0.4860; NQ 0.6361 / 0.4799 | **FAIL** |
| B right tail (HARD) | top-10-day retention vs SM14 >= 0.90, both instruments | 0.8412 MNQ / 0.8415 NQ | **FAIL** |
| C old regime 2006-2021 | net >= SM14 - $10k | $10,815.84 vs $46,866.36 (gap **-$36,050.52**) | **FAIL** (DD and churn criteria pass) |

This is the **second consecutive one-contract family kill** (A-dominant
CONFIRMATION-FAILED in SMV2H2; HTF-gated dominant killed here). Per the frozen spec
decision rule, **the one-contract frontier pauses for a mechanism-expansion pass** —
the next wave must not be a variant of consensus-threshold or HTF-gate mechanisms.

## Reproduction / reconciliation (FACT — required before any new read)

`out/sm14_reconcile.csv`: the SM14 reference was regenerated from the committed
state pipeline (smv2h.py construction, verbatim) on both instruments and matches
`runs/SMV2H2_ONELOT_CONFIRM/out/regen_daily_curves.csv` **EXACTLY: max abs daily
difference = 0.0** for `355_SM14_ref_oldM(3,1)_MNQ` and `_NQ`. As extra evidence the
three A-dominant cells (350/351/357) were also regenerated: 0.0 on all six columns.
n = 1,139 dev sessions (2022-01-03 -> 2026-05-29), 519,714 dev bars.

Disclosure: the comparison reads the CSV with pandas `float_precision="round_trip"`.
The default pandas parser is off by a few ulp from the stored decimal strings
(max 3.6e-12 on NQ magnitudes); under round_trip parsing, SMV2H's canonical
`daily_curves.csv` and SMV2H2's regen also agree at exactly 0.0, so 0.0 here is a
bit-exact reproduction of the committed curves, not a tolerance pass.

## Dev cells (FACT, from out/cells.csv; 2022-01-03 -> 2026-05-29)

| seq | policy | MNQ net | MNQ Sharpe | MNQ maxDD | MNQ CDaR5 | NQ net | NQ Sharpe | NQ maxDD | fills |
|---|---|---|---|---|---|---|---|---|---|
| 355 | SM14 ref | $28,676.10 | 1.056 | $5,963.20 | $4,456.54 | $303,850.92 | 1.120 | $58,517.44 | 3,868 |
| 386 | HTFG thr3 | $30,660.70 | 1.099 | $4,806.10 | $3,207.84 | $323,938.84 | 1.162 | $47,698.12 | 3,540 |
| **387** | **HTFG thr5 (center)** | $32,022.70 | 1.169 | $4,500.80 | $3,207.36 | $336,349.24 | 1.229 | $44,783.36 | 3,301 |
| 388 | HTFG thr7 | $32,628.80 | 1.269 | $4,009.60 | $3,056.02 | $339,930.56 | 1.323 | $39,949.12 | 2,807 |

All 12 point deltas vs SM14 (Sharpe and CDaR, 3 cells x 2 instruments) are positive
(out/gate_A.csv) — the family is pointwise better on dev everywhere. The gates below
test whether that is certifiable; it is not.

## Gate A — dev paired moving-block bootstrap (FACT): FAIL

Preregistered method, identical to SMV2H2: paired block bootstrap on the paired
daily PnL vectors, block = 5, B = 10,000, seed = 20260808, house circular index
construction, one index set shared within every comparison. Statistic 1: dSharpe per
path; statistic 2: dCDaR_0.95 per path (positive = challenger better;
k = max(1, int(0.05*n)) = 56 worst drawdown days of 1,139).

From `out/gate_A.csv`:

| seq | inst | pt dSharpe | pt dCDaR | P(dShp>0) | P(dCDaR>0) | role | pass |
|---|---|---|---|---|---|---|---|
| 386 thr3 | MNQ | +0.043 | +$1,249 | 0.559 | 0.451 | plateau (point) | PASS |
| 386 thr3 | NQ | +0.042 | +$12,088 | 0.558 | 0.449 | plateau (point) | PASS |
| **387 thr5** | **MNQ** | +0.113 | +$1,249 | **0.641** | **0.486** | **CENTER gate** | **FAIL** |
| **387 thr5** | **NQ** | +0.109 | +$11,989 | **0.636** | **0.480** | **CENTER gate** | **FAIL** |
| 388 thr7 | MNQ | +0.213 | +$1,401 | 0.738 | 0.636 | plateau (point) | PASS |
| 388 thr7 | NQ | +0.203 | +$13,461 | 0.727 | 0.628 | plateau (point) | PASS |

90% bands for the center straddle zero on both statistics and both instruments
(dSharpe [-0.417, +0.647] MNQ; dCDaR [-$3,613, +$3,542] MNQ; out/gate_A.csv).
Plateau point-support passes, but is moot given center failure.

INFERENCE: P(dCDaR>0) is below 0.5 for thr3 and ~0.48 for thr5 — the CDaR point
improvement is not even majority-stable under resampling for the lower thresholds.
The center misses the 0.85 bar by more than A-dominant s7 did on dSharpe
(0.64 here vs 0.72 there); certification power, not direction, remains the binding
constraint on this 4.4-year dev window.

## Gate B — top-10-day retention (HARD, FACT): FAIL

From `out/gate_B_retention.csv` (SM14's 10 best dev days; retention =
sum(cell PnL on those days) / sum(SM14 PnL on those days)):

| seq | MNQ retention | NQ retention | overlap of own top-10 |
|---|---|---|---|
| 386 thr3 | 0.8553 | 0.8555 | 7/10 |
| **387 thr5 (gate)** | **0.8412** | **0.8415** | 6/10 |
| 388 thr7 | 0.8204 | 0.8206 | 6/10 |

Hard gate >= 0.90 on both instruments: **FAIL** (0.8412 / 0.8415). The mechanism did
move the diagnosed weakness in the intended direction — A-dominant s7 retained 0.772/0.773
(SMV2H2) vs 0.841/0.842 here — but is still 6 points short of the bar. The single
biggest miss is again 2024-08-08 (SM14 +$1,157.70 MNQ, cell -$211.60), the same day
that led A-dominant's misses.

INFERENCE: the residual right-tail loss is not counter-HTF churn (the gate deletes
that by construction) — it is big Solar days where |T_dd| sat below threshold or the
HTF state disagreed at the moment of the move (2024-08-08 was a rebound day inside
an HTF-down regime, exactly what a side-blind agreement gate must skip).

## Gate C — old-regime (2006-2021) Solar-only non-inferiority (FACT): FAIL

Replay conventions identical to SMV2H2 gate B (disclosed approximation): decisions
at 3m close, fills at NEXT 3m close +-1 tick (uncapped; hist substrate has no OHLC),
identical for both policies; session-close flatten at last-bar close; dev ops windows
verbatim; NQ basis $2.18/side, PV $20. In Solar-only mode B is silent, so the policy
reduces to HTF-gated Solar: pos = sign(T_dd) iff |T_dd| >= thr AND HTF == sign(T_dd).

Substrate bridge verification re-run before history (out/vote_tdd_verify.json):
T = clip(rha(10*vote_pend/13), +-10) reproduces e10 tgt on **519,714/519,714 dev
bars (0 mismatches)**, and the full vote->T-dd construction equals the dev gates'
T-dd (out/tdd_dev_from_tgt.npy) on all 519,714 bars.

From `out/gate_C_oldregime.csv` / `gate_C_summary.json` (center = HTFG_s5):

| | HTFG_s5 (center) | SM14 | criterion | result |
|---|---|---|---|---|
| Net 2006-2021 | $10,815.84 | $46,866.36 | net >= SM14 - $10,000 (gap -$36,050.52) | **FAIL** |
| maxDD (EOD) | $32,743.48 | $59,122.92 | <= 1.25x (ratio 0.554) | PASS |
| Entries/yr | 202.7 | 354.1 | <= 1.5x (ratio 0.572) | PASS |
| Fills/yr | 405.3 | 706.3 | <= 1.5x (ratio 0.574) | PASS |
| Sharpe | 0.072 | 0.174 | (informational) | — |

Informational neighbors: HTFG_s3 net $35,928.16 (gap -$10,938, would also fail c1);
HTFG_s7 net $11,957.36. **Gate C: FAIL** on net non-inferiority.

Kill screen (prominent either way): **no year of any policy is below -$25k NQ**
(out/gate_C_summary.json). Worst center year: 2015, -$8,618.84. Worst SM14 year:
2009, -$14,661.00.

INFERENCE (composition, from out/gate_C_yearly.csv): 2021 alone is -$55,703 of the
-$36,051 gap (SM14 +$57,732 vs HTFG_s5 +$2,029); ex-2021 the center is AHEAD of SM14
by ~$19.7k. 2021 was an HTF-UP melt-up year, so the side-blind gate was open — the
Solar leg still sat out because |T_dd| >= 5 rarely held. This isolates the failure to
the consensus-threshold component, not the HTF gate: SM14's hysteresis (enter at
|M|>=3, exit only below 1) holds through weak-consensus stretches, while every
threshold-dominant family re-evaluates each bar and goes flat when consensus dips.
HYPOTHESIS (for the mechanism-expansion pass, not tested here): trend-year
participation requires entry/exit asymmetry (persistence), which no memoryless
per-bar threshold policy in this class can supply.

## Decision (mechanical, per frozen spec)

- fail any -> **family killed.** Recorded: gates A, B, C all failed on the center cell.
- Second consecutive family kill (SMV2H2 A-dominant, SMV2S HTF-gated dominant) ->
  **one-contract frontier pauses for a mechanism-expansion pass** (V4 §51 clause in
  the frozen spec). SM14-form stays ONE_CONTRACT_FINAL.

## Compliance

- No market data dated >= 2026-08-01 read or used. Dev = sessions <= 2026-05-31
  (prefix mask asserted immediately after load; June/July 2026 rows excluded before
  any use; hist substrate ends 2021-12-31). No recency artifacts touched.
- SM14 reference reconciled EXACTLY against SMV2H2 regen curves before any new read.
- No git commands, no NT8/CrossTrade tools; all writes confined to
  `runs/SMV2S_ONELOT_F2/`.
- Bootstrap exactly per house spec: block=5, B=10,000, seed=20260808.

## Artifacts

`out/sm14_reconcile.csv`, `out/cells.csv`, `out/dev_daily_curves.csv`,
`out/tdd_dev_from_tgt.npy`, `out/gate_A.csv`, `out/gate_B_retention.csv`,
`out/dev_gates_summary.json`, `out/vote_tdd_verify.json`,
`out/gate_C_oldregime.csv`, `out/gate_C_yearly.csv`, `out/gate_C_daily_curves.csv`,
`out/gate_C_summary.json`.
