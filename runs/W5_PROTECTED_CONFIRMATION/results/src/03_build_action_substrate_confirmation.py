"""W5_PROTECTED_CONFIRMATION Family 2 (SECONDARY) -- step_a substrate build. Byte-identical reuse
of runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py's forward-outcome + merge
logic, restricted to the 8 confirmation-pool session tags (via an explicit whitelist, NOT a
sechilo/NQ directory glob, since that directory now also contains the 37 discovery-session files
-- globbing it would silently include sessions outside the authorized 8). value_dist_ticks/
poc_share are read from poc_1s_full_CONFIRM.parquet (built by 01_build_poc_substrate_confirmation.py,
the byte-identical causal_running_poc() construction re-pointed at the 8 confirmation sessions).
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
POC_PATH = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out", "poc_1s_full_CONFIRM.parquet")
OUT = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out")
os.makedirs(OUT, exist_ok=True)

TICK = 0.25
HORIZONS = [1, 3, 20]
CONFIRMATION_DATES = {"20250819", "20250912", "20251028", "20251125",
                       "20260217", "20260302", "20260422", "20260512"}
assert len(CONFIRMATION_DATES) == 8

cols = ["t_idx", "time", "sess_date", "hm", "is_health_only_bar",
        "position_B", "action_B", "block_id_B",
        "target_exposure_A", "action_A", "block_id_A",
        "M", "M_A_raw", "HTF_tilt_state", "vote_dispersion", "sigma460_atr_proxy_pts",
        "open", "high", "low", "close", "session_phase", "minutes_since_session_open",
        "bar_pnl_A_dollars", "bar_pnl_B_nq_dollars"]
u0 = pd.read_parquet(U0_PATH, columns=cols)
assert (u0["t_idx"].to_numpy() == np.arange(len(u0))).all(), "t_idx not dense 0..n-1"

# correctness gate -- reproduce both certified canonical nets before trusting these columns
canon = ~u0["is_health_only_bar"].astype(bool)
net_b = float(u0.loc[canon, "bar_pnl_B_nq_dollars"].sum())
net_a = float(u0.loc[canon, "bar_pnl_A_dollars"].sum())
assert abs(net_b - 301915.92) < 1.0, f"CORRECTNESS GATE FAILED (Product B-NQ): {net_b}"
assert abs(net_a - 177924.40) < 1.0, f"CORRECTNESS GATE FAILED (Product A legacy): {net_a}"
print(f"[build-confirm] correctness gate PASSED: Product B-NQ canonical net={net_b:.2f} (certified 301915.92), "
      f"Product A legacy canonical net={net_a:.2f} (certified 177924.40)", flush=True)

u0["sess_date"] = pd.to_datetime(u0["sess_date"]).dt.date
u0["sess_tag"] = pd.to_datetime(u0["sess_date"]).astype(str).str.replace("-", "", regex=False)

sess_tags_8 = sorted(t for t in u0["sess_tag"].unique() if t in CONFIRMATION_DATES)
assert set(sess_tags_8) == CONFIRMATION_DATES, \
    f"expected exactly the 8 confirmation dates in u0; got {sess_tags_8}"
print(f"[build-confirm] 8 protected-pool confirmation sessions: {sess_tags_8}", flush=True)
assert max(sess_tags_8) < "20260801", "date-firewall violation"

# ---------------------------------------------------------------- forward outcomes (full history,
# identical vectorized construction to the frozen discovery script; restricted afterward)
n = len(u0)
close_arr = u0["close"].to_numpy(dtype=float)
high_arr = u0["high"].to_numpy(dtype=float)
low_arr = u0["low"].to_numpy(dtype=float)
sess_code = pd.factorize(u0["sess_date"].to_numpy())[0]
posB = u0["position_B"].to_numpy(dtype=float)
tgtA = u0["target_exposure_A"].to_numpy(dtype=float)
bpnlA = u0["bar_pnl_A_dollars"].to_numpy(dtype=float)
bpnlB = u0["bar_pnl_B_nq_dollars"].to_numpy(dtype=float)


def fwd_window_excl(arr, H, how):
    rev = pd.Series(arr[::-1])
    if how == "max":
        incl = rev.rolling(H, min_periods=H).max()
    elif how == "min":
        incl = rev.rolling(H, min_periods=H).min()
    else:
        incl = rev.rolling(H, min_periods=H).sum()
    incl = incl.to_numpy()[::-1]
    return pd.Series(incl).shift(-1).to_numpy()


out_cols = {}
for H in HORIZONS:
    valid = (np.arange(n) + H < n)
    end_idx = np.minimum(np.arange(n) + H, n - 1)
    valid = valid & (sess_code == sess_code[end_idx])

    fwd_close = pd.Series(close_arr).shift(-H).to_numpy()
    fwd_hi_max = fwd_window_excl(high_arr, H, "max")
    fwd_lo_min = fwd_window_excl(low_arr, H, "min")
    fwd_pnl_A = fwd_window_excl(bpnlA, H, "sum")
    fwd_pnl_B = fwd_window_excl(bpnlB, H, "sum")

    for tag, side_raw, mfe_key, mae_key, sm_key, fp_key, fp_arr in [
        ("A", tgtA, f"mfe_{H}_A", f"mae_{H}_A", f"signed_markout_{H}_A", f"fwd_pnl_{H}_A", fwd_pnl_A),
        ("B", posB, f"mfe_{H}_B", f"mae_{H}_B", f"signed_markout_{H}_B", f"fwd_pnl_{H}_B", fwd_pnl_B),
    ]:
        side = np.sign(side_raw)
        has_dir = valid & (side != 0)
        sm = np.where(has_dir, side * (fwd_close - close_arr) / TICK, np.nan)
        mfe_long = (fwd_hi_max - close_arr) / TICK
        mae_long = (close_arr - fwd_lo_min) / TICK
        mfe_short = (close_arr - fwd_lo_min) / TICK
        mae_short = (fwd_hi_max - close_arr) / TICK
        mfe = np.where(has_dir & (side > 0), mfe_long, np.where(has_dir & (side < 0), mfe_short, np.nan))
        mae = np.where(has_dir & (side > 0), mae_long, np.where(has_dir & (side < 0), mae_short, np.nan))
        fp = np.where(has_dir, fp_arr, np.nan)
        out_cols[sm_key] = sm
        out_cols[mfe_key] = mfe
        out_cols[mae_key] = mae
        out_cols[fp_key] = fp

for k, v in out_cols.items():
    u0[k] = v

# ---------------------------------------------------------------- restrict to 8-session confirmation
# universe, in-direction bars only
sub = u0[u0["sess_tag"].isin(sess_tags_8)].copy()
assert not sub["is_health_only_bar"].any(), "8-session confirmation universe must be entirely canonical"
in_dir = (sub["position_B"] != 0) | (sub["target_exposure_A"] != 0)
sub = sub[in_dir].reset_index(drop=True)
print(f"[build-confirm] {len(sub)} in-direction bars (position_B!=0 or target_exposure_A!=0) "
      f"across {sub['sess_tag'].nunique()} sessions", flush=True)

# ---------------------------------------------------------------- merge confirmation-pool causal 1s state
poc = pd.read_parquet(POC_PATH, columns=["time", "sess_tag", "poc_share", "value_dist_ticks",
                                          "bid_upd", "ask_upd"])
poc = poc.sort_values(["sess_tag", "time"]).reset_index(drop=True)
poc["bbo_upd"] = poc["bid_upd"] + poc["ask_upd"]
poc["liq60"] = poc.groupby("sess_tag")["bbo_upd"].transform(lambda s: s.rolling(60, min_periods=1).sum())

sub_sorted = sub.sort_values(["sess_tag", "time"]).reset_index(drop=True)
poc_sorted = poc.sort_values(["sess_tag", "time"]).reset_index(drop=True)
merged = pd.merge_asof(
    sub_sorted, poc_sorted[["time", "sess_tag", "poc_share", "value_dist_ticks", "liq60"]],
    on="time", by="sess_tag", direction="backward", tolerance=pd.Timedelta("2s"),
)
merged["matched"] = merged["poc_share"].notna()
merged["tod"] = merged["time"].dt.time
merged["rth"] = (merged["tod"] >= pd.Timestamp("09:30:00").time()) & (merged["tod"] < pd.Timestamp("16:00:00").time())
merged["liquid"] = merged["liq60"] > 0
merged["analysis_ok"] = merged["matched"] & merged["rth"] & merged["liquid"]
merged["abs_value_dist_ticks"] = merged["value_dist_ticks"].abs()
merged = merged.drop(columns=["tod"])

print(f"[build-confirm] match rate {merged['matched'].mean():.4f}, "
      f"rth&liquid&matched (analysis_ok) rate {merged['analysis_ok'].mean():.4f}", flush=True)
print(f"[build-confirm] analysis_ok by session:\n{merged[merged['analysis_ok']]['sess_tag'].value_counts()}", flush=True)

merged.to_parquet(os.path.join(OUT, "action_substrate_CONFIRM.parquet"), compression="zstd", index=False)
print(f"[build-confirm] wrote action_substrate_CONFIRM.parquet: {len(merged)} rows, {merged.shape[1]} cols")
print("BUILD_ACTION_CONFIRM DONE")
