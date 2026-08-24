# VF_CORE_PARITY_REPORT — V1/V2 lifecycle + formula falsification tests
2026-08-24. Code: src/vf_core.py (unit tests PASS, incl. the §16 adversarial
population [100,101,102,103,140]: Q75 percentile-linear=103.0, nearest-rank=103,
min-max=130.0 — sharp separation). Real-data window 2026-03-16..27 (NQ 1m,
close×volume, P=60, A=5, trader pcts 95/75/50/25/5). No PnL used anywhere.

## Lifecycle: VF-ANCHOR vs VF-BLOCK (observable morphology)

| metric | ANCHOR | BLOCK |
|---|---|---|
| mean rail movement per in-period bar (pts) | 0.47 | 0.19 |
| rails moving per in-period bar | 5.00 (all) | 1.34 (current layer only) |
| mean jump at period boundary (pts) | 11.1 | 21.2 |
| mean cloud width Max−Min (pts) | **47.0** | **106.0** |

BLOCK clouds are ~2.3× wider (frozen layers lag price) and step-jump at hour
boundaries; ANCHOR clouds drift smoothly with all rails alive. The VF1-4
image-fidelity selection already picked anchored-cumulative geometry against
the trader's chart frames; these stats quantify why. **VF-ANCHOR remains the
incumbent; VF-BLOCK stays as the falsification control** (a single clean chart
frame with a frozen-rail staircase would flip this — none observed).

## Rail formula: percentile-linear vs min-max (real populations, A=5)

Inner rails differ materially on real data: Median mean |Δ| = 10.3 pts
(p95 32.4), Upper/Lower ≈ 8-9 pts; outer rails ≈ 1.7 pts. Decisive observable:
**min-max forces FairValue ≡ midspan of the cloud (Δ=0.000 by construction);
percentile FVP deviates from midspan by mean 8.9 pts** on skewed populations.
→ Image test: measure FVP position between Min/Max on trader chart frames; a
consistently off-center FVP proves percentile-family, centered proves min-max.
Manual wording ("threshold within the VWAP bands", EV-038) mildly favors
min-max; geometry test outranks wording. Status: OPEN, discriminator defined.

## Price input (V-phase §15)
close vs hlc3 changes rails by mean 0.75 pt (p95 2.4) — second-order; both
kept, decided later by chart-geometry or oracle. Tick-true PV already bounded
(R3 addendum: 1.7% trend-state disagreement).

## §18 anchor-age diagnostics (metadata only, never in the replica)
Age-order concordance mean −0.17 → the sorted cloud is NOT age-ordered; layer
identity carries information the rails discard. Stored via vf_levels(...,
with_meta=True); excluded from ORIGINAL reconstruction per directive.

## EV-039 consequence (from the vendor manual, recorded in EVIDENCE_LEDGER)
BidAskPrice_RealVolume + Tick Replay OFF ⇒ the licensed indicator computes
NOTHING on historical data, yet the trader's SA backtests are full of trades in
exactly that displayed configuration → his 2026 stack is most plausibly his OWN
bar-data implementation with vendor-style parameter names (H4/H3 > H1). Our
bar-level clone is therefore the SAME input class as his build, not an
approximation of it. Purchase-gate oracle protocol must use Tick Replay or
UpDownTick modes for the licensed product to compute historically at all.
