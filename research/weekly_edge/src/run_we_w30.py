"""WE_W30 (spec preregistered): where is production structurally lost?

Primary unit: POINTS PER SESSION (exposure- and price-neutral). Dollars alongside.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, weekly, sharpe                           # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W30_PRODUCTION2", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
BIG = 10 ** 9


def position_series(D, trl):
    """Reconstruct a per-bar |position| indicator from a trade list (entry..exit inclusive)."""
    t = D["t"]
    inpos = np.zeros(D["n"], bool)
    for x in trl:
        a = int(np.searchsorted(t, np.datetime64(x["et"])))
        b = int(np.searchsorted(t, np.datetime64(x["xt"])))
        inpos[a:max(b, a + 1)] = True
    return inpos


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, n_sess = D["n"], D["n_sess"]
    tarr = D["t"]
    idx = np.arange(n)
    avail = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        avail[s], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    okq = (norm <= 0) | (ratio >= 0.8)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL = lag_b(cd >= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in MEMBERS.items()}
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)

    voters, per_member = [], {}
    for mem in MEMBERS:
        vs = []
        for q in (None, 0.7, 0.8, 0.9):
            okv = np.ones(n, bool) if q is None else ((norm <= 0) | (ratio >= q))
            for dg in (True, False):
                a = okv & (dL if dg else True)
                v = np.where((TG[mem] > 0) & a, 1, 0).astype(np.int8)
                vs.append(v); voters.append(v)
        per_member[mem] = np.vstack(vs).mean(axis=0)
    frac = np.vstack(voters).mean(axis=0)
    pos_raw = (frac >= 0.5).astype(np.int8)
    trl = fills_daily(D, pos_raw, halt=1300, target=1000)
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    wkmap = {s: D["wk"][s] for s in range(n_sess)}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]

    out = open(os.path.join(OUT, "prod2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    win = (tarr >= A) & (tarr < B)
    sess_in_win = np.unique(D["sid"][win])
    nsw = len(sess_in_win)
    P_(f"window {A} .. {B}: {nsw} sessions, {win.sum():,} bars, "
       f"available {avail[sess_in_win].sum():,.0f} pts "
       f"({avail[sess_in_win].mean():.1f}/session)\n")

    P_("=== Q1 TIME IN MARKET ===")
    P_(f"{'object':<26}{'inPos%':>9}{'sessTraded%':>13}{'pts/session':>13}"
       f"{'pts/barInPos':>14}{'ptsPerTradedSess':>18}")
    rows = []
    for nm, tl in (("E5 box (1 contract)", trl), ("S1", s1)):
        ip = position_series(D, tl) & win
        p = np.array([x["pnl"] for x in tl
                      if A <= np.datetime64(x["et"]) < B]) / PV
        sess_traded = len({int(D["sid"][int(np.searchsorted(tarr, np.datetime64(x["et"])))])
                           for x in tl if A <= np.datetime64(x["et"]) < B})
        P_(f"{nm:<26}{100*ip.sum()/win.sum():>9.2f}{100*sess_traded/nsw:>13.1f}"
           f"{p.sum()/nsw:>13.2f}{p.sum()/max(ip.sum(),1):>14.4f}"
           f"{p.sum()/max(sess_traded,1):>18.2f}")
        rows.append(dict(obj=nm, in_pos_pct=round(100 * ip.sum() / win.sum(), 2),
                         sess_traded_pct=round(100 * sess_traded / nsw, 1),
                         pts_per_session=round(p.sum() / nsw, 2),
                         pts_per_bar_in_pos=round(p.sum() / max(ip.sum(), 1), 4)))
    both = (position_series(D, trl) | position_series(D, s1)) & win
    P_(f"{'E5box + S1 (either)':<26}{100*both.sum()/win.sum():>9.2f}")

    P_("\n=== Q2 WHERE THE ABSENCE COMES FROM (share of NON-position bars) ===")
    ip = position_series(D, trl) & win
    absent = win & ~ip
    tot = absent.sum()
    vote_low = absent & (frac < 0.5)
    thr_block = absent & (frac >= 0.5) & ~okq
    # halt/target: bars where the raw signal wanted in, the throttle allowed it, but the
    # session box had fired
    want = absent & (frac >= 0.5) & okq
    fired = np.zeros(n, bool)
    for s in sess_in_win:
        m = idx[(D["sid"] == s)]
        xs = [x for x in trl
              if int(D["sid"][int(np.searchsorted(tarr, np.datetime64(x["et"])))]) == s]
        if not xs:
            continue
        acc = 0.0
        last_i = None
        for x in sorted(xs, key=lambda z: z["et"]):
            acc += x["pnl"]
            last_i = int(np.searchsorted(tarr, np.datetime64(x["xt"])))
        if last_i is not None and (acc <= -1300 or acc >= 1000):
            fired[last_i:m[-1] + 1] = True
    box_fired = want & fired
    other = want & ~fired
    for nm, mask in (("vote below 0.5", vote_low), ("range throttle", thr_block),
                     ("session box already fired", box_fired),
                     ("wanted in, between fills", other)):
        P_(f"   {nm:<32}{100*mask.sum()/tot:>7.1f}%  ({mask.sum():,} bars)")
    P_(f"   {'TOTAL absent':<32}{100*tot/win.sum():>7.1f}% of all bars")

    P_("\n=== Q3 CONCURRENCY: 4 member-sets as independent sleeves, each with its own box ===")
    P_(f"{'object':<30}{'contracts':>10}{'pts/session':>13}{'wkMean$':>10}{'wkPos%':>8}"
       f"{'worst$':>10}{'shrp':>7}")

    def rep_port(nm, trls, k):
        allt = [x for t_ in trls for x in t_]
        d = weekly(allt, wk_of, A, B)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in allt if A <= np.datetime64(x["et"]) < B]) / PV
        P_(f"{nm:<30}{k:>10}{p.sum()/nsw:>13.2f}{v.mean():>10,.0f}{wp:>8.1f}"
           f"{v.min():>10,.0f}{s:>7.3f}")
        rows.append(dict(obj=nm, contracts=k, pts_per_session=round(p.sum() / nsw, 2),
                         wk_mean=round(v.mean()), wk_pos=round(wp, 1),
                         worst=round(v.min()), sharpe=round(s, 3)))
    rep_port("E5 box (reference)", [trl], 1)
    mem_trls = []
    for mem in MEMBERS:
        pm = (per_member[mem] >= 0.5).astype(np.int8)
        mem_trls.append(fills_daily(D, pm, halt=1300, target=1000))
    rep_port("4 member sleeves, own boxes", mem_trls, 4)
    rep_port("4 member sleeves + S1", mem_trls + [s1], 5)

    P_("\n=== Q4 CEILING: perfect knowledge of the SESSION's direction only ===")
    dirn = np.zeros(n, np.int8)
    for s in sess_in_win:
        m = idx[D["sid"] == s]
        dirn[m] = 1 if D["c"][m[-1]] >= D["o"][m[0]] else -1
    # our machinery, but every entry forced to the session's realised direction
    perf = np.where((frac >= 0.5) & (dirn > 0), 1,
                    np.where((frac >= 0.5) & (dirn < 0), -1, 0)).astype(np.int8)
    tl4 = fills_daily(D, perf, halt=BIG, target=None)
    p4 = np.array([x["pnl"] for x in tl4 if A <= np.datetime64(x["et"]) < B]) / PV
    P_(f"   with our entries but the session's true direction: "
       f"{p4.sum()/nsw:.1f} pts/session  (vs our {np.array([x['pnl'] for x in trl if A <= np.datetime64(x['et']) < B]).sum()/PV/nsw:.1f})")
    P_(f"   perfect-foresight single trade: {avail[sess_in_win].mean():.1f} pts/session")
    P_("   NOT ACHIEVABLE - this is a decomposition bound, not a target (spec).")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
