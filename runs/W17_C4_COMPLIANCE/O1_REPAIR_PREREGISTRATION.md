# O1 REPAIR — PRE-REGISTRATION OF THE CORRECTED OBJECTIVE

_New file. Appends to the record; nothing in `O1_OBJECTIVE.md`, in `red_team/`, in any
`spec.yaml`, in `CURRENT_TRUTH.md` or in `research/registry/` is edited (rule C7)._

**Module repaired:** `src/analytics/primary_objective_v2.py` (NEW; v1 left untouched on the
record and imported by reference).
**Tests:** `src/analytics/test_primary_objective_v2.py` (plain `python`, 34/34 PASS, 1.0 s;
every fixture synthetic).
**Authoritative defect list:** `runs/W17_C4_COMPLIANCE/red_team/RED_TEAM_o1_objective.md`
(D1–D15). **Framing:** `red_team/INDEX.md` §5, which blocks O2 until "the aggregation rule
and λ calibration [are] fixed and re-pre-registered".

**Scope of this pass.** Repair D1, D4, D9; triage D2, D3, D5, D6, D7, D8, D10, D11, D12,
D13, D14, D15. **No object is scored here.** No candidate's daily or intraday P&L was loaded
by this pass. The consequence arithmetic in the Appendix is arithmetic on components already
published in `O1_OBJECTIVE.md` §5.2/§6.2 and in the red-team document — it is not a new
evaluation, and it was performed *after* everything in §§A–H below was written to disk.

**Nothing here establishes that future profitability is achievable.**

---

## A. THE DEFECTS

### D1 — asymmetric bootstrap aggregation (sign-flipping)

`primary_objective.py:682-686`. `P_ruin` is the **max** over
{`moving5`, `moving20`, `stationary60`}; `CE_g` is the **arithmetic mean** over the same
three; and `J = CE_g − λ·P_ruin` is formed from the two. Pre-registration §2.3 specifies the
max for `P_ruin` and says **nothing** about combining `CE_g` across methods. The word
"pooled" appears twice in the 744-line report, both times inside a result table, never in the
formal-definition section and never in "Open weaknesses".

The mathematical content of the defect is not "one term is conservative and the other is
not". It is that **the resulting scalar is not a functional of any probability
distribution.** `CE_g` is read off one object and `P_ruin` off a different one, so there is
no model of the world — none of the three, none of their mixtures, none outside the family —
under which `J` is the expected value of anything.

### D4 — λ calibration convention mismatch (sign-flipping)

`O1_OBJECTIVE.md:141`. λ is derived from `g_ref = ln(1 + 177315.1/100000)/(1139/252) =
0.225668 /yr`, which is the house **non-compounded** `logG`: the growth rate of an account
that banks a total dollar profit once and never reinvests. But λ multiplies `P_ruin` inside
`J = CE_g − λ·P_ruin`, where `CE_g` is the **compounded** fixed-fraction log growth rate
(`ℓ_d = log1p(L·x_d/C)`, size reset daily in proportion to equity). The two conventions are
different functions of the same P&L path and differ by ~1.5× on the reference object. λ is
therefore expressed in the wrong units for the quantity it prices, and biased low.

### D9 — the shipped `min_unit` code path, and the test that certifies it

`primary_objective.py:850-886`. Three separate defects, only the third of which the red team
named:

1. **Floating-point floor-to-multiple.** `np.floor(u/min_unit)*min_unit` is wrong on exact
   multiples: `floor(0.3/0.1) = 2` because `0.3/0.1 == 2.9999999999999996` in IEEE double.
   Verified: `0.3/0.1 → 0.2`, `0.29/0.01 → 0.28`, `2.4/0.4 → 2.0`, `0.7/0.1 → 0.6`. A whole
   granule is silently lost whenever the target lands on a multiple.
2. **Position reversal at negative equity.** The target `u = L·E/C` goes negative when equity
   does, and `floor` makes it *more* negative, so the model **reverses the position and keeps
   trading**. Verified on a synthetic path: v1 continues from −$1,900,000 to −$20,900,000.
   Invisible in v1's outputs because the log-space figures are floored at `ε·C`.
3. **The de-sizing trap.** Once `u` floors to zero the equity stops moving, so `u` is
   recomputed identically and stays zero **forever**. On a synthetic fixture at the module's
   own advertised settings (C = $100k, L = 1, `min_unit` = 1), **91.0%** of paths freeze;
   `P_ruin` collapses from 0.327 to 0.010 and **J flips from −0.253 to +0.008**. A frozen
   account cannot draw down, so contract granularity is made to look like risk *reduction*.
   `test_primary_objective.py:224-228` asserts only `np.isfinite(J)` and prints the artifact
   as a PASS.

A fourth, related: in `min_unit` mode v1 reports `p_equity_nonpositive` from the
**continuous** model's clip test (`bad_day[idx]`), i.e. for a different model than the one it
just simulated. And `min_unit` + `intraday_path` together are silently accepted, with the
daily leg granular and the intraday leg continuous — the "gap" then conflates granularity
with observation frequency.

---

## B. OPTIONS CONSIDERED FOR D1

Write `F_m` for the distribution over 504-session paths induced by resampling scheme
`m ∈ {moving5, moving20, stationary60}`, and `J(F) = E_F[g] − λ·P_F(ruin)`.

