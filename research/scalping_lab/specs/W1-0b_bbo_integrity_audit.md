# W1-0b — BBO_INTEGRITY_AUDIT (preregistered; Amendment 3 §1)

Date: 2026-08-08. Purpose: decide whether NT8-reconstructed historical BBO is trustworthy
enough to (a) freeze the "NQ is a 2-3 tick market" claim, (b) promote BBO_EXEC from
diagnostic to primary executable model. Until PASS: C1/C2 = promotion truth.

Known limitation being tested (NT8 docs): Bid/Ask/Last historical series each preserve
internal order, but INTER-series real-time ordering is NOT preserved, especially at shared
timestamps.

## Frozen audit sessions (6, stratified across quarters/regimes, chosen before readout)
s20250814, s20251009, s20251117 (monster day), s20260123, s20260317, s20260506.

## Tests
- **T1 same-timestamp ambiguity**: fraction of Bid events sharing an exact (100ns-field)
  timestamp with ≥1 Ask event; fraction of Last events sharing a timestamp with any quote.
- **T2 ordering sensitivity (the decisive test)**: spread distribution under two extreme
  reconstructions: (i) UNRESTRICTED asof (current method: each Bid event paired with latest
  Ask ≤ t); (ii) SYNC-ONLY: spread measured only at exact same-timestamp Bid∧Ask pairs
  (plausibly the same exchange book snapshot). Metric: time/event-weighted median + P(1t).
  **Decision rule: if SYNC-ONLY median < UNRESTRICTED median by ≥ 1 tick, the 2-3-tick
  claim is ruled RECONSTRUCTION-CONFOUNDED and is demoted to "not established"; if the two
  agree within 0.5 tick, the claim is CONFIRMED-PENDING-T4.**
- **T3 staleness surface**: spread conditional on age of the counter-side quote
  ∈ {≤10ms, ≤50ms, ≤250ms, ≤1s, unrestricted}; report the fraction of book-time in each.
- **T3b outside-BBO decomposition**: trade-outside-[Bid,Ask] rate stratified by
  max(age_bid, age_ask) at trade time {≤50ms, ≤250ms, >250ms} and by whether the trade
  shares a timestamp with a quote event. PASS criterion for BBO_EXEC-on-clean-states:
  outside rate ≤ 2% in the fresh stratum.
- **T4 Tick Replay cross-check**: MCP RunStrategyBacktest cannot enable Tick Replay
  (documented limitation) → requires an owner-run Analyzer session with Tick Replay ON and
  a no-order probe strategy, OR stays open. T4 absence caps the audit verdict at
  PROVISIONAL (never blocks C1/C2-based research).

## Outcomes
- PASS (T2 agree + T3b clean-stratum ≤2%): BBO_EXEC promoted for clean states; spread map
  frozen as fact (PROVISIONAL until T4).
- CONFOUNDED (T2 disagree): spread map retracted to "unknown, ≥1 tick"; BBO_EXEC restricted
  to sync-only snapshots; scalp economics computed under C1/C2 + sync-BBO bounds.
- Either way, all prior spread numbers are re-labeled per the outcome. DoF: audit only.
