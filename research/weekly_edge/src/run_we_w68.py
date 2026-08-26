"""WE_W68 - what the object looks like when it leans on the fragile half less.

W67 established that P1 is a Solar ensemble OR-gated with B-MOM, that B-MOM supplies 51 % of the
net, and that B-MOM is a component this repo has independently judged regime-local twice. That
makes the object's largest single risk a disclosure rather than an optimisation.

Two independently-motivated moves reduce that dependence: W66's wider ladder (strengthens Solar)
and a lower B-MOM weight (leans on it less). Neither passed its own bar. Combining two failed
arms is how a fit is manufactured, and the spec says so before running - the cross is tested
because both reduce the SAME disclosed fragility for reasons stated in advance.

NEW ADOPTION CLAUSE, and it is the point of the wave: an arm that improves the numbers while
INCREASING the B-MOM-enabled share of net is not an improvement.
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
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w19 import QS                                                # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import WIDE                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W68_ROBUSTCORE", "out")
os.makedirs(OUT, exist_ok=True)
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
L18 = L13 + [32, 34, 36, 38, 40]
CUTS = (14, 16, 18, 10 ** 9)
DD_TARGET = 20245.0
RNG = np.random.default_rng(20260868)


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "robust.txt"), "w", encoding="utf-8")

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
    yrs = sorted(set(sdate.year))

    z = np.load(os.path.join(W66OUT, f"mem460_clamp_{D['n']}.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    idx_of = {v: k for k, v in enumerate(WIDE)}
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flat = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flat[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tgt[i] = g
        return tgt

    def target(cols, w_bmom, tiltmul=1.25, tilt_arr=None):
        tl = tilt if tilt_arr is None else tilt_arr
        s = mem[:, cols].sum(axis=1).astype(np.int32)
        nm = len(cols)
        T = np.clip(ra(s / float(nm) * 10.0), -10, 10)
        ag = (np.sign(s) == tl) & (s != 0) & (tl != 0)
        Tp = np.clip(ra(T * np.where(ag, tiltmul, 1.0) * 0.9026), -13, 13)
        return hyst(0.7086 * Tp + w_bmom * bmom.astype(float))

    def target_k(cols, k, w_bmom):
        """the Solar side expressed DIRECTLY as 'at least k of NMEM members net-long',
        which W67 proved is what the combiner chain reduces to."""
        s = mem[:, cols].sum(axis=1).astype(np.int32)
        base = np.where(s >= k, 3.0, np.where(s <= -k, -3.0, 0.0))
        hold = np.where(np.abs(s) >= max(1, k // 3), 2.0, 0.0) * np.sign(s)
        M = np.where(base != 0, base, hold) + w_bmom * bmom.astype(float)
        return hyst(M)

    def object_from(tgs, tag):
        vs = []
        for tg in tgs:
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 150:
            return None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], trl

    def bmom_share(trl, ladder):
        cols = [idx_of[v] for v in ladder]
        s = mem[:, cols].sum(axis=1).astype(int)
        ag = (np.sign(s) == tilt) & (s != 0) & (tilt != 0)
        need = np.where(ag, int(round(0.385 * len(ladder))), int(round(0.462 * len(ladder))))
        tot = sum(x["pnl"] for x in trl)
        en = sum(x["pnl"] for x in trl
                 if s[i_of(x["et"])] < need[i_of(x["et"])] and bmom[i_of(x["et"])] > 0)
        return 100.0 * en / tot if tot else np.nan

    def met(sp, ntr, name, mask=None):
        s_ = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s_) < 40:
            return None
        cnt = np.bincount(wi, minlength=NW) > 0
        v = np.bincount(wi, weights=s_, minlength=NW)[cnt]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s_ != 0
        stk = max((len(list(g)) for kk, g in itertools.groupby(v < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(s_.sum() / PV / max(len(s_), 1)),
                    daypos=100 * float((s_ > 0).mean()),
                    trdpos=100 * float((s_[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)
    HDR = (f"{'arm':<32}{'trds':>7}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}{'BMOM%':>8}")

    def show(r, bs, tag=""):
        P_(f"{r['arm']:<32}{r['ntr']:>7}{r['pts']:>7.2f}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}"
           f"{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}{r['weekly']:>10,.0f}"
           f"{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{r['worst']:>9,.0f}"
           f"{(f'{bs:.1f}' if bs == bs else '-'):>8}{tag}")

    # =====================================================================================
    # PHASE 1 - THE CROSS
    # =====================================================================================
    P_(f"\n{'='*136}\n=== PHASE 1: ladder x B-MOM weight. The incumbent and Solar-only are "
       f"CORNERS of this grid, not baselines outside it.")
    P_(f"{'='*136}")
    P_("BMOM% is the share of net from entries the member consensus alone would NOT have made.")
    P_("An arm that improves the numbers while RAISING it is not an improvement (spec, phase 4).\n")
    P_(HDR)
    rows, led = [], {}
    for lname, lad in (("13", L13), ("18", L18)):
        for w in (2.83, 2.00, 0.00):
            tgs = [target([idx_of[v] for v in lad if v <= c], w) for c in CUTS
                   if len([v for v in lad if v <= c]) >= 3]
            r = object_from(tgs, "")
            if r is None:
                continue
            sp, trl = r
            nm_ = f"ladder{lname} w_bmom={w:.2f}"
            m_ = met(sp, len(trl), nm_)
            bs = bmom_share(trl, lad) if w > 0 else 0.0
            show(m_, bs, "   <- INCUMBENT" if (lname == "13" and w == 2.83) else "")
            m_["bmom_share"] = bs
            rows.append(m_); led[nm_] = sp
    inc = led["ladder13 w_bmom=2.83"]
    b1 = inc.sum() / PV / NS
    P_(f"\n   B1 GATE: {b1:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(b1 - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(b1 - 14.72) >= 0.6:
        out.close(); return
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "cross.csv"), index=False)

    # =====================================================================================
    # PHASE 2 - THE CONSENSUS THRESHOLD, aggregated over neighbours
    # =====================================================================================
    P_(f"\n{'='*136}\n=== PHASE 2: the consensus threshold k, the only other live constant")
    P_(f"{'='*136}")
    P_("W67 proved the Solar side reduces to 'at least k of NMEM net-long'. k=6 of 13 is the")
    P_("vendor's. Questioned by AGGREGATING over k in {5,6,7}, never by selecting one.\n")
    P_(HDR)
    cons = []
    for lname, lad, ks in (("13", L13, (5, 6, 7)), ("18", L18, (7, 8, 9))):
        cols = [idx_of[v] for v in lad]
        for k in ks:
            r = object_from([target_k(cols, k, 2.83)], "")
            if r is None:
                continue
            sp, trl = r
            m_ = met(sp, len(trl), f"ladder{lname} k={k} single")
            show(m_, bmom_share(trl, lad)); cons.append(m_)
        tgs = [target_k(cols, k, 2.83) for k in ks]
        r = object_from(tgs, "")
        if r is not None:
            sp, trl = r
            m_ = met(sp, len(trl), f"ladder{lname} k AGGREGATE {ks}")
            show(m_, bmom_share(trl, lad), "   <- aggregate")
            cons.append(m_); led[m_["arm"]] = sp
    pd.DataFrame(cons).to_csv(os.path.join(OUT, "consensus.csv"), index=False)

    # =====================================================================================
    # PHASE 3 - THE TILT
    # =====================================================================================
    P_(f"\n{'='*136}\n=== PHASE 3: the tilt - agrees on 37.5 % of bars, drops the "
       f"requirement 6 -> 5, never examined")
    P_(f"{'='*136}")
    P_(HDR)
    tl_rows = []
    cols13 = [idx_of[v] for v in L13]
    for lab, tm in (("tilt OFF (mult 1.0)", 1.0), ("tilt 1.25 INCUMBENT", 1.25),
                    ("tilt 1.5", 1.5)):
        tgs = [target([idx_of[v] for v in L13 if v <= c], 2.83, tiltmul=tm) for c in CUTS]
        r = object_from(tgs, "")
        if r is None:
            continue
        sp, trl = r
        m_ = met(sp, len(trl), lab)
        show(m_, bmom_share(trl, L13),
             "   <- INCUMBENT" if abs(tm - 1.25) < 1e-9 else "")
        tl_rows.append(m_)
    pd.DataFrame(tl_rows).to_csv(os.path.join(OUT, "tilt.csv"), index=False)

    # =====================================================================================
    # PHASE 4 - PER YEAR and SUB-PERIOD, both labelled with effective sample size
    # =====================================================================================
    P_(f"\n{'='*136}\n=== PHASE 4: per year (5 quasi-independent) and rolling 24-month "
       f"(22 windows, EFFECTIVE independent count about 1)")
    P_(f"{'='*136}")
    P_(f"{'arm':<32}" + "".join(f"{y:>10}" for y in yrs) + f"{'years won':>12}")
    for nm_, sp in led.items():
        pv = [sp[sdate.year == y].sum() / PV / max((sdate.year == y).sum(), 1) for y in yrs]
        iv = [inc[sdate.year == y].sum() / PV / max((sdate.year == y).sum(), 1) for y in yrs]
        P_(f"{nm_:<32}" + "".join(f"{x:>10.2f}" for x in pv)
           + f"{sum(1 for a, b_ in zip(pv, iv) if a > b_):>9} of 5")
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    P_(f"\n{'arm':<32}{'windows':>9}{'trdD+% wins':>14}{'weekly$ wins':>15}{'top5DD wins':>14}"
       f"{'ALL THREE':>12}")
    for nm_, sp in led.items():
        if nm_ == "ladder13 w_bmom=2.83":
            continue
        c1 = c2 = c3 = c4 = tot = 0
        for eend in ends:
            mk = (sdate > eend - pd.DateOffset(months=24)) & (sdate <= eend)
            a_, bb = met(sp, 0, "", mk), met(inc, 0, "", mk)
            if a_ is None or bb is None:
                continue
            tot += 1
            x1 = a_["trdpos"] > bb["trdpos"]; x2 = a_["weekly"] > bb["weekly"]
            x3 = a_["dd_top5"] < bb["dd_top5"]
            c1 += x1; c2 += x2; c3 += x3; c4 += (x1 and x2 and x3)
        P_(f"{nm_:<32}{tot:>9}{100*c1/max(tot,1):>13.0f}%{100*c2/max(tot,1):>14.0f}%"
           f"{100*c3/max(tot,1):>13.0f}%{100*c4/max(tot,1):>11.0f}%")
    P_(f"\n=== STATUS: nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
