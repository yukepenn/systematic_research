"""MS-BBO STREAMING ENGINE - the same frozen object, computed event-by-event with BOUNDED state.

WHY THIS EXISTS.  Historical batch code reads a whole session as arrays. Prospective BBO data
arrives one event at a time, and a strategy that can only be computed from a completed day is not
a strategy. This engine is the proof that MS-BBO-CANDIDATE-1-DEPLOY can exist causally in real time.

RESOURCE SAFETY IS A HARD CONSTRAINT, not a preference. The DOM incident (2026-08-12) is binding:
no unbounded event accumulation, no day-long raw arrays, no full-depth retention. State here is
TIME-EVICTED ring buffers holding ~35 s of distinct-timestamp quote buckets - a few thousand
entries per side, flat in session length.

SAME-MILLISECOND SEMANTICS (directive s7) - the part that cannot be approximated.
    A bucket at timestamp T is NOT readable until it is FINALIZED, and it is finalized only when an
    event with a STRICTLY GREATER timestamp arrives. Until then more events may still join it.
        FEATURES   consume only FINALIZED buckets with T < t
        EXECUTION  the first FINALIZED bucket with T > t  (and > t+h), price = MEAN over the bucket
    Row order inside a millisecond is NEVER used - not first, not last, not as exported.

    The wait for a bucket to close is a BUCKET-FINALIZATION DELAY. It is recorded separately and
    it is NOT alpha latency.

WHAT THIS FILE MAY NOT DO.  It may not change what the signal means. It re-implements the frozen
feature definitions in streaming form; any disagreement with the batch implementation is a defect
in THIS file, to be fixed here - never by touching the frozen definition or tuning a threshold.
"""
from __future__ import annotations

import bisect
import json
import os
import sys
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(RUN), "MSBBO_V1_20260828", "src"))
import bbo_v1 as B                                                      # noqa: E402

NS = B.NS
RETAIN_NS = 35 * NS          # > the 30 s feature window, with headroom for the pre-window element
BID, ASK, TRADE = 1, 2, 0


class SideBook:
    """One quote side. TIME-EVICTED ring of FINALIZED distinct-timestamp buckets.

    Each finalized bucket stores (ts, mean price, is_up) where is_up compares against the
    IMMEDIATELY PRECEDING finalized bucket - reproducing the batch `sign(diff(p, prepend=p[0]))`
    convention, including its consequence that the very first bucket of the stream is never an
    up-move.
    """

    __slots__ = ("ts", "px", "up", "_ot", "_osum", "_on", "_prev_px", "_n_final")

    def __init__(self):
        self.ts, self.px, self.up = deque(), deque(), deque()
        self._ot = None                      # open (not yet finalized) bucket timestamp
        self._osum, self._on = 0.0, 0
        self._prev_px = None                 # last FINALIZED price, for the up-move sign
        self._n_final = 0

    def add(self, t, p):
        """Event arrives. Monotone non-decreasing timestamps assumed (asserted by the caller)."""
        if self._ot is None:
            self._ot, self._osum, self._on = t, p, 1
            return
        if t == self._ot:
            self._osum += p
            self._on += 1
            return
        self._finalize()
        self._ot, self._osum, self._on = t, p, 1

    def _finalize(self):
        if self._ot is None:
            return
        m = self._osum / self._on
        up = (self._prev_px is not None) and (m > self._prev_px)
        self.ts.append(self._ot)
        self.px.append(m)
        self.up.append(up)
        self._prev_px = m
        self._n_final += 1
        self._ot, self._osum, self._on = None, 0.0, 0

    def close_before(self, t):
        """Finalize the open bucket if it is strictly older than t.

        In replay this is exact. In live operation the same condition is reached either by the
        arrival of an event with ts > open_ts, or by the wall clock passing t - both of which
        guarantee no further event can join that bucket, because feed timestamps are monotone.
        """
        if self._ot is not None and self._ot < t:
            self._finalize()

    def evict(self, now):
        cut = now - RETAIN_NS
        while self.ts and self.ts[0] < cut:
            self.ts.popleft()
            self.px.popleft()
            self.up.popleft()

    # ---- readers.  All consume FINALIZED buckets only.
    def prev_at(self, q):
        """Price of the last finalized bucket with ts STRICTLY < q.  NaN if none retained."""
        i = bisect.bisect_left(self.ts, q) - 1
        return self.px[i] if i >= 0 else np.nan

    def window_counts(self, lo, hi):
        """(n updates, n up-moves) over finalized buckets with lo <= ts < hi."""
        a = bisect.bisect_left(self.ts, lo)
        b = bisect.bisect_left(self.ts, hi)
        n = b - a
        u = 0
        for k in range(a, b):
            if self.up[k]:
                u += 1
        return float(n), float(u)

    def first_after(self, q):
        """(price, wait_ms) of the first FINALIZED bucket with ts STRICTLY > q. None if not yet."""
        i = bisect.bisect_right(self.ts, q)
        if i >= len(self.ts):
            return None
        return self.px[i], (self.ts[i] - q) / 1e6

    def horizon_ready(self, q):
        """True once a finalized bucket with ts > q exists (or is provably unreachable)."""
        return bisect.bisect_right(self.ts, q) < len(self.ts)


