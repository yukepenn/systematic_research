"""WE_W98 - SHOULD THE SESSION RISK BUDGET SCALE WITH POSITION SIZE?

Spec: runs/WE_W98_BOXDENOM/spec.yaml, committed BEFORE this ran.

W97/M8: the session box is a DOLLAR limit on TOTAL position P&L, so a size-2 entry trips the
-$1,300 halt at 32.28 points instead of 64.78. P1 runs size 2 on 18.3 % of trades.

Five arms, differing ONLY in the accumulator of the session box:
    ABS        spnl += pnl                      halt -1300   target +1000      (incumbent)
    PCT        spnl += pnl/u                    halt -1300   target +1000      (hypothesis)
    ABS_LOOSE  spnl += pnl                      halt -1300k  target +1000k     (the null for PCT)
    PCT_MATCH  spnl += pnl/u                    halt -1300/k target +1000/k    (control)
    NOBOX      no halt, no target
k is each object's OWN mean contracts per trade, so ABS_LOOSE raises the average dollar budget by
exactly the same factor PCT does.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time
from collections import defaultdict
from math import erf, sqrt

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
from run_we_w97 import votes                                             # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W98_BOXDENOM", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
INF = float("inf")

ARMS = ("ABS", "PCT", "ABS_LOOSE", "PCT_MATCH", "NOBOX")


def gfills(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, per_ctr=False):
    """sfills with ONE switch: whether the session box accumulates total or per-contract P&L.
    At per_ctr=False and size 1 this is sfills verbatim (asserted in H-A/H-B)."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
    return trades


def arm_kw(arm, k):
    if arm == "ABS":
        return dict(halt=1300.0, target=1000.0, per_ctr=False)
    if arm == "PCT":
        return dict(halt=1300.0, target=1000.0, per_ctr=True)
    if arm == "ABS_LOOSE":
        return dict(halt=1300.0 * k, target=1000.0 * k, per_ctr=False)
    if arm == "PCT_MATCH":
        return dict(halt=1300.0 / k, target=1000.0 / k, per_ctr=True)
    if arm == "NOBOX":
        return dict(halt=INF, target=None, per_ctr=False)
    raise KeyError(arm)


