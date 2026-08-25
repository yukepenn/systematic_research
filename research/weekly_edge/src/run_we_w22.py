"""WE_W22 TAIL (spec preregistered): attack the only open weakness of the audited object."""
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
from run_we_w21 import build_paths                                       # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W22_TAIL", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def fills_sized_halt(D, size_arr, halt=None):
    """Next-open fills from a per-bar desired SIZE (>=0, long-only), with an optional
    session-level realized-P&L halt on this sleeve."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; halted = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; halted = False
        want = int(size_arr[i - 1]) if i > 0 and not fb[i] else 0
        if halted:
            want = 0
        if want != u:
            if u > 0:
                pnl = u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if halt is not None and spnl <= -halt:
                    halted = True; want = 0
            u = want
            if u > 0:
                epx, eti = o[i], i
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
    return trades


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    paths = build_paths(D)
    keys = list(paths)
    M = np.vstack([paths[k] for k in keys])
    frac = M.mean(axis=0)
    print(f"paths ready [{_time.time()-t0:.0f}s]", flush=True)
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), D["n"] - 1))
        return wkmap[int(D["sid"][i])]

    # sleeves for combination
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    asia_m = (mod >= 1080) | (mod <= 179)
    asia_size = ((frac >= 0.5) & asia_m).astype(np.int8)
    asia = fills_sized_halt(D, asia_size)

    out = open(os.path.join(OUT, "tail.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def rep(nm, d, note=""):
        s, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        P(f"{nm:<34}{len(v):>7}{net:>12,.0f}{v.mean():>9,.0f}{pos:>8.1f}{v.min():>10,.0f}"
          f"{s:>8.3f}  {note}")
        rows.append(dict(name=nm, weeks=len(v), net=round(net), wk_mean=round(v.mean()),
                         pos=round(pos, 1), worst=round(v.min()), sharpe=round(s, 3)))
        return s, v.min()

    P(f"{'variant':<34}{'weeks':>7}{'net':>12}{'wkMean':>9}{'pos%':>8}{'worst':>10}"
      f"{'sharpe':>8}")
    base_size = (frac >= 0.5).astype(np.int8)
    e5 = fills_sized_halt(D, base_size)
    d5 = weekly(e5, wk_of, A, B)
    s5, w5 = rep("E5 base (vote>=0.5, 1 contract)", d5)
    d1 = weekly(s1, wk_of, A, B)
    rep("S1 alone", d1)
    dc = {w: d5.get(w, 0.0) + d1.get(w, 0.0) for w in set(d5) | set(d1)}
    sc, wc = rep("E5+S1 (reference, <=2)", dc)

    P("\n--- V1 THRESHOLD CURVE (reported whole; no selection) ---")
    for th in (0.30, 0.40, 0.50, 0.60, 0.70, 0.80):
        trl = fills_sized_halt(D, (frac >= th).astype(np.int8))
        rep(f"V1 vote>={th:.2f}", weekly(trl, wk_of, A, B))

    P("\n--- V2 CONVICTION SIZE (1 in [0.5,0.75), 2 at >=0.75; max 2) ---")
    sz = np.where(frac >= 0.75, 2, np.where(frac >= 0.5, 1, 0)).astype(np.int8)
    rep("V2 conviction 1/2", weekly(fills_sized_halt(D, sz), wk_of, A, B))

    P("\n--- V3 THREE SLEEVES (E5+S1+ASIA, max 3) ---")
    da = weekly(asia, wk_of, A, B)
    d3 = {w: dc.get(w, 0.0) + da.get(w, 0.0) for w in set(dc) | set(da)}
    rep("V3 E5+S1+ASIA", d3)

    P("\n--- V4 SESSION HALT ON THE VOTE ---")
    for H in (1300, 2600):
        trl = fills_sized_halt(D, base_size, halt=H)
        dh = weekly(trl, wk_of, A, B)
        rep(f"V4 E5 halt {H}", dh)
        dch = {w: dh.get(w, 0.0) + d1.get(w, 0.0) for w in set(dh) | set(d1)}
        rep(f"V4 E5halt{H}+S1", dch)

    P("\n--- V5 CONCENTRATION CAP (E5+S1 same-direction, cap 2) ---")
    P("   (E5 is long-only 1 contract and S1 is +-1, so the pair already caps at 2 long;")
    P("    the cap therefore binds only when both are long, which is the reference case.)")
    P("   -> V5 is a no-op on this pair and is reported as such rather than fabricated.")

    P("\n=== ADOPTION RULE: worst week better by >=15% WITHOUT reducing Sharpe ===")
    for r in rows:
        if r["name"].startswith(("V1", "V2", "V3", "V4")):
            ref_s, ref_w = (sc, wc) if "+S1" in r["name"] or "ASIA" in r["name"] else (s5, w5)
            better_tail = r["worst"] >= ref_w * 0.85
            keeps_sharpe = r["sharpe"] >= ref_s
            if better_tail and keeps_sharpe:
                P(f"  ADOPT   {r['name']}  (worst {r['worst']:,} vs ref {ref_w:,.0f}; "
                  f"sharpe {r['sharpe']} vs {ref_s:.3f})")
    P("  (nothing printed above = falsifier fired: the tail is the price of the edge)")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
