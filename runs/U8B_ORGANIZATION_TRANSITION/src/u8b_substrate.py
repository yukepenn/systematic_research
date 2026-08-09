"""U8B substrate: load U8's already-verified bar-level organization LEVEL features
(perm_entropy_10/20, reversal_rate_10/20, run_persistence_10/20) verbatim from
u8_bars_with_features.parquet, join a small set of additional U0 columns needed for this family
(M_change, M_slope_20, is_rth, MFE_B_dollars, MAE_B_dollars) on t_idx, and compute the 3
preregistered TRANSITION features (10-bar minus 20-bar). No recomputation of the level features,
no new window. Writes a slim combined table reused by every downstream script."""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U8_PATH = os.path.join(ROOT, "runs", "U8_PATH_ORGANIZATION", "out", "u8_bars_with_features.parquet")
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

LEVEL_COLS = ["reversal_rate_10", "run_persistence_10", "perm_entropy_10",
              "reversal_rate_20", "run_persistence_20", "perm_entropy_20"]

U8_COLS = [
    "t_idx", "sess_date", "hm", "year", "is_health_only_bar", "close",
    "M", "M_A_raw", "ret_1", "sigma460_atr_proxy_pts",
    "trend_efficiency_20", "range_efficiency_20",
    "position_B", "action_B", "block_id_B", "age_bars_B",
    "run_pnl_B_dollars", "bar_pnl_B_nq_dollars",
    "target_exposure_A", "action_A", "block_id_A", "age_bars_A",
    "run_pnl_A_dollars", "bar_pnl_A_dollars",
] + LEVEL_COLS

U0_EXTRA_COLS = ["t_idx", "M_change", "M_slope_20", "is_rth", "MFE_B_dollars", "MAE_B_dollars"]


def load_with_transition_features():
    print("[U8B substrate] loading U8's bar-level features (verbatim, not recomputed) ...", flush=True)
    u8 = pd.read_parquet(U8_PATH, columns=U8_COLS)
    u8 = u8.sort_values("t_idx").reset_index(drop=True)
    n = len(u8)
    assert (u8["t_idx"].to_numpy() == np.arange(n)).all(), "t_idx must be 0..n-1 sequential"
    print(f"  {n} rows from U8", flush=True)

    print("[U8B substrate] joining additional U0 columns (M_change, M_slope_20, is_rth, "
          "MFE_B_dollars, MAE_B_dollars) on t_idx ...", flush=True)
    u0_extra = pd.read_parquet(U0_PATH, columns=U0_EXTRA_COLS)
    u0_extra = u0_extra.sort_values("t_idx").reset_index(drop=True)
    assert (u0_extra["t_idx"].to_numpy() == np.arange(len(u0_extra))).all()
    assert len(u0_extra) == n, f"U0 row count {len(u0_extra)} != U8 row count {n}"

    df = u8.merge(u0_extra, on="t_idx", how="left", validate="one_to_one")
    assert len(df) == n

    print("[U8B substrate] computing 3 transition features (10-bar minus 20-bar, causal, "
          "no new window) ...", flush=True)
    df["perm_entropy_transition"] = df["perm_entropy_10"] - df["perm_entropy_20"]
    df["reversal_rate_transition"] = df["reversal_rate_10"] - df["reversal_rate_20"]
    df["run_persistence_transition"] = df["run_persistence_10"] - df["run_persistence_20"]

    return df


TRANSITION_FEATURES = ["perm_entropy_transition", "reversal_rate_transition", "run_persistence_transition"]
INDEPENDENT_FEATURES = ["perm_entropy_transition", "reversal_rate_transition"]  # run_persistence_transition
# is the near-mirror of reversal_rate_transition, verified empirically in step0 -- not double
# counted in Stage 2 / session / right-tail work per spec.yaml.

if __name__ == "__main__":
    df = load_with_transition_features()
    out_path = os.path.join(OUT, "u8b_bars_with_transition.parquet")
    df.to_parquet(out_path)
    print(f"wrote {out_path} ({df.shape})")
    print(df[TRANSITION_FEATURES].describe().to_string())
    print("\nNaN counts:")
    print(df[TRANSITION_FEATURES].isna().sum().to_string())
