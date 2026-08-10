"""AUCTION02 -- adapted copy of U8_PATH_ORGANIZATION/src/stats_lib.py's bucket-residualization +
OLS delta-R^2 framework (identical qcut_frozen / ols_r2 mechanics), generalized in ONE respect:
this substrate spans ~9 months of sessions (Aug 2025 - May 2026), not multiple calendar years, so
"year-by-year sign stability" is replaced by a first-half/second-half CHRONOLOGICAL SESSION split
-- the exact same adaptation AUCTION01's own D4 diagnostic already made on this identical
substrate ("addendum's year-by-year discipline doesn't map cleanly onto a single 9-month tick
sample, so first-half/second-half session split is used instead"). Also adds dual (session-block
+ trade/block-block) clustered bootstrap helpers matching COMBO01's own precedent (checkpoints/
bars are not independent observations; cluster by session AND by trade).
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260809)
NBOOT = 1000


def qcut_frozen(values_all, fit_mask, labels, q=3):
    fit_vals = pd.Series(values_all)[fit_mask].dropna()
    edges = np.quantile(fit_vals, np.linspace(0, 1, q + 1))
    edges = np.unique(edges)
    if len(edges) < q + 1:
        return pd.Series(pd.qcut(pd.Series(values_all).rank(method="first"), q, labels=labels),
                          index=pd.Series(values_all).index)
    return pd.cut(values_all, bins=edges, labels=labels[: len(edges) - 1],
                  include_lowest=True, duplicates="drop")


def ols_r2(frame, x_cols, y_col):
    sub = frame.dropna(subset=x_cols + [y_col])
    X = sub[x_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = sub[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return r2, coef, len(sub)


def run_cell(frame, feature_col, outcome_col, m_abs_col, vol_col, half_col, label):
    """frame: one row per bar (in-direction, RTH+liquid+matched). Bucket-residualize outcome on
    |M| tercile x sigma460 tercile (fit on this same sample -- no health-only/canonical split
    needed, the whole 37-session substrate is canonical), then compare raw vs residualized
    Spearman, and OLS baseline (m_abs, vol_code) vs extended (+feature) delta-R^2. half_col:
    'H1'/'H2' chronological session-half label, used for a 2-period sign-stability check in
    place of year-by-year (see module docstring)."""
    f = frame.copy()
    fit_mask = pd.Series(True, index=f.index)

    f["_m_tercile"] = qcut_frozen(f[m_abs_col], fit_mask, ["weak", "mid", "strong"])
    f["_vol_tercile"] = qcut_frozen(f[vol_col], fit_mask, ["low", "mid", "high"])
    f["_bucket"] = f["_m_tercile"].astype(str) + "_" + f["_vol_tercile"].astype(str)

    bucket_mean = f.groupby("_bucket")[outcome_col].transform("mean")
    f["_resid"] = f[outcome_col] - bucket_mean

    sub = f.dropna(subset=[feature_col, outcome_col])
    raw_rho = float(sub[feature_col].corr(sub[outcome_col], method="spearman")) if len(sub) > 5 else np.nan
    resid_sub = f.dropna(subset=[feature_col, "_resid"])
    resid_rho = float(resid_sub[feature_col].corr(resid_sub["_resid"], method="spearman")) if len(resid_sub) > 5 else np.nan

    f["_vol_code"] = f["_vol_tercile"].cat.codes if hasattr(f["_vol_tercile"], "cat") else 0
    base_cols = [m_abs_col, "_vol_code"]
    r2_base, _, n_base = ols_r2(f, base_cols, outcome_col)
    r2_ext, coef_ext, n_ext = ols_r2(f, base_cols + [feature_col], outcome_col)
    delta_r2 = r2_ext - r2_base
    feat_coef_sign = "+" if coef_ext[-1] > 0 else "-"

    hby = []
    for h in ["H1", "H2"]:
        g = resid_sub[resid_sub[half_col] == h]
        rho_h = float(g[feature_col].corr(g["_resid"], method="spearman")) if len(g) > 5 else np.nan
        hby.append({"half": h, "n": len(g), "spearman_resid": rho_h})
    signs = np.sign([r["spearman_resid"] for r in hby if not np.isnan(r["spearman_resid"])])
    n_same_sign = int((signs == np.sign(resid_rho)).sum()) if not np.isnan(resid_rho) else 0

    return {
        "cell": label, "feature": feature_col, "outcome": outcome_col,
        "n": len(sub), "raw_spearman": raw_rho, "residualized_spearman": resid_rho,
        "ols_r2_baseline": r2_base, "ols_r2_extended": r2_ext, "ols_delta_r2": delta_r2,
        "ols_feature_coef_sign": feat_coef_sign,
        "n_halves_same_sign": n_same_sign, "n_halves_total": len(hby),
        "half_by_half": hby,
    }


def _group_index(keys_arr):
    """Factorize a cluster-key array into (n_groups, list-of-int-index-arrays) once, so each
    bootstrap replicate is pure numpy index concatenation -- no per-replicate pandas overhead."""
    codes, uniques = pd.factorize(keys_arr)
    idx_by_group = [np.where(codes == g)[0] for g in range(len(uniques))]
    return len(uniques), idx_by_group


def dual_block_bootstrap_corr(df, xcol, ycol, sess_col, trade_col, nboot=NBOOT, rng=RNG):
    """Session-block (primary) and trade/block-block (secondary) clustered bootstrap CI on
    Spearman rho, matching COMBO01's own dual-clustering standard. Numpy-vectorized (no
    per-replicate pandas concat) for tractable runtime at n in the thousands."""
    from scipy.stats import spearmanr
    sub = df.dropna(subset=[xcol, ycol])
    x = sub[xcol].to_numpy(dtype=float)
    y = sub[ycol].to_numpy(dtype=float)
    obs_rho, _ = spearmanr(x, y)
    out = {"n": len(sub), "rho": float(obs_rho)}
    for label, key_col in [("session_block_ci", sess_col), ("trade_block_ci", trade_col)]:
        n_groups, idx_by_group = _group_index(sub[key_col].to_numpy())
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks])
            if len(idx) < 5:
                continue
            xb, yb = x[idx], y[idx]
            if np.unique(xb).size < 2 or np.unique(yb).size < 2:
                continue
            r, _ = spearmanr(xb, yb)
            boots[b] = r
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = n_groups
    return out


def dual_block_bootstrap_meandiff(df, cell_col, cell_a, cell_b, ycol, sess_col, trade_col,
                                   nboot=NBOOT, rng=RNG):
    """Numpy-vectorized dual-clustered bootstrap on a mean difference between two buckets."""
    sub = df.dropna(subset=[ycol, cell_col])
    a_mask = (sub[cell_col] == cell_a).to_numpy()
    b_mask = (sub[cell_col] == cell_b).to_numpy()
    y = sub[ycol].to_numpy(dtype=float)
    a_y, b_y = y[a_mask], y[b_mask]
    obs = a_y.mean() - b_y.mean() if len(a_y) and len(b_y) else np.nan
    out = {"n_a": int(a_mask.sum()), "n_b": int(b_mask.sum()),
           "mean_a": float(a_y.mean()) if len(a_y) else np.nan,
           "mean_b": float(b_y.mean()) if len(b_y) else np.nan, "diff": float(obs)}
    for label, key_col in [("session_block_ci", sess_col), ("trade_block_ci", trade_col)]:
        keys = sub[key_col].to_numpy()
        n_groups_a, idx_a = _group_index(keys[a_mask])
        n_groups_b, idx_b = _group_index(keys[b_mask])
        boots = np.full(nboot, np.nan)
        for i in range(nboot):
            pick_a = rng.integers(0, n_groups_a, size=n_groups_a) if n_groups_a else np.array([], dtype=int)
            pick_b = rng.integers(0, n_groups_b, size=n_groups_b) if n_groups_b else np.array([], dtype=int)
            idxa = np.concatenate([idx_a[g] for g in pick_a]) if len(pick_a) else np.array([], dtype=int)
            idxb = np.concatenate([idx_b[g] for g in pick_b]) if len(pick_b) else np.array([], dtype=int)
            if len(idxa) == 0 or len(idxb) == 0:
                continue
            boots[i] = a_y[idxa].mean() - b_y[idxb].mean()
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = n_groups_a + n_groups_b
    return out
