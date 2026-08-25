"""WE_W06 phase 2 (hypotheses declared in spec BEFORE phase 1 was read).

All variants causal: every gate/condition uses decision-bar information only (W03 am.1 rule);
adds are evaluated on bar i from state known at bar i-1 and filled at o[i].
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                     # noqa: E402
import inverse_core as IC                                                 # noqa: E402
from run_r13_strict_master import run_master                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W06_TRENDCAP", "out")
os.makedirs(OUT, exist_ok=True)


def fills_ext(D, tgt_arr, allow_long=None, allow_short=None, halt=None,
              reentry=False, pyramid_pts=None, hold_bias=0):
    """fills() + H1 re-entry + H2 pyramid. hold_bias reserved (H4 handled in sm14 params).

    H1: after a session-flat/exit while the target is still non-zero in the SAME direction
        and the flow gate agrees, re-enter next bar (instead of waiting for a 0 crossing).
        Baseline fills() has no such block; H1 therefore RE-ARMS after a halt-free exit that
        was caused by the target dropping to 0 for exactly one bar.
    H2: while in position and unrealized >= pyramid_pts and the flow gate still agrees, add
        one unit (max 2); both units exit together.
    """
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    pos = 0; units = 0; epx = 0.0; eti = -1; sess_pnl = 0.0; halted = False
    last_dir = 0; last_flat_bar = -10 ** 9
    for i in range(n):
        if fb[i]:
            sess_pnl = 0.0; halted = False; last_dir = 0
        want = int(tgt_arr[i - 1]) if i > 0 and not fb[i] else 0
        if want == 0 and reentry and pos == 0 and last_dir != 0 and (i - last_flat_bar) <= 3:
            gate_ok = ((last_dir > 0 and (allow_long is None or allow_long[i])) or
                       (last_dir < 0 and (allow_short is None or allow_short[i])))
            tgt_now = int(tgt_arr[i - 1]) if i > 0 else 0
            if gate_ok and tgt_now == 0 and i > 0 and int(tgt_arr[max(0, i - 2)]) == last_dir:
                want = last_dir
        if want != pos and want != 0:
            blockdir = ((want > 0 and allow_long is not None and not allow_long[i]) or
                        (want < 0 and allow_short is not None and not allow_short[i]))
            if halted or blockdir:
                want = 0 if pos == 0 or want == -pos else pos
        if want != pos:
            if pos != 0:
                pnl = pos * units * (o[i] - epx) * PV - COMM_RT * units
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]), pnl=pnl, u=units))
                sess_pnl += pnl
                last_dir = pos; last_flat_bar = i
                if halt is not None and sess_pnl <= -halt:
                    halted = True
            pos = want; units = 1 if want != 0 else 0
            if pos != 0:
                epx, eti = o[i], i
        if pos != 0 and pyramid_pts is not None and units == 1:
            # unrealized measured at the PREVIOUS bar's close (causal), added at o[i]
            prev_c = c[i - 1] if i > 0 else c[i]
            if pos * (prev_c - epx) >= pyramid_pts:
                gate_ok = ((pos > 0 and (allow_long is None or allow_long[i])) or
                           (pos < 0 and (allow_short is None or allow_short[i])))
                if gate_ok and not halted:
                    epx = (epx + o[i]) / 2.0      # average price of the 2 units
                    units = 2
        if lb[i] and pos != 0:
            pnl = pos * units * (c[i] - epx) * PV - COMM_RT * units
            trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]), pnl=pnl, u=units))
            pos = 0; units = 0; last_dir = 0
    return trades


def main():
    t0 = _time.time()
    D = load()

    def lag(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL, aS = lag(cd_arr >= 0), lag(cd_arr <= 0)
    hm = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64))
    hhmm = (hm // 3600) * 100 + (hm // 60) % 60
    early_rth = (hhmm >= 931) & (hhmm <= 1000)

    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(pnl=x["pnl"], xt=str(bb["t"][x["xi"]])) for x in
          run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    NARROW = [6, 8, 10, 12, 14, 16]
    tgn = sm14_1m(D, 460, return_targets=True, volmults=NARROW)
    tgw = sm14_1m(D, 460, return_targets=True, volmults=[18, 20, 22, 24, 26, 28, 30])
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)

    M = {}
    M["S1"] = week_table(s1, D, lambda x: x["xt"])
    M["BASE_S4n.gdl"] = week_table(fills(D, tgn, allow_long=aL, allow_short=aS),
                                   D, lambda x: x["xt"])
    M["H1_reentry"] = week_table(fills_ext(D, tgn, aL, aS, reentry=True),
                                 D, lambda x: x["xt"])
    for pp in (20, 40):
        M[f"H2_pyr{pp}"] = week_table(fills_ext(D, tgn, aL, aS, pyramid_pts=pp),
                                      D, lambda x: x["xt"])
    # H3: early-RTH entries allowed only when flow agrees; elsewhere unchanged
    aL3 = aL | ~early_rth
    aS3 = aS | ~early_rth
    M["H3_earlyflow"] = week_table(fills(D, tgn, allow_long=aL3, allow_short=aS3),
                                   D, lambda x: x["xt"])
    # H4: asymmetric hold -> lower exit level (holds longer) on the whole sleeve
    for xl in (0.0, -1.0):
        tg4 = sm14_1m(D, 460, return_targets=True, volmults=NARROW, exit_level=xl)
        M[f"H4_hold{xl:+.0f}"] = week_table(fills(D, tg4, allow_long=aL, allow_short=aS),
                                            D, lambda x: x["xt"])
    # H5: two-speed
    slow = week_table(fills(D, tgw, allow_long=aL, allow_short=aS), D, lambda x: x["xt"])
    M["S4w.gdl"] = slow
    two = {}
    for src in (M["BASE_S4n.gdl"], slow):
        for s, (net, ntr) in src.items():
            a = two.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
    M["H5_twospeed"] = two
    print(f"variants done [{_time.time()-t0:.0f}s]", flush=True)

    # portfolios with S1
    ports = {}
    for k in ("BASE_S4n.gdl", "H1_reentry", "H2_pyr20", "H2_pyr40", "H3_earlyflow",
              "H4_hold+0", "H4_hold-1", "H5_twospeed"):
        p = {}
        for src in (M["S1"], M[k]):
            for s, (net, ntr) in src.items():
                a = p.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        ports[f"S1+{k}"] = p

    rows = []
    for nm, per_s in list(M.items()) + list(ports.items()):
        rec = {"member": nm}
        for which in ("dev", "hold"):
            r = summarize(per_s, D, which)
            if r is None:
                continue
            stress = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
            rec.update({f"{which}_mean": round(r["mean"]), f"{which}_pos": round(r["pos"], 1),
                        f"{which}_worst": round(r["worst"]),
                        f"{which}_sharpe": round(r["sharpe"], 3),
                        f"{which}_tpw": round(r["tpw"], 1),
                        f"{which}_ptrade": round(r["per_trade"], 1),
                        f"{which}_total": round(r["total"]),
                        f"{which}_stress": round(float(stress.mean()))})
        rows.append(rec)
    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "hypotheses.csv"), index=False)
    cols = ["member", "dev_mean", "dev_pos", "dev_worst", "dev_sharpe", "dev_tpw",
            "dev_ptrade", "dev_stress", "hold_sharpe", "hold_pos"]
    print("\n" + sm[cols].to_string(index=False))
    base = sm[sm["member"] == "BASE_S4n.gdl"].iloc[0]
    print("\nmarginal vs BASE_S4n.gdl (dev_sharpe / $per_trade / worst):")
    for nm in ("H1_reentry", "H2_pyr20", "H2_pyr40", "H3_earlyflow", "H4_hold+0",
               "H4_hold-1", "H5_twospeed"):
        r = sm[sm["member"] == nm].iloc[0]
        print(f"  {nm:<16} {r['dev_sharpe']-base['dev_sharpe']:+.3f}  "
              f"{r['dev_ptrade']-base['dev_ptrade']:+7.1f}  "
              f"{r['dev_worst']-base['dev_worst']:+,.0f}")
    print(f"\ndone [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
