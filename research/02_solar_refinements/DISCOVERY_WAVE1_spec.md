# DISCOVERY WAVE 1 — Preregistered plan (committed before results)

2026-08-06. **Objective update (user directive):** historical-research-only campaign; NO live-sim/shadow-fills/paper-trading/forward-monitoring ever unless explicitly requested. The 2025-03→2026-07 reservation is REMOVED — the research universe is ALL available history, 2022-01-01 → latest 2026 data. Strong, robust full-history economics (with per-year decomposition and neighborhood stability) is the selection standard. Slippage/fees are reported (slip-0 + 1-tick) but are not the research focus.

Full-history window: `2022-01-01T06:00:00Z → 2026-08-02T21:59:59Z` (last session = Fri 2026-07-31; boundary in weekend gap). Commission: Lifetime. Fill: Standard.

## Step 1 — SW02a timed-exit ladder (fast; historical-fill-artifact check)
Implementation: NO new code — the frozen replica's own time filter. `UseTimeFilter=true, StartTime=180000 (cross-midnight window)` blocks only (EndTime, 18:00); the exit is an ordinary market order named L/S-TimeExit filling at the NEXT bar open (a real print), and entries stop for the remainder of the session. Rungs by EndTime → realized exit fill ≈ 1 min later:
- baseline (UseTimeFilter=false, session-close fill at last print) — existing runs
- 165800 → fill ≈ 16:59 | 165500 → ≈ 16:56 | 164500 → ≈ 16:46 | 163000 → ≈ 16:31
Window 2023-01→2025-02 (baseline-comparable), slip 0 and 1 each.
**Preregistered verdict rule:** 16:58-rung slip-0 net ≥ 70% of baseline $146,440.60 → no material fill artifact (PASS; the last-print fill is approximable one minute earlier at real prices). < 50% → artifact CONFIRMED, absolute-edge accounting rewritten to the 16:58 basis. Between → partial artifact; adopt the 16:58 basis conservatively. Earlier rungs (16:45/16:30) measure genuine late-day opportunity cost, not artifact. Direct decision, no external-review workflow.

## Step 2 — Full-history reference (Tier 2)
Canonical 1m/90-179/T1 over the full window, slip 0 + slip 1, full payloads → per-year table, side split, exit split. Also verifies 2025-03→2026-07 data existence via trace bar count/MaxDate.

## Step 3 — Tier-1 sweeps (native optimization, summary metrics, full-history window, slip 0)
- **S4 signal types:** EntrySignalType {0,1,2,3} — 4 combos (characterization of Type 2/3/all).
- **S1 spatial grid:** TrendMultiplier {30,60,90,120} × StopMultiplier {60,90,120,150,180,210,240} = 28 combos (covers 30/60, 90/179≈180 anchor, ratios ~1.8/2.0/2.2 within grid; cells with SM≤TM are structurally poor and expected to fail — logged anyway).
- **S3 temporal grid (at 90/179):** SlowdownScan {2,3,5,8,12} × WeakWeakSplit {5,10,15} = 15 combos (PullbackSplit fixed 10; inert for pure Type-1 unless indicator internals couple — the sweep itself tests that).
- **S2 timeframes (individual runs):** 2m/3m/5m at identical 90/179/5/10/10 (Stage A) + time-normalized 2m:3/5/5, 3m:2/3/3, 5m:1/2/2 (Stage B) — 6 Tier-2 runs.

## Preregistered ranking & refinement rules
- Primary ranking: analytic slip-1 net = net_slip0 − trades×$9.53 (empirical bar-capped rate), tie-broken by PF and worst-year.
- Report per config: net, PF, trades, Sharpe(NT8), analytic slip-1 net & avg trade.
- Region refinement trigger: any config with analytic slip-1 net > full-history canonical baseline AND ≥60% of its grid neighbors positive AND neighbor median ≥ 60% of center → refine with a finer local grid (next sweep).
- Tier-2 confirmation (full payload, real slip-1, per-year decomposition) only for the top ~5 regions.
- NO promotion in Wave 1 — discovery + mapping only. Every combo logged in the registry (multiple-testing count grows accordingly; DSR/PBO accounting at promotion time uses this count).
- Signal-structure variants needing new code (T1+T3 re-entry, selective T2, catastrophe stops) are Wave 2, seeded by these maps.
