"""WE_W45 PRODUCT CLOCK (spec preregistered): the full object on the clock the product uses.

W44: the shipped C# drives its decision stack from a 3-minute secondary series; our object runs
it on 1-minute bars and is 3.1x as active. W41: the 3-minute clock as a BASE sleeve is 9.40
pts/session at $170.8/trade against 1-min's 10.62 at $103.9, correlated only 0.48. Nobody has
put the QUALITY LAYER on the 3-minute clock, and frictions are charged per round turn.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, STRESS_RT, sm14_1m                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly                               # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w44b import clock3                                           # noqa: E402
from we_clocks import expand                                             # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W45_PRODUCTCLOCK", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260845)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS = nsess(A, B)
    out = open(os.path.join(OUT, "productclock.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def full_object(pos):
        """box -> causal quality score -> sized fills. The campaign's standard stack."""
        base = fills_daily(D, pos, halt=1300, target=1000)
        bl = [x for x in base if A <= np.datetime64(x["et"]) < B]
        if len(bl) < 200:
            return None, None
        ent = np.array([i_of(x["et"]) for x in bl])
        sc, _ = causal_score(X, ent, window=WIN)
        return fills_qexit(D, pos, np.where(sc >= 3, 2, 1).astype(np.int8), sc), base

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    C0, base0 = full_object(posL)
    pts0 = np.array([x["pnl"] for x in C0
                     if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS
    P_(f"=== B1: 1-min full object {pts0:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts0-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts0 - 14.72) >= 0.6:
        out.close(); return

    def vote3(vp, blocks=True):
        Dc, ec = clock3(D, anchor_0931=False)          # NT8's grid: session-anchored
        vs = []
        for mem in MEMBERS:
            tgc = sm14_1m(Dc, vp, return_targets=True, volmults=MEMBERS[mem],
                          blocks_on=blocks)
            tg = expand(tgc, ec, n)
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0)
                                                          | (X["ratio"] >= q))
                for dg in (True, False):
                    a = (okv & X["dL"]) if dg else okv
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        return (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)

    keys = sorted(weekly(C0, wk_of, A, B))
    v0 = np.array([weekly(C0, wk_of, A, B).get(k, 0.0) for k in keys])
    dd = np.argsort(v0)[:max(3, len(v0) // 10)]
    rows = []
    hdr = (f"{'arm':<32}{'n':>6}{'sz':>5}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'cvEff':>7}{'stress':>8}"
           f"{'corr':>7}{'corrDD':>8}")

    def rep(nm, trl, ref=None, a=A, b=B, ns=NS, kk=None):
        d = weekly(trl, wk_of, a, b)
        ks = kk if kk is not None else (keys if (a, b) == (A, B) else sorted(d))
        v = np.array([d.get(x, 0.0) for x in ks])
        if len(v) < 8:
            return None
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        u = np.array([x.get("u", 1) for x in trl if a <= np.datetime64(x["et"]) < b])
        if len(p) == 0:
            p, u = np.array([0.0]), np.array([1])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(p) / len(v))
        co = cd = float("nan")
        if len(v) == len(v0):
            co = float(np.corrcoef(v, v0)[0, 1]) if v.std() > 0 else 0.0
            cd = float(np.corrcoef(v[dd], v0[dd])[0, 1]) if v[dd].std() > 0 else 0.0
        r = dict(arm=nm, n=len(p), avg_size=round(float(u.mean()), 2),
                 pts=round(float(p.sum() / PV / ns), 2), per_trade=round(float(p.mean()), 1),
                 wk=round(float(v.mean())), worst=round(float(v.min())), cvar5=round(cv),
                 sharpe=round(s, 3), eff=round(eff, 3), cveff=round(cve, 3), stress=round(st),
                 corr=None if co != co else round(co, 3),
                 corr_dd=None if cd != cd else round(cd, 3))
        tag = ""
        if ref is not None:
            r["passes"] = bool(eff > ref["eff"] and cve > ref["cveff"] and st > 0)
            tag = "  PASS" if r["passes"] else "  reject"
        P_(f"{nm:<32}{r['n']:>6}{r['avg_size']:>5.2f}{r['pts']:>7.2f}{p.mean():>8.1f}"
           f"{r['wk']:>8,.0f}{100*(v>0).mean():>6.1f}{r['worst']:>9,.0f}{r['cvar5']:>9,.0f}"
           f"{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}{r['stress']:>8,.0f}"
           f"{(r['corr'] if r['corr'] is not None else 0):>7.2f}"
           f"{(r['corr_dd'] if r['corr_dd'] is not None else 0):>8.2f}{tag}")
        rows.append(r); return r

    P_(f"\n=== FULL OBJECT ON EACH CLOCK, full window [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    r0 = rep("C0 1-min (incumbent)", C0)
    built = {}
    for nm, vp, blk, cand in (("C1 3-min sigma=460 bars", 460, True, True),
                              ("C2 3-min sigma=153 bars", 153, True, True),
                              ("C3 3-min, no pre-close block", 460, False, False)):
        pos = vote3(vp, blk)
        obj, _ = full_object(pos)
        if obj is None:
            P_(f"{nm}: too few trades"); continue
        built[nm] = obj
        rep(nm + ("" if cand else "  [DIAGNOSTIC]"), obj, r0 if cand else None)
        print(f"   {nm} done [{_time.time()-t0:.0f}s]", flush=True)

    P_(f"\n=== PER YEAR (standing policy) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for nm, obj in [("C0 1-min", C0)] + [(k, v) for k, v in built.items()
                                         if "C3" not in k]:
        for y in (2022, 2023, 2024, 2025, 2026):
            a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
            if a >= b:
                continue
            rep(f"{nm} {y}", obj, None, a, b, nsess(a, b), sorted(weekly(obj, wk_of, a, b)))
        P_("")

    # ---- exposure-matched pair --------------------------------------------------------
    def expo(trl, k=1.0):
        return k * float(sum(x.get("u", 1)
                             * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                / np.timedelta64(1, "m"))
                             for x in trl if A <= np.datetime64(x["et"]) < B))

    def wv(trl, k=1.0):
        d = weekly(trl, wk_of, A, B)
        return np.array([d.get(x, 0.0) for x in keys]) * k

    def ntr(trl, k=1.0):
        return k * len([x for x in trl if A <= np.datetime64(x["et"]) < B])
    key3 = "C1 3-min sigma=460 bars"
    if key3 in built:
        e0, e3 = expo(C0), expo(built[key3])
        P_(f"=== C4 EXPOSURE-MATCHED PAIR (1-min {e0:,.0f} vs 3-min {e3:,.0f} contract-min) "
           f"[{_time.time()-t0:.0f}s] ===")
        P_(f"{'pair':<32}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
           f"{'eff':>8}{'cvEff':>8}{'stress':>9}")

        def show(nm, v, nt):
            nw = max(1, int(np.ceil(0.05 * len(v))))
            cv = float(np.sort(v)[:nw].mean())
            s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
            P_(f"{nm:<32}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
               f"{cv:>10,.0f}{s:>8.3f}{v.mean()/abs(v.min()):>8.3f}"
               f"{v.mean()/abs(cv):>8.3f}{v.mean()-STRESS_RT*nt/len(v):>9,.0f}")
            rows.append(dict(arm=nm, wk=round(float(v.mean())), worst=round(float(v.min())),
                             cvar5=round(cv), sharpe=round(s, 3),
                             eff=round(float(v.mean() / abs(v.min())), 3),
                             cveff=round(float(v.mean() / abs(cv)), 3)))
        show("w=0.00 1-min alone", wv(C0), ntr(C0))
        for w in (0.10, 0.20, 0.30, 0.50):
            kL, kB = 1 - w, w * e0 / e3
            show(f"w={w:.2f} 1-min + 3-min", wv(C0, kL) + wv(built[key3], kB),
                 ntr(C0, kL) + ntr(built[key3], kB))
        show("w=1.00 3-min alone (scaled)", wv(built[key3], e0 / e3),
             ntr(built[key3], e0 / e3))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
