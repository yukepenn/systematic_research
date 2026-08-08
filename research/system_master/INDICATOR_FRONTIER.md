
## SMV2G (2026-08-08): HTF mechanism plateau — CONFIRMED (7/8 neighbors improve)
Identical x1.25 tilt through 8 alternative daily HTF-state definitions (SMA20/100,
EMA50, Donchian50-mid, ret50/ret100 sign, SMA50-slope, dual SMA50&200): 7/8 improve
Sharpe (+0.016..+0.097; only ret50 flat at -0.006). SM08's SMA50 (+0.072) is mid-pack,
not the argmax (SMA20 +0.097) - the effect is the MECHANISM (long-horizon directional
agreement), not a fitted cell. Deployed form stays SMA50. Gate >=6/8: PASS.
Seq 335-342; runs/SMV2G_HTF_MECHANISM/out/results.csv.

## SMV2J JOB1 harness (2026-08-08, seq 366-367) — VR and ER KILLED
Variance ratio (9 cells) and Kaufman ER (3 cells) vs next-session SOLAR_DUAL_HTF PnL with
sigma460 + HTF controls: 0/12 cells reach |t_NW|>2; plateau criterion fails badly (rel-range
3.6-5.4 vs <0.30); states are orthogonal to deployed controls (|corr| ≤ 0.14) so this is a
genuine no-signal result, not collinearity. Old regime: zero sign reversals (8 same-sign, 4
flat). The DR-prior "H1/H3 cluster" was not borne out (corr 0.18). Red-team CONFIRMED.
Queue advances per DR pass B sequencing: B-H2 Kalman innovation whiteness + B-H4 BOCPD regime
age are the next JOB1 candidates (separate frozen spec).
