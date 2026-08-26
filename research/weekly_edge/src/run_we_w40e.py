"""WE_W40 amendment 4: the decisive cell of the preregistered promotion condition.

Amendment 3 found the regime split is monotone and mechanistically sensible:
  B loses in the bottom half of the volatility regime (-$3.0 and -$4.0 per trade) and earns in
  the top half (+$45.8 and +$39.5), where 109 % of its money is.
The preregistered promotion condition asks a narrower question that amendment 3 did not
compute: is the PROFITABLE BAND profitable in BOTH 2022-2024 and 2025-2026 - and does it hold
on the 16 years of deep history the campaign has never used?

Also settles the H1 ambiguity honestly: amendment 3 counted 8/16 positive deep-history years
on NET weekly P&L, which literally meets the promotion threshold. Under the campaign's
standing stress-net requirement ($14.36/RT) the count is different and that is the binding
number. Both are reported here, per period AND per band, with no parameter selected.
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
from run_we_w01 import ROOT, PV, STRESS_RT, COMM_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w40 import OUT, axis_volexp                                  # noqa: E402
from we_quality import build_context                                     # noqa: E402

CUTS = None            # set from the modern window, then applied unchanged to deep history


def regime_rel(D):
    """Causal: trailing-20-session mean TR over trailing-250-session, known at session start."""
    n = D["n"]
    h, l, c = D["h"], D["l"], D["c"]
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    st = np.array([tr[D["sid"] == s].mean() for s in range(D["n_sess"])])
    a = pd.Series(st).rolling(20, min_periods=10).mean().shift(1).values
    b = pd.Series(st).rolling(250, min_periods=60).mean().shift(1).values
    return np.nan_to_num(a / np.maximum(b, 1e-9), nan=1.0)[D["sid"]]


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "second_e.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)
    rows = []

    def load_and_trade(a, b, tag):
        D = load_deep(a, b)
        X = build_context(D)
        BT = sfills(D, axis_volexp(D, X, 1.6, 1.0, 15), halt=1300.0, target=1000.0)
        rel = regime_rel(D)
        n, tarr = D["n"], D["t"]
        ent = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                        for x in BT])
        return (D, BT, rel[ent], np.array([x["pnl"] for x in BT]),
                np.array([np.datetime64(x["et"]) for x in BT]), tag)

    P_("=== the decisive cell: is the PROFITABLE REGIME BAND profitable in every period? ===")
    P_("   band cuts are the modern-window quartiles, applied UNCHANGED to deep history")
    Dm, BTm, relm, pnlm, etm, _ = load_and_trade("2022-01-01", "2026-07-31 17:00", "modern")
    cuts = np.quantile(relm[relm > 0], [0.25, 0.5, 0.75])
    P_(f"   cuts = {cuts.round(3)}  (Q3+Q4 = rel >= {cuts[1]:.3f})")
    Dd, BTd, reld, pnld, etd, _ = load_and_trade("2006-01-05", "2021-12-31 17:00", "deep")
    print(f"loaded both [{_time.time()-t0:.0f}s]", flush=True)

    def cell(nm, rel, pnl, et, a, b):
        m = (et >= np.datetime64(a)) & (et < np.datetime64(b))
        if m.sum() < 30:
            return
        hi = m & (rel >= cuts[1])
        lo = m & (rel < cuts[1])
        for lab, mm in (("HIGH-vol band", hi), ("LOW-vol band ", lo)):
            if mm.sum() < 20:
                continue
            net = pnl[mm].sum()
            stress = net - (STRESS_RT - COMM_RT) * mm.sum()
            P_(f"{nm:<18}{lab:<16}{int(mm.sum()):>7}{pnl[mm].mean():>10.1f}"
               f"{net:>12,.0f}{stress:>12,.0f}  {'OK' if stress > 0 else 'negative'}")
            rows.append(dict(period=nm, band=lab.strip(), n=int(mm.sum()),
                             per_trade=round(float(pnl[mm].mean()), 1), net=round(float(net)),
                             stress_net=round(float(stress))))

    P_(f"\n{'period':<18}{'band':<16}{'n':>7}{'$/tr':>10}{'net$':>12}{'stress$':>12}")
    cell("2022-2024", relm, pnlm, etm, "2022-01-01", "2025-01-01")
    cell("2025-2026", relm, pnlm, etm, "2025-01-01", "2026-08-01")
    P_("")
    for a, b in (("2006-01-01", "2011-01-01"), ("2011-01-01", "2016-01-01"),
                 ("2016-01-01", "2019-01-01"), ("2019-01-01", "2022-01-01")):
        cell(f"{a[:4]}-{b[:4]}", reld, pnld, etd, a, b)

    P_(f"\n=== H1 settled honestly: deep-history years, NET vs STRESS-NET "
       f"[{_time.time()-t0:.0f}s] ===")
    yrs = sorted({int(str(x)[:4]) for x in etd})
    npos = spos = 0
    for y in yrs:
        m = (etd >= np.datetime64(f"{y}-01-01")) & (etd < np.datetime64(f"{y+1}-01-01"))
        if m.sum() < 50:
            continue
        net = pnld[m].sum()
        st = net - (STRESS_RT - COMM_RT) * m.sum()
        npos += net > 0; spos += st > 0
    P_(f"   positive on NET        : {npos}/{len(yrs)}  "
       f"(the preregistered threshold was >= 8 of 16 -> "
       f"{'MET literally' if npos >= 8 else 'NOT met'})")
    P_(f"   positive on STRESS-NET : {spos}/{len(yrs)}  "
       f"(the campaign's standing requirement; this is the binding number)")

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "b_cells.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
