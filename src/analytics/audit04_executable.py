"""AUDIT-04: executable ensemble construction (E0/E1/E13/E10/E20/E3).

Converts N one-contract member fill ledgers into a single master target-position
process and simulates the executable variants the constitution requires:

    E0  : theoretical strict 1/N mean of member P&L (the published convention)
    E1  : continuous fractional NQ-equivalent target (netting diagnostic)
    E13 : one MNQ per member (N MNQ max), result normalized by N/10 NQ-equivalents
    E10 : round(10 * mean_pos) MNQ, max 10 (practical ~1 NQ-equivalent)
    E20 : round(20 * mean_pos) MNQ / 2 (granularity-convergence diagnostic)
    E3  : mixed NQ/MNQ integer target minimizing rounding error

Mechanics
---------
* Member positions change only at fill timestamps (= bar-open instants, since all
  strategies are Calculate.OnBarClose market-on-close-signal, next-bar-open fill).
* Ledger fill prices embed 1-tick NT8 slippage. The simulator recovers the raw
  bar-open price (price - side*tick) and asserts all members that traded at the
  same instant recovered the SAME raw price.
* The master executes only NET target changes, at raw price, with its own
  slippage (slip_ticks * tick_value per contract) and per-contract commission.
* Equity is bar-level TRUE_MTM: cash + position * close * point_value, sampled at
  each session's last bar.

Cost model (base case)
----------------------
NQ : point $20, tick $5,   commission per side: 2.18  (Lifetime, verified in ledgers)
MNQ: point $2,  tick $0.5, commission per side: from MNQ_COMMISSION_PER_SIDE below —
     MUST be set from the empirical Lifetime-template probe run before results are
     quoted (no published MNQ figure exists in the repo).
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_mtm import read_fills, read_bars, session_date  # noqa: E402

TICK = 0.25
NQ = dict(pv=20.0, tick_value=5.0, comm_side=2.18)
MNQ_COMMISSION_PER_SIDE = None  # set by caller after the Lifetime-template probe
MNQ = dict(pv=2.0, tick_value=0.5, comm_side=None)

BUY = {"Buy", "BuyToCover"}


def member_positions(ledger_paths, bars):
    """Union-timeline member position matrix + raw fill price per physical instant.

    NT8 stamps a market fill with the CLOSE time of the bar in which it filled, but
    the fill executes at that bar's OPEN; session-close engine exits execute AT the
    close (AUDIT-02/03 findings). Events are therefore re-timed to their physical
    instants:
        regular fill stamped T      -> previous bar close + 1ns (the bar's open)
        session-close fill stamped T -> T
    so ffill-valuation at bar closes books each event into the correct bar/session.

    Raw price = de-slipped ledger price (price - side*tick). NT8 caps slippage by
    the fill bar's range, so raw prices at one instant may disagree by up to one
    tick across sides; the per-instant mean is used and the spread asserted <= 0.5.

    Returns (pos: DataFrame[instant x member], rawpx: Series[instant], max_spread)."""
    bidx = bars.index
    shift = {}

    def instant(t, is_sc):
        if is_sc:
            return t
        key = (t, False)
        if key not in shift:
            i = bidx.searchsorted(t)
            if i < len(bidx) and bidx[i] == t and i > 0:
                shift[key] = bidx[i - 1] + pd.Timedelta(1, "ns")
            else:
                shift[key] = t  # boundary quirk: keep stamp
        return shift[key]

    events = {}
    raws = {}
    for i, p in enumerate(ledger_paths):
        f = read_fills(p)
        side = np.where(f.order_action.isin(BUY), 1, -1)
        sc = f.name.eq("Exit on session close").values
        inst = [instant(t, s) for t, s in zip(f.time, sc)]
        f = f.assign(rawpx=f.price - side * TICK, inst=inst)
        events[i] = f.groupby("inst").delta.sum()
        for t, v in f.groupby("inst").rawpx.mean().items():
            raws.setdefault(t, []).append(v)
    spread = max((max(v) - min(v)) for v in raws.values())
    if spread > 0.5 + 1e-9:
        worst = max(raws, key=lambda t: max(raws[t]) - min(raws[t]))
        raise AssertionError(f"raw price spread {spread} at {worst} exceeds cap bound")
    raw = {t: float(np.mean(v)) for t, v in raws.items()}
    idx = sorted(raw)
    pos = pd.DataFrame({i: events[i].reindex(idx).fillna(0.0).cumsum()
                        for i in events}, index=pd.DatetimeIndex(idx))
    return pos, pd.Series(raw).sort_index(), spread


def _target_series(mean_pos, mode, n_members):
    if mode == "E1":
        return mean_pos, "NQ_frac"
    if mode == "E13":
        return mean_pos * n_members, "MNQ"          # one MNQ per member
    if mode == "E10":
        return (mean_pos * 10).round(), "MNQ"
    if mode == "E20":
        return (mean_pos * 20).round(), "MNQ"
    raise ValueError(mode)


def simulate(pos, rawpx, bars, mode, slip_ticks=1, mnq_comm_side=None):
    """Simulate one executable variant. Returns (daily TRUE_MTM Series [session],
    diagnostics dict)."""
    n = pos.shape[1]
    mean_pos = pos.mean(axis=1)

    if mode == "E3":
        # mixed integer: nq + mnq/10 approximates mean_pos; prefer whole NQ blocks
        scaled = (mean_pos * 10).round()
        nq_t = (scaled / 10).round().where(scaled.abs() >= 10, 0.0)
        mnq_t = scaled - nq_t * 10
        legs = {"NQ": (nq_t, NQ), "MNQ": (mnq_t, dict(MNQ, comm_side=mnq_comm_side))}
        norm = 1.0
    else:
        tgt, unit = _target_series(mean_pos, mode, n)
        if unit == "NQ_frac":
            legs = {"NQ": (tgt, NQ)}
            norm = 1.0
        else:
            legs = {"MNQ": (tgt, dict(MNQ, comm_side=mnq_comm_side))}
            norm = {"E13": n / 10.0, "E20": 2.0}.get(mode, 1.0)

    total_comm = total_slip = total_traded = 0.0
    equity_parts = []
    exposure_nq_eq = pd.Series(0.0, index=bars.index)
    for name, (tgt, inst) in legs.items():
        if inst["comm_side"] is None:
            raise RuntimeError("commission per side not set (run the probe first)")
        dq = tgt.diff()
        dq.iloc[0] = tgt.iloc[0]
        traded = dq.abs()
        comm = traded * inst["comm_side"]
        slip = traded * slip_ticks * inst["tick_value"]
        cash = (-dq * rawpx * inst["pv"] - comm - slip).cumsum()
        pos_ff = tgt.reindex(bars.index, method="ffill").fillna(0.0)
        cash_ff = cash.reindex(bars.index, method="ffill").fillna(0.0)
        equity_parts.append(cash_ff + pos_ff * bars.close * inst["pv"])
        exposure_nq_eq = exposure_nq_eq + pos_ff * (inst["pv"] / 20.0)
        total_comm += comm.sum()
        total_slip += slip.sum()
        total_traded += traded.sum()
    equity = sum(equity_parts) / norm
    exposure_nq_eq = exposure_nq_eq / norm

    sess = pd.Series([session_date(t) for t in equity.index], index=equity.index)
    last = equity.groupby(sess.values).tail(1)
    daily = last.diff()
    daily.iloc[0] = last.iloc[0]
    daily.index = [session_date(t) for t in last.index]
    mean_tgt = pos.mean(axis=1).reindex(bars.index, method="ffill").fillna(0.0)
    diags = dict(mode=mode, members=n, contracts_traded=int(round(total_traded)),
                 commission=round(total_comm / norm, 2),
                 slippage=round(total_slip / norm, 2),
                 final_equity=round(equity.iloc[-1], 2),
                 mean_abs_exposure_nq_eq=round(exposure_nq_eq.abs().mean(), 4),
                 max_abs_exposure_nq_eq=round(exposure_nq_eq.abs().max(), 4),
                 position_path_corr=round(exposure_nq_eq.corr(mean_tgt), 6))
    return daily, diags


def e0_daily(ledger_paths, bars):
    """E0 = strict 1/N mean of member TRUE_MTM daily vectors (session basis)."""
    from audit_mtm import daily_conventions
    cols = {}
    for i, p in enumerate(ledger_paths):
        f = read_fills(p)
        out, _cal, _tr, _eq, err = daily_conventions(f, bars)
        assert err < 0.01, f"{p}: MTM identity violated ({err})"
        cols[i] = out.true_mtm
    frame = pd.DataFrame(cols)
    return frame.fillna(0.0).mean(axis=1), frame
