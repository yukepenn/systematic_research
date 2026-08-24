# OTR CURRENT TRUTH (prepend-newest)

## 2026-08-23c — Tracks SD / B / V / P adjudicated; Phase-13 old-history stress done

- **Track SD (LossLimit)**: PARTIALLY IDENTIFIED. Per-trade semantics INERT at 2500/4000
  (binds 1-3 trades in 25 months → a trader doesn't tune an inert knob); session-level
  (B stop-new-entries / C flatten+disable) both consistent with late-2025 weeklies;
  C@2500 mildly disfavored (damages W20251228). `solar_dstm_family/LOSSLIMIT_SEMANTICS.md`.
- **Track B**: UNKNOWN MULTI-BLOCK confirmed — zero repo/source hits for any raw token
  group; no mechanism guess admitted (§22). `multiblock_family/TRACK_B_STATUS.md`.
- **Track V**: V-EXACT BLOCKED BY MISSING DATA (bid/ask real volume: only 2 full tick
  sessions inside window A; re-export = CrossTrade, excluded). V-PROXY: 3 bounded passes;
  pass 3 met the frozen success rule (D 2.431 < 5.203) with `PREV|T_LVL|X_MED|C2`:
  **breakout of the PREVIOUS hour's static volume-percentile ladder in EMA20 trend
  direction, not-extended-10% entry gate, median-line exit** → count 189/183, net −5,445
  vs −4,055, hold 36/40m all ✓; WR −8pp and avg-loss −37% out of band; March/April
  cross-window signs unresolved (family membership unknown). Classification:
  BEHAVIORALLY MATCHED — PARTIAL. Running-intra-hour ladder and hourly-EMA20 trend
  FALSIFIED. `volume_vwap_family/TRACK_V_REPORT.md`.
- **Track P**: UNDERDETERMINED. June TP aggregates (32.8 trades/day @ 20.5m, WR 50%)
  need a short-hold high-WR component beyond V+S → corroborates multiple strategies incl.
  unidentified Family B; H1 vs H2 not discriminable; TP commission $1.04/RT is a new
  unresolved evidence item. `account_combination/TRACK_P_NOTES.md`.
- **Phase 13 (S13)**: OTR-S-CAND1 over 2006-2026 = REGIME-LOCAL(recent): sweet spot
  2023-2025 (+$93.5k/+$143.2k/+$26.3k), 2026 Jan-May **−$78.1k** — the reconstructed
  Solar family dies exactly when the trader migrated to the Volume family. Fixed-tick
  params are price-level-dependent; pre-2018 counts are structurally tiny.
- Remaining phases: 10-11 (NinjaScript ports + parity for S-CAND1/V-proxy), final
  package (Phase 14). Window B (2026-08) stays governance-blocked.

## 2026-08-23b — Track S CLOSED: PARTIALLY RECONSTRUCTED (moderate-confidence wrapper)

- **S0 PASS**: pure-Python loop reproduces the canonical Type-1 NT8 run trade-for-trade
  (2,914/2,915 exact; 1 documented boundary-bar diff). Load-bearing discovery: V0 exits on
  an INCLUSIVE touch of the end-of-bar TrailingStop — a touch exits WITHOUT flipping.
- **Candidate OTR-S-CAND1** = E13_R1|W_0400_1600|FF: T1+T3 entries, stop-and-reverse on
  flips, entries 04:00–16:00 ET force-flat outside, touch-exit + session-close. Fit vs
  EARLY_LONG: trades +7.2%, WR −0.5pp, PF −0.039, DD −0.7%, net −13.1%, hold −20.3% (the
  one out-of-band residual). D-score path: 3.52 (V0) → 1.67 (S1) → 1.34 (S3) → 1.15 (S3B);
  S4/S5B/S6 all failed to improve → closed at the frozen §49 three-pass stop rule.
- **Structural findings (high confidence)**: the original wrapper REVERSES at flips; a
  SelTime window blocks roughly 16:00→02:00-04:00 ET (he traded overnight-morning + RTH,
  ~759 in-market min/day — RTH-only is arithmetically impossible); pullback (T2) entries
  are NOT part of the system (every T2 cell crushes WR); WR/PF are engine properties, not
  wrapper properties.
- **S8 cross-window (frozen candidate)**: late-2025 windows consistent (counts/holds in
  range, 3/4 sign agreement) — trader plausibly still ran an S-variant; 2026 windows
  STRONGLY inconsistent (2× counts, half holds) — **2026 headline weeks are NOT Family S**.
- **Layer-2 economics**: $253.7k screenshot-parity → $186.7k at $4.36/RT + 1 tick/side
  (25 months). Behavior survives honest costs in-window.
- S5 pass was VACUOUS (tautological T3 gates) — logged as my spec-design error.
- Ledger: HYPOTHESIS_LEDGER rows OTR-S1-001..OTR-S8-001 (~100 cells, no cherry-picks).
  Full report: `solar_family/TRACK_S_REPORT.md`.

## 2026-08-23 — Campaign opened (OWNER MASTER DIRECTIVE v1.0)

- OTR is the SOLE active research mission; all prior products/campaigns frozen reference.
- Phase 1 scaffold complete: evidence ledgers transcribed from directive (AUTHOR_STATEMENTS,
  EVIDENCE_LEDGER EV-001..013, TARGET_WINDOWS 22 windows, AUTHOR_REPORTED_NQ_RESULT_TIMELINE
  28 weeks, FAMILY_MAP 5 families, IDENTIFICATION_OBJECTIVE, COST_MODEL, UNKNOWN_FIELDS).
- Phase 0 repo/evidence bootstrap running (Solar legacy read + wrapper/TrackV/TrackB
  string search + data audit). DATA_AUDIT.md pending its results.
- Governance notes: LOCKED_FORWARD respected — Track V window B (2026-08-02→08-14) readout
  BLOCKED (≥2026-08-01 virgin); 2026-06/07 data previously consumed → usable for
  reconstruction (not claimable as pristine OOS). CrossTrade excluded from campaign.
- Known reference gap (ORIGINAL vs our Type-1): WR/PF ≈ match, trades 4,351 vs 2,915,
  hold 94m vs 108m, net $292k vs $146k → wrapper unidentified (RECONSTRUCTION_SCORECARD.md).
