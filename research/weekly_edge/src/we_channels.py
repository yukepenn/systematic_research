"""WE_W72 helper - LATCHED INTRADAY CHANNELS that can occupy the object's OR slot.

W67 proved the object is `(>= k of NMEM members net-long) OR (channel == +1 and >= 1 member)`.
B-MOM is one named occupant of that slot. This module builds candidate occupants under B-MOM's
EXACT discipline so that the only thing differing between arms is the trigger:

    * latched: the last non-zero trigger persists until it flips
    * reset to 0 at the 09:31 bar (the RTH open bar, end-stamped)
    * forced to 0 from 15:57 and at every session end
    * decision at bar CLOSE, evaluated on bar-i data complete at bar i's close

Everything is vectorised; the incumbent's own vectorised reconstruction is compared against the
engine's cached `bmom` array as the module's correctness check.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RTH_OPEN = 93100
RTH_LAST_UPDATE = 155400
RTH_KILL = 155700
RTH_END = 160000


def session_clock(D):
    """hhmmss (bar-END stamped, as the engine does), RTH segment id, and the RTH mask."""
    t = D["t"]
    hm = (t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64)
    hhmmss = (hm // 3600) * 10000 + ((hm // 60) % 60) * 100
    is_open = hhmmss == RTH_OPEN
    seg = np.cumsum(is_open) - 1                       # -1 before the first 09:31 ever seen
    in_rth = (seg >= 0) & (hhmmss >= RTH_OPEN) & (hhmmss <= RTH_END)
    return hhmmss, seg, in_rth, int(is_open.sum())


def _latch(raw, seg, in_rth, hhmmss):
    """Carry the last non-zero trigger forward within an RTH segment; kill from 15:57."""
    s = pd.Series(np.where((raw != 0) & in_rth, raw, np.nan))
    out = s.groupby(seg).ffill().fillna(0.0).to_numpy()
    out[~in_rth] = 0.0
    out[hhmmss >= RTH_KILL] = 0.0
    return out.astype(np.int8)


def _cum_vwap(D, seg, in_rth):
    c, v = D["c"], D["v"]
    pv = pd.Series(np.where(in_rth, c * v, 0.0)).groupby(seg).cumsum().to_numpy()
    vv = pd.Series(np.where(in_rth, v, 0.0)).groupby(seg).cumsum().to_numpy()
    return np.where(vv > 0, pv / np.maximum(vv, 1e-12), c)


def _seg_open(D, seg, is_open_mask):
    o = D["o"]
    vals = o[is_open_mask]
    idx = np.maximum(seg, 0)
    return np.where(seg >= 0, vals[np.minimum(idx, len(vals) - 1)], np.nan)


def _mtod(absdisp, seg, hhmmss, in_rth, k=14, mask=None):
    """Trailing mean of |px - anchor| over the last k SEGMENTS at the SAME slot-of-day, using
    only segments strictly before the current one (the engine appends a day's slots at that
    day's session end, so today's own values are never in its own history).

    `mask` widens the set of bars the statistic is defined on; it defaults to the RTH window,
    which is what the incumbent uses. A channel that must fire outside RTH has to pass its own
    wider mask or the statistic is NaN there and the channel silently never fires."""
    m = (in_rth if mask is None else mask) & (seg >= 0)
    df = pd.DataFrame(dict(seg=seg[m], slot=hhmmss[m], x=absdisp[m]))
    # a slot can repeat inside one segment only if the feed is malformed; last wins, as the
    # engine's dict assignment does
    piv = df.pivot_table(index="seg", columns="slot", values="x", aggfunc="last")
    piv = piv.sort_index()
    roll = piv.rolling(k, min_periods=1).mean().shift(1)
    stacked = roll.stack(future_stack=True).rename("mtod").reset_index()
    out = np.full(len(absdisp), np.nan)
    key = pd.MultiIndex.from_arrays([seg[m], hhmmss[m]])
    lut = stacked.set_index(["seg", "slot"])["mtod"]
    out[m] = lut.reindex(key).to_numpy()
    return out


def _prev_session_hl(D):
    """Prior SESSION's high and low, broadcast to every bar of the following session."""
    sid, n_sess = D["sid"], D["n_sess"]
    hi = pd.Series(D["h"]).groupby(sid).max().to_numpy()
    lo = pd.Series(D["l"]).groupby(sid).min().to_numpy()
    phi = np.concatenate([[np.nan], hi[:-1]])
    plo = np.concatenate([[np.nan], lo[:-1]])
    return phi[sid], plo[sid]


def _ema(x, span):
    return pd.Series(x).ewm(span=span, adjust=False).mean().to_numpy()


