"""MS-BBO-V1 - discovery-grade BBO alpha attempt.  Frozen by SPEC.md before this ran.

CEILING, stated up front: there is NO clean BBO historical holdout - every quote-complete session
has had its price outcomes consumed. The best possible outcome here is a DISCOVERY-GRADE CANDIDATE
that must earn real validation PROSPECTIVELY. This run cannot produce "validated alpha".

INFORMATION vs EXECUTION (s13/s14), the distinction this whole design turns on:
    FEATURES   read events with timestamp STRICTLY < t
    EXECUTION  takes the first quote at a DISTINCT timestamp > t (entry) and > t+h (exit)
Same-millisecond ordering is unrecoverable, so neither clock may touch an event stamped exactly t.

PERMANENTLY BLOCKED (MS01A): true aggressor side, queue position, quote-then-trade causality inside
a millisecond, displayed-depth absorption, bid/ask SIZE imbalance, true microprice, depth sweep.
QUOTE VOLUME IS NOT USED ANYWHERE. Bid/ask PRICE only.
"""
from __future__ import annotations

import glob
import hashlib
import os
import re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
V2 = os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

NS = 1_000_000_000
GRID_S, HORIZON_S = 60, 60
RTH_START, RTH_END = "10:00:00", "15:30:00"
MAX_FILL_WAIT_MS = 1000.0          # FROZEN by fill_contract.py from timestamps alone
DPP, TICK = 20.0, 0.25             # NQ $/point, tick size
COMMISSION_RT = 4.36
STRESS_TICKS = (0.0, 0.5, 1.0)     # per SIDE, declared ladder
SEAL = "2026-08-01"
N_FOLD, SEED = 5, 20260828
NULL_SHIFTS = 90
_fh = open(os.path.join(OUT, "bbo_v1.txt"), "w", encoding="utf-8")
ATTEMPTS = []


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def prev_val(ev_t, ev_v, g):
    """Last value at a timestamp STRICTLY < g.  (features)"""
    i = np.searchsorted(ev_t, g, side="left") - 1
    out = np.full(len(g), np.nan)
    ok = i >= 0
    out[ok] = ev_v[i[ok]]
    return out


def next_val(ev_t, ev_v, g):
    """First value at a DISTINCT timestamp > g, plus the wait in ms.  (execution)"""
    i = np.searchsorted(ev_t, g, side="right")
    out = np.full(len(g), np.nan)
    wait = np.full(len(g), np.inf)
    ok = i < len(ev_t)
    out[ok] = ev_v[i[ok]]
    wait[ok] = (ev_t[i[ok]] - g[ok]) / 1e6
    return out, wait


