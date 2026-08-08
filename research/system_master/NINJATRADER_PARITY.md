# NINJATRADER_PARITY — status ledger (compilation ≠ parity)

_2026-08-08. Rule: nothing is "executable parity-complete" until a Strategy Analyzer
run reconciles trade-by-trade against the canonical Python replay._

| object | build | compile | Analyzer parity | notes |
|---|---|---|---|---|
| E10Master_v2 (Solar graded, F1) | ✅ | ✅ | ✅ (V1: GATE_C corr 0.9999968, fills exact 8/13 members, rest boundary-only) | the parity-certified base |
| SolarWaveSMOneLot_v1 (SM14) | ✅ registered | ✅ clean | ✅ **PASSED 2026-08-08** (see below: 99.5% trade-exact, net Δ 0.13%) | canonical replay = `runs/SMV2H_ONECONTRACT/parity_d.py` |
| DAYONLY_DUAL6040 master | ❌ spec only | — | — | NINJATRADER_MASTER_SPEC.md + tilt/short-halving delta; queued #3 |
| SolarWaveSMOneLot_v2 (A-dominant challenger) | not built | — | — | build only after SMV2H2 confirmation gate |

Parity report format (frozen): python trades vs NT trades, matched count, signal
mismatches, fill mismatches, daily corr, max |daily Δ|, net Δ — per directive §32.


## 2026-08-08: SolarWaveSMOneLot_v1 — Strategy Analyzer parity PASSED (Track D)

Full dev window 2022-01-01 → 2026-05-29, NQ 09-26, 3-min, slippage 1 tick, Lifetime
commission, engine = NT8 8.1.8.1 RunBacktest (bit-identical to Strategy Analyzer UI).
Reconciled vs the canonical Python replay (`runs/SMV2H_ONECONTRACT/parity_d.py`):

| metric | value |
|---|---|
| Python trades / NT trades | 1,978 / 1,975 |
| matched on entry-time+direction | **1,965 (99.5%)** |
| entry price exact on matched | **100.00%** |
| exit price / PnL exact on matched | 99.59% |
| daily corr (session attribution) | 0.9990 |
| net delta | **−$402 on $303.9k (0.13%)** |
| max abs session delta | $3,126 (window-end boundary) |

Residual mismatches (10 NT / 13 PY unmatched): ALL cluster on US holiday early-close
sessions (Presidents' Day 2022/2025, Thanksgiving 2023, Memorial Day 2024, Dec 2024,
Juneteenth 2025, July 4 2025, MLK 2026) — session-template differences between the
exported research substrate and NT8's live calendar — plus the final session where the
NT data window ends earlier. Same character as the V1 E10 GATE_B boundary diffs.
Timestamp convention note: NT stamps fills at the fill bar END; research convention
stamps the fill bar OPEN (constant 3-min offset, prices identical).

**Status upgrade: SolarWaveSMOneLot_v1 = EXECUTABLE, ANALYZER-PARITY-VERIFIED.**
(The strategy type resolved in the live AppDomain, i.e., it is present in the NT8
Strategies list now.) NT run artifacts: `runs/SMV2H_ONECONTRACT/out/nt_trades_full.csv`.
