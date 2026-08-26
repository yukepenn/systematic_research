"""WE_W46 RESTORE ON THE PRODUCT'S CLOCK (spec preregistered).

W31 killed restore on the ONE-MINUTE clock: exposure 12.9 % -> 20.7 % of bars while edge
density collapsed 0.0603 -> 0.0025 points per bar-in-position and production fell 10.62 -> 0.70.
W44 then established that the product runs on a THREE-MINUTE clock and our 1-minute object is
2.1x as active, and W45 established that mechanisms do NOT transfer between the two clocks.

Primary metric here is POINTS PER BAR-IN-POSITION, reported beside exposure, because that is
the number that killed W31 and it makes an exposure-driven "gain" visible immediately.
A 1-minute restore CONTROL must reproduce W31's collapse or the run is VOID.
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

OUT = os.path.join(ROOT, "runs", "WE_W46_RESTORE3M", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260846)


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
    out = open(os.path.join(OUT, "restore3m.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---------------- B1 gate: the 1-min full object -----------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    LONG = fills_qexit(D, posL, np.where(scQ0 >= 3, 2, 1).astype(np.int8), scQ0)
    pts = np.array([x["pnl"] for x in LONG
                    if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS
    P_(f"=== B1 GATE: 1-min full object {pts:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    keys = sorted(weekly(LONG, wk_of, A, B))
    v0 = np.array([weekly(LONG, wk_of, A, B).get(k, 0.0) for k in keys])
    dd = np.argsort(v0)[:max(3, len(v0) // 10)]
    rows = []
    hdr = (f"{'arm':<32}{'n':>6}{'pts':>7}{'$/tr':>8}{'inMkt%':>8}{'pts/bar':>9}{'wk$':>8}"
           f"{'wk+%':>6}{'worst':>9}{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'cvEff':>7}"
           f"{'stress':>8}{'corr':>7}{'corrDD':>8}")

    def rep(nm, pos, trl, ref=None, a=A, b=B, ns=NS, kk=None, quiet=False):
        d = weekly(trl, wk_of, a, b)
        ks = kk if kk is not None else (keys if (a, b) == (A, B) else sorted(d))
        v = np.array([d.get(x, 0.0) for x in ks])
        if len(v) < 8:
            return None
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        if len(p) == 0:
            p = np.array([0.0])
        mw = (tarr >= a) & (tarr < b)
        inm = float((pos[mw] != 0).mean())
        bars_in = max(1.0, (pos[mw] != 0).sum())
        dens = float(p.sum() / PV / bars_in)          # points per bar-in-position
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(p) / len(v))
        co = cd = 0.0
        if len(v) == len(v0):
            co = float(np.corrcoef(v, v0)[0, 1]) if v.std() > 0 else 0.0
            cd = float(np.corrcoef(v[dd], v0[dd])[0, 1]) if v[dd].std() > 0 else 0.0
        r = dict(arm=nm, n=len(p), pts=round(float(p.sum() / PV / ns), 2),
                 per_trade=round(float(p.mean()), 1), in_mkt=round(100 * inm, 1),
                 density=round(dens, 4), wk=round(float(v.mean())),
                 worst=round(float(v.min())), cvar5=round(cv), sharpe=round(s, 3),
                 eff=round(eff, 3), cveff=round(cve, 3), stress=round(st),
                 corr=round(co, 3), corr_dd=round(cd, 3))
        tag = ""
        if ref is not None:
            r["passes"] = bool(eff > ref["eff"] and cve > ref["cveff"]
                               and dens >= 0.85 * ref["density"] and st > 0)
            tag = "  PASS" if r["passes"] else "  reject"
        if not quiet:
            P_(f"{nm:<32}{r['n']:>6}{r['pts']:>7.2f}{p.mean():>8.1f}{100*inm:>8.1f}"
               f"{dens:>9.4f}{r['wk']:>8,.0f}{100*(v>0).mean():>6.1f}{r['worst']:>9,.0f}"
               f"{r['cvar5']:>9,.0f}{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}"
               f"{r['stress']:>8,.0f}{r['corr']:>7.2f}{r['corr_dd']:>8.2f}{tag}")
        rows.append(r); return r

    def vote_arm(clock, restore=None, type3=False):
        vs = []
        if clock == 1:
            for mem in MEMBERS:
                tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem],
                             restore=restore, type3=type3)
                for q in QS:
                    okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0)
                                                              | (X["ratio"] >= q))
                    for dg in (True, False):
                        a_ = (okv & X["dL"]) if dg else okv
                        vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        else:
            Dc, ec = clock3(D, anchor_0931=False)
            for mem in MEMBERS:
                tgc = sm14_1m(Dc, 460, return_targets=True, volmults=MEMBERS[mem],
                              restore=restore, type3=type3)
                tg = expand(tgc, ec, n)
                for q in QS:
                    okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0)
                                                              | (X["ratio"] >= q))
                    for dg in (True, False):
                        a_ = (okv & X["dL"]) if dg else okv
                        vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        return (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)

    P_(f"\n=== CONTROL: does the restore machinery still reproduce W31's collapse on 1-min? "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    rep("1-min BASE (W41: 10.62)", posL, baseL)
    p1r = vote_arm(1, restore="plain")
    r1r = rep("1-min BASE + restore (W31)", p1r, fills_daily(D, p1r, halt=1300, target=1000))
    ok_ctl = r1r is not None and r1r["pts"] < 6.0
    P_(f"   CONTROL VERDICT: 1-min restore gives {r1r['pts']:.2f} pts/session against the base's"
       f" 10.62 -> {'PASS (W31 reproduced)' if ok_ctl else 'FAIL - restore machinery broken, RUN VOID'}")
    if not ok_ctl:
        out.close(); return

    P_(f"\n=== 3-MINUTE CLOCK (the product's own), no quality layer [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    built = {}
    p30 = vote_arm(3)
    r0 = rep("R0 3-min base (W41: 9.40)", p30, fills_daily(D, p30, halt=1300, target=1000))
    built["R0 3-min base"] = (p30, fills_daily(D, p30, halt=1300, target=1000))
    for nm, kw in (("R1 3-min + restore plain", dict(restore="plain")),
                   ("R2 3-min + restore conf", dict(restore="conf")),
                   ("R3 3-min + type3", dict(type3=True)),
                   ("R4 3-min + restore + type3", dict(restore="plain", type3=True))):
        pos = vote_arm(3, **kw)
        trl = fills_daily(D, pos, halt=1300, target=1000)
        built[nm] = (pos, trl)
        rep(nm, pos, trl, r0)
        print(f"   {nm} done [{_time.time()-t0:.0f}s]", flush=True)

    P_(f"\n=== PER YEAR (standing policy) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for nm, (pos, trl) in built.items():
        for y in (2022, 2023, 2024, 2025, 2026):
            a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
            if a >= b:
                continue
            rep(f"{nm} {y}", pos, trl, None, a, b, nsess(a, b),
                sorted(weekly(trl, wk_of, a, b)))
        P_("")

    # ---------------- substitution into the adopted W41 basket -------------------------
    P_(f"\n=== SUBSTITUTION INTO THE ADOPTED W41 BASKET (w = 0.03 each) "
       f"[{_time.time()-t0:.0f}s] ===")
    rngp = os.path.join(ROOT, "runs", "WE_W41_CLOCK2", "out", "pos_range.npy")
    if not os.path.exists(rngp):
        P_("   range sleeve cache missing - run run_we_w41b.py first; substitution skipped")
    else:
        rangetrl = fills_daily(D, np.load(rngp), halt=1300, target=1000)

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
        eL, eR = expo(LONG), expo(rangetrl)
        P_(f"{'basket':<40}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
           f"{'eff':>8}{'cvEff':>8}{'stress':>9}")

        def show(nm, v, nt):
            nw = max(1, int(np.ceil(0.05 * len(v))))
            cv = float(np.sort(v)[:nw].mean())
            s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
            P_(f"{nm:<40}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
               f"{cv:>10,.0f}{s:>8.3f}{v.mean()/abs(v.min()):>8.3f}"
               f"{v.mean()/abs(cv):>8.3f}{v.mean()-STRESS_RT*nt/len(v):>9,.0f}")
            rows.append(dict(arm=nm, wk=round(float(v.mean())), worst=round(float(v.min())),
                             cvar5=round(cv), sharpe=round(s, 3),
                             eff=round(float(v.mean() / abs(v.min())), 3),
                             cveff=round(float(v.mean() / abs(cv)), 3)))
        w = 0.03
        kL = 1 - 2 * w
        kR = w * eL / eR
        show("w=0 long alone", wv(LONG), ntr(LONG))
        for nm, (pos, trl) in built.items():
            k3 = w * eL / max(expo(trl), 1e-9)
            show(f"long + range + {nm}",
                 wv(LONG, kL) + wv(rangetrl, kR) + wv(trl, k3),
                 ntr(LONG, kL) + ntr(rangetrl, kR) + ntr(trl, k3))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
