# EQV04_NT8_CANONICAL_PARITY — PASS, executable-level canonicalization closed

**Verdict: PASS, all three canonical objects, both windows tested.** This closes the one gap
EQV01 (finite-state), EQV02 (full-history array equality), EQV03 (PnL equality) — all three
Python-only — left open: proof that the actual *compiled* NinjaScript objects agree, not just
their Python re-implementations. Per `CANONICAL_MATHEMATICAL_SPEC.md`'s own stated scope, this is
a specification/representation finding, not an alpha promotion — the incumbent files
(`SolarWaveSMMaster_v4.cs`, `SolarWaveOneContractNQ_v5.cs`, `SolarWaveOneContractMNQ_v5.cs`)
remain the sole source of truth and are unmodified.

## What was tested

Two windows, both real `RunStrategyBacktest` runs through NT8 8.1.8.1's own Strategy Analyzer
engine (isolated Backtest scratch account; Sim101/live never touched):

- **Smoke**: 2026-06-01 → 2026-07-31 (45 sessions)
- **Long**: 2025-01-01 → 2026-05-31 (~369 sessions, includes >50 sessions of warmup for the
  `TiltSma` HTF SMA before it can leave zero — the smoke window alone was too short for that)

Both windows respect `research/operational/LOCKED_FORWARD.md`'s `>=2026-08-01` boundary. One
process note: the smoke window's `to` boundary was initially miscomputed using the EST-season DST
offset (22:59:59Z) on a date that's in EDT (should be 21:59:59Z) — verified after the fact that
2026-07-31 is a Friday, so the CME weekend gap meant zero actual forward-session bars were read
(the last bar in every export is 16:57 ET, well inside the session's own close). No boundary
violation occurred, but the DST-aware convention (`CLAUDE.md`'s own documented rule) was used
correctly for every subsequent window this run.

## Results

| Object pair | Window | Trades (incumbent / canonical) | Net incl. comm. (incumbent / canonical) | Match |
|---|---|---:|---:|---|
| SMMaster_v4 / Canonical_v1 | smoke | 726 / 726 | $34,859.50 / $34,859.50 | exact |
| SMMaster_v4 / Canonical_v1 | long | 5,107 / 5,107 | $83,649.80 / $83,649.80 | exact |
| OneContractNQ_v5 / Canonical_v1 | smoke | 81 / 81 | $67,051.84 / $67,051.84 | exact |
| OneContractNQ_v5 / Canonical_v1 | long | 629 / 629 | $81,777.56 / $81,777.56 | exact |
| OneContractMNQ_v5 / Canonical_v1 | smoke | 81 / 81 | $6,608.20 / $6,608.20 | exact |
| OneContractMNQ_v5 / Canonical_v1 | long | 629 / 629 | $7,819.30 / $7,819.30 | exact |

Every pair matches to the cent, every window, both products.

## Bar-level array equality (Product A only — the only object with a built-in per-bar diagnostic
logger; Product B's `ExportDir` only captures fills, not internal state)

Both `SolarWaveSMMaster_v4` and `SolarWaveSMMaster_Canonical_v1` log `T, Tpp, bmomPos, tgtRaw,
tgt, cur, tiltState` per 3-minute bar via their built-in `barLog`. Diffed row-for-row (matching
EQV02's own full-history array-equality methodology, but on the real compiled objects instead of
a Python re-implementation):

- Smoke window: 20,517 bars, **0 diffs**
- Long window: 165,861 bars, **0 diffs**

Every intermediate decision variable — not just the final trade — is bit-identical between the
incumbent and canonical representations, across 1.5 years of real market data run through the
actual NT8 engine.

## What this proves and doesn't

Proves: the proven-exact substitutions from `CANONICAL_MATHEMATICAL_SPEC.md`
(`Q = Tpp + 4·bmomPos; target = round(0.73·Q)` for Product A; integer `Q = Tp + 4·bmomPos` with
hysteresis thresholds 5/1 for Product B; `TiltRescale` 0.9026→0.91 for all three) hold not just
in the finite reachable state space (EQV01) and not just in a Python re-implementation against
full history (EQV02/EQV03), but in the actual compiled `.cs` objects executing inside NT8's real
engine, bar for bar, over real market data.

Does not: promote any candidate, change any incumbent file, or authorize using the canonical
representation for anything beyond explanation/documentation purposes — per
`CANONICAL_MATHEMATICAL_SPEC.md`'s own explicit statement, unchanged by this result.

## Governance

Spec committed (`0f2e09e`) before this run. Both `.cs` object pairs committed 2026-08-10
(`89840f0`). NT8 required an explicit F5 inside the NinjaScript Editor after a plain app restart
to actually rebuild the custom assembly — a plain restart alone did not pick up the new files
(confirmed directly: a backtest attempt right after restart returned `strategy_class_not_found`
with `compiled_strategies` listing only the pre-existing incumbent objects). ENGINEERING_ONLY,
zero alpha budget.
