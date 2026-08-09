"""U1 test-1 substrate -- builds the block-level entry tables and forward-return (continuation
value) tables for Product B and Product A directly from U0's certified state table. Reuses the
SAME block-level net_pnl convention P0/R4/R5 established (net_pnl = last run_pnl_*_dollars
within the position/exposure block) -- no new backtest engine, no re-derivation of decisions."""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

COLS = [
    "t_idx", "sess_date", "year", "is_health_only_bar", "session_phase", "is_rth",
    "M", "M_A_raw", "sigma460_atr_proxy_pts",
    "position_B", "action_B", "block_id_B", "run_pnl_B_dollars", "bar_pnl_B_nq_dollars",
    "target_exposure_A", "action_A", "block_id_A", "run_pnl_A_dollars", "bar_pnl_A_dollars",
]
print("loading U0 state table ...", flush=True)
df = pd.read_parquet(U0_PATH, columns=COLS)
n = len(df)
print(f"  {n} bars loaded", flush=True)

# ============================================================= PRODUCT B: block-level entry table
print("building Product-B block-level entry/reversal table ...", flush=True)
pos_blocks_B = df[df["position_B"] != 0]
block_net_B = pos_blocks_B.groupby("block_id_B")["run_pnl_B_dollars"].last()  # P0/R4/R5 convention

