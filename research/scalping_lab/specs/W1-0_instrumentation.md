# W1-0 — Instrumentation Pack (preregistered; NO selection content)

Date: 2026-08-07. Tier: instrumentation (measurements that calibrate all later work; none
of these choose among trading rules, so they carry no selection risk — but their outputs are
frozen constants once published; no re-measuring to taste).

All measurements run on the DEVELOPMENT tick window only (2025-08-10 → 2026-05-31), never
the holdout. Data path: per-session tick/BBO exports via probe-strategy runs (Last + Bid +
Ask 1-tick series) → parquet. Sessions sampled, not exhaustive, per item below.

## I-1 Spread-state map (H-EXEC-1; BBO_EXEC foundation)
On a stratified sample of ≥ 40 sessions (10 per quarter, random within quarter, seed 20260807):
per-second prevailing spread = Ask − Bid (last causal quote pair). Report: % of time spread
= 1 tick / 2 / ≥3, by (a) session hour (18:00→17:00 ET), (b) RTH vs ETH, (c) realized-vol
quintile of the session, (d) ±2min around calendar events. Output: spread_state_map.csv +
the ETH cost ruling (if ETH median spread > 2 ticks, ETH C2-or-excluded rule gets its local
number). No hypothesis test; this is a measurement.

## I-2 Roll-bounce guardrail (H-A3)
Same sessions. Measure 1-bar and k-event autocorrelation of trade-price changes vs MID-price
changes (mid from causal BBO). The gap between trade-price mean-reversion and mid-price
mean-reversion = mechanical bounce magnitude (report in ticks, by spread state). Frozen
consequence: any future sub-minute reversion candidate must clear its edge on MID prices,
or survive a 1-tick-against price shift; the measured bounce is subtracted in Tier-0 screens
of reversion families.

## I-3 Timestamp-integrity audit (Amendment §4-compliant; replaces the withdrawn xcorr test)
(a) Monotonicity: non-decreasing timestamps within each series; count violations.
(b) Cross-series coherence within NQ: trade prints vs quote updates at the same ms — measure
    P(trade price within [Bid, Ask] of latest quote) — a mechanically-true property whose
    failure rate bounds effective NQ-internal sync error WITHOUT assuming any economic result.
(c) ES availability check + the same (a)/(b) on ES if tick data downloads.
(d) ES↔NQ: report the raw trade-time cross-correlation function at ±5s as a DESCRIPTIVE
    object (no "must be zero" assumption); separately measure clock coherence via scheduled
    exogenous events (CPI/FOMC 8:30:00/14:00:00 ET first-reaction times in both series —
    the reaction ONSET difference bounds inter-series clock skew under the weak assumption
    that neither market reacts before the release).
Consequence: no cross-market hypothesis may be tested at horizons < 10× the measured skew bound.

## I-4 L3 field-semantics check
On 3 sessions: join Bid-series and Ask-series events to Last-series trades at identical ms.
Tests: does the Bid/Ask "volume" field (mean ≈ 1.8) equal trade size at bid/ask (→ it is a
trade-split field), track displayed BBO size (→ genuine L3), or neither (→ unknown, treat as
unusable)? Decision rule: L3 declared usable ONLY if the field is demonstrably displayed
size; otherwise campaign proceeds at L2 (prices only) and S8-size stays BLOCKED.

## I-5 Event-rate & pipeline benchmark
One full session exported at full detail: rows, bytes, runtime → sets chunking policy for
the ~205-session export (est. 0.7B rows/yr at L2) and decides parquet partitioning.

Deliverables: research/scalping_lab/artifacts/instrumentation/*.csv + reports/
DATA_AND_EXECUTION_AUDIT.md. Registry: one seq-0 instrumentation row per item.
