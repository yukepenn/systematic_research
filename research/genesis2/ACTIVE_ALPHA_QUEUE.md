# ACTIVE ALPHA QUEUE

**State document.** Replenishment rule (README): < 10 DISCOVERED or < 3 MED/HIGH → auto-launch a
new scan wave. Statuses: DISCOVERED → TRIAGED → PREREGISTERED → TESTING → CLOSED / SURVIVED →
FORWARD-QUEUED.

## Health (2026-08-29, post-Wave-1)

**Queue is FULL.** 33 live cards (37 − 4 killed): 4 HIGH (all → PREREGISTERED/TESTING),
13 MED (TRIAGED, next-wave candidates), 12 LOW (TRIAGED, parked), 1 FORWARD-QUEUED, 2 METHODS,
1 DATA-GATED. **No replenishment trigger active.**

## In formal testing (Wave 1 — specs `runs/G2_F1_*`)

MC-01 ORB · MC-20/22(RV) conditioners · MC-23 TICK fade · MC-36 stop geometry.

## Next-wave bench (MED, in EVI order per skeptic)

MC-36→done, then: MC-14 pullback-entry policy A/B · MC-35 overlay meta-label/sizing · MC-04 IB
conditioning · MC-07 reference-level magnetism · MC-13 late-day hedging momentum · MC-08
sweep-reclaim (mirror-control design) · remaining MED per verdicts file.

## Conversion funnel (§70 — cumulative, updated per wave)

| stage | count |
|---|---:|
| raw leads discovered | ~230 |
| deduped mechanism cards | 37 |
| survived skeptic (MED+) | 18 (+1 forward, +2 methods, +1 data-gated) |
| formally preregistered | 4 runs (5 mechanisms) |
| information survivors | — pending Wave-1 results |
| after-cost survivors | — |
| portfolio survivors | — |
| forward-queued | 1 (LIQREV01) + shadow roster |

**Current measured bottleneck:** cannot be declared yet — first formal wave pending. The
*discovery* stage is demonstrably not the bottleneck (230 leads in one wave).
