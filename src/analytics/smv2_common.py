"""smv2_common.py — shared V2-program metric batteries (SMV2A definitions, frozen)."""
import numpy as np
import pandas as pd


def dd_battery(dates, net, bar_eq=None, label=""):
    dates = pd.to_datetime(pd.Series(dates)); net = np.asarray(net, dtype=float)
    eqd = np.cumsum(net); peak = np.maximum.accumulate(eqd); dd = peak - eqd
    sd = net.std(ddof=1)
    res = {"label": label, "n_days": len(net), "net": net.sum(),
           "daily_vol": sd, "ann_vol": sd * np.sqrt(252),
           "sharpe": net.mean() / sd * np.sqrt(252) if sd > 0 else np.nan,
           "maxDD_eod": dd.max()}
    dn = net[net < 0]
    res["sortino"] = net.mean() / dn.std(ddof=1) * np.sqrt(252) if len(dn) > 1 else np.nan
    ann_ret = net.mean() * 252
    res["calmar"] = ann_ret / dd.max() if dd.max() > 0 else np.nan
    if bar_eq is not None:
        pk = np.maximum.accumulate(bar_eq); res["maxDD_bar"] = (pk - bar_eq).max()
    ddpos = np.sort(dd[dd > 0])[::-1]
    res["CDaR5"] = ddpos[:max(1, int(0.05 * len(dd)))].mean() if len(ddpos) else 0.0
    res["avgDD"] = dd.mean()
    res["ulcer"] = np.sqrt((dd ** 2).mean())
    uw = dd > 1e-9; tuw = 0; cur = 0; rec = []; ep = None
    for i, u in enumerate(uw):
        if u:
            cur += 1; tuw = max(tuw, cur)
            if ep is None: ep = i
        else:
            if ep is not None: rec.append(i - ep); ep = None
            cur = 0
    res["longest_TUW_days"] = tuw
    res["median_recovery"] = float(np.median(rec)) if rec else 0.0
    res["p95_recovery"] = float(np.percentile(rec, 95)) if rec else 0.0
    for w in (20, 40, 60, 120):
        res[f"worst_{w}D"] = pd.Series(net).rolling(w).sum().min() if len(net) >= w else np.nan
    s = pd.Series(net, index=dates)
    mo = s.resample("ME").sum(); qt = s.resample("QE").sum(); wk = s.resample("W").sum()
    res["worst_month"] = mo.min(); res["worst_quarter"] = qt.min()
    res["pos_day_pct"] = (net > 0).mean()
    res["pos_week_pct"] = (wk > 0).mean(); res["pos_month_pct"] = (mo > 0).mean()
    def streak(x):
        b = c = 0
        for v in x:
            c = c + 1 if v < 0 else 0; b = max(b, c)
        return b
    res["losing_month_streak"] = streak(mo.values); res["losing_week_streak"] = streak(wk.values)
    res["rolling60_min"] = pd.Series(net).rolling(60).sum().min() if len(net) >= 60 else np.nan
    return res


def boot_ci_mean(net, block=5, n_boot=10000, seed=20260808, q=(0.05, 0.95)):
    """Circular block bootstrap CI for the daily mean."""
    rng = np.random.default_rng(seed)
    x = np.asarray(net, dtype=float); n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    means = x[idx.reshape(n_boot, -1)[:, :n]].mean(axis=1)
    return np.quantile(means, q[0]), np.quantile(means, q[1]), (means > 0).mean()
