# Execution / Cost Model — frozen constants

Audited base (Lifetime plan, verified to the cent in E10MASTER_V1 validation):

| | NQ | MNQ |
|---|---|---|
| Commission/side | $2.18 | $0.65 |
| Tick value | $5.00 (0.25 pt) | $0.50 (0.25 pt) |
| C0 RT (commission only) | $4.36 = 0.872 ticks | $1.30 = 2.6 ticks |
| **C1 RT (comm + 1 tick slip/exec)** | **$14.36 = 2.872 ticks** | $2.30 = 4.6 ticks |
| C2 RT (comm + 2 ticks slip/exec) | $24.36 = 4.872 ticks | $3.30 = 6.6 ticks |

[CORRECTION 2026-08-08, DR-E audit: the original MNQ C1/C2 cells ($3.30/6.6t and
$5.30/10.6t) double-counted slippage (used 2t and 4t per exec instead of 1t and 2t).
Corrected arithmetic: $1.30 + 2×$0.50 = $2.30 = 4.6 MNQ ticks (C1); $1.30 + 4×$0.50
= $3.30 = 6.6t (C2). NQ cells were always correct. Conclusion unchanged: MNQ C1 4.6t
still exceeds NQ's 2.872t by 60% — MNQ remains excluded from scalp research economics.]

Consequences:
- **NQ is the scalp research vehicle.** MNQ friction is 4.6 ticks/RT at C1 — nearly all
  short-horizon edges die there. MNQ re-enters only at sizing/deployment time.
- C1 is the PRIMARY screen for market-order strategies. C0 is diagnostic only. C2 is stress.
- If bid/ask execution is modeled explicitly (Level 2 data permitting): decompose into
  spread-crossing (half-spread vs mid), additional slippage, and commission — never double
  count spread and the 1-tick slip allowance. State the convention in each spec.
- Passive/limit fills are NEVER assumed from a touched price (queue fantasy). Passive
  execution research is a separate late track requiring queue-quality data (mandate §24).
- Latency: decision-to-fill delay grid {0, next-event, 250ms, 500ms, 1s, 2s, 5s}; DATAPROBE01
  confirmed ~4ms timestamp fidelity, so the full grid is honest.

## Two execution models (Amendment 1 §3; STATUS per Amendment 3: until W1-0b
BBO_INTEGRITY_AUDIT passes, **BENCHMARK_C1/C2 is the promotion truth and BBO_EXEC is a
diagnostic**, because NT8 historical Bid/Ask/Last series do not preserve inter-series
real-time ordering at shared timestamps.)

**BBO_EXEC (primary executable approximation — uses the confirmed L2 data):**
signal observable at t → choose latency L from the grid → reconstruct the latest CAUSAL
Bid/Ask at t+L → buys fill at prevailing Ask, sells at prevailing Bid → charge actual
commission ($2.18/side NQ) → residual implementation slippage applied as a SEPARATE stress
(0 / +1 tick per execution). Components reported separately: observed spread, latency drift
(price change t→t+L), residual slippage, commission. Never double-count spread inside a
generic slippage constant.

**BENCHMARK_C1 (standardized cross-campaign stress, same as Family A):**
first trade print ≥ t+250ms + commission + 1 tick/execution. C2 = 2 ticks/execution.
Retained so every scalp result is comparable to Family-A accounting; not a substitute for
BBO_EXEC.

Common rules: market orders only in Tier 0–2; brackets evaluated on the tick stream (never
bar OHLC), stops fill at the through-print; ETH → C2-or-excluded; ±2min around calendar news
→ C2 mandatory; latency grid {next-event, 250ms, 500ms, 1s, 2s, 5s} (~4ms fidelity
confirmed). Passive/limit fills remain out of scope for backtests — EXTERNAL PRIOR
(source-sample-specific, e.g. one study's 65.8% touch-fill adverse-selection rate): passive
fills can suffer severe adverse selection and touched ≠ filled; no local NQ constant is
claimed until independently reproduced on our data.

Margin context (owner-supplied, ninjatrader.com/pricing/margins 2026-08; floats with vol):
NQ $1,000 intraday / $43,433.67 initial; MNQ $100 / $4,343.38. Intraday margin applies until
16:45 ET. A pure day-scalp (flat by 16:44) needs only intraday margin — same conclusion as
the Family-A 16:44-flatten decision (`research/operational/MARGIN_1644_FLATTEN.md`).
