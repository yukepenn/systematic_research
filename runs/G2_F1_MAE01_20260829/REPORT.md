# G2_F1_MAE01 — RESULT: **PASS (measurement complete) — the intrabar-risk hole is now BOUNDED, and a testimony fell**

Spec committed `c256e21` pre-result. Trial G00020. M1/M2/M3 all PASS; decision rule → **RECORD AND
STOP** (no adoption recommended).

## The measurement (2,131/2,131 trades, per contract, bar extremes)

| MAE pts | p50 | p90 | p95 | p99 | max |
|---|---:|---:|---:|---:|---:|
| all trades | 14.00 | 47.00 | 63.88 | 101.65 | **196.25** (= $3,925/ct; worst position $5,380, a size-2 loss) |

Losers' MAE p50 19.5 / p99 102.4; winners' p50 6.5. MFE p95 176.6 / max 1,271.
**Tick calibration on 70 overlap trades: factor 1.0000, |diff| p95 = 0.000 pts — the SM1M minute
substrate is tick-exact against the dev store** (roll offsets cancel in excursions). Trade-level
maxDD confirmed **$29,492.71**.

## The stop-300 variant

**Never triggers** (max MAE 196.25 < 300): Δnet $0.00, ΔmaxDD 0.00% → clause 2 fails → RECORD AND
STOP. ⚠️ **The W-era risk-menu testimony "300 pts = 13 historical triggers, ~0.7% of gross" does
NOT reproduce on this object** — 0 triggers, 0.000%; that testimony must describe a different
object/era, and may not be quoted for P1/PCT again.

## Standing consequences

1. Incumbent dossier §3 weakest-assumption "no intrabar risk control / MAE unbounded" upgrades to
   **measured**: historical worst intrabar excursion 196.25 pts/ct; a ≥200-pt disaster stop would
   have been free historically (not adopted — sample maximum ≠ bound; any adoption invalidates
   Standard-fill parity per LIVE_READINESS.md:163).
2. The $5,380 worst-position excursion is the honest single-trade tail figure for risk sizing.

**`LIVE ENABLED = NO` · $0 · RISK SPECIFICATION, not alpha.**
