"""Expanded causal feature universe for flip-event quality (W39+).

Every array is a per-bar value that is fully determined by information available at the CLOSE
of bar i-1, so it may be read at bar i where the fill happens at o[i]. The lag is applied here,
once, so callers cannot forget it. Features are grouped by INFORMATION CLASS so that
leave-one-class-out attribution is possible (the charter asks which class carries the money,
not which individual column).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402


def _lag(a):
    return np.concatenate([[a[0]], a[:-1]])


def _roll(s, w, fn="mean", mp=None):
    r = pd.Series(s).rolling(w, min_periods=mp or max(5, w // 8))
    return getattr(r, fn)().values


def build_universe(D):
    """Return (features: dict[name] -> ndarray, classes: dict[name] -> class label)."""
    n = D["n"]
    o, h, l, c, v, t = D["o"], D["h"], D["l"], D["c"], D["v"], D["t"]
    sid, n_sess = D["sid"], D["n_sess"]
    idx = np.arange(n)
    rng_, dmove, atr14, norm = intraday_features(D)
    atr = np.maximum(_lag(atr14), 1e-9)
    c_l, h_l, l_l, o_l, v_l = _lag(c), _lag(h), _lag(l), _lag(o), _lag(v)
    ret = np.diff(c, prepend=c[0])
    _, cd = cd_signals(D)

    def shift(a, k):
        return np.concatenate([[a[0]] * k, a[:-k]])

    F, C = {}, {}

    def add(name, arr, cls):
        F[name] = np.nan_to_num(np.asarray(arr, float), nan=0.0, posinf=0.0, neginf=0.0)
        C[name] = cls

    # ---- session scaffolding (causal) ------------------------------------------------
    sopen = np.zeros(n); shigh = np.zeros(n); slow = np.zeros(n)
    bso = np.zeros(n); or_hi = np.zeros(n); or_lo = np.zeros(n); or_done = np.zeros(n, bool)
    sess_ret = np.zeros(n_sess); sess_rng = np.zeros(n_sess); sess_eff = np.zeros(n_sess)
    prev_c = np.nan
    gap = np.zeros(n)
    vwap = np.full(n, np.nan)
    pv = vv = 0.0
    for i in range(n):
        if D["fb"][i]:
            pv = vv = 0.0
        pv += c[i] * v[i]; vv += v[i]
        vwap[i] = pv / vv if vv > 0 else np.nan
    for s in range(n_sess):
        m = idx[sid == s]
        sopen[m] = o[m[0]]
        hh = np.maximum.accumulate(h[m]); ll = np.minimum.accumulate(l[m])
        shigh[m] = np.concatenate([[h[m[0]]], hh[:-1]])
        slow[m] = np.concatenate([[l[m[0]]], ll[:-1]])
        bso[m] = np.arange(len(m))
        k = min(30, len(m))
        or_hi[m] = h[m[:k]].max(); or_lo[m] = l[m[:k]].min()
        or_done[m] = np.arange(len(m)) > k
        sess_ret[s] = c[m[-1]] - o[m[0]]
        sess_rng[s] = h[m].max() - l[m].min()
        sess_eff[s] = abs(sess_ret[s]) / max(sess_rng[s], 1e-9)
        gap[m] = (o[m[0]] - prev_c) if not np.isnan(prev_c) else 0.0
        prev_c = c[m[-1]]
    vwap_l = _lag(vwap)

    # ---- A. trend / momentum ---------------------------------------------------------
    for k in (15, 60, 240):
        add(f"mom{k}", (c_l - shift(c_l, k)) / atr, "trend")
    sg = [np.sign(F[f"mom{k}"]) for k in (15, 60, 240)]
    add("mom_align", sg[0] + sg[1] + sg[2], "trend")
    add("trend_accel", F["mom15"] - F["mom60"] / 4.0, "trend")
    up = np.concatenate([[0], np.sign(np.diff(c))])
    rl = np.zeros(n); r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        rl[i] = r * (1 if up[i] > 0 else -1)
    add("runlen", _lag(rl), "trend")
    add("dist_hi60", (c_l - _lag(_roll(h, 60, "max"))) / atr, "trend")
    add("dist_lo60", (c_l - _lag(_roll(l, 60, "min"))) / atr, "trend")

    # ---- B. volatility / range -------------------------------------------------------
    add("atr_rel", atr / np.maximum(_roll(atr, 6900, "mean", 1000), 1e-9), "vol")
    add("rv_expansion", np.maximum(_lag(_roll(ret, 15, "std")), 1e-9)
        / np.maximum(_lag(_roll(ret, 120, "std")), 1e-9), "vol")
    add("range_compress", (_lag(_roll(h, 30, "max")) - _lag(_roll(l, 30, "min"))) / atr, "vol")
    add("sess_extension", rng_ / atr, "vol")
    add("ratio_tod", np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0), "vol")
    add("bar_range_rel", (h_l - l_l) / atr, "vol")

    # ---- C. location / value ---------------------------------------------------------
    add("dist_open", (c_l - sopen) / atr, "location")
    add("dist_vwap", (c_l - vwap_l) / atr, "location")
    add("vwap_slope", (vwap_l - shift(vwap_l, 30)) / atr, "location")
    add("dist_prevclose", (c_l - (sopen - gap)) / atr, "location")
    span = np.maximum(shigh - slow, 1e-9)
    add("pos_sess_range", (c_l - slow) / span, "location")
    orw = np.maximum(or_hi - or_lo, 1e-9)
    add("or_pos", np.where(or_done, (c_l - or_lo) / orw, 0.5), "location")
    add("or_width", np.where(or_done, orw / atr, 0.0), "location")
    add("dist_50sess", (c_l - _lag(_roll(c, 69000, "mean", 5000))) / atr, "location")

    # ---- D. overnight / prior session ------------------------------------------------
    add("prev_ret", np.concatenate([[0.0], sess_ret[:-1]])[sid], "prior_session")
    add("prev2_ret", np.concatenate([[0.0, 0.0], sess_ret[:-2]])[sid], "prior_session")
    add("gap_atr", gap / atr, "prior_session")
    prm = np.concatenate([[np.nan], _roll(sess_rng, 20, "mean", 5)[:-1]])
    pr = np.concatenate([[1.0], sess_rng[:-1]]) / np.maximum(np.nan_to_num(prm, nan=1.0), 1e-9)
    add("prev_range_rel", np.nan_to_num(pr, nan=1.0)[sid], "prior_session")
    add("prev_path_eff", np.concatenate([[0.5], sess_eff[:-1]])[sid], "prior_session")

    # ---- E. volume / flow ------------------------------------------------------------
    volnorm = np.maximum(_roll(v, 240, "mean", 30), 1e-9)
    cdl = _lag(cd); vnl = _lag(volnorm)
    add("delta_mag", np.abs(cdl) / vnl, "flow")
    add("delta_signed", cdl / vnl, "flow")
    add("delta_accel", (cdl - shift(cdl, 30)) / vnl, "flow")
    add("vol_surprise", v_l / vnl, "flow")
    add("upvol_share", _lag(_roll((ret > 0).astype(float), 60, "mean", 20)), "flow")
    add("dollarvol_rel", (c_l * v_l) / np.maximum(_lag(_roll(c * v, 240, "mean", 30)), 1e-9),
        "flow")

    # ---- F. path geometry ------------------------------------------------------------
    absret = np.abs(ret)
    add("path_eff", np.abs(c_l - shift(c_l, 30))
        / np.maximum(_lag(_roll(absret, 30, "sum", 10)), 1e-9), "geometry")
    body = np.abs(c - o); tot = np.maximum(h - l, 1e-9)
    add("body_share", _lag(_roll(body / tot, 15, "mean", 5)), "geometry")
    uw = h - np.maximum(o, c); lw = np.minimum(o, c) - l
    add("wick_asym", _lag(_roll((uw - lw) / tot, 15, "mean", 5)), "geometry")
    add("skew60", _lag(_roll(ret, 60, "skew", 20)), "geometry")

    # ---- G. event history ------------------------------------------------------------
    add("bars_since_open", bso, "history")
    flips = (np.sign(F["runlen"]) != np.sign(shift(F["runlen"], 1))).astype(float)
    add("churn60", _roll(flips, 60, "mean", 20), "history")

    # ---- H. clock --------------------------------------------------------------------
    mins = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    add("hour_sin", np.sin(2 * np.pi * mins / 1440.0), "clock")
    add("hour_cos", np.cos(2 * np.pi * mins / 1440.0), "clock")
    dow = pd.to_datetime(D["sess_date"]).dayofweek.values[sid].astype(float)
    add("dow", dow, "clock")
    return F, C
