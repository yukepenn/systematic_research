"""Set-valued inverse trade-path reconstruction (OTR_R11_INVERSE, directive v4.0 P2/P3).

Given (a) an exact Solar event ledger from solar_wave_full() and (b) one day of the
trader's NT8 Daily Analysis report, enumerate ALL single-position trade paths that
reproduce every visible daily aggregate exactly.

This replaces the R1e "which of our trades must be REMOVED" formulation, which
presupposed the original trades are a subset of one candidate stream (falsified: on
2023-01-13 and 2023-01-17 the incumbent stream has FEWER trades than the target).

NT8 conventions are the S0-certified ones (decisions at bar close, market fills at the
next bar open, exit checked before entry, position open at a session's last bar exits at
that bar's CLOSE, entries on the first/last bar of a session dropped, BarsRequired=20).

MAE/MFE use the rule certified 90/90 against NT8's own MaeCurrency/MfeCurrency in
runs/OTR_R6_NT8_PARITY/out/layerA_nt8_raw.json (see run_r11a_maemfe_calib.py):
    scan bars [entry_bar .. last_bar_held_through_close] with full High/Low,
    fold in the exit fill price, floor at 0, x $20/pt.
"""
from __future__ import annotations

import numpy as np

POINT_VALUE = 20.0
TICK_USD = 5.0          # 0.25 pt * $20
BARS_REQUIRED = 20


# ---------------------------------------------------------------------------
# target parsing: recover cropped cells exactly using the $5-tick lattice
# ---------------------------------------------------------------------------
def resolve_cropped(shown_prefix: float, k_trades: int, comm_rt: float,
                    n_missing: int = 1) -> float:
    """Recover a screenshot cell whose trailing digit(s) were cropped.

    Every gross P&L on NQ qty-1 is an integer number of $5 ticks, so a NET aggregate over
    k trades has magnitude  5m + comm_rt*k  for some integer m >= 0. The visible prefix
    pins the magnitude to an interval of width 10**-2 * 10**n_missing; we solve for the
    unique lattice point inside it. Raises if the interval admits 0 or >1 points, which
    would mean the reading itself is wrong.

    `shown_prefix` is the SIGNED displayed value with the cropped digits read as 0.
    Returns the exact signed value.
    """
    sign = -1.0 if shown_prefix < 0 else 1.0
    a = abs(shown_prefix)
    width = 10 ** (n_missing - 2)
    lo, hi = a, a + width - 1e-9
    base = comm_rt * k_trades
    cands = []
    m_lo = int(np.floor((lo - base) / 5.0)) - 1
    for m in range(max(m_lo, 0), m_lo + 5):
        v = 5.0 * m + base
        if lo - 1e-9 <= v <= hi + 1e-9:
            cands.append(round(sign * v, 2))
    if len(cands) != 1:
        raise ValueError(f"cropped resolve failed shown={shown_prefix} k={k_trades} "
                         f"cands={cands}")
    return cands[0]


# ---------------------------------------------------------------------------
# bar / event preparation
# ---------------------------------------------------------------------------
def prepare(sub, params, start_up=False):
    """sub = DataFrame with time/open/high/low/close. Returns a bar bundle."""
    from solarwave import solar_wave_full
    t = sub["time"].values.astype("datetime64[s]")
    gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
    fb = np.zeros(len(sub), bool); fb[0] = True; fb[1:] = gap > 60
    lb = np.zeros(len(sub), bool); lb[:-1] = fb[1:]; lb[-1] = True
    r = solar_wave_full(sub["open"].values, sub["high"].values, sub["low"].values,
                        sub["close"].values, params, start_up=start_up)
    return dict(t=t, o=sub["open"].values, h=sub["high"].values,
                l=sub["low"].values, c=sub["close"].values,
                fb=fb, lb=lb, st=r.signal_trade.astype(int),
                ts=r.trailing_stop, tv=r.trend_vector,
                strend=r.signal_trend.astype(int), n=len(sub))


def sessions(bb):
    """[(first_idx, last_idx)] per session, last_idx inclusive."""
    fi = np.flatnonzero(bb["fb"]); li = np.flatnonzero(bb["lb"])
    return list(zip(fi.tolist(), li.tolist()))


