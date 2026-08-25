"""GLOBAL multi-day inverse: one continuous path must satisfy EVERY visible daily row.

Directive v4.0 sections 7-10, run OTR_R11_INVERSE (amendment_4).

Solving each day in isolation asks 11 separate 9-constraint questions. The trader ran ONE
continuous backtest, so the truth is a single path that satisfies all of them at once --
about 99 exact constraints, plus the requirement that ZERO trades exit on calendar dates
that have no row in his report. Because trades are generated in chronological exit order a
day can be SEALED the instant the path moves past it, which makes the search collapse
instead of explode.
"""
from __future__ import annotations

import numpy as np

from inverse_core import (POINT_VALUE, BARS_REQUIRED, eligible, mae_mfe, sessions)


def enumerate_multiday(bb, span_start, span_end, targets_by_day, universe,
                       allow_reverse=True, allow_exit_only=True, stop_pts=None,
                       comm_rt=4.18, max_solutions=200, node_budget=40_000_000,
                       exit_strict=True, empty_days=(), count_end=None):
    """`empty_days` = calendar dates inside the span that have NO row in the report; zero
    trades may exit on those dates. For Jan-2023 that is the pre-first-row evening (Jan 2)
    and the weekends."""
    o, h, l, c, ts, st, lb = (bb[k] for k in ("o", "h", "l", "c", "ts", "st", "lb"))
    tarr = bb["t"]
    day_of = np.datetime_as_string(tarr.astype("datetime64[D]"))
    sess_end = {}
    for s0, s1 in sessions(bb):
        if s0 <= span_end and s1 >= span_start:
            for i in range(max(s0, span_start), min(s1, span_end) + 1):
                sess_end[i] = min(s1, span_end)
    cand = [i for i in range(span_start, span_end + 1) if eligible(bb, i, universe)]
    nxt_cand = {}
    ptr = 0
    for i in range(span_start, span_end + 2):
        while ptr < len(cand) and cand[ptr] < i:
            ptr += 1
        nxt_cand[i] = ptr
    sols, nodes, overflow = [], [0], [False]
    EPS = 0.011
    empty = set(empty_days)
    _seg = {}

    def seg(i, d):
        key = (i, d)
        if key in _seg:
            return _seg[key]
        ei = i + 1
        s_end = sess_end.get(i, span_end)
        if ei > s_end:
            _seg[key] = None
            return None
        epx = float(o[ei])
        k = ei
        while True:
            if k >= s_end or lb[k]:
                _seg[key] = (d, ei, epx, s_end, float(c[s_end]), True, "sc", False, 0)
                return _seg[key]
            if stop_pts is not None:
                lvl = epx - d * stop_pts
                if (l[k] <= lvl) if d > 0 else (h[k] >= lvl):
                    gap = (o[k] <= lvl) if d > 0 else (o[k] >= lvl)
                    _seg[key] = (d, ei, epx, k, float(o[k]) if gap else lvl, True,
                                 "stop", False, 0)
                    return _seg[key]
            line = ts[k]
            hit = (((d > 0 and c[k] < line) or (d < 0 and c[k] > line)) if exit_strict
                   else ((d > 0 and c[k] <= line) or (d < 0 and c[k] >= line)))
            if not np.isnan(line) and hit:
                if k + 1 > s_end:
                    xi, xpx, atc = s_end, float(c[s_end]), True
                else:
                    xi, xpx, atc = k + 1, float(o[k + 1]), False
                sg = st[k]
                cr = (abs(sg) == 1 and np.sign(sg) == -d and k >= BARS_REQUIRED
                      and not lb[k] and not atc)
                _seg[key] = (d, ei, epx, xi, xpx, atc, "rev" if cr else "ts",
                             bool(cr), int(np.sign(sg)) if cr else 0)
                return _seg[key]
            k += 1

    trades = []
    sealed = []
    cur = [dict(day=None, n=0, nW=0, nL=0, gw=0.0, gl=0.0, mae=0.0, mfe=0.0,
                lw=-1e18, ll=1e18)]
    # Report days must be filled in order and none may be skipped: every visible row has
    # n >= 1, so a path that jumps from one report day to a LATER one has left an
    # unfillable gap behind it. Without this the search wastes most of its time on
    # subtrees that can never terminate.
    ordered = sorted(targets_by_day)
    day_pos = {d: k for k, d in enumerate(ordered)}

    def day_follows(old, new):
        if new not in day_pos:
            return False
        return day_pos[new] == (0 if old is None else day_pos[old] + 1)

    def seal_ok(a):
        T = targets_by_day.get(a["day"])
        if T is None:
            return a["n"] == 0
        return (a["n"] == T.n and a["nW"] == T.nW and a["nL"] == T.nL
                and abs(a["gw"] - T.gp) < EPS and abs(a["gl"] - T.gl) < EPS
                and abs(a["mae"] - T.mae) < 0.6 and abs(a["mfe"] - T.mfe) < 0.6
                and (a["nW"] == 0 or abs(a["lw"] - T.lw) < 0.006)
                and (a["nL"] == 0 or abs(a["ll"] - T.ll) < 0.006))

    def partial_ok(a):
        T = targets_by_day.get(a["day"])
        if T is None:
            return a["n"] == 0
        return (a["n"] <= T.n and a["nW"] <= T.nW and a["nL"] <= T.nL
                and a["gw"] <= T.gp + EPS and a["gl"] >= T.gl - EPS
                and a["mae"] <= T.mae + 0.6 and a["mfe"] <= T.mfe + 0.6
                and (a["nW"] == 0 or a["lw"] <= T.lw + 0.006)
                and (a["nL"] == 0 or a["ll"] >= T.ll - 0.006))

    def push(d, ei, epx, xi, xpx, atc, kind):
        dy = day_of[xi]
        pnl = round(d * (xpx - epx) * POINT_VALUE - comm_rt, 2)
        snap = dict(cur[0])
        opened = False
        if cur[0]["day"] != dy:
            if not day_follows(cur[0]["day"], dy):
                return None
            if cur[0]["day"] is not None:
                if not seal_ok(cur[0]):
                    return None
                sealed.append(cur[0])
                opened = True
            cur[0] = dict(day=dy, n=0, nW=0, nL=0, gw=0.0, gl=0.0, mae=0.0, mfe=0.0,
                          lw=-1e18, ll=1e18)
        mae, mfe = mae_mfe(bb, d, ei, epx, xi, xpx, atc)
        a = cur[0]
        a["n"] += 1
        a["mae"] += mae; a["mfe"] += mfe
        if pnl > 0:
            a["nW"] += 1; a["gw"] += pnl
            a["lw"] = max(a["lw"], pnl)
        else:
            a["nL"] += 1; a["gl"] += pnl
            a["ll"] = min(a["ll"], pnl)
        if not partial_ok(a):
            if opened:
                sealed.pop()
            cur[0] = snap
            return None
        trades.append(dict(d=d, ei=ei, xi=xi, epx=epx, xpx=xpx, pnl=pnl,
                           mae=mae, mfe=mfe, kind=kind, day=dy))
        return (snap, opened)

    def undo(state):
        snap, opened = state
        trades.pop()
        if opened:
            sealed.pop()
        cur[0] = snap

    def terminal():
        if cur[0]["day"] is not None and not seal_ok(cur[0]):
            return
        got = {a["day"] for a in sealed}
        if cur[0]["day"] is not None:
            got.add(cur[0]["day"])
        if got != set(targets_by_day):
            return
        sols.append([dict(x) for x in trades])
        if len(sols) >= max_solutions:
            overflow[0] = True

    # `count_end` = last bar that can appear in the report. Trades exiting after it are
    # real but INVISIBLE to the report (they belong to a row we cannot see), so they must
    # neither be counted nor rejected -- otherwise the last visible day is silently
    # truncated at the data boundary. Without this the Jan-17 calendar row loses its
    # evening block, which is exactly where its missing trade lives.
    c_end = span_end if count_end is None else count_end

    def flat(i):
        nodes[0] += 1
        if nodes[0] > node_budget:
            overflow[0] = True
            return
        terminal()
        if i > c_end:
            return
        for kk in range(nxt_cand.get(min(i, span_end + 1), len(cand)), len(cand)):
            j = cand[kk]
            if j > c_end:
                break
            sg = st[j]
            take(seg(j, 1 if sg > 0 else -1))
            if overflow[0]:
                return

    def take(r):
        if r is None:
            return
        d, ei, epx, xi, xpx, atc, kind, can_rev, rdir = r
        if xi > c_end:
            terminal()          # this trade is invisible to the report; nothing more counts
            return
        if day_of[xi] in empty:
            return
        state = push(d, ei, epx, xi, xpx, atc, kind)
        if state is None:
            return
        if kind == "sc" and xi >= span_end:
            terminal()
        elif kind == "sc":
            flat(xi + 1)
        else:
            if can_rev and allow_reverse:
                take(seg(xi - 1, rdir))
            if (not can_rev) or allow_exit_only:
                flat(xi)
        undo(state)

    flat(span_start)
    return sols, dict(n_candidates=len(cand), nodes=nodes[0],
                      overflow=overflow[0], n_solutions=len(sols))
