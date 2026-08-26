"""WE_W56 BREADTH (spec preregistered): does anything in this repo actually diversify P1?

Reported in the owner's units. Contracts scale money and drawdown together, so the only
meaningful question is: AT THE INCUMBENT'S DRAWDOWN, how many dollars a week? Every portfolio
below is rescaled so its max drawdown equals P1's $20,245 and that is the headline column.

Phase 0 also fixes an infrastructure gap: across all 55 runs/WE_* directories there is no P1
daily or weekly P&L series on disk. Every wave has regenerated it in memory and discarded it.
This one persists it.
"""
from __future__ import annotations

import hashlib
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w40 import axis_volexp                                       # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out")
os.makedirs(OUT, exist_ok=True)
BMOM_H = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w10_bmom_hist",
                      "w10bmom_daily.csv")
BMOM_D = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w8_bmom",
                      "w8bmom_w14_daily.csv")
BREADTH = os.path.join(ROOT, "research", "breadth_lab", "BREADTH01_TSMOM_REPLICATION",
                       "out", "book_daily_full.csv")
WGRID = np.round(np.arange(0.0, 0.601, 0.05), 3)          # 13 points
NDRAW = 200
RNG = np.random.default_rng(20260856)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:16]


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    out = open(os.path.join(OUT, "breadth.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])

    # =====================================================================================
    # PHASE 0 - regenerate and PERSIST
    # =====================================================================================
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ent, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    P1 = [x for x in fills_qexit(D, posL, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
    pts = sum(x["pnl"] for x in P1) / PV / NS
    P_(f"=== B1 GATE: {pts:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    def daily_of(trades):
        d = {}
        for x in trades:
            s = int(sid[i_of(x["et"])])
            if in_win[s]:
                d[sdate[s].date()] = d.get(sdate[s].date(), 0.0) + x["pnl"]
        return pd.Series(d).sort_index()
    p1d = daily_of(P1)
    p1d.index = pd.to_datetime(p1d.index)
    p1d.name = "p1_usd"
    p1d.to_csv(os.path.join(OUT, "p1_daily.csv"))

    tgB = axis_volexp(D, X, 1.6, 1.0, 15)
    trB = [x for x in sfills(D, tgB, halt=1300.0, target=1000.0)
           if in_win[int(sid[i_of(x["et"])])]]
    bd = daily_of(trB)
    bd.index = pd.to_datetime(bd.index)
    bd.name = "axisb_usd"
    bd.to_csv(os.path.join(OUT, "axisb_daily.csv"))
    P_(f"   persisted p1_daily.csv ({len(p1d)} sessions, sha {sha(os.path.join(OUT,'p1_daily.csv'))}) "
       f"and axisb_daily.csv ({len(bd)} sessions, {len(trB)} trades)")

    # ---- the external sleeves -----------------------------------------------------------
    bm = pd.concat([pd.read_csv(BMOM_H), pd.read_csv(BMOM_D)], ignore_index=True)
    bm["sess"] = pd.to_datetime(bm["sess"])
    bmd = bm.set_index("sess")["net_c1_usd"].sort_index()
    br = pd.read_csv(BREADTH)
    br["date"] = pd.to_datetime(br["date"])
    brd = br.set_index("date")["book_net"].sort_index()
    P_(f"   B-MOM {len(bmd):,} sessions {bmd.index.min().date()} -> {bmd.index.max().date()} "
       f"(US$ at 1 NQ, C1 friction) | BREADTH01 {len(brd):,} days "
       f"{brd.index.min().date()} -> {brd.index.max().date()} (daily fractional return)")

    # ---- common weekly frame -------------------------------------------------------------
    lo = max(p1d.index.min(), pd.Timestamp("2022-07-01"))
    hi = min(p1d.index.max(), bmd.index.max(), brd.index.max())
    P_(f"\n   INTERSECTION WINDOW {lo.date()} -> {hi.date()}; P1 loses "
       f"{int((p1d.index > hi).sum())} sessions at the right edge to the sleeves' coverage.")

    def wk(s):
        s = s[(s.index >= lo) & (s.index <= hi)]
        iso = s.index.isocalendar()
        k = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
        return s.groupby(k.values).sum()
    W = pd.DataFrame({"P1": wk(p1d), "AXISB": wk(bd), "BMOM": wk(bmd),
                      "BREADTH": wk(brd)}).fillna(0.0).sort_index()
    NW = len(W)
    P_(f"   {NW} common weeks")

    # =====================================================================================
    # PHASE 1 - CORRELATION AGAINST P1, for the first time
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 1: correlation against P1 ITSELF (every published rho was vs E10)")
    P_(f"{'='*112}")
    v0 = W["P1"].values
    dec = np.argsort(v0)[:max(3, NW // 10)]
    se_dec = 1.0 / np.sqrt(max(len(dec) - 3, 1))

    def uw(v):
        c = np.cumsum(v); return np.maximum.accumulate(c) - c
    P_(f"{'sleeve':<12}{'wk mean $':>11}{'wk sd $':>10}{'annShrp':>9}{'rho vs P1':>11}"
       f"{'rho in P1 worst decile':>24}{'rho underwater':>16}")
    rows = []
    for k in ("AXISB", "BMOM", "BREADTH"):
        v = W[k].values
        sd = v.std(ddof=1)
        r = float(np.corrcoef(v, v0)[0, 1]) if sd > 0 else 0.0
        rd = float(np.corrcoef(v[dec], v0[dec])[0, 1]) if v[dec].std() > 0 else 0.0
        ru = float(np.corrcoef(uw(v), uw(v0))[0, 1])
        P_(f"{k:<12}{v.mean():>11,.3f}{sd:>10,.3f}"
           f"{(v.mean()/sd*np.sqrt(52) if sd > 0 else 0):>9.2f}{r:>11.3f}"
           f"{f'{rd:+.3f} +- {se_dec:.2f}':>24}{ru:>16.3f}")
        rows.append(dict(sleeve=k, wk_mean=v.mean(), wk_sd=sd, rho=r, rho_dec=rd,
                         rho_uw=ru, se_dec=se_dec))
    P_(f"{'P1':<12}{v0.mean():>11,.0f}{v0.std(ddof=1):>10,.0f}"
       f"{v0.mean()/v0.std(ddof=1)*np.sqrt(52):>9.2f}{1.0:>11.3f}")
    P_(f"\n   The worst-decile column conditions on P1 ALONE being extreme, not on the SUM, so")
    P_(f"   it does not carry the selection artifact I created and caught in W53. But it is")
    P_(f"   {len(dec)} weeks: SE(rho) ~ {se_dec:.2f}, so none of these is distinguishable from 0.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "corr.csv"), index=False)

    # =====================================================================================
    # PHASE 2 - CONSTANT RISK, THEN FIXED DRAWDOWN
    # =====================================================================================
    DD0 = float(dd_profile(v0)["maxdd"])
    s0 = v0.std(ddof=1)
    P_(f"\n{'='*112}\n=== PHASE 2: every portfolio rescaled to P1's own max drawdown "
       f"(${DD0:,.0f})")
    P_(f"{'='*112}")
    P_("weekly$ is THE column: how many dollars a week you get for the SAME worst drawdown.\n")

    def at_fixed_dd(v, name, w=None, sleeve=None):
        dp = dd_profile(v)
        if dp["maxdd"] <= 0:
            return None
        k = DD0 / dp["maxdd"]
        vv = v * k
        dq = dd_profile(vv)
        nw5 = max(1, int(np.ceil(0.05 * len(vv))))
        cv = float(np.sort(vv)[:nw5].mean())
        sd = vv.std(ddof=1)
        return dict(arm=name, w=w, sleeve=sleeve, scale=k, weekly=float(vv.mean()),
                    wkpos=100 * float((vv > 0).mean()), worst=float(vv.min()),
                    maxdd=dq["maxdd"], dd_top5=dq["dd_mean_top5"], ulcer=dq["ulcer"],
                    annshrp=float(vv.mean() / sd * np.sqrt(52)) if sd > 0 else 0.0,
                    cveff=float(vv.mean() / abs(cv)) if cv < 0 else 9.9,
                    p1_contracts=1.27 * k * (1 - (w or 0.0)))
    HDR = (f"{'portfolio':<30}{'weekly$':>10}{'wk+%':>7}{'worst$':>10}{'top5DD':>10}"
           f"{'ulcer':>9}{'annShrp':>9}{'cvEff':>8}{'P1 contracts':>14}{'sleeve units':>14}")

    def show(r, su=None):
        P_(f"{r['arm']:<30}{r['weekly']:>10,.0f}{r['wkpos']:>7.1f}{r['worst']:>10,.0f}"
           f"{r['dd_top5']:>10,.0f}{r['ulcer']:>9,.0f}{r['annshrp']:>9.2f}{r['cveff']:>8.3f}"
           f"{r['p1_contracts']:>14.2f}{(f'{su:.2f}' if su is not None else '-'):>14}")
    P_(HDR)
    base_r = at_fixed_dd(v0, "P1 INCUMBENT", 0.0)
    show(base_r)
    scan = []
    for k in ("AXISB", "BMOM", "BREADTH"):
        v = W[k].values
        sc_ = v.std(ddof=1)
        if sc_ <= 0:
            continue
        vn = v * (s0 / sc_)                       # vol-normalised to P1's weekly sigma
        for w in WGRID:
            if w == 0:
                continue
            p = (1 - w) * v0 + w * vn
            r = at_fixed_dd(p, f"P1 + {k} w={w:.2f}", w, k)
            if r is None:
                continue
            r["sleeve_units"] = r["scale"] * w * (s0 / sc_)
            scan.append(r)
    S = pd.DataFrame(scan)
    S.to_csv(os.path.join(OUT, "wscan.csv"), index=False)
    for k in ("AXISB", "BMOM", "BREADTH"):
        q = S[S["sleeve"] == k]
        if not len(q):
            continue
        for _, r in q.iterrows():
            show(r, r["sleeve_units"])
        P_("")
    # best pair
    bp = None
    vb = W["BMOM"].values * (s0 / max(W["BMOM"].values.std(ddof=1), 1e-9))
    vr = W["BREADTH"].values * (s0 / max(W["BREADTH"].values.std(ddof=1), 1e-9))
    for w1 in np.round(np.arange(0.05, 0.45, 0.05), 3):
        for w2 in np.round(np.arange(0.05, 0.45, 0.05), 3):
            if w1 + w2 > 0.6:
                continue
            p = (1 - w1 - w2) * v0 + w1 * vb + w2 * vr
            r = at_fixed_dd(p, f"P1 + BMOM {w1:.2f} + BREADTH {w2:.2f}", w1 + w2, "PAIR")
            if r and (bp is None or r["weekly"] > bp["weekly"]):
                bp = r
    if bp:
        show(bp)

    # =====================================================================================
    # PHASE 3 - THE NULLS
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 3: the nulls (scan-matched - every draw takes its own best of "
       f"{len(WGRID)-1})")
    P_(f"{'='*112}")
    P_("N1 circular shift  : same mean, same vol, alignment with P1 destroyed")
    P_("N3 synthetic sleeve: same mean, vol and lag-1 autocorrelation, drawn independently")
    P_("A zero-mean uncorrelated sleeve STRICTLY HURTS at constant risk, so any gain requires")
    P_("the sleeve's own expectancy. These nulls ask whether the ALIGNMENT adds anything.\n")

    def best_over_w(vn):
        b = None
        for w in WGRID:
            if w == 0:
                continue
            r = at_fixed_dd((1 - w) * v0 + w * vn, "", w)
            if r and (b is None or r["weekly"] > b["weekly"]):
                b = r
        return b
    nullrows = []
    P_(f"{'sleeve':<12}{'real best $':>13}{'N1 mean':>10}{'N1 pct':>9}"
       f"{'N3 mean':>10}{'N3 pct':>9}{'verdict':>10}")
    for k in ("AXISB", "BMOM", "BREADTH"):
        v = W[k].values
        sc_ = v.std(ddof=1)
        if sc_ <= 0:
            continue
        vn = v * (s0 / sc_)
        real = best_over_w(vn)
        if real is None:
            continue
        mu, sg = vn.mean(), vn.std(ddof=1)
        rho1 = float(pd.Series(vn).autocorr(1)) if NW > 5 else 0.0
        rho1 = 0.0 if not np.isfinite(rho1) else float(np.clip(rho1, -0.9, 0.9))
        n1, n3 = [], []
        for _ in range(NDRAW):
            b = best_over_w(np.roll(vn, int(RNG.integers(5, NW - 5))))
            if b:
                n1.append(b["weekly"])
            e = RNG.normal(0, sg * np.sqrt(1 - rho1 ** 2), NW)
            syn = np.empty(NW); syn[0] = e[0]
            for j in range(1, NW):
                syn[j] = rho1 * syn[j - 1] + e[j]
            syn = syn - syn.mean() + mu
            b = best_over_w(syn)
            if b:
                n3.append(b["weekly"])
        a1, a3 = np.array(n1), np.array(n3)
        p1_ = 100 * float((a1 < real["weekly"]).mean())
        p3_ = 100 * float((a3 < real["weekly"]).mean())
        P_(f"{k:<12}{real['weekly']:>13,.0f}{a1.mean():>10,.0f}{p1_:>8.1f}%"
           f"{a3.mean():>10,.0f}{p3_:>8.1f}%"
           f"{('PASS' if (p1_ >= 95 and p3_ >= 95) else 'fail'):>10}")
        nullrows.append(dict(sleeve=k, real=real["weekly"], w=real["w"],
                             n1_mean=float(a1.mean()), n1_pct=p1_,
                             n3_mean=float(a3.mean()), n3_pct=p3_))
    pd.DataFrame(nullrows).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    # =====================================================================================
    # PHASE 4 - THE WEAKNESSES, as measurements
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 4: the weaknesses, measured rather than caveated")
    P_(f"{'='*112}")
    for k, path in (("BMOM", None), ("BREADTH", None)):
        v = W[k].values
        sd = v.std(ddof=1)
        se = sd / np.sqrt(NW)
        P_(f"   {k}: {NW} weeks in-window, weekly mean {v.mean():,.4f} +- {se:,.4f} (SE), "
           f"t = {v.mean()/max(se,1e-12):.2f}")
    # B-MOM era split, using its own full history
    bh = bmd[bmd.index < pd.Timestamp("2022-01-01")]
    bdv = bmd[bmd.index >= pd.Timestamp("2022-01-01")]
    P_(f"\n   B-MOM era split on its OWN full history (the Amendment-1 2(a) question):")
    P_(f"      2006-2021: {len(bh):,} sessions, net ${bh.sum():,.0f}, "
       f"daily mean ${bh.mean():.1f} +- {bh.std()/np.sqrt(len(bh)):.1f} (SE), "
       f"t = {bh.mean()/(bh.std()/np.sqrt(len(bh))):.2f}")
    P_(f"      2022-2026: {len(bdv):,} sessions, net ${bdv.sum():,.0f}, "
       f"daily mean ${bdv.mean():.1f} +- {bdv.std()/np.sqrt(len(bdv)):.1f} (SE), "
       f"t = {bdv.mean()/(bdv.std()/np.sqrt(len(bdv))):.2f}")
    P_(f"      -> the modern era is a {len(bdv):,}-session sample. Amendment 1 2(b) requires a")
    P_(f"         CAUSAL REGIME VARIABLE separating the eras; none is named in the record, so")
    P_(f"         the honest description is 'a 4-year sample', not 'a regime'.")
    bra = brd[(brd.index >= lo) & (brd.index <= hi)]
    P_(f"\n   BREADTH01 notional disclosure: the book is a fractional-return series at "
       f"{100*bra.std()*np.sqrt(252):.2f} % annualised vol in-window.")
    if len(nullrows):
        wsel = [r for r in nullrows if r["sleeve"] == "BREADTH"]
        if wsel:
            P_(f"      at the scanned weight w={wsel[0]['w']:.2f} the implied notional is "
               f"reported in wscan.csv column sleeve_units (units of ONE book).")
    P_(f"\n=== FRONTIER (the owner's column, sorted) ===")
    allr = [base_r] + scan + ([bp] if bp else [])
    Fr = pd.DataFrame(allr).sort_values("weekly", ascending=False)
    Fr.to_csv(os.path.join(OUT, "frontier.csv"), index=False)
    P_(HDR)
    for _, r in Fr.head(8).iterrows():
        show(r, r.get("sleeve_units"))
    P_(f"\n   incumbent weekly at its own drawdown: ${base_r['weekly']:,.0f}")
    top = Fr.iloc[0]
    P_(f"   best portfolio: {top['arm']} at ${top['weekly']:,.0f}/week "
       f"({100*(top['weekly']/base_r['weekly']-1):+.1f} %)")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
