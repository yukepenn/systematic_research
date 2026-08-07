"""dc_overshoot.py — directional-change segment decomposition (DC01 / DC02).

Why this exists
---------------
For a driftless diffusion the running maximum before a drawdown of size delta is
exponentially distributed with mean delta (Lehoczky 1977; Zhang & Hadjiliadis 2009).
A stop-and-reverse system entered at directional-change confirmation and exited at the
next flip therefore earns exactly

    pnl_k = omega_k - (delta + excess_k)

where omega_k is the overshoot from the confirmation price to the segment extreme and
excess_k >= 1 tick is the close-basis crossing excess. Under the null E[omega] = delta,
so E[pnl] = -E[excess] < 0 BEFORE commissions. Every dollar the strategy makes is a
deviation of the overshoot ratio r = E[omega]/delta above 1.

DC01 measures r. DC02 asks the question that decides H-006: is r(delta) stable when
delta is measured in TICKS (=> a fixed threshold is correct and volatility scaling is a
distraction) or when it is measured in units of volatility (=> S = k*sigma is correct)?

This burns zero configuration budget: it is a property of the price series, not of a
strategy.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def dc_segments(close, delta, tick=0.25, start_up=False):
    """Run the recovered ladder and return one row per completed segment.

    Columns
        i_flip   bar index of the flip that opened the segment (entry)
        i_ext    bar index of the segment's close extreme
        i_next   bar index of the flip that closed it (exit)
        dirn     +1 up, -1 down
        p_flip   confirmation price (close at the flip)
        p_ext    extreme close
        p_next   close at the next flip
        omega    overshoot  = (p_ext - p_flip) * dirn        >= 0
        drop     retrace    = (p_ext - p_next) * dirn        >= delta
        excess   drop - delta                                 > 0 (close discretisation)
        pnl_pts  omega - drop   (= the SAR P&L of the segment, in price units)
    """
    c = np.asarray(close, float)
    n = c.size
    S = delta * tick
    is_up = bool(start_up)
    anchor = c[0]
    i_anchor = 0
    i_flip = 0
    p_flip = c[0]
    rows = []
    for t in range(1, n):
        px = c[t]
        if is_up:
            if px >= anchor:
                anchor, i_anchor = px, t
            elif px < anchor - S:
                rows.append((i_flip, i_anchor, t, 1, p_flip, anchor, px))
                is_up = False
                anchor, i_anchor, i_flip, p_flip = px, t, t, px
        else:
            if px <= anchor:
                anchor, i_anchor = px, t
            elif px > anchor + S:
                rows.append((i_flip, i_anchor, t, -1, p_flip, anchor, px))
                is_up = True
                anchor, i_anchor, i_flip, p_flip = px, t, t, px
    df = pd.DataFrame(rows, columns=["i_flip", "i_ext", "i_next", "dirn",
                                     "p_flip", "p_ext", "p_next"])
    if df.empty:
        return df
    # the first row's direction is the seed's, not a real DC; drop it
    df = df.iloc[1:].reset_index(drop=True)
    df["omega"] = (df.p_ext - df.p_flip) * df.dirn
    df["drop"] = (df.p_ext - df.p_next) * df.dirn
    df["excess"] = df["drop"] - S
    df["pnl_pts"] = df.omega - df["drop"]
    df["bars"] = df.i_next - df.i_flip
    return df


def overshoot_table(close, deltas, tick=0.25, times=None, groupby=None):
    """r = E[omega]/delta for each delta, optionally split by a grouping key."""
    out = []
    for d in deltas:
        seg = dc_segments(close, d, tick)
        if seg.empty:
            continue
        S = d * tick
        base = {
            "delta_ticks": d, "delta_pts": S, "n_seg": len(seg),
            "mean_omega_pts": seg.omega.mean(),
            "r": seg.omega.mean() / S,
            "median_omega_over_delta": (seg.omega / S).median(),
            "mean_excess_ticks": seg.excess.mean() / tick,
            "mean_pnl_pts": seg.pnl_pts.mean(),
            "mean_bars": seg.bars.mean(),
        }
        if groupby is None:
            out.append(base)
        else:
            key = np.asarray(groupby)[seg.i_next.to_numpy()]
            for g, sub in seg.groupby(key):
                Sg = S
                out.append({**base, "group": g, "n_seg": len(sub),
                            "mean_omega_pts": sub.omega.mean(),
                            "r": sub.omega.mean() / Sg,
                            "median_omega_over_delta": (sub.omega / Sg).median(),
                            "mean_excess_ticks": sub.excess.mean() / tick,
                            "mean_pnl_pts": sub.pnl_pts.mean(),
                            "mean_bars": sub.bars.mean()})
    return pd.DataFrame(out)


def exponential_fit_stats(seg, delta_pts):
    """Under the null, omega/delta ~ Exp(1): mean 1, sd 1, P(omega>delta)=1/e=0.3679."""
    x = (seg.omega / delta_pts).to_numpy()
    return {
        "mean": float(x.mean()), "sd": float(x.std(ddof=1)),
        "p_gt_1": float((x > 1).mean()),          # null 0.36788
        "p_gt_2": float((x > 2).mean()),          # null 0.13534
        "median": float(np.median(x)),            # null ln2 = 0.69315
        "n": int(len(x)),
        "se_mean": float(x.std(ddof=1) / np.sqrt(len(x))),
        "t_vs_null_1": float((x.mean() - 1.0) / (x.std(ddof=1) / np.sqrt(len(x)))),
    }
