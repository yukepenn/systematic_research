# CONTINUOUS SYSTEM EVOLUTION — Wave 1 synthesis + EVI ranking

**Date:** 2026-08-09. Closes wave 1 of the CONTINUOUS SYSTEM EVOLUTION phase (owner directive,
same day) per sec40's required end-of-wave loop: update ledgers, list unresolved empirical facts,
rank new hypotheses by EVI, autonomously select the top one and continue. Wave 1 covered the
directive's own "required first execution order" (sec60) in full: `U0` (shared state
infrastructure), `U2` (data audit), `H0` (Product-A health), `U1` (session heterogeneity), `U3`
(hold/exposure continuation), `U4` (short-side mechanism), `U5` (soft weighting), `U6`
(Product-A path-dependence), `U7` (2026-regime explanation).

## Headline: zero promotions, both baselines unchanged, campaign genuinely advanced

`SolarWaveSMMaster_v4` (Product A) and `SolarWaveOneContractNQ_v5`/`MNQ_v5` (Product B) are
**unchanged**. Per sec55's standing distinction ("CONTINUE RESEARCH ≠ CONTINUE SEARCHING THE SAME
DATA UNTIL SOMETHING PASSES"), that is a legitimate, expected outcome of a rigorous wave, not a
failure — every family found *something real* and every family correctly declined to force a
construction the evidence didn't support. The system's current-regime health (H0, extending
`CURRENT_EDGE_HEALTH.md`) is independently confirmed HEALTHY for Product A too, with one
POSSIBLE_DECAY flag to monitor (10-13-contract band on a still-tiny extension sample).

## Unresolved empirical facts surfaced this wave (sec40 step 3)

1. Product-B entry quality is real-but-moderately ETH>RTH; Product-B/A continuation-while-holding
   value is RTH>ETH, cross-product-corroborated (U1).
2. Overnight-held positions underperform once they transition into RTH, chronologically very
   stable, but right-tail-unsafe as a single-dimension rule (U3).
3. `giveback_ratio` at the first-M-decay checkpoint is the cleanest right-tail-safe state found
   anywhere in this campaign's diagnostic history for Product-B shorts specifically — 0/19 top-20
   giant winners flagged at n=20, degrading only to 10.3% at n=40 (U4).
4. `vwap_disp_atr`'s apparent strength at Product-A scale-ins is a sunk-profit confound, not
   forward information (U5) — a clean methodological catch, and a reminder to apply the same
   forward-only test retroactively wherever a "residual information" claim rests on a
   whole-trade-outcome label rather than a strictly-forward one.
5. Product-A's scale-in value premium is now mechanistically explained (>100% mediated by \|M\|
   conviction magnitude) rather than just observed (U6).
6. The 2026 entry-timing anomaly (R2V1/R2B) is now partially explained (regime-level loss-
   severity rise tracking a volatility uptrend) rather than an unexplained coincidence — but the
   explanation is incomplete (historical analogs only ~30% replicate the effect) (U7).
7. scalping_lab's tick/BBO substrate is a genuine future asset, presently blocked purely by
   coverage depth (~12 months), not by mechanism or provenance (U2).

## EVI ranking of the four "NOT YET TESTED" candidate ideas (sec40 step 4)

Scored on: mechanistic plausibility, novel information content, drawdown relevance, right-tail
safety potential, sample size, chronology testability, implementation feasibility, relevance to
both products (sec48 — cross-product confirmation weighted up).

| Rank | Idea (family) | Mechanism | Right-tail signal | Chronology | Both products? | EVI verdict |
|---|---|---|---|---|---|---|
| **1** | Graded short de-risk on `giveback_ratio` at first-M-decay (U4) | Established (P0/R1's own giveback/decay mechanism, now signal-gated + short-specific) | **Cleanest in campaign history** (0/19 at n=20; 10.3% at n=40) | Spearman -0.50 to -0.65 **every single year** 2022-2026 incl. extension | Product B only (A never clears the checkpoint) | **Highest** — directly answers the owner's own April-2026 concern, real actionable lead time (90-130 bars), narrowest and best-evidenced of the four |
| 2 | Hierarchical ETH-hold delta (U1) | Plausible (liquidity/participation thinner in ETH holding periods) | Not yet tested for the hold-continuation feature itself (only entries were right-tail-checked) | Product-B HOLD alone is weak (3/5 yrs, flat in extension); Product-A SCALE_IN corroborates in sign but wasn't year-by-year tested | **Yes — cross-product corroborated**, sec48 bonus | Second — the cross-product agreement is real evidence, but the base within-product chronology is weaker than U4's and the right-tail gate for a HOLD-layer (not entry-layer) rule is still unverified |
| 3 | Session x quality-signal 2-D hold refinement (U3) | Plausible but unspecified — no concrete second dimension chosen yet | Base 1-D version fails cleanly (9/20 top winners profitable overnight) | Base finding is very stable (5/5 yrs + extension) but that's the REJECTED version | Both, symmetric | Third — genuinely promising direction but requires a full new preregistration from a blank slate, unlike U4/U1 which have a concrete, already-characterized threshold to test |
| 4 | Scale-rate responsiveness to sigma460/htf_agree/vote_dispersion (U6) | Plausible (conviction-quality-conditioned scaling speed) | Base state is right-tail-symmetric (70-75% of BOTH tails start there) — a rate-based (not filter) mechanism sidesteps this, but untested | Stable 4-5/5 years | Product A only | Fourth — smallest effect sizes (ΔR²<0.003, rank-biserial ≤0.17) of the four candidates |

## Decision (sec40 step 5 — autonomous selection)

**Selected: U4's graded short de-risk idea**, opened as a new, narrowly-scoped, preregistered
family — see `runs/U4B_SHORT_DECAY_DERISK/`. This is the single most concretely-specified,
best-evidenced, most owner-relevant candidate produced by wave 1, and per sec42 gets the full
bounded within-family sequence (preregistered construction → small mechanistic grid → chronology
→ tail → cost → early-validation-equivalent → verdict) rather than a parallel multi-family wave —
construction work is correctness-critical (this campaign has caught two look-ahead bugs at
exactly this stage before) and gets tighter, single-threaded scrutiny accordingly, not more
parallel throughput.

U1's cross-product hierarchical idea, U3's two-dimensional refinement, and U6's scale-rate idea
remain **NOT YET TESTED / NOT AUTHORIZED**, recorded here for the next EVI cycle once U4B closes.
