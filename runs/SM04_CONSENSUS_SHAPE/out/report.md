# SM04 — Consensus Target-Map Shapes: NO PROMOTION (direction real, sub-significant)

_2026-08-08. Spec frozen before read (seq 297-300). Results: `out/results.csv`.
All figures matched-average-exposure vs BASE round(10·mean) map._

| arm | Δnet | ΔSharpe | ΔlogG | ΔmaxDD | top-10-day ret | H1/H2 | P(dSharpe≤0) | P(dmean≤0) |
|---|---|---|---|---|---|---|---|---|
| U1_boost (+2 at \|vote\|≥11) | **+$14.9k (+12.5%)** | +0.045 | +0.066 | −0.4% | **1.116** | +/+ | 0.137 | **0.029** |
| U2_tilt | −$0.1k | −0.047 | −0.000 | −4.8% | 1.051 | −/+ | 0.838 | 0.509 |
| U3_convex | +$42.1k | +0.047 | +0.176 | **−20.7% (worse)** | 1.381 | +/+ | 0.316 | 0.048 |
| D1_deadband | +$21.0k | +0.001 | +0.092 | −6.4% | 1.184 | +/+ | 0.499 | 0.119 |

## Verdict (frozen gates): FAIL — no map clears P(dSharpe≤0) < 0.10

- FACT: the up-weight-consensus family (U1, U3) improves every point estimate and is
  the first conditioning axis found that is RIGHT-TAIL-ALIGNED (retention > 1.0 —
  it amplifies the best days rather than cutting them), consistent with the T0-6
  uniqueness-inversion prediction.
- FACT: significance fails on dSharpe (0.137 best); U1's mean improvement is
  significant (P=0.029) but volatility rises in proportion.
- FACT: U3 is a concentration bet (maxDD +20.7% worse, worst-month −$23.4k) — the
  convex end of the family trades tail-upside for drawdown; not acceptable.
- INFERENCE: the linear E10 map is close to optimal for its risk; the residual
  up-weight signal at full alignment is real but too small to certify at dev length.
- Registry: seq 297-300 FAIL. The axis may return ONLY inside a future portfolio-
  level target-map spec with genuinely new structure (not a re-tune of these maps).
