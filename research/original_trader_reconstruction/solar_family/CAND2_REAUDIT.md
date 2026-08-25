# CAND2_REAUDIT — the D-gate re-adjudicated against invariant labels

Run `runs/OTR_R11_INVERSE/` (amendment_2 preregistered before this readout),
script `solar_family/src/run_r14_gate.py`, outputs `out/gate_labels.csv`,
`out/gate_component_scores.csv`. Directive v4.0 section 13.

**No P&L objective appears anywhere in this fit.** Components are scored only against
TAKE/SKIP labels implied by uniquely-recovered daily trade paths.

## Label provenance and its limits

For 8 of the 11 visible Jan-2023 days the inverse solver returns **exactly one** feasible
trade path under the T1-only universe with the STRICT exit rule. That path fixes, for every
T1 signal at which the strategy was flat, whether it was taken.

- 16 flat T1 decision points; 1 removed as platform warm-up (below); **15 labels, 10 TAKE / 5 SKIP**.
- Status: **INVARIANT_LABELS** — stronger than the retired R1e conditional labels because
  the solution is unique, but still conditional on (universe = T1-only, exit rule = STRICT).
  If a wider universe later admits a second path for one of these days, those labels revert
  to AMBIGUOUS.
- **The sample is small and unbalanced**: 4 of the 5 SKIPs come from a single session
  (2023-01-05). Every conclusion below is bounded by that.

### A platform effect that was NOT a strategy rule

`2023-01-03 18:11` is a SKIP that no gate can explain — session P&L, high-water,
consecutive losses and trade count are all zero there. It is bar **10 of the backtest**, and
`BarsRequiredToTrade = 20`. It is blocked by NinjaTrader, not by the strategy.

This independently corroborates the backtest boundary: the trader's report begins with the
2023-01-03 session, which under NT8's session-based `From` convention opens at 18:00 on
2023-01-02 — consistent with the uniquely-recovered 1/3 path containing a trade entering
2023-01-02 21:39, and with the report having no 1/2 row. Had this point been fed to the
gate fit it would have invented a rule that does not exist.

## Component classification (leave-one-component-out, labels only)

| components | correct / 15 | false-suppress | false-allow | verdict |
|---|---|---|---|---|
| ALL (incumbent X1600 X2 2500 K3 C700 cap20 cd3) | 14 | 1 | 0 | — |
| ALL minus **X** | 12 | 1 | 2 | **NECESSARY** |
| ALL minus **C** | 12 | 0 | 3 | **NECESSARY** |
| ALL minus K | 14 | 1 | 0 | **UNIDENTIFIED** (never binds) |
| ALL minus cap | 14 | 1 | 0 | **UNIDENTIFIED** (never binds) |
| ALL minus cd | 14 | 1 | 0 | **UNIDENTIFIED** (never binds) |

> **K, cap and cooldown do no work on this label set.** They were carried on the strength of
> master-window P&L, which directive v4.0 section 13 forbids as a retention criterion. They
> are not falsified — they are simply unsupported here, and both settings stay alive.

## What is FALSIFIED

**The C-block as specified (prior-session net ≤ −700 ⇒ suppress entries for the first 360
minutes of the session) is FALSIFIED.** It cannot satisfy the labels under any duration:

| session | prior-session net | blocked at MfO | first TAKE at MfO |
|---|---|---|---|
| 2023-01-05 | −1,148.52 | 185, **334** | 530 |
| 2023-01-13 | **−3,321.88** | 75 | **154** |

A single duration would have to be ≥ 334 (to block 01-05) and < 154 (to allow 01-13)
simultaneously. Making the duration depend on the size of the prior loss makes it *worse*:
the session with the **larger** prior loss has the **shorter** block. No clock-time window
works either (20:35 allowed, 21:06 blocked), and it is not a direction rule (both a long and
a short are skipped on 01-05, and both directions are taken elsewhere).

## What SURVIVES

**The C TRIGGER is SUPPORTED and bracketed.** Initial-session skips occur in exactly the two
sessions whose prior session lost meaningfully, and nowhere else:

| session | prior net | initial skips |
|---|---|---|
| 2023-01-06 | −30.08 | **0** (takes at MfO 91) |
| 2023-01-05 | −1,148.52 | 2 |
| 2023-01-13 | −3,321.88 | 1 |
| 01-09 / 01-10 / 01-11 / 01-16 | all positive | 0 |

⇒ threshold **C ∈ (30.08, 1148.52]** — an INTERVAL, not the point value 700. Recorded as an
interval per directive section 6; do not quote 700 as identified.

**X (the armed-then-negative suppression) is NECESSARY**: 2023-01-05's 13:23 and 14:15 skips
occur with session high-water 1,937.46 and session cum −30.08, i.e. the session gave back a
gain — exactly what X encodes. Removing X leaves both unexplained.

## Structural findings that constrain the whole wrapper family

Measured on all 15 decision points, and true by construction of the Solar recurrence:

- On a **T1 flip bar the anchor is reset to the close**, therefore
  `close − TrendVector ≡ ±V` (±22.50 pts) and `close − TrailingStop ≡ ±S` (±44.75 pts),
  *exactly*, on every flip bar without exception.
- On a **T1 flip bar `Signal_Trend` is always ±2 (strong)**, because a flip clears the weak
  latch.

> **Consequence: any proposed entry filter of the form "only enter when the trend is STRONG"
> or "only enter when price is far enough from TrendVector / TrailingStop" is INERT for T1
> entries.** It can never change a T1 decision. A whole family of otherwise-plausible
> wrapper rules is therefore ruled out for the early flagship at zero cost, and any future
> candidate that relies on such a filter to explain T1 behaviour is wrong by construction.

## The one remaining unexplained label

`2023-01-12 20:35` (short, session 01-13) is TAKEN but suppressed by the incumbent C-block.
This is the single false-suppression in the table above, and it is the same observation that
falsifies the block's duration. No constant set in the swept space
(X ∈ {800…2500, ∞} × X2 ∈ {1600…3000, ∞} × K ∈ {2,3,4,∞} × C ∈ {300…900, ∞} ×
cap ∈ {8…20, ∞} × cd ∈ {0…5}, 25,920 sets scored) reaches zero label errors; the best is 1.

Per amendment_2, **no new ad-hoc gate term has been added to force a fit.** The honest state
is: the evening-suppression MECHANISM is unidentified. Its trigger is real and bracketed;
its scope rule is not a fixed time window.

## Status changes recorded

| claim | was | now |
|---|---|---|
| D-gate constants {1600, 2500, 3, 700, 20, 3} identified | INFERENCE (stated as fitted) | **PARTLY FALSIFIED** — C's 360-min scope falsified; C threshold an interval; K/cap/cd UNIDENTIFIED |
| CAND2 "verified model class" | asserted | **conditional reconstruction**; IMPLEMENTATION_PARITY only |
| exit test = inclusive touch | campaign-1 V0 convention, inherited | **STRICT preferred**: 8/11 vs 5/11 days uniquely explained; see amendment_1 |
| trader's backtest start | assumed | **REPRODUCED**: 2023-01-03 session (opens 2023-01-02 18:00 ET) |
