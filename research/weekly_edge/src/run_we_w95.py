"""WE_W95 - IS THE SESSION BOX WORTH HAVING ON A PORTFOLIO?

Spec: runs/WE_W95_BOXLESS/spec.yaml, committed BEFORE this ran.

The box clears a 98th-percentile circular-shift null (W28) and is chosen in 15 of 17 honest
refits (W29) - all on P1, a single fused long-only object. W91 measured a {Solar, BMOM} portfolio
scoring BETTER with no box at all, on metrics that are scale-invariant. This adjudicates it, with
the incumbent control reproduced first and the same null W28 used.
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
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w93 import build                                             # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W95_BOXLESS", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
NOBOX = 1e15
C_P1, C_X9A, C_BMOM = 14.52, 14.55, 12.99
NDRAW = 200
RNG = np.random.default_rng(20260895)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "boxless.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    sess_end = D["sess_end"]
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    bm = np.where(flatm, 0, bmom).astype(np.int8)
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    inw = np.array([in_win[s] for s in sid])
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    NWk = len(set(wk))
    P_(f"=== {len(sess_in)} sessions / {NWk} weeks [{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    def daily(t):
        sp = np.zeros(D["n_sess"])
        for x in t:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def cmin(t):
        v = np.zeros(n)
        for x in t:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return float(v[inw].sum())

    def pan(v, cost_wk, msk=None):
        m = np.ones(len(v), bool) if msk is None else msk
        w = pd.Series(v[m]).groupby(wk[m]).sum().to_numpy() - cost_wk
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9))

    VL, VS = build(D, mem, bmom, tilt, X)
    CH = build_channels(D, which=["X9a_disp_sessanchor"])

    # --- the P1-family object with an arbitrary channel, box optional, SCORE built consistently
    def solar_obj(chan, halt, target):
        # rebuild TG for this channel
        blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
        idx = {v: k for k, v in enumerate(L13)}

        def ra(x):
            return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

        def hyst(M):
            tg = np.zeros(n, np.int8)
            for i in range(n):
                p = 0 if (i == 0 or fb[i]) else tg[i - 1]
                g = p
                if flatm[i]:
                    g = 0
                elif p == 0:
                    if not blocked[i]:
                        g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
                elif p > 0:
                    g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
                else:
                    g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
                tg[i] = g
            return tg
        TG = {}
        for name, vols in MEMBERS.items():
            cols = [idx[v] for v in vols]
            s_ = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            TG[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        vs = []
        for m_ in MEMBERS:
            tg = TG[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & X["dL"] if dg else okv
                    vs.append(np.where((tg > 0) & a_, 1, 0).astype(np.int8))
        p = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        # SCORE built from the SAME box regime the object will trade under (W91's defect)
        bb = fills_daily(D, p, halt=(1300 if halt < 1e14 else int(1e9)),
                         target=(1000 if halt < 1e14 else None))
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return keep(fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_,
                                halt=halt, target=target))

    P_("")
    P_("=" * 118)
    P_("=== B1 CONTROL: P1 WITH the box must reproduce the incumbent before anything else")
    P_("=" * 118)
    TRA = solar_obj(bmom, 1300.0, 1000.0)
    ptsA = sum(x["pnl"] + COMM_RT * x["u"] for x in TRA) / PV / len(sess_in)
    P_(f"    P1 (boxed): {len(TRA):,} trades, {ptsA:.4f} pts/session, "
       f"net ${sum(x['pnl'] for x in TRA):,.0f}")
    P_("    committed reference (W89/W91/W92 rebuild): 2,002 trades, 13.73 pts/session, $280,131")
    okb1 = (len(TRA) == 2002) and abs(ptsA - 13.73) < 0.07
    P_(f"    B1: {'REPRODUCED' if okb1 else '*** FAILED - no other arm is interpreted ***'}")
    if not okb1:
        out.close(); return

    # ---------------------------------------------------------------- the six arms
    P_("")
    P_("=" * 118)
    P_("=== THE ARMS, matched in contract-minutes to the corresponding boxed arm")
    P_("=" * 118)
    TRB = solar_obj(bmom, NOBOX, None)
    TRx_b = solar_obj(CH["X9a_disp_sessanchor"], 1300.0, 1000.0)
    TRx_n = solar_obj(CH["X9a_disp_sessanchor"], NOBOX, None)
    TRm_b = keep(sfills(D, bm, halt=1300.0, target=1000.0))
    TRm_n = keep(sfills(D, bm, halt=NOBOX, target=None))
    tgtN = np.where(VL & VS, 0, np.where(VL, 1, np.where(VS, -1, 0))).astype(np.int8)
    TRn_b = keep(sfills(D, tgtN, halt=1300.0, target=1000.0))
    TRn_n = keep(sfills(D, tgtN, halt=NOBOX, target=None))

    def pair(trm, trx):
        ser = 2 * daily(trm) + 3 * daily(trx)
        cm = 2 * cmin(trm) + 3 * cmin(trx)
        cost = (2 * C_BMOM * sum(x["u"] for x in trm) + 3 * C_X9A * sum(x["u"] for x in trx)) / NWk
        ntr = 2 * len(trm) + 3 * len(trx)
        return ser, cm, cost, ntr

    def single(tr, c):
        return daily(tr), cmin(tr), c * sum(x["u"] for x in tr) / NWk, len(tr)

    ARMS = {
        "A  P1 + box": single(TRA, C_P1),
        "B  P1 no box": single(TRB, C_P1),
        "C  pair 2:3 + boxes": pair(TRm_b, TRx_b),
        "D  pair 2:3 no box": pair(TRm_n, TRx_n),
        "E  NETFUSE_1 + box": single(TRn_b, C_P1),
        "F  NETFUSE_1 no box": single(TRn_n, C_P1),
    }
    REF = {"A": "A  P1 + box", "B": "A  P1 + box", "C": "C  pair 2:3 + boxes",
           "D": "C  pair 2:3 + boxes", "E": "E  NETFUSE_1 + box", "F": "E  NETFUSE_1 + box"}
    P_(f"{'arm':<22}{'trades':>8}{'scale':>7}{'wk $':>9}{'wk+%':>8}{'strk':>6}{'maxDD':>10}"
       f"{'top5DD':>9}{'worst':>10}{'wk$@fixDD':>11}")
    R = {}
    rows = []
    for k, (ser, cm, cost, ntr) in ARMS.items():
        s = ARMS[REF[k[0]]][1] / cm
        a = pan(ser * s, cost * s)
        R[k[0]] = a
        P_(f"{k:<22}{ntr:>8,}{s:>7.3f}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['streak']:>6}"
           f"{a['maxdd']:>10,.0f}{a['top5']:>9,.0f}{a['worst']:>10,.0f}{a['weekly_dd']:>11,.0f}")
        rows.append(dict(arm=k, trades=ntr, scale=s, **a))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "arms.csv"), index=False)

    def legs(x, y):
        """how many of the three gate legs does x win against y"""
        return sum([x["weekly_dd"] > y["weekly_dd"], x["wkpos"] > y["wkpos"],
                    x["top5"] < y["top5"]])
    P_("")
    P_("=== H1: does the box HELP the single object and HURT the portfolio?")
    ab = legs(R["A"], R["B"]); dc = legs(R["D"], R["C"]); fe = legs(R["F"], R["E"])
    P_(f"    P1:        BOX wins {ab}/3 against no-box   "
       f"({'box helps' if ab >= 2 else 'box HURTS'})")
    P_(f"    pair 2:3:  NO-BOX wins {dc}/3 against box   "
       f"({'box HURTS' if dc >= 2 else 'box helps'})")
    P_(f"    NETFUSE_1: NO-BOX wins {fe}/3 against box   "
       f"({'box HURTS' if fe >= 2 else 'box helps'})")
    h1 = (ab >= 2) and (dc >= 2)
    P_(f"    H1 (box helps single AND hurts portfolio): {'PASS' if h1 else 'FAIL'}")

    # ---------------------------------------------------------------- H2: the W28 null
    P_("")
    P_("=" * 118)
    P_("=== H2: W28's CIRCULAR-SHIFT NULL, run on the PORTFOLIO and on P1 so they compare")
    P_("=== Session s is boxed according to session (s+k)'s box EVENTS: the frequency and the")
    P_("=== intraday timing of interventions are preserved; only WHICH session they hit changes.")
    P_("=" * 118)
    starts = np.flatnonzero(fb)
    bounds = list(starts) + [n]
    blocks = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    NB = len(blocks)

    def box_events(tr_boxed, tr_free):
        """per session: the bar index at which the box first suppressed activity, or -1."""
        ev = np.full(D["n_sess"], -1, np.int64)
        last_b = {}
        for x in tr_boxed:
            s = int(sid[i_of(x["et"])]); last_b[s] = max(last_b.get(s, -1), i_of(x["xt"]))
        for s, i in last_b.items():
            ev[s] = i
        return ev

    def apply_shifted_box(tgt_arr, size_arr, ev, k, is_signed):
        """flat from the shifted session's cut-off bar onward, within each session"""
        t2 = tgt_arr.copy()
        for i, (a_, b_) in enumerate(blocks):
            s_src = (i + int(k)) % NB
            cut = ev[s_src]
            if cut < 0:
                continue
            a2, b2 = blocks[s_src]
            off = min(max(cut - a2, 0), b_ - a_)
            t2[a_ + off:b_] = 0
        return t2

    def null_for(tgt_arr, tr_boxed, tr_free, cost_rate, ref_cm, signed=True):
        ev = box_events(tr_boxed, tr_free)
        real = pan(daily(tr_boxed) * (ref_cm / cmin(tr_boxed)),
                   cost_rate * sum(x["u"] for x in tr_boxed) / NWk * (ref_cm / cmin(tr_boxed)))
        ks = RNG.choice(np.arange(1, NB), size=min(NDRAW, NB - 1), replace=False)
        rr = []
        for k in ks:
            t2 = apply_shifted_box(tgt_arr, None, ev, k, signed)
            tr2 = keep(sfills(D, t2, halt=NOBOX, target=None))
            if not tr2:
                continue
            s2 = ref_cm / max(cmin(tr2), 1.0)
            rr.append(pan(daily(tr2) * s2, cost_rate * sum(x["u"] for x in tr2) / NWk * s2))
        return real, pd.DataFrame(rr)

    # P1: use its unsized long target so sfills is comparable
    plong = np.where(np.array([1 if x else 0 for x in VL]), 1, 0).astype(np.int8)
    realP, nullP = null_for(plong, keep(sfills(D, plong, halt=1300.0, target=1000.0)),
                            TRB, C_P1, cmin(keep(sfills(D, plong, halt=1300.0, target=1000.0))))
    realN, nullN = null_for(tgtN, TRn_b, TRn_n, C_P1, cmin(TRn_b))
    P_("")
    P_(f"{'object':<20}{'leg':<22}{'real':>11}{'null mean':>12}{'null p95':>12}{'pctile':>9}")
    nrows = []
    for nm, real, nl in (("P1 (long, size 1)", realP, nullP), ("NETFUSE_1", realN, nullN)):
        for leg, key, hi in (("weekly $ at fixed DD", "weekly_dd", True),
                             ("positive-week %", "wkpos", True),
                             ("raw mean top-5 DD", "top5", False)):
            v = nl[key].to_numpy()
            pc = 100 * float((v < real[key]).mean()) if hi else 100 * float((v > real[key]).mean())
            P_(f"{nm:<20}{leg:<22}{real[key]:>11,.1f}{v.mean():>12,.1f}"
               f"{np.percentile(v, 95 if hi else 5):>12,.1f}{pc:>8.1f}%")
            nrows.append(dict(obj=nm, leg=leg, real=real[key], null_mean=float(v.mean()),
                              pctile=pc))
        P_("")
    pd.DataFrame(nrows).to_csv(os.path.join(OUT, "box_null.csv"), index=False)
    P_("    Read: a HIGH percentile means the REAL box placement beats arbitrary box placements")
    P_("    (W28 got 98th on P1). A LOW percentile means the box is doing nothing that the same")
    P_("    number of arbitrary interventions would not do.")

    # ---------------------------------------------------------------- H3: events vs tail
    P_("")
    P_("=" * 118)
    P_("=== H3: is the damage explained by EVENT REDUCTION (mechanism law 6)?")
    P_("=" * 118)
    P_(f"{'halt':>7}{'target':>8}{'trades':>9}{'wk $':>9}{'wk+%':>8}{'top5DD':>10}"
       f"{'wk$@fixDD':>11}")
    grid = []
    refcm = cmin(TRn_b)
    for h in (600, 900, 1300, 2000, 3000, 5000, NOBOX):
        for tg in (600, 1000, 1600, 3000, None):
            if h >= 1e14 and tg is not None:
                continue
            tr = keep(sfills(D, tgtN, halt=float(h), target=tg))
            if not tr:
                continue
            s = refcm / max(cmin(tr), 1.0)
            a = pan(daily(tr) * s, C_P1 * sum(x["u"] for x in tr) / NWk * s)
            hl = "none" if h >= 1e14 else str(h)
            P_(f"{hl:>7}{str(tg):>8}{len(tr):>9,}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%"
               f"{a['top5']:>10,.0f}{a['weekly_dd']:>11,.0f}")
            grid.append(dict(halt=hl, target=str(tg), trades=len(tr), **a))
    G = pd.DataFrame(grid)
    G.to_csv(os.path.join(OUT, "box_grid.csv"), index=False)
    r = float(np.corrcoef(G["trades"], G["top5"])[0, 1])
    r2 = float(np.corrcoef(G["trades"], G["weekly_dd"])[0, 1])
    P_("")
    P_(f"    corr(trade count, raw top-5 drawdown)      = {r:+.3f}   "
       f"(law 6 predicts NEGATIVE: more events, smaller tail)")
    P_(f"    corr(trade count, weekly $ at fixed DD)    = {r2:+.3f}   "
       f"(law 6 predicts POSITIVE)")
    h3 = (r < -0.4) and (r2 > 0.4)
    P_(f"    H3: {'SUPPORTED' if h3 else 'NOT SUPPORTED - the mechanism is UNKNOWN'}")

    P_("")
    P_("=" * 118)
    P_(f"    H1 {'PASS' if h1 else 'FAIL'}   "
       f"H3 {'SUPPORTED' if h3 else 'NOT SUPPORTED'}")
    P_("    NOTHING IS ADOPTED. The box is not removed from P1 under any outcome (W28's 98th")
    P_("    percentile is not overturned by a portfolio measurement).")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
