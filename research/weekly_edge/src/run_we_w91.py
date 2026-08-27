"""WE_W91 - FUSION vs INDEPENDENT RISK BUDGETS.

Spec: runs/WE_W91_FUSEVSPORT/spec.yaml, committed BEFORE this ran.

P1 is a Solar ensemble OR-GATED with B-MOM (W67). A portfolio of {Solar alone, B-MOM traded
directly} uses exactly the same two ingredients and nothing else. Any difference between them is
attributable to the COMBINER, which is what makes the owner's mechanism hypothesis testable
rather than another object comparison.
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
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W91_FUSEVSPORT", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
COST = {"SOLAR": 14.52, "P1": 14.52, "X9a": 14.55, "BMOM_std": 12.99, "BMOM_L_std": 12.99}
COMM_RT = 4.36


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fuse.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}
    bm = np.where(flatm, 0, bmom).astype(np.int8)

    st = np.zeros(D["n_sess"], np.int64)
    st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    yr = sdate.year.to_numpy()
    NWk = len(set(wk))
    P_(f"=== {len(sess_in)} sessions / {NWk} weeks [{_time.time()-t0:.0f}s]")

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

    def vote_(TGx):
        vs = []
        for m_ in MEMBERS:
            tg = TGx[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & X["dL"] if dg else okv
                    vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)

    def long_obj(TGx):
        p = (vote_(TGx) >= 0.5).astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return [x for x in fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_)
                if in_win[int(sid[i_of(x["et"])])]]

    def keep(trl):
        return [x for x in trl if in_win[int(sid[i_of(x["et"])])]]

    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    TR = {}
    TR["SOLAR"] = long_obj(TG_for(np.zeros(n, np.int8)))
    TR["P1"] = long_obj(TG_for(bmom))
    TR["X9a"] = long_obj(TG_for(CH["X9a_disp_sessanchor"]))
    TR["BMOM_std"] = keep(sfills(D, bm, halt=1300.0, target=1000.0))
    TR["BMOM_L_std"] = keep(sfills(D, np.where(bm > 0, 1, 0).astype(np.int8),
                                   halt=1300.0, target=1000.0))
    P_(f"    five trade lists built [{_time.time()-t0:.0f}s]")

    # ---------------------------------------------------------------- series + occupancy
    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def occ_signed(trl):
        o = np.zeros(n)
        for x in trl:
            o[i_of(x["et"]):i_of(x["xt"])] += x["d"] * x["u"]
        return o

    SER = {k: daily(v) for k, v in TR.items()}
    OCC = {k: occ_signed(v) for k, v in TR.items()}
    RTW = {k: sum(x["u"] for x in v) / NWk for k, v in TR.items()}
    CM = {k: float(np.abs(OCC[k]).sum()) for k in TR}            # contract-minutes
    inw = np.array([in_win[s] for s in sid])

    P_("")
    P_(f"{'object':<12}{'trades':>8}{'ctrRT/wk':>10}{'ctr-min':>12}{'net $':>13}"
       f"{'pts/sess':>10}")
    for k in TR:
        pts = sum(x["pnl"] + COMM_RT * x["u"] for x in TR[k]) / PV / len(sess_in)
        P_(f"{k:<12}{len(TR[k]):>8,}{RTW[k]:>10.2f}{CM[k]:>12,.0f}"
           f"{SER[k].sum():>13,.0f}{pts:>10.2f}")
    P_("    (pts/session is gross of commission, the unit W67 used: Solar alone = 7.26)")

    # ---------------------------------------------------------------- the panel
    def pan(v, msk, cost_wk):
        w = pd.Series(v[msk]).groupby(wk[msk]).sum().to_numpy() - cost_wk
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    eff=float(w.mean()) / max(abs(float(w.min())), 1e-9))
    ALL = np.ones(len(sess_in), bool)

    # ---------------------------------------------------------------- portfolios
    # matched in CONTRACT-MINUTES to P1 (repo rule N1 != N2, exposure-matched)
    def blend(parts):
        """parts = [(name, weight)] -> (daily series, cost/week, contract-minutes, occ)"""
        v = sum(w_ * SER[k] for k, w_ in parts)
        c = sum(w_ * COST[k] * RTW[k] for k, w_ in parts)
        cm = sum(w_ * CM[k] for k, w_ in parts)
        oc = sum(w_ * OCC[k] for k, w_ in parts)
        return v, c, cm, oc

    def scale_to(parts, target_cm):
        _, _, cm, _ = blend(parts)
        return target_cm / cm

    tgt_cm = CM["P1"]
    PORT = {
        "PORT_SB  (Solar+BMOM)": [("SOLAR", .5), ("BMOM_std", .5)],
        "PORT_SBL (Solar+BMOM_L)": [("SOLAR", .5), ("BMOM_L_std", .5)],
        "PORT_XB  (X9a+BMOM 2:3)": [("X9a", .6), ("BMOM_std", .4)],
    }
    P_("")
    P_("=" * 122)
    P_("=== PHASE 1: FUSED vs PORTFOLIO, matched in CONTRACT-MINUTES to P1")
    P_("=" * 122)
    P_(f"{'object':<26}{'scale':>7}{'wk $':>9}{'wk+%':>8}{'strk':>6}{'maxDD':>10}"
       f"{'top5DD':>9}{'worst':>10}{'wk$@fixDD':>11}{'eff':>8}")
    rows = []
    base = {}
    for k in ("SOLAR", "P1", "X9a", "BMOM_std"):
        s = tgt_cm / CM[k]
        a = pan(SER[k] * s, ALL, COST[k] * RTW[k] * s)
        base[k] = a
        P_(f"{k:<26}{s:>7.2f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['streak']:>6}"
           f"{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}{a['worst']:>10,.0f}"
           f"{a['weekly_dd']:>11,.0f}{a['eff']:>8.3f}")
        rows.append(dict(obj=k, kind="single", scale=s, **a))
    P_("")
    for nm, parts in PORT.items():
        s = scale_to(parts, tgt_cm)
        v, c, cm, oc = blend(parts)
        a = pan(v * s, ALL, c * s)
        P_(f"{nm:<26}{s:>7.2f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['streak']:>6}"
           f"{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}{a['worst']:>10,.0f}"
           f"{a['weekly_dd']:>11,.0f}{a['eff']:>8.3f}")
        rows.append(dict(obj=nm, kind="portfolio", scale=s, **a))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "fuse_vs_port.csv"), index=False)

    # the decision: PORT_SB vs P1 on the three gate legs
    sSB = scale_to(PORT["PORT_SB  (Solar+BMOM)"], tgt_cm)
    vSB, cSB, _, _ = blend(PORT["PORT_SB  (Solar+BMOM)"])
    aSB = pan(vSB * sSB, ALL, cSB * sSB); aP1 = base["P1"]
    legs = [("weekly $ at fixed DD", aSB["weekly_dd"], aP1["weekly_dd"], True),
            ("positive-week %", aSB["wkpos"], aP1["wkpos"], True),
            ("raw mean top-5 DD", aSB["top5"], aP1["top5"], False)]
    nwin = 0
    P_("")
    P_("    THE DECISION RULE: PORT_SB vs P1, same two ingredients, matched contract-minutes")
    for nm2, xa, xb, hi in legs:
        winb = (xa > xb) if hi else (xa < xb)
        nwin += winb
        P_(f"      {nm2:<24} portfolio {xa:>10,.1f}   fused {xb:>10,.1f}   "
           f"{'PORTFOLIO' if winb else 'FUSED'}")
    P_(f"      -> portfolio wins {nwin}/3  =>  owner's hypothesis "
       f"{'SUPPORTED' if nwin >= 2 else 'FALSIFIED for the Solar/BMOM pair'}")

    # ============================================================ E_b: timing / overlap
    P_("")
    P_("=" * 122)
    P_("=== PHASE 2: E_b - ENTRY TIMING AND OVERLAP (the owner's named measurements)")
    P_("=" * 122)

    def sess_of(trl):
        return set(int(sid[i_of(x["et"])]) for x in trl)

    PAIRS = [("SOLAR", "BMOM_std"), ("X9a", "BMOM_std"), ("SOLAR", "X9a"), ("P1", "BMOM_std")]
    P_(f"{'pair':<22}{'both-sess %':>13}{'minute Jaccard':>16}{'A solo %':>10}{'B solo %':>10}"
       f"{'OPPOSED %':>11}")
    orows = []
    for a_, b_ in PAIRS:
        sa, sb = sess_of(TR[a_]), sess_of(TR[b_])
        both = len(sa & sb) / max(len(sa | sb), 1)
        oa = OCC[a_][inw]; ob = OCC[b_][inw]
        ina, inb = oa != 0, ob != 0
        jac = (ina & inb).sum() / max((ina | inb).sum(), 1)
        solo_a = (ina & ~inb).sum() / max(ina.sum(), 1)
        solo_b = (inb & ~ina).sum() / max(inb.sum(), 1)
        opp = ((oa * ob) < 0).sum() / max((ina & inb).sum(), 1)
        P_(f"{a_+' / '+b_:<22}{100*both:>12.1f}%{100*jac:>15.1f}%{100*solo_a:>9.1f}%"
           f"{100*solo_b:>9.1f}%{100*opp:>10.1f}%")
        orows.append(dict(a=a_, b=b_, both_sess=100 * both, minute_jaccard=100 * jac,
                          a_solo=100 * solo_a, b_solo=100 * solo_b, opposed=100 * opp))
    pd.DataFrame(orows).to_csv(os.path.join(OUT, "overlap.csv"), index=False)
    P_("    'OPPOSED %' is the share of SHARED minutes in which the two hold opposite signs -")
    P_("    the minutes a single netted brokerage account would cross internally. PHASE 5.")

    P_("")
    P_(f"    entry minute-of-day, median and IQR:")
    for k in TR:
        m = np.array([pd.Timestamp(x["et"]).hour * 60 + pd.Timestamp(x["et"]).minute
                      for x in TR[k]])
        P_(f"      {k:<12} median {int(np.median(m))//60:02d}:{int(np.median(m))%60:02d}   "
           f"IQR {int(np.percentile(m,25))//60:02d}:{int(np.percentile(m,25))%60:02d} - "
           f"{int(np.percentile(m,75))//60:02d}:{int(np.percentile(m,75))%60:02d}   "
           f"RTH share {100*np.mean((m>=570)&(m<960)):.1f} %")

    # ============================================================ E_c: the short leg
    P_("")
    P_("=" * 122)
    P_("=== PHASE 3: E_c - IS THE PORTFOLIO'S ADVANTAGE THE DISCARDED SHORT LEG?")
    P_("=" * 122)
    sSBL = scale_to(PORT["PORT_SBL (Solar+BMOM_L)"], tgt_cm)
    vSBL, cSBL, _, _ = blend(PORT["PORT_SBL (Solar+BMOM_L)"])
    aSBL = pan(vSBL * sSBL, ALL, cSBL * sSBL)
    P_(f"{'':<26}{'wk $':>9}{'wk+%':>8}{'top5DD':>10}{'wk$@fixDD':>11}{'worst':>10}")
    for nm2, a in (("P1 (fused, long-only)", aP1), ("PORT_SBL (long-only BMOM)", aSBL),
                   ("PORT_SB  (both sides)", aSB)):
        P_(f"{nm2:<26}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['top5']:>10,.0f}"
           f"{a['weekly_dd']:>11,.0f}{a['worst']:>10,.0f}")
    P_("")
    P_("    E_c isolated = PORT_SB minus PORT_SBL (the ONLY difference is B-MOM's short leg):")
    P_(f"      weekly $ at fixed DD  {aSB['weekly_dd']-aSBL['weekly_dd']:>+10,.1f}")
    P_(f"      positive-week %       {aSB['wkpos']-aSBL['wkpos']:>+10.2f}")
    P_(f"      raw mean top-5 DD     {aSB['top5']-aSBL['top5']:>+10,.0f}  (negative = better)")
    P_("    Combiner effect  = PORT_SBL minus P1 (both long-only; the ONLY difference is fusion):")
    P_(f"      weekly $ at fixed DD  {aSBL['weekly_dd']-aP1['weekly_dd']:>+10,.1f}")
    P_(f"      positive-week %       {aSBL['wkpos']-aP1['wkpos']:>+10.2f}")
    P_(f"      raw mean top-5 DD     {aSBL['top5']-aP1['top5']:>+10,.0f}  (negative = better)")

    # ============================================================ E_a: the box
    P_("")
    P_("=" * 122)
    P_("=== PHASE 4: E_a - IS IT THE TWO INDEPENDENT RISK BUDGETS?")
    P_("=" * 122)
    P_("    TWO BUDGETS = each sleeve carries its own box (the incumbent portfolio form).")
    P_("    ONE BUDGET  = the sleeves are RE-SIMULATED WITH NO BOX AT ALL, and a single")
    P_("                  portfolio-level box is applied to the combined stream.")
    P_("    A first draft of this phase layered an EXTRA box on top of the per-sleeve boxes,")
    P_("    which tests 'three budgets', not 'one'. That draft is discarded, not reported.")
    NOBOX = 1e15

    def nobox_trades(k):
        if k == "SOLAR":
            return long_obj_nobox(np.zeros(n, np.int8))
        if k == "X9a":
            return long_obj_nobox(CH["X9a_disp_sessanchor"])
        if k == "BMOM_std":
            return keep(sfills(D, bm, halt=NOBOX, target=None))
        if k == "BMOM_L_std":
            return keep(sfills(D, np.where(bm > 0, 1, 0).astype(np.int8),
                               halt=NOBOX, target=None))
        raise KeyError(k)

    def long_obj_nobox(chan):
        TGx = TG_for(chan)
        p = (vote_(TGx) >= 0.5).astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return [x for x in fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_,
                                       halt=NOBOX, target=None)
                if in_win[int(sid[i_of(x["et"])])]]

    def one_budget(parts, halt=1300.0, target=1000.0):
        """Sleeves with NO box, one shared session box on the combined stream."""
        ev = []
        for k, w_ in parts:
            for x in NB[k]:
                ev.append((i_of(x["xt"]), w_ * x["pnl"]))
        ev.sort()
        sp = np.zeros(D["n_sess"]); spnl = 0.0; cur = -1; stopped = False
        for i, p in ev:
            s = int(sid[i])
            if s != cur:
                cur = s; spnl = 0.0; stopped = False
            if stopped:
                continue
            sp[s] += p; spnl += p
            if spnl <= -halt or spnl >= target:
                stopped = True
        return sp[sess_in]

    NB = {k: nobox_trades(k) for k in ("SOLAR", "X9a", "BMOM_std", "BMOM_L_std")}
    NBCM = {k: float(np.abs(occ_signed(v)).sum()) for k, v in NB.items()}
    NBRT = {k: sum(x["u"] for x in v) / NWk for k, v in NB.items()}
    P_("")
    P_(f"    box-free sleeve rebuild: " + "  ".join(
        f"{k} {len(NB[k]):,} tr" for k in NB))
    for nm2, parts in (("PORT_SB", PORT["PORT_SB  (Solar+BMOM)"]),
                       ("PORT_XB", PORT["PORT_XB  (X9a+BMOM 2:3)"])):
        s = scale_to(parts, tgt_cm)
        v2, c2, _, _ = blend(parts)
        a_two = pan(v2 * s, ALL, c2 * s)
        cm1 = sum(w_ * NBCM[k] for k, w_ in parts)
        s1 = tgt_cm / cm1
        c1 = sum(w_ * COST[k] * NBRT[k] for k, w_ in parts)
        a_one = pan(one_budget(parts) * s1, ALL, c1 * s1)
        a_none = pan(sum(w_ * daily(NB[k]) for k, w_ in parts) * s1, ALL, c1 * s1)
        P_(f"\n    {nm2}")
        P_(f"{'':<26}{'wk $':>9}{'wk+%':>8}{'top5DD':>10}{'wk$@fixDD':>11}{'worst':>10}")
        P_(f"{'      TWO budgets':<26}{a_two['weekly']:>9,.0f}{a_two['wkpos']:>7.1f}%"
           f"{a_two['top5']:>10,.0f}{a_two['weekly_dd']:>11,.0f}{a_two['worst']:>10,.0f}")
        P_(f"{'      ONE budget':<26}{a_one['weekly']:>9,.0f}{a_one['wkpos']:>7.1f}%"
           f"{a_one['top5']:>10,.0f}{a_one['weekly_dd']:>11,.0f}{a_one['worst']:>10,.0f}")
        P_(f"{'      NO budget (control)':<26}{a_none['weekly']:>9,.0f}{a_none['wkpos']:>7.1f}%"
           f"{a_none['top5']:>10,.0f}{a_none['weekly_dd']:>11,.0f}{a_none['worst']:>10,.0f}")
        if nm2 == "PORT_SB":
            P_(f"{'      vs FUSED P1':<26}{aP1['weekly']:>9,.0f}{aP1['wkpos']:>7.1f}%"
               f"{aP1['top5']:>10,.0f}{aP1['weekly_dd']:>11,.0f}{aP1['worst']:>10,.0f}")

    # ---------------------------------------------------------------- weight sensitivity
    P_("")
    P_("    weight sensitivity for PORT_SB - reported for SHAPE only. No weight is selected on")
    P_("    the outcome; a best-of-K choice would need a family-wise null (repo rule, W53).")
    P_(f"{'w_BMOM':>8}{'wk $':>9}{'wk+%':>8}{'top5DD':>10}{'wk$@fixDD':>11}")
    for wb in (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        parts = [("SOLAR", 1 - wb), ("BMOM_std", wb)]
        s = scale_to(parts, tgt_cm) if wb not in (0.0, 1.0) else \
            tgt_cm / (CM["SOLAR"] if wb == 0 else CM["BMOM_std"])
        v2, c2, _, _ = blend(parts)
        a = pan(v2 * s, ALL, c2 * s)
        P_(f"{wb:>8.1f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['top5']:>10,.0f}"
           f"{a['weekly_dd']:>11,.0f}")

    # ============================================================ correlations + regime
    P_("")
    P_("=" * 122)
    P_("=== PHASE 5: weekly rho, underwater rho, per-year")
    P_("=" * 122)
    WKS = {k: pd.Series(SER[k]).groupby(wk).sum() for k in TR}

    def uw(k):
        w = WKS[k].to_numpy() - COST[k] * RTW[k]
        c = np.cumsum(w)
        return np.maximum.accumulate(c) - c
    names = list(TR)
    P_(f"{'weekly rho':<14}" + "".join(f"{k:>12}" for k in names))
    crows = []
    for a_ in names:
        line = f"{a_:<14}"
        for b_ in names:
            r = float(np.corrcoef(WKS[a_], WKS[b_])[0, 1]); line += f"{r:>12.3f}"
            crows.append(dict(a=a_, b=b_, weekly=r,
                              underwater=float(np.corrcoef(uw(a_), uw(b_))[0, 1])))
        P_(line)
    P_("")
    P_(f"{'underwater rho':<14}" + "".join(f"{k:>12}" for k in names))
    for a_ in names:
        P_(f"{a_:<14}" + "".join(
            f"{float(np.corrcoef(uw(a_), uw(b_))[0,1]):>12.3f}" for b_ in names))
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "rho.csv"), index=False)

    P_("")
    P_(f"{'per-year wk $':<26}" + "".join(f"{y:>10}" for y in sorted(set(yr))))
    yrows = []
    for k in TR:
        s = tgt_cm / CM[k]
        line = f"{k:<26}"
        for y in sorted(set(yr)):
            a = pan(SER[k] * s, yr == y, COST[k] * RTW[k] * s)
            line += f"{a['weekly']:>10,.0f}"
            yrows.append(dict(obj=k, year=int(y), weekly=a["weekly"], wkpos=a["wkpos"]))
        P_(line)
    for nm2, parts in PORT.items():
        s = scale_to(parts, tgt_cm)
        v2, c2, _, _ = blend(parts)
        line = f"{nm2:<26}"
        for y in sorted(set(yr)):
            a = pan(v2 * s, yr == y, c2 * s)
            line += f"{a['weekly']:>10,.0f}"
            yrows.append(dict(obj=nm2, year=int(y), weekly=a["weekly"], wkpos=a["wkpos"]))
        P_(line)
    pd.DataFrame(yrows).to_csv(os.path.join(OUT, "per_year.csv"), index=False)
    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"), **SER}).to_csv(
        os.path.join(OUT, "series.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
