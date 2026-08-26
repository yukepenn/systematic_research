"""Shared quality-score machinery (W34), factored out so W35+ reuse one definition.

Every feature is lagged one bar; the score at bar i uses decision-bar information only.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, sm14_1m                        # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w19 import MEMBERS                                           # noqa: E402


def build_context(D):
    """All causal context arrays the quality score and the vote need."""
    n = D["n"]
    c, o, v = D["c"], D["o"], D["v"]
    rng_, dmove, atr14, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)
    idx = np.arange(n)
    pv = vv = 0.0
    vwap = np.full(n, np.nan)
    sopen = np.zeros(n)
    for i in range(n):
        if D["fb"][i]:
            pv = vv = 0.0
        pv += c[i] * v[i]; vv += v[i]
        vwap[i] = pv / vv if vv > 0 else np.nan
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sopen[m] = o[m[0]]
    atr_l = np.concatenate([[atr14[0]], atr14[:-1]])
    vwap_l = np.concatenate([[np.nan], vwap[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    sess_ret = np.zeros(D["n_sess"])
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sess_ret[s] = c[m[-1]] - o[m[0]]
    prev_ret = np.concatenate([[0.0], sess_ret[:-1]])[D["sid"]]
    up = np.concatenate([[0], np.sign(np.diff(c))])
    rl = np.zeros(n); r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        rl[i] = r * (1 if up[i] > 0 else -1)
    rl_l = np.concatenate([[0], rl[:-1]])
    volnorm = pd.Series(v).rolling(240, min_periods=30).mean().values
    delta_mag = np.concatenate([[0.0], (np.abs(cd) / np.maximum(volnorm, 1e-9))[:-1]])
    return dict(ratio=ratio, norm=norm, dL=dL, dS=dS, atr_l=atr_l,
                dist_open=(c_l - sopen) / np.maximum(atr_l, 1e-9),
                dist_vwap=(c_l - vwap_l) / np.maximum(atr_l, 1e-9),
                prev_ret=prev_ret, runlen=rl_l, delta_mag=delta_mag)


def long_vote(D, X):
    vs = []
    for mem in MEMBERS:
        tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem])
        for q in (None, 0.7, 0.8, 0.9):
            okv = np.ones(D["n"], bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
            for dg in (True, False):
                a = okv & (X["dL"] if dg else True)
                vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
    return np.vstack(vs).mean(axis=0)


def short_vote(D, X):
    vs = []
    for mem in MEMBERS:
        tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem])
        for q in (None, 0.7, 0.8, 0.9):
            okv = np.ones(D["n"], bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
            for dg in (True, False):
                a = okv & (X["dS"] if dg else True)
                vs.append(np.where((tg < 0) & a, 1, 0).astype(np.int8))
    return np.vstack(vs).mean(axis=0)


def quality_score(X, ent_i, side=1):
    """W34's five-feature score. side=+1 long, -1 short (directional features mirrored)."""
    f = {"dist_open": X["dist_open"] * side,
         "prev_ret": X["prev_ret"] * side,
         "runlen": X["runlen"] * side,
         "dist_vwap": X["dist_vwap"] * side,
         "delta_mag": X["delta_mag"]}
    sc = np.zeros(len(X["ratio"]))
    sc += (f["dist_open"] >= np.nanquantile(f["dist_open"][ent_i], 2 / 3))
    sc += (f["prev_ret"] <= np.nanquantile(f["prev_ret"][ent_i], 1 / 3))
    sc += (f["runlen"] >= np.nanquantile(f["runlen"][ent_i], 0.9))
    sc += (f["dist_vwap"] >= np.nanquantile(f["dist_vwap"][ent_i], 2 / 3))
    sc += (f["delta_mag"] >= np.nanquantile(f["delta_mag"][ent_i], 2 / 3))
    return sc
