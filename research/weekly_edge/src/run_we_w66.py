"""WE_W66 - the object's CORE SIGNAL PARAMETERS, never examined in 65 waves.

The VolMult ladder [6..30], the 460-bar sigma window, the 3.0/1.0 hysteresis and the 40-1200
tick clamp were inherited from the vendor's Solar Wave and frozen as "frozen truth" in campaign
#1. W59 scanned 216 OUTER cells and explicitly excluded these as "a different object needing its
own wave". That wave was never written.

The wave AGGREGATES and never selects: selection has lost at every scale this campaign has
tested (W59: 2.0th percentile free, 18.7th constrained), and different VolMults of the same
ratchet - and the same ratchet at different sigma timescales - are the most near-exchangeable
members this object has.

INFRASTRUCTURE: run_we_w01.sm14_1m gained a `return_members` hook. A member's ratchet state
depends only on price and its own VolMult, never on which set it belongs to (the property W52
verified). So ONE engine run per sigma window yields every ladder, every prefix and every
hysteresis by recomputation - 3 runs instead of 72. The identity gate below proves it.
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
from run_we_w01 import ROOT, PV, sm14_1m, round_away                     # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
os.makedirs(OUT, exist_ok=True)
WIDE = list(range(4, 41))              # the widest ladder: VolMult 4..40 step 1, 37 members
SIGMAS = (230, 460, 920)
BASE = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
LADDERS = {
    "L0 incumbent 6-30 step2": BASE,
    "L1 extend down 4-30": [4] + BASE,
    "L2 extend up 6-40": BASE + [32, 34, 36, 38, 40],
    "L3 extend both 4-40": [4] + BASE + [32, 34, 36, 38, 40],
    "L4 denser 6-30 step1": list(range(6, 31)),
    "L5 wide+dense 4-40 step1": list(range(4, 41)),
}
DD_TARGET = 20245.0


def rebuild_targets(mem, bmom, tilt, cols, D, entry=3.0, exit_=1.0):
    """Recompute the engine's target path for an arbitrary member SUBSET, in numpy + one
    sequential pass for the hysteresis. Must reproduce sm14_1m exactly - the gate proves it."""
    n = mem.shape[0]
    fb, sid, t = D["fb"], D["sid"], D["t"]
    sess_end = D["sess_end"]
    def ra(x):
        # round half AWAY from zero, vectorised - identical to run_we_w01.round_away
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))
    s = mem[:, cols].sum(axis=1).astype(np.int32)
    nm = len(cols)
    T = np.clip(ra(s / float(nm) * 10.0), -10, 10)
    agree = (np.sign(s) == tilt) & (s != 0) & (tilt != 0)
    mm = np.where(agree, 1.25, 1.0)
    Tp = np.clip(ra(T * mm * 0.9026), -13, 13)
    M = 0.7086 * Tp + 2.83 * bmom.astype(float)
    blocked = t >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flat = t >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    tgt = np.zeros(n, np.int8)
    p = 0
    for i in range(n):
        p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
        g = p
        if flat[i]:
            g = 0
        elif p == 0:
            if not blocked[i]:
                if M[i] >= entry:
                    g = 1
                elif M[i] <= -entry:
                    g = -1
        elif p > 0:
            if M[i] <= -entry and not blocked[i]:
                g = -1
            elif M[i] <= exit_:
                g = 0
        else:
            if M[i] >= entry and not blocked[i]:
                g = 1
            elif M[i] >= -exit_:
                g = 0
        tgt[i] = g
    return tgt


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "inner.txt"), "w", encoding="utf-8")

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

    # ---------------- ONE engine run per sigma window ------------------------------------
    MEMS = {}
    for vp in SIGMAS:
        f = os.path.join(OUT, f"mem_{vp}_{D['n']}.npz")
        if os.path.exists(f):
            z = np.load(f)
            MEMS[vp] = (z["mem"], z["bmom"], z["tilt"])
            P_(f"   loaded member matrix sigma={vp} from cache [{_time.time()-t0:.0f}s]")
            continue
        P_(f"   building member matrix sigma={vp}, {len(WIDE)} members x {n:,} bars "
           f"[{_time.time()-t0:.0f}s]")
        _, mem, bmom, tilt = sm14_1m(D, vp, return_members=True, volmults=WIDE)
        np.savez_compressed(f, mem=mem, bmom=bmom, tilt=tilt)
        MEMS[vp] = (mem, bmom, tilt)
        P_(f"      done [{_time.time()-t0:.0f}s]")

    # ---------------- IDENTITY GATE: the rebuild must be exact ----------------------------
    mem, bmom, tilt = MEMS[460]
    idx_of = {v: k for k, v in enumerate(WIDE)}
    P_(f"\n=== IDENTITY GATE: rebuild must reproduce sm14_1m bit-for-bit ===")
    ok_all = True
    for nmn, vms in MEMBERS.items():
        cols = [idx_of[v] for v in vms]
        rb = rebuild_targets(mem, bmom, tilt, cols, D)
        ref = TG[nmn]
        d = int((rb != ref).sum())
        P_(f"   {nmn:<10} {len(vms):>3} members  disagreeing bars {d:>8}  "
           f"({'EXACT' if d == 0 else 'MISMATCH - VOID'})")
        ok_all &= (d == 0)
    if not ok_all:
        P_("   -> the reconstruction is not exact. The wave is VOID rather than approximate.")
        out.close(); return
    P_(f"   -> EXACT on all four member sets. Every ladder below is a column subset of one "
       f"engine run. [{_time.time()-t0:.0f}s]")

    # ---------------- the object, for any ladder x sigma set ------------------------------
    def vote_from(tg_by_set):
        vs = []
        for nmn in tg_by_set:
            tg = tg_by_set[nmn]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)

    def prefixes(ladder):
        """the incumbent's own structure, generalised by VolMult VALUE not by count"""
        out_ = {}
        for cut in (14, 16, 18, 10 ** 9):
            sel = [v for v in ladder if v <= cut]
            if len(sel) >= 3:
                out_[f"<= {cut}"] = sel
        return out_

    def build(ladder, sigmas):
        tg_sets = {}
        for cut, vms in prefixes(ladder).items():
            acc = None
            for vp in sigmas:
                m_, b_, tl_ = MEMS[vp]
                cols = [idx_of[v] for v in vms]
                tg = rebuild_targets(m_, b_, tl_, cols, D).astype(float)
                acc = tg if acc is None else acc + tg
            tg_sets[cut] = acc / len(sigmas)          # the aggregate over sigma timescales
        f = vote_from(tg_sets)
        pos = (f >= 0.5).astype(np.int8)
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 200:
            return None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], len(trl)

    def met(sp, ntr, name, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        cnt = np.bincount(wi, minlength=NW) > 0
        v = np.bincount(wi, weights=s, minlength=NW)[cnt]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s != 0
        st_ = lambda a: max((len(list(g)) for kk, g in __import__("itertools").groupby(a < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(s.sum() / PV / max(len(s), 1)),
                    daypos=100 * float((s > 0).mean()),
                    trdpos=100 * float((s[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(st_(v)),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)
    HDR = (f"{'arm':<34}{'mem':>5}{'trds':>7}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}")

    def show(r, nm_, tag=""):
        P_(f"{r['arm']:<34}{nm_:>5}{r['ntr']:>7}{r['pts']:>7.2f}{r['daypos']:>7.1f}"
           f"{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{tag}")

    # ---------------- PHASE 0: does the clamp bind? --------------------------------------
    P_(f"\n{'='*124}\n=== PHASE 0: does the S clamp bind? "
       f"S = clamp(VolMult x sigma, 40 ticks, 1200 ticks)")
    P_(f"{'='*124}")
    c_ = D["c"]
    dif = np.abs(np.diff(c_, prepend=c_[0]))
    sig = pd.Series(dif).rolling(460, min_periods=100).mean().values
    P_(f"{'VolMult':<10}" + "".join(f"{y:>16}" for y in sorted(set(sdate.year))))
    P_(f"{'':<10}" + "".join(f"{'floor% cap%':>16}" for _ in sorted(set(sdate.year))))
    clampr = []
    ys = pd.to_datetime(D["sess_date"])[D["sid"]].year.values
    for vm in (4, 6, 10, 20, 30, 40):
        line = f"{vm:<10}"
        for y in sorted(set(sdate.year)):
            m = (ys == y) & np.isfinite(sig)
            s_ = vm * sig[m]
            fl = 100 * float((s_ < 40 * 0.25).mean())
            cp = 100 * float((s_ > 1200 * 0.25).mean())
            line += f"{fl:>8.1f}{cp:>8.1f}"
            clampr.append(dict(volmult=vm, year=y, floor_pct=fl, cap_pct=cp))
        P_(line)
    pd.DataFrame(clampr).to_csv(os.path.join(OUT, "clamp.csv"), index=False)

    # ---------------- PHASE 1 + 2: ladders and sigma aggregation --------------------------
    P_(f"\n{'='*124}\n=== PHASE 1: the ladder's ends and density (aggregate, never select)")
    P_(f"{'='*124}")
    P_("Every arm is a strictly LARGER near-exchangeable set that CONTAINS the incumbent's 13.")
    P_("All at a fixed $20,245 max drawdown so weekly$ compares directly.\n")
    P_(HDR)
    rows, ledger = [], {}
    for nm_, lad in LADDERS.items():
        r = build(lad, [460])
        if r is None:
            continue
        sp, ntr = r
        m_ = met(sp, ntr, nm_)
        show(m_, len(lad), "   <- INCUMBENT" if nm_.startswith("L0") else "")
        rows.append(m_); ledger[nm_] = sp
    P_(f"\n{'='*124}\n=== PHASE 2: the SIGMA TIMESCALE - the axis that has never been varied")
    P_(f"{'='*124}")
    P_(f"sigma in {SIGMAS}: the same ratchet estimating the same quantity at different speeds.\n")
    P_(HDR)
    for nm_, lad in (("L0 incumbent", BASE), ("L5 wide+dense", list(range(4, 41)))):
        for sg in ([230], [920], [230, 460], [460, 920], [230, 460, 920]):
            tagn = f"{nm_} sigma{'+'.join(str(x) for x in sg)}"
            r = build(lad, sg)
            if r is None:
                continue
            sp, ntr = r
            m_ = met(sp, ntr, tagn)
            show(m_, len(lad))
            rows.append(m_); ledger[tagn] = sp
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "arms.csv"), index=False)

    # ---------------- PHASE 4: SUB-PERIOD STABILITY, the bar W60 arms all failed ----------
    P_(f"\n{'='*124}\n=== PHASE 4: sub-period stability - every W60 arm scored 0 % on 'all three'")
    P_(f"{'='*124}")
    inc = ledger["L0 incumbent 6-30 step2"]
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    P_(f"{'arm':<34}{'windows':>9}{'trdD+% wins':>14}{'weekly$ wins':>15}{'top5DD wins':>14}"
       f"{'ALL THREE':>12}")
    subs = []
    for nm_, sp in ledger.items():
        if nm_ == "L0 incumbent 6-30 step2":
            continue
        c1 = c2 = c3 = c4 = tot = 0
        for eend in ends:
            b0 = eend - pd.DateOffset(months=24)
            mk = (sdate > b0) & (sdate <= eend)
            a_, b_ = met(sp, 0, "", mk), met(inc, 0, "", mk)
            if a_ is None or b_ is None:
                continue
            tot += 1
            x1 = a_["trdpos"] > b_["trdpos"]; x2 = a_["weekly"] > b_["weekly"]
            x3 = a_["dd_top5"] < b_["dd_top5"]
            c1 += x1; c2 += x2; c3 += x3; c4 += (x1 and x2 and x3)
        P_(f"{nm_:<34}{tot:>9}{100*c1/max(tot,1):>13.0f}%{100*c2/max(tot,1):>14.0f}%"
           f"{100*c3/max(tot,1):>13.0f}%{100*c4/max(tot,1):>11.0f}%")
        subs.append(dict(arm=nm_, n=tot, trd=100*c1/max(tot,1), wk=100*c2/max(tot,1),
                         dd=100*c3/max(tot,1), all3=100*c4/max(tot,1)))
    pd.DataFrame(subs).to_csv(os.path.join(OUT, "subperiod.csv"), index=False)
    P_(f"\n   per year (pts/session), incumbent first:")
    yrs = sorted(set(sdate.year))
    P_(f"{'arm':<34}" + "".join(f"{y:>10}" for y in yrs))
    for nm_, sp in ledger.items():
        P_(f"{nm_:<34}" + "".join(
            f"{sp[sdate.year == y].sum()/PV/max((sdate.year == y).sum(),1):>10.2f}" for y in yrs))
    P_(f"\n=== STATUS: nothing adopted. Nulls are in run_we_w66b.py. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
