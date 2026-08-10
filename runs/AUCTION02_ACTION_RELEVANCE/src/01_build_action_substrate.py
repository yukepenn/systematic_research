"""AUCTION02 -- step 1 build: incumbent-direction bars (Product A and/or Product B nonzero)
on the 37 BBO-confirmed sessions, U0's own 3-min bar grid, with AUCTION01's causal 1s
value_dist_ticks / poc_share merged on via the same merge_asof(backward, by session, tol=2s)
pattern COMBO01 used. GOVERNANCE: reads ONLY runs/U0_UNIFIED_STATE/out/u0_state_table.parquet
(read-only, already-certified) and runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet
(already-built, already-reported). No new tick/BBO/NT8 data touched. Session universe is the
same 37-session sechilo/NQ BBO-confirmed list every prior family in this lineage (AUCTION01,
FLOW01, COMBO01, U9B) has used -- max session tag 20260520, entirely inside the canonical
window and far short of the 2026-08-01 sealed boundary. The ~168-session AMENDMENT_3 protected
pool is never referenced, enumerated, or read.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
POC_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "poc_1s_full.parquet")
OUT = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out")
os.makedirs(OUT, exist_ok=True)

TICK = 0.25
HORIZONS = [1, 3, 20]
EXCLUDE = {"20250811", "20250924", "20260430"}  # same 3 documented BBO holes as every prior family

# ---------------------------------------------------------------- load U0 (full history, read-only)
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
print(f"[build] correctness gate PASSED: Product B-NQ canonical net={net_b:.2f} (certified 301915.92), "
      f"Product A legacy canonical net={net_a:.2f} (certified 177924.40)", flush=True)

u0["sess_date"] = pd.to_datetime(u0["sess_date"]).dt.date
u0["sess_tag"] = pd.to_datetime(u0["sess_date"]).astype(str).str.replace("-", "", regex=False)

sess_tags_37 = sorted(t for t in u0["sess_tag"].unique() if t not in EXCLUDE)
# restrict to the exact 37-session sechilo/NQ BBO-confirmed list (same governance wall as AUCTION01)
sechilo_dir = os.path.join(ROOT, "research", "scalping_lab", "substrate", "sechilo", "NQ")
sechilo_tags = sorted(f.replace("s", "").replace(".parquet", "")
                       for f in os.listdir(sechilo_dir) if f.startswith("s") and f.endswith(".parquet"))
assert set(sechilo_tags) & EXCLUDE == set(), "EXCLUDE list should already be absent from sechilo dir"
assert len(sechilo_tags) == 37
print(f"[build] 37 BBO-confirmed sessions: {sechilo_tags[0]} .. {sechilo_tags[-1]}", flush=True)
assert max(sechilo_tags) <= "20260520" < "20260601", "session set must stay inside canonical window"

# ---------------------------------------------------------------- forward outcomes (full history,
# fully vectorized (reversed-array rolling window trick, no python row loop), session-boundary-safe
# -- computed on the FULL table so t+H never spuriously reads across an unrelated session;
# restricted to the 37-session rows only afterward)
n = len(u0)
close_arr = u0["close"].to_numpy(dtype=float)
high_arr = u0["high"].to_numpy(dtype=float)
low_arr = u0["low"].to_numpy(dtype=float)
sess_code = pd.factorize(u0["sess_date"].to_numpy())[0]  # dense, monotonic per session (t_idx order)
posB = u0["position_B"].to_numpy(dtype=float)
tgtA = u0["target_exposure_A"].to_numpy(dtype=float)
bpnlA = u0["bar_pnl_A_dollars"].to_numpy(dtype=float)
bpnlB = u0["bar_pnl_B_nq_dollars"].to_numpy(dtype=float)


def fwd_window_excl(arr, H, how):
    """max/min/sum of arr[t+1 .. t+H] at each t, via reverse-array rolling (no python row loop).
    how in {'max','min','sum'}."""
    rev = pd.Series(arr[::-1])
    if how == "max":
        incl = rev.rolling(H, min_periods=H).max()
    elif how == "min":
        incl = rev.rolling(H, min_periods=H).min()
    else:
        incl = rev.rolling(H, min_periods=H).sum()
    incl = incl.to_numpy()[::-1]  # incl[t] = how(arr[t : t+H])  (inclusive of t)
    return pd.Series(incl).shift(-1).to_numpy()  # excl[t] = how(arr[t+1 : t+H+1])


out_cols = {}
for H in HORIZONS:
    valid = (np.arange(n) + H < n)
    end_idx = np.minimum(np.arange(n) + H, n - 1)
    valid = valid & (sess_code == sess_code[end_idx])  # sessions are dense contiguous blocks in
    # t_idx order, so sess_code[t]==sess_code[t+H] implies every bar in between is the same session

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
        print(f"[build] horizon {H} product {tag}: usable-window n={int(valid.sum())}, "
              f"in-direction-with-outcome n={int(has_dir.sum())}", flush=True)

for k, v in out_cols.items():
    u0[k] = v

# ---------------------------------------------------------------- restrict to 37-session universe,
# in-direction bars only (position_B != 0 OR target_exposure_A != 0)
sub = u0[u0["sess_tag"].isin(sechilo_tags)].copy()
assert not sub["is_health_only_bar"].any(), "37-session tick universe must be entirely canonical"
in_dir = (sub["position_B"] != 0) | (sub["target_exposure_A"] != 0)
sub = sub[in_dir].reset_index(drop=True)
print(f"[build] {len(sub)} in-direction bars (position_B!=0 or target_exposure_A!=0) "
      f"across {sub['sess_tag'].nunique()} sessions", flush=True)

# ---------------------------------------------------------------- merge AUCTION01's causal 1s state
# (identical mechanics to COMBO01/src/01_build_merged_substrate.py: merge_asof backward, by
# session, 2s tolerance; liq60 reconstructed the same way from bid_upd/ask_upd)
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

print(f"[build] match rate {merged['matched'].mean():.4f}, "
      f"rth&liquid&matched (analysis_ok) rate {merged['analysis_ok'].mean():.4f}", flush=True)

merged.to_parquet(os.path.join(OUT, "action_substrate.parquet"), compression="zstd", index=False)
print(f"[build] wrote action_substrate.parquet: {len(merged)} rows, {merged.shape[1]} cols")
print("BUILD DONE")
