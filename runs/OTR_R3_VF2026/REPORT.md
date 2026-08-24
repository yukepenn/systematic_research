# OTR_R3_VF2026 report (2026-08-24)

Grid: {SIG1,SIG2} × {X_FLIP,X_MED,X_OPP} × {130pt×1, 65pt×2} × {none, 10:15-16:00,
09:15-16:00, 03:00-12:00} on QLEV anchored-cumulative VF4 clone; 17 weekly targets
1/25→5/29/2026 (substrate ends 5/29; later windows unreachable locally).

## Verdicts (preregistered discriminators)
1. **Stop microstructure: 130 pt × qty 1 CONFIRMED; 65 pt × 2 entries REJECTED.**
   The 65×2 emulation can only produce −$1,300 trade ROWS; the targets' largest
   losing TRADE is exactly −$2,600 in every week from 2/1 on — only a single-lot
   130-pt stop makes a −2,600 row. (S65x2 cells scored better on the count metric
   purely because doubling rows compensates the clone's under-trading — artifact,
   rejected on the row-value discriminator.) First −2,600 week = 2/1-2/6 ✓; the 1/25
   week's LL −1,365 predates the cap ✓. Early-Feb short-column −1,300s remain open
   (possible transient 65-pt short-side stop).
2. **Head-window: INCONCLUSIVE.** 09:15-16:00 and 03:00-12:00 variants improve the
   count metric, but trigger-level residuals dominate (weekly net signs wrong in
   ~6/17 weeks; the −42,235 week reproduces sign at 1/3 magnitude; the +17,400 week
   flips sign). Attributing window semantics to [16,0,10,15]/[3,0,12,0] from this
   fit would be overfitting the clone — recorded as OPEN.
3. **Clone boundary reaffirmed**: the remaining residual is the proprietary
   Signal_Trade trigger/exit composition (as preregistered, NOT tunable further
   without the real signal series). The only purchasable oracle remains VWAP Flux
   ($300) — decision stays with the owner; free alternatives exhausted at this
   architecture level.

## Addendum (same day): input-fidelity bound + per-side stop anatomy
- Tick-true PV experiment (s20260511/12, inside the 5/10-22 target window): exact
  per-minute price*volume vs close*vol proxy -> anchored-level paths differ by only
  ~16.5 ticks around the roll constant; trend-state disagreement 1.7% of bars
  (43 vs 39 changes). INPUT FIDELITY IS NOT THE RESIDUAL DRIVER; the proprietary
  trigger is. Reinforces the purchase-gate calculus.
- Per-side largest-loss columns (targets_weekly_2026V): -2,600.00 appears on BOTH
  sides across weeks; 1/30 week has none (cap onset 2/1-6 confirmed); variant-B week
  (6/5) has none (cap belongs to the main VF build); two weeks show SHORT-side
  exactly -1,300.00; the June TP (real execution) shows -3,046.18 = a 130-pt stop
  slipping ~22 pts in live tape (Layer-2 slippage evidence). 2026 weekly L/S counts
  are near-balanced (36/37, 55/56, 31/31...) - the 2026 system retains an SAR-like
  two-sided character.
