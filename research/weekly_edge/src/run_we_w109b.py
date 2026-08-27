"""WE_W109b - the decomposition of W109's failure, plus a defect in my own spec.

W109's primary FAILED (85.0th percentile of the rate-matched random veto null, bar 95th). This
addendum does four things, none of which can promote anything:

(a) THE SPEC'S OVERLAP RULE, APPLIED CONSISTENTLY. The spec disclosed in advance that detector D1
    overlaps the held-out PATH_EFF_TRANS and wrote the discount rule for that case. It did NOT
    anticipate that D3_RANGE_EXP - the detector actually selected - is a MULTIPLICATIVE FACTOR
    INSIDE PATH_EFF_TRANS's own score, which is a strictly worse overlap than the one disclosed.
    By the spec's own logic the discount must apply, so the clean holdout is VALUE_REACCEPT alone.

(b) THE SELECTIVITY RATIO. The statistic that says whether a veto SELECTS or merely REDUCES
    EXPOSURE: trend loss removed divided by range profit removed. A causal trend-day veto should
    have a ratio well above 1. A detector that is pure exposure reduction sits at 1.

(c) The held-out null for ALL 15 calibrated cells, so we know whether ANY cell in the family would
    have passed. Charged and reported as a best-of-15 diagnostic. The primary already failed.

(d) THE DECOMPOSITION THAT MATTERS: does a causal trend-day state EXIST at 11:48 at all? Measured
    as each detector's AUC for discriminating ex-post TREND sessions from RANGE/MIXED ones, against
    a label-permutation null. This separates "we cannot see trend days" from "seeing them does not
    help the fades", and those are very different conclusions for what to build next.
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
from we_lanes import LaneBench, RATES                                    # noqa: E402
from we_fades import DEC, EXIT, FADES, DEV, HOLDOUT, build_fades         # noqa: E402
from run_we_w109 import build_detectors                                  # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W109_FADESTATE", "out")
SEED = 1090
NPERM = 200
NAUC = 2000
TRENDC = ("TREND-UP", "TREND-DOWN")
RANGEC = ("RANGE", "MIXED")


def auc(score, lab):
    g = np.isfinite(score)
    s, y = score[g], lab[g]
    if y.sum() == 0 or (~y).sum() == 0:
        return np.nan
    r = pd.Series(s).rank().to_numpy()
    n1, n0 = int(y.sum()), int((~y).sum())
    return (r[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fadestate_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    rng = np.random.default_rng(SEED)
    MECH, ctx = build_fades(L)
    DET = build_detectors(L, ctx, P_)
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} sessions [{_time.time()-t0:.0f}s]")

    base = {}
    for k in FADES:
        sc, di = MECH[k]
        des = np.nan_to_num(np.where(LaneBench.accept(sc, 0.50), di, 0)).astype(np.int8)
        pnl, take, cost, em = L.trade(des, DEC, EXIT)
        base[k] = dict(des=des, pnl=pnl, take=take, st=L.stats(pnl, take, cost, em))

    def ev(f, hostile):
        b = base[f]
        pnl, take, cost, em = L.trade((b["des"] * (~hostile)).astype(np.int8), DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        if st is None:                       # fewer than 10 survivors: reported, never skipped
            st = dict(n=int(take.sum()), per_trade=np.nan, net=float(pnl[take].sum()))
        return st, pnl, take

    def rnull(f, k_removed, nperm=NPERM):
        idx = np.flatnonzero(base[f]["take"]); pn = base[f]["pnl"][idx]
        if k_removed <= 0 or k_removed >= len(idx) - 10:
            return np.full(nperm, np.nan)
        o = np.empty(nperm)
        for j in range(nperm):
            o[j] = float(pn[rng.permutation(len(idx))[k_removed:]].mean()) - float(pn.mean())
        return o

    # ------------------------------------------------------------------ (a) the spec defect
    P_("")
    P_("=" * 124)
    P_("=== (a) A DEFECT IN MY OWN SPEC. The overlap rule was written for the wrong detector.")
    P_("=" * 124)
    pe = MECH["PATH_EFF_TRANS"][0]
    for k in ("D1_DIR_EFF", "D3_RANGE_EXP"):
        g = L.win & np.isfinite(pe) & np.isfinite(DET[k])
        P_(f"    rank correlation( {k:<13}, PATH_EFF_TRANS score ) = "
           f"{pd.Series(DET[k][g]).corr(pd.Series(pe[g]), method='spearman'):+.3f}")
    P_("")
    P_("    PATH_EFF_TRANS = (1 - path efficiency) x (range / trailing mean range).")
    P_("    D3_RANGE_EXP   =                          range / trailing mean range.")
    P_("    D3 IS A MULTIPLICATIVE FACTOR INSIDE THE HELD-OUT ENGINE'S OWN SCORE. That is a")
    P_("    strictly worse overlap than the D1 case the spec disclosed, and by the spec's own")
    P_("    logic the same discount must apply. The clean holdout is VALUE_REACCEPT alone.")

    hostile = np.nan_to_num(LaneBench.accept(DET["D3_RANGE_EXP"], 0.50)).astype(bool)
    st, _, _ = ev("VALUE_REACCEPT", hostile)
    d = st["per_trade"] - base["VALUE_REACCEPT"]["st"]["per_trade"]
    nn = rnull("VALUE_REACCEPT", base["VALUE_REACCEPT"]["st"]["n"] - st["n"])
    p95 = float(np.nanpercentile(nn, 95))
    P_("")
    P_(f"    CLEAN HOLDOUT (VALUE_REACCEPT only), D3_RANGE_EXP @ 0.50:")
    P_(f"        real delta ${d:,.0f}/trade   random-veto null mean ${np.nanmean(nn):,.0f} "
       f"p95 ${p95:,.0f}  -> {100*float(np.nanmean(nn < d)):.1f}th percentile   "
       f"{'PASSES' if (d > 0 and d > p95) else 'FAILS'}")
    P_("    The wave's verdict does not change - the primary already failed at the 85th")
    P_("    percentile. This makes the failure cleaner, it does not rescue anything.")

    # ------------------------------------------------------------------ (b) selectivity
    P_("")
    P_("=" * 124)
    P_("=== (b) THE SELECTIVITY RATIO - does the veto SELECT, or does it only REDUCE EXPOSURE?")
    P_("===     trend loss removed (%) divided by range profit removed (%).")
    P_("===     A causal trend-day veto is well above 1. Pure exposure reduction sits at 1.")
    P_("=" * 124)
    rm = np.isin(L.klass, list(RANGEC))
    tm = np.isin(L.klass, list(TRENDC))
    P_(f"{'detector':<15}{'rate':>6}" + "".join(f"{f[:11]:>13}" for f in FADES)
       + f"{'POOLED':>10}")
    sel_rows = []
    for k, x in DET.items():
        for r in RATES:
            hv = np.nan_to_num(LaneBench.accept(x, r)).astype(bool)
            per, RB = [], [0.0, 0.0, 0.0, 0.0]
            for f in FADES:
                b = base[f]
                _, pnl, take = ev(f, hv)
                rb = float(b["pnl"][b["take"] & rm].sum()); rv = float(pnl[take & rm].sum())
                tb = float(b["pnl"][b["take"] & tm].sum()); tv = float(pnl[take & tm].sum())
                RB[0] += rb; RB[1] += rv; RB[2] += tb; RB[3] += tv
                rr = 1 - rv / rb if rb > 0 else np.nan
                tr = 1 - tv / tb if tb < 0 else np.nan
                per.append(tr / rr if (np.isfinite(rr) and rr > 1e-6) else np.nan)
            prr = 1 - RB[1] / RB[0] if RB[0] > 0 else np.nan
            ptr = 1 - RB[3] / RB[2] if RB[2] < 0 else np.nan
            pool = ptr / prr if (np.isfinite(prr) and prr > 1e-6) else np.nan
            P_(f"{k:<15}{r:>6.2f}" + "".join(f"{v:>13.2f}" for v in per) + f"{pool:>10.2f}")
            sel_rows.append(dict(det=k, rate=r, pooled=pool,
                                 range_removed=prr, trend_removed=ptr))
        P_("")
    pd.DataFrame(sel_rows).to_csv(os.path.join(OUT, "selectivity.csv"), index=False)

    # ------------------------------------------------------------------ (c) all 15 holdout nulls
    P_("=" * 124)
    P_("=== (c) THE HELD-OUT NULL FOR EVERY CALIBRATED CELL. Would ANY of them have passed?")
    P_("===     D5_MR_FAIL is excluded as UNCALIBRATED. This is a best-of-15 diagnostic and the")
    P_("===     primary has already failed; nothing here can promote anything.")
    P_("=" * 124)
    P_(f"{'detector':<15}{'rate':>6}{'DEV delta':>11}{'HOLD delta':>12}{'null p95':>11}"
       f"{'pctile':>9}{'':>8}{'CLEAN (VALUE_REACCEPT only)':>30}")
    npass = 0
    for k, x in DET.items():
        if k == "D5_MR_FAIL":
            continue
        for r in RATES:
            hv = np.nan_to_num(LaneBench.accept(x, r)).astype(bool)
            dvs = []
            for f in DEV:
                sd, _, _ = ev(f, hv)
                dvs.append(sd["per_trade"] - base[f]["st"]["per_trade"])
            dev = float(np.mean(dvs))
            ds, ns = [], []
            for f in HOLDOUT:
                s2, _, _ = ev(f, hv)
                if not np.isfinite(s2["per_trade"]):
                    ds = []; break
                ds.append(s2["per_trade"] - base[f]["st"]["per_trade"])
                ns.append(rnull(f, base[f]["st"]["n"] - s2["n"]))
            if not ds:
                P_(f"{k:<15}{r:>6.2f}{dev:>11,.0f}{'  too few survivors on a holdout':>32}")
                continue
            real = float(np.mean(ds)); nd = np.nanmean(np.vstack(ns), axis=0)
            p95 = float(np.nanpercentile(nd, 95))
            ok = real > 0 and real > p95
            npass += int(ok)
            s3, _, _ = ev("VALUE_REACCEPT", hv)
            dc = s3["per_trade"] - base["VALUE_REACCEPT"]["st"]["per_trade"]
            nc = rnull("VALUE_REACCEPT", base["VALUE_REACCEPT"]["st"]["n"] - s3["n"])
            p95c = float(np.nanpercentile(nc, 95))
            P_(f"{k:<15}{r:>6.2f}{dev:>11,.0f}{real:>12,.0f}{p95:>11,.0f}"
               f"{100*float(np.nanmean(nd < real)):>8.1f}th{('  PASS' if ok else '  fail'):>8}"
               f"{f'${dc:,.0f} vs p95 ${p95c:,.0f}':>22}"
               f"{('  PASS' if (dc > 0 and dc > p95c) else '  fail'):>8}")
    P_("")
    P_(f"    {npass} of 15 calibrated cells clear their own held-out null. At a 5 % bar, "
       f"{15*0.05:.2f} are expected by chance alone.")

    # ------------------------------------------------------------------ (d) does the state exist?
    P_("")
    P_("=" * 124)
    P_("=== (d) THE DECOMPOSITION THAT MATTERS - does a CAUSAL TREND-DAY STATE EXIST at 11:48?")
    P_("===     AUC for discriminating ex-post TREND-UP/DOWN from RANGE/MIXED, using ONLY")
    P_("===     information available at 11:48. REVERSAL sessions are excluded as neither.")
    P_("===     This is a DIAGNOSTIC of the information, not a tradeable object.")
    P_("=" * 124)
    lab = np.isin(L.klass, list(TRENDC))
    keep = L.win & (np.isin(L.klass, list(TRENDC)) | np.isin(L.klass, list(RANGEC)))
    P_(f"    {int(keep.sum())} sessions: {int((keep & lab).sum())} TREND, "
       f"{int((keep & ~lab).sum())} RANGE/MIXED")
    P_("")
    P_(f"{'detector':<15}{'AUC':>8}{'perm p95':>11}{'pctile':>9}{'verdict':>10}")
    aucs = {}
    for k, x in DET.items():
        s = np.where(keep, x, np.nan)
        a = auc(s, lab)
        aucs[k] = a
        g = np.isfinite(s)
        yy = lab[g]; ss = s[g]
        nulls = np.empty(NAUC)
        for b in range(NAUC):
            nulls[b] = auc(ss, rng.permutation(yy))
        p95 = float(np.nanpercentile(nulls, 95))
        P_(f"{k:<15}{a:>8.3f}{p95:>11.3f}{100*float(np.nanmean(nulls < a)):>8.1f}th"
           f"{('  REAL' if a > p95 else '  null'):>10}")
    P_("")
    P_("    Reading: AUC 0.50 is a coin. An AUC that clears its permutation null means the")
    P_("    information to distinguish a trend day from a range day IS present at 11:48.")
    P_("    Whether that information is worth money to a fade is a SEPARATE question, and")
    P_("    section (b) above is the one that answers it.")
    pd.DataFrame([dict(det=k, auc=v) for k, v in aucs.items()]).to_csv(
        os.path.join(OUT, "class_auc.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
