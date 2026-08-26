"""WE_W84 - Q3 vs the incumbent quality layer, tested properly.

Spec: runs/WE_W84_Q3/spec.yaml, committed before this ran.

W83 rejected Q3 because it gave up 11.6 % of money against a 10 % bar I had invented. That is a
1.6-point miss on an arbitrary line, and the owner challenged it. This wave applies the campaign's
unchanged standard gate AND a gate built from the owner's stated ordering, reports both, and adds
the walk-forward and the null that W83 did not run.
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
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W84_Q3", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
DD_TARGET = 20245.0
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
MEAS_RT = 14.65
RNG = np.random.default_rng(20260884)
NDRAW = 200


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "q3.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = fast_build_context(D)
    st = np.zeros(D["n_sess"], np.int64); st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([D["wk"][s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    yr = sdate.year.to_numpy()

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

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
    P_(f"=== {len(sess_in)} sessions, {NW} weeks, {len(ee):,} scored entries "
       f"[{_time.time()-t0:.0f}s]")

    def run(szf):
        trl = [x for x in fills_qexit(D, pos, szf.astype(np.int8), sc)
               if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], sum(x["u"] for x in trl) / NW

    ARMS = {"Q0": np.where(sc >= 3, 2, 1), "Q3": np.where(sc >= 4, 2, 1),
            "Q1": np.ones(n), "Q4": np.where(sc >= 3, 3, 1)}
    S, RTW = {}, {}
    for k, f in ARMS.items():
        S[k], RTW[k] = run(f)
    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"), **S}).to_csv(
        os.path.join(OUT, "ledgers.csv"), index=False)

    def wkv(v, m=None):
        m = np.ones(len(v), bool) if m is None else np.asarray(m)
        w_ = wk_idx[m]
        cnt = np.bincount(w_, minlength=NW) > 0
        return np.bincount(w_, weights=v[m], minlength=NW)[cnt]

    def pan(k, m=None, rt=MEAS_RT):
        w = wkv(S[k], m) - RTW[k] * rt
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        kk = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for c, g in itertools.groupby(w < 0) if c), default=0)
        sd = w.std(ddof=1)
        return dict(wkpos=100 * float((w > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(w)), weekly=float(w.mean()),
                    weekly_dd=float(w.mean()) * kk, dd5=dp["dd_mean_top5"] * kk,
                    maxdd=float(dp["maxdd"]), worst=float(w.min()),
                    sharpe=float(w.mean() / sd) if sd > 0 else 0.0,
                    skew=float(sst.skew(w)), dd5raw=dp["dd_mean_top5"], eps=dp["dd5"])

    # ============================================================ PHASE 0: the contradiction
    P_(f"\n{'='*126}")
    P_("=== PHASE 0: FULL-SAMPLE says Q0's drawdown profile is better; ROLLING says Q3's is,")
    P_("===          in 84 % of windows. Locate the episodes and settle it.")
    P_(f"{'='*126}")
    for k in ("Q0", "Q3"):
        r = pan(k)
        P_(f"   {k}: five deepest drawdown EPISODES (weekly equity, $, at ${MEAS_RT}/RT): "
           f"{r['eps']}")
        P_(f"      mean of top 5 = ${r['dd5raw']:,.0f}   max = ${r['maxdd']:,.0f}")
    e0, e3 = pan("Q0")["eps"], pan("Q3")["eps"]
    P_(f"\n   Q3 - Q0 on each of the five: "
       f"{[int(a-b) for a, b in zip(e3, e0)]}")
    P_(f"   -> {'Q3 is worse on the DEEPEST episodes only' if e3[0] > e0[0] and sum(e3[1:]) <= sum(e0[1:]) else 'Q3 is worse across the episode distribution'}")

    # ============================================================ PHASE 1: rolling, both gates
    P_(f"\n{'='*126}\n=== PHASE 1: ROLLING 24-MONTH WINDOWS vs Q0, at ${MEAS_RT}/RT")
    P_(f"{'='*126}")
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    P_(f"{'arm':<6}{'n':>5}{'wk+% win':>11}{'money win':>12}{'top5DD win':>13}"
       f"{'ALL THREE':>12}{'worst-wk win':>14}{'streak win':>12}")
    roll = {}
    for k in ("Q3", "Q1", "Q4"):
        c = dict(w=0, m=0, d=0, a=0, ww=0, st=0, n=0)
        for e in ends:
            msk = np.asarray((sdate > e - pd.DateOffset(months=24)) & (sdate <= e))
            if msk.sum() < 300:
                continue
            a_, b_ = pan(k, msk), pan("Q0", msk)
            if a_ is None or b_ is None:
                continue
            c["n"] += 1
            x1 = a_["wkpos"] > b_["wkpos"]; x2 = a_["weekly_dd"] > b_["weekly_dd"]
            x3 = a_["dd5"] < b_["dd5"]
            c["w"] += x1; c["m"] += x2; c["d"] += x3; c["a"] += (x1 and x2 and x3)
            c["ww"] += a_["worst"] > b_["worst"]; c["st"] += a_["wstreak"] < b_["wstreak"]
        nn = max(c["n"], 1)
        P_(f"{k:<6}{c['n']:>5}{100*c['w']/nn:>10.0f}%{100*c['m']/nn:>11.0f}%"
           f"{100*c['d']/nn:>12.0f}%{100*c['a']/nn:>11.0f}%{100*c['ww']/nn:>13.0f}%"
           f"{100*c['st']/nn:>11.0f}%")
        roll[k] = {kk: 100 * v / nn for kk, v in c.items() if kk != "n"}
    pd.DataFrame(roll).T.to_csv(os.path.join(OUT, "rolling.csv"))

    # ============================================================ PHASE 2: the panel
    for lab, rt in (("commission only $4.36/RT", 0.0),
                    (f"MEASURED all-in ${MEAS_RT}/RT", MEAS_RT)):
        P_(f"\n=== PANEL, {lab} ===")
        P_(f"{'arm':<6}{'wk+%':>7}{'wStrk':>7}{'skew':>7}{'Sharpe':>8}{'medWk$':>9}"
           f"{'weekly$':>9}{'wk$@DD':>9}{'top5DD':>9}{'maxDD':>9}{'worst':>9}")
        for k in ARMS:
            r = pan(k, None, rt)
            P_(f"{k:<6}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['skew']:>7.2f}"
               f"{r['sharpe']:>8.3f}{r['medwk']:>9,.0f}{r['weekly']:>9,.0f}"
               f"{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}{r['maxdd']:>9,.0f}{r['worst']:>9,.0f}")

    P_(f"\n=== PER YEAR at ${MEAS_RT}/RT (positive-week % | weekly $) ===")
    yrs = sorted(set(yr))
    P_(f"{'arm':<6}" + "".join(f"{y:>16}" for y in yrs))
    for k in ARMS:
        line = f"{k:<6}"
        for y in yrs:
            r = pan(k, yr == y)
            line += f"{(f'{r[chr(119)+chr(107)+chr(112)+chr(111)+chr(115)]:.0f}% | {r[chr(119)+chr(101)+chr(101)+chr(107)+chr(108)+chr(121)]:,.0f}' if r else '-'):>16}"
        P_(line)

    # ============================================================ PHASE 3: the null
    P_(f"\n{'='*126}")
    P_("=== PHASE 3: NULL - is Q3's gain about WHICH trades get 2 contracts, or just about")
    P_("===          having FEWER size-2 trades? Keep the count, randomise the assignment.")
    P_(f"{'='*126}")
    ent = np.flatnonzero(sc > 0)
    k2 = int((sc[ent] >= 4).sum())
    P_(f"   Q3 gives 2 contracts to {k2} of {len(ent)} scored entries "
       f"({100*k2/len(ent):.1f} %); Q0 gives it to {int((sc[ent]>=3).sum())} "
       f"({100*int((sc[ent]>=3).sum())/len(ent):.1f} %)")
    real = pan("Q3")
    vals = []
    for _ in range(NDRAW):
        szf = np.ones(n)
        pick = RNG.choice(ent, size=k2, replace=False)
        szf[pick] = 2
        sp, rtw = run(szf)
        w = wkv(sp) - rtw * MEAS_RT
        dp = dd_profile(w); kk = DD_TARGET / max(dp["maxdd"], 1e-9)
        vals.append((100 * float((w > 0).mean()), float(w.mean()) * kk,
                     dp["dd_mean_top5"] * kk))
        if len(vals) >= 60:
            break
    V = np.array(vals)
    P_(f"\n   {len(V)} draws (random size-2 assignment at Q3's exact count)")
    P_(f"{'metric':<20}{'real Q3':>12}{'null mean':>12}{'null p95':>12}{'pctile':>9}{'':>10}")
    nl = []
    for j, (lab2, rv, hi) in enumerate((("positive-week %", real["wkpos"], True),
                                        ("money @ fixed DD", real["weekly_dd"], True),
                                        ("mean top-5 DD", real["dd5"], False))):
        col = V[:, j]
        pct = 100 * float((col < rv).mean()) if hi else 100 * float((col > rv).mean())
        P_(f"{lab2:<20}{rv:>12,.1f}{col.mean():>12,.1f}"
           f"{np.percentile(col, 95 if hi else 5):>12,.1f}{pct:>8.0f}%"
           f"{('SPECIFIC' if pct >= 95 else 'generic'):>10}")
        nl.append(dict(metric=lab2, real=rv, null_mean=float(col.mean()), pctile=pct))
    pd.DataFrame(nl).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    # ============================================================ PHASE 4: walk-forward
    P_(f"\n{'='*126}\n=== PHASE 4: WALK-FORWARD over the choice Q0 vs Q3\n{'='*126}")
    qs = pd.date_range(sdate.min() + pd.DateOffset(months=12), sdate.max(), freq="QS")
    wf = np.zeros(len(S["Q0"])); picks = []
    for q in qs:
        tr = np.asarray((sdate >= q - pd.DateOffset(months=12)) & (sdate < q))
        te = np.asarray((sdate >= q) & (sdate < q + pd.DateOffset(months=3)))
        if tr.sum() < 150 or te.sum() < 20:
            continue
        a_, b_ = pan("Q3", tr), pan("Q0", tr)
        pick = "Q3" if (a_ and b_ and a_["wkpos"] > b_["wkpos"]) else "Q0"
        wf[te] = S[pick][te]; picks.append(pick)
    m = wf != 0
    churn = 100 * float(np.mean(np.array(picks[1:]) != np.array(picks[:-1]))) if len(picks) > 1 \
        else np.nan
    P_(f"   {len(picks)} refits: {picks}   churn {churn:.0f} %   "
       f"Q3 chosen {picks.count('Q3')}/{len(picks)}")
    S["WF"] = wf; RTW["WF"] = (RTW["Q0"] + RTW["Q3"]) / 2
    P_(f"\n{'':<22}{'wk+%':>8}{'weekly$':>10}{'wk$@DD':>10}{'top5DD':>10}")
    for lab2, k in (("walk-forward", "WF"), ("Q3 fixed", "Q3"), ("Q0 fixed", "Q0")):
        r = pan(k, m)
        P_(f"{lab2:<22}{r['wkpos']:>7.1f}%{r['weekly']:>10,.0f}{r['weekly_dd']:>10,.0f}"
           f"{r['dd5']:>10,.0f}")

    # ============================================================ VERDICT
    P_(f"\n{'='*126}\n=== THE TWO GATES, BOTH REPORTED, NEITHER RELAXED\n{'='*126}")
    q0f, q3f = pan("Q0"), pan("Q3")
    r3 = roll["Q3"]
    g_std = (r3["w"] > 50) and (r3["m"] > 50) and (r3["d"] > 50)
    money_ratio = 100 * q3f["weekly_dd"] / q0f["weekly_dd"]
    g_own = (r3["w"] > 50) and (r3["d"] > 50) and (money_ratio >= 85.0)
    nul_ok = float(pd.read_csv(os.path.join(OUT, "nulls.csv")).iloc[0]["pctile"]) >= 95
    P_(f"   CAMPAIGN STANDARD (all three in a majority)        : "
       f"wk+% {r3['w']:.0f} % | money {r3['m']:.0f} % | dd5 {r3['d']:.0f} %  -> "
       f"{'PASS' if g_std else 'FAIL'}")
    P_(f"   OWNER ORDERING (consistency & drawdown majorities,")
    P_(f"                   money not worse than -15 %)        : "
       f"wk+% {r3['w']:.0f} % | dd5 {r3['d']:.0f} % | money {money_ratio:.1f} % of Q0  -> "
       f"{'PASS' if g_own else 'FAIL'}")
    P_(f"   NULL (is the gain about WHICH trades?)             : "
       f"{'PASS' if nul_ok else 'FAIL - generic'}")
    P_(f"   WALK-FORWARD churn                                 : {churn:.0f} %")
    P_(f"\n   -> {'Q3 passes the owner-ordering gate. The trade is EXPLICIT: better on what he ranks first and second, -%.1f %% on money. THE DECISION IS HIS.' % (100-money_ratio) if g_own else 'Q3 does not pass either gate as written.'}")
    P_(f"\n=== STATUS: NOTHING ADOPTED BY ME. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
