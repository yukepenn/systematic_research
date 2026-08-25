"""R11-B: set-valued inverse reconstruction over Solar event universes.

Directive v4.0 sections 6-10. Enumerates ALL feasible single-position trade paths per day
per event universe under the exact daily constraints, then emits event invariants
(MUST_TAKE / MUST_SKIP / AMBIGUOUS) and a per-universe feasibility adjudication.
"""
import csv
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
import inverse_core as IC  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")
INV = os.path.join(ROOT, "research", "original_trader_reconstruction",
                   "solar_family", "inverse")
os.makedirs(OUT, exist_ok=True); os.makedirs(INV, exist_ok=True)
COMM = 4.18

# ---------------------------------------------------------------------------
# targets: OTRIMG-0003, Analysis($) Period=Daily Time base=Exit Time.
# (n, win_pct, gross_profit, gross_loss_prefix, largest_win, largest_loss_prefix,
#  avg_MAE, avg_MFE)  -- "prefix" cells had trailing digits cropped in the screenshot.
# ---------------------------------------------------------------------------
RAW = {
 "2023-01-03": (12, 33.33, 5863.28, (-6163.40, 1), 3050.82, (-1179.10, 1), 635.42, 1015.00),
 "2023-01-04": (14, 35.71, 3859.10, (-5007.60, 1), 1865.82, (-899.18, 0), 591.79, 976.43),
 "2023-01-05": (6, 33.33, 2611.64, (-2641.70, 1), 2310.82, (-889.18, 0), 623.33, 1120.00),
 "2023-01-06": (10, 50.00, 6314.10, (-3320.90, 1), 4210.82, (-1384.10, 1), 737.50, 1536.00),
 "2023-01-09": (3, 66.67, 6116.64, (-854.18, 0), 3170.82, (-854.18, 0), 735.00, 2635.00),
 "2023-01-10": (9, 55.56, 3744.10, (-2551.70, 1), 1370.82, (-1084.10, 1), 562.78, 1188.89),
 "2023-01-11": (4, 50.00, 3106.64, (-1338.30, 1), 2190.82, (-749.18, 0), 452.50, 1243.75),
 "2023-01-12": (16, 31.25, 4704.10, (-8025.90, 1), 1535.82, (-1204.10, 1), 678.13, 1143.44),
 "2023-01-13": (6, 50.00, 3337.46, (-1912.50, 1), 1885.82, (-809.18, 0), 513.33, 1194.17),
 "2023-01-16": (3, 66.67, 641.64, (-34.18, 0), 555.82, (-34.18, 0), 106.67, 873.33),
 "2023-01-17": (6, 50.00, 1322.46, (-1737.50, 1), 590.82, (-1089.10, 1), 508.33, 967.50),
}

UNIVERSES = {
    "U1_T1":       (frozenset({1}),       True),
    "U2_T1_T2E":   (frozenset({1, 2}),    True),
    "U3_T1_T2L":   (frozenset({1, 2}),    False),
    "U4_T1_T3":    (frozenset({1, 3}),    True),
    "U5_T1_T2E_T3": (frozenset({1, 2, 3}), True),
    "U6_T1_T2L_T3": (frozenset({1, 2, 3}), False),
}


def build_targets():
    tgts = {}
    for day, (n, wp, gp, (glp, gc), lw, (llp, lc), amae, amfe) in RAW.items():
        nW = int(round(wp * n / 100.0)); nL = n - nW
        gl = IC.resolve_cropped(glp, nL, COMM, gc) if gc else round(glp, 2)
        ll = IC.resolve_cropped(llp, 1, COMM, lc) if lc else round(llp, 2)
        mae = round(amae * n / 5.0) * 5.0
        mfe = round(amfe * n / 5.0) * 5.0
        assert abs(mae / n - amae) < 0.006, (day, mae, amae)
        assert abs(mfe / n - amfe) < 0.006, (day, mfe, amfe)
        tgts[day] = IC.DayTarget(day, n, nW, nL, round(gp, 2), gl, lw, ll,
                                 mae, mfe, round(COMM * n, 2))
    return tgts


