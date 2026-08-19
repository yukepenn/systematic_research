# TOMFLOW01 — Turn-of-month institutional cash-cycle long window (FROZEN SPEC)

**Committed BEFORE any outcome is read.** Date 2026-08-19. Source: ENGINE3_SCOUT_20260819
gatekeeper rank-3 (Lakonishok-Smidt 90yr DJIA; McConnell-Xu JF 2008 incl. futures confirmation;
Etula-Rinne-Suominen-Vaittinen RFS 2020 "Dash for Cash" — month-end payment-cycle flows).
**Second and FINAL alpha hypothesis of this wave (cap 2/2; CLOSEREV01 was the 1st).**
Registry-verified distinct from killed seq 379 (a CONDITIONAL last-2-day MTD-sign FADE; this is
an UNCONDITIONAL always-long window — 3 of 4 held days non-overlapping with 379's window;
mechanical distinctness adjudicated by the scout gatekeeper against the registry).

Honest power prior (stated before the read): full historical effect (~0.47%/window vs ~2.8%
window σ) gives t≈2.6 at N≈244; at half the historical effect (Maberly-Waggoner post-1990 decay
reading) t≈1.3 and the test fails. A FAIL is the expected outcome under the decay literature;
this is a cheap decisive read either way.

## Construction (zero tuned constants; classic McConnell-Xu window)

- Substrate: `nq1m_2005_202605.parquet`; trading day = ≥200 RTH bars (09:30-15:58);
  `sess_close(d)` = last bar ≤15:58 close (LIQREV01 conventions, incl. MANIFEST_NOTES defects).
- **Event**: each calendar month-turn. Enter LONG 1 NQ at `sess_close` of the month's
  SECOND-TO-LAST trading day + 1 tick adverse; exit at `sess_close` of the NEXT month's THIRD
  trading day − 1 tick adverse (captures the classic TOM days: last day + first three).
  Commission $4.36/RT; C1 (RTH-close liquidity; the CLOSEREV post-close spread issue does not
  apply). One event per month-turn; no overlaps by construction.
- **Placebo**: identical 4-held-day long entered at `sess_close` of the month's TENTH-TO-LAST
  trading day (mid-month control), same costs.

## Frozen gates (ALL required)

- **G1** N ≥ 200 events.
- **G2** net $/event: iid bootstrap CI_lo > 0 AND calendar-year-block bootstrap CI_lo > 0
  (resample years with replacement; 10,000 reps, seed 20260821).
- **G3-SPLIT (PRIMARY)**: pre-2020 mean > 0 AND 2020+ mean > 0 AND at least one subsample
  CI_lo > 0 AND neither CI_hi < 0.
- **G4** modern-relevance: 2016-2026 subsample mean > 0 (the Maberly-Waggoner death reading
  wins otherwise).
- **G5** placebo not significantly positive AND TOM mean > placebo mean.
- **G6** window plateau: {T-2→T+3 primary, T-1→T+3, T-2→T+2} all positive sign.
- **G7** tails: top-1% of events ≤ 50% of |net|; no single event (winner OR loser) > 25% of
  |net|; October-2008-class events reported by date.
- **G8** portfolio: losing-day ρ ≤ 0.25 vs certified Solar B_SYM ledger (2022+ overlap; TOM's
  4-days-per-month long beta makes this a REAL test, unlike CLOSEREV) AND the level functional
  (net on Solar losing days) reported; if the level is materially negative the readout must
  carry it as a binding caution regardless of ρ.
- **G9** cost stress: G2 and G3-SPLIT hold at 2 ticks/side + 3× commission.

## Outcomes

PASS-SCREEN → red team before any freeze (house pattern). FAIL → the NQ calendar-flow axis is
CLOSED (joining day-of-week and month-end-fade seq 379); the deliverable is the closure.
Artifacts → `out/`; registry row after readout; substrate ends 2026-05-29, seals untouched.
