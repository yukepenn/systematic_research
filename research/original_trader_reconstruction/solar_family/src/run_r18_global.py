"""R18 (authorised by runs/OTR_R11_INVERSE/amendment_4.yaml):
the GLOBAL inverse -- one continuous path that reproduces EVERY visible daily row.

Runs both day-assignment readings as a controlled pair. No P&L objective.
"""
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
from run_r11b_inverse import build_targets  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")


def main():
    tg = build_targets()
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2023-01-02 18:00") &
             (df["time"] <= "2023-01-17 17:00")].reset_index(drop=True)
    bb = IC.prepare(seg, SolarWaveParams())
    span_start, span_end = 0, bb["n"] - 1
    day_of = np.datetime_as_string(bb["t"].astype("datetime64[D]"))
    all_days = sorted(set(day_of.tolist()))
    empty = [d for d in all_days if d not in tg]
    print(f"bars {bb['n']:,}  {seg['time'].iloc[0]} .. {seg['time'].iloc[-1]}")
    print(f"calendar dates in span: {len(all_days)}   with a report row: {len(tg)}")
    print(f"dates that MUST have zero exits (no row in the report): {empty}\n")

    results = {}
    for strict in (True, False):
        for stop in (None,):
            tagx = "STRICT" if strict else "INCLUSIVE"
            sols, st = enumerate_multiday(
                bb, span_start, span_end, tg, frozenset({1}),
                comm_rt=4.18, exit_strict=strict, stop_pts=stop,
                empty_days=empty, node_budget=60_000_000, max_solutions=200)
            print(f"CALENDAR rule / exit={tagx:<10} -> global paths = {len(sols):<4} "
                  f"nodes={st['nodes']:,} {'(BUDGET)' if st['overflow'] else ''}",
                  flush=True)
            results[f"CALENDAR|{tagx}"] = sols
    # control: the SESSION reading, implemented by relabelling days by session date
    day_sess = day_of.copy()
    for s0, s1 in IC.sessions(bb):
        day_sess[s0:s1 + 1] = day_of[s1]
    bb2 = dict(bb)
    import inverse_multiday as IM
    orig = IM.np.datetime_as_string

    def patched(a, *args, **kw):   # inject session-date labelling
        return day_sess
    IM.np.datetime_as_string = patched
    try:
        for strict in (True, False):
            tagx = "STRICT" if strict else "INCLUSIVE"
            sols, st = enumerate_multiday(
                bb2, span_start, span_end, tg, frozenset({1}),
                comm_rt=4.18, exit_strict=strict, stop_pts=None,
                empty_days=[d for d in sorted(set(day_sess.tolist())) if d not in tg],
                node_budget=60_000_000, max_solutions=200)
            print(f"SESSION  rule / exit={tagx:<10} -> global paths = {len(sols):<4} "
                  f"nodes={st['nodes']:,} {'(BUDGET)' if st['overflow'] else ''}",
                  flush=True)
            results[f"SESSION|{tagx}"] = sols
    finally:
        IM.np.datetime_as_string = orig

    best = results.get("CALENDAR|STRICT") or []
    if best:
        print(f"\n=== GLOBAL PATH (first of {len(best)}) — {len(best[0])} trades ===")
        cum = 0.0
        for x in best[0]:
            cum += x["pnl"]
            print(f"  {'L' if x['d']>0 else 'S'} {str(bb['t'][x['ei']])[5:16]} "
                  f"@{x['epx']:9.2f} -> {str(bb['t'][x['xi']])[5:16]} @{x['xpx']:9.2f} "
                  f"pnl={x['pnl']:9.2f} cum={cum:10.2f} mae={x['mae']:6.0f} "
                  f"mfe={x['mfe']:6.0f} {x['kind']:4} day={x['day']}")
        print(f"\n  total {len(best[0])} trades, net {cum:.2f}")
        agree = all(len({tuple((y['ei'], y['xi'], y['d']) for y in p) for p in best}) == 1
                    for _ in [0])
        print(f"  all {len(best)} global paths identical as trade sets: {agree}")
    json.dump({k: [[{kk: (float(v[kk]) if kk in ('epx', 'xpx', 'pnl', 'mae', 'mfe')
                          else (int(v[kk]) if kk in ('d', 'ei', 'xi') else v[kk]))
                     for kk in ('d', 'ei', 'xi', 'epx', 'xpx', 'pnl', 'mae', 'mfe',
                                'kind', 'day')} for v in p] for p in s[:20]]
               for k, s in results.items()},
              open(os.path.join(OUT, "r18_global_paths.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
