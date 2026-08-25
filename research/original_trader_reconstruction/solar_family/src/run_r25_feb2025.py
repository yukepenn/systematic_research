"""R25 (spec preregistered): global inverse on the Feb-2025 daily table.

Same machinery that recovered 2023-01-03..17 exactly. Tests whether the mechanism pinned
there (T1-only entries, STRICT exit, calendar-date rows) survives into the 2025 era, and
whether the 90-trade day of 2025-02-27 is reachable at all.
"""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
import inverse_core as IC  # noqa: E402
from inverse_multiday import enumerate_multiday  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R25_FEB2025_INVERSE", "out")
os.makedirs(OUT, exist_ok=True)
COMM = 5.68

TG = {
    "2025-02-26": IC.DayTarget("2025-02-26", 15, 8, 7, 4889.56, -1564.76,
                               2089.32, -405.68, 2855.0, 10435.0, 85.20),
    "2025-02-27": IC.DayTarget("2025-02-27", 90, 35, 55, 29306.20, -18222.40,
                               5029.32, -865.68, 30770.0, 64480.0, 511.20),
}
UNIVERSES = {"U1_T1": (frozenset({1}), True),
             "U2_T1_T2E": (frozenset({1, 2}), True),
             "U4_T1_T3": (frozenset({1, 3}), True),
             "U5_T1_T2E_T3": (frozenset({1, 2, 3}), True)}


def main():
    for d, T in TG.items():
        assert abs(T.gp + T.gl - T.net) < 0.011, d
        assert abs(T.mae / T.n * T.n - T.mae) < 1e-9
        print(f"{d}: n={T.n} nW={T.nW} nL={T.nL} gp={T.gp} gl={T.gl} "
              f"net={T.net} MAE={T.mae:.0f} MFE={T.mfe:.0f}  "
              f"(lattice: MAE/5={T.mae/5:.0f}, MFE/5={T.mfe/5:.0f})")
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    # span: from the session that opens the 02-26 calendar day, through 02-27 23:59,
    # plus enough following bars to resolve exits.
    seg = df[(df["time"] >= "2025-02-24 18:00") &
             (df["time"] <= "2025-02-28 17:00")].reset_index(drop=True)
    print(f"\nbars {len(seg):,}  {seg['time'].iloc[0]} .. {seg['time'].iloc[-1]}")

    rows = []
    print(f"\n{'universe':<14} {'exit':>6} {'stop':>5} | {'02-26':>18} | {'02-27':>18} | joint")
    for uname, (mags, early) in UNIVERSES.items():
        bb = IC.prepare(seg, SolarWaveParams(pullback_early=early))
        day_of = np.datetime_as_string(bb["t"].astype("datetime64[D]"))
        alld = sorted(set(day_of.tolist()))
        c_end = int(np.max(np.flatnonzero(day_of == "2025-02-27")))
        empty = [d for d in alld if d not in TG and d <= "2025-02-27"]
        for strict in (True, False):
            for stop in (None, 65.0):
                cells = []
                for d, T in TG.items():
                    lo = int(np.min(np.flatnonzero(day_of == d)))
                    hi = int(np.max(np.flatnonzero(day_of == d)))
                    span = 0
                    for s0, s1 in IC.sessions(bb):
                        if s0 <= lo <= s1:
                            span = s0
                    s, stt = IC.enumerate_calendar_day(
                        bb, span, hi, lo, hi, T, mags, comm_rt=COMM,
                        exit_strict=strict, stop_pts=stop,
                        node_budget=4_000_000, max_solutions=200)
                    cells.append(f"{len(s):>5}{'B' if stt['overflow'] else ' '} paths ")
                    rows.append(dict(universe=uname, exit_rule="STRICT" if strict else "INCL",
                                     stop=stop, scope="day", day=d, n_paths=len(s),
                                     overflow=stt["overflow"], nodes=stt["nodes"]))
                js, jst = enumerate_multiday(
                    bb, 0, bb["n"] - 1, TG, mags, comm_rt=COMM, exit_strict=strict,
                    stop_pts=stop, empty_days=empty, count_end=c_end,
                    node_budget=30_000_000, max_solutions=50)
                rows.append(dict(universe=uname, exit_rule="STRICT" if strict else "INCL",
                                 stop=stop, scope="joint", day="BOTH", n_paths=len(js),
                                 overflow=jst["overflow"], nodes=jst["nodes"]))
                print(f"{uname:<14} {'STRICT' if strict else 'INCL':>6} "
                      f"{str(stop):>5} | {cells[0]:>18} | {cells[1]:>18} | "
                      f"{len(js)}{'B' if jst['overflow'] else ''}", flush=True)
                if js:
                    json.dump([{k: (float(v) if k in ('epx', 'xpx', 'pnl', 'mae', 'mfe')
                                    else (int(v) if k in ('d', 'ei', 'xi') else v))
                                for k, v in x.items()} for x in js[0]],
                              open(os.path.join(OUT, f"path_{uname}_"
                                   f"{'S' if strict else 'I'}_{stop}.json"), "w"), indent=1)
    with open(os.path.join(OUT, "r25_grid.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # how many trades are even REACHABLE on 2025-02-27?
    print("\n=== reachable trade counts on 2025-02-27 (count-only, T1 universe) ===")
    bb = IC.prepare(seg, SolarWaveParams())
    day_of = np.datetime_as_string(bb["t"].astype("datetime64[D]"))
    lo = int(np.min(np.flatnonzero(day_of == "2025-02-27")))
    hi = int(np.max(np.flatnonzero(day_of == "2025-02-27")))
    span = 0
    for s0, s1 in IC.sessions(bb):
        if s0 <= lo <= s1:
            span = s0
    for strict in (True, False):
        for stop in (None, 65.0, 40.0, 25.0):
            best = 0
            for n in range(1, 120):
                T2 = IC.DayTarget("x", n, n, n, 0, 0, 1e9, -1e9, 0, 0, 0)
                s, _ = IC.enumerate_calendar_day(
                    bb, span, hi, lo, hi, T2, frozenset({1}), comm_rt=COMM,
                    exit_strict=strict, stop_pts=stop, node_budget=600_000,
                    max_solutions=1, drop=("gp", "gl", "lw", "ll", "wl", "mae", "mfe"))
                if s:
                    best = n
                elif n > 4:
                    break
            print(f"  exit={'STRICT' if strict else 'INCL':<7} stop={str(stop):<5} "
                  f"-> max reachable trades = {best}   (report says 90)", flush=True)
    print(f"\n  T1 signal bars inside the 2025-02-27 calendar day: "
          f"{sum(1 for i in range(lo, hi+1) if abs(bb['st'][i]) == 1)}")


if __name__ == "__main__":
    main()
