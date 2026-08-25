"""Corrected two-layer VWAP Flux: LAYER A (indicator) and LAYER B (strategy wrapper).

Directive v4.0 sections 22/23, run OTR_R27_VF_LAYERA. Specification:
`vwap_flux_family/VF_SIGNAL_GENERATOR_v2.md` and `VF_WRAPPER_v2.md`.

THE CORRECTION. Vendor manual semantics:
    Signal Quantity Per Trend = max number of SIGNALS emitted per trend/zone
    Signal Split (Bars)       = min bar distance between consecutive SAME-DIRECTION SIGNALS
Both are properties of signal GENERATION. The previous implementation advanced those
counters only where the strategy actually entered or reversed, so a signal the indicator
would emit while the wrapper was already in a position consumed no quota and did not start
the split clock. Here Layer A owns the counters and Layer B cannot write to them.
"""
from __future__ import annotations

import numpy as np

PV = 20.0
STOP = 130.0
QTY_PER_TREND = 3
SPLIT = 5
CLOSE_THR = 0.10


def layer_a(bars, trend, P, C, H, qty=QTY_PER_TREND, split=SPLIT, close_thr=CLOSE_THR):
    """Pure indicator. Returns the emitted Signal_Trade stream.

    Knows nothing about positions. A candidate that survives the quota and split tests IS
    emitted, and consumes quota at that moment whatever the wrapper later does with it.
    """
    n = bars["n"]
    o, h, l, c, lv = bars["o"], bars["h"], bars["l"], bars["c"], bars["lv"]
    MIN, Q25, FV, Q75, MAX = (lv[:, k] for k in range(5))
    sig_out = np.zeros(n, np.int8)
    cnt = {1: 0, -1: 0}
    last = {1: -10 ** 9, -1: -10 ** 9}
    prev_tr = 0
    for i in range(n):
        if np.isnan(MAX[i]):
            continue
        ti = int(trend[i])
        if ti != prev_tr:                 # new trend => quota resets (rival reset rules
            cnt = {1: 0, -1: 0}           # are enumerated in VF_SIGNAL_GENERATOR_v2.md)
            prev_tr = ti
        rng = h[i] - l[i]
        if ti == 0 or rng <= 0:
            continue
        if ti > 0:
            rail = MAX[i] if P == "P_IN" else (Q75[i] if P == "P_Q75" else FV[i])
            touched = l[i] <= rail
            conf = (c[i] > o[i]) if C == "C_DIR" else (c[i] >= rail)
            clv = ((h[i] - c[i]) / rng <= close_thr) if H == "H1a" else \
                  ((c[i] - l[i]) / rng <= close_thr)
            cand = 1 if (touched and conf and clv) else 0
        else:
            rail = MIN[i] if P == "P_IN" else (Q25[i] if P == "P_Q75" else FV[i])
            touched = h[i] >= rail
            conf = (c[i] < o[i]) if C == "C_DIR" else (c[i] <= rail)
            clv = ((c[i] - l[i]) / rng <= close_thr) if H == "H1a" else \
                  ((h[i] - c[i]) / rng <= close_thr)
            cand = -1 if (touched and conf and clv) else 0
        if cand == 0:
            continue
        if cnt[cand] >= qty or (i - last[cand]) < split:
            continue                       # suppressed at the SIGNAL layer
        sig_out[i] = cand
        cnt[cand] += 1                     # <-- consumed by EMISSION, not by execution
        last[cand] = i
    return sig_out


def layer_b(bars, trend, sig, X, stop=STOP):
    """Strategy wrapper. Consumes Layer A's signal stream; never writes back to it."""
    n = bars["n"]
    t, o, h, l, c, lb, lv = (bars[k] for k in ("t", "o", "h", "l", "c", "lb", "lv"))
    FV = lv[:, 2]
    trades = []
    pos = 0; epx = 0.0; ei = -1; pe = 0; px = False

    def realize(i, p, kind):
        nonlocal pos
        trades.append({"d": pos, "et": str(t[ei]), "xt": str(t[i]),
                       "pnl": pos * (p - epx) * PV, "kind": kind,
                       "hold": float((t[i] - t[ei]).astype("timedelta64[s]")
                                     .astype(np.int64)) / 60.0})
        pos = 0

    for i in range(n):
        if px and pos != 0:
            realize(i, o[i], "rule"); px = False
        if pe != 0 and pos == 0:
            pos = pe; epx, ei = o[i], i
        pe = 0
        if pos != 0:
            lvl = epx - pos * stop
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gap else lvl, "stop")
        if lb[i]:
            if pos != 0:
                realize(i, c[i], "sc")
            px = False; pe = 0
            continue
        if np.isnan(FV[i]):
            continue
        s = int(sig[i]); ti = int(trend[i])
        if pos != 0:
            if X == "X_OPP":
                hit = s == -pos
            elif X == "X_FLIP":
                hit = ti == -pos
            else:
                hit = (pos > 0 and c[i] < FV[i]) or (pos < 0 and c[i] > FV[i])
            if hit:
                px = True
                if X == "X_OPP" and s == -pos:
                    pe = s                 # stop-and-reverse; consumes no Layer-A quota
                continue
        if pos == 0 and s != 0 and pe == 0:
            pe = s
    return trades
