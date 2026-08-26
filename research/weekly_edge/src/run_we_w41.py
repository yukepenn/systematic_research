"""WE_W41 CLOCK2 (spec preregistered): the multi-clock axis on the TRUE engine, and the
question W32 never asked - is an alternative-clock sleeve INDEPENDENT enough to be worth
owning at matched exposure?

W32 re-implemented the ratchet and dropped the tilt, hysteresis and combiner (1-min arm 4.85
vs the real object's 10.62), so its verdict is provisional. Here the shipped sm14_1m runs
UNCHANGED on aggregated bars; the throttle, delta gate, session box and ALL FILLS stay on the
1-min clock. Every arm reports its correlation with the long object and its correlation inside
the long object's WORST-DECILE weeks, and portfolio claims scan weight at CONSTANT TOTAL
EXPOSURE - the three measurements W32 and W40's first read each lacked.
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
from we_quality import build_context                                     # noqa: E402
from we_clocks import (clock_time, clock_volume, clock_range, expand,    # noqa: E402
                       size_for_rate)

OUT = os.path.join(ROOT, "runs", "WE_W41_CLOCK2", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260841)


def clock_vote(D, Dc, end_idx, X, sigma_bars):
    """The SAME 32-config long-only vote, with the ratchet advancing on the coarse clock."""
    n = D["n"]
    vs = []
    for mem in MEMBERS:
        tgc = sm14_1m(Dc, sigma_bars, return_targets=True, volmults=MEMBERS[mem])
        tg = expand(tgc, end_idx, n)
        for q in QS:
            okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
            for dg in (True, False):
                a = (okv & X["dL"]) if dg else okv
                vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
    return np.vstack(vs).mean(axis=0)


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
    NS = len(np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    out = open(os.path.join(OUT, "clock2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---- reference object -------------------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    LONG = fills_qexit(D, posL, np.where(scQ0 >= 3, 2, 1).astype(np.int8), scQ0)
    p = np.array([x["pnl"] for x in LONG if A <= np.datetime64(x["et"]) < B])
    P_(f"=== B1a quality object {p.sum()/PV/NS:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(p.sum()/PV/NS-14.72) < 0.6 else 'FAIL'}")
    pb = np.array([x["pnl"] for x in baseL if A <= np.datetime64(x["et"]) < B])
    P_(f"=== B1b base vote+box {pb.sum()/PV/NS:.2f} pts/session (expect 10.62) -> "
       f"{'PASS' if abs(pb.sum()/PV/NS-10.62) < 0.4 else 'FAIL'}")

    # ---- B1c: the clock harness itself, at k = 1 --------------------------------------
    D1, e1 = clock_time(D, 1)
    v1 = clock_vote(D, D1, e1, X, 460)
    pos1 = (v1 >= 0.5).astype(np.int8)
    ident = bool((pos1 == posL).all())
    P_(f"=== B1c CLOCK HARNESS at k=1 reproduces the incumbent vote bar-for-bar: "
       f"{'IDENTICAL - PASS' if ident else 'MISMATCH - RUN VOID'} "
       f"[{_time.time()-t0:.0f}s]")
    if not ident:
        P_("   (this is exactly the check W32 lacked)")
        out.close(); return
    P_("   (this is exactly the check W32 lacked; W32's axis is now testable)")

    keys = sorted(weekly(LONG, wk_of, A, B))
    vL = np.array([weekly(LONG, wk_of, A, B).get(k, 0.0) for k in keys])
    dd = np.argsort(vL)[:max(3, len(vL) // 10)]

    def wvec(trl, k=1.0):
        d = weekly(trl, wk_of, A, B)
        return np.array([d.get(x, 0.0) for x in keys]) * k

    def ntr(trl, k=1.0):
        return k * len([x for x in trl if A <= np.datetime64(x["et"]) < B])

    def expo(trl, k=1.0):
        return k * float(sum(x.get("u", 1)
                             * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                / np.timedelta64(1, "m"))
                             for x in trl if A <= np.datetime64(x["et"]) < B))
    rows = []
    hdr = (f"{'clock':<30}{'bars':>9}{'n':>6}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'shrp':>7}{'eff':>7}{'stress':>8}{'corr':>7}{'corrDD':>8}")

    def rep(nm, trl, nbars, pos=None):
        v = wvec(trl)
        pp = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        if len(pp) == 0:
            pp = np.array([0.0])
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(pp) / len(v))
        cor = float(np.corrcoef(v, vL)[0, 1]) if v.std() > 0 else 0.0
        cdd = float(np.corrcoef(v[dd], vL[dd])[0, 1]) if v[dd].std() > 0 else 0.0
        P_(f"{nm:<30}{nbars:>9,}{len(pp):>6}{pp.sum()/PV/NS:>7.2f}{pp.mean():>8.1f}"
           f"{v.mean():>8,.0f}{(v>0).mean()*100:>6.1f}{v.min():>9,.0f}{s:>7.3f}{eff:>7.3f}"
           f"{st:>8,.0f}{cor:>7.2f}{cdd:>8.2f}")
        r = dict(clock=nm, bars=nbars, n=len(pp), pts=round(float(pp.sum() / PV / NS), 2),
                 per_trade=round(float(pp.mean()), 1), wk=round(float(v.mean())),
                 wkpos=round(float((v > 0).mean() * 100), 1), worst=round(float(v.min())),
                 sharpe=round(s, 3), eff=round(eff, 3), stress=round(st),
                 corr=round(cor, 3), corr_dd=round(cdd, 3))
        rows.append(r); return r

    P_(f"\n=== CLOCKS on the TRUE engine (sigma at the wall-clock equivalent of 460 1-min "
       f"bars) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    rep("1-min base vote + box (ref)", baseL, D["n"], posL)

    V3, R3 = size_for_rate(D, 460)
    V5, _ = size_for_rate(D, 276)
    clocks = [("3-min time", lambda: clock_time(D, 3), max(20, 460 // 3)),
              ("5-min time", lambda: clock_time(D, 5), max(20, 460 // 5)),
              ("volume (=3-min rate)", lambda: clock_volume(D, V3), max(20, 460 // 3)),
              ("range (=3-min rate)", lambda: clock_range(D, R3), max(20, 460 // 3))]
    built = {}
    for nm, fn, sb in clocks:
        Dc, ec = fn()
        vv = clock_vote(D, Dc, ec, X, sb)
        pos = (vv >= 0.5).astype(np.int8)
        trl = fills_daily(D, pos, halt=1300, target=1000)
        built[nm] = (pos, trl)
        rep(nm, trl, Dc["n"], pos)
        print(f"   {nm} done [{_time.time()-t0:.0f}s]", flush=True)
    # 3-min at the SAME BAR COUNT sigma, as the declared sensitivity
    Dc, ec = clock_time(D, 3)
    vv = clock_vote(D, Dc, ec, X, 460)
    pos = (vv >= 0.5).astype(np.int8)
    trl = fills_daily(D, pos, halt=1300, target=1000)
    built["3-min sigma=460 bars"] = (pos, trl)
    rep("3-min, sigma=460 BARS", trl, Dc["n"], pos)

    # ---- weight scan at constant total exposure, versus the QUALITY object -------------
    P_(f"\n=== WEIGHT SCAN at constant total exposure vs the long quality object "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(f"{'pair':<40}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
       f"{'eff':>8}{'cvEff':>8}{'stress':>9}")
    eL = expo(LONG)

    def show(nm, v, nt):
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * nt / len(v))
        P_(f"{nm:<40}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
           f"{cv:>10,.0f}{s:>8.3f}{eff:>8.3f}{cve:>8.3f}{st:>9,.0f}")
        rows.append(dict(clock=nm, wk=round(float(v.mean())), worst=round(float(v.min())),
                         cvar5=round(cv), sharpe=round(s, 3), eff=round(eff, 3),
                         cveff=round(cve, 3), stress=round(st)))
        return eff, cve
    ref_eff, ref_cve = show("w=0.00 long quality alone", wvec(LONG), ntr(LONG))
    winners = []
    for nm, (pos, trl) in built.items():
        eB = expo(trl)
        if eB <= 0:
            continue
        best = None
        for w in (0.05, 0.10, 0.20, 0.30):
            kL, kB = 1 - w, w * eL / eB
            e, c = show(f"w={w:.2f}  long + {nm}", wvec(LONG, kL) + wvec(trl, kB),
                        ntr(LONG, kL) + ntr(trl, kB))
            if e > ref_eff or c > ref_cve:
                best = (w, e, c) if best is None or e > best[1] else best
        if best:
            winners.append((nm, best))
    P_(f"\n   clocks improving eff or CVaR-eff at some weight: "
       f"{[(w[0], w[1][0]) for w in winners] if winners else 'NONE -> W32 verdict CONFIRMED '
          'on the true engine'}")

    # ---- nulls on any winner ----------------------------------------------------------
    for nm, (w, _, _) in winners:
        pos, trl = built[nm]
        P_(f"\n=== NULLS on {nm} [{_time.time()-t0:.0f}s] ===")
        base = wvec(trl)
        real = float(base.mean() / abs(base.min())) if base.min() < 0 else 9.9
        ent_b = np.where((pos != 0) & (np.concatenate([[0], pos[:-1]]) == 0))[0]
        for tag in ("N1 circular shift", "N2 count-matched random"):
            nl = []
            for j in range(100):
                if tag.startswith("N1"):
                    pn = np.roll(pos, int(RNG.integers(20_000, n - 20_000)))
                else:
                    pn = np.zeros(n, np.int8)
                    pick = RNG.choice(n - 40, size=len(ent_b), replace=False)
                    for k_ in pick:
                        pn[k_:k_ + 30] = 1
                v = wvec(fills_daily(D, pn, halt=1300, target=1000))
                nl.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            nu = np.array(nl)
            pct = 100.0 * (nu < real).mean()
            P_(f"   {tag:<26} real {real:.3f} | null mean {nu.mean():.3f} | "
               f"pctile {pct:.1f} | p {(nu>=real).mean():.3f} -> "
               f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
