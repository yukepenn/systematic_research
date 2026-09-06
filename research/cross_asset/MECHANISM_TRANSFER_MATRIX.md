# MECHANISM TRANSFER MATRIX

**State document. Cells filled ONLY from verified experiments** (owner directive §30). This
answers the strategic question: *which effects are UNIVERSAL, which are ASSET-CLASS specific, and
which are MARKET-NATIVE?* — itself a durable research asset.

Cell legend: ✅ = verified edge at scope · ✗ = tested, no edge (with run id) · ? = untested ·
`desc:` = descriptive autopsy finding (DISCOVERY_CONSUMED, not a verified edge) · n/a. Every
✅/✗ must cite a run + ledger trial; do not write a cell from intuition.

> ⭐ **HEADLINE (Wave-1 autopsies, 2026-09-06): NQ is the MOMENTUM OUTLIER of the complex.** Every
> autopsied market (ES/RTY/YM/ZB/CL) is MORE MEAN-REVERTING than NQ at every scale (daily VR<1,
> large moves reverse), whereas NQ continues (VR>1 — its fade graveyard closed because continuation
> won). So P1's continuation mechanism is NQ-native and the cross-asset engines must be
> MEAN-REVERSION / VOL-EVENT, not trend. ρ-to-NQ (daily point returns): ES 0.94, RTY 0.75, YM 0.74,
> **ZB 0.06, CL 0.05** (the orthogonal prizes).

| Mechanism family | NQ | ES | RTY | YM | ZB | CL | GC | 6E | ZN |
|---|---|---|---|---|---|---|---|---|---|
| P1/PCT composite (trend-vol-ratchet ⊕ B-MOM), transferred | ✅ (native) | ✗ underpowered whisper (G00056) | ✗ cost-fragile (G00057) | ✗ underpowered whisper (G00058) | ✗✗ inverts, powered −ve (G00059) | ? | ? | ? | ? |
| trend / momentum persistence (as a native family) | ✅ (P1 core) | ? | ? | ? | ? | ? | ? | ? | ? |
| breakout / range expansion | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| mean reversion (daily/multi-day) | ✗ (fade graveyard — NQ continues, VR>1) | desc: MR VR(10)=0.75 (W1) | desc: MR (W1) | desc: MR VR(10)=0.75 (W1) | desc: MR every horizon (W1) | desc: multi-day MR (W1) | **desc: MR every horizon, prior-down→+7bps t2.94 (W1)** | desc: RW, VR≈1 (W1) | ? |
| volatility clustering (forecastable RV) | ✅ (P1 uses; also VOLSIZE01) | desc: RV acf 0.69 (W1) | ? | desc: RV acf 0.72 (W1) | desc: RV acf 0.58 (W1) | desc: RV long-memory (W1) | **desc: RV acf +0.17, regime-persistent (W1)** | desc: only robust structure (W1) | ? |
| scheduled-macro VOL/event (release) | desc: FOMC vol EXPANDS, 0 dir edge (G2_F12) | ? | ? | ? | desc: 08:30 highest-vol, native (W1) | desc: EIA Wed-10:30 powered vol shock, 0 dir edge (W1) | ? | ? | ? |
| index-residual MR (point-hedged vs NQ) | n/a (anchor) | desc: ~0-beta residual candidate (W1) | ? | desc: value/growth residual (W1) | n/a | n/a | n/a | n/a | n/a |
| compression → expansion | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| session / auction structure | partial (ON-touch, IB-ext banked facts) | ? | ? | ? | ? | ? | ? | ? | ? |
| path organization (ER/entropy) | ✗ (EVENTTIME closed) | ? | ? | ? | ? | ? | ? | ? | ? |
| shock continuation | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| volatility state (as sizing) | ✗ (VOLSIZE01 tail-only) | ? | ? | ? | ? | ? | ? | ? | ? |
| cross-asset / relative state | ✗ (ESNQ null; ZB→NQ null) | ? | ? | ? | ? | ? | ? | ? | ? |

**Cross-market learning rule (§31):** when a market reveals a robust mechanism (e.g. CL shock-state,
GC compression), test that MECHANISM cheaply on the others — controlled scientific transfer, never
blind parameter porting. Record the result here.

_Last verified update: 2026-09-06 (scaffold; NQ column from closed GENESIS/WEEKLY_EDGE results)._
