"""AUCTION03 -- mechanism decomposition, part 2 (M5): incumbent-aligned action-value deterioration.

Question (diagnostic, NOT a policy test): does |value_dist_ticks| (distance from the running POC,
regardless of sign) predict deterioration in the incumbent's own already-chosen-direction
continuation, once we control for momentum strength (|M| / M_A_raw), volatility regime
(sigma460_atr_proxy_pts), and session phase?

R_aligned definition -- IMPORTANT deviation from the literal task text, documented here because it
changes the arithmetic: the task spec says
    R_aligned_A = sign(target_exposure_A) * signed_markout_H_A
but inspection of the substrate builder (AUCTION02/src/01_build_action_substrate.py, lines ~100-114)
shows signed_markout_H_{A,B} is ALREADY incumbent-direction-aligned at construction time:
    side = np.sign(target_exposure_A or position_B)
    signed_markout_H = side * (fwd_close - close) / TICK   (only defined where side != 0)
Multiplying that by sign(target_exposure_A) again would square the sign (=1 for any nonzero
direction) and collapse R_aligned to the RAW, direction-FREE price change -- exactly the opposite
of "incumbent-aligned forward return", and inconsistent with AUCTION02's own step1 script, which
uses signed_markout_H_{prod} directly as the in-direction outcome with no extra sign multiplication
(see run_cell(..., outc) calls in AUCTION02/src/02_step1_diagnostics.py). We therefore define
    R_aligned_{A,B} = signed_markout_H_{A,B}   (rows already restricted to dir_col != 0)
which is the quantity the task's own prose describes and matches house convention exactly.

Method: OLS regression (task option (a)) of R_aligned on
    abs_value_dist_ticks + m_abs [|M_A_raw| for A, |M| for B] + sigma460_atr_proxy_pts
    + phase_RTH_OPEN + phase_RTH_CLOSE   (reference category: RTH_MID)
Dual-clustered (session-block AND trade/block-block, 1000 reps each) bootstrap CI on the
abs_value_dist_ticks coefficient, using the exact numpy cluster-resample machinery already
established in AUCTION02/src/stats_lib_auction02.py (reused here for the tercile mean-diff /
raw-effect leg; a matching OLS-coefficient bootstrap is added below since stats_lib_auction02 has
no regression-coefficient bootstrap helper).

To make the controlled (OLS) effect comparable in magnitude to the raw top-vs-bottom tercile
diff requested in step 3 of the task, we also report a "controlled_effect" = beta_hat *
(mean(abs_value_dist_ticks | top tercile) - mean(abs_value_dist_ticks | bottom tercile)), i.e. the
OLS-implied difference in R_aligned between a bar in the top tercile of |value_dist_ticks| and one
in the bottom tercile, holding the controls fixed -- directly next to the raw (unconditional)
top-minus-bottom diff so a reader can see how much the controls move the picture, per the task's
step 3 instruction.

Samples: DISCOVERY (37-session substrate, runs/AUCTION02_ACTION_RELEVANCE/out/action_substrate.parquet)
and CONFIRMATION (protected internal replication, 8-date W5_PROTECTED_CONFIRMATION batch --
2 of the 8 dates, 20251125 and 20260512, have zero RTH-usable BBO rows and drop out automatically
under the analysis_ok filter, exactly as documented in the task). These are reported SEPARATELY,
never pooled.
"""
import os
import sys
import json

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
AUCTION02_SRC = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "src")
sys.path.insert(0, AUCTION02_SRC)
from stats_lib_auction02 import qcut_frozen, dual_block_bootstrap_meandiff  # noqa: E402

OUT = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT, exist_ok=True)

HORIZONS = [1, 3, 20]
NBOOT = 1000
RNG = np.random.default_rng(20260810)
C1_TICKS = 2.872  # campaign round-trip cost hurdle, ticks

