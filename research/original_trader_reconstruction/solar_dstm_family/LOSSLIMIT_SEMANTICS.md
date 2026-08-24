# LOSSLIMIT SEMANTICS — Track SD adjudication (2026-08-23)

**Verdict: PARTIALLY IDENTIFIED — session-level semantics (B or C) weakly favored;
per-trade semantics (A) behaviorally INERT at the observed values; exact variant not
identifiable from weekly aggregates.** (Directive §40 expected outcome: "LossLimit
semantics may remain partial".)

## Measured behavior of each implementable semantic (on frozen OTR-S-CAND1)

Canonical window (2023-01→2025-01, 539 sessions), deltas vs no-LossLimit base
(4,665 trades / $253,735 / DD −$32,465 / worst trade −$4,445):

| Semantic | LL=2500 | LL=4000 |
|---|---|---|
| A per-trade MTM cap | −3 trades, −$1.8k | −1 trade, −$0.9k |
| B realized-session cap (no new entries) | −184 trades, −$17.6k | −78 trades, −$1.5k |
| C session-MTM flatten+disable | −1,142 trades, −$66.9k, hold 84.1 | −552 trades, −$48.0k |

## Reasoning

1. **A is inert**: with the Solar 44.75-pt stop structure, single-trade losses of $2,500+
   are 0.06% of trades. A trader does not display, and then CHANGE (2500→4000), a
   parameter that never fires — weak Class-C inference that LossLimit is session-level.
2. **B vs C**: both bind at realistic frequency (a losing NQ session at 1 contract
   reaches −$2,500 every 2-4 weeks). On the four late-2025 target windows the base
   candidate and B_2500/B_4000/C_4000 are all within noise of the observed weekly
   fingerprints (e.g. B_2500 gives n=59 vs target 60 in W20251130); C_2500 visibly
   damages W20251228 (20 trades vs 31 observed) — mild evidence AGAINST the most
   aggressive variant at LL=2500 in that era, IF those weeks are SD.
3. Weekly aggregates fundamentally cannot separate "stop new entries" from
   "flatten+disable" — that distinction needs a session-level PnL trace or an intraday
   screenshot of a stop-out day. UNKNOWN_FIELDS.md stays open on this point.

## Collapsed semantics map (directive §13 A-F)

- A per-trade cap → implemented, INERT at 2500/4000
- B realized session cap → implemented (entries blocked; open position exits normally)
- C realized+unrealized session cap → implemented (flatten + disable until next session)
- D daily kill switch → behaviorally identical to C (flatten+disable)
- E max strategy-loss threshold → not adjudicable from weekly windows (never resets;
  would show as the strategy permanently stopping — not observed: trader kept trading)
- F flatten+disable until next session → identical to C

Reset boundary: per-session (18:00 ET) assumed — consistent with Break-at-EOD/intraday-flat
evidence (AS-10). Post-breach: B keeps managing the open trade; C is flat. Both consistent
with "止损也很严格" style statements only if session-level.

Artifacts: runs/OTR_SD1_LOSSLIMIT/out/{results.json, deltas.csv}. DSTM expansion remains
Class D UNKNOWN (zero repo/source hits; never invent).
