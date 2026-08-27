"""we_lab - the shared bench for NEW-ENGINE research (owner directive V4 sections 7-9).

One substrate loader, one feature block, one evaluator, one dashboard, three nulls. Every new
mechanism track plugs a causal target array into `evaluate()` and gets the SAME numbers under the
SAME cost model, so two tracks are comparable without a translation step.

Costs: commission $4.36/ctrRT inside the fill engine, plus the candidate's OWN contract-weighted
spread from W82's committed per-minute profile. The two are additive and never double-counted -
W89 established the profile is pure spread (2.904 ticks x $5 = $14.52 for P1).

Nothing here decides anything. It measures.
"""
from __future__ import annotations

import itertools
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
from run_we_w98 import gfills, arm_kw                                    # noqa: E402

W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
WINDOWS = [("FULL", "2022-07-01", "2026-08-01"), ("2024+", "2024-01-01", "2026-08-01"),
           ("2025", "2025-01-01", "2026-01-01"), ("2026YTD", "2026-01-01", "2026-08-01"),
           ("t12m", "2025-08-01", "2026-08-01"), ("t6m", "2026-02-01", "2026-08-01"),
           ("t3m", "2026-05-01", "2026-08-01")]


def spread_profile():
    """W82's committed per-minute spread, in ticks, with the 17:00 bar filled from 16:59."""
    p = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    p = p.reindex(range(1440))
    p.loc[1020:1079] = p.loc[1019]
    return p


