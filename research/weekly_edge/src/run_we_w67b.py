"""WE_W67 phase 2/3 - what phase 1 forces us to ask.

Phase 1 enumerated the combiner exactly and found that the six inherited constants collapse to
this: entry needs 6 of 13 members net-long normally, 5 with tilt agreement, and ONE - 7.7 % - as
soon as B-MOM agrees. Empirically B-MOM was long at 37.3 % of all long entries and the median
entry has only 5 of 13 members agreeing, with a 10th percentile of 1.

So the object this campaign has described for 67 waves as "a selection-free majority vote over
32 long-only Solar configurations" is in fact a Solar ensemble OR-GATED WITH B-MOM. And B-MOM
standalone was PARKED AS REGIME-LOCAL by the scalping lab (PF 1.013 over 16 unseen years) and
re-measured as a 4-year in-sample result by W57.

This file asks the two questions that follow, and both are attribution rather than search:
  A. how much of P1's money comes from B-MOM-enabled entries versus member-consensus entries?
  B. how does the object behave across the B-MOM weight, from 0 (Solar only) to 4.2 (B-MOM
     alone clears the entry level, so the members stop mattering)?
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
from run_we_w01 import ROOT, PV, round_away                              # noqa: E402
from run_we_w19 import QS                                                # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import WIDE                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W67_COMBINER", "out")
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
BASE = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
CUTS = (14, 16, 18, 10 ** 9)
DD_TARGET = 20245.0
BMOM_W = (0.0, 1.0, 2.0, 2.83, 4.2)


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "combiner2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]

    z = np.load(os.path.join(W66OUT, f"mem460_clamp_{D['n']}.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    idx_of = {v: k for k, v in enumerate(WIDE)}
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flat = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def targets(cols, w_bmom):
        s = mem[:, cols].sum(axis=1).astype(np.int32)
        nm = len(cols)
        T = np.clip(ra(s / float(nm) * 10.0), -10, 10)
        agree = (np.sign(s) == tilt) & (s != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(agree, 1.25, 1.0) * 0.9026), -13, 13)
        M = 0.7086 * Tp + w_bmom * bmom.astype(float)
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flat[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    if M[i] >= 3.0:
                        g = 1
                    elif M[i] <= -3.0:
                        g = -1
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tgt[i] = g
        return tgt

    def build(w_bmom):
        vs = []
        for cut in CUTS:
            vms = [v for v in BASE if v <= cut]
            tg = targets([idx_of[v] for v in vms], w_bmom)
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 150:
            return None, None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], trl

    def met(sp, ntr, name, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        cnt = np.bincount(wi, minlength=NW) > 0
        v = np.bincount(wi, weights=s, minlength=NW)[cnt]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s != 0
        stk = max((len(list(g)) for kk, g in itertools.groupby(v < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(s.sum() / PV / max(len(s), 1)),
                    daypos=100 * float((s > 0).mean()),
                    trdpos=100 * float((s[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)

    # =====================================================================================
    # PHASE 2 - ATTRIBUTION of the incumbent's money by ENTRY STATE
    # =====================================================================================
    sp0, trl0 = build(2.83)
    P_(f"=== B1 GATE: {sp0.sum()/PV/NS:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(sp0.sum()/PV/NS - 14.72) < 0.6 else 'FAIL - VOID'} "
       f"[{_time.time()-t0:.0f}s]")
    if abs(sp0.sum() / PV / NS - 14.72) >= 0.6:
        out.close(); return
    cols = [idx_of[v] for v in BASE]
    s13 = mem[:, cols].sum(axis=1).astype(int)
    agree13 = (np.sign(s13) == tilt) & (s13 != 0) & (tilt != 0)
    P_(f"\n{'='*118}\n=== PHASE 2: whose money is it? Every trade tagged by its ENTRY STATE")
    P_(f"{'='*118}")
    P_("A trade is B-MOM-ENABLED if, at its entry bar, the member consensus alone would NOT have")
    P_("cleared the entry level - i.e. it fired only because B-MOM was pushing the same way.\n")
    recs = []
    for x in trl0:
        i = i_of(x["et"])
        need = 5 if agree13[i] else 6            # from phase 1's threshold table
        recs.append(dict(pnl=x["pnl"], cons=int(s13[i]), agree=bool(agree13[i]),
                         bmom=int(bmom[i]), enabled=bool(s13[i] < need and bmom[i] > 0),
                         yr=int(pd.Timestamp(x["et"]).year)))
    R = pd.DataFrame(recs)
    R.to_csv(os.path.join(OUT, "trade_states.csv"), index=False)
    tot = R["pnl"].sum()
    P_(f"{'entry state':<34}{'trades':>9}{'share':>8}{'net $':>14}{'share of net':>14}"
       f"{'$/trade':>11}{'win %':>8}")
    for lab, m_ in (("B-MOM ENABLED (consensus short)", R["enabled"]),
                    ("member consensus sufficed", ~R["enabled"]),
                    ("   of which tilt agreed", (~R["enabled"]) & R["agree"]),
                    ("   of which no tilt help", (~R["enabled"]) & ~R["agree"])):
        q = R[m_]
        if not len(q):
            continue
        P_(f"{lab:<34}{len(q):>9}{100*len(q)/len(R):>7.1f}%{q['pnl'].sum():>14,.0f}"
           f"{100*q['pnl'].sum()/tot:>13.1f}%{q['pnl'].mean():>11,.0f}"
           f"{100*float((q['pnl'] > 0).mean()):>7.1f}%")
    P_(f"\n   by year, the B-MOM-enabled share of NET:")
    P_(f"{'year':<8}{'trades':>9}{'enabled':>9}{'enabled share of net':>22}{'enabled $/trade':>18}")
    for y in sorted(R["yr"].unique()):
        q = R[R["yr"] == y]
        e_ = q[q["enabled"]]
        P_(f"{y:<8}{len(q):>9}{len(e_):>9}"
           f"{(100*e_['pnl'].sum()/q['pnl'].sum() if q['pnl'].sum() else 0):>21.1f}%"
           f"{(e_['pnl'].mean() if len(e_) else 0):>18,.0f}")
    P_(f"\n   member consensus at entry: median {R['cons'].median():.0f} of 13, "
       f"10th pct {R['cons'].quantile(.10):.0f}, 25th {R['cons'].quantile(.25):.0f}, "
       f"90th {R['cons'].quantile(.90):.0f}")

    # =====================================================================================
    # PHASE 3 - THE B-MOM WEIGHT LADDER
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 3: the B-MOM weight, 0 (Solar only) -> 4.2 (B-MOM alone enters)")
    P_(f"{'='*118}")
    P_("At 4.2 the B-MOM term alone exceeds the 3.0 entry level, so the members stop mattering.")
    P_("This is NOT a search for a better weight - it measures how much of the object is B-MOM.\n")
    HDR = (f"{'w_bmom':<10}{'trds':>7}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}")
    P_(HDR)
    arms, led = [], {}
    for w in BMOM_W:
        sp, trl = build(w)
        if sp is None:
            P_(f"{w:<10.2f}  too few entries")
            continue
        r = met(sp, len(trl), f"w_bmom={w:.2f}")
        P_(f"{w:<10.2f}{r['ntr']:>7}{r['pts']:>7.2f}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}"
           f"{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}{r['weekly']:>10,.0f}"
           f"{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{r['worst']:>9,.0f}"
           + ("   <- INCUMBENT" if abs(w - 2.83) < 1e-9 else ""))
        arms.append(r); led[w] = sp
    pd.DataFrame(arms).to_csv(os.path.join(OUT, "arms.csv"), index=False)
    P_(f"\n   per year (pts/session):")
    yrs = sorted(set(sdate.year))
    P_(f"{'w_bmom':<10}" + "".join(f"{y:>10}" for y in yrs))
    for w, sp in led.items():
        P_(f"{w:<10.2f}" + "".join(
            f"{sp[sdate.year == y].sum()/PV/max((sdate.year == y).sum(),1):>10.2f}" for y in yrs))
    if 0.0 in led and 2.83 in led:
        a0, a3 = led[0.0], led[2.83]
        P_(f"\n   SOLAR-ONLY vs the incumbent: {a0.sum()/PV/NS:.2f} vs {a3.sum()/PV/NS:.2f} "
           f"pts/session, i.e. B-MOM contributes "
           f"{100*(a3.sum()-a0.sum())/max(abs(a3.sum()),1):.0f} % of the object's net.")
        P_(f"   correlation of the two daily series: "
           f"{float(np.corrcoef(a0, a3)[0,1]):.3f}")
    P_(f"\n=== STATUS: attribution only. Nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
