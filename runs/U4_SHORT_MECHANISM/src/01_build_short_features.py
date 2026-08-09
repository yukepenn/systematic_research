"""
U4 step 1 -- build short-focused causal feature table on top of U0, and per-block
(entry-state) summary tables for Product-B short blocks and Product-A short blocks.

All new features are causal run-length / rolling constructions using only data at-or-before
each bar's own row (consistent with every other column already in U0). No new backtest logic,
no new pricing -- this script only READS u0_state_table.parquet and adds descriptive columns.

Outputs (this run's own dir only):
  out/u4_bars_with_features.parquet   -- full 540,232-row table + new feature columns (slim,
                                          only the columns needed downstream, to keep file small)
  out/blocks_B_short.parquet          -- one row per Product-B short block, entry-state features
  out/blocks_A_short.parquet          -- one row per Product-A short block, entry-state features
  out/build_log.json
"""
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = ROOT + r"\runs\U0_UNIFIED_STATE\out\u0_state_table.parquet"
OUT = ROOT + r"\runs\U4_SHORT_MECHANISM\out"

print("Loading U0 state table...")
df = pd.read_parquet(U0_PATH)
df = df.sort_values("t_idx").reset_index(drop=True)
assert (df["t_idx"].values == np.arange(len(df))).all(), "t_idx must be a dense 0..N-1 row order"
n = len(df)
print(f"  {n} rows, {df['sess_date'].nunique()} sessions")

# ---------------------------------------------------------------------------
# New causal features (row-order based, matches U0's own convention for
# M_slope_20/ret_20/etc: continuous causal rolling constructs computed over the
# full row order, not reset per session -- Product B/A are flat at session
# close but the underlying M/Solar13 state is a continuous causal signal).
# ---------------------------------------------------------------------------

M = df["M"].to_numpy()
fast = df["fast_member"].to_numpy().astype(np.int64)

def causal_streak_negative(x):
    """For each t, count consecutive PRIOR bars (t-1, t-2, ...) with x<0, stopping at the
    first non-negative prior bar or the start of the series. Bar t itself is NOT included
    (this is 'how long has the state already been negative coming INTO this bar')."""
    neg = (x < 0).astype(np.int64)
    streak = np.zeros(len(x), dtype=np.int64)
    run = 0
    prev_neg = np.zeros(len(x), dtype=np.int64)
    prev_neg[1:] = neg[:-1]
    for i in range(len(x)):
        streak[i] = run
        run = run + 1 if prev_neg[i] else 0
    return streak

def causal_streak_positive(x):
    pos = (x > 0).astype(np.int64)
    streak = np.zeros(len(x), dtype=np.int64)
    run = 0
    prev_pos = np.zeros(len(x), dtype=np.int64)
    prev_pos[1:] = pos[:-1]
    for i in range(len(x)):
        streak[i] = run
        run = run + 1 if prev_pos[i] else 0
    return streak

print("Building downtrend-age (M<0 streak, fast_member<0 streak)...")
df["downtrend_age_M"] = causal_streak_negative(M)
df["downtrend_age_fast"] = causal_streak_negative(fast.astype(float))
print("Building uptrend-age (mirror, for long-side symmetry / sanity only)...")
df["uptrend_age_M"] = causal_streak_positive(M)

print("Building recent V-reversal frequency (sign(M) flips in trailing 20/40 bars, causal)...")
sign_M = np.sign(M)
flip = np.zeros(n, dtype=np.int64)
flip[1:] = (sign_M[1:] != sign_M[:-1]).astype(np.int64) & (sign_M[1:] != 0)
flip_s = pd.Series(flip)
# trailing window of bars strictly BEFORE t: shift(1) then rolling sum
df["reversal_freq_20"] = flip_s.shift(1).rolling(20, min_periods=1).sum().to_numpy()
df["reversal_freq_40"] = flip_s.shift(1).rolling(40, min_periods=1).sum().to_numpy()

# Sign-flipped prior-selloff magnitude convenience columns (more-negative-original => bigger
# positive value here, i.e. "how big was the prior down-move")
df["prior_selloff_ret20"] = -df["ret_20"]
df["prior_selloff_slope_atr"] = -df["close_slope_20_atr"]

# M_change / M_slope_20 already exist (decay signal proxies). |M| strength:
df["abs_M"] = df["M"].abs()

print("New feature columns added:", [
    "downtrend_age_M", "downtrend_age_fast", "uptrend_age_M", "reversal_freq_20",
    "reversal_freq_40", "prior_selloff_ret20", "prior_selloff_slope_atr", "abs_M",
])

