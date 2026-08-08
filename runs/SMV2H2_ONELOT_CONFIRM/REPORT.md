# SMV2H2_ONELOT_CONFIRM — R2 confirmation of the A-dominant one-lot family (seq 358-360)

_2026-08-08. Spec frozen before execution: `runs/SMV2H2_ONELOT_CONFIRM/spec.yaml`.
Seq 358 = A_dom_s5 (dev cell 350), 359 = A_dom_s7 (dev cell 351, plateau center),
360 = A_dom_s9 (dev cell 357). Reference = SM14 oldM(3,1) (dev cell 355).
Executors: `confirm_gate_a.py`, `confirm_gate_b.py` (this run dir). All numbers below
come from files in `out/`._

## Verdict

**CONFIRMATION FAILED — both gates fail mechanically. SM14-form is retained as
ONE_CONTRACT_FINAL** (per the frozen decision rule). A-dominant is recorded
CONFIRMATION-FAILED with failing gates named:

- **Gate A (dev paired bootstrap): FAIL on both instruments.** Center s7 requires
  P(dSharpe>0) >= 0.85 AND P(dCDaR>0) >= 0.85. Measured (out/gate_A.csv):
  MNQ 0.7169 / 0.6391; NQ 0.7117 / 0.6318. Neither statistic reaches 0.85 on either
  instrument.
- **Gate B (2006-2021 non-inferiority): FAIL on the net criterion.** net(A_dom_s7)
  = $29,708.80 vs net(SM14) = $46,866.36 -> gap -$17,157.56 < -$10,000 threshold
  (out/gate_B_summary.json). The DD and churn criteria pass by wide margins.

Per spec `fail_any_gate`: next action = ONE new bounded discrete-policy family
(V4 §51), separate spec. This is a clean preregistered kill, not a data problem.

## Reproduction / reconciliation (FACT)

`out/crosscheck_dev.csv`: the four dev policy curves (350/351/357/355) were
regenerated on both instruments from the committed state pipeline (smv2h.py
construction, verbatim) and reconcile EXACTLY against the canonical saved outputs:
max abs daily difference vs `runs/SMV2H_ONECONTRACT/out/daily_curves.csv` = 0.0 for
all four MNQ curves; net/Sharpe/maxDD/CDaR5/fills and nq_net/nq_sharpe/nq_maxDD all
match `results.csv` with zero delta. n = 1,139 dev sessions (2022-01-03 -> 2026-05-29).

## Gate A — dev paired moving-block bootstrap (FACT)

Method: paired block bootstrap on the paired daily PnL vectors, block = 5,
B = 10,000, seed = 20260808, house index construction (circular blocks exactly as
`src/analytics/smv2_common.boot_ci_mean`: starts ~ U[0,n), wrap mod n, truncate to
n); one index set shared by challenger and reference within every comparison
(paired). Statistic 1: dSharpe = Sharpe(A_dom) - Sharpe(SM14) per path
(mean/std*sqrt(252), ddof=1). Statistic 2: dCDaR = CDaR_0.95(SM14) - CDaR_0.95(A_dom)
per path (positive = challenger better).

**CDaR_0.95 definition (as required by spec):** the mean of the worst 5% of daily
drawdown values on the cumulative EOD equity curve, where the drawdown series is
d_t = (running peak of cumulative equity) - (cumulative equity at t); worst-k count
k = max(1, int(0.05*n)) = 56 days of 1,139. Point CDaR under this definition
reproduces the saved `results.csv` CDaR5 to 0.0 (crosscheck_dev.csv).

From `out/gate_A.csv`:

| seq | policy | inst | Sharpe (vs SM14) | CDaR (vs SM14) | pt dSharpe | pt dCDaR | P(dShp>0) | P(dCDaR>0) | role | pass |
|---|---|---|---|---|---|---|---|---|---|---|
| 358/350 | A_dom_s5 | MNQ | 1.302 vs 1.056 | 3,285 vs 4,457 | +0.246 | +1,172 | 0.808 | 0.587 | plateau (point) | PASS |
| 358/350 | A_dom_s5 | NQ | 1.370 vs 1.120 | 32,322 vs 43,567 | +0.251 | +11,245 | 0.812 | 0.582 | plateau (point) | PASS |
| **359/351** | **A_dom_s7** | **MNQ** | 1.241 vs 1.056 | 3,101 vs 4,457 | +0.186 | +1,356 | **0.717** | **0.639** | **CENTER gate** | **FAIL** |
| **359/351** | **A_dom_s7** | **NQ** | 1.300 vs 1.120 | 30,558 vs 43,567 | +0.181 | +13,009 | **0.712** | **0.632** | **CENTER gate** | **FAIL** |
| 360/357 | A_dom_s9 | MNQ | 1.288 vs 1.056 | 3,257 vs 4,457 | +0.232 | +1,199 | 0.753 | 0.624 | plateau (point) | PASS |
| 360/357 | A_dom_s9 | NQ | 1.340 vs 1.120 | 32,062 vs 43,567 | +0.221 | +11,505 | 0.740 | 0.616 | plateau (point) | PASS |

90% bootstrap bands for the center (s7): dSharpe [-0.356, +0.724] MNQ,
[-0.362, +0.719] NQ; dCDaR [-$2,587, +$4,322] MNQ, [-$25,245, +$41,220] NQ — all
straddle zero. Plateau support (s5/s9 point deltas > 0 on both instruments) PASSES,
but is moot given center failure.

INFERENCE: every point estimate favors the challenger (all 6 point dSharpe and all
6 point dCDaR positive), but 4.4 years of dev data cannot certify the improvement
at the preregistered 0.85 confidence bar — same underpowering the SMV2H Level-F
diagnostics showed (P(dSharpe>0) 0.71-0.80 there; reproduced here under the
preregistered paired design).

