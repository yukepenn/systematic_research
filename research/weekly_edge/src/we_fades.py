"""we_fades - the five W108 fade mechanisms, FROZEN, as a reusable object.

This is a VERBATIM lift of the construction inside `run_we_w108.py`. It exists so that W109 can
veto the exact same engines W108 measured rather than a re-implementation of them, and so that a
reproduction gate can assert that claim numerically instead of by inspection.

`VWAP_RECLAIM` is deliberately NOT here. W108 closed it: it earns on both TREND classes and loses
on REVERSAL and RANGE, so it is a trend-continuation mechanism wearing a reversal label, and its
54.20 % hit rate is indistinguishable from an always-long control's 54.25 %. Putting a trend
follower into a set whose whole premise is that its members are fades would corrupt the experiment.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MORN_A, MORN_B = 571, 689       # 09:31 - 11:29
DEC, EXIT = 708, 944            # decide 11:48, fill 11:49, hold to 15:44

# W108 out/cells.csv, the 50 % arm. The reproduction gate below asserts against these.
W108_5050 = {
    "VALUE_REACCEPT": (1011, -21.090959),
    "FAILED_BREAK":   (299, -225.346622),
    "EXHAUST_VOL":    (491, -309.125784),
    "EFFORT_NO_RES":  (540, -319.693333),
    "PATH_EFF_TRANS": (556, -38.343813),
}
FADES = ("EFFORT_NO_RES", "EXHAUST_VOL", "FAILED_BREAK", "PATH_EFF_TRANS", "VALUE_REACCEPT")
DEV = FADES[:3]                 # alphabetical, fixed in spec.yaml before any detector existed
HOLDOUT = FADES[3:]


def _trail(x, fn, look=250, minp=60):
    return getattr(pd.Series(x).rolling(look, min_periods=minp), fn)().shift(1).to_numpy()


def session_vwap(L):
    """RTH-anchored session VWAP, per bar. Shared by the fades and by detector D4."""
    rth = L.mod >= MORN_A
    pv = np.where(rth, L.c * L.v, 0.0)
    vv = np.where(rth, L.v, 0.0)
    cpv = pd.Series(pv).groupby(L.sid).cumsum().to_numpy()
    cvv = pd.Series(vv).groupby(L.sid).cumsum().to_numpy()
    return np.where(cvv > 0, cpv / np.maximum(cvv, 1e-9), L.c)


def build_fades(L):
    """Returns (MECH, ctx). MECH maps name -> (score, direction), both per-session."""
    NS = L.NS
    p0931 = L.at(MORN_A, use_open=True)
    p_dec = L.at(DEC)
    mh, ml = L.agg(MORN_A, MORN_B, "high"), L.agg(MORN_A, MORN_B, "low")
    mmid = (mh + ml) / 2.0
    absm = L.agg(MORN_A, MORN_B, "absmove")
    mvol = L.agg(MORN_A, MORN_B, "vol")
    morn_net = L.at(MORN_B) - p0931
    morn_dir = np.sign(morn_net)
    peff = np.abs(morn_net) / np.maximum(absm, 1e-9)

    vwap = session_vwap(L)
    vw_dec = L.at(DEC, arr=vwap)

    m2 = (L.mod > MORN_B) & (L.mod <= DEC)
    i2 = np.flatnonzero(m2)
    s2 = L.sid[i2]
    out_hi = np.zeros(NS); out_lo = np.zeros(NS); nbar = np.zeros(NS); above_vw = np.zeros(NS)
    np.add.at(out_hi, s2, (L.c[i2] > mh[s2]).astype(float))
    np.add.at(out_lo, s2, (L.c[i2] < ml[s2]).astype(float))
    np.add.at(nbar, s2, 1.0)
    np.add.at(above_vw, s2, (L.c[i2] > vwap[i2]).astype(float))
    inside = (p_dec <= mh) & (p_dec >= ml)

    mi = (L.mod >= MORN_A) & (L.mod <= MORN_B)
    ii = np.flatnonzero(mi)
    dfe = pd.DataFrame(dict(s=L.sid[ii], v=L.v[ii], h=L.h[ii], l=L.l[ii]))
    exz = np.zeros(NS); latevol = np.zeros(NS)
    for s, g in dfe.groupby("s"):
        if s >= NS or len(g) < 20:
            continue
        v_ = g["v"].to_numpy()
        md = float(np.median(v_)) or 1.0
        j = (int(np.argmax(g["h"].to_numpy())) if morn_dir[s] > 0
             else int(np.argmin(g["l"].to_numpy())))
        exz[s] = v_[j] / md
        latevol[s] = float(np.mean(v_[-10:])) / md if len(v_) >= 10 else 1.0

    MECH = {
        "VALUE_REACCEPT": (np.where(inside & ((out_hi + out_lo) > 0),
                                    (out_hi + out_lo) / np.maximum(nbar, 1), 0.0),
                           np.sign(mmid - p_dec)),
        "FAILED_BREAK":   (np.where(inside, (out_hi + out_lo) / np.maximum(nbar, 1), 0.0),
                           np.where(out_hi > out_lo, -1.0,
                                    np.where(out_lo > out_hi, 1.0, 0.0))),
        "EXHAUST_VOL":    (exz / np.maximum(latevol, 1e-9), -morn_dir),
        "EFFORT_NO_RES":  (mvol / np.maximum(_trail(mvol, "median"), 1e-9) * (1.0 - peff),
                           -morn_dir),
        "PATH_EFF_TRANS": ((1.0 - peff) * ((mh - ml) / np.maximum(_trail(mh - ml, "mean"), 1e-9)),
                           np.sign(mmid - p_dec)),
    }
    ctx = dict(p0931=p0931, p_dec=p_dec, mh=mh, ml=ml, mmid=mmid, absm=absm, mvol=mvol,
               morn_net=morn_net, morn_dir=morn_dir, peff=peff, vwap=vwap, vw_dec=vw_dec)
    return MECH, ctx
