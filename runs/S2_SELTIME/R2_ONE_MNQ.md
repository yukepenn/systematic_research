# S2_SELTIME R2 — BEST_ONE_MNQ adjudication

**STATUS: NOT PROMOTED**

Per `r2_spec.yaml`'s frozen interpretation: IDENTICAL position-decision sequence to
BEST_ONE_NQ's (confirmed by the independent verifier: `barpos_NQ_*.npy` and `barpos_MNQ_*.npy`
are `np.array_equal` over all 519,714 bars, since signal is NQ-only for both one-contract
objects), executed independently on genuine MNQU6 prices (`runs/PRODUCTB_ONECONTRACT_FINAL/out/
mnq_3m_raw.csv`, confirmed a genuinely distinct back-adjusted series, not an NQ-scaled proxy) and
MNQ's own economics ($0.65/side, $2.00/pt). Code: `src/r2_battery.py`, `src/r2_metrics.py`.
Independently adversarially verified — **CONFIRMED, no bug found**.

## Headline numbers (incumbent -> +S2)

| metric | incumbent | +S2 | delta |
|---|---:|---:|---:|
| Net | $28,587.10 | $29,032.20 | +$445.10 |
| Sharpe | 1.0534 | 1.0798 | +0.0264 |
| CDaR₀.₉₅ | $4,507.20 | $4,302.40 | +$204.80 (better) |
| maxDD (EOD) | $6,050.70 | $5,425.10 | better |
| Capital needed (1x stress, 20% DD-thr) | $57,351 | $55,803 | −$1,548 (better) |

## Gate results — same pattern as BEST_ONE_NQ (same decision sequence)

| gate | result |
|---|---|
| A (Sharpe↑ AND CDaR↑ AND top10-retention≥95%) | **PASS** |
| B (chronology, ≥4/5 years agree) | **FAIL, decisively** — 2/5 years positive (2022, 2023, 2026 negative; 2024, 2025 positive) |
| C (tail preservation) | **FAIL, decisively** — top-1% retention **62.0%**, top-20 retention **67.5%**, long-share drift 4.0pp |

Fails 2 of 3 required gates, both decisively — same underlying cause as BEST_ONE_NQ's failure
(the 2025-04-09 tariff-crash suppressed entry and the same class of blocked-window events), since
the position sequence is identical; only the dollar scale differs.

## A caveat this R2 must disclose that the other two products do not carry

The independent verifier flagged an important scope limitation: this R2's "incumbent" baseline
for MNQ is the **Python-twin-modeled** version (Sharpe 1.0534, matching `build_parity_and_metrics.
py`'s own `ref_sharpe`=1.0557 to within 0.2%) — **not** the NT8-certified real-execution result.
Per `runs/PRODUCTB_ONECONTRACT_FINAL/REPORT.md`, the real NT8 MNQ backtest's own daily-correlation
to this Python twin is **0.8996** (below the ≥0.999 bar), still an open, uncertified item (see
`runs/V1R4_NT8_PARITY/PRODUCT_A_CERTIFICATE.md` family for the parallel Product A parity work).
This R2's incumbent-vs-S2 comparison is internally fair (both arms modeled identically), so the
DIRECTION and GATE-FAIL conclusions above are trustworthy on their own terms -- but they describe
"does S2 help the Python-modeled version of BEST_ONE_MNQ", not a claim about the real NT8 object's
absolute performance, which remains separately open per the parity certificates.

## Robustness context

- **Bootstrap P(Δmean>0) = 0.580** — near coin-flip, same weak-confidence pattern as BEST_ONE_NQ.
- **D7-boundary split**: pre +0.0020, post +0.0599 — same sharp quarter-concentration.
- **2-tick-equivalent cost stress**: stays positive (+0.0311) — cost is not the reason this fails.
- **Capital map**: modestly better (~2.7% less capital needed) — real but small.

## Why NOT PROMOTED, not INCONCLUSIVE

Same reasoning as BEST_ONE_NQ: gate A passing alone is explicitly insufficient per the directive,
and here it is paired with the same decisive chronology and right-tail failures (mechanistically
identical cause). The additional Python-twin-vs-NT8-certified caveat only strengthens the case
for NOT PROMOTED — promoting a change into an object whose own baseline is not yet independently
NT8-certified would compound two open uncertainties rather than resolve one.

## Disposition

`SolarWaveOneContractMNQ_v4.cs` remains the incumbent. No `_v5` created. `BASELINE_MODELS.md` /
`CURRENT_TRUTH.md` updated to record that R2 ran and did not promote.