| # | rule | is it `J(F)` for some `F`? | note |
|---|---|---|---|
| (0) | v1: `mean_m CE_g − λ·max_m P_ruin` | **no** | the shipped defect |
| (i) | equal-weight mixture: `mean_m CE_g − λ·mean_m P_ruin` | **yes**, `F̄ = ⅓ΣF_m` | = pooling all 3·n_boot paths |
| (ii) | term-wise worst: `min_m CE_g − λ·max_m P_ruin` | **no** | same incoherence as (0), pointed the other way |
| (ii′) | Γ-minimax: `min_m J(F_m)` | not a single `F`, but a well-defined `inf` over a family | the standard robust-decision object |
| (iii) | single pre-registered method | **yes**, `F_m` | needs a defensible choice of one block length |
| (iv) | data-driven block length (Politis–White `b̂`) | **yes**, `F_b̂` | introduces a per-candidate tuning knob into a scoring rule |

Option (ii) is excluded immediately: it has the same defect as (0) and additionally adds
unquantified slack, since `min_m CE_g − λ·max_m P_ruin ≤ min_m J(F_m)` always, with equality
only when the argmin and argmax coincide.

Option (iv) is the statistically most principled *estimator* — the block bootstrap has an
optimal block length depending on the dependence structure and the statistic, and 5/20/60 are
three arbitrary guesses at it. It is **rejected for this use** because `J` is a scoring rule
applied across many candidates over time: a tuning parameter fitted to each candidate's own
autocovariance makes the scale candidate-dependent and creates a channel through which a
candidate's serial structure, rather than its economics, moves its score. Recorded as
recommended future work, outside this repair.

Option (iii) is rejected because no principled ground was found for preferring 5, 20 or 60 to
each other; choosing one *after* the per-method results are public (they are, in
`O1_OBJECTIVE.md` §5.2) would be selection, not pre-registration.

That leaves **(i)** and **(ii′)**, and the choice between them is the substance of this
document.

---

## C. THE CHOICE, AND THE ARGUMENT

> **CHOSEN: (i) — the equal-weight mixture, applied identically to BOTH terms.**
>
> `J = J(F̄) = E_F̄[g] − λ·P_F̄(ruin)`, `F̄ = ⅓(F_m5 + F_m20 + F_s60)`.
>
> `min_m J(F_m)` is **retained and always reported** as `aggregation.J_worst`, together with
> `J_by_method` and a mandatory `model_determined_sign` flag.

### C.1 The pooled-sample identity — why (i) is coherent and no max-based rule is

Both terms are expectations under the path distribution:
`CE_g(F) = (252/H)·E_F[log(W_H/W_0)]` and `P_ruin(F) = E_F[1{ruin}]`. Expectation is linear,
and `J` is affine in the two. Therefore, with equal `n_boot` per method,

```
    mean_m J(F_m) = mean_m ( E_{F_m}[g] − λ·E_{F_m}[1_ruin] )
                  = E_F̄[g] − λ·E_F̄[1_ruin]
                  = J(F̄)
```

and, concretely,

> **pool the 3 × n_boot resampled paths into one sample of 6,000 and compute `CE_g` and
> `P_ruin` on the pool.** That is exactly what `aggregate_mixture` does, and test D1-1 pins
> the identity to 1e-12.

`F̄` is a legitimate probability model, statable in one sentence: *draw a resampling scheme
uniformly at random, then draw a path from it.* No analogous statement exists for any rule
containing a `max` or a `min` over methods: `max_m E_{F_m}[1_ruin]` is an order statistic of
three estimates, not an expectation under anything.

This is the decisive property. An objective is a decision-theoretic object; it has to be the
expected value of something under some model, or the "trade-off" it claims to express is not
a trade-off between quantities measured on the same world.

### C.2 The three methods estimate the SAME quantity — so this is estimator combination, not ambiguity aversion

`moving5`, `moving20` and `stationary60` are not three candidate states of the world. They
are three **tunings of one estimator** of one functional of one unknown data-generating
process. Block bootstrap with block length `b` reproduces dependence only up to lag `b`; at
finite `b` the resampled series is biased in a direction set by the mismatch between `b` and
the true dependence length. All three are known to be wrong; none is a hypothesis that could
be true.

Γ-minimax (option ii′) is the right tool when the members of the family are genuine
alternative *models*, each of which might be the truth, and the loss is asymmetric. It is not
the right tool for combining three biased estimates of one number, because:

- **Selection bias.** `E[max_m P̂_m] ≥ max_m E[P̂_m]` by Jensen. Taking the extremum over a
  family of noisy estimators is upward-biased for the target even before any conservatism is
  intended, and the bias grows with the number of methods and with their Monte-Carlo noise.
  The red team's own 8-seed study puts the MC sd of `moving5`'s `P_ruin` at 0.0070 and of `J`
  at 0.0074 — the same order as the headline value. Averaging over methods reduces MC
  variance; taking an extremum converts it into bias.
- **Per-candidate selection.** `max_m P̂_m` does not consistently pick "the most conservative
  method"; it picks *whichever block length happens to be most adverse for this candidate*.
  Applied across the many objects O2 will score, that is a per-candidate selection over three
  correlated estimators, and it systematically overstates ruin for all of them.
- **Instability of the scale.** The value of any extremum rule is set entirely by one member
  of an editable list. Adding a `moving2` in 2027 would mechanically lower every candidate's
  `J` and retroactively invalidate every earlier score. `J` is meant to be a comparable scale
  across objects and across time; `min`/`max` is not one. The mixture also depends on the
  list, but smoothly and with every member contributing, and its arbitrariness is bounded by
  the reported spread.

