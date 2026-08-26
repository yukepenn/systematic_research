"""WE_W61 - the short sleeve, reopened under the CORRECTED objective.

W39's own table calls it "the CONSISTENCY object" and gives it 64.4 % positive weeks against
P1's 58.6 % - the best weekly-consistency number this campaign has measured - and then drops it
because eff falls 0.198 -> 0.175 and its worst week is -$14,606. Charter Amendment 2 demotes eff
and Sharpe; W52 already measured that eff is a single-observation statistic. So the decision was
made on a criterion the owner has since corrected, and knowingly traded away the thing he wants.

It is NOT a second model - it is the same Solar ratchet mirrored, and law 9 stands. It is a
CONSISTENCY sleeve, which is a smaller claim, and this wave says which of the two it is.
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
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out")
os.makedirs(OUT, exist_ok=True)
DD_TARGET = 20245.0
WGRID = np.round(np.arange(0.0, 0.601, 0.05), 3)
NDRAW = 300
RNG = np.random.default_rng(20260861)


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
    out = open(os.path.join(OUT, "short.txt"), "w", encoding="utf-8")

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

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    # ---- P1, exactly as always ----------------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, e, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    P1 = [x for x in fills_qexit(D, posL, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
    p1 = daily(P1)
    pts = p1.sum() / PV / NS
    P_(f"=== B1 GATE: {pts:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    # ---- the mirrored short vote, 1 contract, same box, same fills ----------------------
    fs = vote(TG, D, X, -1)
    posS = -(fs >= 0.5).astype(np.int8)
    SH = [x for x in sfills(D, posS, halt=1300.0, target=1000.0)
          if in_win[int(sid[i_of(x["et"])])]]
    sh = daily(SH)
    P_(f"   short sleeve: {len(SH)} trades, net ${sh.sum():,.0f}, "
       f"{sh.sum()/PV/NS:.2f} pts/session [{_time.time()-t0:.0f}s]")
    pd.DataFrame(dict(date=sdate.strftime("%Y-%m-%d"), p1=p1, short=sh)).to_csv(
        os.path.join(OUT, "ledger.csv"), index=False)

    def met(sp, name, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        v = np.bincount(wi, weights=s, minlength=NW)
        v = v[np.bincount(wi, minlength=NW) > 0]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s != 0
        return dict(arm=name, daypos=100 * float((s > 0).mean()),
                    trdpos=100 * float((s[tr] > 0).mean()) if tr.any() else 0.0,
                    flat=100 * float((~tr).mean()),
                    wkpos=100 * float((v > 0).mean()), dstreak=streak(s), wstreak=streak(v),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    worst=float(v.min()) * k, dd_top5=dp["dd_mean_top5"] * k,
                    ulcer=dp["ulcer"] * k)
    HDR = (f"{'arm':<32}{'day+%':>7}{'trdD+%':>8}{'flat%':>7}{'wk+%':>7}{'dStrk':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}")

    def show(r, tag=""):
        P_(f"{r['arm']:<32}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['flat']:>7.1f}"
           f"{r['wkpos']:>7.1f}{r['dstreak']:>7}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{r['worst']:>9,.0f}{tag}")

    # =====================================================================================
    # PHASE 1
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 1: the short sleeve's own consistency ledger (never measured)")
    P_(f"{'='*128}")
    P_(HDR)
    r_p1 = met(p1, "P1 LONG (incumbent)")
    show(r_p1)
    r_sh = met(sh, "SHORT sleeve standalone")
    show(r_sh)
    flatP1 = p1 == 0
    tradesS = sh != 0
    P_(f"\n   On the {int(flatP1.sum())} sessions P1 is FLAT ({100*flatP1.mean():.1f} %):")
    m = flatP1 & tradesS
    P_(f"      the short sleeve trades {int(m.sum())} of them ({100*m.sum()/max(flatP1.sum(),1):.1f} %)"
       f" and wins {100*float((sh[m] > 0).mean()) if m.any() else 0:.1f} % of those")
    P_(f"      W58's comparison numbers on the same question: axis B 49.4 %, B-MOM 56.9 %, "
       f"BREADTH01 52.3 %")
    both = (~flatP1) & tradesS
    P_(f"   On the {int(both.sum())} sessions BOTH trade, their daily correlation is "
       f"{float(np.corrcoef(p1[both], sh[both])[0,1]):+.3f}")
    P_(f"   Full-sample daily correlation: {float(np.corrcoef(p1, sh)[0,1]):+.3f} | "
       f"weekly: {float(np.corrcoef(np.bincount(wk_idx, weights=p1, minlength=NW), np.bincount(wk_idx, weights=sh, minlength=NW))[0,1]):+.3f}")

    # =====================================================================================
    # PHASE 2 - the weight scan at fixed drawdown
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 2: the combination, constant total risk, fixed "
       f"${DD_TARGET:,.0f} drawdown")
    P_(f"{'='*128}")
    v1 = np.bincount(wk_idx, weights=p1, minlength=NW)
    vs = np.bincount(wk_idx, weights=sh, minlength=NW)
    sd1, sds = v1.std(ddof=1), vs.std(ddof=1)
    shn = sh * (sd1 / sds) if sds > 0 else sh
    P_(HDR)
    show(r_p1)
    rows = []
    for w in WGRID:
        if w == 0:
            continue
        r = met((1 - w) * p1 + w * shn, f"P1 + SHORT w={w:.2f}")
        if r:
            r["w"] = w
            show(r); rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "wscan.csv"), index=False)

    # =====================================================================================
    # PHASE 3 - SUB-PERIOD STABILITY, the bar every W60 arm failed at 0 %
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 3: sub-period stability. Every W60 arm scored 0 % on 'all three'.")
    P_(f"{'='*128}")
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    P_(f"{'arm':<24}{'windows':>9}{'trdD+% wins':>14}{'weekly$ wins':>15}{'top5DD wins':>14}"
       f"{'ALL THREE':>12}")
    subrows = []
    for w in (0.10, 0.20, 0.30, 0.40, 0.50):
        comb = (1 - w) * p1 + w * shn
        c1 = c2 = c3 = c4 = tot = 0
        for eend in ends:
            b0 = eend - pd.DateOffset(months=24)
            mk = ((sdate > b0) & (sdate <= eend)).values
            a_, b_ = met(comb, "", mk), met(p1, "", mk)
            if a_ is None or b_ is None:
                continue
            tot += 1
            x1 = a_["trdpos"] > b_["trdpos"]; x2 = a_["weekly"] > b_["weekly"]
            x3 = a_["dd_top5"] < b_["dd_top5"]
            c1 += x1; c2 += x2; c3 += x3; c4 += (x1 and x2 and x3)
        P_(f"{f'P1 + SHORT w={w:.2f}':<24}{tot:>9}{100*c1/max(tot,1):>13.0f}%"
           f"{100*c2/max(tot,1):>14.0f}%{100*c3/max(tot,1):>13.0f}%{100*c4/max(tot,1):>11.0f}%")
        subrows.append(dict(w=w, n=tot, trd=100*c1/max(tot,1), wk=100*c2/max(tot,1),
                            dd=100*c3/max(tot,1), all3=100*c4/max(tot,1)))
    pd.DataFrame(subrows).to_csv(os.path.join(OUT, "subperiod.csv"), index=False)

    P_(f"\n   the SHORT SLEEVE'S OWN rolling record - the test that caught axis B at the 97th")
    P_(f"   percentile of its own history and B-MOM at the 98th:")
    rr = []
    for eend in ends:
        b0 = eend - pd.DateOffset(months=24)
        mk = ((sdate > b0) & (sdate <= eend)).values
        s_ = sh[mk]
        if len(s_) < 200:
            continue
        se = s_.std(ddof=1) / np.sqrt(len(s_))
        rr.append(dict(end=eend.date(), net=float(s_.sum()),
                       t=float(s_.mean() / se) if se > 0 else 0.0))
    RR = pd.DataFrame(rr)
    if len(RR):
        last = RR.iloc[-1]
        P_(f"      {len(RR)} windows | {100*float((RR['net'] > 0).mean()):.1f} % positive | "
           f"median t {RR['t'].median():+.2f} | latest t {last['t']:+.2f} at the "
           f"{100*float((RR['t'].values < last['t']).mean()):.0f}th percentile of its own history")
    P_(f"\n   per year (short sleeve standalone, pts/session):")
    yrs = sorted(set(sdate.dt.year))
    P_("      " + "  ".join(f"{y}: {sh[(sdate.dt.year == y).values].sum()/PV/max((sdate.dt.year==y).sum(),1):+.2f}"
                            for y in yrs))

    # =====================================================================================
    # PHASE 4 - NULLS
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 4: nulls (scan-matched; every draw takes its own best weight)")
    P_(f"{'='*128}")

    def best_over_w(series):
        b = None
        for w in WGRID:
            if w == 0:
                continue
            r = met((1 - w) * p1 + w * series, "")
            if r and (b is None or r["weekly"] > b["weekly"]):
                b = r
        return b
    real = best_over_w(shn)
    n1 = []
    for _ in range(NDRAW):
        k = int(RNG.integers(20, NS - 20))
        b = best_over_w(np.roll(shn, k))
        if b:
            n1.append((b["weekly"], b["trdpos"], b["wkpos"]))
    a1 = np.array(n1)
    P_(f"{'metric':<16}{'real':>12}{'N1 mean':>12}{'N1 p95':>12}{'percentile':>12}{'verdict':>10}")
    for j, (lab, key, hi) in enumerate((("weekly $", "weekly", True),
                                        ("traded-day %", "trdpos", True),
                                        ("week + %", "wkpos", True))):
        col = a1[:, j]
        v = real[key]
        p = 100 * float((col < v).mean()) if hi else 100 * float((col > v).mean())
        P_(f"{lab:<16}{v:>12,.2f}{col.mean():>12,.2f}{np.percentile(col, 95):>12,.2f}"
           f"{p:>11.1f}%{('PASS' if p >= 95 else 'fail'):>10}")
    P_(f"\n   N1 keeps the short sleeve's mean and vol and destroys only its ALIGNMENT with P1.")
    P_(f"   A pass says it earns WHEN P1 DOES NOT; a fail says it just earns.")
    pd.DataFrame(a1, columns=["weekly", "trdpos", "wkpos"]).to_csv(
        os.path.join(OUT, "nulls.csv"), index=False)
    P_(f"\n=== STATUS: nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
