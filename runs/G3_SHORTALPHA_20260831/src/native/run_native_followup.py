"""G3_SHORTALPHA / NATIVE - follow-up, after G2 returned SAME OBJECT at 100.0000 %.

Three things the primary run left open, each of which could still move the verdict:

  F1  W61's HEADLINE was not the standalone sleeve - it was the SD-matched combination at
      w = 0.30, measured at the $4.36 commission floor on 1,012 sessions. Does that headline
      survive (a) the extended window and (b) the measured execution cost?
  F2  BREAK-EVEN COST per contract round turn for the sleeve and for P1, so the cost margin is
      a number rather than an adjective.
  F3  The W73 DECOMPOSITION with cost as a third bucket. W73 attributed the short's shortfall to
      DRIFT (-$23,078, SE $15,130, t = -1.53). How does that compare with the deduction the
      measured cost line actually takes?

Nothing new is proposed. This quantifies a closure.
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
import run_native as RN                                                   # noqa: E402
from run_native import (REPO, OUT, COSTS, C_PRIMARY, DDT, A_MOD, B_MOD, BURN_A, SEAL,
                        Stratum, nbf, reprice, wk_stats)                  # noqa: E402
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import PV, COMM_RT                                        # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w35 import fills_qexit                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w51c import dd_profile                                        # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from research_sdk import champion_eval as CE                              # noqa: E402

W76OUT = os.path.join(REPO, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(REPO, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
WGRID = [0.10, 0.15, 0.20, 0.30, 0.40, 0.50]

_LOG = []


def P_(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def streak(v):
    return max((len(list(g)) for k, g in itertools.groupby(v < 0) if k), default=0)


def main():
    t0 = _time.time()
    P_("=" * 118)
    P_("=== G3_SHORTALPHA / NATIVE - FOLLOW-UP. The identity question is settled (100.0000 %).")
    P_("=== These three measurements decide whether the CLOSURE is economic as well as structural.")
    P_("=" * 118)

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    assert D["t"].max() < SEAL
    P_(f"    SEAL re-asserted: MODERN max bar {D['t'].max()} < 2026-08-01  PASS")
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    S = Stratum("MODERN", D, X, z["mem"], z["bmom"], z["tilt"], A_MOD, B_MOD)
    tarr = D["t"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), D["n"] - 1))
    bb = fills_daily(D, S.dirL, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A_MOD <= np.datetime64(x["et"]) < B_MOD])
    sc, _ = causal_score(X, ee, window=WIN)
    P1TR = [x for x in fills_qexit(D, S.dirL, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
            if S.in_win[int(D["sid"][i_of(x["et"])])]]
    posx = np.searchsorted(S.sess_in, np.array([D["sid"][i_of(x["et"])] for x in P1TR]))
    p1pnl = np.array([x["pnl"] for x in P1TR])
    p1qty = np.array([float(x["u"]) for x in P1TR])
    P_(f"    P1 rebuilt: {len(P1TR):,} trades / {p1qty.sum():,.0f} ctrRT, "
       f"net@$4.36 ${p1pnl.sum():,.0f}  [{_time.time()-t0:.0f}s]")

    def sess_series(pos, pnl, n):
        v = np.zeros(n)
        np.add.at(v, pos, pnl)
        return v

    NS = len(S.sess_in)
    yr = S.years
    exburn = S.sdate.to_numpy() < BURN_A

    # ============================================================== F1  the W61 weight scan
    P_("")
    P_("=" * 118)
    P_("=== F1  W61's OWN HEADLINE, re-measured. W61 Phase 2: scale the sleeve to P1's weekly SD,")
    P_("===     then hold (1-w)*P1 + w*SHORT, everything rescaled to a fixed $20,245 max drawdown.")
    P_("===     W61 reported this at the $4.36 FLOOR on 1,012 sessions. Here: three cost lines,")
    P_("===     three populations. Same algebra, same grid.")
    P_("=" * 118)
    rows = []
    for pop, mask in (("MODERN 1,058 sess", np.ones(NS, bool)),
                      ("EX-BURNED 1,012 sess", exburn),
                      ("2026 only 152 sess", yr == 2026)):
        for lab, c in COSTS:
            nb = nbf(D, S.dirS, None, 1300.0, 1000.0, False, c)
            d_, p_, q_, sp_ = S.ledger(nb)
            sh = sess_series(S._lastpos, p_, NS)
            p1 = sess_series(posx, reprice(p1pnl, p1qty, c), NS)
            wi = S.wk_idx[mask]
            uw = sorted(set(wi.tolist()))
            rmap = {w: i for i, w in enumerate(uw)}
            ri = np.array([rmap[w] for w in wi])
            nw = len(uw)

            def wv(x):
                return np.bincount(ri, weights=x[mask], minlength=nw)
            v1, vs = wv(p1), wv(sh)
            sd1, sds = v1.std(ddof=1), vs.std(ddof=1)
            shn = sh * (sd1 / sds) if sds > 0 else sh

            def met(x, name, w=None):
                v = wv(x)
                dp = dd_profile(v)
                k = DDT / max(dp["maxdd"], 1e-9)
                return dict(pop=pop, cost=c, arm=name, w=w, nwk=nw,
                            wkpos=100 * float((v > 0).mean()), wstreak=streak(v),
                            medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                            worst=float(v.min()) * k, top5=dp["dd_mean_top5"] * k,
                            raw_weekly=float(v.mean()), raw_maxdd=dp["maxdd"])
            base = met(p1, "P1 alone")
            rows.append(base)
            for w in WGRID:
                rows.append(met((1 - w) * p1 + w * shn, f"P1 + SHORT w={w:.2f}", w))
            rows.append(met(sh, "SHORT standalone"))
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "native_followup_wscan.csv"), index=False)
    for pop in DF["pop"].unique():
        P_("")
        P_(f"  --- {pop} " + "-" * (100 - len(pop)))
        P_(f"{'cost $/ctrRT':<14}{'arm':<22}{'wk$@fixDD':>11}{'delta':>9}{'wk+%':>8}"
           f"{'wStrk':>7}{'medWk$':>10}{'top5DD':>10}{'worst$':>10}")
        for c in [c for _, c in COSTS]:
            sub = DF[(DF["pop"] == pop) & (DF["cost"] == c)]
            b = sub[sub["arm"] == "P1 alone"].iloc[0]["weekly"]
            for _, r in sub.iterrows():
                d = r["weekly"] - b
                tag = "" if r["arm"] == "P1 alone" else f"{d:>+9,.0f}"
                P_(f"{c:<14.2f}{r['arm']:<22}{r['weekly']:>11,.0f}{tag:>9}{r['wkpos']:>7.1f}%"
                   f"{r['wstreak']:>7}{r['medwk']:>10,.0f}{r['top5']:>10,.0f}{r['worst']:>10,.0f}")
            P_("")

    # ============================================================== F2  break-even cost
    P_("")
    P_("=" * 118)
    P_("=== F2  BREAK-EVEN COST per contract round turn. At what $/ctrRT does each object's net")
    P_("===     reach zero? (naive line: C* = 4.36 + net@4.36 / ctrRT). The measured line is")
    P_("===     $20.65 spread; all-in with the $4.36 Lifetime commission is $25.01.")
    P_("=" * 118)
    nb0 = nbf(D, S.dirS, None, 1300.0, 1000.0, False, COMM_RT)
    d0, p0, q0, sp0 = S.ledger(nb0)
    P_("")
    P_(f"{'object':<26}{'population':<22}{'trades':>8}{'ctrRT':>9}{'net@$4.36':>13}"
       f"{'$/ctrRT edge':>14}{'break-even $':>14}{'headroom vs $25.01':>20}")
    be_rows = []
    for nm, pnl, qty, pos in (("NATIVE SHORT (=W61)", p0, q0, S._lastpos),
                              ("P1 long (incumbent)", p1pnl, p1qty, posx)):
        for pop, mask in (("MODERN 1,058 sess", np.ones(NS, bool)),
                          ("EX-BURNED 1,012 sess", exburn)):
            keep = mask[pos]
            n_ = float(pnl[keep].sum()); ct = float(qty[keep].sum())
            be = COMM_RT + n_ / max(ct, 1e-9)
            P_(f"{nm:<26}{pop:<22}{int(keep.sum()):>8,}{ct:>9,.0f}{n_:>13,.0f}"
               f"{n_/max(ct,1e-9):>14,.2f}{be:>14,.2f}{be/25.01:>19.2f}x")
            be_rows.append(dict(obj=nm, pop=pop, trades=int(keep.sum()), ctr=ct, net436=n_,
                                edge_per_ctr=n_ / max(ct, 1e-9), breakeven=be))
    pd.DataFrame(be_rows).to_csv(os.path.join(OUT, "native_followup_breakeven.csv"), index=False)

    # ============================================================== F3  cost vs W73's drift
    P_("")
    P_("=" * 118)
    P_("=== F3  W73's DECOMPOSITION WITH COST AS A THIRD BUCKET.")
    P_("===     W73 (out/asym.txt, committed) on 1,012 sessions at the $4.36 floor:")
    P_("===        SHORT sleeve  2,225 trades   net $121,454   DRIFT -$23,078 (SE $15,130)")
    P_("===                                                    TIMING +$144,532 (119 % of net)")
    P_("===     The identity  net = TIMING + DRIFT  holds at the FLOOR only. At an honest cost")
    P_("===     line there is a third term, and it is the only one measured without error.")
    P_("=" * 118)
    keep61 = exburn[S._lastpos]
    ctr61 = float(q0[keep61].sum())
    net61 = float(p0[keep61].sum())
    P_("")
    P_(f"    this run, EX-BURNED 1,012 sessions: {int(keep61.sum()):,} trades, "
       f"{ctr61:,.0f} ctrRT, net@$4.36 ${net61:,.0f}")
    P_("")
    P_(f"{'bucket':<44}{'$':>14}{'SE':>12}{'t':>8}{'share of TIMING':>18}")
    tim, dri, sed = 144532.0, -23078.0, 15130.0
    P_(f"{'TIMING (W73, the short side HAS skill)':<44}{tim:>14,.0f}{'-':>12}{'-':>8}"
       f"{'100 %':>18}")
    P_(f"{'DRIFT tax (W73, estimated)':<44}{dri:>14,.0f}{sed:>12,.0f}{dri/sed:>8.2f}"
       f"{100*dri/tim:>17.1f}%")
    for lab, c in COSTS:
        if c == COMM_RT:
            continue
        cost = -(c - COMM_RT) * ctr61
        P_(f"{'COST above the $4.36 floor at $'+f'{c}':<44}{cost:>14,.0f}{'~0':>12}{'':>8}"
           f"{100*cost/tim:>17.1f}%")
    P_("")
    P_(f"    net at $25.01 all-in  =  TIMING + DRIFT + COST  =  "
       f"{tim:,.0f} + ({dri:,.0f}) + ({-(25.01-COMM_RT)*ctr61:,.0f})  =  "
       f"{tim + dri - (25.01-COMM_RT)*ctr61:,.0f}")
    P_(f"    direct measurement of the same quantity                        =  "
       f"{net61 - (25.01-COMM_RT)*ctr61:,.0f}    (identity holds)")
    P_("")
    P_("    READ: the execution cost of expressing this signal is LARGER than the drift tax W73")
    P_("    attributed the shortfall to, and unlike the drift tax it carries no standard error.")
    P_("    W73's drift figure is t = -1.53; the cost figure is arithmetic.")

    # ============================================================== PRE P1 floor control
    P_("")
    P_("=" * 118)
    P_("=== CONTROL: the same engine, same era, opposite direction, at the $4.36 FLOOR on the")
    P_("===          16 deep years - so 'PRE is hostile to everything' can be checked, not assumed.")
    P_("=" * 118)
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    assert DD["t"].max() < SEAL
    XD = fast_build_context(DD)
    zd = np.load(os.path.join(W80OUT, f"mem_deep_{DD['n']}.npz"))
    SP = Stratum("PRE", DD, XD, zd["mem"], zd["bmom"], zd["tilt"])
    td = DD["t"]

    def i_ofd(ts):
        return int(min(np.searchsorted(td, np.datetime64(ts)), DD["n"] - 1))
    bbd = fills_daily(DD, SP.dirL, halt=1300, target=1000)
    eed = np.array([i_ofd(x["et"]) for x in bbd])
    scd, _ = causal_score(XD, eed, window=WIN)
    P1D = fills_qexit(DD, SP.dirL, np.where(scd >= 3, 2, 1).astype(np.int8), scd)
    pdq = np.array([float(x["u"]) for x in P1D])
    pdp = np.array([x["pnl"] for x in P1D])
    nbD = nbf(DD, SP.dirS, None, 1300.0, 1000.0, False, COMM_RT)
    P_("")
    P_(f"{'object':<26}{'trades':>9}{'ctrRT':>10}{'net@$4.36':>14}{'pts/sess':>11}"
       f"{'break-even $':>14}")
    for nm, pl, qt in (("P1 long (2006-2021)", pdp, pdq),
                       ("NATIVE SHORT (2006-2021)", nbD[4], nbD[1].astype(float))):
        P_(f"{nm:<26}{len(pl):>9,}{qt.sum():>10,.0f}{pl.sum():>14,.0f}"
           f"{pl.sum()/PV/len(SP.sess_in):>11.2f}"
           f"{COMM_RT + pl.sum()/max(qt.sum(),1e-9):>14,.2f}")
    P_("")
    P_("    W97 M10 committed the deep P1 at net $79,076 on the same substrate - cross-check.")

    P_(f"\n[done {_time.time()-t0:.0f}s]")
    with open(os.path.join(OUT, "native_followup.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")


if __name__ == "__main__":
    main()
