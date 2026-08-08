# STOP_OVERLAY_FRONTIER — Complete Stop/Exit Record: FRONTIER CLOSED

_2026-08-08. The stop/exit design space for the Solar architecture, across both prior
campaigns and SM02B/SM03/SM03B. Every family is now closed with evidence._

| family | evidence | verdict |
|---|---|---|
| Split exit ≠ reversal (α/β thresholds) | H-007: monotone degradation, ratio 1.00 best everywhere; "early exits amputate the right tail" (~$131/RT extra friction) | **DEAD** (class) |
| Resting stop orders at ladder | H-011: −$1.88M, 10/10 cells negative; close-basis excess (89% of friction) unrecoverable | **DEAD** |
| Timed exits (16:30/16:45/16:55/16:58) | SW02a + full-history falsification (16:30 "dominance" withdrawn, wins 4/28 pairs) | **DEAD** |
| Pure time-to-progress stop | SM02B: E[remaining] POSITIVE in every pooled (b,q) cell; every rule stops ≥5.2% of top-1% trades | **DEAD** (Q4 = NO) |
| Loss-reactive throttles (skip-after-loss, streak sizing, daily loss limit) | SM02B: post-loss expectancy AT-OR-ABOVE base (trade: +$101 after 3 losses vs +$55 base; E10 day: +$195 after down day vs +$104) | **DEAD — anti-edge** (directive §24 = no) |
| Close-basis disaster stop | SM03 (seq 291-296): algebraically shadowed by the Solar exit — 0-32 triggers possible | **DEAD** (impossible) |
| Intrabar disaster stop m≥1.0·S | SM03B (seq 301-306): tail-safe (retention 0.98-1.00) but best arm ΔmaxDD +3.9% < 5% gate, ΔSharpe +0.04 (P=0.21), 13× member-netting dilution, and WORSENS the 2006-2021 stress (−6% DD, −$8.4k net) | **FAIL** — not promoted |
| Break-even / trailing variants | Subsumed: any tightening inside S is an H-007 variant; the anchor-ratchet IS the trailing stop; wider-than-S forms are the SM03B family | **CLOSED by inheritance** |

## The two structural facts that close this frontier

1. **37.9% of drawdown dollars are pure winner-absence** (SM02 atlas: big-winner
   frequency collapse with normal-or-better left tails) — no exit rule can help these.
2. Losers already exit near −S by construction; the loss mass beyond −1.0·S (42% of
   gross losses) is reachable only intrabar, and cutting it nets ≈ +7% of member-level
   P&L — which **dilutes ~13× at ensemble level** (netting) to sub-threshold.

**Drawdown engineering therefore lives in the exposure/allocation layer** — where it
worked: HTF tilt (SM08 PASS: DD −13.6%), B-MOM/B1 portfolio (SM05 PASS: maxDD −29%,
worst month −$18.2k→−$10.3k), leverage policy (LEVERAGE_FRONTIER). Directive Q3 = NO
within this architecture; Q5 moot; Q26 = the exposure layer, not stops. FACT throughout.
