# breadth_lab — Binding statistical conventions (campaign #5)

_Frozen 2026-08-19 after BREADTH01's readout, BEFORE any subsequent spec. These bind every
future breadth_lab spec; deviations require a written amendment committed before the spec._

1. **Object class**: diversified multi-asset books (many low-Sharpe streams aggregated).
   Prior per-book Sharpe for anything trend/carry/defensive-shaped: 0.3-0.8. Gate design
   MUST include a written power check against the spec's own prior (BREADTH01 lesson: a
   gate with <60% power under the spec's own prior may not be frozen as PRIMARY).
2. **Era gate for diversified books (replaces raw G3-SPLIT)**: pre/post-2020 era means both
   > 0; first/second-half Sharpes same sign; FULL-period year-block bootstrap CI_lo > 0;
   neither era CI_hi < 0. Era-level significance is NOT required (power arithmetic:
   era Sharpe ≥0.49-0.79 would be needed — selects against the object class itself).
3. **Complementarity is the campaign's reason to exist**: every spec carries the G5 gate
   (ρ_full ≤ 0.25 AND Solar-losing-day ρ ≤ 0.25 AND book return on Solar losing days ≥ 0)
   against the concatenated Solar E10 ledger — WITH a mandatory scale-consistency audit of
   the hist/dev ledger join before first use in any adjudicated gate.
4. **Data**: free public sources allowed (owner grant 2026-08-19); every file sha256'd in a
   MANIFEST with source URL and download timestamp; analysis mask ≤2026-05-31 (aligned with
   the house dev mask); post-mask data stored unread as the book's forward window.
5. **One-shot closures are construction-scoped**: a closed construction may never be
   re-skinned (universe/horizon/parameter variants count as re-skins). New specs need a
   genuinely different MECHANISM. Instrument-level re-adjudication of closed leads is
   exhausted program-wide (ATRPOOL01 precedent, applies here too).
6. **Zero-fitted-parameter replications preferred**: every constant literature-sourced or
   deterministic; any author-chosen constant must be named, justified, and counted in the
   spec's multiplicity.
7. Registry: `REGISTRY.csv` (one row per spec/readout); prereg_guard applies to every
   inference-bearing run; specs committed before readouts, results committed after.
