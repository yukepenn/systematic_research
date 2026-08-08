# Scalping Lab — Campaign State

**Phase: P0 BOOTSTRAP → P1 DATA REALITY** (2026-08-07)

## Now
- [x] Skeleton + constitution + mandate archived
- [x] Contamination ledger initialized (split geometry pending remaining audit items)
- [x] **P1 core: data reality audited** (DATAPROBE01) — L1 CONFIRMED (ms timestamps,
      2025-08→seal), **L2 CONFIRMED** (Bid/Ask tick download on demand, same depth),
      L3 unknown (BBO-size semantics), L4 BLOCKED_BY_DATA. `runs/DATAPROBE01/results.md`.
- [x] P1b: Deep-research batch 1 complete (DR_A..D in `deep_research/`, synthesis in
      HYPOTHESES.md). Zone verdict: micro book-signal harvesting structurally dead at
      retail latency; survivors = structural horizons, mechanical windows, large-magnitude
      events, cost-side engineering. Fill model adopted into EXECUTION_MODEL.md (binding).
- [x] **AMENDMENT 1 applied (2026-08-07)**: zone verdict softened to prior; three-use
      separation (directional/selectivity/execution); BBO_EXEC model specified alongside
      BENCHMARK_C1; xcorr=0 known-answer test WITHDRAWN (replaced by result-agnostic
      timestamp-integrity audit; ES→NQ lag is an empirical object); external numbers
      demoted to EXTERNAL PRIOR; zones MICRO/STRUCTURAL_SCALP/ADJACENT_INTRADAY with
      separate champions; P(+A before −B) excursion axis formalized; NO live recorder
      (owner ruling); owner seed S2a (breakout-pullback rebreak) registered.
- [x] **P2: split geometry FROZEN** (CONTAMINATION_LEDGER): dev tick 2025-08-10→2026-05-31,
      sealed scalp holdout 2026-06-01→2026-07-31 (single-read at Tier-3), minute dev from
      2005, ≥2026-08-01 locked.
- [x] **E10 Flatten1644 CONFIRMED_ADOPT** (Amendment §11): v2 full-period run vs v1 —
      net −5.35% (gate [−8%,0%]), corr 0.9972, DD flag investigated & cleared, tail
      retention 95.8%. v2 = live-ops default. runs/E10MASTER_V2/results.md.
- [ ] **Wave W1 (Tier-0): instrumentation first, alpha second** —
      W1-0 instrumentation (no selection risk): tick/BBO export pipeline → spread-state map
      (H-EXEC-1), Roll-bounce guardrail (H-A3), timestamp-integrity audit, L3 semantics;
      W1-1 Z1 DC scale transfer; W1-2 H-A1/D5 last-30-min momentum (minute data, dev only);
      W1-3 H-B5 spike classification; W1-4 H-D3 cash-close window; W1-5 S2a owner seed.
      Every spec frozen+committed before results; all P&L under BBO_EXEC + BENCHMARK_C1.
- [x] P1c/pilots (2026-08-07): **ES tick/BBO CONFIRMED downloadable** (H-D1 feasible);
      quote series fire on same-price size updates → L3 PLAUSIBLE-size (coarse use only);
      zero timestamp violations; **NQ real spread = 2-3 ticks RTH median, 1-tick only
      2-7% of time** → honest market-order RT ≈ 3-4 ticks; C1 mildly optimistic. Substrate
      architecture adopted (DATA_SUBSTRATE.md, Amendment 2). Session-keying rule learned.
      artifacts/instrumentation/pilot_report.md.
- [x] **LAYER-0 SUBSTRATE BUILT (2026-08-07)**: 40/40 stratified dev sessions exported
      (341M rows -> 1.05GB zstd parquet, substrate/raw/NQ/, MANIFEST.csv). L2 coverage
      37/40 (L1-only: s20250811 pre-boundary, s20250924 + s20260430 server holes; L2
      server depth starts 2025-08-12..14). 13 high-vol sessions truncated at the 12M cap
      (afternoons missing — second pass with RTH trading-hours template queued). Server
      Bid/Ask is a ROLLING ~1yr window: oldest quotes can vanish — backfill remaining
      ~168 dev sessions opportunistically, oldest first.
- [x] **W1-0b BBO audit**: spread map CONFIRMED (sync==asof); BBO_EXEC stays diagnostic
      (same-ms +-1t ambiguity); C1/C2 promotion truth. w10b_bbo_audit_report.md.
- [x] **Layer-1 1s grids built** (40/40). **Z1 CLOSED standalone** (r~2.0 at micro scale —
      real persistence, gross +0.7-0.9t/cycle at theta<=40, but net C1 firmly negative;
      role-B/C re-registration only). **Excursion baselines published**: uncond ~1-2pp
      over null, post-flip +1-4pp more, break-even gap 25-40pp -> single primitives dead,
      interactions are the only micro route. artifacts/z1/z1_report.md.
      **[CORRECTED 2026-08-08 by W2-0: "real persistence" and "gross positive" RETRACTED —
      null was mis-specified (TM null ~2, not 1) and the gross was trigger-jump algebra;
      DIRECT gross is negative at every theta. Closure holds a fortiori.]**
