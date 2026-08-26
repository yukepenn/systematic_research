"""WE_W77 - the object brakes for QUIET sessions and has no brake for VIOLENT ones.

Spec: runs/WE_W77_UPPERTHROTTLE/spec.yaml, committed before this ran.

Motivated by W76 (disclosed contamination): P1 lost -22.49 pts/session over 46 never-seen
sessions in which the median session range went 288 -> 664 points. Every threshold is derived on
2022-07-01 -> 2026-05-29 ONLY; the held-out window is reported for EVERY cell so nothing can be
selected on it.

The falsifier runs first: if the highest-range sessions are PROFITABLE on the derivation window,
the whole idea is dead before an arm is built.
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
from run_we_w01 import ROOT, PV, STRESS_RT, sm14_1m                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W77_UPPERTHROTTLE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
SPLIT = pd.Timestamp("2026-05-30")
DD_TARGET = 20245.0
RNG = np.random.default_rng(20260877)
NDRAW = 200


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "throttle.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = build_context(D)
    st = np.zeros(D["n_sess"], np.int64); st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    en = np.zeros(D["n_sess"], np.int64); en[sid[D["lb"]]] = np.flatnonzero(D["lb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([D["wk"][s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    HELD = np.asarray(sdate >= SPLIT)
    DER = ~HELD
    yr = sdate.year.to_numpy()
    P_(f"=== {NS} sessions | DERIVATION {int(DER.sum())} | HELD OUT {int(HELD.sum())} "
       f"[{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    # -------------------------------------------------- the session-level range ratio
    term_ratio = np.array([X["ratio"][en[s]] for s in range(D["n_sess"])])[sess_in]
    prev_ratio = np.concatenate([[np.nan], np.array([X["ratio"][en[s]]
                                                     for s in range(D["n_sess"])])[:-1]])[sess_in]
    r5 = pd.Series(np.array([X["ratio"][en[s]] for s in range(D["n_sess"])])).rolling(
        5, min_periods=1).mean().shift(1).to_numpy()[sess_in]

    # -------------------------------------------------- rebuild the object
    cache = os.path.join(W76OUT, "mem_ext.npz")
    z = np.load(cache); mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    P_(f"    member matrix reused from W76 [{_time.time()-t0:.0f}s]")
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

    def build(block_sess=None, block_bar=None):
        """block_sess: bool per session in sess_in. block_bar: bool per bar. Entry BLOCK only -
        never an exit rule (W51 recorded that `pos & allow` silently turns a gate into an exit)."""
        vs = []
        for m_ in MEMBERS:
            tg = TG[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        allow = np.ones(n, bool)
        if block_sess is not None:
            bs = np.zeros(D["n_sess"], bool); bs[sess_in] = block_sess
            allow &= ~bs[sid]
        if block_bar is not None:
            allow &= ~block_bar
        held = np.zeros(n, np.int8); h0 = 0
        for i in range(n):
            if fb[i] or pos[i] == 0:
                h0 = 0
            elif h0 == 0 and allow[i]:
                h0 = 1
            held[i] = h0 if pos[i] else 0
        bb = fills_daily(D, held, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        if len(ee) < 100:
            return None
        sc, _ = causal_score(X, ee, window=WIN)
        tr = [x for x in fills_qexit(D, held, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
              if in_win[int(sid[i_of(x["et"])])]]
        return daily(tr), len(tr), float(held[np.isin(sid, sess_in)].astype(bool).mean())

    base = build()
    p1, ntr0, im0 = base
    b1 = p1[DER].sum() / PV / max(DER.sum(), 1)
    P_(f"    B1: incumbent {b1:.2f} pts/session on the DERIVATION window (expect 14.72) -> "
       f"{'PASS' if abs(b1 - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")

    # -------------------------------------------------- PHASE 0: the falsifier
    P_(f"\n{'='*132}\n=== PHASE 0: THE FALSIFIER. P1 by decile of the session's terminal range "
       f"ratio, DERIVATION window only.")
    P_(f"{'='*132}")
    d = pd.DataFrame(dict(r=term_ratio[DER], v=p1[DER]))
    d["dec"] = pd.qcut(d["r"], 10, labels=False, duplicates="drop")
    P_(f"{'decile':<9}{'range ratio':>16}{'sessions':>10}{'net $':>12}{'per session':>13}"
       f"{'pos day %':>11}{'traded %':>10}")
    ph0 = []
    for k_, g in d.groupby("dec"):
        P_(f"{int(k_)+1:<9}{f'{g.r.min():.2f}-{g.r.max():.2f}':>16}{len(g):>10}"
           f"{g.v.sum():>12,.0f}{g.v.mean():>13,.0f}"
           f"{100*float((g.v>0).mean()):>10.1f}%{100*float((g.v!=0).mean()):>9.1f}%")
        ph0.append(dict(decile=int(k_) + 1, lo=float(g.r.min()), hi=float(g.r.max()),
                        n=len(g), net=float(g.v.sum()), per=float(g.v.mean())))
    P0 = pd.DataFrame(ph0); P0.to_csv(os.path.join(OUT, "deciles.csv"), index=False)
    top2 = P0[P0["decile"] >= 9]["net"].sum()
    P_(f"\n   top two deciles (the most violent 20 % of sessions): net ${top2:,.0f}")
    if top2 > 0:
        P_(f"   -> *** FALSIFIED. The highest-range sessions are PROFITABLE on the derivation")
        P_(f"      window. An upper throttle would be cutting the object's own best sessions.")
        P_(f"      The arms below are run and reported anyway, as the spec requires, but the")
        P_(f"      idea is dead on its own falsifier and no arm may be promoted. ***")
    else:
        P_(f"   -> the falsifier does NOT fire; the most violent sessions lose money and an")
        P_(f"      upper brake has a mechanism. Arms proceed.")

    # -------------------------------------------------- arms
    def wkv(v, m):
        wi = wk_idx[m]
        cnt = np.bincount(wi, minlength=NW) > 0
        return np.bincount(wi, weights=v[m], minlength=NW)[cnt]

    def pan(v, m, ntr, im):
        w = wkv(v, m)
        dp = dd_profile(w)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for kk, g in itertools.groupby(w < 0) if kk), default=0)
        return dict(pts=float(v[m].sum() / PV / max(m.sum(), 1)), ntr=ntr, inmkt=100 * im,
                    net=float(v[m].sum()), wkpos=100 * float((w > 0).mean()),
                    wstreak=int(stk), weekly=float(w.mean()), weekly_dd=float(w.mean()) * k,
                    dd5=dp["dd_mean_top5"] * k, maxdd=float(dp["maxdd"]),
                    worst=float(w.min()))

    ARMS = {"U0 incumbent": (None, None)}
    for Q in (1.5, 2.0, 2.5, 3.0):
        ARMS[f"U1 intra ratio>{Q}"] = (None, X["ratio"] > Q)
    for Q in (1.5, 2.0, 2.5):
        ARMS[f"U2 prev sess >{Q}"] = (np.nan_to_num(prev_ratio, nan=0.0) > Q, None)
    for Q in (1.25, 1.5, 2.0):
        ARMS[f"U3 trail5 >{Q}"] = (np.nan_to_num(r5, nan=0.0) > Q, None)

    P_(f"\n{'='*164}\n=== ARMS. Thresholds derived on the DERIVATION window; the held-out "
       f"window is shown for EVERY cell and selects nothing.")
    P_(f"{'='*164}")
    P_(f"{'arm':<22}{'blkS':>6}{'trds':>7}| {'DERIVATION 2022-07 -> 2026-05':^62} | "
       f"{'HELD OUT 2026-06..07':^38}")
    P_(f"{'':<22}{'':>6}{'':>7}| {'pts':>7}{'wk+%':>7}{'wStrk':>7}{'wk$@DD':>9}{'dd5':>9}"
       f"{'worst':>9}{'2022':>8} | {'pts':>8}{'net $':>10}{'wk+%':>7}{'worst':>9}")
    rows, ledg = [], {}
    for nm, (bs, bb_) in ARMS.items():
        r = build(bs, bb_)
        if r is None:
            P_(f"{nm:<22}   (fewer than 100 entries)"); continue
        v, ntr, im = r
        de = pan(v, DER, ntr, im); ho = pan(v, HELD, ntr, im)
        y22 = v[yr == 2022].sum() / PV / max((yr == 2022).sum(), 1)
        nb = int(bs.sum()) if bs is not None else 0
        P_(f"{nm:<22}{nb:>6}{ntr:>7}| {de['pts']:>7.2f}{de['wkpos']:>6.1f}%{de['wstreak']:>7}"
           f"{de['weekly_dd']:>9,.0f}{de['dd5']:>9,.0f}{de['worst']:>9,.0f}{y22:>8.2f} | "
           f"{ho['pts']:>8.2f}{ho['net']:>10,.0f}{ho['wkpos']:>6.1f}%{ho['worst']:>9,.0f}")
        rows.append(dict(arm=nm, blocked=nb, **{f"der_{k}": vv for k, vv in de.items()},
                         **{f"ho_{k}": vv for k, vv in ho.items()}, y2022=y22))
        ledg[nm] = v
    R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "arms.csv"), index=False)
    np.savez_compressed(os.path.join(OUT, "ledgers.npz"), **ledg)

    inc = R[R["arm"] == "U0 incumbent"].iloc[0]
    P_(f"\n=== PREREGISTERED CANDIDATE BAR (derivation window only): better dd5 AND better "
       f"weekly streak AND weekly$@DD not worse by >10 %")
    cand = R[(R["arm"] != "U0 incumbent") & (R["der_dd5"] < inc["der_dd5"])
             & (R["der_wstreak"] < inc["der_wstreak"])
             & (R["der_weekly_dd"] >= 0.90 * inc["der_weekly_dd"])]
    if not len(cand):
        P_(f"   NO ARM CLEARS IT. The upper throttle does not earn a null.")
    else:
        for _, r in cand.iterrows():
            P_(f"   CANDIDATE: {r['arm']}  dd5 {r['der_dd5']:,.0f} vs {inc['der_dd5']:,.0f}, "
               f"streak {int(r['der_wstreak'])} vs {int(inc['der_wstreak'])}, "
               f"wk$@DD {r['der_weekly_dd']:,.0f} vs {inc['der_weekly_dd']:,.0f}")
        P_(f"\n=== N1 NULL on each candidate: shift the BLOCK SCHEDULE, keep its size ===")
        P_(f"{'arm':<22}{'real dd5':>11}{'null mean':>11}{'null p05':>11}{'pctile':>9}")
        nl = []
        for _, r in cand.iterrows():
            bs = ARMS[r["arm"]][0]
            if bs is None:
                P_(f"{r['arm']:<22}   (intra-bar arm - block schedule is not session-wise; "
                   f"null not applicable in this form)")
                continue
            k = int(bs.sum()); vals = []
            for _ in range(NDRAW):
                sh = np.zeros(NS, bool)
                sh[RNG.choice(NS, size=k, replace=False)] = True
                rr = build(sh, None)
                if rr is None:
                    continue
                vals.append(pan(rr[0], DER, rr[1], rr[2])["dd5"])
                if len(vals) >= 40:
                    break
            vals = np.array(vals)
            pct = 100 * float((vals > r["der_dd5"]).mean())
            P_(f"{r['arm']:<22}{r['der_dd5']:>11,.0f}{vals.mean():>11,.0f}"
               f"{np.percentile(vals,5):>11,.0f}{pct:>8.0f}%")
            nl.append(dict(arm=r["arm"], real=r["der_dd5"], null_mean=float(vals.mean()),
                           pctile=pct, n=len(vals)))
        pd.DataFrame(nl).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    P_(f"\n=== STATUS: diagnostic. NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
