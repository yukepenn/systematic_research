# CONTINUOUS SYSTEM EVOLUTION — Wave 4 synthesis

**Date:** 2026-08-09. Covers Master Directive v3 (P0-P8 of its priority queue) and its same-day
multimodal-microstructure addendum, now complete end to end. 17 research artifacts this wave
(SPEC01, PRICE01, the Wave-4 truth audit, the Frontier+O2+GAMMA00 audit, GAMMA00 itself, DATA02,
DOM01, O2, SOFT01, ADD01, WIN01, ICT0102, MOM01, FLOW01, AUCTION01, VAR01, REL01, COMBO01 — 18
counting both audit passes separately). **Zero promotions.** Both baselines (`SolarWaveSMMaster_v4`,
`SolarWaveOneContractNQ_v5`/`_MNQ_v5`) unchanged. One candidate — `U6B_PRODUCT_A_SCALE_RATE` —
strengthened from "closest call in campaign history" to "frozen challenger with new favorable
evidence under a richer owner-utility measure," still short of promotion pending independent
adversarial review.

## Directive sec88's checklist, answered

- **SPEC01 verdict:** CLOSED, not a defect. The owner-recalled "16 evening trades, ~-$33.5k"
  issue was already investigated and resolved before this baseline was frozen — a mis-specified
  Wave-16 compliance test flagged same-evening entries as overnight margin breaches; the
  corrected test shows 0/1,975 real breaches.
- **O2 owner-utility frontier:** Built and run for the first time on real data (previously
  synthetic-fixture-only). Pre-registered the 4 items a blind review had left open — the most
  important one (is leverage optimized per candidate?) resolved cleanly: no, it's pre-registered
  at the deployed unit size. The dry run itself surfaced that the campaign's own previously-
  quoted hand-arithmetic numbers don't match real module output. New finding: U6B's improvement
  over control is positive under both the mixture and Γ-minimax aggregation conventions.
- **ADD01 verdict:** CLOSED_EXACT_CONSTRUCTION. Lowering Product B's EntryLevel is net
  destructive, not a wash — large-sample, uniform-sign losses, mechanistically explained by
  marginal signals disproportionately eating tail-risk bars with no intrabar stop. EntryLevel=3.0
  is doing real, measurable filtering work.
- **WIN01 verdict:** CLOSED_EXIT_MAPPING. Relaxing exit hysteresis for winner-qualified positions
  fails on both products — Product B uniformly (pure giveback, top-20 winners untouched because
  they already escape via reversal/C4/session-close); Product A's one surface-positive cell is a
  single-year regime artifact caught by the too-good-to-be-true gate.
- **SOFT01 + U5 audit:** resolved by reference — U6B already is the valid causal nonzero-weighting
  construction sec34 asks for; no new construction needed.
- **VAR01 report:** NO_LARGE_EFFECT_DETECTED. A genuinely new, non-redundant multi-scale
  variance-spread signature is real but economically negligible at the horizon it's detectable,
  and a clean null at the horizon that would matter for policy.
- **GAMMA00 literature/data feasibility report:** dealer-gamma mechanism is real but "not large"
  even in rigorous SPX studies; zero NQ-specific rigorous evidence exists; fully data-blocked
  locally (documented, not purchased). Spun off MOM01.
- **MICRO02 status:** superseded/subsumed by the addendum's FLOW01 (decision-checkpoint framing
  folded in directly, rather than run as a separate family).
- **Updated A/B baseline status:** unchanged. `BASELINE_MODELS.md` remains authoritative; Product
  A's Python research substrate now has verified genuine-MNQ dual-truth pricing (PRICE01)
  alongside the existing NQ-proxy convention.
- **Next EVI-ranked family:** see "What's next" below.

## The addendum's multimodal program

- **DATA02:** full inventory. Genuine NQ Last-tick coverage ~12mo continuous; Bid/Ask same window
  but ~40% density (bursty). Level-II depth data confirmed absent everywhere, cannot be recovered.
  Resolved that U9B's 37-session sample was a deliberate governance choice (AMENDMENT_3's
  protected confirmation pool), not a hard data ceiling — respected throughout this wave rather
  than routed around.
