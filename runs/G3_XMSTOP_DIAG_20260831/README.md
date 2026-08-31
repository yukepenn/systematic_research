# G3_XMSTOP_DIAG — why is the drawdown big, and is it XM's missing stop?

**DIAGNOSTIC / `DISCOVERY_CONTAMINATED`. Not a candidate, not a proposal, no gate.**
Run in answer to a direct owner question on 2026-08-31.

## THE OBJECT

`WeeklyEdgeXMConflict_v4.cs` `SetDefaults`: **`DisasterStopPoints = 0.0`** — *"OFF by default.
See the header: no level selected."* XM enters at the 09:46 open and holds to the 15:46 open.
**Six hours, no stop. The only intra-trade risk control is the clock**, and the source header
(`:52-53`) says exactly that, together with the worst historical adverse excursion of
**−$10,865 (543 pts) — "a SAMPLE MAXIMUM, NOT A BOUND."**

**My independent recomputation from 1-minute bars returns −$10,865. It matches to the dollar.**

## XM's MAXIMUM ADVERSE EXCURSION — 346 trades

| percentile | MAE $/contract |
|---|---:|
| p1 | −8,762 |
| p5 | −5,448 |
| p25 | −3,072 |
| **p50** | **−1,662** |
| p75 | −669 |
| p95 | −85 |
| **worst** | **−10,865** |

**64% of trades go more than $1,000 against. 43% go more than $2,000 against.** Of those that
dipped past −$2,000, **22% still finished positive** — and the mean trade is +$589.

**XM's edge requires sitting through the excursion.** That is the mechanism, not an oversight.

## WOULD A STOP HAVE HELPED?

Full window 2022-01 → 2026-07, direction recovered for **372 of 373** trades from the P&L identity
(`dir = sign((pnl + comm) / price move)`), 194 long / 178 short:

| stop $ | XM net | XM maxDD | M_11 net/wk | **M_11 maxDD** | vs no stop |
|---|---:|---:|---:|---:|---:|
| **NONE** | **173,403** | 32,383 | **2,160** | **45,138** | — |
| 1,000 | 127,688 | 18,523 | 1,969 | **32,138** | **−13,000** |
| 1,500 | 103,753 | 23,113 | 1,869 | 40,326 | −4,811 |
| 2,000 | 126,278 | 22,803 | 1,963 | 37,616 | −7,521 |
| 3,000 | 126,318 | 26,213 | 1,963 | 38,041 | −7,096 |
| 5,000 | 175,133 | 31,223 | 2,168 | 46,343 | **+1,205** |

And on the **modern window only** (the frozen decision ledger starts 2022-07-04, which is why the
first pass silently excluded H1 2022):

| stop $ | M_11 maxDD |
|---|---:|
| NONE | 23,099 |
| 1,000 | **24,215 — WORSE** |
| 2,000 / 3,000 / 5,000 | 23,099 — unchanged |

## THE ANSWER

**A stop on XM is a REGIME BET, not a risk control.**

- **With H1 2022 in the window** a $1,000 stop cuts M_11's drawdown 29% ($45,138 → $32,138) for
  ~9% of the return ($2,160 → $1,969/wk).
- **On the modern window it does nothing, or makes the drawdown worse.**
- At $5,000 — a level only 21 of 346 trades ever reach — it makes the drawdown *worse* on the full
  window too.

So the missing stop is **not** why the drawdown is big in the current regime. **The drawdown is big
because of H1 2022**, and H1 2022 is the only window in which a stop would have helped.

## TWO CAVEATS THAT ARE NOT DECORATION

1. **A 1-minute bar's low/high is not an intrabar path.** Every stop arm above assumes a fill at
   exactly the stop level with zero slippage. The stop arms are **optimistic** — and they still lose.
2. **This is an in-sample sweep over six levels on a drawdown metric.** That is a search. It would
   need preregistration to mean anything, and it has none. **It is a diagnostic and nothing here
   proposes changing the live object.**

This is also why the repo built `DisasterStopPoints` and left it at `0.0`: **selecting a level is a
free-parameter fit, and the table above shows the "best" level depends entirely on which regime you
put in the window.**
