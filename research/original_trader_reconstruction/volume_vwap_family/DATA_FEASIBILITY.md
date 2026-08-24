# TRACK V — data feasibility verdict (Phase 6, 2026-08-23)

## V-EXACT: BLOCKED PENDING DATA

`BidAskPrice_RealVolume` requires per-trade bid/ask classification. Audit result
(DATA_AUDIT.md, Phase-0):
- Trade-at-bid/ask classification is NOT stored anywhere in the repo.
- Quote-rule classification is BUILDABLE from raw BBO+trade tick streams — but those
  exist for only 48 sampled sessions (2025-08-11→2026-05-20), of which exactly 2 full +
  2 partial fall inside identification window A (2026-05-10→05-22): s20260511, s20260512
  (full); s20260519, s20260520 (capped/partial).
- Full-window exact reconstruction would need NT8-cache re-export → CrossTrade, which is
  EXCLUDED from this campaign (directive §1.7/§39). Escalation-gated; not pursued.
- Window B (2026-08-02→08-14) is LOCKED_FORWARD virgin + no repo data: untouchable.

**Consequence: exact algorithmic identification of the Track-V signal is impossible with
current data. V-EXACT is BLOCKED, not failed.** A 2-session quote-rule micro-probe is the
only exact foothold and cannot adjudicate a 10-session window fingerprint.

## V-PROXY: FEASIBLE (minute OHLCV), with a permanent caveat

Proxy volume state (minute close-price volume distribution) can approximate the
percentile-ladder architecture. ANY V-PROXY result carries the caveat: proxy parity is
NOT exact parity (directive §17); a matching proxy mechanism is at best
"BEHAVIORALLY MATCHED — MECHANISM UNIDENTIFIED" (§40), never "RECONSTRUCTED".

## Frozen architecture facts for any V pass (Class A)

Volume Base=BidAskPrice_RealVolume; Anchor 60 min; VWAP Amount 5; Trend EMA(20);
percentiles 95/75/50/25/5; Signal Quantity Per Trend 3; Signal Close Threshold 10%;
Signal Split 5 bars; NQ 1-minute.

Class-C working interpretation (labeled): a 60-minute anchored volume-at-price
distribution whose 5/25/50/75/95% volume-percentile prices form a ladder ("VWAP Amount
5" = five ladder lines); EMA(20) supplies trend context; ≤3 signal events per trend;
consecutive signals ≥5 bars apart. All open questions remain in UNKNOWN_FIELDS.md.
