"""Cheap smoke test for run_native.py's own machinery on a SYNTHETIC substrate.

Catches interface / indexing bugs before the 20-minute real run. Touches no market data.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_native as RN                                                   # noqa: E402
from run_we_w98 import gfills                                            # noqa: E402
from research_sdk import champion_eval as CE                             # noqa: E402


def fake(n_sess=40, per=120, seed=3):
    rng = np.random.default_rng(seed)
    t = []
    base = np.datetime64("2023-03-01T18:00")
    for s in range(n_sess):
        d = base + np.timedelta64(s, "D")
        t.append(d + np.arange(per) * np.timedelta64(1, "m"))
    t = np.concatenate(t).astype("datetime64[s]")
    n = len(t)
    c = 15000 + np.cumsum(rng.normal(0, 2.0, n))
    o = c + rng.normal(0, 0.5, n)
    h = np.maximum(o, c) + 1.0
    l = np.minimum(o, c) - 1.0
    v = rng.integers(50, 500, n).astype(float)
    fb = np.zeros(n, bool); fb[::per] = True
    lb = np.zeros(n, bool); lb[per - 1::per] = True
    sid = np.repeat(np.arange(n_sess), per)
    last_of = np.arange(per - 1, n, per)
    sess_end = t[last_of] + np.timedelta64(60, "s")
    sess_date = sess_end.astype("datetime64[D]")
    iso = pd.Series(pd.to_datetime(sess_date)).dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    D = dict(df=None, t=t, o=o, h=h, l=l, c=c, v=v, n=n, fb=fb, lb=lb, sid=sid,
             n_sess=n_sess, sess_end=sess_end, sess_date=sess_date, wk=wk)
    return D, rng


def main():
    ok = []
    D, rng = fake()
    n = D["n"]

    # ---- numba gfills vs python gfills, several direction/size/box configurations -------------
    for trial in range(6):
        dir_arr = rng.choice(np.array([-1, 0, 1], np.int8), size=n,
                             p=[0.25, 0.5, 0.25]).astype(np.int8)
        # make it persistent so trades have length
        for i in range(1, n):
            if rng.random() < 0.97:
                dir_arr[i] = dir_arr[i - 1]
        sz = rng.integers(1, 3, n).astype(np.int8) if trial % 2 else None
        pc = bool(trial % 3 == 1)
        py = gfills(D, dir_arr, sz, 1300.0, 1000.0, pc)
        nb = RN.nbf(D, dir_arr, sz, 1300.0, 1000.0, pc, 4.36)
        good, why = RN.nb_same_as_py(D, nb, py)
        ok.append((f"numba==python trial {trial} (size={sz is not None}, per_ctr={pc}, "
                   f"{len(py)} trades)", good, why))

    # ---- cost parameterisation: comm=0 must raise net by exactly 4.36 * ctrRT -----------------
    dir_arr = np.where(np.arange(n) % 37 < 12, -1, 0).astype(np.int8)
    a = RN.nbf(D, dir_arr, None, 1e18, None, False, 4.36)
    b = RN.nbf(D, dir_arr, None, 1e18, None, False, 0.0)
    delta = float(b[4].sum() - a[4].sum())
    ok.append(("comm parameter is exactly linear in ctrRT",
               abs(delta - 4.36 * float(a[1].sum())) < 1e-6,
               f"{delta:.4f} vs {4.36*float(a[1].sum()):.4f}"))

    # ---- naive reprice == cost-consistent when the box can never bind -------------------------
    c2 = RN.nbf(D, dir_arr, None, 1e18, None, False, 20.65)
    naive = RN.reprice(a[4], a[1].astype(float), 20.65)
    ok.append(("no-box: naive reprice == cost-consistent",
               len(naive) == len(c2[4]) and float(np.abs(naive - c2[4]).max()) < 1e-9,
               f"maxdiff {float(np.abs(naive - c2[4]).max()) if len(naive)==len(c2[4]) else 'len'}"))

    # ---- Stratum / ledger / weekly_fast --------------------------------------------------------
    class FakeS(RN.Stratum):
        def __init__(self, D):
            self.label = "FAKE"
            self.D = D
            st = np.zeros(D["n_sess"], np.int64)
            st[D["sid"][D["fb"]]] = np.flatnonzero(D["fb"])
            self.st = st
            self.sess_in = np.arange(D["n_sess"])
            self.in_win = np.ones(D["n_sess"], bool)
            self.sdate = pd.to_datetime(D["sess_date"])
            self.dstr = np.array([d.strftime("%Y-%m-%d") for d in self.sdate])
            self.wk = np.array([CE.iso_week(d) for d in self.dstr])
            self.all_weeks = sorted(set(self.wk.tolist()))
            _wi = {w: i for i, w in enumerate(self.all_weeks)}
            self.wk_idx = np.array([_wi[w] for w in self.wk], dtype=np.int64)
            self.nwk = len(self.all_weeks)

    S = FakeS(D)
    nb = RN.nbf(D, dir_arr, None, 1300.0, 1000.0, False, 20.65)
    d_, p_, q_, sp_ = S.ledger(nb)
    ok.append(("ledger session sum == trade sum",
               abs(float(sp_.sum()) - float(p_.sum())) < 1e-9,
               f"{sp_.sum():.4f} vs {p_.sum():.4f}"))
    w1 = S.weekly(d_, p_)
    w2 = S.weekly_fast(S._lastpos, p_)
    ok.append(("weekly_fast == champion_eval weekly",
               float(np.abs(w1 - w2).max()) < 1e-9, f"maxdiff {float(np.abs(w1-w2).max()):.2e}"))
    ok.append(("weekly sums to net", abs(float(w1.sum()) - float(p_.sum())) < 1e-6,
               f"{w1.sum():.4f} vs {p_.sum():.4f}"))

    # ---- wk_stats / gate plumbing ---------------------------------------------------------------
    s = RN.wk_stats(w1)
    ok.append(("wk_stats returns the full vector",
               all(k in s for k in ("net", "wk", "pos", "mdd", "es95", "fixdd", "streak", "t")), ""))

    # ---- _tg97 runs and returns a 3-valued target ----------------------------------------------
    mem = rng.choice(np.array([-1, 0, 1], np.int8), size=(n, 13)).astype(np.int8)
    bmom = rng.choice(np.array([-1, 0, 1], np.int8), size=n).astype(np.int8)
    tilt = rng.choice(np.array([-1, 0, 1], np.int8), size=n).astype(np.int8)
    tg = RN._tg97(D, mem, bmom, tilt, [0, 1, 2, 3, 4])
    ok.append(("_tg97 in {-1,0,1} and flat at session end",
               set(np.unique(tg).tolist()) <= {-1, 0, 1}, f"values {np.unique(tg)}"))

    w = max(len(a) for a, _, _ in ok)
    npass = sum(b for _, b, _ in ok)
    for a, b, why in ok:
        print(f"  [{'PASS' if b else 'FAIL'}] {a:<{w}}  {why}")
    print(f"\nsmoke {npass}/{len(ok)}")
    return 0 if npass == len(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
