# Instrumentation Pilot Report (I-4 / I-5 / I-1-preview / I-3-partial)

Date: 2026-08-07. Inputs: 3 NQ pilot sessions (2025-09-10 / 2026-01-23 / 2026-05-06, three
different contracts) + 1 ES session (2026-07-15), each exported as Last+Bid+Ask 1-tick via
`SWScalpDataProbe_v1`. Raw CSVs local under `runs/EXPORT01/` (3M rows each, regenerable);
summary table `pilot_i4_i5.csv`.

## Headline finding (preliminary I-1, 2 sessions, both contracts agree)
**NQ is a 2-3 tick market, not a 1-tick market.** Time-weighted quoted spread:
RTH median 2-3 ticks (P(1-tick) = 2-7%), overnight median 3 ticks (P(1-tick) = 0.5-2%),
p95 3-5 ticks. Locked 0.4-0.6%, crossed 0.06-0.07% (coherent book stream).
→ Honest market-order round-trip friction ≈ half-spread×2 + commission ≈ **3-4 ticks
median, worse in fast markets**. BENCHMARK_C1 (2.872t) is mildly OPTIMISTIC as a mean;
BBO_EXEC prices the truth per-moment. Every scalp candidate must clear this real floor.
Full 40-session map (by hour × vol regime × event windows) remains the I-1 deliverable.

## I-4 quote-series semantics
53-68% of consecutive Bid (and Ask) events carry an UNCHANGED price → events fire on
size/queue updates at the standing BBO, not only on price moves. Volume field: mean ≈ 2,
p99 ≈ 6-7 (vs trade sizes mean ≈ 1.1) — consistent with best-level displayed-size-class
information (thin modern NQ book) or size deltas. **Ruling: L2 fully usable (prices);
L3 upgraded from UNKNOWN to PLAUSIBLE-size — usable only for coarse size features until a
dedicated delta-vs-level test; queue-position modeling stays out of scope.**

## I-3 partial (timestamp integrity)
Zero monotonicity violations in all 12 series (3 sessions × 3 + ES). Trades outside the
prevailing [Bid, Ask]: 6.8-8.6%, median excess 1 tick, p95 12-15 ticks — quote-vs-trade
staleness of a few ms concentrated in bursts. Consequence: BBO_EXEC must use asof-joined
quotes with a small tolerance and report the stale fraction; event studies at burst moments
must treat the BBO as ±1 tick uncertain. Exogenous-event clock test still pending (needs ES
+ NQ on a CPI/FOMC day).

## ES (H-D1 prerequisite): CONFIRMED
ES 09-26 Last+Bid+Ask tick downloads on demand (68s incl. server fetch; 1.36M bid events /
session-morning; ms-class stamps). Depth spot-check pending; assume ≈ 1 yr like NQ.

## I-5 pipeline benchmarks
Cached-session export ≈ 14-22s per ~3M rows; server-download adds ~45-60s per new
instrument-day. Full session ≈ 3.0-3.3M rows → the probe's 3M cap truncates at ~10:00 ET;
**the 40-session batch requires `SWScalpTickExport_v1` (12M cap, Tag naming) = one NT8
F5/recompile away** (source already in bin\Custom\Strategies). Engine session-keying rule
(learned the hard way): the `from` timestamp's ET calendar date must equal the session's
END date; bars always load from that session's 18:00 open regardless of `from`.

## Registry
Instrumentation rows I-3p/I-4/I-5 recorded as seq-0 (no selection content). No constants
tuned after readout; the spread finding updates EXECUTION_MODEL context, not the frozen
C1/C2 definitions.
