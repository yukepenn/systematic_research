"""C01T2_KSCALE: capital-scale fee-structure curve K=1/2/3 (frozen block rule).

Preregistered in runs/C01T2_KSCALE/spec.yaml (descriptive, no selection).

K=1 : E10 exactly as audited — round(10 * mean_pos) MNQ, all-MNQ. Anchor; must
      reproduce the audited net $179,361.36 BEFORE K=2/K=3 results are read.
K=2 : units = round(20 * mean_pos), clamp [-20, 20]; NQ blocks = trunc(units/10),
      MNQ = remainder; equity / 2 (per-NQ-eq).
K=3 : units = round(30 * mean_pos), clamp [-30, 30]; same block rule; equity / 3.

Costs (per execution per leg, in the LEG instrument's units):
  NQ  : $2.18/side commission + 1 tick slippage @ $5.00/tick per contract
  MNQ : $0.65/side commission + 1 tick slippage @ $0.50/tick per contract

Member positions, fill re-timing, raw-price recovery and TRUE_MTM session
sampling are reused verbatim from the audited simulator
(src/analytics/audit04_executable.py: member_positions + simulate; the K=1
anchor calls simulate() itself, the K=2/K=3 legs replicate its leg loop
line-for-line with the frozen block targets).

Usage: python src/analytics/c01_t2_kscale.py   (CWD = repo root)
Writes: research/04_complementary_family/c01_t2kscale_curve.csv
        runs/C01T2_KSCALE/results.csv
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit03_mtm_run import load_bars                      # noqa: E402
from audit04_executable import (member_positions, simulate,  # noqa: E402
                                NQ, MNQ, session_date)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER_DIR = os.path.join(ROOT, "runs", "AUDIT02_V3_SWEEP_B", "ledgers")
E0_VECTORS = os.path.join(ROOT, "research", "audit", "e_variant_daily_vectors.csv")
MNQ_COMM = 0.65          # verified AUDIT04_MNQ_PROBE (Lifetime template)
AUDITED_E10_NET = 179361.36


def metrics(d):
    d = d.dropna()
    mu, sd = d.mean(), d.std(ddof=1)
    eq = d.cumsum()
    dd = eq - eq.cummax()
    return dict(net=round(d.sum(), 2),
                sharpe=round(0.0 if sd == 0 else mu / sd * np.sqrt(252), 4),
                max_dd=round(dd.min(), 2))


def simulate_blocks(pos, rawpx, bars, K, slip_ticks=1, mnq_comm_side=MNQ_COMM):
    """Frozen block rule at K NQ-eq capital; per-NQ-eq output (equity / K).

    Leg mechanics are a line-for-line replica of audit04_executable.simulate."""
    mean_pos = pos.mean(axis=1)
    units = (mean_pos * 10 * K).round().clip(-10 * K, 10 * K)
    nq_t = pd.Series(np.trunc(units / 10.0), index=units.index)
    mnq_t = units - nq_t * 10
    legs = {"NQ": (nq_t, NQ),
            "MNQ": (mnq_t, dict(MNQ, comm_side=mnq_comm_side))}
    norm = float(K)

    per_leg = {}
    total_comm = total_slip = total_traded = 0.0
    equity_parts = []
    exposure_nq_eq = pd.Series(0.0, index=bars.index)
    for name, (tgt, inst) in legs.items():
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
        per_leg[name] = dict(contracts=int(round(traded.sum())),
                             commission=round(comm.sum(), 2),
                             slippage=round(slip.sum(), 2))
    equity = sum(equity_parts) / norm
    exposure_nq_eq = exposure_nq_eq / norm

    sess = pd.Series([session_date(t) for t in equity.index], index=equity.index)
    last = equity.groupby(sess.values).tail(1)
    daily = last.diff()
    daily.iloc[0] = last.iloc[0]
    daily.index = [session_date(t) for t in last.index]
    mean_tgt = mean_pos.reindex(bars.index, method="ffill").fillna(0.0)
    diags = dict(mode=f"K{K}_blocks", contracts_traded=int(round(total_traded)),
                 commission=round(total_comm / norm, 2),
                 slippage=round(total_slip / norm, 2),
                 mean_abs_exposure_nq_eq=round(exposure_nq_eq.abs().mean(), 4),
                 max_abs_exposure_nq_eq=round(exposure_nq_eq.abs().max(), 4),
                 position_path_corr=round(exposure_nq_eq.corr(mean_tgt), 6),
                 per_leg=per_leg)
    return daily, diags


def corr_with(e0, daily):
    union = e0.index.union(daily.index)
    return e0.reindex(union).fillna(0.0).corr(daily.reindex(union).fillna(0.0))


def main():
    paths = sorted(glob.glob(os.path.join(LEDGER_DIR, "*.csv")))
    assert len(paths) == 13, f"expected 13 member ledgers, got {len(paths)}"
    bars = load_bars()
    pos, rawpx, spread = member_positions(paths, bars)
    print(f"members: {len(paths)}  raw-price max spread: {spread}")

    ev = pd.read_csv(E0_VECTORS, parse_dates=["day"])
    e0 = ev.set_index("day")["E0_session"].dropna()
    e0.index = pd.Index([t.date() for t in e0.index])
    e0_net = round(e0.sum(), 2)
    print(f"E0_session net (reference): {e0_net:,.2f}")

    rows = []

    # ---- K=1 anchor: the audited E10, via the audited simulate() itself ----
    daily1, diag1 = simulate(pos, rawpx, bars, "E10", slip_ticks=1,
                             mnq_comm_side=MNQ_COMM)
    daily1 = daily1.sort_index()
    m1 = metrics(daily1)
    print(f"K=1 (E10 anchor): net {m1['net']:,.2f}  audited {AUDITED_E10_NET:,.2f}")
    assert abs(m1["net"] - AUDITED_E10_NET) < 0.01, \
        f"K=1 anchor FAILED to reproduce audited E10 net: {m1['net']}"
    print("K=1 anchor VERIFIED against audited E10 net — proceeding to K=2/K=3")
    diag1["per_leg"] = {"MNQ": dict(contracts=diag1["contracts_traded"],
                                    commission=diag1["commission"],
                                    slippage=diag1["slippage"])}

    results = {1: (daily1, diag1)}
    for K in (2, 3):
        d, g = simulate_blocks(pos, rawpx, bars, K)
        results[K] = (d.sort_index(), g)

    for K in (1, 2, 3):
        daily, diag = results[K]
        m = metrics(daily)
        c = corr_with(e0, daily)
        pl = diag["per_leg"]
        rows.append(dict(
            K=K,
            net_per_nq_eq=m["net"],
            sharpe=m["sharpe"],
            max_dd=m["max_dd"],
            commission_per_nq_eq=diag["commission"],
            slippage_per_nq_eq=diag["slippage"],
            fee_drag_pct_of_E0_net=round(
                (diag["commission"] + diag["slippage"]) / e0_net * 100, 3),
            corr_with_E0_session=round(c, 6),
            net_vs_E0=round(m["net"] / e0_net, 4),
            nq_contracts_traded=pl.get("NQ", {}).get("contracts", 0),
            mnq_contracts_traded=pl.get("MNQ", {}).get("contracts", 0),
            mean_abs_exposure_nq_eq=diag["mean_abs_exposure_nq_eq"],
            max_abs_exposure_nq_eq=diag["max_abs_exposure_nq_eq"],
            position_path_corr=diag["position_path_corr"],
        ))
        print(f"K={K}: net/NQeq {m['net']:>12,.2f}  sharpe {m['sharpe']:.4f}  "
              f"maxDD {m['max_dd']:>11,.2f}  comm {diag['commission']:>9,.2f}  "
              f"slip {diag['slippage']:>9,.2f}  corr {c:.6f}")

    curve = pd.DataFrame(rows)
    dest1 = os.path.join(ROOT, "research", "04_complementary_family",
                         "c01_t2kscale_curve.csv")
    dest2 = os.path.join(ROOT, "runs", "C01T2_KSCALE", "results.csv")
    curve.to_csv(dest1, index=False)
    curve.to_csv(dest2, index=False)

    s1, s2 = curve.sharpe[curve.K == 1].iloc[0], curve.sharpe[curve.K == 2].iloc[0]
    c2 = curve.corr_with_E0_session[curve.K == 2].iloc[0]
    claim = (s2 - s1 >= 0.03) and (c2 >= 0.998)
    print(f"claim rule: dSharpe(K2-K1) = {s2 - s1:+.4f} (need >= +0.03), "
          f"corr(K2,E0) = {c2:.6f} (need >= 0.998) -> "
          f"{'CLAIM' if claim else 'NO CLAIM'}")
    print("wrote", dest1, "and", dest2)


if __name__ == "__main__":
    main()
