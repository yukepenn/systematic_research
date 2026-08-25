# VF_ARCHITECTURE_REOPEN — the anchored-VWAP lifecycle question, reopened

**Date:** 2026-08-24. **Mandate:** owner MASTER DIRECTIVE v4.0 (adjudication, adopted here
without argument). **Claim IDs:** V-023, V-024, V-025, V-026, V-027, V-028 in
`../CLAIM_REGISTRY_2026.csv`. **Supersedes:** the lifecycle wording in
`VF_CLEANROOM_SPEC.md` ("VF-ANCHOR … Leading architecture (incumbent)"),
`VF_CORE_PARITY_REPORT.md` ("VF-ANCHOR remains the incumbent"),
`OWNER_REPORT_RECONCILIATION.md` (row 2, "CONFIRMED-incumbent"),
`../CONVERGENCE_PASS_ANSWERS_20260824.md` answer **I** ("ACTIVE ANCHORS (incumbent,
strong)"), and `../vendor_forensics/PURCHASE_GATE.md` ("CLOUD GEOMETRY: solved-to-class").
Those documents are **not** edited by this pass; this file is the controlling record.

**Status vocabulary** — FACT / REPRODUCED / INFERENCE / UNKNOWN / FALSIFIED. Exactly one
per claim. Observation and interpretation are never combined in one sentence. Backtest
P&L is **never** admissible as a selector of a vendor semantic (see §2.7).

---

## 0. What changed, and what did not

**The reclassification (adopted, mandatory).**
The VWAP-layer lifecycle class is **UNKNOWN** (V-024). The prior status —
"CONFIRMED / solved-to-class, ACTIVE-ANCHOR incumbent (strong)" — is **WITHDRAWN**.

**Why it was reopened.** ninZa's public product pages describe the layers in
*segmented* language. Per V-023 (FACT, as quoted in MASTER DIRECTIVE v4.0): with
Anchor Period = 30 and Amount = 3 the three layers are described as covering
"the most recent 30 minutes", "the previous 30 minutes" and "an earlier 30-minute
period", and another official page states that the tool "divides the market into smaller
time segments and recalculates VWAP for each segment".

> **PROVENANCE GAP (must travel with every citation of V-023).** Our repository archives
> the Trader Manual PDF (SHA-256 `d34b50da…`), the `softwareChangeLog` JSON array and the
> 2026-01-14 Wayback capture of the marketing microsite — but **not** this verbatim
> product-page string. We hold it only as quoted inside the owner directive. Re-fetch and
> archive `https://ninza.co/product/vwap-flux` and `https://vwap.nt8.ninza.co/` on the
> next authorized browsing pass. Until then the string is second-hand vendor language,
> and it is *marketing prose*, which this campaign has always refused to treat as
> algorithmic proof (`VWAP_FLUX_VERSION_TIMELINE.md` §0 rule).

**What did NOT change.**
- Every measurement in `VF_CORE_PARITY_REPORT.md` stands as REPRODUCED. Nothing is
  deleted. What changes is what those measurements are *evidence of* (§2.6).
- The panel identification (EV-019, V-001/V-002/V-003) is untouched: 13/13 label+order
  match, trader values `BidAskPrice_RealVolume / 60 / 5 / 20 / EMA / 95 / 75 / 50 / 25 /
  5 / 3 / 10 / 5`, frozen 2026-02-13 → 2026-08-14.
- The rail-formula question is **largely orthogonal** to the lifecycle question, and the
  min-max rejection survives the reopening on a lifecycle-invariant algebraic argument
  newly stated in §3.4. The *numbers* attached to it do not survive unqualified.

---

## 1. The live readings, stated precisely enough to implement

Notation. `P` = Anchor Period in minutes (trader: 60). `A` = VWAP Amount (trader: 5).
Bars indexed `b` with time `t_b`, price input `p_b` (close or hlc3 — V-029 UNKNOWN), and
volume `v_b`. Clock-aligned anchor instants `τ_k` are the epoch-aligned multiples of `P`
(the convention `vf_core.vf_levels` uses: `period_id = epoch_seconds // (P*60)`).

### 1.1 VF-L1 — ACTIVE ANCHORS (legacy name: VF-ANCHOR)

A rolling population of anchored VWAPs, **all still accumulating**.

```
layer_k(b) = Σ_{j : τ_k ≤ t_j ≤ t_b} p_j·v_j  /  Σ_{j : τ_k ≤ t_j ≤ t_b} v_j
```

- At each `τ_k` a **new accumulator is born**; the pool retains the `A` most recent
  anchors; the oldest is dropped (or re-initialised in place).
- **Every retained layer updates on every bar.** Layer spans are *unequal and growing*:
  the newest covers `[0, P)` elapsed, the oldest covers `[(A−1)·P, A·P)` elapsed. The
  oldest layer is therefore the most heavily averaged and sits closest to the long-run
  mean; the newest hugs price.
