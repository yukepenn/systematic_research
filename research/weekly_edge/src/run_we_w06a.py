"""WE_W06 phase 1 (spec preregistered): trend-capture accounting.

Pure measurement — no new strategy. Per session: available perfect-foresight move, captured
points per sleeve, and mutually-exclusive leakage attribution.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, load, sm14_1m                   # noqa: E402
from run_we_w03 import fills, cd_signals                                  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                     # noqa: E402
import inverse_core as IC                                                 # noqa: E402
from run_r13_strict_master import run_master                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W06_TRENDCAP", "out")
os.makedirs(OUT, exist_ok=True)


def available_move(c, lo, hi):
    """Perfect-foresight single trade inside [lo,hi): best long and best short, signed."""
    seg = c[lo:hi]
    if len(seg) < 2:
        return 0.0, 0, 0, 0
    # best long: max(c[j]-c[i]) i<j
    run_min = np.minimum.accumulate(seg)
    gain_l = seg - run_min
    jl = int(np.argmax(gain_l)); best_l = float(gain_l[jl])
    il = int(np.argmin(seg[:jl + 1]))
    run_max = np.maximum.accumulate(seg)
    gain_s = run_max - seg
    js = int(np.argmax(gain_s)); best_s = float(gain_s[js])
    is_ = int(np.argmax(seg[:js + 1]))
    if best_l >= best_s:
        return best_l, 1, lo + il, lo + jl
    return best_s, -1, lo + is_, lo + js


def main():
    t0 = _time.time()
    D = load()
    c = D["c"]
    n_sess = D["n_sess"]
    starts = np.zeros(n_sess, np.int64); ends = np.zeros(n_sess, np.int64)
    idx = np.arange(D["n"])
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        starts[s], ends[s] = m[0], m[-1] + 1
    print(f"sessions {n_sess} [{_time.time()-t0:.0f}s]", flush=True)

    avail = np.zeros(n_sess); adir = np.zeros(n_sess, np.int8)
    astart = np.zeros(n_sess, np.int64); aend = np.zeros(n_sess, np.int64)
    for s in range(n_sess):
        avail[s], adir[s], astart[s], aend[s] = available_move(c, starts[s], ends[s])
    print(f"available computed; mean {avail.mean():.1f} pts/session "
          f"[{_time.time()-t0:.0f}s]", flush=True)

    def lag(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL, aS = lag(cd_arr >= 0), lag(cd_arr <= 0)

    bb = IC.prepare(D["df"], SolarWaveParams())
    tr1 = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)
    sleeves = {"S1": [dict(d=x["d"], pnl=x["pnl"], ei=x["ei"], xi=x["xi"]) for x in tr1]}

    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    tga = sm14_1m(D, 460, return_targets=True)
    tarr = D["t"]

    def idxof(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), D["n"] - 1))

    for nm, tg, hlt in (("S4n.gdl", tgn, None), ("S4a.h1300.gdl", tga, 1300)):
        trl = fills(D, tg, halt=hlt, allow_long=aL, allow_short=aS)
        sleeves[nm] = [dict(d=x["d"], pnl=x["pnl"], ei=idxof(x["et"]), xi=idxof(x["xt"]))
                       for x in trl]
    print(f"sleeves ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "capture.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    P(f"AVAILABLE (perfect-foresight single trade per session): "
      f"mean {avail.mean():.1f} pts  median {np.median(avail):.1f}  "
      f"= ${avail.mean()*PV:,.0f}/session at 1 NQ\n")

    rows = []
    for nm, trs in sleeves.items():
        bysess = {}
        for x in trs:
            s = int(D["sid"][x["ei"]])
            bysess.setdefault(s, []).append(x)
        cap = np.zeros(n_sess); L = {k: 0 for k in ("L1", "L2", "L3", "L4", "L5")}
        late = []; early = []
        for s in range(n_sess):
            xs = bysess.get(s)
            if not xs:
                L["L1"] += 1
                continue
            pts = sum(x["pnl"] for x in xs) / PV
            cap[s] = pts
            netd = np.sign(sum(x["d"] for x in xs))
            if netd != 0 and adir[s] != 0 and netd != adir[s]:
                L["L2"] += 1
                continue
            if pts < 0:
                L["L5"] += 1
                continue
            e0 = min(x["ei"] for x in xs); x1 = max(x["xi"] for x in xs)
            dl, de = e0 - astart[s], aend[s] - x1
            late.append(dl); early.append(de)
            if dl > de:
                L["L3"] += 1
            else:
                L["L4"] += 1
        ratio = cap.sum() / avail.sum()
        tps = len(trs) / n_sess
        P(f"{nm:<16} captured {cap.sum():>10,.0f} pts of {avail.sum():>11,.0f} "
          f"= {100*ratio:>5.2f}%   trades/session {tps:>5.2f}   "
          f"pts/session {cap.mean():>6.2f}")
        P(f"{'':<16} L1 no-trade {100*L['L1']/n_sess:>5.1f}%  "
          f"L2 wrong-side {100*L['L2']/n_sess:>5.1f}%  "
          f"L3 late {100*L['L3']/n_sess:>5.1f}%  "
          f"L4 early-exit {100*L['L4']/n_sess:>5.1f}%  "
          f"L5 chop-loss {100*L['L5']/n_sess:>5.1f}%")
        if late:
            P(f"{'':<16} when traded well: entered {np.median(late):.0f} bars after the "
              f"move's start, exited {np.median(early):.0f} bars before its end (medians)\n")
        rows.append(dict(sleeve=nm, captured_pts=round(cap.sum()), avail_pts=round(avail.sum()),
                         ratio_pct=round(100 * ratio, 2), trades_per_session=round(tps, 2),
                         **{k: round(100 * v / n_sess, 1) for k, v in L.items()}))

    # reference: his trade rate
    P("REFERENCE: his 21 comparable 2026 weeks = 1,752 trades / ~105 sessions "
      "= ~16.7 trades/session at $103/trade gross (R34 am.2).")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
