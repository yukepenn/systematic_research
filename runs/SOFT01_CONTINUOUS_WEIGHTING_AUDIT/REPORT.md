# SOFT01 — nonzero continuous weighting: audit closes into U6B, no new construction needed

**Disposition: RESOLVED BY REFERENCE — U6B already IS the valid causal SOFT01 construction.**
Per directive sec32-34, this family's first job was to determine whether U5's invalidation was a
predictor problem or a construction problem, and whether a strictly-causal nonzero-weight POLICY
had ever actually been tested. The Wave-4 frontier audit already answered both questions.

## What the audit already established

`runs/U5_SOFT_WEIGHTING/`: the diagnostic-predictor question is **CLOSED** — `vwap_disp_atr`
(and 3 weaker features) collapsed from a promising-looking residualized correlation (0.212) to
noise (0.003) once isolated to forward-only P&L, a confirmed sunk-profit confound. Stage 2 (the
preregistered tercile-multiplier {0.75x, 1.0x, 1.25x} nonzero-weighting **policy**) was
**explicitly never attempted** — it was skipped per spec.yaml's own STOP rule once Stage 1's
diagnostic failed. So per sec32: this specific feature's policy-mapping question never got a
fair test, but the feature itself (`vwap_disp_atr`) is not a safe state variable to build one on
— it's confounded, not merely unconstructed.

Per directive sec34: "Product A is the natural soft-weight lab... `target_new = target_incumbent
× bounded_multiplier(state)`." **This is exactly what `U6B_PRODUCT_A_SCALE_RATE` already is** —
a continuous, causal, forward-only scale-RATE multiplier on Product A's own scale-in increments,
built on `sigma460`/`htf_agree`/`vote_dispersion` (a causal quality state at the scale-in bar, not
the confounded `vwap_disp_atr`). It is not a binary filter — it modulates the SIZE of an already-
occurring action, precisely the "weak-but-real causal information expressed without binary
participation deletion" sec33 asks for.

## Why this closes without new construction

U6B has already been:
- Built causally, with a bounded multiplier (F0.5/F0.7), never zeroing out participation.
- Full-battery tested: right-tail-safe ($0.00 impact on top-20 winners — the best-behaved
  construction in this campaign), chronologically stable, non-2026-stub, cost-stress checked.
- **Re-adjudicated under O2's owner-utility framework this same wave**: the delta over control is
  positive under BOTH the mixture and Γ-minimax aggregation conventions — new, favorable evidence
  that doesn't depend on resolving which aggregation convention is "correct."
- Its only blocker was ever the arbitrary <1% wash threshold (0.503%/0.579% deltas), exactly the
  class of "arbitrary/wash-threshold failure" directive sec17 flags as a legitimate
  reconsideration candidate — not a confound, not a chronology failure, not a right-tail failure.

Building a second, parallel SOFT01 construction on a different (and, per U5, confounded) feature
would duplicate work that already exists in a stronger form. Per directive sec32's own framing
("if a valid causal nonzero-weight implementation was ever tested... do not duplicate"), the
correct action is to **point SOFT01 at U6B rather than construct anew.**

## Status

`U6B_PRODUCT_A_SCALE_RATE` remains recorded as a **high-priority frozen challenger** (per O2's
governance — not promoted, pending independent adversarial review per sec18's final requirement).
No new SOFT01-specific work is queued. If a future wave finds a genuinely new, non-confounded
causal state variable (distinct from `vwap_disp_atr`), a second soft-weighting construction would
be legitimate — but per this campaign's standing discipline, that requires the new state variable
to justify itself first (Step-0 redundancy + confound checks), not a blind re-run of Stage 2 on
the same feature U5 already found compromised.
