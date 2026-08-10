# EXP01 — Product-A marginal exposure value shape: CLOSE, no stable shape found

**Disposition: DIAGNOSTIC COMPLETE — no candidate.** After controlling for |M| conviction (the
confound U6 already identified as mediating PA0's raw exposure-band pattern), no clean, stable
linear/concave/convex shape emerges. This is a reassuring result for the incumbent: no evidence
that Product A's current linear KSOLAR/KBMOM exposure mapping is meaningfully mis-calibrated.

## Setup

400,202 usable nonzero-exposure bars (canonical window, levels 1-11 — consistent with PA0's own
finding that |M|≈11 is the practical maximum, the ±13 clamp never binds). Outcome: forward-20-bar
P&L per contract at each bar, matching PA0/U6/U8's own established convention.

## Raw per-level value (PA0-style, for continuity) — reproduces the known pattern

Level 1 mean=−$0.11 through level 11 mean=+$33.73 — broadly increasing with level, consistent
with PA0's own already-published exposure-band monotonicity finding. Not new information on its
own (this is the pattern U6 already explained as >100% mediated by conviction).

## Residualized per-level value (after removing |M|-tercile bucket mean) — the new test

| level | resid mean | n |
|---|---:|---:|
| 1 | +0.14 | 202,200 |
| 2 | +2.81 | 35,963 |
| 3 | +0.72 | 27,692 |
| 4 | −1.89 | 71,559 |
| 5 | +0.49 | 16,302 |
| 6 | −4.45 | 9,101 |
| 7 | −3.34 | 21,620 |
| 8 | +3.19 | 5,461 |
| 9 | +2.62 | 7,037 |
| 10 | −1.82 | 1,114 |
| 11 | **+26.32** | 2,153 |

Once |M| is controlled for, levels 1-10 show no clean monotonic pattern — small, noisy, sign-
alternating residuals. Level 11 stands out sharply (+26.32, vs the next-highest of +3.19) — this
is the maximum practically-achievable exposure level (a boundary effect at the edge of the
range, n=2,153, the second-smallest count of any level) and is doing most of the work in any
apparent "convexity" below.

## Curvature test (interpretable OLS: resid_value ~ level + level²)

| term | coef | se | t |
|---|---:|---:|---:|
| intercept | 2.5704 | 0.6835 | 3.76 |
| level (linear) | −2.0612 | 0.4342 | −4.75 |
| **level² (curvature)** | **+0.2450** | 0.0498 | **4.92** |

R²=0.00006 (n=400,202) — statistically significant curvature term (large n makes even tiny
effects detectable) but essentially zero explanatory power in absolute terms — the same
statistical-vs-economic-significance gap this campaign has repeatedly encountered (LEV01/LEV02/
SKEW01).

## Year-by-year stability — NOT stable

| year | n | curvature coef | t |
|---|---:|---:|---:|
| 2022 | 93,792 | +0.400 | 4.10 |
| 2023 | 88,726 | +0.152 | 2.54 |
| 2024 | 87,629 | −0.120 | −1.27 |
| 2025 | 89,723 | +0.649 | 4.76 |
| 2026 | 40,332 | −0.046 | −0.20 |

Only 3/5 years show a (individually significant) positive curvature; 2024 and 2026 flip sign
(neither reaching significance on its own). This is not a chronologically robust pattern.

## Right-tail check

Top-20 all-time Product-A blocks: mean exposure level 6.35 (max 11). Bottom-20: mean 3.98 (max
11). Population: mean 2.68. Consistent with the already-known, already-explained (via
|M|-mediation) pattern that better blocks reach higher exposure — not new tail-safety
information specific to curvature shape.

## Verdict

**CLOSE — no clear or stable shape.** The pooled regression shows a statistically significant
but economically negligible (R²≈0.00006) convex curvature term, driven substantially by a
boundary effect at the maximum exposure level (11 contracts, the smallest-but-one sample) rather
than a smooth pattern across the practical range. The signal does not survive year-by-year
scrutiny (2/5 years flip sign). **This is a reassuring negative result for the incumbent**:
directive sec28's own preference ("favor simple mappings... a candidate should reduce policy
complexity, not create 13 mini-strategies") is satisfied by the status quo — there is no
evidence here that Product A's linear KSOLAR/KBMOM exposure-to-target mapping should be replaced
with a non-linear one. No candidate constructed. Product A remains unchanged.
