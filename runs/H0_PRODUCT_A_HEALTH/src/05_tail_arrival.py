"""H0 sec8 -- tail-arrival: top-10/top-20 day contribution to total net, giant-winner block
(trip) frequency, with historical-percentile context (is the CURRENT regime tail-rich or tail-poor
vs history?). Mirrors SA0 current_health sec16-17 (persistence/lumpiness) applied to Product A."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
daily = pd.read_csv(os.path.join(OUT, "daily_pnl_A_enriched.csv"), parse_dates=["sess"])
trips = pd.read_csv(os.path.join(OUT, "trip_ledger_A.csv"), parse_dates=["entry_sess", "exit_sess"])

# ============================================================== TOP-10/20-DAY CONTRIBUTION
print("=" * 90, "\nSEC8a -- TOP-10 / TOP-20 DAY CONTRIBUTION TO TOTAL NET (full history)\n", "=" * 90, sep="")
total_net = float(daily["net"].sum())
top10 = daily.nlargest(10, "net")["net"].sum()
top20 = daily.nlargest(20, "net")["net"].sum()
bottom10 = daily.nsmallest(10, "net")["net"].sum()
print(f"total net (full history) = {total_net:.2f}")
print(f"top-10-day sum = {top10:.2f}  ({100*top10/total_net:.1f}% of total net)")
print(f"top-20-day sum = {top20:.2f}  ({100*top20/total_net:.1f}% of total net)")
print(f"bottom-10-day sum = {bottom10:.2f}  ({100*bottom10/total_net:.1f}% of total net)")

# same, restricted to canonical vs health-only-extension separately
for label, sub in [("canonical", daily[~daily["is_health_only"]]), ("health-only ext", daily[daily["is_health_only"]])]:
    tn = float(sub["net"].sum())
    t10 = sub.nlargest(min(10, len(sub)), "net")["net"].sum()
    print(f"[{label}] total={tn:.2f}  top-10-day sum={t10:.2f} ({100*t10/tn:.1f}%)  n_sessions={len(sub)}")

tail_summary = {"total_net": total_net, "top10_day_sum": float(top10), "top10_day_pct": float(100 * top10 / total_net),
                 "top20_day_sum": float(top20), "top20_day_pct": float(100 * top20 / total_net),
                 "bottom10_day_sum": float(bottom10), "bottom10_day_pct": float(100 * bottom10 / total_net)}

# ============================================================== GIANT-WINNER (TRIP/BLOCK) ARRIVAL RATE
print("\n" + "=" * 90, "\nSEC8b -- GIANT-WINNER (TRIP) ARRIVAL RATE BY YEAR\n", "=" * 90, sep="")
giant_cut = trips["net_pnl"].quantile(0.95)
print(f"giant-winner cutoff (95th pct of ALL trip net_pnl, full history): {giant_cut:.2f}")
sessions_by_year = daily.groupby("year")["sess"].nunique()
giant_by_year = trips[trips["net_pnl"] >= giant_cut].groupby("year").size()
arrival_rate = (giant_by_year / sessions_by_year * 250).fillna(0)
print(arrival_rate.round(2))

last_giant = trips.loc[trips["net_pnl"] >= giant_cut, "exit_sess"].max()
days_since_last_giant = (daily["sess"].max() - last_giant).days
print(f"\nlast giant-winner trip exited: {last_giant.date()}  "
      f"({days_since_last_giant} calendar days before latest available session)")

giant_idx = trips[trips["net_pnl"] >= giant_cut].sort_values("entry_sess")
gaps = (giant_idx["entry_sess"].diff().dt.days).dropna().to_numpy()
print(f"waiting time (calendar days) between giant-winner trips: mean={gaps.mean():.1f} "
      f"median={np.median(gaps):.1f} max={gaps.max():.1f}")

top10pct_n = max(1, len(trips) // 10)
top10pct_share = trips.nlargest(top10pct_n, "net_pnl")["net_pnl"].sum() / trips["net_pnl"].sum()
print(f"\ntop-10%-of-trips share of total trip net_pnl (full history, n={top10pct_n}/{len(trips)}): "
      f"{top10pct_share*100:.1f}%")

# ============================================================== HISTORICAL-PERCENTILE CONTEXT: is CURRENT tail-rich or tail-poor?
print("\n" + "=" * 90, "\nSEC8c -- HISTORICAL-PERCENTILE CONTEXT: is the CURRENT regime tail-rich or tail-poor?\n",
      "=" * 90, sep="")


def rolling_tail_share(w):
    """for every rolling-w-session window ending at each session, what fraction of that window's
    net P&L came from its own top-10% best trips (entered within that window)?"""
    trips_sorted = trips.sort_values("entry_sess")
    sess_list = daily["sess"].tolist()
    sess_idx = {s: i for i, s in enumerate(sess_list)}
    trips_sorted = trips_sorted.assign(entry_idx=trips_sorted["entry_sess"].map(sess_idx))
    shares = []
    for end in range(w - 1, len(sess_list)):
        start = end - w + 1
        sub = trips_sorted[(trips_sorted["entry_idx"] >= start) & (trips_sorted["entry_idx"] <= end)]
        if len(sub) < 10:
            shares.append(np.nan); continue
        k = max(1, len(sub) // 10)
        tot = sub["net_pnl"].sum()
        shares.append(sub.nlargest(k, "net_pnl")["net_pnl"].sum() / tot if tot != 0 else np.nan)
    return pd.Series(shares, index=sess_list[w - 1:])


for w in (60, 120):
    s = rolling_tail_share(w)
    cur = s.iloc[-1]
    valid = s.dropna()
    pct = float((valid <= cur).mean() * 100) if len(valid) else np.nan
    print(f"rolling-{w} top-10%-of-trips share of window net: current={cur:.3f} ({cur*100:.1f}%) "
          f"-> {pct:.1f}th percentile of all historical rolling-{w} readings "
          f"(HIGHER percentile = MORE tail-dependent / tail-richer than usual)")
    tail_summary[f"rolling{w}_tail_share_current"] = float(cur)
    tail_summary[f"rolling{w}_tail_share_percentile"] = pct

giant_summary = {
    "giant_cut_95pct": float(giant_cut), "days_since_last_giant": int(days_since_last_giant),
    "giant_gap_mean_days": float(gaps.mean()) if len(gaps) else None,
    "giant_gap_median_days": float(np.median(gaps)) if len(gaps) else None,
    "giant_gap_max_days": float(gaps.max()) if len(gaps) else None,
    "top10pct_trips_share_of_net": float(top10pct_share),
    "arrival_rate_by_year": arrival_rate.round(2).to_dict(),
}
tail_summary.update(giant_summary)
json.dump(tail_summary, open(os.path.join(OUT, "sec8_tail_arrival_summary.json"), "w"), indent=2)
arrival_rate.to_csv(os.path.join(OUT, "sec8_giant_arrival_by_year.csv"))
print("\n[H0] sec8 tail-arrival analysis complete.")
