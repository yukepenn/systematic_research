"""ESNQ_V1 INDEPENDENT STREAMING implementation.  A2/A3 s7: a PRE-CANDIDATE gate.

INDEPENDENCE CONTRACT, and it is the whole point of this file:
  * it MAY import the certified generic utilities (research_sdk/timegrid.py);
  * it MUST NOT import or call esnq_batch's feature construction. It does not import esnq_batch
    at all. If both implementations shared feature logic they would inherit the same mistake, and
    the MS-BBO void proved that self-consistency is worth nothing.

It re-derives the frozen 11 features by a different mechanism: a single forward pass over the
merged event stream with BOUNDED per-series state and bisect lookups, rather than global
searchsorted over whole-session arrays. It independently enforces the 200 ms ES embargo and
independently emits max ES / NQ source timestamps.
"""
from __future__ import annotations

import bisect
import os
import sys
from collections import deque

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
from timegrid import NS_PER_S, lookback_offsets_s, session_grid_ns      # noqa: E402

PARQ = os.path.join(ROOT, "research", "data_esnq", "parquet")
RTH_START, RTH_END = "10:00:00", "15:30:00"
GRID_S, HORIZON_S = 60, 60
EMBARGO_NS = 200 * 1_000_000
RETAIN_NS = 130 * NS_PER_S   # >= 30s lookback + 60s horizon + margin
MAX_WAIT_MS = 1000.0
DPP, TK_NQ, TK_ES = 20.0, 0.25, 0.25
NEG = np.iinfo(np.int64).min


class Side:
    """One quote side: bounded ring of FINALIZED distinct-timestamp buckets (mean price)."""

    __slots__ = ("ts", "px", "_ot", "_s", "_n")

    def __init__(self):
        self.ts, self.px = deque(), deque()
        self._ot, self._s, self._n = None, 0.0, 0

    def add(self, t, p):
        if self._ot is None:
            self._ot, self._s, self._n = t, p, 1
        elif t == self._ot:
            self._s += p
            self._n += 1
        else:
            self._flush()
            self._ot, self._s, self._n = t, p, 1

    def _flush(self):
        if self._ot is not None:
            self.ts.append(self._ot)
            self.px.append(self._s / self._n)
            self._ot, self._s, self._n = None, 0.0, 0

    def close_before(self, t):
        if self._ot is not None and self._ot < t:
            self._flush()

    def evict(self, now):
        cut = now - RETAIN_NS
        while self.ts and self.ts[0] < cut:
            self.ts.popleft()
            self.px.popleft()

    def at_lt(self, q):
        i = bisect.bisect_left(self.ts, q) - 1
        return (self.px[i], self.ts[i]) if i >= 0 else (np.nan, NEG)

    def at_le(self, q):
        i = bisect.bisect_right(self.ts, q) - 1
        return (self.px[i], self.ts[i]) if i >= 0 else (np.nan, NEG)

    def count_in(self, lo, hi):
        """distinct timestamps in (lo, hi]"""
        return bisect.bisect_right(self.ts, hi) - bisect.bisect_right(self.ts, lo)

    def first_gt(self, q):
        i = bisect.bisect_right(self.ts, q)
        if i >= len(self.ts):
            return np.nan, np.inf, NEG
        return self.px[i], (self.ts[i] - q) / 1e6, self.ts[i]


def _events(inst, sd):
    d = pq.read_table(os.path.join(PARQ, inst, f"s{sd}.parquet"),
                      columns=["bip", "time", "price"]).to_pandas()
    t = d["time"].values.astype("datetime64[ns]").astype("int64")
    return t, d["bip"].values, d["price"].values


def session_features_stream(session_date, es_shift_ns=0):
    sd = session_date.replace("-", "")
    nt, nb_, np_ = _events("NQ", sd)
    et, eb_, ep_ = _events("ES", sd)
    if es_shift_ns:
        et = et + es_shift_ns
    day = int(pd.Timestamp(session_date).value)
    grid = session_grid_ns(day, RTH_START, RTH_END, GRID_S)
    off = lookback_offsets_s(30, 1)

    NQB, NQA, ESB, ESA = Side(), Side(), Side(), Side()
    # merge the two streams on timestamp; ES carries a tag so the embargo is applied per-source
    order = np.argsort(np.concatenate([nt, et]), kind="stable")
    allt = np.concatenate([nt, et])[order]
    allb = np.concatenate([nb_, eb_])[order]
    allp = np.concatenate([np_, ep_])[order]
    isnq = np.concatenate([np.ones(len(nt), bool), np.zeros(len(et), bool)])[order]

    n = len(allt)
    rows, pend = [], []
    # Decision k must see every event with ts < grid[k] ALREADY FINALIZED. Locate the segment
    # boundaries by index first, then flush-then-decide at each one. The first version decided
    # BEFORE flushing the open bucket, so a bucket at T < grid[k] was invisible to the decision --
    # which is exactly what the parity gate caught (nq_spread_tk off by 2.58 ticks).
    bnd = np.searchsorted(allt, grid, side="left")
    pos = 0
    for gk in range(len(grid)):
        stop = int(bnd[gk])
        for k in range(pos, stop):
            b = allb[k]
            if b == 1 or b == 2:
                if isnq[k]:
                    (NQB if b == 1 else NQA).add(allt[k], allp[k])
                else:
                    (ESB if b == 1 else ESA).add(allt[k], allp[k])
        pos = stop
        g = int(grid[gk])
        for sd_ in (NQB, NQA, ESB, ESA):
            sd_.close_before(g)          # FLUSH FIRST
            sd_.evict(g)
        rows.append(_decide(g, NQB, NQA, ESB, ESA, off, day))
        pend.append(rows[-1])
        _resolve(pend, NQB, NQA)
    for k in range(pos, n):
        b = allb[k]
        if b == 1 or b == 2:
            if isnq[k]:
                (NQB if b == 1 else NQA).add(allt[k], allp[k])
            else:
                (ESB if b == 1 else ESA).add(allt[k], allp[k])
        if (k & 0xFFFF) == 0:
            for sd_ in (NQB, NQA):
                sd_.close_before(allt[k])
            _resolve(pend, NQB, NQA)
    big = int(grid[-1]) + 10 ** 14
    for sd_ in (NQB, NQA, ESB, ESA):
        sd_.close_before(big)
    _resolve(pend, NQB, NQA)

    for r in rows:
        ok = all(np.isfinite(r[k]) for k in ("a_in", "b_in", "b_out", "a_out"))
        r["long_gross"] = (r["b_out"] - r["a_in"]) * DPP if ok else np.nan
        r["short_gross"] = (r["b_in"] - r["a_out"]) * DPP if ok else np.nan
        r["wait_ok"] = bool(ok and max(r["w1"], r["w2"], r["w3"], r["w4"]) <= MAX_WAIT_MS)
        r["session"] = session_date
    return pd.DataFrame(rows)


