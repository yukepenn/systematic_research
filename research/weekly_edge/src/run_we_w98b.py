"""WE_W98b - the mechanism evidence and the null W98's spec did not carry.

W98 measured that a per-contract session box beats the incumbent dollar box on P1 by +39.0 % at
fixed drawdown, that a UNIFORMLY looser dollar box does not (-5.4 %, paired p = 0.940), and that
holding the average dollar budget fixed while making it size-conditional keeps the whole gain
(+39.6 %). Three things are still owed:

  1. DIRECT MECHANISM. How often does the box actually fire, and at what point excursion, split by
     whether the session held a size-2 position? If the story is true the ABS arm must be halting
     size-2 sessions at roughly half the point move.
  2. A NULL FOR THE MAGNITUDE. Permute WHICH entries carry size 2, preserving the count, and
     recompute the PCT - ABS gap. Stated in advance: a high percentile means the quality score
     interacts with the box - the trades the box was cutting short were the good ones. A middling
     percentile means it is PURE ACCOUNTING, which is still a defect worth fixing but is NOT an
     alpha finding, and the +39 % must then be described as recovering a mis-metered budget.
  3. ATTRIBUTION. How much of the gap is sessions the two arms halt differently?
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
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W98_BOXDENOM", "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
NPERM = 200
SEED = 98


def gfills_diag(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, per_ctr=False):
    """gfills, plus a per-session record of whether/how the box fired."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n, sid = D["fb"], D["lb"], D["n"], D["sid"]
    trades = []
    ev = {}                       # session -> dict(kind, pts, maxu)
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    cur = -1; maxu = 0
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
            cur = int(sid[i]); maxu = 0
            ev[cur] = dict(kind="none", pts=np.nan, maxu=0)
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
                    if cur in ev and ev[cur]["kind"] == "none":
                        ev[cur]["kind"] = "loss" if spnl <= -halt else "target"
                        ev[cur]["pts"] = abs(o[i] - epx)
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
                    maxu = max(maxu, u)
                    if cur in ev:
                        ev[cur]["maxu"] = maxu
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
    return trades, ev


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "w98b_mechanism.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    pos = vl.astype(np.int8)
    bb = fills_daily(D, pos, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    SZ = np.where(sc >= 3, 2, 1).astype(np.int8)
    P_(f"    P1 signal rebuilt on {n:,} bars / {len(sess_in):,} in-window sessions "
       f"[{_time.time()-t0:.0f}s]")

    def rate(trl):
        w = {}
        for x in trl:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts)
                m_ = p_.hour * 60 + p_.minute
                w[m_] = w.get(m_, 0.0) + x["u"]
        tot = sum(w.values())
        return TICKV * sum(float(prof.get(m, 3.0)) * c_ for m, c_ in w.items()) / max(tot, 1e-9)

    def score(trl):
        """weekly $ at fixed max drawdown, net of this arm's own spread friction"""
        sp = np.zeros(D["n_sess"]); ct = np.zeros(D["n_sess"])
        for x in trl:
            s_ = int(sid[i_of(x["et"])])
            sp[s_] += x["pnl"]; ct[s_] += x["u"]
        r = rate(trl)
        ser = sp[sess_in] - r * ct[sess_in]
        w = pd.Series(ser).groupby(wk).sum().to_numpy()
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(fixdd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    weekly=float(w.mean()), poswk=100 * float((w > 0).mean()),
                    top5=dp["dd_mean_top5"], maxdd=dp["maxdd"], streak=int(stk),
                    trades=len(trl), ctr=sum(x["u"] for x in trl))

    # =============================================================== 1. mechanism
    P_("")
    P_("=" * 118)
    P_("=== 1. DOES THE BOX ACTUALLY FIRE EARLIER ON SIZE-2 SESSIONS? (direct mechanism)")
    P_("=" * 118)
    RES = {}
    for arm in ("ABS", "PCT"):
        tr, ev = gfills_diag(D, pos, SZ, **arm_kw(arm, 1.0))
        RES[arm] = (keep(tr), ev)
    P_(f"{'arm':<6}{'sess':>7}{'halt-loss':>11}{'halt-tgt':>10}{'no box':>9}"
       f"{'pts@halt sz1':>15}{'pts@halt sz2':>15}")
    mrows = []
    for arm in ("ABS", "PCT"):
        ev = RES[arm][1]
        rows = [ev[s] for s in sess_in if s in ev]
        nl = sum(1 for r in rows if r["kind"] == "loss")
        nt = sum(1 for r in rows if r["kind"] == "target")
        p1 = [r["pts"] for r in rows if r["kind"] == "loss" and r["maxu"] == 1]
        p2 = [r["pts"] for r in rows if r["kind"] == "loss" and r["maxu"] >= 2]
        P_(f"{arm:<6}{len(rows):>7,}{nl:>11,}{nt:>10,}{len(rows)-nl-nt:>9,}"
           f"{(np.mean(p1) if p1 else np.nan):>15.2f}{(np.mean(p2) if p2 else np.nan):>15.2f}")
        mrows.append(dict(arm=arm, sess=len(rows), halt_loss=nl, halt_tgt=nt,
                          pts_sz1=float(np.mean(p1)) if p1 else np.nan,
                          pts_sz2=float(np.mean(p2)) if p2 else np.nan,
                          n_sz1=len(p1), n_sz2=len(p2)))
    pd.DataFrame(mrows).to_csv(os.path.join(OUT, "w98b_halt.csv"), index=False)
    P_("")
    P_("    PREDICTION IF THE STORY IS TRUE: under ABS the mean point excursion at which a")
    P_("    LOSS-halt fires is roughly HALF on size-2 sessions; under PCT the two are equal.")

    # =============================================================== 3. attribution
    P_("")
    P_("=" * 118)
    P_("=== 3. WHERE DOES THE GAP COME FROM? Sessions the two arms halt differently.")
    P_("=" * 118)
    ea, ep = RES["ABS"][1], RES["PCT"][1]
    diff = [s for s in sess_in if s in ea and s in ep and ea[s]["kind"] != ep[s]["kind"]]
    sp = {}
    for arm in ("ABS", "PCT"):
        v = np.zeros(D["n_sess"])
        for x in RES[arm][0]:
            v[int(sid[i_of(x["et"])])] += x["pnl"]
        sp[arm] = v
    d_all = float((sp["PCT"] - sp["ABS"])[sess_in].sum())
    d_dif = float((sp["PCT"] - sp["ABS"])[np.array(diff)].sum()) if diff else 0.0
    P_(f"    sessions where the halt outcome differs: {len(diff):,} of {len(sess_in):,} "
       f"({100*len(diff)/len(sess_in):.1f} %)")
    P_(f"    gross P&L difference PCT - ABS, ALL sessions ............ ${d_all:>12,.0f}")
    P_(f"    ... of which comes from those divergent sessions ........ ${d_dif:>12,.0f} "
       f"({100*d_dif/d_all if d_all else 0:.1f} %)")

    # =============================================================== 2. the null
    P_("")
    P_("=" * 118)
    P_("=== 2. NULL: permute WHICH entries carry size 2 (count preserved). Is the gap bigger")
    P_("===    because the box was cutting short the trades the SCORE liked, or is it accounting?")
    P_("=" * 118)
    real_abs, real_pct = score(RES["ABS"][0]), score(RES["PCT"][0])
    real_gap = real_pct["fixdd"] - real_abs["fixdd"]
    ent = np.array(sorted({i_of(x["et"]) for x in RES["ABS"][0]}))
    n2 = int(sum(1 for x in RES["ABS"][0] if x["u"] >= 2))
    P_(f"    real: ABS {real_abs['fixdd']:,.0f} -> PCT {real_pct['fixdd']:,.0f}   "
       f"gap {real_gap:+,.0f}   ({len(ent):,} entry bars, {n2:,} carry size 2)")
    rng = np.random.default_rng(SEED)
    gaps = np.empty(NPERM)
    t1 = _time.time()
    for b_ in range(NPERM):
        pick = rng.choice(len(ent), size=n2, replace=False)
        szp = np.ones(n, np.int8)
        szp[ent[pick]] = 2
        ga = score(keep(gfills(D, pos, szp, **arm_kw("ABS", 1.0))))["fixdd"]
        gp = score(keep(gfills(D, pos, szp, **arm_kw("PCT", 1.0))))["fixdd"]
        gaps[b_] = gp - ga
        if b_ == 0:
            P_(f"    [1 permutation costs {_time.time()-t1:.1f}s; {NPERM} will take "
               f"~{NPERM*(_time.time()-t1)/60:.0f} min]")
        if (b_ + 1) % 25 == 0:
            P_(f"    {b_+1:>4}/{NPERM}  null gap mean {gaps[:b_+1].mean():+,.0f}  "
               f"real {real_gap:+,.0f}  pct {100*float((gaps[:b_+1] < real_gap).mean()):.1f}"
               f"  [{_time.time()-t0:.0f}s]")
    pctile = 100 * float((gaps < real_gap).mean())
    P_("")
    P_(f"    null gap: mean {gaps.mean():+,.0f}  sd {gaps.std(ddof=1):,.0f}  "
       f"min {gaps.min():+,.0f}  max {gaps.max():+,.0f}")
    P_(f"    REAL gap {real_gap:+,.0f}  ->  {pctile:.1f}th percentile of {NPERM} permutations")
    P_("")
    if pctile >= 95:
        P_("    READ: the quality score INTERACTS with the box - the size-2 trades the dollar box")
        P_("          was cutting short are specifically the ones worth not cutting short.")
    elif gaps.mean() > 0.5 * real_gap:
        P_("    READ: MOSTLY ACCOUNTING. A random assignment of the same number of size-2 entries")
        P_("          recovers most of the gap. The dollar box was mis-metering a variable-size")
        P_("          position; fixing it is an ENGINEERING CORRECTION, not an alpha discovery.")
    else:
        P_("    READ: intermediate - part accounting, part score interaction. Both are reported.")
    pd.DataFrame(dict(perm=np.arange(NPERM), gap=gaps)).to_csv(
        os.path.join(OUT, "w98b_null.csv"), index=False)

    # =============================================================== 4. why the deep era reverses
    P_("")
    P_("=" * 118)
    P_("=== 4. W98's Tier-3 stress REVERSED for P1 (-31.4 % on 2006-2021). Is the box simply a")
    P_("===    different animal at NQ 1,200 than at NQ 23,000? Measure how often it fires.")
    P_("=" * 118)
    from run_we_w19 import MEMBERS  # noqa: F401  (imported by votes)
    from we_channels import build_channels  # noqa: F401
    W80OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    nd, sidd = DD["n"], DD["sid"]
    XD = fast_build_context(DD)
    zz = np.load(os.path.join(W80OUT, f"mem_deep_{nd}.npz"))
    memd, bmomd, tiltd = zz["mem"], zz["bmom"], zz["tilt"]
    vld, _ = votes(DD, memd, bmomd, tiltd, XD, bmomd)
    posd = vld.astype(np.int8)
    bbd = fills_daily(DD, posd, halt=1300, target=1000)
    tdd = DD["t"]
    eed = np.array([int(min(np.searchsorted(tdd, np.datetime64(x["et"])), nd - 1))
                    for x in bbd])
    scd, _ = causal_score(XD, eed, window=WIN)
    SZd = np.where(scd >= 3, 2, 1).astype(np.int8)
    yrd = pd.to_datetime(DD["sess_date"]).year.to_numpy()
    P_(f"    deep P1 rebuilt [{_time.time()-t0:.0f}s]")
    P_("")
    P_(f"{'era':<14}{'arm':<6}{'sess':>7}{'halt-loss %':>13}{'halt-tgt %':>12}"
       f"{'pts@halt sz1':>15}{'pts@halt sz2':>15}{'mean sess range pts':>21}")
    erows = []
    rngm = {}
    for tag, Dx, posx, szx, sel, yy in (
            ("2006-2021", DD, posd, SZd, np.arange(DD["n_sess"]), yrd),
            ("2022-2026", D, pos, SZ, sess_in, pd.to_datetime(D["sess_date"]).year.to_numpy())):
        stx = np.zeros(Dx["n_sess"], np.int64); stx[Dx["sid"][Dx["fb"]]] = np.flatnonzero(Dx["fb"])
        enx = np.r_[stx[1:], Dx["n"]]
        rr = np.array([Dx["h"][stx[s]:enx[s]].max() - Dx["l"][stx[s]:enx[s]].min()
                       for s in sel])
        rngm[tag] = float(rr.mean())
        for arm in ("ABS", "PCT"):
            _, evx = gfills_diag(Dx, posx, szx, **arm_kw(arm, 1.0))
            rows = [evx[s] for s in sel if s in evx]
            nl = sum(1 for r in rows if r["kind"] == "loss")
            nt = sum(1 for r in rows if r["kind"] == "target")
            p1 = [r["pts"] for r in rows if r["kind"] == "loss" and r["maxu"] == 1]
            p2 = [r["pts"] for r in rows if r["kind"] == "loss" and r["maxu"] >= 2]
            P_(f"{tag:<14}{arm:<6}{len(rows):>7,}{100*nl/max(len(rows),1):>12.1f}%"
               f"{100*nt/max(len(rows),1):>11.1f}%"
               f"{(np.mean(p1) if p1 else np.nan):>15.2f}"
               f"{(np.mean(p2) if p2 else np.nan):>15.2f}{rngm[tag]:>21.1f}")
            erows.append(dict(era=tag, arm=arm, sess=len(rows), halt_loss=nl, halt_tgt=nt,
                              pts_sz1=float(np.mean(p1)) if p1 else np.nan,
                              pts_sz2=float(np.mean(p2)) if p2 else np.nan,
                              mean_range=rngm[tag]))
        P_("")
    pd.DataFrame(erows).to_csv(os.path.join(OUT, "w98b_era.csv"), index=False)
    P_("    A $1,300 box is 65 NQ points in BOTH eras, but the mean session range is not the")
    P_("    same number of points in both eras. If the box binds far more often in one era, the")
    P_("    denominator question is being asked of two different instruments.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