def mae_mfe(bb, dirn, entry_i, entry_px, exit_i, exit_px, at_close):
    """Certified NT8 rule (90/90 vs the engine)."""
    b = exit_i + 1 if at_close else exit_i
    b = max(b, entry_i + 1)
    hi = max(float(np.max(bb["h"][entry_i:b])), exit_px)
    lo = min(float(np.min(bb["l"][entry_i:b])), exit_px)
    if dirn > 0:
        mae, mfe = entry_px - lo, hi - entry_px
    else:
        mae, mfe = hi - entry_px, entry_px - lo
    return max(0.0, mae) * POINT_VALUE, max(0.0, mfe) * POINT_VALUE


# ---------------------------------------------------------------------------
# deterministic forward simulation of one entry (may become a reversal CHAIN)
# ---------------------------------------------------------------------------
def simulate_chain(bb, s_end, decide_i, dirn, universe, reverse_on_flip,
                   stop_pts=None):
    """Enter on the decision at bar `decide_i` (fill at open of decide_i+1) and run
    forward deterministically until FLAT. Returns (trades, flat_at_bar) or None.

    `flat_at_bar` = the bar index at whose CLOSE we are flat again and may decide anew.
    """
    o, h, l, c, ts, st, lb = (bb[k] for k in ("o", "h", "l", "c", "ts", "st", "lb"))
    out = []
    i = decide_i + 1
    if i > s_end:
        return None
    pos, epx, ei = dirn, float(o[i]), i
    while True:
        # -- session close: realize at THIS bar's close, flat afterwards
        if lb[i] or i >= s_end:
            xpx = float(c[s_end])
            xi = s_end
            mae, mfe = mae_mfe(bb, pos, ei, epx, xi, xpx, at_close=True)
            out.append(dict(d=pos, ei=ei, xi=xi, epx=epx, xpx=xpx,
                            g=pos * (xpx - epx) * POINT_VALUE, mae=mae, mfe=mfe,
                            kind="sc"))
            return out, s_end + 1
        # -- optional fixed intrabar stop (era-dependent; 2023 evidence says OFF)
        if stop_pts is not None:
            lvl = epx - pos * stop_pts
            hit = (l[i] <= lvl) if pos > 0 else (h[i] >= lvl)
            if hit:
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                xpx = float(o[i]) if gap else lvl
                mae, mfe = mae_mfe(bb, pos, ei, epx, i, xpx, at_close=True)
                out.append(dict(d=pos, ei=ei, xi=i, epx=epx, xpx=xpx,
                                g=pos * (xpx - epx) * POINT_VALUE, mae=mae, mfe=mfe,
                                kind="stop"))
                return out, i
        # -- trailing-stop touch (inclusive, close vs END-of-bar line)
        line = ts[i]
        if not np.isnan(line):
            hit = (pos > 0 and c[i] <= line) or (pos < 0 and c[i] >= line)
            if hit:
                sig = st[i]
                rev = (reverse_on_flip and abs(sig) == 1 and np.sign(sig) == -pos
                       and i >= BARS_REQUIRED and not lb[i])
                if i + 1 > s_end:
                    xpx, xi, atc = float(c[s_end]), s_end, True
                else:
                    xpx, xi, atc = float(o[i + 1]), i + 1, False
                mae, mfe = mae_mfe(bb, pos, ei, epx, xi, xpx, at_close=atc)
                out.append(dict(d=pos, ei=ei, xi=xi, epx=epx, xpx=xpx,
                                g=pos * (xpx - epx) * POINT_VALUE, mae=mae, mfe=mfe,
                                kind="rev" if rev else "ts"))
                if rev and xi <= s_end:
                    pos, epx, ei = int(np.sign(sig)), xpx, xi
                    i = xi
                    continue
                return out, xi
        i += 1
        if i > s_end:
            i = s_end


