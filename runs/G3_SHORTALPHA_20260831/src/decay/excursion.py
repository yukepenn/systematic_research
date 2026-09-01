"""G3_SHORTALPHA / decay - STAGE 1b: per-trade excursion, so the decay can be split into
"the entries never got favourable" vs "the favourable move was given back".

Reads the cached trade ledger (entry_i / exit_i are indices into the FULL substrate, which
load_deep reproduces deterministically for the same range) and adds, for every short trade:
    mfe_pts  = entry_px - min(low)  over the held bars      (best the trade ever was)
    mae_pts  = entry_px - max(high) over the held bars      (worst it ever was, <= 0)
    eff      = realised gross pts / mfe_pts                  (how much of its own best it kept)

No new construction, no tuning. This is instrumentation of an existing ledger.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

WE = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\src"
sys.path.insert(0, WE)
from run_we_w01 import ROOT                                              # noqa: E402
from run_we_w17 import load_deep                                        # noqa: E402

CACHE = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831", "out", "_decay_cache")
SEAL = np.datetime64("2026-08-01")


def main():
    t0 = _time.time()
    D = load_deep("2006-01-01", "2026-07-31 17:00", extend=True)
    assert D["t"].max() < SEAL, "SEAL VIOLATION"
    print(f"   SEAL ASSERTION [EXCURSION]: max bar {D['t'].max()} < {SEAL} -> PASS", flush=True)
    h, l, o = D["h"], D["l"], D["o"]
    for nm in ("full_short_trades", "full_long_trades"):
        f = os.path.join(CACHE, nm + ".csv")
        df = pd.read_csv(f, parse_dates=["date"])
        n = len(df)
        if df["entry_i"].max() >= D["n"]:
            raise SystemExit("index mismatch - substrate differs from stage 1")
        mfe = np.zeros(n); mae = np.zeros(n)
        ei = df["entry_i"].values; xi = df["exit_i"].values
        ep = df["entry_px"].values; sgn = df["d"].values
        for j in range(n):
            a, b = ei[j], max(xi[j], ei[j]) + 1
            hi = h[a:b].max(); lo = l[a:b].min()
            if sgn[j] > 0:
                mfe[j] = hi - ep[j]; mae[j] = lo - ep[j]
            else:
                mfe[j] = ep[j] - lo; mae[j] = ep[j] - hi
        df["mfe_pts"] = mfe
        df["mae_pts"] = mae
        with np.errstate(invalid="ignore", divide="ignore"):
            df["eff"] = np.where(mfe > 1e-9, df["gross_pts"].values / mfe, np.nan)
        df.to_csv(f, index=False)
        print(f"   {nm}: {n:,} trades instrumented [{_time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
