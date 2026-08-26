"""WE_W35 (spec preregistered): quality-conditioned exits, restore re-opened, short quality,
and a frame challenge on what the quality score actually grades."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, weekly, sharpe                           # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w25 import ema                                               # noqa: E402
from run_we_w34 import sized_fills                                       # noqa: E402
from we_quality import build_context, long_vote, short_vote, quality_score  # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W35_QEXIT", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260835)


def fills_qexit(D, pos_arr, size_at_entry, score, halt=1300.0, target=1000.0,
                big_target=None, cut_bars=None, cut_max_score=1):
    """Sized fills with optional quality-conditioned session target and per-trade time cut."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    sess_tgt = target; ent_sc = 0
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False; sess_tgt = target
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if u > 0 and cut_bars is not None and ent_sc <= cut_max_score and i - eti >= cut_bars:
            want = 0
        if (want > 0) != (u > 0):
            if u > 0:
                pnl = u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if spnl <= -halt or (sess_tgt is not None and spnl >= sess_tgt):
                    stopped = True; want = 0
            if want > 0:
                u = int(size_at_entry[i]); epx, eti = o[i], i
                ent_sc = int(score[i])
                if big_target is not None and ent_sc >= 3 and sess_tgt == target:
                    sess_tgt = big_target
                if u < 1:
                    u = 0
            else:
                u = 0
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
    return trades


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    fl = long_vote(D, X)
    pos = (fl >= 0.5).astype(np.int8)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    win = (tarr >= A) & (tarr < B)
    nsw = len(np.unique(D["sid"][win]))
    base_trl = fills_daily(D, pos, halt=1300, target=1000)
    ent_i = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                      for x in base_trl if A <= np.datetime64(x["et"]) < B])
    sc = quality_score(X, ent_i, side=1)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    ref = sized_fills(D, pos, sz)
    d0 = weekly(ref, wk_of, A, B)
    s0, _, wp0 = sharpe(d0)
    p0 = np.array([x["pnl"] for x in ref if A <= np.datetime64(x["et"]) < B])
    v0 = np.array(list(d0.values()))
    ok_h = abs(s0 - 0.331) < 0.02 and abs(p0.sum() / PV / nsw - 15.86) < 0.8
    print(f"HARNESS: Sharpe {s0:.3f} (expect 0.331), pts/session {p0.sum()/PV/nsw:.2f} "
          f"(expect 15.86) -> {'PASS' if ok_h else 'FAIL - VOID'}", flush=True)
    if not ok_h:
        return
    out = open(os.path.join(OUT, "qexit.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)
    rows = []

    def rep(nm, trl, ref_s=None, ref_w=None, ref_p=None):
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        vv = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        u = np.array([x.get("u", 1) for x in trl if A <= np.datetime64(x["et"]) < B])
        st = float((vv - STRESS_RT * len(p) / max(len(vv), 1)).mean())
        tag = ""
        if ref_s is not None:
            ok = (p.sum() / PV / nsw > ref_p and s >= ref_s and vv.min() >= ref_w * 1.15
                  and st > 0)
            tag = "  ADOPT" if ok else "  reject"
        P_(f"{nm:<32}{len(p):>7}{u.mean():>7.2f}{p.sum()/PV/nsw:>10.2f}{p.mean():>9.1f}"
           f"{vv.mean():>9,.0f}{wp:>8.1f}{vv.min():>10,.0f}{s:>8.3f}{st:>8,.0f}{tag}")
        rows.append(dict(arm=nm, n=len(p), pts=round(p.sum() / PV / nsw, 2),
                         per_trade=round(p.mean(), 1), wk=round(vv.mean()),
                         pos=round(wp, 1), worst=round(float(vv.min())),
                         sharpe=round(s, 3), stress=round(st)))
        return s, float(vv.min()), p.sum() / PV / nsw

    hdr = (f"{'arm':<32}{'n':>7}{'avgSz':>7}{'pts/ses':>10}{'$/tr':>9}{'wkMean':>9}"
           f"{'wkPos%':>8}{'worst':>10}{'sharpe':>8}{'stress':>8}")
    P_("=== REFERENCE (W34 quality-sized) ===")
    P_(hdr)
    rs, rw, rp = rep("REF quality-sized", ref)

    P_("\n=== A QUALITY-CONDITIONED EXIT ===")
    rep("A1 big target on quality", fills_qexit(D, pos, sz, sc, big_target=2000), rs, rw, rp)
    for cb in (60, 120):
        rep(f"A2 cut low-quality @{cb}b", fills_qexit(D, pos, sz, sc, cut_bars=cb),
            rs, rw, rp)
    rep("A3 both (big tgt + cut 120)",
        fills_qexit(D, pos, sz, sc, big_target=2000, cut_bars=120), rs, rw, rp)

    P_("\n=== B RESTORE, RE-OPENED WITH THE QUALITY GATE ===")
    vs = []
    for mem in MEMBERS:
        tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem], restore="plain")
        for q in (None, 0.7, 0.8, 0.9):
            okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
            for dg in (True, False):
                a = okv & (X["dL"] if dg else True)
                vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
    fr_r = np.vstack(vs).mean(axis=0)
    pos_r = (fr_r >= 0.5).astype(np.int8)
    for k in (3, 4):
        gated = pos_r.copy()
        newly = pos_r.astype(bool) & ~pos.astype(bool)      # bars restore adds
        gated[newly & (sc < k)] = 0
        rep(f"B restore, quality>={k}", sized_fills(D, gated, sz), rs, rw, rp)

    P_("\n=== C QUALITY ON THE SHORT SIDE ===")
    fs = short_vote(D, X)
    sposs = -(fs >= 0.5).astype(np.int8)
    sh_base = fills_daily(D, sposs, halt=1300, target=1000)
    ent_s = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                      for x in sh_base if A <= np.datetime64(x["et"]) < B])
    scs = quality_score(X, ent_s, side=-1)
    P_(hdr)
    rep("C short base", sh_base)
    szs = np.where(scs >= 3, 2, 1).astype(np.int8)
    sh_q = sized_fills(D, -sposs, szs)      # sized_fills is long-only; mirror the P&L
    for x in sh_q:
        x["pnl"] = -x["pnl"] - 2 * COMM_RT * x["u"]        # mirror + keep commission a cost
    rep("C short quality-sized", sh_q)
    P_("   (mirror construction disclosed: the long-only sizer is run on the inverted path and")
    P_("    the P&L negated, with commission re-added as a cost.)")

    P_("\n=== E FRAME CHALLENGE: does the score grade FLIPS or the MARKET STATE? ===")
    P_(hdr)
    nl = int(pos.sum())
    rnd = np.zeros(n, np.int8)
    on = RNG.choice(n, size=nl, replace=False)
    rnd[on] = 1
    r_trl = fills_daily(D, rnd, halt=1300, target=1000)
    rs2, rw2, rp2 = rep("E random entries, size 1", r_trl)
    rep("E random entries, quality-sized", sized_fills(D, rnd, sz), rs2, rw2, rp2)
    emap = (ema(D["c"], 20) > ema(D["c"], 100))
    emap = np.concatenate([[False], emap[:-1]]).astype(np.int8)
    e_trl = fills_daily(D, emap, halt=1300, target=1000)
    es, ew, ep = rep("E EMA-cross, size 1", e_trl)
    rep("E EMA-cross, quality-sized", sized_fills(D, emap, sz), es, ew, ep)
    P_("\ninterpretation rule (declared in the spec): if the score lifts the random and")
    P_("EMA arms as much as it lifts the Solar vote, it is a MARKET-STATE edge, not a flip")
    P_("grader, and the frame must change.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
