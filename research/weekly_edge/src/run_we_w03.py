"""WE_W03 AXES (spec preregistered): session halts + S4 context gates + two manual bases.

New code: directional entry gates and session-halt in the fill layer; CumDelta and Multi-Osc
signal constructions per the manual digest (declared choices in the spec); post-hoc halt
overlay for trade-list sleeves. Everything else reused from W01/W02.
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
from run_we_w02 import session_volfilter_mask                             # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "vwap_flux_family", "src"))
from solarwave import SolarWaveParams                                     # noqa: E402
import inverse_core as IC                                                 # noqa: E402
from run_r13_strict_master import run_master                              # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                            # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W03_AXES", "out")
os.makedirs(OUT, exist_ok=True)
W01OUT = os.path.join(ROOT, "runs", "WE_W01_SLEEVE_MAP", "out")


def fills(D, tgt_arr, halt=None, allow_long=None, allow_short=None):
    """Next-bar-open fills with optional per-session dollar halt (entries blocked after the
    sleeve's session realized P&L breaches -halt) and directional entry gates."""
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    pos = 0; epx = 0.0; eti = -1; sess_pnl = 0.0; halted = False
    for i in range(n):
        if fb[i]:
            sess_pnl = 0.0; halted = False
        want = int(tgt_arr[i - 1]) if i > 0 and not fb[i] else 0
        if want != pos and want != 0:
            blockdir = ((want > 0 and allow_long is not None and not allow_long[i]) or
                        (want < 0 and allow_short is not None and not allow_short[i]))
            if halted or blockdir:
                want = 0 if pos == 0 or want == -pos else pos
        if want != pos:
            if pos != 0:
                pnl = pos * (o[i] - epx) * PV - COMM_RT
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                sess_pnl += pnl
                if halt is not None and sess_pnl <= -halt:
                    halted = True
            pos = want
            if pos != 0:
                epx, eti = o[i], i
        if lb[i] and pos != 0:
            pnl = pos * (c[i] - epx) * PV - COMM_RT
            trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            pos = 0
    return trades


def halt_overlay_trades(D, trades, halt):
    """Post-hoc overlay for trade-list sleeves (S1/CD/MO): drop trades ENTERED after the
    session's cumulative realized P&L breached -halt. Approximation declared in the spec."""
    tarr = D["t"]
    out = []
    bysess = {}
    for x in trades:
        i = int(np.searchsorted(tarr, np.datetime64(x["et"])))
        s = int(D["sid"][min(i, D["n"] - 1)])
        bysess.setdefault(s, []).append(x)
    for s, xs in bysess.items():
        xs = sorted(xs, key=lambda x: x["et"])
        cum = 0.0
        for x in xs:
            if cum <= -halt:
                continue
            out.append(x)
            cum += x["pnl"]
    return out


def rma(x, p):
    a = np.full_like(x, np.nan, dtype=float)
    if len(x) < p:
        return a
    a[p - 1] = x[:p].mean()
    k = 1.0 / p
    for i in range(p, len(x)):
        a[i] = a[i - 1] + k * (x[i] - a[i - 1])
    return a


def mo_signals(D):
    """Multi-Osc overlap -> reversal-bar pulses (declared construction, spec)."""
    c, h, l, v = D["c"], D["h"], D["l"], D["v"]
    n = D["n"]
    d = np.diff(c, prepend=c[0])
    up, dn = np.where(d > 0, d, 0.0), np.where(d < 0, -d, 0.0)
    rs = rma(up, 14) / np.maximum(rma(dn, 14), 1e-9)
    rsi = 100 - 100 / (1 + rs)
    tp = (h + l + c) / 3.0
    mf = tp * v
    pos_mf = np.where(np.diff(tp, prepend=tp[0]) > 0, mf, 0.0)
    neg_mf = np.where(np.diff(tp, prepend=tp[0]) < 0, mf, 0.0)
    pos_s = pd.Series(pos_mf).rolling(14).sum().values
    neg_s = pd.Series(neg_mf).rolling(14).sum().values
    mfi = 100 * pos_s / np.maximum(pos_s + neg_s, 1e-9)
    ll = pd.Series(l).rolling(14).min().values
    hh = pd.Series(h).rolling(14).max().values
    k_raw = 100 * (c - ll) / np.maximum(hh - ll, 1e-9)
    k = pd.Series(k_raw).rolling(3).mean().values
    ob = (mfi > 80) & (rsi > 70) & (k > 80)
    os_ = (mfi < 20) & (rsi < 30) & (k < 20)
    sig = np.zeros(n, np.int8)
    side = 0; ridx = 0
    for i in range(1, n):
        if D["fb"][i]:
            side = 0; ridx = 0
        if ob[i]:
            side = 1; ridx = 0
        elif os_[i]:
            side = -1; ridx = 0
        elif side != 0:
            ridx += 1
            if ridx <= 5:
                if side == 1 and c[i] < c[i - 1]:
                    sig[i] = -1; side = 0
                elif side == -1 and c[i] > c[i - 1]:
                    sig[i] = 1; side = 0
            else:
                side = 0
    return sig


def cd_signals(D):
    """CumDelta transition pulses (declared construction, spec)."""
    c, v = D["c"], D["v"]
    n = D["n"]
    sgn = np.sign(np.diff(c, prepend=c[0]))
    sv = sgn * v
    cd = np.zeros(n)
    run = 0.0
    for i in range(n):
        if D["fb"][i]:
            run = 0.0
        run += sv[i]
        cd[i] = run
    s = pd.Series(cd)
    med = s.rolling(240, min_periods=30).median().values
    diff = cd - med
    sd = pd.Series(diff).rolling(240, min_periods=30).std().values
    state = np.zeros(n, np.int8)
    ok = ~np.isnan(sd) & (sd > 0)
    state[ok & (diff > sd)] = 1
    state[ok & (diff < -sd)] = -1
    sig = np.zeros(n, np.int8)
    sig[1:] = np.where((state[1:] != 0) & (state[1:] != state[:-1]), state[1:], 0)
    sig[D["fb"]] = 0
    return sig, cd


def main():
    t0 = _time.time()
    D = load()
    lv = np.load(os.path.join(W01OUT, "vf_levels_cache.npy"))
    FV = lv[:, 2]
    print(f"bars {D['n']:,} [{_time.time()-t0:.0f}s]", flush=True)

    trr = np.maximum(D["h"] - D["l"],
                     np.maximum(np.abs(D["h"] - np.roll(D["c"], 1)),
                                np.abs(D["l"] - np.roll(D["c"], 1))))
    trr[0] = D["h"][0] - D["l"][0]
    atr = pd.Series(trr).rolling(14, min_periods=1).mean().values

    cds, cd_arr = cd_signals(D)
    # amendment_1: gates must carry DECISION-BAR information only -> lag one bar.
    def lag(a):
        return np.concatenate([[True], a[:-1]])
    allow_L_fv = lag(np.isnan(FV) | (D["c"] >= FV))
    allow_S_fv = lag(np.isnan(FV) | (D["c"] <= FV))
    allow_L_dl = lag(cd_arr >= 0)
    allow_S_dl = lag(cd_arr <= 0)

    members = {}

    # ---- S1 ---------------------------------------------------------------------------
    bb = IC.prepare(D["df"], SolarWaveParams())
    tr1 = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)
    tr1 = [dict(pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]])) for x in tr1]
    members["S1.none"] = week_table(tr1, D, lambda x: x["xt"])
    for hlt in (1300, 2600):
        members[f"S1.h{hlt}"] = week_table(halt_overlay_trades(D, tr1, hlt),
                                           D, lambda x: x["xt"])
    print(f"S1 x3 [{_time.time()-t0:.0f}s]", flush=True)

    # ---- S4 grid ----------------------------------------------------------------------
    SUBSETS = {"all13": None, "wide7": [18, 20, 22, 24, 26, 28, 30],
               "narrow6": [6, 8, 10, 12, 14, 16]}
    GATES = {"gnone": (None, None), "gfv": (allow_L_fv, allow_S_fv),
             "gdl": (allow_L_dl, allow_S_dl)}
    for sub, vm in SUBSETS.items():
        tg = sm14_1m(D, 460, return_targets=True, volmults=vm)
        for hname, hlt in (("hnone", None), ("h1300", 1300), ("h2600", 2600)):
            for gname, (aL, aS) in GATES.items():
                trl = fills(D, tg, halt=hlt, allow_long=aL, allow_short=aS)
                members[f"S4.{sub}.{hname}.{gname}"] = week_table(trl, D, lambda x: x["xt"])
        print(f"S4.{sub} x9 [{_time.time()-t0:.0f}s]", flush=True)

    # ---- CD / MO ----------------------------------------------------------------------
    bars = dict(n=D["n"], t=D["t"], o=D["o"], h=D["h"], l=D["l"], c=D["c"],
                lb=D["lb"], lv=np.zeros((D["n"], 5)))
    for nm, sig, fam, par in (("CD", cds, "X_OPP", None), ("MO", mo_signals(D), "X_TIMEOUT", 240)):
        trl = layer_b_exit(bars, None, sig, atr, fam, par, stop=130)
        for x in trl:
            x["pnl"] -= COMM_RT
        members[f"{nm}.ns"] = week_table(trl, D, lambda x: x["xt"])
        members[f"{nm}.h2600"] = week_table(halt_overlay_trades(D, trl, 2600),
                                            D, lambda x: x["xt"])
        print(f"{nm}: {len(trl)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---- S5 carried -------------------------------------------------------------------
    hot = session_volfilter_mask(D)
    tg5 = sm14_1m(D, 460, with_solar=False, with_bmom=True, return_targets=True)
    nb = ~hot
    trl5 = fills(D, tg5, allow_long=nb, allow_short=nb)
    members["S5.ns.vf"] = week_table(trl5, D, lambda x: x["xt"])
    print(f"S5 [{_time.time()-t0:.0f}s]", flush=True)

    # ---- portfolios -------------------------------------------------------------------
    def wsum(names):
        out = {}
        for nm in names:
            for s, (net, ntr) in members[nm].items():
                a = out.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        return out

    ports = {}
    s4names = [k for k in members if k.startswith("S4.")]
    for b in s4names:
        ports[f"S1.none+{b}"] = wsum(["S1.none", b])
        ports[f"S1.h2600+{b}"] = wsum(["S1.h2600", b])
    ports["PC"] = wsum(["S1.none", "S4.all13.h2600.gnone", "CD.h2600", "MO.h2600"])
    ports["PD"] = wsum(["S1.none", "S4.all13.h2600.gnone", "CD.h2600", "MO.h2600", "S5.ns.vf"])

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
                        f"{which}_worst": round(r["worst"]),
                        f"{which}_sharpe": round(r["sharpe"], 3),
                        f"{which}_tpw": round(r["tpw"], 1),
                        f"{which}_ptrade": round(r["per_trade"], 1),
                        f"{which}_total": round(r["total"]),
                        f"{which}_stress_mean": round(float(stress.mean()))})
            if which == "dev":
                okdev = (r["worst"] > -15000 and r["pos"] >= 55
                         and float(stress.mean()) > 0)
        rec["dev_bar"] = bool(okdev)
        rows.append(rec)
    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)

    cols = ["member", "dev_mean", "dev_pos", "dev_worst", "dev_sharpe", "dev_ptrade",
            "dev_stress_mean", "hold_mean", "hold_pos", "hold_worst", "hold_sharpe"]
    passed = sm[sm["dev_bar"]].sort_values("dev_sharpe", ascending=False)
    print(f"\nCLEARING DEV BAR: {len(passed)}")
    if len(passed):
        print(passed[cols].head(20).to_string(index=False))
        ch = passed.iloc[0]
        conf = ch["hold_sharpe"] >= 0.30 and ch["hold_worst"] > -15000
        print(f"\nCHAMPION: {ch['member']} -> holdout confirm {'PASS' if conf else 'FAIL'}")
    else:
        print("NONE.")
    print("\nbest by dev_sharpe (any):")
    print(sm.sort_values("dev_sharpe", ascending=False)[cols].head(15).to_string(index=False))
    print("\nnew bases:")
    print(sm[sm["member"].str.startswith(("CD", "MO"))][cols].to_string(index=False))
    print(f"\ndone [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
