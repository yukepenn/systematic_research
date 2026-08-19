# CLOSEREV01 — Post-cash-close price-pressure reversion, 16:00→16:14 ET (FROZEN SPEC)

**Committed 2026-08-19, BEFORE any outcome is read. The P&L readout is NOT run today: it opens
the NEXT wave's alpha budget (this wave's §15 cap 2/2 was exhausted by HTFDIR01 + LIQREV01).**
Source: ENGINE3_SCOUT_20260819 gatekeeper rank-2 (Bogousslavsky-Muravyev JFM 2023: closing-
auction price deviations revert; the closing cross's uninformed-flow share tripled 2010-2018 —
a structural era falsifier). The 16:00-16:14 futures-only window has never been traded by any
engine or dead family in this repo (verified in the scout).

## Pre-outcome feasibility audits (run 2026-08-19, BEFORE this spec's cost model was frozen;
## outputs in out/feasibility_*.json — no strategy P&L was computed)

1. **Window availability (20-year census)**: 16:00-16:14 minute bars exist for ~247-251
   days/year in every year 2006-2026, median 15/15 bars. PASS.
2. **Execution-cost audit on the local tick/BBO year** (43 usable sessions 2025-08→2026-05):
   window activity ~9,800 trades/session (fillable); **median bid-ask spread 2.0 ticks,
   p90 3.0, 18/43 sessions >2 ticks** — the RTH 1-tick C1 convention UNDERSTATES this window.
   **Kill switch does not fire; consequence (frozen now): the primary cost model is
   C1w = $4.36/RT commission + 1.5 ticks/side slippage ($19.36/RT); stress = 2.0 ticks/side +
   3× commission.** Disclosure: the BBO year is 2025-26 only; older-era spreads are unobservable
   — the stress cost model is the hedge against that.

## Construction (zero tuned constants beyond literature/repo defaults)

- Substrate: `nq1m_2005_202605.parquet` (defects of record in substrate MANIFEST_NOTES apply).
- **Impulse(d)** = close(16:00 bar) − close(15:45 bar), points, on days where both bars and the
  16:14 bar exist.
- **z(d)** = Impulse(d) / σ63(d), σ63 = std of Impulse over trailing 63 sessions, shift(1).
- **Trigger**: |z(d)| ≥ 2. **Side = −sign(Impulse)** (fade). Enter at the 16:00 bar close
  + 1.5 ticks adverse; exit at the 16:14 bar close + 1.5 ticks adverse; commission $4.36/RT;
  1 NQ; no intraday stop (14-minute hold); every trade flat before the 16:15 halt.
- Placebo: |z(d)| < 1 days, same fade construction.

## Frozen gates (ALL required)

- **G1** N ≥ 150.
- **G2** net $/trade: iid bootstrap CI_lo > 0 AND episode-block CI_lo > 0 (episodes = trigger
  days grouped by entry-gap ≤ 5 sessions; 10,000 reps, seed 20260820).
- **G3-SPLIT (PRIMARY — the 2026-08-19 standing lesson, first application)**: pre-2020 subsample
  net/trade > 0 AND 2020+ subsample net/trade > 0 AND at least one subsample CI_lo > 0 AND
  neither subsample CI_hi < 0. A construction alive only post-2020 FAILS here by design.
- **G4** era-trend falsifier (literature-specific): the 2016-2026 net/trade must be ≥ the
  2006-2015 net/trade − 1 SE (the mechanism predicts non-decreasing pressure; a decaying-era
  profile contradicts it).
- **G5** placebo not significantly positive (iid CI_lo ≤ 0).
- **G6** plateau: 3×3 grid (z ∈ {1.5, 2, 2.5} × impulse window start ∈ {15:30, 15:45, 15:50})
  — net/trade positive in sign in all 9 cells.
- **G7** tails: top-1% of trades ≤ 50% of |net|; no single trade (winner OR loser) > 25% of
  |net|; per-trade distribution + event-loss atlas reported (16:05 mega-cap earnings nights
  identified by date).
- **G8** portfolio: losing-day ρ ≤ 0.25 vs certified Solar B_SYM ledger (2022+ overlap) AND the
  LEVEL functional reported (net on Solar losing days) — a 14-minute flat-overnight exposure is
  structurally near-orthogonal; if the level functional is materially negative the readout must
  say so regardless of ρ.
- **G9** cost stress: G2 and G3-SPLIT must also hold at 2.0 ticks/side + 3× commission.

## Outcomes

PASS-SCREEN → red team (before any candidate freeze, HTFDIR01/LIQREV01 pattern) → if it
survives, portfolio-role study under its own prereg. FAIL → post-close pressure family CLOSED
on this substrate (one shot). Artifacts → `out/`; registry row after readout; seal: substrate
ends 2026-05-29.
