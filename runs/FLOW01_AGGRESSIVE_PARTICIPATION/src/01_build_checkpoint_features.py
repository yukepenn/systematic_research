"""FLOW01 step 1 -- build in-position DECISION-CHECKPOINT features (not entry-only events).

Reuses:
  - runs/U9_TRUE_MICROSTRUCTURE's frozen prequential design (session is the unit of
    independence; 37 BBO-confirmed sessions; session-block bootstrap only).
  - runs/U9B_MICROSTRUCTURE_ALPHA/src/01_build_event_features.py's exact BBO-alignment
    pattern (60s causal window ending at each bar's own close, same session-exclusion list,
    same avg_spread_ticks / quote_intensity / ret1s_vol definitions).

NEW here (per FLOW01 addendum C6/C7): checkpoints are EVERY 3-min bar with position_B != 0
(not just ENTRY bars) -- decisions to hold/flatten/reverse WHILE ALREADY IN A POSITION.
"""
import os, glob, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

GRID_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
EXCLUDE_SESSIONS = {"20250811", "20250924", "20260430"}  # documented 0% BBO server holes (U9)

# ---------------------------------------------------------------- 37 BBO-confirmed sessions
files = sorted(glob.glob(os.path.join(GRID_DIR, "*.parquet")))
sess_dates = []
for f in files:
    tag = os.path.basename(f).replace(".parquet", "").replace("s", "")
    if tag in EXCLUDE_SESSIONS:
        continue
    d = pd.Timestamp(f"{tag[:4]}-{tag[4:6]}-{tag[6:8]}").date()
    sess_dates.append((d, f))
print(f"[FLOW01] {len(sess_dates)} BBO-confirmed sessions "
      f"({sess_dates[0][0]} .. {sess_dates[-1][0]})", flush=True)
sess_date_to_file = {d: f for d, f in sess_dates}
sess_date_set = set(sess_date_to_file)

# ---------------------------------------------------------------- correctness gate
# Not building a new pos_seq/exec path (per U9/U9B precedent, this family reads U0's already
# certified bar_pnl_B_nq_dollars column read-only). Sanity-check we are reading the correct,
# uncorrupted column before using it as an outcome: full canonical-window sum must reproduce
# the certified Product-B NQ net exactly.
u0_full = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                           columns=["t_idx", "time", "sess_date", "is_health_only_bar", "position_B",
                                    "action_B", "block_id_B", "bar_pnl_B_nq_dollars",
                                    "sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr", "M"])
canon_net = float(u0_full.loc[~u0_full["is_health_only_bar"], "bar_pnl_B_nq_dollars"].sum())
CERTIFIED_B_NQ = 301915.92
assert abs(canon_net - CERTIFIED_B_NQ) < 1.0, \
    f"CORRECTNESS GATE FAILED: canonical bar_pnl_B_nq_dollars sum {canon_net:.2f} != certified {CERTIFIED_B_NQ}"
print(f"[FLOW01] correctness gate PASSED: canonical-window bar_pnl_B_nq_dollars sum "
      f"= {canon_net:.2f} (certified {CERTIFIED_B_NQ})", flush=True)

# ---------------------------------------------------------------- checkpoints on the 37 sessions
u0_full["sess_date"] = pd.to_datetime(u0_full["sess_date"]).dt.date
u0_sub = u0_full[u0_full["sess_date"].isin(sess_date_set)].sort_values("t_idx").reset_index(drop=True)
print(f"[FLOW01] {len(u0_sub)} U0 bars fall on these {len(sess_date_set)} sessions "
      f"(out of {len(u0_full)} total)", flush=True)

# next-bar action / contiguity (for the PRE_EXIT group)
u0_sub["next_action_B"] = u0_sub["action_B"].shift(-1)
u0_sub["next_t_idx"] = u0_sub["t_idx"].shift(-1)
u0_sub["next_sess_date"] = u0_sub["sess_date"].shift(-1)
contiguous_next = (u0_sub["next_t_idx"] == u0_sub["t_idx"] + 1) & (u0_sub["next_sess_date"] == u0_sub["sess_date"])

