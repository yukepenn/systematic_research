# O1 — BLIND REVIEW OF THE D1 AGGREGATION CHOICE. **They agree. And the mathematics is only partly decisive, so the range rule binds.**

_2026-08-09. Owner directive R3. Append-only; nothing in `O1_REPAIR_PREREGISTRATION.md`,
`O1_OBJECTIVE.md`, `red_team/` or any spec is edited (C7)._

## Why this review existed

The blind repair moved the daily objective **+0.0210 → +0.1241**, i.e. *up*, and the repairing
agent disclosed unprompted that the rule it chose was **the most favourable of the four it
considered**, and that it could not be blind to that because v1 publishes every component. An
objective function defines what counts as success in this program. An objective altered by a
choice that raises the score, self-flagged as the most favourable available, is the highest-risk
governance item on the board. §13 rule 11 — *something looks too good, assume a bug first* —
applied, and O2 was held.

## How the review was kept blind

The reviewer was given the **mathematical question and the six candidate conventions, and
nothing else**. It was **not** told which convention had been chosen, **not** told which raises
or lowers any score, and **not** told that a score existed at all. It was explicitly forbidden
to read any file in this repository — not the module, not the pre-registration, not the earlier
red team — so that no artefact could leak the answer. The six options were restated by hand in a
neutral order with descriptions of comparable length, and were relabelled (A–F) so that the
original numbering (0, i, ii, ii′, iii, iv) could not itself carry a hint.

## The outcome: **AGREEMENT**

The reviewer independently chose the **equal-weight mixture applied to both terms** —
`mean_m E[g] − λ·mean_m P(ruin)` — which is exactly option **(i)** of the repair's own list and
exactly what the repair implemented. Per directive R3, the two are now compared and they agree,
so the repair proceeds and this document says so.

The reviewer reached it by a route the repair did not use, which is the useful part:

- **Decomposition invariance**, and this is stronger than anything in the repair. Write the same
  objective as `J = E[g·1{ruin}] + E[g·1{no ruin}] − λ·P(ruin)` and apply "worst-case each term":
  the result is strictly *smaller* than the term-wise-worst rule on the original two-term form,
  and splitting `u` more finely drives it down without bound. So the term-wise rules are not one
  rule but a family indexed by an arbitrary partition of the payoff, with no canonical member.
  That disqualifies them independently of any view about ambiguity.
- **`J` is linear in `F`** once you write `u(ω) = g(ω) − λ·1{ruin}(ω)`, so `J(F) = E_F[u]`. The
  minimum over the convex hull of the three schemes is therefore attained at an extreme point:
  `min_m J(F_m)` **is** the Gilboa–Schmeidler maxmin value over the credal set they generate.
- **The term-wise rules evaluate the objective outside the convex hull** of the models actually
  considered, and under an absorbing barrier that is worse than arbitrary: `g` and `1{ruin}` are
  functionals of the *same stopped path* and are strongly coupled, so taking one from the
  pessimistic-growth measure and the other from the pessimistic-ruin measure asserts a world
  where both pessimisms are simultaneously right about the same paths.
- **Under min/max rules, Monte-Carlo error enters as bias rather than noise**, and the bias is
  candidate-dependent. The consequence the repair had not identified: *the effective severity of
  the rule becomes a function of the number of bootstrap paths you happened to run* — double N
  and every candidate's score rises. A preference parameter must not be set by the compute budget.
- **Manipulability:** `min_m` rewards making the three schemes agree, so cosmetic changes that
  decorrelate a reported daily series (trade splitting, timing jitter across day boundaries)
  raise the score with no economic improvement. The mixture has no comparable channel.
- **Breakdown and scale drift:** `min` has breakdown point 1/M — one badly specified scheme
  captures the score for *every* candidate — and is monotonically non-increasing as the scheme
  list grows, so stored incumbent scores silently become incomparable to new challenger scores.

## But the mathematics does not determine a unique answer, and R3's fallback therefore binds

The reviewer was explicit, unprompted, that it would not manufacture a winner beyond where the
mathematics reaches:

- **Excluded outright:** the two term-wise rules (worst-each-term, and average-growth-with-worst-
  ruin). Notably the second is **not even reliably conservative** — the reviewer constructed
  numerical examples where it falls *below* the Γ-minimax value.
