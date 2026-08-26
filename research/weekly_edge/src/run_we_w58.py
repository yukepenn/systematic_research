"""WE_W58 - reopen every candidate under the corrected criterion, and attack the number the
owner actually cares about.

The corrected criterion (OWNER_CHARTER_AMENDMENT_2): recent effectiveness is MANDATORY, old-era
weakness is not disqualifying, a regime explanation is attribution and not a gate. The objective
is CONSISTENCY plus small drawdown; Sharpe decides nothing.

"It works in the last two years" is trivially satisfiable, so this wave does not evaluate ONE
window. It evaluates EVERY rolling 24-month window and asks whether the latest is representative
or exceptional.

Runs off the series persisted in W56, so it costs no re-simulation.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W58_REOPEN", "out")
os.makedirs(OUT, exist_ok=True)
W56 = os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out")
BMOM_H = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w10_bmom_hist",
                      "w10bmom_daily.csv")
BMOM_D = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w8_bmom",
                      "w8bmom_w14_daily.csv")
BREADTH = os.path.join(ROOT, "research", "breadth_lab", "BREADTH01_TSMOM_REPLICATION",
                       "out", "book_daily_full.csv")
DD_TARGET = 20245.0
WGRID = np.round(np.arange(0.05, 0.61, 0.05), 3)


def streak(a):
    b = m = 0
    for z in a:
        b = b + 1 if z < 0 else 0
        m = max(m, b)
    return int(m)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "reopen.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    p1 = pd.read_csv(os.path.join(W56, "p1_daily.csv"), index_col=0, parse_dates=True).iloc[:, 0]
    ab = pd.read_csv(os.path.join(W56, "axisb_daily.csv"), index_col=0,
                     parse_dates=True).iloc[:, 0]
    bm = pd.concat([pd.read_csv(BMOM_H), pd.read_csv(BMOM_D)], ignore_index=True)
    bm["sess"] = pd.to_datetime(bm["sess"])
    bm = bm.set_index("sess")["net_c1_usd"].sort_index()
    br = pd.read_csv(BREADTH)
    br["date"] = pd.to_datetime(br["date"])
    br = br.set_index("date")["book_net"].sort_index()
    P_(f"=== B1: persisted series loaded | P1 {len(p1)} sessions net ${p1.sum():,.0f} "
       f"| axisB {len(ab)} net ${ab.sum():,.0f} | B-MOM {len(bm)} | BREADTH {len(br)}")

    lo, hi = pd.Timestamp("2022-07-01"), min(p1.index.max(), bm.index.max(), br.index.max())
    cal = pd.DatetimeIndex(sorted(set(p1.index) | set(ab.index) | set(bm.index)))
    cal = cal[(cal >= lo) & (cal <= hi)]
    Dd = pd.DataFrame(index=cal)
    Dd["P1"] = p1.reindex(cal).fillna(0.0)
    Dd["AXISB"] = ab.reindex(cal).fillna(0.0)
    Dd["BMOM"] = bm.reindex(cal).fillna(0.0)
    Dd["BREADTH"] = br.reindex(cal).fillna(0.0)
    # flags: did the sleeve actually trade that day (non-zero P&L is the only signal we have)
    FLAT = {k: (Dd[k] == 0).values for k in Dd.columns}
    iso = Dd.index.isocalendar()
    Dd["wk"] = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    P_(f"   common calendar {cal.min().date()} -> {cal.max().date()}, {len(cal)} sessions, "
       f"{Dd['wk'].nunique()} weeks")

    # =====================================================================================
    # PHASE 1 - ROLLING 24-MONTH RECORD
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 1: every rolling 24-month window, not just the latest one")
    P_(f"{'='*118}")
    P_("'It works in the last two years' is trivially satisfiable. The question that is not")
    P_("trivial is whether the LATEST window is representative of the sleeve's own history.\n")
    full = pd.concat([p1.rename("P1"), ab.rename("AXISB"), bm.rename("BMOM"),
                      br.rename("BREADTH")], axis=1)
    ends = pd.date_range(full.index.min() + pd.DateOffset(months=24),
                         full.index.max(), freq="ME")
    rows = []
    for k in ("P1", "AXISB", "BMOM", "BREADTH"):
        s = full[k].dropna()
        for e in ends:
            b = e - pd.DateOffset(months=24)
            w = s[(s.index > b) & (s.index <= e)]
            if len(w) < 200:
                continue
            se = w.std(ddof=1) / np.sqrt(len(w))
            rows.append(dict(sleeve=k, end=e.date(), n=len(w), net=float(w.sum()),
                             daily=float(w.mean()), t=float(w.mean() / se) if se > 0 else 0.0,
                             daypos=100 * float((w > 0).mean())))
    RW = pd.DataFrame(rows)
    RW.to_csv(os.path.join(OUT, "rolling24.csv"), index=False)
    P_(f"{'sleeve':<10}{'windows':>9}{'% positive':>12}{'median t':>10}"
       f"{'LATEST window: end':>22}{'net $':>12}{'t':>8}{'percentile of its own history':>32}")
    for k in ("P1", "AXISB", "BMOM", "BREADTH"):
        q = RW[RW["sleeve"] == k].sort_values("end")
        if not len(q):
            continue
        last = q.iloc[-1]
        pct = 100 * float((q["net"].values < last["net"]).mean())
        P_(f"{k:<10}{len(q):>9}{100*float((q['net'] > 0).mean()):>11.1f}%"
           f"{q['t'].median():>10.2f}{str(last['end']):>22}{last['net']:>12,.0f}"
           f"{last['t']:>8.2f}{pct:>31.0f}%")
    P_(f"\n   A sleeve positive in most rolling windows has a recent record that means")
    P_(f"   something. One positive only in the latest window does not.")

    # =====================================================================================
    # PHASE 2 - THE CONSISTENCY LEDGER
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 2: the consistency ledger - the owner's actual objective")
    P_(f"{'='*118}")
    v0 = Dd.groupby("wk")["P1"].sum().values
    s0 = Dd["P1"].values

    def report(dser, name):
        v = pd.Series(dser, index=Dd.index).groupby(Dd["wk"].values).sum().values
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        traded = dser != 0
        return dict(arm=name, daypos=100 * float((dser > 0).mean()),
                    trdpos=100 * float((dser[traded] > 0).mean()) if traded.any() else 0.0,
                    flat=100 * float((~traded).mean()),
                    wkpos=100 * float((v > 0).mean()),
                    dstreak=streak(dser), wstreak=streak(v),
                    medday=float(np.median(dser)) * k, medwk=float(np.median(v)) * k,
                    weekly=float(v.mean()) * k, dd_top5=dp["dd_mean_top5"] * k,
                    ulcer=dp["ulcer"] * k, worst=float(v.min()) * k, scale=k)
    HDR = (f"{'arm':<30}{'day+%':>7}{'trdD+%':>8}{'flat%':>7}{'wk+%':>7}{'dStrk':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'worst$':>9}")

    def show(r):
        P_(f"{r['arm']:<30}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['flat']:>7.1f}"
           f"{r['wkpos']:>7.1f}{r['dstreak']:>7}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['worst']:>9,.0f}")
    P_("All rows rescaled to the SAME $20,245 max drawdown, so weekly$ is comparable.\n")
    P_(HDR)
    base = report(s0, "P1 INCUMBENT")
    show(base)
    crows = [base]
    sd0 = pd.Series(s0, index=Dd.index).groupby(Dd["wk"].values).sum().std(ddof=1)
    for k in ("AXISB", "BMOM", "BREADTH"):
        sv = Dd[k].values
        sdk = pd.Series(sv, index=Dd.index).groupby(Dd["wk"].values).sum().std(ddof=1)
        if sdk <= 0:
            continue
        vn = sv * (sd0 / sdk)
        for w in WGRID:
            r = report((1 - w) * s0 + w * vn, f"P1 + {k} w={w:.2f}")
            r["sleeve"] = k; r["w"] = w
            crows.append(r)
        best_day = max([r for r in crows if r.get("sleeve") == k], key=lambda r: r["daypos"])
        best_wk = max([r for r in crows if r.get("sleeve") == k], key=lambda r: r["weekly"])
        show(best_day); show(best_wk)
    C = pd.DataFrame(crows)
    C.to_csv(os.path.join(OUT, "consistency.csv"), index=False)
    P_(f"\n   rows shown per sleeve: the weight that maximises POSITIVE-DAY RATE, then the")
    P_(f"   weight that maximises weekly dollars. Full grid in out/consistency.csv.")

    # ---- day-level overlap: does the sleeve trade when P1 is flat? ----------------------
    P_(f"\n=== the mechanism behind any positive-day gain: does the sleeve trade P1's FLAT days? ===")
    P_(f"{'sleeve':<12}{'both trade':>12}{'only sleeve':>13}{'only P1':>10}{'both flat':>11}"
       f"{'P1-flat days the sleeve wins':>32}")
    orows = []
    for k in ("AXISB", "BMOM", "BREADTH"):
        a, b_ = ~FLAT["P1"], ~FLAT[k]
        both = int((a & b_).sum()); only_s = int((~a & b_).sum())
        only_p = int((a & ~b_).sum()); none = int((~a & ~b_).sum())
        m = (~a) & b_
        winshare = 100 * float((Dd[k].values[m] > 0).mean()) if m.any() else 0.0
        P_(f"{k:<12}{both:>12}{only_s:>13}{only_p:>10}{none:>11}{winshare:>31.1f}%")
        orows.append(dict(sleeve=k, both=both, only_sleeve=only_s, only_p1=only_p,
                          both_flat=none, p1flat_winrate=winshare))
    pd.DataFrame(orows).to_csv(os.path.join(OUT, "dayoverlap.csv"), index=False)

    # =====================================================================================
    # PHASE 3 - RE-ADJUDICATION
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 3: re-adjudication under the corrected criterion")
    P_(f"{'='*118}")
    cut = hi - pd.DateOffset(months=24)
    P_(f"   trailing-24-month window: {cut.date()} -> {hi.date()}\n")
    P_(f"{'candidate':<12}{'sessions':>10}{'net $':>12}{'daily $':>10}{'SE':>9}{'t':>7}"
       f"{'day+%':>8}{'chronology gate':>18}{'remaining objection':>34}")
    obj = {"AXISB": "statistical: near-zero FULL-window expectancy (+$114/wk stress-net) and a "
                    "92nd-pct count-matched null",
           "BMOM": "IN-SAMPLE: 2022-2026 is its own development window",
           "BREADTH": "statistical: 4th percentile of its own null in W56"}
    for k in ("P1", "AXISB", "BMOM", "BREADTH"):
        s = full[k].dropna()
        w = s[(s.index > cut) & (s.index <= hi)]
        se = w.std(ddof=1) / np.sqrt(len(w)) if len(w) > 2 else np.nan
        t = w.mean() / se if se and se > 0 else 0.0
        gate = "PASS" if (w.mean() > 0 and t >= 1.0) else "FAIL"
        P_(f"{k:<12}{len(w):>10}{w.sum():>12,.4f}{w.mean():>10,.4f}{se:>9,.4f}{t:>7.2f}"
           f"{100*float((w > 0).mean()):>7.1f}%{gate:>18}"
           f"{obj.get(k, '- it is the incumbent'):>34}")
    P_(f"\n   The chronology gate is now the ONLY chronology test. Old-era weakness is not")
    P_(f"   disqualifying. Every remaining objection above is statistical or in-sample.")

    # =====================================================================================
    # PHASE 4 - WHAT WOULD RAISE THE POSITIVE-DAY RATE
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 4: decomposing the positive-day rate (never done before)")
    P_(f"{'='*118}")
    traded = ~FLAT["P1"]
    P_(f"   P1 trades {100*traded.mean():.1f} % of sessions and wins "
       f"{100*float((s0[traded] > 0).mean()):.1f} % of those -> "
       f"{100*float((s0 > 0).mean()):.1f} % of ALL sessions positive.")
    P_(f"\n{'if we could...':<44}{'positive-day rate':>20}{'gain':>10}")
    cur = 100 * float((s0 > 0).mean())
    P_(f"{'(current)':<44}{cur:>19.1f}%{'':>10}")
    for tr in (0.7, 0.8, 0.9, 1.0):
        r = 100 * tr * float((s0[traded] > 0).mean())
        P_(f"{f'trade {100*tr:.0f} % of sessions at the same win rate':<44}{r:>19.1f}%"
           f"{r-cur:>+9.1f}")
    for wr in (0.50, 0.55, 0.60):
        r = 100 * traded.mean() * wr
        P_(f"{f'keep the same days but win {100*wr:.0f} % of them':<44}{r:>19.1f}%"
           f"{r-cur:>+9.1f}")
    P_(f"\n   Arithmetic, not a forecast: the positive-day rate is bounded by the share of")
    P_(f"   sessions traded. P1 is FLAT on {100*(1-traded.mean()):.1f} % of sessions BY DESIGN")
    P_(f"   (the range throttle and the session box), so no entry-side improvement can lift")
    P_(f"   the all-session rate past {100*traded.mean():.1f} %. Raising it REQUIRES either")
    P_(f"   trading more sessions or a sleeve that trades the ones P1 sits out - which is what")
    P_(f"   the overlap table above prices.")
    P_(f"\n=== STATUS: re-adjudication and specification. Nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
