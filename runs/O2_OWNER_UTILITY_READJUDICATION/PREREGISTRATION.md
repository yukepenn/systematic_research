# O2 pre-registration — answers to the 4 items flagged by the blind review, frozen before any candidate is scored

Per `O1_BLIND_REVIEW_OUTCOME.md`'s independent blind review (git commit `cd88199`), O2 retro-
scoring is conditionally unblocked on the aggregation question (mixture vs Γ-minimax — the range
rule is binding policy: report both, any verdict-flip is INCONCLUSIVE), subject to two remaining
preconditions: (i) pre-register answers to four previously-unanswered items, (ii) run one real-
data sanity check of `primary_objective_v2` before trusting it for a multi-candidate pass. This
document satisfies (i). `01_dry_run_sanity_check.py` / `REPORT.md` satisfy (ii).

## Item (a) — is the fixed fraction f (leverage L in `fixed_fraction` mode) pre-registered, or optimized per candidate?

**Pre-registered, not optimized.** Verified directly from `O1_OBJECTIVE.md` §1.2: *"Target
leverage — L = 1.0 (headline), grid {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0} reported."*
The stated reason: *"It is the deployed champion size — one unit of the product as it actually
exists. Any other headline leverage would be a number the program has never run."* — i.e. L=1.0
is fixed **uniformly across every candidate**, chosen for a reason independent of any candidate's
own results (it's the deployed unit size), not selected post-hoc to maximize any candidate's
score. The wider grid is reported only as a secondary cross-check, never substituted for the
headline. **This O2 pass reuses L=1.0 for every candidate, with no per-candidate leverage
selection.** This closes the item the reviewer flagged as "possibly the most important" — there
is no selection-bias channel here.

## Item (b) — is bootstrap path count N common across schemes and candidates?

**Yes, by construction, and this pass will not override it.** `N_BOOT` and `SEED` are module-
level constants in `primary_objective_v2.py`, used as the function's defaults; every call in this
O2 pass uses the defaults unmodified for every candidate. Verified: no per-candidate `n_boot=`
override appears anywhere in this pass's scoring script.

## Item (c) — is historical sample length n common across candidates?

**Not automatically — this needs an explicit rule, which this pass adopts:** every candidate
scored in this O2 pass is evaluated over the **identical canonical window** (2022-01-03 through
2026-05-31, the shared dev window every certified net in this campaign already uses). Any
candidate whose own native series is shorter than this window (e.g. a short-history Track-C
candidate) will be **excluded from this pass** rather than compared on unequal-n terms — per the
reviewer's own concern that the b=60 block-bootstrap estimator's variance scales with n/b, so
unequal n would bias any Γ-minimax (min-based) comparison. This O2 pass is therefore scoped to
**Track-L (long-history) candidates only.**

## Item (d) — at what P(ruin) was λ calibrated?

**Not separately re-resolved here — named as a standing, disclosed limitation, exactly as the
reviewer's own fallback suggests.** λ is held at its single derived module-constant value
(`franchise_lambda`, calibrated once on the reference/champion object, never per-candidate) for
every candidate in this pass. Per the reviewer's own caution, a single λ makes the CE_g/P_ruin
trade-off linear in p — a real commitment near p≈0, where most promotable candidates live. This
pass mitigates it by **always reporting P_ruin itself alongside J**, not J alone, so a reader is
not solely dependent on the linear-trade-off assumption at one calibration point. This is a
disclosed limitation of the primary objective as currently specified, not something this pass
resolves — consistent with directive sec74's instruction that utility trade-offs are judgment
calls made transparently, not hidden inside one scalar.

## Binding policy for this pass (inherited from the blind review, restated for clarity)

Every candidate is scored under **both** aggregation conventions (mixture, primary; Γ-minimax,
`J_worst`). Any candidate whose verdict (sign of J, or ranking relative to another candidate)
flips between the two conventions is recorded **INCONCLUSIVE** and may not be quoted as a single
number or used alone to justify a promotion decision. This pass is **UTILITY RE-ADJUDICATION /
POST-DISCOVERY DECISION ANALYSIS only** — per directive sec14, it does not manufacture new
statistical significance, and per sec18 a candidate becomes canonical immediately only if no new
parameter selection occurred, all original causal/chronology/executable gates were already
satisfied, and the rejection was genuinely only a now-superseded utility criterion (the arbitrary
wash threshold) — otherwise it remains a high-priority frozen challenger pending independent
adversarial review, not an automatic promotion.
