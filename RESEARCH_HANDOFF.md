# RESEARCH_HANDOFF

Read this before starting any new research wave. Kept short on purpose — see
`BASELINE_MODELS.md` / `CURRENT_TRUTH.md` for full detail.

```
CURRENT MODE: RESEARCH
```

> **UPDATE 2026-08-09 (latest) — Master Directive v3 / Wave 4 CLOSED.** Waves 1-3 of the
> CONTINUOUS SYSTEM EVOLUTION phase closed 22 research artifacts (`U0/U2/H0/U1/U3/U4/U5/U6/U7/
> U4B/SHADOW01/U1B/U6B/U8/U9/U9B/U8B/LEV01/LEV02/SKEW01/PORT01/EXP01`); see
> `research/system_master/CONTINUOUS_EVOLUTION_WAVE3_SYNTHESIS.md`. Wave 4 corrected a governance
> error (many prior closures are transforms of the SAME NQ_OHLCV path, not independent proofs) and
> ran 18 more artifacts to completion: SPEC01 (not a defect), PRICE01 (Product-A genuine-MNQ
> dual-truth infra), the O1/O2 owner-utility framework (built and run on real data for the first
> time — `U6B_PRODUCT_A_SCALE_RATE` strengthened, not promoted), ADD01/WIN01/SOFT01/VAR01/REL01
> (all closed negative/null with good discipline), GAMMA00 (literature+data feasibility, spun off
> MOM01), and the full multimodal-microstructure addendum (DATA02/DOM01/ICT01-02/FLOW01/
> AUCTION01/COMBO01) — AUCTION01's causal running-POC concentration/distance state is the one
> genuinely new, confound-checked finding, flagged for a future construction. **Zero promotions
> this wave. Both baselines unchanged.** Full synthesis:
> `research/system_master/CONTINUOUS_EVOLUTION_WAVE4_SYNTHESIS.md`. Do not re-run any closed
> family unchanged; this phase has no stop condition.
>
> **UPDATE 2026-08-09 (later same day) — CONTINUOUS SYSTEM EVOLUTION phase OPEN, wave 1 CLOSED.**
> Per the owner's follow-on directive, research does not stop at zero promotions -- it continues
> via an EVI-ranked loop. Wave 1 (`U0` shared state infra, `U2` data audit, `H0` Product-A health,
> `U1` session heterogeneity, `U3` hold/exposure, `U4` short mechanism, `U5` soft weighting, `U6`
> Product-A path-dependence, `U7` 2026-regime explanation, plus `U4B`, the top-EVI follow-on
> construction) is CLOSED, zero promotions, both baselines still UNCHANGED. Synthesis + EVI
> ranking of what's next: `research/system_master/CONTINUOUS_EVOLUTION_WAVE1_SYNTHESIS.md`. Full
> navigation: `research/system_master/RESEARCH_FRONTIER.md`. Do not re-run any of these families
> unchanged. Superseded by nothing -- this phase has no stop condition; see that synthesis doc
> for the next queued hypothesis.
>
> **UPDATE 2026-08-09 — SYSTEM ARCHITECTURE SCIENCE + ALPHA OPTIMIZATION campaign CLOSED, same
> day, after this file's original text below.** SA0 (full structural/failure-mode decomposition),
> R3 (SelTime-as-state), R2B (pullback-reclaim), R4 (slope/impulse), R5 (OHLCV microstructure
> proxies), R6 (Engine-3 audit), PA0/PA1 (Product A structure/sizing) all closed, zero
> promotions. Closing report: `research/system_master/SYSTEM_SCIENCE_20260809.md`. Current-regime
> health: `research/system_master/CURRENT_EDGE_HEALTH.md` (Product B HEALTHY, no decay evidence).
> Do not re-run any of these 7 families unchanged — see `research/system_master/
> RESEARCH_FRONTIER.md` for exactly what's closed and what (if anything) is left as a disclosed,
> deferred lead for a future wave. The rest of this file (below) is the PRE-this-campaign state,
> retained for history, not current status.

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
