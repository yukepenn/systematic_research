# DRAWDOWN_FRONTIER — current state of DD engineering

> _Supersede note (2026-08-18): frozen at 2026-08-08. Two later closures not reflected below:
> **C-P7 windfall give-back was KILLED at confirmation** (risk reduction indistinguishable from
> random same-duration de-risking; see wave-2 synthesis) — its "only survivor / frozen spec next
> wave" line is dead. Champion/object references are superseded by `/BASELINE_MODELS.md`
> (Product A `SolarWaveSMMaster_v4`). The lever taxonomy itself remains valid reference._

_2026-08-08. Reference: every number at DUAL-Solar dev vol ($37.1k ann) unless noted._

| lever | status | effect on maxDD |
|---|---|---|
| Graded sizing (vote-proportional) | IN (E10 core) | −$57k vs sign×full (the biggest lever we own) |
| HTF agreement tilt ×1.25 | IN (SM08) | −$2.6k |
| HTF-UP short halving (c1_50) | IN (SMV2E) | −$10.8k on Solar core (w/ 72% crisis retention) |
| Engine diversification (B-MOM 40%) | IN | −$7.6k further (60/40 vs DUAL alone) |
| B1 overnight sleeve | OUT (demoted) | ≈0 |
| Stops (all classes) | CLOSED (V1) | negative — kills right tail |
| Loss-reactive throttles | CLOSED (anti-edge) | negative |
| Vol-transition / trend-day / consensus shapes | CLOSED (V1) | none real |

Current champion equal-vol maxDD: **−$18.1k** (DAYONLY_DUAL6040) vs −$40.2k raw Solar
= 55% reduction, right tail intact. Owner stretch <$15k: remaining candidates are
engine #3 diversification (queue #4), winner-drought conditioning (#5), and component
CDaR attribution (#6). One-contract floor: fractional-portfolio equal-vol DD bounds
any {-1,0,+1} policy; A-dominant challenger reaches −$38-47k native NQ (vs −$58.5k).

## SMV2I C-P3 disclosure (2026-08-08, seq 362) — THE HEADLINE DD NUMBER IS ONE PATH
At CURRENT champion size (L=1.0), bootstrap P(any 2-year window maxDD > $25k):
0.142 (stationary mean-block 20) / 0.430 (moving block 5) / 0.157 (joint-loss 2x oversampled).
All exceed the 10% comfort cap, so the DD-constrained scale factor L* is BELOW 1.0 under every
method. FACT: the −$18.1k (research) / −$16.8k (executable twin) historical maxDD is one
realized path; resampled paths breach $25k with ≥14% probability per 2y window. Consequence:
all leverage add-ons are dead at this risk tolerance, and any future "DD improved" claim must
quote the bootstrap band, not the single-path max. (C-P4 drought tilt: DEAD vs placebo.
C-P1 blend LP: fit optima 0.50-0.55 but eval ordering not preserved -> 60/40 retained.
C-P7 windfall give-back: PRE-TEST PASSED (fwd10 −$136/d vs base +$162/d, p=0.0012) — the only
survivor; bounded trim policy gets a frozen spec next wave.)
