"""U3 step 2 -- continuation-value maps (parent task point 1). Bucket mean/median forward
continuation value by a small interpretable state set, at 1/2/5/10/20-bar and until-session-
boundary horizons. Canonical window only (health-only reported separately in step 4)."""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U3_HOLD_EXPOSURE_CONTINUATION", "out")

HORIZON_COLS = ["fwd_1", "fwd_2", "fwd_5", "fwd_10", "fwd_20", "fwd_session"]
STATE_VARS = ["side", "M_abs_tercile", "M_slope_tercile", "M_change_sign", "vote_dispersion_tercile",
              "B_engaged", "vol_tercile", "session_phase", "age_bucket", "giveback_tercile",
              "clv_tercile", "rejection_aligned"]


def tstat(x):
    x = x.dropna()
    n = len(x)
    if n < 2:
        return np.nan
    s = x.std(ddof=1)
    if s == 0:
        return np.nan
    return float(x.mean() / (s / np.sqrt(n)))


def bucket_table(frame, state_var, horizon):
    rows = []
    for b, g in frame.groupby(state_var, observed=True):
        y = g[horizon]
        rows.append({
            "state_var": state_var, "bucket": b, "horizon": horizon,
            "n": int(y.notna().sum()), "mean": float(y.mean()), "median": float(y.median()),
            "std": float(y.std(ddof=1)), "tstat": tstat(y),
        })
    return pd.DataFrame(rows)


def run_leg(tag):
    print(f"=== {tag} continuation-value maps (canonical window) ===", flush=True)
    hold = pd.read_parquet(os.path.join(OUT, f"hold_{tag}.parquet"))
    canon = hold[~hold.is_health_only_bar].copy()

    # baseline (unconditioned) per horizon
    base_rows = []
    for h in HORIZON_COLS:
        y = canon[h]
        base_rows.append({"horizon": h, "n": int(y.notna().sum()), "mean": float(y.mean()),
                           "median": float(y.median()), "std": float(y.std(ddof=1)), "tstat": tstat(y)})
    base_df = pd.DataFrame(base_rows)
    base_df.to_csv(os.path.join(OUT, f"baseline_{tag}.csv"), index=False)
    print(base_df.round(3).to_string(index=False))

    all_tabs = []
    for sv in STATE_VARS:
        for h in ["fwd_1", "fwd_5", "fwd_session"]:
            all_tabs.append(bucket_table(canon, sv, h))
    full = pd.concat(all_tabs, ignore_index=True)
    full.to_csv(os.path.join(OUT, f"continuation_by_bucket_{tag}.csv"), index=False)
    print(f"wrote continuation_by_bucket_{tag}.csv ({len(full)} rows)")
    return base_df, full


base_B, full_B = run_leg("B")
base_A, full_A = run_leg("A")

print("\n02_continuation_maps.py complete.")