# ---------------------------------------------------------------------------
# Slim full-table export (only columns needed downstream, keeps file manageable)
# ---------------------------------------------------------------------------
keep_cols = [
    "t_idx", "time", "sess_date", "hm", "year", "is_health_only_bar", "close",
    "T", "Tp", "HTF_tilt_state", "B", "M", "M_change", "M_slope_20",
    "n_bullish", "n_bearish", "n_flat_members", "vote_dispersion", "fast_member", "slow_member",
    "sigma460_atr_proxy_pts", "bar_range_pts", "range_over_atr", "short_term_vol_ratio",
    "vol_compression_ratio", "clv", "clv_signed", "vwap_dist_pts", "vwap_disp_atr",
    "rejected_upper_break", "rejected_lower_break", "close_slope_20_atr", "trend_efficiency_20",
    "ret_1", "ret_5", "ret_20", "vol_surprise", "direction_x_volume",
    "session_phase", "is_rth", "minutes_since_rth_open", "minutes_to_rth_close",
    "minutes_since_session_open",
    "position_B", "action_B", "block_id_B", "age_bars_B", "run_pnl_B_dollars",
    "MFE_B_dollars", "MAE_B_dollars", "giveback_B_dollars", "giveback_ratio_B",
    "bar_pnl_B_nq_dollars",
    "target_exposure_A", "M_A_raw", "action_A", "block_id_A", "age_bars_A",
    "run_pnl_A_dollars", "MFE_A_dollars", "MAE_A_dollars", "giveback_A_dollars",
    "giveback_ratio_A", "bar_pnl_A_dollars",
    "downtrend_age_M", "downtrend_age_fast", "uptrend_age_M", "reversal_freq_20",
    "reversal_freq_40", "prior_selloff_ret20", "prior_selloff_slope_atr", "abs_M",
]
slim = df[keep_cols].copy()
slim.to_parquet(OUT + r"\u4_bars_with_features.parquet")
print(f"Wrote {OUT}\\u4_bars_with_features.parquet ({slim.shape})")

# ---------------------------------------------------------------------------
# Block-level tables (entry-state features), Product B shorts
# ---------------------------------------------------------------------------
def build_block_table_B(df):
    short_mask = df["position_B"] == -1
    block_ids = df.loc[short_mask, "block_id_B"].unique()
    rows = []
    for bid in block_ids:
        blk = df[df["block_id_B"] == bid]
        entry = blk.iloc[0]
        last = blk.iloc[-1]
        rows.append({
            "block_id_B": bid,
            "entry_t_idx": int(entry["t_idx"]),
            "entry_time": entry["time"],
            "exit_time": last["time"],
            "sess_date": entry["sess_date"],
            "year": int(entry["year"]),
            "is_health_only_bar": bool(entry["is_health_only_bar"]) or bool(last["is_health_only_bar"]),
            "n_bars": len(blk),
            "net_pnl": float(last["run_pnl_B_dollars"]),
            "MFE_dollars": float(last["MFE_B_dollars"]),
            "MAE_dollars": float(last["MAE_B_dollars"]),
            "giveback_ratio_final": float(last["giveback_ratio_B"]),
            # entry-bar causal state
            "entry_T": int(entry["T"]),
            "entry_HTF_tilt_state": float(entry["HTF_tilt_state"]),
            "entry_B_bmom": float(entry["B"]),
            "entry_M": float(entry["M"]),
            "entry_abs_M": float(entry["abs_M"]),
            "entry_M_change": float(entry["M_change"]),
            "entry_M_slope_20": float(entry["M_slope_20"]),
            "entry_vote_dispersion": int(entry["vote_dispersion"]),
            "entry_fast_member": int(entry["fast_member"]),
            "entry_slow_member": int(entry["slow_member"]),
            "entry_sigma460": float(entry["sigma460_atr_proxy_pts"]),
            "entry_vwap_disp_atr": float(entry["vwap_disp_atr"]),
            "entry_clv_signed": float(entry["clv_signed"]),
            "entry_rejected_lower_break": bool(entry["rejected_lower_break"]),
            "entry_prior_selloff_ret20": float(entry["prior_selloff_ret20"]),
            "entry_prior_selloff_slope_atr": float(entry["prior_selloff_slope_atr"]),
            "entry_downtrend_age_M": int(entry["downtrend_age_M"]),
            "entry_downtrend_age_fast": int(entry["downtrend_age_fast"]),
            "entry_reversal_freq_20": float(entry["reversal_freq_20"]),
            "entry_reversal_freq_40": float(entry["reversal_freq_40"]),
            "entry_vol_surprise": float(entry["vol_surprise"]),
            "entry_session_phase": str(entry["session_phase"]),
            "entry_minutes_since_rth_open": float(entry["minutes_since_rth_open"]),
            "entry_is_rth": bool(entry["is_rth"]),
            "entry_htf_agrees_short": bool(entry["HTF_tilt_state"] < 0),
        })
    return pd.DataFrame(rows).sort_values("net_pnl").reset_index(drop=True)

