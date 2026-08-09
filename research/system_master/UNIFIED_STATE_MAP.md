# UNIFIED_STATE_MAP — U0 shared causal state table

**Built:** 2026-08-09, opening the CONTINUOUS SYSTEM EVOLUTION phase (post SYSTEM_SCIENCE_20260809
closure). Source: `runs/U0_UNIFIED_STATE/src/01_build_state_table.py` →
`runs/U0_UNIFIED_STATE/out/u0_state_table.parquet` (540,232 bars × 79 columns, one row per
3-minute bar, 2022-01-03 .. 2026-07-31).

## Why this exists

The prior campaign (SA0 through SYN) treated Product A and Product B as separately-studied
objects. The owner's 2026-08-09 CONTINUOUS SYSTEM EVOLUTION directive reframes them as **two
policies reading the same latent market state** (sec2): Solar13 → HTF tilt → B-MOM → a combined
score `M`, then Product B maps that score to `{-1,0,+1}` and Product A maps the same drivers
(with its own K-coefficients and short-halving overlay) to continuous MNQ exposure `[-13,+13]`.
U0 builds that shared state layer ONCE so every downstream family (U1 session heterogeneity, U3
hold/exposure, U4 short-side, U5 soft weighting, U6 Product-A path-dependence, U7 2026-regime
explanation) reads from one verified source instead of five re-derivations.

## Two windows, kept mechanically distinct

- **Canonical dev window**: 2022-01-03..2026-05-29 (`is_health_only_bar == False`). Every formal
  promotion comparison in this and prior campaigns uses this window. The build script's
  correctness gate slices the table back to this window and reproduces all three certified nets
  *exactly*: Product-B NQ $301,915.92, Product-B MNQ $28,587.10, Product A $177,924.40.
- **Health-only extension**: 2026-06-01..2026-07-31 (`is_health_only_bar == True`, 45 new
  sessions). Bar data already present in the repo (not newly acquired), already read once for a
  different purpose in SM11_HOLDOUT_READ (`CURRENT_TRUTH.md` Wave-18: "nothing left to seal" for
  this window) — reused here for **observational** health monitoring only, never as a tuning
  sample. Data ≥2026-08-01 remains sealed per `research/operational/LOCKED_FORWARD.md` and was
  not read. Every downstream family must report canonical-window and extended-window results
  **separately** (directive sec34) — `is_health_only_bar` makes that split mechanical.

Extended-window (through 2026-07-31) totals, for reference: Product-B NQ $360,590.96 (canonical
$301,915.92 + $58,675 in the 45 new sessions), Product-B MNQ $34,380.30 (+$5,793), Product A
$212,894.50 (+$34,970). Consistent with SA0's current-health HEALTHY finding; not further
interpreted here — that is H0/CURRENT_EDGE_HEALTH_PRODUCT_A.md's job.

## Disclosed approximation

Genuine MNQ OHLC prices exist in this repo only through 2026-05-29
(`runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv`, 519,703 of 540,232 bars). For the 20,529
health-only bars, **Product-B's MNQ leg** prices on NQ OHLC as a proxy (`is_mnq_genuine_price`
column marks which bars are genuine vs proxy) — both instruments track the identical CME
Nasdaq-100 index at the same price levels, differing only in the point-value/tick-dollar
multiplier, and this repo's parity docs already treat small NQ/MNQ fill residuals as an accepted
approximation class. **Product A needs no such proxy**: `pa0_substrate.product_a_exec` was found,
on inspection, to price Product A on NQ's own OHLC throughout (the PV_MNQ=$2/pt dollar multiplier
is applied directly to NQ price levels; no separate MNQ price series was ever used for Product A,
canonical or extended) — matched here verbatim, so Product A's leg is genuine data end-to-end.

## Column groups

