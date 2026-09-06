"""XINST01 - PARAMETERIZED P1/PCT BENCH (spec: runs/XINST01_WEEKLY_EDGE_PORT_20260906/spec.yaml).

This is NOT a fork of the P1/PCT mechanism. It IMPORTS the incumbent's exact building blocks
(sm14_1m member ratchet, votes, fills_daily, causal_score, gfills, fast_build_context) and only
substitutes, per instrument:

    substrate_path, PV (point value), tick size, commission $/ctrRT, spread model,
    box_points_halt / box_points_target  (the session box, transferred by PERCENTILE),

plus the ratchet volatility clamps SMIN/SMAX/STOPM which are POINTS-denominated in the incumbent
and MUST be re-expressed in the instrument's own volatility units to stay scale-invariant (the
W43 hook `smin_pts/smax_pts/stopm_pts` exists precisely for this). Everything else -- every
ATR-normalized Solar feature, the day/quantile params, EntryLevel/ExitLevel, the causal-score
quantiles, QualWindow=250, the flat-at-close guard -- is IDENTICAL and NEVER refit per instrument.

Because gfills/fills_daily/sm14_1m read PV and COMM_RT from their DEFINING module's globals at
call time, this bench sets those module globals before every run and restores them after.

SEAL: >= 2026-08-01 is GLOBAL VIRGIN. load_substrate hard-drops it at load and prints the
boundary. Nothing here reads a bar dated on or after 2026-08-01.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
WE_SRC = os.path.join(REPO, "research", "weekly_edge", "src")
if WE_SRC not in sys.path:
    sys.path.insert(0, WE_SRC)

import run_we_w01 as W01                                            # noqa: E402
import run_we_w26 as W26                                           # noqa: E402
import run_we_w98 as W98                                           # noqa: E402
from run_we_w01 import sm14_1m                                     # noqa: E402
from run_we_w26 import fills_daily                                 # noqa: E402
from run_we_w37 import causal_score                                # noqa: E402
from run_we_w39 import WIN                                         # noqa: E402
from run_we_w51c import dd_profile                                 # noqa: E402
from run_we_w97 import votes                                       # noqa: E402
from run_we_w98 import gfills                                      # noqa: E402
from we_fastctx import fast_build_context                          # noqa: E402

L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
SEAL = np.datetime64("2026-08-01")                                 # global virgin boundary
SEAL_LOAD = pd.Timestamp("2026-07-31 17:00")                       # last bar kept (session close)

# incumbent NQ box + clamps (POINTS). box: halt 65 pts, target 50 pts (== $1300/$1000 at PV 20).
NQ_HALT_PTS = 65.0
NQ_TGT_PTS = 50.0
NQ_SMIN_PTS = 40 * 0.25          # 10.0   sm14_1m default
NQ_SMAX_PTS = 1200 * 0.25        # 300.0  sm14_1m default
NQ_STOPM_PTS = 179 * 0.25        # 44.75  sm14_1m default


# ----------------------------------------------------------------------- substrate loader
def load_substrate(path, label=""):
    """Build the D dict exactly as run_we_w01.load / run_we_w17.load_deep do, but HARD-DROP
    every bar at or after the 2026-08-01 virgin seal at load time, and print the boundary."""
    df = pd.read_parquet(path if os.path.isabs(path) else os.path.join(REPO, path))
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    n_before = len(df)
    # HARD DROP: keep only <= 2026-07-31 17:00 (drops the entire 2026-08-01 session onward,
    # exactly the load_deep(..., "2026-07-31 17:00") convention). No virgin bar is materialized
    # into the arrays used below.
    df = df[df["time"] <= SEAL_LOAD].sort_values("time").reset_index(drop=True)
    n_dropped = n_before - len(df)
    t = df["time"].values.astype("datetime64[s]")
    o, h, l, c = (df[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = df["volume"].values.astype(float)
    n = len(df)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    sid = np.cumsum(fb) - 1
    n_sess = int(sid[-1] + 1)
    last_of = np.zeros(n_sess, np.int64)
    last_of[sid[lb]] = np.nonzero(lb)[0]
    sess_end = t[last_of] + np.timedelta64(60, "s")
    sess_date = sess_end.astype("datetime64[D]")
    iso = pd.Series(pd.to_datetime(sess_date)).dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    D = dict(df=df, t=t, o=o, h=h, l=l, c=c, v=v, n=n, fb=fb, lb=lb, sid=sid,
             n_sess=n_sess, sess_end=sess_end, sess_date=sess_date, wk=wk)
    maxsess = pd.Timestamp(sess_date.max())
    seal_ok = maxsess < pd.Timestamp("2026-08-01")
    boundary = dict(label=label, n_bars=n, n_sess=n_sess, n_dropped=int(n_dropped),
                    first_sess=str(pd.Timestamp(sess_date.min()).date()),
                    last_sess=str(maxsess.date()), seal_ok=bool(seal_ok))
    return D, boundary


# ----------------------------------------------------------------------- volatility scale
def vol_scale(D):
    """Mean |dClose| over in-session bars (exclude the first bar of each session, whose diff
    crosses the overnight gap). This is exactly the statistic sm14_1m's sigma is a trailing
    mean of, so scaling the POINTS clamps by its ratio makes them the SAME multiple of typical
    volatility on every instrument -- scale-invariant, zero free parameters."""
    c = D["c"]
    dc = np.abs(np.diff(c))
    keep = ~D["fb"][1:]                       # drop session-crossing diffs
    return float(np.mean(dc[keep]))


# ----------------------------------------------------------------------- session point-range
def session_ranges(D, a=None, b=None):
    """Per-session (max high - min low) in POINTS, for sessions whose date is in [a,b)."""
    sid, n_sess = D["sid"], D["n_sess"]
    hi = pd.Series(D["h"]).groupby(sid).max().to_numpy()
    lo = pd.Series(D["l"]).groupby(sid).min().to_numpy()
    rng = hi - lo
    sd = D["sess_date"]
    m = np.ones(n_sess, bool)
    if a is not None:
        m &= (sd >= np.datetime64(a))
    if b is not None:
        m &= (sd < np.datetime64(b))
    return rng[m]


def pctile_rank(x, val):
    """percentile (0-100) of `val` within distribution x."""
    x = np.asarray(x, float)
    return float(100.0 * np.mean(x <= val))


# ----------------------------------------------------------------------- the P1/PCT pipeline
def _set_scalars(PV, comm):
    for M in (W01, W26, W98):
        M.PV = PV
        M.COMM_RT = comm


def build_p1pct(D, PV, comm, halt_pts, tgt_pts, smin_pts, smax_pts, stopm_pts,
                win_a, win_b):
    """Run the IDENTICAL P1/PCT mechanism on D with the given per-instrument scalars.

    Returns the in-window trade list (each trade: d,u,et,xt,pnl with commission already
    charged inside gfills at `comm`/ctrRT). Spread is applied later by net_series.
    """
    _set_scalars(PV, comm)
    A = np.datetime64(win_a); B = np.datetime64(win_b)
    tarr, sid, fb = D["t"], D["sid"], D["fb"]
    n = D["n"]
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    # 1. the 13-member Solar ratchet matrix + B-MOM channel + tilt (clamps in the
    #    instrument's own volatility units; NQ passes the defaults -> bit-identical)
    _, mem, bmom, tilt = sm14_1m(D, 460, volmults=L13, return_members=True,
                                 smin_pts=smin_pts, smax_pts=smax_pts, stopm_pts=stopm_pts)
    # 2. causal context (ATR-normalized features, self-normalizing quantile gates)
    X = fast_build_context(D)
    # 3. the OR-gated long-target vote (B-MOM in the OR slot -- this is P1)
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p = vl.astype(np.int8)
    # 4. entry schedule under the session box (box in dollars = points * PV)
    halt_d, tgt_d = halt_pts * PV, tgt_pts * PV
    bb = fills_daily(D, p, halt=halt_d, target=tgt_d)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    # 5. causal quality score -> size 2 when score >= 3 (~20% of entries), QualWindow=250
    sc, _ = causal_score(X, ee, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    # 6. the PCT (per-contract) session box fill -> the P1/PCT trade list (FULL substrate;
    #    net_series filters to the window when it accumulates, but the spread RATE and the
    #    trade count are taken over ALL trades -- the exact WE_W103 net_series convention)
    tr = gfills(D, p, sz, halt=halt_d, target=tgt_d, per_ctr=True)
    trin = [x for x in tr if in_win[int(sid[i_of(x["et"])])]]
    return tr, dict(sess_in=sess_in, in_win=in_win, i_of=i_of, trin=trin,
                    n_entries=len(ee), size2_share=float(np.mean(sz[ee] == 2)) if len(ee) else 0.0,
                    long_target_bars=int(p.sum()), mem=mem, bmom=bmom, tilt=tilt)


# ----------------------------------------------------------------------- cost / net series
def net_series(D, tr, PV, tick, spread_model, sess_in, i_of):
    """Per-session P&L net of commission (already in tr) AND spread, plus contracts and the
    per-ctrRT spread rate. spread_model is either:
       ("nq_profile", prof_series)  -- W82 per-minute spread in ticks, weighted by fill minutes
                                       (reproduces P1's $14.44/ctrRT for NQ)
       ("flat_ticks", k, dv)        -- k ticks of spread per ctrRT, dv = $/tick (= PV*tick)
    Returns (session_net[over sess_in], contracts[over sess_in], rate, n_trades)."""
    sid = D["sid"]
    kind = spread_model[0]
    if kind == "nq_profile":
        prof = spread_model[1]
        dv = PV * tick                                   # $/tick = 5.0 for NQ
        w = {}
        for x in tr:
            for ts in (x["et"], x["xt"]):
                pt = pd.Timestamp(ts); m = pt.hour * 60 + pt.minute
                w[m] = w.get(m, 0.0) + x["u"]
        tot = sum(w.values())
        rate = dv * sum(float(prof.get(m, 3.0)) * q for m, q in w.items()) / max(tot, 1e-9)
    elif kind == "flat_ticks":
        k, dv = spread_model[1], spread_model[2]
        rate = float(k) * float(dv)
    else:
        raise ValueError("unknown spread model %r" % (kind,))
    s_ = np.zeros(D["n_sess"]); ct = np.zeros(D["n_sess"])
    for x in tr:
        si = int(sid[i_of(x["et"])])
        s_[si] += x["pnl"]; ct[si] += x["u"]
    return s_[sess_in] - rate * ct[sess_in], ct[sess_in], float(rate), len(tr)


# ----------------------------------------------------------------------- weekly aggregation
def weekly(D, session_net, sess_in):
    sd = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sd.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    ser = pd.Series(session_net).groupby(wk).sum()
    return ser.to_numpy(), ser.index.to_numpy()


def panel(w):
    dp = dd_profile(w)
    import itertools
    stk = max((len(list(g)) for k, g in itertools.groupby(w < 0) if k), default=0)
    cq = max(1, int(round(0.05 * len(w))))
    return dict(nwk=len(w), weekly=float(w.mean()),
                maxdd=float(dp["maxdd"]), top5=float(dp["dd_mean_top5"]),
                worst=float(w.min()), poswk=100 * float((w > 0).mean()),
                cvar5=float(np.sort(w)[:cq].mean()), streak=int(stk),
                t=float(w.mean()) / max(w.std(ddof=1) / np.sqrt(len(w)), 1e-9))
