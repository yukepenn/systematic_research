"""LANE A step 3 - DISCOVERY SUBSTRATE.  Consumed sessions only; the 141-session blind pool is
NOT opened by this script.

EVERY CHOICE BELOW IS FIXED HERE, BEFORE ANY MODEL IS FITTED (directive s4C/s4D/s4F):

  DECISION CLOCK   a fixed 60-second grid.  s4C makes 60 s the PRIMARY horizon; it was chosen
                   before any MS02 alpha result and matches the execution-compatible frontier.
                   Grid step == horizon, so consecutive decisions do not overlap.

  INFORMATION SET  events with timestamp STRICTLY < t.  Never an event stamped exactly t, because
                   within-millisecond sequence is unrecoverable (MS01A).  s4D.

  FEATURES         ONLY the bucket construction certified by contract.py - distinct-timestamp
                   buckets with order-invariant aggregates.  Three fixed lookbacks 60/300/900 s.
                   No feature search, no lookback search.  s4F: no machine-learning zoo.

  PRICE PROXY      bucket VWAP of the last distinct timestamp strictly before the instant.
                   costmodel.py measured this proxy against TRUE Ask->Bid fills on 58 consumed
                   BBO sessions: correlation 0.9946, and it FLATTERS by $1.596/decision, for which
                   a 0.50-tick surcharge is already inside the frozen cost schedule.

  LABEL            move_$ = (P_{t+h} - P_t) * $20/pt.   LONG net = move - cost(hour);
                   SHORT net = -move - cost(hour);  CASH = 0.  Cash is an action.
                   The economic target is AFTER-COST P&L. Directional accuracy is diagnostic only.
"""
from __future__ import annotations

import glob
import os
import re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
V2 = os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")
V1 = os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ")
BLIND = os.path.join(ROOT, "runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/"
                           "MICRO_BLIND_CONFIRMATION_POOL.csv")

NS = 1_000_000_000
GRID_S = 60
HORIZON_S = 60
LOOKBACKS = (60, 300, 900)          # FIXED. Not searched.
DOLLARS_PER_POINT = 20.0
MIN_GRID = 60                       # a session contributing < 60 decisions is dropped


def buckets_of(path):
    """Distinct-timestamp Last buckets. Order-invariant aggregates only (certified by
    contract.py: max rel diff 0.000e+00 under within-millisecond permutation)."""
    t = pq.read_table(path, columns=["bip", "time", "price", "volume"]).to_pandas()
    d = t[t["bip"] == 0]
    if len(d) == 0:
        return None
    tt = d["time"].values.astype("datetime64[ns]").astype("int64")
    p = d["price"].values.astype(float)
    v = d["volume"].values.astype(float)
    o = np.argsort(tt, kind="stable")
    tt, p, v = tt[o], p[o], v[o]
    # group by distinct timestamp
    new = np.empty(len(tt), bool)
    new[0] = True
    np.not_equal(tt[1:], tt[:-1], out=new[1:])
    gid = np.cumsum(new) - 1
    n = gid[-1] + 1
    vol = np.bincount(gid, weights=v, minlength=n)
    pv = np.bincount(gid, weights=p * v, minlength=n)
    cnt = np.bincount(gid, minlength=n).astype(float)
    hi = np.full(n, -np.inf)
    lo = np.full(n, np.inf)
    np.maximum.at(hi, gid, p)
    np.minimum.at(lo, gid, p)
    return dict(t=tt[new], vwap=pv / vol, vol=vol, cnt=cnt, hi=hi, lo=lo)


def features(b, grid):
    """Causal window aggregates ending STRICTLY BEFORE each grid point."""
    t, w, v, c = b["t"], b["vwap"], b["vol"], b["cnt"]
    hi, lo = b["hi"], b["lo"]
    end = np.searchsorted(t, grid, side="left")             # count of buckets with t < g
    dw = np.diff(w, prepend=w[0])
    sgn = np.sign(dw)
    cs = dict(v=np.concatenate([[0], np.cumsum(v)]),
              c=np.concatenate([[0], np.cumsum(c)]),
              sf=np.concatenate([[0], np.cumsum(sgn * v)]),
              af=np.concatenate([[0], np.cumsum(np.abs(sgn) * v)]),
              r2=np.concatenate([[0], np.cumsum(dw ** 2)]),
              n=np.concatenate([[0], np.cumsum(np.ones_like(v))]))
    out = {}
    for W in LOOKBACKS:
        st = np.searchsorted(t, grid - W * NS, side="left")
        nb = cs["n"][end] - cs["n"][st]
        vv = cs["v"][end] - cs["v"][st]
        with np.errstate(invalid="ignore", divide="ignore"):
            out[f"intensity_{W}"] = nb / W
            out[f"volume_{W}"] = vv / W
            out[f"trades_{W}"] = (cs["c"][end] - cs["c"][st]) / W
            out[f"flowimb_{W}"] = np.where(vv > 0,
                                           (cs["sf"][end] - cs["sf"][st]) / np.maximum(vv, 1), 0.0)
            out[f"rvol_{W}"] = np.sqrt(np.maximum(cs["r2"][end] - cs["r2"][st], 0))
            disp = np.where(nb > 0, w[np.clip(end - 1, 0, len(w) - 1)]
                            - w[np.clip(st, 0, len(w) - 1)], 0.0)
            out[f"disp_{W}"] = disp * DOLLARS_PER_POINT
        rg = np.zeros(len(grid))
        for i in range(len(grid)):
            a, e = st[i], end[i]
            if e > a:
                rg[i] = hi[a:e].max() - lo[a:e].min()
        out[f"range_{W}"] = rg * DOLLARS_PER_POINT
    # acceleration: short-window intensity relative to long-window intensity
    out["accel"] = np.where(out["intensity_900"] > 0,
                            out["intensity_60"] / np.maximum(out["intensity_900"], 1e-9), 0.0)
    return out


