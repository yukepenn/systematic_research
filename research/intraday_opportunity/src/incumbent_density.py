"""INCUMBENT OPPORTUNITY DENSITY -- descriptive measurement of an ALREADY-FROZEN object.

This is NOT a new alpha object and it fits nothing.  It measures what P1/PCT and XM_CONFLICT
actually do inside a session, so that PROGRAM B has a real baseline to move rather than an
impression.  Source of truth is the certified counterfactual ledger from RR_W001, whose cost model
is COMMISSION_PLUS_MODELLED_SPREAD -- the frozen research convention.

THE CENTRAL TABLE is net P&L by ENTRY ORDINAL WITHIN SESSION.  It answers, for the object we
already own, the owner's actual question: does the 2nd / 3rd / 4th trade of the day still make
money, or are we giving back the day's edge?
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # src -> lane -> research -> repo
os.makedirs(OUT, exist_ok=True)
LED = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out")
_fh = open(os.path.join(OUT, "incumbent_density.txt"), "w", encoding="utf-8")
R = {}


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def load(name):
    """Ledgers do not share a schema -- XM has no per-trade counterfactual fields. Parse only what
    is present rather than assuming a common shape."""
    d = pd.read_csv(os.path.join(LED, name))
    for c in ("session_date", "decision_ts", "info_cutoff_ts"):
        if c in d.columns:
            d[c] = pd.to_datetime(d[c])
    return d


P("=" * 108)
P("=== INCUMBENT OPPORTUNITY DENSITY -- descriptive. No fitting, no new object, no promotion.")
P("=" * 108)

p1 = load("ledger_p1pct.csv")
xm = load("ledger_xm.csv")
P(f"    P1/PCT ledger rows {len(p1):,}   cost model {p1['cost_model_id'].iloc[0]}")
P(f"    XM     ledger rows {len(xm):,}")
P(f"    P1 in_window_session=True: {int(p1['in_window_session'].sum()):,}   "
  f"span {p1['session_date'].min().date()} -> {p1['session_date'].max().date()}")

# The canonical headline stream is the FULL 2,401. in_window_session is a NARROWER analysis
# filter used by RR_W001. Both are reported; neither is silently substituted for the other.
POPS = {"FULL LEDGER (2,401 - the canonical headline stream)": p1,
        "in_window_session subset": p1[p1["in_window_session"]].copy()}

for label, d in POPS.items():
    P("")
    P("-" * 108)
    P(f"--- {label}   n = {len(d):,} trades")
    P("-" * 108)
    # SESSION_ID, not session_date. NQ sessions run 18:00 -> 17:00 ET, so one TRADING SESSION
    # spans two CALENDAR dates. Grouping by date splits overnight sessions in two and understates
    # density: session_date gives 712 "sessions" where session_id gives 638. The book ledger is
    # keyed by session (1,058 unique) against only 1,056 unique dates, confirming the unit.
    skey = "session_id" if "session_id" in d.columns else "session_date"
    ns = d[skey].nunique()
    tps = d.groupby(skey).size()
    P(f"    session key used                {skey}")
    P(f"    sessions WITH >=1 P1 trade      {ns:,}   (of 1,058 in-window trading sessions)")
    P(f"    sessions COMPLETELY FLAT        {1058-ns:,} = {(1058-ns)/1058:.1%}")
    P(f"    trades per CALENDAR session     {len(d)/1058:.3f}")
    P(f"    trades per ACTIVE session       mean {tps.mean():.3f}  median {tps.median():.0f}  "
      f"p10 {tps.quantile(.10):.0f}  p90 {tps.quantile(.90):.0f}  max {tps.max()}")
    dist = tps.value_counts().sort_index()
    buckets = {"1": int((tps == 1).sum()), "2": int((tps == 2).sum()), "3-5": int(tps.between(3, 5).sum()),
               "6-10": int(tps.between(6, 10).sum()), ">10": int((tps > 10).sum())}
    P(f"    active-session trade-count mix  " +
      "  ".join(f"{k}:{v} ({v/ns:.1%})" for k, v in buckets.items()))
    P(f"    net total                       ${d['baseline_trade_net'].sum():,.2f}")
    P(f"    net per trade                   ${d['baseline_trade_net'].mean():,.2f}")
    P(f"    median hold (min)               {d['baseline_hold_minutes'].median():.0f}   "
      f"mean {d['baseline_hold_minutes'].mean():.1f}   "
      f"p90 {d['baseline_hold_minutes'].quantile(.9):.0f}")
    P(f"    long / short                    {int((d['side']==1).sum()):,} / {int((d['side']==-1).sum()):,}")

    P("")
    P("    *** MARGINAL ECONOMICS BY ENTRY ORDINAL WITHIN SESSION ***")
    o = d["entry_ordinal_in_session"]
    d = d.assign(bucket=np.select(
        [o == 1, o == 2, o == 3, o.between(4, 5), o >= 6],
        ["1st", "2nd", "3rd", "4th-5th", "6th+"], default="?"))
    g = d.groupby("bucket", observed=True).agg(
        n=("baseline_trade_net", "size"),
        net=("baseline_trade_net", "sum"),
        mean=("baseline_trade_net", "mean"),
        median=("baseline_trade_net", "median"),
        win=("baseline_trade_net", lambda s: float((s > 0).mean())),
        hold=("baseline_hold_minutes", "median"),
        mae=("baseline_mae", "mean"),
        mfe=("baseline_mfe", "mean"))
    order = ["1st", "2nd", "3rd", "4th-5th", "6th+"]
    g = g.reindex([x for x in order if x in g.index])
    P(f"      {'ordinal':<9}{'n':>7}{'total net':>14}{'mean/trade':>13}{'median':>10}"
      f"{'win%':>8}{'hold m':>9}{'mean MAE':>10}{'mean MFE':>10}")
    for k, r_ in g.iterrows():
        P(f"      {k:<9}{int(r_['n']):>7,}{r_['net']:>14,.0f}{r_['mean']:>13,.2f}"
          f"{r_['median']:>10,.2f}{r_['win']:>8.1%}{r_['hold']:>9.0f}"
          f"{r_['mae']:>10,.0f}{r_['mfe']:>10,.0f}")
    # ---- SESSION-CLUSTERED inference (directive s28). A system taking 8 trades/day does NOT
    # have 8 independent observations/day. Trade-level SEs would manufacture significance.
    P("")
    P("    session-clustered bootstrap on the SAME buckets (5,000 resamples of SESSIONS, seed 7)")
    rng = np.random.default_rng(7)
    sess = d[skey].values
    usess = np.unique(sess)
    idx_by_sess = {s: np.where(sess == s)[0] for s in usess}
    P(f"      {'ordinal':<9}{'mean/trade':>13}{'session-clustered 95% CI':>30}{'  P(mean>0)':>12}")
    for k in g.index:
        mask = (d["bucket"] == k).values
        vals = d["baseline_trade_net"].values
        boots = []
        for _ in range(5000):
            pick = rng.choice(usess, len(usess), replace=True)
            rows = np.concatenate([idx_by_sess[s] for s in pick])
            m = mask[rows]
            boots.append(vals[rows][m].mean() if m.any() else np.nan)
        b = np.array([x for x in boots if np.isfinite(x)])
        lo, hi = np.percentile(b, [2.5, 97.5])
        P(f"      {k:<9}{float(vals[mask].mean()):>13,.2f}"
          f"{f'[{lo:,.0f}, {hi:,.0f}]':>30}{float((b>0).mean()):>12.3f}")
        R.setdefault("clustered", {}).setdefault(label, {})[k] = dict(
            mean=float(vals[mask].mean()), lo=float(lo), hi=float(hi),
            p_gt0=float((b > 0).mean()))

    P("")
    P("    per-ordinal (not bucketed), first 8:")
    g2 = d.groupby(o).agg(n=("baseline_trade_net", "size"),
                          mean=("baseline_trade_net", "mean"),
                          net=("baseline_trade_net", "sum"))
    P("      " + "  ".join(f"#{int(k)}: n{int(v['n'])} ${v['mean']:,.0f}"
                           for k, v in g2.head(8).iterrows()))

    # cumulative: what would capping at K trades/session have produced? DIAGNOSTIC ONLY.
    P("")
    P("    OPPORTUNITY SATURATION (DIAGNOSTIC ONLY -- no cap is selected from this)")
    P(f"      {'cap K':>7}{'trades kept':>14}{'net':>14}{'net/trade':>12}{'vs uncapped':>14}")
    full = d["baseline_trade_net"].sum()
    for K in (1, 2, 3, 4, 5, 6, 8, 10, 999):
        sub = d[o <= K]
        lbl = "none" if K == 999 else str(K)
        P(f"      {lbl:>7}{len(sub):>14,}{sub['baseline_trade_net'].sum():>14,.0f}"
          f"{sub['baseline_trade_net'].mean():>12,.2f}"
          f"{sub['baseline_trade_net'].sum()-full:>14,.0f}")

    R[label] = dict(
        trades=int(len(d)), active_sessions=int(ns),
        trades_per_active_session=float(tps.mean()),
        median_hold_min=float(d["baseline_hold_minutes"].median()),
        net=float(d["baseline_trade_net"].sum()),
        net_per_trade=float(d["baseline_trade_net"].mean()),
        buckets=buckets,
        by_ordinal={k: dict(n=int(v["n"]), net=float(v["net"]), mean=float(v["mean"]),
                            win=float(v["win"]), hold=float(v["hold"]))
                    for k, v in g.iterrows()})

# ---------------------------------------------------------------- XM
P("")
P("-" * 108)
P("--- XM_CONFLICT")
P("-" * 108)
P(f"    columns present: {list(xm.columns)}")
skey = "session_date" if "session_date" in xm.columns else xm.columns[0]
xs = xm[skey].nunique()
netcol = next((c for c in ("baseline_trade_net", "trade_net", "net", "pnl")
               if c in xm.columns), None)
P(f"    trades {len(xm):,}   sessions with a trade {xs:,}   "
  f"trades/active session {len(xm)/xs:.3f}")
if "baseline_hold_minutes" in xm.columns:
    P(f"    median hold (min) {xm['baseline_hold_minutes'].median():.0f}")
if netcol:
    P(f"    net ${xm[netcol].sum():,.2f}   per trade ${xm[netcol].mean():,.2f}  (column '{netcol}')")
R["XM"] = dict(trades=int(len(xm)), active_sessions=int(xs), net_column=netcol,
               net=float(xm[netcol].sum()) if netcol else None,
               net_per_trade=float(xm[netcol].mean()) if netcol else None)

json.dump(R, open(os.path.join(OUT, "incumbent_density.json"), "w", encoding="utf-8"),
          indent=2, default=str)
P("")
P("=" * 108)
P("=== Descriptive only. Nothing was fitted, selected, capped or promoted.")
P("=" * 108)
_fh.close()
