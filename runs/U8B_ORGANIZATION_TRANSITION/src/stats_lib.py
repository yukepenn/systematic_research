"""U8B shared statistics library -- copied verbatim from U8's stats_lib.py (Stage 1:
run_cell/print_cell, bucket-residualize against |M| tercile x vol tercile, fit terciles on
canonical rows only per U3's own qcut_frozen convention, then residualized Spearman +
interpretable OLS delta-R^2 via np.linalg.lstsq, year-by-year sign stability on the residualized
relationship, health-only 2026-06/07 extension reported separately and never blended), PLUS a new
Stage 2 (interaction_cell/print_interaction_cell): an explicit np.linalg.lstsq interaction-term
OLS test, pattern reused in spirit from U1_SESSION_HETEROGENEITY/src/03_test2_interaction_ols.py
-- outcome ~ intercept + |M| + vol_tercile_code + feature (additive) vs
outcome ~ intercept + |M| + vol_tercile_code + feature + feature:|M| (interaction), isolating
whether the feature's effect on the outcome DEPENDS on |M| level (distinct from Stage 1's test of
whether the feature adds information after conditioning on an |M| x vol bucket)."""
import numpy as np
import pandas as pd


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


def run_cell(frame, feature_col, outcome_col, m_abs_col, vol_col, year_col, health_col,
             label):
    """frame: one row per observation (block entry / HOLD bar / SCALE_IN bar). Must contain
    feature_col, outcome_col, m_abs_col, vol_col, year_col (int, calendar year), health_col
    (bool, True for 2026-06/07 extension rows). Returns a dict with everything spec.yaml
    requires for one (feature x outcome) cell."""
    f = frame.copy()
    canon = ~f[health_col].astype(bool)

    f["_m_tercile"] = qcut_frozen(f[m_abs_col], canon, ["weak", "mid", "strong"])
    f["_vol_tercile"] = qcut_frozen(f[vol_col], canon, ["low", "mid", "high"])
    f["_bucket"] = f["_m_tercile"].astype(str) + "_" + f["_vol_tercile"].astype(str)

    # bucket means fit on CANONICAL rows only, applied unchanged to all rows (incl. extension)
    canon_bucket_mean = f.loc[canon].groupby("_bucket")[outcome_col].mean()
    f["_bucket_mean"] = f["_bucket"].map(canon_bucket_mean)
    f["_resid"] = f[outcome_col] - f["_bucket_mean"]

    canon_f = f[canon].dropna(subset=[feature_col, outcome_col])
    raw_sub = canon_f.dropna(subset=[feature_col, outcome_col])
    raw_rho = float(raw_sub[feature_col].corr(raw_sub[outcome_col], method="spearman")) if len(raw_sub) > 5 else np.nan

    resid_sub = canon_f.dropna(subset=[feature_col, "_resid"])
    resid_rho = float(resid_sub[feature_col].corr(resid_sub["_resid"], method="spearman")) if len(resid_sub) > 5 else np.nan

    f["_vol_code"] = f["_vol_tercile"].cat.codes if hasattr(f["_vol_tercile"], "cat") else 0
    base_cols = [m_abs_col, "_vol_code"]
    r2_base, _, n_base = ols_r2(canon_f.assign(_vol_code=f.loc[canon_f.index, "_vol_code"]), base_cols, outcome_col)
    r2_ext, coef_ext, n_ext = ols_r2(canon_f.assign(_vol_code=f.loc[canon_f.index, "_vol_code"]),
                                      base_cols + [feature_col], outcome_col)
    delta_r2 = r2_ext - r2_base
    feat_coef_sign = "+" if coef_ext[-1] > 0 else "-"

    # year-by-year sign stability of the RESIDUALIZED relationship (2022-2025 canonical, then
    # 2026-canonical-only as its own row -- health-only extension reported separately, below)
    yby_rows = []
    for yr in [2022, 2023, 2024, 2025]:
        g = resid_sub[resid_sub[year_col] == yr]
        rho_yr = float(g[feature_col].corr(g["_resid"], method="spearman")) if len(g) > 5 else np.nan
        yby_rows.append({"year": yr, "n": len(g), "spearman_resid": rho_yr})
    g26 = resid_sub[(resid_sub[year_col] == 2026)]
    yby_rows.append({"year": "2026-canonical(Jan-May29)", "n": len(g26),
                      "spearman_resid": float(g26[feature_col].corr(g26["_resid"], method="spearman")) if len(g26) > 5 else np.nan})
    yby = pd.DataFrame(yby_rows)
    signs = np.sign(yby["spearman_resid"].dropna())
    n_same_sign = int((signs == np.sign(resid_rho)).sum()) if not np.isnan(resid_rho) else 0
    n_years_valid = int(signs.notna().sum()) if hasattr(signs, "notna") else len(signs)

    # health-only 2026-06/07 extension -- observational only, using the CANON-fit buckets, never
    # blended into the sign-stability count above
    ext = f[f[health_col].astype(bool)].dropna(subset=[feature_col, outcome_col, "_resid"])
    ext_raw_rho = float(ext[feature_col].corr(ext[outcome_col], method="spearman")) if len(ext) > 5 else np.nan
    ext_resid_rho = float(ext[feature_col].corr(ext["_resid"], method="spearman")) if len(ext) > 5 else np.nan

    return {
        "cell": label, "feature": feature_col, "outcome": outcome_col,
        "n_canonical": len(canon_f), "raw_spearman": raw_rho, "residualized_spearman": resid_rho,
        "ols_r2_baseline": r2_base, "ols_r2_extended": r2_ext, "ols_delta_r2": delta_r2,
        "ols_feature_coef_sign": feat_coef_sign,
        "n_years_same_sign": n_same_sign, "n_years_total": len(yby),
        "year_by_year": yby.to_dict("records"),
        "n_health_only_extension": len(ext),
        "extension_raw_spearman": ext_raw_rho, "extension_residualized_spearman": ext_resid_rho,
    }


