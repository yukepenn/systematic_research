# H0 — Product A current-health panel + A/B comparison

**Disposition:** diagnostic complete. Deliverables: `research/system_master/
CURRENT_EDGE_HEALTH_PRODUCT_A.md`, `research/system_master/PRODUCT_A_VS_B_CURRENT_HEALTH.md`.
Full detail lives in those two documents and the ~33 files under `out/`; this REPORT.md records
the run's own correctness gate and top findings for the campaign's standard per-family record
(persisted here by the orchestrating session — the subagent's Write tool blocked writing report/
findings `.md` files directly and returned this content as text instead).

## Correctness gate: PASS

Independently re-verified by the orchestrator: grouping `bar_pnl_A_dollars` by `sess_date`
restricted to `is_health_only_bar==False` in `runs/U0_UNIFIED_STATE/out/u0_state_table.parquet`
reproduces **$177,924.40** exactly, matching the certified canonical Product-A net. Trip-ledger
partition also verified exact (canonical trip net_pnl $184,372.25 + flat-bar residual -$6,447.85
= $177,924.40); exposure-band/transition-class figures reproduce PA0's own published
canonical-window numbers to the cent (FRESH $2.03/contract, SCALE_IN $14.43/contract).

## Top findings — `CURRENT_EDGE_HEALTH_PRODUCT_A.md`

1. Overall verdict **HEALTHY** — 5/8 indicators HEALTHY, 2 NORMAL_WEAK_REGIME, 1 POSSIBLE_DECAY,
   0 STRUCTURAL_BREAK_EVIDENCE, thresholds fixed before computing the current reading.
2. Product A independently confirms Product B's "weak Jan-May 2026 (Sharpe 0.584), strong
   Jun-Jul recovery (Sharpe 3.42)" shape on its own P&L — not inherited, separately derived
   (2026-YTD Sharpe 1.603 exceeds pre-2026's 1.260).
3. PA0's "scale-in ~7x more valuable than fresh entries" reconciles exactly on canonical
   (7.127x) but **compresses to 0.827x** in the 45-session health-only extension (both legs
   still solidly positive in dollar terms) — flagged NORMAL_WEAK_REGIME.
4. Exposure-band monotonicity (PA0's core sizing-validation finding) **breaks at the top end**
   in the extension: the 10-13 contract band flips from canonical's best per-contract band
   (+$1.878) to net negative (-$0.173, on just 331 bars/7 sessions, -$605 total) — flagged
   POSSIBLE_DECAY, the one genuine caution this family surfaced.
5. Giant-winner arrival rate (74.50/250 sessions) is the highest of 5 years, top-10-day
   contribution 54.2% matches Product B's ~52-55% finding, and current regime is tail-*richer*
   than history (63.6th/74.8th percentile) — no right-tail drought.

## Top findings — `PRODUCT_A_VS_B_CURRENT_HEALTH.md`

1. Session-level daily-return correlation 0.883 (stable, rolling-60 range [0.78, 0.93]);
   **P(A loses | B loses) = 91.0%** vs 55.5% unconditional (1.64x lift) — strong co-dependence.
2. 4 of Product A's 5 worst drawdown episodes overlap in calendar time with one of Product B's
   5 worst; 15/20 best days and 11/20 worst days shared between products.
3. Bar-level directional agreement when both hold a position: **99.97%** — they essentially
   never actively disagree on sign (167 of 540,232 bars).
4. Verdict: diversification is **modest and comes mostly from exposure timing/breadth** (A
   holds a position on 77.3% of bars vs B's 38.0%) plus session-specific path-dependence noise
   from continuous re-scaling — not from genuinely different directional views; the
   short-halving overlay is real but narrow (cleanly evidenced on 2025-09-22).
5. Concrete mechanistic examples inspected: 2026-07-29 (A wins via faster re-flipping on a
   whipsaw day), 2025-09-22 (A's short-halving overlay directly protected it), 2026-02-05 and
   2022-04-27 (A's continuous scale-in gave back gains a static B-style position kept),
   2026-05-19 (both lose badly — A's worst day on record — because the *shared* underlying
   signal itself whipsawed, not either product's own layer).

## Scope discipline

Diagnostic only. No candidate constructed, no parameter changed, zero NT8/CrossTrade calls.
Product A (`SolarWaveSMMaster_v4`) and Product B (`SolarWaveOneContractNQ_v5`/`MNQ_v5`) unchanged.
