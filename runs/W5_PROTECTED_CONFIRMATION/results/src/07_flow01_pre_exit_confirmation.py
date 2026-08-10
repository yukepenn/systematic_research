"""W5_PROTECTED_CONFIRMATION Family 3 (OPTIONAL) -- FLOW01 PRE_EXIT confirmation. Byte-identical
reuse of runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/01_build_checkpoint_features.py's checkpoint
construction (in-position bars, PRE_EXIT = bar immediately before an actual EXIT/REVERSAL, same
session, contiguous) and 02_analysis.py's dual clustered-bootstrap methodology, restricted to the
8 confirmation-pool sessions via an explicit whitelist (grid1s/NQ now also holds the 37 discovery
sessions, so a directory glob would silently include unauthorized sessions).
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out")
GRID_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")

CONFIRMATION_DATES = ["20250819", "20250912", "20251028", "20251125",
                       "20260217", "20260302", "20260422", "20260512"]
assert len(CONFIRMATION_DATES) == 8
for d in CONFIRMATION_DATES:
    assert d < "20260801", "date-firewall violation"

sess_dates = []
for tag in CONFIRMATION_DATES:
    f = os.path.join(GRID_DIR, f"s{tag}.parquet")
    assert os.path.exists(f), f"missing grid1s file for confirmation session {tag}"
    d = pd.Timestamp(f"{tag[:4]}-{tag[4:6]}-{tag[6:8]}").date()
    sess_dates.append((d, f))
sess_dates.sort()
print(f"[FLOW01-confirm] {len(sess_dates)} protected-pool confirmation sessions "
      f"({sess_dates[0][0]} .. {sess_dates[-1][0]})", flush=True)
sess_date_to_file = {d: f for d, f in sess_dates}
sess_date_set = set(sess_date_to_file)

# ---------------------------------------------------------------- correctness gate
u0_full = pd.read_parquet(U0_PATH, columns=["t_idx", "time", "sess_date", "is_health_only_bar", "position_B",
                                             "action_B", "block_id_B", "bar_pnl_B_nq_dollars",
                                             "sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr", "M"])
canon_net = float(u0_full.loc[~u0_full["is_health_only_bar"], "bar_pnl_B_nq_dollars"].sum())
CERTIFIED_B_NQ = 301915.92
assert abs(canon_net - CERTIFIED_B_NQ) < 1.0, \
    f"CORRECTNESS GATE FAILED: canonical bar_pnl_B_nq_dollars sum {canon_net:.2f} != certified {CERTIFIED_B_NQ}"
print(f"[FLOW01-confirm] correctness gate PASSED: canonical-window bar_pnl_B_nq_dollars sum "
      f"= {canon_net:.2f} (certified {CERTIFIED_B_NQ})", flush=True)

u0_full["sess_date"] = pd.to_datetime(u0_full["sess_date"]).dt.date
u0_sub = u0_full[u0_full["sess_date"].isin(sess_date_set)].sort_values("t_idx").reset_index(drop=True)
print(f"[FLOW01-confirm] {len(u0_sub)} U0 bars fall on these {len(sess_date_set)} confirmation sessions", flush=True)

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
print(f"[FLOW01-confirm] {len(checkpoints)} total in-position checkpoints on the 8 confirmation sessions "
      f"({checkpoints['action_B'].value_counts().to_dict()})", flush=True)
print(f"[FLOW01-confirm] HOLD group n={checkpoints['is_hold_checkpoint'].sum()}, "
      f"PRE_EXIT group n={checkpoints['is_pre_exit_checkpoint'].sum()}, "
      f"distinct trades (block_id_B) n={checkpoints['block_id_B'].nunique()}, "
      f"distinct sessions n={checkpoints['sess_date'].nunique()}", flush=True)

# ---------------------------------------------------------------- forward markout outcomes
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
            continue
        out[k] = bpnl_arr[idx].sum()
    return out


t_idx_np = checkpoints["t_idx"].to_numpy()
checkpoints["fwd1_pnl"] = fwd_markout_vec(t_idx_np, 1)
checkpoints["fwd3_pnl"] = fwd_markout_vec(t_idx_np, 3)
print(f"[FLOW01-confirm] fwd1_pnl usable n={checkpoints['fwd1_pnl'].notna().sum()}, "
      f"fwd3_pnl usable n={checkpoints['fwd3_pnl'].notna().sum()}", flush=True)

# ---------------------------------------------------------------- microstructure features (verbatim)
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
checkpoints.loc[checkpoints["n_grid_rows_60s"] < 30, FEAT_COLS] = np.nan
checkpoints["M_abs"] = checkpoints["M"].abs()

keep_cols = ["t_idx", "time", "sess_date", "block_id_B", "position_B", "side", "action_B",
             "is_hold_checkpoint", "is_pre_exit_checkpoint",
             "signed_flow_aligned_60s", "flow_persistence_60s", "avg_spread_ticks_60s",
             "quote_intensity_60s", "ret1s_vol_60s", "n_grid_rows_60s",
             "sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr", "M", "M_abs",
             "fwd1_pnl", "fwd3_pnl"]
checkpoints = checkpoints[keep_cols]
checkpoints.to_csv(os.path.join(OUT, "checkpoint_features_CONFIRM.csv"), index=False)

sanity = {
    "n_sessions_confirmation": len(sess_dates),
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
json.dump(sanity, open(os.path.join(OUT, "build_sanity_CONFIRM.json"), "w"), indent=2, default=str)
print("\n[FLOW01-confirm] SANITY:", json.dumps(sanity, indent=2, default=str))
print("\n[FLOW01-confirm] checkpoint-feature substrate build complete.")

# ================================================================== ANALYSIS (02_analysis.py logic)
FEATS = ["signed_flow_aligned_60s", "flow_persistence_60s", "avg_spread_ticks_60s",
         "quote_intensity_60s", "ret1s_vol_60s"]
HORIZONS = ["fwd1_pnl", "fwd3_pnl"]

cp = checkpoints[checkpoints["n_grid_rows_60s"] >= 30].copy()
print(f"\n[FLOW01-confirm] usable checkpoints after window filter: n={len(cp)}", flush=True)

pre_exit = cp[cp["is_pre_exit_checkpoint"]].copy()
n_pe = len(pre_exit)
n_pe_trades = pre_exit["block_id_B"].nunique()
n_pe_sessions = pre_exit["sess_date"].nunique()
print(f"[FLOW01-confirm] PRE_EXIT group: n_checkpoints={n_pe}, n_trades={n_pe_trades}, "
      f"n_sessions={n_pe_sessions}", flush=True)

rng = np.random.RandomState(20260809)


def clustered_bootstrap(df, feat, ycol, cluster_col, n_boot=1000):
    sub = df.dropna(subset=[feat, ycol])
    clusters = sub[cluster_col].unique()
    if len(clusters) < 3:
        return {"observed_rho": (float(sub[feat].corr(sub[ycol], method="spearman")) if len(sub) >= 2 else np.nan),
                "ci_lo": np.nan, "ci_hi": np.nan, "n_boot": 0, "n_clusters": len(clusters), "n": len(sub)}
    cl_groups = {c: sub[sub[cluster_col] == c].index.to_numpy() for c in clusters}
    obs_rho = float(sub[feat].corr(sub[ycol], method="spearman"))
    boot_rhos = []
    for _ in range(n_boot):
        sampled = rng.choice(clusters, size=len(clusters), replace=True)
        idx = np.concatenate([cl_groups[c] for c in sampled if len(cl_groups[c]) > 0])
        if len(idx) < 10:
            continue
        d = sub.loc[idx]
        r = d[feat].corr(d[ycol], method="spearman")
        if r == r:
            boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    ci_lo, ci_hi = (np.percentile(boot_rhos, [2.5, 97.5]) if len(boot_rhos) else (np.nan, np.nan))
    return {"observed_rho": obs_rho, "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
            "n_boot": len(boot_rhos), "n_clusters": len(clusters), "n": len(sub)}


PRE_EXIT_MIN_SESSIONS_FOR_BOOTSTRAP = 3
bootstrap_results = {}
if n_pe_sessions < PRE_EXIT_MIN_SESSIONS_FOR_BOOTSTRAP:
    print(f"\n[FLOW01-confirm] PRE_EXIT group spans only {n_pe_sessions} session(s) with ANY PRE_EXIT "
          f"event -- below the {PRE_EXIT_MIN_SESSIONS_FOR_BOOTSTRAP}-session floor needed for a "
          f"meaningful session-block bootstrap. Per the task's own instruction, this is reported "
          f"honestly as NOT COMPUTABLE rather than forcing a number.", flush=True)
    n_cells_evaluable = 0
    n_both_excl0 = 0
else:
    n_cells_evaluable = 0
    n_both_excl0 = 0
    for ycol in HORIZONS:
        for f in FEATS:
            key = f"{ycol}:{f}"
            sess_boot = clustered_bootstrap(pre_exit, f, ycol, "sess_date")
            trade_boot = clustered_bootstrap(pre_exit, f, ycol, "block_id_B")
            excl0_sess = (sess_boot["ci_lo"] > 0 or sess_boot["ci_hi"] < 0) if sess_boot["ci_lo"] == sess_boot["ci_lo"] else False
            excl0_trade = (trade_boot["ci_lo"] > 0 or trade_boot["ci_hi"] < 0) if trade_boot["ci_lo"] == trade_boot["ci_lo"] else False
            bootstrap_results[key] = {"session_block": sess_boot, "trade_block": trade_boot,
                                       "excludes_zero_session": bool(excl0_sess), "excludes_zero_trade": bool(excl0_trade)}
            n_cells_evaluable += 1
            if excl0_sess and excl0_trade:
                n_both_excl0 += 1
            marker = "  <-- BOTH exclude 0" if (excl0_sess and excl0_trade) else ""
            print(f"  {key}: rho={sess_boot['observed_rho']:+.4f}  "
                  f"session-CI=[{sess_boot['ci_lo']:+.3f},{sess_boot['ci_hi']:+.3f}](n_sess={sess_boot['n_clusters']})  "
                  f"trade-CI=[{trade_boot['ci_lo']:+.3f},{trade_boot['ci_hi']:+.3f}](n_trades={trade_boot['n_clusters']}){marker}",
                  flush=True)
    print(f"\n[FLOW01-confirm] {n_both_excl0}/{n_cells_evaluable} PRE_EXIT cells have BOTH session-block "
          f"and trade-block bootstrap CIs excluding zero.", flush=True)

summary = {
    "n_checkpoints_total_usable": len(cp),
    "pre_exit_group": {"n_checkpoints": n_pe, "n_trades": n_pe_trades, "n_sessions": n_pe_sessions},
    "bootstrap_computable": bool(n_pe_sessions >= PRE_EXIT_MIN_SESSIONS_FOR_BOOTSTRAP),
    "clustered_bootstrap_pre_exit_cells": bootstrap_results,
    "n_cells_both_bootstraps_exclude_zero": n_both_excl0,
    "n_cells_total": n_cells_evaluable,
}
json.dump(summary, open(os.path.join(OUT, "flow01_analysis_summary_CONFIRM.json"), "w"), indent=2, default=str)
print("\nFLOW01_PRE_EXIT_CONFIRM DONE")
