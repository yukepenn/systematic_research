# RR_W005 — THE SESSION BOX IS WORTH A GREAT DEAL, AND EVERY RELAXATION IS STRICTLY WORSE

| | |
|---|---|
| **run class** | **DIAGNOSTIC** — uniform arms only, **no selection**, no threshold chosen, nothing promoted |
| date | 2026-08-27 |
| code | `run_rr_w005_latch.py` (per-session latch value) · `_b` (the fixed-DD arms) |
| **preregistration** | **none claimed, and none is owed.** This began as scoping for frontier row 1 and returned a decisive answer. The five arms were enumerated in the script **before any of them was run**; no arm was added, removed or re-specified afterwards |
| seal | untouched · `DISCOVERY_CONSUMED` · 2026-05-31 → 07-31 `DIRECTLY_BURNED` |

> ### **Frontier row 1 — "is SELECTIVE box un-latching worth anything?" — is CLOSED.**
> ### The uniform half is answered decisively: **every relaxation of the box adds raw dollars and
> ### destroys the scale-invariant headline**, buying the gain purely with exposure. The selective
> ### half needs identification, and `RR_W002A` / `RR_W004` just measured that as **NULL**.

---

## 1. Why this was asked

`RR_W001` found that **35–64 % of its ex-post abstention oracle was REGENERATION** — trades the frozen
policy takes because the session box stops latching once a bad early decision is removed. That put
"selective box un-latching" on the frontier as a new, distinct object: W98 had tested a *uniformly*
looser box (+$6/wk, paired p = 0.940), but suppressing *specific* early losers so the box survives is
not that experiment.

## 2. The latch's own causal value — ex post, per session

One counterfactual per session, on `RR_W001`'s certified replay: **what if the box had not latched?**

| | |
|---|---:|
| in-window sessions where the box changed the schedule | **247** |
| **total value of latching** | **−$44,806** |
| mean per latched session | −$181.40 |
| **median** per latched session | **+$263.72** |
| sessions where latching **helped** | 131 (53.0 %) |
| sessions where latching **hurt** | 116 (47.0 %) |
| **ex-post ceiling of perfect selective un-latching** | **$283,856** |

Two things stand out. The **mean is negative while the median is positive** — latching usually helps
a little and occasionally hurts a lot. And the ex-post selective ceiling is **$283,856**, against
`P1/PCT`'s entire realised net of $296,911.

**Taken alone, those numbers say the box costs money.** They are also the wrong numbers to decide on.

## 3. The fixed-drawdown metric reverses the sign completely

The campaign's headline is **weekly $ at a fixed $20,245 max drawdown** — scale-invariant, so it
cannot be inflated by leverage. `CLAUDE.md` forbids letting a reduced risk denominator masquerade as
information alpha; **the same rule run backwards forbids reading an exposure-funded raw gain as a
cost saved.**

| arm | trades | raw net | maxDD | **wk $ @ fixed DD** | pos wk | t | ctr-min |
|---|---:|---:|---:|---:|---:|---:|---:|
| **BASELINE** (halt −1,300 / target +1,000) | 2,131 | 296,911 | **29,454** | **972** | 58.6 % | **4.17** | 238,673 |
| NO BOX AT ALL | 2,945 | 341,717 | 57,118 | **577** | 60.0 % | 3.62 | 299,906 |
| no halt, keep target | 2,599 | 319,903 | 48,330 | **638** | 61.9 % | 3.84 | 270,452 |
| keep halt, no target | 2,432 | 323,958 | 38,242 | **817** | 56.7 % | 4.05 | 265,629 |
| box × 2 (uniformly looser) | 2,643 | 301,879 | 44,457 | **655** | 59.5 % | 3.76 | 275,581 |

| vs baseline | raw | maxDD | **wk @ fixed DD** | exposure |
|---|---:|---:|---:|---:|
| NO BOX AT ALL | **+44,806** | **+27,664** | **−395 (−40.7 %)** | **+25.7 %** |
| no halt, keep target | +22,992 | +18,876 | −334 (−34.3 %) | +13.3 % |
| keep halt, no target | +27,048 | +8,787 | −155 (−16.0 %) | +11.3 % |
| box × 2 (uniformly looser) | +4,968 | +15,003 | −317 (−32.6 %) | +15.5 % |

> ### **Every single relaxation is worse at fixed drawdown — by 16 % to 41 % — and every one raises
> ### exposure, by 11 % to 26 %.** The −$44,806 "cost of latching" is not a cost. It is **drawdown
> ### control being paid for**, and at the metric this campaign actually decides on, the box is
> ### buying far more than it costs.

`t` falls monotonically too: **4.17 → 4.05 → 3.84 → 3.76 → 3.62**.

## 4. What this closes

**Frontier row 1 is closed.** Its uniform half is answered — there is nothing to harvest by relaxing
the box, in any of the four obvious directions. Its selective half requires knowing *which* sessions
to un-latch, and that is an identification problem `RR_W002A` and `RR_W004` have just measured
directly and found **NULL**: 18 causally-verified features plus 6 HTF features, against a refitted
dependence-preserving null, with a known-null family out-scoring every real arm.

**It also explains `RR_W001`'s regeneration component rather than leaving it open.** Un-latching adds
raw dollars *by adding exposure*. `RR_W001`'s f-curve reported raw net and max drawdown in separate
columns; this run supplies the exchange rate between them, and it is unfavourable.

> ⚠️ **No contradiction with `RR_W001`.** Its abstention oracle *reduced* max drawdown ($29,454 →
> $7,040 at f = 0.20) while raising net, because it un-latched **selectively and with foreknowledge**.
> The arms here are **uniform**. The gap between the two is exactly the value of identification —
> which is the thing now measured as null.

**It also confirms W98 rather than contradicting it.** W98's uniformly looser box was worth +$6/week
at p = 0.940 — indistinguishable from nothing. The `box × 2` arm here is the same experiment at the
fixed-DD metric, and it is **−32.6 %**. Both say the same thing: **the box's parameters are not a
free lever.**

## 5. Constraint this adds

> **The mirror of the leverage rule.** `CLAUDE.md` says never let a reduced risk denominator
> masquerade as information alpha. **The reverse is equally binding: never read an exposure-funded
> raw-dollar gain as a cost avoided.** Here a −$44,806 "cost of latching" and a $283,856 ex-post
> ceiling both evaporate the moment the scale-invariant metric is applied. **Any future finding
> expressed in raw dollars must be re-expressed at fixed drawdown before it is believed.**

## 6. Continuation

| | |
|---|---|
| **outcome** | **row 1 CLOSED.** The box is worth keeping; relaxation is strictly worse |
| **`P1/PCT`** | **unchanged.** The box is not modified. Nothing is promoted or demoted |
| **next** | frontier row 2 — book coverage, **LOW**, n = 32 sessions |
| **the only high-ceiling rows left** | order flow, options, a wider event calendar — **all owner-gated acquisition** |
