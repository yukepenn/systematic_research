"""SA0 sec6 (interaction science) + sec8 (HTF science) + sec9 (B-MOM science). Conditional
expectancy / paired-event analysis only -- no causal language, no new tradable rule."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
ledger = pd.read_parquet(S.LEDGER_PATH)
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
entry_rows = ledger[(ledger["age_bars"] == 1) & (ledger["position"] != 0)].copy()
merged = block_sum.merge(
    entry_rows[["block_id", "vote_dispersion", "n_bullish", "n_bearish", "HTF_tilt_state",
                "T", "Tp", "B", "hm", "sigma460_atr_proxy_pts"]],
    on="block_id", how="left")

print("=" * 90, "\nSEC6 -- INTERACTION SCIENCE (conditional expectancy, paired events)\n", "=" * 90, sep="")

def cond_table(df, group_cols, tag):
    g = df.groupby(group_cols).agg(
        n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), median_pnl=("net_pnl", "median"),
        win_rate=("net_pnl", lambda x: float((x > 0).mean())),
        sum_pnl=("net_pnl", "sum")).reset_index()
    print(f"\n-- {tag} --")
    print(g.round(2).to_string(index=False))
    g.to_csv(os.path.join(OUT, f"sec6_{tag}.csv"), index=False)
    return g

merged["solar_htf_agree"] = np.where(
    (merged["T"] == 0) | (merged["HTF_tilt_state"] == 0), "neutral",
    np.where(np.sign(merged["T"]) == merged["HTF_tilt_state"], "agree", "disagree"))
cond_table(merged, ["solar_htf_agree"], "solar_x_htf_at_entry")

merged["bmom_engaged"] = merged["B_engaged_during_trade"].map({True: "engaged", False: "not_engaged"})
cond_table(merged, ["bmom_engaged"], "bmom_engagement")

merged["bmom_x_htf"] = np.where(
    (merged["B"] == 0) | (merged["HTF_tilt_state"] == 0), "bmom_flat_or_htf_neutral",
    np.where(np.sign(merged["B"]) == merged["HTF_tilt_state"], "bmom_agrees_htf", "bmom_disagrees_htf"))
cond_table(merged, ["bmom_x_htf"], "bmom_x_htf_at_entry")

merged["dispersion_tercile"] = pd.qcut(merged["vote_dispersion"].abs(), 3, labels=["low", "mid", "high"], duplicates="drop")
cond_table(merged.assign(hold_bars=block_sum.set_index("block_id").loc[merged["block_id"], "n_bars"].to_numpy()),
           ["dispersion_tercile"], "dispersion_x_holdproxy")
print("(hold_bars mean by tercile, using n_bars as the hold-duration proxy)")
hold_by_disp = merged.assign(hold_bars=block_sum.set_index("block_id").loc[merged["block_id"], "n_bars"].to_numpy()
                              ).groupby("dispersion_tercile")["hold_bars"].mean()
print(hold_by_disp)

merged["M_strength_tercile"] = pd.qcut((S.WSOLAR * merged["Tp"] + S.WBMOM * merged["B"]).abs(), 3,
                                        labels=["weak", "mid", "strong"], duplicates="drop")
merged["tod_bucket"] = pd.cut(merged["hm"], [0, 900, 1200, 1600, 1800, 2400],
                               labels=["overnight_pre9", "morning", "midday", "close", "evening"], include_lowest=True)
cond_table(merged, ["M_strength_tercile", "tod_bucket"], "Mstrength_x_timeofday")

merged["vol_tercile"] = pd.qcut(merged["sigma460_atr_proxy_pts"], 3, labels=["low_vol", "mid_vol", "high_vol"], duplicates="drop")
cond_table(merged, ["M_strength_tercile", "vol_tercile"], "Mstrength_x_volregime")

print("\n" + "=" * 90, "\nSEC8 -- HTF SCIENCE\n", "=" * 90, sep="")
abl_lb = pd.read_csv(os.path.join(OUT, "sec5_ablation_leaderboard.csv"))
full_nq = abl_lb[(abl_lb["tag"] == "FULL_NQ")].iloc[0]
notilt_nq = abl_lb[(abl_lb["tag"] == "NO_HTF_TILT_NQ")].iloc[0]
htf_summary = {
    "net_added_by_HTF_tilt_NQ": float(full_nq["net"] - notilt_nq["net"]),
    "sharpe_FULL": float(full_nq["sharpe"]), "sharpe_NO_HTF_TILT": float(notilt_nq["sharpe"]),
    "maxDD_FULL": float(full_nq["maxDD_eod"]), "maxDD_NO_HTF_TILT": float(notilt_nq["maxDD_eod"]),
    "CDaR95_FULL": float(full_nq["CDaR95"]), "CDaR95_NO_HTF_TILT": float(notilt_nq["CDaR95"]),
    "long_pnl_FULL": float(full_nq["long_pnl"]), "long_pnl_NO_HTF_TILT": float(notilt_nq["long_pnl"]),
    "short_pnl_FULL": float(full_nq["short_pnl"]), "short_pnl_NO_HTF_TILT": float(notilt_nq["short_pnl"]),
    "net_added_to_longs": float(full_nq["long_pnl"] - notilt_nq["long_pnl"]),
    "net_added_to_shorts": float(full_nq["short_pnl"] - notilt_nq["short_pnl"]),
}
print(json.dumps(htf_summary, indent=2))

agree_expectancy = merged.groupby("solar_htf_agree").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print("\nforward expectancy when Solar/HTF agree vs disagree at entry:")
print(agree_expectancy.round(2))
htf_summary["forward_expectancy_by_agreement"] = agree_expectancy.reset_index().to_dict("records")
json.dump(htf_summary, open(os.path.join(OUT, "sec8_htf_summary.json"), "w"), indent=2)

# tilt multiplier firing rate: how often m_arr==1.25 vs 1.0, at entry vs all bars
m_arr_all = np.where((S.T != 0) & (S.tilt_state != 0) & (np.sign(S.T) == S.tilt_state), S.TILTMULT, 1.0)
print(f"\ntilt multiplier fires (1.25x) on {100*(m_arr_all == S.TILTMULT).mean():.2f}% of all bars; "
      f"{100*(merged['solar_htf_agree'] == 'agree').mean():.2f}% of entries")

print("\n" + "=" * 90, "\nSEC9 -- B-MOM SCIENCE\n", "=" * 90, sep="")

# raw B-as-position standalone backtest: what if we traded exactly sign(B), 1 contract, ignoring
# the EntryLevel gate entirely? This is the only way to measure B's OWN standalone economic
# value, since BMOM_ONLY (sec5) proved B never independently crosses EntryLevel=3.0 on its own
# weighted score (|WBMOM*B| <= 2.83 < 3.0) -- B mathematically cannot trigger an entry alone.
#
# CRITICAL: B_arr[t] is computed inside bmom_pos_series() from bar t's OWN close. Every decision
# layer elsewhere in this codebase (build_pos_seq / one_contract_decisions) holds a ONE-BAR LAG
# between the signal and the position that takes effect (pos_seq[t] reflects the target computed
# from M[t-1], filled using bar t's OHLC) -- this is how look-ahead is avoided when a same-bar
# OHLC fill approximates the next tradable price. Feeding B_arr directly into onelot_exec WITHOUT
# that lag lets bar t's position be "filled" at bar t's own open/high/low using a signal decided
# from bar t's own close -- a genuine look-ahead bug. Caught by cross-checking against the
# already-certified runs/SMV2B_BMOM_EXEC_AUDIT/out/results.csv standalone figure (Sharpe
# 1.20-1.37 across 4 fill conventions, same 1,333 trades) -- an unlagged first attempt at this
# script produced Sharpe 5.4 / net $1.28M, an order of magnitude too high, which is what exposed
# the bug rather than a real finding. Fixed with the same one-bar lag used everywhere else.
B_arr = np.asarray(S.B).astype(int)
pos_B_raw = np.r_[0, B_arr[:-1]]  # one-bar lag, matching build_pos_seq's own pend->p timing
daily_B_raw, barpos_B, bpnl_B = S.onelot_exec(pos_B_raw, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
row_B_raw = S.battery_row("BMOM_RAW_ASPOSITION", daily_B_raw)
print(f"B-MOM raw standalone (lagged 1 bar, traded 1:1 as {{-1,0,1}} position, no EntryLevel gate): "
      f"net={row_B_raw['net']:.2f} sharpe={row_B_raw['sharpe']:.3f} maxDD={row_B_raw['maxDD_eod']:.2f}  "
      f"[cross-check target: SMV2B_BMOM_EXEC_AUDIT net~$319-332k, Sharpe~1.20-1.37]")
print("STRUCTURAL FACT: |WBMOM*B| <= 2.83 always, and EntryLevel=3.0 -- B-MOM's own weighted "
      "score CANNOT independently cross the entry threshold under any circumstance. B-MOM can "
      "only ever act as an amplifier/tiebreaker on top of a Solar score already near the line.")

# entry/hold/reversal/magnitude-only decomposition: FULL pos_seq vs SOLAR_ONLY pos_seq, bar-by-bar
pos_full = S.build_pos_seq(S.M, S.ENTRY_LEVEL, S.EXIT_LEVEL)
M_solar_only = S.WSOLAR * S.Tp
pos_solar_only = S.build_pos_seq(M_solar_only, S.ENTRY_LEVEL, S.EXIT_LEVEL)

full_sign = np.sign(pos_full); solar_sign = np.sign(pos_solar_only)
n_bars = S.n
decomp = np.full(n_bars, "AGREE_MAGNITUDE_ONLY", dtype=object)
decomp[(full_sign != 0) & (solar_sign == 0)] = "BMOM_ENABLES_ENTRY_OR_HOLD"
decomp[(full_sign == 0) & (solar_sign != 0)] = "BMOM_PREVENTS_OR_EXITS"
decomp[(full_sign != 0) & (solar_sign != 0) & (full_sign != solar_sign)] = "BMOM_FLIPS_SIDE"
decomp[(full_sign == 0) & (solar_sign == 0)] = "BOTH_FLAT"
vals, counts = np.unique(decomp, return_counts=True)
decomp_pct = {v: float(c) / n_bars * 100 for v, c in zip(vals, counts)}
print("\nbar-level FULL-vs-SOLAR_ONLY decision decomposition (% of all bars):")
print(json.dumps(decomp_pct, indent=2))

# same decomposition restricted to FRESH ENTRY bars only (transitions from flat in the FULL policy)
fresh_entry_mask = (full_sign != 0) & (np.r_[0, full_sign[:-1]] == 0)
entry_decomp = decomp[fresh_entry_mask]
vals2, counts2 = np.unique(entry_decomp, return_counts=True)
entry_decomp_pct = {v: float(c) / fresh_entry_mask.sum() * 100 for v, c in zip(vals2, counts2)}
print(f"\nsame decomposition restricted to the {int(fresh_entry_mask.sum())} FULL fresh-entry bars only:")
print(json.dumps(entry_decomp_pct, indent=2))

bmom_decomp_summary = {
    "bmom_raw_standalone_battery": row_B_raw,
    "structural_fact_bmom_cannot_solo_enter": "|WBMOM*B| max 2.83 < EntryLevel 3.0",
    "bar_level_decomposition_pct": decomp_pct,
    "fresh_entry_decomposition_pct": entry_decomp_pct,
}
json.dump(bmom_decomp_summary, open(os.path.join(OUT, "sec9_bmom_decomposition.json"), "w"), indent=2, default=str)

# B persistence (run-length) and time-of-day distribution
runs_b = []
cur_val = B_arr[0]; cur_len = 1
for v in B_arr[1:]:
    if v == cur_val:
        cur_len += 1
    else:
        runs_b.append((cur_val, cur_len)); cur_val = v; cur_len = 1
runs_b.append((cur_val, cur_len))
runs_df = pd.DataFrame(runs_b, columns=["B_value", "run_len_bars"])
nz_runs = runs_df[runs_df["B_value"] != 0]
print(f"\nB-MOM nonzero run-length (bars, 3-min each): mean={nz_runs['run_len_bars'].mean():.2f} "
      f"median={nz_runs['run_len_bars'].median():.1f} n_runs={len(nz_runs)}")

tod_nz = pd.cut(S.hm[B_arr != 0], [0, 1000, 1200, 1400, 1600, 2400],
                labels=["9-10", "10-12", "12-14", "14-16", "16+"], include_lowest=True)
print("B-MOM nonzero time-of-day distribution:")
print(pd.Series(tod_nz).value_counts(normalize=True).sort_index().round(3))

# giant winner/loser B-engagement (already have bmom_engagement table above); year-by-year raw B
yby_B = pd.DataFrame({"year": S.year_arr, "pnl": bpnl_B}).groupby("year")["pnl"].sum()
print("\nB-MOM raw standalone year-by-year:")
print(yby_B)
yby_B.to_csv(os.path.join(OUT, "sec9_bmom_raw_year_by_year.csv"))

print("\nSA0 sec6/sec8/sec9 complete.")
