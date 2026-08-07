# Campaign State

_Last updated: 2026-08-06 (Phase 1 complete)_

## Current phase
**DISCOVERY WAVE 1 (user directive 2026-08-06):** historical-research-only (NO live-sim/paper/forward-monitoring ever unless explicitly requested); 2025-03→2026-07 reservation REMOVED; research universe = all data 2022-01→2026-07-31; selection standard = strong robust full-history economics + per-year stability + neighborhood plateaus. SW02a gate PASSED (no fill artifact; 16:30 exit dominates — see research/02_solar_refinements/SW02a_report.md). Full-history canonical reference: net $259,102 slip-0 / ~$162k analytic slip-1, 10,182 trades, PF 1.060, DD −$51,898, positive every year 2022–2026 (2026 thin: $11.19/trade). Wave-1 sweeps running: S1 spatial 28, S3 temporal 18, S2 timeframes 6, S4 signal types done (T1 best after costs; unconditional T2 cost-fragile as thesis predicted).

## Frozen baseline (unchanged)
SolarWaveRKReplicaV0 · T1 · 90/179/5/10/true/10 · 1m Last · NQU6 · Lifetime · canonical window. slip0 $146,440.60 / slip1 $118,645.60 (avg $40.83, PF 1.106). Source sha `221d1e13…`, ledger `fe395c14…`.

## Completed
- PARITY — PASS. SW00 — PASS (research/00_truth/SW00_report.md).
- **SW01c** — gate PASS, thin: 2022 slip1 +$11,385.72, PF 1.012, DD −$44,821; shorts carried (PF 1.071), longs $0.00.
- **SW01b** — null REJECTED p=0.0323 (entry timing ≈ +$90k over median null); machinery alone = 30/30 positive, median $58.6k; hold-to-close random = zero-mean. Instrument: SW01bRandomEntryV1.
- **SW01** — PASS: byte-identical bar ledger (`237203AB…`, also the pre-roll close archive), 100% entry-signal integrity. Findings: 46% of Type-1 signals untaken; chop-veto inverted (4+ flips = PF 1.303 best bucket); eff_120≤0.035 quartile = 25% of trades netting +$157; high-vol tercile = 58% of net.
- **External review** (research/01_diagnostics/external_review.md): P(12-mo forward > 0 at 1-tick) ≈ 35–55%; P(true alpha) 10–20%; session-close fill artifact is the #1 falsifiable risk.

## Active / next
1. **SW02a_TIMED_EXIT_FALSIFICATION (priority 1, spec before run):** variant strategy with explicit timed market exit; ladder 16:58/16:55/16:45/16:30; H-005 registered. Kills or validates the absolute edge.
2. Then SW02 (catastrophe stop + session-close counterfactual, using SW01 tags), SW03 (re-entry, opportunity set = the 46% untaken signals), redesigned SW05 (low-efficiency veto, threshold frozen at dev Q1=0.035, CPCV-tested).

## Protocol upgrades adopted (from external review; binding on all future experiments)
- Archive per-config **daily P&L vectors** in every sweep (CSCV/PBO needs the T×N matrix).
- **CPCV over monthly blocks** replaces 18/6 WFO; per-fold indicator warm-up preregistered.
- Promotion gates add: **PSR (empirical skew/kurt) + Harvey-Liu bracketed haircuts (N∈{10,100,1000})**; state-dependent slippage overlay (2 ticks close/ETH, 5–10 event windows); targeted 2–4 tick stress on close-bucket fills.
- **2025-03→2026-07 reserved** as the only vendor-clean OOS window — single preregistered read, late in campaign.
- Bar archive before September roll: DONE (sw01_bar_ledger.csv). Tags pushed to GitHub.
- MNQ live-sim shadow fills: REQUIRES EXPLICIT USER AUTHORIZATION (outside backtest boundary) — parked.

## Tested-config count
Candidate search-space configs: **1**. Instrumentation/null runs (seq 0): 48 sweep iterations + 2 exporter runs + probes, all registered.

## Compute
32 backtest jobs + 2 sweeps (45 iterations) + 2 export runs; ~9 min engine time total. External review: 6 agents, ~310k tokens.

## Unresolved integrity issues
None. Benign notes: exporter emits 737,707 of 737,708 bars (boundary bar); stop-distance undefined at trend-start bars (trailing stop NaN at episode birth).

## Next highest-value action
Write SW02a spec + `SW01cTimedExitV1`-style variant (new class), preregister the collapse gate, run the 4-rung ladder (Tier-2 full payloads, slip 0 and 1), decide. Everything downstream (SW02/SW03/SW05 designs) is already staged on SW01 outputs.
