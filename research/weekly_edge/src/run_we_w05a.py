"""WE_W05A EXPLAIN (spec preregistered): diagnostics only — where does the money come from?"""
from __future__ import annotations

import csv
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, COMM_RT, load, week_table, sm14_1m           # noqa: E402
from run_we_w02 import session_volfilter_mask                             # noqa: E402
from run_we_w03 import fills, cd_signals                                  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                     # noqa: E402
import inverse_core as IC                                                 # noqa: E402
from run_r13_strict_master import run_master                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W05A_EXPLAIN", "out")
os.makedirs(OUT, exist_ok=True)


def weekly_vec(per_s, D):
    rows = {}
    for s, (net, ntr) in per_s.items():
        w = D["wk"][s]
        r = rows.setdefault(w, 0.0)
        rows[w] = r + net
    return rows


def main():
    t0 = _time.time()
    D = load()
    out = open(os.path.join(OUT, "explain.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True)
        print(*a, file=out)

    def lag(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL, aS = lag(cd_arr >= 0), lag(cd_arr <= 0)

    bb = IC.prepare(D["df"], SolarWaveParams())
    trades = {}
    tr1 = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)
    trades["S1"] = [dict(d=x["d"], pnl=x["pnl"], xt=str(bb["t"][x["xi"]])) for x in tr1]
    tg_n = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    tg_a = sm14_1m(D, 460, return_targets=True)
    trades["S4n.gdl"] = fills(D, tg_n, allow_long=aL, allow_short=aS)
    trades["S4n.gdl.h1300"] = fills(D, tg_n, halt=1300, allow_long=aL, allow_short=aS)
    trades["S4n.gnone"] = fills(D, tg_n)
    trades["S4a.h1300.gdl"] = fills(D, tg_a, halt=1300, allow_long=aL, allow_short=aS)
    hot = session_volfilter_mask(D)
    tg5 = sm14_1m(D, 460, with_solar=False, with_bmom=True, return_targets=True)
    trades["S5.vf"] = fills(D, tg5, allow_long=~hot, allow_short=~hot)
    P(f"engines done [{_time.time()-t0:.0f}s]")

    wt = {k: week_table(v, D, lambda x: x["xt"]) for k, v in trades.items()}
    wv = {k: weekly_vec(v, D) for k, v in wt.items()}
    port = {}
    for w in set(wv["S1"]) | set(wv["S4n.gdl"]):
        port[w] = wv["S1"].get(w, 0.0) + wv["S4n.gdl"].get(w, 0.0)
    wv["PORT"] = port

    # R1 yearly
    P("\n== R1 YEARLY (net / %pos weeks), net of $4.36/RT ==")
    for k in ("S1", "S4n.gdl", "S4a.h1300.gdl", "PORT", "S5.vf"):
        line = f"{k:<16}"
        for yr in ("2022", "2023", "2024", "2025", "2026"):
            xs = [v for w, v in wv[k].items() if w.startswith(yr)]
            if xs:
                line += f" {yr}: {sum(xs):>+9,.0f} ({100*np.mean([x>0 for x in xs]):.0f}%)"
        P(line)

    # R2 monthly
    P("\n== R2 MONTHLY (pooled 2022-2026/07) ==")
    sess_month = pd.to_datetime(D["sess_date"]).astype(str).str[:7]
    for k in ("S1", "S4n.gdl", "PORT"):
        mm = {}
        if k == "PORT":
            per_s = {}
            for kk in ("S1", "S4n.gdl"):
                for s, (net, ntr) in wt[kk].items():
                    per_s[s] = per_s.get(s, 0.0) + net
        else:
            per_s = {s: net for s, (net, _) in wt[k].items()}
        for s, net in per_s.items():
            m = sess_month[s]
            mm[m] = mm.get(m, 0.0) + net
        v = np.array(list(mm.values()))
        P(f"{k:<16} months {len(v)}  pos {100*(v>0).mean():.0f}%  "
          f"mean {v.mean():+,.0f}  worst {v.min():+,.0f}  best {v.max():+,.0f}")

    # R3 complementarity
    P("\n== R3 WEEKLY-NET CORRELATIONS ==")
    keys = ["S1", "S4n.gdl", "S4a.h1300.gdl", "S5.vf"]
    allw = sorted(set().union(*[set(wv[k]) for k in keys]))
    M = np.array([[wv[k].get(w, 0.0) for w in allw] for k in keys])
    C = np.corrcoef(M)
    P("            " + "".join(f"{k:>15}" for k in keys))
    for i, k in enumerate(keys):
        P(f"{k:<12}" + "".join(f"{C[i, j]:>15.2f}" for j in range(len(keys))))

    # R4 vs him
    tg_all = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")))
    sheets = list(csv.DictReader(open(os.path.join(
        ROOT, "runs", "OTR_R34_METHODOLOGY_EQUALIZER", "out", "sheets.csv"))))
    his_weeks = []
    for r in sheets:
        ts = pd.Timestamp(next(x for x in tg_all if x["image_id"] == r["image_id"])["report_end"])
        iso = ts.isocalendar()
        his_weeks.append((f"{iso.year}-W{iso.week:02d}", float(r["HIS"])))
    P("\n== R4 vs HIS 21 displayed weeks (his GROSS+display vs our NET+frozen) ==")
    P(f"{'week':<10}{'HIS':>10}" + "".join(f"{k:>15}" for k in ("S4n.gdl", "PORT")))
    tot = {"HIS": 0.0, "S4n.gdl": 0.0, "PORT": 0.0}
    for w, hv in his_weeks:
        a, b = wv["S4n.gdl"].get(w, 0.0), wv["PORT"].get(w, 0.0)
        tot["HIS"] += hv; tot["S4n.gdl"] += a; tot["PORT"] += b
        P(f"{w:<10}{hv:>10,.0f}{a:>15,.0f}{b:>15,.0f}")
    P(f"{'TOTAL':<10}{tot['HIS']:>10,.0f}{tot['S4n.gdl']:>15,.0f}{tot['PORT']:>15,.0f}")
    for k in ("S4n.gdl", "PORT"):
        xs = [wv[k].get(w, 0.0) for w, _ in his_weeks]
        P(f"{k}: pos {sum(1 for x in xs if x > 0)}/21  worst {min(xs):+,.0f}")

    # R5 explainability of the lead candidate
    P("\n== R5 EXPLAIN S4n.gdl ==")
    for k in ("S4n.gnone", "S4n.gdl"):
        p = np.array([x["pnl"] for x in trades[k]])
        d = np.array([x["d"] for x in trades[k]])
        P(f"{k:<12} n={len(p):>6}  net {p.sum():>+11,.0f}  $/tr {p.mean():>+7.1f}  "
          f"long {p[d > 0].sum():>+11,.0f} ({(d > 0).sum()})  "
          f"short {p[d < 0].sum():>+11,.0f} ({(d < 0).sum()})")
    pg = np.array([x["pnl"] for x in trades["S4n.gdl"]])
    pn = np.array([x["pnl"] for x in trades["S4n.gnone"]])
    P(f"gate marginal: net {pg.sum()-pn.sum():+,.0f}, trades {len(pg)-len(pn):+}, "
      f"$/tr {pg.mean()-pn.mean():+.1f}")
    out.close()
    print(f"\ndone [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
