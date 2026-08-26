"""W80 - a VECTORISED equivalent of we_quality.build_context.

`intraday_features` and `build_context` each contain per-session loops written as
`idx[sid == s]`, which is O(n) per session and therefore O(n x n_sess) overall. On the modern
window (1.6 M bars, 1,187 sessions) that is ~1.9e9 operations and takes ~20 s. On the deep
substrate (6.5 M bars, 4,279 sessions) it is ~2.8e10 and is not runnable.

Nothing here changes any definition. Every array must reproduce the original BIT-FOR-BIT, and
`verify()` is called before this module is used on data the originals have never been run on.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w03 import cd_signals                                        # noqa: E402


def _slices(D):
    starts = np.flatnonzero(D["fb"])
    ends = np.concatenate([starts[1:], [D["n"]]])
    return starts, ends


def fast_intraday_features(D):
    """Bit-identical to run_we_w09.intraday_features, without the O(n x n_sess) indexing."""
    n, sid = D["n"], D["sid"]
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    hm = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    rng = np.zeros(n); dmove = np.zeros(n)
    starts, ends = _slices(D)
    for a, b in zip(starts, ends):                       # O(n) total, not O(n x n_sess)
        hh = np.maximum.accumulate(h[a:b]); ll = np.minimum.accumulate(l[a:b])
        r = hh - ll
        rng[a:b] = np.concatenate([[0.0], r[:-1]])
        dm = np.abs(c[a:b] - o[a])
        dmove[a:b] = np.concatenate([[0.0], dm[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    atr = np.concatenate([[atr[0]], atr[:-1]])

    # Time-of-day norm. The original keeps, per minute-of-day, a LIST of rng values appended one
    # per session AFTER that session has been read, uses it only once it holds >= 20 entries, and
    # takes the median of its LAST 60 ENTRIES. Both details matter and an earlier draft of this
    # function got both wrong: a rolling window over SESSIONS is not a window over OBSERVATIONS
    # when a minute-of-day is absent from some sessions (holidays, half days), and the >= 20 gate
    # is on the WHOLE history, not on the count inside the 60-window.
    df = pd.DataFrame(dict(tod=hm, r=rng))
    g = df.groupby("tod")["r"]
    med = g.transform(lambda x: x.rolling(60, min_periods=1).median().shift(1)).to_numpy()
    prior = g.cumcount().to_numpy()                      # observations strictly before this one
    norm = np.where(prior >= 20, np.nan_to_num(med, nan=0.0), 0.0)
    return rng, dmove, atr, norm


def fast_build_context(D, ifeat=None):
    """Bit-identical to we_quality.build_context."""
    n = D["n"]
    c, o, v = D["c"], D["o"], D["v"]
    rng_, dmove, atr14, norm = ifeat if ifeat is not None else fast_intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)

    starts, ends = _slices(D)
    seg = np.repeat(np.arange(len(starts)), ends - starts)
    pv = pd.Series(c * v).groupby(seg).cumsum().to_numpy()
    vv = pd.Series(v).groupby(seg).cumsum().to_numpy()
    vwap = np.where(vv > 0, pv / np.maximum(vv, 1e-300), np.nan)
    sopen = np.repeat(o[starts], ends - starts)

    atr_l = np.concatenate([[atr14[0]], atr14[:-1]])
    vwap_l = np.concatenate([[np.nan], vwap[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    sess_ret = c[ends - 1] - o[starts]
    prev_ret = np.concatenate([[0.0], sess_ret[:-1]])[seg]

    up = np.concatenate([[0], np.sign(np.diff(c))])
    rl = np.zeros(n); r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        rl[i] = r * (1 if up[i] > 0 else -1)
    rl_l = np.concatenate([[0], rl[:-1]])
    volnorm = pd.Series(v).rolling(240, min_periods=30).mean().values
    delta_mag = np.concatenate([[0.0], (np.abs(cd) / np.maximum(volnorm, 1e-9))[:-1]])
    return dict(ratio=ratio, norm=norm, dL=dL, dS=dS, atr_l=atr_l,
                dist_open=(c_l - sopen) / np.maximum(atr_l, 1e-9),
                dist_vwap=(c_l - vwap_l) / np.maximum(atr_l, 1e-9),
                prev_ret=prev_ret, runlen=rl_l, delta_mag=delta_mag)


def verify(D, tol=0.0):
    """Compare against the ORIGINAL definitions. Must be called before use on new data."""
    from we_quality import build_context
    A = build_context(D)
    Bx = fast_build_context(D)
    bad = []
    for k in A:
        a, b = np.asarray(A[k]), np.asarray(Bx[k])
        if a.dtype == bool:
            ok = bool((a == b).all()); d = float((a != b).sum())
        else:
            d = float(np.nanmax(np.abs(a - b))) if a.size else 0.0
            ok = (d <= tol) and bool((np.isnan(a) == np.isnan(b)).all())
        if not ok:
            bad.append((k, d))
    return bad