DISCOVERY_DATES = [
    "20250814", "20250820", "20250901", "20250902", "20250905", "20250910",
    "20250911", "20250922", "20251002", "20251009", "20251027", "20251029",
    "20251110", "20251117", "20251124", "20251128", "20251209", "20251222",
    "20260123", "20260206", "20260211", "20260218", "20260220", "20260223",
    "20260303", "20260312", "20260317", "20260320", "20260406", "20260409",
    "20260417", "20260423", "20260428", "20260506", "20260511", "20260519",
    "20260520",
]
CONFIRM_DATES = [
    "20250819", "20250912", "20251028", "20251125", "20260217",
    "20260302", "20260422", "20260512",
]


def _norm_date(s):
    """sess_date column is 'YYYY-MM-DD' string; task's date lists are 'YYYYMMDD'. Normalize both
    to 'YYYYMMDD' for the isin() filter."""
    return pd.to_datetime(s).dt.strftime("%Y%m%d")


PRODUCTS = {
    "A": dict(dir_col="target_exposure_A", trade_col="block_id_A", m_abs_src="M_A_raw"),
    "B": dict(dir_col="position_B", trade_col="block_id_B", m_abs_src="M"),
}
PHASE_REF = "RTH_MID"
PHASE_DUMMY_LEVELS = ["RTH_OPEN", "RTH_CLOSE"]  # reference = RTH_MID


def make_phase_dummies(sub):
    d = sub.copy()
    for lvl in PHASE_DUMMY_LEVELS:
        d[f"phase_{lvl}"] = (d["session_phase"] == lvl).astype(float)
    return d


def _group_index(keys_arr):
    codes, uniques = pd.factorize(keys_arr)
    idx_by_group = [np.where(codes == g)[0] for g in range(len(uniques))]
    return len(uniques), idx_by_group


