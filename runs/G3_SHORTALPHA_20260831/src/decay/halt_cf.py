"""G3_SHORTALPHA / decay - STAGE 1c: the no-overlay COUNTERFACTUAL (spec amendment 1).

Conditioning on "was this session halted" is post-outcome selection. The only way to turn the
halt-frequency table into a measurement is to remove the overlay and look. This builds exactly
one extra arm:

    S_nohalt = the same mirrored short sleeve with halt=+inf and target=None.

Nothing else changes. It is never quoted as a candidate. The falsifier is in the spec.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

WE = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\src"
sys.path.insert(0, WE)
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                        # noqa: E402
from run_we_w38 import vote, sfills                                     # noqa: E402
from we_quality import build_context                                    # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import targets_local, trades_frame, session_bounds           # noqa: E402

CACHE = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831", "out", "_decay_cache")
SEAL = np.datetime64("2026-08-01")


def main():
    t0 = _time.time()
    D = load_deep("2006-01-01", "2026-07-31 17:00", extend=True)
    assert D["t"].max() < SEAL, "SEAL VIOLATION"
    print(f"   SEAL ASSERTION [HALT_CF]: max bar {D['t'].max()} < {SEAL} -> PASS", flush=True)
    X = build_context(D)
    print(f"   context [{_time.time()-t0:.0f}s]", flush=True)
    TG = targets_local(D)
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    print(f"   vote [{_time.time()-t0:.0f}s]", flush=True)
    tr = sfills(D, posS, halt=float("inf"), target=None)
    df = trades_frame(tr, D)
    df.to_csv(os.path.join(CACHE, "full_short_trades_nohalt.csv"), index=False)
    print(f"   S_nohalt: {len(df):,} trades [{_time.time()-t0:.0f}s]", flush=True)

    ns = D["n_sess"]
    v = np.zeros(ns); np.add.at(v, df["sess"].values, df["pnl436"].values)
    g = np.zeros(ns); np.add.at(g, df["sess"].values, df["gross_pts"].values)
    nt = np.zeros(ns); np.add.at(nt, df["sess"].values, np.ones(len(df)))
    pd.DataFrame(dict(sess=np.arange(ns), date=pd.to_datetime(D["sess_date"]),
                      nohalt_pnl436=v, nohalt_gross_pts=g, nohalt_ntr=nt)).to_csv(
        os.path.join(CACHE, "full_sessions_nohalt.csv"), index=False)
    print(f"done [{_time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
