# G2_AUG_INCUMBENT_READ — RESULT: August 2026 was a GOOD month, and it was carried by two trades

Spec committed `6e0d728` **before the seal was touched**. Trial G00041. Owner-authorized scoped
read. Engine: NT8 Strategy Analyzer, the **certified `.cs` objects**, NQ 09-26 1-min,
2022-01-03 → 2026-08-30 (the certified parity window extended by one month), template commission,
zero slippage.

## The August read

| | trades | ctrRT | **net (NT8 conv.)** | win rate | largest single |
|---|---:|---:|---:|---:|---:|
| P1/PCT | 39 | 52 | **+$11,653** | **25.6%** | **+$26,951 = 231% of the month's net** |
| XM_v2 | 5 | 5 | **+$9,378** | 60.0% | +$10,756 = 115% of its net |
| **COMBINED (M_11)** | 44 | 57 | **+$21,031** | — | — |

Research-convention estimate (subtracting measured/modeled spread, ≈$1,136): **≈ +$19,895**.

Weekly: W31 −$394 · **W32 +$29,197** · W33 +$1,303 · W34 −$7,262 · W35 −$1,812.

## What it means — and mostly does not

1. **The month is real and positive, and it is a textbook instance of the tail profile.** P1 won
   only **25.6%** of its August trades and still made money because ONE trade (2026-08-04,
   2 contracts, +$26,951) exceeded the entire month's net. XM traded 5 times and one trade
   carried it. This is exactly what `G2_F9_P1_SYMCERT` measured (top-10% of trades = 236.8% of
   net) — the forward month behaved like the distribution, not like an average.
2. **N = 1 month. It is not forward validation of anything.** 44 trades against a strategy whose
   22 best weeks carry 79% of four years of P&L cannot distinguish "alive" from "lucky". Treat
   it as one draw, and note the draw came immediately after July's −$30k combined month.
3. **The July→August swing (−$30,139 → +$21,031) is the machine's normal breathing**, not a
   recovery signal.

## Parity cross-check (mandatory, per spec)

On the consumed Jan–Jul window, decisions reproduce well and dollars differ within the documented
convention band: P1 **246 NT8 trades vs 245 Python** ($41,576 NT8 gross-of-spread vs $42,481
Python net-of-spread); XM **55 vs 54** ($33,620 vs $39,649). The trade-count agreement is the
load-bearing part (decisions before dollars); the dollar gaps sit in the direction of the known
convention differences plus the certified −1.05% residual. ⚠️ A first attempt with a
2026-01 start was **discarded before it was quoted** — P1's 250-entry quality-sizing window was
still cold, distorting every month. The certified 2022-01-03 warm-up is mandatory.

## Coverage note

The NT8 minute store ends ~2026-08-27; P1's last August entry is 08-24 23:35, XM's 08-25 09:46.
The read therefore covers **2026-08-01 → ~08-27**, not the full calendar month.

## ⚠️ BURN DECLARATION (irreversible)

**2026-08 is now `DIRECTLY_BURNED` for `P1/PCT` and `XM_CONFLICT_v2`.** It can never again be
quoted as clean forward evidence for those objects. **Seal preserved and untouched for everything
else** — FOLLOW_MORNING's accumulation, LIQREV01/HTFDIR01's 2026-11-01 readings, and any future
candidate's confirmation window. No object was designed against August data; no gate, promotion,
or policy change follows from this read. The effective seal boundary for all other objects is now
**≥2026-09-01**, which is also `SHADOW_START`.

**`LIVE ENABLED = NO` · $0.**
