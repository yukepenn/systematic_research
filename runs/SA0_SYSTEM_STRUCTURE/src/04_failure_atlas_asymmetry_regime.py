"""SA0 sec12 (failure-mode atlas) + sec14 (long/short asymmetry) + sec16 (regime science).
Descriptive classification only -- no forced taxonomy, no new tradable rule."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
ledger = pd.read_parquet(S.LEDGER_PATH)
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
entry_rows = ledger[(ledger["age_bars"] == 1) & (ledger["position"] != 0)].copy()

print("=" * 90, "\nSEC12 -- FAILURE-MODE ATLAS (descriptive classification, all 1,978 blocks)\n", "=" * 90, sep="")

# exit-reason classification: for each block, look at the bar immediately after its last held bar
last_bars = ledger[ledger["position"] != 0].groupby("block_id")["t_idx"].max().rename("t_last")
atlas = block_sum.merge(last_bars, on="block_id", how="left")
atlas = atlas.merge(entry_rows[["block_id", "hm", "vote_dispersion", "HTF_tilt_state", "B",
                                 "sigma460_atr_proxy_pts", "vwap_dist_pts", "sess_date", "entry_time"]],
                     on="block_id", how="left")
next_idx = np.clip(atlas["t_last"].to_numpy() + 1, 0, S.n - 1)
atlas["next_bar_forced_flat_c4"] = S.forced_flat_c4[next_idx]
is_last_arr = np.asarray(S.bars["is_last_of_sess"])
atlas["next_bar_is_last_of_sess"] = is_last_arr[next_idx]
atlas["exit_reason"] = np.where(atlas["next_bar_forced_flat_c4"], "C4_FORCED_FLAT", "M_DRIVEN_VOLUNTARY")

# reversal vs flat-exit: does a new nonzero block start at exactly t_last+1 (no flat bar between)?
pos_at_next = ledger.set_index("t_idx").reindex(next_idx)["position"].to_numpy()
atlas["exit_type"] = np.where(pos_at_next != 0, "REVERSAL", "FLAT_EXIT")

# tail / ordinary tagging
n_blocks = len(atlas)
atlas["net_pnl_rank_pct"] = atlas["net_pnl"].rank(pct=True)
atlas["tail_tag"] = np.select(
    [atlas["net_pnl_rank_pct"] >= 0.99, atlas["net_pnl_rank_pct"] >= 0.90,
     atlas["net_pnl_rank_pct"] <= 0.01, atlas["net_pnl_rank_pct"] <= 0.10],
    ["TOP_1PCT", "TOP_10PCT", "BOTTOM_1PCT", "BOTTOM_10PCT"], default="ORDINARY")
atlas["long_short"] = np.where(atlas["side"] > 0, "LONG", "SHORT")
atlas["winner_loser"] = np.where(atlas["net_pnl"] > 0, "WINNER", "LOSER")
atlas["tod_bucket"] = pd.cut(atlas["hm"], [0, 900, 1200, 1600, 1800, 2400],
                              labels=["overnight_pre9", "morning", "midday", "close", "evening"], include_lowest=True)
atlas["age_bucket"] = pd.cut(atlas["n_bars"], [0, 20, 60, 150, 100000],
                              labels=["short(<1h)", "medium(1-3h)", "long(3-7.5h)", "very_long(>7.5h)"])
atlas["giveback_bucket"] = pd.cut(atlas["giveback_ratio"].clip(upper=3), [-0.01, 0.1, 0.5, 1.0, 100],
                                   labels=["low_gb(<0.1)", "mid_gb", "high_gb(0.5-1)", "negative_or_gt1"])

atlas.to_csv(os.path.join(OUT, "sec12_failure_atlas_full.csv"), index=False)

for dim in ["exit_reason", "exit_type", "tail_tag", "long_short", "tod_bucket", "age_bucket", "giveback_bucket"]:
    print(f"\n-- distribution + mean/sum net_pnl by {dim} --")
    g = atlas.groupby(dim, observed=True).agg(n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"),
                                                sum_pnl=("net_pnl", "sum"),
                                                win_rate=("net_pnl", lambda x: float((x > 0).mean())))
    print(g.round(2))

# descriptive failure-mode clusters among LOSER blocks only -- only where data actually supports one
losers = atlas[atlas["winner_loser"] == "LOSER"].copy()
print(f"\n{len(losers)} loser blocks of {n_blocks} ({100*len(losers)/n_blocks:.1f}%)")
loser_modes = losers.groupby(["exit_type", "giveback_bucket"], observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum")).reset_index()
loser_modes = loser_modes.sort_values("sum_pnl")
print("\n-- loser sub-clusters (exit_type x giveback_bucket), most damaging first --")
print(loser_modes.round(2).to_string(index=False))
loser_modes.to_csv(os.path.join(OUT, "sec12_loser_submodes.csv"), index=False)

print("\n" + "=" * 90, "\nSEC14 -- LONG/SHORT ASYMMETRY (Product B, NQ + MNQ economics)\n", "=" * 90, sep="")
pos_full = S.build_pos_seq(S.M, S.ENTRY_LEVEL, S.EXIT_LEVEL)
daily_nq, barpos_nq, bpnl_nq = S.onelot_exec(pos_full, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
daily_mnq, barpos_mnq, bpnl_mnq = S.onelot_exec(pos_full, S.COMM_MNQ, S.PV_MNQ, S.o_mnq, S.h_mnq, S.l_mnq, S.c_mnq)


def side_battery(barpos, bpnl, sess_arr, tag_prefix):
    rows = []
    for side_label, mask_fn in [("LONG", lambda p: p > 0), ("SHORT", lambda p: p < 0)]:
        mask = mask_fn(barpos)
        side_pnl = np.where(mask, bpnl, 0.0)
        daily = pd.DataFrame({"sess": sess_arr, "net": side_pnl}).groupby("sess")["net"].sum().reset_index()
        row = S.battery_row(f"{tag_prefix}_{side_label}", daily)
        rows.append(row)
    return rows


side_rows_nq = side_battery(barpos_nq, bpnl_nq, S.sess_arr, "NQ")
side_rows_mnq = side_battery(barpos_mnq, bpnl_mnq, S.sess_arr, "MNQ")
print("NQ economics:")
for r in side_rows_nq:
    print(f"  {r['tag']}: net={r['net']:.2f} sharpe={r['sharpe']:.3f} maxDD={r['maxDD_eod']:.2f} "
          f"CDaR95={r['CDaR95']:.2f} worst_day={r['worst_day']:.2f}")
print("MNQ economics:")
for r in side_rows_mnq:
    print(f"  {r['tag']}: net={r['net']:.2f} sharpe={r['sharpe']:.3f} maxDD={r['maxDD_eod']:.2f}")

long_blocks = atlas[atlas["long_short"] == "LONG"]
short_blocks = atlas[atlas["long_short"] == "SHORT"]
asym_block_stats = {
    "n_long_blocks": int(len(long_blocks)), "n_short_blocks": int(len(short_blocks)),
    "long_win_rate": float((long_blocks["net_pnl"] > 0).mean()),
    "short_win_rate": float((short_blocks["net_pnl"] > 0).mean()),
    "long_avg_win": float(long_blocks.loc[long_blocks["net_pnl"] > 0, "net_pnl"].mean()),
    "long_avg_loss": float(long_blocks.loc[long_blocks["net_pnl"] <= 0, "net_pnl"].mean()),
    "short_avg_win": float(short_blocks.loc[short_blocks["net_pnl"] > 0, "net_pnl"].mean()),
    "short_avg_loss": float(short_blocks.loc[short_blocks["net_pnl"] <= 0, "net_pnl"].mean()),
    "long_avg_holding_bars": float(long_blocks["n_bars"].mean()),
    "short_avg_holding_bars": float(short_blocks["n_bars"].mean()),
    "long_top10pct_share_of_long_net": float(
        long_blocks.nlargest(max(1, len(long_blocks) // 10), "net_pnl")["net_pnl"].sum() / long_blocks["net_pnl"].sum()),
    "short_top10pct_share_of_short_net": float(
        short_blocks.nlargest(max(1, len(short_blocks) // 10), "net_pnl")["net_pnl"].sum() / short_blocks["net_pnl"].sum()),
}
print(json.dumps(asym_block_stats, indent=2))

yby_long = pd.DataFrame({"year": S.year_arr, "pnl": np.where(barpos_nq > 0, bpnl_nq, 0.0)}).groupby("year")["pnl"].sum()
yby_short = pd.DataFrame({"year": S.year_arr, "pnl": np.where(barpos_nq < 0, bpnl_nq, 0.0)}).groupby("year")["pnl"].sum()
print("\nyear-by-year LONG vs SHORT (NQ):")
print(pd.DataFrame({"long": yby_long, "short": yby_short}))

json.dump({"side_battery_nq": side_rows_nq, "side_battery_mnq": side_rows_mnq,
           "block_level_asymmetry": asym_block_stats}, open(os.path.join(OUT, "sec14_long_short_asymmetry.json"), "w"), indent=2)
pd.DataFrame({"long": yby_long, "short": yby_short}).to_csv(os.path.join(OUT, "sec14_long_short_year_by_year.csv"))

print("\n" + "=" * 90, "\nSEC16 -- REGIME SCIENCE (small interpretable buckets, descriptive only)\n", "=" * 90, sep="")
atlas["vol_tercile"] = pd.qcut(atlas["sigma460_atr_proxy_pts"], 3, labels=["low_vol", "mid_vol", "high_vol"], duplicates="drop")
atlas["session_bucket"] = np.where(atlas["hm"] < 930, "overnight", np.where(atlas["hm"] <= 1600, "RTH", "post_RTH"))
atlas["consensus_tercile"] = pd.qcut(atlas["vote_dispersion"].abs(), 3, labels=["low_consensus", "mid_consensus", "high_consensus"], duplicates="drop")

for dims in [["vol_tercile"], ["session_bucket"], ["tod_bucket"], ["consensus_tercile"],
             ["vol_tercile", "session_bucket"]]:
    g = atlas.groupby(dims, observed=True).agg(n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"),
                                                  sum_pnl=("net_pnl", "sum"),
                                                  win_rate=("net_pnl", lambda x: float((x > 0).mean())))
    print(f"\n-- {dims} --")
    print(g.round(2))
    g.to_csv(os.path.join(OUT, f"sec16_regime_{'_x_'.join(dims)}.csv"))

print("\nSA0 sec12/sec14/sec16 complete.")
