"""WE_W101 - THE DIRECTION QUESTION.

Spec: runs/WE_W101_DIRECTION/spec.yaml, committed BEFORE this ran.

W99 priced the bar exactly: a one-trade direction call on NQ breaks even between 50.5 % and
51.4 %. W100 showed the entire short book is that one question asked 1,058 times. So the question
is not "build a short engine" - it is "does any causal statement we can make at 09:45 clear that
bar". Nine predictors, three decision times, one entry, hold to 15:45, size 1, no box, no throttle,
no sizing. The crudest possible instrument, because the question is about the INFORMATION.

Includes the zero-lag known-answer test on the cross-market join. This repo has had four
cross-substrate alignment defects; a one-bar ES lead would manufacture every cross-market cell.
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
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W101_DIRECTION", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
TS = [("09:45", 585), ("10:30", 630), ("11:30", 690)]
EXIT_MOD = 945                       # 15:45
NPERM = 200
SEED = 101
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "direction.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, fb = D["n"], D["t"], D["sid"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    sdate_all = pd.to_datetime(D["sess_date"])
    NSESS = D["n_sess"]

    # ------------------------------------------------------------------ B1: the cross-market join
    P_("=" * 118)
    P_("=== B1: the ZERO-LAG KNOWN-ANSWER TEST on the cross-market join.")
    P_("===     If ES leads NQ by one bar in this join, every cross-market cell below is a lie.")
    P_("=" * 118)
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    ok = True
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        d_ = d_.set_index("time")["close"].rename(k)
        j = nq.join(d_, how="inner")
        rn = np.diff(np.log(j["nq"].to_numpy()))
        rx = np.diff(np.log(j[k].to_numpy()))
        cors = {}
        for lagv in (-2, -1, 0, 1, 2):
            if lagv < 0:
                a_, b_ = rn[-lagv:], rx[:lagv]
            elif lagv > 0:
                a_, b_ = rn[:-lagv], rx[lagv:]
            else:
                a_, b_ = rn, rx
            m_ = np.isfinite(a_) & np.isfinite(b_)
            cors[lagv] = float(np.corrcoef(a_[m_], b_[m_])[0, 1])
        best = max(cors, key=cors.get)
        good = best == 0
        ok &= good
        P_(f"    {k:<4} joined {len(j):>10,} minutes   " +
           "  ".join(f"lag{lv:+d} {cors[lv]:+.4f}" for lv in (-2, -1, 0, 1, 2)) +
           f"   argmax lag {best:+d}  {'PASS' if good else 'FAIL'}")
        XD[k] = j[k].reindex(nq.index).to_numpy()
    if not ok:
        P_("\n    THE JOIN IS LAGGED. No cross-market number is issued.")
        out.close(); return
    P_("    (a one-bar ES lead would show argmax at lag -1 or +1; all three peak at 0)")

    # ------------------------------------------------------------------ session-level frames
    def px_at(mv):
        """close of the bar stamped mv within each session; NaN if the session lacks it"""
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = c[m_]
        return r

    def open_at(mv):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = o[m_]
        return r
    p0930 = open_at(570)
    p1545 = px_at(EXIT_MOD)
    sess_open = o[st_]
    prev_close = np.r_[np.nan, c[en_ - 1][:-1]]
    prev_0930 = np.r_[np.nan, open_at(570)[:-1]]
    prev_dirn = np.sign(prev_close - prev_0930)
    # session VWAP at each decision minute, RTH-anchored
    rthm = (mod >= 570)
    pv = np.where(rthm, c * v, 0.0); vv = np.where(rthm, v, 0.0)
    cpv = pd.Series(pv).groupby(sid).cumsum().to_numpy()
    cvv = pd.Series(vv).groupby(sid).cumsum().to_numpy()
    vwap = np.where(cvv > 0, cpv / np.maximum(cvv, 1e-9), c)

    def vwap_at(mv):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = vwap[m_]
        return r
    # RTH volume 09:30 -> T and its causal trailing median
    valid = np.array([np.isfinite(px_at(mv)).astype(float) for _, mv in TS])
    sess_ok = np.isfinite(p0930) & np.isfinite(p1545)
    for _, mv in TS:
        sess_ok &= np.isfinite(px_at(mv))
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    use = sess_ok & win & np.isfinite(prev_dirn)
    P_(f"\n    sessions usable: {int(use.sum()):,} of {int(win.sum()):,} in window "
       f"(dropped: no 09:30 / no decision bar / no 15:45 / no prior day)")

    # cross-market normalised drive 09:30 -> T
    def xm_drive(mv):
        acc = np.zeros(NSESS)
        cnt = np.zeros(NSESS)
        for k in XM:
            x = XD[k]
            a_ = np.full(NSESS, np.nan); b_ = np.full(NSESS, np.nan)
            m0 = mod == 570; mT = mod == mv
            a_[sid[m0]] = x[m0]; b_[sid[mT]] = x[mT]
            r_ = np.log(b_ / a_)
            s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
            z = r_ / np.maximum(s_, 1e-12)
            g = np.isfinite(z)
            acc[g] += z[g]; cnt[g] += 1
        return np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)

    # ------------------------------------------------------------------ the battery
    P_("")
    P_("=" * 118)
    P_("=== THE BATTERY. One entry at the decision bar's next open, one exit at 15:45, size 1.")
    P_("=" * 118)
    sdate = sdate_all.to_numpy()
    rng = np.random.default_rng(SEED)
    rows = []
    cellstat = {}
    for tname, mv in TS:
        pT = px_at(mv)
        entry = np.full(NSESS, np.nan)
        m_ = mod == mv + 1
        entry[sid[m_]] = o[m_]
        vw = vwap_at(mv)
        rvolT = np.full(NSESS, np.nan)
        mm = rthm & (mod <= mv)
        sv = pd.Series(np.where(mm, v, 0.0)).groupby(sid).sum().to_numpy()
        rvolT[:len(sv)] = sv
        med = pd.Series(rvolT).rolling(250, min_periods=60).median().shift(1).to_numpy()
        xd = xm_drive(mv)
        drive = np.sign(pT - p0930)
        PRED = {
            "DRIVE": drive,
            "ON_RET": np.sign(p0930 - sess_open),
            "GAP": np.sign(p0930 - prev_close),
            "VWAP_SIDE": np.sign(pT - vw),
            "PREV_DAY": prev_dirn,
            "XM_AGREE": np.sign(xd),
            "XM_CONFIRM": np.where(np.sign(xd) == drive, drive, 0.0),
            "XM_CONFLICT": np.where((np.sign(xd) != drive) & (np.sign(xd) != 0), drive, 0.0),
            "VOL_CONFIRM": np.where(rvolT >= med, drive, 0.0),
        }
        cst = COMM_RT + TICKV * (float(prof.loc[mv + 1]) + float(prof.loc[EXIT_MOD])) / 2.0
        u_ = use & np.isfinite(entry)
        move = (p1545 - entry) * PV
        emove = float(np.abs(move[u_]).mean())
        pstar = 0.5 * (1 + cst / emove)
        P_("")
        P_(f"  --- decision {tname}  |  E|move to 15:45| = ${emove:,.0f}  cost ${cst:.2f}  "
           f"p* = {pstar:.4f}  N = {int(u_.sum()):,} " + "-" * 20)
        P_(f"{'predictor':<13}{'N':>7}{'hit %':>8}{'95% CI':>16}{'vs p*':>9}{'$/trade':>10}"
           f"{'net $':>11}{'2024+':>9}{'2025':>9}{'2026YTD':>10}")
        for pn, sg in PRED.items():
            g = u_ & np.isfinite(sg) & (sg != 0)
            N = int(g.sum())
            if N < 30:
                P_(f"{pn:<13}{N:>7}   too few sessions"); continue
            pnl = sg[g] * move[g] - cst
            wins = int((sg[g] * move[g] > 0).sum())
            hit = wins / N
            se = np.sqrt(hit * (1 - hit) / N)
            lo_, hi_ = hit - 1.96 * se, hit + 1.96 * se
            sub = {}
            for wn, xa, xb in (("2024+", "2024-01-01", "2026-08-01"),
                               ("2025", "2025-01-01", "2026-01-01"),
                               ("2026YTD", "2026-01-01", "2026-08-01")):
                mw = g & (sdate >= np.datetime64(xa)) & (sdate < np.datetime64(xb))
                sub[wn] = float((sg[mw] * move[mw] - cst).mean()) if mw.sum() else np.nan
            P_(f"{pn:<13}{N:>7,}{100*hit:>7.2f}%  [{100*lo_:>5.2f},{100*hi_:>6.2f}]"
               f"{100*(hit-pstar):>8.2f}{pnl.mean():>10,.0f}{pnl.sum():>11,.0f}"
               f"{sub['2024+']:>9,.0f}{sub['2025']:>9,.0f}{sub['2026YTD']:>10,.0f}")
            rows.append(dict(T=tname, pred=pn, N=N, hit=hit, ci_lo=lo_, ci_hi=hi_,
                             pstar=pstar, per_trade=float(pnl.mean()), net=float(pnl.sum()),
                             **{f"pt_{k}": v_ for k, v_ in sub.items()}))
            cellstat[(tname, pn)] = (g.copy(), move.copy(), cst, N, sg.copy())
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "battery.csv"), index=False)

    # ------------------------------------------------------------------ best-of-27 null
    P_("")
    P_("=" * 118)
    P_("=== BEST-OF-27 NULL. Replace every predictor's sign with a fair coin on the same")
    P_("===   sessions, recompute, take the MAXIMUM over all cells. 27 cells produce a 55 %")
    P_("===   hit rate somewhere by construction; this is the bar that accounts for it.")
    P_("=" * 118)
    mx_hit = np.empty(NPERM); mx_pt = np.empty(NPERM)
    keys = list(cellstat)
    for b_ in range(NPERM):
        bh, bp = -9.0, -1e18
        for kk in keys:
            g, move, cst, N, _sg = cellstat[kk]
            s_ = rng.choice([-1.0, 1.0], size=N)
            pnl = s_ * move[g] - cst
            bh = max(bh, float((s_ * move[g] > 0).mean()))
            bp = max(bp, float(pnl.mean()))
        mx_hit[b_] = bh; mx_pt[b_] = bp
    h95, p95 = float(np.percentile(mx_hit, 95)), float(np.percentile(mx_pt, 95))
    P_(f"    best-of-27 hit rate under the coin:  mean {100*mx_hit.mean():.2f} %  "
       f"p95 {100*h95:.2f} %")
    P_(f"    best-of-27 $/trade under the coin:   mean ${mx_pt.mean():,.0f}  p95 ${p95:,.0f}")
    P_("")
    best = DF.sort_values("per_trade", ascending=False).head(6)
    P_(f"{'T':<8}{'predictor':<13}{'N':>7}{'hit %':>8}{'$/trade':>10}{'beats hit p95':>15}"
       f"{'beats $ p95':>13}")
    for _, r_ in best.iterrows():
        P_(f"{r_['T']:<8}{r_['pred']:<13}{int(r_['N']):>7,}{100*r_['hit']:>7.2f}%"
           f"{r_['per_trade']:>10,.0f}{'YES' if r_['hit']>h95 else 'no':>15}"
           f"{'YES' if r_['per_trade']>p95 else 'no':>13}")
    prim = DF[(DF["T"] == "09:45") & (DF["pred"] == "DRIVE")]
    if len(prim):
        r_ = prim.iloc[0]
        P_("")
        P_(f"    PRIMARY (DRIVE at 09:45, one test, no selection): hit {100*r_['hit']:.2f} % "
           f"vs p* {100*r_['pstar']:.2f} %  ->  "
           f"{'CLEARS' if r_['hit'] > r_['pstar'] else 'FAILS'} the cost bar; "
           f"${r_['per_trade']:,.0f}/trade")
    pd.DataFrame(dict(perm=np.arange(NPERM), max_hit=mx_hit, max_pt=mx_pt)).to_csv(
        os.path.join(OUT, "bestofk_null.csv"), index=False)

    # ------------------------------------------------------------------ by session class
    P_("")
    P_("=" * 118)
    P_("=== The same cells split by SESSION CLASS (diagnostic: the class is known only ex post)")
    P_("=" * 118)
    P_(f"{'predictor':<13}" + "".join(f"{k:>17}" for k in
                                      ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
    P_(f"{'':13}" + "".join(f"{'n / $ per trade':>17}" for _ in range(5)))
    for pn in ("DRIVE", "XM_CONFIRM", "XM_CONFLICT", "VOL_CONFIRM"):
        kk = ("09:45", pn)
        if kk not in cellstat:
            continue
        g, move, cst, N, sg = cellstat[kk]
        line = f"{pn:<13}"
        for kcl in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
            m2 = g & (klass == kcl)
            if not m2.sum():
                line += f"{'-':>17}"
            else:
                line += f"{int(m2.sum()):>6,} {float((sg[m2]*move[m2]-cst).mean()):>9,.0f}"
        P_(line)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