### C.3 What the objective is FOR, and where the conservatism goes

The objective is a decision rule for whether to promote a levered trading system, and the
ruin term is a penalty. That asymmetry is real, and it is **already priced, explicitly and
arguably**, in two places: the absorbing 25% barrier, and λ. Burying a *second*,
unquantified risk premium inside an order statistic over three legacy tuning values makes the
total premium unstated — a reader cannot tell how much of `J` is preference and how much is
measurement. The repaired design puts every unit of conservatism where it can be argued with:

| where | what |
|---|---|
| `λ` | the priced cost of a ruin event, derived in §D, grid always reported |
| absorbing barrier | in-window forfeiture, priced inside `CE_g` |
| `aggregation.J_by_method` | the full per-method band |
| `aggregation.J_worst` | `min_m J(F_m)` — the Γ-minimax reading, for a reader who wants it |
| `aggregation.model_determined_sign` | fires when `J` and `J_worst` disagree in sign |

**Pre-registered output contract (binding on any use of this module):** `J` may never be
quoted without `J_worst` and the per-method band. When `model_determined_sign` is `True`, the
object's score is set by the choice of resampling method rather than by its P&L, the module
writes a warning into `integrity.warnings`, and the object must be reported as
**MODEL-DETERMINED** — a disagreement that is a finding in its own right and that may not be
resolved by picking the friendlier number. I deliberately do **not** pre-register a promotion
threshold here; thresholds are O2's business.

### C.4 Honest statement: this is the closest call in the repair

It is close, and a competent reviewer could land on (ii′) instead. The strongest argument
against my choice is governance rather than mathematics: §1.6 committed to the house
convention that "the worst member is the one acted on", and a repair that relaxes a
pre-registered conservatism is exactly the kind of move that deserves suspicion. Two things
answer it, and neither fully dissolves it:

1. What §1.6 pre-registered was `max` on `P_ruin` specifically. Applying it symmetrically
   gives option (ii), which is incoherent. `min_m J_m` is a *different* rule from the one
   pre-registered (its argmin need not be the argmax of `P_ruin`). So no repair is "the
   pre-registered rule, applied symmetrically" — every repair is a new rule, which is why
   `INDEX.md` §5 requires re-pre-registration, which is this document.
2. The conservatism is not removed, it is relocated to `J_worst` and made mandatory to
   report. On the worked example that flag fires immediately (Appendix), so the practical
   effect of my rule on that object is *not* a cleaner positive verdict — it is an explicit
   MODEL-DETERMINED verdict.

Both (i) and (ii′) rest on the same indefensible set {5, 20, 60}. Neither becomes principled
without §B option (iv). I record that as the honest limit of what this repair achieves.

### C.5 Disclosure of contamination

I could not be blind to the direction of this choice. `O1_OBJECTIVE.md` §5.2 and §6.2 publish
every per-method component, so anyone who reads the defect list can compute in their head
which aggregation rule raises the worked example's `J` and which lowers it. **The rule I
chose is the most favourable of the four on the daily barrier** (Appendix, table 1). I state
that plainly rather than claiming a blindness I did not have; the argument in §§C.1–C.3 is
the whole justification and must be judged on its own, and `J_worst` — which is negative for
that object — is returned in the same dict so that no re-run is needed to read the
conservative number.

---

## D. THE λ FIX — ALGEBRA AND THE SIZE OF THE BIAS

### D.1 The two conventions, precisely

For a dollar P&L series `x_d`, capital `C`, `N` sessions, `years = N/252`:

```
    NON-COMPOUNDED (house logG; = fixed_contracts mode's own g_ann):
        g_nc  = ln(1 + Σ_d x_d / C) / years

    COMPOUNDED (fixed-fraction; = the CE_g this objective actually averages):
        g_c   = ( Σ_d log1p(L·x_d / C) ) / years
```

On the published reference object (executable dev headline, `CURRENT_TRUTH.md`: net
$177,315.10 over 1,139 sessions, C = $100,000, L = 1):

```
    g_nc = ln(1 + 177315.10/100000) / (1139/252) = 1.019987 / 4.519841 = 0.225668 /yr   <- used by v1
    g_c  = ln(469020/100000)        / (1139/252) = 1.545542 / 4.519841 = 0.341931 /yr   <- the matching one
```

`469,020` is the reference object's terminal fixed-fraction equity on the same $100k base
over the same 1,139 dev sessions, published in `RED_TEAM_o1_objective.md` D4. A compounded
rate is path-dependent and cannot be recovered from a summary net, and no committed per-day
artifact exists for the executable object itself, so the twin is the only available basis —
the same substitution `O1_OBJECTIVE.md` §5.6 makes. Residual direction: the twin's dev net
($179,288.70) is 1.1% above the executable's, so `g_c`, hence λ, is marginally **high**,
i.e. marginally conservative. **`g_ref` is a module constant, calibrated once, never
recomputed per candidate** (see §H.3).

Ratio: `g_c / g_nc = 1.51520`.

### D.2 Correcting the forfeited horizon as well (double-count; §H.1)

§1.5's derivation is: a ruin event forfeits `H_f − H/2 = 9` further years of compounding,
amortized over `H = 2` years, and it explicitly claims *"so that it does not double-count the
in-horizon loss"*. It does double-count. The barrier is **absorbing**: a path that ruins at
`τ` earns exactly zero from `τ` to `H`, and that loss is already inside `CE_g` (which divides
the frozen terminal log wealth by the full `H`). Charging `(H_f − τ)` in λ charges the
interval `[τ, H]` a second time. The out-of-window forfeiture — the only part `CE_g` does not
see — is `H_f − H`.

