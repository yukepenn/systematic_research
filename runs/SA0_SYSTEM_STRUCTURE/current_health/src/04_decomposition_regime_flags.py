"""Current-health part 2: sec6 (2026 decomposition), sec7-9 (right-tail arrival vs conditional
decay, distribution vs relationship shift), sec10 (regime analogs), sec12-13 (indicators+flags),
sec16-18 (persistence, lumpiness, short-side 2026 deep dive)."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import health_substrate as H

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
blocks = pd.read_csv(os.path.join(OUT, "extended_block_ledger.csv"))
blocks["entry_sess"] = pd.to_datetime(blocks["entry_sess"])
daily = H.daily_nq.copy()
daily["sess"] = pd.to_datetime(daily["sess"])
daily = daily.sort_values("sess").reset_index(drop=True)
daily["year"] = daily["sess"].dt.year
sys.path.insert(0, os.path.join(H.ROOT, "src", "analytics"))
from smv2_common import dd_battery

blocks["period"] = np.where(blocks["year"] <= 2025, blocks["year"].astype(str), "2026 (extended, thru Jul-31)")

# ============================================================== SEC6 -- 2026 DECOMPOSITION
print("=" * 90, "\nSEC6 -- 2026 UNDERPERFORMANCE DECOMPOSITION (2022-2025 pooled vs 2026 extended)\n", "=" * 90, sep="")
pre2026 = blocks[blocks["year"] <= 2025]
y2026 = blocks[blocks["year"] == 2026]


def decomp_row(sub, label):
    n_yr_equiv = sub["entry_sess"].dt.year.nunique() if label == "2022-2025 (per-year avg)" else 1
    win = sub[sub["net_pnl"] > 0]; loss = sub[sub["net_pnl"] <= 0]
    top5pct_cut = blocks["net_pnl"].quantile(0.95)
    n_giant = int((sub["net_pnl"] >= top5pct_cut).sum())
    return {
        "label": label, "n_blocks": len(sub),
        "win_rate": float((sub["net_pnl"] > 0).mean()),
        "avg_win": float(win["net_pnl"].mean()) if len(win) else np.nan,
        "avg_loss": float(loss["net_pnl"].mean()) if len(loss) else np.nan,
        "reversal_rate": float((sub["exit_type"] == "REVERSAL").mean()),
        "n_giant_winners_ge_p95": n_giant,
        "giant_winner_rate_pct": float(n_giant / len(sub) * 100) if len(sub) else np.nan,
        "long_pct": float((sub["side"] > 0).mean()),
        "short_side_mean_pnl": float(sub.loc[sub["side"] < 0, "net_pnl"].mean()) if (sub["side"] < 0).any() else np.nan,
        "long_side_mean_pnl": float(sub.loc[sub["side"] > 0, "net_pnl"].mean()) if (sub["side"] > 0).any() else np.nan,
    }


decomp_2225 = decomp_row(pre2026, "2022-2025 pooled")
decomp_2026 = decomp_row(y2026, "2026 (extended, thru Jul-31)")
decomp_df = pd.DataFrame([decomp_2225, decomp_2026])
print(decomp_df.round(3).to_string(index=False))
decomp_df.to_csv(os.path.join(OUT, "sec6_2026_decomposition.csv"), index=False)

# per-year-normalized giant-winner ARRIVAL RATE (per 250 sessions, since 2026 stub is partial)
sessions_by_year = daily.groupby("year")["sess"].nunique()
giant_cut = blocks["net_pnl"].quantile(0.95)
giant_by_year = blocks[blocks["net_pnl"] >= giant_cut].groupby("year").size()
arrival_rate = (giant_by_year / sessions_by_year * 250).fillna(0)
print("\ngiant-winner (>=95th pct block net_pnl) arrival rate, normalized per 250 sessions/year:")
print(arrival_rate.round(2))

# ============================================================== SEC7-9 -- RIGHT-TAIL ARRIVAL VS CONDITIONAL DECAY
print("\n" + "=" * 90, "\nSEC7-9 -- RIGHT-TAIL ARRIVAL (Hyp A) vs CONDITIONAL EDGE DECAY (Hyp B)\n", "=" * 90, sep="")
blocks["M_abs"] = blocks["entry_M"].abs()
blocks["M_strength_tercile"] = pd.qcut(blocks["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")

print("\nHyp A check: giant-winner arrival rate already shown above (2026 vs 2022-2025) -- this IS "
      "the frequency-of-rare-events test.")

print("\nHyp B check: conditional mean pnl BY M-strength tercile, BY YEAR (same state, does 2026 pay worse?):")
condB = blocks.groupby(["M_strength_tercile", "year"], observed=True)["net_pnl"].agg(["size", "mean"]).reset_index()
piv = condB.pivot(index="M_strength_tercile", columns="year", values="mean")
print(piv.round(2))
piv_n = condB.pivot(index="M_strength_tercile", columns="year", values="size")
print("\n(n per cell)")
print(piv_n)
piv.to_csv(os.path.join(OUT, "sec8_conditional_edge_by_year_Mstrength.csv"))

print("\nSEC9 -- distribution shift (P(state) by year) vs relationship shift (E[pnl|state] by year):")
state_freq = blocks.groupby(["year", "M_strength_tercile"], observed=True).size().groupby(level=0).apply(
    lambda x: x / x.sum())
print("P(M_strength_tercile | year) -- distribution of entry quality by year:")
print(state_freq.unstack().round(3))

# ============================================================== SEC10 -- HISTORICAL REGIME ANALOGS
print("\n" + "=" * 90, "\nSEC10 -- HISTORICAL REGIME ANALOGS (rolling 60-session state vector)\n", "=" * 90, sep="")
sess_list = daily["sess"].tolist()
n_sess = len(sess_list)
hm_arr = H.hm
sess_arr_bar = H.sess_arr
sig_arr = H.sig460
M_arr = H.M
B_arr = np.asarray(H.B)

sess_idx_map = {s: i for i, s in enumerate(sess_list)}
bar_sess_pos = pd.Series(sess_arr_bar).map(sess_idx_map).to_numpy()

state_vecs = []
for end in range(59, n_sess):
    start_sess_idx = end - 59
    bar_mask = (bar_sess_pos >= start_sess_idx) & (bar_sess_pos <= end)
    win_blocks = blocks[(blocks["entry_sess"] >= sess_list[start_sess_idx]) & (blocks["entry_sess"] <= sess_list[end])]
    state_vecs.append({
        "end_sess_idx": end, "end_sess": sess_list[end],
        "mean_sigma460": float(np.nanmean(sig_arr[bar_mask])),
        "mean_abs_M": float(np.nanmean(np.abs(M_arr[bar_mask]))),
        "frac_bmom_active": float((B_arr[bar_mask] != 0).mean()),
        "reversal_rate": float((win_blocks["exit_type"] == "REVERSAL").mean()) if len(win_blocks) else np.nan,
        "mean_entry_Mabs": float(win_blocks["M_abs"].mean()) if len(win_blocks) else np.nan,
    })
state_df = pd.DataFrame(state_vecs).dropna()
feat_cols = ["mean_sigma460", "mean_abs_M", "frac_bmom_active", "reversal_rate", "mean_entry_Mabs"]
Fz = (state_df[feat_cols] - state_df[feat_cols].mean()) / state_df[feat_cols].std()
target = Fz.iloc[-1].to_numpy()
dists = np.linalg.norm(Fz.to_numpy() - target, axis=1)
state_df["dist_to_current"] = dists
analogs = state_df[state_df["end_sess_idx"] < n_sess - 30].nsmallest(10, "dist_to_current")  # exclude the trivial near-overlap tail
print("10 nearest historical 60-session-window regime analogs to the CURRENT window "
      "(excluding trivially-overlapping recent windows):")
print(analogs[["end_sess", "dist_to_current"] + feat_cols].round(3).to_string(index=False))

# performance of the system in those analog windows (next-60-session forward net, where available)
analog_perf = []
for _, r in analogs.iterrows():
    idx = int(r["end_sess_idx"])
    fwd_start, fwd_end = idx + 1, min(idx + 60, n_sess - 1)
    if fwd_end > fwd_start:
        fwd_net = daily["net"].iloc[fwd_start:fwd_end + 1].sum()
        analog_perf.append(fwd_net)
if analog_perf:
    print(f"\nforward 60-session net P&L following these {len(analog_perf)} analog windows: "
          f"mean={np.mean(analog_perf):.2f} median={np.median(analog_perf):.2f} "
          f"(vs current rolling-60 net +$34,606.68, sec4)")
state_df.to_csv(os.path.join(OUT, "sec10_regime_state_vectors.csv"), index=False)
analogs.to_csv(os.path.join(OUT, "sec10_nearest_analogs.csv"), index=False)

# ============================================================== SEC16-17 -- PERSISTENCE / LUMPINESS
print("\n" + "=" * 90, "\nSEC16-17 -- PROFITABILITY PERSISTENCE / LUMPINESS\n", "=" * 90, sep="")
persist_rows = []
for w in [20, 60, 120]:
    roll = daily["net"].rolling(w).sum().dropna()
    persist_rows.append({"window": w, "pct_positive_windows": float((roll > 0).mean() * 100),
                          "median_rolling_net": float(roll.median())})
print(pd.DataFrame(persist_rows).round(2).to_string(index=False))

# top-tail contribution / waiting time between giant winners
giant_idx = blocks[blocks["net_pnl"] >= giant_cut].sort_values("entry_sess")
gap_sessions = []
prev = None
for _, r in giant_idx.iterrows():
    if prev is not None:
        gap = (r["entry_sess"] - prev).days
        gap_sessions.append(gap)
    prev = r["entry_sess"]
if gap_sessions:
    print(f"\nwaiting time (calendar days) between giant winners (>=95th pct): "
          f"mean={np.mean(gap_sessions):.1f} median={np.median(gap_sessions):.1f} "
          f"max={np.max(gap_sessions):.1f}")
last_giant = giant_idx["entry_sess"].max()
days_since_last_giant = (daily["sess"].max() - last_giant).days
print(f"days since the last giant winner (as of {daily['sess'].max().date()}): {days_since_last_giant}")

top10pct_share = blocks.nlargest(max(1, len(blocks)//10), "net_pnl")["net_pnl"].sum() / blocks["net_pnl"].sum()
print(f"top-10%-of-blocks share of total net_pnl (full extended history): {top10pct_share*100:.1f}%")

persist_summary = {
    "days_since_last_giant_winner": days_since_last_giant,
    "giant_winner_gap_days_mean": float(np.mean(gap_sessions)) if gap_sessions else None,
    "giant_winner_gap_days_max": float(np.max(gap_sessions)) if gap_sessions else None,
    "top10pct_blocks_share_of_net": float(top10pct_share),
}
json.dump(persist_summary, open(os.path.join(OUT, "sec17_persistence_summary.json"), "w"), indent=2)

# ============================================================== SEC18 -- SHORT-SIDE 2026 DEEP DIVE
print("\n" + "=" * 90, "\nSEC18 -- SHORT-SIDE 2026 DEEP DIVE\n", "=" * 90, sep="")
shorts = blocks[blocks["side"] < 0].copy()
short_by_period = shorts.groupby("period").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())),
    mean_MFE=("MFE_dollars", "mean"), mean_MAE=("MAE_dollars", "mean"),
    reversal_rate=("exit_type", lambda x: float((x == "REVERSAL").mean())),
    mean_holding_bars=("n_bars", "mean"))
print(short_by_period.round(2))
short_by_period.to_csv(os.path.join(OUT, "sec18_short_side_by_period.csv"))

# split 2026 into Jan-May (already-studied stub) vs Jun-Jul (new health-only window)
y2026_shorts = shorts[shorts["year"] == 2026].copy()
y2026_shorts["sub_period"] = np.where(y2026_shorts["entry_sess"] <= H.CANONICAL_END,
                                       "2026 Jan-May (stub)", "2026 Jun-Jul (new)")
sub2026 = y2026_shorts.groupby("sub_period").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print("\n2026 short-side, split stub (already studied) vs new Jun-Jul window:")
print(sub2026.round(2))

print("\ncurrent-health part 2 (sec6-10,16-18) complete.")
