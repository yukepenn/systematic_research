"""WE_W15 TRUEDELTA (spec preregistered): true tick delta vs the 1-min proxy, on the 40 tick sessions."""
from __future__ import annotations

import glob
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, load, sm14_1m                  # noqa: E402
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w14 import true_delta_session                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W15_TRUEDELTA", "out")
os.makedirs(OUT, exist_ok=True)


def main():
    t0 = _time.time()
    D = load()
    n, tarr = D["n"], D["t"]
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ok08 = (norm <= 0) | (ratio >= 0.8)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_proxy = cd_signals(D)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    print(f"base ready [{_time.time()-t0:.0f}s]", flush=True)

    # ---- build true-delta cumulative series on the 1-min clock, tick sessions only ----
    files = [f for f in sorted(glob.glob(os.path.join(
        ROOT, "research", "scalping_lab", "substrate", "raw", "NQ", "s2*.parquet")))
        if "_rth" not in os.path.basename(f)]
    tmin = pd.Series(np.arange(n), index=pd.to_datetime(D["t"]))
    cum_ud = np.full(n, np.nan)
    cum_ba = np.full(n, np.nan)
    covered = np.zeros(n, bool)
    used = 0
    for f in files:
        try:
            g = true_delta_session(f)
        except Exception as e:                                          # noqa: BLE001
            print(f"   skip {os.path.basename(f)}: {e}", flush=True)
            continue
        if len(g) < 200:
            continue
        pos = tmin.reindex(g.index)
        m = pos.notna().values
        if m.sum() < 100:
            continue
        ii = pos[m].values.astype(int)
        cum_ud[ii] = np.cumsum(g["ud"].values[m])
        cum_ba[ii] = np.cumsum(g["ba"].values[m])
        covered[ii] = True
        used += 1
    print(f"tick sessions mapped: {used}, bars covered {covered.sum():,} "
          f"[{_time.time()-t0:.0f}s]", flush=True)

    # restrict every variant to the covered bars so the comparison is like-for-like
    sess_ok = np.zeros(D["n_sess"], bool)
    for s in np.unique(D["sid"][covered]):
        sess_ok[s] = True
    active = sess_ok[D["sid"]]
    idx = np.arange(n)
    avail = np.zeros(D["n_sess"])
    for s in np.nonzero(sess_ok)[0]:
        m = idx[D["sid"] == s]
        avail[s], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)

    out = open(os.path.join(OUT, "truedelta.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    P(f"sample: {used} tick sessions, {covered.sum():,} covered 1-min bars, "
      f"available {avail.sum():,.0f} pts")
    P("NOTE (spec): no Sharpe is quoted from this sample - it is ~8 weeks.\n")
    P(f"{'gate':<12}{'n':>7}{'net':>12}{'$/trade':>10}{'capture%':>10}"
      f"{'long$':>11}{'short$':>11}")

    def run(nm, gl, gs):
        aL = ok08 & active & (gl if gl is not None else True)
        aS = ok08 & active & (gs if gs is not None else True)
        trl = fills(D, tgn, allow_long=aL, allow_short=aS)
        trl = [x for x in trl
               if active[int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))]]
        if not trl:
            P(f"{nm:<12} no trades")
            return
        p = np.array([x["pnl"] for x in trl]); d = np.array([x["d"] for x in trl])
        cap = 100 * p.sum() / PV / avail.sum()
        P(f"{nm:<12}{len(p):>7}{p.sum():>12,.0f}{p.mean():>10.1f}{cap:>10.2f}"
          f"{p[d > 0].sum():>11,.0f}{p[d < 0].sum():>11,.0f}")
        return p

    g0 = run("G0_nogate", None, None)
    g1 = run("G1_proxy", lag_b(cd_proxy >= 0), lag_b(cd_proxy <= 0))
    ud_ok = ~np.isnan(cum_ud)
    ba_ok = ~np.isnan(cum_ba)
    g2 = run("G2_true_UD", lag_b(~ud_ok | (cum_ud >= 0)), lag_b(~ud_ok | (cum_ud <= 0)))
    g3 = run("G3_true_BA", lag_b(~ba_ok | (cum_ba >= 0)), lag_b(~ba_ok | (cum_ba <= 0)))

    P("\n--- preregistered decision rule ---")
    for nm, g in (("G2_true_UD", g2), ("G3_true_BA", g3)):
        if g is None or g1 is None:
            continue
        dpt = 100 * (g.mean() - g1.mean()) / abs(g1.mean()) if g1.mean() else float("nan")
        dtot = 100 * (g.sum() - g1.sum()) / abs(g1.sum()) if g1.sum() else float("nan")
        verdict = ("TICK DATA WORTH ACQUIRING" if dpt >= 25 and dtot >= 25
                   else "does not clear the 25% bar")
        P(f"{nm} vs proxy: $/trade {dpt:+.1f}%   total {dtot:+.1f}%   -> {verdict}")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
