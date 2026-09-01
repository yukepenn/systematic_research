"""Timing probe: how expensive is rebuilding the sleeve's targets on the 2006-2021 substrate?"""
import os
import sys
import time as _time

import numpy as np

ROOT_ = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT_, "research", "weekly_edge", "src"))
from run_we_w01 import sm14_1m                                            # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402

t0 = _time.time()
D = load_deep("2020-01-01", "2020-06-30 17:00")
print(f"probe bars {D['n']:,} sessions {D['n_sess']:,} [{_time.time()-t0:.1f}s]", flush=True)
t1 = _time.time()
tg = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14])
dt = _time.time() - t1
print(f"sm14_1m narrow5 on {D['n']:,} bars: {dt:.1f}s  -> {1e6*dt/D['n']:.2f} us/bar", flush=True)

t2 = _time.time()
Dfull = load_deep("2006-01-05", "2021-12-31 17:00")
print(f"deep bars {Dfull['n']:,} sessions {Dfull['n_sess']:,} [{_time.time()-t2:.1f}s]",
      flush=True)
# 4 member sets, cost roughly proportional to sum of member counts (5+6+7+13 = 31 vs 5 here)
est = dt / D["n"] * Dfull["n"] * (31 / 5)
print(f"ESTIMATED deep target build (4 member sets, 31 members total): {est/60:.1f} min",
      flush=True)
print(f"deep window {Dfull['t'][0]} -> {Dfull['t'][-1]}", flush=True)
