"""WE_W40 amendment 2: full-window and per-year confirmation of the adopted pair.

Amendment 1 measured everything on the walk-forward-comparable window (2023-07 -> 2026-08),
which is the STRONGER half for the long object (16.91 vs 14.72 pts/session full-window).
Before the pair is written into the state documents it must be re-measured on the full window
and year by year, so the headline is not quoted off a favourable slice.
No parameters are chosen here; B stays at its preregistered 1.6/1.0/15.
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
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w40 import OUT, A, WF0, B, axis_volexp                       # noqa: E402
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
    out = open(os.path.join(OUT, "second_c.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    LONG = fills_qexit(D, posL, szQ0, scQ0)
    BT = sfills(D, axis_volexp(D, X, 1.6, 1.0, 15), halt=1300.0, target=1000.0)

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))

    def stats(nm, parts, a, b):
        """parts = [(trades, multiplier)]"""
        keys = sorted(set(k for trl, _ in parts for k in weekly(trl, wk_of, a, b)))
        if len(keys) < 8:
            return None
        v = np.zeros(len(keys)); ntr = 0.0
        for trl, k in parts:
            d = weekly(trl, wk_of, a, b)
            v += np.array([d.get(x, 0.0) for x in keys]) * k
            ntr += k * len([x for x in trl if a <= np.datetime64(x["et"]) < b])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * ntr / len(v))
        P_(f"{nm:<30}{len(keys):>5}{v.mean():>10,.0f}{(v>0).mean()*100:>7.1f}"
           f"{v.min():>10,.0f}{cv:>10,.0f}{s:>8.3f}{eff:>8.3f}{cve:>8.3f}{st:>10,.0f}")
        return dict(arm=nm, weeks=len(keys), wk=round(float(v.mean())),
                    wkpos=round(float((v > 0).mean() * 100), 1), worst=round(float(v.min())),
                    cvar5=round(cv), sharpe=round(s, 3), eff=round(eff, 3),
                    cveff=round(cve, 3), stress=round(st))

    hdr = (f"{'arm':<30}{'wks':>5}{'wk$':>10}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}"
           f"{'shrp':>8}{'eff':>8}{'cvEff':>8}{'stress':>10}")
    rows = []
    P_(f"=== FULL WINDOW 2022-07 -> 2026-08 (the campaign's own window) "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for nm, parts in (("LONG x1", [(LONG, 1.0)]),
                      ("B x1 alone", [(BT, 1.0)]),
                      ("6 long : 1 B", [(LONG, 6.0), (BT, 1.0)]),
                      ("4 long : 1 B", [(LONG, 4.0), (BT, 1.0)]),
                      ("3 long : 1 B", [(LONG, 3.0), (BT, 1.0)])):
        r = stats(nm, parts, A, B)
        if r:
            rows.append(r)
    P_("   exposure-matched long-alone comparators:")
    for k, tag in ((6.52, "6:1"), (4.52, "4:1"), (3.52, "3:1")):
        r = stats(f"long alone x{k:.2f} (={tag})", [(LONG, k)], A, B)
        if r:
            rows.append(r)

    P_(f"\n=== PER YEAR (6 long : 1 B vs exposure-matched long alone) "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for y in (2022, 2023, 2024, 2025, 2026):
        a = max(A, np.datetime64(f"{y}-01-01"))
        b = min(B, np.datetime64(f"{y+1}-01-01"))
        if a >= b:
            continue
        r1 = stats(f"{y} 6:1 pair", [(LONG, 6.0), (BT, 1.0)], a, b)
        r2 = stats(f"{y} long alone x6.52", [(LONG, 6.52)], a, b)
        for r in (r1, r2):
            if r:
                rows.append(r)
        P_("")

    P_(f"=== B ALONE PER YEAR (is the second model stable?) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for y in (2022, 2023, 2024, 2025, 2026):
        a = max(A, np.datetime64(f"{y}-01-01"))
        b = min(B, np.datetime64(f"{y+1}-01-01"))
        if a >= b:
            continue
        r = stats(f"{y} B alone", [(BT, 1.0)], a, b)
        if r:
            rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_c.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
