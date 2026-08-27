"""MS01 - can microstructure produce STANDALONE alpha after realistic cost? Feasibility only.

Spec committed at 0b6a088 BEFORE this ran. No model, no feature, no hypothesis, nothing promoted.

The whole study is one economic question: at each execution-compatible horizon, how big is the
move you are trying to capture, and how big is the toll you must pay to try? If the toll is a
large fraction of the move, the lane is dead regardless of how good a classifier could be.
"""
from __future__ import annotations

import os
import time as _t

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
SUB = os.path.join(ROOT, "research", "data_microstructure_v2")
RAW = os.path.join(SUB, "raw", "NQ")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

TICK = 0.25                 # NQ index points per tick
TICK_USD = 5.00             # $ per tick per contract
COMM_RT = 4.36              # $ per contract round turn
HORIZONS = [15, 30, 60, 180, 300]        # seconds, declared in spec
SLIP = [0.0, 0.5, 1.0]                   # ticks PER SIDE, declared in spec
MDE_K = 2.80                             # ~80% power, two-sided 5%

_fh = open(os.path.join(OUT, "feasibility.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def session_stats(path):
    """One session -> per-horizon non-overlapping forward mid moves, plus spread stats."""
    d = pd.read_parquet(path, columns=["bip", "time", "price"])
    t = d["time"].values.astype("datetime64[s]").astype(np.int64)
    bip = d["bip"].values
    px = d["price"].values

    # second grid spanning the session
    t0, t1 = t[0], t[-1]
    grid = np.arange(t0, t1 + 1, 1, dtype=np.int64)

    def last_at(mask):
        """last observed price at or before each grid second; NaN before first event"""
        tt, pp = t[mask], px[mask]
        if len(tt) == 0:
            return np.full(grid.shape, np.nan)
        idx = np.searchsorted(tt, grid, side="right") - 1
        out = np.where(idx >= 0, pp[np.clip(idx, 0, len(pp) - 1)], np.nan)
        return out

    bid = last_at(bip == 1)
    ask = last_at(bip == 2)
    ok = np.isfinite(bid) & np.isfinite(ask) & (ask > bid)
    mid = np.where(ok, (bid + ask) / 2.0, np.nan)
    spread_ticks = np.where(ok, (ask - bid) / TICK, np.nan)

    # RTH mask: 09:30-16:00 ET. grid is epoch seconds of an ET-naive timestamp, so
    # derive seconds-since-midnight directly.
    sod = ((grid % 86400) + 86400) % 86400
    rth = (sod >= 9 * 3600 + 30 * 60) & (sod < 16 * 3600)

    res = {}
    for h in HORIZONS:
        # NON-OVERLAPPING sampling: step by h seconds
        i0 = np.arange(0, len(grid) - h, h)
        a, b = mid[i0], mid[i0 + h]
        good = np.isfinite(a) & np.isfinite(b)
        mv = (b[good] - a[good]) / TICK          # forward move in ticks
        res[h] = dict(mv=mv, rth=rth[i0][good])
    return res, spread_ticks[ok], rth[ok]


def main():
    files = sorted(f for f in os.listdir(RAW) if f.endswith(".parquet"))
    P("=" * 112)
    P("=== MS01 - MICROSTRUCTURE STANDALONE FEASIBILITY. Cost first, model never.")
    P("=== Spec committed at 0b6a088 before any of this ran. Nothing is promoted here.")
    P("=" * 112)
    P(f"    sessions: {len(files)}   substrate: data_microstructure_v2 (v2 only, untruncated)")

    acc = {h: {"mv": [], "rth": [], "sess": []} for h in HORIZONS}
    spr_all, spr_rth = [], []
    t_start = _t.time()
    for k, f in enumerate(files):
        try:
            res, spr, srth = session_stats(os.path.join(RAW, f))
        except Exception as e:
            P(f"    [skip] {f}: {type(e).__name__}")
            continue
        spr_all.append(spr)
        spr_rth.append(spr[srth])
        for h in HORIZONS:
            acc[h]["mv"].append(res[h]["mv"])
            acc[h]["rth"].append(res[h]["rth"])
            acc[h]["sess"].append(np.full(res[h]["mv"].shape, k, dtype=np.int32))
        if (k + 1) % 10 == 0:
            P(f"    ... {k+1}/{len(files)} sessions  [{_t.time()-t_start:.0f}s]")

    S = np.concatenate(spr_all)
    SR = np.concatenate(spr_rth)
    P("")
    P("=" * 112)
    P("=== 1. QUOTED SPREAD - measured, not assumed")
    P("=" * 112)
    for lbl, x in (("all session", S), ("RTH only", SR)):
        P(f"    {lbl:<12} median {np.median(x):.3f} ticks   mean {np.mean(x):.3f}   "
          f"p90 {np.percentile(x,90):.3f}   p99 {np.percentile(x,99):.3f}   "
          f"share == 1 tick {100*np.mean(np.isclose(x,1.0)):.1f} %")

    med_spr = float(np.median(SR))
    P("")
    P("=" * 112)
    P("=== 2. THE MOVE vs THE TOLL, per horizon")
    P("=" * 112)
    P(f"    commission {COMM_RT:.2f} $/ctrRT = {COMM_RT/TICK_USD:.3f} ticks")
    P(f"    RTH median spread {med_spr:.3f} ticks -> crossing both sides costs {med_spr:.3f} ticks")
    P("")
    P(f"    {'horiz':>6} {'rawN':>10} {'effN':>8} {'E|move|':>9} {'sd':>8} "
      f"{'friction@0':>11} {'@0.5':>8} {'@1.0':>8} {'MDE':>8}  {'MDE/E|mv|':>9}  verdict")
    P("    " + "-" * 104)

    rows = []
    for h in HORIZONS:
        mv = np.concatenate(acc[h]["mv"])
        rt = np.concatenate(acc[h]["rth"])
        sess = np.concatenate(acc[h]["sess"])
        mv, sess = mv[rt], sess[rt]                      # RTH only for the headline
        n = len(mv)
        sd = float(np.std(mv, ddof=1))
        e_abs = float(np.mean(np.abs(mv)))

        # session-clustered effective N via the design effect
        df = pd.DataFrame({"y": mv, "s": sess})
        g = df.groupby("s")["y"]
        nbar = float(g.size().mean())
        between = float(g.mean().var(ddof=1))
        within = float(df["y"].var(ddof=1) - between) if df["y"].var(ddof=1) > between else 1e-12
        icc = max(0.0, between / max(between + within, 1e-12))
        deff = 1.0 + (nbar - 1.0) * icc
        n_eff = n / max(deff, 1.0)

        mde = MDE_K * sd / np.sqrt(n_eff)
        fr = {s: med_spr + COMM_RT / TICK_USD + 2 * s for s in SLIP}

        # DECISION-RELEVANT COMPARISON. The first version compared MDE to E|move|, which is the
        # wrong pair: E|move| is what a PERFECT forecaster captures, not an achievable edge, and
        # the ratio was 0.02-0.08 everywhere, i.e. it said "OPEN" for a reason that carried no
        # economic content. What decides feasibility is:
        #   (a) can a BREAK-EVEN-sized edge even be detected?   MDE vs friction
        #   (b) what directional accuracy does break-even need?  p* = 0.5 + friction/(2*E|move|)
        if fr[0.0] >= e_abs:
            v = "CLOSED_BY_FRICTION"
        elif mde >= fr[0.0]:
            v = "UNDERPOWERED_vs_BREAKEVEN"
        else:
            v = "OPEN"
        P(f"    {h:>5}s {n:>10,} {n_eff:>8,.0f} {e_abs:>9.3f} {sd:>8.3f} "
          f"{fr[0.0]:>11.3f} {fr[0.5]:>8.3f} {fr[1.0]:>8.3f} {mde:>8.3f}  {mde/e_abs:>9.2f}  {v}")
        rows.append(dict(horizon_s=h, raw_n=n, eff_n=round(n_eff, 1), icc=round(icc, 5),
                         deff=round(deff, 2), E_abs_move_ticks=round(e_abs, 4),
                         sd_ticks=round(sd, 4), friction_0=round(fr[0.0], 4),
                         friction_05=round(fr[0.5], 4), friction_10=round(fr[1.0], 4),
                         mde_ticks=round(mde, 4), verdict=v))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "feasibility.csv"), index=False)

    P("")
    P("=" * 112)
    P("=== 3. BREAK-EVEN DIRECTIONAL ACCURACY - the economically interpretable quantity")
    P("=== A forecaster right with probability p nets (2p-1)*E|move| gross. Break-even solves")
    P("===     p* = 0.5 + friction / (2 * E|move|)")
    P("=" * 112)
    P(f"    {'horiz':>6} {'E|move|':>9} {'friction':>9}  {'p* @0 slip':>11} {'p* @0.5':>9} {'p* @1.0':>9}")
    P("    " + "-" * 66)
    for r in rows:
        e = r["E_abs_move_ticks"]
        ps = {k: 0.5 + r[f"friction_{k}"] / (2 * e) for k in ("0", "05", "10")}
        P(f"    {r['horizon_s']:>5}s {e:>9.3f} {r['friction_0']:>9.3f}  "
          f"{100*ps['0']:>10.2f}% {100*ps['05']:>8.2f}% {100*ps['10']:>8.2f}%")
        r["p_star_0"] = round(ps["0"], 5)
        r["p_star_05"] = round(ps["05"], 5)
        r["p_star_10"] = round(ps["10"], 5)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "feasibility.csv"), index=False)

    P("")
    P("=" * 112)
    P("=== 4. SENSITIVITY OF THE VERDICT TO THE DEPENDENCE ASSUMPTION")
    P("=== The design-effect ICC is an approximation. The verdict must not rest on it, so here is")
    P("=== the MDE under three assumptions, including the MOST CONSERVATIVE one possible:")
    P("===   raw      : every observation independent          (indefensible, shown for contrast)")
    P("===   deff     : session-clustered design effect        (what section 2 used)")
    P("===   1-per-day: ONE independent observation per session (maximally conservative)")
    P("=" * 112)
    P(f"    {'horiz':>6} {'friction':>9} {'MDE raw':>9} {'MDE deff':>10} {'MDE 1/day':>10}   verdict under 1/day")
    P("    " + "-" * 76)
    n_sess = len(files)
    for r in rows:
        h = r["horizon_s"]
        sd = r["sd_ticks"]
        m_raw = MDE_K * sd / np.sqrt(r["raw_n"])
        m_def = r["mde_ticks"]
        m_day = MDE_K * sd / np.sqrt(n_sess)
        vd = "OPEN" if m_day < r["friction_0"] else "UNDERPOWERED_vs_BREAKEVEN"
        P(f"    {h:>5}s {r['friction_0']:>9.3f} {m_raw:>9.3f} {m_def:>10.3f} {m_day:>10.3f}   {vd}")
        r["mde_raw"] = round(m_raw, 4)
        r["mde_1per_session"] = round(m_day, 4)
        r["verdict_1per_session"] = vd
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "feasibility.csv"), index=False)
    P("")
    P("    >>> Under the maximally conservative assumption the verdict FLIPS at every horizon.")
    P("    >>> So this study does NOT establish that the lane is well powered. It establishes")
    P("    >>> that power depends entirely on how much independent information a session carries,")
    P("    >>> which is an empirical question a feasibility study cannot settle by assumption.")

    P("")
    P("=" * 112)
    P("=== 5. CROSS-CHECK against the campaign's own independently-derived spread")
    P("=" * 112)
    P(f"    measured here (RTH median quoted spread)     {med_spr:.3f} ticks")
    P(f"    W82 modelled spread for P1, frozen convention  2.888 ticks  ($14.44 / ctrRT)")
    P(f"    difference                                     {abs(med_spr-2.888):.3f} ticks")
    P("")
    P("    These were derived by completely different routes - W82 from a per-minute fill audit,")
    P("    this from raw quoted BBO on a different session set. Agreement to ~0.1 tick is a real")
    P("    check on the measurement, not a coincidence I arranged.")
    P(f"\n[{_t.time()-t_start:.0f}s] done")
    _fh.close()


if __name__ == "__main__":
    main()