```
    forfeited log wealth per ruin event  = (H_f − H) · g_ref
    amortized over the H-year window     λ = (H_f − H)/H · g_ref
```

This also **removes an assumption**: the corrected λ does not depend on the ruin time `τ` at
all, so §1.5's untestable "ruin is on average reached near the middle of the window" is no
longer load-bearing. (v2 measures it anyway, as `ruin.mean_first_ruin_years_given_ruin`, so
the old claim is auditable; on a synthetic fixture it came out at 1.04 yr, close to the
assumed 1.00 — the assumption was not unreasonable, it was simply the wrong quantity to use.)

### D.3 The repaired λ, and the size of the bias

`H_f = 10 yr` (unchanged from §1.5), `H = 504/252 = 2 yr`:

```
    λ_v2 (fixed_fraction)  = (10 − 2)/2 × 0.341931 = 4 × 0.341931 = 1.367725 /yr
    λ_v2 (fixed_contracts) = (10 − 2)/2 × 0.225668 = 4 × 0.225668 = 0.902673 /yr
```

Decomposition against the shipped value:

| step | λ | factor |
|---|---:|---:|
| §1.5 as derived, before rounding: `4.5 × 0.225668` | 1.015507 | — |
| **shipped** (§1.5 rounded to "≈ 1.0") | **1.000000** | ×0.98474 |
| convention fix alone (`4.5 × 0.341931`) — the red team's D4 proposal | 1.538691 | ×1.51520 |
| **+ double-count fix (`4.5 → 4.0`), i.e. λ_v2** | **1.367725** | ×0.88889 |
| **net vs shipped** | | **×1.36773** |

> **Size of the bias being corrected: λ was too low by 0.367725 /yr, i.e. the shipped value is
> 73.1% of the correct one (understated by 26.9%).** The two component errors partly offset:
> the convention error understated λ by 34.0% and the double-count overstated it by 12.5%.
> The red team's D4 correction, taken alone, would have **overshot** by +12.5% because it
> inherits the double-count.

Effect on any `J`: `ΔJ = −(λ_v2 − λ_v1)·P_ruin = −0.367725 · P_ruin`. It is strictly a
penalty rescaling — the growth term is untouched — so it can never change the *ranking* of two
objects that share a `P_ruin`, but it moves every `J` down in proportion to its own ruin
probability, and therefore does change rankings between objects with different ruin
probabilities. That is the point of fixing it.

### D.4 λ is now derived, not a constant

`primary_objective_v2.franchise_lambda(horizon_sessions, leverage_mode, franchise_years)`
computes λ at call time. Consequences, all tested:

- λ **switches convention with the mode**: `fixed_fraction` → compounded `g_ref`;
  `fixed_contracts` → non-compounded `g_ref` (which is that mode's own `g_ann`, so v1's
  λ = 1.0 was very nearly right *there* and wrong only in `fixed_fraction`, the primary mode).
- λ **tracks the horizon**: at `H = 1 yr`, λ = 3.077; at `H = 2 yr`, λ = 1.368; at `H ≥ H_f`,
  λ = 0 (nothing out-of-window is left to forfeit). v1's hard-coded 1.0 was silently wrong at
  every horizon but one — `horizon_sessions` is a free parameter of the public API.
- `lam=` may still be passed explicitly; `spec.lambda_source` records `derived` vs
  `caller_override`, and `spec.lambda_g_ref_used` / `spec.lambda_g_ref_convention` echo the
  calibration.

λ remains a **preference parameter, disclosed, not defended as true.** Its "franchise is
destroyed by an R1 breach" premise makes it an upper bound (see §F, D5).

---

## E. THE D9 FIX

`primary_objective_v2.fixed_fraction_rounded_stats` replaces
`primary_objective._fixed_fraction_rounded_stats`.

**Semantics, stated because they were never stated.** `min_unit` is the minimum tradable
size **in the same units as `leverage`** — multiples of the strategy's one-unit P&L series.
If the deployed unit is K contracts and single contracts are tradable, `min_unit = 1/K`.
(`min_unit = 1.0` therefore means "the whole strategy unit is indivisible", which for
Product A's 11-MNQ unit is an extreme setting, not the natural one; v1's own default
demonstration used it.)

1. **`floor_to_multiple(x, unit)`** floors with a relative tolerance
   (`floor(q + 1e-9 + 1e-12·|q|)`), exact on exact multiples at any magnitude. Test D9-1 pins
   six fp-hostile literals and asserts that v1's arithmetic differs on at least one, so the
   test cannot silently become vacuous. Test D9-2 is end-to-end: at `C = 1.0`, `L = 0.3`,
   `min_unit = 0.1` the target is exactly the float literal 0.3; v2 ends at equity 1.003,
   **v1 ends at 1.002** — the test calls v1 directly and asserts both values, so it would
   have failed against v1's code.
