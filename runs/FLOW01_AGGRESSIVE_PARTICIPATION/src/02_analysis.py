"""FLOW01 step 2 -- redundancy check, residual-information test, trade-collapsed robustness
check, right-tail audit, and DUAL clustered bootstrap (session-block PRIMARY per U9's frozen
design, trade-block SECONDARY per this family's own addendum C7) for the 5 preregistered
checkpoint-level microstructure features against forward markout, computed SEPARATELY for
HOLD checkpoints and PRE_EXIT (immediately-before-actual-EXIT/REVERSAL) checkpoints.

NOT independent-observation data (addendum C7): a single trade can contain hundreds of HOLD
checkpoints. Every inferential statistic below is reported alongside BOTH raw checkpoint n and
effective independent n (n_trades, n_sessions).
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

cp = pd.read_csv(os.path.join(OUT, "checkpoint_features.csv"))
FEATS = ["signed_flow_aligned_60s", "flow_persistence_60s", "avg_spread_ticks_60s",
         "quote_intensity_60s", "ret1s_vol_60s"]
HORIZONS = ["fwd1_pnl", "fwd3_pnl"]

cp = cp[cp["n_grid_rows_60s"] >= 30].copy()  # usable-window filter (per build script)
print(f"[FLOW01] usable checkpoints after window filter: n={len(cp)}", flush=True)

groups = {
    "HOLD": cp[cp["is_hold_checkpoint"]].copy(),
    "PRE_EXIT": cp[cp["is_pre_exit_checkpoint"]].copy(),
}
for g, df in groups.items():
    print(f"[FLOW01] group {g}: n_checkpoints={len(df)}, n_trades={df['block_id_B'].nunique()}, "
          f"n_sessions={df['sess_date'].nunique()}", flush=True)

# ---------------------------------------------------------------- Step 0: redundancy vs existing U0 features
print("\n" + "=" * 90 + "\nSTEP 0 -- REDUNDANCY vs existing OHLCV-derived U0 features\n" + "=" * 90)
redund = {}
for gname, df in groups.items():
    for f in FEATS:
        for existing in ["sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr"]:
            sub = df.dropna(subset=[f, existing])
            if len(sub) < 10:
                continue
            rho = float(sub[f].corr(sub[existing], method="spearman"))
            key = f"{gname}:{f}_vs_{existing}"
            redund[key] = rho
            if abs(rho) > 0.3:
                flag = "REDUNDANT" if abs(rho) > 0.7 else ""
                print(f"  {key}: rho={rho:.3f} {flag}")
max_redund = max(abs(v) for v in redund.values())
print(f"\nmax |rho| across all redundancy checks: {max_redund:.3f} "
      f"({'FLAGGED' if max_redund > 0.7 else 'no feature flagged redundant'})")

# ---------------------------------------------------------------- residual-info test (raw Spearman + OLS controlling for M_abs)
print("\n" + "=" * 90 + "\nRESIDUAL-INFORMATION TEST (raw Spearman + OLS controlling for |M|, checkpoint-level pooled)\n"
      "NOTE: checkpoint-level n is NOT independent-observation n -- see session/trade-block bootstrap below.\n" + "=" * 90)


def ols_r2(df, X_cols, y_col):
    sub = df.dropna(subset=X_cols + [y_col])
    if len(sub) < 15:
        return np.nan, len(sub)
    X = sub[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = sub[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    return (1 - ss_res / ss_tot if ss_tot > 0 else np.nan), len(sub)


results = {}
for gname, df in groups.items():
    for ycol in HORIZONS:
        r2_base, n_base = ols_r2(df, ["M_abs"], ycol)
        print(f"\n{gname} / {ycol} (n={len(df)}): baseline R^2 (M_abs only) = {r2_base:.4f} (n={n_base})")
        for f in FEATS:
            sub = df.dropna(subset=[f, ycol])
            rho = float(sub[f].corr(sub[ycol], method="spearman")) if len(sub) >= 10 else np.nan
            r2_ext, n_ext = ols_r2(df, ["M_abs", f], ycol)
            delta = r2_ext - r2_base if (r2_ext == r2_ext and r2_base == r2_base) else np.nan
            results[f"{gname}:{ycol}:{f}"] = {"raw_rho": rho, "delta_r2": delta, "n_checkpoints": n_ext,
                                               "n_trades": int(sub["block_id_B"].nunique()),
                                               "n_sessions": int(sub["sess_date"].nunique())}
            print(f"  {f}: raw_rho={rho:+.4f}  delta_R2={delta:+.5f}  "
                  f"n_cp={n_ext}  n_trades={results[f'{gname}:{ycol}:{f}']['n_trades']}  "
                  f"n_sess={results[f'{gname}:{ycol}:{f}']['n_sessions']}")

# ---------------------------------------------------------------- trade-collapsed robustness (n=n_trades, no within-trade pseudo-replication)
print("\n" + "=" * 90 + "\nTRADE-COLLAPSED ROBUSTNESS (one row per block_id_B: mean feature, mean fwd markout)\n"
      "Directly removes within-trade pseudo-replication (addendum C7's core concern) rather than\n"
      "relying on the bootstrap alone to account for it.\n" + "=" * 90)
trade_collapsed_results = {}
for gname, df in groups.items():
    coll = df.groupby("block_id_B").agg({**{f: "mean" for f in FEATS}, **{y: "mean" for y in HORIZONS},
                                          "sess_date": "first"}).reset_index()
    for ycol in HORIZONS:
        for f in FEATS:
            sub = coll.dropna(subset=[f, ycol])
            rho = float(sub[f].corr(sub[ycol], method="spearman")) if len(sub) >= 10 else np.nan
            trade_collapsed_results[f"{gname}:{ycol}:{f}"] = {"raw_rho": rho, "n_trades": len(sub)}
    print(f"\n{gname} (n_trades={coll['block_id_B'].nunique()}):")
    for ycol in HORIZONS:
        row = "  " + ycol + ": " + ", ".join(
            f"{f}=rho{trade_collapsed_results[f'{gname}:{ycol}:{f}']['raw_rho']:+.3f}"
            if trade_collapsed_results[f'{gname}:{ycol}:{f}']['raw_rho'] == trade_collapsed_results[f'{gname}:{ycol}:{f}']['raw_rho']
            else f"{f}=rho=NaN" for f in FEATS)
        print(row)

# ---------------------------------------------------------------- clustered-bootstrap helper (used below)
rng = np.random.RandomState(20260809)


def clustered_bootstrap(df, feat, ycol, cluster_col, n_boot=1000):
    sub = df.dropna(subset=[feat, ycol])
    clusters = sub[cluster_col].unique()
    if len(clusters) < 3:
        return {"observed_rho": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "n_boot": 0, "n_clusters": len(clusters)}
    cl_groups = {c: sub[sub[cluster_col] == c].index.to_numpy() for c in clusters}
    obs_rho = float(sub[feat].corr(sub[ycol], method="spearman"))
    boot_rhos = []
    for _ in range(n_boot):
        sampled = rng.choice(clusters, size=len(clusters), replace=True)
        idx = np.concatenate([cl_groups[c] for c in sampled if len(cl_groups[c]) > 0])
        if len(idx) < 10:
            continue
        d = sub.loc[idx]
        r = d[feat].corr(d[ycol], method="spearman")
        if r == r:
            boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    ci_lo, ci_hi = (np.percentile(boot_rhos, [2.5, 97.5]) if len(boot_rhos) else (np.nan, np.nan))
    return {"observed_rho": obs_rho, "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
            "n_boot": len(boot_rhos), "n_clusters": len(clusters)}


# ---------------------------------------------------------------- session-block bootstrap on the TRADE-COLLAPSED
# analysis (the one place a numerically non-trivial correlation appeared: HOLD group,
# signed_flow_aligned_60s, trade-collapsed rho up to +0.31). Trades are already collapsed to
# 1 row each (removes within-trade pseudo-replication); still cluster by SESSION since a
# session can contain >1 trade (63 trades / 33 sessions with checkpoints).
print("\n" + "=" * 90 + "\nSESSION-BLOCK BOOTSTRAP on TRADE-COLLAPSED HOLD data (addresses the one numerically\n"
      "non-trivial trade-collapsed correlation: signed_flow_aligned_60s)\n" + "=" * 90)
hold_coll = groups["HOLD"].groupby("block_id_B").agg(
    **{f: (f, "mean") for f in FEATS}, **{y: (y, "mean") for y in HORIZONS},
    sess_date=("sess_date", "first")).reset_index()
print(f"trades/session distribution: {hold_coll.groupby('sess_date').size().describe().to_dict()}")
trade_collapsed_bootstrap = {}
for ycol in HORIZONS:
    for f in ["signed_flow_aligned_60s", "avg_spread_ticks_60s"]:  # the two trade-collapsed cells worth checking
        b = clustered_bootstrap(hold_coll, f, ycol, "sess_date")
        key = f"HOLD_TRADE_COLLAPSED:{ycol}:{f}"
        trade_collapsed_bootstrap[key] = b
        excl0 = (b["ci_lo"] > 0 or b["ci_hi"] < 0) if b["ci_lo"] == b["ci_lo"] else False
        print(f"  {key}: rho={b['observed_rho']:+.4f}  session-CI=[{b['ci_lo']:+.3f},{b['ci_hi']:+.3f}]"
              f"(n_sess={b['n_clusters']}, n_trade_rows={len(hold_coll)}){'  <-- excludes 0' if excl0 else ''}")

# ---------------------------------------------------------------- strongest cell (checkpoint-level pooled), by |raw rho|
valid = {k: v for k, v in results.items() if v["raw_rho"] == v["raw_rho"]}
best_key = max(valid, key=lambda k: abs(valid[k]["raw_rho"]))
print(f"\nStrongest cell by |raw rho| (checkpoint-level pooled): {best_key} -> {results[best_key]}")
best_group, best_ycol, best_feat = best_key.split(":")

# ---------------------------------------------------------------- right-tail check (top-20/bottom-20)
print("\n" + "=" * 90 + f"\nRIGHT-TAIL CHECK for strongest cell {best_key} (top-20/bottom-20 checkpoints by {best_ycol})\n" + "=" * 90)
df_sel = groups[best_group]
sub = df_sel.dropna(subset=[best_feat, best_ycol]).sort_values(best_ycol)
n_tail = min(20, len(sub) // 3)
bot_tail = sub.head(n_tail)
top_tail = sub.tail(n_tail)
print(f"n={len(sub)}, tail size n={n_tail} each side")
print(f"top-{n_tail} (best {best_ycol}, >= ${top_tail[best_ycol].min():.2f}): "
      f"{best_feat} mean={top_tail[best_feat].mean():.4f}, "
      f"from {top_tail['block_id_B'].nunique()} distinct trades / {top_tail['sess_date'].nunique()} sessions")
print(f"bottom-{n_tail} (worst {best_ycol}, <= ${bot_tail[best_ycol].max():.2f}): "
      f"{best_feat} mean={bot_tail[best_feat].mean():.4f}, "
      f"from {bot_tail['block_id_B'].nunique()} distinct trades / {bot_tail['sess_date'].nunique()} sessions")
print(f"population mean {best_feat} = {sub[best_feat].mean():.4f}")
right_tail = {
    "cell": best_key, "n": len(sub), "n_tail": n_tail,
    "top_tail_mean": float(top_tail[best_feat].mean()), "top_tail_n_trades": int(top_tail["block_id_B"].nunique()),
    "top_tail_n_sessions": int(top_tail["sess_date"].nunique()),
    "bottom_tail_mean": float(bot_tail[best_feat].mean()), "bottom_tail_n_trades": int(bot_tail["block_id_B"].nunique()),
    "bottom_tail_n_sessions": int(bot_tail["sess_date"].nunique()),
    "population_mean": float(sub[best_feat].mean()),
}

# ---------------------------------------------------------------- DUAL clustered bootstrap
print("\n" + "=" * 90 + f"\nCLUSTERED BOOTSTRAPS for ALL cells (1000 resamples each, session-block PRIMARY per\n"
      "U9's frozen design; trade-block SECONDARY per this family's addendum C7)\n" + "=" * 90)
bootstrap_results = {}
for gname, df in groups.items():
    for ycol in HORIZONS:
        for f in FEATS:
            key = f"{gname}:{ycol}:{f}"
            sess_boot = clustered_bootstrap(df, f, ycol, "sess_date")
            trade_boot = clustered_bootstrap(df, f, ycol, "block_id_B")
            excl0_sess = (sess_boot["ci_lo"] > 0 or sess_boot["ci_hi"] < 0) if sess_boot["ci_lo"] == sess_boot["ci_lo"] else False
            excl0_trade = (trade_boot["ci_lo"] > 0 or trade_boot["ci_hi"] < 0) if trade_boot["ci_lo"] == trade_boot["ci_lo"] else False
            bootstrap_results[key] = {"session_block": sess_boot, "trade_block": trade_boot,
                                       "excludes_zero_session": bool(excl0_sess), "excludes_zero_trade": bool(excl0_trade)}
            marker = "  <-- BOTH exclude 0" if (excl0_sess and excl0_trade) else ("  <-- session-only excl 0" if excl0_sess else "")
            print(f"  {key}: rho={sess_boot['observed_rho']:+.4f}  "
                  f"session-CI=[{sess_boot['ci_lo']:+.3f},{sess_boot['ci_hi']:+.3f}](n_sess={sess_boot['n_clusters']})  "
                  f"trade-CI=[{trade_boot['ci_lo']:+.3f},{trade_boot['ci_hi']:+.3f}](n_trades={trade_boot['n_clusters']}){marker}")

n_both_excl0 = sum(1 for v in bootstrap_results.values() if v["excludes_zero_session"] and v["excludes_zero_trade"])
n_cells = len(bootstrap_results)
print(f"\n{n_both_excl0}/{n_cells} cells have BOTH session-block and trade-block bootstrap CIs excluding zero.")

# ---------------------------------------------------------------- summary dump
summary = {
    "n_checkpoints_total_usable": len(cp),
    "group_sizes": {g: {"n_checkpoints": len(df), "n_trades": int(df["block_id_B"].nunique()),
                         "n_sessions": int(df["sess_date"].nunique())} for g, df in groups.items()},
    "max_redundancy_rho": max_redund,
    "residual_info_results_checkpoint_pooled": results,
    "trade_collapsed_results": trade_collapsed_results,
    "trade_collapsed_session_bootstrap": trade_collapsed_bootstrap,
    "strongest_cell_checkpoint_pooled": best_key,
    "right_tail_check": right_tail,
    "clustered_bootstrap_all_cells": bootstrap_results,
    "n_cells_both_bootstraps_exclude_zero": n_both_excl0,
    "n_cells_total": n_cells,
}
json.dump(summary, open(os.path.join(OUT, "flow01_analysis_summary.json"), "w"), indent=2, default=str)
print("\nFLOW01 analysis complete.")
