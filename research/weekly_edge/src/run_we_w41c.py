"""WE_W41 amendment 2: the TRADEABLE form of the adopted clock basket.

Amendment 1 adopted `w = 0.03 each: long + 3-min + range` on continuous weights. Continuous
weights are not orders. At w = 0.03 of total contract-minutes, a clock sleeve is a fraction of
a contract, so the basket is only implementable once the base sleeve is large enough for that
fraction to round to one contract. This run states the exposures, converts them to INTEGER
CONTRACT RATIOS, and finds the SMALLEST base size at which the improvement still holds - which
is the number the owner actually needs.
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
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w41 import OUT, A, B                                         # noqa: E402
from we_quality import build_context                                     # noqa: E402


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]
    out = open(os.path.join(OUT, "clock2_c.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    LONG = fills_qexit(D, posL, np.where(scQ0 >= 3, 2, 1).astype(np.int8), scQ0)
    SL = {}
    for nm in ("3-min", "range", "volume"):
        f = os.path.join(OUT, f"pos_{nm}.npy")
        if not os.path.exists(f):
            P_(f"missing {f} - run run_we_w41b.py first"); out.close(); return
        SL[nm] = fills_daily(D, np.load(f), halt=1300, target=1000)

    keys = sorted(weekly(LONG, wk_of, A, B))

    def wv(trl, k=1.0):
        d = weekly(trl, wk_of, A, B)
        return np.array([d.get(x, 0.0) for x in keys]) * k

    def ntr(trl, k=1.0):
        return k * len([x for x in trl if A <= np.datetime64(x["et"]) < B])

    def expo(trl, k=1.0):
        return k * float(sum(x.get("u", 1)
                             * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                / np.timedelta64(1, "m"))
                             for x in trl if A <= np.datetime64(x["et"]) < B))
    eL = expo(LONG)
    P_(f"=== EXPOSURES (contract-minutes over 2022-07 -> 2026-08) [{_time.time()-t0:.0f}s] ===")
    P_(f"   long quality object   {eL:>12,.0f}   (avg {eL/(60*len(keys)):.2f} contracts held "
       f"per hour of the week)")
    for nm in SL:
        e = expo(SL[nm])
        P_(f"   {nm:<20}  {e:>12,.0f}   -> w=0.03 of total needs "
           f"{0.03*eL/e:.3f} contracts, i.e. the long sleeve at "
           f"{1/(0.03*eL/e):.0f}x for the clock sleeve to be ONE contract")

    rows = []
    hdr = (f"{'arm':<40}{'wk$':>10}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
           f"{'eff':>8}{'cvEff':>8}{'stress':>10}")

    def show(nm, v, nt):
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * nt / len(v))
        P_(f"{nm:<40}{v.mean():>10,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
           f"{cv:>10,.0f}{s:>8.3f}{eff:>8.3f}{cve:>8.3f}{st:>10,.0f}")
        rows.append(dict(arm=nm, wk=round(float(v.mean())), worst=round(float(v.min())),
                         cvar5=round(cv), sharpe=round(s, 3), eff=round(eff, 3),
                         cveff=round(cve, 3), stress=round(st)))
        return eff, cve

    P_(f"\n=== INTEGER CONTRACT RATIOS  (long : 3-min : range), each vs long alone at the "
       f"SAME contract-minutes ===")
    P_(hdr)
    for a_ in (48, 32, 24, 16, 12, 8, 6, 4, 2, 1):
        v = wv(LONG, a_) + wv(SL["3-min"]) + wv(SL["range"])
        nt = ntr(LONG, a_) + ntr(SL["3-min"]) + ntr(SL["range"])
        e_tot = expo(LONG, a_) + expo(SL["3-min"]) + expo(SL["range"])
        k = e_tot / eL
        eb, cb = show(f"{a_} long : 1 3-min : 1 range", v, nt)
        ea, ca = show(f"   long alone x{k:.2f} (matched)", wv(LONG, k), ntr(LONG, k))
        P_(f"   -> {'BOTH improve' if (eb > ea and cb > ca) else ('eff only' if eb > ea else ('CVaR only' if cb > ca else 'neither'))}"
           f"   (eff {eb:.3f} vs {ea:.3f} | cvEff {cb:.3f} vs {ca:.3f})\n")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_c.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
