"""U1B Leg 1 -- Product B (BEST_ONE_NQ/MNQ) session-conditioned HOLD exit. Grid: exit_level_eth
in {1.5, 2.0}. Full validation battery: canonical full-history, 2022-2025-only delta, year-by-
year, LOYO(drop 2026), right-tail check on ETH-touched blocks, turnover/cost check, June-July-
2026 extension reported separately."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import u1b_substrate as U

OUT = U.OUT
ROOT = U.ROOT

# ================================================================== control (baseline)
ctrl_daily_nq, _, ctrl_bpnl_nq = U.HS.onelot_exec(U.CTRL_POS_B, U.HS.COMM_NQ, U.HS.PV_NQ, U.open_, U.high, U.low, U.close)
ctrl_daily_mnq, _, ctrl_bpnl_mnq = U.HS.onelot_exec(U.CTRL_POS_B, U.HS.COMM_MNQ, U.HS.PV_MNQ, U.o_mnq, U.h_mnq, U.l_mnq, U.c_mnq)
assert np.array_equal(ctrl_bpnl_nq, U.CTRL_BPNL_B_NQ) and np.array_equal(ctrl_bpnl_mnq, U.CTRL_BPNL_B_MNQ)

ctrl_daily_nq_canon = ctrl_daily_nq[pd.to_datetime(ctrl_daily_nq["sess"]) <= U.CANONICAL_END].reset_index(drop=True)
ctrl_daily_mnq_canon = ctrl_daily_mnq[pd.to_datetime(ctrl_daily_mnq["sess"]) <= U.CANONICAL_END].reset_index(drop=True)
ctrl_row_nq = U.battery_row("CONTROL_NQ", ctrl_daily_nq_canon)
ctrl_row_mnq = U.battery_row("CONTROL_MNQ", ctrl_daily_mnq_canon)
ctrl_trades = U.trade_volume(U.CTRL_POS_B[U.canon_mask])
print(f"[leg1] CONTROL canonical: NQ net={ctrl_row_nq['net']:.2f} sharpe={ctrl_row_nq['sharpe']:.4f} "
      f"maxDD={ctrl_row_nq['maxDD_eod']:.2f} CDaR95={ctrl_row_nq['CDaR95']:.2f}  "
      f"MNQ net={ctrl_row_mnq['net']:.2f}  trades={ctrl_trades}", flush=True)
print(f"[leg1] CONTROL extension (Jun-Jul-2026, observational): "
      f"NQ={U.CTRL_BPNL_B_NQ[U.health_mask].sum():.2f}  MNQ={U.CTRL_BPNL_B_MNQ[U.health_mask].sum():.2f}", flush=True)

# ================================================================== block population (from U0's table, cross-checked)
u0_path = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
u0 = pd.read_parquet(u0_path, columns=["t_idx", "is_health_only_bar", "is_rth", "position_B",
                                        "block_id_B", "bar_pnl_B_nq_dollars"])
assert len(u0) == U.n, "U0 table row count mismatch vs u1b_substrate"
# cross-check: U0's own position_B / bar_pnl_B_nq_dollars must equal this family's CONTROL exactly
assert np.array_equal(u0["position_B"].to_numpy(), U.CTRL_POS_B), "U0 position_B diverges from U1B CONTROL pos -- construction mismatch"
assert np.allclose(u0["bar_pnl_B_nq_dollars"].to_numpy(), U.CTRL_BPNL_B_NQ, atol=1e-6), "U0 bar_pnl_B_nq_dollars diverges from U1B CONTROL bpnl -- construction mismatch"
print("[leg1] cross-check vs U0 unified state table: position_B and bar_pnl_B_nq_dollars match EXACTLY", flush=True)

u0_canon = u0[~u0["is_health_only_bar"]].copy()
block_tot = u0_canon.groupby("block_id_B").agg(
    net=("bar_pnl_B_nq_dollars", "sum"),
    n_bars=("bar_pnl_B_nq_dollars", "size"),
    sgn=("position_B", lambda s: int(np.sign(s.iloc[0]))),
    eth_touched=("is_rth", lambda s: bool((~s).any())),
).reset_index()
t_idx_map = {bid: g["t_idx"].to_numpy() for bid, g in u0_canon.groupby("block_id_B")}
block_tot["t_idx_list"] = block_tot["block_id_B"].map(t_idx_map)
block_tot = block_tot[block_tot["sgn"] != 0]  # drop the (nonexistent for B, but safety) sgn==0 flat "blocks"
eth_blocks = block_tot[block_tot["eth_touched"]].sort_values("net")
print(f"[leg1] canonical blocks: {len(block_tot)} total, {len(eth_blocks)} ETH-touched "
      f"({len(eth_blocks) / len(block_tot):.1%})", flush=True)

top20 = eth_blocks.nlargest(20, "net")
bot20 = eth_blocks.nsmallest(20, "net")

# ================================================================== grid
GRID = [1.5, 2.0]
results = []
for eth_lvl in GRID:
    tag = f"B_eth{eth_lvl}"
    pos_seq = U.build_pos_seq_eth_exit(eth_lvl)
    daily_nq, barpos_nq, bpnl_nq = U.HS.onelot_exec(pos_seq, U.HS.COMM_NQ, U.HS.PV_NQ, U.open_, U.high, U.low, U.close)
    daily_mnq, barpos_mnq, bpnl_mnq = U.HS.onelot_exec(pos_seq, U.HS.COMM_MNQ, U.HS.PV_MNQ, U.o_mnq, U.h_mnq, U.l_mnq, U.c_mnq)

    daily_nq_canon = daily_nq[pd.to_datetime(daily_nq["sess"]) <= U.CANONICAL_END].reset_index(drop=True)
    daily_mnq_canon = daily_mnq[pd.to_datetime(daily_mnq["sess"]) <= U.CANONICAL_END].reset_index(drop=True)
    row_nq = U.battery_row(f"{tag}_NQ", daily_nq_canon)
    row_mnq = U.battery_row(f"{tag}_MNQ", daily_mnq_canon)

    # 2022-2025-only delta + LOYO(drop 2026) -- same slice, cross-reported
    yrs = pd.to_datetime(daily_nq_canon["sess"]).dt.year
    yrs_ctrl = pd.to_datetime(ctrl_daily_nq_canon["sess"]).dt.year
    pre2026_ctrl = ctrl_daily_nq_canon.loc[yrs_ctrl <= 2025, "net"].sum()
    pre2026_cand = daily_nq_canon.loc[yrs <= 2025, "net"].sum()
    delta_pre2026_nq = pre2026_cand - pre2026_ctrl
    loyo_ctrl = ctrl_daily_nq_canon.loc[yrs_ctrl != 2026, "net"].sum()
    loyo_cand = daily_nq_canon.loc[yrs != 2026, "net"].sum()
    full_delta_nq = row_nq["net"] - ctrl_row_nq["net"]
    full_delta_mnq = row_mnq["net"] - ctrl_row_mnq["net"]

    # year-by-year
    yby = []
    for yr in sorted(yrs.unique()):
        c_net = ctrl_daily_nq_canon.loc[yrs_ctrl == yr, "net"].sum()
        v_net = daily_nq_canon.loc[yrs == yr, "net"].sum()
        yby.append({"year": int(yr), "control_net_NQ": c_net, "candidate_net_NQ": v_net, "delta_NQ": v_net - c_net})
    yby_df = pd.DataFrame(yby)
    n_pos_years = int((yby_df["delta_NQ"] > 0).sum())

    # extension (June-July-2026), observational only
    ext_ctrl_nq = U.CTRL_BPNL_B_NQ[U.health_mask].sum()
    ext_cand_nq = bpnl_nq[U.health_mask].sum()
    ext_ctrl_mnq = U.CTRL_BPNL_B_MNQ[U.health_mask].sum()
    ext_cand_mnq = bpnl_mnq[U.health_mask].sum()

    # turnover / cost check (canonical window)
    cand_trades = U.trade_volume(pos_seq[U.canon_mask])
    extra_trades = cand_trades - ctrl_trades
    extra_commission_nq = extra_trades * U.HS.COMM_NQ
    extra_commission_mnq = extra_trades * U.HS.COMM_MNQ

    # ---------------------------------------------------------- right-tail check (ETH-touched blocks)
    def block_window_pnl(t_idx_list, bpnl_arr):
        return float(bpnl_arr[t_idx_list].sum())

    top20_rows = []
    for _, r in top20.iterrows():
        cand_pnl = block_window_pnl(r["t_idx_list"], bpnl_nq)
        top20_rows.append({"block_id_B": r["block_id_B"], "control_net": r["net"], "candidate_window_net": cand_pnl,
                            "delta": cand_pnl - r["net"]})
    top20_df = pd.DataFrame(top20_rows)
    n_top20_damaged = int((top20_df["delta"] < -1e-6).sum())
    n_top20_flipped_negative = int(((top20_df["control_net"] > 0) & (top20_df["candidate_window_net"] < 0)).sum())

    bot20_rows = []
    for _, r in bot20.iterrows():
        cand_pnl = block_window_pnl(r["t_idx_list"], bpnl_nq)
        bot20_rows.append({"block_id_B": r["block_id_B"], "control_net": r["net"], "candidate_window_net": cand_pnl,
                            "delta": cand_pnl - r["net"]})
    bot20_df = pd.DataFrame(bot20_rows)
    n_bot20_improved = int((bot20_df["delta"] > 1e-6).sum())

    results.append({
        "tag": tag, "exit_level_eth": eth_lvl,
        "net_NQ": row_nq["net"], "net_MNQ": row_mnq["net"],
        "sharpe_NQ": row_nq["sharpe"], "sortino_NQ": row_nq["sortino"], "calmar_NQ": row_nq["calmar"],
        "maxDD_eod_NQ": row_nq["maxDD_eod"], "CDaR95_NQ": row_nq["CDaR95"],
        "worst_day_NQ": row_nq["worst_day"], "worst_month_NQ": row_nq["worst_month"],
        "pos_day_pct_NQ": row_nq["pos_day_pct"],
        "sharpe_MNQ": row_mnq["sharpe"], "maxDD_eod_MNQ": row_mnq["maxDD_eod"], "CDaR95_MNQ": row_mnq["CDaR95"],
        "full_delta_NQ": full_delta_nq, "full_delta_MNQ": full_delta_mnq,
        "delta_pre2026_NQ": delta_pre2026_nq, "loyo_delta_NQ": loyo_cand - loyo_ctrl,
        "n_pos_years_of_5": n_pos_years,
        "ext_delta_NQ": ext_cand_nq - ext_ctrl_nq, "ext_delta_MNQ": ext_cand_mnq - ext_ctrl_mnq,
        "ctrl_trades": ctrl_trades, "cand_trades": cand_trades, "extra_trades": extra_trades,
        "extra_commission_NQ": extra_commission_nq, "extra_commission_MNQ": extra_commission_mnq,
        "n_top20_ETH_blocks_damaged": n_top20_damaged, "n_top20_ETH_blocks_flipped_negative": n_top20_flipped_negative,
        "n_bot20_ETH_blocks_improved": n_bot20_improved,
        "top20_total_delta": float(top20_df["delta"].sum()), "bot20_total_delta": float(bot20_df["delta"].sum()),
    })
    yby_df.to_csv(os.path.join(OUT, f"leg1_{tag}_year_by_year.csv"), index=False)
    daily_nq_canon.to_csv(os.path.join(OUT, f"leg1_{tag}_daily_NQ_canonical.csv"), index=False)
    top20_df.to_csv(os.path.join(OUT, f"leg1_{tag}_top20_ETH_blocks.csv"), index=False)
    bot20_df.to_csv(os.path.join(OUT, f"leg1_{tag}_bot20_ETH_blocks.csv"), index=False)
    print(f"[leg1] {tag}: NQ net={row_nq['net']:.2f} (ctrl {ctrl_row_nq['net']:.2f}, delta={full_delta_nq:+.2f}), "
          f"pre2026 delta={delta_pre2026_nq:+.2f}, LOYO delta={loyo_cand - loyo_ctrl:+.2f}, "
          f"pos_years={n_pos_years}/5, maxDD={row_nq['maxDD_eod']:.2f} (ctrl {ctrl_row_nq['maxDD_eod']:.2f}), "
          f"CDaR95={row_nq['CDaR95']:.2f} (ctrl {ctrl_row_nq['CDaR95']:.2f}), "
          f"extra_trades={extra_trades} (extra comm NQ=${extra_commission_nq:.2f}), "
          f"top20_ETH_damaged={n_top20_damaged}/20 (sum delta ${top20_df['delta'].sum():+.2f}), "
          f"bot20_ETH_improved={n_bot20_improved}/20 (sum delta ${bot20_df['delta'].sum():+.2f}), "
          f"ext_delta_NQ={ext_cand_nq - ext_ctrl_nq:+.2f}", flush=True)

res_df = pd.DataFrame(results)
res_df.to_csv(os.path.join(OUT, "leg1_grid_results.csv"), index=False)
pd.DataFrame([ctrl_row_nq]).to_csv(os.path.join(OUT, "leg1_control_NQ.csv"), index=False)
pd.DataFrame([ctrl_row_mnq]).to_csv(os.path.join(OUT, "leg1_control_MNQ.csv"), index=False)
top20.drop(columns=["t_idx_list"]).to_csv(os.path.join(OUT, "leg1_top20_ETH_blocks_control.csv"), index=False)
bot20.drop(columns=["t_idx_list"]).to_csv(os.path.join(OUT, "leg1_bot20_ETH_blocks_control.csv"), index=False)

print("\n" + "=" * 100 + "\nLEG 1 (Product B) GRID SUMMARY\n" + "=" * 100)
print(res_df.round(2).to_string(index=False))

json.dump({
    "control_net_NQ_canon": ctrl_row_nq["net"], "control_net_MNQ_canon": ctrl_row_mnq["net"],
    "control_sharpe_NQ": ctrl_row_nq["sharpe"], "control_maxDD_NQ": ctrl_row_nq["maxDD_eod"],
    "control_CDaR95_NQ": ctrl_row_nq["CDaR95"], "control_trades_canon": ctrl_trades,
    "control_ext_net_NQ": float(U.CTRL_BPNL_B_NQ[U.health_mask].sum()),
    "control_ext_net_MNQ": float(U.CTRL_BPNL_B_MNQ[U.health_mask].sum()),
    "n_ETH_touched_blocks_canon": int(len(eth_blocks)), "n_total_blocks_canon": int(len(block_tot)),
}, open(os.path.join(OUT, "leg1_control_summary.json"), "w"), indent=2)
print("\nLeg 1 (Product B) construction + grid battery complete.")
