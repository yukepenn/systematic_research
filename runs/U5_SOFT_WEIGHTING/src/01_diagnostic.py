"""U5 Stage 1 -- diagnostic: does R4/R5's residual-information feature set (clv_signed aligned,
vwap_disp_atr aligned, short_term_vol_ratio, rejected_upper/lower_break aligned) predict the
EVENTUAL outcome of a Product-A SCALE_IN action, at the scale-in bar, net of |M| x vol bucket
structure? Same information-addition framework as R4/R5 (residualized Spearman + OLS delta-R^2),
applied to U0's shared state table instead of re-deriving a Product-A ledger.

Explicitly excludes direction_x_volume (R5: fully tail-blind on both tails, disqualified as a
lead entirely, not just as a hard filter -- per U5 spec.yaml)."""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "action_A", "block_id_A", "age_bars_A",
        "target_exposure_A", "run_pnl_A_dollars", "MFE_A_dollars", "giveback_ratio_A",
        "M", "sigma460_atr_proxy_pts", "clv_signed", "vwap_disp_atr", "short_term_vol_ratio",
        "rejected_upper_break", "rejected_lower_break"]

print("[U5-S1] loading U0 state table (needed columns only) ...", flush=True)
df = pd.read_parquet(U0_PATH, columns=COLS)
print(f"[U5-S1] loaded {len(df):,} rows", flush=True)

canon = df[~df["is_health_only_bar"]].reset_index(drop=True)
ext = df[df["is_health_only_bar"]].reset_index(drop=True)
print(f"[U5-S1] canonical window rows: {len(canon):,}   extended (2026-06/07) rows: {len(ext):,}", flush=True)


def build_block_outcomes(frame):
    """One row per TRADING block_id_A (target_exposure_A != 0 at some point): the block-end
    (max age_bars_A) row's run_pnl_A_dollars / MFE_A_dollars / giveback_ratio_A, treated as the
    block's eventual outcome, per spec.yaml Stage 1 point 1 ('run_pnl_A_dollars at block end')."""
    nz = frame[frame["target_exposure_A"] != 0]
    idx_end = nz.groupby("block_id_A")["age_bars_A"].idxmax()
    end_rows = nz.loc[idx_end, ["block_id_A", "run_pnl_A_dollars", "MFE_A_dollars",
                                 "giveback_ratio_A", "target_exposure_A", "age_bars_A"]].copy()
    end_rows = end_rows.rename(columns={
        "run_pnl_A_dollars": "block_final_pnl", "MFE_A_dollars": "block_final_mfe",
        "giveback_ratio_A": "block_final_giveback_ratio", "target_exposure_A": "block_final_exposure",
        "age_bars_A": "block_n_bars"})
    end_rows["block_direction"] = np.sign(end_rows["block_final_exposure"]).astype(int)
    return end_rows.set_index("block_id_A")


print("[U5-S1] building block-level eventual-outcome table (canonical window) ...", flush=True)
block_outcomes = build_block_outcomes(canon)
print(f"[U5-S1] {len(block_outcomes):,} trading blocks (canonical)", flush=True)

# ---------------------------------------------------------------- SCALE_IN feature extraction
scin = canon[canon["action_A"] == "SCALE_IN"].copy()
print(f"[U5-S1] SCALE_IN bars (canonical): {len(scin):,}", flush=True)

scin["direction"] = np.sign(scin["target_exposure_A"]).astype(int)
scin["clv_aligned"] = scin["clv_signed"] * scin["direction"]
scin["vwap_aligned"] = scin["vwap_disp_atr"] * scin["direction"]
scin["stvr"] = scin["short_term_vol_ratio"]  # non-directional by construction (R5 precedent)
scin["bad_rejection"] = np.where(scin["direction"] > 0, scin["rejected_upper_break"],
                                  scin["rejected_lower_break"]).astype(float)
scin["M_abs"] = scin["M"].abs()
scin["vol"] = scin["sigma460_atr_proxy_pts"]

scin = scin.join(block_outcomes[["block_final_pnl", "block_final_mfe",
                                  "block_final_giveback_ratio", "block_n_bars"]], on="block_id_A")
