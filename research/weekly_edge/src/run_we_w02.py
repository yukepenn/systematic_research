"""WE_W02 COMPOSER (spec preregistered): per-trade dollar caps + vol-regime filter + weights.

Reuses run_we_w01 machinery (load/week_table/summarize/sm14_1m with the return_targets hook).
New code: intrabar stop at the fill layer with re-entry blocked until the target returns to 0;
causal prior-session TR percentile entry filter; integer-weight portfolio composition over
weekly tables. Signal engines and their parameters untouched (spec).
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import (ROOT, PV, COMM_RT, STRESS_RT, load, week_table,   # noqa: E402
                        summarize, sm14_1m)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                     # noqa: E402
import inverse_core as IC                                                 # noqa: E402
from run_r13_strict_master import run_master                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W02_COMPOSER", "out")
os.makedirs(OUT, exist_ok=True)
DEVBAR_WORST, DEVBAR_POS, HOLDBAR_SHARPE, HOLDBAR_WORST = -15000.0, 55.0, 0.30, -15000.0


def session_volfilter_mask(D):
    """True on bars of sessions whose PRIOR-session mean TR ranks above the 90th percentile
    of the trailing 60 sessions (fully causal). Entries blocked on True."""
    tr = np.maximum(D["h"] - D["l"],
                    np.maximum(np.abs(D["h"] - np.roll(D["c"], 1)),
                               np.abs(D["l"] - np.roll(D["c"], 1))))
    tr[0] = D["h"][0] - D["l"][0]
    n_sess = D["n_sess"]
    sess_tr = np.array([tr[D["sid"] == s].mean() for s in range(n_sess)])
    hot = np.zeros(n_sess, bool)
    for s in range(1, n_sess):
        a = max(0, s - 61)
        window = sess_tr[a:s]
        if len(window) >= 20:
            hot[s] = sess_tr[s - 1] > np.percentile(window[:-1] if len(window) > 20 else window, 90)
    return hot[D["sid"]]


def positions_to_trades(D, tgt_arr, stop_pts=None, entry_block=None):
    """Next-bar-open fills from a target array. Optional intrabar dollar-cap stop (re-entry
    blocked until the target returns to 0) and optional entry-block mask (new entries and
    reversals suppressed on masked bars; exits to flat always allowed)."""
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    pos = 0; epx = 0.0; eti = -1; blocked = False
    for i in range(n):
        want = int(tgt_arr[i - 1]) if i > 0 and not fb[i] else 0
        if blocked and want == 0:
            blocked = False
        if entry_block is not None and entry_block[i] and want != 0 and want != pos:
            want = 0 if pos == 0 else 0 if want == -pos else pos
        if not blocked and want != pos:
            if pos != 0:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (o[i] - epx) * PV - COMM_RT))
            pos = want
            if pos != 0:
                epx, eti = o[i], i
        if pos != 0 and stop_pts is not None:
            lvl = epx - pos * stop_pts
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                px = o[i] if gap else lvl
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (px - epx) * PV - COMM_RT))
                pos = 0; blocked = True
        if lb[i] and pos != 0:
            trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                               pnl=pos * (c[i] - epx) * PV - COMM_RT))
            pos = 0
    return trades


def main():
    t0 = _time.time()
    D = load()
    hot = session_volfilter_mask(D)
    print(f"bars {D['n']:,}  volfilter hot bars {hot.mean()*100:.1f}% "
          f"[{_time.time()-t0:.0f}s]", flush=True)

    bb = IC.prepare(D["df"], SolarWaveParams())
    members = {}

    for sp in (None, 65, 130):
        tr = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT, stop_pts=sp)
        nm = f"S1.{sp if sp else 'ns'}"
        members[nm] = week_table(
            [dict(pnl=x["pnl"], xt=str(bb["t"][x["xi"]])) for x in tr], D, lambda x: x["xt"])
        print(f"{nm}: {len(tr)} [{_time.time()-t0:.0f}s]", flush=True)

    tgt_s4 = sm14_1m(D, 460, return_targets=True)
    tgt_s5 = sm14_1m(D, 460, with_solar=False, with_bmom=True, return_targets=True)
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)
    for base, tga in (("S4", tgt_s4), ("S5", tgt_s5)):
        for sp in (None, 65, 130):
            for vf in (False, True):
                if base == "S5" and sp is not None:
                    continue                       # spec: S5 variants = {as-is, volfilter}
                trl = positions_to_trades(D, tga, stop_pts=sp,
                                          entry_block=hot if vf else None)
                nm = f"{base}.{sp if sp else 'ns'}{'.vf' if vf else ''}"
                members[nm] = week_table(trl, D, lambda x: x["xt"])
                print(f"{nm}: {len(trl)} [{_time.time()-t0:.0f}s]", flush=True)

    # ---- portfolios ---------------------------------------------------------------------
    def wsum(parts):                               # parts = [(name, weight)]
        out = {}
        for nm, w in parts:
            for s, (net, ntr) in members[nm].items():
                a = out.setdefault(s, [0.0, 0])
                a[0] += net * w; a[1] += ntr * w
        return out

    s1v = [k for k in members if k.startswith("S1.")]
    s4v = [k for k in members if k.startswith("S4.")]
    s5v = [k for k in members if k.startswith("S5.")]
    ports = {}
    for a in s1v:
        for b in s4v:
            for wa, wb in ((1, 1), (1, 2), (2, 1)):
                ports[f"{a}+{b}x{wb if wa==1 else ''}{'x2+' if wa==2 else ''}w{wa}{wb}"] = \
                    wsum([(a, wa), (b, wb)])
            for cvar in s5v:
                ports[f"{a}+{b}+{cvar}"] = wsum([(a, 1), (b, 1), (cvar, 1)])
    print(f"portfolios: {len(ports)} [{_time.time()-t0:.0f}s]", flush=True)

    rows = []
    for nm, per_s in list(members.items()) + list(ports.items()):
        rec = {"member": nm}
        okdev = None
        for which in ("dev", "hold"):
            r = summarize(per_s, D, which)
            if r is None:
                continue
            stress = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
            rec.update({f"{which}_mean": round(r["mean"]), f"{which}_pos": round(r["pos"], 1),
                        f"{which}_worst": round(r["worst"]), f"{which}_sharpe": round(r["sharpe"], 3),
                        f"{which}_maxdd": round(r["maxdd"]), f"{which}_tpw": round(r["tpw"], 1),
                        f"{which}_ptrade": round(r["per_trade"], 1),
                        f"{which}_total": round(r["total"]),
                        f"{which}_stress_mean": round(float(stress.mean()))})
            if which == "dev":
                okdev = (r["worst"] > DEVBAR_WORST and r["pos"] >= DEVBAR_POS
                         and float(stress.mean()) > 0)
        rec["dev_bar"] = bool(okdev)
        rows.append(rec)
    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)

    passed = sm[sm["dev_bar"]].sort_values("dev_sharpe", ascending=False)
    print(f"\nCONFIGS CLEARING THE PREREGISTERED DEV BAR "
          f"(worst>-15k, pos>=55%, stress>0): {len(passed)}")
    cols = ["member", "dev_mean", "dev_pos", "dev_worst", "dev_sharpe", "dev_stress_mean",
            "hold_mean", "hold_pos", "hold_worst", "hold_sharpe"]
    if len(passed):
        print(passed[cols].head(15).to_string(index=False))
        ch = passed.iloc[0]
        conf = (ch["hold_sharpe"] >= HOLDBAR_SHARPE and ch["hold_worst"] > HOLDBAR_WORST)
        print(f"\nCHAMPION: {ch['member']}  -> holdout confirm: "
              f"{'PASS' if conf else 'FAIL'} (sharpe {ch['hold_sharpe']}, worst {ch['hold_worst']})")
    else:
        print("NONE - tail bar unreachable with this library (per spec, reported honestly).")
        print("\nbest by dev_sharpe regardless of bar:")
        print(sm.sort_values("dev_sharpe", ascending=False)[cols].head(12).to_string(index=False))
    print(f"\ndone [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
