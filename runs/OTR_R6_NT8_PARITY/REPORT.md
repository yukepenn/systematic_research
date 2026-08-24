# OTR_R6 — NT8 Strategy Analyzer parity for OTR-S-CAND2 (2026-08-24)

Executed via CrossTrade MCP (owner re-authorized; RunStrategyBacktest = the
same engine as the Analyzer UI, verified bit-identical in campaign #1).
Port under test: src/ninjascript/OriginalTraderSolarCAND2_v2.cs, sandbox-
compiled clean (v1 retired: int.MinValue cooldown-overflow bug produced zero
entries — the first live catch of a Python-vs-C# semantics hazard).

## Layer A — Jan-2023 window (comm 0): **PASS, cent-exact, trade-for-trade**
NT8 n=91, net $6,815.00 == Python n=91, net $6,815.00. All 90 serialized
trades match by (entry-time, PnL) exactly; the 1 unserialized trade is the
known NT8 data-boundary quirk (engine totals include it).

## Layer B — two-year master 2023-01→2025-02 (comm 0): **PASS, bit-exact**
| | NT8 | Python (frozen pre-readout) |
|---|---|---|
| trades | 4,592 (L 2,263 / S 2,329) | 4,592 (2,263/2,329) |
| net | $279,655.00 | $279,655.00 |
| DD | −$30,305.00 | −$30,305.00 |
| consec W/L | 7 / 15 | 7 / 15 |
Trade-multiset diff across 735k bars: NT8-only 0, Python-only 1 = the
2025-01-31 boundary serialization quirk. **Zero real differences.**

## Layer C — era-configured weekly windows (stop 65, comm 0, warmup-sliced)
| window | NT8 | R5 Python | verdict |
|---|---|---|---|
| 10/12-10/17 (old) | n90 43/47 net 6,560 hold 46.9 LL −1300 | identical | **EXACT** |
| 10/26-10/31 (old) | n49 net −5,075 | n50 net −3,310 | 1-trade data-source delta |
| 11/23-11/28 (new180) | n60 30/30 net −11,725 wr 25.00 LL −1300 | n60 30/30 net −11,825 | Δ$100; hold Δ12min = Thanksgiving session-shape difference in substrate |
| 1/4-1/9 (new180) | n64 net −12,805 | n65 net −12,790 | 1-trade delta |
Layer A/B prove LOGIC parity is bit-exact on identical data; Layer C deltas
(≤1 trade/window) are parquet-substrate vs NT8-feed data differences.

## Verdicts
1. **§51-E CLOSED: Python ↔ NinjaScript ↔ NT8 Strategy Analyzer are
   end-to-end consistent (bit-exact on shared data).** The §52 early-family
   chain now holds at every link that has ground truth.
2. Gate-timing projection semantics (R1.j) confirmed harmless in the real
   engine (would have shown as trade diffs; there are none).
3. Port bug ledger: v1 int.MinValue overflow — caught by the zero-trade
   smoke result, fixed in v2, class renamed per HOT-RELOAD rule.
4. Automation: WriteNinjaScriptFile reflection-compile unavailable on this
   build (file_only), but CompileNinjaScript sandbox → RunStrategyBacktest
   resolves the fresh sandbox assembly → fully self-serve iteration loop, no
   F5 needed going forward.