def main():
    blind = set(pd.read_csv(BLIND)["session"])
    sched = pd.read_csv(os.path.join(OUT, "cost_schedule_FROZEN.csv"))
    cost = dict(zip(sched["hour"], sched["cost_rt_FROZEN"]))
    cost_s1 = dict(zip(sched["hour"], sched["cost_rt_STRESS_1x"]))
    cost_s2 = dict(zip(sched["hour"], sched["cost_rt_STRESS_2x"]))

    files = {}
    for dd, tag in ((V2, "v2"), (V1, "v1")):
        for f in sorted(glob.glob(os.path.join(dd, "s*.parquet"))):
            s = re.match(r"^s(\d{8})", os.path.basename(f)).group(0)
            if s not in blind:
                files.setdefault(s, (f, tag))
    keep, dropped = [], []
    for i, s in enumerate(sorted(files)):
        f, tag = files[s]
        try:
            b = buckets_of(f)
        except Exception as e:                                       # noqa: BLE001
            dropped.append((s, f"unreadable: {e}"))
            continue
        if b is None or len(b["t"]) < 1000:
            dropped.append((s, "too few Last buckets"))
            continue
        t0, t1 = b["t"][0], b["t"][-1]
        start = t0 + max(LOOKBACKS) * NS
        grid = np.arange(start, t1 - HORIZON_S * NS, GRID_S * NS)
        if len(grid) < MIN_GRID:
            dropped.append((s, f"only {len(grid)} grid points"))
            continue
        fe = features(b, grid)
        ie = np.searchsorted(b["t"], grid, side="left") - 1
        ih = np.searchsorted(b["t"], grid + HORIZON_S * NS, side="left") - 1
        ok = (ie >= 0) & (ih > ie)
        px_t, px_h = b["vwap"][ie[ok]], b["vwap"][ih[ok]]
        g = grid[ok]
        hod = pd.to_datetime(g)
        df = pd.DataFrame({k: np.asarray(vv)[ok] for k, vv in fe.items()})
        df["session"] = s
        df["src"] = tag
        df["t"] = g
        df["hour"] = hod.hour
        df["tod"] = hod.hour + hod.minute / 60.0
        df["move"] = (px_h - px_t) * DOLLARS_PER_POINT
        df["cost"] = df["hour"].map(cost).astype(float)
        df["cost_s1"] = df["hour"].map(cost_s1).astype(float)
        df["cost_s2"] = df["hour"].map(cost_s2).astype(float)
        df = df.dropna(subset=["cost", "move"])
        keep.append(df)
        if (i + 1) % 20 == 0:
            print(f"  ... {i+1}/{len(files)} sessions, {sum(len(x) for x in keep):,} rows",
                  flush=True)
    d = pd.concat(keep, ignore_index=True)
    d.to_parquet(os.path.join(OUT, "discovery_substrate.parquet"), index=False)
    print(f"\nDISCOVERY SUBSTRATE  {len(d):,} decisions over {d['session'].nunique()} sessions")
    print(f"  span            {pd.to_datetime(d['t'].min())} -> {pd.to_datetime(d['t'].max())}")
    print(f"  dropped         {len(dropped)}  {dropped[:5]}")
    print(f"  features        {len([c for c in d.columns if c not in ('session','src','t','hour','tod','move','cost','cost_s1','cost_s2')])}")
    print(f"  mean |move|     ${d['move'].abs().mean():,.2f}")
    print(f"  mean cost       ${d['cost'].mean():,.2f}")
    print(f"  P(|move|>cost)  {100*np.mean(d['move'].abs() > d['cost']):.2f} %")


if __name__ == "__main__":
    main()