class TradeBook:
    """Distinct-timestamp trade buckets. Order-invariant by construction: a bucket carries total
    volume and a volume-weighted mean price, and the signed flow is signed against the PRIOR
    DISTINCT TIMESTAMP - never against a neighbour inside the same millisecond.
    """

    __slots__ = ("ts", "vol", "sgn", "_ot", "_ov", "_opv", "_prev_vwap")

    def __init__(self):
        self.ts, self.vol, self.sgn = deque(), deque(), deque()
        self._ot, self._ov, self._opv = None, 0.0, 0.0
        self._prev_vwap = None

    def add(self, t, p, v):
        if self._ot is not None and t != self._ot:
            self._finalize()
        if self._ot is None:
            self._ot, self._ov, self._opv = t, 0.0, 0.0
        self._ov += v
        self._opv += p * v

    def _finalize(self):
        if self._ot is None:
            return
        vwap = self._opv / max(self._ov, 1e-9)
        s = 0.0 if self._prev_vwap is None else float(np.sign(vwap - self._prev_vwap))
        self.ts.append(self._ot)
        self.vol.append(self._ov)
        self.sgn.append(s * self._ov)
        self._prev_vwap = vwap
        self._ot, self._ov, self._opv = None, 0.0, 0.0

    def close_before(self, t):
        if self._ot is not None and self._ot < t:
            self._finalize()

    def evict(self, now):
        cut = now - RETAIN_NS
        while self.ts and self.ts[0] < cut:
            self.ts.popleft()
            self.vol.popleft()
            self.sgn.popleft()

    def window(self, lo, hi):
        a = bisect.bisect_left(self.ts, lo)
        b = bisect.bisect_left(self.ts, hi)
        n = float(b - a)
        vv = 0.0
        sf = 0.0
        for k in range(a, b):
            vv += self.vol[k]
            sf += self.sgn[k]
        return n, vv, sf


