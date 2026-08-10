"""LEV01 step 3 -- TOO-GOOD-TO-BE-TRUE GATE: test 2b's unification term (post_entry_vol_change x
short_dummy, t=4.45) is suspicious for the exact reason U5 flagged before it (see
runs/U5_SOFT_WEIGHTING/REPORT.md): post_entry_vol_change is measured over sessions s+1..s+5
AFTER entry, and correlated against block_net_pnl, the block's TOTAL final outcome. If a block
closes within that same 5-session window (very possible -- many blocks are short-lived), both
variables are driven by the SAME underlying price path (continued decline -> short profits AND
leverage-effect vol rises simultaneously) -- concurrent confirmation, not forward-predictive
information. This script checks the overlap directly and re-tests using a forward-ONLY outcome
(P&L accrued strictly AFTER the vol_change measurement window closes), exactly the fix that
killed U5's apparently-strong finding.
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

entries = pd.read_csv(os.path.join(OUT, "productB_entries_with_regime.csv"))
entries["sess_date"] = pd.to_datetime(entries["sess_date"])
sess_series = pd.read_csv(os.path.join(OUT, "session_series.csv"))
sess_series["sess_date"] = pd.to_datetime(sess_series["sess_date"])
FWD_K = 5

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "sess_date", "block_id_B", "bar_pnl_B_nq_dollars", "is_health_only_bar"])
u0["sess_date"] = pd.to_datetime(u0["sess_date"])
canon = u0[~u0["is_health_only_bar"]].copy()

# ---------------------------------------------------------------- overlap diagnostic
sess_dates_sorted = sess_series["sess_date"].sort_values().reset_index(drop=True)
sess_idx = {d: i for i, d in enumerate(sess_dates_sorted)}

block_last_bar = canon.groupby("block_id_B")["t_idx"].max()
block_last_sess = canon.loc[canon.groupby("block_id_B")["t_idx"].idxmax(), ["block_id_B", "sess_date"]].set_index("block_id_B")["sess_date"]
entries["block_end_sess_date"] = entries["block_id_B"].map(block_last_sess)
entries["entry_sess_idx"] = entries["sess_date"].map(sess_idx)
entries["end_sess_idx"] = entries["block_end_sess_date"].map(sess_idx)
entries["sessions_to_close"] = entries["end_sess_idx"] - entries["entry_sess_idx"]

n_overlap = (entries["sessions_to_close"] <= FWD_K).sum()
print(f"[LEV01] {n_overlap}/{len(entries)} ({100*n_overlap/len(entries):.1f}%) of Product-B blocks "
      f"CLOSE WITHIN the {FWD_K}-session vol_change measurement window -- test 2b's outcome and "
      f"predictor variable substantially OVERLAP in time for these blocks.", flush=True)
print(entries["sessions_to_close"].describe())

# ---------------------------------------------------------------- forward-only fix
# for each entry, compute P&L accrued STRICTLY from the bar AFTER session (entry_sess_idx+FWD_K)'s
# last bar onward, through the block's own actual end (0 if the block already closed before then)
sess_last_bar_tidx = canon.groupby("sess_date")["t_idx"].max()
bpnl = canon.set_index("t_idx")["bar_pnl_B_nq_dollars"]

fwd_only_pnl = []
for _, row in entries.iterrows():
    ent_idx = row["entry_sess_idx"]
    cutoff_sess_pos = ent_idx + FWD_K
    if cutoff_sess_pos >= len(sess_dates_sorted):
        fwd_only_pnl.append(np.nan)
        continue
    cutoff_date = sess_dates_sorted.iloc[cutoff_sess_pos]
    cutoff_tidx = sess_last_bar_tidx.get(cutoff_date, np.nan)
    if pd.isna(cutoff_tidx):
        fwd_only_pnl.append(np.nan)
        continue
    block_end_tidx = block_last_bar.get(row["block_id_B"], np.nan)
    if pd.isna(block_end_tidx) or block_end_tidx <= cutoff_tidx:
        fwd_only_pnl.append(0.0)  # block already closed before the window ended -- no forward P&L
        continue
    window = bpnl.reindex(range(int(cutoff_tidx) + 1, int(block_end_tidx) + 1))
    fwd_only_pnl.append(float(window.sum()))
entries["fwd_only_pnl"] = fwd_only_pnl

sub = entries.dropna(subset=["post_entry_vol_change", "fwd_only_pnl"])
print(f"\n[LEV01] {len(sub)} entries usable for forward-only re-test", flush=True)
print(f"fraction of blocks with fwd_only_pnl==0 (closed before window end): "
      f"{(sub['fwd_only_pnl']==0).mean():.3f}")


def ols(df, X_cols, y_col):
    d = df.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    Xc = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(Xc, y, rcond=None)
    resid = y - Xc @ coef
    n_, k_ = Xc.shape
    sigma2 = (resid @ resid) / max(n_ - k_, 1)
    se = np.sqrt(np.maximum(np.diag(sigma2 * np.linalg.pinv(Xc.T @ Xc)), 0))
    return coef, se, len(d)


sub["short_dummy"] = (sub["side"] == -1).astype(float)
sub["volchg_x_short"] = sub["post_entry_vol_change"] * sub["short_dummy"]

print("\n" + "=" * 90 + "\nRE-TEST with block_net_pnl (original, for reference)\n" + "=" * 90)
coef0, se0, n0 = ols(sub, ["post_entry_vol_change", "short_dummy", "volchg_x_short"], "block_net_pnl")
for nm, c, s in zip(["intercept", "vol_change", "short_dummy", "volchg_x_short"], coef0, se0):
    print(f"  {nm}: coef={c:.3f} se={s:.3f} t={c/s if s>0 else float('nan'):.2f}")

print("\n" + "=" * 90 + "\nRE-TEST with fwd_only_pnl (the economically correct, non-confounded outcome)\n" + "=" * 90)
coef1, se1, n1 = ols(sub, ["post_entry_vol_change", "short_dummy", "volchg_x_short"], "fwd_only_pnl")
for nm, c, s in zip(["intercept", "vol_change", "short_dummy", "volchg_x_short"], coef1, se1):
    t = c / s if s > 0 else np.nan
    print(f"  {nm}: coef={c:.3f} se={s:.3f} t={t:.2f}")
print(f"  n={n1}")

collapse_pct = 100 * (1 - abs(coef1[3]) / abs(coef0[3])) if coef0[3] != 0 else np.nan
print(f"\nunification-term magnitude: original={coef0[3]:.2f} -> forward-only={coef1[3]:.2f} "
      f"({'COLLAPSED' if abs(coef1[3]) < abs(coef0[3]) * 0.3 else 'PARTIALLY SURVIVES' if abs(coef1[3]) < abs(coef0[3])*0.7 else 'SURVIVES'})")

summary = {
    "pct_blocks_closing_within_window": float(100 * n_overlap / len(entries)),
    "sessions_to_close_describe": entries["sessions_to_close"].describe().to_dict(),
    "original_test": {"coef": [float(c) for c in coef0], "se": [float(s) for s in se0], "n": n0,
                       "unification_t": float(coef0[3] / se0[3]) if se0[3] > 0 else None},
    "forward_only_test": {"coef": [float(c) for c in coef1], "se": [float(s) for s in se1], "n": n1,
                           "unification_t": float(coef1[3] / se1[3]) if se1[3] > 0 else None},
    "pct_fwd_only_pnl_zero": float((sub["fwd_only_pnl"] == 0).mean()),
}
json.dump(summary, open(os.path.join(OUT, "test3_confound_check.json"), "w"), indent=2, default=str)
print("\nLEV01 confound check complete.")