def build_channels(D, which=None):
    """Return {name: int8 array}. Every channel obeys B-MOM's latch/reset discipline."""
    c, o, h, l = D["c"], D["o"], D["h"], D["l"]
    hhmmss, seg, in_rth, n_seg = session_clock(D)
    is_open_mask = hhmmss == RTH_OPEN
    vwap = _cum_vwap(D, seg, in_rth)
    op = _seg_open(D, seg, is_open_mask)
    warm = seg >= 14                                    # engine's rth_days >= 14
    upd = in_rth & warm & (hhmmss <= RTH_LAST_UPDATE)

    mtod = _mtod(np.abs(c - op), seg, hhmmss, in_rth)
    hi_band, lo_band = op + mtod, op - mtod

    # session-open anchored variants (X9a / X9b)
    sid = D["sid"]
    sess_open = pd.Series(o).groupby(sid).transform("first").to_numpy()
    mtod_s = _mtod(np.abs(c - sess_open), seg, hhmmss, in_rth)
    hi_s, lo_s = sess_open + mtod_s, sess_open - mtod_s
    # X9b fires across the WHOLE session, so its slot statistic must be defined there too
    all_bars = np.ones(len(c), bool)
    mtod_sa = _mtod(np.abs(c - sess_open), seg, hhmmss, in_rth, mask=all_bars)
    hi_sa, lo_sa = sess_open + mtod_sa, sess_open - mtod_sa

    # opening range 09:31-10:00
    orb_m = in_rth & (hhmmss <= 100000)
    orh = pd.Series(np.where(orb_m, h, -np.inf)).groupby(seg).transform("max").to_numpy()
    orl = pd.Series(np.where(orb_m, l, np.inf)).groupby(seg).transform("min").to_numpy()
    orb_live = upd & (hhmmss > 100000)

    phi, plo = _prev_session_hl(D)
    e_f, e_s = _ema(c, 20), _ema(c, 100)
    dh = pd.Series(h).rolling(60).max().shift(1).to_numpy()
    dl = pd.Series(l).rolling(60).min().shift(1).to_numpy()

    def mk(cond_up, cond_dn, live):
        raw = np.where(live & cond_up, 1, np.where(live & cond_dn, -1, 0)).astype(np.int8)
        return _latch(raw, seg, in_rth, hhmmss)

    ok = lambda a: np.nan_to_num(a, nan=np.inf)         # noqa: E731  (never triggers on nan)
    okn = lambda a: np.nan_to_num(a, nan=-np.inf)       # noqa: E731

    ch = {}
    ch["X0v_bmom"] = mk(c > np.maximum(ok(hi_band), vwap),
                        c < np.minimum(okn(lo_band), vwap), upd)
    ch["X1_vwap"] = mk(c > vwap, c < vwap, upd)
    ch["X2_disp"] = mk(c > ok(hi_band), c < okn(lo_band), upd)
    ch["X3_dispORvwap"] = mk((c > ok(hi_band)) | (c > vwap),
                             (c < okn(lo_band)) | (c < vwap), upd)
    ch["X4_orb30"] = mk(c > ok(orh), c < okn(orl), orb_live)
    ch["X5_pdhl"] = mk(c > ok(phi), c < okn(plo), upd)
    ch["X6_ema20_100"] = mk(e_f > e_s, e_f < e_s, upd)
    ch["X7_don60"] = mk(c > ok(dh), c < okn(dl), upd)
    ch["X8_openside"] = mk(c > op, c < op, upd)
    ch["X9a_disp_sessanchor"] = mk(c > ok(hi_s), c < okn(lo_s), upd)
    # X9b: same trigger as X9a but LIVE ALL SESSION (18:00 -> 15:57), latched per SESSION, so
    # it can also gate the overnight hours the incumbent leaves permanently empty.
    live_all = (seg >= 14) & (hhmmss < RTH_KILL)
    raw9b = np.where(live_all & (c > ok(hi_sa)), 1,
                     np.where(live_all & (c < okn(lo_sa)), -1, 0)).astype(np.int8)
    s9 = pd.Series(np.where(raw9b != 0, raw9b, np.nan))
    v9 = s9.groupby(sid).ffill().fillna(0.0).to_numpy()
    # the session runs 18:00 -> 17:00, so the kill window is 15:57..17:00 ONLY; zeroing every
    # bar with hhmmss >= 155700 would silently delete the entire 18:00-23:59 evening
    v9[(hhmmss >= RTH_KILL) & (hhmmss <= 170000)] = 0.0
    ch["X9b_disp_sess_allday"] = v9.astype(np.int8)
    if which:
        ch = {k: v for k, v in ch.items() if k in which}
    return ch


def channel_stats(x, D):
    """Firing rate, sign balance and mean latch run-length - the exposure controls."""
    nz = x != 0
    if not nz.any():
        return dict(fire_pct=0.0, long_pct=0.0, runs=0, mean_run=0.0)
    ch = np.flatnonzero(np.diff(x.astype(np.int16)) != 0) + 1
    runs = np.split(x, ch)
    lens = [len(r) for r in runs if r[0] != 0]
    return dict(fire_pct=100.0 * float(nz.mean()),
                long_pct=100.0 * float((x[nz] > 0).mean()),
                runs=len(lens), mean_run=float(np.mean(lens)) if lens else 0.0)


def shift_channel(x, D, k):
    """Session-wise circular shift: segment s receives segment (s+k)'s values indexed by
    POSITION WITHIN THE SEGMENT. Preserves firing rate, latch runs and intraday shape exactly;
    destroys only which day the path lands on."""
    hhmmss, seg, in_rth, n_seg = session_clock(D)
    out = np.zeros_like(x)
    idx = np.flatnonzero(in_rth)
    segs = seg[idx]
    starts = np.flatnonzero(np.diff(np.concatenate([[-1], segs])) != 0)
    bounds = list(starts) + [len(idx)]
    blocks = [idx[bounds[i]:bounds[i + 1]] for i in range(len(bounds) - 1)]
    nb = len(blocks)
    for i, b in enumerate(blocks):
        src = blocks[(i + k) % nb]
        m = min(len(b), len(src))
        out[b[:m]] = x[src[:m]]
    out[hhmmss >= RTH_KILL] = 0
    return out
