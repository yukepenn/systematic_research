# WE_W13 — NULL CALIBRATION · REPORT (discipline wave)

Spec preregistered; amendment 1 corrected the null method to **circular shift** (block rate and
autocorrelation preserved exactly, only market alignment destroyed — the strictest available
null for "is this gate about the market, or just about trading less?"). 100 nulls per gate.

## N1 — two of my own findings are DEMOTED

| gate | block rate | real Sharpe | null mean | null p95 | percentile | p | verdict |
|---|---|---|---|---|---|---|---|
| **range throttle** | 0.299 | 0.225 | 0.184 | 0.222 | **95.0** | **0.05** | **EVIDENCE** |
| delta gate | 0.500 | 0.225 | 0.172 | 0.246 | 90.0 | 0.10 | weak |
| **wave gate** (W12 headline) | 0.500 | 0.225 | 0.204 | 0.267 | 73.0 | 0.27 | **NOT EVIDENCE** |
| **CLOSE-hour drop** (W11 finding) | 0.043 | 0.225 | 0.220 | 0.234 | 78.0 | 0.22 | **NOT EVIDENCE** |

**W12's headline (the never-used `signal_wave` gate) and W11's CLOSE-hour finding are not
distinguishable from randomly blocking the same fraction of bars with the same structure.**
Both are demoted to "not evidence" per the preregistered rule, regardless of their dev
improvement. The CLOSE-hour null has low power (4.3 % block rate), so its result is
*inconclusive* rather than refuted — but "inconclusive" is not evidence either.

## N2 — per-year stability: PASSES

| year | weeks | net | mean/wk | % pos | worst | Sharpe |
|---|---|---|---|---|---|---|
| 2022 | 52 | +$39,938 | $768 | 51.9 % | −$17,842 | 0.114 |
| 2023 | 52 | +$55,632 | $1,070 | 59.6 % | −$7,378 | 0.253 |
| 2024 | 52 | +$110,398 | $2,123 | 63.5 % | −$5,084 | 0.408 |
| 2025 | 52 | +$125,446 | $2,412 | 63.5 % | −$14,682 | 0.363 |
| 2026 (31 wk) | 31 | +$94,467 | $3,047 | 58.1 % | −$25,032 | 0.231 |

**No negative year**, and the weakest is the earliest. The stack is not a one-regime artifact.

## N3 — sensitivity: passes on the throttle, WARNS on the member set

`q` is flat (0.7 → 0.231, 0.8 → 0.225, 0.9 → 0.224): not a knife-edge parameter.
**Member set is not flat**: narrow6 0.225, narrow5 0.212, **narrow7 0.186 (−0.038)**. The
member choice is a genuine sensitivity and must be treated as a fitted parameter, not a
structural one.

## N4 — leave-one-out

| removed | Sharpe | cost | verdict |
|---|---|---|---|
| delta gate | 0.183 | **+0.041** | KEEP |
| range throttle | 0.203 | +0.022 | KEEP |
| wave gate | 0.214 | +0.011 | keep by N4, **but N1 says not evidence** |
| CLOSE drop | 0.220 | +0.004 | **DEAD WEIGHT → DROP** |

## The honest object after this wave

**EVIDENCE-ONLY STACK** = `S4.narrow6 + range throttle 0.8 + delta gate` (wave gate and
CLOSE drop removed as not-evidence):

| | capture | big-day | wk mean | % pos | worst | Sharpe | stress | holdout |
|---|---|---|---|---|---|---|---|---|
| evidence-only sleeve | 4.87 % | 17.58 % | $1,431 | 59.1 % | −$24,417 | 0.210 | $1,250 | 0.665 |
| range only (no delta) | 4.88 % | 16.90 % | $1,405 | 56.5 % | −$33,920 | 0.176 | $1,163 | 0.538 |
| **PORTFOLIO S1 + evidence-only** | **9.57 %** | **31.39 %** | **$2,830** | **61.3 %** | −$27,182 | **0.248** | $2,107 | 0.668 / **100 % weeks** |

The claimed progression is therefore corrected from **0.225 to 0.210** for the single sleeve;
the portfolio stands at 0.248 because it never used the demoted components.

## What this wave changes about how the campaign reports itself

Two waves' headlines did not survive a null they had never faced. Every future gate claim must
carry its circular-shift percentile in the same table as its Sharpe — a gate without a null is
now an unsupported claim by campaign rule, not by taste.
