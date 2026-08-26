"""WE_W50 CAPTURE AUDIT (spec preregistered): what does the object capture, and what is left?

The object is a volatility-scaled trend-reversal ratchet, so it captures ONE kind of session
structure and is blind to the others by construction. The campaign has never produced a
complete, current decomposition of where a session's money goes and which part we take.
This wave produces it, so the next engine is chosen by measurement rather than by intuition.

Nothing is adopted here. The output is a ranked agenda.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W50_CAPTURE", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    X = build_context(D)
    TG = targets(D)
    idx = np.arange(n)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    out = open(os.path.join(OUT, "capture.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    pos = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, pos, halt=1300, target=1000)
    bl = [x for x in base if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    sc, _ = causal_score(X, entL, window=WIN)
    szq = np.where(sc >= 3, 2, 1).astype(np.int8)
    P1 = fills_qexit(D, pos, szq, sc)
    # per-bar realised position of the traded object (size ignored; direction only)
    held = np.zeros(n, np.int8)
    for x in P1:
        e, xi = i_of(x["et"]), i_of(x["xt"])
        held[e:max(xi, e + 1)] = 1
    sess = [s for s in range(D["n_sess"])
            if A <= tarr[idx[D["sid"] == s][0]] < B]
    NS = len(sess)
    ptot = np.array([x["pnl"] for x in P1
                     if A <= np.datetime64(x["et"]) < B]).sum() / PV
    P_(f"=== B1: {ptot/NS:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(ptot/NS-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(ptot / NS - 14.72) >= 0.6:
        out.close(); return

    # ---------------- per-session ledger ----------------------------------------------
    pnl_s = {}
    for x in P1:
        if A <= np.datetime64(x["et"]) < B:
            s_ = int(D["sid"][i_of(x["et"])])
            pnl_s[s_] = pnl_s.get(s_, 0.0) + x["pnl"]
    rows = []
    for s in sess:
        m = idx[D["sid"] == s]
        op, cl = o[m[0]], c[m[-1]]
        hi, lo = h[m].max(), l[m].min()
        rng = hi - lo
        body = cl - op
        # perfect-foresight single trade within the session
        run_min = np.minimum.accumulate(l[m])
        best_long = float((h[m] - run_min).max())
        run_max = np.maximum.accumulate(h[m])
        best_short = float((run_max - l[m]).max())
        avail = max(best_long, best_short)
        # class (DIAGNOSTIC ONLY - uses end-of-session information)
        if rng <= 1e-9:
            klass = "MIXED"
        elif abs(body) >= 0.60 * rng:
            klass = "TREND-UP" if body > 0 else "TREND-DOWN"
        elif abs(body) <= 0.25 * rng:
            klass = "RANGE"
        else:
            ih, il = int(np.argmax(h[m])), int(np.argmin(l[m]))
            klass = "REVERSAL" if ((ih < il and (cl - lo) < 0.40 * rng) or
                                   (il < ih and (hi - cl) < 0.40 * rng)) else "MIXED"
        hm = held[m].astype(bool)
        first = int(np.argmax(hm)) if hm.any() else -1
        last = int(len(m) - 1 - np.argmax(hm[::-1])) if hm.any() else -1
        got = pnl_s.get(s, 0.0) / PV
        # leakage attribution, mutually exclusive and exhaustive on the LONG-only object
        if first < 0:
            never, late, early, wrong, chop = avail, 0.0, 0.0, 0.0, 0.0
        else:
            late = float(max(0.0, (h[m[:first + 1]].max() - l[m[:first + 1]].min())))
            early = float(max(0.0, (h[m[last:]].max() - l[m[last:]].min())))
            inwin = m[first:last + 1]
            inavail = float((np.maximum.accumulate(h[inwin]) - l[inwin]).max()
                            if len(inwin) else 0.0)
            inavail_long = float((h[inwin] - np.minimum.accumulate(l[inwin])).max()
                                 if len(inwin) else 0.0)
            wrong = float(max(0.0, -got)) if body < 0 else 0.0
            chop = float(max(0.0, inavail_long - max(got, 0.0) - wrong))
            never = float(max(0.0, avail - late - early - chop - wrong - max(got, 0.0)))
        rows.append(dict(sess=s, date=str(D["sess_date"][s]), klass=klass, wk=wkmap[s],
                         rng=rng, body=body, avail=avail, got=got,
                         never=never, late=late, early=early, wrong=wrong, chop=chop,
                         trades=sum(1 for x in P1
                                    if A <= np.datetime64(x["et"]) < B
                                    and int(D["sid"][i_of(x["et"])]) == s),
                         inmkt=float(hm.mean())))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "sessions.csv"), index=False)

    P_(f"\n=== PHASE 1: SESSION TAXONOMY (diagnostic; uses end-of-session facts) ===")
    P_(f"{'class':<14}{'sessions':>10}{'share%':>8}{'avail/ses':>11}{'availShare%':>13}"
       f"{'ourPts/ses':>12}{'capture%':>10}{'trades/ses':>12}{'inMkt%':>8}")
    tot_av = R["avail"].sum()
    for k in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        q = R[R["klass"] == k]
        if not len(q):
            continue
        P_(f"{k:<14}{len(q):>10}{100*len(q)/len(R):>8.1f}{q['avail'].mean():>11.1f}"
           f"{100*q['avail'].sum()/tot_av:>13.1f}{q['got'].mean():>12.2f}"
           f"{100*q['got'].sum()/max(q['avail'].sum(),1e-9):>10.2f}"
           f"{q['trades'].mean():>12.2f}{100*q['inmkt'].mean():>8.1f}")
    P_(f"{'ALL':<14}{len(R):>10}{100.0:>8.1f}{R['avail'].mean():>11.1f}{100.0:>13.1f}"
       f"{R['got'].mean():>12.2f}{100*R['got'].sum()/tot_av:>10.2f}"
       f"{R['trades'].mean():>12.2f}{100*R['inmkt'].mean():>8.1f}")

    P_(f"\n=== PHASE 2: LEAKAGE LEDGER (points per session; sums to available) ===")
    parts = ["got", "never", "late", "early", "wrong", "chop"]
    chk = R[parts].sum(axis=1).sum() / max(R["avail"].sum(), 1e-9)
    P_(f"   ledger closes to {100*chk:.1f} % of available "
       f"({'OK' if abs(chk-1) < 0.15 else 'RESIDUAL - attribution approximate, see note'})")
    P_(f"{'class':<14}" + "".join(f"{p:>10}" for p in parts) + f"{'avail':>10}")
    for k in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED", "ALL"):
        q = R if k == "ALL" else R[R["klass"] == k]
        if not len(q):
            continue
        P_(f"{k:<14}" + "".join(f"{q[p].mean():>10.1f}" for p in parts)
           + f"{q['avail'].mean():>10.1f}")
    R.groupby("klass")[parts + ["avail"]].mean().to_csv(
        os.path.join(OUT, "leakage.csv"))

    P_(f"\n=== PHASE 3: RISK LEDGER - what makes the worst weeks ===")
    wk = R.groupby("wk").agg(pnl=("got", "sum"), n=("got", "size"))
    worst = wk.nsmallest(max(3, len(wk) // 10), "pnl")
    P_(f"   worst {len(worst)} weeks of {len(wk)}: mean {worst['pnl'].mean()*PV:,.0f} $, "
       f"total {worst['pnl'].sum()*PV:,.0f} $")
    inw = R[R["wk"].isin(worst.index)]
    P_(f"   their session classes: "
       + ", ".join(f"{k} {100*v/len(inw):.0f} %"
                   for k, v in inw["klass"].value_counts().items()))
    P_(f"   all-sessions classes:  "
       + ", ".join(f"{k} {100*v/len(R):.0f} %"
                   for k, v in R["klass"].value_counts().items()))
    los = inw[inw["got"] < 0]
    P_(f"   inside those weeks: {len(los)} losing sessions of {len(inw)}, "
       f"mean {los['got'].mean()*PV:,.0f} $, worst single session "
       f"{los['got'].min()*PV:,.0f} $")
    P_(f"   concentration: worst single session is "
       f"{100*abs(los['got'].min())/abs(worst['pnl'].sum()):.1f} % of the whole worst-decile "
       f"loss -> {'SINGLE-SESSION' if abs(los['got'].min()) > 0.25*abs(worst['pnl'].sum()) else 'ACCUMULATION'}")

    P_(f"\n=== PHASE 4: COMPLEMENT TEST - is the un-captured movement actually takeable? ===")
    P_(f"{'class':<14}{'capture%':>10}{'perfect pts/ses':>17}{'open-to-close':>15}"
       f"{'O2C net stress':>16}{'verdict':>24}")
    for k in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        q = R[R["klass"] == k]
        if not len(q):
            continue
        cap = 100 * q["got"].sum() / max(q["avail"].sum(), 1e-9)
        o2c = float(q["body"].abs().mean())          # perfect-direction open-to-close
        o2c_net = o2c - (STRESS_RT / PV)
        verdict = ("not an opportunity" if o2c_net < 1.0 else
                   ("ALREADY WELL CAPTURED" if cap >= 25 else "OPPORTUNITY - rank by size"))
        P_(f"{k:<14}{cap:>10.2f}{q['avail'].mean():>17.1f}{o2c:>15.1f}{o2c_net:>16.1f}"
           f"{verdict:>24}")
    P_("\n   note: the open-to-close column is a CEILING that requires knowing the session's")
    P_("   direction in advance. It bounds what any engine in that class could earn; it is")
    P_("   not an achievable result.")

    P_(f"\n=== RANKED AGENDA (un-captured movement x whether a simple rule could take it) ===")
    ag = []
    for k in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        q = R[R["klass"] == k]
        if not len(q):
            continue
        uncap = float(q["avail"].sum() - q["got"].sum()) / NS
        ceil_ = float(q["body"].abs().sum()) / NS - (STRESS_RT / PV) * len(q) / NS
        ag.append((k, uncap, ceil_, 100 * q["got"].sum() / max(q["avail"].sum(), 1e-9)))
    ag.sort(key=lambda r: -min(r[1], max(r[2], 0)))
    for k, uncap, ceil_, cap in ag:
        P_(f"   {k:<12} un-captured {uncap:>7.2f} pts/session | simple-rule ceiling "
           f"{ceil_:>7.2f} | current capture {cap:>6.2f} %")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
