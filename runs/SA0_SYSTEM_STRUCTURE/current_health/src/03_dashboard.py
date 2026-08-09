"""Current-regime health dashboard. Reuses health_substrate (extended through 2026-07-31) and
the extended block ledger. Sections map to the owner's addendum sec4-18."""
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
daily["cum"] = daily["net"].cumsum()
daily["peak"] = daily["cum"].cummax()
daily["dd"] = daily["peak"] - daily["cum"]

sys.path.insert(0, os.path.join(H.ROOT, "src", "analytics"))
from smv2_common import dd_battery

LATEST_SESS = daily["sess"].max()
print(f"latest available session (current-health window): {LATEST_SESS.date()}")

# ============================================================== SEC4 -- ROLLING DASHBOARD
print("=" * 90, "\nSEC4 -- CURRENT ROLLING DASHBOARD (as of latest available session)\n", "=" * 90, sep="")


def block_stats(sub):
    if len(sub) == 0:
        return dict(n=0, expectancy=np.nan, win_rate=np.nan, avg_win=np.nan, avg_loss=np.nan)
    win = sub[sub["net_pnl"] > 0]["net_pnl"]
    loss = sub[sub["net_pnl"] <= 0]["net_pnl"]
    return dict(n=len(sub), expectancy=float(sub["net_pnl"].mean()),
                win_rate=float((sub["net_pnl"] > 0).mean()),
                avg_win=float(win.mean()) if len(win) else np.nan,
                avg_loss=float(loss.mean()) if len(loss) else np.nan)


rows = []
for w in [20, 60, 120]:
    win_sess = daily["sess"].iloc[-w:]
    win_daily = daily.iloc[-w:]
    b = dd_battery(win_daily["sess"], win_daily["net"].to_numpy(), label=f"roll{w}")
    win_blocks = blocks[(blocks["entry_sess"] >= win_sess.min()) & (blocks["entry_sess"] <= win_sess.max())]
    bs = block_stats(win_blocks)
    long_pnl = None
    row = {
        "window": w, "net": float(win_daily["net"].sum()), "sharpe": b["sharpe"],
        "n_trades": bs["n"], "expectancy_per_trade": bs["expectancy"], "win_rate": bs["win_rate"],
        "avg_win": bs["avg_win"], "avg_loss": bs["avg_loss"],
        "turnover_trades_per_session": bs["n"] / w,
    }
    rows.append(row)
    print(f"rolling {w}: net={row['net']:.2f} sharpe={row['sharpe']:.3f} n_trades={row['n_trades']} "
          f"expectancy={row['expectancy_per_trade']:.2f} win_rate={row['win_rate']:.3f} "
          f"avg_win={row['avg_win']:.2f} avg_loss={row['avg_loss']:.2f}")
roll_df = pd.DataFrame(rows)
roll_df.to_csv(os.path.join(OUT, "sec4_rolling_dashboard.csv"), index=False)

current_dd = float(daily["dd"].iloc[-1])
peak_idx = daily["cum"].idxmax()
dd_start_candidates = daily[daily["cum"] >= daily["cum"].iloc[-1]]
# time-underwater: sessions since the running peak was last equalled/exceeded (before today)
underwater_mask = daily["dd"] > 0
# find current streak of underwater sessions ending at the last row
cur_streak = 0
for v in underwater_mask.iloc[::-1]:
    if v:
        cur_streak += 1
    else:
        break
losing_streak = 0
for v in (daily["net"].iloc[::-1] < 0):
    if v:
        losing_streak += 1
    else:
        break
print(f"\ncurrent drawdown: ${current_dd:.2f}  current time-underwater: {cur_streak} sessions  "
      f"current losing-session streak: {losing_streak}")

# overnight vs RTH, long vs short (bar-level, latest 60 sessions)
w = 60
cutoff_sess = daily["sess"].iloc[-w:].min()
mask60 = (pd.to_datetime(H.sess_arr) >= cutoff_sess)
bar_pnl60 = H.bpnl_nq[mask60]
barpos60 = H.barpos_nq if hasattr(H, "barpos_nq") else None
# barpos not exported by health_substrate as a name; recompute quickly via pos_full already have
barpos_full = H.pos_full
barpos60 = barpos_full[mask60]
hm60 = H.hm[mask60]
long_pnl60 = float(bar_pnl60[barpos60 > 0].sum())
short_pnl60 = float(bar_pnl60[barpos60 < 0].sum())
overnight_mask = (hm60 < 930) | (hm60 >= 1700)
rth_mask = (hm60 >= 930) & (hm60 < 1700)
overnight_pnl60 = float(bar_pnl60[overnight_mask].sum())
rth_pnl60 = float(bar_pnl60[rth_mask].sum())
print(f"latest-60-session split: long={long_pnl60:.2f} short={short_pnl60:.2f}  "
      f"overnight={overnight_pnl60:.2f} RTH={rth_pnl60:.2f}")

dash_summary = {
    "latest_session": str(LATEST_SESS.date()), "current_drawdown": current_dd,
    "current_time_underwater_sessions": cur_streak, "current_losing_streak_sessions": losing_streak,
    "latest60_long_pnl": long_pnl60, "latest60_short_pnl": short_pnl60,
    "latest60_overnight_pnl": overnight_pnl60, "latest60_rth_pnl": rth_pnl60,
}
json.dump(dash_summary, open(os.path.join(OUT, "sec4_dashboard_summary.json"), "w"), indent=2)

# ============================================================== SEC5 -- HISTORICAL PERCENTILE CONTEXT
print("\n" + "=" * 90, "\nSEC5 -- HISTORICAL PERCENTILE CONTEXT for current rolling stats\n", "=" * 90, sep="")


def rolling_series(w):
    net = daily["net"].rolling(w).sum()
    sharpe = daily["net"].rolling(w).apply(
        lambda x: x.mean() / x.std(ddof=1) * np.sqrt(252) if x.std(ddof=1) > 0 else np.nan, raw=False)
    return net, sharpe


percentile_rows = []
for w in [20, 60, 120]:
    net_roll, sharpe_roll = rolling_series(w)
    cur_net = net_roll.iloc[-1]
    cur_sharpe = sharpe_roll.iloc[-1]
    pct_net = float((net_roll.dropna() <= cur_net).mean() * 100)
    pct_sharpe = float((sharpe_roll.dropna() <= cur_sharpe).mean() * 100)
    percentile_rows.append({"window": w, "current_net": cur_net, "net_percentile": pct_net,
                             "current_sharpe": cur_sharpe, "sharpe_percentile": pct_sharpe})
    print(f"rolling {w}: current net={cur_net:.2f} (percentile {pct_net:.1f}) | "
          f"current sharpe={cur_sharpe:.3f} (percentile {pct_sharpe:.1f})")
pd.DataFrame(percentile_rows).to_csv(os.path.join(OUT, "sec5_percentile_context.csv"), index=False)

# current drawdown percentile
dd_hist = daily["dd"].to_numpy()
cur_dd_pctile = float((dd_hist <= current_dd).mean() * 100)
print(f"\ncurrent drawdown ${current_dd:.2f} is at the {cur_dd_pctile:.1f}th percentile of all "
      f"historical daily drawdown readings (higher percentile = worse/deeper than usual)")

print("\nSA0 current-health dashboard part 1 (sec4-5) complete.")