# ---------------------------------------------------------------------------
# the day target
# ---------------------------------------------------------------------------
class DayTarget:
    __slots__ = ("day", "n", "nW", "nL", "gp", "gl", "lw", "ll", "mae", "mfe",
                 "comm", "net")

    def __init__(self, day, n, nW, nL, gp, gl, lw, ll, mae, mfe, comm):
        self.day, self.n, self.nW, self.nL = day, n, nW, nL
        self.gp, self.gl, self.lw, self.ll = gp, gl, lw, ll   # NET of commission
        self.mae, self.mfe, self.comm = mae, mfe, comm        # MAE/MFE in $ (gross)
        self.net = round(gp + gl, 2)


def eligible(bb, i, universe):
    sig = bb["st"][i]
    return (sig != 0 and abs(sig) in universe and i >= BARS_REQUIRED
            and not bb["fb"][i] and not bb["lb"][i])


def enumerate_paths(bb, s_start, s_end, tgt: DayTarget, universe,
                    allow_reverse=True, allow_exit_only=True, stop_pts=None,
                    comm_rt=4.18, max_solutions=50000, node_budget=8_000_000,
                    exit_strict=False):
    """exit_strict=False -> Close vs end-of-bar TrailingStop, INCLUSIVE (campaign-1 V0
    convention). exit_strict=True -> STRICT, which (given the ladder recurrence) is
    equivalent to "exit only when the trend actually FLIPS": for a long in an uptrend
    close <= TS can only occur on a flip bar or on a bar where close == anchor - S exactly.
    The two rules therefore differ ONLY on exact-touch bars, which is why they are hard to
    separate and why separating them needs cent-level day labels."""
    """DFS over the two genuine degrees of freedom, with monotone pruning:

      B1  flat at an eligible signal bar   -> TAKE or SKIP
      B2  trailing-stop touch that carries an opposite T1 signal -> REVERSE or EXIT-ONLY

    Everything else (fill prices, non-flip exits, session-close realisation) is forced by
    the S0-certified NT8 conventions. B2 must be free: a wrapper gate can veto a reversal
    and turn it into a plain exit, so hard-coding stop-and-reverse would exclude real paths.

    Returns (solutions, stats). Each solution is a list of trade dicts carrying net `pnl`.
    """
    o, h, l, c, ts, st, lb = (bb[k] for k in ("o", "h", "l", "c", "ts", "st", "lb"))
    cand = [i for i in range(s_start, s_end + 1) if eligible(bb, i, universe)]
    nxt_cand = {}
    ptr = 0
    for i in range(s_start, s_end + 2):
        while ptr < len(cand) and cand[ptr] < i:
            ptr += 1
        nxt_cand[i] = ptr
    sols, nodes, overflow = [], [0], [False]
    EPS = 0.011

    # ---- memoised segment graph -------------------------------------------
    # seg(i, d) = the trade opened by a decision at bar i in direction d (fill at the
    # open of bar i+1), run forward deterministically to its OWN first exit. Fully
    # determined by (i, d), so each is simulated at most once. Reversals are just
    # seg(touch_bar, -d), which is why the same memo serves both branch points.
    _seg = {}

    def seg(i, d):
        key = (i, d)
        r = _seg.get(key)
        if r is not None:
            return r
        ei = i + 1
        if ei > s_end:
            _seg[key] = None
            return None
        epx = float(o[ei])
        k = ei
        while True:
            if k >= s_end or lb[k]:
                r = (d, ei, epx, s_end, float(c[s_end]), True, "sc", False, 0)
                break
            if stop_pts is not None:
                lvl = epx - d * stop_pts
                if (l[k] <= lvl) if d > 0 else (h[k] >= lvl):
                    gap = (o[k] <= lvl) if d > 0 else (o[k] >= lvl)
                    xpx = float(o[k]) if gap else lvl
                    r = (d, ei, epx, k, xpx, True, "stop", False, 0)
                    break
            line = ts[k]
            hit = (((d > 0 and c[k] < line) or (d < 0 and c[k] > line)) if exit_strict
                   else ((d > 0 and c[k] <= line) or (d < 0 and c[k] >= line)))
            if not np.isnan(line) and hit:
                if k + 1 > s_end:
                    xi, xpx, atc = s_end, float(c[s_end]), True
                else:
                    xi, xpx, atc = k + 1, float(o[k + 1]), False
                sg = st[k]
                can_rev = (abs(sg) == 1 and np.sign(sg) == -d and k >= BARS_REQUIRED
                           and not lb[k] and xi <= s_end and not atc)
                r = (d, ei, epx, xi, xpx, atc, "ts", bool(can_rev),
                     int(np.sign(sg)) if can_rev else 0)
                break
            k += 1
        _seg[key] = r
        return r

    class Acc:
        __slots__ = ("tr", "nW", "nL", "gw", "gl", "mae", "mfe")

        def __init__(self):
            self.tr = []; self.nW = self.nL = 0
            self.gw = self.gl = self.mae = self.mfe = 0.0

    A = Acc()

    def push(dirn, ei, epx, xi, xpx, atc, kind):
        """Add a trade; return False (and add nothing) if it violates a monotone bound."""
        pnl = round(dirn * (xpx - epx) * POINT_VALUE - comm_rt, 2)
        if pnl > 0:
            if A.nW + 1 > tgt.nW or pnl > tgt.lw + 0.006 or A.gw + pnl > tgt.gp + EPS:
                return False
        else:
            if A.nL + 1 > tgt.nL or pnl < tgt.ll - 0.006 or A.gl + pnl < tgt.gl - EPS:
                return False
        mae, mfe = mae_mfe(bb, dirn, ei, epx, xi, xpx, atc)
        if A.mae + mae > tgt.mae + 0.6 or A.mfe + mfe > tgt.mfe + 0.6:
            return False
        A.tr.append(dict(d=dirn, ei=ei, xi=xi, epx=epx, xpx=xpx, pnl=pnl,
                         mae=mae, mfe=mfe, kind=kind))
        if pnl > 0:
            A.nW += 1; A.gw += pnl
        else:
            A.nL += 1; A.gl += pnl
        A.mae += mae; A.mfe += mfe
        return True

    def pop():
        tr = A.tr.pop()
        if tr["pnl"] > 0:
            A.nW -= 1; A.gw -= tr["pnl"]
        else:
            A.nL -= 1; A.gl -= tr["pnl"]
        A.mae -= tr["mae"]; A.mfe -= tr["mfe"]

    def terminal():
        if (A.nW == tgt.nW and A.nL == tgt.nL
                and abs(A.gw - tgt.gp) < EPS and abs(A.gl - tgt.gl) < EPS
                and abs(A.mae - tgt.mae) < 0.6 and abs(A.mfe - tgt.mfe) < 0.6):
            if tgt.nW and abs(max(x["pnl"] for x in A.tr) - tgt.lw) > 0.006:
                return
            if tgt.nL and abs(min(x["pnl"] for x in A.tr) - tgt.ll) > 0.006:
                return
            sols.append([dict(x) for x in A.tr])
            if len(sols) >= max_solutions:
                overflow[0] = True

    def flat(i):
        """Flat and free to decide from bar i onward."""
        nodes[0] += 1
        if nodes[0] > node_budget:
            overflow[0] = True
            return
        if A.nW + A.nL == tgt.n:
            terminal(); return
        for kk in range(nxt_cand.get(min(i, s_end + 1), len(cand)), len(cand)):
            j = cand[kk]
            sg = st[j]
            take(seg(j, 1 if sg > 0 else -1))
            if overflow[0]:
                return

    def take(r):
        """Enter the trade described by segment `r`, then branch on its exit."""
        if r is None:
            return
        d, ei, epx, xi, xpx, atc, kind, can_rev, rdir = r
        if not push(d, ei, epx, xi, xpx, atc, kind):
            return
        if kind == "sc":
            if A.nW + A.nL == tgt.n:
                terminal()
        else:
            if can_rev and allow_reverse:
                A.tr[-1]["kind"] = "rev"
                take(seg(xi - 1, rdir))
                A.tr[-1]["kind"] = kind
            if (not can_rev) or allow_exit_only:
                flat(xi)
        pop()

    flat(s_start)
    return sols, dict(n_candidates=len(cand), nodes=nodes[0],
                      overflow=overflow[0], n_solutions=len(sols))
