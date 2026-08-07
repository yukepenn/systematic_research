# Latest — 2026-08-06 (Phase 1 complete)

**Three Phase-1 experiments + independent external review done, all preregistered (commit `1593ed4`).**

- **SW01b (null control): Type-1 entry timing is real** — baseline $146,440.60 beat all 30 random-entry seeds run through identical exit machinery (p = 0.0323). But the machinery alone (trailing-stop asymmetry) turned random entries into +$12k…+$129k (median $58.6k, 30/30 positive) in this regime, while random hold-to-close was zero-mean (−$15.5k avg). Decomposition: ≈ $56k machinery×regime + ≈ $90k entry timing.
- **SW01c (2022 bear year): gate PASS, thin** — slip-1 net +$11,385.72, PF 1.012, DD −$44,821. Shorts carried the year (PF 1.071), longs exactly $0.00 → long-side 2023-25 excess is drift beta; short side is a stable weak edge.
- **SW01 (attribution): integrity perfect** (byte-identical export, 100% signal-trade match). Discoveries: 46% of Type-1 signals go untaken (SW03 opportunity set); the thesis chop-veto is **inverted** (4+ flip bucket is the best, PF 1.303 — the planned veto would have deleted 74% of profit); the true dead weight is the lowest path-efficiency quartile (25% of trades, +$157 total); the high-vol tercile carries 58% of net.
- **External review** (5-agent evidence sweep + synthesis): P(positive 12-month forward at 1-tick) ≈ **35–55%**; P(genuine transferable alpha) ≈ 10–20%. Critical falsifiable risk identified: the Analyzer's exit-on-session-close fills at the last close print — a fill that may not exist live. **Next experiment SW02a: timed-exit ladder (16:58/16:55/16:45/16:30). If the close-bucket edge collapses by 16:55, the absolute edge is a marking artifact.** Protocol upgrades adopted: CPCV replaces long-window WFO, daily-P&L-vector archiving for PBO/CSCV, PSR + Harvey-Liu haircut gates, state-dependent slippage overlay, pre-roll bar archive (done), 2025-03→2026-07 reserved as the only vendor-clean OOS window.

Full detail: `research/01_diagnostics/SW01_report.md`, `external_review.md`.
