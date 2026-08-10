"""
COMBO01_MULTIMODAL_SYNERGY -- step 1: merge FLOW01 checkpoint substrate with
AUCTION01's causal 1-second value-state substrate.

Strictly causal, backward merge_asof by session. No new data read (governance wall):
only runs/FLOW01_AGGRESSIVE_PARTICIPATION/out/checkpoint_features.csv and
runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet, both already-built, already-
reported substrates from the same 37-session BBO-confirmed universe.

Outputs:
  out/merged_checkpoints.csv   -- every FLOW01 checkpoint, with matched poc_share /
                                   value_dist_ticks and rth/liquid/matched flags.
  out/build_summary.json       -- match-rate and filter-cascade disclosure.
"""
import json
import pandas as pd
import numpy as np

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
FLOW01_PATH = f"{REPO}\\runs\\FLOW01_AGGRESSIVE_PARTICIPATION\\out\\checkpoint_features.csv"
AUCTION01_PATH = f"{REPO}\\runs\\AUCTION01_VALUE_STATE\\out\\poc_1s_full.parquet"
OUT_DIR = f"{REPO}\\runs\\COMBO01_MULTIMODAL_SYNERGY\\out"

RTH_START = pd.Timestamp("09:30:00").time()
RTH_END = pd.Timestamp("16:00:00").time()
TOLERANCE = pd.Timedelta("2s")


def main():
    cf = pd.read_csv(FLOW01_PATH, parse_dates=["time"])
    cf["sess_tag"] = cf["sess_date"].str.replace("-", "", regex=False)
    n_raw_total = len(cf)
    n_raw_hold = int(cf["is_hold_checkpoint"].sum())
    n_raw_preexit = int(cf["is_pre_exit_checkpoint"].sum())

    poc = pd.read_parquet(
        AUCTION01_PATH,
        columns=["time", "sess_tag", "poc_share", "value_dist_ticks", "bid_upd", "ask_upd"],
    )
    poc = poc.sort_values(["sess_tag", "time"]).reset_index(drop=True)
    # Causal trailing-60-row (=60s, since poc_1s_full is one row per second) BBO
    # update-count sum, replicating AUCTION01's own decision-point liquidity gate
    # (trailing-60s(bid_upd+ask_upd) > 0) exactly, computed here because
    # poc_1s_full itself does not carry the precomputed liq60 column (only
    # decision_points_30s does, and that table lacks the sessions/timestamps we
    # need for the full-session merge -- see spec.yaml merge section).
    poc["bbo_upd"] = poc["bid_upd"] + poc["ask_upd"]
    poc["liq60"] = poc.groupby("sess_tag")["bbo_upd"].transform(
        lambda s: s.rolling(60, min_periods=1).sum()
    )

    cf_sorted = cf.sort_values(["sess_tag", "time"]).reset_index(drop=True)
    poc_sorted = poc.sort_values(["sess_tag", "time"]).reset_index(drop=True)

    merged = pd.merge_asof(
        cf_sorted,
        poc_sorted[["time", "sess_tag", "poc_share", "value_dist_ticks", "liq60"]],
        on="time",
        by="sess_tag",
        direction="backward",
        tolerance=TOLERANCE,
    )

    merged["matched"] = merged["poc_share"].notna()
    merged["tod"] = merged["time"].dt.time
    merged["rth"] = (merged["tod"] >= RTH_START) & (merged["tod"] < RTH_END)
    merged["liquid"] = merged["liq60"] > 0
    merged["abs_value_dist_ticks"] = merged["value_dist_ticks"].abs()
    merged["analysis_ok"] = merged["matched"] & merged["rth"] & merged["liquid"]
    merged = merged.drop(columns=["tod"])

    unmatched_sessions = sorted(merged.loc[~merged["matched"], "sess_tag"].unique().tolist())

    # --- filter cascade disclosure ---
    summary = {
        "n_raw_checkpoints_total": n_raw_total,
        "n_raw_hold": n_raw_hold,
        "n_raw_preexit": n_raw_preexit,
        "n_matched_total": int(merged["matched"].sum()),
        "n_unmatched_total": int((~merged["matched"]).sum()),
        "unmatched_sessions_affected": unmatched_sessions,
        "match_rate": round(float(merged["matched"].mean()), 4),
        "cascade": {},
    }

    for grp_name, grp_mask in [
        ("HOLD", merged["is_hold_checkpoint"]),
        ("PRE_EXIT", merged["is_pre_exit_checkpoint"]),
    ]:
        g = merged[grp_mask]
        raw_n = len(g)
        matched = g[g["matched"]]
        rth = matched[matched["rth"]]
        liquid = rth[rth["liquid"]]
        summary["cascade"][grp_name] = {
            "raw_n": raw_n,
            "raw_trades": int(g["block_id_B"].nunique()),
            "raw_sessions": int(g["sess_tag"].nunique()),
            "matched_n": len(matched),
            "matched_rth_n": len(rth),
            "matched_rth_liquid_n": len(liquid),
            "final_trades": int(liquid["block_id_B"].nunique()),
            "final_sessions": int(liquid["sess_tag"].nunique()),
        }

    # --- preregistered tercile cuts, computed ONLY from the HOLD/RTH/liquid
    # predictor marginal distributions (no outcome touched) ---
    hold_final = merged[
        merged["is_hold_checkpoint"] & merged["analysis_ok"]
    ].copy()
    vd_cuts = hold_final["abs_value_dist_ticks"].quantile([1 / 3, 2 / 3]).values.tolist()
    ps_cuts = hold_final["poc_share"].quantile([1 / 3, 2 / 3]).values.tolist()
    summary["preregistered_cuts_recomputed_check"] = {
        "value_dist_ticks_abs_tercile_cuts": vd_cuts,
        "poc_share_tercile_cuts": ps_cuts,
        "note": "must match spec.yaml cut_points exactly (frozen from this same computation).",
    }
    summary["predictor_correlation_value_dist_vs_poc_share"] = round(
        float(hold_final["poc_share"].corr(hold_final["abs_value_dist_ticks"])), 4
    )

    merged.to_csv(f"{OUT_DIR}\\merged_checkpoints.csv", index=False)
    with open(f"{OUT_DIR}\\build_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