entry_rows_B = df[df["action_B"].isin(["ENTRY", "REVERSAL"])].copy()
entry_rows_B["net_pnl"] = entry_rows_B["block_id_B"].map(block_net_B)
entry_rows_B["side"] = np.sign(entry_rows_B["position_B"]).astype(int)
entry_rows_B["M_abs"] = entry_rows_B["M"].abs()
entry_rows_B["vol_at_entry"] = entry_rows_B["sigma460_atr_proxy_pts"]
entry_rows_B["M_strength_tercile"] = pd.qcut(entry_rows_B["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
entry_rows_B["vol_tercile"] = pd.qcut(entry_rows_B["vol_at_entry"], 3, labels=["low", "mid", "high"], duplicates="drop")
entry_rows_B = entry_rows_B.dropna(subset=["net_pnl"])

keep_cols = ["t_idx", "sess_date", "year", "is_health_only_bar", "session_phase", "is_rth",
             "action_B", "block_id_B", "side", "M_abs", "vol_at_entry",
             "M_strength_tercile", "vol_tercile", "net_pnl"]
entry_rows_B[keep_cols].to_csv(os.path.join(OUT, "block_entry_B.csv"), index=False)
print(f"  Product-B entry+reversal table: n={len(entry_rows_B)} "
      f"(ENTRY={int((entry_rows_B['action_B']=='ENTRY').sum())}, "
      f"REVERSAL={int((entry_rows_B['action_B']=='REVERSAL').sum())})", flush=True)

# ============================================================= PRODUCT B: HOLD forward-return proxy
print("building Product-B HOLD forward-1/5-bar continuation-value proxy ...", flush=True)
bpnl_B = df["bar_pnl_B_nq_dollars"].to_numpy()
csum_B = np.concatenate([[0.0], np.cumsum(bpnl_B)])


def forward_sum(csum, t_arr, k, n_total):
    """sum(bpnl[t+1 : t+1+k]) for each t in t_arr, causal (uses only bars AFTER t); NaN if the
    full k-bar forward window would run past the end of the dataset (no partial windows)."""
    t_arr = np.asarray(t_arr)
    valid = (t_arr + k) <= (n_total - 1)
    out = np.full(len(t_arr), np.nan)
    a = np.minimum(t_arr + 1, n_total)
    b = np.minimum(t_arr + 1 + k, n_total)
    out[valid] = csum[b[valid]] - csum[a[valid]]
    return out


hold_B = df[df["action_B"] == "HOLD"].copy()
t_arr = hold_B["t_idx"].to_numpy()
hold_B["forward1_pnl"] = forward_sum(csum_B, t_arr, 1, n)
hold_B["forward5_pnl"] = forward_sum(csum_B, t_arr, 5, n)
hold_cols = ["t_idx", "sess_date", "year", "is_health_only_bar", "session_phase", "is_rth",
             "forward1_pnl", "forward5_pnl"]
hold_B[hold_cols].to_csv(os.path.join(OUT, "hold_fwd_B.csv"), index=False)
print(f"  Product-B HOLD forward-return table: n={len(hold_B)}", flush=True)

# ============================================================= PRODUCT A: block-level ENTRY table
print("building Product-A trip-level ENTRY table ...", flush=True)
pos_blocks_A = df[df["target_exposure_A"] != 0]
block_net_A = pos_blocks_A.groupby("block_id_A")["run_pnl_A_dollars"].last()

entry_rows_A = df[df["action_A"] == "ENTRY"].copy()
entry_rows_A["net_pnl"] = entry_rows_A["block_id_A"].map(block_net_A)
entry_rows_A["side"] = np.sign(entry_rows_A["target_exposure_A"]).astype(int)
entry_rows_A["M_abs"] = entry_rows_A["M_A_raw"].abs()
entry_rows_A["vol_at_entry"] = entry_rows_A["sigma460_atr_proxy_pts"]
# M_A_raw is near-discrete and heavily concentrated at |M_A_raw|=1 (3250/3604 = 90.2% of ENTRY
# events) -- a quantile-based tercile (R4/R5's convention for Product B's continuous M) is
# degenerate here (25th/50th/75th percentiles all equal 1.0). Use fixed, interpretable cutoffs
# on Product A's own known integer scale instead (documented range |M_A_raw|<=11, entry cluster
# at 1); this is disclosed explicitly, not silently substituted.
entry_rows_A["M_strength_tercile"] = pd.cut(entry_rows_A["M_abs"], bins=[-0.5, 1.5, 3.5, np.inf],
                                             labels=["weak", "mid", "strong"])
entry_rows_A["vol_tercile"] = pd.qcut(entry_rows_A["vol_at_entry"], 3, labels=["low", "mid", "high"], duplicates="drop")
entry_rows_A = entry_rows_A.dropna(subset=["net_pnl"])
out_cols_A = ["t_idx", "sess_date", "year", "is_health_only_bar", "session_phase", "is_rth",
              "action_A", "block_id_A", "side", "M_abs", "vol_at_entry",
              "M_strength_tercile", "vol_tercile", "net_pnl"]
entry_rows_A[out_cols_A].to_csv(os.path.join(OUT, "block_entry_A.csv"), index=False)
print(f"  Product-A ENTRY table: n={len(entry_rows_A)}", flush=True)

# ============================================================= PRODUCT A: SCALE_IN forward-return proxy
print("building Product-A SCALE_IN forward-1/5-bar continuation-value proxy ...", flush=True)
bpnl_A = df["bar_pnl_A_dollars"].to_numpy()
csum_A = np.concatenate([[0.0], np.cumsum(bpnl_A)])

scalein_A = df[df["action_A"] == "SCALE_IN"].copy()
t_arr_a = scalein_A["t_idx"].to_numpy()
scalein_A["forward1_pnl"] = forward_sum(csum_A, t_arr_a, 1, n)
scalein_A["forward5_pnl"] = forward_sum(csum_A, t_arr_a, 5, n)
scalein_A["M_abs"] = scalein_A["M_A_raw"].abs()
scale_cols = ["t_idx", "sess_date", "year", "is_health_only_bar", "session_phase", "is_rth",
              "M_abs", "forward1_pnl", "forward5_pnl"]
scalein_A[scale_cols].to_csv(os.path.join(OUT, "scalein_fwd_A.csv"), index=False)
print(f"  Product-A SCALE_IN forward-return table: n={len(scalein_A)}", flush=True)

print("\n01_build_tables complete.")
