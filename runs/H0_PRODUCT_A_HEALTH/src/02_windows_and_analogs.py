"""H0 sec2 -- the 7-row window summary table (FULL-HISTORY / PRE-2026 / 2026-YTD / LATEST-20/60/120
/ ANALOGS), using the SAME dd_battery metric function Product B's panel used. sec2b -- historical
regime-analog identification (mirrors SA0 current-health sec10 exactly, Product-A-flavored trip
features) + pooled forward-60-session Product-A performance following those analogs -> feeds the
ANALOGS row. sec3 -- monthly + quarterly 2026 net P&L table."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
daily = pd.read_csv(os.path.join(OUT, "daily_pnl_A.csv"), parse_dates=["sess"])
trips = pd.read_csv(os.path.join(OUT, "trip_ledger_A.csv"), parse_dates=["entry_sess", "exit_sess"])
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "sess_date", "sigma460_atr_proxy_pts", "M", "B", "year",
                               "is_health_only_bar"])

CANONICAL_END = pd.Timestamp("2026-05-31")

# ============================================================== SEC2b -- REGIME ANALOGS (feeds ANALOGS row)
print("=" * 90, "\nSEC2b -- HISTORICAL REGIME ANALOGS (rolling 60-session state vector, Product-A-flavored)\n",
      "=" * 90, sep="")

sess_list = daily["sess"].tolist()
n_sess = len(sess_list)
sess_idx_map = {s: i for i, s in enumerate(sess_list)}

# per-session bar-level aggregates (sum + count -> exact bar-weighted mean under rolling sums)
u0["sess_date_dt"] = pd.to_datetime(u0["sess_date"])
bar_sess_pos = u0["sess_date_dt"].map(sess_idx_map).to_numpy()
sess_agg = u0.groupby("sess_date_dt", sort=True).agg(
    sum_sigma=("sigma460_atr_proxy_pts", lambda x: np.nansum(x)),
    cnt_sigma=("sigma460_atr_proxy_pts", lambda x: np.sum(~np.isnan(x))),
    sum_absM=("M", lambda x: np.nansum(np.abs(x))),
    cnt_absM=("M", lambda x: np.sum(~np.isnan(x))),
    n_bmom_active=("B", lambda x: np.sum(x != 0)),
    n_bars=("B", "size"),
).reindex(sess_list).fillna(0.0)

# per-session trip aggregates (Product-A-flavored: FLIP rate, mean |entry M_A_raw|)
trips["entry_sess_dt"] = pd.to_datetime(trips["entry_sess"])
trip_agg = trips.groupby("entry_sess_dt").agg(
    n_trips=("net_pnl", "size"),
    n_flip=("exit_type", lambda x: 0),  # placeholder, flip is about how a trip ENDS not starts; see below
    sum_entry_Mabs=("entry_M_A_raw", lambda x: np.nansum(np.abs(x))),
).reindex(sess_list).fillna(0.0)
# reversal/flip rate is a property of how a trip EXITS -- attribute it to the session in which the
# trip EXITED (matches SA0's own semantics: "reversal_rate" of blocks entered in the window, but
# exit_type is only known at exit; use exit_sess for the flip flag to keep it well-defined per bar)
trips["exit_sess_dt"] = pd.to_datetime(trips["exit_sess"])
flip_agg = trips.groupby("exit_sess_dt").agg(
    n_exits=("net_pnl", "size"), n_flip_exits=("exit_type", lambda x: (x == "FLIP_REVERSAL").sum())
).reindex(sess_list).fillna(0.0)

roll_W = 60
sum_sigma_r = sess_agg["sum_sigma"].rolling(roll_W).sum()
cnt_sigma_r = sess_agg["cnt_sigma"].rolling(roll_W).sum()
sum_absM_r = sess_agg["sum_absM"].rolling(roll_W).sum()
cnt_absM_r = sess_agg["cnt_absM"].rolling(roll_W).sum()
n_bmom_r = sess_agg["n_bmom_active"].rolling(roll_W).sum()
n_bars_r = sess_agg["n_bars"].rolling(roll_W).sum()
n_trips_r = trip_agg["n_trips"].rolling(roll_W).sum()
sum_entryM_r = trip_agg["sum_entry_Mabs"].rolling(roll_W).sum()
n_exits_r = flip_agg["n_exits"].rolling(roll_W).sum()
n_flip_r = flip_agg["n_flip_exits"].rolling(roll_W).sum()

state_df = pd.DataFrame({
    "end_sess_idx": np.arange(n_sess), "end_sess": sess_list,
    "mean_sigma460": sum_sigma_r / cnt_sigma_r.replace(0, np.nan),
    "mean_abs_M": sum_absM_r / cnt_absM_r.replace(0, np.nan),
    "frac_bmom_active": n_bmom_r / n_bars_r.replace(0, np.nan),
    "flip_rate_A": (n_flip_r / n_exits_r.replace(0, np.nan)),
    "mean_entry_Mabs_A": sum_entryM_r / n_trips_r.replace(0, np.nan),
}).dropna().reset_index(drop=True)

feat_cols = ["mean_sigma460", "mean_abs_M", "frac_bmom_active", "flip_rate_A", "mean_entry_Mabs_A"]
Fz = (state_df[feat_cols] - state_df[feat_cols].mean()) / state_df[feat_cols].std()
target = Fz.iloc[-1].to_numpy()
dists = np.linalg.norm(Fz.to_numpy() - target, axis=1)
state_df["dist_to_current"] = dists
analogs = state_df[state_df["end_sess_idx"] < n_sess - 30].nsmallest(10, "dist_to_current")
print("10 nearest historical 60-session regime analogs to the CURRENT window (Product-A-flavored "
      "state vector; excludes trivially-overlapping recent windows):")
print(analogs[["end_sess", "dist_to_current"] + feat_cols].round(3).to_string(index=False))
state_df.to_csv(os.path.join(OUT, "sec2b_regime_state_vectors.csv"), index=False)
analogs.to_csv(os.path.join(OUT, "sec2b_nearest_analogs.csv"), index=False)

# pooled forward-60-session Product-A net P&L following each analog window
FWD = 60
analog_fwd_series = []
analog_fwd_nets = []
for _, r in analogs.iterrows():
    idx = int(r["end_sess_idx"])
    fwd_start, fwd_end = idx + 1, min(idx + FWD, n_sess - 1)
    if fwd_end > fwd_start:
        seg = daily["net"].iloc[fwd_start:fwd_end + 1]
        analog_fwd_series.append(seg)
        analog_fwd_nets.append(float(seg.sum()))
print(f"\nforward-60-session Product-A net P&L following each of these {len(analog_fwd_nets)} analog "
      f"windows: {[round(x, 2) for x in analog_fwd_nets]}")
if analog_fwd_nets:
    print(f"mean={np.mean(analog_fwd_nets):.2f}  median={np.median(analog_fwd_nets):.2f}")
pooled_fwd = pd.concat(analog_fwd_series).to_numpy() if analog_fwd_series else np.array([])
n_analog_windows = len(analog_fwd_nets)

# ============================================================== SEC2 -- 7-ROW WINDOW SUMMARY TABLE
print("\n" + "=" * 90, "\nSEC2 -- WINDOW SUMMARY TABLE (dd_battery, same metric fn as Product-B panel)\n",
      "=" * 90, sep="")

window_rows = []


def add_row(label, sub_daily, note=""):
    b = dd_battery(sub_daily["sess"], sub_daily["net"].to_numpy(), label=label)
    window_rows.append({
        "window": label, "n_sessions": b["n_days"], "net": b["net"], "sharpe": b["sharpe"],
        "sortino": b["sortino"], "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"],
        "CDaR5": b["CDaR5"], "worst_day": float(sub_daily["net"].min()),
        "worst_month": b["worst_month"], "pos_day_pct": b["pos_day_pct"], "note": note,
    })


add_row("FULL-HISTORY (2022-01-03..2026-07-31)", daily)
add_row("PRE-2026 (2022-2025)", daily[daily["year"] <= 2025])
add_row("2026-YTD (thru 2026-07-31)", daily[daily["year"] == 2026])
for w in (20, 60, 120):
    add_row(f"LATEST-{w}", daily.tail(w))

# ANALOGS row: pooled dd_battery over the concatenated forward-60-session windows following the
# 10 nearest historical regime analogs. NOTE (disclosed, same caveat class as SA0 sec10): this is
# a spliced series across non-contiguous historical periods, not one contiguous stretch -- Sharpe/
# drawdown here describe "what typically followed analog regimes," not a real equity curve.
if len(pooled_fwd) > 1:
    fake_dates = pd.date_range("2000-01-01", periods=len(pooled_fwd), freq="D")  # dd_battery needs dates; spliced/synthetic
    b = dd_battery(fake_dates, pooled_fwd, label="ANALOGS")
    window_rows.append({
        "window": f"ANALOGS (pooled fwd-60 after {n_analog_windows} nearest regime analogs)",
        "n_sessions": len(pooled_fwd), "net": float(np.mean(analog_fwd_nets)) if analog_fwd_nets else np.nan,
        "sharpe": b["sharpe"], "sortino": b["sortino"], "calmar": np.nan, "maxDD_eod": np.nan,
        "CDaR5": np.nan, "worst_day": float(np.min(pooled_fwd)), "worst_month": np.nan,
        "pos_day_pct": b["pos_day_pct"],
        "note": "net = MEAN forward-60-session net across analogs (not a sum); DD/Calmar fields "
                "N/A -- spliced non-contiguous series, see sec2b caveats",
    })

window_df = pd.DataFrame(window_rows)
print(window_df.round(3).to_string(index=False))
window_df.to_csv(os.path.join(OUT, "sec2_window_summary.csv"), index=False)

# ============================================================== SEC3 -- MONTHLY / QUARTERLY 2026
print("\n" + "=" * 90, "\nSEC3 -- MONTHLY + QUARTERLY 2026 NET P&L\n", "=" * 90, sep="")
d2026 = daily[daily["year"] == 2026].copy()
d2026["month"] = d2026["sess"].dt.to_period("M").astype(str)
d2026["quarter"] = d2026["sess"].dt.to_period("Q").astype(str)
monthly = d2026.groupby("month").agg(n_sessions=("net", "size"), net=("net", "sum"),
                                      win_rate=("net", lambda x: float((x > 0).mean())))
quarterly = d2026.groupby("quarter").agg(n_sessions=("net", "size"), net=("net", "sum"),
                                          win_rate=("net", lambda x: float((x > 0).mean())))
print("Monthly 2026:")
print(monthly.round(2))
print("\nQuarterly 2026:")
print(quarterly.round(2))
monthly.to_csv(os.path.join(OUT, "sec3_monthly_2026.csv"))
quarterly.to_csv(os.path.join(OUT, "sec3_quarterly_2026.csv"))

print("\n[H0] sec2/sec2b/sec3 complete.")
