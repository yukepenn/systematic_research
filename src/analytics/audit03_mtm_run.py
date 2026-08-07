"""AUDIT-03 runner: three-way daily P&L reconciliation for R5 (13 members) and
R4 (21 members) plus bar-level TRUE_MTM statistics.

Conventions compared per ensemble (strict 1/N, flat days as zero, each on the
ensemble's own traded-day union):
    calendar  = round-trip net on CALENDAR date of exit  (published basis, REALIZED_ONLY)
    session   = round-trip net on NT8 session date       (REALIZED_ONLY)
    true_mtm  = bar-level equity sampled at each session's last bar (TRUE_MTM)

Audit checks enforced:
    * per-member |true_mtm - session| == 0 (to the cent) — the flat-at-close identity
      is PROVEN, not assumed;
    * per-member total equals the ledger round-trip net.

TRUE_MTM-only extras: bar-level (intraday) ensemble max drawdown vs daily max
drawdown under each convention.

Usage: python src/analytics/audit03_mtm_run.py   (CWD = repo root)
Writes: research/audit/mtm_reconciliation_metrics.csv
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_mtm import read_fills, daily_conventions  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BARS = os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv")

FAMILIES = {
    "R5_adaptive_13": sorted(glob.glob(os.path.join(
        ROOT, "research", "05_open_axes", "h006", "h006__*.csv"))),
    "R4_fixed_21": sorted(glob.glob(os.path.join(
        ROOT, "research", "02_solar_refinements", "wave1c", "ledgers",
        "w1c__tf3_*_sc_slip1_*.csv")))
    + sorted(glob.glob(os.path.join(ROOT, "research", "05_open_axes", "fixedwide", "*.csv"))),
}


def load_bars():
    bars = pd.read_csv(BARS, parse_dates=["time"]).set_index("time").sort_index()
    # known exporter quirk: the very last boundary bar (2026-07-31 17:00) is absent.
    # Every strategy is flat after that instant, so the mark price is irrelevant;
    # the bar must merely exist so the final session-close cash lands in-session.
    t = pd.Timestamp("2026-07-31 17:00:00")
    if t not in bars.index:
        bars.loc[t] = bars.iloc[-1]
        bars = bars.sort_index()
    return bars


def stats(d, label, basis):
    d = d.dropna()
    mu, sd = d.mean(), d.std(ddof=1)
    dn = d[d < 0].std(ddof=1)
    eq = d.cumsum()
    dd = eq - eq.cummax()
    idx = pd.DatetimeIndex(pd.to_datetime(d.index))
    dts = pd.Series(d.values, index=idx)
    return {
        "ensemble": label, "basis": basis, "n_days": len(d),
        "net": round(d.sum(), 2),
        "sharpe": round(0.0 if sd == 0 else mu / sd * np.sqrt(252), 4),
        "sortino": round(0.0 if dn == 0 else mu / dn * np.sqrt(252), 4),
        "max_dd_daily": round(dd.min(), 2),
        "calmar": round((mu * 252) / abs(dd.min()), 4) if dd.min() else np.nan,
        "es5": round(d[d <= d.quantile(0.05)].mean(), 2),
        "tuw_days": int((dd < 0).sum()),
        "worst_day": round(d.min(), 2),
        "worst_week": round(dts.resample("W").sum().min(), 2),
        "worst_month": round(dts.resample("ME").sum().min(), 2),
        "worst_quarter": round(dts.resample("QE").sum().min(), 2),
    }


def main():
    bars = load_bars()
    rows = []
    for label, paths in FAMILIES.items():
        print(f"{label}: {len(paths)} members")
        cal_v, ses_v, mtm_v, eq_bars = {}, {}, {}, {}
        for p in paths:
            f = read_fills(p)
            out, cal, trades, eq, err = daily_conventions(f, bars)
            name = os.path.basename(p)
            assert err < 0.01, f"{name}: TRUE_MTM vs session identity violated ({err:.4f})"
            ledger_net = trades.net.sum()
            assert abs(out.true_mtm.sum() - ledger_net) < 0.01, \
                f"{name}: MTM total {out.true_mtm.sum():.2f} != ledger net {ledger_net:.2f}"
            cal_v[name], ses_v[name], mtm_v[name] = cal, out.session_realized, out.true_mtm
            eq_bars[name] = eq.equity
        for basis, vecs in [("calendar_REALIZED", cal_v),
                            ("session_REALIZED", ses_v),
                            ("session_TRUE_MTM", mtm_v)]:
            union = sorted(set().union(*[v.index for v in vecs.values()]))
            frame = pd.DataFrame({k: v.reindex(union).fillna(0.0) for k, v in vecs.items()})
            ens = frame.mean(axis=1)
            rows.append(stats(ens, label, basis))
        # bar-level intraday ensemble drawdown (TRUE_MTM only)
        eqf = pd.DataFrame(eq_bars).ffill().fillna(0.0)
        ens_eq = eqf.mean(axis=1)
        dd = (ens_eq - ens_eq.cummax()).min()
        rows.append({"ensemble": label, "basis": "bar_level_TRUE_MTM",
                     "n_days": ens_eq.groupby(
                         [t.date() for t in ens_eq.index]).ngroups,
                     "net": round(ens_eq.iloc[-1], 2), "sharpe": np.nan,
                     "sortino": np.nan, "max_dd_daily": round(dd, 2),
                     "calmar": np.nan, "es5": np.nan, "tuw_days": np.nan,
                     "worst_day": np.nan, "worst_week": np.nan,
                     "worst_month": np.nan, "worst_quarter": np.nan})
    out = pd.DataFrame(rows)
    dest = os.path.join(ROOT, "research", "audit", "mtm_reconciliation_metrics.csv")
    out.to_csv(dest, index=False)
    print(out.to_string(index=False))
    print("wrote", dest)


if __name__ == "__main__":
    main()
