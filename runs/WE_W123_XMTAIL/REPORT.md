# WE_W123 — XM session-tail information · REPORT

Preregistered (`spec.yaml`, committed before any code was written).
POST-W121 owner directive §§10, 11, 19, 23, 26, 28, 31, 32, LANE C. **STAGE A ONLY — no veto built,
tested or costed.**

> ## **NO DETECTABLE TAIL-LOSS INFORMATION — and the SYMMETRY is the result.**
> ## On **exactly the same frozen features, the same 336 trades and the same protocol**: tail **WINNERS** are identifiable at **AUC 0.727, p = 0.000**. Tail **LOSERS** are not — **AUC 0.513, p = 0.380.**
> ## **XM's right tail has a causal pre-entry signature. Its left tail does not.**
> ## Per §11's decision rule, fixed before the run: **keep the XM architecture, rely on portfolio diversification plus the owner's catastrophe policy, and do not data-mine a gate.**

## 0. Small N, stated first as the spec required

**336 trades with all ten frozen features finite; 34 in the tail-loss group.** A regularised
logistic on ten features with ~34 positives is at the edge of what cross-validation can adjudicate.

> **A null here means "not detectable at n = 336", NOT "no such information exists."** That
> distinction is preregistered, not a retrofit.

## 1. Stage 1 — per-feature stratification

Tail-loss group: **n = 34, mean −$4,758** against **+$1,181** for the rest.

| feature | tail mean | rest mean | tail median | rest median | perm p |
|---|---|---|---|---|---|
| **on_range_rel** | **1.406** | 1.132 | 1.310 | 1.023 | **0.005** ✱ |
| **gap_pts** | **123.5** | 89.4 | 76.3 | 62.3 | **0.039** ✱ |
| drive_pts | 41.4 | 34.9 | 32.4 | 26.0 | 0.282 |
| nq_sigma | 0.003 | 0.003 | 0.003 | 0.002 | 0.238 |
| morn_vol_rel | 1.059 | 1.007 | 1.057 | 0.990 | 0.215 |
| abs_comp_z | 0.445 | 0.543 | 0.265 | 0.461 | 0.240 |
| divergence | 1.017 | 1.048 | 0.846 | 0.920 | 0.812 |
| is_long · dow · is_ann | — | — | — | — | 0.48 / 0.88 / 0.62 |

## 2. Stage 2 — one logistic, W110b's corrected null (400 re-fitted permutations)

| target | n pos | **real AUC** | null mean | null p95 | **p** | |
|---|---|---|---|---|---|---|
| **TAIL_LOSS worst 10 %** | 34 | **0.513** | 0.490 | 0.611 | **0.380** | not identifiable |
| TAIL_LOSS worst 5 % | 17 | 0.630 | 0.488 | 0.650 | 0.077 | does not clear |
| **TAIL_WINNER top 10 %** | 34 | **0.727** | 0.495 | 0.603 | **0.000** | **IDENTIFIABLE** |

| gate | spec | observed | |
|---|---|---|---|
| **G1** | TAIL_LOSS AUC > permutation-null p95 | 0.513 vs 0.611 | **FAIL** |

**STAGE-A VERDICT: NO DETECTABLE TAIL-LOSS INFORMATION.**

The tail-winner row also serves as a **reproduction check**: 0.727 here against W110b's 0.735 on the
top-20 cut — consistent, on an independently re-run pipeline.

## 3. ⭐ The asymmetry, and one honest qualification of W110

> ### Same ten features. Same 336 trades. Same cross-validation. Same re-fitted permutation null. **Winners 0.727 (p = 0.000). Losers 0.513 (p = 0.380).**

**Why that is mechanically coherent, and where it qualifies W110:**

`on_range_rel` — the overnight range relative to its trailing median — is elevated in **both** tails:
**1.620** for W110's top-20 winners, **1.406** for tail losers, against **~1.13** for the rest. So a
wide overnight range is substantially a **MAGNITUDE** marker: it says the session will be big, not
which way.

> ⚠️ **That partially qualifies W110's headline.** Part of what made tail winners identifiable is a
> magnitude signature shared with tail losers. **It does not overturn it** — W110's own ablation
> showed the announcement flag alone reaches AUC 0.498 and the eight features excluding
> `is_ann`/`on_range_rel` still reach 0.662, so the winner signal is not purely magnitude. But
> "XM's big winners are predictable" must from now on carry: *"and the same state also marks its
> big losers, which the model cannot separate."*

The clean statement that survives both waves:

> **XM's pre-entry state predicts WHEN the session will be large. Among large sessions it separates
> the winners from the field, but it does not separate the losers.** That is exactly the profile of
> a convex, unstopped, directional forecast — which is what W102 established the object is.

## 4. Session-tail contribution — restated as an upper bound only

| | |
|---|---|
| book worst decile | 106 sessions carrying **−$189,670** |
| XM active in them | **77 of 106 = 72.6 %**, against a **32.9 %** overall activation rate |
| XM dollars inside the book's worst decile | **−$231,273** |
| an **oracle** removing XM's own worst-decile trades | would recover **$161,778** |

> **That oracle knows the outcome.** Stage A measured whether it is knowable in advance, and it is
> not. The $161,778 is a ceiling on what any tail-gate could ever be worth, **not** an estimate of
> what one would deliver — and per §31 any such improvement would be classified **RISK POLICY** or
> **CATASTROPHE CONTROL**, never alpha.

## 5. Decision

**NOTHING PROMOTED. NO VETO BUILT. XM's architecture is unchanged.**

1. **§11's fixed-in-advance outcome applies**: no strong causal loss-state information exists, so
   **keep the architecture, rely on portfolio diversification plus the owner's catastrophe-risk
   policy, and do not data-mine a gate.** This was written down before the run precisely so it
   could not be re-litigated afterwards.
2. **XM keeps ACTIVE COMPONENT status.** §10 is explicit that session-tail composition does not
   withdraw it, and W110's weekly loss-diversification result stands untouched (ρ ∣ P1<0 = −0.165 at
   the 5.2nd percentile). **Two horizons, two answers, both true.**
3. **Ordinary stops remain closed** (W102: every level 20–300 points reduces expectancy at fixed
   drawdown). The disaster level remains an owner capital-risk choice that W105 priced and did not
   select. **This wave touched neither.**
4. **What it adds to the record**: the asymmetry itself, and the qualification that `on_range_rel`
   is a magnitude marker present in both tails. Both go into `CURRENT_BASELINE.md`'s XM caveat list,
   because "the big winners are predictable" is now a claim with a rider attached.
5. **The remaining honest option for XM's tail is not information — it is sizing.** A convex
   unstopped forecast whose left tail is unpredictable is a **capital-allocation** question, and
   that belongs to the owner, not to a research wave.
