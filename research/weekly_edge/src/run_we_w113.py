"""WE_W113 - ROUTE THE ACTUAL BASELINE.

Spec: runs/WE_W113_ROUTEBASE/spec.yaml, committed BEFORE this ran (f678744).

Section 37 asks whether ONE state layer can route MORE THAN ONE engine. W109 answered "not these
fades" - and those fades lose money. This asks the same question of P1/PCT, where the answer is
worth real dollars either way.

Polarity is INVERTED from W109 and that is fixed by mechanism before any P&L is read: P1 is a
long-only TREND-FOLLOWING engine whose breakouts fail on range days, so it is vetoed when the
detector is LOW, not high.
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
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw, same                              # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402
from we_lanes import LaneBench, RATES, DDT                               # noqa: E402
from run_we_w109 import build_detectors                                  # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W113_ROUTEBASE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
CUT = 709                       # 11:49 - the first bar a blocked session may not OPEN a position in
SEED = 113
NPERM = 200
USE = ("D1_DIR_EFF", "D4_VWAP_DISP", "D5_MR_FAIL")


def gfills_blocked(D, dir_arr, size_at_entry, block_bar, halt, target, per_ctr):
    """gfills with ONE addition: `block_bar[i]` forbids OPENING a position at bar i.

    An already-open position is NOT touched - the session box, the target and the session-close
    flatten all still apply to it, exactly as the spec requires. A reversal signal therefore
    still CLOSES the old position and then declines to open the new one, which is what "no new
    entries" means. With block_bar all-False this must be byte-identical to gfills, and the B1
    check below asserts it rather than assuming it.
    """
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0 and block_bar[i]:
                p = 0
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
    return trades


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "routebase.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    st_, en_, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NS)])
    sess_in = np.flatnonzero(win)
    wk = wkall[sess_in]
    rng = np.random.default_rng(SEED)
    P_(f"    substrate {n:,} bars / {len(sess_in):,} in-window sessions [{_time.time()-t0:.0f}s]")

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
    SZ = np.where(sc >= 3, 2, 1).astype(np.int8)
    KW = arm_kw("PCT", 1.183)

    # ------------------------------------------------------------------ B1 harness check
    P_("")
    P_("=" * 124)
    P_("=== 0. B1 HARNESS CHECK - the blocked engine with NOTHING blocked must be gfills verbatim")
    P_("=" * 124)
    base_tr = gfills(D, p1, SZ, **KW)
    ident = gfills_blocked(D, p1, SZ, np.zeros(n, bool), **KW)
    okb = same(base_tr, ident)
    P_(f"    gfills {len(base_tr):,} trades   gfills_blocked(empty) {len(ident):,} trades   "
       f"byte-identical: {okb}")
    if not okb:
        P_("    CHECK FAILED - every number below would be measuring my new loop, not the engine.")
        out.close(); return

    def econ(trades):
        w_ = {}
        for x in trades:
            for ts in (x["et"], x["xt"]):
                pp = pd.Timestamp(ts); m2 = pp.hour * 60 + pp.minute
                w_[m2] = w_.get(m2, 0.0) + x["u"]
        r_ = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) \
            / max(sum(w_.values()), 1)
        ser = np.zeros(NS); ntr = 0; ctr = 0.0
        for x in trades:
            si = int(sid[i_of(x["et"])])
            if win[si]:
                ser[si] += x["pnl"] - r_ * x["u"]; ntr += 1; ctr += x["u"]
        wv = pd.Series(ser[sess_in]).groupby(wk).sum().to_numpy()
        dp = dd_profile(wv)
        s5 = np.sort(ser[sess_in])
        return dict(n=ntr, ctr=ctr, spread=r_, net=float(ser[sess_in].sum()),
                    wk=float(wv.mean()), fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((wv > 0).mean()), maxdd=dp["maxdd"],
                    top5=float(dp.get("top5", np.nan)),
                    cvar=float(s5[:max(1, int(0.05 * len(s5)))].mean()),
                    t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9), ser=ser)
    BASE = econ(base_tr)

    # ------------------------------------------------------------------ money at risk
    P_("")
    P_("=" * 124)
    P_("=== 1. HOW MUCH OF P1/PCT's MONEY IS EVEN AT RISK HERE? Reported FIRST, per the spec.")
    P_("=" * 124)
    pre = post = 0.0; npre = npost = 0
    for x in base_tr:
        si = int(sid[i_of(x["et"])])
        if not win[si]:
            continue
        m2 = pd.Timestamp(x["et"]).hour * 60 + pd.Timestamp(x["et"]).minute
        if m2 >= CUT:
            post += x["pnl"] - BASE["spread"] * x["u"]; npost += 1
        else:
            pre += x["pnl"] - BASE["spread"] * x["u"]; npre += 1
    P_(f"    entries BEFORE 11:49 : {npre:>5} trades   net ${pre:>12,.0f}")
    P_(f"    entries AT/AFTER 11:49: {npost:>5} trades   net ${post:>12,.0f}"
       f"   = {100*post/max(BASE['net'],1e-9):.1f} % of P1/PCT's net")
    P_("")
    P_("    Only the second row can be changed by this wave, in either direction.")

    # ------------------------------------------------------------------ detectors
    L = LaneBench()
    DET = build_detectors(L, None, P_)
    assert L.NS == NS, "session frame mismatch between LaneBench and this substrate"
    P_("")
    P_("=" * 124)
    P_("=== 2. THE 3 x 3 GRID. Veto polarity is LOW = range-like = block P1's new afternoon")
    P_("===    entries. Fixed by mechanism in the spec BEFORE any P&L.")
    P_("=" * 124)
    P_(f"{'cell':<24}{'veto%':>7}{'trades':>8}{'net $':>12}{'wk $':>9}{'wk$@fixDD':>11}"
       f"{'pos wk%':>9}{'maxDD':>10}{'CVaR5':>9}{'t':>7}")
    P_(f"{'BASELINE (no veto)':<24}{0.0:>6.1f}%{BASE['n']:>8}{BASE['net']:>12,.0f}"
       f"{BASE['wk']:>9,.0f}{BASE['fixdd']:>11,.0f}{BASE['poswk']:>8.1f}%"
       f"{BASE['maxdd']:>10,.0f}{BASE['cvar']:>9,.0f}{BASE['t']:>7.2f}")
    rows, vetosets = [], {}
    for k in USE:
        for r in RATES:
            veto = np.nan_to_num(LaneBench.accept(-DET[k], r)).astype(bool)
            vr = float((veto & win).sum()) / max(int(win.sum()), 1)
            if abs(vr - r) > 0.10:
                P_(f"{k + ' @ ' + f'{r:.2f}':<24}{100*vr:>6.1f}%   UNCALIBRATED - excluded "
                   f"(W107b rule)")
                continue
            blk = veto[sid] & (mod >= CUT)
            e = econ(gfills_blocked(D, p1, SZ, blk, **KW))
            vetosets[(k, r)] = veto
            rows.append(dict(det=k, rate=r, vetorate=vr, **{q: e[q] for q in
                                                            ("n", "net", "wk", "fixdd", "poswk",
                                                             "maxdd", "cvar", "t")}))
            P_(f"{k + ' @ ' + f'{r:.2f}':<24}{100*vr:>6.1f}%{e['n']:>8}{e['net']:>12,.0f}"
               f"{e['wk']:>9,.0f}{e['fixdd']:>11,.0f}{e['poswk']:>8.1f}%"
               f"{e['maxdd']:>10,.0f}{e['cvar']:>9,.0f}{e['t']:>7.2f}")
        P_("")
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "grid.csv"), index=False)

    P_("    UNCONDITIONAL CONTROL (W111b's binding rule) - block on EVERY session:")
    eall = econ(gfills_blocked(D, p1, SZ, (mod >= CUT), **KW))
    P_(f"{'BLOCK ALL sessions':<24}{100.0:>6.1f}%{eall['n']:>8}{eall['net']:>12,.0f}"
       f"{eall['wk']:>9,.0f}{eall['fixdd']:>11,.0f}{eall['poswk']:>8.1f}%"
       f"{eall['maxdd']:>10,.0f}{eall['cvar']:>9,.0f}{eall['t']:>7.2f}")

    # ------------------------------------------------------------------ the null
    best = DF.loc[DF["fixdd"].idxmax()]
    bk, br = best["det"], float(best["rate"])
    nveto = int((vetosets[(bk, br)] & win).sum())
    P_("")
    P_("=" * 124)
    P_(f"=== 3. THE PRIMARY: best of {len(DF)} cells = {bk} @ {br:.2f}, "
       f"${best['fixdd']:,.0f}/wk at fixed DD vs the baseline's ${BASE['fixdd']:,.0f}")
    P_(f"===    RATE-MATCHED RANDOM VETO null: {NPERM} draws, each blocking post-11:49 entries on")
    P_(f"===    the same {nveto} sessions chosen uniformly at random. Charged as a best-of-{len(DF)}.")
    P_("=" * 124)
    pool = np.flatnonzero(win)
    nul = np.empty(NPERM)
    for b in range(NPERM):
        vv = np.zeros(NS, bool)
        vv[rng.choice(pool, size=nveto, replace=False)] = True
        nul[b] = econ(gfills_blocked(D, p1, SZ, vv[sid] & (mod >= CUT), **KW))["fixdd"]
        if (b + 1) % 50 == 0:
            P_(f"    ... {b+1}/{NPERM} draws [{_time.time()-t0:.0f}s]")
    p95 = float(np.percentile(nul, 95))
    P_("")
    P_(f"    REAL   ${best['fixdd']:,.0f}/wk at fixed DD")
    P_(f"    NULL   mean ${nul.mean():,.0f}  sd ${nul.std(ddof=1):,.0f}  p95 ${p95:,.0f}"
       f"  -> {100*float((nul < best['fixdd']).mean()):.1f}th percentile")
    P_(f"    BASELINE ${BASE['fixdd']:,.0f}    BLOCK-ALL ${eall['fixdd']:,.0f}")
    v = best["fixdd"] > p95 and best["fixdd"] > BASE["fixdd"]
    P_(f"    VERDICT: {'PASSES' if v else 'FAILS'}")
    np.save(os.path.join(OUT, "null_fixdd.npy"), nul)

    # ------------------------------------------------------------------ redundancy
    P_("")
    P_("=" * 124)
    P_("=== 4. IS THE DETECTOR REDUNDANT WITH WHAT P1 ALREADY DOES?")
    P_("=" * 124)
    hasentry = np.zeros(NS, bool)
    for x in base_tr:
        m2 = pd.Timestamp(x["et"]).hour * 60 + pd.Timestamp(x["et"]).minute
        if m2 >= CUT:
            hasentry[int(sid[i_of(x["et"])])] = True
    P_(f"    P1/PCT takes a post-11:49 entry on {int((hasentry & win).sum())} of "
       f"{int(win.sum())} in-window sessions - it is ALREADY flat after 11:49 on the rest.")
    P_("")
    P_(f"{'cell':<24}{'veto n':>8}{'of which P1 had no entry':>27}{'sessions actually changed':>27}")
    for (k, r), vv in vetosets.items():
        m = vv & win
        P_(f"{k + ' @ ' + f'{r:.2f}':<24}{int(m.sum()):>8}"
           f"{int((m & ~hasentry).sum()):>27}{int((m & hasentry).sum()):>27}")
    P_("")
    P_("    A veto that lands mostly on sessions where P1 was already flat after 11:49 cannot")
    P_("    be doing much, whatever its headline number says.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
