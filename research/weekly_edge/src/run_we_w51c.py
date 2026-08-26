"""WE_W51c - amendment_2 phases E and F: what E4 actually does, and whether 0.5 is a fit.

E4 = do not START a long while price is in the LOWER HALF of the session's realised range so
far.  Causal by construction: the range is measured through bar i-1 and compared with the
close of bar i-1, and the fill happens at bar i+1's open.

Nothing is adopted here. Phase G (the nulls) is run_we_w51d.py and it is the binding test.
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
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, classify, A, B                    # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W51_DONTTRADE", "out")
os.makedirs(OUT, exist_ok=True)
KS = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


# --------------------------------------------------------------------------- shared plumbing
def setup():
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = build_context(D)
    TG = targets(D)
    st, en, elapsed = session_frames(D)
    return D, X, TG, st, en


def pos_range_feature(D, st, en):
    """(close_{i-1} - session low through i-1) / (session range through i-1), causal."""
    n = D["n"]
    h_, l_, c = D["h"], D["l"], D["c"]
    runhi = np.zeros(n); runlo = np.zeros(n)
    for s in range(D["n_sess"]):
        a, b = st[s], en[s]
        hh = np.maximum.accumulate(h_[a:b]); ll = np.minimum.accumulate(l_[a:b])
        runhi[a:b] = np.concatenate([[h_[a]], hh[:-1]])
        runlo[a:b] = np.concatenate([[l_[a]], ll[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    return (c_l - runlo) / np.maximum(runhi - runlo, 1e-9)


def entry_only(D, pos, allow):
    """The gate blocks NEW entries; once open the object exits on its own terms."""
    n = D["n"]
    held = np.zeros(n, np.int8)
    h0 = 0
    fb = D["fb"]
    for i in range(n):
        if fb[i]:
            h0 = 0
        if pos[i] == 0:
            h0 = 0
        elif h0 == 0 and allow[i]:
            h0 = 1
        held[i] = h0
    return held


def dd_profile(v):
    """Drawdown as a distribution, not a single number. v = weekly P&L series."""
    cum = np.cumsum(v)
    peak = np.maximum.accumulate(cum)
    dd = peak - cum
    # episodes: peak -> trough -> new peak
    eps, cur = [], 0.0
    for x in dd:
        if x > 0:
            cur = max(cur, x)
        elif cur > 0:
            eps.append(cur); cur = 0.0
    if cur > 0:
        eps.append(cur)
    eps = sorted(eps, reverse=True)
    return dict(maxdd=float(dd.max()), dd5=[round(float(x)) for x in eps[:5]],
                dd_mean_top5=float(np.mean(eps[:5])) if eps else 0.0,
                dd_mean=float(dd[dd > 0].mean()) if (dd > 0).any() else 0.0,
                pct_underwater=float(100 * (dd > 0).mean()),
                ulcer=float(np.sqrt((dd ** 2).mean())))


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "w51c.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    sess_yr = pd.to_datetime(D["sess_date"]).year.values
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    klass = classify(D, st, en)

    def build(pos, sizing=True):
        base = fills_daily(D, pos, halt=1300, target=1000)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(ent) < 300:
            return None
        sc, _ = causal_score(X, ent, window=WIN)
        sz = (np.where(sc >= 3, 2, 1) if sizing else np.ones(n)).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc)
                if A <= np.datetime64(x["et"]) < B]

    def ledger(trl):
        sp = np.zeros(D["n_sess"]); cm = np.zeros(D["n_sess"])
        for x in trl:
            s = int(sid[i_of(x["et"])])
            sp[s] += x["pnl"]
            cm[s] += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                      / np.timedelta64(1, "m"))
        return sp[sess_in], cm[sess_in]

    def metrics(sp, ntr, name, cm, expo0=None):
        v = np.bincount(wk_idx, weights=sp, minlength=NW)
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        sd = v.std(ddof=1)
        dp = dd_profile(v)
        traded = sp != 0
        r = dict(arm=name, n=ntr, pts=round(float(sp.sum() / PV / NS), 2),
                 wk=round(float(v.mean())),
                 wkpos=round(100 * float((v > 0).mean()), 1),
                 daypos=round(100 * float((sp > 0).mean()), 1),
                 trddaypos=round(100 * float((sp[traded] > 0).mean())
                                 if traded.any() else 0.0, 1),
                 worst=round(float(v.min())), maxdd=round(dp["maxdd"]),
                 dd_top5=round(dp["dd_mean_top5"]), ulcer=round(dp["ulcer"]),
                 underwater=round(dp["pct_underwater"], 1),
                 mar=round(float(v.sum() / max(dp["maxdd"], 1e-9)), 2),
                 annshrp=round(float(v.mean() / sd * np.sqrt(52)) if sd > 0 else 0.0, 2),
                 eff=round(float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9, 3),
                 cveff=round(float(v.mean() / abs(cv)) if cv < 0 else 9.9, 3),
                 stress=round(float(v.mean() - STRESS_RT * ntr / len(v))),
                 expo=round(float(cm.sum())), dd5=dp["dd5"])
        r["expo_pct"] = round(100 * r["expo"] / max(expo0 if expo0 else r["expo"], 1e-9), 1)
        return r

    HDR = (f"{'arm':<32}{'trds':>6}{'pts':>7}{'wk$':>8}{'wk+%':>6}{'trdD+%':>8}{'worst':>9}"
           f"{'maxDD':>9}{'top5DD':>9}{'ulcer':>8}{'uw%':>6}{'MAR':>7}{'annShrp':>8}"
           f"{'cvEff':>7}{'expo%':>7}")

    def show(r):
        P_(f"{r['arm']:<32}{r['n']:>6}{r['pts']:>7.2f}{r['wk']:>8,.0f}{r['wkpos']:>6.1f}"
           f"{r['trddaypos']:>8.1f}{r['worst']:>9,.0f}{r['maxdd']:>9,.0f}{r['dd_top5']:>9,.0f}"
           f"{r['ulcer']:>8,.0f}{r['underwater']:>6.1f}{r['mar']:>7.2f}{r['annshrp']:>8.2f}"
           f"{r['cveff']:>7.3f}{r['expo_pct']:>7.1f}")

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    trs0 = build(posL)
    sp0, cm0 = ledger(trs0)
    EXPO0 = float(cm0.sum())
    r0 = metrics(sp0, len(trs0), "P1 INCUMBENT", cm0, EXPO0)
    P_(f"=== B1 GATE: {r0['pts']:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(r0['pts'] - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(r0["pts"] - 14.72) >= 0.6:
        out.close(); return

    pr = pos_range_feature(D, st, en)
    posE4 = entry_only(D, posL, pr >= 0.5)
    trsE4 = build(posE4)
    spE4, cmE4 = ledger(trsE4)
    rE4 = metrics(spE4, len(trsE4), "E4 entry-only lower-half block", cmE4, EXPO0)

    # =====================================================================================
    # PHASE E - ATTRIBUTION
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE E1: where the change lands (W50 classes, DIAGNOSTIC only)")
    P_(f"{'='*112}")
    kin = klass[sess_in]
    P_(f"{'arm':<32}" + "".join(f"{k:>13}" for k in KS) + f"{'total':>9}")
    for nm, sp in (("P1 INCUMBENT", sp0), ("E4", spE4)):
        P_(f"{nm:<32}" + "".join(f"{sp[kin == k].sum()/PV/NS:>13.2f}" for k in KS)
           + f"{sp.sum()/PV/NS:>9.2f}")
    P_(f"{'DELTA':<32}"
       + "".join(f"{(spE4[kin == k].sum()-sp0[kin == k].sum())/PV/NS:>13.2f}" for k in KS)
       + f"{(spE4.sum()-sp0.sum())/PV/NS:>9.2f}")

    P_(f"\n=== PHASE E2: what E4 blocks ===")
    # an incumbent entry is 'blocked' if the gate was false at that bar
    ent0 = [(i_of(x["et"]), x) for x in trs0]
    blk = [(i, x) for i, x in ent0 if not (pr[i] >= 0.5)]
    kept = [(i, x) for i, x in ent0 if (pr[i] >= 0.5)]
    P_(f"   incumbent entries {len(ent0)} | gate false at {len(blk)} ({100*len(blk)/len(ent0):.1f} %)")
    P_(f"   mean P&L of incumbent trades entered where the gate is FALSE: "
       f"${np.mean([x['pnl'] for _, x in blk]):,.0f}  (win rate "
       f"{100*np.mean([x['pnl'] > 0 for _, x in blk]):.1f} %)")
    P_(f"   mean P&L of incumbent trades entered where the gate is TRUE : "
       f"${np.mean([x['pnl'] for _, x in kept]):,.0f}  (win rate "
       f"{100*np.mean([x['pnl'] > 0 for _, x in kept]):.1f} %)")
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    BUCK = [("18:00-00:00", 1080, 1440), ("00:00-08:00", 0, 480),
            ("08:00-10:30", 480, 630), ("10:30-14:00", 630, 840), ("14:00-17:00", 840, 1080)]
    P_(f"\n{'entry window':<16}{'incumbent':>12}{'gate FALSE':>12}{'blocked %':>11}"
       f"{'their $/trade':>15}")
    for lab, a_, b_ in BUCK:
        m0 = [x for i, x in ent0 if a_ <= mod[i] < b_]
        mb = [x for i, x in blk if a_ <= mod[i] < b_]
        P_(f"{lab:<16}{len(m0):>12}{len(mb):>12}"
           f"{100*len(mb)/max(len(m0),1):>10.1f}%"
           f"{(np.mean([x['pnl'] for x in mb]) if mb else 0):>15,.0f}")
    P_(f"\n{'session class':<16}{'incumbent':>12}{'gate FALSE':>12}{'blocked %':>11}"
       f"{'their $/trade':>15}")
    for k in KS:
        m0 = [x for i, x in ent0 if klass[int(sid[i])] == k]
        mb = [x for i, x in blk if klass[int(sid[i])] == k]
        P_(f"{k:<16}{len(m0):>12}{len(mb):>12}{100*len(mb)/max(len(m0),1):>10.1f}%"
           f"{(np.mean([x['pnl'] for x in mb]) if mb else 0):>15,.0f}")

    P_(f"\n=== PHASE E3: is E4 the GATE, or an interaction with the sizing layer? ===")
    P_(f"   corr(pos_sess_range, dist_open) over all bars = "
       f"{np.corrcoef(pr, X['dist_open'])[0,1]:.3f}   "
       f"at incumbent entries = "
       f"{np.corrcoef(pr[[i for i,_ in ent0]], X['dist_open'][[i for i,_ in ent0]])[0,1]:.3f}")
    P_(HDR)
    show(r0); show(rE4)
    for nm, pos in (("P1 no sizing (1 lot)", posL), ("E4 no sizing (1 lot)", posE4)):
        trl = build(pos, sizing=False)
        sp, cm = ledger(trl)
        show(metrics(sp, len(trl), nm, cm, EXPO0))

    P_(f"\n=== PHASE E4: the session-box interaction (why E1 made the worst week worse) ===")

    def box_fires(trl):
        by = {}
        for x in trl:
            by.setdefault(int(sid[i_of(x["et"])]), []).append(x)
        halt = tgt = 0
        for s, xs in by.items():
            xs = sorted(xs, key=lambda z: z["et"])
            cum = 0.0
            for z in xs:
                cum += z["pnl"]
                if cum <= -1300:
                    halt += 1; break
                if cum >= 1000:
                    tgt += 1; break
        return halt, tgt, len(by)
    P_(f"{'arm':<32}{'sessions traded':>17}{'box HALT':>10}{'box TARGET':>12}{'halt %':>9}")
    e1 = entry_only(D, posL, X["dist_open"] >= 0.0)
    for nm, trl in (("P1 INCUMBENT", trs0), ("E4", trsE4),
                    ("E1 entry-only price>=open", build(e1))):
        hh, tt, ns_ = box_fires(trl)
        P_(f"{nm:<32}{ns_:>17}{hh:>10}{tt:>12}{100*hh/max(ns_,1):>8.1f}%")

    # =====================================================================================
    # PHASE F - ROBUSTNESS
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE F1: is 0.5 a spike? (STABILITY CHECK - adoption stays at 0.5)")
    P_(f"{'='*112}")
    P_(HDR)
    show(r0)
    rob = []
    for thr in (0.3, 0.4, 0.5, 0.6, 0.7):
        trl = build(entry_only(D, posL, pr >= thr))
        sp, cm = ledger(trl)
        r = metrics(sp, len(trl), f"E4 threshold {thr:.1f}", cm, EXPO0)
        show(r); rob.append(r)
    pd.DataFrame(rob).to_csv(os.path.join(OUT, "e4_robust.csv"), index=False)

    P_(f"\n=== PHASE F2: per year (pts/session) ===")
    yrs = sorted(set(sess_yr[sess_in]))
    P_(f"{'arm':<32}" + "".join(f"{y:>12}" for y in yrs))
    for nm, sp in (("P1 INCUMBENT", sp0), ("E4", spE4)):
        P_(f"{nm:<32}"
           + "".join(f"{sp[sess_yr[sess_in]==y].sum()/PV/max((sess_yr[sess_in]==y).sum(),1):>12.2f}"
                     for y in yrs))
    P_(f"{'DELTA':<32}"
       + "".join(f"{(spE4[sess_yr[sess_in]==y].sum()-sp0[sess_yr[sess_in]==y].sum())/PV/max((sess_yr[sess_in]==y).sum(),1):>12.2f}"
                 for y in yrs))

    P_(f"\n=== PHASE F3: the drawdown DISTRIBUTION (max drawdown is one observation) ===")
    P_(f"{'arm':<32}{'5 deepest drawdowns ($)':>46}{'mean top5':>12}{'ulcer':>9}{'uw%':>7}")
    for r in (r0, rE4):
        P_(f"{r['arm']:<32}{str(r['dd5']):>46}{r['dd_top5']:>12,.0f}"
           f"{r['ulcer']:>9,.0f}{r['underwater']:>7.1f}")

    P_(f"\n=== PHASE F4: E4 combined with the VWAP gate (reported, not adopted) ===")
    P_(HDR)
    show(r0); show(rE4)
    trl = build(entry_only(D, posL, (pr >= 0.5) & (X["dist_vwap"] >= 0.0)))
    sp, cm = ledger(trl)
    show(metrics(sp, len(trl), "E4 and price>=VWAP", cm, EXPO0))

    pd.DataFrame([r0, rE4]).to_csv(os.path.join(OUT, "e4_attrib.csv"), index=False)
    P_(f"\n=== STATUS: nothing adopted. run_we_w51d.py holds the binding nulls. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
