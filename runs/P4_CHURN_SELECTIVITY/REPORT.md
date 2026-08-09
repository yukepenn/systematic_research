# P4_CHURN_SELECTIVITY -- RESULTS

Frozen spec (`spec.yaml`) implemented exactly. Churn-state window/threshold (W=20 bars,
threshold=p75=3 same-session flips) came from the flip-count histogram alone
(`out/churn_diagnostic.json`), fixed before any P&L was computed. Code: `src/run.py`.

## Distinctness, confirmed empirically (not just architecturally)

`corr(HIGH_CHURN, 1-ER150) = 0.070` -- the same-session flip-count churn state is **not** a
relabeling of S1's already-closed ER150 score; the two measures are nearly uncorrelated.
HIGH_CHURN is true on 29.4% of bars.

## Grid result: another isolated ridge point, not a plateau

| REQUIRED_FRAC | n suppressed | net | Sharpe | ΔSharpe | gate_A | yearly agree | gate_B |
|---:|---:|---:|---:|---:|---|---:|---|
| 0.20 | 19,203 | $115,227.60 | 0.689 | −0.020 | FAIL | 2/5 | FAIL |
| **0.30** | 26,704 | $127,219.30 | 0.760 | **+0.051** | **PASS** | 2/5 | FAIL |
| 0.40 | 36,898 | $108,692.10 | 0.653 | −0.056 | FAIL | 2/5 | FAIL |

Non-monotonic in the free parameter (0.2 and 0.4 both hurt, only the middle cell helps) --
exactly M3's failure signature. Only 1 of 3 cells passes gate_A, so `gate_C_plateau` (needs
≥2 of 3) fails outright, and even the one passing cell fails gate_B (2/5 years agree in sign,
need ≥4/5) -- the benefit is not chronologically robust even taken alone.

## Gate D disclosure (widest cell, REQUIRED_FRAC=0.40, symmetric outcome check)

36,898 commitments suppressed; mean bar-level P&L on the suppressed bar itself: **−$3.55**,
positive share 45.2%. Suppressing was *slightly* right more often than not by dollars, but
essentially a coin flip by count -- consistent with "requiring more agreement" not being a
strong genuine information signal here, just noise that happens to net negative on average
after commission.

## Disposition: CONFIRMED-NOT-BENEFICIAL

The conditional, churn-state-gated stronger-agreement construction is architecturally distinct
from both `arm_ER` (continuous reweight, closed) and `M3` (unconditional member-level threshold,
closed) -- confirmed both by design and by the near-zero empirical correlation with ER150 -- but
it fails on its own terms: no plateau, no chronological robustness, and the one nominally-passing
cell is a single ridge point in a non-monotonic grid. Priority 4 is closed. No red team required
(clean negative, no promotion proposed, same standard applied to M3/M4).
