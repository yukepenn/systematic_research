"""WE_W109 - FADE_HOSTILE_STATE, the TRANSFER experiment.

Spec: runs/WE_W109_FADESTATE/spec.yaml, committed BEFORE this ran (f01b5fe).

W108 measured that five fade mechanisms are POSITIVE on RANGE and MIXED and heavily NEGATIVE on
both TREND classes. So the missing object is not a better fade - it is a CAUSAL statement, at the
moment the fade would enter, about whether fading has negative action value today.

The whole design is the holdout. Three fades develop the detector, TWO ARE HELD OUT, and the split
is alphabetical and was fixed in the spec before any detector existed. The null is a RATE-MATCHED
RANDOM VETO, because a losing strategy that trades less looks better for free.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_lanes import LaneBench, RATES                                    # noqa: E402
from we_fades import (MORN_A, MORN_B, DEC, EXIT, FADES, DEV, HOLDOUT,    # noqa: E402
                      W108_5050, build_fades, session_vwap)

OUT = os.path.join(ROOT, "runs", "WE_W109_FADESTATE", "out")
os.makedirs(OUT, exist_ok=True)
SEED = 109
NPERM = 200
MRWIN = 60                      # D5 looks at the 60 bars ending at the decision bar
XMP = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
       "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
       "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
CLASSES = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


def trail(x, fn, look=250, minp=60):
    return getattr(pd.Series(x).rolling(look, min_periods=minp), fn)().shift(1).to_numpy()


def build_detectors(L, ctx, P_):
    """Six causal states, every one of them computed from bars stamped at or before 11:48."""
    NS = L.NS
    # ---- D1 directional efficiency over the whole decided window
    net = L.at(DEC) - L.at(MORN_A, use_open=True)
    path = L.agg(MORN_A, DEC, "absmove")
    d1 = np.abs(net) / np.maximum(path, 1e-9)

    # ---- D2 closes pinned at bar extremes
    m = (L.mod >= MORN_A) & (L.mod <= DEC)
    ii = np.flatnonzero(m)
    rng = L.h[ii] - L.l[ii]
    good = rng > 0
    loc = np.abs(2.0 * (L.c[ii][good] - L.l[ii][good]) / rng[good] - 1.0)
    s_ = L.sid[ii][good]
    acc = np.zeros(NS); cnt = np.zeros(NS)
    np.add.at(acc, s_, loc); np.add.at(cnt, s_, 1.0)
    d2 = np.where(cnt >= 20, acc / np.maximum(cnt, 1), np.nan)

    # ---- D3 expanding realized range
    rr = L.agg(MORN_A, DEC, "high") - L.agg(MORN_A, DEC, "low")
    d3 = rr / np.maximum(trail(rr, "mean"), 1e-9)

    # ---- D4 displacement from value
    vw = L.at(DEC, arr=session_vwap(L))
    raw = np.abs(L.at(DEC) - vw)
    d4 = raw / np.maximum(trail(raw, "mean", look=60, minp=20), 1e-9)

    # ---- D5 mean reversion keeps failing: new session extremes in the last 60 bars
    rmask = L.mod >= MORN_A
    dfr = pd.DataFrame(dict(s=L.sid[rmask], h=L.h[rmask], l=L.l[rmask]))
    rmax = dfr.groupby("s")["h"].cummax().to_numpy()
    rmin = dfr.groupby("s")["l"].cummin().to_numpy()
    newext = (dfr["h"].to_numpy() >= rmax - 1e-12) | (dfr["l"].to_numpy() <= rmin + 1e-12)
    modr = L.mod[rmask]
    sel = (modr > DEC - MRWIN) & (modr <= DEC)
    a2 = np.zeros(NS); c2 = np.zeros(NS)
    np.add.at(a2, dfr["s"].to_numpy()[sel], newext[sel].astype(float))
    np.add.at(c2, dfr["s"].to_numpy()[sel], 1.0)
    d5 = np.where(c2 >= 30, a2 / np.maximum(c2, 1), np.nan)

    # ---- D6 cross-market breadth: is the whole complex moving together?
    nq = pd.DataFrame({"time": pd.to_datetime(L.t)}).set_index("time")
    accz = np.zeros(NS); cz = np.zeros(NS)
    for k, path_ in XMP.items():
        f = os.path.join(ROOT, path_)
        if not os.path.exists(f):
            P_(f"    ! {k} substrate missing - D6 will be built from fewer markets")
            continue
        d_ = pd.read_parquet(f, columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        arr = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()
        aa, bb = L.at(MORN_A, arr=arr), L.at(DEC, arr=arr)
        with np.errstate(divide="ignore", invalid="ignore"):
            r_ = np.log(bb / aa)
        sg = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        zz = r_ / np.maximum(sg, 1e-12)
        g = np.isfinite(zz)
        accz[g] += zz[g]; cz[g] += 1
    d6 = np.where(cz > 0, np.abs(accz / np.maximum(cz, 1)), np.nan)

    return {"D1_DIR_EFF": d1, "D2_CLOSE_EXT": d2, "D3_RANGE_EXP": d3,
            "D4_VWAP_DISP": d4, "D5_MR_FAIL": d5, "D6_XBREADTH": d6}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fadestate.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    rng = np.random.default_rng(SEED)
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions [{_time.time()-t0:.0f}s]")

    MECH, ctx = build_fades(L)

    # ------------------------------------------------------------------ reproduction gate
    P_("")
    P_("=" * 124)
    P_("=== 0. REPRODUCTION GATE - are these the SAME five engines W108 measured?")
    P_("=" * 124)
    P_(f"{'fade':<17}{'N here':>9}{'N W108':>9}{'$/tr here':>12}{'$/tr W108':>12}{'':>4}")
    base = {}
    allok = True
    for k in FADES:
        sc, di = MECH[k]
        des = np.nan_to_num(np.where(LaneBench.accept(sc, 0.50), di, 0)).astype(np.int8)
        pnl, take, cost, em = L.trade(des, DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        n0, p0 = W108_5050[k]
        ok = (st["n"] == n0) and (abs(st["per_trade"] - p0) < 0.01)
        allok &= ok
        P_(f"{k:<17}{st['n']:>9}{n0:>9}{st['per_trade']:>12,.2f}{p0:>12,.2f}"
           f"{('  OK' if ok else '  MISMATCH'):>4}")
        base[k] = dict(des=des, pnl=pnl, take=take, cost=cost, em=em, st=st)
    if not allok:
        P_("")
        P_("    GATE FAILED. These are not the engines W108 measured, so a veto measured on them")
        P_("    would not be a statement about W108's result. No table is issued.")
        out.close(); return
    P_("")
    P_("    PASS - all five reproduce exactly. The veto below acts on W108's own engines.")
    P_("    DISCLOSED: VALUE_REACCEPT's score is 0 on most sessions, so its causal quantile is 0")
    P_("    at every rate and it accepts all 1,011 eligible sessions. It is effectively an")
    P_("    ALWAYS-ON fade toward the morning midpoint. That makes it the cleanest veto subject in")
    P_("    the set, and it is one of the two HELD-OUT engines.")

    # ------------------------------------------------------------------ detectors, outcome-blind
    DET = build_detectors(L, ctx, P_)
    P_("")
    P_("=" * 124)
    P_("=== 1. DETECTOR DISTRIBUTIONS ONLY. No P&L has been computed at this point.")
    P_("===    Sign convention fixed in the spec: HIGH = HOSTILE TO FADING, for all six.")
    P_("=" * 124)
    P_(f"{'detector':<15}{'defined':>9}{'p25':>10}{'p50':>10}{'p75':>10}{'p90':>10}"
       f"{'  realised veto rate @ 0.25/0.50/0.75':>40}")
    calib = {}
    for k, x in DET.items():
        d = L.win & np.isfinite(x)
        rr = []
        for r in RATES:
            h = LaneBench.accept(x, r) & L.win
            rr.append(float(h.sum()) / max(int(L.win.sum()), 1))
        calib[k] = rr
        bad = any(abs(a - b) > 0.10 for a, b in zip(rr, RATES))
        P_(f"{k:<15}{int(d.sum()):>9}"
           + "".join(f"{np.nanpercentile(x[d], q):>10.3f}" for q in (25, 50, 75, 90))
           + f"{'   ' + ' / '.join(f'{v:.2f}' for v in rr):>28}"
           + ("   UNCALIBRATED" if bad else ""))
    P_("")
    P_("    Thresholds now FROZEN as trailing causal quantiles. Economics follows.")

    # ------------------------------------------------------------------ the veto machinery
    def veto_eval(fade, hostile):
        b = base[fade]
        des = (b["des"] * (~hostile)).astype(np.int8)
        pnl, take, cost, em = L.trade(des, DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        if st is None:                       # fewer than 10 survivors: report, never silently skip
            st = dict(n=int(take.sum()), hit=np.nan, per_trade=np.nan, net=float(pnl[take].sum()),
                      p_star=np.nan, weekly=np.nan, fixdd=np.nan, poswk=np.nan, t=np.nan)
        return st, pnl, take

    def rand_null(fade, k_removed, nperm=NPERM):
        """rate-matched random veto: remove the SAME NUMBER of this fade's own trades, uniformly."""
        b = base[fade]
        idx = np.flatnonzero(b["take"])
        pn = b["pnl"][idx]
        if k_removed <= 0 or k_removed >= len(idx) - 10:
            return np.full(nperm, np.nan)
        outv = np.empty(nperm)
        for j in range(nperm):
            keep = rng.permutation(len(idx))[k_removed:]
            outv[j] = float(pn[keep].mean()) - float(pn.mean())
        return outv

    # ------------------------------------------------------------------ the full 6 x 3 table
    P_("")
    P_("=" * 124)
    P_("=== 2. THE FULL 6 x 3 TABLE. Development mean is what SELECTS; holdout mean is the ANSWER.")
    P_("===    delta = dollars per trade WITH the veto minus WITHOUT it, per engine, then averaged.")
    P_("=" * 124)
    P_(f"{'detector':<15}{'rate':>6}{'veto%':>7}"
       + "".join(f"{k[:11]:>13}" for k in FADES)
       + f"{'DEV mean':>11}{'HOLD mean':>11}")
    grid = {}
    for k, x in DET.items():
        for r in RATES:
            hostile = np.nan_to_num(LaneBench.accept(x, r)).astype(bool)
            dl = {}
            for f in FADES:
                st, _, _ = veto_eval(f, hostile)
                dl[f] = (st["per_trade"] - base[f]["st"]["per_trade"]) if st else np.nan
            dv = float(np.mean([dl[f] for f in DEV]))
            ho = float(np.mean([dl[f] for f in HOLDOUT]))
            grid[(k, r)] = dict(delta=dl, dev=dv, hold=ho, hostile=hostile)
            vr = float((hostile & L.win).sum()) / max(int(L.win.sum()), 1)
            P_(f"{k:<15}{r:>6.2f}{100*vr:>6.1f}%"
               + "".join(f"{dl[f]:>13,.0f}" for f in FADES)
               + f"{dv:>11,.0f}{ho:>11,.0f}")
        P_("")
    pd.DataFrame([dict(det=k, rate=r, dev=v["dev"], hold=v["hold"],
                       **{f"d_{f}": v["delta"][f] for f in FADES})
                  for (k, r), v in grid.items()]).to_csv(
        os.path.join(OUT, "transfer_grid.csv"), index=False)

    # ------------------------------------------------------------------ selection + the primary
    uncal = {k for k, rr in calib.items() if any(abs(a - b) > 0.10 for a, b in zip(rr, RATES))}
    cand = {kr: v for kr, v in grid.items() if kr[0] not in uncal}
    if uncal:
        P_(f"    EXCLUDED as UNCALIBRATED (W107b rule): {', '.join(sorted(uncal))}")
    best = max(cand, key=lambda kr: cand[kr]["dev"])
    bd, br = best
    P_("=" * 124)
    P_(f"=== 3. SELECTED ON THE DEVELOPMENT SET ONLY: {bd} at veto rate {br:.2f}")
    P_(f"===    development mean delta ${cand[best]['dev']:,.0f}/trade. This is a best-of-"
       f"{len(cand)} selection and is charged as one.")
    P_("=" * 124)
    hostile = cand[best]["hostile"]
    P_(f"{'engine':<17}{'role':>10}{'N base':>8}{'N veto':>8}{'$/tr base':>11}{'$/tr veto':>11}"
       f"{'delta':>9}{'net base':>12}{'net veto':>12}")
    for f in FADES:
        st, _, _ = veto_eval(f, hostile)
        b = base[f]["st"]
        role = "DEV" if f in DEV else "HELD OUT"
        P_(f"{f:<17}{role:>10}{b['n']:>8}{st['n']:>8}{b['per_trade']:>11,.0f}"
           f"{st['per_trade']:>11,.0f}{st['per_trade']-b['per_trade']:>9,.0f}"
           f"{b['net']:>12,.0f}{st['net']:>12,.0f}")

    P_("")
    P_("=" * 124)
    P_("=== 4. THE PRIMARY - the two HELD-OUT engines, nothing re-tuned")
    P_("=" * 124)
    real = cand[best]["hold"]
    nulls = []
    for f in HOLDOUT:
        st, _, _ = veto_eval(f, hostile)
        k_rm = base[f]["st"]["n"] - st["n"]
        nulls.append(rand_null(f, k_rm))
        P_(f"    {f:<17} vetoed {k_rm:>4} of {base[f]['st']['n']:>4} trades   "
           f"delta ${cand[best]['delta'][f]:>8,.0f}/trade")
    nd = np.nanmean(np.vstack(nulls), axis=0)
    p95 = float(np.nanpercentile(nd, 95))
    pct = 100 * float(np.nanmean(nd < real))
    P_("")
    P_(f"    REAL held-out mean delta        ${real:,.0f}/trade")
    P_(f"    RATE-MATCHED RANDOM VETO null   mean ${np.nanmean(nd):,.0f}  sd ${np.nanstd(nd):,.0f}"
       f"  p95 ${p95:,.0f}")
    P_(f"    percentile of the null          {pct:.1f}th")
    verdict = "PASSES" if (real > 0 and real > p95) else "FAILS"
    P_(f"    VERDICT                         {verdict}")
    if bd == "D1_DIR_EFF":
        P_("")
        P_("    ! The spec's DISCLOSED OVERLAP fires: D1 is a directional-efficiency statistic and")
        P_("    ! PATH_EFF_TRANS is built from path efficiency over an overlapping window. Its")
        P_("    ! improvement is CONFOUNDED and discounted in advance; the transfer claim must")
        P_("    ! stand or fall on VALUE_REACCEPT alone.")
        f = "VALUE_REACCEPT"
        st, _, _ = veto_eval(f, hostile)
        k_rm = base[f]["st"]["n"] - st["n"]
        nn = rand_null(f, k_rm)
        rr = cand[best]["delta"][f]
        p95c = float(np.nanpercentile(nn, 95))
        P_(f"    ! CLEAN HOLDOUT {f}: delta ${rr:,.0f}/trade vs null p95 ${p95c:,.0f} -> "
           f"{100*float(np.nanmean(nn < rr)):.1f}th percentile   "
           f"{'PASSES' if (rr > 0 and rr > p95c) else 'FAILS'}")

    # ------------------------------------------------------------------ what did it learn?
    P_("")
    P_("=" * 124)
    P_("=== 5. DIAGNOSTIC ONLY - what the detector learned, against the EX-POST class labels.")
    P_("===    These labels are NEVER an input. This measures the detector, it does not build it.")
    P_("=" * 124)
    P_(f"{'detector':<15}{'rate':>6}" + "".join(f"{'P(hostile|'+c+')':>20}" for c in CLASSES))
    for k, x in DET.items():
        for r in (br,):
            h = np.nan_to_num(LaneBench.accept(x, r)).astype(bool)
            row = []
            for c in CLASSES:
                m = L.win & (L.klass == c)
                row.append(100 * float(h[m].mean()) if m.sum() else np.nan)
            P_(f"{k:<15}{r:>6.2f}" + "".join(f"{v:>19.1f}%" for v in row))

    P_("")
    P_("=" * 124)
    P_("=== 6. SECTION 12 STEP 6 - range profit RETAINED and trend loss REMOVED, separately")
    P_("=" * 124)
    P_(f"{'engine':<17}{'RANGE+MIXED base':>18}{'RANGE+MIXED veto':>18}{'retained':>10}"
       f"{'TREND base':>13}{'TREND veto':>13}{'removed':>10}")
    for f in FADES:
        b = base[f]
        st, pnl, take = veto_eval(f, hostile)
        rm = np.isin(L.klass, ["RANGE", "MIXED"])
        tm = np.isin(L.klass, ["TREND-UP", "TREND-DOWN"])
        rb = float(b["pnl"][b["take"] & rm].sum()); rv = float(pnl[take & rm].sum())
        tb = float(b["pnl"][b["take"] & tm].sum()); tv = float(pnl[take & tm].sum())
        P_(f"{f:<17}{rb:>18,.0f}{rv:>18,.0f}{100*rv/max(abs(rb),1e-9):>9.0f}%"
           f"{tb:>13,.0f}{tv:>13,.0f}{100*(1-tv/min(tb,-1e-9)):>9.0f}%")

    # ------------------------------------------------------------------ the book
    P_("")
    P_("=" * 124)
    P_("=== 7. THE FIVE-ENGINE FADE BOOK, size 1 each, with and without the selected veto")
    P_("=" * 124)
    P_(f"{'book':<17}{'trades':>9}{'net $':>13}{'$/trade':>10}{'wk $':>10}{'wk$@fixDD':>11}"
       f"{'pos wk%':>9}{'maxDD':>11}{'CVaR5':>10}{'t':>7}")
    books = {}
    for lab, hv in (("ALWAYS ON", np.zeros(L.NS, bool)), (f"VETO {bd}@{br:.2f}", hostile)):
        tot = np.zeros(L.NS); ntr = 0
        for f in FADES:
            b = base[f]
            des = (b["des"] * (~hv)).astype(np.int8)
            pnl, take, _, _ = L.trade(des, DEC, EXIT)
            tot += pnl; ntr += int(take.sum())
        ser = tot[L.sess_in]
        wv = pd.Series(ser).groupby(L.wk).sum().to_numpy()
        dp = dd_profile(wv)
        nz = ser[ser != 0]
        cv = float(np.mean(np.sort(nz)[:max(1, int(0.05 * len(nz)))])) if len(nz) else np.nan
        books[lab] = wv
        P_(f"{lab:<17}{ntr:>9}{ser.sum():>13,.0f}{ser.sum()/max(ntr,1):>10,.0f}"
           f"{wv.mean():>10,.0f}{wv.mean()*20245.0/max(dp['maxdd'],1e-9):>11,.0f}"
           f"{100*float((wv>0).mean()):>8.1f}%{dp['maxdd']:>11,.0f}{cv:>10,.0f}"
           f"{wv.mean()/max(wv.std(ddof=1)/np.sqrt(len(wv)),1e-9):>7.2f}")
    pd.DataFrame(books).to_csv(os.path.join(OUT, "book_weekly.csv"), index=False)

    P_("")
    P_(f"[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
