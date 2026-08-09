"""U3 step 1 -- build HOLD-state bar frames (Product B, Product A) with forward continuation-value
labels and a small interpretable state-bucket set. Per spec.yaml: bar-level unit of observation,
forward labels are DESCRIPTIVE (measurement), not a backtest lookahead. Terciles/bins are fit on
the canonical window only, then applied unchanged to the health-only extension.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(ROOT, "runs", "U3_HOLD_EXPOSURE_CONTINUATION", "out")
os.makedirs(OUT, exist_ok=True)

HORIZONS = [1, 2, 5, 10, 20]

COLS = [
    "t_idx", "sess_date", "hm", "year", "is_health_only_bar",
    "M", "M_change", "M_slope_20", "vote_dispersion", "B",
    "sigma460_atr_proxy_pts", "clv_signed", "session_phase",
    "rejected_upper_break", "rejected_lower_break",
    "position_B", "action_B", "block_id_B", "age_bars_B",
    "giveback_ratio_B", "bar_pnl_B_nq_dollars", "run_pnl_B_dollars",
    "target_exposure_A", "action_A", "block_id_A", "age_bars_A",
    "giveback_ratio_A", "bar_pnl_A_dollars", "run_pnl_A_dollars",
]

print("loading U0 state table ...", flush=True)
df = pd.read_parquet(U0_PATH, columns=COLS)
n = len(df)
assert (df["t_idx"].to_numpy() == np.arange(n)).all(), "t_idx must be an exact row-position index"

# ---------------------------------------------------------------------------
# session-end row index per row (last row of the same sess_date, by position)
# ---------------------------------------------------------------------------
sess_end_idx = df.groupby("sess_date")["t_idx"].transform("max").to_numpy()

# ---------------------------------------------------------------------------
# prefix sums for forward-window realized P&L (descriptive labeling only)
# ---------------------------------------------------------------------------
def prefix_sum(arr):
    a = np.nan_to_num(arr.to_numpy(dtype=float), nan=0.0)
    return np.concatenate([[0.0], np.cumsum(a)])


def forward_fixed(cum, t_idx, N):
    """sum of bar_pnl over rows t+1..t+N inclusive; NaN if window runs past array end."""
    hi = t_idx + 1 + N
    valid = hi <= n
    out = np.full(len(t_idx), np.nan)
    out[valid] = cum[hi[valid]] - cum[t_idx[valid] + 1]
    return out


def forward_session(cum, t_idx, end_idx):
    """sum of bar_pnl from t+1 through end_idx (inclusive); 0 if t is already the session's last bar."""
    return cum[end_idx + 1] - cum[t_idx + 1]


def reversal_within(sign_arr, t_idx, N):
    """True if sign flips to the OPPOSITE of sign_arr[t] at any of t+1..t+N (product < 0)."""
    n_ = len(sign_arr)
    s0 = sign_arr[t_idx]
    flag = np.zeros(len(t_idx), dtype=bool)
    checked = np.zeros(len(t_idx), dtype=bool)
    for k in range(1, N + 1):
        shifted_idx = t_idx + k
        ok = shifted_idx < n_
        prod = np.zeros(len(t_idx))
        prod[ok] = s0[ok] * sign_arr[shifted_idx[ok]]
        flag |= (prod < 0)
        checked |= ok
    out = flag.astype(float)
    out[~checked] = np.nan
    return out


def build_leg(action_col, hold_mask_values, side_source_col, block_col, age_col,
              giveback_col, bar_pnl_col, run_pnl_col, tag):
    print(f"building {tag} HOLD frame ...", flush=True)
    mask = df[action_col].isin(hold_mask_values).to_numpy()
    sub = df.loc[mask].copy()
    t = sub["t_idx"].to_numpy()

    cum = prefix_sum(df[bar_pnl_col])
    sign_all = np.sign(df[side_source_col].to_numpy())

    for N in HORIZONS:
        sub[f"fwd_{N}"] = forward_fixed(cum, t, N)
    sub["fwd_session"] = forward_session(cum, t, sess_end_idx[mask])
    sub["bars_left_in_session"] = sess_end_idx[mask] - t

    for N in [5, 10, 20]:
        sub[f"reversal_within_{N}"] = reversal_within(sign_all, t, N)

    sub["side"] = np.sign(sub[side_source_col]).astype(int)
    assert (sub["side"] != 0).all(), f"{tag}: HOLD bars must have nonzero side"

    # ---- interpretable state buckets, fit on CANONICAL rows only ----
    canon = ~sub["is_health_only_bar"]

    def qcut_frozen(values_all, fit_mask, labels, q=3):
        edges = np.quantile(values_all[fit_mask].dropna(), np.linspace(0, 1, q + 1))
        edges = np.unique(edges)
        if len(edges) < q + 1:
            # degenerate distribution; fall back to rank-based qcut on fit sample only info
            return pd.Series(pd.qcut(values_all.rank(method="first"), q, labels=labels), index=values_all.index)
        cats = pd.cut(values_all, bins=edges, labels=labels[: len(edges) - 1],
                       include_lowest=True, duplicates="drop")
        return cats

    sub["M_abs"] = sub["M"].abs()
    sub["M_abs_tercile"] = qcut_frozen(sub["M_abs"], canon, ["weak", "mid", "strong"])

    sub["M_slope_aligned"] = sub["M_slope_20"] * sub["side"]
    sub["M_slope_tercile"] = qcut_frozen(sub["M_slope_aligned"], canon, ["decaying", "flat", "growing"])

    sub["M_change_aligned"] = sub["M_change"] * sub["side"]
    sub["M_change_sign"] = np.select(
        [sub["M_change_aligned"] > 1e-9, sub["M_change_aligned"] < -1e-9],
        ["growing", "decaying"], default="flat")

    sub["vote_dispersion_tercile"] = qcut_frozen(sub["vote_dispersion"].astype(float), canon,
                                                  ["low", "mid", "high"])
    sub["B_engaged"] = sub["B"].ne(0)

    sub["vol_tercile"] = qcut_frozen(sub["sigma460_atr_proxy_pts"], canon, ["low", "mid", "high"])

    age = sub[age_col]
    sub["age_bucket"] = pd.cut(age, bins=[1, 10, 40, 120, 100000],
                                labels=["new_2-10", "young_11-40", "mature_41-120", "old_121+"])

    gb = sub[giveback_col].clip(upper=5.0)
    sub["giveback_tercile"] = qcut_frozen(gb, canon, ["low", "mid", "high"])

    sub["clv_aligned"] = sub["clv_signed"] * sub["side"]
    sub["clv_tercile"] = qcut_frozen(sub["clv_aligned"], canon, ["poor", "mid", "good"])

    sub["rejection_aligned"] = np.where(sub["side"] > 0, sub["rejected_upper_break"],
                                         sub["rejected_lower_break"])

    sub = sub.rename(columns={block_col: "block_id", age_col: "age_bars",
                               giveback_col: "giveback_ratio_raw", bar_pnl_col: "bar_pnl",
                               run_pnl_col: "run_pnl"})
    keep = ["t_idx", "sess_date", "hm", "year", "is_health_only_bar", "session_phase",
            "block_id", "age_bars", "age_bucket", "side", "M_abs", "M_abs_tercile", "M_slope_aligned",
            "M_slope_tercile", "M_change_aligned", "M_change_sign", "vote_dispersion",
            "vote_dispersion_tercile", "B_engaged", "sigma460_atr_proxy_pts", "vol_tercile",
            "giveback_ratio_raw", "giveback_tercile", "clv_aligned", "clv_tercile",
            "rejection_aligned", "bar_pnl", "run_pnl"]
    keep += [f"fwd_{N}" for N in HORIZONS] + ["fwd_session", "bars_left_in_session"]
    keep += [f"reversal_within_{N}" for N in [5, 10, 20]]
    return sub[keep].reset_index(drop=True)