def build_block_table_A(df):
    short_mask = df["target_exposure_A"] < 0
    block_ids = df.loc[short_mask, "block_id_A"].unique()
    rows = []
    for bid in block_ids:
        blk = df[df["block_id_A"] == bid]
        entry = blk.iloc[0]
        last = blk.iloc[-1]
        rows.append({
            "block_id_A": bid,
            "entry_t_idx": int(entry["t_idx"]),
            "entry_time": entry["time"],
            "exit_time": last["time"],
            "sess_date": entry["sess_date"],
            "year": int(entry["year"]),
            "is_health_only_bar": bool(entry["is_health_only_bar"]) or bool(last["is_health_only_bar"]),
            "n_bars": len(blk),
            "net_pnl": float(last["run_pnl_A_dollars"]),
            "MFE_dollars": float(last["MFE_A_dollars"]),
            "MAE_dollars": float(last["MAE_A_dollars"]),
            "giveback_ratio_final": float(last["giveback_ratio_A"]),
            "entry_max_abs_exposure": int(blk["target_exposure_A"].abs().max()),
            "entry_exposure": int(entry["target_exposure_A"]),
            "entry_T": int(entry["T"]),
            "entry_HTF_tilt_state": float(entry["HTF_tilt_state"]),
            "entry_B_bmom": float(entry["B"]),
            "entry_M": float(entry["M"]),
            "entry_M_A_raw": float(entry["M_A_raw"]),
            "entry_abs_M": float(entry["abs_M"]),
            "entry_M_change": float(entry["M_change"]),
            "entry_M_slope_20": float(entry["M_slope_20"]),
            "entry_vote_dispersion": int(entry["vote_dispersion"]),
            "entry_fast_member": int(entry["fast_member"]),
            "entry_slow_member": int(entry["slow_member"]),
            "entry_sigma460": float(entry["sigma460_atr_proxy_pts"]),
            "entry_vwap_disp_atr": float(entry["vwap_disp_atr"]),
            "entry_clv_signed": float(entry["clv_signed"]),
            "entry_rejected_lower_break": bool(entry["rejected_lower_break"]),
            "entry_prior_selloff_ret20": float(entry["prior_selloff_ret20"]),
            "entry_prior_selloff_slope_atr": float(entry["prior_selloff_slope_atr"]),
            "entry_downtrend_age_M": int(entry["downtrend_age_M"]),
            "entry_downtrend_age_fast": int(entry["downtrend_age_fast"]),
            "entry_reversal_freq_20": float(entry["reversal_freq_20"]),
            "entry_reversal_freq_40": float(entry["reversal_freq_40"]),
            "entry_vol_surprise": float(entry["vol_surprise"]),
            "entry_session_phase": str(entry["session_phase"]),
            "entry_minutes_since_rth_open": float(entry["minutes_since_rth_open"]),
            "entry_is_rth": bool(entry["is_rth"]),
            "entry_htf_agrees_short": bool(entry["HTF_tilt_state"] < 0),
        })
    return pd.DataFrame(rows).sort_values("net_pnl").reset_index(drop=True)

print("Building Product-B short block table...")
blocks_B = build_block_table_B(df)
blocks_B.to_parquet(OUT + r"\blocks_B_short.parquet")
print(f"  {len(blocks_B)} short blocks, net sum ${blocks_B['net_pnl'].sum():,.2f}")

print("Building Product-A short block table...")
blocks_A = build_block_table_A(df)
blocks_A.to_parquet(OUT + r"\blocks_A_short.parquet")
print(f"  {len(blocks_A)} short blocks, net sum ${blocks_A['net_pnl'].sum():,.2f}")

# canonical-window-only cross-checks
canon_B = blocks_B[~blocks_B["is_health_only_bar"]]
canon_A = blocks_A[~blocks_A["is_health_only_bar"]]
log = {
    "n_rows": int(n),
    "n_short_blocks_B_all": int(len(blocks_B)),
    "n_short_blocks_B_canonical": int(len(canon_B)),
    "net_pnl_short_B_all": float(blocks_B["net_pnl"].sum()),
    "net_pnl_short_B_canonical": float(canon_B["net_pnl"].sum()),
    "n_short_blocks_A_all": int(len(blocks_A)),
    "n_short_blocks_A_canonical": int(len(canon_A)),
    "net_pnl_short_A_all": float(blocks_A["net_pnl"].sum()),
    "net_pnl_short_A_canonical": float(canon_A["net_pnl"].sum()),
}
with open(OUT + r"\build_log.json", "w") as f:
    json.dump(log, f, indent=2, default=str)
print(json.dumps(log, indent=2))

# sanity check vs SA0 sec14 short NQ net ($35,112.38, canonical window, Product B)
print("\nSA0 sec14 cross-check (Product B canonical short net, expect ~$35,112.38):",
      f"${canon_B['net_pnl'].sum():,.2f}")
