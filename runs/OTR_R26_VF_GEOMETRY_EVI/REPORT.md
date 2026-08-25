# OTR_R26_VF_GEOMETRY_EVI — report

Spec (with the decision rule) preregistered before the readout. Directive v4.0 §34/§35.
Output: `out/geometry_floor.csv`, log `out/r26_log.txt`.

## The question

A licensed VWAP Flux would tell us the vendor's exact cloud geometry — lifecycle and rail
formula — and exact Signal_Trade timing. That is only worth money if **geometry is what is
limiting the 2026 reconstruction**. This run measures whether it is.

For each of six rival geometries the full R7 144-member structural grid was re-run over the
trader's 17 weekly windows (every numeric constant frozen at his own panel values), and the
**minimum** mean §40 distance recorded. That minimum is an *optimistic* bound on what an
oracle could deliver — optimistic because it is chosen with hindsight against the trader's
own data, which a real oracle cannot do.

## Result

| lifecycle | rail formula | floor (min mean §40 distance) | median member | best member |
|---|---|---|---|---|
| block | percentile_linear | **0.4624** | 0.8049 | T_C\|P_MED\|C_DIR\|H1a\|X_OPP |
| block | nearest_rank | **0.4624** | 0.8368 | T_C\|P_MED\|C_DIR\|H1a\|X_OPP |
| anchor | percentile_linear | 0.4761 | 0.8536 | T_C\|P_MED\|C_DIR\|H1a\|X_OPP |
| anchor | nearest_rank | 0.4761 | 0.7964 | T_C\|P_MED\|C_DIR\|H1a\|X_OPP |
| anchor | minmax | 0.4866 | 0.8322 | T_D\|P_IN\|C_DIR\|H1a\|X_FLIP |
| block | minmax | 0.5190 | 0.8649 | T_A\|P_IN\|C_DIR\|H1a\|X_MED |

Best 0.4624 · worst 0.5190 · **spread 0.0566**.

The incumbent geometry (anchor + percentile_linear) reproduces R7's published 0.4761
exactly, which validates the reimplementation.

## Verdict against the preregistered rule

- **BUY_IS_JUSTIFIED required some geometry below 0.35.** The best is **0.4624** — missed by
  a wide margin (32 % above the threshold). **Not met.**
- **BUY_IS_NOT_JUSTIFIED required a spread ≤ 0.05 with all floors above 0.35.** Spread is
  **0.0566**, exceeding 0.05 by 0.0066. **Not formally met either.**

So the rule returns **intermediate**, and I am reporting it as such rather than forcing a
branch. But the two criteria are not equally informative: the spread criterion missed by
0.0066, while the criterion that actually decides usefulness — *does knowing the geometry
put VF anywhere near a reconstructed model* — failed by 0.11.

**Knowing the vendor's exact geometry is worth at most 0.4761 → 0.4624, a 2.9 % improvement
in reconstruction distance.** For comparison, the Solar family's ordinary standalone weekly
fit is 0.280 (dev) to 0.422 (hp), and its 2023 daily reconstruction is *exact*.

## Two findings that shrink the oracle's value further

**1. Two of the three open vendor questions are behaviourally inert.**
`percentile_linear` and `nearest_rank` give **identical floors** in both lifecycles
(0.4761 / 0.4761 and 0.4624 / 0.4624). At n = 5 with percentiles 95/75/50/25/5 the two
formulas coincide on the inner rails, and the best member uses the median. The
linear-vs-nearest-rank question that the clean-room work treated as open is therefore
**unable to change any behaviour we can observe** — an oracle resolving it buys nothing.

**2. min-max is worse under both lifecycles** (0.4866 and 0.5190), independently confirming
EV-040's geometric rejection *behaviourally* rather than by chart inspection.

**3. The lifecycle reopening was correct, and mildly favours SEGMENT/BLOCK** (0.4624 vs
0.4761). That vindicates the directive's instruction to reopen it. It is **not** grounds to
select BLOCK: 0.0137 is not a discriminator, and §6 forbids choosing a semantic by score.
Both stay alive.

## Companion measurement: the vendor's own chart plates — INCONCLUSIVE

The 23 images embedded in `vwapflux-manual.pdf` were extracted and the rail geometry
measured (`vwap_flux_family/src/vf_plate_extract.py`, `vf_plate_flatness.py`). The intended
test was frozen-vs-moving rails between rotations, benchmarked against our own anchor and
block rails rasterised at the same scale so quantisation acts identically.

**It does not discriminate.** The vendor plate's long-horizontal-run share (cyan 0.201,
magenta 0.125) falls *inside* the range spanned by our own anchor controls (MAX rail 0.449,
MIN rail 0.172), while the block controls are wildly asymmetric (MAX 0.759, MIN 0.008). The
statistic is not robust, and we cannot identify which of the five rails the plotted cyan and
magenta lines actually are. Recorded as a negative result: this free surface was exploited
and did not pay.

A first pass using naive colour thresholds produced 216 spurious "jumps" at 0.3-minute
spacing by tracking onto S/R rectangles and marketing furniture; the corrected hue-ratio +
continuity tracker then clipped genuine jumps at its step limit (every reported jump maxed
at exactly 2.88 pt = the 14 px cap). Both artefacts are documented in the code so the
measurement is not mistaken for a result.
