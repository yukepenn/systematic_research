# OWNER_REPORT_RECONCILIATION — owner-supplied VF deep-RE report vs our evidence state
2026-08-24. Directive v3.0 §0: the owner report is an EXTERNAL RESEARCH NOTE,
not automatic truth. Claim-by-claim reconciliation against our ledgers.

## Where the report and our work agree (and who has stronger evidence)

| Report claim | Report confidence | Our status | Our evidence |
|---|---|---|---|
| Rolling anchored-VWAP population, oldest dropped | very high | CONFIRMED | VF1-4 image-fidelity + vf_core morphology |
| Lifecycle = ACTIVE anchors (all keep updating), not frozen blocks | ~90-95% (self-corrected from 60/40 blocks) | CONFIRMED-incumbent + falsifier defined | width 47 vs 106 pts, movers 5.0 vs 1.34/bar, boundary jumps 11 vs 21; frozen-rail staircase never observed; sole public precedent (LuxAlgo, license recorded) |
| Rails = percentile linear interpolation | high, "not proven" | **RESOLVED at vendor level without purchase** | EV-040: FVP hugs price-side cloud edge in trends on the manual's own charts → min-max (FVP≡midspan) CONTRADICTED; linear-vs-nearest-rank still open (outer rails only) |
| FVP = Q50 median | ~95% | RESOLVED (vendor level) | EV-040 same geometry |
| Adversarial pop [100,101,102,103,140] separates formulas | proposed test | IMPLEMENTED as unit test | vf_core _tests(): Q75 pl=103.0 / nr=103 / minmax=130.0 |
| Signal_Trend ±2/±1, CVD = strength qualifier not direction | official | CONFIRMED + version-pinned | manual (2026-02-02) = ±1 only; changelog verbatim: 2/9 Signal_Cum_Delta, 2/24 upgrade → 2-state→4-state bracketed |
| Split = min bars between signals | likely | PINNED stronger | manual §2.13: consecutive SAME-DIRECTION signals |
| QtyPerTrend = max signals per trend | likely | PINNED + reset members tested (inseparable) | manual §2.11; R7 |
| CloseThreshold = CLV family, exact formula unknown | plausible | family PINNED (manual §2.12); THREE readings tested on the trader's windows | R7/R7b: H1a (extreme-toward) empirically dominates, H1b dead, H1c (manual-verbatim) mid-pack — ambiguity remains, but bounded and scored |
| Static zones = separate module, 3-bar pivot-ish | high-level | CONFIRMED in product; **ABSENT from the trader's panels** | manual §2.14 + IMG re-pass: no Zone row in any of ≥9 frames → trader doesn't expose/use zones |
| HelloWin two-stage wrapper (hit bar + window + fixed stop/target); vendor R:R engineered by exits | audit | CONFIRMED at ecosystem level | pub-recon (hellowin.io); same engineered-R:R observation |
| Anchor-age concordance / skew = better features hidden by sorting | suggestion | IMPLEMENTED as diagnostics only | vf_core with_meta + age_concordance (mean −0.17 on real data); §18/§42: excluded from ORIGINAL reconstruction |
| Anchor-phase sensitivity, ablations vs ribbon/session-VWAP | proposed | REGISTERED, deferred per §43 (after mechanism clone; never merged into replica) | directive discipline |

## What we closed that the report leaves open
1. Lifecycle (report's "largest unresolved part") — closed to incumbent+falsifier.
2. Percentile-vs-minmax (report: "clean black-box test can settle in minutes,
   needs purchase") — settled geometrically from the manual charts, no purchase.
3. Report's black-box Tests 1-8 → our PURCHASE_GATE oracle protocol implements
   their equivalents, ready to run post-install (UpDownTick mode; EV-039 caveat).

## The trader-side layer the report does not contain (our unique evidence)
- The trader's ACTUAL params differ from every public preset: 60/5/95-75-50-25-5/
  QtyPerTrend 3/**CloseThreshold 10**/Split 5, Trend 20 EMA — his CT=10 vs the
  presets' universal 70 is a deliberate customization either way it is read.
- EV-039: BidAskPrice_RealVolume + Tick Replay OFF computes NOTHING historically,
  yet his SA backtests are full → his stack is most plausibly his OWN bar-data
  implementation (H3/H4), not the embedded licensed indicator.
- 130-pt wrapper-level stop (pre-dates the first VF frame), −2,600 signatures.
- OTR-VF-CAND1: 208-member bounded signal identification against his 17
  in-sample + 3 true-OOS windows (§40 distance, failure-week DQ, LOWO) —
  the report contains no trader-window fitting at all.

## Two nuances where our evidence corrects the report
1. "Close threshold 80%" (report's settings table): our pub-recon found ALL
   manual presets use CloseThreshold 70; "80" appears publicly only as a
   Level:Max value in 1-min/Renko presets — likely the same misread we
   corrected in TRACK_VF earlier.
2. "Trend Period 14": that is the public example's value; the TRADER's panel
   is 20/EMA (different objects, not a conflict — noted to avoid blending).

## Verdict
The report is architecture-convergent with our clean-room state (same incumbent,
same open items) and adds no new unresolved-hypothesis surface. Its remaining
opens (exact trigger composition, exact CT reading, zone internals) are exactly
our remaining opens; the first two are on the oracle path, the third is moot
for the trader (no zone exposure).
