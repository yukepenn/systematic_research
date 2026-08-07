"""AUDIT-04 runner: executable ensembles for R5 (13 members) and R4 (21 members).

Variants per family (constitution §8 / thesis AUDIT-04):
    E0   theoretical strict 1/N member-P&L mean (session TRUE_MTM basis)
    E1   continuous fractional NQ-equivalent target (netting diagnostic)
    E13  one MNQ per member (N members -> max N MNQ), normalized by N/10
    E10  round(10 * mean_pos) MNQ, max 10  (practical ~1 NQ-equivalent)
    E20  round(20 * mean_pos) MNQ / 2      (granularity diagnostic)
    E3   mixed NQ/MNQ integer target

Cost model: NQ $2.18/side, tick $5; MNQ $0.65/side (verified AUDIT04_MNQ_PROBE),
tick $0.50; 1 tick slippage per execution per contract on net target changes.

Gates (preregistered in the thesis AUDIT-04 §9):
    executable Sharpe >= E0 Sharpe - 0.10
    net retained >= 80% of E0
    max DD no more than 20% worse than E0
    mean |exposure| <= ~1 NQ-equivalent (no hidden leverage)
    top-10 E0 days materially retained

Usage: python src/analytics/audit04_run.py   (CWD = repo root)
Writes: research/audit/executable_ensemble_metrics.csv
        research/audit/netting_cost_attribution.csv
        research/audit/position_rounding_diagnostics.csv
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit03_mtm_run import load_bars, FAMILIES  # noqa: E402
from audit04_executable import member_positions, simulate, e0_daily  # noqa: E402
from audit_mtm import read_fills  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MNQ_COMM = 0.65

MODES = ["E1", "E13", "E10", "E20", "E3"]


def metrics(d):
    d = d.dropna()
    mu, sd = d.mean(), d.std(ddof=1)
    eq = d.cumsum()
    dd = eq - eq.cummax()
    return dict(net=round(d.sum(), 2),
                sharpe=round(0.0 if sd == 0 else mu / sd * np.sqrt(252), 4),
                max_dd=round(dd.min(), 2),
                es5=round(d[d <= d.quantile(0.05)].mean(), 2),
                tuw=int((dd < 0).sum()),
                worst_day=round(d.min(), 2))


def main():
    bars = load_bars()
    rows, costs, rounding = [], [], []
    for label, paths in FAMILIES.items():
        n = len(paths)
        print(f"=== {label} ({n} members) ===")
        e0, member_frame = e0_daily(paths, bars)
        e0 = e0.sort_index()
        m0 = metrics(e0)
        top10 = e0.nlargest(10)
        rows.append(dict(ensemble=label, mode="E0", **m0,
                         daily_corr_with_E0=1.0, net_vs_E0=1.0,
                         sharpe_delta_vs_E0=0.0, dd_vs_E0=1.0,
                         top10_day_retention=1.0, position_path_corr=1.0,
                         mean_abs_exposure_nq_eq=np.nan, commission=np.nan,
                         slippage=np.nan, contracts_traded=np.nan,
                         gates="reference"))
        # embedded theoretical costs of E0 (per NQ-equivalent unit)
        comm_tot = slip_execs = 0.0
        for p in paths:
            f = read_fills(p)
            comm_tot += f.commission.sum()
            slip_execs += len(f)
        costs.append(dict(ensemble=label, variant="E0_theoretical",
                          commission=round(comm_tot / n, 2),
                          slippage_at_1tick=round(slip_execs * 5.0 / n, 2),
                          note="1/N share of member-level costs embedded in ledger prices"))

        pos, rawpx, spread = member_positions(paths, bars)
        print(f"raw-price max cross-member spread: {spread}")
        for mode in MODES:
            daily, diag = simulate(pos, rawpx, bars, mode, slip_ticks=1,
                                   mnq_comm_side=MNQ_COMM)
            daily = daily.sort_index()
            m = metrics(daily)
            union = e0.index.union(daily.index)
            a = e0.reindex(union).fillna(0.0)
            b = daily.reindex(union).fillna(0.0)
            corr = a.corr(b)
            ret10 = b.reindex(top10.index).sum() / top10.sum()
            gates = []
            if m["sharpe"] < m0["sharpe"] - 0.10: gates.append("SHARPE_FAIL")
            if m["net"] < 0.80 * m0["net"]: gates.append("NET_FAIL")
            if abs(m["max_dd"]) > 1.20 * abs(m0["max_dd"]): gates.append("DD_FAIL")
            if diag["mean_abs_exposure_nq_eq"] > 1.05: gates.append("EXPOSURE_FAIL")
            if ret10 < 0.85: gates.append("TOP10_FAIL")
            rows.append(dict(ensemble=label, mode=mode, **m,
                             daily_corr_with_E0=round(corr, 4),
                             net_vs_E0=round(m["net"] / m0["net"], 4),
                             sharpe_delta_vs_E0=round(m["sharpe"] - m0["sharpe"], 4),
                             dd_vs_E0=round(m["max_dd"] / m0["max_dd"], 4),
                             top10_day_retention=round(ret10, 4),
                             position_path_corr=diag["position_path_corr"],
                             mean_abs_exposure_nq_eq=diag["mean_abs_exposure_nq_eq"],
                             commission=diag["commission"],
                             slippage=diag["slippage"],
                             contracts_traded=diag["contracts_traded"],
                             gates=";".join(gates) if gates else "PASS"))
            costs.append(dict(ensemble=label, variant=mode,
                              commission=diag["commission"],
                              slippage_at_1tick=diag["slippage"],
                              note=f"netted executable costs, {diag['contracts_traded']} contracts traded"))
            print(f"{mode}: net {m['net']:>12,.2f}  sharpe {m['sharpe']:.4f}  "
                  f"corr {corr:.4f}  gates {rows[-1]['gates']}")
        # rounding diagnostics: distribution of |target error| for E10/E20/E13
        mean_pos = pos.mean(axis=1)
        for mode, scale in [("E13", n), ("E10", 10), ("E20", 20)]:
            tgt = (mean_pos * scale).round() / scale if mode != "E13" else mean_pos
            err = (tgt - mean_pos).abs()
            rounding.append(dict(ensemble=label, mode=mode,
                                 mean_abs_rounding_err_nq_eq=round(err.mean(), 5),
                                 max_abs_rounding_err_nq_eq=round(err.max(), 5)))

    pd.DataFrame(rows).to_csv(os.path.join(
        ROOT, "research", "audit", "executable_ensemble_metrics.csv"), index=False)
    pd.DataFrame(costs).to_csv(os.path.join(
        ROOT, "research", "audit", "netting_cost_attribution.csv"), index=False)
    pd.DataFrame(rounding).to_csv(os.path.join(
        ROOT, "research", "audit", "position_rounding_diagnostics.csv"), index=False)
    print("wrote executable_ensemble_metrics.csv, netting_cost_attribution.csv, "
          "position_rounding_diagnostics.csv")


if __name__ == "__main__":
    main()
