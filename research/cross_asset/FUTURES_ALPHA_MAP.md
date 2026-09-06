# FUTURES ALPHA MAP

**State document. Cells are populated ONLY from verified experiments — never invented numbers**
(owner directive §29). Blank = not yet researched. This answers: *where does our alpha actually
come from across markets?*

Quality tags: standalone quality on the weekly-vol basis (the lead metric); NQ corr = daily-PnL
correlation vs the live P1 object on shared dev-window dates; portfolio value from Lane D.

| Market | Asset class | Best mechanism (verified) | Status | Standalone quality | NQ corr | Portfolio value |
|---|---|---|---|---|---|---|
| **NQ** | equity idx | P1/PCT (Solar vol-ratchet ⊕ B-MOM, weekly edge) | LIVE (P1-only, MNQ×3) · research DISCOVERY_CONSUMED | raw $1,394/wk, fixed-DD $1,230/wk, t 4.16, maxDD $22,931 | 1.00 | **ANCHOR** |
| ES | equity idx | 🔴 **LEAD: raw daily MR = Sharpe 0.78, +$370/wk** (surfaced as the W2 residual control; residual-hedge FAILED, killed the signal) | 🎯 **W2b-EQ-MR: raw ES-MR judged on PnL-ρ-to-P1** (opposite structure to P1 momentum → may diversify at price ρ0.94) | Sharpe 0.78 in-sample (needs full test) | price +0.94; **PnL-ρ-to-P1 UNMEASURED = the question** | 🎯 potentially high IF PnL-orthogonal to P1 |
| RTY | equity idx | Lane-A P1 cost-fragile; native = MR (VR<1), drift lives overnight | native queued (extend after ES) | — | +0.75 | low unless residual |
| YM | equity idx | Lane-A P1 fails; **native = value/growth residual MR** (price-weighted, MR) | W2 residual (extend after ES) | — | +0.74 | via residual only |
| ZB | rates | Lane-A P1 INVERTS; **native = MR every horizon + sharp 08:30 macro-vol** | 🎯 W2-ZB-MACRO + W2-ZB-VOLSTATE queued | — (native untested) | **+0.06 (orthogonal — the prize)** | 🎯 **highest — orthogonal + native MR/vol structure** |
| CL | energy | autopsy done — **structure is in VOLATILITY/EVENT, not price-trend** (pit returns ≈ random walk; EIA Wed-10:30 = powered vol shock, 0 directional edge; multi-day MR) | native Wave-2 queued: H1 EIA-vol-capture (top EV), H2 shock-MR, H3 settlement | — (no engine yet) | **+0.049 daily (orthogonal — prize profile; rising to +0.27 in 2025, watch)** | 🎯 high IF a vol/event engine clears the bar — orthogonal to NQ |
| GC | metals | — | daily autopsy running | — | — | — |
| 6E | FX | autopsy done (daily 2009+) — **direction ≈ random walk** (VR≈1, no TSMOM/day-type); only robust structure = vol clustering | native: month-end hedge-flow / carry (needs ext. rate data) / vol-corr risk-router — all modest | — | **+0.15 but REGIME-VARYING** (−0.30..+0.50; loses diversification in crises) | modest — weaker prize than ZB/CL |
| GC | metals | autopsy done (daily 2009+) — **MEAN-REVERTS every horizon** (VR<1); vol strongly clustered; neg-skew crash tail (liquidation, not equity) | 🎯 **W2-GC-MR (buy-the-washout, best money-engine shot — cost 10× under the ~7bps edge)**; W2-GC-VOL (regime) | — (native untested) | **+0.07 (orthogonal — the prize)** | 🎯 **high — orthogonal + a measured directional MR edge that cost won't kill** |
| ZN | rates | — | daily-only / thin 1-min | — | — | — |

_Last verified update: 2026-09-06. **XINST01 Lane-A (transfer benchmark) DONE (`wf_d97689db-200`,
G00056-59): P1/PCT does NOT transfer** — port reproduced NQ to 0.0000%, then 0 of 4 instruments
information-supported. ES/YM show a underpowered whisper (same asset class, high NQ-corr → not
diversifiers); RTY cost-fragile; **ZB is genuinely orthogonal (ρ −0.05) but P1's trend-mechanism
inverts on rates → the diversifier must come from a NATIVE ZB engine, not the transfer.** The
campaign thesis is confirmed: value is in native engines, not porting P1._
