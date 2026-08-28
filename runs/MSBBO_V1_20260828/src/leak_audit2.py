"""LEAK AUDIT 2 - the STALE-QUOTE RECONSTRUCTION hazard, which L2/L3 together point straight at.

WHAT L2 AND L3 JOINTLY IMPLY.
    L3: dropping every mid-return feature costs almost nothing ($5,125 -> $4,873/session).
    L2: lagging every feature by one 60 s step DESTROYS the edge ($5,125 -> -$1,490).
So the signal is NOT price momentum, and it lives entirely in the instant before t.

THE HAZARD THAT FITS THAT SIGNATURE EXACTLY, and it is in MY OWN CODE, not the market:

    mid_t and spread_t are built from  (last bid before t, last ask before t).
    THOSE TWO QUOTES CAN BE FROM VERY DIFFERENT INSTANTS.

If the bid updated 2 ms ago and the ask 4 s ago, the reconstructed spread is not a spread at all -
it is a measure of HOW STALE ONE SIDE IS. The very next quote after t then "reveals" the true
level. A model can learn to read that staleness and appear to forecast the next 60 seconds, when
it is really correcting an artifact of the reconstruction. It would be destroyed by a 60 s lag
(staleness is instantaneous) and unaffected by dropping mid returns - precisely what L2 and L3 show.

THE TEST: restrict to decisions where BOTH sides are genuinely fresh. If the edge survives on
fresh-quote decisions it is a market effect; if it collapses it was my reconstruction.
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.linear_model import Ridge

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bbo_v1 as B                                                     # noqa: E402

OUT = B.OUT
_fh = open(os.path.join(OUT, "leak_audit2.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def ages(path):
    """Age in ms of the last bid and last ask STRICTLY BEFORE each decision instant."""
    d = pq.read_table(path, columns=["bip", "time"]).to_pandas()
    ti = d["time"].values.astype("datetime64[ns]").astype("int64")
    bip = d["bip"].values
    day = pd.Timestamp(d["time"].max()).normalize()
    grid = np.arange((day + pd.Timedelta(B.RTH_START)).value,
                     (day + pd.Timedelta(B.RTH_END)).value + 1, B.GRID_S * B.NS)
    out = {}
    for b, nm in ((1, "bid"), (2, "ask")):
        u = np.unique(ti[bip == b])
        i = np.searchsorted(u, grid, side="left") - 1
        a = np.full(len(grid), np.nan)
        ok = i >= 0
        a[ok] = (grid[ok] - u[i[ok]]) / 1e6
        out[f"age_{nm}"] = a
    out["t"] = grid
    return pd.DataFrame(out)


def main():
    files = sorted(glob.glob(os.path.join(B.V2, "s*.parquet")))
    P("=" * 104)
    P("=== LEAK AUDIT 2 - is the edge a STALE-QUOTE RECONSTRUCTION ARTIFACT?")
    P("=" * 104)

    parts, ag = [], []
    for fp in files:
        x = B.session_features(fp)
        if x is None:
            continue
        parts.append(x)
        a = ages(fp)
        a["session"] = x["session"].iloc[0]
        ag.append(a)
    dd = pd.concat(parts, ignore_index=True)
    AG = pd.concat(ag, ignore_index=True)
    dd = dd.merge(AG, on=["session", "t"], how="left")
    meta = ("t", "mid", "long_gross", "short_gross", "wait_ok", "session", "age_bid", "age_ask")
    feats = [c for c in dd.columns if c not in meta]
    dd = dd[dd["wait_ok"] & dd[feats].notna().all(axis=1)
            & dd["long_gross"].notna() & dd["short_gross"].notna()
            & dd["age_bid"].notna() & dd["age_ask"].notna()].copy()
    dd = dd.sort_values("t").reset_index(drop=True)

    P("")
    P("=== QUOTE AGE AT THE DECISION INSTANT")
    for c in ("age_bid", "age_ask"):
        q = dd[c]
        P(f"    {c}:  median {q.median():>8.1f} ms   p75 {q.quantile(.75):>9.1f}   "
          f"p95 {q.quantile(.95):>10.1f}   p99 {q.quantile(.99):>11.1f}   max {q.max():>12.1f}")
    dd["age_max"] = dd[["age_bid", "age_ask"]].max(axis=1)
    dd["age_gap"] = (dd["age_bid"] - dd["age_ask"]).abs()
    P(f"    max-of-two-sides:  median {dd['age_max'].median():.1f} ms   "
      f"p95 {dd['age_max'].quantile(.95):.1f}   p99 {dd['age_max'].quantile(.99):.1f}")
    P(f"    |bid age - ask age|: median {dd['age_gap'].median():.1f} ms   "
      f"p95 {dd['age_gap'].quantile(.95):.1f}")

    y = (dd["long_gross"].values + (-dd["short_gross"].values)) / 2.0
    sess = dd["session"].values
    order = pd.unique(dd["session"])
    blocks = np.array_split(order, B.N_FOLD + 1)
    mk = lambda: Ridge(alpha=10.0)                                     # noqa: E731
    X = np.nan_to_num(dd[feats].values.astype(float), posinf=0, neginf=0)

    def run_on(mask, label):
        sub = dd[mask]
        if sub["session"].nunique() < 10:
            P(f"    {label:<42} too few sessions")
            return np.nan
        bl = [np.array([s for s in b if s in set(sub["session"])]) for b in blocks]
        ix, pr = B.oof(X[mask.values], y[mask.values], sess[mask.values], bl, mk)
        net, act = B.policy_pnl(pr, sub.iloc[ix], 0.0)
        ss = pd.Series(net).groupby(sess[mask.values][ix]).sum()
        P(f"    {label:<42} ${ss.mean():>9,.2f}/session   n {int(mask.sum()):>6,}   "
          f"trade {100*np.mean(act != 0):>5.1f}%")
        return float(ss.mean())

    P("")
    P("=== THE DECISIVE TEST - restrict to decisions where BOTH sides are genuinely fresh")
    base = run_on(pd.Series(True, index=dd.index), "ALL decisions (baseline)")
    for cap in (1000.0, 250.0, 100.0, 25.0):
        run_on(dd["age_max"] <= cap, f"both quotes fresher than {cap:,.0f} ms")

    P("")
    P("=== AND THE MIRROR - decisions where ONE side is badly stale")
    for lo in (250.0, 1000.0):
        run_on(dd["age_max"] > lo, f"at least one side staler than {lo:,.0f} ms")

    P("")
    P("=== EDGE vs STALENESS, by quintile of max quote age")
    dd["_q"] = pd.qcut(dd["age_max"], 5, labels=False, duplicates="drop")
    for q in sorted(dd["_q"].dropna().unique()):
        m = dd["_q"] == q
        rng = f"{dd.loc[m,'age_max'].min():.0f}-{dd.loc[m,'age_max'].max():.0f} ms"
        run_on(m, f"  quintile {int(q)+1}  age {rng}")
    _fh.close()


if __name__ == "__main__":
    main()