- **Admissible as coherent objects:** the equal-weight mixture, Γ-minimax, single-pre-registered-
  scheme, and data-driven block length. Single-scheme is admissible but dominated absent an
  argument for a particular block length; data-driven is "the right instinct with the wrong
  optimality target" (Politis–White optimises for a sample *mean*, while this functional is a
  504-session barrier crossing) and belongs as a diagnostic.
- **The choice between the mixture and Γ-minimax turns on whether the three schemes are three
  estimators of one quantity differing by a bandwidth, or three genuinely different states of the
  world.** The reviewer defends the first firmly — same data, same procedure, one knob, and
  nobody would defend "the future is generated by gluing five-day chunks of the past" as a state
  of the world — but states plainly that this classification **is not itself a theorem**.

**Therefore, per directive R3: the admissible set is {mixture, Γ-minimax}, and the range rule is
now BINDING POLICY.**

1. Every scored object reports `J` under **both** conventions.
2. Any object whose **verdict flips across that range is recorded INCONCLUSIVE**, never passing.

The repaired module already returns `J_worst = min_m J_m` — which *is* the Γ-minimax convention —
alongside a mandatory `model_determined_sign` flag, so the machinery satisfies this without
further code. What changes is that it is now a rule rather than a disclosure.

**Immediate consequence, and it is not a comfortable one.** Product A's daily objective is
**+0.124 under the mixture and −0.126 under Γ-minimax**. The verdict flips across the admissible
range. **Product A's daily objective is INCONCLUSIVE** and may not be quoted as a single number.
The O1a finding is unaffected and survives on the same mixture on both legs: daily **+0.124** vs
intraday **−0.140**.

## What the reviewer added that the repair had not, and which should be adopted

Recorded here as recommendations, **not** implemented in this pass, so that the repair's frozen
argument is not retroactively enlarged:

1. **Put conservatism in a promotion gate, not in the scalar.** Require scheme-wise *dominance*
   (a challenger must beat the incumbent under all three schemes) and a constraint
   `max_m P(ruin) ≤ p̄`. Dominance is strictly more informative than `min`, because `min_A > min_B`
   does not imply scheme-wise dominance while dominance implies it.
2. **Common random numbers.** Score challenger and incumbent on the *same* block index draws and
   rank by the paired `ΔJ` with its paired standard error. This cancels most of the Monte-Carlo
   noise in differences and addresses the noise concern far better than any choice among the six.
3. **Report the profile `J(b)` over a grid of block lengths** (5, 10, 20, 40, 60, 120) rather than
   aggregating three points. If the profile has not flattened by b = 60, the ensemble does not
   bracket the dependence scale — which no scalar aggregation of three points can reveal.
4. **Equal weights are themselves questionable in one specific direction.** If truncation bias is
   O(1/b), the b = 5 member's bias is 12× the b = 60 member's, so equal weighting lets the most
   biased member dominate the average. That is an argument for *unequal, bias-aware* weights —
   a refinement of the mixture, not of Γ-minimax.
5. **The dominant model risk is not bandwidth at all.** All three schemes resample one realised
   series and thereby condition on one regime, one parameter draw, and one realisation of the
   strategy's own overfitting. If the series is non-stationary all three are inconsistent *for the
   same reason* and their spread does not bracket that error. Worst-casing over `b` buys
   conservatism where the risk is small while feeling like robustness — which the reviewer calls
   the most dangerous property of the min-based rules in this application.

## Four underspecified items the reviewer flagged, each of which may matter more than the aggregation

Filed as open questions, unanswered here:

- **Is the fixed fraction `f` pre-registered, or optimised per candidate?** If optimised, `J` is
  already a max over `f` and carries a selection bias that no aggregation convention touches.
- **Is the number of bootstrap paths `N` common across schemes and candidates?** Under any
  min/max rule it must be, or scores are not comparable — which now matters because Γ-minimax is
  in the reported range.
- **Is the historical sample length `n` common across candidates?** The b = 60 estimate's variance
  scales with n/b, so unequal `n` biases min-based scores.
- **At what `P(ruin)` was λ calibrated?** A single λ makes the trade-off linear in `p`, a strong
  commitment near `p ≈ 0` where most promotable candidates live.

## Disposition of O2

**O2 retro-scoring is UNBLOCKED on the aggregation question** — the choice is independently
confirmed and the divergence clause did not fire. It remains subject to two binding conditions
established here: every score is reported under **both** admissible conventions, and any
candidate whose verdict flips is **INCONCLUSIVE**. The four underspecified items above should be
answered before O2 runs, because at least the first (`f` optimised per candidate) would introduce
a selection bias the whole exercise is meant to control for.
