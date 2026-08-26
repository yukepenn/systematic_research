"""WE_W59 phase 0/1 - re-optimise the object's OWN parameters under the CORRECTED objective.

Every parameter of P1 was chosen under production / Sharpe / eff. Charter Amendment 2 demotes
Sharpe to a diagnostic and makes the objective CONSISTENCY plus small drawdown. One parameter
has an obvious mechanical reason to be badly wrong under the new objective:

  THE SESSION PROFIT TARGET. Under production it is a cap on the upside. Under consistency it
  LOCKS A DAY GREEN - a day that reaches +$1,000 and keeps trading can end red; a day that stops
  there cannot. Its level has never been chosen with that in mind.

This file computes and PERSISTS the daily P&L series of all 216 cells so that this wave and
every later one does arithmetic on stored series instead of re-simulating. A grid winner is not
a result: phase 2 (walk-forward selection) and phase 3 (scan-matched nulls) are in run_we_w59b.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets                                           # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W59_REOPTIM", "out")
os.makedirs(OUT, exist_ok=True)
HALTS = [800.0, 1300.0, 2000.0, 1e12]
TARGETS = [500.0, 750.0, 1000.0, 1500.0, 2500.0, 1e12]
VOTES = [0.375, 0.500, 0.625]
CUTS = [2, 3, 4]
DD_TARGET = 20245.0


def streak(a):
    b = m = 0
    for z in a:
        b = b + 1 if z < 0 else 0
        m = max(m, b)
    return int(m)


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "reoptim.txt"), "w", encoding="utf-8")

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

    # the closed form: vote >= thr  <=>  nMem * nThr * (1+dL) >= 32 * thr
    nMem = np.zeros(n, np.int16)
    for mem in MEMBERS:
        nMem += (TG[mem] > 0).astype(np.int16)
    nThr = np.zeros(n, np.int16)
    for q in QS:
        ok = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
        nThr += ok.astype(np.int16)
    prod = nMem.astype(np.int32) * nThr.astype(np.int32) * (1 + X["dL"].astype(np.int32))

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def cell(halt, target, vthr, cut):
        pos = (prod >= int(np.ceil(32 * vthr))).astype(np.int8)
        base = fills_daily(D, pos, halt=halt, target=(None if target > 1e11 else target))
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 200:
            return None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= cut, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc, halt=halt,
                                      target=(None if target > 1e11 else target))
               if in_win[int(sid[i_of(x["et"])])]]
        return daily(trl), len(trl)

    def metrics(sp, ntr, name):
        v = np.bincount(wk_idx, weights=sp, minlength=NW)
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        traded = sp != 0
        nw = max(1, int(np.ceil(0.05 * len(v))))
        return dict(arm=name, ntr=ntr, pts=float(sp.sum() / PV / NS),
                    daypos=100 * float((sp > 0).mean()),
                    trdpos=100 * float((sp[traded] > 0).mean()) if traded.any() else 0.0,
                    flat=100 * float((~traded).mean()),
                    wkpos=100 * float((v > 0).mean()),
                    dstreak=streak(sp), wstreak=streak(v),
                    medday=float(np.median(sp)) * k, medwk=float(np.median(v)) * k,
                    weekly=float(v.mean()) * k, worst=float(v.min()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    cvar5=float(np.sort(v)[:nw].mean()) * k, raw_maxdd=dp["maxdd"])

    # ---------------- B1 -----------------------------------------------------------------
    inc = cell(1300.0, 1000.0, 0.5, 3)
    if inc is None:
        P_("B1 VOID"); out.close(); return
    sp_inc, n_inc = inc
    r_inc = metrics(sp_inc, n_inc, "P1 INCUMBENT")
    P_(f"=== B1 GATE: {r_inc['pts']:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(r_inc['pts'] - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(r_inc["pts"] - 14.72) >= 0.6:
        out.close(); return

    # ---------------- PHASE 0: compute and persist the whole surface ---------------------
    P_(f"\n   computing {len(HALTS)*len(TARGETS)*len(VOTES)*len(CUTS)} cells and persisting "
       f"their daily series [{_time.time()-t0:.0f}s]")
    rows, series = [], {"date": sdate.strftime("%Y-%m-%d")}
    k = 0
    for halt in HALTS:
        for tg in TARGETS:
            for vt in VOTES:
                for ct in CUTS:
                    nm = (f"h{'inf' if halt > 1e11 else int(halt)}"
                          f"_t{'inf' if tg > 1e11 else int(tg)}_v{vt:.3f}_c{ct}")
                    res = cell(halt, tg, vt, ct)
                    k += 1
                    if res is None:
                        continue
                    sp, nt = res
                    r = metrics(sp, nt, nm)
                    r.update(halt=halt, target=tg, vote=vt, cut=ct)
                    rows.append(r)
                    series[nm] = sp
                    if k % 24 == 0:
                        P_(f"      {k}/216 [{_time.time()-t0:.0f}s]")
    G = pd.DataFrame(rows)
    G.to_csv(os.path.join(OUT, "grid.csv"), index=False)
    pd.DataFrame(series).to_parquet(os.path.join(OUT, "cells_daily.parquet"), index=False)
    P_(f"   persisted {len(G)} cells x {NS} sessions -> out/cells_daily.parquet "
       f"[{_time.time()-t0:.0f}s]")

    # ---------------- PHASE 1: read it as a surface --------------------------------------
    P_(f"\n{'='*118}\n=== PHASE 1a: THE PROFIT TARGET, holding everything else at the incumbent")
    P_(f"{'='*118}")
    P_("Under production this was a cap. Under consistency it LOCKS A DAY GREEN.\n")
    HDR = (f"{'cell':<26}{'trades':>8}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'worst$':>9}")

    def show(r, tag=""):
        P_(f"{r['arm']:<26}{r['ntr']:>8}{r['pts']:>7.2f}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}"
           f"{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}{r['weekly']:>10,.0f}"
           f"{r['dd_top5']:>9,.0f}{r['worst']:>9,.0f}{tag}")
    P_(HDR)
    for _, r in G[(G.halt == 1300.0) & (G.vote == 0.5) & (G.cut == 3)].sort_values("target").iterrows():
        show(r, "   <- INCUMBENT" if r["target"] == 1000.0 else "")
    P_(f"\n=== PHASE 1b: THE HALT, everything else at the incumbent ===")
    P_(HDR)
    for _, r in G[(G.target == 1000.0) & (G.vote == 0.5) & (G.cut == 3)].sort_values("halt").iterrows():
        show(r, "   <- INCUMBENT" if r["halt"] == 1300.0 else "")
    P_(f"\n=== PHASE 1c: THE VOTE THRESHOLD and THE QUALITY CUT ===")
    P_(HDR)
    for _, r in G[(G.halt == 1300.0) & (G.target == 1000.0) & (G.cut == 3)].sort_values("vote").iterrows():
        show(r, "   <- INCUMBENT" if r["vote"] == 0.5 else "")
    for _, r in G[(G.halt == 1300.0) & (G.target == 1000.0) & (G.vote == 0.5)].sort_values("cut").iterrows():
        show(r, "   <- INCUMBENT" if r["cut"] == 3 else "")

    # ---------------- the incumbent's rank on each metric --------------------------------
    P_(f"\n{'='*118}\n=== PHASE 1c: how badly did the OLD objective mislead? "
       f"the incumbent's rank among {len(G)} cells")
    P_(f"{'='*118}")
    P_(f"{'metric':<22}{'incumbent':>12}{'best cell value':>18}{'incumbent rank':>17}"
       f"{'best cell':>28}")
    for key, hi in (("trdpos", True), ("daypos", True), ("wkpos", True), ("weekly", True),
                    ("medwk", True), ("dd_top5", False), ("ulcer", False), ("worst", True),
                    ("wstreak", False), ("pts", True)):
        col = G[key].values
        v = float(r_inc[key])
        rank = int((col > v).sum()) + 1 if hi else int((col < v).sum()) + 1
        bi = int(np.argmax(col)) if hi else int(np.argmin(col))
        P_(f"{key:<22}{v:>12,.2f}{col[bi]:>18,.2f}{f'{rank} of {len(G)}':>17}"
           f"{G.iloc[bi]['arm']:>28}")

    # ---------------- plateau vs spike ----------------------------------------------------
    P_(f"\n=== PHASE 1d: is the best consistency cell a PLATEAU or a SPIKE? ===")
    Gp = G[(G.weekly >= r_inc["weekly"]) & (G.dd_top5 <= r_inc["dd_top5"])]
    P_(f"   cells that beat the incumbent on weekly$ AND the top-5 drawdown: {len(Gp)} of {len(G)}")
    if len(Gp):
        bb = Gp.sort_values("trdpos", ascending=False).iloc[0]
        P_(f"   best of those by TRADED-day rate: {bb['arm']}")
        P_(HDR)
        show(r_inc, "   <- INCUMBENT")
        show(bb, "   <- candidate")
        nb = G[(G.halt.isin(sorted(set(HALTS))[max(0, HALTS.index(bb['halt'])-1):
                                              HALTS.index(bb['halt'])+2]))
               & (G.target.isin(sorted(set(TARGETS))[max(0, TARGETS.index(bb['target'])-1):
                                                     TARGETS.index(bb['target'])+2]))
               & (G.vote == bb['vote']) & (G.cut == bb['cut'])]
        P_(f"\n   its one-step neighbourhood ({len(nb)} cells):")
        for _, r in nb.iterrows():
            show(r)
        P_(f"\n   PLATEAU if the neighbours agree, SPIKE if they do not. "
           f"neighbour traded-day rates: "
           + ", ".join(f"{x:.1f}" for x in nb['trdpos'].values))
    P_(f"\n=== STATUS: surface only. A grid winner is NOT a result - run_we_w59b holds the")
    P_(f"    walk-forward selector and the scan-matched nulls, which are the binding tests. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
