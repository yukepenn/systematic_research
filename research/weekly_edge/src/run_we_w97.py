"""WE_W97 - ACT ON THE AUDIT.

Spec: runs/WE_W97_AUDITFIX/spec.yaml, committed BEFORE this ran.

Three measurements the audit forced, each of which can change a published conclusion:
  M10  P1, the 2:3 pair and NETFUSE_1 on the deep 16 years in ONE run, so they share a baseline
       BY CONSTRUCTION. W87 and W93 used different P1 deep series and only one can be right.
  M3   the deconfounding control for "the low rho is temporal disjointness": split each object's
       daily P&L by ENTRY SEGMENT and correlate weekly against BMOM.
  M8   the isolation control for "the quality layer hurts the two-sided object": hold the EXIT
       policy fixed by denominating the session box per contract.
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
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W97_AUDITFIX", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0


def votes(D, mem, bmom, tilt, ctx, chan):
    """(long_target, short_target) for the frozen object with `chan` in the OR slot."""
    n, tarr, sid = D["n"], D["t"], D["sid"]
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx = {v: k for k, v in enumerate(L13)}

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
    TG = {}
    for name, vols in MEMBERS.items():
        cols = [idx[v] for v in vols]
        s_ = mem[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        TG[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))

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


def sfills_perctr(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0):
    """M8's isolation control: identical to sfills EXCEPT the session box accumulates
    PER-CONTRACT P&L, so a size-2 entry does not trip the halt at half the point move."""
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
                spnl += pnl / u                                   # <-- PER CONTRACT
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


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "auditfix.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ============================================================== M10: ONE deep baseline
    P_("=" * 120)
    P_("=== M10: P1 / 2:3 pair / NETFUSE_1 on 2006-2021 in ONE RUN - a shared baseline BY")
    P_("===      CONSTRUCTION. W87 and W93 used different P1 deep series; only one can be right.")
    P_("=" * 120)
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    nd, td, sidd, lbd = DD["n"], DD["t"], DD["sid"], DD["lb"]
    XD = fast_build_context(DD)
    cache = os.path.join(W80OUT, f"mem_deep_{nd}.npz")
    zz = np.load(cache); memd, bmomd, tiltd = zz["mem"], zz["bmom"], zz["tilt"]
    P_(f"    deep substrate {nd:,} bars / {DD['n_sess']:,} sessions "
       f"[cache {os.path.basename(cache)}] [{_time.time()-t0:.0f}s]")
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

    def pand(v):
        w = pd.Series(v).groupby(wkd).sum().to_numpy()
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), net=float(np.sum(v)))

    def long_objd(chan):
        vl, _ = votes(DD, memd, bmomd, tiltd, XD, chan)
        p = vl.astype(np.int8)
        bb = fills_daily(DD, p, halt=1300, target=1000)
        ee = np.array([i_ofd(x["et"]) for x in bb])
        s_, _ = causal_score(XD, ee, window=WIN)
        return fills_qexit(DD, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_)

    CHd = build_channels(DD, which=["X9a_disp_sessanchor"])
    flatd = td >= DD["sess_end"][sidd] - np.timedelta64(21 * 60, "s")
    TRd = {}
    TRd["P1"] = long_objd(bmomd)
    TRd["X9a"] = long_objd(CHd["X9a_disp_sessanchor"])
    TRd["BMOM"] = sfills(DD, np.where(flatd, 0, bmomd).astype(np.int8), halt=1300.0, target=1000.0)
    vl, vs = votes(DD, memd, bmomd, tiltd, XD, bmomd)
    tgd = np.where(vl & vs, 0, np.where(vl, 1, np.where(vs, -1, 0))).astype(np.int8)
    TRd["NETFUSE_1"] = sfills(DD, tgd, halt=1300.0, target=1000.0)
    P_(f"    four deep objects built [{_time.time()-t0:.0f}s]")
    SERd = {k: dailyd(v) for k, v in TRd.items()}
    CMd = {k: cmind(v) for k, v in TRd.items()}
    SERd["PAIR23"] = (2 * SERd["BMOM"] + 3 * SERd["X9a"]) / 5.0
    CMd["PAIR23"] = (2 * CMd["BMOM"] + 3 * CMd["X9a"]) / 5.0
    TRd_n = {k: len(v) for k, v in TRd.items()}
    TRd_n["PAIR23"] = 2 * TRd_n["BMOM"] + 3 * TRd_n["X9a"]

    P_("")
    P_(f"{'object':<12}{'trades':>9}{'ctr-min':>12}{'net $':>13}{'wk+%':>8}{'maxDD':>11}"
       f"{'top5DD':>10}{'worst':>10}{'strk':>6}")
    for k in ("P1", "BMOM", "X9a", "PAIR23", "NETFUSE_1"):
        a = pand(SERd[k])
        P_(f"{k:<12}{TRd_n[k]:>9,}{CMd[k]:>12,.0f}{a['net']:>13,.0f}{a['wkpos']:>7.1f}%"
           f"{a['maxdd']:>11,.0f}{a['top5']:>10,.0f}{a['worst']:>10,.0f}{a['streak']:>6}")
    aP = pand(SERd["P1"])
    P_("")
    P_("    Which committed P1 does this rebuild agree with?")
    P_(f"      THIS RUN        top5 {aP['top5']:>11,.3f}  maxdd {aP['maxdd']:>11,.2f}  "
       f"net {aP['net']:>11,.2f}  wkpos {aP['wkpos']:.3f}")
    for tag, path in (("W87 deep.csv", os.path.join(ROOT, "runs", "WE_W87_DEEPPAIR", "out",
                                                    "deep.csv")),
                      ("W93 deep.csv", os.path.join(ROOT, "runs", "WE_W93_NETFUSE", "out",
                                                    "deep.csv"))):
        t = pd.read_csv(path)
        col = t.columns[0]
        row = t[t[col].astype(str).str.contains("P1")].iloc[0]
        P_(f"      {tag:<15} top5 {row['top5']:>11,.3f}  maxdd {row['maxdd']:>11,.2f}  "
           f"net {row['net']:>11,.2f}  wkpos {row['wkpos']:.3f}")

    P_("")
    P_("    THE BAR (W87's, >= 25 % smaller mean top-5 drawdown than P1) - on ONE baseline:")
    P_(f"{'object':<12}{'NOMINAL exposure':>20}{'INCOME-matched':>18}")
    rows = []
    for k in ("PAIR23", "NETFUSE_1"):
        a = pand(SERd[k])
        red_nom = 100 * (1 - a["top5"] / aP["top5"])
        s = aP["weekly"] / a["weekly"] if abs(a["weekly"]) > 1e-9 else np.nan
        ai = pand(SERd[k] * s) if np.isfinite(s) else None
        red_inc = 100 * (1 - ai["top5"] / aP["top5"]) if ai else np.nan
        P_(f"{k:<12}{red_nom:>19.1f}%{red_inc:>17.1f}%")
        rows.append(dict(obj=k, red_nominal=red_nom, red_income=red_inc,
                         income_scale=s, **a))
    rows.append(dict(obj="P1", red_nominal=0.0, red_income=0.0, income_scale=1.0, **aP))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "deep_common_baseline.csv"), index=False)
    pd.DataFrame({"date": dsd.strftime("%Y-%m-%d"),
                  **{k: SERd[k] for k in SERd}}).to_csv(
        os.path.join(OUT, "deep_series.csv"), index=False)

    # ============================================================== M3: the clock control
    P_("")
    P_("=" * 120)
    P_("=== M3: IS THE LOW rho THE CLOCK, OR IS IT SIGNAL SHARING?")
    P_("===     Split each object's daily P&L by ENTRY SEGMENT and correlate WEEKLY vs BMOM.")
    P_("=" * 120)
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")
    CH = build_channels(D, which=["X9a_disp_sessanchor"])

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    def daily_seg(trl, seg):
        """daily P&L restricted to trades ENTERED in a given segment"""
        sp = np.zeros(D["n_sess"])
        for x in trl:
            m_ = pd.Timestamp(x["et"]).hour * 60 + pd.Timestamp(x["et"]).minute
            rth = 570 <= m_ < 960
            if seg == "RTH" and not rth:
                continue
            if seg == "ON" and rth:
                continue
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def long_obj(chan):
        vl_, _ = votes(D, mem, bmom, tilt, X, chan)
        p = vl_.astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return keep(fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_))
    TRm = {"P1": long_obj(bmom), "X9a": long_obj(CH["X9a_disp_sessanchor"]),
           "SOLAR": long_obj(np.zeros(n, np.int8))}
    TRm["BMOM"] = keep(sfills(D, np.where(flatm, 0, bmom).astype(np.int8),
                              halt=1300.0, target=1000.0))

    def wkv(v):
        return pd.Series(v).groupby(wk).sum().to_numpy()
    bmw = wkv(daily_seg(TRm["BMOM"], "ALL"))
    P_("")
    P_(f"{'series':<20}{'RTH share of net':>18}{'weekly rho vs BMOM':>22}{'z':>8}")
    crows = []
    for k in ("P1", "X9a", "SOLAR"):
        allp = daily_seg(TRm[k], "ALL")
        for seg in ("ALL", "RTH", "ON"):
            v = daily_seg(TRm[k], seg)
            if abs(v).sum() < 1e-9:
                continue
            r = float(np.corrcoef(wkv(v), bmw)[0, 1])
            share = 100 * v.sum() / allp.sum() if allp.sum() else np.nan
            zz_ = r * np.sqrt(len(bmw) - 3)
            P_(f"{k+'_'+seg:<20}{share:>17.1f}%{r:>22.4f}{zz_:>8.2f}")
            crows.append(dict(obj=k, seg=seg, rho=r, z=zz_))
        P_("")
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "clock_control.csv"), index=False)
    P_("    THE TEST: if the low rho is TEMPORAL DISJOINTNESS, X9a_RTH - which shares BMOM's")
    P_("    clock completely - must correlate strongly with BMOM. If it is SIGNAL SHARING,")
    P_("    X9a_RTH stays near zero (X9a has no bmom channel) while P1_RTH is elevated.")

    # ============================================================== M8: isolation control
    P_("")
    P_("=" * 120)
    P_("=== M8: DOES THE QUALITY LAYER HURT, OR IS IT THE EXIT POLICY?")
    P_("===     sfills' box is a DOLLAR limit on TOTAL position P&L, so a size-2 entry trips the")
    P_("===     -$1,300 halt at half the point move. Control: box accumulates PER CONTRACT.")
    P_("=" * 120)
    vl2, vs2 = votes(D, mem, bmom, tilt, X, bmom)
    tgtN = np.where(vl2 & vs2, 0, np.where(vl2, 1, np.where(vs2, -1, 0))).astype(np.int8)
    bb = fills_daily(D, np.abs(tgtN).astype(np.int8), halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sq, _ = causal_score(X, ee, window=WIN)
    szq = np.where((tgtN > 0) & (sq >= 3), 2, 1).astype(np.int8)
    ARM = {
        "NETFUSE_1": keep(sfills(D, tgtN, halt=1300.0, target=1000.0)),
        "NETFUSE_Q (published)": keep(sfills(D, tgtN, size_at_entry=szq,
                                             halt=1300.0, target=1000.0)),
        "NETFUSE_QN (per-ctr box)": keep(sfills_perctr(D, tgtN, size_at_entry=szq,
                                                       halt=1300.0, target=1000.0)),
        "NETFUSE_1N (per-ctr box)": keep(sfills_perctr(D, tgtN, halt=1300.0, target=1000.0)),
    }

    def cmin(t):
        v = np.zeros(n)
        for x in t:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return float(v.sum())

    def daily(t):
        sp = np.zeros(D["n_sess"])
        for x in t:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]
    NWk = len(set(wk))

    def pan(v, cw):
        w = wkv(v) - cw
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    top5=dp["dd_mean_top5"], maxdd=dp["maxdd"], streak=int(stk),
                    worst=float(w.min()),
                    weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    t=float(w.mean()) / max(w.std(ddof=1) / np.sqrt(len(w)), 1e-9))
    ref = cmin(ARM["NETFUSE_1"])
    P_("")
    P_(f"{'arm':<26}{'trades':>8}{'ctr':>7}{'scale':>7}{'wk$@fixDD':>11}{'wk+%':>8}"
       f"{'top5DD':>9}{'strk':>6}{'t':>7}{'2026 wk$':>10}")
    y26 = np.asarray(sdate.year == 2026)
    arows = []
    for k, trl in ARM.items():
        s = ref / cmin(trl)
        ser = daily(trl) * s
        cw = 14.52 * sum(x["u"] for x in trl) / NWk * s
        a = pan(ser, cw)
        w26 = pd.Series(ser[y26]).groupby(wk[y26]).sum().to_numpy() - cw
        P_(f"{k:<26}{len(trl):>8,}{sum(x['u'] for x in trl):>7,}{s:>7.3f}"
           f"{a['weekly_dd']:>11,.0f}{a['wkpos']:>7.2f}%{a['top5']:>9,.0f}{a['streak']:>6}"
           f"{a['t']:>7.2f}{w26.mean():>10,.0f}")
        arows.append(dict(arm=k, trades=len(trl), contracts=sum(x["u"] for x in trl),
                          scale=s, y26=float(w26.mean()), **a))
    pd.DataFrame(arows).to_csv(os.path.join(OUT, "m8_isolation.csv"), index=False)
    P_("")
    P_("    Compare NETFUSE_QN against NETFUSE_1N - both per-contract box, so the ONLY")
    P_("    difference is the sizing layer. That is the isolated effect of quality sizing.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
