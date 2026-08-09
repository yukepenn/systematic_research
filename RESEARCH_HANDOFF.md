# RESEARCH_HANDOFF

Read this before starting any new research wave. Kept short on purpose — see
`BASELINE_MODELS.md` / `CURRENT_TRUTH.md` for full detail.

```
CURRENT MODE: RESEARCH
```

## Current baselines

- **Product A**: `src/ninjascript/SolarWaveSMMaster_v4.cs`
- **Product B-NQ**: `src/ninjascript/SolarWaveOneContractNQ_v5.cs`
- **Product B-MNQ**: `src/ninjascript/SolarWaveOneContractMNQ_v5.cs`
- Canonical source: **`BASELINE_MODELS.md`** (repo root)

## Engineering / parity: CLOSED

A shared NinjaScript defect (hardcoded-clock BMOM end-of-session flatten) was found via
live-NT8 event-level forensics, fixed with a one-line non-signal change, and independently
re-verified against real NT8 output: leg-by-leg exact (0/214 divergent legs) on a Q1-2025
spot-check window, and trade-count exact to ±1 across all 7 chunks spanning the full 4.5-year
canonical history (not leg-verified beyond Q1-2025). Remaining open items are precision, not
correctness: Product A's full-history net-profit residual (+10.91%) is directionally consistent
with two already-disclosed, non-defect conventions (1-tick fill difference, NT8's documented
boundary-serialization quirk), same as BEST_ONE_NQ/MNQ's fully-dollar-reconciled residuals
(+4.13% / +4.41%) — but Product A's has not been reduced to an exact leg-level proof the way
the one-contract objects' have. See `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`.

## Do not reopen unchanged

- **S2_SELTIME's exact frozen rule** (block new commitments/reversals 02:00-08:00 ET) — fully
  adjudicated, NOT PROMOTED for all 3 objects (`runs/S2_SELTIME/R2_*.md`). A materially different
  time/session hypothesis (session-state transition, liquidity-conditioned timing, continuous
  eligibility instead of a binary clock window, time-of-day × signal-strength interaction) is a
  new hypothesis and may be studied — but do not disguise the same clock-window rule with a
  slightly shifted boundary and call it new.
- The 8 named FINAL OPTIMIZATION DIRECTIVE families (S0/S1, M3, M4, A1/A2/A3, P4, D-WINNER) and
  the Engine-3 cross-market slate (15/15 cumulative failures, axis exhausted) — all closed with
  disposition, see `research/registry/tested_configs.csv`. A genuinely new mechanism or data
  source may reopen an axis; an unchanged parameter grid may not.

## Highest-value open research axes

1. Materially new time/session selectivity mechanisms (not a re-run of S2's exact rule).
2. Trade timing / delayed-entry / confirmation mechanisms.
3. Hold / exit / give-back mechanisms (D-WINNER's disclosed-but-not-pursued duration-conditioned
   profit give-back candidate is a starting point, not a preregistered result).
4. Microstructure / order-flow information.
5. Volatility / liquidity state conditioning.
6. A genuinely orthogonal Engine #3 (new data source or new mechanism class required).
7. Execution-aware alpha that changes expected net edge, not just cost accounting.

## Research workflow (standing rule)

```
NEW IDEA
    -> preregister mechanism + falsification criterion
    -> Python fast research screen
    -> candidate survives
    -> EARLY representative-window NT8/CrossTrade executable parity check
    -> chronology / bootstrap / tail / drawdown / capital battery
    -> promotion decision
    -> final full-history executable certification
```

Python stays the research engine. NT8 stays executable truth. The point of the early parity
check is to catch executable divergence WHILE a candidate is still cheap to fix or drop —
not after a full campaign has been built around it. This is the direct lesson of the parity
debt just closed: the defect existed from the start but wasn't caught until certification was
attempted long after the fact.
