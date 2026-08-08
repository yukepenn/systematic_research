# B1_ABLATION — does the overnight sleeve earn its complexity? (SMV2C, seq 324-327)

_2026-08-08. All portfolios vol-matched to tilt-Solar dev σ (equal-vol basis); BMOM leg
on the new canonical E2 execution. Code `runs/SMV2C_B1_ABLATION/smv2c.py`._

| portfolio (equal vol) | net | Sharpe | Calmar | maxDD | CDaR5 | worst mo | TUW | pos-mo % |
|---|---|---|---|---|---|---|---|---|
| P0 tilt-Solar | $130.5k | 0.77 | 0.77 | −$37.6k | −$25.9k | −$17.0k | 162d | 62% |
| **P1 tilt+BMOM (day-only)** | $193.6k | 1.14 | 1.52 | −$28.2k | −$18.3k | −$12.7k | 133d | 66% |
| P2 tilt+B1 | $145.3k | 0.86 | 0.87 | −$37.0k | −$26.2k | −$14.6k | 163d | 60% |
| P3 tilt+BMOM+B1 (=532) | $207.1k | 1.22 | 1.67 | −$27.5k | −$18.9k | −$8.8k | 138d | 66% |

## Verdict (frozen gate): **B1 DEMOTED from CORE**

P3 beat P1 on 4/5 gate metrics (Sharpe +0.08, Calmar +0.15, maxDD +$0.7k, worst month
+$4.0k) but the block-bootstrap P(P3>P1) = **0.737 < 0.9 required**. Per the
preregistered rule: **B1 → EXPERIMENTAL DIVERSIFIER; the CORE full portfolio = P1
(day-only tilt-Solar + B-MOM)**.

Honest nuances carried with the demotion:
- The one substantive B1 contribution is worst-month smoothing (−$8.8k vs −$12.7k).
  An owner who values that specific tail may still run P3; it is not statistically
  distinguishable from P1 on dev.
- B1 alone adds almost nothing to tilt-Solar (P2 vs P0: +0.09 Sharpe, DD unchanged) —
  consistent with SMV2A's ladder finding (B1 ≈ 0 DD effect).
- This resolves the day-only conflict of interest flagged in Directive V2 §5: the
  practical DAY_ONLY frontier and the FULL_RESEARCH frontier now coincide at P1 unless
  a future overnight engine re-earns the slot with P ≥ 0.9.
