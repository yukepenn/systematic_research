# PARAMETER_INTERVENTION_2025 — what the A3/A4/A5 retune actually changes

Run: `runs/OTR_R12_PARAM_INTERVENTION/` (spec preregistered before readout).
Directive v4.0 section 11 / phase P4. Window 2025-06-15 → 2026-01-23, NQ 1-minute,
215,487 bars. **No P&L is computed anywhere in this run**, by construction: the question is
which event families are structurally sensitive, and profit is not allowed to answer it.

Intervention: `A2 179→180, A3 5→3, A4 10→6, A5 10→9` (SlowdownScan / WeakWeakSplit /
PullbackSplit). Each field is also varied ALONE to attribute the effect.

## Headline

| family | OLD 5/10/10 | NEW 3/6/9 | Δ | Jaccard(bar-exact) | attributable to |
|---|---|---|---|---|---|
| **T1** trend start | 2386 | 2364 | **−0.92 %** | 0.9053 | **A2 only** (A3/A4/A5 → J = 1.000000) |
| **T2** pullback (Early) | 6286 | 6475 | **+3.01 %** | 0.9129 | **A5 only** (A3/A4 → J ≈ 0.999) |
| **T3** strengthening | 3466 | 4803 | **+38.57 %** | 0.7011 | **A4 (+17.0 %) then A3 (+12.4 %)**; A5 ≈ 0 |
| weak duty cycle | 66.08 % | 73.94 % | +7.86 pp | — | A4 (+4.4 pp), A3 (+1.7 pp) |
| wave transitions | 5912 | 7257 | +22.8 % | — | A4, A3 |

Single-field isolation (PullbackEarly = True; the False column is materially identical):

| set | T1 | T2 | T3 | J(T1) | J(T2) | J(T3) | weak % |
|---|---|---|---|---|---|---|---|
| OLD 5/10/10 | 2386 | 6286 | 3466 | 1.0000 | 1.0000 | 1.0000 | 66.08 |
| NEW 3/6/9 | 2364 | 6475 | 4803 | 0.9053 | 0.9129 | 0.7011 | 73.94 |
| only A2=180 | 2364 | 6273 | 3449 | 0.9053 | 0.9897 | 0.9882 | 66.27 |
| only A3=3 | 2386 | 6286 | 3896 | **1.000000** | 0.9990 | 0.8610 | 67.76 |
| only A4=6 | 2386 | 6287 | 4056 | **1.000000** | 0.9998 | 0.8477 | 70.44 |
| only A5=9 | 2386 | 6489 | 3461 | **1.000000** | 0.9222 | 0.9968 | 66.08 |

## Preregistered verdicts, reported as they landed

- **P1 (T1 near-invariant, J > 0.97) — FAILED AS WRITTEN (J = 0.9053).**
  The prediction was mis-specified, not the premise. The entire T1 movement is caused by
  **A2 179→180**; A3, A4 and A5 each leave T1 identical to *machine precision*
  (J = 1.000000, count unchanged at 2386). The intended claim — *A3-A5 are invisible to a
  T1-only strategy* — is CONFIRMED more strongly than predicted. The A2 effect is timing
  jitter from a 1-tick threshold change (count −0.9 %, but 9.5 % of flip bars shift).
- **P2 (T3 rises) — PASS**, and it is the dominant effect by an order of magnitude.
- **P3 (T2 rises) — PASS**, but only +3.0 %, and traceable to A5 alone.
- **P4 (more weak-state time) — PASS**, 66.08 % → 73.94 %.

## Side asymmetry

| family | long Δ | short Δ |
|---|---|---|
| T1 | −0.9 % | −0.9 % |
| T2 | +3.4 % | +2.6 % |
| T3 | +36.9 % | **+41.5 %** |

T3 grows more on the short side. This matters because the 2025 residual we are chasing is
itself direction-concentrated (HTFMECH01 closure, and the R5 hp-week short-side residual).

Novel event bars (bars carrying a NEW event where the OLD parameters produced **no event of
any kind**): T1 80, T2 375, **T3 1381**.

## A structural finding recorded because it looks like a bug and is not

`TrendVector` is **bit-identical** between A2 = 179 and A2 = 180 (0 differing elements of
215,487) even though `anchor` differs on 1,072 bars and `is_up` differs on the same 1,072.

Mechanism: A1 = 90 ticks → V = 22.50 pts; A2 = 180 ticks → S′ = 45.00 pts, i.e. **V = S′/2
exactly**. On the 0.25 tick grid, the only excursion that separates the two configurations
is one of *exactly* 45.00 points: the 179-config flips (45.00 > 44.75) while the 180-config
does not (45.00 > 45.00 is false). At that instant one anchor is set to the current close
and the other remains exactly 45.00 = 2V away, so `anchor − V` and `anchor + V` coincide.
Verified specific rather than general: A2 ∈ {178, 181, 182, 190, 240} all produce differing
TrendVectors (1,462 / 935 / 1,788 / 9,963 / 49,217 bars).

Consequence used below: the pullback GEOMETRY (T2 is defined by excursions across
TrendVector) is untouched by the A2 change, so the measured T2 delta is purely A5.

## Adjudication against directive v4.0 section 1H

The directive forbids naming the missing layer "pullback" until it is discriminated. This
run supplies the first quantitative discrimination:

- STATUS **REPRODUCED**: A3, A4, A5 are exactly invisible to T1 event bars (J = 1.000000).
  So a T1-only strategy cannot respond to the trader's retune at all. Whatever his build
  does respond with, it consumes something outside T1.
- STATUS **REPRODUCED**: in event space the retune moves **T3 by +38.6 % and T2 by +3.0 %** —
  a factor of ~13. If the trader's behaviour changed materially at the retune, T3
  (strengthening / weak→new-extreme resumption) is by far the more sensitive carrier.
- STATUS **INFERENCE (weak)**: "the missing layer is T2 pullback." The intervention does not
  support it preferentially; it points at T3.
- STATUS **UNKNOWN**: which family his build actually consumes. Event-count sensitivity is
  NOT behavioural sensitivity — a wrapper that takes only the *first* T2 per trend would be
  nearly insensitive to A5's +3 %, and one that requires a strong-trend T3 would damp the
  +38.6 %. This run ranks the candidates; it does not select one.

## What this run cannot do

The trader moved A3, A4 and A5 **together**, so his own data cannot attribute his
behavioural change to a single field. Only the event-space decomposition above is
attributable. Any claim of the form "he changed A4 because he wanted more re-entries" is
INFERENCE with no separating evidence.

## Falsifier status

The spec's UNINFORMATIVE falsifier ("if every family moves by a similar relative amount")
did NOT trigger: −0.9 % / +3.0 % / +38.6 % is a wide spread, and the single-field isolation
is clean (three of four fields have an exactly-zero effect on at least one family).
