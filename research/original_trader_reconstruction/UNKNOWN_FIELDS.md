# UNKNOWN FIELDS — Class-D registry

Never silently resolve these. Each may be upgraded only by new evidence, with the upgrade
recorded in EVIDENCE_LEDGER.csv and CURRENT_TRUTH.md.

## Track S
- SelTime logic (the strategy is NAMED SelTime — major unresolved component; our old S2
  SelTime experiment must NOT be equated with the author's SelTime)
- T1/T2/T3 signal arbitration policy of the original wrapper
- PullbackEarly setting (not directly observed)
- Exit logic details beyond exit-on-session-close
- Re-entry policy (trade-count gap 4,351 vs 2,915 must be explained)
- Long/short asymmetric rules (only if evidence demands)
- Exact data series the trader's long-history report used (contract merge policy, §12)

## Track SD
- Full strategy name after "RKSelTimeDSTM" (truncated)
- DSTM expansion
- LossLimit semantics (2500 / 4000): per-trade cap vs session realized vs
  realized+unrealized vs kill-switch vs strategy-loss threshold vs flatten+disable;
  reset boundary; post-breach behavior

## Track V
- Exact BidAskPrice_RealVolume algorithm
- Meaning of "VWAP Amount = 5"
- Which distribution the percentile ladder (95/75/50/25/5) ranks
- Trend definition (EMA slope? price vs EMA? VWAP relation? persistence?)
- Signal trigger (percentile crossing/acceptance/rejection/continuation/reversal?)
- What Signal Close Threshold (10%) applies to
- Exact meaning of Signal Quantity Per Trend = 3 (Class C: likely max three signal events
  per trend episode — remains labeled inference)
- What Signal Split = 5 bars enforces exactly

## Track B
- Entire mechanism; family identity
- Cropped tokens: 19?, 18?, 14?, 45?, 20?, 180? (store RAW_VISIBLE_TOKEN vs
  POSSIBLE_INTERPRETATION separately; no silent completion)

## Track P
- Trade Performance report filters (account-level? subset of strategies?)
- Position semantics: H1 (account ±1 total) vs H2 (per-strategy qty=1, overlap)

## Cross-cutting
- Whether Break at EOD was invariant across versions
- Which commission template was active per screenshot
- Whether the ~90/180?/3/6/9 sequence is a late Solar retune (POSSIBLE_LATE_SOLAR_VERSION
  — association unproven)
- Which 2026 headline weeks belong to which family