- Population at bar `b` = `{layer_1(b) … layer_A(b)}`, size `A`, then sorted → rails.

**Sub-variants (implementation-distinguishable, currently undiscriminated):**
| id | difference | status |
|---|---|---|
| L1a | cyclic in-place slot reset with a counter that wraps over `A+1` values, so once per rotation **no** slot resets and the pool transiently spans `A+1` periods (the LuxAlgo `#1` behaviour recorded in `PUBLIC_ANALOGUE_MAP.md`) | UNKNOWN |
| L1b | strict `A`-slot rotation: birth a layer, drop the oldest, always exactly `A` live (**what `vf_core.py` implements**: `layers.append(...)`, `if len(layers) > amount: layers.pop(0)`, then all layers accumulate) | UNKNOWN |
| L1c | pool cleared at the NQ session open (18:00 ET) vs rolling-only across the session boundary | UNKNOWN — no public analogue clears; NinjaTrader natively sees a session break, Pine does not |

### 1.2 VF-L2 — SEGMENT / BLOCK

Each layer is the VWAP of **one bounded time segment**; older segments are **frozen**
once their window ends.

```
segment_k  = the clock-aligned window [τ_k, τ_k + P)
layer_k    = Σ_{j ∈ segment_k} p_j·v_j / Σ_{j ∈ segment_k} v_j     (fixed once segment_k closes)
```

- Layer spans are **equal and bounded** (`P` minutes each). No layer ever sees data
  outside its own segment.
- On a given bar **at most one layer moves** — the current partial segment, and only
  under composition L2b below.
- **Amount-composition sub-readings** (both were built in `OTR_VF1_FLUX_ARCH`):

| id | population of size `A` | note | status |
|---|---|---|---|
| L2a | the `A` most recent **completed** segments; the current partial segment is excluded from the rails | VF1 arm `L_C` | UNKNOWN |
| L2b | current partial segment + `(A−1)` completed segments | VF1 arm `L_E`; **what `vf_core.py lifecycle="block"` implements** (`layers[-1]` only accumulates) | UNKNOWN |

- Predicted morphology (analytic, not measured): the outer rails are **piecewise-constant
  horizontal segments** for `P`-minute stretches, because under L2a *all* and under L2b
  `A−1` of the population members are constants for the whole period; the sorted extremes
  are almost always drawn from the frozen members. This is the "frozen-rail staircase"
  named as V-024's falsifier.

### 1.3 VF-L3 — SLIDING WINDOW (the third reading the wording admits)

Neither anchored-cumulative nor frozen-block: each layer is a VWAP over a **trailing
window of fixed duration**, recomputed every bar, with edges that move continuously.

```
L3a  (disjoint trailing windows)
layer_k(b) = VWAP over ( t_b − k·P , t_b − (k−1)·P ]        k = 1 … A

L3b  (nested trailing windows / "rolling VWAP" family)
layer_k(b) = VWAP over ( t_b − k·P , t_b ]                  k = 1 … A
```

- **All `A` layers move every bar** (like L1) but each has a **bounded, constant span**
  (like L2). Old bars drop out of the sums as they age past the window.
- **No clock-locked boundaries at all** ⇒ **no jumps** at :00, :30, :60. This is the
  signature that separates L3 from both L1 and L2.
- L3a gives disjoint, equal-span layers; L3b gives nested, monotonically-increasing-span
  layers (population is smoother and more compressed than L3a).
