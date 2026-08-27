"""WE_W92 - THE MASTER EXECUTION LAYER, and NETFUSE.

Spec: runs/WE_W92_MASTER/spec.yaml, committed BEFORE this ran.

Two NinjaScript strategies on one netted NQ account are not the algebraic portfolio: when one
sleeve buys while another sells on the same bar, the account crosses internally and never sends
those contracts. Mark-to-market P&L is additive by construction (both sleeves fill at the same
next-bar open), so the whole difference is TURNOVER, and turnover is cost.

Second half: NETFUSE, the single netted long-and-short object. W91 amendment 1 established the
mirrored OR gate already exists inside the SHORT sleeve; what does not exist is one target, one
box, one ledger, with direct reversals instead of two sleeves holding opposite positions.
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
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W92_MASTER", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
C_BMOM, C_X9A, C_P1 = 12.99, 14.55, 14.52          # W89, candidate-specific $/contract RT


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "master.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c, fb, lb = D["o"], D["c"], D["fb"], D["lb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    sess_end = D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}
    bm = np.where(flatm, 0, bmom).astype(np.int8)

    st = np.zeros(D["n_sess"], np.int64)
    st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    inw = np.array([in_win[s] for s in sid])
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    yr = sdate.year.to_numpy()
    NWk = len(set(wk))

    # dp[i] = the price change a position held THROUGH bar i earns.
    dp = np.zeros(n)
    dp[:-1] = o[1:] - o[:-1]
    dp[lb] = c[lb] - o[lb]                 # a session-last bar settles at its CLOSE
    P_(f"=== {len(sess_in)} sessions / {NWk} weeks / {n:,} bars [{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
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
            tgt[i] = g
        return tgt

    def TG_for(chan):
        d = {}
        for name, vols in MEMBERS.items():
            cols = [idx_l13[v] for v in vols]
            s_ = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            d[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        return d

    def vote_(TGx, side):
        vs = []
        for m_ in MEMBERS:
            tg = TGx[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (X["dL"] if side > 0 else X["dS"]) if dg else okv
                    hit = (tg > 0) if side > 0 else (tg < 0)
                    vs.append(np.where(hit & a_, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)

    def keep(trl):
        return [x for x in trl if in_win[int(sid[i_of(x["et"])])]]

    def qscore(p):
        bb = fills_daily(D, np.abs(p).astype(np.int8), halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return s_

    def long_obj(TGx):
        p = (vote_(TGx, +1) >= 0.5).astype(np.int8)
        s_ = qscore(p)
        return keep(fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_))

    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    TG0 = TG_for(bmom)
    TR = {}
    TR["P1"] = long_obj(TG0)
    TR["X9a"] = long_obj(TG_for(CH["X9a_disp_sessanchor"]))
    TR["BMOM"] = keep(sfills(D, bm, halt=1300.0, target=1000.0))
    TR["SHORT"] = keep(sfills(D, -(vote_(TG0, -1) >= 0.5).astype(np.int8),
                              halt=1300.0, target=1000.0))
    P_(f"    sleeves built [{_time.time()-t0:.0f}s]")

    # ---------------------------------------------------------------- occupancy + assertion
    def occ_of(trl):
        v = np.zeros(n)
        for x in trl:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            end = b_ + 1 if lb[b_] else b_
            v[a_:end] += x["d"] * x["u"]
        return v

    OCC = {k: occ_of(v) for k, v in TR.items()}
    P_("")
    P_("=== PRECONDITION: does the occupancy simulator reproduce the trade ledger EXACTLY?")
    ok = True
    for k, trl in TR.items():
        mtm = float((OCC[k] * dp).sum()) * PV
        led = sum(x["pnl"] + COMM_RT * x["u"] for x in trl)
        d_ = abs(mtm - led)
        ok &= d_ < 0.01
        P_(f"    {k:<7} occupancy MTM ${mtm:>13,.2f}   trade ledger (gross) ${led:>13,.2f}   "
           f"|diff| {d_:.6f}  {'OK' if d_ < 0.01 else '*** MISMATCH ***'}")
    if not ok:
        P_("    the simulator does not reproduce the ledger. NO NUMBERS ARE ISSUED.")
        out.close(); return

    def daily_from_occ(occ):
        v = occ * dp * PV
        return np.bincount(sid, weights=v, minlength=D["n_sess"])[sess_in]

    def turnover(occ):
        return np.abs(np.diff(np.concatenate([[0.0], occ, [0.0]])))

    # ============================================================ PHASE 1: the master layer
    P_("")
    P_("=" * 122)
    P_("=== PHASE 1: THE MASTER EXECUTION LAYER for 2 BMOM : 3 X9a")
    P_("=" * 122)
    SL = [("BMOM", 2.0), ("X9a", 3.0)]
    occ_k = {k: w * OCC[k] for k, w in SL}
    acct = sum(occ_k.values())
    gross_ct = sum(turnover(v).sum() for v in occ_k.values())
    net_ct = turnover(acct).sum()
    saved = gross_ct - net_ct
    P_(f"    gross contracts sent by two independent strategies : {gross_ct:>12,.0f}")
    P_(f"    net contracts sent by ONE master account           : {net_ct:>12,.0f}")
    P_(f"    INTERNALLY CROSSED and never sent                  : {saved:>12,.0f}  "
       f"({100*saved/gross_ct:.3f} % of gross)")
    P_(f"    H1 threshold was >= 2.000 % -> "
       f"{'FIRES' if 100*saved/gross_ct >= 2.0 else 'does NOT fire'}")
    # a contract round turn is 2 contract-sides; costs are quoted per ROUND TURN
    rt_saved = saved / 2.0
    P_("")
    P_(f"    saved round turns {rt_saved:,.0f} over {NWk} weeks = {rt_saved/NWk:.3f} per week")
    for lab, rate in (("commission only ($4.36/RT)", COMM_RT),
                      ("+ spread at BMOM's rate ($12.99)", COMM_RT + C_BMOM),
                      ("+ spread at X9a's rate ($14.55)", COMM_RT + C_X9A)):
        P_(f"      {lab:<34} ${rate*rt_saved:>10,.0f} total   "
           f"${rate*rt_saved/NWk:>7,.2f}/week")

    P_("")
    both = np.abs(occ_k["BMOM"]) > 0
    bothx = np.abs(occ_k["X9a"]) > 0
    shared = both & bothx & inw
    opp = shared & ((occ_k["BMOM"] * occ_k["X9a"]) < 0)
    phantom = inw & (np.abs(acct) < 1e-9) & (sum(np.abs(v) for v in occ_k.values()) > 0)
    P_(f"    shared minutes (both sleeves holding)      {int(shared.sum()):>10,}  "
       f"{100*shared.sum()/max(inw.sum(),1):.2f} % of in-window minutes")
    P_(f"    ... of which OPPOSITE signs                {int(opp.sum()):>10,}  "
       f"{100*opp.sum()/max(shared.sum(),1):.1f} % of shared")
    P_(f"    PHANTOM FLAT (account 0, sleeves not)      {int(phantom.sum()):>10,}  "
       f"{100*phantom.sum()/max(inw.sum(),1):.3f} % of in-window minutes")
    P_("")
    gross_exp = sum(np.abs(v) for v in occ_k.values())
    P_(f"{'':<26}{'PEAK':>8}{'time-wtd':>11}")
    P_(f"{'    sum of sleeve |ctr|':<26}{gross_exp[inw].max():>8.0f}"
       f"{gross_exp[inw].mean():>11.3f}")
    P_(f"{'    NET account |ctr|':<26}{np.abs(acct)[inw].max():>8.0f}"
       f"{np.abs(acct)[inw].mean():>11.3f}")
    pd.DataFrame([dict(gross_contracts=gross_ct, net_contracts=net_ct, saved=saved,
                       pct=100 * saved / gross_ct, rt_saved=rt_saved,
                       shared_min=int(shared.sum()), opposite_min=int(opp.sum()),
                       phantom_min=int(phantom.sum()),
                       peak_gross=float(gross_exp[inw].max()),
                       peak_net=float(np.abs(acct)[inw].max()))]).to_csv(
        os.path.join(OUT, "netting.csv"), index=False)

    # ---------------------------------------------------------------- risk, net vs gross cost
    def pan(v, msk, cost_wk):
        w = pd.Series(v[msk]).groupby(wk[msk]).sum().to_numpy() - cost_wk
        dpf = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dpf["maxdd"], top5=dpf["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), weekly_dd=float(w.mean()) * DDT / max(dpf["maxdd"], 1e-9),
                    se=float(w.std(ddof=1) / np.sqrt(len(w))))
    ALL = np.ones(len(sess_in), bool)
    ser = daily_from_occ(acct)
    rt_gross_wk = (2 * sum(x["u"] for x in TR["BMOM"]) + 3 * sum(x["u"] for x in TR["X9a"])) / NWk
    cost_gross = (2 * sum(x["u"] for x in TR["BMOM"]) * (COMM_RT + C_BMOM)
                  + 3 * sum(x["u"] for x in TR["X9a"]) * (COMM_RT + C_X9A)) / NWk
    cost_net = cost_gross - (COMM_RT + C_BMOM) * rt_saved / NWk
    P_("")
    P_(f"{'2:3 basket':<28}{'$/wk cost':>11}{'wk $':>9}{'wk+%':>8}{'maxDD':>10}{'top5DD':>9}")
    for lab, cw in (("GROSS turnover (2 strategies)", cost_gross),
                    ("NET turnover (master account)", cost_net)):
        a = pan(ser, ALL, cw)
        P_(f"{lab:<28}{cw:>11,.0f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%"
           f"{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}")
    P_("    (commission is INCLUDED in these cost lines; the daily series is gross of it)")

    # ============================================================ PHASE 2: NETFUSE
    P_("")
    P_("=" * 122)
    P_("=== PHASE 2: NETFUSE - one target, ONE box, ONE ledger, direct reversals")
    P_("=" * 122)
    vl = vote_(TG0, +1) >= 0.5
    vs_ = vote_(TG0, -1) >= 0.5
    both_fire = vl & vs_
    P_(f"    long vote fires {100*vl.mean():.2f} % of bars, short vote {100*vs_.mean():.2f} %, "
       f"BOTH {100*both_fire.mean():.4f} % ({int(both_fire.sum()):,} bars)")
    P_("    tie rule (preregistered): both -> FLAT.")
    tgt = np.where(both_fire, 0, np.where(vl, 1, np.where(vs_, -1, 0))).astype(np.int8)
    s_q = qscore(tgt)
    sz1 = np.ones(n, np.int8)
    szq = np.where((tgt > 0) & (s_q >= 3), 2, 1).astype(np.int8)
    TR["NETFUSE_1"] = keep(sfills(D, tgt, size_at_entry=sz1, halt=1300.0, target=1000.0))
    TR["NETFUSE_Q"] = keep(sfills(D, tgt, size_at_entry=szq, halt=1300.0, target=1000.0))
    for k in ("NETFUSE_1", "NETFUSE_Q"):
        OCC[k] = occ_of(TR[k])
        mtm = float((OCC[k] * dp).sum()) * PV
        led = sum(x["pnl"] + COMM_RT * x["u"] for x in TR[k])
        assert abs(mtm - led) < 0.01, (k, mtm, led)

    CM = {k: float(np.abs(OCC[k])[inw].sum()) for k in OCC}
    RTW = {k: sum(x["u"] for x in TR[k]) / NWk for k in TR}
    COSTS = {"P1": C_P1, "X9a": C_X9A, "BMOM": C_BMOM, "SHORT": C_P1,
             "NETFUSE_1": C_P1, "NETFUSE_Q": C_P1}
    SER = {k: daily_from_occ(OCC[k]) for k in OCC}
    # comparator: P1 + SHORT as TWO sleeves, 1:1
    occ_ps = OCC["P1"] + OCC["SHORT"]
    cm_ps = float(np.abs(OCC["P1"])[inw].sum() + np.abs(OCC["SHORT"])[inw].sum())
    ser_ps = SER["P1"] + SER["SHORT"]
    cost_ps = (COSTS["P1"] * RTW["P1"] + COSTS["SHORT"] * RTW["SHORT"])
    tgt_cm = CM["P1"]
    P_("")
    P_(f"{'object':<24}{'trades':>8}{'scale':>7}{'wk $':>9}{'wk+%':>8}{'strk':>6}"
       f"{'maxDD':>10}{'top5DD':>9}{'worst':>10}{'wk$@fixDD':>11}")
    rows = []
    for lab, s_ser, s_cm, s_cost, s_ntr in (
            ("P1 (long-only, fused)", SER["P1"], CM["P1"], COSTS["P1"] * RTW["P1"],
             len(TR["P1"])),
            ("SHORT (mirrored fused)", SER["SHORT"], CM["SHORT"],
             COSTS["SHORT"] * RTW["SHORT"], len(TR["SHORT"])),
            ("P1 + SHORT (two sleeves)", ser_ps, cm_ps, cost_ps,
             len(TR["P1"]) + len(TR["SHORT"])),
            ("NETFUSE_1 (one object)", SER["NETFUSE_1"], CM["NETFUSE_1"],
             COSTS["NETFUSE_1"] * RTW["NETFUSE_1"], len(TR["NETFUSE_1"])),
            ("NETFUSE_Q (+quality size)", SER["NETFUSE_Q"], CM["NETFUSE_Q"],
             COSTS["NETFUSE_Q"] * RTW["NETFUSE_Q"], len(TR["NETFUSE_Q"]))):
        sc = tgt_cm / s_cm
        a = pan(s_ser * sc, ALL, s_cost * sc)
        P_(f"{lab:<24}{s_ntr:>8,}{sc:>7.2f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%"
           f"{a['streak']:>6}{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}{a['worst']:>10,.0f}"
           f"{a['weekly_dd']:>11,.0f}")
        rows.append(dict(obj=lab, trades=s_ntr, scale=sc, **a))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "netfuse.csv"), index=False)

    # H2
    scN = tgt_cm / CM["NETFUSE_1"]; scP = tgt_cm / cm_ps
    aN = pan(SER["NETFUSE_1"] * scN, ALL, COSTS["NETFUSE_1"] * RTW["NETFUSE_1"] * scN)
    aP = pan(ser_ps * scP, ALL, cost_ps * scP)
    P_("")
    P_("    H2: NETFUSE_1 vs P1+SHORT as two sleeves, matched contract-minutes")
    nwin = 0
    for nm, xa, xb, hi in (("weekly $ at fixed DD", aN["weekly_dd"], aP["weekly_dd"], True),
                           ("positive-week %", aN["wkpos"], aP["wkpos"], True),
                           ("raw mean top-5 DD", aN["top5"], aP["top5"], False)):
        winb = (xa > xb) if hi else (xa < xb)
        nwin += winb
        P_(f"      {nm:<24} NETFUSE {xa:>10,.1f}   two sleeves {xb:>10,.1f}   "
           f"{'NETFUSE' if winb else 'SLEEVES'}")
    P_(f"      -> NETFUSE wins {nwin}/3  =>  H2 {'PASSES' if nwin >= 2 else 'FAILS'}")

    # H3 recency
    P_("")
    P_("    H3: the only chronology gate")
    t24 = np.asarray(sdate >= pd.Timestamp("2024-08-01"))
    t12 = np.asarray(sdate >= pd.Timestamp("2025-08-01"))
    P_(f"{'object':<24}{'period':<7}{'weeks':>7}{'wk $':>10}{'SE':>9}{'t':>7}{'wk+%':>8}")
    for lab, s_ser, s_cm, s_cost in (
            ("NETFUSE_1", SER["NETFUSE_1"], CM["NETFUSE_1"],
             COSTS["NETFUSE_1"] * RTW["NETFUSE_1"]),
            ("NETFUSE_Q", SER["NETFUSE_Q"], CM["NETFUSE_Q"],
             COSTS["NETFUSE_Q"] * RTW["NETFUSE_Q"]),
            ("P1", SER["P1"], CM["P1"], COSTS["P1"] * RTW["P1"])):
        sc = tgt_cm / s_cm
        for pl, m in (("full", ALL), ("t24", t24), ("t12", t12)):
            a = pan(s_ser * sc, m, s_cost * sc)
            P_(f"{lab:<24}{pl:<7}{a['nwk']:>7}{a['weekly']:>10,.0f}{a['se']:>9,.0f}"
               f"{a['weekly']/max(a['se'],1e-9):>7.2f}{a['wkpos']:>7.1f}%")
        P_("")
    aN24 = pan(SER["NETFUSE_1"] * scN, t24, COSTS["NETFUSE_1"] * RTW["NETFUSE_1"] * scN)
    P_(f"    H3 (NETFUSE_1 t24 weekly > 0): {aN24['weekly']:,.0f} -> "
       f"{'PASS' if aN24['weekly'] > 0 else 'FAIL'}")

    P_("")
    P_(f"{'per-year wk $':<24}" + "".join(f"{y:>10}" for y in sorted(set(yr))))
    yr_rows = []
    for lab, s_ser, s_cm, s_cost in (
            ("NETFUSE_1", SER["NETFUSE_1"], CM["NETFUSE_1"],
             COSTS["NETFUSE_1"] * RTW["NETFUSE_1"]),
            ("NETFUSE_Q", SER["NETFUSE_Q"], CM["NETFUSE_Q"],
             COSTS["NETFUSE_Q"] * RTW["NETFUSE_Q"]),
            ("P1 + SHORT (sleeves)", ser_ps, cm_ps, cost_ps),
            ("P1", SER["P1"], CM["P1"], COSTS["P1"] * RTW["P1"])):
        sc = tgt_cm / s_cm
        line = f"{lab:<24}"
        for y in sorted(set(yr)):
            a = pan(s_ser * sc, yr == y, s_cost * sc)
            line += f"{a['weekly']:>10,.0f}"
            yr_rows.append(dict(obj=lab, year=int(y), weekly=a["weekly"], wkpos=a["wkpos"]))
        P_(line)
    pd.DataFrame(yr_rows).to_csv(os.path.join(OUT, "per_year.csv"), index=False)

    wks = {k: pd.Series(SER[k]).groupby(wk).sum() for k in
           ("NETFUSE_1", "P1", "X9a", "BMOM", "SHORT")}
    P_("")
    P_("    weekly rho of NETFUSE_1 against the library:")
    for k in ("P1", "X9a", "BMOM", "SHORT"):
        P_(f"      vs {k:<8} {float(np.corrcoef(wks['NETFUSE_1'], wks[k])[0,1]):>7.3f}")
    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"),
                  **{k: SER[k] for k in SER}}).to_csv(
        os.path.join(OUT, "series.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
