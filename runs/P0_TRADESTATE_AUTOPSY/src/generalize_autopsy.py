"""P0 -- generalizes the April two-trade finding (T/M conviction decay + giveback, held through
a slow score decay until the coarse EXIT_LEVEL threshold finally crosses) across ALL 1,978
incumbent position-blocks in the full dev window. Percentile-bucketed, descriptive only."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "P0_TRADESTATE_AUTOPSY")
OUT = os.path.join(RUN, "out")

ledger = pd.read_parquet(os.path.join(OUT, "ledger_full.parquet"))
pos_blocks = ledger[ledger["position"] != 0].copy()

rows = []
for bid, g in pos_blocks.groupby("block_id", sort=True):
    side = int(g["position"].iloc[0])
    T_vals = g["T"].to_numpy()
    M_vals = g["M"].to_numpy()
    max_conv = float(np.abs(T_vals).max())
    exit_T = float(T_vals[-1])
    exit_M = float(M_vals[-1])
    entry_T = float(T_vals[0])
    mfe = float(g["MFE_dollars"].iloc[-1])
    net = float(g["run_pnl_dollars"].iloc[-1])
    giveback = float(g["giveback_dollars"].iloc[-1])
    giveback_ratio = giveback / mfe if mfe > 0 else np.nan
    decay_frac = 1.0 - (abs(exit_T) / max_conv) if max_conv > 0 else np.nan
    b_engaged = bool((g["B"] != 0).any())
    peak_conv_bar = int(np.argmax(np.abs(T_vals)))
    bars_from_peak_to_exit = int(len(T_vals) - 1 - peak_conv_bar)
    rows.append({
        "block_id": bid, "side": side, "n_bars": len(g),
        "entry_T": entry_T, "exit_T": exit_T, "max_conviction_T": max_conv,
        "decay_frac": decay_frac, "bars_from_peak_conviction_to_exit": bars_from_peak_to_exit,
        "MFE_dollars": mfe, "net_pnl": net, "giveback_dollars": giveback,
        "giveback_ratio": giveback_ratio, "B_engaged_during_trade": b_engaged,
        "exit_M": exit_M,
    })
tb = pd.DataFrame(rows)
tb.to_csv(os.path.join(OUT, "block_level_summary.csv"), index=False)
print(f"n position-blocks: {len(tb)}   total net: {tb['net_pnl'].sum():.2f}")

n = len(tb)
tb_sorted = tb.sort_values("net_pnl")
def bucket(frac_from_bottom=None, frac_from_top=None):
    k = max(1, int(round(n * (frac_from_bottom or frac_from_top))))
    return tb_sorted.iloc[:k] if frac_from_bottom else tb_sorted.iloc[-k:]

buckets = {
    "bottom_1pct_losers": bucket(frac_from_bottom=0.01),
    "bottom_5pct_losers": bucket(frac_from_bottom=0.05),
    "bottom_10pct_losers": bucket(frac_from_bottom=0.10),
    "top_1pct_winners": bucket(frac_from_top=0.01),
    "top_5pct_winners": bucket(frac_from_top=0.05),
    "top_10pct_winners": bucket(frac_from_top=0.10),
    "all_losers": tb[tb["net_pnl"] <= 0],
    "all_winners": tb[tb["net_pnl"] > 0],
    "ordinary": tb_sorted.iloc[int(0.10 * n):int(0.90 * n)],
}

summary_rows = []
for name, b in buckets.items():
    summary_rows.append({
        "bucket": name, "n": len(b),
        "net_pnl_mean": float(b["net_pnl"].mean()),
        "net_pnl_sum": float(b["net_pnl"].sum()),
        "giveback_ratio_mean": float(b["giveback_ratio"].mean(skipna=True)),
        "giveback_ratio_median": float(b["giveback_ratio"].median(skipna=True)),
        "pct_with_giveback_ratio_gt_1": float((b["giveback_ratio"] > 1.0).mean(skipna=True) * 100),
        "decay_frac_mean": float(b["decay_frac"].mean(skipna=True)),
        "decay_frac_median": float(b["decay_frac"].median(skipna=True)),
        "pct_decay_frac_gt_0.5": float((b["decay_frac"] > 0.5).mean(skipna=True) * 100),
        "n_bars_mean": float(b["n_bars"].mean()),
        "n_bars_median": float(b["n_bars"].median()),
        "max_conviction_T_mean": float(b["max_conviction_T"].mean()),
        "pct_B_engaged": float(b["B_engaged_during_trade"].mean() * 100),
    })
summary = pd.DataFrame(summary_rows)
summary.to_csv(os.path.join(OUT, "bucket_summary.csv"), index=False)
print(summary.to_string(index=False))

# specific test: among losers, does giveback_ratio correlate with size of loss (rank correlation)?
losers = tb[tb["net_pnl"] < 0].dropna(subset=["giveback_ratio"])
winners = tb[tb["net_pnl"] > 0].dropna(subset=["giveback_ratio"])
corr_loss_giveback = float(losers["net_pnl"].corr(losers["giveback_ratio"], method="spearman"))
corr_loss_decay = float(losers["net_pnl"].corr(losers["decay_frac"], method="spearman"))
diagnostics = {
    "spearman_corr_loser_netpnl_vs_giveback_ratio": corr_loss_giveback,
    "spearman_corr_loser_netpnl_vs_decay_frac": corr_loss_decay,
    "note": "negative correlation means MORE negative net_pnl (bigger loss) associates with HIGHER giveback_ratio/decay_frac -- consistent with the April mechanism if negative and material.",
    "pct_all_trades_B_engaged": float(tb["B_engaged_during_trade"].mean() * 100),
    "pct_top10pct_winners_giveback_ratio_lt_0.2": float((buckets["top_10pct_winners"]["giveback_ratio"].dropna() < 0.2).mean() * 100),
    "pct_bottom10pct_losers_giveback_ratio_gt_1.0": float((buckets["bottom_10pct_losers"]["giveback_ratio"].dropna() > 1.0).mean() * 100),
}
print(json.dumps(diagnostics, indent=2))
json.dump(diagnostics, open(os.path.join(OUT, "generalization_diagnostics.json"), "w"), indent=2)
