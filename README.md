# systematic_research

Historical systematic NQ/MNQ research repository.

## Current canonical systems

**Product A** — combined NQ system, ensembles/leverage authorized.
- Current file: `src/ninjascript/SolarWaveSMMaster_v4.cs`
- Trades: MNQ (NQ is the signal-only leg), position `M ∈ [-13,13]` contracts
- Parity: event-level decision mechanism proven correct; full-history net-profit consistent
  with 2 disclosed, non-defect conventions (not yet reduced to an exact leg-level proof)
- Architecture: Solar13 + HTF tilt + c1_50 short-halving + B-MOM, continuous sizing

**Product B — shared one-contract decision core**, two execution adapters:
- **BEST_ONE_NQ**: `src/ninjascript/SolarWaveOneContractNQ_v5.cs` — trades NQ directly, `{-1,0,+1}`
- **BEST_ONE_MNQ**: `src/ninjascript/SolarWaveOneContractMNQ_v5.cs` — trades MNQ, `{-1,0,+1}`
- These are **not two independently optimized alpha systems** — one shared NQ-derived decision
  core (Solar13 → HTF tilt → B-MOM → combined score → hysteresis(3,1) → C4 overlay), with only
  the execution leg (instrument, tick value, commission, fills) differing between the two.
- Parity: leg-by-leg decision agreement proven exact (0/214 divergent legs, live-NT8-verified) on
  a representative spot-check window; trade-count agreement (within ±1) independently confirmed
  across all 7 chunks spanning the full 4.5-year dev window with no gaps

None of the 3 objects is authorized for live trading. All fail closed in realtime by construction.

## Read first

1. **[`BASELINE_MODELS.md`](BASELINE_MODELS.md)** — identity, architecture, exact formula,
   parameters, performance, capital map, and parity status for all 3 objects. The canonical
   record; everything else defers to it for the 3 current systems.
2. **[`research/system_master/CURRENT_TRUTH.md`](research/system_master/CURRENT_TRUTH.md)** —
   current-state snapshot of the active campaign, updated after every wave.
3. **[`research/system_master/FINAL_OWNER_DECISION_20260809.md`](research/system_master/FINAL_OWNER_DECISION_20260809.md)** —
   closing status report answering the owner's standing questions directly.
4. **[`research/system_master/LIVE_READINESS_CHECKLIST.md`](research/system_master/LIVE_READINESS_CHECKLIST.md)** —
   what live enablement would require (not currently authorized).
5. **[`MAP.md`](MAP.md)** — full repo orientation (deeper structural detail than this page).
6. **[`RESEARCH_HANDOFF.md`](RESEARCH_HANDOFF.md)** — read before starting any new research wave.

## Research status

- The original Solar Wave discovery campaign (indicator recovery, raw-edge search) is closed —
  see `research/SOLAR_WAVE_CAMPAIGN_README.md`.
- The SYSTEM_MASTER portfolio-construction campaign's broad research phase closed 2026-08-09
  (0 promotions across 18 tested constructions; S2_SELTIME's own R2 adjudication also closed,
  NOT PROMOTED for all 3 objects).
- The engineering/parity debt that followed is now **closed**: a real, shared NinjaScript defect
  (a hardcoded-clock BMOM end-of-session flatten, DEFECT 3) was found via live-NT8 forensics,
  fixed, and independently re-verified across the full canonical history for all 3 objects.
- **Project mode: RESEARCH.** New hypotheses may be studied under the established research
  discipline — see `RESEARCH_HANDOFF.md` for what's open and what should not simply be rerun.
- No live-trading authorization exists or is implied by any of the above.

## Historical campaigns

- `research/SOLAR_WAVE_CAMPAIGN_README.md` — campaign #1 (indicator recovery), closed 2026-08-07.
- `research/audit/AUDIT_EXECUTIVE.md` — campaign #2 (independent post-campaign audit), closed
  2026-08-07.
- `research/scalping_lab/CAMPAIGN_STATE.md` — campaign #4 (short-horizon scalp-alpha search),
  phase complete, dormant. Its B-MOM/B1/B-FADE evidence directly feeds the current systems.

Full research evidence for every tested construction (including rejected ones) lives under
`runs/`, one immutable directory per experiment — see `MAP.md` for the layout.
