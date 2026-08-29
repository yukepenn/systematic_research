# GENESIS INCUMBENT DOSSIER — P1/PCT and XM under a hostile reading

**State document.** From `runs/GENESIS_W1_FORENSICS_20260828` (C1/D1/J1). The incumbent must win
against the reboot, not inherit the throne; this dossier is the case file.

## 1. What P1/PCT actually is (C1, all file:line-verified)

32-voter ensemble (4 member-sets × throttles {none,.7,.8,.9} × delta-gate on/off) with closed-form
arming `nMemLong·nThr·(1+dL) ≥ 16` (`WeeklyEdgeP1PCT_v1.cs:452`); hysteresis M≥3.0 entry / ≤1.0
exit where `M = 0.7086·Tp + 2.83·bmom` — the "OR-gate with B-MOM" is really this additive term.
Frozen params at `.cs:179-187` (VolPeriod 460, 13 ratchet members VolMult 6..30, S clamp [40,1200]
ticks, entry block 30 min, forced flat 21 min, per-contract box −$1,300/+$1,000, quality sizing
size-2 at score≥3 over trailing-250-entry quantiles). Generating path:
`load_deep → mem_ext.npz → w97 votes → w26 fills (size-1 schedule feeds the causal score) →
w37 causal_score → w98 gfills → w103 economics`. XM: 09:45-vs-09:31-open drive, ES/RTY/YM 60-day
z-composite conflict filter, 09:46→15:45/15:46, no stop; three N's reconciled (342/348/346).

## 2. The honest economics band (J1)

| reading | value | why |
|---|---|---|
| recorded headline | $1,230.36/wk fixed-DD | `WE_W103_CONSOLIDATE/out/components.csv:2`, arithmetic verified |
| bucketing-honest band | **$1,166–1,230/wk** | week-bucketing convention swings maxDD 5.6%; chosen convention is the flattering one |
| selection-deflated floor | **~$885/wk** | the +39% ABS→PCT step is p≈0.058 — "dollars not established" |
| deserved quote | **$900–1,230/wk, in-sample, post-selection** | four unreconciled trade populations (2,401/2,139/2,137/2,131) |
| drawdown | maxDD **$29,454 trade-level** vs $22,931 weekly | the fixed-$20,245 normalization uses the coarsest DD series |
| forward risk | P(13-wk loss) = 14.5% | repo's own bootstrap |

Evidence class DISCOVERY_CONSUMED is correctly tagged. **Nothing about the incumbent is forward
evidence yet**; the shadow (start 2026-09-01) is the first non-consumed class it will ever have.

## 3. Execution reality (D1) — ranked weakest assumptions

1. **Spread external validity — now MEASURED (G2_EXEC01, 2026-08-28 late): the model is
   OPTIMISTIC.** Contract-weighted mean **$20.65/ctrRT** on 131 ctrRT with both legs inside real
   quotes (5.1% overlap, double the prior 35-fill evidence); W82 model on the same RTs = $15.00.
   Impact ≈ **−$70/wk raw** (fixed-DD ≈ $1,168 vs $1,230). Era cut: 2025H2/2026H1 ≈ $17.12,
   **2026 Jun–Jul $28.69** (WATCH in shadow). P1 fills in cheap minutes; the overrun is at fill
   instants. +1-min delay −$90/wk (n.s.); passive entry available 0.7% of the time.
   *(Supersedes: "bounded at $24.00/RT on 35 fills". XM's spread remains unmeasured — same audit owed.)*
2. **Bar-open zero-impact fills** are shared by BOTH parity sides — parity cannot detect this
   error class by construction.
3. **No intrabar risk control in any certified object** — no per-trade stop (P1), none at all
   (XM); the session box only accumulates realized P&L; intrabar MAE unbounded. Any future stop
   invalidates the Standard-fill parity basis (`LIVE_READINESS.md:163`).
4. Session-split-by->60-min-gap heuristic silently splits halted days and grants flat exits at
   pre-gap closes.
5. The new multi-market lane assumes 1-tick spread for all roots with zero quote evidence — the
   same transportability error W82's amendment withdrew for NQ.

Uniform fill contract otherwise: decision at bar-close i → fill at bar i+1 open, zero slippage,
commission $4.36/ctrRT everywhere current; NT8 parity is decisions + commission-only (−1.05% net,
8 unresolved early-exit residuals, 2022-12→2023-01).

## 4. Reproduction result (Wave 2 — `runs/GENESIS_REPRO_INCUMBENT_20260828`, PASS)

**R-1 ✅** pipeline reproduces `components.csv` to machine precision (raw $1,393.573663/wk Δ 0.0;
fixed-DD $1,230.356720 Δ 0.0; maxDD Δ 3.6e-12; t Δ 8.9e-16) — **headline upgraded RECORDED CLAIM →
REPRODUCED FACT** (about a backtest; DISCOVERY_CONSUMED unchanged). Caveat: cache-concordance mode
(`mem_ext.npz` used as recorded, not rebuilt from scratch).
**R-2 ✅** four populations reconciled programmatically: 2,401 warm-up-inclusive · 2,139 entry-ts ·
2,131 session-start · 2,137 NT8-parity-under-entry-ts. ⭐ New: the recorded parity "+6" gap was
**window-filter asymmetry**; true engine disagreement **0.09%** either way.
**R-3** honest band unchanged: **$900–1,230/wk in-sample post-selection** — reproduction removes
arithmetic doubt, not selection debt.
**R-4 ✅** baselines B0–B6 exist (`runs/GENESIS_BASELINES_20260828`): the incumbent dominates every
trivial rule (t 4.16 vs best 2.19; 3.5× at common DD). Best control is momentum-side ORB (t 2.19) —
see scoreboard.
