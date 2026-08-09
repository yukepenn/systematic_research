"""SA0 sec5 (structural ablation) + sec10 (score-mixing local sensitivity) + sec11 (hysteresis
science). Bounded, semantically-clean ablation set only -- no arbitrary combinations, no
optimization. All ablations priced on BOTH NQ and MNQ genuine economics via the verified
substrate. Everything here is explanatory: no candidate is constructed or promoted."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def trade_count(pos_seq):
    return int((np.diff(pos_seq) != 0).sum())


def long_short_split(bar_pos, bar_pnl):
    long_pnl = float(bar_pnl[bar_pos > 0].sum())
    short_pnl = float(bar_pnl[bar_pos < 0].sum())
    return long_pnl, short_pnl


def year_by_year(bar_pnl):
    df = pd.DataFrame({"year": S.year_arr, "pnl": bar_pnl})
    return df.groupby("year")["pnl"].sum().to_dict()


def top_bottom_day_retention(daily_ctrl, daily_arm, k_days=20):
    m = daily_ctrl.merge(daily_arm, on="sess", suffixes=("_ctrl", "_arm"))
    top_ctrl = m.nlargest(k_days, "net_ctrl")
    bot_ctrl = m.nsmallest(k_days, "net_ctrl")
    return {
        f"top{k_days}day_ctrl_sum": float(top_ctrl["net_ctrl"].sum()),
        f"top{k_days}day_arm_sum_same_days": float(top_ctrl["net_arm"].sum()),
        f"top{k_days}day_retention_pct": float(100 * top_ctrl["net_arm"].sum() / top_ctrl["net_ctrl"].sum()) if top_ctrl["net_ctrl"].sum() else None,
        f"bottom{k_days}day_ctrl_sum": float(bot_ctrl["net_ctrl"].sum()),
        f"bottom{k_days}day_arm_sum_same_days": float(bot_ctrl["net_arm"].sum()),
    }


def losing_day_corr(daily_ctrl, daily_arm):
    m = daily_ctrl.merge(daily_arm, on="sess", suffixes=("_ctrl", "_arm"))
    return float(np.corrcoef(m["net_ctrl"], m["net_arm"])[0, 1])


def run_arm(tag, M_arr, entry_level, exit_level, entry_blocked=None, forced_flat=None):
    pos_seq = S.build_pos_seq(M_arr, entry_level, exit_level, entry_blocked, forced_flat)
    daily_nq, barpos_nq, bpnl_nq = S.onelot_exec(pos_seq, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
    daily_mnq, barpos_mnq, bpnl_mnq = S.onelot_exec(pos_seq, S.COMM_MNQ, S.PV_MNQ, S.o_mnq, S.h_mnq, S.l_mnq, S.c_mnq)
    row_nq = S.battery_row(tag + "_NQ", daily_nq)
    row_mnq = S.battery_row(tag + "_MNQ", daily_mnq)
    row_nq["n_trades"] = row_mnq["n_trades"] = trade_count(pos_seq)
    long_pnl_nq, short_pnl_nq = long_short_split(barpos_nq, bpnl_nq)
    row_nq["long_pnl"], row_nq["short_pnl"] = long_pnl_nq, short_pnl_nq
    long_pnl_mnq, short_pnl_mnq = long_short_split(barpos_mnq, bpnl_mnq)
    row_mnq["long_pnl"], row_mnq["short_pnl"] = long_pnl_mnq, short_pnl_mnq
    return {
        "tag": tag, "pos_seq": pos_seq,
        "row_nq": row_nq, "row_mnq": row_mnq,
        "daily_nq": daily_nq, "daily_mnq": daily_mnq,
        "yby_nq": year_by_year(bpnl_nq), "yby_mnq": year_by_year(bpnl_mnq),
    }


print("=" * 90, "\nSEC5 -- STRUCTURAL ABLATION\n", "=" * 90, sep="")

# Tp with HTF tilt forced off (m=1.0 always) -- used by the NO_HTF_TILT ablation
Tp_notilt = np.clip(S.rha(S.T * S.TILTRESCALE), -13, 13)
M_notilt = S.WSOLAR * Tp_notilt + S.WBMOM * np.asarray(S.B)

ARMS = {
    "FULL": dict(M_arr=S.M, entry_level=S.ENTRY_LEVEL, exit_level=S.EXIT_LEVEL),
    "SOLAR_ONLY": dict(M_arr=S.WSOLAR * S.Tp, entry_level=S.ENTRY_LEVEL, exit_level=S.EXIT_LEVEL),
    "BMOM_ONLY": dict(M_arr=S.WBMOM * np.asarray(S.B), entry_level=S.ENTRY_LEVEL, exit_level=S.EXIT_LEVEL),
    "NO_HTF_TILT": dict(M_arr=M_notilt, entry_level=S.ENTRY_LEVEL, exit_level=S.EXIT_LEVEL),
    "NO_HYSTERESIS_GAP": dict(M_arr=S.M, entry_level=S.ENTRY_LEVEL, exit_level=S.ENTRY_LEVEL),
}

results = {}
for tag, cfg in ARMS.items():
    print(f"  running {tag} ...", flush=True)
    results[tag] = run_arm(tag, **cfg)
    r = results[tag]["row_nq"]
    print(f"    NQ net={r['net']:.2f} sharpe={r['sharpe']:.3f} maxDD={r['maxDD_eod']:.2f} "
          f"CDaR95={r['CDaR95']:.2f} n_trades={r['n_trades']} long={r['long_pnl']:.2f} short={r['short_pnl']:.2f}",
          flush=True)

leaderboard_rows = []
for tag, res in results.items():
    row_nq = dict(res["row_nq"]); row_nq["instrument"] = "NQ"
    row_mnq = dict(res["row_mnq"]); row_mnq["instrument"] = "MNQ"
    leaderboard_rows += [row_nq, row_mnq]
pd.DataFrame(leaderboard_rows).to_csv(os.path.join(OUT, "sec5_ablation_leaderboard.csv"), index=False)

# right-tail retention + losing-day correlation, each ablation vs FULL
tail_rows = {}
ctrl_daily_nq = results["FULL"]["daily_nq"]
for tag, res in results.items():
    if tag == "FULL":
        continue
    ret = top_bottom_day_retention(ctrl_daily_nq, res["daily_nq"])
    ret["losing_day_corr_vs_FULL"] = losing_day_corr(ctrl_daily_nq, res["daily_nq"])
    tail_rows[tag] = ret
json.dump(tail_rows, open(os.path.join(OUT, "sec5_ablation_tail_and_corr.json"), "w"), indent=2, default=str)

yby_rows = []
for tag, res in results.items():
    for yr, v in res["yby_nq"].items():
        yby_rows.append({"tag": tag, "year": yr, "net_NQ": v})
pd.DataFrame(yby_rows).pivot(index="year", columns="tag", values="net_NQ").to_csv(
    os.path.join(OUT, "sec5_ablation_year_by_year_NQ.csv"))

print("saved sec5_ablation_leaderboard.csv, sec5_ablation_tail_and_corr.json, sec5_ablation_year_by_year_NQ.csv")

print("\n" + "=" * 90, "\nSEC10 -- SCORE-MIXING LOCAL STRUCTURAL SENSITIVITY (tiny neighborhood, no search)\n", "=" * 90, sep="")

sens_rows = []
base_pos = results["FULL"]["pos_seq"]
for leg, base_w in [("WSOLAR", S.WSOLAR), ("WBMOM", S.WBMOM)]:
    for mult in [0.85, 0.90, 1.00, 1.10, 1.15]:
        if leg == "WSOLAR":
            M_pert = (base_w * mult) * S.Tp + S.WBMOM * np.asarray(S.B)
        else:
            M_pert = S.WSOLAR * S.Tp + (base_w * mult) * np.asarray(S.B)
        pos_pert = S.build_pos_seq(M_pert, S.ENTRY_LEVEL, S.EXIT_LEVEL)
        daily_nq, barpos_nq, bpnl_nq = S.onelot_exec(pos_pert, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
        row = S.battery_row(f"{leg}_x{mult}", daily_nq)
        flip_rate = float((pos_pert != base_pos).mean()) * 100
        row.update({"leg": leg, "mult": mult, "bar_decision_flip_pct": flip_rate})
        sens_rows.append(row)
        print(f"  {leg} x{mult:.2f}: net={row['net']:.2f} sharpe={row['sharpe']:.3f} "
              f"flip%={flip_rate:.3f}", flush=True)
pd.DataFrame(sens_rows).to_csv(os.path.join(OUT, "sec10_score_mixing_sensitivity.csv"), index=False)
print("saved sec10_score_mixing_sensitivity.csv")

print("\n" + "=" * 90, "\nSEC11 -- HYSTERESIS SCIENCE (FULL vs NO_HYSTERESIS_GAP contrast)\n", "=" * 90, sep="")

pos_full = results["FULL"]["pos_seq"]
pos_nogap = results["NO_HYSTERESIS_GAP"]["pos_seq"]
n_trades_full = trade_count(pos_full)
n_trades_nogap = trade_count(pos_nogap)
net_full = results["FULL"]["row_nq"]["net"]
net_nogap = results["NO_HYSTERESIS_GAP"]["row_nq"]["net"]
comm_saved = (n_trades_nogap - n_trades_full) * S.COMM_NQ  # NQ per-side commission, both legs of an extra rt roughly captured by trade_count already counting each flip

# per-bar disagreement: bars where the two policies hold different positions
disagree = pos_full != pos_nogap
hyst_summary = {
    "n_trades_FULL_3_1": n_trades_full,
    "n_trades_NOGAP_3_3": n_trades_nogap,
    "trades_prevented_by_gap": n_trades_nogap - n_trades_full,
    "net_FULL_3_1_NQ": net_full,
    "net_NOGAP_3_3_NQ": net_nogap,
    "net_delta_NQ_gap_minus_nogap": net_full - net_nogap,
    "pct_bars_position_differs": float(disagree.mean() * 100),
    "est_commission_saved_by_gap_NQ": comm_saved,
}
json.dump(hyst_summary, open(os.path.join(OUT, "sec11_hysteresis_summary.json"), "w"), indent=2)
print(json.dumps(hyst_summary, indent=2))

# explicit April-2026 connection: what does the no-gap policy do across the two flagged blocks'
# time spans (P0 REPORT.md block 3743 / 3757)?
ledger = pd.read_parquet(S.LEDGER_PATH)
april_windows = []
for bid in [3743, 3757]:
    rows = ledger[ledger["block_id"] == bid]
    if len(rows) == 0:
        continue
    idx = rows["t_idx"].to_numpy()
    april_windows.append({
        "block_id": int(bid),
        "incumbent_net_pnl": float(rows["bar_pnl_dollars"].sum()),
        "incumbent_side": int(rows["position"].iloc[0]),
        "n_bars_incumbent": len(rows),
        "nogap_net_pnl_same_span": float(results["NO_HYSTERESIS_GAP"]["daily_nq"]["net"].sum()) if False else None,
    })
    # nogap P&L restricted to the same bar indices (approximate span attribution, disclosed)
    bpnl_nogap_full = S.onelot_exec(pos_nogap, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)[2]
    april_windows[-1]["nogap_net_pnl_same_span"] = float(bpnl_nogap_full[idx].sum())
json.dump(april_windows, open(os.path.join(OUT, "sec11_april_hysteresis_check.json"), "w"), indent=2)
print(json.dumps(april_windows, indent=2))

print("\nSA0 sec5/sec10/sec11 complete.")
