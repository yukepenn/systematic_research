# WE_W36 — QUALITY LAYER WALK-FORWARD + ATTRIBUTION · REPORT

## A — VERDICT: **FAIL** on the preregistered Sharpe rule, and the quote is corrected

| object | pts/session | weekly | % weeks + | worst week | **Sharpe** |
|---|---|---|---|---|---|
| **WF_QUALITY (honest refit)** | **14.41** | **$1,545** | 59.3 % | **−$7,418** | **0.303** |
| FIXED_A3 (what W35 quoted) | 17.78 | $1,774 | 59.1 % | −$7,418 | 0.338 |
| BASE (no quality layer) | 10.62 | $1,060 | 59.1 % | −$7,487 | 0.305 |
| BESTFIXED (4, 120, 2000) | — | — | — | — | 0.338 |

WF (0.303) does not exceed BASE (0.305) → **FAIL**. Choice churn 67 % across 16 refits, the
same selection noise W19 diagnosed. **The quality layer's SHARPE advantage is fitted.**
From here the honest quote is **14.41 pts/session at Sharpe ≈ 0.303**, not 17.78 at 0.338.

### But the production gain IS out-of-sample, and on the stated objective it wins

Walk-forward delivers **+36 % points/session and +46 % weekly mean with the worst week
unchanged** (−$7,418 vs −$7,487). Per unit of tail:

| | weekly | worst week | weekly ÷ |worst| |
|---|---|---|---|
| BASE | $1,060 | −$7,487 | 0.142 |
| **WF_QUALITY** | **$1,545** | −$7,418 | **0.208 (+47 %)** |

Sharpe penalises upside variance; the owner's objective ("赚最多、回撤最少") is a **tail**
objective. By the preregistered Sharpe rule the layer fails; by the profit-versus-drawdown
rule it clearly passes. **Both are reported; neither is hidden.**

## B — the quantile surface is FLAT, so the layer is not knife-edge

Perturbing each cut point one at a time moves Sharpe by −0.024 … +0.009. (`prior-ret q=0.50`
scores 18.43 / 0.346, better than baseline — not adopted, that would be exactly the selection
the walk-forward just penalised.)

## C1 — where the improvement actually comes from

| step | pts/session | Δ pts | Sharpe | Δ Sharpe |
|---|---|---|---|---|
| base vote + box | 10.62 | — | 0.305 | — |
| **+ quality sizing** | 15.86 | **+5.24** | 0.331 | **+0.026** |
| + cut low-quality 120 bars | 17.10 | +1.24 | 0.338 | +0.007 |
| + big target on quality | 17.78 | +0.68 | 0.338 | **−0.000** |

Sizing is the whole story; the cut is a small real addition; **the big target contributes
nothing**, confirming W35's A1 rejection from a second direction. It should be dropped for
parsimony — and dropping it removes one of the three parameters that caused the 67 % churn.

## C2 — HOW WE MAKE THE MONEY (the answer to the owner's question)

**By score bucket** — 21 % of trades deliver 79 % of the profit:

| score | trades | avg size | net | $/trade | share |
|---|---|---|---|---|---|
| 0 | 466 | 1.00 | −$3,377 | **−$7.2** | −0.9 % |
| 1 | 763 | 1.00 | $41,683 | $54.6 | 11.6 % |
| 2 | 440 | 1.00 | $35,957 | $81.7 | 10.0 % |
| **3** | **324** | 2.00 | **$210,075** | **$648.4** | **58.3 %** |
| **4** | 106 | 2.00 | $65,626 | $619.1 | 18.2 % |
| 5 | 14 | 2.00 | $10,208 | $729.1 | 2.8 % |

**By regime** — and this is a reversal of W08:

| | trades | net | $/trade | share |
|---|---|---|---|---|
| big days (≥500 pts available) | 185 | $125,288 | $677.2 | 34.8 % |
| **small days** | 1,928 | **$234,883** | $121.8 | **65.2 %** |

W08 measured small days at **−1.87 % capture, −$102k**. With the session box and the quality
layer they are now the **majority of the profit**. The defensive treatment turned the 83 % of
sessions that used to bleed into the larger half of the P&L.

**By ET segment** — Asia is the single biggest contributor:

| segment | trades | net | $/trade | share |
|---|---|---|---|---|
| ASIA 18:00–03:00 (both blocks) | 630 | $154,243 | $231–284 | **42.8 %** |
| RTH_PM | 173 | $64,377 | $372.1 | 17.9 % |
| RTH_AM | 574 | $52,457 | $91.4 | 14.6 % |
| PREOPEN | 139 | $44,494 | $320.1 | 12.4 % |
| EUROPE | 581 | $38,963 | $67.1 | 10.8 % |

## C3 — sizing did NOT make the object more fragile
Top-5 %-of-days share **96.8 % → 94.6 %**; worst day −$5,118 → −$5,933. Concentration fell.

## What this dictates next
The walk-forward failed **because of choice churn across three free parameters**, and C1 shows
one of them (big target) is worthless while B shows the surface is flat. The correct response
is not to tune — it is to **remove the free parameters**: a parameter-free continuous sizing
rule with no score threshold to churn on. That is W37.
