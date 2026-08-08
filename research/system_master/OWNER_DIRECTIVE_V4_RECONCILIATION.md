# Directive V4 → repository reconciliation (2026-08-08, HEAD d3c62e5)

V4 received same day as V1/V2 (owner numbering skips V3). Per V4 §4: repository wins on
any numeric disagreement. This page maps V4's priority stack onto committed evidence so
completed work is NOT rerun.

## §5 object board — VERIFIED against HEAD, no corrections needed
SOLAR_E10 / SOLAR_DUAL_HTF / BMOM_E2 / DAYONLY_DUAL6040 (champion candidate, master
parity NOT yet run) / SM14_ONELOT (FINAL holder, parity PASSED) / A_DOMINANT_ONELOT
(challenger, gate narrowly missed under a mis-specified gate — KNOWN_ERRORS #5) /
B1_OVERNIGHT (demoted). Matches CURRENT_TRUTH.md exactly.

## §52 priority stack vs completed artifacts
| V4 item | status at d3c62e5 | evidence |
|---|---|---|
| P0 repo reconciliation | DONE (this page + V2 truth layer) | CURRENT_TRUTH, CLAIM_LEDGER |
| P0 one-lot NT8 parity | DONE — PASSED 99.5%/100%/Δ0.13% | NINJATRADER_PARITY.md, SMV2H out/nt_trades_full.csv |
| P0 consolidated DAYONLY master + parity | **OPEN → wave-2 Track M** | NINJATRADER_MASTER_SPEC.md exists, no v2 build |
| P0 vol-match causality audit | DONE (frozen dev-static constants; no leak) | DR_V2_PASS_C P2 local check |
| P1 one-contract confirmation | **OPEN → SMV2H2 (spec frozen this commit)** | queue #1 |
| P1 one-contract DD attribution | DONE (top-10 autopsy) | SMV2H out/sm14_dd_autopsy.csv |
| P2 top-DD decomposition | DONE for PORT/OneLot/Solar | SMV2A decomposition_ladder.csv |
| P2 CDaR/EDaR/Ulcer frontier | **OPEN → SMV2I C-P1** | spec frozen this commit |
| P2 winner-drought diagnostics | OPEN (queue #5, after SMV2I) | — |
| P2 common-regime attribution | OPEN (later wave) | — |
| P3 VR / path-efficiency states | **OPEN → SMV2J (B-H1+B-H3 first)** | spec frozen this commit |
| P3 Kalman/entropy/BOCPD | queued behind SMV2J outcome | DR_V2_PASS_B sequencing |
| P4 Engine #3 first slate | **OPEN → SMV2K (A-H1, A-H3, A-H5)** | spec frozen this commit |
| P5 ML | gated behind P3 state evidence (V4 §30 ladder) | — |
| P6 weight frontier | partially DONE (rerank 80/20..50/50); CDaR-LP refinement in SMV2I | SMV2H rerank_portfolios.csv |

## Wave-2 execution plan (parallel, isolated run dirs, registry centralized)
- **SMV2H2** `runs/SMV2H2_ONELOT_CONFIRM/` — R2 CONFIRMATION, seq 358-360.
- **SMV2I** `runs/SMV2I_CURVE_READS/` — PORTFOLIO TEST + DIAGNOSTIC, seq 361-365.
- **SMV2J** `runs/SMV2J_STATE_HARNESS/` — DIAGNOSTIC (JOB1 information only), seq 366-367.
- **SMV2K** `runs/SMV2K_ENGINE3_S1/` — R1 FAMILY TEST, seq 368-370.
- **Track M** DAYONLY_DUAL6040 NinjaScript master build + Analyzer parity (no new alpha:
  Stage 4 implement of frozen components; parity per V4 §16 targets).

All specs frozen and committed BEFORE any read. Red-team pass mandatory per track before
any doc/claim update. Gates preregistered inside each spec; no gate moves after reads.
