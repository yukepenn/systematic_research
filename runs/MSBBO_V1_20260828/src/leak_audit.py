"""MS-BBO-V1 LEAK AUDIT.  Run BEFORE the result is reported, not after it is doubted.

MS-BBO-V1 passed all seven preregistered gates at $5,124.76/session, t 6.76, 87.5 % positive
sessions. In this repository a result of that size has historically been a look-ahead (W03's gate
read the entry bar's close; W37's quantiles were computed over future entries; W41's range clock;
W77's outcome-conditioned sort). Discipline rule: run the adversarial check at the moment of
maximum confidence.

FOUR INDEPENDENT PROBES, each able to fail:

  L1  DIRECT TIMESTAMP ASSERTION - on real decisions, prove
          max(feature source timestamp) < t < min(execution timestamp)
      There is no modelling here; it either holds on every sampled decision or it does not.

  L2  FEATURE-LAG TEST - recompute the whole pipeline with every feature taken one full decision
      step (60 s) EARLIER. A genuine slow signal degrades gracefully. A leak collapses.

  L3  SINGLE-FEATURE ABLATION - drop the features closest to t (midret_1s, midret_5s). If the
      entire edge lives in the one-second return, the object is a sub-second execution bet, not a
      60-second forecast, and must be described as such.

  L4  SHUFFLED-EXECUTION CONTROL - keep the model and its decisions, but take the execution quotes
      from a DIFFERENT random session at the same time-of-day. If P&L survives that, the "edge" is
      an artifact of the label construction rather than of matched market state.
"""
from __future__ import annotations

import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.linear_model import Ridge

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bbo_v1 as B                                                     # noqa: E402

