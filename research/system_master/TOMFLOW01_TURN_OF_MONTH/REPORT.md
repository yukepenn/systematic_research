# TOMFLOW01 — REPORT (readout 2026-08-19; spec frozen at 1d5ee2d BEFORE the run)

**Verdict: FAIL — the NQ calendar-flow axis is CLOSED (joining day-of-week and the seq-379
month-end fade), exactly as the spec's own power prior predicted. Second and final alpha
hypothesis of this wave (2/2).**

## Numbers (N=244 month-turns, 2006-2026, C1)

- Net +$71,576 (+$293/event) — positive point estimate, but **iid CI [−304, +894] and
  year-block CI [−42, +706] both span zero → G2 FAIL.** The spec's honest prior ("at half the
  historical effect t≈1.3 and the test fails") is exactly what happened: realized t ≈ 0.96.
- **G3-SPLIT FAIL**: pre-2020 +$76/event CI [−208, +332]; post-2020 +$774/event CI [−1066,
  +2612] — neither era individually distinguishable from zero.
- **G7 FAIL**: single best event = 33% of |net|, single worst = 28% (worst dates: 2026-01-29
  −$20.4k, 2024-07-30 −$19.7k, 2022-10-28 −$17.2k) — the "effect" is a handful of month-turns
  that happened to sit on big directional weeks.
- **G8 FAIL**: losing-day ρ vs Solar = 0.314 > 0.25 — an unconditional 4-day-per-month long is
  correlated long beta, as the gatekeeper warned ("worst correlation character of the
  survivors").
- **G9 stress FAIL** (CI spans zero at 2t/side + 3× comm). G4/G5/G6 passed (modern era positive
  in point estimate; placebo null; window plateau) — insufficient without economics.
- Per-year: churn (+$33k 2020, −$12.7k 2021, −$8.9k 2022, +$19.4k 2023) — flow-cycle stories do
  not survive contact with a 2.8%-σ window on a 1.7%-mean effect at N=244.

## Interpretation

The turn-of-month premium on NQ is, at best, half its historical textbook size and statistically
indistinguishable from zero on 20 years of data — the Maberly-Waggoner "dead in index futures
post-1990" reading wins over Etula et al's cash-cycle persistence at this instrument and sample.
The closure is the deliverable: the calendar axis (day-of-week, month-end fade, turn-of-month,
pre-holiday-by-literature) is now fully adjudicated dead on NQ. No red team needed (FAIL, nothing
adopted). Artifacts: `out/tomflow01_{results.json,events.csv,placebo.csv}`. Seals untouched
(substrate ends 2026-05-29).
