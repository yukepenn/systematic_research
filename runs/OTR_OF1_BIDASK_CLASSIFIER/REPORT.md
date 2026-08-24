# OTR_OF1 — REPORT (2026-08-24)

**Both full window-A tick sessions now yield healthy causal BidAskPrice_RealVolume-class
series** (quote-rule classification, no CrossTrade needed).

## Results

| Session | at-ask | at-bid | inside(tick-rule) | buy-vol share | corr(1m delta, 1m ret) |
|---|---|---|---|---|---|
| s20260511 (v1 export) | 36.9% | 35.7% | 27.0% | 50.35% | **0.662** |
| s20260512 (v3, offset-corrected) | 47.7% | 47.1% | 5.2% | 50.3% | **0.674** |

## DATA DEFECT DISCOVERED (affects scalping_lab too): v3 exporter quote-contract mismatch

s20260512 raw quotes sit a median **892 ticks (~223 pts) ABOVE trade prices** (93.2% of
trades "below bid") while the internal bid-ask spread is normal (median 1.0 pt) — the v3
exporter recorded quote streams from a DIFFERENT contract than the trade stream
(magnitude ≈ the 06-26 vs 09-26 calendar basis). Naive classification is garbage (95%
at-bid, delta-return corr 0.09). **Fix: causal rolling-median offset correction** (median
of mid−trade over trailing 2,000 trades, quotes snapped to grid) restores clean
classification. Suspect list = all 8 SWScalpTickExport_v3 batch-1 sessions (s20250819,
s20250912, s20251028, s20251125, s20260217, s20260302, s20260422, s20260512); v1 sessions
unaffected (s20260511 clean). Flagged for scalping_lab MANIFEST_NOTES follow-up.

## Proxy-vs-real diagnostics (why minute-proxy volume distributions mislead)

Hourly volume-at-price percentile lines from minute close-binned proxy vs real tick
distribution: mean displacement 3-15 ticks, **max up to 86 ticks** at the tails (P5/P25);
60-min VWAP displacement mean ~3 ticks, max ~13. Tail ladder lines (the 5/95 levels) are
the least trustworthy under proxy volume — relevant to any Flux-style reconstruction.

Artifacts: `out/{s20260511_1m.parquet, s20260512_1m.parquet, s20260512_1m_offsetfixed.parquet,
results.json}`.
