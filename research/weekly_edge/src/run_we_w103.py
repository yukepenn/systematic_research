"""WE_W103 - WHAT IS THE BASE, ACTUALLY? + what is STILL unmonetized.

Spec: runs/WE_W103_CONSOLIDATE/spec.yaml, committed BEFORE this ran.

Five components at the definitions that survived W97-W102c, the full weekly correlation matrix
printed BEFORE any combination, an inverse-volatility primary that cannot be tuned, an integer
grid reported as a plateau, and then W99b's SIGN_ORACLE ledger re-run against the winner.
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
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from run_we_w99 import SEGS, runs_of                                     # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W103_CONSOLIDATE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
ANCH, DEC, ENTM, EXITM = 571, 585, 586, 945      # TRUE RTH open anchor (W102c)
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
COMPS = ("P1_PCT", "X9a_PCT", "BMOM", "PAIR23", "XM_CONFLICT")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "consolidate.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    wk = wkall[sess_in]
    sp_tk = prof.reindex(mod).to_numpy()
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def net_series(tr):
        w_ = {}
        for x in tr:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts); m2 = p_.hour * 60 + p_.minute
                w_[m2] = w_.get(m2, 0.0) + x["u"]
        rate = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) / \
            max(sum(w_.values()), 1e-9)
        s_ = np.zeros(NSESS); ct = np.zeros(NSESS)
        for x in tr:
            si = int(sid[i_of(x["et"])])
            if win[si]:
                s_[si] += x["pnl"] - rate * x["u"]; ct[si] += x["u"]
        return s_, ct, rate, len(tr)

    def obj(chan):
        vl, _ = votes(D, mem, bmom, tilt, X, chan)
        p = vl.astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        sc, _ = causal_score(X, ee, window=WIN)
        return net_series(gfills(D, p, np.where(sc >= 3, 2, 1).astype(np.int8),
                                 **arm_kw("PCT", 1.183)))
    SER, CTR, RATE, NTR = {}, {}, {}, {}
    SER["P1_PCT"], CTR["P1_PCT"], RATE["P1_PCT"], NTR["P1_PCT"] = obj(bmom)
    SER["X9a_PCT"], CTR["X9a_PCT"], RATE["X9a_PCT"], NTR["X9a_PCT"] = \
        obj(CH["X9a_disp_sessanchor"])
    SER["BMOM"], CTR["BMOM"], RATE["BMOM"], NTR["BMOM"] = net_series(
        gfills(D, np.where(flatm, 0, bmom).astype(np.int8), None, **arm_kw("PCT", 1.0)))
    for k in ("SER", "CTR"):
        pass
    SER["PAIR23"] = (2 * SER["BMOM"] + 3 * SER["X9a_PCT"]) / 5.0
    CTR["PAIR23"] = (2 * CTR["BMOM"] + 3 * CTR["X9a_PCT"]) / 5.0
    RATE["PAIR23"] = np.nan; NTR["PAIR23"] = 2 * NTR["BMOM"] + 3 * NTR["X9a_PCT"]
    P_(f"    ratchet objects built  [{_time.time()-t0:.0f}s]")

    # ---- XM_CONFLICT at the CORRECTED anchor
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def at(mv, arr, uo=False):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_])
        return r
    pa, pdc, pe, px = at(ANCH, o, True), at(DEC, c), at(ENTM, o, True), at(EXITM, c)
    drive = np.sign(pdc - pa)
    acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
    for k in XM:
        a_, b_ = at(ANCH, XD[k]), at(DEC, XD[k])
        r_ = np.log(b_ / a_)
        s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        zz = r_ / np.maximum(s_, 1e-12)
        g = np.isfinite(zz); acc[g] += zz[g]; cnt[g] += 1
    xs = np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
    okm = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px) &
           np.isfinite(xs) & (drive != 0) & (xs != 0))
    cf = okm & (xs != drive)
    cstx = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITM])) / 2.0
    sxm = np.zeros(NSESS); ctx = np.zeros(NSESS)
    sxm[cf] = drive[cf] * (px[cf] - pe[cf]) * PV - cstx
    ctx[cf] = 1.0
    SER["XM_CONFLICT"], CTR["XM_CONFLICT"] = sxm, ctx
    RATE["XM_CONFLICT"] = cstx - COMM_RT; NTR["XM_CONFLICT"] = int(cf.sum())
    P_(f"    XM_CONFLICT (anchor {ANCH}=09:31 TRUE RTH open): {int(cf.sum()):,} trades, "
       f"${sxm[cf].mean():,.0f}/trade, hit {100*float((sxm[cf]+cstx>0).mean()):.1f} %")

    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wk).sum().to_numpy()
    WKS = {k: wkv(SER[k]) for k in COMPS}
    NW = len(WKS["P1_PCT"])

    def pan(w):
        dp = dd_profile(w)
        stk = max((len(list(g)) for k_, g in itertools.groupby(w < 0) if k_), default=0)
        cq = max(1, int(round(0.05 * len(w))))
        return dict(weekly=float(w.mean()), fixdd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((w > 0).mean()), maxdd=dp["maxdd"],
                    top5=dp["dd_mean_top5"], worst=float(w.min()),
                    cvar5=float(np.sort(w)[:cq].mean()), streak=int(stk),
                    t=float(w.mean()) / max(w.std(ddof=1) / np.sqrt(len(w)), 1e-9))

    # ============================================================ the correlation matrix FIRST
    P_("")
    P_("=" * 118)
    P_("=== THE WEEKLY CORRELATION MATRIX, printed BEFORE any combination is quoted.")
    P_("===   P1 CONTAINS bmom. X9a is the same object with one channel swapped and shares 13")
    P_("===   ratchet members with P1. PAIR23 is built from BMOM and X9a. These are not five")
    P_("===   information sources and the matrix is here so nobody reads them as five.")
    P_("=" * 118)
    P_(f"{'':14}" + "".join(f"{k:>13}" for k in COMPS))
    M = np.zeros((len(COMPS), len(COMPS)))
    for i_, a2 in enumerate(COMPS):
        line = f"{a2:<14}"
        for j_, b2 in enumerate(COMPS):
            r_ = float(np.corrcoef(WKS[a2], WKS[b2])[0, 1])
            M[i_, j_] = r_
            line += f"{r_:>13.3f}"
        P_(line)
    pd.DataFrame(M, index=list(COMPS), columns=list(COMPS)).to_csv(
        os.path.join(OUT, "corr_matrix.csv"))

    P_("")
    P_("=" * 118)
    P_("=== EACH COMPONENT ALONE (income is per 1 unit; the fixed-DD column is scale-invariant)")
    P_("=" * 118)
    P_(f"{'component':<14}{'trades':>8}{'$/ctrRT':>9}{'wk$':>9}{'wk$@fixDD':>11}{'wk+%':>7}"
       f"{'maxDD':>10}{'top5':>9}{'worst wk':>10}{'CVaR5':>9}{'strk':>6}{'t':>6}")
    srows = []
    for k in COMPS:
        a_ = pan(WKS[k])
        P_(f"{k:<14}{NTR[k]:>8,}{RATE[k]:>9.2f}{a_['weekly']:>9,.0f}{a_['fixdd']:>11,.0f}"
           f"{a_['poswk']:>6.1f}%{a_['maxdd']:>10,.0f}{a_['top5']:>9,.0f}{a_['worst']:>10,.0f}"
           f"{a_['cvar5']:>9,.0f}{a_['streak']:>6}{a_['t']:>6.2f}")
        srows.append(dict(component=k, trades=NTR[k], rate=RATE[k], **a_))
    pd.DataFrame(srows).to_csv(os.path.join(OUT, "components.csv"), index=False)

    # ============================================================ combinations
    P_("")
    P_("=" * 118)
    P_("=== COMBINATIONS. The PRIMARY is inverse-volatility equal risk - no free parameter.")
    P_("===   Everything else is a sensitivity plateau and NOTHING is adopted from an argmax.")
    P_("=" * 118)

    def comb(ws):
        """ws: dict component -> weight; series are scaled to income-match P1 in total"""
        tot = sum(ws[k] * WKS[k] for k in ws)
        return tot

    def show(name, ws):
        tot = comb(ws)
        a_ = pan(tot)
        P_(f"{name:<40}{a_['weekly']:>9,.0f}{a_['fixdd']:>11,.0f}{a_['poswk']:>7.1f}%"
           f"{a_['maxdd']:>10,.0f}{a_['top5']:>9,.0f}{a_['worst']:>10,.0f}{a_['cvar5']:>9,.0f}"
           f"{a_['streak']:>6}{a_['t']:>6.2f}")
        return dict(name=name, **a_, **{f"w_{k}": ws.get(k, 0.0) for k in COMPS})
    P_(f"{'combination':<40}{'wk$':>9}{'wk$@fixDD':>11}{'wk+%':>8}{'maxDD':>10}{'top5':>9}"
       f"{'worst wk':>10}{'CVaR5':>9}{'strk':>6}{'t':>6}")
    crows = []
    for k in COMPS:
        crows.append(show(f"{k} alone", {k: 1.0}))
    P_("")
    for tag, ks in (("INV-VOL: P1 + XM", ("P1_PCT", "XM_CONFLICT")),
                    ("INV-VOL: PAIR + XM", ("PAIR23", "XM_CONFLICT")),
                    ("INV-VOL: P1 + PAIR + XM", ("P1_PCT", "PAIR23", "XM_CONFLICT")),
                    ("INV-VOL: BMOM + X9a + XM", ("BMOM", "X9a_PCT", "XM_CONFLICT")),
                    ("INV-VOL: P1 + PAIR", ("P1_PCT", "PAIR23")),
                    ("INV-VOL: all five", COMPS)):
        sd_ = {k: 1.0 / max(WKS[k].std(ddof=1), 1e-9) for k in ks}
        tot_ = sum(sd_.values())
        crows.append(show(tag + "  *PRIMARY*" if tag == "INV-VOL: P1 + PAIR + XM" else tag,
                          {k: sd_[k] / tot_ for k in ks}))
    P_("")
    P_("    integer-ratio plateau, P1_PCT : PAIR23 : XM_CONFLICT (per unit, income-matched")
    P_("    inside each component). REPORTED AS A SHAPE - the argmax is NOT adopted.")
    P_(f"{'ratio':<40}{'wk$':>9}{'wk$@fixDD':>11}{'wk+%':>8}{'maxDD':>10}{'top5':>9}"
       f"{'worst wk':>10}{'CVaR5':>9}{'strk':>6}{'t':>6}")
    # normalise each component to the same weekly income first, then apply integer ratios
    inc = {k: WKS[k].mean() for k in COMPS}
    NRM = {k: WKS[k] * (inc["P1_PCT"] / inc[k]) if inc[k] else WKS[k] * 0 for k in COMPS}
    grows = []
    for a2 in (0, 1, 2, 3):
        for b2 in (0, 1, 2, 3):
            for c2 in (0, 1, 2, 3):
                if a2 + b2 + c2 == 0:
                    continue
                tot = (a2 * NRM["P1_PCT"] + b2 * NRM["PAIR23"] + c2 * NRM["XM_CONFLICT"])
                a_ = pan(tot)
                grows.append(dict(p1=a2, pair=b2, xm=c2, **a_))
    G = pd.DataFrame(grows).sort_values("fixdd", ascending=False)
    G.to_csv(os.path.join(OUT, "ratio_grid.csv"), index=False)
    for _, r_ in G.head(8).iterrows():
        P_(f"{f'{int(r_.p1)} P1 : {int(r_.pair)} PAIR : {int(r_.xm)} XM':<40}"
           f"{r_['weekly']:>9,.0f}{r_['fixdd']:>11,.0f}{r_['poswk']:>7.1f}%{r_['maxdd']:>10,.0f}"
           f"{r_['top5']:>9,.0f}{r_['worst']:>10,.0f}{r_['cvar5']:>9,.0f}{int(r_['streak']):>6}"
           f"{r_['t']:>6.2f}")
    P_(f"    ... {len(G)} cells; the top-8 span wk$@fixDD "
       f"{G['fixdd'].head(8).min():,.0f} to {G['fixdd'].head(8).max():,.0f} "
       f"({100*(G['fixdd'].head(8).max()/max(G['fixdd'].head(8).min(),1e-9)-1):.1f} % apart) - "
       f"a {'BROAD' if G['fixdd'].head(8).max()/max(G['fixdd'].head(8).min(),1e-9) < 1.15 else 'NARROW'} plateau")
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "combinations.csv"), index=False)

    # ============================================================ the chosen base + recency
    sd_ = {k: 1.0 / max(WKS[k].std(ddof=1), 1e-9) for k in ("P1_PCT", "PAIR23", "XM_CONFLICT")}
    tw = sum(sd_.values())
    Wsel = {k: sd_[k] / tw for k in sd_}
    BASE = sum(Wsel[k] * SER[k] for k in Wsel)
    P_("")
    P_("=" * 118)
    P_("=== THE PRIMARY COMBINATION, per year and recency (t6m/t3m are BURNED)")
    P_(f"===   weights {', '.join(f'{k} {Wsel[k]:.3f}' for k in Wsel)}")
    P_("=" * 118)
    sdv = sdate.to_numpy()[sess_in]
    P_(f"{'window':<10}{'sess':>6}{'wk$':>9}{'wk$@fixDD':>11}{'wk+%':>8}{'day+%':>8}"
       f"{'maxDD':>10}{'top5':>9}{'worst wk':>10}{'strk':>6}{'t':>6}")
    wrows = []
    for wn, x_, y_ in (("FULL", "2022-07-01", "2026-08-01"), ("2024+", "2024-01-01", "2026-08-01"),
                       ("2025", "2025-01-01", "2026-01-01"),
                       ("2026YTD", "2026-01-01", "2026-08-01"),
                       ("t12m", "2025-08-01", "2026-08-01"), ("t6m", "2026-02-01", "2026-08-01"),
                       ("t3m", "2026-05-01", "2026-08-01")):
        m = (sdv >= np.datetime64(x_)) & (sdv < np.datetime64(y_))
        w_ = pd.Series(BASE[sess_in][m]).groupby(wk[m]).sum().to_numpy()
        a_ = pan(w_)
        P_(f"{wn:<10}{int(m.sum()):>6}{a_['weekly']:>9,.0f}{a_['fixdd']:>11,.0f}"
           f"{a_['poswk']:>7.1f}%{100*float((BASE[sess_in][m]>0).mean()):>7.1f}%"
           f"{a_['maxdd']:>10,.0f}{a_['top5']:>9,.0f}{a_['worst']:>10,.0f}{a_['streak']:>6}"
           f"{a_['t']:>6.2f}")
        wrows.append(dict(window=wn, sessions=int(m.sum()), **a_))
    pd.DataFrame(wrows).to_csv(os.path.join(OUT, "base_recency.csv"), index=False)

    # ============================================================ capture ledger v3
    P_("")
    P_("=" * 118)
    P_("=== CAPTURE LEDGER v3 (TASK 13): what is STILL unmonetized, against the BASE")
    P_("=" * 118)
    seg = np.full(n, -1, np.int8)
    for k_, (nm, a2, b2) in enumerate(SEGS):
        seg[(mod >= a2) & (mod < b2)] = k_
    gkey = sid.astype(np.int64) * 16 + seg
    gs, ge = runs_of(gkey)
    G_ = len(gs); g_sess = sid[gs]; g_seg = seg[gs]
    gm = win[g_sess]
    NS = len(sess_in)
    seg_open = o[gs]
    seg_close = np.array([c[e - 1] for e in ge])
    net_g = seg_close - seg_open
    rt_cost = COMM_RT + TICKV * (sp_tk[gs] + np.array([sp_tk[e - 1] for e in ge])) / 2.0
    # attribute the base's money to the entry segment of each sleeve
    gpos = {int(k_): i for i, k_ in enumerate(gkey[gs])}
    ours = np.zeros(G_)
    for k_ in ("P1_PCT", "X9a_PCT", "BMOM"):
        pass
    # rebuild the trade lists once more to attribute by entry bar

    def attribute(tr, wgt, rate):
        for x in tr:
            i_ = i_of(x["et"])
            if win[int(sid[i_])]:
                ours[gpos[int(gkey[i_])]] += wgt * (x["pnl"] - rate * x["u"])
    vlP, _ = votes(D, mem, bmom, tilt, X, bmom)
    pP = vlP.astype(np.int8)
    bbP = fills_daily(D, pP, halt=1300, target=1000)
    eeP = np.array([i_of(x["et"]) for x in bbP if A <= np.datetime64(x["et"]) < B])
    scP, _ = causal_score(X, eeP, window=WIN)
    trP = gfills(D, pP, np.where(scP >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
    vlX, _ = votes(D, mem, bmom, tilt, X, CH["X9a_disp_sessanchor"])
    pX = vlX.astype(np.int8)
    bbX = fills_daily(D, pX, halt=1300, target=1000)
    eeX = np.array([i_of(x["et"]) for x in bbX if A <= np.datetime64(x["et"]) < B])
    scX, _ = causal_score(X, eeX, window=WIN)
    trX = gfills(D, pX, np.where(scX >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
    trB = gfills(D, np.where(flatm, 0, bmom).astype(np.int8), None, **arm_kw("PCT", 1.0))
    attribute(trP, Wsel["P1_PCT"], RATE["P1_PCT"])
    attribute(trX, Wsel["PAIR23"] * 3.0 / 5.0, RATE["X9a_PCT"])
    attribute(trB, Wsel["PAIR23"] * 2.0 / 5.0, RATE["BMOM"])
    for s_ in np.flatnonzero(cf):
        i_ = int(np.flatnonzero((mod == ENTM) & (sid == s_))[0])
        ours[gpos[int(gkey[i_])]] += Wsel["XM_CONFLICT"] * sxm[s_]
    P_(f"{'segment':<10}{'SIGN_ORC $':>12}{'p*':>8}{'P1 alone':>11}{'BASE':>9}"
       f"{'residual':>11}{'covered':>10}")
    frows = []
    # P1-alone attribution for the comparison column
    oursP = np.zeros(G_)
    for x in trP:
        i_ = i_of(x["et"])
        if win[int(sid[i_])]:
            oursP[gpos[int(gkey[i_])]] += x["pnl"] - RATE["P1_PCT"] * x["u"]
    for k_, (nm, a2, b2) in enumerate(SEGS):
        m = gm & (g_seg == k_)
        em = float(np.abs(net_g[m]).mean()) * PV
        cst = float(rt_cost[m].mean())
        so = float((np.abs(net_g[m]) * PV - rt_cost[m]).sum() / NS)
        ou = ours[m].sum() / NS
        op = oursP[m].sum() / NS
        P_(f"{nm:<10}{so:>12,.0f}{0.5*(1+cst/em):>8.4f}{op:>11,.0f}{ou:>9,.0f}"
           f"{so-ou:>11,.0f}{100*ou/so if so else np.nan:>9.1f}%")
        frows.append(dict(segment=nm, sign_oracle=so, p_star=0.5 * (1 + cst / em),
                          p1_alone=op, base=ou, residual=so - ou))
    pd.DataFrame(frows).to_csv(os.path.join(OUT, "ledger_v3_segment.csv"), index=False)
    P_("")
    kl_g = klass[g_sess]
    P_(f"{'class':<12}{'share':>8}{'SIGN_ORC $':>12}{'p*':>8}{'P1 alone':>11}{'BASE':>9}"
       f"{'residual':>11}")
    krows = []
    for kk in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        m = gm & (kl_g == kk)
        nsk = len(set(g_sess[m]))
        em = float(np.abs(net_g[m]).mean()) * PV
        cst = float(rt_cost[m].mean())
        so = float((np.abs(net_g[m]) * PV - rt_cost[m]).sum() / nsk)
        P_(f"{kk:<12}{100*nsk/NS:>7.1f}%{so:>12,.0f}{0.5*(1+cst/em):>8.4f}"
           f"{oursP[m].sum()/nsk:>11,.0f}{ours[m].sum()/nsk:>9,.0f}"
           f"{so-ours[m].sum()/nsk:>11,.0f}")
        krows.append(dict(klass=kk, n=nsk, sign_oracle=so, p1_alone=oursP[m].sum() / nsk,
                          base=ours[m].sum() / nsk, residual=so - ours[m].sum() / nsk))
    pd.DataFrame(krows).to_csv(os.path.join(OUT, "ledger_v3_class.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
