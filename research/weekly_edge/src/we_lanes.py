"""we_lanes - shared machinery for the three parallel discovery lanes (owner amendment section 6).

One substrate, one session frame, one trade evaluator, one OUTCOME-BLIND rate calibrator, one coin
null. All three lanes use these so their numbers are directly comparable.

THE CALIBRATOR IS THE POINT. W100 failed because its gates accepted ~92 % of the target leg and
therefore could not separate anything. Here `causal_threshold` sets a threshold from the TRAILING
250 SESSIONS of the FEATURE ONLY - it never sees P&L - so the acceptance rate is achieved by
construction before any economics is computed.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
QLOOK = 250          # trailing sessions for every causal quantile
QMIN = 60            # minimum history before a threshold exists
RATES = (0.25, 0.50, 0.75)


class LaneBench:
    def __init__(self):
        self.prof = spread_profile()
        D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
        W1.DEV_END = pd.Timestamp("2026-07-31").date()
        self.D = D
        self.n, self.t, self.sid = D["n"], D["t"], D["sid"]
        self.o, self.c, self.h, self.l, self.v = D["o"], D["c"], D["h"], D["l"], D["v"]
        self.st, self.en, _ = session_frames(D)
        self.klass = classify(D, self.st, self.en)
        self.mod = ((self.t - self.t.astype("datetime64[D]")).astype("timedelta64[s]")
                    .astype(np.int64) // 60).astype(np.int32)
        self.NS = D["n_sess"]
        self.sdate = pd.to_datetime(D["sess_date"])
        iso = self.sdate.isocalendar()
        self.wkall = (iso["year"].astype(str) + "-W" +
                      iso["week"].astype(str).str.zfill(2)).to_numpy()
        self.win = np.array([A <= self.t[self.st[s]] < B for s in range(self.NS)])
        self.sess_in = np.flatnonzero(self.win)
        self.wk = self.wkall[self.sess_in]

    # ---------------------------------------------------------------- session-level accessors
    def at(self, mv, use_open=False, arr=None):
        """value at the bar stamped `mv` in each session; NaN where the bar is absent"""
        r = np.full(self.NS, np.nan)
        m = self.mod == mv
        src = self.o if use_open else (self.c if arr is None else arr)
        r[self.sid[m]] = src[m]
        return r

    def idx_at(self, mv):
        r = np.full(self.NS, -1, np.int64)
        m = self.mod == mv
        r[self.sid[m]] = np.flatnonzero(m)
        return r

    def agg(self, lo, hi, what):
        """per-session aggregate over the bars stamped [lo, hi]: max/min/sum/first/last/absmove"""
        m = (self.mod >= lo) & (self.mod <= hi)
        ii = np.flatnonzero(m)
        s = self.sid[ii]
        if what == "high":
            r = np.full(self.NS, -np.inf); np.maximum.at(r, s, self.h[ii]); r[r == -np.inf] = np.nan
        elif what == "low":
            r = np.full(self.NS, np.inf); np.minimum.at(r, s, self.l[ii]); r[r == np.inf] = np.nan
        elif what == "vol":
            r = np.zeros(self.NS); np.add.at(r, s, self.v[ii])
        elif what == "absmove":
            d = np.abs(np.r_[0.0, np.diff(self.c)])[ii]
            r = np.zeros(self.NS); np.add.at(r, s, d)
        else:
            raise KeyError(what)
        return r

    # ---------------------------------------------------------------- the calibrator
    @staticmethod
    def causal_threshold(feat, q, lookback=QLOOK, minhist=QMIN):
        """trailing causal quantile of a per-session feature. Uses ONLY prior sessions, and ONLY
        the feature - never an outcome. NaN until `minhist` prior values exist."""
        s = pd.Series(feat)
        return s.rolling(lookback, min_periods=minhist).quantile(q).shift(1).to_numpy()

    @classmethod
    def accept(cls, feat, rate):
        """boolean per session: is the feature in its top `rate` fraction, causally?"""
        thr = cls.causal_threshold(feat, 1.0 - rate)
        return np.isfinite(feat) & np.isfinite(thr) & (feat >= thr)

    # ---------------------------------------------------------------- the trade evaluator
    def trade(self, desired, dec_mod, exit_mod):
        """one entry at the (dec_mod+1) open, one exit at `exit_mod`'s close, size 1.
        Returns (pnl per session, taken mask, cost, E|move|)."""
        pe = self.at(dec_mod + 1, use_open=True)
        px = self.at(exit_mod)
        cost = COMM_RT + TICKV * (float(self.prof.loc[dec_mod + 1]) +
                                  float(self.prof.loc[exit_mod])) / 2.0
        take = self.win & np.isfinite(pe) & np.isfinite(px) & (np.asarray(desired) != 0)
        pnl = np.zeros(self.NS)
        pnl[take] = np.asarray(desired)[take] * (px[take] - pe[take]) * PV - cost
        elig = self.win & np.isfinite(pe) & np.isfinite(px)
        emove = float(np.abs((px - pe)[elig]).mean()) * PV
        return pnl, take, cost, emove

    def stats(self, pnl, take, cost, emove):
        pn = pnl[take]
        if len(pn) < 10:
            return None
        ser = np.zeros(self.NS); ser[take] = pn
        wv = pd.Series(ser[self.sess_in]).groupby(self.wk).sum().to_numpy()
        dp = dd_profile(wv)
        return dict(n=int(take.sum()), hit=100 * float((pn > 0).mean()),
                    per_trade=float(pn.mean()), net=float(pn.sum()),
                    p_star=0.5 * (1 + cost / max(emove, 1e-9)),
                    weekly=float(wv.mean()),
                    fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((wv > 0).mean()),
                    t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9))

    # ---------------------------------------------------------------- the null
    @staticmethod
    def coin_null(cells, rng, nperm=200):
        """cells: list of (move_array_over_taken, cost). Returns (mean-dist, max-dist)."""
        mn = np.empty(nperm); mx = np.empty(nperm)
        for b in range(nperm):
            vals = []
            for mv, cst in cells:
                if len(mv) < 10:
                    continue
                s = rng.choice([-1.0, 1.0], size=len(mv))
                vals.append(float((s * mv - cst).mean()))
            mn[b] = np.mean(vals) if vals else np.nan
            mx[b] = np.max(vals) if vals else np.nan
        return mn, mx

    # ---------------------------------------------------------------- reporting helpers
    def by_class(self, pnl, take):
        out = {}
        for k in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
            m = take & (self.klass == k)
            out[k] = (int(m.sum()), float(pnl[m].mean()) if m.sum() else np.nan)
        return out

    def weekly(self, pnl, take):
        ser = np.zeros(self.NS); ser[take] = pnl[take]
        return pd.Series(ser[self.sess_in]).groupby(self.wk).sum().to_numpy()
