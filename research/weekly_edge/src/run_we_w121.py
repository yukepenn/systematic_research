"""WE_W121 - TURNOVER AS A CAUSAL STATE.

Spec: runs/WE_W121_TURNOVER/spec.yaml, committed BEFORE this ran (7ad4431).

W119: the book does not lose because an engine was absent (E_NO_ENGINE = 0) and does not lose
because the market fell (TREND-DOWN +0.8 pp). It loses on sessions where P1 takes 3.042 entries
against 1.377, for 18 % FEWER contract-minutes, while the market moves 31 % LESS.

THE BINDING CONTROL IS THE COUNT-MATCHED RANDOM-HALT PLACEBO. Intraday loss-reactivity is a CLOSED
family here and that placebo is the instrument that killed it three times. It must kill this too
unless something genuinely different is present.
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
from run_we_w113 import gfills_blocked                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W121_TURNOVER", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W110W = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out", "weekly.csv")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
DDT = 20245.0
CAPS = (1, 2, 3, 4)
NPERM = 200
SEED = 121


def gfills_capped(D, dir_arr, size_at_entry, cap, halt, target, per_ctr):
    """gfills with ONE addition: at most `cap` NEW entries per session.

    An already-open position is untouched - the box, the target and the session-close flatten all
    still apply. With cap = a large number this must be byte-identical to gfills, and the B1 check
    below asserts it rather than assuming it.
    """
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False; nent = 0
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False; nent = 0
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl, ei=eti))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0 and nent >= cap:
                p = 0
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i; nent += 1
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl, ei=eti))
            p = 0; u = 0
    return trades


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "turnover.txt"), "w", encoding="utf-8")

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
    P_(f"    {len(sess_in):,} in-window sessions [{_time.time()-t0:.0f}s]")

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

    # ------------------------------------------------------------------ B1
    P_("")
    P_("=" * 124)
    P_("=== 0. B1 - the capped engine with an unreachable cap must be gfills verbatim")
    P_("=" * 124)
    base_tr = gfills(D, p1, SZ, **KW)
    idt = gfills_capped(D, p1, SZ, 10 ** 9, **KW)
    okb = same(base_tr, [{k: v for k, v in x.items() if k != "ei"} for x in idt])
    P_(f"    gfills {len(base_tr):,}   gfills_capped(cap=1e9) {len(idt):,}   identical: {okb}")
    if not okb:
        P_("    CHECK FAILED. No table is issued."); out.close(); return

    rP = None

    def econ(trades):
        w_ = {}
        for x in trades:
            for ts in (x["et"], x["xt"]):
                pp = pd.Timestamp(ts); m2 = pp.hour * 60 + pp.minute
                w_[m2] = w_.get(m2, 0.0) + x["u"]
        r_ = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) \
            / max(sum(w_.values()), 1)
        ser = np.zeros(NS); ntr = 0; cm = 0.0
        for x in trades:
            s = int(sid[i_of(x["et"])])
            if win[s]:
                ser[s] += x["pnl"] - r_ * x["u"]; ntr += 1
                cm += x["u"] * max((pd.Timestamp(x["xt"]) - pd.Timestamp(x["et"])).total_seconds()
                                   / 60.0, 0.0)
        wv = pd.Series(ser[sess_in]).groupby(wk).sum().to_numpy()
        dp = dd_profile(wv)
        srt = np.sort(ser[sess_in])
        return dict(n=ntr, cm=cm, spread=r_, net=float(ser[sess_in].sum()),
                    wk=float(wv.mean()), fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((wv > 0).mean()), maxdd=dp["maxdd"],
                    cvar=float(srt[:max(1, int(0.05 * len(srt)))].mean()),
                    t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9), ser=ser)
    BASE = econ(base_tr)
    rP = BASE["spread"]
    P_(f"    baseline: {BASE['n']:,} trades, ${BASE['net']:,.0f}, "
       f"${BASE['fixdd']:,.0f}/wk at fixed DD, spread ${rP:.2f}/ctrRT")

    # ================================================================== STAGE A
    P_("")
    P_("=" * 124)
    P_("=== STAGE A - INFORMATION. Conditional on N-1 prior entries, what is the Nth worth?")
    P_("=" * 124)
    rows = []
    bys = {}
    for x in idt:
        s = int(sid[x["ei"]])
        bys.setdefault(s, []).append(x)
    for s, xs in bys.items():
        if not win[s]:
            continue
        xs = sorted(xs, key=lambda q: q["ei"])
        cum = 0.0
        for k, x in enumerate(xs, start=1):
            u = int(x["u"])
            rows.append(dict(sess=s, ordinal=k, net=x["pnl"] - rP * u, u=u,
                             emin=int(mod[x["ei"]]), cum_before=cum,
                             hold=max((pd.Timestamp(x["xt"]) - pd.Timestamp(x["et"])).total_seconds()
                                      / 60.0, 0.0)))
            cum += x["pnl"] / u
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(OUT, "entries.csv"), index=False)
    uncond = float(T["net"].mean())
    P_(f"    {len(T):,} entries. Unconditional mean ${uncond:,.0f}/entry.")
    P_("")
    P_(f"{'ordinal':<10}{'n':>7}{'% of entries':>14}{'mean net $':>13}{'vs uncond':>11}"
       f"{'hit%':>8}{'hold min':>10}{'mean size':>11}{'mean entry':>12}{'cum $ before':>14}")
    for k in (1, 2, 3, 4):
        d = T[T["ordinal"] == k]
        if len(d) < 20:
            continue
        P_(f"{k:<10}{len(d):>7}{100*len(d)/len(T):>13.1f}%{d['net'].mean():>13,.0f}"
           f"{d['net'].mean()-uncond:>+11,.0f}{100*float((d['net']>0).mean()):>7.1f}%"
           f"{d['hold'].mean():>10.0f}{d['u'].mean():>11.2f}"
           f"{f'{int(d.emin.mean())//60:02d}:{int(d.emin.mean())%60:02d}':>12}"
           f"{d['cum_before'].mean():>14,.0f}")
    d5 = T[T["ordinal"] >= 5]
    if len(d5) >= 20:
        P_(f"{'5+':<10}{len(d5):>7}{100*len(d5)/len(T):>13.1f}%{d5['net'].mean():>13,.0f}"
           f"{d5['net'].mean()-uncond:>+11,.0f}{100*float((d5['net']>0).mean()):>7.1f}%"
           f"{d5['hold'].mean():>10.0f}{d5['u'].mean():>11.2f}"
           f"{f'{int(d5.emin.mean())//60:02d}:{int(d5.emin.mean())%60:02d}':>12}"
           f"{d5['cum_before'].mean():>14,.0f}")
    P_("")
    P_("    HOW MUCH OF 'ENTRY COUNT' IS REALLY 'ALREADY LOSING TODAY'?")
    P_(f"        corr(ordinal, cumulative session $ before that entry) = "
       f"{T['ordinal'].corr(T['cum_before']):+.3f}")
    P_(f"        corr(ordinal, entry minute)                          = "
       f"{T['ordinal'].corr(T['emin']):+.3f}")
    hi = T["ordinal"] >= 2
    P_(f"        of entries with ordinal >= 2, {100*float((T.loc[hi,'cum_before']<0).mean()):.1f} %"
       f" follow a NEGATIVE running session P&L")
    slope = np.polyfit(T["ordinal"].clip(upper=5), T["net"], 1)[0]
    decline = slope < 0
    P_("")
    P_(f"    STAGE A VERDICT: expectancy slope in ordinal = ${slope:,.0f} per entry"
       f"   -> {'DECLINE PRESENT' if decline else 'NO DECLINE - the wave stops here per the spec'}")
    if not decline:
        P_("")
        P_("    Per the spec, W119's turnover signature is then a property of losing SESSIONS")
        P_("    rather than of marginal ENTRIES. That is a result, not a failure.")
        P_(f"\n[done {_time.time()-t0:.0f}s]")
        out.close(); return

    # ================================================================== STAGE B
    P_("")
    P_("=" * 124)
    P_("=== STAGE B - POLICY. Cap at K new entries per session.")
    P_("=" * 124)
    P_(f"{'arm':<26}{'trades':>9}{'ctr-min':>11}{'net $':>12}{'wk$@fixDD':>11}{'pos wk%':>9}"
       f"{'maxDD':>10}{'CVaR5':>9}{'t':>7}")
    P_(f"{'BASELINE (no cap)':<26}{BASE['n']:>9}{BASE['cm']:>11,.0f}{BASE['net']:>12,.0f}"
       f"{BASE['fixdd']:>11,.0f}{BASE['poswk']:>8.1f}%{BASE['maxdd']:>10,.0f}"
       f"{BASE['cvar']:>9,.0f}{BASE['t']:>7.2f}")
    CAPE = {}
    removed = {}
    for K in CAPS:
        tr = gfills_capped(D, p1, SZ, K, **KW)
        e = econ([{k: v for k, v in x.items() if k != "ei"} for x in tr])
        CAPE[K] = e
        rm = np.zeros(NS, int)
        cnt_b = np.zeros(NS, int); cnt_c = np.zeros(NS, int)
        for x in idt:
            cnt_b[int(sid[x["ei"]])] += 1
        for x in tr:
            cnt_c[int(sid[x["ei"]])] += 1
        rm = np.maximum(cnt_b - cnt_c, 0)
        removed[K] = rm
        P_(f"{f'CAP K={K}':<26}{e['n']:>9}{e['cm']:>11,.0f}{e['net']:>12,.0f}{e['fixdd']:>11,.0f}"
           f"{e['poswk']:>8.1f}%{e['maxdd']:>10,.0f}{e['cvar']:>9,.0f}{e['t']:>7.2f}")
    bestK = max(CAPS, key=lambda K: CAPE[K]["fixdd"])
    P_("")
    P_(f"    best K = {bestK} at ${CAPE[bestK]['fixdd']:,.0f}/wk at fixed DD "
       f"vs baseline ${BASE['fixdd']:,.0f}   removes "
       f"{int(removed[bestK][sess_in].sum()):,} of {BASE['n']:,} entries")

    # ---- the binding control
    P_("")
    P_("=" * 124)
    P_("=== THE BINDING CONTROL - COUNT-MATCHED RANDOM-HALT PLACEBO")
    P_(f"===   {NPERM} draws. Each removes the SAME NUMBER of entries per session as the cap did,")
    P_("===   chosen uniformly at random among that session's own entries. Draws are generated ONCE")
    P_("===   per session and SHARED across the four K arms (W116b: independent draws inflate a")
    P_("===   best-of-K bar).")
    P_("=" * 124)
    ent_by_s = {}
    for x in idt:
        ent_by_s.setdefault(int(sid[x["ei"]]), []).append(int(x["ei"]))
    NUL = {K: np.empty(NPERM) for K in CAPS}
    mxd = np.empty(NPERM)
    for b in range(NPERM):
        perm = {s: rng.permutation(np.asarray(v)) for s, v in ent_by_s.items()}
        vals = []
        for K in CAPS:
            blk = np.zeros(n, bool)
            for s, order in perm.items():
                m_ = int(removed[K][s])
                if m_ > 0:
                    blk[order[:m_]] = True
            e = econ(gfills_blocked(D, p1, SZ, blk, **KW))
            NUL[K][b] = e["fixdd"]; vals.append(e["fixdd"])
        mxd[b] = max(vals)
        if (b + 1) % 50 == 0:
            P_(f"    ... {b+1}/{NPERM} draws [{_time.time()-t0:.0f}s]")
    p95max = float(np.percentile(mxd, 95))
    P_("")
    P_(f"{'arm':<14}{'real wk$@fixDD':>16}{'placebo mean':>14}{'placebo p95':>13}{'pctile':>9}")
    for K in CAPS:
        P_(f"{f'CAP K={K}':<14}{CAPE[K]['fixdd']:>16,.0f}{NUL[K].mean():>14,.0f}"
           f"{np.percentile(NUL[K],95):>13,.0f}"
           f"{100*float((NUL[K] < CAPE[K]['fixdd']).mean()):>8.1f}th")
    P_("")
    P_(f"    BEST-OF-4 placebo bar (shared draws): ${p95max:,.0f}   "
       f"best real ${CAPE[bestK]['fixdd']:,.0f}   "
       f"{'CLEARS' if CAPE[bestK]['fixdd'] > p95max else 'FAILS'}")

    # ---- time-matched halt
    P_("")
    P_("=" * 124)
    P_("=== TIME-MATCHED HALT - separates 'stop after K trades' from 'stop trading later in the day'")
    P_("=" * 124)
    target_rm = int(removed[bestK][sess_in].sum())
    bestT, bestdiff = None, 10 ** 9
    for Tm in range(571, 1020, 15):
        rmT = sum(1 for x in idt if win[int(sid[x["ei"]])] and mod[x["ei"]] >= Tm)
        if abs(rmT - target_rm) < bestdiff:
            bestdiff = abs(rmT - target_rm); bestT = Tm
    blkT = np.zeros(n, bool); blkT[mod >= bestT] = True
    eT = econ(gfills_blocked(D, p1, SZ, blkT, **KW))
    P_(f"    cap K={bestK} removes {target_rm:,} entries; the closest time halt is "
       f"{bestT//60:02d}:{bestT%60:02d} which removes "
       f"{sum(1 for x in idt if win[int(sid[x['ei']])] and mod[x['ei']] >= bestT):,}")
    P_(f"{'arm':<26}{'trades':>9}{'net $':>12}{'wk$@fixDD':>11}{'pos wk%':>9}{'maxDD':>10}")
    P_(f"{f'CAP K={bestK}':<26}{CAPE[bestK]['n']:>9}{CAPE[bestK]['net']:>12,.0f}"
       f"{CAPE[bestK]['fixdd']:>11,.0f}{CAPE[bestK]['poswk']:>8.1f}%{CAPE[bestK]['maxdd']:>10,.0f}")
    P_(f"{f'TIME HALT {bestT//60:02d}:{bestT%60:02d}':<26}{eT['n']:>9}{eT['net']:>12,.0f}"
       f"{eT['fixdd']:>11,.0f}{eT['poswk']:>8.1f}%{eT['maxdd']:>10,.0f}")

    # ---- verdict
    g1 = CAPE[bestK]["fixdd"] > BASE["fixdd"]
    g2 = CAPE[bestK]["fixdd"] > p95max
    g3 = CAPE[bestK]["fixdd"] > eT["fixdd"]
    P_("")
    P_("=" * 124)
    P_("=== VERDICT - all three falsifiers must be cleared")
    P_("=" * 124)
    for lab, g in (("beats the uncapped baseline", g1),
                   ("beats the COUNT-MATCHED placebo's best-of-4 p95", g2),
                   ("beats the TIME-MATCHED halt", g3)):
        P_(f"    {lab:<52}{'PASS' if g else 'FAIL'}")
    P_("")
    P_(f"    {'TURNOVER IS A CAUSAL STATE' if (g1 and g2 and g3) else 'FAILS'}")
    if g1 and not g2:
        P_("    -> beats the baseline but NOT the count-matched placebo: this is EXPOSURE")
        P_("       REDUCTION, not information. Exactly the W109 lesson.")

    # ---- the book
    P_("")
    P_("=" * 124)
    P_("=== EFFECT ON THE FULL BOOK (capped P1 + XM unchanged, inverse-vol)")
    P_("=" * 124)
    WK = pd.read_csv(W110W)
    for lab, ser in (("baseline", BASE["ser"]), (f"cap K={bestK}", CAPE[bestK]["ser"])):
        wp = pd.Series(ser[sess_in]).groupby(wk).sum()
        J = WK.set_index("week")[["xm"]].copy(); J["p1"] = wp
        J = J.dropna()
        sp, sx = J["p1"].std(ddof=1), J["xm"].std(ddof=1)
        w1 = (1 / sp) / ((1 / sp) + (1 / sx))
        v = (w1 * J["p1"] + (1 - w1) * J["xm"]).to_numpy()
        dp = dd_profile(v)
        P_(f"    {lab:<16} book ${v.mean():,.0f}/wk  maxDD ${dp['maxdd']:,.0f}  "
           f"fixDD ${v.mean()*DDT/max(dp['maxdd'],1e-9):,.0f}  "
           f"pos wk {100*float((v>0).mean()):.1f}%")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
