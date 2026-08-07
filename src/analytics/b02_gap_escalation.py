"""B02 — gap-rejection escalation gates (seq 232). Config identical to B01e;
reads ONLY the preregistered unseen facets. Gates in runs/B02_GAP_ESCALATION/spec.yaml.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BARS = os.path.join(ROOT, "runs", "B01A_BARS_1M", "nq_1m_2022_2026.csv")
OUT = os.path.join(ROOT, "research", "04_complementary_family")
TICK, PV, RT = 0.25, 20.0, 4.36


def run(slip_ticks):
    bars = pd.read_csv(BARS, parse_dates=["time"])
    bars["date"] = bars.time.dt.date
    m = bars.time.dt.hour * 60 + bars.time.dt.minute
    rows = []
    prior_close = None
    s = slip_ticks * TICK
    for d, g in bars.groupby("date"):
        gm = m.loc[g.index]
        c1600 = g.loc[gm[gm == 960].index]
        open930 = g.loc[gm[gm == 571].index]
        if prior_close is not None and len(open930):
            o = open930.iloc[0].open
            gap = (o - prior_close) / prior_close
            if abs(gap) >= 0.0035:
                side = -np.sign(gap)
                entry = o + (s if side > 0 else -s)
                stop_idx = gm[gm == 690].index
                seg = g.loc[open930.index[0]:(stop_idx[0] if len(stop_idx) else g.index[-1])]
                exit_px = None
                for r in seg.itertuples():
                    if r.low <= prior_close <= r.high:
                        exit_px = prior_close
                        break
                if exit_px is None:
                    exit_px = seg.iloc[-1].close
                exit_px -= (s if side > 0 else -s)
                rows.append(dict(date=d, year=pd.Timestamp(d).year, side=int(side),
                                 gap_pct=100 * gap,
                                 pnl=side * (exit_px - entry) * PV - RT))
        if len(c1600):
            prior_close = c1600.iloc[0].close
    return pd.DataFrame(rows)


def main():
    res = {}
    # (1) slip-2
    t2 = run(2)
    res["slip2_net"] = round(t2.pnl.sum(), 2)
    res["slip2_avg"] = round(t2.pnl.mean(), 2)
    g1 = t2.pnl.sum() > 0 and t2.pnl.mean() >= 35
    # base series for remaining gates
    t1 = run(1)
    dates = pd.DatetimeIndex(pd.to_datetime(t1.date))
    # (2) roll-day integrity: quarterly roll = 2nd Thursday of Mar/Jun/Sep/Dec;
    # exclude sessions within +-2 days of every quarterly 2nd Thursday
    rolls = []
    for y in range(2022, 2027):
        for mth in (3, 6, 9, 12):
            d1 = pd.Timestamp(y, mth, 1)
            thursdays = pd.date_range(d1, d1 + pd.offsets.MonthEnd(0), freq="W-THU")
            rolls.append(thursdays[1])
    roll_win = set()
    for r in rolls:
        for k in range(-2, 3):
            roll_win.add((r + pd.Timedelta(days=k)).date())
    mask = ~pd.Series([d in roll_win for d in t1.date])
    net_all, net_ex = t1.pnl.sum(), t1.pnl[mask.values].sum()
    res["net_slip1"] = round(net_all, 2)
    res["net_ex_roll"] = round(net_ex, 2)
    res["roll_delta_pct"] = round(100 * abs(net_all - net_ex) / abs(net_all), 1)
    g2 = abs(net_all - net_ex) / abs(net_all) < 0.15
    # (3) concentration
    daily = t1.groupby("date").pnl.sum()
    ex_top5 = t1.pnl.sum() - daily.nlargest(5).sum()
    n_top1 = max(1, int(np.ceil(0.01 * len(t1))))
    top1_share = t1.pnl.nlargest(n_top1).sum() / t1.pnl.sum()
    res["net_ex_top5_days"] = round(ex_top5, 2)
    res["top1pct_share"] = round(float(top1_share), 3)
    g3 = ex_top5 > 0 and top1_share < 0.50
    # (4) tail
    res["worst_trade"] = round(t1.pnl.min(), 2)
    es5 = t1.pnl[t1.pnl <= t1.pnl.quantile(0.05)].mean()
    res["trade_es5"] = round(es5, 2)
    g4 = t1.pnl.min() > -4000 and es5 > -1500
    # (5) independence vs Family A (E10 session daily)
    ev = pd.read_csv(os.path.join(ROOT, "research", "audit",
                                  "e_variant_daily_vectors.csv"))
    e10 = pd.Series(ev.E10_round_session.values,
                    index=pd.to_datetime(ev.day)).dropna()
    b = pd.Series(daily.values, index=pd.DatetimeIndex(pd.to_datetime(daily.index)))
    both = pd.DataFrame({"a": e10, "b": b}).dropna()
    lose = both[both.a < 0]
    res["losing_day_corr"] = round(float(lose.a.corr(lose.b)), 4) if len(lose) > 10 else np.nan
    top10 = e10.nlargest(10)
    combo_top10 = (0.5 * top10 + 0.5 * b.reindex(top10.index).fillna(0.0)).sum()
    res["famA_top10_retention_5050"] = round(float(combo_top10 / (0.5 * top10.sum())), 4)
    g5 = res["losing_day_corr"] < 0.2 and res["famA_top10_retention_5050"] >= 0.85
    # (6) monthly stability
    mon = t1.assign(mon=dates.to_period("M")).groupby("mon").agg(
        n=("pnl", "size"), net=("pnl", "sum"))
    mon3 = mon[mon.n >= 3]
    res["months_ge3ev_positive_pct"] = round(100 * (mon3.net > 0).mean(), 1)
    g6 = (mon3.net > 0).mean() >= 0.60
    gates = dict(g1_slip2=g1, g2_roll=g2, g3_conc=g3, g4_tail=g4,
                 g5_indep=g5, g6_monthly=g6)
    res.update({k: bool(v) for k, v in gates.items()})
    verdict = "PASS" if all(gates.values()) else "FAIL"
    res["verdict"] = verdict
    for k, v in res.items():
        print(f"{k}: {v}")
    pd.Series(res).to_csv(os.path.join(OUT, "b02_gap_escalation_result.csv"))
    t1.to_csv(os.path.join(OUT, "b02_gap_trades_slip1.csv"), index=False)


if __name__ == "__main__":
    main()
