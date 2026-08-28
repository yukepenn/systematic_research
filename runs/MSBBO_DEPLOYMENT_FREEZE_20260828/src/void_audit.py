"""VOID AUDIT - MS-BBO-CANDIDATE-1 reads the FUTURE.  Directive s12 applies.

WHAT THE STREAMING-PARITY RUN FOUND, on its first execution.
13 of the 20 frozen features reproduced at exactly 0.000e+00. The other 7 - and ONLY those built
from the 30-sample mid/spread path - disagreed by hundreds of dollars. Meanwhile midret_30s, which
reads the SAME instant t-30s through a different code path, matched exactly. That asymmetry has
exactly one explanation.

    bbo_v1.py:119     step = np.arange(-30, 0) * NS

On Windows with NumPy 1.26, np.arange(-30, 0) has dtype INT32. NS = 1_000_000_000 fits in int32,
so NumPy's value-based casting keeps the product in int32 - and -30 * 1e9 = -3e10 OVERFLOWS.
The offsets are not -30s..-1s. They are a scrambled set, FIFTEEN OF WHICH ARE POSITIVE, reaching
+2.065 SECONDS PAST THE DECISION INSTANT. Silently. No warning is raised for integer overflow.

CONTAMINATED:  rvol_30s  range_30s  dist_hi_30s  dist_lo_30s
               spread_chg_30s  spread_minfrac  spread_pctile
CLEAN:         the 13 others, including every midret_*, which use Python-int arithmetic.

This is not a rounding difference. It is directive s12's first listed condition: LOOK-AHEAD /
FEATURE TIMESTAMP VIOLATION / IMPOSSIBLE REAL-TIME INFORMATION.

>>> MS-BBO-CANDIDATE-1 IS VOID.  So is MS-BBO-CANDIDATE-1-DEPLOY, which inherits the features. <<<

This file proves it three ways rather than asserting it:
    V1  DIRECT TIMESTAMP ASSERTION on the ACTUAL offsets - the probe L1 should have made.
    V2  PERTURBATION - corrupt ONLY post-t events and show contaminated features change.
    V3  SIZE OF THE LEAK - re-run the frozen pipeline with the offsets corrected.
V3 is characterisation for the record and for EVI re-ranking. It is NOT a rescue: a corrected
object is a NEW discovery object on already-consumed data, carrying all the selection debt spent
here, and it would need its own preregistration.
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(RUN), "MSBBO_V1_20260828", "src"))
import bbo_v1 as B                                                      # noqa: E402

OUT = os.path.join(RUN, "out")
NS = B.NS
CONTAM = ["rvol_30s", "range_30s", "dist_hi_30s", "dist_lo_30s",
          "spread_chg_30s", "spread_minfrac", "spread_pctile"]

# The log handle is opened LAZILY, inside main(). A module-level open(..., "w") truncates the log
# whenever another script merely IMPORTS this module - which is exactly the defect recorded in
# MSBBO_V1/CORRECTION_20260828.md s1D-b, and it silently destroyed this file's own output once.
_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def corrected_features(path, fix):
    """The frozen definition with ONE change: the path offsets are computed in int64.

    Everything else - grid, horizon, labels, wait_ok, the other 13 features - is byte-for-byte the
    frozen construction, reproduced here because bbo_v1.py must not be edited.
    """
    d = pq.read_table(path, columns=["bip", "time", "price", "volume"]).to_pandas()
    tt = d["time"].values.astype("datetime64[ns]")
    if pd.Timestamp(tt.max()) >= pd.Timestamp(B.SEAL):
        return None
    ti = tt.astype("int64")
    bip, px, vol = d["bip"].values, d["price"].values, d["volume"].values.astype(float)
    day = pd.Timestamp(tt.max()).normalize()
    grid = np.arange((day + pd.Timedelta(B.RTH_START)).value,
                     (day + pd.Timedelta(B.RTH_END)).value + 1, B.GRID_S * NS)
    gh = grid + B.HORIZON_S * NS

    def side(b):
        m = bip == b
        t_, p_ = ti[m], px[m]
        u, inv = np.unique(t_, return_inverse=True)
        return u, np.bincount(inv, weights=p_) / np.bincount(inv)
    bt, bp = side(1)
    at, ap = side(2)
    lt_m = bip == 0
    lt, lp, lv = ti[lt_m], px[lt_m], vol[lt_m]
    ult, linv = np.unique(lt, return_inverse=True)
    lvol = np.bincount(linv, weights=lv)
    lvwap = np.bincount(linv, weights=lp * lv) / np.maximum(lvol, 1e-9)

    a_in, wa_in = B.next_val(at, ap, grid)
    b_in, wb_in = B.next_val(bt, bp, grid)
    b_out, wb_out = B.next_val(bt, bp, gh)
    a_out, wa_out = B.next_val(at, ap, gh)

    fb = B.prev_val(bt, bp, grid)
    fa = B.prev_val(at, ap, grid)
    mid = (fb + fa) / 2.0
    spread = fa - fb
    F = {"spread_tk": spread / B.TICK}
    for w in (1, 5, 15, 30):
        gm = grid - w * NS
        m0 = (B.prev_val(bt, bp, gm) + B.prev_val(at, ap, gm)) / 2.0
        F[f"midret_{w}s"] = (mid - m0) * B.DPP

    # ---- THE ONE CHANGE -------------------------------------------------
    step = (np.arange(-30, 0, dtype=np.int64) * NS) if fix else (np.arange(-30, 0) * NS)
    # ---------------------------------------------------------------------
    paths = np.array([(B.prev_val(bt, bp, grid + s) + B.prev_val(at, ap, grid + s)) / 2.0
                      for s in step])
    F["rvol_30s"] = np.nanstd(np.diff(paths, axis=0), axis=0) * B.DPP
    F["range_30s"] = (np.nanmax(paths, axis=0) - np.nanmin(paths, axis=0)) * B.DPP
    F["dist_hi_30s"] = (np.nanmax(paths, axis=0) - mid) * B.DPP
    F["dist_lo_30s"] = (mid - np.nanmin(paths, axis=0)) * B.DPP
    sp_path = np.array([B.prev_val(at, ap, grid + s) - B.prev_val(bt, bp, grid + s) for s in step])
    F["spread_chg_30s"] = (spread - sp_path[0]) / B.TICK
    F["spread_minfrac"] = np.nanmean(np.isclose(sp_path, np.nanmin(sp_path, axis=0)), axis=0)
    F["spread_pctile"] = np.array([np.nanmean(sp_path[:, j] <= spread[j]) for j in range(len(grid))])
    for nm, t_, p_ in (("bid", bt, bp), ("ask", at, ap)):
        c_hi = np.searchsorted(t_, grid, side="left")
        c_lo = np.searchsorted(t_, grid - 30 * NS, side="left")
        F[f"{nm}_upd_30s"] = (c_hi - c_lo).astype(float)
        dpz = np.sign(np.diff(p_, prepend=p_[0]))
        cum_up = np.concatenate([[0], np.cumsum(dpz > 0)])
        F[f"{nm}_up_30s"] = (cum_up[c_hi] - cum_up[c_lo]).astype(float)
    c_hi = np.searchsorted(ult, grid, side="left")
    c_lo = np.searchsorted(ult, grid - 30 * NS, side="left")
    cv = np.concatenate([[0], np.cumsum(lvol)])
    F["trade_buckets_30s"] = (c_hi - c_lo).astype(float)
    F["trade_vol_30s"] = (cv[c_hi] - cv[c_lo])
    dv = np.sign(np.diff(lvwap, prepend=lvwap[0]))
    csf = np.concatenate([[0], np.cumsum(dv * lvol)])
    F["signed_flow_30s"] = (csf[c_hi] - csf[c_lo])

    df = pd.DataFrame(F)
    df["t"] = grid
    df["mid"] = mid
    df["long_gross"] = (b_out - a_in) * B.DPP
    df["short_gross"] = (b_in - a_out) * B.DPP
    df["wait_ok"] = ((wa_in <= B.MAX_FILL_WAIT_MS) & (wb_in <= B.MAX_FILL_WAIT_MS) &
                     (wb_out <= B.MAX_FILL_WAIT_MS) & (wa_out <= B.MAX_FILL_WAIT_MS))
    import re
    df["session"] = re.match(r"^s(\d{8})", os.path.basename(path)).group(0)
    df["tod"] = (grid - (day + pd.Timedelta(B.RTH_START)).value) / (3600 * NS)
    return df


def main():
    global _fh
    _fh = open(os.path.join(OUT, "void_audit.txt"), "w", encoding="utf-8")
    P("=" * 104)
    P("=== VOID AUDIT - MS-BBO-CANDIDATE-1 READS THE FUTURE")
    P("=" * 104)

    # ------------------------------------------------------------------ V1
    P("")
    P("=== V1  DIRECT TIMESTAMP ASSERTION on the ACTUAL offsets  (the probe L1 should have made)")
    bad = np.arange(-30, 0) * NS
    good = np.arange(-30, 0, dtype=np.int64) * NS
    nfut = int((bad > 0).sum())
    P(f"    np.arange(-30,0).dtype = {np.arange(-30,0).dtype}   numpy {np.__version__}")
    P(f"    offsets that should ALL be negative:  {nfut} of 30 are POSITIVE")
    P(f"    most future-reaching offset:  {bad.max()/1e9:+.6f} s AFTER the decision instant")
    P(f"    intended range  [{good.min()/1e9:+.0f}s, {good.max()/1e9:+.0f}s]")
    P(f"    actual   range  [{bad.min()/1e9:+.6f}s, {bad.max()/1e9:+.6f}s]")
    P("    >>> VIOLATION: a feature at t reads quote state up to 2.065 s AFTER t.")

    files = sorted(glob.glob(os.path.join(B.V2, "s*.parquet")))

    # ------------------------------------------------------------------ V2
    P("")
    P("=== V2  PERTURBATION - corrupt ONLY events strictly AFTER t; clean features must not move")
    fp = files[len(files) // 2]
    d = pq.read_table(fp, columns=["bip", "time", "price", "volume"]).to_pandas()
    ti = d["time"].values.astype("datetime64[ns]").astype("int64")
    day = pd.Timestamp(d["time"].max()).normalize()
    base = corrected_features(fp, fix=False)
    tpick = base["t"].values[165]
    d2 = d.copy()
    m = ti > tpick                                   # STRICTLY future relative to the decision
    d2.loc[m, "price"] = d2.loc[m, "price"].values + 50.0
    tmp = os.path.join(OUT, os.path.basename(fp).replace(".parquet", "_perturb.parquet"))
    d2.to_parquet(tmp, index=False)
    try:
        pert = corrected_features(tmp, fix=False)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    P(f"    session {os.path.basename(fp)}   decision t = {pd.Timestamp(tpick)}")
    P(f"    perturbed {int(m.sum()):,} events strictly AFTER t by +50.0 points")
    P("")
    P(f"    {'feature':<20} {'unperturbed':>16} {'future corrupted':>18} {'delta':>14}")
    nmoved = 0
    for c in base.columns:
        if c in ("t", "mid", "long_gross", "short_gross", "wait_ok", "session"):
            continue
        a, b = float(base[c].values[165]), float(pert[c].values[165])
        dd = b - a
        if abs(dd) > 1e-9:
            nmoved += 1
        P(f"    {c:<20} {a:>16.6f} {b:>18.6f} {dd:>14.6f}"
          f"{'   <<< READS THE FUTURE' if abs(dd) > 1e-9 else ''}")
    P("")
    P(f"    >>> {nmoved} features changed when ONLY post-t data was corrupted.")
    P("    >>> A causal feature CANNOT move when future data changes. This is decisive.")

    # ------------------------------------------------------------------ V3
    P("")
    P("=" * 104)
    P("=== V3  HOW BIG WAS THE LEAK - the frozen pipeline with offsets corrected to int64")
    P("=== characterisation for the record and for EVI. NOT a rescue: a corrected object is a")
    P("=== NEW discovery object carrying every unit of selection debt already spent here.")
    P("=" * 104)
    res = {}
    for fix in (False, True):
        parts = [x for x in (corrected_features(f, fix) for f in files) if x is not None]
        dd = pd.concat(parts, ignore_index=True)
        meta = ("t", "mid", "long_gross", "short_gross", "wait_ok", "session")
        feats = [c for c in dd.columns if c not in meta]
        dd = dd[dd["wait_ok"] & dd[feats].notna().all(axis=1)
                & dd["long_gross"].notna() & dd["short_gross"].notna()].copy()
        dd = dd.sort_values("t").reset_index(drop=True)
        X = np.nan_to_num(dd[feats].values.astype(float), posinf=0, neginf=0)
        y = (dd["long_gross"].values + (-dd["short_gross"].values)) / 2.0
        sess = dd["session"].values
        order = pd.unique(sess)
        blocks = np.array_split(order, B.N_FOLD + 1)
        ix, pr = B.oof(X, y, sess, blocks, lambda: Ridge(alpha=10.0))
        net, act = B.policy_pnl(pr, dd.iloc[ix], 0.0)
        ss = pd.Series(net).groupby(sess[ix]).sum()
        c = float(np.corrcoef(pr, y[ix])[0, 1])
        res["FIXED" if fix else "AS-FROZEN (leaky)"] = (
            ss.mean(), ss.sum(), len(ss), 100 * np.mean(act != 0), c,
            float(ss.mean() / (ss.std() / np.sqrt(len(ss)))), 100 * np.mean(ss > 0))
    P("")
    P(f"    {'arm':<22} {'$/session':>12} {'net':>12} {'sess':>6} {'trade%':>8} "
      f"{'OOF corr':>10} {'t':>8} {'pos%':>7}")
    for k, v in res.items():
        P(f"    {k:<22} {v[0]:>12,.2f} {v[1]:>12,.0f} {v[2]:>6} {v[3]:>8.1f} "
          f"{v[4]:>10.4f} {v[5]:>8.2f} {v[6]:>7.1f}")
    a, b = res["AS-FROZEN (leaky)"][0], res["FIXED"][0]
    P("")
    P(f"    the look-ahead was worth  ${a - b:,.2f}/session  =  {100*(a-b)/a:.1f} % of the")
    P(f"    reported result.  What survives causally: ${b:,.2f}/session.")
    _fh.close()


if __name__ == "__main__":
    main()