## Gate B — old-regime (2006-2021) non-inferiority stress

### Substrate verification first (FACT, required before history was run)

`out/vote_tdd_verify.json`: on the dev substrate, T = clip(rha(10*vote_pend/13), +-10)
reproduces the SM01 `e10_bar_pnl.parquet` tgt on **519,714 of 519,714 dev bars
(0 mismatches)**, and the full vote->T-dd (DUAL_HTF) construction built from
`vote_state_3m.parquet` vote_pend equals gate A's T-dd series (built from tgt) on
**all 519,714 dev bars (0 mismatches)**. Sample sessions:
`out/vote_tdd_verify_samples.csv`. The hist substrate's vote_pend was generated by
the same committed code path (SM06 `run_hist.py`, `sm01_solarsim.member_trades`
pend sum), so the bridge to 2006-2021 is exact by construction.

### Replay conventions (disclosed)

2006-01-05 -> 2021-12-31, Solar-only (B-MOM silent): A_dom_s7 pos = sign(T_dd) iff
|T_dd| >= 7; SM14 pos = hysteresis(a=3,b=1) on M = 0.7086*T_tilt with B = 0
(hysteresis verbatim from smv2h.py `pol_hyst`). HTF = prior-session close vs SMA50
of session closes, causal on the hist substrate. Decisions at 3m close; fills at
NEXT 3m close +-1 tick slip, uncapped (substrate has NO OHLC — disclosed
approximation, identical for both policies); session-close flatten at last-bar
close -+1 tick; dev ops windows kept verbatim (flatten decided 16:39, freeze
16:30-18:03). NQ basis only: $2.18/side, point value $20.

### Results (FACT, from out/gate_B_oldregime.csv / gate_B_summary.json / gate_B_yearly.csv)

| | A_dom_s7 | SM14 | criterion | result |
|---|---|---|---|---|
| Net 2006-2021 | $29,708.80 | $46,866.36 | net_A >= net_SM14 - $10,000 (gap -$17,157.56) | **FAIL** |
| maxDD (EOD) | $21,101.92 | $59,122.92 | <= 1.25x (ratio 0.357) | PASS |
| Round-trips/yr | 147.4 | 354.1 | <= 1.5x (ratio 0.416) | PASS |
| Fills/yr | 294.8 | 706.3 | <= 1.5x (ratio 0.417) | PASS |
| Sharpe | 0.230 | 0.174 | (informational) | — |

**Gate B: FAIL** (net non-inferiority only).

Kill screen (spec requires prominent reporting either way): **no year of either
policy is below -$25k NQ.** Worst A_dom_s7 year: 2021, -$9,231.20. Worst SM14 year:
2009, -$14,661.00.

INFERENCE (composition of the failure): A_dom_s7 beats SM14 head-to-head in 11 of
16 old years (out/gate_B_yearly.csv); the entire net gap is 2020-2021
(delta -$17,562 and -$66,963), where SM14's hysteresis rode the melt-up (+$29,037,
+$57,732) while strong-consensus-only Solar sat out (2021: -$9,231). The challenger
is materially lower-risk on the old regime (1/3 the maxDD, higher Sharpe, 40% of
the churn) — but the frozen gate is a net non-inferiority gate, and it fails it.
HYPOTHESIS (not tested here, for a future spec only): the s7 consensus filter
removes exactly the long-side persistence that pays in strong trend years; any
successor family must retain trend-year participation, not just cut churn.

## LOYO (verification only, FACT)

`out/loyo.csv` reproduces the published ONE_CONTRACT_FRONTIER addendum for 350/MNQ
exactly: dnet 2022 -$2,161, 2023 +$1,179, 2024 +$1,023, 2025 +$3,896, 2026 +$3,390;
dSharpe -0.42/+0.24/+0.28/+0.44/+1.06. For the center s7/MNQ: dnet -$3,208/+$308/
+$788/+$934/+$4,230 — 4/5 years positive but magnitude concentrated in 2026, and
2022 negative. Same shape on NQ.

## Right tail — top-10-day retention (FACT; warning threshold <90%)

`out/top10_retention.csv`: on SM14's 10 best dev days, A_dom_s7 captures
$12,186.10 of $15,780.60 (MNQ) and $122,059.72 of $157,918.32 (NQ) —
**retention 0.772 / 0.773: the <0.90 warning FIRES on both instruments.** Biggest
single miss: 2024-08-08 (SM14 +$1,157.70 MNQ, A_dom_s7 +$3.10). Overlap of own
top-10 days: 6/10. This independently corroborates the gate A failure: part of the
challenger's risk reduction comes from shedding right-tail days, not only bleed.

## Compliance

- No market data dated >= 2026-08-01 read or used. Dev = sessions <= 2026-05-31
  (prefix mask applied immediately after load; June/July 2026 rows in shared files
  excluded; hist substrate ends 2021-12-31).
- No git commands, no NT8/CrossTrade; all writes confined to
  `runs/SMV2H2_ONELOT_CONFIRM/`.
- Seeds/bootstrap exactly per spec: block=5, B=10,000, seed=20260808.

## Artifacts

`out/regen_daily_curves.csv`, `out/crosscheck_dev.csv`, `out/gate_A.csv`,
`out/gate_A_summary.json`, `out/loyo.csv`, `out/top10_retention.csv`,
`out/tdd_dev_from_tgt.npy`, `out/vote_tdd_verify.json`,
`out/vote_tdd_verify_samples.csv`, `out/gate_B_oldregime.csv`,
`out/gate_B_yearly.csv`, `out/gate_B_daily_curves.csv`, `out/gate_B_summary.json`.
