"""Alternative bar clocks for the TRUE engine (W41).

W32's clock verdict is only provisional because it re-implemented the ratchet and dropped the
HTF tilt, the hysteresis and the combiner (its 1-min arm scored 4.85 against the real object's
10.62). This module instead AGGREGATES BARS and hands them to the shipped `sm14_1m` unchanged.

Two construction facts that are not cosmetic:
  * sm14_1m arms B-MOM on `hhmmss == 93100` and keys its time-of-day baseline on the bar-END
    minute. An unanchored aggregate would never produce a bar ending at 09:31, silently
    disabling B-MOM and making the "true engine" claim false. Every clock here is therefore
    ANCHORED so that a bar boundary falls exactly at the 09:31 bar, and the same anchoring
    repeats every session so the slot history keys line up.
  * Aggregation never spans a session: sessions are the outer loop.

Each builder returns (D_coarse, end_idx) where end_idx[j] is the 1-MINUTE index of the last
bar inside coarse bar j, which is what `expand` needs to put the decision back on the 1-min
clock without look-ahead.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _pack(D, groups):
    """groups: list of arrays of 1-min indices, in order, never spanning a session."""
    n2 = len(groups)
    t = np.empty(n2, dtype=D["t"].dtype)
    o = np.empty(n2); h = np.empty(n2); l = np.empty(n2); c = np.empty(n2); v = np.empty(n2)
    sid = np.empty(n2, np.int64); end_idx = np.empty(n2, np.int64)
    for j, g in enumerate(groups):
        t[j] = D["t"][g[-1]]
        o[j] = D["o"][g[0]]; h[j] = D["h"][g].max(); l[j] = D["l"][g].min()
        c[j] = D["c"][g[-1]]; v[j] = D["v"][g].sum()
        sid[j] = D["sid"][g[0]]; end_idx[j] = g[-1]
    fb = np.zeros(n2, bool); fb[0] = True
    fb[1:] = sid[1:] != sid[:-1]
    lb = np.zeros(n2, bool); lb[:-1] = fb[1:]; lb[-1] = True
    D2 = dict(t=t, o=o, h=h, l=l, c=c, v=v, n=n2, fb=fb, lb=lb, sid=sid,
              n_sess=D["n_sess"], sess_end=D["sess_end"], sess_date=D["sess_date"],
              wk=D["wk"])
    return D2, end_idx


def _anchor_pos(D, m, hhmmss):
    """Local index inside session `m` of the 09:31 bar, or 0 if the session has no RTH."""
    a = np.where(hhmmss[m] == 93100)[0]
    return int(a[0]) if len(a) else 0


def clock_time(D, k):
    """k-minute bars, anchored so a bar ENDS at the 09:31 bar of every session."""
    if k == 1:
        return D, np.arange(D["n"], dtype=np.int64)
    hm = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
          .astype(np.int64))
    hhmmss = (hm // 3600) * 10000 + ((hm // 60) % 60) * 100
    idx = np.arange(D["n"])
    groups = []
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        a0 = _anchor_pos(D, m, hhmmss)
        g = np.arange(len(m)) - a0
        blk = np.floor_divide(g + k - 1, k)          # bar ends where g = blk*k
        for b in np.unique(blk):
            groups.append(m[blk == b])
    return _pack(D, groups)


def clock_volume(D, V):
    """Volume bars: close when cumulative volume >= V; forced close at 09:31 and session end."""
    hm = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
          .astype(np.int64))
    hhmmss = (hm // 3600) * 10000 + ((hm // 60) % 60) * 100
    idx = np.arange(D["n"])
    groups = []
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        cur = []; acc = 0.0
        for i in m:
            cur.append(i); acc += D["v"][i]
            if acc >= V or hhmmss[i] == 93100:
                groups.append(np.array(cur)); cur = []; acc = 0.0
        if cur:
            groups.append(np.array(cur))
    return _pack(D, groups)


def clock_range(D, R):
    """Range bars: close when the running high-low span >= R points; same forced boundaries."""
    hm = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
          .astype(np.int64))
    hhmmss = (hm // 3600) * 10000 + ((hm // 60) % 60) * 100
    idx = np.arange(D["n"])
    groups = []
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        cur = []; hi = -1e18; lo = 1e18
        for i in m:
            cur.append(i)
            hi = max(hi, D["h"][i]); lo = min(lo, D["l"][i])
            if (hi - lo) >= R or hhmmss[i] == 93100:
                groups.append(np.array(cur)); cur = []; hi = -1e18; lo = 1e18
        if cur:
            groups.append(np.array(cur))
    return _pack(D, groups)


def expand(tgt_coarse, end_idx, n):
    """Coarse decision at bar j becomes the 1-min position from its OWN last minute onward.

    The fill layer reads pos[i-1] and fills at o[i], so a decision made at the close of the
    coarse bar's last minute e_j is filled at the open of minute e_j+1. No look-ahead.
    """
    out = np.zeros(n, np.int8)
    for j in range(len(end_idx)):
        a = int(end_idx[j])
        b = int(end_idx[j + 1]) if j + 1 < len(end_idx) else n
        out[a:b] = tgt_coarse[j]
    return out


def size_for_rate(D, bars_per_session):
    """V and R that give the requested mean bars/session, so clocks are EVENT-RATE matched."""
    target = bars_per_session * D["n_sess"]
    V = float(D["v"].sum() / max(target, 1))
    tr = np.maximum(D["h"] - D["l"], 0.0)
    R = float(np.quantile(pd.Series(tr).rolling(3, min_periods=1).sum().values,
                          1.0 - target / D["n"])) if target < D["n"] else float(tr.mean())
    return V, max(R, 1.0)
