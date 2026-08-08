"""SMV2R shared executor helpers — instrumented copy of sm01_solarsim.e10_sim
(verbatim semantics, verified vs e10_daily_py.csv to 1.8e-12 $ in step0) + metric row."""
import sys, os
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm
import sm_metrics as smm
from smv2_common import dd_battery


def e10_exec(bars, tgt, comm_side=sm.MNQ_COMM_SIDE, point_value=sm.MNQ_POINT_VALUE):
    """Returns (daily_df[sess,net,contracts], bar_pos, bar_pnl)."""
    n = len(bars)
    open_ = bars["open"].to_numpy(); high = bars["high"].to_numpy()
    low = bars["low"].to_numpy(); close = bars["close"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    sess_date = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0
    daily = {}; contracts = {}
    prev_equity = 0.0
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    prev_eq_bar = 0.0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p
            side = 1 if d > 0 else -1
            px = sm._fill(open_[t], high[t], low[t], side)
            cash -= d * px * point_value
            cash -= abs(d) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(d)
            p = pend_
        if last_of_sess[t] and p != 0:
            side = -1 if p > 0 else 1
            px = sm._fill(open_[t], high[t], low[t], side, at_close=close[t])
            cash += p * px * point_value
            cash -= abs(p) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(p)
            p = 0; pend_ = 0
        else:
            pend_ = tgt[t]
        eq_bar = cash + p * close[t] * point_value
        bar_pnl[t] = eq_bar - prev_eq_bar
        prev_eq_bar = eq_bar
        bar_pos[t] = p
        if last_of_sess[t]:
            eq = cash + p * close[t] * point_value
            daily[sess_date[t]] = eq - prev_equity
            prev_equity = eq
            contracts.setdefault(sess_date[t], 0)
    dd = pd.DataFrame({"sess": list(daily.keys()), "net": list(daily.values())})
    dd["contracts"] = [contracts[s] for s in daily.keys()]
    return dd, bar_pos, bar_pnl


def metric_row(label, daily):
    """Battery: sm_metrics.metrics + smv2_common CDaR5 on the daily net vector."""
    s = pd.Series(daily["net"].to_numpy(), index=pd.to_datetime(daily["sess"]))
    m = smm.metrics(s)
    b = dd_battery(daily["sess"], daily["net"].to_numpy(), label=label)
    x = daily["net"].to_numpy()
    return {
        "arm": label, "n_sessions": m["n_sessions"], "net": m["net"],
        "sharpe": m["sharpe"], "max_dd": m["max_dd"], "CDaR5": b["CDaR5"],
        "es5_daily": m["es5_daily"], "worst_day": m["worst_day"],
        "worst_month": m["worst_month"],
        "top10_day_sum": float(np.sort(x)[-10:].sum()),
        "top10_day_share": m["top10_day_share"],
        "pos_day_frac": m["pos_day_frac"],
        "avg_contracts_per_day": float(daily["contracts"].mean()),
        "calmar": m["calmar"], "sortino": m["sortino"],
    }
