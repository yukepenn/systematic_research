# NinjaScript parity plan (Phase 10 done; Phase 11 OWNER-GATED)

## Phase 10 — ports written (2026-08-23)

- `src/ninjascript/OriginalTraderSolarSelTime_v1.cs` — OTR-S-CAND1 (Solar engine
  byte-identical to certified SolarWaveOpenV1; wrapper = T1+T3 entries, reverse-on-flip,
  SelTime 04:00–16:00 force-flat, touch-exit). Research-only: self-terminates in realtime.
- `src/ninjascript/OriginalTraderVolumeVWAP_Proxy_v1.cs` — Track-V PROXY candidate
  (prev-hour static volume-percentile ladder, EMA20 trend, C2 not-extended gate, median
  exit). Clearly labeled PROXY; self-terminates in realtime.

Not yet compiled: compilation requires the NT8 environment.

## Phase 11 — parity execution is BLOCKED on an owner decision

Directive §1.7/§39 excludes CrossTrade from this campaign entirely, and CrossTrade MCP is
our only programmatic route to the Strategy Analyzer. Options (owner to choose):

1. **Owner runs the Strategy Analyzer manually** in the NT8 UI (NQ 1-min, window
   2023-01-01→2025-02-02, Standard fill, slippage 0, commission template of choice) and
   exports/screenshots the results — we then verify against the Python trade lists
   (runs/OTR_S0_TYPE1_REPRO conventions; the Python side is already certified
   trade-for-trade against NT8, so divergences would be port bugs, not convention gaps).
2. **Owner explicitly re-authorizes CrossTrade for historical Analyzer runs only** for
   this campaign (a directive amendment) — then the standard automated parity pipeline
   (entry/exit timestamps, prices, per-trade PnL, daily PnL, commissions, totals) runs
   as in campaign #1.
3. Defer parity; the Python engines remain the certified reference (S0 proved the
   convention stack against real NT8 output).

Parity comparison checklist (when unblocked, per directive §38): entry timestamps,
direction, exit timestamps, entry/exit prices, per-trade PnL, daily PnL, commissions,
totals. Compilation alone is not parity.