def ols_fit(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coef, r2


def dual_cluster_ols_coef_ci(sub, y_col, x_cols, sess_col, trade_col, nboot=NBOOT, rng=RNG):
    """Dual-clustered (session-block, trade/block-block) bootstrap CI on the FIRST entry of
    x_cols' OLS coefficient (design matrix = [intercept, x_cols...]). Mirrors the vectorized
    cluster-resample pattern of stats_lib_auction02's dual_block_bootstrap_* helpers, extended to
    a multivariate regression coefficient (no existing helper covers this case)."""
    d = sub.dropna(subset=x_cols + [y_col]).reset_index(drop=True)
    X = np.column_stack([np.ones(len(d)), d[x_cols].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    coef_obs, r2_obs = ols_fit(X, y)
    beta_obs = float(coef_obs[1])  # x_cols[0] == predictor (abs_value_dist_ticks)
    k = X.shape[1]

    out = {"n": len(d), "beta_abs_value_dist_ticks": beta_obs, "r2": r2_obs,
           "coef_all": {c: float(v) for c, v in zip(["intercept"] + x_cols, coef_obs)}}
    for label, key_col in [("session_block_ci", sess_col), ("trade_block_ci", trade_col)]:
        n_groups, idx_by_group = _group_index(d[key_col].to_numpy())
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks])
            if len(idx) < k + 5:
                continue
            Xb, yb = X[idx], y[idx]
            if np.linalg.matrix_rank(Xb) < k:
                continue
            cb, _ = ols_fit(Xb, yb)
            boots[b] = cb[1]
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = n_groups
        out[f"{label}_n_boots_used"] = int(len(boots))
    return out


def run_sample(df, sample_label, date_list):
    df = df.copy()
    df["_datekey"] = _norm_date(df["sess_date"])
    df = df[df["_datekey"].isin(date_list)].copy()
    ok = df[df["analysis_ok"]].copy()
    print(f"[{sample_label}] rows after date filter+analysis_ok: {len(ok)} "
          f"(dates present={sorted(ok['_datekey'].unique())})", flush=True)

    rows = []
    for prod, cfg in PRODUCTS.items():
        sub = ok[ok[cfg["dir_col"]] != 0].copy()
        sub["m_abs"] = sub[cfg["m_abs_src"]].abs()
        sub = make_phase_dummies(sub)
        n_trades = sub[cfg["trade_col"]].nunique()
        n_sess = sub["sess_tag"].nunique()
        print(f"[{sample_label}] product {prod}: n={len(sub)}, trade_blocks={n_trades}, "
              f"sessions={n_sess}", flush=True)

        # preregistered tercile cuts on the predictor's own marginal distribution (no outcome
        # touched) -- identical convention to AUCTION02 step1
        vd_cuts = sub["abs_value_dist_ticks"].quantile([1 / 3, 2 / 3]).tolist()
        sub["vd_tercile"] = pd.cut(sub["abs_value_dist_ticks"],
                                    bins=[-np.inf, vd_cuts[0], vd_cuts[1], np.inf],
                                    labels=["near", "mid", "far"])
        mean_top = float(sub.loc[sub["vd_tercile"] == "far", "abs_value_dist_ticks"].mean())
        mean_bot = float(sub.loc[sub["vd_tercile"] == "near", "abs_value_dist_ticks"].mean())
        tercile_scale = mean_top - mean_bot

        x_cols = ["abs_value_dist_ticks", "m_abs", "sigma460_atr_proxy_pts"] + \
                 [f"phase_{lvl}" for lvl in PHASE_DUMMY_LEVELS]

        for H in HORIZONS:
            y_col = f"signed_markout_{H}_{prod}"

            # ---- raw (unconditional) top-vs-bottom tercile diff, dual-clustered ----
            raw = dual_block_bootstrap_meandiff(sub, "vd_tercile", "far", "near", y_col,
                                                 "sess_tag", cfg["trade_col"])

            # ---- OLS-controlled effect, dual-clustered CI on the abs_value_dist_ticks coef ----
            ols = dual_cluster_ols_coef_ci(sub, y_col, x_cols, "sess_tag", cfg["trade_col"])
            beta = ols["beta_abs_value_dist_ticks"]
            controlled_effect = beta * tercile_scale
            ctrl_ci_sess = [ols["session_block_ci"][0] * tercile_scale,
                             ols["session_block_ci"][1] * tercile_scale]
            ctrl_ci_trade = [ols["trade_block_ci"][0] * tercile_scale,
                              ols["trade_block_ci"][1] * tercile_scale]
            # tercile_scale > 0 by construction (far mean > near mean of an abs() quantity), so
            # sign of the CI endpoints is preserved by this rescaling
            sig_sess = not (min(ctrl_ci_sess) <= 0 <= max(ctrl_ci_sess))
            sig_trade = not (min(ctrl_ci_trade) <= 0 <= max(ctrl_ci_trade))
            significant_dual = bool(sig_sess and sig_trade)
            if significant_dual:
                direction = "deterioration" if controlled_effect < 0 else "improvement"
            else:
                direction = "null"

            row = {
                "sample": sample_label, "product": prod, "horizon": H,
                "n": ols["n"], "n_trade_blocks": n_trades, "n_sessions": n_sess,
                "m_abs_source": cfg["m_abs_src"],
                "tercile_cuts_abs_value_dist_ticks": vd_cuts,
                "tercile_scale_far_minus_near_mean_ticks": tercile_scale,
                # raw (unconditional)
                "raw_diff_top_minus_bottom_tercile": raw["diff"],
                "raw_mean_far": raw["mean_a"], "raw_mean_near": raw["mean_b"],
                "raw_ci_session": raw["session_block_ci"],
                "raw_ci_trade": raw["trade_block_ci"],
                "raw_n_far": raw["n_a"], "raw_n_near": raw["n_b"],
                # OLS-controlled
                "ols_beta_abs_value_dist_ticks_per_tick": beta,
                "ols_r2": ols["r2"], "ols_coef_all": ols["coef_all"],
                "controlled_effect": controlled_effect,
                "controlled_ci_session": ctrl_ci_sess,
                "controlled_ci_trade": ctrl_ci_trade,
                "ols_session_block_ci_beta": ols["session_block_ci"],
                "ols_trade_block_ci_beta": ols["trade_block_ci"],
                "ols_session_n_clusters": ols["session_block_ci_n_clusters"],
                "ols_trade_n_clusters": ols["trade_block_ci_n_clusters"],
                "significant_session": bool(sig_sess), "significant_trade": bool(sig_trade),
                "significant_dual": significant_dual, "direction": direction,
                # economic-relevance context
                "controlled_effect_pct_of_C1": controlled_effect / C1_TICKS,
                "raw_diff_pct_of_C1": raw["diff"] / C1_TICKS,
            }
            rows.append(row)
            print(f"[{sample_label}] {prod} H={H}: raw_diff={raw['diff']:+.4f}t "
                  f"(sess_CI={raw['session_block_ci']}, trade_CI={raw['trade_block_ci']}) | "
                  f"controlled_effect={controlled_effect:+.4f}t "
                  f"(sess_CI={[round(x,4) for x in ctrl_ci_sess]}, "
                  f"trade_CI={[round(x,4) for x in ctrl_ci_trade]}) | "
                  f"beta={beta:+.6f}t/tick | dual_sig={significant_dual} dir={direction}",
                  flush=True)
    return rows


def main():
    disc_path = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out",
                              "action_substrate.parquet")
    conf_path = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                              "action_substrate_CONFIRM.parquet")

    disc_df = pd.read_parquet(disc_path)
    conf_df = pd.read_parquet(conf_path)

    all_rows = []
    all_rows += run_sample(disc_df, "discovery", DISCOVERY_DATES)
    all_rows += run_sample(conf_df, "confirmation", CONFIRM_DATES)

    out_df = pd.DataFrame([{k: v for k, v in r.items()
                             if k not in ("ols_coef_all", "tercile_cuts_abs_value_dist_ticks",
                                          "raw_ci_session", "raw_ci_trade",
                                          "controlled_ci_session", "controlled_ci_trade",
                                          "ols_session_block_ci_beta", "ols_trade_block_ci_beta")}
                            for r in all_rows])
    # flatten CI list columns into lo/hi pairs for the CSV
    ci_cols = ["raw_ci_session", "raw_ci_trade", "controlled_ci_session", "controlled_ci_trade",
               "ols_session_block_ci_beta", "ols_trade_block_ci_beta"]
    for col in ci_cols:
        out_df[f"{col}_lo"] = [r[col][0] for r in all_rows]
        out_df[f"{col}_hi"] = [r[col][1] for r in all_rows]
    out_df["tercile_cut_lo"] = [r["tercile_cuts_abs_value_dist_ticks"][0] for r in all_rows]
    out_df["tercile_cut_hi"] = [r["tercile_cuts_abs_value_dist_ticks"][1] for r in all_rows]

    csv_path = os.path.join(OUT, "m5_action_value_residual.csv")
    out_df.to_csv(csv_path, index=False)
    json_path = os.path.join(OUT, "m5_action_value_residual.json")
    with open(json_path, "w") as f:
        json.dump({"rows": all_rows, "c1_ticks": C1_TICKS,
                   "discovery_dates": DISCOVERY_DATES, "confirmation_dates": CONFIRM_DATES,
                   "notes": "R_aligned = signed_markout_H_{prod} directly (already "
                            "incumbent-direction-aligned at substrate build time); see module "
                            "docstring for why the task's literal sign()*signed_markout formula "
                            "is not applied verbatim."},
                  f, indent=2, default=float)
    print(f"\nWrote {csv_path}")
    print(f"Wrote {json_path}")
    print("M5 ACTION-VALUE RESIDUAL DIAGNOSTIC DONE")


if __name__ == "__main__":
    main()
