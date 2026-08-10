"""AUCTION02 -- Step 1: action-relevance diagnostics. For canonical-window, RTH+liquid,
in-direction bars (Product A: target_exposure_A!=0; Product B: position_B!=0), does
value_dist_ticks (primary) / poc_share (secondary) carry information about the forward outcome
of the incumbent's ALREADY-CHOSEN direction (signed markout, MFE, MAE, large-move probability)?
Bucket-residualization + delta-R^2 (stats_lib_auction02, adapted from U8/R4/R5/EXP01/VAR01's
shared framework) + dual session-block/trade-block clustered bootstrap (COMBO01's own standard).
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib_auction02 import run_cell, dual_block_bootstrap_corr, dual_block_bootstrap_meandiff

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out")
HORIZONS = [1, 3, 20]

df = pd.read_parquet(os.path.join(OUT, "action_substrate.parquet"))
ok = df[df["analysis_ok"]].copy()
print(f"[step1] analysis_ok universe: n={len(ok)}, sessions={ok['sess_tag'].nunique()}", flush=True)

# ---------------------------------------------------------------- chronological session half-split
# (AUCTION01's own precedent for this exact 9-month tick substrate: first-half vs second-half
# session date, not calendar-year, since the sample doesn't span multiple years)
sess_order = sorted(ok["sess_tag"].unique())
mid = len(sess_order) // 2
h1_sessions = set(sess_order[:mid])
ok["half"] = np.where(ok["sess_tag"].isin(h1_sessions), "H1", "H2")
print(f"[step1] chronological split: H1 {sess_order[0]}..{sess_order[mid-1]} ({mid} sessions), "
      f"H2 {sess_order[mid]}..{sess_order[-1]} ({len(sess_order)-mid} sessions)", flush=True)

results = {"per_product": {}, "cascade": {}, "cut_points": {}, "confound_check": {},
           "concentration_check": {}, "large_move": {}}

PRODUCTS = {
    "A": dict(dir_col="target_exposure_A", trade_col="block_id_A", m_abs_src="M_A_raw"),
    "B": dict(dir_col="position_B", trade_col="block_id_B", m_abs_src="M"),
}

for prod, cfg in PRODUCTS.items():
    sub = ok[ok[cfg["dir_col"]] != 0].copy()
    sub["m_abs"] = sub[cfg["m_abs_src"]].abs()
    n_trades = sub[cfg["trade_col"]].nunique()
    n_sess = sub["sess_tag"].nunique()
    print(f"\n[step1] === Product {prod}: n={len(sub)}, trades={n_trades}, sessions={n_sess} ===", flush=True)
    results["cascade"][prod] = {"n": len(sub), "n_trades": n_trades, "n_sessions": n_sess}

    # preregistered tercile cuts (from this product's own marginal distribution, before any
    # outcome is touched) -- matches COMBO01's own convention exactly
    vd_cuts = sub["abs_value_dist_ticks"].quantile([1/3, 2/3]).tolist()
    ps_cuts = sub["poc_share"].quantile([1/3, 2/3]).tolist()
    results["cut_points"][prod] = {"abs_value_dist_ticks": vd_cuts, "poc_share": ps_cuts}
    print(f"[step1] {prod} cut points: |value_dist_ticks| tercile={vd_cuts}, poc_share tercile={ps_cuts}", flush=True)

    sub["vd_tercile"] = pd.cut(sub["abs_value_dist_ticks"], bins=[-np.inf, vd_cuts[0], vd_cuts[1], np.inf],
                                labels=["near", "mid", "far"])
    sub["ps_tercile"] = pd.cut(sub["poc_share"], bins=[-np.inf, ps_cuts[0], ps_cuts[1], np.inf],
                                labels=["low", "mid", "high"])

    # ---- too-good-to-be-true confound check (matches AUCTION01/COMBO01 precedent exactly) ----
    conf = {}
    for pred_col in ["abs_value_dist_ticks", "poc_share"]:
        conf[f"{pred_col}_vs_sigma460"] = float(sub[pred_col].corr(sub["sigma460_atr_proxy_pts"], method="spearman"))
        conf[f"{pred_col}_vs_minutes_since_open"] = float(sub[pred_col].corr(sub["minutes_since_session_open"], method="spearman"))
    results["confound_check"][prod] = conf
    print(f"[step1] {prod} confound check: {conf}", flush=True)

    prod_cells = []
    for pred_col, pred_label in [("abs_value_dist_ticks", "value_dist_ticks_abs"), ("poc_share", "poc_share")]:
        for H in HORIZONS:
            for outc, outc_label in [(f"signed_markout_{H}_{prod}", "signed_markout"),
                                      (f"mfe_{H}_{prod}", "mfe"), (f"mae_{H}_{prod}", "mae")]:
                cell = run_cell(sub, pred_col, outc, "m_abs", "sigma460_atr_proxy_pts", "half",
                                 label=f"{prod}__{pred_label}__{outc_label}_{H}")
                prod_cells.append(cell)
    results["per_product"][prod] = prod_cells
    for c in prod_cells:
        print(f"  {c['cell']}: n={c['n']} raw_rho={c['raw_spearman']:.4f} "
              f"resid_rho={c['residualized_spearman']:.4f} dR2={c['ols_delta_r2']:+.5f} "
              f"halves_same_sign={c['n_halves_same_sign']}/{c['n_halves_total']}", flush=True)

    # ---- dual-clustered bootstrap: PRIMARY predictor (value_dist_ticks_abs) x signed_markout,
    # every horizon; SECONDARY predictor (poc_share) x signed_markout, every horizon ----
    boot_rows = []
    for pred_col, pred_label in [("abs_value_dist_ticks", "value_dist_ticks_abs"), ("poc_share", "poc_share")]:
        for H in HORIZONS:
            ycol = f"signed_markout_{H}_{prod}"
            r = dual_block_bootstrap_corr(sub, pred_col, ycol, "sess_tag", cfg["trade_col"])
            r.update({"product": prod, "predictor": pred_label, "outcome": f"signed_markout_{H}"})
            boot_rows.append(r)
            print(f"  [boot-corr] {prod} {pred_label} vs signed_markout_{H}: n={r['n']} rho={r['rho']:.4f} "
                  f"sess_CI={r['session_block_ci']} trade_CI={r['trade_block_ci']}", flush=True)
    results.setdefault("bootstrap_corr", {})[prod] = boot_rows

    # ---- near-vs-far tercile mean-diff, dual-clustered, on signed_markout / mfe / mae ----
    md_rows = []
    for cut_col, pred_label, lo_lab, hi_lab in [("vd_tercile", "value_dist_ticks_abs", "near", "far"),
                                                 ("ps_tercile", "poc_share", "low", "high")]:
        for H in HORIZONS:
            for outc, outc_label in [(f"signed_markout_{H}_{prod}", "signed_markout"),
                                      (f"mfe_{H}_{prod}", "mfe"), (f"mae_{H}_{prod}", "mae")]:
                r = dual_block_bootstrap_meandiff(sub, cut_col, hi_lab, lo_lab, outc, "sess_tag", cfg["trade_col"])
                r.update({"product": prod, "predictor": pred_label, "outcome": f"{outc_label}_{H}",
                          "contrast": f"{hi_lab}_minus_{lo_lab}"})
                md_rows.append(r)
    results.setdefault("bootstrap_meandiff", {})[prod] = md_rows
    for r in md_rows:
        if r["outcome"].startswith("signed_markout"):
            print(f"  [boot-meandiff] {prod} {r['predictor']} {r['contrast']} {r['outcome']}: "
                  f"diff={r['diff']:.3f} sess_CI={r['session_block_ci']} trade_CI={r['trade_block_ci']}", flush=True)

    # ---- large-move probabilities (H=3, representative middle horizon): P(MFE_3 > pooled
    # median) = "large aligned move"; P(MAE_3 > pooled median) = "large adverse move" ----
    H = 3
    mfe_col, mae_col = f"mfe_{H}_{prod}", f"mae_{H}_{prod}"
    mfe_thresh = float(sub[mfe_col].median())
    mae_thresh = float(sub[mae_col].median())
    sub["_large_aligned"] = (sub[mfe_col] > mfe_thresh).astype(float)
    sub["_large_adverse"] = (sub[mae_col] > mae_thresh).astype(float)
    lm = {"mfe_thresh_ticks": mfe_thresh, "mae_thresh_ticks": mae_thresh, "cells": []}
    for cut_col, pred_label, lo_lab, hi_lab in [("vd_tercile", "value_dist_ticks_abs", "near", "far"),
                                                 ("ps_tercile", "poc_share", "low", "high")]:
        for ind_col, ind_label in [("_large_aligned", "P(large_aligned_move)"), ("_large_adverse", "P(large_adverse_move)")]:
            r = dual_block_bootstrap_meandiff(sub, cut_col, hi_lab, lo_lab, ind_col, "sess_tag", cfg["trade_col"])
            r.update({"predictor": pred_label, "indicator": ind_label, "contrast": f"{hi_lab}_minus_{lo_lab}"})
            lm["cells"].append(r)
            print(f"  [large-move] {prod} {pred_label} {ind_label} {r['contrast']}: "
                  f"P_hi={r['mean_a']:.3f} P_lo={r['mean_b']:.3f} diff={r['diff']:.3f} "
                  f"sess_CI={r['session_block_ci']} trade_CI={r['trade_block_ci']}", flush=True)
    results["large_move"][prod] = lm

    # ---- session/trade concentration check on the far/high tercile (only meaningful if a
    # signal is found -- computed regardless, cheap, for disclosure) ----
    far = sub[sub["vd_tercile"] == "far"]
    near = sub[sub["vd_tercile"] == "near"]
    def top4_share(g, key_col):
        vc = g[key_col].value_counts()
        return float(vc.head(4).sum() / len(g)) if len(g) else np.nan
    results["concentration_check"][prod] = {
        "far_n_trades": int(far[cfg["trade_col"]].nunique()), "far_n_sessions": int(far["sess_tag"].nunique()),
        "far_top4_session_share": top4_share(far, "sess_tag"), "far_top4_trade_share": top4_share(far, cfg["trade_col"]),
        "near_n_trades": int(near[cfg["trade_col"]].nunique()), "near_n_sessions": int(near["sess_tag"].nunique()),
        "near_top4_session_share": top4_share(near, "sess_tag"), "near_top4_trade_share": top4_share(near, cfg["trade_col"]),
    }
    print(f"[step1] {prod} concentration check: {results['concentration_check'][prod]}", flush=True)

with open(os.path.join(OUT, "step1_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=float)
print("\nSTEP1 DIAGNOSTICS DONE")
