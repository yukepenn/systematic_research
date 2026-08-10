# O2 — owner-utility re-adjudication: dry run complete, one real finding for U6B, one capital-mismatch caution for Product B-NQ

**Disposition: UTILITY RE-ADJUDICATION / POST-DISCOVERY DECISION ANALYSIS (per directive sec14) —
not new statistical evidence, not an automatic promotion.** Satisfies both preconditions the
blind review left open (`PREREGISTRATION.md` answers the 4 items; this run is the real-data
sanity check). Correctness gate: **PASS** — all three certified canonical nets (Product A legacy
$177,924.40, Product B-NQ $301,915.92, Product B-MNQ $28,587.10) reproduced exactly before any
`primary_objective_v2` score was trusted.

## Precondition (ii) satisfied — and it surfaced a real discrepancy worth disclosing

`primary_objective_v2` had **never been executed end-to-end on real P&L** before this run — its
34/34 tests were all synthetic fixtures, and the campaign's own previously-quoted Product-A
Appendix figures (J=+0.1241 mixture / J=−0.1259 Γ-minimax) were **hand arithmetic** on already-
published v1 per-method components, not actual v2 module output. Running the real module on the
real certified Product-A daily series gives **J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax)** —
same sign pattern (positive mixture, negative Γ-minimax, so **still INCONCLUSIVE**), but
materially different magnitude from the hand-computed estimate. This is exactly the kind of gap
the blind reviewer worried the "34/34 PASS" synthetic-only testing could hide, and exactly why
this precondition was worth insisting on before trusting v2 for a real scoring pass. **The
hand-arithmetic Appendix numbers should not be cited as v2 output going forward — this run's are
the first genuine ones.**

## Headline scores (C=$100,000, L=1.0 fixed_fraction, per `PREREGISTRATION.md` item a)

| candidate | net | J (mixture) | J (Γ-minimax) | P_ruin (mixture) | verdict |
|---|---:|---:|---:|---:|---|
| Product A — legacy proxy | $177,924.40 | +0.0549 | −0.2220 | 18.2% | INCONCLUSIVE |
| Product A — genuine MNQ | $178,687.40 | +0.0594 | −0.2146 | 18.0% | INCONCLUSIVE |
| Product B-NQ | $301,915.92 | **−1.1502** | −1.2134 | **94.7%** | NEGATIVE |
| Product B-MNQ | $28,587.10 | +0.0602 | +0.0598 | 0.0% | **POSITIVE (clean)** |
| U6B control (= Product A) | $177,924.40 | +0.0549 | −0.2220 | 18.2% | INCONCLUSIVE |
| U6B F0.5 | $178,213.70 | +0.0581 | −0.2071 | 18.0% | INCONCLUSIVE |
| U6B F0.7 | $178,531.30 | +0.0584 | −0.2114 | 18.0% | INCONCLUSIVE |

## Reading Product B-NQ's result: a capital-mismatch artifact, not "Product B-NQ is broken"

A 94.7% modeled probability of breaching a 25%-drawdown ruin barrier at $100k capital / 1x
leverage is a real, expected consequence of comparing every candidate at one uniform capital
level regardless of its own risk scale — Product B-NQ's own certified EOD maxDD is $59,717.44,
already ~60% of a $100k account, so a 25%-DD breach is close to guaranteed historically at this
sizing. This is **not new evidence Product B-NQ is unsound** — it is evidence that $100k is the
wrong capital level to evaluate it at. Directive sec16 calls for exactly this: match risk before
comparing growth (same drawdown budget, not the same dollar capital). **This pass does not do
that risk-matching** — it was scoped to the pre-registered headline only, per items (a)-(c). A
proper cross-candidate comparison needs each object's own capital-map-implied capital
requirement, not one shared $100k figure. Flagged as the clear next step, not resolved here.

## The one genuine new finding: U6B's improvement over control survives BOTH aggregation conventions

**[SUPERSEDED 2026-08-09: this heading overstates the finding.** U6B's independent adversarial
review (`runs/U6B_PRODUCT_A_SCALE_RATE/adversarial_review/REPORT.md`) decomposed the
Γ-minimax/mixture delta by individual bootstrap method and found the positive reading below is
**entirely** the `moving5` method (ΔJ=+0.0149); the other two methods (`moving20`: −0.0015,
`stationary60`: −0.0037) show the candidate *worse* than control. The `moving5` improvement itself
traces to only 18 net path-flips out of 2,000 bootstrap paths (0.9%), every one landing within
~1.5 percentage points of the exact 25%-of-capital ruin threshold — boundary-threshold noise, not
a systematic mechanism. "Survives both conventions" should read "positive under one of three
underlying resampling methods, driven by threshold-boundary noise" — a materially weaker claim.
U6B's final disposition is **NOT PROMOTED**, closed on the merits. See the adversarial review for
the full decomposition.]**

Product A's own absolute utility is INCONCLUSIVE (mixture positive, Γ-minimax negative) — but the
**delta** between U6B's candidates and control is **positive under both conventions**:

| | Δ J (mixture) vs control | Δ J (Γ-minimax) vs control |
|---|---:|---:|
| F0.5 − control | +0.00321 | **+0.01490** |
| F0.7 − control | +0.00353 | **+0.01058** |

This is a materially stronger statement than U6B's own original closure ("real, correctly-signed,
zero right-tail damage, but the 2022-2025-only delta falls under the preregistered 1% wash
threshold"): under this richer utility measure, the improvement doesn't just avoid being
disqualified by an arbitrary wash threshold — it is **directionally robust to which of the two
defensible aggregation conventions you trust**, even while the baseline's own absolute sign
remains contested. This is new information, not a re-statement of U6B's original result.

## Promotion governance (per `PREREGISTRATION.md`'s binding policy and directive sec18)

This does **not** promote U6B. Per sec18, immediate canonicalization requires no new parameter
selection (satisfied — F0.5/F0.7 were already frozen), all original gates already satisfied
(satisfied per U6B's own closure), the original rejection being genuinely only a now-superseded
utility criterion (**plausible** — the 1% wash threshold is exactly the kind of arbitrary
criterion sec17 flags as reconsiderable), robustness under the updated utility (**newly shown
here**, for the delta specifically) — **and** an independent adversarial reviewer confirming the
classification, which has not happened. **Recorded here as a high-priority frozen challenger with
new, favorable evidence**, not as a promotion.

## What this pass did not do (explicitly out of scope, not silently skipped)

- No risk-matched (equal-drawdown-budget) capital comparison across objects (flagged above).
- No broader O2 pass across the full DRAWDOWN_RECONCILIATION.md 7-object candidate list — this
  pass was deliberately scoped to the incumbents plus U6B, the one candidate already flagged as
  the closest call in campaign history. Extending to the full registry is a natural next step.
- No independent adversarial review of the "U6B rejection was genuinely only a wash-threshold
  artifact" classification (sec18's final requirement).

## Verdict

**O2 infrastructure is now genuinely usable** (correctness-gated, pre-registered, real-data-
verified) rather than blocked or synthetic-only. It produced one concrete, disclosed correction
(the Appendix hand-arithmetic numbers don't match real module output), one methodological caution
(uniform $100k capital misrepresents differently-scaled objects — Product B-NQ needs risk-matched
comparison), one clean result (Product B-MNQ: POSITIVE under both conventions, no capital
mismatch at its own scale), and one genuine new piece of evidence for U6B (delta robust to both
aggregation conventions) that raises, but does not resolve, the case for eventually promoting it.
