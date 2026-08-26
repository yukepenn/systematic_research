"""WE_W83 - does the quality SIZING layer hurt the owner's actual objective?

Spec: runs/WE_W83_SKEWLEVER/spec.yaml, committed before this ran.

W42: the score forecasts EXCURSION SIZE, not hit rate. So sizing up on score>=3 concentrates
contracts on the fattest-right-tail trades and ADDS positive skew.
W74: one unit of weekly skew costs 2.99 pp of positive weeks, and P1's +2.11 skew is costing ~6.3.
W39 validated the layer on PRODUCTION and TAIL. Never on the owner's primary metric.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd
from scipy import stats as sst

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W83_SKEWLEVER", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
DD_TARGET = 20245.0
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
MEAS_RT = 14.65                       # W82's measured all-in spread cost per round turn
# W74's frozen exchange rate, fitted on 216 cells, held out on 19 objects (R2 +0.277)
W74_B0, W74_BS, W74_BK = 48.07, 45.41, -2.99


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "skew.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = fast_build_context(D)
    st = np.zeros(D["n_sess"], np.int64); st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([D["wk"][s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    yr = sdate.year.to_numpy()
    P_(f"=== {NS} sessions, {NW} weeks, {sdate.min().date()} -> {sdate.max().date()} "
       f"[{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    # ------------------------------------------------------------------ the shared object
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
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

    vs = []
    for name, vols in MEMBERS.items():
        cols = [idx_l13[v] for v in vols]
        s_ = mem[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        tg = hyst(0.7086 * Tp + 2.83 * bmom.astype(float))
        for q_ in QS:
            okv = np.ones(n, bool) if q_ is None else ((X["norm"] <= 0) | (X["ratio"] >= q_))
            for dg in (True, False):
                vs.append(np.where((tg > 0) & (okv & (X["dL"] if dg else True)), 1,
                                   0).astype(np.int8))
    pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
    del vs
    base = fills_daily(D, pos, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    P_(f"    object + causal score built; {len(ee):,} scored entries [{_time.time()-t0:.0f}s]")

    ARMS = {
        "Q0_incumbent": np.where(sc >= 3, 2, 1),
        "Q1_flat":      np.ones(n),
        "Q2_inverted":  np.where(sc <= 1, 2, 1),
        "Q3_selective": np.where(sc >= 4, 2, 1),
        "Q4_levered":   np.where(sc >= 3, 3, 1),
        "Q5_graded":    np.clip(np.round(1 + sc / 2.5), 1, 3),
    }

    def run(szf):
        trl = [x for x in fills_qexit(D, pos, szf.astype(np.int8), sc)
               if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], trl

    def wkv(v, m=None):
        m = np.ones(len(v), bool) if m is None else np.asarray(m)
        w_ = wk_idx[m]
        cnt = np.bincount(w_, minlength=NW) > 0
        return np.bincount(w_, weights=v[m], minlength=NW)[cnt]

    def pan(v, m=None, rt_wk=0.0):
        w = wkv(v, m) - rt_wk
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for kk, g in itertools.groupby(w < 0) if kk), default=0)
        sd = w.std(ddof=1)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(w)), weekly=float(w.mean()),
                    weekly_dd=float(w.mean()) * k, dd5=dp["dd_mean_top5"] * k,
                    maxdd=float(dp["maxdd"]), worst=float(w.min()),
                    sharpe=float(w.mean() / sd) if sd > 0 else 0.0,
                    skew=float(sst.skew(w)))

    RES, LED = {}, {}
    for k, szf in ARMS.items():
        sp, trl = run(szf)
        rts = sum(x["u"] for x in trl)
        LED[k] = sp
        RES[k] = dict(arm=k, ntr=len(trl), rts=rts, rt_wk=rts / NW,
                      contracts=float(np.mean([x["u"] for x in trl])),
                      sp=sp)
        P_(f"    {k:<14} {len(trl):>5,} trades, {rts:>6,} contract RTs, "
           f"{rts/NW:>5.2f} RT/week [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------- PHASE 0: the falsifier
    P_(f"\n{'='*130}\n=== PHASE 0: THE FALSIFIER. Does the sizing scheme actually move the "
       f"weekly SKEW?")
    P_(f"{'='*130}")
    P_(f"{'arm':<16}{'avg size':>10}{'RT/week':>10}{'weekly skew':>14}{'kurtosis':>11}")
    for k in ARMS:
        r = RES[k]
        p0 = pan(r["sp"])
        w = wkv(r["sp"])
        P_(f"{k:<16}{r['contracts']:>10.2f}{r['rt_wk']:>10.2f}{p0['skew']:>14.2f}"
           f"{float(sst.kurtosis(w)):>11.2f}")
        RES[k]["skew"] = p0["skew"]
    sk = np.array([RES[k]["skew"] for k in ARMS])
    spread = float(sk.max() - sk.min())
    P_(f"\n   skew spread across arms: {spread:.2f} units -> "
       f"{'PREMISE HOLDS' if spread >= 0.5 else 'PREMISE FALSIFIED (< 0.5)'}")
    order_ok = RES["Q2_inverted"]["skew"] < RES["Q1_flat"]["skew"] < RES["Q0_incumbent"]["skew"] \
        < RES["Q4_levered"]["skew"]
    P_(f"   predicted ordering Q2 < Q1 < Q0 < Q4 "
       f"({RES['Q2_inverted']['skew']:.2f} < {RES['Q1_flat']['skew']:.2f} < "
       f"{RES['Q0_incumbent']['skew']:.2f} < {RES['Q4_levered']['skew']:.2f}) -> "
       f"{'CONFIRMED' if order_ok else 'SCRAMBLED - the W42 mechanism is not what drives skew here'}")

    # ------------------------------------------------------------- rolling FIRST
    P_(f"\n{'='*130}\n=== PHASE 1 (BEFORE any full-sample table is interpreted): ROLLING "
       f"24-MONTH WINDOWS vs Q0, at the MEASURED ${MEAS_RT}/RT")
    P_(f"{'='*130}")
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    P_(f"{'arm':<16}{'n':>5}{'wk+% win':>11}{'money win':>12}{'top5DD win':>13}"
       f"{'ALL THREE':>12}")
    roll = []
    for k in ARMS:
        if k == "Q0_incumbent":
            continue
        c1 = c2 = c3 = ca = nn = 0
        for e in ends:
            m = np.asarray((sdate > e - pd.DateOffset(months=24)) & (sdate <= e))
            if m.sum() < 300:
                continue
            fa = RES[k]["rt_wk"] * MEAS_RT
            fb_ = RES["Q0_incumbent"]["rt_wk"] * MEAS_RT
            a_ = pan(RES[k]["sp"], m, fa); b_ = pan(RES["Q0_incumbent"]["sp"], m, fb_)
            if a_ is None or b_ is None:
                continue
            nn += 1
            x1 = a_["wkpos"] > b_["wkpos"]; x2 = a_["weekly_dd"] > b_["weekly_dd"]
            x3 = a_["dd5"] < b_["dd5"]
            c1 += x1; c2 += x2; c3 += x3; ca += (x1 and x2 and x3)
        P_(f"{k:<16}{nn:>5}{100*c1/max(nn,1):>10.0f}%{100*c2/max(nn,1):>11.0f}%"
           f"{100*c3/max(nn,1):>12.0f}%{100*ca/max(nn,1):>11.0f}%")
        roll.append(dict(arm=k, n=nn, wkpos=100 * c1 / max(nn, 1),
                         money=100 * c2 / max(nn, 1), dd=100 * c3 / max(nn, 1),
                         all3=100 * ca / max(nn, 1)))
    RO = pd.DataFrame(roll); RO.to_csv(os.path.join(OUT, "rolling.csv"), index=False)

    # ------------------------------------------------------------- the panel, both frictions
    for lab, rtc in (("net $4.36/RT commission only", 0.0),
                     (f"at W82's MEASURED ${MEAS_RT}/RT all-in", MEAS_RT)):
        P_(f"\n{'='*130}\n=== PHASE 2: the panel, {lab}\n{'='*130}")
        P_(f"{'arm':<16}{'wk+%':>7}{'wStrk':>7}{'skew':>7}{'Sharpe':>8}{'medWk$':>9}"
           f"{'weekly$':>9}{'wk$@DD':>9}{'top5DD':>9}{'maxDD':>9}{'worst':>9}"
           f"{'W74 pred wk+%':>15}")
        rows = []
        for k in ARMS:
            r = pan(RES[k]["sp"], None, RES[k]["rt_wk"] * rtc)
            pred = W74_B0 + W74_BS * r["sharpe"] + W74_BK * r["skew"]
            P_(f"{k:<16}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['skew']:>7.2f}"
               f"{r['sharpe']:>8.3f}{r['medwk']:>9,.0f}{r['weekly']:>9,.0f}"
               f"{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}{r['maxdd']:>9,.0f}"
               f"{r['worst']:>9,.0f}{pred:>14.1f}%")
            rows.append(dict(arm=k, friction=rtc, **r, w74_pred=pred))
        if rtc > 0:
            R2 = pd.DataFrame(rows)
            err = R2["w74_pred"] - R2["wkpos"]
            P_(f"\n   W74's exchange rate on this NEW family (not in its fit or its hold-out):")
            P_(f"      MAE {np.abs(err).mean():.2f} pp, bias {err.mean():+.2f} pp, "
               f"R2 {1-(err**2).sum()/((R2['wkpos']-R2['wkpos'].mean())**2).sum():+.3f}")
            R2.to_csv(os.path.join(OUT, "panel.csv"), index=False)

    P_(f"\n=== PER YEAR (positive-week %, at ${MEAS_RT}/RT) ===")
    yrs = sorted(set(yr))
    P_(f"{'arm':<16}" + "".join(f"{y:>10}" for y in yrs))
    for k in ARMS:
        line = f"{k:<16}"
        for y in yrs:
            r = pan(RES[k]["sp"], yr == y, RES[k]["rt_wk"] * MEAS_RT)
            line += f"{(f'{r[chr(119)+chr(107)+chr(112)+chr(111)+chr(115)]:.0f}%' if r else '-'):>10}"
        P_(line)

    # ------------------------------------------------------------- verdict
    P_(f"\n{'='*130}\n=== PREREGISTERED VERDICT\n{'='*130}")
    q0 = pan(RES["Q0_incumbent"]["sp"], None, RES["Q0_incumbent"]["rt_wk"] * MEAS_RT)
    cand = []
    for _, r in RO.iterrows():
        rr = pan(RES[r["arm"]]["sp"], None, RES[r["arm"]]["rt_wk"] * MEAS_RT)
        keep = (r["wkpos"] > 50) and (rr["weekly_dd"] >= 0.90 * q0["weekly_dd"])
        P_(f"   {r['arm']:<16} wk+% wins {r['wkpos']:>3.0f} % of windows | "
           f"money at fixed DD {100*rr['weekly_dd']/q0['weekly_dd']:>5.1f} % of Q0 -> "
           f"{'CANDIDATE' if keep else 'no'}")
        if keep:
            cand.append(r["arm"])
    P_(f"\n   the layer's measured price, Q0 vs Q1 (layer OFF), at ${MEAS_RT}/RT:")
    q1 = pan(RES["Q1_flat"]["sp"], None, RES["Q1_flat"]["rt_wk"] * MEAS_RT)
    P_(f"      positive weeks  {q0['wkpos']:.1f} % vs {q1['wkpos']:.1f} %  "
       f"({q0['wkpos']-q1['wkpos']:+.1f} pp)")
    P_(f"      weekly skew     {q0['skew']:+.2f} vs {q1['skew']:+.2f}  "
       f"({q0['skew']-q1['skew']:+.2f})")
    P_(f"      money @ fixed DD ${q0['weekly_dd']:,.0f} vs ${q1['weekly_dd']:,.0f}  "
       f"({100*q0['weekly_dd']/max(q1['weekly_dd'],1e-9)-100:+.1f} %)")
    P_(f"\n   -> {'CANDIDATES: ' + ', '.join(cand) if cand else 'NO ARM CLEARS THE BAR. The layer stands.'}")
    P_(f"\n=== STATUS: NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
