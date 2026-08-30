# OWNER DECISION RECORD — 2026-08-30

**Verbatim owner instruction (chat):** 「确认 M_11 以及让影子开始，并且直接在我ninjatrader
simulation account实盘开始跑」

Three decisions, recorded before any action was taken:

1. **OQ-6 RATIFIED: mapping M_11** (P1/PCT ×1 NQ + XM_CONFLICT_v2 ×1 NQ). Slot D upgrades to
   `EXECUTABLE_PORTFOLIO (M_11)`. Basis: `runs/G2_OQ6_MAPPING_20260830` (trial G00040).
2. **SHADOW START authorized by owner.** Runner to be installed on the owner's machine
   (scheduled task); ledger start boundary stays 2026-09-01 18:00 ET as preregistered — the
   ledger mechanically refuses earlier rows. The shadow's forward reads of ≥2026-09-01 bars are
   the protocol's authorized purpose (seal_guard override token `SHADOW_PROTOCOL_20260901`,
   printed loudly on every use). Bars 2026-08-01..08-31 remain sealed and are NOT pulled.
3. **SIMULATION DEPLOYMENT authorized by owner**: run both certified strategies on the
   NinjaTrader **DEMO8383477 paper account** at M_11 quantities. *(Amended mid-decision by owner:
   「为啥是sim101 dem那个账户也是模拟账户 不能那个账户吗」 — target changed from Sim101 to
   DEMO8383477; account verified paper via GetAccount: connection "Simulation", flat, $0.)* This is a **recorded
   exception** to the standing CLAUDE.md "never touch Sim101 / never enable a strategy" clause,
   granted by the boundary's own mechanism ("explicit recorded owner instruction").
   **Scope granted: Sim101 only. Real accounts remain absolutely off-limits. LIVE (real-money)
   ENABLED remains = NO.**

Execution notes binding on the deployment:
- Strategies: `WeeklyEdgeP1PCT_v1` (base qty 1; internal quality-sizing to 2 as certified) and
  `WeeklyEdgeXMConflict_v2` (qty 1). ⛔ XM **v1 must never run** (holiday defect).
- The narrow CrossTrade research-ban is LIFTED for deployment/monitoring actions only;
  research reads of sealed windows stay banned.
- Sim economics ≠ research economics (NT8 template commission, zero modeled spread) — sim fills
  are an execution-evidence stream, not the research headline.
- NT8 + data connection must be running for both sim and shadow to operate (owner's machine).

## Execution log (2026-08-30, after owner granted CrossTrade permissions)

- NT8 restarted by owner; "Simulation" connection **Connected**; handshake add-on v1.13.9.
- `WeeklyEdgeP1PCT_v1` → `dep_46b904d97604` (id 399550057) and `WeeklyEdgeXMConflict_v2` →
  `dep_01b21182696c` (id 399550058), both on **DEMO8383477 / NQ 09-26 / 1-min**, both verified
  **Realtime, is_trading=true**, flat, 0 orders. XM's ES/RTY/YM series loaded and verified.
- `GENESIS_ShadowRunner` daily 17:10 ET scheduled task registered (next run 2026-08-30 17:10).
- Post-deploy runner check: **0 rows ingested** — historical-bar simulation does not touch the
  account. Watermarks unchanged (584/852).
- Owner follow-up 「他可以直接从下个交易日开始而不是9/1吗」: **trading already starts with the
  next session open (Sun 2026-08-30 18:00 ET)** — nothing was waiting on 9/1. The 9/1 boundary
  governs only the research evidence ledger and was **deliberately left unmoved**; the two
  intervening sessions serve as a plumbing shakedown (details in `PAPER_DEPLOYMENT_20260830.md`).
