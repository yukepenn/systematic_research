"""WE_W104 - DOES `XM_CONFLICT` GENERALISE ACROSS THE SESSION?

Spec: runs/WE_W104_XMGENERAL/spec.yaml, committed BEFORE this ran.

The same construction transplanted into seven segments, nothing re-fitted. Primary is the
EQUAL-WEIGHT MEAN of $/trade across all seven, chosen before the run so no segment can be
cherry-picked. Best-of-7 coin null on the individual cells. Zero-lag join test re-run on OVERNIGHT
bars specifically.
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
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W104_XMGENERAL", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
NPERM = 200
SEED = 104
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
# (name, first minute, last minute inclusive, decision offset)
SEG = [("ON_ASIA", 1080, 1439, 54), ("ON_EU", 0, 479, 72), ("PRE", 480, 569, 15),
       ("MORN", 585, 689, 16), ("MID", 690, 809, 18), ("AFT", 810, 944, 20),
       ("POST", 960, 1019, 18)]


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "general.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c = D["o"], D["c"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    wk = wkall[sess_in]
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    # ------------------------------------------------------------------ B1 on OVERNIGHT bars
    P_("=" * 122)
    P_("=== B1: the zero-lag known-answer test, recomputed on OVERNIGHT bars specifically.")
    P_("===     A join that is sound at 10:00 is not automatically sound at 03:00.")
    P_("=" * 122)
    on_mask = (mod >= 1080) | (mod < 480)
    okb = True
    for k in XM:
        for tag, msk in (("RTH  ", (mod >= 570) & (mod < 960)), ("NIGHT", on_mask)):
            a_ = np.log(c[1:] / c[:-1]); b_ = np.log(XD[k][1:] / XD[k][:-1])
            mm = msk[1:] & np.isfinite(a_) & np.isfinite(b_)
            cors = {}
            for lg in (-2, -1, 0, 1, 2):
                if lg < 0:
                    aa, bb, m3 = a_[-lg:], b_[:lg], mm[-lg:]
                elif lg > 0:
                    aa, bb, m3 = a_[:-lg], b_[lg:], mm[:-lg]
                else:
                    aa, bb, m3 = a_, b_, mm
                g = m3 & np.isfinite(aa) & np.isfinite(bb)
                cors[lg] = float(np.corrcoef(aa[g], bb[g])[0, 1])
            best = max(cors, key=cors.get)
            okb &= (best == 0)
            P_(f"    {k:<4} {tag}  " + "  ".join(f"lag{lv:+d} {cors[lv]:+.4f}"
                                                 for lv in (-2, -1, 0, 1, 2)) +
               f"   argmax {best:+d}  {'PASS' if best == 0 else 'FAIL'}")
    if not okb:
        P_("\n    A JOIN IS LAGGED. No cross-market number is issued.")
        out.close(); return

    # ------------------------------------------------------------------ the seven cells
    def at(mv, arr, uo=False):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_])
        return r

    def cell(a_mod, d_mod, x_mod):
        pa = at(a_mod, o, True)
        pdc = at(d_mod, c)
        pe = at(d_mod + 1, o, True)
        px = at(x_mod, c)
        drive = np.sign(pdc - pa)
        acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
        for k in XM:
            aa, bb = at(a_mod, XD[k]), at(d_mod, XD[k])
            r_ = np.log(bb / aa)
            s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
            z = r_ / np.maximum(s_, 1e-12)
            g = np.isfinite(z); acc[g] += z[g]; cnt[g] += 1
        xs = np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
        okm = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px) &
               np.isfinite(xs) & (drive != 0) & (xs != 0))
        cst = COMM_RT + TICKV * (float(prof.loc[d_mod + 1]) + float(prof.loc[x_mod])) / 2.0
        move = (px - pe) * PV
        conf = okm & (xs != drive)
        agre = okm & (xs == drive)
        return drive, okm, conf, agre, move, cst
    P_("")
    P_("=" * 122)
    P_("=== THE SEVEN CELLS. Same construction, nothing re-fitted. p* computed per cell.")
    P_("=" * 122)
    P_(f"{'segment':<10}{'decide':<8}{'hold':<8}{'N':>6}{'share':>8}{'E|move| $':>11}"
       f"{'cost':>7}{'p*':>8}{'hit%':>8}{'vs p*':>8}{'$/trade':>10}{'net $':>11}"
       f"{'AGREE $/tr':>12}")
    rows = []
    STORE = {}
    for nm, a_mod, x_mod, off in SEG:
        d_mod = a_mod + off
        dr, okm, cf, ag, move, cst = cell(a_mod, d_mod, x_mod)
        if cf.sum() < 30:
            P_(f"{nm:<10} too few sessions ({int(cf.sum())})"); continue
        pnl = dr * move - cst
        em = float(np.abs(move[okm]).mean())
        ps = 0.5 * (1 + cst / em)
        hit = float((dr[cf] * move[cf] > 0).mean())
        P_(f"{nm:<10}{f'{(a_mod+off)//60:02d}:{(a_mod+off)%60:02d}':<8}"
           f"{f'{x_mod//60:02d}:{x_mod%60:02d}':<8}{int(cf.sum()):>6}"
           f"{100*cf.sum()/max(okm.sum(),1):>7.1f}%{em:>11,.0f}{cst:>7.2f}{ps:>8.4f}"
           f"{100*hit:>7.2f}%{100*(hit-ps):>8.2f}{pnl[cf].mean():>10,.0f}"
           f"{pnl[cf].sum():>11,.0f}{pnl[ag].mean():>12,.0f}")
        rows.append(dict(segment=nm, decide=d_mod, hold=x_mod, n=int(cf.sum()),
                         share=100 * cf.sum() / max(okm.sum(), 1), e_move=em, cost=cst,
                         p_star=ps, hit=hit, per_trade=float(pnl[cf].mean()),
                         net=float(pnl[cf].sum()), agree_per_trade=float(pnl[ag].mean())))
        STORE[nm] = (cf.copy(), move.copy(), cst, dr.copy())
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "cells.csv"), index=False)

    # ------------------------------------------------------------------ the PRIMARY
    prim = float(DF["per_trade"].mean())
    rng = np.random.default_rng(SEED)
    mean_null = np.empty(NPERM); max_null = np.empty(NPERM)
    keys = list(STORE)
    for b_ in range(NPERM):
        vals = []
        for kk in keys:
            cf, move, cst, _ = STORE[kk]
            N = int(cf.sum())
            s_ = rng.choice([-1.0, 1.0], size=N)
            vals.append(float((s_ * move[cf] - cst).mean()))
        mean_null[b_] = np.mean(vals); max_null[b_] = np.max(vals)
    P_("")
    P_("=" * 122)
    P_("=== THE PRIMARY: equal-weight mean of $/trade across all seven cells - ONE statistic,")
    P_("===   fixed before the run so no segment can be cherry-picked.")
    P_("=" * 122)
    P_(f"    real  ${prim:,.0f}/trade")
    P_(f"    coin null on the same statistic: mean ${mean_null.mean():,.0f} "
       f"sd ${mean_null.std(ddof=1):,.0f}   p95 ${np.percentile(mean_null,95):,.0f}"
       f"   -> {100*float((mean_null < prim).mean()):.1f}th percentile")
    verdict = ("GENERALISES" if prim > np.percentile(mean_null, 95) else
               "DOES NOT GENERALISE - the mechanism is opening-auction-specific")
    P_(f"    VERDICT: {verdict}")
    P_("")
    P_(f"    best-of-7 coin null (for reading the INDIVIDUAL cells): mean "
       f"${max_null.mean():,.0f}  p95 ${np.percentile(max_null,95):,.0f}")
    mx95 = float(np.percentile(max_null, 95))
    P_(f"{'segment':<10}{'$/trade':>10}{'own p* cleared':>17}{'beats best-of-7 p95':>22}")
    for _, r_ in DF.sort_values("per_trade", ascending=False).iterrows():
        P_(f"{r_['segment']:<10}{r_['per_trade']:>10,.0f}"
           f"{('YES' if r_['hit'] > r_['p_star'] else 'no'):>17}"
           f"{('YES' if r_['per_trade'] > mx95 else 'no'):>22}")
    pd.DataFrame(dict(perm=np.arange(NPERM), mean=mean_null, mx=max_null)).to_csv(
        os.path.join(OUT, "null.csv"), index=False)

    # ------------------------------------------------------------------ the mechanism question
    P_("")
    P_("=" * 122)
    P_("=== DOES IT CONCENTRATE NEAR A SESSION OPEN? (18:00 CME open, 09:30 RTH open)")
    P_("=" * 122)
    P_(f"{'segment':<10}{'starts at':<12}{'minutes after an open':>24}{'$/trade':>10}")
    for _, r_ in DF.iterrows():
        a_mod = [s[1] for s in SEG if s[0] == r_["segment"]][0]
        d_ = min((a_mod - 1080) % 1440, (a_mod - 570) % 1440)
        P_(f"{r_['segment']:<10}{f'{a_mod//60:02d}:{a_mod%60:02d}':<12}{d_:>24}"
           f"{r_['per_trade']:>10,.0f}")
    P_("    reference (not a test): RTH open 09:31 -> decide 09:45 -> hold 15:45 = $560/trade")

    # ------------------------------------------------------------------ correlation with the base
    P_("")
    P_("=" * 122)
    P_("=== IS ANY SURVIVOR A SECOND COPY OF THE SAME TRADE? weekly rho vs P1/PCT and vs the")
    P_("===   known RTH-open object.")
    P_("=" * 122)
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p1 = vl.astype(np.int8)
    bb = fills_daily(D, p1, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    trP = gfills(D, p1, np.where(sc >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
    w_ = {}
    for x in trP:
        for ts in (x["et"], x["xt"]):
            pp = pd.Timestamp(ts); m2 = pp.hour * 60 + pp.minute
            w_[m2] = w_.get(m2, 0.0) + x["u"]
    rP = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) / max(sum(w_.values()), 1)
    sP1 = np.zeros(NSESS)
    for x in trP:
        si = int(sid[i_of(x["et"])])
        if win[si]:
            sP1[si] += x["pnl"] - rP * x["u"]
    drR, okR, cfR, _, moveR, cstR = cell(571, 585, 945)
    sR = np.zeros(NSESS); sR[cfR] = drR[cfR] * moveR[cfR] - cstR

    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wk).sum().to_numpy()
    wp, wr = wkv(sP1), wkv(sR)
    P_(f"{'segment':<10}{'wk$':>9}{'wk$@fixDD':>11}{'wk+%':>8}{'rho vs P1':>12}"
       f"{'rho vs RTH-open':>18}")
    crows = []
    for nm in STORE:
        cf, move, cst, dr = STORE[nm]
        s_ = np.zeros(NSESS); s_[cf] = dr[cf] * move[cf] - cst
        w_ = wkv(s_)
        dp = dd_profile(w_)
        P_(f"{nm:<10}{w_.mean():>9,.0f}"
           f"{w_.mean()*DDT/max(dp['maxdd'],1e-9):>11,.0f}"
           f"{100*float((w_>0).mean()):>7.1f}%{float(np.corrcoef(w_,wp)[0,1]):>12.3f}"
           f"{float(np.corrcoef(w_,wr)[0,1]):>18.3f}")
        crows.append(dict(segment=nm, weekly=float(w_.mean()),
                          fixdd=float(w_.mean()) * DDT / max(dp["maxdd"], 1e-9),
                          poswk=100 * float((w_ > 0).mean()),
                          rho_p1=float(np.corrcoef(w_, wp)[0, 1]),
                          rho_rth=float(np.corrcoef(w_, wr)[0, 1])))
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "corr.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
