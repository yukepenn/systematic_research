# WE_W16 — SEGMENT SLEEVES / SHORT BOOK / S1 THROTTLE · REPORT

## Q1 — FALSIFIER FIRED: segmentation is not a general orthogonality source

Segment portfolio (all 5 segments as separate sleeves) dev Sharpe **0.205 vs the single
all-hours sleeve's 0.210**. ASIA's earlier admission was about ASIA specifically, not about
segmentation as a technique. The correlation matrix shows why:

| | ASIA | EUROPE | PREOPEN | RTH_AM | RTH_PM |
|---|---|---|---|---|---|
| ASIA | 1.00 | 0.41 | 0.09 | **−0.12** | **−0.14** |
| EUROPE | 0.41 | 1.00 | 0.54 | 0.28 | 0.20 |
| RTH_AM | −0.12 | 0.28 | 0.33 | 1.00 | 0.41 |

**ASIA is the only segment ANTI-correlated with the US session** (−0.12 / −0.14). Every other
pair is positive (up to 0.54). That is the mechanism behind its admission and it does not
generalise.

## Q2 — the short book is weak but real (W15's negative was a small-sample artifact)

Full 4.6 years:

| sleeve | long $/trade | short $/trade | ratio |
|---|---|---|---|
| S1 | 41.8 | 16.5 | 2.5× |
| S4n | 143.3 | 50.4 | 2.8× |
| ASIA | 245.1 | 117.5 | 2.1× |

Shorts make money everywhere, at roughly **one third the per-trade rate of longs**, on every
sleeve independently. Variants:

| variant | wk mean | % pos | worst | Sharpe | stress | tr/wk |
|---|---|---|---|---|---|---|
| S4n both sides | $1,431 | 59.1 % | −$24,417 | 0.210 | $1,250 | 18.1 |
| **S4n LONG-ONLY** | $1,101 | 57.1 % | **−$15,089** | **0.229** | $1,020 | 8.1 |
| S4n short-gated-by-HTF-tilt | $997 | 58.0 % | −$24,417 | 0.173 | $873 | 12.4 |

Long-only has the better Sharpe and a dramatically better worst week — **but it is a bet on
the 2022–2026 up-drift**, which this sample cannot separate from a structural effect. Gating
shorts by the HTF tilt makes things worse and is rejected.

## Q3 — the portfolio

| portfolio | wk mean | % pos | worst | Sharpe | stress | holdout |
|---|---|---|---|---|---|---|
| S1 + S4n + ASIA | $3,407 | 60.4 % | −$28,222 | **0.282** | $2,647 | 0.772 / 77.8 % |
| **S1+q0.7 + S4n + ASIA** | $3,300 | **61.3 %** | **−$25,405** | 0.280 | $2,617 | **0.867 / 100 %** |
| + short-gated-by-tilt | $2,848 | 61.3 % | −$24,991 | 0.275 | $2,225 | 0.835 / 100 % |

The q0.7-throttled-S1 version ties on dev Sharpe and wins on worst week, positive rate and
holdout. Adopted as the reference portfolio.

## The question this raises, and W17 answers it
Long-only's advantage and the whole stack's calibration rest on **2022–2026 only**. The
substrate holds NQ 1-min back to **2006** — 16 untouched years including 2008. W17 runs the
frozen stack there: not future data, past data we never spent.