- **DOM01:** CLOSED, DATA_LIMITED. No historical L2 data exists; forward-collection scoped but not
  built (entitlement unconfirmed, deserves its own dedicated pass).
- **ICT01+ICT02:** CLOSED_REDUNDANT. Causal PDH/PDL and sweep/MSS constructions both add ~0
  incremental information beyond the incumbent's own M/vol state.
- **FLOW01:** NO_LARGE_EFFECT_DETECTED (HOLD checkpoints, well-powered clean null) /
  DATA_LIMITED (PRE_EXIT, underpowered). Caught and rejected a numerically strong trade-collapsed
  signal as a sunk-P&L confound — the second time this exact discipline has caught a real
  false-positive in a genuinely new information class this campaign (after U5/LEV01).
- **AUCTION01:** USEFUL_STATE_ONLY — **the one new, real, confound-checked finding this wave.**
  Session value-area concentration and distance-from-POC (built from genuine per-trade ticks, not
  a bar-level proxy) predict subsequent absolute price expansion, across all 12 tested cells,
  surviving a time-of-day confound check. Modest effect size, some fading over the sample — not a
  construction yet, flagged as the strongest reusable state to come out of the microstructure
  program.
- **COMBO01:** NO_LARGE_EFFECT_DETECTED. Tested the addendum's own top-priority pairing (AUCTION ×
  FLOW) exactly as preregistered — does FLOW01's null order-flow signal become conditionally
  informative once split by AUCTION01's real value-state? Well-powered HOLD-group test (2,757
  checkpoints/47 trades/31 sessions), 0/8 cells (2 cut variables × 2 horizons, two independent
  statistical formulations, dual session-/trade-block bootstrap) show any signal; ΔR² ≤0.0016
  everywhere. Along the way it found a genuine new caveat AUCTION01's own report hadn't surfaced —
  `poc_share` is heavily entangled with volatility regime (ρ=−0.705 vs sigma460) in this sample,
  while `value_dist_ticks` is much cleaner — now flagged in `STATE_INFORMATION_LIBRARY.csv` for
  any future reuse. Does not close AUCTION01's own main-effect finding.
- **ENGINE-C1/C2:** not reached this wave — gated on COMBO01 showing genuine synergy, and it
  didn't. Given the individual-modality results (mostly null, one modest real effect that doesn't
  combine with anything else tested), the precondition for an independent orthogonal engine isn't
  met on this evidence.

## Governance corrections applied this wave

Per the addendum's core fix (failure of one trading representation ≠ failure of the information
itself), every closure above is scoped, not blanket — see `STATE_INFORMATION_LIBRARY.csv` for the
per-feature ledger and `MULTIMODAL_RESEARCH_MAP.md` for the navigation doc. The
`information_class` discipline (NQ_OHLCV vs NQ_BBO vs NQ_VOLUME_AT_PRICE vs NQ_LEVEL2_DOM, etc.)
is now explicit, preventing ~40 OHLCV-transform constructions from being counted as independent
proofs of exhaustion when they're two convergent sub-campaigns on the same underlying class.

## What's next

The individual-modality microstructure diagnostics are now largely run (FLOW/AUCTION/ICT/VAR/DOM
all reported). The two genuinely open, EVI-worthy threads:

1. **AUCTION01's concentration/distance-from-POC state** — the one real finding this wave — is a
   legitimate candidate for a future construction pass (most naturally a Product-A scale-rate or
   entry-timing modifier, per this campaign's standing preference against binary filters), once
   COMBO01 establishes whether it interacts usefully with anything else first.
2. **U6B_PRODUCT_A_SCALE_RATE** remains the campaign's strongest reconsideration candidate,
   now with O2 evidence in its favor under both aggregation conventions — the next concrete step
   is the independent adversarial review directive sec18 requires before any promotion decision.

Everything else opened this wave (ADD01, WIN01, ICT01/ICT02, MOM01, VAR01, most of FLOW01) closed
negative or null, with good discipline and no forced constructions. This is not a sign the
program is exhausted — DOM01 and REL01 are explicitly deferred (data acquisition, no mechanism
found yet) rather than closed, and GAMMA00's options-data purchase decision remains the owner's
to make. Continuing the EVI loop per standing instruction.