def main():
    tgts = build_targets()
    print("=== resolved daily targets (cropped cells recovered on the $5-tick lattice) ===")
    print(f"{'day':12} {'n':>3} {'nW':>3} {'nL':>3} {'grossP':>9} {'grossL':>10} "
          f"{'LW':>9} {'LL':>10} {'sumMAE':>8} {'sumMFE':>8} {'net':>10}")
    for d in sorted(tgts):
        T = tgts[d]
        print(f"{d:12} {T.n:>3} {T.nW:>3} {T.nL:>3} {T.gp:>9.2f} {T.gl:>10.2f} "
              f"{T.lw:>9.2f} {T.ll:>10.2f} {T.mae:>8.0f} {T.mfe:>8.0f} {T.net:>10.2f}")

    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2022-12-01") & (df["time"] <= "2023-01-18 17:00")].reset_index(drop=True)

    rows, inv_rows = [], []
    detail = {}
    for strict in (True, False):
      for uname, (mags, early) in UNIVERSES.items():
        bb = IC.prepare(seg, SolarWaveParams(pullback_early=early))
        sess = IC.sessions(bb)
        xr = "STRICT" if strict else "INCLUSIVE"
        # map each session to its exit-calendar day (verified equal to session date:
        # zero trades exit in the 18:00-23:59 block for this corpus)
        sd = {}
        for s0, s1 in sess:
            sd[str(bb["t"][s1])[:10]] = (s0, s1)
        print(f"\n=== {uname} (mags={sorted(mags)} pullback_early={early}) ===")
        for day in sorted(tgts):
            if day not in sd:
                print(f"  {day}: SESSION NOT FOUND"); continue
            s0, s1 = sd[day]
            T = tgts[day]
            sols, stats, mx = IC.solve_min_extra(
                bb, s0, s1, T, mags, extras_ladder=(0, 1, 2, 3),
                allow_reverse=True, allow_exit_only=True, stop_pts=None,
                comm_rt=COMM, node_budget=6_000_000, max_solutions=20000,
                exit_strict=strict)
            verdict = ("FEASIBLE" if sols else
                       ("BUDGET_EXCEEDED" if stats["overflow"] else
                        "IMPOSSIBLE_UNDER_UNIVERSE"))
            print(f"  {day}  cand={stats['n_candidates']:>3} nodes={stats['nodes']:>9,} "
                  f"sols={len(sols):>5} min_extra={mx}  {verdict}", flush=True)
            rows.append(dict(universe=uname, exit_rule=xr, day=day, n_target=T.n,
                             n_candidate_signals=stats["n_candidates"],
                             nodes=stats["nodes"], n_solutions=len(sols),
                             min_non_T1_entries=mx, verdict=verdict))
            if sols:
                detail.setdefault(f"{uname}|{xr}", {})[day] = sols
                # event invariants over the feasible set.
                # A trade's ENTRY BAR is the fill bar; the DECISION bar is entry_bar-1,
                # which is the signal the strategy either consumed or ignored.
                taken = [set((tr["ei"] - 1, tr["d"]) for tr in s) for s in sols]
                cands = [i for i in range(s0, s1 + 1) if IC.eligible(bb, i, mags)]
                allev = set().union(*taken) | {
                    (i, 1 if bb["st"][i] > 0 else -1) for i in cands}
                for ev in sorted(allev):
                    cnt = sum(1 for s in taken if ev in s)
                    cls = ("MUST_TAKE" if cnt == len(taken) else
                           "MUST_SKIP" if cnt == 0 else "AMBIGUOUS")
                    inv_rows.append(dict(universe=uname, exit_rule=xr, day=day,
                                         decision_bar=ev[0], dir=ev[1],
                                         signal_mag=int(abs(bb["st"][ev[0]]))
                                         if 0 <= ev[0] < bb["n"] else 0,
                                         decision_time=str(bb["t"][ev[0]]),
                                         in_paths=cnt, of_paths=len(taken), cls=cls))

    with open(os.path.join(INV, "FEASIBLE_PATH_SUMMARY.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    if inv_rows:
        with open(os.path.join(INV, "EVENT_INVARIANTS.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(inv_rows[0].keys())); w.writeheader(); w.writerows(inv_rows)

    print("\n=== FEASIBILITY MATRIX (days solved / 11) ===")
    d = pd.DataFrame(rows)
    piv = d.pivot_table(index=["exit_rule", "universe"], columns="verdict",
                        values="day", aggfunc="count").fillna(0).astype(int)
    print(piv.to_string())
    print("\n=== per-day: which universes can explain it ===")
    for day in sorted(tgts):
        f = d[(d.day == day) & (d.verdict == "FEASIBLE")]
        lab = [f"{r.exit_rule[:4]}/{r.universe}({r.n_solutions})" for r in f.itertuples()]
        print(f"  {day}  {'NONE' if not lab else ', '.join(lab)}")

    json.dump({u: {dd: len(v) for dd, v in m.items()} for u, m in detail.items()},
              open(os.path.join(OUT, "solution_counts.json"), "w"), indent=2)
    json.dump({u: {dd: [[{k: (float(x[k]) if k not in ("d", "ei", "xi") else int(x[k]))
                          for k in ("d", "ei", "xi", "epx", "xpx", "pnl", "mae", "mfe")}
                         for x in s0] for s0 in v[:50]] for dd, v in m.items()}
               for u, m in detail.items()},
              open(os.path.join(OUT, "feasible_paths.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
