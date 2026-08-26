"""WE_W40 amendment 3: is axis B a regime effect or a recency effect?

Amendment 2 found B alone is NEGATIVE in 2022, 2023 and 2024 and positive only in 2025-2026.
Amendment 1's adoption was measured on 2023-07 -> 2026-08, which overweights the good years.
Two cheap diagnostics decide what B actually is:
  H1 DEEP HISTORY - run the identical engine on 2006-2021, never touched by this campaign.
     If B earns in several earlier years, the 2022-2024 gap is a REGIME gap and B is a
     regime-conditional engine. If it is flat/negative for 16 years too, B is recency.
  H2 REGIME CONDITIONING - split B's trades by a CAUSAL volatility-regime variable (trailing
     20-session ATR relative to the trailing 250-session level, known at the session's start).
     If B's edge lives in one regime, it can be gated on an observable rather than run always.
No parameters are selected here; B stays at its preregistered 1.6/1.0/15.
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
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w40 import OUT, A, B, axis_volexp                            # noqa: E402
from we_quality import build_context                                     # noqa: E402


def run_window(a, b, tag, P_):
    D = load_deep(a, b)
    X = build_context(D)
    n, tarr = D["n"], D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
        return wkmap[int(D["sid"][i])]
    BT = sfills(D, axis_volexp(D, X, 1.6, 1.0, 15), halt=1300.0, target=1000.0)
    years = sorted({int(str(x["et"])[:4]) for x in BT})
    P_(f"\n--- {tag}: {D['n']:,} bars, {D['n_sess']:,} sessions, "
       f"{len(BT)} B trades ---")
    P_(f"{'year':<10}{'wks':>5}{'n':>7}{'$/tr':>9}{'wk$':>9}{'wk+%':>7}{'worst':>10}"
       f"{'shrp':>8}{'stress':>9}")
    rows = []
    for y in years:
        ya = np.datetime64(f"{y}-01-01"); yb = np.datetime64(f"{y+1}-01-01")
        d = weekly(BT, wk_of, ya, yb)
        if len(d) < 8:
            continue
        v = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in BT if ya <= np.datetime64(x["et"]) < yb])
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        st = float(v.mean() - STRESS_RT * len(p) / len(v))
        P_(f"{y:<10}{len(v):>5}{len(p):>7}{p.mean():>9.1f}{v.mean():>9,.0f}"
           f"{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}{s:>8.3f}{st:>9,.0f}")
        rows.append(dict(window=tag, year=y, weeks=len(v), n=len(p),
                         per_trade=round(float(p.mean()), 1), wk=round(float(v.mean())),
                         wkpos=round(float((v > 0).mean() * 100), 1),
                         worst=round(float(v.min())), sharpe=round(s, 3), stress=round(st)))
    pos = sum(1 for r in rows if r["wk"] > 0)
    P_(f"   positive years {pos}/{len(rows)}")
    return rows, D, X, BT, wk_of


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "second_d.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    P_("=== H1 DEEP HISTORY: the identical B engine on data this campaign has never used ===")
    rows_deep, _, _, _, _ = run_window("2006-01-05", "2021-12-31 17:00", "2006-2021", P_)
    print(f"deep done [{_time.time()-t0:.0f}s]", flush=True)

    P_("\n=== modern window, same table for comparison ===")
    rows_mod, D, X, BT, wk_of = run_window("2022-01-01", "2026-07-31 17:00", "2022-2026", P_)

    # ---- H2 regime conditioning -----------------------------------------------------
    P_(f"\n=== H2 REGIME CONDITIONING (causal: trailing-20-session ATR / trailing-250) "
       f"[{_time.time()-t0:.0f}s] ===")
    n, tarr = D["n"], D["t"]
    h, l, c = D["h"], D["l"], D["c"]
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    idx = np.arange(n)
    sess_tr = np.array([tr[D["sid"] == s].mean() for s in range(D["n_sess"])])
    short = pd.Series(sess_tr).rolling(20, min_periods=10).mean().shift(1).values
    long_ = pd.Series(sess_tr).rolling(250, min_periods=60).mean().shift(1).values
    rel = np.nan_to_num(short / np.maximum(long_, 1e-9), nan=1.0)
    rel_bar = rel[D["sid"]]
    ent = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                    for x in BT])
    pnl = np.array([x["pnl"] for x in BT])
    r = rel_bar[ent]
    qs = np.quantile(r[r > 0], [0.25, 0.5, 0.75])
    P_(f"   regime variable quartile cuts: {qs.round(3)}")
    P_(f"{'regime':<28}{'n':>7}{'$/tr':>9}{'total$':>12}{'share%':>9}")
    tot = pnl.sum()
    bands = [("Q1 calmest  rel<%.2f" % qs[0], r < qs[0]),
             ("Q2          rel<%.2f" % qs[1], (r >= qs[0]) & (r < qs[1])),
             ("Q3          rel<%.2f" % qs[2], (r >= qs[1]) & (r < qs[2])),
             ("Q4 most expanded", r >= qs[2])]
    reg = []
    for nm, m in bands:
        if m.sum() == 0:
            continue
        P_(f"{nm:<28}{int(m.sum()):>7}{pnl[m].mean():>9.1f}{pnl[m].sum():>12,.0f}"
           f"{100*pnl[m].sum()/tot if tot else 0:>9.1f}")
        reg.append(dict(band=nm, n=int(m.sum()), per_trade=round(float(pnl[m].mean()), 1),
                        total=round(float(pnl[m].sum()))))
    P_("\n   and the same split BY YEAR-HALF, to separate regime from recency:")
    P_(f"{'period':<28}{'n':>7}{'$/tr':>9}{'meanRel':>10}")
    ets = np.array([np.datetime64(x["et"]) for x in BT])
    for y in range(2022, 2027):
        for half, (m0, m1) in (("H1", (1, 7)), ("H2", (7, 13))):
            a = np.datetime64(f"{y}-{m0:02d}-01")
            b_ = np.datetime64(f"{y+1}-01-01") if m1 == 13 else np.datetime64(f"{y}-{m1:02d}-01")
            m = (ets >= a) & (ets < b_)
            if m.sum() < 20:
                continue
            P_(f"{f'{y}{half}':<28}{int(m.sum()):>7}{pnl[m].mean():>9.1f}"
               f"{r[m].mean():>10.3f}")
    pd.DataFrame(rows_deep + rows_mod).to_csv(os.path.join(OUT, "b_years.csv"), index=False)
    pd.DataFrame(reg).to_csv(os.path.join(OUT, "b_regime.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
