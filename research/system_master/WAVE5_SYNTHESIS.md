# CONTINUOUS SYSTEM EVOLUTION — Wave 5 synthesis

**Date:** 2026-08-10. Covers Master Directive v4's two primary fronts (U6B final adjudication,
AUCTION-information-to-policy translation) plus its supporting infrastructure (EVIDENCE01
traceability audit, O2 numeric-provenance correction, DOM01 forward-collector, capital/forward-
readiness/failure-criteria deliverables). **Zero promotions.** Both baselines
(`SolarWaveSMMaster_v4`, `SolarWaveOneContractNQ_v5`/`_MNQ_v5`) unchanged.

## P1 — U6B: CLOSED, NOT PROMOTED

The full adjudication chain this wave: genuine-MNQ repricing (exposure path proven byte-identical
to legacy pricing by code structure) → capital frontier (dominates control on the shared grid, but
gaps sit inside Monte Carlo noise, and an alternative capital normalization disagrees) → intraday
drawdown/ruin (a single-path fact: at $100k capital the realized worst intraday drawdown alone
already breaches the 25% ruin threshold, for CONTROL as much as for the challengers) → forward-
readiness (the 2022-2025 edge concentrates in 2025 alone; 2026 Jan-May is negative) → **independent
adversarial review: DO_NOT_PROMOTE**. The review's decomposition is the decisive piece: it found
this wave's own O2 pass had overstated its case (the "improvement survives both aggregation
conventions" claim was actually one bootstrap method's boundary noise), that one single day
accounts for 99.6% of one candidate's entire multi-year net edge, and that the "quality" signal is
mechanically confounded with trade size. No coding defect was found — the correctness gates are
real — but the evidence itself does not clear the bar, which is a sufficient, valid basis for
non-promotion on its own. `SolarWaveSMMaster_v4` remains the unchanged incumbent per directive
sec45. The O2 report was corrected in place (additive annotation, not rewritten) to reflect this.

## P2 — AUCTION: information confirmed, this specific policy not promoted

`AUCTION01_VALUE_STATE`'s original diagnostic (distance-from-value predicts subsequent price
expansion) generalized cleanly: `AUCTION02_ACTION_RELEVANCE` found, on the 37-session discovery
set, that this state also changes the *value* of acting on the incumbent's already-chosen
direction — non-redundant with U6B's own quality signal — and froze a conservative, U6B-style
Product-A rate-limiter policy for a proper one-shot protected-pool test.

That test ran on 8 of the 168 protected sessions (owner-authorized small batch, given only 52/168
sessions had the required tick+BBO data cached and even those needed a fresh NT8 export). Results:
the diagnostic itself replicated in sign on 12/12 cells (though only 2/12 cleared statistical
significance — a power artifact of the tiny sample, not evidence the effect vanished); the
strongest single result in the whole bundle was that "far-from-value predicts a large adverse
move" replicated cleanly, with dual-clustered significance, for both Product A and Product B; but
the actual constructed policy — the rate-limiter — showed a small negative P&L delta on both grid
cells (from only 23 bars where it ever fired), triggering its own frozen falsification rule.
**Verdict: AUCTION02's specific rate-limiter policy is NOT_PROMOTED**, explicitly flagged as
low-confidence given the sample size rather than a confident rejection. **The underlying
diagnostic remains real and reusable** — this is a `CONFIRMED_INFORMATION, FAILED_ACTION_MAPPING`
outcome (directive sec42), not a closed information class. 8 of 168 protected sessions are now
consumed for these specific constructions; 160 remain available for a larger future batch.

## Supporting infrastructure

- **EVIDENCE01**: independently recomputed headline numbers for U6B, AUCTION01, and 2 seeded prior
  runs directly from source — CLEAN, no P0 defects from Wave 4's subagent-report-transcription
  pattern.
- **O2 numeric-provenance audit**: found and additively corrected 3 canonical docs (`BASELINE_
  MODELS.md`, `CURRENT_TRUTH.md` ×2, `FINAL_CAMPAIGN_BASELINE.md`) still citing superseded
  hand-arithmetic utility figures.
- **DOM01 forward-collector**: a research-only, structurally-incapable-of-trading NinjaScript
  Indicator built and compile-verified against live NT8, honest about its own limits (MBP not
  MBO, no queue priority). Not yet started — one documented owner action remains.
- **CAPITAL_FRONTIER.md / FORWARD_READINESS.md / FAILURE_CRITERIA.md**: owner-facing synthesis
  documents for both current baselines. Headline: Product A's better-supported minimum operating
  capital is $150k, not the $100k headline, once intraday risk is counted; Product B-NQ needs
  ~$300k for the same reason Product A needs $150k (capital-scale mismatch, not a defect);
  Product B-MNQ is capital-efficient throughout. Product A now has its own percentile-based
  failure-criteria bands for the first time, alongside Product B's pre-existing live version.

## What's next (per directive sec40 — do not stop at the wave boundary)

Two genuinely open threads, both already scoped rather than newly invented:

1. **A larger AUCTION02 confirmation batch.** The diagnostic (far-from-value → worse continuation,
   more large moves) is real and sign-stable across two independent samples now (discovery +
   confirmation); the *policy* failed only on an extremely thin 23-bar sample. 160 of 168 protected
   sessions remain untouched — a second, larger batch (cost permitting, an owner decision on NT8
   time again) would give this a fairer test than 8 sessions could.
2. **DOM01's single remaining owner action** (confirm a Level-II-entitled connection, attach the
   already-built recorder to a chart) would begin accumulating genuine forward Level-II evidence,
   the one information class this campaign still has literally zero historical data for.

Both are legitimate continuations, not new inventions — no new mechanism is being manufactured to
fill a slot. Everything else opened this wave (U6B, the AUCTION02 policy as constructed) closed on
its merits with real, disclosed reasoning, continuing this campaign's now well-established pattern:
aggressive in research, conservative in inference, promotion bar unmoved.