n_before = len(scin)
scin = scin.dropna(subset=["block_final_pnl"])
print(f"[U5-S1] SCALE_IN rows with a resolvable block outcome: {len(scin):,} / {n_before:,}", flush=True)

# forward-only outcome: block_final_pnl minus whatever run_pnl_A_dollars ALREADY was as of the
# scale-in bar itself -- isolates "what happens AFTER this scale-in" from "P&L already banked by
# the time of a (possibly late) scale-in", which a raw block-total correlation cannot distinguish
# (a block that is already far from VWAP in its favor by definition has already earned some of its
# eventual total before this specific scale-in; forward_pnl removes that mechanical component).
scin["forward_pnl"] = scin["block_final_pnl"] - scin["run_pnl_A_dollars"]

FEATURES = ["clv_aligned", "vwap_aligned", "stvr", "bad_rejection"]

# bucket residualization: |M| tercile x vol tercile, computed over the SCALE_IN population itself
# (same convention as R4/R5's M_strength_tercile x vol_tercile over their own entry population)
scin["M_tercile"] = pd.qcut(scin["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
scin["vol_tercile"] = pd.qcut(scin["vol"], 3, labels=["low", "mid", "high"], duplicates="drop")
scin["bucket"] = scin["M_tercile"].astype(str) + "_" + scin["vol_tercile"].astype(str)
scin["vol_z"] = scin["vol_tercile"].cat.codes
scin["M_z"] = scin["M_tercile"].cat.codes

for outcome, resid_name in [("block_final_pnl", "resid_pnl"),
                             ("block_final_mfe", "resid_mfe"),
                             ("block_final_giveback_ratio", "resid_giveback")]:
    bucket_mean = scin.groupby("bucket")[outcome].transform("mean")
    scin[resid_name] = scin[outcome] - bucket_mean

scin.to_csv(os.path.join(OUT, "s1_scalein_features.csv"), index=False)
block_outcomes.reset_index().to_csv(os.path.join(OUT, "s1_block_outcomes.csv"), index=False)


def ols_delta_r2(frame, x_cols, y_col, base_cols=("M_abs", "vol_z")):
    sub = frame.dropna(subset=list(base_cols) + list(x_cols) + [y_col])
    def _r2(cols):
        X = sub[list(cols)].to_numpy(dtype=float)
        X = np.column_stack([np.ones(len(X)), X])
        y = sub[y_col].to_numpy(dtype=float)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        yhat = X @ coef
        ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
        return (1 - ss_res / ss_tot if ss_tot > 0 else np.nan), coef
    r2_base, _ = _r2(base_cols)
    r2_ext, coef_ext = _r2(list(base_cols) + list(x_cols))
    return r2_base, r2_ext, r2_ext - r2_base, coef_ext[-1], len(sub)


print("\n" + "=" * 100)
print("PRIMARY OUTCOME: block_final_pnl (run_pnl_A_dollars at block end)")
print("=" * 100)
primary_results = {}
for feat in FEATURES:
    sub = scin.dropna(subset=[feat, "block_final_pnl", "resid_pnl"])
    rho_raw = float(sub[feat].corr(sub["block_final_pnl"], method="spearman"))
    rho_resid = float(sub[feat].corr(sub["resid_pnl"], method="spearman"))
    r2_base, r2_ext, dr2, coef_last, n_ols = ols_delta_r2(scin, [feat], "block_final_pnl")
    primary_results[feat] = {"n": len(sub), "rho_raw": rho_raw, "rho_resid": rho_resid,
                              "r2_base": r2_base, "r2_ext": r2_ext, "delta_r2": dr2,
                              "coef_sign": "+" if coef_last > 0 else "-"}
    print(f"  {feat:14s}  n={len(sub):5d}  raw_rho={rho_raw:+.4f}  resid_rho={rho_resid:+.4f}  "
          f"R2_base={r2_base:.5f}  R2_ext={r2_ext:.5f}  dR2={dr2:+.5f}  coef_sign={primary_results[feat]['coef_sign']}")

print("\n" + "=" * 100)
print("ROBUSTNESS: FORWARD-ONLY OUTCOME (block_final_pnl - run_pnl_A_dollars AS OF THE SCALE-IN BAR)")
print("rules out 'this block had already banked its profit by the time of a late scale-in' confound")
print("=" * 100)
scin["fwd_bucket_mean"] = scin.groupby("bucket")["forward_pnl"].transform("mean")
scin["resid_fwd"] = scin["forward_pnl"] - scin["fwd_bucket_mean"]
forward_results = {}
for feat in FEATURES:
    sub = scin.dropna(subset=[feat, "forward_pnl", "resid_fwd"])
    rho_raw = float(sub[feat].corr(sub["forward_pnl"], method="spearman"))
    rho_resid = float(sub[feat].corr(sub["resid_fwd"], method="spearman"))
    r2_base, r2_ext, dr2, coef_last, n_ols = ols_delta_r2(scin, [feat], "forward_pnl")
    forward_results[feat] = {"n": len(sub), "rho_raw": rho_raw, "rho_resid": rho_resid, "delta_r2": dr2}
    print(f"  {feat:14s}  n={len(sub):5d}  raw_rho={rho_raw:+.4f}  resid_rho={rho_resid:+.4f}  dR2={dr2:+.5f}")
yby_fwd = {}
for feat in FEATURES:
    yby = []
    for yr, g in scin.dropna(subset=[feat, "resid_fwd"]).groupby("year"):
        rho_yr = float(g[feat].corr(g["resid_fwd"], method="spearman")) if len(g) > 5 else np.nan
        yby.append({"year": int(yr), "n": len(g), "rho_resid": rho_yr})
    yby_df = pd.DataFrame(yby)
    first_sign = np.sign(yby_df["rho_resid"].iloc[0]) if len(yby_df) else 0
    same_sign = int((np.sign(yby_df["rho_resid"]) == first_sign).sum())
    yby_fwd[feat] = yby_df.to_dict("records")
    print(f"  {feat} forward-only year-stability: same sign in {same_sign}/{len(yby_df)} years -> {yby_df['rho_resid'].round(4).tolist()}")

print("\n" + "=" * 100)
print("SECONDARY OUTCOMES: block_final_mfe, block_final_giveback_ratio (raw + residualized Spearman only)")
print("=" * 100)
secondary_results = {}
for outcome, resid_name in [("block_final_mfe", "resid_mfe"), ("block_final_giveback_ratio", "resid_giveback")]:
    secondary_results[outcome] = {}
    for feat in FEATURES:
        sub = scin.dropna(subset=[feat, outcome, resid_name])
        rho_raw = float(sub[feat].corr(sub[outcome], method="spearman"))
        rho_resid = float(sub[feat].corr(sub[resid_name], method="spearman"))
        secondary_results[outcome][feat] = {"n": len(sub), "rho_raw": rho_raw, "rho_resid": rho_resid}
        print(f"  {outcome:28s} x {feat:14s}  n={len(sub):5d}  raw_rho={rho_raw:+.4f}  resid_rho={rho_resid:+.4f}")

print("\n" + "=" * 100)
print("YEAR-BY-YEAR STABILITY (residualized Spearman vs block_final_pnl, canonical years only)")
print("=" * 100)
yby_all = {}
for feat in FEATURES:
    yby = []
    for yr, g in scin.dropna(subset=[feat, "resid_pnl"]).groupby("year"):
        rho_yr = float(g[feat].corr(g["resid_pnl"], method="spearman")) if len(g) > 5 else np.nan
        yby.append({"year": int(yr), "n": len(g), "rho_resid": rho_yr})
    yby_df = pd.DataFrame(yby)
    first_sign = np.sign(yby_df["rho_resid"].iloc[0]) if len(yby_df) else 0
    same_sign = int((np.sign(yby_df["rho_resid"]) == first_sign).sum())
    yby_all[feat] = yby_df.to_dict("records")
    print(f"\n{feat} (same sign as first year in {same_sign}/{len(yby_df)} years):")
    print(yby_df.round(4).to_string(index=False))
yby_json_path = os.path.join(OUT, "s1_year_by_year.json")
json.dump(yby_all, open(yby_json_path, "w"), indent=2, default=str)

# ---------------------------------------------------------------- right-tail check
print("\n" + "=" * 100)
print("RIGHT-TAIL CHECK: top-20 / bottom-20 Product-A blocks by block_final_pnl (canonical)")
print("=" * 100)
top20_blocks = block_outcomes.sort_values("block_final_pnl", ascending=False).head(20)
bot20_blocks = block_outcomes.sort_values("block_final_pnl", ascending=True).head(20)
print("\nTop-20 blocks by block_final_pnl:")
print(top20_blocks[["block_final_pnl", "block_final_exposure", "block_n_bars"]].round(2).to_string())
print("\nBottom-20 blocks by block_final_pnl:")
print(bot20_blocks[["block_final_pnl", "block_final_exposure", "block_n_bars"]].round(2).to_string())

# population tercile cut-points (bottom tercile == "bad" for continuous features)
cut = {}
for feat in ["clv_aligned", "vwap_aligned", "stvr"]:
    q1, q2 = scin[feat].quantile([1/3, 2/3])
    cut[feat] = (float(q1), float(q2))
print("\nPopulation tercile cut-points (SCALE_IN sample):", cut)


def tail_summary(block_ids, label):
    sub = scin[scin["block_id_A"].isin(block_ids)]
    print(f"\n{label}: {len(block_ids)} blocks, {len(sub)} SCALE_IN events within them")
    row = {"label": label, "n_blocks": len(block_ids), "n_scalein_events": len(sub)}
    for feat in ["clv_aligned", "vwap_aligned", "stvr"]:
        q1, q2 = cut[feat]
        bad_frac = float((sub[feat] < q1).mean()) if len(sub) else np.nan
        row[f"{feat}_pct_bottom_tercile"] = bad_frac
        print(f"    {feat:14s}: {bad_frac*100:5.1f}% of scale-in events are BOTTOM TERCILE "
              f"(pop cut <{q1:.4f})")
    bad_rej_frac = float(sub["bad_rejection"].mean()) if len(sub) else np.nan
    row["bad_rejection_pct"] = bad_rej_frac
    print(f"    {'bad_rejection':14s}: {bad_rej_frac*100:5.1f}% of scale-in events show the aligned-bad rejection flag")
    # per-block worst case: fraction of blocks where EVERY scale-in event is bottom-tercile on a feature
    per_block_all_bad = {}
    for feat in ["clv_aligned", "vwap_aligned", "stvr"]:
        q1, _ = cut[feat]
        allbad = sub.groupby("block_id_A")[feat].apply(lambda s: bool((s < q1).all()))
        per_block_all_bad[feat] = allbad
        n_allbad = int(allbad.sum())
        print(f"    -> blocks where ALL scale-ins are bottom-tercile {feat}: {n_allbad}/{len(block_ids)}")
        row[f"{feat}_n_blocks_all_scaleins_bad"] = n_allbad
    return row, sub


top_row, top_sub = tail_summary(set(top20_blocks.index), "TOP-20 winners")
bot_row, bot_sub = tail_summary(set(bot20_blocks.index), "BOTTOM-20 losers")

# ---------------------------------------------------------------- assemble summary
summary = {
    "n_scalein_canonical": int(len(scin)),
    "n_trading_blocks_canonical": int(len(block_outcomes)),
    "primary_results": primary_results,
    "forward_only_results": forward_results,
    "forward_only_year_by_year": yby_fwd,
    "secondary_results": secondary_results,
    "tercile_cutpoints": cut,
    "top20_tail_check": top_row,
    "bottom20_tail_check": bot_row,
}
json.dump(summary, open(os.path.join(OUT, "s1_summary.json"), "w"), indent=2, default=str)
pd.DataFrame([top_row, bot_row]).to_csv(os.path.join(OUT, "s1_tail_check.csv"), index=False)

print("\n[U5-S1] Stage 1 diagnostic complete.")
print(json.dumps(summary, indent=2, default=str))
