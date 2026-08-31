"""Diagnostic: at WHICH bar does each engine evaluate the quality score?

Python gfills:   want = dir_arr[i-1]; fill at o[i]; size read at size_at_entry[i]
                 -> score uses X at index i, i.e. information through bar i-1.
NinjaScript:     decides on bar b from lagged cache (info through b-1), fills at open of b+1
                 -> score uses information through b-1 = fill_bar - 2.

If that reading is right, evaluating the Python features one bar EARLIER (index i-1) must
agree with the certified NT8 qty far better than evaluating them at i.
"""
from __future__ import annotations
import os, sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "vwap_flux_family", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "T2_P1SIZE01_20260831", "src"))
from t2_p1size01 import load_substrate, WIN, MINHIST, NT8_TRADES, PV  # noqa

FEATS = [("dist_open", +1, 2 / 3), ("prev_ret", -1, 1 / 3), ("runlen", +1, 0.9),
         ("dist_vwap", +1, 2 / 3), ("delta_mag", +1, 2 / 3)]


def score_at(X, idx):
    vals = {k: np.asarray(X[k])[idx].astype(float) for k, _, _ in FEATS}
    N = len(idx)
    sc = np.zeros(N)
    for j in range(N):
        if j < MINHIST:
            continue
        lo = max(0, j - WIN)
        s = 0
        for k, sgn, q in FEATS:
            thr = np.nanquantile(vals[k][lo:j], q)
            x = vals[k][j]
            s += (x >= thr) if sgn > 0 else (x <= thr)
        sc[j] = s
    return sc


def main():
    D = load_substrate()
    from we_fastctx import fast_build_context
    X = fast_build_context(D)
    nt = pd.read_csv(NT8_TRADES, parse_dates=["et", "xt"])
    nt = nt[nt["et"] <= pd.Timestamp("2026-07-31 17:00")].reset_index(drop=True)
    tt = nt["et"].values.astype("datetime64[s]")
    ei = np.searchsorted(D["t"], tt)
    ok = D["t"][ei] == tt
    nt = nt[ok].reset_index(drop=True); ei = ei[ok]
    q = nt["qty"].to_numpy()
    per = (nt["pnl"] / nt["qty"]).to_numpy()
    print(f"entries {len(ei)}")
    for lag in (0, 1, 2):
        idx = np.maximum(ei - lag, 0)
        sc = score_at(X, idx)
        sz = 1 + (sc >= 3).astype(int)
        ag = float(np.mean(sz == q))
        print(f"  features at fill_bar - {lag}: size agreement with NT8 qty = {100*ag:6.2f}% "
              f"({int((sz==q).sum())}/{len(q)})   arm net ${np.sum(per*sz):,.0f}   "
              f"NT8 net ${nt.pnl.sum():,.0f}")
        np.save(os.path.join(ROOT, "runs", "T2_P1SIZE01_20260831", "out",
                             f"score_lag{lag}.npy"), sc)


if __name__ == "__main__":
    main()
