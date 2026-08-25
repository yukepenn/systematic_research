# WE_W21 — VOTE AUDIT · REPORT

E5 = one-contract majority vote (≥50 %) across the 32 long-only configs. All four attacks run.

## A2 NULL CALIBRATION (binding) — **EVIDENCE**, the campaign's strongest

| real | null mean | null p95 | **percentile** | **p** |
|---|---|---|---|---|
| 0.214 | 0.042 | 0.147 | **98.0** | **0.020** |

100 common circular shifts of every config's position path — block rate and autocorrelation
preserved exactly, only market alignment destroyed. E5 sits above the 98th percentile. For
comparison, the range throttle (W13) sat exactly at 95.0 / p = 0.05, and two other headline
gates were killed at 73 and 78. **This is the first object in the campaign to clear its null
decisively rather than marginally.**

## A4 SUBFAMILY SENSITIVITY — robust (spread 0.034 < 0.05)

| dropped | Sharpe | Δ |
|---|---|---|
| members = narrow5 | 0.225 | +0.011 |
| members = narrow6 | 0.215 | +0.001 |
| members = narrow7 | 0.212 | −0.001 |
| members = all13 | 0.191 | −0.023 |
| q = none / 0.7 / 0.8 / 0.9 | 0.213 / 0.213 / 0.206 / 0.207 | −0.000 … −0.008 |

No single subfamily carries the result — the vote is not a disguised selection.

## A3 ORTHOGONAL COMBINATION

| object | Sharpe | net | wk mean | % pos | worst |
|---|---|---|---|---|---|
| S1 alone | 0.172 | $284,548 | $1,388 | 54.1 % | −$20,957 |
| E5 alone (1 contract) | 0.214 | $227,009 | $1,118 | 59.6 % | **−$17,440** |
| **E5 + S1 (≤2 contracts)** | **0.241** | **$511,557** | **$2,495** | 58.0 % | −$26,850 |

corr(E5, S1) = **0.18** — genuinely orthogonal. The combination buys +0.027 Sharpe and doubles
the money, at the cost of a tail that grows roughly with exposure. **The tail is now the only
open weakness**, which is what W22 attacks.

## A1 DEEP HISTORY (2006–2021, unchanged E5)

Pooled **Sharpe +0.056**, net $65,632, 47.4 % positive weeks, worst week −$8,447, stress −$44.
**8/16 positive years** → verdict **modern-regime object**, as the owner's regime-conditional
stance already accepted. Two things worth recording:

- E5 is *positive* pre-2022 where the fixed stack was *negative* (−0.001). Selection-freedom
  travels better than calibration does.
- The year pattern is monotone-ish: 2006–2009 all negative, 2013 onward mostly positive,
  2020 **+0.274**, 2021 +0.043. **The object has been getting better as NQ became more
  algorithmic and trend-persistent** — consistent with the regime story rather than with luck.

## Status
E5 (and E5+S1) is the campaign's first object to pass a null, a sensitivity audit and an
orthogonality check simultaneously. It is still not promoted: promotion requires the tail work
in W22 and a final adversarial pass.
