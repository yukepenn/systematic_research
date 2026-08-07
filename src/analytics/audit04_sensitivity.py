"""AUDIT-04 remediation (second red team): E10 micro-choice sensitivity.

The E10 gate pass margin is 0.003 Sharpe. The red team required showing the
verdict is not an artifact of unpreregistered micro-choices:
  1. rounding rule: round() vs floor-toward-zero vs ceil-away-from-zero
  2. daily basis: session TRUE_MTM (used for the gate) vs calendar-date sampling
  3. the E-variant daily P&L vectors must be committed for re-checking.

Writes: research/audit/e_variant_daily_vectors.csv
        research/audit/e10_sensitivity.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit03_mtm_run import load_bars, FAMILIES  # noqa: E402
from audit04_executable import member_positions, simulate, e0_daily, MNQ, NQ  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MNQ_COMM = 0.65


def sharpe(d, ann=252):
    d = d.dropna()
    sd = d.std(ddof=1)
    return 0.0 if sd == 0 else d.mean() / sd * np.sqrt(ann)


def simulate_rule(pos, rawpx, bars, rule):
    """E10 with an alternative integerization rule on 10*mean_pos."""
    mean_pos = pos.mean(axis=1)
    x = mean_pos * 10
    if rule == "round":
        tgt = x.round()
    elif rule == "floor":  # toward zero
        tgt = np.trunc(x)
    elif rule == "ceil":   # away from zero
        tgt = np.sign(x) * np.ceil(x.abs())
    else:
        raise ValueError(rule)
    tgt = pd.Series(tgt, index=x.index)
    dq = tgt.diff(); dq.iloc[0] = tgt.iloc[0]
    traded = dq.abs()
    comm = traded * MNQ_COMM
    slip = traded * 1 * MNQ["tick_value"]
    cash = (-dq * rawpx * MNQ["pv"] - comm - slip).cumsum()
    pos_ff = tgt.reindex(bars.index, method="ffill").fillna(0.0)
    cash_ff = cash.reindex(bars.index, method="ffill").fillna(0.0)
    equity = cash_ff + pos_ff * bars.close * MNQ["pv"]
    return equity, float(comm.sum()), float(slip.sum())


def daily_from_equity(equity, mode):
    from audit_mtm import session_date
    if mode == "session":
        keys = pd.Series([session_date(t) for t in equity.index], index=equity.index)
    else:  # calendar-date sampling at each date's last bar
        keys = pd.Series([t.date() for t in equity.index], index=equity.index)
    last = equity.groupby(keys.values).tail(1)
    d = last.diff(); d.iloc[0] = last.iloc[0]
    d.index = keys.loc[last.index].values
    return d


def main():
    bars = load_bars()
    paths = FAMILIES["R5_adaptive_13"]
    e0_sess, _ = e0_daily(paths, bars)
    pos, rawpx, _ = member_positions(paths, bars)

    # E0 calendar-basis: rebuild member equities and sample at calendar days
    from audit_mtm import read_fills, daily_conventions
    e0_cal_cols = {}
    eq_cols = {}
    for i, p in enumerate(paths):
        f = read_fills(p)
        out, cal, trades, eq, err = daily_conventions(f, bars)
        eq_cols[i] = eq.equity
        e0_cal_cols[i] = daily_from_equity(eq.equity, "calendar")
    e0_cal = pd.DataFrame(e0_cal_cols).fillna(0.0).mean(axis=1)

    rows = []
    vectors = {"E0_session": e0_sess, "E0_calendar_mtm": e0_cal}
    for rule in ["round", "floor", "ceil"]:
        equity, comm, slip = simulate_rule(pos, rawpx, bars, rule)
        for basis in ["session", "calendar"]:
            d = daily_from_equity(equity, basis)
            ref = e0_sess if basis == "session" else e0_cal
            rows.append(dict(rule=rule, basis=basis,
                             net=round(d.sum(), 2),
                             sharpe=round(sharpe(d), 4),
                             e0_sharpe=round(sharpe(ref), 4),
                             delta=round(sharpe(d) - sharpe(ref), 4),
                             gate_pass=bool(sharpe(d) - sharpe(ref) >= -0.10),
                             commission=round(comm, 2), slippage=round(slip, 2)))
        vectors[f"E10_{rule}_session"] = daily_from_equity(equity, "session")

    sens = pd.DataFrame(rows)
    sens.to_csv(os.path.join(ROOT, "research", "audit", "e10_sensitivity.csv"), index=False)
    print(sens.to_string(index=False))

    # commit-able daily vectors (session basis) for E0 and the three E10 rules,
    # plus the primary E-variants from the main run for completeness
    for mode in ["E1", "E13", "E20", "E3"]:
        d, _ = simulate(pos, rawpx, bars, mode, slip_ticks=1, mnq_comm_side=MNQ_COMM)
        vectors[f"{mode}_session"] = d
    vec = pd.DataFrame({k: pd.Series(v.values, index=pd.Index(v.index).astype(str))
                        for k, v in vectors.items()})
    vec.index.name = "day"
    vec.to_csv(os.path.join(ROOT, "research", "audit", "e_variant_daily_vectors.csv"))
    print("wrote e10_sensitivity.csv, e_variant_daily_vectors.csv")


if __name__ == "__main__":
    main()
