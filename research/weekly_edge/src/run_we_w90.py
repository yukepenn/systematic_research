"""WE_W90 - B-MOM's TWO SIDES, AS SLEEVES.

Spec: runs/WE_W90_BMOMSIDES/spec.yaml, committed BEFORE this ran.

The campaign rejected a short sleeve five times and every one of those was a mirrored Solar
ratchet. B-MOM's short leg is not that: it is the displacement channel's own negative side, the
same estimator rather than a sign flip of a different one. This wave measures it two ways -
as an attribution split of the object we have (which cannot be traded, because the session box
couples the sides) and as re-simulated standalone sleeves with their own boxes (which can).
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
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W90_BMOMSIDES", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
C_BMOM = 12.99          # W89 FACT, candidate-specific
C_X9A = 14.55           # W89 FACT
RT_X9A = 10.79          # W89 FACT, contract RT per week
RNG = np.random.default_rng(20260890)
NDRAW = 200


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "sides.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    bmom = z["bmom"]
    sess_end = D["sess_end"]
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    bm = np.where(flatm, 0, bmom).astype(np.int8)

    st = np.zeros(D["n_sess"], np.int64)
    st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    yr = sdate.year.to_numpy()
    t12 = np.asarray(sdate >= pd.Timestamp("2025-08-01"))
    t24 = np.asarray(sdate >= pd.Timestamp("2024-08-01"))
    P_(f"=== substrate {n:,} bars / {len(sess_in)} in-window sessions / {len(set(wk))} weeks "
       f"[{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def keep(trl):
        return [x for x in trl if in_win[int(sid[i_of(x["et"])])]]

    # ============================================================ MEASUREMENT A: attribution
    P_("")
    P_("=" * 118)
    P_("=== MEASUREMENT A: ATTRIBUTION of the object we already have")
    P_("    NOT TRADEABLE. The session box halts on COMBINED realised P&L, so these two series")
    P_("    are coupled by construction and neither can be run on its own from this split.")
    P_("=" * 118)
    TB = keep(sfills(D, bm, halt=1300.0, target=1000.0))
    L = [x for x in TB if x["d"] > 0]; S = [x for x in TB if x["d"] < 0]
    P_(f"{'side':<8}{'trades':>9}{'share':>9}{'net $':>14}{'$/trade':>11}{'win %':>9}"
       f"{'median':>10}")
    for nm, g in (("LONG", L), ("SHORT", S), ("BOTH", TB)):
        p = np.array([x["pnl"] for x in g])
        P_(f"{nm:<8}{len(g):>9,}{100*len(g)/len(TB):>8.1f}%{p.sum():>14,.0f}"
           f"{p.mean():>11,.1f}{100*(p>0).mean():>8.1f}%{np.median(p):>10,.1f}")
    P_("")
    P_("    pre-compact session reported 573 long / 579 short. This rebuild says "
       f"{len(L)} / {len(S)}.")
    P_(f"    {'AGREES' if (len(L),len(S))==(573,579) else 'DISAGREES - the earlier figure is WITHDRAWN'}")

    # ============================================================ MEASUREMENT B: sleeves
    P_("")
    P_("=" * 118)
    P_("=== MEASUREMENT B: RE-SIMULATED SLEEVES, each with its OWN session box")
    P_("=" * 118)
    OBJ = {}
    OBJ["BMOM_L"] = keep(sfills(D, np.where(bm > 0, 1, 0).astype(np.int8),
                                halt=1300.0, target=1000.0))
    OBJ["BMOM_S"] = keep(sfills(D, np.where(bm < 0, -1, 0).astype(np.int8),
                                halt=1300.0, target=1000.0))
    OBJ["BMOM_B"] = TB
    NWk = len(set(wk))
    SER, RTW = {}, {}
    for k, trl in OBJ.items():
        SER[k] = daily(trl); RTW[k] = sum(x["u"] for x in trl) / NWk
    SER["BMOM_L+S"] = SER["BMOM_L"] + SER["BMOM_S"]
    RTW["BMOM_L+S"] = RTW["BMOM_L"] + RTW["BMOM_S"]

    def pan(v, msk, cost_wk):
        w = pd.Series(v[msk]).groupby(wk[msk]).sum().to_numpy() - cost_wk
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    medwk=float(np.median(w)), maxdd=dp["maxdd"], top5=dp["dd_mean_top5"],
                    worst=float(w.min()), streak=int(stk),
                    weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    se=float(w.std(ddof=1) / np.sqrt(len(w))))

    ALL = np.ones(len(sess_in), bool)
    P_(f"{'sleeve':<12}{'trades':>8}{'ctrRT/wk':>10}{'wk $':>9}{'wk+%':>8}{'streak':>8}"
       f"{'maxDD':>10}{'top5DD':>9}{'worst':>10}{'wk$@fixDD':>11}")
    for k in ("BMOM_L", "BMOM_S", "BMOM_B", "BMOM_L+S"):
        a = pan(SER[k], ALL, C_BMOM * RTW[k])
        nt = len(OBJ[k]) if k in OBJ else len(OBJ["BMOM_L"]) + len(OBJ["BMOM_S"])
        P_(f"{k:<12}{nt:>8,}{RTW[k]:>10.2f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%"
           f"{a['streak']:>8}{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}{a['worst']:>10,.0f}"
           f"{a['weekly_dd']:>11,.0f}")

    # ---------------------------------------------------------------- H1: recency gate
    P_("")
    P_("=== H1: the ONLY chronology gate - effective over roughly the trailing two years")
    P_(f"{'sleeve':<12}{'period':<8}{'weeks':>7}{'trades':>8}{'wk $':>10}{'SE':>9}{'t':>7}"
       f"{'wk+%':>8}")
    h1 = {}
    for k in ("BMOM_L", "BMOM_S", "BMOM_B"):
        for lab, m in (("full", ALL), ("t24", t24), ("t12", t12)):
            a = pan(SER[k], m, C_BMOM * RTW[k])
            ntr = sum(1 for x in OBJ[k] if in_win[int(sid[i_of(x['et'])])]
                      and m[np.searchsorted(sess_in, int(sid[i_of(x['et'])]))])
            tstat = a["weekly"] / a["se"] if a["se"] > 0 else 0.0
            if lab == "t24":
                h1[k] = a["weekly"]
            P_(f"{k:<12}{lab:<8}{a['nwk']:>7}{ntr:>8,}{a['weekly']:>10,.0f}{a['se']:>9,.0f}"
               f"{tstat:>7.2f}{a['wkpos']:>7.1f}%")
        P_("")
    P_(f"    H1 (BMOM_S t24 weekly > 0): {h1['BMOM_S']:,.0f} -> "
       f"{'PASS' if h1['BMOM_S'] > 0 else 'FAIL'}")

    # ---------------------------------------------------------------- H2: weekly rho
    P_("")
    P_("=== H2: WEEKLY rho (the correct unit - W85 defect 3 / W88)")
    d = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    cl = pd.read_csv(os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out", "members.csv"))
    UNI = {"BMOM_L": SER["BMOM_L"], "BMOM_S": SER["BMOM_S"], "BMOM_B": SER["BMOM_B"],
           "X9a": cl["X9a"].to_numpy(), "P1": d["P1"].to_numpy(), "SHORT": d["SHORT"].to_numpy()}
    WKS = {k: pd.Series(v).groupby(wk).sum() for k, v in UNI.items()}
    names = list(UNI)
    P_(f"{'':<10}" + "".join(f"{k:>10}" for k in names))
    rows = []
    for a_ in names:
        line = f"{a_:<10}"
        for b_ in names:
            r = float(np.corrcoef(WKS[a_], WKS[b_])[0, 1])
            line += f"{r:>10.3f}"
            rows.append(dict(a=a_, b=b_, weekly_rho=r,
                             daily_rho=float(np.corrcoef(UNI[a_], UNI[b_])[0, 1])))
        P_(line)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "rho.csv"), index=False)
    rls = float(np.corrcoef(WKS["BMOM_L"], WKS["BMOM_S"])[0, 1])
    P_(f"\n    H2 (weekly rho(BMOM_L, BMOM_S) < 0.20): {rls:.3f} -> "
       f"{'PASS - two streams' if abs(rls) < 0.20 else 'FAIL - one stream'}")
    P_(f"    daily rho for the same pair: "
       f"{float(np.corrcoef(SER['BMOM_L'], SER['BMOM_S'])[0,1]):.3f}  "
       f"(quoted only to show the unit matters)")
    # underwater correlation, W56's number
    def uw(v, c):
        w = pd.Series(v).groupby(wk).sum().to_numpy() - c
        cum = np.cumsum(w)
        return np.maximum.accumulate(cum) - cum
    P_(f"    UNDERWATER-curve rho(BMOM_L, BMOM_S) = "
       f"{float(np.corrcoef(uw(SER['BMOM_L'], C_BMOM*RTW['BMOM_L']), uw(SER['BMOM_S'], C_BMOM*RTW['BMOM_S']))[0,1]):.3f}"
       f"   (W56 found this, not weekly rho, is what makes a sleeve pay)")

    # ---------------------------------------------------------------- H3: one box or two
    P_("")
    P_("=== H3: one shared box (incumbent) vs two independent boxes")
    a1 = pan(SER["BMOM_B"], ALL, C_BMOM * RTW["BMOM_B"])
    a2 = pan(SER["BMOM_L+S"], ALL, C_BMOM * RTW["BMOM_L+S"])
    legs = [("weekly $ at fixed DD", a2["weekly_dd"], a1["weekly_dd"], True),
            ("positive-week %", a2["wkpos"], a1["wkpos"], True),
            ("raw mean top-5 DD", a2["top5"], a1["top5"], False)]
    nwin = 0
    for nm, x2, x1, hi in legs:
        winb = (x2 > x1) if hi else (x2 < x1)
        nwin += winb
        P_(f"    {nm:<24} two boxes {x2:>10,.1f}   one box {x1:>10,.1f}   "
           f"{'TWO' if winb else 'ONE'}")
    P_(f"    H3 (two boxes win >= 2 legs): {nwin}/3 -> {'FIRES' if nwin >= 2 else 'does not fire'}")
    P_("    NOTE: two boxes doubles the risk budget (each side can lose $1,300), so a money")
    P_("    win here is partly a leverage effect and would need its own exposure-matched null.")

    # ---------------------------------------------------------------- H4: specificity null
    P_("")
    P_("=== H4: is the SHORT leg specific, or is it generic exposure?")
    P_("    count-matched AND contract-minute-matched random subsets of BMOM's own trades")
    occ_all = np.zeros(n)
    for x in TB:
        occ_all[i_of(x["et"]):i_of(x["xt"])] += x["u"]
    cm_short = sum((i_of(x["xt"]) - i_of(x["et"])) * x["u"] for x in S)
    nS = len(S)
    X9 = cl["X9a"].to_numpy()

    def basket_legs(bm_series, rt_bm):
        v = 2 * bm_series + 3 * X9
        cost = 2 * C_BMOM * rt_bm + 3 * C_X9A * RT_X9A
        a = pan(v, ALL, cost)
        return a["weekly_dd"], a["wkpos"], a["top5"]

    ser_L = daily([x for x in TB if x["d"] > 0])
    real = basket_legs(SER["BMOM_B"], RTW["BMOM_B"])
    long_only = basket_legs(ser_L, sum(x["u"] for x in L) / NWk)
    P_(f"    basket 2:3 with the REAL short leg : money {real[0]:>8,.0f}  wk+% {real[1]:>5.1f}  "
       f"top5 {real[2]:>9,.0f}")
    P_(f"    basket 2:3 with NO short leg       : money {long_only[0]:>8,.0f}  "
       f"wk+% {long_only[1]:>5.1f}  top5 {long_only[2]:>9,.0f}")
    idx_all = np.arange(len(TB))
    draws = []
    for _ in range(NDRAW):
        # match count exactly; then accept only draws within 5 % on contract-minutes
        for _try in range(40):
            pick = RNG.choice(idx_all, size=nS, replace=False)
            g = [TB[i] for i in pick]
            cm = sum((i_of(x["xt"]) - i_of(x["et"])) * x["u"] for x in g)
            if abs(cm - cm_short) <= 0.05 * cm_short:
                break
        rest = [TB[i] for i in idx_all if i not in set(pick)]
        draws.append(basket_legs(daily(rest), sum(x["u"] for x in rest) / NWk))
    draws = np.array(draws)
    P_("")
    P_(f"    {NDRAW} count- and contract-minute-matched removals of the SAME NUMBER of trades:")
    P_(f"{'leg':<22}{'real (short kept)':>20}{'null mean':>12}{'null p95':>12}{'pctile':>9}")
    lab = ["weekly $ at fixed DD", "positive-week %", "raw mean top-5 DD"]
    pcts = []
    for j, nm in enumerate(lab):
        rv = real[j]; dv = draws[:, j]
        # for top-5 DD lower is better
        pc = 100 * float((dv > rv).mean()) if j == 2 else 100 * float((dv < rv).mean())
        pcts.append(pc)
        P_(f"{nm:<22}{rv:>20,.1f}{dv.mean():>12,.1f}"
           f"{np.percentile(dv, 5 if j == 2 else 95):>12,.1f}{pc:>8.1f}%")
    P_(f"    H4 (>= 95th on all three): {['%.0f' % p for p in pcts]} -> "
       f"{'SPECIFIC' if all(p >= 95 for p in pcts) else 'GENERIC on at least one leg'}")
    pd.DataFrame(draws, columns=["money", "wkpos", "top5"]).to_csv(
        os.path.join(OUT, "null_short.csv"), index=False)

    # ---------------------------------------------------------------- H5: regime
    P_("")
    P_("=== H5: per-year weekly $ (causal partition - the calendar is known in advance)")
    P_(f"{'sleeve':<12}" + "".join(f"{y:>10}" for y in sorted(set(yr))))
    yrows = []
    for k in ("BMOM_L", "BMOM_S", "BMOM_B", "X9a"):
        v = SER[k] if k in SER else X9
        rt = RTW[k] if k in RTW else RT_X9A
        c = C_BMOM if k.startswith("BMOM") else C_X9A
        line = f"{k:<12}"
        for y in sorted(set(yr)):
            m = yr == y
            a = pan(v, m, c * rt)
            line += f"{a['weekly']:>10,.0f}"
            yrows.append(dict(sleeve=k, year=int(y), weekly=a["weekly"], wkpos=a["wkpos"],
                              nwk=a["nwk"]))
        P_(line)
    pd.DataFrame(yrows).to_csv(os.path.join(OUT, "per_year.csv"), index=False)

    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"), "BMOM_L": SER["BMOM_L"],
                  "BMOM_S": SER["BMOM_S"], "BMOM_B": SER["BMOM_B"]}).to_csv(
        os.path.join(OUT, "sleeves_daily.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
