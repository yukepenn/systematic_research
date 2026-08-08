# W1-1 Z1 Readout — DC Scale Transfer + Excursion Baselines

> ## ⚠ CORRECTION 2026-08-08 (W2-0 Z1_DEFINITION_AND_NULL_AUDIT, Amendment 4 §2)
> This report's INTERPRETIVE claims were wrong; the numbers are reproduced exactly but
> re-baselined. See `z1_null_audit_report.md` (binding). Summary of corrections:
> 1. ω here is TOTAL MOVEMENT (ext-to-ext), not overshoot. The martingale null for
>    r = E[ω]/θ is **≈2.0 (and ≈2.13 for the jump-matched null at θ=5), not 1**.
> 2. "r > 2 ⇒ genuine persistence" is RETRACTED: the only excess over the matched null
>    is +0.032 at θ=5 (~0.16t at amplitude level), nothing elsewhere.
> 3. "gross flip-to-flip +0.7–0.9t/cycle" is RETRACTED — it is trigger-jump algebra;
>    the same algebra is +0.67–1.3t on a sign-randomized MARTINGALE. DIRECT
>    entry→exit gross is **negative at every θ** (−0.07t @5 → −6.6t @160), and direct
>    net C1 is −2.9 to −9.5t/cycle — worse than the table below shows.
> 4. Excursion "mild momentum (+1–2pp over null)" is CORRECTED to +0.2–0.6pp over the
>    jump-matched null (ruin formula is not the right null for a jump process).
> 5. The CLOSED verdict SURVIVES a fortiori. Original text preserved below unedited.

Date: 2026-08-08. Spec: `specs/W1-1_Z1_dc_scale_transfer.md` (frozen 7513c6b before any
tick-level DC statistic was read). Data: 37 L2 discovery sessions, event-level causal MID.
Tables: `z1_r_curve_by_session.csv`, `z1_excursion.csv`. Code: `src/python/z1_dc_ladder.py`.

## r(θ) — the scale map (per-session mean, 37 sessions)

| θ (ticks) | cycles/day | r = E[ω]/θ | gross ticks/cycle (flip-to-flip = ω−2θ) | net after C1 [95% day-CI] |
|---|---|---|---|---|
| 5 | 31,583 | 2.166 | +0.83 | −2.04 [−2.19, −1.81] |
| 10 | 9,447 | 2.092 | +0.93 | −1.95 [−2.11, −1.75] |
| 20 | 2,657 | 2.035 | +0.70 | −2.17 [−2.67, −1.75] |
| 40 | 708 | 2.017 | +0.66 | −2.21 [−2.94, −1.55] |
| 80 | 186 | 1.994 | −0.51 | −3.38 [−7.41, +0.53] |
| 160 | 44 | 1.990 | −1.60 | −4.48 [−15.76, +6.67] |

**Finding 1 — the overshoot ratio is sampling-scale-dependent:** event-level mid gives
r ≈ 2.0–2.17 across the micro grid, vs r ≈ 1.29 measured at θ=179 on 3-min CLOSES
(T0-9). Coarse close-sampling truncates intra-bar extremes and shrinks measured amplitudes
toward θ; at full resolution NQ mid segments average ~2× their threshold, decaying toward
2.0 as θ grows. (No contradiction with DC02b — different sampling objects.)

**Finding 2 — persistence is real but micro-economics are dead:** r > 2 at θ ≤ 40 means
flip-to-flip capture is GROSS-positive (+0.7 to +0.9 ticks/cycle) — genuine directional
persistence measured on our own data. But it is a fraction of friction: net after C1
(the OPTIMISTIC cost model per W1-0b — real BBO crossing costs more) is significantly
negative at every precise θ (5–40), and gross itself turns negative by θ=80. **The answer
to "where does NQ persistence cross from statistically present to economically tradable"
is: NOWHERE on the micro grid under retail friction.** This is our own-data confirmation
of the DR-A/B literature prior (0.1–1 tick gross short-horizon edges).

## Excursion baselines (frozen A/B grid, mid prices, pooled)

| Bracket | Gambler's-ruin null | Unconditional | Post-flip best (θ=80) | Break-even win rate under C1 |
|---|---|---|---|---|
| +4/−2 | 0.333 | 0.347 | 0.370 | 74.5% |
| +6/−2 | 0.250 | 0.268 | 0.292 | 60.9% |
| +6/−3 | 0.333 | 0.345 | 0.360 | 65.2% |
| +8/−4 | 0.333 | 0.343 | 0.356 | 57.4% |

Mid paths run slightly momentum-like (+1–2pp over null); the DC-flip state adds only
+1–4pp more. **The gap to break-even is enormous (~25–40pp).** Single micro primitives are
nowhere near economic; per Amendment 1 §8 the only viable route to a high-precision micro
scalp is small economically-motivated interaction states that lift P(+A before −B) by tens
of points — or micro information used in roles B/C instead of standalone direction.

## Verdict (frozen rules, W1-1 spec)
**Z1 CLOSED AS STANDALONE** ("r(θ)>1 but net/cycle<0 at every θ" clause; C1 is already the
optimistic model, so the closure holds a fortiori under BBO-based costs). The r(θ) curve
and excursion baselines are published as campaign reference constants. Z1 re-registration
is permitted ONLY as a role-B/C feature (selectivity or execution overlay) in a new spec.
No grid refinement, no rescue. DoF charged: 6.