hold_B = build_leg("action_B", ["HOLD"], "position_B", "block_id_B", "age_bars_B",
                    "giveback_ratio_B", "bar_pnl_B_nq_dollars", "run_pnl_B_dollars", "B")
hold_A = build_leg("action_A", ["HOLD", "SCALE_IN"], "target_exposure_A", "block_id_A", "age_bars_A",
                    "giveback_ratio_A", "bar_pnl_A_dollars", "run_pnl_A_dollars", "A")

hold_B.to_parquet(os.path.join(OUT, "hold_B.parquet"))
hold_A.to_parquet(os.path.join(OUT, "hold_A.parquet"))

print(f"hold_B: {len(hold_B)} rows ({(~hold_B.is_health_only_bar).sum()} canonical, "
      f"{hold_B.is_health_only_bar.sum()} health-only)")
print(f"hold_A: {len(hold_A)} rows ({(~hold_A.is_health_only_bar).sum()} canonical, "
      f"{hold_A.is_health_only_bar.sum()} health-only)")

# ---------------------------------------------------------------------------
# block-level entry-phase table (for point 2, transition analysis) + block net_pnl
# (for the right-tail top-20 check) -- built here so downstream scripts reuse it.
# ---------------------------------------------------------------------------
def build_block_table(action_col, starter_actions, ender_actions, block_col, run_pnl_col, tag):
    entry_rows = df[df[action_col].isin(starter_actions)][[block_col, "session_phase", "sess_date", "year",
                                                             "is_health_only_bar"]]
    entry_rows = entry_rows.rename(columns={block_col: "block_id", "session_phase": "entry_session_phase"})
    entry_rows = entry_rows.drop_duplicates(subset="block_id", keep="first")

    # a block ends either at an EXIT row (position -> 0) or a REVERSAL/FLIP row (position flips sign
    # in the same bar, which both closes the old block and opens a new one) -- in BOTH cases the
    # block's final net_pnl is the running P&L of the row immediately BEFORE the ender row (its own
    # block_id, since the ender row itself already belongs to the new/flat block).
    ender_t_idx = df[df[action_col].isin(ender_actions)]["t_idx"].to_numpy()
    pre_ender_idx = ender_t_idx - 1
    pre_ender_idx = pre_ender_idx[pre_ender_idx >= 0]
    net_pnl = df.loc[pre_ender_idx, [block_col, run_pnl_col]].rename(
        columns={block_col: "block_id", run_pnl_col: "net_pnl"})
    net_pnl = net_pnl.drop_duplicates(subset="block_id", keep="last")

    bt = entry_rows.merge(net_pnl, on="block_id", how="left")
    return bt


block_B = build_block_table("action_B", ["ENTRY", "REVERSAL"], ["EXIT", "REVERSAL"],
                             "block_id_B", "run_pnl_B_dollars", "B")
block_A = build_block_table("action_A", ["ENTRY", "FLIP"], ["EXIT", "FLIP"],
                             "block_id_A", "run_pnl_A_dollars", "A")

block_B.to_csv(os.path.join(OUT, "block_table_B.csv"), index=False)
block_A.to_csv(os.path.join(OUT, "block_table_A.csv"), index=False)
print(f"block_B: {len(block_B)} blocks with net_pnl (of which {block_B.net_pnl.notna().sum()} resolved)")
print(f"block_A: {len(block_A)} blocks with net_pnl (of which {block_A.net_pnl.notna().sum()} resolved)")

print("01_build_hold_frames.py complete.")
