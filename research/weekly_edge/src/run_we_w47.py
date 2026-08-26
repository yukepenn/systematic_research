"""WE_W47 CROSS-CLOCK DECISION RULES (spec preregistered).

Every diversification result so far adds a SLEEVE, i.e. EXPOSURE. eff is exposure-invariant,
so exposure cannot raise it. A cross-clock DECISION rule changes WHICH events are taken at ONE
contract - the only class of change that can. W41's own brief listed confirmation, mixed clocks
and cross-clock aggregation; only "coarse clock as an independent sleeve" was ever tested.
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
from run_we_w01 import ROOT, PV, STRESS_RT, sm14_1m                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly                               # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w44b import clock3                                           # noqa: E402
from we_clocks import expand                                             # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W47_CROSSCLOCK", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260847)


def frac3(D, X):
    """The 3-minute vote FRACTION (not thresholded), cached."""
    f = os.path.join(OUT, "frac3.npy")
    if os.path.exists(f):
        a = np.load(f)
        if len(a) == D["n"]:
            return a
    Dc, ec = clock3(D, anchor_0931=False)
    vs = []
    for mem in MEMBERS:
        tgc = sm14_1m(Dc, 460, return_targets=True, volmults=MEMBERS[mem])
        tg = expand(tgc, ec, D["n"])
        for q in QS:
            okv = np.ones(D["n"], bool) if q is None else ((X["norm"] <= 0)
                                                           | (X["ratio"] >= q))
            for dg in (True, False):
                a_ = (okv & X["dL"]) if dg else okv
                vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
    out = np.vstack(vs).mean(axis=0)
    np.save(f, out)
    return out


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

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS = nsess(A, B)
    out = open(os.path.join(OUT, "crossclock.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    f1 = vote(TG, D, X, +1)
    pos1 = (f1 >= 0.5).astype(np.int8)
    base1 = fills_daily(D, pos1, halt=1300, target=1000)
    bl = [x for x in base1 if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    X0q = fills_qexit(D, pos1, np.where(scQ0 >= 3, 2, 1).astype(np.int8), scQ0)
    pts = np.array([x["pnl"] for x in X0q
                    if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS
    P_(f"=== B1 GATE: 1-min full object {pts:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return
    f3 = frac3(D, X)
    print(f"   3-min vote fraction ready [{_time.time()-t0:.0f}s]", flush=True)

    keys = sorted(weekly(X0q, wk_of, A, B))
    v0 = np.array([weekly(X0q, wk_of, A, B).get(k, 0.0) for k in keys])
    dd = np.argsort(v0)[:max(3, len(v0) // 10)]
    rows = []
    hdr = (f"{'arm':<30}{'n':>6}{'pts':>7}{'$/tr':>8}{'inMkt%':>8}{'pts/bar':>9}"
           f"{'expo(k)':>9}{'wk$':>8}{'wk+%':>6}{'worst':>9}{'CVaR5':>9}{'shrp':>7}"
           f"{'eff':>7}{'cvEff':>7}{'stress':>8}{'corr':>7}")

    def expo(trl, a=A, b=B):
        return float(sum(x.get("u", 1)
                         * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                            / np.timedelta64(1, "m"))
                         for x in trl if a <= np.datetime64(x["et"]) < b))

    def rep(nm, pos, trl, ref=None, a=A, b=B, ns=NS, kk=None):
        d = weekly(trl, wk_of, a, b)
        ks = kk if kk is not None else (keys if (a, b) == (A, B) else sorted(d))
        v = np.array([d.get(x, 0.0) for x in ks])
        if len(v) < 8:
            return None
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        if len(p) == 0:
            p = np.array([0.0])
        mw = (tarr >= a) & (tarr < b)
        inm = float((pos[mw] != 0).mean())
        bars_in = max(1.0, float((pos[mw] != 0).sum()))
        dens = float(p.sum() / PV / bars_in)
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(p) / len(v))
        co = float(np.corrcoef(v, v0)[0, 1]) if (len(v) == len(v0) and v.std() > 0) else 0.0
        ex = expo(trl, a, b)
        r = dict(arm=nm, n=len(p), pts=round(float(p.sum() / PV / ns), 2),
                 per_trade=round(float(p.mean()), 1), in_mkt=round(100 * inm, 1),
                 density=round(dens, 4), expo=round(ex), wk=round(float(v.mean())),
                 worst=round(float(v.min())), cvar5=round(cv), sharpe=round(s, 3),
                 eff=round(eff, 3), cveff=round(cve, 3), stress=round(st), corr=round(co, 3))
        tag = ""
        if ref is not None:
            r["passes"] = bool(eff > ref["eff"] and cve > ref["cveff"]
                               and ex <= ref["expo"] * 1.02 and st > 0)
            tag = "  PASS" if r["passes"] else "  reject"
        P_(f"{nm:<30}{r['n']:>6}{r['pts']:>7.2f}{p.mean():>8.1f}{100*inm:>8.1f}{dens:>9.4f}"
           f"{ex/1000:>9.1f}{r['wk']:>8,.0f}{100*(v>0).mean():>6.1f}{r['worst']:>9,.0f}"
           f"{r['cvar5']:>9,.0f}{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}"
           f"{r['stress']:>8,.0f}{r['corr']:>7.2f}{tag}")
        rows.append(r); return r

    # ---- X4 timing split: 3-min gives direction, 1-min gives entry timing ---------------
    def timing_split(f1, f3):
        d3 = (f3 >= 0.5)
        up1 = (f1 >= 0.5)
        pos = np.zeros(n, np.int8)
        held = 0
        for i in range(n):
            if D["fb"][i]:
                held = 0
            if not d3[i]:
                held = 0
            elif held == 0 and up1[i] and (i == 0 or not up1[i - 1]):
                held = 1
            pos[i] = held
        return pos

    P_(f"\n=== CROSS-CLOCK DECISION RULES, all at ONE contract [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    r_base = rep("X0  1-min base vote", pos1, base1)
    r_ref = rep("X0q 1-min full (incumbent)", pos1, X0q)
    arms = {
        "X1  confirm f3 >= 0.50": ((f1 >= 0.5) & (f3 >= 0.5)).astype(np.int8),
        "X2  confirm f3 >= 0.25": ((f1 >= 0.5) & (f3 >= 0.25)).astype(np.int8),
        "X3  pooled 64-config vote": (((f1 + f3) / 2.0) >= 0.5).astype(np.int8),
        "X4  3-min dir + 1-min timing": timing_split(f1, f3),
    }
    built = {}
    for nm, pos in arms.items():
        trl = fills_daily(D, pos, halt=1300, target=1000)
        built[nm] = (pos, trl)
        rep(nm, pos, trl, r_base)

    P_(f"\n=== SAME ARMS + THE CAUSAL QUALITY LAYER (X5) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    best = None
    for nm, (pos, trl) in list(built.items()):
        blx = [x for x in trl if A <= np.datetime64(x["et"]) < B]
        if len(blx) < 200:
            continue
        ent = np.array([i_of(x["et"]) for x in blx])
        sc, _ = causal_score(X, ent, window=WIN)
        q = fills_qexit(D, pos, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
        r = rep(nm.replace("X1 ", "X5a").replace("X2 ", "X5b").replace("X3 ", "X5c")
                .replace("X4 ", "X5d") + " +Q", pos, q, r_ref)
        built[nm + " +Q"] = (pos, q)
        if r and r.get("passes") and (best is None or r["eff"] > best[1]["eff"]):
            best = (nm + " +Q", r, pos, q)

    P_(f"\n=== PER YEAR for anything that passed [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    cands = [k for k in built if any(rr["arm"].startswith(k.split()[0]) and rr.get("passes")
                                     for rr in rows)]
    for nm in (["X0q 1-min full (incumbent)"] + cands):
        pos, trl = (pos1, X0q) if nm.startswith("X0q") else built[nm]
        for y in (2022, 2023, 2024, 2025, 2026):
            a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
            if a >= b:
                continue
            rep(f"{nm[:22]} {y}", pos, trl, None, a, b, nsess(a, b),
                sorted(weekly(trl, wk_of, a, b)))
        P_("")

    if best is None:
        P_("=== NO CROSS-CLOCK RULE BEATS THE INCUMBENT AT EQUAL EXPOSURE -> falsifier fires ===")
    else:
        nm, r, pos, trl = best
        P_(f"=== BINDING NULLS on {nm} [{_time.time()-t0:.0f}s] ===")
        ent = np.where((pos != 0) & (np.concatenate([[0], pos[:-1]]) == 0))[0]
        hold = int(np.clip(np.median(np.diff(np.append(ent, n))[:max(1, len(ent))]), 5, 300))
        for tag in ("N1 circular shift", "N2 count-matched random"):
            nl = []
            for j in range(100):
                if tag.startswith("N1"):
                    pn = np.roll(pos, int(RNG.integers(20_000, n - 20_000)))
                else:
                    pn = np.zeros(n, np.int8)
                    for k_ in RNG.choice(n - hold - 1, size=len(ent), replace=False):
                        pn[k_:k_ + hold] = 1
                d = weekly(fills_daily(D, pn, halt=1300, target=1000), wk_of, A, B)
                v = np.array([d.get(x, 0.0) for x in keys])
                nl.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
                if (j + 1) % 50 == 0:
                    print(f"   {tag} {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
            nu = np.array(nl)
            pct = 100.0 * (nu < r["eff"]).mean()
            P_(f"   {tag:<26} real {r['eff']:.3f} | null mean {nu.mean():.3f} | "
               f"p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
               f"p {(nu>=r['eff']).mean():.3f} -> "
               f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
