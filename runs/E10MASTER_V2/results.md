# E10MASTER_V2 Results — Flatten1644 direct strategy confirmation: **CONFIRMED_ADOPT**

Date: 2026-08-07. Job b31deef507924a7a (NT8 8.1.8.1, same engine fingerprint as v1).
Spec: `spec.yaml` (committed 02fb163 before execution). Full window 2022-01-02 → 2026-07-31,
Standard fill, 1 tick slippage, Lifetime commission — identical to the v1 validation run.

| | v1 (hold to 17:00) | v2 (Flatten1644) |
|---|---|---|
| Net | $181,079.10 | **$171,389.60** |
| Executions / contracts | 39,903 / 52,126 | 39,777 / 51,966 |
| Commission | $33,881.90 | $33,777.90 |
| Max daily-equity DD | −$40,866 | −$41,766 |
| Daily Sharpe | 0.977 | 0.933 |
| Worst day | −$12,667.20 | −$12,667.20 (identical) |

## Gates (preregistered in spec.yaml)
- **G1 identity**: daily P&L corr 0.997157 ✓
- **G2 cost**: −$9,689.50 = **−5.35%** of v1 net — inside [−8%, 0%] ✓. Larger than the
  attribution study's −3.7% exactly as the spec anticipated: the strategy exits at the
  16:45-bar open (~16:42), giving up 16:42→17:00, not just 16:45→17:00, plus execution.
- **G3 risk flag (2.20% DD increase > 2% line) — investigated, cleared**: per-session
  (v1−v2) delta reconciles to v1's 16:42→17:00 window MTM with corr 0.9947, residual mean
  $0.68/session, max |residual| $283 (8 sessions > $100 — execution-price vs bar-MTM
  approximation). Trough date unchanged (2026-06-04); worst day identical. The deeper DD is
  the legitimate consequence of removing a positive-mean exposure window, not divergent
  positions. NO implementation bug.
- **G4 tail retention**: top-10 v1 days retain 95.81% ✓ (≥ 90%).

## Known edge case (documented, accepted)
2023-04-05: flatten did not execute (bar-stamp gap); the engine session-close backstop
closed 2 MNQ at 17:00:00. Frequency 1/1,183 sessions; margin exposure that day ≈ 2 ×
initial. The IsExitOnSessionClose safety net is the designed second layer and worked.

## Ruling
16:44 flatten **finally confirmed** per Owner Amendment 1 §11. `SolarWaveE10Master_v2`
(Flatten1644=true) is the live-operations default going forward; v1 remains the frozen
research champion for analytics continuity. Realized cost of the margin-cliff exit:
≈ $2,100/yr (5.35% of net) — purchased: intraday-margin capital floor ($1k vs $43.4k),
no NT8 risk-desk forced liquidations, aggressive compounding tiers margin-feasible.
Comparison code: `compare.py`; daily join: `out/daily_v1_v2.csv`.
