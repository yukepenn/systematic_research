"""SW00 experiment-level analysis: gate evaluation + report generation."""
import json
import os

import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
R = lambda *p: os.path.join(ROOT, *p)


def load(run):
    return pd.read_parquet(R("runs", run, "trades.parquet"))


def metrics(run):
    with open(R("runs", run, "metrics.json"), encoding="utf-8") as f:
        return json.load(f)


out = {}
t0 = load("SW00_R01")
t1 = load("SW00_R06")

# --- slippage realization: match trades by entry_time+side, measure fill deltas (ticks) ---
m = t0.merge(t1, on=["entry_time", "side"], suffixes=("_0", "_1"))
out["slip_match_n"] = int(len(m))
ent = (m["entry_price_1"] - m["entry_price_0"]) * m["side"] / 0.25   # +1 = adverse 1 tick on entry
exi = (m["exit_price_0"] - m["exit_price_1"]) * m["side"] / 0.25     # +1 = adverse 1 tick on exit
out["entry_slip_ticks_dist"] = ent.value_counts().sort_index().to_dict()
out["exit_slip_ticks_dist"] = exi.round(2).value_counts().sort_index().head(8).to_dict()
out["pct_entry_full_tick"] = round(100 * float((ent == 1).mean()), 2)
out["pct_exit_full_tick"] = round(100 * float((exi == 1).mean()), 2)

# --- audits detail on R01 ---
sc = t0[t0["exit_name"].str.contains("session close", case=False, na=False)]
odd_sc = sc[~((sc["exit_time"].dt.hour == 17) & (sc["exit_time"].dt.minute == 0))]
out["odd_session_close_exits"] = odd_sc["exit_time"].dt.strftime("%Y-%m-%d %H:%M").tolist()
zt = t0[t0["duration_min"] == 0]
out["same_timestamp_trades"] = zt[["entry_time", "entry_price", "exit_price", "exit_name", "profit"]].astype(str).to_dict("records")

# --- High vs Standard fills on the identical sub-window (R09 High vs R11 Standard) ---
t9, t11 = load("SW00_R09"), load("SW00_R11")
cut = t9["entry_time"].max()
t11w = t11[t11["entry_time"] <= cut]
out["high_n"], out["std_n_same_window"] = int(len(t9)), int(len(t11w))
mm = t9.merge(t11w, on=["entry_time", "side"], suffixes=("_h", "_s"))
out["high_matched"] = int(len(mm))
out["high_entry_price_diffs"] = int((mm["entry_price_h"] != mm["entry_price_s"]).sum())
out["high_exit_price_diffs"] = int((mm["exit_price_h"] != mm["exit_price_s"]).sum())
out["high_exit_time_diffs"] = int((mm["exit_time_h"] != mm["exit_time_s"]).sum())
with open(R("runs", "SW00_R09", "raw_result.json"), encoding="utf-8") as f:
    out["high_trace"] = json.load(f)["result"]["trace"]

# --- decompositions on R01 ---
t0["year"] = t0["session"].dt.year
t0["quarter"] = t0["session"].dt.to_period("Q").astype(str)
t0["month"] = t0["session"].dt.to_period("M").astype(str)
t0["dow"] = t0["session"].dt.day_name()
t0["side_name"] = t0["side"].map({1: "Long", -1: "Short"})
t0["rth"] = t0["entry_time"].dt.hour.between(9, 16)  # approx RTH 9:30-17:00 ET tag


def agg(g):
    wins = g[g.profit > 0]["profit"]
    loss = g[g.profit < 0]["profit"]
    return pd.Series(dict(
        n=len(g), net=round(g.profit.sum(), 0),
        avg=round(g.profit.mean(), 2),
        win_pct=round(100 * (g.profit > 0).mean(), 1),
        pf=round(wins.sum() / -loss.sum(), 3) if len(loss) and loss.sum() < 0 else None,
        mae_avg=round(g.mae.mean(), 0), mfe_avg=round(g.mfe.mean(), 0),
    ))


