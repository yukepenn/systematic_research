# G2_F7_AUCTREV_CERT — RESULT: **S1 PASS · S2 FAIL (R_a, R_c) · S3 ABORTED — AUCTREV closed at formulation**

Spec committed `ac8e309` pre-result. Trials G00034/35/36. Program-printed evidence in `out/`.

## S1 — the object is real code-wise (G00034 PASS)

Clean-room reimplementation from the spec alone (forbidden-path audit: 0 hits): event agreement
**99.813%**, per-event net corr **1.000000**, total net within **0.34%**. All 4 disagreements
traced to ONE spec-text ambiguity (time-of-day vs chronological reading of the 09:30 seed on 3
bar-sparse sessions), classified with a dual-rule verifier that reproduced both pipelines to
0.000000. **No MS-BBO-class defect exists in AUCTREV.**

## S2 — and the economics are not what the mechanism claimed (G00035 FAIL)

- **R_a FAIL, decisively**: the top 54 events (10%) carry **203.2% of total net — the remaining
  480 events sum to −5,605 pts.** This is a tail-carried payoff concentrated in a handful of
  crash-rebound episodes, not a broad reversion edge.
- **R_c FAIL — the mechanism claim is falsified**: entering one session LATE degrades the edge
  only **15.4%** (gate ≥50%). The payoff is not the fast overnight reversion of the dislocation;
  it persists a full session, i.e. it is mostly the multi-day rebound of extreme-down days —
  DELEV02-adjacent territory, not the 15:50-auction mechanism.
- R_b passed (LOYO-modern all positive); R_d monotone; R_e $45 holds — none of which rescues a
  falsified mechanism with a tail-carried distribution.

## Disposition

**AUCTREV stops at SURVIVED-DISCOVERY + INDEPENDENT-IMPLEMENTATION-VERIFIED and is CLOSED at
this formulation** — not robustness-supported, not portfolio-tested (S3 correctly ABORTED; the
book-stream plan is on record, no economics quoted). A "crisis-rebound tail" reframing would be
a NEW card that must carry these facts and the DELEV02 null; nothing is licensed by this run.

⭐ **What this wave proves about the machine**: the economics gates (Wave 6) passed and the
certification stage still killed the object on concentration + mechanism-timing — exactly the
false-candidate class that would otherwise have reached the owner. The G00030 information fact
(15:50 break) remains banked and true; its monetization at this geometry is dead.

Multiplicity: 1-of-13 formal objects, ~750 prior experiments. **`LIVE ENABLED = NO` · $0.**