def print_cell(res):
    print(f"\n--- {res['cell']} ---")
    print(f"  n={res['n_canonical']}  raw Spearman={res['raw_spearman']:.4f}  "
          f"residualized Spearman={res['residualized_spearman']:.4f}")
    print(f"  OLS R^2 baseline={res['ols_r2_baseline']:.5f}  extended={res['ols_r2_extended']:.5f}  "
          f"delta={res['ols_delta_r2']:+.5f}  (feature coef sign {res['ols_feature_coef_sign']})")
    print(f"  year-by-year (residualized): " +
          ", ".join(f"{r['year']}={r['spearman_resid']:.4f}(n={r['n']})" for r in res["year_by_year"]))
    print(f"  sign-stability: {res['n_years_same_sign']}/{res['n_years_total']} years same sign as overall residualized rho")
    print(f"  2026-06/07 HEALTH-ONLY extension (n={res['n_health_only_extension']}, observational, "
          f"not blended): raw={res['extension_raw_spearman']:.4f} resid={res['extension_residualized_spearman']:.4f}")


def ols_fit_with_se(X, y):
    """Full OLS fit (intercept prepended) with homoskedastic coefficient SEs, matching U1's
    03_test2_interaction_ols.py ols_fit() exactly."""
    X1 = np.column_stack([np.ones(len(X)), X])
    coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
    yhat = X1 @ coef
    resid = y - yhat
    ss_res = np.sum(resid ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    n, k = X1.shape
    dof = max(n - k, 1)
    sigma2 = ss_res / dof
    try:
        XtX_inv = np.linalg.inv(X1.T @ X1)
        se = np.sqrt(np.diag(sigma2 * XtX_inv))
    except np.linalg.LinAlgError:
        se = np.full(k, np.nan)
    return coef, se, r2, n


def interaction_cell(frame, feature_col, outcome_col, m_abs_col, vol_col, health_col, label):
    """Stage 2: outcome ~ |M| + vol_tercile_code + feature (additive) vs
    outcome ~ |M| + vol_tercile_code + feature + feature:|M| (interaction), canonical rows only
    (terciles/frame already carry vol_tercile computed the same way run_cell does -- recomputed
    here identically so this function is self-contained and callable independent of run_cell)."""
    f = frame.copy()
    canon = ~f[health_col].astype(bool)
    f["_vol_tercile"] = qcut_frozen(f[vol_col], canon, ["low", "mid", "high"])
    f["_vol_code"] = f["_vol_tercile"].cat.codes.astype(float) if hasattr(f["_vol_tercile"], "cat") else 0.0

    sub = f[canon].dropna(subset=[feature_col, outcome_col, m_abs_col, "_vol_code"])
    m_abs = sub[m_abs_col].to_numpy(dtype=float)
    vol_code = sub["_vol_code"].to_numpy(dtype=float)
    feat = sub[feature_col].to_numpy(dtype=float)
    y = sub[outcome_col].to_numpy(dtype=float)

    X_add = np.column_stack([m_abs, vol_code, feat])
    coef_add, se_add, r2_add, n_add = ols_fit_with_se(X_add, y)

    inter = feat * m_abs
    X_int = np.column_stack([m_abs, vol_code, feat, inter])
    coef_int, se_int, r2_int, n_int = ols_fit_with_se(X_int, y)

    names_int = ["intercept", "|M|", "vol_tercile_code", feature_col, f"{feature_col}:|M|"]
    interaction_coef = float(coef_int[-1])
    interaction_se = float(se_int[-1])
    interaction_t = interaction_coef / interaction_se if interaction_se and interaction_se > 0 else np.nan
    delta_r2_interaction = r2_int - r2_add

    return {
        "cell": label, "feature": feature_col, "outcome": outcome_col,
        "n": int(n_int),
        "r2_additive": float(r2_add), "r2_interaction": float(r2_int),
        "delta_r2_interaction": float(delta_r2_interaction),
        "interaction_coef": interaction_coef, "interaction_se": interaction_se,
        "interaction_t": float(interaction_t) if interaction_t == interaction_t else None,
        "coef_names": names_int,
        "coef_additive": {n: float(c) for n, c in zip(["intercept", "|M|", "vol_tercile_code", feature_col], coef_add)},
        "coef_interaction": {n: float(c) for n, c in zip(names_int, coef_int)},
    }


def print_interaction_cell(res):
    print(f"\n--- STAGE 2 (interaction) {res['cell']} ---")
    print(f"  n={res['n']}  R^2 additive={res['r2_additive']:.5f}  R^2 with interaction={res['r2_interaction']:.5f}  "
          f"delta R^2(interaction)={res['delta_r2_interaction']:+.5f}")
    print(f"  interaction coef ({res['feature']}:|M|) = {res['interaction_coef']:.5f}  "
          f"se={res['interaction_se']:.5f}  t={res['interaction_t']}")
