"""execledger.py — Tier-2 analytics from SolarWaveOpenV1X execution ledgers.

The NT8 Strategy Analyzer payload for a full-history run is multi-megabyte JSON,
which is impractical to ship 30+ times. `SolarWaveOpenV1X` instead writes every
fill from OnExecutionUpdate to a compact CSV; this module pairs those fills into
round trips and computes the preregistered Wave-1c metric table.

Round-trip pairing is trivial for this strategy family because it is always
flat-or-one-lot: fills alternate entry, exit, entry, exit, ...  We assert that
invariant rather than assuming it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

POINT_VALUE = {"NQ": 20.0, "MNQ": 2.0, "ES": 50.0, "MES": 5.0}
ENTRY_NAMES = {"Long", "Short"}


def _point_value(instrument: str) -> float:
    root = re.match(r"[A-Z]+", instrument or "NQ")
    return POINT_VALUE.get(root.group(0)[:3] if root else "NQ", 20.0)


def read_exec_ledger(path):
    """Return (trades DataFrame, header dict)."""
    with open(path, "r") as fh:
        header_line = fh.readline().strip()
    header = dict(re.findall(r"(\w+)=([^\s]+)", header_line))
    ex = pd.read_csv(path, comment="#", parse_dates=["time"])
    if ex.empty:
        return pd.DataFrame(), header

    pv = _point_value(header.get("instrument", "NQ"))
    is_entry = ex.name.isin(ENTRY_NAMES).to_numpy()

    # invariant: strictly alternating entry/exit starting with an entry
    if not is_entry[0] or is_entry[-1]:
        raise ValueError(f"{path}: ledger does not start with an entry / end with an exit")
    if (is_entry[::2] == False).any() or (is_entry[1::2] == True).any():
        raise ValueError(f"{path}: fills are not strictly alternating entry/exit")

    en = ex.iloc[0::2].reset_index(drop=True)
    ez = ex.iloc[1::2].reset_index(drop=True)
    direction = np.where(en.name.to_numpy() == "Long", 1.0, -1.0)
    gross = (ez.price.to_numpy() - en.price.to_numpy()) * direction * pv
    commission = en.commission.to_numpy() + ez.commission.to_numpy()

    t = pd.DataFrame({
        "entry_time": en.time, "exit_time": ez.time,
        "dir": direction.astype(int),
        "entry_price": en.price, "exit_price": ez.price,
        "gross": gross, "commission": commission, "net": gross - commission,
        "bars": ez.bar.to_numpy() - en.bar.to_numpy(),
        "exit_name": ez.name, "wave": en.wave, "signal": en.signal,
    })
    return t, header


def slip(trades, ticks, tick_value=5.0):
    """Analytic slippage overlay: `ticks` per execution, both sides."""
    return trades.net - 2.0 * ticks * tick_value


def _drawdown(equity):
    peak = np.maximum.accumulate(equity)
    dd = equity - peak
    return dd.min() if len(dd) else 0.0


def _time_under_water(daily):
    """Longest run of days below the running equity peak, in calendar days."""
    eq = daily.cumsum()
    peak = eq.cummax()
    under = eq < peak - 1e-9
    if not under.any():
        return 0
    best = cur = 0
    start = None
    for day, flag in under.items():
        if flag:
            if start is None:
                start = day
            cur = (day - start).days
            best = max(best, cur)
        else:
            start = None
    return best


def metrics(trades, net_col="net", label="", ann_days=252):
    """Preregistered Wave-1c metric table for one configuration."""
    if trades.empty:
        return {"label": label, "trades": 0}
    pnl = trades[net_col].to_numpy()
    eq = np.cumsum(pnl)
    wins, losses = pnl[pnl > 0], pnl[pnl < 0]

    daily = trades.set_index(pd.DatetimeIndex(trades.exit_time).normalize())[net_col] \
                  .groupby(level=0).sum().sort_index()
    dstd = daily.std(ddof=1)
    downside = daily[daily < 0]
    sharpe = float(daily.mean() / dstd * np.sqrt(ann_days)) if dstd and dstd > 0 else np.nan
    dsd = downside.std(ddof=1)
    sortino = float(daily.mean() / dsd * np.sqrt(ann_days)) if dsd and dsd > 0 else np.nan
    maxdd = _drawdown(eq)
    years = max((trades.exit_time.iloc[-1] - trades.entry_time.iloc[0]).days / 365.25, 1e-9)
    calmar = float(pnl.sum() / years / abs(maxdd)) if maxdd else np.nan

    order = np.sort(pnl)
    es5 = float(order[: max(1, int(len(order) * 0.05))].mean())
    srt = np.sort(pnl)[::-1]

    yearly = trades.groupby(pd.DatetimeIndex(trades.exit_time).year)[net_col].sum()
    quarterly = trades.groupby(pd.PeriodIndex(trades.exit_time, freq="Q"))[net_col].sum()
    half = trades.groupby(pd.PeriodIndex(trades.exit_time, freq="2Q"))[net_col].sum()

    lo = trades[trades.dir == 1][net_col]
    sh = trades[trades.dir == -1][net_col]

    def pf(x):
        p, n = x[x > 0].sum(), abs(x[x < 0].sum())
        return float(p / n) if n else np.inf

    m = {
        "label": label,
        "trades": int(len(pnl)),
        "net": float(pnl.sum()),
        "avg_trade": float(pnl.mean()),
        "pf": pf(pd.Series(pnl)),
        "win_rate": float((pnl > 0).mean()),
        "max_dd": float(maxdd),
        "calmar": calmar,
        "sharpe_daily": sharpe,
        "sortino_daily": sortino,
        "es5": es5,
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "avg_bars": float(trades.bars.mean()),
        "trading_days": int(len(daily)),
        "tuw_days": int(_time_under_water(daily)),
        "worst_year": float(yearly.min()), "best_year": float(yearly.max()),
        "pos_years": float((yearly > 0).mean()), "n_years": int(len(yearly)),
        "worst_quarter": float(quarterly.min()),
        "pos_quarters": float((quarterly > 0).mean()), "n_quarters": int(len(quarterly)),
        "worst_half": float(half.min()),
        "long_n": int(len(lo)), "long_net": float(lo.sum()), "long_pf": pf(lo),
        "short_n": int(len(sh)), "short_net": float(sh.sum()), "short_pf": pf(sh),
        "top1_share": float(srt[0] / pnl.sum()) if pnl.sum() else np.nan,
        "net_ex_top1": float(pnl.sum() - srt[:1].sum()),
        "net_ex_top3": float(pnl.sum() - srt[:3].sum()),
        "net_ex_top5": float(pnl.sum() - srt[:5].sum()),
        "net_ex_top10": float(pnl.sum() - srt[:10].sum()),
    }
    for y, v in yearly.items():
        m[f"y{y}"] = float(v)
    return m


def daily_vector(trades, net_col="net"):
    """Daily P&L series (for CSCV/PBO matrices and bootstraps)."""
    return trades.set_index(pd.DatetimeIndex(trades.exit_time).normalize())[net_col] \
                 .groupby(level=0).sum().sort_index()
