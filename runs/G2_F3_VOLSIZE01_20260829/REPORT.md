# G2_F3_VOLSIZE01 — RESULT: **MC-51 FAIL · MC-38 FAIL · expected-FAIL throttle leg materialized**

Spec committed `bb426af` pre-result. Trials G00025/G00026. Gates in `out/gate_table.txt`;
matched mean exposure enforced IN the table (0.890048 = 0.890048); expanding calibration only
(first usable date printed 2007-01-29). Classification: RISK SPECIFICATION.

> **Extremes-only vol-managed sizing does not improve NQ geometric growth at matched exposure**:
> timing −0.0083 log-wealth (V1 FAIL), below its own null p95 (V3 FAIL), era-inconsistent (V4
> FAIL). **The one thing it does buy is tail: maxDD 18.69% vs 24.82% (V2 PASS)** — a pure
> insurance trade paying ~0.8% of log-wealth over 20 years. The literature's diversified-factor
> gains do not transfer to single-instrument NQ, exactly as the honesty clause anticipated.
> **Drawdown-throttle folklore: −0.238 log-wealth** (expected-FAIL, materialized, closed cheaply).

> **MC-38: HAR-class forecasting demolishes the plain 21d input (QLIKE 0.164 vs 0.287, DM
> p≈1e-11) but the RS−/overnight refinement adds nothing (p = 0.858)** — and the sharper input
> made the SIZING worse (−0.021 vs +0.019 on the same subset): better vol forecasts sharpen the
> *forecast*, not the *timing premium*, which V1–V4 say does not exist here.

⚠️ Substrate caveat (from DELEV01's same-day defect finding): this run's percent-return basis
carries era-scale attenuation from the additively back-adjusted series. The FAIL verdicts stand
(distortion attenuates, it does not manufacture), but the honest revival condition is a retest on
a ratio-adjusted series — recorded, not scheduled.

**Closure scope:** *extremes-only trailing-RV-decile sizing of NQ exposure, 2006–2026-05, this
cost model.* **`LIVE ENABLED = NO` · $0 · no Sharpe printed (per spec).**
