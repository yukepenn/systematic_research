"""TSMOM V2 - SLOW TREND (252-day only).  ONE-SHOT VALIDATION on 2019-01-01 -> 2022-12-31.

V2 INHERITS V1'S MACHINERY EXACTLY. ONE THING CHANGES:

    V1 signal:  mean(sign(R21), sign(R63), sign(R126), sign(R252))
    V2 signal:  sign(R252)                                          <-- the ONLY difference

Unchanged, deliberately and completely: the 21 CORE roots, per-root/date eligibility, 252-day
warmup, the true unmerged .ncd substrate, the causal roll engine and its pre-expiry fallback, the
self-financing basis-safe P&L, the 63-day lagged volatility estimator, inverse-vol / equal-risk
sector sizing, daily rebalance, fractional research sizing, the $4.36 commission, the PRIMARY
(1 tick) and STRESS (2 tick) cost assumptions, long/short symmetry, and sector membership.

NO ROOT IS REMOVED because it hurt V1. NO SHORT LEG IS REMOVED because longs looked better.
NO EQUITY OVERLAY IS ADDED because equities dominated V1. Those are future hypotheses, not V2.

*** EVIDENCE PROVENANCE, WHICH TRAVELS WITH EVERY NUMBER THIS PRODUCES ***

    DEVELOPMENT-DERIVED
    SELECTED AFTER INSPECTING THE FOUR PREDECLARED V1 COMPONENTS
    ONE-OF-FOUR DISCOVERY
    NOT CLEAN DEVELOPMENT EVIDENCE

    Its development diagnostic (net $25,757, Sharpe 0.479) is DISCOVERY, not evidence. The
    untouched 2019-2022 validation is how the post-hoc selection debt is paid - not a haircut,
    not a winner's-curse adjustment, an actual independent window.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pandas as pd

MM = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "research", "multi_market")
sys.path.insert(0, os.path.join(MM, "src"))
import ncd_day as N                                                        # noqa: E402

SUB = os.path.join(MM, "out", "economic_returns.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

# ---- INHERITED FROM V1, UNCHANGED
VOL_LOOKBACK = 63
TARGET_RISK_USD = 1000.0
COMMISSION_RT = 4.36
# ---- THE ONE CHANGE
HORIZON = 252

VAL_START, VAL_END = "2019-01-01", "2022-12-31"
HOLDOUT_START = "2023-01-01"          # BLOCKED during validation
GLOBAL_SEAL = "2026-08-01"            # BLOCKED everywhere in this lane
_fh = open(os.path.join(OUT, "tsmom_v2_validation.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def build():
    r = pd.read_parquet(SUB).sort_values(["root", "date"]).reset_index(drop=True)
    # ---------------- BLOCKING ASSERTIONS (s3 of the directive)
    assert pd.Timestamp(r["date"].max()) < pd.Timestamp(GLOBAL_SEAL), \
        "SEAL VIOLATION: substrate contains data at or beyond 2026-08-01"
    tv = {}
    for root in r["root"].unique():
        x = N.read_contract(N.contract_id(root, N.CYCLES[root][0], 2012))
        tv[root] = float(x["tick_size"].iloc[0]) * N.PV[root] if len(x) else np.nan
    r["tick_usd"] = r["root"].map(tv)
    out = []
    for root, g in r.groupby("root", sort=False):
        g = g.sort_values("date").copy()
        cum = g["ret_usd"].cumsum()
        g["score"] = np.sign(cum - cum.shift(HORIZON))          # <-- THE ONLY CHANGE vs V1
        g.loc[g.index[:HORIZON], "score"] = np.nan
        g["score"] = g["score"].shift(1)                         # lagged one full day, as V1
        g["vol"] = g["ret_usd"].rolling(VOL_LOOKBACK).std().shift(1)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def run(d, spread_ticks, start, end):
    d = d[(d["date"] >= start) & (d["date"] <= end)].copy()
    assert pd.Timestamp(d["date"].max()) < pd.Timestamp(HOLDOUT_START), \
        "HOLDOUT VIOLATION: validation attempted to load data at or beyond 2023-01-01"
    d = d[d["eligible"] & d["score"].notna() & d["vol"].notna() & (d["vol"] > 0)]
    d["inv_vol"] = 1.0 / d["vol"]
    nsec = d.groupby("date")["sector"].transform("nunique")
    nroot = d.groupby(["date", "sector"])["root"].transform("nunique")
    d["q"] = d["score"] * (TARGET_RISK_USD / nsec / nroot) * d["inv_vol"]
    d = d.sort_values(["root", "date"])
    d["q_prev"] = d.groupby("root")["q"].shift(1).fillna(0.0)
    d["dq"] = (d["q"] - d["q_prev"]).abs()
    side = spread_ticks * d["tick_usd"] + COMMISSION_RT / 2.0
    d["cost"] = d["dq"] * side + d["rolled"] * 2.0 * d["q_prev"].abs() * side
    d["gross"] = d["q_prev"] * d["ret_usd"]
    d["net"] = d["gross"] - d["cost"]
    daily = d.groupby("date").agg(gross=("gross", "sum"), cost=("cost", "sum"),
                                  net=("net", "sum"), n=("root", "nunique"))
    return d, daily


def stats(daily):
    x = daily["net"].values
    n = len(x)
    sd = x.std(ddof=1)
    cum = np.cumsum(x)
    return dict(days=n, net=float(x.sum()), per_day=float(x.mean()),
                sharpe=float(x.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan,
                maxdd=float(np.max(np.maximum.accumulate(cum) - cum)),
                es5=float(np.mean(np.sort(x)[:max(1, n // 20)])),
                underwater=float((np.maximum.accumulate(cum) - cum > 0).mean()),
                pos_days=float((x > 0).mean()))


def share_of_positive(series):
    """DECLARED BEFORE THE RUN (directive s4): concentration is measured as a share of the sum of
    POSITIVE contributions, which stays well defined when total net is near zero or negative."""
    pos = series[series > 0].sum()
    if pos <= 0:
        return np.nan, None
    return float(series.max() / pos), series.idxmax()


def main():
    P("=" * 104)
    P("=== TSMOM V2 - SLOW TREND (252d only).  ONE-SHOT VALIDATION.")
    P(f"=== window {VAL_START} -> {VAL_END}   holdout >= {HOLDOUT_START} BLOCKED by assertion")
    P("=" * 104)
    P("    ⚠️ PROVENANCE, attached to every number below:")
    P("       DEVELOPMENT-DERIVED / SELECTED AFTER INSPECTING FOUR PREDECLARED V1 COMPONENTS /")
    P("       ONE-OF-FOUR DISCOVERY / NOT CLEAN DEVELOPMENT EVIDENCE.")
    P("       This untouched window IS the payment for that selection.")

    for f in ("ncd_day.py", "roll.py", "build_substrate.py"):
        h = hashlib.sha256(open(os.path.join(MM, "src", f), "rb").read()).hexdigest()
        P(f"    {f:<22} sha256 {h}")
    P(f"    {'economic_returns.parquet':<22} sha256 "
      f"{hashlib.sha256(open(SUB,'rb').read()).hexdigest()}")
    P(f"    {'THIS FILE':<22} sha256 "
      f"{hashlib.sha256(open(os.path.abspath(__file__),'rb').read()).hexdigest()}")

    d0 = build()
    res = {}
    for lab, tk in (("PRIMARY", 1.0), ("STRESS", 2.0)):
        d, daily = run(d0, tk, VAL_START, VAL_END)
        res[lab] = (d, daily, stats(daily))
    d, daily, s = res["PRIMARY"]
    sS = res["STRESS"][2]

    P("")
    P("=" * 104)
    P("=== VALIDATION RESULT  2019-01-01 -> 2022-12-31")
    P("=" * 104)
    for lab in ("PRIMARY", "STRESS"):
        _, dl, st = res[lab]
        P(f"    {lab:<8} days {st['days']:,}  net ${st['net']:>12,.0f}  Sharpe {st['sharpe']:>6.3f}"
          f"  maxDD ${st['maxdd']:>10,.0f}  ES5% ${st['es5']:>8,.0f}"
          f"  pos days {100*st['pos_days']:>5.1f}%  underwater {100*st['underwater']:>5.1f}%")
        P(f"    {'':<8} gross ${dl['gross'].sum():>12,.0f}  cost ${dl['cost'].sum():>10,.0f}"
          f"  cost drag {100*dl['cost'].sum()/max(abs(dl['gross'].sum()),1):>6.1f}% of |gross|")

    yr = daily.copy()
    yr["y"] = pd.DatetimeIndex(yr.index).year
    ytab = yr.groupby("y")["net"].agg(["sum", "size"])
    ytab["sharpe"] = yr.groupby("y")["net"].apply(
        lambda x: x.mean() / x.std(ddof=1) * np.sqrt(252) if x.std(ddof=1) > 0 else np.nan)
    P("\n  YEARLY (primary)")
    P("    " + ytab.to_string().replace("\n", "\n    "))
    pos_years = int((ytab["sum"] > 0).sum())

    rc = d.groupby("root")["net"].sum().sort_values(ascending=False)
    sc = d.groupby("sector")["net"].sum().sort_values(ascending=False)
    r_share, r_who = share_of_positive(rc)
    s_share, s_who = share_of_positive(sc)
    P("\n  ROOT CONTRIBUTION (top 5 / bottom 5)")
    for k in list(rc.index[:5]):
        P(f"      {k:<5} ${rc[k]:>12,.0f}")
    P("      ...")
    for k in list(rc.index[-5:]):
        P(f"      {k:<5} ${rc[k]:>12,.0f}")
    P("\n  SECTOR CONTRIBUTION")
    for k in sc.index:
        P(f"      {k:<14} ${sc[k]:>12,.0f}")
    ls = d.groupby(np.sign(d["q_prev"]))["net"].sum()
    P("\n  LONG vs SHORT")
    for k, v in ls.items():
        P(f"      {'long' if k > 0 else ('short' if k < 0 else 'flat'):<6} ${v:>12,.0f}")
    x = np.sort(daily["net"].values)[::-1]
    tot = daily["net"].sum()
    P(f"\n  CONCENTRATION  top-1 day {100*x[0]/tot if tot else 0:>7.1f}%   "
      f"top-5 days {100*x[:5].sum()/tot if tot else 0:>7.1f}%   of net")

    P("")
    P("=" * 104)
    P("=== PREREGISTERED VALIDATION GATES (fixed in SPEC.md before this ran)")
    P("=" * 104)
    gates = [
        ("V2-G1 PRIMARY net > 0", s["net"] > 0, f"${s['net']:,.0f}"),
        ("V2-G2 annualised Sharpe >= 0.30", s["sharpe"] >= 0.30, f"{s['sharpe']:.3f}"),
        ("V2-G3 positive in >= 3 of 4 years", pos_years >= 3, f"{pos_years} of {len(ytab)}"),
        ("V2-G4 STRESS net > 0", sS["net"] > 0, f"${sS['net']:,.0f}"),
        ("V2-G5 top root <= 50 % of positive net", (r_share == r_share) and r_share <= 0.50,
         f"{100*r_share:.1f} % ({r_who})" if r_share == r_share else "undefined"),
        ("V2-G6 top sector <= 60 % of positive net", (s_share == s_share) and s_share <= 0.60,
         f"{100*s_share:.1f} % ({s_who})" if s_share == s_share else "undefined"),
    ]
    P(f"    {'gate':<42}{'observed':>26}   verdict")
    P("    " + "-" * 80)
    for nm, ok, obs in gates:
        P(f"    {nm:<42}{obs:>26}   {'PASS' if ok else '*** FAIL ***'}")
    allpass = all(g[1] for g in gates)
    P("")
    if allpass:
        P("    ALL GATES PASS -> freeze V2 immediately, then ONE final-holdout read is authorized.")
    else:
        P("    *** BLOCKING GATE FAILED -> STOP TSMOM V2. ***")
        P("    Per the continuation rule: FINAL HOLDOUT REMAINS UNSPENT. Do NOT try 126d, blend,")
        P("    189d, 300d, change rebalance, drop ags, equal-weight sectors, go long-only, add")
        P("    trend strength, carry or breakout. That would convert VALIDATION into DEVELOPMENT.")
        P("    Slow TSMOM is CLOSED / DE-PRIORITISED at this specification family.")
    daily.to_csv(os.path.join(OUT, "v2_validation_daily.csv"))
    rc.to_csv(os.path.join(OUT, "v2_validation_root.csv"))
    _fh.close()


if __name__ == "__main__":
    main()