class StreamEngine:
    """The frozen candidate as a causal state machine. One instance per session."""

    def __init__(self, model, day_ns):
        m = model["model"]
        self.names = list(m["feature_names_ordered"])
        self.mu = np.array(m["feature_mean"], float)
        self.sd = np.array(m["feature_std"], float)
        self.coef = np.array(m["coef"], float)
        self.b0 = float(m["intercept"])
        self.bid, self.ask, self.trd = SideBook(), SideBook(), TradeBook()
        self.day = day_ns
        self.t0 = day_ns + _ns(B.RTH_START)
        self.grid = list(range(self.t0, day_ns + _ns(B.RTH_END) + 1, B.GRID_S * NS))
        self.gi = 0
        self.pending = deque()               # decisions awaiting their t+h exit legs
        self.rows = []
        self.max_state = 0

    # ---------------------------------------------------------------- features
    def features(self, t):
        """The frozen 20, in the frozen order, from FINALIZED buckets strictly before t."""
        fb, fa = self.bid.prev_at(t), self.ask.prev_at(t)
        mid = (fb + fa) / 2.0
        spread = fa - fb
        F = {"spread_tk": spread / B.TICK}
        for w in (1, 5, 15, 30):
            q = t - w * NS
            m0 = (self.bid.prev_at(q) + self.ask.prev_at(q)) / 2.0
            F[f"midret_{w}s"] = (mid - m0) * B.DPP
        paths = np.empty(30)
        sp_path = np.empty(30)
        for k, s in enumerate(range(-30, 0)):
            q = t + s * NS
            pb, pa = self.bid.prev_at(q), self.ask.prev_at(q)
            paths[k] = (pb + pa) / 2.0
            sp_path[k] = pa - pb
        with np.errstate(all="ignore"):
            F["rvol_30s"] = float(np.nanstd(np.diff(paths))) * B.DPP
            hi, lo = float(np.nanmax(paths)), float(np.nanmin(paths))
            F["range_30s"] = (hi - lo) * B.DPP
            F["dist_hi_30s"] = (hi - mid) * B.DPP
            F["dist_lo_30s"] = (mid - lo) * B.DPP
            F["spread_chg_30s"] = (spread - sp_path[0]) / B.TICK
            F["spread_minfrac"] = float(np.nanmean(np.isclose(sp_path, np.nanmin(sp_path))))
            F["spread_pctile"] = float(np.nanmean(sp_path <= spread))
        lo_t = t - 30 * NS
        for nm, bk in (("bid", self.bid), ("ask", self.ask)):
            n, u = bk.window_counts(lo_t, t)
            F[f"{nm}_upd_30s"], F[f"{nm}_up_30s"] = n, u
        n, vv, sf = self.trd.window(lo_t, t)
        F["trade_buckets_30s"], F["trade_vol_30s"], F["signed_flow_30s"] = n, vv, sf
        F["tod"] = (t - self.t0) / (3600 * NS)
        return F, mid, spread

    def predict(self, F):
        x = np.array([F[n] for n in self.names], float)
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        z = np.zeros_like(x)
        nz = self.sd != 0
        z[nz] = (x[nz] - self.mu[nz]) / self.sd[nz]
        return self.b0 + float(z @ self.coef), x

    # ---------------------------------------------------------------- event loop
    def on_event(self, bip, t, price, volume):
        # 1. FINALIZE anything strictly older than this event's timestamp
        self.bid.close_before(t)
        self.ask.close_before(t)
        self.trd.close_before(t)
        # 2. any decision whose grid time has been passed by finalized state is now computable
        while self.gi < len(self.grid) and self.grid[self.gi] < t:
            self._decide(self.grid[self.gi])
            self.gi += 1
        self._resolve(t)
        # 3. ingest
        if bip == BID:
            self.bid.add(t, price)
        elif bip == ASK:
            self.ask.add(t, price)
        else:
            self.trd.add(t, price, volume)
        # 4. bounded state
        self.bid.evict(t)
        self.ask.evict(t)
        self.trd.evict(t)
        n = len(self.bid.ts) + len(self.ask.ts) + len(self.trd.ts)
        if n > self.max_state:
            self.max_state = n

    def _decide(self, t):
        F, mid, spread = self.features(t)
        pred, xraw = self.predict(F)
        thr = F["spread_tk"] * B.TICK * B.DPP + B.COMMISSION_RT
        act = 1 if pred > thr else (-1 if pred < -thr else 0)
        row = {"t": t, "pred": pred, "thr": thr, "action": act, "mid": mid,
               "feat": xraw, "gap": bool(np.isnan(xraw).any() or np.isinf(xraw).any()),
               "a_in": None, "b_in": None, "b_out": None, "a_out": None,
               "wa_in": np.inf, "wb_in": np.inf, "wb_out": np.inf, "wa_out": np.inf,
               "fin_delay_ms": None}
        self.rows.append(row)
        self.pending.append(row)

    def _resolve(self, now):
        """Fill legs resolve from FINALIZED buckets only, strictly after their reference instant."""
        keep = deque()
        for r in self.pending:
            t, th = r["t"], r["t"] + B.HORIZON_S * NS
            if r["a_in"] is None:
                g = self.ask.first_after(t)
                if g:
                    r["a_in"], r["wa_in"] = g
            if r["b_in"] is None:
                g = self.bid.first_after(t)
                if g:
                    r["b_in"], r["wb_in"] = g
            if r["b_out"] is None:
                g = self.bid.first_after(th)
                if g:
                    r["b_out"], r["wb_out"] = g
            if r["a_out"] is None:
                g = self.ask.first_after(th)
                if g:
                    r["a_out"], r["wa_out"] = g
            if r["fin_delay_ms"] is None and (r["a_in"] is not None or r["b_in"] is not None):
                r["fin_delay_ms"] = (now - t) / 1e6
            if not (r["b_out"] is not None and r["a_out"] is not None):
                keep.append(r)
        self.pending = keep

    def finish(self):
        """End of feed. Finalize, run any remaining decisions, resolve what can still resolve."""
        big = (self.grid[-1] if self.grid else 0) + 10 ** 15
        self.bid.close_before(big)
        self.ask.close_before(big)
        self.trd.close_before(big)
        while self.gi < len(self.grid):
            self._decide(self.grid[self.gi])
            self.gi += 1
        self._resolve(big)
        for r in self.rows:
            ok = all(r[k] is not None for k in ("a_in", "b_in", "b_out", "a_out"))
            r["long_gross"] = (r["b_out"] - r["a_in"]) * B.DPP if ok else np.nan
            r["short_gross"] = (r["b_in"] - r["a_out"]) * B.DPP if ok else np.nan
            r["wait_ok"] = bool(ok and max(r["wa_in"], r["wb_in"],
                                           r["wb_out"], r["wa_out"]) <= B.MAX_FILL_WAIT_MS)
            if r["gap"]:
                q = "GAP"
            elif not ok:
                q = "NO_FILL"
            elif not r["wait_ok"]:
                q = "FILL_TIMEOUT"
            else:
                q = "OK"
            r["data_quality"] = q
        return self.rows


def _ns(hhmmss):
    h, m, s = (int(v) for v in hhmmss.split(":"))
    return ((h * 60 + m) * 60 + s) * NS


def load_model(path=None):
    return json.loads(open(path or os.path.join(RUN, "model.json"), "r",
                          encoding="utf-8").read())
