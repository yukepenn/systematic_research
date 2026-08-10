# U6B — Independent Adversarial Review (Master Directive v4 sec9)

**Reviewer had no prior involvement in building U6B.** Instructed not to confirm the candidate is
good, but to actively try to find reasons it should not be trusted, then report honestly whether
that attempt succeeded or failed. Given the frozen spec, control/challenger series, raw metrics,
testing history (original construction, genuine-MNQ repricing, O2 owner-utility readjudication,
capital-frontier/intraday-DD risk panel, forward-readiness panel), and known risks, with an
explicit instruction to re-derive numbers independently rather than trust report prose.

## Verdict: DO_NOT_PROMOTE

No coding bug was found — the correctness gates are real (independently reproduced from a fresh,
from-scratch re-execution of the construction script, bit-for-bit), and the "byte-identical
exposure path between legacy and genuine-MNQ pricing" claim is provably true by code structure
(the decision layer is architecturally unable to read the price arguments), not merely an
empirical coincidence. **The evidence itself does not clear the bar for promotion — which the
reviewer's own instructions treat as a sufficient, valid basis for DO_NOT_PROMOTE independent of
finding a defect.**

## Failures found (in order of materiality)

1. **O2's "improvement survives both aggregation conventions" claim does not survive
   decomposition.** The reviewer reimplemented `primary_objective_v2`'s bootstrap machinery
   directly and split the pooled/Γ-minimax delta by method (paired, same seed):

   | method | ΔJ (F0.5 − CONTROL) |
   |---|---:|
   | moving5 | **+0.01490** |
   | moving20 | −0.00153 |
   | stationary60 | −0.00373 |

   The positive Γ-minimax reading `runs/O2_OWNER_UTILITY_READJUDICATION/` reported is **entirely**
   the moving5 figure — under the other two resampling conventions the candidate is *worse* than
   control. Digging further: moving5's ruin-probability improvement traces to just 18 net path
   flips out of 2,000 bootstrap paths (0.9%), and **every flipped path lands within ~1.5
   percentage points of the exact 25%-of-capital ruin threshold**. This is boundary-threshold
   noise on a handful of resampled paths, not a systematic risk-reducing mechanism. This is a
   genuine correction to how this campaign's own O2 pass characterized the finding — "positive
   under both conventions" was too strong; it should have read "positive under one of three
   methods, driven by threshold-boundary noise."

2. **The dollar evidence is dominated by single days.** For F0.5, one single day (2022-09-21, an
   FOMC day) contributes $300.10 of the entire $301.30 full-history canonical net delta — **99.6%
   of a 4.5-year, 1,139-session case**. In the actual 2022-2025-only wash-test slice that produced
   the original NOT PROMOTED verdict, the top 3 days account for 99.5% of the $859.20 total delta.
   This sharpens (with an exact number) what the forward-readiness panel's LOYO section already
   found qualitatively (dropping 2025 flips the sign): the effect isn't just concentrated in one
   year, it's concentrated in single days — remove the single best day and essentially the entire
   multi-year case for F0.5 evaporates.

3. **The "quality" signal is confounded with trade size, not independent of it.**
   `vote_dispersion_aligned` has 0.68 correlation with the incumbent's own `|target_exposure_A|`
   on the canonical scale-up population (n=11,620); mean target size is 4.03 contracts on
   quality-high bars vs. 2.19 on quality-low bars. This mechanically explains — not just
   documents — why 85.6%/88.3% of quality-low scale-ups hit the mandatory 1-contract anti-block
   floor: quality-low bars are, by construction of the underlying signal, disproportionately
   small-target moves. The rate limiter is structurally near-inert almost exactly where it's
   supposed to bind.

4. **Path-state contamination is real and was undisclosed quantitatively.** Fresh re-execution
   shows CONTROL has 12,085 scale-up bars vs. F0.5's 12,603 (+4.3%) and F0.7's 12,485 (+3.3%) — the
   rate limiter mechanically creates additional decision points (by changing `p` going into future
   bars) that would not exist as separate events under the control path, each independently
   re-rolling the quality gate. The original spec alludes to this qualitatively but never
   quantifies it.

5. **VOTE_THRESH is a whole-sample statistic applied retroactively, not point-in-time-causal.**
   `VOTE_THRESH=6.0` is the top-tercile cutoff computed over the *entire* 2022–2026 population with
   no time restriction, then applied to gate decisions starting January 2022. Non-circular in the
   narrow sense the spec claims (never touches F0.5/F0.7's own P&L), but a real, previously-
   undisclosed whole-sample look-ahead property in the causal-deployment sense: a real 2022
   operator could not have known the 2022–2026 tercile cutoff.

## Unsolved risks (genuinely open, not forced into a verdict)

- Pre-registration timing (whether F0.5/F0.7 were truly chosen before results were seen) is not
  independently auditable — spec, source, and results all landed in a single git commit.
- The risk panel's capital-normalization disagreement (F0.5 dominates control, F0.7 doesn't, under
  an alternative equal-DD-fraction convention) is very likely a similar extreme-value noise
  artifact to finding #1, but this wasn't independently confirmed with its own bootstrap.
- Whether O2's own $100k headline capital is a sound level to compare candidates at all, given the
  same 25%-of-capital single-path breach applies identically to CONTROL — not specific to U6B, but
  unresolved by this review.

## Disposition

**U6B_PRODUCT_A_SCALE_RATE: NOT PROMOTED — CLOSED, with substantially stronger grounds than the
original construction's own wash-threshold finding.** Per directive sec45: no tuning attempted;
Product A `SolarWaveSMMaster_v4` remains the unchanged incumbent. This closes the O2-flagged
"high-priority frozen challenger" status — the improvement O2 found does not survive independent
decomposition, so this candidate does not return to frozen-challenger status pending future
re-evaluation; it is closed on the merits.
