"""LANE A step 2 - FREEZE THE LAST-ONLY EXECUTION COST MODEL, AND VALIDATE THE PRICE PROXY.
Directive s4E.

THE PROBLEM. The 141 blind sessions are LAST-ONLY: 101 carry no quotes at all. So a strategy
confirmed on them cannot be scored with post-hoc exact Ask/Bid labels - those labels do not exist
there. The cost model must therefore be built ENTIRELY from already-consumed BBO sessions and
FROZEN before a single blind price is decoded.

THE SECOND PROBLEM, which s4E does not name but which would silently destroy the lane. On a
Last-only session the only available price is a TRADE PRINT, and a trade prints at the bid or at
the ask. Using a trade print as both entry and exit price embeds BID-ASK BOUNCE, which manufactures
negative autocorrelation. A reversal strategy fitted on that would "work" on an artifact.

    A LAST PRICE IS NOT A MID. Treating it as one is the microstructure equivalent of the
    look-ahead bug, and it is not detectable from Last-only data alone.

THE TEST. 58 consumed sessions carry BOTH Last and BBO. On those, the TRUE executable label is
computable (LONG: Ask_t -> Bid_t+h ; SHORT: Bid_t -> Ask_t+h) and so is the LAST-PROXY label the
blind pool will have to use. Comparing them measures exactly how wrong the proxy is - in bias, in
dispersion, and most importantly in SIGN - before anything is frozen.

If the proxy FLATTERS, the frozen cost is raised until it does not. The cost model is never tuned
to make a strategy pass; it is tuned only to make the PROXY NOT OPTIMISTIC relative to a true
executable fill, using data whose outcomes are already burned.
"""
from __future__ import annotations

import glob
import os
import re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
V2 = os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")
BLIND = os.path.join(ROOT, "runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/"
                           "MICRO_BLIND_CONFIRMATION_POOL.csv")

