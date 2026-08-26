"""WE_W66 phase 5 (amendment_1) - REMOVE THE TICK CLAMP.

S = clamp(VolMult x sigma, 40 ticks, 1200 ticks). VolMult x sigma is volatility-scaled; 40 and
1200 ticks are fixed. That is dimensionally inconsistent, and phase 0 measured what it does: the
floor binds on 31.0 % of 2023's bars for VolMult 6 (55.8 % for VolMult 4) and the cap binds on
20.0 % of 2026's bars for VolMult 40. The ensemble's effective width has been changing over time
and it is narrowest in the object's worst year.

The algebra, noted in the amendment before running: clamping S to [c1 x sigma, c2 x sigma] is
identical to clamping VolMult to [c1, c2], which the ladder already does. A sigma-relative clamp
is a NO-OP, so the honest form of the fix is simply to remove the tick clamp.

Four arms, all pure aggregations with the incumbent nested inside, no parameter selected.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, sm14_1m                                 # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import rebuild_targets, WIDE                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
DD_TARGET = 20245.0
BASE = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
L2 = BASE + [32, 34, 36, 38, 40]
L5 = list(range(4, 41))
NOCLAMP = dict(smin_pts=1e-9, smax_pts=1e9)     # the tick clamp removed; STOPM warm-up kept
NDRAW = 300
RNG = np.random.default_rng(20260866)


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "clampfix.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    idx_of = {v: k for k, v in enumerate(WIDE)}

    def members(noclamp):
        tag = "noclamp" if noclamp else "clamp"
        f = os.path.join(OUT, f"mem460_{tag}_{D['n']}.npz")
        if os.path.exists(f):
            z = np.load(f)
            return z["mem"], z["bmom"], z["tilt"]
        P_(f"   building member matrix ({tag}) [{_time.time()-t0:.0f}s]")
        kw = NOCLAMP if noclamp else {}
        _, mem, bm, tl = sm14_1m(D, 460, return_members=True, volmults=WIDE, **kw)
        np.savez_compressed(f, mem=mem, bmom=bm, tilt=tl)
        P_(f"      done [{_time.time()-t0:.0f}s]")
        return mem, bm, tl

    def prefixes(ladder):
        o = {}
        for cut in (14, 16, 18, 10 ** 9):
            sel = [v for v in ladder if v <= cut]
            if len(sel) >= 3:
                o[cut] = sel
        return o

    def build(mem, bm, tl, ladder):
        vs = []
        for cut, vms in prefixes(ladder).items():
            tg = rebuild_targets(mem, bm, tl, [idx_of[v] for v in vms], D)
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 200:
            return None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], len(trl)

    def met(sp, ntr, name, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        cnt = np.bincount(wi, minlength=NW) > 0
        v = np.bincount(wi, weights=s, minlength=NW)[cnt]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s != 0
        import itertools
        st_ = max((len(list(g)) for kk, g in itertools.groupby(v < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(s.sum() / PV / max(len(s), 1)),
                    daypos=100 * float((s > 0).mean()),
                    trdpos=100 * float((s[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(st_),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)
    HDR = (f"{'arm':<34}{'mem':>5}{'trds':>7}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}")

    def show(r, nm_, tag=""):
        P_(f"{r['arm']:<34}{nm_:>5}{r['ntr']:>7}{r['pts']:>7.2f}{r['daypos']:>7.1f}"
           f"{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{r['worst']:>9,.0f}{tag}")

    mem_c, bm_c, tl_c = members(False)
    mem_n, bm_n, tl_n = members(True)
    P_(f"\n{'='*133}\n=== PHASE 5: the tick clamp REMOVED. All arms are pure aggregations "
       f"with the incumbent nested.")
    P_(f"{'='*133}")
    P_(HDR)
    ledger, rows = {}, []
    ARMS = [("C0 incumbent, clamp ON", mem_c, bm_c, tl_c, BASE),
            ("C1 incumbent, clamp OFF", mem_n, bm_n, tl_n, BASE),
            ("C2 ladder 6-40, clamp OFF", mem_n, bm_n, tl_n, L2),
            ("C3 ladder 4-40 step1, clamp OFF", mem_n, bm_n, tl_n, L5),
            ("C2r ladder 6-40, clamp ON", mem_c, bm_c, tl_c, L2)]
    for nm_, m_, b_, t_, lad in ARMS:
        r = build(m_, b_, t_, lad)
        if r is None:
            continue
        sp, ntr = r
        mt = met(sp, ntr, nm_)
        show(mt, len(lad), "   <- B1 reference" if nm_.startswith("C0") else "")
        rows.append(mt); ledger[nm_] = sp
    inc = ledger.get("C0 incumbent, clamp ON")
    if inc is None:
        P_("   B1 arm missing, VOID"); out.close(); return
    b1 = rows[0]["pts"]
    P_(f"\n   B1 GATE: {b1:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(b1 - 14.72) < 0.6 else 'FAIL - VOID'}")
    if abs(b1 - 14.72) >= 0.6:
        out.close(); return
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "clamp_arms.csv"), index=False)

    P_(f"\n=== per year (pts/session) ===")
    yrs = sorted(set(sdate.year))
    P_(f"{'arm':<34}" + "".join(f"{y:>10}" for y in yrs))
    for nm_, sp in ledger.items():
        P_(f"{nm_:<34}" + "".join(
            f"{sp[sdate.year == y].sum()/PV/max((sdate.year == y).sum(),1):>10.2f}" for y in yrs))

    P_(f"\n{'='*133}\n=== SUB-PERIOD STABILITY vs the incumbent (the bar is a MAJORITY)")
    P_(f"{'='*133}")
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    P_(f"{'arm':<34}{'windows':>9}{'trdD+% wins':>14}{'weekly$ wins':>15}{'top5DD wins':>14}"
       f"{'ALL THREE':>12}{'verdict':>10}")
    subs = []
    for nm_, sp in ledger.items():
        if nm_.startswith("C0"):
            continue
        c1 = c2 = c3 = c4 = tot = 0
        for eend in ends:
            b0 = eend - pd.DateOffset(months=24)
            mk = (sdate > b0) & (sdate <= eend)
            a_, bb = met(sp, 0, "", mk), met(inc, 0, "", mk)
            if a_ is None or bb is None:
                continue
            tot += 1
            x1 = a_["trdpos"] > bb["trdpos"]; x2 = a_["weekly"] > bb["weekly"]
            x3 = a_["dd_top5"] < bb["dd_top5"]
            c1 += x1; c2 += x2; c3 += x3; c4 += (x1 and x2 and x3)
        all3 = 100 * c4 / max(tot, 1)
        P_(f"{nm_:<34}{tot:>9}{100*c1/max(tot,1):>13.0f}%{100*c2/max(tot,1):>14.0f}%"
           f"{100*c3/max(tot,1):>13.0f}%{all3:>11.0f}%"
           f"{('PASS' if all3 > 50 else 'fail'):>10}")
        subs.append(dict(arm=nm_, n=tot, trd=100*c1/max(tot,1), wk=100*c2/max(tot,1),
                         dd=100*c3/max(tot,1), all3=all3))
    pd.DataFrame(subs).to_csv(os.path.join(OUT, "clamp_subperiod.csv"), index=False)

    P_(f"\n{'='*133}\n=== NULL: does the SPECIFIC ladder beat a RANDOM ensemble of the same size?")
    P_(f"{'='*133}")
    P_("These arms perform no selection, so the right null is a random-member aggregate of equal")
    P_("size drawn from the same 4-40 pool (W59 amendment_1: an aggregate must not be dressed in")
    P_("a scan-matched null it cannot fail).\n")
    tgt_arm = "C2 ladder 6-40, clamp OFF"
    if tgt_arm in ledger:
        real = met(ledger[tgt_arm], 0, "")
        nulls = []
        for _ in range(60):
            pick = sorted(RNG.choice(WIDE, len(L2), replace=False).tolist())
            r = build(mem_n, bm_n, tl_n, pick)
            if r is None:
                continue
            nulls.append(met(r[0], r[1], ""))
        Nd = pd.DataFrame(nulls)
        Nd.to_csv(os.path.join(OUT, "clamp_nulls.csv"), index=False)
        P_(f"{'metric':<16}{'real':>12}{'null mean':>12}{'null p95':>12}{'percentile':>12}"
           f"{'verdict':>10}")
        for key, hi in (("pts", True), ("weekly", True), ("trdpos", True), ("wkpos", True),
                        ("dd_top5", False), ("ulcer", False)):
            a = Nd[key].values.astype(float)
            v = float(real[key])
            p = 100 * float((a < v).mean() if hi else (a > v).mean())
            P_(f"{key:<16}{v:>12,.2f}{a.mean():>12,.2f}"
               f"{np.percentile(a, 95 if hi else 5):>12,.2f}{p:>11.1f}%"
               f"{('PASS' if p >= 95 else 'fail'):>10}")
    P_(f"\n=== STATUS: nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
