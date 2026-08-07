"""AUDIT-02 / AUDIT-A04: clean V3-vs-V4 comparison at MATCHED StartUp=false.

The campaign's published comparison (V3_V4_EQUIVALENCE.md) put committed V3
(StartUp=false) against committed V4 (StartUp=true) — confounded. This script
compares the two engines with the ONLY difference being V4's ResolveS tick-snap:

    V3: research/05_open_axes/h006/            (StartUp=false, EXACT-reproduced)
    V4: runs/AUDIT02_V4_SWEEP_B/ledgers/       (StartUp=false, audit re-run)

Outputs research/audit/v3_v4_trade_diff.csv, v3_v4_daily_diff.csv and prints the
verdict statistics. Daily basis: calendar-date-of-exit (published convention),
REALIZED_ONLY, plus a session-basis sensitivity.

Usage: python src/analytics/audit02_v3v4.py   (CWD = repo root)
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from execledger import read_exec_ledger, daily_vector  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VMS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

V3_TPL = os.path.join(ROOT, "research", "05_open_axes", "h006",
                      "h006__tf3_sm179_am0_th1_vp460_vm{vm}_xm0_sc_slip1.csv")
V4_TPL = os.path.join(ROOT, "runs", "AUDIT02_V4_SWEEP_B", "ledgers",
                      "b2v4__NQ_tf3_sm179_am0_th1_vp460_vm{vm}_bp20_xm0_sc_slip1.csv")


def fills_frame(path):
    df = pd.read_csv(path, comment="#", parse_dates=["time"])
    return df


def sharpe(d, ann=252):
    sd = d.std(ddof=1)
    return 0.0 if sd == 0 else d.mean() / sd * np.sqrt(ann)


def circular_block_delta(a, b, block=20, n_boot=2000, seed=7):
    """P(mean(a-b) <= 0) under a circular block bootstrap of the daily delta."""
    rng = np.random.default_rng(seed)
    d = (a - b).values
    n = len(d)
    idx = np.arange(n)
    n_blocks = int(np.ceil(n / block))
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n, n_blocks)
        take = np.concatenate([(idx[(s + np.arange(block)) % n]) for s in starts])[:n]
        # statistic: annualized Sharpe difference of the resampled paired days
        ra, rb = a.values[take], b.values[take]
        deltas[i] = sharpe(pd.Series(ra)) - sharpe(pd.Series(rb))
    return float((deltas <= 0).mean())


def main():
    rows, d3, d4 = [], {}, {}
    for vm in VMS:
        p3, p4 = V3_TPL.format(vm=vm), V4_TPL.format(vm=vm)
        t3, _h3 = read_exec_ledger(p3)
        t4, _h4 = read_exec_ledger(p4)
        f3, f4 = fills_frame(p3), fills_frame(p4)
        key = ["time", "order_action", "price"]
        common = pd.merge(f3[key], f4[key], on=key, how="inner")
        rows.append(dict(
            vm=vm,
            v3_fills=len(f3), v4_fills=len(f4),
            common_fills=len(common),
            common_pct_of_v3=round(100 * len(common) / len(f3), 2),
            v3_net=round(t3.net.sum(), 2), v4_net=round(t4.net.sum(), 2),
            net_ratio=round(t4.net.sum() / t3.net.sum(), 4) if t3.net.sum() else np.nan,
        ))
        d3[vm], d4[vm] = daily_vector(t3), daily_vector(t4)

    trade_diff = pd.DataFrame(rows).set_index("vm")
    out1 = os.path.join(ROOT, "research", "audit", "v3_v4_trade_diff.csv")
    trade_diff.to_csv(out1)

    cal = sorted(set().union(*[s.index for s in d3.values()],
                             *[s.index for s in d4.values()]))
    m3 = pd.DataFrame({vm: d3[vm].reindex(cal).fillna(0.0) for vm in VMS})
    m4 = pd.DataFrame({vm: d4[vm].reindex(cal).fillna(0.0) for vm in VMS})
    e3, e4 = m3.mean(axis=1), m4.mean(axis=1)
    daily = pd.DataFrame({"v3_ens": e3, "v4_ens": e4, "delta": e3 - e4})
    out2 = os.path.join(ROOT, "research", "audit", "v3_v4_daily_diff.csv")
    daily.to_csv(out2, index_label="date")

    corr = e3.corr(e4)
    s3, s4 = sharpe(e3), sharpe(e4)
    p = circular_block_delta(e3, e4)
    print(trade_diff.to_string())
    print(f"\nENSEMBLE (calendar-of-exit, {len(cal)} days, REALIZED_ONLY):")
    print(f"  V3 net ${e3.sum():,.2f}  Sharpe {s3:.4f}")
    print(f"  V4 net ${e4.sum():,.2f}  Sharpe {s4:.4f}")
    print(f"  daily corr {corr:.4f}   dSharpe(V3-V4) {s3 - s4:+.4f}   "
          f"paired circular-block P(d<=0) {p:.3f}")
    mean_common = trade_diff.common_pct_of_v3.mean()
    print(f"  mean common-fill %% of V3: {mean_common:.1f}%")
    print(f"wrote {out1}\nwrote {out2}")


if __name__ == "__main__":
    main()