- Public precedent exists for the *family* but not for the *construction*: TradingView's
  built-in `Rolling VWAP` (MPL-2.0, `PUBLIC_ANALOGUE_MAP.md` #2) is a single
  sliding-millisecond-window VWAP with σ-bands — **no population, no percentile rails**.
  No public source computes percentile rails over a sliding-window VWAP population.

**Can the public wording distinguish L3?** — **Partly, and against it.**

| wording | status | reads on L3 |
|---|---|---|
| Manual §2.2 verbatim: *"This parameter defines the time cycle, in minutes, used to recalculate the VWAP … when Anchor Period = 30, the indicator will recalculate the VWAP bands every 30 minutes."* | FACT (text-extracted from the archived PDF, this pass) | **Disfavours L3.** L3 recalculates every bar, not "every 30 minutes". A 30-minute *cadence* is asserted. |
| Product page: *"divides the market into smaller time segments and recalculates VWAP for each segment"* (V-023) | FACT, with the §0 provenance gap | **Admits L3.** "Bounded segment, recalculated" fits a sliding segment as readily as a frozen one. |
| Product page: *"the most recent 30 minutes / the previous 30 minutes / an earlier 30-minute period"* (V-023) | FACT, with the §0 provenance gap | **Admits L3, and fits it better than L2.** Under L3 the newest layer covers exactly 30 minutes at every instant; under L2 it covers 0–30 minutes depending on clock phase. |
| The parameter is named **"Anchor Period"** and the objects are named **"VWAP layers"** | FACT (EV-019, manual §2.2/§2.3) | **Disfavours L3.** "Anchor" is a term of art for cumulative-from-a-fixed-point. L3 has no anchor. |

**Net:** the public wording **cannot** cleanly separate L3 from L2 — one page's phrasing
(exact-30-minute spans) actually fits L3 *better* than L2 — but the manual's assertion of
a 30-minute recalculation cadence, and the word "Anchor" itself, both cut against L3. L3
is therefore recorded as **live but weakest of the three**, and it is cheap to kill: any
readable rail jump at a clock boundary falsifies it outright.

### 1.4 VF-L4 — BAND-REFRESH CADENCE (a fourth reading, live but trivially falsifiable)

Manual §2.2 says "**recalculate the VWAP bands** every 30 minutes". Read literally as a
statement about the **bands** rather than about the layers, this admits: *whatever the
layer rule is, the five plotted rails are recomputed only at each `P` boundary and held
constant in between* — i.e. **all five rails are horizontal staircases**, with no
intra-period movement of any kind.

- Status: **UNKNOWN**, low prior.
- Falsifier: **any single chart frame showing any rail moving between boundaries.**
- V-027 (INFERENCE) already reports "smooth drift between hourly steps" on the manual's
  own PNGs, which if converted from eyeball to pixel-metric would close L4 for the cost
  of one image measurement. It is recorded here because a reading that no document
  excludes must be written down, not because it is likely.

### 1.5 Reading-by-observable summary (analytic predictions, not measurements)

| observable, per in-period bar | L1 ACTIVE | L2 SEGMENT | L3 SLIDING | L4 BAND-REFRESH |
|---|---|---|---|---|
| number of rails that move | all 5 | ≤1 (L2b) / 0 (L2a) | all 5 | 0 |
| rail path between boundaries | smooth drift | flat, then step | smooth drift | flat |
| jump at the clock boundary | moderate (one member swapped) | large (whole population re-sorted around a new frozen value) | **none** | large |
| layer span | unequal, growing | equal, bounded | equal (L3a) / nested (L3b), bounded | n/a |
| cloud width scale | compressed toward the long-run mean | ≈ price range over `A·P` minutes | ≈ price range over `A·P` minutes | n/a |
| behaviour at a data gap / reload | pool survives or re-anchors | frozen values survive | window re-fills | n/a |

---

## 2. Evidence, for and against, with status labels

### 2.1 Evidence bearing on **L1 ACTIVE**

| id | evidence | status | direction | limitation |
|---|---|---|---|---|
| V-025 | Our clean-room constructor gives mean cloud width (Max−Min) **47.0 pts under ANCHOR vs 106.0 pts under BLOCK** (NQ 1-min 2026-03-16..27, P=60, A=5, levels 95/75/50/25/5, close×volume) | REPRODUCED | FOR L1 | **OUR model vs OUR model** — see §2.6 |
| V-026 | Same measurement: **rails moving per in-period bar 5.00 (ANCHOR) vs 1.34 (BLOCK)**; **mean jump at period boundary 11.1 pts vs 21.2 pts** | REPRODUCED | FOR L1 | same — §2.6 |
| V-027 | The manual's own embedded chart PNGs (pp.3/8, NQ MAR26 1-min and 3-min, Anchor 60) show **hourly rail steps with smooth drift between them** | INFERENCE | FOR L1 (and against L2, L4) | Eyeball reading of low-resolution PNGs. L2 *also* produces hourly steps; "smooth drift between them" is the discriminating half and it has never been pixel-measured. **This is the single most important upgradeable item in the file.** |
| — | The only public construction that computes **percentile rails over a VWAP population** (LuxAlgo *Rolling VWAP Channel*, CC BY-NC-SA, full source recovered) does it over **live, still-updating anchored VWAPs**; its default rails are 100/70/50/30/0 and its parameter vocabulary is "Anchor Period / VWAP Source / VWAP Amount" | FACT (source read) | FOR L1 | Convention coincidence only. **No copying claim in either direction.** Published 2025-06-11 vs VWAP Flux 2026-01-09 — the ordering permits independent convergence and proves nothing. |
| — | The public analogue that **does** freeze completed blocks (LuxAlgo *VWAP Periodic Close*, `PUBLIC_ANALOGUE_MAP.md` #4) plots the frozen values as **discrete horizontal S/R levels** and computes **no rails over them** | FACT (source read) | FOR L1 (weak) | Absence of a public precedent for "percentile rails over frozen blocks" is an argument from the state of the art, not about ninZa. |
| — | The parameter is literally named **"Anchor Period (Minutes)"**; the objects are "VWAP **layers**" (manual §2.2/§2.3) | FACT | FOR L1 | Naming is chosen by a marketing-facing vendor; "anchor" describes when a cycle starts under L2 just as well. |

### 2.2 Evidence bearing on **L2 SEGMENT / BLOCK**

| id | evidence | status | direction | limitation |
|---|---|---|---|---|
| V-023 | Product page: layers described as "**the most recent 30 minutes**", "**the previous 30 minutes**", "**an earlier 30-minute period**" (at Anchor 30, Amount 3) | FACT | **FOR L2 (and L3)** | §0 provenance gap; marketing prose. But note the force of it: under L1 the *second* layer spans 30–60 minutes of data cumulatively **to the present bar**, which the phrase "the previous 30 minutes" describes badly, while under L2/L3 it describes it exactly. |
| V-023 | Product page: the tool "**divides the market into smaller time segments and recalculates VWAP for each segment**" | FACT | **FOR L2 (and L3)** | §0 provenance gap; marketing prose. "Divides … into segments" is a partition, which is L2's defining property and not L1's (L1's layers overlap by construction). |
| — | Manual §2.2 verbatim: "defines the **time cycle**, in minutes, used to **recalculate** the VWAP … the indicator will **recalculate the VWAP bands every 30 minutes**" | FACT (text-extracted, this pass) | **FOR L2** (also admits L1 and L4; disfavours L3) | "Recalculate" reads more naturally as recompute-from-scratch than as re-anchor-a-new-accumulator-alongside-the-old-ones — but only *more naturally*, not decisively. |
| — | Manual §2.3 verbatim: "Defines the number of **recent VWAP layers** used to construct the VWAP bands … if VWAP Amount = 5, the indicator will use the **five most recent VWAP layers**" | FACT (text-extracted, this pass) | NEUTRAL | Compatible with all of L1/L2/L3. Does not say whether a "layer" keeps updating. |
| — | **Both** vendor texts we hold (manual §2.2 and the product page) read more naturally as L2 than as L1, and they are independent of each other | INFERENCE | FOR L2 | Two readings of the same vendor's prose are not two independent observations of the vendor's code; and the second one is not archived. |
| — | The vendor's own documented **suggested presets** run Anchor 20 / Amount 7 (1-min) and Anchor 3 / Amount 5 (ninZaRenko 12/4) — an L1 pool at Anchor 3 spans only 15 minutes of cumulative history | FACT (manual pp.13-15) | NEUTRAL | Recorded to prevent an argument from "L1 clouds would be absurdly wide at large Anchor". It cuts neither way at the presets' scales. |

### 2.3 Evidence bearing on **L3 SLIDING**

Covered in §1.3. Summary: the product-page 30-minute-span phrasing **admits and mildly
favours** L3 over L2; the manual's 30-minute recalculation cadence and the word "Anchor"
**disfavour** it; **no public analogue** computes percentile rails over a sliding-window
population. Status **UNKNOWN, weakest of the three, cheapest to kill.**

### 2.4 Evidence that bears on **none** of them (recorded so it is not misused)

| id | evidence | status | why it is silent on lifecycle |
|---|---|---|---|
| V-028 | The 164-image corpus contains **zero author platform-chart imagery** (IMG-16 sweep of all 90 social frames + cross-check of all 164 audit records; the only chart anywhere is a commenter's TradingView MNQ shot, OTRIMG-0130, with no time axis) | FACT | There is no trader-side cloud to look at. Corpus label-surface exhaustion is proven. Every "(a) free from the corpus" cell in §4 is therefore **NO**. |
| V-030 | Anchor-age concordance mean −0.17 ⇒ the sorted population is not age-ordered | REPRODUCED | Computed **under L1 only**; it is a diagnostic about our own construction, excluded from the reconstruction per directive §18/§42. Under L2 the age-order structure is different and unmeasured. |
| V-011 / EV-039 | Manual §2.1: in `BidAskPrice_RealVolume` with Tick Replay **disabled**, "the indicator functions only on real-time data and there are **no calculations on historical data**" | FACT | Bears on the **engine** question (V-013/V-014), not on the layer lifecycle. Do not import it here. |
| V-021 | Absence of VWAP Flux artifacts on the *researcher's* machine | **FALSIFIED** (invalid inference, owner-adjudicated) | Must not be cited in any direction. |

### 2.5 Confounding in our own runs (FACT about our artifacts)

`runs/OTR_VF1_FLUX_ARCH/` implemented L2 (arms `L_C` = L2a, `L_E` = L2b) and
`runs/OTR_VF4_ANCHORED_LAYERS/` implemented L1 (`ANC`). **They are not a lifecycle A/B.**
Between the two runs the trend construction, the signal family, the exit family, the
protective stop and the level formula **all** change simultaneously:

| | VF1 | VF4 |
|---|---|---|
| lifecycle | L2a / L2b | L1 |
| levels | min-max range interpolation | min-max primary + a **QLEV** (quantile) disclosure arm |
| trend | `T_A` (EMA20 vs Median + close vs Median) / `T_B` (cloud-break hysteresis) | cloud-break hysteresis only |
| signals | cross-from-above-Highest into band | `SIG1` band entry / `SIG2` low-touch + close ≥ Median |
| exits | `XA` flip / `XB` re-break / `XC` LossLimit-2500 | `X_FLIP` / `X_MED` / `X_OPP` |
| stop | none (except `XC`) | intrabar 130-pt |
| best D | 5.809 (`L_C\|T_B\|XB`) | 3.398 (`ANC\|SIG2\|X_MED\|stop130\|QLEV`) |

**FACT: no clean lifecycle contrast has ever been run in a run directory.** The only
clean, everything-else-held-fixed lifecycle contrast in the campaign is the `vf_core`
morphology measurement (V-025/V-026), which is a geometry measurement and not a
behavioural one.

### 2.6 The limitation on our morphology evidence — stated explicitly, as required

V-025 and V-026 are **REPRODUCED** and are retained in full. But their endpoints are:

> `vf_core.vf_levels(..., lifecycle="anchor")` **↔** `vf_core.vf_levels(..., lifecycle="block")`,
> both evaluated on **our** NQ 1-minute substrate.

That is **our model's morphology versus our model's morphology.** It is not
ORIGINAL_PARITY, it is not vendor ground truth, and **the trader's own rail series has
never been observed by anyone in this campaign** (V-103: no IMPLEMENTATION_PARITY exists
for any VWAP-Flux-family object; the VF clean room is Python-only, with no NinjaScript
port and no NT8 cross-check). What V-025/V-026 legitimately establish is:

1. **The two lifecycles are sharply separable in principle** — a factor ~2.3 in cloud
   width, 5.00 vs 1.34 movers per bar, 11.1 vs 21.2 pt boundary jumps. A discriminator
   exists and is large.
2. **Any observation of a real VWAP Flux cloud would settle it quickly**, because the
   separation is far above pixel noise on a chart.

What they do **not** establish is which one ninZa shipped. Reading them as a lifecycle
decision was the error that directive v4.0 corrects. The correct formulation, used
everywhere below: *these are measurements of the discriminator's power, not measurements
of the answer.*

### 2.7 Inadmissible evidence (binding)

- **Backtest P&L / §40 distance may not select a lifecycle.** VF4's best cell (D=3.398)
  outscoring VF1's best (D=5.809) is **not** evidence for L1. It is confounded six ways
  (§2.5), and even unconfounded it would be P&L selecting a vendor semantic, which this
  campaign forbids. Recorded so that the D-score gap is never quietly re-imported.
- **Absence of a vendor artifact on our machine** (V-021, FALSIFIED) may not be cited.
- **Marketing prose is not algorithmic proof** — this binds the L2 argument from V-023
  exactly as hard as it binds any L1 marketing claim.

---

## 3. Rail formulas, per lifecycle

The five Level percentages map a sorted population of `A` layer values to five plotted
rails. Manual §2.6–§2.10 verbatim: Level Max "defines the **highest threshold within the
VWAP bands**"; Level Median "defines the **threshold for the Fair Value plot within the
VWAP bands**"; Level Min "defines the **lowest threshold within the VWAP bands**"
(V-031, FACT). The wording alone mildly favours a min-max reading and is not decisive.

### 3.1 The candidate formulas (as implemented in `vf_core.rails_from_population`)

Let `v[1] ≤ … ≤ v[n]` be the sorted population, `q = pct/100`.

| id | formula | `n=5`, trader pcts 95/75/50/25/5 |
|---|---|---|
| **F1 percentile-linear (type 7 / inclusive)** | `h = q·(n−1)`; interpolate between `v[⌊h⌋+1]` and `v[⌊h⌋+2]` | 95 → 0.8 of the way from `v[4]` to `v[5]`; 75 → `v[4]`; 50 → `v[3]`; 25 → `v[2]`; 5 → 0.2 above `v[1]` |
| **F1x percentile-linear (exclusive / NIST)** | rank `= q·(n+1)` | differs from F1 materially at 95/5 for `n=5`; **not implemented in `vf_core`** — a genuine gap |
| **F2 nearest-rank** | `k = ⌈q·n⌉`; return `v[k]` | 95 → `v[5]`; 75 → `v[4]`; 50 → `v[3]`; 25 → `v[2]`; 5 → `v[1]` |
| **F3 min-max interpolation** | `v[1] + q·(v[n] − v[1])` | a fixed fractional position in the span, independent of the interior values |

V-032 (REPRODUCED): on the adversarial population `[100,101,102,103,140]`, the 75% level
evaluates to **103.0** (F1), **103** (F2) and **130.0** (F3) — the families are sharply
separable in principle.

**Note (FACT about our code):** with `n=5` and the trader's percentages, **F1 and F2 are
identical at 75/50/25 and differ only at 95/5.** The inner rails cannot discriminate them
at all. Any test must be anchored on the outer rails.

### 3.2 What is already constrained — and what the reopening does to it

| question | status | constrained by | effect of the lifecycle reopening |
|---|---|---|---|
| F3 min-max vs the percentile family (F1/F2) | **INFERENCE: min-max disfavoured at the VENDOR level** (V-035, downgraded from "RESOLVED") | V-034 (EV-040): on the manual's own chart PNGs the Fair Value plot **hugs the price-side cloud edge through sustained trends and never sits at the stretched-range midpoint** | **Survives** — see §3.4, the argument is lifecycle-invariant. The *magnitudes* attached to it do not (§3.3). |
| F1 vs F2 (linear vs nearest-rank) | **UNKNOWN** (V-037) | Separable only on the 95/5 rails; never tested against any observed series | **Amplified** — see §3.3 |
| F1 vs F1x (interpolation variant) | **UNKNOWN**, and **not even implemented** | `PUBLIC_ANALOGUE_MAP.md`: Pine's official docs do not pin the variant; at `n=5` the variants differ materially at p=95/5 | Unchanged; flagged here as a build gap |
| Whether the **trader's** build uses the vendor's formula at all | **UNKNOWN** (V-036), and depends entirely on V-014 (engine UNKNOWN) and V-102 (the untested transfer assumption) | — | Unchanged and still load-bearing: every OTR-VF-CAND1 result was computed with F1 as an **assumption**, not a finding |

### 3.3 What the lifecycle reopening does to the rail evidence — the honest accounting

- **V-033 is anchor-conditional.** "min-max forces FairValue to sit exactly at the cloud
  midspan (Δ = 0.000 by construction) while the percentile FairValue deviates from
  midspan by **mean 8.9 pts**" was measured under L1 on our substrate. The `Δ = 0.000`
  half is algebraic and lifecycle-free; the **8.9 pts** half is not. Under L2 the
  population is ~2.3× more dispersed (V-025), so the percentile-vs-midspan deviation
  would be **larger in absolute points** — INFERENCE from the algebra, magnitude
  **UNKNOWN** because it has never been measured under L2. *Do not quote 8.9 pts as if it
  were lifecycle-free.*
- **F1-vs-F2 separation scales with population spread.** The gap `v[5] − v[4]` (which is
  all that F1 and F2 disagree about at p=95) is larger in a more dispersed population.
  The `≈1.7 pts` outer-rail difference recorded in `VF_CORE_PARITY_REPORT.md` is an
  **L1-conditional** figure; under L2 the F1/F2 discriminator is **stronger**, magnitude
  UNKNOWN. INFERENCE.
- **Which formula was used in every VF run so far:** `percentile_linear` (F1) in R3, R7,
  R7b, R8 — an assumption. VF1 used F3 (min-max range interpolation) throughout, which is
  a second, independent reason VF1's D-scores cannot be read as evidence about L2.

### 3.4 New this pass: the min-max rejection is **lifecycle-invariant** (INFERENCE)

For **any** population and **any** lifecycle, F3 places each rail at a **fixed fractional
position** of the span between the population extremes. Therefore the Fair Value plot sits
at the constant fraction

```
f = (medianPct − minPct) / (maxPct − minPct)
```

of the distance between the **plotted Min rail and the plotted Max rail**, *at every bar,
forever*. With the trader's 95/75/50/25/5 that is `f = 0.5` exactly; with the manual's
5-minute preset 100/70/50/30/0 it is also `0.5`; with the 1-minute preset 80/60/50/40/10
it is `0.571`. In every case it is a **constant**.

Under the percentile family (F1/F2) that fraction **varies with population skew** and
migrates toward whichever edge the trend is pushing.

V-034 reports exactly the varying, edge-hugging behaviour on the vendor's own charts.
That observation therefore rejects F3 **without any assumption about the lifecycle**, and
without needing to know which preset the chart used. **The lifecycle reopening does not
reopen the min-max question.**

Two conditions this argument does depend on, both live:
1. **V-038 (INFERENCE)** — that the Fair Value plot *is* the Median rail of the *same*
   population as the Max/Min rails. Live competitors listed in the registry: a
   volume-weighted centre of the layer set, a recency-weighted centre, or a combined
   5-segment VWAP. If FVP is a separately-computed object, the argument does not apply.
2. **V-034 is an eyeball INFERENCE**, not a pixel measurement (§4, row R2).

---

## 4. Discriminator table

Obtainability legend:
**(a)** free from the existing 164-image corpus · **(b)** free from vendor public material ·
**(c)** requires a licensed copy of the indicator.

| # | pair to separate | concrete observable | predicted split | (a) corpus | (b) vendor public | (c) licensed |
|---|---|---|---|---|---|---|
| **R1** | **L1 vs L2** | On a vendor chart at Anchor `P`: is any of the five rails **exactly horizontal for a full `P`-minute stretch**? Pixel-metric extraction of the rail polylines from the manual's embedded PNGs (pp.3/8, NQ MAR26 1-min & 3-min, Anchor 60, archived PDF SHA-256 `d34b50da…`). | L1: **0 flat bars** (all 5 rails move every bar). L2b: **4 of 5 rails flat** for the whole hour. L2a: **all 5 flat**. | **NO** — V-028 FACT: zero author chart imagery; corpus exhaustion proven | **YES — cheapest and highest-value test in the file.** Assets already in-repo; converts V-027 from eyeball INFERENCE to a measurement | YES (decisive, but unnecessary for this pair) |
| **R2** | **percentile (F1/F2) vs min-max (F3)** | On the same PNGs: measure `(FVP − MinRail) / (MaxRail − MinRail)` bar by bar. | F3: a **constant** (§3.4). F1/F2: **varies**, migrating toward the price-side edge in trends. | NO (V-028) | **YES** — same extraction pass as R1; upgrades V-034/V-035 from eyeball to metric | YES |
| **R3** | **L1/L2 vs L3 SLIDING** | Is there **any discontinuity** in the outer rails at the clock boundaries? EV-040 records readable chart times (18:20 / 19:00 / 20:10 down-arrows; 15:40 / 16:20 / 22:00 up-arrows), so boundary instants are locatable on the frame. | L3: **no jump at any boundary**. L1: moderate jump. L2: large jump. | NO (V-028) | **YES** — falls out of the same R1 extraction | YES |
| **R4** | **L4 BAND-REFRESH vs everything** | Does **any** rail move between two clock boundaries? | L4: **no**. All others: yes. | NO (V-028) | **YES** — free by-product of R1 | YES |
| **R5** | **L1 vs L2/L3 (scale test)** | Cloud width `MaxRail − MinRail` in points, compared against the **price range over the preceding `A·P` minutes on the same frame**. | L2/L3: width ≈ that range. L1: **materially narrower** (cumulative averaging pulls old layers toward the long-run mean). | NO (V-028) | **PARTIAL** — needs the chart's `VWAP Amount`, which is **UNKNOWN** from the PNGs (the plots are the 5 rails, not the layers). Yields a bound, not a decision | YES |
| **R6** | **L1a vs L1b** (rotation quirk) | Does the pool transiently span `A+1` periods once per rotation (a boundary at which **no** layer resets)? | L1a: one boundary in `A+1` shows an anomalously small jump. L1b: uniform jumps. | NO (V-028) | **NO** — far below the resolution of a static PNG | **YES only** |
| **R7** | **L2a vs L2b** (Amount composition) | Is the **newest** rail-population member a partial (in-progress) VWAP or the last completed segment? Equivalent: at a boundary, does the newest member jump to a *fixed* value or start from the boundary bar's price? | L2b: one member moves intra-period. L2a: none. | NO (V-028) | **YES**, conditional on R1 first showing L2 is the class at all | YES |
| **R8** | **L1c** (session reset of the pool) | Cloud behaviour in the **first hour after the 18:00 ET session open**: does the population collapse onto few layers (visibly narrow/degenerate cloud), or carry overnight layers across? | reset: degenerate cloud. rolling-only: continuous. | NO (V-028) | **NO** — neither manual PNG spans a session open (the readable arrow times sit inside a single session) | **YES only** |
| **R9** | **F1 vs F2** (linear vs nearest-rank) | Do the 95/5 rails **coincide exactly with population members**, or sit strictly inside the layer envelope? Only the outer rails carry information (§3.1). | F2: rails land on actual layer values. F1: strictly interior. | NO (V-028) | **NO** — requires knowing the individual layer values, which are not plotted | **YES only** |
| **R10** | **F1 vs F1x** (interpolation variant) | Same as R9, at higher precision. | sub-point differences at `n=5` | NO | NO | **YES only** |
| **R11** | **all of the above, at the TRADER level** (V-036, V-102) | `Signal_Trade` timestamps for any single day from his build, or a per-day 2026 Analyzer table of the OTRIMG-0003 kind | any | **NO** — V-104 FACT: neither exists in the fixed corpus, exhaustion proven | NO | **NO** — a licensed copy answers **vendor** semantics; per V-014 the trader's engine is UNKNOWN, so even (c) does not transfer without V-102 |
| **R12** | **provenance repair for V-023** | Re-fetch and archive `https://ninza.co/product/vwap-flux` and `https://vwap.nt8.ninza.co/`, capturing the segmented-language strings verbatim with SHA-256 | n/a | NO | **YES**, on the next authorized browsing pass | n/a |
| **R13** | **new vendor evidence surface, not yet exploited** | The vendor's published **video** material shows the cloud **moving** (channel `@ninzaco`; VWAP Flux titles dated 2026-01-10 / 01-13 / 01-16 / 01-20 / 01-21 / 02-02 / 02-05 / 02-06 / 04-23 / 07-20). Frame-stepping any clip across a clock boundary answers R1, R3 and R4 directly and at far better effective resolution than a static PNG. | as R1/R3/R4 | NO | **YES** — public, free; requires an authorized browsing pass. **Not attempted in this pass.** | — |

**Reading of the table.** Every cell in column (a) is **NO**: the corpus is exhausted for
cloud geometry and this is proven, not assumed (V-028, V-104). The lifecycle question is
therefore **entirely** a vendor-public-material question (R1/R3/R4 → column b), and those
tests are cheap, already-in-repo, and have not been run. Only R6, R8, R9 and R10 genuinely
require a licensed copy — and per V-014/V-102 none of them transfer to the trader's build
without an assumption we have never tested.

**Consequence for the purchase gate.** The gate's row "CLOUD GEOMETRY: solved-to-class"
is withdrawn (V-024). That does *not* automatically raise the EVI, because V-100 already
records that the EVI downgrade rationale — an oracle answers vendor semantics, not the
trader's build — is itself conditional on V-014 remaining UNKNOWN. The correct update is:
**the gate has one fewer "solved" row, and the cheap (b)-column tests R1/R3/R4 must be run
before any purchase argument is re-opened**, since they may close the lifecycle question
for free.

---

## 5. What we would have got wrong if ACTIVE had stayed closed

We had recorded ACTIVE anchors as CONFIRMED, solved-to-class, on the strength of a
measurement whose two endpoints were both our own code, plus an eyeball reading of two
low-resolution PNGs, plus the observation that the one open-source analogue anyone had
found happened to work that way — and we had never noticed that **both** pieces of vendor
prose we actually hold, the manual's "recalculate the VWAP bands every 30 minutes" and
the product page's "divides the market into smaller time segments and recalculates VWAP
for each segment", read more naturally as SEGMENT than as ACTIVE, and point *away* from
the reading we had closed. Had it stayed closed, the whole VF stack downstream would have
been built on a cloud roughly **2.3× too narrow** with rails that move on every bar
instead of once an hour: OTR-VF-CAND1's 208-member identification, the 17-window §40
distances, the leave-one-window-out ranking of the trend cluster, the failure-week
diagnostic and the "the residual is in the trigger, not the inputs" conclusion were all
computed on L1 geometry with F1 rails, and under L2 every one of those numbers changes —
so a *geometry* error would have kept presenting itself as a *trigger* error, and V-044's
comfortable 1.7% tick-vs-bar input bound would have gone on reassuring us about an input
axis that was not the one that was wrong. We would have kept citing V-025/V-026 in reports
as though 47-vs-106 points were a fact about ninZa rather than a fact about `vf_core`,
kept "CLOUD GEOMETRY: solved-to-class" as a load-bearing row in the purchase-gate EVI
calculation, and — the expensive part — **generated no tests**, because a closed question
generates none: the pixel-metric extraction of the manual's own charts (R1/R2/R3/R4) and
the vendor's own published videos (R13) are free, sitting in the repository or one
authorized browsing pass away, and would simply never have been run. The error would have
been invisible, unbounded, and permanent. That is the cost of closing on morphology we
produced ourselves; the reopening is what makes the cheap vendor-side tests worth running
at all.

---

## 6. Open items created by this pass

| item | type | note |
|---|---|---|
| R1 / R2 / R3 / R4 pixel-metric extraction of the manual PNGs (pp.3/8) | **task, free, in-repo** | Highest priority. Answers L1 vs L2 vs L3 vs L4 and upgrades V-027 and V-034 from eyeball INFERENCE to measurement. Requires only image processing on an archived asset — no purchase, no browsing. |
| R13 vendor video frame-stepping | task, free, needs browsing authorization | Better resolution than any static PNG; not attempted. |
| R12 archive the V-023 product-page strings verbatim + SHA-256 | task, free, needs browsing authorization | Closes the §0 provenance gap. |
| F1x (exclusive/NIST percentile) is not implemented in `vf_core.rails_from_population` | **build gap** | Recorded, not fixed — this pass modifies no `.py` file. |
| No clean lifecycle A/B exists in any run directory (§2.5) | **FACT about our artifacts** | If a behavioural lifecycle contrast is ever wanted, it must hold levels, trend, signals, exits and stop fixed — and even then it may not select a semantic (§2.7). |
| V-033's 8.9 pt and the ~1.7 pt outer-rail figure are L1-conditional | **qualification** | Never re-quote them as lifecycle-free. |
| §3.4 lifecycle-invariance of the min-max rejection | **new INFERENCE, this pass** | Proposed as a registry amendment strengthening V-035's basis; conditional on V-038 and on R2 upgrading V-034. |