- [x] **AMENDMENT 4 applied (2026-08-08)**: FAST_STRUCTURAL (Zone F: 5-120s holds,
      8-32t moves) is now PRIMARY priority; four zones M/F/S/A with separate champions;
      owner-scale clue = ~20t over tens of seconds (economic scale, NOT a strategy spec).
      Mandatory P0 = Z1_DEFINITION_AND_NULL_AUDIT (omega in z1_dc_ladder.py confirmed by
      code-read to be TOTAL MOVEMENT ext-to-ext, so the r~2 null is ~2, NOT 1 — the W1-1
      "persistence" framing is under audit). Verbatim: MANDATE_AMENDMENT_4_FAST_STRUCTURAL.txt.
- [x] **Wave W2 COMPLETE (2026-08-08, specs frozen 1025569 before readouts)**:
      **W2-0 null audit — MAJOR CORRECTION**: omega=TOTAL MOVEMENT, null r~2 (matched
      ~2.13); W1-1 "persistence"/"gross positive" RETRACTED (trigger-jump algebra; the
      same algebra is +0.67-1.3t on a martingale); DIRECT flip-to-flip gross NEGATIVE at
      every theta; excursion "mild momentum" corrected to +0.2-0.6pp over matched null.
      Z1 closure a fortiori. NULL-3 curves = campaign reference nulls; all future DC/
      excursion claims must cite them. artifacts/z1/z1_null_audit_report.md.
      **W2-1 census — owner-scale moves ABUNDANT** (median 60s MFE = 20t = 5 NQ pts;
      ~292 epi/day/dir at H60/M20; t2MFE p50 29s); direction+retention is the whole
      problem. **Excursion surface: viability gap shrinks with bracket size — +32/-10
      needs only ~7pp conditional lift at C1** (vs 25pp micro). Pre-state: activity/vol
      dominates (not a discovery); ONLY directional precursor = CONTRARIAN 5-30s
      counter-move (ret5/ret10 effect 0.5, up-opps preceded by -5t drops); momentum
      precursors ~zero. Spread at opportunity moments 2.42t vs 1.79t control (C1
      optimistic in-state; C2 mandatory). artifacts/census/census_report.md.
- [x] **W3-1 SNAPBACK REJECTED at Tier-0 (2026-08-08, spec frozen 1b3837d, DoF 8)**:
      all 24 configs net C1 -2.3 to -2.9t/trade, CIs<0, coherent negative plateau;
      conditional lift +1-2pp vs needed 7-10pp (census inversion mostly failed — the
      trigger is a near-permanent state at 300-400 epi/day, not a setup). Measured
      signal ladder for fast NQ states: micro momentum +0.2-0.6pp; single fast trigger
      +1-2pp; needed +7-10pp. One-feature fast triggers deprioritized; +1-2pp contrarian
      lift kept as role-B reference fact. artifacts/w31_snapback/w31_report.md.
- [x] **AMENDMENT 5 applied (2026-08-08)**: ALPHA THROUGHPUT MODE — governance to
      maintenance; every wave must deliver A(trade readout)/B(kill)/C(promotion)/
      D(material feature); thin freezes; parallel families; CLEAN_MOVE + path ordering;
      scoreboard (ALPHA_SCOREBOARD.md). Verbatim: MANDATE_AMENDMENT_5_ALPHA_THROUGHPUT.txt.
