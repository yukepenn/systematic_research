# PURCHASE_GATE_v2 — should we buy VWAP Flux ($300)?

Directive v4.0 §34/§35. Supersedes `PURCHASE_GATE.md`. Written 2026-08-25 after the
directive-v4.0 pass. The owner's standing framing: buy only as a last resort, only as an
**information purchase**, never as "buy the profitable indicator".

# Recommendation: **DO NOT BUY.** Verdict: UNNECESSARY, not merely premature.

Not because the money is large, and not on caution — on four measured findings, three of
which are new this pass and any one of which would be enough on its own.

---

## 1. Geometry is not the binding constraint — measured

`runs/OTR_R26_VF_GEOMETRY_EVI` re-ran the full 144-member structural grid over the trader's
17 weekly windows under **all six rival cloud geometries** and took the minimum mean §40
distance in each — an optimistic bound on what an oracle could deliver, since it is chosen
with hindsight against the trader's own data.

| geometry | floor |
|---|---|
| block + percentile_linear | **0.4624** |
| block + nearest_rank | **0.4624** |
| anchor + percentile_linear | 0.4761 (the incumbent) |
| anchor + nearest_rank | 0.4761 |
| anchor + minmax | 0.4866 |
| block + minmax | 0.5190 |

**Perfect knowledge of the vendor's lifecycle and rail formula is worth 0.4761 → 0.4624:
a 2.9 % improvement.** No geometry comes near 0.35, the level at which VF would sit in the
same band as our ordinary Solar weekly fit (0.280 dev / 0.422 hp). The residual is not in
the geometry.

## 2. Two of the three open vendor questions cannot change any observable

`percentile_linear` and `nearest_rank` produce **identical floors** in both lifecycles. At
n = 5 with percentiles 95/75/50/25/5 they coincide on the inner rails, and the best member
uses the median. The linear-vs-nearest-rank question — treated as open through the whole
clean-room effort — is **behaviourally inert**. An oracle answering it buys literally
nothing. `min-max` is already measurably worse, confirming EV-040 behaviourally.

That leaves one live geometry question (lifecycle), worth ≤ 0.0137.

## 3. There is no 2026 evidence surface an oracle's answer could be tested against

The entire 164-image corpus contains per-day Analysis tables — the rows carrying
`avg_MAE` / `avg_MFE` — for exactly **three** records:

| record | coverage | era |
|---|---|---|
| OTRIMG-0003 | 11 days, Jan-2023 | Solar |
| OTRIMG-0026 | 2 days, Feb-2025 | Solar / DSTM |
| OTRIMG-0032 | summary strip, **no per-day rows** | Mar-2025 |

**Nothing for 2026.** All 24 rows of 2026 evidence are *weekly* aggregates, and their
columns contain no MAE/MFE at all.

This matters because of exactly how the 2023 reconstruction succeeded. It required
per-DAY rows, plus MAE/MFE path statistics that no P&L-matching trade subset can fake, plus
the $5-tick lattice that makes their sums exact integers, plus solving the days *jointly*.
That combination collapsed 11 days to **one** trade path. None of that machinery has
anything to bite on in 2026. Even a perfect oracle would leave us fitting a 13-parameter
signal generator plus a wrapper to 24 aggregate rows — the exact regime in which R7/R8
already produced a 4-member inseparable cluster.

## 4. Vendor semantics would not transfer to his build anyway — now proven, not assumed

`runs/OTR_R25_FEB2025_INVERSE` established at **cent level** that this trader's builds
differ across eras: the mechanism that reproduces Jan-2023 exactly (T1-only entries, strict
flip exit) is **infeasible** for 2025-02-26, an ordinary 15-trade day, under exhaustive
search. He modifies his stack. His VF panel already differs from every published vendor
preset (CloseThreshold 10 against a universal 70).

So "what does the vendor's indicator do" and "what does his 2026 strategy do" are
demonstrably different questions, and only the second one matters.

## What changed about EV-039 — and why it does not argue for buying

EV-039 previously read: his frames show `BidAskPrice_RealVolume` with Tick Replay OFF, which
the manual says computes nothing historically, yet his backtests are full — therefore he
reimplemented the indicator. **That premise does not hold.** No frame in the corpus shows
Tick Replay state and `BidAskPrice_RealVolume` *together*: Tick Replay is legible only in
seven Feb-2025 Solar-era frames (all unchecked), and every 2026 frame lacks the row
entirely. The conjunction was assembled across a family change and twelve months. The manual
also explicitly invites user-written wrappers ("you can rely on the signals below to build
your own strategy"), so a custom wrapper is not evidence of reimplementation.

This **removes an argument against** buying (the fear that an oracle would describe an
indicator he never used). It does not create an argument *for* buying — findings 1–3 are
untouched by it, and hypotheses H1–H5 all remain live.

---

## What WOULD flip this decision

Stated in advance so the verdict is falsifiable:

1. **A 2026 per-day Analysis table with avg_MAE / avg_MFE.** This is the binding item. With
   one, the machinery that produced the exact 2023 reconstruction could be aimed at the VF
   era, and vendor-level signal timing would become checkable. The owner has confirmed the
   164 images are the complete corpus, so this is not obtainable — which is precisely why
   the purchase cannot be rescued by spending.
2. **Some geometry reaching a floor below 0.35** in a future re-run (e.g. after the Layer-A
   rebuild corrects the QtyPerTrend/Split semantics). That would show geometry does carry
   the residual after all. The corrected two-layer architecture is specified in
   `VF_SIGNAL_GENERATOR_v2.md` and has not yet been built — **this is the one genuinely
   open free item, and it should be done before the question is revisited.**
3. Direct evidence that his build tracks vendor semantics (e.g. a frame showing a vendor
   version string alongside his panel).

## Free work that was completed this pass, so "not exhausted" is no longer an excuse

- Vendor manual chart plates extracted (23 images) and rail geometry measured with a
  rasterised synthetic control — **inconclusive**, recorded as a negative result rather
  than quietly dropped.
- All six geometries swept behaviourally (R26).
- EV-039 re-audited against the actual frames.
- Signal-vs-execution defect confirmed by code reading and the corrected architecture
  specified.

## Bottom line for the owner

Spending $300 would buy a precise answer to a question worth **2.9 %** of the reconstruction
distance, about an indicator we cannot show he used unmodified, in an era where we hold no
evidence fine-grained enough to check the answer. The binding constraint is **evidence, not
vendor knowledge** — and no amount of money fixes that.

The one thing that could still move 2026 is free: build Layer A correctly and re-measure.
