# I-1 Spread-State Map & I-2 Roll-Bounce — FULL READOUT (37 L2 sessions)

Date: 2026-08-08 (session basis 08-07). Spec: `specs/W1-0_instrumentation.md`. Inputs:
Layer-0 substrate, 37 L2 sessions 2025-08-14 → 2026-05-20. Per-session tables:
`i1_spread_by_session_hour.csv`, `i2_roll_bounce.csv`.

## I-1 — NQ quoted spread (time-weighted, ticks), by ET hour

| Block | Mean spread | P(spread = 1 tick) |
|---|---|---|
| Overnight 18:00–08:00 | 3.4 – 4.6 | 0.2 – 0.4% |
| RTH open 09:00–10:00 | 3.0 | 1.0% |
| RTH midday 11:00–14:00 | 2.3 – 2.4 | 4.6 – 7.5% |
| **RTH close 15:00–16:00** | **2.2 – 2.5** | **9.2 – 10.5%** (daily best) |
| 08:00 hour (pre-open, data releases) | 1.9 mean but P(1t) only 1.2% | bimodal |

**Frozen consequences:** (1) NQ is a 2–3.5-tick market everywhere; the C1 1-tick-slippage
convention understates median half-spread — BBO_EXEC is mandatory for honest Tier-1 P&L,
C1 kept only as the cross-campaign benchmark. (2) ETH ruling per spec: overnight median ≥ 3
ticks → ETH stays C2-or-excluded, now with a local number. (3) Execution-cost gradient
favors late RTH; morning entries pay ~35% more spread than 15:00 entries — a mechanical,
tradable-cost fact for any scalp family (role-C).

## I-2 — Roll bounce guardrail

- Trade-price 1-event autocorrelation: **mean −0.088** (negative = mechanical bounce).
- **Mid-price 1-event autocorrelation: +0.001 ≈ zero** — mid is clean.
- Roll-implied bounce: **0.46 ticks mean** (p10 0.34, p90 0.64) per session.

**Frozen consequence (binding on all reversion research):** ~0.5 tick of fake
mean-reversion lives in Last-trade prices. Every sub-minute reversion statistic must be
computed on MID prices (or survive a 1-tick-against shift); trade-price-only reversion
"edges" ≤ 1 tick are presumptively bounce artifacts. Z1's mid-price-primary design is
vindicated before it runs.

Both measurements are instrumentation (no selection); constants now frozen as campaign
reference values. Remaining W1-0 items: I-3-full exogenous-event clock test (needs an ES
CPI/FOMC day), L3 delta-vs-level test.