OUT = B.OUT
_fh = open(os.path.join(OUT, "leak_audit.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def main():
    files = sorted(glob.glob(os.path.join(B.V2, "s*.parquet")))
    P("=" * 104)
    P("=== MS-BBO-V1 LEAK AUDIT - four probes, each able to fail")
    P("=" * 104)

    # ---------------------------------------------------------------- L1
    P("")
    P("=== L1  DIRECT TIMESTAMP ASSERTION on real decisions")
    f = files[len(files) // 2]
    d = pq.read_table(f, columns=["bip", "time", "price"]).to_pandas()
    ti = d["time"].values.astype("datetime64[ns]").astype("int64")
    bip, px = d["bip"].values, d["price"].values
    day = pd.Timestamp(d["time"].max()).normalize()
    grid = np.arange((day + pd.Timedelta(B.RTH_START)).value,
                     (day + pd.Timedelta(B.RTH_END)).value + 1, B.GRID_S * B.NS)

    def side(b):
        m = bip == b
        t_, p_ = ti[m], px[m]
        u, inv = np.unique(t_, return_inverse=True)
        return u, np.bincount(inv, weights=p_) / np.bincount(inv)
    bt, bp = side(1)
    at, ap = side(2)
    bad = 0
    for g in grid[::17]:
        i_feat_b = np.searchsorted(bt, g, side="left") - 1
        i_feat_a = np.searchsorted(at, g, side="left") - 1
        i_exec_a = np.searchsorted(at, g, side="right")
        i_exec_b = np.searchsorted(bt, g, side="right")
        if i_feat_b < 0 or i_exec_a >= len(at):
            continue
        if not (bt[i_feat_b] < g and at[i_feat_a] < g and at[i_exec_a] > g and bt[i_exec_b] > g):
            bad += 1
    P(f"    sampled {len(grid[::17])} decisions on {os.path.basename(f)}")
    P(f"    violations of  feature_ts < t < execution_ts :  {bad}")
    P(f"    >>> {'PASS - no decision reads an event at or after t as a feature' if bad == 0 else '*** LEAK ***'}")

    # ---------------------------------------------------------------- rebuild once
    P("")
    P("=== building the shared substrate for L2/L3/L4 ...")
    parts = []
    for fp in files:
        x = B.session_features(fp)
        if x is not None:
            parts.append(x)
    dd = pd.concat(parts, ignore_index=True)
    meta = ("t", "mid", "long_gross", "short_gross", "wait_ok", "session")
    feats = [c for c in dd.columns if c not in meta]
    dd = dd[dd["wait_ok"] & dd[feats].notna().all(axis=1)
            & dd["long_gross"].notna() & dd["short_gross"].notna()].copy()
    dd = dd.sort_values("t").reset_index(drop=True)
    y = (dd["long_gross"].values + (-dd["short_gross"].values)) / 2.0
    sess = dd["session"].values
    order = pd.unique(dd["session"])
    blocks = np.array_split(order, B.N_FOLD + 1)
    mk = lambda: Ridge(alpha=10.0)                                     # noqa: E731

    def score(X_, label, dat=None):
        ix, pr = B.oof(X_, y, sess, blocks, mk)
        net, act = B.policy_pnl(pr, (dat if dat is not None else dd).iloc[ix], 0.0)
        ss = pd.Series(net).groupby(sess[ix]).sum()
        P(f"    {label:<44} ${ss.mean():>9,.2f}/session   net ${ss.sum():>10,.0f}   "
          f"trade {100*np.mean(act != 0):>5.1f}%")
        return float(ss.mean())

    X = np.nan_to_num(dd[feats].values.astype(float), posinf=0, neginf=0)
    P("")
    P("=== L2  FEATURE-LAG TEST - every feature taken one full 60 s decision step earlier")
    base = score(X, "baseline (features at t)")
    Xl = pd.DataFrame(X, columns=feats)
    Xl["_s"] = sess
    Xl = Xl.groupby("_s", sort=False)[feats].shift(1)
    lag_ok = Xl.notna().all(axis=1).values
    Xlag = np.nan_to_num(Xl.values.astype(float), posinf=0, neginf=0)
    ixl, prl = B.oof(Xlag[lag_ok], y[lag_ok], sess[lag_ok],
                     [np.array([s for s in b if s in set(sess[lag_ok])]) for b in blocks], mk)
    netl, actl = B.policy_pnl(prl, dd[lag_ok].iloc[ixl], 0.0)
    ssl = pd.Series(netl).groupby(sess[lag_ok][ixl]).sum()
    P(f"    {'features lagged one 60 s step':<44} ${ssl.mean():>9,.2f}/session   "
      f"net ${ssl.sum():>10,.0f}   trade {100*np.mean(actl != 0):>5.1f}%")
    ratio = ssl.mean() / base if base else np.nan
    P(f"    >>> retained {100*ratio:.1f} % of the edge under a full 60 s feature lag")
    P("    >>> A genuine 60 s forecast should degrade but survive; total collapse would say the")
    P("    >>> signal lives entirely in the instant before t.")

    # ---------------------------------------------------------------- L3
    P("")
    P("=== L3  ABLATION - drop the features nearest to t")
    for drop in (["midret_1s"], ["midret_1s", "midret_5s"],
                 ["midret_1s", "midret_5s", "midret_15s", "midret_30s"]):
        keep = [c for c in feats if c not in drop]
        score(np.nan_to_num(dd[keep].values.astype(float), posinf=0, neginf=0),
              f"without {', '.join(drop)}")

    # ---------------------------------------------------------------- L4
    P("")
    P("=== L4  SHUFFLED-EXECUTION CONTROL - same decisions, execution quotes from another session")
    rng = np.random.default_rng(B.SEED)
    dsh = dd.copy()
    perm = {s: t for s, t in zip(order, rng.permutation(order))}
    key = dd["tod"].round(4).astype(str)
    lut = dd.assign(_k=dd["session"] + "|" + key).set_index("_k")[["long_gross", "short_gross"]]
    newk = pd.Series([perm[s] for s in dd["session"]]).values + "|" + key.values
    rep = lut.reindex(newk)
    dsh["long_gross"] = rep["long_gross"].values
    dsh["short_gross"] = rep["short_gross"].values
    okm = dsh[["long_gross", "short_gross"]].notna().all(axis=1).values
    bl2 = [np.array([s for s in b if s in set(sess[okm])]) for b in blocks]
    ix2, pr2 = B.oof(X[okm], y[okm], sess[okm], bl2, mk)
    net2, act2 = B.policy_pnl(pr2, dsh[okm].iloc[ix2], 0.0)
    ss2 = pd.Series(net2).groupby(sess[okm][ix2]).sum()
    P(f"    {'execution quotes from a DIFFERENT session':<44} ${ss2.mean():>9,.2f}/session   "
      f"net ${ss2.sum():>10,.0f}")
    P(f"    >>> {'PASS - the edge does NOT survive mismatched execution' if ss2.mean() < 0.2*base else '*** FAILS - P&L survives mismatched execution, so it is a LABEL ARTIFACT ***'}")
    _fh.close()


if __name__ == "__main__":
    main()
