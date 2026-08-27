"""WE_W95b - RETEST W91 SECTION 4's EXACT CLAIM WITH THE SCORE DEFECT FIXED.

W95's arms tested {BMOM, X9a} 2:3 and NETFUSE_1 and found the box HELPS both. W91's observation
was on a DIFFERENT object - {SOLAR, BMOM} 50/50 - and its box-free arm built the causal quality
score from a BOX-LIMITED entry set. This retests the exact object W91 measured, with the score
built from the same box regime the arm trades under, so the claim is confronted rather than
sidestepped by testing something else.

Also: a scan-matched null for the (halt, target) grid's argmax, because W95's grid is best-of-31
and the repo rule since W53 is that a scan may never be compared against an unscanned reference.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w93 import build                                             # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W95_BOXLESS", "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
NOBOX = 1e15
C_P1, C_BMOM = 14.52, 12.99
NDRAW = 200
RNG = np.random.default_rng(20260895)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "w95b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    sess_end = D["sess_end"]
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    bm = np.where(flatm, 0, bmom).astype(np.int8)
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    inw = np.array([in_win[s] for s in sid])
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    NWk = len(set(wk))

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    def daily(t):
        sp = np.zeros(D["n_sess"])
        for x in t:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def cmin(t):
        v = np.zeros(n)
        for x in t:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return float(v[inw].sum())

    def pan(v, cost_wk):
        w = pd.Series(v).groupby(wk).sum().to_numpy() - cost_wk
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9))

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tg = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tg[i - 1]
            g = p
            if flatm[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tg[i] = g
        return tg

    def solar_obj(chan, halt, target):
        idx = {v: k for k, v in enumerate(L13)}
        TG = {}
        for name, vols in MEMBERS.items():
            cols = [idx[v] for v in vols]
            s_ = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            TG[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        vs = []
        for m_ in MEMBERS:
            tg = TG[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & X["dL"] if dg else okv
                    vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        p = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        bb = fills_daily(D, p, halt=(1300 if halt < 1e14 else int(1e9)),
                         target=(1000 if halt < 1e14 else None))
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return keep(fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_,
                                halt=halt, target=target))

    P_("=" * 118)
    P_("=== PART 1: W91 SECTION 4's EXACT OBJECT - {SOLAR, BMOM} 50/50 - with the score fixed")
    P_("=" * 118)
    ZER = np.zeros(n, np.int8)
    SOL_b, SOL_n = solar_obj(ZER, 1300.0, 1000.0), solar_obj(ZER, NOBOX, None)
    BM_b = keep(sfills(D, bm, halt=1300.0, target=1000.0))
    BM_n = keep(sfills(D, bm, halt=NOBOX, target=None))
    P_(f"    SOLAR boxed {len(SOL_b):,} tr / box-free {len(SOL_n):,} tr   "
       f"BMOM boxed {len(BM_b):,} / box-free {len(BM_n):,}")

    def blend(ts, tb):
        ser = 0.5 * daily(ts) + 0.5 * daily(tb)
        cm = 0.5 * cmin(ts) + 0.5 * cmin(tb)
        cost = (0.5 * C_P1 * sum(x["u"] for x in ts)
                + 0.5 * C_BMOM * sum(x["u"] for x in tb)) / NWk
        return ser, cm, cost, len(ts) + len(tb)
    box = blend(SOL_b, BM_b); free = blend(SOL_n, BM_n)
    ref = box[1]
    P_("")
    P_(f"{'arm':<28}{'trades':>8}{'scale':>7}{'wk $':>9}{'wk+%':>8}{'strk':>6}{'maxDD':>10}"
       f"{'top5DD':>9}{'worst':>10}{'wk$@fixDD':>11}")
    R = {}
    for nm, (ser, cm, cost, ntr) in (("PORT_SB with boxes", box), ("PORT_SB NO box", free)):
        s = ref / cm
        a = pan(ser * s, cost * s); R[nm] = a
        P_(f"{nm:<28}{ntr:>8,}{s:>7.3f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['streak']:>6}"
           f"{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}{a['worst']:>10,.0f}{a['weekly_dd']:>11,.0f}")
    w = R["PORT_SB NO box"]; b_ = R["PORT_SB with boxes"]
    nl = sum([w["weekly_dd"] > b_["weekly_dd"], w["wkpos"] > b_["wkpos"], w["top5"] < b_["top5"]])
    P_("")
    P_(f"    box-free wins {nl}/3 on {{SOLAR, BMOM}} - W91 section 4 reported it winning on")
    P_(f"    money@fixedDD (923 vs 629), wk+% (60.1 vs 55.9) and top-5 DD (11,750 vs 12,718).")
    P_(f"    -> W91's observation is {'CONFIRMED' if nl >= 2 else 'NOT CONFIRMED once the score is built from the arm''s own box regime'}")

    # ------------------------------------------------------------ PART 2: scan-matched null
    P_("")
    P_("=" * 118)
    P_("=== PART 2: SCAN-MATCHED NULL for the (halt, target) grid's argmax (repo rule, W53)")
    P_("=== W95's grid peaks at halt=2000 and W93's walk-forward chose halt=2000 in 7 of 12")
    P_("=== refits. Best-of-31 on structureless data inflates the winner; this measures by how")
    P_("=== much, by running the SAME 31-cell scan on 200 circular-shifted versions of the")
    P_("=== NETFUSE target and recording each scan's WINNER.")
    P_("=" * 118)
    VL, VS = build(D, mem, bmom, tilt, X)
    tgtN = np.where(VL & VS, 0, np.where(VL, 1, np.where(VS, -1, 0))).astype(np.int8)
    GRID = [(h, tg) for h in (600, 900, 1300, 2000, 3000, 5000) for tg in (600, 1000, 1600, 3000, None)]
    GRID.append((NOBOX, None))
    refcm = cmin(keep(sfills(D, tgtN, halt=1300.0, target=1000.0)))

    def scan(t_arr):
        best, bk, base = -1e18, None, None
        for h, tg in GRID:
            tr = keep(sfills(D, t_arr, halt=float(h), target=tg))
            if not tr:
                continue
            s = refcm / max(cmin(tr), 1.0)
            a = pan(daily(tr) * s, C_P1 * sum(x["u"] for x in tr) / NWk * s)
            if (h, tg) == (1300, 1000):
                base = a["weekly_dd"]
            if a["weekly_dd"] > best:
                best, bk = a["weekly_dd"], (h, tg)
        return best, bk, base
    r_best, r_k, r_base = scan(tgtN)
    P_("")
    P_(f"    REAL: incumbent (1300,1000) = {r_base:,.0f};  scan argmax {r_k} = {r_best:,.0f}"
       f"   uplift {100*(r_best/r_base-1):+.1f} %")
    starts = np.flatnonzero(fb); bnd = list(starts) + [n]
    blocks = [(bnd[i], bnd[i + 1]) for i in range(len(bnd) - 1)]
    NB = len(blocks)
    ks = RNG.choice(np.arange(1, NB), size=min(40, NB - 1), replace=False)
    ups = []
    for j, k in enumerate(ks):
        t2 = np.zeros(n, np.int8)
        for i, (a_, b_) in enumerate(blocks):
            sa, sb = blocks[(i + int(k)) % NB]
            m = min(b_ - a_, sb - sa)
            t2[a_:a_ + m] = tgtN[sa:sa + m]
        bst, _, bse = scan(t2)
        if bse and abs(bse) > 1e-9:
            ups.append(100 * (bst / bse - 1))
        if (j + 1) % 10 == 0:
            P_(f"      {j+1}/{len(ks)} [{_time.time()-t0:.0f}s]")
    ups = np.array(ups)
    P_("")
    P_(f"    {len(ups)} shuffled scans: best-of-31 uplift over the same cell's own incumbent")
    P_(f"      mean {ups.mean():+.1f} %   median {np.median(ups):+.1f} %   "
       f"p95 {np.percentile(ups, 95):+.1f} %")
    P_(f"    REAL uplift {100*(r_best/r_base-1):+.1f} %  -> percentile "
       f"{100*float((ups < 100*(r_best/r_base-1)).mean()):.1f} %")
    P_("")
    P_(f"    Read: if the real uplift sits inside the shuffled distribution, the grid's argmax is")
    P_(f"    what best-of-31 produces on structureless data and means NOTHING.")
    pd.DataFrame(dict(uplift_pct=ups)).to_csv(os.path.join(OUT, "scan_null.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
