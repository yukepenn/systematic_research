# WE_W10 — EXPOSURE · REPORT

## F1 FIRED — range-proportional sizing is LEVERAGE, not edge

| variant | capture | big-day | wk mean | Sharpe | worst |
|---|---|---|---|---|---|
| S4n.gdl+A0.8 (base) | 4.87 % | 17.58 % | $1,431 | **0.210** | −$24,417 |
| size2 @ratio≥1.2 | 7.17 % | 27.08 % | $2,078 | **0.182** | −$41,420 |
| size2 @ratio≥1.5 | 6.26 % | 22.33 % | $1,890 | 0.195 | −$34,078 |
| size2 @ratio≥2.0 | 5.81 % | 19.92 % | $1,766 | 0.207 | −$26,889 |

Dollars and tail scale together; Sharpe never improves. Same verdict as W06's pyramiding
(H2). **Closed.** (@2.0 is Sharpe-neutral with better stress and holdout — recorded, but
Sharpe-flat = rejected by the preregistered rule, no exceptions.)

## F2 PARTIALLY FIRED — the throttle is engine-dependent, not a universal regime law

| sleeve | best q | small pts (base → thr) | big-day | Sharpe | verdict |
|---|---|---|---|---|---|
| S4.narrow6.gdl | 0.8 | −5,100 → −4,369 | 17.55→17.58 | 0.193→0.210 | QUALIFIES (W09) |
| **S1** | **0.7** | **+153 → +1,106** | 13.82→12.91 | 0.176→0.176 | **QUALIFIES** |
| S5.vf | 0.8 | −4,866 → −4,725 | 15.44→15.03 | 0.186→0.187 | qualifies, marginal |
| S4.all13.gdl | 0.8 | −9,900 → −10,380 | 20.62→20.14 | 0.195→0.184 | **FAILS** |

Each engine needs its own q, and one engine rejects it outright. The generality claim is
narrowed to: *fast-member and D-gated engines benefit; the full-ensemble engine does not.*

## The headline: portfolio capture nearly doubles

| portfolio | capture | **big-day** | small | wk mean | wk pos | worst | Sharpe | stress | hold Sharpe | hold pos |
|---|---|---|---|---|---|---|---|---|---|---|
| **S1 + S4n+A0.8** | **9.57 %** | **31.39 %** | −1.55 % | **$2,830** | 61.3 % | −$27,182 | **0.248** | $2,107 | 0.668 | **100 %** |
| S1+q0.7 + S4n+A0.8 | 9.49 % | 30.49 % | **−1.20 %** | $2,723 | **62.2 %** | **−$26,628** | 0.246 | $2,077 | **0.769** | 88.9 % |

Capture roughly doubles versus either sleeve alone (4.70 / 4.87 %) because the sleeves are
near-orthogonal (weekly corr 0.19), and **big-day capture reaches 31.4 %, above his 24.8 %
overall figure** — not apples-to-apples (his is an all-day average) but the first metric on
which our frozen, net, 4.6-year object exceeds his displayed one.

Both portfolio variants use ≤2 NQ. Still no promotion; arbiter = virgin ≥2026-11-01 read.
