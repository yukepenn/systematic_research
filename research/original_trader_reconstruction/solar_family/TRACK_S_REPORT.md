# TRACK S — SolarWindRKSelTime reconstruction report (closed 2026-08-23)

**Classification (directive §40): PARTIALLY RECONSTRUCTED, leaning RECONSTRUCTED —
MODERATE CONFIDENCE on wrapper structure.** Search closed at the frozen §49 stop rule:
three meaningfully different mechanism passes (S4 exit-semantics, S5B churn-merge,
S6 T2-conditioning) failed to improve the frontier; S5 (T3-quality) was VACUOUS by
spec-design error (tautological gates) and does not count.

## The candidate: OTR-S-CAND1

`E13_R1 | W_0400_1600 | FF | touch-exit` on frozen Solar 90/179/5/10/true/10, NQ 1-min:
enter on Type-1 flips and Type-3 strengthening when flat; **stop-and-reverse directly on
opposite flips**; exit when Close touches the end-of-bar TrailingStop (inclusive) and at
session close; **entries only 04:00–16:00 ET, force-flat outside**; next-bar-open fills.

| Fingerprint | Target (EARLY_LONG) | OTR-S-CAND1 | Error | Band |
|---|---|---|---|---|
| Trades | ~4,351 | 4,665 | +7.2% | 5–10% ✓ edge |
| Trades/day | ~8.26 | 8.65 | +4.7% | ✓ |
| Win rate | ~40.29% | 39.79% | −0.50pp | ≤2pp ✓ |
| Profit factor | ~1.18 | 1.141 | −0.039 | 0.05–0.10 ✓ |
| Avg hold | ~94m | 74.9m | **−20.3%** | 10–20% ✗ edge |
| Avg trade | ~$67 | $54.4 | −18.8% | 10–20% ✓ edge |
| Max DD | ~−$32,700 | −$32,465 | −0.7% | ✓✓ |
| Net (comm $0) | ~$292,000 | $253,735 | −13.1% | 10–20% ✓ |

Identification is robust at the SHAPE level: every top-frontier cell shares
(reverse-on-flip) + (early-morning entry start 02:00–04:00) + (16:00 cutoff); exact
boundary within that plateau is not identifiable from one aggregate screenshot
(W_0300_1600 D=1.343, W_0400_1600 D=1.153/1.295 across shapes).

## What the wrapper is NOT (falsified, HYPOTHESIS_LEDGER OTR-S1..S6, 100 cells)

- NOT V0's exit-and-wait (2,915 trades — the S0 baseline explains the old campaign's
  count gap); NOT any flat-entry policy without reversal (counts cap ≈4,143 with holds 134m).
- NOT T2-pullback-driven: every T2-including cell drops WR to 33.5–35.6% (target 40.3);
  strong-only-T2 (vendor "reliable pullback" story) drops WR to 36–37.4% — **pullback
  entries are the wrong mechanism for this trader's fingerprint.**
- NOT RTH-only / lunch-skip / skip-open SelTime (in-market arithmetic: RTH caps 390
  min/day vs the 759 min/day the fingerprint requires — the trader DID trade overnight
  hours after ~02:00–04:00 ET).
- NOT strict-cross exits, NOT re-entry cooldowns, NOT one-entry-per-leg caps.

## Certified along the way (S0, Class B now)

Pure-Python NT8-convention loop reproduces the frozen canonical Type-1 NT8 run
trade-for-trade (2,914/2,915 exact; the 1 diff is the documented data-boundary bar).
Load-bearing discovery: **V0's exit is an INCLUSIVE touch of the end-of-bar TrailingStop —
a touch exits WITHOUT flipping the trend** (strict-cross is the flip); touch-exits are why
consecutive same-direction trades appear and why direction chains persist.

## Cross-window (S8, frozen candidate, no retuning)

- Late-2025 (Family-S era per the 90/179/5/10/10 screenshot): counts/holds the right
  order (sim 36/68/19/36 vs tgt 27/60/9/31; sign agreement 3/4). Consistent with the
  trader still running an S-variant, possibly with the SD LossLimit wrapper.
- 2026 windows: STRONGLY inconsistent (sim 141–256 trades/wk at 24–27m holds vs tgt
  76–183 at 33–50m; sign agreement poor). **2026 headline weeks are NOT Family S** —
  supports the V/B-family hypothesis (final-package Q13).

## Layer-2 economics (arithmetic on the frozen candidate, 2023-01→2025-01, 25 months)

| Cost assumption | Net | ~Annualized |
|---|---|---|
| Screenshot (comm $0, slip 0) | $253,735 | ~$122k/yr |
| Trader's ~$2/RT | $244,405 | ~$117k/yr |
| Lifetime $4.36/RT | $233,396 | ~$112k/yr |
| $4.36/RT + 1 tick/side | $186,746 | ~$90k/yr |
| $4.36/RT + 2 ticks/side | $140,096 | ~$67k/yr |

Behavior remains solidly profitable in this historical window under honest costs; the
author's ~0.9×profit adjustment (AS-6) is the same order as the $2RT+1t/side haircut.
(Consistency check only — per COST_MODEL.md the identification used Layer-1.)

## Residual and its honest interpretation (Class C)

The −20% hold / −13% net residual pattern is consistent with: (a) the SolarWind engine
(his) differing from SolarWave (ours) in re-entry event emission — the name difference is
real, observed evidence, and the engine identity is UNVERIFIABLE without a vendor
artifact; (b) a SelTime structure outside our bounded family; (c) his report window
having ~527 sessions vs our 539. None is testable with current evidence (directive §49:
remaining uncertainty is bounded; further search has low expected information value).

## What our old Type-1 replica missed (final-package Q3, answered)

(1) Reversal-on-flip instead of exit-and-wait (+~1,500 trades); (2) Type-3 re-entries
after touch-exits (+~500); (3) the SelTime window (−overnight-early-morning trades,
−in-market time); (4) the touch-exit semantic itself. WR/PF were always right because
they are properties of the underlying Solar flip engine, not the wrapper.
