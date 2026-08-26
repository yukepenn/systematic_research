"""WE_W40 amendment 1 (declared in amendment_1.yaml before this run).

Read 1 paired every axis with the long object at ONE CONTRACT EACH, which handed the
vol-expansion sleeve 34 % of total exposure. That answers "should B get a third of the book",
which nobody asked. The diversification question is whether ANY positive weight improves the
tail at CONSTANT TOTAL EXPOSURE. This run scans weight, measures B's parameter surface, walks
B forward with churn disclosed, and runs both of B's nulls.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly                                           # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w40 import OUT, A, WF0, B, axis_volexp                       # noqa: E402
from we_quality import build_context                                     # noqa: E402

RNG = np.random.default_rng(2026401)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]
    NS = len(np.unique(D["sid"][(tarr >= WF0) & (tarr < B)]))
    out = open(os.path.join(OUT, "second_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    LONG = fills_qexit(D, posL, szQ0, scQ0)
    ptsf = np.array([x["pnl"] for x in LONG
                     if A <= np.datetime64(x["et"]) < B]).sum() / PV / len(
        np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    P_(f"=== B1: {ptsf:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(ptsf-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(ptsf - 14.72) >= 0.6:
        out.close(); return

    keys = sorted(weekly(LONG, wk_of, WF0, B))

    def wvec(trl, scale=1.0):
        d = weekly(trl, wk_of, WF0, B)
        return np.array([d.get(k, 0.0) for k in keys]) * scale

    def expo(trl):
        return float(sum(x.get("u", 1)
                         * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                            / np.timedelta64(1, "m"))
                         for x in trl if WF0 <= np.datetime64(x["et"]) < B))

    def show(nm, v, ntr):
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * ntr / max(len(v), 1))
        P_(f"{nm:<32}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
           f"{cv:>10,.0f}{s:>8.3f}{eff:>8.3f}{cve:>8.3f}{st:>9,.0f}")
        return dict(arm=nm, wk=round(float(v.mean())), wkpos=round(float((v > 0).mean() * 100), 1),
                    worst=round(float(v.min())), cvar5=round(cv), sharpe=round(s, 3),
                    eff=round(eff, 3), cveff=round(cve, 3), stress=round(st))

    hdr = (f"{'arm':<32}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
           f"{'eff':>8}{'cvEff':>8}{'stress':>9}")
    rows = []

    # ---------------- W: weight scan at CONSTANT total exposure -----------------------
    posB = axis_volexp(D, X, 1.6, 1.0, 15)
    BT = sfills(D, posB, halt=1300.0, target=1000.0)
    eL, eB = expo(LONG), expo(BT)
    nL = len([x for x in LONG if WF0 <= np.datetime64(x["et"]) < B])
    nB = len([x for x in BT if WF0 <= np.datetime64(x["et"]) < B])
    P_(f"\n=== W WEIGHT SCAN at constant total exposure (long {eL:,.0f} contract-min, "
       f"B {eB:,.0f}) [{_time.time()-t0:.0f}s] ===")
    P_("   w = share of TOTAL contract-minutes given to B; total held at the long object's own")
    P_("   exposure so every row is directly comparable to w = 0.")
    P_(hdr)
    ref = None
    for w in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50):
        kL = (1 - w) * 1.0
        kB = (w * eL / eB) if eB > 0 else 0.0
        v = wvec(LONG, kL) + wvec(BT, kB)
        r = show(f"w={w:.2f} (long x{kL:.2f} + B x{kB:.2f})", v, kL * nL + kB * nB)
        r["w"] = w
        rows.append(r)
        if w == 0.0:
            ref = r
    best = max([r for r in rows if r["w"] > 0],
               key=lambda r: (r["eff"], r["cveff"]))
    imp = [r for r in rows if r["w"] > 0
           and (r["eff"] > ref["eff"] or r["cveff"] > ref["cveff"])]
    P_(f"\n   weights improving eff OR CVaR-eff over w=0: "
       f"{[r['w'] for r in imp] if imp else 'NONE -> falsifier fires'}")

    P_("\n   tradeable integer ratios (long contracts : B contracts), same construction:")
    P_(hdr)
    for a_, b_ in ((6, 1), (4, 1), (3, 1), (2, 1)):
        v = wvec(LONG, a_) + wvec(BT, b_)
        rows.append(show(f"{a_} long : {b_} B", v, a_ * nL + b_ * nB))
    P_("   (compare each against long-alone at the SAME contract-minutes:)")
    for a_, b_ in ((6, 1), (4, 1), (3, 1), (2, 1)):
        k = (a_ * eL + b_ * eB) / eL
        rows.append(show(f"long alone x{k:.2f} (match {a_}:{b_})", wvec(LONG, k), k * nL))

    # ---------------- R: parameter surface of B ---------------------------------------
    P_(f"\n=== R PARAMETER SURFACE of B (reported, NOT selected) [{_time.time()-t0:.0f}s] ===")
    P_(f"{'up/down/look':<32}{'n':>7}{'pts':>8}{'$/tr':>8}{'wk$':>9}{'shrp':>8}{'eff':>8}"
       f"{'stress':>9}")
    grid = [(u, d, l) for u in (1.4, 1.6, 1.8, 2.0) for d in (0.9, 1.0, 1.1)
            for l in (10, 15, 30)]
    cache = {}
    for gi, g in enumerate(grid):
        cache[g] = sfills(D, axis_volexp(D, X, *g), halt=1300.0, target=1000.0)
        if (gi + 1) % 12 == 0:
            print(f"   grid {gi+1}/{len(grid)} [{_time.time()-t0:.0f}s]", flush=True)
    surf = []
    for up in (1.4, 1.6, 1.8, 2.0):
        for dn in (0.9, 1.0, 1.1):
            for lk in (10, 15, 30):
                tb = cache[(up, dn, lk)]
                v = wvec(tb)
                p = np.array([x["pnl"] for x in tb if WF0 <= np.datetime64(x["et"]) < B])
                if len(p) == 0:
                    continue
                s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
                eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
                st = float(v.mean() - STRESS_RT * len(p) / max(len(v), 1))
                surf.append(dict(up=up, down=dn, look=lk, n=len(p),
                                 pts=round(float(p.sum() / PV / NS), 2),
                                 per_trade=round(float(p.mean()), 1), wk=round(float(v.mean())),
                                 sharpe=round(s, 3), eff=round(eff, 3), stress=round(st)))
                if (up, dn, lk) in ((1.6, 1.0, 15), (1.4, 1.0, 15), (2.0, 1.0, 15),
                                    (1.6, 1.0, 10), (1.6, 1.0, 30), (1.6, 0.9, 15),
                                    (1.6, 1.1, 15)):
                    P_(f"{f'{up}/{dn}/{lk}':<32}{len(p):>7}{p.sum()/PV/NS:>8.2f}"
                       f"{p.mean():>8.1f}{v.mean():>9,.0f}{s:>8.3f}{eff:>8.3f}{st:>9,.0f}")
    sf = pd.DataFrame(surf)
    sf.to_csv(os.path.join(OUT, "b_surface.csv"), index=False)
    pos_share = float((sf["stress"] > 0).mean() * 100)
    P_(f"   surface: {len(sf)} settings | stress-positive in {pos_share:.0f} % | "
       f"Sharpe {sf['sharpe'].min():.3f}..{sf['sharpe'].max():.3f} | "
       f"pts {sf['pts'].min():.2f}..{sf['pts'].max():.2f}"
       f"  -> {'NOT knife-edge' if pos_share >= 60 else 'KNIFE-EDGE, treat as fitted'}")

    # ---------------- WF: walk-forward of B's parameters ------------------------------
    P_(f"\n=== WF QUARTERLY WALK-FORWARD of B's parameters [{_time.time()-t0:.0f}s] ===")
    et_of = {g: np.array([np.datetime64(x["et"]) for x in cache[g]]) for g in grid}
    pn_of = {g: np.array([x["pnl"] for x in cache[g]]) for g in grid}
    qtr = pd.PeriodIndex(pd.to_datetime(np.array([np.datetime64(x["et"]) for x in LONG])),
                         freq="Q")
    picks = []; wf_pnl = []; wf_et = []
    for qp in sorted(set(qtr)):
        qs = np.datetime64(qp.start_time.to_pydatetime())
        if qs < WF0:
            continue
        bestg, bs = None, -9e9
        for g in grid:
            m = (et_of[g] >= qs - np.timedelta64(365, "D")) & (et_of[g] < qs)
            if m.sum() < 30:
                continue
            sc_ = pn_of[g][m].sum() / max(1.0, np.std(pn_of[g][m]) * np.sqrt(m.sum()))
            if sc_ > bs:
                bs, bestg = sc_, g
        if bestg is None:
            continue
        qe = np.datetime64((qp + 1).start_time.to_pydatetime())
        m = (et_of[bestg] >= qs) & (et_of[bestg] < qe)
        picks.append((str(qp), bestg))
        wf_pnl.append(pn_of[bestg][m]); wf_et.append(et_of[bestg][m])
    same = np.mean([picks[i][1] == picks[i - 1][1] for i in range(1, len(picks))]) \
        if len(picks) > 1 else 0.0
    P_(f"   quarters {len(picks)} | unchanged pick {same*100:.0f}% -> "
       f"CHURN {100-same*100:.0f}%")
    P_(f"   picks: {[p[1] for p in picks]}")
    wf_trl = [dict(pnl=float(p), et=str(e), xt=str(e), u=1)
              for arr, ea in zip(wf_pnl, wf_et) for p, e in zip(arr, ea)]
    P_(hdr)
    rows.append(show("B fixed 1.6/1.0/15", wvec(BT), nB))
    rows.append(show("B quarterly walk-forward", wvec(wf_trl), len(wf_trl)))

    # ---------------- N: nulls on B ----------------------------------------------------
    P_(f"\n=== N NULLS on B's entry mask [{_time.time()-t0:.0f}s] ===")
    realB = show("B real (reference)", wvec(BT), nB)
    for tag in ("N1 circular shift", "N2 count-matched random entries"):
        nulls = []
        ent_b = np.where((posB != 0) & (np.concatenate([[0], posB[:-1]]) == 0))[0]
        for j in range(100):
            if tag.startswith("N1"):
                pn = np.roll(posB, int(RNG.integers(20_000, n - 20_000)))
            else:
                pn = np.zeros(n, np.int8)
                pick = RNG.choice(n - 40, size=len(ent_b), replace=False)
                sgn = RNG.choice([-1, 1], size=len(pick))
                for k, s_ in zip(pick, sgn):
                    pn[k:k + 30] = s_
            v = wvec(sfills(D, pn, halt=1300.0, target=1000.0))
            nulls.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            if (j + 1) % 50 == 0:
                print(f"   {tag} {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nu = np.array(nulls)
        pct = 100.0 * (nu < realB["eff"]).mean()
        P_(f"   {tag:<32} real {realB['eff']:.3f} | null mean {nu.mean():.3f} | "
           f"p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
           f"p {(nu>=realB['eff']).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_b.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