- [x] **W4 COMPLETE (2026-08-08, 5 parallel families via workflow, spec 2db9058): 4
      KILLS + 1 label map.** FSS-1 killed (0/48; passive limit variant ALSO killed —
      adverse selection exceeds spread saving: passive gross −1.50 vs market −0.93).
      S2a killed at owner params (3-min fix net C1 −1.675; short-side +13.5 n=43
      OBSERVATION only). FSS-5 killed 0/144 (neither reclaim nor continuation; only
      5-7% of sweeps reclaim). H-B5 killed (P(CONT) 0.390 vs P(REV) 0.407; confounded
      cell's honest readout −3.46t). CLEAN_MOVE labels: path toll P(−4 before +8)=0.63,
      median pre-target DD 7.5t, clean fraction 42%; clean-vs-dirty separates on DEEP
      contrarian pre-move (ret30 −15 vs −5), eff60, flow — NOT vol/spread → W5 seed.
      Synthesis: artifacts/w4_wave_report.md. Data: s20250902 L2 truncated (RTH
      quote-dead, L1-only effectively).
- [x] **ES pipeline CONFIRMED** (pilots ESU5/ESH6 full sessions uncapped, L1+L2 →
      substrate/raw/ES/ + MANIFEST). Oldest-first ES archival of discovery sessions
      running (10 jobs queued 2026-08-08; rolling-window vanishing risk).
- [x] **DR-E GLOBAL STRATEGY REVIEW (owner-requested, 2026-08-08)**: 4 web-research
      lanes converge — Zone F externally corroborated dead (per-event edge pool ~0.5t <
      C1, latency-allocated; retail takers are the documented HFT profit source);
      friction floor sits at ~30-60min holds (required capture 8.4%@5min vs realistic
      ~4%); documented retail-accessible edges live at 30min-multiday; cheapest certain
      win = fractional-Kelly MNQ sizing of R5-E10 (likely over-Kelly today); real
      second-engine route = cross-ASSET persistence screen (GC/CL) + overnight premium
      (Solar-orthogonal by construction), all correlation-gated (<0.3). MNQ C1
      arithmetic corrected (4.6t not 6.6t). deep_research/DR_E_global_strategy_review.md.
- [x] **AMENDMENT 6 applied (2026-08-08)**: DR-E closure conclusions WITHDRAWN (Zone-F
      formal closure, 30-min floor, "certain win" Kelly, "orthogonal by construction"
      overnight) — external evidence reclassified as PRIOR. Three programs run in
      PARALLEL: A Family-A exploitation (bounded), B independent engine discovery
      (largest objective), C bounded fast-scalp frontier + predictability-ceiling test.
      Zone-F closure only per Amendment 6 §9 (5 families + ceiling + red team).
      Verbatim: MANDATE_AMENDMENT_6_NO_PREMATURE_CLOSURE.txt.
- [ ] **W5 (three programs, specs frozen before readout — specs/W5_programs_wave.md)**:
      A1 robust sizing FRONTIER (ledger-only, scenario grid, no single fraction as
      truth). B1 overnight 16:44→09:30 first pass (2022-2026 3-min data) + measured
      correlation vs Solar ledger. B2 intraday-momentum correlation pre-gate (existing
      H-A1 P&L vs Solar ledger). C1 W5-1 CLEAN/deep entry (depth×efficiency×flow +
      recovery-tick entry — mechanically distinct from killed W3-1 raw fade).
      C2 fast FSS-2 (15s/30s completed-bar breakout-acceptance — distinct from killed
      1-min S2a). C3 FSS-3 failed-opposite-probe state machine. C4 FSS-6/7 compression
      →expansion + velocity/low-retracement. C5 predictability-ceiling test (logistic/
      GAM/GBM, day-aware chronological folds, lift vs the 7-10pp gap — measurement,
      not strategy). FSS-10 ES queued behind ES substrate completion (archival running).
- [x] (superseded record) **RESTRUCTURED PROGRAM (per DR-E; supersedes prior W5 queue)**:
      **P0** fractional-Kelly MNQ sizing policy for R5-E10 v2 (immediate, ledger-only).
      **P1** execution overlays on Solar: patient TIME-TRIGGERED exits test (+0.5-1t/exit
      hypothesis) + stop/exit realism audit from own tick data.
      **P2** correlation-gated second-engine search: overnight 16:44->09:30 premium
      (2005-2026, MNQ prototype); intraday-momentum family (ledger-correlation pre-gate
      FIRST, predicted reject); cross-asset r-screen GC/CL/RTY/ZN with W2-0-corrected
      per-instrument nulls + friction conversion.
      **P3** scalp disposition: ZONE F FORMALLY CLOSED (externally corroborated);
      30-min horizon-floor gate adopted for all new families; ONE final migration
      experiment = CLEAN seed at 10-60min holds, 40-80t brackets -> if it fails,
      declare NO QUALIFIED FAST NQ SCALPING EDGE per mandate par.34. Substrate
      repurposed: execution lab + Solar role-B/C per-trade micro-state + >=1min ES
      regime features. Remaining ES/NQ archival continues oldest-first.
      **P4** closed permanently: seconds ES lead-lag, queue/passive scalp alpha,
      regime suppression on Solar, pre-FOMC standalone, day-of-week, MNQ scalp
      economics.
- [ ] Re-queued (Amendment 4 ordering): S2a frozen run (P7); H-B5 (P8); H-B1 anti-chase
      (role C, P11); oldest-first ARCHIVE_ONLY exports of confirmation pool (§20).
- [ ] (done earlier) capped-session RTH second pass → Layer-1 state grids (250ms/1s/5s) →
      I-1 full spread map + I-2 Roll-bounce + I-3-full sync audit → Z1 mid-price DC
      ladder → excursion surfaces P(+A before −B) → H-B5 → S2a.
- [ ] P2: Freeze split geometry in CONTAMINATION_LEDGER.md (after P1c)
- [ ] P3: Event-study factory (Tier-0): first wave candidates = Z1 (DC scale transfer,
      L1-only, tooling exists), S10 (spread state — foundational for all costs), Z2
      (speed-conditional continuation), S9 (tick-rule OFI + BBO)

## Standing rules in force
- ≥ 2026-08-01 sealed (shared with Solar LOCKED_FORWARD)
- No strategy P&L before split geometry is frozen
- NT8 engine exclusivity with Solar campaign work
- Specs committed before results are read; every config numbered in registry

## Log
- 2026-08-07: Campaign opened per owner MANDATE_V2. Bootstrap committed.
