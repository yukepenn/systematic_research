# FUTURES ALPHA MAP

**State document. Cells are populated ONLY from verified experiments — never invented numbers**
(owner directive §29). Blank = not yet researched. This answers: *where does our alpha actually
come from across markets?*

Quality tags: standalone quality on the weekly-vol basis (the lead metric); NQ corr = daily-PnL
correlation vs the live P1 object on shared dev-window dates; portfolio value from Lane D.

| Market | Asset class | Best mechanism (verified) | Status | Standalone quality | NQ corr | Portfolio value |
|---|---|---|---|---|---|---|
| **NQ** | equity idx | P1/PCT (Solar vol-ratchet ⊕ B-MOM, weekly edge) | LIVE (P1-only, MNQ×3) · research DISCOVERY_CONSUMED | raw $1,394/wk, fixed-DD $1,230/wk, t 4.16, maxDD $22,931 | 1.00 | **ANCHOR** |
| ES | equity idx | Lane-A (P1 transfer) — **CLOSED-BY-POWER** | native lane (Wave 1/2) pending | +$193/wk wv but t 0.58, under MDE, not Bonferroni | **+0.65 (high — not a diversifier)** | low (generalization only) |
| RTY | equity idx | Lane-A — **COST-FRAGILE** | native lane pending | +ve 0-tick only; −$211/wk at 1-tick | +0.27 | none (as transferred) |
| YM | equity idx | Lane-A — **CLOSED-BY-POWER** | native lane pending | +$154/wk wv, t 0.46, under MDE | +0.24 | low |
| ZB | rates | Lane-A — **FAIL (powered −ve)** | 🎯 native lane pending | −$4,179/wk, t −10 (P1 inverts on rates) | **−0.05 (orthogonal! the prize profile)** | **0 as transferred — but ρ says a NATIVE ZB engine is the diversifier to find** |
| CL | energy | — | 🎯 autopsy running (full window) | — | — | — |
| GC | metals | — | daily autopsy running | — | — | — |
| 6E | FX | — | daily autopsy running | — | — | — |
| ZN | rates | — | daily-only / thin 1-min | — | — | — |

_Last verified update: 2026-09-06. **XINST01 Lane-A (transfer benchmark) DONE (`wf_d97689db-200`,
G00056-59): P1/PCT does NOT transfer** — port reproduced NQ to 0.0000%, then 0 of 4 instruments
information-supported. ES/YM show a underpowered whisper (same asset class, high NQ-corr → not
diversifiers); RTY cost-fragile; **ZB is genuinely orthogonal (ρ −0.05) but P1's trend-mechanism
inverts on rates → the diversifier must come from a NATIVE ZB engine, not the transfer.** The
campaign thesis is confirmed: value is in native engines, not porting P1._