2. **The size target is clamped at zero before flooring**, so negative equity gives a flat
   account, never a reversed position. Test D9-6 asserts the *unclipped* terminal equity is
   −1,900,000 (v1's reversal reaches −20,900,000); v2 returns `terminal_equity` precisely so
   that this class of bug cannot hide behind the `ε·C` log floor again.
3. **The de-sizing trap is detected, counted, warned, and refused as a score.** The function
   returns a `granularity` block (`p_desized_to_zero`, `p_flat_on_final_step`,
   `mean_frac_steps_flat`, `mean_first_flat_step_given_flat`, `n_negative_unit_steps`,
   `p_equity_nonpositive`), and asserts the invariant that de-sizing is absorbing (a flat
   account's equity is frozen, so the target never recovers) rather than assuming it.
   **Pre-registered degeneracy bar: `MIN_UNIT_DEGENERACY_BAR = 0.05`.** If more than 5% of
   resampled paths de-size to zero under any headline method, `primary.objective_J` is set to
   **NaN**, `primary.objective_J_is_degenerate` is `True`, and a loud warning is appended.
   Every component — including the number that *would* have been reported, under
   `objective_J_before_degeneracy_nan` — stays in the dict, so nothing is deleted (C7); only
   the quotable scalar is withdrawn.
   The 5% bar is chosen as a round, small number on the reasoning that a granularity model in
   which one path in twenty stops trading altogether is no longer measuring granularity; it
   is not calibrated against any candidate's result and I did not look at one to set it.
4. **`p_equity_nonpositive` in `min_unit` mode now comes from the stepped granular equity**,
   not from the continuous model's clip test (test D9-7).
5. **`min_unit` together with `intraday_path` now raises `NotImplementedError`** instead of
   silently pairing a granular daily leg against a continuous intraday leg (test I2).
6. `min_unit` is validated with `is not None` and required positive; v1's `if min_unit:` made
   `min_unit = 0` silently disable granularity *and* bypass the mode guard.

Test D9-5 pins the correctness property that matters: at fine granularity
(`min_unit = 0.001`) the granular model converges to the continuous one
(`|ΔJ| < 0.02`, measured 0.0001) and is not flagged degenerate. Test D9-4 pins the
pathology itself — granular `P_ruin` collapses below continuous **and** the degeneracy flag
is `True` — so the artifact can never again pass as a benign number.

---

## F. THE OTHER TWELVE DEFECTS — WHAT I DID NOT FIX, AND WHY

Each addressed by name. "Surfaced" means v2 adds an output or a label so the defect is
visible, without restating any published number.

**D2 — the CDaR materiality bar is decided on the most favourable method, mislabelled
"worst".** *Not fixed as a verdict.* The verdict lives in a frozen report (§6.3) which C7
forbids me to edit, and re-deciding it would require running O1a on a candidate, which this
pass may not do. **Surfaced:** v2 replaces `cdar_matched_ratio_worst` with
`cdar_matched_ratio_max_over_methods`, `..._min_over_methods` and
`..._n_methods_over_bar`, plus a `_D2_note` stating in the returned dict that `max` is the
most *favourable* method for the hypothesis, not the worst. v2 also adds
`cdar_matched_ratio_mixture` — the ratio of mixture means, which is the only version of the
statistic that is a functional of a single model and hence the D1-consistent one. **v2 takes
no verdict.** O2 must pre-register which of these is the bar before looking at it. Note the
red team's arithmetic stands: two of three headline methods (1.150, 1.197) fail the
pre-registered 1.20 bar.

**D3 — no Monte-Carlo standard error on a scalar whose sign is the point.** *Partially
fixed.* v2 returns `primary.monte_carlo_se_NOT_a_CI_on_the_process` =
`sd(g − λ·1{ruin})/√N` on the pooled sample, plus `n_pooled_paths`; test M6 confirms it
scales as `1/√n_boot`. **What is deliberately not fixed, and is the more serious half:** no
uncertainty measure anywhere in this module reflects sampling uncertainty about the
*process*. As `n_boot → ∞` the MC se → 0 while the estimate stays conditioned on ONE realized
1,139-session sample. The returned key is named so it cannot be mistaken for a confidence
interval. A genuine interval needs an outer resampling of the sample itself, which is a
separate piece of work.

**D5 — §2.2 point 3 is factually wrong (53.5% of ruined paths terminate positive; absorption
costs only 0.054 of CE_g, so absorption is not what makes high leverage unattractive).**
*Not fixed.* It is a prose claim in a frozen document; the code was never wrong. v2 does not
repeat the claim anywhere. It **does** matter to §D: my double-count argument needs only that
the in-window loss is *inside* `CE_g`, not that it is large, so D5 does not weaken it. D5
does weaken λ in the other direction — if an R1 breach leaves the median ruined path with
positive terminal wealth, "the franchise is destroyed and earns zero for `H_f − H` years" is
a strong premise, and λ = 1.368 should be read as an **upper bound** on the true opportunity
cost. Disclosed, not adjusted: adjusting it would require a model of post-ruin redeployment
that nothing in this campaign has.

**D6 — the headline "×1.497" compares two non-overlapping drawdown episodes ten months
apart.** *Not fixed.* `historical_intraday_vs_daily` computes exactly what it claims (max
over the path); the defect is the prose gloss "same trades, same fills, same capital — only
the observation frequency differs", which implies an episode-matched statistic that a
max/max ratio is not. Building an episode-matched comparison requires a candidate's intraday
series to develop and validate against, which this pass may not load, and shipping untested
code into a repair module is worse than the disclosure. Recommended as O2 follow-up. The
*binary* ruin claim (close never breaches, intraday breaches at 2025-07-14 09:51) is
unaffected and survives.

**D7 — the effect filed under "nulls" (method spread) is larger than the effect declared
MATERIAL (the intraday gap), and the two are never placed side by side.** *Not fixed at the
report level* (frozen). **Structurally mitigated:** under D1 the two are now forced into the
same object — `ruin.daily_close.spread_max_minus_min_over_three` and
`ruin.gap.headline_abs` sit in one dict, and `aggregation.model_determined_sign` fires
precisely when modelling choice dominates, writing a warning into the top-level integrity
block. Whether a report places them side by side remains a writing duty, not a module
guarantee.

**D8 — the module's returned `capital_needed_at_thr` (H = 504 horizon) contradicts §5.3's
full-sample-length convention, and the §5.3 null holds under only one of them.** *Not
resolved.* Resolving it means recomputing a candidate's capital map, which this pass may not
do. **Surfaced:** `legacy_diagnostics_NOT_GATES._D8_note` states in the returned dict that
these figures are at the evaluation horizon, not the full-sample length, and that the two
conventions give different bands. O2 must pre-register which convention the capital-map
cross-check uses **before** computing either.

**D10 — the LOCKED-FORWARD guard is vacuous on undated input.** ***Fixed*** (outside the
assigned three, deliberately). `_index_is_datelike` did `pd.to_datetime(idx[:5])`, which
succeeds on an integer `RangeIndex` (ints read as ns since epoch), so a bare array was
flagged `dated=True` with no warning and the campaign's locked-forward rule was never
checked. v2 refuses numeric and boolean indices as dates, and raises when an explicit date
column parses to pre-1990 timestamps (the signature of an integer `YYYYMMDD` misparse).
Tests D10-1/D10-2 assert the new behaviour *and* assert v1's old behaviour, so the repair is
documented. Fixed rather than triaged because carrying a known-vacuous safety guard into a
new module would be indefensible; the cost is two functions and no change to any number.

**D11 — three code paths populate `cdar_frac` with two different statistics, and a log-space
mean is dollarized.** *Surfaced, not unified.* Unifying would restate published tail figures,
which C7 does not allow me to do silently. v2 computes `cdar_frac_arith` — the arithmetic
mean of drawdown *fractions* — correctly in **all** paths (a new helper,
`cdar_frac_arith_from_loginc`, supplies it for the continuous path, where it was not
recoverable from v1's return), dollarizes **that** one, and carries a `_cdar_note` in the
returned dict. v1's `cdar_frac` key keeps v1's meaning so no prior number is quietly changed.

**D12 — the `R3` block scales by leverage in one field and not in the next.** *Surfaced.* v2
returns `capital_needed_at_thr_unit` (unlevered — the house capital-map rule, which is
defined at one unit and is the right object for the cross-check) **and**
`capital_needed_at_thr_at_leverage`, each labelled, and keeps `capital_needed_at_thr` with
v1's meaning. This removes the trap that in `leverage_curve` the field looked leverage-aware
and was constant.

**D13 — 16 dev sessions carry unexplained intraday data holes.** *Not fixed.* The defect is
in an upstream committed artifact (`runs/SMV2AH_DAY_CIRCUIT_BREAKER/out/intraday_mtm_series.parquet`),
not in the objective; repairing it means rebuilding a committed run output, which is out of
scope and forbidden here. **Surfaced:** v2 returns
`integrity.intraday_short_sessions_vs_modal` (modal bar count, count below 90% of modal,
minimum) with a note that bar counts alone cannot separate a calendar early close from a data
hole, and that fewer observation points **understate** intraday risk — so the direction is
conservative for O1a. It is a count, not a verdict.

**D14 — governance/filing: none of this was pre-registered in a `spec.yaml` and none of it
appears in the registry.** *Not fixed — I am forbidden to touch `spec.yaml`,
`research/registry/`, `CAMPAIGN_STATE.md` or `frontier.yaml`.* `INDEX.md` §6 records the
orchestrator's remediation (registry rows 454–457, each labelled NOT PRE-REGISTERED). **This
repair inherits the same gap:** it is filed as a new document under `runs/W17_C4_COMPLIANCE/`
without its own spec. The orchestrator must register it (row 458+) and must record that
`primary_objective_v2` supersedes `primary_objective` as the O2 scoring module, **before**
O2 runs. Flagging so it is not lost.

**D15 — undisclosed padding bias in the bar-level intraday CDaR.** *Not fixed.* It lives in
`build_session_logpath` / `_intraday_path_stats`, which v2 imports **by reference**
specifically so that v1's machinery-reproduction guarantees (its test cases 3 and 4) carry
over unbroken; forking them to fix a bias the red team measured as small and deflationary
would trade a real guarantee for a small correction. **Surfaced:** v2 returns
`integrity.intraday_padding_fraction` with a note that cum/peak freeze during padding, so each
short session's end-of-day drawdown is repeated inside the **bar-level** CDaR sample, and
that the frequency-matched headline statistic is immune.

---

## G. STATEMENT OF ORDER OF WORK

**Dated 2026-08-09.** Sections A through F above, and the whole of
`src/analytics/primary_objective_v2.py` and `src/analytics/test_primary_objective_v2.py`,
were written to disk **before any object was scored with the repaired module, and no object
has been scored with it.** No candidate's daily or intraday P&L was loaded by this pass at
any point. Every fixture used to develop and test the module is synthetic, generated in-file
from a fixed seed; the only real quantities that entered are (i) the two published `g_ref`
scalars of §D.1 and (ii) the per-method components already published in `O1_OBJECTIVE.md`
§5.2/§6.2, used only in the Appendix, only after §§A–H were written, and only as arithmetic.

Two honest qualifications on the word "blind", stated rather than glossed:

1. **The worked example's components are public.** §C.5 records that I could compute the
   direction of each D1 option before choosing, and that the option I chose is the most
   favourable of the four on the daily barrier. The defence is the argument in §§C.1–C.3 and
   the mandatory `J_worst` companion, not a claim of ignorance.
2. **The red team's D1/D4 entries already state their own sign consequences.** Reading the
   authoritative defect list, as instructed, necessarily exposes them.

No data at or after 2026-08-01 was read (the loader raises on it, and test D10-3 asserts the
raise). No 2006–2021 data was used for any magnitude.

No commits were made. No files were deleted, overwritten or edited except the two new source
files and this new document. `src/analytics/primary_objective.py`,
`src/analytics/test_primary_objective.py`, `O1_OBJECTIVE.md`, every red-team file, every
`spec.yaml` and the registry are untouched; v1's own suite still runs 16/16 PASS.

---

## H. WHAT THE RED TEAM MISSED

Ordered by how much each changes what a reader should believe.

**H.1 — λ double-counts the in-window forfeiture; the red team's own D4 correction overshoots
by 12.5%.** §D.2. §1.5 charges `H_f − H/2 = 9` forfeited years while the absorbing barrier
has already charged `[τ, H]` inside `CE_g`. The correct out-of-window forfeiture is
`H_f − H = 8`. D4 as written proposes λ = 1.54; the doubly-corrected value is **1.368**. The
red team verified the convention error and inherited the horizon error. A corollary the
correction buys: the repaired λ does not depend on the ruin time, so §1.5's untestable
"reached near the middle of the window" assumption is no longer load-bearing.

**H.2 — λ is a function of the evaluation horizon, but v1 shipped it as a constant.**
`horizon_sessions` is a free parameter of the public API. Anyone calling
`primary_objective(..., horizon_sessions=252)` got λ = 1.0 when the same derivation gives
3.077 — a factor of 3 error, silently. v2 derives λ from the horizon, and returns 0 when
`H ≥ H_f`.

**H.3 — λ's calibration is endogenous to the object being scored, which breaks `J` as a
comparable scale.** `g_ref` is the *champion's own* realized growth. If λ were recomputed per
candidate, a higher-growth object would incur a larger ruin penalty and `J` would stop being
a fixed ruler; and at higher leverage `CE_g` rises, so a leverage-dependent λ would feed back
into the leverage curve. v2 pins `g_ref` as a **module constant, calibrated once at the
reference object, reference leverage and reference capital, never recomputed per candidate**,
and says so. This was implicit and undocumented in v1.

**H.4 — a second, independent `min_unit` defect: floating-point floor-to-multiple.** §E.1.
`floor(0.3/0.1) = 2`. The red team's D9 is only the freeze; this one corrupts *every*
granular run whose target lands on a multiple, including runs that never freeze, and it
always errs in the same direction (under-sizing by a full granule).

**H.5 — a third: `min_unit` mode reverses the position at negative equity.** §E.2. v1
continues from −$1.9M to −$20.9M on a synthetic path. Invisible because the log-space outputs
are floored at `ε·C` — which is exactly why v2 returns unclipped `terminal_equity`.

**H.6 — the D9 trap does not merely deflate; it flips the sign.** The red team measured
`CE_g` 0.295 → 0.032 and `P_ruin` 0.324 → 0.004. On a synthetic fixture the *objective* goes
from **J = −0.253 (continuous) to J = +0.008 (granular)**: the broken path can turn a losing
configuration into a winning one, not just a smaller one.

**H.7 — `min_unit` mode's `p_equity_nonpositive` was computed for the wrong model** (the
continuous clip test), and **`min_unit` + `intraday_path` was silently accepted**, pairing a
granular daily leg against a continuous intraday leg — so the O1a "gap" would have conflated
granularity with observation frequency while still passing the session-end reconciliation
check. v2 fixes the first and refuses the second.

**H.8 — the whole leverage curve is one draw.** Every grid point in §5.4 uses the *same*
index matrices (same seed, same `n`, same horizon). Differences across `L` are therefore
paired and reliable, but the **level** of the curve and the **location of the turning point**
carry one draw's worth of Monte-Carlo noise common to every point — they are not replicated
by the grid. D3 notes the noise; it does not note that the grid cannot average it away. v2
documents this on `leverage_curve` and returns `mc_se` per point.

**H.9 — `if min_unit:` (truthiness).** `min_unit = 0` silently disabled granularity *and*
bypassed the `leverage_mode` guard on the following line. v2 uses `is not None` and validates
positivity.

**H.10 — there was no pooled-distribution quantile anywhere.** `growth.per_method` reports
per-method q05/q95 only; there was no dispersion statistic for the object the headline
actually claims to describe. v2 adds `growth.pooled_quantiles` (quantiles of the mixture, not
an average of per-method quantiles — the two are different and only the former belongs to
`F̄`).

---

## APPENDIX — CONSEQUENCE ARITHMETIC (written AFTER §§A–H)

**Everything above this line was written to disk before the arithmetic below was performed.**
This section loads no data and runs no module on any candidate. It is arithmetic on the
per-method components already published in `O1_OBJECTIVE.md` §5.2 (growth, daily ruin) and
§6.2 (intraday ruin), reproduced there and independently re-derived by the red team. It is
included because the task asks whether the corrections move the worked example's sign, and
because §C.5 requires me to show the direction of the rule I chose.

Published components (Product A research curve, C = $100k, L = 1, H = 504, n_boot = 2000,
seed 20260808):

| method | CE_g (absorbing) | P_ruin daily | P_ruin intraday |
|---|---:|---:|---:|
| moving5 | 0.3097 | 0.3185 | 0.4975 |
| moving20 | 0.3468 | 0.1205 | 0.2425 |
| stationary60 | 0.3619 | 0.0335 | 0.2335 |
| **mixture (D1)** | **0.339467** | **0.157500** | **0.324500** |

Note the growth term is unchanged by D1 — v1 already averaged `CE_g`; what D1 changes is the
penalty term and the coherence of their combination.

**Table 1 — the four aggregation options, daily barrier, at each λ.**

| rule | λ = 1.0 (v1) | λ = 1.368 (v2) |
|---|---:|---:|
| (i) mixture / mixture — **CHOSEN** | **+0.1820** | **+0.1241** |
| (0) v1 shipped: mean growth − λ·max ruin | +0.0210 | −0.0962 |
| (ii) term-wise worst | −0.0088 | −0.1259 |
| (ii′) `min_m J_m` (Γ-minimax) | −0.0088 | **−0.1259** |

Per-method `J_m` at λ = 1.368: moving5 **−0.1259**, moving20 **+0.1820**,
stationary60 **+0.3161**.

**Table 2 — daily vs intraday barrier under the repaired objective.**

| | CE_g | P_ruin (mixture) | **J** | `J_worst` |
|---|---:|---:|---:|---:|
| daily close | 0.3395 | 0.1575 | **+0.1241** | −0.1259 |
| intraday barrier | 0.3040 | 0.3245 | **−0.1398** | n/a (per-method intraday growth not published) |

### Answers to the questions the task asks

1. **Does the correction flip the worked example's sign?** **No — not in the direction the
   task's framing anticipated, and I state that plainly.** The task describes D1 as a fix that
   "flips the sign of the objective"; that is true of the red team's *self-consistent
   single-method* reading (option ii′/iii, −0.0088 at λ = 1.0) and of option (ii). It is not
   true of the rule I chose. Under (i) + the λ fix the daily-barrier headline moves
   **+0.0210 → +0.1241**, i.e. **up**. The λ fix alone moves it down by
   `0.367725 × 0.1575 = 0.0579`; the D1 fix alone moves it up by
   `1.0 × (0.3185 − 0.1575) = 0.1610`. The D1 term dominates.
2. **What does flip.** The **model-determined-sign flag fires**: `J = +0.1241` while
   `J_worst = −0.1259`. Under the pre-registered output contract of §C.3, Product A's daily
   J may not be quoted as a single number at all — its sign is set by the choice of
   resampling method. That is the honest replacement for a sign flip, and it is a stronger
   statement than either signed number.
3. **The O1a conclusion survives, and is now the only sign change in the example.** Daily
   **+0.124** vs intraday **−0.140**: watching the same barrier at every 3-minute bar instead
   of only at the close still takes the objective from positive to negative. Under v1 that
   comparison was contaminated by the max/mean asymmetry (both legs used it); under the
   repaired rule both legs use the same mixture, so the daily-vs-intraday gap is now a clean
   paired comparison and the finding is on firmer ground than it was.
4. **Is anything on the "not fixed" list more serious than the red team judged?** Yes, two.
   **D3** — the missing standard error is worse than "no band", because the band that is
   missing (sampling uncertainty about the process) cannot be produced by raising `n_boot` at
   all, and the MC se v2 now returns could be mistaken for it. **D9** — worse than "a live
   trap the test blesses": it flips the sign of `J` on a synthetic fixture (§H.6), and it had
   two further independent defects (§H.4, §H.5) plus a wrong-model bankruptcy figure and a
   silently mis-paired intraday leg (§H.7).

These figures are **not** a score of Product A. They are the arithmetic consequence of the
repaired rules on already-published components, shown so that the repair can be audited
without re-running anything. Scoring any object with `primary_objective_v2` is O2's job and
requires its own pre-registration.

---

## PROVENANCE NOTE (added after the working tree was inspected)

Disclosed because it bears on how this document should be read, and because C7 forbids
quietly tidying it away.

`src/analytics/primary_objective_v2.py` and `src/analytics/test_primary_objective_v2.py`
**already existed as tracked files at HEAD**, added by commit `3e02b2f` ("Wave 18"). I did
not check for them before writing, and my `Write` overwrote both. Verified consequence:
`git diff --numstat HEAD` reports **28 insertions / 0 deletions** for the module and
**64 insertions / 0 deletions** for the tests — the working tree is a strict superset of the
committed versions, so **no committed line was destroyed or altered**. What I added on top of
`3e02b2f` is: the D13 short-session counter, the D15 padding-fraction disclosure, the
D1-consistent `cdar_matched_ratio_mixture`, and the two synthetic intraday test cases
(I1, I2).

Two facts follow that the orchestrator should act on:

1. This repair, or one materially identical to it, was evidently performed and committed in
   Wave 18. **This pre-registration document was never committed** (`git log --all` finds no
   history for it), so the committed module has been carrying the repaired aggregation rule
   and λ calibration **without the written argument that D14/`INDEX.md` §5 require**. That is
   the same governance gap as D14, one level down. Filing this document closes it.
2. Nothing in the repo imports `primary_objective_v2` — `grep` finds it referenced only by
   its own test and by this document. So no downstream result depends on it yet, and the
   purely-additive changes above cannot have invalidated one. O2 remains un-run, which is the
   correct state.

No commits were made by this pass; the working tree is left dirty as instructed.