def same(a, b):
    """byte-identity of two trade lists"""
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x["d"] != y["d"] or x["u"] != y["u"] or x["et"] != y["et"] or x["xt"] != y["xt"]:
            return False
        if abs(x["pnl"] - y["pnl"]) > 1e-9:
            return False
    return True


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "boxdenom.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]

    # ================================================================= substrate
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")
    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    P_(f"    substrate {n:,} bars / {D['n_sess']:,} sessions, window {len(sess_in):,} sessions "
       f"{sdate.min().date()} -> {sdate.max().date()}  [{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    # ================================================================= frozen causal scores
    P_("")
    P_("=" * 122)
    P_("=== SIGNALS: votes built ONCE per channel; the causal quality score is FROZEN from the")
    P_("===          incumbent SIZE-1 entry schedule, where the two denominators coincide.")
    P_("=" * 122)
    SIG = {}
    for nm, chan in (("P1", bmom), ("X9a", CH["X9a_disp_sessanchor"])):
        vl, _ = votes(D, mem, bmom, tilt, X, chan)
        p = vl.astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        SIG[nm] = dict(pos=p, sz=np.where(s_ >= 3, 2, 1).astype(np.int8), sc=s_)
        P_(f"    {nm:<6} long-target bars {int(p.sum()):>9,}   size-2 bars {int((s_>=3).sum()):>9,}"
           f"   [{_time.time()-t0:.0f}s]")
    vl2, vs2 = votes(D, mem, bmom, tilt, X, bmom)
    tgtN = np.where(vl2 & vs2, 0, np.where(vl2, 1, np.where(vs2, -1, 0))).astype(np.int8)
    bbN = fills_daily(D, np.abs(tgtN).astype(np.int8), halt=1300, target=1000)
    eeN = np.array([i_of(x["et"]) for x in bbN if A <= np.datetime64(x["et"]) < B])
    scN, _ = causal_score(X, eeN, window=WIN)
    szN = np.where((tgtN > 0) & (scN >= 3), 2, 1).astype(np.int8)
    bm_dir = np.where(flatm, 0, bmom).astype(np.int8)
    P_(f"    NETFUSE signed target built; long {int((tgtN>0).sum()):,} short "
       f"{int((tgtN<0).sum()):,}  [{_time.time()-t0:.0f}s]")

    # object -> (dir_arr, size_arr or None)
    OBJ = {
        "P1":        (SIG["P1"]["pos"], SIG["P1"]["sz"]),
        "X9a":       (SIG["X9a"]["pos"], SIG["X9a"]["sz"]),
        "BMOM":      (bm_dir, None),
        "NETFUSE_1": (tgtN, None),
        "NETFUSE_Q": (tgtN, szN),
    }

    # ================================================================= B1 harness checks
    P_("")
    P_("=" * 122)
    P_("=== B1 HARNESS CHECKS - printed before any arm is read. Any failure stops the wave.")
    P_("=" * 122)
    ok = True
    ha = same(gfills(D, bm_dir, None, 1300.0, 1000.0, False),
              sfills(D, bm_dir, halt=1300.0, target=1000.0))
    P_(f"    H-A  gfills(per_ctr=False) == sfills, byte for byte .................. "
       f"{'PASS' if ha else 'FAIL'}")
    ok &= ha
    tb_abs = gfills(D, bm_dir, None, **arm_kw("ABS", 1.0))
    tb_pct = gfills(D, bm_dir, None, **arm_kw("PCT", 1.0))
    hb = same(tb_abs, tb_pct)
    P_(f"    H-B  BMOM ABS == PCT (0 % size-2, so the denominator cannot bite) ..... "
       f"{'PASS' if hb else 'FAIL'}")
    ok &= hb
    p1_ref = keep(fills_qexit(D, SIG["P1"]["pos"], SIG["P1"]["sz"], SIG["P1"]["sc"]))
    p1_abs = keep(gfills(D, SIG["P1"]["pos"], SIG["P1"]["sz"], **arm_kw("ABS", 1.0)))
    hc1 = same(p1_ref, p1_abs)
    P_(f"    H-C1 gfills ABS reproduces fills_qexit on P1, byte for byte .......... "
       f"{'PASS' if hc1 else 'FAIL'}")
    ok &= hc1
    cnt = {k: (len(v), sum(x["u"] for x in v)) for k, v in
           (("P1", p1_abs),
            ("BMOM", keep(tb_abs)),
            ("X9a", keep(gfills(D, SIG["X9a"]["pos"], SIG["X9a"]["sz"], **arm_kw("ABS", 1.0)))))}
    W89REF = {"P1": (2002, 2368), "BMOM": (1043, 1043), "X9a": (1946, 2299)}
    hc2 = all(cnt[k] == W89REF[k] for k in W89REF)
    P_(f"    H-C2 ABS trade / contract counts == W89's committed table ............ "
       f"{'PASS' if hc2 else 'FAIL'}")
    for k in W89REF:
        P_(f"           {k:<6} this run {cnt[k][0]:>6,} tr /{cnt[k][1]:>6,} ctr    "
           f"W89 {W89REF[k][0]:>6,} tr /{W89REF[k][1]:>6,} ctr")
    ok &= hc2
    miss = sorted(set(range(1440)) - set(int(m) for m in prof.index))
    hd = len(prof) == 1380 and miss == list(range(1020, 1080))
    P_(f"    H-D  W82 spread profile: {len(prof)} minutes, the 60 absent are exactly "
       f"17:00-17:59 (CME break)  {'PASS' if hd else 'FAIL'}")
    ok &= hd
    fillm = set()
    for nm in ("P1", "X9a", "BMOM"):
        d_, s_ = OBJ[nm]
        for x in keep(gfills(D, d_, s_, **arm_kw("ABS", 1.0))):
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts)
                fillm.add(p_.hour * 60 + p_.minute)
    he = len(fillm - set(int(m) for m in prof.index)) == 0
    P_(f"    H-E  every fill minute of P1/X9a/BMOM is covered by the profile - the $3.00 "
       f"fallback never fires  {'PASS' if he else 'FAIL'}")
    ok &= he
    if not ok:
        P_("\n    A HARNESS CHECK FAILED. No arm is read.")
        out.close(); return
    P_("\n    all harness checks PASS.")

    # ================================================================= build every arm
    K = {}
    for nm in OBJ:
        d_, s_ = OBJ[nm]
        tr = keep(gfills(D, d_, s_, **arm_kw("ABS", 1.0)))
        K[nm] = sum(x["u"] for x in tr) / max(len(tr), 1)
    P_("")
    P_("    k = mean contracts per trade, measured on each object's OWN incumbent arm:")
    P_("      " + "   ".join(f"{nm} {K[nm]:.3f}" for nm in OBJ))

    TR = {}
    for nm in OBJ:
        d_, s_ = OBJ[nm]
        for arm in ARMS:
            TR[(nm, arm)] = keep(gfills(D, d_, s_, **arm_kw(arm, K[nm])))
    P_(f"    {len(TR)} sleeve arms built  [{_time.time()-t0:.0f}s]")

    # ================================================================= metrics
    def expo(trl):
        v = np.zeros(n)
        for x in trl:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return v

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def ctrs(trl):
        """contract round-turns ENTERED in each session (cost is charged where the trade opens)"""
        v = np.zeros(D["n_sess"])
        for x in trl:
            v[int(sid[i_of(x["et"])])] += x["u"]
        return v[sess_in]

    def rate(trl):
        """candidate-specific spread friction $/ctrRT from THIS arm's own fill minutes"""
        w = defaultdict(float)
        for x in trl:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts)
                w[p_.hour * 60 + p_.minute] += x["u"]
        tot = sum(w.values())
        if tot <= 0:
            return 0.0
        return TICKV * sum(float(prof.get(m, 3.0)) * c_ for m, c_ in w.items()) / tot

    SER = {k: daily(v) for k, v in TR.items()}
    EXP = {k: expo(v) for k, v in TR.items()}
    CTR = {k: ctrs(v) for k, v in TR.items()}
    RATE = {k: rate(v) for k, v in TR.items()}
    NTR = {k: float(len(v)) for k, v in TR.items()}

    WINDOWS = [("FULL", "2022-07-01", "2026-08-01"),
               ("2024+", "2024-01-01", "2026-08-01"),
               ("2025", "2025-01-01", "2026-01-01"),
               ("2026YTD", "2026-01-01", "2026-08-01"),
               ("t12m", "2025-08-01", "2026-08-01"),
               ("t6m", "2026-02-01", "2026-08-01"),
               ("t3m", "2026-05-01", "2026-08-01")]
    sd = sdate.to_numpy()
    MASK = {w: (sd >= np.datetime64(a_)) & (sd < np.datetime64(b_)) for w, a_, b_ in WINDOWS}
    minmask = {}
    for w, a_, b_ in WINDOWS:
        mm = np.zeros(n, bool)
        keepsess = np.zeros(D["n_sess"], bool)
        keepsess[sess_in[MASK[w]]] = True
        mm = keepsess[sid]
        minmask[w] = mm

    def netser(key, msk):
        """session P&L NET of that session's own candidate-specific spread friction"""
        return SER[key][msk] - RATE[key] * CTR[key][msk]

    def dash(key, w):
        msk, mm = MASK[w], minmask[w]
        ctr = float(CTR[key][msk].sum())
        nwk = len(set(wk[msk]))
        cw = RATE[key] * ctr / max(nwk, 1)
        dser = netser(key, msk)
        wv = pd.Series(dser).groupby(wk[msk]).sum().to_numpy()
        dp = dd_profile(wv)
        stk = max((len(list(g)) for c_, g in itertools.groupby(wv < 0) if c_), default=0)
        ex = EXP[key][mm]
        held = ex[ex > 0]
        cvar_k = max(1, int(round(0.05 * len(wv))))
        cvar = float(np.sort(wv)[:cvar_k].mean())
        npts = float(dser.sum()) / max(msk.sum(), 1) / PV
        return dict(
            obj=key[0], arm=key[1], window=w, nsess=int(msk.sum()), nwk=nwk,
            trades=int(round(NTR[key] * ctr / max(CTR[key].sum(), 1e-9))),
            contracts=int(round(ctr)), rate=RATE[key], cost_wk=cw,
            net=float(dser.sum()), weekly=float(wv.mean()),
            weekly_fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
            pts_sess=npts, posday=100 * float((dser > 0).mean()),
            poswk=100 * float((wv > 0).mean()), medwk=float(np.median(wv)),
            maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(wv.min()),
            cvar5=cvar, streak=int(stk),
            ctrmin=float(ex.sum()), peak=float(ex.max()) if len(ex) else 0.0,
            meansz=float(held.mean()) if len(held) else 0.0,
            ppcm=float(dser.sum()) / max(ex.sum(), 1e-9),
            t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(max(len(wv), 2)), 1e-9))

    # baskets: PER-UNIT combination of independently boxed sleeves (W97's convention).
    # The primary metric is scale-invariant, so the divisor cannot move the verdict.
    for a_, b_, lab in ((1, 1, "1:1"), (1, 2, "1:2"), (2, 3, "2:3")):
        for arm in ARMS:
            kb, kx, kn = ("BMOM", arm), ("X9a", arm), (lab, arm)
            s_ = float(a_ + b_)
            SER[kn] = (a_ * SER[kb] + b_ * SER[kx]) / s_
            EXP[kn] = (a_ * EXP[kb] + b_ * EXP[kx]) / s_
            CTR[kn] = (a_ * CTR[kb] + b_ * CTR[kx]) / s_
            NTR[kn] = (a_ * NTR[kb] + b_ * NTR[kx]) / s_
            TR[kn] = TR[kb] + TR[kx]
            cb, cx = a_ * CTR[kb].sum(), b_ * CTR[kx].sum()
            RATE[kn] = (RATE[kb] * cb + RATE[kx] * cx) / max(cb + cx, 1e-9)
    ALLOBJ = list(OBJ) + ["1:1", "1:2", "2:3"]
    rows = [dash((nm, arm), w) for nm in ALLOBJ for arm in ARMS for w, _, _ in WINDOWS]
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "dashboard.csv"), index=False)

    # ---- ADDITIVE EXPORT (2026-08-27). Changes NO computation: it dumps the same weekly series
    # `dash()` already aggregates, so the ABS/PCT comparison can be run on the standard fixed
    # windows (FULL/104w/52w/26w/13w) that this run's own WINDOWS list does not carry.
    _fullmsk = MASK["FULL"]
    _wk = pd.DataFrame({"week": wk[_fullmsk]})
    for _key in TR:
        if _key[0] != "P1":
            continue
        _wk[_key[1]] = netser(_key, _fullmsk)
    _wk.groupby("week", as_index=True).sum().to_csv(
        os.path.join(OUT, "weekly_arms_P1.csv"))

    # ================================================================= the primary read
    def show(w, objs):
        P_("")
        P_(f"  --- {w} " + "-" * (110 - len(w)))
        P_(f"{'object':<11}{'arm':<11}{'trades':>8}{'ctr':>7}{'$/ctrRT':>9}{'wk$':>9}"
           f"{'wk$@fixDD':>11}{'wk+%':>8}{'day+%':>8}{'maxDD':>10}{'top5':>9}{'CVaR5':>9}"
           f"{'strk':>5}{'t':>6}")
        for nm in objs:
            base = None
            for arm in ARMS:
                r = DF[(DF.obj == nm) & (DF.arm == arm) & (DF.window == w)].iloc[0]
                if arm == "ABS":
                    base = r["weekly_fixdd"]
                d_ = 100 * (r["weekly_fixdd"] / base - 1) if base else 0.0
                tag = "" if arm == "ABS" else f"  {d_:+.1f}%"
                P_(f"{nm:<11}{arm:<11}{r['trades']:>8,}{r['contracts']:>7,}{r['rate']:>9.2f}"
                   f"{r['weekly']:>9,.0f}{r['weekly_fixdd']:>11,.0f}{r['poswk']:>7.1f}%"
                   f"{r['posday']:>7.1f}%{r['maxdd']:>10,.0f}{r['top5']:>9,.0f}"
                   f"{r['cvar5']:>9,.0f}{r['streak']:>5}{r['t']:>6.2f}{tag}")
            P_("")
    P_("")
    P_("=" * 122)
    P_("=== THE PRIMARY: weekly $ at a FIXED $20,245 max drawdown, net of per-arm friction")
    P_("=" * 122)
    show("FULL", ["P1", "X9a", "BMOM", "NETFUSE_1", "NETFUSE_Q", "1:1", "1:2", "2:3"])

    # paired weekly test PCT - ABS and PCT - ABS_LOOSE, on the primary window
    P_("")
    P_("=" * 122)
    P_("=== PAIRED WEEKLY TESTS (CHARTER AMENDMENT 2 sec 2(a): no sub-period claim without an SE)")
    P_("=" * 122)
    P_(f"{'object':<11}{'comparison':<22}{'mean/wk':>10}{'SE':>9}{'t':>7}{'p':>9}{'N':>6}"
       f"{'95% CI':>24}")
    prows = []
    msk = MASK["FULL"]
    for nm in ("P1", "X9a", "BMOM", "NETFUSE_1", "NETFUSE_Q", "1:1", "1:2", "2:3"):
        for lo_, hi_ in (("ABS", "PCT"), ("ABS_LOOSE", "PCT"), ("ABS", "ABS_LOOSE"),
                         ("ABS", "PCT_MATCH"), ("ABS", "NOBOX")):
            wa = pd.Series(netser((nm, lo_), msk)).groupby(wk[msk]).sum().to_numpy()
            wb = pd.Series(netser((nm, hi_), msk)).groupby(wk[msk]).sum().to_numpy()
            d_ = wb - wa
            se = d_.std(ddof=1) / np.sqrt(len(d_))
            tt = d_.mean() / max(se, 1e-9)
            pv = 2 * (1 - 0.5 * (1 + erf(abs(tt) / sqrt(2))))
            P_(f"{nm:<11}{hi_+' - '+lo_:<22}{d_.mean():>10,.0f}{se:>9,.0f}{tt:>7.2f}{pv:>9.3f}"
               f"{len(d_):>6}   [{d_.mean()-1.96*se:>9,.0f},{d_.mean()+1.96*se:>9,.0f}]")
            prows.append(dict(obj=nm, cmp=f"{hi_}-{lo_}", mean=d_.mean(), se=se, t=tt, p=pv,
                              n=len(d_)))
        P_("")
    pd.DataFrame(prows).to_csv(os.path.join(OUT, "paired.csv"), index=False)

    # ================================================================= recency dashboard
    P_("")
    P_("=" * 122)
    P_("=== RECENCY DASHBOARD (directive sec 3 / sec 13). NOTE 2026-05-31 -> 07-31 is BURNED;")
    P_("===  t3m lies entirely inside it and t6m largely does. Labelled, not hidden.")
    P_("=" * 122)
    for w in ("2024+", "2025", "2026YTD", "t12m", "t6m", "t3m"):
        show(w, ["P1", "2:3"])

    # ================================================================= faithfulness check
    P_("")
    P_("=" * 122)
    P_("=== FAITHFULNESS: rebuild P1/PCT SELF-CONSISTENTLY (score recomputed from its own")
    P_("===               entry schedule) and check the verdict does not move.")
    P_("=" * 122)
    bb2 = gfills(D, SIG["P1"]["pos"], None, **arm_kw("PCT", 1.0))
    ee2 = np.array([i_of(x["et"]) for x in bb2 if A <= np.datetime64(x["et"]) < B])
    s2, _ = causal_score(X, ee2, window=WIN)
    tr_sc = keep(gfills(D, SIG["P1"]["pos"], np.where(s2 >= 3, 2, 1).astype(np.int8),
                        **arm_kw("PCT", 1.0)))
    ksc = ("P1_SC", "PCT")
    SER[ksc] = daily(tr_sc); EXP[ksc] = expo(tr_sc); CTR[ksc] = ctrs(tr_sc)
    TR[ksc] = tr_sc; RATE[ksc] = rate(tr_sc); NTR[ksc] = float(len(tr_sc))
    rsc = dash(ksc, "FULL")
    rows.append(rsc)
    for nm, arm in (("P1", "ABS"), ("P1", "PCT")):
        r = DF[(DF.obj == nm) & (DF.arm == arm) & (DF.window == "FULL")].iloc[0]
        P_(f"    {nm+'/'+arm:<14} wk$@fixDD {r['weekly_fixdd']:>9,.0f}   wk+% {r['poswk']:>6.2f}"
           f"   top5 {r['top5']:>9,.0f}   trades {r['trades']:>6,}")
    P_(f"    {'P1_SC/PCT':<14} wk$@fixDD {rsc['weekly_fixdd']:>9,.0f}   wk+% {rsc['poswk']:>6.2f}"
       f"   top5 {rsc['top5']:>9,.0f}   trades {rsc['trades']:>6,}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "dashboard.csv"), index=False)

    # ================================================================= Tier-3 deep stress
    P_("")
    P_("=" * 122)
    P_("=== TIER-3 STRESS 2006-2021 (directive sec 3: recorded, NOT a promotion veto)")
    P_("=" * 122)
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    nd, td, sidd, lbd, fbd = DD["n"], DD["t"], DD["sid"], DD["lb"], DD["fb"]
    XD = fast_build_context(DD)
    zz = np.load(os.path.join(W80OUT, f"mem_deep_{nd}.npz"))
    memd, bmomd, tiltd = zz["mem"], zz["bmom"], zz["tilt"]
    dsd = pd.to_datetime(DD["sess_date"]); isod = dsd.isocalendar()
    wkd = (isod["year"].astype(str) + "-W" + isod["week"].astype(str).str.zfill(2)).to_numpy()
    CHd = build_channels(DD, which=["X9a_disp_sessanchor"])
    flatd = td >= DD["sess_end"][sidd] - np.timedelta64(21 * 60, "s")
    P_(f"    deep substrate {nd:,} bars / {DD['n_sess']:,} sessions  [{_time.time()-t0:.0f}s]")

    def i_ofd(ts):
        return int(min(np.searchsorted(td, np.datetime64(ts)), nd - 1))

    def dailyd(trl):
        sp = np.zeros(DD["n_sess"])
        for x in trl:
            sp[int(sidd[i_ofd(x["et"])])] += x["pnl"]
        return sp

    SIGd = {}
    for nm, chan in (("P1", bmomd), ("X9a", CHd["X9a_disp_sessanchor"])):
        vl, _ = votes(DD, memd, bmomd, tiltd, XD, chan)
        p = vl.astype(np.int8)
        bb = fills_daily(DD, p, halt=1300, target=1000)
        ee = np.array([i_ofd(x["et"]) for x in bb])
        s_, _ = causal_score(XD, ee, window=WIN)
        SIGd[nm] = (p, np.where(s_ >= 3, 2, 1).astype(np.int8))
        P_(f"    deep {nm} built  [{_time.time()-t0:.0f}s]")
    OBJd = {"P1": SIGd["P1"], "X9a": SIGd["X9a"],
            "BMOM": (np.where(flatd, 0, bmomd).astype(np.int8), None)}
    SERd, Kd = {}, {}
    for nm, (d_, s_) in OBJd.items():
        tr = gfills(DD, d_, s_, **arm_kw("ABS", 1.0))
        Kd[nm] = sum(x["u"] for x in tr) / max(len(tr), 1)
    for nm, (d_, s_) in OBJd.items():
        for arm in ARMS:
            SERd[(nm, arm)] = dailyd(gfills(DD, d_, s_, **arm_kw(arm, Kd[nm])))
    for arm in ARMS:
        SERd[("2:3", arm)] = (2 * SERd[("BMOM", arm)] + 3 * SERd[("X9a", arm)]) / 5.0

    def pand(v):
        w = pd.Series(v).groupby(wkd).sum().to_numpy()
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(net=float(v.sum()), weekly=float(w.mean()),
                    weekly_fixdd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((w > 0).mean()), maxdd=dp["maxdd"],
                    top5=dp["dd_mean_top5"], worst=float(w.min()), streak=int(stk))
    P_("")
    P_(f"{'object':<10}{'arm':<11}{'net $':>13}{'wk$':>9}{'wk$@fixDD':>11}{'wk+%':>8}"
       f"{'maxDD':>11}{'top5':>10}{'worst':>10}{'strk':>6}")
    drows = []
    for nm in ("P1", "X9a", "BMOM", "2:3"):
        base = None
        for arm in ARMS:
            a = pand(SERd[(nm, arm)])
            if arm == "ABS":
                base = a["weekly_fixdd"]
            d_ = 100 * (a["weekly_fixdd"] / base - 1) if base else 0.0
            P_(f"{nm:<10}{arm:<11}{a['net']:>13,.0f}{a['weekly']:>9,.0f}"
               f"{a['weekly_fixdd']:>11,.0f}{a['poswk']:>7.1f}%{a['maxdd']:>11,.0f}"
               f"{a['top5']:>10,.0f}{a['worst']:>10,.0f}{a['streak']:>6}"
               f"{'' if arm=='ABS' else f'  {d_:+.1f}%'}")
            drows.append(dict(obj=nm, arm=arm, **a))
        P_("")
    pd.DataFrame(drows).to_csv(os.path.join(OUT, "deep_stress.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
