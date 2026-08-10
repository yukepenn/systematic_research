"""
COMBO01_MULTIMODAL_SYNERGY -- step 2: additive-vs-interaction test of
FLOW01's signed_flow_aligned_60s x AUCTION01's value-state (|value_dist_ticks|,
poc_share) on forward markout (fwd1_pnl, fwd3_pnl).

Preregistered per spec.yaml (frozen before this script was run):
  - primary contrast: near-vs-far tercile (mid dropped), HOLD group, 4 cells
  - secondary/exploratory: same 4 cells, PRE_EXIT group (expected data-limited)
  - robustness: full 3-bucket (near/mid/far, ordinal 0/1/2) linear-interaction,
    all rows, HOLD group only
  - dual clustered bootstrap (session-block PRIMARY, trade-block SECONDARY),
    1000 reps each
  - too-good-to-be-true gate: sigma460 confound residualization + session/trade
    concentration check, applied to any cell where BOTH bootstrap CIs on b3
    exclude zero
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT_DIR = f"{REPO}\\runs\\COMBO01_MULTIMODAL_SYNERGY\\out"

RNG_SEED = 20260809
N_BOOT = 1000

VD_CUTS = (106.0, 288.0)
PS_CUTS = (0.0025263630184046504, 0.003627408988512731)

FLOW_COL = "signed_flow_aligned_60s"


def ols_fit(X, y):
    """OLS via lstsq. X must already include an intercept column. Returns
    (coefs, r2)."""
    coefs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coefs
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coefs, r2


def additive_interaction_stats(flow, bucket, y):
    n = len(y)
    ones = np.ones(n)
    X_add = np.column_stack([ones, flow, bucket])
    X_int = np.column_stack([ones, flow, bucket, flow * bucket])
    coefs_add, r2_add = ols_fit(X_add, y)
    coefs_int, r2_int = ols_fit(X_int, y)
    b3 = coefs_int[3]
    return {
        "b1_flow_main_additive": float(coefs_add[1]),
        "b2_bucket_main_additive": float(coefs_add[2]),
        "r2_additive": float(r2_add),
        "b3_interaction": float(b3),
        "r2_interaction": float(r2_int),
        "delta_r2": float(r2_int - r2_add),
    }


def rho_split(flow, bucket, y):
    """bucket assumed binary 0/1 here (near=0,far=1 or low=0,high=1)."""
    mask0 = bucket == 0
    mask1 = bucket == 1
    rho0 = spearmanr(flow[mask0], y[mask0]).statistic if mask0.sum() > 2 else np.nan
    rho1 = spearmanr(flow[mask1], y[mask1]).statistic if mask1.sum() > 2 else np.nan
    return {
        "rho_near_or_low": float(rho0) if rho0 == rho0 else None,
        "rho_far_or_high": float(rho1) if rho1 == rho1 else None,
        "rho_diff_far_minus_near": float(rho1 - rho0) if (rho0 == rho0 and rho1 == rho1) else None,
    }


def cluster_index_map(cluster_ids):
    """cluster_id (array) -> dict{cluster_value: np.array of row positions}."""
    df = pd.DataFrame({"c": cluster_ids, "idx": np.arange(len(cluster_ids))})
    return {k: v["idx"].to_numpy() for k, v in df.groupby("c")}


def cluster_bootstrap(flow, bucket, y, cluster_ids, statfunc, n_boot=N_BOOT, seed=RNG_SEED):
    """Resample distinct cluster values with replacement; concatenate their row
    indices (with repeats -> duplicated rows, standard cluster bootstrap);
    recompute statfunc(flow_r, bucket_r, y_r) each rep. Returns array of stat
    draws (statfunc may return a dict of named scalars -> collected per key)."""
    rng = np.random.default_rng(seed)
    idx_map = cluster_index_map(cluster_ids)
    clusters = np.array(list(idx_map.keys()))
    n_clusters = len(clusters)
    draws = []
    for _ in range(n_boot):
        sampled = rng.choice(clusters, size=n_clusters, replace=True)
        idx = np.concatenate([idx_map[c] for c in sampled])
        draws.append(statfunc(flow[idx], bucket[idx], y[idx]))
    return draws


def pct_ci(values):
    arr = np.array([v for v in values if v is not None and v == v])
    if len(arr) == 0:
        return [None, None]
    lo, hi = np.percentile(arr, [2.5, 97.5])
    return [float(lo), float(hi)]


def excludes_zero(ci):
    if ci[0] is None:
        return None
    return (ci[0] > 0) or (ci[1] < 0)


def run_cell(df, cut_variable, outcome_col, group_label, cuts):
    """near-vs-far primary contrast for one (cut_variable, outcome) cell."""
    lo_cut, hi_cut = cuts
    if cut_variable == "value_dist_ticks_abs_tercile":
        val = df["abs_value_dist_ticks"].to_numpy()
        bucket_name_lo, bucket_name_hi = "near", "far"
    elif cut_variable == "poc_share_tercile":
        val = df["poc_share"].to_numpy()
        bucket_name_lo, bucket_name_hi = "low", "high"
    else:
        raise ValueError(cut_variable)

    is_lo = val < lo_cut
    is_hi = val >= hi_cut
    sub_mask = is_lo | is_hi
    sub = df.loc[sub_mask].copy()
    bucket = np.where(val[sub_mask] >= hi_cut, 1, 0).astype(float)
    flow = sub[FLOW_COL].to_numpy(dtype=float)
    y = sub[outcome_col].to_numpy(dtype=float)
    trades = sub["block_id_B"].to_numpy()
    sessions = sub["sess_tag"].to_numpy()

    point = additive_interaction_stats(flow, bucket, y)
    point_rho = rho_split(flow, bucket, y)

    def stat_b3_dr2(f, b, yy):
        r = additive_interaction_stats(f, b, yy)
        return {"b3": r["b3_interaction"], "delta_r2": r["delta_r2"]}

    def stat_rho(f, b, yy):
        r = rho_split(f, b, yy)
        return {"rho_diff": r["rho_diff_far_minus_near"]}

    sess_boot_b3dr2 = cluster_bootstrap(flow, bucket, y, sessions, stat_b3_dr2, seed=RNG_SEED)
    trade_boot_b3dr2 = cluster_bootstrap(flow, bucket, y, trades, stat_b3_dr2, seed=RNG_SEED + 1)
    sess_boot_rho = cluster_bootstrap(flow, bucket, y, sessions, stat_rho, seed=RNG_SEED + 2)
    trade_boot_rho = cluster_bootstrap(flow, bucket, y, trades, stat_rho, seed=RNG_SEED + 3)

    sess_b3_ci = pct_ci([d["b3"] for d in sess_boot_b3dr2])
    trade_b3_ci = pct_ci([d["b3"] for d in trade_boot_b3dr2])
    sess_dr2_ci = pct_ci([d["delta_r2"] for d in sess_boot_b3dr2])
    trade_dr2_ci = pct_ci([d["delta_r2"] for d in trade_boot_b3dr2])
    sess_rhodiff_ci = pct_ci([d["rho_diff"] for d in sess_boot_rho])
    trade_rhodiff_ci = pct_ci([d["rho_diff"] for d in trade_boot_rho])

    b3_signal = (excludes_zero(sess_b3_ci) is True) and (excludes_zero(trade_b3_ci) is True)
    rhodiff_signal = (excludes_zero(sess_rhodiff_ci) is True) and (excludes_zero(trade_rhodiff_ci) is True)

    return {
        "group": group_label,
        "cut_variable": cut_variable,
        "outcome": outcome_col,
        "bucket_labels": [bucket_name_lo, bucket_name_hi],
        "n_checkpoints": int(len(sub)),
        "n_trades": int(sub["block_id_B"].nunique()),
        "n_sessions": int(sub["sess_tag"].nunique()),
        "n_checkpoints_near_or_low": int((bucket == 0).sum()),
        "n_checkpoints_far_or_high": int((bucket == 1).sum()),
        "point_estimate": point,
        "point_rho_split": point_rho,
        "bootstrap": {
            "session_block_b3_CI": sess_b3_ci,
            "trade_block_b3_CI": trade_b3_ci,
            "session_block_deltaR2_CI": sess_dr2_ci,
            "trade_block_deltaR2_CI": trade_dr2_ci,
            "session_block_rhodiff_CI": sess_rhodiff_ci,
            "trade_block_rhodiff_CI": trade_rhodiff_ci,
        },
        "signal_b3_both_CIs_exclude_zero": bool(b3_signal),
        "signal_rhodiff_both_CIs_exclude_zero": bool(rhodiff_signal),
    }


def run_3bucket_robustness(df, cut_variable, outcome_col, cuts):
    lo_cut, hi_cut = cuts
    if cut_variable == "value_dist_ticks_abs_tercile":
        val = df["abs_value_dist_ticks"].to_numpy()
    else:
        val = df["poc_share"].to_numpy()
    bucket_ord = np.where(val < lo_cut, 0.0, np.where(val < hi_cut, 1.0, 2.0))
    flow = df[FLOW_COL].to_numpy(dtype=float)
    y = df[outcome_col].to_numpy(dtype=float)
    sessions = df["sess_tag"].to_numpy()
    trades = df["block_id_B"].to_numpy()

    point = additive_interaction_stats(flow, bucket_ord, y)

    def stat_b3_dr2(f, b, yy):
        r = additive_interaction_stats(f, b, yy)
        return {"b3": r["b3_interaction"], "delta_r2": r["delta_r2"]}

    sess_boot = cluster_bootstrap(flow, bucket_ord, y, sessions, stat_b3_dr2, seed=RNG_SEED + 10)
    trade_boot = cluster_bootstrap(flow, bucket_ord, y, trades, stat_b3_dr2, seed=RNG_SEED + 11)
    sess_ci = pct_ci([d["b3"] for d in sess_boot])
    trade_ci = pct_ci([d["b3"] for d in trade_boot])

    return {
        "cut_variable": cut_variable,
        "outcome": outcome_col,
        "n_checkpoints": int(len(df)),
        "n_trades": int(df["block_id_B"].nunique()),
        "n_sessions": int(df["sess_tag"].nunique()),
        "point_estimate": point,
        "session_block_b3_CI": sess_ci,
        "trade_block_b3_CI": trade_ci,
        "signal": bool((excludes_zero(sess_ci) is True) and (excludes_zero(trade_ci) is True)),
    }


def sigma460_confound_check(df, cut_variable, cuts):
    if cut_variable == "value_dist_ticks_abs_tercile":
        val = df["abs_value_dist_ticks"]
    else:
        val = df["poc_share"]
    corr = float(val.corr(df["sigma460_atr_proxy_pts"]))
    return {"cut_variable": cut_variable, "corr_bucket_predictor_vs_sigma460": round(corr, 4)}


def residualized_rerun(df, cut_variable, outcome_col, cuts):
    """Residualize signed_flow_aligned_60s and outcome on sigma460_atr_proxy_pts
    (linear), then rerun the near-vs-far interaction test on residuals. Only
    used inside the too-good-to-be-true gate."""
    lo_cut, hi_cut = cuts
    if cut_variable == "value_dist_ticks_abs_tercile":
        val = df["abs_value_dist_ticks"].to_numpy()
    else:
        val = df["poc_share"].to_numpy()
    is_lo = val < lo_cut
    is_hi = val >= hi_cut
    sub_mask = is_lo | is_hi
    sub = df.loc[sub_mask].copy()
    bucket = np.where(val[sub_mask] >= hi_cut, 1, 0).astype(float)

    sig = sub["sigma460_atr_proxy_pts"].to_numpy(dtype=float)
    ones = np.ones(len(sub))
    Xc = np.column_stack([ones, sig])

    flow_raw = sub[FLOW_COL].to_numpy(dtype=float)
    y_raw = sub[outcome_col].to_numpy(dtype=float)

    coefs_f, _ = ols_fit(Xc, flow_raw)
    flow_resid = flow_raw - Xc @ coefs_f
    coefs_y, _ = ols_fit(Xc, y_raw)
    y_resid = y_raw - Xc @ coefs_y

    point = additive_interaction_stats(flow_resid, bucket, y_resid)
    sessions = sub["sess_tag"].to_numpy()
    trades = sub["block_id_B"].to_numpy()

    def stat_b3(f, b, yy):
        r = additive_interaction_stats(f, b, yy)
        return {"b3": r["b3_interaction"]}

    sess_ci = pct_ci([d["b3"] for d in cluster_bootstrap(flow_resid, bucket, y_resid, sessions, stat_b3, seed=RNG_SEED + 20)])
    trade_ci = pct_ci([d["b3"] for d in cluster_bootstrap(flow_resid, bucket, y_resid, trades, stat_b3, seed=RNG_SEED + 21)])

    return {
        "cut_variable": cut_variable,
        "outcome": outcome_col,
        "b3_on_residuals": point["b3_interaction"],
        "delta_r2_on_residuals": point["delta_r2"],
        "session_block_b3_CI": sess_ci,
        "trade_block_b3_CI": trade_ci,
        "signal": bool((excludes_zero(sess_ci) is True) and (excludes_zero(trade_ci) is True)),
    }


def concentration_check(df, cut_variable, cuts, bucket_side):
    lo_cut, hi_cut = cuts
    if cut_variable == "value_dist_ticks_abs_tercile":
        val = df["abs_value_dist_ticks"]
    else:
        val = df["poc_share"]
    if bucket_side == "hi":
        sel = df.loc[val >= hi_cut]
    else:
        sel = df.loc[val < lo_cut]
    sess_counts = sel["sess_tag"].value_counts()
    trade_counts = sel["block_id_B"].value_counts()
    top4_sess_share = float(sess_counts.head(4).sum() / max(len(sel), 1))
    top4_trade_share = float(trade_counts.head(4).sum() / max(len(sel), 1))
    return {
        "bucket_side": bucket_side,
        "n": int(len(sel)),
        "n_sessions": int(sel["sess_tag"].nunique()),
        "n_trades": int(sel["block_id_B"].nunique()),
        "top4_sessions_share_of_bucket": round(top4_sess_share, 3),
        "top4_trades_share_of_bucket": round(top4_trade_share, 3),
    }


def main():
    merged = pd.read_csv(f"{OUT_DIR}\\merged_checkpoints.csv", parse_dates=["time"])

    results = {"primary_HOLD": [], "secondary_PRE_EXIT": [], "robustness_3bucket_HOLD": [],
               "too_good_to_be_true": {}}

    hold = merged[merged["is_hold_checkpoint"] & merged["analysis_ok"]].copy()
    preexit = merged[merged["is_pre_exit_checkpoint"] & merged["analysis_ok"]].copy()

    cells = [
        ("value_dist_ticks_abs_tercile", "fwd1_pnl", VD_CUTS),
        ("value_dist_ticks_abs_tercile", "fwd3_pnl", VD_CUTS),
        ("poc_share_tercile", "fwd1_pnl", PS_CUTS),
        ("poc_share_tercile", "fwd3_pnl", PS_CUTS),
    ]

    for cut_var, outcome, cuts in cells:
        results["primary_HOLD"].append(run_cell(hold, cut_var, outcome, "HOLD", cuts))

    for cut_var, outcome, cuts in cells:
        results["secondary_PRE_EXIT"].append(run_cell(preexit, cut_var, outcome, "PRE_EXIT", cuts))

    for cut_var, outcome, cuts in [
        ("value_dist_ticks_abs_tercile", "fwd1_pnl", VD_CUTS),
        ("value_dist_ticks_abs_tercile", "fwd3_pnl", VD_CUTS),
        ("poc_share_tercile", "fwd1_pnl", PS_CUTS),
        ("poc_share_tercile", "fwd3_pnl", PS_CUTS),
    ]:
        results["robustness_3bucket_HOLD"].append(run_3bucket_robustness(hold, cut_var, outcome, cuts))

    # --- too-good-to-be-true gate ---
    # (1) sigma460 confound correlation, always computed and reported for the
    #     primary HOLD cut variables (cheap, informative regardless of trigger)
    sigma_checks = [
        sigma460_confound_check(hold, "value_dist_ticks_abs_tercile", VD_CUTS),
        sigma460_confound_check(hold, "poc_share_tercile", PS_CUTS),
    ]
    results["too_good_to_be_true"]["sigma460_confound_correlations"] = sigma_checks

    # (2) trigger condition: any primary HOLD cell with both CIs excluding zero
    #     on b3 -> run residualized rerun + concentration check for that cell
    triggered_cells = [c for c in results["primary_HOLD"] if c["signal_b3_both_CIs_exclude_zero"]]
    residualized = []
    concentration = []
    for c in triggered_cells:
        cuts = VD_CUTS if c["cut_variable"] == "value_dist_ticks_abs_tercile" else PS_CUTS
        residualized.append(residualized_rerun(hold, c["cut_variable"], c["outcome"], cuts))
        concentration.append(concentration_check(hold, c["cut_variable"], cuts, "hi"))
        concentration.append(concentration_check(hold, c["cut_variable"], cuts, "lo"))
    results["too_good_to_be_true"]["triggered_cells"] = [
        {"cut_variable": c["cut_variable"], "outcome": c["outcome"]} for c in triggered_cells
    ]
    results["too_good_to_be_true"]["residualized_on_sigma460"] = residualized
    results["too_good_to_be_true"]["concentration_checks"] = concentration

    # (3) lookahead re-verification note (mechanical, always true by construction
    #     -- recorded here as an explicit disclosed check, not just asserted in
    #     prose)
    results["too_good_to_be_true"]["lookahead_reverification"] = {
        "merge_direction_used": "backward",
        "tolerance": "2s",
        "note": (
            "merge_asof(direction='backward') guarantees the matched poc_share/"
            "value_dist_ticks row's own timestamp is <= the FLOW01 checkpoint's "
            "timestamp within the same session (by=sess_tag). Both parent "
            "features (signed_flow_aligned_60s: trailing 60s window ending at "
            "checkpoint T; poc_share/value_dist_ticks: causal running "
            "cumsum/cummax as of T) are independently already-verified causal in "
            "their own parent REPORT.md by code inspection. No new lookahead is "
            "introduced by this join."
        ),
    }

    with open(f"{OUT_DIR}\\combo01_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