def _decide(t, NQB, NQA, ESB, ESA, off, day):
    tc = t - EMBARGO_NS
    src_nq, src_es = [], []
    fb, s1 = NQB.at_lt(t)
    fa, s2 = NQA.at_lt(t)
    src_nq += [s1, s2]
    nq_mid, nq_spread = (fb + fa) / 2.0, fa - fb
    eb, s3 = ESB.at_le(tc)
    ea, s4 = ESA.at_le(tc)
    src_es += [s3, s4]
    es_mid, es_spread = (eb + ea) / 2.0, ea - eb
    r = {"t": int(t)}
    for w in (1, 5, 15, 30):
        p1, a1 = NQB.at_lt(t - w * NS_PER_S)
        p2, a2 = NQA.at_lt(t - w * NS_PER_S)
        q1, a3 = ESB.at_le(tc - w * NS_PER_S)
        q2, a4 = ESA.at_le(tc - w * NS_PER_S)
        src_nq += [a1, a2]
        src_es += [a3, a4]
        r[f"rel_move_{w}s"] = ((es_mid - (q1 + q2) / 2.0) / es_mid
                               - (nq_mid - (p1 + p2) / 2.0) / nq_mid)
    npath, epath = np.empty(30), np.empty(30)
    for i, o in enumerate(off):
        p1, b1 = NQB.at_lt(t + int(o))
        p2, b2 = NQA.at_lt(t + int(o))
        q1, b3 = ESB.at_le(tc + int(o))
        q2, b4 = ESA.at_le(tc + int(o))
        src_nq += [b1, b2]
        src_es += [b3, b4]
        npath[i] = (p1 + p2) / 2.0
        epath[i] = (q1 + q2) / 2.0
    with np.errstate(all="ignore"):
        r["nq_rvol_30s"] = float(np.nanstd(np.diff(npath))) * DPP
        r["es_rvol_30s"] = float(np.nanstd(np.diff(epath))) / es_mid * 1e4
    r["es_bid_upd_30s"] = float(ESB.count_in(tc - 30 * NS_PER_S, tc))
    r["es_ask_upd_30s"] = float(ESA.count_in(tc - 30 * NS_PER_S, tc))
    r["es_spread_tk"] = es_spread / TK_ES
    r["nq_spread_tk"] = nq_spread / TK_NQ
    r["tod"] = (t - (day + int(pd.Timedelta(RTH_START).value))) / (3600 * NS_PER_S)
    r["max_nq_source_ts"] = int(max(src_nq))
    r["max_es_source_ts"] = int(max(src_es))
    r.update(a_in=np.nan, b_in=np.nan, b_out=np.nan, a_out=np.nan,
             w1=np.inf, w2=np.inf, w3=np.inf, w4=np.inf, entry_ts=NEG, exit_ts=NEG)
    return r


def _resolve(pend, NQB, NQA):
    keep = []
    for r in pend:
        t, th = r["t"], r["t"] + HORIZON_S * NS_PER_S
        if not np.isfinite(r["a_in"]):
            v, w, s = NQA.first_gt(t)
            if np.isfinite(v):
                r["a_in"], r["w1"], r["entry_ts"] = v, w, s
        if not np.isfinite(r["b_in"]):
            v, w, s = NQB.first_gt(t)
            if np.isfinite(v):
                r["b_in"], r["w2"] = v, w
        if not np.isfinite(r["b_out"]):
            v, w, s = NQB.first_gt(th)
            if np.isfinite(v):
                r["b_out"], r["w3"], r["exit_ts"] = v, w, s
        if not np.isfinite(r["a_out"]):
            v, w, s = NQA.first_gt(th)
            if np.isfinite(v):
                r["a_out"], r["w4"] = v, w
        if not (np.isfinite(r["b_out"]) and np.isfinite(r["a_out"])):
            keep.append(r)
    pend[:] = keep
