# NINJATRADER_PARITY — status ledger (compilation ≠ parity)

_2026-08-08. Rule: nothing is "executable parity-complete" until a Strategy Analyzer
run reconciles trade-by-trade against the canonical Python replay._

| object | build | compile | Analyzer parity | notes |
|---|---|---|---|---|
| E10Master_v2 (Solar graded, F1) | ✅ | ✅ | ✅ (V1: GATE_C corr 0.9999968, fills exact 8/13 members, rest boundary-only) | the parity-certified base |
| SolarWaveSMOneLot_v1 (SM14) | ✅ registered | ✅ clean (in-memory vs live AppDomain) | ❌ **PENDING** | blocked on owner F5 rebuild; then RunStrategyBacktest + reconcile vs `runs/SMV2A_DD_RECONCILE` canonical replay. Expected deltas to investigate: ops-window micro-semantics (KNOWN_ERRORS #1) |
| DAYONLY_DUAL6040 master | ❌ spec only | — | — | NINJATRADER_MASTER_SPEC.md + tilt/short-halving delta; queued #3 |
| SolarWaveSMOneLot_v2 (A-dominant challenger) | not built | — | — | build only after SMV2H2 confirmation gate |

Parity report format (frozen): python trades vs NT trades, matched count, signal
mismatches, fill mismatches, daily corr, max |daily Δ|, net Δ — per directive §32.