checkpoints = u0_sub[u0_sub["position_B"] != 0].copy()
checkpoints["is_hold_checkpoint"] = checkpoints["action_B"] == "HOLD"
checkpoints["is_pre_exit_checkpoint"] = (
    contiguous_next.loc[checkpoints.index] &
    checkpoints["next_action_B"].isin(["EXIT", "REVERSAL"])
)
checkpoints["side"] = np.sign(checkpoints["position_B"]).astype(int)
print(f"[FLOW01] {len(checkpoints)} total in-position checkpoints "
      f"({checkpoints['action_B'].value_counts().to_dict()})", flush=True)
print(f"[FLOW01] HOLD group n={checkpoints['is_hold_checkpoint'].sum()}, "
      f"PRE_EXIT group n={checkpoints['is_pre_exit_checkpoint'].sum()}, "
      f"distinct trades (block_id_B) n={checkpoints['block_id_B'].nunique()}, "
      f"distinct sessions n={checkpoints['sess_date'].nunique()}", flush=True)

# ---------------------------------------------------------------- forward markout outcomes
# next-1-bar / next-3-bar bar_pnl_B_nq_dollars, requiring same sess_date (never crosses a
# session boundary) -- bar_pnl already reflects the ACTUAL signed position path, so no
# additional side-alignment is applied to the outcome itself. Vectorized via positional
# indexing (u0_full's t_idx is a dense 0..n-1 range matching row order by construction).
u0_pos = u0_full.sort_values("t_idx").reset_index(drop=True)
assert (u0_pos["t_idx"].to_numpy() == np.arange(len(u0_pos))).all(), "t_idx not a dense 0..n-1 range"
bpnl_arr = u0_pos["bar_pnl_B_nq_dollars"].to_numpy()
sess_arr = u0_pos["sess_date"].to_numpy()
n_rows = len(u0_pos)


def fwd_markout_vec(t_idx_arr, n_bars):
    out = np.full(len(t_idx_arr), np.nan)
    for k, t in enumerate(t_idx_arr):
        idx = np.arange(t + 1, t + 1 + n_bars)
        if idx[-1] >= n_rows:
            continue
        if not np.all(sess_arr[idx] == sess_arr[t]):
            continue  # forward window would cross a session boundary -- require full horizon
        out[k] = bpnl_arr[idx].sum()
    return out


print("[FLOW01] computing forward markouts (vectorized positional lookup) ...", flush=True)
t_idx_np = checkpoints["t_idx"].to_numpy()
checkpoints["fwd1_pnl"] = fwd_markout_vec(t_idx_np, 1)
checkpoints["fwd3_pnl"] = fwd_markout_vec(t_idx_np, 3)
print(f"[FLOW01] fwd1_pnl usable n={checkpoints['fwd1_pnl'].notna().sum()}, "
      f"fwd3_pnl usable n={checkpoints['fwd3_pnl'].notna().sum()} "
      f"(NaN = forward window crosses session close, expected near session end)", flush=True)

# ---------------------------------------------------------------- microstructure features (per session, vectorized)
FEAT_COLS = ["signed_flow_aligned_60s", "flow_persistence_60s", "avg_spread_ticks_60s",
             "quote_intensity_60s", "ret1s_vol_60s", "n_grid_rows_60s"]