for key in ("year", "quarter", "side_name", "dow", "exit_name", "rth"):
    out[f"by_{key}"] = t0.groupby(key, observed=True).apply(agg, include_groups=False).reset_index().to_dict("records")
out["by_entry_hour"] = t0.groupby("entry_hour").apply(agg, include_groups=False).reset_index().to_dict("records")

# monthly table for report
out["by_month"] = t0.groupby("month").apply(agg, include_groups=False).reset_index().to_dict("records")

# largest winners/losers for manual inspection
cols = ["trade_n", "side_name", "entry_time", "entry_price", "exit_time", "exit_price", "exit_name", "profit"]
out["top5_winners"] = t0.nlargest(5, "profit")[cols].astype(str).to_dict("records")
out["top5_losers"] = t0.nsmallest(5, "profit")[cols].astype(str).to_dict("records")

# MFE giveback on winners>0: (mfe - profit_gross)/mfe
g = t0[t0["mfe"] > 0].copy()
g["giveback"] = (g["mfe"] - (g["profit"] + g["commission"])) / g["mfe"]
out["median_mfe_giveback"] = round(float(g["giveback"].median()), 3)

# cost ladder from run metrics
ladder = {}
for run, slip in (("SW00_R01", 0), ("SW00_R06", 1), ("SW00_R07", 2), ("SW00_R08", 3)):
    mt = metrics(run)["metrics"]
    ladder[slip] = dict(net_nt8=round(mt["nt8"]["NetProfit"], 2), avg_trade=mt["avg_trade"],
                        pf=mt["pf"], sharpe=mt["daily_sharpe"], sortino=mt["daily_sortino"],
                        calmar=mt["calmar"], dd_nt8=round(mt["nt8"]["MaxDrawdown"], 2),
                        es95=mt["es95_daily"], worst_q=mt["worst_quarter"],
                        tuw_max=mt["tuw_days_max"], pct_pos_months=mt["pct_positive_months"],
                        top_decile_share=mt["top_decile_share_of_gp"],
                        net_minus_top10=mt["net_minus_top10"])
out["ladder"] = ladder

# gates
g1 = all(metrics(r)["hashes"]["ledger_hash"] == metrics("SW00_R01")["hashes"]["ledger_hash"]
         for r in ("SW00_R02", "SW00_R03", "SW00_R04", "SW00_R05", "SW00_R12", "SW00_R13"))
s1 = ladder[1]
out["gates"] = dict(
    determinism=bool(g1),
    params_echo=all(metrics(r)["hashes"]["params_hash"] == metrics("SW00_R01")["hashes"]["params_hash"]
                    for r in ("SW00_R02", "SW00_R06", "SW00_R07", "SW00_R08")),
    slip1_positive=s1["net_nt8"] > 0 and s1["avg_trade"] > 0,
    slip1_soft_2p5x=s1["avg_trade"] >= 35.90,
    slip2_not_destroyed=ladder[2]["net_nt8"] > 0,
    pnl_identity=metrics("SW00_R01")["audits"]["pnl_identity_max_abs_err"] < 0.005,
    no_session_span=metrics("SW00_R01")["audits"]["trades_spanning_sessions"] == 0,
)

with open(R("research", "00_truth", "SW00_analysis.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
print(json.dumps({k: out[k] for k in ("slip_match_n", "pct_entry_full_tick", "pct_exit_full_tick",
                                       "entry_slip_ticks_dist", "odd_session_close_exits",
                                       "same_timestamp_trades", "high_matched", "high_entry_price_diffs",
                                       "high_exit_price_diffs", "high_exit_time_diffs", "high_trace",
                                       "median_mfe_giveback", "gates")}, indent=1, default=str))
print("BY_YEAR:", json.dumps(out["by_year"], default=str))
print("BY_SIDE:", json.dumps(out["by_side_name"], default=str))
print("BY_EXIT:", json.dumps(out["by_exit_name"], default=str))
print("TOP5W:", json.dumps(out["top5_winners"], default=str))
print("TOP5L:", json.dumps(out["top5_losers"], default=str))
