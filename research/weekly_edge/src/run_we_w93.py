"""WE_W93 - NETFUSE_1 AS A CHALLENGER TO P1.

Spec: runs/WE_W93_NETFUSE/spec.yaml, committed BEFORE this ran.

Five preregistered conditions: the power-checked rolling gate, a session-shift specificity null
that destroys ONLY the alignment between the long and short books, W29's walk-forward of the
inherited constants, the sixteen unseen years as a RISK test, and top-k-day concentration.
Nothing is adopted under any outcome.
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
from run_we_w01 import ROOT, PV, COMM_RT, sm14_1m                        # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_fastctx import fast_build_context, verify                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W93_NETFUSE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
C_P1 = 14.52
NSHIFT = 200
RNG = np.random.default_rng(20260893)


def build(D, mem, bmom, tilt, ctx):
    """Return (long_target, short_target) for the frozen object on any substrate."""
    n, tarr, sid = D["n"], D["t"], D["sid"]
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}

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
    TG = {}
    for name, vols in MEMBERS.items():
        cols = [idx_l13[v] for v in vols]
        s_ = mem[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        TG[name] = hyst(0.7086 * Tp + 2.83 * bmom.astype(float))

    def vote_(side):
        vs = []
        for m_ in MEMBERS:
            tg = TG[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else \
                    ((ctx["norm"] <= 0) | (ctx["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (ctx["dL"] if side > 0 else ctx["dS"]) if dg else okv
                    hit = (tg > 0) if side > 0 else (tg < 0)
                    vs.append(np.where(hit & a_, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)
    return (vote_(+1) >= 0.5), (vote_(-1) >= 0.5)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "netfuse_challenge.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb = D["n"], D["t"], D["sid"], D["lb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    st = np.zeros(D["n_sess"], np.int64)
    st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    inw = np.array([in_win[s] for s in sid])
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    ds = pd.Series(sdate)
    NWk = len(set(wk))
    P_(f"=== {len(sess_in)} sessions / {NWk} weeks [{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(trl):
        return [x for x in trl if in_win[int(sid[i_of(x["et"])])]]

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def cmin(trl):
        v = np.zeros(n)
        for x in trl:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return float(v[inw].sum())

    VL, VS = build(D, mem, bmom, tilt, X)
    tgt = np.where(VL & VS, 0, np.where(VL, 1, np.where(VS, -1, 0))).astype(np.int8)
    TR_NF = keep(sfills(D, tgt, halt=1300.0, target=1000.0))
    # P1 (incumbent) with its quality layer, exactly as everywhere else
    pl = VL.astype(np.int8)
    bb = fills_daily(D, pl, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc_, _ = causal_score(X, ee, window=WIN)
    TR_P1 = keep(fills_qexit(D, pl, np.where(sc_ >= 3, 2, 1).astype(np.int8), sc_))
    NF, P1 = daily(TR_NF), daily(TR_P1)
    cmN, cmP = cmin(TR_NF), cmin(TR_P1)
    rtN = sum(x["u"] for x in TR_NF) / NWk
    rtP = sum(x["u"] for x in TR_P1) / NWk
    sN = cmP / cmN
    P_(f"    NETFUSE_1 {len(TR_NF):,} trades, {rtN:.2f} ctrRT/wk, {cmN:,.0f} contract-minutes")
    P_(f"    P1        {len(TR_P1):,} trades, {rtP:.2f} ctrRT/wk, {cmP:,.0f} contract-minutes")
    P_(f"    exposure-matching scale for NETFUSE_1 = {sN:.4f}")

    def pan(v, msk, cost_wk):
        w = pd.Series(v[msk]).groupby(wk[msk]).sum().to_numpy() - cost_wk
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    se=float(w.std(ddof=1) / np.sqrt(len(w))))
    ALL = np.ones(len(sess_in), bool)
    cN, cP = C_P1 * rtN * sN, C_P1 * rtP

    # ============================================================ C1 - the gate
    P_("")
    P_("=" * 118)
    P_("=== C1: THE CORRECTED ROLLING GATE (oracle battery FIRST)")
    P_("=" * 118)
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")

    def gate(v, cv, base, cb):
        c = dict(m=0, w=0, d=0, a=0, n=0)
        for e in ends:
            msk = np.asarray((ds > e - pd.DateOffset(months=24)) & (ds <= e))
            if msk.sum() < 300:
                continue
            a_ = pan(v, msk, cv); b_ = pan(base, msk, cb)
            if a_ is None or b_ is None:
                continue
            c["n"] += 1
            x1 = a_["weekly_dd"] > b_["weekly_dd"]; x2 = a_["wkpos"] > b_["wkpos"]
            x3 = a_["top5"] < b_["top5"]
            c["m"] += x1; c["w"] += x2; c["d"] += x3; c["a"] += (x1 and x2 and x3)
        nn = max(c["n"], 1)
        return {k: 100 * v_ / nn for k, v_ in c.items() if k != "n"} | {"n": c["n"]}

    ok = True
    for k, v in {"P1 + $200/session": P1 + 200.0, "P1 + $500/session": P1 + 500.0,
                 "P1 losses halved": np.where(P1 < 0, P1 * .5, P1),
                 "P1 losses x0.75": np.where(P1 < 0, P1 * .75, P1)}.items():
        g = gate(v, cP, P1, cP)
        P_(f"    oracle {k:<22} ALL-THREE {g['a']:>5.0f} %")
        ok &= g["a"] >= 75
    P_(f"    -> gate is {'USABLE' if ok else 'BROKEN - NO VERDICTS ISSUED'}")
    if not ok:
        out.close(); return
    gN = gate(NF * sN, cN, P1, cP)
    P_("")
    P_(f"    NETFUSE_1 vs P1, {gN['n']} windows, exposure-matched, candidate costs:")
    P_(f"      money {gN['m']:>5.0f} %   wk+% {gN['w']:>5.0f} %   raw top-5 DD {gN['d']:>5.0f} %"
       f"   ALL-THREE {gN['a']:>5.0f} %")
    P_(f"    C1 (bar > 50 %): {'PASS' if gN['a'] > 50 else 'FAIL'}")

    # ============================================================ C2 - specificity null
    P_("")
    P_("=" * 118)
    P_("=== C2: SPECIFICITY NULL - session-wise circular shift of the SHORT book only")
    P_("=" * 118)
    sess_slice = {}
    for s in range(D["n_sess"]):
        pass
    starts = np.flatnonzero(D["fb"])
    bounds = list(starts) + [n]
    blocks = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    NB = len(blocks)
    real = pan(NF * sN, ALL, cN)
    P_(f"    real: wk+% {real['wkpos']:.2f}  top5DD {real['top5']:,.0f}  "
       f"money@fixDD {real['weekly_dd']:,.0f}")
    P_(f"    {NSHIFT} shifts, each preserving the short book's firing rate, run lengths and")
    P_("    intraday shape and destroying ONLY which session it lands on...")
    ks = RNG.choice(np.arange(1, NB), size=min(NSHIFT, NB - 1), replace=False)
    nulls = []
    for j, k in enumerate(ks):
        vsh = np.zeros(n, bool)
        for i, (a_, b_) in enumerate(blocks):
            sa, sb = blocks[(i + int(k)) % NB]
            m = min(b_ - a_, sb - sa)
            vsh[a_:a_ + m] = VS[sa:sa + m]
        t2 = np.where(VL & vsh, 0, np.where(VL, 1, np.where(vsh, -1, 0))).astype(np.int8)
        tr2 = keep(sfills(D, t2, halt=1300.0, target=1000.0))
        if not tr2:
            continue
        s2 = cmP / max(cmin(tr2), 1.0)
        a2 = pan(daily(tr2) * s2, ALL, C_P1 * sum(x["u"] for x in tr2) / NWk * s2)
        if a2:
            nulls.append((a2["wkpos"], a2["top5"], a2["weekly_dd"]))
        if (j + 1) % 40 == 0:
            P_(f"      {j+1}/{len(ks)} [{_time.time()-t0:.0f}s]")
    nulls = np.array(nulls)
    pd.DataFrame(nulls, columns=["wkpos", "top5", "weekly_dd"]).to_csv(
        os.path.join(OUT, "null_shift.csv"), index=False)
    p_wk = 100 * float((nulls[:, 0] < real["wkpos"]).mean())
    p_t5 = 100 * float((nulls[:, 1] > real["top5"]).mean())
    p_mn = 100 * float((nulls[:, 2] < real["weekly_dd"]).mean())
    P_("")
    P_(f"{'leg':<22}{'real':>12}{'null mean':>12}{'null p95':>12}{'percentile':>12}")
    P_(f"{'positive-week %':<22}{real['wkpos']:>12.2f}{nulls[:,0].mean():>12.2f}"
       f"{np.percentile(nulls[:,0],95):>12.2f}{p_wk:>11.1f}%")
    P_(f"{'raw mean top-5 DD':<22}{real['top5']:>12,.0f}{nulls[:,1].mean():>12,.0f}"
       f"{np.percentile(nulls[:,1],5):>12,.0f}{p_t5:>11.1f}%")
    P_(f"{'weekly $ at fixed DD':<22}{real['weekly_dd']:>12,.0f}{nulls[:,2].mean():>12,.0f}"
       f"{np.percentile(nulls[:,2],95):>12,.0f}{p_mn:>11.1f}%")
    c2 = (p_t5 >= 95) and (p_wk >= 95)
    P_(f"    C2 (>= 95th on top-5 DD AND positive-week %): {'PASS' if c2 else 'FAIL'}")

    # ============================================================ C3 - walk forward
    P_("")
    P_("=" * 118)
    P_("=== C3: WALK-FORWARD of the INHERITED constants (W29's protocol)")
    P_("=" * 118)
    HAL = [800, 1000, 1300, 1600, 2000]
    TGT = [600, 800, 1000, 1400, None]
    P_(f"    grid {len(HAL)}x{len(TGT)} = {len(HAL)*len(TGT)} (halt, target) combinations, "
       f"each run ONCE over the whole series")
    GRID = {}
    for h in HAL:
        for tg in TGT:
            tr = keep(sfills(D, tgt, halt=float(h), target=tg))
            GRID[(h, tg)] = (daily(tr), sum(x["u"] for x in tr) / NWk)
    P_(f"    grid built [{_time.time()-t0:.0f}s]")
    qends = pd.date_range(ds.min() + pd.DateOffset(months=12), ds.max(), freq="QE")
    chosen, wf = [], np.zeros(len(sess_in))
    for qe in qends:
        tr_m = np.asarray((ds > qe - pd.DateOffset(months=12)) & (ds <= qe))
        te_m = np.asarray((ds > qe) & (ds <= qe + pd.DateOffset(months=3)))
        if tr_m.sum() < 150 or te_m.sum() < 20:
            continue
        best, bk = -1e18, None
        for k, (v, rt) in GRID.items():
            a = pan(v, tr_m, C_P1 * rt)
            if a and a["weekly_dd"] > best:
                best, bk = a["weekly_dd"], k
        chosen.append(bk)
        wf[te_m] = GRID[bk][0][te_m]
    fixed = pan(NF, ALL, C_P1 * rtN)
    cov = np.zeros(len(sess_in), bool)
    for qe in qends:
        te_m = np.asarray((ds > qe) & (ds <= qe + pd.DateOffset(months=3)))
        if te_m.sum() >= 20:
            cov |= te_m
    a_wf = pan(wf, cov, C_P1 * rtN); a_fx = pan(NF, cov, C_P1 * rtN)
    ret = 100 * a_wf["weekly_dd"] / max(a_fx["weekly_dd"], 1e-9)
    churn = 100 * sum(1 for i in range(1, len(chosen)) if chosen[i] != chosen[i - 1]) \
        / max(len(chosen) - 1, 1)
    inc = 100 * sum(1 for k in chosen if k == (1300, 1000)) / max(len(chosen), 1)
    P_(f"    {len(chosen)} refits over {int(cov.sum())} traded sessions")
    P_(f"{'':<20}{'wk$@fixDD':>12}{'wk $':>10}{'wk+%':>9}")
    P_(f"{'    walk-forward':<20}{a_wf['weekly_dd']:>12,.0f}{a_wf['weekly']:>10,.0f}"
       f"{a_wf['wkpos']:>8.1f}%")
    P_(f"{'    fixed quote':<20}{a_fx['weekly_dd']:>12,.0f}{a_fx['weekly']:>10,.0f}"
       f"{a_fx['wkpos']:>8.1f}%")
    P_(f"    RETENTION {ret:.0f} %   choice churn {churn:.0f} %   "
       f"(1300, 1000) chosen in {inc:.0f} % of refits")
    P_(f"    C3 (retention >= 80 %): {'PASS' if ret >= 80 else 'FAIL'}")
    pd.DataFrame(dict(refit=range(len(chosen)), halt=[c[0] for c in chosen],
                      target=[str(c[1]) for c in chosen])).to_csv(
        os.path.join(OUT, "walkforward.csv"), index=False)

    # ============================================================ C5 - concentration
    P_("")
    P_("=" * 118)
    P_("=== C5: TOP-k-DAY CONCENTRATION (W76's standing lesson)")
    P_("=" * 118)
    t24 = np.asarray(sdate >= pd.Timestamp("2024-08-01"))
    P_(f"{'drop best':<12}{'full wk $':>12}{'full wk+%':>11}{'t24 wk $':>11}{'t24 wk+%':>10}")
    conc = []
    for kdrop in (0, 1, 3, 5, 10):
        v = NF.copy()
        if kdrop:
            v[np.argsort(v)[-kdrop:]] = 0.0
        af = pan(v, ALL, C_P1 * rtN); a2 = pan(v, t24, C_P1 * rtN)
        P_(f"{kdrop:<12}{af['weekly']:>12,.0f}{af['wkpos']:>10.1f}%{a2['weekly']:>11,.0f}"
           f"{a2['wkpos']:>9.1f}%")
        conc.append(dict(drop=kdrop, full_weekly=af["weekly"], full_wkpos=af["wkpos"],
                         t24_weekly=a2["weekly"], t24_wkpos=a2["wkpos"]))
    pd.DataFrame(conc).to_csv(os.path.join(OUT, "concentration.csv"), index=False)
    c5 = conc[3]["full_weekly"] > 0 and conc[3]["t24_weekly"] > 0
    P_(f"    C5 (positive full AND t24 with best 5 removed): {'PASS' if c5 else 'FAIL'}")

    # ============================================================ C4 - deep history
    P_("")
    P_("=" * 118)
    P_("=== C4: THE SIXTEEN UNSEEN YEARS, 2006-2021 - a RISK test, not a return test")
    P_("=" * 118)
    P_("    W82's $14.65 spread does NOT transport to NQ 1,600-16,000. Commission only below.")
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    nd = DD["n"]
    vD = load_deep("2010-01-04", "2010-12-31 17:00")
    bad = verify(vD)
    P_(f"    fast-context harness check on a 2010 slice ({vD['n']:,} bars): "
       f"{'BIT-EXACT' if not bad else 'MISMATCH ' + str(bad)}")
    if bad:
        P_("    *** harness unverified on deep data - C4 ABANDONED per repo rule ***")
        out.close(); return
    XD = fast_build_context(DD)
    cache = os.path.join(W80OUT, f"mem_deep_{nd}.npz")
    if not os.path.exists(cache):
        P_(f"    no cached deep member matrix at {cache} - building")
        _, memd, bmomd, tiltd = sm14_1m(DD, 460, volmults=L13, return_members=True)
        np.savez_compressed(cache, mem=memd, bmom=bmomd, tilt=tiltd)
    zz = np.load(cache); memd, bmomd, tiltd = zz["mem"], zz["bmom"], zz["tilt"]
    P_(f"    deep substrate {nd:,} bars / {DD['n_sess']:,} sessions [{_time.time()-t0:.0f}s]")
    VLd, VSd = build(DD, memd, bmomd, tiltd, XD)
    td, sidd, lbd = DD["t"], DD["sid"], DD["lb"]
    dsd = pd.to_datetime(DD["sess_date"])
    isod = dsd.isocalendar()
    wkd = (isod["year"].astype(str) + "-W" + isod["week"].astype(str).str.zfill(2)).to_numpy()

    def i_ofd(ts):
        return int(min(np.searchsorted(td, np.datetime64(ts)), nd - 1))

    def dailyd(trl):
        sp = np.zeros(DD["n_sess"])
        for x in trl:
            sp[int(sidd[i_ofd(x["et"])])] += x["pnl"]
        return sp

    def cmind(trl):
        v = np.zeros(nd)
        for x in trl:
            a_, b_ = i_ofd(x["et"]), i_ofd(x["xt"])
            v[a_:(b_ + 1 if lbd[b_] else b_)] += x["u"]
        return float(v.sum())
    tgd = np.where(VLd & VSd, 0, np.where(VLd, 1, np.where(VSd, -1, 0))).astype(np.int8)
    trNd = sfills(DD, tgd, halt=1300.0, target=1000.0)
    pld = VLd.astype(np.int8)
    bbd = fills_daily(DD, pld, halt=1300, target=1000)
    eed = np.array([i_ofd(x["et"]) for x in bbd])
    scd, _ = causal_score(XD, eed, window=WIN)
    trPd = fills_qexit(DD, pld, np.where(scd >= 3, 2, 1).astype(np.int8), scd)
    NFd, P1d = dailyd(trNd), dailyd(trPd)
    sd = cmind(trPd) / max(cmind(trNd), 1.0)

    def pand(v):
        w = pd.Series(v).groupby(wkd).sum().to_numpy()
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), net=float(np.sum(v)))
    aNd, aPd = pand(NFd * sd), pand(P1d)
    P_("")
    P_(f"{'object':<14}{'trades':>8}{'weeks':>7}{'net $':>13}{'pts/sess':>10}{'wk+%':>8}"
       f"{'maxDD':>11}{'top5DD':>10}{'worst':>10}{'streak':>8}")
    for nm, a, tr, s_ in (("NETFUSE_1", aNd, trNd, sd), ("P1", aPd, trPd, 1.0)):
        pts = s_ * sum(x["pnl"] + COMM_RT * x["u"] for x in tr) / PV / DD["n_sess"]
        P_(f"{nm:<14}{len(tr):>8,}{a['nwk']:>7}{a['net']:>13,.0f}{pts:>10.2f}"
           f"{a['wkpos']:>7.1f}%{a['maxdd']:>11,.0f}{a['top5']:>10,.0f}{a['worst']:>10,.0f}"
           f"{a['streak']:>8}")
    red = 100 * (1 - aNd["top5"] / max(aPd["top5"], 1e-9))
    redm = 100 * (1 - aNd["maxdd"] / max(aPd["maxdd"], 1e-9))
    P_("")
    P_(f"    top-5 drawdown reduction vs P1: {red:+.1f} %   max drawdown: {redm:+.1f} %")
    P_(f"    (W87's bar, reused so the two are comparable: >= 25 % smaller top-5)")
    c4 = red >= 25
    P_(f"    C4: {'PASS' if c4 else 'FAIL'}")
    yd = dsd.year.to_numpy()
    P_("")
    P_(f"    per-year net, deep (commission only):")
    yr_rows = []
    for y in sorted(set(yd)):
        m = yd == y
        P_(f"      {y}  NETFUSE {sd*NFd[m].sum():>11,.0f}    P1 {P1d[m].sum():>11,.0f}")
        yr_rows.append(dict(year=int(y), netfuse=float(sd * NFd[m].sum()),
                            p1=float(P1d[m].sum())))
    pd.DataFrame(yr_rows).to_csv(os.path.join(OUT, "deep_per_year.csv"), index=False)
    pd.DataFrame([dict(obj="NETFUSE_1", **aNd), dict(obj="P1", **aPd)]).to_csv(
        os.path.join(OUT, "deep.csv"), index=False)

    # ============================================================ verdict
    P_("")
    P_("=" * 118)
    res = {"C1 rolling gate": gN["a"] > 50, "C2 specificity null": c2,
           "C3 walk-forward": ret >= 80, "C4 deep risk": c4, "C5 concentration": c5}
    for k, v in res.items():
        P_(f"    {k:<24} {'PASS' if v else 'FAIL'}")
    P_(f"    -> {sum(res.values())} of 5.  NOTHING IS ADOPTED IN THIS WAVE UNDER ANY OUTCOME.")
    pd.DataFrame([{k: bool(v) for k, v in res.items()}]).to_csv(
        os.path.join(OUT, "verdict.csv"), index=False)
    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"), "NETFUSE_1": NF, "P1": P1}).to_csv(
        os.path.join(OUT, "series.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
