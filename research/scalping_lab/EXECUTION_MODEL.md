# Execution / Cost Model — frozen constants

Audited base (Lifetime plan, verified to the cent in E10MASTER_V1 validation):

| | NQ | MNQ |
|---|---|---|
| Commission/side | $2.18 | $0.65 |
| Tick value | $5.00 (0.25 pt) | $0.50 (0.25 pt) |
| C0 RT (commission only) | $4.36 = 0.872 ticks | $1.30 = 2.6 ticks |
| **C1 RT (comm + 1 tick slip/exec)** | **$14.36 = 2.872 ticks** | $3.30 = 6.6 ticks |
| C2 RT (comm + 2 ticks slip/exec) | $24.36 = 4.872 ticks | $5.30 = 10.6 ticks |

Consequences:
- **NQ is the scalp research vehicle.** MNQ friction is 6.6 ticks/RT at C1 — nearly all
  short-horizon edges die there. MNQ re-enters only at sizing/deployment time.
- C1 is the PRIMARY screen for market-order strategies. C0 is diagnostic only. C2 is stress.
- If bid/ask execution is modeled explicitly (Level 2 data permitting): decompose into
  spread-crossing (half-spread vs mid), additional slippage, and commission — never double
  count spread and the 1-tick slip allowance. State the convention in each spec.
- Passive/limit fills are NEVER assumed from a touched price (queue fantasy). Passive
  execution research is a separate late track requiring queue-quality data (mandate §24).
- Latency: decision-to-fill delay grid {0, next-event, 250ms, 500ms, 1s, 2s, 5s}; DATAPROBE01
  confirmed ~4ms timestamp fidelity, so the full grid is honest.

## Adopted fill model (DR-C, 2026-08-07 — binding for all event studies and Tier-1 sims)

Market orders only. A signal formed at time t fills at the **first trade print at or after
t + 250ms** (report the decay curve at next-event/500ms/1s alongside). Cost = C1's 1 tick per
execution (interpreted as half-spread ≈ 0.5 + latency drift ≈ 0.5 — never additionally charge
spread crossing on top). Brackets are evaluated on the tick stream (never bar OHLC); stops
fill at the through-print. ETH trades: C2 or excluded. ±2min around calendar news: C2
mandatory. Passive/limit fills remain banned (measured NQ touch-fill adverse-selection rate
65.8%; touched ≠ filled).

Margin context (owner-supplied, ninjatrader.com/pricing/margins 2026-08; floats with vol):
NQ $1,000 intraday / $43,433.67 initial; MNQ $100 / $4,343.38. Intraday margin applies until
16:45 ET. A pure day-scalp (flat by 16:44) needs only intraday margin — same conclusion as
the Family-A 16:44-flatten decision (`research/operational/MARGIN_1644_FLATTEN.md`).