def session_features(path):
    d = pq.read_table(path, columns=["bip", "time", "price", "volume"]).to_pandas()
    tt = d["time"].values.astype("datetime64[ns]")
    if pd.Timestamp(tt.max()) >= pd.Timestamp(SEAL):
        return None
    ti = tt.astype("int64")
    bip, px, vol = d["bip"].values, d["price"].values, d["volume"].values.astype(float)
    day = pd.Timestamp(tt.max()).normalize()
    grid = np.arange((day + pd.Timedelta(RTH_START)).value,
                     (day + pd.Timedelta(RTH_END)).value + 1, GRID_S * NS)
    gh = grid + HORIZON_S * NS

    # ---- collapse each side to DISTINCT timestamps (last price at that stamp is ambiguous
    # inside the ms, so use the MEAN, which is permutation-invariant)
    def side(b):
        m = bip == b
        t_, p_ = ti[m], px[m]
        u, inv = np.unique(t_, return_inverse=True)
        s = np.bincount(inv, weights=p_) / np.bincount(inv)
        return u, s
    bt, bp = side(1)
    at, ap = side(2)
    lt_m = bip == 0
    lt, lp, lv = ti[lt_m], px[lt_m], vol[lt_m]
    ult, linv = np.unique(lt, return_inverse=True)
    lvol = np.bincount(linv, weights=lv)
    lvwap = np.bincount(linv, weights=lp * lv) / np.maximum(lvol, 1e-9)

    # ---- EXECUTION legs: first DISTINCT quote strictly after
    a_in, wa_in = next_val(at, ap, grid)
    b_in, wb_in = next_val(bt, bp, grid)
    b_out, wb_out = next_val(bt, bp, gh)
    a_out, wa_out = next_val(at, ap, gh)

    # ---- FEATURES: everything strictly BEFORE t
    fb = prev_val(bt, bp, grid)
    fa = prev_val(at, ap, grid)
    mid = (fb + fa) / 2.0
    spread = fa - fb
    F = {"spread_tk": spread / TICK}
    for w in (1, 5, 15, 30):
        gm = grid - w * NS
        m0 = (prev_val(bt, bp, gm) + prev_val(at, ap, gm)) / 2.0
        F[f"midret_{w}s"] = (mid - m0) * DPP
    # short realized vol / range / distance to extrema, from a 30s mid path sampled each second
    step = np.arange(-30, 0) * NS
    paths = np.array([(prev_val(bt, bp, grid + s) + prev_val(at, ap, grid + s)) / 2.0
                      for s in step])
    F["rvol_30s"] = np.nanstd(np.diff(paths, axis=0), axis=0) * DPP
    F["range_30s"] = (np.nanmax(paths, axis=0) - np.nanmin(paths, axis=0)) * DPP
    F["dist_hi_30s"] = (np.nanmax(paths, axis=0) - mid) * DPP
    F["dist_lo_30s"] = (mid - np.nanmin(paths, axis=0)) * DPP
    # spread state
    sp_path = np.array([prev_val(at, ap, grid + s) - prev_val(bt, bp, grid + s) for s in step])
    F["spread_chg_30s"] = (spread - sp_path[0]) / TICK
    F["spread_minfrac"] = np.nanmean(np.isclose(sp_path, np.nanmin(sp_path, axis=0)), axis=0)
    F["spread_pctile"] = np.array([np.nanmean(sp_path[:, j] <= spread[j])
                                   for j in range(len(grid))])
    # quote PRICE update intensity (counts of distinct-timestamp updates; no sizes)
    for nm, t_, p_ in (("bid", bt, bp), ("ask", at, ap)):
        c_hi = np.searchsorted(t_, grid, side="left")
        c_lo = np.searchsorted(t_, grid - 30 * NS, side="left")
        F[f"{nm}_upd_30s"] = (c_hi - c_lo).astype(float)
        dpz = np.sign(np.diff(p_, prepend=p_[0]))
        cum_up = np.concatenate([[0], np.cumsum(dpz > 0)])
        F[f"{nm}_up_30s"] = (cum_up[c_hi] - cum_up[c_lo]).astype(float)
    # order-invariant trade controls
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
    # labels from the ACTUAL BBO execution contract; commission exactly once
    df["long_gross"] = (b_out - a_in) * DPP
    df["short_gross"] = (b_in - a_out) * DPP
    df["wait_ok"] = ((wa_in <= MAX_FILL_WAIT_MS) & (wb_in <= MAX_FILL_WAIT_MS) &
                     (wb_out <= MAX_FILL_WAIT_MS) & (wa_out <= MAX_FILL_WAIT_MS))
    df["session"] = re.match(r"^s(\d{8})", os.path.basename(path)).group(0)
    df["tod"] = (grid - (day + pd.Timedelta(RTH_START)).value) / (3600 * NS)
    return df


def policy_pnl(pred, d, extra_ticks):
    """LONG/SHORT/FLAT from a CAUSAL threshold: the spread observable strictly before t plus
    commission is what the decision must clear."""
    thr = d["spread_tk"].values * TICK * DPP + COMMISSION_RT + 2 * extra_ticks * TICK * DPP
    slip = 2 * extra_ticks * TICK * DPP
    act = np.where(pred > thr, 1, np.where(pred < -thr, -1, 0))
    net = np.where(act == 1, d["long_gross"].values - COMMISSION_RT - slip,
                   np.where(act == -1, d["short_gross"].values - COMMISSION_RT - slip, 0.0))
    return net, act


def oof(X, y, sess, blocks, make):
    pr, ix = [], []
    for k in range(1, N_FOLD + 1):
        tr = np.concatenate(blocks[:k])
        mtr, mte = np.isin(sess, tr), np.isin(sess, blocks[k])
        if mtr.sum() < 50 or mte.sum() == 0:
            continue
        mu, sd = X[mtr].mean(0), X[mtr].std(0)
        sd[sd == 0] = 1
        m = make().fit((X[mtr] - mu) / sd, y[mtr])
        pr.append(m.predict((X[mte] - mu) / sd))
        ix.append(np.where(mte)[0])
    return np.concatenate(ix), np.concatenate(pr)


