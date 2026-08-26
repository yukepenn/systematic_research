"""WE_W53 TWO BOOKS (spec preregistered): is the overnight tape a second bet or the same bet?

W51b measured, for the first time in 52 waves, that HALF the object's money is earned between
18:00 and 08:00 ET. The campaign has always treated the 18:00->17:00 session as one book.

The fundamental law of active management says annualised Sharpe goes as IC x sqrt(N), and W36
verified that identity holds for this object to within 8 %. Breadth is therefore the only
lever that raises risk-adjusted return without a better signal - and this campaign has never
pulled it properly: every earlier portfolio test added a small FIXED weight of a second sleeve
instead of scanning weights at CONSTANT TOTAL EXPOSURE.

The wave carries a sharp preregistered prediction from my own unifying law: re-weighting two
books does not reduce events, so INTERIOR weights may win, but CORNER weights (all-night or
all-day) must not. Phase 4 C1 tries to falsify the law directly.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, classify, A, B                    # noqa: E402
from run_we_w51c import setup, entry_only, dd_profile                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W53_TWOBOOKS", "out")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20260853)
NIGHT_LEN = 840                      # 18:00 -> 08:00 ET, in minutes
NDRAW = 200
WGRID = np.round(np.arange(0.0, 1.001, 0.05), 3)


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "twobooks.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    sess_yr = pd.to_datetime(D["sess_date"]).year.values
    keys_w = sorted(set(sess_wk[sess_in]))
    NW = len(keys_w)
    wpos = {k: j for j, k in enumerate(keys_w)}
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)

    def build(pos, halt=1300.0, target=1000.0):
        base = fills_daily(D, pos, halt=halt, target=target)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(ent) < 200:
            return []
        sc, _ = causal_score(X, ent, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc, halt=halt, target=target)
                if A <= np.datetime64(x["et"]) < B]

    def vec_cm(trl):
        """weekly P&L vector and total contract-minutes"""
        v = np.zeros(NW); cm = 0.0
        for x in trl:
            i = i_of(x["et"])
            v[wpos[sess_wk[int(sid[i])]]] += x["pnl"]
            cm += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                   / np.timedelta64(1, "m"))
        return v, cm

    def met(v, ntr, cm, name, expo0=None):
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        sd = v.std(ddof=1)
        dp = dd_profile(v)
        return dict(arm=name, n=int(ntr), pts=round(float(v.sum() / PV / NS), 2),
                    wk=round(float(v.mean())),
                    wkpos=round(100 * float((v > 0).mean()), 1),
                    worst=round(float(v.min())), maxdd=round(dp["maxdd"]),
                    dd_top5=round(dp["dd_mean_top5"]), ulcer=round(dp["ulcer"]),
                    underwater=round(dp["pct_underwater"], 1),
                    mar=round(float(v.sum() / max(dp["maxdd"], 1e-9)), 2),
                    annshrp=round(float(v.mean() / sd * np.sqrt(52)) if sd > 0 else 0.0, 2),
                    eff=round(float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9, 3),
                    cveff=round(float(v.mean() / abs(cv)) if cv < 0 else 9.9, 3),
                    stress=round(float(v.mean() - STRESS_RT * ntr / len(v))),
                    expo=round(cm),
                    expo_pct=round(100 * cm / (expo0 if expo0 else max(cm, 1e-9)), 1))

    HDR = (f"{'arm':<30}{'trds':>6}{'pts':>7}{'wk$':>8}{'wk+%':>6}{'worst':>9}{'maxDD':>9}"
           f"{'top5DD':>9}{'ulcer':>8}{'MAR':>7}{'annShrp':>8}{'cvEff':>7}{'expo%':>7}"
           f"{'stress':>8}")

    def show(r):
        P_(f"{r['arm']:<30}{r['n']:>6}{r['pts']:>7.2f}{r['wk']:>8,.0f}{r['wkpos']:>6.1f}"
           f"{r['worst']:>9,.0f}{r['maxdd']:>9,.0f}{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}"
           f"{r['mar']:>7.2f}{r['annshrp']:>8.2f}{r['cveff']:>7.3f}{r['expo_pct']:>7.1f}"
           f"{r['stress']:>8,.0f}")

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    trs0 = build(posL)
    v0, cm0 = vec_cm(trs0)
    r0 = met(v0, len(trs0), cm0, "P1 INCUMBENT", cm0)
    P_(f"=== B1 GATE: {r0['pts']:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(r0['pts'] - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(r0["pts"] - 14.72) >= 0.6:
        out.close(); return

    # =====================================================================================
    # PHASE 1 - THE TWO BOOKS
    # =====================================================================================
    def in_window(i, start, length):
        d = (mod[i] - start) % 1440
        return d < length
    night = [x for x in trs0 if in_window(i_of(x["et"]), 1080, NIGHT_LEN)]
    day = [x for x in trs0 if not in_window(i_of(x["et"]), 1080, NIGHT_LEN)]
    vN, cmN = vec_cm(night)
    vDy, cmD = vec_cm(day)

    P_(f"\n{'='*112}\n=== PHASE 1: the two books as they already exist inside the object")
    P_(f"{'='*112}")
    P_(HDR)
    show(r0)
    rN = met(vN, len(night), cmN, "NIGHT 18:00-08:00 ET", cm0)
    rD = met(vDy, len(day), cmD, "DAY   08:00-17:00 ET", cm0)
    show(rN); show(rD)
    cor = float(np.corrcoef(vN, vDy)[0, 1])
    dec = np.argsort(v0)[:max(3, NW // 10)]
    cor_d = float(np.corrcoef(vN[dec], vDy[dec])[0, 1])
    P_(f"\n   weekly correlation NIGHT vs DAY, all {NW} weeks          : {cor:+.3f}")
    P_(f"   the same correlation INSIDE the worst decile ({len(dec)} weeks): {cor_d:+.3f}")
    P_(f"   (W43's lesson: unconditional decoupling is NECESSARY AND NOT SUFFICIENT - RTY/YM")
    P_(f"    correlated 0.04/0.03 with NQ unconditionally and still failed inside the tail.)")
    P_(f"\n   exposure split: NIGHT {100*cmN/cm0:.1f} % | DAY {100*cmD/cm0:.1f} % of "
       f"contract-minutes; money split NIGHT {100*vN.sum()/v0.sum():.1f} % | DAY "
       f"{100*vDy.sum()/v0.sum():.1f} %")
    yrs = sorted(set(sess_yr[sess_in]))

    def yr_vec(trl):
        a = np.zeros(len(yrs))
        for x in trl:
            y = sess_yr[int(sid[i_of(x["et"])])]
            a[yrs.index(y)] += x["pnl"] / PV
        return a
    nsy = np.array([max((sess_yr[sess_in] == y).sum(), 1) for y in yrs])
    P_(f"\n=== per year (pts/session) ===")
    P_(f"{'book':<30}" + "".join(f"{y:>12}" for y in yrs))
    for nm, trl in (("P1 INCUMBENT", trs0), ("NIGHT", night), ("DAY", day)):
        P_(f"{nm:<30}" + "".join(f"{x:>12.2f}" for x in yr_vec(trl) / nsy))
    pd.DataFrame([r0, rN, rD]).to_csv(os.path.join(OUT, "books.csv"), index=False)

    # =====================================================================================
    # PHASE 2 - CONSTANT-TOTAL-EXPOSURE WEIGHT SCAN
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 2: constant-total-exposure weight scan")
    P_(f"{'='*112}")
    P_("w = share of the incumbent's TOTAL contract-minutes allocated to the NIGHT book.")
    P_(f"The incumbent sits at w = {cmN/cm0:.3f} by construction and must reproduce exactly.")
    P_("Weights are fractional-contract arithmetic on the realised trade P&L; the session box")
    P_("still truncates the COMBINED book here (phase 3 tests per-book boxes with real re-runs).\n")

    def wscan(vA, cmA, nA, vB, cmB, nB, tot, grid=WGRID, label=""):
        rows = []
        for w in grid:
            aA = w * tot / max(cmA, 1e-9)
            aB = (1 - w) * tot / max(cmB, 1e-9)
            v = aA * vA + aB * vB
            ntr = aA * nA + aB * nB
            rows.append(met(v, ntr, tot, f"{label}w={w:.2f}", tot))
        return rows
    scan = wscan(vN, cmN, len(night), vDy, cmD, len(day), cm0)
    P_(HDR)
    show(r0)
    for r in scan:
        show(r)
    pd.DataFrame(scan).to_csv(os.path.join(OUT, "wscan.csv"), index=False)
    interior = [r for r in scan if 0.05 <= float(r["arm"].split("=")[1]) <= 0.95]
    best = max(interior, key=lambda r: r["mar"])
    corners = [r for r in scan if float(r["arm"].split("=")[1]) in (0.0, 1.0)]
    P_(f"\n   best INTERIOR weight by MAR: {best['arm']} -> MAR {best['mar']:.2f} "
       f"vs incumbent {r0['mar']:.2f}")
    P_(f"   corner weights: " + " | ".join(f"{r['arm']} MAR {r['mar']:.2f}" for r in corners))
    P_(f"   the unifying law predicts corners must NOT win -> "
       + ("law HOLDS here" if best["mar"] >= max(r["mar"] for r in corners)
          else "A CORNER WINS - the event-count law is challenged and must be reopened"))

    # =====================================================================================
    # PHASE 3 - SEPARATE RISK TRUNCATION (real re-runs)
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 3: per-book session boxes at the SAME dollar levels (no re-tuning)")
    P_(f"{'='*112}")
    night_ok = np.array([in_window(i, 1080, NIGHT_LEN) for i in range(n)])
    posN = entry_only(D, posL, night_ok)
    posD = entry_only(D, posL, ~night_ok)
    trN2, trD2 = build(posN), build(posD)
    vN2, cmN2 = vec_cm(trN2)
    vD2, cmD2 = vec_cm(trD2)
    P_(HDR)
    show(r0)
    show(met(vN2, len(trN2), cmN2, "NIGHT own box", cm0))
    show(met(vD2, len(trD2), cmD2, "DAY own box", cm0))
    vS = vN2 + vD2
    rS = met(vS, len(trN2) + len(trD2), cmN2 + cmD2, "SUM of per-book boxes", cm0)
    show(rS)
    sc = cm0 / max(cmN2 + cmD2, 1e-9)
    rSn = met(vS * sc, (len(trN2) + len(trD2)) * sc, (cmN2 + cmD2) * sc,
              "SUM rescaled to equal exposure", cm0)
    show(rSn)
    P_(f"\n   per-book boxes correlation: {float(np.corrcoef(vN2, vD2)[0,1]):+.3f} "
       f"(worst decile {float(np.corrcoef(vN2[dec], vD2[dec])[0,1]):+.3f})")
    scan3 = wscan(vN2, cmN2, len(trN2), vD2, cmD2, len(trD2), cm0, label="box ")
    b3 = max([r for r in scan3 if 0.05 <= float(r["arm"].split("=")[1]) <= 0.95],
             key=lambda r: r["mar"])
    P_(f"   best interior weight with per-book boxes: {b3['arm']} -> MAR {b3['mar']:.2f}, "
       f"pts {b3['pts']:.2f}, top5DD {b3['dd_top5']:,}, ulcer {b3['ulcer']:,}")
    pd.DataFrame(scan3).to_csv(os.path.join(OUT, "wscan_box.csv"), index=False)

    # =====================================================================================
    # PHASE 4 - CONTROL ARMS THAT ATTACK MY OWN LAW AND THIS HYPOTHESIS
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 4 C1: stand aside 10:30-12:00 ET, the only measured-negative window")
    P_(f"{'='*112}")
    P_("This REDUCES events, so the unifying law predicts it fails. If it wins, the law is wrong.")
    dead = (mod >= 630) & (mod < 720)
    trC1 = build(entry_only(D, posL, ~dead))
    vC1, cmC1 = vec_cm(trC1)
    P_(HDR)
    show(r0)
    show(met(vC1, len(trC1), cmC1, "C1 no 10:30-12:00 entries", cm0))

    P_(f"\n{'='*112}\n=== PHASE 4 C2: THE BINDING NULL - random contiguous time splits")
    P_(f"{'='*112}")
    P_(f"{NDRAW} random contiguous {NIGHT_LEN}-minute windows on the session clock, each")
    P_("weight-scanned identically. If a random split reproduces the NIGHT/DAY benefit, the")
    P_("benefit is variance-reduction arithmetic and not a property of the two tapes.\n")
    ent_i = np.array([i_of(x["et"]) for x in trs0])
    pnl_a = np.array([x["pnl"] for x in trs0])
    wk_a = np.array([wpos[sess_wk[int(sid[i])]] for i in ent_i])
    cm_a = np.array([x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                      / np.timedelta64(1, "m")) for x in trs0])
    mod_a = mod[ent_i]
    nulls = []
    for _ in range(NDRAW):
        s0 = int(RNG.integers(0, 1440))
        m_ = ((mod_a - s0) % 1440) < NIGHT_LEN
        if m_.sum() < 100 or (~m_).sum() < 100:
            continue
        vA = np.bincount(wk_a[m_], weights=pnl_a[m_], minlength=NW)
        vB = np.bincount(wk_a[~m_], weights=pnl_a[~m_], minlength=NW)
        cA, cB = float(cm_a[m_].sum()), float(cm_a[~m_].sum())
        sc_ = wscan(vA, cA, int(m_.sum()), vB, cB, int((~m_).sum()), cm0)
        it = [r for r in sc_ if 0.05 <= float(r["arm"].split("=")[1]) <= 0.95]
        bb = max(it, key=lambda r: r["mar"])
        nulls.append(dict(start=s0, corr=float(np.corrcoef(vA, vB)[0, 1]),
                          best_mar=bb["mar"], best_pts=bb["pts"],
                          best_top5=bb["dd_top5"], best_ulcer=bb["ulcer"],
                          best_shrp=bb["annshrp"]))
    NL = pd.DataFrame(nulls)
    NL.to_csv(os.path.join(OUT, "nulls.csv"), index=False)
    P_(f"{'quantity':<22}{'NIGHT/DAY':>12}{'null mean':>12}{'null p95':>12}"
       f"{'percentile':>12}{'verdict':>10}")
    for key, val, hi in (("weekly correlation", cor, False),
                         ("best interior MAR", best["mar"], True),
                         ("best interior pts", best["pts"], True),
                         ("best interior top5DD", best["dd_top5"], False),
                         ("best interior ulcer", best["ulcer"], False),
                         ("best interior annShrp", best["annshrp"], True)):
        col = {"weekly correlation": "corr", "best interior MAR": "best_mar",
               "best interior pts": "best_pts", "best interior top5DD": "best_top5",
               "best interior ulcer": "best_ulcer", "best interior annShrp": "best_shrp"}[key]
        a = NL[col].values.astype(float)
        p = 100 * float((a < val).mean() if hi else (a > val).mean())
        P_(f"{key:<22}{val:>12.3f}{a.mean():>12.3f}"
           f"{np.quantile(a, 0.95 if hi else 0.05):>12.3f}{p:>11.1f}%"
           f"{('PASS' if p >= 95 else 'fail'):>10}")
    P_(f"\n   preregistered bar: >= 95th percentile on BOTH pts and MAR.")
    pm = 100 * float((NL['best_mar'].values < best['mar']).mean())
    pp = 100 * float((NL['best_pts'].values < best['pts']).mean())
    P_(f"   pts {pp:.1f}%  MAR {pm:.1f}%  -> "
       + ("BOTH CLEAR" if (pp >= 95 and pm >= 95)
          else "DOES NOT CLEAR - the NIGHT/DAY split is one bet sampled twice"))
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
