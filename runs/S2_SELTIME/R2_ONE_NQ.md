# S2_SELTIME R2 — BEST_ONE_NQ adjudication

**STATUS: NOT PROMOTED**

Per `r2_spec.yaml`'s frozen interpretation: S2 integrated directly into the hysteresis(3,1)
position state machine (EntryLevel=3.0/ExitLevel=1.0 untouched), checked against the LAGGED
physical position, able to suppress a new entry or reversal only — never an exit. Code:
`src/r2_battery.py` (`one_contract_decisions`, `onelot_exec`), `src/r2_metrics.py`.
Independently adversarially verified — **CONFIRMED, no bug found**; hysteresis logic traced
line-for-line against `SolarWaveOneContractNQ_v4.cs` and matches exactly; every number in
`out/r2/summary_NQ.json` reproduces exactly from the raw saved arrays.

## Headline numbers (incumbent -> +S2)

| metric | incumbent | +S2 | delta |
|---|---:|---:|---:|
| Net | $301,915.92 | $306,253.44 | +$4,337.52 |
| Sharpe | 1.1131 | 1.1394 | +0.0264 |
| CDaR₀.₉₅ | $44,518.39 | $42,517.69 | +$2,000.70 (better) |
| maxDD (EOD) | $59,717.44 | $53,471.92 | better |
| Capital needed (1x stress, 20% DD-thr) | $550,164 | $541,549 | −$8,615 (better) |

(Incumbent Sharpe 1.1131 is within 1% of the independent reference anchor 1.1197 from
`PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py` — confirms no scale/lookahead artifact.)

## Gate results

| gate | result |
|---|---|
| A (Sharpe↑ AND CDaR↑ AND top10-retention≥95%) | **PASS** |
| B (chronology, ≥4/5 years agree) | **FAIL, decisively** — only 2/5 years positive (2022 −0.137, 2023 −0.019, 2026 −0.166 negative; 2024 +0.468, 2025 +0.010 positive) |
| C (tail preservation) | **FAIL, decisively** — top-1% bar retention **71.8%**, top-20-move retention **64.9%** (both far below the 90% bar); long-share drift 3.8pp (inside 15pp) |

Gate A alone is not sufficient; per the frozen rule all three are required. This fails 2 of 3,
both decisively, not narrowly.

## The tail-degradation mechanism is real and understood, not a bug

The independent verifier traced the top-20-move divergence to actual dates: **2025-04-09
03:03-07:03 ET** (the April 2025 tariff-driven volatility spike) sits inside the 02:00-08:00
blocked window, and on that morning the incumbent captured a **+$7,625 long entry that S2
correctly and legitimately suppressed** (the arm stayed flat through that specific window,
losing that entire winner). This is exactly the failure mode the discrete, all-or-nothing
one-contract position layer is vulnerable to in a way the smoother, continuously-graded Product A
E10 aggregate is not: killing a single entry at this layer removes 100% of that trade's P&L,
whereas the same eligibility suppression against a continuous target only trims exposure.

## Robustness context

- **Bootstrap P(Δmean>0) = 0.578** — essentially a coin flip, the weakest confidence reading of
  any of this campaign's evidence this wave.
- **D7-boundary split**: pre-2024-08-05 ΔSharpe +0.0009 (essentially zero), post +0.0613 (large)
  — the SAME quarter-concentration pattern flagged at the diagnostic level, reproduced and if
  anything sharper here.
- **2-tick-equivalent cost stress**: Δ Sharpe stays positive (+0.0310) — cost is not the reason
  this fails.
- **Capital map**: modestly better (~1.6% less capital needed) — real but small, and cannot
  offset two decisive gate failures.

## Why NOT PROMOTED, not INCONCLUSIVE

This is the clearest NOT PROMOTED case of the three products. Gate A passing on pooled Sharpe/
CDaR is exactly the "pooled Sharpe is larger" case the directive explicitly says is NOT
sufficient for promotion — and here it is paired with a severe, mechanistically-explained
right-tail failure (a real ~$7,625 winning entry given up on one date) and a near-coin-flip
bootstrap confidence. The evidence is decisive, not marginal.

## Disposition

`SolarWaveOneContractNQ_v4.cs` remains the incumbent. No `_v5` created. `BASELINE_MODELS.md` /
`CURRENT_TRUTH.md` updated to record that R2 ran and did not promote.
