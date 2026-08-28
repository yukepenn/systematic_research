"""ESNQ_V1 PRIMARY BATCH implementation. Frozen by SPEC.md + A1 + A2 + A3 before this ran.

THE 11 FEATURES, exactly as frozen. No addition, no deletion, no reordering.

    F1  rel_move_{1,5,15,30}s   = ES_ret_w / ES_mid  -  NQ_ret_w / NQ_mid   (unit-free)
    F2  es_spread_tk, es_rvol_30s, es_bid_upd_30s, es_ask_upd_30s
    F3  nq_spread_tk, nq_rvol_30s
    F4  tod

CROSS_MARKET_ES_EMBARGO = 200 ms (A3-3). Every ES source timestamp must satisfy
    max_es_source_ts <= t - 200ms
NQ-native features keep  max_nq_source_ts < t.  Execution is the first DISTINCT NQ quote > t / > t+h.
The embargo is a DATA-CONTRACT SAFETY MARGIN, not an alpha parameter, and is never searched.

Same-millisecond rule: each side is collapsed to DISTINCT timestamps with the MEAN price, which is
permutation-invariant. Export row order is never used.

Every decision EMITS max_es_source_ts and max_nq_source_ts so the causality assertions are made on
timestamps this engine actually touched, not on a claim about how a helper works.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
from timegrid import (NS_PER_S, lookback_offsets_s, session_grid_ns)     # noqa: E402

PARQ = os.path.join(ROOT, "research", "data_esnq", "parquet")

# ---- FROZEN CONSTANTS -------------------------------------------------------
RTH_START, RTH_END = "10:00:00", "15:30:00"
GRID_S, HORIZON_S = 60, 60
ES_EMBARGO_NS = 200 * 1_000_000          # A3-3, frozen, unsearchable
MAX_FILL_WAIT_MS = 1000.0
DPP_NQ, TICK_NQ = 20.0, 0.25
TICK_ES = 0.25
COMMISSION_RT = 4.36
STRESS_TICKS = (0.0, 0.5, 1.0)
RIDGE_ALPHA = 10.0
N_FOLD = 5
SEED = 20260828
FEATURES = ["rel_move_1s", "rel_move_5s", "rel_move_15s", "rel_move_30s",
            "es_spread_tk", "es_rvol_30s", "es_bid_upd_30s", "es_ask_upd_30s",
            "nq_spread_tk", "nq_rvol_30s", "tod"]
# -----------------------------------------------------------------------------


def distinct_sides(path):
    """(bid_ts, bid_px, ask_ts, ask_px) collapsed to DISTINCT timestamps, mean price per stamp."""
    d = pq.read_table(path, columns=["bip", "time", "price"]).to_pandas()
    ti = d["time"].values.astype("datetime64[ns]").astype("int64")
    bip, px = d["bip"].values, d["price"].values
    out = {}
    for b, nm in ((1, "bid"), (2, "ask")):
        m = bip == b
        t_, p_ = ti[m], px[m]
        u, inv = np.unique(t_, return_inverse=True)
        out[nm] = (u, np.bincount(inv, weights=p_) / np.bincount(inv))
    return out["bid"][0], out["bid"][1], out["ask"][0], out["ask"][1]


def prev_le(ev_t, ev_v, q):
    """Last value at a timestamp <= q, and that timestamp. (ES: embargoed cutoff is inclusive.)"""
    i = np.searchsorted(ev_t, q, side="right") - 1
    v = np.full(len(q), np.nan)
    st = np.full(len(q), np.iinfo(np.int64).min, dtype=np.int64)
    ok = i >= 0
    v[ok] = ev_v[i[ok]]
    st[ok] = ev_t[i[ok]]
    return v, st


def prev_lt(ev_t, ev_v, q):
    """Last value at a timestamp STRICTLY < q, and that timestamp. (NQ-native features.)"""
    i = np.searchsorted(ev_t, q, side="left") - 1
    v = np.full(len(q), np.nan)
    st = np.full(len(q), np.iinfo(np.int64).min, dtype=np.int64)
    ok = i >= 0
    v[ok] = ev_v[i[ok]]
    st[ok] = ev_t[i[ok]]
    return v, st


def next_gt(ev_t, ev_v, q):
    """First value at a DISTINCT timestamp > q, plus wait in ms. (execution)"""
    i = np.searchsorted(ev_t, q, side="right")
    v = np.full(len(q), np.nan)
    w = np.full(len(q), np.inf)
    st = np.full(len(q), np.iinfo(np.int64).min, dtype=np.int64)
    ok = i < len(ev_t)
    v[ok] = ev_v[i[ok]]
    st[ok] = ev_t[i[ok]]
    w[ok] = (ev_t[i[ok]] - q[ok]) / 1e6
    return v, w, st


def session_features(session_date, es_shift_ns=0, nq_corrupt=None, es_corrupt=None):
    """Build the frozen 11 features + labels for ONE session.

    es_shift_ns / *_corrupt exist ONLY for the predeclared causality probes and default to no-ops.
    """
    sd = session_date.replace("-", "")
    nb_t, nb_p, na_t, na_p = distinct_sides(os.path.join(PARQ, "NQ", f"s{sd}.parquet"))
    eb_t, eb_p, ea_t, ea_p = distinct_sides(os.path.join(PARQ, "ES", f"s{sd}.parquet"))
    if es_shift_ns:
        eb_t = eb_t + es_shift_ns
        ea_t = ea_t + es_shift_ns
    day_ns = int(pd.Timestamp(session_date).value)
    grid = session_grid_ns(day_ns, RTH_START, RTH_END, GRID_S)
    gh = grid + HORIZON_S * NS_PER_S
    tc = grid - ES_EMBARGO_NS                      # A3-3 embargoed ES cutoff

    if nq_corrupt is not None:
        nb_p, na_p = nq_corrupt(nb_t, nb_p, na_t, na_p, grid)
    if es_corrupt is not None:
        eb_p, ea_p = es_corrupt(eb_t, eb_p, ea_t, ea_p, grid)

    src_nq, src_es = [], []

    # ---- NQ-native state, STRICTLY before t
    fb, s1 = prev_lt(nb_t, nb_p, grid)
    fa, s2 = prev_lt(na_t, na_p, grid)
    src_nq += [s1, s2]
    nq_mid = (fb + fa) / 2.0
    nq_spread = fa - fb

    # ---- ES state, at or before the EMBARGOED cutoff
    eb, s3 = prev_le(eb_t, eb_p, tc)
    ea, s4 = prev_le(ea_t, ea_p, tc)
    src_es += [s3, s4]
    es_mid = (eb + ea) / 2.0
    es_spread = ea - eb

    F = {}
    for w in (1, 5, 15, 30):
        gm = grid - w * NS_PER_S
        m0b, a1 = prev_lt(nb_t, nb_p, gm)
        m0a, a2 = prev_lt(na_t, na_p, gm)
        src_nq += [a1, a2]
        nq_m0 = (m0b + m0a) / 2.0
        tm = tc - w * NS_PER_S
        e0b, a3 = prev_le(eb_t, eb_p, tm)
        e0a, a4 = prev_le(ea_t, ea_p, tm)
        src_es += [a3, a4]
        es_m0 = (e0b + e0a) / 2.0
        F[f"rel_move_{w}s"] = (es_mid - es_m0) / es_mid - (nq_mid - nq_m0) / nq_mid

    # ---- 30-sample paths, int64 offsets via the certified helper
    off = lookback_offsets_s(30, 1)
    nq_path, es_path = np.empty((30, len(grid))), np.empty((30, len(grid)))
    for k, o in enumerate(off):
        pb, b1 = prev_lt(nb_t, nb_p, grid + o)
        pa, b2 = prev_lt(na_t, na_p, grid + o)
        src_nq += [b1, b2]
        nq_path[k] = (pb + pa) / 2.0
        qb, b3 = prev_le(eb_t, eb_p, tc + o)
        qa, b4 = prev_le(ea_t, ea_p, tc + o)
        src_es += [b3, b4]
        es_path[k] = (qb + qa) / 2.0
    with np.errstate(all="ignore"):
        F["nq_rvol_30s"] = np.nanstd(np.diff(nq_path, axis=0), axis=0) * DPP_NQ
        F["es_rvol_30s"] = np.nanstd(np.diff(es_path, axis=0), axis=0) / es_mid * 1e4  # bp

    # ---- ES quote-update intensity over the embargoed 30 s window
    for nm, t_ in (("es_bid_upd_30s", eb_t), ("es_ask_upd_30s", ea_t)):
        hi = np.searchsorted(t_, tc, side="right")
        lo = np.searchsorted(t_, tc - 30 * NS_PER_S, side="right")
        F[nm] = (hi - lo).astype(float)
    F["es_spread_tk"] = es_spread / TICK_ES
    F["nq_spread_tk"] = nq_spread / TICK_NQ
    F["tod"] = (grid - (day_ns + int(pd.Timedelta(RTH_START).value))) / (3600 * NS_PER_S)

    # ---- EXECUTION: first DISTINCT NQ quote after t / t+h
    a_in, wa_in, x1 = next_gt(na_t, na_p, grid)
    b_in, wb_in, x2 = next_gt(nb_t, nb_p, grid)
    b_out, wb_out, x3 = next_gt(nb_t, nb_p, gh)
    a_out, wa_out, x4 = next_gt(na_t, na_p, gh)

    d = pd.DataFrame({k: F[k] for k in FEATURES})
    d["t"] = grid
    d["session"] = session_date
    d["long_gross"] = (b_out - a_in) * DPP_NQ
    d["short_gross"] = (b_in - a_out) * DPP_NQ
    d["wait_ok"] = ((wa_in <= MAX_FILL_WAIT_MS) & (wb_in <= MAX_FILL_WAIT_MS)
                    & (wb_out <= MAX_FILL_WAIT_MS) & (wa_out <= MAX_FILL_WAIT_MS))
    d["max_nq_source_ts"] = np.max(np.vstack(src_nq), axis=0)
    d["max_es_source_ts"] = np.max(np.vstack(src_es), axis=0)
    d["entry_ts"] = np.minimum(x1, x2)
    d["exit_ts"] = np.minimum(x3, x4)
    return d


def policy_pnl(pred, d, extra_ticks):
    """Causal threshold: the NQ spread observable strictly before t, plus commission."""
    thr = d["nq_spread_tk"].values * TICK_NQ * DPP_NQ + COMMISSION_RT \
        + 2 * extra_ticks * TICK_NQ * DPP_NQ
    slip = 2 * extra_ticks * TICK_NQ * DPP_NQ
    act = np.where(pred > thr, 1, np.where(pred < -thr, -1, 0))
    net = np.where(act == 1, d["long_gross"].values - COMMISSION_RT - slip,
                   np.where(act == -1, d["short_gross"].values - COMMISSION_RT - slip, 0.0))
    return net, act


def chrono_folds(sessions, n_fold=N_FOLD):
    """Expanding chronological folds, split at SESSION boundaries. Test strictly after train."""
    blocks = np.array_split(np.asarray(sessions), n_fold + 1)
    return [(np.concatenate(blocks[:k]), blocks[k]) for k in range(1, n_fold + 1)]


def oof(X, y, sess, folds, make):
    """Refit from scratch per fold; standardization on TRAINING ROWS ONLY, inside the fold."""
    ix, pr = [], []
    for tr, te in folds:
        mtr, mte = np.isin(sess, tr), np.isin(sess, te)
        if mtr.sum() < 50 or mte.sum() == 0:
            continue
        mu, sd = X[mtr].mean(0), X[mtr].std(0)
        sd = np.where(sd == 0, 1.0, sd)
        m = make().fit((X[mtr] - mu) / sd, y[mtr])
        pr.append(m.predict((X[mte] - mu) / sd))
        ix.append(np.where(mte)[0])
    return np.concatenate(ix), np.concatenate(pr)
