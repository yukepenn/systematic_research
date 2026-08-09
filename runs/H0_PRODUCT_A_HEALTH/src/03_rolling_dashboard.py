"""H0 sec4 -- rolling 20/60/120-session dashboard (net, Sharpe, expectancy/trip, trip win-rate,
avg-win/avg-loss, turnover, long/short split) + current drawdown/underwater. sec5 -- historical-
percentile context for every rolling reading (net, Sharpe, expectancy, win-rate, turnover), i.e.
where the CURRENT rolling-W reading ranks against the full distribution of all historical rolling-W
readings. Mirrors SA0 current_health/src/03_dashboard.py's sec4-5 structure exactly, extended with
expectancy/win-rate/turnover percentiles (SA0's own panel only percentiled net+Sharpe)."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
daily = pd.read_csv(os.path.join(OUT, "daily_pnl_A.csv"), parse_dates=["sess"])
trips = pd.read_csv(os.path.join(OUT, "trip_ledger_A.csv"), parse_dates=["entry_sess", "exit_sess"])
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "sess_date", "target_exposure_A", "bar_pnl_A_dollars"])

sess_list = daily["sess"].tolist()
n_sess = len(sess_list)

# ============================================================== per-session aggregates (trips + turnover + long/short)
trips["entry_sess_dt"] = pd.to_datetime(trips["entry_sess"])
tsess = trips.groupby("entry_sess_dt").agg(
    n_trips=("net_pnl", "size"), sum_pnl=("net_pnl", "sum"),
    n_win=("net_pnl", lambda x: int((x > 0).sum())),
    sum_win=("net_pnl", lambda x: float(x[x > 0].sum())),
    n_loss=("net_pnl", lambda x: int((x <= 0).sum())),
    sum_loss=("net_pnl", lambda x: float(x[x <= 0].sum())),
).reindex(sess_list).fillna(0.0)

u0["sess_dt"] = pd.to_datetime(u0["sess_date"])
u0 = u0.sort_values("t_idx")
u0["turnover"] = u0["target_exposure_A"].diff().abs()
u0.loc[u0.index[0], "turnover"] = abs(u0["target_exposure_A"].iloc[0])  # first bar overall: entry from implicit 0
turnover_sess = u0.groupby("sess_dt")["turnover"].sum().reindex(sess_list).fillna(0.0)

long_pnl_sess = u0.assign(lp=np.where(u0["target_exposure_A"] > 0, u0["bar_pnl_A_dollars"], 0.0)) \
    .groupby("sess_dt")["lp"].sum().reindex(sess_list).fillna(0.0)
short_pnl_sess = u0.assign(sp=np.where(u0["target_exposure_A"] < 0, u0["bar_pnl_A_dollars"], 0.0)) \
    .groupby("sess_dt")["sp"].sum().reindex(sess_list).fillna(0.0)

daily = daily.set_index("sess")
daily["n_trips"] = tsess["n_trips"].to_numpy()
daily["trip_pnl"] = tsess["sum_pnl"].to_numpy()
daily["n_win"] = tsess["n_win"].to_numpy()
daily["sum_win"] = tsess["sum_win"].to_numpy()
daily["n_loss"] = tsess["n_loss"].to_numpy()
daily["sum_loss"] = tsess["sum_loss"].to_numpy()
daily["turnover"] = turnover_sess.to_numpy()
daily["long_pnl"] = long_pnl_sess.to_numpy()
daily["short_pnl"] = short_pnl_sess.to_numpy()
daily = daily.reset_index()

# ============================================================== SEC4 -- CURRENT ROLLING DASHBOARD
print("=" * 90, "\nSEC4 -- CURRENT ROLLING DASHBOARD (as of latest available session)\n", "=" * 90, sep="")

rows = []
for w in (20, 60, 120):
    win = daily.tail(w)
    b = dd_battery(win["sess"], win["net"].to_numpy(), label=f"roll{w}")
    n_trips = int(win["n_trips"].sum())
    trip_pnl = float(win["trip_pnl"].sum())
    n_win = int(win["n_win"].sum()); n_loss = int(win["n_loss"].sum())
    sum_win = float(win["sum_win"].sum()); sum_loss = float(win["sum_loss"].sum())
    row = {
        "window": w, "net": float(win["net"].sum()), "sharpe": b["sharpe"],
        "n_trips": n_trips, "expectancy_per_trip": trip_pnl / n_trips if n_trips else np.nan,
        "trip_win_rate": n_win / n_trips if n_trips else np.nan,
        "avg_win": sum_win / n_win if n_win else np.nan,
        "avg_loss": sum_loss / n_loss if n_loss else np.nan,
        "turnover_contracts_total": float(win["turnover"].sum()),
        "turnover_contracts_per_session": float(win["turnover"].sum()) / w,
        "long_pnl": float(win["long_pnl"].sum()), "short_pnl": float(win["short_pnl"].sum()),
    }
    rows.append(row)
    print(f"rolling {w}: net={row['net']:.2f} sharpe={row['sharpe']:.3f} n_trips={n_trips} "
          f"expectancy={row['expectancy_per_trip']:.2f} win_rate={row['trip_win_rate']:.3f} "
          f"avg_win={row['avg_win']:.2f} avg_loss={row['avg_loss']:.2f} "
          f"turnover/sess={row['turnover_contracts_per_session']:.2f} "
          f"long={row['long_pnl']:.2f} short={row['short_pnl']:.2f}")
roll_df = pd.DataFrame(rows)

# current drawdown / underwater / losing streak
cum = daily["net"].cumsum(); peak = cum.cummax(); dd = peak - cum
daily["dd"] = dd.to_numpy()
current_dd = float(dd.iloc[-1])
underwater_mask = dd > 0
cur_streak = 0
for v in underwater_mask.iloc[::-1]:
    if v: cur_streak += 1
    else: break
losing_streak = 0
for v in (daily["net"].iloc[::-1] < 0):
    if v: losing_streak += 1
    else: break
print(f"\ncurrent drawdown: ${current_dd:.2f}  current time-underwater: {cur_streak} sessions  "
      f"current losing-session streak: {losing_streak}")

dash_summary = {"current_drawdown": current_dd, "current_time_underwater_sessions": cur_streak,
                 "current_losing_streak_sessions": losing_streak,
                 "latest_session": str(daily["sess"].max().date())}
roll_df.to_csv(os.path.join(OUT, "sec4_rolling_dashboard.csv"), index=False)
json.dump(dash_summary, open(os.path.join(OUT, "sec4_dashboard_summary.json"), "w"), indent=2)

# ============================================================== SEC5 -- HISTORICAL PERCENTILE CONTEXT
print("\n" + "=" * 90, "\nSEC5 -- HISTORICAL PERCENTILE CONTEXT for current rolling readings\n", "=" * 90, sep="")


def sharpe_roll(x):
    sd = x.std(ddof=1)
    return x.mean() / sd * np.sqrt(252) if sd > 0 else np.nan


percentile_rows = []
for w in (20, 60, 120):
    net_r = daily["net"].rolling(w).sum()
    sharpe_r = daily["net"].rolling(w).apply(sharpe_roll, raw=False)
    ntrip_r = daily["n_trips"].rolling(w).sum()
    trippnl_r = daily["trip_pnl"].rolling(w).sum()
    nwin_r = daily["n_win"].rolling(w).sum()
    turnover_r = daily["turnover"].rolling(w).sum() / w
    expectancy_r = trippnl_r / ntrip_r.replace(0, np.nan)
    winrate_r = nwin_r / ntrip_r.replace(0, np.nan)

    def pctile(series):
        cur = series.iloc[-1]
        valid = series.dropna()
        return cur, float((valid <= cur).mean() * 100) if len(valid) else np.nan

    cur_net, pct_net = pctile(net_r)
    cur_sharpe, pct_sharpe = pctile(sharpe_r)
    cur_exp, pct_exp = pctile(expectancy_r)
    cur_wr, pct_wr = pctile(winrate_r)
    cur_to, pct_to = pctile(turnover_r)
    percentile_rows.append({
        "window": w, "current_net": cur_net, "net_percentile": pct_net,
        "current_sharpe": cur_sharpe, "sharpe_percentile": pct_sharpe,
        "current_expectancy": cur_exp, "expectancy_percentile": pct_exp,
        "current_win_rate": cur_wr, "win_rate_percentile": pct_wr,
        "current_turnover_per_sess": cur_to, "turnover_percentile": pct_to,
    })
    print(f"rolling {w}: net={cur_net:.2f} (pct {pct_net:.1f}) | sharpe={cur_sharpe:.3f} (pct {pct_sharpe:.1f}) | "
          f"expectancy={cur_exp:.2f} (pct {pct_exp:.1f}) | win_rate={cur_wr:.3f} (pct {pct_wr:.1f}) | "
          f"turnover/sess={cur_to:.2f} (pct {pct_to:.1f})")
pctile_df = pd.DataFrame(percentile_rows)
pctile_df.to_csv(os.path.join(OUT, "sec5_percentile_context.csv"), index=False)

dd_hist = daily["dd"].to_numpy()
cur_dd_pctile = float((dd_hist <= current_dd).mean() * 100)
print(f"\ncurrent drawdown ${current_dd:.2f} is at the {cur_dd_pctile:.1f}th percentile of all "
      f"historical daily drawdown readings (higher = worse/deeper than usual)")
json.dump({"current_dd_percentile": cur_dd_pctile}, open(os.path.join(OUT, "sec5_dd_percentile.json"), "w"), indent=2)

daily.to_csv(os.path.join(OUT, "daily_pnl_A_enriched.csv"), index=False)
print("\n[H0] sec4/sec5 rolling dashboard complete.")
