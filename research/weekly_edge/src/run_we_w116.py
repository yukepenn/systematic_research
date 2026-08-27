"""WE_W116 - FOLLOW_MORNING, full adjudication under the NEW regime doctrine.

Spec: runs/WE_W116_FMADJUDICATE/spec.yaml, committed BEFORE this ran (5bd8b22).

The owner has superseded the rule that produced W114's verdict: old-regime failure is no longer an
automatic promotion veto, and REGIME_LOCAL is a RISK CLASSIFICATION rather than a demotion. So the
object is judged again on the criteria that now govern.

Nothing is optimised here. The plateau is MEASURED, not searched (directive section 23).
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w114 import Win, RTH0, MORN_B, DEC, EXIT                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W116_FMADJUDICATE", "out")
os.makedirs(OUT, exist_ok=True)
W110W = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out", "weekly.csv")
DDT = 20245.0
SEED = 116
NSHIFT = 1000
DECS = [678, 693, 708, 723, 738]
EXITS = [929, 944, 959]


def acc_of(mv, d):
    g = np.isfinite(mv) & (np.sign(mv) != 0) & (d != 0)
    return float((np.sign(mv[g]) == d[g]).mean()) if g.sum() else np.nan


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fmadj.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    W = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN")
    OLD = Win("2006-01-05", "2021-12-31 17:00", False, "OLD")
    P_(f"    MODERN {len(W.sess_in):,} sessions / OLD {len(OLD.sess_in):,} "
       f"[{_time.time()-t0:.0f}s]")

    md = W.morn_dir()
    R = W.run(DEC, EXIT, md)
    mv, take, cost = R["mv"], R["take"], R["cost"]
    dirv = np.nan_to_num(md)
    st = W.stats(R)
    pstar = R["pstar"]

    # ================================================================== 1. causal ledger
    P_("")
    P_("=" * 126)
    P_("=== 1. THE CAUSAL LEDGER (directive section 4)")
    P_("=" * 126)
    P_("    end-stamped semantics, verified against the substrate:")
    for lab, m_, uo in (("bar 571 OPEN  = the 09:30:00 print (true RTH open)", RTH0, True),
                        ("bar 689 CLOSE = 11:29  (the INFORMATION anchor)", MORN_B, False),
                        ("bar 709 OPEN  = the 11:48:00 print (the FILL)", DEC + 1, True),
                        ("bar 944 CLOSE = 15:44  (the EXIT)", EXIT, False)):
        v = W.at(m_, use_open=uo)
        P_(f"        {lab:<52} present on {100*float(np.isfinite(v)[W.win].mean()):5.1f} % of sessions")
    nmid = int(((W.mod > MORN_B) & (W.mod <= DEC) & W.win[W.sid]).sum())
    P_("")
    P_(f"    THE NINETEEN-MINUTE GAP. Bars 690-708 (11:30-11:48) EXIST - {nmid:,} of them in window")
    P_("    - and are NOT used. That gap was INHERITED from W108's LANE C geometry, not designed.")
    # teeth: perturbing 690..708 must not move the direction; an 11:48-anchored variant must move
    c2 = W.c.copy()
    gapm = (W.mod > MORN_B) & (W.mod < DEC + 1)
    c2[gapm] = c2[gapm] * 1.05 + 137.0
    W2 = object.__new__(Win)
    W2.__dict__.update(W.__dict__); W2.c = c2
    md_pert = W2.morn_dir()
    unchanged = bool(np.allclose(np.nan_to_num(md), np.nan_to_num(md_pert)))
    md1148 = np.sign(W.at(DEC) - W.at(RTH0, use_open=True))
    md1148_p = np.sign(W2.at(DEC) - W2.at(RTH0, use_open=True))
    moved = not bool(np.allclose(np.nan_to_num(md1148), np.nan_to_num(md1148_p)))
    P_(f"        corrupt bars 690-708 -> the 11:29-anchored direction changes: "
       f"{'NO  (the gap is genuinely unused)' if unchanged else 'YES - LEAKAGE'}")
    P_(f"        the same corruption -> an 11:48-anchored direction changes: "
       f"{'YES (the probe has teeth)' if moved else 'NO - probe is dead'}")

    P_("")
    P_("    PROVENANCE of the 11:48 decision minute, from committed artifacts:")
    P_("        11:48 first appears in a committed spec in runs/WE_W108_REVRANGE/spec.yaml as the")
    P_("        decision minute for SIX FADE MECHANISMS. FOLLOW_MORNING did not exist as an object")
    P_("        then - it first appears as a CONTROL at that inherited geometry in W111b. No wave")
    P_("        ever selected the minute by comparing FOLLOW_MORNING outcomes across minutes.")
    P_("        => the single-cell null W114 used is DEFENSIBLE. The conservative best-of-15 bar is")
    P_("        computed below anyway, so the provenance argument need not be relied on.")

    # ================================================================== 2. plateau + selection
    P_("")
    P_("=" * 126)
    P_("=== 2. THE TIMING PLATEAU - MEASURED, NOT SEARCHED (section 23). $/trade and edge in pp.")
    P_("=" * 126)
    P_(f"{'decide':<10}" + "".join(f"{f'exit {e//60:02d}:{e%60:02d}':>22}" for e in EXITS))
    cells = []
    for d_ in DECS:
        line = f"{f'{d_//60:02d}:{d_%60:02d}':<10}"
        for e in EXITS:
            m2 = np.sign(W.at(d_ - 19) - W.at(RTH0, use_open=True))
            RR = W.run(d_, e, m2)
            s2 = W.stats(RR)
            a2 = acc_of(RR["mv"][RR["take"]], np.nan_to_num(m2)[RR["take"]])
            cells.append((RR, s2))
            line += f"{s2['per_trade']:>13,.0f}{100*(a2-RR['pstar']):>8.2f}pp"
        P_(line)
    P_("")
    P_("    SELECTION BURDEN, both readings:")
    nul1 = np.array([float((rng.choice([-1.0, 1.0], size=int(take.sum())) * mv[take] - cost).mean())
                     for _ in range(2000)])
    p95_1 = float(np.percentile(nul1, 95))
    mx = np.empty(2000)
    for b in range(2000):
        vals = []
        for RR, _ in cells:
            m3 = RR["take"]
            vals.append(float((rng.choice([-1.0, 1.0], size=int(m3.sum())) * RR["mv"][m3]
                               - RR["cost"]).mean()))
        mx[b] = max(vals)
    p95_k = float(np.percentile(mx, 95))
    P_(f"        real ${st['per_trade']:,.0f}/trade")
    P_(f"        single-cell coin null p95 ${p95_1:,.0f}  -> "
       f"{100*float((nul1 < st['per_trade']).mean()):.1f}th percentile   "
       f"{'CLEARS' if st['per_trade'] > p95_1 else 'fails'}")
    P_(f"        CONSERVATIVE best-of-15 bar ${p95_k:,.0f}  -> "
       f"{'CLEARS' if st['per_trade'] > p95_k else 'FAILS'}"
       "   <- treats the minute as if it had been chosen here")
    P_("")
    P_("    THE FRESHER-INFORMATION DIAGNOSTIC (a DIFFERENT rule, NOT substituted for the primary):")
    R48 = W.run(DEC, EXIT, md1148)
    s48 = W.stats(R48)
    a48 = acc_of(R48["mv"][R48["take"]], np.nan_to_num(md1148)[R48["take"]])
    P_(f"        direction from the 11:29 close (PRIMARY): ${st['per_trade']:>6,.0f}/trade   "
       f"edge {100*(acc_of(mv[take], dirv[take]) - pstar):>5.2f}pp   N {st['n']}")
    P_(f"        direction from the 11:48 close (fresher): ${s48['per_trade']:>6,.0f}/trade   "
       f"edge {100*(a48 - R48['pstar']):>5.2f}pp   N {s48['n']}")

    # ================================================================== 3. dashboard
    P_("")
    P_("=" * 126)
    P_("=== 3. THE DASHBOARD (section 41). ALL standardised windows printed together (section 33).")
    P_("===    $/trade AND edge in accuracy points above p* - W115 showed these can diverge.")
    P_("=" * 126)
    dts = W.sdate[W.sess_in]
    ser = R["pnl"][W.sess_in]; tk = R["take"][W.sess_in]
    mvw = mv[W.sess_in]; dw = dirv[W.sess_in]
    last = dts.max()
    WINS = [("t3m", dts >= last - pd.Timedelta(days=91)),
            ("t6m", dts >= last - pd.Timedelta(days=182)),
            ("t12m", dts >= last - pd.Timedelta(days=365)),
            ("YTD 2026", dts.year == 2026),
            ("prior yr 2025", dts.year == 2025),
            ("t24m", dts >= last - pd.Timedelta(days=730)),
            ("2022-current", np.ones(len(dts), bool))]
    P_(f"{'window':<16}{'N':>6}{'$/trade':>10}{'edge pp':>10}{'hit%':>8}{'net $':>12}"
       f"{'wk $':>9}{'pos wk%':>9}{'maxDD':>10}{'CVaR5':>9}{'worst':>10}")
    rows = []
    for lab, m_ in WINS:
        mm = m_ & tk
        if mm.sum() < 10:
            continue
        pn = ser[mm]
        em = float(np.abs(mvw[mm]).mean())
        ps = 0.5 * (1 + cost / max(em, 1e-9))
        a = acc_of(mvw[mm], dw[mm])
        s3 = np.zeros(len(dts)); s3[mm] = pn
        wv = pd.Series(s3).groupby(W.wk).sum().to_numpy()
        wv = wv[wv != 0] if (wv != 0).any() else wv
        dp = dd_profile(wv)
        srt = np.sort(pn)
        P_(f"{lab:<16}{int(mm.sum()):>6}{pn.mean():>10,.0f}{100*(a-ps):>9.2f}pp"
           f"{100*float((pn>0).mean()):>7.1f}%{pn.sum():>12,.0f}{wv.mean():>9,.0f}"
           f"{100*float((wv>0).mean()):>8.1f}%{dp['maxdd']:>10,.0f}"
           f"{srt[:max(1,int(0.05*len(srt)))].mean():>9,.0f}{srt[0]:>10,.0f}")
        rows.append(dict(window=lab, n=int(mm.sum()), per_trade=float(pn.mean()),
                         edge_pp=100 * (a - ps), net=float(pn.sum())))
    Rold = OLD.run(DEC, EXIT, OLD.morn_dir())
    sold = OLD.stats(Rold)
    aold = acc_of(Rold["mv"][Rold["take"]], np.nan_to_num(OLD.morn_dir())[Rold["take"]])
    P_(f"{'2006-2021 [diag]':<16}{sold['n']:>6}{sold['per_trade']:>10,.0f}"
       f"{100*(aold-Rold['pstar']):>9.2f}pp{sold['hit']:>7.1f}%{sold['net']:>12,.0f}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "dashboard.csv"), index=False)

    P_("")
    P_("    ⭐ THE ACCURACY-vs-DOLLARS DIVERGENCE W115 SURFACED, per calendar year:")
    P_(f"{'year':<8}{'N':>6}{'E|move| $':>12}{'$/trade':>10}{'edge pp':>10}")
    for y in sorted(set(dts.year)):
        mm = (dts.year == y) & tk
        if mm.sum() < 20:
            continue
        em = float(np.abs(mvw[mm]).mean())
        ps = 0.5 * (1 + cost / max(em, 1e-9))
        P_(f"{y:<8}{int(mm.sum()):>6}{em:>12,.0f}{ser[mm].mean():>10,.0f}"
           f"{100*(acc_of(mvw[mm], dw[mm])-ps):>9.2f}pp")

    P_("")
    P_("    CONCENTRATION and RISK (section 41):")
    pn = ser[tk]; srt = np.sort(pn)[::-1]
    P_(f"        median ${np.median(pn):,.0f}   trimmed(5%) "
       f"${pn[(pn>np.percentile(pn,5))&(pn<np.percentile(pn,95))].mean():,.0f}   "
       f"skew {pd.Series(pn).skew():.2f}   worst ${pn.min():,.0f}")
    P_(f"        top1 {100*srt[0]/pn.sum():.1f}%  top5 {100*srt[:5].sum()/pn.sum():.1f}%  "
       f"top10 {100*srt[:10].sum()/pn.sum():.1f}%  top20 {100*srt[:20].sum()/pn.sum():.1f}%")
    P_("")
    P_("    COST SENSITIVITY:")
    P_("        " + "   ".join(
        f"{m:.0f}x ${W.stats(W.run(DEC, EXIT, md, mult=m))['per_trade']:,.0f}" for m in (0, 1, 2, 3)))
    P_("")
    P_("    CONTROLS on the SAME sessions (section 29):")
    for lab, d_ in (("always LONG", np.where(W.win, 1.0, 0.0)),
                    ("always SHORT", np.where(W.win, -1.0, 0.0)),
                    ("FADE morning", -md)):
        s4 = W.stats(W.run(DEC, EXIT, d_))
        P_(f"        {lab:<16} ${s4['per_trade']:>6,.0f}/trade   N {s4['n']}")
    nrand = np.array([float((np.where(rng.random(int(take.sum())) < 0.5, 1.0, -1.0)
                             * mv[take] - cost).mean()) for _ in range(2000)])
    P_(f"        {'matched RANDOM':<16} ${nrand.mean():>6,.0f}/trade  (p95 ${np.percentile(nrand,95):,.0f})")

    # ================================================================== 4. portfolio
    P_("")
    P_("=" * 126)
    P_("=== 4. MARGINAL PORTFOLIO VALUE (section 22) - the half that decides the book")
    P_("=" * 126)
    WK = pd.read_csv(W110W)
    s5 = np.zeros(W.NS); s5[take] = R["pnl"][take]
    fw = pd.Series(s5[W.sess_in]).groupby(W.wk).sum()
    J = pd.DataFrame(dict(week=WK["week"], p1=WK["p1"], xm=WK["xm"])).set_index("week")
    J["fm"] = fw
    J = J.dropna()
    P_(f"    {len(J)} common weeks")

    def mixw(cols, how):
        if how == "invvol":
            w = np.array([1.0 / max(J[c].std(ddof=1), 1e-9) for c in cols])
        else:                                     # income-matched
            w = np.array([1.0 / max(abs(J[c].mean()), 1e-9) for c in cols])
        w = w / w.sum() * len(cols)
        return sum(w[i] * J[cols[i]] for i in range(len(cols))) / len(cols)

    def summ(v):
        vv = np.asarray(v, float)
        dp = dd_profile(vv)
        srt = np.sort(vv)
        return dict(wk=vv.mean(), maxdd=dp["maxdd"],
                    fixdd=vv.mean() * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((vv > 0).mean()),
                    cvar=float(srt[:max(1, int(0.05 * len(srt)))].mean()),
                    t=vv.mean() / max(vv.std(ddof=1) / np.sqrt(len(vv)), 1e-9))

    P_("")
    P_(f"{'book':<36}{'conv':<12}{'wk $':>9}{'maxDD':>10}{'wk$@fixDD':>11}"
       f"{'pos wk%':>9}{'CVaR5':>9}{'t':>7}")
    BASE = {}
    for how in ("invvol", "income"):
        for lab, cols in (("P1/PCT", ["p1"]), ("P1/PCT + XM", ["p1", "xm"]),
                          ("P1/PCT + XM + FOLLOW", ["p1", "xm", "fm"]),
                          ("P1/PCT + FOLLOW", ["p1", "fm"])):
            v = J[cols[0]] if len(cols) == 1 else mixw(cols, how)
            s6 = summ(v)
            BASE[(how, lab)] = s6
            P_(f"{lab:<36}{how:<12}{s6['wk']:>9,.0f}{s6['maxdd']:>10,.0f}"
               f"{s6['fixdd']:>11,.0f}{s6['poswk']:>8.1f}%{s6['cvar']:>9,.0f}{s6['t']:>7.2f}")
        P_("")
    d_iv = BASE[("invvol", "P1/PCT + XM + FOLLOW")]["fixdd"] - BASE[("invvol", "P1/PCT + XM")]["fixdd"]
    d_im = BASE[("income", "P1/PCT + XM + FOLLOW")]["fixdd"] - BASE[("income", "P1/PCT + XM")]["fixdd"]
    P_(f"    INCREMENTAL fixed-DD weekly $ from adding FOLLOW to P1/PCT+XM:")
    P_(f"        inverse-vol {d_iv:+,.0f}   income-matched {d_im:+,.0f}   "
       f"-> RANGE {min(d_iv,d_im):+,.0f} to {max(d_iv,d_im):+,.0f}")

    # ---- downside, against a circular-shift null
    P_("")
    P_("    DOWNSIDE BEHAVIOUR against a 1,000-shift circular null (W110's instrument):")
    comb = mixw(["p1", "xm"], "invvol").to_numpy()
    fmv = J["fm"].to_numpy()
    p1v = J["p1"].to_numpy()
    NW = len(J)

    def dstats(a, b):
        m = a < 0
        q = np.percentile(a, 10)
        lo = a <= q
        return dict(rho=float(np.corrcoef(a, b)[0, 1]),
                    rho_lose=float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 5 else np.nan,
                    p_both=float((b[m] < 0).mean()) if m.sum() else np.nan,
                    dec_overlap=float(((a <= q) & (b <= np.percentile(b, 10))).mean()),
                    contrib=float(b[m].mean()) if m.sum() else np.nan,
                    tailbeta=float(np.polyfit(a[lo], b[lo], 1)[0]) if lo.sum() > 5 else np.nan)

    for lab, a_ in (("vs P1/PCT", p1v), ("vs P1/PCT+XM combined book", comb)):
        real = dstats(a_, fmv)
        nul = [dstats(a_, np.roll(fmv, k)) for k in range(1, min(NSHIFT, NW))]
        NN = pd.DataFrame(nul)
        P_(f"        --- {lab}  (unconditional P(FM<0) = {float((fmv<0).mean()):.3f}) ---")
        for k, rd in (("rho", "higher=coupled"), ("rho_lose", "rho | book losing"),
                      ("p_both", "P(FM<0 | book<0)"), ("dec_overlap", "worst-decile overlap"),
                      ("contrib", "$ FM makes on book-losing weeks"),
                      ("tailbeta", "tail beta in book's worst decile")):
            nv = NN[k].to_numpy()
            P_(f"            {rd:<36}{real[k]:>10.3f}   null mean {np.nanmean(nv):>8.3f}"
               f"   p95 {np.nanpercentile(nv,95):>8.3f}"
               f"   -> {100*float(np.nanmean(nv < real[k])):>5.1f}th")

    J.to_csv(os.path.join(OUT, "weekly_joint.csv"))
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
