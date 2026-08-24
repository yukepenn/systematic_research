# SIGNAL_TREND_IDENTIFICATION — status after R7/R7b (2026-08-24)

## Version facts (official changelog, pub-recon 2026-08-24, verbatim-sourced)
- 2026-01-09/10 release; 01-14 params rearranged; 01-17 anchor cap removed;
- **2026-02-09 Signal_Cum_Delta ADDED**; **2026-02-24 Signal_Trend UPGRADED** —
  product page now documents Signal_Trend ∈ {+2 strong up, +1 weak up, −1 weak
  down, −2 strong down}; the 2026-02-02 manual documents ±1 only → the upgrade
  was 2-state→4-state (endpoints documented, mechanism inferred).
- Trader alignment (HYPOTHESIS): first VF panel 2/13 = 4 days after the 2/9
  build; late-Feb behavior shifts align with 2/24 (a wrapper testing
  Signal_Trend==1 would silently break on the 4-state upgrade); the 2/20
  checkbox banks have NO vendor event → trader-side UI change.

## Identified structure (bounded family, R7/R7b, no free constants)
Rank-stable leading trend member (13/17 LOWO rotations):
**T_C — direction = close vs FairValue(Q50) with EMA20(close) slope agreement
(state held when they disagree).** T_A (close beyond Max/Min rails) and T_D
(EMA20-vs-FV cross) sit in the same inseparable cluster (Δmean ≤ 0.04).
Strength (4-state) via bar-level CVD-slope agreement changes little
(strong_only gate: 0.476→0.492) — the strength dimension is NOT identifiable
from weekly aggregates on 1-min bars.

## Reconstruction bound
Tick-input fidelity bound stands (R3: 1.7% trend-state disagreement). The
trend LAYER is effectively solved-to-cluster; remaining ambiguity does not
drive the weekly-distance plateau (structurally diverse trend members all
plateau at 0.48-0.52 — the residual lives in the TRADE trigger, not the trend).
