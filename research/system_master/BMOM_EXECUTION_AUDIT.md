# BMOM_EXECUTION_AUDIT — causal fill audit of the frozen W8-1 rule (SMV2B, seq 320-323)

_2026-08-08. Signals untouched (validated 1,333/1,333 against the frozen generator);
only fill timing/price varied. Dev 2022-01-03 → 2026-05-29, 1 NQ.
Code: `runs/SMV2B_BMOM_EXEC_AUDIT/smv2b.py`; ledgers in out/._

## Verdict: **PASS — the edge is NOT an execution artifact.**

| arm (C1 friction 2.872t/RT) | net | Sharpe | Sortino | Calmar | maxDD | worst mo | PF | avg t/trade |
|---|---|---|---|---|---|---|---|---|
| E0 signal-close (old convention) | $319,123 | 1.313 | 1.99 | 1.79 | −$43,325 | −$20,226 | 1.215 | 47.9 |
| **E2 next-3m-bar open (fully causal)** | **$319,198** | **1.314** | 1.99 | 1.80 | −$43,180 | −$20,176 | 1.215 | 47.9 |
| E3 = E2 + 1 tick/side | $305,868 | 1.258 | 1.90 | 1.71 | −$43,340 | −$20,476 | 1.205 | 45.9 |
| E4 = E2 + 2 ticks/side | $292,538 | 1.202 | 1.81 | 1.63 | −$43,500 | −$20,776 | 1.195 | 43.9 |

- Per-trade fill drift (E2 − E0): **mean +0.01 ticks, median 0** (p10 −3t / p90 +3t,
  symmetric). The old signal-close convention was not flattering the rule; breakout
  crossings have symmetric next-open drift on this substrate.
- Frozen gate: E2 Sharpe 1.314 ≥ 0.6×E0 (0.788) ✓; net > 0 ✓; block-bootstrap
  P(daily mean > 0) = 0.998 ✓. All four arms pass; degradation under slip stress is
  graceful and monotone (−0.056 Sharpe per tick/side).
- At the ACTUAL NQ Lifetime commission (0.872t/RT, cheaper than the C1 stress basis
  the ledger was frozen on) E2 = $332.5k / Sharpe 1.370.
- Execution reality (grid1s L1 subsample, 2025-08→2026-05): modern NQ RTH spread is
  **~3 ticks median**, so a market order pays ≈1.5t vs mid per side. **Realistic live
  basis ≈ between E3 and E4** — plan on Sharpe ~1.20-1.26 standalone, not 1.31.
- Annual: every dev year positive in all arms (2023 weakest: $22.8k at E4; 2022/2025
  strongest ~$94-110k). Concentration: top-1% of trades = 56-63% of net — the engine
  is right-tail dependent (known; right-tail gate remains mandatory).

## Canonical basis change (rule-preserving, no retuning)
**E2 (next-bar-open) is now the canonical B-MOM execution convention** for every
downstream object; E3/E4 are the standing stress bands. NinjaScript implementations
already fill on next bar (OnBarClose → market order) — i.e., **the NT8 implementation
was already E2**; research now matches it exactly.

## Portfolio impact — none material (no grandfathering needed)
PORT_TILT_532 recomputed with the E2 leg (frozen scales AND rule-recomputed vm scale):
net $205.1k, Sharpe 1.22, maxDD −$27.2k — identical to the E0-based result to 3 digits.
With E3 stress: Sharpe 1.20, maxDD −$27.5k. `out/port_impact.csv`.

## Claim-taxonomy update
BMOM: RECENT_REGIME INDEPENDENT-ENGINE CHALLENGER — **execution audit PASSED**
(the "pending realistic causal execution audit" qualifier in Directive V2 §2 is
now resolved). Remaining risks unchanged: regime-locality (no pre-2022 structure,
W10) and right-tail concentration; SM13 decay rule stands.
