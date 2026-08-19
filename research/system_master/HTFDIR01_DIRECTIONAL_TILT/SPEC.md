# HTFDIR01 — Direction-conditioned HTF tilt construction (FROZEN SPEC)

**Committed BEFORE any candidate result is read** (prereg_guard discipline: this spec commit
strictly precedes the results commit). Date: 2026-08-18. EVI rank 1 actionable item per
`ACTIVE_RESEARCH_QUEUE.md` (2026-08-14 re-rank, rank 2 overall behind the completed HTFMECH01).
This consumes ONE alpha hypothesis.

## Motivation (all pre-existing, none computed for this spec)

Three independent, committed diagnostics point the same way:
1. **PLACEBO01** (2026-08-10): HTF's real marginal contribution sits at the 27.8th–32.1st
   percentile of its own randomized-chronology null — below the null median for BOTH products.
2. **HTFMECH01** (2026-08-14): that underperformance is direction-concentrated — the agreement
   up-weight is value-additive on longs and value-destructive on shorts (Product A short-side
   marginal −$22,020, >3.5× the whole-window net positive marginal).
3. **SA0/PA0/PA1** long/short asymmetry findings (independent method, same direction).

## Candidate (exactly one; zero new tuned constants)

In both executors the tilt enters as
`m_arr = TILTMULT where sign(T)==tilt_state (both nonzero) else 1.0` (symmetric).

**ARM_LONGONLY** replaces this with:
`m_arr = TILTMULT where (T > 0) & (tilt_state > 0) else 1.0`
i.e. the ×TILTMULT up-weight applies ONLY on long-side agreement; short-side agreement gets 1.0.
Everything else is byte-identical: TILTMULT, TILTRESCALE, SHORTHALF (Product A's separate
disagreement overlay, untouched), KSOLAR/KBMOM, WSOLAR/WBMOM, hysteresis levels, C4 overlay,
cost model (certified comm + 1-tick fills), execution loops (`solve_A`/`solve_B` verbatim from
PLACEBO01/HTFMECH01).

**ARM_SHORTONLY (mechanism-falsification control, NOT a promotion candidate under any outcome):**
`m_arr = TILTMULT where (T < 0) & (tilt_state < 0) else 1.0`
Pre-registered prediction: underperforms the incumbent on both products. If ARM_SHORTONLY
*passes* G1 on either product, the mechanism story is confounded and the wave verdict is capped
at MECHANISM_UNCLEAR regardless of ARM_LONGONLY's numbers.

Disclosed non-decision: TILTRESCALE was calibrated under the symmetric tilt. It is deliberately
NOT recalibrated (zero-degrees-of-freedom principle). Any future recalibration would be a new,
separately preregistered hypothesis.

## Substrate & verification gates (must pass before any candidate number is trusted)

- `grid_core` (GRID01 certified substrate): import self-check must PASS (reproduces certified
  dev nets $177,924.40 / $301,915.92 within $1).
- Local `solve_A`/`solve_B` (copied verbatim) must reproduce grid_core's own full-array
  execution to $0.01 on the dev window (HTFMECH01 gate #2 pattern).
- Data ends 2026-07-31 (already research-consumed era); **nothing ≥ 2026-08-01 is touched.**

## Windows

- **PRIMARY: dev 2022-01-03 → 2026-05-29** (grid_core DEV_MASK). All gates evaluate here.
- Secondary, labeled, non-promotional: 2026-06-01→07-31 extension (research-consumed;
  CURRENT_EDGE_HEALTH precedent) and the canonical 2023-01→2025-02 sub-window.
- TRANSITION/HISTORICAL 3-minute substrate does not exist in grid_core; disclosed limitation
  (same as every prior wave on this substrate).

## Frozen gates (ARM_LONGONLY vs incumbent, per product; Δ = candidate − incumbent)

- **G1 economics**: P(ΔSharpe > 0) ≥ 0.85, day-clustered bootstrap on daily nets, **10,000
  reps** (B1 under-convergence lesson), seed 20260818, per product (A and B-NQ separately;
  B-MNQ shares the decision core and is reported, not separately gated).
- **G2 chronology**: (a) LOYO — Δ(dev Sharpe) with each calendar year dropped stays ≥ 0 in
  every fold; (b) the 2022–2025-only Δnet must be ≥ 0 (R2's 2026-stub-artifact failure mode is
  an explicit FAIL condition even if the full window passes).
- **G3 right tail**: top-10 winning-day dollar retention ≥ 95% per product; per-day table of
  the top-20 winners reported.
- **G4 tail risk**: CDaR₀.₉₅ must not worsen by more than 2%; EOD maxDD reported (no gate,
  disclosed).
- **G5 mechanism control**: ARM_SHORTONLY must not pass G1 on either product (see above).
- **G6 conventions**: Product A scored under BOTH O1 aggregation conventions
  (mixture and Γ-minimax, `primary_objective_v2`); if the verdict flips between them the
  objective line is INCONCLUSIVE and may not be quoted as one number (R3 fallback, binding).
- **G7 recency honesty**: 2026 Jan–May Δ point estimate reported; if the ENTIRE full-window Δ
  is attributable to the 2026 stub (where the incumbent reference is itself degraded —
  Wave-19), the pass is flagged LOW-POWER-VS-DEGRADED-REFERENCE.

## Outcomes (frozen)

- **PASS-SCREEN**: all of G1–G7 clean on ≥1 product → the candidate advances to a SEPARATE,
  separately-preregistered promotion step: NT8 executable build + early representative-window
  parity + the full promotion battery. **No promotion in this wave under any result.** Product-A
  promotion additionally subject to the EXEC01 floor (Python-only improvement < ~$430/0.24%
  cannot promote on Python evidence alone).
- **FAIL**: any gate fails on both products → the direction-conditioned tilt family is CLOSED
  (one shot; no re-tuning of this construction; a materially different HTF hypothesis needs its
  own new preregistration).
- **MECHANISM_UNCLEAR**: G5 trips → family parked, no construction retry without a new
  diagnostic first.

## Bookkeeping

Artifacts → `out/` (results JSON, daily ledgers, bootstrap draws summary, LOYO table).
Registry: one family row appended to `TESTING_LEDGER.csv` after readout. CURRENT_TRUTH +
ACTIVE_RESEARCH_QUEUE updated after readout. Seal audit (`seal_audit.py`) run over the run
artifacts before the results commit.
