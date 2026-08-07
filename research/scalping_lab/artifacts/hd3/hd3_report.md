# W1-4 H-D3 Readout — CLOSED AT 3-MIN RESOLUTION

Date: 2026-08-07. Spec: `specs/W1-4_HD3_cashclose_window.md` (frozen before readout).
Data: 1,095 sessions 2022-01 → 2026-05-31. Zone: ADJACENT_INTRADAY.

| Metric | Value |
|---|---|
| OLS slope (HC1 t) | +0.0293 (t = 0.61, n.s.) |
| Sign agreement | 51.4% (p = 0.36) |
| Gross / net-C1 ticks/day | **+2.61 / −0.26** |
| Net by year 22/23/24/25/26 | +3.0 / −3.4 / −5.1 / +1.8 / +6.1 |
| Era 2022-23 vs 2024-26 | −0.18 vs −0.33 |

**Verdict (frozen rule): not significant → CLOSED at the 3-min construction.** Notable and
recorded honestly: gross is POSITIVE and ≈ 0.9× C1 friction, and the slope sign matches the
imbalance-leak mechanism — the effect is not refuted, it is unresolved at this resolution
(the 15:48→15:54 predictor dilutes the post-15:50 information with 2 pre-publication
minutes). Per the spec, exactly ONE preregistered 1-min reconstruction (predictor strictly
15:50→15:55, target 15:55→16:00, BBO_EXEC) remains permitted and is queued for when the
minute/tick export pipeline exists. DoF charged: 1.
