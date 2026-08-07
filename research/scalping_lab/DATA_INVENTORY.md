# Data Inventory — Scalping Lab

Status: PROBED (cache census + DATAPROBE01 engine probe complete 2026-08-07 — see
`runs/DATAPROBE01/results.md`). **L1 CONFIRMED (ms-class timestamps), L2 CONFIRMED
(historical Bid/Ask tick series download on demand, same ~12-month depth), L3 UNKNOWN
(BBO-size field semantics unverified), L4 BLOCKED_BY_DATA.**
Provider: NinjaTrader hosted historical servers via "Simulation" connection (user rainazur).
Cache: `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\` (hourly `.ncd` files per contract).

## Local-cache census (facts, verified on disk)

| Series | Coverage | Notes |
|---|---|---|
| **NQ Last tick** | **2025-08-10 → 2026-08-06, continuous** | NQ 09-25 (from 08-10) → 12-25 → 03-26 → 06-26 → 09-26. Hourly files, `.Last.ncd` only. Empty shell folders exist for NQ 03-20…12-24 (0 bytes — requested once, never filled; consistent with provider tick depth ≈ 1 year). |
| MNQ Last tick | 03-26/06-26/09-26 contracts (≈ Dec 2025 → now) | Larger files than NQ (more prints). |
| NQ minute | Contracts back to **NQ 03-05 (2005)** | Deep minute history — the Solar campaign's base. |
| NQ Bid/Ask tick | **Not cached** (zero `.Bid.ncd`/`.Ask.ncd`) | Downloadability from NT servers = open question → engine probe. |
| ES (any tick) | **Absent from tick cache** | ES minute presence TBC; ES tick likely downloadable ≈ 1 yr like NQ → probe. |
| Market depth / replay | `db\replay\` **empty** | No recorded L2 history. |

## Data-level determination (preliminary)

- **L0 (OHLCV): CONFIRMED** — minute to 2005, second-bars derivable from tick where tick exists.
- **L1 (last-trade events): CONFIRMED ≈ 12 months** (2025-08-10 → seal). This is the scalp
  campaign's primary resource. ~247 sessions of tick data in the development window
  (2025-08-10 → 2026-07-31).
- **L2 (BBO): OPEN** — two candidate paths, both need the engine probe: (a) bid/ask stamps
  carried on Last-tick events via Tick Replay (`OnMarketData` historical); (b) explicit
  historical Bid/Ask tick series download (`AddDataSeries(..., MarketDataType.Bid)`).
- **L3 (top-of-book sizes): LIKELY BLOCKED** — historical bid/ask sizes generally not in NT
  historical tick; confirm in probe before declaring.
- **L4 (depth): BLOCKED_BY_DATA** — no replay recordings exist; mandate forbids paid data.
  S6/S7/S8 (book-shape families) expected BLOCKED unless L2 probe surprises.

## Consequences for research geometry (to freeze in CONTAMINATION_LEDGER after probe)

- Tick-level development window ≈ 2025-08-10 → 2026-07-31 (~247 sessions); ≥ 2026-08-01
  sealed. One year is enough for Tier-0/1 micro event studies (10⁵–10⁶ events) but spans
  only ~1 vol regime cycle — regime-robustness axes must lean on the 2005+ minute history
  (structural-scalp horizons, 1–5 min) where 20 years exist.
- Two-track design follows naturally: **Track A (micro, tick, 1 yr)** and **Track B
  (structural scalp, 1s–5min bars from minute+tick, deep history at ≥1min)**.
- Timestamp resolution (ms vs s), per-tick volume fidelity, and bid/ask stamp availability =
  engine probe DATAPROBE01 (next).

## Open items
- [ ] DATAPROBE01: NinjaScript export — timestamp resolution, bid/ask series, tick volume
- [ ] ES minute coverage check; trigger ES tick download for the dev window if free
- [ ] Rollover/back-adjust policy for tick-level work (probe uses single contracts — level
  signals must use unadjusted single-contract prices; document merge policy explicitly)
