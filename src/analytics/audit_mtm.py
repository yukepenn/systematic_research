"""AUDIT-03: bar-level mark-to-market equity reconstruction.

Builds, for any campaign fill ledger (execledger CSV format) plus an exported
bar series (AuditBarExport1 CSV), the three daily P&L conventions the audit
must reconcile:

    calendar : whole round-trip net on the CALENDAR date of the exit fill
               (execledger.daily_vector — the published basis)
    session  : whole round-trip net on the NT8 SESSION date of the exit fill
               (runlib.session_date — 18:00 ET roll)
    true_mtm : bar-level position-marked equity, sampled at each session's
               last bar (cash + open-position value), differenced per session

For a strategy that is genuinely flat at every session close, session and
true_mtm must agree to the penny on session granularity — that identity is an
AUDIT CHECK here, not an assumption. calendar differs whenever a session's
trades span the midnight boundary (every CME session does).

All series are labeled by the audit convention: TRUE_MTM or REALIZED_ONLY.

Usage (CWD = repo root):
    from audit_mtm import member_frames, mtm_report
"""
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

POINT_VALUE = {"NQ": 20.0, "MNQ": 2.0, "ES": 50.0, "MES": 5.0}

BUY_ACTIONS = {"Buy", "BuyToCover"}
SELL_ACTIONS = {"Sell", "SellShort"}


def read_fills(path):
    """Fill ledger CSV -> DataFrame with signed quantity delta per fill."""
    df = pd.read_csv(path, comment="#", parse_dates=["time"])
    delta = np.where(df.order_action.isin(BUY_ACTIONS), df.qty,
                     np.where(df.order_action.isin(SELL_ACTIONS), -df.qty, 0))
    if (delta == 0).any():
        bad = df.order_action[pd.Series(delta, index=df.index) == 0].unique()
        raise ValueError(f"unknown order_action values: {bad}")
    df["delta"] = delta
    df["position"] = df.delta.cumsum()
    if df.position.iloc[-1] != 0:
        raise ValueError(f"{path}: ledger does not end flat (pos {df.position.iloc[-1]})")
    return df


def read_bars(path):
    """AuditBarExport1 CSV -> DataFrame indexed by bar close time."""
    bars = pd.read_csv(path, parse_dates=["time"])
    bars = bars.set_index("time").sort_index()
    if bars.index.has_duplicates:
        raise ValueError(f"{path}: duplicate bar timestamps")
    return bars


def session_date(ts):
    """NT8 session date: >=18:00 rolls to next day; weekend rolls to Monday."""
    d = ts.date()
    if ts.hour >= 18:
        d = d + timedelta(days=1)
    while d.weekday() >= 5:
        d = d + timedelta(days=1)
    return d


def bar_equity(fills, bars, point_value=20.0):
    """Bar-close equity curve (cash + open position value). TRUE_MTM basis."""
    cash_flow = (-fills.delta * fills.price * point_value - fills.commission)
    cash_at = cash_flow.groupby(fills.time).sum().cumsum()
    pos_at = fills.delta.groupby(fills.time).sum().cumsum()
    idx = bars.index
    cash = cash_at.reindex(idx, method="ffill").fillna(0.0)
    pos = pos_at.reindex(idx, method="ffill").fillna(0.0)
    equity = cash + pos * bars.close * point_value
    return pd.DataFrame({"equity": equity, "pos": pos})


def daily_conventions(fills, bars, point_value=20.0):
    """Return DataFrame: session-indexed daily P&L under all three conventions,
    plus max intraday (bar-level) equity drawdown stats."""
    # round-trip pairing identical to execledger (flat-or-one-lot enforced upstream)
    eq = bar_equity(fills, bars, point_value)
    sess = pd.Series([session_date(t) for t in eq.index], index=eq.index)
    last_bar = eq.groupby(sess.values).tail(1)
    mtm_daily = last_bar.equity.diff()
    mtm_daily.iloc[0] = last_bar.equity.iloc[0]
    mtm_daily.index = [session_date(t) for t in last_bar.index]

    # realized round trips from fills
    entries, exits, nets = [], [], []
    pos = 0
    entry_px = entry_t = None
    entry_comm = 0.0
    for r in fills.itertuples():
        prev = pos
        pos += r.delta
        if prev == 0 and pos != 0:
            entry_px, entry_t, entry_comm = r.price, r.time, r.commission
        elif prev != 0 and pos == 0:
            side = 1 if prev > 0 else -1
            nets.append(side * (r.price - entry_px) * point_value * abs(prev)
                        - r.commission - entry_comm)
            entries.append(entry_t)
            exits.append(r.time)
    trades = pd.DataFrame({"entry": entries, "exit": exits, "net": nets})
    cal = trades.set_index(pd.DatetimeIndex(trades["exit"]).normalize()) \
                .net.groupby(level=0).sum()
    ses = trades.set_index(pd.Index([session_date(t) for t in trades["exit"]])) \
                .net.groupby(level=0).sum()

    out = pd.DataFrame({
        "true_mtm": mtm_daily,
        "session_realized": ses.reindex(mtm_daily.index).fillna(0.0),
    })
    out.index.name = "session"
    identity_err = (out.true_mtm - out.session_realized).abs().max()
    return out, cal, trades, eq, identity_err


def summary_metrics(daily, ann=252):
    d = daily.dropna()
    mu, sd = d.mean(), d.std(ddof=1)
    sharpe = 0.0 if sd == 0 else mu / sd * np.sqrt(ann)
    equity = d.cumsum()
    dd = equity - equity.cummax()
    maxdd = dd.min()
    es5 = d[d <= d.quantile(0.05)].mean()
    tuw = int((dd < 0).sum())
    return dict(n_days=len(d), net=round(d.sum(), 2), sharpe=round(sharpe, 4),
                max_dd=round(maxdd, 2), calmar=round((mu * ann) / abs(maxdd), 4) if maxdd else np.nan,
                es5=round(es5, 2), tuw_days=tuw,
                worst_day=round(d.min(), 2), best_day=round(d.max(), 2))