| Group | Columns | Notes |
|---|---|---|
| Identity | `t_idx, time, sess_date, hm, year, is_health_only_bar, is_mnq_genuine_price` | `hm` = ET time-of-day as hhmm int |
| OHLCV | `open, high, low, close, volume` | NQ bars (see proxy note above for Product-B MNQ leg pricing) |
| Shared drivers | `T, Tp, HTF_tilt_state, B, M, M_change, M_slope_20` | `M_slope_20` = causal 20-bar OLS slope of `M` itself (R4-style, applied to the decision score, not just close) |
| Solar13 ensemble | `n_bullish, n_bearish, n_flat_members, vote_dispersion, fast_member, slow_member` | From the 13-member `PEND` array (VM=6..30 step 2), reused from `health_substrate.PEND` |
| C4 windows | `entry_blocked_c4, forced_flat_c4` | Same 30min/21min-before-close windows for both products |
| Volatility/range | `sigma460_atr_proxy_pts, bar_range_pts, range_over_atr, short_term_vol_ratio, vol_compression_ratio` | |
| Price-location | `clv, clv_signed, sess_vwap, vwap_dist_pts, vwap_disp_atr, roll_hi20, roll_lo20, rejected_upper_break, rejected_lower_break` | `clv`∈[0,1], `clv_signed`=2·clv−1; rejection flags generalized from R5's entry-only definition to every bar |
| Trend/efficiency | `close_slope_20, close_slope_20_atr, trend_efficiency_20, range_efficiency_20, ret_1, ret_5, ret_20` | Kaufman-style causal efficiency ratios |
| Volume | `vol_avg20, vol_surprise, direction_x_volume` | `vol_surprise[t]` uses the **prior**-bar trailing 20-avg (excludes bar t itself), matching R5's exact convention |
| Session phase | `session_phase, is_rth, minutes_since_session_open, minutes_to_session_close, minutes_since_rth_open, minutes_to_rth_close` | Phase boundaries are standard, publicly-documented futures-session conventions (Asia/London/US premarket/RTH open-mid-close/post-RTH) — **not fit to this system's PnL**, per directive sec29 |
| Product B | `position_B, action_B, block_id_B, age_bars_B, run_pnl_B_dollars, MFE_B_dollars, MAE_B_dollars, giveback_B_dollars, giveback_ratio_B, bar_pnl_B_nq_dollars, bar_pnl_B_mnq_dollars` | `action_B`∈{ENTRY,HOLD,EXIT,REVERSAL,FLAT}; block = contiguous same-sign run (2,064 blocks total, matches SA0 current-health's independently-built block ledger) |
| Product A | `M_A_raw, target_exposure_A, action_A, block_id_A, age_bars_A, run_pnl_A_dollars, MFE_A_dollars, MAE_A_dollars, giveback_A_dollars, giveback_ratio_A, bar_pnl_A_dollars` | `action_A`∈{ENTRY,SCALE_IN,SCALE_DOWN,HOLD,FLIP,EXIT,FLAT}; `M_A_raw` is the pre-round/clamp continuous score, `target_exposure_A` is the actual (rounded, clamped, C4-gated) integer path |

## Action-state definitions (bar-to-bar, causal)

- **Product B** (`position_B`∈{-1,0,1}): ENTRY (0→±1), EXIT (±1→0), REVERSAL (sign flip in one
  bar — real: `build_pos_seq` allows a direct long→short transition when M crosses the opposite
  entry threshold before the exit threshold releases), HOLD (same sign), FLAT (stayed at 0).
  Counts: 1,972 ENTRY / 1,972 EXIT / 92 REVERSAL / 203,252 HOLD / 332,944 FLAT bars.
- **Product A** (`target_exposure_A`∈[-13,13] int): ENTRY, EXIT, FLIP (sign change), SCALE_IN
  (same sign, |exposure| grows), SCALE_DOWN (same sign, |exposure| shrinks), HOLD (same sign,
  same magnitude), FLAT. Counts: 3,604 ENTRY / 3,604 EXIT / 1,385 FLIP / 8,481 SCALE_IN / 8,367
  SCALE_DOWN / 395,392 HOLD / 119,399 FLAT bars — direct confirmation of PA0's finding that
  scale-in/scale-down activity is a large share of Product A's bar-level behavior, not a rare edge
  case.

## Correctness discipline

Every reused formula (Solar13 member construction, T/Tp/HTF-tilt/B/M, Product-B hysteresis
decision layer, Product-A's K-coefficient mapping + short-halving overlay + C4 partial-size
gating, `onelot_exec`/`product_a_exec` pricing) is either imported directly from an
already-certified module (`health_substrate.py`) or copied verbatim with a byte-for-byte
correctness-gate assert against the certified canonical-window net. No new backtest engine, no
new decision logic, no new pricing convention was introduced by this table — it is a pure
re-expression of already-certified arrays plus new *descriptive* features layered on top.

## Known limitations / not yet in this table

- Genuine order-flow/tick data (`scalping_lab`) is NOT merged in — U2 audits it separately.
- ES/RTY/YM context-market bars (`runs/W18_XINST_BARS/`) are NOT merged in — available for a
  future context-feature pass if U1/U7 motivate one.
- Product-A path-dependent "trip" segmentation uses sign-change blocks (matches how PA0 treated
  exposure paths), not magnitude-change blocks — a trend that scales 3→7→3→0 contracts is one
  block, consistent with treating scale-in/down as within-trip actions, not separate trades.
