"""test_primary_objective.py — self-test for src/analytics/primary_objective.py.

Runs under plain `python` (no pytest). Prints PASS/FAIL per case and exits non-zero on
any failure.

    python src/analytics/test_primary_objective.py

Cases 3 and 4 are the important ones: they prove this module's bootstrap generators are
the SAME generators that produced the repo's committed capital maps and the published
C-P3 disclosure, by reproducing those committed numbers exactly.
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import primary_objective as PO  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))


def _p(*parts):
    return os.path.join(REPO, *parts)


# --------------------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------------------
INTRADAY_PARQUET = _p("runs", "SMV2AH_DAY_CIRCUIT_BREAKER", "out", "intraday_mtm_series.parquet")


def product_a_series():
    """Product A's research curve: session-end of the committed intraday MTM series
    (column B = DAYONLY_DUAL6040, the research twin of SolarWaveSMMaster_v2)."""
    df = pd.read_parquet(INTRADAY_PARQUET)
    end = df[df["is_last_of_sess"]]
    s = pd.Series(end["intraday_mtm_B"].to_numpy(float),
                  index=pd.to_datetime(end["sess_date"].to_numpy()))
    return s, df


def nq_nt_daily():
    """The exact daily series the committed capital_map_nq.csv was built on."""
    sys.path.insert(0, _p("src", "analytics"))
    from sm01_solarsim import load_bars_3m
    bars = load_bars_3m()
    dev = pd.to_datetime(bars["sess_date"]) <= pd.Timestamp("2026-05-31")
    bd = bars[dev].reset_index(drop=True)
    m = dict(zip(bd["time"], bd["sess_date"]))
    cal = pd.to_datetime(pd.Index(bd.loc[bd["is_last_of_sess"], "sess_date"]))
    nt = pd.read_csv(_p("runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "nt_trades_nq.csv"),
                     parse_dates=["entry_time", "exit_time"])
    nt["sess"] = nt["exit_time"].map(m)
    na = nt.groupby("sess")["pnl"].sum()
    na.index = pd.to_datetime(na.index)
    return na.reindex(cal).fillna(0.0)


# --------------------------------------------------------------------------------------
def case_1_determinism(daily):
    a = PO.primary_objective(daily, n_boot=300, seed=PO.SEED)
    b = PO.primary_objective(daily, n_boot=300, seed=PO.SEED)
    ok = (a["primary"]["objective_J"] == b["primary"]["objective_J"] and
          a["primary"]["p_ruin"] == b["primary"]["p_ruin"] and
          a["primary"]["ce_log_growth_ann"] == b["primary"]["ce_log_growth_ann"])
    check("1 determinism: same seed -> bit-identical J / CE_g / P_ruin", ok,
          f"J={a['primary']['objective_J']:.6f}")


def case_2_seed_sensitivity(daily):
    a = PO.primary_objective(daily, n_boot=300, seed=PO.SEED)
    b = PO.primary_objective(daily, n_boot=300, seed=PO.SEED + 1)
    diff = abs(a["primary"]["p_ruin"] - b["primary"]["p_ruin"])
    ok = diff > 0 and diff < 0.15
    check("2 seed sensitivity: different seed moves P_ruin, but not wildly", ok,
          f"|dP| = {diff:.4f}")


def case_3_capital_map_reproduction():
    x = nq_nt_daily()
    got = PO.reproduce_capital_map(x.to_numpy(float), stress_mults=(1.0,), nb=2000,
                                   seed=PO.SEED)
    ref = pd.read_csv(_p("runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "capital_map_nq.csv"))
    ref = ref[(ref.stress_mult == 1.0) & (ref.thr == 0.10)].set_index("method")
    g = got[(got.stress_mult == 1.0) & (got.thr == 0.10)].set_index("method")
    worst, detail = 0.0, []
    for m in ("L5", "L20", "stat60"):
        d = abs(g.loc[m, "p95_maxdd_dollar"] - ref.loc[m, "p95_maxdd_dollar"])
        worst = max(worst, d)
        detail.append(f"{m} {g.loc[m, 'p95_maxdd_dollar']:.3f} vs {ref.loc[m, 'p95_maxdd_dollar']:.3f}")
    check("3 bootstrap machinery == committed capital_map_nq.csv (all 3 methods)",
          worst < 1e-6, f"max abs diff = {worst:.2e}; " + "; ".join(detail))


def case_4_cp3_reproduction(daily):
    got = PO.reproduce_cp3(daily.to_numpy(float), cap=25_000.0, path_len=504,
                           n_boot=5000, seed=PO.SEED)
    # published in research/system_master/DRAWDOWN_FRONTIER.md (seq 362)
    ok = (abs(got["A_stationary20"] - 0.142) < 0.001 and
          abs(got["B_moving5"] - 0.430) < 0.001)
    check("4 reproduces PUBLISHED C-P3 disclosure 0.142 / 0.430", ok,
          f"stationary20 {got['A_stationary20']:.4f}, moving5 {got['B_moving5']:.4f}")


def case_5_analytic_constant():
    n = 1000
    s = pd.Series(np.full(n, 500.0), index=pd.bdate_range("2022-01-03", periods=n))
    r = PO.primary_objective(s, capital=100_000.0, leverage=1.0, n_boot=100,
                             horizon_sessions=504)
    expect = math.log1p(500.0 / 100_000.0) * PO.ANN
    ok = (abs(r["primary"]["ce_log_growth_ann"] - expect) < 1e-12 and
          r["primary"]["p_ruin"] == 0.0 and
          abs(r["primary"]["objective_J"] - expect) < 1e-12)
    check("5 analytic: constant +$500/day -> CE_g = 252*log1p(0.005), P_ruin = 0", ok,
          f"CE_g={r['primary']['ce_log_growth_ann']:.9f} expected={expect:.9f}")


def case_6_zero_leverage(daily):
    r = PO.primary_objective(daily, leverage=0.0, n_boot=200)
    ok = (r["primary"]["ce_log_growth_ann"] == 0.0 and r["primary"]["p_ruin"] == 0.0
          and r["primary"]["objective_J"] == 0.0)
    check("6 leverage 0 -> zero growth, zero ruin, J = 0", ok)


def case_7_ruin_monotone(daily):
    ps = []
    for L in (0.25, 0.5, 1.0, 2.0):
        r = PO.primary_objective(daily, leverage=L, n_boot=400)
        ps.append(r["primary"]["p_ruin"])
    ok = all(ps[i] <= ps[i + 1] + 1e-12 for i in range(len(ps) - 1))
    check("7 P_ruin is non-decreasing in leverage", ok,
          " -> ".join(f"{p:.3f}" for p in ps))


def case_8_intraday_ge_daily(daily, idf):
    r = PO.primary_objective(daily, leverage=1.0, n_boot=200,
                             intraday_path=idf, intraday_col="intraday_mtm_B")
    d = r["ruin"]["daily_close"]
    i = r["ruin"]["intraday"]
    ok = all(i[m] >= d[m] - 1e-12 for m in PO.DEFAULT_METHODS)
    check("8 intraday P_ruin >= daily-close P_ruin on identical resampled paths", ok,
          "; ".join(f"{m}: {d[m]:.3f} -> {i[m]:.3f}" for m in PO.DEFAULT_METHODS))
    return r


def case_9_intraday_reconciles(r):
    v = r["integrity"].get("intraday_vs_daily_sessionend_maxabs_logdiff")
    ok = v is not None and v < 1e-12
    check("9 intraday session-end log returns == daily log returns (same object)", ok,
          f"max abs log diff = {v:.3e}" if v is not None else "missing")


def case_10_legacy_sharpe(daily):
    sys.path.insert(0, _p("src", "analytics"))
    from smv2_common import dd_battery
    ref = dd_battery(daily.index, daily.to_numpy(float), label="t")["sharpe"]
    got = PO.daily_sharpe(daily.to_numpy(float))
    check("10 legacy Sharpe == smv2_common.dd_battery sharpe", abs(got - ref) < 1e-12,
          f"{got:.9f} vs {ref:.9f}")


def case_11_legacy_cdar(daily):
    x = daily.to_numpy(float)
    dd = np.sort(np.maximum.accumulate(np.cumsum(x)) - np.cumsum(x))[::-1]
    k = max(1, int(0.05 * len(dd)))
    ref = float(dd[:k].mean())            # smv2i_lib.cdar(x, alpha=0.95), inlined
    got = PO.cdar_dollar(x, 0.95)
    check("11 legacy CDaR_0.95($) == smv2i_lib.cdar convention", abs(got - ref) < 1e-9,
          f"${got:,.2f}")


def case_12_locked_forward_guard():
    s = pd.Series([1.0, 2.0, 3.0],
                  index=pd.to_datetime(["2026-07-30", "2026-07-31", "2026-08-05"]))
    try:
        PO.load_daily_pnl(s)
        check("12 LOCKED_FORWARD guard raises on data >= 2026-08-01", False, "no exception")
    except ValueError as e:
        check("12 LOCKED_FORWARD guard raises on data >= 2026-08-01",
              "LOCKED-FORWARD" in str(e), str(e)[:70])


def case_13_dev_truncation():
    p = _p("runs", "SMV2M_MASTER_BUILD", "out", "twin_daily.csv")
    s, flags = PO.load_daily_pnl(p)
    ok = (s.index.max() <= PO.DEV_END and flags["n_truncated_post_dev"] > 0)
    check("13 post-dev sessions truncated and the truncation is recorded", ok,
          f"n={len(s)}, dropped {flags['n_truncated_post_dev']} after {PO.DEV_END.date()}")


def case_14_absorbing_identity(daily):
    """At a leverage low enough that no path ruins, absorbing and non-absorbing growth
    must be identical."""
    r = PO.primary_objective(daily, leverage=0.05, n_boot=200)
    g = r["growth"]["per_method"][PO.DEFAULT_METHODS[0]]
    ok = (r["primary"]["p_ruin"] == 0.0 and
          abs(g["g_ann_mean"] - g["g_ann_nonabsorbing_mean"]) < 1e-12)
    check("14 no ruin -> absorbing growth == non-absorbing growth", ok)


def case_15_fixed_contracts_mode(daily):
    r = PO.primary_objective(daily, leverage=1.0, n_boot=200,
                             leverage_mode="fixed_contracts")
    ok = (np.isfinite(r["primary"]["objective_J"]) and
          0.0 <= r["primary"]["p_ruin"] <= 1.0)
    check("15 fixed_contracts mode runs and returns a finite J", ok,
          f"J={r['primary']['objective_J']:.4f}, P_ruin={r['primary']['p_ruin']:.3f}")


def case_16_min_unit_granularity(daily):
    r = PO.primary_objective(daily, leverage=1.0, n_boot=150, min_unit=1.0)
    ok = np.isfinite(r["primary"]["objective_J"])
    check("16 contract-granularity (min_unit) path runs and returns a finite J", ok,
          f"J={r['primary']['objective_J']:.4f}")


def main():
    t0 = time.time()
    print("primary_objective self-test\n" + "-" * 78)
    daily, idf = product_a_series()
    print(f"fixture: Product A research daily, n={len(daily)}, "
          f"{daily.index.min().date()} .. {daily.index.max().date()}, net ${daily.sum():,.0f}")
    print("-" * 78)

    case_1_determinism(daily)
    case_2_seed_sensitivity(daily)
    case_3_capital_map_reproduction()
    case_4_cp3_reproduction(daily)
    case_5_analytic_constant()
    case_6_zero_leverage(daily)
    case_7_ruin_monotone(daily)
    r = case_8_intraday_ge_daily(daily, idf)
    case_9_intraday_reconciles(r)
    case_10_legacy_sharpe(daily)
    case_11_legacy_cdar(daily)
    case_12_locked_forward_guard()
    case_13_dev_truncation()
    case_14_absorbing_identity(daily)
    case_15_fixed_contracts_mode(daily)
    case_16_min_unit_granularity(daily)

    n_fail = sum(1 for _, ok in RESULTS if not ok)
    print("-" * 78)
    print(f"{len(RESULTS) - n_fail}/{len(RESULTS)} PASS   ({time.time() - t0:.1f}s)")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