DOLLARS_PER_POINT = 20.0        # NQ
TICK = 0.25
COMMISSION_RT = 4.36            # Lifetime template, per contract round turn
GRID_S = 60                     # PRIMARY decision clock and PRIMARY horizon (s4C: 60 seconds)
HORIZON_S = 60
_fh = open(os.path.join(OUT, "costmodel.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def asof_prev(ev_t, ev_v, grid):
    """Value of the most recent event STRICTLY BEFORE each grid point (s4D).
    searchsorted 'left' gives the count of events with t < g, so index-1 is the last one."""
    idx = np.searchsorted(ev_t, grid, side="left") - 1
    out = np.full(len(grid), np.nan)
    ok = idx >= 0
    out[ok] = ev_v[idx[ok]]
    return out


def session_frame(path):
    t = pq.read_table(path, columns=["bip", "time", "price", "volume"]).to_pandas()
    tt = t["time"].values.astype("datetime64[ns]").astype("int64")
    out = {}
    for b in (0, 1, 2):
        m = t["bip"].values == b
        out[b] = (tt[m], t["price"].values[m], t["volume"].values[m])
    return out


def main():
    blind = set(pd.read_csv(BLIND)["session"])
    files = [f for f in sorted(glob.glob(os.path.join(V2, "s*.parquet")))
             if re.match(r"^s(\d{8})", os.path.basename(f)).group(0) not in blind]
    P("=" * 100)
    P("=== LANE A step 2 - COST MODEL + PRICE-PROXY FIDELITY.  Consumed BBO sessions only.")
    P("=== Frozen BEFORE any blind session is decoded. The blind pool is NOT opened here.")
    P("=" * 100)
    P(f"    consumed BBO sessions used   {len(files)}")
    P(f"    decision clock               {GRID_S} s      horizon {HORIZON_S} s (PRIMARY, s4C)")
    P(f"    information rule             events with timestamp STRICTLY < t  (s4D)")

    recs = []
    for f in files:
        s = re.match(r"^s(\d{8})", os.path.basename(f)).group(0)
        try:
            d = session_frame(f)
        except Exception as e:                                    # noqa: BLE001
            P(f"    !! {s} unreadable: {e}")
            continue
        lt, lp, lv = d[0]
        bt, bp, _ = d[1]
        at, ap, _ = d[2]
        if len(lt) == 0 or len(bt) == 0 or len(at) == 0:
            continue
        t0 = max(lt[0], bt[0], at[0])
        t1 = min(lt[-1], bt[-1], at[-1])
        step = GRID_S * 1_000_000_000
        grid = np.arange(t0 + step, t1 - HORIZON_S * 1_000_000_000, step)
        if len(grid) < 30:
            continue
        gh = grid + HORIZON_S * 1_000_000_000

        # ---- Last-only price proxy: last TRADE PRINT strictly before the instant
        px_t = asof_prev(lt, lp, grid)
        px_h = asof_prev(lt, lp, gh)
        # ---- true executable quotes
        bid_t, ask_t = asof_prev(bt, bp, grid), asof_prev(at, ap, grid)
        bid_h, ask_h = asof_prev(bt, bp, gh), asof_prev(at, ap, gh)
        ok = ~(np.isnan(px_t) | np.isnan(px_h) | np.isnan(bid_t) | np.isnan(ask_t)
               | np.isnan(bid_h) | np.isnan(ask_h))
        ok &= (ask_t > bid_t) & (ask_h > bid_h)
        if ok.sum() < 30:
            continue
        g = grid[ok]
        hod = pd.to_datetime(g).hour + pd.to_datetime(g).minute / 60.0
        spread_pts = (ask_t - bid_t)[ok]
        # TRUE executable gross P&L in dollars, before commission
        true_long = (bid_h - ask_t)[ok] * DOLLARS_PER_POINT
        true_short = (bid_t - ask_h)[ok] * DOLLARS_PER_POINT
        # LAST-PROXY gross move, before ANY cost - what the blind pool can compute
        proxy_move = (px_h - px_t)[ok] * DOLLARS_PER_POINT
        recs.append(pd.DataFrame(dict(session=s, hod=hod, spread_pts=spread_pts,
                                      true_long=true_long, true_short=true_short,
                                      proxy_move=proxy_move)))
        if len(recs) % 10 == 0:
            P(f"    ... {len(recs)} sessions processed")
    r = pd.concat(recs, ignore_index=True)
    r.to_csv(os.path.join(OUT, "cost_sample.csv"), index=False)
    P(f"\n    grid observations {len(r):,} over {r['session'].nunique()} sessions")

    # ------------------------------------------------------------ quoted spread by hour
    P("")
    P("=" * 100)
    P("=== QUOTED SPREAD BY HOUR OF SESSION (ET) - the empirical crossing cost")
    P("=" * 100)
    r["hour"] = r["hod"].astype(int)
    P(f"    {'hour':>5}{'n':>9}{'median ticks':>15}{'p75':>8}{'p90':>8}{'p99':>8}"
      f"{'$ round trip':>15}")
    P("    " + "-" * 68)
    sched = []
    for h, g in r.groupby("hour"):
        tk = g["spread_pts"] / TICK
        med = float(tk.median())
        sched.append(dict(hour=int(h), n=len(g), med_ticks=med,
                          p75=float(tk.quantile(.75)), p90=float(tk.quantile(.90)),
                          p99=float(tk.quantile(.99)),
                          cost_rt=med * TICK * DOLLARS_PER_POINT + COMMISSION_RT))
        P(f"    {int(h):>5}{len(g):>9,}{med:>15.2f}{tk.quantile(.75):>8.2f}"
          f"{tk.quantile(.90):>8.2f}{tk.quantile(.99):>8.2f}"
          f"{med*TICK*DOLLARS_PER_POINT + COMMISSION_RT:>15,.2f}")
    sch = pd.DataFrame(sched)
    sch.to_csv(os.path.join(OUT, "cost_schedule.csv"), index=False)
    cost_map = dict(zip(sch["hour"], sch["cost_rt"]))
    r["cost_rt"] = r["hour"].map(cost_map)

    # ---------------------------------------------------- THE PROXY FIDELITY TEST
    P("")
    P("=" * 100)
    P("=== PRICE-PROXY FIDELITY - is a LAST print an honest stand-in for an executable fill?")
    P("=== proxy_net = last-print move  -  modelled round-trip cost")
    P("=== true_net  = Ask_t -> Bid_t+h  (long)  /  Bid_t -> Ask_t+h  (short),  - commission")
    P("=" * 100)
    r["proxy_long"] = r["proxy_move"] - r["cost_rt"]
    r["proxy_short"] = -r["proxy_move"] - r["cost_rt"]
    r["true_long_net"] = r["true_long"] - COMMISSION_RT
    r["true_short_net"] = r["true_short"] - COMMISSION_RT
    P(f"    {'side':<8}{'mean proxy':>13}{'mean true':>12}{'BIAS':>12}{'corr':>8}"
      f"{'sign agree':>12}   reading")
    P("    " + "-" * 82)
    bias = {}
    for side in ("long", "short"):
        a, b = r[f"proxy_{side}"], r[f"true_{side}_net"]
        bi = float(a.mean() - b.mean())
        bias[side] = bi
        co = float(np.corrcoef(a, b)[0, 1])
        sa = float(np.mean(np.sign(a) == np.sign(b)))
        P(f"    {side:<8}{a.mean():>13,.3f}{b.mean():>12,.3f}{bi:>12,.3f}{co:>8.4f}"
          f"{100*sa:>11.1f}%   {'PROXY FLATTERS' if bi > 0 else 'proxy conservative'}")

    worst = max(bias.values())
    P("")
    if worst > 0:
        extra = np.ceil(worst / (TICK * DOLLARS_PER_POINT) * 4) / 4      # round UP to 1/4 tick
        P(f"    >>> THE PROXY FLATTERS BY ${worst:,.3f} PER DECISION on its worst side.")
        P(f"    >>> A CONSERVATIVE SURCHARGE OF {extra:.2f} TICKS "
          f"(${extra*TICK*DOLLARS_PER_POINT:,.2f}) IS ADDED to every")
        P("    >>> frozen cost, so the Last-only score can never beat a true executable fill.")
    else:
        extra = 0.0
        P(f"    >>> The proxy is CONSERVATIVE on both sides (worst bias ${worst:,.3f}).")
        P("    >>> No surcharge is required. None is added.")

    sch["surcharge_ticks"] = extra
    sch["cost_rt_FROZEN"] = sch["cost_rt"] + extra * TICK * DOLLARS_PER_POINT
    sch["cost_rt_STRESS_1x"] = sch["cost_rt_FROZEN"] + TICK * DOLLARS_PER_POINT
    sch["cost_rt_STRESS_2x"] = sch["cost_rt_FROZEN"] + 2 * TICK * DOLLARS_PER_POINT
    sch.to_csv(os.path.join(OUT, "cost_schedule_FROZEN.csv"), index=False)

    P("")
    P("=" * 100)
    P("=== FROZEN COST SCHEDULE  (this file is the contract; it may not be re-fitted later)")
    P("=" * 100)
    P(f"    {'hour ET':>8}{'n':>9}{'median spr':>12}{'PRIMARY $':>12}{'STRESS +1t':>12}"
      f"{'STRESS +2t':>12}")
    P("    " + "-" * 65)
    for _, q in sch.iterrows():
        P(f"    {int(q['hour']):>8}{int(q['n']):>9,}{q['med_ticks']:>12.2f}"
          f"{q['cost_rt_FROZEN']:>12,.2f}{q['cost_rt_STRESS_1x']:>12,.2f}"
          f"{q['cost_rt_STRESS_2x']:>12,.2f}")
    P("")
    P("    PRIMARY = median quoted crossing cost at that hour + $4.36 commission"
      + (f" + {extra:.2f} tick proxy surcharge" if extra else ""))
    P("    Both STRESS ladders are FIXED HERE, before any alpha exists, exactly so that a")
    P("    disappointing headline cannot later be rescued by discovering a gentler cost model.")
    _fh.close()


if __name__ == "__main__":
    main()