feat_frames = []
for sess_date, grp in checkpoints.groupby("sess_date"):
    f = sess_date_to_file.get(sess_date)
    if f is None:
        continue
    grid = pd.read_parquet(f)
    grid["time"] = pd.to_datetime(grid["time"])
    grid = grid.set_index("time").sort_index()

    roll_spread60 = grid["spread_t"].rolling(60, min_periods=30).mean()
    roll_sflow60 = grid["sflow"].rolling(60, min_periods=30).sum()
    roll_qint60 = (grid["bid_upd"] + grid["ask_upd"]).rolling(60, min_periods=30).mean()
    roll_vol60 = grid["ret1s_t"].rolling(60, min_periods=30).std()
    roll_nrows60 = grid["sflow"].rolling(60, min_periods=1).count()
    # flow persistence: lag-60s autocorrelation of 1s signed flow, estimated over the trailing
    # 180s (3 successive 60s sub-windows) -- corr(sflow[t], sflow[t-60]) for t in the last 120
    # points ending at each timestamp. Direction-invariant (multiplying the whole series by a
    # constant sign, e.g. position side, leaves autocorrelation unchanged) so NOT side-aligned.
    roll_persist = grid["sflow"].rolling(120, min_periods=90).corr(grid["sflow"].shift(60))

    times = pd.DatetimeIndex(grp["time"].to_numpy())
    sub = pd.DataFrame({
        "t_idx": grp["t_idx"].to_numpy(),
        "avg_spread_ticks_60s": roll_spread60.reindex(times).to_numpy(),
        "signed_flow_60s_raw": roll_sflow60.reindex(times).to_numpy(),
        "flow_persistence_60s": roll_persist.reindex(times).to_numpy(),
        "quote_intensity_60s": roll_qint60.reindex(times).to_numpy(),
        "ret1s_vol_60s": roll_vol60.reindex(times).to_numpy(),
        "n_grid_rows_60s": roll_nrows60.reindex(times).to_numpy(),
    })
    feat_frames.append(sub)

feat = pd.concat(feat_frames, ignore_index=True)
checkpoints = checkpoints.merge(feat, on="t_idx", how="left")
checkpoints["signed_flow_aligned_60s"] = checkpoints["signed_flow_60s_raw"] * checkpoints["side"]
# require at least half the 60s window present (matches U9B's own usability threshold)
checkpoints.loc[checkpoints["n_grid_rows_60s"] < 30, FEAT_COLS] = np.nan

checkpoints["M_abs"] = checkpoints["M"].abs()

keep_cols = ["t_idx", "time", "sess_date", "block_id_B", "position_B", "side", "action_B",
             "is_hold_checkpoint", "is_pre_exit_checkpoint",
             "signed_flow_aligned_60s", "flow_persistence_60s", "avg_spread_ticks_60s",
             "quote_intensity_60s", "ret1s_vol_60s", "n_grid_rows_60s",
             "sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr", "M", "M_abs",
             "fwd1_pnl", "fwd3_pnl"]
checkpoints = checkpoints[keep_cols]
checkpoints.to_csv(os.path.join(OUT, "checkpoint_features.csv"), index=False)

# ---------------------------------------------------------------- sanity
sanity = {
    "n_sessions_bbo_confirmed": len(sess_dates),
    "session_date_range": [str(sess_dates[0][0]), str(sess_dates[-1][0])],
    "correctness_gate_canonical_net": canon_net,
    "n_total_checkpoints_position_nonzero": int(len(checkpoints)),
    "n_hold_checkpoints": int(checkpoints["is_hold_checkpoint"].sum()),
    "n_pre_exit_checkpoints": int(checkpoints["is_pre_exit_checkpoint"].sum()),
    "n_distinct_trades_block_id_B": int(checkpoints["block_id_B"].nunique()),
    "n_distinct_sessions_with_checkpoints": int(checkpoints["sess_date"].nunique()),
    "n_usable_feature_window_ge30rows": int((checkpoints["n_grid_rows_60s"] >= 30).sum()),
    "action_B_counts": checkpoints["action_B"].value_counts().to_dict(),
}
json.dump(sanity, open(os.path.join(OUT, "build_sanity.json"), "w"), indent=2, default=str)
print("\n[FLOW01] SANITY:", json.dumps(sanity, indent=2, default=str))
print("\nFLOW01 checkpoint-feature substrate build complete.")
