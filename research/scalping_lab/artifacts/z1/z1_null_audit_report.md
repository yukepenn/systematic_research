# W2-0 Z1_DEFINITION_AND_NULL_AUDIT — READOUT (2026-08-08)

Spec: `specs/W2-0_z1_definition_null_audit.md` (frozen 1025569 before readout).
Code: `src/python/z1_null_audit.py`, `src/python/z1_null_audit_excursion.py`.
Tables: `z1_null_audit.csv`, `z1_null_audit_excursion.csv`. Detector = byte-identical
copy of the frozen `dc_segments`; OBS columns reproduce the published W1-1 numbers
exactly (r: 2.166/2.092/2.035/2.017/1.994/1.990; algebraic gross: +0.83/+0.93/+0.70/
+0.66/−0.51/−1.60) — this audit corrects the same object it audits.

## FACT — what ω is

`z1_dc_ladder.py` records ω = |ext − prev_ext| = extremum-to-extremum **TOTAL MOVEMENT
(TM = θ DC-leg + overshoot)**. It is NOT the DC-literature "overshoot". Identity:
OS = TM − θ.

## FACT — the correct null for r = E[TM]/θ is ≈ 2, and ≈ 2.13 for our data

| θ | NULL-1 ±1 RW | NULL-2 Gauss | NULL-3 sign-flip (matched) | OBS |
|---|---|---|---|---|
| 5 | 2.000 | 2.138 | 2.135 | 2.166 |
| 10 | 1.999 | 2.072 | 2.084 | 2.093 |
| 20 | 2.000 | 2.037 | 2.051 | 2.035 |
| 40 | 2.008 | 2.027 | 2.033 | 2.017 |
| 80 | 1.982 | 2.002 | 2.025 | 1.994 |
| 160 | 2.020 | 2.003 | 1.976 | 1.990 |

NULL-1 pins the theoretical null at 2.0 (E[OS] = θ for a driftless walk). NULL-2/3 show
that fat-tailed/jumpy increments alone push r above 2 at small θ — **even "r > 2" is not
persistence without a matched null.** Paired OBS − NULL-3 excess (day-clustered 95% CI):
**+0.032 [+0.020, +0.044] at θ=5 only**; every other θ is indistinguishable from
its matched null (θ=20/40 even lean negative). The amplitude-level persistence excess is
~0.16 ticks/cycle at θ=5 and nothing anywhere else.

## FACT — the published "gross +0.7–0.9t/cycle" was trigger-jump algebra, not P&L

The flip-to-flip algebra ω − 2θ credits fills at the EXACT confirmation levels ext ∓ θ.
With discrete jumps the confirmation event's actual mid is beyond that level, and the
algebra books that gap as profit. Decisive evidence — the same algebra on the
sign-randomized MARTINGALE null is also "profitable", while direct P&L on the null is ~0
(optional stopping, as it must be):

| θ | algebra NULL-3 | algebra OBS | DIRECT NULL-3 | DIRECT OBS |
|---|---|---|---|---|
| 5 | +0.67 | +0.83 | +0.01 | **−0.07** |
| 10 | +0.84 | +0.93 | −0.04 | **−0.22** |
| 20 | +1.02 | +0.70 | −0.07 | **−0.56** |
| 40 | +1.30 | +0.66 | −0.26 | **−1.82** |
| 80 | +2.01 | −0.51 | +0.70 | **−3.61** |
| 160 | −3.90 | −1.60 | −6.35 | **−6.61** |

(θ≥80 null cells are small-n noise — 44–186 cycles/day.) DIRECT = enter/exit at the
actual flip-event mids. **OBS direct gross is negative at every θ — flip-following loses
money BEFORE any commission or slippage.** Direct net C1 (day-clustered 95% CI):
−2.95 [−3.18,−2.79] @5, −3.10 @10, −3.43 @20, −4.69 @40, −6.48 @80, −9.48 @160 —
worse than the published algebraic numbers at every θ. Paired direct OBS − NULL-3 is ≤ 0
everywhere (significant at θ=40): at the achievable level NQ mid is, if anything, mildly
mean-reverting against the flip direction.

## FACT — the excursion "mild momentum" claim also dies under the matched null

Published W1-1 claim: unconditional P(+A before −B) runs +1–2pp above the gambler's-ruin
null B/(A+B) → "mid paths run slightly momentum-like". The ruin formula is exact only for
continuous/unit-step paths; jumps shift it. Same scan, paired OBS vs NULL-3 by session:

| Bracket | ruin null | OBS | NULL-3 | paired diff [95% CI] |
|---|---|---|---|---|
| +4/−2 | 0.333 | 0.3485 | 0.3444 | +0.0041 [+0.0016, +0.0068] |
| +6/−2 | 0.250 | 0.2683 | 0.2627 | +0.0055 [+0.0029, +0.0083] |
| +6/−3 | 0.333 | 0.3450 | 0.3432 | +0.0019 [−0.0008, +0.0044] |
| +8/−4 | 0.333 | 0.3421 | 0.3381 | +0.0040 [+0.0009, +0.0068] |

Roughly 2/3–3/4 of the published "+1–2pp over the null" was jump artifact. True momentum
content vs the matched martingale: **+0.2–0.6pp, CI excluding 0 on 3 of 4 brackets —
statistically detectable, economically negligible** against a 25–40pp break-even gap.
CORRECTED: "mid paths run slightly momentum-like (+1–2pp)" → "mid paths carry a
detectable but tiny (+0.2–0.6pp) directional excess over a jump-matched martingale."

## INFERENCE — what survives, what is retracted

- RETRACTED: "r ≈ 2 = genuine directional persistence" (null was mis-specified at 1).
- RETRACTED: "gross flip-to-flip capture is positive at θ≤40" (algebra artifact; direct
  gross is negative at ALL θ).
- RETRACTED: excursion "mild momentum" (jump artifact to within ~½pp).
- SURVIVES: **Z1 standalone CLOSED** — a fortiori (spec rule 2: direct net C1 < 0
  everywhere, CIs < 0 through θ=80). Role-B/C eligibility unchanged.
- SURVIVES: the W1-1 conclusion "NOWHERE on the micro grid is persistence economically
  tradable" — now stronger: there is essentially no persistence to trade at any θ; the
  only detectable structure is a +0.03 r-excess at θ=5 (~0.16t at amplitude level) that
  does not exist at the achievable-P&L level.
- NEW REFERENCE: the NULL-3 columns are the campaign's null curves for ALL future DC /
  excursion statistics (spec rule 3). The gambler's-ruin formula is decorative only.

## Consequences binding future work

1. Any "persistence/momentum" claim on event-level NQ mid MUST be stated as an excess
   over a sign-randomized matched null, never over 1, 2, or B/(A+B).
2. Any flip-to-flip / barrier economics MUST be computed at actual event prices (direct),
   never from segment-amplitude algebra.
3. W1-1 report carries a correction banner; original tables preserved (never deleted).
No selection content in this audit; no DoF charged. Registry row S0-A4.
