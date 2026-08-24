# OTR CURRENT TRUTH (prepend-newest)

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
