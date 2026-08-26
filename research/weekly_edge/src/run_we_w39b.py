"""WE_W39 amendment 1 (declared in amendment_1.yaml before this run).

Fixes two defects in read 1's own adoption rule:
  D1 the worst-week gate was exposure-naive and rejected a short arm that BEAT the base at
     matched exposure -> primary criterion is now eff (weekly / |worst week|) and CVaR
     efficiency, both exposure-invariant; absolute worst week is reported, not gated.
  D2 Q1 forced a top-5 pick, which manufactures churn from near-ties -> Q5 admits by a
     t >= 2 THRESHOLD instead, separating "feature information is unstable" from
     "rank-k selection is unstable".
Adds the binding nulls the short arm never received.
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
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import (OUT, A, WF0, B, MINHIST, WIN, bin_score,          # noqa: E402
                        cont_score, size_from_score, screen_t)
from we_quality import build_context                                     # noqa: E402
from we_features import build_universe                                   # noqa: E402

RNG = np.random.default_rng(2026039)
CORE = [("dist_open", +1), ("prev_ret", -1), ("runlen", +1),
        ("dist_vwap", +1), ("delta_mag", +1)]


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
    NS_FULL, NS_WF = nsess(A, B), nsess(WF0, B)

    out = open(os.path.join(OUT, "features_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)
    rows = []
    hdr = (f"{'arm':<34}{'n':>6}{'sz':>5}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'cvEff':>7}{'stress':>8}")

    def rep(nm, trl, a, b, ns, ref=None, scale=1.0):
        d = weekly(trl, wk_of, a, b)
        v = np.array(list(d.values())) * scale if d else np.array([0.0])
        s = float(v.mean() / v.std(ddof=1)) if len(v) > 7 and v.std(ddof=1) > 0 else 0.0
        wp = float((v > 0).mean() * 100)
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b]) * scale
        u = np.array([x.get("u", 1) for x in trl
                      if a <= np.datetime64(x["et"]) < b]) * scale
        if len(p) == 0:
            p, u = np.array([0.0]), np.array([1.0])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cvar = float(np.sort(v)[:nw].mean())
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cveff = float(v.mean() / abs(cvar)) if cvar < 0 else 9.9
        st = float((v - STRESS_RT * scale * len(p) / max(len(v), 1)).mean())
        r = dict(arm=nm, n=len(p), avg_size=round(float(u.mean()), 2),
                 pts=round(float(p.sum() / PV / ns), 2), per_trade=round(float(p.mean()), 1),
                 wk=round(float(v.mean())), wkpos=round(wp, 1), worst=round(float(v.min())),
                 cvar5=round(cvar), sharpe=round(s, 3), eff=round(eff, 3),
                 cveff=round(cveff, 3), stress=round(st))
        if ref is not None:
            r["passes"] = bool(r["eff"] > ref["eff"] and r["cveff"] > ref["cveff"]
                               and st > 0)
        P_(f"{nm:<34}{r['n']:>6}{r['avg_size']:>5.2f}{r['pts']:>7.2f}{r['per_trade']:>8.1f}"
           f"{r['wk']:>8,.0f}{r['wkpos']:>6.1f}{r['worst']:>9,.0f}{r['cvar5']:>9,.0f}"
           f"{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}{r['stress']:>8,.0f}"
           f"{'' if ref is None else ('  PASS' if r['passes'] else '  reject')}")
        rows.append(r)
        return r

    # ---------------- base + B1 -------------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    pnlL = np.array([x["pnl"] for x in bl])
    etL = np.array([np.datetime64(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    q0 = fills_qexit(D, posL, szQ0, scQ0)
    pts0 = np.array([x["pnl"] for x in q0
                     if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS_FULL
    P_(f"=== B1: {pts0:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts0-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts0 - 14.72) >= 0.6:
        out.close(); return
    F, CLS = build_universe(D)
    names = list(F)

    # ---------------- Q5 / Q6: threshold admission instead of top-k -------------------
    qtr = pd.PeriodIndex(pd.to_datetime(etL), freq="Q")
    uq = [q for q in qtr.unique() if q.start_time >= pd.Timestamp(str(WF0))]
    sc5 = np.full(len(entL), np.nan); sc6 = np.full(len(entL), np.nan)
    k5 = np.zeros(len(entL)); k6 = np.zeros(len(entL))
    picks5 = []
    for q in uq:
        qs = np.datetime64(q.start_time.to_pydatetime())
        fit = (etL >= qs - np.timedelta64(365, "D")) & (etL < qs)
        tst = np.where(qtr == q)[0]
        if fit.sum() < 200 or len(tst) == 0:
            continue
        bq, _ = screen_t(F, names, entL[fit], pnlL[fit])
        adm = [(k, v[0]) for k, v in bq.items() if v[1] >= 2.0]
        picks5.append((str(q), sorted(k for k, _ in adm)))
        if adm:
            s_ = bin_score(F, entL, adm, only=list(tst))
            m = len(adm) // 2 + 1
            sc5[tst] = s_[tst]; k5[tst] = m
        else:
            sc5[tst] = 0; k5[tst] = 1
        core = list(CORE)
        for k, sgn in adm:
            if k not in [c for c, _ in core]:
                core.append((k, sgn))
        s6 = bin_score(F, entL, core, only=list(tst))
        sc6[tst] = s6[tst]; k6[tst] = len(core) // 2 + 1
    ov = []
    for i in range(1, len(picks5)):
        a_, b_ = set(picks5[i][1]), set(picks5[i - 1][1])
        ov.append(len(a_ & b_) / max(1, len(a_ | b_)))
    P_(f"\n=== Q5 threshold admission (t >= 2, trailing 12m) [{_time.time()-t0:.0f}s] ===")
    P_(f"   quarters {len(picks5)} | admitted per quarter "
       f"{[len(p[1]) for p in picks5]} | Jaccard overlap {np.mean(ov)*100:.0f}% "
       f"-> CHURN {100-np.mean(ov)*100:.0f}%  (Q1 top-5 churn was 62 %)")
    for qn, ks in picks5:
        P_(f"     {qn}: {', '.join(ks) if ks else '(none admitted)'}")

    def to_bar(sc, k):
        sb = np.zeros(n); kb = np.zeros(n)
        m = ~np.isnan(sc)
        sb[entL[m]] = sc[m]; kb[entL[m]] = k[m]
        return sb, np.where(sb >= np.maximum(kb, 1), 2, 1).astype(np.int8)
    sc5b, sz5 = to_bar(sc5, k5)
    sc6b, sz6 = to_bar(sc6, k6)

    P_(f"\n=== LONG ARMS on the adoption window 2023-07 -> 2026-08 "
       f"(eff/cvEff are the criteria; worst week reported not gated) ===")
    P_(hdr)
    rq0 = rep("Q0 incumbent five (reference)", q0, WF0, B, NS_WF)
    rep("Q5 WF threshold-admitted", fills_qexit(D, posL, sz5, sc5b), WF0, B, NS_WF, ref=rq0)
    rep("Q6 core five + admitted", fills_qexit(D, posL, sz6, sc6b), WF0, B, NS_WF, ref=rq0)
    rep("BASE no quality layer", fills_daily(D, posL, halt=1300, target=1000), WF0, B, NS_WF)

    # ---------------- short side: matched exposure + the missing nulls -----------------
    P_(f"\n=== SHORT SIDE, EXPOSURE-MATCHED (D1 correction) [{_time.time()-t0:.0f}s] ===")
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    S0 = sfills(D, posS)
    sl = [x for x in S0 if A <= np.datetime64(x["et"]) < B]
    entS = np.array([i_of(x["et"]) for x in sl])
    pnlS = np.array([x["pnl"] for x in sl])
    scS = cont_score(F, entS, pnlS, names)
    szSv = size_from_score(scS, cap=2)
    szS = np.ones(n, np.int8); szS[entS] = szSv
    Sc = sfills(D, posS, size_at_entry=szS)
    avg_sz = float(np.mean([x["u"] for x in Sc if A <= np.datetime64(x["et"]) < B]))
    P_(hdr)
    rs0 = rep("S0 short base x1", S0, A, B, NS_FULL)
    rep(f"S0 short base x{avg_sz:.2f} (matched)", S0, A, B, NS_FULL, scale=avg_sz)
    rsc = rep("S-cont continuous score", Sc, A, B, NS_FULL, ref=rs0)

    if rsc.get("passes"):
        P_(f"\n=== BINDING NULLS on S-cont [{_time.time()-t0:.0f}s] ===")
        n2 = int((szSv > 1).sum())
        verdicts = {}
        for tag in ("N1 circular shift", "N2 count-matched random"):
            nulls = []
            for j in range(100):
                if tag.startswith("N1"):
                    szn = np.roll(szS, int(RNG.integers(20_000, n - 20_000)))
                else:
                    szn = np.ones(n, np.int8)
                    szn[entS[RNG.choice(len(entS), size=n2, replace=False)]] = 2
                d = weekly(sfills(D, posS, size_at_entry=szn), wk_of, A, B)
                v = np.array(list(d.values()))
                nulls.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
                if (j + 1) % 50 == 0:
                    print(f"   {tag} {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
            nu = np.array(nulls)
            pct = 100.0 * (nu < rsc["eff"]).mean()
            verdicts[tag] = pct
            P_(f"   {tag:<26} real {rsc['eff']:.3f} | null mean {nu.mean():.3f} | "
               f"p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
               f"p {(nu>=rsc['eff']).mean():.3f} -> "
               f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
        P_(f"   BOTH nulls >= 95th: {all(p >= 95 for p in verdicts.values())}")

    # ---------------- portfolio at matched exposure ------------------------------------
    P_(f"\n=== PORTFOLIO at matched exposure, full window [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    P2 = q0

    def expo(trl):
        """Time-weighted exposure: sum of contracts x minutes held (the honest unit)."""
        return float(sum(x.get("u", 1)
                         * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                            / np.timedelta64(1, "m"))
                         for x in trl if A <= np.datetime64(x["et"]) < B))
    rl1 = rep("long Q0 x1", P2, A, B, NS_FULL)
    comb = P2 + Sc
    sc_l = expo(comb) / max(expo(P2), 1e-9)
    P_(f"   time-weighted exposure: long {expo(P2):,.0f} contract-min, "
       f"long+short {expo(comb):,.0f} -> long must be scaled x{sc_l:.2f} to match")
    rep(f"long Q0 x{sc_l:.2f} (matched)", P2, A, B, NS_FULL, scale=sc_l)
    rep("long Q0 + S-cont", comb, A, B, NS_FULL)
    rep("long Q0 + S0 short", P2 + S0, A, B, NS_FULL)

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_b.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
