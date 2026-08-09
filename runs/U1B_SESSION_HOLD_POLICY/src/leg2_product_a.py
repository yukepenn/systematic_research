"""U1B Leg 2 -- Product A session-conditioned HOLD exposure scale-down. Grid: multiplier in
{0.85, 0.70}. Full validation battery: canonical full-history, 2022-2025-only delta, year-by-
year, LOYO(drop 2026), right-tail check on ETH-touched blocks, turnover/cost check, June-July-
2026 extension reported separately."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import u1b_substrate as U

OUT = U.OUT
ROOT = U.ROOT

# ================================================================== control (baseline)
ctrl_daily, _, ctrl_bpnl = U.product_a_exec_eth_scale(1.0)
assert np.allclose(ctrl_bpnl, U.CTRL_BPNL_A, atol=1e-6)
ctrl_daily_canon = ctrl_daily[pd.to_datetime(ctrl_daily["sess"]) <= U.CANONICAL_END].reset_index(drop=True)
ctrl_row = U.battery_row("CONTROL_A", ctrl_daily_canon)
ctrl_trades = U.trade_volume(U.CTRL_POS_A[U.canon_mask])
print(f"[leg2] CONTROL canonical: A net={ctrl_row['net']:.2f} sharpe={ctrl_row['sharpe']:.4f} "
      f"maxDD={ctrl_row['maxDD_eod']:.2f} CDaR95={ctrl_row['CDaR95']:.2f}  trades={ctrl_trades}", flush=True)
print(f"[leg2] CONTROL extension (Jun-Jul-2026, observational): A={U.CTRL_BPNL_A[U.health_mask].sum():.2f}", flush=True)

# ================================================================== block population (from U0's table, cross-checked)
u0_path = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
u0 = pd.read_parquet(u0_path, columns=["t_idx", "is_health_only_bar", "is_rth", "target_exposure_A",
                                        "block_id_A", "bar_pnl_A_dollars"])
assert len(u0) == U.n, "U0 table row count mismatch vs u1b_substrate"
assert np.array_equal(u0["target_exposure_A"].to_numpy(), U.CTRL_POS_A), "U0 target_exposure_A diverges from U1B CONTROL pos -- construction mismatch"
assert np.allclose(u0["bar_pnl_A_dollars"].to_numpy(), U.CTRL_BPNL_A, atol=1e-6), "U0 bar_pnl_A_dollars diverges from U1B CONTROL bpnl -- construction mismatch"
print("[leg2] cross-check vs U0 unified state table: target_exposure_A and bar_pnl_A_dollars match EXACTLY", flush=True)

u0_canon = u0[~u0["is_health_only_bar"]].copy()
block_tot = u0_canon.groupby("block_id_A").agg(
    net=("bar_pnl_A_dollars", "sum"),
    n_bars=("bar_pnl_A_dollars", "size"),
    sgn=("target_exposure_A", lambda s: int(np.sign(s.iloc[0]))),
    eth_touched=("is_rth", lambda s: bool((~s).any())),
).reset_index()
t_idx_map = {bid: g["t_idx"].to_numpy() for bid, g in u0_canon.groupby("block_id_A")}
block_tot["t_idx_list"] = block_tot["block_id_A"].map(t_idx_map)
block_tot = block_tot[block_tot["sgn"] != 0]
eth_blocks = block_tot[block_tot["eth_touched"]].sort_values("net")
print(f"[leg2] canonical blocks: {len(block_tot)} total, {len(eth_blocks)} ETH-touched "
      f"({len(eth_blocks) / len(block_tot):.1%})", flush=True)

top20 = eth_blocks.nlargest(20, "net")
bot20 = eth_blocks.nsmallest(20, "net")

# ================================================================== grid
GRID = [0.85, 0.70]
results = []
for mult in GRID:
    tag = f"A_mult{mult}"
    daily, barpos, bpnl = U.product_a_exec_eth_scale(mult)
    daily_canon = daily[pd.to_datetime(daily["sess"]) <= U.CANONICAL_END].reset_index(drop=True)
    row = U.battery_row(f"{tag}", daily_canon)

    yrs = pd.to_datetime(daily_canon["sess"]).dt.year
    yrs_ctrl = pd.to_datetime(ctrl_daily_canon["sess"]).dt.year
    pre2026_ctrl = ctrl_daily_canon.loc[yrs_ctrl <= 2025, "net"].sum()
    pre2026_cand = daily_canon.loc[yrs <= 2025, "net"].sum()
    delta_pre2026 = pre2026_cand - pre2026_ctrl
    loyo_ctrl = ctrl_daily_canon.loc[yrs_ctrl != 2026, "net"].sum()
    loyo_cand = daily_canon.loc[yrs != 2026, "net"].sum()
    full_delta = row["net"] - ctrl_row["net"]

    yby = []
    for yr in sorted(yrs.unique()):
        c_net = ctrl_daily_canon.loc[yrs_ctrl == yr, "net"].sum()
        v_net = daily_canon.loc[yrs == yr, "net"].sum()
        yby.append({"year": int(yr), "control_net_A": c_net, "candidate_net_A": v_net, "delta_A": v_net - c_net})
    yby_df = pd.DataFrame(yby)
    n_pos_years = int((yby_df["delta_A"] > 0).sum())

    ext_ctrl = U.CTRL_BPNL_A[U.health_mask].sum()
    ext_cand = bpnl[U.health_mask].sum()

    cand_trades = U.trade_volume(barpos[U.canon_mask])
    extra_trades = cand_trades - ctrl_trades
    extra_commission = extra_trades * U.COMM_MNQ_A

    def block_window_pnl(t_idx_list, bpnl_arr):
        return float(bpnl_arr[t_idx_list].sum())

    top20_rows = []
    for _, r in top20.iterrows():
        cand_pnl = block_window_pnl(r["t_idx_list"], bpnl)
        top20_rows.append({"block_id_A": r["block_id_A"], "control_net": r["net"], "candidate_window_net": cand_pnl,
                            "delta": cand_pnl - r["net"]})
    top20_df = pd.DataFrame(top20_rows)
    n_top20_damaged = int((top20_df["delta"] < -1e-6).sum())
    n_top20_flipped_negative = int(((top20_df["control_net"] > 0) & (top20_df["candidate_window_net"] < 0)).sum())

    bot20_rows = []
    for _, r in bot20.iterrows():
        cand_pnl = block_window_pnl(r["t_idx_list"], bpnl)
        bot20_rows.append({"block_id_A": r["block_id_A"], "control_net": r["net"], "candidate_window_net": cand_pnl,
                            "delta": cand_pnl - r["net"]})
    bot20_df = pd.DataFrame(bot20_rows)
    n_bot20_improved = int((bot20_df["delta"] > 1e-6).sum())
    n_bot20_damaged = int((bot20_df["delta"] < -1e-6).sum())

    results.append({
        "tag": tag, "multiplier": mult,
        "net_A": row["net"], "sharpe_A": row["sharpe"], "sortino_A": row["sortino"], "calmar_A": row["calmar"],
        "maxDD_eod_A": row["maxDD_eod"], "CDaR95_A": row["CDaR95"], "worst_day_A": row["worst_day"],
        "worst_month_A": row["worst_month"], "pos_day_pct_A": row["pos_day_pct"],
        "full_delta_A": full_delta, "delta_pre2026_A": delta_pre2026, "loyo_delta_A": loyo_cand - loyo_ctrl,
        "n_pos_years_of_5": n_pos_years, "ext_delta_A": ext_cand - ext_ctrl,
        "ctrl_trades": ctrl_trades, "cand_trades": cand_trades, "extra_trades": extra_trades,
        "extra_commission_A": extra_commission,
        "n_top20_ETH_blocks_damaged": n_top20_damaged, "n_top20_ETH_blocks_flipped_negative": n_top20_flipped_negative,
        "n_bot20_ETH_blocks_improved": n_bot20_improved, "n_bot20_ETH_blocks_damaged": n_bot20_damaged,
        "top20_total_delta": float(top20_df["delta"].sum()), "bot20_total_delta": float(bot20_df["delta"].sum()),
    })
    yby_df.to_csv(os.path.join(OUT, f"leg2_{tag}_year_by_year.csv"), index=False)
    daily_canon.to_csv(os.path.join(OUT, f"leg2_{tag}_daily_A_canonical.csv"), index=False)
    top20_df.to_csv(os.path.join(OUT, f"leg2_{tag}_top20_ETH_blocks.csv"), index=False)
    bot20_df.to_csv(os.path.join(OUT, f"leg2_{tag}_bot20_ETH_blocks.csv"), index=False)
    print(f"[leg2] {tag}: A net={row['net']:.2f} (ctrl {ctrl_row['net']:.2f}, delta={full_delta:+.2f}), "
          f"pre2026 delta={delta_pre2026:+.2f}, LOYO delta={loyo_cand - loyo_ctrl:+.2f}, "
          f"pos_years={n_pos_years}/5, maxDD={row['maxDD_eod']:.2f} (ctrl {ctrl_row['maxDD_eod']:.2f}), "
          f"CDaR95={row['CDaR95']:.2f} (ctrl {ctrl_row['CDaR95']:.2f}), "
          f"extra_trades={extra_trades} (extra comm=${extra_commission:.2f}), "
          f"top20_ETH_damaged={n_top20_damaged}/20 (sum delta ${top20_df['delta'].sum():+.2f}), "
          f"bot20_ETH_improved={n_bot20_improved}/20 damaged={n_bot20_damaged}/20 (sum delta ${bot20_df['delta'].sum():+.2f}), "
          f"ext_delta_A={ext_cand - ext_ctrl:+.2f}", flush=True)

res_df = pd.DataFrame(results)
res_df.to_csv(os.path.join(OUT, "leg2_grid_results.csv"), index=False)
pd.DataFrame([ctrl_row]).to_csv(os.path.join(OUT, "leg2_control_A.csv"), index=False)
top20.drop(columns=["t_idx_list"]).to_csv(os.path.join(OUT, "leg2_top20_ETH_blocks_control.csv"), index=False)
bot20.drop(columns=["t_idx_list"]).to_csv(os.path.join(OUT, "leg2_bot20_ETH_blocks_control.csv"), index=False)

print("\n" + "=" * 100 + "\nLEG 2 (Product A) GRID SUMMARY\n" + "=" * 100)
print(res_df.round(2).to_string(index=False))

json.dump({
    "control_net_A_canon": ctrl_row["net"], "control_sharpe_A": ctrl_row["sharpe"],
    "control_maxDD_A": ctrl_row["maxDD_eod"], "control_CDaR95_A": ctrl_row["CDaR95"],
    "control_trades_canon": ctrl_trades, "control_ext_net_A": float(U.CTRL_BPNL_A[U.health_mask].sum()),
    "n_ETH_touched_blocks_canon": int(len(eth_blocks)), "n_total_blocks_canon": int(len(block_tot)),
}, open(os.path.join(OUT, "leg2_control_summary.json"), "w"), indent=2)
print("\nLeg 2 (Product A) construction + grid battery complete.")