def main():
    P("=" * 104)
    P("=== MS-BBO-V1 - DISCOVERY-GRADE ONLY.  No clean BBO historical holdout exists.")
    P("=" * 104)
    P(f"    THIS FILE sha256 "
      f"{hashlib.sha256(open(os.path.abspath(__file__),'rb').read()).hexdigest()}")
    parts = []
    for f in sorted(glob.glob(os.path.join(V2, "s*.parquet"))):
        try:
            x = session_features(f)
        except Exception as e:                                       # noqa: BLE001
            P(f"    !! {os.path.basename(f)} {type(e).__name__}: {e}")
            continue
        if x is not None:
            parts.append(x)
        if len(parts) % 15 == 0 and parts:
            P(f"    ... {len(parts)} sessions built")
    d = pd.concat(parts, ignore_index=True)
    meta = ("t", "mid", "long_gross", "short_gross", "wait_ok", "session")
    feats = [c for c in d.columns if c not in meta]
    d = d[d["wait_ok"] & d[feats].notna().all(axis=1)
          & d["long_gross"].notna() & d["short_gross"].notna()].copy()
    d = d.sort_values("t").reset_index(drop=True)
    X = np.nan_to_num(d[feats].values.astype(float), posinf=0, neginf=0)
    # TARGET: the future mid move in dollars. The POLICY, not the target, applies the cost.
    y = ((d["long_gross"].values + (-d["short_gross"].values)) / 2.0)
    sess = d["session"].values
    order = pd.unique(d["session"])
    blocks = np.array_split(order, N_FOLD + 1)

    P("")
    P(f"    sessions {len(order)}   decisions {len(d):,}   features {len(feats)}")
    P(f"    decisions/session {len(d)/len(order):.1f}   "
      f"mean |mid move| ${np.abs(y).mean():,.2f}   "
      f"median spread {np.median(d['spread_tk']):.1f} tk")
    P(f"    THE SESSION IS THE DEPENDENCE UNIT: {len(order)}, not {len(d):,}.")
    P(f"    features: {', '.join(feats)}")

    # ---------------------------------------------------------------- arms
    mk = {"RIDGE (primary)": lambda: Ridge(alpha=10.0),
          "GBM (challenger)": lambda: HistGradientBoostingRegressor(
              max_depth=3, max_iter=150, learning_rate=0.05, random_state=SEED)}
    P("")
    P("=" * 104)
    P("=== ARMS - out-of-fold after-cost net P&L (the primary score)")
    P("=" * 104)
    res = {}
    for nm, f in mk.items():
        ATTEMPTS.append(nm)
        ix, pr = oof(X, y, sess, blocks, f)
        net, act = policy_pnl(pr, d.iloc[ix], 0.0)
        ss = pd.Series(net).groupby(sess[ix]).sum()
        tr = act != 0
        acc = float(np.mean(np.sign(y[ix][tr]) == act[tr])) if tr.sum() else np.nan
        se = ss.std(ddof=1) / np.sqrt(len(ss))
        res[nm] = dict(ix=ix, pr=pr, net=net, act=act, ss=ss)
        P(f"    {nm:<20} net ${ss.sum():>10,.0f}   ${ss.mean():>8,.2f}/session   "
          f"t {ss.mean()/se if se>0 else np.nan:>6.2f}   trade {100*np.mean(tr):>5.1f}%   "
          f"dir acc {100*acc:>5.1f}%   pos sess {100*np.mean(ss>0):>5.1f}%")
        for st in STRESS_TICKS[1:]:
            n2, _ = policy_pnl(pr, d.iloc[ix], st)
            P(f"    {'':<20} STRESS +{st} tk/side: net ${n2.sum():>10,.0f}")

    best = max(res, key=lambda k: res[k]["ss"].mean())
    P(f"\n    best arm by OOF net/session: {best}")
    obs = float(res[best]["ss"].mean())

    # ---------------------------------------------------------------- nulls
    P("")
    P("=" * 104)
    P("=== NULLS - full pipeline refit inside every replicate, MAX-STAT over BOTH model families")
    P("=" * 104)
    n_s = len(order)
    per = [y[sess == s] for s in order]
    maxstat = []
    for k in range(1, min(n_s, NULL_SHIFTS + 1)):
        yk = np.empty_like(y)
        for i, s in enumerate(order):
            m = sess == s
            yk[m] = np.resize(per[(i + k) % n_s], int(m.sum()))
        vals = []
        for nm, f in mk.items():
            ixk, prk = oof(X, yk, sess, blocks, f)
            nk, _ = policy_pnl(prk, d.iloc[ixk], 0.0)
            vals.append(float(pd.Series(nk).groupby(sess[ixk]).sum().mean()))
        maxstat.append(max(vals))
    maxstat = np.array(maxstat)
    pct_null = 100.0 * float((maxstat < obs).mean())
    assert len(np.unique(np.round(maxstat, 6))) > 1, "NULL HAS ONE DISTINCT VALUE"
    P(f"    session-block outcome-shift null, {len(maxstat)} replicates, "
      f"{len(np.unique(np.round(maxstat,6)))} distinct values, sd ${maxstat.std(ddof=1):,.2f}")
    P(f"    MAX-STAT over {{Ridge, GBM}} - the better model is NOT compared to a single-model null")
    P(f"    null mean ${maxstat.mean():,.2f}   observed ${obs:,.2f}   -> {pct_null:.1f}th percentile")

    ix, act = res[best]["ix"], res[best]["act"]
    rng = np.random.default_rng(SEED)
    pl = []
    for _ in range(500):
        rs = np.where(rng.random(len(ix)) < .5, 1, -1) * (act != 0)
        nn = np.where(rs == 1, d.iloc[ix]["long_gross"].values - COMMISSION_RT,
                      np.where(rs == -1, d.iloc[ix]["short_gross"].values - COMMISSION_RT, 0.0))
        pl.append(float(pd.Series(nn).groupby(sess[ix]).sum().mean()))
    pl = np.array(pl)
    pct_pl = 100.0 * float((pl < obs).mean())
    P(f"\n    activity-matched random-direction placebo: mean ${pl.mean():,.2f}/session "
      f"-> observed at {pct_pl:.1f}th percentile")

    mir = np.where(act == 1, d.iloc[ix]["short_gross"].values - COMMISSION_RT,
                   np.where(act == -1, d.iloc[ix]["long_gross"].values - COMMISSION_RT, 0.0))
    mss = pd.Series(mir).groupby(sess[ix]).sum()
    P(f"    same-trigger MIRROR (opposite direction, identical timestamps): "
      f"${mss.mean():,.2f}/session")
    P(f"    candidate minus mirror: ${obs - float(mss.mean()):,.2f}/session")

    # ---------------------------------------------------------------- gates
    ss = res[best]["ss"]
    srt = np.sort(ss.values)[::-1]
    tot = ss.sum()
    top5 = 100 * srt[:5].sum() / tot if tot > 0 else np.inf
    q = np.array_split(np.arange(len(ss)), 4)
    qn = [float(ss.values[i].sum()) for i in q]
    nstress, _ = policy_pnl(res[best]["pr"], d.iloc[ix], STRESS_TICKS[1])
    P("")
    P("=" * 104)
    P("=== PREREGISTERED GATES (SPEC.md, fixed before this ran)")
    P("=" * 104)
    g = [("B1 OOF PRIMARY net > 0", tot > 0, f"${tot:,.0f}"),
         ("B2 > 95th pctile of max-stat null", pct_null > 95, f"{pct_null:.1f}th"),
         ("B3 > 95th pctile of placebo", pct_pl > 95, f"{pct_pl:.1f}th"),
         ("B4 beats same-trigger mirror", obs > float(mss.mean()),
          f"{obs - float(mss.mean()):+,.2f}"),
         ("B5 net > 0 at STRESS +0.5tk", nstress.sum() > 0, f"${nstress.sum():,.0f}"),
         ("B6 top-5 sessions <= 50 % of net", top5 <= 50, f"{top5:.1f}%"),
         ("B7 net > 0 in >= 3 of 4 quartiles", sum(x > 0 for x in qn) >= 3,
          f"{sum(x > 0 for x in qn)} of 4")]
    P(f"    {'gate':<38}{'observed':>16}   verdict")
    P("    " + "-" * 68)
    for nm, okg, ob in g:
        P(f"    {nm:<38}{ob:>16}   {'PASS' if okg else '*** FAIL ***'}")
    allp = all(x[1] for x in g)
    P("")
    P(f"    attempts counted: {len(ATTEMPTS)} -> {ATTEMPTS}")
    P("")
    if allp:
        P("    ALL GATES PASS -> MS-BBO-CANDIDATE-1 exists.  DISCOVERY-GRADE ONLY.")
        P("    It is NOT validated, NOT confirmed, NOT production-ready, NOT live-eligible.")
        P("    Freeze source/features/model/hyperparameters/schedule/execution/costs, then its")
        P("    next scientific stage is PROSPECTIVE SHADOW.")
    else:
        P("    *** NO CANDIDATE.  MS-BBO-V1 CLOSED. ***")
        P("    Do NOT switch to 30s or 15s, add features, add quote size, add neural models,")
        P("    hand-select hours, choose high-vol days, invert a losing strategy, or change the")
        P("    execution model after the fact. A failed well-designed BBO wave is EVIDENCE.")
    ss.to_csv(os.path.join(OUT, "bbo_v1_sessions.csv"))
    _fh.close()


if __name__ == "__main__":
    main()