class Bench:
    """Substrate + features + evaluator, built once and reused by every track."""

    def __init__(self, a="2022-01-01", b="2026-07-31 17:00", lo=A, hi=B, extend=True,
                 deep=False):
        self.D = load_deep(a, b, extend=extend)
        W1.DEV_END = pd.Timestamp("2026-07-31").date()
        D = self.D
        self.n = D["n"]
        self.t, self.sid, self.lb, self.fb = D["t"], D["sid"], D["lb"], D["fb"]
        self.o, self.c, self.h, self.l, self.v = D["o"], D["c"], D["h"], D["l"], D["v"]
        self.st, self.en, self.elapsed = session_frames(D)
        self.klass = classify(D, self.st, self.en)
        self.mod = ((self.t - self.t.astype("datetime64[D]")).astype("timedelta64[s]")
                    .astype(np.int64) // 60).astype(np.int32)
        self.bidx = np.arange(self.n) - self.st[self.sid]
        self.prof = spread_profile()
        self.sp_tk = self.prof.reindex(self.mod).to_numpy()
        if np.isnan(self.sp_tk).any():
            raise ValueError("a bar minute is not covered by the spread profile")
        self.sess_in = np.array([s for s in range(D["n_sess"])
                                 if lo <= self.t[self.st[s]] < hi])
        self.in_win = np.zeros(D["n_sess"], bool); self.in_win[self.sess_in] = True
        self.sdate = pd.to_datetime(D["sess_date"])[self.sess_in]
        iso = self.sdate.isocalendar()
        self.wk = (iso["year"].astype(str) + "-W" +
                   iso["week"].astype(str).str.zfill(2)).to_numpy()
        self.NW = len(set(self.wk))
        sd = self.sdate.to_numpy()
        self.MASK = {w: (sd >= np.datetime64(x)) & (sd < np.datetime64(y))
                     for w, x, y in WINDOWS}
        # flat-at-session-close guard shared by every engine here
        self.flatm = self.t >= D["sess_end"][self.sid] - np.timedelta64(21 * 60, "s")
        self._feat = None

    # ---------------------------------------------------------------- features
    def _sess_cum(self, x):
        cs = np.cumsum(x)
        return cs - np.r_[0.0, cs[:-1]][self.st[self.sid]]

    def _sess_roll(self, x, k, fn):
        """causal rolling over the last k bars, never crossing a session start"""
        s = pd.Series(x).rolling(k, min_periods=k).apply(fn, raw=True).to_numpy() \
            if fn is not None else pd.Series(x).rolling(k, min_periods=k).mean().to_numpy()
        s[self.bidx < k - 1] = np.nan
        return s

    def _roll_mean(self, x, k):
        s = pd.Series(x).rolling(k, min_periods=k).mean().to_numpy()
        s[self.bidx < k - 1] = np.nan
        return s

    def _roll_std(self, x, k):
        s = pd.Series(x).rolling(k, min_periods=k).std(ddof=0).to_numpy()
        s[self.bidx < k - 1] = np.nan
        return s

    def features(self):
        """Everything is CAUSAL: computed from bars <= i and acted on at bar i+1's open."""
        if self._feat is not None:
            return self._feat
        c, o, h, l, v = self.c, self.o, self.h, self.l, self.v
        F = {}
        rng = h - l
        body = np.abs(c - o)
        F["rng"] = rng
        F["body"] = body
        F["clv"] = np.where(rng > 0, (c - l) / np.maximum(rng, 1e-9), 0.5)
        tr = np.maximum(h, np.r_[c[0], c[:-1]]) - np.minimum(l, np.r_[c[0], c[:-1]])
        tr[self.fb] = rng[self.fb]
        F["atr20"] = self._roll_mean(tr, 20)
        # --- volume, the axis this program has never used
        F["vmean20"] = self._roll_mean(v, 20)
        F["vsd20"] = self._roll_std(v, 20)
        F["vz"] = (v - F["vmean20"]) / np.maximum(F["vsd20"], 1e-9)
        F["relvol"] = v / np.maximum(F["vmean20"], 1e-9)
        F["rngz"] = (rng - self._roll_mean(rng, 20)) / np.maximum(self._roll_std(rng, 20), 1e-9)
        # --- realized semivariance, the axis that attacks the short-side weakness
        r = np.r_[0.0, np.diff(c)]
        r[self.fb] = 0.0
        F["rsv_dn"] = np.sqrt(np.maximum(self._roll_mean(np.where(r < 0, r * r, 0.0), 30), 0.0))
        F["rsv_up"] = np.sqrt(np.maximum(self._roll_mean(np.where(r > 0, r * r, 0.0), 30), 0.0))
        F["rsv_share"] = F["rsv_dn"] / np.maximum(F["rsv_dn"] + F["rsv_up"], 1e-9)
        # --- session anchors and VWAP
        tp = (h + l + c) / 3.0
        F["vwap"] = self._sess_cum(tp * v) / np.maximum(self._sess_cum(v), 1e-9)
        F["vwap_z"] = (c - F["vwap"]) / np.maximum(F["atr20"], 1e-9)
        F["vwap_slope"] = (F["vwap"] - np.r_[np.nan, F["vwap"][:-1]]) / np.maximum(F["atr20"], 1e-9)
        op = np.zeros(self.D["n_sess"]); m9 = self.mod == 570
        op[self.sid[m9]] = o[m9]
        F["open930"] = op[self.sid]
        orbh = np.full(self.D["n_sess"], -np.inf); orbl = np.full(self.D["n_sess"], np.inf)
        ii = np.flatnonzero((self.mod >= 570) & (self.mod < 585))
        np.maximum.at(orbh, self.sid[ii], h[ii]); np.minimum.at(orbl, self.sid[ii], l[ii])
        F["orb_h"] = orbh[self.sid]; F["orb_l"] = orbl[self.sid]
        self._feat = F
        return F

    # ---------------------------------------------------------------- evaluation
    def i_of(self, ts):
        return int(min(np.searchsorted(self.t, np.datetime64(ts)), self.n - 1))

    def run(self, tgt, size=None, box="PCT", halt=1300.0, tgt_usd=1000.0, flat_close=True):
        """tgt: causal signed target per bar. Returns the in-window trade list."""
        g = np.asarray(tgt, np.int8).copy()
        if flat_close:
            g[self.flatm] = 0
        kw = dict(halt=halt, target=tgt_usd, per_ctr=(box == "PCT"))
        tr = gfills(self.D, g, size, **kw)
        return [x for x in tr if self.in_win[int(self.sid[self.i_of(x["et"])])]]

    def rate(self, trl):
        w = {}
        for x in trl:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts)
                m_ = p_.hour * 60 + p_.minute
                w[m_] = w.get(m_, 0.0) + x["u"]
        tot = sum(w.values())
        if tot <= 0:
            return 0.0
        return TICKV * sum(float(self.prof.get(m, 3.0)) * q for m, q in w.items()) / tot

    def series(self, trl):
        """(net-of-friction session P&L over the window, contracts per session, $/ctrRT)"""
        sp = np.zeros(self.D["n_sess"]); ct = np.zeros(self.D["n_sess"])
        for x in trl:
            s_ = int(self.sid[self.i_of(x["et"])])
            sp[s_] += x["pnl"]; ct[s_] += x["u"]
        r = self.rate(trl)
        return sp[self.sess_in] - r * ct[self.sess_in], ct[self.sess_in], r

    def expo(self, trl):
        p = np.zeros(self.n)
        for x in trl:
            a_, b_ = self.i_of(x["et"]), self.i_of(x["xt"])
            p[a_:(b_ + 1 if self.lb[b_] else b_)] += x["u"]
        return p

    def dash(self, trl, window="FULL", name=""):
        ser, ct, r = self.series(trl)
        m = self.MASK[window]
        wv = pd.Series(ser[m]).groupby(self.wk[m]).sum().to_numpy()
        dp = dd_profile(wv)
        stk = max((len(list(g)) for k, g in itertools.groupby(wv < 0) if k), default=0)
        cq = max(1, int(round(0.05 * len(wv))))
        ex = self.expo(trl)
        keeps = np.zeros(self.D["n_sess"], bool); keeps[self.sess_in[m]] = True
        exw = ex[keeps[self.sid]]
        held = exw[exw > 0]
        return dict(
            name=name, window=window, nsess=int(m.sum()), nwk=len(wv),
            trades=int(sum(1 for x in trl
                           if m[np.searchsorted(self.sess_in,
                                                int(self.sid[self.i_of(x["et"])]))])),
            contracts=float(ct[m].sum()), rate=r,
            net=float(ser[m].sum()), weekly=float(wv.mean()),
            weekly_fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
            pts_sess=float(ser[m].sum()) / max(m.sum(), 1) / PV,
            posday=100 * float((ser[m] > 0).mean()), poswk=100 * float((wv > 0).mean()),
            medwk=float(np.median(wv)), maxdd=dp["maxdd"], top5=dp["dd_mean_top5"],
            worst=float(wv.min()), cvar5=float(np.sort(wv)[:cq].mean()), streak=int(stk),
            ctrmin=float(exw.sum()), peak=float(exw.max()) if len(exw) else 0.0,
            meansz=float(held.mean()) if len(held) else 0.0,
            ppcm=float(ser[m].sum()) / max(exw.sum(), 1e-9),
            t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(max(len(wv), 2)), 1e-9))

    HEAD = (f"{'name':<22}{'window':<9}{'trades':>8}{'ctr':>8}{'$/RT':>7}{'net $':>11}"
            f"{'wk$':>8}{'wk$@fixDD':>11}{'wk+%':>7}{'day+%':>7}{'maxDD':>10}{'top5':>9}"
            f"{'strk':>5}{'t':>6}")

    @staticmethod
    def line(d):
        return (f"{d['name']:<22}{d['window']:<9}{d['trades']:>8,}{d['contracts']:>8,.0f}"
                f"{d['rate']:>7.2f}{d['net']:>11,.0f}{d['weekly']:>8,.0f}"
                f"{d['weekly_fixdd']:>11,.0f}{d['poswk']:>6.1f}%{d['posday']:>6.1f}%"
                f"{d['maxdd']:>10,.0f}{d['top5']:>9,.0f}{d['streak']:>5}{d['t']:>6.2f}")

    # ---------------------------------------------------------------- nulls
    def null_circular_shift(self, tgt, k, rng, size=None, **kw):
        """shift the SIGNAL relative to the price path; preserves the signal's own structure"""
        sh = int(rng.integers(720, self.n - 720))
        return self.run(np.roll(np.asarray(tgt), sh), size, **kw)

    def null_sign_permute(self, trl, rng):
        """hold the trade SCHEDULE fixed and permute the directions - the harder null (W93)"""
        d = np.array([x["d"] for x in trl])
        perm = rng.permutation(d)
        out = []
        for x, dd in zip(trl, perm):
            y = dict(x)
            if dd != x["d"]:
                y["pnl"] = -(x["pnl"] + COMM_RT * x["u"]) - COMM_RT * x["u"]
                y["d"] = int(dd)
            out.append(y)
        return out

    def null_count_matched(self, tgt, rng, size=None, **kw):
        """same number of entries, placed at uniformly random eligible bars, same hold lengths"""
        g = np.asarray(tgt)
        ent = np.flatnonzero((g != 0) & (np.r_[0, g[:-1]] == 0))
        if not len(ent):
            return []
        holds = np.diff(np.r_[ent, self.n])
        holds = np.minimum(holds, 240)
        gg = np.zeros(self.n, np.int8)
        picks = rng.choice(self.n - 300, size=len(ent), replace=False)
        for p_, hh in zip(picks, holds):
            gg[p_:p_ + max(int(hh), 1)] = int(rng.choice([-1, 1]))
        return self.run(gg, size, **kw)
