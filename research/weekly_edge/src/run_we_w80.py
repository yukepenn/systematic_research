"""WE_W80 - P1 vs X9a, and the first run of the FULL OBJECT on the sixteen unseen years.

Spec: runs/WE_W80_ANCHOR_HEADTOHEAD/spec.yaml, committed before this ran.

Per W79's meta-finding (six consecutive full-sample winners failed sub-period testing, always on
the drawdown sub-metric), THE ROLLING TEST RUNS FIRST, before any full-sample table is computed.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context, verify                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
DD_TARGET = 20245.0
SPLIT = pd.Timestamp("2026-05-30")
RNG = np.random.default_rng(20260880)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "anchor.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    d = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    d["date"] = pd.to_datetime(d["date"])
    iso = d["date"].dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    keys = sorted(set(wk)); wi = np.array([keys.index(x) for x in wk]); NW = len(keys)
    ds = d["date"]; yr = ds.dt.year.to_numpy()
    HELD = np.asarray(ds >= SPLIT)
    P1, X9 = d["P1"].to_numpy(), d["w72:X9a"].to_numpy()
    P_(f"=== modern extended window: {len(d)} sessions, {NW} weeks, "
       f"rho(P1, X9a) = {np.corrcoef(P1, X9)[0,1]:+.3f}")

    def wkv(v, m=None):
        m = np.ones(len(v), bool) if m is None else np.asarray(m)
        w_ = wi[m]
        cnt = np.bincount(w_, minlength=NW) > 0
        return np.bincount(w_, weights=v[m], minlength=NW)[cnt]

    def pan(v, m=None):
        w = wkv(v, m)
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for kk, g in itertools.groupby(w < 0) if kk), default=0)
        mm = np.ones(len(v), bool) if m is None else np.asarray(m)
        return dict(net=float(v[mm].sum()), wkpos=100 * float((w > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(w)), weekly=float(w.mean()),
                    weekly_dd=float(w.mean()) * k, dd5=dp["dd_mean_top5"] * k,
                    maxdd=float(dp["maxdd"]), worst=float(w.min()))

    # ================================================================ PHASE 1 - ROLLING FIRST
    P_(f"\n{'='*118}\n=== PHASE 1 (RUN FIRST, per W79's meta-finding): ROLLING 24-MONTH WINDOWS")
    P_(f"{'='*118}")
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")
    c1 = c2 = c3 = ca = nn = 0
    for e in ends:
        m = ((ds > e - pd.DateOffset(months=24)) & (ds <= e)).to_numpy()
        if m.sum() < 300:
            continue
        a_, b_ = pan(X9, m), pan(P1, m)
        if a_ is None or b_ is None:
            continue
        nn += 1
        x1 = a_["weekly_dd"] > b_["weekly_dd"]; x2 = a_["wkpos"] > b_["wkpos"]
        x3 = a_["dd5"] < b_["dd5"]
        c1 += x1; c2 += x2; c3 += x3; ca += (x1 and x2 and x3)
    a3 = 100 * ca / max(nn, 1)
    P_(f"   {nn} windows.  X9a beats P1 on:")
    P_(f"      weekly $ at a fixed $20,245 drawdown : {100*c1/max(nn,1):>5.0f} %")
    P_(f"      positive-week %                      : {100*c2/max(nn,1):>5.0f} %")
    P_(f"      mean top-5 drawdown                  : {100*c3/max(nn,1):>5.0f} %")
    P_(f"      ALL THREE                            : {a3:>5.0f} %   (bar: > 50 %) -> "
       f"{'PASS' if a3 > 50 else 'FAIL'}")
    pd.DataFrame([dict(n=nn, money=100 * c1 / nn, wkpos=100 * c2 / nn, dd=100 * c3 / nn,
                       all3=a3)]).to_csv(os.path.join(OUT, "rolling.csv"), index=False)

    # ================================================================ PHASE 2 - the panel
    HDR = (f"{'object':<22}{'net $':>11}{'wk+%':>7}{'wStrk':>7}{'medWk$':>9}{'weekly$':>9}"
           f"{'wk$@DD':>9}{'top5DD':>9}{'maxDD':>9}{'worst':>9}")
    P_(f"\n{'='*118}\n=== PHASE 2: the modern panel\n{'='*118}\n{HDR}")
    for lab, v in (("P1 (champion)", P1), ("X9a (challenger)", X9)):
        r = pan(v)
        P_(f"{lab:<22}{r['net']:>11,.0f}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}{r['maxdd']:>9,.0f}"
           f"{r['worst']:>9,.0f}")

    P_(f"\n=== PER YEAR (weekly $ | positive-week %) ===")
    yrs = sorted(set(yr))
    P_(f"{'object':<22}" + "".join(f"{y:>18}" for y in yrs))
    for lab, v in (("P1", P1), ("X9a", X9)):
        line = f"{lab:<22}"
        for y in yrs:
            r = pan(v, yr == y)
            line += f"{(f'{r[chr(119)+chr(101)+chr(101)+chr(107)+chr(108)+chr(121)]:,.0f} | {r[chr(119)+chr(107)+chr(112)+chr(111)+chr(115)]:.0f}%' if r else '-'):>18}"
        P_(line)

    P_(f"\n=== W76's 46 held-out sessions, WITH the concentration check (method rule 29) ===")
    P_(f"{'object':<22}{'net':>11}{'minus top-3':>14}{'median traded':>15}{'pos day %':>11}")
    for lab, v in (("P1", P1), ("X9a", X9)):
        h = v[HELD]; s = np.sort(np.abs(h))[::-1]
        top3 = h[np.argsort(-np.abs(h))][:3].sum()
        tr = h[h != 0]
        P_(f"{lab:<22}{h.sum():>11,.0f}{h.sum()-top3:>14,.0f}"
           f"{np.median(tr):>15,.0f}{100*float((h>0).mean()):>10.1f}%")

    # ================================================================ PHASE 3 - choice stability
    P_(f"\n{'='*118}\n=== PHASE 3: does the CHOICE between them churn?\n{'='*118}")
    qs = pd.date_range(ds.min() + pd.DateOffset(months=12), ds.max(), freq="QS")
    wf = np.zeros(len(P1)); picks = []
    for q in qs:
        tr = ((ds >= q - pd.DateOffset(months=12)) & (ds < q)).to_numpy()
        te = ((ds >= q) & (ds < q + pd.DateOffset(months=3))).to_numpy()
        if tr.sum() < 150 or te.sum() < 20:
            continue
        ra_, rb_ = pan(X9, tr), pan(P1, tr)
        pick = "X9a" if (ra_ and rb_ and ra_["weekly_dd"] > rb_["weekly_dd"]) else "P1"
        wf[te] = (X9 if pick == "X9a" else P1)[te]; picks.append(pick)
    m = wf != 0
    churn = 100 * float(np.mean(np.array(picks[1:]) != np.array(picks[:-1]))) if len(picks) > 1 \
        else np.nan
    P_(f"   {len(picks)} refits: {picks}")
    P_(f"   churn {churn:.0f} %   |   X9a chosen {picks.count('X9a')} of {len(picks)}")
    P_(f"\n{'':<22}{'wk+%':>8}{'weekly$':>10}{'wk$@DD':>10}{'top5DD':>10}{'worst':>10}")
    for lab, r in (("quarterly choice", pan(wf, m)), ("P1 fixed", pan(P1, m)),
                   ("X9a fixed", pan(X9, m))):
        P_(f"{lab:<22}{r['wkpos']:>7.1f}%{r['weekly']:>10,.0f}{r['weekly_dd']:>10,.0f}"
           f"{r['dd5']:>10,.0f}{r['worst']:>10,.0f}")

    # ================================================================ PHASE 4 - THE DEEP RUN
    P_(f"\n{'='*118}")
    P_("=== PHASE 4: THE SIXTEEN UNSEEN YEARS. The FULL OBJECT - not just the channel - has")
    P_("===          NEVER been run on 2006-2021 for either arm. This is the campaign's")
    P_("===          largest untouched sample.")
    P_(f"{'='*118}")
    P_("   CAVEAT that travels with every number below: the quality score's five features were")
    P_("   chosen by a full-sample scan on 2022-2026 (W33), so this measures the object AS")
    P_("   SPECIFIED, including that specification-level look-ahead. That is the right test.")

    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    nd, td, sidd = DD["n"], DD["t"], DD["sid"]
    P_(f"\n   deep substrate {nd:,} bars, {DD['n_sess']:,} sessions, {td[0]} -> {td[-1]} "
       f"[{_time.time()-t0:.0f}s]")

    vD = load_deep("2010-01-04", "2010-12-31 17:00")
    bad = verify(vD)
    P_(f"   fast-context harness check on a 2010 slice ({vD['n']:,} bars): "
       f"{'ALL ARRAYS BIT-EXACT' if not bad else 'MISMATCH ' + str(bad)} "
       f"[{_time.time()-t0:.0f}s]")
    if bad:
        P_("   *** harness unverified on deep data - PHASE 4 ABANDONED per spec ***")
        out.close(); return

    XD = fast_build_context(DD)
    P_(f"   deep context built [{_time.time()-t0:.0f}s]")
    cache = os.path.join(OUT, f"mem_deep_{nd}.npz")
    if os.path.exists(cache):
        z = np.load(cache); memd, bmomd, tiltd = z["mem"], z["bmom"], z["tilt"]
        P_(f"   member matrix from cache [{_time.time()-t0:.0f}s]")
    else:
        _, memd, bmomd, tiltd = sm14_1m(DD, 460, volmults=L13, return_members=True)
        np.savez_compressed(cache, mem=memd, bmom=bmomd, tilt=tiltd)
        P_(f"   member matrix built on 16 years [{_time.time()-t0:.0f}s]")

    CH = build_channels(DD, which=["X9a_disp_sessanchor"])
    x9d = CH["X9a_disp_sessanchor"]
    fbd = DD["fb"]; sed = DD["sess_end"]
    blocked = td >= sed[sidd] - np.timedelta64(30 * 60, "s")
    flatm = td >= sed[sidd] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(nd, np.int8)
        for i in range(nd):
            p = 0 if (i == 0 or fbd[i]) else tgt[i - 1]
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

    def deep_object(chan, tag):
        TG = {}
        for name, vols in MEMBERS.items():
            cols = [idx_l13[v] for v in vols]
            s_ = memd[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tiltd) & (s_ != 0) & (tiltd != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            TG[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        vs = []
        for name in MEMBERS:
            tg = TG[name]
            for q in QS:
                okv = np.ones(nd, bool) if q is None else ((XD["norm"] <= 0) | (XD["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (XD["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        del vs
        base = fills_daily(DD, pos, halt=1300, target=1000)
        ee = np.array([int(min(np.searchsorted(td, np.datetime64(x["et"])), nd - 1))
                       for x in base])
        sc, _ = causal_score(XD, ee, window=WIN)
        trl = fills_qexit(DD, pos, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
        P_(f"   {tag}: {len(trl):,} trades [{_time.time()-t0:.0f}s]")
        return trl

    res = {}
    for tag, chan in (("P1 (09:31 anchor)", bmomd), ("X9a (18:00 anchor)", x9d)):
        trl = deep_object(chan, tag)
        et = pd.to_datetime([x["et"] for x in trl]); pnl = np.array([x["pnl"] for x in trl])
        u = np.array([x["u"] for x in trl])
        sp = np.zeros(DD["n_sess"])
        for x in trl:
            sp[int(sidd[int(min(np.searchsorted(td, np.datetime64(x["et"])), nd - 1))])] += x["pnl"]
        res[tag] = dict(et=et, pnl=pnl, u=u, sp=sp)
        pd.DataFrame(dict(et=et, pnl=pnl)).to_csv(
            os.path.join(OUT, f"deep_{tag.split()[0]}.csv"), index=False)

    sdd = pd.to_datetime(DD["sess_date"])
    isod = sdd.isocalendar()
    wkd = (isod["year"].astype(str) + "-W" + isod["week"].astype(str).str.zfill(2)).to_numpy()
    kd = sorted(set(wkd)); wid = np.array([kd.index(x) for x in wkd]); NWD = len(kd)

    P_(f"\n{'object':<22}{'trades':>9}{'net $':>13}{'stress $':>13}{'pts/sess':>10}"
       f"{'$/trade':>10}{'t':>7}{'PF':>7}{'wk+%':>7}{'yrs>0':>8}")
    deep_rows = []
    for tag, r in res.items():
        pnl = r["pnl"]; se = pnl.std(ddof=1) / np.sqrt(len(pnl))
        gw = pnl[pnl > 0].sum(); gl = -pnl[pnl < 0].sum()
        w = np.bincount(wid, weights=r["sp"], minlength=NWD)
        w = w[np.bincount(wid, minlength=NWD) > 0]
        yv = pd.Series(pnl).groupby(r["et"].year).sum()
        P_(f"{tag:<22}{len(pnl):>9,}{pnl.sum():>13,.0f}"
           f"{pnl.sum()-STRESS_RT*r['u'].sum():>13,.0f}"
           f"{pnl.sum()/PV/DD['n_sess']:>10.2f}{pnl.mean():>10.1f}{pnl.mean()/se:>7.2f}"
           f"{(gw/gl if gl else np.nan):>7.3f}{100*float((w>0).mean()):>6.1f}%"
           f"{int((yv>0).sum()):>5}/{len(yv):<3}")
        deep_rows.append(dict(obj=tag, trades=len(pnl), net=float(pnl.sum()),
                              stress=float(pnl.sum() - STRESS_RT * r["u"].sum()),
                              pts=float(pnl.sum() / PV / DD["n_sess"]),
                              per_trade=float(pnl.mean()), t=float(pnl.mean() / se),
                              pf=float(gw / gl) if gl else np.nan,
                              wkpos=100 * float((w > 0).mean()),
                              yrs_pos=int((yv > 0).sum()), yrs=len(yv)))
    pd.DataFrame(deep_rows).to_csv(os.path.join(OUT, "deep.csv"), index=False)

    P_(f"\n   per year, net $ at 1 contract (deep-era dollars are NOT comparable to modern ones "
       f"- NQ traded 2,000-16,000):")
    ys = sorted(set(res["P1 (09:31 anchor)"]["et"].year))
    P_(f"{'':<22}" + "".join(f"{y:>9}" for y in ys))
    for tag, r in res.items():
        yv = pd.Series(r["pnl"]).groupby(r["et"].year).sum()
        P_(f"{tag:<22}" + "".join(f"{yv.get(y, 0):>9,.0f}" for y in ys))

    P_(f"\n{'='*118}\n=== VERDICT")
    P_(f"{'='*118}")
    dp1 = deep_rows[0]; dx9 = deep_rows[1]
    P_(f"   (1) rolling all-three in a majority : {a3:>5.0f} %  -> "
       f"{'PASS' if a3 > 50 else 'FAIL'}")
    P_(f"   (2) materially better over 2006-2021: X9a {dx9['pts']:.2f} vs P1 {dp1['pts']:.2f} "
       f"pts/session  -> {'PASS' if dx9['pts'] > dp1['pts'] * 1.2 else 'FAIL'}")
    P_(f"   (3) the quarterly choice does not churn: {churn:.0f} %  -> "
       f"{'PASS' if churn < 30 else 'FAIL'}")
    P_(f"\n   -> {'X9a REPLACES P1' if (a3>50 and dx9['pts']>dp1['pts']*1.2 and churn<30) else 'P1 REMAINS THE BASELINE. X9a is not promoted.'}")
    P_(f"\n=== STATUS: NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
