"""TSMOM V1 - FROZEN BEFORE DEVELOPMENT P&L (s8), costed (s9), gated (s10).

EVERYTHING BELOW IS DECLARED BEFORE ANY DEVELOPMENT NUMBER IS READ. No parameter is searched.

SIGNAL (s8), deliberately boring:
    horizons          21 / 63 / 126 / 252 trading days of ECONOMIC return, equally weighted
    score             mean(sign(R_21), sign(R_63), sign(R_126), sign(R_252)) in {-1,-.5,0,+.5,+1}
    no fitted coefficients, no horizon chosen because it wins

VOLATILITY (s8): ONE estimator. 63-day trailing realised sd of the daily USD economic return,
    LAGGED ONE FULL DAY. No estimator zoo.

WEIGHTS (s8): inverse dollar volatility -> equal risk per root inside a sector -> equal risk per
    sector -> score scales exposure. No covariance optimizer, no correlation timing, no
    P1-aware weighting, no dynamic sector rotation. An expert, not an optimizer.

COSTS (s9): charged on signal turnover, daily resizing, roll close and roll reopen.
    one-way per contract = SPREAD_TICKS x tick_value + commission/2
    PRIMARY spread 1 tick, STRESS 2 ticks. commission $4.36 per contract round turn.
    No zero-cost headline. Fractional research positions are used for portfolio science and are
    LABELLED AS SUCH - integer-contract implementation is a later, separate question.

CONTINUATION GATES (s10), fixed here, capable of failing, ALL must pass:
    G1  DEVELOPMENT net P&L at PRIMARY cost > 0
    G2  annualised Sharpe >= 0.30
    G3  positive in >= 6 of the development years
    G4  net still > 0 at STRESS cost
    G5  no single root contributes > 50 % of net
    G6  no single sector contributes > 60 % of net
If V1 fails: RECORD IT. Do not tune horizons, sector weights or the vol lookback.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ncd_day as N                                                        # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
HORIZONS = (21, 63, 126, 252)
VOL_LOOKBACK = 63
TARGET_RISK_USD = 1000.0          # per-sector daily risk budget; a SCALE, not a fitted parameter
COMMISSION_RT = 4.36
DEV_START, DEV_END = "2009-03-30", "2018-12-31"
_fh = open(os.path.join(OUT, "tsmom_v1_dev.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def tick_value(root):
    return None


def build(dev_only=True):
    r = pd.read_parquet(os.path.join(OUT, "economic_returns.parquet"))
    r = r.sort_values(["root", "date"]).reset_index(drop=True)
    tv = {}
    for root in r["root"].unique():
        x = N.read_contract(N.contract_id(root, N.CYCLES[root][0], 2012))
        ts = float(x["tick_size"].iloc[0]) if len(x) else np.nan
        tv[root] = ts * N.PV[root]
    r["tick_usd"] = r["root"].map(tv)

    out = []
    for root, g in r.groupby("root", sort=False):
        g = g.sort_values("date").copy()
        cum = g["ret_usd"].cumsum()
        for h in HORIZONS:
            g[f"sgn_{h}"] = np.sign(cum - cum.shift(h))
            g.loc[g.index[:h], f"sgn_{h}"] = np.nan
        g["score"] = g[[f"sgn_{h}" for h in HORIZONS]].mean(axis=1)
        # LAGGED ONE FULL DAY: the signal and the vol used on day t use data through t-1
        g["score"] = g["score"].shift(1)
        g["vol"] = g["ret_usd"].rolling(VOL_LOOKBACK).std().shift(1)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def run(d, spread_ticks, label):
    d = d[(d["date"] >= DEV_START) & (d["date"] <= DEV_END)].copy()
    d = d[d["eligible"] & d["score"].notna() & d["vol"].notna() & (d["vol"] > 0)]
    # inverse-vol unit, equal risk within sector, equal risk across sectors
    d["inv_vol"] = 1.0 / d["vol"]
    nsec = d.groupby("date")["sector"].transform("nunique")
    nroot = d.groupby(["date", "sector"])["root"].transform("nunique")
    d["q"] = d["score"] * (TARGET_RISK_USD / nsec / nroot) * d["inv_vol"]
    d = d.sort_values(["root", "date"])
    d["q_prev"] = d.groupby("root")["q"].shift(1).fillna(0.0)
    d["dq"] = (d["q"] - d["q_prev"]).abs()
    side_cost = spread_ticks * d["tick_usd"] + COMMISSION_RT / 2.0
    # roll days pay a full close + reopen of the CARRIED position, on top of any resize
    d["cost"] = d["dq"] * side_cost + d["rolled"] * 2.0 * d["q_prev"].abs() * side_cost
    d["gross"] = d["q_prev"] * d["ret_usd"]
    d["net"] = d["gross"] - d["cost"]
    daily = d.groupby("date").agg(gross=("gross", "sum"), cost=("cost", "sum"),
                                  net=("net", "sum"), n=("root", "nunique"))
    return d, daily


def stats(daily):
    x = daily["net"].values
    n = len(x)
    ann = np.sqrt(252)
    sharpe = (x.mean() / x.std(ddof=1) * ann) if x.std(ddof=1) > 0 else np.nan
    cum = np.cumsum(x)
    dd = float(np.max(np.maximum.accumulate(cum) - cum))
    es = float(np.mean(np.sort(x)[:max(1, n // 20)]))
    uw = int((np.maximum.accumulate(cum) - cum > 0).sum())
    return dict(days=n, net=float(x.sum()), per_day=float(x.mean()), sharpe=float(sharpe),
                maxdd=dd, es5=es, underwater_frac=uw / n,
                pos_days=float((x > 0).mean()))


def main():
    d0 = build()
    P("=" * 104)
    P("=== TSMOM V1 - DEVELOPMENT ONLY.  Frozen before this ran. No parameter searched.")
    P(f"=== window {DEV_START} -> {DEV_END}   horizons {HORIZONS}   vol {VOL_LOOKBACK}d lagged 1d")
    P("=" * 104)

    res = {}
    for lab, tk in (("PRIMARY (1 tick)", 1.0), ("STRESS (2 ticks)", 2.0)):
        d, daily = run(d0, tk, lab)
        s = stats(daily)
        res[lab] = (d, daily, s)
        P(f"\n  {lab}")
        P(f"    days {s['days']:,}   net ${s['net']:>14,.0f}   $/day {s['per_day']:>9,.0f}   "
          f"ann Sharpe {s['sharpe']:>6.3f}")
        P(f"    maxDD ${s['maxdd']:>12,.0f}   ES5% ${s['es5']:>10,.0f}   "
          f"positive days {100*s['pos_days']:>5.1f} %   underwater {100*s['underwater_frac']:>5.1f} %")
        P(f"    gross ${daily['gross'].sum():>14,.0f}   cost ${daily['cost'].sum():>12,.0f}   "
          f"cost drag {100*daily['cost'].sum()/max(abs(daily['gross'].sum()),1):>6.1f} % of |gross|")

    d, daily, s = res["PRIMARY (1 tick)"]
    dS = res["STRESS (2 ticks)"][2]

    # ---- yearly
    P("\n  YEARLY (primary)")
    yr = daily.copy()
    yr["y"] = pd.DatetimeIndex(yr.index).year
    ytab = yr.groupby("y").agg(net=("net", "sum"), days=("net", "size"))
    ytab["sharpe"] = yr.groupby("y")["net"].apply(
        lambda x: x.mean() / x.std(ddof=1) * np.sqrt(252) if x.std(ddof=1) > 0 else np.nan)
    P("    " + ytab.to_string().replace("\n", "\n    "))
    pos_years = int((ytab["net"] > 0).sum())

    # ---- attribution
    P("\n  ROOT CONTRIBUTION (primary, top and bottom 5)")
    rc = d.groupby("root")["net"].sum().sort_values(ascending=False)
    tot = rc.sum()
    for k in list(rc.index[:5]) + ["..."] + list(rc.index[-5:]):
        if k == "...":
            P("      ...")
            continue
        P(f"      {k:<5} ${rc[k]:>12,.0f}   {100*rc[k]/tot if tot else 0:>7.1f} % of net")
    sc = d.groupby("sector")["net"].sum().sort_values(ascending=False)
    P("\n  SECTOR CONTRIBUTION (primary)")
    for k in sc.index:
        P(f"      {k:<14} ${sc[k]:>12,.0f}   {100*sc[k]/tot if tot else 0:>7.1f} % of net")
    ls = d.groupby(np.sign(d["q_prev"]))["net"].sum()
    P("\n  LONG vs SHORT (primary)")
    for k, v in ls.items():
        P(f"      {'long' if k > 0 else ('short' if k < 0 else 'flat'):<6} ${v:>12,.0f}")

    # ---- horizon components as DIAGNOSTICS ONLY
    P("\n  HORIZON COMPONENTS - DIAGNOSTIC ONLY, the equal-weight blend remains primary (s10)")
    for h in HORIZONS:
        dh = d0.copy()
        dh["score"] = dh[f"sgn_{h}"].shift(1)
        _, dl = run(dh, 1.0, f"h{h}")
        sh = stats(dl)
        P(f"      {h:>4}d   net ${sh['net']:>13,.0f}   Sharpe {sh['sharpe']:>6.3f}")

    # ---- GATES
    P("\n" + "=" * 104)
    P("=== PREREGISTERED CONTINUATION GATES (declared in the module docstring before this ran)")
    P("=" * 104)
    top_root = float(rc.max() / tot) if tot > 0 else np.inf
    top_sec = float(sc.max() / tot) if tot > 0 else np.inf
    gates = [
        ("G1 net > 0 at PRIMARY cost", s["net"] > 0, f"${s['net']:,.0f}"),
        ("G2 annualised Sharpe >= 0.30", s["sharpe"] >= 0.30, f"{s['sharpe']:.3f}"),
        ("G3 positive in >= 6 of the years", pos_years >= 6, f"{pos_years} of {len(ytab)}"),
        ("G4 net > 0 at STRESS cost", dS["net"] > 0, f"${dS['net']:,.0f}"),
        ("G5 top root <= 50 % of net", top_root <= 0.50, f"{100*top_root:.1f} % ({rc.idxmax()})"),
        ("G6 top sector <= 60 % of net", top_sec <= 0.60, f"{100*top_sec:.1f} % ({sc.idxmax()})"),
    ]
    P(f"    {'gate':<36}{'observed':>26}   verdict")
    P("    " + "-" * 74)
    for name, ok, obs in gates:
        P(f"    {name:<36}{obs:>26}   {'PASS' if ok else '*** FAIL ***'}")
    allpass = all(g[1] for g in gates)
    P("")
    P(f"    ALL GATES: {'PASS -> VALIDATION may be opened ONCE' if allpass else 'FAIL -> RECORD IT. Do NOT tune.'}")
    daily.to_csv(os.path.join(OUT, "tsmom_v1_dev_daily.csv"))
    d.groupby("root")["net"].sum().to_csv(os.path.join(OUT, "tsmom_v1_dev_root.csv"))
    _fh.close()


if __name__ == "__main__":
    main()
