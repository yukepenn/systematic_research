"""WE_W24 SHORT (spec preregistered): shorts designed for the short side, not mirrored."""
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
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly, sharpe                       # noqa: E402
from run_we_w23 import signed_fills, build_side_paths                    # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W24_SHORT", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def timed_fills(D, sig, hold_bars, halt=1300.0):
    """Short entries from a pulse array with a hard time exit."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; epx = 0.0; eti = -1; spnl = 0.0; halted = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; halted = False
        if p != 0 and (i - eti >= hold_bars or lb[i]):
            px = c[i] if lb[i] else o[i]
            pnl = p * (px - epx) * PV - COMM_RT
            trades.append(dict(d=p, u=1, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            spnl += pnl; p = 0
            if spnl <= -halt:
                halted = True
        if lb[i]:
            continue
        if p == 0 and not halted and i > 0 and sig[i - 1] < 0:
            p = -1; epx, eti = o[i], i
    return trades


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    pl, _, ratio, norm = build_side_paths(D, "long")
    ps, _, _, _ = build_side_paths(D, "short")
    fl = np.vstack([pl[k] for k in pl]).mean(axis=0)
    fs = -np.vstack([ps[k] for k in ps]).mean(axis=0)
    n = D["n"]
    print(f"paths ready [{_time.time()-t0:.0f}s]", flush=True)
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), D["n"] - 1))
        return wkmap[int(D["sid"][i])]

    # session features
    idx = np.arange(n)
    n_sess = D["n_sess"]
    s_hi = np.zeros(n_sess); s_lo = np.zeros(n_sess); s_op = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        s_hi[s] = D["h"][m].max(); s_lo[s] = D["l"][m].min(); s_op[s] = D["o"][m[0]]
    prev_hi = np.concatenate([[np.nan], s_hi[:-1]])[D["sid"]]
    prev_lo = np.concatenate([[np.nan], s_lo[:-1]])[D["sid"]]
    open_now = s_op[D["sid"]]
    tr = np.maximum(D["h"] - D["l"], np.maximum(np.abs(D["h"] - np.roll(D["c"], 1)),
                                                np.abs(D["l"] - np.roll(D["c"], 1))))
    tr[0] = D["h"][0] - D["l"][0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    atr = np.concatenate([[atr[0]], atr[:-1]])
    cprev = np.concatenate([[D["c"][0]], D["c"][:-1]])
    sess_close = np.array([D["c"][idx[D["sid"] == s][-1]] for s in range(n_sess)])
    tilt = np.zeros(n_sess, np.int8)
    for s in range(52, n_sess):
        tilt[s] = int(np.sign(sess_close[s - 1] - sess_close[s - 51:s - 1].mean()))
    tiltbar = tilt[D["sid"]]

    # reference pair
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    e5 = signed_fills(D, (fl >= 0.5).astype(np.int8), halt=1300)
    d5 = weekly(e5, wk_of, A, B); d1 = weekly(s1, wk_of, A, B)
    dref = {w: d5.get(w, 0.0) + d1.get(w, 0.0) for w in set(d5) | set(d1)}
    sref, netref, posref = sharpe(dref)
    wref = min(dref.values()); mref = np.mean(list(dref.values()))

    out = open(os.path.join(OUT, "short.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []
    P(f"REFERENCE  E5halt1300 + S1 : Sharpe {sref:.3f}  wk ${mref:,.0f}  "
      f"pos {posref:.1f}%  worst ${wref:,.0f}\n")
    P(f"{'short engine':<28}{'n':>7}{'net':>11}{'wkMean':>9}{'pos%':>7}{'worst':>10}"
      f"{'shrp':>7}   | combined with the reference pair")
    P(f"{'':<28}{'':>7}{'':>11}{'':>9}{'':>7}{'':>10}{'':>7}   "
      f"{'wkMean':>9}{'pos%':>7}{'worst':>10}{'shrp':>7}  verdict")

    def test(nm, trl):
        if len(trl) < 60:
            P(f"{nm:<28} only {len(trl)} trades")
            return
        d = weekly(trl, wk_of, A, B)
        s, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        dc = {w: dref.get(w, 0.0) + d.get(w, 0.0) for w in set(dref) | set(d)}
        s2, net2, pos2 = sharpe(dc)
        v2 = np.array(list(dc.values()))
        gain = 100 * (v2.mean() - mref) / abs(mref)
        deg = 100 * (wref - v2.min()) / abs(wref)
        ok = (s2 >= sref and pos2 > posref and deg < gain)
        P(f"{nm:<28}{len(trl):>7}{net:>11,.0f}{v.mean():>9,.0f}{pos:>7.1f}{v.min():>10,.0f}"
          f"{s:>7.3f}   {v2.mean():>9,.0f}{pos2:>7.1f}{v2.min():>10,.0f}{s2:>7.3f}"
          f"  {'ADOPT' if ok else 'reject'}")
        rows.append(dict(name=nm, n=len(trl), wk_mean=round(v.mean()), pos=round(pos, 1),
                         worst=round(v.min()), sharpe=round(s, 3),
                         comb_wk=round(v2.mean()), comb_pos=round(pos2, 1),
                         comb_worst=round(v2.min()), comb_sharpe=round(s2, 3),
                         verdict="ADOPT" if ok else "reject"))

    short_vote = (fs >= 0.5)
    # X1 vol expansion
    for r in (1.2, 1.5):
        arr = np.where(short_vote & (ratio >= r), -1, 0).astype(np.int8)
        test(f"X1 vol-expansion r>={r}", signed_fills(D, arr, halt=1300))
    # X2 breakdown of prior low
    bd = np.where(~np.isnan(prev_lo) & (cprev < prev_lo), -1, 0).astype(np.int8)
    hold = np.zeros(n, np.int8); cur = 0
    for i in range(n):
        if D["fb"][i]:
            cur = 0
        if bd[i] < 0:
            cur = -1
        elif cur < 0 and not np.isnan(prev_lo[i]) and cprev[i] > prev_lo[i]:
            cur = 0
        hold[i] = cur
    test("X2 breakdown prior-low", signed_fills(D, hold, halt=1300))
    # X3 fast exits
    sig = np.where(short_vote, -1, 0).astype(np.int8)
    for hb in (30, 60):
        test(f"X3 fast-exit {hb} bars", timed_fills(D, sig, hb))
    # X4 gap fade
    for k in (0.5, 1.0):
        gap = (~np.isnan(prev_hi)) & (open_now > prev_hi + k * atr)
        cur = np.zeros(n, np.int8); st = 0
        for i in range(n):
            if D["fb"][i]:
                st = -1 if gap[i] else 0
            elif st < 0 and not np.isnan(prev_hi[i]) and cprev[i] <= prev_hi[i]:
                st = 0
            cur[i] = st
        test(f"X4 gap-fade k={k}", signed_fills(D, cur, halt=1300))
    # X5 drift-aware control
    arr = np.where(short_vote & (tiltbar < 0), -1, 0).astype(np.int8)
    test("X5 drift-aware (control)", signed_fills(D, arr, halt=1300))
    # plain mirror, for the record
    test("X0 plain mirror (W23)", signed_fills(D, np.where(short_vote, -1, 0).astype(np.int8),
                                               halt=1300))

    P("\nfalsifier: if nothing is ADOPTed, shorts on NQ in this regime are a hit-rate")
    P("diversifier rather than a source of edge, and belong sized as insurance.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
